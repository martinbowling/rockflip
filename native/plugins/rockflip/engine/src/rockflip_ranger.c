#pragma bank 255
#include "rockflip_ranger.h"
void rf_ranger_0_portrait(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_0_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;
void rf_ranger_0_camp_frame(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_1_portrait(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_1_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;
void rf_ranger_1_camp_frame(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_2_portrait(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_2_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;
void rf_ranger_2_camp_frame(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_3_portrait(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_3_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED;
void rf_ranger_3_camp_frame(UBYTE ranger,UBYTE frame) BANKED;
void rf_ranger_portrait(UBYTE ranger,UBYTE frame) BANKED {if(ranger>15)ranger=0;switch(ranger/4){case 0:rf_ranger_0_portrait(ranger%4,frame);break;case 1:rf_ranger_1_portrait(ranger%4,frame);break;case 2:rf_ranger_2_portrait(ranger%4,frame);break;case 3:rf_ranger_3_portrait(ranger%4,frame);break;}}
void rf_ranger_camp(UBYTE ranger,UBYTE x,UBYTE y) BANKED {if(ranger>15)ranger=0;switch(ranger/4){case 0:rf_ranger_0_camp(ranger%4,x,y);break;case 1:rf_ranger_1_camp(ranger%4,x,y);break;case 2:rf_ranger_2_camp(ranger%4,x,y);break;case 3:rf_ranger_3_camp(ranger%4,x,y);break;}}
void rf_ranger_camp_frame(UBYTE ranger,UBYTE frame) BANKED {if(ranger>15)ranger=0;if(frame>11)frame=0;switch(ranger/4){case 0:rf_ranger_0_camp_frame(ranger%4,frame);break;case 1:rf_ranger_1_camp_frame(ranger%4,frame);break;case 2:rf_ranger_2_camp_frame(ranger%4,frame);break;case 3:rf_ranger_3_camp_frame(ranger%4,frame);break;}}
void rf_ranger_camp_idle(UBYTE ranger,UBYTE phase) BANKED {static const UBYTE poses[]={0,1,0,2};rf_ranger_camp_frame(ranger,poses[phase&3]);}
