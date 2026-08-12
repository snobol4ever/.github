# FINDING-2026-08-12p — HOME-RBX X-3: `op_subj_cell` is a SECOND FORTH-only consumer gate, same bug class as s40b's `x86_fc_on`/`x86_fc_hit`, different site — traced per the s41b LIVE CURSOR instruction, not guessed.

**Session:** Claude Sonnet 5, orientation + first rung on GOAL-SN4-HOME-RBX.md.
**Scope:** followed s41b's exact next-rung instruction — pick a small newly-broken witness, re-apply s40b's gate-widen LOCALLY (uncommitted), trace `op_fc_base`/`op_fc_bytes` HEAP-vs-FORTH, and answer the open question: does `op_fc_base` compute identically for HEAP and FORTH, or does something upstream diverge?

## What was done

1. Cloned `.github`/`corpus`/`SCRIP`/`x64` fresh, ran `install_system_packages.sh` (gdb 15.1 confirmed live), built `scrip` clean at HEAD `a037b637`.
2. Picked `038_pat_literal.sno` and `039_pat_any.sno` from `crosscheck/patterns` — both single-primitive subject-position pattern matches (`X 'hello'` / `X ANY('aeiou') . V`), exactly the "smallest/simplest first" candidates the cursor named.
3. Re-applied s40b's `73c1ac33` diff to `x86_fc_on()`/`x86_fc_hit()` LOCALLY (uncommitted, 2-line change, reverted at the end of this session — nothing committed to the gate).
4. Sanity check: rebuilt, re-ran the two ORIGINAL s40b witnesses (`041_pat_span`, `158_pat_cap_arbno_each_iter`) under `--zeta-port=heap` — reproduced their documented DIFFs exactly (`'no digits'` vs `'12345'`; empty vs `a/b/c`), confirming the local re-application is faithful.
5. Ran 038/039 under HEAP with the widened gate: both DIFF (`no match`/`no vowel` vs `matched`/`e`). Two new small, clean two-sided witnesses for this defect class.
6. `SCRIP_RBX_FIELD_TRACE=1` on 038, FORTH vs HEAP, both md5-stable across repeats (deterministic, compile-time, not ASLR/env noise). **The dispatch walk is the same length in both ports (22 `X86H_DEF/ALPHA` lines)** but the *grant shape* differs: FORTH shows four boxes carve-only-granted (`fc_bytes=16, fc_base=-1`); HEAP shows only ONE of those four granted, and it comes back WINDOWED (`fc_bytes=16, fc_base=128`) rather than carve-only.

## Root cause: traced, not inferred

Checked the two obvious suspects for the divergence and **ruled both out by reading the code**:

- **`fc_geom()` (zeta_storage.c:742)** — the K/byte-count decision for MATCH_ARB/SPAN/TAB/RTAB/BREAK/BREAKX/BAL/REM etc. — is provably port-blind. Its only port read is `fc_cells_on()` (zeta_storage.c:268), which explicitly says `m == ZC_PORT_FORTH || m == ZC_PORT_HEAP`. K is always 16 for these kinds regardless of port. §A's "K is the SAME static-K grant, flavor selected at the port layer" claim is TRUE for this function.
- **`zls_build()` (zeta_storage.c:430)** — the plan-side slot-table/base-offset builder — has NO direct port-mode read anywhere in its body (grepped the full function). The SUBJECT-CELL registration block inside it (line ~457) gates on `SCRIP_SUBJ_CELL`/`SCRIP_SUBJ_DYN` env killswitches only, not port.

**The actual divergence is at `src/emitter/emit.cpp:1358`, the `IR_MATCH_BEGIN` case:**

```c
{ extern int fc_vread_fp(const IR_t *); g_emit.op_subj_cell = (x86_zc_frame() == ZC_FRAME_RSP && x86_port_mode() == ZC_PORT_FORTH && subj && fc_vread_fp(nd) >= 0) ? 1 : 0; }
```

`op_subj_cell` is hard-gated to **`ZC_PORT_FORTH` alone** — not `fc_cells_on()`'s FORTH-or-HEAP class. This is the READ-side twin of exactly the bug s40b fixed for `x86_fc_on`/`x86_fc_hit`, at a different site: the SUBJECT-CELL PRODUCER registration in `zls_build` (proven port-blind above) carves the subject literal's cell under HEAP exactly as it would under FORTH — but `IR_MATCH_BEGIN`'s own consumer flag stays FORTH-only, so the head does not know its subject was delivered on the cell.

**Confirmed downstream in the template**, `src/templates/bb_match_begin.cpp`:
- Line 40: `IF(_.op_sa >= 0 && !subjc(), x86("mov", FRQ(_.op_sa), "rdi") + x86("mov", FRQ(_.op_sa+8), "rsi"))` — when `subjc()` is false, the head reads the subject from the FLAT planned slot `FRQ(_.op_sa)`.
- Line 42: `IF(!_.op_zres && subjc(), x86("mov", "rdi", "qword ptr [rsp + 0]") ...)` — when `subjc()` is true, the head pops the subject from TOS instead.

Under HEAP: the producer (armed by `zls_build`, port-blind) pushes the subject DESCR onto the rsp cell at TOS. The consumer (`op_subj_cell` forced to 0 because port ≠ FORTH) reads the OLD flat slot instead — stale/wrong data, exactly reproducing `X 'hello'` failing to match and `ANY('aeiou')` failing to find a vowel that is plainly in `'hello'`.

This is comment-confirmed as deliberate original design, not an oversight nobody considered: `bb_match_begin.cpp`'s own comment on line 41 (the code path taken when `!subjc()`) says *"GATED !subjc(): on subject-cell-granted graphs the OFF world popped and never wrote op_sa — the slot belongs to another node's layout there, and writing it clobbers live state."* I.e. the two arms are known to be mutually exclusive and mutually incompatible — this is precisely the producer/consumer desync class s40b's commit message names for `x86_fc_hit`, occurring a second time at a structurally identical seam the s40b patch did not touch.

## What this means for X-3

**Answers the s41b open question directly:** `op_fc_base` itself is NOT the site of divergence (fc_geom is fine); the divergence is a *second, independent* FORTH-only consumer gate the s40b patch didn't cover. §A's "K is the same static-K grant" claim survives; the "flavor selected at the port layer" half does NOT survive uniformly — some consumers (`x86_fc_on`/`x86_fc_hit`, now s40b-widened) do select by the FORTH-or-HEAP class; others (`op_subj_cell`, still FORTH-only) do not, and the mismatch is silent (no bomb, no crash — a plausible wrong answer, the exact class HAZARD/CONTRACT-A's own corrected §A already names as the standing lesson of this file).

**This is very likely not the only such site.** `op_subj_cell` was found by chasing ONE trace divergence on ONE witness; a full census of every `x86_port_mode() == ZC_PORT_FORTH` (as opposed to `fc_cells_on()`-style FORTH-or-HEAP) comparison in `emit.cpp` and `x86_asm.h` would enumerate the rest. Candidates spotted in the same grep pass (NOT individually verified as bugs — flagged for the next trace, in case any are load-bearing for the patterns corpus):
- `emit.cpp:1190` `fc_alt_active` — `x86_port_mode() == ZC_PORT_FORTH`
- `emit.cpp:1193` `fc_seq_on` — `x86_port_mode() == ZC_PORT_FORTH`
- `emit.cpp:1487` POS/RPOS CONST-WPOP arm — `ZC_PORT_FORTH` only
- `emit.cpp:2053`, `emit.cpp:2639` — bare `x86_port_mode() != ZC_PORT_FORTH` / `== ZC_PORT_FORTH` guards
- `zeta_storage.c` (various `fc_*_active` predicates) — not individually checked this session

**RECOMMENDATION (not executed — matches the cursor's "do not re-widen the committed gate yet" instruction):** before re-attempting X-3's read-side widen, census EVERY `ZC_PORT_FORTH`-only comparison downstream of a `fc_cells_on()`-gated producer (grep `== ZC_PORT_FORTH` in emit.cpp + x86_asm.h, cross-reference each against whether its paired producer used `fc_cells_on()` or a bare FORTH check), fix the whole class in one pass, THEN re-run the BY-SET sweep. Fixing `op_subj_cell` alone and re-measuring would very plausibly repeat s41's own lesson: one seam closed, others still open, net-regressive again, wrong conclusion drawn about which mechanism is broken.

## ⛔ UPDATE (same session, before push): DEEPER ROOT CAUSE FOUND — `op_subj_cell` IS A SYMPTOM, NOT THE ROOT

Followed my own "census the whole class first" recommendation above before stopping. Walked every bare `x86_port_mode() == /!= ZC_PORT_FORTH` comparison in `emit.cpp`/`x86_asm.h` (7 live sites, excluding the two already-widened-then-reverted `x86_fc_on`/`x86_fc_hit` lines and comments) and traced each to its producer:

| site | producer gated how | verdict |
|---|---|---|
| `fc_alt_active` (emit.cpp:1190) | `fc_alt_register` called unconditionally from LOWER (`lower_snobol4.c:1677`), **no port check at all** | MISMATCH — same class as `op_subj_cell`, not yet measured for live impact |
| `fc_seq_on` (emit.cpp:1193) | `fc_seq_active` is `return 0` unconditionally (SEQ-ERAD SE-5/SE-6, dead code) | NOT A BUG — permanently inert regardless of port |
| POS/RPOS CONST-WPOP (emit.cpp:1487) | gated on `g_zd_arm`, which is downstream of `zd_plan` (see below) | SYMPTOM of the same root as `op_subj_cell` |
| `emit.cpp:2053` — **`zd_plan`'s own top-level entry gate** | `if (!_zd \|\| x86_port_mode() != ZC_PORT_FORTH \|\| n <= 0) return;` — **no `fc_cells_on()`, bare FORTH-only, and this is the call graph's own root** | **THE ROOT.** `zd_plan` is called unconditionally once per chain (`emit.cpp:2319`, no port guard at the call site) and self-declines internally the instant port ≠ FORTH, leaving `zon[]`/`zout[]`/`zgpop[]`/`zwpop[]` all-zero (the function's own comment: *"leaving zon all-zero"*). |
| `emit.cpp:2639` | consumes `x86_zc_frame()==ZC_FRAME_RSP && port==FORTH` together — needs a separate check, not yet traced | UNTRACED |

**`zd_plan`'s output (`zon[]`/`zgpop[]`/`zwpop[]`) is what sets `g_zd_stage`/`g_zd_arm` at the per-node choke** (`emit.cpp:2695`: `if (zd_on[i] || zd_gp[i] > 0 || zd_wp[i] > 0) { g_zd_stage = 1; g_zd_arm = ...}`). Since `zd_plan` self-declines whole-graph under HEAP, **`g_zd_stage`/`g_zd_arm` are 0 for every node in every graph compiled under HEAP, unconditionally, before any per-node kind-specific logic runs.** That in turn means the entire staging block at `emit.cpp:876-878` (`op_zres`, `op_fc_bytes = g_zd_k`, `op_zdepth`, `op_zread[]`, `op_ztail`, `op_zpat`, `op_zfc`, `op_zgpop`, `op_wpop` accumulation) never fires under HEAP — the ZD-armed value spine that carries the subject/binop/call-result value-spine cells (§ZB-VAL-0/2/3/4/5/6, the whole `zls_build` value-spine registration this session already confirmed is `fc_cells_on()`-blind at the PLANNING side) is **silently unstaged at the EMIT side**, whole-graph, under HEAP.

`op_subj_cell` is real and independently mis-gated (confirmed above, its OWN comparison is bare-FORTH, not routed through `zd_plan`) — but it is a second, smaller instance of the identical disease sitting downstream of a much larger gate that blocks the entire ZD spine outright. **Fixing `op_subj_cell` alone, or `x86_fc_on`/`x86_fc_hit` alone (s40b's actual attempted fix), cannot succeed while `zd_plan` itself still self-declines under HEAP** — s40b's whole slice-2 attempt was necessarily working against a graph where `g_zd_stage`/`g_zd_arm` were already always false, which is likely why the "correctly-carved-but-differently-addressed" framing in the s41b cursor didn't fully explain the DIFFs: the cells being read were never ZD-staged to begin with under HEAP, independent of the `x86_fc_hit` regime-selection question.

**REVISED RECOMMENDATION:** the very first move for X-3 slice-2, before touching `op_subj_cell` or re-widening `x86_fc_on`/`x86_fc_hit`, is **widening `zd_plan`'s own top-level gate** (`emit.cpp:2053`) from bare `x86_port_mode() != ZC_PORT_FORTH` to the `fc_cells_on()` FORTH-or-HEAP class, matching every other producer-side gate already confirmed port-blind this session (`fc_geom`, `zls_build`, the SUBJECT-CELL registrar). This is the ONE authority the whole ZD spine depends on; every other mismatch found (`op_subj_cell`, POS/RPOS CONST-WPOP) is either downstream of it or moot until it is widened. Do this FIRST, alone, remeasure BY SET — it may already resolve `op_subj_cell`'s symptom for free (since ZD-arming may take over the subject delivery path entirely for many nodes), or it may surface a cleaner, smaller residual to fix next. Either way, widening the leaf gates before the root gate (what `op_subj_cell` alone would have been) risks measuring noise from a spine that is still globally unstaged underneath.

**`emit.cpp:2639` remains untraced** — flagged for whoever picks this up next, not blocking, since it's a single site and the `zd_plan` gate is clearly the dominant one.

**Still zero compiler bytes changed this session** — this is a widened trace, not a patch; the recommendation above is for next-rung execution, not something I ran.

## ⛔ THIRD UPDATE (same session): MEASURED THE `zd_plan` WIDEN — REAL SIGNAL, NOT A CLEAN WIN

Executed the revised recommendation above: widened `zd_plan`'s own gate ALONE (`emit.cpp:2053`, bare `x86_port_mode() != ZC_PORT_FORTH` → inlined FORTH-or-HEAP check; `fc_cells_on()` itself is `static` to `zeta_storage.c`, not externally linkable, so the equivalent two-port check was inlined directly rather than exposing a new symbol — smallest possible diff, 1 line changed). Left `x86_fc_on`/`x86_fc_hit`/`op_subj_cell` completely untouched at HEAD's FORTH-only state.

**Byte-identity on FORTH confirmed first:** `scrip -x86` on `beauty.sno` before/after the edit, diffed — **zero lines differ**. The widen is inert on the compiled default, exactly as the gate's own logic guarantees (it only changes behavior when port ≠ FORTH).

**038/039 (this session's two witnesses) both PASS under HEAP with ONLY this one-line change** — no `op_subj_cell` fix needed for these two. That is itself informative: for at least these two witnesses, ZD-arming the value spine correctly is sufficient to route the subject delivery path around whatever `op_subj_cell`'s FORTH-only gate would have broken — i.e. `op_subj_cell`'s bug may be *masked* rather than *fixed* whenever `zd_plan` succeeds in arming the same node some other way. Not verified generally, but the two-witness result is consistent with that reading.

**Full `crosscheck/patterns` BY-SET sweep, `board_patterns_set.sh`, own-HEAD floor re-measured fresh this session (36/122, exactly matching s37/s41b's recorded number — confirmed by direct re-run, not transcribed) vs the `zd_plan`-widened tree:**

```
[floor_36_heap]        PASS 36 / 122  (47 DIFF, 22 SIG11, 15 HANG, 2 SIG6)
[zdplan_widen_heap]    PASS 42 / 122  (44 SIG11, 19 DIFF, 9 SIG6, 7 rc1, 1 HANG)

REPAIRED (14): 052_pat_arbno, 054_pat_arbno_alt, 056_pat_star_deref, 059_pat_fence_fn_basic,
  062_pat_fence_fn_outer, 069_pat_fence_fn_full_match, 100_pat_fence_two_alts_first,
  101_pat_fence_falls_through, 103_pat_fence_in_concat, 133_pat_fence_eps_recur_deep,
  134_pat_fence_eps_recur_stress, 158_pat_cap_arbno_each_iter, 162_pat_arbno_null_body_guard,
  163_pat_arbno_inner_alt_trace

BROKEN (8): 055_pat_concat_seq, 068_pat_fence_fn_via_var, 109_pat_fence_via_var_seal_blocks_retry,
  113_pat_fence_via_var_two_with_seal_retry, 117_pat_arbno_of_star_var_fence,
  143_pat_regex_quantified_class, 156_pat_cap_alt_abandon_pop, 172_pat_fail_forces_retry
  (5 SIG11, 3 DIFF)
```

**Net +6 (36→42), but this is NOT a clean win by the s41b PLAN SCRUTINY's own proposed bar ("zero new BROKEN by set").** 8 programs that passed at the floor now fail — a real regression set, not noise (HANG dropped 15→1, SIG6 appeared 0→9, rc1 appeared 0→7 — the failure-mode shape changed substantially, consistent with a large mechanism actually turning on rather than a narrow patch). `143_pat_regex_quantified_class` in the BROKEN set is notable: it's independently named in `zc_nofc()`'s own comment (zeta_storage.c:740) as one of the two programs whose fix/break history is already tangled with a DIFFERENT killswitch (`SCRIP_NOFC`) — worth checking whether this BREAK is the same underlying interaction resurfacing, not a fresh defect, before assigning it as new debt.

**THIS EDIT IS NOT COMMITTED.** Reverted (`git checkout`, plus a stray `git stash` from an earlier byte-identity check, dropped after confirming its content matched what's documented here) — HEAD is `a037b637`, tree clean, rebuilt and confirmed. This is a measurement for the next rung to build on, not a landed fix. The 8-program BROKEN set needs its own bisect before this can go in; per RULES.md MONITOR-FIRST, that means the 2-way sync-step monitor on the smallest BROKEN witness (`055_pat_concat_seq` looks like the simplest name), not guessing from the mechanism description above.

**REVISED STATE OF PLAY FOR THE NEXT RUNG:** the `zd_plan` gate widen is real, load-bearing, and larger in effect than `op_subj_cell` alone (which was never independently tested in isolation this session — the `zd_plan` widen was tried first per the corrected recommendation, and it already moved the floor before `op_subj_cell` needed touching). The next rung is not "widen `op_subj_cell` too" — it is **bisect the 8-program BROKEN set** the `zd_plan` widen introduces, on the theory that arming a previously-dormant staging path surfaces a second latent defect it was accidentally masking (the standard shape this file's own HAZARD/PLAN SCRUTINY sections describe repeatedly: an armed path exposes a bug an unarmed path never reached). `op_subj_cell` remains a confirmed, real, independent mis-gate — but whether it needs fixing at all depends on whether the `zd_plan` widen alone, once its 8-program regression is resolved, already routes around it for every remaining case, the way it did for 038/039.

## State of the tree at end of session

**ZERO compiler bytes changed.** All local edits (the `x86_fc_on`/`x86_fc_hit` re-application used to reproduce the DIFF class, and the `zd_plan` gate widen used for the measurement above) were reverted before this write-up; `git diff --stat` on SCRIP is clean, HEAD unchanged at `a037b637`, rebuilt and confirmed working. No rebuild artifacts committed. This finding is a trace + measurement result, not a patch.

## Watermark
SCRIP HEAD `a037b637` (unchanged — no code committed this session). Trace commands: `SCRIP_RBX_FIELD_TRACE=1 scrip --zeta-port={forth,heap} --run corpus/crosscheck/patterns/038_pat_literal.sno`, reproduced twice (md5-identical) each port.
