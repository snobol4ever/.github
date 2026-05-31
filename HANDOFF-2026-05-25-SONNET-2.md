# HANDOFF — 2026-05-25 — Claude Sonnet 4.6 Session (second)

**SCRIP HEAD:** `f9cda41a`
**\.github HEAD:** `24da7b7f`
**Gate:** smoke_prolog 5/5 ✅ · crosscheck_prolog 128/0 ✅ · AUDIT GREEN

---

## Work completed this session

### PJ-10 — BB_PL_* opcode rename (partial promotion)

Six clean opcodes (no collision with Icon/Snocone) renamed:
- `BB_PL_ARITH` → `BB_ARITH`
- `BB_PL_ATOM` → `BB_ATOM`
- `BB_PL_BUILTIN` → `BB_BUILTIN`
- `BB_PL_CHOICE` → `BB_CHOICE`
- `BB_PL_CUT` → `BB_CUT`
- `BB_PL_UNIFY` → `BB_UNIFY`

Four kept with `PL_` (collision with Icon ops — distinct semantics, kept readable):
- `BB_PL_VAR`, `BB_PL_CALL`, `BB_PL_SEQ`, `BB_PL_ALT`

BB template files renamed on disk to match: `bb_arith.cpp`, `bb_atom.cpp`, `bb_builtin.cpp`, `bb_unify.cpp`. Makefile updated. All gates hold.

### Infrastructure fixes (also in f9cda41a)

- `sm_bb_calls.cpp` IS_MACRO_DEF — `BB_ONCE_PROC`/`BB_PUMP_PROC` if-return chain → `IF()` concat; `s_3asm` third-arg comment fixed to `# comment`
- `sm_arith.cpp` — removed duplicate `DEFINE_ENTRY`/`DEFINE` macro emissions (owned by `sm_defines.cpp`)
- `emit_sm.c` — deleted `.include "sm_macros.s"` (stale; template dispatch IS the macro library)
- `emit_sm.c` — set `EMIT_TEXT` mode before `xa_bb_macro_library` so `bb_macros.s` is actually written to disk
- `xa_pl_builder.cpp` / `xa_pl_sub_builder.cpp` — `mov rsi`/`mov rcx` → `mov esi`/`mov ecx` (32-bit int params)
- `Makefile` — added `emit_str.cpp` to `RT_PIC_SRCS`; added `-lstdc++` to `libscrip_rt.so` link
- `run_prolog_via_x86_backend.sh` — emits `.s` next to source (CWD = PLDIR); assembler also runs from PLDIR

---

## Open items

### PJ-9e — factorial Mode 4 segfault

`hello.pl` works end-to-end in Mode 4 (assembles, links, runs, prints). `factorial.pl` (multi-clause predicate) segfaults at runtime. Root: `rt_pl_b_set_opaque` stores sub-cfg ptr into `BB_SUCCEED` node's `->opaque`, but something goes wrong when `ir_exec.c` dereferences it at runtime. Next step: `gdb` the binary.

```bash
# Reproduce:
cd /home/claude/SCRIP && make libscrip_rt
bash scripts/run_prolog_via_x86_backend.sh /tmp/factorial.pl
# factorial.pl content:
#   fact(0, 1) :- !.
#   fact(N, F) :- N > 0, N1 is N - 1, fact(N1, F1), F is N * F1.
#   :- initialization(main).
#   main :- fact(5, F), write(F), nl.
```

### INVARIANT (do not forget)

`.s` files are always emitted next to the original source (CWD == source dir).
`bb_macros.s` also lands in that same CWD. Run scripts must `cd` to source dir
before invoking scrip AND before invoking the assembler.

---

## Active step in GOAL-PROLOG-BB.md

**PJ-10 ✅ complete.** Next: resume **PJ-9e** — debug factorial Mode 4 segfault.

## Watermark

```
SCRIP: f9cda41a
.github: 24da7b7f
smoke_prolog: 5/5 ✅
crosscheck_prolog: 128/0 ✅
honest_prolog: 124/0/0 (not re-run this session — no regression expected)
honest_icon: 277/0/0 (not re-run this session)
broker: 20/49
```
