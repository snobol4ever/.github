# FINDING 2026-09-02 hq_P — the van Roy loop wrapper runs its body EXACTLY TWICE for every N on SCRIP (m3 and m4, rc=0); both angle harnesses divided N by that and printed SCRIP at ~6,400x gprolog, agreeing with each other; and neither angle ever consulted the rival preludes, so the ten self-timed kernels read UNPROVEN for gnu AND swi

**Row:** ceo standup `prolog-instruments-and-baseline-standup` (the van Roy two-number baseline pin; ceo CEO-148 ruled the pin commit `f4532dea`, then parked the pin until rung 8 at 13:40–13:50 on Lon's rung-0 restart ruling — relayed in-session, brief pending). **Mode:** TRIO (MODE file). **Tree:** SCRIP `f4532dea` (pristine `make pristine` rc=0 at 18:34Z, `RT_OPT=-O0`), corpus `a0b196b58`, `.github` `d36bc491`. **Box:** three pristine builds (ceo, hq_C, this seat) ran 18:30–18:34Z; measurements below were taken at load 2.0–2.9 on 16 cores with hq_C's `make test` and this seat's `make test` overlapping — stated because it moved in nobody's favour on a correctness count and would have on a rate.

## 1. What I set out to do, and what stopped it

The brief was to take the two-number baseline (`bench_triangulate_prolog.sh` then `bench_prolog_vanroy.sh --two-number`, 21 kernels, three angles) and pin it. My previous session had recorded one null without chasing it: `bench_triangulate_prolog.sh` with `KERNELS="fib nrev queens_8"` returned **12 UNPROVEN cells in 6 s**, gnu and swi included. That null is two instrument defects, both in hq_P's lane, both cured here before any number was taken. **No baseline number is quoted in this FINDING and none is pinned** — the pin is parked by ceo, and the instrument that would have taken it was fabricating its SCRIP column.

## 2. Defect A — angle 1 and angle 2 never load the rival preludes (an instrument fault printed as a kernel finding)

Ten of the 21 kernels (`cal derive deriv divide10 fib log10 ops8 sendmore tak times10`) are self-timed on the two-number basis and call `wall_us/1` + `wall_ms/1` — SCRIP builtins, undefined on gprolog/swipl unless `prelude_gplc.pl` / `prelude_swipl.pl` is consulted first. `bench_prolog_vanroy.sh --two-number` consults them; `test_bench_prolog_timed.sh` (angle 1) and `bench_prolog_fixed_iter.sh` (angle 2) did not — zero occurrences of `prelude` in either.

Controls, `fib.pl`, run by hand:
```
gprolog --consult-file bench/fib.pl --query-goal halt          -> warning: ... existence_error(procedure,wall_us/1)   (no answer)
swipl -q -g halt bench/fib.pl                                   -> ERROR: main/0: Unknown procedure: wall_us/1          (no answer)
gprolog --consult-file prelude_gplc.pl --consult-file bench/fib.pl --query-goal halt -> 10946 ; stderr BENCH kernel=fib work_us=2000 work_ms=2
swipl -q -g halt prelude_swipl.pl bench/fib.pl                  -> 10946 ; stderr BENCH kernel=fib work_us=2178 work_ms=3
```
Angle 1's single-shot correctness gate requires gnu, swi AND m3 to match `.expected`, so every bracketed kernel read `SKIP correctness-fail(single-shot)` on ALL FOUR engines and the TSV published `UNPROVEN` for the rivals too. **The instrument's question was "does the rival print the answer without its clock"; it was read as "does the rival agree".** (RULES.md fifteenth batch — a correct instrument answering a narrower question never says so.)

## 3. Defect B — the failure-driven loop runs its body exactly twice on SCRIP, for every N, and exits 0

Both angle harnesses time `main :- l__(N). l__(N) :- between(1,N,_), bench__main, fail. l__(_).` and gate the reading on `bench_rusage`'s `exit=` field only. Measured on the pristine `f4532dea` tree (`./scrip --run <wrapper> | wc -l`; swipl with its prelude for the control):

| N | m3 answers printed | m4 answers printed | swipl | gprolog | rc (m3, m4) |
|---|---|---|---|---|---|
| 1 | **2** | — | 1 | — | 0 |
| 3 | **2** | — | 3 | — | 0 |
| 64 (`vanroy/fib.pl`) | **2** | **2** | 64 | 64 | 0 |
| 65536 (`vanroy/nrev.pl`) | **0** | — | 65536 (angle 2) | 65536 (angle 2) | 0 |

At N=3 the two m3 answers each carry their own fresh bracket (`work_us=6267` then `work_us=6272`), so the body genuinely executes twice — the first pass, then ONE β re-entry that re-runs it, then the loop ends. It is an over-count at N=1 and an under-count at every N>1; the count is a property of the redesign's β path, not of N. `nrev` prints nothing at all and still exits 0.

**Consequence in the harnesses, with the prelude defect cured and the loop defect not yet:** angle 1 `fib` read `m3 3,102,442.7 iter/s · m4 4,314,417.4 iter/s` beside `gnu 485.6 · swi 344.9`; angle 2 `fib` (N=64) read `m3 3,129.6 · m4 4,075.9`, `nrev` (N=65536) `m3 4,985,242.7 · m4 18,219,627.5`, all marked `ok`. The doubling search never reached its 500 ms budget because the program stopped after two iterations, so it capped at N=65536 and divided by two iterations' CPU. ⛔ **Angle 1 and angle 2 then AGREE on the fabrication to within 1% (3.10M vs 3.13M), because they share the defect** — the cross-proof was about to certify a 6,400x multiple as MEASURED. This is the "engines agreed at reps=0" witness of RULES.md THE INSTRUMENT LAWS §2, arriving through a loop that does not loop.

⛔ **Consequence in hq_C's acceptance gate (`test_gate_vanroy_prolog_acceptance.sh`, CLEAN = rc 0 and no refusal text):** `fib` is CLEAN having printed 2 of 64 answers; `nrev` is CLEAN having printed 0 of 65536. The pinned `CLEAN_FLOOR=3` counts programs that do not run. A value counted is not a value graded (eighth batch §3). Routed to hq_C in § 8 — their instrument, their lane; the cure below is reusable by it in one line.

## 4. The cure — one library, two harnesses, both directions proven

**Landed: SCRIP `4253dd88`** (scripts only: `lib_prolog_bench.sh` new, `test_bench_prolog_timed.sh`, `bench_prolog_fixed_iter.sh`, `bench_triangulate_prolog.sh`, `test_gate_pl_quad_regs.sh` new; rebased onto hq_B's `6faa3215`, self-test re-proven after the rebase, pushed).

`SCRIP/scripts/lib_prolog_bench.sh` (new): `gnu_filter` (the one banner filter, previously inlined in angle 1's correctness gate) and `loop_check <eng> <stdout> <N> <expected>` — stdout must equal N copies of the kernel's `.expected` byte-for-byte (gnu banner-filtered first); otherwise the cell reads `LOOP-OUTPUT-MISMATCH(lines=<seen>/<wanted>)` and never a rate; no N or no `.expected` is `UNGRADED`, also no rate. Applied to all four engines identically (NO PER-ENGINE FILTER). Both harnesses source it and REFUSE rc=2 if they cannot; both consult the preludes on every rival invocation and REFUSE rc=2 if the preludes are missing; angle 2 gained the bench dir it needed to find `.expected`.

Proofs, `KERNELS="fib nrev"`, same binary throughout (`git show HEAD:` for the old arms):

| arm | fib | nrev |
|---|---|---|
| angle 1 OLD | `SKIP correctness-fail(single-shot)` ×4 | SKIP ×4 |
| angle 1 prelude only | gnu 485.6 · swi 344.9 · **m3 3,102,442.7 · m4 4,314,417.4** ok | SKIP (m3 single-shot crash, correct) |
| angle 1 CURED | gnu 604.6 · swi 507.2 · m3 NA · m4 NA `m4@N=1:LOOP-OUTPUT-MISMATCH(lines=2/1)` | SKIP |
| angle 2 OLD | N=64 gnu 477.9 · swi 403.2 · **m3 3,129.6 · m4 4,075.9** ok | N=65536 gnu 172,874.9 · swi 64,248.1 · **m3 4,985,242.7 · m4 18,219,627.5** ok |
| angle 2 CURED | gnu 475.5 · swi 429.8 · m3 NA · m4 NA `m3:LOOP-OUTPUT-MISMATCH(lines=2/64)` | gnu 174,677.0 · swi 63,333.1 · NA · NA `m3:LOOP-OUTPUT-MISMATCH(lines=0/65536)` |
| refusal arms | `PROLOG_DIR=/nonexistent` → `⛔ REFUSED-TO-GRADE rival preludes missing` rc=2, both scripts; lib renamed → `⛔ REFUSED-TO-GRADE (rc=2): cannot source lib_prolog_bench.sh` | |

Rates in this table are scouting data taken under load and are not citable; the columns that matter are the words. The rival cells are unchanged in kind by the cure (they looped before, they loop now); the SCRIP cells changed from a number to a named observation.

## 5. Single-shot ground at `f4532dea` (the denominator angle 1 can ever measure)

`for k in vanroy/*: gnu(prelude) / swi(prelude) / m3 --run vs bench/<k>.expected`, single shot: **gnu 21/21 ok · swi 21/21 ok · m3 10/21 ok** — the ten self-timed kernels — and 11 not ok: `crypt ham meta_qsort mu nreverse nrev qsort zebra` dump core, `queens_8 queens query` fail `main/0` (`Warning: initialization goal failed`). That set is exactly EXCLUDED.tsv's crash class minus the ten that now run; the ten were declared there too (`cal derive divide10 log10 ops8 sendmore times10 tak`, 8 of 10) and the file's own header orders their removal the moment they carry an AGREE row — see § 7.

**r9 datum, re-measured on the pin tree, command named:** `./scrip --compile --target=x86 bench/<k>.pl | grep -c 'rtccb+48'` (SCRIP `f4532dea`, `-O0`) → `nrev` **225** reloads (562 `r12` lines, 10,664 lines), `nreverse` **168** (339 `r12` lines, 8,121 lines). ceo's 244 for `nrev` was taken on `2748100d` and is a different tree; hq_C's 168 for `nreverse` reproduces exactly. Rung 2.0's DONE-WHEN compares against THESE, on this tree.

## 6. Triangulation on the cured instrument
Two full runs, both on the `f4532dea` binary (the SCRIP commits since are `scripts/` only), corpus `a0b196b58`, load 1.2–2.0, hq_C's and ceo's boards idle.

**Run 1 (19:02–19:06Z, committed wrappers as they were):** `fib` and `sendmore` AGREE on both rivals; SCRIP m3/m4 UNPROVEN on all 21 (the loop check); the 11 non-runners UNPROVEN on every engine (angle 1's single-shot gate, correctly); and **8 self-timed kernels DISAGREE by 1.18x–2.75x** (`cal` 2.41/2.47, `log10` 2.29/2.75, `divide10` 1.66/2.32, `times10` 1.79/2.11, `ops8` 1.52/2.13, `deriv` 1.39/1.56, `derive` 1.18/1.52, `tak` 0.86/0.83). ⛔ **Defect D, the reason:** angle 2's committed `vanroy/<k>.pl` drivers were cut on 08-27 from the PRE-BRACKET kernel bodies, angle 1 wraps today's bracketed bodies — two clock reads and a `format` to stderr per iteration is a 2x tax on a microsecond kernel — so the two angles timed different programs and the cross-proof measured the bracket, not the adequacy of the budget. Cured in corpus `d0351a546`: 11 drivers refreshed from today's `bench/` bodies with their committed N untouched (fib 64, tak 16, sendmore 256, the rest 65536); verified a refreshed driver still prints N answers on swipl. The first run's TSV was deleted uncommitted.

**Run 2 (19:09–19:13Z, refreshed drivers; the committed TSV `triangulation-20260902T190902Z.tsv`, rc=1 because DISAGREE cells remain):**

| kernel | gnu (a2/a1) | swi (a2/a1) | bucket rule (both rivals) |
|---|---|---|---|
| cal | AGREE 0.9972x | AGREE 0.9271x | **MEASURED** |
| derive | AGREE 0.9874x | AGREE 1.0724x | **MEASURED** |
| divide10 | AGREE 0.9620x | AGREE 0.9480x | **MEASURED** |
| ops8 | AGREE 0.9329x | AGREE 0.9921x | **MEASURED** |
| deriv | AGREE 0.9890x | DISAGREE 0.8926x | not promoted |
| fib | DISAGREE 0.8887x | AGREE 1.0337x | not promoted |
| sendmore | AGREE 0.9626x | DISAGREE 1.1202x | not promoted |
| times10 | AGREE 1.0890x | DISAGREE 1.1500x | not promoted |
| log10 | DISAGREE 0.8526x | DISAGREE 0.8804x | declared: calibration |
| tak | DISAGREE 0.8963x | DISAGREE 0.8334x | declared: calibration (N=16, startup dominates angle 2) |
| the 11 non-runners | UNPROVEN | UNPROVEN | REFUSE (run) / DECLARED (rc 0) |

The 2x class is gone; what remains sits at 0.83–1.15x against a flat, UNBAKED 10 % tolerance (the triangulator's own header) — the instrument's adequacy check saying "budget or N", which is the question it exists to ask and is left open here (the pin is parked; calibration is rung 8's first job). `bench_prolog_vanroy.sh --measured-from` on the TSV: `MEASURED: cal derive divide10 ops8`. `--two-number` on it: `ROWS: 21 (MEASURED=4 DECLARED=5 REFUSE=12)`, rc=0 — **the bucket plumbing, quoted for its counts only; no multiple from that run is quoted anywhere, the pin is parked.**

**Defect E, found by running the coverage gate on the new state — `test_gate_bench_rivals_coverage.sh prolog` counted 23 kernels and had been RED since 2026-09-01.** It enumerated every `bench/*.pl` (23) while EXCLUDED.tsv, the two-number board and hq_B's ruling name the universe as the 21 `vanroy/` drivers; seat12 correctly removed `queensn` from EXCLUDED.tsv as "not one of the 21" and the gate went red for exactly that, joined by `witness_depth_nrev8`. Cured in SCRIP `48b09e04`: when a language keeps a driver dir its basenames are the universe, an orphan driver (no `bench/` source) REFUSES, bench/-only files print as INFO; the duplicate-basename check compares the raw list to its own unique count (it had compared universe to raw and false-refused "23 files, 21 unique" on the first cut of the fix). Before/after: `total=23 … missing=2 rc=2` → `total=21 measured=8 declared=13 covered=21 missing=0 rc=0`; negatives: a declared line removed → `missing=1 rc=2`, an orphan driver → rc=2, a real duplicate → refused; pascal unchanged 11/11. ⭐ **Two instruments, two rules, now written where both readers look (EXCLUDED.tsv's header):** the gate counts a kernel MEASURED on ANY AGREE row in ANY committed TSV (measured=8), the board promotes only on AGREE from EVERY rival in the LATEST TSV (MEASURED=4). A kernel can be covered by one and REFUSE in the other; that is the board saying "not excused", not a contradiction.

**EXCLUDED.tsv (corpus `d0351a546`):** every "segfault on single-shot" line for a self-timed kernel was FALSE at `f4532dea` — all ten answer correctly single-shot; four removed as MEASURED, two removed as false, `log10`/`tak` declared WITH their discharge condition (remove when both rivals AGREE), and the eleven non-runners carry the exact reading of § 5 measured without a pipe: `crypt mu nrev queens query` SIGSEGV rc=139 · `meta_qsort zebra` rc=134 (`pl_trail_unwind` guard) · `qsort` rc=1 ERROR 246 · `nreverse queens_8` rc=0 `main/0` failed · **`ham` rc=0 with a WRONG ANSWER** (28 bytes ≠ `.expected` — a wrong answer is hq_C's; noted in the routed message). A line names a reading and a date, never a permanent class: the acceptance gate shows 11 of 21 flip.

## 6a. Defect C, found by the re-run — a `timeout` the bounded process may decline is not a bound

The first full triangulation on the cured harness sat **648 s** on angle 2's `vanroy/queens.pl` under swipl with `timeout 60` in front of it: swipl runs at 99.8 % CPU through `timeout`'s SIGTERM (it handles the signal at its own safe points and never reached one), and the whole triangulation waited behind it. `bench_prolog_vanroy.sh`'s legacy path already used `timeout -k 5`; the two angle harnesses did not. Cured: every `timeout` in both harnesses carries `-k 5` (13 sites), so the deadline is unconditional and an overrun reads `CRASH(signal 9)` through the `exit=` gate, never a rate. The run was restarted from scratch on the patched scripts; § 6 is that run.

## 6b. The quad gate — minted, born red, proven both ways (ceo's rung-0 brief, instrument lane)

`scripts/test_gate_pl_quad_regs.sh` pins Lon's grants: `r12` TR · `r13` B · `r14` ROOT · `r15` BALL, **no write reachable from a Prolog graph outside the TR/B/ROOT/BALL helpers**. ARM 1 compiles every Prolog witness fresh (`ladder__` + `probe_plz` origins of `ALL.pl`, `benchmarks/prolog/bench/*.pl`, `demos/prolog/*.pl`; the committed `.s` artifacts are never read) and attributes every destination-write to `r12`–`r15` (Intel syntax; the `;`-packed lines and the label-on-the-instruction-line shape both handled; byte-safe over the Greek port labels) to its enclosing box label and `.L` local; legal iff either matches `QUAD_HELPER_RX`. ARM 2 sweeps the rtx functions reachable from those `.s` files (call/jmp targets that are `RTX_FUNC` names, closed transitively inside `src/runtime/rtx/`); a function with a balanced push/pop of the register is callee-saved-clean; unreached rtx functions are INFO, not graded. `QUAD_HELPER_RX` is the ONE allow-list — today it matches nothing because no helper exists, and hq_C names the helpers there in the rung that creates them.

Measured on `f4532dea` (`-O0`, 51 s):

```
ARM 1: witnesses = ladder 0 + probe_plz 9 + bench 23 + demos 3 -> compiled=35 noemit=0 quad-writes=5303 violations=5303
       by instruction: 4606 lea r12, · 417 mov r12, · 245 pop r12 · 35 xor r14d   (r13, r15: zero writes anywhere)
ARM 2: functions=47  reachable-from-the-witnesses=2  reachable quad-writes=0  violations=0  INFO unreached: rtx_match.s:rt_match_replace writes=3
GATE FAIL(1): 5303 quad-register writes outside the TR/B/ROOT/BALL helpers (examined 35 witnesses)
```
The 4606 `lea r12,[rip+g_pl_*]` are the by-name sinks' scratch (`g_pl_trail`, `g_pl_zf_pending_cursor`, `g_plw_cellws_on`), the 245 `pop r12` the `dcα` continuation pops (`pop r12; jmp r12`), the 35 `xor r14d` one per mode-4 `main` prologue — all of which the cut deletes or the rungs re-home; `r13`/`r15` are untouched today. Proofs: `QUAD_HELPER_RX='.'` on the same tree → `PASS(0)` over the same 5303 sites (it can say YES); `--self-test` → arm 1 flags 3 fixture writes (`lea r12`, a `pop r12` on a label line, `xchg rax,r13`) and accepts a helper-labelled `add r12`, arm 2 reaches a dirty function transitively through a clean one, accepts the clean one's balanced push/pop and leaves an unreached one ungraded (it can say NO and YES on both arms, independent of the tree); `QUAD_RTX_ALL=1` prints the full rtx census (3 writes, all in SNOBOL4's `rt_match_replace`, its C.A.S. cursor by design).

## 7. Acceptance gate reading on the pin tree (`bash scripts/test_gate_vanroy_prolog_acceptance.sh`, worst-of-3)
`CLEAN=3 (floor 3) · REFUSE=3 · CRASH=13 · other=2`, **11 of 21 flip between reps on the unchanged binary**, `GATE FAIL(1)`; REFUSE `deriv[R..]! sendmore[RRR] tak[RR.]!`; CRASH `cal[CCC] crypt[CCC] derive[RCC]! divide10[RRC]! ham[CRC]! log10[CCR]! meta_qsort[CRC]! mu[CCC] ops8[RCC]! queens[CRC]! query[CCC] times10[CCR]! zebra[CCC]`; other `nreverse[ooo] qsort[ooo]`. Taken 18:41–18:47Z at load 2.0–3.3 with `make test` overlapping. The three CLEAN are `fib nrev queens_8` — the first prints 2 of 64 answers and the second 0 of 65536 (§ 3), so the pinned floor of 3 is, on this reading, a floor of programs that exit 0 rather than programs that run. Note `cal` is CRASH here and correct single-shot (§ 5): its second entry is what dies, which is the loop shape of § 3 again from the other side.

## 8. Routed

- **hq_C** (`s4e_msg.sh send hq_C vanroy-clean-counts-two-of-n`): the acceptance gate's CLEAN admits a program that printed 2 of 64 answers (`fib`) and one that printed 0 of 65536 (`nrev`); the "exactly twice for every N, own bracket each time, rc 0" shape is a β-path datum for the rung ladder; `loop_check` in `lib_prolog_bench.sh` is the one-line cure if they want it.
- **ceo**: receipt with the `handoff_status.sh` verdict line, as asked. The pin stays parked per the 13:40–13:50 ruling; when it is taken, the two-number board reads the TSV of § 6.
- **ceo (rung-0 brief):** the quad gate is minted (§ 6b) and waits on origin with this FINDING; rung 6 starts from `f4532dea`'s 10/21 single-shot-correct kernels and the `_rkfn` count of § E's DONE-WHEN, once hq_C's rung 2 is on origin.
- **Also landed:** SCRIP `48b09e04` (coverage-gate universe, Defect E) · corpus `d0351a546` (drivers, TSV, EXCLUDED.tsv, Defect D).
- **Not touched:** `src/` (held per ceo's telegram), `bench_prolog_vanroy.sh`'s legacy per-iteration path (still bare `command -v`, still no preludes — it is the producer of the committed `vanroy/*.pl` wrappers, so regenerating them would move every angle-2 N; left as the row's own header asks, and named here so nobody reads its SKIPs on the self-timed kernels as kernel findings), hq_C's acceptance gate.

## 9. Verdicts on the pushed tree
- **Pin tree, pristine (`make pristine` rc=0 18:34Z), `make test` 18:35–18:46Z, rc=0:** `m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0` (master total=1726, xfail 70/70, xpass 0/0), the four trailing gates GATE OK. This session's SCRIP change is `scripts/` only (two harnesses + one new lib), so this is the tree's standing verdict re-verified, not a verdict on codegen.
- **Instrument proofs (§ 4):** angle 1 and angle 2 each fail on the old arm the way the defect predicts and measure on the cured arm; SCRIP cells read `LOOP-OUTPUT-MISMATCH(lines=2/1)`, `(lines=2/64)`, `(lines=0/65536)`; refusal arms rc=2 for a missing prelude and a missing lib; `bash -n` clean on all three scripts.
- **Triangulation at scale:** § 6, two runs; the committed TSV is the one `--two-number` reads; coverage gate 21/21 rc=0 on SCRIP `48b09e04` + corpus `d0351a546`.
- **`handoff_status.sh`:** verdict line carried in the receipt to ceo, as asked.
