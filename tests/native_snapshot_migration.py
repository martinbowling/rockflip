"""Real-SRAM append-only pose migration and tie-upgrade controller regression.

Uses the root-owned production harness definitions without running its full
roster test. Fixtures are input-earned SRAM, never fabricated progress bytes.
--capture-schema1-score3 preserves a real score3 fixture from the prior ROM.
Default mode requires the new stable2448/schema2 ROM+matching NOI.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[1]
BASE=3*8192;OLD=2256;NEW=2448;SNAPSHOT=2256
OUT=ROOT/'output/qa/native-snapshot-migration'
FIXTURE=ROOT/'output/qa/save-native/rf02-schema1-2256.ram'
SOURCE_SHA='cf73d421941c91e82d507afe476695517403f8fe7ddf94840cdc6da2a92f23c1'

def crc16(data):
    crc=65535
    for value in data:
        crc^=value<<8
        for _ in range(8):crc=((crc<<1)^0x1021)&65535 if crc&0x8000 else (crc<<1)&65535
    return crc

def record(data,slot):
    b=data[BASE+slot*4096:BASE+(slot+1)*4096];size=int.from_bytes(b[6:8],'little')
    if len(b)!=4096 or b[:4]!=b'RF02' or b[4]!=2 or not 0<size<=4080:return None
    if crc16(b[:10]+b[12:16]+b[16:16+size])!=int.from_bytes(b[10:12],'little'):return None
    return {'slot':slot,'schema':b[5],'size':size,'sequence':int.from_bytes(b[8:10],'little'),'payload':b[16:16+size],'bytes':b}

def latest(data):
    a,b=record(data,0),record(data,1)
    if not a:return b
    if not b:return a
    return b if (b['sequence']-a['sequence'])%65536<=32768 else a

def harness(rom,noi):
    # The existing definitions do legal route walking, ferry confirmation and
    # file-free screen/value observation. Stop before its top-level ROM run.
    source=(ROOT/'tests/production_playtest.py').read_text().split('with tempfile.TemporaryDirectory',1)[0]
    source=source.replace("ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'",'ROM=Path('+repr(str(rom))+')')
    source=source.replace("noi=Path(str(ROM)+'.debug/symbols.noi').read_text()",'noi=Path('+repr(str(noi))+').read_text()')
    ns={'__file__':str(ROOT/'tests/production_playtest.py')};exec(compile(source,str(ROOT/'tests/production_playtest.py'),'exec'),ns)
    ns['OUT']=OUT;ns['checks']=[];ns['inputs']=[];ns['frames']=0
    ns['LEGACY_LINEAR_ROUTES']=hashlib.sha256(rom.read_bytes()).hexdigest()==SOURCE_SHA
    return ns

def open_rom(h,path,data=None):
    if data is not None:Path(str(path)+'.ram').write_bytes(data)
    h['pb']=h['PyBoy'](str(path),window='null',sound_emulated=False);h['pb'].set_emulation_speed(0);h['tick'](180)

def snap(h,sid=5):return h['pb'].memory[h['RF']+SNAPSHOT+sid]
def score(h,sid=5):return h['best'](sid)
def check(h,label,condition):h['check'](label,condition)
def resume(h):h['enter_hike']();check(h,'continue migrated native world',h['screen']()==2)
def save_once(h):
    h['press']('start',150);check(h,'one controller save opens pack orcamp',h['screen']() in(9,25))
    # stop emits the actual SRAM file without taking any further game input.
    h['pb'].stop()
def album(h,label):
    h['press']('select');check(h,'guide opens for saved photo',h['screen']()==7)
    for _ in range((5-h['value'](14))%151):h['press']('right',25)
    h['press']('start');check(h,'actual saved-photo album opens',h['screen']()==10);h['snapshot'](label)
    h['press']('b');h['press']('b');check(h,'album returns to native trail',h['screen']()==2)

def retake(h,wanted):
    site=next(s for s in h['sites'] if s['spot_id']==0)
    h['travel'](0);h['rest_to'](1);h['face'](site)
    # Actual cover opening/restoration plus bounded eligible lookup recovery.
    for _ in range(3):
        h['press']('a',100)
        if h['screen']()==3:break
        h['press']('b')
    check(h,'native kingsnake encounter for tie test',h['screen']()==3 and h['value'](6)==5)
    h['press']('a');check(h,'native retake viewfinder',h['screen']()==4)
    new_quality='DEF _rf_bonus_disturbed ' in h['noi']
    if wanted==3:
        h['press']('down',20) # Preserve the prior distance3 photo composition.
        if new_quality:h['press']('right',20) # Frame the natural moving glide.
    sx=h['symbol']('rf_subject_x')
    for _ in range(240):
        h['tick'](2)
        x=h['pb'].memory[sx];x=x-256 if x>=128 else x
        aim=h['value'](9);aim=aim-256 if aim>=128 else aim
        center=x==aim
        if wanted==3 and new_quality:center=center and x!=0
        if h['value'](7)>=(60 if wanted==3 and new_quality else 45) and center==(wanted==3) and not h['pb'].memory[h['HIDDEN']]:
            h['press']('a',150)
            if h['screen']() in {2,5} and h['value'](11)==wanted and score(h)==wanted:break
    check(h,'input-earned requested photo score',h['screen']() in {2,5} and h['value'](11)==wanted and score(h)==wanted)
    if h['screen']()==5:h['press']('b')
    h['press']('b');check(h,'retake restored stone and trail',h['screen']()==2)

def capture_schema1(rom,noi):
    checksha=hashlib.sha256(rom.read_bytes()).hexdigest();assert checksha==SOURCE_SHA,'Prior-ROM capture requires exact documentedcf73d4 artifact'
    h=harness(rom,noi)
    with tempfile.TemporaryDirectory(prefix='rockflip-pose-old-') as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,FIXTURE.read_bytes());resume(h);retake(h,3);save_once(h)
        data=Path(str(path)+'.ram').read_bytes();r=latest(data)
        assert r and r['schema']==1 and r['size']==OLD
        check(h,'score3 is genuinely earned in prior schema1 ROM',r['payload'][h['offset'](15)+5]==3)
        fixture=OUT/'rf02-schema1-score3.ram';fixture.write_bytes(data)
    report={'result':'pass','scope':'prior_native_ROM_controller_earned_schema1_score3_fixture','rom_sha256':checksha,'fixture':str(fixture),'fixture_sha256':hashlib.sha256(data).hexdigest(),'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs']}
    (OUT/'score3-capture.json').write_text(json.dumps(report,indent=2)+'\n');return report

def migration_case(rom,noi,fixture,wanted,label):
    original=fixture.read_bytes();old=latest(original);assert old and old['schema']==1 and old['size']==OLD
    h=harness(rom,noi)
    with tempfile.TemporaryDirectory(prefix='rockflip-pose-migration-') as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,original)
        check(h,'old actual photo survives cold native migration',score(h)==wanted and h['value'](12)>=1)
        check(h,'unknown old photo pose is zero',snap(h)==0)
        check(h,'all192 migrated photo poses begin unknown',all(h['pb'].memory[h['RF']+SNAPSHOT+i]==0 for i in range(192)))
        check(h,'old native scene phase and points preserved',h['value'](4)==old['payload'][h['offset'](4)] and h['value'](13)==old['payload'][h['offset'](13)])
        # First single explicit save must target the opposite slot.
        resume(h);save_once(h);migrated=Path(str(path)+'.ram').read_bytes();new=latest(migrated)
        check(h,'first native migration commits schema2 size2448',bool(new) and new['schema']==2 and new['size']==NEW)
        check(h,'first native save chooses opposite verified slot',new['slot']==(old['slot']^1) and new['sequence']==(old['sequence']+1)%65536)
        check(h,'selected prior2256record preserved byte-identically',migrated[BASE+old['slot']*4096:BASE+(old['slot']+1)*4096]==old['bytes'])
        check(h,'first saved snapshots retain unknown zero',new['payload'][SNAPSHOT:NEW]==bytes(192))
        open_rom(h,path,migrated);check(h,'cold schema2 record retains photo and unknownpose',score(h)==wanted and snap(h)==0);resume(h);album(h,label+'-legacy-unknown')
        oldscore=score(h);retake(h,wanted)
        check(h,'equal-score retake preserves bestscore',score(h)==oldscore)
        check(h,'equal-score native retake upgrades unknownpose',bool(snap(h)&128) and not(snap(h)&112))
        packed=snap(h);photophase=h['pb'].memory[h['RF']+h['offset'](18)+5];photomap=h['word'](h['RF']+h['offset'](22)+5*2)
        album(h,label+'-pose-known');save_once(h);known=Path(str(path)+'.ram').read_bytes();open_rom(h,path,known)
        check(h,'actual cold snapshot byte survives',snap(h)==packed and score(h)==wanted)
        check(h,'cold photo phase/map metadata survive',h['pb'].memory[h['RF']+h['offset'](18)+5]==photophase and h['word'](h['RF']+h['offset'](22)+5*2)==photomap)
        h['pb'].stop()
    return {'fixture':str(fixture),'fixture_sha256':hashlib.sha256(original).hexdigest(),'score':wanted,'result':'pass','assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],'snapshot_byte':packed,'pose_fields':{'known':bool(packed&128),'subject_x':(packed&3)-1,'subject_y':((packed>>2)&1)-1,'motion_frame':(packed>>3)&1}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--noi',type=Path);p.add_argument('--capture-schema1-score3',action='store_true');args=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);noi=args.noi or Path(str(args.rom)+'.debug/symbols.noi')
    if args.capture_schema1_score3:report=capture_schema1(args.rom,noi)
    else:
        assert hashlib.sha256(args.rom.read_bytes()).hexdigest()!=SOURCE_SHA,'New2448schema2ROM is not built yet; preserve prior fixture and wait for stable new build'
        cases=[migration_case(args.rom,noi,FIXTURE,2,'equal2'),migration_case(args.rom,noi,OUT/'rf02-schema1-score3.ram',3,'equal3')]
        report={'result':'pass','scope':'actual_native_SRAMPyBoy_cold_schema1_to_schema2_and_controller_equal_score_snapshot_upgrade','rom_sha256':hashlib.sha256(args.rom.read_bytes()).hexdigest(),'assertions':sum(x['assertions'] for x in cases),'cases':cases,'physical_hardware_verified':False}
        (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['result','assertions','rom_sha256']},indent=2))
if __name__=='__main__':main()
