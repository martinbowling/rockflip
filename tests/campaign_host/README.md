# Regional campaign host checks

Run `python3 tests/campaign_host/run.py`. The runner compiles the current generated native module to a temporary shared library and exercises its public APIs using ctypes. Native C is read directly and never rewritten. `gbdk/platform.h` erases the banking annotation and supplies exact-width scalar types. The host compiler ignores the bank pragma; this does not test ROM banking, UI input, saves, or cartridge behavior. Evidence with current input hashes is written to `output/qa/campaign-host.json`.

The 2,515 assertions cover all 64 exact photo predicates, rejected wrong species/site/phase/quality/distance/focus, care ordering, 48 stage transitions and adjacent region bit preservation, text limits, chapter completion, four exhibit captions, the opening-journal dependency, and the 150-regular-photo hidden gate. The executable semantic test is authored in `run.py`; no separate C assertions are needed.
