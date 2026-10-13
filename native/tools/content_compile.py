"""Compile stable game identities to independently banked native content bundles."""
import json
from pathlib import Path

STYLE={'desert':0,'regional':1}
BEHAVIORS={'protected':0,'freeze':1,'wedge':2,'glide':3,'hop':4,'push_up':5,'slow_walk':6,'dash_settle':7,'water_emerge':8,'night_peek':9,'natural_display':10,'rain_arrival':11}

def emit_content(root,out,art,pal,species,pixels,tilebytes,decl):
    include=out/'include';src=out/'src'
    manifest_path=art/'species-art-manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        for animal in species:
            entry=manifest[animal['art']]
            assert entry['species_id']==animal['id'] and entry['canonical_scientific_name']==animal['scientific_name'],'Canonical species/art identity mismatch'
            for frame in entry['frames']:assert (art/frame).is_file(), 'Missing authored motion frame'
    header=['#ifndef RF_CONTENT_H','#define RF_CONTENT_H','#include <gbdk/platform.h>',
            '#define RF_SPECIES_CAPACITY 192','#define RF_MAP_CAPACITY 400','#define RF_SPOT_CAPACITY 1000',
            '#define RF_SPECIES_COUNT '+str(len(species)),
            'typedef struct {UWORD id,west,east; UBYTE district,style,camp_x,camp_y,spot_count; UWORD spots[16]; char name[21],terrain[7][11];UWORD north,south;UBYTE north_x,south_x;} RFMap;',
            'typedef struct {UWORD id,room; UBYTE x,y,type,species,phases;} RFSpot;',
            'void rf_world_load(UWORD map,RFMap *out) BANKED;','void rf_world_spot(UWORD spot,RFSpot *out) BANKED;',
            'UBYTE rf_species_rule(UBYTE species,UBYTE field) BANKED;','UBYTE rf_world_transition(UWORD from,UWORD to) BANKED;','UWORD rf_world_trailhead(UBYTE district) BANKED;']
    wrappers=[]
    for start in range(0,len(species),4):
        group=species[start:start+4];n=start//4;prefix=f'rf_creature_{n:02d}'
        c='#pragma bank 255\n#include "rockflip_art.h"\n#include <gb/cgb.h>\n#include "palette.h"\n#include <string.h>\n'
        small=[];p32=[];p48=[];colors=[]
        for s in group:
            small+=tilebytes(pixels('critter_'+s['art']+'.png'))
            for frame in range(2):
                path=art/f"portrait_{s['art']}_idle{frame}.png"
                im=pixels(path.name) if path.exists() else pixels(f"portrait_{s['art']}.png")
                p48+=tilebytes(im)
                from PIL import Image
                path32=art/f"portrait32_{s['art']}_idle{frame}.png"
                p32+=tilebytes(pixels(path32.name) if path32.exists() else im.resize((32,32),Image.Resampling.NEAREST))
            colors += [int(x['rgb555'],16) for x in pal['obj'][pal['critter_palette_map'][s['art']]]]
        for name,data in [('icons',small),('p32',p32),('p48',p48)]:c+=decl(name,data)
        c+='static const UWORD colors[]={'+','.join(map(str,colors))+'};\n'
        c+='static const char names[][17]='+json.dumps([s['name'] for s in group]).replace('[','{').replace(']','}')+';\n'
        c+='static const char sci[][48]='+json.dumps([s['scientific_name'] for s in group]).replace('[','{').replace(']','}')+';\n'
        c+='static const char facts[][3][21]='+json.dumps([s['facts'] for s in group]).replace('[','{').replace(']','}')+';\n'
        c+=f'void {prefix}_portrait(UBYTE s,UBYTE scale,UBYTE frame) BANKED {{VBK_REG=1;if(scale==2)set_bkg_data(128,16,p32+((UWORD)s*2+(frame&1))*256);else set_bkg_data(128,36,p48+((UWORD)s*2+(frame&1))*576);VBK_REG=0;memcpy(((UWORD*)BkgPalette)+20,colors+s*4,8);set_bkg_palette(5,1,colors+s*4);}}\n'
        c+=f'void {prefix}_icon(UBYTE s,UBYTE hidden,UBYTE slot) BANKED {{UWORD colors4[4];UBYTE buf[64],i;memcpy(colors4,colors+s*4,8);colors4[0]=RGB(30,29,25);set_bkg_palette(slot,1,colors4);memcpy(buf,icons+(UWORD)s*64,64);if(hidden)for(i=0;i<64;i+=2)buf[i]=buf[i+1]=buf[i]|buf[i+1];VBK_REG=1;set_bkg_data(64+slot*4,4,buf);VBK_REG=0;}}\n'
        c+=f'void {prefix}_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED {{if(kind==0)strcpy(out,names[s]);else if(kind==1)strcpy(out,facts[s][line]);else strcpy(out,sci[s]);}}\n'
        (src/(prefix+'.c')).write_text(c)
        wrappers += [f'void {prefix}_portrait(UBYTE s,UBYTE scale,UBYTE frame) BANKED;',f'void {prefix}_icon(UBYTE s,UBYTE hidden,UBYTE slot) BANKED;',f'void {prefix}_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED;']
    count=(len(species)+3)//4
    wrappers.append('void rf_art_portrait_frame(UBYTE s,UBYTE scale,UBYTE frame) BANKED {switch(s/4){'+''.join(f'case {n}:rf_creature_{n:02d}_portrait(s%4,scale,frame);break;' for n in range(count))+'}}')
    wrappers.append('void rf_art_portrait(UBYTE s,UBYTE scale) BANKED {rf_art_portrait_frame(s,scale,0);}')
    wrappers.append('void rf_art_icon(UBYTE s,UBYTE hidden,UBYTE slot) BANKED {switch(s/4){'+''.join(f'case {n}:rf_creature_{n:02d}_icon(s%4,hidden,slot);break;' for n in range(count))+'}}')
    wrappers.append('static void rf_species_text(UBYTE s,UBYTE kind,UBYTE line,char*out) {switch(s/4){'+''.join(f'case {n}:rf_creature_{n:02d}_text(s%4,kind,line,out);break;' for n in range(count))+'}}')
    wrappers+=['void rf_art_name(UBYTE s,char*out) BANKED {rf_species_text(s,0,0,out);}','void rf_art_fact(UBYTE s,UBYTE line,char*out) BANKED {rf_species_text(s,1,line,out);}','void rf_art_scientific(UBYTE s,char*out) BANKED {rf_species_text(s,2,0,out);}']
    rules=[]
    for s in species:rules += [BEHAVIORS[s['behavior']],s.get('behavior_params',{}).get('period',90),s.get('behavior_params',{}).get('minimum_distance',2),s.get('behavior_params',{}).get('stress_threshold',4)]
    wrappers.append(decl('rf_rules',rules)+'UBYTE rf_species_rule(UBYTE s,UBYTE field) BANKED {return rf_rules[(UWORD)s*4+field];}')
    world=sorted(json.loads((root/'data/world.json').read_text())['maps'],key=lambda m:m['id'])
    sites=sorted(json.loads((root/'data/foundation_encounters.json').read_text())['records'],key=lambda s:s['spot_id'])
    header+=['#define RF_MAP_COUNT '+str(len(world)),'#define RF_SPOT_COUNT '+str(len(sites)),'#endif']
    (include/'rockflip_content.h').write_text('\n'.join(header)+'\n')
    dispatch='#pragma bank 255\n#include "rockflip_content.h"\n'
    for start in range(0,len(world),32):
        n=start//32;rows=[]
        for m in world[start:start+32]:
            ids=[s['spot_id'] for s in sites if s['room_id']==m['id']];assert len(ids)<=16
            camp=m['camp'] or [255,255]
            rows.append('{'+','.join(map(str,[m['id'],65535 if m['west'] is None else m['west'],65535 if m['east'] is None else m['east'],int(m['district_id'][1:])-1,STYLE[m['art_style']],*camp,len(ids)]))+',{'+','.join(map(str,ids+[65535]*(16-len(ids))))+'},'+json.dumps(m['name'])+',{'+','.join(json.dumps(row) for row in m['terrain'])+'},'+','.join(map(str,[65535 if m.get('north') is None else m['north'],65535 if m.get('south') is None else m['south'],m.get('north_x',255),m.get('south_x',255)]))+'}')
        fn=f'rf_maps_{n:02d}'
        c='#pragma bank 255\n#include "rockflip_content.h"\n#include <string.h>\nstatic const RFMap maps[]={'+','.join(rows)+'};\n'+f'void {fn}(UBYTE slot,RFMap*out) BANKED {{memcpy(out,maps+slot,sizeof(RFMap));}}\n'
        (src/(fn+'.c')).write_text(c);dispatch+=f'void {fn}(UBYTE slot,RFMap*out) BANKED;\n'
    dispatch+='void rf_world_load(UWORD map,RFMap*out) BANKED {switch(map/32){'+''.join(f'case {n}:rf_maps_{n:02d}(map%32,out);break;' for n in range((len(world)+31)//32))+'}}\n'
    for start in range(0,len(sites),64):
        n=start//64;rows=[]
        for s in sites[start:start+64]:rows.append('{'+','.join(str(s[k]) for k in ['spot_id','room_id','game_tile_x','game_tile_y','interaction_type','species_id','phase_mask'])+'}')
        fn=f'rf_spots_{n:02d}'
        (src/(fn+'.c')).write_text('#pragma bank 255\n#include "rockflip_content.h"\n#include <string.h>\nstatic const RFSpot spots[]={'+','.join(rows)+'};\n'+f'void {fn}(UBYTE slot,RFSpot*out) BANKED {{memcpy(out,spots+slot,sizeof(RFSpot));}}\n')
        dispatch+=f'void {fn}(UBYTE slot,RFSpot*out) BANKED;\n'
    dispatch+='void rf_world_spot(UWORD spot,RFSpot*out) BANKED {switch(spot/64){'+''.join(f'case {n}:rf_spots_{n:02d}(spot%64,out);break;' for n in range((len(sites)+63)//64))+'}}\n'
    ferry=[]
    lookup={m['id']:m for m in world}
    for m in world:
        for link in ('west','east'):
            to=m[link]
            if to is None:continue
            other=lookup[to]
            if (m['district_id']=='D12') != (other['district_id']=='D12') or (m['district_id']==other['district_id']=='D12' and m.get('subarea_id')!=other.get('subarea_id')):ferry.append((m['id'],to))
    dispatch+='UBYTE rf_world_transition(UWORD from,UWORD to) BANKED {return '+('||'.join(f'(from=={a}&&to=={b})' for a,b in ferry) or '0')+';}\n'
    heads=[next((m['id'] for m in world if m['district_id']==f'D{i+1:02d}' and m.get('district_trailhead')),world[0]['id']) for i in range(16)]
    hidden=next((m['id'] for m in world if m.get('hidden')),65535)
    dispatch+='static const UWORD trailheads[]={'+','.join(map(str,heads+[hidden]))+'};\nUWORD rf_world_trailhead(UBYTE district) BANKED {return district<17?trailheads[district]:trailheads[0];}\n'
    (src/'rockflip_content.c').write_text(dispatch)
    return '\n'.join(wrappers)+'\n'
