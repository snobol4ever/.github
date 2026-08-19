# FINDING s147 (web seat, Claude Opus 5) — CN-3 LANDED; AND THE BLAST-RADIUS SWEEP FOUND A LIVE DANGLING `.rodata` STRING

SCRIP `9d85ca98` · corpus `9dd32aa4`. Rung: SN4-CONSTANTS **CN-3** (+ CN-3b record). Both committed.

---

## 1. CN-3 — what it is, in one sentence

**Declaration replaces inference for the half it can, and does not excuse the half it cannot.**

`sno_seal_pat()` must PROVE single-assignment, and so carries two gates a *declared*
constant does not need:

- `sno_fz_wrcount(nm) != 1` — a per-name textual write count.
- `g_sno_fz_unsafe` — a **WHOLE-PROGRAM poison**: one `EVAL`/`CODE`/`CLEAR`, or one
  indirect `$(...)` assignment *anywhere*, voids static staging for **every name in
  the program**.

CN-2 already put the guarantee at the cell (`NV_t.is_const`, error 341, enforced at
the cell and not the spelling, so `OPSYN`/indirect/`FIELD` aliasing cannot bypass it).
So for a `&Name` neither gate applies, and `sno_const_pat()` consults neither.
`sno_pat_dfree` — transitive defer-freedom, manual p.122, the half that is still a
genuine property of *this tree* — still runs. A constant whose value contains a
dynamic `*Y` correctly stays 0.

## 2. The actual defect CN-3 fixed

The pre-scan arm skipped **every** `&Name =` statement wholesale. A constant's
defining tree never entered `g_sno_seal`, so `*&Name` could resolve nothing — which
is precisely why CN-2's own comment at the defer site left `pat_static` at "the
conservative MVP". One arm, one `continue`.

**Classification needed no second copy of the keyword list** (ONE AUTHORITY): only a
tier-3 user constant can reach that arm with a *pattern* RHS, because every assignable
tier-2 keyword takes an integer or string and every tier-1 protected keyword refuses
assignment outright (**oracle error 209, measured this session**). `sno_is_pattern_rhs`
IS the classifier.

## 3. Measured

| item | result |
|---|---|
| `pat_static` on the `*&Name` node | **0 → 1** (EARN diag: 2 vs 1 nodes across arms) |
| witnesses `cn_arbno_static`, `cn_const_chain` | green **m3 AND m4**, m3 ≡ m4 |
| `.ref` provenance | **classic twins** through `x64/bin/sbl` — extension programs ORACLE_FAIL by construction (stock `sbl` rejects a tier-3 `&name` with **error 251**) |
| MD5 blast radius, all 1572 corpus+test `.sno` | **0 differing** under fixed ASLR |

**⛔ THE T2 PAYOFF IS NOT YET REALIZED — emitted asm is byte-identical.** Every current
`pat_static` consumer is default-OFF (`SCRIP_DEFER_HAZ_STATIC`), `PATV$`-gated, or
unreached by these shapes. And **s101's reason for distrusting `pat_static` as a hazard
exemption is about the defer's runtime spine record — declaration does NOT fix that**,
so it cannot simply be switched on. CN-3 lands the lowering half only.

## 4. ⛔ A LIVE DANGLING `.rodata` STRING — PRE-EXISTING, FOUND BY THE SWEEP, NOT CONSTANTS-RELATED

`corpus/programs/snobol4/parser/unary_not.sno` — the whole program is `x = ~BREAK(nl)`.

The sweep flagged it as the ONE file of 1572 differing across killswitch arms. It is
**not** a CN-3 effect. It is nondeterministic:

```
n5_assign_α:   lea   rdi, [rip + .S0]        <- the string is LIVE, it is referenced
.S0:           .string "\324:\002"           <- run 1
.S0:           .string "-\270\003"           <- run 2   same binary, same arm
.S0:           .string "'\205"               <- run 3
.S0:           .string ";\004"               <- stable ONLY under setarch -R
```

Five runs in a **fixed** arm give five different strings; `setarch -R` freezes it.
**The emitter is writing ASLR-dependent uninitialized memory into `.rodata`, and the
program loads its address.** Re-diffed under `setarch -R`, the two arms are
byte-identical — hence the 0/1572 above.

- The oracle **errors** here: `ERROR 069 -- break argument is not a string or expression`
  (`nl` is unset, so `BREAK(null)` is invalid). **SCRIP silently succeeds, rc=0, no output** —
  a separate oracle divergence in the same one-line file.
- Consequence for house process: this file's `.s` artifact is **nondeterministic**, so
  `util_regen_*_s_artifacts.sh` will commit churn for it on every run. This is consistent
  with the existing law that `.s` is honest current output and never a pinned golden, but
  it means **an `.s` diff is not by itself evidence of a codegen change** — the s147 sweep
  would have reported a false positive had the outlier not been chased.
- **Lesson, stated generally:** the blast-radius sweep must run under `setarch -R`, or a
  nondeterministic file will masquerade as a real emission delta.

This is in the **parser** corpus, which is beauty-adjacent. Not taken — B1/B2 are HQ-owned.

## 5. CN-3b and the honest inertness record

Both keyword arms added for the *constant-chain* case (`&Item = &Word | &Num`) are
**INERT today**. `sno_pat_supported()` has no `TT_KEYWORD` arm and returns 0; it gates
registration, so the chain is refused before either classifier is consulted. The chain
witness stamps 1 node in **both** arms — that is the number CN-3c must move to 2.

**The missing third arm is not a one-liner.** `sno_pat_supported` asserts *the lowerer
can emit this tree*. Admitting bare `&Word` in pattern position is a claim about the
pattern-valued keyword read path (the `IR_MATCH_VALUE`/dynamic class, not the static
one); asserting it without proving the emission would seal-note a tree the lowerer
cannot build — staging a graph for `*&Item` that has no emitter. Arms kept and
annotated at both sites so CN-3c does not re-derive the measurement.

## 6. Keyword initial values — manual v3.7 is STALE, the binary is law

Probed because KW-2 (s146) and manual ch.16 disagree:

```
&TRIM=1   &MAXLNGTH=16777216   &FULLSCAN=1   &CASE=1   &STLIMIT=2147483647   &ANCHOR=0   &ERRLIMIT=0
```

Manual p.191 says `&TRIM` is *initially zero* and p.190 says `&MAXLNGTH` defaults to
**4,194,304**. Both are wrong against the live `x64/bin/sbl`. **s146's Class B values
stand**; SCRIP FOLLOWS SPITBOL SEMANTICS means the binary, not the book.

## 7. `&ERRLIMIT` → statement failure: the mechanism CONFIRMED at the oracle

s146 routed this as "SCRIP does not have it at all". Measured what SCRIP must match:

```
&ERRLIMIT = 10 ; &ALPHABET = 'x'  :S(YES)F(NO)   ->  takes F, &ERRTYPE=208, &ERRTEXT set
&ERRLIMIT = 20 ; &STCOUNT = 5     :S(A)F(B)      ->  takes F, 209 "keyword in assignment is protected"
&CONSTANT = 1                                     ->  251 "keyword operand is not name of defined keyword"
```

Error **209** is the protected-write code; **208** fires FIRST on a non-integer value
(confirming s146's Class D ordering: value test before protected test); **251** is the
closed-namespace rejection that makes every `&`-extension program ORACLE_FAIL by
construction.

**This matters for SN4-CONSTANTS beyond KW-5:** the enforcement path for
"never assigned twice" — CN-2's error 341 — is the SAME machinery. Today 341 is a hard
`core_runtime_error`. To be oracle-shaped it must become interceptable the way 208/209
are: `&ERRLIMIT` non-zero converts it to statement failure with `&ERRTYPE`/`&ERRTEXT`
set, and a `SETEXIT` label takes precedence. **CN and KW-5 share one mechanism**; whoever
builds `&ERRLIMIT` should build it for both.

## 8. Next

- **CN-3c** — the `sno_pat_supported` `TT_KEYWORD` arm, gated on proving the bare-`&Name`
  pattern-position emission. Gate: `cn_const_chain` moves 1 → 2 stamped nodes.
- **CN-3 T2** — emitter-side consumer widening. ⛔ **Needs a ruling** (§9).
- **The `.S0` dangling read** — own rung; smallest repro already exists and is one line.

## 9. ⛔ FOR LON — one ruling gates the entire T2 payoff

The goal file's T2 is "defer-site **bypass**": for `*&P` on a declared constant, emit no
`IR_MATCH_DEFER` at all and inline the pattern graph. That collides head-on with CN-2's
**error 342, "read before one-time assignment"** — inlining a compile-time-known tree
would silently match even when the defining statement has not executed, and the design
of record says a silent null there "would defeat GUARANTEED".

**The question:** does a declared constant's defer-site bypass get to drop the 342 check,
or must it keep a guard? SNOBOL4's arbitrary `:(GOTO)` control flow makes
definition-dominates-use unprovable in general, so the realistic choices are (a) bypass
and accept that 342 becomes unreachable for bypassed sites, (b) keep one cheap
`NV_EXISTS` guard at entry and bypass everything after it, or (c) bypass only when the
definition is textually first AND the program contains no goto that can reach the use
without crossing it.

Not taken on this seat. It is a semantics call, not an implementation one.
