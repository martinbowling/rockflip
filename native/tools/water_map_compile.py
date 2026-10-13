"""Stage a bank-safe animated-water replacement for map_art_compile.

Imported emit_map_art has the existing compiler API. Standalone writes only to
output/world-water/src, never native output. Root must explicitly integrate it.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
from map_art_compile import CAMERA_SLOTS,camera_loads

def water_frames(root,pixels,tilebytes):
    pal=json.loads((root/'art/out/palettes.json').read_text())
    k=pal['sheet_order']['tiles_creek'].index('creek')
    base=pixels('tiles_creek.png').crop((k*16,0,k*16+16,16))
    assert set(base.get_flattened_data()) <= {1,2}, 'Only wave-on-water creek can be shifted'
    second=base.copy()
    # Shift authored light wave pixels one pixel. Preserve the dark-water fill,
    # whole metatile extent and all outside-bank geometry exactly.
    for y in range(16):
        for x in range(16): second.putpixel((x,y),base.getpixel(((x-1)%16,y)))
    assert base.tobytes()!=second.tobytes()
    return [tilebytes(base),tilebytes(second)]

def emit_map_art(root,out,pixels,tilebytes,decl):
    maps=json.loads((root/'data/world.json').read_text())['maps']
    meta=json.loads((root/'art/out/world-art-manifest.json').read_text())
    frames=water_frames(root,pixels,tilebytes)
    dispatch='#pragma bank 255\n#include "rockflip_art.h"\n'
    proofs=[]
    for m in maps:
        if m['art_style']=='desert': continue
        entry=meta[str(m['id'])];im=pixels(entry['indices'])
        unique=[];lookup={};mapping=[];attrs=list(entry['attributes'])
        water_positions=set()
        for ty in range(14):
            for tx in range(20):
                p=ty*20+tx
                if m['terrain'][ty//2][tx//2]=='W':
                    water_positions.add(p);mapping.append(None)
                    assert attrs[p]==3, ('Water palette must be3',m['id'],p)
                    q=(ty%2)*2+tx%2
                    assert tilebytes(im.crop((tx*8,ty*8,tx*8+8,ty*8+8)))==frames[0][q*16:q*16+16],('Frame0 differs from authoredW geometry',m['id'],p)
                    continue
                b=tuple(tilebytes(im.crop((tx*8,ty*8,tx*8+8,ty*8+8))))
                if b not in lookup: lookup[b]=len(unique);unique.append(b)
                mapping.append(136+lookup[b])
        reserve=4 if water_positions else 0
        assert len(unique)+reserve<=120, ('Animated world tile allocation overflow',m['id'],len(unique),reserve)
        water_start=136+len(unique)
        for p in water_positions:
            tx,ty=p%20,p//20
            mapping[p]=water_start+(ty%2)*2+tx%2
        assert all((value>=water_start)==(p in water_positions) for p,value in enumerate(mapping)),('Water alias escapedW cells',m['id'])
        name=f"rf_map_art_{m['id']:04d}"
        c='#pragma bank 255\n#include "rockflip_art.h"\n#include "palette.h"\n#include <gb/cgb.h>\n'
        c+=decl('tiles',[v for tile in unique for v in tile])+decl('mapping',mapping)+decl('attrs',[8|x for x in attrs])
        if water_positions:
            c+=decl('water_frame0',frames[0])+decl('water_frame1',frames[1])
            c+=f'void {name}_water(UBYTE frame) BANKED {{VBK_REG=1;set_bkg_data({water_start},4,(frame&1)?water_frame1:water_frame0);VBK_REG=0;}}\n'
            dispatch+=f'void {name}_water(UBYTE frame) BANKED;\n'
        colors=[((b>>3)<<10)|((g>>3)<<5)|(r>>3) for p in entry['palette_slots'] for r,g,b in p]
        c+='static const UWORD colors[]={'+','.join(map(str,colors))+'};\n'
        # Photos intentionally use the same static authored central crop for
        # camera and album: water phase is ambient, not saved photo metadata.
        camera=im.crop((16,24,144,88));cu=[];cl={};cm=[]
        for y in range(8):
            for x in range(16):
                b=tuple(tilebytes(camera.crop((x*8,y*8,x*8+8,y*8+8))))
                if b not in cl: cl[b]=len(cu);cu.append(b)
                assert cl[b]<len(CAMERA_SLOTS), ("Camera tile allocation overflow",m["id"])
                cm.append(CAMERA_SLOTS[cl[b]])
        assert len(cu)<=len(CAMERA_SLOTS)
        ca=[entry['attributes'][(y+3)*20+x+2] for y in range(8) for x in range(16)]
        c+=decl('camera_tiles',[v for tile in cu for v in tile])+decl('camera_map',cm)+decl('camera_attrs',ca)
        c+=f'void {name}(UBYTE phase,UBYTE camera) BANKED {{UBYTE i;UWORD v,shade[16];for(i=0;i<16;i++){{v=colors[i];if(phase==2)v=RGB((v&31)/2,((v>>5)&31)/2,((v>>10)&31)/2+5);else if(phase==1)v=RGB(v&31,((v>>5)&31)*3/4,((v>>10)&31)*3/4);shade[i]=v;((UWORD *)BkgPalette)[i]=v;}}set_bkg_palette(0,4,shade);if(camera){{VBK_REG=0;{camera_loads(len(cu))}set_bkg_tiles(2,4,16,8,camera_map);VBK_REG=1;set_bkg_tiles(2,4,16,8,camera_attrs);VBK_REG=0;return;}}VBK_REG=1;set_bkg_data(136,{len(unique)},tiles);'
        if water_positions:c+=f'set_bkg_data({water_start},4,water_frame0);'
        c+='set_bkg_tiles(0,2,20,14,attrs);VBK_REG=0;set_bkg_tiles(0,2,20,14,mapping);}\n'
        (out/'src'/(name+'.c')).write_text(c)
        dispatch+=f'void {name}(UBYTE phase,UBYTE camera) BANKED;\n'
        proofs.append({'map_id':m['id'],'static_unique_tiles':len(unique),'reserved_water_tiles':reserve,
                       'total_tiles':len(unique)+reserve,'water_pattern_start':water_start if reserve else None,
                       'water_metatiles':len(water_positions)//4,'only_W_cells_reference_water_patterns':True,
                       'water_palette':3 if reserve else None,'water_frame_changes':sum(a!=b for a,b in zip(*frames)) if reserve else 0,
                       'camera_static_crop_sha256':hashlib.sha256(camera.tobytes()).hexdigest(),'camera_pattern_count':len(cu),'camera_pattern_slots':list(CAMERA_SLOTS[:len(cu)])})
    dispatch+='UBYTE rf_art_map(UWORD map,UBYTE phase,UBYTE camera) BANKED {switch(map){'+''.join(f"case {m['id']}:rf_map_art_{m['id']:04d}(phase,camera);return 1;" for m in maps if m['art_style']!='desert')+'default:return 0;}}\n'
    # Only retain the original16-pattern legacy path while map1actually uses
    # legacy art. A regeneratedregionalmap1uses ordinaryfamily3/fourpatterns.
    legacy_water=[m['id'] for m in maps if m['id']==1 and m['art_style']=='desert']
    dispatch+='void rf_art_map_water(UWORD map,UBYTE frame) BANKED {switch(map){'
    if legacy_water:dispatch+='case 1:rf_art_water(frame&1);break;'
    dispatch+=''.join(f"case {p['map_id']}:rf_map_art_{p['map_id']:04d}_water(frame);break;" for p in proofs if p['reserved_water_tiles'])
    dispatch+='default:break;}}\n'
    (out/'src/rockflip_map_art.c').write_text(dispatch)
    receipt={'status':'staged_generator_tile_and_alias_checks_passed','native_observed':False,'canonical_integrated':False,
             'maps':len(maps),'regional_water_maps':sum(bool(p['reserved_water_tiles']) for p in proofs),
             'legacy_water_maps':legacy_water,'all_water_maps':sum(any('W' in row for row in m['terrain']) for m in maps),
             'maximum_map_tile_allocation':max(p['total_tiles'] for p in proofs),'signed_BG_world_budget':120,
             'maximum_camera_tile_allocation':max(p['camera_pattern_count'] for p in proofs),'camera_safe_budget':len(CAMERA_SLOTS),
             'camera_safe_runs':[[96,127],[164,223]],'camera_reserved_ranges_preserved':[[0,95],[128,163],[224,229],[230,233]],
             'swap_bank':1,'patterns_per_regional_swap':4,'swap_bytes':64,'palette':3,
             'water_frames_sha256':[hashlib.sha256(bytes(f)).hexdigest() for f in frames],
             'input_world_sha256':hashlib.sha256((root/'data/world.json').read_bytes()).hexdigest(),
             'input_manifest_sha256':hashlib.sha256((root/'art/out/world-art-manifest.json').read_bytes()).hexdigest(),
             'photo_semantics':'Camera/album use static authored central crop; ambient water animation phase is not recorded. Runtime applies independently stored weather metadata.',
             'map_proofs':proofs,'remaining_gates':['root import/API/header/timer integration','native allwatermap crop capture','VRAM tile diff proves64-byte reserved-pattern-only swap','full-world native regression and human visual review']}
    (out/'water-animation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

def main():
    root=Path(__file__).resolve().parents[2];art=root/'art/out';out=root/'output/world-water';(out/'src').mkdir(parents=True,exist_ok=True)
    def pixels(path):
        im=Image.open(art/path);assert im.mode=='P' and set(im.get_flattened_data())<={0,1,2,3};return im
    def tilebytes(im):
        result=[]
        for ty in range(0,im.height,8):
            for tx in range(0,im.width,8):
                for y in range(8):
                    lo=hi=0
                    for x in range(8):
                        v=im.getpixel((tx+x,ty+y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
                    result.extend((lo,hi))
        return result
    def decl(name,values):return 'static const UBYTE '+name+'[]={'+','.join(map(str,values))+'};\n'
    proof=emit_map_art(root,out,pixels,tilebytes,decl)
    print(json.dumps({k:v for k,v in proof.items() if k!='map_proofs'},indent=2))

if __name__=='__main__':main()
