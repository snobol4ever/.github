# A crashed callgrind run hands back a plausible Ir total, and six harnesses published it

**Found by:** hq_P, 2026-09-10, on hq_U's ask that the void my Icon kernel board applied to one
crashed cell become the rule for **every** Ir cell in the tree.
**Tree:** SCRIP `429c259e8` · corpus `69d9fa5b0` · `.github` `fa2e36da` · `RT_OPT=-O0`.
**Status:** CURED and gated. Predecessor: `FINDING-2026-09-10-hq_P-both-icon-modes-segv-under-
valgrind-in-gc-zeta-frame-while-running-clean-natively.md` (that one is hq_U's, still open).

## The defect, stated generally rather than on Icon

callgrind counts instructions whatever the client does. A program that SEGVs, error-exits, or is
killed by a timeout still produces a well-formed `PROGRAM TOTALS` — the instruction count of its
dying path — in the same shape as every honest cell on a board.

Witness, deliberately not an Icon program so the class is visible: a C program that sums 200,000
ints and then writes through a null pointer yields **2,157,144 Ir** to the exact `awk` extraction
six harnesses used. Its honest sibling reads 2,154,815. The crash is **0.004%** away from the
truth — inside the noise of anything a reader would sanity-check it against.

⭐ **A crash that announces itself as a NUMBER is strictly worse than one that announces itself as
a HOLE** (hq_U's phrasing, and it is the right one).

## ⛔ The correction I owe my own earlier finding

That finding argued the void partly from **non-determinism** — two crashed Icon runs disagreeing by
1,814 Ir on an instrument whose validity rests on byte-identical reproduction. **That argument is
weaker than it looks and this row should not rest on it.** Measured here: three crashed runs of the
null-deref witness at fixed argv+env read **2,157,204 three times, byte-identical.** A crashed
reading can be perfectly reproducible. The Icon `concat_table` disagreement is a property of *that*
program — its fault point moves with heap and GC state — not of dead runs in general.

⭐ **The argument that always holds is simpler: the number counts a path that did not do the work,
so it does not answer the question the column asks. Reproducing it exactly only makes it a reliable
answer to the wrong question.**

## Where it was live

| harness | what it did |
|---|---|
| `bench_triangulate_snocone.sh` | no exit-status check at all — **and divided by the result** |
| `bench_triangulate_rebus.sh` | no exit-status check at all |
| `profile_callgrind.sh` | a full blob-share attribution table computed off a dying path |
| `test_gate_instr_budget.sh` | ⛔ **the worst direction** — see below |
| `test_gate_dispatch_gc_safepoint_inline.sh` | ⛔ **an A/B, the shape that hides a crash best** — see below |
| `bench_ir_slope.sh`, `bench_two_number_ir.sh` | void was already correct; only the **reason** was lost |

⛔ **`test_gate_instr_budget.sh` fails in the worst possible direction.** A program that dies early
does *less* work, so an uncaught SEGV arrives **below** the watermark and `check_budget` prints
`NOTE … improved; consider re-pinning down`. **The crash would have argued for lowering the budget
it broke.**

⛔ **`test_gate_dispatch_gc_safepoint_inline.sh` is an A/B, which hides a crash better than anything
else.** If the cure-on and killswitch-off arms both die the same way they produce the same (empty)
output, the correctness `diff` **passes**, and the two dying-path counts are then compared to each
other as though they measured the cure. ⭐ **Two crashes that agree look exactly like two
measurements that agree.** Only the exit status tells them apart.

⭐ The last two are the subtler lesson: their void was already right, and they were still wrong. A
crashed arm and an absent valgrind both printed one bare `UNPROVEN`/`NA`. **"Not measured" and
"measured and thrown away" are different facts, and a board that prints one word for both has
destroyed the difference.**

## The cure

`SCRIP/scripts/lib_ir_measure.sh` — THE ONE AUTHORITY for **taking** a reading, as
`lib_perf_fmt.sh` is for **printing** a multiple, and for the identical recorded reason: six
harnesses re-derived this rule and four of them got it wrong. A caller that cannot load it REFUSES
rather than falling back to a private extraction.

**Three outcomes, never two:** `<digits>` · `RC:<n>` → `REFUSED(rc=n)` · `NOMEASURE:<why>` →
`NOT-MEASURED(why)`, each with an `ir_reason` sentence. ⭐ **The status rides in the VALUE**, never
in a global and never in a return code — the first cut of the Icon harness carried it in a global
that could not survive the command substitution calling it, so a crashed arm read back as rc=0 with
an empty value and printed a bare `NA`.

## The gate, and why neither arm is a grep

`SCRIP/scripts/test_gate_ir_reading_voids_a_dead_run.sh`.

- **ARM 1 is behavioural.** It builds programs that really die and requires all four outcomes to be
  distinguishable. It also asserts **the trap is still real** — that an unguarded reader still gets
  a well-formed total from the crash — so the gate voids something rather than congratulating
  itself on an absence.
- **ARM 2 censuses call sites**, and skips comment lines. Its first cut flagged `bench_wrap.sh`,
  whose only hit is the phrase inside a comment listing tools. ⭐ **A census that counts prose finds
  violations nobody can fix, which is how a gate teaches people to ignore it.**

⛔ **Mutation-proved in both directions**, because a gate that cannot fail is the `make test` trap
wearing a different hat: a lib that ignores `rc` reds ARM 1 — **the SEGV read back as 1,157,112,
plausible enough to pass any range check** — and a new unguarded call site reds ARM 2.

## Verified

- ✅ gate green; both negative arms red on demand.
- ✅ `test_gate_dispatch_gc_safepoint_inline.sh` PASS on a fresh incremental build — cure-on
  97,507,435 Ir vs killswitch-off 103,433,105 Ir (5.73%).
- ✅ `bench_triangulate_rebus.sh` green, `voided_arms=0`.
- ⚠️ `bench_triangulate_snocone.sh` still REFUSES rc=2 on `fib_recur`'s mode-4 link. **PRE-EXISTING
  and not this row** — control arm: the unmodified script from `HEAD`, copied into `scripts/` so its
  `$HERE` resolves and run in place, fails identically, and the `gcc` line is byte-identical. It is
  a real red someone owns; it is not mine and I did not touch it.
