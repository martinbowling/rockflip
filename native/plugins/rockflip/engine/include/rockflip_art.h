#ifndef RF_ART_H
#define RF_ART_H
#include <gbdk/platform.h>
void rf_art_font(void) BANKED;
void rf_art_hud_mask(void) BANKED;
void rf_art_load(void) BANKED;
void rf_art_tint(UBYTE phase) BANKED;
void rf_art_logo(void) BANKED;
void rf_art_title(void) BANKED;
void rf_art_water(UBYTE frame) BANKED;
void rf_art_map_water(UWORD map,UBYTE frame) BANKED;
void rf_art_backdrop(UWORD room,UBYTE phase) BANKED;
UBYTE rf_art_map(UWORD map,UBYTE phase,UBYTE camera) BANKED;
void rf_art_portrait(UBYTE species,UBYTE scale) BANKED;
void rf_art_icon(UBYTE species,UBYTE silhouette,UBYTE slot) BANKED;
void rf_art_portrait_frame(UBYTE species,UBYTE scale,UBYTE frame) BANKED;
void rf_art_scientific(UBYTE species,char*out) BANKED;
void rf_art_name(UBYTE species,char *out) BANKED;
void rf_art_fact(UBYTE species,UBYTE line,char *out) BANKED;
UBYTE rf_art_terrain_pal(UBYTE tile) BANKED;
#endif
