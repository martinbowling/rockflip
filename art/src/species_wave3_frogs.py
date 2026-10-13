"""Nine remaining original Anura portraits: exact native pixels, no traced art.

Editable icons are literal16x16 grids. Independent48x48 anatomy plans below
use hand-placed silhouettes, skin, eyes and foot rays, never icon enlargement.
Two frames show quiet breathing/head/foot settling; no induced defensive pose.
Source-only until independent anatomy, native composition and motion review.
"""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SELECTION=[
(22,'arroyo_toad','arroyo',[(224,216,176),(40,40,24),(128,128,88),(216,200,128)]),
(23,'yosemite_toad','yosemite_female',[(184,208,176),(32,40,24),(136,128,88),(224,216,160)]),
(109,'northern_red_legged','aurora',[(184,208,192),(40,32,24),(152,120,80),(192,96,72)]),
(110,'foothill_yellow_legged','boylii',[(176,208,208),(40,40,32),(128,136,104),(216,192,104)]),
(111,'cascades_frog','cascadae',[(184,208,192),(32,40,24),(128,128,72),(208,192,128)]),
(112,'california_red_legged','draytonii',[(184,208,184),(48,32,24),(152,112,64),(200,96,64)]),
(113,'southern_yellow_legged','muscosa',[(184,208,208),(40,40,32),(136,120,72),(224,192,96)]),
(118,'couch_spadefoot','couchii',[(232,216,160),(40,40,24),(152,152,72),(224,208,112)]),
(124,'western_spadefoot','hammondii',[(216,208,160),(40,40,24),(136,136,88),(216,192,112)]),
]
BY_NAME={a:(sid,kind,pal) for sid,a,kind,pal in SELECTION}
SOURCES={
'arroyo_toad':['https://www.fws.gov/species/arroyo-toad-anaxyrus-californicus'],
'yosemite_toad':['https://www.nps.gov/articles/000/yosemitetoad.htm','https://www.fws.gov/policy/library/2013/2013-09600.pdf'],
'northern_red_legged':['https://nas.er.usgs.gov/queries/factsheet.aspx?SpeciesID=68','https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/northern-red-legged-frog-2015.html'],
'foothill_yellow_legged':['https://www.fws.gov/species/foothill-yellow-legged-frog-rana-boylii','https://www.fs.usda.gov/psw/publications/documents/psw_gtr248/psw_gtr248.pdf'],
'cascades_frog':['https://home.nps.gov/mora/learn/nature/amphibians.htm'],
'california_red_legged':['https://www.nps.gov/yose/learn/nature/caredfrog.htm'],
'southern_yellow_legged':['https://www.fws.gov/species/mountain-yellow-legged-frog-rana-muscosa'],
'couch_spadefoot':['https://escholarship.org/content/qt79s5p5f8/supp/IB_104_Lab_Manual_2021.pdf'],
'western_spadefoot':['https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=190378'],
}
NOTES={
'arroyo_toad':'Adult stocky warty toad, blunt snout, pale eyelid V and parotoid/sacral blotches; no western-toad mid-dorsal stripe. Horizontal pupils, no enlarged treefrog toe discs.',
'yosemite_toad':'Adult female: cream-bordered dark patches and obvious warts. Adult males are more uniform olive/yellow-green; sex variation is not a guide slot. Horizontal pupils and paired parotoid glands.',
'northern_red_legged':'Adult smooth/slightly rugose slender ranid, dorsolateral folds, mask and lip edge, fine dark flecks. Red shown only on visible folded hindleg undersides, not bright red entire legs or iris. No inflated vocal sac.',
'foothill_yellow_legged':'Adult rough pebbly skin, pale snout triangle, indistinct dorsolateral folds, yellow visible hindleg undersides and fully webbed rear feet. Tiny expanded toe tips are not treefrog adhesive discs.',
'cascades_frog':'Adult brown/olive ranid with dark spots, prominent folds and long folded hindlegs. Tiny portrait cannot prove species identity against other ranids; final morphology review required.',
'california_red_legged':'Large adult ranid in a different lateral crouch from aurora, dark dorsal blotches and red visible lower hindleg/abdomen. No sex-specific throat sac animation; color varies naturally.',
'southern_yellow_legged':'Adult variable brown/yellow blotched mountain ranid; yellow is strongly represented on underside of folded rear limbs. Authored shoreline head/foreleg settling, never a defensive display.',
'couch_spadefoot':'Adult female-style reticulate markings, large bulging eyes with vertical pupils, no true-toad parotoid lumps, visible sickle-shaped black hindfoot spade. Adult sex pattern varies; not a counted variant.',
'western_spadefoot':'Adult squat comparatively smooth spadefoot, short limbs and vertical pupils; visible compact black hindfoot spade, no large parotoid glands and no treefrog discs.',
}
# Independently drawn16px guide icons, not scaled portraits. 0 is transparent.
ICONS={
'arroyo_toad': ['0000000000000000','0000110000110000','0001331001331000','0001321111321000','0001233233210000','0001221222210000','0012212222121000','0122212122222100','0122122221222100','0111221222111100','0011122222111000','0112111111121100','0121100000112100','0111100000111100','0000000000000000','0000000000000000'],
'yosemite_toad':['0000000000000000','0000111100000000','0011333111000000','0013232322100000','0012322222210000','0001221332211000','0011223113322100','0122221322322210','0121332221332210','0112332122312110','0001221332211100','0000112222111000','0011121112111000','0122110001221100','0111100000111100','0000000000000000'],
'northern_red_legged':['0000000000000000','0000000011100000','0000000122211000','0000001232112100','0000001222222100','0000011222211000','0000122122221100','0011222212222210','0122212222212110','0122112212211000','0013311222211000','0011333111112100','0111113310012110','0122101110000110','0111100000000000','0000000000000000'],
'foothill_yellow_legged':['0000000000000000','0000000111000000','0000011322110000','0000112333211000','0001222212221000','0001222122211000','0000112222210000','0011221222111000','0122222122222100','0121132221122100','0013332223331100','0011233111221100','0111133000331110','0122110000012210','0111100000001110','0000000000000000'],
'cascades_frog':['0000000000000000','0000011000011000','0000133100133100','0000122111122100','0001222122212100','0001222221221100','0000122212221000','0001121222121100','0012222122222210','0122122221222210','0111221332211110','0001112222111000','0012221112211100','0122110001122110','0111100000111100','0000000000000000'],
'california_red_legged':['0000000000000000','0000000001111000','0000000012321100','0000000122122210','0000011122212100','0000122221221100','0001222122221100','0012222222212100','0122122212222100','0122211221222100','0013331222111100','0011333311112100','0111113310012210','0122211100001110','0111110000000000','0000000000000000'],
'southern_yellow_legged':['0000000000000000','0000001110000000','0000013231100000','0000122113210000','0001222322210000','0001221232210000','0000122222100000','0011122221110000','0122213232221000','0122122212222100','0013332221332100','0001133311211100','0011213310012110','0122111000001110','0111100000000000','0000000000000000'],
'couch_spadefoot':['0000000000000000','0000110000110000','0001331001331000','0001313113131000','0001323113231000','0001232223210000','0012221122221000','0122112211222100','0121222212212100','0122211221222100','0012212212221000','0011112221111000','0112111111121100','0121100000112100','0110000000001100','0000000000000000'],
'western_spadefoot':['0000000000000000','0000011000110000','0000133101331000','0000131313131000','0000123332221000','0001222222221000','0001221121221000','0012222222221100','0122221122222100','0122112221122100','0111222222111100','0001112221110000','0011211111211000','0121100000112100','0110000000000110','0000000000000000'],
}
class Pen:
 def __init__(self,im):self.im=im;self.d=ImageDraw.Draw(im)
 def line(self,pts,c=1,w=1):self.d.line(pts,fill=c,width=w)
 def poly(self,pts,c=2):self.d.polygon(pts,fill=c,outline=1)
 def oval(self,box,c=2):self.d.ellipse(box,fill=c,outline=1)
 def dot(self,x,y,c=1):self.d.point((x,y),fill=c)
 def eye(self,x,y,vertical=False,blink=False,iris=3):
  self.oval((x-3,y-3,x+3,y+3),iris)
  if blink:self.line([(x-2,y+1),(x+2,y+1)],1)
  elif vertical:self.line([(x,y-2),(x,y+2)],1,2)
  else:self.line([(x-2,y),(x+2,y)],1,2)
 def toes(self,base,rays,web=False,c=2):
  if web:self.poly([base]+rays,c)
  for end in rays:self.line([base,end],1)
 def specks(self,pts,wart=False):
  for x,y in pts:
   if wart:self.oval((x,y,x+2,y+2),2);self.dot(x+1,y,3)
   else:self.dot(x,y,1);self.dot(x+1,y,1)
def canvas(art,size=(48,48),transparent=False):
 im=Image.new('P',size,0);pal=BY_NAME[art][2];im.putpalette([v for rgb in pal for v in rgb]+[0]*756)
 if transparent:im.info['transparency']=0
 return im

def portrait(art,frame=0):
 im=canvas(art);p=Pen(im);_,kind,_=BY_NAME[art]
 if kind=='arroyo':
  # Low, compact frontal stocky toad. Short legs and bumps, not ranid haunches.
  p.poly([(13,26),(7,28),(5,35),(10,39),(17,34)]);p.poly([(33,26),(39,29),(42,35),(37,40),(29,34)])
  p.toes((8,37),[(3,40),(5,42),(7,43),(10,42),(12,40)]);p.toes((39,37),[(36,42),(39,43),(42,42),(44,40),(45,38)])
  p.oval((11,16-frame,36,37));p.oval((12,11,36,25))
  p.oval((11,19,17,26),2);p.oval((31,19,37,26),2)
  p.line([(13,19),(16,18)],3,2);p.line([(32,18),(35,19)],3,2)
  p.eye(17,14,blink=bool(frame));p.eye(31,14,blink=bool(frame))
  p.line([(13,11),(18,10),(24,15),(30,10),(35,11)],3)
  p.line([(16,24),(24,26+frame),(32,24)],1)
  p.poly([(16,27),(13,35),(10+frame,37),(14+frame,38),(18,32)]);p.poly([(31,27),(35,34),(38,37),(33,39),(29,32)])
  p.toes((12+frame,37),[(10+frame,40),(12+frame,41),(14+frame,41),(16+frame,40)])
  p.specks([(16,28),(22,28),(27,29),(30,33),(20,34),(14,31),(26,21),(22,20)],True)
  p.line([(17,30),(20,31)],3);p.line([(29,30),(31,31)],3)
 elif kind=='yosemite_female':
  # Three-quarter female, broader right haunch; oval glands and cream-edged patches.
  p.poly([(13,28),(7,29),(5,37),(11,41),(18,36)]);p.poly([(32,24),(41,28),(43,38),(37,42),(29,35)])
  p.toes((9,38),[(3,41),(5,43),(8,44),(11,43),(13,41)]);p.toes((39,38),[(35,43),(38,44),(41,43),(44,41),(46,39)])
  p.oval((12,14-frame,36,36));p.oval((10,9,32,24));p.oval((9,18,16,26));p.oval((29,15,36,22))
  p.eye(14,11,blink=bool(frame));p.eye(27,11,blink=bool(frame))
  p.line([(14,24),(23,25),(30,22)],1)
  for box in [(17,26,22,31),(25,27,31,32),(18,16,23,20),(29,31,33,35),(13,29,16,32)]:
   p.oval(box,3);x,y,r,b=box;p.oval((x+1,y+1,r-1,b-1),1)
  p.poly([(15,26),(14,34),(10,37),(15,39),(19,32)]);p.poly([(29,25),(31,33+frame),(35,36+frame),(30,38+frame),(26,31)])
  p.toes((12,37),[(8,40),(11,42),(14,41),(17,40)]);p.toes((33,36+frame),[(31,40),(34,41),(37,39),(39,38)])
  p.specks([(23,23),(28,20),(34,27),(18,23),(9,33),(39,34)],True)
 elif kind=='aurora':
  # Slender low lateral ranid with long folded hindlimb and restrained fine flecks.
  p.poly([(12,27),(5,30),(4,36),(10,39),(21,35)]);p.poly([(25,26),(34,29),(35,36),(30,39),(21,34)])
  p.poly([(6,34),(12,33),(20,36),(17,39),(8,38)],3)
  p.toes((8,37),[(1,40),(2,42),(5,44),(9,43),(13,41)],True,2)
  p.oval((10,16-frame,30,33));p.poly([(24,13),(31,9),(40,11),(44,17),(39,22),(28,24)])
  p.line([(29,17),(37,19),(42,17)],1,2);p.line([(27,22),(37,22),(41,20)],2)
  p.eye(35,11,blink=bool(frame),iris=2)
  p.line([(14,18),(20,16),(26,16)],2,2);p.line([(13,20),(16,27),(22,30)],1)
  p.poly([(30,24),(34,29),(36,35),(41,36),(38,38),(32,34),(27,26)])
  p.toes((39,36),[(40,40),(42,41),(44,40),(46,38)])
  p.specks([(16,21),(20,23),(24,25),(17,27),(23,19),(29,15)])
  p.line([(6,32),(10,33),(12,36)],1);p.line([(27,31),(30,32)],1)
 elif kind=='boylii':
  # Broad frontal river frog, pebbly texture and webbed spread hind feet.
  p.poly([(14,23),(6,25),(3,33),(6,38),(15,35)]);p.poly([(33,24),(40,28),(44,36),(39,40),(30,35)])
  p.toes((7,36),[(1,37),(2,41),(5,44),(9,43),(13,40)],True,3);p.toes((39,38),[(34,42),(38,44),(41,43),(45,41),(46,37)],True,3)
  p.oval((13,15-frame,35,35));p.poly([(12,19),(12,12),(17,8),(30,8),(36,14),(36,22),(26,26),(16,25)])
  p.eye(17,12,blink=bool(frame));p.eye(31,12,blink=bool(frame))
  p.poly([(20,13),(28,13),(24,20)],3);p.line([(16,24),(24,25+frame),(32,23)],1)
  p.poly([(18,25),(13,31),(12,36),(18,38),(21,32)]);p.poly([(29,24),(32,31),(35,35),(31,38),(27,31)])
  p.toes((15,36),[(11,39),(14,41),(17,40),(20,39)]);p.toes((33,36),[(30,40),(33,41),(36,40),(38,38)])
  p.specks([(16,18),(31,18),(21,23),(17,28),(25,29),(28,26),(24,33),(7,30),(39,32)],True)
 elif kind=='cascadae':
  # Upright narrow three-quarter meadow frog, defined folds, elongated knees.
  p.poly([(14,28),(7,32),(5,39),(13,41),(20,35)]);p.poly([(28,27),(37,28),(42,35),(39,39),(29,37)])
  p.toes((8,39),[(2,41),(5,44),(8,45),(12,43),(15,41)],True);p.toes((39,37),[(36,41),(39,43),(42,42),(45,40),(46,38)],True)
  p.oval((14,12-frame,31,34));p.poly([(12,15),(13,8),(20,5),(29,7),(34,13),(30,22),(19,23)])
  p.eye(17,9,blink=bool(frame));p.eye(29,10,blink=bool(frame))
  p.line([(14,18),(21,21),(29,19)],1);p.line([(15,21),(16,28),(19,32)],3);p.line([(29,22),(28,29),(26,33)],3)
  p.poly([(19,23),(15,30),(17,37),(21,38),(22,32)]);p.poly([(29,23),(32,29+frame),(33,36+frame),(38,37+frame),(35,39+frame),(30,35)])
  p.toes((19,37),[(15,40),(18,42),(21,40),(23,39)]);p.toes((36,37+frame),[(35,41),(38,42),(40,40),(42,39)])
  for x,y in [(18,24),(23,25),(20,28),(26,28),(23,31),(25,15),(19,14),(10,34),(37,33)]:p.oval((x,y,x+2,y+2),1)
 elif kind=='draytonii':
  # Large broad lateral crouch; strong folded haunch and differently arranged arms.
  p.poly([(13,22),(5,24),(2,34),(8,39),(21,35)]);p.poly([(28,24),(37,27),(40,36),(35,39),(25,34)])
  p.poly([(4,33),(11,30),(21,34),(17,38),(7,37)],3)
  p.toes((7,37),[(1,38),(2,42),(5,44),(9,43),(13,40)],True,2)
  p.oval((9,13-frame,32,33));p.poly([(28,12),(34,7),(41,9),(46,16),(42,22),(31,24)])
  p.eye(37,10,blink=bool(frame),iris=2);p.line([(31,18),(40,20),(44,18)],1,2)
  p.line([(12,17),(17,14),(26,14)],2,2);p.line([(13,19),(17,25),(22,29)],1)
  p.poly([(31,24),(33,31),(39,35),(43,37),(39,39),(33,35),(28,27)])
  p.toes((40,37),[(41,41),(43,43),(45,41),(47,39)])
  for x,y in [(14,19),(19,18),(23,23),(17,26),(26,18),(30,16),(35,29),(7,27)]:p.oval((x,y,x+2,y+2),1)
  p.line([(4,29),(9,30),(12,33)],1);p.line([(27,29),(31,32)],1)
 elif kind=='muscosa':
  # Compact asymmetric mountain shoreline frog with full folded yellow rear-leg underside.
  p.poly([(14,25),(8,25),(4,31),(5,37),(15,37),(20,32)]);p.poly([(31,24),(37,25),(42,32),(39,39),(29,36)])
  p.poly([(6,33),(12,30),(20,32),(16,37),(8,37)],3);p.poly([(32,32),(38,30),(40,36),(34,38)],3)
  p.toes((7,36),[(1,39),(3,42),(6,44),(10,43),(14,40)],True,3);p.toes((38,37),[(34,42),(38,44),(41,43),(44,41),(46,38)],True,3)
  p.oval((13,13-frame,34,33));p.poly([(12,16),(15,8),(25,6),(34,12),(37,19),(30,25),(20,25)])
  p.eye(18,11,blink=bool(frame));p.eye(31,14,blink=bool(frame))
  p.line([(16,23),(24,25),(32,22)],1);p.line([(18,26),(20,31),(26,32)],3)
  p.poly([(19,26),(13,31),(16,37),(21,38),(23,32)]);p.poly([(30,25),(33,30),(37+frame,35),(34+frame,38),(30,34)])
  p.toes((18,37),[(14,40),(17,42),(20,41),(23,39)]);p.toes((35+frame,36),[(33+frame,40),(36+frame,41),(39+frame,40),(41+frame,38)])
  for x,y in [(20,16),(25,12),(29,18),(24,20),(18,20),(24,27),(28,30)]:p.oval((x,y,x+2,y+2),1)
  p.line([(17,15),(19,17)],3);p.line([(26,16),(29,16)],3)
 elif kind=='couchii':
  # Rounded high-eyed spadefoot, network markings and visible sickle pad.
  p.poly([(12,27),(6,29),(4,36),(10,40),(18,34)]);p.poly([(34,27),(40,30),(44,37),(36,42),(29,34)])
  p.toes((8,38),[(3,40),(5,43),(8,44),(11,43),(14,40)]);p.toes((39,39),[(34,43),(38,44),(42,43),(45,41),(46,38)])
  p.line([(5,40),(6,43),(9,43),(11,41)],1,3)
  p.oval((11,16-frame,37,37));p.oval((12,12,36,26));p.eye(17,11,True,bool(frame));p.eye(32,11,True,bool(frame))
  p.line([(16,24),(24,26+frame),(32,24)],1)
  p.line([(16,27),(19,30),(16,34),(21,35),(24,32),(29,34),(32,30),(28,27),(24,29),(20,26),(16,27)],1,2)
  p.line([(20,18),(22,21),(26,19),(29,22)],1);p.line([(12,29),(14,32)],3)
  p.poly([(17,27),(14,34),(13,38),(18,40),(21,33)]);p.poly([(31,26),(34,34),(39,37),(35,40),(29,33)])
  p.toes((16,38),[(12,42),(15,43),(18,42),(21,40)]);p.toes((36,38),[(33,42),(36,43),(39,42),(42,40)])
  p.specks([(21,23),(28,24),(24,36),(35,30),(9,32)])
 elif kind=='hammondii':
  # Low oval spadefoot with short crouched limbs and broad eye sockets.
  p.poly([(12,27),(6,28),(3,34),(8,38),(18,34)]);p.poly([(33,26),(39,27),(42,34),(38,39),(29,34)])
  p.toes((6,36),[(1,38),(3,41),(6,42),(10,40),(12,38)]);p.toes((39,37),[(35,41),(38,43),(41,41),(44,40),(46,37)])
  p.line([(3,39),(6,39),(7,41)],1,3)
  p.oval((11,16-frame,36,35));p.poly([(10,19),(13,10),(20,9),(29,8),(36,14),(37,21),(31,25),(18,26)])
  p.eye(17,12,True,bool(frame));p.eye(31,12,True,bool(frame));p.line([(15,24),(24,25+frame),(32,24)],1)
  p.line([(14,18),(20,16),(28,16),(33,18)],3)
  p.poly([(17,26),(13,31),(14,36),(18,38),(20,32)]);p.poly([(30,26),(32,31),(35,35),(31,38),(28,32)])
  p.toes((16,36),[(12,40),(15,41),(18,40),(21,38)]);p.toes((33,36),[(30,40),(33,41),(36,40),(39,38)])
  p.specks([(18,27),(25,28),(29,30),(23,22),(17,21),(33,19),(21,31)])
  p.line([(20,29),(24,30)],3)
 return im

def icon(art):
 im=canvas(art,(16,16),True);g=ICONS[art];assert len(g)==16 and all(len(row)==16 for row in g)
 for y,row in enumerate(g):
  for x,v in enumerate(row):im.putpixel((x,y),int(v))
 return im

def emit_species_wave3_frogs(output_dir):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);registry={r['species_id']:r for r in json.loads((ROOT/'data/production_roster.json').read_text())['records']};result={}
 sheet=Image.new('RGB',(3*158,3*86),(208,208,184));label=ImageDraw.Draw(sheet);motion=[];valid=[]
 for n,(sid,art,kind,palette) in enumerate(SELECTION):
  r=registry[sid];assert r['group']=='Amphibia';frames=[]
  for f in range(2):fn=f'portrait_{art}_idle{f}.png';portrait(art,f).save(out/fn);frames.append(fn)
  base=f'portrait_{art}.png';portrait(art).save(out/base);small=f'portrait32_{art}.png';portrait(art).resize((32,32),Image.Resampling.NEAREST).save(out/small)
  ico=f'critter_{art}.png';icon(art).save(out/ico);anim=canvas(art,(96,48));anim.paste(portrait(art,0),(0,0));anim.paste(portrait(art,1),(48,0));an=f'portrait_{art}_animation.png';anim.save(out/an)
  meta={'art_id':art,'species_id':sid,'canonical_scientific_name':r['canonical_scientific_name'],'scientific_name_provisional':r['canonical_scientific_name'],'common_name':r['common_name'],'icon':ico,'portrait':base,'portrait32':small,'frames':frames,'animation_sheet':an,'dimensions':[48,48],'icon_dimensions':[16,16],'palette':palette,'palette_rgb555':[f'0x{((b>>3)<<10)|((g>>3)<<5)|(r>>3):04X}' for r,g,b in palette],'frame_duration_ticks':36,'behavior_animation':'quiet_breath_blink' if kind not in ('arroyo','muscosa') else 'quiet_foreleg_settle','status':'art_only_pending_independent_anatomy_and_native_review','taxon_count_approval':False,'anatomy_plan':kind,'allowed_districts_from_roster':[p['region_id'] for p in r['region_permissions']],'anatomy_sources':SOURCES[art],'review_notes':[NOTES[art],'Original source art only; no photo tracing or external image import.','Exact frame timing is an authored game abstraction; calm motion is never a provoked defensive reward.','Final anatomical identification, native camera/guide readability and human acceptance remain pending.']}
  result[art]=meta;x=(n%3)*158;y=(n//3)*86
  for f in range(2):sheet.paste(portrait(art,f).convert('RGB'),(x+f*50+3,y+3))
  sheet.paste(icon(art).convert('RGBA'),(x+110,y+18),icon(art).convert('RGBA'));label.text((x+3,y+55),f'{sid}: '+art[:20],fill=(32,32,32));label.text((x+3,y+69),r['canonical_scientific_name'],fill=(32,32,32))
  a,b=portrait(art,0),portrait(art,1);i=icon(art);changed=sum(x!=y for x,y in zip(a.getdata(),b.getdata()));assert changed>0
  for im in [a,b,i]:assert im.mode=='P' and set(im.getdata())<=set(range(4))
  assert a.size==b.size==(48,48) and i.size==(16,16);assert all(all(c%8==0 and 0<=c<=248 for c in rgb) for rgb in palette)
  unique=len({tuple(a.crop((tx,ty,tx+8,ty+8)).getdata()) for ty in range(0,48,8) for tx in range(0,48,8)})
  valid.append({'species_id':sid,'art_id':art,'canonical_scientific_name':r['canonical_scientific_name'],'changed_pixels':changed,'unique_tiles_frame0':unique,'sha256':hashlib.sha256((out/base).read_bytes()).hexdigest(),'icon_sha256':hashlib.sha256((out/ico).read_bytes()).hexdigest()})
 assert len({v['sha256'] for v in valid})==9 and len({v['icon_sha256'] for v in valid})==9
 for f in range(2):
  page=Image.new('RGB',(3*56,3*56),(208,208,184))
  for n,(_,art,_,_) in enumerate(SELECTION):page.paste(portrait(art,f).convert('RGB'),((n%3)*56+4,(n//3)*56+4))
  motion.append(page.resize((504,504),Image.Resampling.NEAREST))
 motion[0].save(out/'species-wave3-frogs-motion.gif',save_all=True,append_images=motion[1:],duration=600,loop=0)
 sheet.resize((948,516),Image.Resampling.NEAREST).save(out/'species-wave3-frogs-contact-sheet_2x.png')
 (out/'species-wave3-frogs-manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/'species-wave3-frogs-validation.json').write_text(json.dumps({'source_only':True,'native_observed':False,'count':len(result),'records':valid},indent=2)+'\n')
 return result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('output_dir');args=p.parse_args();emit_species_wave3_frogs(args.output_dir)
