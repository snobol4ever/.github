# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `cnode-build` — Sprint 1 of 4 toward M-CNODE |
| **Milestone** | M-CNODE (then M-BEAUTY-FULL) |
| **HEAD** | `6d9c227 — feat(emit): multi-line concat_sv for chains ≥3 deep` |

## ⚡ SESSION 76 FIRST PRIORITY: Sprint cnode-build

Build `emit_cnode.c` — CNode IR tree from Expr*. No output yet.

**Gate:** `flat_print(build_expr(e))` matches current `emit_expr(e)` output exactly.
Verify by generating beauty_tramp.c before and after, diffing the expression output.

---

## M-CNODE — Why and What

**The problem:** `emit_expr` is a streaming printer. No lookahead. Every long-line
fix is a local heuristic. `concat_sv(A, B)` where A and B are each long stays on
one line because chain depth=2 — the printer doesn't know the total width.

**The solution:** pp/qq split, same model as beauty.sno:
- `build_expr(e)` → CNode IR tree (no output)
- `cn_flat_width(n, limit)` → "qq" lookahead: flat width or INT_MAX
- `pp_cnode(n, fp, col, indent, maxcol)` → "pp": inline if fits, multiline if not

**Scope:** Expression trees only. Structural lines (PLG/PS/PG) stay as-is.
Seam: `E("SnoVal _v%d = ", u)` → `pp_cnode(build_expr(e))` → `E(";\n")`.

**File:** `src/sno2c/emit_cnode.c` + `src/sno2c/emit_cnode.h`

### CNode IR

```c
typedef enum { CN_RAW, CN_CALL, CN_SEQ } CNodeKind;

typedef struct CNode {
    CNodeKind    kind;
    const char  *text;      // CN_RAW: literal; CN_CALL: fn name
    struct CNode **args;    // CN_CALL: arg subtrees
    int           nargs;
    struct CNode *left, *right; // CN_SEQ
} CNode;
```

### Sprint map (4 sprints to M-CNODE)

| Sprint | What | Gate |
|--------|------|------|
| `cnode-build` ⬅ **NOW** | `build_expr` + `build_pat` → CNode tree | `flat_print` diff=0 vs current output |
| `cnode-measure` | `cn_flat_width(n, limit)` early-exit | Correct + fast |
| `cnode-pp` | `pp_cnode` inline/multiline | Valid C, 0 lines > 120 |
| `cnode-wire` | Replace emit_expr/emit_pat calls | Smoke tests pass. **M-CNODE fires.** |

---

## Sprint cnode-build — Step by step

1. Create `src/sno2c/emit_cnode.h` — CNode typedef + arena allocator + API
2. Create `src/sno2c/emit_cnode.c` — `cn_raw()`, `cn_call()`, `cn_seq()` constructors
3. Write `build_expr(Expr *e)` — mirrors `emit_expr` exactly, returns CNode* instead of printing
4. Write `build_pat(Expr *e)` — mirrors `emit_pat` exactly
5. Write `cn_flat_print(CNode *n, FILE *fp)` — flat printer for validation
6. In `emit.c`, add temporary validation shim: emit via old path AND via build_expr+flat_print, diff
7. Once diff=0, remove old path → sprint done

### Key mapping (emit_expr → build_expr)

| emit_expr | build_expr |
|-----------|------------|
| `E("NULL_VAL")` | `cn_raw(arena, "NULL_VAL")` |
| `E("strv("); emit_cstr(s); E(")")` | `cn_call(arena, "strv", cn_cstr(arena,s), 1)` |
| `E("aply(\"%s\",...)", nm)` | `cn_call(arena, "aply", args, nargs)` |
| `emit_expr(e->left); E(","); emit_expr(e->right)` | `cn_seq(arena, build_expr(e->left), cn_raw(arena,","), build_expr(e->right))` |
| `E("concat_sv("); emit_expr(l); E(","); emit_expr(r); E(")")` | `cn_call(arena, "concat_sv", [build_expr(l), build_expr(r)], 2)` |

### Arena allocator (simple bump allocator)

```c
typedef struct CArena { char *buf; size_t cap, used; } CArena;
CArena *cn_arena_new(size_t cap);   // malloc cap bytes
void   *cn_arena_alloc(CArena *a, size_t sz); // bump ptr
void    cn_arena_free(CArena *a);   // free whole arena at once
```

One arena per statement. Free after `E(";\n")` is emitted. Zero GC pressure.

---

## Bug (still active): START produces empty output

`c` field of UDEF tree node returns SSTR not ARRAY. Deferred — M-CNODE first.

---

## Build command

```bash
cd /tmp && tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz
cd /tmp/snobol4-2.3.3 && ./configure --prefix=/usr/local && make -j$(nproc) && make install
apt-get install -y m4 libgc-dev

TOKEN=TOKEN_SEE_LON
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-tiny /home/claude/SNOBOL4-tiny
git clone https://x-access-token:${TOKEN}@github.com/SNOBOL4-plus/SNOBOL4-corpus /home/claude/SNOBOL4-corpus
git -C /home/claude/SNOBOL4-tiny config user.name "LCherryholmes"
git -C /home/claude/SNOBOL4-tiny config user.email "lcherryh@yahoo.com"
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
| 2026-03-15 | 3-column format `d5b9c3c` | emit_pretty.h shared, emit.c converted |
| 2026-03-15 | multi-line concat_sv `6d9c227` | long lines 68→17 |
| 2026-03-15 | PIVOT: M-CNODE CNode IR + pp/qq | Lon: right architecture — split build from print |
