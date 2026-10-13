"""Stage useful native N/S loops while preserving canonical map/site identities.

Default writes output/world-branches only. Root must explicitly authorize and
invoke --install-world to replace world.json; compiler/engine edits are separate.
Ports use each destination's opposite portal column, not the source column.
"""
from pathlib import Path
from collections import defaultdict, deque, Counter
import argparse, copy, hashlib, heapq, json
from expand_world import adjacent, reachable, watery
from validate_species import reject_localities, validate_placement

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/world-branches"
PREFERRED = [4, 5, 3, 6, 2, 7, 1, 8]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def route_order(group):
    """Stable W/E order, accepting an appended correction screen without metadata."""
    lookup = {m['id']: m for m in group}
    first = [m for m in group if m['west'] not in lookup]
    ordered, seen = [], set()
    for start in sorted(first, key=lambda m: m.get('route_sequence', m['id'])):
        m = start
        while m['id'] not in seen:
            ordered.append(m); seen.add(m['id'])
            if m['east'] not in lookup: break
            m = lookup[m['east']]
    ordered.extend(sorted((m for m in group if m['id'] not in seen),
                          key=lambda m: m.get('route_sequence', 10000 + m['id'])))
    return ordered

def occupied(m, sites):
    return {(s['game_tile_x'], s['game_tile_y']) for s in sites} | \
        ({tuple(m['camp'])} if m['camp'] else set())

def carve_port(m, direction, sites):
    """Least destructive route from reachable land to a marked boundary portal.

    Water, Joshua/tree formations, encounter/camp cells are never carved.
    Dijkstra charges blocked granite twenty steps; existing ground one step.
    The preferred column is only a tiebreaker after minimum destructive edits.
    """
    obstacles = occupied(m, sites)
    land = reachable(m, obstacles=obstacles)
    row = 0 if direction == 'north' else 6
    plans = []
    for rank, x in enumerate(PREFERRED):
        end = (x, row)
        if end in obstacles or m['terrain'][row][x] in 'WJj': continue
        q = [(0, 0, end, [end])]; best = {}
        while q:
            cuts, steps, p, path = heapq.heappop(q)
            if p in best: continue
            best[p] = (cuts, steps)
            if p in land:
                plans.append((cuts, rank, steps, x, list(reversed(path))))
                break
            for n in adjacent(*p):
                c = m['terrain'][n[1]][n[0]]
                if n in obstacles or c in 'WJj' or n in best: continue
                heapq.heappush(q, (cuts + (c == 'G'), steps + 1, n, path + [n]))
    assert plans, ('No safe portal corridor', m['id'], direction)
    _, _, _, x, path = min(plans)
    edits = []
    mark = set(path[-2:])
    inward = (x, 1 if direction == 'north' else 5)
    if inward in land and inward not in obstacles:
        mark.add(inward)
        if inward not in path: path.append(inward)
    for px, py in path:
        old = m['terrain'][py][px]
        if old == 'G' or (px, py) in mark:
            if old != 'T':
                line = list(m['terrain'][py]); line[px] = 'T'
                m['terrain'][py] = ''.join(line)
                edits.append({'x': px, 'y': py, 'before': old, 'after': 'T'})
    return x, edits

def pairs_for(group, district):
    if district != 'D12':
        assert len(group) >= 14, (district, len(group))
        return [(group[a], group[b]) for a, b in [(2,6),(5,10),(8,13)]]
    # Actual island identity is represented by source subarea: never shortcut
    # across northern woodland / southern scrub and silently bypass the ferry.
    islands = defaultdict(list)
    for m in group: islands[m['subarea_id']].append(m)
    per_island = []
    for key in sorted(islands):
        g = islands[key]
        per_island.append([(g[a],g[b]) for a,b in [(1,5),(2,6),(0,4),(3,7)] if b<len(g)])
    candidates = [g[i] for i in range(4) for g in per_island if i<len(g)]
    chosen, used = [], set()
    # Round robin among island groups, maintaining three substantial loops.
    for a,b in candidates:
        if a['id'] in used or b['id'] in used: continue
        chosen.append((a,b)); used.update((a['id'],b['id']))
        if len(chosen)==3: break
    assert len(chosen)==3, ('Island loop capacity', islands.keys())
    return chosen

def stage(source, encounters):
    world = copy.deepcopy(source)
    maps = {m['id']:m for m in world['maps']}
    bysite, groups = defaultdict(list), defaultdict(list)
    for s in encounters['records']: bysite[s['room_id']].append(s)
    for m in maps.values():
        m.update(north=None, south=None, north_x=255, south_x=255)
        if not (m.get('hidden') or m.get('hidden_reserved')):
            groups[m['district_id']].append(m)
    loops=[]
    for district in sorted(groups):
        group=route_order(groups[district])
        for index,(a,b) in enumerate(pairs_for(group,district)):
            assert a['north'] is None and b['south'] is None
            ax, ae=carve_port(a,'north',bysite[a['id']])
            bx, be=carve_port(b,'south',bysite[b['id']])
            a['north'],a['north_x']=b['id'],ax
            b['south'],b['south_x']=a['id'],bx
            loops.append({'id':district+'-LOOP-'+str(index+1), 'district':district,
                          'from_map':a['id'],'from_name':a['name'],'north_x':ax,
                          'to_map':b['id'],'to_name':b['name'],'south_x':bx,
                          'ordinary_screen_distance':group.index(b)-group.index(a),
                          'choice':'Take the marked north trail or follow the longer east/west investigation route.',
                          'terrain_edits':{str(a['id']):ae,str(b['id']):be}})
    return world, loops

def audit(source, world, encounters, loops):
    reject_localities(world)
    old={m['id']:m for m in source['maps']};maps={m['id']:m for m in world['maps']}
    roster={r['species_id']:r for r in json.loads((ROOT/'data/production_roster.json').read_text())['records']}
    assert set(old)==set(maps)
    bysite=defaultdict(list)
    for s in encounters['records']: bysite[s['room_id']].append(s)
    proofs=[]
    for mid,m in maps.items():
        # Metadata/biology and existing world graph may never change as a side
        # effect of navigation. Native geometry is the only mutable old field.
        for k,v in old[mid].items():
            if k not in ('terrain','north','south','north_x','south_x'):
                assert m[k]==v,('Changed stable metadata',mid,k)
        obstacles=occupied(m,bysite[mid]);land=reachable(m,obstacles=obstacles)
        assert (0,3) in land and (9,3) in land, ('W/E access',mid)
        if m['camp']: assert any(p in land for p in adjacent(*m['camp'])),('Camp access',mid)
        for s in bysite[mid]:
            assert any(p in land for p in adjacent(s['game_tile_x'],s['game_tile_y'])),('Site access',mid,s['spot_id'])
            validate_placement(roster[s['species_id']],s['region_id'],s['habitat_id'],m.get('subarea_id'))
            if watery(s['habitat_id']):
                assert any(m['terrain'][y][x]=='W' for x,y in adjacent(s['game_tile_x'],s['game_tile_y'])),('Water habitat',s['spot_id'])
        for key,row,opposite,arrival_row in [('north',0,'south',6),('south',6,'north',0)]:
            dest=m[key];x=m[key+'_x']
            if dest is None: assert x==255;continue
            assert mid!=dest and 1<=x<=8 and (x,row) in land
            target=maps[dest];arrival=(target[opposite+'_x'],arrival_row)
            assert target[opposite]==mid and m['district_id']==target['district_id']
            assert not (m.get('hidden') or m.get('hidden_reserved') or target.get('hidden') or target.get('hidden_reserved'))
            if m['district_id']=='D12': assert m['subarea_id']==target['subarea_id']
            targetland=reachable(target,start=arrival,obstacles=occupied(target,bysite[dest]))
            assert (0,3) in targetland and (9,3) in targetland,('Arrival collision trap',mid,dest)
            proofs.append({'from':mid,'direction':key,'exit':[x,row],
                           'to':dest,'arrival':list(arrival),'arrival_reachable_tiles':len(targetland)})
    assert len({tuple(m['terrain']) for m in maps.values()})==len(maps),'Duplicate modified collision layouts'
    counts=Counter(loop['district'] for loop in loops)
    assert len(counts)==16 and all(n==3 for n in counts.values())
    assert len(proofs)==96 and all(loop['ordinary_screen_distance']>=3 for loop in loops)
    return {'status':'staged_structural_biology_and_native_collision_audit_passed',
            'native_observed':False,'release_approved':False,'maps':len(maps),
            'sites_preserved':len(encounters['records']),'bidirectional_loops':len(loops),
            'directed_portals':len(proofs),'loops_per_district':dict(counts),
            'hidden_isolation_preserved':True,'island_identity_preserved':True,
            'west_east_graph_preserved':True,'source_habitat_permissions_preserved':True,
            'portal_proofs':proofs,'loops':loops,
            'integration_contract':{'RFMap_append':'UWORD north,south; UBYTE north_x,south_x;',
                'none_neighbor':65535,'none_column':255,
                'north_arrival':'destination.south_x, y=6',
                'south_arrival':'destination.north_x, y=0',
                'require_exit_column':True,'canonical_sites_unchanged':True},
            'remaining_gates':['root compiler/engine movement integration','regenerated indexed map art',
                               'native controller trace all96 directions and reverse arrivals',
                               'fresh full-world save/stack/OAM regression','human navigation/fun review']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install-world',action='store_true',help='Root-authorized canonical installation; default is staging only.')
    args=parser.parse_args();wp=ROOT/'data/world.json';ep=ROOT/'data/foundation_encounters.json'
    hashes={'world':digest(wp),'encounters':digest(ep),'roster':digest(ROOT/'data/production_roster.json')}
    source=json.loads(wp.read_text());encounters=json.loads(ep.read_text())
    world,loops=stage(source,encounters);proof=audit(source,world,encounters,loops)
    assert hashes=={'world':digest(wp),'encounters':digest(ep),'roster':digest(ROOT/'data/production_roster.json')},'Inputs changed while staging; rerun against latest source.'
    proof['input_sha256']=hashes;OUT.mkdir(parents=True,exist_ok=True)
    staged=json.dumps(world,indent=2)+'\n';(OUT/'world.json').write_text(staged)
    proof['staged_world_sha256']=hashlib.sha256(staged.encode()).hexdigest()
    proof['canonical_installed']=args.install_world
    (OUT/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
    if args.install_world:wp.write_text(staged)
    print(json.dumps({k:v for k,v in proof.items() if k not in ('loops','portal_proofs')},indent=2))

if __name__=='__main__':main()
