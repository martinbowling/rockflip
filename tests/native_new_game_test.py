"""After adoption only: genuine earned-save cancel/confirmed restart/cold/downgrade.
No RAM writes; future-format protection is an explicit file-format fault fixture.
"""
from pathlib import Path
import sys,argparse,ast
own_file=__file__;ROOT=Path(own_file).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from native_snapshot_migration import record,latest,harness,open_rom
parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);parser.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');parser.add_argument('--earned-save',type=Path,default=ROOT/'output/qa/controller-earned-151-c66c.ram');parser.add_argument('--old-rom',type=Path,default=ROOT/'output/build-candidates/RockFlip-Statewide-9471.gbc');args=parser.parse_args()
source=ROOT/'tests/production_playtest.py';prefix=[]
for node in ast.parse(source.read_text()).body:
 if isinstance(node,ast.With):break
 if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROM'for t in node.targets):node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(args.rom.resolve()))],keywords=[])
 prefix.append(node)
__file__=str(source);exec(compile(ast.fix_missing_locations(ast.Module(body=prefix,type_ignores=[])),str(source),'exec'),globals());__file__=own_file
assert hashlib.sha256(ROM.read_bytes()).hexdigest()==args.expected_sha,'Exact build required'
if not re.search(r'DEF _rf_newgame_choice ',noi):raise SystemExit('New-game menu not integrated; rebuild first.')
OUT=ROOT/'output/qa/new-game-native';OUT.mkdir(parents=True,exist_ok=True)
CHOICE=symbol('rf_newgame_choice');LOCK=symbol('rf_store_locked');SAVE=symbol('rf_save_ok');DIR=symbol('rf_dir')
original=args.earned_save.read_bytes();old=latest(original);assert old and old['schema']in(3,4,5,6)and old['size']==2544

def boot(path,data=None):
 global pb
 if data is not None:Path(str(path)+'.ram').write_bytes(data)
 pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);check('real cold title',screen()==0)
def progress():return bytes(pb.memory[RF+1:RF+2544])
def options():
 press('select');check('valid saved title opens save options default Continue',screen()==35 and pb.memory[CHOICE]==0)
def confirming():
 options();press('down');press('a');check('new choice opens a separate confirmation default Keep',screen()==36 and pb.memory[CHOICE]==0)
def do_new():
 confirming();press('down');press('a',150);check('explicit confirmation starts genuine fresh welcome',screen()==29 and value(12)==0 and value(13)==0 and tuple(value(i)for i in[1,2,3,4])==(0,2,6,0)and pb.memory[DIR]==2 and not pb.memory[SAVE]);check('new live journal has no earned photos/quests',all(best(i)==0 for i in range(192))and flags()[:9]==[0,0,0,0,0,0,0,32,2])

def line(y):return ''.join(chr(pb.memory[0,0x9800+y*32+x]+32)for x in range(20))
with tempfile.TemporaryDirectory(prefix='rockflip-new-game-native-')as work:
 work=Path(work)
 blank=work/'fresh.gbc';shutil.copy2(ROM,blank);boot(blank);press('select');check('fresh title has no saved-journal replacement menu',screen()==0 and not pb.memory[SAVE]);press('start');check('fresh title retains normal welcome',screen()==29 and value(12)==0);pb.stop()
 default=work/'default-continue.gbc';shutil.copy2(ROM,default);boot(default,original);before=progress();options();press('a',150);check('default menuA continues original journal without tutorial/reset',screen()==2 and value(12)==151 and progress()==before);pb.stop();check('default menuContinue saves no bytes',Path(str(default)+'.ram').read_bytes()==original)
 for case in ['menuB','confirmB','defaultKeepA']:
  cart=work/(case+'.gbc');shutil.copy2(ROM,cart);boot(cart,original);check('authentic earned151 loads',value(12)==151 and bool(pb.memory[SAVE])and not pb.memory[LOCK]);before=progress()
  if case=='menuB':options();press('down');press('up');press('b')
  else:
   confirming()
   if case=='confirmB':press('down');press('b')
   else:press('a')
  check('cancel preserves complete live journal',screen()==0 and progress()==before);pb.stop();check('opening/browsing/cancel writes zero SRAM bytes',Path(str(cart)+'.ram').read_bytes()==original)
  boot(cart);check('cold cancel retains old earned151 and complete metadata',value(12)==151 and progress()==before);enter_hike();check('ordinary continue retains earned journal',screen()==2 and value(12)==151);pb.stop()
 # Confirming changes live state only: power-off before first save resumes old.
 cart=work/'pre-autosave.gbc';shutil.copy2(ROM,cart);boot(cart,original);do_new();pb.stop();check('confirmed fresh welcome has not erased/written old SRAM',Path(str(cart)+'.ram').read_bytes()==original);boot(cart);check('cold before new autosave restores old journal',value(12)==151 and bool(pb.memory[SAVE]));pb.stop()
 # First confirmed new autosave preserves exactly the preceding verified record.
 cart=work/'new.gbc';shutil.copy2(ROM,cart);boot(cart,original);do_new();press('b',150);check('fresh hike begins unearned beside Nell',screen()==2 and value(12)==0 and flags()[:9]==[0,0,0,0,0,0,0,32,2]);press('start',150);check('first actual new autosave opens real Nell camp',screen()==9);pb.stop();new=Path(str(cart)+'.ram').read_bytes();r=latest(new)
 check('new autosave uses schema6 and advanced old sequence',r and r['schema']==6 and r['size']==2544 and r['sequence']==(old['sequence']+1)&65535)
 preserved=record(new,old['slot']);check('preceding verified old journal record byte-exact',preserved and preserved['bytes']==old['bytes'])
 boot(cart);check('cold actual new journal retains empty progress and fresh position',value(12)==0 and value(13)==0 and tuple(value(i)for i in[1,2,3,4])==(0,2,6,0));press('start',150);check('new saved journal continues directly without repeated welcome',screen()==2);pb.stop();(OUT/'confirmed-new-first-autosave.ram').write_bytes(new)
 # Explicit future-layout file locks all new-game entry and attempted writes.
 future=bytearray(original);future[3*8192:3*8192+4]=b'RF03';future[3*8192+4]=3
 locked=work/'future.gbc';shutil.copy2(ROM,locked);boot(locked,future);check('future layout is locked and explicitly labelled at title',pb.memory[LOCK]and 'READ ONLY'in line(14));press('select');check('locked title cannot open new-game menu',screen()==0);press('start',150);check('locked title enters readonly world without intro',screen()==2);press('start',150);pb.stop();check('locked future SRAM byte-identical after actual save attempt',Path(str(locked)+'.ram').read_bytes()==bytes(future))
 # Real older schema3 reader refuses the new schema6 safely; it cannot erase either record.
 oldrom=args.old_rom;oldnoi=Path(str(oldrom)+'.debug/symbols.noi');assert oldrom.exists()and oldnoi.exists(),'Provide pinned old schema3 cartridge+NOI for downgrade proof'
 h=harness(oldrom,oldnoi);h['OUT']=OUT;oldcart=work/'downgrade.gbc';shutil.copy2(oldrom,oldcart);open_rom(h,oldcart,new);h['check']('downgrade reader protects schema6',h['pb'].memory[h['symbol']('rf_store_locked')]==1);h['enter_hike']();h['press']('start',150);h['pb'].stop();check('downgrade save attempt cannot overwrite new or preceding record',Path(str(oldcart)+'.ram').read_bytes()==new)
receipt={'result':'pass','rom_sha256':args.expected_sha,'assertions':len(checks)+len(h['checks']),'frames':frames+h['frames'],'checks':checks,'old_reader_checks':h['checks'],'inputs':inputs,'genuine_source_save_sha256':hashlib.sha256(original).hexdigest(),'old_reader_ROM_sha256':hashlib.sha256(args.old_rom.read_bytes()).hexdigest(),'menu_screens':[35,36],'cancel_byte_exact':True,'confirmed_live_new_until_first_autosave':True,'preceding_record_kept_on_new_autosave':True,'future_and_downgrade_writes_blocked':True,'memory_writes':False,'human_reviewed':False,'physical_device_tested':False}
(OUT/'playtest.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['checks','old_reader_checks','inputs']},indent=2))
