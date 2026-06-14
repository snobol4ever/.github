# HANDOFF 2026-06-14 — Opus 4.8 — GOAL-BB-FIXUP-Z-to-A — RESOLVER FAMILY DELETED

**Session:** lap 1, 12th session. Opened at cursor `bb_resolve.cpp` (HELD since the 6th session).
**Result:** the entire `bb_resolve` resolver subsystem (12 files) was found DEAD at HEAD and DELETED.
**SCRIP:** pushed `20e8844` (rebased over concurrent `0494c45`). **.github:** this commit.
**Cursor:** ADVANCED `bb_resolve.cpp` → `bb_query_frame.cpp`.

---

## What happened (one paragraph)

The 11th session's "NEXT" was `bb_is_cmp`, with a recipe whose mandated first step is "fire-probe to
establish dead vs live." The probe overturned the premise. Since the 11th session (`62ab2d2`→`89fc357`,
9 commits) the **PL-GZ GUT** (`9480185`, 2026-06-13) had made the GZ cell path the *only* Prolog backend
(flat + rich/heap-env tiers deleted). Combined with the now-complete `IR_DET_*` family, every Prolog
builtin either GZ-admits → `IR_DET_*` (→ `bb_det_*`, never the resolver) or GZ-declines → **PL-GZ FENCE**
rejection (never reaches emit). There is no third path. The whole `bb_resolve`/`bdisp` chain is therefore
unreachable. Rather than do the timid sub-handler conversion of `bb_is_cmp`, this session executed the
endgame the 11th watermark itself named ("bb_resolve should DISSOLVE … the actual objective"), whose
stated precondition — `IR_DET_*` coverage total-or-reject — the GUT had just satisfied: **delete it.**

## The finding (resolver is dead at HEAD)

Instrumented `bdisp` (the resolver dispatcher) and threw a battery at every builtin it handles — `is`,
arith-cmp (`< > >= =< =:= =\=`), term-cmp (`== \== @< @> @=< @>=`), `findall`, `atom_string`,
`functor`/`arg`/`=..`, type-tests, `succ`/`plus`, `atomic_list_concat`/`concat_atom`, `sort`/`msort`,
`format`, `retract` — across m2/m3/m4. **Zero resolver fires.**

This **overturns the 11th-session "bb_list is LIVE" finding.** It is reconciled, not contradicted: that
session's A/B was at baseline `95bc33f` and was correct *then*; the interim commits progressively shadowed
bb_list's last live paths (`atomic_list_concat`→`IR_DET_ATOM_OP` at `scrip.c:1632`; `sort`/`msort`→
`IR_DET_SORT`). The finding was **overtaken by drift.** `IR_BUILTIN` is created only in `lower_prolog.c`
(a Prolog-only opcode — no other frontend emits it), and `IR_BUILTIN → bb_resolve` (`emit_core.c:524`) was
its lone emit-time consumer.

## Changeset (SCRIP `20e8844`)

Deleted (12): `bb_resolve.cpp` + `bb_io`, `bb_is_cmp`, `bb_type_test`, `bb_term_inspect`,
`bb_aggregate_nb`, `bb_atom_string`, `bb_term_io`, `bb_findall`, `bb_succ_plus`, `bb_list`,
`bb_retract_throw`.
Modified (4): `Makefile` (−24 lines: source list + per-file compile rules), `bb_common.h` (−11 decls),
`bb_templates.h` (−1 decl: `bb_resolve`), `emit_core.c` (IR_BUILTIN dispatch → loud abort).

The dispatch is now **safer** than before: a surviving `IR_BUILTIN` aborts loudly
(`IR_BUILTIN '%s' survived GZ-ONLY lowering (unreachable)`) instead of silently emitting the dead
resolver's possibly-divergent bytes. If a future `pl_gz_admit`/lowering gap ever lets an `IR_BUILTIN`
through, it surfaces immediately.

## Safety verification (airtight — abort-as-detector)

An abort under the deletion build fires *precisely* when an `IR_BUILTIN` would have reached `bb_resolve`
at baseline. So **0 aborts across a wide battery = the resolver is provably unreachable.**

- **Phase 1** (abort wired, files still present): corpus + battery m2/m3/m4 → 0 aborts. A/B vs pristine
  baseline `89fc357` (git-stash): m2/m3 **byte-identical**; m4 ASM identical after `bbN`-label
  normalization (cosmetic pointer-derived label renumber from the changed binary layout — the same
  phenomenon the 11th session documented for bb_list); compiled+linked m4 binaries **identical output**.
- **Phase 2** (deletion): rebuild clean — no dangling symbols (the build is the oracle). A/B re-run →
  0 m2/m3 diffs, 0 m4-normalized diffs, 0 aborts. Then a **38-shape battery of the exact 11th-session
  documented firing cases** (sort with bound/non-LOGICVAR result, alc all arities + split mode, compound
  arith-cmp operands, floaty/unary `is`, exotic `functor`/`arg`/`=..`) × compile+run → **0 aborts.**
- **Rebase:** absorbed concurrent `0494c45` (PL-BB-1a, `emit_bb.c` backtrack collapse) — clean rebase,
  rebuilt, re-ran the 38-shape battery on the combined tree → **0 aborts**; xchecks still green.

## Gates (green vs baseline)

prolog xcheck 4/0 · icon xcheck 4/0 HARD + m4 4/4 · no_value_stack PASS · no_new_global PASS (17/17
floor) · no_bb_bin_t 0 · no_vstack 3 floor · coupling PASS · **no_handencoded_bytes: raw-byte lines
(`bytes(`/`u32le`/`u64le`/`u8(`) across the WHOLE `BB_templates/` dir → 0** (bb_is_cmp alone carried 33).

## Pre-existing reds (NOT mine — verified identical on `/tmp/scrip.base`)

- **GZ gates `gz2`–`gz7` FAIL** — they expect the pre-GUT `INTERP-FALLBACK` banner that the PL-GZ GUT
  replaced with PL-GZ FENCE rejection. They are **stale**, red on HEAD independent of this work
  (confirmed by running them against the pristine baseline binary). **Retarget candidate** (see below).
- rebus hello row-drift; `bb_call_write_slot.cpp` fprintf purity rc=1.

## Follow-ups for Lon

1. **Retarget the 9 stale GZ gates** (`gz2`–`gz7`): they should grep for the PL-GZ FENCE message, not
   `INTERP-FALLBACK`. They predate the GUT and have nothing to do with this deletion.
2. **Dead IR_BUILTIN emit infrastructure** now also unreachable: `emit_bb.c` `bb_prepare` IR_BUILTIN block
   (~`:1148`), `emit_term_build.cpp:130`, `emit_bb.c:2611` FILL case. Left in place (harmless; the
   `bb_prepare` IR_BUILTIN block may share structure with live paths — not chased). Candidate cleanup.
3. The `bb_det_*` ∥ resolver-sub-handler **duplication** the prior handoffs tracked is now **resolved by
   deletion** — `bb_det_*` is the sole survivor.

## Resume (next session, cold start)

The resolver family is GONE; there is **no held cursor anymore** — this is now an ordinary Z→A sweep.

1. `cursor=$(grep -m1 '^# CURSOR:' .github/BB-REVAMP-TRACKER.md | awk '{print $NF}')` → `bb_query_frame.cpp`.
2. `bb_query_frame.cpp` is dirty (2 violations) → **work it** (it is the cursor and non-CLEAN).
3. Then continue to the first dirty file sorting strictly before `bb_query_frame` (Z→A), per the rank.

ENV: `bash scripts/install_system_packages.sh` (needs libgc-dev + libgmp-dev), then `make -j4 scrip` and
`make libscrip_rt`. Source tree is CLEAN and matches pushed SCRIP `20e8844`.
