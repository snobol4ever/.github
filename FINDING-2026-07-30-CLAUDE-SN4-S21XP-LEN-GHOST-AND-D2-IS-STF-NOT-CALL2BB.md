# FINDING s21x-p (2026-07-30, Claude) — THE LEN GHOST CELL, AND D2 IS AN STF DEFECT, NOT A CALL2BB DEFECT

SCRIP commits: `4c375fe2` (GLUE-4) · `a42ac31f` (ZREL-1) · `42e81405` (LEN-GHOST) · `2aec9a4b` (js/jns) + `.s` regen ×3.
Watermark: m3 251/65 → 264/52 · m4 248/32/36 → 264/50/2 · killswitch EXACT (312/4 · 312/2/2 · DIV=2 {140,141}) throughout.

## 1. The roman double-add (Lon's observation) decomposed

`n11_match_len` showed `sub rsp,16` at α but TWO `add rsp,16` on the ω path. Killswitch A/B split them exactly:
the add that SURVIVES `SCRIP_BB_ALLOC=0` is the SAVE/COND pend-record ABANDON-POP (n8_match_assign_save pushes a
16B saved-cursor record; the guarded leaf pops it on failure before unwinding to head β) — correct protocol. The
second add was the glue leave of a cell LEN was GRANTED AND NEVER NEEDED (Lon: "that box needs ZERO bytes").

## 2. The ghost cell's cause: a wiring edge mistaken for a value read

`zw_node_k` already elides dead ≤16B results, and IR_MATCH_LEN was already in `zls_elide_ok` — only a FALSE
liveness blocked it. gdb + a temporary marker printf proved the marker: `zls_mark_value_refs` counted
`IR_MATCH_ASSIGN_COND.operands[0]` as a value read. The lowerer's own construction comment names that operand
"[0] inner entry" — the backtrack-in WIRING edge — while `[1]` = SAVE is the genuine ZB-FC-3c cross-box slot
read. So EVERY capture-guarded inner leaf (`pat . var`, `pat $ var`) was marked live and granted a ghost cell.
FIX (`42e81405`): skip `(COND|IMM, j==0)` only — a blanket kind exclusion would have killed the SAVE liveness
the s4 audit protects. Effect: LEN collapses byte-for-byte to the killswitch shape; m3 +5, m4 +6, 18 programs
un-SKIPped, DIV 3→2; killswitch untouched (elide is the pre-proven mechanism, now fed the truth).

## 3. js/jns: the "gated-only" abort was a default-path compile bomb

Pursuing Lon's proc-demolition directive, the gated compile aborted at `x86_jcc_invert: unknown condition 'js'`.
Adding the pair (encoders 0x88/0x89 pre-existed) moved the DEFAULT watermark: m3 256→264, m4 254→264, SKIP 18→2
— the conditional-ω synth hits `js` on sign checks in ordinary programs; those 16 SKIPs were this abort.

## 4. D2 autopsy: CALL2BB exonerated; the defect is STF-side, one weld from fixed

Minimal probe (oracle output "A"):
```
        DEFINE('F(N)T')                :(F_END)
F       N LEN(1) . T =                 :F(FRETURN)
        F = T                          :(RETURN)
F_END
        OUT = F('AB')
        OUTPUT = OUT
END
```
- Monitor bracket: diverges at step 2 (spl LABEL 4 vs scr "@1 CALL F") — but the stno-tap granularity gap (GE-1)
  cannot distinguish mis-wire from missing tap. Mode-4 label trace settled it, and en route disproved my first
  two hypotheses (args ARE delivered to NV correctly — gdb shows a proper 'AB' DESCR in NV[N] at blob entry —
  and the blob body DOES read formals from NV absolute, no [rbp+k] param cells).
- **`SCRIP_CALL2BB=1` ALONE: probe PASSES, and recursive roman computes `result: MDCCLXXVI` CORRECTLY (713ms).**
  The two-BB constant-folded DEFINE world (laws 6/7) is functionally alive INCLUDING RECURSION.
- **`SCRIP_STMT_FRAME=1` ALONE: probe heap-exhausts** — backtrace `n7_match_release_α → c_rt_dcap_end_ok_open
  (mark=garbage) → rt_dcap_pump → memcpy`. s21x-i's "D2 defect" was therefore MIS-ATTRIBUTED to CALL2BB.
- **ROOT:** `bb_match_head`'s `stfh()` arm carves 48 bracket bytes (s21x-k SUBJ-ARM-2) live at RELEASE.α;
  `bb_match_release` NEVER GOT THE MATCHING ARM — n7's emitted block is byte-identical between regimes, so its
  `[rsp+16/24/32/96/120]` head-cell reads land 48 deep inside the bracket slots (saved regs/pointers → the
  garbage dcap mark; the poisoned `mov rsp,[rsp+32]` wholesale unwind is roman-under-gates' segv, hit-2/3 of the
  staged-breakpoint trace). s21x-k's "STF-EXIT-SEGV cured" was PARTIAL. THE WELD: head-side carve and every
  head-cell reader (RELEASE; audit REPLACE) share ONE predicate (stfh) and ONE layout authority (the
  RBP-HOUSEKEEPING five-field bracket map).
- COHERENCE NOTE: `fc_walk_range`'s fp counts fc/WINDOWED cells only; carve-only cells net out by γ — this is
  CORRECT under the default regime by construction. Do not "fix" it while welding.

## 5. roman-ref correction (voids this session's own early claim)

"roman fails at HEAD both modes" was WRONG: the only diff is the nondeterministic `ms:` line roman.sno itself
prints (source line 19) against a ref deliberately trimmed to the deterministic line. roman is semantically
GREEN at HEAD default. Benchmark comparisons must strip/normalize the timing line; do not hunt roman as a
legacy-class residual.

## 6. The proc-demolition path (Lon: "DELETE that stupidity"), now singular

The vehicle exists and works: CALL2BB two-BB lowering (lower:185) + the DEFINE-stub discriminator (emit:2535,
"NO region, NO fill, NO main-layout floor"). Remaining, in order: (1) the RELEASE stfh weld above; (2) retire
the discriminator's `!flat_pat` conjunct; (3) flip default + delete the legacy proc jmp-entry carve arm
(`sub rsp,N` + zero-fill + wire-park — the named anti-pattern, literally visible as `proc_LBL__ROMAN_α`).
