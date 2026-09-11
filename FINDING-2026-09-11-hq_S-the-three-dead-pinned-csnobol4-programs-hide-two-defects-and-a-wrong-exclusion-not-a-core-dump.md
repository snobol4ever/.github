# FINDING — the three dead-pinned csnobol4 programs hide two defects and a wrong exclusion, not a core dump

**Seat:** hq_S · **When:** 2026-09-11 · **Mode:** NONET (read from `/home/resources/postoffice/MODE`)
**Row:** `snobol4-an-unresolved-return-label-dumps-core-and-three-dead-pins-were-hiding-it` (rank 0, ceo CEO-427)
**Trees:** SCRIP `70a0bc6c0` (incremental `make`, `RT_OPT=-O0`) · corpus `aa4bb4238` · .github `dce803caf`
**Oracles:** `/home/resources/x64/bin/sbl -bf` (the one correctness oracle) and `/home/resources/csnobol4/snobol4`
(the suite's own upstream engine, named as "the reference engine" in the row's GOAL)

## The claim in one line

The row's premise — `function`, `label` and `setexit4` all abort at `site=865 label=RETURN` — **does not
reproduce, and did not reproduce at the tree the row was minted on**. The row's *second* half, which nobody had
done, pays: comparing all three against the reference engines names **one dialect gap, one live SCRIP defect,
one wrong exclusion that was hiding that defect, and one crash that is real but in a different program shape.**

## 1. The abort: confirmed absent at the MINT-TIME tree, not just at HEAD

hq_B reported on 2026-09-09 that the aborts do not reproduce on origin HEAD freshly built
(`FINDING-2026-09-09-hq_B-the-three-aborts-behind-the-dead-pins-do-not-reproduce-on-origin-head-freshly-built.md`)
and named a stale binary as the remaining explanation. **I closed the remaining hole in that argument**: HEAD had
moved, so "HEAD is clean" and "the ceo's tree was clean" are different claims. I built `01eb996ca` — the SCRIP
commit standing at the moment the row was minted (2026-09-09T02:55Z) — in a **separate worktree with its own
objdir**, and ran all three the runner's way:

| program | CEO-427 | `01eb996ca` fresh worktree build, m3 | `70a0bc6c0` m3 | `70a0bc6c0` m4 |
|---|---|---|---|---|
| `function` | 4 lines then ABORT | rc=0, 8 lines | rc=0, 8 lines | rc=0, 8 lines |
| `label`    | 4 lines then ABORT | rc=0, 4 lines | rc=0, 4 lines | rc=0, 4 lines |
| `setexit4` | 4 lines then ABORT | rc=0, 8 lines | rc=0, 8 lines | rc=0, 8 lines |

⭐ **The stale-binary reading is now proven rather than inferred.** hq_B's mechanism argument stands untouched:
`bb_emit_end` (`src/emitter/emit.cpp:133-147`) aborts at EMIT time, so stdin, cwd and `split_at_end` cannot
reach it — only the binary can. **The abort class on these three programs is CLOSED as a defect of the tree.**

## 2. `function` and `label` — the oracle refuses them; the residual is one dialect gap

`sbl -bf` dies at the first `FUNCTION(`/`LABEL(` call: `ERROR 022 -- undefined function called` at line 2 and
line 5 respectively, **rc=0 while printing a fatal report** (the gimpel shape). Both are already permanently
filed in `OUTSIDE_SPITBOL_BASELINE.tsv`, correctly. Their `.ref` files are transcripts of the oracle dying —
and ⛔ **the runner's own `--recut` arm would cut that transcript again**, because it accepts a ref whenever
`rc != 1` (`test_snobol4_csnobol4_suite.sh`). The dead pin here is REPRODUCIBLE BY THE INSTRUMENT, not a
one-time accident; that is worth more than the two programs.

Against the suite's own engine both are near-green, and the residual is **one cause, not two programs**:

| program | csnobol4 | SCRIP | the gap |
|---|---|---|---|
| `function` | 10 lines | 8 | the `&CASE = 1` block repeats the `&CASE = 0` answers |
| `label` | 5 lines | 4 | same block, same cause |

`&CASE = 1` does not re-enable case-folded name lookup for `FUNCTION()`/`LABEL()`. ⛔ This is **outside the one
oracle** — SPITBOL's `&CASE` is documented as compile-time folding (manual :7891) and `sbl` never reaches these
calls — so it is a dialect note, not a board cell, and I am not curing it on my own word.

## 3. `setexit4` — a live SCRIP defect, and an exclusion that was hiding it

**Both reference engines refuse `&Z = 1`; SCRIP alone accepts it.**

| engine | on `&Z = 1` |
|---|---|
| `sbl -bf` | `ERROR 251 -- keyword operand is not name of defined keyword` |
| csnobol4 | `err: 7 (Unknown keyword) @S9` |
| SCRIP | **nothing — the statement succeeds** |

The cause is `&USER_DECLARED_CONSTANTS`, which **defaults to 1** (`src/runtime/keywords.c:191,224`), so every
undefined `&NAME` lands in the user-constant namespace instead of being diagnosed. Flipping that default to 0
and rebuilding takes `setexit4` from diverging at output line 4 to agreeing through line 8, and exposes three
further items, each measured under that experiment and then reverted:

1. `&ERRTEXT` carries an appended operand (`... not name of defined keyword: &Z`) where SPITBOL's text is bare;
2. `&LASTNO` reads 13 in the handler where `sbl` reads 18;
3. `:(SCONTINUE)` inside a live handler: `sbl` raises `ERROR 331 -- goto scontinue with no user interrupt` and
   re-enters the handler until `&ERRLIMIT` is exhausted; csnobol4 resumes the interrupted statement; SCRIP
   follows csnobol4. **A genuine engine split with no single reference answer.**

⛔ **BLAST RADIUS OF THE DEFAULT FLIP, MEASURED RATHER THAN FEARED.** Every deliberate UDC witness in the master
sets the switch explicitly first (`grep -n USER_DECLARED_CONSTANTS corpus/tests/snobol4/ALL.sno`), so the 27
`probe_cn__` entries do **not** rest on the default. A token census of `ALL.sno` for a non-canonical `&Name`
on a line that does not set the switch leaves **three one-liner entries** (`keyword_1`,
`arbno_pos_rpos_branch_*`) plus multi-line entries that set it on another line. ⛔ The flip is a SNOBOL4-wide
default and hq_P already holds the sibling row `snobol4-unknown-keyword-assignment-not-detected`
(named in its own `test_gate_sno_keyword_spelling_is_case_sensitive.sh` header, landed the same day), so this
is routed as an ASK with the measurement, not landed.

### The exclusion that was hiding it

`setexit4.sno` was filed outside the SPITBOL baseline the same day on the ground that *"the program sets &Z, a
settable USER keyword CSNOBOL4 allows and the one oracle does not."* ⛔ **That ground is backwards** — csnobol4
answers `err: 7 (Unknown keyword)` on that very line, so no engine allows `&Z`, and the sentence converted a
defect of ours into an oracle allowance. ⭐ **The instrument caught it independently the same hour**: ARM 20 of
`test_gate_package_runners_print_the_inventory.sh` refused the package because the reason named our own
compiler, which is `lib_inventory.sh`'s standing rule — *UNGRADABLE is a statement about the ORACLE, never
about us; a program excluded because we fail it is a red moved out of the denominator.* **The exclusion still
stands, on the SCONTINUE ground above, which is an oracle fact**; the reason column in both
`UNGRADABLE.tsv` and `OUTSIDE_SPITBOL_BASELINE.tsv` is rewritten to say so, and the `&Z` half is named as our
row rather than carried as an exclusion. This is hq_V's standing practice paying out twice in one sitting: a
wrong exclusion costs more than a wrong cure, because a red stays visible and an excluded name cannot be red.

## 4. Two cures landed from this row

**(a) A goto with no preceding error is three diagnostics, not one.** Measured live against `sbl -bf`:

| goto at level zero, no preceding error | `sbl -bf` | SCRIP before | SCRIP after |
|---|---|---|---|
| `:(ABORT)` | `ERROR 036 -- goto abort with no preceding error` | `ERROR 035 -- Not in a SETEXIT handler` | matches |
| `:(CONTINUE)` | `ERROR 037 -- goto continue with no preceding error` | `ERROR 035 -- Not in a SETEXIT handler` | matches |
| `:(SCONTINUE)` | `ERROR 321 -- goto scontinue with no preceding error` | `ERROR 035 -- Not in a SETEXIT handler` | matches |

`035` is **csnobol4's** error 35 reached through `core_err_msgs[]`, which SCRIP carries for codes 1..39. It is
dialect residue: `core_errnum_csnobol4()` has been hard `0` since the compat switch was retired at CEO-388/390,
so every other number SCRIP publishes is SPITBOL's and this one was not. Cured in `sno_setexit_resume`
(`src/runtime/core/core.c`). Gate `test_gate_sno_goto_with_no_preceding_error.sh`, 16 arms, both modes, wired
into `make test`; negative-tested before wiring — **12 of 16 arms RED on the pre-cure tree, all 4 control arms
GREEN in both modes.**

**(b) `:(FRETURN)` at level zero jumped to a non-code site in mode 3.** `rt_outer_call`
(`src/runtime/rt/rt.c`) pushes the address of `rt_kw_return_level_zero` as the level-zero landing — **once**.
The mode-4 driver pushes it **twice** (`src/driver/scrip.c:1486`, `push rax; push rax`), because the convention
at that jump is the γ/ω wire pair: `[rsp+0]` is the success landing and `[rsp+8]` the failure landing. So
`:(RETURN)` and `:(NRETURN)` landed on the sentinel and raised `ERROR 242 -- function return from level zero`
exactly as `sbl` does, while `:(FRETURN)` popped whatever lay above it — **rc=139, rip in a non-executable
page, caller `0x0`** — and mode 4 was correct all along. ⭐ **This is the shape the row's GOAL named** ("an
unresolved RETURN label reaching a site that is not code", "hq_S's non-executable-page jump after FRETURN"):
the family was real even though the three programs it was pinned to were measured on a stale binary. Cured by
pushing the sentinel into both slots; the 8-byte alignment pad it replaces keeps `rsp` at the same offset, so
the only change is that a previously-garbage word now holds the sentinel. All three forms now answer
`ERROR 242` in **both** modes, matching `sbl -bf`, and the row
`snobol4-return-at-level-zero-crashes-instead-of-error-242` exits 0 on its own DONE-WHEN.

## 5. One crash left open, isolated to four lines

`:(RETURN)` reached **inside a live SETEXIT handler** at level zero still SIGSEGVs in **both** modes:

```
	SETEXIT(.f)
	&ERRLIMIT = 4
	X = 1 / 0
	OUTPUT = 'tail'	:(END)
f	OUTPUT = 'caught'	:(RETURN)
END
```

`:(END)` and `:(CONTINUE)` in the same handler are clean, and the same `:(RETURN)` outside a handler now raises
242, so the trigger is the handler path alone: `rt_goto_transfer` → `rt_chain_enter`
(`src/runtime/runtime_eval.c:68`) **jumps into the handler without leaving a return address** — unlike its
sibling `rt_chain_enter_v`, which pushes one. csnobol4 answers `Error 18 ... Return from level zero`.
Reproduced at `01eb996ca`, so it predates this sitting. ⛔ **Not landed here**: `rt_chain_enter` is a shared
trampoline reached by every mode-3 goto, so the fix is a shared-node change wanting hq_U's co-sign. Minted as
its own row.

## What this costs a reader who quotes the old line

⭐ The general shape, and it is the third time this project has paid for it: **a row's premise and a row's
work are separable, and a premise that evaporates does not make the row empty.** CEO-427 was wrong about the
three programs and right about the family; had the row been closed as "does not reproduce" when hq_B's
measurement landed, the FRETURN sentinel, the three collapsed goto diagnostics, the undefined-keyword silence
and the backwards exclusion would all still be in the tree — four findings behind one false premise.
