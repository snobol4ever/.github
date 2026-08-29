# FINDING — a byname CALL's earlier argument slots (`ZOPD`/`ZOPQ` operand 0, 1, ...) read as zeroed garbage when a LATER argument's own evaluation is a relop materialized through `pas_mat` (`BINOP_TEST` + literal-1/0 + temp var); root cause is upstream of Pascal, in the shared `zd_plan`/`op_zread[]` ζ-depth accounting in `src/emitter/emit.cpp`

**seat09 · 2026-08-29 · SCRIP tree `a9408237` (no code changed — a debug probe was added, used, then fully reverted; `git diff --stat` empty) · row `pascal-restore-prezeta`**

## What this refutes from the standing NEXT block

seat10's `## NEXT` (ROOT CAUSE #2, `8ebf6535`) listed `boolptr` (`WRONG_rc0`, prints `1 1` where `.ref` says `1 0`) as "likely candidate for the SAME class of bug as ROOT CAUSE #2 ... worth checking whether `op_zres` and `op_off`/`op_sa`/`op_sb` are even populated the way this box expects." **They are not the same bug.** `boolptr`'s two relops both compile as `IR_BINOP_TEST` (confirmed via `--dump-ir`), never `IR_BINOP_RELOP_VAL` — grepped `src/lower/lower_pascal.c` for `RELOP_VAL`: **zero matches, today, in this tree.** (`IR_BINOP_RELOP_VAL` is emitted only by `src/lower/lower_raku.c:185,217` — ROOT CAUSE #2's fix is real and correctly cures Raku's own value-context relops and, incidentally, every Pascal `IR_BINOP_TEST` that happens to reach the zd arm with the now-added `op_node_kind` guard, but the mechanism it targets is not what `boolptr` exercises.) `bb_binop_relop_val.cpp`'s zd `IR_BINOP_TEST` arm was independently verified byte-inert for this witness class (see below) — this is not a box-guard bug at all.

## Minimal witnesses (ASM-DIFF-FIRST step 1: ablate to a witness, per RULES.md)

All run mode-3, pristine-adjacent (not a full `make pristine`, but a plain incremental `make` on top of `a9408237`, RT_OPT=-O0 default).

| # | program shape | result |
|---|---|---|
| w1_solo | `p^.f := i<3` alone, one record, one field, single statement | **PASS** (`0`) |
| w2 | `b := i>3; if...; writeln(99); b := i<3; if...` — plain var, unrelated CALL between the two relops | **PASS** (`1,99,0`) |
| w3 | `p^.f := i>3; p^.f := i<3; if p^.f...` — SAME field written twice, no read between, single read at the end | **FAIL** (`1`, expected `0`) |
| w4 | `p^.f := i>3; if...; p^.g := i<3; if...` — two DIFFERENT fields of the same record | **PASS** (`1,0`) — see "why w4 looked clean" below, it is not actually clean |
| w5 | `p^.f := i<3; if...; p^.f := i>3; if...` — same field, order swapped (FALSE write first, TRUE second) | **PASS** (`0,1`) |
| w6 | `b := i>3; b := i<3; if b...` — plain var, no CALL at all (bypasses `__pas_field_set` entirely) | **PASS** (`0`) |

The task file's own `boolptr.pas` is structurally w3 plus interleaved reads (write, read+writeln, write, read+writeln) and fails identically (`1,1` vs ref `1,0`).

**Reading across the table:** the bug needs (a) a *named runtime CALL* as the value's consumer — not a plain zeta-cell `ASSIGN` (w6 is clean) — and (b) two such calls in the same flat graph where the SECOND call's relop-materialize sub-chain (`pas_mat`: `BINOP_TEST` → `LIT 1`/`LIT 0` → `ASSIGN __pbtN` → `VAR __pbtN`) is evaluated as one of the call's OWN arguments. Order matters (w5 clean, w3/original broken) only insofar as it changes which write is "second" — the corruption always lands on the SECOND such call, never the first.

## Why w4 looked clean and is not actually evidence of anything

Added a temporary `PBT_DEBUG`-gated trace (top of `script_try_call_builtin_by_name` in `src/runtime/by_name_dispatch.c`, plus one inside the `__pas_field_set` arm printing raw `args[0..2]`). **Fully reverted after use — `git diff --stat` on `src/runtime/by_name_dispatch.c` is empty, nothing committed.**

w3's second `__pas_field_set` call:
```
[PBT_TRACE] fn=__pas_field_set nargs=3
[PBT_RAW] args0.v=0 args0.i=0 args1.v=0 args1.i=0 args2.v=3 args2.i=0 isint0=0
```
`args[2]` (the new value, evaluated LAST, right before the call fires) is correct: `v=3` = `DT_I`, `i=0` = false. **`args[0]` (the record's heap index) and `args[1]` (the field index literal) are both hard-zeroed** — not garbage, exactly zero in both the type-tag and value words. `IS_INT_fn(args[0])` reads false, so `__pas_field_set`'s own defensive guard (`if (n<=0) { *out=args[2]; return 1; }`, `src/runtime/by_name_dispatch.c:2724`) fires and the call **silently no-ops** — no crash, no wrong write, just nothing happens.

w4's second call (`p^.g := i<3`, field index 1, not 0) shows the **identical** zeroing:
```
[PBT_RAW] args0.v=0 args0.i=0 args1.v=0 args1.i=0 args2.v=3 args2.i=0 isint0=0
```
It reads as PASS only because field `g` had never been written before, so its alloc-time default (`__pas_alloc_rec`, `by_name_dispatch.c:2697-2703`, initializes every field segment to the string `"0"`) already equals the value the silently-dropped write was trying to set. **w4 is not a clean control arm — it is the same defect, masked by a value coincidence.** This is exactly the "value counted is not a value graded" class (RULES.md § INSTRUMENT LAWS, clause 11) turned around: here it's "a write dropped is not a write that happened," invisible because the drop and the intent agreed by chance.

## Root cause location (not fully bottomed out — see "why not fixed here")

`bb_call_byname_str`'s ZD arm (`src/templates/bb/bb_call.cpp:290-330`, the `_.op_zres` branch used under the default `cell-stack` ζ-storage config) stages all `narg` arguments by reading each one through `ZOPQ(i, narg*16 + {0,8})` and writing into a fresh `sub rsp, narg*16` scratch block — this box is not itself suspect; it reads whatever `ZOPD`/`ZOPQ` (`src/templates/x86/x86_asm.h:966`, `_.op_zread[k]`) hand it.

`op_zread[]` (`src/emitter/emit.cpp:1022`) is copied from `g_zd_read[]`, which is populated per-node by a backward scan (`emit.cpp:~3193-3197`) that, for each operand `_zj` of the node currently being emitted, finds the operand's PRODUCER node at flat-array index `_k` and computes:
```c
g_zd_read[_zj] = zd_out[i] - zd_out[_k] + _xh;
```
— a ζ-stack-depth DELTA between the consumer (`i`, the CALL) and the producer (`_k`, e.g. the `VAR "p"` node or the field-index `LIT_INTEGER` node), plus `_xh`, a correction that (as written) accounts ONLY for `IR_MATCH_DEFER`/`IR_MATCH_BEGIN`/`zd_arm[i]` nodes encountered while walking backward between producer and consumer. `zd_out[]` itself comes from `zd_plan()` (`emit.cpp:2484`), which builds its depth accounting by chasing `γ`-only straight-line "runs" from designated head nodes (`bb_src_of` boundaries), not a full CFG walk.

**The three IR nodes already confirmed to sit between `p`'s producer and the CALL, for the SECOND field-write only, are exactly the `pas_mat` materialize chain**: `BINOP_TEST` (its own zd arm consumes/produces ζ cells for ITS OWN two operands) → `LIT_INTEGER` → `ASSIGN __pbtN` → `VAR __pbtN` (a γ/ω MERGE point — both the true-literal-assign and false-literal-assign branches converge here, confirmed via the full `--dump-ir` graph trace for `boolptr`, node 12/30 reached from both node 11/29 and node 53/48). None of `_xh`'s three named cases (`MATCH_DEFER`, `MATCH_BEGIN`, `zd_arm[i]`) matches "a BINOP_TEST zd-arm plus a γ/ω merge sits between producer and consumer" — **the leading hypothesis is that this specific intervening shape is exactly the kind of ζ-depth contributor `_xh` does not know how to account for, and/or that `zd_out[]`'s straight-line-run construction (chasing `γ` only) does not assign a consistent depth to a node reached via TWO DIFFERENT incoming edges (the pas_mat merge) in the first place.** This is a hypothesis pinned to a code location, not a proven mechanism — I did not instrument `zd_out[]`/`g_zd_read[]` directly (see below).

## Why not fixed here

`zd_plan`/`zd_out`/`g_zd_read` (`emit.cpp` lines ~2484-3200+) is the shared ζ-depth planning pass for every frontend using `cell-stack` storage — SNOBOL4's own pattern-matching machinery is its heaviest user (the file is dense with `MATCH_BEGIN`/`MATCH_DEFER`/`fence`/`alternate` special-casing accumulated over many prior incidents; comments reference `ZB-FC-3d`, `REG-2/3/6`, `S10e` as historical scar tissue). SNOBOL4 stays 1299/1299 FAIL=0 throughout this entire investigation, so whatever is wrong here is either (a) already-guarded-against for every shape SNOBOL4's own corpus exercises, or (b) needs the specific "byname CALL, non-first argument is a materialize-relop with a real γ/ω merge" combination that SNOBOL4's corpus may simply not construct the way `pas_mat` does. Patching `_xh`'s correction list or `zd_plan`'s run-construction without first instrumenting `zd_out[]`/`g_zd_read[]` directly (which I did not do — I stopped at the `by_name_dispatch.c` boundary once the zeroing was confirmed, per the wall-clock check-in discipline) risks exactly the "confirmed but unexplained regression" class seat12's own reverted fix #2 hit on this same row (see task file `## SUPERSEDED-NEXT`, seat12 block) — a plausible-looking correction to shared, ζ-storage-adjacent code that breaks something a differently-shaped witness would have caught. This is core, shared, high-blast-radius machinery; it deserves a sitting that starts by instrumenting `zd_out[i]`/`g_zd_read[_zj]` directly on the w3 witness, not a patch guessed from reading the formula.

## Standing instructions for whoever picks this up

1. Add a temporary trace INSIDE `emit.cpp`'s backward-scan (~line 3197, gated on a fresh env var, same discipline as this FINDING's own reverted probe) printing `i, _zj, _k, zd_out[i], zd_out[_k], _xh, g_zd_read[_zj]` for the `IR_CALL` node in w3's SECOND `__pas_field_set` (operands 0 and 1 specifically — operand 2 is fine and does not need tracing). Compare against the SAME print for w4's second call (also broken, per the RAW trace above) and w1_solo's only call (correct, for contrast).
2. Confirm directly whether the defect is in `zd_out[]` (the straight-line-run depth assignment disagreeing between the two `pas_mat` branches that MERGE at the `VAR __pbtN` node) or in `_xh`'s missing case, per the hypothesis above — these are different fixes.
3. Grade any cure against the full shared-node battery before trusting it: Pascal M3/M4 (this row's own gates, isolated `RESULTS=`), SNOBOL4 blocking set (standing constraint 1), Icon rung suite (standing constraint 2), Raku smoke (shared-node law — `pas_mat`-shaped materialize-then-CALL is plausible in Raku too, not checked this session).
4. `boolidx` (`EMPTY_rc1`, crashes after exactly 3 of its 4 `arr_set_pure` calls trace, per a `PBT_TRACE`-only run — not yet confirmed with the raw-args probe) is a PLAUSIBLE but NOT CONFIRMED fourth instance of this same mechanism: `arr_set_pure` likely lacks `__pas_field_set`'s defensive `n<=0`/`!hc` early-return, so the same arg-zeroing could crash instead of silently no-op. Confirm with the same raw-args trace before assuming it's the same cause — it could equally be a distinct array-specific bug.
5. `pb34` (`WRONG_rc0`, prints `2 0` vs ref `1 0`) has no field_set/pointer/materialize-into-CALL-argument shape at all on inspection (sets, nested procedures, boolean locals via plain `ASSIGN` not `pas_mat`-through-a-CALL) — **not investigated this session, no reason yet to believe it's related.** `deep5` remains the already-understood, self-diagnosing `PAS-DISPLAY L>=4 fallback unimplemented` bomb — unrelated, out of scope, per seat10's existing characterization.
6. This mechanism is NOT Pascal-specific by construction (it lives in the shared emitter, triggered by an IR shape — "byname CALL with a materialize-relop non-first argument" — that any frontend could construct). Worth a `grep -rn` for byname CALLs whose argument list can include a relop in Raku's and Snocone's lowerers before assuming this is a Pascal-only latent defect.
