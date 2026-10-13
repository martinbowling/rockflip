"""Actual controller-route water animation and rendering isolation for every wet map.

No RAM/VRAM/register writes, seeded progression or emulator states. Screen pixels
and OAM readbacks are observations. Exact ROM hash is required to bind evidence.
"""
from pathlib import Path
import argparse,json,hashlib,tempfile,shutil,sys,re
ROOT=Path(__file__).resolve().parents[1];ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);args=p.parse_args()
OUT=ROOT/'output/qa/native-visual/water';OUT.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha,'ROM differs from requested frozen artifact'
source=(ROOT/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0]
h={'__file__':str(ROOT/'tests/production_playtest.py')};exec(compile(source,'water_navigation_helpers','exec'),h)
h['OUT']=OUT;h['checks']=[];h['inputs']=[];h['frames']=0
wet=[m for m in h['world'].values() if any('W' in row for row in m['terrain'])];assert len(wet)==106
report={'status':'running','rom_sha256':sha,'wet_maps_expected':106,'samples_per_map':33,'frames_per_sample':3,'sample_span_frames':96,'progress_method':'actual normal travel/rest/controller inputs; no memory or bank writes','maps':[],'pending':['Human motion/pacing review','Physical Chromatic display acceptance']}
def hashbytes(data):return hashlib.sha256(data).hexdigest()
def check(label,ok):h['check'](label,ok)
try:
 with tempfile.TemporaryDirectory(prefix='rockflip-water-controller-') as tmp:
  path=Path(tmp)/ROM.name;shutil.copy2(ROM,path);h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();check('real title enters hike',h['screen']()==2)
  for m in wet:
   mid=m['id'];h['travel'](mid);h['rest_to'](0);h['tick'](24);check(f'actual water map{mid} day arrival',h['value'](1)==mid and h['value'](4)==0 and h['screen']()==2)
   # Full160x144 image: exclude exactly authored W16x16 cells at gameplay y16.
   positions=[(x,y) for y,row in enumerate(m['terrain']) for x,c in enumerate(row) if c=='W']
   water={ (16*x+dx,16+16*y+dy) for x,y in positions for dx in range(16) for dy in range(16)}
   camp=m.get('camp');camp_pixels=set()
   if camp:camp_pixels={(camp[0]*16+dx,8+camp[1]*16+dy) for dx in range(16) for dy in range(24)}
   allpos=[(x,y) for y in range(144) for x in range(160)];nonwater=[xy for xy in allpos if xy not in water and xy not in camp_pixels];water=sorted(water)
   legacy_water=mid==1 and m.get('art_style')=='desert'
   if legacy_water:
    c=(ROOT/'native/plugins/rockflip/engine/src/rockflip_art.c').read_text();start=80;length=256;array_names=['rf_water_0','rf_water_1']
   else:
    c=(ROOT/f'native/plugins/rockflip/engine/src/rf_map_art_{mid:04d}.c').read_text();start=int(re.search(r'set_bkg_data\((\d+),4,\(frame&1\)',c)[1]);length=64;array_names=['water_frame0','water_frame1']
   expected=[bytes(int(v) for v in re.search(name+r'\[\]\s*=\s*\{([^}]+)',c)[1].split(',')) for name in array_names]
   vram_addr=0x9000+(start if start<128 else start-256)*16
   landhashes=set();waterhashes=set();oamhashes=set();vram_outside=set();bank0=set();native_pattern_frames=set();transitional_pattern_samples=0;colors=[];samples=[]
   for n in range(33):
    if n:h['tick'](3)
    im=h['pb'].screen.image.convert('RGB');land=bytes(v for xy in nonwater for v in im.getpixel(xy));sea=bytes(v for xy in water for v in im.getpixel(xy))
    pattern=bytes(h['pb'].memory[1,vram_addr:vram_addr+length]);
    # A video-frame boundary may pause the CPU midway through set_bkg_data.
    # Transitional bytes must still come only from the two exact authored
    # patterns, and both complete patterns must appear in the96-frame window.
    valid=all(v==a or v==b for v,a,b in zip(pattern,*expected))
    if not valid:report['pattern_failure']={'map_id':mid,'sample':n,'address':vram_addr,'length':length,'actual':pattern.hex(),'expected':[e.hex() for e in expected]}
    check(f'map{mid} sampled native bytes belong only to source frame0/1',valid)
    if pattern in expected:native_pattern_frames.add(expected.index(pattern))
    else:transitional_pattern_samples+=1
    vram=bytes(h['pb'].memory[1,0x8000:0x9800]);at=vram_addr-0x8000
    vram_outside.add(hashbytes(vram[:at]+vram[at+length:]));v0=bytes(h['pb'].memory[0,0x8000:0x9800]);bank0.add(hashbytes(v0[:0xe00]+v0[0xe60:] if camp else v0))
    wh=hashbytes(sea);waterhashes.add(wh);landhashes.add(hashbytes(land));oamhashes.add(hashbytes(bytes(h['pb'].memory[0xfe00:0xfea0])))
    if wh not in samples:
     samples.append(wh);im.save(OUT/f'map-{mid:04d}-water-variant{len(samples)-1}.png')
    colors.append(sum(b>r and b>=g for r,g,b in (im.getpixel(xy) for xy in water))/len(water))
   check(f'map{mid} native source frame0 and1 both observed',native_pattern_frames=={0,1})
   check(f'map{mid} only reserved water span and independently tested camp frame span change',len(vram_outside)==1 and len(bank0)==1)
   check(f'map{mid} native water visibly animates',len(waterhashes)>1)
   check(f'map{mid} nonwater terrain UI/player pixels remain stable',len(landhashes)==1)
   check(f'map{mid} water updater preserves actual OAM',len(oamhashes)==1)
   check(f'map{mid} water remains visibly blue',min(colors)>.45)
   report['maps'].append({'map_id':mid,'district_id':m['district_id'],'native_swap_bank':1,'native_swap_bytes':length,'native_pattern_start':start,'native_source_frames_observed':sorted(native_pattern_frames),'transitional_pattern_samples':transitional_pattern_samples,'outside_bank1_pattern_variants':len(vram_outside),'bank0_pattern_variants':len(bank0),'excluded_camp_pattern_bytes':96 if camp else 0,'excluded_camp_pixels':len(camp_pixels),'water_metatiles':len(positions),'water_variants':len(waterhashes),'nonwater_variants':len(landhashes),'oam_variants':len(oamhashes),'water_blue_min_fraction':min(colors),'native_water_palette_expected':4 if legacy_water else 3,'water_frame_hashes':sorted(waterhashes),'nonwater_sha256':next(iter(landhashes))})
  h['pb'].stop();check('all106 wetmaps verified via controller',len(report['maps'])==106)
 report['status']='pass'
except Exception as exc:
 report['status']='fail';report['failure']=str(exc)
 try:h['pb'].screen.image.save(OUT/'first-failure.png');h['pb'].stop(save=False)
 except Exception:pass
finally:
 report['assertions']=len(h['checks']);report['checks']=h['checks'];report['inputs']=h['inputs'];report['frames']=h['frames'];report['native_rom_unchanged']=hashlib.sha256(ROM.read_bytes()).hexdigest()==sha
 (OUT/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','rom_sha256','assertions','frames']},indent=2))
 if report['status']!='pass':print(report.get('failure'));sys.exit(1)
