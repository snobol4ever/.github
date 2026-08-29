# FINDING — a row title that asserts a mechanism becomes the hypothesis nobody re-tests

**hq_C · 2026-08-29 · MODE FLEET-8 · row `pascal-m4-for-spine-leak-64b-per-iter`**

## What happened

The row is named **`pascal-m4-for-spine-leak-64b-per-iter`**. That name asserts three things: a **mechanism** (*leak*),
a **magnitude** (*64b*), and a **rate** (*per-iter*). None was ever re-measured. All three carried into every session
as if established — including into an hq_C design ruling, where I built a falsifiable arithmetic prediction
(`0x40 = 4 × 0x10`, "count the self-carving targets on the back-edge") **on top of the rate, without ever checking
the sign**.

seat08 executed the test exactly as briefed and reported back:

- the count is **~40, not 4** — the prediction is refuted
- the crash is **immediate**, at a loop-**transition** boundary (`n31_var_bx`), not a per-iteration creep
- `8191 × 64B ≈ 512KB` — nowhere near enough to explain an immediate crash even if the rate model held

## The thing the title hid, visible in the row's own GOAL line

> *"RSP drifts **UPWARD** 0x40 each traversal and runs off the **top** of the stack"*

and seat08's measured crash value: **`rsp=0x7ffffffff050`**, under `setarch -R`, which is **above the stack base**.

⭐ **The x86-64 stack grows DOWN. RSP rising past where it started is an OVER-RELEASE, not a leak.** The row's own
body contained the refutation of the row's own title, in the same sentence, and had for the row's whole life. Every
participant — three prior solo attempts, two seats, and this HQ — inherited the word *"leak"* and went looking for
carve-without-release. The correct search is for a **release whose matching carve is on a different path**, which
also explains, as nothing else does, why the crash is immediate and located at a transition.

## The rule this is an instance of

This is kin to § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE, one level up: **a NAME is a signal too.**
A row title, a variable name, a label — each is read by every downstream consumer, and when it asserts an unmeasured
mechanism, it is a confident specific claim that reads as a measurement. The distinctive damage is that a *title* is
re-read at the start of every session, so it re-installs the wrong model in each new participant, and the people best
placed to refute it are the ones it has already primed.

**Proposed, for ceo's judgement:** a row title may name a **symptom** and a **location**; it must not assert an
unmeasured **mechanism**, **magnitude** or **rate**. *"pascal-m4-for-sigsegv-rsp-above-stack-base"* would have been
true, useful, and would not have cost three sessions of looking in the wrong direction.

## What went right, and it is the process working exactly as designed

⭐ **The falsifier did its job and the seat used it correctly.** The brief said *"record the count either way, and do
NOT go hunting a fifth mechanism to rescue the arithmetic."* seat08 recorded `~40`, said plainly that the prediction
was refuted, offered their read as *"a read not a claim"*, reverted their patch, verified the tree byte-identical to
origin, and held. **A prediction that is cheap to falsify converts a wrong HQ answer into a measurement instead of
into wasted weeks.** The error cost one arm.

⛔ **One thing to correct in how the seat deferred:** seat08 wrote *"not confident it is the SAME edge or the SAME
magnitude your arithmetic assumed."* That instinct was better than the HQ arithmetic, and it arrived hedged. An HQ
number is not evidence. Told them so directly.

## Also recorded from the same session

- **`test_gate_icn_scan.sh` is RED (rc=1) and PRE-EXISTING** — a coverage floor (`m2 9<26 · m3 9<26 · m4 7<24`), not
  a correctness break. Proved by stashing an in-flight change, rebuilding, and re-running: identical rc, identical
  floor numbers. Named rather than adopted.
- ⭐ **A pull is a point-in-time fact, not a standing one.** All three repos were pulled at the start of the session;
  `test_gate_corpus_coverage_classified` still went red mid-grade because `crosscheck/coverage` was renamed to
  `tests/snobol4/coverage` on origin **during** the session. The SCRIP manifest had already retired the line,
  asserting *"corpus/crosscheck/ now holds nothing at all"* — true on origin, false in the local clone. A
  `merge --ff-only` resolved it. **A cross-repo claim is only as current as the stalest of the two clones.**
