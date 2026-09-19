# FINDING — THE ALLOCATING SET MISSED EVERY TAIL-JUMP ALLOCATOR, AND 27 CALL SITES WERE OUTSIDE THE DENOMINATOR (cto, 2026-09-18)

**CURED IN THE SAME LANDING** (SCRIP `9f7dec1b3`, design § 6.5d, gate WIRED 415). Written down because the SHAPE
is the recurring one and the number it corrupted is the one the whole GC emergency is steered by.

## What was wrong

`util_gc_census.allocating_entries_from_binary` derived "every function that reaches `rt_gcheap_alloc`" from
`objdump -d`, recording **`call` edges only**. The hand-written asm allocators in `src/runtime/rtx/rtx_alloc.s`
reach the carve by a **tail jump**:

```
RTX_FUNC(rt_str_alloc)
    RTX_GATE(alloc, c_rt_str_alloc)
    mov     r10, [rip + g_hp_fr@GOTPCREL]
    mov     eax, dword ptr [r10 + 24]
    test    eax, eax
    je      c_rt_str_alloc          <- the C fallback, by a conditional JUMP
    ...
    jmp     .Lga_armed              <- the inlined bump, by a JUMP
RTX_ENDF(rt_str_alloc)
```

Neither path executes `call rt_gcheap_alloc`. So `rt_str_alloc` and `rt_agg_alloc` read NON-ALLOCATING, and so
did everything reaching the heap only through them.

## Measured, SCRIP `4e1683fa9` → `9f7dec1b3`

| | call edges only | + inter-function tail jumps |
|---|---|---|
| allocating functions (of 8565) | 1584 | **1683** (+99) |
| emitter allocating call sites | 210 | **237** (+27) |
| `safe-points.unpolled` | 97 | **123** (+26) |

The 99 include the SNOBOL4 string builtins — `DUPL_fn`, `REVERS_fn`, `SUBSTR_fn`, `TRIM_fn`, `BCHAR_fn`,
`_CHAR_`, `_COLLECT_`, `_ITEM_`, `_INTEGER_`, `_REAL_` — 85 call sites reach `rt_str_alloc@plt` and 28 reach
`rt_agg_alloc@plt` inside the runtime alone.

## Why a tail jump is an edge for this question

Control reaches the target, the target may allocate, and it returns **past us to our caller** with the caller's
frame live. That is exactly the condition a safe point exists for. It is not an over-approximation: `objdump`
prints an intra-function jump as `<fn+0xNN>`, the symbol pattern refuses a `+`, and a self-edge is dropped — two
planted selftest arms hold both directions (a tail-jump-only allocator must enter the set; a looping function
must not).

## The shape, which is the reason this is a FINDING and not just a fix

Three instruments in two days have reported success while measuring a population that did not contain the thing
they grade — the misaligned conservative scan (§ 6.8b), the callee-saved census reading `heap=0` (§ 6.5c), and
this one. All three were GREEN. The question that catches the class is not "is the criterion right" but
**"does this instrument's population contain an instance of what it grades?"** — and here the answer was that an
entire allocator implementation strategy was invisible to the derivation because of one mnemonic.

⛔ **It was found only because the set was being written out as a table for a second consumer.** A derivation
used by one reader is never cross-checked; the gate now holds the table and the census to the same population
(`ONLY_TABLE=0 ONLY_CENSUS=0`) and names `rt_str_alloc` and `rt_agg_alloc` in the table by name, so the
narrowing cannot come back in silence.
