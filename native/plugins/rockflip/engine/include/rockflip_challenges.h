#ifndef ROCKFLIP_CHALLENGES_H
#define ROCKFLIP_CHALLENGES_H
#include <gbdk/platform.h>
#define RF_CHALLENGE_COUNT 32u
/* Global index = district * 2 + local index. Invalid target = 255.
 * Kind 0 title(1),1 brief(2),2 hint(3),3 care(1),4 retry(2),5 rule(3).
 * Completion uses persisted reserved journal highbits, layout5; verified oldbest awards migrate once. */
void rf_challenge_fresh(void) BANKED;
void rf_challenge_migrate(void) BANKED;
UBYTE rf_challenge_awards_valid(void) BANKED;
UBYTE rf_challenge_record(void) BANKED;
UBYTE rf_challenge_count(UBYTE district) BANKED;
UBYTE rf_challenge_species(UBYTE index) BANKED;
UBYTE rf_challenge_district(UBYTE index) BANKED;
UWORD rf_challenge_spot(UBYTE index) BANKED;
UWORD rf_challenge_map(UBYTE index) BANKED;
UBYTE rf_challenge_phase(UBYTE index) BANKED;
UBYTE rf_challenge_complete(const UBYTE *best,UBYTE index) BANKED;
UBYTE rf_challenge_completed(const UBYTE *best,UBYTE district) BANKED;
UBYTE rf_challenge_total_completed(const UBYTE *best) BANKED;
void rf_challenge_text(UBYTE index,UBYTE kind,UBYTE line,char *out) BANKED;
#endif
