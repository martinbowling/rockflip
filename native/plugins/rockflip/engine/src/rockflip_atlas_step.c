#pragma bank 255
#include "rockflip_atlas_step.h"
#include "rockflip_runtime.h"
/* Keep the next-index calculation outside the large state dispatcher.
 * Its former compound struct assignment/modulo failed actual atlas traversal
 * after code layout changed (retained d9bb controller diagnostics).
 * Explicit bounded arithmetic also avoids division on this hot UI path.
 */
/* Read the two state fields here: the large caller passed an address byte
 * instead of the actual discovery flag in the first workaround. Its exact
 * entry-stack trace is retained with the fecbae failed-wrap diagnostics.
 */
UBYTE rf_atlas_step(UBYTE forward) BANKED {
    UBYTE index = (UBYTE)rf.travel;
    UBYTE count = 16;
    if (rf.quest_flags[31] & 128) count = 17;
    if (index >= count) index = 0;
    if (forward) {
        index++;
        if (index >= count) index = 0;
    } else if (index) {
        index--;
    } else {
        index = count - 1;
    }
    return index;
}
