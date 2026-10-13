#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <setjmp.h>
unsigned host_ram_bank,host_ram_enabled;
static unsigned checks;
static unsigned char host_sram[8192];
static unsigned writes,cutoff;
static unsigned fault_enabled;
static jmp_buf power_loss;
static void host_write(volatile unsigned char *p,unsigned offset,unsigned char value){
 if(fault_enabled && writes==cutoff)longjmp(power_loss,1);
 p[offset]=value;writes++;
}
#define CHECK(c) do{checks++;assert(c);}while(0)
#include "save-under-test.c"
static void closed(void){CHECK(host_ram_bank==0 && host_ram_enabled==0);}
int main(void){
 UBYTE payload[4080],copy[4080],legacy[64],sum,i;
 UWORD crc;unsigned cut;unsigned char previous[8192];
 memset(host_sram,255,8192);memset(payload,42,4080);
 CHECK(rf_store_load(copy,4080,legacy)==0);closed();
 crc=65535;for(i=0;i<9;i++)crc=crc_byte(crc,"123456789"[i]);CHECK(crc==0x29B1);
 rf_store_save(payload,4080);CHECK(rf_store_ok && valid_record(slot_pointer(0),1));closed();
 CHECK(rf_store_load(copy,4080,legacy)==1 && memcmp(payload,copy,4080)==0);closed();
 payload[4079]=99;rf_store_save(payload,4080);CHECK(rf_store_ok && valid_record(slot_pointer(1),1));closed();
 CHECK(rf_store_load(copy,4080,legacy)==1 && copy[4079]==99);closed();
 host_sram[4096+16+4079]^=1;CHECK(rf_store_load(copy,4080,legacy)==1 && copy[4079]==42);closed();
 rf_store_save(payload,4080);CHECK(rf_store_ok);host_sram[4096]=0;
 CHECK(rf_store_load(copy,4080,legacy)==1 && copy[4079]==42);closed();
 memset(host_sram,255,8192);memset(host_sram,0,64);memcpy(host_sram,"RF01",4);
 sum=0;for(i=0;i<63;i++)sum+=host_sram[i];host_sram[63]=sum;
 CHECK(rf_store_load(copy,4080,legacy)==2 && memcmp(legacy,host_sram,64)==0);closed();
 rf_store_save(payload,4080);CHECK(rf_store_ok && valid_legacy(slot_pointer(0)) && valid_record(slot_pointer(1),1));closed();
 CHECK(rf_store_load(copy,4080,legacy)==1 && copy[4079]==99);closed();
 memset(host_sram,255,8192);memcpy(host_sram,"RF03",4);CHECK(rf_store_load(copy,4080,legacy)==3 && rf_store_locked);closed();
 rf_store_save(payload,4080);CHECK(!rf_store_ok && memcmp(host_sram,"RF03",4)==0);closed();
 memset(host_sram,255,8192);rf_store_locked=0;rf_store_save(payload,4080);
 host_sram[8]=255;host_sram[9]=255;crc=record_crc(host_sram,4080);host_sram[10]=crc;host_sram[11]=crc>>8;
 payload[0]=88;rf_store_save(payload,4080);CHECK(rf_store_ok && read_word(slot_pointer(1),8)==0);closed();
 CHECK(rf_store_load(copy,4080,legacy)==1 && copy[0]==88);closed();
 CHECK(rf_store_load(copy,4000,legacy)==3 && rf_store_locked);closed();
 rf_store_locked=0;rf_store_save(payload,4081);CHECK(!rf_store_ok);closed();
 /* Inject power loss BEFORE every actual SRAM write in the transformed save
  * function. Source has 16 header stores + payload + 2 CRC + final commit.
  * Two good existing records ensure the destination is an older valid slot. */
 memset(host_sram,255,8192);rf_store_locked=0;memset(payload,31,64);
 rf_store_save(payload,64);payload[0]=32;rf_store_save(payload,64);memcpy(previous,host_sram,8192);
 payload[0]=33;
 for(cut=0;cut<83;cut++){
  memcpy(host_sram,previous,8192);writes=0;cutoff=cut;fault_enabled=1;
  if(!setjmp(power_loss))rf_store_save(payload,64);
  fault_enabled=0;host_ram_enabled=0;host_ram_bank=0; /* simulated reboot */
  CHECK(rf_store_load(copy,64,legacy)==1 && copy[0]==32);closed();
 }
 memcpy(host_sram,previous,8192);rf_store_save(payload,64);
 CHECK(rf_store_load(copy,64,legacy)==1 && copy[0]==33);closed();
 /* Repeat every interruption point on a first RF01 migration write. */
 memset(host_sram,255,8192);memset(host_sram,0,64);memcpy(host_sram,"RF01",4);
 sum=0;for(i=0;i<63;i++)sum+=host_sram[i];host_sram[63]=sum;
 memcpy(previous,host_sram,8192);
 for(cut=0;cut<83;cut++){
  memcpy(host_sram,previous,8192);writes=0;cutoff=cut;fault_enabled=1;rf_store_locked=0;
  if(!setjmp(power_loss))rf_store_save(payload,64);
  fault_enabled=0;host_ram_enabled=0;host_ram_bank=0;
  CHECK(rf_store_load(copy,64,legacy)==2 && memcmp(legacy,previous,64)==0);closed();
 }

 /* Baseline368 checks above remain unchanged. Snapshot-layout extension tests
  * exercise the actual source control flow; these are not emulator proofs. */
 assert(checks==368);
 memset(host_sram,255,8192);rf_store_locked=0;
 for(crc=0;crc<RF_STORE_PRE_SNAPSHOT_SIZE;crc++)payload[crc]=(UBYTE)(crc%251);
 rf_store_save(payload,RF_STORE_PRE_SNAPSHOT_SIZE);
 CHECK(rf_store_ok && host_sram[5]==1 && read_word(host_sram,6)==RF_STORE_PRE_SNAPSHOT_SIZE);closed();
 memcpy(previous,host_sram,8192);memset(copy,255,4080);
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==4 && rf_store_ok && !rf_store_locked);closed();
 CHECK(memcmp(copy,payload,RF_STORE_PRE_SNAPSHOT_SIZE)==0);
 for(crc=RF_STORE_PRE_SNAPSHOT_SIZE;crc<RF_STORE_SNAPSHOT_SIZE;crc++)CHECK(copy[crc]==0);
 CHECK(memcmp(previous,host_sram,8192)==0); /* load performs no SRAM mutation */
 /* The first schema2 write must preserve the sole verified old RF02 slot. */
 memcpy(payload,copy,RF_STORE_SNAPSHOT_SIZE);payload[RF_STORE_PRE_SNAPSHOT_SIZE]=0x80;
 rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);
 CHECK(rf_store_ok && host_sram[4096+5]==2 && read_word(slot_pointer(1),6)==RF_STORE_SNAPSHOT_SIZE);closed();
 CHECK(memcmp(previous,host_sram,4096)==0 && valid_record(slot_pointer(0),1));
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==1 && copy[RF_STORE_PRE_SNAPSHOT_SIZE]==0x80);closed();
 /* Metadata and snapshot CRC corruption cannot bless a bad new record. */
 host_sram[4096+16+RF_STORE_PRE_SNAPSHOT_SIZE]^=1;
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==4 && copy[RF_STORE_PRE_SNAPSHOT_SIZE]==0);closed();
 rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);CHECK(rf_store_ok);closed();
 host_sram[4096+8]^=1;
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==4);closed();
 rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);CHECK(rf_store_ok);closed();
 CHECK(rf_store_load(copy,RF_STORE_PRE_SNAPSHOT_SIZE,legacy)==3 && rf_store_locked);closed();
 memcpy(previous,host_sram,8192);rf_store_save(payload,RF_STORE_PRE_SNAPSHOT_SIZE);
 CHECK(!rf_store_ok && memcmp(previous,host_sram,8192)==0);closed();
 /* Unsupported schema/size pairs lock without altering either record. */
 for(i=0;i<4;i++){
  memset(host_sram,255,8192);rf_store_locked=0;rf_store_save(payload,64);
  if(i==0){host_sram[5]=2;} /* schema2/64 */
  if(i==1){host_sram[5]=3;} /* future schema */
  if(i==2){host_sram[6]=(UBYTE)RF_STORE_SNAPSHOT_SIZE;host_sram[7]=(UBYTE)(RF_STORE_SNAPSHOT_SIZE>>8);} /* schema1/2448 */
  if(i==3){host_sram[4]=3;} /* future format version */
  memcpy(previous,host_sram,8192);
  CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==3 && rf_store_locked);closed();
  rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);CHECK(!rf_store_ok && memcmp(previous,host_sram,8192)==0);closed();
 }
 /* RF01 still migrates directly into schema2 without erasing its checksum. */
 memset(host_sram,255,8192);memset(host_sram,0,64);memcpy(host_sram,"RF01",4);
 sum=0;for(i=0;i<63;i++)sum+=host_sram[i];host_sram[63]=sum;memcpy(previous,host_sram,8192);rf_store_locked=0;
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==2);closed();rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);
 CHECK(rf_store_ok && valid_legacy(slot_pointer(0)) && valid_record(slot_pointer(1),1) && slot_pointer(1)[5]==2);closed();
 CHECK(memcmp(previous,host_sram,64)==0);
 /* All2467 actual byte-store cut points, first schema1->schema2 migration. */
 memset(host_sram,255,8192);rf_store_locked=0;memset(payload,51,RF_STORE_PRE_SNAPSHOT_SIZE);rf_store_save(payload,RF_STORE_PRE_SNAPSHOT_SIZE);memcpy(previous,host_sram,8192);
 memset(payload,52,RF_STORE_SNAPSHOT_SIZE);
 for(cut=0;cut<RF_STORE_SNAPSHOT_SIZE+19;cut++){
  memcpy(host_sram,previous,8192);writes=0;cutoff=cut;fault_enabled=1;rf_store_locked=0;
  if(!setjmp(power_loss))rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);
  fault_enabled=0;host_ram_enabled=0;host_ram_bank=0;
  CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==4 && copy[0]==51 && copy[RF_STORE_PRE_SNAPSHOT_SIZE]==0);closed();
  CHECK(memcmp(previous,host_sram,4096)==0);
 }
 memcpy(host_sram,previous,8192);writes=0;rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);
 CHECK(writes==RF_STORE_SNAPSHOT_SIZE+19 && rf_store_ok);closed();
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==1 && copy[0]==52 && copy[RF_STORE_PRE_SNAPSHOT_SIZE]==52);closed();
 /* All2467 cut points overwriting an older valid schema2 slot. */
 payload[0]=53;rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);memcpy(previous,host_sram,8192);payload[0]=54;
 for(cut=0;cut<RF_STORE_SNAPSHOT_SIZE+19;cut++){
  memcpy(host_sram,previous,8192);writes=0;cutoff=cut;fault_enabled=1;rf_store_locked=0;
  if(!setjmp(power_loss))rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);
  fault_enabled=0;host_ram_enabled=0;host_ram_bank=0;
  CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==1 && copy[0]==53);closed();
 }
 memcpy(host_sram,previous,8192);rf_store_save(payload,RF_STORE_SNAPSHOT_SIZE);
 CHECK(rf_store_load(copy,RF_STORE_SNAPSHOT_SIZE,legacy)==1 && copy[0]==54);closed();

 /* Same-size3/4/5->6 with every real streaming byte-store interruption. */
 for(i=3;i<=5;i++){
  memset(host_sram,255,8192);rf_store_locked=0;memset(payload,51,2544);rf_store_save(payload,2544);CHECK(host_sram[5]==6);
  host_sram[5]=i;crc=record_crc(slot_pointer(0),2544);host_sram[10]=(UBYTE)crc;host_sram[11]=(UBYTE)(crc>>8);
  memcpy(previous,host_sram,8192);CHECK(rf_store_load(copy,2544,legacy)==4 && rf_store_loaded_layout==i && !rf_store_locked);CHECK(memcmp(copy,payload,2544)==0);closed();
  payload[0]=52;
  for(cut=0;cut<2563;cut++){
   memcpy(host_sram,previous,8192);fault_enabled=1;cutoff=cut;writes=0;
   if(!setjmp(power_loss))rf_store_save(payload,2544);
   fault_enabled=0;host_ram_bank=0;host_ram_enabled=0;CHECK(rf_store_load(copy,2544,legacy)==4 && rf_store_loaded_layout==i && copy[0]==51);closed();CHECK(memcmp(previous,host_sram,4096)==0);
  }
  memcpy(host_sram,previous,8192);rf_store_save(payload,2544);CHECK(rf_store_ok && host_sram[4096+5]==6);CHECK(memcmp(previous,host_sram,4096)==0);CHECK(rf_store_load(copy,2544,legacy)==1 && rf_store_loaded_layout==6 && copy[0]==52);closed();
 }
 /* Unsupported future7 is write locked, even while predecessor6 remains. */
 memcpy(previous,host_sram,8192);host_sram[4096+5]=7;memcpy(previous,host_sram,8192);CHECK(rf_store_load(copy,2544,legacy)==3 && rf_store_locked);rf_store_save(payload,2544);CHECK(memcmp(previous,host_sram,8192)==0);closed();
 printf("{\"passed\":true,\"assertions\":%u,\"baseline_assertions\":368,\"torn_write_cut_points\":12789,\"schema2_migration_cut_points\":2467,\"schema2_overwrite_cut_points\":2467,\"same_size3_4_5_to6_cut_points\":7689}\n",checks);
 return 0;
}
