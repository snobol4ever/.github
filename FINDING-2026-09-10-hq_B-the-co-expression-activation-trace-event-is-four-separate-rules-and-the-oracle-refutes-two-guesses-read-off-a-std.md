# FINDING 2026-09-10 hq_B — the co-expression activation trace event is four separate rules, and the oracle refutes two guesses read off a `.std`

**Row:** `icon-arizona-jcon-class-trace-and-error-diagnostics` (tracer + transmit). **Cause cured:** transmit's SECOND cause (CEO-483) — SCRIP emitted no co-expression activation trace event at all, 70 of `transmit.std`'s 104 lines.

**Result:** `transmit` matches `transmit.std` BYTE-EXACT in BOTH modes (m3 and m4, 0 diff lines, 104/104). `tracer` remains blocked and untouched (its #GP is the cto's N-2 pad, CEO-471).

## What the oracle said that a `.std` could not

The baton's NEXT section carried the shape read off `transmit.std` alone, and flagged one item as "an OBSERVATION off one `.std`, not a measured semantic". Four purpose-built witnesses run under `/home/resources/icon-master/bin/{icont,iconx}` settled it. Two of the standing guesses were wrong:

1. ⛔ **The value renderer is `outimage`, NOT `image`.** A transmitted list prints `list_1 = [1,2,3]`, where `image` returns `list_1(3)`. The baton said to reuse `try_call_builtin_by_name("image", ...)` as the existing printer does. That is correct for `&null`, strings and integers — which is everything `transmit` transmits — and WRONG for structures. **This cure uses image and is therefore right on `transmit` and wrong on a structure**; the residual is named below rather than hidden.
2. ⛔ **There is a THIRD event shape the `.std` never showed: `returned … to`.** `transmit.std` contains only the transmit event and the `failed to` twin, so the baton described two. The oracle prints `main; co-expression_3 returned &null to co-expression_2` when a co-expression's procedure RETURNS rather than fails. It is the same emit site and is implemented here.
3. ✅ **The `main;` quirk is REAL and is not "the activator's procedure".** The baton observed lines 100/102 of `transmit.std` saying `main;` where the running procedure was `reader`/`word`, and refused to encode it unverified. Measured: on BOTH twins the procedure name is `main` even when NEITHER party is main (`chain.icn`: co-expression_3 returned to co-expression_2, printed `main;`). Encoded as the literal `main`.
4. ✅ **Truncation is at 16 characters, then `...`, inside the quotes.** A 16-char string prints whole; 17 chars prints `"0123456789abcdef..."`. Integers are never truncated.

## The three rules that are NOT in the baton and are what actually cost the cycles

- **Bar depth for all three co-expression events is `&level`, not `&level - 1`.** Procedure entry/return lines print `&level - 1` bars (`trace_print_icon` already did). The co-expression events print one MORE. Reusing the existing prefix builder verbatim, as the baton advised, produces every line one bar short.
- **The event's procedure name is the CURRENTLY-EXECUTING procedure, not the co-expression's body procedure.** `nest.icn`: a co-expression running `outer` which calls `helper` which transmits prints `helper;`. This rules out storing the name on the co-expression, and it is why the name is now a compile-time constant passed by the template (`cx->pname` at lower → `g_emit.op_activate_proc` → `x86_load_ro` into r8) rather than any runtime state. **No new global variable was created** (RULES.md § NO NEW GLOBAL VARIABLES); `g_emit` fields are explicitly outside that rule per Lon 2026-09-02.
- **`g_line` is ONE global shared by every co-expression thread, so a resumed co-expression inherits whatever line another co-expression last executed.** This is what made 28 of the 68 transmit events print `:17` (word's suspension line) or `:23` (reader's line) instead of `:19`. Cured by saving/restoring `g_line` per co-expression across the switch (`ctx->cur_line`).
- **The `@` token's line was never recorded.** `TT_ACTIVATE` inherited the enclosing STATEMENT's line, so an `@` nested inside a scan/while body reported the statement head. The parser now stamps `p->cur.line` from the `@` token on both activate forms. ⭐ This is why adding a line hook at the activate site changed NOTHING on the first attempt — the hook fired correctly with the wrong number, which reads exactly like a hook that did not fire.

## Item 2 (the create-site line) came free and is also cured

The baton listed as a separate item that a procedure entered through `create` is attributed to the ACTIVATION site, not the CREATE site (`:11` vs `:10`). The `failed to`/`returned to` twins need the create-site line too — the oracle prints the create line on them — so `ctx->create_line` had to exist for THIS cause anyway. Replaying it at first entry cures item 2 in one line. That is the whole remaining 3-line diff, and `transmit` is byte-exact with it.

## Residuals, named not hidden

- **`@&source` now emits its event** (it did not until the root co-expression's lazily-zero serial stopped being read as "not a co-expression"), but **a transmitted STRUCTURE still renders through `image`, so `list_1 = [1,2,3]` prints as `list_1(3)`.** One line of `trunc.icn`; absent from `transmit`, `tracer`, and every Arizona `.std` graded here. It is a distinct cause (the trace value renderer needs `outimage`, not `image`) and is left for its own row rather than folded in silently.
- `tracer` is untouched and still red — blocked on the cto's N-2 pad per CEO-471, exactly as the baton directs.

## The four witnesses, inline, so they outlive the scratchpad

Deliberately NOT minted into `corpus/tests/icon/` — the Icon master pair has ONE writer (hq_V, CEO-452) and
oracle probes are hq_V's lane. They are recorded here instead, which is versioned and collides with nobody.
Run each as: `icont -s -o W W.icn && diff <(iconx ./W) <(scrip W.icn </dev/null 2>&1)`, with the binaries at
`/home/resources/icon-master/bin/{icont,iconx}` (⛔ not on PATH — `command -v` answers a narrower question).
All four are byte-exact against icont on SCRIP `ff5ab8dde` EXCEPT `trunc`'s single structure line.

**`nest.icn` — which procedure name does the event carry?** (Answer: the currently-executing one, `helper`.)
```icon
global sink
procedure main()
   &trace := -1;
   sink := create rcv();
   outer();
end
procedure outer()
   helper();
end
procedure helper()
   "deep" @ sink;
end
procedure rcv()
   while @&source;
end
```

**`chain.icn` — the `returned to` twin, with NEITHER party being main.** (Answer: it still prints `main;`.)
```icon
global b, c
procedure main()
   &trace := -1;
   b := create mid();
   c := create deep();
   @b;
   write("back in main");
end
procedure mid()
   @c;
   @&main;
end
procedure deep()
   return;
end
```

**`trunc.icn` — the truncation boundary AND the one open residual.** 16 chars print whole, 17 truncate to
16 + `...`; integers never truncate; and the list line is the `outimage`-vs-`image` residual.
```icon
procedure main()
   &trace := -1;
   c := create rcv();
   "0123456789" @ c;
   "0123456789abcde" @ c;
   "0123456789abcdef" @ c;
   "0123456789abcdefg" @ c;
   "0123456789abcdefghij" @ c;
   12345678901234567890 @ c;
   [1,2,3] @ c;
end
procedure rcv()
   while @&source;
end
```

**`failed.icn` — the `failed to` twin and its create-site line number.**
```icon
procedure main()
   &trace := -1;
   c := create producer();
   d := create consumer();
   @c;
   @c;
   @c;
   @d;
end
procedure producer()
   @&source;
   @&source;
end
procedure consumer()
   x := @&source;
end
```
