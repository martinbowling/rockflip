"""Actual controller clue/HUD/icon regression; never writes gameplay/videoRAM.
Run only on the merged candidate, exactROM+NOI. Optionalhidden fixture must be
controller-earned150/unphotographed150 SRAM, never fabricated progress.
"""
from pathlib import Path
import argparse,ast,json,hashlib,shutil,tempfile,sys,re
from PIL import Image
D=Path(__file__).resolve().parent;ROOT=D.parent if D.name=='tests' else D.parents[1]
p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--expected-sha',required=True);p.add_argument('--hidden-save',type=Path);p.add_argument('--out',type=Path,default=ROOT/'output/qa/cover-hud-native');args=p.parse_args();ROM=args.rom.resolve();sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha;OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'tests/production_playtest.py';nodes=[]
for node in ast.parse(source.read_text()).body:
 if isinstance(node,ast.With):break
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='ROM'for t in node.targets):node.value=ast.Constant(str(ROM));node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[node.value],keywords=[])
 nodes.append(node)
h={'__file__':str(source)};exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'cover_navigation','exec'),h);h['OUT']=OUT;h['checks']=[];h['inputs']=[];h['frames']=0
assert re.search(r'DEF _rf_clue_hud ',h['noi']),'Merged clue API not in requested ROM';assert sum(s['interaction_type']==0 for s in h['sites'])==14,'Canonical site14-cover candidate not integrated'
DIR=h['symbol']('rf_dir');MOVE=h['symbol']('rf_moving');RF=h['RF'];SIZE=2544
closed={0:'A:LIFT B:LEAVE',1:'A:PEEK B:LEAVE',2:'A:LOOK B:LEAVE',3:'A:LOOK SAND B:LEAVE',4:'A:LOOK B:LEAVE',5:'A:ROCK B:LEAVE',6:'A:PEEK B:LEAVE',7:'A:WATCH B:LEAVE',8:'A:WATCH B:LEAVE',9:'A:LOOK B:LEAVE'}
font=Image.open(ROOT/'art/out/field_font.png');pal=json.loads((ROOT/'art/out/palettes.json').read_text());sheet=next(k for k,v in pal['sheet_order'].items()if k.startswith('tiles_')and'tracks'in v);idx=pal['sheet_order'][sheet].index('tracks');sand=Image.open(ROOT/'art/out'/(sheet+'.png')).crop((idx*16,0,idx*16+16,16))
report={'status':'running','rom_sha256':sha,'memory_writes':False,'video_register_writes':False,'controller_only':True,'cases':[],'obj_occluded_hint_pixels':0,'hidden_prephoto_fixture_tested':False,'source_bindings':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [source,ROOT/'data/foundation_encounters.json',ROOT/'data/weather_species_policy.json',ROOT/'art/out/field_font.png',ROOT/'art/out'/ (sheet+'.png')]}}
def check(n,ok):h['check'](n,ok)
def rawRF():return bytes(h['pb'].memory[RF:RF+SIZE])
def SRAM():return b''.join((bytes(h['pb'].memory[b,0xa000:0xbfff])+bytes([h['pb'].memory[b,0xbfff]]))for b in range(4))
def row(y):return ''.join(chr(h['pb'].memory[0,0x9800+y*32+x]+32)for x in range(20)).rstrip()
def region_rows():return [bytes(h['pb'].memory[b,0x9800+2*32:0x9800+16*32])for b in range(2)]
def row17():return [bytes(h['pb'].memory[b,0x9800+17*32:0x9800+17*32+20])for b in range(2)]
def pattern(im):
 out=[]
 for y in range(8):
  lo=hi=0
  for x in range(8):v=im.getpixel((x,y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
  out.extend((lo,hi))
 return bytes(out)
def glyphs(text):
 pb=h['pb'];shadow=h['symbol']('BkgPalette');colors=[h['word'](shadow+(28+i)*2)for i in range(4)]
 check('worldpalette7paper1duplicates0',colors[1]==colors[0]);rgb=lambda c:((c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3)
 for col,ch in enumerate(text):
  tile=ord(ch)-32;at=0x9800+16*32+col;check('hintglyphbankpalette7',pb.memory[0,at]==tile and pb.memory[1,at]==135)
  g=font.crop((tile%(font.width//8)*8,tile//(font.width//8)*8,tile%(font.width//8)*8+8,tile//(font.width//8)*8+8));g.putdata([1 if v==0 else v for v in g.get_flattened_data()]);addr=0x9000+tile*16;check('exactauthoredhintfontpattern',bytes(pb.memory[0,addr:addr+16])==pattern(g))
  crop=pb.screen.image.crop((col*8,128,col*8+8,136)).convert('RGB')
  for y in range(8):
   for x in range(8):
    want=rgb(colors[g.getpixel((x,y))]);actual=crop.getpixel((x,y))
    if actual!=want:report['glyph_failure']={'col':col,'char':ch,'pixel':[col*8+x,128+y],'actual':actual,'expected':want,'source_index':g.getpixel((x,y)),'palette_shadow':colors,'OAM':[list(pb.memory[0xfe00+i*4:0xfe00+i*4+4])for i in range(40)]}
    occluded=False
    if actual!=want and pb.memory[0xff40]&2:
     height=16 if pb.memory[0xff40]&4 else 8
     for j in range(40):
      oy=pb.memory[0xfe00+j*4]-16;ox=pb.memory[0xfe01+j*4]-8
      if ox<=col*8+x<ox+8 and oy<=128+y<oy+height:occluded=True;break
    if occluded:report['obj_occluded_hint_pixels']+=1
    check('visiblehintglyphpixelsmatchsourcepalette',actual==want)
 # A video-frame boundary may interrupt unrelated water/camp VRAM work.
 # API exit restoration is source-checked; final tile/attribute pixels above are observed.
def expect(text,label):check(label,row(16)==text);glyphs(text)
def current_site():
 x,y=h['value'](2),h['value'](3);direction=h['pb'].memory[DIR];dx,dy={0:(0,1),1:(0,-1),2:(-1,0),3:(1,0)}[direction];x+=dx;y+=dy;m=h['world'][h['value'](1)]
 if m.get('camp')==[x,y]:return 'camp'
 return next((s for s in h['sites']if s['room_id']==m['id']and(s['game_tile_x'],s['game_tile_y'])==(x,y)),None)
def flag(s):return h['pb'].memory[RF+h['offset'](19)+s['spot_id']]
def expected():
 s=current_site()
 if s=='camp':return'A:TALK B:LEAVE'
 if s is None:return'A:LOOK B:LEAVE'
 if s['interaction_type']in(0,5)and flag(s)&1:return'B:REPLACE THE ROCK'
 return closed[s['interaction_type']]
def refresh(label):expect(expected(),label)
def face_key(s,key):
 dx,dy=h['DIRS'][key];nx,ny=s['game_tile_x']-dx,s['game_tile_y']-dy
 if not(0<=nx<10 and 0<=ny<7)or h['blocked'](s['room_id'],nx,ny):return False
 h['walk'](nx,ny);before=(h['value'](2),h['value'](3),h['value'](21));h['press'](key,30);check('blockedsitefacekeepspositionandsteps',before==(h['value'](2),h['value'](3),h['value'](21)));check('actualfrontspotisrequested',isinstance(current_site(),dict)and current_site()['spot_id']==s['spot_id']);refresh('blockedfacingrefreshescurrentclue');return True
def face(s):
 for key in h['DIRS']:
  if face_key(s,key):return
 raise AssertionError('No legal observation approach')
def leave_readonly(s=None,expected_terrain=None):
 h['tick'](12);check('leavebeginsstationaryworld',h['screen']()==2 and not h['pb'].memory[MOVE]);before=rawRF();ram=SRAM();terrain=region_rows()if expected_terrain is None else expected_terrain;guide=row17();h['press']('b',80)
 check('Bpeekentire2544RFunchanged',rawRF()==before);check('Bpeekall32KiBSRAMunchanged',SRAM()==ram);check('Bpeekterrainmapattrsunchanged'if expected_terrain is None else'BweatherNoticeRestoresExactPriorTerrainMapAttrs',region_rows()==terrain);check('Bpeekrow17unchanged',row17()==guide);check('Bpeekremainsworld',h['screen']()==2)
 want='NO OPEN ROCK HERE.'if s is None else'LEAVE COVER AS FOUND'if s['interaction_type']==6 else'LEAVE IT AS FOUND.';expect(want,'Bleaveexactnote')
def boot(path):
 h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();check('actualcoldorfreshhike',h['screen']()==2)
def icon(s,tile):
 pb=h['pb'];x,y=s['game_tile_x']*2,2+s['game_tile_y']*2
 for i in range(4):
  at=0x9800+(y+i//2)*32+x+i%2;check('actualsandiconmetatile13bank1palette0',pb.memory[0,at]==tile*4+i and pb.memory[1,at]==8);check('actualsandiconbitplanesmatch1xsource',bytes(pb.memory[1,0x9000+(tile*4+i)*16:0x9000+(tile*4+i)*16+16])==pattern(sand.crop((i%2*8,i//2*8,i%2*8+8,i//2*8+8))))
def open_wrongphase(s):
 h['travel'](s['room_id']);phase=next(p for p in range(3)if not(s['phase_mask']&(1<<p)));h['forecast_to'](phase,0);face(s);h['press']('a',150);check('wrongphasecoveropenwithoutencounter',h['screen']()==2 and flag(s)&1);expect('QUIET. B:REPLACE','emptycoverretainsexplicitrestorationhint');h['press']('select');check('openworldguideopens',h['screen']()==7);h['press']('b');refresh('worldreturnrestorationpriority');before=h['value'](13);old=flag(s);h['press']('b',300);check('wrongphasecovercanonicallyclosedonce',not(flag(s)&1)and flag(s)&4 and h['value'](13)==min(before+(not(old&4)),99));h['press']('b',80);check('repeatclosedcovernogain',h['value'](13)==min(before+(not(old&4)),99));report['cases'].append({'kind':'wrongphase_restore','site':s['spot_id'],'type':s['interaction_type']})
try:
 with tempfile.TemporaryDirectory(prefix='rockflip-clue-controller-')as temp:
  path=Path(temp)/'fresh.gbc';shutil.copy2(ROM,path);boot(path);refresh('freshcamppriority');h['press']('a');check('campAactuallytalks',h['screen']()==9);h['press']('b');refresh('campworldreturnclue')
  for typ in range(10):
   s=next(s for s in h['sites']if s['interaction_type']==typ);h['travel'](s['room_id']);face(s);check('closedtyperepresentative',not(flag(s)&1));before=region_rows();guide=row17();leave_readonly(s);check('afterBclosedcluedoesnotrepaintbody',before==region_rows()and guide==row17());h['press']('select');h['press']('b');refresh('guideworldreturncurrentfrontclue');report['cases'].append({'kind':'closed_hint_Breadonly','site':s['spot_id'],'type':typ})
  first=next(s for s in h['sites']if s['spot_id']==0);h['travel'](first['room_id']);faced=[]
  for key in h['DIRS']:
   if face_key(first,key):faced.append(key)
  check('allfouractualfacingdirections',set(faced)==set(h['DIRS']))
  # Actualmovement refreshes newlyfacedcell; no directmemory heading writes.
  mid=h['value'](1)
  for key,(dx,dy)in h['DIRS'].items():
   nx,ny=h['value'](2)+dx,h['value'](3)+dy
   if 0<=nx<10 and 0<=ny<7 and not h['blocked'](mid,nx,ny):h['press'](key,30);refresh('successfulsteprefreshesnewfrontclue');break
  else:raise AssertionError('No legal step for refreshcase')
  if current_site()is None:leave_readonly()
  for s in [s for s in h['sites']if s['interaction_type']==3]:h['travel'](s['room_id']);face(s);icon(s,13)
  check('all17authoredsandclueschecked',sum(s['interaction_type']==3 for s in h['sites'])==17)
  for typ in(0,5):open_wrongphase(next(s for s in h['sites']if s['interaction_type']==typ and s['phase_mask']!=7))
  # Genuineweatherdenial exists at waterpeek, not at currentlyunrestrictedrocks.
  wet=next(s for s in h['sites']if s['species_id']==9 and s['interaction_type']==7);h['travel'](wet['room_id']);h['forecast_to'](next(p for p in range(3)if wet['phase_mask']&(1<<p)),0);face(wet);pre_weather_terrain=region_rows();h['press']('a',150);check('weatherblockedpeekdoesnotopenrock',h['screen']()==2 and not(flag(wet)&1));expect('PLAN WEATHER AT CAMP','reviewedweatherdenial');leave_readonly(wet,expected_terrain=pre_weather_terrain)
  policy={r['species_id']:r for r in json.loads((ROOT/'data/weather_species_policy.json').read_text())['records']};unrestricted=all(policy[s['species_id']]['weather_mask']==15 and policy[s['species_id']]['season_mask']==15 for s in h['sites']if s['interaction_type']in(0,5));check('wrongweathercoverbranchnotauthored',unrestricted);report['wrongweather_open_cover']='not_controller_reachable_under_reviewed_currentall15masks; sourceguardonly, actualwaterpeekweatherdenialtested'
  h['press']('select')
  for _ in range((150-h['value'](14))%151):h['press']('right',40)
  h['press']('a',100);check('freshhiddenidentitystillmasked',h['best'](150)==0 and row(0)=='UNWRITTEN FIELD PAGE');h['pb'].screen.image.save(OUT/'fresh-hidden-guide.png');h['press']('b');h['press']('b');h['pb'].stop(save=False)
  if args.hidden_save:
   hidden=Path(temp)/'hidden.gbc';shutil.copy2(ROM,hidden);shutil.copy2(args.hidden_save,Path(str(hidden)+'.ram'));boot(hidden);check('genuineprephotohiddenfixture',h['best'](150)==0 and all(h['best'](s)>0 for s in range(150))and h['flags']()[31]&128);s=next(s for s in h['sites']if s['species_id']==150);h['travel'](s['room_id']);face(s);expect('A:PEEK B:LEAVE','hiddenfrontclueanonymous');leave_readonly(s);h['pb'].screen.image.save(OUT/'genuine-prephoto-hidden-clue.png');h['pb'].stop(save=False);report['hidden_prephoto_fixture_tested']=True;report['fixture_sha256']=hashlib.sha256(args.hidden_save.read_bytes()).hexdigest()
  else:report['hidden_world_scope']='awaitsgenuineprehidden150fixture; freshguideguardtestedonly'
  meta=json.loads((ROOT/'art/out/world-art-manifest.json').read_text());counts=[]
  for r in meta.values():
   im=Image.open(ROOT/'art/out'/r['indices']);n=lambda q:len({q.crop((x,y,x+8,y+8)).tobytes()for y in range(0,q.height,8)for x in range(0,q.width,8)});counts.append((n(im),n(im.crop((16,24,144,88)))))
  check('sourceworldcamera120_92budgetretained',max(x for x,y in counts)<=120 and max(y for x,y in counts)<=92);report['source_budget']={'world':max(x for x,y in counts),'camera':max(y for x,y in counts),'sand_sign_new_patterns':0}
 check('zeroOBJoccludedHUDpixels',report['obj_occluded_hint_pixels']==0)
 report['status']='pass'if report['hidden_prephoto_fixture_tested']else'partial_hidden_fixture_pending'
except Exception as exc:
 report['status']='fail';report['failure']=str(exc)
 try:h['pb'].screen.image.save(OUT/'first-failure.png');h['pb'].stop(save=False)
 except Exception:pass
finally:
 report.update({'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],'frames':h['frames'],'native_ROM_unchanged':hashlib.sha256(ROM.read_bytes()).hexdigest()==sha});(OUT/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','rom_sha256','assertions','frames']},indent=2))
 if report['status']=='fail':print(report['failure']);sys.exit(1)
