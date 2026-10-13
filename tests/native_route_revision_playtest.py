"""Forthcoming6 controller migration, legacy rules, fresh care and local notes.
Authentic5 fixture and real5 reader; never writes emulated progress memory.
"""
from pathlib import Path
import argparse,sys,hashlib,json,shutil,tempfile
R=Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name=='tests' else Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests'))
from native_snapshot_migration import harness,open_rom,latest,BASE
import campaign_native_driver as driver
parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);a=parser.parse_args()
ROM=R/'native/build/rom/RockFlip-Statewide.gbc';assert hashlib.sha256(ROM.read_bytes()).hexdigest()==a.expected_sha
O=R/'output/qa/route-revision-native';O.mkdir(parents=True,exist_ok=True)
FIX=R/'output/qa/normal-play-audit/actual-layout5-partial-D01.ram';oldrom=R/'output/build-candidates/RockFlip-Statewide-5762.gbc'
original=FIX.read_bytes();record=latest(original);assert record['schema']==5 and record['size']==2544
checks=[];frames=0;inputs=[]
def setup(cart,data=None,rom=ROM):
 h=harness(rom,Path(str(rom)+'.debug/symbols.noi'));h['OUT']=O;open_rom(h,cart,data)
 original_press=h['press'];h['press']=lambda button,settle=70:original_press(button,max(settle,150))
 return h
def finish(h):
 global frames
 checks.extend(h['checks']);frames+=h['frames'];inputs.extend(h['inputs'])
def line(h,y):return ''.join(chr(v+32)for v in h['pb'].memory[0,0x9800+y*32:0x9800+y*32+20]).rstrip()
def read(h,offset,n):return bytes(h['pb'].memory[h['RF']+offset:h['RF']+offset+n])
with tempfile.TemporaryDirectory(prefix='rockflip-route6-')as td:
 td=Path(td);cart=td/'legacy.gbc';shutil.copy2(ROM,cart);h=setup(cart,original);flags=h['flags']();qoff=h['offset'](23)+56
 h['check']('genuine old5 authenticated as legacy route0',h['pb'].memory[h['symbol']('rf_store_loaded_layout')]==5 and not(flags[8]&2))
 h['check']('every old partial/filed/award flag preserved without reseeding',bytes(flags)==record['payload'][qoff:qoff+32])
 h['check']('entire old album and spot states retained',read(h,16,2184)==record['payload'][16:2200])
 h['check']('old pose conditions retained byte exactly',read(h,2256,288)==record['payload'][2256:2544]);h['enter_hike']();h['open_camp']();h['press']('down')
 h['check']('old partially earned D01 still shows original first investigation',h['screen']()==17 and line(h,2)=='A HOME BELOW')
 h['pb'].stop();migrated=Path(str(cart)+'.ram').read_bytes();new=latest(migrated)
 assert new['schema']==6 and new['size']==2544;checks.append('first actual save migrates5 to6 same2544')
 assert migrated[BASE+record['slot']*4096:BASE+(record['slot']+1)*4096]==record['bytes'];checks.append('old committed record preserved4096 bytes')
 h2=setup(cart);h2['check']('cold6 legacy flags stay exact without award reseed',h2['flags']()==flags and not(h2['flags']()[8]&2));h2['pb'].stop();finish(h);finish(h2)
 oldcart=td/'reader5.gbc';shutil.copy2(oldrom,oldcart);old=setup(oldcart,migrated,oldrom);old['check']('actual accepted5 reader locks future6',old['pb'].memory[old['symbol']('rf_store_locked')]==1);old['enter_hike']();old['press']('start');old['pb'].stop();assert Path(str(oldcart)+'.ram').read_bytes()==migrated;checks.append('actual5 reader leaves both records byte exact');finish(old)
 fresh=td/'fresh.gbc';shutil.copy2(ROM,fresh);h=setup(fresh);h['enter_hike']();h['check']('genuine fresh6 route variant enabled with no earned campaign',bool(h['flags']()[8]&2)and h['flags']()[10:30]==[0]*20)
 h['travel'](68);h['open_camp']();h['press']('b');h['press']('start')
 # Pack pinnednotes needs physical away tile; select nearest reachable legal tile.
 if h['screen']()==9:h['press']('b')
 for y in range(7):
  for x in range(10):
   mid=h['value'](1);camp=h['world'][mid]['camp']
   if not h['blocked'](mid,x,y)and abs(x-camp[0])+abs(y-camp[1])>1:
    try:h['walk'](x,y)
    except AssertionError:continue
    break
  else:continue
  break
 h['press']('start');h['press']('up');h['check']('unfinished opening no longer hides current D05 goal',h['screen']()==32 and line(h,3)=='A HIGH LAKE EDGE');h['press']('b');h['press']('b')
 h['travel'](19);h['rest_to'](2);site=next(s for s in h['sites']if s['spot_id']==52);h['face'](site);h['press']('a');h['check']('prior-care observation is actual site52',h['screen']()==3);h['press']('b');h['press']('b');h['check']('prior care cannot grant missing new photo/care',not(h['flags']()[14]&8)and not(h['flags']()[28]&1))
 driver.photo_target(h,0);h['check']('former site0 photo and closure cannot satisfy new night52 evidence',not(h['flags']()[14]&8)and not(h['flags']()[28]&1))
 driver.photo_target(h,52);h['check']('actual focused night52 photo and committed closure grant paired evidence',bool(h['flags']()[14]&8)and bool(h['flags']()[28]&1));h['pb'].stop();finish(h)
result={'result':'pass','rom_sha256':a.expected_sha,'assertions':len(checks),'frames':frames,'authentic_old5_fixture_sha256':hashlib.sha256(original).hexdigest(),'actual_old5_reader_sha256':hashlib.sha256(oldrom.read_bytes()).hexdigest(),'old5_awards_never_reseeded':True,'legacy_mode_preserved':True,'fresh_photo_first_care':True,'memory_writes':False,'human_fun_approved':False,'checks':checks,'inputs':inputs}
(O/'playtest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['checks','inputs']}))
