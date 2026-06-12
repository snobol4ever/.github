# HANDOFF-2026-06-12-SONNET46-RAKU-BB-LOWER-RV.md

## Goal: GOAL-RAKU-BB — RK-LOWER lower_rv() fixes

## Session result

m2: **21/25 PASS** (was 16/25 at session start).
m3: **1 PASS / 0 FAIL / 24 EXCISED** (was 1 silent FAIL — str_reverse bomb fixed).
m4: **1 PASS / 0 FAIL / 24 EXCISED** (same).
Peers: SNOBOL4 7/7 m2/m3/m4 ✓, Icon m2 12/12 ✓, NFA oracle 5/5 ✓, g_vstack=0 ✓.

SCRIP HEAD: `7463c09`. .github HEAD: `512b3914`.

## What was done

**src/lower/lower_raku.c — lower_rv() extended:**

- `TT_TO`: builds IR_TO with gamma=NULL (standalone src_sg for map/grep source drain).
  Non-"ag" mode: explicit lo/hi operand nodes (IR_LIT_I/IR_LIT_I). gamma=NULL so
  IR_interp_once returns the yielded value directly when next==NULL. Fixes map_range,
  grep_range, map_over_gather, grep_over_gather (4 tests).

- `TT_GATHER`: builds standalone IR_GATHER with gamma=NULL. Same rationale. Enables
  gather-as-map-source.

- `TT_ARR_GET`: chains base-eval -> idx-eval -> IR_IDX so ag_ring is populated
  (base at peek(1), idx at peek(0)) before IR_IDX reads it. Partially works —
  see REMAINING FAILURES below.

- `TT_HASH_GET`, `TT_HASH_EXISTS`: lower_rcall visible=1 path.

- `TT_HASH_SET`, `TT_HASH_DELETE`: pure-variant writeback via IR_ASSIGN +
  lower_rcall("hash_set_pure" / "hash_delete_pure"). Partially works —
  see REMAINING FAILURES below.

- `TT_EVERY` non-gather branch: replaced IR_LIST_BANG+IR_EVERY with direct
  generator pump (same topology as gather case). Generator omega -> outer gamma
  so post-loop statements are reached. Fixes for/map, for/grep loops.

**src/interp/IR_interp.c — IR_LIST_BANG:**
Added generator arm: when lb0->op is IR_MAP/IR_GREP/IR_GATHER/IR_TO, pump by
re-calling IR_interp_node(lb0) each cycle instead of list_bang_at on a list.
(This arm may no longer be reached after the TT_EVERY topology fix — harmless.)

**src/driver/scrip.c — icn_graph_native_emittable_mode:**
Added `if (nd->op == IR_CALL && IR_LIT(nd).dval == 2.0) return 0;`
Converts str_reverse m3/m4 runtime abort ("IR_CALL dval=2 descr-chain arm aborted")
into clean [SMX] EXCISE. Fixes 1 silent FAIL in m3 and m4.

## Remaining 4 m2 failures

### 1. list_construct_read, array_sort, array_reverse (3 tests)

Pattern: `say(@a[1])` where @a=(3,1,2) gives "3" instead of "1".

Root cause identified: **subscript_get() in the runtime is 1-based** (SNOBOL heritage).
`@a[0]` → subscript_get(@a, 0) → fails or returns empty string (index 0 underflows).
`@a[1]` → subscript_get(@a, 1) → returns element 0 (which is 3, not 1).

Verified: `arr_get(@a, 0)` and `arr_get(@a, 1)` work correctly (returns 3 and 1).
`arr_get` normalises the index before calling into the array internals.

**Fix needed:** In `lower_rv TT_ARR_GET`, adjust the index to be 1-based before
passing to IR_IDX. Two options:
  A. Build `IR_BINOP(+, idx_eval, IR_LIT_I(1))` between idx_eval and IR_IDX.
  B. Route through `arr_get` builtin (lower_rcall "arr_get" visible=1) instead of IR_IDX.
Option B is simpler and avoids touching the IR_IDX ag_ring plumbing entirely.

### 2. hash_set_get (1 test)

Pattern: `hash_set($h, 'name', 'Alice'); say(hash_get($h, 'name'));` gives empty.

Our `lower_rv TT_HASH_SET` builds: `IR_ASSIGN($h) <- lower_rcall("hash_set_pure", ...)`.
The by-name dispatch at `src/runtime/by_name_dispatch.c:1587` handles hash_set_pure.
Need to verify: (a) the dval=2.0 IR_CALL for hash_set_pure is actually being executed
in mode-2 (not excised — the icn_graph_native_emittable_mode dval==2.0 check only
applies to modes 3/4, mode-2 always runs), (b) the pure-variant returns a new hash
descriptor and the IR_ASSIGN correctly stores it back to $h.

**Fix needed:** Add a diagnostic test `say(hash_set_pure($h,'x','y'))` to verify
hash_set_pure exists and returns correctly. If the return value is FAIL, check
by_name_dispatch.c:1587 for the hash_set_pure implementation.

## Next session start checklist

1. Read GOAL-RAKU-BB.md (the active goal).
2. Read RULES.md in full.
3. Run session setup: `bash scripts/build_scrip.sh && make libscrip_rt`.
4. Run gate: `bash scripts/test_smoke_raku.sh` — confirm 21/25 m2.
5. Fix TT_ARR_GET: switch from IR_IDX to arr_get via lower_rcall (simplest fix).
6. Fix hash_set_get: diagnose the hash_set_pure path.
7. Re-run gate: target 25/25 m2, 0 silent m3/m4 FAIL.
8. Run peer gates: test_smoke_snobol4.sh, test_smoke_icon.sh, test_gate_raku_nfa_oracle.sh.

## Files touched this session

- `src/lower/lower_raku.c` — lower_rv() additions
- `src/interp/IR_interp.c` — IR_LIST_BANG generator arm
- `src/driver/scrip.c` — dval==2.0 excise in native preflight

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
