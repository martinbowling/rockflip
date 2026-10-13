#ifndef ROCKFLIP_CAMPAIGN_VARIANT_H
#define ROCKFLIP_CAMPAIGN_VARIANT_H
#include <gb/gb.h>
typedef struct{UWORD spot;UBYTE species,phase,distance,care;} RFCTarget;
UBYTE rf_campaign_variant_target(UBYTE index,RFCTarget*out) BANKED;
UBYTE rf_campaign_variant_text(UBYTE district,UBYTE stage,UBYTE row,char*out) BANKED;
void rf_campaign_route_hint(UBYTE row,char*out) BANKED;
#endif
