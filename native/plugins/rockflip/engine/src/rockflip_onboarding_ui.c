#pragma bank 255
#include "rockflip_art.h"
#include "rockflip_onboarding_ui.h"
#include "rockflip_runtime.h"
#include "rockflip_ranger.h"
#include "rockflip_journal.h"
#include "rockflip_campaign.h"
#include "rockflip_campaign_variant.h"
#include "rockflip_conditions.h"
#include <gb/cgb.h>
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
 UBYTE y;HIDE_SPRITES;rf_art_font();
 for(y=0;y<18;y++)row_write(0,y,20,rf_blank_row);
}
static const char titles[3][21]={"WELCOME TO ROCK FLIP","A HOME BELOW","BRING BACK A NOTE"};
static const char asides[3][3][13]={{"HI, I'M NELL","FIELD RANGER","LET'S HIKE."},{"FIRST NOTES:","DAYLIGHT.","TORTOISE."},{"OUR FIRST","STORY STARTS","WITH A HOME."}};
static const char bodies[3][4][21]={{"16 DISTRICTS AWAIT.","DESERTS TO COASTS.","PHOTOS TELL STORIES.","BUILD YOUR EXHIBIT."},{"LOOK BY A BURROW.","KEEP SPACE FOUR.","HOLD STILL TO FOCUS.","A: TAKE ITS PHOTO."},{"RETURN TO MY CAMP.","UP: OPENING JOURNAL","COMPARE THE SHELTER.","PUT EVERY ROCK BACK."}};

static void cell(UBYTE x,UBYTE y,UBYTE tile,UBYTE attr){VBK_REG=0;set_bkg_tiles(x,y,1,1,&tile);VBK_REG=1;set_bkg_tiles(x,y,1,1,&attr);VBK_REG=0;}
void rf_ui_welcome(UBYTE page) BANKED {
 UBYTE i;static const UBYTE body_rows[4]={9,11,12,14};
 if(page>2)page=2;clear();line(0,titles[page]);
 rf_ranger_portrait(0,0);
 for(i=0;i<36;i++)cell(1+i%6,2+i/6,128+i,13);
 for(i=0;i<3;i++)text(8,2+i*2,asides[page][i]);
 for(i=0;i<4;i++)line(body_rows[i],bodies[page][i]);
 line(17,page==2?"A:HIKE B:SKIP":"A:NEXT B:SKIP");
}
void rf_ui_pinned_notes(void) BANKED {
 UBYTE i,stage=rf_journal_stage(rf.quest_flags),district=rf_map.district,wet=255;char b[21];
 clear();line(0,"CURRENT FIELD NOTES");
 if(stage<5&&district==0){
  line(1,"NELL'S FIRST SURVEY");rf_journal_text(stage,0,0,b);line(3,b);
  for(i=0;i<5;i++){rf_journal_text(stage,1,i,b);line(5+i,b);}
 }else{
  stage=rf_campaign_stage(rf.quest_flags,district);rf_campaign_ranger(district,b);line(1,b);
  if(stage>=3){line(3,"REGIONAL STORY FILED");for(i=0;i<2;i++){rf_campaign_text(district,2,4,i,b);line(5+i,b);}line(9,"PHOTO CHALLENGES WAIT");}
  else{
   rf_campaign_text(district,stage,0,0,b);line(3,b);
   for(i=0;i<2;i++){rf_campaign_text(district,stage,1,i,b);line(5+i,b);}
   if(district==1&&stage==0)wet=118;else if(district==5&&(stage==0||stage==2))wet=9;else if(district==6&&stage==2)wet=124;
   if(wet!=255){rf_conditions_clue(wet,0,b);line(8,b);rf_conditions_clue(wet,1,b);line(9,b);}
  }
 }
 if(rf_journal_stage(rf.quest_flags)<5&&district==0){line(11,"COMPARE HOMES, THEN");line(12,"FILE NOTES AT CAMP.");}else{line(11,"LOOK NEAR:");rf_campaign_route_hint(0,b);line(12,b);rf_campaign_route_hint(1,b);line(13,b);line(16,"FILE AT RANGER CAMP");}
 line(14,"PLAN WEATHER AT CAMP");line(17,"B: BACK TO PACK");
}
