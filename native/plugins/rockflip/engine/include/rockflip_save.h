#ifndef ROCKFLIP_SAVE_H
#define ROCKFLIP_SAVE_H
#include <gb/gb.h>

#define RF_STORE_PAYLOAD_MAX 4080u
#define RF_STORE_PRE_SNAPSHOT_SIZE 2256u
#define RF_STORE_SNAPSHOT_SIZE 2448u
#define RF_STORE_SNAPSHOT_BYTES 192u
#define RF_STORE_WEATHER_SIZE 2544u
#define RF_STORE_WEATHER_BYTES 96u
/* 0 blank/corrupt, 1 RF02 copied, 2 checksum-valid RF01 copied to legacy64,
 * 3 unsupported committed format/layout or caller-size mismatch,
 * 4 verified older RF02 copied with zero-filled append-only tail.
 * Native layouts: 1/2256 pre-pose; 2/2448 poses; 3/2544 conditions;4/2544 lens;5/2544 regionalchallenge flags;6/2544 fresh route variant.
 * Migrations allowed: 2256->2448,2256->2544,2448->2544, and layout3/4/5->6 at same2544 size. Generic64/4080
 * remain layout1; layouts2/3/4/5/6 require their exact reserved sizes. Downgrades lock.
 * Snapshot bit7: pose known; bit4: conditions known, requiring pose known.
 * Bit5 stores lens override;bit6 forbidden. Weather/season each2bits packed one nibble per species,
 * two species per appended byte. Layout6 store preserves all prior payload bytes; runtime alone migrates32 unused journal highbits and mode7bit5 on authenticated oldload. Newgames mark current mode before firstsave. No albumderived awards on currentlayouts5/6. Zero tail means unknown, not measured fair.
 * Opaque store does not validate animal/domain data; runtime must enforce bits.
 * First save after return4 writes the alternate slot preserving the old record.
 * Payload must be stable WRAM, not SRAM or switchable ROM. No staging buffer.
 * All calls restore SRAM bank zero and disable SRAM, matching engine ownership. */
extern UBYTE rf_store_ok;
extern UBYTE rf_store_locked;
/* Authenticated source layout from last load; zero for blank/RF01/future. */
extern UBYTE rf_store_loaded_layout;
UBYTE rf_store_load(void *payload, UWORD size, UBYTE *legacy64) BANKED;
void rf_store_save(const void *payload, UWORD size) BANKED;
#endif
