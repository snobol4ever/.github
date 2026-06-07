# HANDOFF — 2026-06-07 — BB-FIXUP 16th attended run (Opus 4.8) — LAP 2: SCAN FAMILY COMPLETE

**Run:** 16th attended, Opus 4.8, Lon attending (context checks at ~25%/~50%/~75%, extension word at ~73%, handoff word ~83%).
**Goal:** GOAL-BB-FIXUP.md · **Queue:** SCRIP/BB-REVAMP-TRACKER.md · **SCRIP @ 451bfd0** (verified local==origin) · **.github @ this commit.**

---

## HEADLINE

Seven stops, seven ✅ v2 — **the scan family is now FULLY v2**: any/bal/find (15th run) + many/match/move/pos/stmt/tab/upto (this run). Close rank **930→878** (open 41 dirty/65 clean → close 34/72; fixup −52). Emit-blind steady 235. One new ring-wide asm-diff practice finding (intern-order / FOR-ladder). Two new law-5 flags (Icon scan-fail control flow). One concurrent absorbed with re-certification. Gates at floors every commit. No LADDER rungs closed (FIX-1 is the standing lap rung).

## SESSION OPEN

Baseline matched the 15th-run close watermark exactly: rank 930, 41/65, emit-blind 235, all gates at floors (smoke m4 7/7 HARD · pat M4=18, 053 pre-existing SKIP · icon m2 12/12 HARD, m3=m4 10/12 pre-existing · purity 2-floor · bin_t 0 · vstack 3 · sno_pat_reg HARD · prove 68 PASS + 3 inherited FAIL, the law-5 trio). prove counting note: grep `'; PASS'` / `'; FAIL'` — bare `FAIL` over-matches the PFAIL sentinel node names in the dump output.

## THE STOPS

**1. bb_scan_many 06b27d1 ✅ v2 6→0.** pe 4→0 (PORT_*→Greek glyphs, `\xCE\xB2/\xCE\xB3/\xCF\x89` re-verified at head), lv 2→0 (off/cs → `_.op_off`/`_.op_name1` inline ×3 sites), merged guard same short-circuit, bomb-in-_str all paths, wrapper one-liner. strchr_ptr() kept (sanctioned-exception shape — C++ overload resolution). L(0)/L(1) loop + push-rax/r10 cursor save verbatim. Proof: asm-diff EMPTY ×2 (bbN/RESOLVE/.LcallN normalized), MANY LIVE both .s, behavior A/B identical ×6 (m2/m3/m4-run: `many('a')` on "aaabc"→4; `many('xy')` on "xxxyz"→5).

**2. bb_scan_match 473b966 ✅ v2 8→0.** pe 5→0, lv 3→0 — `len` → `(long)strlen(_.op_name1)` inline ×3 sites (strlen pure, multi-eval identical, bb_scan_find precedent); memcmp_ptr() kept; split comment string kept verbatim. Proof: EMPTY ×2, MATCH LIVE both, identical ×6 (`match("he")` on "hello"→3; `match("abcd")` on "abcdef"→5).

**3. bb_scan_move cbbd665 ✅ v2 7→0.** pe 5→0, lv 2→0 (off ×4 / n / sa → `_.op_off/_.op_sb/_.op_sa`); double push/pop r10 align + β-REVERSES δ-restore verbatim. Proof: EMPTY ×2, MOVE LIVE, identical ×6 (`move(2)`→he ×3 modes). **⛔ LAW-5 FLAG (a), pre-existing identical A/B, NOT swept, owner ICON-BB/Lon:** `if "abc" ? move(9) then write("yes") else write("no")` prints "no" m2 but NOTHING m3/m4 rc=0 — scan-fail does not drive the else branch natively; same family smell as the icon m3/m4 pre-existing FAILs.

**4. bb_scan_pos 0593fd4 ✅ v2 6→0.** pe 4→0, lv 2→0; the `n>=1` value test preserved verbatim inside the merged guard. Probes: `pos(1)` + `pos(4)`-fail (empty ×3 consistent — fail path probe, distinct n in emitted asm). Proof: EMPTY ×2, POS LIVE both, identical ×6. **⛔ LAW-5 FLAG (b), pre-existing identical A/B, NOT swept, owner ICON-BB/Lon:** `write("abc" ? pos(1))` prints NOTHING m2 but 1 m3/m4 — **INVERSE direction** of the usual divergences; the m2 oracle looks wrong here (real Icon pos(1) at scan start succeeds returning 1).

**5. bb_scan_stmt 391068f ✅ v2 12→0 — the heavy stop (the SNOBOL IR_SCAN statement box).** pe 8→0; lv 4→0 — the a_subj/a_slit/a_patlit/a_rlit conditional locals → **FOR(0,5) sequenced arg ladder** with IF(i==N) per-operand arms (bb_gvar_assign FOR-lambda + bb_scan_find i==N precedents); statement-level `if (MEDIUM_TEXT)` branch → **ONE return of mutually-exclusive IF arms** (bb_gen_scan idiom); the 3 TEXT admission bombs → cascading first-match IF arms, TEXT-scoped verbatim (BINARY with non-literal pattern remains admitted — graph pointers); **BINARY rt_scan arm chain VERBATIM** (its own eval order untouched — only changed structure needs the ladder); wrapper untouched INCLUDING its no-x86_begin shape (law 1 — preserved, not "fixed"). Proof: EMPTY ×2 SNOBOL probes, rt_scan_lit LIVE both .s, identical ×6 (`S "b" = "X"` → aXc — name-subj + repl shape; lit-subj no-name no-repl → yes). smoke 7/7 + pat M4=18 are themselves live-fire on this box. Both sides of all three IF-pairs exercised across the two probes.

**6. bb_scan_tab 32a0db0 ✅ v2 8→0.** pe 5→0, lv 3→0 — the `tgt` selector local → IF(sb>=1)/IF(sb<1) complementary pair: **PURE-formatter inline** (zero intern sites in file → splice-order free per the 15th-run bb_scan_find proof — no FOR ladder needed); `(n>=1||sa>=0)` value test verbatim in merged guard. Proof: EMPTY ×2, TAB LIVE with **BOTH tgt arms fired** — `tab(3)` literal-n + `tab(upto('l'))` sibling-slot (`mov rax,[r12+48]` in .s) — identical ×6 (he ×6).

**7. bb_scan_upto 451bfd0 ✅ v2 3→0 (EXTENSION stop, Lon's word at ~73%).** pe 3→0, lv 2→0 (off / cur=off+16 ×4 / cs inline); zero intern sites (sole trailing ro_seal — splice-free); the FIRST SCAN GENERATOR **β-RE-PUMP cursor loop verbatim**. Proof: EMPTY ×2, UPTO LIVE both, identical ×6 (`upto('l')`→3 ×3 modes; `every write("hello" ? upto('lo'))` prints 3 only — **CONSISTENT m2==m3==m4** on this head: generator suspension yields first result only; NO divergence, A-state preserved and recorded — not a law-5 flag because all three modes agree).

## ⛔ ASM-DIFF PRACTICE FINDING (ring-wide; tracker note at bb_scan_stmt)

Dissolving locals whose initializers carry **INTERN side-effects** (scan_lbl/emit_intern_str/strtab) into a `+` chain **REORDERS the interns** — gcc evaluates operator+ chain terms **right-to-left**, so `.S` label NUMBERING permutes while instruction order stays correct (the instruction stream rides the concatenated STRING, which is structural and eval-order-immune; only side-effect counters follow eval order). **The tell:** asm-diff shows lea-label swaps only (e.g. `.S2↔.S3`). Caught LIVE at bb_scan_stmt first attempt; fixed same-stop. **The fix:** FOR(0,N) ladder, ≤1 intern per iteration, iteration order = original decl order. **Pure-formatter locals** (L(), mov-imm/FRQ selectors) remain splice-free per the 15th-run proof. Corollary recorded: verbatim-copied chains keep their own (original) eval order — only restructured expressions need the ladder.

## CONCURRENTS

×1 merged green: **IRD-3-CHAIN-1 d20c45e** (19:42:01 UTC) raced the bb_scan_move push — emit-time RPN chain writers → operands[], touched emit_core op-priming + drivers, **ZERO BB_templates files** (no law-4 windows created in the ring). Full battery re-certified on the rebased head per 8th-run precedent + this-run probe spot-check (many/match/move outputs unchanged) before continuing.

## GATES (floors held at every commit)

smoke m4 7/7 HARD · pat M4=18 FAIL=0 SKIP=1 (053 pre-existing) · icon m2 12/12 HARD, m3=m4 10/12 (proc_zeroarg/proc_recursion pre-existing) · purity 2-floor (bb_call_write_slot, bb_every — FIX-3 family) · bin_t 0 · vstack 3 · sno_pat_reg TIER1+TIER2 HARD · prove 68 PASS + 3 inherited FAIL (law-5 trio: PL-GZ-7 ITE pair 10≠8/9≠7 + PL-GZ-8 arith-is 2≠5).

## PROBE-SHAPE RECIPES (for the next session)

Icon scan probes: `write("hello" ? builtin(args))` one-liners fire the boxes mode-4; `every write(...)` for generator re-pump arms; m4-run link: `gcc -no-pie X.s -L out -lscrip_rt -Wl,-rpath,$PWD/out`. SNOBOL IR_SCAN: `S "pat" = "repl"` (name+repl shape) and bare `"lit" "pat" :S(L)` (lit-subj shape). asm-diff normalizer (5th/11th/15th-run practice, all three): `s/bb[0-9]+/bbN/g; s/RESOLVE\(name\/-?[0-9]+\)/RESOLVE(N)/g; s/\.Lcall[0-9]+/.LcallN/g`.

## CURSOR + NEXT SESSION

`# CURSOR: bb_subject.cpp` (cold first-audit; ef=1 pe=6 lv=2 per open rank — cheap). Behind it: bb_succeed (pe=3, cheap) → **bb_succ_plus rb=25** (the thrice-proven movabs/mov32/stk32/call-ro conversion recipe applies — plan as the next run's first substantial stop) → bb_term_inspect(84)/bb_term_io(115) rb-heavies. **Priority alternative on Lon's word** (standing 15th-run order, scan tail now done): jump the cursor to **FIX-4** (gvar 3c capture pin + execute) → **FIX-3 family** with per-member design calls (bb_return op_sa-relocation is the landed model) → **bb_resolve** dedicated TIER S session.

## OUTSTANDING LON VERDICTS (6 + 2 new law-5 observations)

1. x86_movimm uint32-truncation (bb_call_fn, 8th-run flag)
2. RING/DIRECTORY RECONCILE (106 dir vs tracker count)
3. prove rc=0-on-FAIL hardening
4. PL-GZ-8 arith-is 2-vs-5 (owner PL-GZ)
5. m2 disj-backtrack silent-empty (owner PROLOG-BB)
6. IRD-2b IR_t.own DEVIATION ratification
7. NEW law-5 (a): Icon scan-fail else-branch silent m3/m4 (owner ICON-BB)
8. NEW law-5 (b): pos(1) m2-silent INVERSE divergence — m2 oracle suspect (owner ICON-BB)

## HANDOFF RULE 1

No LADDER rungs closed this run; nothing deleted from the goal file (FIX-1 is the standing round-robin rung and stays open).
