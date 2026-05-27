# GOAL-RAKU-BB.md — Raku: goal-directed ~20% onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md.
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**.
  `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_SWITCH` with `a[2].i` tag handing control to a BB graph.
Tags: `SM_BBSW_ICN_GEN` (0x49434E47), `SM_BBSW_PL_ENTRY` (0x504C454E),
`SM_BBSW_RK_GEN` (0x524B474E "RKGN"). Raku reuses the ICN_GEN emit-time
contract verbatim — `sm_bb_switch.cpp` / `emit_sm.c` / `sm_interp.c` arms
accept both tags.

**Where Raku sits:** Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed.
Raku today is ~100% eager SM in practice; the goal-directed ~20% is what
this goal moves onto shared BB kinds.

**Rules (RULES.md):** no C Byrd boxes; no SM/BB walking at runtime in modes 3/4;
ports are α/β/γ/ω; no `rt_*`/`raku_*` *port-logic* helpers (conversion/effect
helpers via `@PLT` are fine). X86 arms only.

## The insight (validated by RK-BB-1)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**.
`gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand.
ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP)
suffices; every generative construct is a PRODUCER or CONSUMER of it. A would-be
10-kind ladder collapses to ~3 rungs on already-templated shared kinds.

## Port semantics (identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | `take` yield / next Seq element |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`**. NOT Prolog's `BB_ONCE`.

## Pipeline

```
Raku source → frontend (raku.y/.l)
  → SM spine: scalar/eager → SM_CALL_FN
             generative   → lower_raku_* → BB_graph(lang=BB_LANG_RKU)
                          → SM_emit_sii(SM_BB_SWITCH, NULL, bb_idx, SM_BBSW_RK_GEN)
  → SHARED templates (already filled): bb_to_by.cpp, bb_upto.cpp,
                                       bb_iterate.cpp, bb_gen_alt.cpp
  → emitted x86 (Mode 4)
```

## Moves to BB vs stays SM

**MOVES (goal-directed, REUSE shared kinds):**

| Raku construct | shared BB kind | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | `BB_TO_BY` | RK-BB-1 ✅ |
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 |
| lazy `map` / `grep` | `BB_ITERATE` consumer (γ predicate for grep) | RK-BB-3 |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse on ω/γ | RK-BB-4 |

**STAYS eager SM:** scalar builtins (`uc`/`lc`/`substr`/`trim`/`index`/`rindex`),
`say`/`print`, arithmetic, hash/array element ops, class/method dispatch,
`sort` (whole-list), `try`/`CATCH` (the existing inline `raku_exc_*` SM is the
right shape).

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. SNOBOL4 pattern
axis (`BB_SCAN`+`BB_PAT_*`) plus Prolog `BB_ONCE`+OR-retry for rule selection.
Heaviest lift; defer until SNOBOL4-BB and PROLOG-BB land more rungs. Today's
eager `raku_nfa_exec` stays.

## ⛔ No `rt_*`/`raku_*` port-logic helpers

Never add `raku_seq_pull` / `rk_take_yield` / `raku_grep_step` / junction
dispatch helpers. Port logic (α/β/γ/ω) lives in the shared `bb_*.cpp` templates,
emitted inline as x86. If a rung "needs" a new `raku_*` helper, the lowering is
wrong — fix the BB graph, not the runtime.

## Ladder steps

- [x] **RK-BB-1** ✅ (2026-05-27, Opus, one4all `13cef01a`) — lazy inclusive range
  `for $a..$b -> $i` → shared `BB_TO_BY`. `lower_raku_range` synthesizes
  `TT_TO_BY`, reuses `lower_icn_expr_top`, retags `BB_LANG_RKU`. `lower_for_range`
  gated `LANG_RAKU && !exclusive`. Arms widened in `sm_bb_switch.cpp` /
  `emit_sm.c` / `sm_interp.c`. `bb_to_by.cpp` REUSED unchanged. GATE-RK4 +
  `run_raku_via_x86_backend.sh` + `rk_range_for` test added. Shared runtime fix:
  `rt_nv_set` made non-consuming (peek) so mode-4 STORE_VAR matches mode-2.
  Open follow-on (RK-BB-1b): exclusive `..^` + non-literal-bound ranges
  (currently fall through to eager SM).

- [x] **RK-BB-2** ✅ (2026-05-27, Opus 4.7, one4all `d08237e0`) — KEYSTONE lazy `Seq` box.
  `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP. REUSE `bb_upto.cpp`.
  `test/raku/rk_gather.raku` PASSES `--compile` (mode-4): byte-exact `10\n20\n30\ndone\n`.
  - Step 1 ✅ (one4all `2f2aed25`) — `lower_icn_proc_body` accepts TT_SUB_DECL;
    hoist registers `__gather_N` in proc_table.
  - Step 2 ✅ (one4all `340b804d`) — `TT_SUSPEND` case in `lower_icn_expr_node`
    emits `BB_SUSPEND` node (Raku-gated via `cfg->lang`).
  - Step 3 ✅ (one4all `8a046af1`) — `lower_every`/`lower_iterate` accept
    LANG_RAKU; have_switch guard prevents PUSH_VAR a[0] clobber.
  - Step 4 ✅ (one4all `e8568ee4`) — `bb_suspend.cpp` template authored:
    literal-int fast-path pushes DESCR_t{DT_I, val_i} onto r12 via
    `rt_push_int@PLT` (TEXT) or inline 16-byte stack push (BINARY).
  - Step 5 ✅ (one4all `e8568ee4`) — `emit_core.c` walk_bb_node: BB_SUSPEND
    peeled off bb_stub group → routes to `bb_suspend(nd)`.
  - Step 6 ✅ (one4all `d08237e0`) — UNBLOCKED. Three-edit patch in lower.c:
    (a) `lower_hoist_gather_in_expr`: `def->v.sval = intern(gname)` →
        `def->v.ival = 0`. The v.sval/v.ival union-clobber was causing
        `lower_icn_proc_body` to read garbage as nparams (Open Q5).
    (b) `lower_stmt` RAKU+TT_SUB_DECL branch: skip body emission when the
        proc name starts with `__gather_`. Body lives in the BB graph;
        emitting at top-level orphans it (stack underflow on startup).
    (c) `lower_expr_inner` TT_SUB_DECL case: same defensive skip; keeps
        `SM_PUSH_NULL` contract intact.
    lower_icn_proc_body builds the BB graph (BB_SEQ→3×BB_SUSPEND); lower_fnc
    routing emits `SM_BB_SWITCH(SM_BBSW_RK_GEN, bb_idx)` at every call site;
    sm_bb_switch.cpp dispatches via bb_seq → bb_suspend (template emission).
    NOT needed: the separate `lower_raku_proc_body()` the handoff anticipated.
    The existing path works once nparams is correct. Open follow-on
    (RK-BB-2b): mode-2 still stack-underflows on `rk_gather` (bb_exec.c has
    no executor for BB_SUSPEND) — a separate Icon-shared goal per the
    handoff's gating comment in TT_SUSPEND.

- [ ] **RK-BB-3** — lazy `map`/`grep` as Seq CONSUMERS. REUSE `bb_iterate.cpp`;
  grep adds γ-port predicate test (loop on false, γ on true, ω on source ω).
  Migrate `lower.c:1872-1881` off eager `SM_CALL_FN raku_map`/`raku_grep` for
  the lazy path. `rk_map_grep_sort24.raku` under `--compile` (sort stays eager).

  ## RK-BB-3 substrate analysis — Opus 4.7, 2026-05-27 (post-RK-BB-2 audit)

  Inspecting the failing target `rk_map_grep_sort24.raku` uncovered four substrate
  gaps that block RK-BB-3 as originally scoped. The scope as written ("lower the
  map/grep ops, reuse bb_iterate") underestimates the work because `bb_iterate.cpp`
  is not yet a polymorphic iterator: it hard-codes Icon's `!"literal"` semantics.

  ### Gaps (verified by probing, not from memory)

  1. **`for @arr -> $v` does not loop in mode-4 or mode-2.** `lower_iterate`
     RAKU branch (lower.c:1602-1607) emits the array expr once and stores it
     into `$v` with no loop. New probe `test/raku/rk_for_array_simple.raku` is
     a 3-line `push;push;push; for { say }` — FAILS both modes with Error 5.

  2. **`bb_iterate.cpp` is DT_S-only.** Template assumes a compile-time `hay`
     string and reads `pBB->ival` for slen. No runtime type-dispatch on the
     iterable.

  3. **Mode-2 `BB_ITERATE` executor (bb_exec.c:2227) is also DT_S-only.** Reads
     `nd->α->value.s`; arrays would see len=0 and return ω immediately.

  4. **Raku arrays are `\x01`-separated STRINGS (DT_S), NOT Icon-lists.** From
     test/raku/rk_arrays.raku top-of-file: `# Arrays stored as \x01-separated
     strings in normal DESCR_t slots. push/pop/elems/arr_get as builtins; @arr[$i]
     = val via arr_set builtin.` The design choice is to encode arrays as a
     single string with `\x01` (SOH) between elements, kept in normal DT_S
     slots. **Earlier audit-memo claim that Raku arrays use Icon DT_DATA was
     INCORRECT.** Verified by running mode-2 rk_arrays: it FAILS with Error 5
     (push/pop/arr_get/elems handlers ABSENT in raku_builtins.c). Mode-2 GATE-RK
     8/31 PASS list contains zero array tests — all array tests fail in both
     modes today. The aspirational \x01-string design is documented in test
     file comments but has no runtime implementation yet.

  5. **`arr_get` / `arr_set` / `raku_map` / `raku_grep` / `raku_sort` are not
     `rt_*` symbols.** They're SM_CALL_FN names dispatched through `rt_call`,
     which chains only `icn_try_call_builtin_by_name` then `INVOKE_fn`. The
     existing `raku_try_call_builtin(tree_t*, DESCR_t*)` takes an AST node
     (mode-2 only) and calls `interp_eval`, so it can't be chained from
     `rt_call` without a parallel by-name-by-args entry point.

  6. **`BB_LIST_BANG` mode-4 template is `bb_icn_stub` too.** So Icon's `!L`
     over a Raku-style list is ALSO not emitted at mode-4 today; reusing that
     kind would require authoring a fresh template, not just retagging.

  ### Decomposition (REVISED 2026-05-27 post-correction)

  Because Raku arrays are \x01-separated strings (NOT DT_DATA), the work
  collapses considerably. No FIELD_GET_fn call needed; the iterable IS
  already a string. `bb_iterate.cpp`'s existing DT_S machinery is more
  applicable than first appeared — only the source-string-discovery
  changes (runtime peek of α->value instead of compile-time `hay`).

  - [x] **RK-BB-3.0** ✅ (2026-05-27, Opus 4.7, one4all `7a60d30e`) — fleshed
    out the runtime builtins so arrays work in both mode-2 and mode-4.
    Non-mutating half (elems, arr_get, substr, index/rindex, uc/lc/chars/
    length/trim, sort) authored at fcac4ab3, made REACHABLE by RK-BB-3.0a
    (ba481112). Mutating half (push/pop/arr_set) authored at fcac4ab3,
    made REACHABLE by RK-BB-3.0b (7a60d30e). All ops use \x01-separated
    string representation per test/raku/rk_arrays.raku spec.

  - [x] **RK-BB-3.0b** ✅ (2026-05-27, Opus 4.7, one4all `7a60d30e`) —
    GAP 2 mutators wired. lower.c lower_fnc (push/pop): prepend
    SM_PUSH_LIT_S vname when first real arg is TT_VAR; nargs+1.
    lower.c case TT_ARR_SET: same prepend; nargs 3→4. sm_interp.c
    SM_CALL_FN + rt.c rt_call: mutating branch above the non-mutating
    raku chain peels args[0].s as vname when fn ∈ {push, pop, arr_set}
    AND args[0].v == DT_S, calls raku_try_mutating_builtin_by_name.
    GATE-RK 9→10 (+rk_arrays), GATE-RK4 10→11 (+rk_arrays). All
    smokes/broker hold. FACT RULE clean.

  - [x] **RK-BB-3d** ✅ (2026-05-27, Opus 4.7, one4all `fcac4ab3` +
    `ba481112`) — `raku_try_call_builtin_by_name(fn, args, nargs, out)`
    parallel entry point added to raku_builtins_byname.c; chained into
    `rt_call` AND `sm_interp.c` SM_CALL_FN dispatch, BEFORE icn fallback,
    gated on `g_lang == LANG_RAKU`. RK-BB-3.0a (ba481112) added the
    `rt_set_lang` prologue emission so mode-4's libscrip_rt.so g_lang
    is stamped before any rt_call runs.

  - [x] **RK-BB-3.0a** ✅ (2026-05-27, Opus 4.7, one4all `ba481112`) —
    unblock for fcac4ab3's infra: (1) lower.c lower_fnc c[0]-dup
    suppression (LANG_RAKU-gated, name-equality guard); (2) rt_set_lang(int)
    + XA_FILE_HEADER prologue emits `mov edi, <g_lang>; call rt_set_lang@PLT`
    so mode-4's libscrip_rt.so g_lang is stamped before any rt_call;
    (3) `trim` aliased onto `raku_trim` in byname dispatcher. GATE-RK
    8→9 (+rk_str22), GATE-RK4 9→10 (+rk_str22). All smokes hold. FACT
    RULE clean. 100% template emission preserved.

  - [~] **RK-BB-3a** (mode-2 ✅, mode-4 WIP, 2026-05-27, Opus 4.7) —
    `for @arr -> $v` polymorphism for `BB_ITERATE`. **Mode-2 GREEN; +2
    gate wins (rk_for_array_simple + rk_for_array).** Decomposition:

    **Lowering** (lower.c): `lower_raku_iterate_arr(arr_vname)` builds
    a 1-node BB graph — `BB_ITERATE`, `sval=intern(arr_vname)`,
    `cfg->lang=BB_LANG_RKU`, α/β self-loop, γ/ω NULL (patched by
    scaffold). `lower_every` widened: pattern-matches
    `TT_EVERY(TT_ITERATE(TT_VAR(arr), sval=$v), body)` ahead of the
    generic scaffold; emits SM_BB_SWITCH(RK_GEN, bb_idx), JUMP_F → exit,
    `emit_var_store($v)` on γ-yield, lower_expr(body), JUMP back to
    SWITCH, patches exit, stamps `a[0].i=exit_pos`. Mirrors
    `lower_for_range` pattern (RK-BB-1's BB_TO_BY scaffold).

    **Discriminator**: `BB_t.sval` presence (no new BB_t fields per
    PEERS RULE). Raku sets `sval=arr_vname`; Icon's legacy path stays
    `sval=NULL`. `cfg->lang` carried but not accessed from templates
    (no cfg back-pointer per PEERS RULE).

    **Mode-2** (bb_exec.c BB_ITERATE): sval-polymorphic case branches
    before the legacy α-as-operand-box code. Raku branch fetches source
    via `NV_GET_fn(nd->sval)` on EVERY call (re-fetch, not cache —
    `nd->value` is the yielded-segment return slot, not a source cache).
    Walks counter as byte-offset; scans for `\x01`; yields substring as
    fresh GC-allocated DT_S; advances counter past separator (end+1).
    Exhaustion (counter ≥ slen) → ω. Icon legacy path untouched.

    **Mode-4** (bb_iterate.cpp): Raku MEDIUM_TEXT arm authored. .data
    slots: `.Liter<id>_name: .asciz "<vname>"` + `.Liter<id>_cnt: .quad
    0`. α resets counter, jmp load. β falls through to load (counter
    already advanced). load: `call NV_GET_fn@PLT` → DESCR_t in
    `rax:rdx` per SysV ABI (≤16-byte struct); `mov rsi,rax; shr rsi,32`
    extracts slen; `mov r10,rdx` saves base ptr; bounds check vs counter
    `jge ω`. scan: walks `rcx` looking for `\x01` byte or slen end.
    send: computes `r8=seg_len`, `r11=seg_start_ptr`; advances counter
    to `end+1`; `mov rdi=r11, rsi=r8; call rt_push_str@PLT; jmp γ`.
    **100% template emission** — only conversion/effect helpers
    (NV_GET_fn, rt_push_str) via @PLT; all port-logic inline x86.
    FACT RULE clean (no seg_byte/SL_B/sl_emit_one/emit_standard_blob).

    **Mode-4 known issue (blocks `rk_for_array_simple` mode-4 PASS):**
    in the full program, `NV_GET_fn("x")` returns NULVCL (slen=0) at
    the BB_ITERATE body, even though `push(@x,...)` mutators correctly
    populate `_var_buckets["x"]` and `say(@x)` reads the populated
    value. **Isolated asm test** (gcc-compiled standalone with the
    exact instruction sequence) yields 3 segments correctly. So the
    asm logic is verified — the issue is at the wrapper/program level.
    Hypotheses for next session:
      (a) Section-switch fall-through: `.section .data` slots are
          embedded between `.Licngen<n>_fresh:` and `.Licngen<n>_α:`;
          assembler may be misplacing the fall-through.
      (b) Name mismatch: my `.asciz "x"` from `pBB->sval` vs `.S2:
          .string "x"` used by `PUSH_VAR` — unlikely lexically identical
          but worth a binary check.
      (c) Scope/timing: `_var_buckets` may be cleared/reset between
          the push calls and the BB_ITERATE entry.
    Recommendation: `objdump -d` on the linked binary; print the
    `_var_buckets[hash("x")]->val.slen` from a small custom debug
    helper called right before `NV_GET_fn`.

  - [ ] **RK-BB-3a-mode4-debug** — root-cause + fix the slen=0 bug in
    the full-program mode-4 path. Once green, RK-BB-3a closes; mode-4
    flips +2 (rk_for_array_simple + rk_for_array, mirroring mode-2).

  - [ ] **RK-BB-3b/c** — map/grep as Seq consumers. Once 3a's polymorphic
    BB_ITERATE exists, lazy map = `BB_ITERATE(@arr)` → γ-side block runs
    the lambda, leaves result on r12 → yield. grep = same with γ
    predicate gate. Result materialization via the new `push` builtin
    accumulating into a fresh \x01-string.

  ### Recommended execution order

  3.0 → 3d (commit together — they enable each other) → 3a (lowering +
  template polymorphism, single commit) → 3b → 3c. Each commit gate-safe;
  3.0+3d should land green movement even without 3a (rk_arrays, rk_str22,
  rk_subs, rk_try_catch25 likely flip).

  ### Open questions for Lon (gating RK-BB-3a; UPDATED post-correction)

  Q1. **Polymorphic BB_ITERATE or new BB_ARR_ITERATE kind?**
      Going polymorphic per "kinds are language-agnostic." Icon's existing
      template behavior is preserved bit-identically for char-by-char DT_S;
      the Raku \x01-scan branch is gated on a discriminator field.

  Q2. **\x01-string array representation — keep or revise?** Raku arrays
      as SOH-delimited strings is unusual but documented in the test
      corpus. It's lightweight (no new heap structure), works with
      existing DT_S machinery, and serializes naturally. Alternatives:
      DT_A (ARBLK_t, 1-based), DT_DATA Icon-list, or a new DT_RAKULIST.
      Per "follow existing comments," keep \x01-string. Confirm?

  Q3. **`my @x = map { ... } @y` materialization** — eager-drain into a
      fresh \x01-string (one rung less, mode-2 keeps working) or stay
      lazy as a Seq box (truer to Raku, needs a new value type carrying
      the BB graph + state)? Recommend eager-drain for RK-BB-3b; lazy
      is a future rung.

  ### What was DONE this session (pre-direction)

  - Cloned + built. All gates HOLD at baseline (no regressions).
  - Added test/raku/rk_for_array_simple.raku + .expected as the RK-BB-3a
    probe. Mode-4: 9/31 (was 9/30, +1 fail by added test). Mode-2: 8/31.
  - Inspected substrate; this memo is the deliverable. Zero code changes.
  - NO commits — waiting on Q1/Q2/Q3 directives before authoring 3a.

- [ ] **RK-BB-4** — junctions + infix `|`/`&` → `BB_ALTERNATE` with Bool-collapse
  policy on ω/γ. REUSE `bb_gen_alt.cpp`/`bb_alt.cpp`. Add junction test.

- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers, one rung
  each. `zip`/`cross` = multi-Seq drivers (later).

## Rung methodology (mostly REUSE)

Per rung: (1) lower the Raku construct to the shared BB kind via
`lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp`
covers it (Icon proved most cases); (3) only if Raku semantics differ, extend
the shared template behind a `lang==BB_LANG_RKU` guard (last resort — prefer
making the lowering match the template); (4) run GATE-RK4 + GATE-PK + GATE-RK
(mode-2) + smoke. Commit when the Mode-4 golden matches and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (30 cases). The job is mode-4 conformance to
those goldens (the Prolog GATE-4 pattern), not correctness-from-zero — mode-2
already runs them. Add NEW flat files only for laziness probes the eager suite
can't express (e.g. `(1..Inf)[4]` that must terminate).

## Mode-3 (`--run`) — needs a Lon directive

RULES.md sanctions exactly one temporary SM-walk exception (Prolog `--run`,
AGW-1c). Do NOT route Raku `--run` through `sm_interp_run` without a Lon
directive. Mode-4 is this ladder's target; Mode-3 follows for free when the
templates land (same `bb_*.cpp` serves both per ARCH-SCRIP §"Mode 4").

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt > /tmp/build.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash scripts/test_raku_ir_rungs.sh    # GATE-RK mode-2 baseline
bash scripts/test_raku_mode4_rung.sh  # GATE-RK4 mode-4 baseline
bash scripts/test_smoke_raku.sh       # smoke baseline
# GATE-PK currently SEGFAULTS — see watermark; do not block on it.
```

## Gates

```
GATE-PK    test_per_kind_diff.sh        # currently segfaults (NOT this goal — see watermark)
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: 706e2828 (RK-BB-3a partial — mode-2 + mode-3 polymorphism; +2 mode-2 +2 mode-3; mode-4 template authored)
.github: HEAD (handoff — RK-BB-3a partial; mode-4 blocked on slen=0 NV_GET issue)
corpus:  unchanged

Gates at RK-BB-3a partial (2026-05-27, Opus 4.7):
  GATE-RK mode-2:  12/31  (cumulative +4 from baseline 8: rk_str22, rk_arrays, rk_for_array_simple, rk_for_array)
  Mode-3 (--run):  12/31  (matches mode-2; bb_exec.c polymorphism serves both — SBL-MODE3-REACTIVATE 380b4683 made --run live again this session)
  GATE-RK4 mode-4: 11/31  (cumulative +2 from baseline 9: rk_str22, rk_arrays — RK-BB-3a mode-4 not yet flipping; see blocker below)
  Smoke raku:      5/0    HOLD
  Smoke icon:      5/5    HOLD
  Smoke prolog:    5/5    HOLD
  Broker Icon:     198    HOLD
  GATE-PK: ⛔ harness segfault — INHERITED. Owed: SBL-ANY session.
  FACT RULE grep:  0
  Build:           clean

⛔ RK-BB-3a partial ✅ (mode-2) + ⚠ (mode-4 blocked) — 2026-05-27, Opus 4.7:

THREE FILES TOUCHED (+242/-50 across):
  (1) src/lower/lower.c (+54): lower_raku_iterate_arr(arr_vname) builds
      a single-node BB graph with BB_ITERATE, sval=intern(arr_vname),
      cfg->lang=BB_LANG_RKU. α/β self-loop; γ/ω left NULL for scaffold.
      lower_every widened: when LANG_RAKU and gen_expr is
      TT_ITERATE(TT_VAR(arr), sval=$v) — emit SM_BB_SWITCH(RK_GEN,
      bb_idx); JUMP_F→exit; emit_var_store($v); body; JUMP→SWITCH;
      patch exit; stamp a[0].i=exit_pos. Mirrors lower_for_range
      (RK-BB-1 pattern).

  (2) src/lower/bb_exec.c (+39): BB_ITERATE case sval-polymorphic.
      Raku branch (sval != NULL) fetches via NV_GET_fn EVERY call
      (re-fetch, not cache — nd->value is the yielded-segment return
      slot). Walks counter as byte-offset; scans for \x01 byte; yields
      GC-allocated DT_S substring; advances counter past separator.
      Exhaustion → ω. Icon legacy α-as-operand-box path untouched.

  (3) src/emitter/BB_templates/bb_iterate.cpp (+150 net): Raku
      MEDIUM_TEXT arm authored. .data slots: .Liter<id>_name (asciz)
      + .Liter<id>_cnt (.quad 0). α resets counter, jmp load. β falls
      through to load. load: call NV_GET_fn@PLT → DESCR_t in rax:rdx
      per SysV ABI struct-≤16 convention; mov rsi,rax; shr rsi,32 →
      slen; mov r10,rdx → base ptr; bounds check vs counter; jge ω.
      scan: rcx walks looking for \x01 or slen; r9 = seg start. send:
      r8 = seg_len; r11 = seg_ptr; counter++; call rt_push_str@PLT
      (rdi=ptr, rsi=len); jmp γ. 100% template emission. Legacy Icon
      path preserved as dead code (still broken: "inc qword ptr [rax],"
      trailing comma + r12-direct in --compile — kept for shape
      compatibility, NOT reached today since Icon !E lowers via
      BB_LIST_BANG).

VERIFIED:
  - Mode-2 rk_for_array_simple byte-exact to .expected (10\n20\n30\n).
  - Mode-2 rk_for_array flips green too.
  - All sibling smokes (icon, prolog, raku, broker) HOLD.
  - FACT RULE grep: 0 call-sites.
  - Isolated mode-4 asm test (gcc-compiled standalone with exact
    instruction sequence from template) yields 3 segments + ω cleanly.

⛔ MODE-4 BLOCKER — slen=0 from NV_GET_fn at full-program runtime:

Debug instrumentation (added then removed) confirmed:
  - α fires; load fires; NV_GET_fn("x") returns DESCR_t with slen=0.
  - Same program, when it executes `say(@x)` AFTER the push() calls
    and BEFORE the for-loop, prints "10\x0120\x0130" — proving
    _var_buckets["x"] is correctly populated at that point.
  - The mutators DO populate (verified with rk_dbg programs).
  - The isolated standalone asm test (same instruction sequence,
    manually-populated _var_buckets["x"]) yields all 3 segments
    correctly via NV_GET_fn → bounds-check → scan → rt_push_str.

So the failure is at the wrapper-level, not the template-asm level.
HYPOTHESES (ordered by plausibility) for next session:

  (1) SECTION-SWITCH FALL-THROUGH BUG. The SM_BB_SWITCH wrapper
      emits its own .section .data block for the entry-flag byte
      (.Licngen0_ent), then .section .text. My α template body
      ALSO emits .section .data (for name + counter slots) then
      .section .text + .intel_syntax noprefix. The fall-through
      path from .Licngen0_fresh: → .Licngen0_α: crosses TWO
      section-switch pairs. If gas's section-tracking gets confused
      and the byte after `mov byte ptr [rax], 1` lands in .data
      instead of .text, the CPU executes garbage. Check via
      objdump -d to confirm reachability.

  (2) NAME LOOKUP MISMATCH. My .Liter<id>_name: .asciz "x" vs the
      .S<n>: .string "x" used by PUSH_VAR. Both should be identical
      ("x" stripped of @-sigil at Raku-parse time). Verify with
      objdump -s -j .data; compare addresses of both labels' bytes.

  (3) NV_GET_fn called too early — relative ordering of α-body vs
      preceding pushes' CALL_FN macros. Unlikely (SM_BB_SWITCH PC=23
      is well after push CALL_FNs at PC=11,16,21) but objdump will
      confirm.

  (4) Calling-convention rare-edge: NV_GET_fn returns DESCR_t via
      `rax:rdx`. My `shr rsi, 32` after `mov rsi, rax` should extract
      slen. The isolated test verifies this works. But maybe in the
      full binary, NV_GET_fn's @PLT entry resolves to a different
      function than the standalone test? Unlikely but verifiable
      via objdump on the import table.

RECOMMENDED NEXT SESSION FIRST MOVES (10-15 min triage):
  a. Build the rk_for_array_simple binary.
  b. `objdump -d` it; locate .Licngen0_α; verify fall-through path
     from .Licngen0_fresh is clean text.
  c. `objdump -s -j .data` to see the .Liter*_name slot byte contents.
  d. Add a printf-style debug call WITH stack-alignment via the
     rt_pl_write_atom@PLT pattern (already verified in this session's
     instrumentation — the call works, just unable to figure out
     the post-NV_GET state).
  e. Or: add a one-time rt_* debug helper (rt_raku_iter_probe(name))
     that dumps the bucket contents — easier than asm debugging.

OPEN: RK-BB-3a-mode4-debug. Once green, RK-BB-3a closes; mode-4
flips +2 (rk_for_array_simple + rk_for_array, mirroring mode-2).
Then RK-BB-3b/c (lazy map/grep) is the next rung — needs the
polymorphic BB_ITERATE substrate this rung establishes.

⛔ END RK-BB-3a partial HANDOFF

⛔ PRIOR HANDOFFS RETAINED FOR HISTORY: 3.0b, 3.0a, 3.0+3d infra,
   RK-BB-2 below.

⛔ RK-BB-3.0b ✅ COMPLETE (2026-05-27, Opus 4.7, one4all 7a60d30e):

Completes the mutating half of RK-BB-3.0. The non-mutating half landed
in RK-BB-3.0a (ba481112). 3.0b makes push/pop/arr_set reachable in both
mode-2 and mode-4 by routing them through the existing
raku_try_mutating_builtin_by_name dispatcher (authored fcac4ab3).

Four-file commit (+66/-4):
  (1) lower.c lower_fnc (after the RK-BB-3.0a skip0 gate):
      Detect mutator-by-name (push/pop) in LANG_RAKU and emit
      SM_PUSH_LIT_S vname BEFORE the regular args loop when first
      real arg (after skip0) is TT_VAR. SM_CALL_FN nargs+=1.
  (2) lower.c case TT_ARR_SET (@arr[i] = v doesn't go through TT_FNC):
      Same prepend; c[0] is the array variable TT_VAR. nargs 3→4.
  (3) src/processor/sm_interp.c SM_CALL_FN — mutating branch above
      the existing raku_try_call_builtin_by_name chain. Peels
      args[0].s as vname; passes &args[1] / nargs-1. Gated on
      g_lang == LANG_RAKU AND args[0].v == DT_S.
  (4) src/runtime/rt/rt.c rt_call — mirror dispatch for mode-4.
      Same vname-peel. NAMEPTR/NAMEVAL deref on out before push.
      rt_set_lang prologue from RK-BB-3.0a ensures g_lang ==
      LANG_RAKU in the mode-4 binary's libscrip_rt.so.

Verified mode-2 + mode-4 rk_arrays byte-exact to .expected.

⛔ NEXT — RK-BB-3a (BB_ITERATE polymorphism for `for @arr -> $v`):

Runtime substrate is now COMPLETE (arr_get/elems/push/pop/arr_set all
work mode-2 + mode-4). The remaining gap is iteration: `for @arr -> $v`
currently doesn't loop in either mode — lower_iterate's Raku branch
(lower.c:1602-1607) emits the array expression once and stores it to
$v without a loop.

Decomposition (per prior audit memo):
  - lower.c lower_iterate Raku branch: build a BB graph wrapping
    BB_ITERATE with the @arr variable as α-operand; wrap in
    SM_BB_SWITCH(SM_BBSW_RK_GEN). lower_every finds the SWITCH and
    engages the loop scaffold. Loop var stored on γ pull.
  - bb_iterate.cpp template: extend for \x01-string DT_S Raku-array
    semantics. Polymorphic discriminator at α-time. Icon's DT_S
    char-by-char path stays bit-identical (gated on cfg->lang ==
    BB_LANG_ICN); Raku path scans for SOH (\x01) and yields each
    substring as a fresh DESCR_t.
  - bb_exec.c BB_ITERATE executor (~L2227): same polymorphism for
    mode-2 (so for-loop works in --interp too).

Gates probe: rk_for_array_simple should flip mode-2 + mode-4 once 3a
lands. Then rk_for_array (which mixes for-loop with arr_get etc.)
likely flips too. RK-BB-3b/c (lazy map/grep) follow.

Pre-existing segfault cluster (rk_subs, rk_interp, rk_try_catch25)
remains a separate concern — verified at baseline pre-RK-BB-3.0a.
Consider RK-BB-SEGFAULT-CLUSTER as a new rung if Lon prioritizes.

⛔ END RK-BB-3.0b HANDOFF

⛔ PRIOR HANDOFFS RETAINED FOR HISTORY:
   RK-BB-3.0a HANDOFF + Gates-at-ba481112 trailer is below; the original
   fcac4ab3 RK-BB-3.0+3d infra HANDOFF block is below that. Both retained
   for context — GAP 1 was solved in 3.0a, GAP 2 was solved in 3.0b.

⛔ HANDOFF — Opus 4.7, 2026-05-27, ba481112 (RK-BB-3.0a, Gates trailer):
  GATE-RK mode-2:  9/31   (+1: rk_str22)
  GATE-RK4 mode-4: 10/31  (+1: rk_str22)
  Smoke raku:      5/0    HOLD
  Smoke icon:      5/5    HOLD
  Smoke prolog:    5/5    HOLD
  Broker Icon:     198    HOLD
  GATE-PK: ⛔ harness segfault — INHERITED. Owed: SBL-ANY session.
  FACT RULE grep:  0
  Build:           clean

⛔ RK-BB-3.0a ✅ COMPLETE (2026-05-27, Opus 4.7, one4all ba481112):

Two-part unblock for the RK-BB-3.0+3d infra landed in fcac4ab3.

PART 1 — lower.c lower_fnc c[0]-dup suppression (lower.c:~L562-572):
  Raku frontend make_call() (raku.y:59-64) intentionally constructs TT_FNC
  with v.sval=name AND c[0]=TT_VAR(name) — pre-dating the by-name dispatch
  path. lower_fnc iterated all children, pushing the function name as the
  first stack arg, so CALL_FN saw nargs+1 args with the function name in
  args[0]. Suppression gated LANG_RAKU + c[0]==TT_VAR + c[0]->v.sval ==
  t->v.sval. Icon (v.sval=NULL, c[0]=callable) and SNOBOL4 (v.sval=name,
  no dup) bit-identical. Confirmed by inspection of all frontends'
  TT_FNC construction.

PART 2 — rt_set_lang + XA_FILE_HEADER prologue emission:
  g_lang is in libscrip_rt.so's BSS (zero-init = LANG_SNO=0). Mode-4
  binaries link libscrip_rt directly without going through scrip's
  frontend, so the LANG_RAKU-gated raku-builtin chain in rt_call
  (fcac4ab3) was DEAD CODE in mode-4 — g_lang never got set.
  Fix: rt_set_lang(int) added to rt.c after rt_gc_init. XA_FILE_HEADER
  template extended to emit `mov edi, <g_lang>; call rt_set_lang@PLT`
  between rt_gc_init and rt_register_expressions. The compiler's
  current g_lang (LANG_RAKU=3 for .raku source) is baked into the
  prologue, runs before any rt_call, stamps libscrip_rt's g_lang.
  This is the doctrinally-correct 100% template emission path —
  every new byte goes through xa_file_header.cpp via xa_dispatch
  (no emit_textf / seg_byte additions). FACT RULE grep stays 0.

PART 3 — raku_builtins_byname.c trim alias (+1 char):
  trim handler only matched "raku_trim" (mangled); user code writes
  plain trim(...). Aliased per peer pattern (uc/lc/chars/length).

Diagnostic path:
  - mode-2 rk_str22 was producing "  hello" instead of "hello" for
    the trim($padded) call after PART 1 alone — exposed the missing
    alias. With PART 3, mode-2 flipped green.
  - mode-4 still errored "Error 5 Undefined function" because
    g_lang=0. Inspected nm out/libscrip_rt.so: g_lang at BSS offset
    0x56cec0 (B = uninitialized). Verified only one definition site
    (lower.c:1710 g_lang=lang) which runs in scrip's process, not
    the mode-4 binary's process. Added PART 2 → mode-4 flipped.

NOT this session: Q5 union-clobber proper fix (open in goal); the
defensive v.ival=0 from RK-BB-2 step 6 (d08237e0) still load-bearing.

⛔ NEXT — GAP 2 from prior handoff (mutators):

  push($arr, $val) / pop($arr) / arr_set($arr, $i, $val) mutate a
  variable. The raku_try_mutating_builtin_by_name() entry point is
  already authored in raku_builtins_byname.c — it expects args[0]
  to be a STRING containing the variable NAME (not the var value).

  Lowering tweak in lower.c (lower_fnc, near the new skip0 gate):
    if (LANG_RAKU && t->v.sval && is_mutator(t->v.sval)) {
        /* Push variable NAME as args[0] instead of c[0]'s value-push */
        SM_emit_s(g_p, SM_PUSH_LIT_S, c[0]->v.sval);  /* var name as string */
        for (int i = 0; i < nargs - skip0; i++) lower_expr(t->c[i + skip0]);
        SM_emit_si(g_p, SM_CALL_FN, t->v.sval, nargs - skip0 + 1);
        return;
    }
  where is_mutator(fn) = strcmp(fn,"push")==0 || ..."pop"==0 || "arr_set"==0.

  Mode-2 sm_interp.c SM_CALL_FN dispatch + rt.c rt_call both need a
  tiny adjustment: when fn ∈ mutator set AND args[0] is DT_S (name),
  call raku_try_mutating_builtin_by_name(fn, args[0].s, &args[1],
  nargs-1, out) and write back via _rt_nv_fold_set on success.

  Expected uplift: rk_arrays, rk_for_array_simple, rk_for_array flip
  mode-2 (then mode-4 follows immediately given rt_set_lang now stamps
  g_lang in mode-4 too). Probably +3..5 each gate.

  After GAP 2: pre-existing segfaults in rk_subs / rk_interp /
  rk_try_catch25 (verified at baseline pre-RK-BB-3.0a) are SEPARATE
  bugs unrelated to this thread. Cluster them into a new step
  (RK-BB-SEGFAULT-CLUSTER?) or leave for later.

  THEN — RK-BB-3a (BB_ITERATE polymorphism for `for @arr -> $v`)
  as already scoped in the goal body. With \x01-string array repr
  confirmed and arr_get/elems/push working from GAP 2, RK-BB-3a is
  just the lowering pass + bb_iterate.cpp polymorphism + mode-2
  bb_exec.c BB_ITERATE polymorphism, all per the existing 4-rung
  decomposition above (3a → 3b → 3c).

⛔ END RK-BB-3.0a HANDOFF

⛔ PRIOR HANDOFF (fcac4ab3, RK-BB-3.0+3d infra) — RETAINED FOR HISTORY:
   GAP 1 SOLVED in RK-BB-3.0a (above). GAP 2 + GAP 3 still open and
   are the explicit "NEXT" in RK-BB-3.0a's handoff block.

⛔ HANDOFF — Opus 4.7, 2026-05-27, fcac4ab3 (RK-BB-3.0+3d infra landed):

INFRASTRUCTURE NOW IN PLACE:
  - src/runtime/interp/raku_builtins_byname.c (NEW, ~250 LOC):
      raku_try_call_builtin_by_name(fn, args, nargs, out) — pre-evaluated
      DESCR_t args version (the AST-based raku_try_call_builtin was dead
      code, reachable only from icn_call_builtin which itself is never
      called). Implements: elems, arr_get, raku_substr/substr,
      raku_index/index, raku_rindex/rindex, uc/lc/chars/length/raku_trim,
      raku_sort, raku_die. Plus raku_try_mutating_builtin_by_name() with
      push/pop/arr_set entry points (await lowering tweak — see GAP 2).
  - sm_interp.c SM_CALL_FN dispatch — chains raku BEFORE icn when
    g_lang == LANG_RAKU (gates on the language so Icon path bit-identical).
  - rt.c rt_call (mode-4) — same chain, parallel structure.
  - Makefile updated (RT_PIC_SRCS + cc rule).

KNOWN GAP 1 — lower_fnc emits redundant c[0]:
  Raku TT_FNC for `substr(s, 0, 5)` parses to:
    t->v.sval = "substr", c = [TT_VAR("substr"), TT_VAR("s"),
                               TT_LIT_I(0), TT_LIT_I(5)]
  lower.c:558-559 emits ALL 4 children + SM_CALL_FN nargs=4. The first
  push (var-value-of "substr") is a vestigial duplicate of the fn name —
  the by-name dispatcher then sees args = [<garbage>, "s_value", 0, 5]
  and the off-by-one means substr returns ""/FAIL instead of "hello".
  Mode-2 substr now exits rc=0 with empty output (was Error 5 — the
  chain IS firing) but still no test flips green.
  RECOMMENDED FIX (next session, first move):
    In lower.c:558-559, before the loop, detect when
      nargs >= 1 && c[0] && c[0]->t == TT_VAR && c[0]->v.sval
                 && t->v.sval && strcmp(c[0]->v.sval, t->v.sval) == 0
    and skip c[0]: `for (int i = 1; i < nargs; i++)` + SM_CALL_FN nargs-1.
    Affects ALL languages — check Icon/SNOBOL4 don't depend on the
    duplicate push (run smoke_icon + GATE-PK after the change).
  AFTER FIX, expected gate uplift (the new by-name handlers will reach
  args correctly): rk_str22, rk_subs, rk_interp, rk_try_catch25 likely
  flip in both mode-2 and mode-4. raku_sort uplifts on partial map_grep
  test. Speculative count: +4..8 each gate.

KNOWN GAP 2 — mutating ops (push/pop/arr_set) need lowering tweak:
  These mutate the variable, so the dispatcher needs the var NAME, not
  just the value. raku_try_mutating_builtin_by_name() is authored and
  ready; the lowering for TT_FNC of push/pop/arr_set must push
    SM_PUSH_LIT_S "<vname>"  BEFORE  SM_PUSH_VAR "<vname>"
  so the by-name SM/rt dispatch can recognize the leading string arg as
  a name. Mode-2 SM_CALL_FN handler needs a tiny adjustment to peel off
  args[0] as the vname and call raku_try_mutating_builtin_by_name when
  fn ∈ {push, pop, arr_set}. ~30 LOC across lower.c + sm_interp.c + rt.c.
  AFTER FIX: rk_arrays, rk_for_array, rk_for_array_simple flip mode-2;
  mode-4 follows immediately. Probably another +3..5 each gate.

KNOWN GAP 3 — for @arr -> $v still needs BB_ITERATE polymorphism:
  Even with GAP 1 + GAP 2 fixed, `for @arr -> $v` does not LOOP in mode-2;
  the Raku lower_iterate branch (lower.c:1602-1607) emits the array
  expression once and stores it to $v. The loop scaffold in lower_every
  finds no SM_BB_SWITCH and degenerates to a single pass.
  This is the original RK-BB-3a (substrate). After GAPs 1+2, the
  for-array probe still won't flip, BUT rk_arrays will (it uses indexed
  arr_get, not a for-loop). The for-loop work is its own rung.

EXECUTION ORDER FOR NEXT SESSION (recommended):
  1. Fix GAP 1 in lower.c (one branch in lower_fnc). Run all smokes +
     GATE-RK + GATE-RK4 + GATE-PK + smoke_icon. Commit only if no
     Icon/SNOBOL4 regression; the duplicate push may have been load-
     bearing somewhere — be defensive (gate the suppression on LANG_RAKU
     if needed).
  2. Verify substr/sort/elems/arr_get flip green in mode-2 and mode-4.
     Commit as RK-BB-3.0a (the part of 3.0 reachable without mutators).
  3. Fix GAP 2 (lowering tweak + 3-line SM/rt dispatcher hook for
     mutators). Commit as RK-BB-3.0b. Verify rk_arrays.
  4. Then RK-BB-3a: BB_ITERATE polymorphic for-loop substrate.
  5. RK-BB-3b/c: map/grep BB lowering.

LATENT BUG NOTED (NOT BLOCKING): raku_builtins.c lines 144, 318, 353, 399
use `call->c[1]->t == TERM_VAR` to test AST node type, but TERM_VAR=1
(Prolog term tag) while TT_VAR=5 (AST tag). Check ALWAYS FAILS; the
NAME-write-back branch in raku_subst etc. is unreachable. Not this
session's scope but worth a SNOBOL4-or-RUNTIME-side cleanup goal.

⛔ END HANDOFF

⛔ RK-BB-2 STEP 6 ✅ COMPLETE (2026-05-27, Opus 4.7, commit d08237e0):

Three surgical edits in src/lower/lower.c (only file touched, +27/-5):

(1) lower_hoist_gather_in_expr (~L2202): the Open Q5 union-clobber.
    `def->v.sval = intern(gname)` clobbered v.ival (same union), so
    lower_icn_proc_body read garbage as nparams → body_off overshot
    proc->n → NULL return on every Raku TT_SUB_DECL. Fix: v.ival = 0
    (nparams=0). Name lives in c[0]->v.sval (TT_VAR), already correct.

(2) lower_stmt RAKU+TT_SUB_DECL branch (~L1787): skip body emission
    when proc name starts with __gather_. Hoisted gather procs are
    driven via SM_BB_SWITCH(RK_GEN) at the call site; their body lives
    in the BB graph. Emitting at top-level orphaned it before main
    started → stack underflow on startup.

(3) lower_expr_inner TT_SUB_DECL case (~L1965): same defensive skip.
    SM_PUSH_NULL still emitted to preserve the contract.

Diagnostic path (probes removed before commit):
  [DBG-procbody] both main AND __gather_0 → body_irb=(nil) initially.
  [DBG-subdecl] __gather_0 had proc->n=4 children:
    [TT_VAR(5), TT_SUSPEND(50), TT_SUSPEND(50), TT_SUSPEND(50)] —
    BB graph should have been trivial to build.
  After v.ival=0 fix: body_irb=0x37bdbad0 — BB graph built.
  SM dump count: 49 → 25 after orphan-emit suppression.

NOT needed: the separate lower_raku_proc_body() the prior handoff
anticipated. lower_icn_proc_body widened in Step 1 already handles
TT_SUB_DECL correctly once nparams is right.

End-to-end verification via run_raku_via_x86_backend.sh:
  ./scrip --compile rk_gather.raku → .s → as → ld → ./a.out
  Output: 10\n20\n30\ndone\n — byte-exact to .expected.

OPEN: RK-BB-2b — mode-2 still stack-underflows on rk_gather. bb_exec.c
has no executor for BB_SUSPEND (TT_SUSPEND case in lower_icn.c gates on
BB_LANG_RKU specifically because Icon `suspend` would break rung03 if
BB_SUSPEND emitted with no mode-2 handler). Adding a mode-2 BB_SUSPEND
executor is a separate cross-language session (Icon-shared) — see the
gating comment in lower_icn.c TT_SUSPEND case (~L651).

NEXT: RK-BB-3 — lazy map/grep as Seq CONSUMERS. BB_ITERATE consumer +
γ-port predicate test for grep. Migrate lower.c:1872-1881 off eager
SM_CALL_FN raku_map / raku_grep for the lazy path. Reuse bb_iterate.cpp
(Icon proved most cases). Verify rk_map_grep_sort24.raku under --compile.

⛔ RK-BB-3 SUBSTRATE AUDIT (2026-05-27, Opus 4.7, post-RK-BB-2 session):

Findings from inspecting rk_map_grep_sort24's failure path: six substrate
gaps make RK-BB-3 a multi-rung effort, NOT a one-commit "reuse bb_iterate".
See the full memo embedded under "Ladder steps → RK-BB-3" above for:
  - 6 gaps verified by probing (bb_iterate is DT_S-only template AND
    DT_S-only mode-2 executor; lower_iterate RAKU branch doesn't loop;
    Raku arrays are Icon-list DT_DATA not DT_A; raku_*/arr_* builtins
    aren't rt_* symbols and rt_call has no raku-chain; BB_LIST_BANG
    mode-4 template is also still bb_icn_stub).
  - 4-rung decomposition: 3a (polymorphic BB_ITERATE substrate) →
    3b (map) → 3c (grep) → 3d (sort reachability).
  - 3 open questions for Lon (Q1 polymorphic kind, Q2 FIELD_GET_fn in
    template, Q3 eager vs lazy materialization on `my @x = map { ... }`).

This session added test/raku/rk_for_array_simple.raku + .expected (RK-BB-3a
probe). Mode-4: 9/31 (+1 fail by added test). Mode-2: 8/31. All gates HOLD.
NO commits this session — design memo only; waiting on Q1/Q2/Q3 directives.
```

## Open questions for Lon

ALL FOUR RESOLVED (2026-05-27, Lon): 100% template emission via BB/SM/XA only.

1. ~~`lower_gather_hoist_pass` retarget (Path α) vs replace (Path β)?~~
   **→ Path β** (direct BB_SUSPEND lowering — cleaner BB graph; eager-SM
   intermediate would need unwinding later).
2. ~~`bb_upto.cpp` REUSE — literal vs structural?~~ **→ Structural.**
   Write new `bb_suspend.cpp` using `bb_upto.cpp`'s loop+yield as reference.
3. ~~Junction Boolean-collapse — shared `BB_ALTERNATE` guard vs SM wrapper?~~
   **→ Shared `BB_ALTERNATE` with `lang==BB_LANG_RKU` guard.** Port logic
   belongs in the template.
4. ~~GOAL-RAKU-PAT-BB — stub now vs defer?~~ **→ Defer.** Wait for
   SNOBOL4-BB and PROLOG-BB BB_SCAN/BB_ONCE machinery to mature.

NEW open item (deferred to a separate session):

5. **Union-clobber proper fix.** TT_SUB_DECL currently uses `v.ival` for
   nparams AND wants `v.sval` for name. Move nparams to a side-channel
   (leading TT_VLIST child, TT_ATTR, or separate tree_t field) so
   `v.sval = name` semantics is restored, and retire the polyglot.c c[0]
   fallback. Touches every TT_SUB_DECL reader.

RK-BB-3 open items (gating RK-BB-3a; full context in the in-line memo
under "Ladder steps → RK-BB-3"):

6. **Polymorphic BB_ITERATE or new BB_ARR_ITERATE kind?** Recommend
   polymorphic (DT_S | DT_DATA-list branch) per "kinds are
   language-agnostic." Icon's DT_S template path stays bit-identical;
   DT_DATA is purely additive.

7. **FIELD_GET_fn call from inside a BB template** — does this fit the
   "no port-logic helpers" rule? FIELD_GET_fn is a data-fetch, not
   α/β/γ/ω routing. Treating as allowed unless flagged.

8. **`my @x = map { ... } @y` materialization** — eager-drain into a
   fresh list (one rung less, mode-2 keeps working unchanged) or stay
   lazy as a Seq box (truer to Raku, needs `icn_type="seq"` DT_DATA
   carrying the BB graph)? Recommend eager-drain for RK-BB-3b; lazy is
   a future rung.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
