#ifndef ROCKFLIP_CLUE_UI_H
#define ROCKFLIP_CLUE_UI_H
#include <gb/gb.h>
/* Argument-free BANKED selectors read actual facing/current cachedRAM state.
 * Neither function modifies persistent fields or calls save. */
void rf_clue_hud(void) BANKED;
/* Returns1 only when B was handled as leaving a closed/nonmovable clue.
 * Returns0 for an actual open type0/5 so existing restoration runs unchanged. */
UBYTE rf_clue_leave(void) BANKED;
#endif
