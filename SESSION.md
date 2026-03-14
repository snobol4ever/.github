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
| **HEAD** | `ac725e8 — artifact: beauty_tramp_session65.c — 28382 lines, 0 gcc errors, Internal Error active` |

---

## State at handoff (session 65)

Commits this session:
- `bc8a520` — fix(emit_byrd): E_VAR in pattern context → implicit deref, not epsilon
- `70e5d89` — fix(emit_byrd): ~ operator emits Shift() call for tree-stack pushes
- `ac725e8` — artifact: beauty_tramp_session65.c

**Progress this session:**
- Confirmed Src is correctly set to `"X = 1\n"` — Hypothesis A from S64 was wrong
- Root cause of infinite loop found: `E_VAR` in pattern context emitted epsilon → `nl` terminator in pat_Command silently skipped → ARBNO looped forever matching "X " repeatedly
- **Fix 1:** E_VAR now emits proper deref logic (match_pattern_at for string vars, direct call for compiled named pats). match_pattern_at: 9→122. Infinite loop gone.
- Root cause of Internal Error found: `~` (E_COND) only assigned to variable but never called `Shift()` → Reduce('Stmt',7) popped from empty value stack
- **Fix 2:** emit_imm gains `do_shift` param; emit_cond passes 1 → 48 Shift() calls now emitted
- **Current symptom:** `START\n` → Internal Error; `X = 1\n` → Parse Error; `* comment\n` → passes ✓

---

## Root cause of current failure — Internal Error on START

`START\n` parses as: label="START", epsilon*4 arm → Stmt γ at cur=5, nl matches → pat_Command γ, Reduce('Stmt',7). But Shift() calls now exist — still getting Internal Error. Possibilities:

**Hypothesis A (most likely): Shift count mismatch — not exactly 7 pushes fire for the label-only path**

Count `~` operators on the label-only path through Stmt:
```
*Label → Label = BREAK(...)~'Label'          ← 1 Shift('Label', 'START')
| epsilon~'' epsilon~'' epsilon~'' epsilon~'' ← 4 Shifts (inner group)
FENCE(*Goto | epsilon~'' epsilon~'')          ← 2 Shifts (goto section)
```
= 7 total. But *Label uses E_COND internally — does `~'Label'` fire Shift? Check if `Label = BREAK(...)~'Label'` in the *named pattern* emits Shift when called via E_DEREF.

**Hypothesis B: Shift() aply() is calling the wrong function**
`aply("Shift", args, 2)` may call the C-registered `_w_Shift` which calls snobol4_inc.c `Shift()` — that calls `push_val(tree(t,v))`. But the user-defined SNOBOL4 `Shift` function from ShiftReduce.sno is a different code path. Check which one `aply("Shift",...)` resolves to.

**Hypothesis C: X=1 → Parse Error means pat_Stmt still failing**
Even with E_VAR fix, `*Expr14` on "= 1\n" (after label "X") still fails → FENCE arm1 (`epsilon~'' *White '='~'=' *White *Expr`) needs to fire. But `*Expr14` must first succeed (or be optional). Re-examine whether the outer `*White *Expr14` arm is truly optional when Expr14 fails.

---

## ONE NEXT ACTION

```bash
# 1. Confirm which Shift is being called and that it pushes to the right stack:
grep -n "_w_Shift\|register_fn.*Shift\|define.*Shift" \
  /home/claude/SNOBOL4-tiny/src/runtime/snobol4/snobol4*.c | head -10

# 2. Add debug to count stack depth before/after Shift and before Reduce:
#    In generated C, find pat_Label's ~'Label' Shift call and pat_Stmt's
#    epsilon~'' Shift calls — add fprintf(stderr,"SHIFT fired\n") before each
#    Then before Reduce('Stmt',7) add: fprintf(stderr,"REDUCE depth=%d\n", val_stack_depth())

# 3. Check if val_stack_depth() exists or needs to be added to snobol4.h

# 4. For X=1 Parse Error: add debug inside pat_Stmt to trace which FENCE arm fires
#    and whether epsilon~'' is being reached after Expr14 fails
```

---

## Artifact convention (mandatory every session touching sno2c/emit*.c)

```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
N=66   # increment from last session
mkdir -p artifacts/trampoline_session$N
./src/sno2c/sno2c -trampoline -I$INC $BEAUTY > artifacts/trampoline_session$N/beauty_tramp_session$N.c
md5sum artifacts/trampoline_session$N/beauty_tramp_session$N.c
wc -l  artifacts/trampoline_session$N/beauty_tramp_session$N.c
```

---

## Container Setup (fresh session)

```bash
apt-get install -y m4 libgc-dev
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/.github
cd SNOBOL4-tiny && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
cd src/sno2c && make
```

---

## Build command (session 65 baseline)

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
```

---

## CRITICAL Rules (no exceptions)

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin** — engine_stub.c only (beauty_tramp_bin still uses engine.c for dynamic fallbacks — that's ok for now)
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
| 2026-03-15 | ~ emits Shift() `70e5d89` | 48 Shift calls; Internal Error persists |
