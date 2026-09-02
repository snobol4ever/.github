# FINDING 2026-09-02 hq_P — BX-0 lands: `SCRIP_PL_TRACE=1` prints Byrd's four ports from the one hook, `=2` profiles them; r15 is a driver mmap address at every ω today, so `Exception` is withheld; the van Roy baseline pin is PARKED (Lon's wrap-up)

**Row:** ceo standup `prolog-instruments-and-baseline-standup` (ARCH-PROLOG-BYRD-BOX-TRANSLATION.md § D, § E rung 1). **Mode:** TRIO (MODE file). **Tree:** SCRIP `f4532dea` (rebased onto hq_B/hq_C's `8f1565da`; first verified as `839a3480` on `2748100d`, re-verified pristine after the rebase), corpus `tests/prolog/ALL.trace` added, `RT_OPT=-O0`, pristine (`make pristine` rc=0 at 17:50Z).
**Instrument:** `SCRIP/scripts/test_gate_pl_port_trace.sh` (graded population: the nine `probe_plz` origins of `corpus/tests/prolog/ALL.pl`, m3 and m4).

## 1. What landed

- **One arm in `x86_port_hook`** (`x86_asm.h`, `x86_pl_trace_ev`): Call at an α definition, Redo at a β definition (the pair-define sites now hand the hook their own label), Exit at a γ jump, Fail at an ω jump. `x86_jcc` to γ/ω routes through the existing invert-and-jump shape when the arm is on, so a **conditional exit traces only when taken** — no `pushfq`, no flag evaluation in the runtime. The arm reads `getenv("SCRIP_PL_TRACE")` at the point of use (no static cache: the 2026-09-01 ruling).
- **Runtime `src/runtime/rt/porttrace.cpp`:** prints `(N) D Port: box [-> target]` — N is Byrd's invocation number (assigned at Call, reused at Exit/Redo/Fail by a bracket stack keyed on `x86_uid`), D the bracket depth. `=2` counts α/β/γ/ω per box in the pre-existing `portcount.c` container, **widened from two ports to four** (`rt_port_counts_cell` = the ungated allocator, `rt_port_counts_report` = the four-column table with B/A and W/G ratios; the legacy `SCRIP_PORT_COUNTS` mode-3 path prints its two columns unchanged). `=3` both.
- **State lives on `g_emit`** (`pl_trace_*` fields; Lon 2026-09-02: `g_emit` fields were never under the no-globals rule) — `libscrip_rt.so` exports `g_emit`, so a mode-4 binary reaches it. **No new file-scope or function-scope static.**
- **Exit-time reporters carry `force_align_arg_pointer`.** Measured, not guessed: `SCRIP_PL_TRACE=2` SIGSEGV'd inside `__fprintf` on the `%.1f` of `rt_port_counts_report`, called from `__run_exit_handlers` ← `exit()` ← `icn_zf_exit_γ` (`scrip.c:98`) ← emitted code: the emitted program's `exit()` runs atexit handlers on the box's unaligned stack. The pre-existing `rt_port_counts_dump` had the same latent fault and got the same attribute.
- **Gate + refs:** per witness, (1) killswitch both ways on the `.s` (no env ≡ `=0`, ≠ `=1`), (2) stdout and rc identical with and without the trace in both modes, (3) the normalised trace equals its ref block (depth column dropped — the brief's clause; `n<k>_` node numbers stripped; `$2F` → `/`; the `r15=` field dropped), (4) answer vs `.ref` reported beside it. `--cut` regenerates `corpus/tests/prolog/ALL.trace` (18 blocks); a runaway witness is pinned as a **prefix plus its total line count**. Negative-tested: one altered ref line → `FAIL(1)`; a moved total → `FAIL(1)`; zero trace lines → `UNPROVEN(2)`.

## 2. Measured

| witness | trace lines (m3 = m4) | answer | note |
|---|---|---|---|
| p1_single_clause | 22 | ok | |
| p2_two_clause_first | 22 | ok | |
| p3_faildriven | 134 | ok | 6 Redo |
| p4_recursion | 162 | ok | |
| p5_inline_disj | 126 | ok | 4 Redo |
| p6_member | 62,888 | **RED** (pre-existing xfail `list_directive_1`: prints `1 2 _G0 _G0 …`) | ref = 400-line prefix + total |
| p7_cut_commit | 47 | ok | |
| p8_cut_bars_retry | 46 | ok | |
| p9_guard_then_cut | 96 | ok | 2 Redo |

- **Killswitch:** `fact2.pl` mode-4 `.s` md5 `000ecf54…` for the pristine `922cfaf4` build, for no env, and for `=0`; `aca60c45…` with `=1`. **Default-arm byte identity at scale:** the 23 `corpus/benchmarks/prolog/bench/*.s` artefacts hq_C regenerated on `2748100d` (corpus `a0cca818`) compile **23/23 byte-identical** on `839a3480` (the same arm, unchanged, on `f4532dea`).
- **⛔ r15 is NOT the ball yet.** Before the classification was withheld, every witness read `Fail=0 Exception=N` (p3 3, p4 3, p5 2, p8 2, p9 1): at **every ω of every witness r15 holds one mmap address inherited from the driver** (`0x708ae7866000` on one run, `0x7bf3043ee000` on the next — ASLR-random), never written by any Prolog path (hq_C's C10 census agrees: 0 r13/r14/r15 writes on Prolog paths; the only writers are Pascal's display arm in `xa_flat`/`bb_var_frame_ref`). So the ω line prints `Fail` and appends `r15=0x…` — the register's state is **visible, not classified**. C37 (r15 = BALL, zeroed at Prolog entry) flips the one line in `porttrace.cpp` and re-cuts the refs. hq_C: the boundary/entry must zero or save r15 before claiming it, or every ω reads as an exception.
- **Modes agree on the port sequence.** m3 numbers nodes per graph and names the top chain `pat_flat`; m4 numbers per program and names it `main` (`scrip.c:1751/1860` vs the proc name) — the normalised traces of all nine witnesses are identical between modes except the top-chain name, which is why the refs are per-mode blocks.
- **Profile sample** (`SCRIP_PL_TRACE=2`, `fact2.pl`): 34 boxes, 24 α-entered, α-total 52, β 4, γ 50, ω 2; `n3_call_prolog $unify` reads α 3 / γ 2 / ω 1 (W/G 0.500) — the clause-head miss the WAM tunes on.
- **The trace does not perturb answers:** stdout and rc identical with and without `SCRIP_PL_TRACE=1` on all nine, both modes (hq_C's PZ-4 (a) has the retained frame above rsp; the hook pushes 80 bytes at every port).

## 3. Verdicts on the pushed tree (pristine `-O0`, SCRIP `839a3480`)

- Prolog smoke `PASS=5 FAIL=0` in all three columns · Icon smoke m3 `14/14` m4 `14/14` (the shared-node control arm for an `x86_asm.h` change) · `test_gate_pl_port_trace.sh` `GATE PASS(0) … examined 18` · `strip_comments.py --check` 0 files · touched runtime files within 200 columns.
- SNOBOL4 blocking set (`make test`, pristine, after the rebase onto `8f1565da`): m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0 (pristine, SCRIP f4532dea, make test 18:09Z) — the trace gate and `strip_comments.py --check` 0 re-run green on `f4532dea`; the Prolog/Icon smokes above were taken on `839a3480`, the same arm before the rebase.

## 4. Parked (Lon 2026-09-02 13:xx: wrap up for the account switch) — cursor lines in GOAL-PROLOG-100.md and GOAL-HQ-PERFORM.md

1. **The van Roy two-number baseline pin — NOT MEASURED.** Nothing was run; no number exists. Next seat: `bash scripts/bench_triangulate_prolog.sh` then `bash scripts/bench_prolog_vanroy.sh --two-number` on a quiet box, `RT_OPT=-O0`, and pin the grid in GOAL-PROLOG-100.md as *after PZ-4 (a), before PZ-4 (b)-(f)* — the ceo named `922cfaf4`, but origin has since taken hq_C's `d42d2918` (runtime-image change) and this inert arm; confirm the pin commit with ceo before labelling. The rival-on-0-ticks refusal the brief asked for already exists (`bench_prolog_vanroy.sh:92`, `⛔ NO MULTIPLE: rival is under its 1 ms floor`). Pin beside it ceo's r9 datum: 244 dead `rtccb+48` reloads per `nrev.pl` compile at `2748100d` (hq_C rung 2.0 removes them).
2. **ceo's C9 witness** `catch((member(X,[1,2,3]), X>1, throw(t)), t, true)` — to be added to the trace refs (it must show no `Redo: member` after the exception); the gate's population is the `probe_plz` family, so the witness enters the master suite under that origin prefix and the refs are re-cut.
3. **Optbypass per-entry durations:** hq_C landed the names + wall clock at `2748100d`; my per-entry-duration draft was reverted unlanded (ceo: drop the row). If wanted, it is a `timed()` wrapper in `run_arm` returning `(kind, rc, dur)` and a sorted print in the violation block — small, but not proven on a census run, so not landed.
4. **`Exception` classification** waits on C37 (above).

## 5. What the instrument already shows (a reading, not a row)

The trace of `main :- fact(X,Y), write(X), write(Y), nl, fail.` reads exactly as Byrd would draw it: `(3) Call: call_proc_staged fact/2` → the clause's `$trail_mark`, two `var_ref`/`lit_string`/`$unify` triples, `suspend` → `(3) Exit` → the body's writes → `(3) Redo: call_proc_staged fact/2` → clause 2 → `(3) Exit` → `(3) Fail … -> main_γ`. The retained-box β re-entry (`Redo`) carries the Call's invocation number, which is the property C9 tests.
