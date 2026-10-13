"""All151 actualstored-album portraits: sourcequadbytes+palette+visiblepixels.
Genuinecontroller-earnedcompleteSRAM only. No progress/RAM/video-register writes.
Exactsaved lens/distance/pose/aim/phase drive sourceexpectation; name/nonblank/hash
checks cannot substitute for every displayed animalquad and every visiblepixel.
"""
from pathlib import Path
import argparse,json,hashlib,shutil,tempfile,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);p.add_argument('--full-save',type=Path,required=True);args=p.parse_args();sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha
OUT=ROOT/'output/qa/native-saved-art';OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0];h={'__file__':str(ROOT/'tests/production_playtest.py')};exec(compile(source,'saved_art_navigation','exec'),h);h['OUT']=OUT;h['checks']=[];h['inputs']=[];h['frames']=0
manifest=json.loads((ROOT/'art/out/species-art-manifest.json').read_text());byid={a['species_id']:a for a in manifest.values()};report={'status':'running','rom_sha256':sha,'fixture_path':str(args.full_save),'fixture_sha256':hashlib.sha256(args.full_save.read_bytes()).hexdigest(),'controller_only':True,'progress_memory_writes':False,'video_register_writes':False,'species':[],'source_manifest_sha256':hashlib.sha256((ROOT/'art/out/species-art-manifest.json').read_bytes()).hexdigest(),'pending':['Independentanatomicalrecognitionandhumanappealreview','PhysicalChromaticdisplay']}
def check(name,ok):h['check'](name,ok)
def tilebytes(im):
 data=[]
 for y in range(8):
  lo=hi=0
  for x in range(8):v=im.getpixel((x,y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
  data.extend((lo,hi))
 return bytes(data)
def rgb555(c):return (c[0]>>3)|((c[1]>>3)<<5)|((c[2]>>3)<<10)
def rgb(v):return ((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3)
def observe(sid):
 pb=h['pb'];r=byid[sid];distance=pb.memory[h['RF']+h['offset'](16)+sid];aim=pb.memory[h['RF']+h['offset'](17)+sid];aim=aim-256 if aim>=128 else aim;phase=pb.memory[h['RF']+h['offset'](18)+sid];snap=pb.memory[h['RF']+2256+sid];small=distance==4 and not(snap&32);size=32 if small else 48;side=size//8;frame=(snap>>3)&1 if snap&128 else 0;x=(8 if small else 7)-aim;y=6 if small else 5
 if snap&128:x+=(snap&3)-1;y+=((snap>>2)&1)-1
 path=ROOT/'art/out'/r['frames32' if small else 'frames'][frame];expected=Image.open(path);check('savedsourceframecorrectdimensions',expected.size==(size,size));shadow=h['symbol']('BkgPalette');original=[h['word'](shadow+(20+i)*2) for i in range(4)];source_colors=[rgb555(c) for c in r['palette']]
 for i in (1,2,3):check(f'species{sid}compiledpalettebinding{i}',original[i]==source_colors[i])
 colors=source_colors[:]
 if phase==2 and sid not in (61,73):colors=[((v&31)*3//4)|((((v>>5)&31)*3//4)<<5)|(((((v>>10)&31)*3//4+3)&31)<<10) for v in colors]
 colors[0]=h['word'](shadow) # Actualstoredmap/phase/conditionbackgroundmatte.
 screen=pb.screen.image.copy();crop=screen.crop((x*8,y*8,x*8+size,y*8+size)).convert('RGB');check('bodyentirelyonscreen',0<=x and x+side<=20 and 0<=y and y+side<=18)
 for yy in range(side):
  for xx in range(side):
   at=0x9800+(y+yy)*32+x+xx;tile=pb.memory[0,at];attr=pb.memory[1,at];check(f'species{sid}animalquadpalettebank{xx}/{yy}',attr==13);check('expectedcontiguoustilelayout',tile==128+yy*side+xx);address=0x9000+(tile-256)*16;raw=bytes(pb.memory[1,address:address+16]);check(f'species{sid}exactsourcequad{xx}/{yy}',raw==tilebytes(expected.crop((xx*8,yy*8,xx*8+8,yy*8+8))))
 used=set()
 for yy in range(size):
  for xx in range(size):
   index=expected.getpixel((xx,yy));used.add(index);check(f'species{sid}actualRGBsourcepalette',crop.getpixel((xx,yy))==rgb(colors[index]))
 check('sourceanatomypixelsuseatleast3paletteentries',len(used)>=3)
 screen.save(OUT/f'species-{sid:03d}-album.png');crop.save(OUT/f'species-{sid:03d}-body-{size}px.png');report['species'].append({'id':sid,'scientific_name':r['canonical_scientific_name'],'art_id':r['art_id'],'stored_scale':size,'stored_frame':frame,'stored_phase':phase,'stored_snapshot':snap,'lens_override':bool(snap&32),'source_path':str(path.relative_to(ROOT)),'source_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_grid_sha256':hashlib.sha256(expected.tobytes()).hexdigest(),'actual_crop_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),'quad_count':side*side,'pixel_count':size*size,'actual_quadbytes_source_exact':True,'actual_palette_and_pixels_source_exact':True,'palette_display_RGB555':colors})
try:
 with tempfile.TemporaryDirectory(prefix='rockflip-151-native-art-') as tmp:
  path=Path(tmp)/ROM.name;shutil.copy2(ROM,path);shutil.copy2(args.full_save,Path(str(path)+'.ram'));h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();check('genuineearnedall151loaded',all(h['best'](sid)>0 for sid in range(151)));h['press']('select');check('actualguideopened',h['screen']()==7)
  for sid in range(151):
   for _ in range((sid-h['value'](14))%151):h['press']('right',40)
   check('normalcontrollernavigationselectsidentity',h['value'](14)==sid);h['press']('start',100);check('actualstoredalbumopened',h['screen']()==10);h['tick'](8);observe(sid);h['press']('b');check('albumreturnstoguide',h['screen']()==7)
  h['pb'].stop(save=False)
 for start in range(0,151,50):
  canvas=Image.new('RGB',(960,((len(report['species'][start:start+50])+9)//10)*110),(32,36,40));d=ImageDraw.Draw(canvas)
  for i,r in enumerate(report['species'][start:start+50]):
   picture=Image.open(OUT/f'species-{r["id"]:03d}-body-{r["stored_scale"]}px.png');picture=picture.resize((96,96),Image.Resampling.NEAREST);x=i%10*96;y=i//10*110;canvas.paste(picture,(x,y));d.text((x,y+97),f'{r["id"]:03} {r["stored_scale"]} F{r["stored_frame"]}',fill='white')
  canvas.save(OUT/f'actual151-contact-{start:03d}.png')
 report['status']='pass'
except Exception as exc:
 report['status']='fail';report['failure']=str(exc)
 try:h['pb'].screen.image.save(OUT/'first-failure.png');h['pb'].stop(save=False)
 except Exception:pass
finally:
 report['assertions']=len(h['checks']);report['checks']=h['checks'];report['inputs']=h['inputs'];report['frames']=h['frames'];report['native_ROM_unchanged']=hashlib.sha256(ROM.read_bytes()).hexdigest()==sha;(OUT/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','rom_sha256','assertions','frames']},indent=2))
 if report['status']!='pass':print(report['failure']);sys.exit(1)
