# FINDING — s192 seat5 (`/home/claude5`, Claude Opus 5) — queue row `opsyn-3arg-ruling`, rank 2

## ⭐⭐⭐ THE RULING IS (a) — AND THE ROW'S OWN FRAMING WAS WRONG TWICE: THE THIRD ARGUMENT IS NOT AN ARITY, AND SCRIP WAS NOT BEING *PERMISSIVE* ABOUT IT. IT WAS DISCARDING IT.

**DISPOSITION: (a) SCRIP REFUSES, AND `f14_opsyn.sno` IS THE WRONG-DIALECT PROGRAM.** Manual citation, corpus measurement, blast radius and the counter-argument are all below. Option (b) — keep the permissive form as a documented extension — is refused on three grounds: RULES.md declares SCRIP follows SPITBOL semantics; the manual names this restriction *deliberate*; and, decisively, **SCRIP's own optimizer already depends on the rule the runtime was not enforcing** (§4).

---

## 1. THE CONTRACT, AND WHY THE BRIEF'S NAME FOR IT MATTERS

The brief calls the third argument an **arity** — `OPSYN(new, old, arity)`. It is not an arity. It is a **KIND SELECTOR**, and every wrong prediction in this row follows from the other reading.

> **v3.7 p.116 (tutorial):** *"The third argument is 0, 1, or 2. If it is omitted, SPITBOL assumes that the third argument is 0. A third argument of 0 means that the first argument is a function name, not an operator. If the third argument is 1, then the first argument must be one of the unused unary operators (!, %, /, #, =, |). When the third argument is 2, the first argument must be one of the unused binary operators (& @ # % ~)"*
>
> **v3.7 p.116, the sentence that settles the ruling:** *"The normal SPITBOL operators cannot be redefined: `OPSYN('+', 'PLUS', 2)` → Error #156. **This is one of the few places where SPITBOL is more restrictive than other SNOBOL4 dialects. However, by not allowing basic system functions and operators to be redefined, SPITBOL is able to optimize the code it generates.**"*
>
> **v3.7 p.234–235 (reference):** *"If i is omitted or 0, the first argument must be a function name; it cannot be an operator … In contrast with SNOBOL4, the second argument must always be an already defined function name. SPITBOL also differs from SNOBOL4 by not allowing built-in functions or operators to be redefined."*

The engine spells the same thing (`v37.min` `s$ops`, 16804–16866: `err 152` at :16805, `erb 156` at :16861): `gtsmi` loads arg 3 · `bnz wb,sops2` takes the OPERATOR path on non-zero · `bne wa,=num01,sops5` refuses a name that is not **one character** · the survivor is looked up in a table holding only the **undefined** operators · `erb 156` otherwise.

## 2. THREE FACTS MEASURED ON THE LIVE ORACLE, EACH CONTRADICTING THE OBVIOUS READING

Prose is not the contract; `x64/bin/sbl -bf` is. All three came out of sweeps, not out of the manual.

| what | measured | why it is not what you would have written |
|---|---|---|
| the two sets | 19-character sweep of `OPSYN(c,'SIZE',1)` / `OPSYN(c,'DIFFER',2)` ⇒ unary `! # % / = \|` (6), binary `# % & @ ~` (5) | exactly the manual's lists — and `1 + 5 == 6` **is** the SIL's `add =opbun,wb / beq wb,=opuun,sops3` arithmetic, so sweep and engine confirm each other |
| the legal values of `i` | `i=3` and `i=99` are **accepted, as BINARY opsyns** | the manual says "0, 1, or 2". That same arithmetic sends **1** to the unary table and **everything else non-zero** to the binary one. A `kind == 2` test would have been **stricter than SPITBOL** |
| the 153 cutoff | bisected: **16777216 (2²⁴) accepted, 16777217 refused**; negatives refused | it is not `INT_MAX` — `2147483647` is already ERROR 153. It is `gtsmi`'s small-integer range |

Coercion follows every other numeric argument: `'2'`, `'  2  '`, `2.0`, `2.7` all reach the binary path; `-0.5` truncates to 0; null is 0; a non-numeric string is **ERROR 152**.

⭐ **AND THE 2²⁴ BOUND IS NOT AN OPSYN FACT.** `keywords.c`'s KW-7 range test bisected the **same** 16777216 ceiling for ERROR **210** on keyword assignment, independently and one rung earlier. Two arguments, two error codes, one SPITBOL small-integer range. Corroboration, not a second authority.

## 3. WHAT SCRIP ACTUALLY DID — NOT PERMISSIVENESS, BLINDNESS

`src/runtime/pattern_match.c:447` opened `(void)type;`. The third argument was **read and thrown away**, so every form was a function alias. That is a stronger and worse statement than the brief's "SCRIP is more permissive", and it shows up as **silent wrong answers**, not as extra capability:

| program | SPITBOL | CSNOBOL4 | SCRIP (both modes, before) |
|---|---|---|---|
| `OPSYN('STRLEN','SIZE',1)` ⇒ `STRLEN('hello')` | ERROR 156 | `5` | `5` |
| `OPSYN('SUM','+',2)` ⇒ `SUM(3,4)` | ERROR 156 | `7` | **nothing printed** |
| `OPSYN('+','ADD',2)` ⇒ `3 + 4` | ERROR 156 | Error 21, stack overflow at level 266 | **`7`, rebind silently dropped** |
| `OPSYN('!','SIZE',3)` | ERROR 156 | Error 10 | accepted |
| `OPSYN('!','SIZE','x')` | ERROR 152 | Error 1 | accepted |

Rows 2 and 3 match **neither** oracle. SCRIP was not implementing the csnobol4 dialect; it was implementing nothing.

## 4. ⭐⭐⭐ WHY THIS IS A CORRECTNESS FIX AND NOT CONFORMANCE PEDANTRY

`src/optimizer/proc_collect.c:55` (`scc_taint_graph`) already treats **a literal third argument of 1 or 2 as proof** that an OPSYN is an operator rebind, and leaves SCC on for the whole program on that basis. With no check in the runtime, `OPSYN('SUM','+',2)` rebound a **function name** straight through that exemption. The invariant the optimizer assumed was never enforced anywhere.

That is the manual's own reason, arrived at from the other end: *"by not allowing basic system functions and operators to be redefined, SPITBOL is able to optimize the code it generates."* **SCRIP has the identical stake.** Enforcing at the one authority is the cure; widening the taint would have been the other one, and it would have cost the optimization on every legal program.

## 5. THE CORPUS MEASUREMENT THE BRIEF DEMANDED

Census of every `OPSYN(` call site in `corpus/` outside `programs/lon/` and `programs/include/`: **70 sites parsed** — 17 function-form (`i` absent/0), 46 legal operator-form (4 unary, 42 binary), and **7 that SPITBOL refuses, in 4 files**:

| file | sites | state **before** this rung |
|---|---|---|
| `programs/csnobol4-suite/alis.sno` | 4 (`SUM`,`PROD` fn-names with i=2; `+`,`*` used-ops) | **already red both engines** — parse-errors on `\` at line 57 in SCRIP *and* in SPITBOL (ERROR 230); `.ref` is CSNOBOL4-pinned, ungradeable against the oracle |
| `programs/gimpel/SYSTEM.sno` | 1 (`OLD_SHARP` fn-name, i=2) | **unreachable by the module's own design, and SCRIP agrees with the oracle about why.** `SYSTEM` gates on `IDENT(DATATYPE(.X),'STRING')`; measured — `sbl` answers **`NAME`** and takes `SYSTEM_2`, CSNOBOL4 answers **`STRING`** and does reach `SYSTEM_1`. **SCRIP answers `NAME`.** `SYSTEM_driver.sno` prints `SPITBOL` under `sbl`, and under SCRIP in **both** killswitch arms |
| `programs/snobol4/feat/f14_opsyn.sno` | 1 | the witness; **no `.ref`, ungraded** |
| `crosscheck/coverage/coverage_sno_nodes.sno` | 1 | dies before line 105 in **both** engines; no `.ref` |

**Not one is a currently-green graded row.** The strictness costs nothing, measured rather than assumed.

Two independent confirmations:
- **Killswitch A/B (`SCRIP_OPSYN_KIND=0`) over all 54 corpus programs mentioning OPSYN: 1 mover / 54 — and the mover is the probe written to demonstrate the change.**
- **`programs/include/` cleared without reading a line of it:** all **144** `programs/gimpel/*_driver.sno` run with `SNO_LIB=programs/gimpel:programs/include`, scanned for the presence of error **152/153/156** in their output — **0 of 144**. The question "does the include tree hide an illegal OPSYN" is answerable by *error-code presence*, which needs no content; a grep of those files would have published them.

## 6. ⛔ THE INSTRUMENT ALMOST PUBLISHED TWO FALSE MOVERS, AND THE CONTROL IS WHAT CAUGHT IT

The first gimpel A/B compared **one md5 per arm** and reported `ORVISUAL_driver` and `PERM_driver` as movers. **Neither arm is self-stable:** ORVISUAL returned **3 different md5s in 3 default runs**; PERM returned **3 distinct md5s in each arm**. The programs flap on their own, and a single-draw diff over a flapping program is not a mover — it is two draws from the same distribution.

⭐ **THE GENERALISABLE MOVE: before an A/B convicts, self-diff each arm.** Same family as seat1's s191 `nqueens` (two boards under identical load disagreed, so load was not the variable) and seat7's s190 mover count (one mechanism × 478 sites read as a 144-file blast radius). **An A/B is only as sharp as the stability of its arms, and stability is a measurement, not an assumption.** The replacement instrument does not care about flapping at all: it asks whether the *new error codes* appear, which is the question the change is actually about.

## 7. THE CURE

**`src/runtime/pattern_match.c` — `opsyn()`, the ONE authority** (`by_name_dispatch.c` `BID_OPSYN` and `core.c` `_OPSYN_` both funnel here, so there is no second spelling to keep in step — checked, because s191's row in this same seat was a spelled-twice defect):

- `is_numeric_like(type)` else **152** · range `0 … 16777216` else **153** · `kind != 0` ⇒ `nm` must be exactly one char in `!#%/=|` (kind 1) or `#%&@~` (kind ≥ 2) else **156**.
- `is_numeric_like` was `static` in `core.c` and is now exported through `core.h` — **the predicate is reused, not respelled.**
- Killswitch `SCRIP_OPSYN_KIND=0` restores the discard verbatim. Read with a bare `getenv` and no memoising `static`: `opsyn()` runs once per OPSYN statement, so the cache would have bought nothing and minted file-scope state the FACT RULE forbids.

⛔ **THE ERRORS RIDE `kwb_error`, NOT `core_runtime_error`, AND THE PROBE IS WHAT FORCED IT.** The first cut used `core_runtime_error` and **printed and exited** where the oracle merely fails the statement: that function's conversion arm needs a pushed `jmp_buf` (`g_error != 0 && g_core_errjmp_n > 0`) and **only the EVAL boundary pushes one**. `kwb_error` is KW-5's one adjudicator for *"&ERRLIMIT says convert or report"* — it decrements the credit, publishes `&ERRTYPE`/`&ERRTEXT`, and returns 0 for the caller to propagate FAIL, exactly as 208/209/210 do. At the **default `&ERRLIMIT` of 0 it calls `core_runtime_error` itself**, so the default arm is behaviourally unchanged and only a program that has *asked* to catch errors sees anything new.

⭐ **AND THAT IS WHAT MAKES THE CONTRACT PINNABLE AT ALL.** An unconverted OPSYN error prints a SPITBOL dump no `.ref` may honestly carry — `sbl` exits **0** while dying (the trap s190 filed and s191 `gimpel-suite-harness` filed again). Under `&ERRLIMIT` the oracle prints clean, diffable lines. **`&ERRLIMIT` is the general instrument for pinning any SPITBOL error class**, and this row is its second user.

## 8. THE TWO CORPUS FILES

**`programs/snobol4/feat/f14_opsyn.sno` — REWRITTEN** (the program was the wrong dialect, exactly as Lon's rank-0 `kw-uppercase-dialect` ruling says to treat this class: *normalize the program, do not relabel it*). It now exercises the three forms SPITBOL actually offers — 2-arg function synonym, `i=0` function synonym, `i=2` unused-binary operator synonym with both the success and the failure direction of `&`⇒`DIFFER`. `.ref` = `PASS`, **byte-identical to `sbl -bf`**, and CSNOBOL4 prints `PASS` too. **m3 ≡ m4 ≡ oracle.**

**`corpus/probe/opsyn/opsyn_kind_selector.sno` — NEW, and it pins the whole ruling in 13 diffable lines**, `&ERRLIMIT`-converted so every code is data instead of a dump: fn-name at i=1 and i=2 ⇒ 156 · a used operator at i=2 ⇒ 156 · a *binary* operator offered at i=1 ⇒ 156 · unused `&` at i=2, unused `!` at i=1 and unused `@` **at i=3** ⇒ accepted · non-integer ⇒ 152 · negative and 2²⁴+1 ⇒ 153 · 2²⁴, `'2'` and `2.7` ⇒ accepted. `.ref` taken **byte-identical from the live oracle**; **m3 ≡ m4 ≡ oracle, 13/13.** It lands in the scorecard's `probes_misc` suite **green**.

## 8b. ⭐⭐ TWO SEATS REACHED THIS FILE FROM OPPOSITE ENDS IN THE SAME SESSION, AND THE OTHER ONE'S TOOL CONVICTS THE OLD PROGRAM INDEPENDENTLY

seat1's s191 row `ref-the-ungraded-suites` landed `scripts/util_ref_mint.sh` plus a `scorecard_snobol4.sh oracle <suite> <program>` verb — *mint a `.ref` through the same door the board grades through* — and it minted **16** new pins into `programs/snobol4/feat/` (its own commit title: *"16 live-oracle .ref pins for feat/ — ground truth is checked in, and it changed NO verdict"*). **It did not mint one for `f14_opsyn`**, and its own status vocabulary says exactly why. Run through that door:

```
misc        f14_opsyn.sno  (this rung)   -> LIVE           0    5 bytes   ⇒ .ref byte-identical
probes_misc opsyn_kind_selector.sno      -> LIVE           0  329 bytes   ⇒ .ref byte-identical
misc        f14_opsyn.sno  (PRE-rung)    -> DEAD_REPORT    0  386 bytes   ⇒ REFUSED, unmintable
```

**`DEAD_REPORT` is that tool's name for "`sbl` exited 0 while printing a fatal error dump".** So the minter, arriving from the ungraded-suites side, refused this program as unpinnable; this row, arriving from the semantics side, says *why* the program was wrong and normalizes it — after which the same door mints it `LIVE`. **Neither seat needed the other, and the two answers are the same answer.** Both of this rung's `.ref` files were validated through that door rather than only by hand, which is the rule my own s191 wrote and seat1's tool header cites: *a census is a harness — copy `run_one`, never re-derive it.*

## 9. ⛔ WHAT THIS RUNG DOES NOT DO, NAMED RATHER THAN LEFT TO BE DISCOVERED

- **IT TEACHES THE REFUSAL HALF ONLY.** The *legal* unary form still does not **parse**: `OPSYN('!','SIZE',1)` then `!'x'` is `FATAL lower_snobol4 … binary operator with missing operand` — the standing checked-in reds `probe/opsyn/d_unary.sno` and `probe/opsyn/opsyn_unary_target.sno` (the manual's own p.116 example) — and binary `#` fails in the parser too (`probe/opsyn/opsyn_builtin_target.sno`). **NOT filed as a new queue row on purpose** — `GOAL-SNOBOL4-100` **R-8** already owns exactly this, with the cause named (`snobol4.y` hard-wires `T_2POUND→TT_MUL`, `T_2PERCENT→TT_DIV`, `T_1BANG→TT_POW`, …), and a fresh row would have been a second name for an open rung, which is the disease this row is about. R-8 is annotated in place instead. SCRIP now refuses what SPITBOL refuses while still refusing some of what SPITBOL accepts, and that asymmetry is stated, not hidden.
- **ERROR 155** (i=0 and the first argument is not a natural variable name) is **deliberately not implemented**: the oracle *accepts* `OPSYN('&','DIFFER',0)`, so "natural variable name" is wider than "identifier", there is no witness, and guessing at it could only reject programs that work.
- **`proc_collect.c` is untouched.** Its `ival == 1 || ival == 2` test now taints *conservatively* (an `i=3` binary opsyn taints and merely loses an optimization), and its assumption is, for the first time, an enforced invariant rather than a hope.

## 10. WATERMARK AND GATES

**Pristine at the PUSHED heads — SCRIP `3f0dc46a`, corpus `6f174239` — RT_OPT `-O0`, both trees clean.** Rebuilt and re-proven from pristine a THIRD time here, because the push rebased onto seat8's `prototype-spelled-twice` (`eef7fec9`), which edits `core.c`/`core.h` — the same two files this rung touches. Both witnesses re-verified m3 ≡ m4 ≡ oracle at these heads. Broad corpus board **m3 335/2 · m4 328/8 · SKIP 1 (337)**.

⛔ **THE +1/+1 IS NOT MINE, AND SAYING SO IS THE POINT.** Measured on this box in this session, this rung's own A/B is **0/0**: pre-patch and post-patch boards at SCRIP `d1994fe3` were **both** `m3 334/3 · m4 327/9 · SKIP 1`, fail-sets identical by name. The board then moved *after a `git pull --rebase`* pulled in seat3's s192 `rty-fail-inline-retry` (`ed61196c`) and seat6's `const-nest-flip` (`c512089a`) — and the row that went green is **`175_pat_bal_generator_retry`**, whose defect (*a generator never retries*) is seat3's brief verbatim. **A board run after a rebase measures the MERGED tree**, and attributing its whole delta to your own rung is how a watermark becomes a lie — the same trap this seat named at s191 and walked into from the other side here, because this time the delta was *flattering*.

⭐ **CORROBORATED FROM OUTSIDE THIS ROW, AND I DID NOT HAVE TO ASK:** seat3's own s192 cursor already records `m3 335/2 · m4 328/8 SKIP 1` at SCRIP `ed61196c` — *their* commit, measured before this patch existed. My post-rebase board reproduces their number to the digit, which is what a rung that moves nothing on this board looks like.

This rung's honest board contribution is **zero, by construction**: the only program it moves is the new probe, and the broad board does not run `probe/`. Its measured effect lives in the killswitch A/B (1 mover / 54) and in `probes_misc`. Gates: `emit_no_lang` · `template_medium_invisible` (0 / ceiling 0) · `icn_no_stack` · `icn_one_reg_frame` · `icn_semicolon_required` — all rc=0.

**`.s` REGEN — NOT APPLICABLE, AND THE REASON IS STRUCTURAL, NOT AN ASSUMPTION:** the three touched files are all runtime (`pattern_match.c`, `core.c`/`core.h`, `keywords.c`); nothing in `src/emitter/`, `src/templates/`, `x86_asm.h`, `src/lower/` or the optimizer moved, and `opsyn`'s symbol name and signature are unchanged, so no emitted byte can differ. Verified by regen anyway rather than asserted — **all five RULES step-4 scripts run, `changed=0` on every one** (`programs` emitted=623 changed=0 · `prolog_bench` emitted=22 changed=0 · `feature` 0 changed · `benchmark` and `demo` produced no commit), both trees clean at the pushed heads.

---

## 11. ⭐⭐⭐ THIS ROW WAS ALREADY OPEN IN THE GOAL FILE UNDER ANOTHER NAME, AND ITS DEFECT TABLE IS TWO-THIRDS STALE

`GOAL-SNOBOL4-100.md` **R-8** (opened by Lon in-chat s105) names this exact defect in its own words — *"Conversely SCRIP **silently accepts** the illegal `OPSYN('+','PLUS',2)` and prints `3` where the oracle raises 156 — permissive where it must be strict"* — and cites the same p.116 sentence about optimization. **That half of R-8 is closed by this rung.** The queue row and the goal rung were the same defect wearing two names; a seat taking `opsyn-3arg-ruling` without opening R-8 would have re-derived the manual citation from scratch, which is why this is recorded rather than merely fixed.

⛔ **AND R-8's MEASURED DEFECT TABLE IS NO LONGER TRUE.** Re-measured this session, pristine, both modes, against the same eight `probe/opsyn/` witnesses s105 minted:

| witness | s105 said | s192 measures |
|---|---|---|
| `opsyn_bin_amp` (`&`) | SIG11 | **PASS m3 · PASS m4** |
| `opsyn_bin_at` (`@`) | SIG11 | **PASS m3 · PASS m4** |
| `opsyn_bin_tilde` (`~`) | SIG11 | **PASS m3 · PASS m4** |
| `opsyn_rebind_twice` | SIG11 | **PASS m3 · FAIL m4** ⬅ half-cured, and now a MODE-PARITY break |
| `opsyn_bin_pound` (`#`) | prints `0` | FAIL m3 · FAIL m4 |
| `opsyn_bin_pct` (`%`) | prints `0` | FAIL m3 · FAIL m4 |
| `opsyn_builtin_target` (`#`→DIFFER) | rc=1 | FAIL m3 · **m4 does not compile** (parse error) |
| `opsyn_unary_target` (unary `!`→ANY) | rc=1 | FAIL m3 · **m4 does not compile** |

**Four of eight cured; three SIG11s gone.** The survivors are one class and it is the one R-8 already named: the grammar hard-wires the *unused* operators to arithmetic (`snobol4.y` `T_2POUND→TT_MUL`, `T_2PERCENT→TT_DIV`, `T_1BANG→TT_POW`, …), so `#` and `%` and the whole unary family carry a static identity SPITBOL says they must not have. `d_unary` (program-defined unary target) fails the same way.

⛔ **TWO m3 ≠ m4 SPLITS IN THIS FAMILY, AND ONE IS IN NO LEDGER AT ALL:** `opsyn_rebind_twice` (m3 PASS, m4 FAIL) and **`f_apply` (m3 PASS, m4 SIGSEGV)** — `f_apply` is not in R-8's table, not in the queue, and m3 ≡ m4 is a design invariant. Both are **pre-existing**, not this rung's doing: the `SCRIP_OPSYN_KIND=0` A/B moves neither. Routed, not opened.

## 12. ⭐ THE QUARANTINE THIS RUNG DISSOLVES — AND ITS PREMISE DID NOT REPRODUCE

`corpus/probe/opsyn/unstable-oracle/` held `opsyn_used_op_err156.sno.manual` — **the same assertion as this row**, parked at s105 because an ERROR-156 run of `sbl` ends in a banner (`execution time msec`, `memory used (bytes)`, `REGENERATIONS`, every line doubled) that no `.ref` can compare against. Its README posed R-8(c) as a two-way choice: **(a)** teach the grader to normalise the banner, or **(b)** leave it manual.

**`&ERRLIMIT` is option (c), and it needs no grader change**: the *program* asks the oracle to convert, and the error code arrives as ordinary output. That is what `opsyn_kind_selector.sno` does, and it is why thirteen error-class assertions are gradeable today instead of one being parked.

⛔ **AND THE QUARANTINE'S STATED REASON DOES NOT HOLD, WHICH SHARPENS THE LESSON RATHER THAN WEAKENING IT.** Five live draws of the parked witness returned **one md5, five times** — the program is small enough that `execution time msec` and `REGENERATIONS` are both 0 and `memory used` is fixed. Instability is *not* what makes that banner unpinnable. What does is that **`sbl` exits 0 while dying**, so a banner-shaped `.ref` pins a dump that looks like a successful run. The park was right; its reason was the weaker of the two available. README rewritten in place; the `.manual` pair kept, unswept, as the record of the oracle's exact wording. **Nothing deleted.**

⭐ **THE GENERALISABLE MOVE, AND IT OUTLIVES OPSYN: when the oracle's answer is an ERROR, do not try to pin the error report — make the witness catch the error and print its CODE.** `&ERRLIMIT` + `&ERRTYPE` converts any SPITBOL error class into stable, diffable, honest output, and SCRIP already implements the mechanism (KW-5). `test_stack` (R-3(f)) is the obvious next candidate; it is named, not claimed.
