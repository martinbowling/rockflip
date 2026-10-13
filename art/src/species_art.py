"""Original, editable first-wave wildlife artwork; no copied or generated imagery.

Independent 48x48 anatomy drawings (never enlarged guide icons), two deliberately
posed frames and four indexed colors. This module emits source assets only;
biological review, bank allocation and native motion observation remain gates.
Call emit_species_art(output_dir) from the canonical make_sprites.py entry point.
Pixel coordinates and silhouettes are intentionally explicit for hand editing.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw

SPECS = {
 'fence_lizard': ('Sceloporus occidentalis', 'Western fence lizard', [(240,216,160),(40,32,32),(144,120,88),(64,136,208)], 'push_up', 'Side-view belly accent; regional color variants need review.'),
 'newt': ('Taricha torosa', 'California newt', [(192,216,176),(48,32,24),(112,80,48),(240,144,48)], 'slow_step', 'Natural walking only; defensive posture is not a reward.'),
 'chorus_frog': ('Pseudacris regilla', 'Pacific chorus frog', [(192,216,176),(40,48,24),(104,152,64),(224,208,128)], 'breath', 'Northern species identity; do not use for southern chorus frog taxa.'),
 'tiger_salamander': ('Ambystoma californiense', 'California tiger salamander', [(192,216,176),(24,24,32),(64,72,72),(240,208,64)], 'slow_step', 'Protected subject: long-distance photography and no handling.'),
 'island_night_lizard': ('Xantusia riversiana', 'Island night lizard', [(208,192,144),(48,40,24),(128,112,72),(208,184,104)], 'tail_sway', 'No movable eyelids; vertical pupils. Island placement requires reviewed explicit island permissions.'),
 'alligator_lizard': ('Elgaria multicarinata', 'Southern alligator lizard', [(208,216,168),(40,40,24),(136,120,64),(208,176,104)], 'slow_step', 'Long body, short limbs and long tail; no defensive photo bonus.'),
 'banded_gecko': ('Coleonyx variegatus', 'Western banded gecko', [(240,216,160),(56,40,32),(176,112,72),(240,208,144)], 'tail_sway', 'Eyelid blink and slender toes; no adhesive toe pads.'),
 'desert_iguana': ('Dipsosaurus dorsalis', 'Desert iguana', [(240,216,160),(64,48,32),(176,160,112),(232,224,176)], 'breath', 'Slender long tail, blunt head and mottled pale body.'),
 'rosy_boa': ('Lichanura orcutti', 'Rosy boa', [(240,216,160),(56,40,40),(176,96,72),(208,184,136)], 'head_sway', 'Taxon assignment and local stripe expression pending ecologist review.'),
 'western_pond_turtle': ('Emys marmorata', 'Western pond turtle', [(176,208,184),(40,40,24),(104,112,64),(192,184,104)], 'head_lift', 'Northern versus southern pond turtle split pending taxonomy review.'),
 'arboreal_salamander': ('Aneides lugubris', 'Arboreal salamander', [(192,216,176),(48,32,24),(136,104,64),(224,200,144)], 'toe_step', 'Large head and climbing digits; ground-based natural step animation.'),
 'yellow_legged_frog': (None, 'Yellow-legged frog', [(168,216,224),(48,48,32),(144,136,72),(224,192,88)], 'breath', 'Taxon intentionally unresolved: Rana sierrae versus Rana muscosa.')
}

# Independently authored guide silhouettes. 0 is transparent in OBJ artwork.
ICONS = {
 'fence_lizard': ['................','...........11...','..........1221..','..11....112211..','...1211122221...','....122323221...','..11122222211...','..1..122221.1...','......12221.....','.....1221.11....','....1221........','...1221.........','..121...........','..11............','................','................'],
 'newt': ['................','......1111......','.....122221.....','.....121121.....','......1221......','...1.122221.1...','...1122322211...','.....122221.....','.....122221.....','...1122322211...','...1..1221..1...','......1231......','.......1231.....','........12311...','.........1111...','................'],
 'chorus_frog': ['................','................','....11....11....','...1231..1231...','...1211111211...','....12222221....','..111232322111..','.1221222221221..','.1211222221121..','..11122222211...','...1122222211...','..122111111221..','..111......111..','................','................','................'],
 'tiger_salamander': ['................','.....111111.....','....12322331....','....12122121....','.....123221.....','..1.11232211.1..','..111232223111..','.....123221.....','.....132321.....','..111222233111..','..1..123221..1..','......1231......','......1221......','.......12311....','........1111....','................'],
 'island_night_lizard': ['................','......1111......','.....122221.....','.....121121.....','......1221......','...1112323111...','..11.123221.11..','.....132321.....','.....123221.....','..111232323111..','..1..122221..1..','......1221......','......1231......','.......12111....','........1111....','................'],
 'alligator_lizard': ['................','..........111...','.........12221..','.........12121..','.......112221...','..11111232321...','...1222222211...','..1112222221.1..','..1..122221.....','......1221......','.....1221.......','....1221........','...1221.........','..1221..........','.111............','................'],
 'banded_gecko': ['................','.....111111.....','....12322331....','....13122131....','.....122221.....','..1.11222211.1..','..111333333111..','.....122221.....','.....133331.....','..111222222111..','..1..133331..1..','......1221......','......1331......','.......12211....','........1111....','................'],
 'desert_iguana': ['................','..........111...','.........13331..','........113211..','...11.1123231...','....111323221...','...1123232311...','..11.122221.11..','......1231......','.....1231.......','....1231........','...1231.........','..1231..........','.1231...........','.11.............','................'],
 'rosy_boa': ['................','.........1111...','........123321..','....1111123211..','...123333321....','..123222211.....','..123211........','...12331111.....','....12333321....','......1122321...','...1111112321...','..1233333321....','.1232111111.....','.111............','................','................'],
 'western_pond_turtle': ['................','................','......11111.....','....112332211...','...12322322311..','..123232323221..','..132323232321..','..1232323232211.','..12322322322131','...122222221111.','...111111111....','..1331....1331..','..111.....111...','................','................','................'],
 'arboreal_salamander': ['................','.....111111.....','....12222221....','....12322321....','.....122221.....','..1.11232211.1..','..111222222111..','.....123221.....','.....122321.....','..111232222111..','..1..122221..1..','......1221......','......1231......','.......12211....','........1111....','................'],
 'yellow_legged_frog': ['................','................','....11....11....','...1231..1231...','...121111121....','....12222221....','..111232322111..','.1321223221231..','.1311222321131..','..11123222211...','...1122222211...','..133111111331..','..111......111..','................','................','................']
}


def canvas(name, size=(48,48), transparent=False):
    im=Image.new('P',size,0)
    colors=[tuple((c>>3)<<3 for c in rgb) for rgb in SPECS[name][2]]
    im.putpalette([v for rgb in colors for v in rgb]+[0]*756)
    if transparent: im.info['transparency']=0
    return im


def portrait(name, frame=0):
    """Hand-placed native pixel anatomy; every frame uses only indices 0..3."""
    im=canvas(name); d=ImageDraw.Draw(im)
    def line(points,c=1,w=1): d.line(points,fill=c,width=w)
    def oval(box,c=2): d.ellipse(box,fill=c,outline=1)
    def poly(points,c=2): d.polygon(points,fill=c,outline=1)
    def eye(x,y,blink=False,vertical=False):
        if vertical:
            d.rectangle((x,y,x+2,y+2),fill=3);line([(x+1,y),(x+1,y+2)],1)
        else:
            d.rectangle((x,y,x+2,y+2),fill=1);d.point((x,y),fill=3)
        if blink:
            d.rectangle((x,y,x+2,y+2),fill=2); line([(x,y+1),(x+2,y+1)])
    if name in ('newt','tiger_salamander','arboreal_salamander','island_night_lizard','banded_gecko'):
        # Top view: shoulders, four articulated limbs, tail taper and jaw.
        broad=name in ('tiger_salamander','arboreal_salamander','island_night_lizard')
        left,right=(17,31) if broad else (20,28)
        shift=frame if name not in ('island_night_lizard','banded_gecko') else 0
        for y,off in [(19,shift),(30,-shift)]:
            for side in (-1,1):
                bx=left if side<0 else right; ex=bx+side*8
                line([(bx,y),(ex,y-3+off),(ex+side*2,y+2+off)],1,3)
                line([(bx,y),(ex,y-3+off)],2)
                for toe in (-2,0,2): line([(ex+side*2,y+2+off),(ex+side*4,y+toe+3+off)])
        tail=[(24,31),(24,37),(29,41),(36,43+frame)]
        line(tail,1,5);line(tail,3 if name=='newt' else 2,3)
        oval((left,14,right,34)); oval((17 if broad else 19,5,31 if broad else 29,16))
        line([(20,14),(28,14)])
        eye(19 if broad else 20,9,False,name=='island_night_lizard');eye(27 if broad else 26,9,False,name=='island_night_lizard')
        if name=='newt':
            line([(left+1,18),(left+1,30)],3,2);line([(23,17),(23,31)],1)
            line([(24,34),(26,38),(31,41)],3)
        elif name=='tiger_salamander':
            for x,y in [(20,6),(26,7),(18,12),(29,13),(19,18),(27,20),(22,24),(29,27),(18,29),(24,32),(25,37),(30,40)]:
                d.rectangle((x,y,x+2,y+1),fill=3)
            line([(22,17),(22,31)],2)
        elif name=='arboreal_salamander':
            for x,y in [(20,7),(26,11),(19,18),(25,21),(28,25),(20,28),(25,31),(29,40)]: d.point((x,y),3)
            for y in range(20,31,3): line([(left+1,y),(left+3,y+1)],1)
            line([(20,6),(26,6)],3)
        elif name=='island_night_lizard':
            for y in range(17,33,3):
                line([(18,y),(21,y+1),(24,y),(27,y+1),(30,y)],1)
                d.point((20,y),3);d.point((27,y),3)
            for y in range(35,42,2): line([(23,y),(27,y)],1)
        else:
            # Broad soft-looking head, big eyelidded eyes, narrow unpadded toes.
            oval((17,5,31,16),3);eye(18,9,frame==1);eye(28,9,frame==1)
            line([(21,14),(27,14)])
            for y in (18,25,32): d.rectangle((21,y,27,y+2),fill=1);line([(22,y+1),(26,y+1)],2)
            for x,y in [(20,7),(25,6),(23,12),(22,21),(26,29),(29,41)]:d.point((x,y),2)
            line([(24,36),(28,39)],1,2)
    elif name in ('fence_lizard','alligator_lizard','desert_iguana'):
        # Three different side silhouettes. Tail is much longer than body.
        lift=frame*2 if name=='fence_lizard' else frame
        by=25-lift
        tail=[(18,by+1),(12,by+3),(8,33),(4,38),(2,40)]
        line(tail,1,5);line(tail,2,3);line([(8,33),(4,38),(2,40)],1)
        if name=='alligator_lizard':
            oval((13,by-6,34,by+4));poly([(31,by-6),(40,by-8),(45,by-4),(42,by),(32,by)],2)
        elif name=='desert_iguana':
            oval((16,by-8,34,by+4));poly([(30,by-9),(36,by-12),(41,by-11),(43,by-7),(39,by-3),(31,by-3)],3)
        else:
            oval((16,by-7,34,by+4));poly([(30,by-8),(36,by-12),(41,by-11),(43,by-7),(39,by-3),(32,by-3)])
        for x,sgn in [(19,-1),(31,1)]:
            line([(x,by+1),(x+sgn*4,by+6),(x+sgn*6,36)],1,3)
            line([(x,by+1),(x+sgn*4,by+6)],2)
            for toe in (-2,0,2):line([(x+sgn*6,36),(x+sgn*7+toe,38)])
        eye(38,by-9)
        line([(39,by-5),(43,by-5)],1)
        if name=='fence_lizard':
            line([(20,by+2),(28,by+2)],3,2)
            for x in range(18,32,4): poly([(x,by-5),(x+3,by-3),(x+2,by-1)],1)
            for x,y in [(22,by-6),(27,by-5),(33,by-7)]:d.point((x,y),2)
        elif name=='alligator_lizard':
            for x in range(16,33,3):line([(x,by-4),(x+1,by),(x,by+2)],1)
            line([(15,by-5),(32,by-5)],3)
            for x,y in [(13,by+3),(10,by+6),(8,33)]:line([(x,y),(x+2,y+1)],1)
        else:
            for x,y in [(18,by-5),(23,by-6),(28,by-4),(20,by),(26,by+1),(31,by-1),(12,by+4),(8,33)]:
                d.rectangle((x,y,x+1,y+1),fill=3)
            for x in range(19,31,3):d.point((x,by-8),1)
    elif name in ('chorus_frog','yellow_legged_frog'):
        breath=frame
        oval((12,17-breath,36,35));
        # Long folded hind legs versus small articulated forefeet.
        for side in (-1,1):
            x=13 if side<0 else 35
            poly([(x,26),(x+side*8,28),(x+side*10,36),(x+side*3,40),(x,34)],3 if name=='yellow_legged_frog' else 2)
            line([(x,25),(x+side*4,32),(x+side*2,38)],1)
            line([(x+side*2,38),(x+side*7,39)],1,2)
            for t in range(3):line([(x+side*6+t,38),(x+side*6+t,41)],1)
        oval((12,10,21,21),3);oval((27,10,36,21),3)
        eye(15,12,frame==1);eye(30,12,frame==1)
        line([(16,24),(24,26+breath),(32,24)])
        for x in (16,32):line([(x,26),(x-1,34),(x-4,37)],1,2)
        if name=='chorus_frog':
            line([(12,17),(17,20),(22,20)],1,2);line([(36,17),(31,20),(26,20)],1,2)
            for x,y in [(19,27),(27,29),(23,32)]:d.point((x,y),3)
        else:
            for x,y in [(18,19),(25,20),(30,24),(20,29),(27,31),(11,33),(37,32)]:
                d.rectangle((x,y,x+1,y+1),fill=1)
            line([(16,34),(22,35)],3);line([(28,35),(34,34)],3)
    elif name=='rosy_boa':
        points=[(5,38),(10,32),(20,33),(29,36),(38,31),(39,24),(31,20),(20,21),(13,16),(16,9),(29+frame,9)]
        line(points,1,9);line(points,3,7);line(points,2,3)
        oval((28+frame,5,40+frame,13),3);line([(29+frame,7),(37+frame,7)],2,2)
        eye(36+frame,8);line([(40+frame,10),(44+frame,11)],1)
        line([(5,38),(2,41)],1,2)
    elif name=='western_pond_turtle':
        for x,y in [(12,29),(29,30)]:
            poly([(x,y),(x+5,y),(x+4,39),(x-2,39)],2)
            for dx in (0,2,4):line([(x+dx,36),(x+dx-1,39)],3)
        line([(8,31),(3,34),(8,33)],1)
        oval((7,12,36,33));oval((34,24-frame*3,45,30-frame*3),2)
        eye(41,25-frame*3);line([(35,28-frame*3),(40,29-frame*3)],3)
        for x,y in [(11,20),(18,16),(25,16),(30,22),(23,27),(15,27)]:
            poly([(x,y),(x+3,y-2),(x+6,y),(x+5,y+5),(x+1,y+5)],2)
            line([(x+1,y),(x+3,y-1),(x+5,y)],3)
        line([(10,31),(33,31)],1,2)
    return im


def emit_species_art(output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    metadata={};sheet=Image.new('RGB',(4*112,3*72),(208,200,168));d=ImageDraw.Draw(sheet)
    for n,(name,spec) in enumerate(SPECS.items()):
        sci,common,palette,behavior,note=spec
        palette=[tuple((v>>3)<<3 for v in rgb) for rgb in palette]
        icon=canvas(name,(16,16),True)
        assert len(ICONS[name])==16 and all(len(row)==16 for row in ICONS[name])
        for y,row in enumerate(ICONS[name]):
            for x,ch in enumerate(row):icon.putpixel((x,y),0 if ch=='.' else int(ch))
        icon_name=f'critter_{name}.png';icon.save(out/icon_name)
        frames=[]
        for frame in range(2):
            im=portrait(name,frame);filename=f'portrait_{name}_idle{frame}.png';im.save(out/filename);frames.append(filename)
        portrait_name=f'portrait_{name}.png';portrait(name).save(out/portrait_name)
        small=f'portrait32_{name}.png';portrait(name).resize((32,32),Image.Resampling.NEAREST).save(out/small)
        animation=Image.new('P',(96,48));animation.putpalette(portrait(name).getpalette())
        animation.paste(portrait(name,0),(0,0));animation.paste(portrait(name,1),(48,0));animname=f'portrait_{name}_animation.png';animation.save(out/animname)
        rgb555=[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in palette]
        metadata[name]={'art_id':name,'scientific_name_provisional':sci,'common_name':common,'icon':icon_name,'portrait':portrait_name,'portrait32':small,'frames':frames,'animation_sheet':animname,'dimensions':[48,48],'icon_dimensions':[16,16],'palette':palette,'palette_rgb555':rgb555,'frame_duration_ticks':24 if behavior=='push_up' else 36,'behavior_animation':behavior,'review_note':note,'status':'art_authored_pending_biology_and_native_review','taxon_count_approval':False}
        x=(n%4)*112;y=(n//4)*72
        for f in range(2):sheet.paste(portrait(name,f).convert('RGB'),(x+f*50+2,y+2))
        d.text((x+2,y+51),name[:17],fill=(32,32,32));sheet.paste(icon.convert('RGBA'),(x+92,y+52),icon.convert('RGBA'))
    (out/'species-art-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    sheet.resize((896,432),Image.Resampling.NEAREST).save(out/'species-art-contact-sheet_2x.png')
    # Timed source review only. No native gameplay claim is attached to this GIF.
    motion=[]
    for f in range(2):
        page=Image.new('RGB',(4*56,3*56),(208,200,168))
        for n,name in enumerate(SPECS):page.paste(portrait(name,f).convert('RGB'),((n%4)*56+4,(n//4)*56+4))
        motion.append(page.resize((672,504),Image.Resampling.NEAREST))
    motion[0].save(out/'species-art-motion.gif',save_all=True,append_images=motion[1:],duration=600,loop=0)
    return metadata

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('output_dir');args=parser.parse_args()
    emit_species_art(args.output_dir)
