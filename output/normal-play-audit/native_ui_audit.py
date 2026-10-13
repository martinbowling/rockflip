"""AI technical route/clue counterexamples on exact accepted5762, not human fun."""
from pathlib import Path
import ast,json,hashlib,tempfile,shutil,sys
ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/'tests/production_playtest.py';prefix=[]
for n in ast.parse(SOURCE.read_text()).body:
 if isinstance(n,ast.With):break
 prefix.append(n)
oldfile=__file__;__file__=str(SOURCE);exec(compile(ast.Module(body=prefix,type_ignores=[]),str(SOURCE),'exec'),globals());__file__=oldfile
SHA='5762c0022396470147c9eeca529c193964ecbbd71ddb6c36cccc7804bac53cb5';assert hashlib.sha256(ROM.read_bytes()).hexdigest()==SHA
OUT=ROOT/'output/qa/normal-play-audit';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tests'));import campaign_native_driver as campaign_driver
base_press=press
def settled_press(button,settle=150):return base_press(button,max(settle,150))
def line(y):return ''.join(chr(c+32)for c in pb.memory[0,0x9800+y*32:0x9800+y*32+20]).rstrip()
with tempfile.TemporaryDirectory(prefix='rockflip-normal-ui-')as work:
 cart=Path(work)/'audit.gbc';shutil.copy2(ROM,cart);pb=PyBoy(str(cart),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);enter_hike()
 # Open-world travel offers every region before opening journal completion.
 travel(8);open_camp();press('down');check('fresh openworld has actual D05 investigation',screen()==17 and line(2)=='A HIGH LAKE EDGE');d05clue=[line(y)for y in [2,4,5]];snapshot('D05-camp-current-clue');press('b');press('b')
 # Select a reachable away-camp fieldpack position, preserving camp real rules.
 for y in range(7):
  for x in range(10):
   if not blocked(value(1),x,y) and abs(x-world[value(1)]['camp'][0])+abs(y-world[value(1)]['camp'][1])>1:
    try:walk(x,y);break
    except AssertionError:continue
  else:continue
  break
 press('start',150);check('actual awaycamp fieldpack',screen()==25);press('up');check('fresh D05 pinned notes prioritize distant Nell opening',screen()==32 and line(1)=="NELL'S FIRST SURVEY");pinned=[line(y)for y in [1,3,5,6,7,8]];snapshot('D05-pinned-distant-opening');press('b');press('b');travel(0)
 # Earn every actual opening task, then file D01 without another animal/route.
 # Inputs settle fully across care+save; no progress/position writes.
 saved_press=press;press=settled_press
 campaign_driver.complete_opening(globals());open_camp();press('down');check('D01 campaign starts unfiled after opening',screen()==17 and (flags()[10]&3)==0)
 check('opening already supplies allfour D01 regional photo bits',flags()[14]&15==15)
 pb.stop();shutil.copy2(Path(str(cart)+'.ram'),OUT/'actual-layout5-partial-D01.ram');pb=PyBoy(str(cart),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);enter_hike();open_camp();press('down')
 before_count=value(12);before_steps=value(21);before_visit=bytes(pb.memory[RF+offset(23):RF+offset(23)+50]);record=[]
 d01=json.loads((ROOT/'data/campaign.json').read_text())['districts'][0]
 for st in d01['stages']:
  record.append({'stage':st['stage_index'],'title':line(2),'clue':[line(4),line(5)]});snapshot('D01-prefilled-'+str(st['stage_index']))
  press('a');
  for _ in range(st['correct_choice']):press('down')
  press('a');press('b');press('start');check('D01 prefilled evidencefilesstage'+str(st['stage_index']),screen()==19 and flags()[10]&3==st['stage_index']+1);press('b')
 check('D01 complete without another photograph or hike',value(12)==before_count and value(21)==before_steps and bytes(pb.memory[RF+offset(23):RF+offset(23)+50])==before_visit)
 snapshot('D01-story-without-new-route');pb.stop()
receipt={'result':'observed-design-risks','rom_sha256':SHA,'assertions':len(checks),'frames':frames,'AI_technical_review_only':True,'human_fun_approved':False,'memory_writes':False,'D05_actual_campaign_clue':d05clue,'D05_actual_pinned_opening_clue':pinned,'D01_three_stages_prefilled_by_opening':True,'D01_no_additional_shutters_steps_or_visited_maps':True,'D01_photo_count_after_opening':before_count,'D01_caption_only_stages':record,'inputs':inputs,'checks':checks}
(OUT/'native-ui-audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['inputs','checks']},indent=2))
