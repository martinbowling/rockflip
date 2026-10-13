import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ecology', ROOT/'native/tools/validate_species.py')
ec=importlib.util.module_from_spec(spec);spec.loader.exec_module(ec)

class EcologyTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads((ROOT/'data/roster_policy.json').read_text())
        self.registry=json.loads((ROOT/'data/species_ecology.json').read_text())
        self.lookup=ec.validate_registry(self.policy,self.registry)
    def test_all_151_runtime_species_have_support(self):
        self.assertEqual(ec.validate_runtime_species(),151)
    def test_toad_rejected_in_unapproved_alpine_region(self):
        with self.assertRaises(ec.EcologyError):ec.validate_placement(self.lookup[4],'D05','alpine_lake')
    def test_toad_rejected_in_dry_desert_burrow(self):
        with self.assertRaises(ec.EcologyError):ec.validate_placement(self.lookup[4],'D01','desert_burrow')
    def test_toad_spring_assignment_passes(self):
        ec.validate_placement(self.lookup[4],'D01','desert_spring')
    def test_statewide_occurrence_is_not_an_allowlist(self):
        with self.assertRaises(ec.EcologyError):ec.validate_placement(self.lookup[5],'D16')
    def test_repeat_species_does_not_inflate_count(self):
        self.registry['records'].append(copy.deepcopy(self.registry['records'][0]))
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry)
    def test_introduced_species_rejected(self):
        self.registry['records'][0]['native_in_california']=False
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry)
    def test_candidate_cannot_compile(self):
        self.registry['records'][0]['status']='candidate'
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry)
    def test_permission_without_evidence_rejected(self):
        self.registry['records'][0]['region_permissions'][0]['evidence_urls']=[]
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry)
    def test_nested_location_data_rejected(self):
        self.registry['records'][0]['extra']={'Coordinates':[1,2]}
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry)
    def test_reordered_runtime_would_misbind_art_and_is_rejected(self):
        runtime=json.loads((ROOT/'data/species.json').read_text())
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,list(reversed(runtime)))
    def test_duplicate_runtime_row_is_rejected(self):
        runtime=json.loads((ROOT/'data/species.json').read_text())
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,runtime+[copy.deepcopy(runtime[0])])
    def test_runtime_art_name_identity_mismatch_is_rejected(self):
        runtime=json.loads((ROOT/'data/species.json').read_text())
        runtime[0]['scientific_name']=runtime[1]['scientific_name']
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,runtime)
    def test_actual_encounter_table_covers_runtime_species(self):
        sites=json.loads((ROOT/'data/foundation_encounters.json').read_text())
        self.assertEqual(ec.validate_encounters(self.policy,self.registry,sites),set(range(151)))
    def test_actual_encounter_toad_in_dry_habitat_rejected(self):
        sites=json.loads((ROOT/'data/foundation_encounters.json').read_text())
        sites['records'][5]['habitat_id']='desert_burrow'
        with self.assertRaises(ec.EcologyError):ec.validate_encounters(self.policy,self.registry,sites)
    def test_actual_encounter_in_other_district_rejected(self):
        sites=json.loads((ROOT/'data/foundation_encounters.json').read_text())
        sites['records'][5]['region_id']='D05'
        with self.assertRaises(ec.EcologyError):ec.validate_encounters(self.policy,self.registry,sites)
    def test_private_coordinate_aliases_rejected(self):
        for key in ('private_latitude','private_longitude','decimalLatitude','decimalLongitude'):
            with self.subTest(key=key), self.assertRaises(ec.EcologyError):
                ec.reject_localities({'extra':[{key:0}]})
    def test_unknown_ecology_fields_rejected(self):
        self.registry['records'][0]['unreviewed_location_hint']='synthetic unsupported payload'
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry)
    def test_unknown_runtime_fields_rejected(self):
        runtime=json.loads((ROOT/'data/species.json').read_text())
        runtime[0]['unreviewed_payload']='synthetic unsupported payload'
        with self.assertRaises(ec.EcologyError):ec.validate_runtime_rows(self.policy,self.registry,runtime)
    def test_secret_slot_is_reserved_correctly(self):
        self.assertEqual(self.policy['hidden_discovery']['guide_number'],151)
        self.assertFalse(self.policy['hidden_discovery']['mandatory_for_ending'])
    def test_foundation_cannot_pass_full_release_gate(self):
        with self.assertRaises(ec.EcologyError):ec.validate_registry(self.policy,self.registry,release=True)
    def test_capacity_can_hold_release_target(self):
        self.assertEqual(self.policy['total_species_target'],151)
        self.assertGreaterEqual(self.policy['runtime_species_capacity'],151)

if __name__=='__main__':unittest.main()
