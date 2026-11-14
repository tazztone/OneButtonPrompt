from dataclasses import dataclass, field
import re

try:
    from random_functions import PickContext
except ImportError:
    from .random_functions import PickContext


@dataclass
class PromptClause:
    compound_id: int
    bucket: str
    text: str
    is_subject: bool = False


@dataclass
class ResolutionState:
    used_values: set = field(default_factory=set)
    samehumansubject: str = ""
    sameothersubject: str = ""
    artiststyle: str = ""
    artistmedium: str = ""
    artistdescription: str = ""
    isphoto: int = 0
    smartsubject: bool = True


_TAG_SPAM = frozenset({
    "dslr", "masterpiece", "best quality", "high quality", "ultra detailed",
    "extremely detailed", "absurdres", "highres", "8k", "4k", "uhd", "hdr",
    "intricate details", "detailed background", "simple background", "white background",
    "bw", "monochrome", "grayscale", "photorealistic", "hyperrealistic",
    "octane render", "unreal engine", "artstation", "pixabay",
})

_TAG_SALAD_TOKENS = _TAG_SPAM | frozenset({
    "looking at viewer", "upper body", "lower body", "full body", "cowboy shot",
    "solo", "1girl", "1boy", "2girls", "2boys", "multiple girls", "multiple boys",
    "pov", "chibi", "anime",
})


def _pick_random_bracket(match, ctx):
    inner = match.group(1)
    if "|" in inner:
        parts = [p.strip() for p in inner.split("|") if p.strip()]
        if parts:
            return ctx.pick(parts, key="a1111_alt")
    if ":" in inner:
        # [a:b:N] or [a:b]
        parts = [p.strip() for p in inner.split(":")]
        candidates = [p for p in parts[:2] if p and not p.replace(".", "", 1).isdigit()]
        if candidates:
            return ctx.pick(candidates, key="a1111_swap")
    return inner


def strip_a1111_syntax(text: str, ctx=None) -> str:
    """
    Strip A1111/Danbooru weighting syntax while preserving legitimate English parentheticals
    such as `(circa 1920)` or `(born 1890)`.
    """
    if not text:
        return text
    if ctx is None:
        ctx = PickContext()

    out = text
    # 1. Resolve [a|b|c] and [a:b:N] brackets randomly (inside-out)
    for _ in range(8):
        new_out = re.sub(r"\[([^\[\]]+)\]", lambda m: _pick_random_bracket(m, ctx), out)
        if new_out == out:
            break
        out = new_out

    # 2. Iteratively strip weighted parens (phrase:1.2) inside-out
    for _ in range(8):
        new_out = re.sub(r"\(([^()]+?):\s*-?\d+(?:\.\d+)?\s*\)", r"\1", out)
        if new_out == out:
            break
        out = new_out

    # 3. Strip pure emphasis ((phrase)) / (((phrase))) while preserving single (circa 1920)
    for _ in range(8):
        new_out = re.sub(r"\(\(([^()]+)\)\)", r"\1", out)
        if new_out == out:
            break
        out = new_out

    # 4. Clean orphaned colons/double-commas/double-spaces
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,+", ", ", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip(" ,")


def _clean_fragment(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text.strip(" ,;"))


def _split_tag_salad(text: str, drop_spam: bool = False):
    """Separate natural prose clauses from short Danbooru/A1111 tag-salad fragments."""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    prose = []
    tags = []
    for p in parts:
        low = p.lower()
        if drop_spam and low in _TAG_SPAM:
            continue
        if low in _TAG_SALAD_TOKENS:
            tags.append(p)
        else:
            prose.append(p)
    return ", ".join(prose), ", ".join(tags)


def build_relational_subject(pools: dict, ctx, mute_pop_culture: bool = False) -> str:
    """Build cross-domain multi-subject compositions: [scalemod] subject_a + interaction + [scalemod] subject_b."""
    subject_keys = ["animal", "manwoman", "humanoid", "object"]
    if not mute_pop_culture:
        subject_keys.extend(["fictional", "nonfictional"])

    available = [k for k in subject_keys if pools.get(k)]
    if not available:
        return ""

    key_a = ctx.pick(available, key="rel_subj_key_a")
    key_b = ctx.pick(available, key="rel_subj_key_b")
    subj_a = ctx.pick(pools[key_a], key=f"rel_{key_a}_a")
    subj_b = ctx.pick(pools[key_b], key=f"rel_{key_b}_b")

    scalemods = pools.get("scalemod") or []
    if scalemods and ctx.randint(1, 4) == 1:
        subj_a = f"{ctx.pick(scalemods, key='rel_scale_a')} {subj_a}"
    if scalemods and ctx.randint(1, 4) == 1:
        subj_b = f"{ctx.pick(scalemods, key='rel_scale_b')} {subj_b}"

    interactions = pools.get("interaction") or ["standing beside"]
    interaction = ctx.pick(interactions, key="rel_interaction")

    phrase = f"a {subj_a} {interaction} a {subj_b}"

    props = pools.get("prop") or []
    flora = pools.get("flora") or []
    if props and ctx.randint(1, 3) == 1:
        phrase += f" near a {ctx.pick(props, key='rel_prop')}"
    elif flora and ctx.randint(1, 3) == 1:
        phrase += f" amidst {ctx.pick(flora, key='rel_flora')}"

    return phrase


_NATURAL_FRAMES = [
    lambda f, m, ar, s, d, st, a: ", ".join(p for p in (m, f, s, d, a, st, ar) if p) + ".",
    lambda f, m, ar, s, d, st, a: (
        f"In a scene framed by {f}, {s}"
        + "".join(f", {p}" for p in (d, m, a, ar) if p)
        + (f". {st}." if st else ".")
        if f
        else ", ".join(p for p in (m, s, d, a, st, ar) if p) + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"{s}{', ' + d if d else ''}, set against {a}"
        + "".join(f", {p}" for p in (f, m, st, ar) if p)
        + "."
        if a
        else ", ".join(p for p in (m, f, s, d, st, ar) if p) + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"{st + ': ' if st else ''}"
        + ", ".join(p for p in (m, f, s, d, a, ar) if p)
        + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"Captured with {a}, "
        + ", ".join(p for p in (m, s, d, f, st, ar) if p)
        + "."
        if a
        else ", ".join(p for p in (m, f, s, d, st, ar) if p) + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"{s} emerges{' amidst ' + a if a else ''}"
        + "".join(f", {p}" for p in (d, f, m, st, ar) if p)
        + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"A {m + ' ' if m else ''}view of {s}"
        + "".join(f", {p}" for p in (d, f, a, st, ar) if p)
        + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"{f + ' — ' if f else ''}"
        + ", ".join(p for p in (m, s, d, a, st, ar) if p)
        + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"The focus rests on {s}"
        + "".join(f", {p}" for p in (d, a, f, m, st, ar) if p)
        + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"{s}{', ' + d if d else ''}"
        + ("; " + ", ".join(p for p in (a, f, m, st, ar) if p) if any((a, f, m, st, ar)) else "")
        + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        f"With {f}, "
        + ", ".join(p for p in (m, s, d, a, st, ar) if p)
        + "."
        if f
        else ", ".join(p for p in (m, s, d, a, st, ar) if p) + "."
    ),
    lambda f, m, ar, s, d, st, a: (
        ", ".join(p for p in (ar, m, s, d, f, a, st) if p) + "."
    ),
]


def _format_natural_compound(buckets: dict, ctx, natural_language: bool = False) -> str:
    f = _clean_fragment(buckets.get("framing", ""))
    f = re.sub(r"\b(?:of\s+a|of)\s*$", "", f, flags=re.IGNORECASE).strip(" ,;")
    m = _clean_fragment(buckets.get("medium", ""))
    ar = _clean_fragment(buckets.get("artist", ""))
    s = _clean_fragment(buckets.get("subject", ""))
    d = _clean_fragment(buckets.get("details", ""))
    st = _clean_fragment(buckets.get("style", ""))
    a = _clean_fragment(buckets.get("atmosphere_tech", ""))

    # Separate tag-salad fragments into trailing qualifiers
    trailing_tags = []
    f, t_f = _split_tag_salad(f, drop_spam=natural_language)
    m, t_m = _split_tag_salad(m, drop_spam=natural_language)
    d, t_d = _split_tag_salad(d, drop_spam=natural_language)
    st, t_st = _split_tag_salad(st, drop_spam=natural_language)
    a, t_a = _split_tag_salad(a, drop_spam=natural_language)
    for t in (t_f, t_m, t_d, t_st, t_a):
        if t:
            trailing_tags.append(t)

    if not s:
        parts = [p for p in (m, f, d, a, st, ar) if p]
        base = ", ".join(parts)
    else:
        frame_fn = ctx.pick(_NATURAL_FRAMES, key="natural_frame")
        base = frame_fn(f, m, ar, s, d, st, a)

    base = _clean_fragment(base)
    base = re.sub(r"[,;\s]+\.", ".", base)
    base = re.sub(r"\.{2,}", ".", base)
    if trailing_tags:
        tag_str = ", ".join(trailing_tags)
        base = f"{base}, {tag_str}" if base else tag_str
    return base


def _strip_trailing_of_a(text: str) -> str:
    return re.sub(r"\b(?:of\s+a|of\s+an|of)\s*$", "", text, flags=re.IGNORECASE).strip(" ,;")


def _format_shuffled_compound(buckets: dict, coherence: str, ctx) -> str:
    non_subj_keys = [k for k in ("framing", "medium", "artist", "details", "style", "atmosphere_tech") if buckets.get(k)]
    ctx.shuffle(non_subj_keys)

    drop_chance = 0.0
    if coherence == "wild":
        drop_chance = 0.2
    elif coherence == "chaos":
        drop_chance = 0.35

    kept = []
    for k in non_subj_keys:
        if drop_chance > 0 and ctx.random() < drop_chance and len(kept) >= 1:
            continue
        val = _clean_fragment(buckets[k])
        if k == "framing":
            val = _strip_trailing_of_a(val)
        if val:
            kept.append(val)

    subj = _clean_fragment(buckets.get("subject", ""))
    if subj:
        insert_pos = ctx.randint(0, len(kept))
        kept.insert(insert_pos, subj)
    return ", ".join(p for p in kept if p)


def _format_soup_compound(buckets: dict, soup_pools: dict, ctx) -> str:
    parts = []
    for k, v in buckets.items():
        val = _clean_fragment(v)
        if k == "framing":
            val = _strip_trailing_of_a(val)
        if val:
            parts.append(val)
    if soup_pools:
        for key in ("tokens", "abstract_concepts", "media_artifacts"):
            pool = soup_pools.get(key)
            if pool and ctx.randint(1, 2) == 1:
                parts.append(ctx.pick(pool, key=f"soup_{key}"))
    ctx.shuffle(parts)
    return ", ".join(p for p in parts if p)


def compose_clauses(
    clauses: list,
    grammar_mode: str,
    coherence: str,
    ctx,
    remove_weights: bool = False,
    natural_language: bool = False,
    soup_pools: dict = None,
) -> tuple:
    """
    Compose PromptClause objects into (completeprompt, prompt_g, prompt_l).
    prompt_g contains subject clauses; prompt_l contains non-subject clauses.
    """
    if ctx is None:
        ctx = PickContext()

    effective_mode = grammar_mode
    if effective_mode == "auto":
        roll = ctx.random()
        if coherence == "strict":
            soup_thresh = 0.0
        elif coherence in ("wild", "chaos"):
            soup_thresh = 0.20
        else:
            soup_thresh = 0.10
        if roll < soup_thresh:
            effective_mode = "soup"
        elif roll < soup_thresh + 0.25:
            effective_mode = "shuffled"
        else:
            effective_mode = "natural"

    # Group clauses by compound_id
    compounds = {}
    user_prefixes = []
    user_suffixes = []
    for c in clauses:
        text = strip_a1111_syntax(c.text, ctx=ctx) if remove_weights else c.text
        text = _clean_fragment(text)
        if not text:
            continue
        if c.bucket == "user_prefix":
            user_prefixes.append(text)
            continue
        if c.bucket == "user_suffix":
            user_suffixes.append(text)
            continue
        compounds.setdefault(c.compound_id, []).append(
            PromptClause(c.compound_id, c.bucket, text, c.is_subject)
        )

    compound_strings = []
    g_parts = []
    l_parts = []

    for cid in sorted(compounds.keys()):
        c_list = compounds[cid]
        for c in c_list:
            if c.is_subject:
                g_parts.append(c.text)
            else:
                l_parts.append(c.text)

        if len(c_list) == 1 and c_list[0].bucket == "monolith":
            compound_strings.append(c_list[0].text)
            continue

        buckets = {}
        for c in c_list:
            if c.bucket in buckets:
                buckets[c.bucket] = f"{buckets[c.bucket]}, {c.text}"
            else:
                buckets[c.bucket] = c.text

        if effective_mode == "standard":
            ordered = [_clean_fragment(c.text) for c in c_list if _clean_fragment(c.text)]
            compound_strings.append(", ".join(ordered))
        elif effective_mode == "shuffled":
            compound_strings.append(_format_shuffled_compound(buckets, coherence, ctx))
        elif effective_mode == "soup":
            compound_strings.append(_format_soup_compound(buckets, soup_pools, ctx))
        else:
            # "natural"
            compound_strings.append(_format_natural_compound(buckets, ctx, natural_language=natural_language))

    main_str = " | ".join(s for s in compound_strings if s) if len(compound_strings) > 1 else (compound_strings[0] if compound_strings else "")
    prefix_str = ", ".join(user_prefixes)
    suffix_str = ", ".join(user_suffixes)

    full_parts = [p for p in (prefix_str, main_str, suffix_str) if p]
    completeprompt = ", ".join(full_parts)
    completeprompt = re.sub(r"[,;\s]+\.", ".", completeprompt)
    completeprompt = re.sub(r"\.{2,}", ".", completeprompt)
    prompt_g = ", ".join(p for p in g_parts if p)
    if not prompt_g:
        prompt_g = main_str or completeprompt
    prompt_l = ", ".join(p for p in l_parts if p)
    prompt_l = re.sub(r"\b(landscape|close\s+up)\s+of\s+an?\b", r"\1", prompt_l, flags=re.IGNORECASE)

    return completeprompt, prompt_g, prompt_l
