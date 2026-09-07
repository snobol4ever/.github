# FINDING — `&FNCLEVEL` had NO write site at all: the role-4 shim is what a DEFINE'd call actually reaches, and the located cause on the baton was for the wrong mechanism

**hq_P · 2026-09-06 · MODE OCTET · row `conform-fnclevel-not-tracked` (ceo-365: the standing SNOBOL4 master red) · RT_OPT `-O0` · incremental `make` · oracle `/home/resources/x64/bin/sbl -bf`**

## The refutation first, because it is the transferable part

The baton carried a precise, gdb-backed root cause from 2026-09-04: trivial `DEFINE`'d procedures take `bb_tiny_shim_ok()`'s fast-call path, which has no `&FNCLEVEL` awareness, and so bypass `bb_define_activate`'s enter/leave pair that already maintains `kw_fnclevel`. The recommended cure was to make such programs ineligible for the tiny shim.

⛔ **One command refuted it on today's tree.** `SCRIP_NO_TINY=1` — the env switch that disables the tiny shim outright — still prints `inside=0`:

```
$ SCRIP_NO_TINY=1 ./scrip --run probe_loose_conformance_k10_fnclevel.sno
outside=0 / inside=0 / outside-after=0        (oracle: inside=1)
```

⭐ **A located cause that was never made to predict anything is a hypothesis wearing a diagnosis's clothes.** The gdb observation behind it — `watch kw_fnclevel` never fires — was *true and remains true*; what did not follow was the attribution. The watchpoint proves nobody writes the variable; it cannot distinguish *"the writer exists but this call path bypasses it"* from *"no writer is emitted at all"*, and only the second is the case.

## What is actually true, by asm grep on a five-shape witness

A witness with five `DEFINE`s (no-arg, one formal, one local, nested caller, repeat) emitted:

```
kw_fnclevel  occurrences in the .s : 6      <- and all six are READS, one per &FNCLEVEL in the source
rt_k_level_p occurrences in the .s : 0      <- the enter/leave pair is not emitted anywhere
```

So `&FNCLEVEL` is read correctly (`mov rcx, qword ptr [rip + kw_fnclevel@GOTPCREL]`) and **never written**. `bb_define_activate()` is a sibling mechanism for a different calling convention; the file's own TRACE-tap comment already recorded that it is *"confirmed unreached for a tiny-shim-eligible DEFINE'd proc"* and that **the role-4 SIG shim (`fnsig()`) is the one actually reached** — written for a different row, and exactly the fact this row needed.

## The cure

`bb_fnclevel_enter()` / `bb_fnclevel_leave()` — the pair `bb_define_activate` already carries inline, factored into one place so its two halves cannot drift — wired into the role-4 shim at **three** sites: entry (where the TRACE CALL tap sits, after the marshal-in), the gamma exit, and **the omega exit**.

⭐ **Omega is not optional here, and the TRACE row is the reason to say so out loud.** Its RETURN tap is gamma-only and its comment says so deliberately. For a *reporting* tap that is a defensible scope decision; for a *depth counter* an unbalanced exit is a leak — one `FRETURN` and every later reading of `&FNCLEVEL` is permanently one too high. Witness `h1.sno` exercises `RETURN`, `FRETURN` and `NRETURN` interleaved and is byte-identical to the oracle.

⛔ `kw_fnclevel` is written **through** `rt_k_level`, never alone: the tree's invariant is `kw_fnclevel == rt_k_level - 1` (`rt.c:515-516` / `526-527`), so a cure that bumped only the shadow would be silently reset by the next writer of either.

## The mistake I made, and the shape that hid it

The first cut assumed `rax` and `rcx` were dead at both exits. `rax` is. **`rcx` is not** — `SIGQ(d)` is `[rcx + d]`, not rsp-relative (the lambda at the head of the arm), so `rcx` is the signature-block **base**. The emitted asm said so plainly once looked at:

```
mov rax, qword ptr [rip + kw_fnclevel@GOTPCREL]
mov qword ptr [rax + 0], rcx
mov rcx, qword ptr [rcx + 8]      <- base taken from the value just written
```

⭐ **The symptom is the part worth remembering: a no-formals procedure survived it, and a one-formal procedure printed the correct answer and then SIGSEGVed on RETURN.** A register-liveness error at a return path reads exactly like a returning-path bug, and the correct output immediately before the crash argues *against* looking at the code that just ran. Both exits now save `rcx`; the entry site already did, because the TRACE tap beside it pushes `rcx` and thereby documents that it is live.

## Scope — the shared-node duty

`grep -c IR_DEFINE src/lower/lower_*.c` → `lower_snobol4.c` 9, **`lower_prolog.c` 1**, every other lowerer 0. So SNOBOL4, Snocone (which lowers through `lower_snobol4.c`) and **Prolog** are in scope, and all three are graded below.

## Cost — measured, because this seat owns the question

Callgrind Ir at fixed work, `-O0`, mode 3, same corpus, pre-cure vs cured binaries built from the same checkout:

| witness | pre | cured | × (pre / cured) |
|---|---|---|---|
| 100,001 bare calls | 275,749,740 | 278,050,089 | **0.9917x** |
| `func_call` | 28,542,403 | 28,973,546 | 0.9851x |
| `arith_loop` (1 DEFINE, 2 calls) | 23,440,944 | 23,654,941 | 0.9910x |
| `fib_recur` | 82,706,089 | 86,017,087 | **0.9615x** |

⭐ **Two terms, and they reconcile across all four rows rather than being fitted to one:** a per-call cost of **+20.9 Ir** — which is the 21 instructions added, so the run-time story is complete and has no residue — and a one-time **~214k Ir per `DEFINE`** of *compile*-time emitter work at `-O0` (`arith_loop`, with 1 DEFINE and 2 calls, is almost entirely this term; the 100k-call witness is `214k + 100001 × 20.9`). The worst case is deep recursion, where the call *is* the work: `fib_recur` at `0.9615x`.

⛔ **The zero-cost version needs a NEW GLOBAL and is therefore not mine to take.** The gate is the one the baton proposed — a per-compilation-unit flag, mirroring `g_sno_uses_stmtkw`, that skips the pair entirely for the overwhelming majority of programs that never reference `&FNCLEVEL`. That is file-scope mutable state, which needs Lon's explicit in-chat banner grant, so it is routed as an ask rather than folded in. I checked for a no-new-state route first and there is none today: `bb_define()` sees one graph, the keyword can be read from any other, and no whole-program accessor is exposed to the emitter.
