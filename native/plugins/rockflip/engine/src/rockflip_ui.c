#pragma bank 255
#include "rockflip_art.h"
#include "rockflip_ui.h"
#include "rockflip_runtime.h"
#include "rockflip_conditions.h"
#include "rockflip_save.h"
#include "rockflip_ranger.h"
#include "rockflip_camp_route.h"
#include "rockflip_challenges.h"
#include "actor.h"
#include "rockflip_journal.h"
#include "rockflip_campaign.h"
#include "rockflip_campaign_variant.h"
#include <string.h>
#include <gb/cgb.h>
static const char *phases[]={"DAY","DUSK","NIGHT"};
static void cell(UBYTE x,UBYTE y,UBYTE tile,UBYTE attr){VBK_REG=0;set_bkg_tiles(x,y,1,1,&tile);VBK_REG=1;set_bkg_tiles(x,y,1,1,&attr);VBK_REG=0;}
/* Staged exact text renderer; cell() remains unchanged for mixed-palette art.
 * Local tilebuf20bytes, constantattributes inROM, no new persistentWRAM.
 * All exits restore VRAMbank0. Text is clipped exactly at native column20.
 */
static const UBYTE rf_row_attributes[20]={7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7};
static const UBYTE rf_blank_row[20]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static void row_write(UBYTE x,UBYTE y,UBYTE count,const UBYTE*tiles){
 if(count){VBK_REG=0;set_bkg_tiles(x,y,count,1,tiles);VBK_REG=1;set_bkg_tiles(x,y,count,1,rf_row_attributes);}
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
 UBYTE y;HIDE_SPRITES;rf_art_font();PLAYER.flags|=ACTOR_FLAG_HIDDEN;
 for(y=0;y<18;y++)row_write(0,y,20,rf_blank_row);
}

static void number(UBYTE x,UBYTE y,UBYTE n){char s[4];s[0]='0'+n/100;s[1]='0'+(n/10)%10;s[2]='0'+n%10;s[3]=0;text(x,y,s);}
void rf_ui_station(void) BANKED{UBYTE i;clear();rf_ranger_portrait(rf_map.district,rf_campaign_stage(rf.quest_flags,rf_map.district)>=3);for(i=0;i<36;i++)cell(1+i%6,2+i/6,128+i,13);line(1,"  RANGER FIELD CAMP");line(8,rf_store_locked?"NEWER SAVE: READ ONLY":"PHOTOS SAVED.");text(9,3,"PHOTOS:");number(9,4,rf.count);text(12,4,"/");number(13,4,RF_SPECIES_COUNT);text(9,6,"CARE:");number(14,6,rf.points);line(9,"A: FORECAST / REST");{char c[21];rf_conditions_label(rf_conditions_current(),c);line(10,c);}line(11,"SELECT: FIELD GUIDE");line(12,"RIGHT: EXPEDITIONS");line(13,"UP:INTRO DOWN:NOTES");line(14,"LEFT: EXHIBIT");line(15,"START: MUSIC ON/OFF");line(17,"B: RETURN TO TRAIL");}
void rf_ui_fieldkit(void) BANKED{char b[21];UWORD camp,next;UBYTE dir;RFMap m;clear();line(0,"    FIELD PACK");line(2,rf_store_locked?"NEWER SAVE: READ ONLY":"YOUR PHOTOS ARE SAVED");line(4,rf_map.name);line(6,"RANGER CAMPS OFFER");line(7,"REST, NOTES, TRAVEL.");rf_conditions_label(rf_conditions_current(),b);line(8,b);if(rf_camp_route(rf.room,&camp,&next,&dir)){rf_camp_route_hint(rf.room,b);line(10,b);rf_world_load(camp,&m);line(12,m.name);}else{line(10,"RIGHT: RETURN HIKE");line(12,"TO THE COAST CAMP.");}line(14,"A: PHOTO CHALLENGES");line(15,"SELECT: FIELD GUIDE");line(16,"UP: NOTES LEFT: MAP");line(17,"B/START: KEEP HIKING");}
void rf_ui_challenges(void) BANKED{UBYTE i;char b[21];RFMap m;clear();line(0,"   PHOTO CHALLENGES");rf_challenge_text(rf_challenge,0,0,b);line(2,b);line(3,rf_challenge_complete(rf.best,rf_challenge)?"THREE-STAR PAGE DONE":"A NATURAL MOMENT");for(i=0;i<2;i++){rf_challenge_text(rf_challenge,1,i,b);line(5+i,b);}for(i=0;i<3;i++){rf_challenge_text(rf_challenge,2,i,b);line(8+i,b);}rf_challenge_text(rf_challenge,3,0,b);line(11,b);if(rf_challenge==10)line(12,"RAIN / COOL SEASON");rf_world_load(rf_challenge_map(rf_challenge),&m);line(13,m.name);text(0,14,"LOOK AT:");text(9,14,phases[rf_challenge_phase(rf_challenge)]);line(16,"LEFT/RIGHT: NEXT");line(17,"B: BACK TO PACK");}
static UBYTE regular_count(void){UBYTE i,n=0;for(i=0;i<150&&i<RF_SPECIES_COUNT;i++)if(rf.best[i])n++;return n;}
void rf_ui_journal(void) BANKED{UBYTE i,stage=rf_journal_stage(rf.quest_flags);char buf[21];clear();line(0,"NELL'S FIELD JOURNAL");rf_journal_text(stage,0,0,buf);line(2,buf);for(i=0;i<5;i++){rf_journal_text(stage,1,i,buf);line(4+i,buf);}line(10,"PHOTO + NOTE + CARE");line(12,"A: WRITE A NOTE");line(13,"START: FILE EVIDENCE");line(16,"B: RETURN TO CAMP");if(stage>=5)line(12,"MORE TRAILS TO STUDY");}
void rf_ui_journal_question(void) BANKED{UBYTE i;char buf[21];clear();line(0,"WHAT DID YOU NOTICE?");for(i=0;i<3;i++){rf_journal_text(rf_j_stage,2,i,buf);line(2+i,buf);}for(i=0;i<3;i++){rf_journal_text(rf_j_stage,3,i,buf);text(0,7+i*2,i==rf_j_choice?">":" ");text(1,7+i*2,buf);}line(15,"UP/DOWN: CHOOSE");line(16,"A: NOTE  B: JOURNAL");}
void rf_ui_journal_feedback(void) BANKED{UBYTE i;char buf[21];clear();line(0,"RANGER NELL");if(rf_j_kind==6){line(4,"LOOK AGAIN AT THE");line(5,"ANIMAL AND ITS HOME.");line(7,"TRY ANOTHER NOTE.");}else if(rf_j_kind==7){line(4,"NOTE ADDED.");line(6,"FILE YOUR EVIDENCE");line(7,"WHEN YOU ARE READY.");}else for(i=0;i<12;i++){rf_journal_text(rf_j_stage,rf_j_kind,i,buf);line(2+i,buf);}line(17,"A/B: FIELD JOURNAL");}
void rf_ui_campaign(void) BANKED{UBYTE i;char b[21];rf_c_district=rf_map.district;rf_c_stage=rf_campaign_stage(rf.quest_flags,rf_c_district);clear();rf_campaign_ranger(rf_c_district,b);line(0,b);if(rf_c_stage>=3){line(3,"REGIONAL STORY FILED");for(i=0;i<2;i++){rf_campaign_text(rf_c_district,2,4,i,b);line(5+i,b);}line(10,"OTHER HOMES AWAIT.");}else{rf_campaign_text(rf_c_district,rf_c_stage,0,0,b);line(2,b);for(i=0;i<2;i++){rf_campaign_text(rf_c_district,rf_c_stage,1,i,b);line(4+i,b);}{UBYTE wet=255;if(rf_c_district==1&&rf_c_stage==0)wet=118;else if(rf_c_district==5&&(rf_c_stage==0||rf_c_stage==2))wet=9;else if(rf_c_district==6&&rf_c_stage==2)wet=124;if(wet!=255){rf_conditions_clue(wet,0,b);line(6,b);rf_conditions_clue(wet,1,b);line(7,b);}}line(9,"A: COMPARE NOTES");line(11,"START: FILE EVIDENCE");line(12,"LOOK NEAR:");rf_campaign_route_hint(0,b);line(13,b);rf_campaign_route_hint(1,b);line(14,b);}line(15,"SELECT: CHALLENGES");line(16,"LEFT: TRAIL SKETCH");line(17,"B: RETURN TO CAMP");}
void rf_ui_campaign_question(void) BANKED{UBYTE i;char b[21];clear();line(0,"COMPARE EVIDENCE");for(i=0;i<2;i++){rf_campaign_text(rf_c_district,rf_c_stage,2,i,b);line(3+i,b);}for(i=0;i<3;i++){rf_campaign_text(rf_c_district,rf_c_stage,3,i,b);text(0,7+i*2,i==rf_c_choice?">":" ");text(1,7+i*2,b);}line(15,"UP/DOWN: CHOOSE");line(17,"A: NOTE B: RETURN");}
void rf_ui_campaign_feedback(void) BANKED{UBYTE i;char b[21];clear();if(rf_c_kind==6){line(4,"LOOK AT THE HABITAT.");line(6,"TRY ANOTHER CAPTION.");}else if(rf_c_kind==7){line(4,"FIELD NOTE ADDED.");line(6,"FILE WHEN READY.");}else{for(i=0;i<2;i++){rf_campaign_text(rf_c_district,rf_c_stage,rf_c_kind,i,b);line(4+i,b);}if(rf_c_kind==4)line(8,"REGIONAL PAGE FILED.");}line(17,"A/B: FIELD PAGES");}
void rf_ui_exhibit(void) BANKED{UBYTE i,mask=rf_campaign_chapters(rf.quest_flags);char b[21];clear();line(0,"STATEWIDE EXHIBIT");for(i=0;i<4;i++){rf_campaign_chapter_text(i,0,b);text(0,3+i*2,mask&(1<<i)?"*":".");text(1,3+i*2,b);}if(mask!=15)line(12,"FILE ALL16 STORIES.");else if(rf_campaign_finale_complete(rf.quest_flags)){line(12,"YOUR EXHIBIT IS OPEN");line(14,"A: CREDITS");line(15,"START: A LAST CLUE");}else{line(12,"MATCH FOUR CAPTIONS.");line(14,"A: ARRANGE EXHIBIT");}line(16,"SELECT: PHOTO WALL");line(17,"B: RETURN TO CAMP");}
void rf_ui_finale_question(void) BANKED{UBYTE i,q=rf_campaign_finale_stage(rf.quest_flags);char b[21];clear();line(0,"ARRANGE YOUR EXHIBIT");for(i=0;i<2;i++){rf_campaign_finale_text(q,0,i,b);line(3+i,b);}for(i=0;i<3;i++){rf_campaign_finale_text(q,1,i,b);text(0,7+i*2,i==rf_c_choice?">":" ");text(1,7+i*2,b);}line(15,"UP/DOWN: CHOOSE");line(17,"A: CAPTION B: BACK");}
void rf_ui_credits(void) BANKED{UBYTE i;char b[21];clear();for(i=0;i<4;i++){rf_campaign_finale_text(0,2,i,b);line(1+i,b);}for(i=0;i<5;i++){rf_campaign_finale_text(0,3,i,b);line(7+i,b);}line(14,"YOUR HIKE CONTINUES.");line(17,"A/B: RETURN TO TRAIL");}
void rf_ui_secret(void) BANKED{UBYTE i;char b[21];clear();line(0,"A LAST FIELD PAGE");for(i=0;i<3;i++){rf_campaign_hidden_text(0,i,b);line(3+i,b);}line(8,"REGULAR PHOTOS:");number(16,8,regular_count());if(rf_campaign_hidden_ready(rf.quest_flags)){line(11,"UNMARKED TRAIL OPEN");line(13,"SEE EXPEDITIONS.");}else line(11,"150 PHOTOS + CAPTION");line(15,"A: CONSIDER THE CLUE");line(17,"B: EXHIBIT");}
void rf_ui_secret_question(void) BANKED{UBYTE i;char b[21];clear();for(i=0;i<2;i++){rf_campaign_hidden_text(1,i,b);line(2+i,b);}for(i=0;i<3;i++){rf_campaign_hidden_text(2,i,b);text(0,7+i*2,i==rf_c_choice?">":" ");text(1,7+i*2,b);}line(15,"UP/DOWN: CHOOSE");line(17,"A: NOTE B: CLUE");}
void rf_ui_atlas(void) BANKED{UBYTE i,id,total=(rf.quest_flags[31]&128)?17:16;RFMap m;clear();line(0,"    EXPEDITIONS");line(1,"SELECT: TRAIL SKETCH");for(i=0;i<6;i++){id=(rf.travel/6)*6+i;if(id>=total)break;rf_world_load(rf_world_trailhead(id),&m);text(0,3+i*2,id==rf.travel?">":" ");text(1,3+i*2,id==16?"UNMARKED TRAIL":m.name);}line(15,"D-PAD: CHOOSE REGION");line(16,"A: HIKE FROM CAMP");line(17,"B: RETURN");}
