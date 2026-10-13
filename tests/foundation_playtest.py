"""Input-driven regression of the exact native foundation cartridge.
Never grants progress or writes emulator RAM. Saves are tested by cold boot.
"""
from pathlib import Path
import hashlib, json, re, shutil, tempfile
from collections import deque
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
SYMBOLS=Path(str(ROM)+'.debug/symbols.noi').read_text()
RF=int(re.search(r'DEF _rf 0x([0-9A-Fa-f]+)',SYMBOLS)[1],16)
OUT=ROOT/'output/qa';OUT.mkdir(parents=True,exist_ok=True)
checks=[];inputs=[];frames=0
maps=[m['terrain'] for m in json.loads((ROOT/'data/world.json').read_text())['maps']]
spots=[(0,4,3),(0,7,2),(0,2,1),(0,6,5),(0,8,5),(1,4,3),(1,2,5)]
directions={'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
RF_OFFSETS=int(re.search(r'DEF _rf_offsets 0x([0-9A-Fa-f]+)',SYMBOLS)[1],16)
def word(at):return pb.memory[at]|(pb.memory[at+1]<<8)
def offsets():return [word(RF_OFFSETS+i*2) for i in range(24)]
def readfield(index):
    at=RF+offsets()[index]
    return word(at) if index in (1,20,21) else pb.memory[at]
def state():
    o=offsets();base=[readfield(i) for i in range(14)]
    flags=list(pb.memory[RF+o[19]:RF+o[19]+7])
    base += [sum((v&1)<<i for i,v in enumerate(flags)),sum(((v>>1)&1)<<i for i,v in enumerate(flags)),sum(((v>>2)&1)<<i for i,v in enumerate(flags)),readfield(14)]
    for i in [15,16,17,18]:base+=list(pb.memory[RF+o[i]:RF+o[i]+6])
    base+=[(v>>3)&3 for v in flags]+[readfield(20)&255,readfield(20)>>8,readfield(21)&255,readfield(21)>>8]
    return base
def check(name,condition):
    assert condition,f'{name}: state={state()}'
    checks.append(name)
def tick(n):
    global frames
    pb.tick(n,True);frames+=n

def press(key,settle=40):
    inputs.append({'frame':frames,'button':key,'held_frames':8,'neutral_frames':settle})
    pb.button_press(key);tick(8);pb.button_release(key);tick(settle)
def snap(name):pb.screen.image.save(OUT/(name+'.png'))
def walk(x,y):
    room=state()[1];start=tuple(state()[2:4]);goal=(x,y);q=deque([(start,[])]);seen={start}
    while q:
        (cx,cy),path=q.popleft()
        if (cx,cy)==goal:
            for key in path:press(key,20)
            check(f'walk to {room}:{x},{y}',tuple(state()[2:4])==goal)
            return
        for key,(dx,dy) in directions.items():
            nx,ny=cx+dx,cy+dy
            if not (0<=nx<10 and 0<=ny<7) or (nx,ny) in seen:continue
            if maps[room][ny][nx] in 'GWJj' or (room,nx,ny) in spots or (room==0 and (nx,ny)==(1,6)):continue
            seen.add((nx,ny));q.append(((nx,ny),path+[key]))
    raise AssertionError('No route')
def face_spot(i):
    room,x,y=spots[i];assert state()[1]==room
    for dx,dy,key in [(-1,0,'right'),(1,0,'left'),(0,1,'up'),(0,-1,'down')]:
        nx,ny=x+dx,y+dy
        if 0<=nx<10 and 0<=ny<7 and maps[room][ny][nx] not in 'GWJj' and (room,nx,ny) not in spots:
            walk(nx,ny);press(key,20);return
    raise AssertionError('No adjacent viewing tile')
def photo(i,species):
    face_spot(i);press('a');check(f'encounter species {species}',state()[0]==3 and state()[6]==species)
    press('a');check('camera entered',state()[0]==4)
    press('down');tick(140)
    check('stillness reaches full focus',state()[7]==60)
    press('a',150);check(f'photo records species {species}',state()[0]==5 and state()[18+species]>=1)
    snap('photo-result' if species==5 else f'species-{species}-result')
    press('b',60)
    if i in [0,5,6]:
        press('b');check('cover restored',not state()[14]&(1<<i))

def rest():
    origin=state()[1];x,y=state()[2:4]
    if origin==1:walk(0,3);press('left',100)
    walk(2,6);press('start',150);check('physicalcamp reached',state()[0]==9);press('a',150);check('rest returns to trail',state()[0]==2)
    if origin==1:walk(9,3);press('right',100)
    walk(x,y)
with tempfile.TemporaryDirectory(prefix='rockflip-qa-') as tmp:
    testrom=Path(tmp)/ROM.name;shutil.copy2(ROM,testrom)
    pb=PyBoy(str(testrom),window='null',sound_emulated=False)
    pb.set_emulation_speed(0);tick(180)
    check('cold boot title',state()[0]==0);snap('title')
    press('start');check('tutorial',state()[0]==1)
    press('a',60);check('Mojave start',state()[:5]==[2,0,4,4,1]);snap('overworld')
    photo(0,5);check('first guide increment',state()[12]==1);check('care point',state()[13]==1)
    press('select',60);check('guide grid',state()[0]==7);snap('field-guide')
    press('a',60);check('guide detail',state()[0]==8);press('start',60);check('album',state()[0]==10)
    press('b');press('b',60)
    rest();check('night after dusk',state()[4]==2)
    face_spot(4);press('a');check('night sidewinder',state()[0]==3 and state()[6]==3);press('a')
    press('down');check('protected approach from four to three',state()[8]==3)
    press('down');check('protected approach stops at three',state()[8]==3)
    press('down');check('protected minimum distance rejects closer approach',state()[8]==3);press('a',150);check('protected photo',state()[18+3]>=1);press('b',60)
    walk(9,3);press('right',60);check('screen flip to spring',state()[1:4]==[1,0,3]);snap('spring-night')
    water_frames=set()
    for n in range(20):
        tick(8);water_frames.add(hashlib.sha256(pb.screen.image.crop((112,32,144,64)).tobytes()).hexdigest())
    check('spring water animates without input',len(water_frames)>=2)
    photo(5,4);check('third species',state()[12]==3)
    rest();check('day after night',state()[4]==0)
    face_spot(5);press('a');check('toad excluded by daylight',state()[0]==2 and state()[12]==3);press('b')
    walk(0,3);press('left',60);check('reverse screen flip',state()[1:4]==[0,9,3])
    photo(1,1);photo(2,0);photo(3,2);check('six unique species',state()[12]==6)
    walk(2,6);press('start',150);check('finalphoto save at physicalcamp',state()[0]==9);snap('all-six-camp');press('b',60)
    before=state();pb.stop()
    savepath=Path(str(testrom)+'.ram');check('battery RAM file exists',savepath.is_file())
    saved_hash=hashlib.sha256(savepath.read_bytes()).hexdigest()
    inputs.append({'frame':frames,'event':'cold_boot_from_sram'})
    pb=PyBoy(str(testrom),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    check('cold reboot restores all six',state()[12]==6 and state()[18:24]==before[18:24])
    check('cold reboot retains care',state()[13]==before[13])
    check('cold reboot retains region and phase',state()[1]==before[1] and state()[4]==before[4]);snap('continue-title');pb.stop()
report={'result':'pass','scope':'original six-species Mojave route on expanded engine; not full statewide campaign or physical hardware','rom_path':str(ROM),'rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'pyboy_version':'2.7.0','assertions':len(checks),'checks':checks,'frames':frames,'inputs':inputs,'save_sha256':saved_hash,'persistence':'actual SRAM file; separate cold emulator boot; no savestate','limitations':['this regression covers the original six only','physical Chromatic not tested','human audio and pacing not reviewed','full production acceptance tracked separately']}
(OUT/'foundation-playtest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['result','assertions','frames','rom_sha256','scope']},indent=2))
