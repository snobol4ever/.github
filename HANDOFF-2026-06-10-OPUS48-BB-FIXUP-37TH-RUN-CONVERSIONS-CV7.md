# HANDOFF 2026-06-10 — BB-FIXUP 37th attended run (Opus 4.8, Lon attending) — closed ~96% law 7

## STATE AT CLOSE
- SCRIP @ 544e329 · .github @ be86e07b (this commit follows) — both local==origin at every push.
- CURSOR: bb_assign_frame.cpp (tracker line semantics unchanged).
- CEILING (pending Lon ratify): 115 files / 108 dirty / 7 clean / GRAND 2496.
- Gates at floors on EVERY commit: smoke m4 7/7 HARD · icon m2 12/12 HARD (m3=m4 10/12 pre-existing) · prolog m2 5/5 HARD m3=m4 5/5 · pat M4 19/0 (053 M2/M3 pre-existing) · prove_lower 68P+3F rc=0 (law-5 trio) · purity 2 · bin_t 0 · vstack 3 · sno_pat_reg HARD · med_inv 103.

## LON RULINGS THIS RUN (all recorded in GOAL-BB-FIXUP.md + tracker)
1. C++ template DUPLICATION SANCTIONED — no anti-duplication requirement; code reduction at the VERY END when everything works.
2. 120-char max/separator ERADICATED from HQ MDs for C/C++ — max is 200 (RULES.md:58-59 was already correct; fixed GOAL-BB-FIXUP R4+xc def + 3 HANDOFFs, 37207628). Snocone-scoped GOAL-PARSER-* 120s out of scope. Both swept files now carry 200-total separators.
3. R6/CV6 — NO LOCALS in top-level template functions (a local = decl inside the function body, e.g. the old `int n` in bb_alt_str). Delivery via zero-emit value-computer helpers (may have locals), _.op_*/_.bb_* slots, or lambda params.
4. NOMENCLATURE: the conversion list = the **CONVERSIONS** (CV1..CVn; R1-R6 = CV1-CV6 aliases) — "RULES" was ambiguous vs RULES.md/FACT-RULES. A CONVERSION = TARGET → CHANGE-TO spec.
5. CV7 — VALID MNEMONICS ONLY: every x86("XXX") must be a valid x86/x64 instruction.

## LANDED (chronological)
- bb_alt v3 ddd60fe: 29→10 (mt1→0 bp5→0 hc1→0 rp15→7; R1 IR_ALT). NEW x86("ro_seal_q") dispatch (lossless 64-bit operand round-trip + live-diff verified). Corpus-silent box → 2 LIVE probes CREATED: /tmp shapes `every write(1|2|3)` + `every write("aa"|"bb")` (Icon). Asm instruction-stream IDENTICAL bbN-normalized, sole delta = R1 comment; m2=m3=m4 parity.
- bb_arith v3 6ce62e9: 6→0 CLEAN rc=0. ⛔ PROBE-HUNT FINDING: box is LOWER-UNREACHABLE (stronger than 36th's corpus-silent) — all 5 g_arith_expr sites operand-push only; bb_resolve/bterm_arith consumes IR_ARITH operands inline; nothing chains IR_ARITH into the walked flat chain. C2 = string-identity-by-construction (35th-run bivar precedent). Already EMIT-BLIND (bb_prepare delivers _.bb_*). No [S].
- bb_alt R6 redo 60a22b5: int n/arms HOISTED → bb_alt_n (admission+count) + bb_alt_arm (accessor) zero-emit value-computers; _str = ONE lazy-IF return, ZERO locals; bomb-in-_str (15th-run gen_scan precedent); wrapper 2 lines zero locals single-eval. Asm re-proven IDENTICAL ×2.
- CV7 544e329: "ro_load_q" mnemonic REMOVED from dispatch (it is NOT an instruction — it was `mov r64, qword ptr [rip+slot]`); added ROQ(n) operand helper + XK_ROSLOT parse + mov dispatch arm → same internal encoder; 4 sites converted (bb_alt ×1, bb_det_is ×2, bb_det_write ×1) to x86("mov", reg, ROQ(n)). Asm identical; GRAND unchanged.
- HQ: R6 + CONVERSIONS nomenclature + CV7 spec in GOAL-BB-FIXUP.md; 120-eradication ×5 sites; tracker 37th-run header + 2 addenda + ticks.
- THREE BB-neutral concurrents absorbed w/ re-certification each (db97f49 + 8ddfd2a pascal-nl, 0ecd99c raku-nl UNPARK).

## OUTSTANDING LON VERDICTS (standing 6 + NEW 5)
Standing: x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (PL-GZ) · m2 disj-backtrack silent-empty (PROLOG-BB) · IRD-2b IR_t.own DEVIATION ratify · ml comment-substring false-positive.
NEW this run:
1. nw audit-regex widen — subscript form `arms[i]->op` NOT matched (alias form only): bb_alt's neighbor inquiry PERSISTS though nw reads 0 (counter masking, honest-noted in tick).
2. lv counter re-scope to top-level (R6/CV6 pairs) OR ratify ceiling re-baseline 2495→2496 (R6 compliance moved locals into helpers; file-wide ruler +1).
3. bb_arith dead-dispatch retirement (LOWER-unreachable) — keep or delete `case IR_ARITH` + template.
4. ro_seal_q / ro_seal_str under CV7 — they emit DATA (label + .quad/.string), not instructions; directive-name mapping (e.g. x86(".quad",slot,val)) or a sanctioned seal-form? 14 more files also call x86_ro_load_q as a FREE FUNCTION (bypass class — their own cursor stops convert to mov+ROQ).
5. smoke_compile harness make-target MISSING (out/sm_codegen_x64_emit_test — pre-existing Makefile gap; gate unrunnable as written).

## [S] STANDING ON bb_alt
arms[i]->op/ival/sval operand-aux neighbor inquiry + admission loop → needs IR_ALT_LITERAL LOWER split delivering per-arm (type,value) via operands/ζ-slots; design NOT pinned; cross-subsystem — do NOT cowboy.

## NEXT SESSION (Session open protocol → THE LOOP)
1. Clone both repos; build (install_system_packages.sh, build_scrip.sh, make libscrip_rt); read GOAL-BB-FIXUP.md CONVERSIONS CV1-CV7 + tracker header.
2. Cursor stop: bb_assign_frame.cpp (✅ v2 7th run — re-audit under CV6 no-locals + CV7 valid-mnemonics + 200 separators; expect small).
3. Apply ALL CONVERSIONS per stop, ONE C1-C5 battery, one-file commit, rebase, push, tick+cursor SAME commit, re-certify after any concurrent rebase.
4. C2 normalizers: bbN (`bb[0-9]+_`→`bbN_`) + R1-comment strip (+ RESOLVE/.LcallN where firing); LIVE probe when corpus silent; string-identity-by-construction ONLY when LOWER-unreachable (prove unreachability from lowering source, bb_arith precedent).
5. Shell note: bash_tool sh is NOT bash — no process substitution; use temp files for diffs; python3 for tracker edits (Greek glyphs break sed/grep -c1 UTF-8).
