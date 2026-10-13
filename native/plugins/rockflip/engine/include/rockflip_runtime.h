#ifndef ROCKFLIP_RUNTIME_H
#define ROCKFLIP_RUNTIME_H
#include <gb/gb.h>
#include "rockflip_content.h"
/* Fixed2544-byte schema6 payload. Fresh route variant uses quest8bit1; authenticated layouts1..5 retain legacy routes. Challenge awards reuse unused journal highbits; verified layouts1..4 migrate once. No RFState growth. */
struct RFState {UBYTE screen;UWORD room;UBYTE x,y,phase,spot,species,focus,distance;
 INT8 aim;UBYTE stress,score,count,points,guide;
 UBYTE best[RF_SPECIES_CAPACITY],photo_distance[RF_SPECIES_CAPACITY];
 INT8 photo_aim[RF_SPECIES_CAPACITY];UBYTE photo_phase[RF_SPECIES_CAPACITY];
 UWORD photo_map[RF_SPECIES_CAPACITY];UBYTE spot_state[RF_SPOT_CAPACITY],visited_maps[50];
 UWORD rng,steps,travel;UBYTE quest_flags[32];UBYTE photo_snapshot[RF_SPECIES_CAPACITY];
 /* Append96bytes after all prior fields: even species low nibble, odd high. */
 UBYTE photo_conditions[RF_SPECIES_CAPACITY/2];};
extern struct RFState rf;
extern RFMap rf_map;
extern UBYTE rf_challenge;
extern UBYTE rf_j_choice,rf_j_stage,rf_j_kind,rf_c_district,rf_c_stage,rf_c_choice,rf_c_kind;
#endif
