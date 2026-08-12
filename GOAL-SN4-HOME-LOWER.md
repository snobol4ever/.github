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
- [x] **L-3b · ⭐ CLOSED s43 — l3 BOARD 13/13 GREEN. A SECOND defect (below the one this rung's text describes) closed the carving class too: `fc_walk_range` in `lower_snobol4.c` contributed 0 to `fp`/`op_fc_disp` for `IR_LIT_INTEGER`/`LIT_STRING`/`LIT_REAL`, which `zd_k` universally carves K=16 for — two authorities for one carve decision, the `s22k` spelled-twice class. ONE LINE (SCRIP `93fbe1e2`). `tab_nonterm`/`rtab_nonterm`/`tab_linear3`/`pos` ALL flipped PASS. ⛔ THE 'STILL OPEN: carving class untouched, separate defect' CLAUSE AT THE END OF THIS RUNG'S TEXT IS DISCHARGED, and L-3/s36's 'POS/RPOS is a third independent defect' is FALSIFIED — there was no third defect. Full derivation in the s43 LIVE CURSOR.** Original text retained: **L-3b · THE FIX — non-carving class fully landed s41 (SCRIP `3d223c12`, pushed). ARB/BREAK residual ROOT-CAUSED AND FIXED same session, not the match-primitive-specific bug earlier cursors suspected.** SPAN/REM/lit-replacement shapes fixed s39/40: read at `FR(op_off)`/`FRQ(op_off+24)`. **ARB/BREAK fixed s41: the bug was in `x86_zop()` itself (`x86_asm.h`), not in any match-primitive template.** Regime-2 (per-BB FORTH-cell window) resolved its offset correctly ONCE (`off - op_fc_base + bump`) but spelled the result as a plain `"[rsp + N]"` string — byte-identical to the regime-4 raw-rsp spelling `x86_fr32_prefix()`/`x86_fr64_prefix()` produce on an unpinned graph. `x86_parse`'s classifier matches the regime-4 prefix BEFORE the dead plain-`[rsp+N]` `XK_RSP32` fallback, so an ALREADY-RESOLVED regime-2 address was re-parsed as an unresolved flat ZLS coordinate and got `op_zdepth` added a SECOND time. ARB's own scratch cell (retry-extension-counter at `+0`, saved-start-cursor at `+4`) landed 16 bytes past its own window — exactly the address `bb_match_end.cpp`'s writer independently targets by design (`op_off+op_fc_disp`) — so MATCH_END's splice-start write picked up ARB's retry counter instead of a cursor. SPAN passed only because its guts variant never writes its own `+0` slot (only `+4`), so the same double-resolution was silently self-consistent — not evidence the address was ever right. **FIX:** regime-2 now spells the `"[rsp# + N]"` raw-machine escape (the same one the `bump!=0` arm already used, per the ARGREAD land mine comment on the neighboring line) so `XK_RSP32`/`XK_RSP64` claims the string first and `x86_frame_off()` never re-runs on an already-resolved address. l3 board 8/13→**11/13** (arb_nonterm, break_nonterm flip). Broad SNOBOL4 corpus mode-3 261→**264**, mode-4 255→**257**, zero regressions (FAIL/SKIP sets diffed byte-for-byte). Three bonus flips outside the l3 board: `157_pat_cap_arb_alt_keep`, `174_pat_bal_manual_example`, `176_pat_bal_balanced_forms` (BAL shares the same scratch-cell shape per `fc_geom`'s own grouping in `zeta_storage.c`). **STILL OPEN:** carving class (TAB/RTAB/POS/RPOS) untouched by design, separate defect, own conviction needed. ⛔ **PROVENANCE NOTE (Claude Sonnet 5, s41):** the diagnostic instrumentation and root-cause analysis were mine, built and verified across several rebuild/measure cycles in this transcript; the `git commit` that landed the fix (`f21e3215`→`3d223c12` after rebase) does not appear in my own tool-call history — I never issued `git add`/`git commit`. I independently reverified every number in the commit message (fresh build, fresh l3 board, fresh broad-corpus run) before trusting or building further on it, and they all reproduced exactly. Per the s40 precedent: naming this, not explaining it away. If another LOWER-adjacent seat is live in this same container, its work here was correct and is not being contested — only the authorship is uncertain.
- [ ] **L-4 · 061 — VARIABLE-ARG PATTERN-PRIMITIVE CLASS.** ⛔ s45: ROOT CAUSE FOUND, gdb-confirmed with live numbers — NOT YET FIXED. The `ZOPQ` cross-head staging site (`emit.cpp:2702`, the ONE authority for `g_zd_read[k]`) computes a naive `zd_out[consumer]-zd_out[producer]` difference that has no visibility into `IR_MATCH_BEGIN`'s own runtime carve; when the producer predates the match and the consumer is inside it (exactly `POS(N)`'s shape here), the read is short by MATCH_BEGIN's carve plus every un-popped intervening node's K (measured: 48 = 32+16 for this witness). The site's OWN inline comment already names this defect class for the sibling primitive `IR_MATCH_LEN` and gives a formula referencing `zd_ud`/`zdh` fields that **do not exist in the codebase** — documented, never implemented. Corrected mechanism identification vs s44 (which misattributed the read to the `FRQ` legacy arm — it is actually `ZOPQ`, byte-identical spelling at this offset, hence the confusion). Full derivation, exact numbers, and the proposed general fix (adapt `g_zd_zunder`'s backward-scan pattern to this staging site) in the s45 LIVE CURSOR. Separately: `l4_span_varg_hang.sno` (SPAN(V) variant) now passes m3 clean but SEGFAULTS m4 — new, unstarted, possibly-unrelated finding, own witness.
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

## ⭐ LIVE CURSOR — 2026-08-12 s45 (Claude Sonnet 5). **L-4/061 ROOT CAUSE FOUND, GDB-CONFIRMED WITH LIVE RUNTIME NUMBERS. NOT YET FIXED — the correct compensation formula is not yet known, only the deficit's exact size and origin. NO CODE CHANGED THIS SESSION.**

**Correction to s44:** s44 traced the read to `bb_match_pos.cpp`'s `FRQ(_.op_sa+8)` arm and said it goes through "regime-3/4, not the already-fixed regime-2 path" — that mechanism identification was WRONG. Fresh gdb trace this session shows `g_emit.op_zres` **is** 1 for this node at `emit.cpp:1488`'s dynamic-arg branch (`g_emit.op_sa=192`), so `bb_match_pos.cpp` actually takes the **`ZOPQ(0,8)` arm** (op_sa>=0 && op_zres — the ZD/FORTH-cell path), not `FRQ`. `ZOPQ(k,w)` and `FRQ(off)` are BYTE-IDENTICAL in their raw spelling when `op_zread[0]=0` (both produce `[rsp#+8]`), which is exactly why s44 misread the disassembly — the two arms are textually indistinguishable at this specific offset. The instrumentation (`SCRIP_ZOP_DIAG`) that would have disambiguated is a `x86_zop()`-only diagnostic and never fires on the `ZOPQ`/`x86_zref` path, so it printed nothing for this node — a silent, not a positive, absence. **Standing lesson for future seats: `[rsp#+N]` in the `.s` does not by itself tell you which of the four ZD-1 accessor families produced it — check `g_emit.op_zres` at the staging site, don't infer from the spelling.**

### L-4/061 — ROOT CAUSE (gdb-confirmed, live process, not hand-derived from `.s` text)

**MONITOR re-run fresh** (`PARTICIPANTS="spl scr"`): divergence confirmed unchanged from s44 — at `X POS(N) 'a' . V` (stmt 3), SPITBOL matches and continues; SCRIP branches straight to the failure label (`LABEL stno=INT=7` = `DONE`). SCRIP m3 now: empty output, rc=0 (fresh-confirmed, matches s44).

**The actual mechanism:** `emit.cpp:2702` is the ONE site that stages `g_zd_read[k]` (consumed as `op_zread[k]` by `ZOPQ`), and it computes the NAIVE difference `zd_out[i] - zd_out[_k]` (consumer's static walk position minus producer's). Its own inline comment — written for a DIFFERENT primitive (`IR_MATCH_LEN`, "ZD-5b-LEN cross-head correction") — already names this exact defect class and gives a corrected formula (`zd_ud[consumer] - K(consumer) + zdh - zd_out[producer]`), but **`zd_ud` and `zdh` do not exist anywhere in this codebase** (`grep` confirms zero hits outside this one comment). The formula was written down and never implemented; the code on the same line still does the naive subtraction the comment says is wrong. `IR_MATCH_POS` shares `IR_MATCH_LEN`'s exact staging path (both go through `zd_nops`'s `n_operands` arm, emit.cpp:2030) and so inherits the identical unfixed defect.

**Why it fires here:** `zd_out` is a static, pre-drive tally over the node sequence. It has NO visibility into `IR_MATCH_BEGIN`'s own RUNTIME carve (`sub rsp,32`, confirmed in the `.s`) because that carve is emitted later, at drive time, per-match — it is not part of the walk `zd_out` was computed from. So whenever a ZD-armed node's operand is a PRE-MATCH_BEGIN producer (here `IR_COERCE_INTEGER` for `N`, staged BEFORE the match) and the consuming node is POST-MATCH_BEGIN (here `IR_MATCH_POS`, inside the match), the naive `zd_out[consumer]-zd_out[producer]` misses every runtime carve that landed in between — both `MATCH_BEGIN`'s own Kc AND any un-popped predecessor cells (the "non-popping run" design means `coerce_integer`'s own 16B stays live on the spine too).

**Numbers, gdb-verified live (not read from `.s` text alone):**
- `zd_out[IR_COERCE_INTEGER(N)] = zd_out[IR_MATCH_BEGIN] = zd_out[IR_MATCH_POS] = 48` (all three identical — confirms `zd_out` cannot see the runtime carve).
- `g_zd_read[0]` (⇒ `op_zread[0]`) stages to `0` ⇒ `ZOPQ(0,8)` spells `[rsp#+8]`.
- Independently traced through the emitted `.s`: `coerce_integer` writes `N`'s value at `[rsp+16+8]=[rsp+24]` relative to ITS OWN post-carve rsp (after its `sub rsp,16`); falls through to `match_begin` WITHOUT popping (non-popping run); `match_begin` does its own `sub rsp,32`; the SAME physical cell is now at `[rsp+24+32]=[rsp+56]` relative to match_begin's post-carve rsp, which is the rsp `match_pos` reads under.
- **Correct offset: 56. Emitted offset: 8. Deficit: exactly 48 = MATCH_BEGIN's own carve (32) + coerce_integer's un-popped carve (16).**
- Checked whether `fc_head_fp(MATCH_BEGIN)` (an existing accessor already used for a structurally similar cross-head compensation at emit.cpp:2697, for `IR_MATCH_REPLACE`) supplies this number directly: it returns **16**, not 32 or 48 — it is measuring a different quantity (a fixed-cell WINDOW byte count, `ZB-FC-3d`, not the runtime carve size). **Do not assume `fc_head_fp` is the drop-in fix term without re-deriving what it counts; it is NOT simply Kc.**

⛔ **NOT YET DONE, DO NOT SKIP:** the general correction formula. I have ONE witness's exact deficit (48), not a derivation of the general term (something that generalizes across producer/consumer position pairs the way `op_zdepth`/`op_flat_disp` do for the FRQ arm — see x86_asm.h's ZTOS-1/ZTOS-2 comments for the shape a correct derivation should take: "a box compensates for exactly what IT carved"). A single-witness constant (hardcode +48) would almost certainly be wrong for any other producer/consumer depth combination — this is precisely the "MEASURED root cause... off by Kc=256" LEN precedent's own warning: Kc varies per witness (32 here for POS with one un-popped predecessor; presumably 256 for whatever LEN witness the stale comment describes), so it is NOT a constant, it is `MATCH_BEGIN`'s actual runtime Kc plus the summed K of every un-popped node between producer and consumer — the same "under" accumulation pattern `g_zd_zunder` already implements for `IR_MATCH_REPLACE` at emit.cpp:2697 (backward-scan from the node to `IR_MATCH_BEGIN`, summing `zd_k()` of every armed node crossed). **NEXT RUNG:** adapt `g_zd_zunder`'s backward-scan pattern (already proven correct for REPLACE) to the general cross-head `ZOPQ` staging loop at line 2702 — when producer is found before the run-local `MATCH_BEGIN` and consumer after it, add the backward-scan sum (predecessor's own runtime carve + every un-popped intervening node's K) to the naive `zd_out` difference. Verify against `061` (expect deficit exactly cancels, offset resolves to 56) AND re-run the FULL l3 board + broad SNOBOL4 corpus (a change to the ONE staging site for ZOPQ affects every ZD-armed cross-head read in the codebase, SNOBOL4 and Icon and Prolog alike — this is exactly the kind of one-authority site where a fix can widen far past the single witness, for better or worse; judge BY SET, expect the LEN witness the stale comment describes to also flip if it's in the corpus).

### GATES status this session
No code touched. Diagnosis only — this cursor carries the full gdb trace; promote to `FINDING-*.md` when the fix lands (per s44's own convention).

**UNBLOCKS:** none outside this seat — L-4's fix touches only `emit.cpp:2702`'s staging loop, inside LOWER's own charter (ZERO emitter frame-arm bytes, this is depth-staging not frame-arm emission). Any seat picking up L-4 next has the exact formula shape to implement, not a fresh hunt.



**Session start note:** this seat was given the standard three-repo clone (`.github`, `corpus`, `SCRIP`) and hit exactly the oracle-less trap s43 §PLAN SCRUTINY item 3 predicted — fixed the same way (hand-cloned `x64`). Also set `git config --local` identity in **corpus**, not just SCRIP (s43 §PLAN SCRUTINY item 4). `install_system_packages.sh` run clean, `gdb` confirmed live, `scrip`+`libscrip_rt.so` built clean at SCRIP `0bbf092b` / corpus `7814057e`. **These were already on `origin` — s43's "PUSH BLOCKED" note above is now STALE, confirmed by `git log` on a fresh clone; the s43 commits are pushed.**

**l3 board re-run fresh (not transcribed): 14/14 PASS**, m3, at HEAD — independently reconfirms L-3b's claim.

### L-4/061 — measured, not fixed; s43's own top hypothesis for it is FALSIFIED
`061_capture_in_arbno.sno` (`POS(N) 'a' . V` with `N` a runtime variable) still diverges from the live SPITBOL oracle: SCRIP m3 now produces **empty output** (was previously reported as a hang; now a silent match-failure, rc=0) against oracle's `a\na\na`. `SCRIP_CAP_DIAG` shows the SAVE (capture) node for this witness resolves `save_active=1 fc_bytes=16` — **correctly counted**, via `fc_geom`'s early grant (zeta_storage.c:745) — so s43's "L-4 is very likely the same defect-#2 mechanism, audit `IR_MATCH_ASSIGN_SAVE` in `fc_walk_range`" is **FALSIFIED for this witness**: that arm is sound here and never even reached (the pre-switch `fc_geom` check short-circuits it). ⛔ **DO NOT RE-SPEND ON THE ASSIGN_SAVE HYPOTHESIS FOR 061 WITHOUT NEW EVIDENCE.**

2-way monitor (`PARTICIPANTS="spl scr"`) pinpoints the actual first divergence cleanly: at `POS(N) 'a'` itself, SPITBOL matches and continues to the capture; SCRIP branches straight to the failure label. The match predicate on the dynamic (variable) argument is wrong, not the capture. This matches the **original** (pre-s43) L-4 wording — "the dynamic arm reads a cell the arg never landed in" — not the footprint-counting class L-3b closed.

Traced as far as: `bb_match_pos.cpp`'s dynamic arm reads via `FRQ(op_sa+8)` → `x86_zop()`. `SCRIP_ZOP_DIAG` confirms this specific read **never appears in the regime-2 log** — i.e. it is NOT going through the already-fixed ARB/BREAK regime-2 path (`x86_fc_hit` declines it; makes sense, it's not "this box's own per-BB cell", it's a value crossing from an `IR_COERCE_INTEGER` predecessor through `MATCH_BEGIN`'s own `sub rsp,32`). It is going through the regime-3/4 path (`x86_fr64_prefix()` → later reclassified `XK_FR64` by `x86_parse` → `x86_frame_off()`/`op_zdepth` compensation at encode time).

⛔ **RETRACTED, DO NOT INHERIT (mine, same session):** I stated in-transcript a specific "32-byte offset drift" between the coerce_integer write and the match_pos read, computed by hand from the raw `.s` text. That arithmetic **assumed zero depth compensation** between producer and consumer, which is false — `x86_frame_off()`/`op_zdepth` exist specifically to compensate for exactly this kind of intervening carve, and I had not traced whether that compensation is correct or broken for this specific producer/consumer pair before stating the number. The number should not be trusted or re-derived from; the *symptom* (POS(N) with dynamic N fails to match) is solid (monitor-confirmed), the *mechanism* is not yet established.

**NEXT RUNG for L-4:** MONITOR-FIRST step 2, properly — gdb breakpoint on `x86_frame_off()` (or the specific `FRQ(op_sa+8)` call site in `bb_match_pos_body`) with a hit-count/ignore-counter isolating this witness's one call, single-step, compare the address it computes against the address `rt_coerce_int_d` actually wrote to (visible via a watch/print on `rsp` at both sites). Do not hand-derive the offset again from static `.s` text — this file's own `.s` text was exactly what produced my retracted claim.

### NEW, UNSTARTED — mode-3/mode-4 divergence on the L-4 gift witness
`corpus/probe/earn0/l4_span_varg_hang.sno` (`SPAN(V)` with a plain variable `V`, minted s33b) — the smaller reproducer for the same variable-arg class — now **passes clean in mode 3** (byte-identical to `.ref`, confirming SPAN(V)'s dynamic arm is NOT broken the same way POS(N)'s is — worth noting as a discriminator between the two primitives' dynamic-arg paths). But compiled properly mode-4 (`--compile` → `gcc -c` → `gcc -no-pie -lscrip_rt`) it **segfaults** (rc=139). This is a genuine, currently-unexplained BOTH-MEDIUM violation (RULES.md), not yet monitor-bracketed, not yet gdb'd. Own witness, own investigation — do not conflate with L-4/061's POS(N) mechanism above; they may or may not share a root cause.

### GATES status this session
No code touched ⇒ no regen, no new commit beyond this cursor + the git-identity/tooling housekeeping. l3 board reconfirmed green. No FINDING filed separately — this cursor carries the full record; promote to a standalone `FINDING-*.md` if a later session lands the actual fix and wants the diagnosis preserved outside the cursor's prune window.

### ⭐ PLAN SCRUTINY (s44) — six items; two are NEW defects in THIS FILE that cost me time directly

1. ⛔⭐ **THIS RUNG'S OWN TEXT CONTAINED A DANGLING POINTER, AND I PAID FOR IT.** L-4 said *"MONITOR bracket exists per s39b — read that cursor first, do not re-spend."* **There is no s39b section in this file.** Section headers run s33/s33b/s34/s35/s36/s37/s38/s39/s40/s41/s42/s43 — I grepped the whole file twice looking for it. So the one instruction the rung gave for not re-spending pointed at nothing, and the "bracket" it promised may never have existed or may live in a FINDING nobody named. **Rung text fixed this session** to cite what actually exists. **Standing lesson: a rung that says "see X" must name a file or a section that a grep can find** — the cursor-prune convention (STALE-ORIENTATION (c), "prune below the last ~3") *guarantees* these pointers rot, so cross-rung references must go to `FINDING-*.md` filenames, never to session numbers.

2. ⛔⭐ **"061" IS AMBIGUOUS IN THE CORPUS AND THIS FILE NEVER SAYS WHICH ONE.** There are two: `corpus/crosscheck/capture/061_capture_in_arbno.sno` and `corpus/crosscheck/patterns/061_pat_fence_fn_seal.sno`. I disambiguated by reading both and matching against the rung's own description ("variable-arg pattern-primitive"), which fits the capture one. A seat that guessed the other would have investigated a FENCE-sealing witness and concluded L-4 was about something else entirely. **Fix (cheap, mechanical): every witness reference in every goal file gets its corpus-relative path, not its bare number.** `CORPUS-LOCATIONS.md` exists precisely to stop path rediscovery and this is the same disease one level down.

3. **THE WITNESS CHANGED FAILURE CLASS AND NO CURSOR WOULD HAVE TOLD THE NEXT SEAT.** Every prior mention of the L-4 class describes a **hang** (`rc=124`); at this HEAD `061` is a **silent empty-output rc=0**, and `l4_span_varg_hang` (named for the hang!) doesn't hang either — it passes m3 and segfaults m4. That matters operationally: RULES §1 notes the monitor is *good* at wrong-answer divergence and *dark* on hangs (gdb has no second trace to align). So this class just moved from the hard-to-instrument bucket into the easy one — **that is a genuine opportunity, not just bookkeeping.** ⛔ A seat inheriting "L-4 = the hang class" will reach for the wrong instrument.

4. ⛔ **`board_earn0_set.sh`'s m4 arm is STILL structurally broken (s43 item 2, unfixed) — and I now have the exact working replacement, verified by hand this session.** It diffs `--compile`'s stdout (assembly text) against a `.ref` of expected program output. The correct sequence is `compile_mode4()` from `scripts/test_broad_corpus_snobol4.sh:30` — `--compile > p.s` · `gcc -c p.s -o p.o` · `gcc -no-pie p.o -L out -lscrip_rt -lm -Wl,-rpath,<out> -o bin` · run. **I used exactly that by hand and it is how I found the `l4_span_varg_hang` m4 segfault** — a real defect that the board's own m4 column would have reported as just another indistinguishable FAIL. This is ~10 lines and converts a lying column into a working one. **I did not land it because BOARD owns the instruments (§COLLISION PINS: "ONLY BOARD re-cuts instruments") — but the diagnosis is complete and the patch is trivial. Lon: if you'd rather LOWER just fix it, say so and it's a five-minute rung.**

5. **THE ORACLE GAP HAS NOW BEEN PAID FOR THREE TIMES (s40 predicted, s43 measured, s44 hit it again).** `PLAN.md`'s standard seat instruction is ".github, corpus and SCRIP"; every board in this file needs `x64`. **I fixed the clone block in `PLAN.md` this session** (added `x64` to the session-start clone step — this is the *setup instructions* block, NOT the goals table, which RULES step 3 correctly forbids editing on routine handoff). The complementary half — the `[ -x "$SBL" ] || { echo "ORACLE MISSING"; exit 2; }` guard inside the board scripts — is BOARD's to land, and is still open. **Until it lands, an all-FAIL board table is not evidence of anything.**

6. **SEAT-LIVE ENFORCEMENT (s40, seconded s43) — still unbuilt; adding a clean NEGATIVE data point.** No `SEAT-LIVE-*` file exists. **This session saw zero provenance anomalies** — every commit in my history is mine, nothing appeared in my tree unbidden, and s43's own "PUSH BLOCKED" claim resolved benignly (the commits were on origin; the note was simply stale, not evidence of another writer). So the invariant held this time, unenforced. That is not an argument against the guard — five prior incidents are — but it does mean the guard's cost should be judged against a real base rate, and I'd rather record the quiet session than let the file read as if every session is contested. **I still second building it.**

---
## ⭐ LIVE CURSOR — 2026-08-12 s43 (Claude Opus 5). **⛔⭐ L-3b IS CLOSED. THE l3 BOARD IS 13/13 GREEN.** SCRIP `93fbe1e2` + artifact commits; corpus `5da19d40`. **PUSH BLOCKED — credential requested in chat, not yet supplied. Both repos are ahead of origin and LOCAL ONLY.**

**TWO defects, not one, and the second was never on anyone's list.** s41/s42 (below) and I were all hunting the ARB/BREAK residual. That was defect #1 and it is fixed. But the *carving class* (TAB/RTAB/POS/RPOS) — which every cursor in this file since s35 has called a separate, unstarted, unconvicted defect — turned out to be **one line in LOWER**, and it is now also fixed. The board went 8/13 → 11/13 (defect #1) → **13/13** (defect #2).

| rung | state | evidence |
|---|---|---|
| l3 board m3 | **13/13 PASS** | re-ran `EARN0=/home/claude/corpus/probe/l3 bash scripts/board_earn0_set.sh m3` at final HEAD |
| broad SNOBOL4 corpus (336) | m3 **264**, m4 **257** (from 261/255) | FAIL+SKIP sets diffed byte-for-byte with `comm -23`/`comm -13` against a stashed-and-rebuilt baseline **in this session**; zero new failures at either step |
| `probe/bb/run_suite.sh` | 159 pass / 1 xfail / 0 XPASS / **5 regression** | those 5 are `D12 D13 H31 X01 X10` — **the identical set and count s39 recorded and proved pre-existing.** Unmoved. |

### DEFECT #1 — ZOP regime-2 double-resolution (SCRIP `3d223c12`)
Identical in every particular to s42's account below; I derived it independently and it is correct, so I am not restating it. `x86_zop()` regime 2 resolved once, spelled the answer as plain `[rsp + N]`, and `x86_parse` — whose regime-4 prefix check runs first — reclassified the resolved address as an unresolved flat coordinate and ran `x86_frame_off()` on it again. Fix: spell the `[rsp# + N]` raw escape the `bump!=0` arm of the same function already used for this exact reason.

### ⭐ DEFECT #2 — `fc_walk_range` zeroed a carve that `zd_k` actually emits (SCRIP `93fbe1e2`, ONE LINE)
**`lower_snobol4.c` `fc_walk_range()`'s `IR_LIT_INTEGER`/`IR_LIT_STRING`/`IR_LIT_REAL` arm contributed 0 to `fp`** — the footprint sum that becomes `op_fc_disp`. Those three kinds are **not** in `zd_k`'s K=0 exception list (`emit.cpp` ~2005), so the universal ZD arm (`emit.cpp` ~841: `g_zd_arm` → `op_zres=1`, `op_fc_bytes=g_zd_k=16`) **unconditionally carves 16 bytes** for them. The `fc_geom` check one line above is a *different, narrower* authority (`fc_vlit_active`-gated) that a pattern primitive's constant argument — the `14` in `TAB(14)` — misses, while still being admitted by `lit_ok` and still carving.

**Two authorities for ONE carve decision, disagreeing — the exact `s22k` "spelled twice" class this tree's own law forbids.** `op_fc_disp` came out 16 short *per uncounted literal argument, for the whole containing statement*, so MATCH_END's writer and `bb_match_replace`'s reader computed RSP-relative addresses against different depth assumptions and missed each other. Fix: count what the ZD arm actually carves (`*fp += 16`), rather than re-deriving it from `fc_geom`'s narrower eligibility.

⛔ **THIS RETIRES A STANDING CLAIM, DO NOT INHERIT IT:** L-3's text and the s36 record both assert **"`l3_spl_pos` reads the fully correct slot and STILL fails ⇒ POS/RPOS confirmed a third, independent defect."** **FALSIFIED.** `pos` flipped PASS on this one-line LOWER fix along with `tab_nonterm`/`rtab_nonterm`/`tab_linear3`. There was no third defect. The "reads the correct slot" observation was true and the inference from it was wrong — the slot was right and the *depth the reader assumed* was wrong, which a slot-level check cannot see.

### ⛔⭐ PROVENANCE — THE ONE INVARIANT WAS VIOLATED AGAIN, AND THIS TIME I CAN NAME BOTH HALVES (5th recorded: s34, s35, s38b, s40, now s43)
**s42's cursor below describes my session's work** — my mechanism, my numbers (11/13, 264/336, 257/336), my BAL trio, and my commit hash `3d223c12` — and states plainly that its author never issued the commit. **I issued it.** Conversely, the two diagnostics that made defect #1 findable (`SCRIP_ARB_DIAG` in `bb_match_arb.cpp`, `SCRIP_ZOP_DIAG` in `x86_asm.h`) were **already in my working tree, uncommitted, when I started**, and I recorded at the time that I assumed they came from "a prior session." They came from s42, live, concurrently. So: **s42 built the instruments, s42 and I both independently traced the same root cause, and I landed the commit s42 then observed and could not account for.** Both write-ups are honest; neither is plagiarism; the *duplicated spend is real* and is the cost s40 predicted in writing. Both diagnostics are retained in-tree deliberately (env-gated, additive-only) — they earned it.

### NEXT RUNG — in this order
1. **`git push` both repos** the moment a credential exists. Nothing below matters until this lands; s39 lost a session to exactly this.
2. **L-4 (061 variable-arg pattern-primitive class) is now the top open item, and it is very likely the SAME defect as #2.** L-4's own text says "the dynamic arm reads a cell the arg never landed in (whole class, not POS-specific)" — that is a *depth* symptom, and defect #2 is a depth-accounting gap in the arm that handles primitive *arguments*. ⛔ **Re-measure 061 at this HEAD before spending anything on it.** It may already be fixed.
3. **Audit `fc_walk_range` for the same class of gap in its OTHER arms.** I fixed the arm I had a witness for. The `switch` at `lower_snobol4.c` ~1093 has a `break`-with-no-`fp`-contribution for `IR_MATCH_LIT/LEN/ANY/NOTANY/POS/RPOS/ATP/ASSIGN_SAVE/ASSIGN_COND/ASSIGN_IMM/GOTO`. I verified against `zd_k` that the `MATCH_*` ones are genuinely K=0 — **but `IR_MATCH_ASSIGN_SAVE` is K=16 in `zd_k`** (its own comment says so: "IR_MATCH_ASSIGN_SAVE stays K=16"). That arm may be a live second instance of defect #2. **This is the highest-value cheap probe available right now:** mint an l3-style witness with a capture (`SPAN('e') . V`) inside a splice statement and see whether it reproduces the same writer/reader miss.
4. Only then L-1 (Defect A), honouring its ⛔ (fixing A alone RAISES the hang count — do not revert on that signal).

### ⭐ PLAN SCRUTINY (s43) — four items, two of them cheap and high-value
1. ⛔⭐ **THE ONE INVARIANT STILL HAS NO MECHANICAL ENFORCEMENT AND HAS NOW COST FIVE INCIDENTS.** s40 wrote the fix (`SEAT-LIVE-<SEAT>.json` + heartbeat + refuse-to-start), Lon has not been asked for a decision on it since, and it has not been built. **I checked: no `SEAT-LIVE-*` file exists in `.github`.** This session is the first where the duplication is *fully documented from both sides* — s42 and I each independently paid for the same root-cause hunt. **Lon: this is one small script and it converts an invariant nobody can see into one nobody can violate silently. I second s40's ask without reservation and would build it on request.**
2. ⛔ **`board_earn0_set.sh`'s m4 arm is STRUCTURALLY BROKEN for the l3 suite and reports it as 14×FAIL.** It captures `scrip --compile`'s **stdout — which is assembly text** — and diffs that against a `.ref` holding expected *program output*. It never assembles, links, or runs. So m4 reads all-FAIL including known-good controls like `len_pure`. **Every "m4 UNMEASURED / BOARD B-0 owns it" note in this file is downstream of this, and the fix is small:** borrow the `compile_mode4()` function from `scripts/test_broad_corpus_snobol4.sh`, which does the assemble→link→run correctly. Until then, ⛔ **do not read this script's m4 column as evidence of anything.**
3. **s40's item 3 is now MEASURED, not just predicted.** It warned that a seat told to clone ".github, corpus, SCRIP" gets no oracle and the board then prints a plausible all-FAIL table. That is exactly what happened to me — I hit it, recognized it from s40's note, and cloned `x64` by hand. **The note saved me a wrong conclusion; the underlying gap is still open.** Fix is one line in the board script (`[ -x "$SBL" ] || { echo "ORACLE MISSING"; exit 2; }`) plus adding `x64` to the standard seat instruction in `PLAN.md`.
4. **The `.s` regen scripts silently no-op'd on a missing git identity and printed "Committed."** `util_regen_demo_s_artifacts.sh` hit `Author identity unknown` in the **corpus** repo, printed the failure to stderr, and then printed `  Committed.` anyway — leaving 13 staged-but-uncommitted files that would have been invisible at handoff. `REPO-SCRIP.md`'s session-start block sets `--local` identity for **SCRIP only**; nothing sets it for **corpus**, which every regen script also commits to. **Two cheap fixes:** add the `git config --local` pair for corpus to the session-start block, and make the regen scripts check the commit's exit status before claiming success.

---
## ⭐ s42 record (retained — INDEPENDENT, CONCURRENT derivation of defect #1; see s43's PROVENANCE above for how this and s43 relate. Its analysis is correct and its "still open" list is superseded only by s43's defect #2.)

## ⭐ LIVE CURSOR — 2026-08-12 s42 (Claude Sonnet 5). **L-3b ARB/BREAK: FIXED AND LANDED.** SCRIP at `3d223c12` (pushed — see push status below). l3 board independently re-verified fresh: **11 PASS / 2 FAIL** — correction, 11/13, FAIL = `pos`, `rtab_nonterm`, `tab_linear3`, `tab_nonterm` (all four are the carving class, exactly as expected, none touched by this fix). Broad SNOBOL4 corpus independently re-verified fresh: mode-3 **PASS=264/336**, mode-4 **PASS=257/336**. Both numbers reproduced exactly what the landed commit message claims — I ran the boards myself from a clean build, not by trusting the commit's prose.

### s42 — the ACTUAL root cause is one level below where s41 (below) was looking, and it's already fixed
**s41's diagnosis of the SYMPTOM was correct in every particular** (ARB writes its own extension counter into `x86_scratch_off+0`, BREAK writes its own post-match cursor into the same relative slot, MATCH_END's read collides with whichever one is there) — **but the root cause is one level lower than s41's fix targeted.** s41 proposed adding a brand-new stable `match_start` slot at MATCH_BEGIN's `op_off+8` and rewiring both MATCH_BEGIN's write and MATCH_END's read to use it (three attempts, all reverted, see s41's record below — kept verbatim, it is good work and the next-lower root cause does not make it wrong, just unnecessary).

**What actually broke:** `x86_zop()`'s regime-2 branch (`x86_asm.h` — the per-BB FORTH-cell window arm every match-primitive's OWN scratch cell uses, including ARB's counter/cursor pair) resolved its offset correctly exactly once (`off - op_fc_base + bump` → `0` for ARB's counter cell, confirmed by direct instrumentation), then formatted the answer as a plain `"dword ptr [rsp + 0]"` string. That string is BYTE-IDENTICAL to what `x86_fr32_prefix()` (the regime-4 raw-rsp spelling) produces on an unpinned graph. `x86_parse`'s classifier checks the regime-4 prefix FIRST, so it silently reclassified the already-resolved regime-2 address as an unresolved flat ZLS coordinate and ran it through `x86_frame_off()` a SECOND time, adding `op_zdepth` (16, for the one un-popped `sub rsp,16` match-primitive predecessor) on top of an answer that needed no further compensation. ARB's counter cell landed 16 bytes past its own window — exactly the fixed address MATCH_END's writer independently targets by design (`op_off+op_fc_disp`) — so MATCH_END picked up ARB's own counter instead of any cursor. **s41's `raw_start=2`/`raw_start=11` readings were measuring the effect of this bug, correctly, one layer downstream of its cause.**

**Why this explains SPAN's accidental pass** (s41 found this too, independently, same conclusion): SPAN's chain-mode arm never writes its own `scratch+0` — only `+4` — so the double-displaced `+0` slot holds whatever `start_δ` (MATCH_BEGIN's own retry cursor, one full frame away) happens to leave there, which for SPAN's witnesses is coincidentally the true start. Not a convention, an accident — confirmed by both seats independently.

**The fix (already landed, one line):** regime-2 now spells the SAME `"[rsp# + N]"` raw-machine escape the `bump!=0` arm of the same function already used for exactly this reason (see the adjacent ARGREAD land-mine comment, witness 083) — so `XK_RSP32`/`XK_RSP64` claims the string first at parse time and `x86_frame_off()` never runs on an already-resolved regime-2 address. Zero change to MATCH_BEGIN/MATCH_END/bb_match_arb.cpp/bb_match_break.cpp themselves — the fix is entirely inside the ONE operand-address authority, so it applies uniformly to every regime-2 consumer (SPAN/TAB/RTAB/BREAK/BAL/REM), which is presumably why BAL's three programs (`157_pat_cap_arb_alt_keep`, `174_pat_bal_manual_example`, `176_pat_bal_balanced_forms`) flipped PASS too, outside the l3 board entirely.

⛔ **PROVENANCE (Claude Sonnet 5, s42, same container as s41):** I built the diagnostic instrumentation and traced the root cause across several rebuild/measure cycles in my own transcript. The `git commit` that actually landed the fix (`f21e3215`→`3d223c12` after a `pull --rebase`) does not appear in my own tool-call history — I never issued `git add`/`git commit` this session. I independently reverified every claimed number (fresh build, fresh l3 board, fresh broad-corpus run, from my own clean checkout) before trusting or building on it, and all of them reproduced exactly. Per the s40 precedent in this same file: naming this plainly rather than silently absorbing it into my own narrative or silently taking credit for someone else's tree state. The most likely explanation, per s40's own standing ask to Lon, is a second live LOWER-adjacent seat in this container — possibly s41 itself continuing past its own written handoff, possibly a third seat. Whoever committed it, the fix is independently verified correct and is not being contested.

### Still open after s42
Carving class (TAB/RTAB/POS/RPOS) untouched by design — separate defect, own conviction needed, not addressed by this fix (confirmed: those four still FAIL on the freshly re-run l3 board). L-1/L-2/L-4/L-5 untouched. m4 arm of the l3 board specifically still not measured against oracle per-probe (broad corpus mode-4 total moved 255→257, consistent, but that corpus may not exercise every l3 shape) — BOARD B-0 still owns the m4 harness per every prior cursor's note.

---
## ⭐ s41 record (retained — correct, careful symptom diagnosis; its proposed fix was never landed and is now superseded by s42's lower-level root cause above, but the analysis is good and worth keeping for the "why doesn't the naive `op_off+8` idea work" reasoning alone)

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

---
## ⭐ LIVE CURSOR — 2026-08-12 s41 (Claude Sonnet 4.6). **L-3b ARB/BREAK: ROOT CAUSE FULLY CONFIRMED, FIX NOT YET LANDED.** SCRIP at `7eac50a9` (s39's push confirmed on origin — the "push blocked" note in s39 was stale; fresh clone shows `7eac50a9` already at `origin/main`). l3 board re-proved at session start: **8 PASS / 6 FAIL** (matches s39 exactly, floor re-established by running, not transcribed). Context consumed: ~78% at handoff.

### s41 record — root cause fully diagnosed, three fix attempts reverted, clean handoff

**THE ROOT CAUSE OF ARB/BREAK's `start=wrong` is now COMPLETELY UNDERSTOOD, measured, and confirmed:**

`MATCH_END`'s read of `RDD("rsp", op_fc_disp)` (the instruction `mov eax, dword ptr [rsp + 16]` in the emitted `.s`) is architecturally wrong — the cell it reads is NOT a stable "match start cursor" slot. It is the **last-carved match-primitive's own `fc_geom` scratch cell, offset+0**, whose contents are defined by that primitive's own template — not by any start-cursor convention:

- **SPAN** (PASS, accidentally): its chain-mode arm never writes its own `scratch+0` (`[rsp+20]` only) — so `start_δ`'s value (the unanchored retry cursor, which IS the correct match-start by construction of the retry loop) happens to survive untouched underneath. ACCIDENTAL correctness.
- **ARB** (FAIL, `start=2`): `bb_match_arb.cpp` explicitly zeros `FR(x86_scratch_off+0)` then increments it as an extension counter. That counter reaches 2 in `arb_nonterm` (ARB extends twice before `'g'` matches). MATCH_END reads `2`, not `10`.
- **BREAK** (FAIL, `start=11`): `bb_match_break.cpp`'s success arm stores `r14d` (the post-`ANY('+')` cursor = 11) into `FR(x86_scratch_off+0)` as its own internal bookkeeping. MATCH_END reads `11`, not `10`.

**Confirmed by runtime instrumentation** (`SCRIP_REPL_TRACE=1`): `arb_nonterm` → `raw_start=2 raw_end=14`; `break_nonterm` → `raw_start=11 raw_end=14`; `span_nonterm` → `raw_start=10 raw_end=14`. End is correct in all three. A temporary `SCRIP_MEND_RUNTIME_DIAG` probe (built, used, reverted before handoff) confirmed the value sitting at `[rsp+op_fc_disp]` at that exact point is literally the extension counter / scan-offset, not any cursor.

**The correct source of the start cursor IS `start_δ`**, which is: (1) initialized to 0 by MATCH_BEGIN, (2) incremented by the unanchored retry loop until `ANY('+')` succeeds, (3) copied into `r14d` right at the top of `L(0)` (`mov r14d, FR(_.op_off)`) — the exact moment before `x86_gamma()` jumps into the pattern body. At this point `r14d` = 10 for these witnesses. `start_δ` lives at `FR(_.op_off)` / `[rsp+0]` inside MATCH_BEGIN's own 32-byte `hfc` frame.

**The fix must do two things:**
1. **Write** `r14d`'s value (= `start_δ`, = correct match-start) into a stable cell at MATCH_BEGIN's `L(0)` — one that CANNOT be clobbered by any match-primitive's `fc_geom` scratch cell.
2. **Read** that stable cell in MATCH_END (and nowhere else — MATCH_REPLACE already reads from what MATCH_END stores into the post-restore RSP-relative slot, so fixing MATCH_END fixes MATCH_REPLACE automatically).

**The stable cell: `op_off+8` inside MATCH_BEGIN's own 32-byte hfc frame.** This slot is confirmed free:
- `op_off+0` = `start_δ`, `op_off+16` = `rsp_mark` — both documented and used.
- `op_off+8` = explicitly vacated by W-1c.3 (the patstk slot-save was deleted); this file's own comment at line 71 AND `bb_match_end.cpp:97` both name it as vacated.
- NEVER touched by any `fc_geom` grant (all primitive carves allocate ABOVE this 32-byte frame; the 32B carve is MATCH_BEGIN's own `x86_zclaim(32)`, which completes before any primitive runs).

**The addressing problem that defeated three fix attempts this session:**

`FR(op_off+8)` uses `x86_frame_off`, which adds `op_zdepth` — a **per-node-local** term ("the bytes THIS box carved on RSP", per `emit.h`). MATCH_BEGIN's `op_zdepth` and MATCH_END's `op_zdepth` are different. So `FR(op_off+8)` resolves to DIFFERENT absolute addresses at MATCH_BEGIN's write site vs MATCH_END's read site. This was verified empirically: with `FR(op_off+8)` used at both sites, emitted `.s` showed both targeting `[rsp+8]` symbolically, but RSP differs by the primitive's `fc_geom` carve (16B for SPAN/ARB/BREAK) between the two points → wrong absolute address → `raw_start=0` for ALL witnesses (worse than before).

**The correct addressing scheme for the write side:** At MATCH_BEGIN's `L(0)` write site, MATCH_BEGIN's own 32-byte carve is the ONLY carve open — RSP sits exactly at MATCH_BEGIN's own frame base. So `[rsp+8]` at that point IS `op_off+8` with zero further compensation needed. Use **raw `RDD("rsp", 8)`** (or `RSD(8)` if that helper exists), not `FR`.

**The correct addressing scheme for the read side:** At MATCH_END, `op_fc_disp` (computed by `fc_walk_range` / `fc_head_register` as the explicit sum of all `fc_geom` K-values for primitives in the pattern range) correctly tracks the accumulated carve depth — this is already proven by the fact that `end`'s stash (`RDD("rsp", op_off+op_fc_disp+32)`) is correct for all witnesses. The read should be `RDD("rsp", op_fc_disp + 8)` — i.e., the SAME `op_fc_disp` compensation as the existing correct code, but displaced by 8 into the frame (the new `match_start` slot) rather than by `op_off+32` (the old clobbered `start_δ`-aliasing slot).

**Pseudo-code for the two-line fix:**

In `bb_match_begin.cpp`, immediately after `+ x86("note", "start_δ") + x86("mov", "r14d", stfh() ? HKD() : FR(_.op_off))` and before `+ x86_gamma()`:

```cpp
+ x86("note", "match_start") + x86("mov", RDD("rsp", 8), "r14d")
```

In `bb_match_end.cpp`, replace the old `x86("mov", "eax", RDD("rsp", (int)_.op_fc_disp))` with:

```cpp
x86("mov", "eax", RDD("rsp", (int)(_.op_fc_disp + 8)))
```

(Only the `rfc()` arm, only the `ZC_FRAME_RSP` path — `op_dval != 0.0` gate, same as before. The `stfh()` legacy arm's read `x86("mov", stfh() ? HKD() : FR(_.op_off), "eax")` may need its own HKS() twin for `+8` on the negative-rbp side, OR may be safely left as-is if `stfh()` graphs never reach the op_dval branch — verify before touching.)

**WARNING: `RDD("rsp", 8)` at MATCH_BEGIN's write site is only correct on the `hfc()` arm** (the FORTH-spine + FC-window arm that allocates the 32-byte frame). The `stfh()` arm uses a different frame entirely. Gate the new write on `!stfh()` (or equivalently `hfc()`), same as how `rsp_mark`'s write is gated, and handle `stfh()` separately if needed.

### Instrumentation that confirmed the root cause (reverted before handoff, rebuild to verify board is clean)

- `SCRIP_REPL_TRACE=1` (already wired in `gen_runtime.c`) → exact `raw_start`/`raw_end` per call. Use this.
- `SCRIP_MEND_RUNTIME_DIAG` probe: a temporary `mend_rt_diag(long)` extern + call sequence inserted at the `RDD("rsp", op_fc_disp)` read site to print the value at that exact instruction. Built, confirmed 2/11/10 for ARB/BREAK/SPAN respectively, then reverted. Do not re-add; the root cause is fully understood.

### NEXT RUNG (what the next seat should do immediately)

1. **Re-prove the l3 board floor** (`EARN0=/home/claude/corpus/probe/l3 bash scripts/board_earn0_set.sh m3`) — confirm 8/13 before touching anything.
2. **Land the two-line fix** as described above. Key: `RDD("rsp", 8)` at MATCH_BEGIN write-side (raw, pre-primitive-carve RSP); `RDD("rsp", (int)(_.op_fc_disp + 8))` at MATCH_END read-side.
3. **Rebuild and run the l3 board** — expect `arb_nonterm` and `break_nonterm` to flip to PASS. Expect no regression on SPAN/LEN/REM/LIT_LEN controls.
4. **Run `SCRIP_REPL_TRACE=1`** on `arb_nonterm` and `break_nonterm` — confirm `raw_start=10` for both.
5. **Run the broad SNOBOL4 corpus** (both modes, both directions, diff FAIL sets — not just counts) per GATES.
6. **Commit and push** (credential: supplied by Lon at session start — ask if not provided).

### Context / register usage note

`r9` was used as the staging register for the match_start value in the attempted (reverted) MATCH_END fix. Check what `r9` holds at MATCH_END's α before committing to it — may need a different callee-save register if `r9` is live with something else at that point in the graph. Alternatively, read directly into `eax` (clobbering the old `mov eax, RDD(...)`) and immediately store into the stash slot, with no staging register needed.

