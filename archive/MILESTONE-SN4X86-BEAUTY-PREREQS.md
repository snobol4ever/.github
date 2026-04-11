# MILESTONE-SN4X86-BEAUTY-PREREQS.md — Beauty Suite Prerequisites

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-09
**Goal:** All 19 beauty driver tests pass before attempting beauty self-hosting.
**Depends on:** B-1 ✅ B-2 ✅ P2 ✅ (tilde, &ALPHABET, LABEL_DONE)
**Blocks:** MILESTONE-SN4X86-BEAUTY.md B-3

Run command (all 19):
```bash
cd /home/claude/one4all
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
INC=/home/claude/corpus/programs/snobol4/demo/inc
PASS=0; FAIL=0
for sno in "$BEAUTY"/beauty_*_driver.sno; do
    name=$(basename "$sno" .sno)
    ref="$BEAUTY/${name}.ref"
    [ ! -f "$ref" ] && continue
    got=$(SNO_LIB="$INC" timeout 10 ./scrip --ir-run "$sno" 2>/dev/null)
    [ "$got" = "$(cat $ref)" ] && { echo "PASS $name"; PASS=$((PASS+1)); } \
                                || { echo "FAIL $name"; FAIL=$((FAIL+1)); }
done
echo "--- PASS=$PASS FAIL=$FAIL"
```

**Baseline (2026-04-09h+1):** PASS=10 FAIL=9

---

## BP-0 — &STLIMIT / &STCOUNT wired in ir-run loop

**Status:** ✅ COMPLETE (bea4045f) — execute_program + call_user_function hardcoded limits removed; sno_err_is_terminal break wired
**Priority:** FIRST — needed for all debugging of infinite loops

`kw_stlimit` and `kw_stcount` are declared in `snobol4.h` and exist in `snobol4.c`
but are **never checked in the top-level ir-run statement loop** in `scrip.c`.
The inner `call_user_function` loop has a hardcoded `step_limit = 5000000` but
the top-level loop has no guard at all.

### Fix
In `scrip.c`, the top-level `--ir-run` statement dispatch loop (around line 107
and the main run loop):

```c
extern int64_t kw_stlimit;
extern int64_t kw_stcount;
```

At the top of each statement iteration:
```c
kw_stcount++;
if (kw_stlimit > 0 && kw_stcount > kw_stlimit) {
    fprintf(stderr, "** Termination by statement limit (%lld)\n",
            (long long)kw_stlimit);
    break;
}
```

Also wire `&STLIMIT` read/write in `NV_GET_fn`/`NV_SET_fn` if not already done.

### Gate
```bash
cat > /tmp/stlimit_test.sno << 'EOF'
        &STLIMIT = 5
loop    :(loop)
END
EOF
./scrip --ir-run /tmp/stlimit_test.sno 2>&1 | grep "Termination"
# → ** Termination by statement limit (5)
```

---


## Sprint tracking

| Bug | Status | Affects | Notes |
|-----|--------|---------|-------|
| BP-0 &STLIMIT wired | ⬜ | debugging | First — enables loop diagnosis |
| BP-1 DATA field NAMEPTR | ⬜ | stack/counter/ShiftReduce/semantic/TDump | Central fix |
| BP-2 null DT_E source | ⬜ | Gen/beauty self-host | Trace upstream |
| BP-3 empty-string prefix | ⬜ | Qize/XDump | Likely follows BP-2 |
| BP-4 omega DATATYPE | ⬜ | omega | Standalone |

**Gate:** PASS=19/19 → proceed to MILESTONE-SN4X86-BEAUTY.md B-3
