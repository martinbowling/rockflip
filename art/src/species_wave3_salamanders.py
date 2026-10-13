"""Original editable Caudata artwork: independent icons and 48px photographs.

Source production only. No traced photography, real locality, defense display or
new species identity. Edit PROFILES, POSES, FOOT_TIPS and marking coordinates.
Distinct poses are composition choices, not diagnostic natural-history claims.
The canonical make_sprites.py is deliberately untouched by this wave.
"""
from pathlib import Path
import hashlib,json,math,textwrap
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
PALETTES={
 'brown':[(184,208,176),(24,24,16),(88,72,48),(184,152,96)],
 'rust':[(192,208,176),(32,24,16),(104,72,48),(192,112,64)],
 'bronze':[(176,200,176),(24,32,24),(72,80,56),(168,160,96)],
 'black':[(184,208,184),(16,24,24),(40,48,40),(152,168,136)],
 'frost':[(184,208,192),(16,24,24),(48,64,56),(144,168,144)],
 'newt':[(176,208,192),(32,32,24),(104,80,48),(232,168,64)],
 'red_newt':[(184,208,184),(24,24,24),(64,56,40),(208,88,48)],
 'yellow':[(184,208,176),(16,24,24),(56,64,48),(216,200,88)],
 'granite':[(192,208,200),(32,32,32),(104,104,80),(192,184,128)],
}
SOURCES={
 'aneides_revision':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6679913/',
 'wandering':'https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/wandering-salamander-2014.html',
 'clouded':'https://research.fs.usda.gov/treesearch/25045',
 'sierra_slender_1998':'https://www.biodiversitylibrary.org/part/208101',
 'coastal_slender_2001':'https://www.researchgate.net/publication/272542972_Molecular_Phylogenetic_Analysis_of_Slender_Salamanders_Genus_Batrachoseps_Amphibia_Plethodontidae_from_Central_Coastal_California_with_Descriptions_of_Four_New_Species',
 'sierra_slender_2012':'https://doi.org/10.11646/zootaxa.3190.1.1',
 'robustus':'https://www.researchgate.net/publication/250067402_New_Species_of_Slender_Salamander_Genus_Batrachoseps_from_the_Southern_Sierra_Nevada_of_California',
 'stebbinsi':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=32034',
 'wakei':'https://bioone.org/journals/ichthyology-and-herpetology/volume-109/issue-3/h2020027/A-New-Relict-Species-of-Slender-Salamander-Plethodontidae--Batrachoseps/10.1643/h2020027.pdf',
 'hydromantes':'https://escholarship.org/content/qt7sk3n2dq/qt7sk3n2dq.pdf',
 'plethodon':'https://www.fs.usda.gov/pnw/pubs/pnw_gtr337.pdf',
 'asupak':'https://www.researchgate.net/publication/237211279_Newly_discovered_populations_of_salamanders_from_Siskiyou_County_California_represent_a_species_distinct_from_Plethodon_stormi',
 'longtoe':'https://www.nps.gov/glac/learn/nature/amphibians.htm',
 'ensatina':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1438',
 'giant_california':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=190337&inline=',
 'giant_coastal':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1510',
 'newts':'https://www.nps.gov/crla/learn/nature/mazama-newts.htm',
 'rivularis':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=190363&inline=',
 'sierra_newt':'https://www.nps.gov/seki/learn/nature/amphibfish.htm',
 'lyell':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1460',
 'brunus':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1464',
 'attenuatus':'https://home.nps.gov/prsf/learn/nature/california-slender-salamander.htm',
 'nigriventris':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1444',
 'pacificus':'https://irmadev.nps.gov/DataStore/Reference/Profile/2286638',
 'major':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1440',
 'simatus':'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=1448',
}
# stable ID, art ID, family, pose, body/head pixel widths, limb reach,
# representative adult marking, palette, proportion/identity note, source key.
PROFILES=[
(20,'long_toed_salamander','mole',0,7,8,7,'broken_stripe','yellow','Longest fourth hind toe; dark body with uneven dorsal stripe.','longtoe'),
(26,'clouded_salamander','aneides',1,8,9,8,'clouds','bronze','Long climbing limbs, squared toe tips; clouded bronze-gray representative.','clouded'),
(27,'black_salamander','aneides',2,9,10,7,'few_speckles','black','Robust broad head; representative speckled form, not every population.','aneides_revision'),
(28,'shasta_black_salamander','aneides',3,9,10,8,'dense_speckles','black','Robust jaw; numerous small pale speckles rather than universal black silhouette.','aneides_revision'),
(29,'klamath_black_salamander','aneides',4,8,9,8,'frost','frost','Broad head and terminally expanded digits; frosted adult color form.','aneides_revision'),
(30,'santa_cruz_black_salamander','aneides',5,9,11,7,'plain','black','Broad jaw and nearly black adult form; labels remain necessary.','aneides_revision'),
(31,'wandering_salamander','aneides',6,7,8,9,'bronze_mottle','bronze','Long legs and squared terminal digits; mottling varies with age.','wandering'),
(38,'greenhorn_slender_salamander','slender',1,5,6,5,'narrow_stripe','brown','Slender trunk, small four-toed feet; current altasierrae, not historical relictus.','sierra_slender_2012'),
(39,'california_slender_salamander','slender',2,4,5,4,'dorsal_ribbon','rust','Very narrow body, small feet and long cylindrical tapering tail.','attenuatus'),
(40,'fairview_slender_salamander','slender',3,5,6,6,'broken_ribbon','rust','Current upper-canyon species; moderately developed feet and long tail.','sierra_slender_2012'),
(42,'hell_hollow_slender_salamander','slender',4,5,6,5,'fleck_band','brown','Four-toed slender salamander; larger head than most delicate drawn forms.','sierra_slender_1998'),
(44,'gabilan_slender_salamander','slender',5,5,6,5,'light_mottle','brown','Four-toed slender form; external resemblance cannot replace identity labels.','coastal_slender_2001'),
(45,'gregarious_slender_salamander','slender',6,4,5,4,'fine_ribbon','rust','Long thin trunk and small four-toed feet; not a social-pose collectible.','sierra_slender_1998'),
(46,'san_simeon_slender_salamander','slender',7,5,6,5,'broken_ribbon','brown','Conservative thin-bodied coastal-complex adult, four toes each foot.','coastal_slender_2001'),
(47,'sequoia_slender_salamander','slender',8,5,6,5,'light_mottle','bronze','Small four-toed feet and long tail; diagnosis requires context.','sierra_slender_1998'),
(48,'santa_lucia_slender_salamander','slender',9,5,6,5,'dorsal_ribbon','brown','Slender coastal-complex adult; composition variation is not diagnostic.','coastal_slender_2001'),
(49,'southern_slender_salamander','slender',10,6,7,5,'vermiculate','brown','Larger pacificus-group form; vermiculate tan dorsal pattern on brown.','wakei'),
(50,'lesser_slender_salamander','slender',11,4,5,4,'fine_ribbon','brown','Small gracile form with tiny four-toed limbs; independent pose.','coastal_slender_2001'),
(51,'black_bellied_slender_salamander','slender',12,4,5,4,'dorsal_ribbon','rust','Thin trunk and long tail; dark venter cannot be identified from this dorsal art.','nigriventris'),
(52,'channel_islands_slender_salamander','slender',13,6,7,5,'vermiculate','bronze','Larger pacificus-group form, tan longitudinal mottling; species labels essential.','wakei'),
(53,'kings_river_slender_salamander','slender',14,5,6,5,'fleck_band','brown','Four-toed slender adult; separately authored posture, not new color taxon.','sierra_slender_1998'),
(54,'relictual_slender_salamander','slender',15,5,6,5,'broken_ribbon','brown','Current restricted relictus form; not a placeholder for former altasierrae.','sierra_slender_2012'),
(55,'kern_plateau_slender_salamander','slender_robust',2,7,8,6,'rust_mottle','rust','Broad head, robust short trunk and stout tail; larger feet, four toes.','robustus'),
(56,'kern_canyon_slender_salamander','slender',0,5,6,5,'dorsal_ribbon','brown','Current lower-canyon identity; separately posed thin adult with four toes.','simatus'),
(57,'tehachapi_slender_salamander','slender_robust',4,7,8,8,'patches','rust','Long legs and unusually large, more webbed four-toed feet; robust body.','stebbinsi'),
(75,'california_giant_salamander','giant',1,11,13,8,'marble','bronze','Adult broad head and stout body; marbled color, no larval external gills.','giant_california'),
(76,'coastal_giant_salamander','giant',5,10,12,8,'marble','brown','Adult stout limbs and strong tail; marbling variable and not a unique ID.','giant_coastal'),
(79,'ensatina','ensatina',7,8,10,8,'warm_flanks','rust','Constriction at tail base; large eyes and moderately robust body.','ensatina'),
(84,'limestone_salamander','web',2,8,11,8,'brown_fleck','brown','Broad flattened head, webbed hands/feet; short strongly tapered tail.','brunus'),
(85,'mount_lyell_salamander','web',3,8,12,8,'granite_mottle','granite','Very broad flattened head and webbed feet; short tapered tail.','lyell'),
(86,'samwel_shasta_salamander','web',9,7,9,8,'brown_fleck','brown','Cryptic Shasta-complex form; short blunt tapering tail, sepia/chestnut adult.','hydromantes'),
(88,'wintu_shasta_salamander','web',12,7,9,8,'tail_ochre','bronze','Cryptic Shasta-complex form; ochre-tailed color form, light webbed feet.','hydromantes'),
(104,'scott_bar_salamander','plethodon',6,8,9,8,'paired_band','brown','More robust, wider head and longer limbs than elongatus/stormi.','asupak'),
(105,'dunns_salamander','plethodon',8,7,8,7,'wide_band','bronze','Broad greenish/tan dorsal band on dark ground; five hind toes.','plethodon'),
(106,'del_norte_salamander','plethodon',10,6,7,6,'narrow_band','rust','Slender long trunk, short limbs and faint reddish-brown dorsal band.','plethodon'),
(107,'siskiyou_mountains_salamander','plethodon',14,7,8,7,'fine_speckles','brown','Intermediate robust body and pale flecking; cryptic relatives need labels.','plethodon'),
(128,'rough_skinned_newt','newt',0,9,9,7,'grain','newt','Robust terrestrial newt; grainy skin and orange underside, not scales.','newts'),
(129,'red_bellied_newt','newt',11,9,9,7,'grain_red','red_newt','Robust dark terrestrial newt with reddish belly and dark eyes.','rivularis'),
(130,'sierra_newt','newt',13,8,9,7,'grain_gold','newt','Terrestrial roughened skin; closely resembles California newt, no defensive arch.','sierra_newt'),
(150,'arguello_slender_salamander','slender_robust',15,6,6,6,'wakei','rust','Large long-bodied species, relatively small rounded head; vermiculate tan marks.','wakei'),
]
# Each whole-animal portrait is authored at native 48px, never scaled from icon.
# Head -> shoulder -> waist -> rump. Tail control points follow independently.
POSES=[
 ([(33,10),(30,17),(25,24),(20,30)],[(20,30),(15,35),(8,37),(5,32),(8,27)]),
 ([(31,12),(27,17),(23,24),(18,30)],[(18,30),(17,37),(24,41),(34,38),(38,32)]),
 ([(32,13),(28,18),(23,24),(19,30)],[(19,30),(12,34),(6,34),(4,27),(9,23)]),
 ([(29,11),(26,17),(22,24),(17,30)],[(17,30),(13,37),(20,41),(31,39),(36,33)]),
 ([(30,11),(28,18),(23,25),(18,31)],[(18,31),(11,34),(7,40),(15,43),(23,40)]),
 ([(32,14),(27,18),(23,24),(18,30)],[(18,30),(12,33),(7,31),(4,23),(8,17)]),
 ([(31,10),(29,17),(24,23),(19,29)],[(19,29),(14,34),(13,41),(22,43),(29,39)]),
 ([(30,12),(28,18),(25,24),(20,30)],[(20,30),(16,36),(9,39),(4,35),(5,29)]),
 ([(32,10),(28,17),(25,23),(20,30)],[(20,30),(18,36),(24,41),(33,41),(39,37)]),
 ([(30,11),(27,17),(24,24),(20,31)],[(20,31),(14,36),(7,36),(4,30),(6,24)]),
 ([(33,12),(29,18),(25,25),(20,31)],[(20,31),(16,37),(22,42),(33,39),(38,34)]),
 ([(31,13),(27,18),(23,24),(18,31)],[(18,31),(11,35),(5,33),(4,27),(7,21)]),
 ([(31,10),(29,17),(25,24),(21,30)],[(21,30),(16,36),(8,40),(5,34),(7,28)]),
 ([(33,13),(29,18),(24,24),(19,30)],[(19,30),(16,37),(22,43),(31,41),(37,36)]),
 ([(31,11),(28,17),(23,24),(18,30)],[(18,30),(13,35),(6,37),(4,31),(9,26)]),
 ([(32,12),(29,18),(24,24),(19,31)],[(19,31),(15,37),(20,43),(30,42),(37,38)]),
]
FOOT_TIPS={4:[(-3,3),(-1,4),(1,4),(3,3)],5:[(-4,2),(-2,4),(0,5),(2,4),(4,2)]}
BY_ART={p[1]:p for p in PROFILES}
SELECTION=[(p[0],p[1],p[2],PALETTES[p[8]]) for p in PROFILES]

def canvas(art,size=(48,48),transparent=False):
    im=Image.new('P',size,0)
    im.putpalette([v for rgb in PALETTES[BY_ART[art][8]] for v in rgb]+[0]*756)
    if transparent:im.info['transparency']=0
    return im

def segment(draw,a,b,width,c):
    draw.line([a,b],fill=c,width=max(1,width))
    r=max(0,(width-1)//2)
    for x,y in (a,b):draw.ellipse((x-r,y-r,x+r,y+r),fill=c)

def tapered(draw,path,width,c):
    for n,(a,b) in enumerate(zip(path,path[1:])):
        length=max(abs(b[0]-a[0]),abs(b[1]-a[1]))
        for t in range(length+1):
            z=t/max(1,length);x=round(a[0]+(b[0]-a[0])*z);y=round(a[1]+(b[1]-a[1])*z)
            w=max(1,round(width*(1-(n+z)/max(1,len(path)-1))))
            r=w//2 if w>1 else 0;draw.ellipse((x-r,y-r,x+r,y+r),fill=c)

def foot(draw,xy,toes,web=False,longtoe=False):
    x,y=xy;tips=FOOT_TIPS[toes]
    if web:draw.polygon([(x,y-1)]+[(x+dx,y+dy-1) for dx,dy in tips],fill=2,outline=1)
    for n,(dx,dy) in enumerate(tips):
        if longtoe and n==3:dy+=2
        draw.line([(x,y),(x+dx,y+dy)],fill=1,width=1)
        if web:draw.point((x+dx,y+dy),fill=3)
    draw.point((x,y),fill=2)

def portrait(art,frame=0):
    sid,_,family,pose,bw,hw,reach,pattern,_,note,source=BY_ART[art]
    im=canvas(art);d=ImageDraw.Draw(im);path=[tuple(xy) for xy in POSES[pose][0]];tail=list(POSES[pose][1]);head=path[0];rump=path[-1]
    short=family=='web';tail=tail[:3] if short else tail
    if short:tail[-1]=(tail[-2][0]-5,tail[-2][1]+2)
    if frame:tail[-1]=(tail[-1][0]+1,tail[-1][1]-1)
    tailw=max(4,bw-1) if family in ('giant','newt','ensatina','slender_robust','web') else max(3,bw-2)
    # All tails taper as a whole; web-footed forms keep a blunt tip.
    tapered(d,tail,tailw+2,1);tapered(d,tail,tailw,2)
    if family=='ensatina':segment(d,rump,tail[1],3,1);segment(d,rump,tail[1],1,2)
    # Four limbs remain grounded. Frame1 advances one forefoot, not a stress arch.
    limbwidth=3 if bw>=7 else 2
    for i,at in enumerate((path[1],path[-1])):
        for sign in (-1,1):
            ax,ay=at;el=(ax+sign*(reach-2),ay+1);end=(ax+sign*reach,ay+4)
            if frame and i==0 and sign==1:end=(end[0]+1,end[1]-1)
            segment(d,(ax,ay),el,limbwidth+1,1);segment(d,el,end,limbwidth+1,1)
            segment(d,(ax,ay),el,limbwidth-1,2);segment(d,el,end,limbwidth-1,2)
            toes=4 if family.startswith('slender') or i==0 else 5
            foot(d,end,toes,family=='web' or sid==57,sid==20 and i==1)
    for a,b in zip(path,path[1:]):segment(d,a,b,bw+2,1)
    for a,b in zip(path,path[1:]):segment(d,a,b,bw,2)
    hx,hy=head
    # Broad heads and modest eyes. Four indexed colors only, no antialiasing.
    headh=5 if family=='web' else 7 if family in ('giant','aneides') else 6
    d.ellipse((hx-hw//2,hy-headh//2,hx+hw//2,hy+headh//2),fill=2,outline=1)
    # Sample the whole trunk along its curve for costal folds and markings.
    samples=[]
    for a,b in zip(path,path[1:]):
        for t in range(5):
            z=t/5;samples.append((round(a[0]+(b[0]-a[0])*z),round(a[1]+(b[1]-a[1])*z)))
    for n,(x,y) in enumerate(samples[2:]):
        if n%2==0 and family!='newt':d.line([(x-bw//2+1,y),(x-bw//2+2,y+1)],fill=1)
    # Highlights express moist smooth skin, not reptile scales; newts alone grainy.
    if pattern in ('dorsal_ribbon','fine_ribbon','narrow_stripe','narrow_band','wide_band','paired_band','broken_stripe','broken_ribbon','fleck_band'):
        for n,(x,y) in enumerate(samples):
            if pattern in ('broken_stripe','broken_ribbon','fleck_band') and n%4==0:continue
            if pattern=='paired_band':d.point((x-1,y),fill=3);d.point((x+1,y),fill=3)
            else:d.line([(x,y),(x+(1 if pattern in ('dorsal_ribbon','wide_band') else 0),y)],fill=3)
    elif pattern=='plain':
        for x,y in samples[2:6]:d.point((x+1,y),fill=2)
    elif pattern in ('dense_speckles','few_speckles','frost','fine_speckles'):
        step=1 if pattern in ('dense_speckles','frost') else 3
        for n,(x,y) in enumerate(samples):
            if n%step==0:
                d.point((x+(n%3)-1,y),fill=3)
                if pattern=='frost':d.line([(x-bw//2+1,y),(x+1,y)],fill=3)
    elif pattern in ('vermiculate','wakei'):
        for n,(x,y) in enumerate(samples):
            d.point((x+(n%3)-1,y),fill=3)
            if n%3==0:d.point((x+1,y+1),fill=3)
        if pattern=='wakei':tapered(d,tail[-3:],3,3)
    elif pattern.startswith('grain'):
        for n,(x,y) in enumerate(samples):
            if n%3==0:d.point((x-2,y),fill=1);d.point((x+2,y+1),fill=1)
        # Side-view edge glimpse of underside; no unken reflex or deliberate flip.
        for x,y in samples[5:]:d.point((x-bw//2+1,y+1),fill=3)
    elif pattern=='tail_ochre':
        for n,(x,y) in enumerate(samples):
            if n%3==0:d.point((x+1,y),fill=3)
        tapered(d,tail,3,3)
    elif pattern=='warm_flanks':
        for x,y in samples[4:]:d.point((x-bw//2+1,y),fill=3)
    else:
        # Controlled natural mottling, fully deterministic editable species pattern.
        for n,(x,y) in enumerate(samples):
            if (n+sid)%3==0:
                x+=((n+sid)%3)-1
                if pattern in ('marble','patches','rust_mottle','clouds'):d.line([(x-1,y),(x+1,y+1)],fill=3,width=1)
                else:d.point((x,y),fill=3)
    # Two eyes and snout: orientation follows the independently drawn head.
    eyes=[(hx-hw//2+1,hy-1),(hx+hw//2-1,hy-1)]
    for x,y in eyes:
        d.rectangle((x,y,x+1,y+1),fill=1)
        if sid!=129:d.point((x,y),fill=3)
    d.line([(hx-1,hy-headh//2+1),(hx+1,hy-headh//2+1)],fill=1)
    return im

# Independently authored native16px stances. These are natural composition
# differences, not new diagnostic features or coordinate-scaled portrait grids.
ICON_POSES=[
 ((10,3),(8,8),[(8,9),(5,11),(3,14),(1,12)]),
 ((11,3),(7,8),[(7,9),(7,12),(11,13),(13,10)]),
 ((10,4),(7,8),[(7,9),(3,11),(2,9),(4,7)]),
 ((11,2),(7,8),[(7,9),(4,12),(7,14),(11,13)]),
 ((10,3),(7,9),[(7,10),(3,11),(2,14),(6,15)]),
 ((11,4),(7,8),[(7,9),(3,10),(1,7),(3,4)]),
 ((11,2),(8,8),[(8,9),(5,12),(5,15),(9,14)]),
 ((10,3),(8,9),[(8,10),(5,12),(2,13),(1,10)]),
 ((11,3),(8,8),[(8,9),(8,12),(11,14),(14,13)]),
 ((10,2),(8,9),[(8,10),(4,12),(2,10),(2,7)]),
 ((12,3),(8,9),[(8,10),(6,13),(9,15),(13,13)]),
 ((11,4),(7,9),[(7,10),(3,12),(1,10),(2,7)]),
 ((11,2),(9,8),[(9,9),(6,12),(2,14),(1,11)]),
 ((12,4),(8,8),[(8,9),(7,12),(10,15),(14,12)]),
 ((10,2),(7,8),[(7,9),(4,11),(1,13),(2,9)]),
 ((11,3),(8,9),[(8,10),(6,13),(9,15),(13,14)]),
]

def icon(art):
    sid,_,family,pose,bw,hw,reach,pattern,_,note,source=BY_ART[art]
    im=canvas(art,(16,16),True);d=ImageDraw.Draw(im)
    (hx,hy),(bx,by),original_tail=ICON_POSES[pose]
    rw=1 if family=='slender' else 2 if family in ('slender_robust','plethodon','mole') else 3
    tail=list(original_tail)
    if family=='web':tail=[(bx,by+1),(bx-2,by+3),(bx-4,by+3)]
    if family=='ensatina':d.line(tail,fill=1,width=3);d.line(tail,fill=2,width=1)
    else:d.line(tail,fill=1,width=rw+1);d.line(tail,fill=2,width=max(1,rw-1))
    shoulder=((hx*2+bx)//3,(hy*2+by)//3)
    for x,y in [shoulder,(bx,by)]:
        for sign in(-1,1):
            span=3 if family in ('web','aneides') or sid==57 else 2
            end=(x+sign*span,y+2)
            d.line([(x,y),end],fill=1,width=2)
            d.point(end,fill=2)
            if family=='web' or sid==57:d.point((end[0],end[1]+1),fill=2)
    d.line([(hx,hy),(bx,by)],fill=1,width=rw+3);d.line([(hx,hy),(bx,by)],fill=2,width=rw+1)
    head_extra=hw>=10
    d.ellipse((hx-2-head_extra,hy-2,hx+2,hy+1),fill=2,outline=1)
    d.point((hx+1,hy-1),fill=3)
    if pattern in ('dense_speckles','few_speckles','fine_speckles'):
        for n,(x,y) in enumerate([shoulder,(shoulder[0]-1,shoulder[1]+2),(bx,by)]):
            if pattern=='dense_speckles' or n==1:d.point((x,y),fill=3)
    elif pattern=='frost':d.line([(hx-1,hy+2),(bx,by)],fill=3,width=2)
    elif pattern!='plain':d.line([(hx-1,hy+2),(bx,by)],fill=3,width=1)
    if family=='newt':d.point((bx-1,by),fill=3)
    return im


def guide_lines(p):
    family=p[2]
    text={'slender':'FOUR TOES EACH FOOT.','slender_robust':'FOUR TOES EACH FOOT.','web':'WEBBED HANDS AND FEET.','newt':'A ROBUST NEWT.','aneides':'A LUNGLESS SALAMANDER.','plethodon':'A LUNGLESS SALAMANDER.','giant':'A STOUT ADULT FORM.','mole':'A LONG FOURTH TOE.','ensatina':'A NARROW TAIL BASE.'}[family]
    return textwrap.wrap(text,20)+['LOOK WITHOUT TOUCH.','PATTERNS CAN VARY.']

def emit_species_wave3_salamanders(output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    registry={r['species_id']:r for r in json.loads((ROOT/'data/production_roster.json').read_text())['records']}
    # Foundation18 are fixed stable roster IDs. Regeneration remains valid after
    # parent later integrates this wave into data/species.json.
    foundation_ids=set(range(18))
    from species_wave2 import SELECTION as wave2
    excluded={x[0] for x in wave2}
    remaining={r['species_id'] for r in registry.values() if r['group']=='Amphibia' and r['canonical_scientific_name'].split()[0] in {'Ambystoma','Aneides','Batrachoseps','Dicamptodon','Ensatina','Hydromantes','Plethodon','Rhyacotriton','Taricha'} and r['species_id'] not in excluded and r['species_id'] not in foundation_ids}
    assert remaining=={p[0] for p in PROFILES},(remaining^{p[0] for p in PROFILES})
    result={};validation=[];sheet=Image.new('RGB',(5*150,8*88),(184,200,176));label=ImageDraw.Draw(sheet)
    for n,p in enumerate(PROFILES):
        sid,art,family,pose,bw,hw,reach,pattern,pal,note,source=p;record=registry[sid];palette=PALETTES[pal];frames=[]
        for f in range(2):
            filename=f'portrait_{art}_idle{f}.png';portrait(art,f).save(out/filename);frames.append(filename)
        portrait_name=f'portrait_{art}.png';portrait(art).save(out/portrait_name)
        small=f'portrait32_{art}.png';portrait(art).resize((32,32),Image.Resampling.NEAREST).save(out/small)
        icon_name=f'critter_{art}.png';icon(art).save(out/icon_name)
        anim=canvas(art,(96,48));anim.paste(portrait(art,0),(0,0));anim.paste(portrait(art,1),(48,0));anim_name=f'portrait_{art}_animation.png';anim.save(out/anim_name)
        m={'art_id':art,'species_id':sid,'canonical_scientific_name':record['canonical_scientific_name'],'scientific_name_provisional':record['canonical_scientific_name'],'common_name':record['common_name'],'icon':icon_name,'portrait':portrait_name,'portrait32':small,'frames':frames,'animation_sheet':anim_name,'dimensions':[48,48],'icon_dimensions':[16,16],'palette':palette,'palette_rgb555':[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in palette],'frame_duration_ticks':36,'behavior_animation':'grounded_slow_step_tail_tip','status':'art_only_pending_independent_anatomy_and_native_review','taxon_count_approval':False,'anatomy_plan':family,'allowed_districts_from_roster':[r['region_id'] for r in record['region_permissions']],'review_notes':['Source art only. Individually composed original posture; not diagnostic species isolation.','External color forms vary. Source text and habitat/identity labels are required; no field identification from tiny sprites.','Portrait0/1 are independent native48px pixel compositions, not icon enlargements.','Four-toed versus five-toed hind feet are represented in portrait geometry; 16px icons cannot promise countable toes.',note],'anatomy_evidence_urls':[SOURCES[source]]+[u for perm in record['region_permissions'] for u in perm['evidence_urls'] if 'amphibiansoftheworld' in u][:1],'anatomy_review_status':'authored_source_informed_pending_independent_species_color_digit_and_proportion_review','representative_form':'terrestrial adult; variable color expression is illustrative, never a new taxon','guide_draft_lines':guide_lines(p),'color_index_contract':{'habitat':0,'outline_and_deep_shadow':1,'animal_body':2,'animal_highlights_and_marks':3},'sprite_alpha_index':0,'anatomy_parameters':{'portrait_pose':pose,'body_width':bw,'head_width':hw,'limb_reach':reach,'marking_plan':pattern,'fore_digits':4,'hind_digits':4 if family.startswith('slender') else 5,'costal_grooves':'visible symbolic folds, not diagnostic counts' if family!='newt' else 'no drawn costal grooves; grainy terrestrial skin','tail':'short strongly tapered' if family=='web' else 'base constricted' if family=='ensatina' else 'tapered representative adult tail'}}
        result[art]=m;x=(n%5)*150;y=(n//5)*88
        for f in range(2):sheet.paste(portrait(art,f).convert('RGB'),(x+f*51+2,y+3))
        sheet.paste(icon(art).convert('RGBA'),(x+110,y+22),icon(art).convert('RGBA'))
        label.text((x+2,y+54),f'{sid} '+record['canonical_scientific_name'].split()[0],fill=(24,32,24));label.text((x+2,y+68),record['canonical_scientific_name'].split()[1],fill=(24,32,24))
        a,b=portrait(art,0),portrait(art,1);i=icon(art)
        assert a.mode==b.mode==i.mode=='P' and a.size==b.size==(48,48) and i.size==(16,16)
        assert all(set(im.get_flattened_data())<=set(range(4)) for im in (a,b,i))
        assert all(all(v%8==0 for v in rgb) for rgb in palette)
        assert len(set(m['palette_rgb555']))==4
        changed=sum(v!=w for v,w in zip(a.get_flattened_data(),b.get_flattened_data()));assert changed>0,(art,'no motion')
        animal=sum(v!=0 for v in a.get_flattened_data());assert animal>=150,(art,'empty drawing')
        # Indexed and silhouette hashes distinguish recolors from actual geometry.
        indexed=hashlib.sha256(bytes(a.get_flattened_data())).hexdigest();silhouette=hashlib.sha256(bytes(int(v!=0) for v in a.get_flattened_data())).hexdigest()
        tiles={tuple(a.crop((x,y,x+8,y+8)).get_flattened_data()) for y in range(0,48,8) for x in range(0,48,8)}
        validation.append({'art_id':art,'species_id':sid,'changed_pixels':changed,'animal_pixels':animal,'unique_tiles_frame0':len(tiles),'indexed_sha256':indexed,'silhouette_sha256':silhouette,'sha256':hashlib.sha256((out/frames[0]).read_bytes()).hexdigest()})
    assert len({v['indexed_sha256'] for v in validation})==len(PROFILES),'duplicate indexed drawing'
    (out/'species-wave3-salamanders-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'species-wave3-salamanders-validation.json').write_text(json.dumps({'source_only':True,'native_observed':False,'count':len(result),'unique_indexed_portraits':len({v['indexed_sha256'] for v in validation}),'unique_silhouettes':len({v['silhouette_sha256'] for v in validation}),'records':validation},indent=2)+'\n')
    sheet.save(out/'species-wave3-salamanders-contact-sheet.png');sheet.resize((1500,1408),Image.Resampling.NEAREST).save(out/'species-wave3-salamanders-contact-sheet_2x.png')
    motion=[]
    for f in range(2):
        page=Image.new('RGB',(5*56,8*56),(184,200,176))
        for n,p in enumerate(PROFILES):page.paste(portrait(p[1],f).convert('RGB'),((n%5)*56+4,(n//5)*56+4))
        motion.append(page.resize((560,896),Image.Resampling.NEAREST))
    motion[0].save(out/'species-wave3-salamanders-motion.gif',save_all=True,append_images=motion[1:],duration=600,loop=0)
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('output_dir');args=parser.parse_args();emit_species_wave3_salamanders(args.output_dir)
