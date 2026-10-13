"""Candidate-only real controller font/priority/12pose/feet test. NoRAM writes."""
from pathlib import Path
import argparse,json,hashlib,shutil,tempfile
from contextlib import nullcontext
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parent if D.name=='tests' else D.parents[1];p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);p.add_argument('--out',type=Path);a=p.parse_args();ROM=R/'native/build/rom/RockFlip-Statewide.gbc';sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==a.expected_sha
O=a.out if a.out is not None else R/'output/qa/explorer-actions-native';O.mkdir(parents=True,exist_ok=True);h={'__file__':str(R/'tests/production_playtest.py')};exec(compile((R/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0],'navigation','exec'),h);h['OUT']=O;h['checks']=[];h['inputs']=[];h['frames']=0
font=Image.open(R/'art/out/field_font.png');sprite=Image.open(R/'art/out/player.png');names=json.loads((R/'art/out/palettes.json').read_text())['sheet_order']['player'];pose={}
for k,n in enumerate(names):
 im=Image.new('P',(16,32),0);im.paste(sprite.crop((k*16,0,k*16+16,24)),(0,0));pose.setdefault(im.tobytes(),[]).append(n)
actions=Image.open(R/'art/out/player_actions.png');action_names=json.loads((R/'art/out/player-actions.json').read_text())['order']
for k,n in enumerate(action_names):
 im=Image.new('P',(16,32),0);im.paste(actions.crop((k*16,0,k*16+16,24)),(0,0));pose.setdefault(im.tobytes(),[]).append(n)
sourcepal=[int(c['rgb555'],16)for c in json.loads((R/'art/out/palettes.json').read_text())['obj']['ranger']];native_to_source=[0,3,2,1]
pose_bottom={n:max(y for y in range(24)for x in range(16)if im[x+y*16])for im,ns in pose.items()for n in ns}
report={'status':'running','rom_sha256':sha,'controller_only':True,'RAM_video_register_writes':False,'poses':[],'rows':[]};seen=set();real_tick=h['tick']
def check(n,b):h['check'](n,b)
def sram():
 pb=h['pb'];return b''.join(bytes(pb.memory[b,0xa000:0xbfff])+bytes([pb.memory[b,0xbfff]])for b in range(4))
def tilebytes(im):
 b=[]
 for y in range(8):
  lo=hi=0
  for x in range(8):v=im.getpixel((x,y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
  b.extend((lo,hi))
 return bytes(b)
def objs():
 pb=h['pb'];return [tuple(pb.memory[0xfe00+j*4:0xfe00+j*4+4])for j in range(40)if 0<pb.memory[0xfe00+j*4]<160 and 0<pb.memory[0xfe01+j*4]<168]
def observe_pose(entries=None,palette_snapshot=None):
 pb=h['pb']
 if h['screen']()!=2 or not(pb.memory[0xff40]&2):return
 entries=objs()if entries is None else entries
 if len(entries)!=4:return
 left=min(e[1]-8 for e in entries);top=min(e[0]-16 for e in entries);im=Image.new('P',(16,32),0)
 for yy,xx,t,attr in entries:
  x0,y0=xx-8-left,yy-16-top
  for y in range(16):
   sy=15-y if attr&64 else y;addr=0x8000+(t&254)*16+(sy//8)*16+(sy%8)*2;lo=pb.memory[(attr>>3)&1,addr];hi=pb.memory[(attr>>3)&1,addr+1]
   for x in range(8):
    sx=7-x if attr&32 else x;v=((lo>>(7-sx))&1)|(((hi>>(7-sx))&1)<<1)
    if v and 0<=x0+x<16 and 0<=y0+y<32:im.putpixel((x0+x,y0+y),native_to_source[v])
 n=pose.get(im.tobytes())
 if n is None:
  report['unrecognized_native_pose']={'frame':h['frames'],'OAM':entries,'lower_padding_nonzero':sum(im.getpixel((x,y))!=0 for y in range(24,32)for x in range(16))};check('allObservedWorldOBJGridsMatchAnAuthoredPose',False)
 if n and not set(n)<=seen:
  check('nativeOBJLower8RowsEntirelyTransparent',all(im.getpixel((x,y))==0 for y in range(24,32)for x in range(16)))
  # A live OAM read can straddle a frame change. Credit a pose only when the
  # actual rendered nontransparent body also matches originalsource RGB.
  image=pb.screen.image.convert('RGB');shadow=h['symbol']('SprPalette');colors=palette_snapshot if palette_snapshot is not None else[h['word'](shadow+i*2)for i in range(4)]
  for native_index in(1,2,3):check('explorerImportedPaletteMatchesAuthoredIndex',colors[native_index]==sourcepal[native_to_source[native_index]])
  visual=True
  for yy in range(24):
   for xx in range(16):
    v=im.getpixel((xx,yy));sx,sy=left+xx,top+yy
    if v and 0<=sx<160 and 16<=sy<128:
     c=sourcepal[v];want=((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3)
     if image.getpixel((sx,sy))!=want:visual=False
  if visual:seen.update(n);n=n[0];im.putpalette(sprite.getpalette());im.info['transparency']=0;im.save(O/(n+'-source-index.png'));im.convert('RGBA').save(O/(n+'-decoded-OBJ-RGBA.png'));pb.screen.image.save(O/(n+'-actual-screen.png'))
 return n
def tick(n):
 for _ in range(n):
  previous=objs();shadow=h['symbol']('SprPalette');colors=[h['word'](shadow+i*2)for i in range(4)]
  real_tick(1);observe_pose(previous,colors)
h['tick']=tick
def fontcheck(world):
 pb=h['pb'];check('CGBpriorityenabledLCDCbit0',bool(pb.memory[0xff40]&1))
 for k in range(96):
  im=font.crop((k%(font.width//8)*8,k//(font.width//8)*8,k%(font.width//8)*8+8,k//(font.width//8)*8+8))
  if world:im.putdata([1 if v==0 else v for v in im.get_flattened_data()])
  addr=0x9000+k*16;check('same96slotexactworldormenuFont',bytes(pb.memory[0,addr:addr+16])==tilebytes(im))
 pal=h['symbol']('BkgPalette');c=[h['word'](pal+(28+i)*2)for i in range(4)];check('worldpaperduplicate_menuoriginal',c[1]==(c[0]if world else 23|(18<<5)|(12<<10)))
 if not world:return
 for row in [0,1,16,17]:
  for col in range(20):
   at=0x9800+row*32+col;k=pb.memory[0,at];check('HUDprioritypalette7bank0',pb.memory[1,at]==135);check('HUDonlyfontglyphIDs',k<96)
   g=font.crop((k%(font.width//8)*8,k//(font.width//8)*8,k%(font.width//8)*8+8,k//(font.width//8)*8+8));actual=pb.screen.image.crop((col*8,row*8,col*8+8,row*8+8)).convert('RGB')
   for y in range(8):
    for x in range(8):v=g.getpixel((x,y));v=1 if v==0 else v;cc=c[v];want=((cc&31)<<3,((cc>>5)&31)<<3,((cc>>10)&31)<<3);check('allHUDpixelsunoccludedIncludingBlanks',actual.getpixel((x,y))==want)
def feet(row):
 entries=objs();check('fourObjectsUnchanged',len(entries)==4);top=min(e[0]-16 for e in entries);check('nativeSpriteAnchorLogicalTile',top==8+16*row);n=observe_pose();check('lastAuthoredBootPixelWithinCell',n is not None and top+pose_bottom[n]<=31+16*row);check('OBJScanlineMaxTwo',max(sum(e[0]-16<=y<e[0]for e in entries)for y in range(144))==2)
temporary=tempfile.TemporaryDirectory(prefix='rockflip-hud-mask-')
try:
 with nullcontext(temporary.name)as tmp:
  rom=Path(tmp)/ROM.name;shutil.copy2(ROM,rom);h['pb']=h['PyBoy'](str(rom),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);fontcheck(False);h['enter_hike']();fontcheck(True)
  # Bidirectional long horizontal and vertical controller walks expose all3
  # native movement frames per facing; sourceleft is actualhardwareflip.
  for direction,(dx,dy)in h['DIRS'].items():
   found=False
   for m in h['world'].values():
    for y in range(7):
     for x in range(10):
      points=[(x+dx*i,y+dy*i)for i in range(4)]
      if all(0<=xx<10 and 0<=yy<7 and not h['blocked'](m['id'],xx,yy)for xx,yy in points):
       h['travel'](m['id']);h['walk'](x,y)
       for _ in range(3):h['press'](direction,24)
       found=True;break
     if found:break
    if found:break
   check('legalFourCellFacingRouteFound',found)
  check('all12StridePosesRetainedBeforeActions',set(names)<=seen)
  used=set()
  for direction,(dx,dy)in h['DIRS'].items():
   for action,types in [('lift',(0,)),('peek',(1,6))]:
    site=next(z for z in h['sites']if z['spot_id']not in used and z['interaction_type']in types and 0<=z['game_tile_x']-dx<10 and 0<=z['game_tile_y']-dy<7 and not h['blocked'](z['room_id'],z['game_tile_x']-dx,z['game_tile_y']-dy))
    used.add(site['spot_id']);h['travel'](site['room_id'])
    # Weather setup does not select an authored site's time window. Use the
    # ordinary camp forecast before requiring an actual encounter to open.
    if not site['phase_mask']&(1<<h['value'](4)):
     h['rest_to'](next(phase for phase in range(3)if site['phase_mask']&(1<<phase)))
    h['conditions_for_subject'](site['species_id']);h['walk'](site['game_tile_x']-dx,site['game_tile_y']-dy);h['press'](direction,24)
    before=sram();h['press']('a',0);check('LOOKdelayDoesNotCommitSRAM',sram()==before);check('LOOKdelayStillWorldUntilBothPoses',h['screen']()==2);h['tick'](20)
    check('deferredLOOKcompletedAfterBothSourcePoses',h['screen']()==3)
    # The screen flag changes before its blocking drawing/save completes.
    # Release input and allow that prior transaction to settle before measuring
    # the next camera action's independent no-save window.
    h['tick'](90)
    if action=='peek':
     before=sram();h['press']('a',0);check('cameraReadyDelayDoesNotCommitSRAM',sram()==before);check('cameraReadyStillWorldBeforeDetailedUI',h['screen']()==2)
     for _ in range(240):
      if h['screen']()==4:break
      h['tick'](1)
     check('cameraReadyCompletedIntoCamera',h['screen']()==4);h['tick'](90);h['press']('b')
    else:h['press']('b')
    check('normalReturnWorldAfterAction',h['screen']()==2)
    if action=='lift':h['press']('b',90)
    fontcheck(True)
  check('all24NativeInteractionPoseSourcePixelsActuallySeen',set(action_names)<=seen)
  check('all36AuthoredNativePosesActuallyRendered',set(names+action_names)<=seen)
  h['open_camp']();fontcheck(False);h['press']('b');fontcheck(True);report['status']='pass' 
except Exception as e:
 report['status']='fail';report['error']=str(e)
 if 'pb'in h:h['pb'].screen.image.save(O/'first-failure.png')
finally:
 if 'pb'in h:h['pb'].stop(save=False)
 temporary.cleanup()
 report.update(poses=sorted(seen),assertions=len(h['checks']),checks=h['checks'],inputs=h['inputs'],frames=h['frames']);(O/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','rom_sha256','assertions','frames','poses','rows']},indent=2))
if report['status']!='pass':raise SystemExit(1)
