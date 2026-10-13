"""Whole-game trail sketch through real buttons; browsing grants no progress."""
from pathlib import Path
import hashlib,json,shutil,tempfile
from native_snapshot_migration import harness,open_rom
from native_weather_migration import line
ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'native/build/rom/RockFlip-Statewide.gbc'
OUT=ROOT/'output/qa/region-native'
FIX=ROOT/'output/qa/controller-earned-151-9471.ram'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    h=harness(ROM,Path(str(ROM)+'.debug/symbols.noi'));h['OUT']=OUT
    def check(label,ok):h['check'](label,ok)
    def state():
        data=bytearray(h['pb'].memory[h['RF']:h['RF']+2544]);data[h['offset'](0)]=0
        return bytes(data)
    def selected():
        name=line(h,2 if h['screen']()==31 else 1)
        district=h['pb'].memory[h['symbol']('rf_region_district')]+1
        nodes=[m for m in h['world'].values()if m['name']==name and m['district_id']==f'D{district:02d}']
        assert len(nodes)==1,('Unique rendered trail name',name)
        return nodes[0]
    def browse(origin,label):
        before=state();check(label+' sketch30',h['screen']()==30)
        for button in ('right','down','left','up'):
            h['press'](button,60);check(label+' sketch moves cursor '+button,h['screen']()==30)
            check(label+' sketch preserves full progression '+button,state()==before)
        h['press']('a',100);check(label+' details31',h['screen']()==31)
        for button,key in [('right','east'),('left','west'),('up','north'),('down','south')]:
            at=selected();dest=at.get(key);h['press'](button,100)
            check(label+' follows exact '+key,selected()['id']==(dest if dest is not None else at['id']))
            check(label+' details preserve full progression '+key,state()==before)
            check(label+' VRAM bank restored',h['pb'].memory[0xff4f]&1==0)
        h['snapshot'](label);h['press']('b',100)
        check(label+' returns exact context',h['screen']()==origin)
        check(label+' return preserves progression',state()==before)
    with tempfile.TemporaryDirectory(prefix='rockflip-region-native-')as tmp:
        path=Path(tmp)/ROM.name;shutil.copy2(ROM,path);open_rom(h,path,FIX.read_bytes())
        h['enter_hike']();check('authentic earned151 retained',h['value'](12)==151)
        for district in range(16):
            target=next(m['id']for m in h['world'].values()if m['district_id']==f'D{district+1:02d}'and m.get('camp'))
            h['travel'](target);h['open_camp']();h['press']('down',100)
            check('regional pages17 open',h['screen']()==17);h['press']('left',100)
            browse(17,f'district-{district:02d}-campaign');h['press']('b',100)
            h['press']('right',100);check('atlas12 open',h['screen']()==12)
            h['press']('select',100);browse(9,f'district-{district:02d}-atlas');h['press']('b',100)
            # Open pack away from a physical camp, using an actual legal tile.
            m=h['world'][h['value'](1)];cx,cy=m['camp']
            tile=next((x,y)for y in range(7)for x in range(10)
                      if not h['blocked'](m['id'],x,y)and abs(x-cx)+abs(y-cy)>1)
            h['walk'](*tile);h['press']('start',100);check('fieldpack25 open',h['screen']()==25)
            h['press']('left',100);browse(25,f'district-{district:02d}-pack');h['press']('b',100)
        h['travel'](131);h['press']('start',100);h['press']('left',100)
        check('earned hidden node selectable',selected()['id']==131)
        browse(25,'earned-hidden');h['pb'].stop()
    report={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),
            'fixture_sha256':hashlib.sha256(FIX.read_bytes()).hexdigest(),
            'assertions':len(h['checks']),'checks':h['checks'],'inputs':h['inputs'],
            'scope':'Actual full-game entries/returns for all16 districts, graph links, full RF progression unchanged by browsing and genuine earned hidden node. Isolated module proof separately covers all241 nodes/574 edges.',
            'physical_hardware_verified':False}
    (OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in['result','assertions','rom_sha256']}))
if __name__=='__main__':main()
