#ifndef ROCKFLIP_AUDIO_H
#define ROCKFLIP_AUDIO_H
#include <gb/gb.h>
#define RF_SFX_LOOK 0
#define RF_SFX_PHOTO 1
#define RF_SFX_CARE 2
#define RF_SFX_JOURNAL 3
/* District0..15,phase0day/1dusk/2night; poll outsideISR; internal VBlank clock preserves tempo position.
 * Reserves2melody/3quietwaveharmony/4sparseambient;1effects.
 * No active competing engine tracker may own these channels. Defaultmaster3/7;
 * mute persists untilcallerchangesit (persist preferencein parent save/UI).
 * Original patterns require human listening and physicalhardware validation. */
void rf_audio_init(void) BANKED;
void rf_audio_update(UBYTE district,UBYTE phase) BANKED;
void rf_audio_mute(UBYTE value) BANKED;
void rf_audio_sfx(UBYTE type) BANKED;
#endif
