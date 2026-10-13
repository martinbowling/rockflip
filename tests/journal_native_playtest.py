"""All shipped species/maps exercised through controller input on the real ROM."""
from pathlib import Path
from collections import deque
import json,re,hashlib,shutil,tempfile
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1];ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
noi=Path(str(ROM)+'.debug/symbols.noi').read_text()
def symbol(name):return int(re.search(r'DEF _'+name+r' 0x([0-9a-fA-F]+)',noi)[1],16)
RF=symbol('rf');OFF=symbol('rf_offsets');MOTION=symbol('rf_motion');HIDDEN=symbol('rf_hidden')
world=json.loads((ROOT/'data/world.json').read_text())['maps'];world={m['id']:m for m in world}
sites=json.loads((ROOT/'data/foundation_encounters.json').read_text())['records']
species=json.loads((ROOT/'data/species.json').read_text())
checks=[];inputs=[];frames=0;photos={};art_frames={};map_frames={}
OUT=ROOT/'output/qa/production';OUT.mkdir(parents=True,exist_ok=True)
DIRS={'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
def word(at):return pb.memory[at]|(pb.memory[at+1]<<8)
def offset(i):return word(OFF+i*2)
def value(i):return word(RF+offset(i)) if i in (1,20,21) else pb.memory[RF+offset(i)]
def best(sid):return pb.memory[RF+offset(15)+sid]
def screen():return value(0)
def flags():return list(pb.memory[RF+offset(23)+56:RF+offset(23)+88])
def check(name,ok):
    if not ok:
        pb.screen.image.save(OUT/'first-failure.png')
        (OUT/'first-failure.json').write_text(json.dumps({'check':name,'frame':frames,'inputs':inputs,'state':{str(i):value(i) for i in range(15)}},indent=2)+'\n')
    assert ok,name
    checks.append(name)
def tick(n):
    global frames
    pb.tick(n,True);frames+=n

def press(button,settle=70):
    inputs.append({'frame':frames,'button':button,'held':8,'neutral':settle})
    pb.button_press(button);tick(8);pb.button_release(button);tick(settle)
def enter_hike():
    """Actual title entry: new welcome, saved-direct, or older controls page.

    General regressions skip explanation deliberately; dedicated onboarding
    acceptance exercises all pages and first journal rather than using this.
    Never issue an extra A once hiking (it could talk/open a habitat).
    """
    for _ in range(8):
        state=screen()
        if state==2:return
        if state==0:press('start',150)
        elif state==1:press('a',150)
        elif state==29:press('b',150)
        else:raise AssertionError(f'Unexpected entry screen{state}')
    raise AssertionError('Controller entry did not reach hike within eight inputs')
def snapshot(name):pb.screen.image.save(OUT/(name+'.png'))
def route_walk(mid):
    start=value(1);target=world[mid];q=deque([(start,[])]);seen={start};path=None
    while q:
        at,route=q.popleft()
        if at==mid:path=route;break
        for key in ('west','east','north','south'):
            nxt=world[at].get(key)
            if nxt is not None and nxt not in seen and world[nxt]['district_id']==target['district_id']:
                seen.add(nxt);q.append((nxt,route+[(at,key,nxt)]))
    assert path is not None,f'No legal district route from {start} to {mid}'
    for at,key,nxt in path:
        if key in ('west','east'):walk(0 if key=='west' else 9,3);button='left' if key=='west' else 'right'
        else:walk(world[at][key+'_x'],0 if key=='north' else 6);button='up' if key=='north' else 'down'
        press(button,100)
        if screen()==16:press('a',100)
        check(f'legal district screen-flip reaches {nxt}',screen()==2 and value(1)==nxt)
    check(f'normal route enters map {mid}',value(1)==mid)
def open_camp():
    if value(1)==131:
        press('start',150);check('hidden refuge has safe field pack',screen()==25);press('right',150);check('earned refuge return reaches coast trailhead',screen()==2 and value(1)!=131)
    origin=world[value(1)];q=deque([value(1)]);seen=set();camp=None
    while q:
        mid=q.popleft()
        if mid in seen:continue
        seen.add(mid);m=world[mid]
        if m['camp'] is not None:camp=mid;break
        for k in ('west','east','north','south'):
            nxt=m.get(k)
            if nxt is not None and world[nxt]['district_id']==origin['district_id'] and (origin['district_id']!='D12' or world[nxt]['subarea_id']==origin['subarea_id']):q.append(nxt)
    assert camp is not None,'No reachable physical camp'
    route_walk(camp);x,y=world[camp]['camp']
    for _,(dx,dy) in DIRS.items():
        nx,ny=x-dx,y-dy
        if 0<=nx<10 and 0<=ny<7 and not blocked(camp,nx,ny):walk(nx,ny);break
    press('start',150);check('actual adjacent physical camp opens',screen()==9)
def travel(mid):
    if value(1)==mid:return
    target=world[mid];district=int(target['district_id'][1:])-1;current=value(1)
    if target.get('hidden') or world[current]['district_id']!=target['district_id'] or current==131:
        index=16 if target.get('hidden') else district
        if index==16:check('hidden travel requires earned discovery',bool(flags()[31]&128))
        open_camp();current=value(1);press('right');check('expedition atlas opens',screen()==12)
        selected=int(world[current]['district_id'][1:])-1;total=17 if flags()[31]&128 else 16
        for _ in range((index-selected)%total):press('right',35)
        press('a',150)
        if screen()==16:press('a',150)
        check('regional trailhead travel returns to hike',screen()==2)
    route_walk(mid)
def blocked(mid,x,y):
    m=world[mid]
    return m['terrain'][y][x] in 'GWJj' or [x,y]==m['camp'] or any(s['room_id']==mid and (s['game_tile_x'],s['game_tile_y'])==(x,y) for s in sites)
def walk(x,y):
    mid=value(1);start=(value(2),value(3));q=deque([(start,[])]);seen={start}
    while q:
        pos,path=q.popleft()
        if pos==(x,y):
            for key in path:press(key,24)
            check('legal walk reaches observation approach',(value(2),value(3))==(x,y));return
        for key,(dx,dy) in DIRS.items():
            nx,ny=pos[0]+dx,pos[1]+dy
            if not 0<=nx<10 or not 0<=ny<7 or (nx,ny) in seen or blocked(mid,nx,ny):continue
            seen.add((nx,ny));q.append(((nx,ny),path+[key]))
    raise AssertionError(f'unreachable approach {mid}:{x},{y}')
def face(site):
    x,y=site['game_tile_x'],site['game_tile_y'];mid=site['room_id']
    for key,(dx,dy) in DIRS.items():
        nx,ny=x-dx,y-dy
        if 0<=nx<10 and 0<=ny<7 and not blocked(mid,nx,ny):
            try:walk(nx,ny)
            except AssertionError:continue
            press(key,24);return
    raise AssertionError('site has no legal observation approach')
def forecast_to(phase,conditions):
    origin=value(1);open_camp();press('a',80);check('camp forecast opens',screen()==27)
    settings=[('rf_forecast_phase',phase,3),('rf_forecast_weather',conditions&3,4),('rf_forecast_season',conditions>>2,4)]
    for field,(name,target,mod) in enumerate(settings):
        if field:press('down',30)
        for _ in range((target-pb.memory[symbol(name)])%mod):press('right',30)
    press('a',150);check('chosen forecast returns to hike',screen()==2 and value(4)==phase and ((flags()[9]>>1)&15)==conditions)
    travel(origin)
def rest_to(phase):
    if value(4)==phase:return
    if '_rf_forecast_phase ' in noi:
        forecast_to(phase,(flags()[9]>>1)&15);return
    origin=value(1)
    while value(4)!=phase:
        open_camp();press('a',150);check('physical rest returns to hike',screen()==2)
    travel(origin)
def conditions_for_subject(sid):
    if '_rf_forecast_phase ' not in noi or sid not in (9,24,118,124):return
    c=(flags()[9]>>1)&15;w=c&3;season=c>>2
    allowed=(w==2 and season!=2) if sid==9 else (w>=2 and season in (1,2)) if sid in (24,118) else (w>=2 and season!=2)
    if not allowed:forecast_to(value(4),6) # actual rain/spring is eligible for all four selected vignettes

OUT=ROOT/"output/qa/journal-native";OUT.mkdir(parents=True,exist_ok=True)
def photo_site(spot):
    site=next(s for s in sites if s['spot_id']==spot)
    travel(site['room_id']);rest_to(next(i for i in range(3) if site['phase_mask']&(1<<i)));face(site);press('a',100)
    for _ in range(2):
        if screen()==3:break
        press('b');press('a',100)
    check('eligible site retries are bounded',screen()==3);press('a');press('down',20);tick(100);press('a',150)
    check('journal evidence photograph succeeds',screen()==5 and value(11)>=2);press('b')
    if site['interaction_type'] in (0,5):press('b')
def open_journal():open_camp();press('up');check('native journal opens',screen()==13)
def note(choice):
    press('a');check('observation choices open',screen()==14)
    for _ in range(choice):press('down')
    press('a');check('note feedback opens',screen()==15);press('b')
def file_stage(expected):
    press('start');check('ranger turn-in feedback opens',screen()==15)
    check('exact investigation stage completes',flags()[0]==expected);snapshot('stage-'+str(expected));press('b')
def return_trail():press('b');press('b');check('journal returns to trail',screen()==2)
with tempfile.TemporaryDirectory(prefix='rockflip-journal-') as tmp:
    testrom=Path(tmp)/ROM.name;shutil.copy2(ROM,testrom)
    pb=PyBoy(str(testrom),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180);enter_hike()
    open_journal();note(1);check('wrong answer gives no note credit',flags()[2]==0)
    press('start');check('missing evidence cannot advance',flags()[0]==0);press('b');return_trail()
    photo_site(2);check('photo event credits exact burrow before annotation',flags()[1]&1)
    open_journal();note(0);file_stage(1);return_trail()
    photo_site(3);photo_site(1);open_journal();note(2);file_stage(3);return_trail()
    photo_site(0);check('matching photographed rock earns care',flags()[3]&1);open_journal();note(1);file_stage(7);return_trail()
    photo_site(5);photo_site(7);check('spring restoration earns independent care',flags()[3]&2);open_journal();note(0);file_stage(15)
    note(2);file_stage(31);check('first survey flag and rewards persist',flags()[8]&1 and flags()[7]==31)
    before=flags();press('start');check('completed survey cannot duplicate reward',flags()==before);press('b');snapshot('first-survey-filed');return_trail();press('start');press('b',100)
    before=flags();pb.stop();pb=PyBoy(str(testrom),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    check('actual cold SRAM restores every journal flag',flags()==before);snapshot('cold-journal-continue');pb.stop()
report={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'frames':frames,'inputs':inputs,'first_survey_complete':True,'scope':'five-stage Mojave opening withphysicalcamp filing; separate fullcampaign regression exists'}
(OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['result','assertions','rom_sha256']},indent=2))
