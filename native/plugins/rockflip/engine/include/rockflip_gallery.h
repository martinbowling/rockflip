#ifndef ROCKFLIP_GALLERY_H
#define ROCKFLIP_GALLERY_H
#include <gb/gb.h>
extern UBYTE rf_gallery_district,rf_gallery_pair;
UBYTE rf_gallery_subject(UBYTE district,UBYTE pair) BANKED;
UBYTE rf_gallery_photo_ready(UBYTE district,UBYTE pair) BANKED;
void rf_gallery_begin(UBYTE district) BANKED;
void rf_gallery_draw(void) BANKED;
/* Returns20 when caller must repaint exhibit. Other keys handled locally. */
UBYTE rf_gallery_input(UBYTE keys) BANKED;
#endif
