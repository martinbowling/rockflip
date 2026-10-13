#pragma bank 255
#include "rockflip_lens.h"
#include "rockflip_runtime.h"
#include "rockflip_campaign.h"
#include <string.h>
/* One transient byte, no added save fields or duplicate photo buffers. */
UBYTE rf_lens_active;
UBYTE rf_lens_ready(void) BANKED{return rf_campaign_chapters(rf.quest_flags)!=0;}
void rf_lens_begin(void) BANKED{rf_lens_active=0;if(rf_lens_ready()&&(rf.quest_flags[9]&32))rf_lens_active=1;}
UBYTE rf_lens_toggle(void) BANKED{if(!rf_lens_ready())return 0;rf.quest_flags[9]^=32;rf_lens_active=0;if(rf.quest_flags[9]&32)rf_lens_active=1;return 1;}
UBYTE rf_lens_scale(UBYTE distance) BANKED{if(distance==4&&!rf_lens_active)return 2;return 3;}
UBYTE rf_lens_saved_scale(UBYTE distance,UBYTE snapshot) BANKED{if(distance==4&&!(snapshot&32))return 2;return 3;}
UBYTE rf_lens_snapshot_bit(void) BANKED{if(rf_lens_active)return 32;return 0;}
UBYTE rf_lens_should_replace(UBYTE score,UBYTE best,UBYTE snapshot) BANKED{if(!score||score>3)return 0;if(score>best)return 1;if(score<best)return 0;if((snapshot&144)!=144)return 1;if((snapshot&32)!=rf_lens_snapshot_bit())return 1;return 0;}
void rf_lens_hint(char*out) BANKED{if(!rf_lens_ready())strcpy(out,"FILE A CHAPTER FIRST");else if(rf_lens_active)strcpy(out,"SELECT: WIDE FRAME");else strcpy(out,"SELECT: FIELD LENS");}
