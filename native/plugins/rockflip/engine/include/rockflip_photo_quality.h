#ifndef ROCKFLIP_PHOTO_QUALITY_H
#define ROCKFLIP_PHOTO_QUALITY_H
#include <gb/gb.h>
typedef struct {
 UBYTE behavior,cycle,motion,distance,minimum_distance,focus,stress;
 UBYTE visible,disturbed,elapsed_cycle,centered;
 INT8 x,y;
} RFPhotoQuality;
/* 1 ordinary visiblephoto;2 focusedfieldrecord;3 focused/centered naturalmoment.
 * Hidden/unsafe photographs cannot qualify. Disturbed means this encounter
 * actually triggered hiding/wedging from approach, not harmless camera framing.
 * Biological defensive displays must never use natural_display behavior.
 */
/* Separate comparator avoids a confirmed SDCC4.5 pointer-store optimizer defect. */
UBYTE rf_photo_quality_centered(INT8 subject,INT8 aim) BANKED;
UBYTE rf_photo_quality_bonus(const RFPhotoQuality*q) BANKED;
UBYTE rf_photo_quality_score(const RFPhotoQuality*q) BANKED;
void rf_photo_quality_hint(const RFPhotoQuality*q,char*out) BANKED;
#endif
