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
| **HEAD** | `27325b6 — fix(emit_byrd+runtime): ARBNO beta npush restore + nhas_frame()` |

---

## State at handoff (session 69)

Commits this session:
- `6abfdf6` — fix(emit_byrd): nPush beta → omega not gamma
- `27325b6` — fix(emit_byrd+runtime): ARBNO beta npush restore + nhas_frame()

**CSNOBOL4 2.3.3 installed at `/usr/local/bin/snobol4`** — oracle available.
(Fresh container: upload snobol4-2_3_3_tar.gz, `./configure && make -j$(nproc) && make install`)

### Fix 6 — emit_byrd.c: nPush beta → omega
nPush beta was wired to gamma (→ ARBNO alpha = depth reset).
Every Parse beta re-entry reset ARBNO depth=-1 → infinite zero-iteration loop.
Fix: `PLG(beta, omega)` — nPush has no alternatives on backtrack.
Result: `X = 1` infinite loop eliminated. Oracle match: `Parse Error\nX = 1`.

### Fix 7 — ARBNO beta: conditional npush via nhas_frame()
After alpha-path `nPush→ARBNO(0)→Reduce(Parse,0)→nPop()`, `_ntop=-1`.
On ARBNO beta extension, `nInc()` inside Command was no-op (no frame).
Fix: emit `if (!nhas_frame()) npush();` at ARBNO beta entry.
Added `nhas_frame()` to `snobol4.c` + `snobol4.h`.
Result: `ntop()` now correctly returns N after N Commands.

### Remaining bug — @S stack pollution from premature Reduce(Parse,0)

**Root cause (identified, not yet fixed):**

ARBNO zero-match alpha path fires `Reduce(Parse,0)` immediately,
pushing a zero-child Parse tree onto `$'@S'` BEFORE any Command runs.
When ARBNO then extends via beta and Command runs:
- `Shift("Label","START")` pushes Label tree → `$'@S'` = [Label, zero-Parse]
- `Reduce('Stmt',7)` pops 7 items → gets [Label, zero-Parse, 5×null]
  The zero-Parse tree is CONSUMED as a Stmt child → wrong tree structure.
- `Reduce('Parse',1)` pops 1 item → gets the corrupted Stmt tree.
- `pp_Stmt` gets wrong children → outputs nothing (START case) or Parse Error.

**The fix needed:**
The `$'@S'` tree stack must be checkpointed at ARBNO entry and restored
before each extension attempt — so the zero-match Reduce side effects are
undone when ARBNO tries more iterations.

**Where to fix:**
In `emit_arbno()` in `emit_byrd.c`:
1. At ARBNO alpha entry: save `$'@S'` pointer to a local variable.
2. At ARBNO beta entry (before extending): restore `$'@S'` to the saved value,
   discarding any trees pushed by the previous shorter match.

This is analogous to how CSNOBOL4 handles generator frame checkpointing.
The save/restore uses `var_get("@S")` and `var_set("@S", saved)`.

**Pseudo-code for emit_arbno fix:**
```c
/* alpha: save @S, then zero-match → gamma */
PL(alpha, gamma, "%s_saved_stk = var_get(\"@S\"); %s = -1;", uid, depth_var);

/* beta: restore @S to saved, then extend */
PLG(beta, NULL);
PS(NULL, "var_set(\"@S\", %s_saved_stk);", uid);  // undo previous match's pushes
PS(NULL, "if (!nhas_frame()) npush();");
PS(omega, "if (++%s >= 64)", depth_var);
PS(child_α, "%s[%s] = %s;", stack_var, depth_var, cursor);
```

The `%s_saved_stk` needs to be declared as a `SnoVal` in the struct
(via `decl_add`).

---

## Test results (session 69)

| Input | Compiled | Oracle | Status |
|-------|----------|--------|--------|
| `* comment` | `* comment` | `* comment` | ✅ MATCH |
| `START` | (empty) | `START` | ❌ @S pollution |
| `X = 1` | `Parse Error\nX = 1` | `Parse Error\nX = 1` | ✅ MATCH |
| `label OUTPUT = "hello"` | `Parse Error\n...` | beautified | ❌ @S pollution |

---

## ONE NEXT ACTION

Fix `emit_arbno()` in `emit_byrd.c` to checkpoint/restore `$'@S'` at ARBNO boundaries:

```bash
# 1. Edit src/sno2c/emit_byrd.c — function emit_arbno()
# 2. Add SnoVal decl for saved stack pointer:
#    decl_add("SnoVal %s_saved_stk", uid_str);  // where uid_str = sprintf of uid
# 3. At alpha entry: save @S before zero-match fires
# 4. At beta entry: restore @S before each extension attempt
# 5. Rebuild:
cd /tmp/snobol4-tiny/src/sno2c && make
INC=/tmp/snobol4-corpus/programs/inc
BEAUTY=/tmp/snobol4-corpus/programs/beauty/beauty.sno
RT=/tmp/snobol4-tiny/src/runtime; SNO2C=/tmp/snobol4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c -lgc -lm -w -o /tmp/beauty_tramp_bin
# 6. Test:
printf '* comment\n' | /tmp/beauty_tramp_bin   # expect: * comment
printf 'START\n'     | /tmp/beauty_tramp_bin   # expect: START
printf 'X = 1\n'     | /tmp/beauty_tramp_bin   # expect: Parse Error\nX = 1
printf 'label          OUTPUT         =  "hello"\n' | /tmp/beauty_tramp_bin
# oracle: printf 'label          OUTPUT         =  "hello"\n' | snobol4 -f -P256k -I$INC $BEAUTY
```

---

## Artifact convention

Session 69 artifact: `artifacts/beauty_tramp_session69.c`
- Lines: 29932
- MD5:   c8beae48e8e072de513f15ac25eb41a4
- Compile: 0 errors
- Tests: comment ✅  START ❌(empty)  X=1 ✅  label=hello ❌

Next artifact: `beauty_tramp_session70.c`

---

## Build command

```bash
apt-get install -y m4 libgc-dev
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/.github /home/claude/snobol4-hq
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
cd src/sno2c && make
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c -lgc -lm -w -o /tmp/beauty_tramp_bin
```

---

## CRITICAL Rules (no exceptions)

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin** (beauty_tramp_bin uses engine.c — ok for now)
- **ALWAYS run `git config user.name/email` after every clone**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | M-TRAMPOLINE fired `fb4915e` | trampoline.h + 3 POC files |
| 2026-03-14 | M-STMT-FN fired `4a6db69` | trampoline emitter, beauty 0 gcc errors |
| 2026-03-14 | M-COMPILED-BYRD fired `560c56a` | engine.c dropped from compiled path |
| 2026-03-15 | DATA tree/link startup + &STLIMIT `50ef58f` | START passes; X=1 loops |
| 2026-03-15 | nPush β→ω `6abfdf6` | X=1 infinite loop eliminated |
| 2026-03-15 | ARBNO beta nhas_frame `27325b6` | ntop counts correctly; @S pollution remains |
