# FINDING s183 — THE JIT ROAD PUBLISHED A SCAFFOLDING `IR_GOTO` AS ITS RESUME CARRIER

**Seat:** seat1 (Opus 5), 2026-08-20, queue row 1 `m1-fncat-beta`. **Tree:** SCRIP + this session's one edit, corpus at `d598b813`, **pristine build at RT_OPT=-O0** (`make pristine`, rc=0) before every verdict below.
**Brief:** FINDING-2026-08-20-s182 addendum 3 — *"give the JIT'd `TT_SEQ` a real β."*

## ⭐ THE HEADLINE — THE WIRE WAS NEVER MISSING FROM THE SEAM, IT WAS MISSING FROM THE PUBLICATION
`sno_pat_tree_graph_rt` (`lower_snobol4.c:2841`) — the graph builder for the **runtime/JIT** road (`dtp_fn_of` → `bb_compile_pat_tree_sz`) — published
```c
gp->body_root = (gp->n > before_pat && !sno_pat_right_sealed(pat)) ? gp->all[before_pat] : NULL;
```
For a composed `TT_SEQ`, `gp->all[before_pat]` is **not an element** — it is the nary builder's argument-less **`IR_GOTO` relay sentinel**. That node is never emitted, so the β-dispatch's carrier lookup (`emit.cpp:3347`, `nodes[i] == body_root`) **could never match**, `resume_tgt` stayed `lbl_ω`, and the blob emitted the wholesale concede. The left-cascade seam the retreat needed **was already built by the element templates**; nothing was ever wired to enter it.

## THE PROOF, MEASURED NOT INFERRED (`SCRIP_RESUME_WHY=1`, plain build, no monitor)
| witness | `body_root_op` | `in_nodes` | consequence |
|---|---|---|---|
| `ptw_min_fncat_arbno` (RED), JIT'd `P = mk() ''` blob | **116 = `IR_SUCCEED`** (raw: 35 = `IR_GOTO`, folded by the optimizer) | **0 — NOT IN THE EMITTED GRAPH** | no carrier → `PAT$N_β: jmp PAT$N_ω` |
| `ptw_min_varcat` (PASS), static `PAT$` blob | 72 = `IR_MATCH_LIT`, tier 2 | 1 | seam entered at its right end, walks leftward to the ARBNO |
A `SCRIP_RTGRAPH_WHY` dump of the JIT graph named the shape outright: `before_pat=2 n=5 nodes: [2]=IR_GOTO [3]=IR_MATCH_DEFER<ENTRY> [4]=IR_MATCH_LIT`. **`all[before_pat]` is the scaffold; the elements are `[3]` and `[4]`.**
The ZSM census read the same defect from the other end: retreat arrives at the outer `*P` defer and goes straight to `MATCH_BEGIN`'s restart loop — `β·MATCH_DEFER → ω·MATCH_DEFER → β MATCH_BEGIN` — never touching the composed elements.

## THE CURE — RTSEQ-RESUME (one function, mirroring a precedent already in the tree)
**s121 half B1 solved this exact problem for the STATIC `PAT$` road** (`lower_snobol4.c:2594-2628`) and the JIT road never received it. Two halves, transplanted verbatim:
1. **the right tail** — a fence-free multi-element top is built through `sno_seq_nary` (the *identical* flatten→nary path `sno_pat_node`'s own `TT_SEQ` arm takes, so emission is byte-identical) one level lower **only to capture `out_rtail`**, the run's rightmost element carrier;
2. **the GOTO skip** — the fallback walks past argument-less `IR_GOTO` relays to the first REAL body node.
**Narrowed deliberately:** the fenced RT case keeps today's publication **exactly** — one rung, one change. **Zero new globals** (`sno_rtseq_resume()` is a function-local `static`, the construction `sno_defer_resume`/`sno_const_feature` already use). **Killswitch `SCRIP_RTSEQ_RESUME=0`** restores the pre-fix emission.

## RECEIPTS (pristine, RT_OPT=-O0; every A/B is the killswitch, not a recorded number)
- **THE GATE, MET:** `ptw_min_fncat_arbno` ARBNO ports **2 (α+γ only) → 6 (β retries present)**, `nomatch → match`, oracle-identical. `ptw_min_fncat_two` likewise.
- **CONTROLS UNCHANGED:** `ptw_min_varcat`, `ptw_min_fncat_inline` — 6 ports, `match`, both arms.
- **THE 7-MOVER FENCE CLASS ALL GREEN:** 114 · 119 · 129 · 130 · 148 · 149 · 150.
- **CORPUS m3 332/5 · m4 325/11 — and the FAIL-SET IS BYTE-IDENTICAL** across the killswitch A/B (`diff` empty). Zero regressions, measured both arms this session.
- **PASSTHRU BOARD — A PURE CURE, +5 IN BOTH MODES:** m3 **114 → 119**, m4 **106 → 111**. Red-set diff is five programs RED→GREEN and **zero new reds**: `ptw_min_fncat_arbno` · `ptw_min_fncat_two` · `ptw_min_compose` · `ptw_min_compose_nocap` · `ptw_min_poison_eval`.
- **STATIC EMISSION UNTOUCHED:** `treebank` / `json` / `calculator-1` mode-4 `.s` **byte-identical** across the A/B. ⛔ The `.s` regen commit `d598b813` is therefore **pre-existing drift from prior landings, NOT this rung's output** — recorded so nobody reads that churn as codegen movement.

## ⭐⭐ AND THE POISON CLASS WAS THE SAME CLASS
s182 recorded the EVAL/indirect poison as a **separate** defect producing silent wrong answers on the runtime-composed road. **It was this defect all along.** The poison's only role was to *push* a variable-held concat onto the runtime road; once there, the road had no β. `ptw_min_poison_eval`, `ptw_min_compose` and `ptw_min_compose_nocap` all fall to this one wire, with no change to the poison itself. The poison remains a real staging-loss issue; it is no longer a wrong-answer generator on this road.

## ⛔ BEAUTY: `Parse Error` → **SIGSEGV**. STATED PLAINLY, NOT BURIED.
`printf '\n' | scrip beauty.sno` was `Parse Error` (rc=0) and is now **rc=139**; `SCRIP_RTSEQ_RESUME=0` restores `Parse Error`, so this rung caused the change. The oracle answers one blank line. **This is not M1 finished, and it is not a new class:** the backtrace is `SIGSEGV in _rtld_global`, `#1 0x0000000000000000 in ?? ()` — **the identical signature s182 addendum 1 already recorded** for the `Parse = *Command` / `*Label nl` override witnesses, i.e. a wild jump through a corrupted continuation, the pass-thru class (ARCH-PASSTHRU law 0a/2). With the β wire in place beauty's `Parse` now genuinely re-enters the composed graph and reaches the wall those overrides already isolated, instead of concealing it behind an early wrong answer. Honest bomb over silent wrong answer (RULES), and the override witnesses are the standing handle on it.

## NEXT, IN ORDER
1. **The pass-thru continuation defect** — beauty's SIGSEGV and the s182 `Parse = *Command` / `*Label nl` overrides are now provably one target with a 1-byte input and a 2-frame backtrace.
2. Re-run `util_autobug.sh` on beauty and watch the divergence step move again (1499 → 1568 on the first cure).
3. The fenced RT publication, deliberately left at today's behavior by this rung — the static road refuses it (NULL); the JIT road still publishes the stale first-allocated node.
4. `&FULLSCAN=0` → ERROR 274 (s182 carry-over, cheap, unrelated).
