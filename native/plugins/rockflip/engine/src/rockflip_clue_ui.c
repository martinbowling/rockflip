#pragma bank 255
#include "rockflip_clue_ui.h"
#include "rockflip_runtime.h"
#include <gb/cgb.h>
extern RFSpot rf_spots[16];
extern UBYTE rf_dir;
/* Same bounded bulk-row contract as existing UI. Only row16 is touched.
 * Constant glyph attributes stay inROM,20-byte localbuffer, no newWRAMarray.
 * Restore VBK0 on every text exit. No wildlife identity is read or displayed. */
static const UBYTE row_attrs[20]={135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135,135};
static void hint(const char *s){
 UBYTE tiles[20],i=0;char c;
 while(i<20){if(*s){c=*s++;if(c>=32)tiles[i]=c-32;else tiles[i]=31;}else tiles[i]=0;i++;}
 VBK_REG=0;set_bkg_tiles(0,16,20,1,tiles);
 VBK_REG=1;set_bkg_tiles(0,16,20,1,row_attrs);VBK_REG=0;
}
static void front(INT8 *x,INT8 *y){
 *x=rf.x;*y=rf.y;
 if(rf_dir==0)(*y)++;else if(rf_dir==1)(*y)--;
 else if(rf_dir==2)(*x)--;else (*x)++;
}
static UBYTE front_index(INT8 x,INT8 y){
 UBYTE i;if(x<0||x>9||y<0||y>6)return 255;
 for(i=0;i<rf_map.spot_count&&i<16;i++)
  if(rf_spots[i].x==(UBYTE)x&&rf_spots[i].y==(UBYTE)y)return i;
 return 255;
}
void rf_clue_hud(void) BANKED {
 INT8 x,y;UBYTE s,type;front(&x,&y);
 if(rf_map.camp_x!=255&&x>=0&&y>=0&&(UBYTE)x==rf_map.camp_x&&(UBYTE)y==rf_map.camp_y){hint("A:TALK B:LEAVE");return;}
 s=front_index(x,y);if(s==255){hint("A:LOOK B:LEAVE");return;}
 type=rf_spots[s].type;
 if((type==0||type==5)&&(rf.spot_state[rf_spots[s].id]&1)){
  hint("B:REPLACE THE ROCK");return;
 }
 switch(type){
 case 0:hint("A:LIFT B:LEAVE");break;
 case 1:case 6:hint("A:PEEK B:LEAVE");break;
 case 3:hint("A:LOOK SAND B:LEAVE");break;
 case 5:hint("A:ROCK B:LEAVE");break;
 case 7:case 8:hint("A:WATCH B:LEAVE");break;
 default:hint("A:LOOK B:LEAVE");break;
 }
}
UBYTE rf_clue_leave(void) BANKED {
 INT8 x,y;UBYTE s,type;front(&x,&y);s=front_index(x,y);
 if(s==255){hint("NO OPEN ROCK HERE.");return 1;}
 type=rf_spots[s].type;
 if((type==0||type==5)&&(rf.spot_state[rf_spots[s].id]&1))return 0;
 if(type==6)hint("LEAVE COVER AS FOUND");else hint("LEAVE IT AS FOUND.");return 1;
}
