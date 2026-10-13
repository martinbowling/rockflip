#pragma bank 255
#include "rockflip_audio.h"
#include <gb/hardware.h>
/* Original eight-step regional motifs, composed for this project. No sampled
 * audio or borrowed melodies. Quiet pentatonic/open-interval material leaves
 * room for photography effects. Every region has an authored note/rhythm pair.
 * Channels:1 SFX only;2 pulse melody;3 quiet triangle harmony;4 sparse softnoise.
 * Caller polls update outside ISR; elapsed VBlanks drive the motif timeline.
 * Do not also run an
 * active tracker competing for these channels. Mute clears ALL four channels.
 * Register/sequence tests are not listening, mastering or physicalaudio proof.
 */
static const UBYTE motifs[16][8]={
 {0,4,7,4,2,4,7,255}, /* Mojave: open sunlit ascent */
 {0,2,7,9,7,4,2,255}, /* Colorado: low-desert winding */
 {0,7,4,2,9,7,4,255}, /* Eastern basin: airy leaps */
 {0,4,2,4,7,9,7,4}, /* Sierra foothill: oak trail */
 {7,9,7,4,2,4,0,255}, /* High Sierra: clear summit descent */
 {0,2,4,7,4,2,0,255}, /* Sacramento: riparian circle */
 {0,4,7,9,4,2,4,255}, /* San Joaquin: vernal opening */
 {0,7,9,7,2,4,2,255}, /* Bay/Delta: water channels */
 {4,7,9,7,4,2,0,255}, /* Central Coast: fog arc */
 {0,2,4,9,7,4,2,4}, /* South Coast: lively scrub walk */
 {0,7,4,9,7,2,4,255}, /* Southern mountains: climb/creek */
 {0,4,9,7,4,7,2,255}, /* Islands: maritime lift */
 {0,2,7,4,2,0,4,255}, /* North Coast: quiet rain canopy */
 {7,4,0,2,4,7,9,255}, /* Klamath: rock/stream turn */
 {0,7,9,4,7,2,4,255}, /* Cascades: volcanic stepping */
 {0,4,2,7,9,2,0,255}  /* Modoc: wide sage horizon */
};
static const UBYTE roots[16]={0,2,7,5,9,0,4,2,5,7,9,4,2,7,0,5};
static const UBYTE rhythm[16][8]={
 {24,18,24,18,24,18,30,18},{20,20,28,20,24,20,28,20},
 {28,18,22,22,28,18,28,22},{18,18,24,18,18,24,18,24},
 {28,22,22,28,22,22,32,24},{22,22,28,22,22,28,22,28},
 {20,18,24,28,20,18,24,28},{22,18,28,22,18,22,28,22},
 {28,22,28,22,28,22,32,24},{18,18,24,18,24,18,24,18},
 {22,18,28,18,22,28,22,28},{22,22,28,18,22,18,28,24},
 {30,24,28,24,30,24,32,28},{24,20,24,28,20,24,28,24},
 {20,18,26,20,18,26,20,26},{28,20,24,28,20,24,32,24}
};
static const UBYTE harmony_steps[4]={0,5,7,0};
static const UBYTE triangle[16]={0x01,0x23,0x45,0x67,0x89,0xAB,0xCD,0xEF,0xFE,0xDC,0xBA,0x98,0x76,0x54,0x32,0x10};
/* Equal-tempered C3..B5 registervalues; square131072Hz/wave65536Hz numerators. */
static const UWORD square_freq[36]={1046u,1102u,1155u,1205u,1253u,1297u,1339u,1379u,1417u,1452u,1486u,1517u,1547u,1575u,1602u,1627u,1650u,1673u,1694u,1714u,1732u,1750u,1767u,1783u,1798u,1812u,1825u,1837u,1849u,1860u,1871u,1881u,1890u,1899u,1907u,1915u};
static const UWORD wave_freq[36]={1547u,1575u,1602u,1627u,1650u,1673u,1694u,1714u,1732u,1750u,1767u,1783u,1798u,1812u,1825u,1837u,1849u,1860u,1871u,1881u,1890u,1899u,1907u,1915u,1923u,1930u,1936u,1943u,1949u,1954u,1959u,1964u,1969u,1974u,1978u,1982u};
static UBYTE ready,muted,last_district=255,last_phase=255,step,bar,wait_frames;
static UWORD last_vblank;
static UWORD vblank_now(void){UWORD now;__critical {now=sys_time;}return now;}
static void silence(void){NR12_REG=0;NR22_REG=0;NR32_REG=0;NR42_REG=0;NR30_REG=0;}
void rf_audio_init(void) BANKED {UBYTE i;NR52_REG=0x80;NR50_REG=0x33;NR51_REG=0xFF;silence();for(i=0;i<16;i++)AUD3WAVE[i]=triangle[i];ready=1;muted=0;last_district=last_phase=255;step=bar=wait_frames=0;last_vblank=vblank_now();}
void rf_audio_mute(UBYTE value) BANKED {if(!ready)rf_audio_init();muted=value?1:0;if(muted)silence();else{last_district=last_phase=255;wait_frames=0;}}
static void audio_frame(UBYTE district,UBYTE phase) {
 UBYTE note,index,tempo;UWORD frequency;
 if(!ready)rf_audio_init();if(muted)return;if(district>=16)district=0;if(phase>2)phase=0;
 if(district!=last_district||phase!=last_phase){last_district=district;last_phase=phase;step=bar=wait_frames=0;NR22_REG=0;NR32_REG=0;NR42_REG=0;}
 if(wait_frames){wait_frames--;return;}
 tempo=rhythm[district][step]+(phase==2?8:phase==1?4:0);wait_frames=tempo-1;
 note=motifs[district][step];
 if(note==255)NR22_REG=0;
 else{index=roots[district]+12+note;frequency=square_freq[index];NR21_REG=0x80;NR22_REG=phase==2?0x23:0x43;NR23_REG=(UBYTE)frequency;NR24_REG=0x80|(frequency>>8);}
 if((step&1)==0){index=roots[district]+harmony_steps[bar];frequency=wave_freq[index];NR30_REG=0x80;NR31_REG=0;NR32_REG=0x60;NR33_REG=(UBYTE)frequency;NR34_REG=0x80|(frequency>>8);}
 /* Sparse short, low-volume noise texture. It is not a wildlife call. */
 if(step==0 && phase!=2){NR41_REG=52;NR42_REG=0x11;NR43_REG=0x65+(district&1);NR44_REG=0xC0;}
 step++;if(step==8){step=0;bar=(bar+1)&3;}
}
void rf_audio_sfx(UBYTE type) BANKED {static const UBYTE notes[4]={19,24,16,28};UWORD frequency;if(!ready)rf_audio_init();if(muted)return;if(type>3)type=0;frequency=square_freq[notes[type]];NR10_REG=0;NR11_REG=0x80|40;NR12_REG=0x52;NR13_REG=(UBYTE)frequency;NR14_REG=0xC0|(frequency>>8);}

/* Phase catch-up preserves tempo position across render/save stalls. It cannot
 * retroactively play missed audio; native stall duration/audio audition remain
 * gates. No banked function executes from VBlank ISR. 16-bit subtraction wraps.
 */
void rf_audio_update(UBYTE district,UBYTE phase) BANKED {
 UWORD now,elapsed;if(!ready)rf_audio_init();now=vblank_now();
 elapsed=(UWORD)(now-last_vblank);last_vblank=now;if(muted)return;
 if(district>=16)district=0;if(phase>2)phase=0;
 if(district!=last_district||phase!=last_phase){audio_frame(district,phase);if(elapsed)elapsed--;}
 while(elapsed){audio_frame(district,phase);elapsed--;}
}
