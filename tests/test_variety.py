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


if __name__ == "__main__":
    unittest.main()
