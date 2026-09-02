# FINDING 2026-09-01 (hq_B) — On the work basis the Raku grid tells a different story than the totals grid did, in both directions

**Row:** `bench-grids-rebase-to-two-number-basis` (Lon's basis ruling 2026-08-30, RULES.md § THE TWO-NUMBER BENCHMARK BASIS; ceo's
switch ruling 2026-09-01: "Raku triangulator + clock hook first"). **Mode during the session:** TRIO when it opened, **FLEET-8 then FLEET-16 declared while it ran** (read from the MODE file each time — three values in one session, exactly the worked example the seat digest carries; "file a row" became a real handoff mid-session, and the two rows below were minted the moment it did).
**Tree:** scripts half SCRIP `0da5a050` (park mark + gate, banner-side hook install, runner stderr + HARNESS injection, SCORE generator + splice) · runtime half <<<HASHES>>>

## THE CLAIM, measured

<<<GRID>>>

⭐ **NOTHING REGRESSED — both grids are real and measure different things**, exactly the shape of the Prolog inversion two days
ago (SCRIP `56fd19b5`). The totals grid (SCRIP README, 2026-08-30) reported string-escape at **55.9x**. Rakudo's process overhead is
~270–365 ms; the kernel does ~2 ms of work in Rakudo and ~80 µs in SCRIP. So ~99% of Rakudo's total was startup, and the multiple was a
startup story wearing an engine label. On the two `point_class_add` kernels the same constant worked the **other** way: it was padding
Rakudo's denominator, so the totals grid (0.41x, 0.14x) flattered SCRIP — on work alone SCRIP is further behind on object/method-heavy
code, not closer. The published qualitative split survives (loop/integer/string work ahead, object/method work behind); every number
under it moved.

⛔ **These are single-angle numbers and are labelled so everywhere they appear.** Angles 1 and 2 (fixed-time / fixed-iteration) have
no Raku instrument; the cross-proof column of every TSV row reads `UNPROVEN`, and `test_gate_bench_rivals_coverage.sh raku` still
refuses (total=17 measured=0). That refusal is **correct** and was left red on purpose: an `EXCLUDED.tsv` line saying "no instrument yet"
would turn the gate green for a language with zero triangulated kernels — the false-green shape with a reason attached.

## WHAT WAS BUILT (all of it re-runnable; nothing here is a hand-typed number)

1. **The Raku clock hook** — `wall_us()` / `wall_ms()` as SCRIP builtins (`src/runtime/by_name_dispatch.c`), placed **adjacent** to the
   Prolog `$wall_us`/`$wall_ms` so the two cannot drift apart: one law, two frontends. Arity differs on purpose (Prolog unifies an
   out-parameter, Raku returns a value) — each in its own idiom, same clock, same units. Verified in both modes against a 200k-iteration
   loop (m3 and m4 agree with Rakudo on the answer; work 1.1–1.9 ms vs Rakudo 26 ms on that probe).
2. **`note(...)`** — Raku's say-to-stderr, which SCRIP simply did not have (`Undefined function or operation`). It is what lets a kernel
   report its work delta **without touching stdout**, so every `.ref` still verifies unchanged. ⛔ **Guarded by `rt_proc_is_registered`**
   because the dispatcher is a shared node with **no entry guard**, and `note` is a name real programs already use — measured before
   adding it: three Icon programs (`packages/icon/{arizona,jcon}_tests/…/args.icn`, `tests/icon/rung36_jcon_args.icn` — since converted into `rung36_all` entry 40, corpus `b6767fb2`, the
   same sitting) and `tests/snobol4/ALL.sno`, which is on the blocking board. All four byte-verified in both modes after the change. ⚠️ The listop form
   `note "x";` (no parens) still does not parse — a grammar gap, left open and stated, not half-cured.
3. **`corpus/benchmarks/raku/prelude_rakudo.rakumod`** — the Rakudo arm's `wall_us`/`wall_ms`, loaded with `-M` so the kernel source is
   byte-identical on every engine (mirrors `prelude_swipl.pl`). ⛔ **Rakudo precompiles a `-M` module into `.precomp/` beside it, and the
   first hand run with `-I.` wrote `.precomp/` into the corpus** — the tmp1/tmp2 litter class ceo deleted the same day. The writer is
   the cure: the harness stages the prelude in a `mktemp` dir; the file's own header now says so, because its first draft literally
   instructed the reader to do the thing that litters.
4. **Four kernels self-timed** — `string-escape`, `send-more-money-loops`, `point_class_add1`, `point_class_add` — the same
   `BENCH kernel=… work_us=… work_ms=…` stderr line as the Prolog kernels, bracket around the work only. Each byte-matches its `.ref`
   on **m3, m4 and Rakudo**, every rep. The other 13 are declared by name on every triangulator run, never silently absent.
5. **`scripts/bench_triangulate_raku.sh`** — modelled on the Prolog one (extend, not rebuild). Implements angle 3 (bench_rusage elapsed +
   self-timed work → overhead) with these refusals and invariants: rc=2 on any missing instrument; a cell contributes only if **every**
   rep's stdout is byte-equal to `.ref` (hq_P's precondition, `.github 682367fd`); `exit=` from the rusage line is the only crash signal;
   `work_us > elapsed_us` → VOID-CLOCK; `|work_us/1000 − work_ms| > 1` → VOID-UNITS; a partial success (some reps DIFF) is a bad cell,
   because best-of over a set containing an unverified run would be choosing the run whose answer was not checked. Output:
   `corpus/benchmarks/raku/worktime-<stamp>.tsv` (13 columns, cross-proof column always `UNPROVEN` until angles 1+2 exist).
6. **The README grid is rendered from the TSV**, not typed (RULES.md § TRANSCRIPTION IS WHERE PROVENANCE DIES): the multiple is
   `rakudo work_us / SCRIP work_us` via the same `reference/ours` formula `lib_perf_fmt.sh` implements, the overhead line is the TSV's
   own column, and the label names arm, basis, reps, spread and machine load.

## SIDE FINDINGS — each measured, two cured, the rest recorded with numbers

- ⛔ **A refusal that blamed the wrong construct, cured in both modes.** `my $t = now;` (no map, no grep, no box) was rejected with
  *"a box has no MEDIUM_BINARY arm — Raku map/grep"*. The text was **hardcoded** at both `[SMX]` sites in `src/driver/scrip.c`; the real
  cause was the `IR_VAR` check in `graph_native_emittable_mode` (`now` is read and never assigned — Raku's clock term is not a SCRIP
  builtin). The function now writes the reason into a caller buffer and both sites print it:
  `…does not yet cover this program: variable 'now' is read but never assigned and is not a parameter.` A refusal naming the wrong cause
  costs more than no message; the reader goes looking for map/grep.
- ⛔⛔ **RETRACTED THE SAME NIGHT — "sentinel tombstones" was WRONG, and the deletion regressed two programs before the smoke caught it.**
  The first version of this bullet said `IR_OP_COUNT` (the IR op enum's COUNT sentinel) "is assigned to no node anywhere in `src/`" and called
  the driver's 30 comparisons against it dead. The census asked *is it assigned with `=`* (zero hits) and I read *does any node ever carry it*.
  It does: `lower_raku.c:82 rk_excise()` and `lower_prolog.c:461/773/877` **build** nodes with op `IR_OP_COUNT` — the excised/placeholder node,
  which the IR dump prints as `UNKNOWN` and which `bb_assign_local`, `bb_unop_gvar_slot`, `bb_binop_gvar_arith_slot` and `emit.cpp:1117` all test
  for. The six guards I deleted from `graph_native_emittable_mode` were what made the driver **refuse** such programs with a clean `[SMX]`
  banner (the Raku smoke's PASS-or-REFUSED bar accepts that — and the A/B on pristine HEAD `3a1807bd` without my change shows exactly that:
  both programs `[SMX]`-REFUSED, both modes); without them `reverse(@a)` reached `emit_drive` and died — *"IR op=133 has no
  template"*, SIGABRT, both modes: `array_reverse` and `str_reverse` went from REFUSED to core dump, 724/724 → 722/724. Caught by
  `test_smoke_raku.sh` on the merged-tree chain; ONE named guard restored (the old line 459 refused any such node unconditionally and shadowed
  the rest, so one guard reproduces the original semantics exactly and now says *why*); pristine re-run before anything is pushed.
  ⭐ **THE REAL BEAUTY DEFECT** survives the retraction: the COUNT sentinel doubles as a live op, so any reader who knows what a sentinel is will
  call those guards dead — I did, with the file open. Row `driver-emittability-predicates-sentinel-tombstones` is re-scoped to *name the excised
  node* (`IR_EXCISED`) so the guards read as guards; the 21 remaining comparisons are then simply renamed, not "swept". Two instruments answered
  narrower questions in one bullet — the census grep, and my own eyes on a function I had already rewritten once that hour.
- ✅ **The Icon rung ladder reads 261/9/27 at HEAD `8eac17da`, and that is pre-existing, not the `note` change.** hq_C's number
  (262/7/1/27) was from a different HEAD. Same tree with and without my change, built in separate worktrees with separate objdirs:
  identical PASS/FAIL/XFAIL and the identical 8 FAIL names (`rung36_jcon_{cxprimes,genqueen,level,prefix,proto,recogn,scan,var}`).
  Zero delta. The A/B is the answer; a remembered watermark from another tree is not.
- ⚠️ **The machine is not quiet and will not be.** Fleet seat processes and hq_P's own SNOBOL4 board ran throughout; 1-min load
  <<<LOAD>>> on 16 cores when the published REPS=5 run started (read from `/proc/loadavg` by the chain, not typed). Best-of-N under contention is the right estimator (the minimum is the least-contended rep) and the spread
  column is the honest error bar. Numbers are published with both stated rather than withheld — withholding would leave the 55.9x
  totals grid standing, which is the worse falsehood.
- ⚠️ **Three instruments answered a narrower question than I read them as answering** (RULES.md fifteenth instrument batch, landed
  this same day — the form below is the one it prescribes: the instrument's question beside its answer, then the wider question):
  `ls -a | grep precomp` said *nothing named precomp in the CURRENT directory* — I read *the corpus is clean*; the cwd had drifted and
  the litter was untouched. `cut -c1-200` said *these are the first 200 columns* — I read *this is the function*; the assert that
  expected 6 sentinel hits met 9 and refused to write (the lines were in fact ≤184 chars — the count, not the cut, was my error, but
  the refusal is what saved it). `grep -c 'HERE='` → 0 said *no such assignment in this file* and there I asked the wider question
  on purpose — it is why the undefined-variable installer never shipped. Each catch was an assert or a falsification, never a reading.
  And a fourth, the most literal: a cleanup loop that killed by *pattern* matched my own shell — whose command line contained the
  pattern as text inside the `case` that was looking for it — and sent it `KILL`; the first loop had only been saved by a 70-column
  `cut`. ceo's relay of hq_P's box-wide `pkill -f` had named "pgrep -f self-matching" one hour earlier. The rule I now follow: a kill
  names a PID whose `/proc/<pid>/cwd` and *exact* argv[0..1] were checked, never a pattern — and a loop that kills must exclude `$$`.
- ⚠️ **For every seat running a verdict chain through the Claude Code harness: a background Bash task is killed at the 10-minute
  `timeout` cap (exit 144) even though the tool describes it as detached.** Two pristine+board+gates chains died this way tonight at
  ~600 s each, mid-board, under fleet load; nothing on the box sent a signal. The instrument's question was *did this task exit within
  its timeout* — read as *is my chain running*. Cure: write the chain to a script, launch it with `setsid nohup … &` from a foreground
  call that returns at once, and watch its own log (a poll that also fires when the process is gone without a done line). The same
  cap explains an rc=124/144 board that "hung" for a seat whose box was merely busy.

## THREE INSTRUMENT DEFECTS REPORTED TO THIS SEAT MID-SESSION, ALL CURED (FLEET-16 mail)

- **`park` never wrote `.last-row`** (seat07): the Stop banner fell back to the marker left by the last `unclaim`/`done`, so a
  session that ended by parking was attributed to a days-old row with a cumulative commit count. `park` now calls
  `s4e_mark_row <topic> PARKED`; the class (a cure that enumerates its closing verbs reopens with every new verb) is written at
  the call site, and the durable shape — one `s4e_close_claim` writer — is named there for the next verb's author.
  ceo minted it rank 0 the same evening (seat14 hit it too, ladder I rung I7) with the cure shape *mark only on the own-claim branch*
  — which is where the call sits — plus a gate: `test_gate_s4e_release_verbs_mark_last_row.sh` runs claim/unclaim/done/park against a
  **scratch postoffice** (`S4E_POST`/`S4E_SEAT`), proves unclaim → RELEASED, done → DONE, park-own → PARKED, park-of-another-seat's
  claim leaves the marker and the claim alone, and goes red on a copy of the dispatcher with park's mark deleted (fail-once). `done`'s own
  refusal of a no-op `DONE-WHEN` (`true`) caught my first fixture — the guard is right, the fixture now tests a real path.
- **The commit-msg hook self-install never fired on any fleet seat** (seat04): it rode `s4e_inbox_hook.sh` on `UserPromptSubmit`,
  and a census of every root's `.claude/settings.json` found **16 of 19 wire only `Stop`** — all sixteen fleet seats. The row's
  "rejected in every clone" was true in the three HQ roots and silently false in sixteen. The installer now also runs from
  `banner` (Stop is the one event every root has), same quiet guard; `test_gate_commit_msg_hook.sh` green after the change.
- **ceo's hook-reach note** (the ceo root had no hooks at all until `make hooks`): same class, same cure — the banner path covers a
  root with no `UserPromptSubmit` and a root with no inbox hook alike.
- **A clone that is behind cannot receive a fix delivered by being current** (seat11): a SCRIP clone 74 commits behind had no
  installer script to run, so "installs itself at your next prompt" was a pull-gated action described as automatic. The banner path
  does not change that — it runs the clone's *own* `install_commit_msg_hook.sh`. The honest wording for any future all-hands, in
  seat11's words: *no action needed IF your clone is current; if `make hooks` reports no such target, you are behind — pull, then
  re-run.* And a behind clone lacking `8846246a` reproduces the cured FENCE SIGSEGV as a false hard-gate regression — PULL-BEFORE-TRUST.
- ⛔ **My own first draft of the banner installer referenced `$HERE`, which this script never defines** — it would have tested
  `-x /install_commit_msg_hook.sh`, false forever, silently: the exact class the block is curing, one paragraph below the census that
  motivated it. Caught by the verify line (`grep -c 'HERE='` → 0) before the commit. The path now derives from `BASH_SOURCE`, and the
  claim was **falsified the right way**: delete a repo's hook, run `banner`, watch it come back.

## NEXT (in order; each unblocks the next)

1. **Angles 1+2 for Raku** need a loop-driven derived twin per kernel (the kernels are top-level scripts, not callable subs) plus a
   `bench_raku_fixed_iter.sh` — the prolog `vanroy/` + `bench_prolog_fixed_iter.sh` pair is the model. Minted as
   **`raku-bench-angles-1-and-2-fixed-iter-instrument`** (rank 2, brief written). Until it lands every cell stays `UNPROVEN` and the
   coverage gate stays red for raku, correctly.
2. **Self-time the remaining 13** (`grep -L 'wall_us()' corpus/benchmarks/raku/*.raku`) — each joins the grid only when it byte-matches
   `.ref` on all three arms with the bracket in.
3. **Icon triangulator** is in this row's scope (ceo 2026-08-30) and is untouched this session.
4. **Prolog angles 1+2** stay blocked on the 8-line witness; pz4 is now `BLOCKED-ON:calling-convention-depth-tracked` (the row that
   carries host RBP promotion — `park` refused the mechanism name as a blocker, by a guard this seat minted with pz4 as its example).

## PROVENANCE
```
bash scripts/bench_triangulate_raku.sh                         # REPS=5 PERF_COLOR=0 for the published table
bash scripts/test_corpus_snobol4.sh                            # pristine, both trees (runtime-only; runtime+driver)
bash scripts/test_smoke_icon.sh; bash scripts/test_icon_x64_all_rungs.sh   # Icon control arms, A/B in a worktree
git show HEAD:src/driver/scrip.c | grep -o '[!=]= IR_OP_COUNT' | sort | uniq -c
```
