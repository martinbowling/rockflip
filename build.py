"""Regenerate and compile Rock Flip with an already installed official GB Studio CLI."""
from pathlib import Path
import argparse,hashlib,os,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cli',type=Path,help='gb-studio-cli.js, or set GB_STUDIO_CLI')
p.add_argument('--skip-regenerate',action='store_true')
p.add_argument('--expected-sha',help='Optional exact-ROM reproducibility check')
a=p.parse_args()
if not a.skip_regenerate:
 (ROOT/'output/qa').mkdir(parents=True,exist_ok=True)
 subprocess.run([sys.executable,str(ROOT/'native/tools/production_generate.py')],cwd=ROOT,check=True)
cli=a.cli or (Path(os.environ['GB_STUDIO_CLI'])if os.environ.get('GB_STUDIO_CLI')else Path.home()/'Library/Application Support/modretro-chromatic/toolchain/.local/vendor/gb-studio/out/cli/gb-studio-cli.js')
if not cli.is_file():p.error('Install the Chromatic toolchain or supply --cli /path/to/gb-studio-cli.js. No compiler is bundled.')
node=shutil.which('node')
if not node:p.error('Node.js must be installed and available on PATH.')
rom=ROOT/'native/build/rom/RockFlip-Statewide.gbc';rom.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([node,str(cli),'make:rom',str(ROOT/'native/project.gbsproj'),str(rom),'--verbose'],cwd=ROOT/'native',check=True)
# The CLI does not emit symbols; never leave a previous build's symbols beside it.
debug=rom.with_name(rom.name+'.debug')
if debug.exists():shutil.rmtree(debug)
sha=hashlib.sha256(rom.read_bytes()).hexdigest()
if a.expected_sha and sha!=a.expected_sha:raise SystemExit('Built ROM differs from requested SHA256: '+sha)
print('Built:',rom.relative_to(ROOT),'SHA256:',sha)
print('Use the Chromatic plugin debug build when matching symbols are needed for native tests.')
