# FINDING — quick.pas's partition conditional has the identical IR shape as bubble's i=89 defect, but CANNOT exhibit it: `qsort` is a framed procedure with one fixed-size stack frame, and the i=89-class mechanism only bites where `zd_plan`'s computed pop is actually emitted as a literal rsp instruction

Row: `pascal-m4-site1-forloop-backedge-64byte-excess` (seat04, FLEET-16 per live MODE at claim time), answering
NEXT ACTOR item 1 from seat09's FINDING ("quick.pas's own pivot/partition conditional is a very plausible
second instance of this exact mechanism — worth checking with the same breakpoint-the-two-arms technique").
Fresh pull first: `.github` was behind origin and was actually missing seat09's own cited FINDING file until
pulled (`1a52bf07..3e2f457d`); `SCRIP` was one commit behind (`ae078681`, touching only `bb_match_fence1.cpp`
— unrelated to Pascal/emitter, confirmed via `git log 18f7125e..HEAD -- src/emitter/emit.cpp src/frontend/pascal/
src/templates/`). `make pristine` before measuring.

## 0. THE NODE, IDENTIFIED AND STRUCTURALLY MATCHED TO BUBBLE'S i=89

`SCRIP_ZD_MAP=1 SCRIP_ZD_DIAG=1 ./scrip --compile quick.pas`, cross-checked directly against `--compile -o
/tmp/quick.s`'s own node labels — the same `i=<NN>` ↔ `n<NN>` correspondence seat09 found for bubble holds
here for `qsort`'s own nodes (emitted first, numbered from 0). qsort's body has exactly 6 `IR_BINOP_TEST`
nodes (n16, n25, n32, n59, n62, n68), matching its 6 source conditionals one-for-one in emission order:
`while sortlist[ii]<x do ii:=ii+1` (n16), `while x<sortlist[jj] do jj:=jj-1` (n25), **`if ii<=jj then begin
... end` (n32)**, the repeat-loop's own `until ii>jj` back-edge test (n59), and the two recursive-call guards
`if l<jj then qsort(l,jj)` / `if ii<r then qsort(ii,r)` (n62, n68).

n32 (`g=33 o=57`): gamma enters the swap body (`n33`..`n56`, 24 nodes — `w:=sortlist[ii];
sortlist[ii]:=sortlist[jj]; sortlist[jj]:=w; ii:=ii+1; jj:=jj-1`); omega skips directly to `n57`, the first
node of the `until` test's own operand setup. Confirmed directly off the `.s`: `cmp rax,rcx; jg n57_var_α` /
fallthrough to `n33_var_α`. **Identical shape to bubble's i=89**: if-with-no-else, asymmetric arms (24 nodes
vs. 0), same pass-0 run (no cross-run reference — `zd_plan`'s claim for n32 and n57 is the same run), omega
skipping straight to the eventual reconvergence point.

## 1. BUT qsort's entire body carves NOTHING dynamically — it is FRAMED, not FLAT

Exhaustive grep of every `sub rsp`/`add rsp` across `FN__qsort`'s full emitted range (`n0` through its
epilogue): **exactly one `sub rsp, 1632` at entry, matching `add rsp, 1632` at each of its two exits** (plus
small `+8` adjustments on those same two paths — ordinary frame/alignment bookkeeping) — **zero
stack-pointer instructions anywhere inside the body**, including the entire 24-node swap span (n33-n56) and
every back-edge/call site. Every node inside the procedure addresses its storage via a fixed `[rsp+K]` offset
into the one pre-sized frame; none of them individually carve or release.

This contrasts directly with bubble.pas, and with quick.pas's **own top-level program body** (labeled `main:`
in the same `.s`, `sub rsp, 65544` once at entry) — whose statements afterward *do* use bubble's incremental
per-node convention (confirmed `sub rsp,16`/`add rsp,16` pairs around the flat body's own nodes, e.g.
n182/n183, `jmp flat_ω`-terminated). The linked runtime pulls in both `bb_glue_flat.o` and `bb_glue_framed.o`
— evidently procedures compile through the framed convention and only flat (no-procedure, top-level) regions
use the incremental carve/release convention seat09's mechanism depends on.

**`zd_plan` still computes `zgpop`/`zwpop` for qsort's internal nodes** (confirmed in the
`SCRIP_ZD_DIAG=1` dump — n32 itself reads `zgpop=0 zwpop=0`, same as bubble's i=89) **but those values are
never emitted as instructions here.** The over-release mechanism requires a literal `add rsp,<wrong
constant>` at a back-edge/exit; framed procedures don't emit any such instruction for their internal nodes
at all, so there is nothing for a wrong constant to corrupt.

## 2. GDB-CONFIRMED: zero $rsp drift across the full run, swap-taken and swap-skipped alike

Built a real linked binary (`gcc -no-pie -g quick.s -lscrip_rt`) and breakpointed `n33_var_bx` (swap entry)
and `n57_var_bx` (reconvergence point), logging `$rsp` on every hit, full run to completion (`echo 1 |`,
`setarch -R`):

```
SWAP_ENTRY rsp=0x7ffffffe9940
N57_HIT    rsp=0x7ffffffe9940   <- swap happened; same value
SWAP_ENTRY rsp=0x7ffffffe9940
N57_HIT    rsp=0x7ffffffe9940   <- swap again; same value
N57_HIT    rsp=0x7ffffffe9940   <- NO swap this time; STILL the same value (contrast bubble's own +0x120 here)
```

All 13 distinct `$rsp` values observed across the whole run are recursion-depth markers (each exactly
0x670=1648 bytes apart, matching qsort's own frame size plus call overhead), not per-iteration drift — and
at every depth, `SWAP_ENTRY` and `N57_HIT` addresses are byte-identical regardless of how many (or how few)
swaps happened in between. **Zero drift, full population, not a sample — the static finding holds
dynamically exactly as predicted.**

Process exited normally (rc=0); output reproduced exactly as every prior session measured (`10414` vs.
`.ref`'s `15505`), m3 reconfirmed clean (`15505`, matches `.ref`) — both consistent with the known baseline,
confirming nothing else shifted under this investigation.

## 3. WHAT THIS ANSWERS, AND WHAT IT DOESN'T

**NEXT ACTOR item 1 is answered, and the answer is no, for a structural reason, not an absence of
evidence:** quick.pas's partition conditional has the identical IR shape as bubble's defect but cannot
physically manifest the bug, because `zd_plan`'s wrong pop constant is only dangerous in flat-glued code,
and `qsort` — a recursive procedure — is framed. **Worth generalizing: seat09's FINDING (§3) conjectured the
i=89-class mechanism is general to "any embedded if-with-unequal-arms inside a continuous run" — true of the
IR shape, but the actual risk is further conditioned on which calling convention lowers that run, and framed
procedures are categorically immune.**

As a cheap adjacent check (not the full dynamic treatment): the main program body's own analogous
construct — `if sortlist[i]>biggest then ... else if sortlist[i]<littlest then ...` (n231/n240, flat-glued,
confirmed via a consistent `i=<local>+182` ↔ `n<global>` offset against n192/n203/n231/n240) — already gets
clean `[ZD-FINAL]` treatment from both exits (`gback`/`oback` both populated), mirroring bubble's own
now-resolved confusion about its structurally identical construct. So this doesn't look like the residual
defect site either, **though it was not dynamically re-verified this pass** (static `SCRIP_ZD_DIAG` reading
only).

**NOT attempting a fix** — nothing to fix in qsort for this mechanism, and the row's own standing
authorization for the actual Site-1 repair remains reserved for hq_C/hq_P's calling-convention-depth-tracked
design regardless.

**NEXT ACTOR item 2 (quick's m3-clean/m4-wrong-output asymmetry) remains completely open** — if anything,
narrower now: the two most obvious flat-vs-framed candidates in quick.pas (qsort's own partition conditional,
and main's biggest/littlest) are both ruled out or already correctly handled, so the actual defect causing
`10414` vs `15505` is somewhere else in the main body (the two `for`-loop tests themselves, the qsort
call-site/return interaction, or argument marshalling into the recursive calls — none characterized this
pass).

## What the next actor gets for free

- **The flat/framed split matters for this whole defect class.** Before assuming an IR shape with the right
  diamond pattern is a live instance of Site 1's bug, check whether the enclosing code region is flat-glued
  (top-level program body — vulnerable) or framed (a procedure — immune, because no per-node rsp
  instructions are emitted at all). `grep -c "sub .*rsp\|add .*rsp"` over a procedure's own `.s` range is a
  one-line test.
- qsort's 6 `IR_BINOP_TEST` nodes, by source line and emission label, for whoever needs them again: n16/n25 =
  the two `while` tests, **n32 = the partition conditional**, n59 = the repeat-loop's own back-edge test,
  n62/n68 = the two recursive-call guards.
- The `i=<NN>` ZD-MAP index ↔ global `n<NN>` emission label correspondence seat05 flagged as tree-fragile
  holds for qsort (offset 0) and for quick's main body too, but with a non-zero, also tree-fragile offset
  (**+182** — confirmed by matching all four of i=10/21/49/58 against n192/203/231/240 exactly). Do not
  assume offset zero generalizes to every scope — recompute it per scope before trusting it.
- Not independently re-verified: whether the two `for`-loop tests themselves (n192 "for rep", n203 "for i")
  have any asymmetry-of-arms issue of their own, distinct from the reconvergence-gate question seat08 already
  closed for them.

Tree byte-identical to origin throughout (only `/tmp` scratch: quick.s, the gdb binary, gdb command file; no
tracked file touched by the investigation itself).
