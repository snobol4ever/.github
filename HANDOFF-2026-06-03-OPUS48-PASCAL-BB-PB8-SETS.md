# HANDOFF 2026-06-03 OPUS48 — Pascal BB: PB-8 sets

**Goal:** `GOAL-PASCAL-BB.md`. **Repos:** SCRIP (`1b4e0fe`), corpus (`54d5ce5`), `.github` (goal watermark +
this file). PLAN.md untouched (routine handoff).

One rung landed: **PB-8 `set`** (mode-2, `--interp`), zero cross-language regression. PB-8 stays `[ ]` overall
(pointers/`new` still open) but `record` (session 8) + `set` (this session) are both DONE.

---

## PB-8 sets — COMPLETE (SCRIP `1b4e0fe`)

Sets ride the **integer-bitmask rail** — a `set of 0..47` is a 48-bit mask held in a plain `INTVAL`. **Zero
structural lower/interpreter changes** (same philosophy as records-on-the-array-rail). Every set operation is a
builtin call (`TT_FNC`→`IR_CALL`); no new TT_ or IR opcode was needed.

### Parser (`pascal.y`)
- `[a,b,c]` → `mk_set_ctor` → `__pas_set(a,b,c)`; `e in s` → `mk_in` → `__pas_in(e,s)`. (Both were dead
  placeholders before: `[...]` dropped to `TT_SUCCEED`; `in` built a malformed `bin(TT_FNC,…)`.)
- New `expression_list_opt` carries its element list (was untyped) so the empty set `[]` → `__pas_set()` → 0.
- **Set-var tracking**: the `set of …` `type` arm now returns sentinel **`-2`**; `var_decl` registers such a
  var via `pas_setvar_add`. `pas_is_setexpr(node)` is true for a set-var `TT_VAR` or a `__pas_set*` call.
- `pas_arith_or_set(arith_kind, setfn, a, b)` redirects `+`/`*`/`-` and `<=`/`>=` to
  `__pas_setuni`/`__pas_setint`/`__pas_setdif`/`__pas_subset`/`__pas_super` **only when `pas_is_setexpr(a)||
  pas_is_setexpr(b)`** — integer arithmetic and integer relops are byte-for-byte unchanged. `=`/`<>` need no
  redirect (bitmask integer compare is already correct).
- Reset `g_pas_nsetvar = 0` in `pascal_parse_string`.

### Runtime (`by_name_dispatch.c`, `script_try_call_builtin_by_name`)
Seven name-gated builtins, placed right after `__pas_sqr`:
- `__pas_in(e,s)` → `(e>=0 && e<64 && ((s>>e)&1))?1:0`
- `__pas_set(…)` → OR of `1<<ei` for each in-range element
- `__pas_setuni/setint/setdif` → `a|b` / `a&b` / `a&~b`
- `__pas_subset(a,b)` → `(a&~b)==0`; `__pas_super(a,b)` → `(b&~a)==0`

### Why these are correct (grounded in `int.p`)
`int.p` set opcodes: `sgs` (singleton), `uni`/`int`/`dif` (∪/∩/∖), `inn` (∈), set `equ`/`neq`/`leq`/`geq`.
The bitmask maps each directly. Crucially, **overlapping union** must use bitwise-OR, not integer `+` (which
carries): `{1,2}+{2,3}` → oracle 3, and the old integer-`+` path gave 2. Now correct.

### Oracle facts discovered
- The corpus **`pcom.pas` is `sethigh=47, setsize=1`** (a 48-element single-word set). The **uploaded
  `comp.p` is a different copy at `sethigh=63,setsize=4`** — do not use it as the bound. Base type must be
  `0..47`; `0..58`/`set of char`/named-subrange-to-58 are rejected (error 169 "error in base set").
- **Set ranges `[a..b]` are rejected by `pcom` itself** (error 6) — OUT OF SCOPE, not a bug. The set
  constructor reads comma-separated `expression`s only.

### Probes (corpus `54d5ce5`, all byte-identical to `pint`)
`set1` constructor+`in`→4 · `set2` inline literal in condition→4 · `set3` empty set→0 · `set5` overlapping
union→3 · `set6` intersection→2 · `set7` difference→2 · `set8` subset/superset/`=`/`<>`→1111. (No `set4`: the
range probe was removed because the oracle rejects it.)

---

## Regression evidence (direct rebuild + suite run)
- **Pascal suite 24/24** byte-identical (the 17 prior + the 7 set probes). Integer arithmetic untouched
  (`recursion` through `fact(7)` byte-identical; `fact(8)` is the pre-existing deferred 16-bit overflow).
- **Icon `--interp` 130 PASS / 117 FAIL / 36 XFAIL** — identical to the PB-7/PB-8-records baseline.
- **Prolog honest mode-2 132/132, 0 ABORT** — identical.
- **SNOBOL4 `--interp` smoke 2/0.** (Note SCRIP is case-sensitive: `OUTPUT` ≠ `output`.)
- C style clean (0 lines >200). Parser s/r count still **1** (pre-existing dangling-else; no new conflict).

---

## Architecture review this session (Lon raised, resolved — NO code change)
Lon flagged several IR/AST choices in the Pascal grid. Verified against source:
- **`IR_IF` / `IR_WHILE` are NOT language tags** — `TT_IF` is emitted by icon/pascal/prolog/raku/rebus/snocone
  and `TT_WHILE` by icon/pascal/raku/rebus/snocone; both lower via the shared `v_if`/`v_while`, and the
  `IR_interp` handlers are lang-agnostic (branch on `IS_FAIL`). The goal doc's boolean model already relies on
  `IR_IF`. Removing them from Pascal would diverge from five other frontends and contradict the goal doc — so
  they stay.
- **Two genuine cross-language borrows logged for later cleanup** (deferred by Lon, not blocking):
  1. Pascal's `TT_IDX` arms call **Raku-named** `v_raku_det_call` / `v_raku_mutate_writeback` (the documented
     PB-5 "Raku array rail"). Approach is fine; the *naming* is the smell. Cleanup: neutral helper names.
  2. Pascal procs use the SNOBOL4-style **`TT_STMT`+`:subj` envelope**. **rebus** is the cleaner precedent
     (bare `TT_PROGRAM`, no envelope). Cleanup: drop the envelope for Pascal and read procs directly in
     `lower_program.c`.

---

## Setup / gotchas (unchanged)
- **Parser regen workaround still required** (`regenerate_parser_and_lexer_from_sources.sh` is `set -e` and
  aborts at the snobol4 flex step). Regen Pascal directly: `cd src/parser/pascal && bison -d -o pascal.tab.c
  pascal.y`. `pascal.l`/`pascal.lex.c` untouched this session.
- corpus build artifacts (`pcom`,`pint`,`*.o`,`prr`,`prd`) gitignored under `programs/pascal/`; add probe
  `.pas` files explicitly.
- `test/raku/rk_array_literal.raku` FAILS on the clean baseline (pre-existing).

## Build / verify
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
cd /home/claude/corpus/programs/pascal
for f in set1 set2 set3 set5 set6 set7 set8; do
  ./pcom < $f.pas >/dev/null 2>&1 && cp prr prd && echo "$f oracle: $(./pint </dev/null 2>/dev/null|tr -d ' \n')  scrip: $(/home/claude/SCRIP/scrip --interp $f.pas </dev/null 2>/dev/null|tr -d ' \n')"
done
```

## Recommended next
- **PB-8 pointers/`new`** — the last aggregate. `int.p`: `new` (csp 4) grows `np` downward; `^` deref is `ind`;
  `nil` is `maxstr`. In mode-2 the NV namespace can model heap cells (observable behavior, not P-machine
  layout). Add only what a probe forces.
- Then the deferred record edge cases (nested records, `with`, record-valued `var` params, per-activation
  record locals) when a probe needs them.
- Optional housekeeping: the two cross-language-borrow cleanups above (neutral array-helper names; drop the
  `:subj` proc envelope).
- Eventually **PB-9** (mode-3/4 compiled BBs) once the mode-2 ladder is comfortably green.
