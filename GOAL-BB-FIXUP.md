# GOAL-BB-FIXUP.md — The Continuous BB-Template Hygiene Sweep

**Carved:** 2026-06-04 (Lon directive)
**Repo:** SCRIP + .github
**Sister:** GOAL-SNOBOL4-BB.md (canonical TEMPLATE SPEC v2 text) · GOAL-ICON-BB.md · GOAL-PROLOG-BB.md · `SCRIP/BB-REVAMP-TRACKER.md` (the per-file work queue + violator snapshots)

## PURPOSE — N sessions generate; ONE session cleans

4–8 concurrent generator sessions produce new boxes and features and leave non-conforming template code behind. THIS goal is the ONE dedicated fixup session — run in a loop, or as a scheduled **Claude Code routine** (see DEPLOYMENT below) — that sweeps `src/emitter/BB_templates/` + `XA_templates/` to TEMPLATE SPEC v2 and the FACT RULES, file by file, behavior-neutral. Quality enforcement is its ONLY job. It adds no features, fixes no bugs beyond hygiene, and makes no semantic decisions — those get flagged for Lon.

## THE TARGET — what "clean" means (pointer list; canonical text lives in GOAL-SNOBOL4-BB.md)

**TEMPLATE SPEC v2** (canonical block: GOAL-SNOBOL4-BB.md "⛔ TEMPLATE SPEC v2"): no local variables · ONE return per PLATFORM returning ONE concatenated string · IF()/FOR() string functions · ONE source line == ONE asm line · REAL Greek α β γ ω · no MEDIUM_* at template top level · zero emit_fmt() · zero C comments · zero blank lines · **ONE-IR-ONE-LOGIC** (1 IR kind never carries N distinct four-port logics; split in LOWER) · **EMIT-BLIND / NO NEIGHBOR INQUIRY** (a template never dereferences a neighboring IR node to admit or choose an emission; LOWER decides, templates emit). REGENERATE whole, don't patch.

**FACT RULES the sweep also enforces** (canonical blocks in GOAL-*-BB.md; do NOT fork their text): `bb_bin_t` ABOLISHED (in-band records via `bb_emit_x86`) · ONE MEDIUM INVISIBLE (no `IF(MEDIUM_BINARY,…)` instruction pairs; encode via `x86()`) · NO C BYRD-BOX FUNCTIONS (`(ζ,int entry)` signature) · NO VALUE STACK · NO DUPLICATED LOGIC (DUP FORMS 1–4; value work = ONE `rt_*` call) · PER-BOX LOCAL STORAGE (RO `[rip+disp]` / RW `[ζ=r12+off]`) · X86-64 register convention (Σ=r13 δ=r14 Δ=r15 ζ=r12) · TEMPLATE-ONLY EMISSION · LANGUAGE-BLIND TEMPLATES.

## TWO TIERS — classify before touching

- **TIER H (hygiene — mechanical, behavior-neutral by construction):** locals→inline, return-shape, Greek ports, emit_fmt removal, comment/blank purge, MEDIUM-branch collapse into `x86()`, `bb_bin_t`→in-band records, register-convention conformance. No IR changes, no LOWER changes, no dispatch changes. The emitted asm should be IDENTICAL or gate-equivalent.
- **TIER S (structural — needs LOWER + dispatch work):** ONE-IR-ONE-LOGIC splits (new IR codes, new `emit_core.c` cases, new template files, LOWER arms) and EMIT-BLIND fixes that move neighbor-kind decisions into LOWER and operand values into `_.op_*`/ζ-slots. One IR-split per commit chain; `prove_lower2.sh` + full gates each rung. A TIER S fix that requires NAMING new IR kinds follows the existing pattern (`IR_ASSIGN_LIT_S` style); if the right split is ambiguous, FLAG in the tracker for Lon — never guess a semantic boundary.

## ⛔ FIXUP DISCIPLINE (the laws of the loop)

1. **BEHAVIOR-NEUTRAL ALWAYS.** Full gate battery green before AND after every file. TIER H additionally proves asm equivalence where the transform claims identity: `git stash`-baseline method — emit `--compile` output for the rung corpus before and after, `diff` must be empty (or differences explained by the sanctioned transform, e.g. label renames).
2. **ONE FILE PER COMMIT.** A conflict then costs one file, not a batch. Commit message: `FIXUP <file>: <criteria cleared>`.
3. **PULL BEFORE EVERY FILE.** `git pull --rebase` on SCRIP + .github at the top of every iteration. Push immediately after each green commit.
4. **SKIP HOT FILES.** If `git log --since="6 hours ago" -- <file>` shows a non-fixup commit, a generator session owns it right now — skip, take the next ranked violator. Never fight a live session for a file.
5. **NEVER WIDEN SCOPE.** No feature work, no bug fixes beyond the hygiene transform, no "while I'm here." A discovered functional bug → tracker note + handoff doc, untouched.
6. **GATES ARE THE ONLY BRAKE** (this matters for unattended routine runs): no green → no commit → no push. A run that cannot get green REVERTS its working tree and writes a tracker note instead.
7. **BOUNDED WORK PER RUN.** 1–3 files maximum per iteration/routine-run. Small, verifiable, mergeable.

## THE LOOP (one iteration — also the routine-run body)

```
1. Clone/pull SCRIP + .github (rebase).  git config per RULES.md identity.
2. Session Setup (below): install, build, libscrip_rt.
3. Baseline gate battery — must be green BEFORE touching anything (else: tracker note "inherited red", stop).
4. Run the AUDIT BATTERY → ranked violator list.
5. Pick top violator that is (a) unticked in BB-REVAMP-TRACKER.md, (b) not HOT (law 4), (c) TIER H unless the ladder says a TIER S rung is next.
6. REGENERATE the file whole to SPEC v2.
7. Build + full gate battery + (TIER H) asm-equivalence diff.
8. Green → tick + annotate tracker → commit (one file) → pull --rebase → push (SCRIP first, .github last if touched).
9. ≤3 files this run? GOTO 4. Else stop (routine run ends; next trigger resumes).
```

## AUDIT BATTERY (ranked-violator detector)

Per-file grep counts (comments stripped), summed as the rank score:
`pBB->[αβγω]` (EMIT-BLIND) · neighbor `->t ==` via local aliases · `b.size(` · `x86_Lrec|x86_Jrec|x86_Drec|x86_b[123]\(|bytes\(|u8\(|u32le|u64le` · `IF(MEDIUM_BINARY|IF(MEDIUM_MACRO_DEF` · `emit_fmt\(` · `^\s*//` + prose block comments · blank lines · `PORT_ALPHA|PORT_BETA|PORT_GAMMA|PORT_OMEGA` · local variable declarations at template top level.
Plus the standing gates: `test_gate_no_bb_bin_t.sh` · `test_gate_template_medium_invisible.sh` · `test_gate_no_handencoded_bytes.sh` · `test_gate_sno_pat_reg.sh` · `util_template_purity_audit.sh` · `test_gate_no_vstack.sh`.
**FIX-0 authors `scripts/audit_bb_fixup_rank.sh`** to print this as one ranked table, and `scripts/test_gate_bb_emit_blind.sh` (informational baseline → `--strict` zero at FIX-FENCE).

## DEPLOYMENT — Claude Code ROUTINE (Lon's "routine runs" question: YES, this is the fit)

A **routine** = saved prompt + repositories + environment + connectors, run unattended as a fresh Claude Code session on Anthropic-managed cloud infra, fired by a **schedule** (hourly minimum cadence), an **API POST**, or a **GitHub event**. Research preview; Pro/Max/Team/Enterprise; daily run cap per account; draws subscription usage like interactive sessions. Manage at `claude.ai/code/routines`, `/schedule` in the CLI, or Desktop → Routines → New routine → Remote.

**Why it fits THIS goal:** each run is a FRESH session — no context-window decay — and this goal file + the tracker + git ARE the externalized state, so stateless re-entry is free. The HQ session-start protocol already assumes it.

**Routine prompt (paste as the routine's prompt; keep it this short — the goal file carries the protocol):**
> Clone github.com/snobol4ever/.github and github.com/snobol4ever/SCRIP. Read /.github/GOAL-BB-FIXUP.md and execute ONE iteration of THE LOOP exactly as written, honoring all FIXUP DISCIPLINE laws. Maximum 3 files. If gates cannot go green, revert and write a tracker note. Do not widen scope.

**Configuration:** repositories = SCRIP + .github (both; cloned fresh from default branch each run) · environment must allow `apt-get` (Session Setup installs libgc-dev etc.) · trigger = **schedule, hourly or nightly** (steady, predictable usage) — a GitHub push-trigger on SCRIP is the elegant alternative (generators push → fixer wakes) but preview-period webhook caps and 4–8 active generators make schedule the calmer choice · connectors: none needed.
**Branch policy decision for Lon:** default, routines push only `claude/`-prefixed branches → fixup lands on `claude/bb-fixup-*` and Lon merges (SAFEST while trust is earned, but goes stale fast against 8 generators). Enabling **"Allow unrestricted branch pushes"** lets it commit gated work straight to main like every other session (house style; the gates + laws 1/6/7 are the brake). RECOMMENDATION: start restricted for the first few runs, flip to unrestricted once the run transcripts look right.
**One-off test:** create the routine, hit **Run now**, read the session transcript at claude.ai before trusting the schedule.

## LADDER

- [ ] **FIX-0** — Author `scripts/audit_bb_fixup_rank.sh` (ranked table) + `scripts/test_gate_bb_emit_blind.sh` (baseline from tracker snapshot 2026-06-04). Add both to Session Setup here. Gate: scripts run clean on current tree; counts match tracker snapshot.
- [ ] **FIX-1** — TIER H sweep, builtin family by rank: `bb_builtin_is_cmp`(28) → `bb_builtin_atom_string`(28) → `bb_builtin_term_inspect`(15) → `bb_builtin_term_io`(12) → `bb_builtin_aggregate_nb`(9) → `bb_builtin_succ_plus`(8) → `bb_builtin_list`(8) → `bb_builtin_io`(8) → `bb_builtin_type_test`(4) → `bb_builtin_retract_throw`(4). NOTE: their `pBB->α/β` reads are EMIT-BLIND (TIER S where the fix needs LOWER operand delivery) — clear the TIER H criteria per file now, leave a `[S]` tracker mark for the residue.
- [ ] **FIX-2** — `bb_assign_frame` + `bb_assign_frame_ref`: operand fusion (`pBB->α->ival/dval`) → `_.op_*` plumbing (driver prepares; template goes blind).
- [ ] **FIX-3** — `bb_call` family (`bb_call`, `bb_call_proc_staged`, `bb_call_write_slot`, `bb_return`, `bb_every`): two-level neighbor classification (`lf->t`, `fin->α->t`) moves to LOWER. TIER S; design the IR shapes first, one split per commit chain.
- [ ] **FIX-4** — `bb_gvar_assign` ONE-IR-ONE-LOGIC split: 6 arms → per-shape IR codes + templates. TIER S.
- [ ] **FIX-5** — `bb_match` split: HEAD/RETRY/ADVANCE → three IR codes, three templates. TIER S.
- [ ] **FIX-6** — Audit residue: `bb_keyword` (4 arms — confirm near-identical-parameterized vs distinct), `bb_scan_stmt` (literal vs non-literal arms), then everything `audit_bb_fixup_rank.sh` still ranks > 0.
- [ ] **FIX-LOOP** — Steady state: tracker fully ticked once; the routine keeps running the AUDIT BATTERY and catches NEW violations from generator sessions within one cadence period.
- [ ] **FIX-FENCE** — All v2 gates `--strict` zero · `test_gate_bb_emit_blind.sh --strict` green · tracker clean · this fence in every generator goal file's Session Setup.

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
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

**Carved 2026-06-04 (Opus 4.8 session, Lon directive).** No fixup commits yet. Baseline = BB-REVAMP-TRACKER.md violator snapshot 2026-06-04 (EMIT-BLIND: 12 files w/ direct `pBB->[αβγω]` totaling 132 refs + 5 files w/ aliased neighbor walks). Tracker v1-done marks carried over. Next: FIX-0.
