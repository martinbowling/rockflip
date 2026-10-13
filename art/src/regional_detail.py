"""Original staged regional16px art. Collision/water identity preserved."""
from PIL import Image,ImageDraw
STYLES={'D01':'desert_shrub','D02':'palm','D03':'sage','D04':'oak','D05':'conifer','D06':'willow','D07':'bunchgrass','D08':'reeds','D09':'coast_scrub','D10':'chaparral','D11':'pine','D12':'island_scrub','D13':'redwood','D14':'fern','D15':'fir','D16':'sage'}
def vegetation(style):
 im=Image.new('P',(16,16),0);d=ImageDraw.Draw(im)
 if style in ('conifer','pine','fir'):
  d.line((8,3,8,15),fill=3,width=2)
  for y,w in ((1,2),(4,4),(7,6)):
   d.polygon([(8,y),(8-w,y+5),(8+w,y+5)],fill=2,outline=3);d.line([(8,y+1),(8-w+2,y+4)],fill=1)
  d.point((7,14),fill=1)
 elif style=='redwood':
  d.polygon([(6,0),(9,0),(10,12),(13,15),(2,15),(5,11)],fill=2,outline=3)
  d.line([(6,2),(6,12),(4,14)],fill=1);d.line([(8,0),(8,13),(10,15)],fill=3)
  for x,y in [(0,2),(10,1),(0,7),(11,6)]:
   d.line([(x,y+3),(x+4,y)],fill=3);d.line([(x+1,y+2),(x+4,y+1)],fill=1)
 elif style=='fern':
  for top in ((1,3),(8,0),(14,3)):
   d.line([(8,15),top],fill=3)
   for t in (3,6,9):
    x=8+(top[0]-8)*t//12;y=15+(top[1]-15)*t//12
    d.line([(x-3,y-2),(x,y),(x+3,y-2)],fill=2);d.point((x-2,y-2),fill=1)
 elif style in ('reeds','bunchgrass'):
  for x,y in ((2,4),(5,1),(8,5),(11,2),(14,6)):
   d.line([(x,15),(x-1,y)],fill=3);d.line([(x,12),(x+1,y+4)],fill=1)
   if style=='reeds':d.rectangle((x-2,y,x,y+3),fill=2);d.point((x-1,y),fill=1)
   else:d.line([(x,14),(x+2,y+4)],fill=2)
 elif style=='palm':
  d.line([(7,14),(9,5)],fill=3,width=2);d.point((7,12),fill=1)
  for p in [(1,2),(2,6),(4,0),(13,0),(15,4),(14,8)]:
   d.line([(9,4),p],fill=2,width=2);d.line([(9,3),p],fill=1)
 elif style=='juniper':
  for box in ((1,4,7,10),(7,2,13,8),(9,7,15,12)):d.ellipse(box,fill=2,outline=3)
  d.line([(7,15),(9,9),(5,6)],fill=3,width=2);d.line([(7,13),(8,10)],fill=1)
  d.point((3,6),fill=1);d.line([(9,3),(11,3)],fill=1)
 elif style in ('oak','willow'):
  if style=='oak':
   for box in ((1,3,8,10),(6,0,13,8),(8,4,15,11)):d.ellipse(box,fill=2,outline=3)
   d.line([(6,3),(9,2)],fill=1);d.line([(2,6),(5,5)],fill=1)
  else:
   for x in (2,5,8,11,14):d.line([(8,2),(x,5),(x-1,12)],fill=2,width=2);d.point((x,6),fill=1)
  d.line([(8,15),(8,8),(4,6)],fill=3,width=2);d.line([(8,11),(12,8)],fill=3)
 else:
  # Separate low shrub crowns and exposed branching, not an evergreen trident.
  profiles={'desert_shrub':[(2,8,6,12),(5,3,10,8),(10,7,14,11)],'sage':[(1,9,6,12),(3,5,8,9),(8,6,14,11)],'coast_scrub':[(0,8,7,13),(4,4,12,11),(9,7,15,13)],'chaparral':[(1,4,8,12),(6,1,13,9),(9,7,15,13)],'island_scrub':[(0,9,8,13),(5,4,11,11),(11,8,15,12)]}
  for box in profiles[style]:d.ellipse(box,fill=2,outline=3);d.line([(box[0]+2,box[1]+1),(box[2]-2,box[1]+1)],fill=1)
  d.line([(8,15),(8,9),(4,9)],fill=3);d.line([(8,12),(12,10)],fill=3)
 return [ ''.join(str(im.getpixel((x,y))) for x in range(16)) for y in range(16)]
def geology(district):
 im=Image.new('P',(16,16),0);d=ImageDraw.Draw(im)
 d.polygon([(0,12),(2,6),(6,2),(10,1),(13,4),(15,9),(14,13),(8,15),(3,14)],fill=2,outline=3)
 d.polygon([(3,6),(6,3),(9,3),(11,6),(7,7),(5,10)],fill=1)
 if district in ('D15','D16'):
  d.line([(10,4),(9,8),(11,12)],fill=3);d.line([(4,8),(3,12)],fill=3);d.point((12,8),fill=1)
 elif district in ('D05','D11'):
  d.line([(9,3),(8,7),(11,12)],fill=3);d.line([(3,11),(6,12)],fill=1)
 elif district=='D14':
  d.line([(7,4),(6,9),(9,13)],fill=3);d.line([(11,6),(13,9)],fill=1)
 else:
  d.line([(9,4),(8,9),(11,12)],fill=3);d.point((3,11),fill=1)
 return [''.join(str(im.getpixel((x,y))) for x in range(16)) for y in range(16)]

def terrain_tile(rid,kind,context,c,x,y):
    if c not in 'CGS':return None
    habitat=' '.join((context or {}).get('habitat_ids',[]));sub=(context or {}).get('subarea_id','')
    forest=any(k in habitat for k in ('forest','conifer','woodland','redwood','moist_leaf_litter','island_moist_cover'))
    wet=any(k in habitat for k in ('wetland','marsh','freshwater','pool','stream','creek'))
    rocky=any(k in habitat for k in ('talus','rock_outcrop','lava','limestone'))
    if c=='G':
        if rid=='D02' and 'PALM' in (context or {}).get('name','') and (x+y)%3==0:return vegetation('palm'),1
        if rid=='D03' and 'JUNIPER' in (context or {}).get('name','') and (x+y)%3==0:return vegetation('juniper'),1
        if forest and not rocky:
            row=(context or {}).get('terrain',[''])[y];start=x
            while start>0 and row[start-1]=='G':start-=1
            part=(x-start)%2;left=x-part
            if left+1<len(row) and row[left+1]=='G':return canopy('oak' if rid in ('D04','D09','D10','D12') else 'redwood' if rid=='D13' else 'conifer',part),1
        if forest and 'limestone' not in habitat and (not rocky or (x+y)%3==0):
            return vegetation('redwood' if rid=='D13' else 'oak' if rid in ('D04','D09','D10','D12') else 'fir' if rid=='D15' else 'conifer'),1
        return geology(rid),2
    if c=='C':
        style=STYLES[rid]
        if style in ('redwood','conifer','pine','fir','oak','willow','palm'):style='fern' if forest else 'reeds' if wet else 'chaparral' if rid in ('D04','D11') else 'bunchgrass' if rid=='D05' else 'desert_shrub' if rid=='D02' else 'sage'
        return vegetation(style),1
    # Lowground language remains fully passable. Four8px-compatible finite grids.
    style='litter' if forest else 'silt' if wet else 'scree' if rocky else 'grass' if rid in ('D06','D07','D08') else 'sand'
    return ground(style,(x+y*3)%3),0

def canopy(style,part):
    # Acomplete32x16 crown/groundedtrunk uses TWOactualG blockers, neverC.
    im=Image.new('P',(32,16),0);d=ImageDraw.Draw(im)
    if style=='conifer':
        # Pointed independent needle sprays, open sky between branch tiers.
        # The paired32x16 blocker crown must still read as conifer at1x.
        d.line([(15,2),(15,12)],fill=3,width=2)
        sprays=(
            [(15,0),(11,5),(14,4),(12,7),(18,7),(17,4),(19,5)],
            [(10,4),(7,6),(9,6),(3,10),(6,10),(1,13),(11,11),(14,7)],
            [(18,5),(21,7),(20,7),(28,10),(26,10),(31,13),(21,12),(17,8)],
            [(13,9),(8,11),(10,11),(4,14),(11,13),(15,11)],
            [(17,9),(22,11),(20,11),(28,14),(20,13),(16,11)])
        for points in sprays:d.polygon(points,fill=2,outline=3)
        d.line([(14,2),(12,5)],fill=1)
        d.line([(10,6),(7,8),(4,10)],fill=1)
        d.line([(13,10),(9,12)],fill=1)
        d.line([(20,8),(24,10)],fill=1)
        d.line([(19,12),(23,13)],fill=2)
        for x,y in ((8,9),(11,8),(21,10),(24,11)):d.point((x,y),fill=0)
    else:
        for box in ((0,3,13,11),(7,0,23,10),(18,3,31,12)):d.ellipse(box,fill=2,outline=3)
        d.line([(7,3),(12,2),(18,2)],fill=1);d.line([(2,6),(6,5)],fill=1);d.line([(23,6),(28,7)],fill=1)
    d.rectangle((13,9,18,15),fill=3);d.line([(14,10),(14,15)],fill=1)
    if style=='redwood':d.line([(16,10),(16,15)],fill=2)
    im=im.crop((part*16,0,part*16+16,16))
    return [''.join(str(im.getpixel((x,y))) for x in range(16)) for y in range(16)]

def ground(style,variant):
    im=Image.new('P',(16,16),0);d=ImageDraw.Draw(im)
    offset=[(0,0),(3,1),(-1,2)][variant]
    # Authored sparse arrangements keepwalking surfaces quiet; notID noise.
    if style=='litter':
        for x,y in ((2+offset[0],3+offset[1]),(10,10)):
            d.polygon([(x,y),(x+2,y-1),(x+4,y+1),(x+2,y+2)],fill=2);d.line([(x+1,y),(x+3,y+1)],fill=1)
        if variant==1:d.line([(11,2),(12,5),(13,3)],fill=3)
    elif style=='silt':
        for x,y in ((1+offset[0],4+offset[1]),(10,11)):d.line([(x,y),(x+3,y)],fill=1)
        if variant==2:d.line([(12,3),(14,3)],fill=2)
        d.point((6,13),fill=1)
    elif style=='scree':
        for x,y in ((2+offset[0],2+offset[1]),(10,10)):d.polygon([(x,y+2),(x+2,y),(x+4,y+2)],fill=1);d.point((x+1,y+2),fill=2)
    elif style=='grass':
        for x,y in ((2+offset[0],4+offset[1]),(10,12)):d.line([(x,y),(x-1,y-2)],fill=2);d.line([(x,y),(x+1,y-2)],fill=1)
    else:
        for x,y in ((1+offset[0],3+offset[1]),(9,11)):d.line([(x,y),(x+2,y)],fill=1)
        if variant==2:d.point((12,13),fill=2)
        d.point((6,7),fill=1)
    return [''.join(str(im.getpixel((x,y))) for x in range(16)) for y in range(16)]

# Organic landmark revisions, authored on the existing native grids.
# Zero stays transparent to the existing blocked-cell ground; no collision edits.
def organic_primary(rid,kind):
    if kind not in ('coast','island','forest','alpine','volcanic'):return None
    im=Image.new('P',(32,48),0);d=ImageDraw.Draw(im)
    if kind in ('coast','island'):
        # Wind-pruned canopy with exposed forks, uneven lobes and foliage gaps.
        d.line([(16,45),(14,32),(17,22),(13,14)],fill=3,width=4)
        d.line([(14,33),(7,23),(4,17)],fill=3,width=3)
        d.line([(16,29),(25,22),(28,15)],fill=3,width=3)
        d.line([(15,43),(13,32),(16,24)],fill=1)
        crowns={'D09':((0,13,11,23),(5,5,18,17),(13,2,25,14),(21,10,31,21),(10,17,23,26)),
                'D10':((1,7,13,18),(8,1,22,13),(18,6,31,17),(4,17,17,27),(15,15,29,25)),
                'D12':((0,14,13,25),(5,8,18,20),(12,11,26,22),(22,15,31,25),(9,21,22,29))}
        for box in crowns.get(rid,crowns['D09']):
            d.ellipse(box,fill=2,outline=3)
            x,y,xx,yy=box;d.line([(x+3,y+2),(x+5,y+1),(xx-3,y+3)],fill=1)
            d.line([(x+2,yy-3),(x+4,yy-2)],fill=3)
        # Irregular foliage edges and open sky between actual branches.
        for x,y in ((3,14),(8,6),(16,3),(23,5),(28,11),(8,21),(22,23)):d.point((x,y),fill=0)
        d.line([(9,24),(14,27),(19,24)],fill=3)
        if rid=='D12':
            d.line([(18,28),(23,31),(28,32)],fill=3,width=2)
            d.line([(14,35),(8,37)],fill=3)
        elif rid=='D10':d.line([(14,27),(10,15)],fill=3,width=2)
        d.line([(11,35),(9,39),(6,43)],fill=3)
        d.line([(16,39),(21,43),(23,45)],fill=3)
    else:
        # Layered branch sprays with broken tips, not stacked triangle roofs.
        d.line([(16,4),(15,46)],fill=3,width=3);d.line([(15,28),(14,44)],fill=1)
        d.polygon([(16,0),(13,4),(15,4),(11,8),(16,7),(19,9),(18,5),(20,6)],fill=2,outline=3)
        for y,width in ((8,7),(15,11),(23,14),(31,15)):
            d.line([(16,y),(16-width,y+6)],fill=3,width=2)
            d.line([(16,y+1),(16+width-1,y+7)],fill=3,width=2)
            for side in (-1,1):
                for n in range(2,width,3):
                    x=16+side*n;yy=y+n//2
                    d.line([(x,yy),(x+side*2,yy+3)],fill=2,width=2)
                    d.line([(x,yy),(x-side,yy-2)],fill=2)
                    if side<0:d.point((x,yy),fill=1)
            d.line([(14,y+2),(18,y+3)],fill=2,width=2)
        d.line([(15,44),(11,46)],fill=3);d.line([(16,44),(20,46)],fill=3)
    return im

def organic_secondary(rid):
    if rid not in ('D01','D03','D05','D06','D08','D09','D11','D12','D15','D16'):return None
    im=Image.new('P',(32,32),0);d=ImageDraw.Draw(im)
    if rid in ('D06','D08'):
        # Exposed willow roots and water-worn stones replace fence-like bars.
        d.line([(17,0),(16,10),(18,20),(16,27)],fill=3,width=4)
        d.line([(15,2),(15,10),(17,19)],fill=1)
        for path in ([(17,14),(8,19),(3,25)],[(17,20),(23,23),(29,29)],[(16,25),(11,29),(8,31)]):d.line(path,fill=3,width=2)
        for box in ((0,23,9,30),(21,25,31,31),(4,15,12,21)):
            d.ellipse(box,fill=2,outline=3);d.arc(box,190,285,fill=1)
        d.line([(7,10),(6,5),(4,3)],fill=2);d.line([(7,10),(10,6),(11,2)],fill=2)
    elif rid in ('D09','D12'):
        # Several rounded, separated shore rocks; no continuous retaining wall.
        for pts in ([(0,28),(2,21),(8,17),(13,22),(12,29)],[(11,26),(14,13),(21,11),(26,17),(27,27)],[(24,31),(24,24),(29,21),(31,25),(31,31)]):
            d.polygon(pts,fill=2,outline=3)
            a,b=pts[1],pts[2];d.line([(a[0]+1,a[1]+1),(b[0],b[1]+2)],fill=1)
        d.line([(18,14),(17,20),(20,24)],fill=3);d.point((5,25),fill=1)
    else:
        # Natural fractured rock faces: irregular silhouette, diagonal joints,
        # separated talus at the foot instead of continuous horizontal courses.
        d.polygon([(0,27),(2,16),(7,10),(12,12),(16,4),(22,2),(27,8),(30,14),(29,27),(23,30),(13,28),(6,30)],fill=2,outline=3)
        d.polygon([(3,17),(7,12),(11,14),(17,6),(21,4),(25,9),(19,10),(15,18),(9,20)],fill=1)
        d.line([(21,6),(18,13),(20,18),(16,23),(17,28)],fill=3)
        d.line([(7,14),(8,21),(4,26)],fill=3)
        d.line([(23,12),(25,18),(28,20)],fill=1)
        d.line([(11,23),(13,25),(11,28)],fill=1)
        for box in ((0,28,6,31),(23,28,30,31)):
            d.ellipse(box,fill=2,outline=3);d.point((box[0]+2,box[1]+1),fill=1)
        if rid=='D05':d.line([(15,6),(20,3),(24,7)],fill=0,width=2)
        if rid=='D15':
            d.line([(23,9),(22,17),(25,24)],fill=3)
            d.line([(12,15),(11,21)],fill=3)
    return im
