# Build and test

The repository contains editable source and generated 1x assets, not installed
compilers or proprietary plugin binaries. The tested stack is GB Studio CLI 4.3.2,
GBDK 4.5.0, Python 3.13.12, PyBoy 2.7.0, Pillow 12.3.0 and NumPy 2.5.3.

## Recommended: ModRetro Chromatic plugin

Install the plugin in Codex and ask its toolchain doctor for the installed
compiler/Python/emulator readiness. Select the absolute checkout path to
`native/project.gbsproj`. Build using `rom_build` with debug artifacts enabled,
GBC-only mode and a 240000ms timeout. Place the returned cartridge at
`native/build/rom/RockFlip-Statewide.gbc` and its matching debug directory beside it.
The plugin also provides official browser export and recorded controller playtests.

## Source regeneration

Use Python 3.13 and install the repository requirements in your environment:

```sh
python -m pip install -r requirements.txt
python native/tools/production_generate.py
python -m unittest discover -s tests -p 'test_*.py'
```

Use only this production generator; older prototype scripts can replace reviewed
content. Art source is `art/src/make_sprites.py`. Keep indexed 1x PNGs and their
metadata. The full generator also creates native C tables, palettes and resource
metadata; it does not download wildlife pictures or coordinates.

## Optional installed-CLI build

If the official CLI and its compiler are already installed, this helper
regenerates and compiles the cartridge without bundling a toolchain:

```sh
python build.py --cli /path/to/gb-studio-cli.js
```

Or set `GB_STUDIO_CLI` to that file. On macOS the helper can discover the standard
Chromatic plugin toolchain path under your own home directory. Node.js must be on
PATH. This helper builds the ROM; use the plugin debug build for newly matched
debug symbols. It does not flash a cartridge or alter an open browser game.

## Native acceptance

After building the exact cartridge with matching symbols:

```sh
python native/tools/acceptance_run.py --expected-sha YOUR_ROM_SHA256
python tests/native_title_playtest.py --expected-sha YOUR_ROM_SHA256
python native/tools/hardware_report.py --out output/qa/hardware-current
```

All 31 suites run in dependency order. They use ordinary controller input and
genuine automated old/current regression fixtures. The world suite creates fresh
full/prehidden saves before later consumers. Historical fixtures are tracked at
the paths listed in `docs/test-fixtures.json`; they are not human browser saves.
Generated QA output is ignored. `--collect-only` joins receipts and does not run tests.

The downloadable ROM's SHA256 is in `dist/SHA256SUMS`. A changed toolchain or source
can produce a different hash; always bind test results to that actual new cartridge.

A clean packaged-source CLI build was also compiled successfully. It differs
from the shipped cartridge only in GB Studio's four-byte generated project save
signature and the resulting header checksum. That upstream signature hashes
loaded project metadata, so rebuilds are not promised to be byte-identical.
Rock Flip's journal uses its own versioned save format. Test each new ROM with
its own debug artifacts; the release QA counts describe the shipped hash above.
