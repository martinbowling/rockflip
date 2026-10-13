"""Stage nearest physical-camp navigation data; never edit native outputs."""
from pathlib import Path
from collections import deque,defaultdict
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/world-camps'
DIRECTIONS={'west':1,'east':2,'north':3,'south':4}
HINTS=['CAMP ON THIS TRAIL','WEST TOWARD CAMP','EAST TOWARD CAMP','NORTH TOWARD CAMP','SOUTH TOWARD CAMP']

def build(world):
    maps={m['id']:m for m in world['maps']};rows=[];proofs=[]
    assert set(maps)==set(range(len(maps)))
    for mid,m in sorted(maps.items()):
        q=deque([(mid,[])]);seen={mid};found=None
        while q:
            here,path=q.popleft();at=maps[here]
            if at['camp'] is not None:found=(here,path);break
            for direction in DIRECTIONS:
                dest=at.get(direction)
                if dest is None or dest in seen:continue
                target=maps[dest]
                if target['district_id']!=m['district_id']:continue
                # Physical-camp hints may not imply walking between islands.
                if m['district_id']=='D12' and target['subarea_id']!=m['subarea_id']:continue
                seen.add(dest);q.append((dest,path+[(here,direction,dest)]))
        if found is None:
            assert m.get('hidden') or m.get('hidden_reserved'),('Ordinary map lacks reachable regional camp',mid)
            rows.append((65535,65535,255))
            proofs.append({'map_id':mid,'nearest_camp':None,'status':'isolated_hidden_refuge_needs_explicit_expedition_return','path':[]})
            continue
        camp,path=found
        direction=DIRECTIONS[path[0][1]] if path else 0;next_map=path[0][2] if path else mid
        rows.append((camp,next_map,direction));proofs.append({'map_id':mid,'nearest_camp':camp,'camp_name':maps[camp]['name'],'hops':len(path),'first_direction':path[0][1] if path else 'local','next_map':next_map,'path':path})
        for a,k,b in path:
            opposite={'west':'east','east':'west','north':'south','south':'north'}[k]
            assert maps[b].get(opposite)==a
            assert maps[b]['district_id']==m['district_id']
    return rows,proofs

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    wp=ROOT/'data/world.json';world=json.loads(wp.read_text());rows,proofs=build(world)
    header='''#ifndef ROCKFLIP_CAMP_ROUTE_H
#define ROCKFLIP_CAMP_ROUTE_H
#include <gb/gb.h>
/* 0 localcamp;1west;2east;3north;4south;255 no walking route.
 * Hints are nearest by map hops, not player-position pixel distance.
 * No crossing regional/island boundaries. Hiddenrefuge needs explicit return.
 */
UBYTE rf_camp_route(UWORD map,UWORD*camp,UWORD*next,UBYTE*direction) BANKED;
void rf_camp_route_hint(UWORD map,char*out) BANKED;
#endif
'''
    c='#pragma bank 255\n#include "rockflip_camp_route.h"\n#include <string.h>\n'
    c+='typedef struct {UWORD camp,next;UBYTE direction;} CampRoute;\n'
    c+='static const CampRoute routes[]={'+','.join('{'+','.join(map(str,r))+'}' for r in rows)+'};\n'
    c+='static const char hints[5][21]={'+','.join(json.dumps(s) for s in HINTS)+'};\n'
    c+=f'UBYTE rf_camp_route(UWORD map,UWORD*camp,UWORD*next,UBYTE*direction) BANKED {{if(map>={len(rows)}||routes[map].camp==65535){{*camp=*next=65535;*direction=255;return 0;}}*camp=routes[map].camp;*next=routes[map].next;*direction=routes[map].direction;return 1;}}\n'
    c+=f'void rf_camp_route_hint(UWORD map,char*out) BANKED {{if(map>={len(rows)}||routes[map].direction==255)strcpy(out,"RETURN EXPEDITION");else strcpy(out,hints[routes[map].direction]);}}\n'
    (OUT/'rockflip_camp_route.h').write_text(header);(OUT/'rockflip_camp_route.c').write_text(c)
    report={'status':'staged_graph_route_checks_passed','native_observed':False,'canonical_integrated':False,'input_world_sha256':hashlib.sha256(wp.read_bytes()).hexdigest(),'map_count':len(rows),'physical_camps':sum(m['camp'] is not None for m in world['maps']),'ordinary_maps_with_route':sum(r[0]!=65535 for r in rows),'isolated_map_ids':[p['map_id'] for p in proofs if p.get('nearest_camp') is None],'maximum_camp_hops':max(p.get('hops',0) for p in proofs),'direction_counts':dict(__import__('collections').Counter(p.get('first_direction','no_walk_route') for p in proofs)),'nearest_metric':'Fewest regional map hops; D12 same-island subarea only; source-order direction tiesW/E/N/S. Local camp approach remains actual player navigation.','proofs':proofs,'remaining_gates':['root chooses physicalcamp pause/save/rest/return rules','explicit hiddenrefuge expedition-return prevents trapping player','native hints agree with collision/portals/ferry presentation','normal play pacing/navigation review']}
    (OUT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='proofs'},indent=2))

if __name__=='__main__':main()
