"""Independent real-ROM visual checks using controller-only progress and cold SRAM.

Reads live state/symbols for observation; never writes RAM or injects achievements.
Reuses the established legal navigation helpers but asserts actual rendered pixels.
"""
from pathlib import Path
import hashlib,json,shutil,tempfile,sys,argparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
parser=argparse.ArgumentParser();parser.add_argument('--expected-sha',required=True);parser.add_argument('--probe-13',action='store_true');args=parser.parse_args();EXPECTED=args.expected_sha
OUT=ROOT/'output/qa/native-visual';OUT.mkdir(parents=True,exist_ok=True)
# Import definitions only, avoiding the full test and its diagnostic canary writes.
source=(ROOT/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0]
h={'__file__':str(ROOT/'tests/production_playtest.py')};exec(compile(source,'navigation_helpers','exec'),h)
h['OUT']=OUT;h['checks']=[];h['inputs']=[];h['frames']=0
sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==EXPECTED,'Need exact requested frozen ROM'
manifest=json.loads((ROOT/'art/out/ranger-art-manifest.json').read_text())
campaign=json.loads((ROOT/'data/campaign.json').read_text())['districts']
results={'status':'running','rom_sha256':sha,'progress_method':'normal controller inputs only; RAM read for observation, never written','rangers':[],'photos':[],'visual_blockers':[],'comparison_mask':{'excluded_pixels':128,'field_pixels':8192,'reason':'Two8x8camera reticle cells absent from album; all other animal and backdrop pixels compared exactly'},'pending':['Human aesthetic/audio/fun review','Physical Chromatic display and cartridge acceptance']}
def check(name,ok):h['check'](name,ok)
def image(name):
 im=h['pb'].screen.image.copy();im.save(OUT/(name+'.png'));return im

def exact_index_shape(actual,expected):
 # Native RGB output can be emulator-transformed; each authored index must map
 # consistently to one distinct displayed RGB value at every pixel.
 mapping={}
 for idx,rgb in zip(expected.get_flattened_data(),actual.convert('RGB').get_flattened_data()):
  if idx in mapping and mapping[idx]!=rgb:return False
  mapping[idx]=rgb
 return len(set(mapping.values()))==len(mapping)

def picture_bytes(im):
 # Same128x64 camera field in both screens; mask only the two8x8 UI reticle
 # cells, which are absent in album. No animal/background pixels otherwise masked.
 im=im.crop((16,32,144,96)).convert('RGB')
 for x in (32,88):
  for y in range(24,32):
   for xx in range(x,x+8):im.putpixel((xx,y),(0,0,0))
 return im.tobytes()

def snapshot_byte(sid):return h['pb'].memory[h['RF']+2256+sid]
def album(sid,label):
 h['press']('select');check('guide opens by SELECT',h['screen']()==7)
 for _ in range((sid-h['value'](14))%151):h['press']('right',24)
 h['press']('start',100);check('stored album opens by START',h['screen']()==10)
 im=image(label);h['press']('b');h['press']('b');check('album exits to trail',h['screen']()==2);return im

def blue_field(im):
 pixels=list(im.crop((16,32,144,96)).convert('RGB').get_flattened_data())
 return sum(b>r and b>=g for r,g,b in pixels)/len(pixels)

def photograph(sid,distance,phase):
 site=next(s for s in h['sites'] if s['species_id']==sid and s['phase_mask']&(1<<phase))
 h['travel'](site['room_id']);h['rest_to'](phase);h['face'](site)
 h['press']('a',100);check(f'normal encounter species{sid}',h['screen']()==3 and h['value'](6)==sid)
 h['press']('a');check('viewfinder opens',h['screen']()==4)
 for _ in range(4-distance):h['press']('down',20)
 check('requested native photo scale',h['value'](8)==distance)
 # Wait for a real nonzero motion frame with ample transition margin. No timing
 # flags are forced. Both water turtles may naturally hide during one cycle.
 clock=h['symbol']('rf_behavior_clock');period=h['species'][sid].get('behavior_params',{}).get('period',24)
 for _ in range(2000):
  h['tick'](2);c=h['word'](clock)
  if h['value'](7)>=45 and h['pb'].memory[h['MOTION']]==1 and not h['pb'].memory[h['HIDDEN']] and 3<c%period<period-10:break
 else:raise AssertionError(f'No calm focused nonzero pose for{sid}')
 before_state={'subject_x':h['pb'].memory[h['symbol']('rf_subject_x')],'subject_y':h['pb'].memory[h['symbol']('rf_subject_y')],'aim':h['value'](9),'distance':h['value'](8),'motion':h['pb'].memory[h['MOTION']],'clock':h['word'](clock),'focus':h['value'](7)}
 results.setdefault('photo_transactions',[]).append({'species_id':sid,'before':before_state})
 if sid in (13,61,73):check(f'quality helper preserves naturally stationary horizontal position{sid}',before_state['subject_x']==0)
 # A framebuffer belongs to a completed LCD frame; live C state can lead the
 # last rendered image during a banked draw. Wait for an unchanged frame/state.
 h['tick'](8)
 before=image(f'species-{sid:03d}-camera-{distance}px');results['photo_transactions'][-1]['camera_portrait_cells']=[(x,y,h['pb'].memory[0,0x9800+y*32+x]) for y in range(4,12) for x in range(2,18) if h['pb'].memory[1,0x9800+y*32+x]==13];beforepose=h['pb'].memory[h['MOTION']]
 h['press']('a',100);check('real shutter stores photo',h['screen']()==5 and h['best'](sid)>=2)
 packed=snapshot_byte(sid);results['photo_transactions'][-1]['stored']={'snapshot':packed,'aim':h['pb'].memory[h['RF']+h['offset'](17)+sid],'distance':h['pb'].memory[h['RF']+h['offset'](16)+sid]};check('stored nonzero known animation pose',packed&128 and packed&8 and beforepose==1)
 check('distance metadata matches requested scale',h['pb'].memory[h['RF']+h['offset'](16)+sid]==distance)
 h['press']('b');
 if site['interaction_type'] in (0,5):h['press']('b')
 saved=album(sid,f'species-{sid:03d}-album')
 a,b=picture_bytes(before),picture_bytes(saved);diff=sum(x!=y for x,y in zip(a,b))
 if a!=b:results['visual_blockers'].append({'species_id':sid,'issue':'Camera-to-album animal/backdrop pixels differ outside reticle','changed_color_bytes':diff,'evidence':[f'species-{sid:03d}-camera-{distance}px.png',f'species-{sid:03d}-album.png']})
 else:check(f'camera animal/backdrop equals actual album species{sid}',True)
 if sid in (61,73):check(f'marine{sid} camera and album visibly blue',blue_field(before)>.55 and blue_field(saved)>.55)
 result={'species_id':sid,'spot_id':site['spot_id'],'map_id':site['room_id'],'phase':phase,'distance':distance,'portrait_scale':32 if distance==4 else 48,'snapshot_byte':packed,'motion_frame':(packed>>3)&1,'camera_album_changed_color_bytes':diff,'field_sha256':hashlib.sha256(a).hexdigest(),'camera_blue_fraction':blue_field(before) if sid in (61,73) else None}
 results['photos'].append(result);return saved

try:
 with tempfile.TemporaryDirectory(prefix='rockflip-native-visual-') as tmp:
  path=Path(tmp)/ROM.name;shutil.copy2(ROM,path)
  def boot():
   h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();check('boot enters playable trail',h['screen']()==2)
  boot()
  hashes=set()
  for d in ([] if args.probe_13 else campaign):
   mid=next(m['id'] for m in h['world'].values() if m['district_id']==d['district_id'] and not m.get('hidden'))
   h['travel'](mid);h['open_camp']();check('physical camp by legal route and START',h['screen']()==9)
   im=image(f"camp-{d['district_id']}-{d['ranger_name']}");crop=im.crop((8,16,56,64));digest=hashlib.sha256(crop.tobytes()).hexdigest();hashes.add(digest)
   magenta=sum(r>220 and g<40 and b>220 for r,g,b in crop.convert('RGB').get_flattened_data())
   if magenta:results['visual_blockers'].append({'district_id':d['district_id'],'issue':'Opaque magenta transparency sentinel rendered in BG portrait slot0','magenta_pixels':magenta,'evidence':f"camp-{d['district_id']}-{d['ranger_name']}.png"})
   art=next(m for m in manifest.values() if m['district_index']==d['native_district'])
   check(f"native camp matches authored{d['ranger_name']} silhouette",exact_index_shape(crop,Image.open(ROOT/'art/out'/art['frames'][0])))
   h['press']('down');check('local notes opens',h['screen']()==17)
   name=''.join(chr(h['pb'].memory[0x9800+i]+32) for i in range(20)).strip();check('actual screen name pairs with portrait',name==d['ranger_name'])
   image(f"camp-name-{d['district_id']}");h['press']('b');h['press']('b')
   results['rangers'].append({'district_id':d['district_id'],'rendered_name':name,'portrait_crop_sha256':digest,'native_shape_matches_authored':True})
  if not args.probe_13:check('all16 native camp crops unique',len(hashes)==16)
  saved={}
  cases=[(13,3,0)] if args.probe_13 else [(13,3,0),(5,4,1),(61,4,0),(73,4,0)]
  for sid,distance,phase in cases:
   if '_rf_forecast_phase ' in h['noi']:h['forecast_to'](phase,{13:13,5:2,61:11,73:0}[sid])
   saved[sid]=photograph(sid,distance,phase)
  # Explicit input save; cold boot reads actual emulator-emitted cartridge SRAM.
  h['open_camp']();check('save physical camp reached',h['screen']()==9);h['pb'].stop()
  sram=Path(str(path)+'.ram').read_bytes();(OUT/'input-earned-visual-save.ram').write_bytes(sram)
  boot()
  for row in results['photos']:
   sid=row['species_id'];im=album(sid,f'species-{sid:03d}-cold-album')
   check(f'cold boot preserves photo pose{sid}',snapshot_byte(sid)==row['snapshot_byte'])
   check(f'cold boot preserves exact album pixels{sid}',picture_bytes(im)==picture_bytes(saved[sid]))
   row['cold_album_exact_match']=True
  h['pb'].stop()
 results['functional_status']='pass'
 check('all native visual regressions including magenta and camera-album identity pass',not results['visual_blockers'])
 results['status']='pass'
except Exception as exc:
 results['status']='needs_visual_revision' if results['visual_blockers'] else 'fail';results['failure']=str(exc)
 try:image('first-visual-failure');h['pb'].stop(save=False)
 except Exception:pass
finally:
 results['assertions']=len(h['checks']);results['checks']=h['checks'];results['inputs']=h['inputs'];results['frames']=h['frames'];results['native_rom_unchanged']=hashlib.sha256(ROM.read_bytes()).hexdigest()==sha
 (OUT/'acceptance.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({k:results[k] for k in ('status','rom_sha256','assertions','frames')},indent=2))
 if results['status']!='pass':print(results.get('failure','Observed visual blocker; see acceptance.json'));sys.exit(1)
