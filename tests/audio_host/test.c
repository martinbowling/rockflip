#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "audio-under-test.c"
static unsigned checks;
#define CHECK(c) do{checks++;assert(c);}while(0)
int main(void){
 UBYTE d,p,i;unsigned frame;
 rf_audio_init();CHECK(NR52_REG==0x80);CHECK(NR50_REG==0x33);CHECK(NR51_REG==255);CHECK(memcmp(AUD3WAVE,triangle,16)==0);
 for(i=0;i<36;i++){CHECK(square_freq[i]<2048);CHECK(wave_freq[i]<2048);if(i){CHECK(square_freq[i]>square_freq[i-1]);CHECK(wave_freq[i]>wave_freq[i-1]);}}
 for(d=0;d<16;d++){
  for(i=0;i<8;i++){CHECK(motifs[d][i]==255||roots[d]+12+motifs[d][i]<36);CHECK(rhythm[d][i]>=18&&rhythm[d][i]<=32);}
  for(p=0;p<3;p++){
   NR10_REG=17;NR11_REG=18;NR12_REG=19;NR13_REG=20;NR14_REG=21;
   for(frame=0;frame<1024;frame++){
    rf_audio_update(d,p);CHECK(last_district==d&&last_phase==p);CHECK(step<8&&bar<4);CHECK(wait_frames<40);CHECK(NR50_REG==0x33);
   }
   CHECK(NR10_REG==17&&NR11_REG==18&&NR12_REG==19&&NR13_REG==20&&NR14_REG==21);
  }
 }
 for(d=0;d<16;d++)for(i=d+1;i<16;i++)CHECK(memcmp(motifs[d],motifs[i],8)!=0);
 rf_audio_mute(1);CHECK(muted);CHECK(!NR12_REG&&!NR22_REG&&!NR32_REG&&!NR42_REG&&!NR30_REG);
 NR24_REG=1;NR34_REG=2;NR44_REG=3;NR14_REG=4;
 for(frame=0;frame<1024;frame++){rf_audio_update(255,255);rf_audio_sfx(1);}
 CHECK(NR24_REG==1&&NR34_REG==2&&NR44_REG==3&&NR14_REG==4);
 rf_audio_mute(0);rf_audio_update(255,255);CHECK(last_district==0&&last_phase==0);CHECK(NR22_REG!=0&&NR32_REG==0x60);
 for(i=0;i<5;i++){
  UBYTE a=NR22_REG,b=NR24_REG,c=NR32_REG,e=NR34_REG,f=NR42_REG,g=NR44_REG;
  rf_audio_sfx(i);CHECK(NR12_REG==0x52);CHECK((NR14_REG&0xC0)==0xC0);CHECK(NR22_REG==a&&NR24_REG==b&&NR32_REG==c&&NR34_REG==e&&NR42_REG==f&&NR44_REG==g);CHECK(NR50_REG==0x33&&NR51_REG==255);
 }
 printf("{\"passed\":true,\"assertions\":%u,\"districts\":16,\"phases\":3}\n",checks);return 0;
}
