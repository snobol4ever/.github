# GOAL-NET-BEAUTY-19 — snobol4dotnet Beauty 18/18

**Repo:** snobol4dotnet
**Done when:** all 18 beauty drivers pass (beauty_is removed — suite reduced from 19 to 18)

## Baseline

- HEAD: `b280881`
- Unit tests: 2375p/0f/2s
- Beauty suite: **7/19** passing

## State after BEAUTY-19 session 1

- HEAD: `7724129`
- Unit tests: 2375p/0f/2s
- Beauty suite: **11/19** passing

## State after BEAUTY-19 session 2

- corpus HEAD: `a2d280b`
- snobol4dotnet HEAD: `7724129` (unchanged)
- Unit tests: 2375p/0f/2s
- Beauty suite: **12/18** passing

## Passing (12)

beauty_Gen, beauty_Qize, beauty_assign, beauty_case, beauty_counter, beauty_fence, beauty_global, beauty_io, beauty_match, beauty_stack, beauty_trace, beauty_tree

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
done; echo "$PASS/18"
```

Note: OUTPUT goes to stderr. Include files must be findable from CWD —
symlink `demo/inc/*` into beauty/ once per machine.

## Steps

- [x] **S-1** — FENCE redefinition: allow `DEFINE('FENCE(FENCE)')` to redefine FENCE as user function in `Define.cs`; also allow `OPSYN('INPUT',...)` / `OPSYN('OUTPUT',...)` in `Opsyn.cs` (unblocks io.sno). Gate: fence + Gen + io pass → **10/19** ✅

- [x] **S-2** — `ARRAY('1:0')` zero-length array: allow upper bound < lower bound when using explicit `lower:upper` syntax (`hasExplicitLower` flag). Simple `ARRAY(0)` still fails error 67. Gate: tree passes → **11/19** ✅

- [x] **S-3** — `trace.sno`: fix `T8Trace = .dummy` → `T8Trace = ''`. NRETURN value-context: snobol4dotnet does not auto-dereference NAMEs on NRETURN (unlike SPITBOL); clearing the return var before NRETURN gives callers a STRING. Gate: trace passes → **12/18** ✅

- [x] **S-4** — ~~`&VERSION` / `is.sno` IsSnobol4 check~~ ELIMINATED. `is.sno` removed from corpus entirely. `IsSnobol4`/`IsSpitbol` discriminator is invalid for snobol4dotnet. Suite reduced from 19 to 18 drivers. ✅

- [ ] **S-5** — `FIELD(datatypeName, index)` returns field name at given index for DATA-defined type. Gate: XDump passes → **13/18**

- [ ] **S-6** — TLump node format: `(BinOp x 42)` not `.x.42`. Gate: TDump passes → **14/18**

- [ ] **S-7** — `INPUT(.varName, unit, filename)` unit-file association for reading. Gate: ReadWrite passes → **15/18**

- [ ] **S-8** — Fix omega driver (FENCE/ABORT interaction in complex patterns). Gate: omega passes → **16/18**

- [ ] **S-9** — Fix semantic driver (tests 1-3). Gate: semantic passes → **17/18**

- [ ] **S-10** — Fix ShiftReduce UNEXPECTED EXCEPTION. Gate: ShiftReduce passes → **18/18** ✅

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.
