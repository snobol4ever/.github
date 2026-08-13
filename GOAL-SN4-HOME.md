# GOAL-SN4-HOME — SNOBOL4 ALL THE WAY HOME (master orchestrator)

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


**⛔⭐⭐⭐ CHARTER (Lon in-chat 2026-08-12 s30, verbatim in substance):** *"This is the final stretch. Make RUNGS and STEPS to take SNOBOL4 all the way HOME, i.e. 100% working with RSP stack relative and RBP stack relative and RBX GC heap-top relative. Use multiple Opus sessions concurrently. Rearrange EVERYTHING."*

**THE EMISSION KEY (Lon, same session, verbatim in substance):** *"A BB will EITHER access its operand's RESULT and its own LOCALS via RBP, OR via RSP."* Per-BB binary, decided at plan time by `frame_need_of` (EARN-1), emitted only by `x86_alpha`/`x86_omega` (s29 ruling: RBP is never glue work). The reading-edge sharpening keeps ALT/CAT on the RSP side even with `*P` operands.

This file is the MAP. Seats execute their own seat file (below); cursors live in seat files. All prior laws bind (RULES.md · MONITOR-FIRST · TEMPLATE-ONLY · BOTH-MEDIUM · LIVE CURSOR discipline · one clone per seat · `git config --local`, never global).

## ⛔⭐⭐⭐ 2026-08-12 EVENING AUDIT — Lon-ordered in chat ("Go check those GOAL files and find out how they did. What went wrong? Fix it in the GOAL files.") — CLAUDE-FABLE5

**THE MORNING BOARD, BY SEAT** (from seat cursors + git at SCRIP `42398e69` · corpus `1dd3ff15` · .github `391eca8c`; every claim verifiable at those hashes):

| seat | net | receipts |
|---|---|---|
| **RBP-EARN** | ✅✅ BOTH EARN-0-gating compiler defects FIXED (s44 wire-save · s45b bare-`TT_VAR` seal arm); earn0 board 26→28 m3, xc/patterns 77→82 BY SET; also landed the r9/GVA `main_alpha` seed (`677e8753`) that revived BOARD's m4, and the MATCH_SPAN eax-clobber fix (`ecc111c7`). **EARN-0 hand-check UNBLOCKED — the streak is over.** | SCRIP `42398e69` `4174782e` |
| **LOWER** | ✅ **L-3b CLOSED, l3 board 13/13 green** — non-carving splice class + ARB/BREAK ZOP double-resolution + `fc_walk_range` carve-zero; broad m3 260→261, zero regressions BY SET; s44 cleanly falsified its own s43 hypothesis. | SCRIP `7eac50a9` `b352d996` `e6def8fe` |
| **BOARD** | ✅ m4 board ALIVE, 2→157 pass (consumed RBP's seed, exactly as B-0 predicted); MON-CAP crash-safety landed; broad-336 pinned both modes; NEW UNCLAIMED compiler bug named (duplicate `.Lbynamefn*` labels = all six m4 SKIPs). ⛔ Cursor ordering violates STALE-ORIENTATION (c): s35 sits ABOVE s37 — next BOARD seat reorders newest-first. | SCRIP `5ec6e607` `94d283c1` |
| **MODE34** | ✅ 5a DEFINE-entry double-emission FIXED (it was silently corrupting mode 3); harness `-no-pie` bug fixed; 5b root-caused (SPAN(var) inline-arm stale FRQ offset); corrected two of its own findings in place. | SCRIP `cea77eca` `94d283c1` |
| **WIRES** | ◐ W-7 interim guard LANDED floor-neutral; X01 blanket-widening AND W-2's premise both FALSIFIED (dead work prevented); ⛔ ended with a NEW defer crash NOT root-caused (repro minted, `witness_wreg_s39/`) and THREE investigations blocked on MON-CAP, itself blocked on `TOKEN_SEE_LON` — a credential ask that has sat in this file's questions blocks and never reached chat. | SCRIP `45ffcb23` · FINDING-12p/q/r |
| **RBX** | ⚠ NET-ZERO on the gate-widen at full-session cost: s40b LANDED it (`73c1ac33`) WITHOUT first running the BY-SET sweep its own commit text mandated; s41 ran the sweep, found 20/122 vs the 36/122 s37 floor (58 BROKEN / 1 REPAIRED), REVERTED (`a037b637`); s41b then caught s41's own wrong next-rung too. The fork-(a) carve (`9780591d`) survives and is clean. Discipline recovered same-day; the violation was existing law (RULES Testing: "Run goal's gate before every commit"), not missing law. | FINDING-12o · .github `52d156af` `ec4ee29f` |

**Net for the morning: two rungs genuinely closed (LOWER L-3b · RBP-EARN's defect pair), one board revived (m4), one regression caught-and-reverted same-day, one hunt handed off open.** That is a working board — the first one in ~17 sessions — and it worked because the s43/s44 rulings and the tooling fix (`31fd63eb`) removed the inherited blockers first.

**WHAT WENT WRONG THIS MORNING (three items, distinct from the streak pattern):**
1. **Gate-after-land (RBX s40b).** The BY-SET sweep that convicted the fix was mandated by the fix's own text and ran one session LATE. Existing law violated, not new law needed — named here so the next seat sees the conviction, not just the revert.
2. **Questions for Lon accumulate in files, never in chat.** WIRES carries Lon-question blocks at three depths and its own s39 text says "several are re-asks — s35's went unanswered." `TOKEN_SEE_LON` blocks three investigations and was never asked for where Lon actually is. **Files RECORD; CHAT escalates.** Consolidated queue below.
3. **Opening a new hunt at end-of-context.** s39c found a new crash and handed off "not root caused." The standing "deletion at end-of-context = broken tree" law has no analog for hunts: **do not OPEN a hunt you cannot close — mint the repro, route it, stop.** (s39c minted the repro; that half was right.)

**THE 17-SESSION MALFUNCTION (Lon's ask, answered from the record — s29–s45 on RBP-EARN; the file's own count is 13 sessions of pure crash-triage, s33–s45, zero rungs closed):**
**ONE ROOT: fresh seats trusted their inheritance and ground solo instead of forcing a 30-second escalation.** Four instances, all documented:
- **gdb-404** — SEVEN sessions (s33–s39) each re-concluded "gdb is unavailable in this container," inherited from the previous cursor's unverified claim; the tooling fix (`31fd63eb`) landed only 2026-08-12.
- **Missing x64 oracle** — board scripts print a full, plausible, entirely FALSE all-FAIL table without it; THREE sessions paid before LOWER s44 made the clone a mandatory numbered PLAN.md step.
- **EARN-0 mislabeled** "no code, cheap, opens any session" while gated on two MASKING compiler defects (fixing A alone → hang, so partial progress read as failure) — seat after seat opened it and burned the runway on triage; label corrected only at s42.
- **Escalation latency** — the s43 crater ruling cost Lon ~30 seconds and ended the streak on the spot. Nothing in the process forced that question into chat at s34, so it waited nine sessions.
The triage was not waste — Lon's s43(1) ruling confirms it WAS the prerequisite, and it fixed two real compiler defects — but roughly ten of the seventeen sessions were spent REDISCOVERING blockers rather than working them.

**CORRECTIVES (this is the MAP; seat files inherit):**
- ⛔ **VERIFY-INHERITED-BLOCKERS (standing; conviction: gdb-404 ×7).** Any inherited claim that a tool/instrument/path is unavailable, broken, or dark is RE-TESTED with one command at orientation before it is believed, acted on, or re-recorded. A cursor that records a blocker MUST carry the verifying command beside the claim.
- ⛔ **CHAT-ESCALATION / STREAK BREAKER (PROPOSED — Lon ratify or strike):** (a) any blocker only Lon can clear (credential, ruling, routing) and any rung blocked ≥2 consecutive sessions goes INTO CHAT as one specific, answerable question at the TOP of the session's first reply — a questions block in a goal file is a record, not an escalation; (b) a goal at two consecutive zero-rung sessions opens its next session with that question BEFORE any code or triage. Precedent: s43.

**⛔ LON QUEUE — CONSOLIDATED (everything currently waiting on you, pulled up from all five seat files; answering these in chat is the highest-leverage 5 minutes on the board):**
1. **`TOKEN_SEE_LON` credential** → unblocks MON-CAP/csnobol4 → unblocks THREE WIRES investigations.
2. **WIRES W-2 disposition** — (a) close FALSIFIED · (b) demote to hygiene · (c) re-scope to the raw-byte TEMPLATE-ONLY cleanup at emit.cpp:2688-2724. Seat recommends closing or re-scoping; your pick.
3. **D12/D13 routing** — ARBNO template-dispatcher defect (FINDING-12k), owned by no seat; strike it from W-2's witness line either way.
4. **Duplicate `.Lbynamefn*` label bug** (all six m4 SKIPs) — unclaimed; MODE34's 12n suggests possibly superseded — route or confirm supersession.
5. **RBX X-2 (8 sessions unseated) · X-4 (5 sessions L-2-blocked)** — staff or park, explicitly.
6. **Ratify or strike the STREAK BREAKER above.**

## ⛔⭐⭐⭐ EXECUTION MODE SELECT (Lon ruling 2026-08-12 late, in-chat — supersedes the same-day SOLO-only ruling; both modes defined, **CONCURRENT IS THE DEFAULT**)

**THE RULING, in substance:** concurrency is restored as a standing CHOICE and it is the **DEFAULT** — the FIRE-AND-FORGET block below is live law again, ready for multiple seats (Opus or otherwise) the moment Lon fires them. Lon may override any session to **SOLO** in-chat (his phrase: a reminder that "you are just solo"), in which case ONE operator takes in the work of ALL the goals, walks every seat file serially, wears the seat whose rung it executes, and signs cursors in that seat's voice. Nothing ever moves physically in either mode. **The chat carrying this ruling continues SOLO by Lon's own override.**

**HOW A SESSION KNOWS ITS MODE:** Lon's fire line. A seat-named fire line (table below) = CONCURRENT seat, that file only. "You are solo" / one operator handed the whole board = SOLO. No line = assume the DEFAULT and claim ONE seat via a cursor line in your first push.

**SESSION PROTOCOL — BOTH MODES, EVERY SESSION (the s46 audit's correctives operationalized by this ruling; these are what the 17-session streak lacked, and a plan carrying them is the one "stupid enough to actually work"):**
1. **TOOLING FIRST** — `bash /home/claude/SCRIP/scripts/install_system_packages.sh` before any build (the s33 phantom-SEGV trap), then clone the x64 oracle.
2. **VERIFY-INHERITED-BLOCKERS** — any inherited "X is unavailable/broken/dark" claim is re-tested with ONE command before it is believed, acted on, or re-recorded (conviction: gdb-404 ×7 sessions).
3. **CHAT-ESCALATION / STREAK BREAKER** — any blocker only Lon can clear (credential, ruling, routing) goes INTO CHAT as one specific answerable question at the TOP of the session's first reply; a goal at TWO consecutive zero-rung sessions opens its next session with that question BEFORE any code or triage. Precedent: the s43 crater ruling, ~30 seconds of Lon, ended a 13-session streak. (Entered PROPOSED at s46; this ruling operationalizes it — LON QUEUE item 6 discharged.)
4. **GATE-BEFORE-LAND** — RULES Testing law restated because RBX s40b paid for skipping it: the goal's own BY-SET gate runs BEFORE the commit, never one session after.
5. **END-OF-CONTEXT LAW, extended** — do not OPEN a hunt or a deletion you cannot close this session; mint the repro, route it, stop.

**SOLO-mode specifics (when overridden):** orientation reads every LIVE CURSOR; execute the highest-value unblocked rung on the whole board; LON QUEUE staffing items route to the solo operator; the streak breaker binds even harder — no peer seat exists to catch a stalled inheritance. **CONCURRENT-mode specifics:** the FIRE-AND-FORGET block below, unchanged — one live session per seat file, commit and push freely, git merges, semantic collisions caught mechanically by the claim gates. ⛔ **FIRING PREREQUISITE:** new seats orient from ORIGIN — never fire a fresh seat while ruling/cursor commits sit unpushed, or day one re-runs the stale-inheritance failure this section exists to kill.

## ⛔⭐⭐⭐ EXECUTION MODEL — FIRE-AND-FORGET (s32; RULES 2026-08-10 applied to this plan: no windows, no waiting, no human scheduling. Supersedes every "solo" / "‖" / "SERIAL, one seat at a time" reading below.)

**LON'S ENTIRE JOB: keep FIVE sessions alive, ONE PER SEAT FILE, re-fired with the same line whenever one ends. Nothing else — no who/what/when decisions. The files route the work.**

| fire with (verbatim) | file the session owns |
|---|---|
| `here we go — RBP seat, GOAL-RBP-EARN.md` | `GOAL-RBP-EARN.md` |
| `here we go — BOARD seat, GOAL-SN4-HOME-BOARD.md` | `GOAL-SN4-HOME-BOARD.md` |
| `here we go — LOWER seat, GOAL-SN4-HOME-LOWER.md` | `GOAL-SN4-HOME-LOWER.md` |
| `here we go — WIRES seat, GOAL-SN4-HOME-WIRES.md` | `GOAL-SN4-HOME-WIRES.md` |
| `here we go — RBX seat, GOAL-SN4-HOME-RBX.md` | `GOAL-SN4-HOME-RBX.md` |

**THE ONE INVARIANT (the only scheduling rule in the plan): ONE LIVE SESSION PER SEAT FILE.** Two sessions in one file is the s38b race. Everything else is git.

**SELF-GATING PROTOCOL — every session, at orientation and before every rung:**
0. ⛔ **TOOLING FIRST — `bash /home/claude/SCRIP/scripts/install_system_packages.sh`.** One authority, idempotent, seconds when already present, and it prints whether `gdb` is live. **`gdb` is MANDATORY** — RULES.md MONITOR-FIRST step (2) *is* a gdb breakpoint with a spin/ignore counter, so a seat without it cannot run the prescribed hunt and will hand off half-localized defects instead of fixing them. ⛔ **Never hand-run `apt-get install gdb`:** bare apt pulls gdb's Recommends (`libc-dbg`) against a container apt index baked at image-build time, that version has been superseded and deleted from the mirror, and it 404s — on a package gdb does not need. **This trap cost RBP-EARN seven sessions (s33–s39)**, each one re-concluding "gdb is unavailable in this container" and recording it as fact. The script does `apt-get update` first and passes `--no-install-recommends`. Runtime `rt_*` symbols live in `out/libscrip_rt.so` and need `set breakpoint pending on` — "Function not defined" is dynamic linking, not a broken gdb. **If any tool you need is genuinely absent, ADD IT TO THAT SCRIPT in the same push — never work around it silently, and never leave the next seat to rediscover it.**
1. `git pull --rebase` every repo; read YOUR file's LIVE CURSOR and any `UNBLOCKS:` lines pushed since.
2. Walk YOUR rungs top-down. A rung carrying a ⛔ REQUIRES line: evaluate its predicate against the repo (one command, stated on the rung). TRUE ⇒ run it. FALSE ⇒ **skip DOWN — never wait, never park** (RULES). If the missing prerequisite is UNCLAIMED anywhere, doing it yourself IS your next rung — first push wins, the duplicate seat pulls and consumes (the s38b concurrent-repair pattern).
3. Own ladder exhausted, or every remaining rung predicate-false ⇒ **pull the top unclaimed POOL item** (below); claim it with a cursor line in the same push.
4. Every handoff cursor ends with **`UNBLOCKS: <seat> <rung>`** naming what your landing opened.
5. **Floors & controls — THE STALENESS LAW (s32b):** every published number is hash-stamped and STALE the moment another seat pushes — that is normal, not a defect, because **GATES RE-MEASURE; FILES RECORD.** Your per-rung A/B control is ALWAYS your own open-state, measured at your own HEAD and re-proved after every rebase — never a number transcribed from BOARD's file. BOARD's floors are the RATCHET: at close, re-RUN the instrument at your HEAD and hold ≥ floor **BY SET, never by count** (sets compose under concurrency — a program another seat broke appears in your set-diff with your diff clean of it; FINDING + bisect assigns the owner). The EARN-2 census works identically: `unearned==0 && owed==0` is evaluated by RUNNING the script at your HEAD; its committed output expires on the first frame-moving landing by its own rule. ⛔ Never quote an m4 number without the 30-second liveness check — **and the check is "at least one probe PASSES", NEVER "returns non-empty"** (BOARD s33 / FINDING-2026-08-12c: the non-empty form passed continuously through a two-day total m4 outage, because 159 failing probes each print a non-empty `got =[]` line; a dead mode is not a quiet one). Run `MODE=compile bash corpus/probe/bb/run_suite.sh X12` — X12 and `zleak_matchbegin_stfh` are the only m4 survivors at the s33 hash, so a green there is the cheapest true liveness signal. Dark ⇒ m3-only, say so — and B-0/B-0b are fair game to claim.

## THE POOL (unclaimed work for any seat whose ladder is exhausted or blocked; disjoint surfaces by construction; claim = cursor line, first push wins)
1. **DEFER-LATCH** — `g_star_peek` → per-site resolution (`pattern_match.c` only; witnesses `140`/`141`, RED m3 rc=139 / PASS m4 — two-sided for free). Authority: GOAL-SNOBOL4-RTX row + s31 ledger.
2. **LADDER KW** — GOAL-SNOBOL4-BB KW-0..6 (acceptance = xc318 keywords-12 green both modes).
3. **CLIMB C-10 / C-11** — GOAL-SN4-ZETA-CLIMB (C-11 doubles as the EARN reentrancy stress suite).
4. **LADDER AB** — GOAL-SNOBOL4-BB AB-3..6. ⛔ REQUIRES (predicate): EARN-11 sole-writer landed AND EARN-7's completion greps green in the tree you arm.
5. **BOARD B-8 / B-7(iv)** — RTX instrument debts · witness promotions · BREAKX mint (if BOARD's session is deep in B-0..B-4).

## REGISTER CONTRACT OF RECORD (the HOME state)

| reg | role | authority |
|---|---|---|
| RSP | FORTH spine: box operands, ζ cells, choice/resume records — compile-time-constant offsets always | ZETA-MECH ONE-SYSTEM + LIFO law |
| RBP | EARNED frames ONLY (LAW: cell↔RSP distance non-constant at a reading site); ONE ENTER at α; `[rbp+ANCHOR]` chain to MATCH_BEGIN; α/ω SOLE writer; callee-saved ⇒ free across C | `GOAL-RBP-EARN.md` LAW + s28/s29/s30 rulings |
| RBX | GC heap-top / allocation frontier: inline bump-alloc in emitted code; GC honors rbx as frontier; today's DESCR mint pointer, formalized | `GOAL-SN4-HOME-RBX.md` |
| R12 | capture-pending arena TOP (mmap'd, STACK discipline — Lon s30b: *"Capture pending are in their own MMAP'd R12-topped arena"*); restored at backtrack re-entry (oracle pin W5); GC-visible | RBP-EARN s30b + EARN-5 (ONE AUTHORITY vs ζ-cell arm) |
| R10 / R11 | rΓ / rΩ wires, BOTH glue kinds, one product-wide convention; per-activation template-emitted saves; preserved or veneered at every C crossing | `GOAL-SN4-HOME-WIRES.md` (absorbs LADDER WREG + PT) |
| R13 / R14 / R15 | Σ subject base / δ cursor / Δ subject length-end — the match-state file ("match state collapses to four registers plus the frame", FINDING 08-02d); δ restore rides the choice record by design; ⛔ Σ/Δ save-restore across a NESTED match is an EARN-0b crossing row — verify on `161_pat_defer_fn_nested_match` watching r13/r15 (the LIFO check verified rsp/rbp only) | `x86_asm.h` literals + GOAL-SNOBOL4-BB FACT RULE; full 16-row map = HOME-RBX X-0 deliverable (s31) |
| R9 | GVA base (RTCC LIVE claim) | GOAL-RTCC |
| R8 + arg tier (rax rcx rdx rsi rdi) | RTCC slots; arg tier: claim it or stop paying for it (RC-8b) | **HOME-RBX X-5 (RC-8b/8c ADOPTED s31, gated on X-1)**; GC gap = HOME-RBX X-1; GOAL-RTCC stays law+history |

## HOME GATE — Definition of DONE (every line measurable; "100%" means THIS)

### ⛔ HONEST FLOOR TABLE — all suites at ONE hash, BOARD s41 (SCRIP `9780591d`-era build, corpus current). THE ONLY PLACE IN THIS PLAN WHERE EVERY SUITE IS SHOWN SIDE BY SIDE. Re-run, never re-quote — `GATES RE-MEASURE, FILES RECORD`.

| suite | m3 | m4 | ~% green |
|---|---|---|---|
| probe/bb (165) | 159 pass · 5 REG | 157 pass · 6 REG | ~96% |
| broad-336 | 260/336 | 255/336 · 6 SKIP | ~77% |
| bench-22 | ⛔ no m3 arm exists in the runner | OK=15 · FAIL=4 · CRASH=4 | ~68% |
| demo/15-board | 2/15 | 2/15 | 13% |
| beauty 17/17 | 0/17 | ⛔ instrument cannot invoke m4 at all | 0% |

⚠ **READ THIS BEFORE JUDGING A RUNG LANDED:** the numbers are monotone in integration level — per-construct probes are ~96% while the two suites that resemble real programs are 13% and 0%. **A rung measured only against probe/bb will look green while HOME is far away.** Name at least one integration board in every cursor, even if unchanged. Full analysis + open questions: `GOAL-SN4-HOME-BOARD.md` §BOARD'S READ OF THE PLAN (s41).

1. probe suite · crosscheck/patterns · xc318 · broad-336 · demo board (honest denominator — fence-dupe fixed) · bench-22: **oracle-green BY SET, BOTH modes, m3 ≡ m4 outputs byte-identical**; xfail only where oracle-blessed (p.123 stack-overflow class, `-s` remedy).
2. EARN-2 census: **`unearned == 0 && owed == 0`**; emitted frame count == classifier output exactly.
3. Gates strict: claim gate DATA-DRIVEN over {rbx r9 r10 r11 r12 + tiers}; **zero r10/r11 scratch anywhere incl. RTX hand asm**; RC-8a GC coverage green; TEMPLATE-ONLY + BOTH-MEDIUM greps == 0.
4. Deletions complete: BLOB-GRANT pins · CLASS-D `{res,rbp}` records + res stubs + ω absolute unwind + scanfail whack · legacy ARBNO arm · every dead killswitch · **`g_blob_ctx`/`rt_blob_ctx_ptr` grep == 0** (largely discharged by `0970838f` g_zctx per-activation base stack — the gate VERIFIES, never assumes).
5. Monitor sees the classes it has been dark on: stdout-only divergence (MON-CAP) + table-element-assign VALUE events. `handoff_status.sh` prints COMPLETE.
6. **BEAUTY:** the `beauty_suite` drivers green BOTH modes AND `demo/beauty/beauty.sno` byte-identical to oracle — **Milestone-1's md5 `abfd19a7a834484a96e824851caee159` re-proved at HOME** (any delta must be Lon-blessed as an oracle-behaviour change).
7. **RE-ENTRY EDGE INVENTORY CLOSED (s31):** every RBP/R12 restore edge enumerated and INDIVIDUALLY witnessed — backtrack β per choice class (arena pin W5: verify, never assume) · ω unwind · FENCE whack · scanfail · ABORT drain · unanchored retry bump · **NRETURN · direct Goto `:<C>` into CODE() blocks · SETEXIT traps** (manual Ch.9/19 non-local transfers — named in no seat file before s31). One missed edge = the FF-0 class. Deliverable rides EARN-3 (see GOAL-RBP-EARN s31 cursor).

## INSTRUMENT MAP (scanned 2026-08-12 s30 at corpus `5c17de98` — every suite, its runner, who consumes it)

| suite | where / size | runner | consumed by |
|---|---|---|---|
| **BB probe suite** | `probe/bb/probes/` — **163 .sno**; prefix families A=13 D=13 F=6 G=27 H=31 L=20 **N=33 (ARBNO)** X=12 f=4 t=3 z=1; `SUITE.md` is the row authority | `SCRIP/scripts/run_suite.sh` both modes (⛔ m4 arm DARK → B-0 first) | UNIVERSAL per-rung BY-SET gate. Family→seat: N → RBP/EARN-4 · D (D06/D12/D13 recursion) → RBP + WIRES W-2 · F/f + 151 + fence_probe → RBP FENCE rows · X (defer×DEFINE) + A → P3 AB · G/H/L broad |
| **Named witnesses** | `probe/` top — `arb1` (⛔ EARN-4's NAMED gate, T1+T2) · `w_cap_*`×6 + `mv_*`×2 (⛔ EARN-5's BY-NAME gate) · `dc_*`×5 (**`dc_recur` = the W-5 flip witness**, MECH bulletin) · `pb_*`×4 (LADDER PB) · `pt_inline_*`×3 (PT/WREG-5 gate) · `ab_*`×11 (P3 AB) · `rtx11_dynvar*`/`rtx_func_11*` (RBX X-2) · `uw2/uw3` (unwind) · `z4_*`×5 | sbl `.ref` beside each | seat-specific acceptance, cited by name in rungs |
| **earn0 witnesses** | `probe/earn0/` — **16 .sno** (s29 defect set + s30 pending-lifetime pins W1–W5) | refs oracle-baked | RBP monitor hunt · LOWER L-0..L-2 · ANY arena change (W1–W5 = acceptance) |
| **crosscheck ≡ xc318** | `crosscheck/**` — 34 dirs, **318 .sno EXACTLY** (the sum IS xc318): `rung2..rung11` + `rungW01..07` = the rung suites · patterns **122** · capture 9 · **gc 15 → RBX** · keywords 12 (LADDER KW) · **functions 10 → P3 AB/EARN-8** · strings 17 · library 4 · arith 10 · assign 8 · control 8 · data 6 · output 8 · concat 6 · hello 4 · coverage 1 | `board_patterns_set.sh` (patterns, BY SET, watch the BROKEN set); ⛔ B-1 names ONE sanctioned runner per remaining dir — and pins the broad-336 / 622-sweep denominators to a SCRIPT, not lore | phase-boundary floor both modes; patterns+capture are RBP/LOWER per-rung gates |
| **DEMOS** | `programs/snobol4/demo/` — **24 .sno**: the 15-board = {claws5, json, calculator-1, calculator-2, treebank}×{base, -match, -match-fence} (+ treebank-array/-list); plus roman · porter · wordcount · counter · arithmetic · expression · pattern_test · hello | `board_sno15_ident.sh` (**the ONLY sanctioned demo correctness instrument**) · `board_sno15_perf/perf2.sh` · `board_demos_zeta.sh` · oracle-ms baselines on record (json-match 34ms · treebank-match 10ms · treebank-array 8118ms · calc-1 55ms) | ⛔ **CORRECTED s39: 2/15 is the PASSING count** (claws5-match, claws5-match-fence), 13/15 BROKEN. ⛔⭐ **FURTHER CORRECTED s43 (FINDING-2026-08-12n): THE 13 ARE NOT ONE BUG AND MUST STOP BEING COUNTED AS ONE.** At least THREE mechanisms, gdb-separated: **(a)** calculator-1/2 + their 4 match variants (~6 programs) = **resumable-generator-through-a-defer, which `lower_snobol4.c:1182` documents as DELIBERATELY UNIMPLEMENTED** (its own named witnesses 178/179/182 still hang today — verified) ⇒ a FEATURE gap on nobody's ladder, see BOARD s43 §SCOPE HOLE; **(b)** treebank-array = unchecked ~16MB R12 capture-arena exhaustion, deterministic one-past-the-end write, crashes on its SIMPLEST input line; **(c)** the beauty/FUNC-11 wild-`rbx` class. All three can land `rip` in the anonymous JIT slab — **`rbx`/`r12` mapping status is the discriminator, NOT the crash PC's section.** ⇒ "EXPECTED restored by EARN additions" is unsupported for (a) at minimum. This board is the plan's most legible progress meter, and it currently reads BADLY, not nearly-done · P4 timing board |
| **BENCHMARKS** | `benchmarks/snobol4/` — 23 .sno, 1 xfail ⇒ **22 graded** | `test_bench_snobol4_modes.sh` (post-09f floor OK=17) + `bench_sno_*` + `build_benchmarks.sh` | perf floor **"18/22 hold-or-better"** (BB DoD, carried) + CRASH-class tracker · RBX X-3 perf proof |
| **BEAUTY** | `programs/snobol4/demo/beauty/beauty.sno` (Milestone-1 flagship) + `programs/snobol4/beauty_suite/` + `smoke/beauty_compiled.sno` | `test_gate_sn7_beauty_self_host.sh` · `test_monitor_beauty_smoke.sh` · `test_gate_em_beauty_subsystems_mode4.sh` · `test_interp_broad_corpus_and_beauty.sh` | ⛔ **17/17 drivers SIGSEGV at HEAD (FUNC-11, one include)** ⇒ **RBX X-2's ACCEPTANCE**; the flagship byte-identity is **P4's seal (HOME GATE line 6)** |
| **lib/** | `case.sno` · `string.sno` · `math.sno` · `stack.sno` | exercised via demo/xc customers | LOWER L-3 (`test_case` is a splice customer) · L-5 (`test_string`) |

## PHASES — DEPENDENCY MAP ONLY (s32: NOT a schedule; the only gates are rung-level ⛔ REQUIRES predicates; the "solo"/"‖"/"SERIAL" wording below is legacy shape, non-binding — see EXECUTION MODEL)

- **P0 — BASELINE (BOARD seat, solo, opens immediately):** m4 harness repair → floors re-proved BOTH modes at ONE hash → EARN-2 census re-cut to UNEARNED/OWED (⛔ standing law: BEFORE any frame-moving rung; also settles 557-vs-263) → discriminating refs (the 10 unclearable + polarity siblings) → claim gate data+strict. **Output = the floors every later seat judges BY SET against.**
- **P1 — ‖ FOUR SEATS (disjoint file surfaces):** **RBP** (GOAL-RBP-EARN): MONITOR-FIRST on `earn0_disc_arbno_star_fence_positive` → EARN-1 dormant → EARN-3 anchor → EARN-4 ARBNO-from-scratch (discharges ruling (c) by execution; witnesses N22–N33 + arb1 T1/T2 + 151) ‖ **LOWER** (HOME-LOWER): Defect A → B → C-9 residuals → 061 ‖ **WIRES** (HOME-WIRES): claim sweep incl. asm → ZCTX r10/r11 scratch eradication → guard unification → WREG mechanism DORMANT ‖ **RBX** (HOME-RBX): contract → RC-8a → FUNC-11 allocation instrumentation → fix.
- **P2 — ‖ THREE SEATS:** **RBP**: EARN-5 (ONE AUTHORITY: ζ-cell vs arena; W1–W5 acceptance) + EARN-6 (MATCH_BEGIN/FENCE conditional; FENCE(P) row classified) ‖ **WIRES**: PROC-shim delete (PT) + **WREG FLIP — ⛔ REQUIRES EARN-1 + EARN-3 LANDED** (EARN-10 ordering: pass-thru with zero frame is only correct once needy constructs earned theirs; the old 19-SEGV+7-HANG residual is EXPECTED cured — measure, never assume) + RTCC re-entrant preservation + default-ON revalidated (kill the m4-130 class) ‖ **RBX**: inline bump-alloc arms + ZHP-exhaustion re-check post Defect B.
- **P3 — SERIAL, one seat at a time, FULL RUNWAY each (a half-flipped sole authority is a broken tree by construction):** EARN-11 α/ω sole-RBP-writer flip (dormant byte-identical → per-node arming) → EARN-7 residue sweep (CLASS-D scaffolding, BLOB-GRANT pins, legacy ARBNO remnants) → LADDER AB call path (`fn_cell` jmp; RTX call asm) → EARN-8 STATEMENT/FUNCTION re-exam (ruling (d) becomes DECIDABLE here, with EARN-7 measurements in hand).
- **P4 — SEAL:** full-suite sweep · killswitch deletion · regen ×N · census seal · FINDINGs · handoff per FACT RULE.

## SEATS

| seat | file | absorbs / owns |
|---|---|---|
| RBP | `GOAL-RBP-EARN.md` (existing — the EARN ladder IS the plan) | EARN-0..11, ARBNO, FENCE rows, 151, D12/D13 recursion class |
| LOWER | `GOAL-SN4-HOME-LOWER.md` | s29 Defects A/B, CLIMB C-9 residuals, 061, test_string |
| WIRES | `GOAL-SN4-HOME-WIRES.md` | LADDER WREG + LADDER PT (from RBP-EARN, by reference), MECH M-1c guards, RTCC wire half |
| RBX | `GOAL-SN4-HOME-RBX.md` | rbx contract, RC-8a, RTX-FUNC-11, inline alloc, arena GC visibility |
| BOARD | `GOAL-SN4-HOME-BOARD.md` | EARN-2 census, floors, refs/witness hygiene, gates, m4 harness, MON-CAP — **PLUS the demo/bench REPAIR incl. compiler bytes, and minimal-reproducer isolation (Lon rulings (2)+(3), s41b)**. ⛔ **THE "ZERO compiler bytes ever / collision-free by construction" EXEMPTION IS REPEALED** — named here so a session orienting from memory cannot re-import it. BOARD is now subject to §COLLISION PINS like every other seat (can collide with RBP on `emit.cpp` frame arms, WIRES on ZCTX/push-pop guards, RBX on alloc arms), and owes RULES.md handoff step 4 (`.s` regen) whenever it touches codegen. Flagged by BOARD s41b, which deliberately left it rather than rush the master's partition rationale on ~8% context; fixed s43 (Claude Sonnet 5) — starting the demo/bench SIGSEGV repair now. |

Legacy goals (SNOBOL4-BB · SNOBOL4-RTX · RTCC · ZETA-MECH · ZETA-CLIMB) remain HISTORY + law authority; their open SNOBOL4 items are absorbed above; their Icon/Prolog scope is untouched.

## COLLISION PINS (named in advance — this is why the partition works)

- **`emit.cpp` frame arms:** RBP seat lands EARN-1/3/4 there; WIRES must NOT cut those arms before P3/EARN-11 — the s12 "highest collision surface" note is now an ORDERING LAW. **s31 extension:** the pin covers the ZCTX sequences and the push/pop guard pair (emit.cpp:2373/2806) — W-1/W-2 edits sit adjacent to the α/ω authority EARN-11 later claims. Under the CONSOLIDATED seat this is internal sequencing; on any re-fan-out it is a named pin.
- **Arena record layout (+16B wire-pair slot, WREG-3):** WIRES OWNS the layout; RBP/EARN-5 CONSUMES. One authority — the CAP-SYM lesson.
- **`x86_asm.h`:** encoder ADDS only (TEMPLATE-ONLY law); any seat may add, none may reshape.
- **RTCC veneer ↔ wires:** safe config = RTCC-ON **AND** wire capture/restore — neither alone (s14 arbitration). WIRES owns the pair.
- **Floors/census:** ONLY BOARD re-cuts instruments; every other seat consumes and cites.

## ADOPTED / PARKED LEDGER — s31 CONSOLIDATION AUDIT (legacy work the seat files did not carry, now assigned or explicitly parked; audit FINDING-2026-08-12b)

- **LADDER KW** (GOAL-SNOBOL4-BB KW-0..6, keywords native): **ADOPTED, P3.5** (after EARN-11/EARN-7, before P4 seal). Acceptance = the xc318 keywords-12 dir green both modes — HOME GATE 1's implied requirement made explicit. Authority stays the BB file. KW-5's native `&STLIMIT`/`&STCOUNT` also feeds the monitor (BOARD-adjacent).
- **DEFER LATCH** (`g_star_peek` → per-site resolution; GOAL-SNOBOL4-RTX row): **ADOPTED, P1-concurrent** — `pattern_match.c` only, zero collision with any seat surface. Witnesses `140_pat_eval_double_fn_trick`/`141_pat_eval_double_fn_arbno` (RED m3 rc=139 / m4 PASS — a two-sided gate for free) promoted to the named-witness layer (BOARD B-7(iv)). Manual-proven structurally wrong (Ch.7 p.86 + Ch.9 pp.122–3: deferred eval RE-ENTERS deferred eval; a one-entry name-keyed latch is guaranteed clobbered). Same single-cell disease as `g_blob_ctx`/`g_rtcc_block`.
- **MECH S-LADDER** (M-SLEN S0–S5 incl. S4 register-only MATCH_BEGIN α): **RIDES EARN-6** (RBP seat) — S4 is EARN-6's implementation arm, never orphaned. Authority GOAL-SN4-ZETA-MECH.
- **CLIMB C-10 / C-11** (data+keywords witnesses; EVAL/CODE/EXEC summit incl. the 1016/1019/161 gatekeep class): **ADOPTED, P3.5.** C-11 doubles as the EARN REENTRANCY STRESS SUITE — EVAL/CODE re-entry is exactly what earned frames + the R12 arena must survive. Authority GOAL-SN4-ZETA-CLIMB.
- **RTCC residue:** RC-8b/8c **ADOPTED at HOME-RBX X-5** (gated on X-1); RC-5 anchor re-open + RC-7 fold **PARKED** in GOAL-RTCC pending Lon + X-1.
- **RTX perf ladders** (RTX-4/6/9/10/12): **PARKED BY DESIGN** — correctness first; HOME GATE 3 already pulls the RTX hand-asm surface into W-0/W-1. RTX instrument debts adopted at **BOARD B-8**.
- **LADDER PB: CLOSED pre-consolidation** (all rungs `[x]`, BB cursor 07e "LADDER PB CLOSED") — PLAN.md's row is stale by design; do NOT reopen. Its `131` residual (`pat_static=0` 528B UCLAIM class) flows to EARN-7/M-3 deletion.
- **BB demo-board bisect** (`d2328f81..942ef1b1`, predicate `/home/claude/bisect_tb.sh`, witness treebank-match rc=139): **HELD AS FALLBACK** — P2's prediction is EARN restores the FF-0 defer members; if the 15-board does not recover, the bisect is the instrument, not a re-derivation.
- **Milestone-2** (stage2 self-host): explicitly **OUT OF HOME SCOPE** — GATE 6 re-proves Milestone-1 only.

## ⭐ LIVE CURSOR — 2026-08-12 s42 (Opus 5) — **TOOLING MADE MECHANICAL + TWO STALE MASTER FACTS CORRECTED. ZERO COMPILER BYTES.**

**SELF-GATING PROTOCOL GREW A STEP 0 (TOOLING FIRST).** `scripts/install_system_packages.sh` is the one authority; it now runs `apt-get update` (never did before) and installs `gdb --no-install-recommends`. **RBP-EARN s33–s39 lost seven sessions to a stale apt index** — bare `apt-get install gdb` pulls Recommends `libc-dbg`, whose indexed version was deleted from the mirror, 404s, and each seat concluded "no gdb in this container" and passed it on. libc6-dbg is not a gdb dependency. MONITOR-FIRST step (2) is now available to every seat; any seat carrying the old lore should re-test. **New standing rule in step 0: a genuinely missing tool gets ADDED TO THAT SCRIPT in the same push — never worked around silently.**

**§SEATS BOARD ROW CORRECTED** — the repealed "ZERO compiler bytes ever / collision-free by construction" exemption is struck and named as struck (Lon rulings (2)+(3), recorded in BOARD s41b, which flagged this row and deliberately left it on ~8% context). BOARD now carries demo/bench repair incl. compiler bytes, is subject to §COLLISION PINS, and owes RULES step 4 regen when it touches codegen.

**⛔ THIS FILE'S OWN CURSOR WAS STALE AND SHOULD BE READ AS A WARNING:** the s32 cursor below says *"P0 STILL UNOPENED"* while BOARD's file had reached s41b and this file's own §HONEST FLOOR TABLE is stamped BOARD s41. A seat orienting from the master's cursor rather than the seat file's would have been eight sessions behind. STALE-ORIENTATION (b) already says trust the seat cursor — this is the measured instance.

**NOT DONE / DELIBERATELY LEFT:** no rung executed, no watermark re-measured (zero compiler bytes ⇒ no number of mine to claim), RULES step 4 regen NOT APPLICABLE and not run.

## ⭐ LIVE CURSOR — 2026-08-12 s32 (Fable 5 — EXECUTION MODEL landed: fire-and-forget, five sessions one-per-seat-file, self-gating REQUIRES predicates + THE POOL; no human scheduling exists in this plan. The s31 audit facts below stand unchanged. ZERO compiler bytes.)
P0 STILL UNOPENED; first seat BOARD (B-0 m4 harness repair first). **s31 = the consolidation audit** (`FINDING-2026-08-12b-CLAUDE-FABLE5-SN4-HOME-CONSOLIDATION-AUDIT-…md`): the EARN scheme VERIFIED as frame-pointer-on-demand (alloca/VLA discipline) + side arena — sound, taxonomy total, conditional on (i) reads-based census incl. glue reads, (ii) the closed re-entry edge inventory (new GATE line 7), (iii) GC coverage (X-1). Ledger above minted; register contract completed (R13/R14/R15 rows; REGISTER-LAYOUT.md's r12=ζ row bannered STALE); RC-8b/8c → RBX X-5; defer-latch → P1; KW + C-10/C-11 → P3.5; three obligations attached to EARN rungs (RBP-EARN s31 cursor). Fingerprints at s30 mint stand: SCRIP `fc5b0754` · corpus `5c17de98`+witnesses · x64 `5035571`. Ruling ledger unchanged: (a) RULED s30/s30b (arena stands) · (b) OPEN, zero-cost · (c) discharged by EARN-4 execution when P1-RBP runs it · (d) decidable at P3.
