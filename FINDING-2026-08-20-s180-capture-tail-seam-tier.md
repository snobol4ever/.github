# FINDING s180 (HQ, Fable 5, 2026-08-20) — THE BEAUTY PARSE WALL IS TWO ROADS: THE BLOB HALF FELL TODAY (CAPTURE WRAPPERS JOIN SEAM TIER 2), THE COMPOSED-VALUE HALF IS NAMED AND WITNESSED

## The hunt (fwctx conjunction → a 6-line mechanism), each step measured
1. In-program ladder probes on `fwctx_conjunction`: needle vars correct; `*Command` DIRECT matches with all SHX captures firing; the failure is the **Parse composition layer**.
2. Element bisect: `ARBNO(*Command)` ✓ · `nP2() ARBNO(*Command)` ✓ · **`ARBNO(*Command) ("'Parse'" & 1)` ✗** — the `&` conjunct after ARBNO.
3. Stock sbl: bare `&` = ERROR 029 undefined operator ⇒ the includes define it: `semantic.inc: OPSYN('&','reduce',2) / OPSYN('~','shift',2)` — **beauty's shift-reduce grammar is BUILT on OPSYN'd binary operators** (why every ingredient passes alone: no OPSYN without the includes). Bonus fact: stock sbl FOLDS LABEL CASE (`reduce`/`Reduce` = ERROR 217 duplicate) and SIGSEGVs after 217 — relevant to the datatype-case row and to witness minting.
4. Standalone 20-liner: `'a' ("'q'" & 1)` ✓ vs `ARBNO('a') ("'q'" & 1)` ✗. Further ablation: even **`ARBNO('a') ('' . v)`** via `*P` seam fails; inline (no seam) passes; draw-out (`… ('' . v) 'b'` retreat inside the blob) passes; capture-less seam passes. **Class: β-retreat across the `*P` seam into a stored pattern whose rightmost element is a CAPTURE.**
5. ASM diff (wpass/wfail pair): the confession verbatim — `PAT$0_β: jmp PAT$0_ω` (wholesale refusal) vs wpass's `PAT$0_β → n0_match_arbno_β`. The interior β chain (`cond_β: sub r12,24` → `lit_β/save_β: add rsp,16` → arbno extend) was ALREADY EMITTED AND CORRECT — only the dispatch refused to enter it.

## The cure (SCRIP `zeta_depth.c`, ONE lattice line + killswitch)
`resume_carrier_ok` consults `zdp_seam_tier` (s124: tier 1 = extending generators; tier 2 = deterministic self-undo fail-throughs, refusal list named "ASSIGN_* capture wrappers"). The capture wrappers ARE tier-2 members by the tier's own definition — measured, not assumed. `IR_MATCH_ASSIGN_COND/_SAVE → 2` behind `SCRIP_CAP_SEAMTIER` (=0 reverts byte-identically). ASSIGN_IMM stays 0 (side effect fires during match; undo is not a pure record pop; unmeasured).

## Receipts (pristine -O0 `e33be152`+)
8-row ablation family oracle-identical · **passthru board m3 105/106 → 106/106** — the cure ALSO felled `pt1_retreat_3layer_bare`, the s177 standing DT_P red, BOTH modes (m4 97→98) · corpus **m3 331/6 · m4 325/11 fail-sets exact** · killswitch-off reproduces the nomatch verbatim. Witnesses pushed: `ptct_seam_tail` (green acceptance).

## ⛔ THE RESIDUE — beauty's actual road, NAMED RED, witnessed, next rung
`ptw_min_compose` (8 lines): `A = ARBNO('a')` · `B = '' . v` · **`P2 = A B`** — both elements VARIABLE-HELD pattern values, so `A B` is lowered as generic concat (string-vs-pattern unknowable statically) and the match runs the RUNTIME-COMPOSED road; scrip nomatch, oracle match. One static element in the RHS (either side) is cured by today's fix. Beauty's grammar assignments are exactly this shape (build-time calls `nP2()`/`&`-calls composing pattern VALUES), so **beauty m3 still prints Parse Error** — unchanged by the blob-side cure. Second residue witness: `ptw_min_opsyn_evalpat` (the OPSYN fn-returned EVAL pattern after ARBNO — same road, dressed as beauty). The hunt resumes INSIDE the runtime composer/C-engine: how a concat-of-DT_P-values node propagates β-retreat from a capture-value element back into an ARBNO-value element's extension (the "4 patv C-road calls at cur=0" from the s178-f gdb receipt is this road's signature).

## Also learned on the way
`opsyn_bin_pct`/`opsyn_bin_pound` (`%`/`#` FAIL where `&`/`@`/`~` PASS — a parser-side per-character face, separate from all of the above) · `opsyn_unary_target`, `d_unary`, `opsyn_builtin_target` fail — the unary-OPSYN and builtin-target faces; family census in `probe/opsyn/`.
