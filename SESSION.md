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
| **HEAD** | `5837bf1 — fix(emit_byrd+emit): quote-strip fixes` |

---

## State at handoff (session 73)

Two fixes committed and pushed (`5837bf1`). Artifact `beauty_tramp_session73.c` committed.
HQ PLAN.md updated with 3-column format requirement, save/restore Byrd box requirement,
and active `c` field bug.

**CSNOBOL4 2.3.3 NOT pre-installed** — must build from tarball at session start.
Tarball is at `/mnt/user-data/uploads/snobol4-2_3_3_tar.gz` (uploaded by Lon).
Install: `cd /tmp && tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz && cd snobol4-2.3.3 && ./configure --prefix=/usr/local && make -j$(nproc) && make install`
Then oracle is at `/usr/local/bin/snobol4`.

---

## Bug: START produces empty output — NEW ROOT CAUSE

### Symptom
| Input | Compiled | Oracle | Status |
|-------|----------|--------|--------|
| `* comment` | `* comment` | `* comment` | ✅ |
| `START` | *(empty)* | `START` | ❌ |
| `X = 1` | `Parse Error\nX = 1` | `Parse Error\nX = 1` | ✅ |

### What was fixed this session (5837bf1)
1. `emit_byrd.c` `emit_simple_val` E_STR: strips outer single-quote pair from sval.
   `STR_VAL("'Stmt'")` → `STR_VAL("Stmt")`. Root: `"'Stmt'"` double-quoted SNOBOL4 source
   stores `'Stmt'` as sval; inner quotes are delimiters, not content.
2. `emit.c` computed-goto dispatch: strips ALL quote chars from `_cg_raw` into `_cg_buf`
   before the strcmp chain. Handles `pp_'Stmt'` → `pp_Stmt`.
3. `runtime/snobol4_pattern.c` `evl()`: returns bare string for quoted literals
   (`EVAL("'Stmt'")` → `"Stmt"`). Not the root cause of START but correct fix.

### Current root cause — `c` field returns SSTR not ARRAY

**Trace confirms:**
- `Reduce("Stmt", 7)` fires with bare `t_arg=|Stmt|` ✅ (quote-strip fix working)
- `tree("Stmt", NULL, 7, c_array)` stores correctly — `t_stored=|Stmt|` ✅
- `pp(sno)` called with Parse node (UDEF type=9, t=|Parse|) ✅
- `pp_Parse` dispatches correctly ✅ (quote-strip fix working)
- `pp_Parse` loops: `indx(get(_c), {vint(1)}, 1)` returns **SFAIL** (type=10)
- `c.type=1` (SSTR) — the `c` field accessor returns a string, not the array

**Next action — exactly one step:**

```bash
# Step 1: check field_get for UDEF array-valued fields
grep -n "field_get\|UDEF\|u->fields\|u->vals" src/runtime/snobol4/snobol4.c | head -30

# Step 2: check if indx is registered as a builtin
grep -n "register_fn.*indx\|\"indx\"" src/runtime/snobol4/snobol4.c

# Step 3: check how c[i] compiles in generated C — it may use a different call path
grep -n "indx\b" /tmp/beauty_tramp.c | head -10
```

The fix is likely one of:
- (a) `field_get` for ARRAY-valued UDEF fields serializes to string — fix to return ARRAY directly
- (b) `indx()` is not registered as a builtin — register it or use the correct accessor
- (c) `c[i]` in SNOBOL4 compiles to something other than `aply("indx", {c, i}, 2)`

---

## Build command

```bash
# Install oracle (ONCE per container)
cd /tmp && tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz
cd /tmp/snobol4-2.3.3 && ./configure --prefix=/usr/local && make -j$(nproc) && make install
apt-get install -y m4 libgc-dev

# Clone repos
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git -C /home/claude/SNOBOL4-tiny config user.name "LCherryholmes"
git -C /home/claude/SNOBOL4-tiny config user.email "lcherryh@yahoo.com"

# Build sno2c
cd /home/claude/SNOBOL4-tiny/src/sno2c && make

# Generate + compile beauty_tramp_bin
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c -lgc -lm -w -o /tmp/beauty_tramp_bin

# Test
printf '* comment\n' | /tmp/beauty_tramp_bin
printf 'START\n'     | /tmp/beauty_tramp_bin   # should output: START  (currently: empty)
printf 'X = 1\n'     | /tmp/beauty_tramp_bin

# Oracle self-beautify
/usr/local/bin/snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > /tmp/oracle_out.sno
/tmp/beauty_tramp_bin < $BEAUTY > /tmp/compiled_out.sno
diff /tmp/oracle_out.sno /tmp/compiled_out.sno | head -40
```

---

## Artifact convention

Last artifact: `beauty_tramp_session73.c`
Next artifact: `beauty_tramp_session74.c` (commit after START bug is fixed)
Current generated C: 30108 lines, md5 `95c6eb104a1ab7cf5c8415c9fbbf9245`
**Artifact matches session73.c — no change needed at next session start unless sno2c changes.**

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin**
- **ALWAYS run `git config user.name/email` after every clone**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-15 | DATA tree/link startup `50ef58f` | START passes; X=1 loops |
| 2026-03-15 | nPush β→ω `6abfdf6` | X=1 infinite loop eliminated |
| 2026-03-15 | ARBNO beta nhas_frame `27325b6` | ntop counts correctly |
| 2026-03-15 | @S checkpoint ARBNO `emit_arbno` | @S stack pollution fixed |
| 2026-03-15 | @S checkpoint per-stmt `emit.c` | per-stmt @S save/restore |
| 2026-03-15 | computed goto infrastructure `e8f9e5d` | $COMPUTED:expr preserved; dispatch TODO |
| 2026-03-15 | computed goto inline dispatch `c5d5c2b` | $COMPUTED now dispatches correctly |
| 2026-03-15 | quote-strip fixes `5837bf1` | STR_VAL strips single-quotes; _cg strips quotes; evl() fixed |

---

## State at handoff (session 72)

No new commits this session — debug-only work, all in /tmp. HQ PLAN.md updated (`39ed06d`).

**CSNOBOL4 2.3.3 NOT pre-installed** — must build from tarball at session start.
Tarball is at `/mnt/user-data/uploads/snobol4-2_3_3_tar.gz` (uploaded by Lon).
Install: `cd /tmp && tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz && cd snobol4-2.3.3 && ./configure --prefix=/usr/local && make -j$(nproc) && make install`
Then oracle is at `/usr/local/bin/snobol4`.

---

## Bug: START produces empty output (confirmed, root cause fully traced)

### Symptom
| Input | Compiled | Oracle | Status |
|-------|----------|--------|--------|
| `* comment` | `* comment` | `* comment` | ✅ |
| `START` | *(empty)* | `START` | ❌ |
| `X = 1` | `Parse Error\nX = 1` | `Parse Error\nX = 1` | ✅ |

### Execution path for START (confirmed via SNO_TRACE)
1. `main00` reads `START\n` into `Line`
2. `main01`: `Line POS(0) ANY('*-')` fails → `:F(main02)`
3. `main02`: `Src = "START\n"`, then `Line = INPUT` → EOF → `:F(main05)`
4. `main05`: `Src POS(0) *Parse *Space RPOS(0)` — **succeeds**
5. `stmt_431` line 794: `DIFFER(sno = Pop())` — Pop returns **type='Parse' n=1** ✅
6. `stmt_432` line 795: `pp(sno)` — called with correct Parse tree (n=1) ✅
7. Inside `pp()`: `n(x)=1`, `type_of_x='Parse'` ✅ — pp_Parse dispatches correctly
8. `pp_Parse` → `ppWidth = ppStop[4]` → `:(pp_0)` → `i=0` → `i = LT(i,n) i+1`

### Root cause — CONFIRMED IN SESSION 72
`pp_Parse` recurses into `c[1]` (the Stmt node). The `$('pp_' t)` computed goto
dispatches for type `'Stmt'`. The issue is **somewhere in pp_Stmt or the $COMPUTED
dispatch for 'Stmt'**. The SNO_TRACE shows line 437 (`pp_1`: `pp(c[i])`) running,
then immediately returning to line 427 (pp entry) — which means the recursive
call to `pp(c[1])` either:
  (a) The `$('pp_' t)` dispatch for `'Stmt'` is not reaching `pp_Stmt`, OR
  (b) `pp_Stmt` runs but Gen() produces nothing (Gen/output system broken), OR
  (c) The Stmt tree itself has wrong structure (label node missing children)

### ONE NEXT ACTION — Session 73

**Step 1 — Add debug print in pp at line 433 dispatch:**

Find the stmt for beauty.sno line 433 in beauty_tramp.c:
```bash
grep -n "line 433" /tmp/beauty_tramp.c | head -5
```
Add a fprintf before the `$('pp_' t)` computed goto that prints the value of `t`.
This tells us what type the Stmt's child nodes have and whether dispatch is firing.

**Step 2 — Specifically: does pp_Stmt run at all?**

Add a print at `block__pp_Stmt` entry:
```bash
grep -n "block__pp_Stmt\b" /tmp/beauty_tramp.c | head -5
```
If pp_Stmt never fires, the dispatch is broken. If it fires but Gen produces nothing,
the issue is in Gen/output system.

**Step 3 — Check Stmt tree structure**

After Pop() in stmt_431, also print `c[1]` of the Parse tree:
The Parse tree has 1 child (the Stmt). Check: `t(c(sno)[1])` should be `'Stmt'`.
If it's something else, the Reduce("Stmt", 7) is wrong.

**Step 4 — If dispatch is broken: check emit.c $COMPUTED for pp_**

The `$('pp_' t)` computed goto was fixed in session 71 (`c5d5c2b`). It emits a
strcmp chain over all labels in the pp() function body. Verify the chain includes
`pp_Stmt` (and `pp_Label` etc.).

```bash
grep -A5 "pp_Stmt\|pp_Label\|strcmp.*pp_" /tmp/beauty_tramp.c | head -30
```

---

## Build command

```bash
# Install oracle (ONCE per container)
cd /tmp && tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz
cd /tmp/snobol4-2.3.3 && ./configure --prefix=/usr/local && make -j$(nproc) && make install
apt-get install -y m4 libgc-dev

# Clone repos
TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git -C /home/claude/SNOBOL4-tiny config user.name "LCherryholmes"
git -C /home/claude/SNOBOL4-tiny config user.email "lcherryh@yahoo.com"

# Build sno2c
cd /home/claude/SNOBOL4-tiny/src/sno2c && make

# Generate + compile beauty_tramp_bin
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
RT=/home/claude/SNOBOL4-tiny/src/runtime
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I$SNO2C -I$RT -I$RT/snobol4 \
    /tmp/beauty_tramp.c $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine.c -lgc -lm -w -o /tmp/beauty_tramp_bin

# Test
printf '* comment\n' | /tmp/beauty_tramp_bin
printf 'START\n'     | /tmp/beauty_tramp_bin   # should output: START  (currently: empty)
printf 'X = 1\n'     | /tmp/beauty_tramp_bin

# Oracle self-beautify
/usr/local/bin/snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > /tmp/oracle_out.sno
/tmp/beauty_tramp_bin < $BEAUTY > /tmp/compiled_out.sno
diff /tmp/oracle_out.sno /tmp/compiled_out.sno | head -40
```

---

## Artifact convention

Last artifact: `beauty_tramp_session69.c`
Next artifact: `beauty_tramp_session73.c` (commit after START bug is fixed)
Current generated C: 30108 lines, md5 `d07f3b8d5cb721c9b4ff87648d8fbfe6` (differs from session69)
**Artifact is STALE — must be committed next session after fix.**

Run artifact check per PLAN.md protocol:
```bash
LAST=$(ls /home/claude/SNOBOL4-tiny/artifacts/beauty_tramp_session*.c | sort -V | tail -1)
md5sum $LAST  # compare against current generated C
```

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin**
- **ALWAYS run `git config user.name/email` after every clone**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-15 | DATA tree/link startup `50ef58f` | START passes; X=1 loops |
| 2026-03-15 | nPush β→ω `6abfdf6` | X=1 infinite loop eliminated |
| 2026-03-15 | ARBNO beta nhas_frame `27325b6` | ntop counts correctly |
| 2026-03-15 | @S checkpoint ARBNO `emit_arbno` | @S stack pollution fixed |
| 2026-03-15 | @S checkpoint per-stmt `emit.c` | per-stmt @S save/restore |
| 2026-03-15 | computed goto infrastructure `e8f9e5d` | $COMPUTED:expr preserved; dispatch TODO |
| 2026-03-15 | computed goto inline dispatch `c5d5c2b` | $COMPUTED now dispatches correctly; snoParse/Label next |
| 2026-03-15 | Session 72 debug (no commit) | START: Parse tree n=1 correct, pp gets right tree, bug in pp_Stmt dispatch or Stmt tree structure |
