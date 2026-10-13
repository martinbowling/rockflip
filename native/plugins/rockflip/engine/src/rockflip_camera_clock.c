#pragma bank 255
#include "rockflip_camera_clock.h"
#include "rockflip_runtime.h"
extern UWORD rf_behavior_clock;
extern UBYTE rf_motion,rf_wedged;
/* Eight transient bytes; no persistent fields, buffers or catch-up loops. */
static UWORD last_behavior_vbl,last_focus_vbl,behavior_position;
static UBYTE focus_fraction,completed_cycle;
static UWORD now_vbl(void){UWORD n;__critical{n=sys_time;}return n;}
void rf_camera_clock_focus_reset(void) BANKED{rf.focus=0;focus_fraction=0;last_focus_vbl=now_vbl();}
void rf_camera_clock_begin(void) BANKED{UWORD n=now_vbl();last_behavior_vbl=last_focus_vbl=n;behavior_position=0;focus_fraction=completed_cycle=0;rf_behavior_clock=0;}
UBYTE rf_camera_clock_step(void) BANKED{
 UWORD now=now_vbl(),delta=(UWORD)(now-last_behavior_vbl),focus_delta=(UWORD)(now-last_focus_vbl);
 UWORD period=rf_species_rule(rf.species,1),real_period=period+5,span=real_period*4;
 UWORD crossings=delta/real_period,carry=(behavior_position%real_period)+(delta%real_period);
 UWORD next_position=behavior_position+(delta%span),units;
 UBYTE changed=0,old_focus=rf.focus,old_wedged=rf_wedged;
 last_behavior_vbl=last_focus_vbl=now;
 crossings+=carry/real_period;
 if(crossings){completed_cycle=1;rf_motion^=(UBYTE)(crossings&1);changed|=1;}
 behavior_position=next_position%span;
 /* Keep exported source-period/cycle semantics for the existing quality API.
  * After the first turn, cycle0 is represented by 4*period, never fresh0. */
 rf_behavior_clock=(behavior_position/real_period)*period;
 if(completed_cycle&&!rf_behavior_clock)rf_behavior_clock=period*4;
 rf_behavior_clock+=(behavior_position%real_period)*period/real_period;
 if(rf_wedged){
  if(delta>=rf_wedged){rf_wedged=0;changed|=6;focus_delta=0;}
  else{rf_wedged-=(UBYTE)delta;focus_delta=0;}
  rf.focus=0;focus_fraction=0;
 }else if(rf.focus<60){
  /* 45units=60VBlanks;60units=80VBlanks, calibrated to native e6fa60/82.
   * Clamp before multiplication, including a long synchronous save stall. */
  if(focus_delta>=80){rf.focus=60;focus_fraction=0;}
  else{units=focus_delta*3+focus_fraction;focus_fraction=units&3;units=rf.focus+units/4;rf.focus=units>60?60:(UBYTE)units;}
 }
 if(old_focus<45&&rf.focus>=45)changed|=4;
 if(old_focus/10!=rf.focus/10||(old_focus<45&&rf.focus>=45)||(old_wedged&&!rf_wedged))changed|=2;
 return changed;
}
