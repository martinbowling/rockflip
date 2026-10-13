"""Earn old positions by walking; cold-load new terrain without progress writes."""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
from native_snapshot_migration import harness,open_rom,latest
from native_weather_migration import verify_legacy_challenge_awards
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'output/build-candidates/RockFlip-Statewide-9471.gbc'
NEW=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
OUT=ROOT/'output/qa/landmark-migration-native'
BASE=ROOT/'output/qa/controller-earned-151-9471.ram'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    oldworld={m['id']:m for m in json.loads((ROOT/'output/level-landmarks/world-original.json').read_text())['maps']}
    repairs=json.loads((ROOT/'output/level-landmarks/legacy-standing-repairs.json').read_text())['repairs']
    candidates=[next(r for r in repairs if oldworld[r['map']]['district_id']==f'D{d+1:02d}' and r['old_path_distance']is not None)for d in range(16)]
    fixtures=[]
    with tempfile.TemporaryDirectory(prefix='rockflip-old-standing-')as tmp:
        for i,r in enumerate(candidates):
            dest=OUT/f'district-{i:02d}-old.ram'
            if not dest.exists():
                h=harness(OLD,Path(str(OLD)+'.debug/symbols.noi'));h['world']=oldworld;h['OUT']=OUT
                path=Path(tmp)/f'old-{i}.gbc';shutil.copy2(OLD,path);open_rom(h,path,BASE.read_bytes())
                h['enter_hike']();h['travel'](r['map']);h['walk'](*r['old_standing'])
                h['press']('start',150);h['check']('old save controller at exact changed terrain',h['value'](1)==r['map']and[h['value'](2),h['value'](3)]==r['old_standing'])
                h['pb'].stop();shutil.copy2(Path(str(path)+'.ram'),dest)
                (OUT/f'district-{i:02d}-old-inputs.json').write_text(json.dumps({'rom_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'inputs':h['inputs'],'checks':h['checks']},indent=2)+'\n')
            fixtures.append({'repair':r,'path':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    (OUT/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    if args.prepare_only:print('Prepared16 genuine controller-earned old-position saves.');return
    checks=[];inputs=[]
    with tempfile.TemporaryDirectory(prefix='rockflip-new-standing-')as tmp:
        for i,f in enumerate(fixtures):
            old=Path(f['path']).read_bytes();payload=bytearray(latest(old)['payload'])
            h=harness(NEW,Path(str(NEW)+'.debug/symbols.noi'));h['OUT']=OUT
            path=Path(tmp)/f'new-{i}.gbc';shutil.copy2(NEW,path);open_rom(h,path,old)
            r=f['repair'];h['check']('cold old-position repair exact',h['value'](1)==r['map']and[h['value'](2),h['value'](3)]==r['new_standing'])
            # Layout6 keeps the old route mode and migrates earlier challenge awards. Verify the exact
            # once-only award migration before comparing every other byte.
            q=h['offset'](23)+56
            seeded=verify_legacy_challenge_awards(h,list(payload[q:q+32]))
            payload[q:q+32]=bytes(seeded)
            # Only presentation resets and x/y relocation remain permitted.
            actual=bytearray(h['pb'].memory[h['RF']:h['RF']+2544])
            for slot in (0,2,3,5,14):
                at=h['offset'](slot);actual[at]=payload[at]
            h['check']('old-position repair preserves complete progress and photo payload',actual==payload)
            h['enter_hike']();h['check']('repaired tile actually walkable',not h['blocked'](r['map'],h['value'](2),h['value'](3)))
            h['snapshot'](f'district-{i:02d}-repaired');h['press']('start',150);h['pb'].stop()
            saved=Path(str(path)+'.ram').read_bytes();open_rom(h,path,saved)
            h['check']('repair persisted and idempotent after secondcold',h['value'](1)==r['map']and[h['value'](2),h['value'](3)]==r['new_standing'])
            h['check']('migrated awards persist exactly without cold re-derivation',h['flags']()==seeded)
            h['pb'].stop(save=False)
            checks.extend(h['checks']);inputs.append(h['inputs'])
    report={'result':'pass','rom_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),'old_rom_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'fixtures':fixtures,'inputs':inputs,'progress_memory_writes':False,'physical_hardware_verified':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in('result','assertions','rom_sha256')}))
if __name__=='__main__':main()
