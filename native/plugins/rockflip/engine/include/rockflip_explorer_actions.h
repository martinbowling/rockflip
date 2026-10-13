#ifndef RF_EXPLORER_ACTIONS_H
#define RF_EXPLORER_ACTIONS_H
#include <gbdk/platform.h>
#define RF_EXPLORER_PEEK 1
#define RF_EXPLORER_LIFT 2
#define RF_EXPLORER_CAMERA 3
/* Transient only: zero SRAM fields; caller owns deferred gameplay operation. */
void rf_explorer_action_begin(UBYTE kind) BANKED;
UBYTE rf_explorer_action_update(void) BANKED;
void rf_explorer_action_end(void) BANKED;
#endif
