# Rock Flip contributor instructions

Read HANDOFF.md before editing. This is an original Game Boy Color game for
ModRetro Chromatic, with a complete statewide campaign.

- Original IP only. Wildlife is observed and photographed, never caught or fought.
- Never add real wildlife coordinates. Routes and tile positions are fictional.
- Canonical art entrypoint: art/src/make_sprites.py. Import only indexed 1x PNGs.
- Regenerate using native/tools/production_generate.py; avoid historical prototype generators.
- Build through the installed Chromatic/GB Studio toolchain. Match debug symbols to the exact ROM.
- Each gameplay milestone needs a bootable ROM and an actual controller playtest.
- Keep technical, human playtesting and physical-device acceptance distinct.
- Preserve saves and stable species IDs. Keep upstream notices and license scopes.
