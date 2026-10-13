"""Author the statewide screen-flip source world and audit its fictional sites.

This is a source-content milestone, not release approval. No wildlife coordinates.
Geometry is composed from curated seven-row route plans, district formations,
and exact roster habitat/subarea permissions. Existing stable identities survive.
"""
from pathlib import Path
from collections import defaultdict, deque, Counter
import json, hashlib, argparse

ROOT=Path(__file__).resolve().parents[2]
BLOCKED=set('GWJj')
# Fifteen deliberately composed routes: switchbacks, forked internal paths,
# sheltered bowls, stepping banks, narrow ridges, and connected side clearings.
# Exit corridor cells are always on row three because that is the native ABI.
PLANS=[
 ['GGSSSSCCGG','GSSCTTSSCG','SSCTTSCCSS','TTTTTTSTTT','SSCCSTTSSS','GSSSCTTSCG','GGSSSSCCGG'],
 ['CCSSSSSSCC','CSSTTCSSSC','SSTTCCSSSS','TTTSSSSTTT','SSSTTCCSSS','CSSTTSSSCC','CCSSSSSSCC'],
 ['GGSSCSSSGG','GSSSCTTSSG','SSSCTTSCSS','TTTTTSSSTT','SSCTTSCSCS','GSSSTTSSSG','GGSSCSSSGG'],
 ['CSSSSSSSSC','SSCCSTTCCS','SSTTTTSCCS','TTTSSSTTTT','SCCSTTSSSS','SSSSTTCCSS','CSSSSSSSSC'],
 ['GGSSSSSSGG','GSSCTTTSSG','SSCTTCSTTS','TTTTSSSSTT','SSCTTCSSSS','GSSCTTTSSG','GGSSSSSSGG'],
 ['CCSSCSSSCC','CSSTTSSSSC','SSTTCCTTSS','TTSSSSTTTT','SSCCSTTSSS','CSSSSTTCSC','CCSSCSSSCC'],
 ['GGSSSSSCGG','GSSCSTTSSG','SSTTCCTTSS','TTTSSSSTTT','SSTTCSTTSS','GSSCSTTSSG','GGSSSSSCGG'],
 ['CSSSSCSSSC','SSCTTTCCSS','STTTSSSTTS','TTSSSSTTTT','SSCTTSSSCS','SCCSTTTSSS','CSSSSCSSSC'],
 ['GGSCSSSSGG','GSSSTTCCSG','SSTTTSSCCS','TTSSSSTTTT','SSCCSSTTSS','GSSCTTSSSG','GGSCSSSSGG'],
 ['CCSSSSSSCC','CSSCTTTSSC','SSTTCCSTTS','TTSSSTTTTT','SSSTTCCSSS','CSSTTTCCSC','CCSSSSSSCC'],
 ['GGSSCSSCGG','GSSSTTTSSG','SCTTSSSTTS','TTTSSSSTTT','SSSTTCCSSS','GSSSCTTSSG','GGSSCSSCGG'],
 ['CSSSSSSCCC','SSCTTSSSCS','STTSSCTTSS','TTSSSSTTTT','SSCCSTTSSS','SSTTTCCSSS','CSSSSSSCCC'],
 ['GGSSSCSSGG','GSSSTTTCSG','SSTTCSSCCS','TTSSSSTTTT','SCCSSTTSSS','GSSCTTTSSG','GGSSSCSSGG'],
 ['CCSSSSSCCC','CSSTTTCCSC','SSTTSSSTTS','TTTSSSSTTT','SSCTTCCSSS','CSSCTTTSSC','CCSSSSSCCC'],
 ['GGSSSSCCGG','GSSTTTTSSG','SSTTCSSTTS','TTSSSSTTTT','SSSTTCCSSS','GSSSTTTCSG','GGSSSSCCGG'],
]
# Names are authored landmarks, not real natural-history collection localities.
NAMES={
 'D01':['JOSHUA GATE','SUNBAKED FAN','TRACK DUNE','BASALT STEPS','CREOSOTE TURN','SHADOW PASS','PEBBLE WASH','DRY FALL BOWL','CACTUS LOOKOUT','WIND ARCH','PALE RIDGE','RAINSTONE HOLLOW','BROKEN MESA','YUCCA TURNOUT','DAWN CAMP'],
 'D02':['LOW DESERT GATE','RAINPOOL PLAIN','PALM WASH','GRAVEL FAN','SAND RIBBON','DRY CANYON','GRANITE SHELF','DUNE HOLLOW','RIVER REEDS','SANDSTONE ALCOVE','SALT TURN','OCOTILLO BEND','MICA GULLY','SUNSET LEDGE','FAN CAMP'],
 'D03':['BASIN GATE','SPRING MARSH','COLD SPRING','SAGE TURN','VALLEY WATER','TALUS STAIR','ALKALI EDGE','RABBITBRUSH WAY','WIND BASIN','PUMICE PASS','JUNIPER SHELF','REED POCKET','SILVER FLATS','BASALT KNOLL','BASIN CAMP'],
 'D04':['OAK TRAILHEAD','UPPER CANYON','WESTERN SLOPE','OAK LITTER BOWL','SHADY DRAIN A','SHADY DRAIN B','SEEP WOOD','LOW CANYON','TRANSITION RIDGE','LIMESTONE BOWL','CREEK SWITCHBACK','GRASS SADDLE','GRANITE GATE','ROOT TURN','OAK CAMP'],
 'D05':['HIGH COUNTRY GATE','NORTHERN LAKE','WETLAND MEADOW','SOUTH CONIFER','SHADY HEADWATER A','SHADY HEADWATER B','PLATEAU WOOD','SOUTH LAKE SHELF','PINE SWITCHBACK','GRANITE BRIDGE','SNOWMELT BANK','TALUS WINDOW','COLD POOL BOWL','HIGH MEADOW','PINE CAMP'],
 'D06':['RIVER TRAILHEAD','VERNAL BASIN','OAK MEADOW','REED BANK','WILLOW TURN','POOL OVERLOOK','SILT BAR','GRASSLAND LOOP','FLOODPLAIN EDGE','SHADY BACKWATER','COTTONWOOD WALK','VALLEY CHANNEL','WET MEADOW BEND','POOL BOARDWALK','RIVER CAMP'],
 'D07':['VALLEY TRAILHEAD','SCRUB REMNANT','DUNE GRASS TURN','WETLAND REMNANT','VERNAL RIM','BURROW FLATS','DRY CREEK BED','TULE SHELF','GRASS HOLLOW','SALT EDGE','OAK ISLET','SANDY MEADOW','POOL RIBBON','SHADE CORRIDOR','VALLEY CAMP'],
 'D08':['BAY TRAILHEAD','PENINSULA RIDGE','SOUTHERN WOOD','FERN SWITCHBACK','OAK MOSS BANK','SHADY STREAM','SAGE SADDLE','COAST ROCK TURN','LEAF LITTER BOWL','CREEK ROOTS','GRANITE WINDOW','WOODLAND STAIR','POND OVERLOOK','FOG MEADOW','BAY CAMP'],
 'D09':['COAST TRAILHEAD','SEASONAL POOL','INLAND OAKS','MIST WOOD A','NORTH MIST WOOD','SOUTH MIST WOOD','OFFSHORE VIEW','COAST RANGE CREEK','INLAND WOOD TURN','QUIET REFUGE','SAGE BLUFF','MOSS GULLY','MARITIME HOLLOW','SHORE OVERLOOK','COAST CAMP'],
 'D10':['SOUTH COAST GATE','BAY OBSERVATORY','BORDER SCRUB','SAGE TERRACE','SANDY POOL','COAST WOODLAND','CANYON SHADE','ROCKY STREAM','PALM HOLLOW','DUNE SHOULDER','OAK ROOT TURN','CHAPARRAL BOWL','SALT AIR BLUFF','WET GRASS BEND','SOUTH COAST CAMP'],
 'D11':['MOUNTAIN GATE','MIST GRANITE','CONIFER REFUGE','BORDER UPLANDS','RESTORED POOL','GRANITE SLOPE','ROCKY SADDLE','SHADY HEADWATER','OAK PINE TURN','BOULDER WINDOW','CANYON RIBBON','CHAPARRAL STAIR','RAIN-SEEP BOWL','PINE NEEDLE WAY','MOUNTAIN CAMP'],
 'D12':['ISLAND LANDING','SOUTH SCRUB','NORTH WOODLAND','SALT WIND RIDGE','CACTUS HOLLOW','LEAF LITTER BAY','ROCKY ISLAND TURN','SCRUB TERRACE','SHADE ISLET','WOODLAND SHELF','MARITIME GRASS','COAST CREVICE','NORTH DOCK','SOUTH DOCK','ISLAND CAMP'],
 'D13':['FOREST TRAILHEAD','MARITIME WOOD','HILL FOREST','COAST TALUS','SOUTH MIST WOOD','MARITIME STREAM','FERN GULLY','RAIN LOG BOWL','CEDAR SWITCHBACK','RIVER ROCK BANK','CANOPY WINDOW','MOSS BOULDER','FALLEN FIR','COLD CREEK TURN','FOREST CAMP'],
 'D14':['KLAMATH GATE','INLAND FOOTHILL','NORTH TALUS','KARST POCKET A','KARST POCKET B','KARST POCKET C','TALUS POCKET A','LIMESTONE STAIR','CONIFER CANYON','RAIN ROCK SHELF','DAMP RIDGE','OAK PINE BORDER','SEEP SWITCHBACK','FOREST STREAM','KLAMATH CAMP'],
 'D15':['CASCADE GATE','NORTH WETLAND','LAVA STAIR','CONIFER POOL','VOLCANIC HOLLOW','FIR NEEDLE WAY','MEADOW SEEP','COOL ROCK BOWL','LAVA WINDOW','COLD HEADWATER','PINE LAKE BEND','MOSSY CREVICE','RAIN LOG TURN','WET TALUS BANK','CASCADE CAMP'],
 'D16':['PLATEAU GATE','SAGEBRUSH FAN','JUNIPER PASS','SEASONAL POOL','BASALT RIDGE','SAGE CREEK BANK','LAVA HOLLOW','GRAVEL SWITCHBACK','PINE BORDER','WIND MEADOW','COOL STONE SHELF','DAMP GRASS POOL','OPEN WOOD TURN','SAGE SADDLE','PLATEAU CAMP'],
}
# Hand-composed district-specific formations occupy meaningful multi-tile areas,
# rather than stamping the same screen with a different palette. C is rendered
# through the district kit (boulder, shrub, reed, or forest cover); G is impassable
# relief. Water is added only for supported waterside habitat observations.
FORMATIONS={
 'D01':[(0,0,'GGSS'),(6,5,'CCSS'),(3,1,'CS')],
 'D02':[(0,0,'SSGG'),(5,6,'SSCC'),(6,1,'CSC')],
 'D03':[(0,0,'GSSGG'),(5,6,'GGSSG'),(2,1,'SS')],
 'D04':[(0,0,'CSSCC'),(6,6,'CCSC'),(1,5,'CC')],
 'D05':[(0,0,'GGGSS'),(5,6,'SSGGG'),(1,1,'GC')],
 'D06':[(0,0,'SSCSS'),(5,6,'SCSSS'),(2,5,'SSS')],
 'D07':[(0,0,'SSSSS'),(5,6,'SSSCS'),(1,1,'SS')],
 'D08':[(0,0,'CCSSS'),(5,6,'SSSCC'),(6,1,'CC')],
 'D09':[(0,0,'GCCSS'),(5,6,'SSCCG'),(1,5,'CS')],
 'D10':[(0,0,'SSCCS'),(5,6,'CCSSS'),(6,5,'CS')],
 'D11':[(0,0,'GGCCS'),(5,6,'SCCGG'),(7,1,'GC')],
 'D12':[(0,0,'GGGSC'),(5,6,'CSGGG'),(1,1,'GS')],
 'D13':[(0,0,'CCCCC'),(5,6,'CCCCC'),(1,5,'CC')],
 'D14':[(0,0,'GCGCC'),(5,6,'CCGCG'),(1,1,'CG')],
 'D15':[(0,0,'CGGGC'),(5,6,'CGGGC'),(7,5,'GC')],
 'D16':[(0,0,'GSSCS'),(5,6,'SCSSG'),(6,1,'SSS')],
}
WATER_WORDS=('water','stream','creek','river','pond','pool','lake','marsh','seep','spring','wet_meadow','marine','offshore')
def watery(h):return any(s in h for s in WATER_WORDS)
def adjacent(x,y):
 return [(a,b) for a,b in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)] if 0<=a<10 and 0<=b<7]
def reachable(m,start=(0,3),obstacles=()):
 cells=set();q=deque([start]);ob=set(obstacles)
 while q:
  p=q.popleft()
  if p in cells or p in ob or m['terrain'][p[1]][p[0]] in BLOCKED:continue
  cells.add(p)
  q.extend(a for a in adjacent(*p) if a not in cells)
 return cells
def setcell(m,p,c):
 x,y=p;r=list(m['terrain'][y]);r[x]=c;m['terrain'][y]=''.join(r)
def type_for(h):
 if watery(h):return 7
 if h=='wet_rock_cover':return 5
 if h in ('desert_rock_cover','coastal_rock_cover','moist_rock_cover'):return 0
 if 'burrow' in h or 'soil' in h:return 2
 if 'sand' in h or 'dune' in h:return 3
 if 'perch' in h or 'canopy' in h or 'tree_cover' in h:return 8
 if any(a in h for a in ('log','litter','forest','moist_cover','woodland')):return 6
 if any(a in h for a in ('crevice','outcrop','talus','granite')):return 1
 if any(a in h for a in ('scrub','shrub','chaparral','sage','yucca')):return 4
 # Open grass, lava shelter, and a general canyon are observation clues, not
 # permission to lift loose stones or disturb a permanent shelter.
 return 9
def phases(r,runtime):
 if r['species_id'] in runtime:return {'day':1,'dusk':2,'night':4,'any':7}.get(runtime[r['species_id']].get('time'),7)
 # A temporary authored availability mask, explicitly not a seasonality claim.
 # Runtime behavior review must challenge these before release.
 genus=r['canonical_scientific_name'].split()[0]
 if genus in ('Rana','Sceloporus','Aspidoscelis','Uta','Urosaurus','Phrynosoma','Gopherus','Sauromalus','Dipsosaurus','Crotaphytus','Gambelia','Actinemys','Clemmys','Trachemys'):return 1
 if r['group']=='Amphibia' or genus in ('Coleonyx','Xantusia','Lichanura','Charina','Hypsiglena','Arizona','Chionactis','Chilomeniscus','Rena'):return 4
 return 3
def build():
 world=json.loads((ROOT/'data/world.json').read_text());enc=json.loads((ROOT/'data/foundation_encounters.json').read_text())
 # On repeat builds, retain the original identities only; new content is regenerated.
 maps=[m for m in world['maps'] if m['id']<10];sites=[s for s in enc['records'] if s['spot_id']<21]
 roster=json.loads((ROOT/'data/production_roster.json').read_text())['records'];lookup={r['species_id']:r for r in roster}
 runtime={r['id']:r for r in json.loads((ROOT/'data/species.json').read_text())}
 groups=defaultdict(lambda:defaultdict(list))
 for r in roster:
  for p in r['region_permissions']:
   sub=(p.get('subarea_ids') or ['broad_habitat_route'])[0]
   groups[p['region_id']][sub].append((r,p))
 districtmaps=defaultdict(list)
 for m in maps:districtmaps[m['district_id']].append(m)
 # Every district receives fifteen screens including retained foundation screens.
 for district in NAMES:
  legacy=districtmaps[district];subs=list(groups[district]);covered={m.get('subarea_id') for m in legacy}
  required=[s for s in subs if s not in covered]
  remaining=15-len(legacy)
  assert len(required)<=remaining,(district,required)
  allocation=required+[(subs[n%len(subs)]) for n in range(remaining-len(required))]
  for n,sub in enumerate(allocation):
   idx=len(legacy);mid=len(maps);terrain=list(PLANS[idx]);di=int(district[1:])-1
   m={'id':mid,'district_id':district,'name':NAMES[district][idx],'terrain':terrain,'west':None,'east':None,'camp':[1,4] if idx in (0,7,14) else None,'art_style':'regional','investigation_target':2,'subarea_id':sub,'route_plan_id':idx,'landmark':NAMES[district][idx].lower(),'habitat_ids':[],'production_status':'authored_source_pending_native_and_human_review'}
   for x,y,cells in FORMATIONS[district]:
    for offset,c in enumerate(cells):setcell(m,(x+offset,y),c)
   # Curated region formations change skyline, ground, and shelter distribution.
   # Interior corridors remain intact; this is not a random obstacle scatter.
   crest=[(2+(di%5),0),(1+(di*3%8),6),(1+(di*5%8),1),(1+(di*7%8),5)]
   for a,p in enumerate(crest):setcell(m,p,('C','G','C','S')[(a+di)%4])
   if district=='D01' and idx%3==0:setcell(m,(2,0),'J');setcell(m,(2,1),'j')
   if district in ('D13','D14','D15') and idx%3==1:setcell(m,(7,0),'J');setcell(m,(7,1),'j')
   if m['camp']:setcell(m,tuple(m['camp']),'T')
   setcell(m,(0,3),'T');setcell(m,(9,3),'T')
   maps.append(m);legacy.append(m)
 # Stage one exact supported permission on at least one matching subarea screen.
 assigned=defaultdict(list)
 already={(s['species_id'],s['region_id']) for s in sites}
 for district,subs in groups.items():
  for sub,entries in subs.items():
   matching=[m for m in districtmaps[district] if m.get('subarea_id')==sub]
   for r,p in entries:
    if (r['species_id'],district) in already:continue
    choices=[m for m in matching if m['id']>=10]
    if not choices:choices=matching
    dest=min(choices,key=lambda m:len(assigned[m['id']]))
    assigned[dest['id']].append((r,p,p['habitat_ids'][0]))
 # Place two diverse habitat observations on each ordinary added screen. Repeats
 # are an authored route population, never an extra species count.
 for m in maps[10:]:
  entries=groups[m['district_id']][m['subarea_id']]
  if any(r['hidden'] for r,p in entries):
   m['hidden_reserved']=True;m['hidden']=True;m['discovery_gate']='pending_exhibit_and_private_refuge_gate';m['camp']=None
  target=1 if m.get('hidden_reserved') else 2
  pool=[(r,p,h) for r,p in entries for h in p['habitat_ids'] if not r['hidden'] or m.get('hidden_reserved')]
  while len(assigned[m['id']])<target:
   n=(m['id']+len(assigned[m['id']]))%len(pool);assigned[m['id']].append(pool[n])
 # All ordinary maps form a reciprocal trail, ordered within district. The
 # hidden refuge has no default edge or camp. Borders represent expedition
 # transitions in source metadata; ferry/gate presentation is engine work.
 ordinary=[]
 for d in NAMES:
  group=[m for m in districtmaps[d] if not m.get('hidden_reserved')]
  if d=='D12':group.sort(key=lambda m:(m['subarea_id']!='southern_island_scrub',m['id']))
  ordinary.extend(group)
 for d in NAMES:
  first=next(m for m in districtmaps[d] if not m.get('hidden_reserved'))
  first['district_trailhead']=True
  if first['camp'] is None:first['camp']=[1,4]
 for i,m in enumerate(ordinary):
  m['route_sequence']=i
  m['west']=ordinary[i-1]['id'] if i else None;m['east']=ordinary[i+1]['id'] if i+1<len(ordinary) else None
  if i and ordinary[i-1]['district_id']!=m['district_id']:m['arrival_transition']='ferry' if m['district_id']=='D12' or ordinary[i-1]['district_id']=='D12' else 'expedition'
 for m in maps:
  if m['camp']:setcell(m,tuple(m['camp']),'T')
  m['camp_start']=bool(m['camp'])
  existing=[s for s in sites if s['room_id']==m['id']];used={(s['game_tile_x'],s['game_tile_y']) for s in existing}
  if m['camp']:used.add(tuple(m['camp']))
  used|={(0,3),(9,3)}
  pending=assigned[m['id']]
  # Water sites are reached from a bank: the site tile is legal ground and an
  # adjacent water tile is a visual habitat requirement. Never place on water.
  for r,p,h in pending:
   land=reachable(m);candidates=[]
   for x,y in land:
    if (x,y) in used or x in (0,9) or y in (0,6):continue
    neigh=adjacent(x,y)
    if not any(a in land and a not in used for a in neigh):continue
    occupied={(a['game_tile_x'],a['game_tile_y']) for a in sites if a['room_id']==m['id']}|{(x,y)}
    obstacles=occupied|({tuple(m['camp'])} if m['camp'] else set())
    native_land=reachable(m,obstacles=obstacles)
    if (9,3) not in native_land or not all(any(a in native_land for a in adjacent(*old)) for old in occupied):continue
    if m['camp'] and not any(a in native_land for a in adjacent(*m['camp'])):continue
    wet=[a for a in neigh if m['terrain'][a[1]][a[0]]=='W']
    candidates.append(((0 if wet else 1) if watery(h) else (1 if wet else 0),y,x))
   assert candidates,(m['id'],h)
   _,y,x=min(candidates)
   if watery(h) and not any(m['terrain'][b][a]=='W' for a,b in adjacent(x,y)):
    choices=[a for a in adjacent(x,y) if a not in used and a!=(x,y) and a[1]!=3 and a[0] not in (0,9)]
    choices.sort(key=lambda a:(m['terrain'][a[1]][a[0]] not in BLOCKED,a[1],a[0]))
    success=False
    for water in choices:
     old=m['terrain'][water[1]][water[0]];setcell(m,water,'W');land2=reachable(m)
     occupied={(a['game_tile_x'],a['game_tile_y']) for a in sites if a['room_id']==m['id']}|{(x,y)}
     native_land=reachable(m,obstacles=occupied|({tuple(m['camp'])} if m['camp'] else set()))
     if (x,y) in land2 and (9,3) in native_land and (m['camp'] is None or any(a in native_land for a in adjacent(*m['camp']))) and all(a in land2 for a in used if a!=(0,3)) and all(any(a in native_land for a in adjacent(*old)) for old in occupied):
      success=True;break
     setcell(m,water,old)
    assert success,('water bank',m['id'],h,x,y)
   s={'spot_id':len(sites),'room_id':m['id'],'game_tile_x':x,'game_tile_y':y,'interaction_type':type_for(h),'species_id':r['species_id'],'phase_mask':phases(r,runtime),'region_id':m['district_id'],'habitat_id':h};sites.append(s);used.add((x,y))
  m['habitat_ids']=sorted({s['habitat_id'] for s in sites if s['room_id']==m['id']})
  m['investigation_target']=min(3,max(1,len([s for s in sites if s['room_id']==m['id']])))
 # Retained water observations also need a visible nearby water feature.
 for s in sites[:21]:
  if not watery(s['habitat_id']):continue
  m=maps[s['room_id']];p=(s['game_tile_x'],s['game_tile_y'])
  if any(m['terrain'][b][a]=='W' for a,b in adjacent(*p)):continue
  protected={(a['game_tile_x'],a['game_tile_y']) for a in sites if a['room_id']==m['id']}|{(0,3),(9,3)}
  if m['camp']:protected.add(tuple(m['camp']))
  for w in adjacent(*p):
   if w in protected or w[1]==3:continue
   old=m['terrain'][w[1]][w[0]];setcell(m,w,'W');land=reachable(m)
   if protected<=land and any(a in land for a in adjacent(*p)):break
   setcell(m,w,old)
  else:raise AssertionError(('retained water habitat',s['spot_id']))
 # Collision plans should be genuinely distinct, even before district pixels.
 # Resolve any identical curated composition with an accessible edge alcove.
 patterns=set()
 for m in maps:
  t=tuple(m['terrain'])
  if t in patterns:
   for x in range(1,9):
    old=m['terrain'][0][x];setcell(m,(x,0),'C' if old!='C' else 'S')
    t=tuple(m['terrain'])
    if t not in patterns:break
   assert t not in patterns
  patterns.add(t)
 world={'schema_version':1,'scope':'statewide_authored_source_pending_native_and_independent_review','maps':maps}
 enc={'schema_version':1,'scope':'authored_game_sites_only; positions are fictional game tiles','locations_are_game_tiles_not_real_world':True,'records':sites}
 return world,enc

def audit(world,enc):
 from validate_species import validate_placement,reject_localities
 reject_localities(world);reject_localities(enc)
 roster=json.loads((ROOT/'data/production_roster.json').read_text())['records'];lookup={r['species_id']:r for r in roster}
 maps={m['id']:m for m in world['maps']};sites=enc['records'];byscreen=defaultdict(list)
 assert 240<=len(maps)<=400 and set(maps)==set(range(len(maps)));assert {s['spot_id'] for s in sites}==set(range(len(sites))) and len(sites)<=1000
 assert {s['species_id'] for s in sites}==set(range(151));assert len({tuple(m['terrain']) for m in maps.values()})==len(maps)
 for s in sites:byscreen[s['room_id']].append(s)
 proofs=[]
 for m in maps.values():
  assert len(m['terrain'])==7 and all(len(a)==10 and set(a)<=set('STCGWJjB') for a in m['terrain'])
  assert len(m['name'])<=20 and m['name'].isascii();assert len(byscreen[m['id']])<=16
  land=reachable(m);assert (9,3) in land
  if m['camp']:assert tuple(m['camp']) in land
  for direction,opposite in [('west','east'),('east','west'),('north','south'),('south','north')]:
   if m.get(direction) is not None:assert maps[m[direction]].get(opposite)==m['id']
  occupied={(s['game_tile_x'],s['game_tile_y']) for s in byscreen[m['id']]};assert len(occupied)==len(byscreen[m['id']])
  native_land=reachable(m,obstacles=occupied|({tuple(m['camp'])} if m['camp'] else set()))
  assert (9,3) in native_land,('native boundary path',m['id'])
  if m['camp']:assert any(a in native_land for a in adjacent(*m['camp'])),('native camp access',m['id'])
  for s in byscreen[m['id']]:
   r=lookup[s['species_id']];assert s['region_id']==m['district_id'];validate_placement(r,s['region_id'],s['habitat_id'],m.get('subarea_id'))
   p=(s['game_tile_x'],s['game_tile_y']);assert p in land and p not in ((0,3),(9,3)) and list(p)!=m['camp']
   assert any(a in native_land for a in adjacent(*p)),('interaction adjacency',m['id'],s['spot_id'])
   if watery(s['habitat_id']):assert any(m['terrain'][b][a]=='W' for a,b in adjacent(*p)),('water visual',s['spot_id'])
   assert s['interaction_type'] in range(10) and s['phase_mask'] in range(1,8)
  proofs.append({'map_id':m['id'],'district':m['district_id'],'subarea_id':m['subarea_id'],'reachable_land_tiles':len(land),'native_walkable_tiles':len(native_land),'site_count':len(byscreen[m['id']]),'terrain_sha256':hashlib.sha256('\n'.join(m['terrain']).encode()).hexdigest()})
 seen=set();q=[0]
 while q:
  mid=q.pop()
  if mid in seen:continue
  seen.add(mid);q.extend(maps[mid][a] for a in ('west','east') if maps[mid][a] is not None)
 hidden={m['id'] for m in maps.values() if m.get('hidden_reserved')}
 assert seen==set(maps)-hidden and len(hidden)==1
 assert all(s['room_id'] in hidden for s in sites if s['species_id']==150)
 assert all(maps[mid]['camp'] is None for mid in hidden)
 counts=Counter(m['district_id'] for m in maps.values());assert all(v>=15 for v in counts.values()) and len(counts)==16
 expected={(r['species_id'],p['region_id']) for r in roster for p in r['region_permissions']};covered={(s['species_id'],s['region_id']) for s in sites};assert expected==covered
 return {'status':'source_structural_and_roster_permission_checks_passed','native_observed':False,'release_approved':False,'map_count':len(maps),'unique_collision_layouts':len(maps),'connected_default_maps':len(seen),'hidden_reserved_maps':sorted(hidden),'species_coverage':151,'region_permission_pairs_covered':len(covered),'spot_count':len(sites),'maximum_sites_per_map':max(len(v) for v in byscreen.values()),'district_counts':dict(counts),'water_sites_have_visible_adjacent_water':True,'all_sites_have_reachable_legal_adjacent_land':True,'reciprocal_boundary_exits':True,'map_proofs':proofs,'remaining_gates':['independent ecology and human level-design challenge','runtime 151 integration and bank budgets','input-driven whole-world native playtest','hidden discovery unlock','ferry/expedition transition presentation','phase masks seasonal behavior challenge','story branches require engine exits beyond west/east']}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--audit-existing',action='store_true');a=p.parse_args()
 if a.audit_existing:w=json.loads((ROOT/'data/world.json').read_text());e=json.loads((ROOT/'data/foundation_encounters.json').read_text())
 else:
  if a.write and (ROOT/'data/world.json').exists() and len(json.loads((ROOT/'data/world.json').read_text())['maps'])>=240:
   raise RuntimeError('Historical world scaffolder refuses to replace reviewed statewide maps. Audit with --audit-existing; edit stable canonical records and use branch_world.py for topology.')
  w,e=build()
 proof=audit(w,e)
 if a.write:
  (ROOT/'data/world.json').write_text(json.dumps(w,indent=2)+'\n');(ROOT/'data/foundation_encounters.json').write_text(json.dumps(e,indent=2)+'\n')
 print(json.dumps({k:v for k,v in proof.items() if k!='map_proofs'},indent=2))
