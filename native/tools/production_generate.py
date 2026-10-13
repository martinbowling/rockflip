"""Regenerate the native cartridge from reviewed canonical content and 1x art.

Run with the Chromatic toolchain Python. Historical first-wave/world scaffolds
are deliberately excluded: they would replace reviewed stable identities.
"""
from pathlib import Path
import argparse, json, runpy, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / 'native/plugins/rockflip/engine'
parser = argparse.ArgumentParser()
parser.add_argument('--skip-art', action='store_true',
                    help='Keep unchanged existing canonical 1x PNGs.')
args = parser.parse_args()
if not args.skip_art:
    sys.path.insert(0, str(ROOT / 'art/src'))
    runpy.run_path(str(ROOT / 'art/src/make_sprites.py'), run_name='__main__')
for name in ('generate', 'journal_compile', 'campaign_compile', 'ranger_compile',
             'guide_compile', 'conditions_compile', 'rock_restore_compile',
             'landmark_spawn_compile', 'gallery_compile', 'region_map_compile'):
    old_args = sys.argv
    sys.argv = [str(ROOT / f'native/tools/{name}.py')]
    if name in ('campaign_compile', 'region_map_compile'):
        sys.argv.append('--emit-native')
    try:
        runpy.run_path(sys.argv[0], run_name='__main__')
    finally:
        sys.argv = old_args
from marine_art_compile import emit_marine_content
emit_marine_content(ROOT / 'art/out', ENGINE)
from challenge_compile import compile as compile_challenges
compile_challenges(json.loads((ROOT / 'data/photo_challenges.json').read_text()), ENGINE)
(ROOT / 'output/qa/challenge-progress-source.json').write_text(json.dumps({'schema':6,'payload_bytes':2544,'persistent_bytes_added':0,'challenge_count':32,'criterion':'actual three-star authoredsite/map/phase shutter, independent bestalbum','legacy':'verified old layouts1–4 seed prior best>=3 awards once; old5 retains explicit awards','reserved_journal_masks':[224,192,224,252,252,254,248],'mode_byte':7,'mode_mask':32},indent=2)+'\n')
camp = runpy.run_path(str(ROOT / 'native/tools/camp_route_compile.py'))
camp['main']()
for name in ('rockflip_camp_route.c', 'rockflip_camp_route.h'):
    shutil.copy2(ROOT / 'output/world-camps' / name,
                 ENGINE / ('include' if name.endswith('.h') else 'src') / name)
print('Reviewed statewide content and indexed1x art regenerated for native build.')
