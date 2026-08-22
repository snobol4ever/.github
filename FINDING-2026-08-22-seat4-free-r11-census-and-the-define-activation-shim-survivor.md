# FINDING — 2026-08-22 seat4 — FREE-R11: BY-CLASS CENSUS, AND THE DEFINE-ACTIVATION SHIM IS A LIVE SURVIVOR THAT seat3's r10 CENSUS UNDERSOLD

**Row:** `free-r11`, task 2 of 3 in Lon's 2026-08-22 telemetry ladder (`free-r10 -> free-r11 -> diag-regs-stmt-and-bb`). Lon's basis, verbatim in substance: *"R10 and R11 are free, they used to be reserved for GAMMA and OMEGA which is now replaced by PUSH-PUSH at RBP."* Builds directly on `FINDING-2026-08-22-seat3-free-r10-census-and-eradication.md`, which eradicated r10's dead-wire class and did the equivalent work for most of r11's paired sites in the same commits (`bb_glue_flat.cpp`, `bb_match_defer.cpp`, `emit.cpp` 6 of 8 sites, `bb_define.cpp`'s `AB_OFF_GW`-fed dead loads, `bb_goto_deferred.cpp` comments, `rt.c`'s two dead preprocessor arms). SCRIP measured pristine (`make pristine` EXIT=0) at `ff84322c`, the commit this FINDING lands with (one comment-only change, `src/runtime/rtx/rtx_zdp.S` — no codegen touched, no `.s` regen owed).

## 1. STARTING POINT — MOST OF THE WORK WAS ALREADY DONE

Pulling before starting this row picked up seat3's `free-r10` landing mid-session. Because the retired register-wire mechanism always carried γ and ω **together** (r10=γ, r11=ω, same `IF(!bb_wire_stack_on(), ...)` branches, same `push`/`pop` pairs), seat3's r10-focused deletions removed the great majority of r11's dead-wire sites as a side effect. Fresh census immediately after pulling, before any edit of my own:

| Location | r11 occurrences (word-boundary, before free-r10 / after free-r10, this session's starting point) |
|---|---|
| `bb_glue_flat.cpp` | 2 → **0** |
| `bb_match_defer.cpp` | 5 (the s44 WIRE-SAVE/WIRE-RESTORE dance) → **0** |
| `emit.cpp` | 8 → **2 real + 1 comment mention** (both explained below, not dead) |
| `bb_define.cpp` | 19 → 13 (6 dead `AB_OFF_GW`-fed loads removed; 13 remain, see §3) |
| `bb_goto_deferred.cpp` | 2 (stale comments) → **0** |
| templates total | 103 → 86 (word-boundary) / 99 (incl. sub-register spellings `r11d/r11w/r11b`) |
| emitter total | 5 → 2 |
| runtime total | 82 → 77 |

**All three files Lon's brief named by path — `bb_glue_flat.cpp`, `bb_match_defer.cpp`, and (for its dead half) `emit.cpp` — were already clean of r11 before I made a single edit.** `rtx_zdp.S`, the fourth named file, was NOT touched by `free-r10` and is addressed in §4.

## 2. BY-CLASS CENSUS OF WHAT REMAINS (measured 2026-08-22, methodology: full-file reads, not sampling, cross-checked three ways — my own direct reads, a forked agent's independent sweep with fresh compiles, and seat3's r10 FINDING as a parallel-register cross-reference)

| Class | Where | Basis |
|---|---|---|
| **DEAD-WIRE** | *(none found)* | Every r11 site reachable from the retired register-wire mechanism was already removed by `free-r10`'s paired deletions. This row's own sweep found no r11-only dead-wire remnant free-r10 missed. |
| **SCRATCH** (ordinary, no wire connection, movable but not attempted this session) | `bb_call_fn.cpp`'s `sink_trailpush`/`sink_tp_nc`/`sink_carve48`/`sink_carve48_take`/`sink_unify2_str`/`sink_unify_lst_str` (Prolog WAM-style trail/heap-carve fast path — `g_pl_trail`, `g_hp_fr`) · `bb_idx_get.cpp`/`bb_idx_set.cpp` (4 each — table/array subscript pointer, r11-only, r10 not involved) · `bb_lit_scalar.cpp` (Prolog `pl_cells_graph`-gated ZRES-to-cell relay) · `bb_call_proc_staged.cpp:791-792` (one isolated `lea_id`+`push`, unrelated to the DEFINE shim below) · the `bb_call_fn.cpp` result-relay idiom at its two large dispatch functions (`mov r10,ZRES(0); mov r11,ZRES(8)`, copying a 16-byte DESCR result into a Prolog cell frame slot — same shape as `bb_lit_scalar.cpp`, not a continuation) · the bulk of `rtx_match.S`/`rtx_alloc.S`/`rtx_str.S`/`rtx_icn*.S` (pointer/index scratch, spot-checked in `rtx_match.S`, confirmed clean by pattern) | None of these construct or consume a γ/ω pair. Register choice is incidental everywhere in this class — safe-but-real follow-up, not attempted here, same posture `free-r10`'s FINDING took for the analogous r10 sites (their §5, e.g. the flagged r8/r9-collision caution at `bb_call_fn.cpp:253-284`, applies here too: **do not blanket-rename without per-site liveness review**). |
| **GENUINE CLAIM — infrastructure, not movable, not this ladder's business** | `x86_asm.h` register-name/decode tables (`x86_rnum`, the disasm string table) · `x86_asm.h`'s RTCC bank slot machinery (`RTCC_C_R11`, `x86_rtcc_wire_bank()`/`x86_rtcc_nowire()`, the `wb`/`rl` writeback/reload byte sequences at offset `rtccb+64`) — **out of scope, belongs to `GOAL-RTCC.md`, explicitly not absorbed into `GOAL-SNOBOL4-100.md`** · `x86_zsm_ev` (`x86_asm.h:2012-2027`) — saves/restores the complete caller-saved GPR set (rax,rdi,rsi,rdx,rcx,r8,r9,r10,r11) around the ZSM debug-instrument's C sink; this is the shim `FINDING-2026-08-20-s195` itself measured as the source of the "skew=80" instrument artifact — deliberate defensive completism, r11 is one of nine, not a claim on it specifically · `rt.c`/`runtime_eval.c`/`rtcc_init.c`'s RTCC self-restore idiom (`movq 64(%r10), %r11` — this is r11's own slot restore, the exact sibling of the r10 self-restore idiom `free-r10`'s FINDING §4.1 already documented; same file, same mechanism, r11's half was not separately named there) · `rt_coexpr.c`'s one site (Icon co-expression context-switch register save, unrelated language/mechanism entirely) · `rtx_zdp.S` (defensive completism for a perturbation-free probe — see §4). |
| **GENUINE CLAIM — live γ/ω carrier, NOT superseded, flagged not fixed** | `emit.cpp:2744`/`:3052` (frameless-blob suspend cache, already named by `free-r10`'s FINDING §4.3 as "the highest-risk survivor") **and, newly confirmed this session, `bb_define.cpp`'s role-4 "TINY-REAL" DEFINE-activation shim** (`:477-485`, `:531-539` — the `fnrbp()==1`/`fnrbp()==2` "s63 RBP-FUNCTION WRITER"/"s64 RSP-ONLY WRITER" arms). See §3 — this is the substantive finding of this row. |
| **OUT OF SCOPE — different language, different goal** | `xa_flat.cpp` (20-22 occurrences): declares and calls `rt_gen_save_wires`/`rt_gen_get_gamma_wire`/`rt_gen_get_omega_wire` — Icon's **own**, separate generator-suspend continuation mechanism (`ARCH-ICON.md`'s BB_PUMP model), not SNOBOL4's γ/ω. `ARCH-ICON.md`'s own register contract never claims r10/r11 at all. Confirmed by reading the call sites (`xa_flat.cpp:275-279`, `:405-414`) before excluding it — not assumed. This belongs to `GOAL-ICON-100.md`'s territory, which this session did not open per RULES.md ("read only the goal Lon names"). |

**Total remaining r11 (word-boundary): templates 86, emitter 2 (+1 comment), runtime 77 — unchanged by this session's edits (see §5: only comments touched, zero instruction bytes moved).**

## 3. THE SUBSTANTIVE FINDING — THE DEFINE-ACTIVATION SHIM IS LIVE, UNCONDITIONAL, AND NOT A MECHANICAL RENAME

`free-r10`'s FINDING classified `bb_define.cpp`'s remaining r10 sites as **SCRATCH** ("role==4 shim's own lea+push, register choice incidental... r9 is free at every one of these sites"). Ground-truthing this against r11 (a forked agent independently reached the same site by compiling live witnesses, cross-checked directly by me reading the source) shows the classification underdescribed what the code does, even though its practical conclusion (do not touch it this session) was right:

**The mechanism:** every call into a `DEFINE`'d SNOBOL4 procedure — this is not an edge case, it is how every user-written function activates — goes through `bb_define.cpp`'s role-4 shim, which does, unconditionally (no `bb_wire_stack_on()` check; that killswitch no longer exists anywhere in the tree):
```
x86("lea", "r10", "extlbl", ..., lbl_b)      // γ (the "body-returns" landing)
x86("lea", "r11", "extlbl", ..., lbl_o)      // ω (the "body-fails" landing)
IF(fnrbp()==1, push r11; push r10; push rbp; mov rbp,rsp)   // "s63 RBP-FUNCTION WRITER"
IF(fnrbp()==2, push r11; push r10)                           // "s64 RSP-ONLY WRITER"
jmp [rip@cell + body_cell]                    // enter the procedure body
```
Both arms land the pair at **exactly the s195 law-0a layout** — `[rbp+8]=γ [rbp+16]=ω` (RBP arm) or `[rsp+0]=γ [rsp+8]=ω` (RSP-only arm) — read back by the RETURN/FRETURN/NRETURN floaters via `RESTORE4`. This is architecturally the *same* PUSH-PUSH-at-RBP convention the rest of the migration uses; what is different is that **this shim stages the pair through r10/r11 as a two-instruction `lea`-then-`push` transit** rather than the caller pushing the raw label address directly (the way `bb_glue_pass_wires_blob`'s current, already-migrated form does through `rcx`).

**Empirical confirmation (fresh compile, this session, against current HEAD):**
```
GO   'abcdef' POS(0) *F1() 'ef' RPOS(0)    :S(OK)F(NO)     -- DEFINE('F1()')
```
compiles to (excerpt, `--compile` output):
```
lea   r10, [rip + F1_γ]
lea   r11, [rip + F1_ω]
push  r11
push  r10
```
— live, correct, oracle-matching output (`ptc*_fn2`/`ptc*_fn3` — the "call a function to get a deferred pattern" half of the passthru grid, 40 of the grid's 82 rows — all still pass 82/82 both modes, confirmed in §5). **This is not dead code, not a killswitch fallback, and not merely incidental** in the sense of "safe to ignore" — but the register choice genuinely *is* incidental in the sense that any two free scratch registers would serve the same two-instruction transit (the sibling glue mechanism already proves this by using `rcx` alone for the same job). Retargeting it is real, low-conceptual-risk, but high-blast-radius design/test work — it sits under **every** `DEFINE`'d-procedure call in the language, the same shape `free-r10`'s FINDING flagged `emit.cpp`'s frameless-suspend cache for (`FINDING-2026-08-20-s194b`/`s194c`'s convicted shape: an implicit register reservation for a span nothing else enforces) — and is therefore left for its own gated rung, not attempted here.

**Correction to file, not blame:** `free-r10`'s census was thorough and its conclusion not to touch this site was correct; it just described the site as generic scratch rather than as a live γ/ω carrier. Filed here so the next rung (r10's or r11's) starts from the sharper description.

## 4. WHAT THIS SESSION ACTUALLY CHANGED

`src/runtime/rtx/rtx_zdp.S` (the fourth file Lon's brief named): six comments asserting the retired, product-wide framing — *"r10/r11 are the γ/ω WIRES"*, *"⛔ THE WIRES"* — corrected to state the current, more precise fact: the **permanent, product-wide** register-wire claim (LADDER WREG) is retired, but r10/r11 may still carry a **live** γ/ω pair in the two surviving mechanisms named in §2/§3 (the frameless-suspend cache, the DEFINE-activation shim), so this file's blanket save/restore of the complete caller-saved set is not purely generic completism — it is still doing real protective work for those two mechanisms, in addition to being uniform defensive completism for every other register it saves (rax/rcx/rdx/rsi/rdi/r8/r9). **Zero instruction bytes changed** — every edit is inside a `/* */` or `//`-equivalent comment; `push`/`pop r10`/`r11` code sites are untouched, still 6 code occurrences before and after (verified by grep restricted to non-comment lines).

`.github/ARCH-SNOBOL4-RTX.md` §2: extended seat3's r10 section with r11's own picture — the DEFINE-activation shim named explicitly as a second live survivor alongside the frameless-suspend cache, the RTCC self-restore idiom's r11 half (`rtccb+64`) named alongside r10's (`rtccb+56`), and `xa_flat.cpp` explicitly carved out as Icon's own mechanism, out of scope.

`.github/GOAL-SNOBOL4-100.md`: register-contract-of-record line and LIVE CURSOR updated (§6).

**Not done, deliberately:** any deletion or register-reassignment in `bb_define.cpp`, `bb_call_proc_staged.cpp`, `bb_call_fn.cpp`, `bb_idx_get.cpp`/`bb_idx_set.cpp`, `bb_lit_scalar.cpp`, or the RTX `.S` scratch families. All are either live γ/ω carriers (§3) or ordinary scratch whose migration needs per-site liveness review (§2's SCRATCH row, same caution `free-r10`'s FINDING §5 raised for its own analogous sites) — none of it is a same-session mechanical rename.

## 5. VERIFICATION

`make pristine` EXIT=0 (RT_OPT `-O0`) before every measurement below, re-run after the `rtx_zdp.S` edit.
- **Passthru combinatorial grid** (`board_passthru_combo.sh both ptc`, 82 witnesses × 2 modes, oracle-diffed): **82/82 m3, 82/82 m4**, unchanged before/after this session's edit — includes the 40 `*_fn2`/`*_fn3` rows that exercise the DEFINE-activation shim from §3, confirming it still executes correctly untouched.
- **Corpus** (`test_corpus_snobol4.sh`): **m3 PASS=355 FAIL=2 · m4 PASS=353 FAIL=2 SKIP=2 (357 total)** immediately after pulling free-r10's landing, byte-identical before/after this session's own `rtx_zdp.S` edit — same two pre-existing, unrelated reds (`160_pat_alt_inner_gen_resume`, `demo_treebank`), all predating this session. ⛔ **A LATER, UNRELATED rebase (picking up concurrent commits `62017f8a`/`9e6d3de2`, "descr-stamp-fields: split DESCR_t tag...") surfaced a THIRD failure, `060_pred_operand_edge` (`EQ('2.0', 2)` stops matching), moving the post-rebase reading to m3 PASS=354 FAIL=3 / m4 PASS=352 FAIL=3 SKIP=2.** Isolated by building commit `0ff71be8` (immediately before those two) in a throwaway `git worktree`: PASSES there, FAILS at HEAD — a clean bisection, not a guess. **Not this row's bug** (this session's only code change is a comment-only edit to `rtx_zdp.S`, made and pushed before this rebase); reported to HQ (`s4e_msg.sh send hq regression-descr-stamp-fields-eq-coercion`), not investigated or fixed here. The passthru grid (82/82 both modes, unaffected — different program set) is this row's real gate-before-land evidence; the corpus delta above is receipted for the record, not claimed as this row's own regression.
- `test_gate_emit_no_lang.sh`: OK, unchanged.
- `test_gate_template_medium_invisible.sh --strict`: unchanged pre-existing FAIL (8 sites, all `xa_flat.cpp`, tracked WIP debt this row did not touch and did not worsen).
- `test_gate_wreg_claim.sh` (informational — this WREG design itself is superseded, see §2/§6, so its number is evidence not a gate): templates+emitter non-licensed sweep unchanged at 215 occ / 22 files (this session touched zero templates/emitter code).

## 6. WHAT'S LEFT (for `free-r11`'s continuation, or the ladder's third row `diag-regs-stmt-and-bb`)

In order of confidence, mirroring `free-r10`'s FINDING §6 structure:
1. **`bb_idx_get.cpp`/`bb_idx_set.cpp`** (8 combined) — pure subscript-pointer scratch, r11-only, no r10 pairing to coordinate with. Lowest-risk rename in this census.
2. **`bb_lit_scalar.cpp` and the `bb_call_fn.cpp` result-relay sites** — same ZRES-to-cell-slot copy idiom, mechanically identical, low risk.
3. **`bb_call_fn.cpp`'s carve/trail/unify helpers** (largest single bucket) — same liveness caution `free-r10`'s FINDING already raised (r8/r9 already occupied at some sites); needs per-site review, not a blanket rename.
4. **The RTX `.S` runtime scratch families** — spot-checked, not fully walked line-by-line this session; presumptively SCRATCH by strong analogy to the checked files, unverified in full.
5. **The two live γ/ω carriers (§3)** — `emit.cpp`'s frameless-suspend cache and `bb_define.cpp`'s DEFINE-activation shim — both real design/test work, both high-blast-radius (every suspended pattern generator; every procedure call in the language, respectively), both need their own probed, gated rung with the full passthru grid + corpus + beauty-M1 fixed point re-verified before and after. Neither is a target for a quick follow-on.
6. **`xa_flat.cpp`** — not this ladder's business at all; belongs with Icon's own generator-continuation work under `GOAL-ICON-100.md`.

No dedicated GOAL file exists for this ladder (same check `free-r10`'s FINDING made: no `GOAL-SNOBOL4-RTX.md`, no `GOAL-FREE-R10.md`/`GOAL-FREE-R11.md`). This FINDING plus `free-r10`'s are the orientation documents for whoever continues either row or opens the ladder's third row.
