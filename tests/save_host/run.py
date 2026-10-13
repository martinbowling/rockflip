"""Reproducible host execution of production save C; does not emulate a GB.

Only SRAM address mapping and individual store instrumentation are substituted.
GBDK declarations/register macros use a narrow host shim. The real production
CRC, record selection, migration and save/load control flow remain unchanged.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path);parser.add_argument('--header',type=Path);parser.add_argument('--report',type=Path);args=parser.parse_args()
src=args.source or ROOT/'native/plugins/rockflip/engine/src/rockflip_save.c'
header=args.header or ROOT/'native/plugins/rockflip/engine/include/rockflip_save.h'
compiler=shutil.which('clang') or shutil.which('cc')
if not compiler:raise SystemExit('Host C compiler clang/cc unavailable')
s=src.read_text().replace('#pragma bank 255','')
old='return (volatile UBYTE *)(slot ? 0xB000u : 0xA000u);'
if s.count(old)!=1:raise SystemExit('SRAM pointer mapping changed: update harness adapter')
s=s.replace(old,'return host_sram + (slot ? 4096 : 0);')
s=s.replace('p[10]=p[11]=0;','p[10]=0;p[11]=0;')
# Instrument assignment statements only. Preserve comparisons and all reads.
s,count=re.subn(r'p\[([^\]]+)\]\s*=(?!=)\s*([^;]+);',r'host_write(p,\1,\2);',s)
if count!=17:raise SystemExit(f'Save store statements changed: expected17, found{count}; update interruption accounting')
with tempfile.TemporaryDirectory(prefix='rockflip-save-host-') as tmp:
 tmp=Path(tmp);(tmp/'save-under-test.c').write_text(s);shutil.copy(header,tmp/header.name)
 command=[compiler,'-std=c99','-O2','-Wall','-Wextra','-Werror','-I'+str(HERE),'-I'+str(tmp),str(HERE/'test.c'),'-o',str(tmp/'test')]
 subprocess.run(command,check=True,capture_output=True,text=True)
 try:
  output=subprocess.run([str(tmp/'test')],check=True,capture_output=True,text=True).stdout
 except subprocess.CalledProcessError as error:
  raise SystemExit(error.stderr or error.stdout or str(error))
 result=json.loads(output)
result.update({'scope':'host_C_logic_with_SRAM_store_fault_injection','native_emulator_verified':False,'physical_hardware_verified':False,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'source_adaptations':['replace_fixed_SRAM_address_with_host_array','instrument_individual_SRAM_assignments','GBDK_type_and_bank_register_shim'],'checks':['CRC16-CCITT-FALSE standard vector29B1','4080-byte maximum payload','dual-record newest selection','corrupt newest fallback','RF01 migration preservation','RF03 write locking','65535-to-0 sequence wrap','payload length mismatch locking','maximum length guard','bankzero_disabled_SRAM_on_normal_exits','powerloss_before_every_store_in64byte_record_overwrite','powerloss_before_every_store_in_first64byte_RF01_migration','schema1_2256_to_schema2_2448_streaming_zero_append','powerloss_before_every_store_in2448byte_RF02_migration_and_schema2_overwrite','schema2_exact_size_and_future_layout_locks','corrupt_schema2_fallback_to_verified_schema1','CRC_covers_snapshot_metadata_and_payload','schema2_oldsize_caller_refuses_downgrade','all7689_byte_store_cut_points_same_size3_4_5_to6','layout6_preserves_old4096_record','unsupported_future7_locks_writes']})
out=args.report or ROOT/'output/qa/save-host.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
