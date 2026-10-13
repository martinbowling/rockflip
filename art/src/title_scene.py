"""Original four-color title illustration, authored at the cartridge's resolution."""
from PIL import Image, ImageDraw
import json

COLORS = [(240, 224, 184), (216, 176, 96), (144, 104, 64), (32, 64, 56)]

def emit_title(out, font):
    from pathlib import Path
    out = Path(out)
    im = Image.new('P', (160, 104), 0)
    im.putpalette(sum((list(c) for c in COLORS), []) + [0]*756)
    d = ImageDraw.Draw(im)
    def words(s, y, scale=1, color=3, shadow=False):
        x = (160-(len(s)*6-1)*scale)//2
        for n,ch in enumerate(s):
            if ch==' ':continue
            for yy,row in enumerate(font[ch].split()):
                for xx,v in enumerate(row):
                    if v=='1':
                        box=(x+(n*6+xx)*scale,y+yy*scale,x+(n*6+xx+1)*scale-1,y+(yy+1)*scale-1)
                        if shadow:d.rectangle(tuple(v+1 for v in box),fill=2)
        for n,ch in enumerate(s):
            if ch==' ':continue
            for yy,row in enumerate(font[ch].split()):
                for xx,v in enumerate(row):
                    if v=='1':d.rectangle((x+(n*6+xx)*scale,y+yy*scale,x+(n*6+xx+1)*scale-1,y+(yy+1)*scale-1),fill=color)
    # A field-journal border and a deliberately condensed, shaded logo.
    d.line((8,4,151,4),fill=2);d.line((8,25,151,25),fill=1)
    words('ROCK FLIP',8,2,3,True)
    words('WILDLIFE PHOTO HIKE',29)
    words('CALIFORNIA',40,1,2)
    d.ellipse((132,47,146,61),fill=1)
    d.line((5,53,23,53),fill=1);d.line((10,50,20,50),fill=1)
    # Coast, Sierra ridgeline, forest and desert are a title montage, not a
    # biological claim that the depicted habitats share a wildlife locality.
    ridge=[(0,74),(12,66),(21,70),(38,59),(49,65),(63,51),(77,64),(88,60),(103,70),(118,62),(133,68),(159,61),(159,104),(0,104)]
    d.polygon(ridge,fill=2)
    d.line(ridge[:14],fill=3)
    d.polygon([(53,61),(63,51),(72,60),(65,58),(61,60),(59,57)],fill=0)
    d.polygon([(0,81),(21,77),(37,82),(49,85),(45,103),(0,103)],fill=3)
    for x,y,w in [(1,85,13),(9,90,20),(0,96,17),(25,85,9)]:d.line((x,y,x+w,y),fill=0)
    d.polygon([(33,89),(58,76),(82,83),(114,75),(144,82),(159,76),(159,103),(33,103)],fill=1)
    d.line([(40,100),(64,92),(81,95),(102,90),(117,95),(159,92)],fill=2)
    # Open branch clusters retain the game's irregular native foliage style.
    d.line((15,64,15,86),fill=3,width=2)
    for y,w in [(64,4),(68,7),(73,9),(78,11)]:
        d.line((15-w,y+3,15,y,15+w,y+2),fill=3,width=2)
    d.line((147,80,147,99),fill=3,width=3)
    d.line((147,86,139,81,138,73),fill=3,width=2)
    d.line((147,84,154,79,154,70),fill=3,width=2)
    for x,y in [(137,73),(146,78),(154,70)]:
        d.line((x-4,y-3,x+4,y+2),fill=3);d.line((x-3,y+3,x+3,y-3),fill=3);d.line((x,y-5,x,y+4),fill=3)
    # Reuse the original explorer's authored camera pose and tortoise body.
    actions=Image.open(out/'player_actions.png')
    order=json.loads((out/'player-actions.json').read_text())['order']
    k=order.index('camera_right_1')
    hero=actions.crop((k*16,0,k*16+16,24))
    animal=Image.open(out/'portrait_tortoise_idle0.png')
    for src,ox,oy,mapping in [(hero,49,76,{1:0,2:2,3:3}),(animal,88,57,{1:3,2:2,3:1})]:
        for y in range(src.height):
            for x in range(src.width):
                v=src.getpixel((x,y))
                if v and 0<=oy+y<104:im.putpixel((ox+x,oy+y),mapping[v])
    for x,y in [(73,98),(85,87),(134,96),(128,84)]:
        d.line((x-2,y,x+3,y),fill=2);d.point((x,y-1),fill=0)
    d.line((0,103,159,103),fill=3)
    im.save(out/'title_scene.png')
    im.resize((640,416),Image.Resampling.NEAREST).save(out/'title_scene_4x.png')
    (out/'title_scene.json').write_text(json.dumps({'width':160,'height':104,'colors':COLORS,'status':'authored_source_not_native_observed'},indent=2)+'\n')
