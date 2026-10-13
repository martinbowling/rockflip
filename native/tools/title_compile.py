"""Compile the authored title montage into a deduplicated, banked BG atlas."""
from pathlib import Path
from PIL import Image
import json

def emit_title(root):
    root=Path(root);art=root/'art/out';im=Image.open(art/'title_scene.png')
    assert im.mode=='P' and im.size==(160,104)
    unique=[];lookup={};mapping=[]
    for ty in range(13):
        for tx in range(20):
            raw=[]
            for y in range(8):
                lo=hi=0
                for x in range(8):
                    v=im.getpixel((tx*8+x,ty*8+y));assert 0<=v<4
                    lo|=(v&1)<<(7-x);hi|=(v>>1)<<(7-x)
                raw.extend((lo,hi))
            key=tuple(raw)
            if key not in lookup:lookup[key]=len(unique);unique.append(key)
            mapping.append(lookup[key])
    assert len(unique)<=256,'Title exceeds one BG bank'
    def array(name,values):return 'static const UBYTE '+name+'[]={'+','.join(map(str,values))+'};\n'
    colors=json.loads((art/'title_scene.json').read_text())['colors']
    words=[(r>>3)|((g>>3)<<5)|((b>>3)<<10)for r,g,b in colors]
    text='#pragma bank 255\n#include "rockflip_art.h"\n#include <gb/cgb.h>\n#include "palette.h"\n#include <string.h>\n'
    text+=array('title_tiles',[b for tile in unique for b in tile])
    text+=array('title_map',mapping)+array('title_attrs',[8]*260)
    text+='static const UWORD title_palette[]={'+','.join(map(str,words))+'};\n'
    text+='void rf_art_title(void) BANKED {memcpy(BkgPalette,title_palette,8);set_bkg_palette(0,1,title_palette);VBK_REG=1;'
    text+=f'set_bkg_data(0,{min(128,len(unique))},title_tiles);'
    if len(unique)>128:text+=f'set_bkg_data(128,{len(unique)-128},title_tiles+2048);'
    text+='set_bkg_tiles(0,0,20,13,title_attrs);VBK_REG=0;set_bkg_tiles(0,0,20,13,title_map);}\n'
    (root/'native/plugins/rockflip/engine/src/rockflip_title.c').write_text(text)
    (root/'output/qa/title-source.json').write_text(json.dumps({'width':160,'height':104,'unique_tiles':len(unique),'tile_bank':1,'palette':0,'font_bank_untouched':True,'saved_bytes_added':0},indent=2)+'\n')
