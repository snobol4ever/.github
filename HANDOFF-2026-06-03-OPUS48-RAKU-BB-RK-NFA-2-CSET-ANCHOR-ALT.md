# HANDOFF 2026-06-03 (Opus 4.8) — RAKU-BB: RK-NFA-2 (L4-L12 cset/anchor/ordered-alt verdict set)

## TL;DR

- **RK-NFA-2 LANDED** — the L4-L12 cset/anchor/ordered-alt verdict set is now FORMALIZED as an
  oracle-equivalence proof. The IR_NFA_* graph backtracking walk (`raku_nfa_bb.c`, `RK_NFA_BB=1`)
  is proven byte-identical to the parallel-NFA oracle (`raku_re.c raku_nfa_exec`, `RK_NFA_BB=0`) on
  a 23-probe cset/anchor verdict battery + an 8-probe safe-extent capture battery.
- **ISOLATED, gate+corpus only:** ZERO C / lowerer / emitter / template touched. The IR-graph walker
  already handled all of L4-L12 (RK-NFA-1 exercised a subset); this rung pins down the full edge-case
  verdict set and documents the `|`-LTM vs `||`-ordered SPLIT-resolution seam.
- **The semantic finding (most important carry-forward):** single `|` lowers to an NFA SPLIT; the
  oracle resolves it leftmost-LONGEST (Raku `|` = LTM/declarative), the backtracking walker resolves
  it leftmost-FIRST (Raku `||` = ordered). **Verdicts agree everywhere; match EXTENT/captures agree
  only where leftmost-longest == leftmost-first.** Overlapping-`|` extent (`/(a|ab)/`~"ab" → oracle
  "ab" vs walker "a") diverges BY DESIGN — it is the Phase-2 `|`-LTM-on-parallel-NFA vs
  `||`-ordered-on-IR_NFA_* boundary, not a bug. `||` is not yet parseable.
- All gates GREEN; SNOBOL4 7/7 / Icon 12/12 m2 byte-unchanged; prove_lower2 67/0; FACT md5 ×3 unchanged.
- Mode-2 only (the HARD oracle). The NFA leaf templates remain SHELVED (tier-seam decision), so
  modes 3/4 EXCISE this path — untouched by this rung.

## COMMITS

- SCRIP `<this commit>` — RK-NFA-2: extend `test_gate_raku_nfa_oracle.sh` with the L4-L12 cset/anchor
  + safe-extent batteries; add `test/raku/rk_re38.raku` + `.expected`. (Parent: Pascal `9af83ea`.)
- .github `<this commit>` — GOAL-RAKU-BB.md: RK-NFA-2 rung [x], gate-table line, NEXT line, watermark.

## WHAT LANDED

### 1. `scripts/test_gate_raku_nfa_oracle.sh` (the formalization mechanism)

Inserted an **RK-NFA-2 section** between the RK-NFA-1 verdict section and the RK-NFA-3 capture
section. Two new batteries, each run under both `RK_NFA_BB=0` (parallel oracle) and `RK_NFA_BB=1`
(IR-graph backtracking walk), with `diff` required empty:

- **`$TMP/cset.raku` — 23 cset/anchor verdict probes:**
  - Negated shorthand csets: `\D`, `\W`, `\S` (NK_CLASS with inverted bitmap, shared by both engines),
    plus `\w` full coverage and `\s` tab.
  - Enumerated csets: multi-range `[a-z0-9]`, negated `[^0-9]`, two-range `[A-Za-z]`.
  - Mixed shorthand inside `[...]`: `[\d\s]`, `[\w-]` (word + literal dash).
  - BOL/EOL anchors: `^h`, `^e` (miss), `o$`, `h$` (miss), `^hello$`, `^hello$` long-miss, `^$` empty.
- **`$TMP/ext2.raku` — 8 safe-extent capture probes** (the envelope where leftmost-longest ==
  leftmost-first): disjoint alternation `(foo|bar)`, anchored alternation `^(cat|dog)$`, greedy
  negated/range/digit csets `(\D+)`/`([a-z]+)`/`([0-9]+)`, two greedy captures `(\w+)=(\w+)`, named
  captures over csets, greedy star `(a*)`.

The gate header + an in-line SEMANTIC NOTE document the `|`/`||` seam (see TL;DR). Header bumped to
"RK-NFA-1/2/3 oracle-equivalence gate".

Gate output now:
```
PASS: 30 verdict probes — IR_NFA_* graph walk == parallel-NFA oracle (byte-identical)        [RK-NFA-1]
PASS: 23 cset/anchor verdict probes — IR_NFA_* graph walk == parallel-NFA oracle (byte-identical)  [RK-NFA-2]
PASS: safe-extent captures (greedy / disjoint+anchored alt / csets) — IR-graph spans == oracle      [RK-NFA-2]
PASS: captures ($0/$1/$<name>) — IR-graph spans == parallel-NFA oracle (byte-identical)        [RK-NFA-3]
```

### 2. `test/raku/rk_re38.raku` + `.expected` (durable corpus artifact)

Follows the established `rk_re3X` convention (32=compile, 33=match, 34=pos-cap, 35=named-cap,
37=global/subst → **38=cset/anchor edge-case verdicts**). 21 lines of self-checking verdict output,
verified IDENTICAL between both matchers and matching `.expected` under default mode-2.

## SEMANTICS — grounded in the uploaded Rakudo sources (per the standing instruction)

Read BEFORE coding from `rakudo-main/src/Raku/ast/regex.rakumod`:
- `RakuAST::Regex::CharClass::Digit/Word/Space` → `QAST::Regex.new(:rxtype<cclass>, :name<d|w|s>,
  :negate(self.negated))` — the negatable built-in classes; `\D`/`\W`/`\S` are the `:negate` forms.
  Matches the C builder's `cc_fill_{digit,word,space}` + `cc_invert`.
- `RakuAST::Regex::CharClass::Any` → `:rxtype<cclass> :name<.>` — and the GOAL-locked note "`.` =
  non-newline" matches the C `NK_ANY` (`ch != '\n'`).
- `RakuAST::Regex::Alternation` → `:rxtype<alt>` (LTM/declarative) vs
  `RakuAST::Regex::SequentialAlternation` → `:rxtype<altseq>` (ordered) — this is the `|` vs `||`
  distinction. The SCRIP frontend currently parses only `|` (→ SPLIT); the two SCRIP engines split on
  it differently (oracle=LTM, walker=ordered), which is exactly the `alt` vs `altseq` semantics, and
  is why `|`-LTM is the Phase-2 parallel-NFA destination while `||`-ordered is the IR_NFA_* walker's.

## SCOPE BOUNDARIES discovered (honest notes for the next session)

- **`||` is not parseable.** `raku_re.c parse_alt` handles only single `|`. `OP_SMATCH` in `raku.y`
  is `~~`, unrelated. So "ordered alt" can only be exercised via the walker's interpretation of `|`.
- **Angle-bracket enum csets `<[...]>` are not supported.** SCRIP uses POSIX-style `[...]` for
  charclass (in real Raku `[...]` is a non-capturing group). A probe with `<[A..Z]>` produces
  `raku_re: compile error: bad named capture <n>` (the `<` is read as a named-capture opener).
- **Overlapping-`|` extent divergence is intentional**, not in scope to "fix" here. Resolving it ⇒
  RK-NFA-4/5 (`|`-LTM on the parallel forward path) or making the frontend distinguish `|`/`||`.

## GATE STATE AT HANDOFF (all green)

```
make scrip                         rc=0
make libscrip_rt                   rc=0
test_smoke_raku.sh         m2 25/25 HARD ✓  | m3 1/20/4  m4 2/19/4 (UNCHANGED — mode-2 gate only)
test_gate_raku_nfa_oracle.sh   RK-NFA-1 (30) + RK-NFA-2 (23 + safe-extent) + RK-NFA-3 (caps) ✓
prove_lower2.sh            67/0 ✓ (UNCHANGED — no lowerer touched)
test_smoke_snobol4.sh      m2 7/7 ✓ (byte-unchanged — NFA isolation intact)
test_smoke_icon.sh         m2 12/12 ✓ (byte-unchanged)
audit_concurrency_invariants.sh   OK — FACT RULES byte-identical ×3, no dup case labels
util_template_purity_audit.sh     2 non-binary side-effects (bb_call_write_slot, bb_every — Icon/SNOBOL, ZERO Raku, pre-existing)
```

## FILES

- `scripts/test_gate_raku_nfa_oracle.sh` — RK-NFA-2 section (cset/anchor + safe-extent batteries) + header
- `test/raku/rk_re38.raku` — RK-NFA-2 cset/anchor edge-case verdict corpus
- `test/raku/rk_re38.expected` — oracle-generated reference (matchers identical)
- `.github/GOAL-RAKU-BB.md` — RK-NFA-2 rung [x], gate-table line, NEXT line, watermark (STATE + entry)

## NEXT

- **RK-HY-4** (de-dup + RT-fix across Raku boxes) + **RK-HY-FENCE** — done-bar `m3/m4 18/22` is
  unreachable until **Icon lands the descr-mode `IR_ASSIGN` ζ-slot store** (the standing BLOCKER:
  the Icon template-revamp deleted `bb_assign.cpp`, leaving descr-mode `IR_ASSIGN` at `unhandled`, so
  `bb_var` bombs on `my $x = …`). Raku m3/m4 recover automatically once Icon lands it.
- Otherwise: `map`/`grep` native (`bb_rk_map.cpp`/`bb_rk_grep.cpp` — inline closure emission, the
  large lift); RK-GRAM-3 (the real BB seam: subrule `<name>` backtracking via the generator PUMP);
  RK-LOWER-5c/5d (try/CATCH/die, class/method).
- RK-NFA-4/5 (mode-3/4 leaf emission) stay SHELVED per the tier-seam decision.
- Still deferred: the lockstep "three → four" FACT-RULE roster expansion across all GOAL files.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
