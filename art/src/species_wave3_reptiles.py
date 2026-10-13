"""Original source art for the sixty remaining reviewed reptile identities.

Natural poses, 4-color native grids, separately drawn icons and photo portraits.
Never copies photographs, upscales an icon or treats authored art as biology/native
approval. Profiles below expose each silhouette and pattern for hand correction.
Marine turtles require shore-based observation, never a rock-flip ground encounter.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
from species_wave2 import Pen
ROOT=Path(__file__).resolve().parents[2]
# sid: (body plan, pattern, pose/profile, length, thickness)
# Different patterns include scale plates, longitudinal stripes, bordered diamonds,
# speckles, ocelli, bars, leaf/shovel/snouted heads, horn/fringe geometry and scutes.
PROFILES={
33:('snake','legless',0,28,5),34:('snake','blotches',1,32,7),37:('lizard','whiptail',0,21,7),58:('lizard','zebra',1,19,8),
60:('snake','mountain_king',2,36,5),61:('marine','green',0,26,18),62:('snake','racer',3,36,5),63:('snake','sharp',4,32,4),
66:('viper','western',0,30,8),67:('viper','speckled',1,28,8),68:('viper','red_diamond',2,29,9),69:('viper','mojave',3,31,8),70:('viper','panamint',4,29,8),
71:('lizard','collared',2,20,10),73:('marine','leatherback',1,32,17),74:('snake','ringneck',5,27,5),77:('lizard','alligator',3,27,6),
80:('lizard','cope_leopard',4,21,9),82:('lizard','long_leopard',5,23,8),83:('lizard','gila',0,28,13),
89:('snake','night_desert',0,25,6),90:('snake','night_coast',1,27,5),91:('snake','coach_baja',2,37,5),92:('snake','stripe_racer',3,33,5),93:('snake','coach_desert',4,36,5),
95:('lizard','rock',1,25,10),96:('horned','coast',0,22,19),98:('horned','flat_tail',1,25,17),100:('snake','leafnose',5,25,6),101:('snake','gopher',0,36,8),102:('lizard','gilbert',2,25,6),
114:('snake','thread',1,38,3),115:('snake','longnose',2,32,6),117:('snake','patchnose',3,34,5),119:('lizard','sagebrush',3,19,8),120:('lizard','desert_spiny',4,24,11),121:('lizard','granite_spiny',5,22,10),
122:('snake','shovelnose',4,27,5),123:('snake','ground',5,26,4),126:('snake','blackhead_smith',0,25,4),127:('snake','blackhead_west',1,28,4),
131:('snake','garter_aquatic',2,30,6),132:('snake','garter_sierra',3,31,6),133:('snake','garter_terrestrial',4,32,6),134:('snake','garter_giant',5,38,8),135:('snake','garter_two',0,30,7),136:('snake','garter_checkered',1,31,8),137:('snake','garter_nw',2,27,5),138:('snake','garter_common',3,34,6),139:('snake','lyre',4,29,6),
140:('fringe','coachella',0,21,10),141:('fringe','colorado',1,23,10),142:('fringe','mojave',2,24,11),
143:('small_lizard','brush_long',0,18,5),144:('small_lizard','brush_baja',1,17,6),145:('small_lizard','tree',2,19,7),146:('small_lizard','sideblotch',3,18,7),
147:('night_lizard','sandstone',0,20,9),148:('night_lizard','granite',1,21,9),149:('night_lizard','desert',2,18,8),
}
PALETTES={
'snake':[(232,216,168),(40,32,24),(144,120,72),(224,192,120)],
'viper':[(232,216,168),(48,40,32),(152,136,96),(224,208,152)],
'lizard':[(224,216,168),(40,40,24),(136,128,72),(216,184,104)],
'horned':[(232,216,168),(56,40,24),(144,112,64),(224,192,120)],
'fringe':[(240,224,176),(56,48,32),(184,160,112),(232,208,152)],
'small_lizard':[(208,216,168),(40,40,24),(128,136,80),(200,184,112)],
'night_lizard':[(224,208,160),(40,32,24),(144,120,72),(208,184,128)],
'marine':[(152,200,216),(24,40,40),(72,112,96),(192,208,160)],
}
COILS=[
[(3,41),(7,32),(17,28),(29,34),(39,29),(39,21),(31,17),(20,19),(15,13),(20,7),(31,8)],
[(2,38),(11,31),(21,32),(32,37),(40,31),(37,23),(26,22),(17,17),(18,9),(31,7)],
[(4,40),(12,34),(21,30),(31,34),(39,28),(34,19),(23,20),(17,13),(24,7),(34,9)],
[(3,42),(10,35),(18,33),(29,35),(40,29),(38,21),(26,18),(18,20),(13,14),(18,8),(30,7)],
[(1,43),(8,35),(19,30),(31,34),(39,30),(40,23),(33,18),(22,20),(17,14),(22,9),(34,7)],
[(2,41),(10,33),(22,36),(34,32),(40,25),(34,18),(25,20),(17,15),(19,8),(31,8)],
]
SOURCES={
'garter_two':['https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=190376'],
'garter_checkered':['https://ksoutdoors.gov/var/news/storage/original/application/c28dec4f1df3ae9d5ef53121d76acfc1.pdf'],
'marine':['https://www.fisheries.noaa.gov/sea-turtles'],
'green':['https://www.fisheries.noaa.gov/species/green-turtle','https://www.fisheries.noaa.gov/sea-turtles'],
'leatherback':['https://www.fisheries.noaa.gov/species/leatherback-turtle','https://www.fisheries.noaa.gov/sea-turtles'],
'gila':['https://www.nps.gov/sagu/learn/nature/gila-monster.htm'],
'mountain_king':['https://www.nps.gov/yose/blogs/sierra-mountain-kingsnake.htm','https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=2769'],
'desert_spiny':['https://escholarship.org/content/qt79s5p5f8/supp/IB_104_Lab_Manual_2021.pdf'],
'zebra':['https://www.nps.gov/orpi/learn/nature/lizards.htm'],
'fringe':['https://eplanning.blm.gov/public_projects/nepa/77304/103087/126160/App-E-Mojave_Fringe-toed_Lizard_Study_Proposal.pdf'],
}

def art_id(sid):return 'r_'+str(sid).zfill(3)
def palette(sid):
    kind,pattern,pose,length,width=PROFILES[sid];colors=list(PALETTES[kind])
    if pattern=='mountain_king':colors=[(232,216,168),(24,24,24),(216,72,48),(232,224,200)]
    if pattern=='gila':colors=[colors[0],(24,24,24),(72,56,48),(232,136,72)]
    if pattern in ('racer','blackhead_smith','blackhead_west','ringneck','garter_common'):colors=[colors[0],(16,24,24),(64,72,48),(216,184,104)]
    if pattern=='red_diamond':colors=[colors[0],(56,32,24),(168,96,64),(224,184,128)]
    if pattern=='leatherback':colors=[colors[0],(16,24,32),(48,56,64),(200,208,208)]
    if pattern in ('longnose','shovelnose','ground'):colors=[colors[0],(40,24,24),(184,96,48),(224,208,144)]
    if pattern in ('collared','granite_spiny','tree'):colors=[colors[0],(32,40,40),(96,128,120),(216,184,104)]
    return colors

def canvas(sid,size=(48,48),transparent=False):
    im=Image.new('P',size,0);im.putpalette([v for rgb in palette(sid) for v in rgb]+[0]*756)
    if transparent:im.info['transparency']=0
    return im

def mountain_king_image(frame=0,small=False):
    """Original gentle S-curve, transverse rings and calm head/tail displacement.

    The independent icon has its own shorter path. Ring colors follow arc length,
    avoiding stripes painted across unrelated coils. No rattle/defensive display.
    """
    import math
    im=canvas(60,(16,16) if small else (48,48),transparent=small)
    if small:
        controls=[(1,14),(4,11),(10,13),(14,10),(11,7),(4,7),(3,4),(8,2),(12,3)]
        radius=1.55;period=5;head=(12,3)
    else:
        controls=[(4+frame*2,41),(8,34),(20,37),(35,35),(40,28),(36,20),(22,21),(10,17),(14,8),(28,6),(36-frame,10+frame*2)]
        radius=2.7;period=14;head=controls[-1]
    # Catmull-Rom interpolated editable control points make smooth slender curves.
    samples=[];dist=0.;last=None;pad=[controls[0]]+controls+[controls[-1]]
    for i in range(1,len(pad)-2):
        a,b,c,d=pad[i-1:i+3]
        for step in range(20):
            t=step/20.;t2=t*t;t3=t2*t
            point=tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t2+(-a[k]+3*b[k]-3*c[k]+d[k])*t3) for k in (0,1))
            if last:dist+=math.hypot(point[0]-last[0],point[1]-last[1])
            samples.append((point[0],point[1],dist));last=point
    samples.append((*controls[-1],dist))
    for y in range(im.height):
        for x in range(im.width):
            px,py,arc=min(samples,key=lambda q:(q[0]-x)**2+(q[1]-y)**2)
            distance=math.hypot(px-x,py-y)
            if distance>radius:continue
            phase=arc%period
            color=(2 if phase<2 else 1 if phase<3 else 3 if phase<4 else 1) if small else (2 if phase<6 else 1 if phase<8 else 3 if phase<12 else 1)
            if distance>radius-.65:color=1
            # Naturally taper the last tail-tip pixels, not a blunt boa tail.
            if arc<3 and distance>radius*(.25+arc/4):continue
            im.putpixel((x,y),color)
    d=ImageDraw.Draw(im);x,y=head
    if small:
        d.ellipse((x-1,y-1,x+2,y+1),fill=1);d.point((x+1,y),fill=3)
    else:
        d.ellipse((x-3,y-3,x+4,y+2),fill=1)
        d.ellipse((x+1,y-2,x+3,y),fill=3);d.point((x+2,y-1),fill=1)
        d.point((x+4,y+1),fill=3)
    return im

def checkered_markings(im,points,width):
    """KDWP136 general morphology only: narrow stripes, bold checks between.

    Width8 intentionally makes brown channels+darkchecks readable at32px;
    no relative adult-size claim and no Kansas habitat/range transfer.
    """
    import math
    segments=[];total=0.
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length:segments.append((a,b,dx,dy,length,total));total+=length
    for y in range(im.height):
        for x in range(im.width):
            best=None
            for a,b,dx,dy,length,arc in segments:
                t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(length*length)))
                xx,yy=a[0]+t*dx,a[1]+t*dy;dist=math.hypot(x-xx,y-yy)
                if best is None or dist<best[0]:best=(dist,((x-xx)*(-dy)+(y-yy)*dx)/length,arc+t*length)
            if best is None:continue
            dist,normal,arc=best
            # Preserve authored head/round pupil and natural tapered tailtip.
            if arc<1 or arc>total-(5 if im.width==48 else 2):continue
            if dist>width/2-.45 or im.getpixel((x,y))==0:continue
            if dist>width/2-1:color=1
            elif abs(normal)<.6 or abs(abs(normal)-2.9)<.5:color=3
            elif 1.0<=abs(normal)<=2.3 and (int(arc//3)+(normal<0))%2==0:color=1
            else:color=2
            im.putpixel((x,y),color)

def two_striped_markings(im,points,width):
    """CDFW135: pale lateral stripes, no longitudinal middorsal stripe.

    Original indexed pixels follow the local curve normal. Preserve the calm
    curve, eye/head and tailtip; bodywidth7 intentionally leaves a visible
    browncenter between pale sidebands atnative32, replacing previouswidth5.
    """
    import math
    segments=[];total=0.0
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length:segments.append((a,b,dx,dy,length,total));total+=length
    band=2.5 if width>=5 else 0.8
    for y in range(im.height):
        for x in range(im.width):
            if im.getpixel((x,y))==0:continue
            best=None
            for a,b,dx,dy,length,offset in segments:
                t=max(0.0,min(1.0,((x-a[0])*dx+(y-a[1])*dy)/(length*length)))
                px,py=a[0]+t*dx,a[1]+t*dy;distance=math.hypot(x-px,y-py)
                signed=((x-px)*(-dy)+(y-py)*dx)/length
                if best is None or distance<best[0]:best=(distance,signed,offset+t*length)
            distance,signed,along=best
            if along<2 or along>total-(5 if width>=5 else 2):continue
            if abs(signed)<0.45 and distance<0.7:
                im.putpixel((x,y),2 if width>=5 else 1)
            elif abs(abs(signed)-band)<=(0.55 if width>=5 else 0.45) and distance<=band+(0.55 if width>=5 else 0.4):
                im.putpixel((x,y),3)

def portrait(sid,frame=0):
    if sid==60:return mountain_king_image(frame)
    kind,pattern,pose,length,width=PROFILES[sid];im=canvas(sid);p=Pen(im)
    if kind in ('snake','viper'):
        points=list(COILS[pose]);last=points[-1];points[-1]=(last[0]+frame,last[1]-frame)
        # Shorter tails/compact versus slender extended coils are deliberate
        # profile choices, still pending proportions against the exact taxon.
        points[0]=(points[0][0]+(38-length)//3,points[0][1]-(38-length)//4)
        p.line(points,1,width);p.line(points,2,max(1,width-2))
        if kind=='viper':
            x,y=points[-1];p.poly([(x-3,y-4),(x+6,y-4),(x+10,y),(x+6,y+5),(x-3,y+4),(x-5,y)],2)
            p.eye(x+4,y-2,True)
            for n,(x,y) in enumerate(points[1:-1]):
                if pattern=='speckled':
                    for dx,dy in [(-2,-1),(0,1),(2,-2)]:p.point((x+dx,y+dy),3 if n%2 else 1)
                else:
                    p.poly([(x,y-3),(x+3,y),(x,y+3),(x-3,y)],3 if pattern!='western' else 1)
                    p.poly([(x,y-1),(x+1,y),(x,y+1),(x-1,y)],1 if pattern!='western' else 3)
            if pattern=='mojave':
                for y in range(33,42,3):p.line([(2,y),(7,y)],3,2);p.line([(2,y+2),(7,y+2)],1)
            elif pattern=='panamint':
                for x,y in points[2:7]:p.point((x+2,y-2),1)
            x,y=points[0]
            for n in range(3):p.oval((x-2,y+n*2,x+2,y+n*2+2),3)
        else:
            x,y=points[-1];headw=7 if pattern=='rubber' else 5
            if pattern=='thread':p.oval((x-1,y-1,x+3,y+1),2);p.point((x+2,y),1)
            elif pattern in ('leafnose','shovelnose'):p.poly([(x-3,y-2),(x+6,y-3),(x+8,y),(x+5,y+3),(x-3,y+2)],2);p.line([(x+5,y-2),(x+7,y)],3,2)
            else:p.oval((x-3,y-3,x+headw,y+3),2)
            if pattern!='thread':p.eye(x+2,y-1,pattern.startswith('night_') or pattern=='lyre')
            if frame and pattern!='thread':p.line([(x+headw,y+1),(min(47,x+headw+4),y+1),(min(47,x+headw+5),y)],1)
            if pattern in ('legless','stripe_racer','patchnose') or pattern.startswith('garter'):
                if pattern=='garter_two':two_striped_markings(im,points,width)
                elif pattern=='garter_checkered':checkered_markings(im,points,width)
                else:p.line(points,3,1 if width<7 else 2)
                if pattern not in ('garter_two','garter_checkered','legless'):p.line([(x+1,y+2) for x,y in points[2:-1]],1)
                if pattern in ('garter_aquatic','garter_terrestrial'):
                    for n,(x,y) in enumerate(points[1:-1]):p.point((x-2,y+(n%2)),1)
                if pattern=='garter_checkered':
                    hx,hy=points[-1];p.line([(hx-1,hy-2),(hx-2,hy-1),(hx-1,hy+1)],3)
                if pattern=='patchnose':p.line([(points[-1][0]+3,points[-1][1]-2),(points[-1][0]+5,points[-1][1]+1)],3,2)
            elif pattern in ('longnose','shovelnose','ground'):
                for n,(x,y) in enumerate(points[1:-1]):p.line([(x-2,y-2),(x+2,y+2)],1 if n%2==0 else 3,3)
                if pattern=='longnose':p.line([(points[-1][0],points[-1][1]-2),(points[-1][0]+4,points[-1][1]-2)],3)
            elif pattern in ('blotches','gopher') or pattern.startswith('night_') or pattern=='lyre':
                for n,(x,y) in enumerate(points[1:-1]):p.oval((x-2,y-2,x+2,y+1),1)
                if pattern.startswith('night_'):
                    x,y=points[-1];p.line([(x-2,y+3),(x+3,y+3)],1,2)
                    if pattern=='night_coast':p.line([(x-2,y+4),(x+2,y+4)],3)
                if pattern=='lyre':
                    x,y=points[-1];p.line([(x-2,y-1),(x,y-3),(x+2,y-1),(x+4,y-3),(x+5,y)],1)
            elif pattern=='ringneck':
                x,y=points[-2];p.line([(x-3,y),(x+2,y+3)],3,3)
                p.line([(x,y+2) for x,y in points[:3]],3)
            elif pattern.startswith('blackhead'):
                x,y=points[-1];p.oval((x-3,y-3,x+5,y+3),1);p.point((x+3,y-1),3)
                p.line([(points[-2][0]-2,points[-2][1]),(points[-2][0]+2,points[-2][1]+2)],3)
            elif pattern=='sharp':
                for x,y in points[1:5]:p.line([(x,y),(x+2,y+1)],3)
                p.line([points[0],(max(0,points[0][0]-2),min(47,points[0][1]+4))],1)
            elif pattern.startswith('coach'):
                for n,(x,y) in enumerate(points[1:-1]):
                    p.line([(x-2,y),(x,y-1),(x+2,y+1)],1 if n%2 else 3)
                if pattern=='coach_baja':p.line([(x,y+1) for x,y in points[-4:-1]],1,2)
            elif pattern=='rubber':p.line([(x,y+2) for x,y in points[1:5]],3);p.oval((points[0][0]-2,points[0][1]-1,points[0][0]+2,points[0][1]+2),2)
            elif pattern=='thread':
                # Tiny threadsnake has a small non-expanded head, not a viper.
                x,y=points[-1];p.oval((x-1,y-1,x+3,y+1),2);p.point((x+2,y),1)
    elif kind=='marine':
        # Top-down swimming view. Flipper stroke changes limbs while the shell
        # remains anchored; there are no terrestrial feet or rock-flip poses.
        long=pattern=='leatherback';p.oval((17,3,30,12),2);p.eye(18,6);p.eye(25,6)
        if long:p.poly([(16,11),(32,11),(37,22),(33,34),(24,42),(15,34),(11,22)],2)
        else:p.poly([(17,10),(31,10),(36,18),(34,31),(24,38),(14,31),(12,19)],2)
        for side in (-1,1):
            bx=15 if side<0 else 33;tip=2 if side<0 else 46
            p.poly([(bx,14),(tip,20+frame*5),(tip+side,27+frame*2),(bx+side*2,22)],2)
            p.poly([(17 if side<0 else 31,31),(11 if side<0 else 37,39-frame),(16 if side<0 else 33,41),(20 if side<0 else 28,35)],2)
        if long:
            for x in (14,17,20,24,28,31,34):p.line([(x,14),(x-1 if x<24 else x+1,25),(24+(x-24)//2,37)],3)
            for x,y in [(19,6),(27,7),(17,18),(30,23),(19,30),(26,34),(5,23),(40,25)]:p.point((x,y),3)
        else:
            for x,y in [(17,16),(25,15),(15,24),(24,23),(28,29),(20,30)]:p.poly([(x,y),(x+3,y-2),(x+6,y),(x+4,y+5),(x,y+4)],3)
            p.line([(23,11),(23,34)],1)
    elif kind in ('horned','fringe','night_lizard'):
        # Dorsal forms use explicit head horns, foot fringes or granular scales.
        left=24-width//2;right=24+width//2
        tail=[(24,32),(23+frame,38),(29+frame,43),(35,45)]
        if kind=='horned' and pattern=='flat_tail':tail=[(24,31),(25+frame,37),(33+frame,40),(38,41)]
        p.line(tail,1,5 if kind=='horned' else 4);p.line(tail,2,3 if kind=='horned' else 2)
        for y in (19,29):
            for side in (-1,1):
                bx=left if side<0 else right;ex=bx+side*7
                p.line([(bx,y),(ex,y-3),(ex+side,y+3)],1,3);p.line([(bx,y),(ex,y-3)],2)
                for t in (-2,-1,0,1,2):
                    p.line([(ex+side,y+3),(ex+side+t,y+5-frame)],1)
                    if kind=='fringe' and y==29:p.line([(ex+side+t,y+5-frame),(ex+side+t-1,y+6-frame)],3)
        p.oval((left,14,right,34));p.oval((17,5,31,17),2);p.eye(18,9,kind=='night_lizard',frame==1 and kind!='night_lizard');p.eye(27,9,kind=='night_lizard',frame==1 and kind!='night_lizard')
        if kind=='horned':
            for x,y in [(17,7),(20,5),(27,5),(31,7)]:p.poly([(x,y+2),(x-2,y-4 if pattern=='coast' else y-2),(x+1,y)],1)
            for y in (19,25,30):p.poly([(left,y),(left-3,y),(left,y+3)],1);p.poly([(right,y),(right+3,y),(right,y+3)],1)
            for x,y in [(18,19),(26,20),(22,25),(29,28),(17,29)]:p.poly([(x,y),(x+2,y-2),(x+4,y+1)],3)
            if pattern=='flat_tail':p.line([(24,16),(24,31)],1)
        elif kind=='fringe':
            for y in range(17,33,4):
                for x in range(left+2,right-1,4):p.oval((x,y,x+2,y+2),1);p.point((x+1,y+1),3)
            if pattern=='coachella':p.line([(23,17),(23,31)],3)
            elif pattern=='colorado':p.line([(left+1,17),(left+1,31)],1)
            else:p.line([(right-1,17),(right-1,31)],1)
        else:
            for y in range(18,32,3):
                for x in range(left+2,right-1,3):p.point((x+(y//3)%2,y),1 if pattern=='granite' else 3)
            if pattern=='sandstone':p.line([(left+1,17),(left+1,30)],3)
            elif pattern=='desert':p.line([(23,17),(23,31)],3)
    else:
        # Side poses: long thin skink/whiptail bodies, muscular collared/leopard,
        # stout bead-scaled Gila, crested spiny forms and miniature brush lizards.
        by=25;head_h=9 if kind=='small_lizard' else 8
        l=12 if length>24 else 16;r=33 if kind!='small_lizard' else 30
        h=width//2;raise_body=frame if pattern in ('collared','desert_spiny','granite_spiny','rock') else 0
        by-=raise_body
        tail=[(l+1,by+1),(9,by+5),(6,35),(2,43)]
        if pattern=='gila':tail=[(l,by+1),(7,by+5),(5,35),(7,40)]
        if pattern=='zebra':tail=[(l,by+1),(8,by+4),(6,21),(10+frame,15)]
        p.line(tail,1,8 if pattern=='gila' else 4);p.line(tail,2,6 if pattern=='gila' else 2)
        p.oval((l,by-h,r,by+h));snout=46 if pattern=='long_leopard' else 43
        p.poly([(r-2,by-h),(37,by-h-4),(snout,by-h-2),(snout,by-h+3),(38,by-h+5),(r,by+1)],2)
        for x,side in ((l+4,-1),(r-2,1)):
            knee=(x+side*4+(frame if side>0 else 0),by+7-(frame if side>0 else 0));foot=(x+side*5,39)
            p.line([(x,by+1),knee,foot],1,4 if pattern=='gila' else 2);p.line([(x,by+1),knee],2)
            for t in (-2,-1,0,1,2):p.line([foot,(foot[0]+t,41)],1)
        p.eye(38,by-h-1)
        if pattern=='gila':
            # NPS describes contrasting irregular pink/orange bands/blotches
            # with bead-like scales. Tiny outlined2x2ellipses previously lost
            # alltheir orangefill, incorrectly making this torso all-dark.
            # Clip hand-placed orangepatches to theexisting body silhouette.
            mask=Image.new('L',(48,48),0);md=ImageDraw.Draw(mask)
            patches=[[(14,by-3),(17,by-5),(20,by-3),(18,by-1),(15,by-1)],
                     [(22,by-5),(25,by-4),(26,by-1),(23,by),(21,by-2)],
                     [(28,by-3),(31,by-2),(32,by),(30,by+2),(27,by+1)],
                     [(15,by+2),(18,by),(21,by+2),(20,by+4),(16,by+4)],
                     [(23,by+2),(25,by+1),(28,by+3),(26,by+5),(23,by+4)]]
            for points in patches:md.polygon(points,fill=255)
            for yy in range(by-h+1,by+h):
                for xx in range(l+1,r):
                    if mask.getpixel((xx,yy)) and im.getpixel((xx,yy))!=0:p.point((xx,yy),3)
            # Granular dark separations oncolorpatches andisolated highlighted
            # beads elsewhere, not copied from anyindividual photograph.
            for xx,yy in [(16,by-2),(23,by-3),(29,by),(18,by+2),(25,by+3)]:p.point((xx,yy),1)
            for xx,yy in [(14,by),(20,by-4),(27,by-4),(22,by+4),(31,by+2)]:
                if im.getpixel((xx,yy))==2:p.point((xx,yy),3)
            for yy in (32,36):p.line([(3,yy),(7,yy)],3,2)
            p.line([(35,by-h),(35,by+1)],1,2)
        elif pattern in ('collared','rock'):
            p.line([(32,by-h),(31,by+h)],1,3);p.line([(35,by-h+1),(34,by+1)],1,2)
            for x,y in [(19,by-2),(24,by-3),(28,by),(20,by+2)]:p.point((x,y),3)
            if pattern=='rock':p.line([(14,by-3),(23,by-3)],3)
        elif 'leopard' in pattern:
            for x,y in [(18,by-2),(23,by-3),(28,by),(20,by+2),(28,by+3),(11,by+6),(5,36)]:p.oval((x,y,x+2,y+2),1)
            if pattern=='cope_leopard':p.line([(17,by-4),(31,by-4)],3)
        elif pattern in ('alligator','gilbert') or pattern=='whiptail':
            if pattern=='alligator':
                for x in range(l+2,r,3):p.line([(x,by-h+1),(x+1,by+h-1)],1)
            elif pattern=='whiptail':
                for y in (by-2,by,by+2):p.line([(l+2,y),(31,y-1)],3)
                for x in (19,23,27):p.point((x,by+3),1)
            else:p.line([(l+1,by-1),(31,by-2)],3);p.line([(l+2,by+2),(31,by+1)],1)
        elif pattern=='zebra':
            for y in (17,20,23,26):p.line([(4,y),(8,y)],3 if y%2 else 1,2)
            p.line([(27,by-h+1),(27,by+2)],1,2)
        elif 'spiny' in pattern or pattern=='sagebrush':
            for x in range(l+2,r,3):p.poly([(x,by-h+2),(x+2,by-h),(x+3,by-h+3)],1)
            for x in range(l+2,r-1,4):p.line([(x,by-1),(x+3,by+1),(x,by+3)],3)
            if pattern=='desert_spiny':
                # Diagnostic dark shoulder wedge behind the forelimb/head,
                # following the Berkeley manual; grounded through both poses.
                p.poly([(29,by-h+1),(33,by-h+2),(30,by+3)],1)
            if pattern=='granite_spiny':
                for x,y in [(19,by-3),(23,by+2),(28,by-2),(32,by)]:p.oval((x,y,x+1,y+1),1)
                p.line([(27,by+3),(31,by+3)],3)
        else:
            p.line([(l+2,by-h+2),(r-2,by-h+1)],3)
            for x,y in [(l+3,by),(l+7,by+2),(r-3,by-1)]:p.point((x,y),1)
            if pattern=='sideblotch':p.oval((27,by-1,30,by+2),1)
            elif pattern=='brush_long':p.line([(8,31),(5,37),(1,45)],2)
            elif pattern=='tree':p.line([(29,by+2),(29,by+4)],3,2)
    return im


def icon(sid):
    if sid==60:return mountain_king_image(small=True)
    # Independent native icon geometry (not a thumbnail of the 48px painting).
    kind,pattern,pose,length,width=PROFILES[sid];im=canvas(sid,(16,16),True);p=Pen(im)
    if kind in ('snake','viper'):
        paths=[[(1,14),(3,10),(8,11),(13,11),(13,7),(6,6),(7,3),(12,3)],[(1,13),(5,9),(11,12),(14,9),(9,7),(5,4),(12,2)],[(2,14),(5,11),(10,12),(14,8),(10,6),(6,6),(7,2),(12,3)],[(1,14),(5,11),(10,13),(14,10),(13,6),(7,7),(5,4),(11,2)],[(1,15),(4,10),(9,10),(13,12),(14,8),(10,5),(6,5),(8,2),(12,3)],[(2,15),(6,11),(12,12),(14,7),(10,6),(6,7),(5,3),(11,3)]]
        pts=paths[pose];w=4 if kind=='viper' or width>7 else 2 if width<5 else 3
        p.line(pts,1,w);p.line(pts,2,max(1,w-1));x,y=pts[-1]
        if kind=='viper':p.poly([(x-2,y-2),(x+2,y-2),(x+3,y),(x+1,y+2),(x-2,y+1)],2);p.line([(1,12),(1,15)],3,2)
        else:p.oval((x-1,y-1,min(15,x+3),y+1),2)
        p.point((min(15,x+1),y),3)
        if pattern=='garter_two':two_striped_markings(im,pts,w)
        elif pattern=='garter_checkered':checkered_markings(im,pts,w)
        elif pattern.startswith('garter') or pattern in ('legless','stripe_racer','patchnose'):p.line(pts,3)
        elif kind=='viper' or pattern in ('blotches','gopher','longnose','shovelnose','ground','lyre'):
            for x,y in pts[1:-1:2]:p.line([(x-1,y),(x+1,y)],3)
        elif pattern=='ringneck':p.line([(pts[-2][0],pts[-2][1]-1),(pts[-2][0]+1,pts[-2][1]+1)],3,2)
        elif pattern.startswith('blackhead'):x,y=pts[-1];p.oval((x-1,y-1,min(15,x+3),y+1),1);p.point((x+1,y),3)
        elif pattern.startswith('coach'):p.point(pts[2],3);p.point(pts[4],1)
        elif pattern=='sharp':p.line([(pts[0][0],pts[0][1]),(max(0,pts[0][0]-1),min(15,pts[0][1]+1))],1);p.point(pts[2],3)
        if pattern=='garter_checkered':
            for x,y in pts[1:5:2]:p.point((x-1,y),1)
        elif pattern=='garter_nw':p.point((pts[4][0]+1,pts[4][1]),1)
        elif pattern=='patchnose':x,y=pts[-1];p.line([(x+2,y-1),(min(15,x+3),y+1)],3)
        elif pattern.startswith('night_'):x,y=pts[-2];p.line([(x-1,y),(x+1,y+1)],1)
    elif kind=='marine':
        p.oval((6,1,10,4),2);p.poly([(5,3),(11,3),(13,8),(10,13),(7,14),(3,9)],2)
        p.poly([(5,5),(0,7),(1,10),(5,8)],2);p.poly([(11,5),(15,7),(15,10),(11,8)],2)
        if pattern=='leatherback':
            for x in (5,8,11):p.line([(x,5),(x,10)],3)
        else:
            for x,y in [(5,5),(8,4),(6,8),(9,8)]:p.point((x,y),3)
    elif kind in ('horned','fringe','night_lizard'):
        fat=kind=='horned';l,r=(3,13) if fat else (5,11)
        p.oval((5,1,11,5));p.oval((l,4,r,11));p.point((6,3),3);p.point((10,3),3)
        for y in (6,10):p.line([(l,y),(l-2,y+2)],1);p.line([(r,y),(r+2,y+2)],1)
        p.line([(8,10),(8,13),(12,15)],1,3);p.line([(8,10),(8,13),(12,15)],2)
        if fat:
            for x in (5,8,11):p.point((x,0),1)
        for x,y in [(6,6),(9,7),(7,9)]:p.point((x+(pose%2),y),3 if kind!='fringe' else 1)
        if kind=='fringe':p.line([(2,12),(4,13)],3);p.line([(12,13),(14,12)],3)
    else:
        p.line([(6,8),(3,11),(1,15)],1,4 if pattern=='gila' else 3);p.line([(6,8),(3,11),(1,15)],2)
        p.oval((3 if length>24 else 5,5,12,10));p.poly([(10,5),(12,2),(15,3),(15,6),(12,7)],2);p.point((13,3),3)
        p.line([(6,9),(4,13)],1,2);p.line([(10,9),(13,13)],1,2)
        if pattern=='gila':
            for xy in [(5,6),(8,8),(10,6),(3,12)]:p.point(xy,3)
        elif 'leopard' in pattern or 'spiny' in pattern:
            for xy in [(6,6),(8,8),(10,6)]:p.point(xy,1)
        elif pattern=='collared':p.line([(11,5),(10,8)],1,2)
        elif pattern=='sideblotch':p.point((10,8),1)
        elif pattern=='zebra':p.line([(3,11),(5,9),(4,6)],3)
        elif pattern=='alligator':
            for x in (5,8,10):p.line([(x,6),(x,9)],1)
        elif pattern=='gilbert':p.line([(4,7),(11,6)],3);p.line([(5,9),(11,8)],1)
        elif pattern=='whiptail':p.line([(5,6),(11,5)],3);p.line([(5,8),(11,7)],3);p.point((8,9),1)
        elif pattern=='sagebrush':p.line([(6,6),(8,8),(10,6)],1);p.line([(9,9),(12,11)],1)
        elif pattern=='rock':p.line([(11,5),(10,8)],1,2);p.point((6,7),3)
        elif pattern=='brush_baja':p.line([(4,12),(2,14)],1);p.line([(5,7),(11,6)],3)
        elif pattern=='brush_long':p.line([(2,12),(0,15)],2);p.line([(5,7),(11,6)],3)
        elif pattern=='tree':p.line([(10,9),(12,11),(12,13)],1);p.point((7,8),3)
        else:p.line([(5,7),(11,6)],3)
        if pattern=='granite_spiny':p.point((8,6),3);p.point((10,9),3)
        elif pattern=='desert_spiny':p.point((5,4),1);p.point((8,4),1)
        elif pattern=='long_leopard':p.line([(10,4),(14,4)],2)
    return im


def emit_species_wave3_reptiles(output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    registry={r['species_id']:r for r in json.loads((ROOT/'data/production_roster.json').read_text())['records']}
    result={};sheet=Image.new('RGB',(6*110,10*74),(208,200,168));labels=ImageDraw.Draw(sheet)
    validation=[];unique_portraits=set()
    for n,sid in enumerate(PROFILES):
        r=registry[sid];assert r['group']=='Reptilia';
        if sid==60:assert r['canonical_scientific_name']=='Lampropeltis zonata','Master ID60 identity must be corrected before canonical generation'
        aid=art_id(sid);kind,pattern,pose,length,width=PROFILES[sid]
        frames=[]
        for f in range(2):name=f'portrait_{aid}_idle{f}.png';portrait(sid,f).save(out/name);frames.append(name)
        still=f'portrait_{aid}.png';portrait(sid).save(out/still);small=f'portrait32_{aid}.png';portrait(sid).resize((32,32),Image.Resampling.NEAREST).save(out/small)
        ic=f'critter_{aid}.png';icon(sid).save(out/ic)
        anim=canvas(sid,(96,48));anim.paste(portrait(sid,0),(0,0));anim.paste(portrait(sid,1),(48,0));an=f'portrait_{aid}_animation.png';anim.save(out/an)
        pal=palette(sid)
        result[aid]={'art_id':aid,'species_id':sid,'canonical_scientific_name':r['canonical_scientific_name'],'scientific_name_provisional':r['canonical_scientific_name'],'common_name':r['common_name'],'icon':ic,'portrait':still,'portrait32':small,'frames':frames,'animation_sheet':an,'dimensions':[48,48],'icon_dimensions':[16,16],'palette':pal,'palette_rgb555':[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in pal],'frame_duration_ticks':36,'behavior_animation':'swim_stroke' if kind=='marine' else 'quiet_head_sway' if kind in ('snake','viper') else 'quiet_tail_step_no_blink' if kind=='night_lizard' else 'grounded_step_or_blink','status':'art_only_pending_independent_anatomy_and_native_review','taxon_count_approval':False,'anatomy_plan':kind+'_'+pattern,'allowed_districts_from_roster':[p['region_id'] for p in r['region_permissions']],'mechanic_requirement':'shore_observation_no_ground_rock_encounters' if kind=='marine' else 'reviewed_natural_observation','anatomy_reference_urls':SOURCES.get(pattern,SOURCES.get(kind,[])),'review_notes':(['Night lizards lack movable eyelids; vertical pupil and quiet tail movement, never blink.'] if kind=='night_lizard' else [])+['Anatomy and proportions require independent species-by-species review.','Patterns are hand-authored source proposals; similar genera may require additional silhouette or marking refinements.','No defensive provocation, handling or threatening rattle behavior is a photo bonus.']}
        a=portrait(sid,0);b=portrait(sid,1);ic_im=icon(sid)
        for im,size in [(a,(48,48)),(b,(48,48)),(ic_im,(16,16))]:assert im.mode=='P' and im.size==size and set(im.get_flattened_data())<={0,1,2,3}
        changed=sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()));assert changed>0,(sid,'static frame pair')
        tiles={tuple(a.crop((x,y,x+8,y+8)).get_flattened_data()) for y in range(0,48,8) for x in range(0,48,8)}
        unique_portraits.add(bytes(a.get_flattened_data()))
        validation.append({'species_id':sid,'art_id':aid,'changed_pixels':changed,'unique_tiles_frame0':len(tiles),'sha256':hashlib.sha256((out/still).read_bytes()).hexdigest()})
        x=(n%6)*110;y=(n//6)*74
        for f in range(2):sheet.paste(portrait(sid,f).convert('RGB'),(x+f*50+2,y+2))
        labels.text((x+2,y+51),str(sid)+' '+r['common_name'][:12],fill=(32,32,32));sheet.paste(ic_im.convert('RGBA'),(x+92,y+52),ic_im.convert('RGBA'))
    assert len(unique_portraits)==len(PROFILES),'duplicate portrait index grids'
    (out/'species-wave3-reptiles-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    sheet.resize((1320,1480),Image.Resampling.NEAREST).save(out/'species-wave3-reptiles-contact-sheet_2x.png')
    (out/'species-wave3-reptiles-validation.json').write_text(json.dumps({'source_only':True,'native_observed':False,'count':len(result),'unique_native_portrait_grids':len(unique_portraits),'records':validation},indent=2)+'\n')
    pages=[]
    for f in range(2):
        im=Image.new('RGB',(6*56,10*56),(208,200,168))
        for n,sid in enumerate(PROFILES):im.paste(portrait(sid,f).convert('RGB'),((n%6)*56+4,(n//6)*56+4))
        pages.append(im.resize((672,1120),Image.Resampling.NEAREST))
    pages[0].save(out/'species-wave3-reptiles-motion.gif',save_all=True,append_images=pages[1:],duration=600,loop=0)
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('output_dir');a=p.parse_args();emit_species_wave3_reptiles(a.output_dir)
