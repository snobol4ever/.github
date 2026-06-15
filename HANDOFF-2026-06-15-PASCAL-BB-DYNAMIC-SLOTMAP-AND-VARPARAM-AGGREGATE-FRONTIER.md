# HANDOFF 2026-06-15 — Pascal BB: dynamic slotmap/varslot (no hard caps); var-param-of-aggregate frontier

## TL;DR

One clean fix landed, one file touched. The `bb_gvar_assign call-result: op_a_slot==-1` BOMB
(the prior handoff's named NEXT FRONTIER) is **fixed** by converting the two fixed-size emitter
side tables (`g_bb_slotmap`, `g_bb_varslot`) from static arrays to dynamic `realloc`-grown arrays.
No more hard cap — they grow to whatever a proc needs and are reused across procs. Gates unchanged
at **M3 123/0 · M4 123/0**. With the slotmap wall gone, pcom advances and exposes the next
pre-existing frontier, now precisely diagnosed: **pass-by-reference of a record field inside a
heap-allocated pointer** (`genlabel(uprcptr^.pfname)`), which needs copy-in/copy-out.

## What landed (SCRIP `src/emitter/emit_bb.c` ONLY — zero template/x86/binary changes)

**Root cause of the bomb:** `BB_SLOTMAP_MAX 512` (a static `g_bb_slotmap[512]`). Every
`bb_slot_alloc*` / `bb_slot_register` guarded its append with `if (g_bb_slotmap_n < BB_SLOTMAP_MAX)`
— so past 512 entries the append **silently no-op'd**. For a large proc (e.g. `charA`-style ≥90
`array[char]` assigns, or any pcom proc), a call-result node's slot was therefore never recorded;
`bb_slot_get(callnode)` later returned −1 → `op_a_slot == -1` → the `bb_gvar_assign` IR_CALL arm
hit `x86_bomb`. Same class of latent cap as the patch-table (`BB_PATCH_MAX`) fixed in the prior
handoff.

**Fix (the directive was "use dynamic REALLOC arrays, don't hard-code limitations"):**

- `g_bb_slotmap`: was `static struct {…} g_bb_slotmap[512]`. Now a typed pointer
  `bb_slotmap_ent_t *g_bb_slotmap` + `g_bb_slotmap_n` + `g_bb_slotmap_max`, grown by a new
  `bb_slotmap_push(nd, off)` helper using the **doubling idiom already used by `emit_label_alloc`
  in this same subsystem** (`new_max = max ? max*2 : 512; realloc(...)`). All five appenders
  (`bb_slot_alloc`, `bb_slot_alloc16`, `bb_slot_alloc16_or_get`, `bb_slot_alloc24`,
  `bb_slot_register`) now route through `bb_slotmap_push`. The one inline push in
  `flat_drive_gen_scan` (was `… && g_bb_slotmap_n < BB_SLOTMAP_MAX) { g_bb_slotmap[…]=… }`) now
  calls `bb_slot_register(pBB, body_slot)`.
- `g_bb_varslot`: was `static struct {…} g_bb_varslot[256]`. Now
  `bb_varslot_ent_t *g_bb_varslot` + `_n` + `_max`, grown inline with the same idiom
  (`new_max = max ? max*2 : 256`). (Same cap class; would bite pcom-sized procs next.)
- **Reset semantics unchanged:** the per-proc resets still set only `_n = 0`. The `realloc`'d
  buffers persist with their `_max` capacity, so each table grows once to the largest proc and is
  reused for all others — no per-proc malloc churn. Stale pointers in `[n..max)` are never read.

`BB_SLOTMAP_MAX` / `BB_VARSLOT_MAX` are **gone** (grep == 0 in emit_bb.c). Diff: +28 −11, one file.

## Gate state at handoff (all green / no regression)

| Gate | Result |
|---|---|
| Pascal M3 `--run` | **123 / 0** (XFAIL=1 recursion.pas) |
| Pascal M4 `--compile`+as+link+run | **123 / 0** SKIP=0 (XFAIL=1) |
| SNOBOL4 M4 crosscheck | **166 / 87** SKIP=8 — byte-identical to baseline, same fail list |
| Icon `hello.icn` `--run` | `Hello, World!` |
| Prolog `hello.pl` `--run` | `Hello, World!` |
| SNOBOL4 DEFINE canary `DOUBLE(21)` | `42` (M3 and M4) — shares the gvar flat-chain driver + slotmap |
| template-medium-invisible `--strict` | **0 violations** |
| `git status` | only `src/emitter/emit_bb.c` modified |

NOTE: the watermark moved 122→123 vs the prior handoff because a probe was added to the corpus
between sessions; the baseline this session opened at 123/0 ×2 and closed at 123/0 ×2.

## New canaries (verify the wall is GONE, not moved)

- `charA N=90` (nested proc `ctypes` with 90 `chartp['x']:=N` assigns inside `outer`, called from
  main with `[S]/[A]/[B]/[E]` markers) → `[S][A][B][E]` in BOTH M3 and M4. (N=64 was the prior
  patch-table boundary; N≈90 was where THIS slotmap bomb began.)
- `charbig N=300` (300 distinct `array[char]` assigns) → `[S][A][B][E]` in BOTH M3 and M4. Proves
  the dynamic growth genuinely removes the limit rather than relocating it.

Reproduce: generate either program (single nested proc with N `chartp[c] := k` statements) and run
`scrip --run` / `scrip --compile`+as+link.

## NEXT FRONTIER (precisely diagnosed this session) — var-param of a heap-aggregate field

With the slotmap fixed, `scrip --run pcom.pas < tiny.pas` (tiny = `program t(output); begin end.`)
now advances much further and hits a **different, pre-existing** runtime bomb:

```
libscrip_rt: BOMB — marshal_varparam_addr: var-param arg is not a variable
```

**This is NOT introduced by the slotmap fix.** Verified by rebuilding the baseline (old static
slotmap): pcom bombs *earlier* there, at `op_a_slot==-1`. The slotmap fix is pure forward progress
that uncovers the next real construct.

**Exact culprit (instrumented, confirmed):** `procedure genlabel(var nxtlab: integer)` (pcom l.847)
is called as `genlabel(uprcptr^.pfname)` inside `with uprcptr^ do …` (pcom l.3787 and l.3793). The
`with` on a **dereferenced pointer** resolves the field `pfname` to
`arr_get(__pas_deref(uprcptr), pfname_idx)`. Because `nxtlab` is a **var** (by-reference)
parameter, the marshaller's byref branch calls `marshal_varparam_addr` on that `arr_get` node;
`marshal_varparam_addr` only handles `IR_VAR_FRAME` (162), `IR_VAR_FRAME_REF` (164), and named
`IR_VAR` (4) — an `IR_CALL` (9, `arr_get`) falls through to its final `x86_bomb`.

Diagnostic breakdown of ALL byref args emitted for pcom (one `--run` pass):
`91× IR_VAR_FRAME · 2× IR_VAR_FRAME_REF · 6× named IR_VAR · 2× arr_get(idx=0, callee=genlabel)`.
Only the 2 `arr_get` ones bomb.

**Why it's hard (the impedance mismatch):** the var-param ABI passes a **pointer to a 16-byte
descriptor cell** (`[aoff]={tag 0}`, `[aoff+8]={cell_addr}`); the callee dereferences it to
read AND write the actual location. Frame slots and gvars have a stable addressable cell
(`rt_gvar_cell` / `[r12+off]`). But `uprcptr^.pfname` is an element **inside an SOH-separated
record string** — there is no stable standalone 16-byte cell to take the address of. So the
existing cell-address mechanism cannot represent it.

**Recommended design — copy-in / copy-out as a PURE AST/LOWERING REWRITE (zero emitter risk).**
This was investigated and PROVEN this session. Rewrite the call

```
genlabel(p^.fld)   ⟶   tmp := p^.fld;   genlabel(tmp);   p^.fld := tmp;
```

The var-param then receives `tmp`, a frame-local (`IR_VAR_FRAME`, op 162) which
`marshal_varparam_addr` ALREADY handles — so NO emitter/template/x86/binary change is needed. This
is exactly the behavior-neutral-lowering pattern the Pascal frontend already uses throughout.

**PROOF-OF-CONCEPT (verified M3 AND M4 this session):** the manual rewrite
`t := p^.fld;  t := 42;  p^.fld := t;  writeln(p^.fld); writeln(p^.other)` prints `42` then `99`
(write-back lands in `fld`, sibling `other` untouched) in BOTH modes — i.e. both legs already work
with existing primitives:
- copy-in (deref-field read `t := p^.fld`) lowers fine;
- copy-out (deref-field write-back `p^.fld := t`) lowers to the existing `__pas_deref_set`/
  `__pas_field_set` path (the same one `ptr^.field := v` uses) and works.
So the ONLY missing piece is the automatic rewrite. Semantically exact for the alias-free case
(pcom's `genlabel` writes a fresh label int, no aliasing during the call).

**Concrete implementation plan (all in the parser/lower; no emitter files):**
1. **Where:** `pascal.y` `mk_call` (proc-call AST build) is the cleanest site — emit a
   `TT_SEQ_EXPR` of `[ TT_ASSIGN(tmp, arg) , <call with arg replaced by tmp> , TT_ASSIGN(arg, tmp) ]`
   when an argument is a byref lvalue that is an aggregate element. `lower_seq` already chains
   `TT_SEQ_EXPR` through `IR_CONJ`, so the sequencing is free.
2. **Byref test:** the callee's mask is in `g_stage2.proc_table[pi].byref_mask` (look up by name;
   `proc_table` also carries `name`/`nparams`). If the parser can't see the callee signature yet
   (forward calls), do the rewrite in `lower_pascal.c` `lower_call` instead, which definitely has
   `g_stage2` available (it reads `proc_table` at l.585-598 already).
3. **"Aggregate element" test:** the arg lowers to `arr_get(...)` (record/array element) or
   `arr_get(__pas_deref(ptr), idx)` (deref-field, the pcom case). A plain `IR_VAR`/`IR_VAR_FRAME`
   arg must NOT be rewritten (those already work — don't regress the 99 working byref args).
4. **Temp:** synthesize a unique frame-local name (e.g. `__pas_vptmp_N`); it becomes an
   `IR_VAR_FRAME` slot via the normal local mechanism. One temp per such argument per call site.
5. **Write-back store:** for the deref-field case use `__pas_deref_set`/`__pas_field_set`
   (`p^.fld := tmp`); for an array element use `arr_set_pure` (`a[i] := tmp`). Both already exist.

**Isolated gated probe (ADD to corpus, reproduces the bomb today, expected `42`/`99` after fix):**
```pascal
program vpfld(output);
type rec = record fld: integer; other: integer end; pr = ^rec;
var p: pr;
  procedure genlabel(var nxtlab: integer); begin nxtlab := 42 end;
begin new(p); p^.fld := 7; p^.other := 99; genlabel(p^.fld);
  writeln(p^.fld); writeln(p^.other) end.
```
Gate it M3/M4 + fpc cross-check (ref is fpc-derived but integer output → take from M-mode at
width-10 per the .ref convention) BEFORE touching pcom further. Also add an array-element variant
(`genlabel(a[i])`) to cover `arr_set_pure` write-back.

Repro of the pcom bomb: `cd corpus/programs/pascal && printf 'program t(output);\nbegin end.\n' >
/tmp/tiny.pas && scrip --run pcom.pas < /tmp/tiny.pas` (vs a clean baseline build for contrast).

## LESSON (logged — bit me this session, costs real time)

**A failed `make -j4 scrip` leaves the PREVIOUS good `scrip` in place** (the binary is not removed
on compile error), so subsequent runs silently use a **stale binary** and instrumentation appears
not to fire. A scope-bug in a one-off diagnostic patch (`{…}` block breaking a `for`-loop variable)
failed the build for several iterations while I read stale output. ALWAYS `rm -f scrip` before
`make` (the GOAL landmine #1 is real) AND confirm `[ -x scrip ]` plus a fresh build log after every
template edit — do not trust a run whose build you didn't just confirm succeeded.

## Build / gate quickrefs

```
cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
# Pascal M3:  loop corpus/programs/pascal/*.pas (skip pcom/pint/ppp; recursion=XFAIL); scrip --run f.pas vs f.ref
# Pascal M4:  scrip --compile f.pas > p.s ; gcc -c p.s ; gcc -no-pie p.o -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out ; run vs f.ref
# Cross-lang (REQUIRED before committing shared emit_bb.c): scripts/test_crosscheck_snobol4.sh (166/87/8),
#   scripts/test_gate_template_medium_invisible.sh --strict (0), Icon/Prolog via direct --run.
```
