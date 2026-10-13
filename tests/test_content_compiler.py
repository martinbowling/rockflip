"""Content identity and native safety regressions; no game progress injection."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
cc=module('content_compile','native/tools/content_compile.py')
ec=module('ecology','native/tools/validate_species.py')
def read(path):return json.loads((ROOT/path).read_text())
def pixels(name):return Image.open(ROOT/'art/out'/name)
def bits(im):
    out=[]
    for ty in range(0,im.height,8):
        for tx in range(0,im.width,8):
            for y in range(8):
                lo=hi=0
                for x in range(8):
                    v=im.getpixel((tx+x,ty+y));lo|=(v&1)<<(7-x);hi|=((v>>1)&1)<<(7-x)
                out += [lo,hi]
    return out
def decl(name,values):return 'static const UBYTE '+name+'[]={'+','.join(map(str,values))+'};\n'
class ContentTests(unittest.TestCase):
    def setUp(self):
        self.policy=read('data/roster_policy.json');self.registry=read('data/species_ecology.json');self.runtime=read('data/species.json');self.world=read('data/world.json');self.sites=read('data/foundation_encounters.json')
    def test_source_reordering_preserves_native_bank_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();out=root/'engine';(out/'include').mkdir(parents=True);(out/'src').mkdir()
            def emit(world,sites):
                (root/'data/world.json').write_text(json.dumps(world));(root/'data/foundation_encounters.json').write_text(json.dumps(sites))
                cc.emit_content(root,out,ROOT/'art/out',read('art/out/palettes.json'),self.runtime,pixels,bits,decl)
                return {f.name:f.read_bytes() for f in (out/'src').glob('*.c')}
            baseline=emit(self.world,self.sites)
            self.world['maps'].reverse();self.sites['records'].reverse()
            self.assertEqual(emit(self.world,self.sites),baseline)
    def test_period_zero_or_byte_overflow_cannot_enter_camera(self):
        for value in (0,256,-1,1.5):
            with self.subTest(value=value):
                self.runtime[6]['behavior_params']['period']=value
                with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,self.runtime)
    def test_unknown_behavior_rejected(self):
        self.runtime[6]['behavior']='imaginary'
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,self.runtime)
    def test_bad_min_distance_rejected(self):
        self.runtime[6]['behavior_params']['minimum_distance']=1
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,self.runtime)
    def test_fourth_fact_cannot_overrun_native_table(self):
        self.runtime[6]['facts'].append('EXTRA')
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,self.runtime)
    def test_duplicate_encounter_position_rejected(self):
        self.sites['records'][1]['game_tile_x']=4;self.sites['records'][1]['game_tile_y']=3
        with self.assertRaises(ec.EcologyError):ec.validate_encounters(self.policy,self.registry,self.sites,self.world)
    def test_blocked_arrival_rejected(self):
        self.world['maps'][2]['terrain'][3]='G'+self.world['maps'][2]['terrain'][3][1:]
        with self.assertRaises(ec.EcologyError):ec.validate_encounters(self.policy,self.registry,self.sites,self.world)
    def test_island_subarea_permission_is_enforced(self):
        record=next(r for r in self.registry['records'] if r['species_id']==10)
        with self.assertRaises(ec.EcologyError):ec.validate_placement(record,'D12','island_scrub','northern_island_woodland')
        ec.validate_placement(record,'D12','island_scrub','southern_island_scrub')
    def test_selected151_have_unique_native_species_and_guide_ids(self):
        records=read('data/production_roster.json')['records']
        self.assertEqual(len(records),151);self.assertEqual(len({r['canonical_scientific_name'] for r in records}),151)
        self.assertEqual([r['guide_number'] for r in records],list(range(1,152)))
        self.assertTrue(all(r['native_in_california'] and r['status']=='source_reviewed' and r['region_permissions'] for r in records))
        self.assertEqual(sum(r['hidden'] for r in records),1)
if __name__=='__main__':unittest.main()
