"""Actual controller onboarding acceptance. Run only after root integration.
Fresh skip and all three pages are deliberate checks, never blind enter_hike.
"""
from pathlib import Path
import ast,sys
own_file=__file__;ROOT=Path(own_file).resolve().parents[1];source=ROOT/'tests/production_playtest.py';prefix=[]
for node in ast.parse(source.read_text()).body:
 if isinstance(node,ast.With):break
 prefix.append(node)
__file__=str(source);exec(compile(ast.Module(body=prefix,type_ignores=[]),str(source),'exec'),globals());__file__=own_file
OUT=ROOT/'output/qa/onboarding-native';OUT.mkdir(parents=True,exist_ok=True)
if not re.search(r'DEF _rf_welcome_page ',noi):raise SystemExit('Onboarding not in current ROM; rebuild matching ROM/NOI first.')
PAGE=symbol('rf_welcome_page');LOCK=symbol('rf_store_locked');SAVE=symbol('rf_save_ok');DIR=symbol('rf_dir')
portrait=bytes(int(v)for v in re.search(r'portraits\[\]=\{([^}]+)',(ROOT/'native/plugins/rockflip/engine/src/rf_ranger_0.c').read_text())[1].split(','))[:576]
def start(path):
 global pb
 pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);check('actual title displayed',screen()==0)
def pristine():return value(12)==0 and value(13)==0 and flags()[:9]==[0,0,0,0,0,0,0,32,2]
def welcome_page(n):
 check('correct actual welcome page',screen()==29 and pb.memory[PAGE]==n)
 check('intro leaves all progress unearned',pristine())
 check('actual Nell48px portrait source matches',bytes(pb.memory[1,0x8800:0x8a40])==portrait)
 for i in range(36):
  x=1+i%6;y=2+i//6;check('Nell portrait uses bank1 palette5 cells',pb.memory[0,0x9800+y*32+x]==128+i and pb.memory[1,0x9800+y*32+x]==13)
 snapshot(f'welcome-page-{n}')
def away_from_camp():
    mid=value(1);camp=world[mid]['camp'];positions=sorted(((x,y)for y in range(7)for x in range(10)if not blocked(mid,x,y)and(camp is None or abs(x-camp[0])+abs(y-camp[1])>1)),key=lambda p:abs(p[0]-value(2))+abs(p[1]-value(3)))
    for x,y in positions:
        try:walk(x,y);return(x,y)
        except AssertionError as exc:
            if not str(exc).startswith('unreachable approach'):raise
    raise AssertionError('No reachable legal away-camp tile')
def pinned():
 # Move away from Nell before checking the field pack's readonly current clue.
 away_from_camp();press('start',150);check('actual away-camp field pack',screen()==25)
 before=flags();points=value(13);count=value(12);press('up');check('pinned notes opens screen32',screen()==32)
 title=bytes(pb.memory[0,0x9800+3*32:0x9800+3*32+20]);want='A HOME BELOW'if not(flags()[0]&1)else'HIDE IN PLAIN SIGHT'
 check('pinned notes match actual first journal stage',title==bytes(ord(c)-32 for c in want.ljust(20)))
 for button in ['a','start','select','left','right','up','down']:press(button,30);check('pinned page cannot file notes or grant rewards',screen()==32 and flags()==before and value(13)==points and value(12)==count)
 press('b');check('pinned notes returns actual field pack',screen()==25);press('b')
with tempfile.TemporaryDirectory(prefix='rockflip-onboarding-native-')as work:
 skip=Path(work)/'skip.gbc';shutil.copy2(ROM,skip);start(skip)
 check('fresh default beside Nell in daylight',tuple(value(i)for i in [1,2,3,4])==(0,2,6,0)and pb.memory[DIR]==2 and not pb.memory[SAVE]and not pb.memory[LOCK])
 press('start');welcome_page(0);press('b',150)
 check('B skips explanation to actual hike without progress',screen()==2 and pristine());check('fresh player retains left-facing camp approach',pb.memory[DIR]==2)
 # A from this real position must talk to Nell, not open an encounter.
 press('a',150);check('fresh player can talk directly to adjacent Nell',screen()==9);press('b');pinned();pb.stop()
 for skip_page in [1,2]:
  partial=Path(work)/f'skip-page-{skip_page}.gbc';shutil.copy2(ROM,partial);start(partial);press('start')
  for _ in range(skip_page):press('a')
  welcome_page(skip_page);press('b',150);check('B skips any welcome page without progress',screen()==2 and pristine());pb.stop()
 full=Path(work)/'full.gbc';shutil.copy2(ROM,full);start(full);press('start');welcome_page(0);press('a');welcome_page(1);press('a');welcome_page(2);press('a',150)
 check('all pages finish at intended actual trail without rewards',screen()==2 and pristine()and tuple(value(i)for i in [1,2,3,4])==(0,2,6,0))
 press('a',150);check('first actual camp interaction reaches Nell',screen()==9);press('up');check('existing journal task opens',screen()==13)
 press('a');check('existing caption choices opens',screen()==14);press('down');press('a',150)
 check('wrong first caption grants no note/progression',screen()==15 and flags()[2]==0 and flags()[0]==0);press('b');press('start',150)
 check('wrong/no evidence cannot advance first journal stage',screen()==15 and flags()[0]==0);press('b');press('b');press('b')
 # Take the existing tortoise/burrow target through safe camera buttons.
 site=next(s for s in sites if s['spot_id']==2);face(site);press('a',150);check('first tortoise encounter native',screen()==3 and value(6)==0);press('a',30)
 check('safe camera starts space4',screen()==4 and value(8)==4);press('right',30)
 # Off-center focused photograph deliberately proves accessible two stars.
 for _ in range(200):
  tick(1)
  if value(7)>=45 and not pb.memory[HIDDEN]:break
 check('first camera focuses naturally',value(7)>=45 and value(8)==4);press('a',150)
 check('actual focused safe tortoise earns two stars',screen()==5 and value(11)==2 and best(0)==2 and bool(flags()[1]&1));press('b',150)
 open_camp();press('up');press('a');press('a',150);check('correct shelter caption earns original annotation',screen()==15 and bool(flags()[2]&1));press('b');press('start',150)
 check('actual photo + correct caption completes only first task',screen()==15 and flags()[0]&31==1 and flags()[7]&31==1);press('b');press('b');press('b');pinned()
 # Choose a changed phase/location, save normally, then cold continue directly.
 forecast_to(1,(flags()[9]>>1)&15);away_from_camp();press('start',150)
 saved={i:value(i)for i in [1,2,3,4,12,13]};saved_flags=flags();pb.stop();ram=Path(str(full)+'.ram');earned=ram.read_bytes();shutil.copy2(ram,OUT/'first-task-earned.ram')
 start(full);check('native cold load recognized save',bool(pb.memory[SAVE])and not pb.memory[LOCK]);press('start',150)
 check('returning title skips every tutorial directly to world',screen()==2)
 check('cold continue preserves earned location phase and progress',all(value(i)==v for i,v in saved.items())and flags()==saved_flags and best(0)==2);pb.stop()
 # File-format future fixture follows existing fault suite; no RAM injection.
 locked=Path(work)/'locked.gbc';shutil.copy2(ROM,locked);future=bytearray(earned);future[3*8192:3*8192+4]=b'RF03';future[3*8192+4]=3;Path(str(locked)+'.ram').write_bytes(future)
 start(locked);check('future format is read-only on boot',bool(pb.memory[LOCK]));press('start',150);check('locked title also bypasses fresh onboarding',screen()==2 and bool(pb.memory[LOCK]));press('start',150);pb.stop()
 check('locked future save remains byte-identical',Path(str(locked)+'.ram').read_bytes()==bytes(future))
receipt={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'frames':frames,'checks':checks,'inputs':inputs,'actual_three_pages_and_skip':True,'first_original_journal_task_earned':True,'wrong_caption_no_progress':True,'two_star_distance4_native_photo':True,'pinned_notes_readonly':True,'saved_direct_continue_cold':True,'newer_locked_direct_continue_no_SRAM_write':True,'memory_writes':False,'human_reviewed':False,'physical_device_tested':False}
(OUT/'playtest.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['checks','inputs']},indent=2))
