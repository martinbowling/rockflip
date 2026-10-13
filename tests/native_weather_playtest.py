"""Controller-only forecasts, wet-window ecology, natural walk and world tint.

Root's shared movement/physical-camp/quality helpers are used without progress
writes. World palette checks are separate from the known c66 legacy-Mojave
camera fresh-base defect; they do not claim all-camera palette acceptance.
"""
from pathlib import Path
import json,hashlib,shutil,tempfile
from native_weather_migration import setup,choose,read,line,snapshot,conditions
from native_snapshot_migration import open_rom,latest
ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc';NOI=Path(str(ROM)+'.debug/symbols.noi')
OUT=ROOT/'output/qa/weather-native';OUT.mkdir(parents=True,exist_ok=True)
POLICY=json.load(open(ROOT/'output/weather-review/weather_species_policy.json'));pmap={r['species_id']:r for r in POLICY['records']}


def check(h,label,ok):h['check'](label,ok)
def current(h):return(h['flags']()[9]>>1)&15

def palette(h):
    at=h['symbol']('BkgPalette');return bytes(h['pb'].memory[at:at+64])
def surface(h):return hashlib.sha256(h['pb'].screen.image.crop((0,16,160,80)).tobytes()).hexdigest()
def back(h):h['press']('b',150);check(h,'menu/encounter return restores hike',h['screen']()==2)

def verify_ui_selection(h,w,s):
    # Enter/cancel without changing committed window; exact visible labels.
    h['open_camp']();before=h['flags']()[9];h['press']('a',150);check(h,'visible forecast screen27',h['screen']()==27)
    check(h,'forecast weather label matches currentselection',line(h,8)==['FAIR','CLOUDY','RAIN','AFTER RAIN'][w])
    check(h,'forecast season label matches currentselection',line(h,11)==['WINTER','SPRING','SUMMER','FALL'][s])
    h['press']('b',150);check(h,'forecast cancel changes no persistedbits',h['screen']()==9 and h['flags']()[9]==before);back(h)


def lookup(h,site,eligible,label):
    h['travel'](site['room_id']);h['face'](site)
    before=read(h,h['offset'](19),768);h['press']('a',150)
    if not eligible:
        check(h,label+' unavailable through actuallookup',h['screen']()==2)
        check(h,label+' visible ecological recoveryclue','PLAN WEATHER AT CAMP'==line(h,16))
        row=pmap[site['species_id']]['selected_evidence'];check(h,label+' specificwet clue',line(h,14)==row['clue'][0]and line(h,15)==row['clue'][1])
        h['snapshot'](label+'-blocked')
    else:
        for _ in range(2):
            if h['screen']()==3:break
            check(h,label+' boundedretry remains hike',h['screen']()==2);h['press']('a',150)
        check(h,label+' eligible region/habitat species opens',h['screen']()==3 and h['value'](6)==site['species_id'])
        h['snapshot'](label+'-encounter')
    after=read(h,h['offset'](19),768);check(h,label+' observation never flips cover',before[site['spot_id']]&1==after[site['spot_id']]&1==0)


def natural_walk(h,site):
    h['press']('a',20)
    start=h['frames']
    while h['screen']()!=4 and h['frames']-start<180:h['tick'](1)
    check(h,'wet arrival camera opens within bounded native gesture',h['screen']()==4)
    h['tick'](40)
    check(h,'wet arrival camera remains open after initial draw',h['screen']()==4)
    h['aim_to'](1);state=h['wait_for']('rain arrival calm walking step',lambda s:h['natural_window']('rain_arrival',s))
    check(h,'rain arrival walks horizontally without hop',state['x']==1 and state['y']==0 and state['motion']==1 and state['distance']==4 and not state['stress']and not state['disturbed'])
    h['shutter']('rain-arrival-natural',3);check(h,'actual rain walk earns3star persistentphoto',h['best'](9)==3 and snapshot(h,9)&144==144 and conditions(h,9)==6)
    h['return_trail'](site);return state


def main():
    h=setup(ROM,NOI);h['OUT']=OUT
    # Shared production face() proactively picks eligible weather; negative
    # ecology tests choose their own forecasts and must retain that selection.
    h['conditions_for_subject']=lambda sid: None
    forecast=[];world_palettes=[];drawn=[];availability=[]
    with tempfile.TemporaryDirectory(prefix='rockflip-weather-native-')as tmp:
        path=Path(tmp)/ROM.name;shutil.copy2(ROM,path);open_rom(h,path);h['enter_hike']();check(h,'fresh forecast cartridge enters hike',h['screen']()==2)
        # Music preference is earned through its real menu, then must survive
        # every forecast value and cancel. No unallocated flag bits are injected.
        h['open_camp']();h['press']('start',150);check(h,'actual music preference toggled',bool(h['flags']()[9]&128));back(h)
        protected_bits=h['flags']()[9]&225
        for season in range(4):
            for weather in range(4):
                nibble=weather+(season<<2);choose(h,0,weather,season)
                check(h,'all16 settings commit exact nibble',current(h)==nibble and h['flags']()[9]&225==protected_bits)
                before=palette(h);image=surface(h);world_palettes.append(before);drawn.append(image)
                if len(world_palettes)>1:check(h,'forecast leaves world wildlife/UI palettes5to7 unchanged',before[40:]==world_palettes[0][40:])
                check(h,'world tint allRGB555 words valid',all(int.from_bytes(before[i:i+2],'little')<=32767 for i in range(0,64,2)))
                # Opening/reopening menus must not compound terrain shading.
                for _ in range(2):
                    verify_ui_selection(h,weather,season);check(h,'repeated forecast cancellation doesnotdarken world',palette(h)==before);check(h,'same world surface remains drawn',surface(h)==image)
                h['snapshot'](f'world-window-{nibble:02d}')
                h['pb'].stop();saved=Path(str(path)+'.ram').read_bytes();r=latest(saved);check(h,'forecast saved in actual schema6 record',r['schema']==6 and r['size']==2544)
                open_rom(h,path,saved);check(h,'each forecast survives coldrestart',current(h)==nibble and h['flags']()[9]&225==protected_bits)
                h['enter_hike']();check(h,'cold selected window returns hike',h['screen']()==2)
                forecast.append({'nibble':nibble,'weather':weather,'season':season,'palette_sha256':hashlib.sha256(before).hexdigest(),'world_surface_sha256':image})
        check(h,'allfourweather states visibly alter world palette',len({world_palettes[w]for w in range(4)})==4)
        check(h,'weather shading actuallychanges drawn world pixels',len(set(drawn))>=4)
        for sid in[9,24,118,124]:
            site=next(s for s in h['sites']if s['species_id']==sid)
            choose(h,2,0,1);lookup(h,site,False,f'species-{sid}-fair')
            choose(h,2,2,2 if sid in(9,124) else 0);lookup(h,site,False,f'species-{sid}-wrongseason')
            choose(h,2,2,1);lookup(h,site,True,f'species-{sid}-rain-spring')
            if sid==9:walk_state=natural_walk(h,site)
            else:back(h)
            availability.append({'species_id':sid,'spot_id':site['spot_id'],'region_id':site['region_id'],'fair_blocked':True,'wrong_season_blocked':True,'rain_spring_opened':True,'cover_never_handled':True})
        # Speciesname does not infer rain exclusivity: actual FAIR encounter.
        choose(h,2,0,2);site=next(s for s in h['sites']if s['species_id']==125);lookup(h,site,True,'great-basin-fair');back(h)
        check(h,'GreatBasin spadefoot remains fairweather accessible',current(h)==8)
        h['open_camp']();back(h);h['pb'].stop();saved=Path(str(path)+'.ram').read_bytes();(OUT/'actual-weather-progress.ram').write_bytes(saved)
    report={'result':'pass','scope':'Actual16 forecast UI/commit/cancel/cold settings, reserved-bit retention, selected4 wet lookup policies, fair GreatBasin lookup, safe3star salamander walking and repeated world-palette stability. No injected progress.','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],'forecasts':forecast,'availability':availability,'rain_walk':walk_state,'known_separate_camera_limitation':'c66 legacy Mojave camera lacks freshpalette reset; root fixed source for nextbuild. This world/availability proof doesnotclaim allcamera tint acceptance.','physical_hardware_verified':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['result','assertions','rom_sha256']},indent=2))
if __name__=='__main__':main()
