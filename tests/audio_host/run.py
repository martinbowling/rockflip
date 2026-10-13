"""Host PSG register/control-flow checks; no synthesis/listening/hardware proof."""
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
source=ROOT/'native/plugins/rockflip/engine/src/rockflip_audio.c';header=ROOT/'native/plugins/rockflip/engine/include/rockflip_audio.h'
with tempfile.TemporaryDirectory(prefix='rockflip-audio-host-') as directory:
 p=Path(directory);(p/'audio-under-test.c').write_text(source.read_text().replace('#pragma bank 255',''));shutil.copy(header,p/header.name)
 compiler=shutil.which('clang') or shutil.which('cc')
 subprocess.run([compiler,'-std=c99','-O2','-Wall','-Wextra','-Werror','-I'+str(p),'-I'+str(HERE),str(HERE/'test.c'),'-o',str(p/'test')],check=True,capture_output=True,text=True)
 result=json.loads(subprocess.run([str(p/'test')],check=True,capture_output=True,text=True).stdout)
result.update({'scope':'host_register_shim_and_sequence_admission','native_emulator_verified':False,'audio_synthesized':False,'human_listened':False,'physical_hardware_verified':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':['all16motifs_distinct','note_indices_and_frequency_register_values_bounded','all16districts_3phases_1024updates_each','melody_harmony_noise_updates_preservechannel1effects','effects_preserveotherchannels','mastervolume3of7_panningallchannels','muteblocks_music_andFX_triggers','invaliddistrictphase_clamps','trianglewaveRAM_writtenwhilechannel3disabled']})
out=ROOT/'output/qa/audio-host.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
