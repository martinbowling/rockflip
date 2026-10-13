"""V07 exact native guide icon palette/register/raster and origin-return audit.
No RFState/progress writes. FF68 observational palette read selector is changed
and restored exactly, never writes FF69/color data. Uses frozen source icons
and genuine earned SRAM. Hardware selector touches explicitly disclosed.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,tempfile
from PIL import Image
import native_weather_migration as w
from native_snapshot_migration import open_rom,resume
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/qa/guide-palette-native';FREEZE=ROOT/'output/qa/release-63201c8b';ART_ROOT=ROOT/'art/out'

def check(h,label,ok):h['check'](label,ok)
def palettes(h):
    old=h['pb'].memory[0xFF68];raw=[]
    for index in range(64):
        h['pb'].memory[0xFF68]=index;raw.append(h['pb'].memory[0xFF69])
    h['pb'].memory[0xFF68]=old
    check(h,'FF68 read selector restored exactly',h['pb'].memory[0xFF68]==old)
    return [raw[i]+(raw[i+1]<<8)for i in range(0,64,2)]
def colors555(v):return ((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3)
def state(h):return w.read(h,16,2544-16)
def icons(h,full,label,manifest,species):
    h['press']('select',150);check(h,'paletteaudit guide opens',h['screen']()==7);baseline=state(h);all_pages=[]
    for page in range(26):
        wanted=page*6
        for _ in range((wanted-h['value'](14))%151):h['press']('right',25)
        check(h,'exact ALL page selection',h['value'](14)==wanted)
        hardware=palettes(h);image=h['pb'].screen.image.convert('RGB');page_records=[]
        for slot,sid in enumerate(range(wanted,min(wanted+6,151))):
            x=2+(slot%3)*6;y=3+(slot//3)*6
            if sid==150 and not full:
                check(h,'hidden undiscovered icon has no animaltiles',all(h['pb'].memory[0,0x9800+(y+k//2)*32+x+k%2]==31 for k in range(4)));continue
            art=manifest[species[sid]['art']];palette=[30+(29<<5)+(25<<10),*[int(v,16)for v in art['palette_rgb555'][1:]]]
            check(h,f'{label} icon{sid} slot{slot} exact4RGB555',hardware[slot*4:slot*4+4]==palette)
            check(h,'icon cells use bank1 and own palette',all(h['pb'].memory[1,0x9800+(y+k//2)*32+x+k%2]==8+slot for k in range(4)))
            check(h,'icon cells use own fourtile slot',all(h['pb'].memory[0,0x9800+(y+k//2)*32+x+k%2]==64+slot*4+k for k in range(4)))
            png=Image.open(ART_ROOT/art['icon']);indices=list(png.get_flattened_data());expected=[3 if p else 0 for p in indices]if not full else indices
            pixels=list(image.crop((x*8,y*8,(x+2)*8,(y+2)*8)).get_flattened_data())
            check(h,f'{label} icon{sid} renderedRGBmatchesPNGandpalette',pixels==[colors555(palette[p])for p in expected])
            check(h,'each drawnicon has visiblecontrast',len(set(pixels))>=2)
            page_records.append({'sid':sid,'slot':slot,'palette':palette,'raster_sha256':hashlib.sha256(bytes(v for p in pixels for v in p)).hexdigest()})
        check(h,'browsing icons changes noRF progress',state(h)==baseline)
        all_pages.append({'page':page,'icons':page_records})
        if page in(0,12,25):h['snapshot'](label+'-page'+str(page))
    h['press']('b',150);check(h,'guide returns actualhike',h['screen']()==2)
    return all_pages

def origin(h,origin,phase,weather,season,label):
    w.choose(h,phase,weather,season)
    if origin==9:h['open_camp']()
    elif origin==25:
        m=h['world'][h['value'](1)];camp=m['camp'];target=next((x,y)for y in range(7)for x in range(10)if not h['blocked'](m['id'],x,y)and(camp is None or abs(x-camp[0])+abs(y-camp[1])>1));h['walk'](*target);h['press']('start',150);check(h,'physical pack25',h['screen']()==25)
    before=palettes(h);frame=h['pb'].screen.image.convert('RGB').tobytes();baseline=state(h);h['snapshot'](label+'-before')
    h['press']('select',150);check(h,'guide opens from legitimateorigin',h['screen']()==7)
    for _ in range(7):h['press']('right',25)
    h['press']('a',150);check(h,'real saved detail from origin',h['screen']()==8)
    h['press']('start',150);check(h,'real saved album from origin',h['screen']()==10)
    h['press']('b',150);h['press']('b',150);check(h,'B restores originalcontext',h['screen']()==origin)
    after=palettes(h);attrs={h['pb'].memory[1,0x9800+y*32+x]&7 for y in range(18)for x in range(20)}
    (OUT/(label+'-palette-diagnostic.json')).write_text(json.dumps({'origin':origin,'before':before,'after':after,'active_palette_ids':sorted(attrs),'mismatched_active_palette_ids':[p for p in attrs if before[p*4:p*4+4]!=after[p*4:p*4+4]]},indent=2)+'\n');h['snapshot'](label+'-after')
    check(h,'all activelydrawn originpalettes restored',all(before[p*4:p*4+4]==after[p*4:p*4+4]for p in attrs))
    # Menu pixels static. World OAM/water animate naturally, so compare only
    # decoded background registers when world returns; no false frame equality.
    if origin in(9,25):check(h,'actual staticorigin raster restored',h['pb'].screen.image.convert('RGB').tobytes()==frame)
    check(h,'origin browsing retains progress apartfromguideindex',state(h)==baseline)
    h['snapshot'](label+'-returned')
    if origin!=2:h['press']('b',150)
    return {'origin':origin,'phase':phase,'weather':weather,'season':season,'active_palette_ids':sorted(attrs),'all64bytes_restored':before==after,'active_palette_words_restored':True}

def case(rom,noi,fixture,full,label,manifest,species):
    h=w.setup(rom,noi);h['OUT']=OUT
    with tempfile.TemporaryDirectory(prefix='rockflip-guide-palette-')as tmp:
        path=Path(tmp)/rom.name;shutil.copyfile(rom,path);open_rom(h,path,fixture.read_bytes()if fixture else None);resume(h)
        records=[];origins=[]
        for phase,weather,season,tag in [(0,0,2,'fairday'),(2,2,0,'rainnight')]:
            w.choose(h,phase,weather,season);before=palettes(h);records.append({'condition':tag,'pages':icons(h,full,label+'-'+tag,manifest,species)});check(h,'all worldpalette words reset afterguide',palettes(h)==before)
        (OUT/(label+'-all-icon-pages.json')).write_text(json.dumps({'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'result':'pass','all_icon_pages':records,'assertions':len(h['checks'])},indent=2)+'\n')
        if full:
            for phase,weather,season,tag in[(0,0,2,'fairday'),(2,2,0,'rainnight')]:
                for origin_screen in(2,9,25):origins.append(origin(h,origin_screen,phase,weather,season,label+'-'+tag+'-origin'+str(origin_screen)))
        h['pb'].stop()
    return {'label':label,'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],'pages':records,'origins':origins}

def main():
    global ART_ROOT
    p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--noi',type=Path);p.add_argument('--art-root',type=Path);p.add_argument('--species-file',type=Path);a=p.parse_args();noi=a.noi or Path(str(a.rom)+'.debug/symbols.noi')
    assert hashlib.sha256(a.rom.read_bytes()).hexdigest()==a.expected_sha,'Need frozen exact expected ROM'
    retained=str(a.rom.resolve()).startswith(str(FREEZE.resolve()))
    ART_ROOT=a.art_root or (FREEZE/'art/out'if retained else ROOT/'art/out');species_file=a.species_file or(FREEZE/'data/species.json'if retained else ROOT/'data/species.json')
    OUT.mkdir(parents=True,exist_ok=True);w.OUT=OUT;manifest=json.loads((ART_ROOT/'species-art-manifest.json').read_text());species=json.loads(species_file.read_text())
    cases=[]
    try:
        cases.append(case(a.rom,noi,None,False,'fresh-silhouettes',manifest,species));cases.append(case(a.rom,noi,FREEZE/'output/qa/lens-native/controller-earned-lens-layout4.ram',True,'earned-icons',manifest,species))
    except Exception as exc:
        (OUT/'failure.json').write_text(json.dumps({'result':'fail','failure':str(exc),'rom_sha256':hashlib.sha256(a.rom.read_bytes()).hexdigest(),'completed_cases':cases,'RFState_or_progress_writes':False,'palette_selector_only':'FF68 changed to read colors and restored; FF69 never written'},indent=2)+'\n');raise
    report={'result':'pass','scope':'Actual guide RGB555 hardware registers + source-indexed PNG raster, all151 earned and150 fresh silhouette icons in all26pages under fair/day andrain/night; activelydrawn originpalettes/context restoration. Unused menu palettes may retain icon colors without drawn effects.','rom_sha256':hashlib.sha256(a.rom.read_bytes()).hexdigest(),'assertions':sum(c['assertions']for c in cases),'cases':cases,'RFState_or_progress_writes':False,'hardware_selector_writes':'FF68 read index temporarily changed then exact old restored; FF69/colors never written','human_palette_readability_approved':False,'physical_hardware_verified':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['result','assertions','rom_sha256']},indent=2))
if __name__=='__main__':main()
