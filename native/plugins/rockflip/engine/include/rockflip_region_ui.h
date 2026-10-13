#ifndef ROCKFLIP_REGION_UI_H
#define ROCKFLIP_REGION_UI_H
#include <gb/gb.h>
/* Three transient bytes only; engine owns screens30/31 and context return. */
extern UBYTE rf_region_cursor,rf_region_district,rf_region_origin;
void rf_region_open(UWORD map,UBYTE origin) BANKED;
void rf_region_move(UBYTE key) BANKED;
UBYTE rf_region_follow(UBYTE key) BANKED;
UWORD rf_region_selected(void) BANKED;
void rf_ui_region_map(void) BANKED;
void rf_ui_region_detail(void) BANKED;
void rf_ui_welcome(UBYTE page) BANKED;
#endif
