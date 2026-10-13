"""Compile indexed marine backdrop to banked native C; staging is DEFAULT.
Pass --install only after the parent confirms no native build is in progress.
Never accepts a preview image. No real-world coordinates or copied imagery.
"""
from pathlib import Path
import argparse,json,hashlib,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]

def emit_marine_content(art_directory,output_directory):
 art=Path(art_directory);out=Path(output_directory);(out/'src').mkdir(parents=True,exist_ok=True);(out/'include').mkdir(parents=True,exist_ok=True)
 meta=json.loads((art/'marine-art-manifest.json').read_text());im=Image.open(art/meta['asset'])
 assert im.mode=='P' and im.size==(128,64) and set(im.get_flattened_data())<={0,1,2,3}
 assert im.getpalette()[:12]==[v for c in meta['palette'] for v in c]
 def tile(tx,ty):
  result=[]
  for y in range(8):
   lo=hi=0
   for x in range(8):v=im.getpixel((tx*8+x,ty*8+y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
   result.extend([lo,hi])
  return tuple(result)
 unique=[];lookup={};mapping=[]
 for y in range(8):
  for x in range(16):
   b=tile(x,y)
   if b not in lookup:lookup[b]=len(unique);unique.append(b)
   mapping.append(96+lookup[b])
 assert 1<=len(unique)<=128 and max(mapping)<=223
 colors=[int(v,16)for v in meta['palette_rgb555']]
 header='''#ifndef ROCKFLIP_MARINE_H
#define ROCKFLIP_MARINE_H
#include <gb/gb.h>
/* Open-water photo/album frame for exactmarineIDs61/73. Parentenforceslong
 * distance4, nohandling and legalshoreobservation. Notarock-fliphabitat.
 * Backdropusesbank0tiles96..223maximum, BGpalette3, screen(2,4)16x8tiles.
 * Foregroundportraitbank1/UIpalette7/fonttiles0..95remainuntouched.
 * Reloadnormalworld/habitatpalettesonexit; these functionsownonlycamera3,
 * portraitground5:0 andBkgPalette[0]groundmirrorwhencalled. */
void rf_marine_backdrop(UBYTE phase) BANKED;
void rf_marine_tint(UBYTE phase) BANKED;
#endif
'''
 def decl(name,data):return 'static const UBYTE '+name+'[]={'+','.join(map(str,data))+'};\n'
 c='#pragma bank 255\n#include "rockflip_marine.h"\n#include "palette.h"\n#include <gb/cgb.h>\n'
 c+=decl('sea_tiles',[v for b in unique for v in b])+decl('sea_map',mapping)+decl('sea_attrs',[3]*128)
 c+='static const UWORD sea_colors[]={'+','.join(map(str,colors))+'};\n'
 c+='''static UWORD shade_color(UWORD v,UBYTE phase){if(phase==2)return RGB((v&31)/2,((v>>5)&31)/2,((v>>10)&31)/2+5);if(phase==1)return RGB(v&31,((v>>5)&31)*3/4,((v>>10)&31)*3/4);return v;}
void rf_marine_tint(UBYTE phase) BANKED {UWORD ground=((UWORD*)BkgPalette)[12];(void)phase;((UWORD*)BkgPalette)[0]=ground;((UWORD*)BkgPalette)[20]=ground;set_bkg_palette_entry(5,0,ground);}
void rf_marine_backdrop(UBYTE phase) BANKED {UBYTE i;UWORD colors[4];for(i=0;i<4;i++){colors[i]=shade_color(sea_colors[i],phase);((UWORD*)BkgPalette)[12+i]=colors[i];}set_bkg_palette(3,1,colors);VBK_REG=0;set_bkg_data(96,TILE_COUNT,sea_tiles);set_bkg_tiles(2,4,16,8,sea_map);VBK_REG=1;set_bkg_tiles(2,4,16,8,sea_attrs);VBK_REG=0;rf_marine_tint(phase);}
'''.replace('TILE_COUNT',str(len(unique)))
 (out/'include/rockflip_marine.h').write_text(header);(out/'src/rockflip_marine.c').write_text(c)
 installed=out.resolve()==(ROOT/'native/plugins/rockflip/engine').resolve()
 receipt={'installed_native_source':installed,'scope':'original_art_and_native_C_installed_not_compiled_or_observed' if installed else 'staged_original_art_and_native_C_not_installed_or_observed','source_art':str(art/meta['asset']),'source_png_sha256':hashlib.sha256((art/meta['asset']).read_bytes()).hexdigest(),'tiles':len(unique),'vram_pattern_first':96,'vram_pattern_last':max(mapping),'tile_count_limit':128,'palette_slot':3,'font_ui_preserved':True,'quiet_portrait_composition_region':[16,8,112,56],'native_emulator_verified':False,'source_C_sha256':hashlib.sha256(c.encode()).hexdigest()}
 (out/'marine-native-art-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--art-dir',type=Path,default=ROOT/'output/marine-art-work');p.add_argument('--install',action='store_true',help='Write nativeengine files onlyafterparentbuildfinishedsignal');p.add_argument('--output-dir',type=Path);args=p.parse_args()
 destination=args.output_dir or (ROOT/'native/plugins/rockflip/engine' if args.install else ROOT/'output/marine-art-work/native-staging')
 print(json.dumps(emit_marine_content(args.art_dir,destination),indent=2))
