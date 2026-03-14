# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `pattern-block` (sprint 4/9 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `f05d3c4 — fix(parse+emit_byrd): ~ operator now emits E_COND+Shift — 7 Shifts fire for START` |

---

## State at handoff (session 66)

Commits this session:
- `f05d3c4` — fix(parse+emit_byrd): ~ operator now emits E_COND+Shift — 7 Shifts fire for START

**Progress this session:**
- Traced Internal Error all the way to root: `parse_expr13` was doing `(void)r` — discarding the `~ 'tag'` right-hand side entirely. No E_COND nodes were built for Label/Stmt/Goto/Comment/Control patterns. Zero Shift() calls fired.
- **Fix 1 (parse.c):** `l = binop(E_COND, l, r)` — binary `~` now builds E_COND node with tag as right child.
- **Fix 2 (emit_byrd.c):** `skip_cstatic |= do_shift` — tag strings (`'Label'`, `'comment'`, `''`) never emit invalid C statics like `_comment = STR_VAL(...)`.
- **Confirmed:** `* comment\n` → passes cleanly. `START\n` → 7 Shifts fire via `_sno_fn_Shift`, `Reduce('Stmt',7)` fires — but still "Internal Error".
- `X = 1\n` → Parse Error (separate issue, not regressed).

---

## Root cause of current failure — Internal Error on START (post-fix)

7 Shifts fire. `_sno_fn_Shift` is called correctly. `Reduce('Stmt',7)` fires.
But `sno = Pop()` still returns FAIL → `DIFFER(sno)` succeeds → `mainErr2`.

**The stack is `push()`/`pop()` via the SNOBOL4 linked-list `$'@S'` in `stack.sno`.**
`_sno_fn_Shift` calls `_sno_fn_Push(s)` which calls `Push` the SNOBOL4 function,
which does `$'@S' = link($'@S', x)`. `_sno_fn_Reduce` calls `_sno_fn_Pop()`.

**Hypothesis A (most likely): `$'@S'` indirect variable not working.**
`Push` does `$'@S' = link(...)` — this is an indirect assignment through a
string-valued variable name `'@S'`. If `var_set`/`var_get` for indirect names
`$'@S'` is broken, Push silently fails and `$'@S'` stays null. Pop then hits
`DIFFER($'@S') :F(FRETURN)` and returns FRETURN.

**Hypothesis B: `link()` DATA type not constructed correctly.**
`DATA('link(next,value)')` must be defined before `Push` runs.
`_sno_fn_InitStack` exists but is never called in the trampoline execution.
`stack.sno` has `DATA('link(next,value)') :(StackEnd)` — this runs as a
statement when the inc file is processed. Check if the trampoline emits that
DATA() call.

**Hypothesis C: `_sno_fn_Push` args wiring.**
`Push(x)` takes one arg. `_sno_fn_Shift` calls `aply("Push", {s}, 1)`.
Inside `_sno_fn_Push`, `_args[0]` should be `s`. Verify arg binding.

---

## ONE NEXT ACTION

```bash
# Add single targeted debug to _sno_fn_Push in generated C:
# Find its definition and add fprintf before/after $'@S' assignment

grep -n "_sno_fn_Push\b" /tmp/beauty_tramp_s67_clean.c | head -5
# Then sed-patch one fprintf at entry of _sno_fn_Push to print arg value
# and one after the $'@S' = link() line to print new @S value

# Also check if DATA('link(next,value)') is emitted in the trampoline:
grep -n "link\|data_define\|DATA.*link" /tmp/beauty_tramp_s67_clean.c | head -10
```

**Expected:** If `DATA('link(...)')` is missing, `link()` constructor returns
FAIL, `$'@S' = FAIL` silently no-ops, stack stays null. Fix: ensure the
`DATA('link(next,value)')` statement from stack.sno is emitted in the trampoline.

---

## Artifact convention (mandatory every session touching sno2c/emit*.c)

```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
N=68   # increment from last session
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > artifacts/beauty_tramp_session$N.c
md5sum artifacts/beauty_tramp_session$N.c
wc -l  artifacts/beauty_tramp_session$N.c
```

---

## Container Setup (fresh session)

```bash
apt-get install -y m4 libgc-dev
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/.github /home/claude/snobol4-github
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
cd src/sno2c && make
```

---

## Build command (session 66 baseline)

```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
printf 'START\n' | /tmp/beauty_tramp_bin
printf '* comment\n' | /tmp/beauty_tramp_bin
printf 'X = 1\n' | /tmp/beauty_tramp_bin
```

---

## CRITICAL Rules (no exceptions)

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin** — engine_stub.c only (beauty_tramp_bin still uses engine.c — ok for now)
- Read PLAN.md fully before coding

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | M-TRAMPOLINE fired `fb4915e` | trampoline.h + 3 POC files |
| 2026-03-14 | M-STMT-FN fired `4a6db69` | trampoline emitter in sno2c, beauty 0 gcc errors |
| 2026-03-14 | block grouping bug fixed `98ec305` | first_block flag |
| 2026-03-14 | pattern-block sprint `373d939` | 112 named pat fns, 0 gcc errors |
| 2026-03-14 | E_COND/E_IMM E_STR fix `6d09bfa` | binary compiles, runs, fails on static re-entrancy |
| 2026-03-14 | beauty.sno snoXXX→XXX `d504d80` | oracle now self-referential |
| 2026-03-14 | Technique 1 struct-passing `a3ea9ef` | re-entrancy fixed, 0 gcc errors |
| 2026-03-14 | emit_imm var_set fix `dc8ad4b` | bare labels pass |
| 2026-03-14 | Greek watermark α/β/γ/ω `f74a384` | Lon's branding |
| 2026-03-14 | Three-column pretty layout `e00f851` | Lon's watermark layout |
| 2026-03-14 | Binary ~ fix + wrap fix `06f4715` | START clean, X=1 segfaults |
| 2026-03-14 | Compile named pats from fn bodies `6467ff2` | 196 compiled pats |
| 2026-03-14 | E_DEREF + sideeffect + C-static `09e5a5d` `5e90712` | 33→9 match_pattern_at |
| 2026-03-15 | E_VAR implicit deref `bc8a520` | infinite ARBNO loop eliminated |
| 2026-03-15 | ~ emits Shift() `70e5d89` | 48 Shift calls wired; Internal Error persisted |
| 2026-03-15 | parse_expr13 E_COND fix `f05d3c4` | 7 Shifts now fire for START; * comment passes |
