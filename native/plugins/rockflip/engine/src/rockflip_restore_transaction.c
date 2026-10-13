#pragma bank 255
#include "rockflip_restore_transaction.h"
UBYTE rf_restore_busy,rf_restore_spot,rf_restore_frame;
UWORD rf_restore_since;
void rf_restore_begin(UBYTE spot,UWORD now) BANKED {rf_restore_busy=1;rf_restore_spot=spot;rf_restore_frame=0;rf_restore_since=now;}
UBYTE rf_restore_tick(UWORD now) BANKED {
 UWORD age;
 if(!rf_restore_busy)return 0;
 age=(UWORD)(now-rf_restore_since);
 /* Two VBlanks include one complete displayed closed frame before commit. */
 if(rf_restore_frame==3){if(age>=2)return 2;return 0;}
 if(age<8)return 0;
 rf_restore_frame++;
 return 1;
}
/* Caller stamps after the actual VRAM upload, avoiding shorter visible holds. */
void rf_restore_drawn(UWORD now) BANKED {rf_restore_since=now;}
void rf_restore_end(void) BANKED {rf_restore_busy=0;}
