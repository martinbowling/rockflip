"""Compile authored Mojave journal JSON to a bounded banked native flag module.
No best-photo dependence: parent forwards every valid shutter event. No locality
fields enter the ROM. Generated files are owned source artifacts, not mock data.
"""
from pathlib import Path
import json,argparse
ROOT=Path(__file__).resolve().parents[2]

def emit_journal(root=ROOT):
    root=Path(root);source=json.loads((root/'data/journal_prototype.json').read_text())
    tasks=source['tasks'];assert len(tasks)==5 and [t['native_slot'] for t in tasks]==list(range(5))
    phases={'day':0,'dusk':1,'night':2};texts=[];photos=[];care=[];stages=[]
    photo_flags={};care_flags={};photo_index=0
    def lines(values):
        for s in values:
            if not isinstance(s,str) or len(s.encode('ascii'))>20:raise ValueError('Native journal text exceeds20ASCII columns')
        return values
    for n,t in enumerate(tasks):
        photo_mask=0;care_mask=0;note=None;done_mask=(1<<n)-1;must_closed=0
        expected=[] if n==0 else [tasks[n-1]['id']]
        assert t['prerequisite_task_ids']==expected
        for requirement in t['requirements_all']:
            kind=requirement['type']
            if kind=='photo_event':
                eligible=requirement['eligible_spot_ids'];assert 1<=len(eligible)<=2 and all(0<=s<1000 for s in eligible)
                stars=requirement['minimum_stars'];distance=requirement['minimum_distance'];focus=requirement['focus_frames_minimum']
                assert 1<=stars<=3 and 2<=distance<=4 and 1<=focus<=255 and requirement['require_safe_distance']
                assert 0<=requirement['species_id']<192
                bit=1<<photo_index;photo_flags[requirement['flag']]=bit;photo_mask|=bit
                photos.append({'species':requirement['species_id'],'phase':phases[requirement['phase']],'stars':stars,'distance':distance,'focus':focus,'count':len(eligible),'spots':eligible+[65535]*(2-len(eligible)),'bit':bit,'care':255})
                photo_index+=1
            elif kind=='care_after_photo':
                assert requirement['event_sequence']==['valid_photo_at_spot','restore_same_spot'] and requirement['requires_actual_flipped_rock'] and requirement['reward_once']
                index=len(care);assert index<2
                match=next(p for p in photos if p['species']==requirement['species_id'] and p['spots'][:p['count']]==requirement['eligible_spot_ids'])
                match['care']=index;care.append(match);care_mask|=1<<index;care_flags[requirement['care_flag']]=1<<index
            elif kind=='annotation_choice':
                assert note is None and requirement['retry']=='unlimited_immediate_no_penalty';note=requirement
            elif kind=='task_flags_all':
                assert requirement['task_ids']==[x['id'] for x in tasks[:n]]
            elif kind=='no_unrestored_rocks':
                assert requirement['spot_ids']==[0,5,6];must_closed=7
            else:raise ValueError('Unsupported journal requirement: '+kind)
        assert note is not None and len(note['options'])==3
        options=note['options'];assert len({o['id'] for o in options})==3 and all(len(o['lines'])==1 for o in options)
        rotated=options[n%3:]+options[:n%3];correct=next(i for i,o in enumerate(rotated) if o['id']==note['correct_option_id'])
        stage_text=[[t['title']],t['hint_lines'],note['prompt_lines'],[o['lines'][0] for o in rotated],[x for page in t['completion_dialogue_pages'] for x in page],['CHECK THE EVIDENCE.','PHOTO, NOTE, CARE.']]
        texts.append([lines(v) for v in stage_text]);stages.append([photo_mask,care_mask,1<<n,done_mask,must_closed,correct])
    assert photo_index==6 and len(care)==2
    texts.append([['FIRST SURVEY FILED'],['NEXT: OAK COUNTRY.'],[],[],['A FIRST MOJAVE STORY','MORE REGIONS AWAIT.'],[]])
    out=root/'native/plugins/rockflip/engine';out.mkdir(parents=True,exist_ok=True)
    header='''#ifndef ROCKFLIP_JOURNAL_H
#define ROCKFLIP_JOURNAL_H
#include <gb/gb.h>
#define RF_JOURNAL_STAGE_COUNT 5
/* Stable version-one layout inside the parent's32-byte RF02 quest flag buffer:
 * 0 donebits0..4;1photoevidencebits0..5;2annotationbits0..4;3carebits0..1;
 * 4 pendingkingsnake spotmask(0->bit0,6->bit1);5pendingtoad spotmask(5->bit0);
 * 6 currentopenrocks(0->bit0,5->bit1,6->bit2);7deliveredrewardbits0..4;
 * 8 bit0 firstMojavesurveyfiled;9bit0 D04lead;10..31 now owned by campaign/finale; journal leaves them untouched.\n * Layout5 reserves previously unused highbits0:5..7,1:6..7,2:5..7,\n * 3:2..7,4:2..7,5:1..7,6:3..7 for32 regionalchallenge awards;\n * 7bit5 is challenge mode. Every journal operation preserves these bits.
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
'''
    c='#pragma bank 255\n/* Generated by journal_compile.py from authored journal_prototype.json. */\n#include "rockflip_journal.h"\n#include <string.h>\n'
    c+='typedef struct {UBYTE species,phase,stars,distance,focus,count;UWORD spots[2];UBYTE bit,care;} RFJPhoto;\n'
    c+='static const RFJPhoto photos[]={'+','.join('{'+','.join(str(p[k]) for k in ['species','phase','stars','distance','focus','count'])+',{'+','.join(map(str,p['spots']))+'},'+str(p['bit'])+','+str(p['care'])+'}' for p in photos)+'};\n'
    c+='/* stage fields:photo mask,care mask,note mask,precedingdone,openblocked,correctdisplaychoice */\nstatic const UBYTE stages[5][6]='+json.dumps(stages).replace('[','{').replace(']','}')+';\n'
    for s,kinds in enumerate(texts):
        for k,value in enumerate(kinds):
            if value:c+=f'static const char text_{s}_{k}[][21]='+json.dumps(value).replace('[','{').replace(']','}')+';\n'
    c+='''
UBYTE rf_journal_stage(const UBYTE*flags) BANKED {UBYTE s;for(s=0;s<5;s++)if(!(flags[RF_J_DONE]&(1<<s)))return s;return 5;}
void rf_journal_rock(UBYTE*flags,UWORD spot,UBYTE open) BANKED {UBYTE bit=spot==0?1:spot==5?2:spot==6?4:0;if(open)flags[RF_J_OPEN_ROCKS]|=bit;else flags[RF_J_OPEN_ROCKS]&=~bit;}
void rf_journal_photo(UBYTE*flags,UBYTE species,UWORD spot,UBYTE phase,UBYTE stars,UBYTE distance,UBYTE focus) BANKED {
 UBYTE i,j;const RFJPhoto*p;
 if(stars>3||distance>4||distance<2||phase>2)return;
 for(i=0;i<6;i++){p=photos+i;if(species!=p->species||phase!=p->phase||stars<p->stars||distance<p->distance||focus<p->focus)continue;
  for(j=0;j<p->count;j++)if(spot==p->spots[j]){flags[RF_J_PHOTOS]|=p->bit;if(p->care!=255)flags[RF_J_PENDING_KING+p->care]|=1<<j;break;}}
}
void rf_journal_care(UBYTE*flags,UWORD spot) BANKED {
 UBYTE i,j,bit,openbit=spot==0?1:spot==5?2:spot==6?4:0;const RFJPhoto*p;UBYTE wasopen=flags[RF_J_OPEN_ROCKS]&openbit;rf_journal_rock(flags,spot,0);if(!wasopen)return;
 for(i=0;i<6;i++){p=photos+i;if(p->care==255)continue;for(j=0;j<p->count;j++){bit=1<<j;if(spot==p->spots[j]&&(flags[RF_J_PENDING_KING+p->care]&bit)){
  flags[RF_J_CARE]|=1<<p->care;flags[RF_J_PENDING_KING+p->care]&=~bit;}}}
}
UBYTE rf_journal_answer(UBYTE*flags,UBYTE choice) BANKED {
 UBYTE s=rf_journal_stage(flags);if(s>=5||choice>2||choice!=stages[s][5])return 0;flags[RF_J_NOTES]|=stages[s][2];return 1;
}
UBYTE rf_journal_turn_in(UBYTE*flags) BANKED {
 UBYTE s=rf_journal_stage(flags);const UBYTE*r;if(s>=5)return 0;r=stages[s];
 if((flags[RF_J_PHOTOS]&r[0])!=r[0]||(flags[RF_J_CARE]&r[1])!=r[1]||(flags[RF_J_NOTES]&r[2])!=r[2]||(flags[RF_J_DONE]&r[3])!=r[3]||(flags[RF_J_OPEN_ROCKS]&r[4]))return 0;
 flags[RF_J_DONE]|=1<<s;flags[RF_J_REWARDS]|=1<<s;if(s==3)flags[RF_J_LEAD]|=1;if(s==4)flags[RF_J_DISTRICT]|=1;return 1;
}
void rf_journal_text(UBYTE stage,UBYTE kind,UBYTE line,char*out) BANKED {out[0]=0;switch(stage){
'''
    for s,kinds in enumerate(texts):
        c+=f'case {s}:switch(kind){{'
        for k,value in enumerate(kinds):
            if value:c+=f'case {k}:if(line<{len(value)})strcpy(out,text_{s}_{k}[line]);break;'
        c+='}break;\n'
    c+='}}\n'
    (out/'include/rockflip_journal.h').write_text(header);(out/'src/rockflip_journal.c').write_text(c)
    return {'stage_count':5,'photo_requirements':6,'care_requirements':2,'correct_display_choices':[s[5] for s in stages],'flag_bytes_used':10,'generated_source_bytes':len(c)}

if __name__=='__main__':print(json.dumps(emit_journal(),indent=2))
