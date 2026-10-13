# Validation

The shipped v0.9.2 native cartridge has SHA256
`ad49fd56702f25b09db9f7d028a6d19db0e734db8982b753550d8e123156b464`.
All 31 native suites pass 4,985,434 assertions on this exact ROM. A fresh
controller-driven adventure obtains all 151 species, completes all 16 districts,
four chapter conclusions, the exhibit and earned hidden discovery. No progress
flags are injected to claim campaign completion.

Coverage includes all 241 maps, all 151 saved portraits, guide palettes, fresh and
legacy investigations/exhibits, all 32 optional awards, forecast conditions,
safe-distance photography, natural behavior, camera timing through clock wrap,
cover restoration, interrupted/cold saves and actual older-reader protection.
Explorer checks compare all 36 rendered poses to their authored pixels. Technical
pixel matching is separate from biological recognition and human art review.

The title separately passes 33,294 actual pixel/credits/fresh/Continue checks.
A 2,532-frame recorded plugin run starts at the title, hikes, takes real photos,
replaces cover, commits care and shows filled guide entries.

See [the public result summary](qa-summary.json) for suite names/counts. Local
raw logs, browser states, personal saves and capability URLs are deliberately
excluded. The small fixture inventory contains automated regression saves and
older ROM readers only. Tests can be rerun using docs/BUILD.md.

## Remaining acceptance

This release has not passed physical Chromatic power-off/save/display/audio
testing, human full-campaign fun/pacing review, full human anatomy/recognition
review or complete listening/handheld readability review. Campaign hour targets
remain unmeasured. Intermediate blank/partial loading frames remain a polish
item. None of these is inferred from assertion totals or screenshots.

Run source checks in GitHub Actions; native ROM/emulator checks require the
separately installed toolchain and matching symbols. CI source checks are not a
claim of cartridge or physical-device acceptance.

The public source package also passes all 31 source unit tests and regenerates
its production assets without downloading external media. Its CLI-compiled ROM
matches every shipped game-code/content byte; only the upstream project signature
and header checksum differ. Controller-tested journal loading and saving passed
in both directions between those builds. This does not transfer the shipped
full-suite totals to an independently rebuilt cartridge.
