"""Execute generated native journal C flags on host; no emulator/hardware claim."""
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
source=ROOT/'native/plugins/rockflip/engine/src/rockflip_journal.c';header=ROOT/'native/plugins/rockflip/engine/include/rockflip_journal.h'
compiler=shutil.which('clang') or shutil.which('cc')
if not compiler:raise SystemExit('HostCcompiler unavailable')
with tempfile.TemporaryDirectory(prefix='rockflip-journal-host-') as directory:
 p=Path(directory);(p/'journal-under-test.c').write_text(source.read_text().replace('#pragma bank 255',''));shutil.copy(header,p/header.name)
 subprocess.run([compiler,'-std=c99','-O2','-Wall','-Wextra','-Werror','-I'+str(p),'-I'+str(HERE),str(HERE/'test.c'),'-o',str(p/'test')],check=True,capture_output=True,text=True)
 result=json.loads(subprocess.run([str(p/'test')],check=True,capture_output=True,text=True).stdout)
result.update({'scope':'generated_native_C_flag_logic_on_host','native_emulator_verified':False,'physical_hardware_verified':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'authored_json_sha256':hashlib.sha256((ROOT/'data/journal_prototype.json').read_bytes()).hexdigest(),'checks':['all_photo_predicate_fields_rejected_individually_whenwrong','evidence_beforeactivation_withoutbestalbumreplacement','same_site_photo_thenactualcare_binding','carebeforephoto_rejected','persistentcare_flags','rotatedchoices_wrong_retry_nonpunitive','allrequirements_andprecedingstages_required','unrestoredtrackedrocks_blocksurveyturnin','idempotentturnin_rewards','onlyfirstsurvey_andD04lead_nochapterflags','reservedbytes10to31_untouched','alltext21bytebufferbounds']})
output=ROOT/'output/qa/journal-host.json';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
