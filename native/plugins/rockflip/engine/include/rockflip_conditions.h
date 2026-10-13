#ifndef RF_CONDITIONS_H
#define RF_CONDITIONS_H
#include <gb/gb.h>
/* Nibble: weather0..3 + season0..3 <<2. Quest9 bits1..4 persist selection. */
UBYTE rf_conditions_current(void) BANKED;
UBYTE rf_conditions_allowed(UBYTE species,UBYTE conditions) BANKED;
void rf_conditions_label(UBYTE conditions,char *out) BANKED;
void rf_conditions_clue(UBYTE species,UBYTE line,char *out) BANKED;
void rf_conditions_shade(UBYTE conditions) BANKED;
UBYTE rf_conditions_photo(UBYTE species) BANKED;
void rf_conditions_record(UBYTE species,UBYTE conditions) BANKED;
void rf_conditions_forecast(void) BANKED;
extern UBYTE rf_forecast_phase,rf_forecast_weather,rf_forecast_season,rf_forecast_field;
#endif
