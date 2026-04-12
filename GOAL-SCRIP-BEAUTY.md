# GOAL-SCRIP-BEAUTY — Scrip Beauty Suite

**Repo:** one4all
**Done when:** all 19 beauty drivers pass `scrip --ir-run`

## Baseline

- one4all HEAD: `f23ef24c`
- `scrip --ir-run` PASS=193/203
- Beauty suite: **14/19** passing

## Current state (session 2025-04-12)

- one4all HEAD: `825f053c`
- Beauty suite: **14/18** passing (18 drivers in corpus, not 19)
- Failing: Gen, TDump, XDump, omega

## Run command

```bash
cd /home/claude/one4all
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
INC=/home/claude/corpus/programs/snobol4/demo/inc
PASS=0; FAIL=0
for sno in "$BEAUTY"/beauty_*_driver.sno; do
    name=$(basename "$sno" .sno); ref="$BEAUTY/${name}.ref"
    [ ! -f "$ref" ] && continue
    got=$(SNO_LIB="$INC" timeout 10 ./scrip --ir-run "$sno" 2>/dev/null)
    [ "$got" = "$(cat $ref)" ] && { echo "PASS $name"; PASS=$((PASS+1)); } \
                               || { echo "FAIL $name"; FAIL=$((FAIL+1)); }
done; echo "--- PASS=$PASS FAIL=$FAIL"
```

## Steps

- [x] **S-1** — `set_and_trace()` helper in `scrip.c`; replace NV_SET_fn at assignment sites. Gate: `beauty_trace_driver` passes stdout diff against SPITBOL. *(already done before session)*

- [x] **S-2** — Replace manual `kw_stcount++`/stlimit check with `comm_stno(stno)`. Gate: STNO events appear in ready pipe. *(already done before session)*

- [x] **S-3** — Add CALL/RETURN hooks in `call_user_function()`. Gate: CALL/RETURN events appear in pipe. *(already done before session)*

- [x] **S-4** — Write `test/monitor/run_monitor_2way.sh` (SPITBOL x64 vs scrip --ir-run, 2-party). Gate: `[2way] beauty_trace_driver → EXIT 0`. *(bootsbl built, monitor runs)*

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

1. **TDump S-6/S-10**: Isolate TValue/TLump DATA field ordering — `tree('Name','foo',,)` t/v positions. Check if t(x)/v(x) accessor order matches DATA spec.
2. **omega S-9**: Add `g_eval_string_pat_hook` — set in scrip.c main() to a function that calls `interp_eval_pat` on the parsed expression from cmpile_eval_expr, returning DT_P.
3. **Gen S-7**: Trace ARBNO null DT_E source.
4. **XDump S-8**: Fix array bounds format `1` → `1:1` in XDump pretty-printer.

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full rules including handoff checklist.
