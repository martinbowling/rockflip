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
hardware_peak={"visible_obj":0,"obj_per_scanline":0,"observed_frames":0}
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
    if pb.memory[0xFF40]&2:
        height=16 if pb.memory[0xFF40]&4 else 8
        objects=[(pb.memory[0xFE00+i*4]-16,pb.memory[0xFE01+i*4]-8) for i in range(40)]
        visible=sum(1 for y,x in objects if y<144 and y+height>0 and x<160 and x+8>0)
        perline=max(sum(1 for y,x in objects if y<=line<y+height) for line in range(144))
        assert visible<=40 and perline<=10,'Native OAM/scanline allocation exceeded hardware'
        hardware_peak['visible_obj']=max(hardware_peak['visible_obj'],visible)
        hardware_peak['obj_per_scanline']=max(hardware_peak['obj_per_scanline'],perline)
        hardware_peak['observed_frames']+=1

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
        for key in (('west','east') if globals().get('LEGACY_LINEAR_ROUTES') else ('west','east','north','south')):
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
    conditions_for_subject(site['species_id'])
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
with tempfile.TemporaryDirectory(prefix='rockflip-production-') as tmp:
    testrom=Path(tmp)/ROM.name;shutil.copy2(ROM,testrom)
    pb=PyBoy(str(testrom),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    data_start=int(re.search(r'DEF s__DATA 0x([0-9A-Fa-f]+)',noi)[1],16);data_end=max(int(re.search(r'DEF s__'+sec+r' 0x([0-9A-Fa-f]+)',noi)[1],16)+int(re.search(r'DEF l__'+sec+r' 0x([0-9A-Fa-f]+)',noi)[1],16) for sec in ('DATA','BSS','INITIALIZED','HEAP','HEAP_END'));stack_top=int(re.search(r'DEF \.STACK 0x([0-9A-Fa-f]+)',noi)[1],16);canary_end=pb.register_file.SP
    check('runtime stack canary starts in unused WRAM gap',canary_end-data_end>=768 and canary_end<=stack_top)
    for addr in range(data_end,canary_end):pb.memory[addr]=0xA5
    check('native boot reaches live title',screen()==0 and (value(2),value(3),value(4))==((2,6,0)if '_rf_welcome_page 'in noi else(4,4,1)));enter_hike()
    from campaign_native_driver import complete_opening,complete_regions_and_exhibit
    ordered=[r for r in sites if r['species_id']!=150]+[r for r in sites if r['species_id']==150]
    for site in ordered:
        if site['species_id']==150:
            check('all150regular species precede hidden discovery',value(12)==150 and not (flags()[31]&128))
            complete_opening(globals());complete_regions_and_exhibit(globals())
            check('actual exhibit and allregional stories precede hidden trail',flags()[30]&15==15 and all(((flags()[10+d//4]>>((d%4)*2))&3)==3 for d in range(16)))
            check('hidden trail is earned through caption and150photos',flags()[31]&128)
            # Preserve the actually committed cartridge RAM before its first
            # hidden portrait is known. These are read-only bank observations,
            # not a fabricated fixture or a gameplay-memory write.
            from native_snapshot_migration import latest
            hidden_sram=b''.join(bytes(pb.memory[bank,0xa000:0xbfff])+bytes([pb.memory[bank,0xbfff]]) for bank in range(4))
            hidden_record=latest(hidden_sram)
            check('actual prehidden save contains150 photos and earned refuge',
                  hidden_record is not None and hidden_record['payload'][offset(12)]==150
                  and hidden_record['payload'][offset(15)+150]==0
                  and hidden_record['payload'][offset(23)+56+31]&128)
            (OUT/'controller-earned-prehidden150.ram').write_bytes(hidden_sram)
            (OUT/'prehidden150-binding.json').write_text(json.dumps({
                'rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),
                'sram_sha256':hashlib.sha256(hidden_sram).hexdigest(),
                'frames':frames,'regular_photos':150,'hidden_photo_known':False,
                'source':'Actual committed four-bank SRAM observed before first hidden photograph; no injected progress'},indent=2)+'\n')
        travel(site['room_id']);mid=site['room_id'];sid=site['species_id']
        if mid not in map_frames:
            rest_to(0);snapshot(f'map-{mid:04d}');map_frames[mid]=hashlib.sha256(pb.screen.image.crop((0,16,160,128)).tobytes()).hexdigest()
        phase=next(i for i in range(3) if site['phase_mask']&(1<<i));rest_to(phase);face(site);press('a',100)
        check(f'species {sid} valid region/habitat encounter',screen()==3 and value(6)==sid)
        press('a');check(f'species {sid} camera opens',screen()==4)
        # Retain native portrait animation evidence from the actual viewfinder.
        tick(180);crops=set();poses=set()
        for _ in range(max(32,species[sid].get('behavior_params',{}).get('period',90)//4)):
            tick(24);crops.add(hashlib.sha256(pb.screen.image.crop((16,32,144,96)).tobytes()).hexdigest());poses.add(pb.memory[MOTION])
        art_frames[sid]=len(crops)
        if sid in (6,13):check(f'species {sid} timed push-up pose is observable',len(crops)>1 and len(poses)>1)
        min_distance=species[sid].get('behavior_params',{}).get('minimum_distance',2)
        press('down',20);tick(100)
        for _ in range(24):
            while pb.memory[HIDDEN] or value(7)<45:tick(12)
            press('a',150) # Wait for the real streaming SRAM commit/result draw.
            if screen()==5:break
        check(f'species {sid} photograph updates guide record',screen()==5 and best(sid)>0)
        photos[sid]=best(sid);snapshot(f'species-{sid:03d}-result');press('b',70)
        if site['interaction_type'] in (0,5):press('b')
    check('all shipped identities count exactly once',value(12)==len(species) and len(photos)==len(species))
    check('all authored maps reached',set(map_frames)==set(world))
    check('daylight terrain renderings differ across authored maps',len(set(map_frames.values()))==len(world))
    for mid,m in world.items():
        if m['east'] is None:continue
        travel(mid);walk(9,3);press('right',60);
        if screen()==16:press('a',60)
        check(f'actual east screen flip {mid}',value(1)==m['east'] and value(2)==0 and value(3)==3)
        press('left',60);
        if screen()==16:press('a',60)
        check(f'actual reciprocal west screen flip {mid}',value(1)==mid and value(2)==9 and value(3)==3)
    for mid,m in world.items():
        for direction,row,reverse,arrival_row in [('north',0,'south',6),('south',6,'north',0)]:
            target=m.get(direction)
            if target is None:continue
            travel(mid);walk(m[direction+'_x'],row);press('up' if direction=='north' else 'down',60)
            check(f'actual{direction}portal {mid}->{target}',value(1)==target and value(2)==world[target][reverse+'_x'] and value(3)==arrival_row)
            press('down' if direction=='north' else 'up',60)
            check(f'actual reciprocal{reverse}portal returns{mid}',value(1)==mid and value(2)==m[direction+'_x'] and value(3)==row)
    press('select');check('guide opens',screen()==7)
    for _ in range((len(species)-1-value(14))%len(species)):press('right',30)
    check('guide cursor reaches highest shipped species',value(14)==len(species)-1);snapshot('guide-last-page')
    press('a');check('highest species scientific detail opens',screen()==8);snapshot('guide-last-detail');press('start');check('highest species album opens',screen()==10)
    press('b');press('b');press('start',150);check('save usesfieldpack orphysicalstation',screen() in (9,25));press('b',100)
    changed=[addr for addr in range(data_end,canary_end) if pb.memory[addr]!=0xA5];lowest=min(changed) if changed else canary_end;stack_report={'initial_sp':canary_end,'lowest_changed_canary':lowest,'observed_max_depth':stack_top-lowest,'remaining_data_gap':lowest-data_end,'instrumentation':'diagnostic canary writes only to compiled unused WRAM below paused SP; gameplay flags never injected'}
    check('native full trace retains512byte WRAM stack margin',lowest-data_end>=512)
    captured={sid:best(sid) for sid in photos};count=value(12);room=value(1)
    persistent_ranges=[(offset(15),offset(23)+50),(offset(23)+56,offset(23)+88),(2256,2448)]
    if '_rf_forecast_phase ' in noi:persistent_ranges.append((2448,2544))
    persistent_bytes=[bytes(pb.memory[RF+a:RF+b]) for a,b in persistent_ranges]
    position_before={i:value(i) for i in (1,2,3,4,13,20,21)}
    pb.stop();savepath=Path(str(testrom)+'.ram');check('actual SRAM file emitted',savepath.exists());sram=savepath.read_bytes();(OUT/'controller-earned-complete.ram').write_bytes(sram)
    check('both RF02 save slots committed',sram[3*8192:3*8192+4]==b'RF02' and sram[3*8192+4096:3*8192+4100]==b'RF02')
    pb=PyBoy(str(testrom),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    check('cold native boot restores all actual photo records',value(12)==count and all(best(sid)==score for sid,score in captured.items()))
    check('cold native boot restores current region',value(1)==room)
    check('cold restore preserves every photo metadata/site/visited byte',bytes(pb.memory[RF+persistent_ranges[0][0]:RF+persistent_ranges[0][1]])==persistent_bytes[0])
    check('cold restore preserves full campaign/finale/hidden/preferences flags',bytes(pb.memory[RF+persistent_ranges[1][0]:RF+persistent_ranges[1][1]])==persistent_bytes[1])
    check('cold restore preserves all192 stored pose bytes',bytes(pb.memory[RF+2256:RF+2448])==persistent_bytes[2])
    check('cold restore preserves actual position/phase/care/RNG/steps',all(value(i)==v for i,v in position_before.items()))
    if len(persistent_ranges)>3:check('cold restores all96 packed condition bytes',bytes(pb.memory[RF+2448:RF+2544])==persistent_bytes[3])
    snapshot('cold-continue');pb.stop()
report={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'species_count':len(species),'map_count':len(world),'district_count':len({m['district_id'] for m in world.values()}),'frames':frames,'inputs':inputs,'native_portrait_frame_variants':art_frames,'stack_watermark':stack_report,'hardware_peak':hardware_peak,'all_shipped_species_photographed':True,'cold_sram_restored':True,'scope':'full native151-species241-map/16-district development cartridge including campaign/exhibit/hidden inputs; human fun/audio and physical acceptance remain pending'}
(OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['result','assertions','species_count','map_count','district_count','rom_sha256']},indent=2))
