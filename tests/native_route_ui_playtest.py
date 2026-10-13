"""Actual controller route/phase/clue/pacing proof on forthcoming6.
No emulated-memory progress writes; both modes use real earned SRAM.
"""
from pathlib import Path
from collections import deque
import argparse,sys,json,hashlib,tempfile,shutil
R=Path(__file__).resolve().parents[1]if Path(__file__).resolve().parent.name=='tests'else Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests'))
from native_snapshot_migration import harness,open_rom
import campaign_native_driver as driver
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);a=p.parse_args();ROM=R/'native/build/rom/RockFlip-Statewide.gbc';assert hashlib.sha256(ROM.read_bytes()).hexdigest()==a.expected_sha
O=R/'output/qa/route-ui-native';O.mkdir(parents=True,exist_ok=True);new=json.loads((R/'data/campaign.json').read_text());old=json.loads((R/'output/normal-play-proposals/campaign-legacy.json').read_text())
checks=[];frames=0;inputs=[];rows=[]
def setup(cart,data=None):
 h=harness(ROM,Path(str(ROM)+'.debug/symbols.noi'));h['OUT']=O;open_rom(h,cart,data);base=h['press'];h['press']=lambda button,settle=70:base(button,max(settle,150));h['enter_hike']();return h
def finish(h):
 global frames
 frames+=h['frames'];checks.extend(h['checks']);inputs.extend(h['inputs']);h['pb'].stop()
def line(h,y):return ''.join(chr(v+32)for v in h['pb'].memory[0,0x9800+y*32:0x9800+y*32+20]).rstrip()
def rfbytes(h):return bytes(h['pb'].memory[h['RF']+1:h['RF']+2544])
def direction(h,target):
 start=h['value'](1);world=h['world'];q=deque([(start,None)]);seen={start}
 if start==target:return'LOOK IN THIS HABITAT'
 names={'west':'W: FOLLOW THE TRAIL','east':'E: FOLLOW THE TRAIL','north':'N: TAKE THE SHORTCUT','south':'S: TAKE THE SHORTCUT'}
 while q:
  mid,first=q.popleft()
  for key in names:
   nxt=world[mid].get(key)
   if nxt is None or nxt in seen or world[nxt]['district_id']!=world[start]['district_id']:continue
   word=names[key]
   if world[mid]['district_id']=='D12'and world[mid]['subarea_id']!=world[nxt]['subarea_id']:word='W: ISLAND FERRY'if key=='west'else'E: ISLAND FERRY'
   step=first or word
   if nxt==target:return step
   seen.add(nxt);q.append((nxt,step))
 return'CHECK THE TRAIL MAP'
def expected(h,data,d):
 f=h['flags']();stage=(f[10+d//4]>>((d%4)*2))&3;bits=(f[14+d//2]>>((d%2)*4))&15
 if stage>=3:return None
 inds=[0]if stage==0 else[1,2]if stage==1 else[3];missing=[i for i in inds if not bits&(1<<i)];targets=data['districts'][d]['photo_targets']
 pick=next((i for i in missing if targets[i]['phase']==h['value'](4)),missing[0]if missing else None)
 if pick is None:
  if stage==2 and d in(0,9)and not(f[28+d//8]&(1<<(d%8))):return('REPLACE ITS COVER',direction(h,targets[3]['map_id']))
  return('PHOTOS READY','FILE AT YOUR CAMP')
 target=targets[pick];name=h['world'][target['map_id']]['name'];return(name,direction(h,target['map_id']))
def inspect(h,data,d,pinned=False):
 if pinned:
  driver.return_to_trail(h);mid=h['value'](1);camp=h['world'][mid]['camp']
  chosen=False
  for y in range(7):
   for x in range(10):
    if not h['blocked'](mid,x,y)and(camp is None or abs(x-camp[0])+abs(y-camp[1])>1):
     try:h['walk'](x,y)
     except AssertionError:continue
     chosen=True;break
   if chosen:break
  assert chosen;h['press']('start');h['check']('actual awaycamp pack25',h['screen']()==25);before=rfbytes(h);h['press']('up');h['check']('actual pinned notes32',h['screen']()==32);name_row,dir_row=12,13
 else:
  driver._local_campaign(h,d);before=rfbytes(h);h['press']('b');h['press']('down');name_row,dir_row=13,14
 want=expected(h,data,d)
 if want:
  h['check']('visible next missing fictional habitat name '+str((d,h['value'](1))),line(h,name_row)==want[0]);h['check']('visible direction follows actual portals '+str((d,h['value'](1))),line(h,dir_row)==want[1]);rows.append({'mode':bool(h['flags']()[8]&2),'district':d,'stage':driver._stage(h,d),'phase':h['value'](4),'map':h['value'](1),'name':line(h,name_row),'direction':line(h,dir_row)})
 h['check']('reading goal mutates no RF progress bytes',rfbytes(h)==before);h['press']('b');driver.return_to_trail(h)
def caption(h,data,d,wrong=False):
 st=data['districts'][d]['stages'][driver._stage(h,d)];choice=(st['correct_choice']+1)%3 if wrong else st['correct_choice'];driver._local_campaign(h,d);before=h['flags']();h['press']('a')
 for _ in range(choice):h['press']('down')
 h['press']('a');h['press']('b');h['press']('start');h['check']('physical ranger feedback19',h['screen']()==19)
 if wrong:h['check']('wrong caption never advances or earns note',h['flags']()==before)
 h['press']('b');driver.return_to_trail(h)
with tempfile.TemporaryDirectory(prefix='rockflip-route-ui-')as td:
 td=Path(td);cart=td/'fresh.gbc';shutil.copy2(ROM,cart);h=setup(cart)
 driver.complete_opening(h);h['check']('opening photos do not fill fresh D01 regional investigation',h['flags']()[14]&15==1 and not(h['flags']()[28]&1));h['check']('opening alone leaves regional story unfiled',driver._stage(h,0)==0)
 inspect(h,new,0);caption(h,new,0,True);caption(h,new,0);h['check']('first local habitat files stage0 only',driver._stage(h,0)==1)
 # Later-stage observation cannot bypass the still-missing paired comparison.
 driver.photo_target(h,new['districts'][0]['photo_targets'][3]);caption(h,new,0);h['check']('out-of-order night photo cannot advance missing day comparison',driver._stage(h,0)==1)
 for phase in [0,2]:h['rest_to'](phase);inspect(h,new,0,True)
 driver.photo_target(h,new['districts'][0]['photo_targets'][2]);inspect(h,new,0,True);driver.photo_target(h,new['districts'][0]['photo_targets'][1]);inspect(h,new,0);caption(h,new,0);h['check']('two distinct maps10 and14 legitimately file paired daylight stage',driver._stage(h,0)==2)
 inspect(h,new,0);caption(h,new,0);h['check']('actual map19 night52 photo plus committed care finish D01',driver._stage(h,0)==3)
 h['check']('all new D01 target maps physically visited',all(h['pb'].memory[h['RF']+h['offset'](23)+(mid>>3)]&(1<<(mid&7))for mid in [0,10,14,19]))
 points=h['value'](13);flags=h['flags']();driver._local_campaign(h,0);h['press']('start');h['press']('a');h['press']('b');h['check']('filed local story repeated inputs do not farm points or flags',h['value'](13)==points and h['flags']()==flags);driver.return_to_trail(h)
 for d in [4,15]:
  for st in new['districts'][d]['stages']:
   for i in st['photo_target_indexes']:
    driver.photo_target(h,new['districts'][d]['photo_targets'][i]);inspect(h,new,d,True)
   inspect(h,new,d);caption(h,new,d);h['check']('fresh D'+str(d+1)+' local phase/site predicates advance only current stage',driver._stage(h,d)==st['stage_index']+1)
 h['check']('southSierra72 and later Modoc234/237 really visited',all(h['pb'].memory[h['RF']+h['offset'](23)+(mid>>3)]&(1<<(mid&7))for mid in [72,234,237]));h['travel'](80);h['check']('actual map80 is visible named Delta habitat',h['value'](1)==80 and h['world'][80]['name']=='DELTA REED BANK'and line(h,0)=='DELTA REED BANK');h['pb'].screen.image.save(O/'Delta80.png');finish(h)
 lc=td/'legacy.gbc';shutil.copy2(ROM,lc);h=setup(lc,(R/'output/qa/normal-play-audit/actual-layout5-partial-D01.ram').read_bytes());h['check']('genuine continued5 route remains legacy',not(h['flags']()[8]&2));inspect(h,old,0);caption(h,old,0);inspect(h,old,0);driver._local_campaign(h,0);h['check']('legacy paired caption title retained',line(h,2)=='SAND AND CREVICE');h['press']('b');driver.return_to_trail(h)
 h['travel'](68);inspect(h,old,4);h['rest_to'](2);inspect(h,old,4,True);finish(h)
result={'result':'pass','rom_sha256':a.expected_sha,'assertions':len(checks),'frames':frames,'checks':checks,'inputs':inputs,'observed_route_rows':rows,'memory_writes':False,'AI_technical_pacing_review':True,'human_fun_approved':False};(O/'playtest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['checks','inputs','observed_route_rows']}))
