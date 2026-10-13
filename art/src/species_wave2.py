"""Original second-wave native pixel artwork, independently posed at 48px.

This is source production, not biological signoff or native observation. Exact
identities and broad permission metadata are read from production_roster.json;
no coordinates, photos, tracing or species substitutions are used. Icons are
separate 16px geometry; portraits never enlarge guide pixels. Hand-edit the
profiles, points, palette indices and markings below. canonical make_sprites.py
may invoke emit_species_wave2(output_dir) after review.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
# ID, independent art ID, anatomical drawing plan, native RGB555 palette.
SELECTION=[
(18,'sw_pond_turtle','turtle',[(176,208,192),(32,40,24),(96,104,56),(200,184,104)]),
(19,'northwestern_salamander','nw_salamander',[(184,208,176),(24,32,24),(80,88,64),(160,168,112)]),
(21,'western_toad','western_toad',[(192,208,160),(40,40,24),(120,120,72),(216,200,128)]),
(24,'great_plains_toad','plains_toad',[(232,216,160),(48,40,24),(136,136,72),(224,216,152)]),
(25,'black_toad','black_toad',[(192,208,184),(24,24,24),(56,64,56),(208,208,176)]),
(32,'temblor_legless_lizard','legless',[(232,216,176),(48,40,32),(136,112,72),(208,176,104)]),
(35,'coastal_tailed_frog','tailed_frog',[(176,208,200),(40,32,24),(136,104,64),(216,184,112)]),
(36,'orange_throated_whiptail','whiptail',[(208,216,160),(40,32,24),(136,128,72),(224,136,48)]),
(41,'inyo_mtns_salamander','inyo_slender',[(216,208,168),(40,32,24),(112,96,56),(192,176,112)]),
(43,'san_gabriel_salamander','gabriel_slender',[(192,208,168),(32,32,24),(96,88,64),(176,152,104)]),
(59,'northern_rubber_boa','rubber_boa',[(192,208,168),(40,40,24),(136,128,80),(200,184,128)]),
(64,'common_sharp_tail','sharp_tail',[(192,208,168),(48,32,24),(136,96,64),(208,184,136)]),
(65,'western_diamondback','diamondback',[(232,216,168),(48,40,32),(160,144,104),(224,216,176)]),
(72,'baja_collared_lizard','collared',[(232,216,160),(24,40,40),(104,152,128),(216,184,88)]),
(78,'panamint_alligator','panamint',[(232,216,168),(48,40,24),(144,120,64),(216,192,128)]),
(81,'blunt_nosed_leopard','leopard',[(216,208,160),(48,40,24),(160,144,88),(224,208,128)]),
(87,'shasta_salamander','web_foot',[(192,208,184),(32,40,32),(104,104,64),(200,200,136)]),
(94,'striped_whipsnake','whipsnake',[(216,216,168),(32,40,32),(96,112,64),(216,208,128)]),
(97,'pygmy_horned_lizard','pygmy_horned',[(208,216,160),(48,40,24),(128,112,64),(216,184,104)]),
(99,'peninsula_leaf_toed','leaf_gecko',[(232,216,168),(48,32,24),(168,128,80),(232,200,136)]),
(103,'western_skink','skink',[(192,208,168),(40,32,24),(136,112,56),(72,144,208)]),
(108,'california_treefrog','treefrog',[(184,208,200),(40,40,32),(144,144,120),(208,200,160)]),
(116,'southern_torrent_salamander','torrent',[(168,208,200),(40,48,24),(136,144,64),(224,176,64)]),
(125,'great_basin_spadefoot','spadefoot',[(208,216,168),(40,40,24),(136,144,72),(224,200,104)]),
]
BY_NAME={art:(sid,kind,palette) for sid,art,kind,palette in SELECTION}

class Pen:
    def __init__(self,im):self.im=im;self.d=ImageDraw.Draw(im)
    def line(self,points,c=1,w=1):self.d.line(points,fill=c,width=w)
    def oval(self,box,c=2):self.d.ellipse(box,fill=c,outline=1)
    def poly(self,points,c=2):self.d.polygon(points,fill=c,outline=1)
    def point(self,xy,c=3):self.d.point(xy,fill=c)
    def eye(self,x,y,vertical=False,blink=False):
        self.d.rectangle((x,y,x+3,y+3),fill=3)
        self.line([(x+1,y),(x+1,y+3)],1) if vertical else self.line([(x,y+1),(x+3,y+1)],1)
        if blink:self.d.rectangle((x,y,x+3,y+3),fill=2);self.line([(x,y+2),(x+3,y+2)],1)


def canvas(art,size=(48,48),transparent=False):
    im=Image.new('P',size,0);pal=BY_NAME[art][2]
    im.putpalette([v for rgb in pal for v in rgb]+[0]*756)
    if transparent:im.info['transparency']=0
    return im


def portrait(art,frame=0):
    sid,kind,palette=BY_NAME[art];im=canvas(art);p=Pen(im)
    if kind in ('legless','rubber_boa','sharp_tail','diamondback','whipsnake'):
        # Entirely different coiling thickness/profile, not recolored snake art.
        paths={
          'legless':[(3,39),(9,33),(19,34),(28,30),(31,22),(22,18),(16,12),(20,7),(31,8)],
          'rubber_boa':[(7,37),(10,30),(18,29),(26,35),(36,34),(39,26),(32,21),(20,21),(16,15),(23,10),(33,11)],
          'sharp_tail':[(2,42),(8,35),(15,30),(26,34),(36,30),(35,23),(24,21),(15,16),(19,10),(31,9)],
          'diamondback':[(5,39),(7,30),(18,28),(29,34),(38,29),(39,22),(31,18),(21,18),(17,11),(26,8)],
          'whipsnake':[(2,42),(8,37),(13,31),(21,33),(31,35),(40,31),(41,24),(34,19),(24,21),(17,15),(23,9),(35,8)]}
        path=list(paths[kind]);path[-1]=(path[-1][0]+frame,path[-1][1]-frame)
        width={'legless':5,'rubber_boa':9,'sharp_tail':5,'diamondback':9,'whipsnake':5}[kind]
        p.line(path,1,width);p.line(path,2,width-2)
        if kind=='diamondback':
            for x,y in [(7,33),(13,29),(20,29),(29,33),(37,28),(35,20),(26,18),(19,14),(22,9)]:
                p.poly([(x,y-2),(x+3,y),(x,y+2),(x-3,y)],3);p.point((x,y),1)
            p.poly([(28+frame,3-frame),(37+frame,3-frame),(41+frame,8-frame),(37+frame,13-frame),(29+frame,12-frame),(26+frame,8-frame)],2)
            for y in (33,36,39):p.line([(4,y),(8,y)],3,2)
            for y in (40,42,44):p.oval((3,y,7,y+2),3)
            p.eye(34+frame,6-frame,True)
        else:
            x,y=path[-1];p.oval((x-3,y-3,x+7,y+3),2);p.eye(x+3,y-1)
            if kind in ('whipsnake','legless'):
                p.line(path,3,1);p.line([(x-2,y+1),(x+5,y+1)],3)
            elif kind=='sharp_tail':
                for x,y in [(7,36),(15,31),(24,33),(34,29),(29,21),(17,16)]:p.line([(x,y),(x+2,y+2)],3)
                p.line([(2,42),(0,45)],1)
            else:p.line([(10,32),(17,31),(25,36),(34,35)],3,1);p.line([(4,39),(7,37)],2,4)
            if frame:p.line([(x+7,y+1),(x+11,y+1),(x+12,y)],1)
    elif kind=='turtle':
        # Shell profile and thick neck, four clawed feet remain grounded.
        for x in (11,29):
            p.poly([(x,28),(x+6,28),(x+5,39),(x-1,39)],2)
            for t in (0,2,4):p.line([(x+t,37),(x+t-1,40)],3)
        p.line([(8,31),(3,34),(7,33)],1);p.oval((7,12,36,33))
        for x,y in [(12,17),(21,15),(29,20),(15,25),(25,25)]:
            p.poly([(x,y),(x+3,y-2),(x+6,y+1),(x+5,y+5),(x+1,y+5)],2)
            p.line([(x+1,y),(x+4,y)],3)
        p.oval((34,23-frame*2,45,30-frame*2));p.eye(40,24-frame*2)
        p.line([(35,29-frame*2),(41,29-frame*2)],3)
    elif kind in ('western_toad','plains_toad','black_toad','tailed_frog','treefrog','spadefoot'):
        broad=kind in ('western_toad','plains_toad');top=18-frame
        l,r=(11,37) if broad else (15,33)
        p.oval((l,top,r,35),2)
        # Six separately posed frog/toad anatomies and foot treatment.
        for side in (-1,1):
            x=l if side<0 else r
            if kind=='tailed_frog':p.poly([(x,24),(x+side*7,29),(x+side*10,35),(x+side*5,38),(x,31)],2)
            elif kind=='treefrog':p.poly([(x,24),(x+side*6,28),(x+side*8,37),(x+side*2,40),(x,32)],2)
            else:p.poly([(x,25),(x+side*7,28),(x+side*8,37),(x+side*2,40),(x,33)],2)
            p.line([(x+side*3,30),(x+side*4,37),(x+side*7,38)],1)
            for t in range(3):
                p.line([(x+side*5+t,37),(x+side*5+t,40)],1)
                if kind=='treefrog':p.oval((x+side*5+t-1,39,x+side*5+t+1,41),3)
            if kind=='spadefoot':p.line([(x+side*6,38),(x+side*8,39)],1,3)
        head_l=12 if broad else 15;head_r=36 if broad else 33
        p.oval((head_l,11,head_r,25),2);p.oval((head_l,10,head_l+8,18),3);p.oval((head_r-8,10,head_r,18),3)
        p.eye(head_l+2,11,kind in ('tailed_frog','spadefoot'),frame==1)
        p.eye(head_r-5,11,kind in ('tailed_frog','spadefoot'),frame==1)
        p.line([(18,24),(24,26+frame),(30,24)],1)
        for side in (-1,1):
            x=18 if side<0 else 30
            p.line([(x,28),(x+side*2,35),(x+side*5,37)],1,2)
        if kind=='western_toad':
            p.line([(24,17),(24,33)],3,2)
            for x,y in [(15,20),(30,21),(18,28),(31,29),(14,34),(34,34)]:p.oval((x,y,x+2,y+2),2)
            p.oval((12,18,18,23),2);p.oval((30,18,36,23),2)
        elif kind=='plains_toad':
            for x,y in [(16,20),(26,20),(16,27),(27,27)]:p.oval((x,y,x+5,y+5),3);p.oval((x+1,y+1,x+4,y+4),1)
            p.line([(24,16),(24,33)],3)
        elif kind=='black_toad':
            for x,y in [(18,19),(26,20),(20,25),(29,27),(18,31),(25,34),(12,34),(35,35)]:p.point((x,y),3)
        elif kind=='tailed_frog':
            p.line([(15,17),(18,20),(22,20)],1,2);p.line([(33,17),(29,20),(26,20)],1,2)
            p.poly([(21,34),(24,41),(26,42),(27,39),(25,34)],2)
            for x,y in [(21,22),(29,27),(21,31)]:p.point((x,y),3)
        elif kind=='treefrog':
            for x,y in [(21,18),(28,20),(18,25),(27,28),(22,31)]:p.oval((x,y,x+2,y+1),1)
            p.line([(17,22),(19,23)],3);p.line([(29,23),(32,22)],3)
        else:
            p.line([(19,18),(20,26),(18,31)],3);p.line([(29,18),(28,26),(30,31)],3)
            for x,y in [(23,21),(24,27),(21,32)]:p.point((x,y),1)
    elif kind in ('nw_salamander','inyo_slender','gabriel_slender','web_foot','torrent'):
        # Deliberately separate body plans: robust ambystomatid, two slender
        # species with distinct curved posture, squat webfeet and slim torrent.
        if kind=='nw_salamander':head=(15,5,33,17);body=(17,15,31,34);tail=[(24,32),(25,37),(32,41),(38,41)]
        elif kind=='web_foot':head=(13,8,35,18);body=(16,16,32,32);tail=[(24,30),(26,36),(29,38)]
        elif kind=='torrent':head=(18,6,30,16);body=(20,14,28,32);tail=[(24,30),(25,36),(29,41),(34,43)]
        elif kind=='inyo_slender':head=(26,5,34,12);body=None;tail=[(24,29),(22,35),(26,41),(31,44)]
        else:head=(19,4,29,12);body=(21,11,27,29);tail=[(24,28),(26,34),(34,38),(40,43)]
        p.line(tail,1,6 if kind in ('nw_salamander','web_foot') else 4);p.line(tail,2,4 if kind in ('nw_salamander','web_foot') else 2)
        if body:p.oval(body)
        else:p.line([(30,11),(28,17),(24,23),(24,31)],1,7);p.line([(30,11),(28,17),(24,23),(24,31)],2,5)
        p.oval(head);p.eye(head[0]+2,head[1]+3);p.eye(head[2]-5,head[1]+3)
        for y in (18,28):
            for side in (-1,1):
                bx=(18 if side<0 else 30) if kind in ('nw_salamander','web_foot') else (21 if side<0 else 27)
                if kind=='inyo_slender':bx=25 if side<0 else 30
                ex=bx+side*(8 if kind in ('nw_salamander','web_foot') else 5)
                shift=frame if (y==18 and side<0) or (y==28 and side>0) else 0
                p.line([(bx,y),(ex,y-2),(ex+side,y+3-shift)],1,3 if kind in ('nw_salamander','web_foot') else 2)
                p.line([(bx,y),(ex,y-2)],2)
                if kind=='web_foot':
                    p.poly([(ex-3,y+2-shift),(ex+3,y+2-shift),(ex+4,y+6-shift),(ex-4,y+6-shift)],3)
                    for t in (-2,0,2):p.line([(ex,y+3-shift),(ex+t,y+6-shift)],1)
                else:
                    # Individually placed small digits; slender Batrachoseps
                    # silhouette keeps its famously minute limbs instead of
                    # copying a bulky tiger-salamander shoulder construction.
                    digits=(-2,-1,1,2) if y==18 or kind in ('inyo_slender','gabriel_slender') else (-2,-1,0,1,2)
                    for t in digits:p.line([(ex+side,y+3-shift),(ex+side+t,y+5-shift)],1)
        if kind=='nw_salamander':
            p.oval((15,14,19,20),2);p.oval((29,14,33,20),2)
            for y in range(20,32,3):p.line([(18,y),(21,y+1)],1);p.line([(27,y+1),(30,y)],1)
            p.line([(20,7),(28,7)],2)
        elif kind=='web_foot':
            for x,y in [(18,12),(29,12),(18,22),(27,24),(22,28),(26,35)]:p.point((x,y),3)
            p.line([(17,20),(18,28)],1)
        elif kind=='torrent':
            p.line([(21,16),(21,29)],3,2);p.line([(26,17),(26,30)],3)
            for x,y in [(21,9),(27,12),(24,20),(24,25),(25,35)]:p.point((x,y),1)
            p.line([(24,32),(26,37),(30,40)],3)
        elif kind=='inyo_slender':
            p.line([(30,12),(28,17),(25,22),(25,30)],3)
            for x,y in [(28,15),(26,20),(23,26),(23,35)]:p.point((x,y),1)
        else:
            p.line([(24,12),(24,27)],3,2)
            for y in range(14,28,3):p.point((21,y),1);p.point((27,y),1)
            p.line([(28,34),(34,38)],3)
    else:
        # Lizards are side-profile except wide horned/leaf-toed forms. Species
        # have explicit skull, trunk, foot, scale and tail differences.
        if kind in ('pygmy_horned','leaf_gecko'):
            fat=kind=='pygmy_horned';left,right=(13,35) if fat else (19,29)
            p.line([(24,31),(24,37),(28+frame,42),(33+frame,43)],1,6 if fat else 4)
            p.line([(24,31),(24,37),(28+frame,42),(33+frame,43)],2,4 if fat else 2)
            for y in (19,30):
                for side in (-1,1):
                    bx=left if side<0 else right;ex=bx+side*(6 if fat else 8)
                    p.line([(bx,y),(ex,y-3),(ex+side,y+3)],1,3)
                    for t in (-3,-1,1,3):
                        p.line([(ex+side,y+3),(ex+side+t,y+5-frame)],1)
                        if not fat:p.oval((ex+side+t-1,y+4-frame,ex+side+t+1,y+6-frame),3)
            p.oval((left,14,right,34));p.oval((16 if fat else 17,5,32 if fat else 31,17))
            p.eye(18,9,not fat,frame==1 and fat);p.eye(27,9,not fat,frame==1 and fat)
            if fat:
                for x,y in [(16,8),(20,5),(28,5),(32,8)]:p.poly([(x,y+2),(x-1,y-2),(x+2,y)],1)
                for y in (20,25,30):
                    p.poly([(left,y),(left-2,y),(left,y+3)],1);p.poly([(right,y),(right+2,y),(right,y+3)],1)
                for x,y in [(18,19),(25,20),(30,25),(20,29),(27,31)]:p.poly([(x,y),(x+2,y-1),(x+3,y+2)],3)
            else:
                for x,y in [(20,7),(25,12),(22,18),(27,22),(22,27),(25,32)]:p.oval((x,y,x+2,y+1),1)
        else:
            lift=frame if kind in ('collared','leopard') else 0
            y=24-lift
            profiles={'whiptail':(17,32,6),'collared':(16,33,8),'panamint':(12,35,5),'leopard':(17,33,7),'skink':(15,33,4)}
            l,r,h=profiles[kind]
            tail=[(l+1,y+1),(10,y+5),(6,35),(2,42)]
            p.line(tail,1,4 if kind in ('skink','whiptail') else 5);p.line(tail,3 if kind=='skink' else 2,2 if kind in ('skink','whiptail') else 3)
            p.oval((l,y-h,r,y+4));p.poly([(r-2,y-h),(37,y-h-4),(43,y-h-2),(44,y-h+3),(38,y-h+6),(r,y)],2)
            for x,side in ((l+4,-1),(r-2,1)):
                knee=(x+side*4+(frame if side>0 else 0),y+7-(frame if side>0 else 0));foot=(x+side*5,37)
                p.line([(x,y+1),knee,foot],1,3 if kind in ('collared','leopard') else 2)
                p.line([(x,y+1),knee],2)
                for t in (-2,-1,0,1,2):p.line([foot,(foot[0]+t,39)],1)
            p.eye(38,y-h)
            if kind=='whiptail':
                for off in (-3,0,3):p.line([(19,y+off),(30,y+off-1)],3)
                p.line([(34,y-1),(40,y-1)],3,2)
            elif kind=='collared':
                p.line([(31,y-h),(30,y+2)],1,3);p.line([(34,y-h),(33,y)],1,2)
                for x,dy in [(19,-4),(24,-5),(27,-1),(20,1),(25,3)]:p.point((x,y+dy),3)
            elif kind=='leopard':
                for x,dy in [(19,-4),(25,-5),(29,-2),(21,1),(27,2),(13,6),(7,13)]:p.oval((x,y+dy,x+2,y+dy+2),1)
                p.line([(39,y-h+4),(43,y-h+4)],1)
            elif kind=='panamint':
                for x in range(15,35,3):p.line([(x,y-3),(x+1,y+2)],1)
                p.line([(14,y-4),(33,y-4)],3)
            else:
                p.line([(16,y-2),(30,y-3),(39,y-h+1)],3)
                p.line([(17,y+1),(31,y)],1)
                # Foreleg knee articulation above supplies grounded motion.
    return im


def icon(art):
    """Independent low-resolution native silhouette, never portrait resizing."""
    sid,kind,pal=BY_NAME[art];im=canvas(art,(16,16),True);p=Pen(im)
    if kind in ('legless','rubber_boa','sharp_tail','diamondback','whipsnake'):
        points=([(1,14),(4,10),(9,11),(14,9),(12,6),(8,6),(7,3),(12,2)] if kind=='whipsnake' else [(1,13),(4,10),(9,12),(13,10),(12,7),(6,6),(7,3),(12,3)])
        width=4 if kind in ('rubber_boa','diamondback') else 3
        p.line(points,1,width);p.line(points,2,width-1);p.oval((10,1,14,4),2);p.point((13,2),3)
        if kind in ('legless','whipsnake'):p.line(points,3)
        elif kind=='diamondback':
            for xy in [(3,10),(8,11),(12,9),(9,6),(7,3)]:p.point(xy,3)
            p.line([(1,12),(1,15)],3,2)
        elif kind=='sharp_tail':p.line([(0,15),(2,12)],1);p.line([(5,10),(6,12)],3)
    elif kind=='turtle':
        p.oval((2,4,12,11));p.oval((11,8,15,11));p.point((14,9),3)
        for x in (4,10):p.poly([(x,10),(x+2,10),(x+1,14),(x-1,14)],2)
        for x,y in [(4,6),(8,5),(6,8),(9,8)]:p.poly([(x,y),(x+2,y),(x+2,y+2),(x,y+2)],3)
    elif kind in ('western_toad','plains_toad','black_toad','tailed_frog','treefrog','spadefoot'):
        p.oval((4,5,12,12));p.oval((3,3,6,7),3);p.oval((10,3,13,7),3)
        p.point((5,5),1);p.point((11,5),1)
        p.poly([(5,8),(1,9),(1,13),(5,14),(6,11)],2);p.poly([(11,8),(15,9),(15,13),(11,14),(10,11)],2)
        p.line([(6,8),(10,8)],1)
        if kind=='tailed_frog':p.line([(8,12),(8,15)],2,2);p.line([(3,6),(6,7)],1)
        elif kind=='western_toad':p.line([(8,5),(8,11)],3)
        elif kind=='plains_toad':
            for xy in [(5,8),(10,8),(6,11),(9,11)]:p.oval((xy[0],xy[1],xy[0]+1,xy[1]+1),3)
        elif kind=='black_toad':
            for xy in [(5,8),(9,9),(7,11),(13,11)]:p.point(xy,3)
        elif kind=='treefrog':p.point((3,13),3);p.point((13,13),3);p.point((7,7),1)
        else:p.line([(5,7),(5,11)],3);p.line([(11,7),(11,11)],3)
    elif kind in ('nw_salamander','inyo_slender','gabriel_slender','web_foot','torrent'):
        fat=kind in ('nw_salamander','web_foot');l,r=(5,11) if fat else (7,9)
        p.oval((l-1,1,r+1,5));p.oval((l,4,r,11));p.point((l,3),3);p.point((r,3),3)
        if kind=='inyo_slender':
            # Natural curved slender posture, not a fabricated diagnosticmark.
            p.line([(10,4),(9,7),(8,10)],1,3);p.line([(10,4),(9,7),(8,10)],2)
        elif kind=='torrent':
            p.oval((6,1,11,5));p.point((7,3),3);p.point((10,3),3)
        for y in (6,10):
            p.line([(l,y),(l-3,y+1),(l-3,y+3)],1,2 if fat else 1)
            p.line([(r,y),(r+3,y+1),(r+3,y+3)],1,2 if fat else 1)
            if kind=='web_foot':p.oval((l-4,y+2,l-2,y+4),3);p.oval((r+2,y+2,r+4,y+4),3)
        p.line([(8,10),(8,13),(12,15)],1,3 if fat else 2);p.line([(8,10),(8,13),(12,15)],2)
        if kind in ('inyo_slender','gabriel_slender'):p.line([(8,5),(8,11)],3)
        elif kind=='torrent':p.line([(7,6),(7,10)],3);p.line([(9,6),(9,10)],3)
        if kind=='nw_salamander':p.line([(5,7),(6,8)],1)
        if kind=='web_foot':p.point((7,8),3)
    elif kind in ('pygmy_horned','leaf_gecko'):
        fat=kind=='pygmy_horned';l,r=(3,13) if fat else (6,10)
        p.oval((5,1,11,5));p.oval((l,4,r,11));p.point((6,3),3);p.point((10,3),3)
        for y in (5,10):p.line([(l,y),(l-2,y+2)],1,2);p.line([(r,y),(r+2,y+2)],1,2)
        p.line([(8,10),(8,13),(11,14)],1,3);p.line([(8,10),(8,13),(11,14)],2)
        if fat:
            for x in (5,8,11):p.point((x,0),1)
            for xy in [(5,6),(10,6),(7,9)]:p.point(xy,3)
        else:
            for x,y in [(4,7),(12,7),(4,12),(12,12)]:p.oval((x-1,y-1,x+1,y+1),3)
            p.point((7,6),1);p.point((9,9),1)
    else:
        p.line([(6,8),(3,11),(1,15)],1,3);p.line([(6,8),(3,11),(1,15)],3 if kind=='skink' else 2)
        p.oval((4,5,12,10));p.poly([(10,5),(12,2),(15,3),(15,6),(12,7)],2);p.point((13,3),3)
        p.line([(6,9),(4,13)],1,2);p.line([(10,9),(13,12)],1,2)
        if kind=='collared':p.line([(11,5),(10,8)],1,2)
        elif kind=='leopard':
            for xy in [(6,6),(8,8),(10,6)]:p.point(xy,1)
        elif kind=='panamint':
            for x in (6,8,10):p.line([(x,6),(x,9)],1)
        else:p.line([(5,7),(11,6)],3)
    return im


def emit_species_wave2(output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    registry={r['species_id']:r for r in json.loads((ROOT/'data/production_roster.json').read_text())['records']}
    result={};sheet=Image.new('RGB',(6*110,4*76),(208,200,168));label=ImageDraw.Draw(sheet)
    for n,(sid,art,kind,palette) in enumerate(SELECTION):
        record=registry[sid];frames=[]
        for f in range(2):
            filename=f'portrait_{art}_idle{f}.png';portrait(art,f).save(out/filename);frames.append(filename)
        portrait_name=f'portrait_{art}.png';portrait(art).save(out/portrait_name)
        small=f'portrait32_{art}.png';portrait(art).resize((32,32),Image.Resampling.NEAREST).save(out/small)
        icon_name=f'critter_{art}.png';icon(art).save(out/icon_name)
        anim=canvas(art,(96,48));anim.paste(portrait(art,0),(0,0));anim.paste(portrait(art,1),(48,0));anim_name=f'portrait_{art}_animation.png';anim.save(out/anim_name)
        metadata={'art_id':art,'species_id':sid,'canonical_scientific_name':record['canonical_scientific_name'],'scientific_name_provisional':record['canonical_scientific_name'],'common_name':record['common_name'],'icon':icon_name,'portrait':portrait_name,'portrait32':small,'frames':frames,'animation_sheet':anim_name,'dimensions':[48,48],'icon_dimensions':[16,16],'palette':palette,'palette_rgb555':[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in palette],'frame_duration_ticks':36,'behavior_animation':{'turtle':'head_lift','diamondback':'quiet_head_sway','rubber_boa':'head_sway','sharp_tail':'head_sway','whipsnake':'head_sway','legless':'head_sway'}.get(kind,'grounded_step' if kind in ('nw_salamander','inyo_slender','gabriel_slender','web_foot','torrent','whiptail','panamint','skink') else 'grounded_body_raise' if kind in ('collared','leopard') else 'tail_toe_sway' if kind=='leaf_gecko' else 'blink_tail_sway' if kind=='pygmy_horned' else 'breath_blink'),'status':'art_only_pending_independent_anatomy_and_native_review','taxon_count_approval':False,'anatomy_plan':kind,'allowed_districts_from_roster':[r['region_id'] for r in record['region_permissions']],'review_notes':['Source art only; range permission is inherited metadata, not new biological signoff.','Native composition, readability, animation timing and ecological text remain production gates.']}
        if kind=='tailed_frog':metadata['review_notes'].append('Adult male artwork: tail is reproductive anatomy, not a defensive display or collectible variant.')
        if kind=='skink':metadata['review_notes'].append('Blue-tail age/color expression needs final anatomy review; life stage never adds a species slot.')
        result[art]=metadata;x=(n%6)*110;y=(n//6)*76
        for f in range(2):sheet.paste(portrait(art,f).convert('RGB'),(x+f*50+2,y+2))
        label.text((x+2,y+51),f'{sid}: '+art[:13],fill=(32,32,32));sheet.paste(icon(art).convert('RGBA'),(x+92,y+56),icon(art).convert('RGBA'))
    (out/'species-wave2-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    sheet.resize((1320,608),Image.Resampling.NEAREST).save(out/'species-wave2-contact-sheet_2x.png')
    pages=[]
    for f in range(2):
        page=Image.new('RGB',(6*56,4*56),(208,200,168))
        for n,(_,art,_,_) in enumerate(SELECTION):page.paste(portrait(art,f).convert('RGB'),((n%6)*56+4,(n//6)*56+4))
        pages.append(page.resize((1008,672),Image.Resampling.NEAREST))
    pages[0].save(out/'species-wave2-motion.gif',save_all=True,append_images=pages[1:],duration=600,loop=0)
    validation=[]
    for art,m in result.items():
        a=Image.open(out/m['frames'][0]);b=Image.open(out/m['frames'][1]);small=Image.open(out/m['icon'])
        assert a.mode==b.mode==small.mode=='P' and a.size==b.size==(48,48) and small.size==(16,16)
        assert set(a.get_flattened_data())<=set(range(4)) and set(b.get_flattened_data())<=set(range(4)) and set(small.get_flattened_data())<=set(range(4))
        changed=sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()));assert changed>0,(art,'frame pair not animated')
        tiles={tuple(a.crop((x,y,x+8,y+8)).get_flattened_data()) for y in range(0,48,8) for x in range(0,48,8)}
        validation.append({'art_id':art,'species_id':m['species_id'],'changed_pixels':changed,'unique_tiles_frame0':len(tiles),'sha256':hashlib.sha256((out/m['frames'][0]).read_bytes()).hexdigest()})
    (out/'species-wave2-validation.json').write_text(json.dumps({'source_only':True,'native_observed':False,'count':len(result),'records':validation},indent=2)+'\n')
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('output_dir');args=parser.parse_args();emit_species_wave2(args.output_dir)
