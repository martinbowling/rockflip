"""One-time source migration, retained for review; do not run on migrated source."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'plugins/rockflip/engine/src/states/rockflip.c'
s=p.read_text();assert 'static const char maps' in s
s=s.replace('#include <string.h>','#include <string.h>\n#include <stddef.h>\n#include "rockflip_content.h"\n#include "rockflip_save.h"')
a=s.index('/* Roam');b=s.index('/* Live state',a);s=s[:a]+s[b:]
a=s.index('struct RFState');b=s.index('static const UWORD day_pal',a)
s=s[:a]+'''struct RFState {UBYTE screen;UWORD room;UBYTE x,y,phase,spot,species,focus,distance;
 INT8 aim;UBYTE stress,score,count,points,guide;
 UBYTE best[RF_SPECIES_CAPACITY],photo_distance[RF_SPECIES_CAPACITY];
 INT8 photo_aim[RF_SPECIES_CAPACITY];UBYTE photo_phase[RF_SPECIES_CAPACITY];
 UWORD photo_map[RF_SPECIES_CAPACITY];UBYTE spot_state[RF_SPOT_CAPACITY],visited_maps[50];
 UWORD rng,steps,travel;UBYTE quest_flags[32];};
struct RFState rf;
RFMap rf_map;
RFSpot rf_spots[16];
UWORD rf_offsets[24];
UBYTE rf_photo_dirty;
UBYTE rf_ready,rf_oldjoy,rf_repeat,rf_moving,rf_dir,rf_tick,rf_wedged,rf_motion,rf_save_ok;
INT8 rf_dx,rf_dy,rf_subject_x,rf_subject_y;
UWORD rf_behavior_clock;
static void cache_map(void){UBYTE i;rf_world_load(rf.room,&rf_map);for(i=0;i<rf_map.spot_count;i++)rf_world_spot(rf_map.spots[i],rf_spots+i);}
static UBYTE *spot_flags(UBYTE i){return rf.spot_state+rf_spots[i].id;}
''' + s[b:]
s=s.replace('char s[3];s[0]=\'0\'+n/10;s[1]=\'0\'+n%10;s[2]=0;',"char s[4];s[0]='0'+n/100;s[1]='0'+(n/10)%10;s[2]='0'+n%10;s[3]=0;")
s=s.replace('for(i=0;i<6;i++)if(rf.best[i])','for(i=0;i<RF_SPECIES_COUNT;i++)if(rf.best[i])')
a=s.index('/* Reserve SRAM');b=s.index('static UBYTE random8',a)
s=s[:a]+'''/* RF02 payload has fixed capacity independent of the installed content count.
 * Engine bank 3 is the only SRAM owned here; store module streams dual records. */
static void save(void){rf_store_save(&rf,sizeof(rf));rf_save_ok=rf_store_ok;}
static void defaults(void){memset(&rf,0,sizeof(rf));rf.phase=1;rf.x=4;rf.y=4;rf.rng=0xACE1;}
static void load(void){UBYTE legacy[64],status,i,valid=1;status=rf_store_load(&rf,sizeof(rf),legacy);
 if(status==2){if(legacy[4]>1||legacy[5]>9||legacy[6]>6||legacy[7]>2||legacy[8]>99){defaults();return;}
 rf.room=legacy[4];rf.x=legacy[5];rf.y=legacy[6];rf.phase=legacy[7];rf.points=legacy[8];
 for(i=0;i<6;i++){rf.best[i]=legacy[12+i];rf.photo_distance[i]=legacy[18+i];rf.photo_aim[i]=(INT8)legacy[24+i];rf.photo_phase[i]=legacy[30+i];rf.photo_map[i]=rf.room;}
 for(i=0;i<7;i++)rf.spot_state[i]=((legacy[9]>>i)&1)|(((legacy[10]>>i)&1)<<1)|(((legacy[11]>>i)&1)<<2)|((legacy[36+i]&3)<<3);
 rf.rng=legacy[43]|((UWORD)legacy[44]<<8);rf.steps=legacy[45]|((UWORD)legacy[46]<<8);
 }else if(status!=1)return;
 if(rf.room>=RF_MAP_COUNT||rf.x>9||rf.y>6||rf.phase>2||rf.points>99)valid=0;
 for(i=0;i<RF_SPECIES_COUNT;i++)if(rf.best[i]>3||rf.photo_phase[i]>2||(rf.best[i]&&(rf.photo_distance[i]<2||rf.photo_distance[i]>4||rf.photo_aim[i]<-3||rf.photo_aim[i]>3||rf.photo_map[i]>=RF_MAP_COUNT)))valid=0;
 if(!valid){defaults();return;}rf.screen=0;rf.guide=0;rf.spot=0;recount();rf_save_ok=1;}
''' + s[b:]
s=s.replace('maps[rf.room]','rf_map.terrain')
s=s.replace('static UBYTE spot_at(UBYTE x,UBYTE y){UBYTE i;for(i=0;i<7;i++)if(spots[i][0]==rf.room&&spots[i][1]==x&&spots[i][2]==y)return i;return 255;}','static UBYTE spot_at(UBYTE x,UBYTE y){UBYTE i;for(i=0;i<rf_map.spot_count;i++)if(rf_spots[i].x==x&&rf_spots[i].y==y)return i;return 255;}')
s=s.replace('UBYTE type=spots[i][3],x=spots[i][1],y=spots[i][2];','UBYTE type=rf_spots[i].type,x=rf_spots[i].x,y=rf_spots[i].y;').replace('(rf.flipped&(1<<i))','(*spot_flags(i)&1)')
a=s.index('static void hud(');b=s.index('static void world(',a)
s=s[:a]+'''static void hud(void){UBYTE i;line(0,rf_map.name);text(0,1,phases[rf.phase]);number(7,1,rf.count);text(10,1,"/");number(11,1,RF_SPECIES_COUNT);line(16,"A:LOOK  B:REPLACE");line(17,"SELECT:GUIDE   START");}
''' + s[b:]
s=s.replace('clear();rf_art_load();palettes();for(y=0;', 'clear();cache_map();rf.visited_maps[rf.room/8]|=1<<(rf.room%8);rf_art_load();palettes();for(y=0;')
s=s.replace('for(i=0;i<7;i++)if(spots[i][0]==rf.room)draw_spot(i);if(!rf.room){metatile(1,6,18,6);}hud();position();','rf_art_map(rf.room,rf.phase,0);for(i=0;i<rf_map.spot_count;i++)draw_spot(i);if(rf_map.camp_x!=255)metatile(rf_map.camp_x,rf_map.camp_y,18,6);hud();position();')
a=s.index('static void station(');b=s.index('static void portrait_at(',a)
s=s[:a]+'''static void station(void){clear();line(1,"  RANGER FIELD CAMP");line(3,rf_store_locked?"NEWER SAVE: READ ONLY":"PHOTO ALBUM SAVED.");line(5,"FIELD GUIDE:");number(13,5,rf.count);text(16,5,"/");number(17,5,RF_SPECIES_COUNT);line(6,"RANGER POINTS:");number(15,6,rf.points);line(8,"A: REST UNTIL");text(14,8,phases[(rf.phase+1)%3]);line(10,"SELECT: FIELD GUIDE");line(12,"RIGHT: EXPEDITIONS");line(15,"B: RETURN TO TRAIL");if(rf.count==RF_SPECIES_COUNT)line(16,"YOUR GUIDE IS FILLED!");}
static void atlas(void){UBYTE i;RFMap m;clear();line(0,"    EXPEDITIONS");for(i=0;i<6;i++){UWORD id=(rf.travel/6)*6+i;if(id>=RF_MAP_COUNT)break;rf_world_load(id,&m);text(0,3+i*2,id==rf.travel?">":" ");text(1,3+i*2,m.name);}line(15,"D-PAD: CHOOSE ROUTE");line(16,"A: TRAVEL TO CAMP");line(17,"B: RETURN");}
static void guide_grid(void){UBYTE i,x,y,k,s;clear();line(0,"    FIELD GUIDE");number(5,1,rf.count);text(8,1,"/");number(9,1,RF_SPECIES_COUNT);for(i=0;i<6;i++){s=(rf.guide/6)*6+i;if(s>=RF_SPECIES_COUNT)break;x=2+(i%3)*6;y=3+(i/3)*6;rf_art_icon(s,!rf.best[s],i);for(k=0;k<4;k++)cell(x+(k&1),y+(k>>1),64+i*4+k,8+i);text(x,y+2,rf.best[s]?"SEEN":"????");text(x,y+3,"***");for(k=rf.best[s];k<3;k++)text(x+k,y+3,".");if(s==rf.guide)text(x-1,y,">");}line(15,"D-PAD: CHOOSE / PAGE");line(16,"A: FACTS START:ALBUM");line(17,"B: BACK TO TRAIL");}
''' +s[b:]
s=s.replace('char buf[21];clear();rf_art_name(rf.guide,buf);','char buf[48];clear();rf_art_name(rf.guide,buf);')
s=s.replace('for(i=0;i<3;i++){rf_art_fact(rf.guide,i,buf);line(12+i,buf);}','for(i=0;i<3;i++){rf_art_fact(rf.guide,i,buf);line(12+i,buf);}rf_art_scientific(rf.guide,buf);text(0,1,buf);if(strlen(buf)>20)text(0,2,buf+20);')
s=s.replace('BEST PHOTO / MOJAVE','BEST FIELD PHOTO').replace('PHOTOGRAPHED / MOJAVE','PHOTOGRAPHED')
s=s.replace('rf_art_portrait(rf.species,scale);rf_art_tint','rf_art_portrait_frame(rf.species,scale,(rf_behavior_clock/36)&1);rf_art_tint')
a=s.index('static void look(');b=s.index('static UBYTE blocked(',a)
s=s[:a]+'''static void look(void){UBYTE s=front_spot(),type;UBYTE *flags;if(s==255){line(16,"LOOK AT ROCKS / CLUES");return;}rf.spot=s;rf.species=rf_spots[s].species;type=rf_spots[s].type;flags=spot_flags(s);if(*flags&1){line(16,"B: PUT THE ROCK BACK");return;}if(type==0||type==5){*flags|=1;draw_spot(s);}if(!(rf_spots[s].phases&(1<<rf.phase))){line(16,rf.phase==2?"QUIET. TRY DAYLIGHT.":"QUIET. TRY LATER.");save();return;}if((*flags&2)&&((random8()&3)==0||(*flags&24)&&(random8()&1))){line(16,"JUST DIRT THIS TIME.");save();return;}*flags|=2;rf.screen=3;encounter();sound(0);save();}
static void replace(void){UBYTE s=front_spot();UBYTE *flags;if(s==255||!(*spot_flags(s)&1)){line(16,"NO FLIPPED ROCK HERE");return;}flags=spot_flags(s);*flags&=6;if(!(*flags&4)){*flags|=4;if(rf.points<99)rf.points++;}draw_spot(s);line(16,"ROCK REPLACED. +CARE");sound(1);save();}
''' +s[b:]
s=s.replace('if(!rf.room&&x==1&&y==6)','if(x==rf_map.camp_x&&y==rf_map.camp_y)')
a=s.index('static void departure(');b=s.index('static void move(',a)
s=s[:a]+'''static void departure(void){UBYTE i,*flags,n;for(i=0;i<rf_map.spot_count;i++){flags=spot_flags(i);n=(*flags>>3)&3;if((*flags&1)&&n<3)*flags=(*flags&7)|((n+1)<<3);}}
''' +s[b:]
s=s.replace('if((rf.room==0&&x>9)||(rf.room==1&&x<0)){departure();rf.room^=1;','if((x>9&&rf_map.east!=65535)||(x<0&&rf_map.west!=65535)){UWORD next=x<0?rf_map.west:rf_map.east;departure();rf.room=next;')
s=s.replace('memset(&rf,0,sizeof(rf));rf.phase=1;rf.x=4;rf.y=4;rf.rng=0xACE1;','defaults();')
# The defaults implementation must remain concrete, not recursive after replacement.
s=s.replace('static void defaults(void){defaults();}','static void defaults(void){memset(&rf,0,sizeof(rf));rf.phase=1;rf.x=4;rf.y=4;rf.rng=0xACE1;}')
s=s.replace('load();memcpy(BkgPalette', 'load();cache_map();memcpy(BkgPalette')
fields=['screen','room','x','y','phase','spot','species','focus','distance','aim','stress','score','count','points','guide','best','photo_distance','photo_aim','photo_phase','spot_state','rng','steps','photo_map','visited_maps']
s=s.replace('defaults();rf_dir=1;', 'defaults();'+''.join(f'rf_offsets[{i}]=offsetof(struct RFState,{f});' for i,f in enumerate(fields))+'rf_dir=1;')
s=s.replace('if(rf.room&&(rf_tick&31)==0)','if(rf.room==1&&(rf_tick&31)==0)')
s=s.replace('if(!rf.room&&rf.x<=2&&rf.y==5)','if(rf.x<=rf_map.camp_x+1&&rf.x+1>=rf_map.camp_x&&rf.y+1==rf_map.camp_y)')
s=s.replace('if(rf.species==5&&rf_behavior_clock%90==0)', 'if(rf_species_rule(rf.species,0)==3&&rf_behavior_clock%rf_species_rule(rf.species,1)==0)')
s=s.replace('if(rf.species==4&&rf_behavior_clock%80==0)', 'if(rf_species_rule(rf.species,0)==4&&rf_behavior_clock%rf_species_rule(rf.species,1)==0)')
s=s.replace('if(keys&J_B){rf.screen=2;world();return;}if(keys&15){rf_photo_dirty=1;', 'if(rf_behavior_clock%36==0){rf_photo_dirty=1;photo();}if(keys&J_B){rf.screen=2;world();return;}if(keys&15){rf_photo_dirty=1;')
s=s.replace('if(rf.species!=0&&rf.species!=2&&rf.species!=3)', 'if(rf_species_rule(rf.species,0)!=0&&rf_species_rule(rf.species,0)!=1)')
s=s.replace('if(rf.species==1){rf_wedged=90;', 'if(rf_species_rule(rf.species,0)==2){rf_wedged=90;')
s=s.replace('rf.photo_phase[rf.species]=rf.phase;', 'rf.photo_phase[rf.species]=rf.phase;rf.photo_map[rf.species]=rf.room;')
s=s.replace('(rf.guide+1)%6','(rf.guide+1)%RF_SPECIES_COUNT').replace('(rf.guide+5)%6','(rf.guide+RF_SPECIES_COUNT-1)%RF_SPECIES_COUNT').replace('(rf.guide+(keys&J_RIGHT?1:5))%6','(rf.guide+(keys&J_RIGHT?1:RF_SPECIES_COUNT-1))%RF_SPECIES_COUNT')
s=s.replace('if(rf.screen==9){', 'if(rf.screen==12){if(keys&J_B){rf.screen=9;station();return;}if(keys&15){rf.travel=(rf.travel+(keys&(J_RIGHT|J_DOWN)?1:RF_MAP_COUNT-1))%RF_MAP_COUNT;atlas();}if(keys&J_A){departure();rf.room=rf.travel;rf.x=0;rf.y=3;rf.screen=2;world();save();}return;}\n if(rf.screen==9){if(keys&J_RIGHT){rf.travel=rf.room;rf.screen=12;atlas();return;}')
s=s.replace('for(i=0;i<7;i++)if(!(rf.flipped&(1<<i))){rf.visited&=~(1<<i);rf.awarded&=~(1<<i);}', 'for(i=0;i<rf_map.spot_count;i++)if(!(*spot_flags(i)&1))*spot_flags(i)&=24;')
p.write_text(s)
