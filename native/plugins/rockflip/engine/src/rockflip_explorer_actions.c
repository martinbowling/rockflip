#pragma bank 255
#include "rockflip_explorer_actions.h"
#include "actor.h"
#include "data_manager.h"
#include "data/game_globals.h"
/* Generated named state indices address animations_lookup, never metasprite
 * dedup indices. Missing metadata states fail compilation, rather than falling
 * back to a walking frame. load_animations restores the caller's ROM bank. */
static UBYTE rf_explorer_action_frames;
void rf_explorer_action_begin(UBYTE kind) BANKED {
 UWORD state;
 if(kind==RF_EXPLORER_LIFT)state=STATE_EXPLORER_LIFT;
 else if(kind==RF_EXPLORER_CAMERA)state=STATE_EXPLORER_CAMERA;
 else state=STATE_EXPLORER_PEEK;
 load_animations(PLAYER.sprite.ptr,PLAYER.sprite.bank,state,PLAYER.animations);
 actor_set_anim_idle(&PLAYER);
 actor_stop_anim(&PLAYER);
 rf_explorer_action_frames=12;
}
UBYTE rf_explorer_action_update(void) BANKED {
 if(rf_explorer_action_frames)rf_explorer_action_frames--;
 if(rf_explorer_action_frames==6){
  /* Named animation end is the authored second pose; hold each pose six frames. */
  UBYTE frame=PLAYER.animations[PLAYER.animation].end;
  actor_set_frames(&PLAYER,frame,frame+1);
 }
 return rf_explorer_action_frames==0;
}
void rf_explorer_action_end(void) BANKED {
 rf_explorer_action_frames=0;
 load_animations(PLAYER.sprite.ptr,PLAYER.sprite.bank,STATE_DEFAULT,PLAYER.animations);
 actor_reset_anim(&PLAYER);
}
