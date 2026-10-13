"""Real title pixels, fresh entry and existing-journal continuation; no RAM writes."""
from pathlib import Path
import argparse,hashlib,json,tempfile,shutil
from PIL import Image
from native_snapshot_migration import harness,open_rom
from native_weather_migration import line
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True);a=p.parse_args()
rom=R/'native/build/rom/RockFlip-Statewide.gbc';noi=Path(str(rom)+'.debug/symbols.noi')
assert hashlib.sha256(rom.read_bytes()).hexdigest()==a.expected_sha
out=R/'output/qa/title-native';out.mkdir(parents=True,exist_ok=True)
source=Image.open(R/'art/out/title_scene.png').convert('RGB');checks=0;profiles=[]
for name,fixture in [('fresh',None),('continue',R/'output/qa/production/controller-earned-complete.ram')]:
 h=harness(rom,noi);h['OUT']=out
 with tempfile.TemporaryDirectory(prefix='rockflip-title-')as td:
  cart=Path(td)/'title.gbc';shutil.copy2(rom,cart);open_rom(h,cart,fixture.read_bytes()if fixture else None);h['tick'](180)
  h['check']('title remains at ordinary menu',h['screen']()==0)
  actual=h['pb'].screen.image.convert('RGB')
  for y in range(104):
   for x in range(160):h['check']('nativeTitlePixelExactlyAuthored',actual.getpixel((x,y))==source.getpixel((x,y)))
  h['check']('appropriate title action',('CONTINUE'if fixture else 'FIRST HIKE')in line(h,13))
  h['check']('credit Bilby visible','BILBY'in line(h,15))
  h['check']('credit Martin visible','MARTIN BOWLING'in line(h,16))
  h['check']('credit Roam visible','ROAM'in line(h,17))
  h['pb'].screen.image.save(out/(name+'-title.png'))
  h['pb'].screen.image.resize((640,576),Image.Resampling.NEAREST).save(out/(name+'-title_4x.png'))
  before=h['value'](12);h['enter_hike']()
  h['check']('title entry keeps actual journal count',h['value'](12)==before)
  h['check']('ordinary input reaches field',h['screen']()==2)
  h['pb'].screen.image.save(out/(name+'-field.png'))
  checks+=len(h['checks']);profiles.append({'name':name,'frames':h['frames'],'inputs':h['inputs'],'assertions':len(h['checks'])});h['pb'].stop(save=False)
report={'status':'pass','rom_sha256':a.expected_sha,'assertions':checks,'profiles':profiles,'controller_only':True,'RAM_video_register_writes':False}
(out/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['status','rom_sha256','assertions']}))
