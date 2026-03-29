# SESSION-icon-x64.md — Icon × x86 (one4all)

**Repo:** one4all · **Frontend:** Icon · **Backend:** x86
**Session prefix:** `IX` · **Trigger:** "playing with Icon x64" or "Icon asm"
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| x64 emitter patterns | `BACKEND-X64.md` | codegen, register model |
| JCON deep analysis | `ARCH-icon-jcon.md` | four-port templates |

---

## §BUILD

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

All tools, repos, and oracles installed by bootstrap. scrip-cc at `/home/claude/one4all/scrip-cc`.


## §NOW — IX-18

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-18 | `c648df5` | rung10–35 all green on x64 backend |

### Context: JVM vs x64

**The JVM backend (`icon_emit_jvm.c`) has rung01–35 all 5/5 ✅.**  
The x64 backend (`icon_emit.c`) is a separate, younger emitter. IX-17 established
the first real x64 scan: the driver gate was wired, `ICN_AUGOP` implemented, and a
corpus harness written. x64 is now buildable and testable but many node kinds are
still missing or buggy.

### x64 Baseline (IX-17 scan, commit `c648df5`)

Harness: `test/frontend/icon/run_icon_x64_rung.sh`  
Link recipe: `gcc -nostdlib -no-pie -Wl,--no-warn-execstack <obj> src/frontend/icon/icon_runtime.c`

| Rung | x64 result | Notes |
|------|-----------|-------|
| rung01–09 | **✅ (pre-existing)** | Were passing before IX-17 |
| rung10_augop | **5/5 ✅** | Fixed IX-17: `ICN_AUGOP` now implemented |
| rung11_bang_augconcat | 0/5 ❌ | `ICN_BANG` unimpl + str rdi/push duality bug |
| rung12_strrelop_size | 1/5 ❌ | `ICN_SLT/SGT/SLE/SGE/SNE` + `ICN_SIZE` unimpl |
| rung13_alt | 0/5 ❌ | str rdi/push duality: `ICN_STR` in ALT loses pointer |
| rung14_limit | 1/5 ❌ | `ICN_LIMIT` unimpl |
| rung15–20 | mostly ❌ | reals, subscript, section, seqexpr unimpl |
| rung21_global_initial | 3/5 ❌ | `ICN_INITIAL` unimpl |
| rung22–24 | 0/5 ❌ | lists/tables/records unimpl |
| rung25_global | 5/7 ✅ | Global ints pass; str globals hit rdi bug |
| rung26–33 | mostly ❌ | pow, read, builtins, sort, case unimpl |
| rung34_null_test | 3/5 ❌ | `ICN_NONNULL` unimpl |
| rung35_block_body | 1/5 ❌ | `ICN_SEQ_EXPR` unimpl |
| rung36_jcon | separate | jcon subsystem |

### Failure taxonomy (priority order for IX-18)

**#1 — `ICN_STR`/`ICN_CSET` rdi/push duality (high-impact, ~15 tests)**

`emit_str` uses `lea rdi, [rel label]` — leaves pointer in rdi, nothing on hw
stack. Every other leaf node pushes. This inconsistency is handled ad-hoc in
`emit_call`/`emit_assign`/`emit_concat` by checking `arg->kind == ICN_STR`, but
breaks whenever a STR appears inside `ICN_ALT`, `ICN_AUGOP`, or any context that
doesn't check kind. Fix options:
- **A (recommended):** Make `emit_str` push like all other nodes — `push rdi` after
  the `lea`. Then remove all `rhs_is_str`/`left_is_str`/`right_is_str` special-cases
  in emit_assign, emit_concat, emit_augop. Update emit_call `write` handler to always
  `pop rdi` for str args. Update scan/concat to always pop.
- **B:** Keep rdi convention but propagate it through ALT/AUGOP — harder, non-local.

Option A is cleaner. Cross-check against `emit_seq` (uses `icn_str_eq`, needs two
char* args) and `emit_scan` (needs subject pointer) — both currently special-case
the STR node kind; after fix they just pop normally.

**#2 — `ICN_BANG` unimplemented (~8 tests)**

`!E` generator: for strings, iterates characters; for lists, iterates elements.
In the x64 backend there's no list/GC infrastructure. Stub: implement string-only
`!str` via a BSS index counter (like `ICN_TO`) — iterates over chars of the string
at each β, pushes char* (single-char via arena). That unblocks rung11 and rung13.

**#3 — String relops `ICN_SLT/SLE/SGT/SGE/SNE` (~5 tests)**

`icn_str_lt(const char*, const char*)` etc. are not in `icon_runtime.c`. Add them
(wrapper around `strcmp`) and add `emit_strrelop()` mirroring `emit_relop()` but
calling the C runtime fn. Wire SLT/SLE/SGT/SGE/SNE in dispatch.

**#4 — `ICN_SIZE` (~2 tests)**

`*E`: string size. Emit E, then call `icn_str_len(char*)` → push long. Add
`icn_str_len` to runtime. Wire `ICN_SIZE` in dispatch.

**#5 — `ICN_LIMIT` (~4 tests)**

`E \ N`: limit generator. BSS counter per node, decrements on each β, fails
when zero. Wire `ICN_LIMIT` in dispatch.

**#6 — `ICN_SEQ_EXPR` (~4 tests)**

`(E1; E2; E3)`: evaluates each in sequence, value is last. For x64: emit E1
(discard value), emit E2 (discard), ..., emit En (keep). Wire in dispatch.

**#7 — `ICN_INITIAL` (~2 tests)**

`initial { ... }`: runs once on first call to enclosing proc. BSS flag per proc.
Wire in dispatch.

**#8 — `ICN_NONNULL` (~2 tests)**

`\E`: succeed and yield E's value if E succeeds (identity except it makes the
non-null test explicit). α → E.α; E.γ → ports.γ (value already on stack); E.ω →
ports.ω. β → E.β.

**#9 — write() type dispatch bug (~10 tests)**

After fixing #1, `write(s)` where `s` is a string var still calls `icn_write_int`
because `icn_expr_kind(ICN_VAR)` returns `'?'` unless type inference fired. Fix:
in `emit_call` write handler, after `pop rdi`, use the inferred type: if kind is
`'S'` call `icn_write_str`, else if kind is `'I'` call `icn_write_int`, else emit
a runtime type check (or just call `icn_write_int` as fallback for now).

### Files to edit

- `src/frontend/icon/icon_emit.c` — all emit fixes, new emit_* functions
- `src/frontend/icon/icon_runtime.c` — add `icn_str_lt`, `icn_str_le`, `icn_str_gt`,
  `icn_str_ge`, `icn_str_ne`, `icn_str_len`, `icn_bang_str_init`/`icn_bang_str_next`

### What was fixed (IX-17, commit `c648df5`)

1. **Driver gate** (`main.c`): removed `"Icon requires -jvm"` stub; `-icn` without
   `-jvm` now routes to `icn_emit_file()` (Byrd Box NASM x64 emitter).

2. **`ICN_AUGOP`** (`icon_emit.c`): `emit_augop()` — synthesises a temporary
   binop/relop/concat node on the fly, emits it, pops result, stores back into LHS
   variable (local slot or BSS global). Handles `+:=` `-:=` `*:=` `/:=` `%:=`
   `||:=` `=:=` `==:=` `<:=` `<=:=` `>:=` `>=:=` `~=:=`. Unrecognised subtypes
   fall to emit_fail_node.

3. **x64 corpus harness** (`test/frontend/icon/run_icon_x64_rung.sh`): new script
   mirrors `run_crosscheck_x86_rung.sh` but for `.icn`/`.expected` pairs. Uses
   `scrip-cc -icn`, nasm, `gcc -nostdlib`, diff. PASS/FAIL/SKIP counts.

### NEXT ACTION — IX-18

Work down the failure taxonomy above. Highest leverage first:

1. Fix `ICN_STR` push convention (Option A) — unblocks rung11, rung13, rung21 str tests, rung25 str
2. Implement `ICN_NONNULL`, `ICN_SEQ_EXPR`, `ICN_LIMIT`, `ICN_SIZE`
3. Add string relops + runtime fns (`icn_str_lt` etc.)
4. Implement `ICN_BANG` for strings
5. Fix write() type dispatch

Run harness after each batch:
```bash
bash test/frontend/icon/run_icon_x64_rung.sh \
  test/frontend/icon/corpus/rung10_augop \
  test/frontend/icon/corpus/rung11_bang_augconcat \
  ... (rung10–35)
```
