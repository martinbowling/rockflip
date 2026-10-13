"""Author and compile the exact-site, bounded16-district campaign to banked C.

Only campaign data/header/module/report are written. World, species, saves and
state UI are parent-owned. Real locality data never enters this module.
"""
from pathlib import Path
import json,argparse,hashlib
ROOT=Path(__file__).resolve().parents[2]
ENGINE=ROOT/'native/plugins/rockflip/engine'
# Four exact source-supported sites per region, checked against current tables.
SITES=[[2,1,3,0],[84,70,76,68],[94,96,104,99],[10,11,136,147],[18,175,160,162],[14,15,189,196],[221,219,223,225],[12,13,247,260],[19,20,300,279],[311,334,319,312],[350,356,358,352],[16,382,378,381],[410,413,424,419],[457,455,459,461],[17,479,493,505],[512,508,510,516]]
TITLES=['THE LIVING DESERT','SHADE AND LOW WATER','BASIN REFUGES','THE OAK CONNECTION','HIGH WATER HOMES','TWO VALLEY WATERS','THE VALLEY MOSAIC','CREEK TO ROCK','THE FOG FOLDER','A COAST OF REFUGES','TWO MOUNTAIN PATHS','ISLAND DIFFERENCES','THE FOREST LAYERS','THREE SMALL POCKETS','VOLCANIC NEIGHBORS','THE PLATEAU MOSAIC']
RANGERS=['NELL','SOL','IVO','TESS','MIRA','JUNE','ADA','FINN','BEA','RUI','LEO','UMA','KIT','OREN','WREN','PAX']
# Each stage has title, two clue lines, two question lines, correct and two
# incorrect captions, two conclusion lines. Options rotate deterministically.
STORIES=[
 [
 ('A HOME BELOW',['DAY: TORTOISE BURROW','KEEP THREE OR FOUR.'],['WHAT DOES A BURROW','OFFER IN THE HEAT?'],'COOL SHELTER','A PLACE TO DIG','A CAMERA STAND',['SHELTER IS EVIDENCE.','NOW COMPARE HOMES.']),
 ('SAND AND CREVICE',['DAY: SAND LIZARD.','DAY: CHUCKWALLA.'],['MATCH THE TWO','DESERT HOMES.'],'SAND / ROCK CRACK','BOTH IN A POND','BOTH IN TREE BARK',['TWO KINDS OF COVER.','NEITHER NEEDS TOUCH.']),
 ('LEAVE IT WHOLE',['DUSK: KINGSNAKE.','PHOTO. REPLACE ROCK.'],['WHAT FINISHES THIS','ROCK OBSERVATION?'],'REPLACE THE ROCK','TAKE ROCK TO CAMP','LEAVE ITS HOME OPEN',['A LIVING DESERT.','YOUR FOLDER IS READY'])
 ],
 [
 ('A LOW DESERT POOL',['NIGHT: SPADEFOOT.','LOOK BY A RAIN POOL.'],['WHICH CLUE FITS','THIS LOW-DESERT HOME'],'A TEMPORARY POOL','A SALTWATER REEF','A SNOWY SUMMIT',['RAIN CAN MAKE A HOME','WITHOUT MAKING A SEA']),
 ('SAND IS NOT EMPTY',['DAY: HORNED LIZARD.','DAY: DUNE FRINGE-TOE'],['WHAT LINKS THESE','TWO DESERT PHOTOS?'],'SANDY GROUND','BOTH ARE IN TREES','BOTH NEED DEEP WATER',['SAND HAS NEIGHBORS.','KEEP SOIL IN PLACE.']),
 ('ROCK ABOVE THE WASH',['DAY: COLLARED LIZARD','WATCH THE ROCK EDGE.'],['HOW DOES THE LAST','PHOTO ADD TO THE SET'],'A ROCKY REFUGE','ALL HOMES ARE SAND','ONE HOME FITS ALL',['POOL, SAND AND ROCK.','THE LOW DESERT LIVES'])
 ],
 [
 ('A SPRING IN A BASIN',['DAY: BLACK TOAD.','LOOK BY SPRING MARSH'],['WHY NOTE THE WATER','BESIDE THIS TOAD?'],'IT SHOWS ITS REFUGE','ALL BASINS ARE WET','TO MARK A DIG SITE',['A SMALL WET REFUGE.','NOW LOOK UP-SLOPE.']),
 ('SEEP AND TALUS',['NIGHT: INYO SALAM.','DAY: PANAMINT ALLIG.'],['MATCH THESE TWO','MOUNTAIN REFUGES.'],'SEEP / WET TALUS','OCEAN / PALM TOP','DRY DUNE / OCEAN',['WET POCKETS DIFFER.','KEEP THEM INTACT.']),
 ('SAGE COUNTRY WATER',['NIGHT: SPADEFOOT.','LOOK BY SAGE POOLS.'],['WHAT SHOULD STAY','WHEN YOU LEAVE?'],'SOIL AND COVER','A NEW DRAINAGE DITCH','THE ANIMAL AT CAMP',['BASIN, SEEP AND POOL','REFUGES LINK THE SET'])
 ],
 [
 ('DAY ON A ROCK',['DAY: FENCE LIZARD.','WATCH ITS ROCK PERCH'],['WHICH CAPTION FITS','THIS FIRST PHOTO?'],'A DAYLIGHT ROCK HOME','A DEEP SEA HOME','A PHOTO IN MIDNIGHT',['A SUNNY OPENING.','OAKS ADD A NEW PAGE.']),
 ('OAK AND CANYON',['NIGHT: OAK SALAM.','NIGHT: CANYON SALAM.'],['WHAT LINKS THESE','TWO QUIET HOMES?'],'DAMP SHELTER','ONE EMPTY HABITAT','ONLY SUNNY SAND',['COVER CONNECTS HOMES','LEAVE WOOD IN PLACE.']),
 ('THE FOREST MARGIN',['NIGHT: ENSATINA.','LOOK BY DAMP FOREST.'],['HOW SHOULD YOU','FINISH THIS WALK?'],'LEAVE COVER SAFE','PEEL OFF TREE BARK','CLEAR LEAF LITTER',['OAK TO CANYON COVER.','A LIVING CORRIDOR.'])
 ],
 [
 ('A HIGH LAKE EDGE',['DAY: SIERRA YL FROG','WATCH FROM LAKE EDGE'],['WHICH CAPTION FITS','YOUR FIRST PHOTO?'],'MOUNTAIN LAKE EDGE','A LOW DESERT DUNE','A SALTY TIDE POOL',['HIGH WATER IS HOME.','NOW COMPARE REFUGES.']),
 ('MEADOW AND GRANITE',['DAY: YOSEMITE TOAD.','NIGHT: LYELL SALAM.'],['MATCH THE TWO','HIGH-COUNTRY HOMES.'],'POOL / DAMP GRANITE','BOTH IN OPEN SEA','BOTH IN DRY SAND',['WATER AND DAMP ROCK.','NOT ONE EMPTY SUMMIT']),
 ('A MOUNTAIN POND',['NIGHT: LONG-TOED.','LOOK BY A HIGH POND.'],['WHAT KEEPS THIS','OBSERVATION CAREFUL?'],'KEEP WATER CLEAN','WALK THROUGH WATER','TAKE THE ANIMAL HOME',['LAKE, MEADOW, POND.','HIGH SET COMPLETE.'])
 ],
 [
 ('A GRASSLAND HOME',['NIGHT: TIGER SALAM.','LEAVE BURROWS ALONE.'],['WHAT IS THIS','FIRST SHELTER CLUE?'],'A GRASSLAND BURROW','A HOLE YOU MUST DIG','A SEA TURTLE NEST',['SHELTER ABOVE WATER.','COMPARE WET HOMES.']),
 ('POND AND MARSH',['DAY: POND TURTLE.','DAY: GIANT GARTER.'],['MATCH THE TWO','FRESHWATER PHOTOS.'],'POND / MARSH','BOTH IN DESERT DUNES','BOTH ON DRY SUMMITS',['TWO KINDS OF WATER.','KEEP THE BANKS SAFE.']),
 ('THE OTHER SALAM PAGE',['NIGHT: TIGER SALAM.','LOOK BY A RAIN POOL.'],['IS A BURROW PHOTO','ITS WHOLE LIFE STORY'],'ALSO NOTE THE POOL','THE POOL IS USELESS','DIG UP EVERY BURROW',['BURROW AND RAIN POOL','ONE ANIMAL: 2 HOMES'])
 ],
 [
 ('GRASSLAND DETAILS',['DAY: BLUNT-NOSE.','LOOK IN DRY GRASS.'],['WHICH CLUE FITS','THIS VALLEY LIZARD?'],'DRY GRASSLAND','A ROCKY OCEAN REEF','A COOL FOREST POND',['DRY GROUND HAS LIFE.','LOOK FOR OTHER HOMES']),
 ('SCRUB AND WATER',['DUSK: LEGLESS LIZARD','DAY: GIANT GARTER.'],['MATCH THE TWO','VALLEY NEIGHBORS.'],'SCRUB / MARSH','BOTH IN TREE CANOPY','BOTH IN DEEP SEA',['A VALLEY IS A MOSAIC','NOT JUST ONE FIELD.']),
 ('AFTER THE DRY PAGE',['NIGHT: SPADEFOOT.','LOOK BY A RAIN POOL.'],['WHAT SHOULD YOU','LEAVE IN PLACE?'],'SOIL AND BURROWS','EVERY ANIMAL AT CAMP','AN OPEN DRAIN TRENCH',['DRY AND WET REFUGES.','THE VALLEY SET IS IN'])
 ],
 [
 ('A SHADED CREEK',['DAY: CALIFORNIA NEWT','WATCH BY SHADY WATER'],['WHICH CAPTION FITS','THE NEWT PHOTO?'],'A SHADED CREEK','A HIGH DESERT DUNE','A SALTWATER BAY',['SHADY WATER HAS LIFE','ROCKS ADD A NEW CLUE']),
 ('STRIPE AND DARK FORM',['NIGHT: CHORUS FROG.','NIGHT: BLACK SALAM.'],['WHICH PAIR OF HOMES','FITS YOUR TWO PHOTOS'],'WATER / DAMP ROCK','BOTH IN DRY DUNES','BOTH IN OPEN OCEAN',['SMALL PHOTOS NEED','HABITAT NOTES TOO.']),
 ('THE WATER CONNECTION',['DAY: AQUATIC GARTER','LOOK BY ROCKY CREEK.'],['WHAT IS THE CAREFUL','WAY TO WATCH HERE?'],'KEEP WATER CLEAN','CHASE IT DOWNSTREAM','PUT IT IN A BUCKET',['CREEK, EDGE AND ROCK','YOUR FOLDER CONNECTS'])
 ],
 [
 ('A FOGGY CREEK',['DAY: CALIFORNIA NEWT','LOOK BY SHADED WATER'],['WHAT CLUE BELONGS','WITH THE COAST PAGE?'],'SHADY FRESH WATER','A DESERT RAIN DUNE','AN OFFSHORE REEF',['FOG IS NOT THE HOME.','LOOK AT COVER TOO.']),
 ('OAK AND POOL',['NIGHT: OAK SALAM.','DAY: RED-LEGGED FROG'],['MATCH THE TWO','CENTRAL COAST HOMES.'],'OAK COVER / POND','BOTH IN PALM TOPS','BOTH IN DRY SAND',['ONE COAST, TWO HOMES','KEEP THEIR NOTES.']),
 ('THE LITTER REFUGE',['NIGHT: GABILAN SALAM','LOOK IN OAK LITTER.'],['WHAT SHOULD REMAIN','AFTER THE PHOTO?'],'LEAVES AND COVER','A CLEARED WOOD FLOOR','THE ANIMAL IN A JAR',['CREEK, OAK AND POOL.','YOUR FOG SET LIVES.'])
 ],
 [
 ('A SANDY STREAM POOL',['NIGHT: ARROYO TOAD.','WATCH BY SANDY WATER'],['WHICH HOME FITS','THIS TOAD PHOTO?'],'SANDY STREAM POOL','A HIGH SNOWFIELD','A SALTWATER REEF',['SMALL WATER HOMES.','SCRUB ADDS CONTRAST.']),
 ('POND AND SAGE',['DAY: SW POND TURTLE','DAY: ORANGE WHIPTAIL'],['MATCH THE TWO','SOUTH COAST PHOTOS.'],'FRESH POND / SCRUB','BOTH IN A LAVA CAVE','BOTH IN OPEN OCEAN',['A COAST HAS INLAND','REFUGES WORTH NOTING']),
 ('KEEP THE COAST COVER',['NIGHT: NIGHTSNAKE.','PHOTO. REPLACE ROCK.'],['WHAT FINISHES THE','LOOSE-ROCK SEARCH?'],'PUT THE ROCK BACK','TAKE ALL ROCKS HOME','LEAVE THE COVER OPEN',['POOL, SCRUB AND ROCK','THE SOUTH COAST SET.'])
 ],
 [
 ('ONE MOUNTAIN REFUGE',['NIGHT: GABRIEL SALAM','DAMP MOUNTAIN COVER.'],['WHAT MAKES THIS','CLUE MORE USEFUL?'],'ITS OWN DAMP REFUGE','ALL MOUNTAINS MATCH','ANY DESERT ROCK WILL',['MOUNTAIN NAMES NEED','HABITAT NOTES TOO.']),
 ('STREAM AND GRANITE',['DAY: MOUNTAIN FROG.','DAY: GRANITE SPINY.'],['MATCH THESE TWO','MOUNTAIN HOMES.'],'STREAM / GRANITE','BOTH IN A SALT MARSH','BOTH UNDER DRY DUNES',['WATER AND ROCKS HAVE','DIFFERENT NEIGHBORS.']),
 ('THE CONIFER PAGE',['DUSK: RUBBER BOA.','LOOK BY CONIFERS.'],['HOW DO YOU FINISH','THE QUIET BOA WATCH?'],'LEAVE WOOD IN PLACE','PEEL BARK FOR PHOTOS','TAKE IT TO WATER',['TWO MOUNTAIN PATHS.','KEEP EACH HOME SAFE.'])
 ],
 [
 ('A NAME IS NO CLOCK',['DAY: ISLAND N LIZARD','WATCH ITS SCRUB HOME'],['WHEN DOES THIS','GAME PHOTO OCCUR?'],'IN DAYLIGHT','ONLY AT MIDNIGHT','ONLY IN SNOW',['A NIGHT LIZARD NAME','IS NOT A TIME RULE.']),
 ('ISLAND WOOD PAGES',['NIGHT: TWO SLENDERS','WATCH THEIR COVER.'],['CAN ONE ISLAND HOME','MATCH ALL ISLANDS?'],'KEEP ISLAND NOTES','ALL ISLANDS ARE SAME','MOVE ANIMALS BETWEEN',['VARIED ISLAND HOMES.','NEED DISTINCT NOTES.']),
 ('A CREVICE AT DAY',['DAY: ISLAND N LIZARD','WATCH THE ROCK GAP.'],['WHAT KEEPS THIS','PHOTO CAREFUL?'],'LEAVE THE GAP INTACT','PRY THE ROCKS APART','PULL IT OUT TO SEE',['SCRUB, COVER, GAPS.','THE ISLAND SET IS IN'])
 ],
 [
 ('A FOREST POND',['DAY: RED-LEGGED FROG','LOOK BY FOREST WATER'],['WHICH CAPTION FITS','THIS FOREST PHOTO?'],'A FRESHWATER POND','A COASTAL SALT POOL','AN OPEN DESERT DUNE',['FOREST WATER IS HOME','LOOK BELOW THE TREES']),
 ('WOOD AND FAST WATER',['NIGHT: CLOUDED SALAM','NIGHT: TAILED FROG.'],['MATCH THESE TWO','NORTHERN REFUGES.'],'LOG / COLD STREAM','BOTH IN OPEN OCEAN','BOTH IN SUNNY SAND',['FOREST LAYERS DIFFER','LEAVE WOOD IN PLACE.']),
 ('A LARGE STREAM ADULT',['NIGHT: GIANT SALAM.','WATCH FOREST WATER.'],['WHAT IS THE QUIET','WAY TO FINISH THIS?'],'LOOK WITHOUT TOUCH','MOVE IT TO THE POND','PEEL EVERY LOG OPEN',['POND, WOOD, STREAM.','FOREST SET COMPLETE'])
 ],
 [
 ('ONE KARST POCKET',['NIGHT: SHASTA SALAM.','DAMP LIMESTONE GAP.'],['WHICH NOTE HELPS','CRYPTIC SALAMANDER?'],'ITS NAME AND HABITAT','ONLY COLOR PROVES ID','NO NOTES ARE NEEDED',['SMALL ART HAS LIMITS','COMPARE THE POCKETS.']),
 ('THE OTHER POCKETS',['NIGHT: SAMWEL/WINTU','EACH HAS ITS OWN GAP'],['CAN ONE KARST POCKET','STAND FOR ALL THREE?'],'KEEP DISTINCT NOTES','ONE HOME FITS ALL','MOVE ANIMALS BETWEEN',['THREE NAMES, HOMES.','NO NEW COLOR SPECIES']),
 ('THE TALUS NEIGHBOR',['NIGHT: SCOTT BAR.','LOOK BY DAMP TALUS.'],['WHAT SHOULD STAY','AFTER YOUR WATCH?'],'COVER AND CREVICES','A PRIED ROCK FACE','THE ANIMAL AT CAMP',['KARST / TALUS HOMES.','KLAMATH SET COMPLETE'])
 ],
 [
 ('THE COVER UNDERFOOT',['DAY: ALLIGATOR LIZ.','LOOK BY ROCK OR LOG.'],['WHICH CLUE FITS','THIS VOLCANIC HOME?'],'ROCK AND LOG COVER','A SEA TURTLE NEST','A DRY CORAL REEF',['VOLCANIC LAND HAS','MORE THAN BARE ROCK.']),
 ('WETLAND AND FOREST',['DAY: CASCADES FROG.','DUSK: N RUBBER BOA.'],['MATCH THESE TWO','VOLCANIC REFUGES.'],'POOL / FOREST COVER','BOTH ON SNOW SUMMITS','BOTH IN OPEN OCEAN',['WET AND WOODED HOMES','KEEP THEIR NOTES.']),
 ('THE MOUNTAIN PERCH',['DAY: SAGEBRUSH LIZ.','LOOK BY HIGH ROCKS.'],['HOW DO YOU FINISH','A ROCK-PERCH PHOTO?'],'LEAVE THE PERCH SAFE','CHASE IT UP THE ROCK','PRY THE ROCK APART',['WOOD, POOL AND PERCH','VOLCANIC SET DONE'])
 ],
 [
 ('THE JUNIPER PAGE',['DAY: PYGMY HORNED.','LOOK BY JUNIPERS.'],['WHICH CAPTION FITS','THIS FIRST PHOTO?'],'A JUNIPER HOME','A SALTWATER BAY','A LOW PALM OASIS',['HIGH DESERT HOMES.','LAVA ADDS A NEW PAGE']),
 ('LAVA AND SAGE',['DUSK: W RATTLESNAKE','DAY: STRIPED WHIP.'],['WHAT MAKES THE','SNAKE PHOTOS CAREFUL'],'SPACE WITHOUT TOUCH','LIFT THEM FOR A SHOT','CHASE THE ANIMAL',['LAVA AND SAGE DIFFER','KEEP A WIDE VIEW.']),
 ('A POOL AMONG SAGE',['NIGHT: SPADEFOOT.','LOOK BY SAGE POOLS.'],['WHAT DOES THIS LAST','PHOTO ADD TO THE SET'],'A WATER REFUGE','ALL BASINS ARE LAKES','NO CHANGE OF HABITAT',['JUNIPER, LAVA, POOL.','PLATEAU SET COMPLETE'])
 ]
]
# Explicitly parent-owned UI consumes these stable kinds like the Mojave journal.
TEXT_KINDS={0:'title',1:'clue',2:'question',3:'options',4:'conclusion',5:'blocked'}

def ascii_lines(seq):
    for line in seq:
        if not line.isascii() or len(line)>20:raise ValueError((line,len(line)))
    return seq

def author():
    runtime=json.loads((ROOT/'data/species.json').read_text());world=json.loads((ROOT/'data/world.json').read_text());encounters=json.loads((ROOT/'data/foundation_encounters.json').read_text());ecology=json.loads((ROOT/'data/species_ecology.json').read_text());policy=json.loads((ROOT/'data/roster_policy.json').read_text())
    from validate_species import validate_encounters,validate_runtime_rows
    validate_runtime_rows(policy,ecology,runtime);validate_encounters(policy,ecology,encounters,world)
    sites={x['spot_id']:x for x in encounters['records']};maps={x['id']:x for x in world['maps']};districts=[]
    for d in range(16):
        did=f'D{d+1:02d}';targets=[];stages=[]
        for n,sid in enumerate(SITES[d]):
            s=sites[sid];assert s['region_id']==did;animal=runtime[s['species_id']];phase={'day':0,'dusk':1,'night':2}[animal['time']];assert s['phase_mask']&(1<<phase)
            targets.append({'target_index':n,'species_id':s['species_id'],'spot_id':sid,'map_id':s['room_id'],'district_id':did,'habitat_id':s['habitat_id'],'subarea_id':maps[s['room_id']].get('subarea_id'),'phase':phase,'phase_name':animal['time'],'minimum_stars':2,'minimum_focus':45,'minimum_distance':max(3 if s['species_id']==0 else 2,animal.get('behavior_params',{}).get('minimum_distance',2)),'interaction_type':s['interaction_type'],'requires_restore_after_photo':n==3 and s['interaction_type'] in {0,5},'map_name':maps[s['room_id']]['name']})
        for st,raw in enumerate(STORIES[d]):
            title,clue,question,right,wrong0,wrong1,conclusion=raw;correct=(d+st)%3;options=[wrong0,wrong1];options.insert(correct,right)
            lines=[title]+clue+question+options+conclusion;ascii_lines(lines)
            stages.append({'id':f'CP_{did}_{st+1}','stage_index':st,'title':title,'clue':clue,'question':question,'options':options,'correct_choice':correct,'conclusion':conclusion,'photo_target_indexes':[[0],[1,2],[3]][st],'photo_mask':[1,6,8][st],'requires_matching_care':st==2 and targets[3]['requires_restore_after_photo'],'care_goal':'Restore photographed loose stone at exact same site after valid photo.' if st==2 and targets[3]['requires_restore_after_photo'] else 'Answer the non-disturbance/habitat observation choice; no stone/log/water manipulation required.','requires_mojave_journal_complete':d==0 and st==2,'wrong_choice_recovery':'Immediate retry with no penalty or discarded evidence.','native_acceptance_steps':[{'action':'photograph_exact_site','target':targets[i]} for i in [[0],[1,2],[3]][st]]+[{'action':'restore_same_photographed_stone','spot_id':targets[3]['spot_id']}]*(1 if st==2 and targets[3]['requires_restore_after_photo'] else 0)+[{'action':'answer_caption','choice':correct},{'action':'turn_in','expected_district_stage':st+1}]})
        districts.append({'district_id':did,'native_district':d,'ranger_name':RANGERS[d],'title':TITLES[d],'source_scope':'Actual fictional authored sites validated against species_ecology default-deny permissions; no real locality.','photo_targets':targets,'stages':stages,'complete_when_stage':3})
    finale=[
      {'id':'EX01','question':['MATCH THE FIRST','CHAPTER FOLDER.'],'options':['SHELTER AND HEIGHT','FOG AND ISLANDS','ONLY OCEAN PHOTOS'],'correct_choice':0},
      {'id':'EX02','question':['MATCH THE SECOND','CHAPTER FOLDER.'],'options':['ONLY DRY DUNES','CHANGING WATER','ONLY NORTHERN TREES'],'correct_choice':1},
      {'id':'EX03','question':['MATCH THE THIRD','CHAPTER FOLDER.'],'options':['EVERY ISLAND IS SAME','ONLY HIGH DESERT','COASTS AND ISLANDS'],'correct_choice':2},
      {'id':'EX04','question':['MATCH THE FOURTH','CHAPTER FOLDER.'],'options':['NORTHERN CONNECTIONS','ONLY LOW DESERT','ONLY SOUTHERN COAST'],'correct_choice':0},
    ]
    for q in finale:ascii_lines(q['question']+q['options'])
    chapter_text=[['SHELTER AND HEIGHT','DESERT TO OAK HOMES.'],['CHANGING WATER','HIGH LAKES, VALLEYS'],['COASTS AND ISLANDS','DISTINCT COAST HOMES'],['NORTHERN CONNECTIONS','FOREST, LAVA, SAGE.']]
    for a in chapter_text:ascii_lines(a)
    hidden=next(s for s in encounters['records'] if s['species_id']==150);assert maps[hidden['room_id']].get('hidden')
    data={'schema_version':1,'implementation_status':'authored_and_compiled_native_module_pending_parent_UI_hooks_and_ROM_acceptance','scope':'16 districts x3 meaningful habitat/care stages; exact-site photos plus caption comparison, four chapter clusters, exhibit finale and optional hidden clue. Not human-reviewed playtime or release approval.','districts':districts,'chapter_clusters':[{'chapter_index':i,'district_indexes':list(range(i*4,i*4+4)),'completion_text':chapter_text[i]} for i in range(4)],'text_kinds':TEXT_KINDS,'finale_questions':finale,'ending_lines':['YOUR EXHIBIT IS OPEN','SIXTEEN STORIES.','MANY HOMES TO NOTICE','KEEP EXPLORING.'],'credits_lines':['ROCK FLIP','MARTIN AND ROAM','IDEA: BILBY','ORIGINAL FIELD ART','THANKS FOR PLAYING.'],'hidden_clue':{'species_id':150,'guide_number':151,'map_id':hidden['room_id'],'spot_id':hidden['spot_id'],'availability':'After actual exhibit completion, all150 regular photos and correct optional caption clue; no hidden species required for ending.','question':['A LAST COASTAL PAGE','HOW SHOULD WE LOOK?'],'options':['WATCH DAMP SCRUB','DIG UP ALL REFUGES','MOVE THEM TO CAMP'],'correct_choice':0,'clue_lines':['ONE LAST COAST PAGE','DAMP SCRUB, QUIETLY.','LOOK. DO NOT HANDLE.'],'real_locality_policy':'Fictional clue only. No real source coordinates, locality directions or observation links.'},'flags':{'region_states_bytes':[10,11,12,13],'photo_bits_bytes':list(range(14,22)),'note_bits_bytes':list(range(22,28)),'care_bits_bytes':[28,29],'finale_byte':30,'finale_correct_bits':[0,1,2,3],'credits_ack_bit':4,'hidden_byte':31,'hidden_clue_seen_bit':0,'hidden_correct_bit':1,'hidden_trail_unlocked_bit':7},'event_contract':'Every shutter event is evaluated, even if album best does not replace. rf_campaign_photo returns care-pending1 only for qualifying exact loose-stone target. Parent latches site bit7 and consumes it on genuine same-site restoration before rf_campaign_care. No care callback from permanent crevices, logs, soil, water or marine subjects.','safe_distance_note':'Tortoise campaign minimum3; all others >=actual species rule.','save_contract':'Flags32bytes remain parent-owned persistent RF02 quest state; no additional transient state required in module.','source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/world.json','data/foundation_encounters.json','data/species.json','data/species_ecology.json']}}
    for key in ['ending_lines','credits_lines']:ascii_lines(data[key])
    ascii_lines(data['hidden_clue']['question']+data['hidden_clue']['options']+data['hidden_clue']['clue_lines'])
    return data

HEADER='''#ifndef ROCKFLIP_CAMPAIGN_H
#define ROCKFLIP_CAMPAIGN_H
#include <gbdk/platform.h>
#define RF_CAMPAIGN_DISTRICTS 16
#define RF_CAMPAIGN_STAGES 3
/* All district indexes0..15, matching RFMap.district. Caller saves flags. */
UBYTE rf_campaign_photo(UBYTE *flags,UBYTE species,UWORD spot,UBYTE phase,UBYTE stars,UBYTE distance,UBYTE focus) BANKED;
void rf_campaign_care(UBYTE *flags,UWORD spot) BANKED;
UBYTE rf_campaign_stage(const UBYTE *flags,UBYTE district) BANKED;
UBYTE rf_campaign_answer(UBYTE *flags,UBYTE district,UBYTE choice) BANKED;
UBYTE rf_campaign_turn_in(UBYTE *flags,UBYTE district) BANKED;
UBYTE rf_campaign_chapters(const UBYTE *flags) BANKED;
void rf_campaign_text(UBYTE district,UBYTE stage,UBYTE kind,UBYTE line,char *out) BANKED;
void rf_campaign_ranger(UBYTE district,char *out) BANKED;
void rf_campaign_chapter_text(UBYTE chapter,UBYTE line,char *out) BANKED;
UBYTE rf_campaign_finale_stage(const UBYTE *flags) BANKED;
UBYTE rf_campaign_finale_answer(UBYTE *flags,UBYTE choice) BANKED;
UBYTE rf_campaign_finale_complete(const UBYTE *flags) BANKED;
void rf_campaign_finale_text(UBYTE question,UBYTE kind,UBYTE line,char *out) BANKED;
void rf_campaign_ack_credits(UBYTE *flags) BANKED;
void rf_campaign_hidden_clue(UBYTE *flags) BANKED;
UBYTE rf_campaign_hidden_answer(UBYTE *flags,UBYTE choice) BANKED;
UBYTE rf_campaign_unlock_hidden(UBYTE *flags,UBYTE regular_photo_count) BANKED;
UBYTE rf_campaign_hidden_ready(const UBYTE *flags) BANKED;
void rf_campaign_hidden_text(UBYTE kind,UBYTE line,char *out) BANKED;
#endif
'''

def carray(values):return json.dumps(values).replace('[','{').replace(']','}')
def compile_campaign(data):
    rows=[];texts=[];targets=[];care=[]
    for d in data['districts']:
        for t in d['photo_targets']:targets.append([t['spot_id'],t['species_id'],t['phase'],t['minimum_distance'],int(t['requires_restore_after_photo'])])
        care.append(int(d['photo_targets'][3]['requires_restore_after_photo']))
        rows.append([s['correct_choice'] for s in d['stages']])
        # Fixed10lines per stage: title, clue2, question2,options3,conclusion2,
        # plus no redundant fixed padding for the blocked feedback.
        texts.append([[s['title']]+s['clue']+s['question']+s['options']+s['conclusion'] for s in d['stages']])
    q=data['finale_questions'];hidden=data['hidden_clue']
    c='#pragma bank 255\n#include "rockflip_campaign.h"\n#include <string.h>\n'
    c+='typedef struct {UWORD spot;UBYTE species,phase,distance,care;} Target;\n'
    c+='static const Target targets[64]='+carray(targets)+';\n'
    c+='static const UBYTE choices[16][3]='+carray(rows)+';\n'
    c+='static const UBYTE needs_care[16]='+carray(care)+';\n'
    c+='static const char stage_text[16][3][10][21]='+carray(texts)+';\n'
    c+='static const char rangers[16][6]='+carray([d['ranger_name'] for d in data['districts']])+';\n'
    c+='static const char chapters[4][2][21]='+carray([a['completion_text'] for a in data['chapter_clusters']])+';\n'
    c+='static const char final_questions[4][5][21]='+carray([a['question']+a['options'] for a in q])+';\n'
    c+='static const UBYTE final_choices[4]='+carray([a['correct_choice'] for a in q])+';\n'
    c+='static const char endings[4][21]='+carray(data['ending_lines'])+';\n'
    c+='static const char credits[5][21]='+carray(data['credits_lines'])+';\n'
    c+='static const char secret[8][21]='+carray(hidden['clue_lines']+hidden['question']+hidden['options'])+';\n'
    c+='''
static UBYTE getbits(const UBYTE*f,UBYTE base,UBYTE bit,UBYTE width){UBYTE i,v=0;for(i=0;i<width;i++)if(f[base+((bit+i)>>3)]&(1<<((bit+i)&7)))v|=1<<i;return v;}
static void setbits(UBYTE*f,UBYTE base,UBYTE bit,UBYTE width,UBYTE v){UBYTE i,*p,m;for(i=0;i<width;i++){p=f+base+((bit+i)>>3);m=1<<((bit+i)&7);if(v&(1<<i))*p|=m;else *p&=~m;}}
static UBYTE stage(const UBYTE*f,UBYTE d){return getbits(f,10,d*2,2);}
UBYTE rf_campaign_stage(const UBYTE*f,UBYTE d) BANKED {return d<16?stage(f,d):3;}
UBYTE rf_campaign_photo(UBYTE*f,UBYTE species,UWORD spot,UBYTE phase,UBYTE stars,UBYTE distance,UBYTE focus) BANKED {UBYTE i,b,pending=0;const Target*t;if(stars<2||focus<45||distance>4||phase>2)return 0;for(i=0;i<64;i++){t=targets+i;if(t->species==species&&t->spot==spot&&t->phase==phase&&distance>=t->distance){b=getbits(f,14,(i>>2)*4,4)|(1<<(i&3));setbits(f,14,(i>>2)*4,4,b);if(t->care)pending=1;}}return pending;}
void rf_campaign_care(UBYTE*f,UWORD spot) BANKED {UBYTE d;for(d=0;d<16;d++)if(needs_care[d]&&targets[d*4+3].spot==spot&&(getbits(f,14,d*4,4)&8))setbits(f,28,d,1,1);}
UBYTE rf_campaign_answer(UBYTE*f,UBYTE d,UBYTE choice) BANKED {UBYTE s;if(d>=16)return 0;s=stage(f,d);if(s>=3||choice!=choices[d][s])return 0;setbits(f,22,d*3+s,1,1);return 1;}
UBYTE rf_campaign_turn_in(UBYTE*f,UBYTE d) BANKED {UBYTE s,p,required;if(d>=16)return 0;s=stage(f,d);if(s>=3)return 0;required=s==0?1:s==1?6:8;p=getbits(f,14,d*4,4);if((p&required)!=required||!getbits(f,22,d*3+s,1))return 0;if(s==2&&needs_care[d]&&!getbits(f,28,d,1))return 0;if(d==0&&s==2&&(f[0]&31)!=31)return 0;setbits(f,10,d*2,2,s+1);return 1;}
UBYTE rf_campaign_chapters(const UBYTE*f) BANKED {UBYTE c,d,ok,v=0;for(c=0;c<4;c++){ok=1;for(d=c*4;d<c*4+4;d++)if(stage(f,d)!=3)ok=0;if(ok)v|=1<<c;}return v;}
void rf_campaign_text(UBYTE d,UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED {UBYTE index=255;out[0]=0;if(d>=16||s>=3)return;if(kind==0&&line==0)index=0;else if(kind==1&&line<2)index=1+line;else if(kind==2&&line<2)index=3+line;else if(kind==3&&line<3)index=5+line;else if(kind==4&&line<2)index=8+line;else if(kind==5&&line<2){strcpy(out,line==0?"CHECK PHOTO AND NOTE":"KEEP ITS HOME SAFE.");return;}if(index!=255)strcpy(out,stage_text[d][s][index]);}
void rf_campaign_ranger(UBYTE d,char*out) BANKED {out[0]=0;if(d<16)strcpy(out,rangers[d]);}
void rf_campaign_chapter_text(UBYTE c,UBYTE line,char*out) BANKED {out[0]=0;if(c<4&&line<2)strcpy(out,chapters[c][line]);}
UBYTE rf_campaign_finale_stage(const UBYTE*f) BANKED {UBYTE q;for(q=0;q<4;q++)if(!(f[30]&(1<<q)))return q;return 4;}
UBYTE rf_campaign_finale_complete(const UBYTE*f) BANKED {return rf_campaign_chapters(f)==15&&(f[30]&15)==15;}
UBYTE rf_campaign_finale_answer(UBYTE*f,UBYTE choice) BANKED {UBYTE q;if(rf_campaign_chapters(f)!=15)return 0;q=rf_campaign_finale_stage(f);if(q>=4||choice!=final_choices[q])return 0;f[30]|=1<<q;return 1;}
void rf_campaign_finale_text(UBYTE q,UBYTE kind,UBYTE line,char*out) BANKED {out[0]=0;if(kind==0&&q<4&&line<2)strcpy(out,final_questions[q][line]);else if(kind==1&&q<4&&line<3)strcpy(out,final_questions[q][line+2]);else if(kind==2&&line<4)strcpy(out,endings[line]);else if(kind==3&&line<5)strcpy(out,credits[line]);}
void rf_campaign_ack_credits(UBYTE*f) BANKED {if(rf_campaign_finale_complete(f))f[30]|=16;}
void rf_campaign_hidden_clue(UBYTE*f) BANKED {if(rf_campaign_finale_complete(f))f[31]|=1;}
UBYTE rf_campaign_hidden_answer(UBYTE*f,UBYTE choice) BANKED {if(!rf_campaign_finale_complete(f)||!(f[31]&1)||choice!=0)return 0;f[31]|=2;return 1;}
UBYTE rf_campaign_unlock_hidden(UBYTE*f,UBYTE regular_count) BANKED {if(rf_campaign_finale_complete(f)&&(f[31]&2)&&regular_count>=150)f[31]|=128;return (f[31]&128)!=0;}
UBYTE rf_campaign_hidden_ready(const UBYTE*f) BANKED {return (f[31]&128)!=0;}
void rf_campaign_hidden_text(UBYTE kind,UBYTE line,char*out) BANKED {out[0]=0;if(kind==0&&line<3)strcpy(out,secret[line]);else if(kind==1&&line<2)strcpy(out,secret[3+line]);else if(kind==2&&line<3)strcpy(out,secret[5+line]);}
'''
    return c

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--emit-native',action='store_true');args=p.parse_args()
    import tempfile
    from campaign_route_compile import generate
    work=ROOT/'output/campaign-work';work.mkdir(parents=True,exist_ok=True)
    data=generate(work);c=(work/'rockflip_campaign_legacy_dispatch.c').read_text()
    if not args.check:
        (ROOT/'data/campaign.json').write_text(json.dumps(data,indent=2)+'\n')
        if args.emit_native:
            (ENGINE/'include/rockflip_campaign.h').write_text(HEADER);(ENGINE/'src/rockflip_campaign.c').write_text(c)
            (ENGINE/'include/rockflip_campaign_variant.h').write_text((work/'rockflip_campaign_variant.h').read_text())
            (ENGINE/'src/rockflip_campaign_variant.c').write_text((work/'rockflip_campaign_variant.c').read_text())
        else:
            staging=ROOT/'output/campaign-work';staging.mkdir(parents=True,exist_ok=True);(staging/'rockflip_campaign.h').write_text(HEADER);(staging/'rockflip_campaign.c').write_text(c)
    print('16districts/48stages/64exact photo predicates compiled; four chapter clusters, exhibit4questions, credits/postgame and optional hidden clue. UI/runtime acceptance pending.')
if __name__=='__main__':main()
