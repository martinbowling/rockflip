"""Staged controller acceptance: elapsed video time, not game-update counts.
Run only after integration; reads state, never writes clocks/RAM/progress.
The all151 and twelve-family quality suites remain independent requirements.
"""
from pathlib import Path
import argparse,sys,tempfile,shutil,json,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tests'))
from native_snapshot_migration import harness,open_rom,resume
p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=R/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--noi',type=Path);p.add_argument('--expected-sha',required=True);p.add_argument('--fixture',type=Path,default=R/'output/qa/production/controller-earned-complete.ram');p.add_argument('--out',type=Path,default=R/'output/qa/camera-cadence-native');a=p.parse_args()
assert hashlib.sha256(a.rom.read_bytes()).hexdigest()==a.expected_sha
noi=a.noi or Path(str(a.rom)+'.debug/symbols.noi');assert '_rf_camera_clock_step 'in noi.read_text(), 'Staged timing not integrated; old ROM is no proof'
a.out.mkdir(parents=True,exist_ok=True);results=[]
for sid,room,lens in [(0,0,False),(64,62,False),(64,203,False),(64,62,True),(64,203,True),(8,4,False)]:
 h=harness(a.rom,noi);h['OUT']=a.out
 with tempfile.TemporaryDirectory(prefix='rockflip-vblank-camera-') as td:
  cart=Path(td)/'candidate.gbc';shutil.copyfile(a.rom,cart);open_rom(h,cart,a.fixture.read_bytes());resume(h)
  h['travel'](room);site=next(s for s in h['sites']if s['species_id']==sid and s['room_id']==room);h['rest_to'](next(i for i in range(3)if site['phase_mask']&(1<<i)));h['face'](site)
  for _ in range(4):
   h['press']('a',150)
   if h['screen']()==3:break
   if site['interaction_type']in(0,5):h['press']('b',150)
  h['check']('actual subject selected',h['screen']()==3);h['press']('a',100)
  pb=h['pb'];read=lambda name:pb.memory[h['symbol'](name)];clock=lambda:h['word'](h['symbol']('rf_behavior_clock'));vbl=lambda:h['word'](h['symbol']('sys_time'))
  if bool(read('rf_lens_active'))!=lens:h['press']('select',100)
  # Real framing reset after any blocking setup; natural behavior is not reset.
  h['press']('right',0)
  for _ in range(100):
   h['tick'](1)
   if h['value'](7)>0:break
  start=vbl();first=h['value'](7);threshold={};transitions=[];last=read('rf_motion');samples=[]
  for _ in range(1600):
   h['tick'](1);elapsed=(vbl()-start)&65535;focus=h['value'](7);motion=read('rf_motion')
   if focus>=45 and 45 not in threshold:threshold[45]=elapsed
   if focus>=60 and 60 not in threshold:threshold[60]=elapsed
   if motion!=last:transitions.append(elapsed);last=motion
   if len(transitions)>=5 and 60 in threshold:break
  h['check']('full focus uses approximately80 actual VBlanks after first increment',70<=threshold[60]<=84)
  h['check']('usable focus uses approximately60 actual VBlanks after first increment',50<=threshold[45]<=64)
  period=h['species'][sid].get('behavior_params',{}).get('period',90)
  gaps=[y-x for x,y in zip(transitions,transitions[1:])]
  h['check']('four natural cycles remain calibrated despite lens/map redraws',len(gaps)==4 and all(abs(g-(period+5))<=6 for g in gaps))
  h['check']('harmless framing keeps stress zero',h['value'](10)==0)
  # Actual >16bit video-clock wrap. No injection. Bounded elapsed computation
  # must preserve a still usable camera and source-period quality semantics.
  before=vbl();h['tick'](66000);h['check']('natural clock wrapped during uninterrupted camera wait',((vbl()-before)&65535)<1000)
  h['check']('focus remains full after wrap',h['value'](7)==60)
  h['check']('camera remains available',h['screen']()==4)
  h['check']('elapsed_cycle cannot become fresh again at wrap',clock()>=period)
  h['snapshot'](f'cadence-{sid}-{room}-lens{int(lens)}')
  results.append({'species':sid,'map':room,'lens':lens,'first_focus':first,'threshold_vbl':threshold,'motion_intervals_vbl':gaps,'checks':h['checks'],'inputs':h['inputs'],'frames':h['frames']});pb.stop(save=False)
report={'result':'pass','rom_sha256':a.expected_sha,'assertions':sum(len(r['checks']) for r in results),'frames':sum(r['frames'] for r in results),'fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'controller_only':True,'RAM_clock_progress_writes':False,'scope':'Actual controller cadence/fullVBlankwrap only; independent score, wedge, save and all151 suites also required','records':results};(a.out/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['result','rom_sha256','assertions','frames','fixture_sha256']},indent=2))
