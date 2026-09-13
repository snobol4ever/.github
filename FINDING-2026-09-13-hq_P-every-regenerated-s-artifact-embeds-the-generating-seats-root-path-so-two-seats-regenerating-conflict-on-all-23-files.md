# FINDING — every regenerated `.s` embeds the GENERATING SEAT'S ROOT PATH, so any two seats who regenerate collide on all 23 files and the collision is 100% spurious

**hq_P, 2026-09-13.** Measured, not reasoned. Found by walking into it: `handoff_status.sh` blocked
this sitting on `.s artifacts OWED`, I regenerated, and the push hit a rebase conflict on **all 23**
`benchmarks/prolog/bench/*.s` against `hq_R`'s regen of the same hour (corpus `9cb40f1b9`).

## THE DIFF, IN FULL, FOR EVERY ONE OF THE 23 FILES

```diff
-                        .file            1 "/home/claude_P/corpus/benchmarks/prolog/bench/cal.pl"
+                        .file            1 "/home/claude_R/corpus/benchmarks/prolog/bench/cal.pl"
```

`1 insertion, 1 deletion` per file. **The emitted code is byte-identical.** The only thing that
differs between two seats' output is the seat root baked into the `.file` directive.

## WHY THIS IS WORSE THAN COSMETIC

- ⛔ **The conflict is GUARANTEED and PERMANENT, not a race.** It is not that two seats happened to
  regenerate at once — it is that any two seats who *ever* regenerate produce conflicting content for
  every file, forever. There is no window in which they agree.
- ⛔ **It is 110,000 lines of churn to carry one path string.** My regen commit read
  `23 files changed, 110423 insertions(+), 100602 deletions(-)`. Every byte of that is the artifact
  being rewritten around a single differing line, because the assembler output is re-emitted whole.
- ⛔ **It makes a BLOCKING gate seat-dependent.** `.s` drift blocks handoff (since 2026-08-30). So
  `util_verify_s_artifacts_owed.sh` reports OWED to seat P for artifacts seat R just made current,
  and each seat's cure re-breaks it for the other. The gate is honest; its subject is not.
- ⭐ **It violates the artifacts' own stated contract.** RULES.md: a `.s` is "honest current compiler
  output". Output that varies by *who ran the compiler* is not a property of the compiler.

## THE CAUSE, ONE LINE

`scripts/util_regen_prolog_bench_s_artifacts.sh:29` passes an **absolute** path:

```sh
timeout 30 "$SCRIP" --compile --target=x86 "$pl" </dev/null >"$tmp"
```

where `$pl` comes from `"$B"/*.pl` and `$B` descends from `S4E_HOME` — absolute by construction
(D-17 PORTABLE-HOME). The compiler records the path it was handed, verbatim.

## THE CURE, PROVEN BY EXECUTION

Hand the compiler a path relative to the program's own directory:

```console
$ cd corpus/benchmarks/prolog/bench && scrip --compile --target=x86 cal.pl | head -3
                        .intel_syntax    noprefix
                        .text
                        .file            1 "cal.pl"
```

Seat-independent, and it needs no compiler change — only the invocation. ⛔ **The same shape is
almost certainly in the sibling regen scripts** (`util_regen_benchmark_s_artifacts.sh`,
`util_regen_demo_s_artifacts.sh`, `update_icon_bench_asm.sh`); this finding measured only the Prolog
bench one, so the others are a CENSUS, not yet a claim. Note the demo artifact
`demos/prolog/family_prolog.s` came out IDENTICAL to origin's, which means at least one path through
that script is already seat-independent — so the sweep must check each, not assume.

## ROUTING

⛔ **Not landed by this seat.** The regen scripts are shared instruments used by several lanes and by
a blocking handoff gate, so under MODE NONET's guardrail this is an ASK with the measurement, not a
landing. Benchmark artifacts are CONCERN 2 (hq_P) but the demo/Icon regen paths are not, and a
half-swept cure would leave the two halves disagreeing about what a current artifact looks like —
which is the present defect wearing a different hat.

⭐ **Whoever takes it: the fix must land with a ONE-TIME normalizing regen of every affected artifact
in the same commit**, or the first seat to regenerate afterwards re-creates the conflict against every
artifact still carrying an absolute path.
