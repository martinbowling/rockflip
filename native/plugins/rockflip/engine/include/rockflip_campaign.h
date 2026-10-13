#ifndef ROCKFLIP_CAMPAIGN_H
#define ROCKFLIP_CAMPAIGN_H
#include <gbdk/platform.h>
#define RF_CAMPAIGN_DISTRICTS 16
#define RF_CAMPAIGN_STAGES 3
/* All district indexes0..15, matching RFMap.district. Caller saves flags. */
UBYTE rf_campaign_photo(UBYTE *flags,UBYTE species,UWORD spot,UBYTE phase,UBYTE stars,UBYTE distance,UBYTE focus) BANKED;
void rf_campaign_care(UBYTE *flags,UWORD spot) BANKED;
UBYTE rf_campaign_stage(const UBYTE *flags,UBYTE district) BANKED;
UBYTE rf_campaign_answer(UBYTE *flags,UBYTE district,UBYTE choice) BANKED;
UBYTE rf_campaign_turn_in(UBYTE *flags,UBYTE district) BANKED;
UBYTE rf_campaign_chapters(const UBYTE *flags) BANKED;
void rf_campaign_text(UBYTE district,UBYTE stage,UBYTE kind,UBYTE line,char *out) BANKED;
void rf_campaign_ranger(UBYTE district,char *out) BANKED;
void rf_campaign_chapter_text(UBYTE chapter,UBYTE line,char *out) BANKED;
UBYTE rf_campaign_finale_stage(const UBYTE *flags) BANKED;
UBYTE rf_campaign_finale_answer(UBYTE *flags,UBYTE choice) BANKED;
UBYTE rf_campaign_finale_complete(const UBYTE *flags) BANKED;
void rf_campaign_finale_text(UBYTE question,UBYTE kind,UBYTE line,char *out) BANKED;
void rf_campaign_ack_credits(UBYTE *flags) BANKED;
void rf_campaign_hidden_clue(UBYTE *flags) BANKED;
UBYTE rf_campaign_hidden_answer(UBYTE *flags,UBYTE choice) BANKED;
UBYTE rf_campaign_unlock_hidden(UBYTE *flags,UBYTE regular_photo_count) BANKED;
UBYTE rf_campaign_hidden_ready(const UBYTE *flags) BANKED;
void rf_campaign_hidden_text(UBYTE kind,UBYTE line,char *out) BANKED;
#endif
