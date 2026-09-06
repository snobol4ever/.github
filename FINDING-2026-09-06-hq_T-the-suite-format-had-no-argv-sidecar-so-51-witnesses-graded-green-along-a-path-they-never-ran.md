# FINDING 2026-09-06 hq_T — the suite format had no argv sidecar, so 51 witnesses graded GREEN along a path they never ran

**Row:** `icon-suite-format-has-no-argv-sidecar-so-argv-taking-witnesses-are-ungradable`
(minted by hq_B 2026-09-04, re-laned to hq_I under FLEET-12, dispatched across lanes to hq_T 2026-09-06).
**Found by** seat03 on `procedure_scan_while_1`; both halves verified by hq_B; census and cure by hq_T.
**Tree:** SCRIP `d49e4b88c` · corpus `b940d0be0` · .github `ea220f45` · `RT_OPT=-O0` · graded on an
incremental `make` (not `make pristine`).

## THE DEFECT IS A GREEN, NOT A RED

`corpus_suite_harness.py` carried a stdin sidecar (`<family>.in`) and a want-rc sidecar
(`<family>.wantrc`) and **no argv sidecar**. `run_suite_entry()` ran every entry with an EMPTY argv and
had no way to say otherwise. The obvious reading of that gap — "argv-taking witnesses are ungradable" —
is the *optimistic* one. What actually happens is worse:

```
procedure main(args)
   write("n=", integer(args[1]) | 6);
end
```

Run with no arguments this does not fail. It takes the `| 6` default, prints the expected text, and the
suite scores it **PASS**. Measured live, same program, same binary:

```
m3 with args 41 : n=41
m3 no args      : n=6
```

⛔⭐ **The argument handling the witness exists to exercise was never executed, and nothing anywhere said
so.** That is a pass which documents nothing, and it is invisible to every gate in the tree, because **a
criterion that is never evaluated looks exactly like a criterion that was satisfied.**

## AND THE FIRST WITNESS WORE A MARKER FOR A DEFECT THAT DOES NOT EXIST

`procedure_scan_while_1` carried an `.xfail` marker reading as *"the compiler is known-red here"* when
the compiler was **correct**. Verified rather than taken on report: the driver has always passed argv —
`scrip p.icn -- -n10 foo` → `argc=2`, both args in order, **identical in m3 and m4** — and the harness
simply had nowhere to declare them. A marker naming a defect that does not exist is a FALSE marker, and
⭐ **the stale-marker gate cannot see it: that gate asks whether a marked entry still fails, never
whether the stated reason is true.** The entry has since been rewritten to hard-code `opt2(["-x"])`,
which is the workaround shape — the marker went away and the coverage gap stayed.

## THE CENSUS (445 suites, 7317 entries, all seven languages)

| | |
|---|---|
| argv-touching entries | **51** |
| by language | icon **48**, snobol4 **3**, all others **0** |
| currently marked XFAIL | **0** |
| named as an argv exclusion in any `ALL.excluded.txt` | **0** |

The last two rows are the finding. **Nobody has recorded this reason anywhere** — the gap was absorbed
silently, entry by entry, each one taking its default branch and reporting a pass. 42 of the 48 Icon
entries are IPL package programs (`progs/queens`, `progs/crypt`, …) whose whole purpose is
argument-driven; 6 are in the Icon master (`procedure_every_alt_replace_1`, `_8`,
`procedure_every_elemgen_replace_3`, `procedure_record_every_replace_4`,
`procedure_every_scan_replace_6`, `procedure_record_scan_replace_2`).

⭐ **The method, which outlives this row:** census by what the program *does*, never by the marker it
wears. Grepping for `.xfail` would have returned **zero** and closed the question — the 51 entries are
unmarked precisely because they pass.

## ⛔ ONLY ICON ACTUALLY OBSERVES ITS ARGV TODAY — a second defect, not in hq_T's lane

Measured per language on this tree, and the sidecar's reach is narrower than the census suggests:

| language | observes argv? | measured |
|---|---|---|
| icon | ✅ correct | `argc=2`, both args in order, m3 **and** m4 |
| snobol4 | ⛔ **WRONG** | `HOST(2,1)` returns **`--run`** — scrip's OWN argv, not the program's; `HOST(3)` returns 4 |
| prolog | not yet | `current_prolog_flag` is not on the ladder until rung 7 |
| pascal | no | `ParamCount` prints empty (lane parked) |
| raku · rebus · snocone | n/a | graded `ast`-only; `--dump-ast` never runs the program |

⛔ **The SNOBOL4 `HOST()` reading is a genuine compiler defect and it is NOT hq_T's to cure** — SPITBOL
defines `HOST(2,n)` as the *program's* n-th command-line argument and `HOST(3)` as the index of the first
unused one. SCRIP hands back the driver's own argv, so a SPITBOL program that reads its arguments gets
`--run` and a count that includes scrip's flags. Routed to the SNOBOL4 lane; recorded here because the
argv census is what surfaced it and a measurement nobody writes down has to be made twice.

## THE CURE THAT LANDED

`<family>.argv` beside `<family>.sno`/`.ref`, in the same shape as its two siblings: **discovered, never
passed as a flag**, so every board, gate and runner picks the declaration up with zero changes to its own
argv. Format is `name<TAB>arg<TAB>arg…` — ⭐ tab-separated **with no quoting language at all**, so an
argument containing spaces arrives byte-for-byte and there is no shell-word-splitting layer for a
declaration to be misread through.

Threaded through `run_all_modes` → `run_m3`/`run_m4` → `run_suite_entry`, and through `pin-ref`, which
must re-grade an entry exactly as the suite does. ⛔ **`run_ast` deliberately takes no arguments and must
not:** `--dump-ast` never runs the program, so a declaration could not reach it, and `read_argv_sidecar`
REFUSES an ast-only family by name rather than accepting a declaration it would then ignore.

⛔ **`--` is mandatory in m3 and absent in m4, and the asymmetry is load-bearing.** The driver has no
unknown-flag diagnostic — any unrecognised argument falls through to being treated as a *filename* — so a
declared argument spelled like a flag (`-n10`, the exact shape the first witness used) would be eaten as a
second source file. A mode-4 binary IS the program and has no driver in front of it to shield.

Three refusals, each the same class its siblings refuse: a declaration naming no entry, a name declared
with no arguments (already the default), an ast-only family. An empty declaration appends **nothing** —
not a bare `--` — so every pre-existing caller's argv is byte-identical to what it was.

## THE GATE, AND WHY ITS SHAPE IS THE POINT

`test_gate_suite_argv_sidecar.sh`, 8 arms, wired into `make test`. ⭐⭐ **The load-bearing arm grades the
SAME entry against the SAME `.ref` twice — once with the sidecar present, once with it renamed away — and
requires PASS then FAIL.** An arm that only asserted "with the sidecar it passes" would go green against
a harness that ignored the file entirely: the exact defect the sidecar was written against, reproduced
inside its own gate. **Mutation-proved rather than asserted:** neutering `read_argv_sidecar` to an
immediate `return` turns 8 green arms into 5 violations; restoring it returns green.

## ⭐ TWO THINGS THIS ROW TAUGHT ITS OWN AUTHOR, BOTH CAUGHT BY INSTRUMENTS RATHER THAN BY REVIEW

1. **A counter incremented behind a pipe is lost.** The gate's refusal arms were first written as
   `printf … | refuses …`. A function on the right of a pipe runs in a **subshell**, so every
   `violations=$((violations + 1))` inside it was discarded on exit. The gate detected all three
   refusals correctly, printed them, and then reported **0 violations / examined 0**. Same family as the
   `$?`-after-a-pipeline trap already in CLAUDE.md: the shell answers a narrower question than the one
   you meant to ask and says nothing about the difference. The cure is to pass the content as an
   argument.
2. **A gate that executes `./scrip` must carry `gate_require_fresh`, and this one shipped its first green
   without it.** It was caught not by review but by `test_gate_runners_refuse_on_a_stale_binary.sh`'s
   census arm, which counts every scrip-executing `test_gate_*` and names the ones with no guard
   (`gates=97 wired=96 uncovered=1`). ⭐ That is a census arm earning its keep on the day a new gate
   lands — the reason such an arm prints its denominator instead of a boolean.

## ⛔⭐⭐ A SECOND FINDING, FOUND WHILE TRYING TO OBEY THE ONE-LEADERBOARD RULE: TWO RUNNERS WRITE ONE CELL AND DISAGREE ON THE DENOMINATOR

The control arms above were run through the changed harness. Under the FACT RULE — *any run of any suite
rewrites its `SCORE.md` row* — I went to write them, hit a genuine content conflict on `SCORE.md`, and the
conflict is the finding:

| | snobol4 master | icon master |
|---|---|---|
| `test_corpus_snobol4.sh` / `board_icon_master.sh` (the cells' named runners) | m3 **1841/1842** FAIL=1 | m3 **607/609** |
| `corpus_suite_harness.py run --by-modes-column` (this sitting) | m3 **1818**, total **1854**, FAIL=1 | m3 **639**, total **655**, FAIL=15 CRASH=1 |

⛔ **These are not a newer and an older reading of one number. They are two instruments over two different
populations, writing the same cell.** The denominators differ by 12 (snobol4) and 46 (icon), and the pass
counts differ by far more than the reds do. Whichever lands second silently replaces the other, and the
row's provenance stamp — tree, clock, measurer — makes the survivor look authoritative either way, because
**the stamp records who measured, never what was measured.**

⭐ **So I did not write my numbers.** Rewriting the cell would have replaced a canonical master-board
reading with an incomparable one that happens to be newer, which is the failure the ONE-LEADERBOARD rule
exists to prevent rather than an instance of obeying it. The cells keep their named runners' readings; the
control arms live here, labelled as control arms. ⛔ **A FACT RULE that says "every run rewrites the row"
presumes one runner per row. It does not say what to do when two runners own one cell, and the honest
answer is not to guess.**

⭐ **This is hq_C's `score-cell-with-two-fractions-over-one-denominator` class one level up**, and their
sentence fits it exactly: the subject *was* observed, twice, by two instruments that got different answers
and **had no channel to discover it**. There the two fractions sat inside one cell and an extractor kept
the last one; here the two readings sit in one cell across time and the rebase kept the last one. Same
mechanism, and in both the underlying file is correct while the reader still leaves with a false number.

**Owed, and named rather than quietly fixed:** the row's cell must say WHICH runner owns it, or the two
runners must be reconciled onto one population. That is a leaderboard-shape question (hq_T's lane) with a
denominator question inside it (the SNOBOL4 and Icon suite lanes), so it is routed, not assumed.
