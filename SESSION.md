# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-first` — fix runtime bugs → M-BEAUTY-FULL |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `eec84e7` — EMERGENCY WIP: SIL naming rename + beauty_core stub build clean |

---

## ⚡ SESSION 85 FIRST PRIORITY

### The agreement — beauty_core FIRST, beauty_full SECOND

beauty_core = beauty.sno compiled with `-I src/runtime/inc_stubs` (19 comment-only stub .sno files).
The stubs mean zero SNOBOL4 inc code is compiled in. `snobol4_inc.c` provides C implementations.
beauty_full = beauty.sno compiled with `-I SNOBOL4-corpus/programs/inc` (real inc files).

**Do NOT switch to beauty_full until beauty_core works end-to-end.**

### The one bug to fix:
`aply("c", {x}, 1)` on a tree node returns `DT_S` (string) not `DT_A` (array).

**Debug traces are still live in snobol4.c and snobol4_pattern.c — remove them first.**

Root cause: still undiagnosed despite multiple sessions.
`MAKE_TREE_fn` fires correctly — tree nodes ARE being built.
`APLY_fn("c", ...)` fires — `_b_tree_c` fn pointer is non-NULL.
But the return value has `.v == DT_S` instead of `.v == DT_A`.

**Session 85 first action:**
1. Strip debug traces from `_b_tree_c` and `MAKE_TREE_fn`
2. Add ONE trace inside `FIELD_GET_fn` to print `obj.v` and the returned field's `.v`
3. Build beauty_core_bin and run `printf " OUTPUT = 'hello'\n" | /tmp/beauty_core_bin`
4. Read the trace — is `obj.v == DT_DATA`? Is `fields[3].v == DT_A`?
5. If fields[3].v is already DT_S at storage time → bug is in `DATCON_fn` / `udef_new`
6. If fields[3].v is DT_A but return is DT_S → bug is in `FIELD_GET_fn`

---

## Build commands

```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev
make -C src/sno2c

RT=src/runtime
STUBS=src/runtime/inc_stubs
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

# beauty_core (stubs — USE THIS)
src/sno2c/sno2c -trampoline -I$STUBS $BEAUTY > /tmp/beauty_core.c
gcc -O0 -g /tmp/beauty_core.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine_stub.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c \
    -lgc -lm -w -o /tmp/beauty_core_bin

# beauty_full (real includes — DO NOT USE until beauty_core works)
INC=/home/claude/SNOBOL4-corpus/programs/inc
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp.c
gcc -O0 -g /tmp/beauty_tramp.c \
    $RT/snobol4/snobol4.c $RT/snobol4/snobol4_inc.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine_stub.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c \
    -lgc -lm -w -o /tmp/beauty_tramp_bin
```

⚠️ engine_stub.c — NOT engine.c
⚠️ Test input MUST have leading space: `printf " OUTPUT = 'hello'\n"` not `echo`
⚠️ Use beauty_core_bin (stubs) until _c field bug is fixed

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno`

---

## What was done this session (Session 84)

### Massive SIL naming rename — mechanical, zero semantic change

| Old | New | Notes |
|-----|-----|-------|
| `SnoVal` | `DESCR_t` | SIL descriptor |
| `SnoType` enum | `DTYPE_t` enum | SIL type field |
| enum values `SSTR`, `SINT` etc | `DT_S`, `DT_I` etc | DT_ prefix avoids C collisions |
| `SNULL` | `DT_SNUL` | |
| `SFAIL` | `DT_FAIL` | |
| `UDEF` | `DT_DATA` | user DATA types start at 100 |
| `.type` field | `.v` field | SIL v-field |
| `SPAT_LIT` | `XCHR` | SIL X-codes throughout |
| `SPAT_ARBNO` | `XARBN` | |
| `SPAT_ASSIGN_COND` | `XNME` | |
| all functions | `FUNC_fn` suffix | e.g. `APLY_fn`, `PUSH_fn`, `NV_GET_fn` |
| all typedefs | `TYPE_t` suffix | e.g. `DESCR_t`, `PATND_t`, `ARBLK_t` |
| `E_MUL` | `E_MPY` | SIL MPY proc |
| `E_ALT` | `E_OR` | SIL OR proc |
| `E_COND` | `E_NAM` | SIL NAM proc |
| `E_IMM` | `E_DOL` | SIL DOL proc |
| `E_CALL` | `E_FNC` | |

### Build fixes applied
- `cs_alloc`: emit `block%s` not `block_%s` — avoids double-underscore on labels starting with `_`
- `parse.c`: `$'literal'` goto → `$COMPUTED:'literal'` — computed goto path
- `trampoline.h`: `sno_computed_goto` + `_BlockEntry_t` + `_block_label_table`
- `emit.c`: emit `_block_label_table[]` at file scope before `main()`
- `emit.c`: emit forward decls + stubs for undefined goto target labels (e.g. `err`)
- `emit.c`: `tramp_collect_labels` skips function-body labels
- `snobol4_pattern.c`: removed `TREE_VAL`/`.t` member, use `FIELD_GET_fn` through `DATINST_t`
- `src/runtime/inc_stubs/`: 19 comment-only stub `.sno` files for beauty_core build

### Current state
- beauty_core_bin: **builds clean, 0 errors** ✓
- beauty_full_bin: **builds clean, 0 errors** ✓  
- Both output `OUTPUT` for input ` OUTPUT = 'hello'` — truncated (active bug)
- Debug traces still live in snobol4.c/_b_tree_c and snobol4_pattern.c/MAKE_TREE_fn

---

## Active bug: `aply("c", {x}, 1)` returns DT_S not DT_A

**Symptom:** pp_Stmt outputs only the label. `_c` set in pp_Stmt has `.v == DT_S`.
`indx(get(_c), {vint(2)}, 1)` returns DT_FAIL → ppSubj/ppPatrn/ppRepl never set.

**What is known:**
- `MAKE_TREE_fn` fires with `children.v=4` (= `DT_A` — ARRAY) ✓ tree IS built with array
- `APLY_fn("c", ...)` fires — fn pointer is valid (not NULL)
- `_b_tree_c` calls `FIELD_GET_fn(a[0], "c")`
- `FIELD_GET_fn` returns `obj.u->fields[3]` raw — no coercion
- `data_define("tree(t,v,n,c)")` in `runtime_init` is called THEN `register_fn("c", _b_tree_c)` overrides

**The mystery:** fields[3] should be the array stored by MAKE_TREE_fn — but returned value is DT_S.
Next step: trace FIELD_GET_fn to print `obj.v`, `fields[3].v` directly.

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — engine_stub.c only
- **ALWAYS run `git config user.name/email` after every clone**
- **ALWAYS use leading space in test input:** `printf " stmt\n"` not `echo "stmt"`
- **beauty_core (stubs) FIRST — beauty_full (real inc) SECOND**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | Session 80 runtime fixes | engine_stub T_FUNC/T_CAPTURE etc |
| 2026-03-14 | Session 83 diagnosis | _c = data_define overwrites _b_tree_c (later disproved) |
| 2026-03-14 | Session 84 SIL rename | DESCR_t/DTYPE_t/XKIND_t/_fn/_t throughout |
| 2026-03-14 | Session 84 build fixes | cs_alloc, computed goto, label table, inc_stubs |
| 2026-03-14 | Session 84 HALT | broke beauty_core/beauty_full agreement — reverted to stubs |
