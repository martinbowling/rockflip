#pragma bank 255
#include "rockflip_guide_ui.h"
#include "rockflip_guide.h"
#include "rockflip_runtime.h"
#include "rockflip_art.h"
#include "rockflip_conditions.h"
#include "actor.h"
#include <gb/cgb.h>
/* Four transientbytes; no save schema changes or duplicate seen bitset. */
static UBYTE filter,page,origin,empty;
static const char filter_names[5][21]={"ALL","UNPHOTOGRAPHED","SEEN","PHOTOGRAPHED","CURRENT DISTRICT"};
static const char *phases[]={"DAY","DUSK","NIGHT"};
static const UBYTE attrs[20]={7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7};
static const UBYTE blanks[20]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static void cell(UBYTE x,UBYTE y,UBYTE t,UBYTE a){VBK_REG=0;set_bkg_tiles(x,y,1,1,&t);VBK_REG=1;set_bkg_tiles(x,y,1,1,&a);VBK_REG=0;}
/* Same bounded bulk-row algorithm as current validated main/UI source. */
static void row_write(UBYTE x,UBYTE y,UBYTE n,const UBYTE*t){if(n){VBK_REG=0;set_bkg_tiles(x,y,n,1,t);VBK_REG=1;set_bkg_tiles(x,y,n,1,attrs);}VBK_REG=0;}
static void text(UBYTE x,UBYTE y,const char*s){UBYTE tilebuf[20],n=0;while(*s&&x+n<20){tilebuf[n++]=*s>=32?*s-32:31;s++;}row_write(x,y,n,tilebuf);}
static void line(UBYTE y,const char*s){row_write(0,y,20,blanks);text(0,y,s);}
static void number(UBYTE x,UBYTE y,UBYTE v){char b[4];b[0]='0'+v/100;b[1]='0'+v/10%10;b[2]='0'+v%10;b[3]=0;text(x,y,b);}
static void clear(void){UBYTE y;HIDE_SPRITES;rf_art_font();for(y=0;y<18;y++)row_write(0,y,20,blanks);}
static UBYTE match(UBYTE s){return rf_guide_match(s,filter,rf_map.district,rf.best,rf.spot_state);}
static void select_valid(void){UBYTE n;empty=0;if(match(rf.guide))return;n=rf_guide_next(150,0,filter,rf_map.district,rf.best,rf.spot_state);if(n==255){empty=1;return;}rf.guide=n;}
void rf_guide_grid(void) BANKED {
 UBYTE s,rank=0,total,start,slot=0,x,y,k;clear();select_valid();total=rf_guide_count(filter,rf_map.district,rf.best,rf.spot_state);
 line(0,"FIELD GUIDE");line(1,filter_names[filter]);number(16,0,total);
 if(empty){line(6,"NO MATCHING PAGES.");line(8,"SELECT: NEXT FILTER");}
 else{
  for(s=0;s<rf.guide;s++)if(match(s))rank++;
  start=(rank/6)*6;rank=0;
  for(s=0;s<151&&slot<6;s++)if(match(s)){
   if(rank++<start)continue;x=2+(slot%3)*6;y=3+(slot/3)*6;
   if(s==150&&!rf.best[150]){for(k=0;k<4;k++)cell(x+(k&1),y+(k>>1),31,7);text(x,y+2,"????");}
   else{rf_art_icon(s,!rf.best[s],slot);for(k=0;k<4;k++)cell(x+(k&1),y+(k>>1),64+slot*4+k,8+slot);text(x,y+2,rf.best[s]?"PHOTO":rf_guide_seen(s,rf.best,rf.spot_state)?"SEEN":"????");}
   text(x,y+3,"...");for(k=0;k<rf.best[s];k++)text(x+k,y+3,"*");if(s==rf.guide)text(x-1,y,">");slot++;
  }
 }
 line(14,"SELECT: FILTER");line(15,"D-PAD: PAGE/CHOOSE");line(16,"A:FACTS START:ALBUM");line(17,origin==9?"B: BACK TO CAMP":origin==25?"B: BACK TO PACK":"B: BACK TO TRAIL");
}
void rf_guide_open(UBYTE from) BANKED {origin=from;if(origin!=2&&origin!=9&&origin!=25)origin=2;filter=page=empty=0;rf.screen=7;rf_guide_grid();}
static void header(void){UBYTE i;char b[21];for(i=0;i<2;i++){rf_guide_text(rf.guide,0,i,b);line(i,b);rf_guide_text(rf.guide,1,i,b);line(i+2,b);}}
static void paragraph(UBYTE kind,UBYTE row){UBYTE i,n=rf_guide_lines(rf.guide,kind);char b[21];for(i=0;i<n&&row+i<15;i++){rf_guide_text(rf.guide,kind,i,b);line(row+i,b);}}
void rf_guide_detail(UBYTE album) BANKED {
 UBYTE i;char b[21];RFMap m;clear();
 /* Every text/image/range path is guarded before any hidden identity access. */
 if(rf.guide==150&&!rf.best[150]){line(0,"UNWRITTEN FIELD PAGE");line(6,"PHOTO TO REVEAL.");line(17,"B: GUIDE");return;}
 header();
 if(album){
  if(rf.best[rf.guide]){rf_guide_album_picture();line(12,"BEST FIELD PHOTO");for(i=0;i<rf.best[rf.guide];i++)text(17+i,12,"*");rf_world_load(rf.photo_map[rf.guide],&m);line(13,m.name);line(14,"TAKEN AT:");text(10,14,phases[rf.photo_phase[rf.guide]]);if(!(rf.photo_snapshot[rf.guide]&128))line(15,"LEGACY POSE UNKNOWN");else if(!(rf.photo_snapshot[rf.guide]&16))line(15,"OLD WEATHER UNKNOWN");else{rf_conditions_label(rf_conditions_photo(rf.guide),b);line(15,b);}}
  else{line(6,"NO PHOTO YET.");line(8,"WATCH HABITAT/TIME.");}
  line(16,"LEFT/RIGHT: SPECIES");line(17,"A:FACTS B:GUIDE");return;
 }
 if(page==0){
  if(rf.best[rf.guide]){rf_guide_album_picture();line(11,"PHOTOGRAPHED");for(i=0;i<rf.best[rf.guide];i++)text(17+i,11,"*");}
  else line(9,rf_guide_seen(rf.guide,rf.best,rf.spot_state)?"SEEN; PHOTO AWAITS.":"NO PHOTO YET.");
  paragraph(2,12);
 }else if(page==1){line(4,"HABITAT NOTES");paragraph(3,5);}
 else if(page==2){line(4,"HIKE REGIONS");paragraph(4,5);line(11,"TIME ON THIS HIKE");paragraph(5,12);}
 else if(page==3){line(4,"CARE IN THE FIELD");paragraph(6,6);line(11,"NO HANDLING OR FLASH");line(12,"TO PROVOKE A POSE.");}
 else{line(4,"WEATHER / SIGNS");for(i=0;i<2;i++){rf_conditions_clue(rf.guide,i,b);line(6+i,b);}line(10,"ON THESE GAME HIKES,");line(11,"ACTIVITY CAN VARY.");}
 line(15,"SELECT: NEXT PAGE");line(16,"LEFT/RIGHT: SPECIES");line(17,"START:ALBUM B:GUIDE");
}
UBYTE rf_guide_input(UBYTE keys) BANKED {
 UBYTE s,n;
 if(rf.screen==7){
  if(keys&J_B){rf.screen=origin;return origin;}
  if(keys&J_SELECT){filter=(filter+1)%5;select_valid();rf_guide_grid();return 0;}
  if(!empty&&keys&15){n=(keys&(J_UP|J_DOWN))?6:1;while(n--){s=rf_guide_next(rf.guide,(keys&(J_LEFT|J_UP))!=0,filter,rf_map.district,rf.best,rf.spot_state);if(s==255)break;rf.guide=s;}rf_guide_grid();return 0;}
  if(!empty&&keys&J_A){page=0;rf.screen=8;rf_guide_detail(0);return 0;}
  if(!empty&&keys&J_START){rf.screen=10;rf_guide_detail(1);}return 0;
 }
 if(keys&J_B){rf.screen=7;rf_guide_grid();return 0;}
 if(keys&(J_LEFT|J_RIGHT)){s=rf_guide_next(rf.guide,(keys&J_LEFT)!=0,filter,rf_map.district,rf.best,rf.spot_state);if(s!=255)rf.guide=s;rf_guide_detail(rf.screen==10);return 0;}
 if(rf.screen==8&&keys&J_SELECT){page=(page+1)%5;rf_guide_detail(0);return 0;}
 if(keys&J_START){rf.screen=10;rf_guide_detail(1);return 0;}
 if(rf.screen==10&&keys&J_A){page=0;rf.screen=8;rf_guide_detail(0);}return 0;
}
