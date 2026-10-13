#pragma bank 255
#include "rockflip_guide.h"
void rf_guide_data_0_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_data_0_lines(UBYTE s,UBYTE kind) BANKED;
UWORD rf_guide_data_0_regions(UBYTE s) BANKED;
UBYTE rf_guide_data_0_seen(UBYTE s,const UBYTE*spots) BANKED;
void rf_guide_data_1_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_data_1_lines(UBYTE s,UBYTE kind) BANKED;
UWORD rf_guide_data_1_regions(UBYTE s) BANKED;
UBYTE rf_guide_data_1_seen(UBYTE s,const UBYTE*spots) BANKED;
void rf_guide_data_2_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_data_2_lines(UBYTE s,UBYTE kind) BANKED;
UWORD rf_guide_data_2_regions(UBYTE s) BANKED;
UBYTE rf_guide_data_2_seen(UBYTE s,const UBYTE*spots) BANKED;
void rf_guide_data_3_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_data_3_lines(UBYTE s,UBYTE kind) BANKED;
UWORD rf_guide_data_3_regions(UBYTE s) BANKED;
UBYTE rf_guide_data_3_seen(UBYTE s,const UBYTE*spots) BANKED;
void rf_guide_data_4_text(UBYTE s,UBYTE kind,UBYTE line,char*out) BANKED;
UBYTE rf_guide_data_4_lines(UBYTE s,UBYTE kind) BANKED;
UWORD rf_guide_data_4_regions(UBYTE s) BANKED;
UBYTE rf_guide_data_4_seen(UBYTE s,const UBYTE*spots) BANKED;
void rf_guide_text(UBYTE sid,UBYTE kind,UBYTE line,char*out) BANKED {if(sid>=151){out[0]=0;return;}switch(sid/32){case 0:rf_guide_data_0_text(sid%32,kind,line,out);return;case 1:rf_guide_data_1_text(sid%32,kind,line,out);return;case 2:rf_guide_data_2_text(sid%32,kind,line,out);return;case 3:rf_guide_data_3_text(sid%32,kind,line,out);return;case 4:rf_guide_data_4_text(sid%32,kind,line,out);return;}}
UBYTE rf_guide_lines(UBYTE sid,UBYTE kind) BANKED {if(sid>=151){return 0;}switch(sid/32){case 0:return rf_guide_data_0_lines(sid%32,kind);case 1:return rf_guide_data_1_lines(sid%32,kind);case 2:return rf_guide_data_2_lines(sid%32,kind);case 3:return rf_guide_data_3_lines(sid%32,kind);case 4:return rf_guide_data_4_lines(sid%32,kind);}return 0;}
UWORD rf_guide_regions(UBYTE sid) BANKED {if(sid>=151){return 0;}switch(sid/32){case 0:return rf_guide_data_0_regions(sid%32);case 1:return rf_guide_data_1_regions(sid%32);case 2:return rf_guide_data_2_regions(sid%32);case 3:return rf_guide_data_3_regions(sid%32);case 4:return rf_guide_data_4_regions(sid%32);}return 0;}
UBYTE rf_guide_seen(UBYTE sid,const UBYTE*best,const UBYTE*spots) BANKED {if(sid>=151)return 0;if(best[sid])return 1;switch(sid/32){case 0:return rf_guide_data_0_seen(sid%32,spots);case 1:return rf_guide_data_1_seen(sid%32,spots);case 2:return rf_guide_data_2_seen(sid%32,spots);case 3:return rf_guide_data_3_seen(sid%32,spots);case 4:return rf_guide_data_4_seen(sid%32,spots);}return 0;}
UBYTE rf_guide_match(UBYTE sid,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED {if(sid>=151||filter>4)return 0;switch(filter){case 0:return 1;case 1:if(!best[sid])return 1;return 0;case 2:return rf_guide_seen(sid,best,spots);case 3:if(best[sid])return 1;return 0;case 4:if(district>15||sid==150&&!best[150])return 0;if(rf_guide_regions(sid)&((UWORD)1<<district))return 1;return 0;}return 0;}
UBYTE rf_guide_count(UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED {UBYTE sid,count=0;for(sid=0;sid<151;sid++)if(rf_guide_match(sid,filter,district,best,spots))count++;return count;}
UBYTE rf_guide_next(UBYTE sid,UBYTE backward,UBYTE filter,UBYTE district,const UBYTE*best,const UBYTE*spots) BANKED {UBYTE n;if(sid>=151)sid=backward?0:150;for(n=0;n<151;n++){if(backward){if(sid)sid--;else sid=150;}else{sid++;if(sid>=151)sid=0;}if(rf_guide_match(sid,filter,district,best,spots))return sid;}return 255;}
