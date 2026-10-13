# Third-party notices

This project includes original Rock Flip game material and separately licensed scaffold/runtime components. Publication of the repository does not replace their notices or grant a new blanket license to every file.

## GB Studio scaffold

The native project was scaffolded with GB Studio. Its existing Chris Maltby MIT notice is retained in `native/LICENSE` and `licenses/GB-STUDIO-MIT.txt`.

## GBVM runtime and adapted headers

GB Studio cartridges include the GBVM runtime, and this source tree includes adapted GBVM actor/VM headers. Copyright(c)2020 Toxa; MIT. The full notice is retained in `licenses/GBVM-MIT.txt`. Retain that notice when redistributing these components or the cartridge.

## ModRetro Chromatic plugin starter assets

These files match the plugin's original starter artwork: `native/assets/backgrounds/workshop.png`, `native/assets/sprites/workshop_player.png`, `native/assets/fonts/bench-mono.png`, `native/assets/ui/frame.png` and `native/assets/ui/cursor.png`. Their existing MIT license is copyright(c)2026 Eric Provencher, retained in `licenses/MODRETRO-SAMPLE-MIT.txt`. They are scaffold assets, separate from Rock Flip's authored wildlife/explorer/scenery art. The upstream sample provenance identifies editable cell/recipe sources and licensed original sample artwork. Its original-art documentation notes that eleven Bench Mono glyph definitions reuse original Signal Lost title glyphs; the remainder and the room/player/UI were authored for the plugin release. This attribution is preserved here.

## GBDK and SDCC runtime libraries

The cartridge links GBDK/SDCC runtime library code under GPL version2 with the express linking exception. The full installed notice is retained in `licenses/GBDK-GPL-2.0-linking-exception.txt`. That exception states that linking the library does not by itself make the executable subject to GPL. This project does not redistribute the compiler/toolchain executables. Their own licenses remain separate; this notice does not relicense them.

## Original game art, music and research references

Rock Flip's native wildlife portraits, explorer poses, rangers, scenery, title/font grids and sound motifs are generated from the editable source under `art/src/` and the authored audio module. Biology source URLs document factual identity, range, habitat and distinguishing-trait review. They are not licenses to republish external photographs, articles or maps; those reference media are not included in this game package.

The existing Rock Flip engine-plugin metadata declares MIT. Preserve that existing declaration. These notices do not extend it to every original project asset, dataset or document. No additional project-wide license is selected by publishing this repository. Consult any explicit per-file license and the project owners for uses beyond the applicable existing license.

## External tools not bundled

GB Studio, GBDK, PyBoy, Pillow, Node.js and the ModRetro Chromatic plugin are separately installed development tools. Their executables, installed dependencies and proprietary Chromatic CLI/driver bundles are not included here. The plugin supplier's permission to distribute proprietary CLI binaries within its official plugin is not transferred to this public game repository.
