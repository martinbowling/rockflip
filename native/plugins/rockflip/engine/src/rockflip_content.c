#pragma bank 255
#include "rockflip_content.h"
void rf_maps_00(UBYTE slot,RFMap*out) BANKED;
void rf_maps_01(UBYTE slot,RFMap*out) BANKED;
void rf_maps_02(UBYTE slot,RFMap*out) BANKED;
void rf_maps_03(UBYTE slot,RFMap*out) BANKED;
void rf_maps_04(UBYTE slot,RFMap*out) BANKED;
void rf_maps_05(UBYTE slot,RFMap*out) BANKED;
void rf_maps_06(UBYTE slot,RFMap*out) BANKED;
void rf_maps_07(UBYTE slot,RFMap*out) BANKED;
void rf_world_load(UWORD map,RFMap*out) BANKED {switch(map/32){case 0:rf_maps_00(map%32,out);break;case 1:rf_maps_01(map%32,out);break;case 2:rf_maps_02(map%32,out);break;case 3:rf_maps_03(map%32,out);break;case 4:rf_maps_04(map%32,out);break;case 5:rf_maps_05(map%32,out);break;case 6:rf_maps_06(map%32,out);break;case 7:rf_maps_07(map%32,out);break;}}
void rf_spots_00(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_01(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_02(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_03(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_04(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_05(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_06(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_07(UBYTE slot,RFSpot*out) BANKED;
void rf_spots_08(UBYTE slot,RFSpot*out) BANKED;
void rf_world_spot(UWORD spot,RFSpot*out) BANKED {switch(spot/64){case 0:rf_spots_00(spot%64,out);break;case 1:rf_spots_01(spot%64,out);break;case 2:rf_spots_02(spot%64,out);break;case 3:rf_spots_03(spot%64,out);break;case 4:rf_spots_04(spot%64,out);break;case 5:rf_spots_05(spot%64,out);break;case 6:rf_spots_06(spot%64,out);break;case 7:rf_spots_07(spot%64,out);break;case 8:rf_spots_08(spot%64,out);break;}}
UBYTE rf_world_transition(UWORD from,UWORD to) BANKED {return (from==6&&to==166)||(from==166&&to==6)||(from==167&&to==180)||(from==179&&to==181)||(from==180&&to==167)||(from==181&&to==179);}
static const UWORD trailheads[]={0,22,37,3,8,5,94,4,9,137,152,6,181,196,7,225,131};
UWORD rf_world_trailhead(UBYTE district) BANKED {return district<17?trailheads[district]:trailheads[0];}
