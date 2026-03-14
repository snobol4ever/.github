# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-first` — fix Parse Error on `-INCLUDE` → M-BEAUTY-CORE |
| **Milestone** | M-BEAUTY-CORE (stubs first) → M-BEAUTY-FULL (real inc, second) |
| **HEAD** | `8676bd9` — refactor: restore proper English names — undo P4 misspelling technique |

---

## ⚡ SESSION 86 FIRST ACTION

### Active bug: Parse Error on `-INCLUDE` lines

beauty_core_bin outputs comment header lines correctly, then hits `Parse Error`
at the first `-INCLUDE 'global.sno'` line.

`Command` pattern tries: `*Comment` → `*Control` → `*Stmt`  
`Control = '-' BREAK(nl ';')` — should match `-INCLUDE 'global.sno'`  
`pat_Control` is compiled correctly in generated C.

**Root cause suspected:** `pat_Control` calls `BREAK` with charset built dynamically:
```c
CONCAT_fn(STRVAL(VARVAL_fn(NV_GET_fn("nl"))), STRVAL(";"))
```
`nl` is pre-initialized in `SNO_INIT_fn` — but `VARVAL_fn(NV_GET_fn("nl"))` returns
the string value of `nl`, which is `\n` (char 10). The BREAK charset is `"\n;"`.

**The real question:** is `pat_Control` even being reached and tried, or is the
FENCE in `Command` failing before it gets there? The `-INCLUDE` line starts at
column 0 (no leading space). `pat_Comment` tries `*` — fails. `pat_Control` tries
`-` — should succeed. But does `pat_Stmt` upstream require a leading space?

**Session 86 first action:**
1. Add a single `fprintf(stderr, "trying Control on: %.20s\n", _subj_np + _cur_np)`
   at `_Control_α:` in snobol4_pattern.c — NO, wrong place. Add it in the
   generated code by patching `pat_Control` directly in `/tmp/beauty_core.c`
   (don't touch source — just test the hypothesis fast).
2. Run: `printf " -INCLUDE 'x'\n" | /tmp/beauty_core_bin`
   Note the LEADING SPACE — test input always needs leading space.
3. If Control matches with leading space but not without → the issue is that
   `-INCLUDE` lines have no leading space in beauty.sno input, but the subject
   line fed to the pattern has the newline stripped and cursor starts at 0.
4. Check `mainErr1` in beauty.sno — what triggers it? Line 796 in beauty.sno.

**Oracle:** `test/smoke/outputs/session50/beauty_oracle.sno`
Oracle shows `-INCLUDE` lines ARE output — so csnobol4 handles them fine.
The first line after comments in oracle is `START` then `-INCLUDE` lines.

---

## Build commands

```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev
make -C src/sno2c

RT=src/runtime
STUBS=src/runtime/inc_stubs
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

# beauty_core (stubs — USE THIS, DO NOT switch to beauty_full)
src/sno2c/sno2c -trampoline -I$STUBS $BEAUTY > /tmp/beauty_core.c
gcc -O0 -g /tmp/beauty_core.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine_stub.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c \
    -lgc -lm -w -o /tmp/beauty_core_bin
```

⚠️ engine_stub.c — NOT engine.c  
⚠️ Test input MUST have leading space: `printf " stmt\n"` not `echo "stmt"`  
⚠️ beauty_core (stubs) FIRST — beauty_full (real inc) only after M-BEAUTY-CORE fires  

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno`

---

## What was done this session (Session 85)

### Agreement breach resolved
Session 84 broke the beauty_core/beauty_full agreement. Session 85 confirmed
`inc_stubs/` is intact (19 stubs), both binaries build clean.

### Rename audit — Session 84 SIL rename verified
Full word-for-word audit of 40+ renames. All clean. One bug found and fixed:
`ARRAY_VAL` macro used `.a` instead of `.arr` — dormant (never called), fixed.
Full audit written to HQ PLAN.md.

### M-BEAUTY-CORE / M-BEAUTY-FULL split written into HQ
PLAN.md, TINY.md, SESSION.md all updated. The two-phase agreement is now
a hard architectural rule in HQ, not just a session note.

### P4 misspelling technique fully undone
ALLCAPS_fn suffix provides its own namespace — misspellings no longer needed.
18 names restored to proper English:

| Old | New |
|-----|-----|
| APLY_fn | APPLY_fn |
| CONC_fn | CONCAT_fn |
| ccat (char*) | STRCONCAT_fn |
| RPLACE_fn | REPLACE_fn |
| evl | EVAL_fn |
| divyde | DIVIDE_fn |
| powr | POWER_fn |
| entr | ENTER_fn |
| xit | EXIT_fn |
| abrt | ABORT_fn |
| indx | INDEX_fn |
| replc | REPLACE_fn |
| mtch | MATCH_fn |
| strv | STRVAL_fn |
| vint | INTVAL_fn |
| ccat | CONCAT_fn |
| dupl (char*) | STRDUP_fn |
| ini | INIT_fn |

Also fixed: SNOBOL4 registration strings that had picked up `_fn` suffix
from Session 84 rename: `"SIZE"`, `"DUPL"`, `"TRIM"`, `"SUBSTR"`, `"DATA"`,
`"FAIL"`, `"DEFINE"`.

### Debug traces
Stripped bare debug traces from `_b_tree_c`, `APLY_fn(c)`, `MAKE_TREE_fn`.
Single trace added in `FIELD_GET_fn` — result: trace never fires on simple
input, meaning stmt_205 (which calls `APPLY_fn("c",...)`) is never reached.
Parse Error fires before the tree walk. Fix Parse Error first.

---

## Active bug: Parse Error on `-INCLUDE` lines (see SESSION 86 FIRST ACTION above)

**What is known:**
- `pat_Control` is compiled correctly: matches `-` then `BREAK(nl ';')`
- `pat_Control` IS in the generated code at line ~8960
- Simple ` OUTPUT = 'hello'` input works fine (output: `OUTPUT`)
- `-INCLUDE 'global.sno'` triggers Parse Error
- Oracle shows `-INCLUDE` lines should pass through as-is
- The FIELD_GET_fn / _c field bug is SECONDARY — unreachable until parsing works

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — engine_stub.c only
- **ALWAYS run `git config user.name/email` after every clone**
- **ALWAYS use leading space in test input:** `printf " stmt\n"` not `echo "stmt"`
- **beauty_core (stubs) FIRST — beauty_full (real inc) SECOND**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | Session 80 runtime fixes | engine_stub T_FUNC/T_CAPTURE etc |
| 2026-03-14 | Session 83 diagnosis | _c = data_define overwrites _b_tree_c (later disproved) |
| 2026-03-14 | Session 84 SIL rename | DESCR_t/DTYPE_t/XKIND_t/_fn/_t throughout |
| 2026-03-14 | Session 84 build fixes | cs_alloc, computed goto, label table, inc_stubs |
| 2026-03-14 | Session 84 HALT | broke beauty_core/beauty_full agreement — reverted to stubs |
| 2026-03-14 | Session 85 cleanup | agreement breach resolved, rename audit, P4 undo, M-BEAUTY-CORE split |
