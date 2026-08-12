# GOAL-SN4-HOME-LOWER — front-half correctness: LOWER + splice (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** every SNOBOL4 wrong-answer whose owner is `lower_snobol4.c` or the replace/splice arithmetic. **ZERO emitter frame-arm bytes** — that surface is the RBP seat's; this partition is what makes P1 four-way concurrent.

**LAWS THAT BIND HARDEST HERE:** MONITOR-FIRST (RULES §1) · anti-pattern §2 (never guess an offset — instrument) · s29 STANDING INSTRUMENT RULE (state what the defective arm would print; every board carries a known-PASS control row) · judge BY SET vs BOARD's P0 floors.

## RUNGS
- [x] **L-0 · WITNESS FLOOR — LANDED s33.** Board adopted and MECHANISED as `SCRIP/scripts/board_earn0_set.sh` (m3/m4/both; `REPEAT=n` reports a row whose verdict is not constant as **FLAKY**, never as whichever arm came up first — `earn0_stored_capture` is the known member and a single-shot board misleads by design). All four controls PASS at HEAD. Floor table in the LIVE CURSOR; re-RUN the script, never transcribe it (STALENESS LAW).
- [ ] **L-1 · DEFECT A — PRODUCER ELISION (LOWER, convicted by knob `SCRIP_PAT_INLINE=0`).** Why is a use inside a stored composite not an inlining site, and why is the producer elided before that is known? Fix in LOWER. ⛔ **FIXING A ALONE LOOKS LIKE A REGRESSION** — silent rc=0 passes become rc=124 hangs as the mask comes off (measured s29 §2b). Judge BY SET against the FINDING table; EXPECT the hang count to RISE; a seat that reverts on that signal reverts a correct fix. `SCRIP_PAT_INLINE=0` stays a diagnostic discriminator ONLY.
- [ ] **L-2 · DEFECT B — THE CONSUMER HANG A WAS MASKING.** Mint the default-arm witness FIRST (unreachable today until A lands); then MONITOR-FIRST; the s29 bounded probes say match-time, inside one statement, plausibly unbounded allocation (`[ZHP] heap exhausted` sibling arm — plausible, NOT established; cross-check with HOME-RBX X-4).
- [x] **L-3 · C-9 RESIDUALS — ROOT-CAUSED s35 (FINDING-2026-08-12f). Reader defect, 16B low. Fix = L-3b.** ⛔ **THIS RUNG'S OLD TEXT IS SUPERSEDED — three of its claims are now falsified, do not inherit them:** (i) *"no displacement of any sign or slope can fix it; find the WRITER"* — the writer was never missing (`MATCH_BEGIN` writes `head.cursor` ZLS+48, `MATCH_END` writes `head.end` ZLS+72, correctly, in passing AND failing shapes); a **principled** displacement (the replacement subtree's footprint) is exactly the fix, though no **constant** one is. (ii) *"start=constant 3"* is the **DESCR type tag `DT_I`=0x03** of MATCH_BEGIN's result cell at ZLS+32 — flat because a tag has no cursor semantics; and *"end=slen"* is a **`zeta_mark` GC pointer clamped** by `c_rt_match_replace`. (iii) *"`op_zpat`=0 for POS/RPOS, still splice [0,1)"* — `l3_spl_pos` reads the **CORRECT** slot (start_off 64) and still fails, so POS/RPOS is a separate defect and `op_zpat` is not its discriminator. **TAB/RTAB now suspect as the SAME defect:** `tab_nonterm` reads at 48 with the class; only its `end` is correct. ⛔ **Re-measure TAB after L-3b lands BEFORE spending anything on s41's Series-T displacement theory — it may fall out entirely.**
- [ ] **L-3b · THE FIX — ⛔ REWRITTEN s37; ITS ORIGINAL PREMISE WAS FALSE.** ~~Un-guard the C-9 REPL-ZDEPTH correction / find why the replace node declines ZD~~ — **the node does NOT decline (measured), and `op_zdepth` is not read by this template (verified in `x86_zop`).** Both claims are dead; see the LIVE CURSOR's falsified-claims list before touching anything. **The rung is now: L-3b STEP-0′ — build the runtime-RSP instrument, establish whether the true cursor is ever stored near the read address, and only then consider arithmetic.** ⛔ **THE DISPLACEMENT FAMILY IS EXHAUSTED**: three variants (`-op_zpat`, `+op_zfc+32`, `+op_zfc`) yield `start` = 3, 0, 18 where 10 is correct — do not tune a fourth. ⛔ **NEVER HARDCODE 16** still stands. Concat witness exists (`corpus/probe/l3/l3_spl_span_concat.sno`); **`P8_concat_repl` NEVER EXISTED** — do not hunt it. Codegen rung ⇒ regen ×3 + both-mode gates apply **if and when emitted bytes actually change** (s37 changed none).
- [ ] **L-4 · 061 — VARIABLE-ARG PATTERN-PRIMITIVE CLASS.** The dynamic arm reads a cell the arg never landed in (whole class, not POS-specific). MONITOR bracket exists per s39b — read that cursor first, do not re-spend.
- [ ] **L-5 · `test_string` SECOND COMPONENT.** Capture also wrong (`r=[   hello]`) — NOT the splice signature; alternation-arm / post-SPAN cursor suspect, unconvicted. Own witness, own conviction.

## GATES (every rung)
crosscheck/patterns + probe BY SET vs P0 floors, both modes · monitor divergence must MOVE PAST the fix · regen ×3 iff codegen touched (splice arithmetic counts) · FINDING per land mine · cursor move per handoff.

## ⭐ LIVE CURSOR — 2026-08-12 s37 (Opus 5). **⛔ L-3b's STEP-1 PREMISE IS FALSIFIED: THE REPLACE NODE DOES *NOT* DECLINE THE ZD ARM, AND THE C-9 `op_zdepth` FIX IS WIRED TO A CONSUMER THAT DOES NOT EXIST.** Three displacement variants tested and all three FAIL — the defect is NOT a displacement at all. Board re-measured at HEAD: **3 PASS / 10 FAIL, identical BY SET to s36's floor** (no regression, no gain). **ZERO emitted-byte change this session** (diff audited line-by-line + board re-run + `x86("mov",…)` args character-identical). FINDING-2026-08-12h. **NEXT RUNG: L-3b STEP-0′ — see "WHAT THE NEXT SEAT MUST DO FIRST" below; do NOT resume displacement arithmetic.**

### ⛔⭐⭐⭐ FOUR INHERITED CLAIMS FALSIFIED THIS SESSION — DO NOT RE-SPEND ON THEM

1. **"Find why the replace node declines the ZD arm" (L-3b step 1, s35+s36 NEXT-SEAT item #1) — VACUOUS. IT DOES NOT DECLINE.** Measured `SCRIP_ZD_DIAG=1` on `l3_spl_span_nonterm`: the whole `h=4` run admits, `IR_MATCH_REPLACE` at `i=12` arms with `zout=48`, **no DECLINE line at all**. `zd_wl_kind` returns 1 unconditionally for SN4 — emit.cpp:1909 short-circuits (`if (!(icn_cells_graph || pl_cells_graph)) return 1;`), so the entire per-kind whitelist below it is **Icon/Prolog-only and structurally unreachable from SNOBOL4**. There is no guard to find. The 64-group/48-group split has a different cause.
2. **The C-9 `op_zdepth` correction (emit.cpp:841) CANNOT REACH `bb_match_replace`.** The template reads `FR`/`FRQ` → `x86_zop()` (x86_asm.h:1021), and **`op_zdepth` appears nowhere in `x86_zop`**. It is read only by `x86_ztos`/`ZTOS` — a different accessor family this template never calls. Three sessions of cursor text describe `FRQ` as `[rsp+off+op_zdepth]`; **that is false at HEAD.** The template's only live lever is `op_zpat`.
3. **`op_zpat` IS NOT THIS CLASS'S FIELD.** Its own `emit.h:627` authorship comment scopes it to *"PATTERN-INTERIOR match primitives (**TAB/RTAB/POS/RPOS**)"* — i.e. the **carving** class s36 correctly split out. Its backward-scan predicate (`op >= IR_MATCH && op <= IR_MATCH_VALUE`) is **broader than its documented intent** and incidentally sums SPAN's K=16, which is why it reads nonzero for non-carving witnesses. `zpat=16` on a SPAN witness is a **formula artifact, not evidence**.
4. **"`fc_head_fp` is dead code" — MY OWN ERROR, RECORDED SO IT IS NOT REPEATED.** I concluded this from a 2-file grep. A full-tree grep finds the live registrar at **`src/lower/lower_snobol4.c:1828`** (`fc_head_register(head, fp_stmt)`). `fc_head_fp` returns real values (**16** for SPAN, **0** for pure-LEN) and is genuinely load-bearing. ⛔ **Grep the whole tree before declaring anything dead.**

### ⭐ THE MEASUREMENT THAT MATTERS (five new instruments, all env-gated, all landed inert)
`SCRIP_ZPAT_DIAG` · `SCRIP_REPL_ADDR_DIAG` · `SCRIP_MEND_ADDR_DIAG` · `SCRIP_EDRIVE_END_DIAG` · `SCRIP_FCDISP_DIAG`. Writer and reader, same run, same coordinate system:

| witness | `op_fc_disp` (=`fc_head_fp`) | WRITER stores at | READER loads at | delta |
|---|---|---|---|---|
| `len_pure` (**PASS**) | 0 | `rsp+80` / `rsp+104` | `rsp+48` / `rsp+72` | **32** |
| `span_nonterm` (FAIL) | 16 | `rsp+96` / `rsp+120` | `rsp+32` / `rsp+56` | **64** |

Writer formula (bb_match_end.cpp, `rfc()`+`ZC_FRAME_RSP` arm, **confirmed live**: `rfc=1 zc_frame=2` both witnesses) = `[rsp + op_off + op_fc_disp + 32]`. The reader has **neither** term.

⛔ **THE PASSING ROW IS THE KEY AND IT KILLS THE WHOLE DISPLACEMENT FAMILY.** `len_pure` reads **32 bytes below where the writer wrote** and is *correct*. So RSP is **not** equal at the two program points, and "make the reader's N match the writer's N" is the **wrong target**. Three variants tested, all FAIL, each with a *distinct* wrong `start`: `-op_zpat`(HEAD) → `start=3`; `+op_zfc+32` → `start=0`; `+op_zfc` → `start=18`(slen). Correct is `start=10`. **A quantity that lands 3, 0, and 18 while never landing 10 is not a displacement that needs tuning — the reader is reading a cell nobody wrote the cursor into.** This is s34's *"find the writer, not an offset"* instinct, re-earned the hard way after s35 prematurely discharged it.

### ⛔⭐ WHAT THE NEXT SEAT MUST DO FIRST — L-3b STEP-0′ (ordering is the whole point)
1. **PROVE THE RSP DELTA, DO NOT ASSUME IT.** Everything above is emit-time constants. Nobody has measured **actual runtime RSP** at `MATCH_END`'s store vs `MATCH_REPLACE`'s load. Until that delta is a measured number, every offset comparison in this goal file (mine included) is two coordinate systems in a trench coat — the 7th conviction, which I re-committed in a new form. ⛔ **No gdb in the container** (`gdb: not found`, s37) — so the instrument must be an emitted `mov rax,rsp` + call to a trace helper at both sites, or `SCRIP_REPL_TRACE`-style runtime capture. Build that first; it is the missing instrument, and it is cheap.
2. **THEN ask whether the writer ever stores the true cursor at all.** `raw_start` has now been observed as 3, 0, and 18 across three read addresses — consistent with *no* nearby cell holding 10. Instrument `MATCH_END`'s **value** (the `eax` it stores, from `RDD("rsp", op_fc_disp)`), not just its address.
3. **Only then consider arithmetic.** And if a fix needs a carrier surviving the per-node reset, `op_zfc`/`g_zd_zfc` is **already staged and printed** at the `g_zd_zpat` choke (emit.cpp) — wire a consumer, do not re-derive the plumbing. It is deliberately a **separate field from `op_zpat`**, so the carving class stays uncoupled per s36's ruling.

**HOW TO RUN THE BOARD** (the `[` builtin mis-parses the bracketed output — cost me a false all-FAIL read): use `[ "$g" = "$w" ]`, never `==`, and `tr '\n' '|'` before printing.

⛔ **`x86("comment", …)` IS A GUARANTEED EMPTY STRING** (x86_asm.h:1590, SN4-ASM-CRIT/s173 — *"BB emissions are COMMENT-FREE"*). A diagnostic written that way is **silently inert, not broken**. Use `fprintf(stderr,…)`. Cost me a build cycle.

⛔ **`FR`/`FRQ`/`x86_zop` return a shared static rotating buffer** (`static char b[16][48]`). Capture into a `std::string` **immediately**; re-deriving the same expression later in a chain can read an aliased slot.

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

### NEXT SEAT, IN ORDER
1. Find why the replace node declines the ZD arm for the non-carving class (`zd_on[i]`, emit.cpp:2656) — the single guard separating the 64-group from the 48-group.
2. Land the subtree-footprint correction via `g_zd_wpop` (never a literal 16); gate on `P8_concat_repl` AND l3 board rows `{span,arb,break,rem,VACUOUS}_nonterm` AND probe/bb BY SET. **Expect `{tab,rtab}_nonterm`/`tab_linear3` to remain FAIL — not a regression, they are a different defect.**
3. Before touching the carving class at all: mint a same-box-count PASS/FAIL control pair for TAB (e.g. two-box `LEN(n) LEN(m)` replace, no var-length primitive) — none exists yet, and TAB's raw offsets (`op_sa`=192) are not comparable to SPAN's (`op_sa`=176) without one.
4. Only then `bal` (own row, untouched), then L-1 (Defect A) — honouring its ⛔ (fixing A alone RAISES the hang count).

**UNBLOCKS:** LOWER L-3 non-carving sub-class fix-ready; carving sub-class explicitly NOT unblocked — a future seat should not inherit s35's TAB hedge as settled fact. **m3 only — this board's m4 arm is UNMEASURED, not green; BOARD B-0 still owns it.**

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

### ⛔⭐⭐⭐ TWO-SEATS ALARM (s35) — THE ONE INVARIANT FAILED AGAIN, SECOND SESSION RUNNING
s34 recorded two live LOWER sessions and asked Lon to retire one before re-firing. **It was not resolved and it recurred:** SCRIP `67e9383c` (local, unpushed, `ahead 1`) landed in s35's tree citing `FINDING-2026-08-12f/g` — `f` was minted by s35 minutes earlier and **never pushed**, so it was read from a shared tree, and `g` is not s35's. No work appears lost and the halves are again COMPLEMENTARY (s35 = root cause + witness; the other = the trace instrument) — **but that is luck, not the invariant.**
⛔ **Lon: this needs a DECISION, not a third note.** Either (i) retire one LOWER session before re-firing, or (ii) accept LOWER as two seats and **SPLIT THIS FILE** along the cut s33b/s34 already discovered independently: **splice / `start`-`end` arithmetic (L-3, L-3b, L-4)** vs **capture / alternation (L-5 + the `cap_after_*` rows)** — s34 proved these are two defects with no shared authority, which is exactly what makes the split safe. HOME's ONE INVARIANT is a human-scheduling rule and RULES 2026-08-10 cannot fix it: that rule abolished scheduling for *files*, not for *seats*.
