"""Real native timer rollovers through waiting and controller input only.

Two observed 16-bit system-clock rollovers, one on a water/camp screen and
one inside a wildlife camera. No memory injection, no campaign-hours claim.
"""
from pathlib import Path
import sys, argparse, json, hashlib, tempfile, shutil
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from native_weather_migration import setup, read
from native_snapshot_migration import open_rom, latest

p = argparse.ArgumentParser()
p.add_argument('--rom', type=Path, default=ROOT/'native/build/rom/RockFlip-Statewide.gbc')
p.add_argument('--noi', type=Path)
p.add_argument('--expected-sha', required=True)
p.add_argument('--out', type=Path, default=ROOT/'output/qa/native-soak')
a = p.parse_args()
assert hashlib.sha256(a.rom.read_bytes()).hexdigest() == a.expected_sha
a.out.mkdir(parents=True, exist_ok=True)
h = setup(a.rom, a.noi or Path(str(a.rom)+'.debug/symbols.noi'))
h['OUT'] = a.out
check = h['check']
wraps = []

def object_budget():
    pb = h['pb']
    raw = bytes(pb.memory[0xfe00:0xfea0])
    height = 16 if pb.memory[0xff40]&4 else 8
    visible = [(raw[i]-16,raw[i+1]-8) for i in range(0,160,4)
               if 0<raw[i]<160 and 0<raw[i+1]<168]
    check('long idle actual OAM remains within hardware limits',
          len(visible)<=40 and max((sum(y<=s<y+height for y,x in visible)
                                    for s in range(144)),default=0)<=10)

def wait_rollover(context, screen, stable):
    before = h['word'](h['symbol']('sys_time'))
    start = h['frames']
    seen = False
    while h['frames']-start < 66560:
        h['tick'](128)
        now = h['word'](h['symbol']('sys_time'))
        if now<before:
            seen = True
            wraps.append({'context':context,'frame':h['frames'],
                          'before':before,'after':now})
        check(context+' native VBlank time advances modulo65536',
              (now-before)&65535 == 128)
        check(context+' remains in requested gameplay screen',h['screen']()==screen)
        check(context+' retains earned album/journal/cover data',stable())
        object_budget()
        before = now
    check(context+' actual system clock wraps without injected memory',seen)
    h['snapshot'](context+'-after-wrap')

with tempfile.TemporaryDirectory(prefix='rockflip-native-soak-') as tmp:
    cart = Path(tmp)/a.rom.name
    shutil.copy2(a.rom,cart)
    open_rom(h,cart)
    h['enter_hike']()
    h['travel'](1)
    base = read(h,0,2544)
    wait_rollover('water-camp-hike',2,lambda:read(h,0,2544)==base)
    # The actual physical camp remains usable after timer wrap and saves the
    # same progression. This also catches stale idle input being replayed.
    h['open_camp']()
    check('camp controller input works after long idle',h['screen']()==9)
    h['press']('b',150)
    check('camp returns to hike after long idle',h['screen']()==2)
    site = next(s for s in h['sites'] if s['spot_id']==0)
    h['open_subject'](site)
    preserved = (read(h,h['offset'](15),192),
                 read(h,h['offset'](19),1000),bytes(h['flags']()))
    def same_progress():
        return preserved == (read(h,h['offset'](15),192),
                             read(h,h['offset'](19),1000),bytes(h['flags']()))
    wait_rollover('wildlife-camera',4,same_progress)
    check('long calm camera never approaches or provokes animal',
          h['value'](8)==4 and h['value'](10)==0)
    h['aim_to'](1)
    h['wait_for']('natural photo after timer rollover',
                  lambda s:h['natural_window']('glide',s))
    h['shutter']('long-session-natural',3)
    h['return_trail'](site)
    check('post-rollover photo and restoration complete normally',
          h['best'](5)==3 and h['screen']()==2)
    # Open the same already cared-for stone, then let the real timer approach
    # its boundary. Restoration must display every pose across that boundary
    # and must not duplicate the earlier care reward.
    h['open_subject'](site)
    h['press']('b',150)
    check('restoration rollover starts from open cover on trail',
          h['screen']()==2 and bool(read(h,h['offset'](19),1000)[0]&1))
    clock = h['symbol']('sys_time')
    while h['word'](clock)<65392:
        h['tick'](128)
    while h['word'](clock)<65520:
        h['tick'](1)
    previous = h['word'](clock)
    points = h['value'](13)
    busy = h['symbol']('rf_restore_busy')
    pose = h['symbol']('rf_restore_frame')
    h['pb'].button_press('b')
    h['tick'](1)
    seen = set()
    crossed = False
    started = False
    trace = []
    for _ in range(200):
        h['tick'](1)
        if _==7:
            h['pb'].button_release('b')
        now = h['word'](clock)
        crossed |= now<previous
        previous = now
        trace.append({'clock':now,'busy':h['pb'].memory[busy],
                      'pose':h['pb'].memory[pose]})
        if h['pb'].memory[busy]:
            started = True
            # Internal phase4 commits SRAM after the four displayed poses;
            # it is deliberately still input-blocked and is not a fifth pose.
            if h['pb'].memory[pose]<=3:
                seen.add(h['pb'].memory[pose])
            check('timer-wrap restoration stays in input-blocked hike',h['screen']()==2)
        elif started:
            break
    (a.out/'restoration-wrap-trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    check('restoration crosses actual VBlank rollover and all four poses',
          started and crossed and seen=={0,1,2,3})
    check('timer-wrap restoration closes cover without duplicate reward',
          not(read(h,h['offset'](19),1000)[0]&1) and h['value'](13)==points)
    wraps.append({'context':'four-pose-restoration','after':previous,
                  'poses':sorted(seen),'frame':h['frames']})
    h['open_camp']()
    h['pb'].stop()
    ram = Path(str(cart)+'.ram').read_bytes()
    record = latest(ram)
    check('long session saves valid current payload',record is not None and record['size']==2544)
    open_rom(h,cart,ram)
    h['enter_hike']()
    check('cold restart retains actually earned post-rollover photo',h['best'](5)==3)
    h['pb'].stop()
    (a.out/'controller-earned-soak.ram').write_bytes(ram)

report = {'result':'pass','rom_sha256':a.expected_sha,'assertions':len(h['checks']),
          'frames':h['frames'],'checks':h['checks'],'inputs':h['inputs'],
          'timer_wraps':wraps,'memory_writes':False,
          'scope':'Actual native hike and camera waiting across 16-bit VBlank rollovers; continued input/photo/care/save/cold. Not human pacing, hours of adventure, sound audition or physical hardware.',
          'physical_hardware_verified':False}
(a.out/'playtest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['result','rom_sha256','assertions','frames','timer_wraps']},indent=2))
