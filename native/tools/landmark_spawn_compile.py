"""Reproduce reviewed legal-position repairs without resetting any game progress.
All coordinates are fictional10x7 game cells, never wildlife locations.
"""
from pathlib import Path
import json,hashlib

def emit(root,out):
    table=json.loads((root/'data/landmark_spawn_repairs.json').read_text());records=sorted(table['repairs'],key=lambda r:(r['map'],r['old_standing'][1]*10+r['old_standing'][0]));maps={m['id']:m for m in json.loads((root/'data/world.json').read_text())['maps']};sites=json.loads((root/'data/foundation_encounters.json').read_text())['records'];keys=set()
    for r in records:
        assert r['map'] in maps
        assert all(0<=p[0]<10 and 0<=p[1]<7 for p in (r['old_standing'],r['new_standing']))
        key=(r['map'],tuple(r['old_standing']));assert key not in keys;keys.add(key)
        x,y=r['new_standing'];m=maps[r['map']];assert m['terrain'][y][x] not in 'GWJj' and m.get('camp')!=[x,y]
        assert not any(s['room_id']==r['map'] and (s['game_tile_x'],s['game_tile_y'])==(x,y) for s in sites)
        assert r['progress_changes'] is False
    (out/'include').mkdir(parents=True,exist_ok=True);(out/'src').mkdir(parents=True,exist_ok=True)
    header='#ifndef RF_LANDMARK_REPAIR_H\n#define RF_LANDMARK_REPAIR_H\n#include <gb/gb.h>\n/* Return1 onlywhenxyrelocated. Doesnotmodifyphotos/flags/phase/weather/care/identity. */\nUBYTE rf_landmark_repair(UWORD map,UBYTE*x,UBYTE*y) BANKED;\n#endif\n';(out/'include/rockflip_landmark_repair.h').write_text(header)
    c='#pragma bank 255\n#include "rockflip_landmark_repair.h"\ntypedef struct{UWORD map;UBYTE oldcell,newcell;} PositionRepair;\nstatic const PositionRepair repairs[]={\n'
    c+=',\n'.join('{'+f'{r["map"]},{r["old_standing"][1]*10+r["old_standing"][0]},{r["new_standing"][1]*10+r["new_standing"][0]}'+'}' for r in records)+'\n};\n'
    c+='''UBYTE rf_landmark_repair(UWORD map,UBYTE*x,UBYTE*y) BANKED {
 UWORD lo=0,hi=sizeof(repairs)/sizeof(repairs[0]),mid;UBYTE cell,to;
 if(*x>9||*y>6){*x=0;*y=3;return 1;}
 cell=*y*10+*x;
 while(lo<hi){mid=lo+(hi-lo)/2;if(repairs[mid].map<map||(repairs[mid].map==map&&repairs[mid].oldcell<cell))lo=mid+1;else hi=mid;}
 if(lo<sizeof(repairs)/sizeof(repairs[0])&&repairs[lo].map==map&&repairs[lo].oldcell==cell){to=repairs[lo].newcell;*x=to%10;*y=to/10;return 1;}
 return 0;
}
''';(out/'src/rockflip_landmark_repair.c').write_text(c)
    return {'entries':len(records),'data_bytes':len(records)*4,'progress_mutations':False,'table_sha256':hashlib.sha256((root/'data/landmark_spawn_repairs.json').read_bytes()).hexdigest()}

def main():
    root=Path(__file__).resolve().parents[2];print(json.dumps(emit(root,root/'native/plugins/rockflip/engine')))
if __name__=='__main__':main()
