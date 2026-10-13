"""Ecology preflight: default-deny regional/habitat assignment and roster gates.
Source-support flags are review records, not an automatic biological oracle.
Candidate inventory never becomes game data merely because it exists.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = {'latitude','longitude','lat','lng','lon','coordinates','geometry','geojson','observation_id','observation_url','exact_locality','locality_coordinates','private_latitude','private_longitude','decimalLatitude'.lower(),'decimalLongitude'.lower()}

class EcologyError(ValueError):
    pass

def reject_localities(value, path='root'):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN:
                raise EcologyError(f'precise-locality field forbidden: {path}.{key}')
            reject_localities(item, f'{path}.{key}')
    elif isinstance(value, list):
        for n, item in enumerate(value):
            reject_localities(item, f'{path}[{n}]')

def allowed_fields(record, fields, label):
    extra = set(record) - set(fields)
    if extra:
        raise EcologyError(f'unsupported {label} fields: {sorted(extra)}')

def validate_registry(policy, registry, release=False):
    reject_localities(policy)
    reject_localities(registry)
    target = policy['regular_species_target'] + policy['hidden_species_target']
    if target != policy['total_species_target'] or target > policy['runtime_species_capacity']:
        raise EcologyError('roster target/capacity mismatch')
    allowed_fields(registry, {'schema_version','scope','records'}, 'registry')
    records = registry['records']
    ids, names, guide_ids = set(), set(), set()
    allowed_regions = set(policy['region_ids'])
    for record in records:
        allowed_fields(record, {'species_id','guide_number','canonical_scientific_name','group','native_in_california','status','hidden','region_permissions','release_review_status'}, 'ecology record')
        sid = record['species_id']
        name = record['canonical_scientific_name']
        guide = record['guide_number']
        if sid in ids or name.casefold() in names or guide in guide_ids:
            raise EcologyError('duplicate species identity or guide number')
        if not (0 <= sid < policy['runtime_species_capacity']) or not (1 <= guide <= target):
            raise EcologyError('species/guide ID exceeds planned capacity')
        if not re.fullmatch(r'[A-Z][a-z]+ [a-z][a-z-]+', name):
            raise EcologyError('canonical identity must be a species binomial, not a variant')
        if record['group'] not in policy['allowed_taxon_groups'] or record['native_in_california'] is not True:
            raise EcologyError('native herp roster rejects non-native or unreviewed native status')
        if record['status'] not in ('foundation_source_supported','source_reviewed','release_ready'):
            raise EcologyError('candidate cannot enter runtime roster')
        if record['hidden'] != (guide == policy['hidden_discovery']['guide_number']):
            raise EcologyError('hidden guide identity mismatch')
        permissions = record['region_permissions']
        if not permissions:
            raise EcologyError('species has no supported region')
        seen_regions = set()
        for permission in permissions:
            allowed_fields(permission, {'region_id','habitat_ids','evidence_urls','evidence_scope','checked_on','review_status','game_time_note','evidence_notes','subarea_ids'}, 'region permission')
            region = permission['region_id']
            if region not in allowed_regions or region in seen_regions:
                raise EcologyError('unknown or duplicated district permission')
            if permission['review_status'] != 'source_supported':
                raise EcologyError('unreviewed region permission')
            if not permission['habitat_ids'] or not permission['evidence_urls']:
                raise EcologyError('region permission needs habitat and evidence')
            if not all(url.startswith('https://') for url in permission['evidence_urls']):
                raise EcologyError('evidence must have a source URL')
            seen_regions.add(region)
        if release and (record['status'] != 'release_ready' or record['release_review_status'] != 'passed'):
            raise EcologyError('independent release review is incomplete')
        ids.add(sid); names.add(name.casefold()); guide_ids.add(guide)
    if release:
        if len(records) != target or sum(r['hidden'] for r in records) != policy['hidden_species_target']:
            raise EcologyError('full 150+1 roster is incomplete')
        if guide_ids != set(range(1,target+1)):
            raise EcologyError('release guide numbering is incomplete')
    return {r['species_id']: r for r in records}

def validate_placement(record, region_id, habitat_id=None, subarea_id=None):
    permission = next((p for p in record['region_permissions'] if p['region_id'] == region_id), None)
    if permission is None:
        raise EcologyError(f"{record['canonical_scientific_name']} has no supported placement in {region_id}")
    if permission.get('subarea_ids') and subarea_id not in permission['subarea_ids']:
        raise EcologyError(f"{record['canonical_scientific_name']} requires an approved district subarea")
    if habitat_id is not None and habitat_id not in permission['habitat_ids']:
        raise EcologyError(f"{record['canonical_scientific_name']} has no supported habitat {habitat_id}")

def validate_encounters(policy, registry, encounters, world=None):
    """Validate the exact encounter rows used to generate the foundation C table."""
    reject_localities(encounters)
    lookup = validate_registry(policy, registry)
    allowed_fields(encounters, {'schema_version','scope','locations_are_game_tiles_not_real_world','records'}, 'encounter manifest')
    if world is None:
        world = json.loads((ROOT/'data/world.json').read_text())
    reject_localities(world)
    maps = {m['id']: m for m in world['maps']}
    if not (0 < len(maps) <= 400) or set(maps) != set(range(len(world['maps']))):
        raise EcologyError('world map identities must be unique and dense')
    game_coords=set()
    for m in maps.values():
        if m['district_id'] not in policy['region_ids'] or len(m['terrain']) != 7 or any(len(row)!=10 or set(row)-set('STCGWJjB') for row in m['terrain']):
            raise EcologyError('invalid authored map district or terrain')
        if len(m['name'])>20 or not m['name'].isascii():
            raise EcologyError('map label exceeds native display width')
        if m['terrain'][3][0] in 'GWJj' or m['terrain'][3][9] in 'GWJj':
            raise EcologyError('map arrival/exit cells must be passable')
        if m['camp'] is not None and (len(m['camp'])!=2 or not 0<=m['camp'][0]<10 or not 0<=m['camp'][1]<7):
            raise EcologyError('invalid game camp position')
        for link in ('west','east'):
            if m[link] is not None and m[link] not in maps:
                raise EcologyError('world exit references unknown map')
    for m in maps.values():
        for direction,row,reverse in [('north',0,'south'),('south',6,'north')]:
            target=m.get(direction);column=m.get(direction+'_x',255)
            if target is None:
                if column!=255:raise EcologyError('unused portal must have255 column')
                continue
            if type(target) is not int or target not in maps or type(column) is not int or not 0<=column<10 or m['terrain'][row][column] in 'GWJj':raise EcologyError('invalid vertical portal or blocked arrival')
            other=maps[target]
            if other.get(reverse)!=m['id'] or other['district_id']!=m['district_id'] or m.get('hidden') or other.get('hidden'):raise EcologyError('vertical portal must be reciprocal within ordinary district')
            if m['district_id']=='D12' and m.get('subarea_id')!=other.get('subarea_id'):raise EcologyError('islands requireferry, neverlandportal')
    seen, placed = set(), set()
    for site in encounters['records']:
        allowed_fields(site, {'spot_id','room_id','game_tile_x','game_tile_y','interaction_type','species_id','phase_mask','region_id','habitat_id'}, 'encounter site')
        sid = site['species_id']
        if site['spot_id'] in seen or sid not in lookup:
            raise EcologyError('duplicated spot or unknown species')
        if site['room_id'] not in maps or site['region_id'] != maps[site['room_id']]['district_id']:
            raise EcologyError('foundation room/district mismatch')
        if not (0 <= site['game_tile_x'] < 10 and 0 <= site['game_tile_y'] < 7):
            raise EcologyError('encounter outside authored game screen')
        pos=(site['room_id'],site['game_tile_x'],site['game_tile_y'])
        m=maps[site['room_id']]
        if pos in game_coords or m['terrain'][pos[2]][pos[1]] in 'GWJj' or list(pos[1:])==m['camp'] or pos[1:]==(0,3) or pos[1:]==(9,3) or (m.get('north') is not None and pos[1:]==(m['north_x'],0)) or (m.get('south') is not None and pos[1:]==(m['south_x'],6)):
            raise EcologyError('encounter must have unique passable placement clear of camp/arrivals')
        game_coords.add(pos)
        if site['interaction_type'] not in range(10) or site['phase_mask'] not in range(1, 8):
            raise EcologyError('invalid interaction or time mask')
        validate_placement(lookup[sid], site['region_id'], site['habitat_id'], maps[site['room_id']].get('subarea_id'))
        seen.add(site['spot_id']); placed.add(sid)
    if not (0 < len(seen) <= 1000) or seen != set(range(len(encounters['records']))):
        raise EcologyError('encounter IDs must be unique, dense and within 1000-spot capacity')
    return placed

def validate_runtime_rows(policy, registry, runtime):
    lookup = validate_registry(policy, registry)
    reject_localities(runtime)
    # The151 frozen canonical IDs are direct-indexed in banked art/data tables.
    # RF02 arrays reserve192 slots without changing identity on later content builds.
    if not (0 < len(runtime) <= policy['runtime_species_capacity']) or set(lookup) != set(range(len(runtime))):
        raise EcologyError('runtime must match reviewed dense IDs within capacity')
    if [species['id'] for species in runtime] != list(range(len(runtime))):
        raise EcologyError('runtime IDs must be unique and ordered to match direct-indexed art/name tables')
    if len({species['scientific_name'].casefold() for species in runtime}) != len(runtime):
        raise EcologyError('duplicate runtime scientific identity')
    for species in runtime:
        allowed_fields(species, {'id','name','scientific_name','art','region','time','spot','behavior','behavior_params','facts','source'}, 'runtime species')
        if len(species['name'])>16 or len(species['scientific_name'])>47 or len(species['facts'])!=3 or any(len(f)>20 or not f.isascii() for f in species['facts']):
            raise EcologyError('native species text exceeds authored display bounds')
        if species['behavior'] not in {'protected','freeze','wedge','glide','hop','push_up','slow_walk','dash_settle','water_emerge','night_peek','natural_display','rain_arrival'}:
            raise EcologyError('unknown behavior profile')
        params=species.get('behavior_params',{})
        allowed_fields(params, {'period','minimum_distance','stress_threshold'}, 'behavior parameters')
        for key,default,low,high in [('period',90,1,255),('minimum_distance',2,2,4),('stress_threshold',4,1,255)]:
            value=params.get(key,default)
            if type(value) is not int or not low<=value<=high:
                raise EcologyError('invalid byte-sized behavior parameter')
        record = lookup.get(species['id'])
        if record is None or species['scientific_name'] != record['canonical_scientific_name']:
            raise EcologyError('runtime identity lacks an ecology record')
        region = policy['runtime_region_aliases'].get(species['region'])
        if region is None:
            raise EcologyError('unknown runtime district alias')
        permission=next((p for p in record['region_permissions'] if p['region_id']==region),None)
        if permission is None:
            raise EcologyError('runtime region is not source-supported')
    return {species['id'] for species in runtime}

def validate_runtime_species(root=ROOT):
    policy = json.loads((root/'data/roster_policy.json').read_text())
    registry = json.loads((root/'data/species_ecology.json').read_text())
    runtime = json.loads((root/'data/species.json').read_text())
    runtime_ids = validate_runtime_rows(policy, registry, runtime)
    sites = json.loads((root/'data/foundation_encounters.json').read_text())
    placed = validate_encounters(policy, registry, sites, json.loads((root/'data/world.json').read_text()))
    if placed != runtime_ids:
        raise EcologyError('runtime species/encounter coverage mismatch')
    return len(runtime)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', action='store_true', help='Require all 150+1 reviewed species; expected to fail until production is complete.')
    args = parser.parse_args()
    try:
        count = validate_runtime_species()
        if args.release:
            validate_registry(json.loads((ROOT/'data/roster_policy.json').read_text()), json.loads((ROOT/'data/species_ecology.json').read_text()), release=True)
        print(f'Ecology preflight passed for {count} implemented species; planned target is 150 regular + 1 hidden.')
    except EcologyError as exc:
        parser.exit(1, f'Ecology preflight failed: {exc}\n')
