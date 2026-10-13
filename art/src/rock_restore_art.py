"""Original indexed loose-stone restoration poses for the canonical art entrypoint.
Endpoints always follow the editable canonical TILES; intermediatepixels original.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw

def emit_rock_restore_art(output_dir,tiles_source,palette):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    def blank():
     im=Image.new('P',(16,16),0);im.putpalette([v for rgb in palette for v in rgb]+[0]*756);return im
    frames=[]
    for name in ('rock_flipped','rock'):
     im=blank();im.putdata([int(v) for row in tiles_source[name][1] for v in row]);frames.append(im)
    # Damp underside shrinks beneath a stone that settles over its original footprint.
    settle=blank();d=ImageDraw.Draw(settle);d.ellipse((1,7,13,14),fill=2)
    d.polygon([(7,1),(13,2),(15,6),(12,12),(7,12),(4,6)],fill=1,outline=3);d.line([(8,3),(12,4),(13,6)],fill=0);d.line([(8,8),(12,10)],fill=2);d.point((3,12),fill=3)
    close=blank();d=ImageDraw.Draw(close);d.ellipse((2,9,13,14),fill=2)
    d.polygon([(3,4),(9,3),(14,6),(15,10),(11,14),(5,13),(1,9)],fill=1,outline=3);d.polygon([(3,9),(8,8),(13,10),(11,13),(5,12)],fill=2);d.line([(4,6),(7,5),(10,6)],fill=0);d.line([(7,8),(9,7)],fill=3)
    frames=[frames[0],settle,close,frames[1]]
    names=[]
    for n,im in enumerate(frames):
        assert im.mode=='P' and im.size==(16,16) and set(im.get_flattened_data())<={0,1,2,3}
        name=f'rock_restore_{n}.png';im.save(out/name);names.append(name)
    sheet=Image.new('RGB',(96,24),tuple(palette[0]))
    for n,im in enumerate(frames):sheet.paste(im.convert('RGB'),(n*24+4,4))
    sheet.resize((576,144),Image.Resampling.NEAREST).save(out/'rock_restore_storyboard_6x.png')
    meta={'frames':names,'palette':palette,'dimensions':[16,16],'frame_VBlank_ticks':[8,8,8,2],'mechanic':'loose_stone_type0_only','status':'authored_source_pending_native_and_human_review','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'rock-restore-art-manifest.json').write_text(json.dumps(meta,indent=2)+'\n');return meta
