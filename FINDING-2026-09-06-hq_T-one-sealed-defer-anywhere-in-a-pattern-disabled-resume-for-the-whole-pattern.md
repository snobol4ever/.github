# One sealed DEFER anywhere in a pattern disabled the resume carrier for the WHOLE pattern

**Seat:** hq_T · **Date:** 2026-09-06 · **Row:** `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries`
**Cure:** SCRIP `7de78810a` (`src/emitter/emit.cpp`) — `_sd` scoped to the body_root instead of the whole node list. Corpus `6f9eaa0ea` promotes the two markers and corrects four stale reasons.
**DONE-WHEN n: 13 → 11.** Cured: `arbno_fence_bal_replace_branch_1` and `_3`, both modes.

## The witness, minimized to five load-bearing ingredients

```
G0 = FENCE('a')
P  = (ARBNO(*G0) | 'zzz')
'a' POS(0) *P RPOS(0)        scrip=nomatch   oracle(sbl -bf)=match
```

Remove **any one** and SCRIP agrees with the oracle again — each was ablated and measured, not argued:

| removed | replacement | result |
|---|---|---|
| the FENCE | `G0 = 'a'` / `BAL` / `LEN(1)` | AGREE |
| the inner defer | `ARBNO(FENCE('a'))` inline | AGREE |
| the alternation | `P = ARBNO(*G0)` | AGREE |
| the ARBNO | `P = (*G0 \| 'zzz')` | AGREE |
| the outer defer | pattern written inline at the match | AGREE |

⚠️ The fifth (`*P`) was NOT in my first ingredient list. I inherited `*P` from the fuzz witness and
carried it unablated through four probes, publishing "four ingredients" before testing it. The inline
form agrees, so the outer defer is load-bearing and the count was wrong. **An ingredient you never
removed is not an ingredient you tested** — inheriting a witness's scaffolding as if it were its subject.

## The defect

`emit.cpp`'s resume gate computed:

```c
int _sd = 0; for (int i = 0; i < n; i++) if (nodes[i]->op == IR_MATCH_DEFER && nodes[i]->seal == 1) { _sd = 1; break; }
...
if (!_f1r) for (...) if (nodes[i] == body_root && resume_carrier_ok(nodes[i], _sd)) resume_tgt = betas[i];
```

and `resume_carrier_ok` at seam tier 3 returns `(_nc == 1 && !sealed_defer && !nd->seal)`.

`nodes[]` is **every node of the pattern**. So a sealed DEFER *anywhere* — here `*G0`, buried inside the
ARBNO's body — cleared the resume carrier for the pattern's **root**. `P` then compiled with
`resume_tgt = lbl_ω`: once it succeeded it could never be re-entered. `POS(0) *P RPOS(0)` therefore took
`P`'s zero-iteration solution, failed `RPOS(0)`, and conceded the whole match instead of asking `P` for
its next solution.

The scope is wrong in both directions of the semantics. A sealed defer forbids backtracking **into that
defer**; it says nothing about whether the *root alternation* has another solution — and here it plainly
does, since the ARBNO arm yields one more iteration. `resume_carrier_ok` already tests the body_root's own
seal (`!nd->seal`); the `sealed_defer` parameter was a second, wider test of a different node.

**Measured proof of the mechanism, not inferred:** `SCRIP_RESUME_WHY=1` prints `sd=1` for the failing
witness and `sd=0` for the passing one, with every other field of `[RESUME-WHY]` identical. A gdb trace of
the m4 binary confirms the consequence: `n5_match_arbno_β` is **never reached** — the retry never happens.

## The cure

`_sd` is set only when the sealed DEFER **is the body_root or a direct operand of it** — the nodes whose
seal can actually bear on receding into the body_root. One expression in one function; no new global, no
new IR field, no template change.

⛔ Deliberately NOT done: widening `resume_carrier_ok`, or deleting the `sealed_defer` parameter. Two
other call sites below read `_sd` for the alt-carrier fallbacks, and the differential below is what
licenses the narrowing — not the argument above it.

## Blast radius — measured over all seven languages, 5021 master entries, not sampled

| master | entries | asm CHANGED | identical | compile-fail both | rc diverged |
|---|---|---|---|---|---|
| snobol4 | 1882 | **2** | 1844 | 36 | 0 |
| icon | 837 | 0 | 826 | 11 | 0 |
| prolog | 693 | 0 | 649 | 44 | 0 |
| raku | 917 | 0 | 855 | 62 | 0 |
| snocone | 302 | 0 | 290 | 12 | 0 |
| pascal | 251 | 0 | 251 | 0 | 0 |
| rebus | 139 | 0 | 136 | 3 | 0 |

The 5019 byte-identical or identically-compile-failing entries are **exonerated by construction**. The two
that changed are the two cured entries, FAIL→PASS in both modes. Stability 10/10 with ASLR on and 3/3 under
`setarch -R`, both modes, both entries.

⭐ The cross-language arms are the SHARED-NODE VERDICT SCOPE control: `emit.cpp` is shared by all seven
frontends, so "SNOBOL4 is green" would not have discharged the duty. Byte-identity discharges it more
strongly than a board could, because it holds per entry rather than in aggregate.

## Two candidate cures FALSIFIED first, and cheaply

Both were plausible from the code and both were disproven on the witness in minutes, before any board:

* **Always emit ARBNO's exhaust `jne`** (`bb_match_arbno.cpp:120` drops it when `actframe`). The dropped
  `jne` is real and visible — the emitted exhaust arm ends `cmp r14d, eax; jmp <concede>`, a compare whose
  answer is thrown away. It is a **symptom**, not the cause: restoring it left the witness at `nomatch`.
* **Count a sealed DEFER as `_dfr` rather than `_ref`** in the `op_arbno_body_actframe` classifier
  (`emit.cpp:1214`). Also `nomatch`.

⛔⭐ **A pair I compared was not a one-ingredient pair, and it briefly produced a confident wrong answer.**
I first diffed the failing witness against `ARBNO(*G0)` *without* the alternation, saw the same missing
`jne` in both, and concluded the `jne` was irrelevant. Both halves of that were wrong: the programs differed
by two ingredients, and the `jne` **is** the delta on the true pair (`G0='a'` vs `G0=FENCE('a')`, everything
else fixed). **A differential over a pair that differs in two places cannot exonerate either one** — and it
fails silently, because it still prints a clean diff.

## Instrument notes for the next seat on this row

* `SCRIP_RESUME_WHY=1` prints `[RESUME-NIL]`, `[RTGRAPH]`, `[RESUME-GATE]` and `[RESUME-WHY]`. It named this
  defect in one line after the ablation. It was already in the tree; nobody on this row had used it.
* `setarch -R` remains mandatory for this family (2 of the original 19 are ASLR-bimodal). All measurements
  here are deterministic runs.
* `grep -a` on any `ALL.*` — `ALL.ref` holds a NUL byte at offset 919, so plain grep reports rc=1 and no
  output for a name that is certainly present. Promotion here was done byte-level in Python for that reason.

## Receipt

Graded on an **incremental `make`** (HQ-27 pristine-before-verdict is VOID as a per-landing requirement, Lon
2026-09-03). SCRIP `7de78810a` · corpus `6f9eaa0ea` · `RT_OPT=-O0` · both modes · all measurements under `setarch -R`.

⛔ **No board is quoted in this receipt, and that is deliberate rather than an omission.** My first run graded a tree I
rebuilt under it three times and I stopped it — a board grading a moving tree is not a receipt, and quoting one would
be worse than having none. A clean board was launched on the settled tree after the push. The landing evidence is the
5021-entry cross-language differential above, which is stronger than a board for this change: it holds per entry
rather than in aggregate, and byte-identity exonerates by construction.

Per CEO-335 the inherited red set is the **demo_\*** class only (json, calculator-1, calculator-2, treebank and their
`_match` / `_match_fence` variants), owned by hq_R, cause `285f8fb12`. Nothing this change touches is in that set —
the only two entries whose emitted code changed at all are `arbno_fence_bal_replace_branch_1` and `_3`, and both moved
FAIL→PASS. The `user_function_*` inheritance is withdrawn as of CEO-335 and none of those entries changed here either.
