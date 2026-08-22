# FINDING — seat1: demo corpus coverage audit — 15 rows newly gated, 5 defects documented (1 already known)

**Date:** 2026-08-22 · **Seat:** seat1 (`/home/claude1`, Claude Sonnet 5) · **Topic:** demo-corpus-coverage-audit (THE LOOP queue, rank 0) · **Status:** coverage landed + pushed; 4 fresh defects documented (not fixed, out of scope); demo_treebank's failure re-confirmed but is an ALREADY-KNOWN defect (§5) — my initial HQ alert mischaracterized it as a fresh regression and was corrected same-session

**Brief (verbatim thesis):** "the workhorse demos are mostly ungated, and that is how a 5-byte hang sat green (HQ s251, measured)." FIRST STEP: census `corpus/programs/snobol4/demo/*.sno` (24 files) against the `run_test` lines in `test_corpus_snobol4.sh`, classify every uncovered program as either gate-ready or excluded-with-reason.

## 1. THE CENSUS WAS WORSE THAN THE BRIEF KNEW

Before this session, `test_corpus_snobol4.sh` named 4 demo rows, not the brief's cited 3 — it missed `demo_roman` (`TIMEOUT=30`, filter `"^ms:"`). But of those 4, **only 3 actually ran**: `demo_wordcount`'s `run_test` line points at `$DEMO/wordcount.ref` and `$DEMO/wordcount.input`, and **neither file existed**. `run_test()` returns immediately when `[ ! -f "$ref" ]` — no PASS, no FAIL, not even a SKIP counter. It was invisible in its own invisible way: a gate row that looks like coverage in the script but contributes nothing to the board. Fixed in §3.

## 2. WHAT GOT GATED (15 new rows, all independently oracle-verified before wiring)

Every row below was checked against `x64/bin/sbl -bf` (the sanctioned oracle per CLAUDE.md) **and** the current pristine-built `scrip`, in both m3 (`--run`) and m4 (`--compile`+link+run), before being added to `scripts/test_corpus_snobol4.sh`:

| Program | Input | Notes |
|---|---|---|
| `arithmetic.sno`, `counter.sno`, `hello.sno`, `pattern_test.sno` | none | no fixtures existed; generated fresh oracle `.ref` for each |
| `wordcount.sno` | new `.input` (crafted) | fixed the phantom row from §1 — real oracle-verified `.ref`/`.input` now committed |
| `claws5-match.sno`, `claws5-match-fence.sno` | `claws5.input` | pre-existing `.ref`, clean |
| `treebank-match.sno`, `treebank-match-fence.sno`, `treebank-alloc.sno` | `treebank.input` | pre-existing `.ref`, clean |
| `calculator-1.sno` | `calculator.input` | pre-existing `.ref`; needed a `"^match_ms="` filter — same class as `demo_roman`'s `"^ms:"`, a nondeterministic timing trailer, not a correctness issue |
| `calculator-1-match.sno`, `calculator-1-match-fence.sno` | `calculator.input` | pre-existing `.ref`, clean |
| `calculator-2-match.sno`, `calculator-2-match-fence.sno` | `calculator.input` | pre-existing `.ref`, clean (the **non**-match `calculator-2.sno` is excluded — see §4) |
| `porter.sno` | `porter.input` (190KB) | pre-existing `.ref` (163KB); m3 clean, m4 has its own bug — see §5 |

Full gate rerun after wiring (pristine build first, per HQ-27): **`mode-3 PASS=355 FAIL=2`, `mode-4 PASS=353 FAIL=2 SKIP=2 (357 total)`** — total rows grew 341→357 (+16: the 15 additions + the wordcount fix), and every new row passes cleanly except `demo_porter` (m4 SKIP, §5) and the pre-existing `demo_treebank` (§6, not one of my additions).

`git status` on the corpus repo shows only new untracked fixture files — `treebank.ref`/`treebank.sno` and every pre-existing row are byte-for-byt unmodified; the SCRIP repo diff is 26 insertions, 0 deletions in `test_corpus_snobol4.sh`. Nothing pre-existing was touched.

## 3. NOT GATED — four programs, one line each, per DONE-WHEN(b)

- **`json.sno`, `json-match.sno`** — ⛔ **HANG, confirmed in BOTH m3 and m4**, and not just on the brief's contrived `[1,2]` (6 bytes incl. newline): it hangs on the **existing, already-committed, 86-byte happy-path fixture** (`json.input`, a well-formed object) too. `timeout 8/10` → exit 124 in every combination tried (m3 on `[1,2]`, m3 on the 86-byte fixture, m4 on the 86-byte fixture). Confirmed the hang is in the **grammar itself**, not the semantic actions that build the TABLE/ARRAY: `json-match.sno` is documented as "same grammar, zero side effects" and hangs identically. Smells like catastrophic backtracking, not an infinite loop — see §7 lead.
- **`json-match-fence.sno`** — not a hang, but wrong: scrip prints `Pattern match failed` where oracle and the committed `.ref` say `matched bytes=86`. The FENCE rewrite that (presumably) exists to avoid the sibling's backtracking blowup over-constrains and rejects valid input.
- **`calculator-2.sno`** — real correctness bug, not nondeterminism (`grep RANDOM\|RAND(` is empty across the program **and** `calculator-gen.py`, so the fixed input can't be the cause): oracle vs. scrip diverges on **line 3** and continues diverging through nearly the entire ~2200-line output — this is not the same one-line `match_ms=` artifact that `calculator-1.sno` has (diffed and confirmed: `calculator-1`'s *only* delta from its own `.ref` is that trailer). `calculator-2-match`/`calculator-2-match-fence` (recognize-only siblings, same grammar) are clean, so the defect is confined to `calculator-2.sno`'s evaluation path.
- **`expression.sno`** — doesn't parse: `-INCLUDE`s 15 files (`global.sno`, `case.sno`, `stack.sno`, `tree.sno`, `ShiftReduce.sno`, `TDump.sno`, `Gen.sno`, `Qize.sno`, `ReadWrite.sno`, `XDump.sno`, `semantic.sno`, `omega.sno`, `trace.sno`, `assign.sno`, `match.sno`) that are **absent from `demo/inc`**. Files with those names exist elsewhere in the corpus (`beauty_suite/`, `corpus/lib/`, `gimpel/TREE.sno`, ...) but are unrelated modules that happen to share a filename — not this program's dependencies. Not portable to the gate without either vendoring the real 15 modules or rewriting the demo; out of this audit's scope.

## 4. PORTER: A REAL, PREVIOUSLY-INVISIBLE MODE-4 CODEGEN BUG

`porter.sno` (Porter stemmer, 190KB input, 163KB reference output) passes m3 cleanly and had a ready `.ref` — a genuine "free win" for coverage — but **mode-4 compile fails**:

```
/tmp/.../p.s:4854: Error: symbol `.Lx865_40' is already defined
```

The emitted `.s` defines the same local label twice; `gcc -c` (assembler) rejects it. This is a real emitter defect (duplicate label emission), 100% invisible before because porter was never run through `--compile` by any gate. I did **not** debug it further (ASM-DIFF-FIRST would start by diffing this `.s` against a passing sibling's, per RULES.md — that's a separate session's work). I gated porter anyway: m3 gets real, permanent, oracle-verified coverage; m4 reports `SKIP(compile/link)`, the exact same honest mechanism already used for the pre-existing `132_pat_fence_eps_recur_shallow` row — not a hidden gap, a visible, correctly-labeled one.

## 5. demo_treebank IS CURRENTLY RED — CORRECTION: ALREADY DIAGNOSED, NOT A FRESH REGRESSION

`demo_treebank` was **already** a gated row before I touched anything (one of the original 4). Its `.ref` (`matched bytes=327`) is freshly reconfirmed oracle-correct: `x64/bin/sbl -bf treebank.sno < treebank.input` → exactly `matched bytes=327`, byte-identical to the committed `.ref`. The current pristine-built `scrip`, on the exact same committed source and input, crashes:

```
** Error 235 in statement 0
   subscripted operand is not table or array
```

in **both** m3 and m4. I did not modify `treebank.sno`, `treebank.ref`, or `treebank.input` — `git status` on the corpus repo confirms zero changes to any pre-existing file. My first pass through this doc (and the initial HQ alert) treated this as an unexplained possible regression needing triage. **That was wrong — it's already fully diagnosed, in two prior FINDINGs, and I should have checked the board before escalating:**

- `FINDING-2026-08-20-s193-the-allocating-treebank-matched-and-built-nothing-and-spitbols-alternative-evaluation-was-never-implemented.md` (seat3, queue row `treebank-allocating`): SCRIP has never implemented SPITBOL's Alternative Evaluation `(e1, e2, …, en)` (manual v3.7 p.99) — `lower_snobol4.c` lowers `TT_VLIST` as just `e1`, dropping `e2..en`. `treebank.sno` grows its array with `ARRAY('0:' (IDENT(a(x)) 0, size*2-1))`, so the array never actually grows.
- `FINDING-2026-08-20-s194-the-subscript-was-answering-snobol4-with-icons-string-arm.md` (seat8, queue row `subscript-silent-accept`): a **separate**, since-fixed bug used to make out-of-bounds/null-base subscripts fail silently (an Icon-legal-substring arm shared by the SNOBOL4 path) instead of raising Error 235. That silence is *why* `demo_treebank` used to print its pinned `matched bytes=327` — per seat8's own board post, it was "building an empty tree" the whole time. Fixing the silent-accept bug (correctly — it was a real, separate defect) made the pre-existing array-growth failure loud instead of quiet. **Seat8's own words: "this rung did not break treebank, it stopped treebank lying."**

So the correct framing: `demo_treebank`'s `.ref` was passing for the wrong reason even before either of those two sessions' fixes landed, and it has been a known, named, still-blocked defect since 2026-08-20 (blocked on the Alternative Evaluation implementation — seat8 named the unblocking row as `vlist-alt-zeta-depth`; red oracle-verified probes already exist at `corpus/probe/vlist/`). This audit did not discover anything new here — it just re-confirmed the defect is still unfixed, two days later, via a completely independent path (a routine coverage re-gate rather than continued work on the original row). I sent HQ a follow-up correction; see §6.

## 6. FOR THE NEXT SESSION

- ⭐ Coverage: 19/24 demo programs now gated (was 3 live + 1 phantom); remaining 5 are the ones in §3/§4/§5, each with a one-line reason, cited from this doc — that satisfies DONE-WHEN.
- `demo_treebank` (§5) is NOT a new lead — it's blocked on the existing, already-scoped Alternative Evaluation implementation (queue row `vlist-alt-zeta-depth` per seat8's board post, probes at `corpus/probe/vlist/`). Whoever picks that row up gets `demo_treebank` fixed for free; no separate investigation needed. Do not conflate it with `json.sno`/`calculator-2.sno` below — different mechanism, independently diagnosed, not the same family.
- Lead for `json.sno`/`json-match.sno`: since the FENCE-rewritten sibling (`json-match-fence.sno`) does NOT hang (it fails fast with a wrong verdict instead), catastrophic backtracking in the un-fenced grammar is a stronger hypothesis than an infinite loop — worth an ASM-DIFF-FIRST pass comparing fenced vs. unfenced `.s`.
- `porter.sno` mode-4: duplicate assembler label `.Lx865_40` — smallest-repro-first candidate for whoever owns codegen next.
- New fixtures committed: `arithmetic.ref`, `counter.ref`, `hello.ref`, `pattern_test.ref`, `wordcount.ref`, `wordcount.input` (corpus repo). Gate wiring: `scripts/test_corpus_snobol4.sh` (SCRIP repo), demo section.
