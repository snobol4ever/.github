# GOAL-SCRIP-BEAUTY — Scrip Beauty Suite

**Repo:** one4all
**Done when:** all 19 beauty drivers pass `scrip --ir-run`

## Baseline

- one4all HEAD: `f23ef24c`
- `scrip --ir-run` PASS=193/203
- Beauty suite: **14/19** passing

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

- [ ] **S-1** — Add `set_and_trace()` helper in `scrip.c`; replace all `NV_SET_fn(name,val)` at assignment sites with `set_and_trace(name,val)`. Gate: `beauty_trace_driver` passes stdout diff against SPITBOL.

- [ ] **S-2** — Replace manual `kw_stcount++`/stlimit check in ir-run loop with `comm_stno(stno)`. Gate: STNO events appear in ready pipe.

- [ ] **S-3** — Add CALL/RETURN hooks in `call_user_function()`. Gate: CALL/RETURN events appear in pipe.

- [ ] **S-4** — Write `test/monitor/run_monitor_2way.sh` (SPITBOL x64 vs scrip --ir-run, 2-party). Gate: `[2way] beauty_trace_driver → EXIT 0`.

- [ ] **S-5** — Run 2-way monitor on all 5 failing drivers (Gen, Qize, TDump, XDump, omega); capture first diverging event for each.

- [ ] **S-6** — Fix `DATA field .field(x)` returns NAMEPTR not NAMEVAL (`E_NAME/E_FNC` child must call `data_field_ptr()`). Fixes: stack, counter, ShiftReduce, semantic, TDump.

- [ ] **S-7** — Fix null DT_E upstream (ARBNO infinite loop). Gate: Gen driver passes.

- [ ] **S-8** — Fix empty-string prefix in pattern concat. Gate: Qize + XDump pass.

- [ ] **S-9** — Fix omega pattern DATATYPE mismatch (PATTERN vs STRING). Gate: omega passes.

- [ ] **S-10** — Fix TDump node format. Gate: TDump passes.

- [ ] **S-11** — Fix ShiftReduce. Gate: ShiftReduce passes.

- [ ] **S-12** — Fix semantic driver (tests 1-3). Gate: semantic passes.

- [ ] **S-13** — Fix remaining failures identified by monitor in S-5. Gate: 19/19.

- [ ] **S-14** — Verify: all 19 beauty drivers pass. Gate: PASS=19 FAIL=0. ✅

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`
