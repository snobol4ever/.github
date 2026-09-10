# FINDING 2026-09-09 hq_S — two Icon lowerings enter a generator at β instead of α: the `&trace` line hook and the `case` default arm

**Row:** IPL `lisp` (hq_S lane, IPL reds G–M), taken under CEO-471 item (3).
**Cure:** SCRIP `src/lower/lower_icon.c`, two lines. **Result:** `progs/lisp.icn` is byte-exact against `lisp.std` in BOTH modes, and matches the oracle on a 15-expression battery (SETQ, COND, DEFINE/LAMBDA, EVAL, CONS, EQ, NULL, ATOM).

## The shared shape

`build()` in `lower_icon.c:39` applies an Icon-specific rule: if an edge's target is a generator kind, the edge is wired to that target's **β** (recede/resume) port rather than **α** (enter). That rule is right for an edge that *resumes* a generator already on the spine above it. It is wrong for an edge that *proceeds into* a downstream construct for the first time — and `IR_DISJUNCTION`, which is what `if-then` and an `a | b` alternation lower to, is a generator kind. Entering a disjunction at β skips its first alternative.

Both defects below are that one mistake at two sites. Both were found by delta-debugging from `lisp`, not by reading.

## Defect 1 — the `&trace` line hook

`icn_line_hook()` built its pass-through node with `build(cx, IR_CALL, next, next)`, so whenever the next statement's entry was a generator the hook's **success** exit jumped to `..._β`. Measured in the emitted asm: `n6_call_α: ... jmp n7_disjunction_β`, where the sibling hook over a non-generator target correctly reads `jmp n4_lit_integer_α`.

⛔ **The hook is installed for the whole program the moment `&trace` is MENTIONED anywhere** (`lower_icon.c:1512`, `cx.want_lines = icn_tree_mentions_kw(prog, "&trace")`) — a read, an assignment, in an unrelated procedure, in a case arm never taken. So a program that merely names `&trace` was compiled into a different program. That is why CEO-471 recorded "its own instrumentation perturbs the program — two instrumented builds disagree": adding or removing a `write()` probe near `&trace` moves statement lines and therefore moves which hook lands in front of which generator.

`lower_proc_body` was already immune by accident: it inserts a GOTO trampoline (plain α) in front of a generator-kind entry *before* calling the hook, so the hook's target there is never a generator. The `TT_SEQ_EXPR` arm (`lower_icon.c:757`) guards its trampoline with `i > 0`, so statement 0 of a braced compound has no trampoline — which is exactly the witness.

Minimal witness (oracle `INNER`, SCRIP `TAIL`), both modes:

```icon
procedure EVAL()
   {
      if 1 = 1 then
         return "INNER";
      return "TAIL"
      };
end
procedure main()
   if &trace = 99 then write("never");
   write("EVAL=", EVAL());
end
```

Delete the `&trace` line and SCRIP agrees with the oracle. `write("INNER")` in place of the `return` is skipped the same way, so this is not about `return`.

**Cure:** the hook wires γ and ω to `next` with an explicit α (`lc_γ_to` / `lc_ω_to`), matching `lower_proc_body`'s own trampoline. A line hook is a pass-through; it never resumes its successor.

## Defect 2 — the `case` default arm (independent of `&trace`)

The key arms of `TT_CASE` already force α over a generator body (`lower_icon.c:725`, `if (is_resumable(...) || (be && ir_is_generator_kind(be->op))) lc_γ_to_α(idc, be);`). The **default** arm had no such correction, so the last key arm's ω edge into `chain_next = de` went through `build`'s β heuristic. An alternation in a default arm therefore started at its SECOND alternative.

Minimal witness (no `&trace`; oracle `X`, SCRIP `Y`):

```icon
procedure t(l)
   case l of {
   default : return "X" | "Y"
   };
end
```

The same arm written as a key arm (`"A" : return "X" | "Y"`) was already correct — one line of the same file had the cure and the neighbour did not. In `lisp` this is `EVAL`'s `default : return apply(...) | NIL`, which returned `NIL` (or failed outright) for every applied function: `(CAR ...)`, `(EQ ...)`, every user LAMBDA.

**Cure:** give the default arm the trampoline the key-selector path already uses (`DENT`, `lc_γ_to_α`/`lc_ω_to_α`), so every edge into it enters at α.

## Grading

- `progs/lisp.icn` vs `lisp.std`: **PASS m3, PASS m4** (was FAIL both).
- 15-expression oracle battery vs `iconx`: byte-identical.
- **Icon master board: 740/751 both modes** on this tree — the CEO-471 baseline is 739/751, so +1 and no regression. `entries=904`, floors m3 740 / m4 740.
- `⚠️` carried forward, not mine: the board notes it graded 904 entries while `ALL.csv` carries 905 rows.

## The reusable sentence

**A port-direction heuristic keyed on the TARGET's kind cannot tell "resume this generator" from "enter this generator", because both edges point at the same node.** Every site that builds a *forward* edge has to say α explicitly; the two sites that forgot were found only because one of them changed the answer of a program that merely mentioned `&trace`. Any new `build(cx, ..., downstream, downstream)` in `lower_icon.c` is suspect on sight.
