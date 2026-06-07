# HANDOFF — BB-FIXUP 17th attended run (Opus 4.8), 2026-06-07

Lon attending ("your choice, continue" ×3, context checks at ~70/60/38% remaining; "perform hand off" at ~25%). All stops fully closed. SCRIP @ `4bfe09b` verified local==origin. Goal watermark landed `.github c2def82b`; this doc + HANDOFF line follow.

## SESSION OPEN

Baseline matched the 16th-run close watermark exactly: rank 878, 34 dirty / 72 clean, emit-blind 235, all gates at floors (smoke m4 7/7 HARD · pat M4=18, 053 pre-existing SKIP · icon m2 12/12 HARD, m3=m4 10/12 proc_zeroarg/proc_recursion pre-existing · purity 2-floor · bin_t 0 · vstack 3 · sno_pat_reg TIER1+TIER2 HARD · prove 68 PASS + 3 inherited FAIL, the law-5 trio). Corpus repo cloned fresh (icon suite needs /home/claude/corpus). CHOICE STATED AT OPEN per the 14th-run correction: hold the cursor — subject/succeed cheap, succ_plus rb=25 as the substantial stop; FIX-4/FIX-3 left next-in-queue for live veto. No veto.

INHERITED-RED OBSERVED IN PASSING (not in this goal's battery, law 5, owner ICON-BB): `test_gate_icn_var.sh` FAILs on untouched origin HEAD — rung21/25 global-family m4 FAILs + rung13_alt/16_subscript/23_table/24_records m2 FAILs. Recorded; untouched.

## THE STOPS

**1. bb_subject 9c14a1d ✅ v2 9→0.** ef 1→0 (emit_fmt→std::string concat; subj_name() is never-NULL so %s ≡ concat), pe 6→0 (PORT_*→literal Greek glyphs, `\xCE\xB2/\xCE\xB3/\xCF\x89` re-verified at head), lv 2→0 (`sa`→`_.op_sa` inline ×4 pure field reads; `len`→`(long)strlen(subj_chars())` inline — pure, single-site, type-cast preserved). Zero intern sites moved — splice-free per the 16th-run FOR-ladder finding, stated for the record. Guards + the NV push/align/call sequence verbatim. Proof: asm-diff EMPTY ×3 (pat corpus 039_pat_any/042_pat_break/043_pat_len; three-pattern normalizer bbN + RESOLVE(N) + .LcallN), SUBJECT VAR arm LIVE in all three .s, behavior A/B identical ×9 (e/hello/abc × m2/m3/m4-run, rc=0).

⛔ **ARM-REACHABILITY FINDING (tracker note at the entry — do not re-hunt):** the sole live IR_SUBJECT producer is `flat_drive_scan_native` (emit_bb.c), admission `MEDIUM_TEXT && !op_scan_pat_lit && IR_LIT(pBB).sval && sval[0] && !ival` = VARIABLE subject + non-literal pattern → only the VAR arm fires. The LITERAL arm (`subj_chars()` set) is DRIVER-UNREACHABLE on this head: `lower_subject_entry` (the other producer) is called only by `tools/prove_lower.c`. Probe shapes that do NOT fire this box, recorded to save future hunts: plain SNOBOL scan statements — literal-subject (`'hello' ANY('h')`) and var-subject-literal-pattern (`S "b" = "X"`) — both route the statement-level `IR_SCAN`/`rt_scan_lit` box instead. String-identity-by-construction is the literal arm's proof per the XK_SYM standard.

**PUSH RACE at stop 1:** IRD-3-CHAIN-2 `fec38d4` (2026-06-07 **20:50:51 UTC** — SNOBOL CALL arg-list → operands[], zero α/β usage end-to-end) landed mid-push. Rebased, FULL battery re-certified on the rebased head per 8th-run precedent, probe spot-check repeated, then re-pushed. `fec38d4` touched **two ring files** — `bb_call.cpp` and `bb_call_write_slot.cpp` (one-line dual-reads; its commit message explicitly coordinates: "BB-FIXUP owns BB_templates") — both **law-4 HOT until ~02:50:51 UTC 2026-06-08**. Its companion .github handoff `1cac02fd` (20:55:24 UTC) later raced this run's watermark push; rebased clean.

**2. bb_succeed c9e018e ✅ v2 3→0.** pe 3→0 (glyphs). The no-`x86_begin` wrapper shape left untouched per law 1 (bb_scan_stmt precedent — not "fixed").

⛔ **NEW PROOF STANDARD LANDED — OBJECT BYTE-IDENTITY:** A/B compile of the lone TU with the Makefile's CXXRT flag set **minus `-g`** (debug paths would differ) — `g++ -O0 -std=c++17 -finput-charset=UTF-8 <project -I set> -c bb_succeed.cpp` at B then A (stash), `cmp` the .o pair → **byte-identical**. Since `#define PORT_GAMMA "\xCE\xB3"` and the literal `"γ"` are the same two bytes, the preprocessor output is identical and the object proves it. Strictly stronger than asm-diff; supersedes the LIVE-probe requirement wherever the transform is macro↔literal or otherwise pre-compilation-identical. Use it for cheap glyph-only stops instead of arm-hunting. (Context: IR_SUCCEED is skipped by the xscan drivers and the flat arm at emit_bb.c:2125 is unexercised by smoke/pat/simple-prolog shapes; the arm hunt was stopped at budget once object-identity closed the question.)

**3. bb_succ_plus 4bfe09b — rb 25→0 (TOTAL 45→20).** Arrived COLD: IRD-2b window (eae6b0b 14:55:56 → 20:56 UTC) had lapsed **9 minutes** before arrival at 21:05 — the 15th-run handoff's lapse prediction verified by timestamp math (12th-run lesson applied). BOTH MEDIUM_BINARY arms converted bytes()→x86() under the corrected rule — succ (9 instruction groups) and plus (16): mov32 (BF/B9+imm32), movabs (48/49 B8|r+imm64), xor-rr (31/45-31), stk32 (off=0 → `C7 04 24` no-disp; off=8/16 → `44 24 disp8` — the modrm split re-verified at encoder source this head), RSP()-store64 (48 89 44 24 disp8), call-ro (48 B8 imm64 + FF D0), REX.W sub/add rsp, test eax,eax. `x86_lit_bytes` wraps DROPPED in _str — the x86() forms self-Lrec; 1-Lrec→N-Lrec framing is payload-identical per the bb_findall precedent.

**PROOF — the 12-shape A/B harness (transplantable recipe):** standalone .cpp including the REAL x86_asm.h (7th-run pattern); OLD builders = the verbatim byte streams parameterized on scalars (k,i,s triples — avoids fabricating post-IRD-2b IR_t/sidecar nodes); NEW builders = the x86() forms under test, same scalars; FIXED fake rt-fn addresses so both sides embed the same imm64; Lrec-strip on the NEW side, raw on the OLD, payload `cmp` across the FULL branch matrix — succ ×4 (s0/s1 present/NULL) + plus ×8 (s0/s1/s2). **ALL 12 SHAPES BYTE-IDENTICAL.** Link recipe: `/tmp/si_objs/emit_str.o` (bytes/u32le/u64le live there) + a 4-line stub TU (`sm_emit_t g_emit; bb_medium_t g_medium;` + `rt_bomb` no-op), `g_medium = BB_MEDIUM_BINARY` in main. HONESTY NOTE: the harness's first pass printed 12 FAILs — a harness artifact (the OLD side is unframed raw bytes but both sides were fed through the Lrec-deframer); the NEW payloads in those hexdumps were already instruction-for-instruction correct; comparison fixed (raw-OLD vs deframed-NEW), rerun, 12/12 PASS.

Behavior + asm: asm-diff EMPTY ×1 normalized on `succ(3,X)+plus(2,3,Z)` with BOTH TEXT arms LIVE (`rt_succ@PLT` + `rt_plus@PLT` in .s); behavior A/B identical ×3 modes (4/5, rc=0 — note m3 prints 4/5 on this box, NOT interp-silent). medium-invisible gate: **bb_succ_plus DELISTED** (REMAINING now conj/io/is_cmp/list/resolve/retract_throw/term_inspect/term_io/type_test). [S] eb=8 nw=12 stands untouched — admission/operand fusion → LOWER `_.op_*`/ζ-slot plumbing, FIX-3-adjacent, design unpinned.

⛔ **STOP-ORDER ERRATUM (self-caught, recorded):** stops ran subject→succeed→succ_plus per the 16th-run watermark's arrival notes, but tracker DOCUMENT ORDER is subject→**succ_plus**→succeed (`'_'` 0x5F < `'e'` 0x65). One-position swap; both files closed; nothing skipped; cursor lands correctly past all three. Lesson: the tracker list is the ring — arrival notes are notes.

## GATES (floors held at every commit)

smoke m4 7/7 HARD · pat M4=18 FAIL=0 SKIP=1 (053 pre-existing) · icon m2 12/12 HARD, m3=m4 10/12 (proc_zeroarg/proc_recursion pre-existing) · purity 2-floor (bb_call_write_slot, bb_every — FIX-3 family) · bin_t 0 · vstack 3 · sno_pat_reg TIER1+TIER2 HARD · prove_lower 68 PASS + 3 inherited FAIL (law-5 trio: PL-GZ-7 ITE pair 10≠8/9≠7 + PL-GZ-8 arith-is 2≠5) · handencoded 0 · medium-invisible trend (succ_plus delisted).

## CLOSE STATE

Rank 878→841 (−9 subject, −3 succeed, −25 succ_plus); 34 dirty/72 clean → **32 dirty/74 clean**. Emit-blind steady 235 (the succ_plus eb/nw [S] untouched — honest). `# CURSOR: bb_term_inspect.cpp`.

## NEXT SESSION

Arrival notes for `bb_term_inspect.cpp`: the rb-HEAVIEST remaining — rb=50 (incl. `emit_term_from_node_bin` node-ptr movabs, which stays [S]-parked pending LOWER term plumbing — convert AROUND it via `x86_lit_bytes` bridges per the bb_aggregate_nb/bb_atom_string pattern, leaving the honest substring-artifact rb markers), eb=12 nw=22 [S]. The conversion recipe is **four-times proven** (aggregate_nb → atom_string → findall → succ_plus) and the 12-shape harness transplants directly — its 8 TEXT arms were probe-LIVE in the 6th-run TIER H pass, reuse those probe shapes. Behind it: bb_term_io rb=43 (incl. the 6th-run RESET-TO-A redo under the corrected rule), then bb_to/bb_type_test/bb_unify/bb_unop/bb_var* close the lap. **THE FORK stands on Lon's word:** cursor into the rb-heavies vs jump to FIX-4 (gvar 3c capture pin + execute) / FIX-3 family (bb_return op_sa-relocation is the landed model; bb_call + bb_call_write_slot are law-4 HOT until ~02:50 UTC 06-08 anyway, which argues for term_inspect first if the next run opens before then).

## OUTSTANDING VERDICTS (6, unchanged)

x86_movimm uint32-truncation (bb_call_fn) · RING/DIRECTORY RECONCILE (106 vs tracker) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (owner PL-GZ) · m2 disj-backtrack silent-empty (owner PROLOG-BB) · IRD-2b IR_t.own DEVIATION ratification.

No LADDER rungs closed this run (FIX-1 is the standing lap rung; nothing deleted per handoff rule 1).
