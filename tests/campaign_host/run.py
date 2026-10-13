import ctypes,json,hashlib,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];data=json.loads((root/'data/campaign.json').read_text());
source=root/'native/plugins/rockflip/engine/src/rockflip_campaign.c'; header=root/'native/plugins/rockflip/engine/include/rockflip_campaign.h';
work=tempfile.TemporaryDirectory(prefix='rockflip-campaign-host-'); so=Path(work.name)/'campaign.so';
adapter=Path(work.name)/'adapter.c';adapter.write_text('#include \"rockflip_runtime.h\"\nstruct RFState rf;RFMap rf_map;void host_fresh_mode(void){rf.quest_flags[8]=2;}\n')
variant=source.parent/'rockflip_campaign_variant.c'
subprocess.run(['cc','-shared','-fPIC','-std=c99','-Wno-unknown-pragmas','-I'+str(Path(__file__).parent),'-I'+str(header.parent),str(source),str(variant),str(adapter),'-o',str(so)],check=True);
lib=ctypes.CDLL(str(so));B=ctypes.c_uint8;W=ctypes.c_uint16;P=ctypes.POINTER(B);A=B*32;checks=0
specs={'rf_campaign_photo':([P,B,W,B,B,B,B],B),'rf_campaign_care':([P,W],None),'rf_campaign_stage':([P,B],B),'rf_campaign_answer':([P,B,B],B),'rf_campaign_turn_in':([P,B],B),'rf_campaign_chapters':([P],B),'rf_campaign_finale_stage':([P],B),'rf_campaign_finale_answer':([P,B],B),'rf_campaign_finale_complete':([P],B),'rf_campaign_ack_credits':([P],None),'rf_campaign_hidden_clue':([P],None),'rf_campaign_hidden_answer':([P,B],B),'rf_campaign_unlock_hidden':([P,B],B),'rf_campaign_hidden_ready':([P],B),'rf_campaign_text':([B,B,B,B,ctypes.c_char_p],None)}
for name,(arg,ret) in specs.items():f=getattr(lib,name);f.argtypes=arg;f.restype=ret
def check(v,label):
 global checks
 assert v,label;checks+=1
lib.host_fresh_mode();f=A();f[0]=31;f[8]=2
for q in data['finale_questions']:check(lib.rf_campaign_finale_answer(f,q['correct_choice'])==0,'early finale')
for district in data['districts']:
 d=district['native_district'];before=list(f)
 for st in district['stages']:
  s=st['stage_index'];check(lib.rf_campaign_stage(f,d)==s,'stage initial')
  check(lib.rf_campaign_turn_in(f,d)==0,'no evidence')
  check(lib.rf_campaign_answer(f,d,(st['correct_choice']+1)%3)==0,'wrong note')
  for i in st['photo_target_indexes']:
   t=district['photo_targets'][i];args=[t['species_id'],t['spot_id'],t['phase'],2,4,45]
   for offset,value in [(0,(t['species_id']+1)%151),(1,t['spot_id']+1000),(2,(t['phase']+1)%3),(3,1),(4,t['minimum_distance']-1),(5,44)]:
    bad=args.copy();bad[offset]=value;earlier=list(f);check(lib.rf_campaign_photo(f,*bad)==0,'invalid photo pending');check(list(f)==earlier,'invalid photo no state mutation')
   if t['requires_restore_after_photo']:
    earlier=list(f);lib.rf_campaign_care(f,t['spot_id']);check(list(f)==earlier,'care before photo refused')
   pending=lib.rf_campaign_photo(f,*args);check(pending==t['requires_restore_after_photo'],'correct care pending')
  check(lib.rf_campaign_answer(f,d,st['correct_choice'])==1,'correct note')
  if st['requires_matching_care']:
   check(lib.rf_campaign_turn_in(f,d)==0,'care missing blocks')
   target=district['photo_targets'][3];earlier=list(f);lib.rf_campaign_care(f,target['spot_id']+1000);check(list(f)==earlier,'wrong care spot')
   lib.rf_campaign_care(f,target['spot_id'])
  check(lib.rf_campaign_turn_in(f,d)==1,'stage completion');check(lib.rf_campaign_stage(f,d)==s+1,'stage increments once')
  check(lib.rf_campaign_turn_in(f,d)==0,'no unearned repeat reward')
  for other in range(16):
   if other!=d:check(lib.rf_campaign_stage(f,other)==((before[10+other//4]>>((other%4)*2))&3),'neighbor region bits preserved')
  for kind,limit in [(0,1),(1,2),(2,2),(3,3),(4,2),(5,2)]:
   for line in range(limit):
    b=ctypes.create_string_buffer(21);lib.rf_campaign_text(d,s,kind,line,b);check(0<len(b.value)<=20,'native text bounds')
 check(lib.rf_campaign_chapters(f)==(1<<((d+1)//4))-1,'chapter cluster progression')
check(lib.rf_campaign_finale_complete(f)==0,'captions still required')
for q in data['finale_questions']:
 check(lib.rf_campaign_finale_stage(f)==data['finale_questions'].index(q),'ordered finale')
 check(lib.rf_campaign_finale_answer(f,(q['correct_choice']+1)%3)==0,'wrong finale')
 check(lib.rf_campaign_finale_answer(f,q['correct_choice'])==1,'correct finale')
check(lib.rf_campaign_finale_complete(f)==1,'full ending complete')
check(lib.rf_campaign_unlock_hidden(f,150)==0,'secret clue still needed')
lib.rf_campaign_hidden_clue(f);check(lib.rf_campaign_hidden_answer(f,1)==0,'wrong hidden clue');check(lib.rf_campaign_hidden_answer(f,0)==1,'hidden clue')
check(lib.rf_campaign_unlock_hidden(f,149)==0,'150 regular required');check(lib.rf_campaign_unlock_hidden(f,150)==1,'hidden unlocked');check(lib.rf_campaign_hidden_ready(f)==1,'hidden ready')
check(list(f)[:10]==[31]+[0]*7+[2,0],'opening journal flag bytes preserved')
# Mojave full district cannot bypass its separate five-stage opening journal.
g=A();g[8]=2
for t in data['districts'][0]['photo_targets']:lib.rf_campaign_photo(g,t['species_id'],t['spot_id'],t['phase'],2,4,45)
lib.rf_campaign_care(g,data['districts'][0]['photo_targets'][3]['spot_id'])
for s in range(3):
 lib.rf_campaign_answer(g,0,data['districts'][0]['stages'][s]['correct_choice']);check(lib.rf_campaign_turn_in(g,0)==(1 if s<2 else 0),'Mojave opening gate')
g[0]=31;check(lib.rf_campaign_turn_in(g,0)==1,'Mojave opening completes full district')
report={'evidence_layer':'host_compiled_generated_module_semantics_only_not_native_player_input','passed_checks':checks,'districts':16,'stages':48,'predicates':64,'finale_questions':4,'hidden_species_optional_for_ending':True,'reviewed_on_utc':datetime.now(timezone.utc).isoformat(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'variant_sha256':hashlib.sha256(variant.read_bytes()).hexdigest(),'header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'campaign_data_sha256':hashlib.sha256((root/'data/campaign.json').read_bytes()).hexdigest(),'adaptation':'Native generated C compiled unchanged except BANKED erased and UBYTE/UWORD defined by fixed-width host shim; bank pragma ignored. No engine or player-input proof.'}
(root/'output/qa').mkdir(parents=True,exist_ok=True);(root/'output/qa/campaign-host.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
