# FINDING: Icon `&trace` of a call WITH AN ARGUMENT dies in a misaligned SSE store, and every trace line loses its `&level` bar

**Seat:** hq_B · **Date:** 2026-09-09 · **Tree:** SCRIP `01eb996ca`, corpus `0f5effdc7`
**Lane:** CEO-445 Arizona reds M-Z. **Program:** `arizona_tests/general/tracer.icn` (rc=139).
**Status:** root-cause MECHANISM proven, cure NOT in hand. Handing on rather than guessing.

## The witness — 7 lines, deterministic, both modes

```icon
procedure main()
   &trace := -1;
   f(1);
end
procedure f(a)
   suspend 9;
end
```
`scrip p_fail.icn` → **SIGSEGV rc=139**, m3 and m4 alike. icont/iconx 9.5.25a prints:
```
p_fail.icn   :    3  | f(1)
p_fail.icn   :    6  | f suspended 9
p_fail.icn   :    4  main failed
```

**The passing sibling differs by exactly one ingredient** — the traced procedure takes no parameter:
`procedure f()` / `suspend 9` runs clean. `return a` instead of `suspend` also runs clean.
So the crash needs: `&trace` on **+** the callee `suspend`s **+** the call passes ≥1 argument.

## What is proven

The path is `generated code → rt_proc_call_open_det → rt_proc_call_prologue_lex` (`rt.c:1618`)
`→ rt_trace_event_args → trace_print_icon` (`core.c:156`) `→ image` builtin
`→ by_name_dispatch.c:5311 snprintf(buf,256,"%lld",…)` → **`movaps %xmm0,-0xc0(%rbp)`**.

⭐ **It is a #GP from a misaligned SSE store, NOT a page fault and NOT stack exhaustion** — and the two
read identically as SIGSEGV, which is why this is worth writing down:
- `(rbp - 0xc0) % 16 == 8` at the faulting instruction. `0xc0` is a multiple of 16, so `rbp` is 8-mod-16.
- `si_addr == 0x0`. A page fault reports the address; a #GP reports zero. **The zero is the evidence.**
- Not exhaustion: 12,648 bytes of *mapped* stack remained below `rsp` at the call, `ulimit -s` is 8 MB,
  and the write target was inside the mapping. I chased exhaustion first — 4.02 MB was already consumed —
  and it was a red herring. **Consumed stack is not the same question as "did this write run off the end".**
- `rt_proc_call_open_det`'s TRUE entry (`break *rt_proc_call_open_det`, not `break rt_proc_call_open_det`)
  reads `rsp % 16 == 8`, which is the CORRECT SysV state. ⛔ My first parity reading was taken at gdb's
  post-prologue breakpoint and was therefore not the entry value at all — `break func` skips the prologue,
  so it silently answers a different question than the one alignment work needs asking. Use `break *func`.

This is the same family the emitter already documents at `bb_call_proc_staged.cpp:375` (the "N-2 ABI WORD"
row): a lone 8-byte push flips call parity, **stays latent until some callee reaches an aligned SSE store**,
and dies deep inside `snprintf`. That row cured the armed generator call site; the pads are present and
correct in this witness's emitted asm (`sub 8` + `sub 8` + `push` = 24 B, leaving 0-mod-16 at the `call`).
So this is that class at a site the earlier cure did not reach. **Where the 8 bytes are lost between the
correctly-aligned runtime entry and the faulting store is exactly what is NOT yet established** — every
intervening frame is ordinary gcc-compiled C, which should preserve alignment, and that contradiction is
the open question. Do not assume the earlier fix's location; re-derive it.

## A SECOND, SEPARABLE DEFECT on the same line — cheaper, and provable on its own

`trace_print_icon` (`core.c:152`) prints the `&level` indentation as
`for (int k = *rt_k_level_p - 1; k > 0; k--) fputs("| ", stderr);`
Measured at the trace call: **`*rt_k_level_p == 1`** where the oracle's output implies 2 — so **zero bars
print, and every Icon `&trace` line in the corpus is missing its `| ` prefix.** This shows up in the
NON-crashing sibling too (`f()` prints `f()` where iconx prints `| f()`), so it is independently
reproducible without touching the alignment bug. The entry-side `&level` increment in `emit.cpp` is gated
on `_iws && _use_zframe_install && !root_graph`; this call arrives through `rt_proc_call_prologue_lex`
instead, which never increments. ⭐ **Fix this one first**: it is one defect, one site, provable against a
one-line witness, and it is very likely a share of the 17 Arizona reds on its own — `tracer` cannot pass
on the crash cure alone, because every one of its 85 expected lines carries the bar.

## Disposition

Not cured this sitting; no code changed. `tracer` remains red. Arizona stands at m3 73/90, m4 73/90
(`test_icon_arizona_suite.sh`, SCRIP `01eb996ca`), reds `args cfuncs coexpr errors evalx extlvals fncs
gener ilib misc recent sorting struct tracer transmit traps var` — M-Z mine, A-L the cfo's.
