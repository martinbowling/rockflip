"""Compile16 original district rangers in four safe banked artwork groups."""
import json,argparse,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'art/out';OUT=ROOT/'native/plugins/rockflip/engine'
def tiles(im):
    assert im.mode=='P' and set(im.get_flattened_data())<={0,1,2,3}
    result=[]
    for y in range(0,im.height,8):
        for x in range(0,im.width,8):
            for row in range(8):
                a=b=0
                for col in range(8):
                    v=im.getpixel((x+col,y+row));a|=(v&1)<<(7-col);b|=(v>>1)<<(7-col)
                result.extend((a,b))
    return result
manifest=json.loads((ART/'ranger-art-manifest.json').read_text());entries=sorted(manifest.values(),key=lambda m:m['district_index']);assert [m['district_index'] for m in entries]==list(range(16))
campaign=json.loads((ROOT/'data/campaign.json').read_text())
assert [m['ranger_name'] for m in entries]==[d['ranger_name'] for d in campaign['districts']]
def array(name,data,kind='UBYTE'):return 'static const '+kind+' '+name+'[]={'+','.join(map(str,data))+'};\n'
dispatch='#pragma bank 255\n#include "rockflip_ranger.h"\n'
for group in range(4):
    portraits=[];sprites=[];colors=[]
    for m in entries[group*4:group*4+4]:
        for f in m['frames']:portraits+=tiles(Image.open(ART/f))
        assert len(m['sprite_frames'])==12
        for fn in m['sprite_frames']:
            image=Image.open(ART/fn);assert image.size==(16,24) and image.mode=='P';sprites+=tiles(image)
        colors += [int(x,16) for x in m['palette_rgb555']]
    c='#pragma bank 255\n#include "rockflip_ranger.h"\n#include "palette.h"\n#include <gb/cgb.h>\n#include <string.h>\n'+array('portraits',portraits)+array('sprites',sprites)+array('colors',colors,'UWORD')
    c+=f'void rf_ranger_{group}_portrait(UBYTE ranger,UBYTE frame) BANKED {{UWORD c[4];memcpy(c,colors+ranger*4,8);c[0]=RGB(30,29,25);VBK_REG=1;set_bkg_data(128,36,portraits+((UWORD)ranger*2+(frame&1))*576);VBK_REG=0;memcpy(((UWORD*)BkgPalette)+20,c,8);set_bkg_palette(5,1,c);}}\n'
    c+=f'void rf_ranger_{group}_camp_frame(UBYTE ranger,UBYTE frame) BANKED {{VBK_REG=0;set_bkg_data(224,6,sprites+((UWORD)ranger*12+frame)*96);}}\n'
    c+=f'void rf_ranger_{group}_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED {{UBYTE i,t,a=6;UWORD c[4];memcpy(c,colors+ranger*4,8);c[0]=((UWORD*)BkgPalette)[0];set_bkg_palette(6,1,c);VBK_REG=0;set_bkg_data(224,6,sprites+(UWORD)ranger*1152);for(i=0;i<6;i++){{t=224+i;VBK_REG=0;set_bkg_tiles(x*2+(i&1),1+y*2+i/2,1,1,&t);VBK_REG=1;set_bkg_tiles(x*2+(i&1),1+y*2+i/2,1,1,&a);}}VBK_REG=0;}}\n'
    assert len(portraits)==4608 and len(sprites)==4608 and len(colors)==16
    (OUT/f'src/rf_ranger_{group}.c').write_text(c)
    dispatch+=f'void rf_ranger_{group}_portrait(UBYTE ranger,UBYTE frame) BANKED;\nvoid rf_ranger_{group}_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;\nvoid rf_ranger_{group}_camp_frame(UBYTE ranger,UBYTE frame) BANKED;\n'
dispatch+='void rf_ranger_portrait(UBYTE ranger,UBYTE frame) BANKED {if(ranger>15)ranger=0;switch(ranger/4){'+''.join(f'case {n}:rf_ranger_{n}_portrait(ranger%4,frame);break;' for n in range(4))+'}}\n'
dispatch+='void rf_ranger_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED {if(ranger>15)ranger=0;switch(ranger/4){'+''.join(f'case {n}:rf_ranger_{n}_camp(ranger%4,x,y);break;' for n in range(4))+'}}\n'
dispatch+='void rf_ranger_camp_frame(UBYTE ranger,UBYTE frame) BANKED {if(ranger>15)ranger=0;if(frame>11)frame=0;switch(ranger/4){'+''.join(f'case {n}:rf_ranger_{n}_camp_frame(ranger%4,frame);break;' for n in range(4))+'}}\n'
dispatch+='void rf_ranger_camp_idle(UBYTE ranger,UBYTE phase) BANKED {static const UBYTE poses[]={0,1,0,2};rf_ranger_camp_frame(ranger,poses[phase&3]);}\n'
(OUT/'src/rockflip_ranger.c').write_text(dispatch)
(OUT/'include/rockflip_ranger.h').write_text('#ifndef RF_RANGER_H\n#define RF_RANGER_H\n#include <gb/gb.h>\nvoid rf_ranger_portrait(UBYTE ranger,UBYTE frame) BANKED;\nvoid rf_ranger_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;\n/* Frame0..11: down/right/up/left, idle/weightshift1/weightshift2. Only swaps96bytes bank0tiles224..229, no map/attributes/palette/OAM writes. */\nvoid rf_ranger_camp_frame(UBYTE ranger,UBYTE frame) BANKED;\n/* Root advances phase0..3 every96 VBlank: authored0,1,0,2poses. */\nvoid rf_ranger_camp_idle(UBYTE ranger,UBYTE phase) BANKED;\n#endif\n')
print('16 district rangers compiled with all192 original movement frames.')
