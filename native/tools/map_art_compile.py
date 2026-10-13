"""Compile authored map backgrounds to native banks, never RGB previews."""
import json
from PIL import Image

# Bank0 font0..95, camp224..229 and restore230..233 survive camera redraws.
# Portraits128..163 are in BANK1; skipping the same bank0 indices is conservative.
# The backdrop uses two disjoint, natively verified runs.
CAMERA_SLOTS=tuple(range(96,128))+tuple(range(164,224))
def camera_loads(count):
    assert 0<count<=len(CAMERA_SLOTS),'Camera tiles exceed92 nonoverlapping slots'
    loads=f'set_bkg_data(96,{min(count,32)},camera_tiles);'
    if count>32:loads+=f'set_bkg_data(164,{count-32},camera_tiles+512);'
    return loads

def emit_map_art(root,out,pixels,tilebytes,decl):
    maps=json.loads((root/'data/world.json').read_text())['maps']
    meta=json.loads((root/'art/out/world-art-manifest.json').read_text()) if (root/'art/out/world-art-manifest.json').exists() else {}
    dispatch='#pragma bank 255\n#include "rockflip_art.h"\n'
    for m in maps:
        if m['art_style']=='desert':continue
        entry=meta[str(m['id'])];im=pixels(entry['indices']);unique=[];lookup={};mapping=[]
        for y in range(14):
            for x in range(20):
                b=tuple(tilebytes(im.crop((x*8,y*8,x*8+8,y*8+8))))
                if b not in lookup:lookup[b]=len(unique);unique.append(b)
                mapping.append(136+lookup[b])
        assert len(unique)<=120,'World tiles overflow native signed-BG allocation'
        name=f"rf_map_art_{m['id']:04d}"
        c='#pragma bank 255\n#include "rockflip_art.h"\n#include "palette.h"\n#include <gb/cgb.h>\n'
        c+=decl('tiles',[v for tile in unique for v in tile])+decl('mapping',mapping)+decl('attrs',[8|x for x in entry['attributes']])
        colors=[((b>>3)<<10)|((g>>3)<<5)|(r>>3) for p in entry['palette_slots'] for r,g,b in p]
        c+='static const UWORD colors[]={'+','.join(map(str,colors))+'};\n'
        # A contextual camera background, with its own bank-0 pattern range.
        camera=im.crop((16,24,144,88));cu=[];cl={};cm=[]
        for y in range(8):
            for x in range(16):
                b=tuple(tilebytes(camera.crop((x*8,y*8,x*8+8,y*8+8))))
                if b not in cl:cl[b]=len(cu);cu.append(b)
                assert cl[b]<len(CAMERA_SLOTS),'Camera tile allocation overflow'
                cm.append(CAMERA_SLOTS[cl[b]])
        assert len(cu)<=len(CAMERA_SLOTS)
        ca=[entry['attributes'][(y+3)*20+x+2] for y in range(8) for x in range(16)]
        c+=decl('camera_tiles',[v for tile in cu for v in tile])+decl('camera_map',cm)+decl('camera_attrs',ca)
        c+=f'void {name}(UBYTE phase,UBYTE camera) BANKED {{UBYTE i;UWORD v,shade[16];for(i=0;i<16;i++){{v=colors[i];if(phase==2)v=RGB((v&31)/2,((v>>5)&31)/2,((v>>10)&31)/2+5);else if(phase==1)v=RGB(v&31,((v>>5)&31)*3/4,((v>>10)&31)*3/4);shade[i]=v;((UWORD *)BkgPalette)[i]=v;}}set_bkg_palette(0,4,shade);if(camera){{VBK_REG=0;{camera_loads(len(cu))}set_bkg_tiles(2,4,16,8,camera_map);VBK_REG=1;set_bkg_tiles(2,4,16,8,camera_attrs);VBK_REG=0;return;}}VBK_REG=1;set_bkg_data(136,{len(unique)},tiles);set_bkg_tiles(0,2,20,14,attrs);VBK_REG=0;set_bkg_tiles(0,2,20,14,mapping);}}\n'
        (out/'src'/(name+'.c')).write_text(c);dispatch+=f'void {name}(UBYTE phase,UBYTE camera) BANKED;\n'
    dispatch+='UBYTE rf_art_map(UWORD map,UBYTE phase,UBYTE camera) BANKED {switch(map){'+''.join(f"case {m['id']}:rf_map_art_{m['id']:04d}(phase,camera);return 1;" for m in maps if m['art_style']!='desert')+'default:return 0;}}\n'
    (out/'src/rockflip_map_art.c').write_text(dispatch)
