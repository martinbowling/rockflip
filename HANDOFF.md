# Rock Flip — public development handoff

The latest development cartridge is v0.9.2, SHA256
`ad49fd56702f25b09db9f7d028a6d19db0e734db8982b753550d8e123156b464`.
It includes the illustrated California title, all 36 explorer poses and corrected
garter-snake markings. See README.md, docs/BUILD.md and docs/QA.md.

Implemented:150 regular native species plus one earned hidden discovery,
241 maps,538 observation sites,16 districts,48 investigation stages,32 optional
photo tasks,16 rangers,four chapters,a statewide exhibit,credits and postgame.
The exact cartridge passes all 31 native acceptance suites. This is a public
development release; human pacing/listening/recognition and physical Chromatic
tests remain separate.

The editable distributed project is native/project.gbsproj. Banked GBDK C lives
under native/plugins/rockflip/engine. Art is authored under art/src and generated
through make_sprites.py into indexed1x art/out. Native compilation is generated
by native/tools/production_generate.py. Read docs/BUILD.md before regeneration.

Save layout 6 retains a 2544-byte payload and dual committed records in battery
SRAM. Fresh games use revised regional investigations; authenticated older
layouts retain legacy progress and awards. Newer unsupported saves are read-only.
Never reinterpret species IDs or clear a journal without deliberate confirmation.

Title art uses 175 BG patterns in bank1; world entry reloads terrain and palettes.
Explorer 92 raw patterns occupy 736 bytes in each OBJ bank, with four objects and
two per scanline. Camera focus/behavior use elapsed VBlanks and bounded wrap-safe
timing. Cover restoration finishes its closed pose before care/save commits.

All wildlife placements are broad reviewed habitat/district permissions. Game
tile positions are fictional; the game is not a real-world wildlife locator.
