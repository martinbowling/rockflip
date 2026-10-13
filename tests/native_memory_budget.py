"""Reject compiled WRAM collisions; static gap is not a runtime stack watermark."""
from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parents[1];rom=root/'native/build/rom/RockFlip-Statewide.gbc';noi=Path(str(rom)+'.debug/symbols.noi').read_text()
def address(name):return int(re.search(r'DEF '+re.escape(name)+r' 0x([0-9A-Fa-f]+)',noi)[1],16)
start=address('s__DATA');length=address('l__DATA');occupied_end=max(address('s__'+section)+address('l__'+section) for section in ('DATA','BSS','INITIALIZED','HEAP','HEAP_END'));stack=address('.STACK');gap=stack-occupied_end
assert start>=0xC000 and occupied_end<=stack and gap>=768, f'Unsafe compiled WRAM/stack gap: {gap}'
report={'result':'pass','rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'data_start':start,'data_bytes':length,'data_end':start+length,'occupied_wram_end':occupied_end,'initialized_bytes':address('l__INITIALIZED'),'stack_start':stack,'static_gap_bytes':gap,'minimum_static_gap':768,'runtime_stack_watermark':'pending','physical_hardware':'not tested'}
(root/'output/qa/native-memory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
