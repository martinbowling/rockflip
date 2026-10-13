#pragma bank 255
#include "rockflip_art.h"
#include "rockflip_conditions.h"
#include "rockflip_runtime.h"
#include "palette.h"
#include "actor.h"
#include <gb/cgb.h>
#include <string.h>
UBYTE rf_forecast_phase,rf_forecast_weather,rf_forecast_season,rf_forecast_field;
static const char weather[4][11]={"FAIR","CLOUDY","RAIN","AFTER RAIN"};
static const char seasons[4][7]={"WINTER","SPRING","SUMMER","FALL"};
static const char phases[3][6]={"DAY","DUSK","NIGHT"};
UBYTE rf_conditions_current(void) BANKED {return (rf.quest_flags[9]>>1)&15;}
static const UBYTE weather_masks[]={15,15,15,15,15,15,15,15,15,4,15,15,15,15,15,15,15,15,15,15,15,15,15,15,12,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,12,15,15,15,15,15,12,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15};
static const UBYTE season_masks[]={15,15,15,15,15,15,15,15,15,11,15,15,15,15,15,15,15,15,15,15,15,15,15,15,6,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,6,15,15,15,15,15,11,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15};
UBYTE rf_conditions_allowed(UBYTE species,UBYTE conditions) BANKED {if(species>=RF_SPECIES_COUNT||conditions>15)return 0;if(!(weather_masks[species]&(1<<(conditions&3))))return 0;if(!(season_masks[species]&(1<<(conditions>>2))))return 0;return 1;}
void rf_conditions_label(UBYTE conditions,char *out) BANKED {
 strcpy(out,weather[conditions&3]);strcat(out," / ");strcat(out,seasons[(conditions>>2)&3]);
}
void rf_conditions_clue(UBYTE species,UBYTE line,char *out) BANKED {
 if(species==9)strcpy(out,line?"FALL / WINTER / SPR.":"RAINY NIGHT WALK.");
 else if(species==24||species==118)strcpy(out,line?"SPRING / SUMMER.":"WARM WET NIGHT.");
 else if(species==124)strcpy(out,line?"FALL / WINTER / SPR.":"COOL WET NIGHT.");
 else strcpy(out,line?"CHOOSE TIME AT CAMP.":"ALL FORECAST WINDOWS");
}
UBYTE rf_conditions_photo(UBYTE species) BANKED {UBYTE v=rf.photo_conditions[species>>1];return (species&1)?v>>4:v&15;}
void rf_conditions_record(UBYTE species,UBYTE conditions) BANKED {
 UBYTE i=species>>1;conditions&=15;
 if(species&1)rf.photo_conditions[i]=(rf.photo_conditions[i]&15)|(conditions<<4);
 else rf.photo_conditions[i]=(rf.photo_conditions[i]&240)|conditions;
}
/* Apply exactly once after loading fresh map/backdrop palettes. Wildlife and UI
 * palettes remain original; palette0's ground tint joins portrait transparency.
 * No repeated cumulative tinting, weather tiles, OAM or geometry changes. */
void rf_conditions_shade(UBYTE conditions) BANKED {
 UBYTE p,i,r,g,b,w=conditions&3,s=(conditions>>2)&3;UWORD c[4],v;
 for(p=0;p<5;p++){
  for(i=0;i<4;i++){
   v=((UWORD*)BkgPalette)[p*4+i];r=v&31;g=(v>>5)&31;b=(v>>10)&31;
   if(w==1){r=r*7/8;g=g*7/8;}
   else if(w==2){r=r*3/4;g=g*7/8;if(b<29)b+=2;}
   else if(w==3){r=r*7/8;if(g<31)g++;if(b<31)b++;}
   if(s==0&&b<31)b++;else if(s==3&&p==1){if(r<31)r++;g=g*7/8;}
   c[i]=RGB(r,g,b);((UWORD*)BkgPalette)[p*4+i]=c[i];
  }
  set_bkg_palette(p,1,c);
 }
}
static const UBYTE attrs[20]={7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7};
static void line(UBYTE y,const char *s){UBYTE t[20],i;char v;for(i=0;i<20;i++){v=*s;if(v)s++;t[i]=v?(v>=32?v-32:31):0;}VBK_REG=0;set_bkg_tiles(0,y,20,1,t);VBK_REG=1;set_bkg_tiles(0,y,20,1,attrs);VBK_REG=0;}
void rf_conditions_forecast(void) BANKED {
 UBYTE i;PLAYER.flags|=ACTOR_FLAG_HIDDEN;HIDE_SPRITES;rf_art_font();for(i=0;i<18;i++)line(i,"");
 line(0,"    PLAN YOUR HIKE");line(2,"REST TO A NEW WINDOW");
 line(4,"TIME");line(5,phases[rf_forecast_phase]);
 line(7,"FORECAST");line(8,weather[rf_forecast_weather]);
 line(10,"SEASON");line(11,seasons[rf_forecast_season]);
 line(13,rf_forecast_field==0?"SELECTED: TIME":rf_forecast_field==1?"SELECTED: FORECAST":"SELECTED: SEASON");
 line(14,"UP/DOWN: FIELD");line(15,"LEFT/RIGHT: CHANGE");line(16,"A: REST AND HIKE");line(17,"B: KEEP THIS WINDOW");
}
