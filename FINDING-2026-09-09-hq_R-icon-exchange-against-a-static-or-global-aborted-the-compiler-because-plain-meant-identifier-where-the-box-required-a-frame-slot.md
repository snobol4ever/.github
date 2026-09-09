# Icon `:=:` against a static or global aborted the compiler — "plain" meant *identifier* where the box required *frame slot*

**hq_R, 2026-09-09. Cured in SCRIP (`lower_icon.c`), one file, no emitter change.**

## The witness

Ten lines, ablated from `corpus/packages/icon/ipl/procs/wrap.icn:89`
(`return "" ~== (s :=: line)`, where `line` is a `static`):

```icon
procedure p(s)
   static line
   initial line := "A"
   s :=: line
   return s
end
procedure main()
   write(p("B")); write(p("C"))
end
```

`icont` prints `A` then `B`. SCRIP did not print a wrong answer — it **aborted the
whole compile**:

```
FATAL emit_drive: IR op=123 has no template in the universal driver.
```

**CONTROL, the passing sibling with one ingredient removed:** the identical program
with `line` declared `local` instead of `static` compiled and ran before the cure
and is unchanged after it. One word is the entire difference.

## The cause

`lower_icon.c` called an exchange operand "plain" when it was a `TT_VAR` that was
not a keyword, and sent the pair to `IR_SWAP`. `IR_SWAP`'s drive case resolves
**both** operands through `bb_varslot_peek` and calls `drive_unowned` — which
`abort()`s — when either returns −1.

But an Icon `static` is mangled to a synthesized global (`icn_static_mangled`,
`wrap__STATIC__line`), and a global is not in the activation frame. Neither owns a
frame slot and **neither ever could**. The predicate and the box disagreed about
what the word "plain" guaranteed: lowering read it as *is an identifier*, the box
required *has a frame slot*.

## The cure

`plain` additionally requires `icn_is_local()` — the same local/non-local test the
assignment path at `lower_icon.c:438` already used. Non-locals now fall to the
`IR_SWAP_VAR` path immediately below, which already lowers arbitrary lvalues
through `lower_lvalue_var` and already handles statics via
`icn_variable_lit_target`.

⭐ **No emitter change and no new box.** The general path that handles this was
sitting three lines below the abort the whole time; the plain-path guard was
simply too wide. A missing-template FATAL is not always a missing template.

## What the class actually is

**Both kinds, not just statics** — measured on the baseline binary rather than
reasoned: a *global* exchange (`s :=: g`) aborts identically. The population is any
`:=:` with a non-local operand. 71 IPL files use `:=:`; roughly twenty also declare
statics, and several are `procs/` **libraries** (`wrap`, `strings`, `lists`,
`itokens`, `iolib`) linked by many programs, so a single library flips every
program that links it.

## Two traps worth carrying

⛔ **The op number in that FATAL is not stable across trees.** The same defect
prints `op=122` before SCRIP `2d4abc25f` and `op=123` after, because `IR_STMT_MARK`
was inserted into the enum. The message's own note is the reliable half: when `op=N`
plainly *has* a case, the **backtrace line** names the failing guard, not the number.
Chase the backtrace.

⛔ **A board run across a rebuild is not a board.** An 851-program IPL run was
started, `./scrip` was rebuilt mid-run, and the result was discarded rather than
reported: programs graded before the rebuild and after it were graded by two
different compilers, and nothing in the output would have said so.

## Arms

Icon master board both modes PASS=707/707 FAIL=0, ast-shape 153/153, entries=860
above floor 534. `ipl progs/ilnkxref` no longer aborts the compiler (rc=134 → rc=1)
and now fails on a **second, unrelated** defect behind this one (run-time error 103,
string expected) — named, not claimed. `lower_icon.c` is Icon-only, and the SNOBOL4
and Prolog masters emit **byte-identical** assembly across the change.
