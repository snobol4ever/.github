# Every Icon &trace line in mode 3 names the LAST-compiled procedure, because the BINARY medium bakes a dead stack pointer

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-09 · **Lane:** the &trace class (Arizona M-Z)
**Build graded on:** incremental `make`. `RT_OPT` = `-O0`. NOT YET CURED — this is the diagnosis; the cure is my next row.

## The witness

Three procedures, `main` calls the FIRST one. `iconx` v9.5.25a is the oracle.

```icon
procedure main()
   &trace := -1
   aa()
end
procedure aa()   return 1   end
procedure bb()   return 2   end
procedure cc()   return 3   end
```

```
ORACLE            nm3.icn : 3  | aa()          nm3.icn : 6  | aa returned 1
SCRIP mode-3      nm3.icn : 3  | cc()          nm3.icn : 6  | cc returned 1     <- WRONG
SCRIP mode-4      nm3.icn : 3  | aa()          nm3.icn : 6  | aa returned 1     <- CORRECT
```

Every trace line names `cc` — the **last** procedure compiled, not the one running. The line numbers, the depth bars
and the returned *values* are all correct; only the NAME is wrong, which is why it survives a board that greps for
crashes. With a single non-`main` procedure the bug is INVISIBLE (last == only), and that is exactly the shape a
minimal witness reaches for first.

## Root cause — a BOTH-MEDIUM violation, TEXT correct and BINARY wrong

`icn_trace_tap()` (`src/emitter/emit.cpp:2789`) builds the tap once for both mediums:

```cpp
+ x86("directive", (fl + ": .string \"" + pname + "\"").c_str()) ...
+ x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t)pname, fl.c_str());
```

- **TEXT (mode 4)** takes the `.string` directive: the bytes are **copied** into `.rodata`, one label per tap
  (`.Licn_trace_nm0: .string "aa"`, `..nm14: "bb"`, `..nm28: "cc"` — verified in the emitted `.s`). Correct.
- **BINARY (mode 3)** takes the operand: it bakes `(uintptr_t)pname`, the emit-time **pointer**, into the sealed slab.

That pointer's provenance is the defect. `pname` traces back through `g_emit.flat_fam` (`xa_flat.cpp:434`) and
`codegen_flat_chain_body`'s `prefix` to `src/driver/scrip.c:1751`:

```c
char _m3pfx[300]; snprintf(_m3pfx, sizeof _m3pfx, "proc_%s", pname);
... emit_chain(bb_proc_entry(&s2->proc_table[_pi]), NULL, _m3pfx);
```

`_m3pfx` is a **stack buffer declared inside the per-procedure loop**. It is overwritten on the next iteration and
dead once the loop exits. The slab keeps the address. At run time every tap dereferences that one stack slot and
reads whatever last landed there — the last procedure emitted. Three witnesses agree: one proc -> correct,
two procs -> both read `beta`, three procs -> all read `cc`.

## Why no gate caught it

The BOTH-MEDIUM law is policed by `test_gate_template_medium_invisible.sh` and by the ban on `MEDIUM_*` inside
`bb_*.cpp`. This function contains **no `MEDIUM_*` branch at all** — it is medium-complete by construction and passes
every structural check. The divergence is not in the control flow; it is in the **lifetime of a value one arm captures
by reference and the other copies**. A structural gate cannot see that.

## The reusable lesson

⭐ **"Both mediums take the same branch" is not "both mediums are correct."** When one arm *copies* bytes and the other
*captures a pointer*, the two arms have different lifetime requirements even though they have identical control flow —
and only the capturing arm can be broken by a caller's stack frame going away. Any `x86(...)` operand built from
`(uintptr_t)<some char *>` is a lifetime contract with every caller of that emitter, and nothing in the type states it.

⭐ The second half is the witness lesson, the same one as this session's bar cure: **a one-procedure witness cannot
distinguish "the right name" from "the last name."** Mint the sibling where the two answers differ.

## Owed next

Cure candidates, cheapest first: intern the name in compiler-owned storage that outlives emission (the emitter already
owns per-graph name storage via `zls_graph_name`), or hoist `_m3pfx` out of the loop into a stable per-procedure
allocation. NOT hoisting alone — a single hoisted buffer is the same bug with a longer fuse. Neither touches frame
code, so both are clear of the CEO-447 freeze.
