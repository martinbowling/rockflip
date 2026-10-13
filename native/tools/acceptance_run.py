"""Join exact-cartridge native proofs; use the Chromatic Python interpreter.

The Chromatic plugin builds the ROM first. This runner never rebuilds, updates
the browser, flashes a device, or supplies human approval. Reports and the first
failure are frozen per run. Existing prior-hash receipts cannot satisfy it.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / 'native/build/rom/RockFlip-Statewide.gbc'
FULL_SAVE = ROOT / 'output/qa/production/controller-earned-complete.ram'
# Order preserves genuine controller-generated fixture dependencies.
SUITES = [
    ('hud_mask', 'native_hud_mask_playtest.py', 'hud-mask-native/acceptance.json', 'sha'),
    ('explorer_actions', 'native_explorer_actions_playtest.py', 'explorer-actions-native/acceptance.json', 'sha'),
    ('atlas', 'native_atlas_playtest.py', 'atlas-native/playtest.json', 'sha'),
    ('opening', 'native_onboarding_test.py', 'onboarding-native/playtest.json', ''),
    ('new_game', 'native_new_game_test.py', 'new-game-native/playtest.json', 'sha'),
    ('route_revision', 'native_route_revision_playtest.py', 'route-revision-native/playtest.json', 'sha'),
    ('restoration', 'native_restore_playtest.py', 'restore-native/playtest.json', 'sha'),
    ('world', 'production_playtest.py', 'production/playtest.json', ''),
    ('route_ui', 'native_route_ui_playtest.py', 'route-ui-native/playtest.json', 'sha'),
    ('cover_hud', 'native_cover_hud_playtest.py', 'cover-hud-native/acceptance.json', 'sha_hidden'),
    ('challenges', 'native_challenge_playtest.py', 'challenge-native/playtest.json', ''),
    ('regional_challenges', 'native_regional_challenge_playtest.py', 'regional-challenge-native/playtest.json', 'sha'),
    ('gallery', 'native_gallery_playtest.py', 'gallery-native/playtest.json', 'full'),
    ('guide', 'native_guide_playtest.py', 'guide-native/acceptance.json', 'sha_full'),
    ('guide_palettes', 'native_guide_palette_audit.py', 'guide-palette-native/playtest.json', 'sha'),
    ('lens', 'native_lens_playtest.py', 'lens-native/playtest.json', ''),
    ('weather', 'native_weather_playtest.py', 'weather-native/playtest.json', ''),
    ('field_notice', 'native_field_notice_playtest.py', 'field-notice-native/probe.json', 'sha'),
    ('behavior', 'native_behavior_quality.py', 'behavior-quality-native/playtest.json', ''),
    ('migration', 'native_weather_migration.py', 'weather-migration-native/playtest.json', ''),
    ('standing', 'native_landmark_migration.py', 'landmark-migration-native/playtest.json', ''),
    ('sketch', 'native_region_playtest.py', 'region-native/playtest.json', ''),
    ('world_art', 'native_landmark_art_playtest.py', 'native-landmarks/acceptance.json', 'sha_full'),
    ('water', 'native_water_playtest.py', 'native-visual/water/acceptance.json', 'sha'),
    ('characters', 'native_visual_acceptance.py', 'native-visual/acceptance.json', 'sha'),
    ('camera', 'native_camera_allocation_playtest.py', 'native-camera-allocation/acceptance.json', 'sha'),
    ('camera_cadence', 'native_camera_cadence.py', 'camera-cadence-native/playtest.json', 'sha'),
    ('saved_art', 'native_saved_art_playtest.py', 'native-saved-art/acceptance.json', 'sha_full'),
    ('audio', 'native_audio_playtest.py', 'audio-native/playtest.json', ''),
    ('camp_animation', 'native_camp_animation.py', 'camp-animation-native/playtest.json', ''),
    ('timer_soak', 'native_soak_playtest.py', 'native-soak/playtest.json', 'sha'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--collect-only', action='store_true', help='Verify and freeze existing exact-hash reports; do not rerun tests.')
    parser.add_argument('--suite', action='append', choices=[s[0] for s in SUITES])
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()
    selected = [s for s in SUITES if not args.suite or s[0] in args.suite]
    if args.list:
        print(json.dumps(selected, indent=2))
        return
    if digest(ROM) != args.expected_sha:
        raise SystemExit('ROM differs from requested cartridge. No checks started.')
    debug = Path(str(ROM) + '.debug')
    if not (debug / 'symbols.noi').is_file():
        raise SystemExit('Build matching symbols through the Chromatic plugin first.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = ROOT / 'output/qa/acceptance-runs' / (args.expected_sha[:12] + '-' + stamp)
    out.mkdir(parents=True)
    shutil.copy2(ROM, out / ROM.name)
    shutil.copytree(debug, out / 'debug')
    manifest = {
        'status': 'running', 'rom_sha256': args.expected_sha,
        'python': sys.version, 'platform': platform.platform(),
        'dependencies': {n: importlib.metadata.version(n) for n in ('pyboy', 'pillow', 'numpy')},
        'collect_only': args.collect_only, 'suites': [],
        'source_hashes': {}, 'human_verified': False, 'physical_verified': False,
    }
    for folder in ('native/plugins/rockflip/engine', 'native/tools', 'native/assets',
                   'native/project.gbsproj', 'art/src', 'art/out', 'data', 'tests'):
        entry = ROOT / folder
        for path in ([entry] if entry.is_file() else sorted(entry.rglob('*'))):
            if path.is_file() and '__pycache__' not in path.parts and not (folder == 'art/out' and '_4x' in path.stem):
                manifest['source_hashes'][str(path.relative_to(ROOT))] = digest(path)
                frozen = out / 'source' / path.relative_to(ROOT)
                frozen.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, frozen)
                if digest(frozen) != manifest['source_hashes'][str(path.relative_to(ROOT))]:
                    raise ValueError('Source changed while freezing acceptance inputs: '+str(path))
    destination = out / 'manifest.json'

    def save():
        destination.write_text(json.dumps(manifest, indent=2) + '\n')

    save()
    try:
        for name, script, receipt, mode in selected:
            if digest(ROM) != args.expected_sha:
                raise ValueError('Cartridge changed during acceptance.')
            command = [sys.executable, str(ROOT / 'tests' / script)]
            if 'sha' in mode:
                command += ['--expected-sha', args.expected_sha]
            if 'full' in mode:
                command += ['--full-save', str(FULL_SAVE)]
            if 'hidden' in mode:
                command += ['--hidden-save', str(ROOT/'output/qa/production/controller-earned-prehidden150.ram')]
            row = {'name': name, 'command': command, 'status': 'running'}
            manifest['suites'].append(row)
            save()
            print('Checking ' + name, flush=True)
            if not args.collect_only:
                with (out / (name + '.log')).open('w') as log:
                    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=1800)
                row['exit_code'] = result.returncode
                if result.returncode:
                    raise ValueError(name + ' failed; its original log is preserved.')
            path = ROOT / 'output/qa' / receipt
            body = json.loads(path.read_text())
            shutil.copy2(path, out / (name + '-receipt.json'))
            if body.get('rom_sha256') != args.expected_sha:
                raise ValueError(name + ' receipt belongs to another cartridge.')
            if body.get('result', body.get('status')) != 'pass':
                raise ValueError(name + ' receipt does not pass.')
            row.update(status='pass', assertions=body.get('assertions'), receipt_sha256=digest(path))
            save()
        if digest(ROM) != args.expected_sha:
            raise ValueError('Cartridge changed before final binding.')
        for relative, expected in manifest['source_hashes'].items():
            if digest(ROOT / relative) != expected:
                raise ValueError('Canonical source changed during acceptance: ' + relative)
        manifest['status'] = 'pass'
        manifest['scope'] = 'Requested native suite receipts only; compilation, human pacing/audio and physical-device gates remain separate.'
    except Exception as error:
        manifest['status'] = 'failed'
        manifest['first_failure'] = str(error)
        if manifest['suites']:
            manifest['suites'][-1]['status'] = 'failed'
        save()
        raise
    save()
    print(json.dumps({'status': 'pass', 'rom_sha256': args.expected_sha, 'suites': len(selected), 'manifest': str(destination)}))


if __name__ == '__main__':
    main()
