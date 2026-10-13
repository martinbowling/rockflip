"""Compile complete reviewed151-species guide text and bounded filter data."""
from pathlib import Path
import json,textwrap,hashlib
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'HANDOFF.md').exists());BASE=ROOT/'output/qa/guide-source';BASE.mkdir(parents=True,exist_ok=True);OUT=ROOT/'native/plugins/rockflip/engine'
roster=json.loads((ROOT/'data/production_roster.json').read_text())['records'];ecology=json.loads((ROOT/'data/species_ecology.json').read_text())['records'];runtime=json.loads((ROOT/'data/species.json').read_text());sites=json.loads((ROOT/'data/foundation_encounters.json').read_text())['records']
assert [r['species_id'] for r in roster]==list(range(151));eco={r['species_id']:r for r in ecology};species={r['id']:r for r in runtime}
REGIONS=['MOJAVE','COLORADO DESERT','E.SIERRA/GREAT BASIN','SIERRA FOOTHILLS','SIERRA HIGH COUNTRY','SACRAMENTO VALLEY','SAN JOAQUIN VALLEY','BAY/DELTA/IN.COAST','CENTRAL COAST/RANGES','SOUTH COAST','SOUTHERN MOUNTAINS','CHANNEL ISLANDS','NORTH COAST/RANGES','KLAMATH MOUNTAINS','CASCADES','MODOC PLATEAU']
def wrap(s,maxlines=None):
 s=s.strip().replace('’',"'");assert s.isascii();lines=textwrap.wrap(s,20,break_long_words=True,break_on_hyphens=True)
 if maxlines==2 and len(lines)>2:
  # Prefer a legal word or existing hyphen boundary that fits BOTH lines.
  choices=[i for i in range(1,min(20,len(s))+1) if len(s[i:].lstrip())<=20 and (s[i:i+1]==' ' or s[i-1]=='-')]
  at=max(choices) if choices else 20;lines=[s[:at].rstrip(),s[at:].lstrip()]
 assert all(len(x)<=20 for x in lines) and (maxlines is None or len(lines)<=maxlines),(s,lines)
 return lines
records=[]
for r in roster:
 sid=r['species_id'];s=species[sid];e=eco[sid];assert r['canonical_scientific_name']==s['scientific_name']==e['canonical_scientific_name']
 permissions=e['region_permissions'];districts=sorted({int(p['region_id'][1:])-1 for p in permissions});habitats=sorted({h for p in permissions for h in p['habitat_ids']})
 activity=s['time'].upper().replace('_',' ');activity=activity.replace(' / ','/')
 # Existing facts and permission nouns only; this is game availability, never
 # exclusive biological activity or observation-coordinate information.
 text=[wrap(r['common_name'].upper(),2),wrap(r['canonical_scientific_name'].upper(),2),list(s['facts']),[line for h in habitats for line in wrap(h.replace('_',' ').upper())],[REGIONS[d] for d in districts],['ON THIS HIKE:']+wrap(activity)+['ACTIVITY CAN VARY.'],['TAKE PHOTOS ONLY.','NO HANDLING.','LEAVE SHELTER WHOLE.']]
 assert all(len(line)<=20 and line.isascii() for kind in text for line in kind);assert len(text[3])<=8
 ids=sorted(p['spot_id'] for p in sites if p['species_id']==sid)
 records.append({'species_id':sid,'common_name':r['common_name'],'scientific_name':r['canonical_scientific_name'],'hidden':sid==150,'text':text,'region_mask':sum(1<<d for d in districts),'spot_ids_for_seen':ids,'care_basis':'HANDOFF original no-handling/leave-habitat-whole ethics, not a species-specific medical rule','habitat_permission_ids':habitats,'sources':sorted({u for p in permissions for u in p.get('evidence_urls',[])})})
(OUT/'include/rockflip_guide.h').write_text('''#ifndef RF_GUIDE_H
#define RF_GUIDE_H
#include <gb/gb.h>
#define RF_GUIDE_COUNT 151
#define RF_GUIDE_NONE 255
/* kind0 fullcommon,1 scientific,2 reviewedfacts,3 habitats,4 broadregions,
 *5 authoredgameavailability(nonexclusive),6 generalnonhandlingcare. out>=21. */
void rf_guide_text(UBYTE sid,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_lines(UBYTE sid,UBYTE kind) BANKED;
UWORD rf_guide_regions(UBYTE sid) BANKED;
UBYTE rf_guide_seen(UBYTE sid,const UBYTE*best,const UBYTE*spot_flags) BANKED;
/* filters0ALL,1UNPHOTOGRAPHED,2SEEN,3PHOTOGRAPHED,4CURRENTDISTRICT.
 * Hidden150range is excluded until actualphoto; UI never calls text for it
 * before photo. ALL/unphotographed may retain an anonymous slot. */
UBYTE rf_guide_match(UBYTE sid,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED;
UBYTE rf_guide_count(UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED;
UBYTE rf_guide_next(UBYTE sid,UBYTE backward,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED;
#endif
''')
def array(name,values,kind='UBYTE'):return 'static const '+kind+' '+name+'[]={'+','.join(map(str,values))+'};\n'
dispatch='#pragma bank255\n#include "rockflip_guide.h"\n'.replace('bank255','bank 255');receipts=[]
for group in range(5):
 rows=records[group*32:(group+1)*32];pool=bytearray();lookup={};offsets=[];counts=[];spot_offsets=[0];spot_ids=[]
 for r in rows:
  for lines in r['text']:
   key=b''.join(x.encode()+b'\0' for x in lines)
   if key not in lookup:lookup[key]=len(pool);pool.extend(key)
   offsets.append(lookup[key]);counts.append(len(lines))
  spot_ids.extend(r['spot_ids_for_seen']);spot_offsets.append(len(spot_ids))
 name=f'rf_guide_data_{group}';c='#pragma bank 255\n#include "rockflip_guide.h"\n'
 c+=array('pool',pool)+array('offsets',offsets,'UWORD')+array('counts',counts)+array('regions',[r['region_mask'] for r in rows],'UWORD')+array('spot_offsets',spot_offsets,'UWORD')+array('spot_ids',spot_ids or [0],'UWORD')
 c+=f'void {name}_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED {{UWORD at;UBYTE i;out[0]=0;if(s>={len(rows)}||kind>6||line>=counts[(UWORD)s*7+kind])return;at=offsets[(UWORD)s*7+kind];while(line--){{while(pool[at])at++;at++;}}for(i=0;i<20&&pool[at];i++)out[i]=pool[at++];out[i]=0;}}\n'
 c+=f'UBYTE {name}_lines(UBYTE s,UBYTE kind) BANKED {{if(s>={len(rows)}||kind>6)return 0;return counts[(UWORD)s*7+kind];}}\n'
 c+=f'UWORD {name}_regions(UBYTE s) BANKED {{if(s>={len(rows)})return 0;return regions[s];}}\n'
 c+=f'UBYTE {name}_seen(UBYTE s,const UBYTE*spots) BANKED {{UWORD i,end;if(s>={len(rows)})return 0;i=spot_offsets[s];end=spot_offsets[s+1];for(;i<end;i++)if(spots[spot_ids[i]]&2)return 1;return 0;}}\n'
 (OUT/f'src/{name}.c').write_text(c);receipts.append({'group':group,'species':len(rows),'string_pool_bytes':len(pool),'data_bytes':len(pool)+len(offsets)*2+len(counts)+len(rows)*2+len(spot_offsets)*2+len(spot_ids)*2,'maximum_seen_query_sites':max(len(r['spot_ids_for_seen']) for r in rows)})
 for signature in [f'void {name}_text(UBYTE s,UBYTE kind,UBYTE line,char*out)',f'UBYTE {name}_lines(UBYTE s,UBYTE kind)',f'UWORD {name}_regions(UBYTE s)',f'UBYTE {name}_seen(UBYTE s,const UBYTE*spots)']:dispatch+=signature+' BANKED;\n'
for api,returntype,args,call in [('text','void','UBYTE sid,UBYTE kind,UBYTE line,char*out','sid%32,kind,line,out'),('lines','UBYTE','UBYTE sid,UBYTE kind','sid%32,kind'),('regions','UWORD','UBYTE sid','sid%32')]:
 default='out[0]=0;return;' if api=='text' else 'return 0;'
 dispatch+=f'{returntype} rf_guide_{api}({args}) BANKED {{if(sid>=151){{{default}}}switch(sid/32){{'+''.join(f'case {g}:'+('' if api=='text' else 'return ')+f'rf_guide_data_{g}_{api}({call});'+('return;' if api=='text' else '') for g in range(5))+'}'+('' if api=='text' else 'return 0;')+'}\n'
dispatch+='UBYTE rf_guide_seen(UBYTE sid,const UBYTE*best,const UBYTE*spots) BANKED {if(sid>=151)return 0;if(best[sid])return 1;switch(sid/32){'+''.join(f'case {g}:return rf_guide_data_{g}_seen(sid%32,spots);' for g in range(5))+'}return 0;}\n'
dispatch+='''UBYTE rf_guide_match(UBYTE sid,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED {if(sid>=151||filter>4)return 0;switch(filter){case 0:return 1;case 1:if(!best[sid])return 1;return 0;case 2:return rf_guide_seen(sid,best,spots);case 3:if(best[sid])return 1;return 0;case 4:if(district>15||sid==150&&!best[150])return 0;if(rf_guide_regions(sid)&((UWORD)1<<district))return 1;return 0;}return 0;}
UBYTE rf_guide_count(UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED {UBYTE sid,count=0;for(sid=0;sid<151;sid++)if(rf_guide_match(sid,filter,district,best,spots))count++;return count;}
UBYTE rf_guide_next(UBYTE sid,UBYTE backward,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED {UBYTE n;if(sid>=151)sid=backward?0:150;for(n=0;n<151;n++){if(backward){if(sid)sid--;else sid=150;}else{sid++;if(sid>=151)sid=0;}if(rf_guide_match(sid,filter,district,best,spots))return sid;}return 255;}
'''
(OUT/'src/rockflip_guide.c').write_text(dispatch)
(BASE/'guide-content.json').write_text(json.dumps({'status':'derived_from_current_reviewed_data_pending_independent_text_native_review','records':records},indent=2)+'\n')
(BASE/'content-validation.json').write_text(json.dumps({'species':151,'text_kinds':7,'bounded_line_width':20,'common_name_lines_max':2,'scientific_name_lines_max':2,'no_real_coordinates':True,'groups':receipts,'runtime_seen_mask':2,'runtime_seen_bit_index':1,'spot_flags_new_WRAM_bytes':0,'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/production_roster.json','data/species_ecology.json','data/species.json','data/foundation_encounters.json']},'remaining':['Independent text semantics review','Parent integration and complete native filtered/return/hidden/album tests','Human/readability/physical review']},indent=2)+'\n');print(receipts)
