"""Current layout6 controller acceptance; exact hash required, no RAM writes."""
from pathlib import Path
import ast,argparse,json,hashlib,shutil,tempfile
ROOT=Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name=='tests' else Path(__file__).resolve().parents[2];HERE=ROOT/'tests'
parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);args=parser.parse_args()
prefix=[]
for node in ast.parse((HERE/'native_behavior_quality.py').read_text()).body:
 if isinstance(node,ast.With):break
 prefix.append(node)
old_file=__file__;__file__=str(HERE/'native_behavior_quality.py');exec(compile(ast.Module(body=prefix,type_ignores=[]),str(HERE/'native_behavior_quality.py'),'exec'),globals());__file__=old_file
sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha
assert re.search(r'DEF _rf_challenge_record ',noi),'Need adopted regional shutter challenge module'
OUT=ROOT/'output/qa/regional-challenge-native';OUT.mkdir(parents=True,exist_ok=True)
BYTES=[0,0,0,1,1,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5,5,5,5,6,6,6,6,6]
MASKS=[32,64,128,64,128,32,64,128,4,8,16,32,64,128,4,8,16,32,64,128,2,4,8,16,32,64,128,8,16,32,64,128]
def awards():return [bool(flags()[b]&m)for b,m in zip(BYTES,MASKS)]
def row(y):return bytes(pb.memory[0,0x9800+y*32:0x9800+y*32+20])
def caption(t):return bytes(ord(c)-32 for c in t.ljust(20))
def boot(cart):
 global pb
 pb=PyBoy(str(cart),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
def open19():
 travel(137);open_camp();press('down');press('select');press('right',100);check('actual D10 challenge19 UI',screen()==26 and pb.memory[symbol('rf_challenge')]==19)
def leave():press('b',100);press('b',100)
def natural_photo(spot,label):
 site=next(s for s in sites if s['spot_id']==spot);open_subject(site);aim_to(1);wait_for(label,lambda s:natural_window('slow_walk',s));shutter(label,3);return_trail(site)
with tempfile.TemporaryDirectory(prefix='rockflip-regional-challenge-')as work:
 cart=Path(work)/'fresh.gbc';shutil.copy2(ROM,cart);boot(cart);enter_hike()
 check('fresh regional mode marker set without awards',flags()[7]&32 and not any(awards()))
 open19();check('fresh actual target incomplete',row(3)==caption('A NATURAL MOMENT'));leave()
 natural_photo(348,'foreign D11 natural moment');check('foreign best3 does not award D10 task',best(22)==3 and not awards()[19])
 original_map=word(RF+offset(22)+44);check('original best photograph genuinely D11',original_map==152)
 open19();check('foreign district does not mark advertised local challenge done',row(3)==caption('A NATURAL MOMENT'));snapshot('foreign-rejected');leave()
 natural_photo(311,'local D10 natural moment');check('exact local shutter awards regional task',awards()[19])
 check('equal-star local shutter awards even though bestalbum stays D11',word(RF+offset(22)+44)==original_map)
 check('exactly one regional award exists',sum(awards())==1)
 open19();check('local challenge now visibly complete',row(3)==caption('THREE-STAR PAGE DONE'));snapshot('local-earned');leave();earned=flags();pb.stop();ram=Path(str(cart)+'.ram').read_bytes();(OUT/'local-earned.ram').write_bytes(ram)
 boot(cart);enter_hike();check('cold current local awards retained exactly',flags()==earned and awards()[19]and sum(awards())==1);pb.stop()
 # Actual input-earned old4 foreign-shot fixture must retain oldderived achievement.
 legacy=ROOT/'output/qa/revisit-challenge/actual-D11-nightsnake-layout4.ram';lc=Path(work)/'legacy.gbc';shutil.copy2(ROM,lc);shutil.copy2(legacy,Path(str(lc)+'.ram'));boot(lc)
 check('verified old4 awards migrated once without revocation',pb.memory[symbol('rf_store_loaded_layout')]==4 and awards()[19]and flags()[7]&32)
 check('legacy migration preserves actual best foreignphoto identity',best(22)==3 and word(RF+offset(22)+44)==152)
 enter_hike();open19();check('legacy earned achievement remains visibly awarded',row(3)==caption('THREE-STAR PAGE DONE'));leave();old_awards=awards();press('start',150);pb.stop();migrated=Path(str(lc)+'.ram').read_bytes();(OUT/'legacy-migrated.ram').write_bytes(migrated)
 boot(lc);enter_hike();check('migrated old award coldpersists with currentlayout6',pb.memory[symbol('rf_store_loaded_layout')]==6 and awards()==old_awards);pb.stop()
 # Actual prior layout4 native reader must fail closed on this newer semanticlayout.
 import importlib.util
 spec=importlib.util.spec_from_file_location('snapshot_fixture',HERE/'native_snapshot_migration.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 oldrom=ROOT/'output/challenge-locality/old-reader/RockFlip-Statewide-63201c.gbc';h=helper.harness(oldrom,Path(str(oldrom)+'.debug/symbols.noi'));h['OUT']=OUT;oldcart=Path(work)/'old-reader.gbc';shutil.copy2(oldrom,oldcart);helper.open_rom(h,oldcart,migrated);h['check']('actual layout4 reader locks future5',h['pb'].memory[h['symbol']('rf_store_locked')]==1);h['enter_hike']();h['press']('start',150);h['pb'].stop();check('old native reader cannot overwrite oldornew records',Path(str(oldcart)+'.ram').read_bytes()==migrated)
receipt={'result':'pass','rom_sha256':sha,'assertions':len(checks),'frames':frames,'memory_writes':False,'wrong_district_rejected':True,'local_equal_best_event_awards':True,'cold_awards_exact':True,'actual_old4_awards_preserved_once':True,'actual_old4_reader_locks_current6':True,'legacy_fixture_sha256':hashlib.sha256(legacy.read_bytes()).hexdigest(),'inputs':inputs,'checks':checks}
(OUT/'playtest.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['inputs','checks']},indent=2))
