#ifndef RF_CONTENT_H
#define RF_CONTENT_H
#include <gbdk/platform.h>
#define RF_SPECIES_CAPACITY 192
#define RF_MAP_CAPACITY 400
#define RF_SPOT_CAPACITY 1000
#define RF_SPECIES_COUNT 151
typedef struct {UWORD id,west,east; UBYTE district,style,camp_x,camp_y,spot_count; UWORD spots[16]; char name[21],terrain[7][11];UWORD north,south;UBYTE north_x,south_x;} RFMap;
typedef struct {UWORD id,room; UBYTE x,y,type,species,phases;} RFSpot;
void rf_world_load(UWORD map,RFMap *out) BANKED;
void rf_world_spot(UWORD spot,RFSpot *out) BANKED;
UBYTE rf_species_rule(UBYTE species,UBYTE field) BANKED;
UBYTE rf_world_transition(UWORD from,UWORD to) BANKED;
UWORD rf_world_trailhead(UBYTE district) BANKED;
#define RF_MAP_COUNT 241
#define RF_SPOT_COUNT 538
#endif
