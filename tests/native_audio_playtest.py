"""Capture actual synthesized native PSG samples, controller-only music/SFX.

PyBoy Sound API local docs: ndarray contains signed8-bit stereo for the last
emulated frame; collect everyframe and encode PCM16 WAV at actual sample_rate.
This proves emulator synthesis/timing/control, not listening or physical audio.
"""
from pathlib import Path
import ast,json,hashlib,tempfile,shutil,wave
import numpy as np
HERE=Path(__file__).resolve().parent;shared=HERE/'production_playtest.py'
tree=ast.parse(shared.read_text());prefix=[]
for node in tree.body:
 if isinstance(node,ast.With):break
 prefix.append(node)
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(shared),'exec'),globals())
OUT=ROOT/'output/qa/audio-native';OUT.mkdir(parents=True,exist_ok=True)
capturing=False;samples=[];psg=[];clips=[]
def tick(n):
 global frames
 if not capturing:pb.tick(n,True,True);frames+=n;return
 for _ in range(n):
  pb.tick(1,True,True);frames+=1;samples.append(pb.sound.ndarray.copy())
  psg.append({'frame':frames,'status':pb.memory[0xFF26],'nr12':pb.memory[0xFF12],
              'nr22':pb.memory[0xFF17],'nr32':pb.memory[0xFF1C],'nr42':pb.memory[0xFF21]})
def start_capture():
 global capturing,samples,psg
 samples=[];psg=[];capturing=True
def finish_capture(name,kind,extra=None):
 global capturing
 capturing=False;data=np.concatenate(samples,axis=0)
 check(name+' synthesized signed8bit stereo samples',data.ndim==2 and data.shape[1]==2 and data.dtype==np.int8 and len(data)>0)
 pcm=data.astype(np.int16)*256;path=OUT/(name+'.wav')
 with wave.open(str(path),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(pb.sound.sample_rate);w.writeframes(pcm.tobytes())
 f=data.astype(np.float64);centered=f-f.mean(axis=0)
 clip={'name':name,'kind':kind,'path':str(path),'sample_rate':pb.sound.sample_rate,'stereo_samples':len(data),
       'duration_seconds':len(data)/pb.sound.sample_rate,'peak_signed8':int(np.max(np.abs(f))),
       'ac_rms_signed8':float(np.sqrt(np.mean(centered**2))),'peak_to_peak':float(np.ptp(f)),
       'clip_fraction':float(np.mean(np.abs(f)>=127)), 'wav_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'channel1_active_frames':sum(bool(v['status']&1)for v in psg),
       'channel2_active_frames':sum(bool(v['status']&2)for v in psg),
       'channel3_active_frames':sum(bool(v['status']&4)for v in psg),
       'channel4_active_frames':sum(bool(v['status']&8)for v in psg),
       'psg_trace_sha256':hashlib.sha256(json.dumps(psg,sort_keys=True).encode()).hexdigest()}
 if extra:clip.update(extra)
 (OUT/(name+'-psg.json')).write_text(json.dumps(psg,indent=2)+'\n');clips.append(clip);return clip
def idle_clip(name,kind,n=960,extra=None):
 start_capture();tick(n);return finish_capture(name,kind,extra)
def audible(clip):
 check(clip['name']+' has synthesized waveform variation',clip['ac_rms_signed8']>0.1)
 check(clip['name']+' has no sustained sample clipping',clip['clip_fraction']<0.01)
def effect_clip(name,button):
 start_capture();press(button,150);clip=finish_capture(name,'button-earned_sfx')
 audible(clip);check(name+' actualchannel1 effect triggered',clip['channel1_active_frames']>0)
 return clip
with tempfile.TemporaryDirectory(prefix='rockflip-audio-native-')as work:
 path=Path(work)/ROM.name;shutil.copy2(ROM,path)
 pb=PyBoy(str(path),window='null',sound_emulated=True);pb.set_emulation_speed(0);tick(180)
 enter_hike();check('audio native fresh hike',screen()==2)
 check('fresh cartridge default music enabled',not(flags()[9]&128))
 for district in range(16):
  head=next(m['id']for m in world.values()if m['district_id']==f'D{district+1:02d}'and m.get('district_trailhead'))
  travel(head)
  for phase in range(3):
   rest_to(phase);check('native motif district andphase observed',world[value(1)]['district_id']==f'D{district+1:02d}'and value(4)==phase)
   clip=idle_clip(f'district-{district+1:02d}-phase-{phase}','regional_motif',960,{'district':district+1,'phase':phase,'map_id':value(1)})
   audible(clip);check('idle regional music reserveschannel1 for effects',clip['channel1_active_frames']==0)
   check('regional motif pulseandwave are synthesized',clip['channel2_active_frames']>0 and clip['channel3_active_frames']>0)
 check('all16districts/all3phases captured',len([c for c in clips if c['kind']=='regional_motif'])==48)
 # Three effects are activated by legal observation/photo/restoration buttons.
 site=next(s for s in sites if s['spot_id']==0);travel(site['room_id']);rest_to(1);face(site)
 effect_clip('effect-look','a');check('look effect accompanies real encounter',screen()==3)
 press('a',150);tick(120);effect_clip('effect-shutter','a');check('shutter effect accompanies saved photo',screen()==5 and best(site['species_id'])>0)
 press('b',150);effect_clip('effect-cover-care','b');check('care effect accompanies actual restoredcover',screen()==2 and value(13)>0)
 open_camp();press('start',150);check('actualstation music toggle sets savedmute flag',screen()==9 and(flags()[9]&128))
 press('b',150);tick(240);muted=idle_clip('music-muted','saved_mute',240)
 check('muted native audio has no changing waveform',muted['peak_to_peak']<=1)
 check('mute clears pulse/noise envelopes andwavevolumeDAC',
       not any(pb.memory[a]for a in [0xFF12,0xFF17,0xFF21])
       and not(pb.memory[0xFF1C]&0x60)and not(pb.memory[0xFF1A]&0x80))
 pb.stop();check('mutepreference actualSRAM emitted',Path(str(path)+'.ram').exists())
 pb=PyBoy(str(path),window='null',sound_emulated=True);pb.set_emulation_speed(0);tick(180)
 check('coldboot preserves savedmute flag',flags()[9]&128)
 cold=idle_clip('cold-title-muted','cold_saved_mute',180);check('coldtitle stays audiblyquiet in emulatorsynthesis',cold['peak_to_peak']<=1)
 enter_hike();open_camp();press('start',150);check('actualstation unmute clearssaved flag',not(flags()[9]&128))
 press('b',150);audible(idle_clip('music-unmuted-after-cold','cold_unmute',960));pb.stop()
report={'result':'pass','rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'assertions':len(checks),'checks':checks,'frames':frames,'inputs':inputs,'clips':clips,'regional_motif_clips':48,'source_audio_sha256':hashlib.sha256((ROOT/'native/plugins/rockflip/engine/src/rockflip_audio.c').read_bytes()).hexdigest(),'sample_source':'ActualPyBoyPSG signed8-bit stereo peremulatedframe; convertedlosslesslyPCM16by256scale, actualsample_rate retained','memory_writes':False,'audio_synthesized':True,'human_listened':False,'physical_hardware_verified':False,'scope':'Native16district/3phase synthesizedmusic, actualbuttonlook/shutter/care effects, stationmute andcoldSRAM preference. Waveformtechnicaladmission isnot composition/mastering/listening/physicalapproval.'}
(OUT/'playtest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['result','assertions','regional_motif_clips','frames','rom_sha256','human_listened']},indent=2))
