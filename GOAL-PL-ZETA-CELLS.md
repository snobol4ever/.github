# GOAL-PL-ZETA-CELLS.md — Prolog at 100% per-BB ζ CELLS on the RSP-topped FORTH stack

## ⚙️ CONCURRENT BY DEFAULT — AND THE REPOS MOVE UNDER YOU

**Many seats run this file's siblings at the same time. Edit any file, commit and push whenever a rung is buildable and green — mid-session, per rung. Never park work or decline an edit on concurrency grounds; stranding has cost this project far more than merging ever has.** Git merges; `git pull --rebase` and resolve normally.

**⛔ ASSUME ORIGIN MOVED SINCE YOU LAST LOOKED.** Another seat may have landed in your exact files while you were reading them.
- `git pull --rebase` before every push; **re-prove THIS file's gate/watermark after any rebase** — shared state moves under you and a watermark measured pre-rebase is void.
- `git log origin/main..HEAD` at orientation AND before handoff. **A clean `git status` is NOT a clean tree** — it hides local commits a peer seat left in a shared working copy.
- Place trees at canonical absolute paths (`/home/claude/{SCRIP,corpus,.github,x64}`) BEFORE running any gate: **many scripts grade a tree by absolute path.**
- Prefer **one clone per seat**; two seats in one working copy silently overwrite each other's uncommitted edits, and a global gitconfig scrambles attribution.
- Push **code repos before `.github`**, so no FINDING ever describes an unpushed tree.
- Push needs a credential — **ask Lon in chat and wait.** Never write push status into a doc.
- `bash scripts/handoff_status.sh` verbatim is the ONLY push truth. Not this file, not a commit message.

**Semantic collisions (two seats claiming one register) are caught MECHANICALLY by the claim gates, not by scheduling.** That is why no window is needed.

## ⛔⭐ LIVE CURSOR — s16 (2026-08-09, Claude Sonnet 4.6 — BUG-BETA LANDED `9313935`; bench-22 cells=1 == cells=0 green=11. NEXT RUNG = ZK-5B VAR_REF MATERIALIZATION per s14 protocol.)

**⭐ s16 WATERMARKS (HEAD `9313935`, -O0, TIMEOUT=6s, bench-22, re-proved post-rebase):** cells=0 **green=11 broken=11** · cells=1 **green=11 broken=11**. **FULL PARITY.** (s14's green=6 baseline improved to 11 via parallel sessions landing between `ada979eb` and `4a5f873`; BUG-BETA repaired the times10 regression that was the sole cells=1 deficit at `4a5f873`.)

**⭐ s16 WHAT LANDED (commit `9313935`, `bb_call_fn.cpp` line 552):**
BUG-BETA: `x86_beta_trampoline()` in the ZD arm of `bb_call_fn_str` incorrectly elided the β label define in BINARY mode (`--run`) for `CALL_BUILTIN_PROLOG` nodes on `pl_cells_graph`. Root cause: `flat_beta_used_scan` computes `bused[]` against `nodes[]` built by the codegen BFS. In BINARY mode (`g_is_text=0`) the GVA RPO pass (`if (!g_is_text || entry == g_emit_cfg->entry)`) adds group-anchor nodes to `nodes[]`, shifting indices so the β-tagged predecessor arc from node 2 (write/nl CBP) maps to a different `bused[]` slot than in TEXT mode → `bused[3]=0` → `op_beta_dead=1` → trampoline elided → forward ref to `n3_call_builtin_prolog_β` unresolved → `bb_emit_end` abort (rc=134). TEXT mode (`--compile`) skips the RPO extension → `bused[3]=1` → clean. Symptom class: `( cond → write(ok) ; write(failed) ), nl` programs abort m3, pass m4.
Fix: when `pl_cells_graph=1`, bypass `op_beta_dead` — emit `x86_beta() + x86_jmp(X86P_OMEGA)` directly. Net bytes identical to trampoline with `op_beta_dead=0`. SN4/Icon: `pl_cells_graph=0` → `x86_beta_trampoline()` unchanged = byte-identical. Diagnosis confirmed pre-patch via `SCRIP_BETA_ELIDE_OFF=1` escape (bench-22 cells=1 green=11 with elide-off = same result as after fix). ONE AUTHORITY: `bb_call_fn.cpp:552`.

**⭐ s16 CONCURRENCY NOTE:** Parallel seat wrote `6a4eba9` with the identical fix (referenced in the s15 cursor written by that seat). Our `9313935` reached origin first via rebase onto `53a4f62`; `6a4eba9` will be a clean no-op duplicate when that seat rebases. Per concurrency protocol: noted here, not silently dominated.

**⭐ s16 SESSION ANALYSIS:** BUG-BETA root cause was isolated through `SCRIP_BETA_ELIDE_OFF=1` escape → TEXT/BINARY split mechanism → GVA RPO pass as index-shift source. Fix: one-line additive change with byte-identical proof. All gates held, no broken commits, no push-pending banners, no help from Lon required.

**⭐ s16 ZK-5B NEXT SESSION:** (1) `git status --short` every repo — refuse dirty tree. (2) Re-derive both bench-22 boards at new HEAD. (3) **Build discriminating witness FIRST** — a program red on cells=1 today, green under correct VAR_REF materialization (`app/3` and `two.pl` do NOT discriminate — s14 CORRECTION OF RECORD). (4) Re-apply `.github/WIP-2026-08-09-PL-ZK-5B-option-A-FALSIFIED.patch`; 2-way sync-step monitor first; test `[nargs, nparams)` bound repair (s14 ROOT-CAUSE HYPOTHESIS). (5) Killswitch must cover RUNTIME site (`rt.c`) not just emitter — s14 KILLSWITCH-COMPLETENESS DEFECT rule. (6) Lon's A-vs-B ruling for VAR_REF materialization unchanged: Option A (pre-allocate TERM_VAR in `rt_jmp_frame_lexprep2`) vs Option B (template arm calling `rt_pl_fresh_var_ref()`).

## ⛔⭐ LIVE CURSOR — s14 (2026-08-09, Claude Opus — ZK-5B OPTION A **AS IMPLEMENTED IS FALSIFIED**: green 6→0. SCRIP TREE CLEAN AT `ada979eb`, ZERO CODE LANDED. NEXT RUNG = ZK-5B, restart from the patch.)

**⭐ s14 WATERMARKS (HEAD `ada979eb`, -O0, TIMEOUT=6s, bench-22 `test_bench_prolog_modes.sh`):** cells=0 **green=6 broken=16** · cells=1 **green=6 broken=16**. **PARITY HOLDS — s13's claim reproduces exactly.** s13's noted `qsort/m4` cells=1 regression (green=5) NO LONGER REPRODUCES; a parallel seat repaired it between `069c2fd8` and `ada979eb`. Re-derive again at open — this number moved under s13 without s13 touching it.

**⛔ s14 SESSION-OPEN LAND MINE — THE CONTAINER'S SCRIP TREE WAS DIRTY AND SELF-LABELLED `s14`:** `/home/claude/SCRIP` pre-existed at `ada979eb` with three uncommitted modified files (`emit.cpp`, `rt/rt.c`, `bb_var_ref.cpp`) implementing Option A, with comments already reading `PL-ZK-5B OPTION A (s14)`. **s14 did not write them.** They were measured, not adopted. Preserved verbatim at `.github/WIP-2026-08-09-PL-ZK-5B-option-A-FALSIFIED.patch`. **ADD TO SESSION OPEN: `git status --short` on every repo BEFORE the first build; a dirty tree at open is an unattributed artifact.** (Prior precedent: the s217 "I twice read a working tree as origin" finding.)

**⭐ s14 THE FALSIFICATION (four boards, one HEAD):** clean cells=0 **6** · clean cells=1 **6** · +patch cells=1 **0** · +patch cells=1 `SCRIP_ZD_PL_VR=0` **5**. The patch costs the entire board with VAR_REF admitted, and **still costs one program with the documented killswitch thrown.**

**⛔ s14 KILLSWITCH-COMPLETENESS DEFECT (rule-shaped, affects every future rung):** `SCRIP_ZD_PL_VR=0` gates VAR_REF **admission** in `zd_wl_kind` — emitter-side only. Option A's third edit lives in `rt_jmp_frame_lexprep2` (`rt.c`) and fires **unconditionally on every Prolog lex frame**, killswitch or not. The RUNGS-preamble obligation *"each: own commit, killswitch, `=0` byte-identity"* is therefore **unsatisfiable as written** for this rung — there is no `=0` position from which the runtime half disappears. **RULE: a rung with both an emitter arm and a runtime arm must read the killswitch at the RUNTIME site too, or both sites consult one env var. Otherwise every `=0` byte-identity proof for that rung is vacuous.**

**⭐ s14 CORRECTION OF RECORD — s13's ACCEPTANCE WITNESS DOES NOT DISCRIMINATE:** s13 NEXT-SESSION step (4) says *"Verify `app([a,b],[c],R)→[a,b,c]` … with VR enabled."* Measured: **`app/3` already prints `[a,b,c]` on the cells arm at clean HEAD with VR disabled**, and is the FIRST casualty when the patch lands (empty output). It is a **regression detector, not an acceptance witness.** `two.pl` two-clause dispatch prints `pos` on all four configurations and discriminates nothing either. ⛔ **ZK-5B HAS NO WITNESS THAT IS RED-WITHOUT AND GREEN-WITH. Build one before the next attempt** — otherwise the next session again cannot distinguish progress from parity, which is how s10/s11/s12 each burned a session.

**⭐ s14 ROOT-CAUSE HYPOTHESIS (NOT PROVEN — no monitor, no gdb; do NOT act on it as a diagnosis):** the rt.c loop promotes a param slot when `_s->v == DT_SNUL`. `descr.h` pins `DT_SNUL == 0` and states *"Zeroed memory is a valid null string"* — so that test **cannot separate "never bound" from "legitimately zero."** The loop also spans `[0, nparams)`, not `[nargs, nparams)`, so slots `rt_frame_bind_args` just filled are clobbered into fresh unbound vars — the shape that yields `app/3` → empty. **If it holds, the repair is the BOUND, not the tag:** seed only `[nargs, nparams)`, and never read `DT_SNUL` as an "unset" sentinel anywhere. Per RULES MONITOR-FIRST, point the 2-way sync-step monitor here first and let it name the divergence.

**⭐ s14 NEXT SESSION PROTOCOL:** (1) `git status --short` every repo; refuse to adopt a dirty tree. (2) Re-derive both boards at the new HEAD. (3) **Build the discriminating witness FIRST** — a program that is red on cells=1 today and would go green under correct VAR_REF materialization. (4) Re-apply `.github/WIP-2026-08-09-PL-ZK-5B-option-A-FALSIFIED.patch`; monitor-first to the divergence; test the `[nargs, nparams)` bound repair. (5) Move the killswitch read into `rt.c` so `=0` byte-identity is provable. (6) Lon's A-vs-B ruling is **unchanged** by this result — this session falsified an *implementation*, not the design.

**⭐ s14 LANDED: NOTHING.** SCRIP tree returned to clean `ada979eb`; no commit. Publishing a green→0 board as a rung landing violates RULES ("No broken commits"). `.github` carries the patch + the FINDING + this cursor.

## ⭐⭐ WHAT THE PRIOR SCANS ALREADY FOUND (s162–s164 + FINDING-2026-08-01-PL §11 — the machinery this ladder EXTENDS, never re-derives)
1. **The unlock set is FIVE kinds and it is ALL-OR-NOTHING PER RUN** (s163, measured): `IR_CALL_BUILTIN_PROLOG` gates **185/185 runs** · `IR_MOVE_LABEL` 157 · `IR_VAR_REF` 130 · `IR_VAR` 93 · `IR_CALL_PROC_STAGED` 91. Single-kind admission unlocks ZERO runs; 2-kind best (CBP+MOVE_LABEL) = 29/185; all five = 185/185. **No sequence that omits CBP unlocks anything.**
2. ⛔ **THE SINK-BYPASS DEFECT IS THE REAL BLOCKER** (s163, structural + sized): the ZD arm in `bb_call_fn_str` early-returns BEFORE `dop_direct_fp` and the PL-SINK ladder — an armed call emits generic `rt_call_arr` by-name dispatch, discarding SINK-1/2/4/8 (~97% of the data plane: 65 `rt_pl_dop_*` vs 2 `rt_call_arr` sites in nrev.s). Silently-green perf regression class. **DESIGN CORRECTION OF RECORD: ZD IS A STORAGE DISCIPLINE, NOT A DISPATCH ROUTE** — sink/dop selection stays; only operand SOURCE (ZOPQ vs FRQ) and result DEST (ZRES vs FRQ) move. ZD-PL-A (dop_direct_fp inside the ZD arm) LANDED s163b; slice 2a ($trail_mark, 30% of main traffic, needs the `esi==0` runtime read first) and 2b ($unify, addressing parameterization) are SPECIFIED NOT LANDED.
3. ⭐ **PROC-ENTRY IS THE ONE ITEM THAT IS NOT "ARM ANOTHER KIND"** (FINDING-08-01 §11): 781 frame refs (17.3%) with NO BB to own them — the entry protocol itself (wire header, saved rcx/rdx/rbp). Per-BB self-allocation needs an explicit design answer here: a FUNCTION-class frame per SN4 MECH's frame census, or wire cells at fixed spine offsets. **CROSS-REQUEST TO `GOAL-SN4-ZETA-MECH.md` — this is a MECH-shaped decision; never land a new frame/glue protocol from this file.**
4. ⚠ **The `IR_VAR` "RETIRED AS VACUOUS — DO NOT WIDEN" ruling was made for SN4 GLOBALS** and needs re-examination for Prolog (Prolog vars ARE graph locals) — a reasoned re-open with Lon visibility, never a blind widen (s163 NEXT(d)).
5. **Storage-weight vs run-gating are DIFFERENT ORDERINGS and a ladder needs both** (FINDING-08-01 §11): `move_label` gates 157 runs on 5 refs; `lit_string`/`lit_integer` own 438 refs and gate nothing.
6. **Instruments that exist:** `SCRIP_ZD_CENSUS` per-graph census (ZK-0 pattern, falsify both directions before believing any zero) · `SCRIP_ZD_GAP` callee= reporting · LD_PRELOAD PLT interposition for dynamic hotness (s148, `perf`/`gdb` absent in container) · the deterministic-instrument gap (s164: wall time DISQUALIFIED on Prolog until one exists — every perf claim on this ladder inherits that gate).

## RUNGS (each: own commit, killswitch, `=0` byte-identity, SN4+ICN+PL-zframe-arm invariance, FINDING per land mine)
- [x] DONE — PL-ZK-0 FLAG + CENSUS (a5597f65)
- [x] DONE — PL-ZK-1 ADMISSION ROUTING (a2386c3f)
- [x] DONE — PL-ZK-2 LEAF SPINE + SINK PRESERVATION (a7c80b4b)
- [x] DONE — PL-ZK-3 PROC-ENTRY DESIGN (d32f4dd2)
- [x] DONE — PL-ZK-4 CHOICE POINTS + TRAIL (fc2f21ec)
- [ ] **PL-ZK-5 SUSPEND CLASS.** Predicate/generator graphs (the 70.3%): pending-cells vs pthread decided by measurement, the ICN-ZK suspension-decision shape.
- [ ] **PL-ZK-6 RATCHET.** bench 22/22 m3+m4 on the cells arm · rung 164/164 both modes · smoke 5/5 · sink census ≥ legacy arm.
- [ ] **PL-ZK-7 GATES + DOCS.** Cells-arm gate script; A/B table vs the zframe arm (the two-backends precedent) for Lon's default ruling; cursor sync.

## COORDINATION
This file NEVER lands a new frame/glue/claim protocol — MECH owns structure (cross-request in both cursors). Shared chokes (`zd_wl_kind`/`zd_k`/`zd_nops` one-authority lines, staging choke, `bb_call_fn.cpp` dfp chain) take ADDITIVE arms only. `git pull --rebase` before every commit; re-derive every count at session start; line numbers drift daily — re-grep, never trust. Perf claims blocked on the deterministic instrument (item 6). `.github` pushes last.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

## DRAFT RULING R-PL-ZK-A (walker default, s0b; Lon overrides at any session start)
ZK-0's naming decision defaults to: ADD a separate `pl_cells_graph` field at IR_graph_t struct END (s141 ABI law) — cheapest, zero Icon coupling, no rename churn. A shared behavior-named `cells_graph` consolidation becomes a later hygiene rung once both language arms are proven. This unblocks ZK-0 without waiting on the ruling.
