# FINDING — table_size_replace_1 (SplitWords) SIGSEGV cured: `zd_omega_test_kind()` was missing
IR_IDENT/IR_DIFFER, the same "spelled-twice list" class as FINDING-2026-08-22-seat07-ir-ident-differ-inline.md

**seat16 (`/home/claude16`, Claude Sonnet 5), 2026-09-04, THE LOOP row
`snocone-table-size-replace-1-splitwords-segv-on-procedure-return` (baton minted by seat02, resumed
via `s4e_msg.sh next` off a stale FLEET-16 claim from earlier the same day; four prior sessions —
seat02, seat05, seat01, and seat02 again — had each investigated and released this row unfixed,
citing the risk of shipping a guess against this exact shared γ/ω-pop mechanism without a full
regression gate; see their trail in the task file's LEDGER, preserved below this row's new NEXT).**

## ROOT CAUSE

`zd_omega_test_kind()` (`src/emitter/emit.cpp:2510`) is the allowlist that decides which IR node
kinds are eligible to be the source of an "omega head" — i.e. which nodes' `ω` (fail/concede) edges
`zd_omega_head()`/`zd_omega_seed()`/`zd_omega_test_idx()` will chase to discover code that needs its
own `zd_plan()` run:

```c
static int zd_omega_test_kind(IR_e op) { ...
    return (op == IR_CMP_TEST || (_tf && op == IR_BINOP_TEST)) ? 1 : 0; }
```

Only `IR_CMP_TEST` (numeric/general comparison) and, behind a killswitch, `IR_BINOP_TEST` were
listed. **`IR_IDENT`/`IR_DIFFER` — the string/pattern identity-comparison boxes SNOBOL4/Snocone
lower `IDENT(a,b)`/`DIFFER(a,b)` and `if`/`else` string-equality tests into — were never added.**

Consequence, traced end-to-end on the real witness (not a synthetic one): SplitWords' `if
IDENT(c,' ') {...} else { w = w && c }` compiles so that the `else` body (`w = w && c`, IR nodes
45–48 in one representative compile) is reached only via the IDENT box's omega/recede edge. Because
`zd_omega_test_kind(IR_IDENT)` returned 0, `zd_omega_head()` never recognized node 45 as a valid
head, so **pass 1 of `zd_plan()`'s two-pass sweep (`emit.cpp:2543-2546`) never claims/plans nodes
45-48 at all** — confirmed directly: a temporary diagnostic at the pass-1 admission check
(`emit.cpp:2546`) printed `isomegahead=0` for hi=45 on every invocation, and grepping the full
`SCRIP_ZD_DIAG=1` log for `h=45` returned zero lines (no run was ever built for it, not even a
REFUSED one).

That orphaned status is what breaks the compensator math one hop earlier: node 28 (the last box
before the recede into node 45) computes its release amount (`zwpop`) via the "omega target already
`zon`" cross-reference (`oback`, `emit.cpp:2610`/`2619`/`2623`). Since node 45 is never `zon`, `oback`
resolves to -1 and the code falls back to the *unconditional* formula `zout[i]-K` (`zout[28]-16 =
144`), instead of the cross-claim formula it should have used had node 45/49 been planned
(`zout[i]-K-_obpre`, which — using the REAL planned `zout[49]=416` from claim 17's own run —
evaluates to `-256`). The emitted instruction is `add rsp, 144` where the iteration needs `add rsp,
-256` (`src/emitter/emit.cpp` via `x86_asm.h`'s `x86_omega`, visible in the compiled `.s` at
`n28_var_β: ...; add rsp, 144; jmp n45_var_α`).

**The result is a per-branch-taken stack-depth invariant violation, not a one-off wrong offset.**
Measured directly with `gdb` (`nexti`-level instruction trace, `stepi` avoided to skip over runtime
calls) across real loop iterations of `table_size_replace_1`'s witness input (`'the cat sat on the
mat the cat'`, 30 chars, 7 spaces):

- An iteration that takes the `else` (IDENT-fails, ordinary character) path nets **+400 bytes**
  released, start-of-iteration (`n30_ident_α` entry) to start-of-next-iteration.
- An iteration that takes the `then` (IDENT-succeeds, space found) path nets **+0 bytes**.
- Both paths reach the shared rejoin point (`n49_var_α`, the loop's `i = i + 1` step) at the
  **identical absolute `rsp`** every time (confirmed: both traces hit `n49_var_bx` at
  `0x7ffffffedfe0` in one continuous gdb session) — so the shared tail code itself is *not* where the
  bug lives; the divergence is entirely in what each branch does *before* that rejoin, and it happens
  to cancel out exactly at that one checkpoint while leaving the two branches at different depths
  relative to where they started.
- A data-dependent-trip-count loop can only be statically compiled correctly if **every** iteration,
  regardless of which internal branch fires, returns to the trip-count-independent SAME depth
  (canonically zero net) — `zd_plan()`'s own "run" (claim 17, built by chasing `γ` edges from the
  statement head, i.e. modelling the `then`/succeed path) already encodes that assumption: the `then`
  path's own accounting nets exactly 0, matching the model. The `else` path's stray `+400` is what
  breaks the invariant. Over `23` non-space characters in the witness that is `23*400 = 9200` bytes
  over-released by the time the loop exits, so `SplitWords_γ`'s `mov rcx, qword ptr [rsp+920]`
  epilogue read (the exact instruction the task's GOAL names as the crash site) lands 9200 bytes away
  from the real continuation-descriptor slot → garbage → the observed SIGSEGV in `mov rcx, [rcx+8]`.
- This also explains, precisely, the ablation ladder in the task LEDGER without any new guesswork:
  witness #12 (`EQ(i,99)`, numeric, always false) is `IR_CMP_TEST` — already on the allowlist — and
  works. Witness #13 (`IDENT(c,' ')`, always false for its no-space input) and #14 (`DIFFER`) are not
  on the allowlist and crash *even taking the "else" path on every single iteration*, which is the
  tell that this was never really about "IDENT vs DIFFER" or "which branch is more common" — a
  *uniformly* wrong per-iteration net is exactly as broken as a mixed one, for a variable-trip-count
  loop.

## WHY THE PREVIOUS FOUR SESSIONS' LEADS WERE CLOSE BUT NOT IT

The live `## NEXT` this row carried (seat01, narrowing seat05's lead) suspected
`emit.cpp:2622`'s `zgpop[i] = (gback >= 0) ? (_wzdepth - _gbpre) : (...)` — the *gamma* side of the
same file — missing a `claim[gback]==claim[i]` guard mirroring the one the omega side already has at
`emit.cpp:2644`. **That node (30, `IR_IDENT` itself) was a red herring.** Re-diagnosed with an
extended `SCRIP_ZD_DIAG` printf (`claim=/cg=/co=` added to both the pass-1 `[ZD]` and pass-2
`[ZD-FINAL]` lines, reverted before this fix landed — see LEDGER) confirmed `claim[gback]==claim[i]`
already holds for node 30 (both 17): the branch is never even reached, because `gin` is correctly
`true` for node 30 (its γ target, node 31, genuinely is the next admitted node in the very same run —
found via the plain in-run scan at `emit.cpp:2609`, `k > r`, nothing to do with the cross-run `zon`
backscan at all). `gpop=0` for node 30 is the *correct*, untouched default for a genuine in-run edge,
not a computed-and-wrong value — the misleading part was that `SCRIP_ZD_DIAG`'s `[ZD-FINAL]` block
recomputes `gback`/`oback` for *every* `zon`'d node globally regardless of whether the surrounding
`if (!zgin[i])` will ever use them, so a `gback=31` prints right next to `gpop=0` for node 30 even
though that `gback` value is never read for that node — exactly the "same small integers recur across
unrelated statements" trap seat05's own LEDGER entry warned future readers about, just one layer
subtler (same invocation, unused value, not a different invocation).

seat01's actual proposed fix — mirror the omega side's `claim[oback]==claim[i]` idea onto the gamma
side — was directionally reasonable engineering caution but aimed at the wrong node; it would not
have moved this witness at all (verified: `SCRIP_ZD_BACKEDGE=0`, which disables the entire
gback/oback mechanism on *both* sides, was already ruled out by seat05 and re-confirmed here — the
crash is identical with it on or off, because the real defect is upstream of that mechanism entirely:
node 45 is never planned, so there is no `zon`'d target for *any* backedge scan, guarded or not, to
find).

## THE FIX

One line, `src/emitter/emit.cpp:2510`:

```c
-    return (op == IR_CMP_TEST || (_tf && op == IR_BINOP_TEST)) ? 1 : 0; }
+    return (op == IR_CMP_TEST || op == IR_IDENT || op == IR_DIFFER || (_tf && op == IR_BINOP_TEST)) ? 1 : 0; }
```

No new globals, no killswitch added (matching `IR_CMP_TEST`'s own unconditional treatment, not
`IR_BINOP_TEST`'s gated one — IDENT/DIFFER are core always-on SNOBOL4/Snocone primitives, not an
experimental feature). Scope deliberately minimal: only the two ops this witness's ablation
demonstrates are affected; no other `CMP_TEST`-shaped opcode is added speculatively.

This is the same defect *class* `FINDING-2026-08-22-seat07-ir-ident-differ-inline.md` already named
and fixed twice (the `zw_carve_k` `_spine` exclusion list, and `zd_nops`'s operand-count ternary) —
a classification list that lists `IR_CMP_TEST` as the closest sibling and was never taught the two
newer opcodes. `zd_omega_test_kind()` is a third instance of the same shape, evidently added to the
codebase after that finding's slice landed (it is part of the newer ζ-backedge-detection layer), so
it never got the memo. **Future opcode work in this family should grep `zd_omega_test_kind` alongside
the two lists that finding already named.**

## VERIFICATION

- **This row's own DONE-WHEN**, verbatim, both modes: `green both modes`.
- **Full `test_corpus_snobol4.sh`** (incremental build, per RULES.md's pristine-build loosening):
  `✅ GATE OK: m3 PASS=1698 FAIL=0 · m4 PASS=1698 FAIL=0 SKIP=0 · MISSING=0` (master total=1736,
  xfail=61 both modes, unrelated to this row). Tree `SCRIP=8cb8e9368-DIRTY` at measurement (dirty =
  this fix, uncommitted at grading time) — `corpus=e351e9a4c .github=90c0db3b`.
- **Full Snocone master suite** (`corpus_suite_harness.py run ALL.sc ALL.ref --lang snocone --modes
  m3,m4 --by-modes-column`, the language actually touched): AST population 67/67 PASS. Run population
  216/216: `m3 pass=199 fail=0 crash=0 hang=0 xfail=17 xpass=0`, `m4` identical. Zero crash, zero fail,
  zero unexplained xpass across the *entire* suite (`table_size_replace_1` itself is inside this 199).
- **Icon master board** (`board_icon_master.sh`, shared/language-blind machinery, checked because
  `zd_omega_test_kind` is used by every frontend, not just SNOBOL4/Snocone): `✅ ICON MASTER BOARD OK:
  entries=731 at/above floor 534 · run-graded m3 PASS=569 m4 PASS=569/578 · ast-graded PASS=153/153
  (watermarks held)`. The only 4 non-pass lines are `procedure_every_to_17`/`_18` in both modes —
  pre-existing, unrelated to IDENT/DIFFER or `zd_omega_test_kind` (Icon does not lower to those two
  opcodes at all).
- **`make test`** (the full blocking gate chain, incremental build): completed; every gate that can
  fail the target passed (`strip_comments.py --check`: 384 files, 0 with a comment/blank line;
  `test_gate_our_files_are_lf.sh`: 5066 tracked files, 0 CRLF; the s4e/postoffice hermetic gates;
  `test_gate_pl_quad_regs`: 0 violations; `test_corpus_snobol4.sh` inside the chain: same
  FAIL=0 as standalone above). The two REPORTED-not-BLOCKING arms
  (`test_gate_no_xfail_survives.sh`, `board_packages.sh`) are explicitly documented in their own
  output as non-gating at this stage and are pre-existing, cross-language, unrelated to this fix
  (package board reds span Pascal/Prolog/SNOBOL4-csnobol4-compat/snoflake vendored suites).
- **No new globals.** One-line diff, zero comments added, matches C style (200-char lines, no blank
  lines).

## NOT DONE / OUT OF SCOPE

- Did not audit every other `CMP_TEST`-shaped opcode for the same gap in `zd_omega_test_kind()` —
  only IDENT/DIFFER, the two this witness demonstrates. Worth a dedicated row if another
  string/pattern comparison box is later found to share this shape (grep sibling boxes' `x86_omega`
  call sites the way `zd_wl_kind`/`zd_nops`/`_spine` were audited in the precedent finding).
- Diagnostic instrumentation added mid-investigation (extra `claim=/cg=/co=` fields on the
  `SCRIP_ZD_DIAG` prints, a temporary `[ZD-OH]` pass-1 admission printf) was reverted before this fix
  landed — not shipped, kept the diff to the one real line. The pre-existing `gin=/oin=/gback=/oback=`
  extension to `[ZD]` left uncommitted by seat01/seat05 was left as-is (harmless, diagnostic-only,
  matches this file's existing `SCRIP_ZD_DIAG` culture).
