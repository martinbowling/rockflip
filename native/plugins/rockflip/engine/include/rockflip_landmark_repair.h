#ifndef RF_LANDMARK_REPAIR_H
#define RF_LANDMARK_REPAIR_H
#include <gb/gb.h>
/* Return1 onlywhenxyrelocated. Doesnotmodifyphotos/flags/phase/weather/care/identity. */
UBYTE rf_landmark_repair(UWORD map,UBYTE*x,UBYTE*y) BANKED;
#endif
