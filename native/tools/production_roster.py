"""Consolidate reviewed research and integrate the authored first production wave."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def write(p,v):(ROOT/p).write_text(json.dumps(v,indent=2)+'\n')
reptiles=[s for s in read('research/roster/verified-reptiles.json')['rows'] if s['review_status']=='source_reviewed']
amphibians=[s for s in read('research/roster/verified-amphibians.json')['species'] if s['review_status']=='source_reviewed']
lookup={s['scientific_name']:s for s in reptiles+amphibians}
assert len(lookup)==151,'Do not silently revise the roster target'
if len(read('data/species.json'))>18:
 raise RuntimeError('Historical first-wave scaffolder refuses to truncate the statewide roster. Use integrate_species.py for current species and reviewed canonical data.')
base=read('data/species.json')[:6]
wave=[
('Sceloporus occidentalis','FENCE LIZARD','fence_lizard','D04','rock_perch','push_up','day',['IT BASKS ON ROCKS.','BLUE COLOR ON BELLY.','WATCH THE PUSH-UPS.']),
('Taricha torosa','CALIFORNIA NEWT','newt','D08','shaded_creek','slow_walk','day',['IT WALKS ON LAND.','BREEDS IN WATER.','LOOK. DO NOT HANDLE.']),
('Pseudacris regilla','CHORUS FROG','chorus_frog','D08','freshwater_edge','hop','night',['A DARK EYE STRIPE.','LOOK BY FRESH WATER.','WATCH WITHOUT TOUCH.']),
('Ambystoma californiense','TIGER SALAMANDER','tiger_salamander','D06','grassland_burrow','slow_walk','night',['YELLOW SPOTS ON DARK.','IT USES SPRING POOLS.','LEAVE BURROWS ALONE.']),
('Xantusia riversiana','ISLAND N LIZARD','island_night_lizard','D12','island_scrub','night_peek','day',['AN ISLAND LIZARD.','LOOK IN DAYLIGHT.','LET IT STAY IN COVER.']),
('Elgaria multicarinata','S ALLIGATOR LIZ','alligator_lizard','D15','rock_log_cover','dash_settle','day',['LONG BODY AND TAIL.','SMALL LEGS MOVE IT.','LEAVE ITS COVER SAFE']),
('Coleonyx variegatus','BANDED GECKO','banded_gecko','D01','desert_rock_cover','dash_settle','night',['IT MOVES AFTER DARK.','BANDS CROSS ITS BODY.','KEEP ITS COVER SAFE.']),
('Dipsosaurus dorsalis','DESERT IGUANA','desert_iguana','D01','desert_wash','push_up','day',['A DESERT PLANT EATER','IT BASKS IN WARMTH.','WATCH FROM FAR AWAY.']),
('Lichanura orcutti','ROSY BOA','rosy_boa','D01','desert_canyon','glide','dusk',['LONG STRIPES ON BODY.','IT MOVES SLOWLY.','DO NOT PICK IT UP.']),
('Actinemys marmorata','NORTHWEST TURTLE','western_pond_turtle','D06','freshwater_pond','water_emerge','day',['A FRESHWATER TURTLE.','IT BASKS ABOVE WATER.','STAY BACK FROM WATER']),
('Aneides lugubris','ARBOREAL SALAM.','arboreal_salamander','D04','oak_tree_cover','slow_walk','night',['IT CAN CLIMB TREES.','DAMP COVER HELPS IT.','LOOK WITHOUT TOUCH.']),
('Rana sierrae','SIERRA YL FROG','yellow_legged_frog','D05','mountain_lake_edge','water_emerge','day',['A HIGH-COUNTRY FROG.','ITS LEGS ARE YELLOW.','KEEP THE LAKE CLEAN.'])]
order=[s['scientific_name'] for s in base]+[v[0] for v in wave]
secret='Batrachoseps wakei'
order += sorted(set(lookup)-set(order)-{secret});order.append(secret)
assert len(order)==151 and len(set(order))==151
records=[]
for sid,name in enumerate(order):
    s=lookup[name];permissions=[]
    for p in s['region_permissions']:
        assert p.get('habitat_review_status','source_reviewed')=='source_reviewed'
        permissions.append({'region_id':p['region_id'],'habitat_ids':p['habitat_ids'],'evidence_urls':p['evidence_urls'],'checked_on':'2026-10-12','review_status':'source_supported','evidence_scope':'broad_region_and_habitat_only','evidence_notes':s.get('taxonomy_native_range_notes','Current species taxonomy and conservative source-supported broad district; independent production review pending.')})
    records.append({'species_id':sid,'guide_number':sid+1,'canonical_scientific_name':name,'common_name':s['common_name'],'group':'Amphibia' if s in amphibians else 'Reptilia','native_in_california':True,'status':'source_reviewed','hidden':sid==150,'region_permissions':permissions,'release_review_status':'pending_independent_taxonomy_ecology_text_art_and_gameplay_review','production_gates':{'art_authored':sid<18,'native_integrated':False,'native_observed':False,'independent_review':False,'human_review':False}})
write('data/production_roster.json',{'schema_version':1,'authority_policy':{'Reptilia':'SSAR2025','Amphibia':'AMNH ASW6.2 current; unresolved chorus complex conservatively one species'},'scope':'151 source-reviewed research species; not151 implemented or release-approved species','records':records})
policy=read('data/roster_policy.json');policy['hidden_discovery']['taxon_assignment']=secret;policy['hidden_discovery']['taxon_status']='source_reviewed_pending_art_clue_chain_runtime_and_release_review';policy['runtime_region_aliases'].update({f'D{i:02d}':f'D{i:02d}' for i in range(1,17)});write('data/roster_policy.json',policy)
for sid,v in enumerate(wave,6):
    name,label,art,region,habitat,behavior,time,facts=v
    facts=[f.rstrip('.') if len(f)>20 else f for f in facts]
    assert len(label)<=16 and all(len(f)<=20 for f in facts),(label,facts)
    permission=next(p for p in lookup[name]['region_permissions'] if p['region_id']==region)
    assert habitat in permission['habitat_ids']
    base.append({'id':sid,'name':label,'scientific_name':name,'art':art,'region':region,'time':time,'spot':habitat,'behavior':behavior,'behavior_params':{'period':80 if behavior=='hop' else 90,'minimum_distance':2,'stress_threshold':4},'facts':facts,'source':permission['evidence_urls'][0]})
write('data/species.json',base)
ecology=read('data/species_ecology.json');ecology['scope']='first18 source-supported species; release review pending';ecology['records']=ecology['records'][:6]+ [{k:v for k,v in record.items() if k not in ('common_name','production_gates')} for record in records[6:18]];write('data/species_ecology.json',ecology)
# Actual authored routes. Broad names contain no real localities or coordinates.
world=read('data/world.json');world['maps']=world['maps'][:2]
layouts={
'D01':['GGSSSSSGGG','SCSSCTSSGS','SJSSTSSCSS','SjSSTTTTTT','SSSCTSSGSS','SCSSSSSCCS','GGSSGSSSGG'],
'D04':['GGSSCSSCGG','SCSSSTSCSS','SSCSSTSSCS','TTTTTTTTTT','SCSSCTSSCS','SSSSSTSSSS','GGCSCSSCGG'],
'D05':['GGGSSSSGGG','SGSSCTWWGS','SSSCTSWWSG','TTTTTTTTTT','SSGGSTSCSS','SCSSSTSSCS','GGGSSSSGGG'],
'D06':['CSSSSCCSSC','SWWSTSSCWS','SWWSTSSWWS','TTTTTTTTTT','SCWWSTSCCS','SSWWSTSSCS','CCSSSCSSCC'],
'D08':['CCSSSSSCCC','CSSSCSTWWC','SSCCSSTWWC','TTTTTTTTTT','CSCCSSTCSC','CCSSSSTSSC','CCCWWWCCCC'],
'D09':['GGGSSSSCGG','GWWSSCTSSS','GWWSCSTCSS','TTTTTTTTTT','SSCSSCTSSG','SCSSSSSCCG','GGSSCSSGGG'],
'D12':['WWWSSSSWWW','WWSSTSSSWW','WSSCTSSCSW','TTTTTTTTTT','WSSSSCTSSW','WWSSSCSSWW','WWWSSSSWWW'],
'D15':['GGGSSSSGGG','GGSCSTSSGG','SSSCSTSSCS','TTTTTTTTTT','SGSSSTSCCS','GSSSSSSSGG','GGGSSSSGGG']}
routes=[('D01','MOONLIT ROCK WASH',[12,13,14]),('D04','OAK ROCK CORRIDOR',[6,16]),('D08','FERN CREEK TRAIL',[7,8]),('D06','SEASONAL POOL BANK',[9,15]),('D12','MARITIME SCRUB',[10]),('D15','VOLCANIC FOREST',[11]),('D05','SNOWMELT LAKE',[17]),('D09','FOGGY WOOD CANYON',[7,16])]
sites=read('data/foundation_encounters.json');sites['records']=sites['records'][:7];sites['scope']='authored_game_sites_only; positions are fictional game tiles'
for region,label,ids in routes:
    mid=len(world['maps']);rows=list(layouts[region]);camp=[1,4]
    world['maps'].append({'id':mid,'district_id':region,'name':label,'terrain':rows,'west':None,'east':None,'camp':camp,'art_style':'regional','investigation_target':len(ids)})
    taken=set()
    for sid in ids:
        p=next(p for p in records[sid]['region_permissions'] if p['region_id']==region)
        habitat=wave[sid-6][4] if region==wave[sid-6][3] else p['habitat_ids'][0]
        assert habitat in p['habitat_ids']
        wet=any(k in habitat for k in ('water','lake','creek','pond'))
        options=[(x,y) for y in (2,4,1,5) for x in range(3,9) if rows[y][x] not in 'GWJj' and (x,y) not in taken]
        if wet:
            options.sort(key=lambda pos:min(abs(pos[0]-x)+abs(pos[1]-y) for y,row in enumerate(rows) for x,c in enumerate(row) if c=='W'))
        x,y=options[0];taken.add((x,y))
        interaction=7 if wet else 2 if 'burrow' in habitat else 6 if 'cover' in habitat or 'tree' in habitat else 1
        phase={'day':1,'dusk':2,'night':4}[base[sid]['time']]
        sites['records'].append({'spot_id':len(sites['records']),'room_id':mid,'game_tile_x':x,'game_tile_y':y,'interaction_type':interaction,'species_id':sid,'phase_mask':phase,'region_id':region,'habitat_id':habitat})
write('data/world.json',world);write('data/foundation_encounters.json',sites)
print('Integrated18 species,10 authored maps,8 district identities; full151research roster preserved.')
