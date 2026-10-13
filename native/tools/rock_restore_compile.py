"""Compile original rock pose2bpp tables from canonical indexedPNG source output."""
from pathlib import Path
from PIL import Image
import argparse,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'HANDOFF.md').exists());p=argparse.ArgumentParser();p.add_argument('--art-dir',type=Path,default=ROOT/'art/out');p.add_argument('--output-dir',type=Path,default=ROOT/'native/plugins/rockflip/engine/src');args=p.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
assert out.resolve()!= (ROOT/'native/plugins/rockflip/engine').resolve(),'stagingonly'
meta=json.loads((args.art_dir/'rock-restore-art-manifest.json').read_text());raw=[]
for fn in meta['frames']:
 im=Image.open(args.art_dir/fn);assert im.mode=='P' and im.size==(16,16) and set(im.get_flattened_data())<={0,1,2,3}
 for ty in range(2):
  for tx in range(2):
   for row in range(8):
    a=b=0
    for col in range(8):v=im.getpixel((tx*8+col,ty*8+row));a|=(v&1)<<(7-col);b|=(v>>1)<<(7-col)
    raw.extend((a,b))
assert len(raw)==256
c='#pragma bank 255\n#include "rockflip_rock_restore.h"\n#include <gb/cgb.h>\nstatic const UBYTE frames[]={'+','.join(map(str,raw))+'};\n'
c+='void rf_rock_restore_frame(UBYTE x,UBYTE y,UBYTE frame) BANKED {UBYTE i,t,a=0;if(frame>3)frame=3;VBK_REG=0;set_bkg_data(230,4,frames+(UWORD)frame*64);for(i=0;i<4;i++){t=230+i;VBK_REG=0;set_bkg_tiles(x*2+(i&1),2+y*2+(i>>1),1,1,&t);VBK_REG=1;set_bkg_tiles(x*2+(i&1),2+y*2+(i>>1),1,1,&a);}VBK_REG=0;}\n'
(out/'rockflip_rock_restore.c').write_text(c);header_out=out.parent/'include' if out.resolve()==(ROOT/'native/plugins/rockflip/engine/src').resolve() else out;header_out.mkdir(parents=True,exist_ok=True);(header_out/'rockflip_rock_restore.h').write_text('#ifndef RF_ROCK_RESTORE_H\n#define RF_ROCK_RESTORE_H\n#include <gb/gb.h>\nvoid rf_rock_restore_frame(UBYTE x,UBYTE y,UBYTE frame) BANKED;\n#endif\n');print('Compiled rock restoration from canonical indexed1x PNGs')
