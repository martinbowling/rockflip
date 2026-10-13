#pragma bank 255
#include "states/rockflip.h"
#include "rockflip_art.h"
#include "actor.h"
#include "camera.h"
#include "input.h"
#include "palette.h"
#include <gb/cgb.h>
#include <string.h>
#include <stddef.h>
#include "rockflip_content.h"
#include "rockflip_save.h"
#include "rockflip_journal.h"
#include "rockflip_photo_quality.h"
#include "rockflip_camera_clock.h"
#include "rockflip_ranger.h"
#include "rockflip_audio.h"
#include "rockflip_campaign.h"
#include "rockflip_marine.h"
#include "rockflip_camp_route.h"
#include "rockflip_challenges.h"
#include "rockflip_runtime.h"
#include "rockflip_ui.h"
#include "rockflip_conditions.h"
#include "rockflip_guide_ui.h"
#include "rockflip_lens.h"
#include "rockflip_gallery.h"
#include "rockflip_region_ui.h"
#include "rockflip_landmark_repair.h"
#include "rockflip_onboarding_ui.h"
#include "rockflip_clue_ui.h"
#include "rockflip_explorer_actions.h"
#include "rockflip_new_game_ui.h"
#include "rockflip_atlas_step.h"
#include "rockflip_rock_restore.h"
#include "rockflip_restore_transaction.h"
/* Transient overlay only; never serialized as game progress. */
static UBYTE rf_field_notice;
#define station rf_ui_station
#define fieldkit rf_ui_fieldkit
#define challenges rf_ui_challenges
#define atlas rf_ui_atlas
#define secret_question rf_ui_secret_question
#define secret rf_ui_secret
#define credits rf_ui_credits
#define finale_question rf_ui_finale_question
#define exhibit rf_ui_exhibit
#define campaign_feedback rf_ui_campaign_feedback
#define campaign_question rf_ui_campaign_question
#define campaign rf_ui_campaign
#define journal_feedback rf_ui_journal_feedback
#define journal_question rf_ui_journal_question
#define journal rf_ui_journal

/* Live state is intentionally named for reproducible emulator checks. */

typedef char RFSavePayloadSizeCheck[(sizeof(struct RFState)==RF_STORE_WEATHER_SIZE)?1:-1];
struct RFState rf;
RFMap rf_map;
RFSpot rf_spots[16];
UWORD rf_offsets[24];
volatile UBYTE rf_input_edges,rf_input_sample;
UBYTE rf_welcome_page,rf_newgame_choice;
UBYTE rf_input_registered;
void rf_capture_input(void) NONBANKED {UBYTE sample=joypad();rf_input_edges|=sample&~rf_input_sample;rf_input_sample=sample;}
UBYTE rf_photo_dirty,rf_j_choice,rf_j_stage,rf_j_kind,rf_hidden,rf_c_district,rf_c_stage,rf_c_choice,rf_c_kind;
UBYTE rf_ready,rf_oldjoy,rf_repeat,rf_moving,rf_dir,rf_tick,rf_wedged,rf_motion,rf_save_ok;
INT8 rf_dx,rf_dy,rf_subject_x,rf_subject_y;
UWORD rf_behavior_clock;
UWORD rf_water_clock;
static void water_sync(UBYTE force){UWORD now;__critical {now=sys_time;}if(force||((now>>5)!=(rf_water_clock>>5))){rf_water_clock=now;rf_art_map_water(rf.room,(now>>5)&1);}}
/* Camp figures share bank0 tiles224..229; no extra hardware sprites.
 * Animation is serviced outside interrupts and measured in actual VBlanks. */
UWORD rf_camp_clock;
UBYTE rf_camp_pose;
static void camp_sync(UBYTE force){UWORD now;if(rf_map.camp_x==255)return;__critical {now=sys_time;}if(force){rf_camp_clock=now;rf_camp_pose=0;}else if((UWORD)(now-rf_camp_clock)>=96){rf_camp_clock=now;rf_camp_pose=(rf_camp_pose+1)&3;rf_ranger_camp_idle(rf_map.district,rf_camp_pose);}}
UBYTE rf_bonus_disturbed,rf_challenge;
static void quality_observation(RFPhotoQuality*q){UBYTE period=rf_species_rule(rf.species,1);q->behavior=rf_species_rule(rf.species,0);q->cycle=(rf_behavior_clock/period)&3;q->motion=rf_motion;q->distance=rf.distance;q->minimum_distance=rf_species_rule(rf.species,2);q->focus=rf.focus;q->stress=rf.stress;q->visible=!(rf_hidden||rf_wedged);q->disturbed=rf_bonus_disturbed;q->elapsed_cycle=rf_behavior_clock>=period;q->centered=rf_photo_quality_centered(rf_subject_x,rf.aim);q->x=rf_subject_x;q->y=rf_subject_y;}
static void cache_map(void){UBYTE i;rf_world_load(rf.room,&rf_map);for(i=0;i<rf_map.spot_count;i++)rf_world_spot(rf_map.spots[i],rf_spots+i);}
static UBYTE *spot_flags(UBYTE i){return rf.spot_state+rf_spots[i].id;}
static const UWORD day_pal[]={
 RGB(30,27,20),RGB(23,18,12),RGB(14,12,9),RGB(5,4,3),
 RGB(30,27,20),RGB(17,21,9),RGB(8,13,6),RGB(4,5,3),
 RGB(30,27,20),RGB(23,23,20),RGB(15,16,15),RGB(6,8,8),
 RGB(18,24,12),RGB(10,18,8),RGB(5,11,6),RGB(2,5,3),
 RGB(30,27,20),RGB(19,26,28),RGB(6,15,21),RGB(5,7,8),
 RGB(30,27,20),RGB(5,4,3),RGB(18,14,8),RGB(28,25,16),
 RGB(30,27,20),RGB(29,25,16),RGB(8,15,14),RGB(4,5,4),
 RGB(30,29,25),RGB(23,18,12),RGB(12,11,8),RGB(4,5,4)
};
static const UWORD ranger_pal[]={RGB(0,0,0),RGB(31,26,20),RGB(25,17,7),RGB(5,4,3)};
static const char *phases[]={"DAY","DUSK","NIGHT"};
static void cell(UBYTE x,UBYTE y,UBYTE tile,UBYTE attr){VBK_REG=0;set_bkg_tiles(x,y,1,1,&tile);VBK_REG=1;set_bkg_tiles(x,y,1,1,&attr);VBK_REG=0;}
/* Staged exact text renderer; cell() remains unchanged for mixed-palette art.
 * Local tilebuf20bytes, constantattributes inROM, no new persistentWRAM.
 * All exits restore VRAMbank0. Text is clipped exactly at native column20.
 */
static const UBYTE rf_row_attributes[20]={7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7};
static const UBYTE rf_hud_attributes[20]={135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135};
static const UBYTE rf_blank_row[20]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static void row_write(UBYTE x,UBYTE y,UBYTE count,const UBYTE*tiles){
 if(count){VBK_REG=0;set_bkg_tiles(x,y,count,1,tiles);VBK_REG=1;set_bkg_tiles(x,y,count,1,(rf.screen==2&&(y<2||y>=16))?rf_hud_attributes:rf_row_attributes);}
 VBK_REG=0;
}
static void text(UBYTE x,UBYTE y,const char*s){
 UBYTE tilebuf[20],count=0;char ch;
 while(*s&&x+count<20){ch=*s++;if(ch>=32)tilebuf[count]=ch-32;else tilebuf[count]=31;count++;}
 row_write(x,y,count,tilebuf);
}
static void line(UBYTE y,const char*s){
 UBYTE tilebuf[20],count=0;char ch;
 while(count<20){if(*s){ch=*s++;if(ch>=32)tilebuf[count]=ch-32;else tilebuf[count]=31;}else tilebuf[count]=0;count++;}
 row_write(0,y,20,tilebuf);
}
static void clear(void){
 UBYTE y;PLAYER.flags|=ACTOR_FLAG_HIDDEN;if(rf.screen!=2)HIDE_SPRITES;rf_art_font();
 for(y=0;y<18;y++)row_write(0,y,20,rf_blank_row);
}

static void number(UBYTE x,UBYTE y,UBYTE n){char s[4];s[0]='0'+n/100;s[1]='0'+(n/10)%10;s[2]='0'+n%10;s[3]=0;text(x,y,s);}
static void sound(UBYTE type){rf_audio_sfx(type);}
static void palettes(void){UBYTE i;UWORD colors[32],v;for(i=0;i<32;i++){v=day_pal[i];if(i<20&&rf.phase==2)v=RGB((v&31)/2,((v>>5)&31)/2,((v>>10)&31)/2+5);else if(i<20&&rf.phase==1)v=RGB((v&31),((v>>5)&31)*3/4,((v>>10)&31)*3/4);colors[i]=v;}memcpy(BkgPalette,colors,64);set_bkg_palette(0,8,colors);memcpy(SprPalette,ranger_pal,8);set_sprite_palette(0,1,ranger_pal);}
static void recount(void){UBYTE i;rf.count=0;for(i=0;i<RF_SPECIES_COUNT;i++)if(rf.best[i])rf.count++;}
/* RF02 payload has fixed capacity independent of the installed content count.
 * Engine bank 3 is the only SRAM owned here; store module streams dual records. */
static void save(void){rf_store_save(&rf,sizeof(rf));rf_save_ok=rf_store_ok;}
static void defaults(void){memset(&rf,0,sizeof(rf));rf.phase=0;rf.x=2;rf.y=6;rf.rng=0xACE1;rf.quest_flags[9]=72;rf_challenge_fresh();rf.quest_flags[8]|=2;}
static void load(void){UBYTE legacy[64],status,i,valid=1;status=rf_store_load(&rf,sizeof(rf),legacy);
 if(status==2){if(legacy[4]>1||legacy[5]>9||legacy[6]>6||legacy[7]>2||legacy[8]>99){defaults();return;}
 rf.room=legacy[4];rf.x=legacy[5];rf.y=legacy[6];rf.phase=legacy[7];rf.points=legacy[8];
 for(i=0;i<6;i++){rf.best[i]=legacy[12+i];rf.photo_distance[i]=legacy[18+i];rf.photo_aim[i]=(INT8)legacy[24+i];rf.photo_phase[i]=legacy[30+i];rf.photo_map[i]=rf.room;}
 for(i=0;i<7;i++)rf.spot_state[i]=((legacy[9]>>i)&1)|(((legacy[10]>>i)&1)<<1)|(((legacy[11]>>i)&1)<<2)|((legacy[36+i]&3)<<3);
 rf.rng=legacy[43]|((UWORD)legacy[44]<<8);rf.steps=legacy[45]|((UWORD)legacy[46]<<8);
 }else if(status!=1&&status!=4)return;
 /* Contentrevision2:SSAR merges formerSouthernRubberBoa60 intoRubberBoa59.
  * New60 is a separately sourced mountainkingsnake. Never reinterpret an old
  * boa photograph as that new species. Old room/site evidence remains the same
  * physicalboa population, now canonically59; copiedpose is explicitlyunknown. */
 if(!(rf.quest_flags[9]&64)){if(rf.best[60]>rf.best[59]){rf.best[59]=rf.best[60];rf.photo_distance[59]=rf.photo_distance[60];rf.photo_aim[59]=rf.photo_aim[60];rf.photo_phase[59]=rf.photo_phase[60];rf.photo_map[59]=rf.photo_map[60];rf.photo_snapshot[59]=0;}rf.best[60]=rf.photo_distance[60]=rf.photo_aim[60]=rf.photo_phase[60]=rf.photo_snapshot[60]=0;rf.photo_map[60]=0;rf.quest_flags[9]|=64;}
 if(rf.room>=RF_MAP_COUNT||rf.x>9||rf.y>6||rf.phase>2||rf.points>99)valid=0;
 for(i=0;i<RF_SPECIES_COUNT;i++)if((rf.photo_snapshot[i]&64)||(rf.photo_snapshot[i]&&!(rf.photo_snapshot[i]&128))||rf.best[i]>3||rf.photo_phase[i]>2||(rf.best[i]&&(rf.photo_distance[i]<2||rf.photo_distance[i]>4||rf.photo_aim[i]<-3||rf.photo_aim[i]>3||rf.photo_map[i]>=RF_MAP_COUNT)))valid=0;
 if(!valid){defaults();return;}if(rf_store_loaded_layout<6)rf.quest_flags[8]&=253;if(rf_store_loaded_layout<5)rf_challenge_migrate();else if(!rf_challenge_awards_valid()){defaults();return;}rf.screen=0;rf.guide=0;rf.spot=0;recount();{UBYTE n=0;for(i=0;i<150;i++)if(rf.best[i])n++;if(n<150)rf.quest_flags[31]&=127;}rf_save_ok=1;}
static UBYTE random8(void){rf.rng^=rf.rng<<7;rf.rng^=rf.rng>>9;rf.rng^=rf.rng<<8;return rf.rng&255;}
static UBYTE terrain(UBYTE x,UBYTE y) {
    char c=rf_map.terrain[y][x];
    if(c=='T') {
        if(x==0||rf_map.terrain[y][x-1]!='T')return 14;
        if(x==9||rf_map.terrain[y][x+1]!='T')return 15;
        return 2;
    }
    if(c=='C')return rf.room&&x>=6?19:5;
    if(c=='G')return ((x+y)&1)?16:6;
    if(c=='W')return 20+(y==2?2:0)+(x==8?1:0);
    if(rf.room&&x>5&&y<4)return 10;
    switch((x*3+y*7)%9) {
        case 0:return 1;
        case 2:return 9;
        case 4:return 12;
        case 6:return 11;
        default:return 0;
    }
}
static void metatile(UBYTE x,UBYTE y,UBYTE id,UBYTE pal){UBYTE t;for(t=0;t<4;t++)cell(x*2+(t&1),2+y*2+(t>>1),id*4+t,pal|8);}
static UBYTE spot_at(UBYTE x,UBYTE y){UBYTE i;for(i=0;i<rf_map.spot_count;i++)if(rf_spots[i].x==x&&rf_spots[i].y==y)return i;return 255;}
static void draw_spot(UBYTE i) {
    UBYTE type=rf_spots[i].type,x=rf_spots[i].x,y=rf_spots[i].y;
    if(type==0||type==5)metatile(x,y,(*spot_flags(i)&1)?4:3,0);
    else if(type==1)metatile(x,y,16,2);
    else if(type==2)metatile(x,y,17,0);
    else if(type==6)metatile(x,y,24,2);
    else if(type==7)metatile(x,y,19,1);
    else if(type==3)metatile(x,y,13,0);
    else metatile(x,y,5,1);
}
static void position(void){PLAYER.pos.x=PX_TO_SUBPX((UWORD)rf.x*16);PLAYER.pos.y=PX_TO_SUBPX((UWORD)32+rf.y*16);PLAYER.flags|=ACTOR_FLAG_PINNED;PLAYER.flags&=~(ACTOR_FLAG_HIDDEN|ACTOR_FLAG_DISABLED);SHOW_SPRITES;}
static void hud(void){static const char *w[]={"FR","CL","RN","AR"};static const char *season[]={"WI","SP","SU","FA"};UBYTE c=rf_conditions_current();line(0,rf_map.name);text(0,1,phases[rf.phase]);number(7,1,rf.count);text(10,1,"/");number(11,1,RF_SPECIES_COUNT);text(15,1,w[c&3]);text(18,1,season[c>>2]);rf_clue_hud();line(17,"SELECT:GUIDE   START");}
static void world(void){UBYTE x,y,i,t;rf_field_notice=0;clear();cache_map();rf.visited_maps[rf.room/8]|=1<<(rf.room%8);rf_art_load();palettes();for(y=0;y<7;y++)for(x=0;x<10;x++){t=terrain(x,y);metatile(x,y,t,rf_art_terrain_pal(t));if(rf_map.terrain[y][x]=='J'||rf_map.terrain[y][x]=='j'){UBYTE k=rf_map.terrain[y][x]=='J'?0:4;for(i=0;i<4;i++)cell(x*2+(i&1),2+y*2+(i>>1),100+k+i,9);}}for(y=0;y<7;y++)for(x=0;x<9;x++)if(rf_map.terrain[y][x]=='G'&&rf_map.terrain[y][x+1]=='G') {
    for(i=0;i<8;i++)cell(x*2+(i%4),2+y*2+(i/4),108+i,10);
    x++;
}
rf_art_map(rf.room,rf.phase,0);rf_conditions_shade(rf_conditions_current());for(i=0;i<rf_map.spot_count;i++)draw_spot(i);if(rf_map.camp_x!=255)metatile(rf_map.camp_x,rf_map.camp_y,18,6);if(rf_map.camp_x!=255)rf_ranger_camp(rf_map.district,rf_map.camp_x,rf_map.camp_y);if(rf_map.north!=65535)cell(rf_map.north_x*2,2,62,7);if(rf_map.south!=65535)cell(rf_map.south_x*2,15,54,7);water_sync(1);camp_sync(1);rf_art_hud_mask();hud();position();}
static void title(void){clear();palettes();rf_art_title();line(13,rf_store_locked?"START: READ ONLY":rf_save_ok?"  START: CONTINUE":"  START: FIRST HIKE");if(rf_store_locked)line(14,"NEWER SAVE READ ONLY");else if(rf_save_ok)line(14,"SELECT: SAVE OPTIONS");line(15,"    IDEA: BILBY");line(16,"   MARTIN BOWLING");line(17,"       + ROAM");}
static void restore_flush_input(void);
/* Explicit confirmation changes live state; SRAM is never erased here. */
static void start_new_journal(void){
 if(rf_store_locked){rf.screen=0;title();return;}
 defaults();rf_save_ok=rf_store_ok=0;rf_welcome_page=0;rf_newgame_choice=0;
 rf_restore_end();rf_lens_begin();rf_audio_mute(0);rf_moving=rf_repeat=rf_dx=rf_dy=0;
 rf_hidden=rf_wedged=rf_motion=rf_photo_dirty=0;rf_dir=2;
 actor_set_dir(&PLAYER,DIR_LEFT,0);cache_map();palettes();restore_flush_input();
 rf.screen=29;rf_ui_welcome(0);
}
static void help(void){clear();line(1,"  TAKE ONLY PHOTOS");line(3,"D-PAD: HIKE AND AIM");line(4,"A: LOOK / SHUTTER");line(5,"B: REPLACE THE ROCK");line(7,"CAMERA: UP BACKS OFF");line(8,"DOWN CREEPS CLOSER");line(9,"WAIT TO FOCUS.");line(10,"RUSH: CRITTERS HIDE.");line(12,"START: SAVE / PACK");line(13,"SELECT: FIELD GUIDE");line(15,"NO TOUCHING WILDLIFE");line(17,"A: BEGIN YOUR HIKE");}

/* Saving stays available on every trail. Ranger/rest/travel facilities live
 * at the49 physical camps; the detached postgame refuge has an explicit return. */
static UBYTE near_camp(void){INT8 dx,dy;if(rf_map.camp_x==255)return 0;dx=(INT8)rf.x-rf_map.camp_x;dy=(INT8)rf.y-rf_map.camp_y;if(dx<0)dx=-dx;if(dy<0)dy=-dy;return dx+dy==1;}


static void sync_journal_rocks(void){rf_journal_rock(rf.quest_flags,0,rf.spot_state[0]&1);rf_journal_rock(rf.quest_flags,5,rf.spot_state[5]&1);rf_journal_rock(rf.quest_flags,6,rf.spot_state[6]&1);}



static UBYTE regular_count(void){UBYTE i,n=0;for(i=0;i<150&&i<RF_SPECIES_COUNT;i++)if(rf.best[i])n++;return n;}









#define guide_grid rf_guide_grid
#define detail rf_guide_detail
static void portrait_at(UBYTE x,UBYTE y,UBYTE scale){UBYTE i,side=scale==2?4:6;rf_art_portrait(rf.guide,scale);rf_art_tint(0);for(i=0;i<side*side;i++)cell(x+i%side,y+i/side,128+i,13);}
static UBYTE marine(UBYTE species){return species==61||species==73;}
void rf_guide_album_picture(void) BANKED {UBYTE i,side,scale,x,y,snap=rf.photo_snapshot[rf.guide];scale=rf_lens_saved_scale(rf.photo_distance[rf.guide],snap);side=scale==2?4:6;x=(scale==2?8:7)-rf.photo_aim[rf.guide];y=scale==2?6:5;if(snap&128){x+=(snap&3)-1;y+=((snap>>2)&1)-1;}{UBYTE phase=rf.phase;rf.phase=rf.photo_phase[rf.guide];palettes();rf.phase=phase;}if(marine(rf.guide))rf_marine_backdrop(rf.photo_phase[rf.guide]);else rf_art_backdrop(rf.photo_map[rf.guide],rf.photo_phase[rf.guide]);if(snap&16)rf_conditions_shade(rf_conditions_photo(rf.guide));rf_art_portrait_frame(rf.guide,scale,(snap&128)?(snap>>3)&1:0);if(marine(rf.guide))rf_marine_tint(rf.photo_phase[rf.guide]);else rf_art_tint(rf.photo_phase[rf.guide]);for(i=0;i<side*side;i++)cell(x+i%side,y+i/side,128+i,13);}
static void encounter(void){char name[21];clear();if(rf.species==150&&!rf.best[150])strcpy(name,"UNWRITTEN FIELD PAGE");else rf_art_name(rf.species,name);line(1,"         !");line(3,name);rf.guide=rf.species;portrait_at(7,5,3);line(12,"KEEP A LITTLE SPACE.");line(14,"A: OPEN YOUR CAMERA");line(16,"B: LEAVE IT IN PEACE");}
static void photo(void){UBYTE x,y,i,side,scale=rf_lens_scale(rf.distance);char buf[21];if(rf.species==150&&!rf.best[150])strcpy(buf,"UNWRITTEN FIELD PAGE");else rf_art_name(rf.species,buf);line(0,buf);text(0,1,"FOCUS:");number(6,1,rf.focus);text(11,1,"SPACE:");number(17,1,rf.distance);line(3," +----------------+");for(y=4;y<12;y++){text(1,y,"|");text(18,y,"|");}line(12," +----------------+");if(rf_photo_dirty){palettes();if(marine(rf.species))rf_marine_backdrop(rf.phase);else rf_art_backdrop(rf.room,rf.phase);rf_conditions_shade(rf_conditions_current());rf_art_portrait_frame(rf.species,scale,rf_motion);if(marine(rf.species))rf_marine_tint(rf.phase);else rf_art_tint(rf.phase);side=scale==2?4:6;x=scale==2?8:7;x+=(rf_subject_x-rf.aim);y=scale==2?6:5;y+=rf_subject_y;if(!rf_wedged&&!rf_hidden)for(i=0;i<side*side;i++)cell(x+i%side,y+i/side,128+i,13);rf_photo_dirty=0;}/* A quiet two-corner reticle avoids covering the animal. */text(rf.focus>=45?6:5,7,"[");text(rf.focus>=45?13:14,7,"]");line(14,(rf_wedged||rf_hidden)?"HIDING... HOLD STILL":rf.focus>=45?"FOCUSED. A: SHUTTER":"HOLD STILL TO FOCUS");if(!rf_hidden&&!rf_wedged&&rf.focus>=45){RFPhotoQuality q;quality_observation(&q);rf_photo_quality_hint(&q,buf);line(14,buf);}rf_lens_hint(buf);line(13,buf);line(15,"LEFT/RIGHT: FRAME");line(16,"UP:BACK DOWN:CLOSER");line(17,"A:SHUTTER  B:LEAVE");}
static void result(void){UBYTE i;char buf[21];clear();line(1,rf.score?"    PHOTO SAVED!":"    IT SLIPPED AWAY");if(rf.species==150&&!rf.best[150])strcpy(buf,"UNWRITTEN FIELD PAGE");else rf_art_name(rf.species,buf);line(3,buf);rf.guide=rf.species;portrait_at(7,5,3);if(rf.score){for(i=0;i<rf.score;i++)text(8+i,12,"*");line(13,rf.score==3?"NATURAL PHOTO BONUS":"FIELD RECORD SAVED");rf_art_fact(rf.species,0,buf);line(14,buf);rf_art_fact(rf.species,1,buf);line(15,buf);}else{line(13,"SLOW DOWN NEXT TIME.");line(14,"LET WILDLIFE RELAX.");}line(17,"A/B: RETURN TO TRAIL");}
static void begin_photo_now(void){rf_lens_begin();rf.screen=4;rf.focus=0;rf.distance=4;rf.aim=0;rf.stress=rf_wedged=rf_motion=rf_hidden=0;rf_subject_x=rf_subject_y=0;rf_behavior_clock=0;rf_bonus_disturbed=0;rf_photo_dirty=1;clear();photo();rf_camera_clock_begin();}
static UBYTE front_spot(void){INT8 x=rf.x,y=rf.y;if(rf_dir==0)y++;else if(rf_dir==1)y--;else if(rf_dir==2)x--;else x++;if(x<0||x>9||y<0||y>6)return 255;return spot_at(x,y);}
static void look_now(void){UBYTE s=front_spot(),type;UBYTE *flags;if(s==255){line(16,"LOOK AT ROCKS/CLUES");return;}rf.spot=s;rf.species=rf_spots[s].species;if(rf.species==150&&!rf_campaign_hidden_ready(rf.quest_flags)){line(16,"QUIET REFUGE. LATER.");return;}type=rf_spots[s].type;flags=spot_flags(s);if(*flags&1){line(16,"B: PUT THE ROCK BACK");return;}if(type==0||type==5){*flags|=1;rf_journal_rock(rf.quest_flags,rf_spots[s].id,1);draw_spot(s);}if(!(rf_spots[s].phases&(1<<rf.phase))){if(type==0||type==5)line(16,"QUIET. B:REPLACE");else line(16,rf.phase==2?"QUIET. TRY DAYLIGHT.":"QUIET. TRY LATER.");save();return;}if(!rf_conditions_allowed(rf.species,rf_conditions_current())){char clue[21];rf_field_notice=1;rf_conditions_clue(rf.species,0,clue);line(14,clue);rf_conditions_clue(rf.species,1,clue);line(15,clue);if(type==0||type==5)line(16,"B:REPLACE. USE CAMP");else line(16,"PLAN WEATHER AT CAMP");save();return;}if((*flags&2)&&((*flags>>5)&3)<2&&((random8()&3)==0||(*flags&24)&&(random8()&1))){*flags+=32;if(type==0||type==5)line(16,"QUIET. B:REPLACE");else line(16,"QUIET. LOOK AGAIN.");save();return;}*flags=(*flags&31)|2;rf.screen=3;encounter();sound(0);save();}
/* Transient explorer actions never enter the saved RFState schema. The
 * actual look/photo operation runs once, after the second source pose renders.
 * Player coordinates/direction cannot change during this short window. */
static UBYTE rf_action_pending;
static void look(void){UBYTE s=front_spot();
 if(s==255||(*spot_flags(s)&1)){look_now();return;}
 /* Keep the original hidden-refuge preflight ahead of any action gesture. */
 if(rf_spots[s].species==150&&!rf_campaign_hidden_ready(rf.quest_flags)){look_now();return;}
 rf_action_pending=1;
 rf_explorer_action_begin((rf_spots[s].type==0)?RF_EXPLORER_LIFT:RF_EXPLORER_PEEK);
 restore_flush_input();
}
static void begin_photo(void){
 /* Show the camera being raised on the same trail before entering its UI. */
 rf.screen=2;world();rf_action_pending=2;
 rf_explorer_action_begin(RF_EXPLORER_CAMERA);restore_flush_input();
}
/* Called only after final closed pose is visible, or for unchanged wet-rock type5. */
static void replace_finish(UBYTE s){UBYTE gained,pending;UBYTE*flags=spot_flags(s);
 gained=!(*flags&4)&&rf.points<99;pending=*flags&128;
 *flags&=102;draw_spot(s);
 if(pending)rf_campaign_care(rf.quest_flags,rf_spots[s].id);
 rf_journal_care(rf.quest_flags,rf_spots[s].id);
 if(!(*flags&4)){*flags|=4;if(rf.points<99)rf.points++;}
 line(16,gained?"ROCK REPLACED. +CARE":"HOME RESTORED.");sound(2);save();
}
static UWORD restore_now(void){UWORD now;__critical {now=sys_time;}return now;}
static void restore_flush_input(void){__critical {rf_oldjoy=joypad();rf_input_edges=0;rf_input_sample=rf_oldjoy;}rf_repeat=0;}
static void replace(void){UBYTE s;
 /* Closed/nonmovable clues only leave a note; no progress or save. */
 if(rf_clue_leave())return;
 s=front_spot();
 if(s==255||!(*spot_flags(s)&1))return;
 if(rf_spots[s].type!=0){replace_finish(s);return;}
 rf_restore_begin(s,restore_now());
 rf_rock_restore_frame(rf_spots[s].x,rf_spots[s].y,0);
 rf_restore_drawn(restore_now());restore_flush_input();
}
static UBYTE blocked(UBYTE x,UBYTE y){UBYTE s;char c=rf_map.terrain[y][x];if(c=='G'||c=='W'||c=='J'||c=='j')return 1;if(x==rf_map.camp_x&&y==rf_map.camp_y)return 1;s=spot_at(x,y);return s!=255;}
static void departure(void){UBYTE i,*flags,n;for(i=0;i<rf_map.spot_count;i++){flags=spot_flags(i);n=(*flags>>3)&3;if((*flags&1)&&n<3)*flags=(*flags&231)|((n+1)<<3);}}
static void move(UBYTE keys){INT8 x=rf.x,y=rf.y;direction_e d;rf_dx=rf_dy=0;if(keys&J_DOWN){rf_dy=1;rf_dir=0;d=DIR_DOWN;}else if(keys&J_UP){rf_dy=-1;rf_dir=1;d=DIR_UP;}else if(keys&J_LEFT){rf_dx=-1;rf_dir=2;d=DIR_LEFT;}else{rf_dx=1;rf_dir=3;d=DIR_RIGHT;}actor_set_dir(&PLAYER,d,0);rf_clue_hud();x+=rf_dx;y+=rf_dy;if((y<0||y>6)&&rf.x==(y<0?rf_map.north_x:rf_map.south_x)){UWORD next=y<0?rf_map.north:rf_map.south;if(next!=65535){departure();rf.room=next;cache_map();rf.x=y<0?rf_map.south_x:rf_map.north_x;rf.y=y<0?6:0;world();save();}return;}if((x<0||x>9)&&rf.y==3){if((x>9&&rf_map.east!=65535)||(x<0&&rf_map.west!=65535)){UWORD next=x<0?rf_map.west:rf_map.east;if(rf_world_transition(rf.room,next)){rf.travel=next;rf.screen=16;clear();line(1,"    ISLAND FERRY");line(4,"SEPARATE ISLANDS,");line(5,"DIFFERENT HOMES.");line(8,"KEEP YOUR NOTES");line(9,"WITH EACH ISLAND.");line(13,"A: BOARD THE FERRY");line(15,"B: KEEP EXPLORING");return;}departure();rf.room=next;rf.x=x<0?9:0;rf.y=3;world();save();}return;}if(x<0||x>9||y<0||y>6||blocked(x,y))return;rf.x=x;rf.y=y;rf_moving=8;rf.steps++;actor_set_dir(&PLAYER,d,1);rf_clue_hud();}
void rockflip_init(void) BANKED {defaults();rf_offsets[0]=offsetof(struct RFState,screen);rf_offsets[1]=offsetof(struct RFState,room);rf_offsets[2]=offsetof(struct RFState,x);rf_offsets[3]=offsetof(struct RFState,y);rf_offsets[4]=offsetof(struct RFState,phase);rf_offsets[5]=offsetof(struct RFState,spot);rf_offsets[6]=offsetof(struct RFState,species);rf_offsets[7]=offsetof(struct RFState,focus);rf_offsets[8]=offsetof(struct RFState,distance);rf_offsets[9]=offsetof(struct RFState,aim);rf_offsets[10]=offsetof(struct RFState,stress);rf_offsets[11]=offsetof(struct RFState,score);rf_offsets[12]=offsetof(struct RFState,count);rf_offsets[13]=offsetof(struct RFState,points);rf_offsets[14]=offsetof(struct RFState,guide);rf_offsets[15]=offsetof(struct RFState,best);rf_offsets[16]=offsetof(struct RFState,photo_distance);rf_offsets[17]=offsetof(struct RFState,photo_aim);rf_offsets[18]=offsetof(struct RFState,photo_phase);rf_offsets[19]=offsetof(struct RFState,spot_state);rf_offsets[20]=offsetof(struct RFState,rng);rf_offsets[21]=offsetof(struct RFState,steps);rf_offsets[22]=offsetof(struct RFState,photo_map);rf_offsets[23]=offsetof(struct RFState,visited_maps);rf_restore_end();rf_action_pending=0;rf_welcome_page=rf_newgame_choice=0;rf_dir=1;rf_ready=rf_oldjoy=rf_repeat=rf_moving=rf_tick=rf_save_ok=0;camera_offset_x=camera_offset_y=0;camera_deadzone_x=camera_deadzone_y=127;camera_settings=CAMERA_UNLOCKED;camera_x=PX_TO_SUBPX(80u);camera_y=PX_TO_SUBPX(72u);PLAYER.flags|=ACTOR_FLAG_HIDDEN;/* An8-update tile walk must expose all3 stride poses: mask1 advances every2 gameframes. Scene player defaults were loaded before this custom init. */PLAYER.anim_tick=1;load();sync_journal_rocks();cache_map();if(rf_save_ok)rf_landmark_repair(rf.room,&rf.x,&rf.y);if(!rf_save_ok&&!rf_store_locked){rf_dir=2;actor_set_dir(&PLAYER,DIR_LEFT,0);}rf_audio_init();rf_audio_mute((rf.quest_flags[9]&128)!=0);rf_input_edges=rf_input_sample=0;if(!rf_input_registered){add_VBL(rf_capture_input);rf_input_registered=1;}memcpy(BkgPalette,day_pal,64);memcpy(SprPalette,ranger_pal,8);}
void rockflip_update(void) BANKED {UBYTE keys=joy&~rf_oldjoy,i;__critical {keys|=rf_input_edges;rf_input_edges=0;}HIDE_WIN;rf_audio_update(rf_map.district,rf.phase);if(rf.screen!=2)HIDE_SPRITES;move_bkg(0,0);if(!rf_ready){rf_ready=1;rf_art_load();title();rf_oldjoy=joy;return;}if((joy&15)&&(joy&15)==(rf_oldjoy&15)){if(++rf_repeat>=12){keys|=joy&15;rf_repeat=0;}}else rf_repeat=0;rf_oldjoy=joy;rf_tick++;
 if(rf.screen==0){if(keys&J_SELECT&&rf_save_ok&&!rf_store_locked){rf_newgame_choice=0;rf.screen=35;rf_ui_save_options(0);return;}if(keys&(J_START|J_A)){if(rf_save_ok||rf_store_locked){rf.screen=2;world();}else {rf_welcome_page=0;rf.screen=29;rf_ui_welcome(0);}}return;}
 if(rf.screen==35||rf.screen==36){
  if(keys&J_B){rf_newgame_choice=0;rf.screen=0;title();return;}
  if(rf_store_locked){if(keys&J_A){rf.screen=0;title();}return;}
  if(keys&(J_UP|J_DOWN)){rf_newgame_choice^=1;if(rf.screen==35)rf_ui_save_options(rf_newgame_choice);else rf_ui_new_game_confirm(rf_newgame_choice);return;}
  if(keys&J_A){
   if(rf.screen==35){if(!rf_newgame_choice){rf.screen=2;world();}else{rf_newgame_choice=0;rf.screen=36;rf_ui_new_game_confirm(0);}}
   else if(!rf_newgame_choice){rf.screen=0;title();}else start_new_journal();
  }
  return;
 }
 if(rf.screen==29){if((keys&J_B)||((keys&(J_A|J_START))&&rf_welcome_page==2)){rf.screen=2;world();return;}if(keys&(J_A|J_START)){rf_welcome_page++;rf_ui_welcome(rf_welcome_page);}return;}
 if(rf.screen==1){if(keys&(J_A|J_START)){rf.screen=2;world();}return;}
 if(rf_action_pending){water_sync(0);camp_sync(0);
  if(rf_explorer_action_update()){
   UBYTE action=rf_action_pending;rf_action_pending=0;
   rf_explorer_action_end();restore_flush_input();
   if(action==1)look_now();else begin_photo_now();
  }
  return;
 }
 if(rf.screen==2){water_sync(0);camp_sync(0);if(rf_restore_busy){UBYTE step=rf_restore_tick(restore_now());
 if(step==1){rf_rock_restore_frame(rf_spots[rf_restore_spot].x,rf_spots[rf_restore_spot].y,rf_restore_frame);rf_restore_drawn(restore_now());}
 else if(step==2){rf_restore_frame=4;replace_finish(rf_restore_spot);rf_restore_end();}
 restore_flush_input();return;}
if(rf_moving){__critical {rf_input_edges|=keys&(J_A|J_B|J_START|J_SELECT);}PLAYER.pos.x+=(INT16)rf_dx*64;PLAYER.pos.y+=(INT16)rf_dy*64;if(!--rf_moving){position();actor_set_anim_idle(&PLAYER);}return;}if(rf_field_notice&&(keys&(J_B|15)))world();if(keys&J_SELECT){rf_guide_open(rf.screen);return;}if(keys&J_START){save();if(near_camp()){rf.screen=9;station();}else{rf.screen=25;fieldkit();}return;}if(keys&J_A){if(rf_map.camp_x!=255&&((rf_dir==0&&rf.x==rf_map.camp_x&&rf.y+1==rf_map.camp_y)||(rf_dir==1&&rf.x==rf_map.camp_x&&rf.y==rf_map.camp_y+1)||(rf_dir==2&&rf.x==rf_map.camp_x+1&&rf.y==rf_map.camp_y)||(rf_dir==3&&rf.x+1==rf_map.camp_x&&rf.y==rf_map.camp_y))){save();rf.screen=9;station();}else look();return;}if(keys&J_B){replace();return;}if(keys&15)move(keys);return;}
 if(rf.screen==30||rf.screen==31){
  if(keys&J_B){rf.screen=rf_region_origin;if(rf.screen==25)fieldkit();else if(rf.screen==17)campaign();else {rf.screen=9;station();}return;}
  if(keys&J_A){if(rf.screen==30){rf.screen=31;rf_ui_region_detail();}else {rf.screen=30;rf_ui_region_map();}return;}
  if(keys&15){if(rf.screen==30){rf_region_move(keys);rf_ui_region_map();}else {rf_region_follow(keys);rf_ui_region_detail();}}return;
 }
 if(rf.screen==32){if(keys&J_B){rf.screen=25;fieldkit();}return;}
 if(rf.screen==25){if(keys&J_UP){rf.screen=32;rf_ui_pinned_notes();return;}if(keys&J_LEFT){rf_region_open(rf.room,25);rf.screen=30;rf_ui_region_map();return;}if(keys&J_A){rf_challenge=rf_map.district*2;rf.screen=26;challenges();return;}if(keys&(J_B|J_START)){rf.screen=2;world();return;}if(keys&J_SELECT){rf_guide_open(rf.screen);return;}if(keys&J_RIGHT&&rf.room==131){departure();rf.room=rf_world_trailhead(8);rf.x=0;rf.y=3;rf.screen=2;world();save();return;}return;}
 if(rf.screen==26){if(keys&J_B){rf.screen=25;fieldkit();return;}if(keys&(J_LEFT|J_RIGHT)){rf_challenge=(rf_challenge+(keys&J_RIGHT?1:31))%32;challenges();}return;}
 if(rf.screen==3){if(keys&J_A)begin_photo();else if(keys&J_B){rf.screen=2;world();}return;}
 if(rf.screen==4){UBYTE timing=rf_camera_clock_step();if(rf.focus>=45)rf.stress=0;if(timing&4)rf_photo_dirty=1;if(timing&1){UBYTE b=rf_species_rule(rf.species,0),cycle=(rf_behavior_clock/rf_species_rule(rf.species,1))&3;
 if(b==3){rf_subject_x=cycle==1?1:cycle==3?-1:0;}
 else if(b==6){rf_subject_x=cycle<2?0:1;rf_subject_y=0;}
 else if(b==7){rf_subject_x=cycle==1?2:cycle==2?1:0;}
 else if(b==11){rf_subject_y=0;rf_subject_x=cycle==1?1:cycle==2?2:0;}
 else if(b==4){rf_subject_y=cycle==1?-1:0;rf_subject_x=cycle==1?1:0;}
 else if(b==8){rf_hidden=cycle==1;rf_subject_y=cycle==2?-1:0;}
 else if(b==9){rf_hidden=cycle==1;rf_subject_x=cycle==2?1:0;}
 else if(b==10){rf_subject_y=cycle==1?-1:0;}
 rf_photo_dirty=1;}if(timing||rf_photo_dirty)photo();
 if(keys&J_SELECT){if(rf_lens_toggle()){rf.focus=0;rf_photo_dirty=1;save();photo();rf_camera_clock_focus_reset();}else line(13,"FILE A CHAPTER FIRST");return;}if(keys&J_B){rf.screen=2;world();return;}if(keys&15){UBYTE approached=(keys&J_DOWN)&&rf.distance>rf_species_rule(rf.species,2);rf_photo_dirty=1;if(keys&J_LEFT&&rf.aim>-3)rf.aim--;if(keys&J_RIGHT&&rf.aim<3)rf.aim++;if(keys&J_UP&&rf.distance<4)rf.distance++;if(keys&J_DOWN&&rf.distance>rf_species_rule(rf.species,2))rf.distance--;rf_camera_clock_focus_reset();if(approached&&rf_species_rule(rf.species,0)!=0&&rf_species_rule(rf.species,0)!=1){rf.stress++;if(rf.stress>=rf_species_rule(rf.species,3)){if(rf_species_rule(rf.species,0)==2){rf_wedged=95;rf_bonus_disturbed=1;rf.stress=0;}else{rf.score=0;rf.screen=5;result();return;}}}photo();}if(keys&J_A){if(rf_wedged||rf_hidden){line(14,"WAIT. IT IS HIDING.");return;}{RFPhotoQuality q;quality_observation(&q);rf.score=rf_photo_quality_score(&q);}if(rf_lens_should_replace(rf.score,rf.best[rf.species],rf.photo_snapshot[rf.species])){rf.best[rf.species]=rf.score;rf.photo_distance[rf.species]=rf.distance;rf.photo_aim[rf.species]=rf.aim;rf.photo_phase[rf.species]=rf.phase;rf.photo_map[rf.species]=rf.room;rf.photo_snapshot[rf.species]=144|rf_lens_snapshot_bit()|(rf_subject_x+1)|((rf_subject_y+1)<<2)|((rf_motion&1)<<3);rf_conditions_record(rf.species,rf_conditions_current());}rf_challenge_record();rf_journal_photo(rf.quest_flags,rf.species,rf_spots[rf.spot].id,rf.phase,rf.score,rf.distance,rf.focus);if(rf_campaign_photo(rf.quest_flags,rf.species,rf_spots[rf.spot].id,rf.phase,rf.score,rf.distance,rf.focus))*spot_flags(rf.spot)|=128;recount();save();rf.screen=5;sound(1);result();}return;}
 if(rf.screen==5){if(keys&(J_A|J_B)){rf.screen=2;world();}return;}
 if(rf.screen==7||rf.screen==8||rf.screen==10){i=rf_guide_input(keys);if(i==2)world();else if(i==9)station();else if(i==25)fieldkit();return;}
 if(rf.screen==12){if(keys&J_SELECT){rf_region_open(rf_world_trailhead(rf.travel),9);rf.screen=30;rf_ui_region_map();return;}if(keys&J_B){rf.screen=9;station();return;}if(keys&15){if(keys&(J_RIGHT|J_DOWN))rf.travel=rf_atlas_step(1);else rf.travel=rf_atlas_step(0);atlas();}if(keys&J_A){UWORD next=rf_world_trailhead(rf.travel);if(rf_world_transition(rf.room,next)){rf.travel=next;rf_dx=1;rf.screen=16;clear();line(1,"    ISLAND FERRY");line(4,"SEPARATE ISLANDS,");line(5,"DIFFERENT HOMES.");line(13,"A: BOARD THE FERRY");line(15,"B: KEEP EXPLORING");return;}departure();rf.room=next;rf.x=0;rf.y=3;rf.screen=2;world();save();}return;}
 if(rf.screen==17){if(keys&J_LEFT){rf_region_open(rf.room,17);rf.screen=30;rf_ui_region_map();return;}if(keys&J_SELECT){rf_challenge=rf_map.district*2;rf.screen=26;challenges();return;}if(keys&J_B){rf.screen=9;station();return;}if(keys&J_A&&rf_c_stage<3){rf_c_choice=0;rf.screen=18;campaign_question();return;}if(keys&J_START&&rf_c_stage<3){rf_c_kind=rf_campaign_turn_in(rf.quest_flags,rf_c_district)?4:5;save();rf.screen=19;campaign_feedback();}return;}
 if(rf.screen==18){if(keys&J_B){rf.screen=17;campaign();return;}if(keys&(J_UP|J_DOWN)){rf_c_choice=(rf_c_choice+(keys&J_DOWN?1:2))%3;campaign_question();}if(keys&J_A){rf_c_kind=rf_campaign_answer(rf.quest_flags,rf_c_district,rf_c_choice)?7:6;save();rf.screen=19;campaign_feedback();}return;}
 if(rf.screen==19){if(keys&(J_A|J_B)){rf.screen=17;campaign();}return;}
 if(rf.screen==33||rf.screen==34){if(rf_gallery_input(keys)==20)exhibit();return;}
 if(rf.screen==20){if(keys&J_SELECT){rf_gallery_begin(rf_map.district);return;}if(keys&J_B){rf.screen=9;station();return;}if(keys&J_A&&rf_campaign_chapters(rf.quest_flags)==15){rf_c_choice=0;if(rf_campaign_finale_complete(rf.quest_flags)){rf.screen=22;credits();}else{rf.screen=21;finale_question();}return;}if(keys&J_START&&rf_campaign_finale_complete(rf.quest_flags)){rf_campaign_hidden_clue(rf.quest_flags);rf_campaign_unlock_hidden(rf.quest_flags,regular_count());save();rf.screen=23;secret();}return;}
 if(rf.screen==21){if(keys&J_B){rf.screen=20;exhibit();return;}if(keys&(J_UP|J_DOWN)){rf_c_choice=(rf_c_choice+(keys&J_DOWN?1:2))%3;finale_question();}if(keys&J_A){if(rf_campaign_finale_answer(rf.quest_flags,rf_c_choice)){save();rf.screen=20;exhibit();}else line(14,"COMPARE THE FOLDERS.");}return;}
 if(rf.screen==22){if(keys&(J_A|J_B)){rf_campaign_ack_credits(rf.quest_flags);save();rf.screen=20;exhibit();}return;}
 if(rf.screen==23){if(keys&J_B){rf.screen=20;exhibit();return;}if(keys&J_A){rf_c_choice=0;rf.screen=24;secret_question();}return;}
 if(rf.screen==24){if(keys&J_B){rf.screen=23;secret();return;}if(keys&(J_UP|J_DOWN)){rf_c_choice=(rf_c_choice+(keys&J_DOWN?1:2))%3;secret_question();}if(keys&J_A){if(rf_campaign_hidden_answer(rf.quest_flags,rf_c_choice)){rf_campaign_unlock_hidden(rf.quest_flags,regular_count());save();rf.screen=23;secret();}else line(14,"LEAVE THE HOME SAFE.");}return;}
 if(rf.screen==16){if(keys&J_B){rf.screen=2;world();return;}if(keys&J_A){departure();rf.room=rf.travel;rf.x=rf_dx<0?9:0;rf.y=3;rf.screen=2;world();save();}return;}
 if(rf.screen==13){if(keys&J_B){rf.screen=9;station();return;}if(keys&J_A){rf_j_stage=rf_journal_stage(rf.quest_flags);if(rf_j_stage<5){rf_j_choice=0;rf.screen=14;journal_question();}return;}if(keys&J_START){sync_journal_rocks();rf_j_stage=rf_journal_stage(rf.quest_flags);rf_j_kind=rf_journal_turn_in(rf.quest_flags)?4:5;save();rf.screen=15;journal_feedback();}return;}
 if(rf.screen==14){if(keys&J_B){rf.screen=13;journal();return;}if(keys&(J_UP|J_DOWN)){rf_j_choice=(rf_j_choice+(keys&J_DOWN?1:2))%3;journal_question();}if(keys&J_A){rf_j_kind=rf_journal_answer(rf.quest_flags,rf_j_choice)?7:6;save();rf.screen=15;journal_feedback();}return;}
 if(rf.screen==15){if(keys&(J_A|J_B)){rf.screen=13;journal();}return;}
 if(rf.screen==27){
  if(keys&J_B){rf.screen=9;station();return;}
  if(keys&(J_UP|J_DOWN)){rf_forecast_field=(rf_forecast_field+(keys&J_DOWN?1:2))%3;rf_conditions_forecast();return;}
  if(keys&(J_LEFT|J_RIGHT)){UBYTE d=keys&J_RIGHT?1:3;if(rf_forecast_field==0)rf_forecast_phase=(rf_forecast_phase+(keys&J_RIGHT?1:2))%3;else if(rf_forecast_field==1)rf_forecast_weather=(rf_forecast_weather+d)&3;else rf_forecast_season=(rf_forecast_season+d)&3;rf_conditions_forecast();return;}
  if(keys&J_A){departure();rf.phase=rf_forecast_phase;rf.quest_flags[9]=(rf.quest_flags[9]&225)|((rf_forecast_weather|(rf_forecast_season<<2))<<1);for(i=0;i<rf_map.spot_count;i++)if(!(*spot_flags(i)&1))*spot_flags(i)&=30;save();rf.screen=2;world();return;}
  return;
 }
 if(rf.screen==9){if(keys&J_DOWN){rf.screen=17;campaign();return;}if(keys&J_LEFT){rf.screen=20;exhibit();return;}if(keys&J_START){rf.quest_flags[9]^=128;rf_audio_mute((rf.quest_flags[9]&128)!=0);save();station();return;}if(keys&J_UP){sync_journal_rocks();rf.screen=13;journal();return;}if(keys&J_RIGHT){rf.travel=rf_map.district;rf.screen=12;atlas();return;}if(keys&J_B){rf.screen=2;world();return;}if(keys&J_SELECT){rf_guide_open(rf.screen);return;}if(keys&J_A){UBYTE c=rf_conditions_current();rf_forecast_phase=(rf.phase+1)%3;rf_forecast_weather=c&3;rf_forecast_season=c>>2;rf_forecast_field=0;rf.screen=27;rf_conditions_forecast();return;}}
}
