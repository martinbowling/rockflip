#ifndef ROCKFLIP_MARINE_H
#define ROCKFLIP_MARINE_H
#include <gb/gb.h>
/* Open-water photo/album frame for exactmarineIDs61/73. Parentenforceslong
 * distance4, nohandling and legalshoreobservation. Notarock-fliphabitat.
 * Backdropusesbank0tiles96..223maximum, BGpalette3, screen(2,4)16x8tiles.
 * Foregroundportraitbank1/UIpalette7/fonttiles0..95remainuntouched.
 * Reloadnormalworld/habitatpalettesonexit; these functionsownonlycamera3,
 * portraitground5:0 andBkgPalette[0]groundmirrorwhencalled. */
void rf_marine_backdrop(UBYTE phase) BANKED;
void rf_marine_tint(UBYTE phase) BANKED;
#endif
