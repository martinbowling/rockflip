from pathlib import Path
import importlib.util,json,copy,sys,difflib
ROOT=Path(__file__).resolve().parents[2]
def generate(destination):
 P=Path(destination);P.mkdir(parents=True,exist_ok=True)
 sys.path.insert(0,str(ROOT/'native/tools'))
 spec=importlib.util.spec_from_file_location('route_campaign',ROOT/'native/tools/campaign_compile.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 old=m.author();oldsites=copy.deepcopy(m.SITES);oldstories=copy.deepcopy(m.STORIES)
 m.SITES[0]=[2,21,30,52]
 m.STORIES[0][1]=('SAND AND HIGH ROCK',['DAY: FENCE LIZARD.','DAY: ZEBRA-TAIL.'],['MATCH THE TWO','DAYLIGHT REFUGES.'],'HIGH ROCK / SAND','BOTH IN A POND','BOTH IN TREE BARK',['PERCH AND OPEN SAND','KEEP BOTH HOMES SAFE'])
 m.STORIES[0][2]=('THE NIGHT COVER',['NIGHT: NIGHTSNAKE.','PHOTO. REPLACE ROCK.'],['WHAT FINISHES THIS','ROCK OBSERVATION?'],'REPLACE THE ROCK','TAKE ROCK TO CAMP','LEAVE ITS HOME OPEN',['DAY AND NIGHT HOMES.','YOUR DESERT SET.'])
 m.SITES[4]=[18,175,160,172]
 m.STORIES[4][2]=('THE SOUTHERN WATER',['DAY: S MOUNTAIN FROG','LOOK BY SOUTH WATER.'],['WHY KEEP THE REGION','WITH THIS LAKE PAGE?'],'ITS OWN WATER HOME','ALL FROGS: ONE LAKE','ANY DESERT POND FITS',['TWO SIERRA REFUGES.','KEEP EACH NAME SAFE.'])
 m.SITES[15]=[512,525,526,532]
 new=m.author();new['implementation_status']='authored_route_revision_runtime_acceptance_required'
 new['save_contract']='Layout6 SAME2544; newgame quest8bit1 chooses route variant. Verified layout1..5 retains old predicate/text variant and all filed/partial evidence. Never invent photo or reseed layout5 taskawards.'
 (P/'campaign-proposed.json').write_text(json.dumps(new,indent=2)+'\n');(P/'campaign-legacy.json').write_text(json.dumps(old,indent=2)+'\n')
 changes=[i for i in range(64)if old['districts'][i//4]['photo_targets'][i%4]!=new['districts'][i//4]['photo_targets'][i%4]]
 # Seven target bindings differ; no species/ecology permissions change.
 assert changes==[1,2,3,19,61,62,63],changes
 header='''#ifndef ROCKFLIP_CAMPAIGN_VARIANT_H
#define ROCKFLIP_CAMPAIGN_VARIANT_H
#include <gb/gb.h>
typedef struct{UWORD spot;UBYTE species,phase,distance,care;} RFCTarget;
UBYTE rf_campaign_variant_target(UBYTE index,RFCTarget*out) BANKED;
UBYTE rf_campaign_variant_text(UBYTE district,UBYTE stage,UBYTE row,char*out) BANKED;
void rf_campaign_route_hint(UBYTE row,char*out) BANKED;
#endif
'''
 source='#pragma bank 255\n#include "rockflip_campaign_variant.h"\n#include "rockflip_campaign.h"\n#include "rockflip_runtime.h"\n#include <string.h>\n'
 def ca(x):return json.dumps(x).replace('[','{').replace(']','}')
 variants=[]
 for i in changes:
  t=new['districts'][i//4]['photo_targets'][i%4];variants.append([t['spot_id'],t['species_id'],t['phase'],t['minimum_distance'],int(t['requires_restore_after_photo'])])
 source+='static const RFCTarget variants[7]='+ca(variants)+';\n'
 source+='UBYTE rf_campaign_variant_target(UBYTE index,RFCTarget*out) BANKED {switch(index){'+''.join(f'case {i}:memcpy(out,variants+{n},sizeof(RFCTarget));return 1;'for n,i in enumerate(changes))+'}return 0;}\n'
 storykeys=[(0,1),(0,2),(4,2)];texts=[]
 for d,s in storykeys:
  t=new['districts'][d]['stages'][s];texts.append([t['title']]+t['clue']+t['question']+t['options']+t['conclusion'])
 source+='static const char new_text[3][10][21]='+ca(texts)+';\n'
 source+='UBYTE rf_campaign_variant_text(UBYTE d,UBYTE s,UBYTE row,char*out) BANKED {if(row>=10)return 0;'+''.join(f'if(d=={d}&&s=={s}){{strcpy(out,new_text[{n}][row]);return 1;}}'for n,(d,s)in enumerate(storykeys))+'return 0;}\n'
 # Route names reveal only fictional authored trail names, no coordinates.
 names=[t['map_name']for d in old['districts']for t in d['photo_targets']];names[22]='DELTA REED BANK'
 source+='static const char old_places[64][21]='+ca(names)+';\n'
 newnames=[new['districts'][i//4]['photo_targets'][i%4]['map_name']for i in changes]
 source+='static const char new_places[7][21]='+ca(newnames)+';\n'
 source+='static void place(UBYTE i,char*out){if(rf.quest_flags[8]&2){switch(i){'+''.join(f'case {i}:strcpy(out,new_places[{n}]);return;'for n,i in enumerate(changes))+'}}strcpy(out,old_places[i]);}\n'
 # Offline shortest graph routes. No runtime BFS or RFMap allocation.
 from collections import deque
 world={x['id']:x for x in json.loads((ROOT/'data/world.json').read_text())['maps']}
 keys=[('west',1),('east',2),('north',3),('south',4)]
 def direction(start,target):
  if start==target:return 0
  q=deque([(start,0)]);seen={start}
  while q:
   at,first=q.popleft()
   for key,code in keys:
    nxt=world[at].get(key)
    if nxt is None or nxt in seen or world[nxt]['district_id']!=world[start]['district_id']:continue
    if world[at]['district_id']=='D12' and world[at]['subarea_id']!=world[nxt]['subarea_id']:
     if key=='west':code=7
     elif key=='east':code=6
    step=first or code
    if nxt==target:return step
    seen.add(nxt);q.append((nxt,step))
  return 255
 routes=[]
 for data in [old,new]:
  rows=[]
  for mid in range(len(world)):
   d=int(world[mid]['district_id'][1:])-1
   rows.append([direction(mid,t['map_id'])for t in data['districts'][d]['photo_targets']])
  routes.append(rows)
 source+='static const UBYTE old_routes[241][4]='+ca(routes[0])+';\n'
 source+='static const UBYTE new_routes[241][4]='+ca(routes[1])+';\n'
 phase=[t['phase']for d in old['districts']for t in d['photo_targets']]
 newphase=[new['districts'][i//4]['photo_targets'][i%4]['phase']for i in changes]
 source+='static const UBYTE old_phases[64]='+ca(phase)+';\n'
 source+='static const UBYTE new_phases[7]='+ca(newphase)+';\n'
 source+='static UBYTE phase_for(UBYTE i){if(rf.quest_flags[8]&2){switch(i){'+''.join(f'case {i}:return new_phases[{n}];'for n,i in enumerate(changes))+'}}return old_phases[i];}\n'
 source+='''void rf_campaign_route_hint(UBYTE row,char*out) BANKED {
 UBYTE d=rf_map.district,s,bits,first,last,i,pick=255,dir;out[0]=0;if(d>=16||row>1)return;
 s=rf_campaign_stage(rf.quest_flags,d);if(s>=3)return;
 bits=(rf.quest_flags[14+d/2]>>((d&1)*4))&15;
 first=s==0?0:s==1?1:3;last=s==1?2:first;
 for(i=first;i<=last;i++)if(!(bits&(1<<i))){if(pick==255)pick=i;if(phase_for(d*4+i)==rf.phase){pick=i;break;}}
 if(pick==255){if(s==2&&(d==0||d==9)&&!(rf.quest_flags[28+d/8]&(1<<(d&7)))){if(row==0){strcpy(out,"REPLACE ITS COVER");return;}pick=3;}else{if(row==0)strcpy(out,"PHOTOS READY");else strcpy(out,"FILE AT YOUR CAMP");return;}}
 if(row==0){place(d*4+pick,out);return;}
 if(rf.room>=241){strcpy(out,"CHECK THE TRAIL MAP");return;}
 if(rf.quest_flags[8]&2)dir=new_routes[rf.room][pick];else dir=old_routes[rf.room][pick];
 switch(dir){case 0:strcpy(out,"LOOK IN THIS HABITAT");break;
 case 1:strcpy(out,"W: FOLLOW THE TRAIL");break;case 2:strcpy(out,"E: FOLLOW THE TRAIL");break;
 case 3:strcpy(out,"N: TAKE THE SHORTCUT");break;case 4:strcpy(out,"S: TAKE THE SHORTCUT");break;
 case 6:strcpy(out,"E: ISLAND FERRY");break;case 7:strcpy(out,"W: ISLAND FERRY");break;
 default:strcpy(out,"CHECK THE TRAIL MAP");break;}
}
'''
 (P/'route-proof-source.json').write_text(json.dumps({'ROM_route_rows':241*4*2,'bytes':241*4*2,'no_runtime_BFS':True,'no_local_RFMap':True,'all_regular_maps_routes_reachable':all(code!=255 for table in routes for mid,row in enumerate(table)for code in row if mid!=131),'hidden_map131_no_ordinary_route':True,'target_choices_prefer_current_phase':True},indent=2)+'\n')
 (P/'rockflip_campaign_variant.h').write_text(header);(P/'rockflip_campaign_variant.c').write_text(source)
 # Existing module remains the legacy data source. Target copy and text overrides
 # are banked separately to avoid a >16KiB combined campaign data unit.
 base=m.compile_campaign(old)
 base=base.replace('#include "rockflip_campaign.h"','#include "rockflip_campaign.h"\n#include "rockflip_campaign_variant.h"\n#include "rockflip_runtime.h"')
 base=base.replace('typedef struct {UWORD spot;UBYTE species,phase,distance,care;} Target;','typedef RFCTarget Target;')
 needle='static const UBYTE choices[16][3]='
 insert='static void read_target(UBYTE i,Target*out){memcpy(out,targets+i,sizeof(Target));if(rf.quest_flags[8]&2)rf_campaign_variant_target(i,out);}\n'
 base=base.replace(needle,insert+needle)
 base=base.replace('const Target*t;if(stars','Target observed;const Target*t;if(stars').replace('t=targets+i;if(t->species','read_target(i,&observed);t=&observed;if(t->species')
 oldcare='void rf_campaign_care(UBYTE*f,UWORD spot) BANKED {UBYTE d;for(d=0;d<16;d++)if(needs_care[d]&&targets[d*4+3].spot==spot&&(getbits(f,14,d*4,4)&8))setbits(f,28,d,1,1);}'
 newcare='void rf_campaign_care(UBYTE*f,UWORD spot) BANKED {UBYTE d;Target observed;for(d=0;d<16;d++)if(needs_care[d]){read_target(d*4+3,&observed);if(observed.spot==spot&&(getbits(f,14,d*4,4)&8))setbits(f,28,d,1,1);}}'
 assert oldcare in base;base=base.replace(oldcare,newcare)
 base=base.replace('if(index!=255)strcpy(out,stage_text[d][s][index]);','if(index!=255){if((rf.quest_flags[8]&2)&&rf_campaign_variant_text(d,s,index,out))return;strcpy(out,stage_text[d][s][index]);}')
 (P/'rockflip_campaign_legacy_dispatch.c').write_text(base)
 return new
