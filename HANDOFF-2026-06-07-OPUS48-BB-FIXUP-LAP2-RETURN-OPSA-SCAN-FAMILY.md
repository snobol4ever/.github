# HANDOFF — 2026-06-07 — Opus 4.8 — BB-FIXUP 15th attended run
## LAP 2: bb_return (FIX-3 first member, op_sa relocation) + bb_scan_any/bal/find

**Repos at close:** SCRIP @ `98ef8a5` (verified local==origin) · .github @ this commit.
**Cursor at close:** `# CURSOR: bb_scan_many.cpp` (cold, no prior annotation — first audit).
**Close rank:** 956 → 930 · 106 files · 41 dirty / 65 clean · emit-blind steady 235.
**Run shape:** Lon attending; opened on "Continue" after orientation; extended past the law-7 line on Lon's word once (the clean-close-then-Continue pattern, 11th/13th-run precedent); ended ~78%, all stops fully closed. No LADDER rungs closed (nothing deleted per handoff rule 1 — FIX-3 stays open: one family member landed, four remain).

---

## STOP 1 — bb_return.cpp ✅ v2 6→0 — THE FIX-3 FIRST FAMILY MEMBER (commit `547566e`)

**TIER H:** ef 1→0 (comment emit_fmt → std::to_string concat) · pe 2→0 (PORT_OMEGA ×2 → literal `ω`; `\xCF\x89` re-verified at this head in x86_asm.h:23) · lv 3→0 (`src`→`_.op_sa`; `head` dissolved into ONE lazy-IF return; wrapper `s` eliminated, bomb moved inside `_str` per the bb_gen_scan idiom incl. the !PLATFORM_X86 path).

**THE DESIGN CALL (stated in-run per the 14th-run correction; executed under the 13th-run rescope; reversible on Lon's word):** the template-side neighbor inquiry `_.node->α` → `bb_slot_get(...)` was RELOCATED to the SOLE dispatch site — `emit_core.c` case IR_RETURN — following the emit_bb.c line-1116 `g_emit.op_sa = bb_slot_get(pBB->α)` driver precedent. Delivery via `_.op_sa`. The dispatch computes a **dual-read**: `operands[0]` preferred, `α` fallback — matching IRD-3b-2's (`fbfd71c`) convention, which landed MID-SESSION and made `icn_return` push the value to `operands[0]` (RETURN kind-complete across all 3 lowering producers). The chain-α → operands[] migration itself was NOT swept (law 5): IRD-3b-2 explicitly scopes chain-ecosystem α residue to its own bulk stage; the dual-read keeps this dispatch correct through that migration unchanged. `bb_slot_get(NULL)` returns −1 ≡ the old `src = -1` sentinel, so the bare-return case reproduces the old expression exactly. **The template now dereferences ZERO IR nodes.**

**FIRING PATH PINNED EMPIRICALLY (recorded so no session re-hunts):** bb_return fires from the **icn_proc descr-chain builders** (`descr_flat_chain_build_proc[_text]`, prefix `icn_proc_%s`, 16-byte reserved result area = the `[r12+0/8]` the template stores). The SNOBOL DEFINE path does **NOT** fire it on this head — a `DEFINE('F(X)')` … `:(RETURN)` probe compiles and runs (42) with zero `BOX IR_RETURN` in the .s; SNOBOL returns route through other machinery. The program-level RET/FRET nodes (lower_program.c:504–505) are valueless dval-1.0/2.0 landings consumed by `flat_drive_return`/the gvar arm, not this template.

**PROOF SET:** asm-diff EMPTY ×3 probes, bbN/.LcallN/RESOLVE-normalized, with ALL arms LIVE in m4 .s:
- `p1` value return (`procedure answer() return 42; end`) — value arm, slot 16 LIVE
- `p2` recursion (`fact(5)`) — 2 RETURN boxes
- `p3` bare return (`return;`) — null arm LIVE, slot −1 → DT_SNUL zeros

Behavior A/B identical ×3 probes: m2 = 42/120/ok · m4-run = empty/empty/ok (the p1/p2 m4 empties ARE the pre-existing proc_zeroarg/proc_recursion smoke FAILs, byte-identical both sides) · m3 = identical SMX EXCISED message (procs driver-excised mode-3; TEXT-arm + x86() both-media construction is the m3 proof surface).

**ONE-COMMIT NOTE:** template + dispatch + tracker landed in one commit (FIX-5 `529df0d` precedent — splitting would leave op_sa unset under a reading template, an intermediate non-neutral state).

## STOP 2 — bb_scan_any.cpp ✅ v2 7→0 (commit `5c5ea17`)
pe 5→0 (ω×3/γ/β glyphs) · lv 2→0 (`off`/`cs` → `_.op_off`/`_.op_name1` ×5 sites) · bomb inside `_str` on the compound guard (same condition set, single eval). **`strchr_ptr()` static helper KEPT** — it exists for C++ overload resolution on `strchr` (direct cast is ambiguous between the two `<cstring>` overloads); recorded as the sanctioned helper shape so later laps don't "fix" it. asm-diff EMPTY; SCAN_ANY LIVE m4; behavior 2/2/2 identical × m2/m3/m4 on `"hello" ? write(any('h'))` — **m3 LIVE on the scan family** (unlike procs).

## STOP 3 — bb_scan_bal.cpp ✅ v2 6→0 (commit `95a7d4f`)
pe 4→0 · lv 2→0 (`off/cur/cnt/cs` → `_.op_off`/`+16`/`+24`/`_.op_name1` ×14 sites) · merged guard preserves short-circuit order, null-safe. **Host-side `strchr` bracket-admission KEPT in the guard** — that is operand-STRING admission via op_name1 (driver-delivered), not neighbor inquiry; stated so the emit-blind reading is unambiguous. asm-diff EMPTY; BAL LIVE m4; behavior 5/5/5 × m2/m3/m4 on `"a(b)c" ? write(bal('c'))`.

## STOP 4 (extension) — bb_scan_find.cpp ✅ v2 7→0 (commit `98ef8a5`)
pe 3→0 · lv 4→0 — the `cmps` unrolled-compare accumulator → **FOR() lambda** (bb_gvar_assign precedent) with i==0/i!=0 IF-arms and `(long)(unsigned char)` casts verbatim; `m` → strlen-inline both sites. **SPLICE-ORDER PROVEN FREE before moving it:** the old code evaluated the loop's x86() calls before the header's; checked the bb_gvar_assign strtab-order caution and found it inapplicable here — `L()` is a pure rotating-buffer formatter (x86_asm.h:218) and this template has ZERO strtab/seal sites, so x86() invocation order carries no side effects; only the final string matters and it is position-identical. asm-diff EMPTY; FIND LIVE m4 with the 2-char needle `find("ca")` exercising BOTH lambda arms; behavior 3/3/3 × m2/m3/m4.

---

## CONCURRENTS — FIVE landed this run, battery re-certified on every rebased head (8th-run precedent), floors held each time
1. `fbfd71c` IRD-3b-2 (at open) — ICON control cluster; **swept the RETURN kind** (icn_return → operands[0]); directly informed stop 1's dual-read.
2. `c6b09f5` IRD-3c (at open) — PROLOG UNIFY/ARITH operands.
3. `2f17bf4` SNO-ISO-1 (raced the bb_return push) — SNOBOL value-lower isolation.
4. `5a40338` IRD-3e-1 (same race) — IF/WHILE cond → operands[0]; same dual-read convention as stop 1.
5. `b2cfd08` IRD-3e-2 (raced the bb_scan_bal push) — DISJ child-alpha deleted.
None touched ring files or the IR_RETURN dispatch. bb_return.cpp itself was COLD (last touch 06-04) — law 4 is about the FILE, applied correctly.

## PRACTICE ADDENDA (apply forward)
- **`.Lcall<int>_pname` normalizer:** these labels are pointer-derived nondeterministic run-to-run (same-binary 2-run proof: 79984 ≠ 60784). Normalize `\.Lcall[0-9]+` alongside `bb[0-9]+` and `RESOLVE\(name\/-?[0-9]+\)` in every asm-diff. (5th/11th-run practice extended.)
- **Cursor erratum, self-caught + corrected in-run (`562c5f5`):** a stray earlier sed set the cursor to `bb_scan_break.cpp` (not a ring entry) inside the bb_scan_bal commit; corrected next commit. LESSON: print/verify the `# CURSOR` line POST-sed, PRE-commit — applied on both later stops.
- **Goal-file watermark editing:** twice this run a watermark append was initially written as a replace (clobbering the prior run's closing lines); both caught and restored before commit. Mechanical lesson: append-after, never replace-tail.

## GATES AT FLOORS, EVERY COMMIT
smoke m4 7/7 HARD · pat M4=18 (053 pre-existing SKIP) · icon m2 12/12 HARD, m3=m4 10/12 (proc_zeroarg/proc_recursion pre-existing) · purity 2-floor (bb_call_write_slot, bb_every) · bin_t 0 · vstack 3 · sno_pat_reg HARD · prove_lower 68 PASS + 3 inherited FAIL (the law-5 trio: PL-GZ-7 ITE pair 10≠8/9≠7 + PL-GZ-8 arith-is 2≠5).

## OUTSTANDING LON VERDICTS (6, unchanged)
1. x86_movimm uint32-truncation (bb_call_fn, 8th-run flag)
2. RING/DIRECTORY RECONCILE (106 dir vs tracker count)
3. prove_lower rc=0-on-FAIL hardening
4. PL-GZ-8 arith-is 2-vs-5 node count (owner PL-GZ)
5. m2 disj-backtrack silent-empty (owner PROLOG-BB)
6. IRD-2b IR_t.own backpointer DEVIATION ratification

## NEXT SESSION
THE LOOP at `bb_scan_many.cpp` (cold, first audit), then the scan tail — match/move/pos/stmt/tab (stmt pe=8 lv=4, tab pe=5 lv=3 per the open rank table; the any/bal/find recipe covers them). After the scan tail, per the 13th-run priority order: **FIX-4** (gvar 3c capture split) then the **FIX-3 family proper** — bb_return's landed op_sa-delivery is the family's smallest precedent, but bb_call (TOTAL=157) / bb_call_proc_staged / bb_call_write_slot / bb_every carry two-level classification + emit-pair scans and still expect per-member design calls STATED IN-RUN for live veto. Then bb_resolve term plumbing as its own dedicated session. rb-heavies still queued: bb_term_io(43, incl. the 6th-run RESET redo) · bb_term_inspect(50) · bb_list(32) · bb_succ_plus(25) — recipe thrice-proven.
