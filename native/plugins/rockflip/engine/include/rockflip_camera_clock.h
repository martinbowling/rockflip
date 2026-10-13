#ifndef ROCKFLIP_CAMERA_CLOCK_H
#define ROCKFLIP_CAMERA_CLOCK_H
#include <gb/gb.h>
void rf_camera_clock_begin(void) BANKED;
void rf_camera_clock_focus_reset(void) BANKED;
/* Bit0 natural phase crossed; bit1 text refresh; bit2 portrait recomposition. */
UBYTE rf_camera_clock_step(void) BANKED;
#endif
