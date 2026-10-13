#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "journal-under-test.c"
static unsigned checks;
#define CHECK(c) do{checks++;assert(c);}while(0)
static void photo(UBYTE*f,UBYTE species,UWORD spot,UBYTE phase){rf_journal_photo(f,species,spot,phase,2,3,45);}
int main(void){
 UBYTE f[32],snapshot[32],i,j;char text[23];const RFJPhoto*p;
 memset(f,0,sizeof(f));CHECK(rf_journal_stage(f)==0);CHECK(!rf_journal_turn_in(f));
 /* Every required event rejects each independently wrong predicate. */
 for(i=0;i<6;i++){
  p=photos+i;
  for(j=0;j<6;j++){
   memset(f,0,32);
   rf_journal_photo(f,j==0?p->species+20:p->species,j==1?999:p->spots[0],j==2?(p->phase+1)%3:p->phase,j==3?1:2,j==4?1:3,j==5?44:45);
   CHECK(!f[RF_J_PHOTOS]);
  }
  memset(f,0,32);photo(f,p->species,p->spots[0],p->phase);CHECK(f[RF_J_PHOTOS]&p->bit);
 }
 memset(f,0,32);rf_journal_care(f,0);CHECK(!f[RF_J_CARE]);photo(f,5,0,1);rf_journal_care(f,0);CHECK(!f[RF_J_CARE]);memset(f,0,32);
 photo(f,5,0,1);rf_journal_rock(f,0,1);rf_journal_care(f,6);CHECK(!f[RF_J_CARE]);CHECK(f[RF_J_OPEN_ROCKS]==1);
 rf_journal_care(f,0);CHECK(f[RF_J_CARE]==1);CHECK(!f[RF_J_OPEN_ROCKS]);CHECK(!f[RF_J_PENDING_KING]);
 rf_journal_care(f,0);CHECK(f[RF_J_CARE]==1);
 memset(f,0,32);photo(f,5,6,1);rf_journal_rock(f,6,1);rf_journal_care(f,0);CHECK(!f[RF_J_CARE]);rf_journal_care(f,6);CHECK(f[RF_J_CARE]==1);
 /* Full authored chain, evidence deliberately recorded before activation.
  * API does not receive album replacement status, so lower/equal photos credit. */
 memset(f,0,32);for(i=10;i<32;i++)f[i]=0xA5;
 photo(f,0,2,0);photo(f,2,3,0);photo(f,1,1,0);photo(f,5,0,1);photo(f,4,5,2);photo(f,12,7,2);
 CHECK(f[RF_J_PHOTOS]==63);CHECK(!f[RF_J_DONE]);rf_journal_rock(f,0,1);rf_journal_rock(f,5,1);
 CHECK(!rf_journal_answer(f,1));CHECK(!rf_journal_answer(f,2));CHECK(!f[RF_J_NOTES]);
 CHECK(rf_journal_answer(f,0));CHECK(rf_journal_turn_in(f));CHECK(rf_journal_stage(f)==1);CHECK(f[RF_J_DONE]==1);CHECK(f[RF_J_REWARDS]==1);
 CHECK(!rf_journal_turn_in(f));CHECK(f[RF_J_REWARDS]==1);
 CHECK(!rf_journal_answer(f,0));CHECK(rf_journal_answer(f,2));CHECK(rf_journal_turn_in(f));CHECK(rf_journal_stage(f)==2);
 CHECK(rf_journal_answer(f,1));CHECK(!rf_journal_turn_in(f));rf_journal_care(f,6);CHECK(!rf_journal_turn_in(f));rf_journal_care(f,0);CHECK(rf_journal_turn_in(f));CHECK(rf_journal_stage(f)==3);
 CHECK(rf_journal_answer(f,0));CHECK(!rf_journal_turn_in(f));rf_journal_care(f,5);CHECK(rf_journal_turn_in(f));CHECK(rf_journal_stage(f)==4);CHECK(f[RF_J_LEAD]==1);CHECK(!f[RF_J_DISTRICT]);
 CHECK(rf_journal_answer(f,2));rf_journal_rock(f,0,1);rf_journal_rock(f,6,1);CHECK(!rf_journal_turn_in(f));rf_journal_rock(f,0,0);CHECK(!rf_journal_turn_in(f));rf_journal_rock(f,6,0);CHECK(rf_journal_turn_in(f));CHECK(rf_journal_stage(f)==5);CHECK(f[RF_J_DONE]==31);CHECK(f[RF_J_REWARDS]==31);CHECK(f[RF_J_DISTRICT]==1);
 CHECK(!rf_journal_turn_in(f));CHECK(!rf_journal_answer(f,0));CHECK(f[RF_J_REWARDS]==31);
 memcpy(snapshot,f,32);memset(f,0,32);memcpy(f,snapshot,32);CHECK(rf_journal_stage(f)==5);
 for(i=10;i<32;i++)CHECK(f[i]==0xA5);
 /* Every text accessor isbounded/NULterminated; absent lines return empty. */
 for(i=0;i<6;i++)for(j=0;j<6;j++){
  unsigned line;
  for(line=0;line<16;line++){memset(text,'X',23);rf_journal_text(i,j,line,text);CHECK(strlen(text)<=20);CHECK(text[21]=='X'&&text[22]=='X');}
 }
 rf_journal_text(5,0,0,text);CHECK(strcmp(text,"FIRST SURVEY FILED")==0);
 rf_journal_text(200,0,0,text);CHECK(text[0]==0);
 printf("{\"passed\":true,\"assertions\":%u,\"stages\":5}\n",checks);return 0;
}
