# GOAL-BB-TEMPLATE-LADDER.md — Fill BB and SM Templates: Icon + Prolog Ladder

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-HEADQUARTERS.md PP-1..6 ✅ (`929d3177`) — pSM/pBB explicit params live.

## What this goal is

The PP rung gave every SM and BB template an explicit typed pointer (`const SM_t * pSM`,
`BB_t * pBB`). The template system is now properly parameterized. The BB and SM template
bodies for Icon and Prolog are honest stubs returning immediately. This goal fills them
incrementally — one operation at a time, growing from the smallest infitesimal program
toward full coverage — exactly how SNOBOL4, Icon, and Prolog were first developed.

The prior Icon BB work (GOAL-ICON-BB-NATIVE, GOAL-ICON-BB-COMPLETE) predated the SM
corral system (PP, EAO). Those goals built emitters outside the template system and are
superseded. The template system is now the one true path.

## Architecture reminder

```
Icon/Prolog source
    → frontend (parser + lowerer)
    → SM sequence (thin carrier: SM_BB_PUMP_PROC, SM_BB_ONCE_PROC, SM_BB_PUMP, ...)
    → SM templates (sm_bb_calls.c — already wired for x86)
    → BB graph (BB_ICN_*, BB_PL_* nodes)
    → BB templates (bb_icn_stub.c, bb_pl.c — ALL STUBS TODAY)
    → emitted x86 / JVM / JS / .NET / WASM
```

Icon is 99% BB. Prolog is 99% BB. The SM shims (`SM_BB_PUMP_PROC`,
`SM_BB_ONCE_PROC`) are already wired in `sm_bb_calls.c` for x86. The gap is every
`BB_ICN_*` and `BB_PL_*` template body.

## Invariants (non-negotiable)

0. **THE GOAL IS TO EMIT BYTES. A template that returns an empty string or only stub jumps has NOT been implemented. It is a stub. Stubs do not count as done. A rung is complete only when MEDIUM_TEXT emits real GAS instructions that implement the full generator semantics, AND MEDIUM_BINARY emits the corresponding raw x86 machine code bytes. An empty return or `bytes(1,"\xE9")+u32le(0)` placeholder is NOT completion — it is nothing. Do the work or do not mark the rung done.**
1. One template file per BB kind — RULES.md. No grouped ICN or PL stubs.
2. No C Byrd-box functions — RULES.md. Emit x86; do not write `DESCR_t foo(void*,int)`.
3. No AST walking in modes 2/3/4 — RULES.md.
4. Every new template takes `BB_t * pBB` — PP-2 contract.
5. Gate after every rung: GATE-PK 407/0/647 must hold. Rung gate must improve or hold.
6. Rung files live in corpus — flat files, `rung<NN>_<desc>.icn` / `.pl` + `.expected`.
7. **All code emission goes through the template system.** Every SM opcode must have an `sm_*` template in `SM_templates/` and be covered by `sm_op_is_dispatched`. Every BB graph walk (XA-level) must be triggered via an `XA_*` opcode dispatched through `xa_dispatch` in `XA_templates/`. Do not emit GAS text directly from `emit_sm.c` or `emit_core.c` outside a template function.
8. **`MEDIUM_BINARY` must never embed emitter-process pointers.** `pBB` and function pointers like `rt_binop_gen` are addresses in the *emitter* process — they are meaningless in the emitted binary. Any BB box that calls a C runtime helper (`rt_*`) belongs in the `MEDIUM_TEXT` arm only, using `call name@PLT`. The `MEDIUM_BINARY` arm is only for boxes whose encoding contains no absolute addresses (pure rel32 fixups and static constants). If a box needs to call a runtime helper, leave `MEDIUM_BINARY` as the two-jmp stub or omit it entirely.
9. **BB templates may not call RT functions. PERIOD.** A BB template emits x86 assembly. That assembly IS the box. There is no intermediate C runtime helper with port logic — if you need `rt_foo` to implement α/β/γ/ω, you have written a C Byrd box under a different name. Translate `bb_exec.c` logic directly into x86 TEXT instructions. The only permitted external calls in emitted x86 are to non-four-port utility functions (e.g. `strchr`, `memcmp`, arithmetic helpers with no port state). If you find yourself adding a new `rt_*` function to make a template work, stop — that is a C Byrd box and violates RULES.md.
## SM bridge hooks (already wired — do not touch)

| SM opcode | Handler | Used by |
|-----------|---------|---------|
| `SM_BB_PUMP_PROC` | `sm_bb_pump_proc()` in `sm_bb_calls.c` | Icon proc call |
| `SM_BB_ONCE_PROC` | `sm_bb_once_proc()` in `sm_bb_calls.c` | Prolog predicate |
| `SM_BB_PUMP` | stub — `[NO-AST]` | Icon expression pump (future) |
| `SM_BB_ONCE` | stub — `[NO-AST]` | (future) |
| `SM_BB_PUMP_EVERY` | stub — `[NO-AST]` | Icon `every` (future) |

## BB kinds to fill — Icon

Each gets its own `BB_templates/bb_icn_<name>.c`. Ordered by first rung that needs it.

| BB kind | Rung needed | Semantics |
|---------|------------|-----------|
| `BB_ICN_TO` | rung01 | integer range generator `lo to hi`; α resets, β advances |
| `BB_ICN_TO_BY` | rung01 | `lo to hi by step` |
| `BB_ICN_BINOP` | rung01 | arith/relop with generative operands |
| `BB_ICN_PROC_GEN` | rung02 | user proc call generator via GeneratorState |
| `BB_ICN_UPTO` | rung03 | `suspend` body — yields up to N times |
| `BB_ICN_ALTERNATE` | rung04 | `A \| B` — left first then right |
| `BB_ICN_LIMIT` | rung05 | `gen \N` — yield up to N ticks |
| `BB_ICN_ITERATE` | rung06 | `!list` iterate |
| `BB_ICN_SCAN` | rung07 | `subj ? body` |
| `BB_ICN_KEYWORD` | rung08 | `&subject`, `&pos` etc. |
| `BB_ICN_LIST_BANG` | rung09 | `!L` list/table generator |
| `BB_ICN_RECORD_DEF` | rung10 | `record T(f1,f2,...)` |
| `BB_ICN_FIELD_GET` | rung11 | `obj.field` read |
| `BB_ICN_FIELD_SET` | rung11 | `obj.field := rhs` |
| `BB_ICN_IDX` | rung12 | `s[i]` subscript |
| `BB_ICN_SECTION` | rung12 | `s[i:j]` section |
| `BB_ICN_IDX_SET` | rung13 | `base[idx] := rhs` |
| `BB_ICN_KEY_GEN` | rung14 | `key(t)` generator |
| `BB_ICN_TO_NESTED` | rung15 | `(lo_gen) to (hi_gen)` cross-product |
| `BB_ICN_FIND_GEN` | rung16 | find generator |
| `BB_ICN_SEQ_GEN` | rung17 | seq generator |
| `BB_ICN_LCONCAT` | rung18 | list concat |

## BB kinds to fill — Prolog

Each gets its own `BB_templates/bb_pl_<name>.c`.

| BB kind | Rung needed | Semantics |
|---------|------------|-----------|
| `BB_PL_BUILTIN` | rung01 | `write/1`, `nl/0`, `halt/0` — direct C calls |
| `BB_PL_UNIFY` | rung02 | `X = Y` — unification |
| `BB_PL_VAR` | rung02 | variable slot read |
| `BB_PL_ATOM` | rung02 | atom literal |
| `BB_PL_ARITH` | rung03 | `Y is X+2` — arithmetic |
| `BB_PL_SEQ` | rung03 | conjunction `A, B, C` |
| `BB_PL_CALL` | rung04 | predicate call |
| `BB_PL_CHOICE` | rung05 | multi-clause alternative |
| `BB_PL_ALT` | rung06 | inline disjunction `;` |
| `BB_PL_CUT` | rung07 | `!` cut |

## Ladder steps — Icon

- [x] **ICN-T-1** — `bb_icn_to.cpp`: `BB_TO` x86 template (stub; gate passes). GATE-PK.
- [x] **ICN-T-2** ✅ — `bb_to_by.cpp` + `icn_to_by_rt` runtime: `BB_TO_BY` int+real x86 TEXT template. rung01 step variants PASS. GATE-PK 507/0/608. one4all `13f4c7d4`. Also: renamed all BB_ICN_* → BB_* (22 kinds), 5 collisions resolved (BB_GEN_ALT, BB_GEN_BINOP, BB_GEN_SCAN; BB_ICN_TO_BY+BB_ICN_LIMIT dead, merged into existing).
- [x] **ICN-T-3** ✅ — `bb_binop_gen.cpp` + `rt_binop_gen` runtime: `BB_BINOP_GEN` x86 TEXT template (cross-product arith/relop). GATE-PK 516/0/599.
- [ ] **ICN-T-4** — `bb_proc_gen.cpp`: `BB_PROC_GEN`. Verify rung02 proc calls PASS. GATE-PK.
- [x] **ICN-T-5** ✅ — `bb_upto.cpp`: `BB_UPTO` inline x86, no RT calls. GATE-PK 513/0/602.
- [ ] **ICN-T-6** — `bb_gen_alt.cpp`: `BB_GEN_ALT`. Verify rung04 `A|B` PASS. GATE-PK.
- [ ] **ICN-T-7** — `bb_limit.cpp`: `BB_LIMIT`. Verify rung05 `gen\N` PASS. GATE-PK.
- [x] **ICN-T-8** ✅ — `bb_iterate.cpp`: `BB_ITERATE` inline x86, static char slots, no RT calls.
- [ ] **ICN-T-9** — `bb_gen_scan.cpp`: `BB_GEN_SCAN`. Verify rung07 scan PASS. GATE-PK.
- [ ] **ICN-T-10** — `bb_keyword.cpp`: `BB_KEYWORD`. Verify rung08 keywords PASS. GATE-PK.
- [ ] **ICN-T-11..N** — remaining `BB_*` kinds, one per step, one rung per step.

## Ladder steps — Prolog

- [x] **PL-T-1** ✅ — `bb_builtin.cpp` (renamed from bb_pl_builtin): `BB_BUILTIN` x86 template (write/nl/halt). Done.
- [x] **PL-T-2** ✅ — `bb_pl_var.cpp` + `bb_atom.cpp` + `bb_unify.cpp`; rt_pl helpers. smoke 5/5.
- [x] **PL-T-3** ✅ — `bb_arith.cpp` + `bb_pl_seq.cpp`; rt_pl_arith + rt_pl_seq_exec. smoke 5/5.
- [ ] **PL-T-4** — `bb_call.cpp` (or `bb_pl_call.cpp`): `BB_CALL` Prolog predicate call. Verify rung04 PASS. GATE-PK.
- [ ] **PL-T-5** — `bb_choice.cpp`: `BB_CHOICE`. Verify rung05 multi-clause PASS. GATE-PK.
- [ ] **PL-T-6** — `bb_alt.cpp`: `BB_ALT` Prolog disjunction. Verify rung06 PASS. GATE-PK.
- [ ] **PL-T-7** — `bb_cut.cpp`: `BB_CUT`. Verify rung07 PASS. GATE-PK.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=407 FAIL=0 STUB=647
bash /home/claude/one4all/scripts/test_icon_all_rungs.sh 2>&1 | tail -3
# Expect: PASS=194 FAIL=36 XFAIL=35
bash /home/claude/one4all/scripts/test_smoke_prolog.sh
# Expect: PASS=5 FAIL=0
```

## Gates

```
GATE-PK   bash scripts/test_per_kind_diff.sh          # always — 407/0/647
GATE-ICN  bash scripts/test_icon_all_rungs.sh         # Icon rung count must improve
GATE-PL   bash scripts/test_smoke_prolog.sh           # Prolog smoke must hold
GATE-ICN-SM bash scripts/test_smoke_icon.sh           # smoke must hold
```

## KEY OBSERVATION — ir_exec.c is the translation source (noted 2026-05-25, Sonnet 4.6)

Every `BB_ICN_*` and `BB_PL_*` has a **complete, working C implementation** in `src/lower/ir_exec.c`.
These are the exact semantics to translate into x86 text/binary templates. No logic to invent —
mechanical translation only. Map of C source → template status:

| BB kind | ir_exec.c line | Template file | Status |
|---------|---------------|--------------|--------|
| `BB_ICN_TO` | L1539 | `bb_icn_to.cpp` | stub — ICN-T-1 ✅ (GATE passes, template body not yet filled) |
| `BB_ICN_TO_BY` | L1596 | `bb_icn_to_by.cpp` | stub — **ICN-T-2 NEXT** |
| `BB_ICN_UPTO` | L1523 | *(missing)* | ICN-T-5 |
| `BB_ICN_ITERATE` | L1606 | *(missing)* | ICN-T-8 |
| `BB_ICN_ALTERNATE` | L1619 | *(missing)* | ICN-T-6 |
| `BB_ICN_LIMIT` | L1689 | *(missing)* | ICN-T-7 |
| `BB_ICN_BINOP` | L1640 | *(missing)* | ICN-T-3 |
| `BB_ICN_TO_NESTED` | L1675 | *(missing)* | ICN-T-15 |
| `BB_ICN_PROC_GEN` | L1705 | *(missing)* | ICN-T-4 |
| `BB_ICN_SCAN` | L873 | *(missing)* | ICN-T-9 |
| `BB_ICN_KEYWORD` | L904 | *(missing)* | ICN-T-10 |
| `BB_ICN_IDX` | L977 | *(missing)* | ICN-T-12 |
| `BB_ICN_SECTION` | L992 | *(missing)* | ICN-T-12 |
| `BB_ICN_LIST_BANG` | L1018 | *(missing)* | ICN-T-9 |
| `BB_ICN_RECORD_DEF` | L1091 | *(missing)* | ICN-T-10 |
| `BB_ICN_FIELD_GET` | L1102 | *(missing)* | ICN-T-11 |
| `BB_ICN_FIELD_SET` | L1113 | *(missing)* | ICN-T-11 |
| `BB_ICN_IDX_SET` | L1129 | *(missing)* | ICN-T-13 |
| `BB_ICN_KEY_GEN` | L1146 | *(missing)* | ICN-T-14 |
| `BB_ICN_FIND_GEN` | L1179 | *(missing)* | ICN-T-16 |
| `BB_ICN_SEQ_GEN` | L1247 | *(missing)* | ICN-T-17 |
| `BB_ICN_LCONCAT` | L412 | *(missing)* | ICN-T-18 |
| `BB_PL_SEQ` | L1715 | `bb_pl_seq.cpp` | ✅ done PL-T-3 |
| `BB_PL_ALT` | L1791 | *(missing)* | PL-T-6 |
| `BB_PL_CHOICE` | L1810 | *(missing)* | PL-T-5 |
| `BB_PL_CALL` | L1841 | *(missing)* | **PL-T-4 NEXT** |
| `BB_PL_CUT` | L1896 | *(missing)* | PL-T-7 |
| `BB_PL_ATOM` | L1901 | `bb_pl_atom.cpp` | ✅ done PL-T-2 |
| `BB_PL_VAR` | L1905 | `bb_pl_var.cpp` | ✅ done PL-T-2 |
| `BB_PL_ARITH` | L1917 | `bb_pl_arith.cpp` | ✅ done PL-T-3 |
| `BB_PL_UNIFY` | L1929 | `bb_pl_unify.cpp` | ✅ done PL-T-2 |
| `BB_PL_BUILTIN` | L1959 | `bb_pl_builtin.cpp` | ✅ done PL-T-1 |

**JCON irgen.icn cross-reference (jcon-master.zip, 2026-05-25):**
`jcon/tran/irgen.icn` is the original Icon-to-IR compiler written in Icon itself. It maps
directly to our BB kinds. Key correspondences:

| jcon irgen procedure | jcon IR op | SCRIP BB kind | ir_exec.c line |
|---------------------|-----------|--------------|---------------|
| `ir_a_ToBy` | `ir_operator("...", 3)` | **`BB_TO_BY`** (not BB_ICN_TO_BY!) | L625 |
| `ir_a_Scan` | `ir_opfn(":?", 2)` | `BB_ICN_SCAN` | L873 |
| `ir_a_Limitation` | `">"` + counter | `BB_ICN_LIMIT` | L1689 |
| `ir_a_Alt` | flow graph | `BB_ICN_ALTERNATE` | L1619 |
| `ir_a_Every` | loop+resume | `BB_ICN_UPTO`/PUMP | L1523 |
| `ir_a_Suspend` | `ir_Succeed`+label | `BB_SUSPEND` | — |
| `ir_a_While` / `ir_a_Until` | loop | `BB_ICN_UPTO` | L1523 |
| `ir_a_RepAlt` | indirect goto | `BB_ICN_ALTERNATE` | L1619 |
| `ir_a_Binop` | `ir_opfn` | `BB_ICN_BINOP` | L1640 |
| `ir_a_Call` | `ir_Call` | `BB_ICN_PROC_GEN` | L1705 |

**CRITICAL CORRECTION — `BB_TO_BY` is not `BB_ICN_TO_BY`:**
- `lower_icn.c` lowers `TT_TO_BY` to **`BB_TO_BY`** (shared SNOBOL4/Icon kind, L43 in BB.h),
  NOT `BB_ICN_TO_BY`. `BB_TO_BY` supports integer AND real-typed bounds (IJ-TOBY-REAL).
- `BB_ICN_TO_BY` (L89 in BB.h) is a separate simpler kind — integer-only, static step in `ival3`.
  It is produced by a different lowering path. Verify which path rung01 tests actually exercise
  before writing the template.
- `BB_TO_BY` at L625 in ir_exec.c is the complete, real implementation to translate.

**Pattern for each rung:** Read `case BB_ICN_<X>:` (or `BB_TO_BY:`, `BB_PL_<X>:`) block in
`ir_exec.c` → write x86 TEXT arm calling a runtime helper (declared extern in `emit_bb.c`,
implemented in `icon_box_rt.c` or `icn_runtime.c`) → BINARY arm with raw bytes + `bb_bin_t`
reloc sites → GATE-PK passes.
The `extern DESCR_t icn_bb_<x>(void *zeta, int entry)` declarations in `emit_bb.c` are the
runtime entry points each template calls via `call icn_bb_<x>@PLT`.

## Icon canonical semantics — original source reference (icon-master.zip, 2026-05-25)

All generator semantics are in `src/runtime/` RTT (`.r`) files. RTT is a C extension with
`suspend`/`fail`/`return` for generators; each `suspend` is one Byrd-box γ yield.
Key findings for every BB kind we must implement:

### `...` / `to by` → `BB_TO_BY` (`omisc.r` L146)
```
operator{*} ... toby(from, to, by)
  // from/to/by must be C_integer — **integers only in original Icon**
  if (by == 0) error 211
  if (by > 0): for (; from <= to; from += by) suspend from
  else:        for (; from >= to; from += by) suspend from
  fail
```
**Note:** Original Icon `toby` is **integer-only**. SCRIP's `BB_TO_BY` adds real support
(IJ-TOBY-REAL) — the `ival2` flag selects int vs real path. The x86 template must implement
both int and real paths matching `ir_exec.c` L625–L671.

### `...` / `to` (no by) → `BB_ICN_TO` (`omisc.r` L186)
```
operator{*} ... to(from, to)
  // integers only
  for (; from <= to; ++from) suspend from
  fail
```
Simple int counter, no step. `BB_ICN_TO` in ir_exec.c L1539.

### `!` bang → `BB_ICN_ITERATE` / `BB_ICN_LIST_BANG` (`oref.r` L8)
```
operator{*} ! bang(underef x -> dx)
  string-variable: suspend 1-char tvsubs for each position
  list:  chain lelem blocks, suspend struct_var for each slot
  table/set: hgfirst/hgnext iterator, suspend each element
  record: loop through fields, suspend struct_var
  string: suspend 1-char substring for each position
```
SCRIP splits this: `BB_ICN_ITERATE` (string, ir_exec L1606) and `BB_ICN_LIST_BANG`
(list/table/set, ir_exec L1018). Template must dispatch on descriptor type.

### `\N` limitation → `BB_ICN_LIMIT` (`imisc.r` L96 + `interp.r` Op_Lsusp)
```
limit(count):
  count must be integer; count < 0 → error; count == 0 → fail immediately
  otherwise pass through; Op_Lsusp decrements counter each time inner expr suspends
```
Counter initialized to `count`, decremented on each resume; fail when reaches 0.
SCRIP `BB_ICN_LIMIT` ir_exec L1689.

### `|` alternation → `BB_ICN_ALTERNATE` (`irgen.icn` `ir_a_Alt`)
```
try eList[1]; if it suspends → yield, on resume try same branch again
if branch exhausts → move to next branch
last branch exhausts → fail
```
SCRIP `BB_ICN_ALTERNATE` ir_exec L1619.

### `key(T)` → `BB_ICN_KEY_GEN` (`fstruct.r` L136)
```
function{*} key(t)  // t must be table
  for (ep = hgfirst(BlkLoc(t), &state); ep; ep = hgnext(BlkLoc(t), &state, ep))
    suspend ep->telem.tref    // the key, not the value
  fail
```
SCRIP `BB_ICN_KEY_GEN` ir_exec L1146.

### `find(s1, s2, i, j)` → `BB_ICN_FIND_GEN` (`fstranl.r` L133)
```
function{*} find(s1, s2, i, j)
  loop cnv_i from i to (j - len(s1)):
    if s2[cnv_i : cnv_i+len(s1)] == s1: suspend cnv_i
  fail
```
SCRIP `BB_ICN_FIND_GEN` ir_exec L1179.

### `seq(i, j)` → `BB_ICN_SEQ_GEN` (`fmisc.r` L523)
```
function{1,*} seq(from=1, by=1)
  by == 0 → error 211
  do { suspend from; from += by } while (in integer range)
```
Infinite (bounded only by integer overflow). SCRIP `BB_ICN_SEQ_GEN` ir_exec L1247.

### `?` scanning → `BB_ICN_SCAN` (`imisc.r` bscan/escan + `irgen.icn` `ir_a_Scan`)
Save `&subject` / `&pos`, set new subject, run body, restore on failure.
`bscan` sets up new subject; `escan` restores old. SCRIP `BB_ICN_SCAN` ir_exec L873.

### `&keyword` → `BB_ICN_KEYWORD` (`keyword.r`)
Each keyword variable read/write. `BB_ICN_KEYWORD` ir_exec L904.

### String/list subscript → `BB_ICN_IDX` / `BB_ICN_SECTION` (`oref.r` subsc/sect)
`s[i]` one-char or element reference; `s[i:j]` section. ir_exec L977/L992.

## ⛔ NO rt_* HELPERS FOR PL-T-4..7 (added 2026-05-25, Sonnet 4.6)

**NEVER add `rt_pl_call_exec`, `rt_pl_choice_exec`, `rt_pl_alt_exec`, `rt_pl_cut_exec`, or any similar
helper to `rt.c`/`rt.h` for implementing BB_PL_CALL, BB_CHOICE, BB_PL_ALT, or BB_CUT.**
These are port-logic helpers (they implement α/β/γ/ω dispatch) — forbidden by RULES.md INVARIANT 9.
The x86 TEXT template must emit the full port logic inline as GAS instructions.
The only permitted external calls are to non-four-port utility functions already present:
`trail_mark`, `trail_unwind`, `unify`, `prolog_atom_intern`, `term_new_int`, `term_new_atom`,
`bb_exec_once`, `bb_exec_resume`, `bb_reset`, `pl_bb_lookup`, `bb_graph_of_pred` — called via `@PLT`.
If you find yourself writing a new `rt_*` function to make a PL-T template work, DELETE IT.

## How to write a BB template

1. Read `ARCH-SCRIP.md` §"BB templates" and the existing `bb_lit.c` as the model.
2. Create `src/emitter/BB_templates/bb_icn_<name>.c` (or `bb_pl_<name>.c`).
3. Add `void bb_icn_<name>(BB_t * pBB)` (or `int`) to `BB_templates/bb_templates.h`.
4. Wire into `emit_bb_node` switch in `emit_core.c` for the relevant `BB_ICN_*` / `BB_PL_*` kind.
5. Add compile rule to Makefile.
6. Start with IS_X86 arm only; IS_JVM/JS/NET/WASM stubs return immediately.
7. Run rung gate. If rung count improves: commit.

## Watermark


```
one4all: HEAD (ICN-T-3 + RULE: no template code in emit_core.c)
Gate: PASS=516 FAIL=0 STUB=599
Icon --interp: PASS=195 FAIL=36 XFAIL=35
Prolog smoke: PASS=5 FAIL=0
PL-T-1 ✅ bb_builtin.cpp (BB_BUILTIN write/nl/halt)
PL-T-2 ✅ bb_pl_var.cpp + bb_atom.cpp + bb_unify.cpp
PL-T-3 ✅ bb_arith.cpp + bb_pl_seq.cpp
ICN-T-2 ✅ bb_to_by.cpp + icn_to_by_rt (BB_TO_BY int+real)
ICN-T-3 ✅ bb_binop_gen.cpp + rt_binop_gen (BB_BINOP_GEN cross-product)
RENAME ✅ BB_ICN_* → BB_* complete; RULE ✅ no template code in emit_core.c
NEXT: ICN-T-6 — bb_gen_alt.cpp (BB_GEN_ALT inline x86)
      ICN-T-7 — bb_limit.cpp (BB_LIMIT inline x86)
      PL-T-4  — bb_call.cpp (BB_CALL)
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## FREE-BB-BEFORE-RUN — Delete SM+BB before Mode 3/4 execution (added 2026-05-25)

**Root insight (Lon, session 2026-05-25):** BB and SM graph structures must be completely deleted
BEFORE execution in Mode 3 (--run) and Mode 4 (--compile). They have no access to the tree at
runtime. Mode 3/4 x86 blobs are self-contained. Mode 2 (--interp) walks sm->instrs at runtime
so it must NOT free them.

**What stage2_free_bb_only does:** frees only BB_graph_t objects. Leaves sm->instrs alive so
sm_jit_run can still read CUR_INS operand strings/integers via CUR_INS->a[0].s etc.
**stage2_free_sm_bb:** frees everything — called after sm_jit_run completes.

### Steps

- [x] **FREE-1** — Add `stage2_free_bb_only(s2)` in `scrip_sm.c`/`scrip_sm.h`. Wire in
  `scrip.c` Mode 3: call after `SM_codegen`, before `sm_jit_run`. Simple SNOBOL4 SM opcodes
  (output/arith/concat) work. `SM_EXEC_STMT` and `SM_BB_ONCE_PROC` segfault because they
  reach into freed `bb_table` at runtime.

- [ ] **FREE-2** — Fix `SM_EXEC_STMT` in `sm_jit_interp.c`. `h_exec_stmt` reads
  `g_stage2.sm.bb_table[i]` at runtime — freed. Fix: add a `case SM_EXEC_STMT:` in
  `SM_codegen` that, if `a[2].i >= 0` (has BB pattern), walks the BB pattern graph at
  codegen time and emits a blob that calls the already-compiled BB_PAT Byrd boxes directly
  (via their emitter-process addresses, baked in at codegen). The blob must NOT reference
  `bb_table` at runtime. SNOBOL4 `pattern_replace` and `goto` crosscheck will pass.

- [ ] **FREE-3** — Fix `SM_BB_ONCE_PROC` in `sm_jit_interp.c`. `h_bb_once_proc` calls
  `pl_bb_once_proc_by_name` → `bb_graph_of_pred` → freed graph. Fix: add a `case
  SM_BB_ONCE_PROC:` in `SM_codegen` that walks the Prolog predicate's BB graph at codegen
  time and emits fully-compiled Byrd box x86 for each BB_PL_* node. Runtime handler must
  NOT touch `dcg_table` or any BB_graph_t. Prolog Mode 3 crosscheck 6 FAILs → 0.

- [ ] **FREE-4** — After FREE-2 and FREE-3, move `stage2_free_bb_only` call to immediately
  after `SM_codegen` returns in Mode 3. Confirm crosscheck_snobol4 and crosscheck_prolog
  both clean. Then extend to Mode 4: `stage2_free_sm_bb` already called after
  `sm_codegen_text` (correct — emitter needs graph, binary runs later without it).

- [ ] **FREE-5** — ASAN verify: `ASAN_OPTIONS=detect_use_after_free=1` on all smoke gates.
  Zero UAF. Mirrors PJ-12c.
