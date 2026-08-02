# DESIGN-SN4-ZW-ZD-OPUS-PLAYBOOK — walk the ladder without re-deriving it

**Written s23p (2026-08-02, Fable) at Lon's direction so that Claude Opus sessions can execute `GOAL-SNOBOL4-BB.md`'s ZW / ZD / RBP-SHED rungs mechanically.** Every claim below was re-measured against a fresh clone + fresh build this session (SCRIP HEAD at write time; `scrip` built green first try with `make scrip`). Nothing here is inherited prose: where the goal file's rung text has drifted (it has — see §8), THIS doc records the drift and the goal file's LIVE CURSOR still outranks both on "what's next."

**READ ORDER FOR AN EXECUTING SESSION (non-negotiable, ~10 min):** `PLAN.md` → `RULES.md` (in full) → `GOAL-SNOBOL4-BB.md` LIVE CURSOR + THE MODEL + LADDERS → this doc → the FINDING doc the cursor names for your rung → `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` **before touching any `x86_asm.h` encoder or template** → `ARCH-ICON.md` register contract section. Then the rung.

---

## §0 THE MODEL, OPERATIONALLY (what the machine code must look like)

Lon's words, verbatim from the STF-UNFLIP comment (emit.cpp, grep `STF-UNFLIP`): *"NO BB EVER CONSUMES ANYTHING, EVER. A BB allocates EXACTLY at alpha — one `sub rsp, K`, its OWN cell — never at beta (ARBNO-class excepted); it frees at omega; and the whole accumulation is freed AT THE END OF THE STATEMENT."* Cells stack non-popping through the statement; consumers READ operand cells at `[rsp + Δdepth]`; ONE statement-terminal release (`op_zgpop`) drops everything. RBP is licensed ONLY for housekeeping that must survive an unwind (ARBNO/FENCE1/CALL, the match frame) — law 4. The WHACK CONTRACT (goal file, THE MODEL section) governs release placement: two mechanisms (determinable = one `add rsp,K_total` at final success; indeterminable = empty RBP frame + `mov rsp,rbp; pop rbp`), three site classes (statement end · match end · FENCE0/1 commit), GLUE NEVER WHACKS.

**COMPLIANT witness (regenerate, don't trust):**
```
printf '    A = 2\n    B = 3\n    OUTPUT = A + B\nEND\n' > /tmp/probe1.sno
/home/claude/SCRIP/scrip --compile /tmp/probe1.sno </dev/null > /tmp/probe1.s
```
Statement 3 emits: `n4_var_α: sub rsp,16` · `n5_var_α: sub rsp,16` · `n6_binop_α: sub rsp,16`, binop reads operands NON-POPPING at `[rsp+32]/[rsp+16]`, writes own cell `[rsp+0]` — then `n7_assign` (K=0 sink) reads the cell and carries the fused `add rsp,48` + `jmp main_γ`. That trailing add is the **placement debt** (correct amount, wrong home — belongs to the IR_STATEMENT box, rung ZW-5). The `.Lx14_*` skip + adds + jmp inside n6 is the **jcc-invert synth** (x86_asm.h, grep `x86_fc_jcc_gamma`) — conditional edges that must release ride it; don't mistake it for a second release authority.

**NON-COMPLIANT witness (the block Lon keeps seeing):** `roman.sno` ROMAN-body statement 1 → `n1_var_α: sub rsp, 240` + 30 `stmt_claim` zero stores. Measured cause this session, decisive: `SCRIP_LP_DIAG=1` prints `[LP] prefix=proc_LBL__ROMAN n=30 armed=0 all_zd=0 ... jmp=1` while `SCRIP_ZD_GAP=1` shows **every node in that run admits individually** (VAR/MATCH_BEGIN/SEQ/END/LIT/REPLACE all `admit=1`). The decline is **graph-level**: LBL__ pseudo-proc bodies are jmp-entry chains (EXIT-CLASS C), and zd_plan's jmp-entry gate (emit.cpp, grep `ZD-1 JMP-ENTRY DECLINE, REFINED`) declines them wholesale → every statement head falls to the UCLAIM arm (§2). roman's other blocker is `IR_CALL admit=0 callee=ROMAN` = ZD-7. **So: the 240B block is drained by ZD-4 (+ the zdyn/FENCE1 veto where present) and ZD-7 — not by any ZW rung directly.** Do not "fix" it in a template; the template is downstream of the plan.

---

## §1 SESSION BOOT (mechanical)

```
git clone https://github.com/snobol4ever/.github /home/claude/.github
git clone https://github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://github.com/snobol4ever/corpus /home/claude/corpus
git clone https://github.com/snobol4ever/x64    /home/claude/x64      # SPITBOL oracle: /home/claude/x64/bin/sbl -b f.sno
cd /home/claude/SCRIP && make scrip -j$(nproc)                        # deps: libgc-dev flex nasm libgmp-dev m4 (usually preinstalled)
git config user.name "LCherryholmes"; git config user.email "lcherryh@yahoo.com"   # per repo you touch
```
`scrip --compile f.sno` prints `.s` to **stdout** (redirect it). `scrip --run f.sno` = mode-3. Always `< /dev/null`, always `timeout 8s` (unit) / `timeout 30s` (corpus). Crosscheck harness: `xc.sh` lives in `.github` root — copy to /tmp, **absolute** scrip path (it cd's; `./scrip` = phantom rc 127). Regen ×4 after any codegen-touching session: `scripts/util_regen_{benchmark,feature,demo,crosscheck}_s_artifacts.sh "<rung>"`. Push-state truth = `scripts/handoff_status.sh` ONLY.

**Diag/killswitch env vars (all verified live this session):** `SCRIP_LP_DIAG=1` per-graph arm census · `SCRIP_ZD_GAP=1` per-node admission verdicts · `SCRIP_STF_DEBUG=1` · `SCRIP_ZETA_OMEGA_TRACE` · gates: `SCRIP_ZD_SR=0`, `SCRIP_ZD_DYNARM` (bitmask: 1=DEFER 2=PATREF 4=FENCE1), `SCRIP_HEAD_PIN=0`, `SCRIP_STMT_FRAME=1` (opt-in, model-violating, leave off), `SCRIP_OPT=0` (emergency only), `SCRIP_ZD_JMPENTRY` (ZD-4's hatch — verify it still exists before relying; grep first).

**Time-box:** `date +%s` at phase start; check every few rounds; 10-min default; crossing = check in, not abort.

---

## §2 THE COORDINATE SYSTEM (read this or you will corrupt rsp)

ONE planning walk, ONE application choke, ONE release authority. Grep anchors (never trust line numbers — s23-era emit.cpp shifts weekly):

- **`zd_plan(...)`** (emit.cpp, grep `static void zd_plan`): the single execution-order walk, run once per chain BEFORE emission (grep `ZD-1: the ONE execution-order walk`). Produces per-node: armed flag `zd_on[]`, depth-out `zd_out[]`, γ-release `zd_gp[]`, ω-release `zd_wp[]`, UCLAIM triple `zd_uk/zd_ud/zd_uh[]`, ZW verdict `zd_zw[]`.
- **`zd_k(nd)` / `zd_nops(nd)`** (adjacent, grep `THE ONE AUTHORITY for K`): K∈{0,16} per kind; operand counts per kind. **These are the two one-authority functions.** Any new admitted kind = one edit in each, NOTHING re-spelled elsewhere (the s22k law: every duplicate spelling that ever existed caused a silent stack skew, measured).
- **Staging choke** (grep `ZD-1: cleared at the choke UNCONDITIONALLY`): `g_zd_*` → `g_emit.op_*` exactly once per drive; every other entry path sees zeros. Fields: `op_zres` (has cell), `op_zread[k]` = `zd_out[consumer] − zd_out[producer]` = the `[rsp+Δ]` operand distance, `op_zkind[k]` (note names), `op_zgpop`/`op_wpop` (terminal releases), `op_uclaim/op_udout/op_uhead` (UCLAIM triple), `op_zw` (canonical-frame verdict), `op_stmt_pin` (head-pin slot).
- **Release authority** (x86_asm.h, grep `STATEMENT-TERMINAL GAMMA RELEASE`): the X86H_JMP γ arm emits `add rsp, op_zgpop` (+ pin restore under `op_stmt_pin`); the ω twin emits `op_wpop` gated on `op_wterm`. Conditional edges route via the jcc-invert synth (grep `x86_fc_jcc_gamma`). **There is no other whack spelling.** ZW-5's whole job is moving the STAGING of op_zgpop, never adding an emission site.
- **UCLAIM arm** (x86_asm.h, grep `UCLAIM (wholesale flip`): declined-run head α = `sub rsp, op_uclaim` + CLAIM-ZERO loop (the `stmt_claim` notes; grep `ON-5 FIX`) via the `[rsp# + N]` **raw escape**. β re-entries carve nothing (claim live across backtracks BY DESIGN — per-node claims were tried and rejected: retry re-carve leaks; see the comment's full argument before "improving" this).
- **`zvo_resolve` / owner table** (emit.cpp, grep `UCLAIM OWNER TABLE`): legacy `FR/FRQ` spellings resolve claim-relative through it. **ARGREAD hazard:** plain `RDQ("rsp",N)` gets RE-RESOLVED; the raw escapes `rsp#`/`rbp#` bypass (grep `raw-cell escape`). Writing a claim slot with the wrong spelling silently lands 8–48 bytes off (ON-5's 4-cells-never-written defect).
- **ZW frame model entries** (emit.cpp, grep `ZW-12: the canonical frame's push rbp`): `+ZW_FRAME_TOTAL` at head, `−ZW_FRAME_TOTAL` at MATCH_END — planner and emission share the named constant so depth math cannot drift.
- **Templates speak x86() only.** One concatenation chain, medium invisible, consumed by `bb_emit_x86`'s record walk. The per-medium pair (`IF(MEDIUM_TEXT,...)+IF(MEDIUM_BINARY,...)`) is the NAMED FORBIDDEN SHAPE. New instruction → new encoder in x86_asm.h, both media, never bytes in a template.

**Probe suites cannot certify emission rewrites** (s23o law §2: a guardless mnemonic silently dropped two cmps and probes stayed green on stale flags). Emission changes are certified by `.s` region diff + full crosscheck BY SET both modes + bench board.

---

## §3 GATES — run these, paste outputs, never summarize from memory

1. **Watermark bracket:** reprove at session OPEN before any edit, again at close. `xc.sh` over `corpus/crosscheck/` (318), TIMEOUT=8, both modes. Compare **BY SET** (sort the fail/timeout program lists; `comm`), never by count — the fail/timeout split shifts with container speed. Record of record lives in the goal file's cursor (s23o: m3 280/27/10 · m4 266/39/10/2L; 213_gc_exhaustion_churn is the named m3 flake; {test_string,1017_arg_local} the named 2L pair).
2. **Bench board:** `corpus/benchmarks/snobol4/` — 18/21 exact record hold (roman + the eval pair = pre-existing residue). Compare stdout to `.ref`.
3. **Regen ×4** (codegen sessions): insertions==deletions on annotation-only rungs; any code-different artifact must be explainable or the rung is not neutral. Artifacts are HONEST CURRENT OUTPUT, never pinned goldens; regen proves the compiler that ran it, not HEAD — fresh-build first.
4. **Any diverge → MONITOR FIRST** (RULES ⛔): `scripts/test_monitor_2way_sync_step_bin.sh <file>`; bracket theorem; gdb breakpoint + `ignore N-1` spin counter (HW watchpoints are dead in this container). Never hunt by reading code.
5. **Byte-identity sweeps** for intended-neutral rungs: compile all 318 pre/post, md5 per file, diff the manifests.

**Census one-liners (re-run per rung; the goal file's numbers are STALE-CITED by its own admission):**
```
D=/tmp/cs; mkdir -p $D; for f in /home/claude/corpus/crosscheck/*.sno; do timeout 8 /home/claude/SCRIP/scrip --compile "$f" </dev/null > $D/$(basename $f .sno).s 2>/dev/null; done
grep -c 'stmt_claim' $D/*.s | awk -F: '$2>0' | wc -l                                    # UCLAIM-head statement population
grep -B1 'add *rsp' $D/*.s | grep -cE 'jmp +main_[γω]'                                  # fused-terminal proxy (refine per rung)
grep -hE 'sub +rsp, [0-9]+' $D/*.s | awk '{print $NF}' | sort -n | uniq -c | tail -5    # claim-size histogram (the 240/496 class)
grep -lc 'rbp' $D/*.s | wc -l                                                            # rbp-bearing program count (SHED metric)
```

---

## §4 LADDER ZW — rung-by-rung

**Order of execution per the LIVE CURSOR: ZW-5s2 → ZW-5s3 → ZW-1 → ZW-2 → ZW-3 → ZW-6.** ZW-0 is DONE (both stages; ladder checkbox stale). ZW-4 is DONE as scoped (g_anchor half; the g_patstk half is ZW-1/2's by design — six live template readers: `grep -n g_patstk_sp src/templates/*.cpp` → begin ×4, end ×2, plus rtx_match.S lazy-init and the fence1 comment).

### ZW-5 slice 2 — lower mints IR_STATEMENT  (the cursor's NEXT; ~1 session)
CURRENT STATE (verified): `bb_statement.cpp` = 16-line dormant template (α → bomb → γ → β-trampoline); dispatch case live (emit.cpp grep `case IR_STATEMENT`) staging `op_zgpop = nd->ival`, `op_fc_bytes = 0`; `zd_k` returns 0 for the kind; lower does NOT mint. Read `FINDING-2026-08-02d` §7 + the s23k addendum in the goal file FIRST — the design of record; do not re-derive.
STEPS:
1. **Locate lower's statement-run construction** (`src/lower/lower_snobol4.c`; grep `bb_src_of` roots and the chase loop the ON-4 finding annotated). Admission gate for slice 2: statements whose fail edges all arrive at depth 0 (the template comment's own condition — "the lower gate must decline fail edges arriving at depth > 0"). Everything else lowers exactly as today (degrade never die).
2. Mint `IR_STATEMENT` per admitted statement: node first, body lowered with `succ := γ-side`, threaded `cx` fail continuations → the box's ω. Stamp `K_total` into `nd->ival` (source of K_total = zd_plan's terminal figure for the run — do NOT hand-sum; the seed forbids hand-counted pops, grep `ZERO HAND-COUNTED POPS`).
3. Wire α→body child in the template (replace the slice-1 bomb) via the driver child-handoff idiom — copy the dispatch/emit shape of an existing bracket-ish box (IR_MATCH_BEGIN's drive is the sibling), not a new mechanism.
4. **Migrate the last-operator op_zgpop staging** to the statement box: at the staging site (emit.cpp grep `g_zd_gpop = zd_gp`), armed-and-minted statements stage zgpop on the STATEMENT node and zero it on the last operator. The emission arm in x86_asm.h is UNTOUCHED (one-authority law — s23o-b measured all template mentions are comments; the 5,923 are firings, not spellings).
5. Killswitch: `SCRIP_ZW5=0` reverts to last-operator staging (ZD-SR precedent shape).
GATES: full §3. Expected deltas: fused `add rsp,K + jmp main_γ` pairs on last operators → the statement box's γ; count with the census proxy pre/post; crosscheck BY SET identical; bench 18/21 hold. TRAPS: (a) K_total staged ≠ planner depth = silent skew, one authority only; (b) jmp-entry/EVAL fragments are NOT admitted (the s193 falsification: fragment protocol reads its slot, ZD gpop frees the cell under it → segv at EVAL — grep `admitting ALL jmp-entry citizens regressed`); (c) the β-trampoline in the template is load-bearing for suspend/resume — keep it.

### ZW-5 slice 3 — ω per-depth stub ladder + planner  (~1 session)
Lands ATOMICALLY with its planner (s22h law — a ladder without the depth-set computation is a bomb, and a planner without the ladder is dead code; neither half ships alone). Planner: per admitted statement, the SET of distinct fail-arrival depths; emit one `s<stno>_ω_d<K>` stub per depth (add rsp,K; jmp shared ω tail). Then LIFT slice-2's depth-0-only admission gate. `zd_wp`/`op_wterm` semantics (grep `HEAD-PIN (s22z): restore gated on op_wterm`) must keep meaning "restores to statement entry" — mid-statement folds must NOT gain pin restores. GATES: full §3 + `SCRIP_ZETA_OMEGA_TRACE` diff pre/post (site count + death classes).

### ZW-1 — light the MATCH_BEGIN canonical frame  (~1–2 sessions)
**The op_zw arm ALREADY EXISTS** in bb_match_begin.cpp (grep `_.op_zw`) behind planner verdict `zws` (emit.cpp grep `RUNG ZW-12 verdict`, gate fn `zw_frame_on()`): arms only where Kc>0 ∧ no blob members ∧ no ABORT/FENCE1 seal ∧ an IR_MATCH_END closes the run ∧ window-integrity pre-scan passes. Rung = finish the arm's contract + widen/flip + delete legacy:
1. Verify current default of `zw_frame_on()` and the armed population (`SCRIP_LP_DIAG` + a zws counter if none prints — add a diag, file-static env-gated, ZD-GAP shape).
2. Complete the frame per the design of record (FINDING-2026-08-02d §7): `push rbp; mov rbp,rsp; sub rsp,K≤64`; cells {outer Σ/δ/Δ, cas_base, **anchor_snapshot**, start_δ}. anchor_snapshot: read `[rip+rt_anchor_g]` ONCE at α (SPITBOL manual: `&ANCHOR` is obtained only at match start — the s23o deliberate deferral lands HERE); the unanchored-retry loop reads the SNAPSHOT cell, not the global.
3. Subject read IN PLACE from its producer cell (no pop — fixes the measured operator-rule violation: legacy head α pops the subject `add rsp,16` before pinning; grep the WHACK CONTRACT clause 5 parenthetical).
4. Delete, ONLY inside the op_zw arm's population: dual marks, old_rbp slot ceremony, the marker rsp/patstk snapshot pushes (the CAS-MARKER-CARRY block — its readers die in ZW-2). The `!_.op_zw` legacy arm stays byte-identical until ZW-2 lands and the flip is proven.
5. NOTE ON STALE RUNG TEXT: the "emit.cpp:2509/2521 per-medium retry-blob pair" the rung names was ALREADY converted to x86() chains by s23o (verified: the retry blob is one medium-invisible chain using `rbp#` + the GOT anchor lea). What remains of that item is relocating the retry loop's storage onto the frame's cells — offsets, not media.
GATES: full §3 + the goal file's pattern-heavy set (100_pat, 105_pat_fence_empty, string_pattern, mixed_workload, roman bistable pair) + monitor on any diverge. TRAPS: HKQ's `"+ -N"` spelling is deliberate (x86_parse strtol); the head's zref subject read executes at α depth BEFORE the push (planner comment — reorder and every claim-slot read is +TOTAL wrong); `rpin()`/op_stmt_pin publication is the LEGACY regime's mechanism and must stay suppressed under op_zw (the existing `!_.op_zw` guard — keep it).

### ZW-2 — MATCH_END frame-pop whack  (~1 session, pairs with ZW-1)
The op_zw γ arm ALREADY EXISTS in bb_match_end.cpp: apply-walk pump `rt_dcap_end_ok_open` with `rdi=[rbp-32] (cas_base), rsi=r12 (live top), rdx=Σ`, then the whack `mov rsp,rbp; pop rbp`. Finish: ω = same minus walk; then DELETE (armed population): rsp_mark/patstk_mark reads, both marker scans, the g_patstk_sp readers in end (×2) — and once begin's ×4 die with ZW-1, retire `g_patstk_sp` itself + the rtx_match.S lazy-init arm + the 1,112 emitted mark sites (they are mark-ONLY; s23k measured zero pushers ever — grep the FINDING). Coordinate law already in the planner: END's zout is POST-WHACK (grep `END's zout ... POST-WHACK`). GATES: full §3; the deletion half is where the 318 crosscheck earns its keep — captures/ARBNO/alternation programs are the population.

### ZW-3 — r12 CAS live  (~1 session; AUDIT-first)
Design (FINDING-2026-08-02d §6.1): the slab already IS the CAS — `rt_dcap_e` records (pattern_match.c, grep `typedef struct { const char *varname`) γ-pushed by bb_match_capture, pumped by END. Do: reverse s5's r12-parking — 6 emitted sites + 2 m4 wrapper seeds + `rt_outer_call` thunk (r12 = live top, callee-saved coherence, cell = lazy-init seed only); `rtx_match.S` r12-direct; fail-discard `r12 ← cas_base` (REQUIRES ZW-1/2's frame cell); THEN cap_gen deletion. ⛔ stacklets (grep `iteration-reuse` in pattern_match.c) get a WRITTEN AUDIT before any edit — separate commit, separate gate run. r12 is currently zero-use corpus-wide (s23k measurement) so the reversal's first commit is wiring-only + the INSTRUMENTED canary (x86_asm.h grep `R12-wiring assert`).

### ZW-6 — FENCE + glue relocation  (~1–2 sessions)
**The discriminator is ALREADY LEDGERED** — do not re-derive: emit.cpp grep `EXIT-CLASS LEDGER (s22v` names the three glue classes and their verdicts. CLASS O (outer one-shot, main_γ/ω `mov rsp,rbp; pop rbp` — 676 census-class): relocate into the terminal END_STATEMENT release once ZW-5 is lit; main's glue becomes pass-through + exit. CLASS C (chain-entered LBL__/EVAL): the whack IS the m3 return-to-C mechanism (s22u falsification: suppressing it broke 1016_eval) — KEEP, by ledgered decision; relocation here means giving chains a real statement-box release first. CLASS P (wire-entered DEFINE stubs): already whack-free through the wires. PAT$N scanfail/ω shared exits (302): move into match machinery = ZW-2's ω once the frame owns unwind. FENCE0 rides the SNO$PB0 blob (grep `BLOB-GRANT (s22z` for the blob's self-allocation seed — the α wire quad + pin layout is documented there verbatim); FENCE1's commit-whack canonicalizes onto contract mechanism (2). Hook glue-leave sites: x86_asm.h grep `bb_glue_flat_leave` (γ gated on `zwco`, ω unconditional) — the relocation edits the CONDITION set, the leave body (`add rsp, op_fc_bytes` under CELL_STACK) stays one spelling.

---

## §5 LADDER ZD — what actually drains Lon's 240-byte block

Census discipline: `[ZD]` first-blocker line + `SCRIP_ZD_GAP=1` full-run verdicts; a decline count is a FRONTIER reading (clearing a cheap blocker promotes the expensive one). Re-run after every rung. s21x-y frontier: 790 declined = CALL 519 · MATCH_BEGIN 247 · SAVE_RESTORE 18 · GOTO_DEFERRED 6; value spine = zero.

### ZD-4 — lift the jmp-entry decline  (roman's named blocker; ~1 session)
CURRENT STATE (measured): `proc_LBL__ROMAN n=30 armed=0` with every kind admitting → the decline is the graph-level gate, emit.cpp grep `ZD-1 JMP-ENTRY DECLINE, REFINED s22k (ZD-9)`. Its own comment records the two prior falsifications: blanket admission regressed expr_eval/161/1016/1019 (fragment protocol reads a slot the terminal gpop just freed); the refined form admits DEFINE-STUB blobs via `zd_stub_ok` — **which s23g deleted as caller-less** — so verify what the gate ACTUALLY tests at HEAD before anything (grep the gate body; the [LP] proc_ROMAN armed=2 vs proc_LBL__ROMAN armed=0 split tells you the current live discriminator). STEPS: (1) census the jmp-entry population by exit class (the s22v ledger's `g_flat_frame_floor` predicate is the driver's own verdict — reuse it, never a new language-ish flag); (2) admit CLASS C chains whose statements are ordinary (the ROMAN-body shape) under hatch `SCRIP_ZD_JMPENTRY=1`; (3) the rung's own recipe: diff 1019's fragment `.s` hatch-on/off, fix the divergence the monitor brackets, delete the gate for the admitted class. Also examine the `zdyn` MATCH veto (grep `DYNAMIC-BOX DECLINE`) — FENCE1/dynamic DEFER statements stay declined until ZW-6/s23i's static-shape arming covers them; `SCRIP_ZD_DYNARM` bits are the A/B instrument. EXPECTED RESULT: roman's `n1_var_α` drops 240 → 16 and the UCLAIM zero-loop vanishes for admitted statements; roman stays red on IR_CALL until ZD-7. GATES: full §3 + EVAL family by name (1016/1019/161/expr_eval) + monitor.

### ZD-7 / ZD-7c — IR_CALL + user-proc arm  (7c is SPEC'D, ~20 min + gates)
The goal file's ZD-7c entry is already Opus-grade — execute it verbatim; verified at HEAD: `zd_nops` already returns `n_operands` for IR_CALL and stages per-arg reads automatically (grep `ZD-7 (b)`), the exclusion lives in `zd_wl_kind` via `rt_proc_is_registered`, and `bb_deref.cpp:13-22` is the sibling idiom to copy. Killswitch `SCRIP_ZD_PROC=0`. The named controls MUST flip: 085/086/087 were the naive-admission falsification and are the regression oracle. ZD-7 proper (builtin calls, SAVE_RESTORE role interplay) follows the same staging authority; role-0 SR stays declined (CALL2BB-only, unmeasured — its decline is a DECISION, recorded in zd_wl_kind's comment).

### ZD-5 — match family (5a-PRE ledger first)
5a-PRE: the STFH-48 (grep `stfh()` claim in bb_match_begin) is a second allocation authority `zw_carve_k`-blind — enumerate its non-HKQ `[rsp+off]` refs, ledger, THEN touch. 5a linear bridgehead (head→LEN/POS/RPOS/SPAN/ANY/NOTANY/REM/TAB/RTAB→end, no alt/arbno/fence/defer/capture) mostly falls out of ZW-1/2; 5b (branching-run planner) is the ONE design-tier item on the board — bring it to Lon with a written proposal, not a diff; 5c per-template smallest-first. SPITBOL semantics per construct: manual ch.18 six-step algorithm (the CAS spec), ARBNO = shy + extend-on-retry (the mechanism-2 citizen), FENCE primitive ≠ FENCE(P) function (backtrack-fail vs alternatives-skip — FENCE(P) is SPITBOL-only).

### ZD-2c / ZD-2g / ZD-3 / ZD-6 — small, gated by need
2c/2g arm only when a widened statement first-blocks on them (today: never). ZD-3 legacy-arm deletion per fully-covered kind (grep `vfc` census == the deletion list; byte-identity sweep on the untouched population). ZD-6 standalone: 130/131 clean-HEAD segv (monitor-first), W04_arbno_basic DIV member, bb_op_name gaps ops 14/73–77.

---

## §6 RBP-SHED (order 3→1→2→4→5; each ≤ half session)

Metric per step: the rbp census one-liner (§3) — instruction count + bearing-program count, pre/post, cited in the FINDING. SHED-3 REC-PIN-OWN: stale-emission globals → per-graph g_emit mirror at the emit_chain choke (grep `emit_chain`). SHED-1: retire the `g_flat_outer_nparams>=1` pin conjunct for depth-static graphs (grep it; the pin predicate is `emit_jmp_pin_rbp` — ARCH-ICON register section is the contract). SHED-2: ABORT → statement fail exit (interacts with ZW-5s3's depth ladder — sequence AFTER it). SHED-4: scanhit/scanfail hooks through x86() — s23o did the SPD-2 pair; grep `X86H` hook bodies for any remaining raw emission. SHED-5: retire the transient push-rbp alignment window (grep `ALIGN` in x86_asm.h) once ZW-1's frame makes it moot.

---

## §7 WHAT "DONE" MEANS (the directive's completion tests)

1. Compliant-shape census: claim-size histogram shows no statement-head `sub rsp` above ~64 outside ARBNO/CALL frames; `stmt_claim` population → 0 as ZD admits.
2. Fused-terminal census → 0: no `add rsp,K` on an operator box's γ/ω that crosses a statement boundary; the release fires from IR_STATEMENT / MATCH_END / FENCE commits only.
3. Glue census: CLASS O whacks relocated; CLASS C ledgered or converted; `main_γ` = pass-through.
4. rbp census: bearing programs = exactly the law-4 population (match frames, ARBNO/FENCE1, CALL protocol) — compare against `SCRIP_LP_DIAG` pat/gen flags.
5. All of it under the standing gates: crosscheck 318 BY SET both modes at-or-above record, bench 18/21+, regen ×4 honest, `handoff_status.sh` says COMPLETE.

## §8 STALENESS LEDGER (found this session; trust measurement over prose)

- Ladder checkbox ZW-0 `[~]` — actually DONE (s23n cursor). ZW-1's "emit.cpp:2509/2521 per-medium pair" — already converted s23o; the remaining work is storage relocation. ZD-9's `zd_stub_ok` — deleted s23g; the jmp-entry gate's live form must be re-read at HEAD. The 5,923/223/1,264/982 census figures are s23k-era — STALE-CITED per the goal file itself; re-run §3's one-liners at your bracket. THE MODEL and the WHACK CONTRACT are current and binding.
- Rule for executing sessions: **every file:line in any doc (including this one) is a hint; the grep anchor beside it is the reference.** If a grep comes back empty, the mechanism moved — find it, fix the doc's anchor in the same commit as your rung, and say so in the FINDING.
