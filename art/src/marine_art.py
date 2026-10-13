"""Original indexed marine viewing backdrop, not shoreline wildlife coordinates.
The calm central ground matches portrait index0 across all supported aim offsets;
edge wave ribbons imply openwater without texture rectangles behind BG portraits.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
PALETTE=[(152,200,216),(104,176,200),(48,128,160),(24,64,96)]

def emit_marine_art(output_dir):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
 im=Image.new('P',(128,64),0);im.putpalette([v for c in PALETTE for v in c]+[0]*756);d=ImageDraw.Draw(im)
 # Open sea, not terrestrial ground. Leave x16..111/y8..55 atlightblue0 so
 # all32/48px portraits and legal horizontal aiming offsets composite cleanly.
 for x in range(0,128,24):
  d.line([(x,2),(x+7,2),(x+9,1),(x+16,1),(x+19,2)],fill=1)
  d.line([(x+3,6),(x+10,6),(x+13,5),(x+20,5)],fill=2)
 for x in range(0,128,32):
  d.line([(x,59),(x+9,59),(x+12,58),(x+20,58),(x+24,59)],fill=1)
  d.line([(x+5,62),(x+12,62)],fill=2)
 for y in (15,27,39,51):
  d.line([(1,y),(6,y),(8,y-1),(12,y-1)],fill=1)
  d.line([(115,y+1),(119,y+1),(122,y),(126,y)],fill=2)
 d.line([(0,0),(127,0)],fill=3)
 filename='marine_photo.png';im.save(out/filename)
 im.resize((512,256),Image.Resampling.NEAREST).save(out/'marine_photo_4x.png')
 manifest={'asset':filename,'dimensions':[128,64],'palette':PALETTE,'palette_rgb555':[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in PALETTE],'bg_palette_slot':3,'vram_bank':0,'pattern_first_tile':96,'screen_tile_origin':[2,4],'portrait_palette_slot':5,'portrait_ground_index':0,'quiet_portrait_region':[16,8,112,56],'mechanic_requirement':'long_distance_shore_observation_no_handling','subject_species_ids':[61,73],'scene':'fictional_openwater_camera_frame','source_status':'authored_not_native_or_human_verified','pixels_sha256':hashlib.sha256(im.tobytes()).hexdigest()}
 assert im.mode=='P' and set(im.get_flattened_data())=={0,1,2,3}
 assert all(im.getpixel((x,y))==0 for y in range(8,56) for x in range(16,112))
 assert all(c%8==0 for rgb in PALETTE for c in rgb)
 (out/'marine-art-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('output_dir');args=p.parse_args();emit_marine_art(args.output_dir)
