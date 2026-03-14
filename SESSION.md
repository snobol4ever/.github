# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `block-fn` (sprint 3/9 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `4a6db69 — feat(stmt-fn): M-STMT-FN — trampoline emitter wired into sno2c` |

---

## State at handoff (session 56)

Two milestones fired this session:
- M-TRAMPOLINE `fb4915e` — `trampoline.h` + 3 hand-written POC programs ✅
- M-STMT-FN `4a6db69` — `-trampoline` flag wired into `sno2c` ✅

beauty.sno → `sno2c -trampoline` → **0 gcc errors** ✅
Binary runs but outputs only 10 lines (block grouping bug — see below).

---

## ONE NEXT ACTION — Fix block grouping in `emit_trampoline_program`

**File:** `src/sno2c/emit.c`

**The bug:** Pass 2 of `emit_trampoline_program` (around line 1590) opens
`block_START` correctly but fails to close and re-open blocks for each
subsequent labeled statement. All stmts end up in one giant `block_START`.

**The fix — replace the block open/close logic in Pass 2:**

Find this section (roughly lines 1590–1625):
```c
const char *cur_block_label = NULL;
int block_open = 0;

for (int sid = 1; sid <= stmt_count; sid++) {
    Stmt *s = sid_stmt[sid];

    if (s->label && block_open) {
        E("    return block_%s; /* fall into next block */\n}\n\n",
          cs_label(s->label));
        block_open = 0;
    }

    if (!block_open) {
        if (!s->label || sid == 1) {
            if (!cur_block_label) {
                E("static void *block_START(void) {\n");
            } else {
                E("static void *block_%s(void) {\n", cs_label(cur_block_label));
            }
        } else {
            cur_block_label = s->label;
            E("static void *block_%s(void) {\n", cs_label(s->label));
        }
        block_open = 1;
    }
    ...
```

Replace with this clean version:
```c
int block_open = 0;

for (int sid = 1; sid <= stmt_count; sid++) {
    Stmt *s = sid_stmt[sid];

    /* Labeled stmt → close current block (fall through to this label) */
    if (s->label && block_open) {
        E("    return block_%s;\n}\n\n", cs_label(s->label));
        block_open = 0;
    }

    /* Open a new block if none is open */
    if (!block_open) {
        if (s->label) {
            E("static void *block_%s(void) {\n", cs_label(s->label));
        } else {
            E("static void *block_START(void) {\n");
        }
        block_open = 1;
    }

    E("    { void *_r = stmt_%d();\n", sid);
    E("      if (_r != _tramp_next_%d) return _r; }\n", sid_uid[sid]);
}

/* Close final block */
if (block_open) {
    E("    return block_END;\n}\n\n");
}
```

**Test sequence after fix:**
```bash
cd /home/claude/SNOBOL4-tiny/src/sno2c && make -B

INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
R=/home/claude/SNOBOL4-tiny/src/runtime
SNO=/home/claude/snobol4-install/bin/snobol4

# 1. Regenerate
./sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c

# 2. Compile
gcc -O0 -g -I. -I$R -I$R/snobol4 /tmp/beauty_tramp.c \
    $R/snobol4/snobol4.c $R/snobol4/snobol4_inc.c \
    $R/snobol4/snobol4_pattern.c $R/engine_stub.c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
echo "gcc exit: $?"

# 3. Run
/tmp/beauty_tramp_bin < $BEAUTY > /tmp/beauty_tramp_out.sno
echo "bin exit: $?  lines: $(wc -l < /tmp/beauty_tramp_out.sno)"

# 4. Oracle
$SNO -f -P256k -I$INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno

# 5. Diff
diff /tmp/beauty_oracle.sno /tmp/beauty_tramp_out.sno
# Expect: empty → M-BEAUTY-FULL fires
```

**Commit when diff is empty:**
```
feat: M-BEAUTY-FULL — beauty.sno self-beautifies through trampoline compiled binary
```

---

## Artifact convention (mandatory every session touching sno2c/emit*.c)

```bash
# At END of session:
./sno2c -trampoline -I$INC $BEAUTY > artifacts/beauty_tramp_sessionN.c
# Record md5, line count, gcc errors, active bug in artifacts/README.md or per-session dir
# Commit: artifact: beauty_tramp_sessionN.c — <one-line status>
```

Also commit interesting test .sno + generated .c pairs in `artifacts/trampoline_sessionN/`.

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
| 2026-03-14 | block grouping bug found | block_START absorbs all stmts |
