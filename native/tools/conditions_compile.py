"""Compile reviewed authored weather/season permissions for all151 identities."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
policy=json.loads((ROOT/'data/weather_species_policy.json').read_text())
rows=policy['records'];assert [r['species_id'] for r in rows]==list(range(151))
species=json.loads((ROOT/'data/species.json').read_text())
for row,s in zip(rows,species):
 assert row['scientific_name']==s['scientific_name']
 assert 0<row['weather_mask']<16 and 0<row['season_mask']<16
p=ROOT/'native/plugins/rockflip/engine/src/rockflip_conditions.c';source=p.read_text()
for label,key in (('weather_masks','weather_mask'),('season_masks','season_mask')):
 value='static const UBYTE '+label+'[]={'+','.join(str(r[key]) for r in rows)+'};'
 source,n=re.subn(r'static const UBYTE '+label+r'\[\]=\{[^}]*\};',value,source)
 assert n==1
p.write_text(source)
print('151 source-reviewed weather/season permission pairs compiled.')
