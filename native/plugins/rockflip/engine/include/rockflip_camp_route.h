#ifndef ROCKFLIP_CAMP_ROUTE_H
#define ROCKFLIP_CAMP_ROUTE_H
#include <gb/gb.h>
/* 0 localcamp;1west;2east;3north;4south;255 no walking route.
 * Hints are nearest by map hops, not player-position pixel distance.
 * No crossing regional/island boundaries. Hiddenrefuge needs explicit return.
 */
UBYTE rf_camp_route(UWORD map,UWORD*camp,UWORD*next,UBYTE*direction) BANKED;
void rf_camp_route_hint(UWORD map,char*out) BANKED;
#endif
