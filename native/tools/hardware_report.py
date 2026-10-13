"""Read-only per-build hardware/content/evidence inventory. No release gate.
UsesexactROM/NOI andexplicitreceipts; priorhash passes are nevercurrentnativepass.
RunwithChromatic Python. Onlyoutputsunderrequested reportdirectory.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,re,hashlib,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,default=ROOT/'native/build/rom/RockFlip-Statewide.gbc');p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
ROM=args.rom;binary=ROM.read_bytes();sha=hashlib.sha256(binary).hexdigest();noi=Path(str(ROM)+'.debug/symbols.noi');symbols={n:int(v,16) for n,v in re.findall(r'^DEF (\S+) 0x([\da-fA-F]+)$',noi.read_text(),re.M)};checks=[]
def check(name,ok):
 if not ok:raise ValueError(name)
 checks.append(name)
def load(path):
 try:
  before=path.read_bytes();x=json.loads(before);after=path.read_bytes()
  if before!=after:return None
  return x
 except (OSError,ValueError):return None

def read(rel):
 x=load(ROOT/rel)
 if x is None:raise ValueError('Missingorunstablecanonicalinput:'+rel)
 return x

# Linkerarea extents, notheuristiccounts ofnon-FF-ROMbytes.
areas=[];bybank=defaultdict(list)
for name,length in symbols.items():
 if not name.startswith('l__') or not length:continue
 section=name[3:];start=symbols.get('s__'+section)
 if start is None:continue
 bank=start>>16;address=start&65535
 if address>=0x8000:continue
 window=0 if bank==0 else 0x4000
 if bank>0 and address<0x4000:continue
 check('linkerROMsectionfits16KiB:'+section,address+length<=window+16384)
 areas.append({'section':section,'bank':bank,'cpu_start':address,'bytes':length});bybank[bank].append((address-window,address-window+length))
banks=[]
for bank,intervals in sorted(bybank.items()):
 merged=[]
 for lo,hi in sorted(intervals):
  if merged and lo<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],hi)
  else:merged.append([lo,hi])
 used=sum(hi-lo for lo,hi in merged);high=max(hi for lo,hi in merged);banks.append({'bank':bank,'linked_bytes':used,'linked_high_water_offset':high,'tail_free_bytes':16384-high,'occupancy_percent':round(used*100/16384,2)})
rom_size=32768<<binary[0x148];ram_sizes={0:0,1:2048,2:8192,3:32768,4:131072,5:65536};ram_size=ram_sizes.get(binary[0x149]);check('ROMdeclaredsizematchesfile',len(binary)==rom_size);check('GBConlyheader',binary[0x143]==0xC0);check('MBC5batteryRAMheader',binary[0x147] in (0x1B,0x1E));check('fourSRAMbanks',ram_size==32768);checksum=0
for value in binary[0x134:0x14D]:checksum=(checksum-value-1)&255
check('headerchecksumvalid',checksum==binary[0x14D]);global_sum=(sum(binary)-binary[0x14E]-binary[0x14F])&65535;check('globalchecksumvalid',global_sum==int.from_bytes(binary[0x14E:0x150],'big'))
occupied=max(symbols.get('s__'+n,0)+symbols.get('l__'+n,0) for n in ('DATA','BSS','INITIALIZED','HEAP','HEAP_END'));stack=symbols['.STACK'];gap=stack-occupied;check('WRAMstaticgap768',gap>=768)

paths={
 'full_world':'production/playtest.json','guide':'guide-native/acceptance.json','saved_art':'native-saved-art/acceptance.json',
 'world_art':'native-landmarks/acceptance.json','visual':'native-visual/acceptance.json',
 'water':'native-visual/water/acceptance.json','camera_bands':'native-camera-allocation/acceptance.json',
 'region_map':'region-native/playtest.json','standing_migration':'landmark-migration-native/playtest.json',
 'restore':'restore-native/playtest.json','lens':'lens-native/playtest.json',
 'weather':'weather-native/playtest.json','save':'save-native/playtest.json',
 'weather_migration':'weather-migration-native/playtest.json','snapshot_migration':'native-snapshot-migration/playtest.json',
 'taxonomy_migration':'native-taxonomy60-migration/playtest.json','behavior':'behavior-quality-native/playtest.json',
 'challenges':'challenge-native/playtest.json','audio':'audio-native/playtest.json',
 'onboarding':'onboarding-native/playtest.json','camp_animation':'camp-animation-native/playtest.json',
 'hud_mask':'hud-mask-native/acceptance.json','atlas':'atlas-native/playtest.json',
 'new_game':'new-game-native/playtest.json','route_revision':'route-revision-native/playtest.json',
 'route_ui':'route-ui-native/playtest.json','cover_hud':'cover-hud-native/acceptance.json',
 'regional_challenges':'regional-challenge-native/playtest.json','gallery':'gallery-native/playtest.json',
 'guide_palettes':'guide-palette-native/playtest.json','field_notice':'field-notice-native/probe.json',
 'timer_soak':'native-soak/playtest.json'}
evidence={};raw={}
for kind,rel in paths.items():
 path=ROOT/'output/qa'/rel;x=load(path)
 if x is None:evidence[kind]={'state':'missing_or_being_written','path':str(path.relative_to(ROOT))};continue
 rsha=x.get('rom_sha256');status=x.get('status',x.get('result'));passed=status=='pass';current=rsha==sha
 evidence[kind]={'state':'current_hash_pass' if passed and current else 'prior_hash_pass' if passed and rsha else 'failed_or_unbound','native_status':status,'rom_sha256':rsha,'path':str(path.relative_to(ROOT)),'receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'assertions':x.get('assertions'),'frames':x.get('frames')};raw[kind]=x
prod=raw.get('full_world',{});current_prod=evidence.get('full_world',{}).get('state')=='current_hash_pass';runtime_stack=prod.get('stack_watermark') if current_prod else None
if runtime_stack:check('currentnativewatermark512',runtime_stack['remaining_data_gap']>=512)
peak=prod.get('hardware_peak') if current_prod else None
if peak:check('observedOBJ40scanline10',peak['visible_obj']<=40 and peak['obj_per_scanline']<=10)

# Relateoldproofs byactualbytecomparison without relabelingthemcurrentruns.
prior_path=ROOT/'output/qa/2581-art-landmark-water-visual-proof/native/build/rom/RockFlip-Statewide.gbc';prior_diff=None
if prior_path.exists():
 old=prior_path.read_bytes();changed=[{'offset':i,'old':a,'new':b} for i,(a,b) in enumerate(zip(old,binary)) if a!=b];prior_diff={'prior_sha256':hashlib.sha256(old).hexdigest(),'current_sha256':sha,'same_length':len(old)==len(binary),'changed_bytes':changed,'changed_byte_count':len(changed),'meaning':'Byteequivalence isprovenonlyoutside these offsets. PriorQA remainsboundto priorhash.'}

world=read('data/world.json')['maps'];sites=read('data/foundation_encounters.json')['records'];roster=read('data/production_roster.json')['records'];ecology=read('data/species_ecology.json')['records'];art=read('art/out/species-art-manifest.json');mapart=read('art/out/world-art-manifest.json');by_sid={r['species_id']:r for r in roster};by_map={m['id']:m for m in world};eco={r['species_id']:r for r in ecology};art_by={r['species_id']:r for r in art.values()};site_by=defaultdict(list)
check('151distinctscientificidentities',len(by_sid)==151 and len({r['canonical_scientific_name'] for r in roster})==151);check('241maps',len(by_map)==241);check('538sites',len(sites)==538 and len({s['spot_id'] for s in sites})==538);check('16districts',len({m['district_id'] for m in world})==16)
for s in sites:
 sid=s['species_id'];m=by_map[s['room_id']];perm=[p for p in by_sid[sid]['region_permissions'] if p['region_id']==s['region_id'] and s['habitat_id'] in p['habitat_ids'] and (not p.get('subarea_ids') or m['subarea_id'] in p['subarea_ids'])];check('reviewedplacementpermission',bool(perm) and m['district_id']==s['region_id']);check('maphabitatpermission',s['habitat_id'] in m['habitat_ids']);site_by[sid].append(s)
source_binding={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('data/world.json','data/foundation_encounters.json','data/production_roster.json','data/species_ecology.json','art/out/species-art-manifest.json','art/out/world-art-manifest.json')}
encounter_counts=Counter();photo_counts=Counter()
if current_prod:
 for label in prod.get('checks',[]):
  a=re.fullmatch(r'species (\d+) valid region/habitat encounter',label);b=re.fullmatch(r'species (\d+) photograph updates guide record',label)
  if a:encounter_counts[int(a[1])]+=1
  if b:photo_counts[int(b[1])]+=1
 # Sourceandcurrentnativecontrollertrace covereveryfixedsite throughsamecount.
 check('all538currentnativeencounters',sum(encounter_counts.values())==len(sites))
regions=[]
for district in sorted({m['district_id'] for m in world}):
 maps=[m for m in world if m['district_id']==district];ss=[s for s in sites if s['region_id']==district];sub=[]
 for subarea in sorted({m['subarea_id'] for m in maps}):
  mids={m['id'] for m in maps if m['subarea_id']==subarea};subsites=[s for s in ss if s['room_id'] in mids];sub.append({'subarea':subarea,'maps':len(mids),'sites':len(subsites),'species':len({s['species_id'] for s in subsites}),'native_maps':'all_authored_maps_reached_current_hash' if current_prod and 'all authored maps reached' in prod.get('checks',[]) else 'not_currently_bound'})
 regions.append({'district':district,'maps':len(maps),'sites':len(ss),'species':len({s['species_id'] for s in ss}),'primary_landmarks':sum(bool(m.get('landmark_primary')) for m in maps),'secondary_landmarks':sum(bool(m.get('landmark_secondary')) for m in maps),'subareas':sub})

species_report=[]
for sid in range(151):
 r=by_sid[sid];a=art_by[sid];check('rosterartidentitymatch',a['canonical_scientific_name']==r['canonical_scientific_name']==eco[sid]['canonical_scientific_name']);check('specieshassites',bool(site_by[sid]));frames={}
 for key,size in [('frames',48),('frames32',32)]:
  images=[Image.open(ROOT/'art/out'/name) for name in a[key]];check('indexednativeframepair',len(images)==2 and all(im.mode=='P' and im.size==(size,size) and set(im.get_flattened_data())<={0,1,2,3} for im in images));check('nativeposepairsnotidentical',images[0].tobytes()!=images[1].tobytes());frames[str(size)]=[hashlib.sha256((ROOT/'art/out'/name).read_bytes()).hexdigest() for name in a[key]]
 check('RGB555speciespalette',len(a['palette'])==4 and all(0<=v<=248 and v%8==0 for c in a['palette'] for v in c));guide=evidence.get('guide',{});portrait_variants=prod.get('native_portrait_frame_variants',{}).get(str(sid)) if current_prod else None
 species_report.append({'id':sid,'common_name':r['common_name'],'scientific_name':r['canonical_scientific_name'],'group':r['group'],'source_identity_status':r['status'],'source_release_status':r['release_review_status'],'source_placements':len(site_by[sid]),'districts':sorted({s['region_id'] for s in site_by[sid]}),'subareas':sorted({by_map[s['room_id']]['subarea_id'] for s in site_by[sid]}),'native_encounters_current_hash':encounter_counts[sid] if current_prod else None,'native_photo_events_current_hash':photo_counts[sid] if current_prod else None,'native_portrait_crop_variants_current_hash':portrait_variants,'native_photo_status':'current_hash_controller_observed_and_cold_records_restored' if current_prod and photo_counts[sid] and prod.get('cold_sram_restored') else 'not_currently_bound','guide_status':guide.get('state'),'guide_receipt_hash':guide.get('rom_sha256'),'portrait48_and32_source':'indexed_original_twoframes_validated','portrait_source_file_hashes':frames,'native_saved_art_status':evidence.get('saved_art',{}).get('state'),'native_saved_art_receipt_hash':evidence.get('saved_art',{}).get('rom_sha256'),'anatomical_diagnostic_recognition':'not_inferred_from_pixel_or_hash_checks'})

from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('camera_budget',ROOT/'native/tools/map_art_compile.py');cam=module_from_spec(spec);spec.loader.exec_module(cam);mapcounts=[]
for m in world:
 im=Image.open(ROOT/'art/out'/mapart[str(m['id'])]['indices']);patterns=lambda q:len({q.crop((x,y,x+8,y+8)).tobytes() for y in range(0,q.height,8) for x in range(0,q.width,8)});wc=patterns(im);cc=patterns(im.crop((16,24,144,88)));check('world120camera92',wc<=120 and cc<=len(cam.CAMERA_SLOTS));check('4RGB555worldpalettefamilies',len(mapart[str(m['id'])]['palette_slots'])==4 and all(0<=v<=248 and v%8==0 for p in mapart[str(m['id'])]['palette_slots'] for c in p for v in c));mapcounts.append({'map':m['id'],'world_patterns':wc,'camera_patterns':cc})
water_path=ROOT/'native/plugins/rockflip/engine/water-animation-receipt.json';water=load(water_path)
oam=load(Path(__file__).resolve().parent/'oam-probe.json')
# Exact imported OBJ storage from ROM tileset headers, not source numTiles hints.
# GBVM tileset_t begins with16-bit n_tiles then inline16-byte8x8 patterns.
obj_import={'state':'not_bound','reason':'Stable explorer tileset symbols or source descriptor unavailable'}
obj_names=['_sprite_camera_ranger_deluxe_tileset','_sprite_camera_ranger_deluxe_bank2_tileset']
obj_resource=ROOT/'native/assets/sprites/ranger_deluxe.png.gbsres'
if all(n in symbols for n in obj_names) and obj_resource.is_file():
 descriptor=load(obj_resource);entries=[]
 for vrambank,name in enumerate(obj_names):
  pointer=symbols[name];bank=pointer>>16;address=pointer&65535
  offset=bank*16384+(address&16383) if bank else address
  count=int.from_bytes(binary[offset:offset+2],'little')
  check('importedOBJtilesetheaderfitsbank',count>0 and address+2+count*16<=32768)
  data=binary[offset+2:offset+2+count*16];check('importedOBJtilebytespresent',len(data)==count*16)
  entries.append({'symbol':name,'ROM_bank':bank,'CPU_address':address,'VRAM_bank':vrambank,'raw8x8_tiles':count,'tile_bytes_sha256':hashlib.sha256(data).hexdigest()})
 hud=evidence.get('hud_mask',{});hud_current=hud.get('state')=='current_hash_pass'
 obj_import={'state':'ROM_tileset_storage_and_source_descriptor_bound','rom_sha256':sha,'descriptor_path':str(obj_resource.relative_to(ROOT)),'descriptor_sha256':hashlib.sha256(obj_resource.read_bytes()).hexdigest(),'source_canvas_width':descriptor['canvasWidth'],'source_canvas_height':descriptor['canvasHeight'],'tilesets':entries,'total_raw8x8_tiles':sum(e['raw8x8_tiles']for e in entries),'VRAM_split_counts':[e['raw8x8_tiles']for e in entries],'current_native_RGBA_pose_count':len(raw['hud_mask'].get('poses',[]))if hud_current else None,'current_native_RGBA_checker':hud if hud_current else None,'limitation':'Storage counts/sourcecanvas do not alone prove rendered anatomy or liveOBJ allocation; actualcurrentRGBA/OAM receipts remain distinct.'}
# Route-variant code is a compiled layout6 marker; currentRFstore source and
# exact native save/migration reports remain separately bound in evidence.
current_layout=6 if '_rf_campaign_variant_target' in symbols else 5 if '_rf_challenge_record' in symbols else 4
report={'status':'validated_hardware_and_evidence_inventory_not_release_approval','generated_from_readonly_inputs':True,'rom':{'path':str(ROM),'sha256':sha,'bytes':len(binary),'banks':len(binary)//16384,'header_valid':True,'color_mode':'GBC_only','mapper':'MBC5_RAM_BATTERY','declared_SRAM_bytes':ram_size},'NOI':{'path':str(noi),'sha256':hashlib.sha256(noi.read_bytes()).hexdigest(),'binding':'runtime_receipts_readmatchingNOIsymbols; nofabricatedembeddedROMhash'},'source_binding':source_binding,'bank_occupancy':banks,'fixed_bank':next(b for b in banks if b['bank']==0),'WRAM':{'static_data_start':symbols['s__DATA'],'DATA_bytes':symbols['l__DATA'],'INITIALIZED_bytes':symbols['l__INITIALIZED'],'occupied_static_end':occupied,'stack_top':stack,'static_gap':gap,'actual_stack_watermark_current_hash':runtime_stack,'actual_OAM_peak_current_hash':peak,'OAM_short_probe':oam if oam and oam['rom_sha256']==sha else None},'SRAM':{'physical_banks':4,'engine_owned_banks':[0,1,2],'RF_store_bank':3,'record_offsets_within_bank':[0,4096],'record_bytes':4096,'header_bytes':16,'payload_current_bytes':2544,'payload_capacity':4080,'current_layout':current_layout,'layouts':{'1':2256,'2':2448,'3':2544,'4':2544,'5':2544,'6':2544},'layout6_route_variant':{'byte':8,'mask':2,'fresh':'bitset selects fresh campaign target/text/gallery tables','authenticated_layouts1_to5':'bitcleared; legacy0 predicates/texts remain; allfiled/partial/photos preserved','current6':'bothlegacy0/fresh2 valid; no payloadgrowth'},'layout5_challenge_progress':'32 previously unused journal highbits plus mode7bit5; no payloadgrowth; oldderived awards seed strictlyon verified loaded_layout<5; layout5/6 awards never reseeded','commit_byte_written_last':'R','checksum':'CRC16_CCITT_FALSE_header_metadata_and_payload','older_RF01':'checksum_valid64byte_migration_only','future_or_downgrade':'writes_locked','domain_integrity':'runtimevalidatesopaqueRFpayload'},'VRAM_and_palettes':{'BG_bank0':{'font':[0,95],'current_camera_safe_runs':[[96,127],[164,223]],'camp':[224,229],'restoration_scratch':[230,233]},'BG_bank1':{'world_signed_context':[136,255],'wildlife_or_station_portrait_context':[128,163],'guide_icons_context':[64,87],'contexts_are_mutually_exclusive':True},'portrait_vs_camera_bank_correction':'Portraits areBANK1; camerasBANK0. The splitcameraallocation isconservative, not a provenoldportraitcorruptionfix.','world_palette_slots':[0,1,2,3],'water_palette':3,'wildlife_or_ranger_portrait_palette':5,'camp_palette':6,'UI_palette':7,'water_pattern_bank':1,'animated_patterns_per_map':4,'maximum_source_world_patterns':max(r['world_patterns'] for r in mapcounts),'maximum_source_camera_patterns':max(r['camera_patterns'] for r in mapcounts),'object_hardware_limits':{'total':40,'per_scanline':10},'imported_explorer_OBJ':obj_import,'OBJ_allocation':'GBVM managed; exactobservedshortwalk tilebankset inOAMprobe, no assumedglobalOBJreservation'},'world_source_and_native_coverage':{'maps':241,'sites':538,'species':151,'districts':16,'regions':regions,'current_native_encounter_checks':sum(encounter_counts.values()) if current_prod else None,'current_native_allmaps_reached':current_prod and 'all authored maps reached' in prod.get('checks',[]),'site_permissions_checked':538,'native_context':'Controllerreceiptcounts areexplicit; no realworldcoordinatesareincluded.'},'per_species':species_report,'QA_evidence':evidence,'prior_ROM_binary_difference':prior_diff,'water_compiler_receipt':{'path':str(water_path.relative_to(ROOT)),'receipt':{k:v for k,v in (water or {}).items() if k!='map_proofs'}},'assertions':len(checks),'human_and_physical':'No approval is inferred; reportinventoriestechnicalevidence only.'}
check('ROMunchangedduringreport',hashlib.sha256(ROM.read_bytes()).hexdigest()==sha);report['assertions']=len(checks);dest=args.out/(sha[:12]+'-hardware-evidence.json');dest.write_text(json.dumps(report,indent=2)+'\n')
text=f'Hardware/evidence inventory for `{sha}`.\n\n{len(binary)//1024}KiB ROM; {len(bybank)} occupied linked banks. Fixed-bank tail {report["fixed_bank"]["tail_free_bytes"]}bytes. WRAM staticgap {gap}bytes; current native observed margin {runtime_stack["remaining_data_gap"] if runtime_stack else "unbound"}bytes.\n\n151 sourceidentities /241 maps /538 permission-checked sites /16 districts. Current native trace encounterchecks: {sum(encounter_counts.values()) if current_prod else "unbound"}.\n\n| Evidence | Binding | SHA |\n|---|---|---|\n'+''.join(f'| {k} | {v["state"]} | {str(v.get("rom_sha256",""))[:12]} |\n' for k,v in evidence.items())+'\nPortraits use VRAMbank1; cameras use bank0. The adopted split is safe but was not a demonstrated portrait collision fix. Prior-hash evidence is preserved and not called current native acceptance.\n';(args.out/(sha[:12]+'-hardware-evidence.md')).write_text(text);print(json.dumps({'report':str(dest),'assertions':len(checks),'current_hash':sha,'static_gap':gap,'native_stack_margin':runtime_stack['remaining_data_gap'] if runtime_stack else None},indent=2))
