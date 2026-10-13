#pragma bank 255
#include "rockflip_gallery.h"
#include "rockflip_runtime.h"
#include "rockflip_campaign.h"
#include "rockflip_guide_ui.h"
#include "rockflip_art.h"
#include <gb/cgb.h>
#ifndef RF_GALLERY_ISOLATED
#include "actor.h"
#endif
/* Two transient navigation bytes; no new progress/metadata or browse rewards. */
UBYTE rf_gallery_district,rf_gallery_pair;
#include "rockflip_gallery_data.h"
static const UBYTE attrs[20]={7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7};
static void text(UBYTE x,UBYTE y,const char*s){UBYTE tiles[20],n=0;while(*s&&x+n<20)tiles[n++]=*s++-32;if(n){VBK_REG=0;set_bkg_tiles(x,y,n,1,tiles);VBK_REG=1;set_bkg_tiles(x,y,n,1,attrs);}VBK_REG=0;}
static void line(UBYTE y,const char*s){UBYTE tiles[20],n=0;while(n<20){tiles[n++]=*s?*s++-32:0;}VBK_REG=0;set_bkg_tiles(0,y,20,1,tiles);VBK_REG=1;set_bkg_tiles(0,y,20,1,attrs);VBK_REG=0;}
static void clear(void){UBYTE y;HIDE_SPRITES;rf_art_font();
#ifndef RF_GALLERY_ISOLATED
PLAYER.flags|=ACTOR_FLAG_HIDDEN;
#endif
for(y=0;y<18;y++)line(y,"");}
UBYTE rf_gallery_subject(UBYTE district,UBYTE pair) BANKED{if(district>=16||pair>=2)return 255;if(rf.quest_flags[8]&2)return fresh_subjects[district][pair];return subjects[district][pair];}
UBYTE rf_gallery_photo_ready(UBYTE district,UBYTE pair) BANKED{UBYTE sid=rf_gallery_subject(district,pair);if(sid==255)return 0;if(rf_campaign_stage(rf.quest_flags,district)<3)return 0;if(rf.best[sid]<2)return 0;return 1;}
void rf_gallery_draw(void) BANKED{
 UBYTE i,d,sid,old,cluster=rf_gallery_district/4;char b[21];RFMap m;
 clear();
 if(rf.screen==33){
  line(0,"GROWING EXHIBIT");rf_campaign_chapter_text(cluster,0,b);line(2,b);
  for(i=0;i<4;i++){d=cluster*4+i;text(0,5+i*2,d==rf_gallery_district?">":" ");text(1,5+i*2,rf_campaign_stage(rf.quest_flags,d)>=3?"*":".");text(2,5+i*2,overview_titles[d]);}
  if(rf_campaign_chapters(rf.quest_flags)&(1<<cluster)){rf_campaign_chapter_text(cluster,1,b);line(13,b);line(14,"FOUR STORIES CONNECT");}
  else{line(13,"FILED REGIONS GROW.");line(14,"* = STORY FILED");}
  line(15,"UP/DOWN: CHAPTER");line(16,"L/R: REGION A: VIEW");line(17,"B: EXHIBIT");return;
 }
 d=rf_gallery_district;sid=rf_gallery_subject(d,rf_gallery_pair);
 if(rf_gallery_photo_ready(d,rf_gallery_pair)){
  old=rf.guide;rf.guide=sid;rf_guide_album_picture();rf.guide=old;
  line(0,titles[d]);line(1,rangers[d]);rf_art_name(sid,b);line(2,b);line(3,"SAVED FIELD PHOTO");
  rf_world_load(rf.photo_map[sid],&m);line(11,m.name);
 }else{
  line(0,titles[d]);line(1,rangers[d]);line(3,"A PLACE FOR EVIDENCE");
  if(rf_campaign_stage(rf.quest_flags,d)<3){line(6,"FILE THIS REGION'S");line(7,"THREE FIELD PAGES.");}
  else{line(6,"NO MATCHING PHOTO.");line(7,"TWO STARS ARE ENOUGH");}
  line(9,"THIS FRAME IS EMPTY");
 }
 if(rf.quest_flags[8]&2){line(12,fresh_themes[d]);line(13,fresh_responses[d][0]);line(14,fresh_responses[d][1]);}else{line(12,themes[d]);line(13,responses[d][0]);line(14,responses[d][1]);}
 line(15,rf_gallery_pair?"SELECT: FIRST PHOTO":"SELECT: OTHER PHOTO");line(16,"L/R: REGION");line(17,"B: CHAPTER GALLERY");
}
void rf_gallery_begin(UBYTE district) BANKED{rf_gallery_district=district<16?district:0;rf_gallery_pair=0;rf.screen=33;rf_gallery_draw();}
UBYTE rf_gallery_input(UBYTE keys) BANKED{
 UBYTE c=rf_gallery_district/4,r=rf_gallery_district%4;
 if(keys&J_B){if(rf.screen==34){rf.screen=33;rf_gallery_draw();return 0;}rf.screen=20;return 20;}
 if(rf.screen==33){
  if(keys&(J_UP|J_DOWN)){c=(c+((keys&J_UP)?3:1))%4;rf_gallery_district=c*4+r;rf_gallery_draw();return 0;}
  if(keys&J_A){rf.screen=34;rf_gallery_pair=0;rf_gallery_draw();return 0;}
 }else if(keys&J_SELECT){rf_gallery_pair^=1;rf_gallery_draw();return 0;}
 if(keys&(J_LEFT|J_RIGHT)){r=(r+((keys&J_LEFT)?3:1))%4;rf_gallery_district=c*4+r;rf_gallery_pair=0;rf_gallery_draw();}
 return 0;
}
