# FINDING 2026-09-22 hq_raku — Raku `return` inside a nested block fell through instead of exiting the sub

**Symptom, measured:** a plain 3-deep recursive function stack-overflowed:

```raku
sub A($k) {
  if $k <= 0 { return 0; }
  return A($k - 1) + 1;
}
say A(3);
```

Tracing with an added `say "enter k=", $k;` at function entry showed `k` walking 3, 2, 1, 0, -1, -2, -3, ...
without stopping — the base case's `return 0;` never exited the function. Minimal repro:

```raku
sub A($k) {
  if $k <= 0 { return 0; }
  say "after if, k=", $k;
  return 1;
}
say A(-5);
```
prints `after if, k=-5` then `1` — the `return 0;` inside the `if` is a no-op; control falls through to
the code that textually follows the `if`.

**Root cause, found via `--dump-ir`:** `src/lower/lower_raku.c`'s block lowering (`lower_rblock`, and the
equivalent reverse-loop in `lower_raku_proc` for the top-level proc body) threads each statement's γ
(success-continuation) port to whatever box was built for the *next statement in its own block* — correct
for ordinary statements, since that is literally structured fallthrough. `TT_RETURN`'s lowering (line ~675)
reused that same passed-in γ for the `IR_RETURN` box it built, with no special case. `bb_return.cpp` ends by
emitting `x86_gamma()` — an unconditional jump to whatever the box's γ was wired to — so whenever a `return`
was not literally the last statement in the function's own top-level body, its γ pointed at "next statement
in the enclosing block" instead of the function's real exit, and the emitted code jumped straight over the
epilogue into leftover sibling code.

Confirmed with `--dump-ir` on the minimal repro: the first `RETURN` box read `γ=<next-statement-box>`
while the second (syntactically-last) `RETURN` correctly read `γ=<SUCCEED>` (the proc's own exit) — same
box kind, different γ, because only the second one happened to be lowered against the proc's own top-level
threaded exit.

**Fix (SCRIP, this commit):** `rcx_t` gains a `proc_exit` field, set once per proc lowering (same idiom as
the existing `loop_exit`/`loop_next` pair used for `break`/`next`). `TT_RETURN` now always wires its
`IR_RETURN` box's γ to `cx->proc_exit`, bypassing whatever γ the enclosing block threading passed in.

**Verified:** four hand-written witnesses (bare early-return, early-return feeding a further recursive
call, a traced version, and the original stack-overflow repro) all correct in both m3 and m4 after the fix.
`test_smoke_raku.sh` 10/10 both modes unchanged. `test_raku_ladder.sh --to 20` 218/218 unchanged. RakM
master suite: 865/929 -> 866/929 both modes (`scrip_test_rk_subs` flips PASS; it was the one master-suite
entry whose early-return sat inside a *further-mismatched* fallthrough rather than a merely-redundant one,
which is why only one entry in this particular suite moved even though the defect is general).

**General form, worth keeping:** a control-transfer statement (`return`, and by the same reasoning any
future `last`/`next`-style construct) must never inherit the γ an enclosing block thread hands it "for
free" — that γ encodes *sequencing*, and a statement whose entire job is to skip the rest of the sequence
must be wired to its real target explicitly, or it silently degrades into an ordinary statement whose only
effect is the side effect of the boxes it runs, with none of its control-transfer semantics.

**Not fixed here, named rather than folded in:** the man-or-boy-test class of failure (`variable 'B'/'k' is
read but never assigned and is not a parameter`, mode-3 native emitter rejection) is a separate, still-open
defect — a closure that reads an enclosing sub's parameter or a self-referential `:=` binding. Minimal
repro:
```raku
sub A($k) {
  my $B := { $k };
  say $B();
}
A(5);
```
Also separate and unresolved: the `benchmark_rc-*`/`point_class_add2` cluster in RakM all share the
"empty stdout, rc=1" fingerprint (md5 `d41d8cd9`) — that fingerprint is just "zero bytes on stdout" and is
NOT evidence of one shared cause; each needs its own root-cause pass.
