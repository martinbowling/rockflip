#pragma bank 255
#include "rockflip_art.h"
#include "rockflip_new_game_ui.h"
#include "rockflip_runtime.h"
#include "rockflip_save.h"
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

static void selection(UBYTE y,const char*s,UBYTE selected){text(0,y,selected?">":" ");text(2,y,s);}
void rf_ui_save_options(UBYTE choice) BANKED {
 clear();line(0,"YOUR FIELD JOURNAL");
 if(rf_store_locked){line(4,"NEWER SAVE READ ONLY");line(7,"NEW HIKE DISABLED.");line(17,"B: BACK TO TITLE");return;}
 line(2,"KEEP EXPLORING, OR");line(3,"START A NEW JOURNAL.");
 selection(6,"CONTINUE MY HIKE",choice==0);selection(9,"NEW JOURNAL",choice!=0);
 line(12,"YOUR SAVE STAYS SAFE");line(13,"UNTIL YOU CONFIRM.");
 line(16,"UP/DOWN: CHOOSE");line(17,"A:CHOOSE B:TITLE");
}
void rf_ui_new_game_confirm(UBYTE choice) BANKED {
 clear();line(0,"START A NEW JOURNAL?");
 if(rf_store_locked){line(4,"NEWER SAVE READ ONLY");line(7,"NEW HIKE DISABLED.");line(17,"B: KEEP YOUR SAVE");return;}
 line(2,"PHOTOS AND NOTES");line(3,"WILL START EMPTY.");
 selection(6,"KEEP MY JOURNAL",choice==0);selection(9,"START NEW JOURNAL",choice!=0);
 line(12,"OLD SAVE STAYS UNTIL");line(13,"THE NEW HIKE SAVES.");
 line(16,"UP/DOWN: CHOOSE");line(17,"A:CHOOSE B:CANCEL");
}
