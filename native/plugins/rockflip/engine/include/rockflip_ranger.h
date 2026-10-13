#ifndef RF_RANGER_H
#define RF_RANGER_H
#include <gb/gb.h>
void rf_ranger_portrait(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;
/* Frame0..11: down/right/up/left, idle/weightshift1/weightshift2. Only swaps96bytes bank0tiles224..229, no map/attributes/palette/OAM writes. */
void rf_ranger_camp_frame(UBYTE ranger,UBYTE frame) BANKED;
/* Root advances phase0..3 every96 VBlank: authored0,1,0,2poses. */
void rf_ranger_camp_idle(UBYTE ranger,UBYTE phase) BANKED;
#endif
