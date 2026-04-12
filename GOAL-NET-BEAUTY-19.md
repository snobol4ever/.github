# GOAL-NET-BEAUTY-19 — snobol4dotnet Beauty 19/19

**Repo:** snobol4dotnet
**Done when:** all 19 beauty drivers pass

## Baseline

- HEAD: `b280881`
- Unit tests: 2375p/0f/2s
- Beauty suite: **7/19** passing

## State after BEAUTY-19 session

- HEAD: `7724129`
- Unit tests: 2375p/0f/2s
- Beauty suite: **11/19** passing

## Passing (11)

beauty_Gen, beauty_Qize, beauty_assign, beauty_case, beauty_counter, beauty_fence, beauty_global, beauty_io, beauty_match, beauty_stack, beauty_tree

## Run command

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

Note: OUTPUT goes to stderr. Include files must be findable from CWD —
symlink `demo/inc/*` into beauty/ once per machine.

## Steps

- [x] **S-1** — FENCE redefinition: allow `DEFINE('FENCE(FENCE)')` to redefine FENCE as user function in `Define.cs`; also allow `OPSYN('INPUT',...)` / `OPSYN('OUTPUT',...)` in `Opsyn.cs` (unblocks io.sno). Gate: fence + Gen + io pass → **10/19** ✅

- [x] **S-2** — `ARRAY('1:0')` zero-length array: allow upper bound < lower bound when using explicit `lower:upper` syntax (`hasExplicitLower` flag). Simple `ARRAY(0)` still fails error 67. Gate: tree passes → **11/19** ✅

- [ ] **S-3** — `DATATYPE()` returns `'name'` for NAME values. Gate: trace passes → **12/19**

  **NOTE:** S-3 diagnosis complete. trace fails tests 4-7 because T8Trace NRETURNs with its return variable still a NAME (not dereferenced). Attempted fix (null string on NRETURN) broke `1013_func_nreturn` — NRETURN must pass through the NAME for lvalue assignment semantics. Fix belongs in: (a) trace.sno T8Trace body should clear return var before NRETURN, OR (b) the caller's assignment path should dereference NRETURN NAMEs unless assigning to lvalue. Investigate `trace.sno` T8Trace body and SPITBOL oracle behavior next session.

- [ ] **S-4** — `&VERSION` keyword identifies snobol4dotnet correctly so `is.sno` IsSnobol4 check passes. Gate: is passes → **13/19**

- [ ] **S-5** — `FIELD(datatypeName, index)` returns field name at given index for DATA-defined type. Gate: XDump passes → **14/19**

- [ ] **S-6** — TLump node format: `(BinOp x 42)` not `.x.42`. Gate: TDump passes → **15/19**

- [ ] **S-7** — `INPUT(.varName, unit, filename)` unit-file association for reading. Gate: ReadWrite passes → **16/19**

- [ ] **S-8** — Fix omega driver (FENCE/ABORT interaction in complex patterns). Gate: omega passes → **17/19**

- [ ] **S-9** — Fix semantic driver (tests 1-3). Gate: semantic passes → **18/19**

- [ ] **S-10** — Fix ShiftReduce UNEXPECTED EXCEPTION. Gate: ShiftReduce passes → **19/19** ✅

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- See RULES.md for full rules including handoff checklist.
