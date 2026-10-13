"""Actualnative241-map art/landmark audit usingcontroller travel andgenuineSRAM.
ObservesVRAM/OAM/RGB, never writes progress or video registers. Sourcequadpixels
must matchcartridgeBG patterns; visibleRGB must preserve authoredindices.
"""
from pathlib import Path
import argparse,json,hashlib,shutil,tempfile,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc';OUT=ROOT/'output/qa/native-landmarks';OUT.mkdir(parents=True,exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);p.add_argument('--full-save',type=Path,default=ROOT/'output/qa/controller-earned-151-c66c.ram');args=p.parse_args();sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha
source=(ROOT/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0];h={'__file__':str(ROOT/'tests/production_playtest.py')};exec(compile(source,'landmark_navigation','exec'),h);h['OUT']=OUT;h['checks']=[];h['inputs']=[];h['frames']=0
meta=json.loads((ROOT/'art/out/world-art-manifest.json').read_text());result={'status':'running','rom_sha256':sha,'progress_method':'genuinecontroller-earnedSRAM+coldboot+actuallegaltravel','memory_writes':False,'fixture_sha256':hashlib.sha256(args.full_save.read_bytes()).hexdigest(),'maps':[],'pending':['Humanregionalrecognizability/leveldesign/readability/pacing','PhysicalChromaticdisplay']}
def check(name,ok):h['check'](name,ok)
def tilebytes(im):
 r=[]
 for y in range(8):
  lo=hi=0
  for x in range(8):v=im.getpixel((x,y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
  r.extend((lo,hi))
 return bytes(r)
def oam_pixels():
 pb=h['pb'];height=16 if pb.memory[0xFF40]&4 else 8;rects=[]
 for i in range(40):
  y,x=pb.memory[0xFE00+i*4]-16,pb.memory[0xFE01+i*4]-8
  if y<144 and y+height>0 and x<160 and x+8>0:rects.append((x,y,x+8,y+height))
 return rects

def audit(mid):
 m=h['world'][mid];h['travel'](mid);h['tick'](8);check('actualmapentered',h['screen']()==2 and h['value'](1)==mid);pb=h['pb'];im=Image.open(ROOT/'art/out'/meta[str(mid)]['indices']);actual=pb.screen.image.copy();actual.save(OUT/f'map-{mid:04d}.png');attrs=meta[str(mid)]['attributes'];excluded=set()
 for s in h['sites']:
  if s['room_id']==mid:excluded.update((s['game_tile_x']*2+dx,s['game_tile_y']*2+dy) for dy in (0,1) for dx in (0,1))
 if m.get('camp'):
  cx,cy=m['camp'];excluded.update((cx*2+dx,cy*2+dy) for dy in (-1,0,1) for dx in (0,1))
 for edge,y in (('north',0),('south',13)):
  if m.get(edge) is not None:excluded.add((m[edge+'_x']*2,y))
 rgbmap={};oam=oam_pixels();checked=0;visible=0;waters=0
 for ty in range(14):
  for tx in range(20):
   if (tx,ty) in excluded:continue
   at=0x9800+(ty+2)*32+tx;attr=pb.memory[1,at];tile=pb.memory[0,at];check(f'map{mid}sourcepaletteattr{tx}/{ty}',attr==8|attrs[ty*20+tx])
   if m['terrain'][ty//2][tx//2]=='W':waters+=1;check('actualwaterfamily3',attr&7==3);continue
   expected=im.crop((tx*8,ty*8,tx*8+8,ty*8+8));bank=(attr>>3)&1;pattern=0x9000+(tile if tile<128 else tile-256)*16;raw=bytes(pb.memory[bank,pattern:pattern+16]);check(f'map{mid}actualVRAMmatchesnativeart{tx}/{ty}',raw==tilebytes(expected));checked+=1
   for yy in range(8):
    for xx in range(8):
     x,y=tx*8+xx,(ty+2)*8+yy
     if any(a<=x<c and b<=y<d for a,b,c,d in oam):continue
     key=(attr&7,expected.getpixel((xx,yy)));rgb=actual.getpixel((x,y))[:3]
     if key in rgbmap:check('visibleRGBpreservesauthoredindex',rgbmap[key]==rgb)
     else:rgbmap[key]=rgb
     visible+=1
 # Everyauthoredlandmark footprint fullychecked inVRAM; OAMmayoccluderasterbutnotBGdata.
 for field,w,hh in [('landmark_primary',4,6),('landmark_secondary',4,4)]:
  mark=m.get(field)
  if mark:check('plannedfullsizelandmarknotmaskedbyinteractiveoverlay',all((mark['x']*2+x,mark['y']*2+y) not in excluded for y in range(hh) for x in range(w)))
 result['maps'].append({'id':mid,'district':m['district_id'],'hero32x48':bool(m.get('landmark_primary')),'secondary32x32':bool(m.get('landmark_secondary')),'native_nonwater_quads_exact':checked,'native_visible_pixels_index_consistent':visible,'water_quads':waters,'image_sha256':hashlib.sha256(actual.tobytes()).hexdigest()})
try:
 with tempfile.TemporaryDirectory(prefix='rockflip-native-landmark-') as tmp:
  path=Path(tmp)/ROM.name;shutil.copy2(ROM,path);shutil.copy2(args.full_save,Path(str(path)+'.ram'));h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();check('actualearned151retained',all(h['best'](s)>0 for s in range(151)))
  h['forecast_to'](0,0)
  for mid in sorted(h['world']):audit(mid)
  check('all241actualcontrollerrooms',len(result['maps'])==241);check('all80actualfullsizeheroes',sum(r['hero32x48'] for r in result['maps'])==80);check('all241actualfullsizesecondaries',sum(r['secondary32x32'] for r in result['maps'])==241);h['pb'].stop();result['status']='pass'
except Exception as exc:
 result['status']='fail';result['failure']=str(exc)
 try:h['pb'].screen.image.save(OUT/'first-failure.png');h['pb'].stop(save=False)
 except Exception:pass
finally:
 result['assertions']=len(h['checks']);result['checks']=h['checks'];result['inputs']=h['inputs'];result['frames']=h['frames'];result['native_ROM_unchanged']=hashlib.sha256(ROM.read_bytes()).hexdigest()==sha;(OUT/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','rom_sha256','assertions','frames']},indent=2))
 if result['status']!='pass':print(result.get('failure'));sys.exit(1)
