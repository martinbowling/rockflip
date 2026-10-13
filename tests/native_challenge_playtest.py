"""All32 optional challenges: native text, safe natural3star input, cold save.

Imports read-only quality opportunity helpers before their top-level ROM run.
No emulator memory writes or fabricated progress; all routes/camps/photos use
real controller buttons. Run only after the challenge+quality ROM is rebuilt.
"""
from pathlib import Path
import ast,json,hashlib,shutil,tempfile
HERE=Path(__file__).resolve().parent
source=(HERE/'native_behavior_quality.py').read_text();tree=ast.parse(source);prefix=[]
for node in tree.body:
    if isinstance(node,ast.With):break
    prefix.append(node)
# Inherited quality helper loads the root physical-camp harness unchanged.
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(HERE/'native_behavior_quality.py'),'exec'),globals())
OUT=ROOT/'output/qa/challenge-native';OUT.mkdir(parents=True,exist_ok=True)
challenge_data=json.loads((ROOT/'data/photo_challenges.json').read_text());targets=challenge_data['records']
CHALLENGE=symbol('rf_challenge');observations=[]

def tile_line(y):
    # Native font uses ASCII minus32; renderer leaves VBK=0 after each cell.
    return ''.join(chr(pb.memory[0x9800+y*32+x]+32)for x in range(20)).rstrip()

def assert_ui(row,complete):
    i=row['index'];check(f'challenge{i} exactnativeindex',screen()==26 and pb.memory[CHALLENGE]==i)
    expected={0:'   PHOTO CHALLENGES',2:row['title'][0],3:'THREE-STAR PAGE DONE'if complete else'A NATURAL MOMENT',11:row['care'][0],13:world[row['approved_hint_site']['map_id']]['name'],16:'LEFT/RIGHT: NEXT',17:'B: BACK TO PACK'}
    for n,line in enumerate(row['brief']):expected[5+n]=line
    for n,line in enumerate(row['hint']):expected[8+n]=line
    for y,text in expected.items():check(f'challenge{i} native text row{y} matchesdata',tile_line(y)==text.rstrip())
    phase=['DAY','DUSK','NIGHT'][row['approved_hint_site']['phase']]
    check(f'challenge{i} displayedphase matchesapprovedsite',tile_line(14).endswith(phase))

def field_pack_challenges():
    check('open challenge from hiking',screen()==2)
    mid=value(1);camp=world[mid]['camp']
    # Field pack requires a position away from the physical camp.
    if camp and abs(value(2)-camp[0])+abs(value(3)-camp[1])<=1:
        moved=False
        for y in range(7):
            for x in range(10):
                if not blocked(mid,x,y)and abs(x-camp[0])+abs(y-camp[1])>1:
                    try:walk(x,y);moved=True;break
                    except AssertionError:continue
            if moved:break
        check('legal walk away fromcamp for fieldpack',moved)
    press('start',150);check('fieldpack opens awayfromcamp',screen()==25)
    press('a',150);check('fieldpack opens local first challenge',screen()==26 and pb.memory[CHALLENGE]==(int(world[value(1)]['district_id'][1:])-1)*2)

def browse_all(done):
    field_pack_challenges()
    for _ in range(pb.memory[CHALLENGE]):press('left',40)
    for i,row in enumerate(targets):
        assert_ui(row,done)
        snapshot(('cold-complete'if done else'unearned')+f'-challenge-{i:02d}')
        press('right',40)
    check('all32challenge browsing wraps tozero',pb.memory[CHALLENGE]==0)
    press('b',150);check('challengeB returns fieldpack',screen()==25);press('b',150);check('fieldpackB returns hiking',screen()==2)

def challenge_photo(row):
    sid=row['species_id'];site=next(s for s in sites if s['spot_id']==row['approved_hint_site']['spot_id'])
    check('challenge site identity matches source data',site['species_id']==sid and site['room_id']==row['approved_hint_site']['map_id'])
    open_subject(site);check('approved phase reached',value(4)==row['approved_hint_site']['phase'])
    family=species[sid]['behavior'];target=1 if family in('glide','hop','slow_walk','night_peek','rain_arrival') else 0
    aim_to(target)
    try:state=wait_for(row['id']+' safe naturalwindow',lambda s:natural_window(family,s))
    except AssertionError:
        (OUT/'window-failure.json').write_text(json.dumps({'challenge':row['id'],'observed':observed()},indent=2)+'\n');raise
    check('challenge earned at safe four-space distance',state['distance']==4)
    check('challenge natural moment is calm and notprovoked',state['stress']==0 and state['disturbed']==0)
    snapshot('before-'+str(row['index']).zfill(2))
    (OUT/'shutter-attempt.json').write_text(json.dumps({'challenge':row['id'],'before':state},indent=2)+'\n')
    shutter('challenge-'+str(row['index']).zfill(2)+'-natural',3);check('challenge persistentbest earns exactly3stars',best(sid)==3)
    observations.append({'challenge_id':row['id'],'species_id':sid,'spot_id':site['spot_id'],'map_id':site['room_id'],'before_shutter':state,'best':best(sid)})
    return_trail(site)
    field_pack_challenges()
    current=pb.memory[CHALLENGE]
    for _ in range((row['index']-current)%32):press('right',40)
    assert_ui(row,True);press('b',150);press('b',150)

AWARD_BYTES=[0,0,0,1,1,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5,5,5,5,6,6,6,6,6]
AWARD_MASKS=[32,64,128,64,128,32,64,128,4,8,16,32,64,128,4,8,16,32,64,128,2,4,8,16,32,64,128,8,16,32,64,128]
def actual_awards():return tuple(bool(flags()[b]&m)for b,m in zip(AWARD_BYTES,AWARD_MASKS))

with tempfile.TemporaryDirectory(prefix='rockflip-challenge-native-')as work:
    path=Path(work)/ROM.name;shutil.copy2(ROM,path)
    pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    enter_hike();check('fresh native cartridge enters hiking',screen()==2)
    check('challenge roster remains32distinctregularidentities',len(targets)==32 and len({r['species_id']for r in targets})==32 and all(r['species_id']<150 for r in targets))
    check('fresh layout5 challenge mode has no awards',flags()[7]&32 and not any(actual_awards()))
    browse_all(False)
    open_camp();press('down',150);check('actual localcampaign opens',screen()==17);press('select',150);check('campaignSELECT opens same localchallenges',screen()==26);assert_ui(targets[0],False);press('b',150);check('campaignchallenge returns fieldpack',screen()==25);press('b',150)
    for n,row in enumerate(targets):
        challenge_photo(row)
        check('exact local shutter earns its own persisted task bit',actual_awards()[row['index']])
        check('completion count follows explicit regional awards',sum(actual_awards())==n+1)
    check('all32 regional awards completed without exhibitending',sum(actual_awards())==32 and not(flags()[30]&15))
    check('hidden discovery doesnotgate challenges',best(150)==0 and not(flags()[31]&128))
    open_camp();press('b',150);room=value(1);poses={r['species_id']:pb.memory[RF+2256+r['species_id']]for r in targets}
    check('all32 photos have independently captured knownposes',all(v&128 for v in poses.values()))
    earned_awards=actual_awards();pb.stop();saved=Path(str(path)+'.ram').read_bytes();(OUT/'completed-challenges.ram').write_bytes(saved)
    pb=PyBoy(str(path),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    check('cold SRAM retains all32three-star photos',all(best(r['species_id'])==3 for r in targets))
    check('cold exact regional award bitmap remains32',actual_awards()==earned_awards and sum(actual_awards())==32 and flags()[7]&32)
    check('cold photo pose metadata preserved',all(pb.memory[RF+2256+sid]==pose for sid,pose in poses.items()))
    enter_hike();check('coldcontinue actualhike',screen()==2 and value(1)==room);browse_all(True);pb.stop()
report={'result':'pass','scope':'Actual native32challenge screens, controller-earned natural3star photographs at approved regional sites, explicit32 regionalaward bits and exactbitmap cold-save retention. No injected progress.','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'challenge_data_sha256':hashlib.sha256((ROOT/'data/photo_challenges.json').read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'inputs':inputs,'frames':frames,'challenges':observations,'cold_completion_count':32,'ending_required':False,'physical_hardware_verified':False}
(OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in('result','assertions','rom_sha256','cold_completion_count')},indent=2))
