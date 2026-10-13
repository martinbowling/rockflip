#ifndef ROCKFLIP_JOURNAL_H
#define ROCKFLIP_JOURNAL_H
#include <gb/gb.h>
#define RF_JOURNAL_STAGE_COUNT 5
/* Stable version-one layout inside the parent's32-byte RF02 quest flag buffer:
 * 0 donebits0..4;1photoevidencebits0..5;2annotationbits0..4;3carebits0..1;
 * 4 pendingkingsnake spotmask(0->bit0,6->bit1);5pendingtoad spotmask(5->bit0);
 * 6 currentopenrocks(0->bit0,5->bit1,6->bit2);7deliveredrewardbits0..4;
 * 8 bit0 firstMojavesurveyfiled;9bit0 D04lead;10..31 now owned by campaign/finale; journal leaves them untouched.
 * Layout5 reserves previously unused highbits0:5..7,1:6..7,2:5..7,
 * 3:2..7,4:2..7,5:1..7,6:3..7 for32 regionalchallenge awards;
 * 7bit5 is challenge mode. Every journal operation preserves these bits.
 * Rest never clears journal evidence/care/done. Parent saves flags after events.
 * Photo/care/rock callbacks are trusted actual game events; care must be called
 * only AFTER a truly flipped rock was restored; the prior journal openbit must
 * still be set when care is emitted (care clears it). Sync at load/turn-in.
 * Prior albums may seed only demonstrably valid events including exactsite/focus;
 * absent albummetadata must never synthesize annotation or sequence-boundcare.
 * Stage5 meansfirstsurveyfiled, neverfullchapter orwholegame completion. */
#define RF_J_DONE 0
#define RF_J_PHOTOS 1
#define RF_J_NOTES 2
#define RF_J_CARE 3
#define RF_J_PENDING_KING 4
#define RF_J_PENDING_TOAD 5
#define RF_J_OPEN_ROCKS 6
#define RF_J_REWARDS 7
#define RF_J_DISTRICT 8
#define RF_J_LEAD 9
UBYTE rf_journal_stage(const UBYTE*flags) BANKED;
void rf_journal_photo(UBYTE*flags,UBYTE species,UWORD spot,UBYTE phase,UBYTE stars,UBYTE distance,UBYTE focus) BANKED;
void rf_journal_care(UBYTE*flags,UWORD spot) BANKED;
void rf_journal_rock(UBYTE*flags,UWORD spot,UBYTE open) BANKED;
UBYTE rf_journal_answer(UBYTE*flags,UBYTE choice) BANKED;
UBYTE rf_journal_turn_in(UBYTE*flags) BANKED;
/* kinds0title,1hint,2question,3rotatedchoices,4success,5missing.
 * Output isalwaysNULterminated, atmost20ASCII bytes; caller reserves21bytes.
 * line>=authoredcount returns empty. Stage5 givesfirstsurvey/nextlead text. */
void rf_journal_text(UBYTE stage,UBYTE kind,UBYTE line,char*out) BANKED;
#endif
