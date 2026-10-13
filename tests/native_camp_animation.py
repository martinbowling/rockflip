"""Controller-earned sixteen district camp idle animations and cold persistence.

Read VRAM banks directly via PyBoy; never write VBK/gameplay RAM. Camera/menus
do not run idle timers. Only authored camp96bytes/pixels and W patterns may vary.
"""
from pathlib import Path
import ast,json,hashlib,tempfile,shutil,re
HERE=Path(__file__).resolve().parent;shared=HERE/'production_playtest.py'
tree=ast.parse(shared.read_text());prefix=[]
for node in tree.body:
 if isinstance(node,ast.With):break
 prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(shared),'exec'),globals())
OUT=ROOT/'output/qa/camp-animation-native';OUT.mkdir(parents=True,exist_ok=True)
if not re.search(r'DEF _rf_camp_pose ',noi):raise SystemExit('Camp idle integration not in selected ROM; rebuild first.')
POSE=symbol('rf_camp_pose');CLOCK=symbol('rf_camp_clock');SYSTEM_CLOCK=symbol('sys_time');reports=[];peak_objects=peak_scanline=0
def digest(data):return hashlib.sha256(bytes(data)).hexdigest()
def carray(path,name):return bytes(int(v)for v in re.search(name+r'\[\]\s*=\s*\{([^}]+)',path.read_text())[1].split(','))
def water_span(mid):
 m=world[mid]
 if not any('W'in row for row in m['terrain']):return None
 if mid==1:return 0x9000+(80*16),256
 path=ROOT/f'native/plugins/rockflip/engine/src/rf_map_art_{mid:04d}.c'
 start=int(re.search(r'set_bkg_data\((\d+),4,\(frame&1\)',path.read_text())[1]);return 0x9000+(start if start<128 else start-256)*16,64
def oam_budget():
 global peak_objects,peak_scanline
 raw=bytes(pb.memory[0xFE00:0xFEA0]);height=16 if pb.memory[0xFF40]&4 else 8
 visible=[(raw[i]-16,raw[i+1]-8)for i in range(0,160,4)if 0<raw[i]<160 and 0<raw[i+1]<168]
 lines=[sum(y<=scan<y+height for y,x in visible)for scan in range(144)]
 peak_objects=max(peak_objects,len(visible));peak_scanline=max(peak_scanline,max(lines,default=0))
 check('camp actualOAM within40objects and10perscanline',len(visible)<=40 and max(lines,default=0)<=10)
 return raw
with tempfile.TemporaryDirectory(prefix='rockflip-camp-native-')as work:
 path=Path(work)/ROM.name;shutil.copy2(ROM,path)
 pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);enter_hike()
 for district in range(16):
  candidates=[m for m in world.values()if m['district_id']==f'D{district+1:02d}'and m['camp']is not None]
  m=next((m for m in candidates if any('W'in row for row in m['terrain'])),candidates[0]);mid=m['id'];travel(mid);rest_to(0)
  if value(1)!=mid:travel(mid)
  check('actualcampmap anddistrict reached',value(1)==mid and screen()==2)
  # Source-only directions3..11 are admitted by304 generator checks. Native
  # world exposes three grounded down poses, not twelve wandering directions.
  table=carray(ROOT/f'native/plugins/rockflip/engine/src/rf_ranger_{district//4}.c','sprites')
  expected=[table[((district%4)*12+i)*96:((district%4)*12+i+1)*96]for i in range(3)]
  check('allthree sourcecamp poses differ',len(set(expected))==3 and all(len(b)==96 for b in expected))
  camp={(16*m['camp'][0]+dx,8+16*m['camp'][1]+dy)for dx in range(16)for dy in range(24)}
  wet={(16*x+dx,16+16*y+dy)for y,row in enumerate(m['terrain'])for x,c in enumerate(row)if c=='W'for dx in range(16)for dy in range(16)}
  outside=[(x,y)for y in range(144)for x in range(160)if(x,y)not in camp and(x,y)not in wet]
  pixel_hashes=set();bank0outside=set();bank1outside=set();maps=set();oams=set();waterframes=set();seen=set();phases=[];transient=0;before_flags=flags();before_points=value(13);before_steps=value(21)
  water=water_span(mid)
  for i in range(151):
   if i:tick(3)
   pattern=bytes(pb.memory[0,0x8E00:0x8E60])
   check(f'district{district+1} camppattern bytes onlyauthored0/1/2',all(v in {a,b,c}for v,a,b,c in zip(pattern,*expected)))
   if pattern in expected:
    pose=expected.index(pattern)
    if pose not in seen:snapshot(f'district-{district+1:02d}-pose-{pose}')
    seen.add(pose)
   else:transient+=1
   phase=pb.memory[POSE]
   if not phases or phases[-1]!=phase:phases.append(phase)
   raw0=bytes(pb.memory[0,0x8000:0x9800]);bank0outside.add(digest(raw0[:0xE00]+raw0[0xE60:]))
   raw1=bytes(pb.memory[1,0x8000:0x9800])
   if water:
    start,length=water;at=start-0x8000;waterframes.add(digest(raw1[at:at+length]));raw1=raw1[:at]+raw1[at+length:]
   bank1outside.add(digest(raw1));maps.add(digest(bytes(pb.memory[0,0x9800:0x9C00])+bytes(pb.memory[1,0x9800:0x9C00])));oams.add(digest(oam_budget()))
   im=pb.screen.image.convert('RGB');pixel_hashes.add(digest(bytes(v for p in outside for v in im.getpixel(p))))
  check('allthree districtcamp sourceposes actuallyobserved',seen=={0,1,2})
  check('camp idle fourphase order wraps0/1/2/3',set(phases)=={0,1,2,3}and all(b==(a+1)%4 for a,b in zip(phases,phases[1:])))
  check('campframe updates preserveotherbank0patterns',len(bank0outside)==1)
  check('campframe updates preserveworld patternsoutsidewater',len(bank1outside)==1)
  check('campframe updates preservetilemaps attributes andOAM',len(maps)==1 and len(oams)==1)
  check('camp idle preservesnoncamp/nonwater pixels',len(pixel_hashes)==1)
  check('camp idle preservesprogresscareandcoordinates',flags()==before_flags and value(13)==before_points and value(21)==before_steps)
  if water:check('water continues duringcampidle',len(waterframes)>1)
  # Opening the actual station while an idle phase is nearits boundary must
  # produce one menu; menus freeze world-only pattern swapping.
  open_camp();check('actualstation opensonce duringidle',screen()==9)
  frozen=bytes(pb.memory[0,0x8E00:0x8E60]);tick(220)
  check('station doesnotanimate overworldcamppatterns',bytes(pb.memory[0,0x8E00:0x8E60])==frozen)
  press('b',150);check('station returns tosame districttrail',screen()==2 and world[value(1)]['district_id']==m['district_id'])
  # Time a real input to the next idle phase. The updater services animation
  # before camp input, so this catches lost or duplicated boundary presses.
  for _ in range(130):
   if ((word(SYSTEM_CLOCK)-word(CLOCK))&65535)>=95:break
   tick(1)
  prior_pose=pb.memory[POSE];press('start',150)
  check('boundary idle update and START produce one station',screen()==9 and pb.memory[POSE]==(prior_pose+1)%4)
  tick(120);check('held/released boundary input does not duplicate menu',screen()==9)
  press('b',150);check('boundary station return resumes normal hike',screen()==2)
  reports.append({'district':district+1,'map_id':mid,'poses_observed':sorted(seen),'phase_order':phases,'transitional_pattern_samples':transient,'bank0outside_variants':len(bank0outside),'bank1outside_variants':len(bank1outside),'outside_pixel_variants':len(pixel_hashes),'tilemap_variants':len(maps),'OAM_variants':len(oams),'water_pattern_variants':len(waterframes),'idle_window_frames':450})
 # Earn genuine photo/careprogress before coldboot; do not useempty-save proof.
 site=next(s for s in sites if s['spot_id']==0);travel(0);rest_to(1);face(site);press('a',150);check('coldproof actualencounter',screen()==3);press('a',150);tick(120);press('a',150);check('coldproof actualphoto',screen()==5 and best(5)>0);press('b',150);press('b',150);check('coldproof actualcare',value(13)>0)
 open_camp();saved={'best':best(5),'count':value(12),'points':value(13),'flags':flags(),'room':value(1)};pb.stop()
 pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
 check('coldboot restores earnedphoto/care/quest metadata',best(5)==saved['best']and value(12)==saved['count']and value(13)==saved['points']and flags()==saved['flags'])
 enter_hike();check('coldcontinue legalcampmap',screen()==2 and value(1)==saved['room'])
 cold_phases=set()
 for _ in range(140):tick(3);cold_phases.add(pb.memory[POSE])
 check('coldcontinue observes allfour naturalcampidle phases',cold_phases=={0,1,2,3});pb.stop()
report={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'frames':frames,'inputs':inputs,'districts':reports,'native_idle_source_poses':48,'all_direction_source_frames_native_observed':False,'peak_objects':peak_objects,'peak_scanline_objects':peak_scanline,'memory_writes':False,'loose_stone_animated':False,'human_or_physical_approved':False,'scope':'Actual16district three-source-pose camps, fourphaseidle,96bytebank0 isolation,watercontinuation,map/attrs/OAM/pixel isolation,stationinput/menu freeze,coldearnedphoto/care persistence. Directionframes3..11 andloose-stone motion are separatefuturegates.'}
(OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['result','assertions','frames','native_idle_source_poses','rom_sha256','peak_objects','peak_scanline_objects']},indent=2))
