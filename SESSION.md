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
| **HEAD** | `6467ff2 — fix(emit): compile named patterns from fn bodies + expr_contains_pattern E_IMM/E_COND` |

---

## State at handoff (session 63)

Commits this session:
- `6467ff2` — Three fixes toward M-BEAUTY-FULL:
  1. scan DEFINE fn bodies for named-pattern assignments
  2. expr_contains_pattern recurse into E_IMM/E_COND
  3. pass 0a pre-registration before emit_fn + NamedPat.emitted dedup flag

**Progress this session:**
- 112 → 196 compiled named pattern functions
- Core grammar now compiled: Parse, Command, Stmt, Label, Control, Comment, Compiland
- Leaf patterns now compiled: Function, BuiltinVar, SpecialNm, ProtKwd, UnprotKwd
- match_pattern_at calls: 82 → 33, all bch/qqdlm (genuine dynamic locals — correct fallback)
- Previous segfault (match_pattern_at stack overflow) eliminated
- New crash: pat_Expr infinite recursion — root cause fully pinned (see below)

---

## Root cause of new crash — pat_Expr infinite left-recursion

**Symptom:** `printf 'X = 1\n' | beauty_tramp_bin` → segfault at pat_Expr (stack overflow).

**Call chain:** `pat_Command → pat_Stmt → pat_Expr17 → pat_Expr (via cat_r_554_α) → pat_Expr0 → ... → pat_Expr17 → pat_Expr → ...` infinite.

**Why:** beauty.sno `Expr17 = FENCE(nPush() $'(' *Expr ...)`.
Parser produces: `E_IMM(left=nPush(), right='(')` — because `$` is binary right-associative and `nPush()` is the preceding concat element (left operand of `$`).
emit_imm treats `nPush()` as the child pattern. `nPush()` succeeds immediately (zero cursor advance), then `*Expr` is called — recursing before ever matching `(`.

**The parse tree structure:**
```
concat(
  E_IMM(left=nPush(), right=E_STR("(")),  ← $ applied to nPush()
  concat(*Expr, ...)
)
```
emit_imm records start, runs `nPush()` as child (zero advance), reaches do_assign, calls *Expr — infinite.

**What SHOULD happen:**
`$'('` in Gimpel SNOBOL4 pattern concat means: match literal `(`, capture it.
The E_IMM child should be E_STR("(") — a literal match — not `nPush()`.
The parse tree reflects operator precedence: `nPush() $ '('` binds nPush() as left, `'('` as right.
But emit_imm should treat this as: run nPush() unconditionally (side-effect call, not a pattern child), then match `'('` as the actual child pattern.

**Fix strategy (ONE next action):**
In `emit_imm`, detect when left child is a user-call side-effect (E_CALL to nPush/nInc/nPop/Reduce):
- Emit the side-effect call unconditionally at α
- Then match E_STR right-side (the actual literal guard) as the child
OR: revisit whether `$'('` should be parsed differently — E_IMM(left=E_STR("("), right=nPush()) — but that would require a parse change. The emit fix is simpler.

Actually simpler fix: in emit_imm, if `child` is an E_CALL that is NOT a pattern builtin (i.e. it's a side-effect call like nPush), emit it inline as a statement (not as a pattern match), then proceed to gamma without pattern gating. This matches how the oracle C files handle nPush/nInc — they just call the function inline, no success/fail branching.

**Files to edit:** `src/sno2c/emit_byrd.c` — `emit_imm()` function around line 1081.

---

## ONE NEXT ACTION

```bash
# 1. Rebuild environment
apt-get install -y m4 libgc-dev valgrind
cd /home/claude/SNOBOL4-tiny/src/sno2c && make

# 2. In emit_byrd.c emit_imm(): detect side-effect-only E_CALL children
#    If child->kind == E_CALL && !is_pat_builtin_call(child):
#      emit child as inline call (no pattern gating)
#      then goto gamma directly (treat as epsilon match)
#    This fixes nPush() $'(' *Expr — nPush() fires, cursor unchanged,
#    then the rest of the concat matches '(' *Expr normally.
#
#    BUT: the real fix may need to be in how E_IMM child is determined.
#    The right child (E_STR "(") is what should gate. Check the actual
#    parse tree shape by adding a debug dump.

# 3. Test:
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
./sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g ... -o /tmp/beauty_tramp_bin
printf 'X = 1\n' | /tmp/beauty_tramp_bin
# Goal: no crash, output is beautified 'X = 1'
```

---

## Artifact convention (mandatory every session touching sno2c/emit*.c)

```bash
# At END of session:
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
N=64   # increment from last session
mkdir -p artifacts/trampoline_session$N
./src/sno2c/sno2c -trampoline -I$INC $BEAUTY > artifacts/trampoline_session$N/beauty_tramp_session$N.c
md5sum artifacts/trampoline_session$N/beauty_tramp_session$N.c
wc -l  artifacts/trampoline_session$N/beauty_tramp_session$N.c
# Write artifacts/trampoline_session$N/README.md
# git add artifacts/ && git commit -m "artifact: beauty_tramp_session$N.c — <status>"
```

---

## Container Setup (fresh session)

```bash
apt-get install -y m4 libgc-dev valgrind
TOKEN=TOKEN_SEE_LON
git clone https://LCherryholmes:$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-tiny.git
git clone https://LCherryholmes:$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-corpus.git
git clone https://LCherryholmes:$TOKEN@github.com/SNOBOL4-plus/.github.git snobol4-plus-github
cd SNOBOL4-tiny && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"

# CSNOBOL4 — upload snobol4-2_3_3_tar.gz and:
tar xzf snobol4-2_3_3_tar.gz && cd snobol4-2.3.3
./configure --prefix=/usr/local && make -j$(nproc) && make install
cd ..

cd SNOBOL4-tiny/src/sno2c && make
```

---

## CRITICAL Rules (no exceptions)

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin** — engine_stub.c only
- Read PLAN.md fully before coding

---

## Build command (session 63 baseline)

```bash
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
```
Note: engine.c + snobol4_pattern.c still linked for bch/qqdlm dynamic fallbacks.
Once those are resolved, switch to engine_stub.c only.

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
| 2026-03-14 | beauty.sno snoXXX→XXX `d504d80` + beautifier bootstrap | oracle now self-referential |
| 2026-03-14 | S4_expression.sno→expression.sno `596cc5f` | same rename + jcooper paths fixed |
| 2026-03-14 | Technique 1 struct-passing `a3ea9ef` | re-entrancy fixed, 0 gcc errors, X=1 passes |
| 2026-03-14 | emit_imm var_set fix `dc8ad4b` | bare labels pass (START works) |
| 2026-03-14 | Greek watermark α/β/γ/ω `f74a384` | Lon's branding in all emitted labels |
| 2026-03-14 | Three-column pretty layout `e00f851` | Lon's watermark layout |
| 2026-03-14 | Binary ~ fix + wrap fix `06f4715` | START clean, X=1 segfaults (engine stack overflow) |
| 2026-03-14 | Compile named pats from fn bodies + E_IMM fix `6467ff2` | 196 compiled pats, new crash: pat_Expr infinite recursion |
