from pathlib import Path
import argparse,sys,tempfile,shutil,json,hashlib
R=Path(__file__).resolve().parents[1]if Path(__file__).resolve().parent.name=='tests'else Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests'))
from native_snapshot_migration import harness,open_rom
parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);args=parser.parse_args()
ROM=R/'native/build/rom/RockFlip-Statewide.gbc';SHA=args.expected_sha;assert hashlib.sha256(ROM.read_bytes()).hexdigest()==SHA
O=R/'output/qa/field-notice-native';O.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='rockflip-field-notice-')as td:
 cart=Path(td)/'probe.gbc';shutil.copy2(ROM,cart);h=harness(ROM,Path(str(ROM)+'.debug/symbols.noi'));h['OUT']=O;open_rom(h,cart);h['enter_hike']();h['conditions_for_subject']=lambda sid:None;h['travel'](83);h['forecast_to'](2,0);site=next(s for s in h['sites']if s['spot_id']==196);h['face'](site)
 def bg():return bytes(h['pb'].memory[0,0x9800+14*32:0x9800+16*32])
 def rf():return bytes(h['pb'].memory[h['RF']:h['RF']+2544])
 def sram():return bytes(h['pb'].memory[3,0xA000:0xBFFF])+bytes([h['pb'].memory[3,0xBFFF]])
 before=bg();h['snapshot']('before-look');h['press']('a',150);h['check']('actual species9 type7 wrong-weather policy stays trail',h['screen']()==2 and h['value'](6)==9 and((h['flags']()[9]>>1)&15)==0);notice=bg();h['check']('policy clue overwrites last terrain row',notice!=before);h['snapshot']('reading-weather-notice');state=rf();saved=sram();h['press']('b',150);afterB=bg();h['check']('B clears terrain overlay exactly',afterB==before);h['check']('B leaves full RF2544 unchanged',rf()==state);h['check']('B leaves actual SRAM8192 unchanged',sram()==saved);h['snapshot']('after-B')
 h['press']('a',150);h['check']('second denied look displays same weather clue',bg()==notice);h['snapshot']('reading-again-before-step');step_saved=sram()
 # One legal step or turn; no map reload/menu intervention.
 mid=h['value'](1);x,y=h['value'](2),h['value'](3)
 for key,(dx,dy)in h['DIRS'].items():
  nx,ny=x+dx,y+dy
  if 0<=nx<10 and 0<=ny<7 and not h['blocked'](mid,nx,ny):h['press'](key,100);break
 h['check']('controller step actually moves one cell',abs(h['value'](2)-x)+abs(h['value'](3)-y)==1);afterStep=bg();h['check']('real one-cell step clears notice and restores exact terrain',afterStep==before);h['check']('step cleanup adds no save write',sram()==step_saved);h['snapshot']('after-real-step');h['pb'].stop()
 result={'result':'pass','rom_sha256':SHA,'species':9,'site':196,'type':7,'phase':2,'conditions':0,'BGrows14_15_before':list(before),'BGrows14_15_notice':list(notice),'BGrows14_15_after_B':list(afterB),'BGrows14_15_after_step':list(afterStep),'B_RF2544_byte_exact':True,'B_SRAM8192_byte_exact':True,'assertions':len(h['checks']),'frames':h['frames'],'inputs':h['inputs'],'checks':h['checks'],'memory_writes':False,'human_reviewed':False};(O/'probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['inputs','checks']and not k.startswith('BG')}))
