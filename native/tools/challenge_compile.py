"""Validate and stage optional challenge banked code; no canonical writes."""
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
KINDS=['title','brief','hint','care','retry','rule']
def validate(data):
    records=data['records'];assert len(records)==32
    assert len({r['id']for r in records})==32 and len({r['species_id']for r in records})==32
    assert [r['index']for r in records]==list(range(32))
    sites={s['spot_id']:s for s in json.loads((ROOT/'data/foundation_encounters.json').read_text())['records']}
    world={m['id']:m for m in json.loads((ROOT/'data/world.json').read_text())['maps']}
    roster={r['species_id']:r for r in json.loads((ROOT/'data/production_roster.json').read_text())['records']}
    runtime=json.loads((ROOT/'data/species.json').read_text())
    for district in range(16):assert len([r for r in records if r['district']==district])==2
    for r in records:
        sid=r['species_id'];h=r['approved_hint_site'];s=sites[h['spot_id']];m=world[h['map_id']]
        assert sid<150 and r['scientific_name']==runtime[sid]['scientific_name']
        assert r['district']==r['index']//2 and r['region_id']==f"D{r['district']+1:02d}"
        assert s['species_id']==sid and s['room_id']==h['map_id'] and s['region_id']==r['region_id'] and s['habitat_id']==h['habitat_id']
        assert s['phase_mask']&(1<<h['phase']) and h['subarea_id']==m['subarea_id']
        p=next(p for p in roster[sid]['region_permissions']if p['region_id']==r['region_id']and h['habitat_id']in p['habitat_ids'])
        assert not p.get('subarea_ids')or h['subarea_id']in p['subarea_ids']
        assert not r['required_for_ending'] and r['completion']=={'kind':'persistent_regional_shutter','minimum_stars':3,'species_id':sid,'map_id':h['map_id'],'spot_id':h['spot_id'],'phase':h['phase'],'counts_existing_photo_anywhere':False,'new_save_flags':True,'new_save_bytes':0,'reserved_journal_bits_layout':5}
        assert r['source_urls'] and all(u.startswith('https://')for u in r['source_urls'])
        for kind in KINDS:
            assert 1<=len(r[kind])<=3
            for line in r[kind]:assert line and len(line)<=20 and line.isascii()
        if sid in(61,73):assert 'DRY LAND' in ' '.join(r['brief']) and 'FOUR' in ' '.join(r['hint'])
    return records

def compile(data,out):
    r=validate(data);out.mkdir(parents=True,exist_ok=True);(out/'include').mkdir(exist_ok=True);(out/'src').mkdir(exist_ok=True)
    header='''#ifndef ROCKFLIP_CHALLENGES_H\n#define ROCKFLIP_CHALLENGES_H\n#include <gbdk/platform.h>\n#define RF_CHALLENGE_COUNT 32u\n/* Global index = district * 2 + local index. Invalid target = 255.\n * Kind 0 title(1),1 brief(2),2 hint(3),3 care(1),4 retry(2),5 rule(3).\n * Completion uses persisted reserved journal highbits, layout5; verified oldbest awards migrate once. */\nvoid rf_challenge_fresh(void) BANKED;\nvoid rf_challenge_migrate(void) BANKED;\nUBYTE rf_challenge_awards_valid(void) BANKED;\nUBYTE rf_challenge_record(void) BANKED;\nUBYTE rf_challenge_count(UBYTE district) BANKED;\nUBYTE rf_challenge_species(UBYTE index) BANKED;\nUBYTE rf_challenge_district(UBYTE index) BANKED;\nUWORD rf_challenge_spot(UBYTE index) BANKED;\nUWORD rf_challenge_map(UBYTE index) BANKED;\nUBYTE rf_challenge_phase(UBYTE index) BANKED;\nUBYTE rf_challenge_complete(const UBYTE *best,UBYTE index) BANKED;\nUBYTE rf_challenge_completed(const UBYTE *best,UBYTE district) BANKED;\nUBYTE rf_challenge_total_completed(const UBYTE *best) BANKED;\nvoid rf_challenge_text(UBYTE index,UBYTE kind,UBYTE line,char *out) BANKED;\n#endif\n'''
    strings=[]
    for x in r:
        strings.append('{'+','.join('{'+','.join(json.dumps(t)for t in x[k]+['']*(3-len(x[k])))+'}'for k in KINDS)+'}')
    targets=','.join('{'+f"{x['species_id']},{x['approved_hint_site']['spot_id']},{x['approved_hint_site']['map_id']},{x['approved_hint_site']['phase']}"+'}'for x in r)
    source='''#pragma bank 255\n#include "rockflip_challenges.h"\n#include "rockflip_runtime.h"\n#include <string.h>\ntypedef struct{UBYTE species;UWORD spot,map;UBYTE phase;} Challenge;\nstatic const Challenge targets[32]={'''+targets+'''};\nstatic const char words[32][6][3][21]={'''+','.join(strings)+'''};\nUBYTE rf_challenge_count(UBYTE d) BANKED{return d<16?2:0;}\nUBYTE rf_challenge_species(UBYTE i) BANKED{return i<32?targets[i].species:255;}\nUBYTE rf_challenge_district(UBYTE i) BANKED{return i<32?i/2:255;}\nUWORD rf_challenge_spot(UBYTE i) BANKED{return i<32?targets[i].spot:65535;}\nUWORD rf_challenge_map(UBYTE i) BANKED{return i<32?targets[i].map:65535;}\nUBYTE rf_challenge_phase(UBYTE i) BANKED{return i<32?targets[i].phase:255;}\n/* Layout5 reuses ONLY journal bits explicitly unused by layouts1..4.\n * byte0 bits5..7;byte1 bits6..7;byte2 bits5..7;byte3 bits2..7;\n * byte4 bits2..7;byte5 bits1..7;byte6 bits3..7. Mode byte7bit5.\n * Existing journal masks never touch these bits. No RFState payload growth. */\nstatic const UBYTE award_byte[32]={0,0,0,1,1,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5,5,5,5,6,6,6,6,6};\nstatic const UBYTE award_mask[32]={32,64,128,64,128,32,64,128,4,8,16,32,64,128,4,8,16,32,64,128,2,4,8,16,32,64,128,8,16,32,64,128};\nstatic const UBYTE journal_keep[7]={31,63,31,3,3,1,7};\nstatic void clear_awards(void){UBYTE i;for(i=0;i<7;i++)rf.quest_flags[i]&=journal_keep[i];}\nvoid rf_challenge_fresh(void) BANKED{clear_awards();rf.quest_flags[7]|=32;}\nvoid rf_challenge_migrate(void) BANKED{UBYTE i;clear_awards();for(i=0;i<32;i++)if(rf.best[targets[i].species]>=3)rf.quest_flags[award_byte[i]]|=award_mask[i];rf.quest_flags[7]|=32;}\nUBYTE rf_challenge_awards_valid(void) BANKED{if(rf.quest_flags[7]&32)return 1;return 0;}\nUBYTE rf_challenge_record(void) BANKED{UBYTE i;UWORD spot;\n if(!(rf.quest_flags[7]&32)||rf.score!=3||rf.spot>=rf_map.spot_count)return 0;\n spot=rf_map.spots[rf.spot];\n for(i=0;i<32;i++)if(rf.species==targets[i].species&&rf.room==targets[i].map&&spot==targets[i].spot&&rf.phase==targets[i].phase){\n  if(rf.quest_flags[award_byte[i]]&award_mask[i])return 0;\n  rf.quest_flags[award_byte[i]]|=award_mask[i];return 1;\n }\n return 0;\n}\n/* Preserve caller ABI while completion now reads explicit persisted awards.\n * b is retained only for existing invalid/null API contract, never derived. */\nUBYTE rf_challenge_complete(const UBYTE*b,UBYTE i) BANKED{if(!b||i>=32)return 0;if(rf.quest_flags[award_byte[i]]&award_mask[i])return 1;return 0;}\n\nUBYTE rf_challenge_completed(const UBYTE*b,UBYTE d) BANKED{UBYTE i,n=0;if(d>=16)return 0;for(i=d*2;i<d*2+2;i++)if(rf_challenge_complete(b,i))n++;return n;}\nUBYTE rf_challenge_total_completed(const UBYTE*b) BANKED{UBYTE i,n=0;for(i=0;i<32;i++)if(rf_challenge_complete(b,i))n++;return n;}\nvoid rf_challenge_text(UBYTE i,UBYTE k,UBYTE l,char*out) BANKED{out[0]=0;if(i<32&&k<6&&l<3)strcpy(out,words[i][k][l]);}\n'''
    (out/'include/rockflip_challenges.h').write_text(header);(out/'src/rockflip_challenges.c').write_text(source)
    receipt={'result':'pass','layer':'authored_staged_bank_module_not_native_integrated','records':32,'distinct_species':32,'districts':16,'mandatory_for_ending':False,'json_sha256':hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'header_sha256':hashlib.sha256(header.encode()).hexdigest()}
    (out/'compile-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=ROOT/'data/photo_challenges.json');p.add_argument('--out',type=Path,default=ROOT/'native/plugins/rockflip/engine');a=p.parse_args();print(json.dumps(compile(json.loads(a.data.read_text()),a.out),indent=2))
