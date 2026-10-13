"""Controller-earned field lens and authentic RF02 layout3 ->6 regression.

Run only after root builds matching lens ROM/NOI. Genuine c66c fixtures, read
only observations, no memory progress writes. Existing weather migration suite
separately retains actual layout1/2 -> current6 coverage.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
import native_weather_migration as w
from native_snapshot_migration import open_rom,resume,latest,BASE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/qa/lens-native';FIX=ROOT/'output/lens-production/fixtures'

def check(h,label,ok):h['check'](label,ok)
def setup(rom,noi):
    h=w.setup(rom,noi);h['OUT']=OUT;return h

def portrait_cells(h):
    # Portrait is authored in VRAM bank1, BG palette5: attribute13. Bank is
    # changed only through CPU execution; PyBoy observations are read-only.
    # Tile indices128..163 in photo rectangle count drawn 4x4 or6x6 cells.
    return sum(128<=h['pb'].memory[0x9800+y*32+x]<=163 for y in range(4,11)for x in range(2,18))

def toggle(h,earned,active):
    before=h['flags']();distance=h['value'](8);stress=h['value'](10)
    h['press']('select',2)
    check(h,'SELECT preserves safe distance and stress',h['value'](8)==distance and h['value'](10)==stress)
    expected=before.copy();expected[9]^=32 if earned else 0
    check(h,'SELECT modifies only earned preferencebit5',h['flags']()==expected)
    check(h,'transient lens follows earned toggle',h['pb'].memory[h['symbol']('rf_lens_active')]==active)
    if earned:check(h,'lens change resets focus without approach',h['value'](7)<45)
    else:check(h,'locked lens explains chapter requirement','FILE A CHAPTER FIRST' in w.line(h,13))
    h['tick'](150)

def photo(h,sid,wanted,lens,label):
    site=next(s for s in h['sites']if s['species_id']==sid)
    h['open_subject'](site)
    if bool(h['pb'].memory[h['symbol']('rf_lens_active')])!=bool(lens):toggle(h,True,lens)
    check(h,'safe framing starts at distance4',h['value'](8)==4)
    family=h['species'][sid]['behavior']
    target=1 if family in('glide','slow_walk','rain_arrival','night_peek')else 0
    h['aim_to'](-3 if wanted==2 else target)
    if wanted==3:state=h['wait_for'](label,lambda s:h['natural_window'](family,s))
    else:state=h['wait_for'](label,lambda s:s['focus']==60 and h['visible_window'](s)and s['x']!=s['aim'])
    h['snapshot'](label+'-camera')
    # Exact portrait composition is tested below via camera/album pixel region;
    # background graphics can also use high tile IDs, so no count-only proof.
    h['shutter'](label,wanted);h['return_trail'](site)
    check(h,'photo never uses approach for fieldlens',state['distance']==4 and not state['stress']and not state['disturbed'])
    return state

def view(h,sid,label,mode):
    h['press']('select',150);check(h,'guide opened',h['screen']()==7)
    for _ in range((sid-h['value'](14))%151):h['press']('right',25)
    h['press']('start',150);check(h,'stored photo album opened',h['screen']()==10)
    snap=w.snapshot(h,sid);distance=h['pb'].memory[h['RF']+h['offset'](16)+sid];side=4 if distance==4 and not snap&32 else 6
    aim=h['pb'].memory[h['RF']+h['offset'](17)+sid];aim=aim-256 if aim>=128 else aim
    x=(7 if side==6 else 8)-aim+(snap&3)-1
    y=(5 if side==6 else 6)+((snap>>2)&1)-1
    (OUT/'album-diagnostic.json').write_text(json.dumps({'sid':sid,'snapshot':snap,'distance':h['pb'].memory[h['RF']+h['offset'](16)+sid],'aim':aim,'x':x,'y':y,'side':side,'tile_rows':[[h['pb'].memory[0,0x9800+row*32+col]for col in range(20)]for row in range(4,11)]},indent=2)+'\n')
    check(h,'album uses saved lens dimension '+str(side),all(h['pb'].memory[0,0x9800+(y+i//side)*32+x+i%side]==128+i for i in range(side*side)))
    picture=h['pb'].screen.image.crop((16,32,144,88)).tobytes();h['snapshot'](label+'-album')
    h['press']('a',150);check(h,'album A opens recorded detail',h['screen']()==8)
    check(h,'detail retains all saved picturecells above label',all(h['pb'].memory[0,0x9800+(y+i//side)*32+x+i%side]==128+i for i in range(side*side)))
    check(h,'photographed label below image','PHOTOGRAPHED'in w.line(h,11))
    check(h,'detail and album saved picture same pixels',h['pb'].screen.image.crop((16,32,144,88)).tobytes()==picture)
    h['snapshot'](label+'-detail');h['press']('b',150);h['press']('b',150);check(h,'guide returns hike',h['screen']()==2)
    check(h,'current preference does not alter savedlens',bool(h['flags']()[9]&32)==bool(mode))
    return picture

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

def migration(rom,noi,name):
    original=(FIX/name).read_bytes();old=latest(original);assert old and old['schema']==3 and old['size']==2544
    h=setup(rom,noi)
    with tempfile.TemporaryDirectory(prefix='rockflip-lens-migration-')as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,original)
        check(h,'actual layout3 conditions and poses unchanged on load',w.read(h,2256,288)==old['payload'][2256:2544])
        check(h,'all photo scores survived layout3 load',w.read(h,h['offset'](15),192)==old['payload'][h['offset'](15):h['offset'](15)+192])
        off=h['offset'](19);check(h,'site evidence survives layout3 load',w.read(h,off,1000)==old['payload'][off:off+1000])
        q=h['offset'](23)+56;migrated_awards=verify_legacy_challenge_awards(h,old['payload'][q:q+32])
        resume(h);w.first_save(h);saved=Path(str(path)+'.ram').read_bytes();new=latest(saved)
        check(h,'first actualsave is layout6 exact2544',new and new['schema']==6 and new['size']==2544)
        check(h,'first layout6 save alternate nextsequence',new['slot']==old['slot']^1 and new['sequence']==(old['sequence']+1)%65536)
        check(h,'old verifiedlayout3 record preserved entire4096',saved[BASE+old['slot']*4096:BASE+(old['slot']+1)*4096]==old['bytes'])
        check(h,'all saved poses and conditions preserved at commit',new['payload'][2256:2544]==old['payload'][2256:2544])
        open_rom(h,path,saved);check(h,'layout6 coldload preserves exact legacy awards once',h['flags']()==migrated_awards);check(h,'cold layout6 poses and conditions unchanged',w.read(h,2256,288)==old['payload'][2256:2544]);h['pb'].stop()
        (OUT/(name.replace('.ram','')+'-layout6.ram')).write_bytes(saved)
    return {'fixture':name,'fixture_sha256':hashlib.sha256(original).hexdigest(),'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs']},saved

def locked(rom,noi):
    h=setup(rom,noi)
    with tempfile.TemporaryDirectory(prefix='rockflip-lens-locked-')as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,(FIX/'actual-condition-upgrades-c66c-schema3.ram').read_bytes());resume(h)
        check(h,'authentic unfiled fixture has no completedchapter',all(v!=255 for v in h['flags']()[10:14]))
        site=next(s for s in h['sites']if s['species_id']==0);h['open_subject'](site);toggle(h,False,0)
        h['aim_to'](0);h['wait_for']('locked normal safe photo',lambda s:h['natural_window']('protected',s));h['shutter']('locked-normal-3star',3);h['return_trail'](site)
        check(h,'locked ordinary safe three stars still achievable',h['best'](0)==3 and not w.snapshot(h,0)&32);h['pb'].stop()
    return {'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs']}

def earned(rom,noi):
    h=setup(rom,noi)
    with tempfile.TemporaryDirectory(prefix='rockflip-lens-earned-')as tmp:
        path=Path(tmp)/rom.name;shutil.copy2(rom,path);open_rom(h,path,(FIX/'actual-completed-c66c-schema3.ram').read_bytes());resume(h)
        check(h,'genuine completedchapter earns fieldlens',any(v==255 for v in h['flags']()[10:14]))
        photo(h,13,3,1,'initial-earned-lens');photo(h,13,3,0,'wide-three');check(h,'ordinary distance4 saved as32px',not w.snapshot(h,13)&32);wide=view(h,13,'wide',0)
        before=h['best'](13);photo(h,13,3,1,'fieldlens-equal-three');check(h,'equal3 upgrades lens metadata withoutscoreinflation',h['best'](13)==before==3 and w.snapshot(h,13)&32)
        detailed=view(h,13,'fieldlens',1);check(h,'fieldlens saved picture differs from ordinary32',detailed!=wide)
        retained=w.snapshot(h,13);nibble=w.conditions(h,13)
        for weather in range(4):
            for season in range(4):
                w.choose(h,0,weather,season);check(h,'all16 forecast commits preserve earned lensbit5',bool(h['flags']()[9]&32))
        w.choose(h,0,0,0,True);check(h,'forecast cancel preserves earned lensbit5',bool(h['flags']()[9]&32))
        photo(h,13,2,0,'lower-wide-two');check(h,'lower score cannotoverwrite lens photo',h['best'](13)==3 and w.snapshot(h,13)==retained and w.conditions(h,13)==nibble)
        retained_pixels=view(h,13,'stored-lens-preference-wide',0);check(h,'stored lens ignores current wide preference',retained_pixels==detailed)
        w.choose(h,0,2,1);check(h,'forecast preserves lens preferencebit5',not(h['flags']()[9]&32))
        photo(h,61,3,1,'shore-fieldlens');check(h,'marine lens uses safeshore distance4',h['pb'].memory[h['RF']+h['offset'](16)+61]==4 and w.snapshot(h,61)&32)
        view(h,61,'shore-fieldlens',1)
        poses=w.read(h,2256,288);flags=h['flags']();w.save_from_trail(h);saved=Path(str(path)+'.ram').read_bytes();(OUT/'controller-earned-lens-layout6.ram').write_bytes(saved);open_rom(h,path,saved)
        check(h,'cold saved lens preference survives',h['flags']()[9]==flags[9]);check(h,'all192 poses/96conditions coldsurvive',w.read(h,2256,288)==poses)
        resume(h);view(h,13,'cold-stored-lens',1);h['pb'].stop()
    return {'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs']},saved

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--noi',type=Path);a=p.parse_args();noi=a.noi or Path(str(a.rom)+'.debug/symbols.noi')
    assert '_rf_lens_ready'in noi.read_text(),'Lens-integrated ROM not yet built; no native proof recorded'
    OUT.mkdir(parents=True,exist_ok=True);w.OUT=OUT
    migrations=[migration(a.rom,noi,n)[0]for n in['actual-completed-c66c-schema3.ram','actual-condition-upgrades-c66c-schema3.ram']]
    locked_result=locked(a.rom,noi);earned_result,saved=earned(a.rom,noi)
    old=w.old_reader(FIX/'schema3-source.gbc',FIX/'schema3-source.noi',saved)
    report={'result':'pass','scope':'Controller-only authentic layout3->6, earned/locked lens, safe4 natural3stars, equal/lower-score metadata, authoritative stored album/detail, marine shore lens, cold save, old-layout3-reader failclosed','rom_sha256':hashlib.sha256(a.rom.read_bytes()).hexdigest(),'migration':migrations,'locked':locked_result,'earned':earned_result,'old_reader':old,'assertions':sum(c['assertions']for c in migrations)+locked_result['assertions']+earned_result['assertions']+len(old['checks']),'progress_injected':False,'physical_hardware_verified':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['result','assertions','rom_sha256']},indent=2))
if __name__=='__main__':main()
