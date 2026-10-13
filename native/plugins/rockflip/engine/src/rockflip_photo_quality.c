#pragma bank 255
#include "rockflip_photo_quality.h"
#include <string.h>
static const char hints[12][21]={
 "KEEP SAFE SPACE.","WAIT UNTIL STILL.","WATCH WITHOUT RUSH.",
 "FRAME ITS GLIDE.","WATCH A NATURAL HOP.","WAIT FOR A PUSH-UP.",
 "WATCH A WALKING STEP", "WAIT FOR IT TO REST", "WAIT FOR IT TO RISE.",
 "WATCH A COVER EDGE.","WATCH A NATURAL POSE", "WATCH A RAINY STEP."
};
UBYTE rf_photo_quality_bonus(const RFPhotoQuality*q) BANKED {
 if(!q||!q->visible||q->disturbed||q->stress||q->focus<60||!q->centered
    ||q->distance<q->minimum_distance||q->distance>4)return 0;
 switch(q->behavior){
  case 0:return 1; /* Protection rewarded through patience and safe distance. */
  case 1:return 1; /* A relaxed, clearly resolved still subject. */
  case 2:return q->elapsed_cycle; /* No wedge-trigger history, no hiding bonus. */
  case 3:return q->x!=0; /* Lead and frame the natural glide. */
  case 4:return q->y<0; /* Natural hop, never induced movement. */
  case 5:return q->motion!=0; /* Authored voluntary push-up animation. */
  case 6:case 11:return q->x!=0&&q->motion!=0;
  case 7:return q->elapsed_cycle&&q->cycle==3; /* Calm after natural dash. */
  case 8:return q->cycle==2&&q->y<0; /* Naturally emerging above water. */
  case 9:return q->cycle==2&&q->x!=0; /* Visible peek at undisturbed cover. */
  case 10:return q->y<0; /* Source-checked nondefensive natural posture only. */
  default:return 0;
 }
}
UBYTE rf_photo_quality_score(const RFPhotoQuality*q) BANKED {
 if(!q||!q->visible||q->distance<q->minimum_distance||q->distance>4)return 0;
 if(q->focus<45)return 1;
 return 2+rf_photo_quality_bonus(q);
}
void rf_photo_quality_hint(const RFPhotoQuality*q,char*out) BANKED {
 if(!q){out[0]=0;return;}
 if(q->disturbed){strcpy(out,"LET IT REST QUIETLY.");return;}
 if(q->focus<60){strcpy(out,"HOLD STILL A LITTLE.");return;}
 if(rf_photo_quality_bonus(q)){strcpy(out,"NATURAL MOMENT! A.");return;}
 if(!q->centered){strcpy(out,"FRAME THE ANIMAL.");return;}
 strcpy(out,hints[q->behavior<12?q->behavior:0]);
}

UBYTE rf_photo_quality_centered(INT8 subject,INT8 aim) BANKED {if(subject==aim)return 1;return 0;}
