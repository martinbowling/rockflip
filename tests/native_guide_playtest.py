"""Controller-only native field-guide content/filter/origin/seen/cold acceptance.
Requires the exact completedROM. Optional fixtures must be input-earnedSRAM;
never constructs photo/quest bytes or injects progress into emulator memory.
"""
from pathlib import Path
import argparse,json,hashlib,shutil,tempfile,sys
ROOT=Path(__file__).resolve().parents[1];ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);p.add_argument('--full-save',type=Path);p.add_argument('--challenge-save',type=Path,default=ROOT/'output/qa/challenge-native/completed-challenges.ram');args=p.parse_args()
OUT=ROOT/'output/qa/guide-native';OUT.mkdir(parents=True,exist_ok=True);sha=hashlib.sha256(ROM.read_bytes()).hexdigest();assert sha==args.expected_sha,'Need frozen exactguideROM'
source=(ROOT/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0];h={'__file__':str(ROOT/'tests/production_playtest.py')};exec(compile(source,'guide_navigation_helpers','exec'),h);h['OUT']=OUT;h['checks']=[];h['inputs']=[];h['frames']=0
content=json.loads((ROOT/'output/qa/guide-source/guide-content.json').read_text())['records'];report={'status':'running','rom_sha256':sha,'controller_progress_only':True,'memory_writes':False,'checks_scope':[],'fixtures':[],'pending':['Human editorial/readability/fun','Physical Chromatic display']}
def check(n,ok):h['check'](n,ok)
def text(row):return ''.join(chr(h['pb'].memory[0,0x9800+row*32+i]+32) for i in range(20)).rstrip()
def capture(n):h['pb'].screen.image.save(OUT/(n+'.png'))
def boot(path):
 h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180);h['enter_hike']();check('nativeboot trail',h['screen']()==2)
def visible_glyphs(row,line):
 for col,ch in enumerate(line):
  if ch==' ':continue
  at=0x9800+row*32+col;tile=h['pb'].memory[0,at];attr=h['pb'].memory[1,at];bank=(attr>>3)&1
  glyph_at=0x9000+(tile if tile<128 else tile-256)*16
  raw=bytes(h['pb'].memory[bank,glyph_at:glyph_at+16])
  check(f'visiblefontglyph{ord(ch)}at{row}/{col}',any(raw))
  pixels=h['pb'].screen.image.crop((col*8,row*8,col*8+8,row*8+8)).convert('RGB')
  check('actualglyphrasterhasforegroundcontrast',len(set(pixels.get_flattened_data()))>1)
def row_check(label,row,line):
 check(label,text(row)==line);visible_glyphs(row,line)
def header(sid):
 r=content[sid]
 for i,line in enumerate(r['text'][0]):row_check(f'fullcommon{sid}row{i}',i,line)
 for i in range(len(r['text'][0]),2):check('commonemptyheaderrow',text(i)=='')
 for i,line in enumerate(r['text'][1]):row_check(f'fullscientific{sid}row{i}',i+2,line)
 for i in range(len(r['text'][1]),2):check('scientificemptyheaderrow',text(i+2)=='')
def select(sid):
 # OnlyALLfilter is used here; rightmovesone entry, never UP/DOWN olddelta1.
 for _ in range((sid-h['value'](14))%151):h['press']('right',65)
 check(f'controllerselects{sid}',h['value'](14)==sid)
def hidden():
 select(150)
 for key,screen in [('a',8),('start',10)]:
  h['press'](key);check('hiddenanonymousdetailopens',h['screen']()==screen)
  for _ in range(5):
   check('hiddenidentityscientificnotrendered',text(0)=='UNWRITTEN FIELD PAGE' and text(1)=='' and text(2)=='' and text(3)=='')
   alltext=' '.join(text(y) for y in range(18)).upper();check('hiddenwordsnotleaked',content[150]['common_name'].upper() not in alltext and content[150]['scientific_name'].upper() not in alltext)
   h['press']('select')
  h['press']('b');check('hiddenreturnsguide',h['screen']()==7)
 capture('fresh-hidden-allpaths')
def filter_checks():
 best=[h['best'](s) for s in range(151)];flags=list(h['pb'].memory[h['RF']+h['offset'](19):h['RF']+h['offset'](19)+1000]);district=int(h['world'][h['value'](1)]['district_id'][1:])-1
 for mode in range(5):
  expected=[s for s in range(151) if mode==0 or mode==1 and not best[s] or mode==2 and (best[s] or any(flags[i]&2 for i in content[s]['spot_ids_for_seen'])) or mode==3 and best[s] or mode==4 and (s!=150 or best[150]) and content[s]['region_mask']&(1<<district)]
  rendered=text(0)[16:19];check(f'filter{mode}exactcountD{district+1}',rendered==f'{len(expected):03}')
  if not expected:
   check('nomatchmessagevisible',text(6)=='NO MATCHING PAGES.');old=h['value'](14)
   for key in ['a','start','right','down']:h['press'](key);check('nomatchinputboundedstaysgrid',h['screen']()==7 and h['value'](14)==old)
  else:
   check('selectedbelongsfilter',h['value'](14) in expected)
   for _ in range(min(len(expected)+1,8)):
    old=h['value'](14);at=expected.index(old);h['press']('right',65);check('nextfilterentrycorrect',h['value'](14)==expected[(at+1)%len(expected)])
   old=h['value'](14);at=expected.index(old);h['press']('down',65);check('downadvancessixmatches',h['value'](14)==expected[(at+6)%len(expected)])
  h['press']('select',100)
 check('fivefiltercyclebackALL',text(1)=='ALL')
def headers_and_pages(count):
 for sid in range(count):
  select(sid);h['press']('a');check('factsdetailopens',h['screen']()==8);header(sid)
  for i,line in enumerate(content[sid]['text'][2]):row_check(f'facts{sid}line{i}',12+i,line)
  for kind,start in [(3,5),(4,5),(6,6)]:
   h['press']('select');header(sid)
   for i,line in enumerate(content[sid]['text'][kind]):row_check(f'pagekind{kind}species{sid}line{i}',start+i,line)
   if kind==4:
    for i,line in enumerate(content[sid]['text'][5]):row_check(f'gameavailability{sid}line{i}',12+i,line)
  h['press']('select');header(sid);check('weatherpageopens',text(4)=='WEATHER / SIGNS')
  weather=['RAINY NIGHT WALK.','FALL / WINTER / SPR.'] if sid==9 else ['WARM WET NIGHT.','SPRING / SUMMER.'] if sid in (24,118) else ['COOL WET NIGHT.','FALL / WINTER / SPR.'] if sid==124 else ['ALL FORECAST WINDOWS','CHOOSE TIME AT CAMP.']
  for i,line in enumerate(weather):row_check(f'reviewedweatherclue{sid}line{i}',6+i,line)
  row_check(f'weathereditorialfooter{sid}',10,'ON THESE GAME HIKES,')
  row_check(f'weatheractivityfooter{sid}',11,'ACTIVITY CAN VARY.')
  h['press']('select');header(sid);check('fivedetailpageswraptofacts',h['screen']()==8)
  # B resetsgrid; page0 will reset onA nextspecies.
  if sid in (0,60,95,126,150):capture(f'guide-fullname-{sid:03d}')
  h['press']('b');check('detailreturnsguidegrid',h['screen']()==7)
 report['checks_scope'].append(f'{count}completecommon/scientific/fact/habitat/range/time/care/weatherpages throughcontroller')
def open_from(origin):
 if origin==9:h['open_camp']();h['press']('select')
 elif origin==25:
  # Routeawayfromcamp;STARTthenfieldpackatnonadjacentfictionalgamecell.
  for y in range(7):
   done=False
   for x in range(10):
    m=h['world'][h['value'](1)];camp=m['camp']
    if h['blocked'](m['id'],x,y) or camp and abs(x-camp[0])+abs(y-camp[1])<=1:continue
    try:h['walk'](x,y)
    except AssertionError:continue
    h['press']('start');check('noncampopensfieldpack',h['screen']()==25);h['press']('select');done=True;break
   if done:break
  else:raise AssertionError('Cannotreachfieldpackcell')
 else:h['press']('select')
 check('guideoriginopens',h['screen']()==7);h['press']('b');check(f'Breturnstoorigin{origin}',h['screen']()==origin)
 if origin!=2:h['press']('b');check('originmenureturnstotrail',h['screen']()==2)
def seen_rest_cold(path):
 site=next(s for s in h['sites'] if s['species_id']==5 and s['room_id']==0);h['travel'](0);h['rest_to'](1);h['face'](site);h['press']('a',100)
 check('actualencounterwithoutphoto',h['screen']()==3 and h['value'](6)==5 and h['best'](5)==0);h['press']('b');h['press']('b');h['press']('select');h['press']('select');h['press']('select');check('seenfilterselectsrealencounter',text(1)=='SEEN' and h['value'](14)==5);h['press']('b')
 h['rest_to'](2);h['press']('select');h['press']('select');h['press']('select');check('seenpersistsafteractualrest',text(1)=='SEEN' and h['value'](14)==5);h['press']('b');h['open_camp']();h['pb'].stop();sram=Path(str(path)+'.ram').read_bytes();(OUT/'input-earned-seen-without-photo.ram').write_bytes(sram)
 boot(path);check('coldseenstillnotphotographed',h['best'](5)==0);h['press']('select');h['press']('select');h['press']('select');check('seenpersistscoldfromrealSRAM',text(1)=='SEEN' and h['value'](14)==5);h['press']('b')
try:
 with tempfile.TemporaryDirectory(prefix='rockflip-guide-controller-') as tmp:
  path=Path(tmp)/ROM.name;shutil.copy2(ROM,path);boot(path)
  for origin in (2,9,25):open_from(origin)
  h['press']('select');filter_checks();hidden();headers_and_pages(150);h['press']('b')
  for d in range(16):
   mid=next(m['id'] for m in h['world'].values() if m['district_id']==f'D{d+1:02d}' and not m.get('hidden'));h['travel'](mid);h['press']('select');filter_checks();h['press']('b')
  seen_rest_cold(path);h['pb'].stop()
  if args.challenge_save.exists():
   shutil.copy2(args.challenge_save,Path(str(path)+'.ram'));report['fixtures'].append({'kind':'genuineinputearnedchallenge','path':str(args.challenge_save),'sha256':hashlib.sha256(args.challenge_save.read_bytes()).hexdigest()});boot(path);h['press']('select');filter_checks();h['press']('b');h['pb'].stop()
  if args.full_save:
   shutil.copy2(args.full_save,Path(str(path)+'.ram'));report['fixtures'].append({'kind':'genuineinputearned151completion','path':str(args.full_save),'sha256':hashlib.sha256(args.full_save.read_bytes()).hexdigest()});boot(path);check('genuineall151photosrestored',all(h['best'](s)>0 for s in range(151)));h['press']('select');headers_and_pages(151);h['press']('b');h['pb'].stop()
  else:report['pending'].append('Hidden150actualphotoidentity/full151SRAM acceptance pending genuinefullworld fixture')
 report['status']='pass'
except Exception as exc:
 report['status']='fail';report['failure']=str(exc)
 try:capture('first-guide-failure');h['pb'].stop(save=False)
 except Exception:pass
finally:
 report['assertions']=len(h['checks']);report['checks']=h['checks'];report['inputs']=h['inputs'];report['frames']=h['frames'];report['native_ROM_unchanged']=hashlib.sha256(ROM.read_bytes()).hexdigest()==sha;(OUT/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','rom_sha256','assertions','frames']},indent=2))
 if report['status']!='pass':print(report.get('failure'));sys.exit(1)
