"""Execute after restoration integration: actual buttons, no memory writes."""
from pathlib import Path
import ast,argparse,hashlib
parser=argparse.ArgumentParser();parser.add_argument("--rom",type=Path);parser.add_argument("--expected-sha");args=parser.parse_args()
if args.rom and args.expected_sha:assert hashlib.sha256(args.rom.read_bytes()).hexdigest()==args.expected_sha,"Requested ROM hash differs"
own_file=__file__;ROOT=Path(own_file).resolve().parents[1];source=ROOT/'tests/production_playtest.py';tree=ast.parse(source.read_text());prefix=[]
for node in tree.body:
 if isinstance(node,ast.With):break
 if args.rom and isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROM'for t in node.targets):node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(args.rom.resolve()))],keywords=[])
 prefix.append(node)
__file__=str(source);exec(compile(ast.fix_missing_locations(ast.Module(body=prefix,type_ignores=[])),str(source),'exec'),globals());__file__=own_file
OUT=ROOT/'output/qa/restore-native';OUT.mkdir(parents=True,exist_ok=True)
if not re.search(r'DEF _rf_restore_busy ',noi):raise SystemExit('Restoration module not integrated in selected ROM; rebuild first.')
BUSY=symbol('rf_restore_busy');POSE=symbol('rf_restore_frame');SINCE=symbol('rf_restore_since');CLOCK=symbol('sys_time')
raw=bytes(int(v)for v in re.search(r'frames\[\]=\{([^}]+)',(ROOT/'native/plugins/rockflip/engine/src/rockflip_rock_restore.c').read_text())[1].split(','))
reports=[];completed_uploads=[]
def spotflag(site):return pb.memory[RF+offset(19)+site['spot_id']]
def on_completed_upload(context):
 pose=pb.memory[POSE]
 if pb.memory[BUSY]and pose<=3:
  check('completed art API returns bank0',not(pb.memory[0xff4f]&1))
  check('completed art API matches exact source pose',bytes(pb.memory[0,0x8e60:0x8ea0])==raw[pose*64:(pose+1)*64])
  completed_uploads.append({'frame':frames,'pose':pose,'map':value(1)})
def boot(path):
 global pb
 pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0)
 packed=int(re.search(r'DEF _rf_restore_drawn 0x([0-9a-fA-F]+)',noi)[1],16);pb.hook_register(packed>>16,packed&65535,on_completed_upload,None)
 tick(180)
 for _ in range(8):
  if screen()==2:break
  press('b'if screen()==29 else'a',150)
 check('ordinary controller boot reaches hike',screen()==2)
def opened(site,photo=False):
 travel(site['room_id']);rest_to(next(p for p in range(3)if site['phase_mask']&(1<<p)));face(site);press('a',150)
 if screen()==3:
  if photo:press('a');tick(180);press('a',150);check('actual source photo earns record',screen()==5 and best(site['species_id'])>0)
  press('b',150)
 check('actual loose/wet rock opened on trail',screen()==2 and bool(spotflag(site)&1))
def begin():
 pb.button_press('b');tick(1);pb.button_release('b')
 for _ in range(10):
  if pb.memory[BUSY]:return
  tick(1)
 check('actual B begins restoration transaction',False)
def vram(bank):return bytes(pb.memory[bank,0x8000:0x9fff])+bytes([pb.memory[bank,0x9fff]])
def water_span(mid):
 m=world[mid]
 if not any('W'in row for row in m['terrain']):return None
 if mid==1 and m.get('art_style')=='desert':return 0x9500,256
 text=(ROOT/f'native/plugins/rockflip/engine/src/rf_map_art_{mid:04d}.c').read_text()
 start=int(re.search(r'set_bkg_data\((\d+),4,\(frame&1\)',text)[1]);return 0x9000+(start if start<128 else start-256)*16,64
def complete(site):
 before=[value(i)for i in [1,2,3,4,13,21]];flags_before=flags();spot_before=spotflag(site);seen=set();since={};frame0=frames;pose_trace=[]
 # Deliberately cross an actual idle timer boundary on camp maps.
 mid=value(1);camp=world[mid]['camp'];wet=water_span(mid)
 if camp is not None:
  for _ in range(110):
   if ((word(CLOCK)-word(symbol('rf_camp_clock')))&65535)>=88:break
   tick(1)
 elif wet:
  while word(CLOCK)&31<24:tick(1)
 base=[vram(0),vram(1)];oam=bytes(pb.memory[0xfe00:0xfea0]);water_patterns=set();camp_patterns=set()
 x=site['game_tile_x']*2;y=2+site['game_tile_y']*2;target={0x1800+y*32+x,0x1800+y*32+x+1,0x1800+(y+1)*32+x,0x1800+(y+1)*32+x+1}
 begin()
 inject={3:'start',7:'a',11:'select',15:'right',19:'b',35:'start',39:'a',43:'right',47:'b'};held=None
 for n in range(180):
  if held:pb.button_release(held);held=None
  if n in inject:held=inject[n];pb.button_press(held)
  tick(1);pose=pb.memory[POSE]
  got_diag=bytes(pb.memory[0,0x8e60:0x8ea0]);pose_trace.append({'frame':frames,'pose':pose,'busy':pb.memory[BUSY],'source_match':[i for i in range(4)if got_diag==raw[i*64:(i+1)*64]],'since':word(SINCE),'clock':word(CLOCK),'target_tiles':[pb.memory[0,0x9800+(y+dy)*32+x+dx]for dy in [0,1]for dx in [0,1]],'target_attrs':[pb.memory[1,0x9800+(y+dy)*32+x+dx]for dy in [0,1]for dx in [0,1]]})
  if pb.memory[BUSY]and pose<=3:
   check('animation retains hike and input-blocked explorer',screen()==2 and [value(i)for i in [1,2,3,4,13,21]]==before)
   check('animation preserves open/pending-care and quest flags',spotflag(site)==spot_before and flags()==flags_before)
   check('animation keeps actual player OBJ enabled',bool(pb.memory[0xff40]&2))
   check('animation leaves OAM positions and patterns unchanged',bytes(pb.memory[0xfe00:0xfea0])==oam)
   for bank in [0,1]:
    current=vram(bank)
    def permitted(i):
     if i in target:return True
     if bank==0 and 0xe60<=i<0xea0:return True
     if bank==0 and camp is not None and 0xe00<=i<0xe60:return True
     return bank==1 and wet is not None and wet[0]-0x8000<=i<wet[0]-0x8000+wet[1]
    bad=[{'address':hex(0x8000+i),'before':a,'after':b}for i,(a,b)in enumerate(zip(base[bank],current))if a!=b and not permitted(i)]
    if bad:(OUT/'VRAM-failure.json').write_text(json.dumps({'ROM_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'site':site,'bank':bank,'pose':pose,'water_span':wet,'camp':camp,'bad':bad},indent=2)+'\n')
    check('animation leaves unrelated VRAM patterns/maps/attrs unchanged',not bad)
   if camp is not None:camp_patterns.add(bytes(pb.memory[0,0x8e00:0x8e60]))
   if wet:water_patterns.add(bytes(pb.memory[1,wet[0]:wet[0]+wet[1]]))
   got=bytes(pb.memory[0,0x8e60:0x8ea0])
   if got==raw[pose*64:(pose+1)*64]:
    seen.add(pose);since.setdefault(pose,frames);check('source pattern frame exact at observed visible pose',True)
  if not pb.memory[BUSY]:break
 if held:pb.button_release(held)
 (OUT/'last-pose-trace.json').write_text(json.dumps({'seen':sorted(seen),'trace':pose_trace},indent=2)+'\n')
 check('all four poses natively observed',seen=={0,1,2,3})
 check('final canonical cover is closed and care incremented once',not(spotflag(site)&1)and bool(spotflag(site)&4)and value(13)==min(before[4]+(0 if spot_before&4 else 1),99))
 check('queued menus/movement do not fire after closure',screen()==2 and [value(i)for i in [1,2,3,4,21]]==[before[i]for i in [0,1,2,3,5]])
 points=value(13);press('b',150);check('duplicate restoration earns no extra care',value(13)==points and not pb.memory[BUSY])
 if camp is not None:check('camp idle animation continues during restoration',len(camp_patterns)>=2)
 if wet:check('water keeps valid native animation during restoration',len(water_patterns)>=1)
 reports.append({'camp_pattern_variants':len(camp_patterns),'water_pattern_variants':len(water_patterns),'site':site['spot_id'],'region':site['region_id'],'source_poses':sorted(seen),'source_pose_frames':since,'input_to_finished_frames':frames-frame0})
with tempfile.TemporaryDirectory(prefix='rockflip-restore-native-')as work:
 cart=Path(work)/ROM.name;shutil.copy2(ROM,cart);boot(cart)
 first=next(s for s in sites if s['interaction_type']==0)
 opened(first,True);points=value(13);quest=flags();oldspot=spotflag(first);position={i:value(i)for i in [1,2,3,4]};begin()
 for _ in range(40):
  tick(1)
  if pb.memory[BUSY]and pb.memory[POSE]==1:break
 check('interruption occurs during unsettled source pose',pb.memory[BUSY]and pb.memory[POSE]==1)
 pb.stop();ram=Path(str(cart)+'.ram');check('actual prior SRAM exists at interruption',ram.exists());shutil.copy2(ram,OUT/'interrupted-open.ram')
 boot(cart);check('cold interruption restores old open cover with no early reward',spotflag(first)==oldspot and value(13)==points and flags()==quest and all(value(i)==v for i,v in position.items())and not pb.memory[BUSY]);face(first);complete(first)
 # Each newly introduced stone has its own interrupted transaction and cold
 # continuation, rather than borrowing the first site's recovery evidence.
 for sid in [7,145,296,463,490]:
  introduced=next((s for s in sites if s['spot_id']==sid and s['interaction_type']==0),None)
  if introduced is None:continue
  opened(introduced);points=value(13);quest=flags();oldspot=spotflag(introduced)
  position={i:value(i)for i in [1,2,3,4]};begin()
  for _ in range(40):
   tick(1)
   if pb.memory[BUSY]and pb.memory[POSE]==1:break
  check(f'new site{sid} actually interrupted in unsettled pose',pb.memory[BUSY]and pb.memory[POSE]==1)
  pb.stop();shutil.copy2(Path(str(cart)+'.ram'),OUT/f'interrupted-open-site{sid}.ram')
  boot(cart)
  check(f'new site{sid} cold interruption retains open cover and complete progression',
        spotflag(introduced)==oldspot and value(13)==points and flags()==quest
        and all(value(i)==v for i,v in position.items())and not pb.memory[BUSY])
  face(introduced);complete(introduced)
 # Every shipped loose cover gets its own actual four-pose transaction.
 # A per-district representative cannot prove all authored locations.
 completed_sites={r['site']for r in reports}
 for site in sorted((s for s in sites if s['interaction_type']==0 and s['spot_id']not in completed_sites),key=lambda s:s['spot_id']):
  opened(site);complete(site)
 check('every authored dry cover independently restores through all four poses',
       {r['site']for r in reports}=={s['spot_id']for s in sites if s['interaction_type']==0})
 wet=next(s for s in sites if s['interaction_type']==5);opened(wet);old=value(13);press('b',150)
 check('type5 wet rock keeps instant path and once-only care',not pb.memory[BUSY]and not(spotflag(wet)&1)and value(13)==min(old+1,99));press('b',150);check('wet rock duplicate grants no care',value(13)==min(old+1,99))
 points=value(13);care={s['spot_id']:spotflag(s)for s in sites if spotflag(s)&4};pb.stop();boot(cart)
 check('cold committed closure retains care and cover',value(13)==points and all(pb.memory[RF+offset(19)+sid]==v for sid,v in care.items()));pb.stop()
receipt={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'frames':frames,'reports':reports,'checks':checks,'inputs':inputs,'memory_writes':False,'completed_art_upload_hooks':completed_uploads,'hook_scope':'Read-only execution breakpoint in isolated copied ROM after art API returns; no gameplay RAM writes','cold_interruption':'prior actual open SRAM restored without rewards','type5_instant_tested':True,'all_authored_dry_sites':len(reports),'human_reviewed':False,'physical_device_tested':False}
(OUT/'playtest.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['checks','inputs','reports']},indent=2))
