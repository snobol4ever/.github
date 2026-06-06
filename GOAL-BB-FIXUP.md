# GOAL-BB-FIXUP.md — The Continuous BB-Template Hygiene Sweep

**Carved:** 2026-06-04 (Lon directive)
**Repo:** SCRIP + .github
**Sister:** GOAL-SNOBOL4-BB.md (canonical TEMPLATE SPEC v2 text) · GOAL-ICON-BB.md · GOAL-PROLOG-BB.md · `SCRIP/BB-REVAMP-TRACKER.md` (the per-file work queue + violator snapshots)

## PURPOSE — N sessions generate; ONE session cleans

4–8 concurrent generator sessions produce new boxes and features and leave non-conforming template code behind. THIS goal is the ONE dedicated fixup session — **ATTENDED, opened by Lon for periodic runs** — that sweeps `src/emitter/BB_templates/` + `XA_templates/` to TEMPLATE SPEC v2 and the FACT RULES via a **ROUND-ROBIN CURSOR**: fix the file at the cursor, commit, push, advance, next. The cursor persists in the tracker, so every new session resumes exactly where the last one left off. Quality enforcement is its ONLY job. It adds no features, fixes no bugs beyond hygiene, and makes no semantic decisions — those get flagged for Lon.

## THE TARGET — what "clean" means (pointer list; canonical text lives in GOAL-SNOBOL4-BB.md)

**TEMPLATE SPEC v2** (canonical block: GOAL-SNOBOL4-BB.md "⛔ TEMPLATE SPEC v2"): no local variables · ONE return per PLATFORM returning ONE concatenated string · IF()/FOR() string functions · ONE source line == ONE asm line · REAL Greek α β γ ω · no MEDIUM_* at template top level · zero emit_fmt() · zero C comments · zero blank lines · **ONE-IR-ONE-LOGIC** (1 IR kind never carries N distinct four-port logics; split in LOWER) · **EMIT-BLIND / NO NEIGHBOR INQUIRY** (a template never dereferences a neighboring IR node to admit or choose an emission; LOWER decides, templates emit). REGENERATE whole, don't patch.

**FACT RULES the sweep also enforces** (canonical blocks in GOAL-*-BB.md; do NOT fork their text): `bb_bin_t` ABOLISHED (in-band records via `bb_emit_x86`) · ONE MEDIUM INVISIBLE (no `IF(MEDIUM_BINARY,…)` instruction pairs; encode via `x86()`) · NO C BYRD-BOX FUNCTIONS (`(ζ,int entry)` signature) · NO VALUE STACK · NO DUPLICATED LOGIC (DUP FORMS 1–4; value work = ONE `rt_*` call) · PER-BOX LOCAL STORAGE (RO `[rip+disp]` / RW `[ζ=r12+off]`) · X86-64 register convention (Σ=r13 δ=r14 Δ=r15 ζ=r12) · TEMPLATE-ONLY EMISSION · LANGUAGE-BLIND TEMPLATES.

## TWO TIERS — classify before touching

- **TIER H (hygiene — mechanical, behavior-neutral by construction):** locals→inline, return-shape, Greek ports, emit_fmt removal, comment/blank purge, MEDIUM-branch collapse into `x86()`, `bb_bin_t`→in-band records, register-convention conformance. No IR changes, no LOWER changes, no dispatch changes. The emitted asm should be IDENTICAL or gate-equivalent.
- **TIER S (structural — needs LOWER + dispatch work):** ONE-IR-ONE-LOGIC splits (new IR codes, new `emit_core.c` cases, new template files, LOWER arms) and EMIT-BLIND fixes that move neighbor-kind decisions into LOWER and operand values into `_.op_*`/ζ-slots. One IR-split per commit chain; `prove_lower2.sh` + full gates each rung. A TIER S fix that requires NAMING new IR kinds follows the existing pattern (`IR_ASSIGN_LIT_S` style); if the right split is ambiguous, FLAG in the tracker for Lon — never guess a semantic boundary.

## ⛔ FIXUP DISCIPLINE (the laws of the loop)

1. **BEHAVIOR-NEUTRAL ALWAYS.** Full gate battery green before AND after every file. TIER H additionally proves asm equivalence where the transform claims identity: `git stash`-baseline method — emit `--compile` output for the rung corpus before and after, `diff` must be empty (or differences explained by the sanctioned transform, e.g. label renames).
2. **ONE FILE PER COMMIT, STRAIGHT TO MAIN.** No branches — ever, for this goal. The unit of work is small enough that main + gates IS the safety. Commit message: `FIXUP <file>: <criteria cleared>`. A conflict then costs one file, not a batch.
3. **PULL BEFORE EVERY FILE, PUSH AFTER EVERY FILE.** `git pull --rebase` on SCRIP at the top of every cursor stop; push immediately after the green commit. The cursor advance travels IN the same commit as the file's tick (both live in the tracker).
4. **SKIP HOT FILES.** If `git log --since="6 hours ago" -- <file>` shows a non-fixup commit, a generator session owns it right now — advance the cursor past it (it gets caught next lap). Never fight a live session for a file.
5. **NEVER WIDEN SCOPE.** No feature work, no bug fixes beyond the hygiene transform, no "while I'm here." A discovered functional bug → tracker note + handoff doc, untouched.
6. **GATES ARE THE ONLY BRAKE.** No green → no commit. A file that cannot get green REVERTS its working tree, gets a tracker note at its entry, cursor advances.
7. **CONTEXT-BUDGET HANDOFF.** The session loops until Lon ends it OR its context window reaches ~70% consumed — then it finishes the current file, commits, pushes, updates the watermark, and stops cleanly. A senile session pushing to main is worse than a short one. (This law exists because a "continuous" session decays; the cursor makes short sessions free.)

## THE CURSOR (the resume mechanism)

`SCRIP/BB-REVAMP-TRACKER.md` carries one header line: `# CURSOR: <file>`. The file list in the tracker (alphabetical) is the ring. A session reads the cursor, works that file, and the cursor advance commits TOGETHER with the file's tick/note — one commit, one file, cursor moved. End of list wraps to the top: **laps**. Ticked files are NOT skipped on later laps — they get a cheap re-audit (the per-file checker), because generators keep dirtying the tree; clean → advance free, dirty → un-tick, re-fix, re-tick. The tracker is a living document; the cursor makes every session resumable from cold.

## THE LOOP (one cursor stop)

```
0. Session open (once): clone/pull SCRIP + .github; git config per RULES.md; Session Setup; baseline gates GREEN
   (else: tracker note "inherited red at <file>", stop and tell Lon).
1. git pull --rebase. Read # CURSOR from tracker.
2. HOT? (law 4) → advance cursor, commit "FIXUP cursor: skip <file> (hot)", GOTO 1.
3. Per-file audit (audit battery below) → clean? → advance cursor (tick stands), commit, GOTO 1.
4. Dirty → classify TIER H / TIER S.
   TIER H: REGENERATE whole to SPEC v2.
   TIER S, design pinned in LADDER: execute the rung (its own commit chain, prove_lower2 + full gates per rung).
   TIER S, design NOT pinned: do the TIER H portion only, leave [S] flag in tracker, advance.
5. Build + full gate battery + (TIER H) asm-equivalence diff.
6. Green → tick + annotate + ADVANCE CURSOR in tracker → commit (one file) → push.
   Red → revert tree, tracker note, advance cursor, commit, push.
7. Context < ~70% consumed AND Lon hasn't stopped the session? GOTO 1. Else: watermark, final push, stop.
```

## AUDIT BATTERY (the per-file checker + lap progress table)

Per-file grep counts (comments stripped) — the checker run at every cursor stop, and summed across the tree as the lap-progress metric:
`pBB->[αβγω]` (EMIT-BLIND) · neighbor `->t ==` via local aliases · `b.size(` · `x86_Lrec|x86_Jrec|x86_Drec|x86_b[123]\(|bytes\(|u8\(|u32le|u64le` · `IF(MEDIUM_BINARY|IF(MEDIUM_MACRO_DEF` · `emit_fmt\(` · `^\s*//` + prose block comments · blank lines · `PORT_ALPHA|PORT_BETA|PORT_GAMMA|PORT_OMEGA` · local variable declarations at template top level.
Plus the standing gates: `test_gate_no_bb_bin_t.sh` · `test_gate_template_medium_invisible.sh` · `test_gate_no_handencoded_bytes.sh` · `test_gate_sno_pat_reg.sh` · `util_template_purity_audit.sh` · `test_gate_no_vstack.sh`.
**FIX-0 authors `scripts/audit_bb_fixup_file.sh <file>`** (the per-file checker; rc=0 clean) and `scripts/audit_bb_fixup_rank.sh` (whole-tree table — the lap progress report, printed at session open and close), and `scripts/test_gate_bb_emit_blind.sh` (informational baseline → `--strict` zero at FIX-FENCE).

## OPERATION — ATTENDED SESSIONS ONLY (Lon 2026-06-04)

Lon opens a session when a periodic run is wanted; the cursor resumes it from cold. **NO branches** (one file straight to gated main, per law 2). **NO unattended/scheduled runs.**

**WHY ATTENDED — READ THIS, it is recorded so no session re-litigates it.** The track record is in the goal files: the `(ζ, int entry)` deletion was ordered THREE times over TWO months and sessions declined, re-introduced, or reverted it "to keep the build green"; the TWO-LITERAL-FORMS rule had to be RE-ISSUED after a session INVERTED it. Every one of those sessions had green gates throughout. Gates verify BEHAVIOR; they do not verify JUDGMENT — and the failure mode this goal exists to clean up is confident wrongness that passes every automated check. An unattended fixer is built from the same material as the generators; Lon watching is the only control with a working track record, catching the first wrong move at file #1 instead of file #40. (Claude Code "routines" — scheduled unattended cloud runs — exist and would mechanically fit the cursor model; they stay OFF the table until the attended runs have earned trust. Revisit only on Lon's word.)

**Session open protocol (what a fixup session does on "here we go"):** standard PLAN.md session start → open THIS goal file → run Session Setup → print `audit_bb_fixup_rank.sh` table → enter THE LOOP at the cursor. Stop when Lon says stop or law 7 fires.

## LADDER

- [x] **FIX-0** — Author `scripts/audit_bb_fixup_file.sh` (per-file checker, rc=0 clean) + `scripts/audit_bb_fixup_rank.sh` (lap progress table) + `scripts/test_gate_bb_emit_blind.sh` (baseline from tracker snapshot 2026-06-04). Add to Session Setup here. Gate: scripts run clean on current tree; counts match tracker snapshot. ✅ SCRIP d4e3a45 2026-06-06 — 91 files / 1984 total violations; emit-blind baseline: 132 direct pBB->[αβγω] + 95 alias-walk refs (227 total); matches tracker snapshot exactly.
- [ ] **FIX-1** — LAP 1: cursor round-robin from `# CURSOR` through the whole tracker ring, TIER H per file. The 2026-06-04 violator snapshot is the expected heavy stops (builtin family: is_cmp 28, atom_string 28, term_inspect 15, term_io 12, aggregate_nb 9, succ_plus 8, list 8, io 8, type_test 4, retract_throw 4 — their `pBB->α/β` reads are TIER S residue; clear TIER H now, mark `[S]`).
- [ ] **FIX-2** — `bb_assign_frame` + `bb_assign_frame_ref`: operand fusion (`pBB->α->ival/dval`) → `_.op_*` plumbing (driver prepares; template goes blind). TIER S, design pinned: execute when the cursor arrives.
- [ ] **FIX-3** — `bb_call` family (`bb_call`, `bb_call_proc_staged`, `bb_call_write_slot`, `bb_return`, `bb_every`): two-level neighbor classification (`lf->t`, `fin->α->t`) moves to LOWER. TIER S, design NOT pinned — flag on arrival; Lon pins the IR shapes first.
- [ ] **FIX-4** — `bb_gvar_assign` ONE-IR-ONE-LOGIC split: 6 arms → per-shape IR codes + templates. TIER S, design NOT pinned — flag on arrival until Lon names the kinds.
- [ ] **FIX-5** — `bb_match` split: HEAD/RETRY/ADVANCE → three IR codes, three templates. TIER S, design NOT pinned — flag on arrival.
- [ ] **FIX-6** — Audit residue: `bb_keyword` (4 arms — confirm near-identical-parameterized vs distinct), `bb_scan_stmt` (literal vs non-literal arms), then everything `audit_bb_fixup_rank.sh` still counts > 0.
- [ ] **FIX-LOOP** — Steady state: laps continue indefinitely; a lap that completes with zero dirty files is the green signal that generators' new code is being caught within one lap period.
- [ ] **FIX-FENCE** — All v2 gates `--strict` zero · `test_gate_bb_emit_blind.sh --strict` green · a full clean lap · this fence in every generator goal file's Session Setup.

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```

Lap status (run at open and close):
```bash
bash scripts/audit_bb_fixup_rank.sh
bash scripts/test_gate_bb_emit_blind.sh
```

Gates (every commit; the rung floors are the values at carve time — never regress them):
```bash
bash scripts/test_smoke_snobol4.sh                   # m2 7/7 HARD, m3 6/6, m4 6/6
bash scripts/test_snobol4_pat_rung_suite.sh          # M2>=18 M4>=17
bash scripts/prove_lower2.sh                         # PASS (mandatory for any TIER S rung)
bash scripts/util_template_purity_audit.sh           # clean
bash scripts/test_gate_no_bb_bin_t.sh                # 0
bash scripts/test_gate_template_medium_invisible.sh  # trend to 0
bash scripts/test_gate_no_handencoded_bytes.sh       # trend to 0
bash scripts/test_gate_sno_pat_reg.sh                # TIER1=0 HARD
bash scripts/test_gate_no_vstack.sh                  # g_vstack 0
```

## Watermark

**Carved 2026-06-04, REVISED same day to ATTENDED-CURSOR model (Opus 4.8 session, Lon directive: no branches, no unattended runs, round-robin cursor in tracker). FIX-0 COMPLETE 2026-06-06: audit scripts authored, SCRIP d4e3a45. LAP 1 STARTED 2026-06-06 (same session): cursor stop 1 = bb_alt.cpp TIER H (emit_fmt→inline, PORT_*→Greek literals, locals 6→3 via FOR(); [S] flag on operand-aux walk; asm-diff EMPTY) at ad8996b; cursor stop 2 = bb_arith.cpp REGENERATED full v2 CLEAN rc=0 (FIRST tick; one return/PLATFORM, Greek literals, zero locals; asm-diff EMPTY incl. arith.sno mode-4 which exercises it) at 56c4c54. Lap metric: 91 dirty/1984 violations → 90 dirty/1969. Emit-blind 227 (unchanged — all [S]). Session stopped cleanly at ~47% context per law 7 BEFORE opening the FIX-2 TIER S chain. `# CURSOR: bb_assign_frame.cpp` = FIX-2, design pinned. FIX-2 RECON (baked for cold resume): fusion reads at bb_assign_frame.cpp:38-39,45-46 (rhops = pBB->α->dval, frame idx = pBB->α->ival; sibling bb_assign_frame_ref identical); driver-prep precedent = emit_bb.c g_emit.op_* population sites (e.g. :372,:484,:974); rung = dispatcher computes rhops+rvoff into _.op_* fields pre-call, both templates go blind, prove_lower2 + full gates, one commit chain.**
