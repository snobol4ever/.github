# HANDOFF 2026-05-29 — Opus 4.8 — RAKU-BB mode-2 junctions COMPLETE + gather + ACOMP

**Repo:** one4all `30e7c0a1` (pushed). **Goal:** GOAL-RAKU-BB.md.
**Net:** GATE-RK mode-2 **23 → 26/33** (+rk_gather, +rk_given18, +rk_junctions). Zero regressions.

## What landed (4 pieces, 9 files)

### 1. RK-M2-GATHER — mode-2 gather multi-yield (`src/lower/bb_exec.c`)
`rk_gather` FAILed mode-2. The gather body lowers to `BB_SEQ → SUSPEND·SUSPEND·SUSPEND·FAIL`
(each `SUSPEND.α` = a `BB_LIT_I` take value; `γ==ω` advances). Mode-2 had no `BB_SUSPEND`
case (→ `default:` → FAIL) and `bb_exec_once/resume` walk to `next==NULL` with no pause-at-yield,
so the graph collapsed to FAIL on the first pull.

Fix: a gather driver INSIDE `case BB_SEQ`, gated `g_current_cfg->lang==BB_LANG_RKU &&
bb->α->t==BB_SUSPEND`. Yields ONE take per (re)entry using `bb->counter` as the resume cursor
(reset to 0 by `bb_exec_once`, preserved by `bb_exec_resume`); evaluates the counter-th SUSPEND's
`α` into `bb->value` and returns terminal `NULL` (driver hands value to the SM consumer); walking
past the last SUSPEND onto `BB_FAIL` → `FAILDESCR`. Mirrors the mode-3 `bb_seq_gather_binary`
(resume_slot ≡ counter; per-child γ-yield ≡ the NULL return through the driver loop). Ordinary
proc-body SEQs (α not a SUSPEND) take the unchanged AG-PURE passthrough.

### 2. RK-M2-ACOMP — `SM_ACOMP` string→numeric coercion (`src/processor/sm_interp.c`)
`rk_given18` FAILed mode-2: `given` on a `for`-loop variable missed every `when` arm. Array
elements pulled via `BB_ITERATE` arrive as `DT_S`; `SM_ACOMP` treated any non-`DT_I`/`DT_R`
operand as `0`, so topic `"1"` compared as `0==1` → false → default. Fix mirrors `SM_ADD`:
`lv = (l.v==DT_S) ? to_real(l) : ...` (and r). GATE-RK m2 +1.

**Shared path across all languages — verified zero regression:** SNOBOL4 crosscheck identical
before/after (stash test; `beauty_omega` FAIL is pre-existing); Icon real/int relop correct
direct (`x = 3.0` → equal; `i = 2` loop); broad broker 6/6; smokes hold.

### 3. RK-BB-4a — constructor junctions any/all/one/none (mode-2)
- `src/lower/lower.c` `lower_fnc`: Raku lowercase `any/all/one/none` intercept → `SM_CALL_FN
  __rk_jct_<flavor>` (NOT the SNOBOL4/Icon `ANY` pattern path). Skips the RK-BB-3.0a dup-name
  first arg (`c[0]=TT_VAR(name)`). Per RULES "behavior lives in lowering."
- `src/runtime/interp/raku_builtins_byname.c`: `__rk_jct_*` builders pack a tagged-string
  junction VALUE (Q12): `ETX(0x03) + flavor('a'/'l'/'o'/'n') + SOH-separated members`. ETX is
  free of the SOH(0x01)/STX(0x02) array/hash bytes. `rk_junction_is` + `rk_junction_collapse`
  (recursive on junction-tagged members) thread the relop per flavor: any=OR, all=AND,
  one=exactly-one, none=NONE. numeric path via `strtod`/`to_real`; string path via `strcmp`.
- `src/processor/sm_interp.c`: junction guard at the top of `SM_ACOMP` (numeric) and `SM_LCOMP`
  (string) — `DT_S && s[0]==0x03`, never fires for ordinary values → proven path untouched.

### 4. RK-BB-4b — infix `|`/`&` junctions (mode-2)
- `src/frontend/raku/raku.l`: single-char `"|"`→`'|'`, `"&"`→`'&'` AFTER `&&`/`||` (flex
  longest-match keeps those; no code-sigil conflict — `&`/`|` were untokenized).
- `src/frontend/raku/raku.y`: `mk_junction(flav,l,r)` builds `l|r`→`any(l,r)`, `l&r`→`all(l,r)`
  as the SAME `TT_FNC` node `make_call` produces, so infix + constructor share one lowering +
  collapse. **Same-flavor chains FLATTEN at parse time** (`(3&3)&3`→`all(3,3,3)`), sidestepping
  the nested-`\x01` leak in the flat SOH rep. `%left '|' '&'` between OP_AND and `'!'`.
- Regenerated `raku.tab.c`/`raku.lex.c`/`raku.tab.h` via
  `scripts/regenerate_parser_and_lexer_from_sources.sh` — **zero grammar conflicts**.

**Full `rk_junctions` probe PASS mode-2** (any/all/none/one + pipe + amp). The interim
`rk_junctions_ctor` probe was removed (subsumed by the canonical probe).

## Q9-Q12 (answered by Lon, 2026-05-29)
- Q9: reuse existing kinds; break out new SM/BB opcodes ONLY if language-specific behavior diverges.
- Q10: build on `BB_ALT` (live substrate Icon uses); split later.
- Q11: substrate-first.
- Q12: tagged-string rep.

## BB_ALT substrate — proven (no code change)
- mode-2: complete n-ary alternation engine. `x=(1|2|3)`→hit, `x=(7|8|9)`→miss,
  `every write(10|20|30)`→10/20/30.
- mode-4: `MEDIUM_BINARY` is a real counter-state dispatch slab (α zero-counter, β increment,
  per-arm `cmp rcx,i; je arm_α[i]`, exhaust `jmp ω`). The probe header's "stub"/"no-op" claims
  (#3/#4) refer to the ORPHAN `BB_ALTERNATE`; only the `MEDIUM_TEXT` arm is a passthrough.

## Gates
```
GATE-RK   mode-2:  26/33  (was 23)   fails = 6 regex (deferred) + rk_stdio39 (test-fidelity)
GATE-RK4  mode-4:  26/33  HOLD       (rk_junctions still mode-2-only — RK-BB-4c)
GATE-RK3  mode-3:  26/33  HOLD       (no native code touched this session)
smoke raku/prolog/icon/snobol4: 5/5/5/13   broad broker: 6/6   FACT: 0   build: clean
```

## NEXT — RK-BB-4c (mode-3/4 junctions)
`rk_junctions` FAILs mode-4 (mode-2-only collapse). The `__rk_jct_*` lowering is already
language-agnostic; the missing piece is the collapse at the `SM_ACOMP`/`SM_LCOMP` TEMPLATE sites.
- Route (i) [faster]: emit a `rt_junction_collapse` call (@PLT mode-4 / movabs+call mode-3) guarded
  on a junction-tagged operand — reuses the mode-2 helper. Builders + collapse are conversion/effect
  helpers (FACT-clean; no port-logic helper).
- Route (ii) [Q11 substrate-first]: lower `any`/`|` through the proven `BB_ALT` binary slab
  (first-success = any), all/none/one as collapse variants.
Recommend (i) to flip mode-4 green, then (ii) if the BB_ALT substrate should be exercised.

## NEXT-after — RK-BB-4d edges (documented in goal file)
1. MIXED-flavor NESTED junctions (`1 | (2 & 3)`) break the flat SOH rep (inner `\x01` leaks);
   needs length-prefixed members or SOH-escaping. Same-flavor chains already flatten, so the probe
   is fine.
2. Unparenthesized precedence of `$x == 1|2|3` (probe always parenthesizes).
3. Junction stored in a var / threaded through non-`==` relops (var round-trip untested).

## Flag for Lon — `rk_stdio39`
Mode-2 FAIL is a TEST-FIDELITY issue, not a bug. The `--interp` harness captures stdout only, but
`rk_stdio39.expected` lists `stderr ok` as line 3 (encoding `$*STDERR→fd 1`). Mode-2 correctly routes
`$*STDERR`→fd 2 (real Raku); mode-4 only "passes" by mis-routing stderr→stdout. Fix the golden, or
accept the mode-2/mode-4 divergence — your call.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
