#ifndef RF_GUIDE_H
#define RF_GUIDE_H
#include <gb/gb.h>
#define RF_GUIDE_COUNT 151
#define RF_GUIDE_NONE 255
/* kind0 fullcommon,1 scientific,2 reviewedfacts,3 habitats,4 broadregions,
 *5 authoredgameavailability(nonexclusive),6 generalnonhandlingcare. out>=21. */
void rf_guide_text(UBYTE sid,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_lines(UBYTE sid,UBYTE kind) BANKED;
UWORD rf_guide_regions(UBYTE sid) BANKED;
UBYTE rf_guide_seen(UBYTE sid,const UBYTE*best,const UBYTE*spot_flags) BANKED;
/* filters0ALL,1UNPHOTOGRAPHED,2SEEN,3PHOTOGRAPHED,4CURRENTDISTRICT.
 * Hidden150range is excluded until actualphoto; UI never calls text for it
 * before photo. ALL/unphotographed may retain an anonymous slot. */
UBYTE rf_guide_match(UBYTE sid,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED;
UBYTE rf_guide_count(UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED;
UBYTE rf_guide_next(UBYTE sid,UBYTE backward,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED;
#endif
