"""Compile authored exhibit data into one bank-local native header.

Canonical destinations: data/exhibit_gallery.json and
native/plugins/rockflip/engine/include/rockflip_gallery_data.h. No game, art,
main or UI mutations. Re-run after editing authored gallery content.
"""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]

def compile_gallery(source,out):
    data=json.loads(source.read_text());campaign=json.loads((ROOT/'data/campaign.json').read_text());ecology={r['species_id']:r for r in json.loads((ROOT/'data/species_ecology.json').read_text())['records']}
    rows=data['records'];fresh=data['fresh_records'];legacy_path=ROOT/'output/campaign-work/campaign-legacy.json';legacy_campaign=json.loads(legacy_path.read_text());assert len(rows)==16 and [r['district']for r in rows]==list(range(16))
    assert len(fresh)==16 and [r['district']for r in fresh]==list(range(16))
    for mode,entries in enumerate([rows,fresh]):
      for d in entries:
          assert d['district_id']==f'D{d["district"]+1:02d}' and d['minimum_best_score']==2
          assert len(d['targets'])==2 and len({t['species_id']for t in d['targets']})==2
          for key in ['title','ranger','theme','overview_title']:
              s=d[key];assert isinstance(s,str)and s.isascii()and 0<len(s)<=(18 if key=='overview_title'else 20),(key,s)
          assert len(d['response'])==2
          for s in d['response']:assert s.isascii()and 0<len(s)<=20,s
          original=(campaign if mode else legacy_campaign)['districts'][d['district']]
          for t in d['targets']:
              c=original['photo_targets'][t['campaign_target_index']]
              assert all(t[a]==c[b]for a,b in [('species_id','species_id'),('evidence_site_id','spot_id'),('evidence_map_id','map_id'),('habitat_id','habitat_id'),('subarea_id','subarea_id')]),t
              assert any(p['region_id']==d['district_id']and t['habitat_id']in p['habitat_ids']for p in ecology[t['species_id']]['region_permissions'])
    for a,b in zip(rows,fresh):
        for key in ['district','district_id','title','ranger','overview_title','minimum_best_score','unlock','picture_contract']:assert a[key]==b[key],key
    def arr(values):return '{'+','.join(json.dumps(v)for v in values)+'}'
    text='/* Generated from authored exhibit_gallery.json; no new taxa/save flags. */\n#ifndef ROCKFLIP_GALLERY_DATA_H\n#define ROCKFLIP_GALLERY_DATA_H\n'
    text+='static const UBYTE subjects[16][2]={'+','.join('{'+','.join(str(t['species_id'])for t in d['targets'])+'}'for d in rows)+'};\n'
    for name,key,width in [('titles','title',21),('overview_titles','overview_title',19),('themes','theme',21),('rangers','ranger',21)]:text+=f'static const char {name}[16][{width}]='+arr([d[key]for d in rows])+';\n'
    text+='static const char responses[16][2][21]={'+','.join(arr(d['response'])for d in rows)+'};\n#endif\n'
    text=text.replace('#endif\n','')
    text+='static const UBYTE fresh_subjects[16][2]={'+','.join('{'+','.join(str(t['species_id'])for t in d['targets'])+'}'for d in fresh)+'};\n'
    text+='static const char fresh_themes[16][21]='+arr([d['theme']for d in fresh])+';\n'
    text+='static const char fresh_responses[16][2][21]={'+','.join(arr(d['response'])for d in fresh)+'};\n#endif\n'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
    return {'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'header_sha256':hashlib.sha256(text.encode()).hexdigest(),'regions':16,'actual_campaign_species_refs':64,'legacy_and_fresh_descriptors_validated':True,'additional_persistent_bytes':0}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'data/exhibit_gallery.json');p.add_argument('--out-header',type=Path,default=ROOT/'native/plugins/rockflip/engine/include/rockflip_gallery_data.h');p.add_argument('--receipt',type=Path);a=p.parse_args();r=compile_gallery(a.source,a.out_header)
    if a.receipt:a.receipt.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
