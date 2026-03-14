# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-first` — fix `c` field SSTR bug → START → M-BEAUTY-FULL |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `ac54bd2 — feat(cnode): sprint cnode-wire` |

## ⚡ M-CNODE FIRED — ac54bd2

All four cnode sprints complete. Zero expression lines > 120 chars.
Remaining 10 long lines are emit_byrd.c SPAN/ANY inlining + computed-goto dispatch
— not reachable by CNode. M-CNODE trigger satisfied.

**Mark M-CNODE ✅ in PLAN.md at session start.**

---

## ⚡ SESSION 77 FIRST PRIORITY: Fix `c` field SSTR bug → START → M-BEAUTY-FULL

Now that M-CNODE is done, return to the main line.

**The one job:**
1. Fix `c` field SSTR bug (one grep, one fix — see below)
2. Test: `printf 'START\n' | /tmp/beauty_tramp_bin` → should output `START`
3. Run full self-beautify diff → `diff /tmp/oracle_out.sno /tmp/compiled_out.sno`
4. Fix every diff line until diff is empty
5. Commit: **M-BEAUTY-FULL fires**

---

## Bug: START produces empty output

### Symptom
| Input | Compiled | Oracle | Status |
|-------|----------|--------|--------|
| `* comment` | `* comment` | `* comment` | ✅ |
| `START` | *(empty)* | `START` | ❌ |
| `X = 1` | `Parse Error\nX = 1` | `Parse Error\nX = 1` | ✅ |

### Root cause — confirmed session 73
- `Reduce("Stmt", 7)` fires correctly ✅
- `tree("Stmt", NULL, 7, c_array)` stores correctly ✅
- `pp(sno)` called with correct Parse tree ✅
- `pp_Parse` dispatches correctly ✅
- `pp_Parse` loops: `indx(get(_c), {vint(1)}, 1)` → **SFAIL** (type=10)
- `c.type=1` (SSTR) — `field_get` on UDEF tree node returns string not array

### Next action — Step 1 (one grep)
```bash
grep -n "field_get\|UDEF\|u->fields\|u->vals" \
    src/runtime/snobol4/snobol4.c | head -40
```

### Next action — Step 2
```bash
grep -n "register_fn.*indx\|\"indx\"" src/runtime/snobol4/snobol4.c
```

### Next action — Step 3
Check how `c[i]` in SNOBOL4 compiles in generated C:
```bash
grep -n "indx\b" /tmp/beauty_tramp.c | head -10
```

Fix is likely one of:
- `field_get` for ARRAY-valued UDEF fields serializes to string — fix to return ARRAY directly
- `indx()` not registered as builtin
- `c[i]` subscript compiles differently than `aply("indx", {c, i}, 2)`

---

## M-CNODE completed — what was done (sessions 75–76)

| Sprint | Commit | Status |
|--------|--------|--------|
| `cnode-build` | `160f69b` | ✅ `build_expr`/`build_pat`, 0 mismatches |
| `cnode-measure` | (in 160f69b) | ✅ `cn_flat_width` early-exit |
| `cnode-pp` | (in 160f69b) | ✅ `pp_cnode` inline/multiline |
| `cnode-wire` | `ac54bd2` | ✅ `PP_EXPR`/`PP_PAT` wired, long lines 68→10 |

Remaining 10 long lines: emit_byrd.c SPAN/ANY + computed-goto dispatch.
Not expr lines — M-CNODE trigger satisfied.

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
| 2026-03-15 | 3-column format `d5b9c3c` | emit_pretty.h shared |
| 2026-03-15 | multi-line concat_sv `6d9c227` | heuristic approach, superseded |
| 2026-03-15 | M-CNODE CNode IR `160f69b`+`ac54bd2` | proper pp/qq architecture |
| 2026-03-15 | Return to M-BEAUTY-FULL | M-CNODE done, back to main line |
