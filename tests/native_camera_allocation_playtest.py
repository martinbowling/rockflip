"""Native split-camera-run proof onboth >32patternmaps, controllerphotos+cold.
Reusesrealphoto/pixel helpers; camera observer readsallloadedbank0 patterns
AFTERportraitload, provingthe portrait doesnotcorrupt latecamera tiles.
"""
from pathlib import Path
import json,argparse,hashlib,shutil,tempfile,sys
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);args=p.parse_args();ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc';sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha
OUT=ROOT/'output/qa/native-camera-allocation';OUT.mkdir(parents=True,exist_ok=True)
prefix=(ROOT/'tests/native_visual_acceptance.py').read_text().split('try:\n with tempfile.TemporaryDirectory',1)[0];v={'__file__':str(ROOT/'tests/native_visual_acceptance.py')};exec(compile(prefix,'photo_helpers','exec'),v);h=v['h'];h['checks']=[];h['inputs']=[];h['frames']=0;h['OUT']=OUT
from PIL import Image
meta=json.loads((ROOT/'art/out/world-art-manifest.json').read_text());observations=[];pictures=[]
def tilebytes(im):
 raw=[]
 for y in range(8):
  lo=hi=0
  for x in range(8):n=im.getpixel((x,y));lo|=(n&1)<<(7-x);hi|=((n>>1)&1)<<(7-x)
  raw.extend((lo,hi))
 return bytes(raw)
oldimage=v['image']
def image_observer(name):
 im=oldimage(name)
 if '-camera-' in name:
  mid=h['value'](1);index=Image.open(ROOT/'art/out'/meta[str(mid)]['indices']).crop((16,24,144,88));unique=[]
  for y in range(8):
   for x in range(16):
    b=tilebytes(index.crop((x*8,y*8,x*8+8,y*8+8)))
    if b not in unique:unique.append(b)
  v['check']('actualtestcameraexercisesmorethan32patterns',len(unique)>32)
  slots=list(range(96,128))+list(range(164,224))
  for n,b in enumerate(unique):
   slot=slots[n];address=0x9000+(slot if slot<128 else slot-256)*16
   v['check'](f'actualcamera{mid}pattern{slot}survivesportrait',bytes(h['pb'].memory[0,address:address+16])==b)
  reserved=set(range(0,96))|set(range(128,164))|set(range(224,234));v['check']('cameraallocationsnotreserved',not(set(slots[:len(unique)])&reserved))
  observations.append({'map':mid,'patterns':len(unique),'second_run':slots[32:len(unique)],'portrait_already_loaded':True,'all_camera_patterns_exact':True,'camera_image_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
 return im
v['image']=image_observer
try:
 with tempfile.TemporaryDirectory(prefix='rockflip-camera-bands-') as tmp:
  for mid,sid,phase,distance in [(6,10,0,4),(6,10,0,3),(62,51,2,4),(62,51,2,3)]:
   case=OUT/f'map{mid:03}-species{sid:03}-distance{distance}';case.mkdir(exist_ok=True);v['OUT']=case;path=Path(tmp)/f'case{mid}-{distance}.gbc';shutil.copy2(ROM,path)
   h['sites'].sort(key=lambda r:(r['room_id']!=mid,r['spot_id']))
   def boot():
    h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();v['check']('actualfreshorcoldhike',h['screen']()==2)
   boot();stored=v['photograph'](sid,distance,phase);snapshot=v['snapshot_byte'](sid);v['check']('bothcameraalbumexact',not v['results']['visual_blockers']);h['open_camp']();h['pb'].stop();shutil.copy2(Path(str(path)+'.ram'),case/'input-earned-photo.ram');boot();cold=v['album'](sid,'cold-album');v['check']('coldposepreserved',v['snapshot_byte'](sid)==snapshot);v['check']('coldpixelsidentical',v['picture_bytes'](cold)==v['picture_bytes'](stored));h['pb'].stop();pictures.append({'map':mid,'sid':sid,'phase':phase,'distance':distance,'scale':32 if distance==4 else 48,'camera_album_cold_exact':True})
 report={'status':'pass'}
except Exception as exc:
 report={'status':'fail','failure':str(exc)}
 try:h['pb'].screen.image.save(OUT/'first-failure.png');h['pb'].stop(save=False)
 except Exception:pass
finally:
 report.update({'rom_sha256':sha,'assertions':len(h['checks']),'checks':h['checks'],'frames':h['frames'],'inputs':h['inputs'],'camera_pattern_proofs':observations,'transactions':pictures,'memory_writes':False,'native_ROM_unchanged':hashlib.sha256(ROM.read_bytes()).hexdigest()==sha,'pending':['HumanLCDandfunreview','PhysicalChromatic']});(OUT/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','rom_sha256','assertions','frames']},indent=2))
 if report['status']!='pass':print(report['failure']);sys.exit(1)
