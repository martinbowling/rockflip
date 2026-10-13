"""Actual controller atlas traversal on fresh16 and genuinely earned17 saves.
No emulated memory writes. Requires the exact root-approved candidate hash.
"""
from pathlib import Path
import argparse,ast,json,hashlib,shutil,tempfile
args_parser=argparse.ArgumentParser()
args_parser.add_argument('--expected-sha',required=True)
args_parser.add_argument('--earned-save',type=Path,default=Path('output/qa/controller-earned-151-c66c.ram'))
args=args_parser.parse_args()
HERE=Path(__file__).resolve().parent
source=(HERE/'production_playtest.py').read_text();tree=ast.parse(source);prefix=[]
for node in tree.body:
    if isinstance(node,ast.With):break
    prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(HERE/'production_playtest.py'),'exec'),globals())
actual_hash=hashlib.sha256(ROM.read_bytes()).hexdigest()
assert actual_hash==args.expected_sha,'Candidate ROM hash differs from authorized test hash'
OUT=ROOT/'output/qa/atlas-native';OUT.mkdir(parents=True,exist_ok=True)
profiles=[]
def cursor():return word(RF+offset(23)+54)
def state():return bytes(pb.memory[RF:RF+2544])
def menu_snapshot():
    data=bytearray(state());data[offset(23)+54:offset(23)+56]=b'\0\0';return bytes(data)
def rendered_cursor(expected,total):
    if cursor()!=expected or screen()!=12:
        (OUT/'cursor-failure.json').write_text(json.dumps({'rom_sha256':actual_hash,'expected':expected,'actual':cursor(),'flags31':flags()[31],'total':total,'frame':frames,'RF':list(state())},indent=2)+'\n')
    check('atlas current cursor equals expected',cursor()==expected and screen()==12)
    for row in range(6):
        idx=expected//6*6+row
        if idx>=total:break
        mid=next((m['id'] for m in world.values() if m.get('district_trailhead') and int(m['district_id'][1:])-1==idx),None) if idx<16 else 131
        name='UNMARKED TRAIL' if idx==16 else world[mid]['name']
        expected_row=(('>' if idx==expected else ' ')+name)[:20].ljust(20)
        got=bytes(pb.memory[0,0x9800+(3+row*2)*32:0x9800+(3+row*2)*32+20])
        check(f'visible expedition label {idx}',got==bytes(ord(c)-32 for c in expected_row))
def select(index,total):
    for _ in range((index-cursor())%total):press('right',100)
    rendered_cursor(index,total)
def start(cart):
    global pb
    pb=PyBoy(str(cart),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);enter_hike()
with tempfile.TemporaryDirectory(prefix='rockflip-atlas-') as work:
    for profile,total in [('fresh',16),('earned',17)]:
        cart=Path(work)/(profile+'.gbc');shutil.copy2(ROM,cart)
        if profile=='earned':shutil.copy2(args.earned_save,Path(str(cart)+'.ram'))
        start(cart)
        check(profile+' correct actual hidden eligibility',bool(flags()[31]&128)==(total==17))
        if profile=='earned':check('genuine earned collection has151 species',value(12)==151)
        open_camp();press('right',100);check('physical camp opens atlas',screen()==12)
        initial=cursor();untouched=menu_snapshot();rendered_cursor(initial,total)
        for button,delta in [('right',1),('left',-1),('down',1),('up',-1)]:
            before=cursor()
            for count in range(total):
                press(button,100);rendered_cursor((before+delta*(count+1))%total,total)
                check(profile+' browsing preserves all other progress bytes',menu_snapshot()==untouched)
            check(profile+' complete direction cycle wraps',cursor()==before)
            if button=='right':print(json.dumps({'signal':'actual atlas right-cycle wrap passed','profile':profile,'total':total,'rom_sha256':actual_hash}),flush=True)
        # Visit all real destinations through actual A, including ferry consent.
        destinations=[]
        for idx in range(total):
            select(idx,total);before_flags=flags();press('a',150)
            if screen()==16:press('a',150)
            expected=131 if idx==16 else next(m['id'] for m in world.values() if m.get('district_trailhead') and int(m['district_id'][1:])-1==idx)
            check(profile+f' actual expedition A reaches trailhead {expected}',screen()==2 and value(1)==expected)
            check(profile+' expedition preserves earned hidden gate',bool(flags()[31]&128)==(total==17))
            destinations.append(expected);snapshot(profile+f'-destination-{idx:02}')
            open_camp();press('right',100);check(profile+' next physical camp atlas opens',screen()==12)
        press('b',100);check('B returns to physical camp',screen()==9);pb.stop()
        profiles.append({'profile':profile,'count':total,'destinations':destinations,'fixture_sha256':hashlib.sha256(args.earned_save.read_bytes()).hexdigest() if profile=='earned' else None})
receipt={'result':'pass','rom_sha256':actual_hash,'assertions':len(checks),'frames':frames,'profiles':profiles,'checks':checks,'inputs':inputs,'memory_writes':False,'human_reviewed':False,'physical_device_tested':False}
(OUT/'playtest.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['checks','inputs']},indent=2))
