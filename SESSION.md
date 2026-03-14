# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-first` — fix runtime bugs → M-BEAUTY-FULL |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `93e0fdb` — fix(runtime): engine_stub T_FUNC/T_CAPTURE; SPAT_USER_CALL primitive builtins; UCASE/LCASE/digits pre-init |

---

## ⚡ SESSION 83 FIRST PRIORITY

### The one job:
Trace `_c` type in pp_Stmt to find why `c[N]` subscript returns wrong value.

**Exact next action:**
```bash
# After cloning and building, patch beauty_tramp.c line ~10291:
# Find: set(_c, _v803); var_set("c", _c);
# Add immediately after: fprintf(stderr, "DBG _c type=%d\n", _v803.type);
# Then run: echo " OUTPUT = 'hello'" | /tmp/beauty_tramp_bin 2>&1
```

Expected: `_c type=6` (ARRAY=6). If different, that's the bug.

**If _c is ARRAY (type=6):** the bug is in `_aref_impl` — it checks `arr.type == ARRAY` 
but `_c` may be getting the UDEF tree node (type=9 UDEF) not the children SnoArray.
Trace: `aply("c", {x}, 1)` where `x` is the pp dispatch argument — does it return 
the SARRAY children or the whole tree UDEF?

**If _c is UDEF (type=9):** `aply("c", {x}, 1)` is returning the tree node itself.
The `c` field accessor (`_b_tree_c`) must be broken — check `field_get` finds field "c" 
in the "tree" UDEF type (fields: t, v, n, c — index 3).

---

## Build command

```bash
apt-get install -y libgc-dev
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
make -C src/sno2c

RT=src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

src/sno2c/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g /tmp/beauty_tramp.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine_stub.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
```

⚠️ engine_stub.c — NOT engine.c. engine.c is fully superseded.

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno` (790 lines, committed).

---

## Session 80 what was done

| Step | Result |
|------|--------|
| Moved build_beauty.sh | Retired to artifacts/retired/ — was linking engine.c |
| engine_stub.c | Added T_FUNC + T_CAPTURE handlers |
| snobol4_pattern.c | SPAT_USER_CALL: ANY/SPAN/BREAK/NOTANY/LEN/POS/RPOS/TAB/RTAB resolve to proper T_* nodes |
| snobol4.c runtime_init | Pre-init UCASE, LCASE, digits as physical constants |
| Parse Error | Gone — pat_Id now matches identifiers correctly |
| Output wrong | `OUTPUT = 'hello'` → outputs `OUTPUT` only. ppSubj/ppPatrn/ppRepl wrong |
| Root cause traced | `_c` set by `aply("c", {x}, 1)` at beauty_tramp.c line ~10291. Type unknown — needs trace |

---

## What works now
- Comments (`* ...`) — output correctly
- Control lines (`-INCLUDE`) — output correctly  
- Label-only lines (`START`) — silently dropped (secondary bug, fix after c[N])
- Simple assignment `OUTPUT = 'hello'` — gets to pp_Stmt, outputs label only

## Active bug: c[N] subscript wrong

**Symptom:** `indx(get(_c), {vint(2)}, 1)` in pp_Stmt returns wrong value for ppSubj.
ppLbl = ss(c[1]) outputs "OUTPUT" correctly — so c[1] returns the Label node.
But ppSubj = c[2] apparently returns something that prints as "OUTPUT" again (the label).

**Hypothesis:** `_c` holds UDEF tree node (type=9), not SARRAY (type=6=ARRAY).
If so: `_aref_impl` returns FAIL_VAL for UDEF — `_ok947` is false — ppSubj never set.
Then pp_Stmt uses stale ppSubj from previous call.

**Fix path if hypothesis correct:**
`aply("c", {x}, 1)` → `_b_tree_c` → `field_get(x, "c")` → returns fields[3] = SARRAY.
If `_b_tree_c` is not registered or field lookup fails, returns NULL_VAL.
Then `_c` = NULL_VAL, `indx(NULL_VAL, ...)` = FAIL_VAL, `_ok947` = false, ppSubj stale.

Check: does `_b_tree_c` registration in `runtime_init` happen BEFORE `inc_init`?
If `inc_init` also tries to register "c" and overwrites it, that could be the issue.

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — engine_stub.c only, engine.c fully superseded
- **ALWAYS run `git config user.name/email` after every clone**
- **ALWAYS update TINY.md and SESSION.md at HANDOFF**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-15 | 3-column format `d5b9c3c` | emit_pretty.h shared |
| 2026-03-15 | M-CNODE CNode IR `160f69b`+`ac54bd2` | proper pp/qq architecture |
| 2026-03-15 | Return to M-BEAUTY-FULL | M-CNODE done, back to main line |
| 2026-03-14 | `0113d90` pat_lit fix | emit_cnode.c build_pat E_STR strv() removed |
| 2026-03-14 | Session 78 TINY.md/SESSION.md rewrite | both were severely stale |
| 2026-03-14 | Session 80 runtime fixes | engine_stub T_FUNC/T_CAPTURE; SPAT_USER_CALL builtins; UCASE/LCASE/digits |
