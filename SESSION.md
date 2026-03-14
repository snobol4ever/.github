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
| **HEAD** | `dc8ad4b — artifact: beauty_tramp_session59.c — 27483 lines, 0 gcc errors, bare-label bug` |

---

## State at handoff (session 59)

Commits this session:
- `a3ea9ef` (TINY) — Technique 1 struct-passing: fix static re-entrancy bug ✅
- `dc8ad4b` (TINY) — artifact: beauty_tramp_session59.c ✅

**Technique 1 fully implemented.** All named pattern functions now allocate a
heap struct (`pat_X_t`) on entry==0, thread it through re-entry (entry==1).
All locals live in the struct via `#define field z->field` aliases. Child frame
pointers (`deref_N_z`) embedded in parent struct for E_DEREF calls. gcc 0 errors.

**Current state:** Binary runs. Simple statements pass (`X = 1`, `* comment`).
Bare label lines fail (`START` → Parse Error).

**Root cause pinned:** `emit_imm` (the `$ capture` operator) stores the captured
span into a local `str_t var_nl` inside the named pattern function body, but
**never calls `var_set("nl", ...)`**. So `var_get("nl")` returns empty in
`pat_Label`'s `BREAK(' ' tab nl ';')`, causing bare labels to fail.

Verified: `nl` is set by `global.sno` line 6:
```
&ALPHABET  POS(10) LEN(1) . nl
```
This is a `$ capture` (`. nl`) — it hits `emit_imm`. The do_assign block writes
`var_nl.ptr / var_nl.len` (local str_t) but never `var_set("nl", ...)`.

---

## ONE NEXT ACTION — Fix emit_imm to call var_set after capture

In `src/sno2c/emit_byrd.c`, `emit_imm`, the `do_assign` non-OUTPUT branch
(around line 970–985 after the struct-passing rewrite):

```c
/* do_assign: write span into variable */
B("%s:\n", do_assign);
// ADD THIS — push captured value into SNOBOL4 variable table:
B("    { int64_t _len = %s - %s;\n", cursor, start_var);
B("      char *_os = malloc(_len + 1);\n");
B("      memcpy(_os, %s + %s, _len); _os[_len] = 0;\n", subj, start_var);
B("      var_set(\"%s\", strv(_os)); free(_os); }\n", varname);
// KEEP or remove the str_t local (str_t is used if varname != OUTPUT)
```

**Test after fix:**
```bash
cd /home/claude/SNOBOL4-tiny/src/sno2c && make -B

INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
R=/home/claude/SNOBOL4-tiny/src/runtime
SNO=/home/claude/snobol4-install/bin/snobol4

./sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g -I. -I$R -I$R/snobol4 /tmp/beauty_tramp.c \
    $R/snobol4/snobol4.c $R/snobol4/snobol4_inc.c \
    $R/snobol4/snobol4_pattern.c $R/engine_stub.c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
echo "gcc exit: $?"

printf 'START\n' | /tmp/beauty_tramp_bin        # expect: START
printf 'X = 1\n' | /tmp/beauty_tramp_bin        # expect: X = 1

/tmp/beauty_tramp_bin < $BEAUTY > /tmp/beauty_tramp_out.sno
$SNO -f -P256k -I$INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_tramp_out.sno
# Expect: empty → M-BEAUTY-FULL fires
```

---

## Artifact convention (mandatory every session touching sno2c/emit*.c)

```bash
# At END of session:
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
mkdir -p artifacts/trampoline_sessionN
./sno2c -trampoline -I$INC $BEAUTY > artifacts/trampoline_sessionN/beauty_tramp_sessionN.c
# Record md5, line count, gcc errors, active bug in artifacts/trampoline_sessionN/README.md
# Commit: artifact: beauty_tramp_sessionN.c — <one-line status>
```

---

## Container Setup (fresh session)

```bash
apt-get install -y m4 libgc-dev
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
TOKEN=TOKEN_SEE_LON
git clone https://$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-tiny.git
git clone https://$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-corpus.git
git clone https://$TOKEN@github.com/SNOBOL4-plus/.github.git dotgithub

cp /mnt/user-data/uploads/snobol4-2_3_3_tar.gz .
tar xzf snobol4-2_3_3_tar.gz && cd snobol4-2.3.3
./configure --prefix=/home/claude/snobol4-install && make -j$(nproc) && make install
cd ..

cd SNOBOL4-tiny/src/sno2c && make
```

---

## CRITICAL Rules (no exceptions)

- **NEVER write the token into any file**
- **NEVER link engine.c in beauty_full_bin** — engine_stub.c only
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
| 2026-03-14 | beauty.sno snoXXX→XXX `d504d80` + beautifier bootstrap | oracle now self-referential |
| 2026-03-14 | S4_expression.sno→expression.sno `596cc5f` | same rename + jcooper paths fixed |
| 2026-03-14 | Technique 1 struct-passing `a3ea9ef` | re-entrancy fixed, 0 gcc errors, X=1 passes |
| 2026-03-14 | Next blocker: emit_imm missing var_set | var_get("nl") returns empty, bare labels fail |
