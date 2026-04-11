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

## BP-1 — DATA field `.field(x)` returns NAMEPTR not NAMEVAL

**Status:** ⬜
**Affects:** counter, stack, ShiftReduce, semantic (4 drivers failing)

### Symptom
```
Top returned: []   (expected: 42)
```

`Top = .value($'@S') :(NRETURN)` — the dot operator on a DATA field accessor
must return a **NAMEPTR** (interior pointer into the DATA struct cell), not a
NAMEVAL (string name). Currently `NAME_fn` for `E_FNC` (field accessor calls)
returns NAMEVAL, so `NAME_DEREF` does `NV_GET_fn("value")` → looks up the
variable named "value" → gets NULVCL → empty string.

### Root cause
In `scrip.c` `E_NAME` case (~line 638):
```c
if ((child->kind == E_VAR || child->kind == E_FNC || child->kind == E_KEYWORD)
        && child->sval)
    return NAME_fn(child->sval);
```
For `.value(s)`, `child->kind == E_FNC` with `sval="value"` and `children[0]=s`.
`NAME_fn("value")` returns `NAMEVAL("value")` — no data instance involved.

### Fix
In `E_NAME` handling: when `child->kind == E_FNC`, evaluate the child arguments,
call the field accessor to get the DATA instance, then return a NAMEPTR into the
correct field slot of the DATINST_t struct.

```c
case E_NAME: {
    EXPR_t *child = e->children[0];
    if (child->kind == E_FNC && child->sval && child->nchildren == 1) {
        /* .field(x) — get interior ptr into DATA struct field */
        DESCR_t inst = interp_eval(child->children[0]);
        DESCR_t *cell = data_field_ptr(child->sval, inst);
        if (cell) return NAMEPTR(cell);
    }
    if ((child->kind == E_VAR || child->kind == E_FNC || child->kind == E_KEYWORD)
            && child->sval)
        return NAME_fn(child->sval);
    DESCR_t *cell = interp_eval_ref(child);
    if (cell) return NAMEPTR(cell);
    return FAILDESCR;
}
```

`data_field_ptr(fname, inst)` — new helper that:
1. Checks `inst.v >= DT_DATA` (is a DATA instance)
2. Looks up field index for `fname` in the DATA type definition
3. Returns `&inst.u->fields[field_idx]`

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty_stack_driver.sno 2>/dev/null
# → PASS: 1 push/top = 42
# → PASS: 2 top of 3 = 30
# → PASS: 3 pop restores 20
```
Affects: beauty_stack, beauty_counter, beauty_ShiftReduce, beauty_semantic

---

## BP-2 — Null DT_E upstream source (ARBNO infinite loop)

**Status:** ⬜
**Affects:** Gen (infinite output), beauty self-hosting (times out)

### Symptom
`pat_cat` receives `{.v=DT_E, .ptr=NULL}` — a frozen expression with null ptr.
`pat_to_patnd` returns NULL for it. Silencing with epsilon causes ARBNO to loop
infinitely (matches empty string forever).

### Diagnosis
The null DT_E is produced upstream — likely in `interp_eval` for some expression
node type that returns `{DT_E, NULL}` as a sentinel instead of NULVCL or FAILDESCR.

### Fix path
Add targeted fprintf at null DT_E creation site:
```c
/* In pat_to_patnd, after !frozen check: */
if (!frozen) {
    fprintf(stderr, "pat_to_patnd: NULL DT_E — caller must be fixed\n");
    return NULL;
}
```
Then run beauty_Gen_driver with 2s timeout and trace stderr.
Find which interp_eval path produces `{DT_E, NULL}` and return NULVCL instead.

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty_Gen_driver.sno 2>/dev/null
# → PASS: 5 Gen buffering  (no infinite output)
```

---

## BP-3 — Qize/XDump empty-string prefix in pattern concat

**Status:** ⬜
**Affects:** Qize, XDump (2 drivers)

### Symptom
```
got:  ['' 'hello']
want: ['hello']
```

Extra empty string being prepended in pattern match capture. Likely related to
BP-2 null DT_E being epsilon'd in an alternation or concat, producing an extra
empty-string capture.

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty_Qize_driver.sno 2>/dev/null
# → PASS: 2 Qize simple
SNO_LIB=.../inc ./scrip --ir-run beauty_XDump_driver.sno 2>/dev/null
# → (all pass)
```

---

## BP-4 — Omega pattern DATATYPE mismatch

**Status:** ⬜
**Affects:** omega (1 driver, test 2 and 4)

### Symptom
```
FAIL: 2 TZ xTrace=1 STRING   (expected PATTERN)
```

A value that should be DT_P (PATTERN) is arriving as DT_S (STRING).
Likely a pattern being stored then retrieved as a string — DATATYPE() returning
STRING instead of PATTERN. May be a VARVAL coercion overwriting DT_P with DT_S.

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty_omega_driver.sno 2>/dev/null
# → all PASS
```

---

## BP-5 — TDump PASS/FAIL label mismatch

**Status:** ⬜
**Affects:** TDump (1 driver)

### Symptom
```
FAIL: 1 TLump leaf got: foo     (expected: PASS: 1 TLump leaf)
FAIL: 2 TLump node got: (BinOp x 42)
```

TDump driver is outputting the tree dump value instead of the PASS string.
Suggests `IDENT` or `DIFFER` comparison in the driver is failing and the wrong
branch is taken. Likely a DATA field access issue (same root as BP-1 — TLump
uses tree fields).

Will likely be fixed by BP-1.

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
