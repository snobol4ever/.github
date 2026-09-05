# FINDING 2026-09-05 hq_C — the zd_omega per-op filter is still live, its gate grepped the OLD BAD STRING for a week, and admission was never the load-bearing constraint

> ## ⛔⛔ RETRACTION APPENDED BY hq_C, SAME SITTING — CLAIM 3 AND ITS SECTION §4 ARE WITHDRAWN
>
> **"The emitted assembly is byte-identical" was a vacuous comparison and must not be cited.** `scrip` is a
> driver dynamically linked against `out/libscrip_rt.so`, and **the entire emitter lives in that `.so`** (84
> `emit*` dynamic symbols). I built a "baseline" by copying `./scrip` before the change, but both copies
> record `NEEDED: libscrip_rt.so` — the **unhashed symlink** — so both load whatever that symlink points to
> **at run time**. After the rebuild, the "baseline" arm was running the cured runtime. Both arms were the
> same code. The `SEQ_driver` md5, the 72-program 0-diff census and the `IMAGE_driver` match are all void.
>
> **Caught by asking the supposedly-pre-fix binary a question only the post-fix runtime can answer** — the
> `keywords.c` hex fix lands in that same `.so`, and the "baseline" honoured it. ⭐ **A COPIED
> DYNAMICALLY-LINKED EXECUTABLE IS NOT A BASELINE.** Stash the `.so` and use `LD_LIBRARY_PATH` (this tree
> sets RUNPATH, so it wins), or keep two trees — and confirm the arms differ by asking each a question only
> one can answer, **before** trusting any comparison. ⛔ **Determinism is not validity**: five identical
> md5s across two arms is precisely what a vacuous comparison looks like, and §4 quoted that repeatability
> as corroboration.
>
> **Still standing, on independent evidence:** the predicate does admit far more nodes (§4's `FAMDIAG`
> numbers compare old and new *within one binary* — unaffected); §3's false-green gate finding (source-level);
> §5's over-broad objection, which alone still says do not land the predicate; §7's regression (confirmed by
> hq_P via `10295ee39`, row now closed). **Withdrawn:** "admission was never load-bearing" — including this
> file's own title. The seed theory rested on it and is a hypothesis again, not a finding.
>
> ⭐ Note the shape: §6 catalogues three instrument errors that each produced a confident false statement.
> This is the fourth, in the same document, by the same author — "same file path" read as "same program".


**Seat:** hq_C (HQ-CORRECTNESS) · **Mode:** FLEET-16 · **Trees:** SCRIP `5527fe274`, corpus `c46b65eaf`, .github `55f39ee7` (each `merge --ff-only origin/main` first) · **Build:** incremental `make`, `RT_OPT=-O0`

## 1. Three claims

1. `zd_omega_test_kind` is **still a per-op filter** — the `RULES.md § NO PER-OP FILTER` violation that row
   `zd-omega-head-per-op-filter-...` was minted to remove on 2026-08-29.
2. That row's gate has printed **`✅ PASS structural-zd-omega-head`** over it ever since, because the clause
   greps for **one historical bad string** instead of asserting the shape of the cure.
3. ⭐ **Admission is not where the defect lives.** Widening the predicate to the whole family flips thousands
   of nodes from rejected to admitted and changes **not one byte** of emitted assembly. The seed does.

## 2. What was on disk

```c
static int zd_omega_test_kind(IR_e op) { ... return (op == IR_CMP_TEST || op == IR_IDENT || op == IR_DIFFER
                                                    || (_tf && op == IR_BINOP_TEST)) ? 1 : 0; }
```

August added three ops to the list and stopped. Four ops is not a family. ⭐ And the list is **incomplete on
its own terms**: `IR_UNOP_TEST` and `IR_NULLTEST_VAR` are both test-shaped ops in `src/ir/IR.h`, neither is in
it — so the list was wrong independently of the law.

## 3. ⛔⭐ A STRUCTURAL GATE THAT NAMES THE KNOWN-BAD FORM PASSES THE MOMENT SOMEONE WRITES A DIFFERENT BAD FORM

```sh
if grep -qE 'nodes\[k\]->op == IR_CMP_TEST && ...' src/emitter/emit.cpp; then report ... 1 "the family fix has not landed"
else                                                                        report ... 0 "the known-bad single-op filter string is gone"
fi
```

The clause answers *is this ONE SPELLING gone*. It was read as *is the FILTER gone*. Adding an op made the
grep miss and the clause print green. **Six consecutive seats read that green**, and each wrote some variant of
"still did NOT touch emit.cpp/zd_plan/zd_omega_head" into the row — which is exactly the behaviour a green
structural clause licenses. It also cost a full independent re-derivation: seat05 re-found the mechanism from
SNOBOL4 `SEQ_driver` on 2026-09-04 via gdb + `SCRIP_ZD_DIAG`, not knowing the row existed, because nothing on
the board said it was open.

Same family as `RULES.md § A CORRECT PROCEDURE WITH A FALSE EXPLANATION`, and the same root shape as this
root's `command -v icont` lesson: **an instrument that answers a narrower question than you think you asked
will never say so.**

**Cured.** The clause now fails on any `op ==` chain *of any length*, on a predicate consulting no ω port (so
"admit everything" cannot pass), and on the function being absent (silence is not a pass). Proved to
discriminate all four shapes — including the one that was actually on disk:

| predicate shape | new clause |
|---|---|
| `op == IR_CMP_TEST` (the original) | ⛔ FAIL(op-identity) |
| **the four-op form — the false green** | ⛔ **FAIL(op-identity)** |
| `return 1` (admits everything) | ⛔ FAIL(admits-all) |
| function absent | ⛔ FAIL(absent) |
| ω-structural predicate | ✅ PASS |

## 4. ⭐⭐ ADMISSION WAS NEVER LOAD-BEARING — THE SEED IS

Built the class predicate (`ω.node && zd_chase(ω) != zd_chase(γ)`) and instrumented old-vs-new admission:

- On seat05's `SEQ_driver`, their `IR_GOTO_DEFERRED` flips exactly as predicted: **`oldhead=0 → newhead=1`**.
  `IR_STATEMENT_BEGIN`/`IR_STATEMENT_END`/`IR_SUBSCRIPT` flip too — **thousands** of nodes suite-wide.
- **The emitted assembly is byte-identical.** Same md5, deterministic over 5 runs, baseline vs cured; 0
  emission diffs over 72 SNOBOL4 programs; `IMAGE_driver` identical too (md5 `cdd8525d…`), both still SIGSEGV.

Because **pass 0 of `zd_plan` claims nearly every node via `bb_src_of` before the omega-head pass runs**, the
surviving gate is the seed: `zd_omega_seed()` returns `zon[k] ? zout[k] : 0` — **0** whenever the seeding
source is not itself on. seat05's measured 64-vs-0 is a **seeding** defect. The accept list is answered, and
it is not the answer. Two independent witnesses now agree: SEQ via `IR_SUBSCRIPT`, IMAGE via `IR_MATCH_BREAK`.

⚠ `SEQ_driver` is **confounded** — it also carries the code-object `RETURN` defect (row
`snobol4-return-after-a-code-object-transfer-crashes`, seat04). `IMAGE_driver`'s chain has zero `CODE()`/`:<`,
so it is the **unconfounded** acceptance witness (seat05's call, adopted).

## 5. ⛔ THE CLASS PREDICATE IS OVER-BROAD, AND THAT IS A SEPARATE OBJECTION FROM "IT REGRESSES"

In this IR the ω port is the generic per-statement failure funnel, so *almost every node* has ω ≠ γ — the
predicate admits `IR_LIT_INTEGER`, `IR_VAR`, `IR_STATEMENT_BEGIN`. It is not the test family; it is nearly the
whole graph. It is **inert today** and therefore harmless today, but a predicate that is right only by
accident of another pass claiming first is not a cure. The behavioural property that distinguishes the four
listed ops is a **role** — a test yields no value and its whole product is the port it selects — and this
codebase's sanctioned home for a role is a named family predicate in the spine (`ir_is_matcher`,
`ir_is_matcher_element`, `ir_is_call_kind` in `src/ir/IR.h`), not an ad-hoc list at an emitter use site.

## 6. ⛔⛔ THREE INSTRUMENT ERRORS I MADE, RECORDED BECAUSE EACH ONE PRODUCED A CONFIDENT FALSE STATEMENT

1. **I attributed a pre-existing red to my own change.** The gate reported `a_plainvar` and `pascal-boolidx`
   FAIL while I held the emitter change, and I wrote "the class fix regresses them" into a FINDING draft and
   into a message to ceo. **They fail identically on a baseline binary built from the unmodified tree** —
   same output, same error, byte-identical asm. My change causes neither. I had "re-measured" the gate and
   not the thing that mattered; the green I compared against was seat14's, from *yesterday, on a different
   tree*. `RULES.md § THE REBASE-BASELINE COROLLARY` is exactly this. ⭐ **A gate FAIL while you hold a change
   attributes itself to your change. The red is a fact; the attribution is an inference; only a baseline arm
   separates them.** (That red is real and is now its own row — see §7.)
2. **I edited the gate script while it was executing.** `bash` reads a script by byte offset, so the rewrite
   shifted the offsets and the running shell resumed mid-token: `syntax error near unexpected token '('` on a
   line that is valid. It had already printed plausible PASS/FAIL lines, **so it looked like a partial
   verdict.** Never trust a run that spanned an edit of its own script.
3. **I reused one scratch filename across two censuses** (`a.s` as both "baseline SEQ output" and a loop
   temporary) and reported `emission DIFFERS` for SEQ — false. Caught only by testing determinism (same
   binary twice) instead of believing the first diff. ⭐ **When two of my own measurements disagree, distrust
   the instrument rather than adopting the more interesting result.**

## 7. A SEPARATE, LIVE REGRESSION FOUND ON THE WAY — NOT PASCAL-ONLY UNTIL PROVEN SO

`corpus/tests/pascal/boolidx.pas` and the inline `a_plainvar` witness print their first line then die with
**`Run-time error 102 numeric expected`**, both modes, on **unmodified origin/main**. seat14 measured both
green yesterday at `c7fed4779`, so the window is `c7fed4779..5527fe274` (~20 commits); the error shape points
at `0fa9c4cb4` *"snobol4: an integer-required keyword coerces a STRING holding a real"* — a SNOBOL4-motivated
change to **shared** coercion. `boolptr` stays green as a control arm. Rowed as
`pascal-boolidx-and-a-plainvar-regressed-to-runtime-error-102-numeric-expected` (hq_P lane, PARKED under the
SNOBOL4 cut, DONE-WHEN proven red as written). ⛔ **A coercion change yields wrong numbers, not crashes** —
Pascal happened to convert it into a loud error; a SNOBOL4 program on the same path would print a different
digit and stay green against refs we generated ourselves. ⚠ It sat unnoticed all day because **the only gate
grading these two witnesses is not in `make test`.**

## 8. State left behind

- **LANDED:** the gate's structural clause (false green → true red) and this FINDING.
- **NOT LANDED:** the ω-structural predicate — inert (§4) and over-broad (§5). `emit.cpp` is reverted to the
  four-op filter and the repaired clause now correctly reports the row **⛔ FAIL**, which is the honest state.
- **NEXT (hq_C, HQ-only codegen lane, CEO-19):** fix the **seed**, not the accept list; define the test role
  once in `src/ir/IR.h` in the style of `ir_is_matcher`; grade on `IMAGE_driver`, not `SEQ_driver`.
