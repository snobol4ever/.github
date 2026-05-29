# RK-NFA-4 / G1-1 — RESOLVED ENTRY CONTRACT (drop-in spec)

**Status:** contract resolved by reading the real code paths (Opus 4.8, 2026-05-29). NO code committed
— this note converts G1-1 from "register model proposed" to "pure transcription." Execute as one
env-gated unit so the default path is never at risk.

## Why the templates were NOT the first sub-step

`walk_bb_flat` (emit_bb.c) has **no `flat_drive_nfa` arm** → `BB_NFA_*` kinds hit `default:`
(`define β; jmp ω; jmp ω`, the degenerate skip). The flat slab is entered via `call fn(NULL,0)`
(`xa_flat.cpp` prologue: `sub rsp,8; cmp esi,0; je α_body; jmp β`) — **no subject/pos/slen args**,
only `g_vstack` + the SIGMA return slot. So the "proposed" r13/r14/r15 model had no setup and the
7 templates had no driver. The driver/ABI is the prerequisite, not the templates.

## The five confirmed facts (all from real code)

1. **Pattern is compile-time** — `raku.y:468` `TT_SMATCH` c[1] = `leaf_sval(TT_QLIT, LIT_REGEX)`;
   at lower time the raw regex source is `t->c[1]->v.sval`. → can compile in the lowering.
2. **Graph builder ready** — `raku_nfa_to_bb(Raku_nfa*)` (RK-NFA-1b ✅, raku_nfa_bb.c) emits the
   isolated `BB_NFA_*` graph: γ=out1-node, β=out2-node (SPLIT only), CHAR ival=char,
   CLASS sval=32-byte cset, CAP ival=group-idx, `bbg->entry`=start.
3. **Registration** — `int64_t bb_idx = SM_seq_bb_add(g_p, bbg); SM_emit_si(g_p, SM_BB_INVOKE, NULL, bb_idx);`
   (lower.c:245-246 model).
4. **Relocation machinery** — `bin = {{site_offsets},{label_ptrs},{is_def}}`; `is_def=true` defines a
   label AT that offset, `false` patches a rel32 there (bb_eps.cpp / bb_alt.cpp).
5. **SPLIT live model** — `bb_alt.cpp` MEDIUM_BINARY is the counter-state dispatch slab to mirror for
   `bb_nfa_split` (try γ, on backtrack β).

## Matcher spec to reproduce in x86 (nfa_bt, raku_nfa_bb.c)

ACCEPT→return pos; EPS/CAP→tail to γ; BOL→`pos==0`?γ:ω; EOL→`pos==slen`?γ:ω;
CHAR→`pos<slen && subj[pos]==ch`?(pos++ ;γ):ω; ANY→`pos<slen && subj[pos]!='\n'`?(pos++;γ):ω;
CLASS→`pos<slen && cset_test`?(pos++;γ):ω; SPLIT→try γ(out1); on fail try β(out2); both fail→ω.

## Register/ABI contract (now grounded, not proposed)

The slab takes no subject arg, so the **driver** loads it once:
- **r14** = subject base ptr, **r15d** = slen (popped from g_vstack top via `rt_pop` → DESCR str+len),
- **r13** = pos (cursor), set per sweep iteration,
- **capture block** = `GC_malloc(ncap*2*8)` quad array, address held in a malloc'd slot reached by
  `movabs` (mode-3) / `@PLT` (mode-4) — **never a BB_t field** (PEERS RULE).
- r13/r14/r15 are callee-saved and the flat prologue/epilogue clobber none of them → safe to own.

## Sub-step ordering (all behind `getenv("RK_NFA_BB")`, default OFF)

### S1 — lowering rewiring (lower.c TT_SMATCH, ~line 2488)
```c
if (getenv("RK_NFA_BB") && strcmp(flavor,"match")==0
    && t->n>=2 && t->c[1] && t->c[1]->v.sval) {
    Raku_nfa *nfa = raku_nfa_compile(t->c[1]->v.sval);     /* raku_re.c */
    BB_graph_t *bbg = nfa ? raku_nfa_to_bb(nfa) : NULL;     /* RK-NFA-1b */
    if (bbg && bbg->entry) {
        lower_expr(t->c[0]);                                /* subject → vstack */
        int64_t bb_idx = (int64_t)SM_seq_bb_add(g_p, bbg);
        SM_emit_si(g_p, SM_BB_INVOKE, NULL, bb_idx);
        return;
    }
    if (bbg) BB_free(bbg);
}
/* fall through to the proven C-matcher SM_CALL_FN raku_match path (unchanged) */
```

### S2 — driver: `flat_drive_nfa` arm in `walk_bb_flat` (emit_bb.c)
Detect entry kind ∈ BB_NFA_* → emit preamble (pop subject → r14/r15, GC_malloc cap block,
sweep-loop top: `r13 = sp`), then FILL the entry node (γ-chain walks the leaves via existing flat
machinery), wiring every leaf ω → sweep-continue label, ACCEPT γ → outer γ; sweep exhausted → outer ω.
Mirror the leftmost sweep in `raku_nfa_bb_match` (`for sp 0..slen`).

### S3 — leaf templates (bb_nfa.cpp), against r13/r14/r15
- **bb_nfa_accept**: push match result (pos in r13) → `jmp γ`.
- **bb_nfa_char**: `cmp byte [r14+r13], ival` `jne ω`; `inc r13`; `jmp γ`. (+bounds `cmp r13d,r15d; jge ω`.)
- bb_nfa_any / bb_nfa_class / bb_nfa_bol / bb_nfa_eol per the matcher spec; bb_nfa_split per bb_alt model.

### S4 — gate ladder (per sub-step)
Default (RK_NFA_BB unset): GATE-RK 41/42, GATE-RK4 42/42, GATE-RK3 41/42, smoke 5/5/5/13/5,
SNOBOL4 iso M2 19/0 M4 18/1, FACT 0 — **must hold every step** (default path untouched).
With RK_NFA_BB=1: prove L1 `/x/`~"x", then L2/L3 `/.*/`, … up the L1–L15 ladder the C matcher already
passes. Flip default last (G1-3) only when the full ladder is green via BB.

## First testable atom

L1 `/x/`~"x" needs only S1 + S2 + bb_nfa_char + bb_nfa_accept. That is the smallest end-to-end runnable
slice; everything below CHAR/ACCEPT (ANY/CLASS/SPLIT/BOL/EOL) extends it leaf-by-leaf.
