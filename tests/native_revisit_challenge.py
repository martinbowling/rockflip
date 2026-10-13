"""Independent current challenge locality audit through actual controller input.
Records current behavior, never grants flags or assumes broader scope is approved.
"""
from pathlib import Path
import ast,argparse,json,hashlib,shutil,tempfile
parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);args=parser.parse_args()
HERE=Path(__file__).resolve().parent
prefix=[]
for node in ast.parse((HERE/'native_behavior_quality.py').read_text()).body:
 if isinstance(node,ast.With):break
 prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(HERE/'native_behavior_quality.py'),'exec'),globals())
sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha
OUT=ROOT/'output/qa/revisit-challenge';OUT.mkdir(parents=True,exist_ok=True)
def row(y):return bytes(pb.memory[0,0x9800+y*32:0x9800+y*32+20])
def caption(text):return bytes(ord(c)-32 for c in text.ljust(20))
with tempfile.TemporaryDirectory(prefix='rockflip-revisit-challenge-')as tmp:
 cart=Path(tmp)/'audit.gbc';shutil.copy2(ROM,cart);pb=PyBoy(str(cart),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);enter_hike()
 # First visit the D10 target challenge but collect no evidence.
 travel(137);open_camp();press('down');press('select');check('D10 challenge opens',screen()==26);press('right',100)
 check('actual challenge19 starts incomplete',pb.memory[symbol('rf_challenge')]==19 and row(3)==caption('A NATURAL MOMENT'))
 snapshot('before-local-photo');press('b',100);check('challenge returns fieldpack',screen()==25);press('b',100)
 # Natural three stars on the same species in D11, without D10 target311.
 site=next(s for s in sites if s['spot_id']==348);open_subject(site);aim_to(1)
 wait_for('actual calm D11 walking moment',lambda s:natural_window('slow_walk',s));shutter('D11-nightsnake-natural',3);return_trail(site)
 check('saved animal photograph originates D11 not D10',word(RF+offset(22)+22*2)==152 and best(22)==3)
 d10_photo_bits=(flags()[18]>>4)&15
 check('no D10 campaign exactphoto bit earned',d10_photo_bits==0)
 travel(137);open_camp();press('down');press('select');press('right',100)
 observed_complete=row(3)==caption('THREE-STAR PAGE DONE')
 check('actual menu still targets D10 challenge19',screen()==26 and pb.memory[symbol('rf_challenge')]==19)
 snapshot('after-foreign-district-photo');pb.stop();shutil.copy2(Path(str(cart)+'.ram'),OUT/'actual-D11-nightsnake-layout4.ram')
receipt={'result':'observed-scope-gap' if observed_complete else 'locality-enforced','rom_sha256':sha,'assertions':len(checks),'frames':frames,'challenge_index':19,'advertised_target':{'spot':311,'map':137,'district':'D10'},'actual_three_star_capture':{'spot':348,'map':152,'district':'D11','species':22},'D10_target_photo_evidence':d10_photo_bits,'marked_done_without_local_target':observed_complete,'memory_writes':False,'source_semantics':'Completion presently means species best>=3, independent of target site/map/phase. This test records a concrete design gap, not a save-corruption claim.','inputs':inputs,'checks':checks}
(OUT/'audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['inputs','checks']},indent=2))
