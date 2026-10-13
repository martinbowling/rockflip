#ifndef ROCKFLIP_LENS_H
#define ROCKFLIP_LENS_H
#include <gb/gb.h>
extern UBYTE rf_lens_active;
UBYTE rf_lens_ready(void) BANKED;
void rf_lens_begin(void) BANKED;
UBYTE rf_lens_toggle(void) BANKED;
UBYTE rf_lens_scale(UBYTE distance) BANKED;
UBYTE rf_lens_saved_scale(UBYTE distance,UBYTE snapshot) BANKED;
UBYTE rf_lens_snapshot_bit(void) BANKED;
UBYTE rf_lens_should_replace(UBYTE score,UBYTE best,UBYTE snapshot) BANKED;
void rf_lens_hint(char *out) BANKED;
#endif
