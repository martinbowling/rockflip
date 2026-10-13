#ifndef RF_GUIDE_UI_H
#define RF_GUIDE_UI_H
#include <gb/gb.h>
void rf_guide_open(UBYTE origin) BANKED;
void rf_guide_grid(void) BANKED;
void rf_guide_detail(UBYTE album) BANKED;
/* Returns0 when handled;2/9/25 when main must repaint origin context. */
UBYTE rf_guide_input(UBYTE keys) BANKED;
/* Existing main album renderer, exported unchanged exceptBANKEDname. */
void rf_guide_album_picture(void) BANKED;
#endif
