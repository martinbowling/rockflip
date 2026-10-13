#ifndef RF_RESTORE_TRANSACTION_H
#define RF_RESTORE_TRANSACTION_H
#include <gb/gb.h>
/* Frame0..3 means animating; caller uses4 for final synchronous commit.
 * Five transient bytes. No RFState changes or persistent progress writes. */
extern UBYTE rf_restore_busy,rf_restore_spot,rf_restore_frame;
extern UWORD rf_restore_since;
void rf_restore_begin(UBYTE spot,UWORD now) BANKED;
/* 0=no change, 1=draw new frame, 2=closed has been visible >=1VBlank. */
UBYTE rf_restore_tick(UWORD now) BANKED;
void rf_restore_drawn(UWORD now) BANKED;
void rf_restore_end(void) BANKED;
#endif
