import os
import re
import sys
import tempfile
import time
import types
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Stub ComfyUI / torch-dependent modules when running standalone
if "folder_paths" not in sys.modules:
    _fp = types.ModuleType("folder_paths")
    _fp.base_path = REPO_ROOT
    _fp.get_folder_paths = lambda *args, **kwargs: []
    sys.modules["folder_paths"] = _fp

if "superprompter" not in sys.modules:
    sys.modules["superprompter"] = types.ModuleType("superprompter")
    sys.modules["superprompter.superprompter"] = types.ModuleType("superprompter.superprompter")
    sys.modules["OneButtonPrompt.superprompter"] = sys.modules["superprompter"]
    sys.modules["OneButtonPrompt.superprompter.superprompter"] = sys.modules["superprompter.superprompter"]

from csv_reader import csv_to_list
from prompt_composer import strip_a1111_syntax
from build_dynamic_prompt import build_dynamic_prompt, createpromptvariant
PARENT_DIR = os.path.dirname(REPO_ROOT)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
import OneButtonPrompt.OneButtonPromptNodes as OneButtonPromptNodes


class TestHighVariancePrompts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO_ROOT, "build_dynamic_prompt.py"), "r", encoding="utf-8") as f:
            cls.registered_wildcards = set(re.findall(r'"(-[a-z0-9]+-)"', f.read()))

    def test_01_syntax_hygiene_and_weight_stripping(self):
        self.assertIn(
            strip_a1111_syntax("(circa 1920) ((bold)) (foo:1.2) [a|b]"),
            ("(circa 1920) bold foo a", "(circa 1920) bold foo b"),
        )
        idx = 0
        for coh in ("strict", "balanced", "wild", "chaos"):
            for gm in ("auto", "natural", "shuffled", "soup"):
                for ins in (2, 5, 8):
                    idx += 1
                    p = build_dynamic_prompt(
                        insanitylevel=ins,
                        base_model="Natural Language",
                        coherence=coh,
                        grammar_mode=gm,
                        use_shuffle_bag=True,
                        seed=200 + idx,
                    )
                    self.assertTrue(isinstance(p, str) and len(p) > 0)
                    self.assertNotIn("OR(", p)
                    self.assertIsNone(re.search(r":\d+\.\d+\)", p), f"Leaked weight: {p}")
                    self.assertNotIn("[", p)
                    self.assertNotIn("]", p)
                    self.assertNotIn("cameran", p.lower())
                    self.assertNotIn("a hour", p.lower())
                    self.assertNotIn("an unicorn", p.lower())
                    dangling = [t for t in re.findall(r"-[a-z0-9]+-", p) if t in self.registered_wildcards]
                    self.assertEqual(dangling, [], f"Dangling wildcards {dangling} in {p}")

    def test_02_legacy_compat_and_comfy_nodes(self):
        leg = build_dynamic_prompt(base_model="SDXL", seed=42)
        self.assertTrue(isinstance(leg, str) and len(leg) > 10)
        var = createpromptvariant("a -cameraangle- of -weather- and -archstyle-")
        self.assertNotIn("-cameraangle-", var)
        self.assertNotIn("-weather-", var)
        self.assertNotIn("-archstyle-", var)

        self.assertIn("OneButtonPrompt", OneButtonPromptNodes.NODE_CLASS_MAPPINGS)
        self.assertIn("OneButtonPromptWild", OneButtonPromptNodes.NODE_CLASS_MAPPINGS)

        legacy_node = OneButtonPromptNodes.NODE_CLASS_MAPPINGS["OneButtonPrompt"]()
        out_leg = legacy_node.Comfy_OBP(5, "", 42, "all", "all", "------ all", 20, "all", False, "", "SDXL", "none", "", "")
        self.assertEqual(len(out_leg), 3)

        wild_cls = OneButtonPromptNodes.NODE_CLASS_MAPPINGS["OneButtonPromptWild"]
        input_types = wild_cls.INPUT_TYPES()
        for section in ("required", "optional"):
            for k, spec in input_types.get(section, {}).items():
                if isinstance(spec[0], list) and len(spec) > 1 and "default" in spec[1]:
                    self.assertIn(spec[1]["default"], spec[0], f"Invalid COMBO default for {k}")

        wild_node = wild_cls()
        out_wild = wild_node.Comfy_OBP_Wild(insanitylevel=5, seed=42, unique_id="test_node_1")
        self.assertEqual(len(out_wild), 3)
        self.assertTrue(len(out_wild[0]) > 0)

    def test_03_shuffle_bag_lru_replay_and_csv_cache(self):
        # Interleaved two-node replay
        a1 = build_dynamic_prompt(base_model="Natural Language", coherence="wild", grammar_mode="natural", use_shuffle_bag=True, stream_id="n1", seed=301)
        b1 = build_dynamic_prompt(base_model="Natural Language", coherence="wild", grammar_mode="natural", use_shuffle_bag=True, stream_id="n2", seed=401)
        a1_r = build_dynamic_prompt(base_model="Natural Language", coherence="wild", grammar_mode="natural", use_shuffle_bag=True, stream_id="n1", seed=301)
        b1_r = build_dynamic_prompt(base_model="Natural Language", coherence="wild", grammar_mode="natural", use_shuffle_bag=True, stream_id="n2", seed=401)
        self.assertEqual(a1, a1_r)
        self.assertEqual(b1, b1_r)

        # Advancing seed progresses
        a2 = build_dynamic_prompt(base_model="Natural Language", coherence="wild", grammar_mode="natural", use_shuffle_bag=True, stream_id="n1", seed=302)
        self.assertNotEqual(a1, a2)

        # tokens.csv cached tuple & post-cache antilist
        t0 = time.time()
        toks = csv_to_list("tokens", skipheader=True, copy_list=False)
        self.assertIsInstance(toks, tuple)
        self.assertGreater(len(toks), 500000)
        toks_warm = csv_to_list("tokens", skipheader=True, copy_list=False)
        self.assertIs(toks, toks_warm)
        self.assertLess(time.time() - t0, 5.0)

        # mtime invalidation
        with tempfile.TemporaryDirectory() as tmpdir:
            p = os.path.join(tmpdir, "sample.csv")
            with open(p, "w", encoding="utf-8") as f:
                f.write("alpha\nbeta\n")
            r1 = csv_to_list("sample", directory=tmpdir + os.sep, delimiter="?")
            self.assertEqual(r1, ["alpha", "beta"])
            time.sleep(0.02)
            with open(p, "w", encoding="utf-8") as f:
                f.write("alpha\nbeta\ngamma\n")
            r2 = csv_to_list("sample", directory=tmpdir + os.sep, delimiter="?")
            self.assertEqual(r2, ["alpha", "beta", "gamma"])
            r_anti = csv_to_list("sample", antilist=["beta"], directory=tmpdir + os.sep, delimiter="?")
            self.assertEqual(r_anti, ["alpha", "gamma"])
            r_clean = csv_to_list("sample", directory=tmpdir + os.sep, delimiter="?")
            self.assertEqual(r_clean, ["alpha", "beta", "gamma"])

    def test_04_clause_buffer_prompt_g_and_l_splitting(self):
        for gm in ("auto", "natural", "shuffled", "soup"):
            full, pg, pl = build_dynamic_prompt(
                base_model="Natural Language",
                coherence="wild",
                grammar_mode=gm,
                prompt_g_and_l=True,
                promptcompounderlevel="2",
                seed=555,
            )
            self.assertTrue(len(full) > 0)
            self.assertTrue(len(pg) > 0)
            self.assertTrue(len(pl) > 0)
            self.assertNotIn("of a.", pl)

    def test_05_variety_gain_benchmark(self):
        wild_prompts = [
            build_dynamic_prompt(
                base_model="Natural Language",
                coherence="wild",
                grammar_mode="auto",
                use_shuffle_bag=True,
                stream_id="bench_wild",
                seed=1000 + i,
            )
            for i in range(20)
        ]
        wild_trigrams = {tuple(p.lower().split()[:3]) for p in wild_prompts}
        self.assertEqual(len(set(wild_prompts)), 20)
        self.assertGreaterEqual(len(wild_trigrams), 12)

    def test_06_csv_schema_integrity(self):
        for name in ("weather", "textures", "props", "architectural_styles", "cinematicstyles", "interactions", "camera_angles", "compositions", "atmosphere", "media_artifacts", "scale_modifiers", "abstract_concepts"):
            rows = csv_to_list(name, directory="./csvfiles/", delimiter="?", bypass_subsets=True)
            self.assertGreater(len(rows), 0, f"{name}.csv is empty")

        for sname in ("insideshots", "minilocationadditions", "backgroundtypes", "buildhair", "buildaccessorie", "buildface", "objectadditions", "humanadditions", "conceptmixer"):
            rows = csv_to_list(sname, directory="./csvfiles/special_lists/", delimiter="?")
            self.assertGreater(len(rows), 0, f"{sname}.csv is empty")

        for tname in ("dynamic_templates_prefix", "dynamic_templates_suffix", "tokinator", "modern_templates"):
            rows = csv_to_list(tname, directory="./csvfiles/templates/", delimiter="?")
            self.assertGreater(len(rows), 0, f"{tname}.csv is empty")

        with open(os.path.join(REPO_ROOT, "csvfiles/templates/modern_templates.csv"), "r", encoding="utf-8") as f:
            mt_tokens = set(re.findall(r"-[a-z0-9]+-", f.read()))
        self.assertEqual(mt_tokens - self.registered_wildcards, set())

        for fname in ("fictional characters", "nonfictional characters"):
            rows = csv_to_list(fname, directory="./csvfiles/", delimiter=";", listoflistmode=True)
            for row in rows:
                if row:
                    self.assertGreaterEqual(len(row), 2, f"{fname}.csv has short row: {row}")

    def test_07_phase5_composer_and_syntax(self):
        from build_dynamic_prompt import build_dynamic_negative
        dangling_ends = (" to", " into", " beside", " atop", " for")
        for i in range(25):
            p = build_dynamic_prompt(
                insanitylevel=6,
                base_model="Natural Language",
                coherence="chaos",
                grammar_mode="soup",
                seed=500 + i,
            )
            self.assertFalse(p.lower().rstrip(".").endswith(dangling_ends), f"Dangling soup ending: {p}")

        for i in range(25):
            p = build_dynamic_prompt(
                insanitylevel=6,
                base_model="Natural Language",
                coherence="wild",
                grammar_mode="natural",
                prefixprompt="USER_PRE",
                suffixprompt="USER_SUF",
                seed=600 + i,
            )
            self.assertNotIn("framed by art by", p.lower())
            self.assertNotIn("captured with ,", p.lower())
            self.assertTrue(p.startswith("USER_PRE"), f"Missing user_prefix: {p}")
            self.assertTrue(p.endswith("USER_SUF"), f"Missing user_suffix: {p}")

        neg = build_dynamic_negative(
            positive_prompt="a cat",
            insanitylevel=3,
            base_model="Natural Language",
        )
        self.assertNotRegex(neg, r":[0-9]+\.[0-9]+")

        p_comp = build_dynamic_prompt(
            insanitylevel=5,
            base_model="Natural Language",
            coherence="wild",
            grammar_mode="natural",
            promptcompounderlevel="2",
            prefixprompt="USER_PRE",
            suffixprompt="USER_SUF",
            seed=650,
        )
        self.assertEqual(p_comp.count("USER_PRE"), 1)
        self.assertEqual(p_comp.count("USER_SUF"), 1)

    def test_08_phase5_mute_pop_culture_and_expanded_csvs(self):
        for subj in ("all", "humanoid", "animal", "landscape"):
            for i in range(10):
                p = build_dynamic_prompt(
                    insanitylevel=6,
                    forcesubject=subj,
                    base_model="Natural Language",
                    coherence="wild",
                    grammar_mode="auto",
                    mute_pop_culture=True,
                    seed=700 + i,
                )
                self.assertNotIn("-pokemon-", p)
                self.assertNotIn("-locationvideogame-", p)
                self.assertNotIn("-fictional-", p)
                self.assertNotIn("-nonfictional-", p)

        min_sizes = [
            ("faceparts", "./csvfiles/", 35, ";"),
            ("hairvomit", "./csvfiles/", 35, "?"),
            ("minioutfits", "./csvfiles/", 40, "?"),
            ("prints", "./csvfiles/", 40, ";"),
            ("elements", "./csvfiles/", 40, ";"),
            ("focus", "./csvfiles/", 40, ";"),
            ("buildfaceparts", "./csvfiles/special_lists/", 30, "?"),
            ("animaladditions", "./csvfiles/special_lists/", 32, "?"),
            ("animalsuffixadditions", "./csvfiles/special_lists/", 35, "?"),
            ("miniactivity", "./csvfiles/special_lists/", 45, "?"),
            ("modern_templates", "./csvfiles/templates/", 90, "?"),
        ]
        for name, directory, min_len, delim in min_sizes:
            rows = csv_to_list(name, directory=directory, delimiter=delim, bypass_subsets=True)
            self.assertGreaterEqual(len(rows), min_len, f"{name}.csv has {len(rows)} < {min_len}")

        with open(os.path.join(REPO_ROOT, "csvfiles/minioutfits.csv"), "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                s = line.strip()
                if not s:
                    continue
                parts = s.split("?")
                self.assertEqual(len(parts), 2, f"minioutfits.csv:{line_no} invalid format: {s}")
                self.assertIn(parts[1], ("both", "female", "male"), f"minioutfits.csv:{line_no} invalid gender: {s}")

    def test_09_all_node_inputs_have_tooltips(self):
        for node_name, node_cls in OneButtonPromptNodes.NODE_CLASS_MAPPINGS.items():
            input_types = node_cls.INPUT_TYPES()
            for section in ("required", "optional"):
                for input_name, spec in input_types.get(section, {}).items():
                    self.assertGreaterEqual(len(spec), 2, f"{node_name}.{section}.{input_name} missing options dict")
                    self.assertIsInstance(spec[1], dict, f"{node_name}.{section}.{input_name} options must be dict")
                    tooltip = spec[1].get("tooltip")
                    self.assertIsInstance(tooltip, str, f"{node_name}.{section}.{input_name} missing string tooltip")
                    self.assertTrue(tooltip.strip(), f"{node_name}.{section}.{input_name} has empty tooltip")

    def test_10_phase6_expanded_pools_and_cleanup(self):
        import build_dynamic_prompt as _bdp_mod
        # 1. Zero trailing ", ." in cleanup() and generated prompts
        self.assertEqual(_bdp_mod.cleanup("a cabin, .", "SDXL"), "a cabin.")
        for seed in range(500, 520):
            p = build_dynamic_prompt(
                insanitylevel=5,
                seed=seed,
                base_model="Natural Language",
                coherence="wild",
                grammar_mode="natural",
            )
            self.assertFalse(p.endswith(", ."), f"Trailing ', .' in seed {seed}: {p}")
            self.assertNotIn("-storycue-", p, f"Leaked -storycue- in seed {seed}: {p}")

        # 2. createpromptvariant resolves -storycue-
        variant = _bdp_mod.createpromptvariant("a cabin with -storycue-")
        self.assertNotIn("-storycue-", variant)
        self.assertTrue(variant.strip())

        # 3. Non-empty prompt_g in templatemode with prompt_g_and_l=True
        res = build_dynamic_prompt(
            insanitylevel=5,
            seed=777,
            base_model="Natural Language",
            imagetype="only templates mode",
            prompt_g_and_l=True,
        )
        self.assertIsInstance(res, tuple)
        self.assertTrue(res[1].strip(), "prompt_g should be non-empty in templatemode")

        # 4. Zero "cosplaying as" under mute_pop_culture=True
        for seed in range(600, 625):
            p = build_dynamic_prompt(
                insanitylevel=7,
                seed=seed,
                forcesubject="humanoid",
                mute_pop_culture=True,
            )
            self.assertNotIn("cosplaying as", p.lower())

        # 5. manwomanrelations.csv ;female|male|genderless format
        rel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "csvfiles", "manwomanrelations.csv")
        with open(rel_path, "r", encoding="utf-8") as f:
            rel_lines = [l.strip() for l in f if l.strip()]
        self.assertEqual(rel_lines[0], "manwomanrelation;gender")
        self.assertGreaterEqual(len(rel_lines), 35)
        for line in rel_lines[1:]:
            parts = line.split(";")
            self.assertEqual(len(parts), 2, f"Invalid manwomanrelations row: {line}")
            self.assertIn(parts[1], ("female", "male", "genderless"), f"Invalid gender in: {line}")

        # 6. Phase 6 CSV minimum counts
        root = os.path.dirname(os.path.dirname(__file__))
        min_counts = {
            "csvfiles/cameras.csv": 80,
            "csvfiles/lenses.csv": 78,
            "csvfiles/lenses_medium.csv": 50,
            "csvfiles/lighting.csv": 115,
            "csvfiles/lighting_medium.csv": 60,
            "csvfiles/descriptors.csv": 770,
            "csvfiles/quality.csv": 88,
            "csvfiles/events.csv": 340,
            "csvfiles/locationsbiome.csv": 141,
            "csvfiles/poses.csv": 160,
            "csvfiles/focus_light.csv": 25,
            "csvfiles/focus_medium.csv": 32,
            "csvfiles/lenses_light.csv": 28,
            "csvfiles/lighting_light.csv": 35,
            "csvfiles/directions_light.csv": 28,
            "csvfiles/directions_medium.csv": 38,
            "csvfiles/directions.csv": 50,
            "csvfiles/imagetypes_light.csv": 28,
            "csvfiles/imagetypes_medium.csv": 40,
            "csvfiles/shotsizes_light.csv": 32,
            "csvfiles/moods_light.csv": 40,
            "csvfiles/story_cues.csv": 60,
            "csvfiles/templates/modern_templates.csv": 140,
        }
        for rel, minimum in min_counts.items():
            with open(os.path.join(root, rel), "r", encoding="utf-8") as f:
                count = sum(1 for l in f if l.strip())
            self.assertGreaterEqual(count, minimum, f"{rel} has {count} < {minimum}")

        # 7. modern_templates.csv wildcards resolve cleanly
        with open(os.path.join(root, "csvfiles/templates/modern_templates.csv"), "r", encoding="utf-8") as f:
            templates = [l.strip() for l in f if l.strip()]
        for tmpl in templates[-20:]:
            resolved = _bdp_mod.createpromptvariant(tmpl)
            self.assertNotIn("-storycue-", resolved)

    def test_11_frontend_labels_and_wild_renames(self):
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "__init__.py"), "r", encoding="utf-8") as f:
            init_src = f.read()
        self.assertIn('WEB_DIRECTORY = "./web"', init_src)
        self.assertIn("WEB_DIRECTORY", init_src)

        js_path = os.path.join(root, "web", "js", "obp_labels.js")
        self.assertTrue(os.path.isfile(js_path), f"Missing {js_path}")
        with open(js_path, "r", encoding="utf-8") as f:
            js_src = f.read()

        block_match = re.search(r"const LABEL_OVERRIDES\s*=\s*\{(.*?)\n\};", js_src, re.S)
        self.assertIsNotNone(block_match, "LABEL_OVERRIDES not found in obp_labels.js")
        for node_name, body in re.findall(r"(\w+)\s*:\s*\{([^}]*)\}", block_match.group(1)):
            self.assertIn(node_name, OneButtonPromptNodes.NODE_CLASS_MAPPINGS)
            it = OneButtonPromptNodes.NODE_CLASS_MAPPINGS[node_name].INPUT_TYPES()
            all_keys = set(it.get("required", {})) | set(it.get("optional", {}))
            for py_key in re.findall(r"(\w+)\s*:", body):
                self.assertIn(py_key, all_keys, f"{node_name}.{py_key} missing from INPUT_TYPES()")

        wild_cls = OneButtonPromptNodes.NODE_CLASS_MAPPINGS["OneButtonPromptWild"]
        wild_opt = wild_cls.INPUT_TYPES()["optional"]
        for new_k in ("custom_subject", "exclude_terms", "preset"):
            self.assertIn(new_k, wild_opt)
        for old_k in ("givensubject", "antivalues", "obp_preset"):
            self.assertNotIn(old_k, wild_opt)
        out = wild_cls().Comfy_OBP_Wild(
            insanitylevel=5, seed=42, custom_subject="cyberpunk fox", exclude_terms="cat", preset="none"
        )
        self.assertEqual(len(out), 3)
        self.assertTrue(len(out[0]) > 0)


if __name__ == "__main__":
    unittest.main()
