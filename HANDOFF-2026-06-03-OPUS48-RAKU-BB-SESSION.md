# HANDOFF 2026-06-03 (Opus 4.8) — RAKU-BB SESSION: RK-NFA-2 + epsilon-loop SIGSEGV fix

Session wrap-up. Two landed work items this session, both in the **Raku mode-2 IR_NFA_* regex lane**,
both ISOLATED (Raku-owned files only). Detailed per-item handoffs are committed alongside this one:
- `HANDOFF-2026-06-03-OPUS48-RAKU-BB-RK-NFA-2-CSET-ANCHOR-ALT.md`
- `HANDOFF-2026-06-03-OPUS48-RAKU-BB-NFA-EPS-LOOP-SEGV-FIX.md`

## Landed commits (mine)

- **SCRIP `00ef311`** — RK-NFA-2: L4-L12 cset/anchor/ordered-alt verdict set formalized into
  `scripts/test_gate_raku_nfa_oracle.sh` (23 cset/anchor verdict probes + 8 safe-extent capture probes,
  IR-graph walk == parallel-NFA oracle byte-identical) + durable corpus `test/raku/rk_re38.raku`/`.expected`.
  Gate + corpus ONLY — zero C/lowerer/emitter/template.
- **SCRIP `bedf906`** — fuzz-found epsilon-loop SIGSEGV fix in `src/parser/raku/raku_nfa_bb.c`
  (`nfa_bt_ir_cap`) via a **(node,pos) visited memo** + a 12-probe epsilon-loop TERMINATION battery in the
  same gate. Raku-only C; mode-2 walker only.
- **.github `928502b7`** — GOAL-RAKU-BB.md watermark (RK-NFA-2 entry, RK-NFA hardening entry, STATE
  headline, rung `[x]`, gate-table line, NEXT line) + both detailed handoffs.

> NOTE: origin/main has since advanced past these (peers landed ICN-HY-4 `b48f0cd`, Pascal PB-6b `521726d`,
> a Prolog audit, etc.). My commits are in history; each was rebased onto the latest peer tip and re-gated
> green before push. As of this writing SCRIP origin/main ≈ `4aa19d7f`, .github origin/main ≈ `71547ef8`.

## What RK-NFA-2 established (the semantic seam — carry forward)

The C builder (`raku_re.c`) parses only single `|` → an NFA `SPLIT`. The two mode-2 engines resolve that
SPLIT differently, BY DESIGN:
- **parallel-NFA oracle** (`raku_nfa_exec`, `RK_NFA_BB=0`): leftmost-**LONGEST** = Raku `|` (LTM/declarative).
- **IR-graph backtracking walker** (`raku_nfa_bb.c`, `RK_NFA_BB=1`): leftmost-**FIRST** = Raku `||` (ordered).

VERDICTS always agree (any branch reaching ACCEPT ⇒ matched) — so the verdict batteries span alternation
freely. EXTENT/captures agree ONLY where leftmost-longest == leftmost-first (greedy quantifiers,
disjoint/anchored alternatives). Overlapping-`|` extent (`/(a|ab)/`~"ab" → oracle "ab" vs walker "a")
diverges — that is the Phase-2 `|`-LTM-on-parallel-NFA vs `||`-ordered-on-IR_NFA_* boundary, documented in
the gate. `||` is not yet parseable; angle-bracket enum csets `<[...]>` are unsupported (SCRIP uses POSIX
`[...]` for charclass). Grounded in `rakudo-main/src/Raku/ast/regex.rakumod` (CharClass::{Digit,Word,Space}
`:rxtype<cclass> :negate`; Any `:name<.>` non-newline; `Alternation`=`alt`/LTM vs
`SequentialAlternation`=`altseq`/ordered).

## What the eps-loop fix did

A differential verdict-fuzz (deterministic seeded generator over the supported subset; ~9200 probes)
caught the walker SIGSEGV-ing on 82/100 seeds where the oracle ran clean. Cause: a quantifier over an
empty-matchable subpattern (`(a?)*`, `(a*)*`, `()*`, `(|a)*`, and the same shapes under a backtrack-forcing
suffix like `(a?)*$` on "aab") builds an epsilon loop; the recursive walker overflowed the C stack (the
`depth>100000` guard is too late). Fix mirrors the oracle's per-step `visited[]`: a `(node,pos)` memo
(node id in `IR_t.counter`, an `n*(slen+1)` grid cleared per leftmost-sweep, set-without-restore). Keying
by BOTH node and pos is essential (single per-node stamp gets overwritten across positions during
backtracking — rejected first attempt). Sound for verdict + ordered captures; also bounds work at
`n*(slen+1)` so the ordered walk no longer degrades to exponential backtracking.

## Verified gate state at session end (all green; verified at each push)

```
make scrip / libscrip_rt          rc=0 / rc=0
test_gate_raku_nfa_oracle.sh      RK-NFA-1 (30 verdicts) + RK-NFA-2 (23 cset/anchor + safe-extent)
                                  + epsilon-loop (12) + RK-NFA-3 (captures) — ALL PASS
test_smoke_raku.sh                m2 25/25 HARD ✓ | m3 1/20/4  m4 2/19/4 (UNCHANGED all session)
test_smoke_snobol4.sh             m2 7/7 ✓ (byte-unchanged — NFA isolation proof)
test_smoke_icon.sh                m2 12/12 ✓
prove_lower2.sh                   67/0 ✓
audit_concurrency_invariants.sh   OK — FACT RULES byte-identical ×3
differential fuzz (this session)  ~9200 probes, 0 crashes, 0 divergences
```

Mode-2 is the HARD oracle and is fully healthy. Modes 3/4 EXCISE the NFA path (leaf templates SHELVED per
the tier-seam decision); the Raku m3/m4 numbers are gated behind the Icon `IR_ASSIGN` blocker, not this work.

## Flags for the team (pre-existing, NOT this session — each verified on the pristine tree)

1. **Standalone corpus rot:** `test/raku/rk_re32.raku` (uses `raku_nfa_compile`; aborts
   `[lower2] UNHANDLED role=0 kind=45`) and `rk_re37.raku` (global match/subst) DIFF their `.expected` on a
   pristine build (confirmed by stashing this session's C change + rebuilding). These files are wired to no
   automated runner. `rk_re33/34/35/38` pass.
2. **Shared mode-2 driver ceiling:** any program with **≥32 statements** aborts (rc=134) with the misleading
   `[SBB] FATAL: mode-2 driver: SNOBOL4 main BB graph not found` — a fixed-capacity IR-pool/driver overflow
   hit before the `RK_NFA_BB` branch, identically under both matchers. Fuzzing worked around it at ≤30
   statements/file. Both flags are outside the isolated RK-NFA lane.

## Reusable fuzz harness

`/tmp/rknfa2/gen_fuzz.py` (ephemeral — recreate from the eps-loop handoff): deterministic seeded generator
over the supported regex subset emitting an `if (SUBJ ~~ /PAT/) say('i Y/N')` battery; compare VERDICTS
under `RK_NFA_BB=0` vs `=1`. Keep ≤30 statements/file (driver ceiling). Verdicts always agree across the
`|`/`||` seam, so any rc≠0 or any diff is a real signal.

## NEXT (priority order; unchanged this session)

1. **RK-HY-4** (de-dup + RT-fix across Raku boxes) + **RK-HY-FENCE** — BLOCKED: done-bar `m3/m4 18/22` is
   unreachable until **Icon lands the descr-mode `IR_ASSIGN` ζ-slot store** (the standing cross-language
   blocker; `bb_var` bombs on `my $x = …` because the Icon template-revamp left descr-mode `IR_ASSIGN`
   `unhandled`). Raku m3/m4 recover automatically once Icon lands it. NOTE: peer ICN-HY-4 `b48f0cd` (native
   to/to_by generators) landed this session — worth re-checking whether it moved the `IR_ASSIGN` needle.
2. `map`/`grep` native (`bb_rk_map.cpp`/`bb_rk_grep.cpp`) — inline closure emission, the large lift.
3. **RK-GRAM-3** — the real BB grammar seam: subrule `<name>` backtracking via the generator PUMP.
4. RK-LOWER-5c/5d — try/CATCH/die, class/method (shared-lowerer / FACT-sensitive; tread carefully).
5. RK-NFA-4/5 (mode-3/4 leaf emission) stay SHELVED. Optional: a capture-EXTENT fuzz inside the
   leftmost-longest==leftmost-first envelope; re-fuzz once the 32-statement driver ceiling is lifted.
6. Still deferred: the lockstep "three → four" FACT-RULE roster expansion across all GOAL files.

## Constraints honored all session (keep honoring)

ISOLATION (`raku_nfa_bb.c` is Raku-only; SNOBOL4/Icon/Prolog pattern paths untouched — IR_NFA_* family
isolated by design; edit only `bb_rk_*` boxes / the Raku `TT_SMATCH` arm / the Raku gate+corpus). No value
stack, no `bb_bin_t`, no C byrd-box `(ζ,int entry)` functions — none touched. Mode-2 only (the HARD oracle);
default `~~` runs on the C matcher; m3/m4 EXCISE the NFA path. FACT RULE blocks never edited (concurrency
audit byte-identical ×3). Always `git pull --rebase` + rebuild + re-gate before each push (peers push
concurrently). Authors line on every commit/handoff.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
