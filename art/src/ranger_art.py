"""Sixteen original district rangers: editable native sprites and independent portraits.
Source art only. Native placement/OAM/animation and human review remain gates.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
RANGERS={
'nell':{'name':'RANGER NELL','personality':'Patient field mentor; observes first and keeps an illustrated journal.','gear':'braid, brimmed hat, camera strap, field journal','palette':[(248,0,248),(32,40,32),(72,136,88),(240,200,144)],'districts':['D01','D04']},
'sol':{'name':'RANGER SOL','personality':'Desert trail guide; notices shade and reads small sand tracks.','gear':'broad sun hat, scarf, camera and desert walking boots','palette':[(248,0,248),(48,32,24),(184,112,56),(240,208,144)],'districts':['D02','D03','D07']},
'iris':{'name':'RANGER IRIS','personality':'Coast observer; keeps tide and habitat notes in a waterproof notebook.','gear':'rain hood, short curl clusters, field notebook and backpack','palette':[(248,0,248),(24,40,48),(64,144,160),(232,200,152)],'districts':['D09','D10','D12']},
'vale':{'name':'RANGER VALE','personality':'Northern forest guide; patient around creeks and an enthusiastic map maker.','gear':'wool cap, beard shadow, folded map and binocular strap','palette':[(248,0,248),(32,32,40),(120,120,184),(232,200,160)],'districts':['D13','D14','D15','D16']},
}
# 16x24 idle pixel grids; walking modifies anchored knees/boots deliberately.
FRONT=[
'................','.....111111.....','....12222221....','...1222222221...',
'..111111111111..','....13333331....','....13133131....','....13333331....',
'.....133331.....','....11222111....','...1222222221...','..132211122231..',
'..131213312131..','..131211112131..','...1122222211...','....12222221....',
'....12212221....','....11111111....','.....121121.....','.....121121.....',
'.....131131.....','.....111111.....','....111..111....','................']
SIDE=[
'................','.....111111.....','....12222221....','...1222222221...',
'...11111111111..','....13333331....','....11331331....','....11333331....',
'.....133331.....','.....122221.....','....12222221....','....12211111....',
'....13213331....','....13111111....','....11222211....','.....122221.....',
'.....122221.....','.....111111.....','......12121.....','......12121.....',
'......13131.....','......11111.....','.....111.111....','................']

def sprite(name,direction='down',frame=0):
    grid=[list(r) for r in (SIDE if direction in ('right','left') else FRONT)]
    if direction=='up':
        for y in range(5,9):
            for x in range(5,11):grid[y][x]='1' if y<7 else '2'
        for y in range(10,16):
            for x in range(5,11):grid[y][x]='2'
        for x in range(5,11):grid[11][x]='1';grid[15][x]='1'
    if name=='nell':
        # Dark braid beside the right cheek and journal resting at hip.
        for y in range(7,13):grid[y][11]='1';grid[y][12]='3' if y%2 else '2'
        grid[14][3]=grid[15][3]='3';grid[14][4]=grid[15][4]='1'
    elif name=='sol':
        for x in range(1,15):grid[4][x]='1'
        for x in range(5,11):grid[9][x]='3'
        grid[10][5]='3';grid[11][5]='3'
    elif name=='iris':
        for y in range(2,9):grid[y][3]='1';grid[y][12]='1'
        for x in range(5,11):grid[2][x]='2'
        grid[5][4]=grid[7][4]='1';grid[5][11]=grid[7][11]='1'
        for y in range(12,16):grid[y][3]='3';grid[y][4]='1'
    else:
        for x in range(5,11):grid[3][x]='3'
        for x in range(6,10):grid[8][x]='1'
        grid[12][6]=grid[12][9]='1';grid[13][6]=grid[13][9]='3'
    if frame:
        # Separate alternating grounded boots rather than whole-frame shifting.
        for y in (19,20,21,22):
            for x in range(4,12):grid[y][x]='.'
        if frame==1:
            for x,y,c in [(5,19,'2'),(5,20,'2'),(4,21,'1'),(5,21,'1'),(6,21,'1'),(9,19,'2'),(9,20,'2'),(9,21,'3'),(9,22,'1'),(10,22,'1')]:grid[y][x]=c
        else:
            for x,y,c in [(6,19,'2'),(6,20,'2'),(5,22,'1'),(6,22,'1'),(7,22,'1'),(10,19,'2'),(10,20,'2'),(9,21,'1'),(10,21,'1'),(11,21,'1')]:grid[y][x]=c
    if direction=='left':grid=[row[::-1] for row in grid]
    return [''.join(row) for row in grid]

def canvas(name,size):
    im=Image.new('P',size,0);im.putpalette([v for rgb in RANGERS[name]['palette'] for v in rgb]+[0]*756);return im

def portrait(name,frame=0):
    im=canvas(name,(48,48));d=ImageDraw.Draw(im)
    def line(points,c=1,w=1):d.line(points,fill=c,width=w)
    def oval(box,c):d.ellipse(box,fill=c,outline=1)
    def poly(points,c):d.polygon(points,fill=c,outline=1)
    # Original half-length character composition, not an enlarged sprite.
    poly([(8,46),(8,34),(16,29),(32,29),(40,34),(41,47)],2)
    poly([(18,27),(18,33),(23,36),(30,31),(29,27)],3)
    oval((14,8,34,29),3);line([(18,20),(21,20)],1);line([(27,20),(30,20)],1)
    line([(23,21),(22,24),(24,24)],2);line([(21,27),(25,28),(29,26)],1)
    # Eyes/head/gear remain grounded while blinking or settling the notebook.
    if not frame:d.point((19,19),fill=1);d.point((28,19),fill=1)
    else:line([(18,19),(21,19)],1);line([(27,19),(30,19)],1)
    if name in ('nell','sol'):
        poly([(12,14),(14,7),(18,3),(31,3),(35,8),(37,14)],2)
        line([(14,10),(34,10)],3,2);line([(8 if name=='sol' else 10,14),(40 if name=='sol' else 38,14)],1,3)
        if name=='nell':
            line([(14,15),(12,22),(13,28),(11,34),(14,37)],1,3)
            for y in (22,26,30,34):line([(11,y),(14,y+1)],3)
            poly([(11,34+frame),(21,32+frame),(23,43+frame),(13,45)],3);line([(14,36+frame),(20,35+frame)],1)
        else:
            poly([(15,29),(24,34),(33,29),(31,37),(24,39),(17,35)],3)
            line([(18,36),(15,43)],3,2)
    elif name=='iris':
        poly([(10,18),(11,8),(16,3),(30,3),(36,9),(38,21),(33,25),(34,13),(30,8),(18,8),(13,16),(14,26)],2)
        for x,y in [(14,15),(16,13),(31,13),(33,16)]:oval((x,y,x+2,y+2),1)
        poly([(8,35+frame),(20,32+frame),(23,44),(11,47)],3)
        for y in (36,39,42):line([(12,y+frame),(18,y-1+frame)],1)
    else:
        poly([(13,12),(13,6),(18,2),(31,2),(35,7),(35,14)],2)
        line([(14,11),(34,11)],3,2);line([(16,26),(19,30),(28,30),(32,26)],1,3)
        poly([(8,37),(20,34),(25,41),(15,46)],3)
        line([(12,38),(18,36),(20,40),(15,43)],1)
    line([(30,33),(26,38),(24,43)],1,2)
    # Nell/Sol camera, Vale binoculars, Iris notebook keep prop identities clear.
    if name in ('nell','sol'):
        d.rectangle((26,38,37,45),fill=1);d.rectangle((28,39,35,44),fill=2);oval((30,39,34,43),3)
        d.rectangle((28,37,31,38),fill=1)
    elif name=='vale':
        d.rectangle((28,38,31,45),fill=1);d.rectangle((34,38,37,45),fill=1);line([(31,40),(34,40)],1,2)
        d.point((29,44),fill=3);d.point((35,44),fill=3)
    return im

# Preserve the four early concepts as editable source studies. The production
# identities below map one-to-one to campaign districts, never district/4.
LEGACY_RANGERS=RANGERS
legacy_portrait=portrait
legacy_sprite=sprite
# name, headgear, hair, prop, shoulders, facebox, palette, personal field habit
PROFILES=[
('nell','brim','braid','camera',0,(14,8,34,29),(72,136,88),(240,200,144),'Draws tiny habitat sketches before reaching for the camera.'),
('sol','sun','short','camera',1,(13,9,35,29),(184,112,56),(240,208,144),'Reads shade and sand tracks; packs extra water for friends.'),
('ivo','cap','beard','compass',2,(15,8,34,30),(112,136,168),(208,160,112),'Likes comparing basin refuges and folds maps into perfect squares.'),
('tess','none','curls','journal',1,(12,8,35,28),(160,104,72),(224,168,120),'Keeps an oak-leaf bookmark and notices connections between homes.'),
('mira','wool','long','binoculars',0,(15,9,33,30),(112,112,184),(232,192,160),'Waits quietly beside high-country water and loves clear reflections.'),
('june','visor','ponytail','waterbook',2,(13,8,33,28),(88,160,152),(200,136,96),'Records seasonal water changes with a pencil tied to the notebook.'),
('ada','none','bun','journal',0,(15,7,35,29),(168,144,64),(216,176,128),'Asks careful comparison questions and marks every page with tabs.'),
('finn','bucket','short','lens',1,(14,9,34,31),(64,128,144),(224,184,136),'Finds the creek-to-rock route and carries a battered lens pouch.'),
('bea','hood','curls','waterbook',2,(15,10,34,30),(112,160,120),(184,120,88),'Enjoys foggy observation mornings and keeps a waterproof field folder.'),
('rui','visor','sweep','scope',0,(14,7,33,29),(96,144,192),(232,176,120),'Watches coastal refuges from a distance and teaches patient framing.'),
('leo','cap','afro','binoculars',1,(13,8,35,29),(168,88,72),(168,112,80),'Makes mountain trail comparisons and laughs at their own muddy boots.'),
('uma','sun','plaits','scope',0,(15,9,34,30),(88,160,184),(216,160,104),'Keeps island observation notes and spots quiet offshore shapes.'),
('kit','none','pixie','magnifier',2,(13,8,33,27),(144,128,72),(240,200,160),'Examines forest layers with a hand lens while leaving each home intact.'),
('oren','wool','beard','map',1,(12,9,35,32),(144,104,144),(200,152,112),'Remembers every small habitat pocket and shares folded trail diagrams.'),
('wren','bucket','bob','camera',0,(15,10,35,30),(104,144,96),(232,184,136),'Sketches volcanic stones and photographs the neighbors beside them.'),
('pax','earflap','short','compass',2,(14,10,33,30),(152,120,72),(176,120,88),'Greets plateau dawns with a warm scarf and a well-used compass.'),
]
RANGERS={}
for i,(name,hat,hair,prop,shape,face,coat,skin,habit) in enumerate(PROFILES):
    RANGERS[name]={'name':'RANGER '+name.upper(),'ranger_name':name.upper(),'district_id':f'D{i+1:02}',
        'district_index':i,'districts':[f'D{i+1:02}'],'headgear':hat,'hairstyle':hair,'prop':prop,
        'shape':shape,'face':face,'palette':[(248,0,248),(32,32,40),coat,skin],
        'personality':habit,'gear':f'{hat} headwear, {hair} hair, {prop}, walking boots'}

def sprite(name,direction='down',frame=0):
    spec=RANGERS[name];hat=spec['headgear'];hair=spec['hairstyle'];prop=spec['prop']
    grid=[list(r) for r in (SIDE if direction in ('right','left') else FRONT)]
    # At sixteen pixels headgear, hair and carried-tool silhouettes carry identity.
    for y in range(1,5):
        for x in range(1,15):grid[y][x]='.'
    for y in (2,3):
        for x in range(5,11):grid[y][x]='1' if y==2 else '2'
    if hat in ('brim','sun','bucket','visor'):
        for x in range(2 if hat=='sun' else 3,14 if hat=='sun' else 13):grid[4][x]='1'
        if hat=='bucket':grid[2][4]=grid[2][11]='2'
        if hat=='visor':
            for x in range(5,11):grid[2][x]='1';grid[3][x]='3'
    elif hat in ('hood','earflap'):
        for y in range(3,10):grid[y][3]=grid[y][12]='2'
        for x in range(4,12):grid[1][x]='1'
    elif hat in ('cap','wool'):
        for x in range(4,12):grid[3][x]='3' if hat=='wool' else '2'
        if hat=='cap':grid[4][12]=grid[4][13]='1'
    else:
        for x in range(4,12):grid[3][x]=grid[4][x]='1'
    if hair=='afro':
        for x,y in ((3,2),(4,1),(6,1),(9,1),(11,1),(12,2),(3,4),(12,4)):grid[y][x]='1'
    elif hair=='bun':grid[1][6]=grid[1][7]=grid[0][7]=grid[0][8]='1'
    elif hair in ('braid','plaits','long','ponytail','bob'):
        for y in range(7,14 if hair in ('braid','plaits') else 11):
            grid[y][11]='1'
            if hair in ('plaits','long','bob'):grid[y][4]='1'
            if hair=='braid' and y%2:grid[y][12]='3'
    elif hair in ('curls','sweep','pixie'):
        for x,y in ((4,5),(5,4),(6,5),(10,4),(11,5),(4,7)):grid[y][x]='1'
        if hair=='sweep':grid[5][9]=grid[5][8]='1'
    if hair=='beard':
        for x in range(5,11):grid[8][x]='1'
    if spec['shape']==1:
        grid[10][2]=grid[10][13]='2';grid[11][2]=grid[11][13]='1'
    if spec['shape']==2:
        for y in (10,11):grid[y][3]=grid[y][12]='.'
        grid[16][3]=grid[16][12]='2'
    # Boots share a grounded stride; tools and shoulder width are authored above.
    if frame:
        for y in (19,20,21,22):
            for x in range(4,12):grid[y][x]='.'
        pts=([(5,19,'2'),(5,20,'2'),(4,21,'1'),(5,21,'1'),(6,21,'1'),(9,19,'2'),(9,20,'2'),(9,21,'3'),(9,22,'1'),(10,22,'1')] if frame==1 else [(6,19,'2'),(6,20,'2'),(5,22,'1'),(6,22,'1'),(7,22,'1'),(10,19,'2'),(10,20,'2'),(9,21,'1'),(10,21,'1'),(11,21,'1')])
        for x,y,c in pts:grid[y][x]=c
    if direction=='up':
        for y in range(5,9):
            for x in range(5,11):grid[y][x]='1' if y<7 else '2'
        for y in range(10,16):
            for x in range(5,11):grid[y][x]='2'
        for x in range(5,11):grid[11][x]='1';grid[15][x]='1'
    else:
        if prop in ('journal','waterbook','map'):
            for y in range(12,16):grid[y][3]='1';grid[y][4]=grid[y][5]='3'
        elif prop in ('scope','lens'):
            for y in range(11,15):grid[y][12]='1';grid[y][13]='2'
        elif prop=='binoculars':grid[12][6]=grid[12][9]='1';grid[13][6]=grid[13][9]='3'
        elif prop=='magnifier':grid[12][3]=grid[12][4]=grid[13][3]=grid[13][4]='3';grid[14][4]='1'
        elif prop=='compass':grid[12][6]=grid[12][7]='3';grid[13][6]=grid[13][7]='1'
    if direction=='left':grid=[row[::-1] for row in grid]
    return [''.join(row) for row in grid]

def portrait(name,frame=0):
    spec=RANGERS[name];im=canvas(name,(48,48));d=ImageDraw.Draw(im)
    def line(points,c=1,w=1):d.line(points,fill=c,width=w)
    def oval(box,c):d.ellipse(box,fill=c,outline=1)
    def poly(points,c):d.polygon(points,fill=c,outline=1)
    hat,hair,prop=spec['headgear'],spec['hairstyle'],spec['prop'];a,b,c,e=spec['face'];cx=(a+c)//2
    shoulder=(8,5,11)[spec['shape']]
    poly([(shoulder,47),(shoulder,35),(17,30),(31,30),(48-shoulder,35),(48-shoulder,47)],2)
    poly([(19,27),(19,32),(cx,36),(30,31),(29,27)],3)
    oval((a,b,c,e),3)
    # Cheek/nose/mouth proportions vary with the explicit face boxes.
    eye_y=b+11;line([(a+4,eye_y-2),(a+7,eye_y-2)],1);line([(c-7,eye_y-2),(c-4,eye_y-2)],1)
    if frame:line([(a+4,eye_y),(a+7,eye_y)],1);line([(c-7,eye_y),(c-4,eye_y)],1)
    else:d.point((a+5,eye_y),fill=1);d.point((c-5,eye_y),fill=1)
    line([(cx,eye_y+1),(cx-1,eye_y+4),(cx+1,eye_y+4)],2)
    line([(cx-4,e-3),(cx,e-2),(cx+4,e-4)],1)
    if hair in ('long','bob','plaits','braid','ponytail'):
        length=35 if hair in ('plaits','braid') else 29
        line([(a,b+4),(a-2,20),(a-1,length)],1,3)
        if hair in ('long','plaits','bob'):line([(c,b+4),(c+2,20),(c+1,length)],1,3)
        if hair=='braid':
            for y in (20,24,28,32):line([(a-3,y),(a,y+1)],3)
        if hair=='ponytail':poly([(c,10),(c+4,12),(c+5,24),(c+1,29),(c+1,17)],1)
    elif hair=='afro':
        for x,y in ((a-1,10),(a+2,5),(a+7,3),(cx+3,3),(c-3,5),(c+1,10)):oval((x-3,y-3,x+4,y+4),1)
    elif hair=='bun':oval((cx-5,1,cx+4,9),1);line([(a+1,12),(a+3,5),(c-3,5),(c-1,12)],1,3)
    elif hair in ('curls','sweep','pixie'):
        for x,y in ((a+1,10),(a+4,7),(cx,6),(c-4,7),(c-1,11)):oval((x-2,y-2,x+2,y+2),1)
        if hair=='sweep':poly([(a+2,7),(c-3,6),(cx,14),(a+2,12)],1)
    elif hair=='beard':line([(a+2,e-5),(a+5,e+1),(c-5,e+1),(c-2,e-5)],1,3)
    else:line([(a+1,b+3),(a+4,b),(c-3,b),(c-1,b+4)],1,2)
    if hat in ('brim','sun','bucket'):
        poly([(a-2,13),(a,7),(a+4,3),(c-4,3),(c,7),(c+2,13)],2)
        line([(a,10),(c,10)],3,2);line([(5 if hat=='sun' else a-5,14),(43 if hat=='sun' else c+5,14)],1,3)
        if hat=='bucket':line([(a-2,12),(a-5,16),(c+4,16),(c+1,12)],2,2)
    elif hat in ('cap','visor'):
        if hat=='cap':poly([(a,12),(a+2,4),(c-3,3),(c+1,11)],2)
        line([(a-1,12),(c+5,12)],1,3);line([(a+1,11),(c+2,11)],3)
    elif hat in ('wool','earflap'):
        poly([(a-1,13),(a,6),(a+4,2),(c-3,2),(c,6),(c+1,13)],2)
        line([(a-1,12),(c+1,12)],3,2)
        if hat=='earflap':line([(a,12),(a-2,23)],2,3);line([(c,12),(c+2,23)],2,3)
    elif hat=='hood':
        poly([(a-5,24),(a-5,10),(a,3),(c-2,3),(c+5,10),(c+5,25),(c+1,27),(c+1,12),(c-3,8),(a+3,8),(a-1,13),(a-1,27)],2)
    # Individually authored face details and clothing cuts, not palette swaps.
    if name in ('ivo','ada'):
        d.rectangle((a+2,eye_y-2,a+8,eye_y+2),outline=1)
        d.rectangle((c-8,eye_y-2,c-2,eye_y+2),outline=1)
        line([(a+8,eye_y-1),(c-8,eye_y-1)],1)
    if name=='kit':
        poly([(a+2,eye_y-2),(a+9,eye_y-2),(a+6,eye_y+3)],1)
        poly([(c-9,eye_y-2),(c-2,eye_y-2),(c-6,eye_y+3)],1)
        d.point((a+6,eye_y),fill=3);d.point((c-6,eye_y),fill=3)
    if name in ('tess','wren'):
        for x,y in ((a+3,eye_y+4),(a+5,eye_y+5),(c-3,eye_y+4),(c-5,eye_y+5)):d.point((x,y),fill=2)
    if name=='finn':line([(a+4,e-2),(cx,e),(c-4,e-2)],2)
    if name in ('mira','uma'):oval((c,eye_y+3,c+2,eye_y+5),2)
    if name=='leo':line([(c-5,e-5),(c-3,e-4)],2)
    if name in ('sol','pax','wren'):
        poly([(17,29),(cx,34),(32,29),(31,35),(cx,39),(18,35)],3)
        line([(20,35),(17,42)],3,2)
    # Field clothes: open lapels, pockets, strap and explicit hand positions.
    line([(17,31),(20,39),(cx,36),(29,39),(32,31)],1)
    line([(11,34),(28,45)],1,2)
    d.rectangle((31,34,36,38),fill=1);line([(32,35),(35,35)],3)
    y=36+frame
    if prop in ('journal','waterbook','map'):
        poly([(9,y),(21,y-3),(25,45),(13,47)],3)
        for yy in (y+2,y+5):line([(13,yy),(20,yy-1)],1)
        if prop=='map':line([(16,y),(17,44),(22,42)],2);line([(11,y+5),(22,y+1)],2)
        if prop=='waterbook':line([(10,y),(20,y-3)],2,2)
        oval((20,39+frame,25,42+frame),3)
    elif prop=='camera':
        d.rectangle((25,y,38,y+8),fill=1);d.rectangle((27,y+1,36,y+7),fill=2);oval((29,y+1,35,y+7),3);d.rectangle((27,y-2,30,y),fill=1)
        oval((22,y+2,26,y+6),3)
    elif prop=='binoculars':
        d.rectangle((24,y,29,y+9),fill=1);d.rectangle((33,y,38,y+9),fill=1);line([(29,y+3),(33,y+3)],1,2)
        line([(25,y+7),(28,y+7)],3);line([(34,y+7),(37,y+7)],3);oval((20,y+3,24,y+6),3)
    elif prop in ('scope','lens'):
        poly([(23,y+3),(31,y-2),(39,y),(39,y+5),(29,y+7)],1);line([(30,y),(37,y+2)],2,3);line([(25,y+4),(28,y+5)],3,2)
        if prop=='scope':line([(31,y+6),(27,47)],1,2)
    elif prop=='magnifier':
        oval((10,y-3,20,y+7),1);oval((12,y-1,18,y+5),3);line([(18,y+5),(24,47)],1,3);oval((21,y+7,25,y+10),3)
    else:
        oval((24,y,36,y+11),1);oval((26,y+2,34,y+9),3);poly([(30,y+3),(28,y+7),(32,y+7)],2);oval((20,y+4,25,y+8),3)
    return im

def emit_ranger_art(output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);result={};sheet=Image.new('RGB',(4*144,4*112),(208,200,168));d=ImageDraw.Draw(sheet)
    for n,(name,spec) in enumerate(RANGERS.items()):
        frames=[];source=canvas(name,(192,24));padded=canvas(name,(192,32));source.info['transparency']=padded.info['transparency']=0
        for i,(direction,frame) in enumerate((dr,f) for dr in ('down','right','up','left') for f in range(3)):
            grid=sprite(name,direction,frame);assert len(grid)==24 and all(len(r)==16 for r in grid)
            im=canvas(name,(16,24));im.info['transparency']=0
            for y,row in enumerate(grid):
                for x,ch in enumerate(row):im.putpixel((x,y),0 if ch=='.' else int(ch))
            filename=f'npc_{name}_{direction}_{frame}.png';im.save(out/filename);source.paste(im,(i*16,0));padded.paste(im,(i*16,0));frames.append(filename)
        sprite_name=f'npc_{name}.png';source.save(out/sprite_name);padded_name=f'npc_{name}_padded32.png';padded.save(out/padded_name)
        portrait_frames=[]
        for f in range(2):filename=f'npc_portrait_{name}_idle{f}.png';portrait(name,f).save(out/filename);portrait_frames.append(filename)
        for f in range(2):portrait(name,f).resize((32,32),Image.Resampling.NEAREST).save(out/f'npc_portrait32_{name}_idle{f}.png')
        still=f'npc_portrait_{name}.png';portrait(name).save(out/still);small=f'npc_portrait32_{name}.png';portrait(name).resize((32,32),Image.Resampling.NEAREST).save(out/small)
        pal=spec['palette'];result[name]={**spec,'sprite':sprite_name,'sprite_padded32':padded_name,'sprite_dimensions':[192,24],'frame_dimensions':[16,24],'sprite_frames':frames,'portrait':still,'portrait32':small,'frames':portrait_frames,'palette_rgb555':[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in pal],'frame_duration_ticks':12,'direction_order':['down','right','up','left'],'portrait32_frames':[f'npc_portrait32_{name}_idle{f}.png' for f in range(2)],'native_meta_requirement':'16x24actor padded32 atlas; idleframe0 walkframes1/2 eachdirection','obj_budget_per_actor':4,'maximum_obj_per_scanline_per_actor':2,'bg_tiles_per_idle_frame':6,'status':'authored_source_not_native_integrated_or_observed'}
        for f in range(2):
            im=portrait(name,f);rgba=im.convert('RGBA');mask=Image.new('L',im.size);mask.putdata([255 if v else 0 for v in im.get_flattened_data()]);rgba.putalpha(mask);sheet.paste(rgba,((n%4)*144+f*50+4,(n//4)*112+5),rgba)
        ico=Image.open(out/frames[0]).convert('RGBA');sheet.paste(ico,((n%4)*144+110,(n//4)*112+12),ico);d.text(((n%4)*144+2,(n//4)*112+59),spec['name'],fill=(32,32,32))
        d.text(((n%4)*144+2,(n//4)*112+75),spec['gear'].split(',')[0],fill=(32,32,32))
    campaign=json.loads((Path(__file__).resolve().parents[2]/'data/campaign.json').read_text())['districts']
    assert [(m['district_id'],m['ranger_name'],m['district_index']) for m in result.values()]==[(d['district_id'],d['ranger_name'],d['native_district']) for d in campaign]
    assert len({bytes(portrait(name).get_flattened_data()) for name in result})==16
    assert len({bytes(Image.open(out/m['sprite_frames'][0]).get_flattened_data()) for m in result.values()})==16
    receipt={'status':'authored_source_checked_not_native_observed','rangers':16,'native_sprite_frames':192,'portrait48_frames':32,'portrait32_frames':32,'distinct_portrait_index_patterns':16,'distinct_front_sprite_index_patterns':16,'campaign_identity_mapping_checked':True,'palette': 'four RGB555-aligned colors per identity; slot0 transparent','pending':['Native compiler integration and bank limits','District NPC identity in emulator','Movement/OAM scanline budget in actual world','Human face/readability/personality review','Physical Chromatic display acceptance'],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'ranger-art-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'ranger-art-manifest.json').write_text(json.dumps(result,indent=2)+'\n');sheet.resize((1152,896),Image.Resampling.NEAREST).save(out/'ranger-art-contact-sheet_2x.png')
    for name,m in result.items():
        for fn in m['sprite_frames']+m['frames']+[m['portrait'],m['portrait32'],m['sprite'],m['sprite_padded32']]:
            im=Image.open(out/fn);assert im.mode=='P' and set(im.get_flattened_data())<={0,1,2,3}
        assert bytes(portrait(name,0).get_flattened_data())!=bytes(portrait(name,1).get_flattened_data())
    return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('output_dir');a=p.parse_args();emit_ranger_art(a.output_dir)
