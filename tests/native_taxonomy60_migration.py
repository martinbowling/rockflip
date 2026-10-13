"""Controller-earned old ID60 boa save -> current ID59; fresh ID60 kingsnake.

Only temporary cartridge copies and owned evidence files are written. No
emulator photo/quest writes or canonical ROM/source edits occur.
"""
from pathlib import Path
import json,hashlib,shutil,tempfile
from native_snapshot_migration import harness,open_rom,resume,save_once,latest,FIXTURE,SOURCE_SHA,BASE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/qa/native-taxonomy60-migration';OUT.mkdir(parents=True,exist_ok=True)
OLDROM=ROOT/'output/qa/native-snapshot-migration/schema1-source.gbc'
OLDNOI=ROOT/'output/qa/native-snapshot-migration/schema1-source.noi'
NEWROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
NEWNOI=Path(str(NEWROM)+'.debug/symbols.noi')
NEW_SHA=hashlib.sha256(NEWROM.read_bytes()).hexdigest()

def read(h,off,n):return bytes(h['pb'].memory[h['RF']+off:h['RF']+off+n])
def photo(h,site,sid,phase):
    h['travel'](site['room_id']);h['rest_to'](phase);h['face'](site);h['press']('a',100)
    h['check']('actual encounter has intended native identity',h['screen']()==3 and h['value'](6)==sid)
    h['press']('a');h['check']('actual camera opens',h['screen']()==4)
    for _ in range(160):
        h['tick'](6)
        if h['value'](7)>=45 and not h['pb'].memory[h['HIDDEN']]:
            h['press']('a',150)
            if h['screen']()in(2,5) and h['best'](sid)>=2:break
    h['check']('controller photo really earns guide score',h['screen']()in(2,5) and h['best'](sid)>=2)
    h['snapshot']('old-boa-photo'if sid==60 and h['value'](1)==154 else'fresh-kingsnake-photo')
    if h['screen']()==5:h['press']('b')
    if site['interaction_type']in(0,5):h['press']('b')
    h['check']('photography leaves native trail',h['screen']()==2)

def main():
    assert hashlib.sha256(OLDROM.read_bytes()).hexdigest()==SOURCE_SHA
    assert hashlib.sha256(NEWROM.read_bytes()).hexdigest()==NEW_SHA,'Requires reviewed stable current ROM'
    h=harness(OLDROM,OLDNOI);h['OUT']=OUT
    with tempfile.TemporaryDirectory(prefix='rockflip-taxonomy60-')as tmp:
        oldpath=Path(tmp)/'old.gbc';shutil.copy2(OLDROM,oldpath);open_rom(h,oldpath,FIXTURE.read_bytes());resume(h)
        # Earn an actual nonzero opening task before the old boa photograph.
        photo(h,next(s for s in h['sites']if s['spot_id']==2),0,0)
        h['open_camp']();h['press']('up');h['check']('old actual opening journal',h['screen']()==13)
        h['press']('a');h['press']('a');h['press']('b');h['press']('start');h['check']('old first journal task filed',bool(h['flags']()[0]&1))
        h['press']('b');h['press']('b');h['press']('b')
        site=next(s for s in h['sites']if s['spot_id']==352);photo(h,site,60,1)
        h['check']('retained old ROM ID60 is separately photographed',h['best'](60)>0 and h['best'](59)==0)
        h['press']('select');h['check']('old photographed identity guide opens',h['screen']()==7)
        for _ in range((60-h['value'](14))%151):h['press']('right',25)
        h['press']('a');h['check']('old ID60 native species detail opens',h['screen']()==8 and h['value'](14)==60);h['snapshot']('old-60-species-detail');h['press']('b');h['press']('b')
        oldflags=h['flags']();oldspots=read(h,h['offset'](19),768);oldscore=h['best'](60)
        fields={i:read(h,h['offset'](i)+60*(2 if i==22 else 1),2 if i==22 else 1).hex()for i in(16,17,18,22)}
        save_once(h);oldsave=Path(str(oldpath)+'.ram').read_bytes();old=latest(oldsave)
        h['check']('genuine old save is schema1 size2256',old['schema']==1 and old['size']==2256)
        fixture=OUT/'controller-earned-old-60.ram';fixture.write_bytes(oldsave)
        capture={'checks':h['checks'],'inputs':h['inputs'],'score60':oldscore,'photo_fields':fields,'quest_flags':oldflags,'fixture_sha256':hashlib.sha256(oldsave).hexdigest()}
        h=harness(NEWROM,NEWNOI);h['OUT']=OUT;newpath=Path(tmp)/'new.gbc';shutil.copy2(NEWROM,newpath);open_rom(h,newpath,oldsave)
        h['check']('old boa photo merged to canonical59',h['best'](59)==oldscore)
        h['check']('new kingsnake60 not falsely discovered',h['best'](60)==0)
        h['check']('merged boa has unknown legacy pose',h['pb'].memory[h['RF']+2256+59]==0 and h['pb'].memory[h['RF']+2256+60]==0)
        for i,v in fields.items():h['check']('old boa metadata follows identity59 field'+str(i),read(h,h['offset'](i)+59*(2 if i==22 else 1),2 if i==22 else 1).hex()==v)
        for i in(16,17,18,22):h['check']('old60 metadata cleared field'+str(i),not any(read(h,h['offset'](i)+60*(2 if i==22 else 1),2 if i==22 else 1)))
        now=h['flags']();expected=oldflags[:];expected[9]|=64
        h['check']('quest evidence preserved except revision marker',now==expected)
        h['check']('all existing site evidence preserved',read(h,h['offset'](19),768)==oldspots)
        resume(h);save_once(h);newsave=Path(str(newpath)+'.ram').read_bytes();new=latest(newsave)
        h['check']('taxonomy migration saves schema2 size2448',new['schema']==2 and new['size']==2448)
        h['check']('migration preserves selected verified oldslot',newsave[BASE+old['slot']*4096:BASE+(old['slot']+1)*4096]==old['bytes'])
        open_rom(h,newpath,newsave);h['check']('cold merged identity59 persists',h['best'](59)==oldscore and h['best'](60)==0);resume(h)
        site=next(s for s in h['sites']if s['species_id']==60);photo(h,site,60,0)
        h['check']('fresh current kingsnake obtains known own pose',bool(h['pb'].memory[h['RF']+2256+60]&128))
        h['check']('new60 photograph retains migrated boa59',h['best'](59)==oldscore and h['best'](60)>0)
        newscore=h['best'](60);pose=h['pb'].memory[h['RF']+2256+60];save_once(h);fresh=Path(str(newpath)+'.ram').read_bytes();open_rom(h,newpath,fresh)
        h['check']('cold current kingsnake and oldboa remain distinct',h['best'](59)==oldscore and h['best'](60)==newscore and h['pb'].memory[h['RF']+2256+60]==pose);h['pb'].stop()
        result={'result':'pass','scope':'Actual controller-earned old60 boa photo migrates to59; quest/site evidence and oldslot retained; new60 kingsnake independently discovered and cold-saved. No progress injection.','old_rom_sha256':SOURCE_SHA,'rom_sha256':NEW_SHA,'capture':capture,'assertions':len(capture['checks'])+len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],'physical_hardware_verified':False}
        (OUT/'playtest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in('result','assertions','rom_sha256')},indent=2))
if __name__=='__main__':main()
