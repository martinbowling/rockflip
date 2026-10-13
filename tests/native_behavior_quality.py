"""Controller-only paired behavior-quality tests on the delivered native ROM.

Reuse the current production harness definitions, including root's physical
camp navigation. Every progression mutation comes from buttons. Memory is
read only; no quest, quality, position, save or diagnostic-canary writes.
Run after quality/stress integration is compiled. Baseline052f lacks symbols.
"""
from pathlib import Path
import ast,json,hashlib,shutil,tempfile

HERE=Path(__file__).resolve().parent
source=(HERE/'production_playtest.py').read_text()
tree=ast.parse(source);prefix=[]
for node in tree.body:
    if isinstance(node,ast.With):break
    prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(HERE/'production_playtest.py'),'exec'),globals())
OUT=ROOT/'output/qa/behavior-quality-native';OUT.mkdir(parents=True,exist_ok=True)
required=['rf_subject_x','rf_subject_y','rf_behavior_clock','rf_wedged','rf_bonus_disturbed']
missing=[name for name in required if not re.search(r'DEF _'+name+r' 0x([0-9a-fA-F]+)',noi)]
if missing:raise SystemExit('Native quality integration is not in the selected ROM yet; rebuild before running this acceptance test. Missing symbols: '+', '.join(missing))
SYMS={name:symbol(name) for name in required}
FAMILY_IDS={'protected':0,'freeze':1,'wedge':2,'glide':3,'hop':4,'push_up':5,
            'slow_walk':6,'dash_settle':7,'water_emerge':8,'night_peek':9,'natural_display':10,'rain_arrival':11}
records=[]

def signed(v):return v-256 if v>=128 else v
def observed():
    sid=value(6);period=species[sid].get('behavior_params',{}).get('period',90)
    clock=word(SYMS['rf_behavior_clock'])
    return {'species':sid,'screen':screen(),'focus':value(7),'distance':value(8),
            'aim':signed(value(9)),'stress':value(10),'score':value(11),
            'x':signed(pb.memory[SYMS['rf_subject_x']]),'y':signed(pb.memory[SYMS['rf_subject_y']]),
            'motion':pb.memory[MOTION],'hidden':pb.memory[HIDDEN],
            'wedged':pb.memory[SYMS['rf_wedged']], 'disturbed':pb.memory[SYMS['rf_bonus_disturbed']],
            'clock':clock,'cycle':(clock//period)&3,'period':period}

def wait_for(label,predicate,limit=16000):
    start=frames
    while frames-start<limit:
        state=observed()
        if predicate(state):
            check(label+' reached through bounded native waiting',True)
            return state
        if screen()!=4:check(label+' remains in camera',False)
        tick(2)
    check(label+' reachable within native frame budget',False)

def visible_window(s):
    return not s['hidden'] and not s['wedged'] and 16<s['clock']%s['period']<s['period']-16

def aim_to(target):
    for _ in range(8):
        at=signed(value(9))
        if at==target:return
        press('right' if at<target else 'left',2)
        check('harmless camera framing leaves stress zero',value(10)==0)
    check('camera aim target reached',signed(value(9))==target)

def open_subject(site):
    check('start subject from hiking screen',screen()==2)
    travel(site['room_id']);rest_to(next(i for i in range(3) if site['phase_mask']&(1<<i)));face(site)
    for _ in range(3):
        press('a',150)
        if screen()==3:break
        check('eligible observation retry remains on trail',screen()==2)
        if site['interaction_type'] in (0,5):press('b',150)
    check('bounded legal encounter opens chosen species',screen()==3 and value(6)==site['species_id'])
    press('a',20)
    # Explorer camera-ready gesture runs before the camera's blocking draw.
    # Wait through actual controller entry, then finish its visible UI render.
    start=frames
    while screen()!=4 and frames-start<180:tick(1)
    check('quality camera opens within bounded native gesture',screen()==4)
    tick(40)
    check('quality camera stays open after its initial draw',screen()==4)
    check('each new camera starts safe distance4 and calm',value(8)==4 and value(10)==0)
    check('new encounter resets persistent disturbed flag',pb.memory[SYMS['rf_bonus_disturbed']]==0)

def shutter(label,expected):
    before=observed();press('a',150)
    (OUT/'last-shutter.json').write_text(json.dumps({'label':label,'before':before,'after':observed(),'expected':expected},indent=2)+'\n')
    check(label+' result arrives after full save settle',screen()==5)
    check(label+' exact new-photo star result',value(11)==expected)
    check(label+' species record exists',best(before['species'])>0)
    snapshot(label);records.append({'label':label,'before':before,'result_stars':value(11)})

def return_trail(site):
    press('b',150);check('photo return restores hiking',screen()==2)
    if site['interaction_type'] in (0,5):press('b',150)

def natural_window(family,s):
    if not visible_window(s) or s['focus']<60 or s['stress'] or s['disturbed'] or s['aim']!=s['x']:return False
    if family in ('protected','freeze'):return True
    if family=='wedge':return s['clock']>=s['period']
    if family=='glide':return s['x']!=0
    if family=='hop':return s['y']<0
    if family=='push_up':return bool(s['motion'])
    if family in ('slow_walk','rain_arrival'):return s['x']!=0 and bool(s['motion'])
    if family=='dash_settle':return s['clock']>=s['period'] and s['cycle']==3
    if family=='water_emerge':return s['cycle']==2 and s['y']<0
    if family=='night_peek':return s['cycle']==2 and s['x']!=0
    if family=='natural_display':return s['y']<0
    raise AssertionError(family)

representatives={}
for row in species:
    family=row['behavior']
    if family not in FAMILY_IDS or family in representatives:continue
    site=next((s for s in sites if s['species_id']==row['id'] and s['species_id']!=150),None)
    if site:representatives[family]=site
assert set(representatives)==set(FAMILY_IDS),'Every shipped behavior family must have a legal representative'
with tempfile.TemporaryDirectory(prefix='rockflip-behavior-quality-') as tmp:
    testrom=Path(tmp)/ROM.name;shutil.copy2(ROM,testrom)
    pb=PyBoy(str(testrom),window='null',sound_emulated=False);pb.set_emulation_speed(0);tick(180)
    enter_hike();check('fresh cartridge enters hiking',screen()==2)
    for family in FAMILY_IDS:
        site=representatives[family];open_subject(site)
        aim_to(-3)
        state=wait_for(family+' baseline focus',lambda s:s['focus']==60 and visible_window(s))
        check(family+' baseline is safe but deliberately offcenter',state['distance']==4 and state['x']!=state['aim'])
        shutter(family+'-baseline',2);return_trail(site)
        open_subject(site)
        # Real camera controls, observed before45focus could mask a stress bug.
        press('left',2);check(family+' framing left is harmless',value(10)==0)
        press('right',2);check(family+' framing right is harmless',value(10)==0)
        press('down',2);check(family+' actual closer approach is available',value(8)==3)
        prior=value(10);press('up',2)
        check(family+' backing off returns distance4',value(8)==4)
        check(family+' backing away does not add stress',value(10)<=prior)
        target=1 if family in ('glide','hop','slow_walk','night_peek','rain_arrival') else 0
        # Existing stress from the one actual approach clears through patience,
        # then framing remains harmless. It must not trigger defensive behavior.
        wait_for(family+' calm after harmless spacing',lambda s:s['focus']==60 and not s['stress'] and visible_window(s))
        aim_to(target)
        state=wait_for(family+' natural calm moment',lambda s:natural_window(family,s))
        check(family+' natural bonus keeps distance4',state['distance']==4)
        shutter(family+'-natural',3);return_trail(site)
    # Deliberate bad approach is a negative QA action, never a rewarded task.
    site=representatives['wedge'];open_subject(site)
    for _ in range(12):
        if pb.memory[SYMS['rf_wedged']]:break
        if value(8)==2:press('up',2)
        press('down',2)
    check('actual repeated approach triggers defensive wedge',pb.memory[SYMS['rf_wedged']]>0)
    check('defensive wedge marks encounter permanently disturbed',pb.memory[SYMS['rf_bonus_disturbed']]==1)
    while value(8)<4:press('up',2)
    aim_to(0)
    wait_for('wedged animal recovers calmly',lambda s:s['focus']==60 and visible_window(s))
    check('recovery does not erase provocation history',pb.memory[SYMS['rf_bonus_disturbed']]==1)
    shutter('wedge-provoked-recovery',2);check('provocation cannot replace calm3star record',best(site['species_id'])==3);return_trail(site)
    # Hidden natural phase blocks the shutter, even for an already-seen species.
    site=representatives['water_emerge'];open_subject(site)
    wait_for('natural hiding phase',lambda s:s['hidden'] and s['cycle']==1 and s['period']-(s['clock']%s['period'])>24)
    prior_best=best(site['species_id']);prior_count=value(12);before=observed();press('a',150)
    check('hidden shutter remains in camera',screen()==4)
    check('hidden shutter cannot improve record or count',best(site['species_id'])==prior_best and value(12)==prior_count)
    records.append({'label':'hidden-shutter-rejected','before':before,'record_unchanged':True});snapshot('hidden-shutter-rejected')
    press('b',150);check('hidden observation can leave safely',screen()==2)
    if site['interaction_type'] in (0,5):press('b',150)
    # Unsafe distance is prevented by controller clamping, not injected RAM.
    site=representatives['protected'];open_subject(site)
    minimum=species[site['species_id']].get('behavior_params',{}).get('minimum_distance',2)
    for _ in range(8):
        press('down',2);check('protected approach never crosses minimum distance',value(8)>=minimum)
    check('unsafe camera state is unreachable by repeated approach',screen()==4 and value(8)==minimum)
    while value(8)<4:press('up',2)
    wait_for('protected safe recovery',lambda s:s['focus']==60 and visible_window(s))
    shutter('protected-safe-clamp',3);return_trail(site)
    pb.stop()
report={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'frames':frames,'inputs':inputs,'family_count':len(FAMILY_IDS),'representative_sites':{k:v['spot_id'] for k,v in representatives.items()},'observations':records,'memory_writes':False,'unsafe_controller_evidence':'RepeatedDOWN cannot reach below-minimum camera distance; no unsafe state injected. Hidden native shutter explicitly rejects. PureC host test separately rejects unsafe observations.','scope':'Native button-earned2/3star behavior pairs, calm/provoked wedge, harmlessframing/backoff, hidden rejection, safe-distance clamp. Human fun/audio and physical cartridge notapproved.'}
(OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['result','assertions','family_count','frames','rom_sha256']},indent=2))
