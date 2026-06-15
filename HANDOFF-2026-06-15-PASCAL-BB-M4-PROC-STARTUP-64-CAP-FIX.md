# HANDOFF 2026-06-15 — Pascal BB: M4 proc-startup 64-procedure registration cap removed (pcom first-output divergence CLOSED)

## TL;DR

One clean fix, one file touched (`src/driver/scrip.c`, **+6 −4**). The prior handoff's named NEXT
FRONTIER — "pcom M3/M4 first-output divergence: on tiny, M3 emits the 2-line source listing but M4
emits NOTHING (both rc=0)" — is **fully closed**. ROOT CAUSE: the mode-4 driver's shared
gvar-flat-chain emission block (`scrip.c` ~2520, serving Pascal AND SNOBOL4) registered each
compiled proc's function address (`rt_proc_set_fn`/`rt_proc_register`/`rt_proc_set_frame_bytes`)
through two **fixed-size `static int [64]`** side tables (`pidx_buf`/`peak_buf`) guarded by
`if (n_procs < 64)`. pcom has **103 procedures**; the emission loop still emitted all 103 proc
bodies (so the asm had every `<name>_α` label), but only the **first 64** procs were registered in
`proc_startup`. Calling any of the ~39 unregistered procs in M4 returned FAIL → the caller's
`cmp eax,99; je ω` dropped the rest of its statement chain. pcom's main body calls many procs (incl.
`initscalars`, the first setup call) before the first listing `write`; once an unregistered proc was
hit the chain died, so M4 produced no output. FIX: convert `pidx_buf`/`peak_buf` from `static int
[64]` to `malloc`'d arrays sized by `s2->proc_count` (an exact upper bound on the proc count), remove
the two `< 64` guards, `free` after the registration loop. Behaviour-neutral for ≤64 procs (the
common case, identical to the old static array), correct for >64. ZERO emitter/template/x86/binary
/runtime changes. Gates: Pascal **M3 126/0 · M4 126/0** (was 125/0 ×2; +1 new gated probe
`manyproc.pas`, zero regressions). SNOBOL4 M4 broad corpus **166 PASS** byte-identical to baseline;
SNOBOL4 `DOUBLE(21)=42` M3==M4; Icon `hello` M4 clean; template-medium-invisible `--strict` 0
violations.

## What landed (SCRIP `src/driver/scrip.c` ONLY)

The live mode-4 path for Pascal is the final `{ }` block at `scrip.c` ~2520 (the
`gvar_flat_chain_build_text_at` emitter, shared with SNOBOL4). The Icon/Raku block (~2336–2473,
which has its own identical `proc_names_buf[64][128]` cap) and the Prolog block (~2475–2518) return
earlier and are NOT reached by Pascal.

The block does two passes over `s2->proc_table`:
- **emission loop** (~2565): for every non-main, non-dup proc with a valid bb graph, emits the proc
  body via `gvar_flat_chain_build_text_at` (this loop is NOT capped — all 103 bodies emitted).
- **`proc_startup`** (~2603): emits, for each *recorded* proc, the runtime wiring
  `rt_proc_register` + `rt_proc_set_fn(name, &<name>_α)` + `rt_proc_set_frame` +
  `rt_proc_set_frame_bytes`. This is gated by what was recorded into the side tables.

The side tables `pidx_buf` (proc-table index) and `peak_buf` (per-proc frame-byte peak from
`g_last_flat_frame_bytes`, Session 60's mechanism) were `static int [64]`, appended under
`if (n_procs < 64)`. So `proc_startup` only ever wired the first 64 procs. `rt_proc_set_fn` is what
binds a proc *name* to its compiled *function pointer* for `rt_call_named_proc`; without it the
runtime cannot dispatch the call and the call FAILs.

**Diff:**
```c
-            static int pidx_buf[64];
-            static int peak_buf[64];
+            int _pbcap = (s2->proc_count > 0) ? s2->proc_count : 1;
+            int *pidx_buf = (int *)malloc((size_t)_pbcap * sizeof(int));
+            int *peak_buf = (int *)malloc((size_t)_pbcap * sizeof(int));
             int n_procs = 0;
 ...
-                { extern int g_last_flat_frame_bytes; if (n_procs < 64) peak_buf[n_procs] = g_last_flat_frame_bytes; }
-                if (n_procs < 64) pidx_buf[n_procs++] = _pi;
+                { extern int g_last_flat_frame_bytes; peak_buf[n_procs] = g_last_flat_frame_bytes; }
+                pidx_buf[n_procs++] = _pi;
 ...
                 printf("  pop rbp\n  ret\n");
             }
+            free(pidx_buf); free(peak_buf);
```

`s2->proc_count` is the total proc_table length; the number of recorded (non-main, non-dup, valid)
procs is ≤ that, so the buffers never overflow — no doubling idiom needed (cf. Session 61's dynamic
slotmap, which grew incrementally; here the bound is known up front).

## How it was found (triangulation)

1. Confirmed the documented frontier: pcom on `tiny` (`program t(output); begin end.`) — M3 emits
   the listing, M4 emits nothing, both rc=0.
2. Binary-searched the write path: isolated probes for the `endofline` write
   (`write(output,int:6,'  ':2)`), the nested `insymbol`→`nextch`→`endofline` chain, the `prr`
   external file var, `assign`/`rewrite`/`close`, and an `initscalars`-shaped setup proc ALL passed
   M4. So the *write emission itself* is fine — M4 control flow simply never reaches the write.
3. Instrumented pcom's main body with phase markers `[M0]…[M9]`: **M3 printed `[M0]…[M8]`, listing,
   `[M9]`; M4 printed only `[M0]`.** The chain died at the first setup call (`initscalars`).
4. Replicated `initscalars` in isolation → worked in M4. So the failure was *contextual to full
   pcom*, not intrinsic to the proc body → suspected a scale cap (cf. Session 61's 512 slotmap cap).
5. Grepped fixed-size caps; found `pidx_buf[64]`/`peak_buf[64]`. pcom has 103 procs.
6. **Confirmed with a clean probe**: a program with N trivial procs each `g:=g+1`, all called, then
   `writeln(g)`. M3 always correct; M4 correct for N≤64, **empty for N≥65**. Exact threshold 64.
7. After the fix: N=65,66,70,103,120 all M4==M3. pcom `tiny` M3==M4 byte-identical; marker probe
   M4 now prints `[M0]…[M8]`, listing, `[M9]`.

## Gated probe added

`corpus/programs/pascal/manyproc.pas` (+ `.ref`): 70 procedures `p1..p70`, each `g := g+1`, all
called from main in order, then `writeln(g)` → `        70` (width-10, ref from M3). This program
**failed M4 before the fix** (empty output, chain dropped at `p65`) and **passes both modes after**.
It is the only probe that exercises the >64-proc registration path. Gate is now **126/0** both modes.

## IMPORTANT correction to the prior frontier description (read before chasing pcom further)

The prior handoff also reported, as a secondary observation, that on richer input "M3 emits line 1
but M4 emits nothing." **That residual M4-vs-M3 difference is a stdout-BUFFERING ARTIFACT of the
test harness, NOT a real divergence.** Verified this session:

- On a `const`-containing program (`program t(output); const n = 3; begin end.`), pcom emits the
  line-1 listing then **stops** (rc=0). Captured through a pipe (block-buffered), M4 showed nothing
  while M3 showed line 1 — but under `stdbuf -oL` M4 shows line 1 too, and **M3 vs M4 are
  byte-identical (37 bytes each)**. pcom's early-termination path in M4 returns from `main` without
  flushing the block-buffered `output` stream; M3 (in-process) flushes. So there is **no remaining
  M4 codegen divergence** — the 64-cap fix closed it completely.
- (A `var`- or `for`-containing program runs further and is byte-identical M3==M4 with or without
  line buffering, because pcom doesn't terminate early on those — the flush happens normally.)

So: do NOT re-open "M4 first-output divergence." It is closed. Two follow-ups remain, in priority
order:

## NEXT FRONTIER — pcom terminates after the first source line on a `const` declaration (MODE-INDEPENDENT)

This is now the live pcom blocker and is **NOT a mode divergence** — M3 and M4 behave identically
(byte-identical output, rc=0). On any program whose first declaration is `const` (e.g.
`program t(output); const n = 3; begin end.`), pcom emits the line-1 listing then returns from main
early, emitting nothing further. The const-declaration parse path
(`block`'s `constsy` branch → `constdeclaration` → `constant` / `new(lcp,konst)` / `with lcp^ do …`
/ `enterid`) drops the statement chain (a statement FAILs → eax=99 → caller takes ω → early return).
`var`/`for`/`begin-end` programs do NOT trigger it (they run further). Suggested next:
- Instrument pcom's `constdeclaration` and `block`-const branch with `[Cn]` markers (writes) to find
  the exact statement after which the chain drops — OR
- Build a minimal probe mirroring the const path: `new(lcp,konst); with lcp^ do begin name := id;
  idtype := nil; next := nil; klass := konst end; enterid(lcp)` on a record with a variant/`konst`
  case (`identifier` in pcom has `konst: (values: valu)`), then a `constant`-style scalar store
  (`values.ival := …`), and see which sub-step FAILs in M3 (mode-independent, so M3 is enough to
  reproduce — no M4 needed for the hunt). This echoes the Session-55 nested-aggregate-store class
  (`gattr.cval.ival`) and the `konst: (values: valu)` variant field; the `with lcp^ do … klass :=
  konst` write into a variant-record field is the prime suspect.

## SECONDARY (only matters once pcom is gated) — M4 stdout not flushed on early-return

When an M4 program returns from `main` *early* (chain dropped), the runtime `output` stream (block
buffered when stdout is a pipe, as in the gate harness `got=$(... )`) is not flushed, so emitted
output is lost. Normal programs that run to completion flush fine (gate is 126/0). This only bites
programs that terminate early AND are captured through a pipe. If pcom is ever gated before the
const blocker is fixed, force `stdbuf -oL` or add an `atexit`/end-of-program flush to the M4 runtime
`output` path. Low priority — downstream of the const blocker.

## Validation log (this session)

- Pascal gate **M3 126/0 XFAIL=1**, **M4 126/0 XFAIL=1** (assemble+link+run, `-no-pie`,
  `out/libscrip_rt.so`). Was 125/0 ×2; +1 probe `manyproc.pas`, zero regressions.
- Proc-count sweep post-fix: N∈{64,65,66,70,103,120} all **M3==M4**.
- pcom on `tiny`: M3==M4 byte-identical (`     1        9 program t(output); begin end. `).
- pcom marker probe on `tiny`: M4 `[M0][M1]…[M8]` listing `[M9]` (was `[M0]` only).
- pcom on `const`-only: M3==M4 byte-identical 37 bytes (under `stdbuf -oL`).
- SNOBOL4 M4 broad corpus **166 PASS** (baseline 166, byte-identical pass set).
- SNOBOL4 `DOUBLE(21)` M3==M4 → `42`. Icon `hello` M4 → `hello`.
- `scripts/test_gate_template_medium_invisible.sh --strict` → 0 violations.

## Files touched

- `SCRIP/src/driver/scrip.c` — the fix (+6 −4).
- `corpus/programs/pascal/manyproc.pas` + `manyproc.ref` — gated >64-proc regression probe.
- `.github/GOAL-PASCAL-BB.md` — watermark → Session 63; this handoff referenced.
- `.github/HANDOFF-2026-06-15-PASCAL-BB-M4-PROC-STARTUP-64-CAP-FIX.md` — this file.
