# FINDING — ZD-5 MATCH-SPINE: the quartet ARMS, the claim moves to the HEAD, and the default flips ON

**Session:** s23h (2026-08-02) · **Directive (Lon):** complete the NON-POPPING FORTH-style RSP zeta stack for match statements — *"a var just needs a little space"*, the subject read must not pop — then *"All your choices. I'm with you on this. Continue."*

**VERDICT:** `SCRIP_ZD_MATCH` default is now **ON**. Full crosscheck-318 identical **BY SET** to the declined regime in both modes — m3 280/27/10 · m4 266/39/10/2C, the s23g record exactly — pattern-family 131 identical by set, zero P→F flips in any arm. `SCRIP_ZD_MATCH=0` restores the declined regime byte-identically (proven on roman.s after every single edit of the session).

## THE SHAPE (what a match statement emits now)

`n3_var_α: sub rsp,16` (the var carves ONLY its cell — the complaint verbatim) · `n4_match_head_α: sub rsp,240` (CLAIM-AT-HEAD: the match owns its scanner storage; hook-carved at the head's α, once per statement execution, zeroed per the s23a contract) · quartet SEQUENCE/RELEASE/REPLACE noalloc · replacement producer carves its own 16 · terminal cuts release cells+claim together. Subject read is **non-popping**: `mov rdi/rsi, [rsp# + op_uclaim + op_zread[0]]` — the claim below plus the staged delta to the subject's cell among the above-claim producers.

## MEASURED LAWS (each one a bracketed witness, chronological)

1. **REPLACE operand seats:** `op_sa` is the SUBJECT (`# sub_lo/sub_hi` in the OFF listing); the replacement travels BY ADDRESS through `replp`/r9. The first armed arm inverted this — roman printed only the last recursion level. Armed r9 is now `lea` of rv's cell; rsi/rdx read the op_sa slot regime-blind (the head mirrors there).
2. **The pin is a pure coordinate rebase** — its own doc said so ("NOT depth compensation"); hybrid douts broke the K−K≡0 identity it leaned on. `zvo_resolve_base` + `zvo_owner_dout` restore it by construction. This one fix recovered 46/50 broken pattern programs.
3. **Blob members resolve DECLINED-IDENTICAL (dout delta zero).** 174_pat_bal: bal's counter spellings coincide with claim-relative resolution only at delta 0; +16 wrote the neighboring assign_save cell — corrupted paren counter, BAL accepted `'-2)'`.
4. **Raw claim spellings are shift-fragile BY DESIGN** (the ON-5/ARGREAD escapes: `rspd`, `x86_zref`, the cap-slot `lea rdi,[rsp+176]`). gdb bracket on 156: wild `rt_cap_push` slot pointer + garbage delta under a −16 world. Consequence: **rsp at head-α must equal the claim base** — which CLAIM-AT-HEAD delivers at zero instruction cost (pre-head cells ride ABOVE the claim). The intermediate HEAD-FOLD (planner-staged pop) was correct but strictly dominated; superseded same-session.
5. **The mirror is gated `!subjc()`**: on subject-cell-granted graphs OFF popped and never wrote op_sa — the slot belongs to another node's layout (054: the mirror's two stores were the ONLY functional diff and flipped it red).
6. **The subject is not always adjacent**: POS(N)/LEN(n) variable operands put coerce chains on the spine between subject and head. 061_capture_in_arbno read the coerce cell as the subject descr under a hardcoded `+0` and failed every match. `op_uclaim + op_zread[0]` is the general spelling; the zread=0 class is byte-unchanged.
7. **Dynamic-box decline mirrors s22y**: graphs bearing DEFER/PATREF/FENCE1 keep the declined regime (degrade never die). PATREF measured both ways: 117/142 arm GREEN — **the named next rung** — but 135/136_pat_balanced_parens crash armed (recursive stored patterns re-enter the blob at unmodeled depths).
8. **Exit pops are position-gated**: pre-head exits (subject-eval failure) free cells alone; the claim rides pops only from hpos onward.
9. **Span shrink**: armed value members' zls extents are dead (values live in cells) and no longer inflate the claim — EXCEPT the !subjc subject producer's (its slot is the live op_sa dataflow).

## FLAKE LEDGER (grew this session, all with identical-bytes proof)

{135, 136, 164, 165, 183} + prior {test_string, 213}: baseline-crash citizens whose P/T/F flickers with ASLR / stdout-flush timing. Proof of class: the SAME OFF binary at the SAME path scored P in one sweep and rc=139 the next; 165's armed .s is byte-identical to OFF yet both die rc=139 *after* flushing correct output. **Sweep law: compare BY SET and re-roll singleton flips before believing them.**

## HONEST RESIDUE

- roman.sno is **baseline-red at HEAD** (both modes, both regimes print empty) — it was never a valid bring-up vehicle; the minimal probe (`/tmp/strip.sno`, recursive RPOS/LEN strip + replace) is green all four arms and is the demonstration artifact.
- 061_capture_in_arbno remains red→red (OFF and armed both loop infinitely — a scrip baseline defect in POS(N) overrun, out of scope).
- PATREF class (roman among them) stays declined; the 117/142 green is the measured entry point for arming it.

**Artifacts:** regen ×4 auto-committed (corpus `e814a248`/`126b3c7f` + SCRIP feature commit) with the armed default — every checked-in `.s` asserts the compiler at HEAD, per the s23g artifact-truth law.
