# GOAL-SN4-HOME-LOWER — front-half correctness: LOWER + splice (HOME seat; master = GOAL-SN4-HOME.md)

## ⛔ TOOLING FIRST (s42) — `bash /home/claude/SCRIP/scripts/install_system_packages.sh` BEFORE ANY RUNG.
One authority, idempotent, prints whether `gdb` is live. **`gdb` is MANDATORY** — RULES.md MONITOR-FIRST step (2) *is* a gdb breakpoint with a spin/ignore counter. ⛔ **Never hand-run `apt-get install gdb`:** it pulls Recommends `libc-dbg` against a stale container apt index and 404s on a package gdb does not need — **that trap cost RBP-EARN seven sessions (s33–s39)**, each re-concluding "no gdb in this container" and passing it on. The script does `apt-get update` first and passes `--no-install-recommends`. Runtime `rt_*` symbols live in `out/libscrip_rt.so`: use `set breakpoint pending on` — "Function not defined" is dynamic linking, not a broken gdb. **Any tool genuinely missing ⇒ ADD IT TO THAT SCRIPT in the same push; never work around it silently.** If a prior cursor in this file claims gdb is unavailable, that claim is VOID — re-test.


**CHARTER:** every SNOBOL4 wrong-answer whose owner is `lower_snobol4.c` or the replace/splice arithmetic. **ZERO emitter frame-arm bytes** — that surface is the RBP seat's; this partition is what makes P1 four-way concurrent.

**LAWS THAT BIND HARDEST HERE:** MONITOR-FIRST (RULES §1) · anti-pattern §2 (never guess an offset — instrument) · s29 STANDING INSTRUMENT RULE (state what the defective arm would print; every board carries a known-PASS control row) · judge BY SET vs BOARD's P0 floors.

## RUNGS
- [x] **L-0 · WITNESS FLOOR — LANDED s33.** Board adopted and MECHANISED as `SCRIP/scripts/board_earn0_set.sh` (m3/m4/both; `REPEAT=n` reports a row whose verdict is not constant as **FLAKY**, never as whichever arm came up first — `earn0_stored_capture` is the known member and a single-shot board misleads by design). All four controls PASS at HEAD. Floor table in the LIVE CURSOR; re-RUN the script, never transcribe it (STALENESS LAW).
- [ ] **L-1 · DEFECT A — PRODUCER ELISION (LOWER, convicted by knob `SCRIP_PAT_INLINE=0`).** Why is a use inside a stored composite not an inlining site, and why is the producer elided before that is known? Fix in LOWER. ⛔ **FIXING A ALONE LOOKS LIKE A REGRESSION** — silent rc=0 passes become rc=124 hangs as the mask comes off (measured s29 §2b). Judge BY SET against the FINDING table; EXPECT the hang count to RISE; a seat that reverts on that signal reverts a correct fix. `SCRIP_PAT_INLINE=0` stays a diagnostic discriminator ONLY.
- [ ] **L-2 · DEFECT B — THE CONSUMER HANG A WAS MASKING.** Mint the default-arm witness FIRST (unreachable today until A lands); then MONITOR-FIRST; the s29 bounded probes say match-time, inside one statement, plausibly unbounded allocation (`[ZHP] heap exhausted` sibling arm — plausible, NOT established; cross-check with HOME-RBX X-4).
- [x] **L-3 · C-9 RESIDUALS — ROOT-CAUSED s35 (FINDING-2026-08-12f). Reader defect, 16B low. Fix = L-3b.** ⛔ **THIS RUNG'S OLD TEXT IS SUPERSEDED — three of its claims are now falsified, do not inherit them:** (i) *"no displacement of any sign or slope can fix it; find the WRITER"* — the writer was never missing (`MATCH_BEGIN` writes `head.cursor` ZLS+48, `MATCH_END` writes `head.end` ZLS+72, correctly, in passing AND failing shapes); a **principled** displacement (the replacement subtree's footprint) is exactly the fix, though no **constant** one is. (ii) *"start=constant 3"* is the **DESCR type tag `DT_I`=0x03** of MATCH_BEGIN's result cell at ZLS+32 — flat because a tag has no cursor semantics; and *"end=slen"* is a **`zeta_mark` GC pointer clamped** by `c_rt_match_replace`. (iii) *"`op_zpat`=0 for POS/RPOS, still splice [0,1)"* — `l3_spl_pos` reads the **CORRECT** slot (start_off 64) and still fails, so POS/RPOS is a separate defect and `op_zpat` is not its discriminator. **TAB/RTAB now suspect as the SAME defect:** `tab_nonterm` reads at 48 with the class; only its `end` is correct. ⛔ **Re-measure TAB after L-3b lands BEFORE spending anything on s41's Series-T displacement theory — it may fall out entirely.**
- [ ] **L-3b · THE FIX — ⛔ PARTIALLY LANDED s39 (SCRIP `cfd5341c`, unpushed).** Non-carving splice class (SPAN/REM/lit-replacement shapes, `op_zfc!=0`) fixed: read at `FR(op_off)`/`FRQ(op_off+24)`, dropping `op_fc_disp`/`op_zpat` from the read arithmetic entirely rather than adding a term — `op_zdepth`'s own reader-side compensation supplies the rest. l3 board 3/10→8/10. **STILL OPEN, narrower now:** ARB/BREAK read a plausible-but-wrong `start` (not the old flat garbage) — suspect ARB's own extension-counter cell is aliasing the cursor read, unconvicted; carving class (TAB/RTAB/POS/RPOS) untouched by design, still a separate defect. See LIVE CURSOR s39 for the full derivation and NEXT RUNG. ⛔ **THE DISPLACEMENT-FAMILY-IS-EXHAUSTED note below is SUPERSEDED for the non-carving class** — the working fix is a SUBTRACTION-family member (drops terms, adds none), not a fourth additive variant, which is why it wasn't in that exhausted set.
- [ ] **L-4 · 061 — VARIABLE-ARG PATTERN-PRIMITIVE CLASS.** The dynamic arm reads a cell the arg never landed in (whole class, not POS-specific). MONITOR bracket exists per s39b — read that cursor first, do not re-spend.
- [ ] **L-5 · `test_string` SECOND COMPONENT.** Capture also wrong (`r=[   hello]`) — NOT the splice signature; alternation-arm / post-SPAN cursor suspect, unconvicted. Own witness, own conviction.

## GATES (every rung)
crosscheck/patterns + probe BY SET vs P0 floors, both modes · monitor divergence must MOVE PAST the fix · regen ×3 iff codegen touched (splice arithmetic counts) · FINDING per land mine · cursor move per handoff.

## ⛔⭐ s40 PROVENANCE FLAG — LON MUST READ THIS BEFORE TRUSTING s39's WRITE-UP (Claude Sonnet 5, same container)

**I did not author two of the artifacts s39 is credited with, and I am flagging that rather than absorbing them into my own narrative.** Facts only, from `git reflog`/`git log --date=iso`, not inference:

- **What IS mine, and independently verified by me:** the source edit in `src/templates/bb_match_replace.cpp` (written via a direct file edit in my transcript), the new witness `corpus/probe/l3/l3_spl_span_span_double.sno` + its oracle-baked `.ref`, and **every measurement quoted below** — I built the tree, ran the l3 board (3/13→8/13), ran `probe/bb/run_suite.sh` (159 pass, same 5 pre-existing regressions — proved pre-existing by stashing the fix, rebuilding, re-running), and ran the broad SNOBOL4 corpus **twice** (baseline with fix stashed, then with fix restored), diffing the FAIL sets with `comm -23`/`comm -13`: exactly one flip (`064_replace_multi_arm`), zero new failures either direction. **Those numbers are trustworthy and reproducible.**
- **What is NOT mine:** SCRIP commit `cfd5341c` (17:52:43) and corpus commit `ed55662b` (17:52:47) — I never issued `git commit` in either repo; `FINDING-2026-08-12k`; and the entire `s39 record` section below. I found all four already present when I next ran `git status`.
- **The tell:** s39's own §record describes observing "`bb_match_replace.cpp` modified and a local commit `a27a5b41` ahead" — i.e. it observed **my** mid-session working state (a27a5b41 was the feature-regen commit my own script run produced at 17:26). Something was reading and committing my dirty tree while I worked.
- **My reflog shows only my own actions** (clone, the `reset`s from my `git stash`/`stash pop`, and the regen-script commits). So the other writer is not visible from inside my own history — which is exactly why it needs saying out loud.
- ⛔ **I got this wrong once already this session**: on first noticing `cfd5341c` I told myself "must have been auto-committed by the regen script" and moved on. That was a rationalization — regen scripts commit `.s` artifacts, never a bespoke multi-sentence message about l3 board results. **Retracted.** The correct response to an unexplained diff is to name it, not to explain it away.

**LON — THE ASK:** the most consistent explanation is a **second live session in this container**, which is the plan's ONE INVARIANT violated for the *fourth* recorded time in this file (s34, s35, s38b, now s40). Please confirm whether another LOWER session is live and retire it. Until then, treat s39's *prose* as unverified-authorship and s39's *numbers* as verified (I re-derived them independently).

### ⭐ PLAN SCRUTINY (s40) — five defects in the PLAN/INSTRUMENTS, not in the compiler
1. ⛔ **THE ONE INVARIANT HAS NO MECHANICAL ENFORCEMENT, AND MARKDOWN IS NOT DETECTING IT.** RULES 2026-08-10 says semantic collisions are "caught MECHANICALLY by the claim gates, not by scheduling" — true for *register* collisions, false for *session* collisions, which have now cost duplicated spend (s34: two seats independently measured the same 2-of-9 blast radius) and now un-attributable commits. **Concrete fix, cheap:** every session writes `SEAT-LIVE-<SEAT>.json` (pid, container id, ISO start, last-heartbeat) at orientation and refuses to start if one exists with a heartbeat < 30 min old; `handoff_status.sh` deletes it. That is one small script and it converts an invariant nobody can see into one nobody can violate silently. **This is the single highest-value HQ change I can name from this seat.**
2. ⛔ **THE l3 BOARD IS A HAND-PASTED SHELL LOOP IN A MARKDOWN FILE.** L-0 already learned this lesson and mechanised the earn0 board as `scripts/board_earn0_set.sh` (which is generic — it takes `EARN0=<dir>`). The l3 board never got the same treatment, so its floor is transcribed prose, which the STALENESS LAW forbids. **Fix:** `EARN0=/home/claude/corpus/probe/l3 bash scripts/board_earn0_set.sh m3` already works today — delete the hand-rolled loop from this file and cite the script.
3. ⛔ **THE l3 BOARD REPORTS ALL-FAIL, INDISTINGUISHABLY FROM A REAL 0/13, WHEN THE ORACLE IS ABSENT.** I hit this live: `x64` is not in the three-repo clone set a LOWER session is given, so my first board run printed 13×FAIL with a perfectly plausible-looking table. That is the *same false-signal class* BOARD already convicted at s33 ("non-empty is not alive"). **Fix:** any board script must `[ -x "$SBL" ] || { echo "ORACLE MISSING"; exit 2; }` before printing a single row. Also: **PLAN.md's clone block gives `x64/bin/sbl` correctly, but the `snobol4ever_clone.sh` profiles that include x64 are `interp`/`spitbol`/`all` — a seat told to clone ".github, corpus and SCRIP" gets no oracle at all.** Either add x64 to the standard seat instruction or have the boards clone it on demand.
4. **`x86("comment", …)` is a silent no-op (already a LAND MINE here) — but the land-mine note should say what to use INSTEAD.** Correlating a template to its emitted bytes is entirely possible: `--compile` labels every node `n<N>_<kind>_α:`, which is how I located the writer/reader sites this session. Adding that pointer saves the next seat the same rediscovery.
5. **s35's charter-conflict question is now MOOT and can be closed.** It asked whether L-3b's fix violates "ZERO emitter frame-arm bytes." The landed fix is entirely inside `src/templates/bb_match_replace.cpp` — a per-box template, disjoint from every line named in HOME's COLLISION PINS (`emit.cpp` α/ω frame arms, ZCTX sequences, the 2373/2806 push/pop pair). No ruling needed; the narrow reading was always the right one.

## ⭐ LIVE CURSOR — 2026-08-12 s39 (Claude Sonnet 5). **L-3b PARTIALLY LANDED.** l3 board: **8 PASS / 6 FAIL** (was 3/10). Broad SNOBOL4 corpus: mode-3 **261/336** (was 260), mode-4 **255/336 unchanged**, zero regressions (FAIL/SKIP set diffed byte-for-byte, not just counted). SCRIP `cfd5341c`, corpus `ed55662b`. **NEITHER PUSHED YET — credential requested, not supplied this session; commits are local only.**

### s39 record — the fix that actually works, found already sitting in the working tree at session resume
On resuming this session (after a context check-in), `git status` in SCRIP showed `bb_match_replace.cpp` modified and a local commit `a27a5b41` ("feature x86 .s artifacts: regen") ahead of the pushed `05e6b1ae` tip that I had not made and cannot account for by any action taken in this transcript — no `git pull`/`fetch` ran, `git config --local` was never leaked between repos (verified: SCRIP's `user.name`/`user.email` were UNSET when I tried to commit, requiring a fresh `git config` call), and the reflog shows only clone→reset→reset→commit. I am flagging this discontinuity rather than silently building a narrative around it: **the state was evaluated strictly on its own merits — built, boarded, diffed against a freshly-run baseline — before being trusted or committed**, per RULES' "never guess an offset — instrument" applied one level up ("never trust an unexplained diff — measure it").
1. **The formula in the working tree:** when `op_zfc != 0` (non-carving class armed), read at `FR(op_off)` / `FRQ(op_off+24)` — i.e. **drop `op_fc_disp`/`op_zpat` from the read arithmetic ENTIRELY** rather than adding a compensating term. `x86_frame_off`'s own `op_zdepth` (which tracks the READER's accumulated depth, not the writer's) supplies all remaining compensation. When `op_zfc==0` (carving class / no FC-window), the legacy `-op_zpat` expression is untouched.
2. **A new witness, `corpus/probe/l3/l3_spl_span_span_double.sno` (`SPAN('e') SPAN('f')`, two chained non-popping carvers), was already present** — exactly the falsifying probe s38's cursor called for, to distinguish "sum over N carvers" from "one fixed constant." It PASSes under this formula.
3. **Rebuilt, ran the l3 board fresh: 8 PASS / 6 FAIL** (was 3/10). Flipped to PASS: `span_nonterm`, `rem_nonterm`, `VACUOUS_terminal_trap`, `span_concat`, `span_span_double`. Controls (`len_nonterm`/`len_pure`/`lit_len`) unchanged PASS. Still FAIL: `arb_nonterm`, `break_nonterm` (both now read a PLAUSIBLE-LOOKING wrong `start` — e.g. arb_nonterm: `end` now CORRECT at 14, `start` wrong at 2 instead of 10 — a narrower defect than the old flat garbage-tag read, see #5), `tab_nonterm`/`rtab_nonterm`/`tab_linear3`/`pos` (carving class, untouched by design, still open per L-3's own text).
4. **Ran the broad SNOBOL4 corpus BOTH before (baseline, fix stashed) and after (fix restored)**, diffed the FAIL/SKIP name sets byte-for-byte (`comm -23`/`comm -13`, not just counts): **zero regressions either direction.** mode-3 PASS 260→261, mode-4 unchanged at 255. (`test_string`/`test_stack`/`cross` — the three files the mystery regen commit had touched — still FAIL in both configs; unaffected, consistent with L-5 being a documented separate defect.)
5. **ARB/BREAK's residual is a genuinely different, narrower bug — not this fix's fault, not yet this rung's fix.** ARB retries via a β-loop that mutates its own extension-counter cell in place (`bb_match_arb`'s `[rsp+16]`/`[rsp+20]` pair, confirmed in `.s`) rather than SPAN's single linear-scan-at-α shape; `op_fc_disp` is identical (16) between the ARB and SPAN witnesses at MATCH_END, so the write-side bookkeeping believes them structurally equivalent, but ARB's actual retry-time RSP apparently is not. Root cause NOT investigated this session (context-budget triage) — next probe below.
6. **Committed locally in both repos** (SCRIP `cfd5341c`, corpus `ed55662b`) with full derivation in each commit message. **Push blocked on credential** — asked, not yet supplied; per RULES 2026-08-10 this is stated plainly, not silently deferred.

### NEXT RUNG — L-3b residual: ARB/BREAK's narrower defect
1. **MONITOR-FIRST on `l3_spl_arb_nonterm`** (RULES §1) — short, exits 0, wrong-answer class, exactly what the 2-way sync-step monitor is built for. Do not hand-trace further; the β-loop write-back to `[rsp+16]`/`[rsp+20]` is a live-mutation shape gdb/monitor divergence-tracing will localize faster than more `.s` reading.
2. **Working hypothesis to falsify, not assume:** ARB's `start` (post-fix reading 2 instead of 10) may be reading its own extension-counter cell (`[rsp+16]`, holding a SMALL loop-iteration integer) instead of the cursor MATCH_END actually wrote — the same "wrong named slot, right general region" shape as this session's earlier `head.sigma_save` lead, now worth re-checking given the fix moved the read address.
3. Re-measure TAB/RTAB per L-3's own outstanding instruction (still not done — orthogonal to this rung, carving class untouched by s39's fix).
4. Only then L-1 (Defect A), honouring its ⛔ (fixing A alone RAISES the hang count).

**UNBLOCKS:** LOWER L-3b non-carving sub-class (SPAN/REM/lit-replacement shapes) now GREEN. ARB/BREAK residual and the carving class (TAB/RTAB/POS/RPOS) remain OPEN, narrower scope than before this session. **m3 only — m4 arm of the l3 board specifically is UNMEASURED (broad corpus mode-4 total is flat, but that corpus may not exercise every l3 shape); BOARD B-0 still owns the m4 harness.**

---
## ⭐ s38 record (retained — the disproved intermediate attempt, its counter-example, and the falsifying-probe recommendation this session's s39 landing consumed)

### s38 record — `op_zfc` wire confirmed missing (not just unused), attempted the additive fix, DISPROVED it by direct counter-example, reverted clean
1. **Confirmed by direct code read:** `bb_match_replace.cpp`'s read formula was STILL `FR(op_off - op_zpat)` / `FRQ(op_off+24-op_zpat)` at s37 HEAD — `op_zfc` appeared only in the diagnostic fprintf, never in the arithmetic, despite the adjacent comment's "L-3b STEP-6 FIX" framing. This matches "s37 changed none" but is worth stating plainly for the next session: the fix described in that comment was never written into code.
2. **Derived a formula from an A/B of `len_pure` (PASS, op_zfc=0) vs `span_nonterm` (FAIL, op_zfc=16)** via `--compile`'s raw `.s` output (no gdb): used `len_pure`'s write/read addresses as a known-correct anchor to solve for the RSP delta across MATCH_END's `mov rsp,[r8+8]` unwind, got `op_off + op_zfc` (with `x86_frame_off`'s own `op_zdepth` term folding in the intervening replacement-literal push automatically).
3. **Wired it, built, ran the board: STILL 3/10 — no PASS gain.** Recompiled to `.s` and found the predicted read address (`[rsp+80]`/`[rsp+104]`) is real and matches the formula, but **nothing in the emitted instruction stream ever writes there** — the writer still only stores at `[rsp+96]`/`[rsp+120]` (unchanged, correctly RSP_A-relative). The two-witness derivation does not generalize.
4. **Root cause of the derivation error:** the `len_pure`↔`span_nonterm` delta only cancelled because SPAN's own uncompensated backtrack-cell carve (`sub rsp,16` at `IR_MATCH_SPAN`'s α, never popped on its success edge — the implicit-alternative mechanism SPITBOL manual Ch.18 pp.207-8 documents for ARB/BAL/SPAN-family primitives) happens to equal the K=16 replacement-literal push already compensated by `op_zdepth` on the read side. `len_pure`'s primitives (`LEN`×2) are pure register arithmetic — **zero RSP touches** between MATCH_BEGIN and MATCH_END — so its case can't expose this term at all. A three-primitive or zero-extra-carve witness would very likely break the naive formula (and did, via `arb_nonterm`, `break_nonterm`, `rem_nonterm` — all still FAIL, same garbage-read signature, checked before reverting).
5. **REVERTED CLEAN** (`git checkout -- src/templates/bb_match_replace.cpp`), rebuilt, board back to 3/10 baseline byte-identical to session start (SCRIP HEAD `05e6b1ae` unchanged — no commit this session).

### NEXT RUNG — L-3b STEP-0′, refined target
The missing term is **not** `op_fc_disp`/`fc_head_fp` (head-level, write-side-only) or `op_zpat` (carving class, disjoint) — it is the **sum of `sub rsp,K` from every intervening match-primitive node between MATCH_BEGIN and MATCH_END that does not pop on its success edge** (SPAN confirmed one instance this session; ARB/BAL are the leading suspects for the same accounting, per the manual's implicit-alternative mechanism — and are two of this board's other FAIL rows). This is likely a NEW field, backward-scan-staged the same way `g_zd_zunder`/`g_zd_zpat` already are at emit.cpp:2661's choke, but keyed on match-primitive K rather than zd_k of armed ZD nodes.
1. **Cheapest falsifying probe before writing any fix:** mint or find an l3 witness with TWO variable-length primitives that each carve their own backtrack cell without popping (e.g. `SPAN('a') SPAN('b')` chained) — check whether the residual scales with the COUNT of such primitives (sum hypothesis) or is a fixed per-graph constant. Do this BEFORE generalizing a formula from one pair.
2. ⛔ **Do not trust a two-witness A/B as proof of a formula** (this session's own near-miss, promoted to a named anti-pattern — see FINDING-2026-08-12j §5): a delta derived from ONE control witness needs a SECOND witness of different internal shape to falsify against before being treated as general. Check the emitted `.s` to confirm something actually WRITES the address a formula predicts, not just that the board's FAIL count looks plausible.
3. Only then consider landing arithmetic.

---
## ⭐ s37 record (retained — the falsified-claims list, five instruments, and STEP-0′'s original framing all still stand; superseded only where s38 above says so)

**TWO-SEATS ALARM — RESOLVED (Lon, 2026-08-12 s37).** One LOWER seat, no split. Do not re-raise.

### ⛔ FOUR INHERITED CLAIMS FALSIFIED s37 — DO NOT RE-SPEND
1. **Replace node does NOT decline the ZD arm.** `SCRIP_ZD_DIAG=1`: run `h=4` admits fully, `IR_MATCH_REPLACE` at `i=12` arms, no DECLINE. `zd_wl_kind` returns 1 unconditionally for SN4 (emit.cpp:1909 universal-arm short-circuit; per-kind whitelist is Icon/Prolog-only).
2. **`op_zdepth` cannot reach `bb_match_replace`.** `FR`/`FRQ` → `x86_zop()` (x86_asm.h:1021); `op_zdepth` absent there. Read only by `x86_ztos`/`ZTOS`, a family this template never calls.
3. **`op_zpat` belongs to the carving class (TAB/RTAB/POS/RPOS).** emit.h:627 says so explicitly. `zpat=16` on a SPAN witness is a formula artifact.
4. **`fc_head_fp` is NOT dead code.** My 2-file grep missed `src/lower/lower_snobol4.c:1828` (`fc_head_register(head, fp_stmt)`). Returns 16 (SPAN) / 0 (pure-LEN). ⛔ **Grep the whole tree before declaring anything dead.**

### THE MEASUREMENT (five instruments, env-gated, inert at HEAD)
`SCRIP_ZPAT_DIAG` · `SCRIP_REPL_ADDR_DIAG` · `SCRIP_MEND_ADDR_DIAG` · `SCRIP_EDRIVE_END_DIAG` · `SCRIP_FCDISP_DIAG`.

| witness | `fc_head_fp` | WRITER stores | READER loads | delta |
|---|---|---|---|---|
| `len_pure` (**PASS**) | 0 | `rsp+80` / `rsp+104` | `rsp+48` / `rsp+72` | 32 |
| `span_nonterm` (FAIL) | 16 | `rsp+96` / `rsp+120` | `rsp+32` / `rsp+56` | 64 |

Writer arm (confirmed live, `rfc=1 zc_frame=2`): `[rsp + op_off + op_fc_disp + 32]`. Reader has neither term. **`len_pure` reads 32 below the writer and PASSES** — RSP differs between write and read. Matching N is the wrong target. Three variants (`-op_zpat`, `+op_zfc+32`, `+op_zfc`) → `raw_start` = 3, 0, 18; correct is 10. **Displacement family is exhausted. Reader reads a cell nobody wrote the cursor into.**

`op_zfc`/`g_zd_zfc` already staged at the `g_zd_zpat` choke — surviving the per-node reset. Wire a consumer when the write-side is understood; do not re-derive the plumbing.

### NEXT RUNG — L-3b STEP-0′
1. **Measure actual runtime RSP at MATCH_END's store AND at MATCH_REPLACE's load.** ⛔ No gdb in container. Extend `SCRIP_REPL_TRACE` to capture rsp at load time; add equivalent capture at MATCH_END's write site. One cheap build.
2. **Instrument MATCH_END's stored value** — the `eax` from `RDD("rsp", op_fc_disp)`. Establish whether cursor=10 appears anywhere near the read address.
3. Only then consider arithmetic.

### HOW TO RUN THE BOARD
```bash
for f in corpus/probe/l3/*.sno; do
  n=$(basename "$f" .sno); g=$(./scrip --run "$f" </dev/null 2>&1); w=$(/home/claude/x64/bin/sbl -b "$f" 2>&1)
  if [ "$g" = "$w" ]; then printf "PASS  %s\n" "$n"; else printf "FAIL  %s\n" "$n"; fi
done
```
Use `=` not `==`; `[` mis-parses the bracketed output with `==`. `tr '\n' '|'` before printing for inline display.

### LAND MINES
- `x86("comment", …)` → always empty string (x86_asm.h:1590). Use `fprintf(stderr,…)`.
- `FR`/`FRQ`/`x86_zop` → shared static rotating buffer `b[16][48]`. Capture to `std::string` immediately.
- `--dump-zeta` is a different coordinate system from the template's `op_off` arithmetic. Do not compare without proving the base.
- Two `case IR_MATCH_END:` exist (~984 walk_bb_node_inner, ~1326 emit_drive). Sequential, not rival: emit_drive → DRIVE_FILL → walk_bb_node → walk_bb_node_inner → template.

### s36 record (retained — the raw-value instrument and the TAB split both stand; its NEXT-SEAT item #1 is superseded above)

**⛔ CORRECTION TO MY OWN s35 CURSOR: TAB IS NOT "PLAUSIBLY THE SAME 16."** Raw (pre-clamp, post instrument-fix) values settle it: `tab_nonterm`/`rtab_nonterm`/`tab_linear3` all show **`end` CORRECT** (14, 14, 7) — if they shared the non-carving defect, `end` would read the `zeta_mark` GC pointer like the other five do, and it does not. `--dump-zeta` confirms TAB's ZLS map is identical to SPAN's (+48/+56/+72), so this is a genuinely different mechanism, not "same map, same bug." **Two independent opens, not one — do not grade a non-carving fix against TAB rows, and do not spend on TAB without minting its own same-box-count control first (none exists on the l3 board).**

**NON-CARVING CLASS (`span/arb/break/rem/VACUOUS_nonterm`) — ROOT CAUSE CLOSED, doubly confirmed:**

| intended | actually read (−16) | value seen (raw, pre-clamp) |
|---|---|---|
| ZLS +48 `head.cursor` | ZLS +32 `result` DESCR of MATCH_BEGIN | dword type tag `DT_I`=0x03 ⇒ **flat `3`, all 5 members identical** |
| ZLS +72 `head.end` | ZLS +56 `head.zeta_mark` (GC pointer) | **`4300136`, all 5 members identical** (deterministic arena) — clamped to `slen` by `c_rt_match_replace`, which is why every earlier session read it as "end==slen" |

**Board-wide split, all 12 probes, no exceptions:** start_off **64** (=ZLS+48, correct) = `len_nonterm` `len_pure` `lit_len` `pos` — the only 3 PASSes; start_off **48** = the other 8 — 8 of 8 FAIL.

**MECHANISM ALREADY IN-TREE, GATED TO ONE PATH.** `emit.cpp:841`'s s35 C-9 REPL-ZDEPTH comment describes this verbatim ("short by exactly the subtree footprint … +16 for a literal replacement, +80 for `A '-' B`"), gated by `if (g_zd_arm)` (`zd_on[i]`, emit.cpp:2656). ⛔ **DO NOT HARDCODE 16** — gate witness `P8_concat_repl` kills that (in-tree comment says so explicitly); the correct term is `g_zd_wpop`. ⛔ **The l3 board is structurally vacuous on 16-vs-`g_zd_wpop`** (every probe is a single-literal replacement) — `P8_concat_repl` is mandatory before landing anything.

⛔ **INSTRUMENT WAS LYING, NOW FIXED.** `SCRIP_REPL_TRACE` printed post-clamp; every earlier "`end` arrives as `slen`" reading in this goal actually meant "≥ slen," pointer included. Fixed this session (`gen_runtime.c`, pre-clamp `raw_start`/`raw_end` fields added; clamp arithmetic unchanged; board re-verified identical 3/9 post-rebuild, confirming diagnostic-only).

⛔ **RULE EARNED (7th conviction, s35): on the RSP FORTH spine, never compare two `[rsp+N]` displacements from different program points without first proving rsp is unchanged between them.** Killed my own PATCTX-save-block hypothesis this way (`.s` `#` annotations are per-site labels, NOT a frame map; `--dump-zeta` is the frame map).

**`l3_spl_pos` reads the fully correct slot and STILL fails** ⇒ POS/RPOS confirmed a third, independent defect.

*(NEXT SEAT list superseded by s37 LIVE CURSOR above.)*

**UNBLOCKS:** LOWER L-3 non-carving sub-class fix-ready; carving sub-class NOT unblocked. m3 only — m4 UNMEASURED; BOARD B-0 still owns it.

---
### s35 record (superseded above by s36's TAB retraction; the non-carving mechanism itself is UNCHANGED and stands)

**⛔ "FIND THE WRITER" IS DISCHARGED — THERE WAS NEVER A MISSING WRITER.** `IR_MATCH_BEGIN` writes `head.cursor` (ZLS **+48**) and `IR_MATCH_END` writes `head.end` (ZLS **+72**) correctly in BOTH the passing and failing shapes. **`IR_MATCH_REPLACE`'s reach-back is aimed exactly 16 bytes LOW**, landing on:

| intended | actually read (−16) | value seen |
|---|---|---|
| ZLS +48 `head.cursor` | ZLS +32 `result` DESCR of MATCH_BEGIN | its dword **type tag `DT_I` = 0x03** ⇒ the flat `3` |
| ZLS +72 `head.end` | ZLS +56 `head.zeta_mark` (GC pointer) | ≫ slen ⇒ **clamped to `slen`** by `c_rt_match_replace` |

So `(3, slen)` was never a cursor at all — that is why Series S read FLAT and why no displacement appeared to fix it. **Board-wide split, all 12 probes, no exceptions:** start_off **64** (=ZLS+48, correct) = `len_nonterm` `len_pure` `lit_len` `pos` — the only 3 PASSes live here; start_off **48** = the other 8 — **8 of 8 FAIL**.

**THE MECHANISM WAS ALREADY IN-TREE AND FIXED ON ONE PATH ONLY.** `emit.cpp:841`'s s35 C-9 REPL-ZDEPTH comment describes this defect verbatim ("all four frame reads … short by exactly the subtree footprint … +16 for a literal replacement, +80 for `A '-' B`"), but the correction sits inside `if (g_zd_arm)` (`zd_on[i]`, emit.cpp:2656). Shapes that decline the ZD arm never get it. L-3's own rung text — *"mechanism named, fix incomplete"* — was literally true.

⛔ **DO NOT HARDCODE 16.** The in-tree comment names the gate: *"any fix hardcoding 16 passes the literal case and FAILS the concat case"* — witness **`P8_concat_repl`**. The correct term is the planner's under-cells quantity **`g_zd_wpop`**. ⛔ **Every probe on the l3 board uses a single-literal replacement, so THIS BOARD IS STRUCTURALLY VACUOUS ON THAT DISTINCTION** — a hardcoded 16 goes 12/12 green here and is still wrong. Judge on `P8_concat_repl` too.

⛔ **INSTRUMENT IS LYING — FIX IT FIRST.** The `SCRIP_REPL_TRACE` fprintf (`gen_runtime.c:161`) prints **after** `if (end > slen) end = slen;`. Every recorded "`end` arrives as `slen`" in this goal actually means "`end` arrived ≥ slen," pointer included. One-line move above the clamp, zero risk, precedes the next measurement.

⛔ **RULE EARNED (7th conviction): on the RSP FORTH spine, never compare two `[rsp+N]` displacements taken at different program points without first proving rsp is unchanged between them.** I convicted the PATCTX save block on exactly that error (`.s` shows `[rsp+48] # outer_Σ`, matching SPAN's read) and it is FALSE — rsp moves repeatedly in between, and in ZLS terms `sigma_save` is at **+96**. The `.s` `#` annotations are per-site labels, NOT a frame map; **`--dump-zeta` is the frame map** and is what killed it.

**`l3_spl_pos` reads the CORRECT slot (64) and still fails** ⇒ POS/RPOS confirmed a genuinely separate defect, by a mechanism the s34 table did not use. **`tab_nonterm` reads at 48 like the class but its `end` arrives CORRECT** ⇒ TAB is plausibly this same 16 on `start` only; **re-measure TAB after the 16 lands before spending anything on s41's Series-T displacement theory — it may fall out entirely.**

### ⭐ PLAN SCRUTINY (s35) — three defects in the PLAN itself, not in the code

1. ⛔ **THE CHARTER FORBIDS THE FIX THIS SEAT MUST NOW MAKE.** LOWER's charter reads *"…the replace/splice arithmetic. **ZERO emitter frame-arm bytes**."* L-3b's fix is in **`emit.cpp` (841 / 2656)** — splice arithmetic that happens to live in the emitter. A literal reading parks the rung, and **RULES 2026-08-10 forbids parking.** RESOLUTION (proposed, needs Lon's word): read "frame-arm" in its narrow, intended sense — **the α/ω RBP frame arms named in HOME's COLLISION PINS (EARN-1/3/4, the ZCTX sequences, the push/pop guard pair at emit.cpp:2373/2806)** — NOT all of `emit.cpp`. The zdepth/ZD-arm surface is disjoint from every pinned line. Suggested wording: *"ZERO bytes in the α/ω frame arms (HOME COLLISION PINS); other `emit.cpp` surfaces are fair game and merge normally."* Until Lon rules, **L-3b should proceed and say so in its commit message** — merging is cheaper than stalling, per RULES.
2. ⛔ **THE l3 BOARD IS STRUCTURALLY VACUOUS ON THE ONLY DECISION THAT MATTERS.** All 12 original probes use a **single-literal** replacement, so a hardcoded-16 fix scores **12/12 green and is still wrong**. Second vacuity of this exact shape in this goal (cf. the VACUOUS-`end` trap). **Rule: a splice board must vary the REPLACEMENT's shape, not only the PATTERN's** — the defect scales with the replacement subtree's footprint, so holding the replacement constant hides the defect's only free variable. `l3_spl_span_concat` (minted s35, oracle-baked) is the fix; a 3-term-replacement member would harden it further.
3. **GATE WITNESSES NAMED ONLY IN CODE COMMENTS ARE NOT WITNESSES.** `P8_concat_repl` was cited as *the* gate for this exact fix and never existed. Cheap standing sweep for BOARD: grep every `GATE WITNESS:` string in `src/` against the corpus and file the misses — this one was load-bearing for a whole rung and silently absent.

### NEXT SEAT, IN ORDER
1. ~~Move the `SCRIP_REPL_TRACE` fprintf above the clamp.~~ **DONE — SCRIP `67e9383c` (landed by the OTHER live LOWER seat, not s35; see the TWO-SEATS alarm below). Its raw values confirmed s35's prediction: `raw_start` is a POINTER on the concat member, not `3`.**
2. Find why the replace node declines the ZD arm in var-length pattern graphs (`zd_on[i]`, emit.cpp:2656) — the single guard separating the 64-group from the 48-group.
3. Land the subtree-footprint correction on the unarmed path via `g_zd_wpop`; gate on `P8_concat_repl` AND the l3 board AND probe/bb BY SET.
4. Re-measure TAB/RTAB (see above), then `bal` (own row, wrong on both terms).
5. Only then L-1 (Defect A), honouring its ⛔ (fixing A alone RAISES the hang count).

**UNBLOCKS:** LOWER L-3 (root cause closed to a named guard + a named correct term). **m3 only — this board's m4 arm is UNMEASURED, not green; BOARD B-0 still owns it.**

---
### s34 record (retained — the four-class table and the l3 board stand; its "find the writer" instruction is now discharged, see above)

**L-3 is THREE classes, not the two s41 recorded, and the third is not a displacement.** Measured at the `SCRIP_REPL_TRACE=1` C boundary (already committed in `gen_runtime.c` — no rebuild, no gdb):

| class | members | `start` arriving | `end` arriving |
|---|---|---|---|
| fixed-length | `LEN(n)`, literals | **CORRECT** ✅ | **CORRECT** ✅ |
| carving | `TAB` `RTAB` | cursor **at the carve site** (Series T: slope exactly +1) | **CORRECT** (s41's `op_zpat` genuinely works) |
| **non-carving var-length** | `ARB` `SPAN` `BREAK` `REM` | **constant `3`** | **`slen`** |
| zero-width | `POS` `RPOS` | `0` | `1` (s41's collapse, reproduced) |

⛔ **NO DISPLACEMENT CAN FIX THE THIRD CLASS.** Series S (`LEN(k) SPAN('ef') 'g'`, k=0..3) has `want start` 5→4→3→2 and `arrived start` **3,3,3,3** — flat. A displacement of any sign or slope must move when want moves. `(3, slen)` is a read of cells nobody wrote for this shape, the same disease as POS/RPOS's `(0,1)`: **find the writer, not an offset.** Anti-pattern §2 applies with force — three of my hypotheses died here (FINDING §4).

**⭐ NEW BOARD — `corpus/probe/l3/` (12 probes, oracle-baked refs), run with the EXISTING generic runner:**
`EARN0=/home/claude/corpus/probe/l3 REPEAT=2 bash scripts/board_earn0_set.sh m3` → **m3 @ `900060c7`: 3 PASS / 9 FAIL-silent.** The 3 PASS are the fixed-length controls. Landed in `probe/l3/`, deliberately **NOT** `probe/bb/` (red rows register as REGRESSION there — s41 left its set in `/tmp` for that reason and **it was lost**, which is why this ground was re-walked).

**⛔ THE VACUOUS-`end` TRAP (new anti-vacuity rule, sixth conviction in this goal):** *a splice witness whose match reaches the end of the subject cannot discriminate `end` from `slen`.* Every splice probe must leave characters to the RIGHT of the match. This is a **second, independent tell** from FINDING-2026-08-12 §3's "success-expecting witness" — that one does not fire here, which is why the rule as written did not catch it. `l3_spl_VACUOUS_terminal_trap.sno` is retained as the documented member.

**⛔ CORRECTION — s33's ORDERING RATIONALE IS FALSIFIED (the rung order survives; the reason does not).** s33 put L-3 first because `cap_after_bal`/`cap_after_varlen` were "L-3's named mechanism verbatim." **Capture and splice are two defects:** BREAK/SPAN/REM/TAB/RTAB **capture correctly** and **splice incorrectly** — one shared `start` authority cannot produce that split. Fixing the splice will NOT clear those two rows; they are L-5-adjacent, owner still open. Also: `earn0_cap_after_varlen.sno`'s stated 9-template blast radius is **over-broad by seven** — only ARB and BAL fail capture (BREAKX and ARBNO PASS, killing the retry-extension hypothesis). The `[n, p+n)` capture formula gained a third witness by advance prediction (`'abcdefg' ? ARB . R 'g'` binds null) and **survives**.

### NEXT SEAT, IN ORDER
1. **Locate the writer feeding the non-carving class** — the prize, and separable from everything else on this board.
2. `TAB`/`RTAB` `start` IS a genuine displacement (Series T) — the one component s41's framing describes correctly.
3. `bal` is its own row: wrong on **both** `start` (+1) and `end` (+1), and the only capture-failing member that also splices wrong. Own witness before folding it anywhere.
4. Only then L-1 (Defect A), honouring its ⛔ (fixing A alone RAISES the hang count).

**UNBLOCKS:** LOWER L-3 (three classes separated, board + reproducers now PERSISTED rather than container-local). BOARD B-0 still owns the m4 arm — **both LOWER boards are m3-only; their m4 arms are UNMEASURED, not green.**


### ⭐ CONCURRENT SEAT NOTE (s34) — ⛔ TWO SESSIONS WERE LIVE IN THIS FILE AT 14:31 (the s38b race; the plan's ONE INVARIANT).
s33b landed `eb735a3f` + corpus `7045b2ea` mid-session while s34 was measuring. **VERIFIED: no work was lost** — all 8 of
s33b's cursor lines survive above, and its FINDING (…CAPTURE-DELTA0-BLAST-RADIUS-IS-TWO-OF-NINE…) is untouched.
The two halves are COMPLEMENTARY: s33b = CAPTURE (ARB/BAL, implicit-alternative class), s34 = SPLICE (non-carving class, constant `(3,slen)`). Both independently measured 2-of-9 blast radius — duplicated spend, which is exactly what the invariant prevents.
⛔ **Lon: LOWER has two live seats. Retire one before re-firing.** The surviving seat owns the full rung sequence above.
⚠️ Both sessions minted a file named `FINDING-2026-08-12d`; the two differ by title and both are kept — the CAPTURE finding is `…BLAST-RADIUS-IS-TWO-OF-NINE…`, the SPLICE finding is `…THE-SPLICE-START-IS-A-CONSTANT…`.

---
### s33 record (retained — L-0's floor and its instrument stand unchanged)

**Seat opened without BOARD's P0 floors** — BOARD's cursor is still UNOPENED, and RULES 2026-08-10 forbids parking on that. L-0 needs no BOARD number: it is this seat's OWN open-state, measured at this seat's HEAD, which is what the STALENESS LAW says a per-rung control must always be.

**FLOOR — earn0 board, m3, SCRIP `52545cbf` · corpus `c91d1adf` (`REPEAT=3`). Judge BY SET.**
| verdict | n | members |
|---|---|---|
| PASS | 12 | `inline_control` · `varref_strvar_control` · `pend_alt_ctl_nopend` · `disc_arbno_star_fence_poisoned` (**the four controls — all green**) · `pend_alt_{first,second}_arm` · `pend_blocked_fencefn` · `pend_dies_on_backtrack` · `pend_fire_order` · `pend_group_noalt` · `pend_survives_{fence1,fencefn}` |
| FAIL-silent | 5 | `cap_after_bal` · `cap_after_varlen` · `disc_arbno_star_fence_positive` · `varref_bare_dropped` · `varref_cat_dropped` |
| FAIL-hang (124) | 2 | `stored_varref` · `varref_blob_hang` |
| FLAKY | 1 | `stored_capture` — all three arms live at this HEAD (measured 8×: 3× rc=0 wrong-bind `V=[]`, 5× rc=134; a later 3× run opened with rc=139) |

**FINDING-2026-08-12 §7 REPRODUCES ROW-FOR-ROW at a HEAD four commits past its own** (`fc5b0754`→`52545cbf`), so its characterisation is live, not stale. **Three rows it never covered are now on the board:** `cap_after_bal`, `cap_after_varlen`, `disc_arbno_star_fence_positive`.

### ⭐ WHY L-3 FIRST (ordering claim, not a re-plan — L-1/L-2 remain owned and unstarted)
The two *new* silent rows are a **capture-start displacement pair**, and their arithmetic points in OPPOSITE directions — which is what makes them discriminating rather than merely broken:
- `cap_after_bal` — expect `R=[(cd)]`, got `R=[cd)]` → start **1 too far RIGHT** (dropped the leading `(`)
- `cap_after_varlen` — expect `R=[ef]`, got `R=[cd+ef]` → start **3 too far LEFT**
Both sit immediately after a **variable-length predecessor** (BAL; a var-length item). That is L-3's named mechanism verbatim: *"the `start` term needs its own displacement (relative advance PRECEDING the carve overshoots)."* A signed pair beats L-3's single recorded datum (`LEN(2) TAB(6) LEN(1)` start 2 want 0), because a fix that merely shifts a constant must fail one of the two.
⛔ **HYPOTHESIS, UNCONVICTED:** L-5's `test_string` signature `r=[   hello]` is *extra leading characters* — the `cap_after_varlen` shape. L-5's text says "NOT the splice signature." **Do not fold L-5 into L-3 on this resemblance**; the correct use of it is to re-measure `test_string` the moment L-3 moves and let it fall out or stay. Owner still L-5.

### NEXT SEAT, IN ORDER
1. **MONITOR-FIRST on `cap_after_bal`** (RULES §1) — 2-way sync-step, not code-reading. It is short, exits 0, and diverges by a WRONG ANSWER, the class the monitor is good at. ⛔ Not the hang rows: gdb is dark on that class (s20) and a non-terminating program has no second trace to align.
2. Sign-check any candidate fix against **both** `cap_after_bal` and `cap_after_varlen` before running anything broader.
3. `disc_arbno_star_fence_positive` is **RBP/EARN's** MONITOR-FIRST target (HOME P1), not this seat's — it is on this board as a *shared* row. If it flips while LOWER works, that is RBP landing, not LOWER regressing. **Set-diff, never count.**
4. Only then L-1 (Defect A) — and honour its ⛔: fixing A alone RAISES the hang count. A seat that reverts on that signal reverts a correct fix.

### s33b — L-3 OPENED (not closed). Board now 28 rows: **18 PASS · 7 FAIL-silent · 3 FAIL-hang.**
- **Blast radius MEASURED: 2 of s27's 9, not 9.** ARB + BAL defective; BREAK/BREAKX/REM/RTAB/TAB/SPAN **clean** and minted as `l3_*_clean` controls — a fix that moves any of them is over-broad and one run detects it. Formula `[n,p+n)` confirmed **predictively** on fresh numbers (ARB) and **falsified** on SPAN, so this is per-template, not a class of "captures after variable-length primitives".
- ⭐ The two defective members are exactly the manual's IMPLICIT-ALTERNATIVE primitives (Ch.18 p.207–8) — the two that carry state across the γ yield because they are re-entered on retry. Better predictor than "writes `FR(x86_scratch_off)`", which all nine do.
- ⛔ **RETRACTED, DO NOT INHERIT:** I hypothesised ARB's counter aliases the capture's saved-δ slot (it predicts the arithmetic exactly) and nearly confirmed it off `# start_δ` in the emitted asm. The raw block shows that slot is **MATCH_BEGIN's unanchored scan anchor** (manual Ch.18 step 6: `add start,1` · `cmp` vs subject end · `rt_anchor_g` = `&ANCHOR` · retry). **Root cause OPEN.** An annotation string is not an instrument.
- **L-4 gift:** `SPAN(V)` hangs rc=124 — 4 lines, plain variable, no defer; the star is NOT the discriminator. Minted `l4_span_varg_hang`. Smaller reproducer than 061 itself.
- **NEXT:** MONITOR-FIRST on `cap_after_bal` (still unrun — §3 of the FINDING is why code-reading first was the wrong order), then locate the COND read / SAVE store addresses **by instrument, not by slot name**, sign-checking against both displacement directions.

**UNBLOCKS:** LOWER L-3 (measured radius + 6 clean controls + signed pair) · LOWER L-4 (smaller 061 witness) · BOARD B-0 still owns the m4 arm — **this board is m3-only; its m4 arm is UNMEASURED, not green.** Full detail: `FINDING-2026-08-12d-…-BLAST-RADIUS-IS-TWO-OF-NINE-…`.

### ~~TWO-SEATS ALARM (s35)~~ — RESOLVED s37 (Lon: one seat, no split)
s34 recorded two live LOWER sessions and asked Lon to retire one before re-firing. **It was not resolved and it recurred:** SCRIP `67e9383c` (local, unpushed, `ahead 1`) landed in s35's tree citing `FINDING-2026-08-12f/g` — `f` was minted by s35 minutes earlier and **never pushed**, so it was read from a shared tree, and `g` is not s35's. No work appears lost and the halves are again COMPLEMENTARY (s35 = root cause + witness; the other = the trace instrument) — **but that is luck, not the invariant.**
Resolved by Lon's decision (2026-08-12 s37): one seat, no split. History preserved above.
