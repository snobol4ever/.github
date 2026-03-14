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
| **HEAD** | `5d0e584 — fix(emit+emit_byrd): nl/tab init + nTop() string→ntop() + nPush beta re-push` |

---

## State at handoff (session 67)

Commits this session:
- `5d0e584` — fix(emit+emit_byrd): nl/tab init + nTop() string→ntop() + nPush beta re-push

**Three bugs found and fixed (not yet verified — container crashed before final test):**

### Fix 1 — emit.c: nl/tab init
`nl` and `tab` are used pervasively in beauty.sno patterns (BREAK(nl), Comment,
Control, Stmt termination) but never defined in any inc file beauty.sno uses.
Added `var_set("nl", CHAR(10))` and `var_set("tab", CHAR(9))` before
`trampoline_run(block_START)` in the emitted `main()`.

### Fix 2 — emit_byrd.c emit_simple_val: 'nTop()' string → INT_VAL(ntop())
In `("'Parse'" & 'nTop()')`, the `'nTop()'` is a quoted string literal.
`emit_simple_val` was emitting `STR_VAL("nTop()")` which Reduce then EVAL'd,
calling SNOBOL4-level `TopCounter()` → reads `$'#N'` linked list. But compiled
byrd boxes use C-level `npush()`/`ntop()` (`_nstack[]`). These two counter
systems never communicated — `ntop()` always returned 0, Reduce always built
zero-child trees. Fix: `emit_simple_val` intercepts `E_STR("nTop()")` and
emits `INT_VAL(ntop())` directly.

### Fix 3 — emit_byrd.c nPush beta: re-push on backtrack
Alpha path of `nPush ARBNO(*Command) Reduce nPop`:
- npush() → ARBNO(0 iters) → Reduce(0) → npop() → γ (cursor=0)
- RPOS(0) fails → backtrack to Parse β → ARBNO β tries first Command

On β re-entry, `_ntop=-1` (already popped by α-path npop). So `ninc()` inside
Command was a no-op → `ntop()=0` → Reduce always got n=0.

Fix: `nPush β` calls `npush()` (re-push) instead of going to ω. This restores
the counter frame before ARBNO extension fires.

**Status: committed but NOT run-tested.** Container crashed during final test.

---

## ONE NEXT ACTION

```bash
cd /home/claude/SNOBOL4-tiny/src/sno2c && make
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c -lgc -lm -w -o /tmp/beauty_tramp_bin
printf '* comment\n' | /tmp/beauty_tramp_bin
printf 'START\n'     | /tmp/beauty_tramp_bin
printf 'X = 1\n'     | /tmp/beauty_tramp_bin
```

Expected: `* comment` passes, `START` parses to a tree (no Internal Error),
`X = 1` may still hit Parse Error (separate issue).

If `START` still fails: add debug to verify `ntop()` value at `cat_r_846_α`
in pat_Parse. Key grep: `grep -n "INT_VAL(ntop())" /tmp/beauty_tramp.c | head`
— should show two hits at the Parse Reduce sites.

If nPush beta re-push causes infinite loop or stack overflow: the β→γ wiring
may be wrong. Alternative fix: nPush β → ω (revert fix 3) and instead emit a
fresh `npush()` call at the start of the ARBNO β block in `emit_arbno()`.

---

## Artifact convention (mandatory every session touching sno2c/emit*.c)

```bash
N=68
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > artifacts/beauty_tramp_session$N.c
md5sum artifacts/beauty_tramp_session$N.c
wc -l  artifacts/beauty_tramp_session$N.c
# commit: artifact: beauty_tramp_session68.c — <status>
```

---

## Container Setup (fresh session)

```bash
apt-get install -y m4 libgc-dev
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/.github /home/claude/snobol4-hq
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
cd src/sno2c && make
```

---

## Build command

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
| 2026-03-15 | nl/tab init + nTop() fix + nPush β `5d0e584` | 3 bugs fixed; untested — container crashed |
