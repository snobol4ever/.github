# GOAL-SCRIP-BEAUTY — Scrip Beauty Suite

**Repo:** one4all (`src/driver/scrip.c`, `snobol4dotnet`)
**Done when:** beauty.sno self-beautifies via snobol4dotnet (output matches input exactly)

## Baseline

- one4all HEAD: `f23ef24c`
- `scrip --ir-run` PASS=193/203 · beauty suite **14/19** passing (one4all)
- snobol4dotnet HEAD: `b280881` · beauty suite **7/19** passing

## Steps — one4all (scrip --ir-run)

Steps S-1 through S-5 wire TRACE/MONITOR infrastructure so the 2-way monitor can
diagnose the 5 remaining failures. Steps S-6 through S-14 fix each failure.

- [ ] **S-1** — Add `set_and_trace()` helper in `scrip.c`; replace all `NV_SET_fn(name,val)` calls at assignment sites with `set_and_trace(name,val)`. Gate: `beauty_trace_driver` passes stdout diff against SPITBOL.

- [ ] **S-2** — Replace manual `kw_stcount++`/stlimit check in ir-run loop with `comm_stno(stno)`. Gate: STNO events appear in ready pipe.

- [ ] **S-3** — Add CALL/RETURN hooks in `call_user_function()`. Gate: CALL/RETURN events appear in pipe.

- [ ] **S-4** — Write `test/monitor/run_monitor_2way.sh` (SPITBOL x64 vs scrip --ir-run, 2-party). Gate: `[2way] beauty_trace_driver → EXIT 0`.

- [ ] **S-5** — Run 2-way monitor on all 5 failing drivers (Gen, Qize, TDump, XDump, omega); capture first diverging event for each. Gate: first divergence line recorded for each.

- [ ] **S-6** — Fix `DATA field .field(x)` returns NAMEPTR not NAMEVAL (`E_NAME/E_FNC` child must call `data_field_ptr()`). Fixes: stack, counter, ShiftReduce, semantic, TDump.

- [ ] **S-7** — Fix null DT_E upstream (ARBNO infinite loop). Gate: Gen driver passes.

- [ ] **S-8** — Fix empty-string prefix in pattern concat (Qize/XDump). Gate: Qize + XDump pass.

- [ ] **S-9** — Fix omega pattern DATATYPE mismatch (PATTERN vs STRING). Gate: omega passes.

- [ ] **S-10** — Fix TDump PASS/FAIL label format. Gate: TDump passes.

- [ ] **S-11** — Fix ShiftReduce. Gate: ShiftReduce passes.

- [ ] **S-12** — Fix semantic driver (tests 1-3). Gate: semantic passes.

- [ ] **S-13** — Fix remaining failures identified by monitor in S-5. Gate: 19/19.

- [ ] **S-14** — Verify: all 19 beauty drivers pass `scrip --ir-run`. Gate: PASS=19 FAIL=0.

## Steps — snobol4dotnet

- [ ] **S-15** — FENCE redefinition: allow `DEFINE('FENCE(FENCE)')` to redefine FENCE as user function. Gate: fence + Gen + io pass → **10/19**.

- [ ] **S-16** — `ARRAY('1:0')` zero-length array allowed. Gate: tree passes → **11/19**.

- [ ] **S-17** — `DATATYPE()` returns `'name'` for NAME values. Gate: trace passes → **12/19**.

- [ ] **S-18** — `&VERSION` keyword identifies snobol4dotnet correctly. Gate: is passes → **13/19**.

- [ ] **S-19** — `FIELD(datatypeName, index)` returns field name at index for DATA-defined type. Gate: XDump passes → **14/19**.

- [ ] **S-20** — TLump node format: `(BinOp x 42)` not `.x.42`. Gate: TDump passes → **15/19**.

- [ ] **S-21** — `INPUT(.varName, unit, filename)` unit-file association for reading. Gate: ReadWrite passes → **16/19**.

- [ ] **S-22** — Fix omega driver failures (FENCE/ABORT interaction). Gate: omega passes → **17/19**.

- [ ] **S-23** — Fix semantic driver (tests 1-3). Gate: semantic passes → **18/19**.

- [ ] **S-24** — Fix ShiftReduce UNEXPECTED EXCEPTION. Gate: ShiftReduce passes → **19/19**.

## Step 25 — self-hosting (the goal)

- [ ] **S-25** — beauty.sno self-beautifies via snobol4dotnet: `dotnet Snobol4.dll -b beauty.sno < beauty.sno` output matches input. Gate: diff is empty. ✅

## Run commands

**one4all beauty suite:**
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

**snobol4dotnet beauty suite:**
```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd /home/claude/corpus/programs/snobol4/beauty
PASS=0; FAIL=0
for driver in beauty_*_driver.sno; do
    name="${driver%_driver.sno}"
    dotnet $SNO4 -b "$driver" > /dev/null 2>/tmp/err.txt || true
    grep -v "^Unhandled\|^ at \|^Aborted" /tmp/err.txt > /tmp/actual.txt
    diff -q /tmp/actual.txt "${driver%.sno}.ref" > /dev/null 2>&1 \
        && { echo "PASS $name"; PASS=$((PASS+1)); } \
        || { echo "FAIL $name"; FAIL=$((FAIL+1)); }
done; echo "$PASS/19"
```

## Commit identity

Always: `LCherryholmes` / `lcherryh@yahoo.com`
