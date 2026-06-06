# GOAL-BB-FIXUP.md — The Continuous BB-Template Hygiene Sweep

**Carved:** 2026-06-04 (Lon directive)
**Repo:** SCRIP + .github
**Sister:** GOAL-SNOBOL4-BB.md (canonical TEMPLATE SPEC v2 text) · GOAL-ICON-BB.md · GOAL-PROLOG-BB.md · `SCRIP/BB-REVAMP-TRACKER.md` (work queue + per-file [S] state + cursor)

## PURPOSE — N sessions generate; ONE session cleans
4–8 generator sessions dirty `src/emitter/BB_templates/` + `XA_templates/`. THIS is the ONE fixup session — **ATTENDED, opened by Lon for periodic runs** — sweeping to TEMPLATE SPEC v2 + FACT RULES via a **ROUND-ROBIN CURSOR** (tracker-persisted; every session resumes from cold). Quality enforcement is its ONLY job: no features, no bug fixes beyond hygiene, no semantic decisions — those get flagged for Lon.

## THE TARGET (pointers; canonical text lives in GOAL-SNOBOL4-BB.md "⛔ TEMPLATE SPEC v2")
**v2:** no locals · ONE return per PLATFORM returning ONE concatenated string · IF()/FOR() string functions · ONE source line == ONE asm line · REAL Greek α β γ ω · no MEDIUM_* at template top level · zero emit_fmt() · zero C comments · zero blank lines · **ONE-IR-ONE-LOGIC** (split in LOWER) · **EMIT-BLIND / NO NEIGHBOR INQUIRY** (LOWER decides, templates emit). REGENERATE whole, don't patch.
**FACT RULES** (canonical blocks in GOAL-*-BB.md; do NOT fork their text): `bb_bin_t` ABOLISHED · ONE MEDIUM INVISIBLE · NO C BYRD-BOX FUNCTIONS · NO VALUE STACK · NO DUPLICATED LOGIC · PER-BOX LOCAL STORAGE (RO `[rip+disp]` / RW `[ζ=r12+off]`) · X86-64 convention (Σ=r13 δ=r14 Δ=r15 ζ=r12) · TEMPLATE-ONLY EMISSION · LANGUAGE-BLIND TEMPLATES.

## ⛔ BINARY-ARM PORTS (recorded 2026-06-06 — do not re-learn this at mode-3's expense)
The ONLY sanctioned pe-fix inside a `MEDIUM_BINARY` arm is the **literal Greek glyph string** (`"γ"` `"β"` `"ω"`): it parses `XK_PORT`, byte-identical to the `PORT_*` macros. `_.lbl_*` strings parse `XK_SYM` and emit **NOTHING** in BINARY `jmp`/`def` — a silent mode-3 jump loss that stays gate-green because the corpus fires most resolve-family templates mode-4 only. TEXT arms keep `_.lbl_*`. Verify the `x86()` parse path (`x86_asm.h` `x86_parse`/`x86_port_of`) before any port-arg transform.

## TWO TIERS — classify before touching
- **TIER H (mechanical, behavior-neutral):** locals→inline/static helpers, return-shape, Greek ports, emit_fmt removal, comment/blank purge, MEDIUM-branch collapse into `x86()`, register conformance. No IR/LOWER/dispatch changes; emitted asm IDENTICAL or gate-equivalent.
- **TIER S (structural):** ONE-IR-ONE-LOGIC splits + EMIT-BLIND fixes (LOWER arms, new IR codes per existing pattern, `_.op_*`/ζ-slot plumbing). One IR-split per commit chain; `prove_lower2.sh` + full gates per rung. Ambiguous split → FLAG in tracker for Lon, never guess.

## ⛔ FIXUP DISCIPLINE (the laws of the loop)
1. **BEHAVIOR-NEUTRAL ALWAYS.** Full gate battery green before AND after every file; TIER H additionally proves asm equivalence (git-stash baseline `--compile` diff: empty, or differences explained by the sanctioned transform).
2. **ONE FILE PER COMMIT, STRAIGHT TO MAIN.** No branches — ever. Message: `FIXUP <file>: <criteria cleared>`.
3. **PULL BEFORE EVERY FILE, PUSH AFTER.** Cursor advance travels IN the same commit as the file's tick/note.
4. **SKIP HOT FILES.** Non-fixup commit in last 6h → advance past; caught next lap.
5. **NEVER WIDEN SCOPE.** Discovered functional bug → tracker note + handoff doc, untouched.
6. **GATES ARE THE ONLY BRAKE.** No green → revert tree, tracker note, advance, commit.
7. **CONTEXT-BUDGET HANDOFF (~70%).** Finish current file, commit, push, watermark, stop cleanly.

## THE CURSOR
`SCRIP/BB-REVAMP-TRACKER.md` header: `# CURSOR: <file>`. The tracker list is the ring — **DOCUMENT ORDER** since the 2026-06-06 rename (re-sort only at lap end, on Lon's word). End wraps to top: laps. Ticked files get a cheap re-audit on later laps (clean → free advance; dirty → un-tick, re-fix).

## THE LOOP (one cursor stop)
```
0. Session open (once): clone/pull SCRIP + .github; git config per RULES.md; Session Setup; baseline gates GREEN
   (else: tracker note "inherited red at <file>", stop and tell Lon).
1. git pull --rebase. Read # CURSOR from tracker.
2. HOT? (law 4) → advance cursor, commit "FIXUP cursor: skip <file> (hot)", GOTO 1.
3. Per-file audit → clean? → advance cursor, commit, GOTO 1.
4. Dirty → TIER H: REGENERATE whole to v2. TIER S pinned: execute the rung. TIER S unpinned: TIER H portion only, [S] flag, advance.
5. Build + full gate battery + (TIER H) asm-equivalence diff.
6. Green → tick + annotate + ADVANCE CURSOR → one commit → push. Red → revert, note, advance, commit, push.
7. Context < ~70% AND Lon hasn't stopped? GOTO 1. Else: watermark, final push, stop.
```

## AUDIT BATTERY
Per-file checker `scripts/audit_bb_fixup_file.sh <file>` (rc=0 clean) · lap table `scripts/audit_bb_fixup_rank.sh` (print at open AND close) · `scripts/test_gate_bb_emit_blind.sh` (informational → `--strict` zero at FIX-FENCE). Plus the standing gates in Session Setup.

## OPERATION — ATTENDED SESSIONS ONLY (Lon 2026-06-04; recorded so no session re-litigates it)
Lon opens a session when a run is wanted; the cursor resumes it from cold. NO branches, NO unattended/scheduled runs. **WHY:** the `(ζ, int entry)` deletion was ordered THREE times and sessions declined/re-introduced/reverted it "to keep the build green"; TWO-LITERAL-FORMS had to be RE-ISSUED after a session INVERTED it — all with green gates throughout. **Gates verify BEHAVIOR; they do not verify JUDGMENT.** The 2026-06-06 XK_SYM port bug is the same lesson from the other side: confident wrongness passes every automated check on unexercised paths. Lon watching is the only control with a working track record. Claude Code routines stay OFF the table until attended runs earn trust; revisit only on Lon's word.
**Session open protocol ("here we go"):** PLAN.md session start → this goal file → Session Setup → print rank table → enter THE LOOP at the cursor.

## LADDER
- [ ] **FIX-1** — LAP 1: cursor round-robin through the ring, TIER H per file; per-file [S] residue lives in the tracker. Heavy stops = the resolve-family arms (ex-builtin family).
- [ ] **FIX-3** — `bb_call` family (`bb_call`, `bb_call_proc_staged`, `bb_call_write_slot`, `bb_return`, `bb_every`): two-level neighbor classification moves to LOWER. TIER S, design NOT pinned — flag on arrival; Lon pins IR shapes first. **HOT 2026-06-06** (PB-9f + PB-10b + ICN-HY-7c rewrote `bb_call.cpp`) — re-audit on arrival, trust no old counts.
- [ ] **FIX-4** — `bb_gvar_assign` ONE-IR-ONE-LOGIC split: 6 arms → per-shape IR codes + templates. Design NOT pinned — flag on arrival.
- [ ] **FIX-5** — `bb_match` split: HEAD/RETRY/ADVANCE → three IR codes, three templates. Design NOT pinned — flag on arrival.
- [ ] **FIX-6** — Audit residue: `bb_keyword` (4 arms — parameterized vs distinct?), `bb_scan_stmt`, then everything rank still counts > 0.
- [ ] **FIX-LOOP** — Steady state: laps continue; a zero-dirty lap = generators' new code caught within one lap period.
- [ ] **FIX-FENCE** — All v2 gates `--strict` zero · emit-blind `--strict` green · a full clean lap · this fence in every generator goal's Session Setup.

## Session Setup
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```
Lap status (open and close):
```bash
bash scripts/audit_bb_fixup_rank.sh
bash scripts/test_gate_bb_emit_blind.sh
```
Gates (every commit; floors = carve-time values, never regress):
```bash
bash scripts/test_smoke_snobol4.sh                   # m2 7/7 HARD, m3 6/6, m4 6/6
bash scripts/test_snobol4_pat_rung_suite.sh          # M2>=18 M4>=18
bash scripts/prove_lower2.sh                         # PASS (mandatory for any TIER S rung)
bash scripts/util_template_purity_audit.sh           # floor: 2 sites (bb_call_write_slot, bb_every — FIX-3 family); NO GROWTH
bash scripts/test_gate_no_bb_bin_t.sh                # 0
bash scripts/test_gate_template_medium_invisible.sh  # trend to 0
bash scripts/test_gate_no_handencoded_bytes.sh       # trend to 0
bash scripts/test_gate_sno_pat_reg.sh                # TIER1+TIER2 HARD
bash scripts/test_gate_no_vstack.sh                  # g_vstack 0
```

## Watermark
**2026-06-06 5th attended run (Opus 4.8). LAP 1 stops 15–16 ✅: bb_list 057dd8a (100→52; bls_* helpers; asm-diff EMPTY 17-file corpus + LIVE msort/atomic_list_concat TEXT-arm probe byte-identical) · bb_retract_throw 62c1554 (18→10; rtt_* helpers; LIVE catch/throw probe byte-identical; E9-rel32-0 retract placeholder verbatim). Both: BINARY ports→literal Greek glyphs per ⛔ BINARY-ARM PORTS; [S] eb/nw + rb residue annotated in tracker (de-aliased reads now counter-visible: emit-blind 219→225, honest). HOT-RULE CLARIFIED: 75662d3 (4th run's own RENAME) is a FIXUP commit — does not trigger law 4; the prior turn's hot-skip plan was wrong and discarded uncommitted. ASM-DIFF PRACTICE: bbNNNN labels are pointer-derived, nondeterministic run-to-run — always bbN-normalize; add a LIVE probe when the corpus doesn't exercise the template (XK_SYM lesson applied forward). ⛔ INHERITED RED FLAGGED FOR LON (tracker note + HANDOFF-2026-06-06-OPUS48-BB-FIXUP-LAP1-STOPS-15-16.md): prove_lower2 on 9193511 = 66 PASS + 2 FAIL (#49 nodes 10≠8, #50 nodes 9≠7) with rc=0 — stash-A/B proves not fixup-caused; chain: PL-GZ-7 3d9ccfd ITE_COMMIT/ITE_GATE +2 nodes vs hardcoded harness counts; SNO-HY-2b's "67->68" measured pre-rebase; semantic call (counts vs lowering) owner PL-GZ/Lon, not swept (law 5); suggest hardening prove_lower2.sh to exit non-zero on FAIL. Other gates at floors: smoke 19/0 · pat-rung M2=18/M4=18 (053 pre-existing) · purity 2-floor · bin_t 0 · vstack 3 · sno_pat_reg HARD · medium-invisible 346→339. Lap 1593→1542, 95 files / 85 dirty / 10 clean. Concurrents merged green ×4 (ICN-HY-7d/7e · SNO-HY-2b · PL-GZ-7 · PB-10a2). `# CURSOR: bb_succ_plus.cpp`. Ended ~62% per law 7. Next: resume LAP 1 at cursor; FIX-3 flag-on-arrival; Lon verdict on prove_lower2 before any TIER S rung.**
