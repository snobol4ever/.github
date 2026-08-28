# FINDING 2026-08-28 (seat01) — polyglot-demo-empty-output-rc0: the row's own localization is stale; one file is now fixed, the other fails a different way with a sharper new cause

## Context
Row MINTED BY hq_C 2026-08-28 (same day), measuring both `demo02/wordcount.scrip` and `demo04/palindrome.scrip` as "8/8 runs: empty stdout, rc=0" and localizing the defect to the polyglot dispatch path (not any language section). Picked up FREE. **The tree moved underneath this row between hq_C's measurement and this session**: commit `d585afff` ("prolog: implement string_chars/2, string_codes/2, pairs_keys_values/3, group_pairs_by_key/2") landed and reached this checkout via a `git pull --rebase` done for unrelated work earlier in this session — but the local `scrip` binary was not rebuilt from it until partway through this investigation. The first measurements taken this session (against the stale binary) reproduced hq_C's numbers exactly; a rebuild changed the picture completely. **Lesson for whoever reads a "N/N runs" claim on this row next: re-measure against a binary built from current HEAD before trusting it, this row is proof the ground moves under it.**

## demo04/palindrome.scrip: FIXED, byte-exact
```
$ diff <(scrip demo04/palindrome.scrip) demo04/palindrome.expected
(no output -- exact match: "yes\nno\nyes")
```
10/10 confirmed on the rebuilt binary. This half of DONE-WHEN is satisfied. Not investigated further which specific missing builtin was the cause (plausibly `string_chars`/`string_codes` or one of the other three `d585afff` added — did not isolate, since the fix already landed elsewhere and isolating the exact mechanism has no remaining value).

## demo02/wordcount.scrip: STILL FAILS, but the FAILURE MODE CHANGED
Before rebuild (stale binary, matching hq_C's measurement): rc=0, empty stdout, empty stderr.
After rebuild (current HEAD): **rc=134 (SIGABRT), stderr: `rt_pl_cterm: island exhausted (16777216 used)`.**

This is not the signature this row was minted to chase. The polyglot dispatch path is not obviously broken any more either — the process now runs long enough to exhaust a 16MB term arena, which requires the Prolog section to have actually been entered and executed a substantial amount of work, not silently skipped.

### Narrowed to phrase/3 + DCG, not string_chars, not dispatch
Isolated the Prolog section to a standalone `.pl` file (same method hq_C used for the SNOBOL4 section). Bisected line by line:
- `string_chars("hi there", Chars), write(Chars)` → **prints `[h,i, ,t,h,e,r,e]` correctly.** string_chars is confirmed working, including on this exact demo's input shape.
- Adding `phrase(words(Ws), Chars, [])` on that SAME 8-element list (the DCG grammar from the demo: `whites`/`word`/`words`, all right-recursive, unremarkable) → **immediately reproduces the exact same `island exhausted` abort.**

An 8-character input exhausting a 16MB term arena on a plain right-recursive DCG is not a "needs more memory" situation — it is almost certainly unbounded/pathological backtracking (an infinite or combinatorially-exploding choice-point trail), reproducible on the smallest possible non-trivial witness. Minimal repro kept at hand for whoever picks this up (not committed anywhere, trivial to reconstruct):
```prolog
:- initialization(main, main).
whites --> [].
whites --> [C], { char_type(C, space) }, whites.
word([C|Cs]) --> [C], { char_type(C, alpha) }, word(Cs).
word([])     --> [].
words([])     --> whites.
words([W|Ws]) --> whites, word(W), { W \= [] }, words(Ws).
main :- string_chars("hi there", Chars), phrase(words(Ws), Chars, []), write(Ws), nl.
```

### Where I looked, and where I stopped
- `src/frontend/prolog/prolog_parse.c`'s DCG translator (`dcg_expand_body`/`dcg_expand_clause`, ~lines 854-960): read in full. Handles `{}`, `[]`, list terminals, `,`, `;`, `!`, `true`, and the non-terminal fallback (`dcg_call_nt`, appending S0/S as two trailing args) in what reads as textbook-correct DCG translation on a static read. **Not ruled out by measurement, only by reading** — do not treat this as cleared, only as the lower-priority half of the search space.
- `phrase/3`'s own compiled call path: `src/lower/lower_prolog.c:607-620`. Compiles to `IR_CALL_PROC_STAGED` with the non-terminal's name + base arity + 2 threaded args. **Not yet traced for correctness** — this is the more likely site given `phrase` gets special-cased compilation rather than going through the generic det-builtin dispatch every other predicate in this investigation used.
- The underlying choice-point/backtracking runtime (wherever Prolog clause resolution retries alternatives) was not examined at all. If the DCG translation and `phrase/3` compilation are both sound, the defect is here.
- `rt_pl_cterm`'s allocator itself (the "island" being exhausted) was not examined — is 16MB a hardcoded ceiling that could legitimately be raised as a workaround, or is it already generous and the real defect is consumption? Not measured; do not raise the ceiling as a fix without first confirming this is genuinely runaway consumption and not a reasonable request under a too-small cap.

## Not done
- The task's own instruction to check the other 8 demos for the same signature — **not done this session.** Given the underlying tree has moved (string_chars landing may have silently fixed or newly broken others), a fresh sweep is needed, not a reuse of any prior sweep.
- No source code changed. All investigation was read + build + run; the one temporary debug instrumentation added (two `fprintf` calls in `by_name_dispatch.c`, gated behind `getenv("SEAT01_DBG")`) was fully reverted (`git checkout --`) before this FINDING was written — tree is byte-identical to origin/main.
- DONE-WHEN is not satisfied (still requires both files matching). One of two files now passes; the row is not closeable.
