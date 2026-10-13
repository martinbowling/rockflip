"""Integrated controller gallery proof, never writes gameplay RAM.
Requires newly built gallery symbols. Genuinely earns D01 before chapter0 is
complete; then reviews all16regions/32 authoritative saved photos using a
retained controller-earned complete-game SRAM fixture.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
import native_weather_migration as w
import campaign_native_driver as c
from native_snapshot_migration import open_rom,resume
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/qa/gallery-native';DATA=ROOT/'data/exhibit_gallery.json'
if not DATA.exists():DATA=ROOT/'output/exhibit-gallery/gallery.json'

def entries(h,data):return data['fresh_records']if h['flags']()[8]&2 else data['records']

def check(h,label,ok):h['check'](label,ok)
def stage(h,d):return (h['flags']()[10+d//4]>>((d%4)*2))&3
def state(h):return w.read(h,16,2544-16)
def open_gallery(h):
    
    try:h['travel'](0)
    except Exception:
        (OUT/'travel-diagnostic.json').write_text(json.dumps({'room':h['value'](1),'native_map_district':h['pb'].memory[h['symbol']('rf_map')+6],'atlas_selection':h['value'](21),'flags':h['flags'](),'inputs':h['inputs']},indent=2)+'\n');h['snapshot']('travel-failure');raise
    h['open_camp']();h['press']('left',150);check(h,'exhibit20 through actualcamp',h['screen']()==20)
    h['press']('select',150);check(h,'SELECT opens visualgallery33',h['screen']()==33)
def picture(h,sid,label):
    snap=w.snapshot(h,sid);distance=h['pb'].memory[h['RF']+h['offset'](16)+sid];aim=h['pb'].memory[h['RF']+h['offset'](17)+sid];aim=aim-256 if aim>=128 else aim
    side=4 if distance==4 and not snap&32 else 6;x=(8 if side==4 else 7)-aim;y=6 if side==4 else 5
    if snap&128:x+=(snap&3)-1;y+=((snap>>2)&1)-1
    check(h,label+' exact stored frame rectangle',all(h['pb'].memory[0,0x9800+(y+i//side)*32+x+i%side]==128+i for i in range(side*side)))
    h['snapshot'](label);return h['pb'].screen.image.crop((16,32,144,88)).tobytes()
def finish_d01(h):
    c.complete_opening(h)
    d=json.loads((ROOT/'data/campaign.json').read_text())['districts'][0]
    for st in d['stages']:
        for i in st['photo_target_indexes']:c.photo_target(h,d['photo_targets'][i])
        c._local_campaign(h,0);h['press']('a',150);check(h,'real D01caption18',h['screen']()==18)
        for _ in range(st['correct_choice']):h['press']('down',25)
        h['press']('a',150);h['press']('b',150);h['press']('start',150);check(h,'actual D01stage filed',stage(h,0)==st['stage_index']+1);h['press']('b',150);c.return_to_trail(h)
    check(h,'one actualfiledregion but incompletechapter',stage(h,0)==3 and all(stage(h,d)==0 for d in range(1,16)))
def partial(rom,noi):
    h=w.setup(rom,noi);h['OUT']=OUT
    with tempfile.TemporaryDirectory(prefix='rockflip-gallery-partial-')as tmp:
        path=Path(tmp)/rom.name;shutil.copyfile(rom,path);open_rom(h,path);resume(h);finish_d01(h);open_gallery(h)
        baseline=state(h);guide=h['value'](14);check(h,'chapterconclusion notawarded afterone region','FOUR STORIES CONNECT'not in w.line(h,14))
        h['press']('a',150);check(h,'filed first region displayed beforechapter complete','SAVED FIELD PHOTO'in w.line(h,3));picture(h,0,'first-filed-D01')
        h['press']('select',150);picture(h,entries(h,json.loads(DATA.read_text()))[0]['targets'][1]['species_id'],'first-filed-D01-compare')
        h['press']('right',150);check(h,'unfiled neighbor empty no inventedphoto','THIS FRAME IS EMPTY'in w.line(h,9))
        check(h,'browse keepsprogress andexactguide',state(h)==baseline and h['value'](14)==guide)
        h['press']('b',150);h['press']('b',150);check(h,'galleryreturns sameexhibit20',h['screen']()==20);h['press']('b',150);h['press']('b',150);w.save_from_trail(h)
        saved=Path(str(path)+'.ram').read_bytes();(OUT/'controller-earned-first-region.ram').write_bytes(saved);open_rom(h,path,saved);resume(h);open_gallery(h);h['press']('a',150);check(h,'coldfirst-region gallery remainsvisible','SAVED FIELD PHOTO'in w.line(h,3));picture(h,0,'cold-first-filed-D01');h['pb'].stop()
    result={'result':'pass','scope':'Actual controller-earned D01 becomes visible before chapter completion; neighbor remains empty; browsing preserves progress/guide and cold gallery survives. Full-gallery acceptance reported separately.','rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs']}
    (OUT/'first-region-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
def full(rom,noi,fixture):
    h=w.setup(rom,noi);h['OUT']=OUT;data=json.loads(DATA.read_text());original=fixture.read_bytes()
    with tempfile.TemporaryDirectory(prefix='rockflip-gallery-full-')as tmp:
        path=Path(tmp)/rom.name;shutil.copyfile(rom,path);open_rom(h,path,original);resume(h);open_gallery(h);base=state(h);guide=h['value'](14)
        for cluster in range(4):
            check(h,'actual four filed stories earnchapterconclusion','FOUR STORIES CONNECT'in w.line(h,14))
            for relative in range(4):
                d=cluster*4+relative;r=entries(h,data)[d];check(h,'native gallerydistrict selected',h['pb'].memory[h['symbol']('rf_gallery_district')]==d)
                h['press']('a',150);check(h,'region gallerycard34',h['screen']()==34)
                for pair in range(2):
                    sid=r['targets'][pair]['species_id'];check(h,'card reflects actualsavedphoto2orbetter',h['best'](sid)>=2 and 'SAVED FIELD PHOTO'in w.line(h,3));check(h,'originalmeaningfulregiontheme',w.line(h,12)==r['theme']);check(h,'originalrangerresponse',all(w.line(h,13+i)==r['response'][i]for i in range(2)))
                    savedmap=h['word'](h['RF']+h['offset'](22)+sid*2);check(h,'captionshowsactualsavedmapname',w.line(h,11)==h['world'][savedmap]['name'])
                    picture(h,sid,f'D{d+1:02d}-pair{pair}');check(h,'photo renderer restoresguide andallprogress',h['value'](14)==guide and state(h)==base)
                    if pair==0:h['press']('select',150)
                h['press']('b',150);h['press']('right',150)
            h['press']('down',150)
        h['press']('b',150);check(h,'browse returnexhibit unchangedpredicates',h['screen']()==20 and state(h)==base);h['press']('b',150);h['press']('b',150);w.save_from_trail(h)
        saved=Path(str(path)+'.ram').read_bytes();open_rom(h,path,saved);resume(h);open_gallery(h);check(h,'coldall16gallery chapters unchanged',all(stage(h,d)==3 for d in range(16)));h['press']('a',150);picture(h,entries(h,data)[0]['targets'][0]['species_id'],'cold-completed-D01');h['pb'].stop()
    return {'fixture_sha256':hashlib.sha256(original).hexdigest(),'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--noi',type=Path);p.add_argument('--legacy-save',type=Path,default=ROOT/'output/gallery-route-integration/fixtures/controller-earned-complete-5762-layout5.ram');p.add_argument('--full-save',type=Path,default=ROOT/'output/qa/lens-native/controller-earned-lens-layout5.ram');a=p.parse_args();noi=a.noi or Path(str(a.rom)+'.debug/symbols.noi');assert '_rf_gallery_begin'in noi.read_text(),'Integrated gallery is not built yet'
    OUT.mkdir(parents=True,exist_ok=True);w.OUT=OUT
    cases=[partial(a.rom,noi),full(a.rom,noi,a.full_save),full(a.rom,noi,a.legacy_save)];report={'result':'pass','scope':'Actual integrated controller-only firstfiledregion beforechapter completion plus all16regional pairs, exact savedpose/lens/frame/map and readonlybrowse, coldrestart. No perfect3star gate.','rom_sha256':hashlib.sha256(a.rom.read_bytes()).hexdigest(),'assertions':sum(x['assertions']for x in cases),'cases':cases,'progress_injected':False,'physical_hardware_verified':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['result','assertions','rom_sha256']},indent=2))
if __name__=='__main__':main()
