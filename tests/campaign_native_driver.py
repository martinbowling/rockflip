"""Controller-only campaign helpers for a root-owned native PyBoy harness.

Import this module; it never boots a ROM or writes emulator memory itself. Pass
root harness globals/dict containing press/check/value/flags/travel/rest_to/face/
tick/pb/HIDDEN/sites/world. The callbacks must use actual controller inputs;
travel must follow the current16-region atlas, routes and ferry confirmation.
Reading flags/state is observation, never injected quest/photo progress.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def _screen(h):return h['value'](0)
def _check(h,label,condition):h['check'](label,condition)
def _stage(h,d):return (h['flags']()[10+d//4]>>((d%4)*2))&3

def _world(h):
    w=h['world'];return w if isinstance(w,dict) else {m['id']:m for m in w}
def _sites(h):
    s=h['sites'];return list(s.values()) if isinstance(s,dict) else s

def return_to_trail(h):
    """Exit only the root's known journal/campaign/exhibit menus, by input."""
    for _ in range(8):
        screen=_screen(h)
        if screen==2:return
        if screen==22:h['press']('b')
        elif screen in {9,13,14,15,17,18,19,20,21,23,24,25,26}:h['press']('b')
        else:raise AssertionError(f'Cannot return to trail from unexpected screen{screen}')
    raise AssertionError('Menu return did not reach trail within eight inputs')

def photo_target(h,target):
    """Legal walk/rest/look/focus/shutter/care, never best-photo injection.

    Target accepts campaign predicate or an integer globalspotID. Two-star
    focused distance4 photographs suffice; subject centering is optional here.
    Natural hide periods are observed through the root HIDDEN symbol.
    """
    if isinstance(target,int):
        spot=target;site=next(s for s in _sites(h) if s['spot_id']==spot)
        target={'spot_id':spot,'species_id':site['species_id'],'map_id':site['room_id'],'phase':next(i for i in range(3) if site['phase_mask']&(1<<i)),'minimum_stars':2,'minimum_focus':45,'minimum_distance':3 if site['species_id']==0 else 2}
    site=next(s for s in _sites(h) if s['spot_id']==target['spot_id']);assert site['species_id']==target['species_id'] and site['room_id']==target['map_id']
    return_to_trail(h);h['travel'](target['map_id']);h['rest_to'](target['phase']);h['face'](site)
    _check(h,f"campaign legal map{target['map_id']} and phase{target['phase']}",h['value'](1)==target['map_id'] and h['value'](4)==target['phase'])
    for attempt in range(3):
        h['press']('a',100)
        if _screen(h)==3:break
        _check(h,'eligible retry remains on trail',_screen(h)==2)
        if site['interaction_type'] in {0,5}:h['press']('b',150)
    _check(h,f"bounded encounter at exactsite{site['spot_id']}",_screen(h)==3 and h['value'](6)==target['species_id'])
    h['press']('a');_check(h,'campaign viewfinder opens',_screen(h)==4)
    # Start at camera distance4 and preserve it. No chase or required perfectscore.
    for attempt in range(160):
        h['tick'](6)
        hidden=bool(h['pb'].memory[h['HIDDEN']]) if h.get('HIDDEN') is not None else False
        if h['value'](7)>=target['minimum_focus'] and not hidden:
            # The 2448-byte streaming commit and result draw span VBlanks.
            # Do not issue a second shutter while that real save is pending.
            h['press']('a',150)
            if _screen(h)==5:break
            _check(h,'hidden-frame shutter retry stays in camera',_screen(h)==4)
    _check(h,f"qualifying focused photo at site{site['spot_id']}",_screen(h)==5 and h['value'](11)>=target['minimum_stars'] and h['value'](8)>=target['minimum_distance'])
    h['press']('b');_check(h,'photo return keeps habitat context',_screen(h)==2)
    if site['interaction_type'] in {0,5}:h['press']('b',150)
    return site

def _open_journal(h):
    return_to_trail(h);h['open_camp']();h['press']('up');_check(h,'opening journal opens by controller',_screen(h)==13)
def _opening_note(h,choice):
    h['press']('a');_check(h,'opening caption menu',_screen(h)==14)
    for _ in range(choice):h['press']('down')
    h['press']('a');_check(h,'opening caption feedback',_screen(h)==15);h['press']('b');_check(h,'opening feedback returns to journal',_screen(h)==13)

def complete_opening(h):
    """Actually finish five Mojave tasks; no direct prerequisite flag seeding."""
    source=json.loads((ROOT/'data/journal_prototype.json').read_text());start=h['flags']()[0]&31
    for n,task in enumerate(source['tasks']):
        if h['flags']()[0]&(1<<n):continue
        for requirement in task['requirements_all']:
            if requirement['type']=='photo_event':photo_target(h,requirement['eligible_spot_ids'][0])
        note=next(r for r in task['requirements_all'] if r['type']=='annotation_choice');rotated=note['options'][n%3:]+note['options'][:n%3];choice=next(i for i,o in enumerate(rotated) if o['id']==note['correct_option_id'])
        _open_journal(h);_opening_note(h,choice);h['press']('start');_check(h,'opening turn-in feedback',_screen(h)==15)
        expected=(1<<(n+1))-1;_check(h,f'opening task{n+1} legally complete',h['flags']()[0]&31==expected);h['press']('b');return_to_trail(h)
    _check(h,'all five opening tasks complete through input',h['flags']()[0]&31==31)
    return {'opening_done':True,'initial_completed_bits':start,'ending_completed_bits':h['flags']()[0]&31}

def _local_campaign(h,d):
    # Ensure the observed world district is the intended localcamp investigation.
    return_to_trail(h)
    _check(h,f'local district{d} matches current map',_world(h)[h['value'](1)]['district_id']==f'D{d+1:02d}')
    h['open_camp']();_check(h,'camp for campaign',_screen(h)==9);h['press']('down');_check(h,'regional campaign opens',_screen(h)==17)

def complete_regions_and_exhibit(h,photo=photo_target,with_secret=True):
    """Complete48regionalstages, four exhibit answers and realcredits screens.

    Existing earned photo/note flags may be consumed, but actual missing photos
    are obtained by the provided controller helper. Complete_opening separately.
    This does not claim hidden unlocked before150regularphotos exist.
    """
    data=json.loads((ROOT/'data/campaign.json').read_text());completed=[]
    _check(h,'opening prerequisite present from actual journal play',h['flags']()[0]&31==31)
    for district in data['districts']:
        d=district['native_district']
        for st in district['stages']:
            if _stage(h,d)>st['stage_index']:continue
            _check(h,'regional stage progression ordered',_stage(h,d)==st['stage_index'])
            for i in st['photo_target_indexes']:photo(h,district['photo_targets'][i])
            _local_campaign(h,d);h['press']('a');_check(h,'regional caption menu',_screen(h)==18)
            for _ in range(st['correct_choice']):h['press']('down')
            h['press']('a');_check(h,'regional note feedback',_screen(h)==19);h['press']('b');_check(h,'regional note returns to overview',_screen(h)==17)
            h['press']('start');_check(h,'regional turn-in feedback',_screen(h)==19);_check(h,st['id']+' legally advances',_stage(h,d)==st['stage_index']+1)
            completed.append(st['id']);h['press']('b');return_to_trail(h)
        _check(h,f'D{d+1:02d} full investigation complete',_stage(h,d)==3)
    _check(h,'all sixteen investigations complete',all(_stage(h,d)==3 for d in range(16)))
    return_to_trail(h);h['open_camp']();h['press']('left');_check(h,'actual exhibit opens',_screen(h)==20)
    for n,q in enumerate(data['finale_questions']):
        if h['flags']()[30]&(1<<n):continue
        h['press']('a');_check(h,'exhibit caption question',_screen(h)==21)
        for _ in range(q['correct_choice']):h['press']('down')
        h['press']('a');_check(h,'correct caption returns to exhibit',_screen(h)==20);_check(h,f'exhibit caption{n+1} persists',h['flags']()[30]&(1<<n))
    _check(h,'all four exhibit captions completed',h['flags']()[30]&15==15)
    h['press']('a');_check(h,'real native credits screen opens',_screen(h)==22);h['press']('b');_check(h,'credits return to postgame exhibit',_screen(h)==20)
    _check(h,'credits acknowledgment persists',h['flags']()[30]&16)
    if with_secret:answer_secret(h,already_exhibit=True)
    return_to_trail(h)
    return {'stages_completed_this_call':completed,'all16_complete':True,'exhibit_complete':True,'credits_observed':True,'hidden_ready':bool(h['flags']()[31]&128)}

def answer_secret(h,already_exhibit=False):
    """Read/answer optional postgame clue via input; verifyactualregularcount gate."""
    if not already_exhibit:return_to_trail(h);h['open_camp']();h['press']('left')
    _check(h,'secret starts at actual exhibit',_screen(h)==20);h['press']('start');_check(h,'optional secret clue screen',_screen(h)==23);h['press']('a');_check(h,'optional secret caption choices',_screen(h)==24)
    choice=json.loads((ROOT/'data/campaign.json').read_text())['hidden_clue']['correct_choice']
    for _ in range(choice):h['press']('down')
    h['press']('a');_check(h,'secret answer returns to clue',_screen(h)==23);_check(h,'correct secret answer persists',h['flags']()[31]&2)
    if 'best' in h:
        regular=sum(bool(h['best'](sid)) for sid in range(150));_check(h,'hidden unlock follows actual150regularphotos',bool(h['flags']()[31]&128)==(regular==150))
    h['press']('b');_check(h,'secret returns to exhibit',_screen(h)==20)
