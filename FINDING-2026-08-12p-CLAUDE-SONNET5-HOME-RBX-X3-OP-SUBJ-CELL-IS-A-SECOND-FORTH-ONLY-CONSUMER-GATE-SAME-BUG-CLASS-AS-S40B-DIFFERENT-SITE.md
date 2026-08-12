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

## State of the tree at end of session

**ZERO compiler bytes changed.** The local `x86_fc_on`/`x86_fc_hit` re-application was reverted (`git checkout -- src/templates/x86_asm.h`) before this write-up; `git diff --stat` on SCRIP is clean, HEAD unchanged at `a037b637`. No rebuild artifacts committed. This finding is a trace result, not a patch.

## Watermark
SCRIP HEAD `a037b637` (unchanged — no code committed this session). Trace commands: `SCRIP_RBX_FIELD_TRACE=1 scrip --zeta-port={forth,heap} --run corpus/crosscheck/patterns/038_pat_literal.sno`, reproduced twice (md5-identical) each port.
