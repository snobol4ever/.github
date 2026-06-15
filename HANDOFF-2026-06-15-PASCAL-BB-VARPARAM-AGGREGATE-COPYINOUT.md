# HANDOFF 2026-06-15 — Pascal BB: var-param-of-aggregate copy-in/out (marshal_varparam_addr frontier closed)

## TL;DR

One clean fix landed, one file touched (`src/lower/lower_pascal.c`, **+38 −0**). The
`marshal_varparam_addr: var-param arg is not a variable` BOMB (the prior handoff's named NEXT
FRONTIER) is **fixed** by a pure AST/lowering copy-in/copy-out rewrite for `var` parameters whose
call-site argument is an aggregate ELEMENT. ZERO emitter/template/x86/binary/runtime changes —
exactly the design the prior handoff recommended and POC-proved. Gates: Pascal **M3 125/0 · M4
125/0** (was 123/0 ×2; +2 new probes, zero regressions). SNOBOL4 M4 crosscheck **166/87/8
byte-identical**. With the bomb gone, **pcom now runs its real logic** and emits the source listing.

## What landed (SCRIP `src/lower/lower_pascal.c` ONLY)

**Root cause.** A `var` (by-reference) parameter passes a pointer to a stable 16-byte descriptor
cell; the callee dereferences it to read AND write the caller's location. Frame slots
(`[r12+off]`) and gvars (`rt_gvar_cell`) have such a cell. But an aggregate ELEMENT —
`genlabel(uprcptr^.pfname)` lowers to `arr_get(__pas_deref(uprcptr), idx)` (a `TT_IDX`, op
IR_CALL=9), and `genlabel(a[i])` to `arr_get(a, i)` — lives inside an SOH-separated record/array
string with no standalone addressable cell. The byref marshaller only handles `IR_VAR_FRAME`(162),
`IR_VAR_FRAME_REF`(164), named `IR_VAR`(4); the `arr_get` IR_CALL fell to `x86_bomb`. (pcom byref
arg census from the prior session: 91× IR_VAR_FRAME · 2× IR_VAR_FRAME_REF · 6× named IR_VAR · **2×
arr_get** — only the 2 arr_get bombed.)

**Fix (the prior handoff's recommended copy-in/copy-out, done in the lower, not the parser).**
In `lower_call`:
1. Look up the callee's `byref_mask` from `g_stage2.proc_table` by name (`pas_callee_byref_mask`).
   The table is populated by `polyglot.c` BEFORE any lowering runs, so the mask is available even
   for forward calls — which is exactly why the lower (not `pascal.y mk_call`) is the right site.
2. If any byref-position arg is a `TT_IDX` (aggregate element), rewrite the whole call:
   `genlabel(agg[i])` ⟶ `tmp := agg[i];  genlabel(tmp);  agg[i] := tmp`
   by synthesizing a unique temp `__pas_vptmp_N` (`pas_vptmp_var`), building a `TT_SEQ_EXPR` of
   `[ copy-in assigns…, rewritten call (arg replaced by tmp), copy-out assigns… ]`, and lowering
   THAT (`lower_seq` chains it through `IR_CONJ` for free).
3. The temp lowers to a named `IR_VAR` (out of scope) → the marshaller's named-`IR_VAR` path
   handles it. The copy-out reuses the EXISTING write-back lowering: `p^.fld := tmp` →
   `__pas_field_set` (the `__pas_deref` base branch of `lower_assign`); `a[i] := tmp` →
   `arr_set_pure`. No new runtime primitive needed.
4. Plain-var byref args (`TT_VAR`) are NOT rewritten — the 99-arg working class is untouched.
   The re-entry of `lower_call` on the rewritten `genlabel(tmp)` sees `tmp` as `TT_VAR`, so no
   recursion and no double-rewrite.

Three tiny local AST helpers were added (`pas_lc_leaf` / `pas_lc_bin` / `pas_lc_clone`) so the
lower does not depend on `pascal.y` internals (`leaf_s`/`bin`/`pas_tree_clone` are parser-local).
The copy-out clones BOTH the lvalue and the temp node so no AST node is shared between the call arg
and the write-back (avoids double-ownership during lowering).

## Why it's behavior-neutral / safe

- Fires ONLY when the callee mask marks the position byref AND the arg is `TT_IDX`. Every other
  call lowers down the unchanged original path (the `if (brm)` block is skipped entirely when the
  callee has no byref params, which is the overwhelming majority).
- Semantically exact for the alias-free case (pcom's `genlabel` writes a fresh label int; no
  aliasing during the call). Both legs were independently POC-proved M3+M4 in the prior session.
- A named `IR_VAR` temp uses a global scratch cell rather than a frame-local. For pcom's `genlabel`
  (one complete statement, never two such calls live simultaneously) this is correct. If a future
  probe exhibits reentrancy/aliasing on the temp, escalate to a frame-local temp (add the name to
  the proc's `lower_sc` so it gets a real slot) — noted as the only conceivable follow-up, not
  needed today.

## Gate state at handoff (all green / no regression)

| Gate | Result |
|---|---|
| Pascal M3 `--run` | **125 / 0** (XFAIL: recursion.pas has no .ref) |
| Pascal M4 `--compile`+as+link+run | **125 / 0** |
| New probe `vpfld` (deref record-field var-param) M3+M4 | `42` / `99` ✓ |
| New probe `vparr` (array-element var-param) M3+M4 | `7` / `42` / `9` ✓ |
| SNOBOL4 M4 crosscheck | **166 / 87 / 8** — byte-identical to baseline, same fail list |
| SNOBOL4 DEFINE canary `DOUBLE(21)` | `42` |
| Icon `hello.icn` / Prolog `hello.pl` `--run` | clean |
| template-medium-invisible `--strict` | **0 violations** |
| Plain-var byref probes (varparam/swap/varframe/varmix/vartrans/recparam{,2,3}) | all PASS |
| `git status` | only `src/lower/lower_pascal.c` (committed) |

## New probes (committed to corpus)

```pascal
{ vpfld.pas — var-param of a record field reached through a pointer deref }
program vpfld(output);
type rec = record fld: integer; other: integer end; pr = ^rec;
var p: pr;
  procedure genlabel(var nxtlab: integer); begin nxtlab := 42 end;
begin new(p); p^.fld := 7; p^.other := 99; genlabel(p^.fld);
  writeln(p^.fld); writeln(p^.other) end.    { -> 42 / 99 ; sibling untouched }
```
```pascal
{ vparr.pas — var-param of an array element (arr_set_pure write-back) }
program vparr(output);
var a: array[1..3] of integer; i: integer;
  procedure genlabel(var nxtlab: integer); begin nxtlab := 42 end;
begin a[1]:=7; a[2]:=8; a[3]:=9; i:=2; genlabel(a[i]);
  writeln(a[1]); writeln(a[2]); writeln(a[3]) end.   { -> 7 / 42 / 9 }
```
Both bombed on the pre-fix build (`marshal_varparam_addr`) and now pass M3+M4. `.ref`s built at
fpc default integer width 10 (fpc unavailable offline, but integer output is unambiguous).

## pcom advance (the payoff) + NEXT FRONTIER

`scrip --run pcom.pas < /tmp/tiny.pas` (tiny = `program t(output);\nbegin end.`) **no longer
bombs** — pcom runs its real logic and emits the source listing:
```
     1        9 program t(output);
     2        9 begin end.
```
pcom M4 `--compile` emits **234,201 asm lines, assembles cleanly, links, and runs** (the Session-60
`.Lcallfn` duplicate-label blocker #3 is NOT reproducing on the current tree).

**NEXT FRONTIER — pcom M3/M4 first-output divergence.** On tiny, **M3 emits the 2-line listing,
M4 emits NOTHING** (both rc=0). pcom's first `write` (the source-listing line) reaches stdout in M3
but not M4 — a mode-specific early-I/O divergence, echoing the Session-59 note that pcom's first
`write` didn't reach stdout in one mode. This is independent of the var-param fix. Suggested next:
build a minimal `write`-in-a-proc / listing-shaped probe that PASSES M4, then diff the emitted asm
for the first `__pas_write` path between it and pcom to find what M4 drops (M3 demonstrably executes
it). NOTE: there is **no mode-2 `--interp` flag** anymore (the DE-INTERP goal removed the misnomer);
only `--run` (M3) and `--compile` (M4) exist — the GOAL file's "Mode-2 interp" row is stale.

## Build / gate quickrefs

```
cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt   # landmine #1: always rm -f scrip first
# Pascal M3: loop corpus/programs/pascal/*.pas (skip pcom/pint/ppp; recursion has no .ref);
#   if a matching f.in exists, feed it on stdin; scrip --run f.pas vs f.ref
# Pascal M4: scrip --compile f.pas > p.s ; gcc -c p.s ; gcc -no-pie p.o -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out ; run vs f.ref
# Cross-lang (REQUIRED before committing anything in lower/ or emitter/):
#   scripts/test_crosscheck_snobol4.sh  (166/87/8, ~100s)
#   scripts/test_gate_template_medium_invisible.sh --strict  (0)
#   Icon/Prolog hello via direct --run
```

## Notes for next session

- The read1–4 probes need their `.in` stdin files (in corpus); the naive gate that pipes
  `/dev/null` to everything will show 4 spurious fails. Feed `f.in` when present (read1–4 pass).
- `lower.h` already pulls in `stage2.h`, so `g_stage2`/`ProcEntry`/`byref_mask` are visible in
  `lower_pascal.c` from the top (the `#include "stage2.h"` at l.~572 is redundant but harmless).
- `--dump-ast` segfaults on pointer/record programs (e.g. vpfld); it works on simple programs. The
  AST shape was confirmed from the parser productions instead (`selector ARROW` → `__pas_deref`,
  `selector PERIOD IDENT` with known rectype → `TT_IDX(__pas_deref(p), ilit(fieldidx))`).
