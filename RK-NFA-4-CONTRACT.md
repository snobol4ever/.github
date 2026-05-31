## ✅ UPDATE-2 (Opus 4.8, 2026-05-29 — S2+S3 L1 GREEN, SCRIP `57ec5cea`)

The corrected S2 design below is now BUILT and PROVEN. L1 `/x/`~"x" matches through the emitted
isolated BB_NFA_* slab in mode-4, byte-identical to the C matcher (match / miss / leftmost-offset).
The node-keyed walker is `nfa_text_box()` in `sm_bb_switch.cpp`'s SM_BB_INVOKE **MEDIUM_TEXT** arm
(gated `bb_op_is_nfa(gen->t)`); leaves `bb_nfa_char`/`bb_nfa_accept` (MEDIUM_TEXT) in `bb_nfa.cpp`;
`emit_core.c` routes CHAR/ACCEPT (ANY/CLASS/SPLIT/BOL/EOL still `bb_stub`). Register model exactly
as specified: r13=pos, r14=base, r15d=slen, r12d=sweep-sp, callee-saved (push/pop r12-r15 in the
walker). Subject popped off the SM value stack (rax{v|slen}:rdx{ptr}); int verdict pushed so the
`if` SM_VOID_POP balances; `last_ok` drives JUMP_F. Default OFF; all gates at baseline; FACT 0.
NEXT: bb_nfa_any/class/bol/eol/split leaves (SPLIT needs its β=out2 label threaded in `nfa_text_box`),
then RK-NFA-3 captures, then RK-NFA-5 mode-3 BINARY twins.

---

# RK-NFA-4 / G1-1 — RESOLVED ENTRY CONTRACT (drop-in spec)

## ⚠️ UPDATE (Opus 4.8, 2026-05-29 — S1 LANDED + S2 CONTRACT CORRECTED, SCRIP `c8aeb90d`)

**S1 DONE and pushed.** The gated `~~` rewiring is in `lower.c` TT_SMATCH (NOT ~line 2488 — the real
case is ~line 2492). `getenv("RK_NFA_BB") && flavor==match` → `raku_nfa_build(t->c[1]->v.sval)` (the
compile fn is `raku_nfa_build`, **NOT** `raku_nfa_compile` as this note originally said) →
`raku_nfa_to_bb` → `lower_expr(c[0])` (subject) → `SM_seq_bb_add` + `SM_BB_INVOKE`; `raku_nfa_free(nfa)`
after (the builder copies everything out — safe). Verified by `--dump-sm`: flag OFF → `SM_CALL_FN
raku_match`; flag ON → `SM_BB_INVOKE`. Default path untouched; all gates at baseline (m2 41/42, m4 42/42,
m3 41/42 CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0).

**⛔ S2 CONTRACT WAS WRONG — corrected here (the real blocker for the next session).** The "S2 —
`flat_drive_nfa` arm in `walk_bb_flat`" plan below targets the **WRONG entry**. Traced the live mode-4
Raku `~~` path against real code:

- `SM_BB_INVOKE` → `emit_core.c:858 sm_bb_invoke(pSM)` → `SM_templates/sm_bb_switch.cpp` **MEDIUM_BINARY**
  arm. That arm builds a per-site entry-flag dispatch (fresh-α vs β-resume), then calls
  **`walk_bb_node(gen, NULL)`** (emit_core.c:528) — a **SINGLE-NODE** dispatcher that emits ONLY the
  entry node's template and returns — then a γ-postamble (`rt_set_last_ok(1)`) / ω-postamble (reset flag,
  `rt_set_last_ok(0)`). `SM_BB_INVOKE` is always followed by `SM_JUMP_F` reading `last_ok`.
- `walk_bb_flat` (the `flat_drive_*` family) is the **Icon flat-codegen** path (`codegen_flat_body`),
  reached for Icon's `--run`/BB slabs — NOT the Raku `SM_BB_INVOKE` path. So adding `flat_drive_nfa`
  there would never be hit by Raku `~~`.
- Why `bb_to_by`/`bb_iterate` work as single `walk_bb_node` nodes: each is **self-contained** — bounds
  baked compile-time (`bb_to_by`: `movabs rax,hi`) or read from a **named var** (`bb_iterate`:
  `NV_GET_fn(pBB->sval)`), state in `&pBB->counter`. The NFA graph from `raku_nfa_to_bb` is genuinely
  **multi-node** (CHAR→ACCEPT, SPLIT branching) with γ/β pointers between nodes — one `walk_bb_node`
  call cannot traverse it.

**Corrected S2 (the design the next session must build):** add an NFA-graph walker **inside the
`sm_bb_switch.cpp` MEDIUM_BINARY arm**, gated on `gen->t ∈ BB_NFA_*` (and `gen` graph lang == RKU),
that:
1. **Subject preamble (α):** pop the subject DESCR off the SM value stack (the subject was pushed by S1's
   `lower_expr(c[0])`). Unpack to base ptr + slen. Model the unpack on `bb_iterate.cpp`'s DESCR handling
   (`low32=v, hi32=slen; rdx=base ptr`) but the *source* is the vstack (`rt_pop`-style), not `NV_GET`.
   Hold subject base / slen / pos in callee-saved regs (r14/r15d/r13 still fine — the slab prologue
   `sub rsp,8` clobbers none).
2. **Leftmost sweep:** wrap the node walk in a `for sp in 0..slen` loop (mirror `raku_nfa_bb_match`);
   leaf-ω → sweep-continue, ACCEPT-γ → outer γ-postamble, sweep-exhausted → outer ω-postamble.
3. **Node-keyed walk:** mint a label per graph node (mirror `flat_drive_seq`'s node→label table,
   `emit_bb.c:745`), emit each leaf via its `bb_nfa_*` template, wire γ→next-node-label,
   β→SPLIT-out2-label. The templates (S3) own only their own leaf bytes (FACT); the walker owns the
   wiring + preamble + sweep. The cap block (`GC_malloc`) for `$0`/`$1` lands with RK-NFA-3 captures;
   L1 (`/x/`) needs none.

This is a NEW node-keyed walker in the BINARY arm — **NOT pure transcription**; budget a fresh session.
First atom unchanged: **L1 `/x/`~"x" = S1(done) + S2-walker + bb_nfa_char + bb_nfa_accept** (no SPLIT).

The original (now-superseded for the entry-point question) analysis follows; its template *byte sketches*
and matcher *spec* (`nfa_bt`) remain valid — only the "where the driver lives" claim changed.

---

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
