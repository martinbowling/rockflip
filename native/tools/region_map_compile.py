"""Refresh only trail sketch content arrays from canonical fictional world.
Renderer, controls, transient state and font remain hand-authored unchanged.
"""
from pathlib import Path
import json,argparse,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
def order(group):
 lookup={m['id']:m for m in group};result=[];seen=set()
 for start in sorted((m for m in group if m['west']not in lookup),key=lambda m:m.get('route_sequence',m['id'])):
  at=start
  while at['id']not in seen:
   result.append(at);seen.add(at['id'])
   if at['east']not in lookup:break
   at=lookup[at['east']]
 result.extend(m for m in group if m['id']not in seen);return result
def compile_region(source,world):
 offsets=[0];maps=[]
 for d in range(16):
  group=order([m for m in world if m['district_id']==f'D{d+1:02d}'and not m.get('hidden')]);group.extend(m for m in world if m['district_id']==f'D{d+1:02d}'and m.get('hidden'))
  assert 1<=len(group)<=20;maps.extend(group);offsets.append(len(maps))
 assert len(maps)==len(world)and len({m['id']for m in maps})==len(world)
 def ca(x):return json.dumps(x,separators=(',',':')).replace('[','{').replace(']','}')
 rows=[]
 for m in maps:
  name=m['name'];assert name.isascii()and len(name)<=20
  rows.append([m['id']]+[m[k]if m.get(k)is not None else 65535 for k in ['west','east','north','south']]+[int(m['camp']is not None),int(bool(m.get('hidden'))),name])
 for pattern,replacement in [(r'static const UWORD starts\[\]=\{[^;]+;', 'static const UWORD starts[]='+ca(offsets)+';'),(r'static const TrailNode nodes\[\]=\{[^;]+;', 'static const TrailNode nodes[]='+ca(rows)+';')]:
  source,n=re.subn(pattern,lambda match:replacement,source);assert n==1,pattern
 return source,rows,offsets

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--emit-native',action='store_true');a=p.parse_args()
 path=ROOT/'native/plugins/rockflip/engine/src/rockflip_region_ui.c';world=json.loads((ROOT/'data/world.json').read_text())['maps'];source,rows,offsets=compile_region(path.read_text(),world)
 if not a.check:
  target=path if a.emit_native else ROOT/'output/region-work/rockflip_region_ui.c';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
 print(json.dumps({'scope':'trail sketch content arrays only','maps':len(rows),'districts':16,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'map80':next(r[-1]for r in rows if r[0]==80),'renderer_controls_preserved':True}))
if __name__=='__main__':main()
