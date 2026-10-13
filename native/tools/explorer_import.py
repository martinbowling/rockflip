"""Append authored named actions to the registered explorer without replacing IDs.
Run after generate.py's existing nine-frame stride import. No compiled frame IDs.
"""
from pathlib import Path
from PIL import Image
import json,uuid,hashlib

def emit_explorer_actions(root):
 root=Path(root);art=root/'art/out';registered=root/'native/assets/sprites/ranger_deluxe.png'
 if not registered.exists():raise RuntimeError('Register the deluxe explorer before adding actions')
 sidecar=Path(str(registered)+'.gbsres');meta=json.loads(sidecar.read_text())
 names=json.loads((art/'player-actions.json').read_text())['order'];source=Image.open(art/'player_actions.png')
 old=Image.open(registered).crop((0,0,144,32));out=Image.new('RGB',(432,32),(101,255,0));out.paste(old,(0,0))
 shades=[(101,255,0),(7,24,33),(134,192,108),(224,248,207)]
 uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'rockflip/explorer/action/'+s))
 # Preserve every existing default resource/state/animation/frame/tile ID.
 meta['states']=[s for s in meta['states']if s['name'] not in ('explorer_peek','explorer_lift','explorer_camera')]
 for an,action in enumerate(('peek','lift','camera')):
  animations=[]
  for slot,direction in enumerate(('right','left','up','down','right','left','up','down')):
   fs=[];draw_direction='right' if direction=='left' else direction
   for phase in range(2):
    frame=9+an*6+('right','up','down').index(draw_direction)*2+phase;k=names.index(f'{action}_{draw_direction}_{phase}')
    for y in range(24):
     for x in range(16):out.putpixel((frame*16+x,y),shades[source.getpixel((k*16+x,y))])
    ts=[{'id':uid(f'{action}/{slot}/{phase}/{x}/{sy}'),'x':x,'y':16 if sy==0 else 0,'sliceX':frame*16+x,'sliceY':sy,'flipX':False,'flipY':False,'palette':0,'paletteIndex':0,'objPalette':'OBP0','priority':False}for sy in (0,16)for x in (0,8)]
    fs.append({'id':uid(f'{action}/{slot}/{phase}'),'tiles':ts})
   animations.append({'id':uid(f'{action}/{slot}'),'frames':fs})
  meta['states'].append({'id':uid(action),'name':'explorer_'+action,'animationType':'multi_movement','flipLeft':True,'animations':animations})
 out.save(registered);meta.update(width=432,height=32,canvasHeight=32,spriteMode='8x16',checksum=hashlib.sha1(registered.read_bytes()).hexdigest())
 meta['numTiles']=len({out.crop((f*16+x,y,f*16+x+8,y+16)).tobytes()for f in range(27)for x in (0,8)for y in (0,16)})
 sidecar.write_text(json.dumps(meta,indent=2)+'\n')
