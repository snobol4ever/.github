# FINDING 2026-07-25 — RK: out-of-range read, `@a[*]` whole-list slice, default parameter values

Session goal GOAL-RAKU-BB, RAKU-100 coverage arc. **Three rungs landed.** Starting watermark m3 633/0,
m4 633/0 (verified LIVE, matched the prior cursor's claim and `git log` HEAD `d8c575d1`). Final
**m3 655/0, m4 655/0** (+22 smokes, every one `[m3 PASS] [m4 PASS]`). Peers unchanged throughout:
Icon 14/14, SNOBOL4 7/7, Prolog 5/5/5, Rebus 4/4. Lang-blind gate GREEN. All builds `-O0` per O0-DEV.

**Toolchain provenance established BEFORE the first edit:** bison 3.8.2 + flex 2.6.4 reproduced the
committed `raku.tab.c`, `raku.tab.h` AND `raku.lex.c` byte-for-byte from HEAD's sources.
⚠ **Method note for future sessions:** regenerating to a *different output filename* (e.g. `-o /tmp/x.tab.c`)
makes `cmp` report DIFFERS spuriously — bison embeds the output path in `#line` directives and the header
guard. Regenerate into a scratch dir using the SAME basenames, or the provenance check lies to you.

---

## RUNG 1 — out-of-range subscript read yields undef, not a silent unwind (`3e80613a`, +7)

**Defect (as inherited, reproduced exactly):** `say @a[3]` on a 3-element array killed the remainder of the
statement sequence — `"after"` never printed, exit code 0. A silent unwind, the worst failure shape.

**Canonical semantics, read from source, not assumed:**
- `Array.rakumod:503-532` `AT-POS` → `!AT_POS_SLOW` → for a non-negative index past the end,
  `!AT_POS_CONTAINER($pos)` (`Array.rakumod:559-568`) returns a fresh `Scalar` whose value is the
  descriptor default, or **`Any`** when there is no descriptor. **Not a Failure, not an exception** —
  execution continues.
- `Array.rakumod:776-780` `!INDEX_OOR` — a **negative** index yields an `X::OutOfRange` **Failure**.

**Root cause:** `arr_get` returns `FAILDESCR` for out-of-range, which rides the four-port ω spine outward
and unwinds the enclosing sequence.

**⚠ THE FIND THAT MADE THIS A ONE-LINE RUNG — `arr_get` IS SHARED WITH PASCAL.** Callers are
`lower_raku.c:417` **and `lower_pascal.c:508`**. Editing the runtime helper would have silently changed
Pascal's array semantics. RULES' sanctioned pattern ("when two or more lowerers share a common helper whose
behavior must differ … each lowerer calls the variant it needs; the shared helper NEVER branches on a
language token") gives the correct fix: **the Raku lowerer routes to the NULVCL variant already in tree.**

```
-    case TT_ARR_GET: return lower_rcall(cx, t, "arr_get", 0, γ, ω, res);
+    case TT_ARR_GET: return lower_rcall(cx, t, "__rk_arr_at", 0, γ, ω, res);
```

`__rk_arr_at` (minted s2026-07-22c for destructuring surplus targets) is byte-for-byte `arr_get` except
`FAILDESCR` → `NULVCL`. **Total diff: 1 file, 1 line. Zero runtime, zero emitter, zero template, zero
grammar files.** Pascal keeps `arr_get` verbatim — proven by `git diff --stat`, not asserted.

**DIVERGENCE, RECORDED HONESTLY:** SCRIP prints an *empty line* for `say @a[3]`; canonical Raku prints
`(Any)`. `NULVCL` is one sentinel doing duty for Nil AND Any, and `say Nil` / `say Any` render differently
in Raku (`Nil` vs `(Any)`), so one sentinel cannot render both correctly. That is a representation rung,
not this one. **Negative indices** also give undef here rather than an `X::OutOfRange` Failure — a second,
smaller divergence, left deliberately: `@a[*-1]` is the supported spelling and already works.

---

## RUNG 2 — `@a[*]` whole-list slice (`7a317ccc`, +7)

**Blocked by the lexer, exactly as the prior cursor predicted:** `raku.l` owns `"[*]"` as the `OP_REDUCE`
metaop, so flex longest-match consumed the `[*]` of `@a[*]` and the slice was unreachable from the grammar.

**Canonical:** `array_slice.rakumod:252-262` — `postcircumfix:<[ ]>(\SELF, Whatever:D, *%_)`, no adverbs →
fast path: push all elements into an `IterationBuffer`, return `$buffer.List`. I.e. the whole list, in
order — exactly `__rk_arr_slice(arr, 0, elems-1)`, which is already in tree and already returns empty when
`hi < lo` (so the empty-array case falls out free).

**Fix:** one lexer rule matching `@name[*]` as a single `ARR_ALL_SLICE` token, defeating longest-match at
its own game; one `atom` production; one helper `rk_arr_all` reusing the existing `rk_dec` and the proven
`.elems` `TT_METHCALL` idiom (NO-DUP-LOGIC). Zero runtime code, zero new IR opcodes, zero templates.

**`@a[*-N]` is unaffected** — the `[*]` pattern needs a literal `]`, so `[*-1]` never matched it.

### Conflict delta: +1 s/r (92 → 93), r/r flat at 9 — CHARACTERIZED
Evidence, in descending strength:
1. **No new conflicting STATE.** States-with-conflicts count is **39 before and 39 after**. Exactly one
   existing state moved 30 → 31 s/r. (Stronger than the s2026-07-25 rung-3 precedent, which added a state.)
2. **The state is identified and it is the known family.** State 167 is `stmt_list: %empty .` — the
   block-trailing-expression family. Its reduce-lookahead set enumerates every token that can begin a
   statement; `ARR_ALL_SLICE` now appears in it, right after `OP_REDUCE`. The conflict is
   reduce-empty-`stmt_list` vs shift into the `'{' stmt_list expr '}'` forms — the *same* conflict that
   all 30+ sibling term-starting tokens already have, resolved identically by the default shift.
3. **Behavioural.** `[*] @n` → 24, `[+] @n` → 10, `[min]` → 1, `[max]` → 4, `[~]` → `ab`, `[*] (1,2,3,4)`
   → 24 all still correct; `@a[*].join/.elems/.sum`, empty array, single-element array all correct.
   Two dedicated regression smokes lock the metaop.

**PRE-EXISTING, PROVEN NOT-MINE BY STASH-COMPARISON BUILD:** `say ([*] 1,2,3,4)` → `1234` and
`my $p = [*] 1,2,3,4;` → parse error. I stashed the rung, rebuilt pristine HEAD, and got **byte-identical**
results. This is the documented s2026-07-23b bare-comma-list limitation (the reduce operand is a
`unary_expr`); the idiomatic `[*] @n` and `[*] (1,2,3,4)` forms are correct.

---

## RUNG 3 — default parameter values in sub/method signatures (`d7ba5409`, +8)

`sub f($x = 5)` was a hard parse error — no signature production accepted a default at all.

**Desugar, validated by hand BEFORE any grammar edit:** `$x = DEFAULT unless $x.defined` as a body
prologue. Verified `f()`→5, `f(9)`→9, and critically **`f(0)`→0** — a supplied falsy value must NOT trigger
the default, and `.defined` gets that right where a truthiness test would not. `defined($x)` as a *function*
does not exist in SCRIP Raku ("Undefined function or operation"); the `.defined` **method** does.

**Implementation:** `param_list` gains two productions (`VAR_SCALAR '=' expr`, first and after-comma). The
defaulted param is carried as a `TT_ASSIGN` **marker node** — never reaching the final AST. Helper
`rk_defaults_prologue(params, body)` unwraps each marker back to a plain param and returns a NEW `TT_SEQ`
whose head is the conditional-bind statements. Applied at all **8** param-taking sub/method sites.

**⚠ THE GOTCHA THAT WILL BITE ANY RE-IMPLEMENTATION:** in every one of those 8 actions,
`exprlist_free(params)` runs **before** `tree_t *body = $N;`. The prologue call must therefore be **hoisted
above** the param-copy loop (bind `rkbody` early, use it later) — calling it at the natural-looking place,
next to the body binding, reads freed memory.

**Defaults may reference earlier parameters** — `sub h($a, $b = $a * 2); h(3)` → 9 — and this falls out for
free, because the prologue statements run in signature order after the real binds. Methods work
(`method m($v = 42)`). **Conflict delta: ZERO (93/9 unchanged).**

### DROPPED ON PURPOSE — typed defaults (`sub t(Int $n = 7)`)
Written, built, measured, then **removed**. `t()` dies with *"Type check failed in binding to parameter
'$n'; expected Int"*: the type check fires at **bind** time, before any body prologue can run, so this
desugar structurally cannot express it. The available workaround — emit the param untyped and let the
prologue fill it — **silently discards a type constraint the programmer wrote**, which is worse than not
supporting the form. Untyped defaults (the common case) landed; typed defaults need the default moved into
the binder itself, which is its own rung. Typed params WITHOUT defaults are unaffected and smoke-locked.

**Also deferred:** named parameters (`sub f(:$n)`) and slurpies (`sub f(*@r)`) — both still parse errors.

---

## MEASURED GAP INVENTORY (empirical probe on this session's HEAD — not inherited prose)

**Confirmed working:** chained relops, ternary `?? !!`, `x` repeat, `.join/.sort/.unique/.chars/.uc/.lc/
.index/.split`, hash literals + `.keys`, `if/elsif/else`, typed params, implicit return, nested arrays.

**Gaps, ranked by my read of value/cost:**

1. **⭐ `/` TRUNCATES TO INTEGER — WRONG ARITHMETIC, not a display bug.** `7/2` → `3`, and
   `(7/2) * 2` → **6**, proving the truncation is internal. Canonical `Rat.rakumod:256`:
   `infix:</>(Int:D, Int:D)` → `DIVIDE_NUMBERS` → a **Rational**, so `7/2` is `3.5`. `1/3` → `0`, `22/7` → `3`.
   `div` (`7 div 2` → 3) and `%` are correct and must stay. **Highest-value open rung.** Note `TT_DIV` maps
   through the SHARED `lc_binop_code` (code 3) used by SNOBOL4/Icon/Pascal, where integer division is
   CORRECT — so this is the rung-1 pattern again: route Raku's `/` to a Raku-specific operation, never edit
   the shared arm. **Coupled to (2)** — reals must print correctly before `/` can return them.
2. **Whole floats print with a trailing `.0`.** `say 4.0` / `say sqrt(16)` → `4.0`; canonical prints `4`.
   ⚠ The inherited note that this renders as `4.` via `real_str` is **STALE** — Raku's `say` does not reach
   `real_str`; it goes through `to_cstring` → `rtos` (`by_name_dispatch.c:331`, `gcvt(r,14,buf)`). The
   peer-shared SPITBOL `real_str` (`string_ops.c:87`, which really does emit `0.`/`4.`) is a DIFFERENT path.
   This matters: the Raku fix may be containable inside `rtos` without touching the SPITBOL formatter at
   all — cheaper than the "needs a language-routed write path" prior sessions assumed. **Verify before trusting.**
3. **`.push`/`.pop`/`.shift`/`.unshift` produce SILENT EMPTY OUTPUT** — not a parse error, not a decline:
   `my @a=(1,2); @a.push(3); say @a.join(",")` prints nothing at all. A silent-failure class. The known
   two-representation entanglement (SOH-string vs `DT_DATA`) + lvalue writeback.
4. Named params `sub f(:$n)` and slurpies `sub f(*@r)` — parse errors; natural follow-on to rung 3.
5. `given`/`when` and `.map`/`.grep` with block args — `[SMX]` native decline (the map/grep BB family).
6. Single-element trailing comma — still costs +2 uncharacterized s/r; still buys nothing.

---

## Gate/audit state at handoff

- Raku **655/0 m3, 655/0 m4**; Icon 14/14; SNOBOL4 7/7; Prolog 5/5/5; Rebus 4/4.
- Lang-blind gate GREEN. Conflicts **93 s/r / 9 r/r** (+1 total for the session, characterized above).
- Generated artifacts reproduce byte-for-byte from the committed `raku.y`/`raku.l` (re-verified post-edit).
- No `.s` regen: **zero** Raku `.s` artifacts exist beside the 233 `.raku` sources; no SNOBOL4/Icon codegen touched.
- Session diff touches only `src/lower/lower_raku.c`, `src/parser/raku/raku.{y,l,tab.c,tab.h,lex.c}`,
  `scripts/test_smoke_raku.sh`. **Zero emitter, zero template, zero runtime `.c`.** No `libscrip_rt` rebuild
  was required this session (no runtime source changed).
- Three SCRIP commits: `3e80613a`, `7a317ccc`, `d7ba5409`.
