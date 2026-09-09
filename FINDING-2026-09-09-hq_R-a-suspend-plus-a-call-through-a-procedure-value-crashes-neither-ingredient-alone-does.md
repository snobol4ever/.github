# FINDING 2026-09-09 hq_R — a `suspend` PLUS a call through a procedure VALUE crashes; neither ingredient alone does

**PRE-EXISTING, NOT CURED, NOT MINE TO CURE.** Measured on clean origin `cb993dd4c`.
Routed to the cto (procedure-generator frame tier, CEO-447) and hq_U (shared engine);
it is the concrete crash under hq_U's standing row
`icon-generator-through-a-procedure-value-is-ungraded-at-the-intersection`.

## The witness — the two ingredients, separated

```icon
procedure helper(m);
   return *string(m);
end
procedure v1(g, n);                                    # suspend + procedure VALUE -> CRASH
   local i, r;
   every i := 1 to n do { r := g(i); suspend r };
end
procedure v2(g, n);                                    # procedure VALUE, no suspend -> ok
   local i, r;
   every i := 1 to n do { r := g(i); write("  v2 ", r) };
end
procedure v3(n);                                       # suspend, DIRECT call -> ok
   local i, r;
   every i := 1 to n do { r := helper(i); suspend r };
end
procedure main();
   local x;
   write("v2:"); v2(helper, 2);
   write("v3:"); every x := v3(2) do write("  v3 ", x);
   write("v1:"); every x := v1(helper, 2) do write("  v1 ", x);
end
```

`icont` runs all three. SCRIP prints v2 and v3 correctly and **SIGSEGVs (rc=139) on v1**.
⭐ **The isolation is the finding:** the generator alone is fine, the procedure value alone
is fine, and the crash lives only at their intersection — so neither `suspend` nor
by-value dispatch is individually at fault, and grading either in isolation will keep
reporting green.

## Where it lands

```
#0  __printf_buffer_init (... buf=0x7fffffbf7038) at include/printf_buffer.h:137
#4  try_call_builtin_by_name_bl (fn="string", nargs=1, out=0x7fffffbf8b98, bidlen=393381)
      at src/runtime/by_name_dispatch.c:5223
#5  rt_call_arr_impl (...)  #6  rt_call_arr_bl (...)  #7  0x00007fffe9c001cb in ?? ()   <- emitted code
```

⛔ **The allocator is EXONERATED, and it is the obvious suspect, so this is worth writing
down.** `by_name_dispatch.c:5223` is `snprintf(buf,64,"%lld",…)` on a `buf` from
`rt_ws_alloc(64)`, so the first reading is "the workspace island returned a bad pointer".
It did not. Read at the fault:

| global | value |
|--------|-------|
| `g_wsi_base` | `0x7fffa9bff030` |
| `g_wsi_ws`   | `0x7fffa9c08810` |
| `g_wsi_wss`  | `0x7fffe9bfb7b0` |
| `g_wsi_end`  | `0x7fffe9bff030` |
| `buf`        | `0x7fffa9c087d0` |

`buf` is inside `[base, end)` and `g_wsi_ws` is exactly `buf + 0x40`, i.e. the 64-byte
bump that just happened. The slab is intact and the returned pointer is correct. The
faulting address in frame 0 is the `printf_buffer` STRUCT at `0x7fffffbf7038` — a C-stack
local, not the output buffer — so the fault is on the C stack under the emitted call, not
in the heap. `bidlen=393381` arriving as a builtin-id length is garbage from the same
place and is the second symptom of one cause.

⛔ The SIGSEGV handler in `rt_stack_overflow.c` does NOT report this: the process dumps
core with no diagnostic, so whatever this is, it is not being recognised as the stack
condition that handler exists for.

## How it was reached

`ipl procs/dif.icn` calls its grouping procedure through a value (`/group := groupfactor`,
then `gf := group(*difflist[1])`) from inside `dif()`, which is itself a generator
(`suspend result`) — the v1 shape exactly. `groupfactor` opens with `m := string(m)`, and
that is the by-name builtin call in the trace. `ipl progs/diffn` and `progs/diffu` both
crash there, identically.

⛔ **They only reach it after hq_R's `every … do break` cure lands** (see the companion
FINDING): before that, `dif()` never detected a difference and returned without ever
calling the grouping procedure. So the break cure does not CAUSE this crash — measured
absent-cure on `cb993dd4c`, the witness above still SIGSEGVs — it removes the earlier
wrong answer that was hiding it. Two IPL programs move from silently-wrong to crashing,
which is the same FAIL cell and a worse symptom, and is stated rather than buried.
