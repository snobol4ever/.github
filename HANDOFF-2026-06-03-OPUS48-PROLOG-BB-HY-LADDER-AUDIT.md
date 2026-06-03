# HANDOFF 2026-06-03 (Opus 4.8) — Prolog BB-HYGIENE ladder AUDIT: 1c vacuous, 2/3/4 subsumed, 5 complete, FENCE unwritten

## TL;DR

Investigation session. **No SCRIP / corpus code touched.** SCRIP HEAD unchanged at
`3610475`. Goal was the nominal next ladder step **PL-HY-1c (de-fuse)**; the finding is that
PL-HY-1c is **vacuous** in the current Prolog path and that **PL-HY-2/3/4 are already subsumed**
by the completed `x86()` template revamp (PL-RV-1..6) — the ladder's watermark sizes were stale
(pre-revamp, ~2× the real line counts). Only `.github` changed (this handoff + the GOAL ladder
annotations). All gates re-verified green.

## Gate state (re-verified this session — unchanged baseline, no code touched)

- GATE-1 smoke: **m2 5/5**, m3 4/5 (the one m3 `unify` FAIL is the known smoke-harness artifact,
  covered by the rung suite), m4 5/5.
- GATE-3 rung suite: **m2 111/111 · m3 111/111** byte-identical · **m4 75 / 0 FAIL / 36 EXCISED**.
- FACT greps: `seg_byte(SEG_CODE`/`SL_B(` outside templates **0**; `g_vstack` **0**.

## Findings (evidence)

### PL-HY-1c (DE-FUSE) — VACUOUS in the current Prolog path
The de-fuse criterion is "an arm reading `pBB->α->ival/sval` for an operand **whose own box fills a
slot**." Proven that no such site exists in Prolog today:
- **No Prolog-owned template calls `bb_slot_alloc`/`bb_slot_alloc16`.** (The slot allocators are
  used only by SNOBOL4/Icon/Raku paths: `bb_call*`, `bb_call_proc_staged`, `bb_gather`, `bb_pat_arb`.)
- **`emit_bb.c` gives the Prolog operand/builtin kinds a `FILL`-only dispatch** (lines ~1525–1528:
  `IR_ARITH`, `IR_BUILTIN`, `IR_ATOM` → `FILL(nd, …)` with no slot). `IR_LIT_I`/`IR_LIT_S` slot-alloc
  only under `g_descr_flat_chain` (the SNOBOL4 chain); there is no `g_pl_flat_chain`.
- **The three Prolog operand boxes are pure pass-throughs** (α→γ, β→ω) and write **0** frame slots:
  `bb_atom.cpp`, `bb_logicvar.cpp`, `bb_arith.cpp` (grep for `x86_frame_store`/`[r12+` = 0 each).
- 136 operand-scalar reads (`a0->ival`/`a0->sval`/etc.) exist across the Prolog templates, but each
  is the **only** place that value lives — there is no producer slot to route through. The Prolog
  builtins correctly pass `(kind, ival, sval)` triples to `rt_*` (that IS the Prolog ABI, distinct
  from the SNOBOL4/Icon DESCR-slot model).

**Conclusion:** PL-HY-1c cannot be performed until a `g_pl_flat_chain` + slot-filling operand boxes
exist — a LOWERER prereq (the GOAL's own DUP-FORM-3 note flags this). That is a DESIGN step (touches
the shared `lower.c` under the SHARED-LOWERER concurrency rule, mutates the proven-green
`bb_atom`/`bb_logicvar`, and would change the builtin call convention) — **needs Lon's sign-off; not
a mechanical 1c task.**

### PL-HY-2/3/4 (DE-CRAM) — SUBSUMED by the x86() revamp; watermark sizes stale
Actual `wc -l` vs the ladder's claimed sizes:

| File | Watermark | Actual | Structure |
|---|---|---|---|
| `bb_choice.cpp` | 318 | **163** | ONE CP state machine; clause variation = loop over `n`; shared CP record / cut save-restore / dispatch / epilogue. "first/next-clause" = `pre[0]` vs `pre[i>0]` arms in one flow. "CP-elision" shape ABSENT (that's WAM-CP-12). |
| `bb_goal.cpp` | 264 | **134** | one `bb_goal_str` + `build_arg` helper; single call shape. |
| `bb_unify.cpp` | 151 | **76** | inline `u_*` guards: vacuous / deferred-bomb (compound/float = PL-HY-1a deferral) / self-unify `x=x` (= WAM-CP-7 var-var, already present) / var-const. |

Each is a **single coherent box**, not N crammed shapes. A router-split would **over-split** —
forbidden by the NO-DUP rule ("grouping near-identical shapes is correct; splitting them is
over-splitting"). The "split + router" instruction was written against the pre-revamp sizes.

### PL-HY-5 (DE-DUP + RT-FIX) — EFFECTIVELY COMPLETE
- **Zero duplicated-algorithm TEXT/BINARY pairs remain.** The only `_bin` symbol is
  `emit_term_from_node_bin` (the 3-line marshal+call helper PL-HY-1a introduced to REPLACE the
  deleted `_bin` walker — not itself a walker).
- **All 11 `bb_builtin_*` family files have 0 emit-time value-work loops** — every arm is
  "marshal args → `call rt_*` → wire 4 ports," the sanctioned RT split.
- The one recursive walker `emit_build_compound_term` is the **mode-4 serialized encoder** PL-HY-1a
  deliberately kept (an in-process `&node` baked into a separately-linked binary would dangle); its
  mode-3 twin is the single `rt_node_to_term_ptr` call. PL-HY-1a's verdict (NOT a dup) stands.

### PL-HY-FENCE — gate script not yet authored; the property already holds
`scripts/test_gate_bb_one_box.sh` does not exist. The one-box property it would enforce already
holds: no Prolog-owned file has >1 `extern "C" void bb_*(…)` box entry (`bb_builtin_*` are `_str`
helpers behind the `bb_builtin.cpp` router; `bb_unify`/`bb_cut`/`bb_disj`/`bb_conj`/`bb_ite`/
`bb_catch`/`bb_arith` each have one box under the `(void)` signature reading emit-time globals).

## What changed on disk (this session)

- `.github/GOAL-PROLOG-BB.md` — annotated the PL-HY ladder (1c..FENCE) with the findings above and
  updated the gate-table caption watermark (HEAD `3610475`, no code touched). **FACT-RULE blocks
  untouched** — verified byte-identical to GOAL-SNOBOL4-BB / GOAL-ICON-BB (NO-VALUE-STACK block md5
  `e13a8ad954b24f6d14a5ba7383d76089` matches across all three). Steps left as `- [ ]` (NOT
  checkmarked) because the work described was found unnecessary/blocked, not performed by me —
  awaiting Lon's call to reclassify `[x]` vs delete.
- `.github/HANDOFF-2026-06-03-OPUS48-PROLOG-BB-HY-LADDER-AUDIT.md` — this file.
- **corpus**: the gate runs regenerated all 111 Prolog `.s` artifacts (the current emitter at HEAD
  `3610475` produces leaner output than the committed `.s`, which were generated at an earlier HEAD).
  **Reverted** — that drift belongs to whoever lands the emitter change that caused it, with their
  own verification; folding it into a Prolog-audit handoff would be cross-session contamination.

## NEXT — the two real pieces of forward work (both need a decision)

1. **Author `scripts/test_gate_bb_one_box.sh`** (PL-HY-FENCE). Small, safe gate: assert exactly one
   `extern "C" void bb_*` entry per Prolog-owned template file (helper `_str` files exempt). Would
   pass immediately. Lowest-risk; can land in one rung.
2. **Design the `g_pl_flat_chain` lowerer prereq** that makes PL-HY-1c real: allocate frame slots for
   Prolog operand nodes (IR_ATOM/IR_LOGICVAR/IR_LIT in arg position), convert `bb_atom`/`bb_logicvar`
   to slot-filling producers, then switch builtin arms from `(k,i,s)` triples to slot reads. Touches
   shared `lower.c` (concurrency-sensitive) + risks GATE-3 111/111 byte-identity → **needs Lon's
   design sign-off before any code.**

Recommend also reclassifying PL-HY-2/3/4 (`[x]` SUBSUMED) and PL-HY-5 (`[x]`) once Lon confirms the
audit, leaving PL-HY-1c (blocked) and PL-HY-FENCE (write the gate) as the live ladder.

## Build / verify recipe
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh            # GATE-1 m2 5/5
bash scripts/test_prolog_rung_suite.sh       # GATE-3 m2 111/111, m3 111/111, m4 75/0/36
# the suite regenerates corpus/programs/prolog/*.s — `git checkout -- programs/prolog/*.s` to re-clean
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include='*.c' --include='*.cpp' | grep -v _templates/ | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l             # 0
```
Authors: LCherryholmes · Claude Opus 4.8
