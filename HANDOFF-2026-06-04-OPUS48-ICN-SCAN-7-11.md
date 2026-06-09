# HANDOFF 2026-06-04 (Opus 4.8) — Icon-BB: ICN-SCAN-7…11 — the wave-1 scan family is COMPLETE (stub list empty) + generator plumbing + two baseline-free oracle extensions

## TL;DR

Five gated rungs landed+pushed (SCAN-6 `b1a54a0` landed just before this window), each probe-green
m2==m3==m4, corpus set-diffs clean or explained, full gate battery per commit, clean rebases onto
orthogonal peers (Prolog PT-4a `89c730c`, Pascal PB-9e-1 `bd79c8b`) with merged-HEAD re-verification:

- **SCAN-7 `cc77b63` `bb_scan_tab`** — first δ-WRITER ("Reverses effects if resumed": saved-δ slot, β
  restore→ω); new `rt_icn_substr(sigma,a,b)` runtime entry (order-normalizing, GC_malloc copy, DESCR in
  rax:rdx); driver arm takes lit-int≥1 XOR a sibling IR_CALL producer slot with inline
  `flat_emit_arg_subchain` emission when the slot is missing — `tab(many('he'))` composition green.
- **SCAN-8 `14ec99a` `bb_scan_move`** + **FAMILY-WIDE TERMINALITY soundness fix.** Probing `move(-1)`
  exposed entry-only lit-arg digs across the family: the frontend lowers `-1` as `LIT_I(1)→γ→NEG`;
  admission/driver inspected only the subgraph ENTRY and mis-admitted the bare literal — confirmed live
  divergences `tab(-1)` (m2 'hell' vs native '' = silently ran tab(1)) and `pos(-1)`. Fix: a literal arg
  counts only when entry IS the whole subgraph (γ null or IR_SUCCEED) — `icn_scan_lit_entry` in scrip.c,
  `icn_arg_entry_terminal` mirrored in all six emit_bb driver digs. ZERO corpus flips: purely defensive.
- **SCAN-9 `c72e27d` `bb_scan_upto`** — THE FIRST SCAN GENERATOR: memory-slot cursor seeded δ, suspend
  `{DT_I,cursor+1}` with state persisting, **β RE-PUMPS** (cursor++ → loop). Three pieces of subchain
  generator plumbing, all gated `g_icn_scan_regs_live`: (1) BFS queues IR_CALL ω-successors (collects the
  EVERY tail, mirroring the main-chain collector); (2) subchain nodes register into `g_flat_chain_set`
  (without it `flat_drive_every` re-walks the body → duplicate `bb<id>_α` labels — binary m3 silently
  tolerates, text m4 rejects: a recurring m3/m4 asymmetry smell); (3) γ-resolution backward-edge generator
  redirect → `betas[k]` (`icn_subchain_node_is_generator`) — DORMANT: the lowerer never creates
  gen-backedges for IR_CALL scan fns, so native deterministically yields first results, matching the
  oracle bit-for-bit. **bb_every flat-dispatch parity fix:** dispatch is now
  `(MEDIUM_BINARY || g_descr_flat_chain) → bb_every_flat_str`; the legacy text template re-walks the body
  INSIDE the box string and emits an unlabeled leave fragment for GEN_SCAN bodies → undefined
  `.Levery<id>_body_α` at link (was the rung06 m4 failure). Legacy survives only non-flat text.
- **SCAN-10 `c9a728e` `bb_scan_find`** — UNROLLED literal byte-compare: the self-encoder's `movzx` is
  HARDWIRED to the `[r13+rcx]` subject form and no needle-byte load exists, but the needle is a wave-1
  LITERAL → per byte i: rcx=cursor+i, movzx subject byte, `cmp64` vs immediate `(uchar)s1[i]`. Zero
  calls, zero seals, zero push/pop. Admission needle 1..32. **Oracle:** by_name_dispatch had NO 1-arg
  scan-context find — BOTH dispatch sites extended (suffix-strstr + base rebasing at site-1; scan_subj
  fallback at site-2), gated on m2 129 set-identity BEFORE the box landed: baseline-free.
- **SCAN-11 `5de8d37` `bb_scan_bal`** — cursor+cnt two-slot state (`bb_slot_claim(8)`×2); wave-1
  c2='(' c3=')' as immediates, c1 via strchr; canon `cnt<0 → ω` (`jl`, mov/sub/mov — no dec encoder).
  **β-soundness BY ADMISSION:** the re-pump skips the suspended char's bracket count — canon-exact iff
  c1∩{'(',')'}=∅, so admission excludes brackets from c1 (the SCAN-8 lens generalized: restrict admission
  until the skipped work is provably a no-op). **Oracle:** site-2 (the live m2 path) had no bal clause at
  all — canon-exact clause added; site-1's existing clause canon-fixed (c1-test-first order; unconditional
  cnt-- failing on negative, was clamped at depth>0). Gated baseline-free. **`icn_kind_native_stub` now
  carries ZERO `IR_SCAN_*` kinds** — pos/any/match/many/tab/move/upto/find/bal all have native boxes.

Standing numbers at `5de8d37`: corpus m2 **129 HARD** / m3 **18** PASS·82F·**147E** / m4 **25**
PASS·136F·**86E**; smokes Icon 12/12 HARD · Prolog 5/5 · broker 32; gates: bb_bin_t 0 ·
no-handencoded --strict 0 · no-stack 10≤127 · one-reg-frame 0≤21 · no-vstack 3 · prove_lower2 PASS.

## FLAGS FOR LON

1. **ORACLE SCAN-FN GENERATIVITY (the decision).** Goal probes specify multi-result behavior
   (`"hello" ? every write(upto('l'))` → `3 4`; find → `2 4`; bal likewise). The m2 oracle is ONE-SHOT for
   every scan builtin: by_name_dispatch returns the first result from scan_pos with no per-call resumption
   state; `IR_interp.c` (~:291) declares scan fns non-single-shot as INTENT only — no pump machinery for
   name-dispatched builtins exists. Native matches the oracle exactly today and is PUMP-READY: every
   generator box has a working β re-pump and the subchain γ-redirect is wired (dormant — needs lowerer
   gen-arg recognition for IR_CALL scan fns). Making m2 generative SHIFTS THE 129 HARD BASELINE
   (rung08_strbuiltins_find_gen and friends would flip) → deliberately NOT done unilaterally. Your call on
   sequencing: oracle resumption machinery first, then lowerer recognition, then the native redirect goes
   live for free.
2. **rung02 userproc recursion abort (pre-existing).** PLAIN `write(fact(5))` — no every, no scan —
   aborts m4 `[GZ-10] recursion depth exceeded (4096)` and is silent-empty m3 (expected 120). Surfaced
   when the bb_every parity fix changed which body copy executes in the every-wrapped corpus entries
   (failure SHAPE changed; FAIL membership unchanged). Userproc-lane base-case bug, orthogonal to SCAN.
3. **bal site-1 semantics.** The site-1 canon fix (order + fail-on-negative) was baseline-free on m2, but
   if site-1 serves another consumer (m3 rt dispatch?), that path's behavior moved toward fstranl.r canon.

## NEXT

**ICN-SCAN-12 — `=s` sugar (NO new BB):** lowerer Icon unary-`=` arm rewrites to the `tab(match(s))`
shape per the goal entry. Then SCAN-13 `?:=` scan-assign, SCAN-FENCE. Probe files in /tmp are
container-ephemeral; recreate from the goal probes.

## Transferable findings

- Self-encoder gaps: `movzx` subject-hardwired; no `xor`, no `dec` → `mov reg,imm` / mov-sub-mov; `jl`=0x8C
  exists. Literal operands prefer unrolled immediate compares over runtime loads (find).
- Duplicate-label link errors in m4-only = double emission that binary mode masks; check
  `g_flat_chain_set` registration first.
- Corpus entries keep four artifacts (.icn/.expected/.s/.j); the suite globs ONLY *.icn — the .s files are
  reference output from another emitter, not inputs.
- Oracle extensions are safe when gated on m2 set-identity BEFORE the native box lands (find, bal).
