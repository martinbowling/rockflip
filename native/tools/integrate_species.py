"""Materialize the frozen151 reviewed identities without modifying art/world/C.

Runtime time/animation timing are authored availability, not measurements or
exclusive natural activity. The source roster remains the regional authority.
First18 runtime rows are preserved verbatim. No new taxon or release approval.
"""
import argparse,copy,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'native/tools'))
from validate_species import validate_registry,validate_runtime_rows,validate_encounters,EcologyError
MANIFESTS=[
 'output/art-wave2-work/species-wave2-manifest.json',
 'output/art-wave3-reptiles-work/species-wave3-reptiles-manifest.json',
 'output/art-wave3-salamanders-work/species-wave3-salamanders-manifest.json',
 'output/art-wave3-frogs-work/species-wave3-frogs-manifest.json',
]
# Compact individually authored anatomical observations. These do not teach
# definitive identification of cryptic taxa; names/context still matter.
FACT0={
18:'A FRESHWATER TURTLE.',19:'A STOCKY SALAMANDER.',20:'A LONG FOURTH TOE.',21:'A PALE BACK STRIPE.',22:'A SMALL SANDY TOAD.',23:'A HIGH-MEADOW TOAD.',24:'PAIRED DARK PATCHES.',25:'A DARK SPRING TOAD.',
26:'CLOUDED BACK COLORS.',27:'FLECKS VARY BY FORM.',28:'MANY TINY SPECKLES.',29:'A FROSTED DARK FORM.',30:'A NEARLY BLACK FORM.',31:'LONG CLIMBING LEGS.',32:'A LEGLESS LIZARD.',33:'A LEGLESS LIZARD.',34:'SMOOTH SHINY SCALES.',35:'A FOREST STREAM FROG',36:'A SLENDER WHIPTAIL.',37:'LONG LEGS AND TAIL.',
38:'FOUR TOES EACH FOOT.',39:'A VERY SLENDER BODY.',40:'FOUR-TOED FEET.',41:'SLENDER SEEP DWELLER',42:'LUNGLESS SALAMANDER.',43:'FOUR TOES EACH FOOT.',44:'SLENDER OAK DWELLER.',45:'A LONG SLENDER TAIL.',46:'FOUR TOES EACH FOOT.',47:'LUNGLESS SALAMANDER.',48:'A LONG NARROW BODY.',49:'A SLENDER SALAMANDER',50:'A SMALL SLENDER FORM',51:'A DARK-BELLIED FORM.',52:'AN ISLAND SALAMANDER',53:'FOUR-TOED FEET.',54:'LUNGLESS SALAMANDER.',55:'ROBUST SLENDER FORM.',56:'A LONG NARROW BODY.',57:'LARGE FEET FOR SIZE.',
58:'DARK BARS ON TAIL',59:'SMOOTH RUBBERY SKIN.',60:'RED WHITE BLACK.',61:'SWIMS WITH FLIPPERS.',62:'A LONG SLENDER SNAKE',63:'A SMALL FOREST SNAKE',64:'A POINTED TAIL TIP.',65:'A RATTLESNAKE.',66:'A RATTLESNAKE.',67:'A SPECKLED DARK FORM',68:'A RATTLESNAKE.',69:'A RATTLESNAKE.',70:'A RATTLESNAKE.',71:'DARK NECK COLLARS.',72:'DARK NECK COLLARS.',73:'A LEATHERY SHELL.',74:'A PALE NECK RING.',75:'A BROAD-HEADED ADULT',76:'A MARBLED ADULT FORM',77:'LONG BODY, TINY LEGS',78:'LONG BODY, TINY LEGS',79:'A NARROW TAIL BASE.',80:'A SPOTTED LIZARD.',81:'A BLUNT SNOUT.',82:'A LONGER SNOUT.',83:'STOUT WITH BEAD SKIN',84:'WEBBED FEET / HANDS.',85:'A BROAD FLAT HEAD.',86:'A SHORT TAPERED TAIL',87:'WEBBED FEET / HANDS.',88:'A SHORT TAPERED TAIL',89:'A SMALL DESERT SNAKE',90:'A SMALL COAST SNAKE.',91:'A LONG SLENDER SNAKE',92:'LONGITUDINAL STRIPES',93:'A LONG SLENDER SNAKE',94:'LONGITUDINAL STRIPES',95:'A ROCK LIZARD.',96:'HORNS FRAME ITS HEAD',97:'SMALL, SHORT HORNS.',98:'A BROAD FLAT TAIL.',99:'EXPANDED TOE TIPS.',100:'A BROAD NOSE SCALE.',101:'A BLOTCHED SNAKE.',102:'SMOOTH LIZARD SCALES',103:'SMOOTH LIZARD SCALES',104:'ROBUST WOODLAND FORM',105:'A BROAD DORSAL BAND.',106:'A LONG SLENDER TRUNK',107:'LUNGLESS SALAMANDER.',108:'A ROCKY-CREEK FROG.',109:'FOLDED LONG HINDLEGS',110:'YELLOW UNDER LEGS.',111:'DARK SPOTS ON BACK.',112:'RED UNDER ITS LEGS.',113:'YELLOW UNDER LEGS.',114:'A VERY THIN SNAKE.',115:'BANDS CROSS ITS BODY',116:'A SMALL SEEP DWELLER',117:'A LARGE NOSE SCALE.',118:'A HINDFOOT SPADE.',119:'A SMALL SPINY LIZARD',120:'A LARGE SPINY LIZARD',121:'A SPINY ROCK LIZARD.',122:'A SHOVEL-LIKE SNOUT.',123:'A SMALL GROUND SNAKE',124:'A HINDFOOT SPADE.',125:'A HINDFOOT SPADE.',126:'A DARK-HEADED SNAKE.',127:'A DARK-HEADED SNAKE.',128:'GRAINY LAND SKIN.',129:'A REDDISH UNDERSIDE.',130:'A ROBUST NEWT.',131:'A WATER-EDGE SNAKE.',132:'A STREAMSIDE SNAKE.',133:'STRIPED GARTERSNAKE.',134:'A LARGE GARTERSNAKE.',135:'TWO SIDE STRIPES.',136:'A CHECKERED FORM.',137:'A SMALL GARTERSNAKE.',138:'STRIPED GARTERSNAKE.',139:'A BROAD-HEADED SNAKE',140:'TOE FRINGES IN SAND.',141:'TOE FRINGES IN SAND.',142:'TOE FRINGES IN SAND.',143:'A LONG THIN TAIL.',144:'A SMALL BRUSH LIZARD',145:'A SMALL TREE LIZARD.',146:'A DARK SIDE PATCH.',147:'A CREVICE DWELLER.',148:'A CREVICE DWELLER.',149:'A COVER DWELLER.',150:'FOUR TOES EACH FOOT.',
}
# Every label is deliberately abbreviated, not silently clipped mid-word.
NAMES={
18:'SW POND TURTLE',19:'NW SALAMANDER',20:'LONG-TOED SALAM',21:'WESTERN TOAD',22:'ARROYO TOAD',23:'YOSEMITE TOAD',24:'G PLAINS TOAD',25:'BLACK TOAD',26:'CLOUDED SALAM',27:'BLACK SALAM',28:'SHASTA BLACK',29:'KLAMATH BLACK',30:'SANTA CRUZ BLACK',31:'WANDERING SALAM',32:'TEMBLOR LEGLESS',33:'S DIEGO LEGLESS',34:'GLOSSY SNAKE',35:'COAST TAIL FROG',36:'ORANGE WHIPTAIL',37:'TIGER WHIPTAIL',38:'GREENHORN SALAM',39:'CA SLENDER',40:'FAIRVIEW SLENDER',41:'INYO SALAMANDER',42:'HELL HOLLOW',43:'SAN GABRIEL',44:'GABILAN SLENDER',45:'GREGARIOUS SALAM',46:'SAN SIMEON SALAM',47:'SEQUOIA SLENDER',48:'SANTA LUCIA',49:'SOUTHERN SLENDER',50:'LESSER SLENDER',51:'BLACK-BELLY',52:'ISLANDS SLENDER',53:'KINGS RIVER',54:'RELICTUAL SALAM',55:'KERN PLATEAU',56:'KERN CANYON',57:'TEHACHAPI SALAM',58:'ZEBRA-TAIL LIZ',59:'RUBBER BOA',60:'MTN KINGSNAKE',61:'GREEN SEA TURTLE',62:'N AMERICAN RACER',63:'F SHARP-TAIL',64:'C SHARP-TAIL',65:'W DIAMONDBACK',66:'W RATTLESNAKE',67:'SW SPECKLED',68:'RED DIAMOND',69:'MOJAVE RATTLER',70:'PANAMINT RATTLER',71:'G BASIN COLLARED',72:'BAJA COLLARED',73:'LEATHERBACK',74:'RING-NECK SNAKE',75:'CA GIANT SALAM',76:'COAST GIANT',77:'N ALLIGATOR LIZ',78:'PANAMINT ALLIG',79:'ENSATINA',80:'BAJA LEOPARD',81:'BLUNT-NOSE LEOP',82:'LONG-NOSE LEOP',83:'GILA MONSTER',84:'LIMESTONE SALAM',85:'MT LYELL SALAM',86:'SAMWEL SHASTA',87:'SHASTA SALAM',88:'WINTU SHASTA',89:'DESERT NIGHTSNK',90:'COAST NIGHTSNAKE',91:'BAJA COACHWHIP',92:'STRIPED RACER',93:'DESERT COACHWHIP',94:'STRIPE WHIPSNAKE',95:'MEARNS ROCK LIZ',96:'BLAINVILLE HORN',97:'PYGMY HORNED',98:'FLAT-TAIL HORNED',99:'LEAF-TOED GECKO',100:'LEAF-NOSE SNAKE',101:'GOPHERSNAKE',102:'GILBERT SKINK',103:'WESTERN SKINK',104:'SCOTT BAR SALAM',105:'DUNNS SALAM',106:'DEL NORTE SALAM',107:'SISKIYOU SALAM',108:'CA TREEFROG',109:'N RED-LEG FROG',110:'FOOTHILL YL FROG',111:'CASCADES FROG',112:'CA RED-LEG FROG',113:'S MOUNTAIN YL',114:'W THREADSNAKE',115:'LONG-NOSE SNAKE',116:'S TORRENT SALAM',117:'PATCH-NOSE SNAKE',118:'COUCH SPADEFOOT',119:'SAGEBRUSH LIZARD',120:'DESERT SPINY',121:'GRANITE SPINY',122:'SHOVEL-NOSE SNK',123:'W GROUNDSNAKE',124:'W SPADEFOOT',125:'G BASIN SPADEFT',126:'SMITH BLACK-HEAD',127:'W BLACK-HEAD',128:'ROUGH-SKIN NEWT',129:'RED-BELLY NEWT',130:'SIERRA NEWT',131:'AQUATIC GARTER',132:'SIERRA GARTER',133:'LAND GARTER',134:'GIANT GARTER',135:'TWO-STRIP GARTER',136:'CHECKERED GARTER',137:'NW GARTER',138:'COMMON GARTER',139:'CA LYRESNAKE',140:'COACHELLA FRINGE',141:'COLORADO FRINGE',142:'MOJAVE FRINGE',143:'LONG-TAIL BRUSH',144:'BAJA BRUSH',145:'ORNATE TREE LIZ',146:'SIDE-BLOTCH LIZ',147:'SANDSTONE NIGHT',148:'GRANITE NIGHT',149:'DESERT NIGHT',150:'ARGUELLO SLENDER',
}
HABITAT_LINE={
 'freshwater_pond':'LOOK BY FRESH WATER.','freshwater_stream':'LOOK BY A STREAM.','forest_pond':'LOOK BY FOREST POOLS','montane_pond':'MOUNTAIN POOLS.','coastal_seasonal_pond':'COASTAL RAIN POOLS.','freshwater_edge':'LOOK AT WATER EDGES.','sandy_riparian_pool':'SANDY STREAM POOLS.','high_meadow_pool':'LOOK BY MEADOW POOLS','desert_rain_pool':'DESERT RAIN POOLS.','spring_marsh':'LOOK BY SPRING MARSH','forest_log':'LOOK BY FALLEN WOOD.','wet_forest_cover':'LOOK IN DAMP FOREST.','shaded_canyon_creek':'SHADY CANYON WATER.','damp_talus':'LOOK BY DAMP TALUS.','damp_rock_outcrop':'DAMP ROCKS ARE COVER','alkali_scrub':'LOOK IN ALKALI SCRUB','moist_sandy_soil':'LOOK BY DAMP SAND.','open_sand':'LOOK ON OPEN SAND.','cold_fast_stream':'COOL FLOWING WATER.','coastal_sage_scrub':'LOOK IN COAST SCRUB.','desert_shrub':'LOOK BY DESERT SCRUB','moist_conifer_litter':'DAMP CONIFER LITTER.','canyon_seep_rock_cover':'LOOK BY CANYON SEEPS','mountain_spring_seep':'MOUNTAIN SEEPS.','chaparral_moist_cover':'DAMP CHAPARRAL COVER','montane_moist_cover':'DAMP MOUNTAIN COVER.','oak_leaf_litter':'LOOK IN OAK LITTER.','coastal_moist_cover':'LOOK BY DAMP COAST.','moist_leaf_litter':'LOOK IN DAMP LITTER.','island_moist_cover':'DAMP ISLAND COVER.','forest_stream_seep':'FOREST STREAM SEEPS.','canyon_moist_cover':'LOOK IN DAMP CANYONS','forest_cover':'LOOK BY FOREST COVER','conifer_forest':'LOOK IN CONIFERS.','marine_bay':'WATCH FROM THE SHORE','open_grassland':'LOOK IN GRASSLAND.','humid_conifer_forest':'DAMP CONIFER COVER.','rock_log_cover':'LOOK BY ROCK OR LOG.','desert_riparian':'LOOK BY DESERT WATER','lava_outcrop':'LOOK BY LAVA ROCKS.','rock_outcrop':'LOOK BY ROCK FACES.','rocky_chaparral':'LOOK BY ROCKY SCRUB.','open_desert':'LOOK ON DESERT SOIL.','offshore_surface':'WATCH OFFSHORE WATER','forest_stream':'LOOK BY FOREST WATER','wet_talus':'LOOK BY WET TALUS.','open_chaparral':'LOOK IN OPEN SCRUB.','dry_grassland':'DRY GRASSLAND COVER.','rocky_desert_wash':'ROCKY DESERT WASHES.','damp_limestone_crevice':'DAMP LIMESTONE COVER','damp_granite_talus':'LOOK BY DAMP GRANITE','desert_rock_cover':'LOOK BY DESERT ROCKS','coastal_rock_cover':'LOOK BY COAST ROCKS.','coastal_dunes':'LOOK BY COAST DUNES.','chaparral':'LOOK IN CHAPARRAL.','sagebrush':'LOOK BY SAGEBRUSH.','open_oak_woodland':'LOOK IN OPEN OAKS.','juniper_woodland':'LOOK BY JUNIPERS.','rock_crevice':'LOOK BY ROCK CRACKS.','creosote_scrub':'LOOK BY CREOSOTE.','moist_rock_cover':'DAMP ROCKS ARE COVER','open_forest_edge':'LOOK AT FOREST EDGES','forest_streamside':'LOOK BESIDE A STREAM','rocky_creek':'LOOK BY ROCKY CREEKS','rocky_river_margin':'LOOK AT RIVER EDGES.','montane_meadow_pool':'HIGH MEADOW POOLS.','mountain_stream':'LOOK BY HIGH STREAMS','cold_headwater_seep':'COOL HEADWATER SEEPS','desert_wash':'LOOK IN A DRY WASH.','montane_rock_outcrop':'MOUNTAIN ROCK COVER.','joshua_woodland':'LOOK BY JOSHUA TREES','granite_outcrop':'LOOK BY GRANITE ROCK','vernal_pool':'LOOK BY RAIN POOLS.','sagebrush_seasonal_pool':'SAGE COUNTRY POOLS.','coastal_chaparral':'LOOK IN COAST SCRUB.','shaded_creek':'LOOK BY SHADY CREEKS','freshwater_marsh':'LOOK IN WATER MARSH.','wet_meadow':'LOOK BY DAMP MEADOWS','desert_canyon':'LOOK IN ROCK CANYONS','sand_dunes':'LOOK BY SAND DUNES.','sandstone_crevice':'LOOK BY SANDSTONE.','granite_crevice':'LOOK BY GRANITE GAPS','fallen_yucca':'LOOK BY FALLEN YUCCA','coastal_scrub_moist_cover':'DAMP COAST SCRUB.','grassland_burrow':'GRASSLAND BURROWS.','soil_burrow':'LOOK BY SOIL BURROWS','mountain_lake_edge':'LOOK BY HIGH LAKES.',
}
CAUDATA={'Ambystoma','Aneides','Batrachoseps','Dicamptodon','Ensatina','Hydromantes','Plethodon','Rhyacotriton','Taricha'}
SNAKES={'Arizona','Charina','Coluber','Contia','Crotalus','Diadophis','Hypsiglena','Masticophis','Phyllorhynchus','Pituophis','Rena','Rhinocheilus','Salvadora','Sonora','Tantilla','Thamnophis','Trimorphodon'}

def read(path):return json.loads((ROOT/path).read_text())
def art_registry():
    out={}
    for path in MANIFESTS:
        for m in read(path).values():
            sid=m['species_id']; assert sid not in out,('duplicate art metadata',sid)
            out[sid]=m
    canonical=ROOT/'art/out/species-art-manifest.json'
    if canonical.exists():
        for m in json.loads(canonical.read_text()).values():
            if 'species_id' in m and 'canonical_scientific_name' in m:
                if m['species_id'] in out:assert out[m['species_id']]['art_id']==m['art_id'],('canonical art mismatch',m)
                out[m['species_id']]=m
    return out

def profile(record):
    sid=record['species_id'];genus=record['canonical_scientific_name'].split()[0]
    phase='day';behavior='dash_settle';minimum=2;stress=4+sid%3
    if genus in CAUDATA:
        phase='day' if genus in {'Taricha','Rhyacotriton'} else 'night';behavior='slow_walk'
        if genus=='Hydromantes':behavior='night_peek'
        if genus=='Rhyacotriton':behavior='water_emerge'
    elif genus in {'Anaxyrus','Ascaphus','Pseudacris','Rana','Scaphiopus','Spea'}:
        phase='night' if genus in {'Ascaphus','Pseudacris','Scaphiopus','Spea'} or sid in {24,25} else 'day'
        behavior='water_emerge' if genus in {'Rana','Ascaphus'} else 'hop'
        if genus in {'Scaphiopus','Spea'}:behavior='hop' # no weather engine yet
        if sid==22:phase='night';behavior='slow_walk' # arroyo toads walk while foraging
    elif genus in SNAKES:
        phase='dusk';behavior='glide'
        if genus=='Crotalus':phase='night' if sid in {65,67,68,69,70} else 'dusk';behavior='protected';minimum=3;stress=6
        if genus in {'Contia','Rena','Tantilla'}:phase='night';behavior='freeze'
        if genus in {'Arizona','Hypsiglena','Phyllorhynchus','Rhinocheilus','Sonora','Trimorphodon'}:phase='night'
        if genus in {'Coluber','Masticophis','Salvadora','Thamnophis'}:phase='day'
    elif genus in {'Chelonia','Dermochelys','Actinemys'}:behavior='water_emerge';minimum=4 if genus in {'Chelonia','Dermochelys'} else 2;stress=6
    elif genus=='Anniella':phase='dusk';behavior='glide'
    elif genus=='Phrynosoma':behavior='freeze'
    elif genus in {'Coleonyx','Phyllodactylus'}:phase='night';behavior='night_peek'
    elif genus=='Xantusia':phase='day' if sid in {147,148} else 'dusk';behavior='night_peek'
    elif genus=='Heloderma':phase='dusk';behavior='protected';minimum=3;stress=6
    elif genus in {'Crotaphytus','Petrosaurus','Sceloporus'}:behavior='natural_display'
    elif genus in {'Urosaurus','Uta'}:behavior='freeze'
    # All new periods are distinct deterministic authored timing slots, never
    # asserted as measured species motion. Slow enough for visible focus/recovery.
    phase={25:'day',60:'day',129:'night',136:'dusk',149:'day'}.get(sid,phase)
    period=72+(sid*17)%151
    return phase,behavior,{'period':period,'minimum_distance':minimum,'stress_threshold':stress}

def care_line(sid,genus,habitat):
    if genus in {'Crotalus','Heloderma'}:return 'KEEP A SAFE DISTANCE'
    if genus in {'Chelonia','Dermochelys'}:return 'KEEP WATCH FROM LAND'
    if 'burrow' in habitat:return 'LEAVE BURROWS ALONE.'
    if genus in {'Rana','Ascaphus','Rhyacotriton','Actinemys'}:return 'KEEP THE WATER CLEAN'
    if genus in CAUDATA:return ['KEEP DAMP COVER SAFE','LOOK WITHOUT TOUCH.','LEAVE LITTER ALONE.','DO NOT MOVE ITS HOME'][sid%4]
    if genus in {'Anniella','Rena','Tantilla','Scaphiopus','Spea'}:return 'LEAVE SOIL IN PLACE.'
    return ['WATCH WITHOUT TOUCH.','LET IT SETTLE.','KEEP ITS COVER SAFE.','NO HANDLING NEEDED.'][sid%4]

def build():
    runtime_old=read('data/species.json');old_ecology=read('data/species_ecology.json');roster=read('data/production_roster.json');policy=read('data/roster_policy.json');art=art_registry()
    assert len(roster['records'])==151
    assert [r['species_id'] for r in roster['records']]==list(range(151))
    assert sum(r['hidden'] for r in roster['records'])==1
    foundation=copy.deepcopy(runtime_old[:18]);foundation[3]['behavior_params']={'period':90,'minimum_distance':3,'stress_threshold':6};foundation_ecology={r['species_id']:r for r in old_ecology['records'] if r['species_id']<18}
    assert [s['id'] for s in foundation]==list(range(18))
    assert len(foundation_ecology)==18
    runtime=foundation;records=[];art_matches=[]
    allowed_record={'species_id','guide_number','canonical_scientific_name','group','native_in_california','status','hidden','region_permissions','release_review_status'}
    for r in roster['records']:
        sid=r['species_id'];record={k:copy.deepcopy(v) for k,v in r.items() if k in allowed_record}
        # Preserve stronger foundation provenance while retaining the frozen
        # roster's full permission list and all finer subarea restrictions.
        if sid<18:
            old=foundation_ecology[sid];record['status']=old['status'];record['release_review_status']=old['release_review_status']
            for p in record['region_permissions']:
                earlier=next((q for q in old['region_permissions'] if q['region_id']==p['region_id']),None)
                if earlier:
                    p['evidence_urls']=list(dict.fromkeys(earlier['evidence_urls']+p['evidence_urls']))
                    if earlier.get('evidence_notes'):
                        retained=earlier['evidence_notes'];frozen=p.get('evidence_notes','')
                        p['evidence_notes']=retained if not frozen or frozen in retained else retained+' '+frozen
        for p in record['region_permissions']:
            p['game_time_note']='Authored game availability and frame timing, not exclusive or measured natural activity; final behavior/text/anatomy review pending.'
        records.append(record)
        if sid<18:
            assert foundation[sid]['scientific_name']==r['canonical_scientific_name']
            if sid in art:assert art[sid]['art_id']==foundation[sid]['art'] and art[sid]['canonical_scientific_name']==r['canonical_scientific_name']
            continue
        m=art[sid];assert m['canonical_scientific_name']==r['canonical_scientific_name'],(sid,m)
        permission=r['region_permissions'][0];habitat=permission['habitat_ids'][0]
        phase,behavior,params=profile(r);genus=r['canonical_scientific_name'].split()[0]
        facts=[FACT0[sid],'SEASONAL POOLS.' if sid==20 else 'WOODLAND ROCK COVER' if sid==60 else HABITAT_LINE[habitat],care_line(sid,genus,habitat)]
        trait_sources=m.get('anatomy_evidence_urls') or m.get('anatomy_sources') or m.get('anatomy_reference_urls') or []
        source=trait_sources[0] if trait_sources else permission['evidence_urls'][0]
        source={26:'https://www.nps.gov/articles/000/clouded-salamander.htm',61:'https://www.fisheries.noaa.gov/species/green-turtle',141:'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=2675'}.get(sid,source)
        # All factual trait lines remain authored source-informed text pending
        # independent anatomy/text review; no release-ready status is asserted.
        runtime.append({'id':sid,'name':NAMES[sid],'scientific_name':r['canonical_scientific_name'],'art':m['art_id'],'region':permission['region_id'],'time':phase,'spot':habitat,'behavior':behavior,'behavior_params':params,'facts':facts,'source':source})
        art_matches.append({'species_id':sid,'art_id':m['art_id'],'name':r['canonical_scientific_name'],'source_art_status':m.get('status','art_pending_review')})
    registry={'schema_version':1,'scope':'151 frozen source-reviewed native identities in runtime tables; source art and text pending independent anatomy/ecology/native/release review; encounter/campaign availability separately tested.','records':records}
    validate_registry(policy,registry);validate_runtime_rows(policy,registry,runtime)
    assert all(runtime[i]==runtime_old[i] for i in range(18) if i!=3),'foundation runtime row changed outside reviewed sidewinder care correction'
    assert len({s['name'] for s in runtime})==151,'short display name collision'
    assert len({s['art'] for s in runtime})==151,'art reuse across taxon IDs'
    assert all(s['time'] in {'day','dusk','night'} for s in runtime)
    assert all(s['name'].isascii() for s in runtime)
    assert all(s['source'].startswith('https://') for s in runtime)
    for s in runtime[18:]:
        p=next(p for p in registry['records'][s['id']]['region_permissions'] if p['region_id']==s['region'])
        assert s['spot'] in p['habitat_ids']
    return runtime,registry,{'count':151,'regular':150,'hidden':1,'foundation18_preserved':True,'art_matches':art_matches,'behavior_families':sorted({s['behavior'] for s in runtime}),'new_authored_periods_unique':len({s['behavior_params']['period'] for s in runtime[18:]})==133,'source_roster_sha256':hashlib.sha256((ROOT/'data/production_roster.json').read_bytes()).hexdigest()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true',help='Validate materialization without writing.');args=parser.parse_args()
    runtime,registry,report=build()
    if not args.check:
        (ROOT/'data/species.json').write_text(json.dumps(runtime,indent=2)+'\n');(ROOT/'data/species_ecology.json').write_text(json.dumps(registry,indent=2)+'\n')
    policy=read('data/roster_policy.json')
    try:
        placed=validate_encounters(policy,registry,read('data/foundation_encounters.json'))
        missing=sorted(set(range(151))-placed)
        report['encounter_validation']='existing placements passed';report['currently_placed']=len(placed);report['missing_encounter_species_ids']=missing
    except EcologyError as e:report['encounter_validation']=str(e)
    print(json.dumps({k:v for k,v in report.items() if k!='art_matches'},indent=2))
if __name__=='__main__':main()
