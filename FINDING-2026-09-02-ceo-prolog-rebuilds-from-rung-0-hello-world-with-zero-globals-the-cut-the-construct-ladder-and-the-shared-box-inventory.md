# FINDING 2026-09-02 (ceo, TRIO, first session after the account switch) — Prolog rebuilds from rung 0: hello world with zero Prolog-only globals, the cut, the construct ladder, the shared box inventory, and ζ-STANDING is not a surrogate global

**Trees:** SCRIP `f4532dea` · corpus `a0b196b58` · .github `d36bc491` at the start of the session, pristine `-O0` build in `/home/claude/SCRIP`. **Clock:** box clock (`date`), 13:29–14:25 CDT. **Sovereign routing:** `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § B.0 (inventory) + § C ruling paragraph + § E (ladder) + § E.2 (retired rows mapped); `RULES.md` § THE PROLOG REBUILD GATE (the one law change of the session, six clauses); `ARCH-PROLOG-THREE-ZETAS.md` § 1 + § 6; `GOAL-PROLOG-100.md` LIVE CURSOR; `GOAL-CEO.md` CEO-149; postoffice `MODE` line 2, baton `prolog-rung-0-the-cut-and-hello-world-with-zero-globals`.

## Lon's six rulings, in-chat to ceo, verbatim in substance, in order

1. ~13:40 *"So do we not just begin at rung 0 and begin climbing the ladder for Prolog language constructs starting at simple and climbing to complex?"*
2. ~13:45 *"Do we not just delete ALL the globals on the list and start from scratch. I think so. How do you think? Justify."*
3. ~13:48 *"Have you laid out which BB's you will need for Prolog based on all the white papers you read and that are found in /home/resources folder."*
4. ~13:55 *"Are we not ready for a hello world Prolog program with zero globals and begin to rebuild?"*
5. ~14:05 *"Keep in mind to share BB's with Icon and SNOBOL4. No need to create a new BB that does exactly what one already does."*
6. ~14:20 *"We are the main architects here. Let ensure we use the THREE ZETA's, and do not mis-use the STANDING ZETA as a surrogate global for things program wide."*

## The ceo's answer: yes to all six, and why

**Construct ladder, not mechanism order.** § E as written this morning ordered the work by the mechanism rows inherited from `ARCH-PROLOG-THREE-ZETAS.md` § 6 (frame header → β resume → choice stacks → cut flag → unwind floor → catch → call/N). That order is the one that failed for five days: PZ-4 took twenty baton passes, three seats hit the same wall in one day (`FINDING-2026-08-27-seat07-…`, `-seat01-…`), the rung suite sat at 3/15, van Roy had 11 of 21 kernels flapping. § B was already written per construct with a Proebsting shape each; the ladder makes each rung one § B shape with its own witness and BX-0 trace ref, and the mechanism rows become consequences of the construct that first needs them.

**Delete all the globals in one cut, not a ratchet.** § C already sends every one of its 29 rows to "deleted" or a root cell; the ratchet was deleting them slowly while keeping both machines alive, and that coexistence IS the wall (old global trail beside a new frame log; old pending cursor beside `F.RES`). ZETA HAS NO MODES forbids the killswitch coexistence a ratchet needs. Precedent: `struct Term` went in one push on 2026-09-02 (490 word-refs → 0, board 351 → 348). The shallow board (348/371) measures the wrong thing (Lon's ruling of the morning: Prolog health is the deep rungs), so guarding it through incremental rungs guards a false number. `r12`–`r15` are callee-saved under the SysV ABI, so every C value service preserves the register quad for free and rung 2.0 shrinks from re-homing 339 `r12` lines to a gate on emitted code and `rtx_*.s`.

**What the cut removes, measured on `f4532dea`:**

| piece | measure |
|---|---|
| live Prolog-only globals (census 56, 9 dead already deleted at `d42d2918`) | 47 |
| `g_pl_trail` references | 281 in 6 files (`grep -rw g_pl_trail src`) |
| `by_name_dispatch.c` | 7,289 lines, 21 `plc_` statics (`grep -c '^static.*\bplc_'`) |
| `unification.c` | 2,256 lines (the control half goes, the value services stay) |
| `rt.c` CP/retry/zf3/pending machinery | `:1632-1727` |
| `lower_prolog.c` | 1,481 lines (the control lowering goes) |
| templates carrying Prolog arms | 12 of 136 (`grep -l -i 'pl_\|prolog' bb_*.cpp`) |
| dead templates with no lowerer | `bb_cell_ite.cpp`, `bb_cell_cut.cpp` (0 emitters of `IR_CELL_ITE`/`IR_CELL_CUT`) |
| `nm -D out/libscrip_rt.so` Prolog-only DATA exports | 26 |

**What stays (the boundary):** the parser (parser suite PASS 45), the DESCR cell layer, the atom table, `rtx_plunify.s`, the `dop_*` value bodies, the shared boxes, the BX-0 hook. Deleting past this line restarts the Term→DESCR work.

**Hello world today (the control arm for rung 0's DONE-WHEN).** `hello.pl` = `:- initialization(main). main :- write(hello_world), nl.` On `f4532dea`, pristine: m3 prints `hello_world` rc=0; `--compile` emits 187 lines whose `.s` references **0** Prolog-only globals (`grep -oE 'g_pl_|g_plw_|g_resolve_|g_rt_pl_|pl_wot_'`) but makes **3** `call rt_call_arr_bl` (by-name dispatch of `write`/`nl`) and **1** `call rt_plw_floor_bypass_on`; the BX-0 trace (`SCRIP_PL_TRACE=1`) prints `Call n0_lit_string … Exit n3_call_prolog $nl0 -> pat_flat_γ` — the two leaves, and `main` is NOT a box. Rung 0's DONE-WHEN therefore has both directions to fail: 0 by-name calls, 0 exported Prolog-only data symbols, `Call main … Exit main` in the trace, the frame rbp-relative.

**The inventory (ruling 3 + ruling 5), measured:** Prolog lowers to 18 IR kinds, 14 shared with Icon (`grep -oE 'IR_[A-Z_0-9]+' src/lower/lower_{prolog,icon}.c | sort -u | comm -12`); 4 Prolog-only (`IR_CALL_PROLOG IR_CUT IR_MOVE_LABEL IR_OP_COUNT`). Of the eleven box shapes Prolog needs, nine are boxes Icon or SNOBOL4 already own (`bb_call_proc_staged`, `bb_call`/`bb_call_fn`, `bb_conjunction`, `bb_disjunction`, `bb_cut`, `bb_bound` + `bb_indirect_goto`/`bb_move_label`, `bb_to`/`bb_call_builtin_gen`+`bb_suspend`/`bb_repalt`, `bb_iterate`/`bb_every`, `bb_call_value` + the runtime compiler); ONE new box (`bb_catch`) and ONE new arm (LCO on `bb_call_proc_staged`). `IR_CALL_PROLOG` collapses into `IR_CALL_PROC_STAGED`. Table: § B.0.

**ζ-STANDING (ruling 6).** My § C had sent the dynamic DB, `nb_setval` and the flags to "one root-frame slot" each — a table-of-everything slot is a global with a frame address. Re-disposed in the § C ruling paragraph: one named root cell per dynamic predicate (declared by `:- dynamic` or the `pl_dyn_mark` prepass, like a SNOBOL4 natural variable), one root cell per compile-time-constant `nb_setval` key (a computed key is compiled through the runtime compiler, which resolves the same cell), constant flags RO in the slab, `double_quotes` is parser-time state, the proc table RO. Engine state (trail, choice, cursor, ball, counters) never reaches the root.

## Law change (one per session): `RULES.md` § THE PROLOG REBUILD GATE

Six clauses: (1) the cut is one push, `nm -D` arm from then on; (2) the boundary; (3) shared boxes first, keyed on IR kind, graded on every frontend sharing the box; (4) the master board is REPORTED (348/371 both modes on `f4532dea` is the last pre-cut reading) and not a landing gate until rung 10 — the ladder runner + trace refs + `nm -D` are the Prolog gate; SNOBOL4 floor + Icon watermark hard on every push; (5) one seat per rung, from origin, instrument lane never on `src/`; (6) the three zetas, ζ-STANDING never a surrogate global. Fleet mailed (every seat inbox) and every root's `CLAUDE.md` digest given the pointer in the same session — the law is not routed until the fleet is mailed.

## Org state at the ruling

MODE `TRIO` (read from the file), the HQs live as `ListAgents` peers. On the ceo's instant pointer all three confirmed ZERO uncommitted `src/` changes and are holding until `rung-0-landed`: hq_B had CLAIMED rung 2.0 at 13:29 and measured only (reproduced hq_C's 339 `r12` lines / 168 `rtccb+48` reloads; two brief corrections kept at § E.2 — the corpus is a sibling root; in `xa_flat`'s PL-DC γ/ω shims `rcx` is live and `r8` is the dead temp); hq_C was running the computed `done` of `prolog-delete-g-zeta-mode-definition-zeta-has-no-modes` and the Term umbrella (postoffice only); hq_P was curing two van Roy harness defects in `scripts/` only (angles 1/2 never consult the rival preludes; the between/fail loop runs 2 of N iterations on m3/m4 and exits 0 — the between defect rung 7 names).

## Population and limits

Every number above is one measurement on one tree (`f4532dea`), pristine `-O0`, box clock; the census denominator is the 2026-09-02 ceo census FINDING; the IR-kind sharing count is a `grep` of two lowerers, not a run. No performance number is claimed. The audits owed this session (one closed rung per HQ) run in the background on the same tree and are recorded in CEO-149 when they complete.
