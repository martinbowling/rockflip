"""Actual RF02 schema1/2 -> current6 weather-photo migration through controller input.

Authentic prior fixtures only; no emulator progress writes. First save uses a
single START from the restored trail before any travel/camp helper can autosave.
Requires the root's new2544-byte forecast ROM and matching symbols.
"""
from pathlib import Path
import argparse,ast,json,hashlib,shutil,tempfile
from native_snapshot_migration import harness,open_rom,resume,latest,BASE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/qa/weather-migration-native'
FIX=ROOT/'output/weather-save/fixtures'
POSE=2256;CONDITIONS=2448;NEW=2544
TARGET_LAYOUT=3

def setup(rom,noi,quality=True):
    h=harness(rom,noi);h['OUT']=OUT
    if quality:
        names={'signed','observed','wait_for','visible_window','aim_to','open_subject','natural_window','shutter','return_trail'}
        tree=ast.parse((ROOT/'tests/native_behavior_quality.py').read_text())
        body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
        exec(compile(ast.Module(body=body,type_ignores=[]),str(ROOT/'tests/native_behavior_quality.py'),'exec'),h)
        h['SYMS']={n:h['symbol'](n)for n in['rf_subject_x','rf_subject_y','rf_behavior_clock','rf_wedged','rf_bonus_disturbed']};h['records']=[]
    return h

def read(h,offset,count):return bytes(h['pb'].memory[h['RF']+offset:h['RF']+offset+count])
def snapshot(h,sid):return h['pb'].memory[h['RF']+POSE+sid]
def conditions(h,sid):
    v=h['pb'].memory[h['RF']+CONDITIONS+(sid>>1)];return v>>4 if sid&1 else v&15

def check(h,label,ok):h['check'](label,ok)
def line(h,y):return ''.join(chr(v+32)for v in h['pb'].memory[0,0x9800+y*32:0x9800+y*32+20]).rstrip()
def first_save(h):
    h['press']('start',150);check(h,'single first START opens camp or fieldpack',h['screen']()in(9,25));h['pb'].stop()
def save_from_trail(h):
    if h['screen']()!=2:h['press']('b',150)
    first_save(h)

def choose(h,phase,weather,season,cancel=False):
    h['open_camp']();before=h['flags']()[9];before_phase=h['value'](4)
    h['press']('a',150);check(h,'physical camp opens forecast27',h['screen']()==27)
    for name,target,size,expected_field in [('rf_forecast_phase',phase,3,0),('rf_forecast_weather',weather,4,1),('rf_forecast_season',season,4,2)]:
        field=h['symbol']('rf_forecast_field')
        for _ in range((expected_field-h['pb'].memory[field])%3):h['press']('down',25)
        at=h['pb'].memory[h['symbol'](name)]
        for _ in range((target-at)%size):h['press']('right',25)
        check(h,'forecast chosen '+name,h['pb'].memory[h['symbol'](name)]==target)
    h['press']('b'if cancel else'a',150)
    if cancel:
        check(h,'forecast cancel returns camp without selectionchange',h['screen']()==9 and h['flags']()[9]==before and h['value'](4)==before_phase);h['press']('b',150)
    else:
        check(h,'forecast commits hike phase and nibble',h['screen']()==2 and h['value'](4)==phase and ((h['flags']()[9]>>1)&15)==weather+(season<<2))
        check(h,'forecast commit preserves quest9 otherbits',(h['flags']()[9]&~30)==(before&~30))

def album(h,sid,label,known):
    h['press']('select',150);check(h,'migrated guide opens throughinput',h['screen']()==7)
    for _ in range((sid-h['value'](14))%151):h['press']('right',25)
    h['press']('start',150);check(h,'migrated photo album opens',h['screen']()==10)
    text=' '.join(line(h,y)for y in range(18))
    if not known:check(h,'legacy condition label explicitlyunknown','UNKNOWN'in text or'NOT RECORDED'in text)
    else:check(h,'known condition album shows actualweather','FAIR'in text or'CLOUDY'in text or'RAIN'in text)
    h['snapshot'](label);h['press']('b',150);h['press']('b',150);check(h,'album returns hike',h['screen']()==2)

def retake(h,sid,wanted,phase,weather,season,label):
    choose(h,phase,weather,season)
    site=next(s for s in h['sites']if s['species_id']==sid)
    h['open_subject'](site);check(h,'retake starts safefourspaces',h['value'](8)==4)
    family=h['species'][sid]['behavior']
    if wanted==2:
        h['aim_to'](-3);state=h['wait_for'](label+' focused offcenter',lambda s:s['focus']==60 and h['visible_window'](s)and s['x']!=s['aim'])
    else:
        h['aim_to'](1 if family in('glide','hop','slow_walk','night_peek')else 0);state=h['wait_for'](label+' natural calm moment',lambda s:h['natural_window'](family,s))
    h['shutter'](label,wanted);h['return_trail'](site)
    check(h,'equal score keeps best and adds knownconditions',h['best'](sid)==wanted and snapshot(h,sid)&144==144)
    check(h,'retake stores exact chosen condition nibble',conditions(h,sid)==weather+(season<<2))
    return state

def old_reader(rom,noi,saved):
    h=setup(rom,noi,False)
    with tempfile.TemporaryDirectory(prefix='rockflip-weather-old-reader-')as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,saved)
        locked=h['symbol']('rf_store_locked');check(h,'old actualROM rejects newer committedlayout',bool(h['pb'].memory[locked]))
        h['enter_hike']();check(h,'old readonly reader canenter safehike',h['screen']()==2)
        h['press']('start',150);check(h,'old readonly pack/camp displays explicitnotice',h['screen']()in(9,25)and any('NEWER SAVE'in line(h,y)for y in range(18)))
        h['pb'].stop();check(h,'old actualROM cannotoverwrite eithernewrecord',Path(str(path)+'.ram').read_bytes()==saved)
    return {'result':'pass','reader_rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'checks':h['checks'],'inputs':h['inputs']}

CHALLENGE_FLAG_BYTES=[0,0,0,1,1,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5,5,5,5,6,6,6,6,6]
CHALLENGE_FLAG_MASKS=[32,64,128,64,128,32,64,128,4,8,16,32,64,128,4,8,16,32,64,128,2,4,8,16,32,64,128,8,16,32,64,128]
# Mask ONLY the newly claimed unused highbits+mode; every former bit is retained.
CHALLENGE_OLD_MASKS=[31,63,31,3,3,1,7,223,253]+[255]*23
def verify_legacy_challenge_awards(h,oldflags):
    actual=h['flags']();check(h,'old authenticated save retains original route mode0',not(actual[8]&2));expected=[b&m for b,m in zip(oldflags,CHALLENGE_OLD_MASKS)]
    records=json.loads((ROOT/'data/photo_challenges.json').read_text())['records']
    for r,b,m in zip(records,CHALLENGE_FLAG_BYTES,CHALLENGE_FLAG_MASKS):
        if h['best'](r['species_id'])>=3:expected[b]|=m
    expected[7]|=32
    check(h,'every preexisting allocated quest bit retained across layout6 migration',[b&m for b,m in zip(actual,CHALLENGE_OLD_MASKS)]==[b&m for b,m in zip(oldflags,CHALLENGE_OLD_MASKS)])
    check(h,'exactly32 former derived achievements seeded once plus mode marker',actual==expected)
    return list(actual)

def case(rom,noi,fixture,label,oldsize,oldscore):
    h=setup(rom,noi);original=fixture.read_bytes();old=latest(original);assert old and old['size']==oldsize and old['schema']==(1 if oldsize==2256 else 2)
    with tempfile.TemporaryDirectory(prefix='rockflip-weather-migration-')as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,original)
        check(h,'genuine oldfixture photograph survives',h['best'](5)==oldscore if oldsize==2256 else all(h['best'](r['species_id'])==3 for r in json.load(open(ROOT/'data/photo_challenges.json'))['records']))
        poses=read(h,POSE,192);check(h,'all96 legacy conditionbytes appendzero',read(h,CONDITIONS,96)==bytes(96));check(h,'alllegacy photos conditionflag unknown',all(not(v&16)for v in poses))
        if oldsize==2256:check(h,'schema1 retains unknown legacyposes',poses==bytes(192))
        else:check(h,'schema2 knownposes survive byteidentically',poses==old['payload'][POSE:CONDITIONS])
        # Observe persisted evidence before inputs; runtime may set only the
        # preexisting taxonomy revision bit6 during old-schema1 content migration.
        off=h['offset'](19);check(h,'old site evidence retained',read(h,off,1000)==old['payload'][off:off+1000]);q=h['offset'](23)+56;expected=bytearray(old['payload'][q:q+32]);expected[9]|=64
        migrated_awards=verify_legacy_challenge_awards(h,expected)
        resume(h);first_save(h);migrated=Path(str(path)+'.ram').read_bytes();new=latest(migrated)
        check(h,'first actualsave commits layout'+str(TARGET_LAYOUT)+' exact2544',new and new['schema']==TARGET_LAYOUT and new['size']==NEW)
        check(h,'first actualsave alternate slot nextsequence',new['slot']==old['slot']^1 and new['sequence']==(old['sequence']+1)%65536)
        check(h,'selected olderverifiedrecord preserved byteidentically',migrated[BASE+old['slot']*4096:BASE+(old['slot']+1)*4096]==old['bytes'])
        open_rom(h,path,migrated);check(h,'layout6 coldload keeps seeded awards exactly without re-derivation',h['flags']()==migrated_awards);check(h,'cold currentlayout legacyconditions stillunknown',read(h,CONDITIONS,96)==bytes(96));resume(h)
        album(h,5 if oldsize==2256 else 0,label+'-unknown',False)
        choose(h,0,3,3,True)
        if oldsize==2256:
            state=retake(h,5,oldscore,1,1,2,label+'-equal'+str(oldscore));ids=[5]
        else:
            before_neighbor=conditions(h,1);retake(h,0,3,0,0,2,label+'-even0');check(h,'even write preserves oddneighbor',conditions(h,1)==before_neighbor)
            before_neighbor=conditions(h,12);retake(h,13,3,0,1,3,label+'-odd13');check(h,'odd write preserves evenneighbor',conditions(h,12)==before_neighbor);ids=[0,13]
            check(h,'all32 existing challengephotos survive retakes',all(h['best'](r['species_id'])==3 for r in json.load(open(ROOT/'data/photo_challenges.json'))['records']))
        if oldsize==2448:
            check(h,'all untouched legacy poses remain exact',all(snapshot(h,sid)==poses[sid] for sid in range(192) if sid not in ids))
            check(h,'untouched legacy conditions remain unknown',all(not(snapshot(h,sid)&16) and conditions(h,sid)==0 for sid in range(192) if sid not in ids))
        retained={sid:{'pose':snapshot(h,sid),'conditions':conditions(h,sid),'score':h['best'](sid)}for sid in ids}
        for sid in ids:album(h,sid,label+'-known'+str(sid),True)
        save_from_trail(h);saved=Path(str(path)+'.ram').read_bytes();(OUT/(label+'-schema'+str(TARGET_LAYOUT)+'.ram')).write_bytes(saved);open_rom(h,path,saved)
        check(h,'cold knownconditions andposes survive',all(snapshot(h,sid)==v['pose']and conditions(h,sid)==v['conditions']and h['best'](sid)==v['score']for sid,v in retained.items()));
        if oldsize==2448:
            check(h,'cold all32 best records survive',all(h['best'](r['species_id'])==3 for r in json.load(open(ROOT/'data/photo_challenges.json'))['records']))
            check(h,'cold untouched poses stay byteidentical',all(snapshot(h,sid)==poses[sid] for sid in range(192) if sid not in ids))
            check(h,'cold untouched condition bytes stay unknown',all(conditions(h,sid)==0 and not(snapshot(h,sid)&16) for sid in range(192) if sid not in ids))
        h['pb'].stop()
    return {'label':label,'fixture_sha256':hashlib.sha256(original).hexdigest(),'result':'pass','assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],'retained_records':retained},saved

def main():
    global TARGET_LAYOUT
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--noi',type=Path);a=p.parse_args();noi=a.noi or Path(str(a.rom)+'.debug/symbols.noi');OUT.mkdir(parents=True,exist_ok=True)
    text=noi.read_text();TARGET_LAYOUT=6 if '_rf_campaign_variant_target' in text else 5 if '_rf_challenge_record' in text else 4 if '_rf_lens_ready' in text else 3;assert '_rf_conditions_current'in text,'New weatherROM is not built yet'
    cases=[]
    for fixture,label,size,score in[(FIX/'schema1-actual-2256.ram','schema1-equal2',2256,2),(FIX/'schema1-actual-score3.ram','schema1-equal3',2256,3),(FIX/'schema2-actual-challenges.ram','schema2-evenodd',2448,3)]:
        receipt,saved=case(a.rom,noi,fixture,label,size,score);cases.append(receipt)
    old=old_reader(FIX/'schema2-source.gbc',FIX/'schema2-source.noi',saved)
    report={'result':'pass','scope':'Actual controller-only cold RF02schema1/2->'+str(TARGET_LAYOUT)+', first alternate save, legacyunknown conditions, equal-score condition upgrades and retained actual old-ROM write protection','target_layout':TARGET_LAYOUT,'rom_sha256':hashlib.sha256(a.rom.read_bytes()).hexdigest(),'cases':cases,'old_reader':old,'assertions':sum(c['assertions']for c in cases)+len(old['checks']),'physical_hardware_verified':False,'progress_injected':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['result','assertions','rom_sha256']},indent=2))
if __name__=='__main__':main()
