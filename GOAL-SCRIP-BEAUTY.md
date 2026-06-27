# GOAL-SCRIP-BEAUTY — Scrip Beauty Suite

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** all 19 beauty drivers pass `scrip --run`

## Baseline

- SCRIP HEAD: `f23ef24c`
- `scrip --run` PASS=193/203
- Beauty suite: **14/19** passing

## Current state (session 2026-04-13, session 5)

- SCRIP HEAD: `29a703ea` (no code commits this session — diagnosis only)
- Beauty suite: **10/18** passing (regressed from 14 due to prior UNIFIED-BROKER work)
- Failing: Gen, TDump, XDump, Qize, ReadWrite, case, global, semantic

## ROOT CAUSE FOUND — ALL PATTERN CAPTURES BROKEN

**Single bug blocks all 8 failing drivers.**

`bb_box_fn` was changed to return `DESCR_t` in commit `452889dd`
(UNIFIED-BROKER U-5: "all SNOBOL4 boxes return DESCR_t"). But the SNOBOL4
box functions in `stmt_exec.c` (`bb_capture`, `bb_len`, `bb_pos`, `bb_span`,
etc.) were **never migrated** — they still return `spec_t`.

The exec_stmt Phase 3 scan loop calls:
```c
spec_t result = spec_from_descr(root.fn(root.ζ, α));
```

`root.fn` returns a `spec_t` reinterpreted as `DESCR_t`. `spec_from_descr`
checks `d.v != DT_S || !d.s` — always true on a misinterpreted `spec_t` —
so it always returns `spec_empty`. **Every pattern match fails silently.**

Confirmed by debug: `LEN(1) . letter` on `'hi'` — NAM_push fires (bb_capture
γ-port runs, child match succeeds internally), but outer scan loop sees
spec_empty and discards it. NAM_commit never reached.

## Next session — Fix bb_box_fn return type mismatch (THE fix)

**Option A (preferred — minimal, safe):** In exec_stmt Phase 3 only, cast
the return at the call site in `stmt_exec.c`:
```c
// Change Phase 3 scan loop from:
spec_t result = spec_from_descr(root.fn(root.ζ, α));
// To:
spec_t result = ((spec_t(*)(void*,int))root.fn)(root.ζ, α);
```
All box functions in `stmt_exec.c` correctly return `spec_t` — only the
call-site wrapper `spec_from_descr` is wrong. The binary/live path
(`bb_build_flat`/`bb_build_binary`) is already in the DESCR_t world and is
unaffected (it uses a separate code path that never calls `spec_from_descr`).

**Option B:** Migrate all ~20 box functions in `stmt_exec.c` to return
`DESCR_t` via `descr_from_spec(...)` wrappers. More invasive, higher risk.

**Gate after fix:** Run full beauty suite — expect recovery to 14+ passing.
Update pass count here.

## Run command

```bash
cd /home/claude/SCRIP
BEAUTY=/home/claude/corpus/programs/snobol4/beauty_suite
INC=/home/claude/corpus/programs/snobol4/demo/inc
PASS=0; FAIL=0
for sno in "$BEAUTY"/beauty_*_driver.sno; do
    name=$(basename "$sno" .sno); ref="$BEAUTY/${name}.ref"
    [ ! -f "$ref" ] && continue
    got=$(SNO_LIB="$INC" timeout 10 ./scrip --run "$sno" 2>/dev/null)
    [ "$got" = "$(cat $ref)" ] && { echo "PASS $name"; PASS=$((PASS+1)); } \
                               || { echo "FAIL $name"; FAIL=$((FAIL+1)); }
done; echo "--- PASS=$PASS FAIL=$FAIL"
```

## Steps

- [x] **S-1** — `set_and_trace()` helper in `scrip.c`; replace NV_SET_fn at assignment sites. Gate: `beauty_trace_driver` passes stdout diff against SPITBOL. *(already done before session)*

- [x] **S-2** — Replace manual `kw_stcount++`/stlimit check with `comm_stno(stno)`. Gate: STNO events appear in ready pipe. *(already done before session)*

- [x] **S-3** — Add CALL/RETURN hooks in `call_user_function()`. Gate: CALL/RETURN events appear in pipe. *(already done before session)*

- [x] **S-4** — Write `test/monitor/run_monitor_2way.sh` (SPITBOL x64 vs scrip --run, 2-party). Gate: `[2way] beauty_trace_driver → EXIT 0`. *(bootsbl built, monitor runs)*

- [x] **S-5** — Run 2-way monitor on all 5 failing drivers; capture first diverging event for each. *(done — Gen: FENCE error 248; omega: TRACE error 198; TDump: step ordering; XDump: CALL ordering)*

- [ ] **S-6** — Fix `DATA field .field(x)` returns NAMEPTR not NAMEVAL. Fixes: stack, counter, ShiftReduce, semantic, TDump.

  **Status:** *Partially investigated. TDump tests 1&2 fail: TLump(leaf,80) returns 'foo' instead of '(Name)'. Root: TValue with t='Name',v='foo' hits `IDENT(t,'Name') v(x)` branch and returns 'foo'. SPITBOL does the same but gets '(Name)' — suggests TValue/TLump DATA field ordering issue (t/v swap?) needs isolation.*

- [ ] **S-7** — Fix null DT_E upstream (ARBNO infinite loop). Gate: Gen driver passes.

  **Status:** *Gen gets `pat_cat: left is not a pattern (DT=11)` warning, then hangs/blanks on tests 5+. Monitor: SPITBOL hits error 248 (FENCE redefinition in instrumented .sno). Real bug: ARBNO upstream produces null DT_E.*

- [ ] **S-8** — Fix empty-string prefix in pattern concat. Gate: Qize + XDump pass.

  **Status:** *Qize already passes. XDump: array format `ARRAY['1']` vs `ARRAY['1:1']`, table integer keys printed as strings. Separate formatting bug in XDump pretty-printer.*

- [ ] **S-9** — Fix omega pattern DATATYPE mismatch (PATTERN vs STRING). Gate: omega passes.

  **Status:** *Root cause: `EVAL(string)` goes through `eval_node` E_FNC which calls `APPLY_fn("LEN",...)` returning STRING not PATTERN. Fix A applied (eval_code.c E_CAT uses pat_cat when DT_P), but not yet effective because eval_node E_FNC itself doesn't return DT_P. Next fix: add `g_eval_string_pat_hook` in snobol4.h set from scrip.c to route EVAL(string) through interp_eval_pat.*

- [ ] **S-10** — Fix TDump node format. Gate: TDump passes.

  **Status:** *execute_program used interp_eval (value context) for pattern slot — fixed to interp_eval_pat (commit 825f053c). *IDENT/*DIFFER now correct in pattern context. TDump still fails: TLump/TValue DATA field issue remains (S-6 dependency).*

- [ ] **S-11** — Fix ShiftReduce. Gate: ShiftReduce passes.

- [ ] **S-12** — Fix semantic driver (tests 1-3). Gate: semantic passes.

- [ ] **S-13** — Fix remaining failures identified by monitor in S-5. Gate: 19/19.

- [ ] **S-14** — Verify: all 19 beauty drivers pass. Gate: PASS=19 FAIL=0. ✅

## Next session priorities

0. **E_INDIRECT subject bug (blocks TDump + Gen)**: The real subject kind at
   execute_program runtime is NOT E_INDIRECT — the branch never fires. Add:
   ```c
   fprintf(stderr, "DBG subj kind=%d\n", s->subject->kind);
   ```
   at line ~1615 in execute_program (scrip.c) for statements with a pattern.
   E_INDIRECT enum = 58 (ir.h). Find actual kind, add matching branch.
   Suspect: prescan_defines or label_table_build transforms subject node kind.
   Once fixed, BREAK(nl) . outline nl REM . $'$B' will drain $'$B' correctly,
   unblocking TDump tests 4/5 and Gen driver.

1. **TDump S-6/S-10**: After E_INDIRECT fix, check remaining TDump failures.
   Isolate TValue/TLump DATA field ordering — `tree('Name','foo',,)` t/v positions.

2. **omega S-9**: `EVAL(string)` returns DT_S not DT_P. Add `g_eval_string_pat_hook`.

3. **Gen S-7**: After E_INDIRECT fix, trace ARBNO null DT_E source.

4. **XDump S-8**: Fix array bounds format `1` → `1:1` in XDump pretty-printer.

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full rules including handoff checklist.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```
