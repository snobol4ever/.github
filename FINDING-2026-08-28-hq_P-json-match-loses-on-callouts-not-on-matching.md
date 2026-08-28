# json-match loses on CALLOUTS, not on matching — and claws5-match wins for the mirror-image reason

**Seat:** hq_P · **Date:** 2026-08-28 · **Mode:** DUO · **Row:** Lon tier-1 demo campaign (json's match-phase gap, handed to me by ceo)
**Instrument:** the two-aspect rep-loop bracket (match phase isolated), clean of the association tax — see the companion FINDING.

## The claim

json-match's match-phase deficit is **not a pattern-engine deficit**. Only **15.6%** of its match phase
runs in emitted match boxes at all. The rest is SNOBOL4 **procedure-call ceremony**, paid once per
pattern callout.

Measured, m4 `-O0`, 60,000 reps, clean bracket:

| symbol | share | what it is |
|---|---|---|
| `rt_name_save_push` | 5.78% | locals saved/restored **by name** |
| `rt_proc_call_prologue` | 5.52% | |
| `rt_proc_find` | 4.90% | |
| `__memmove_avx512` | 3.85% | argument copying |
| `rt_call_proc_descr` | 2.93% | |
| `rt_proc_call_open` | 2.52% | |
| `rt_proc_enter` | 2.02% | |
| `rt_name_save_grow` | 1.26% | |
| `rt_proc_call_epilogue_γ` | 1.05% | |
| **≈ 31.6%** | | **pure procedure-entry ceremony** |

plus ~4.5% in defer boxes and `rt_defer_probe_run`/`rt_defer_get_pat_dtp`, and ~8.7% in the kernel
(page faults).

## The differential is the diagnosis

The same profile taken on **claws5-match**, which SCRIP **wins at 1.681x**, comes back as **100% emitted
match boxes** in its top ten: `n81_match_break_α` 19.9%, `n79_match_span_α` 16.2%, `n84_match_span_α`
14.5%, `n82_match_lit_α` 7.1%, `n78_match_alternate_α` 7.0% — **zero runtime ceremony**.

⭐ **One mechanism explains both the win and the loss.** claws5's grammar is pure pattern primitives
(BREAK/SPAN/ANY/alternation), so it runs entirely inside emitted code and beats SPITBOL. json's grammar
drives the same engine through **procedure callouts**, and every callout pays full SNOBOL4 procedure
entry — name-based save/restore, proc lookup, prologue, argument copy, epilogue. **Where we spend time
in the pattern engine we win; where a demo reaches the engine through callouts we lose, and the loss is
the callout, not the match.**

## Corroborated by an independent instrument

This attribution was reached from the **match phase in isolation** (rep-loop bracket). `ceo` reached a
closely matching one the same night from a **whole-process** `perf record`: `rt_name_save_push` 6.7,
`rt_proc_find` 5.1, `rt_proc_call_prologue` 4.1, `rt_call_proc_descr` 3.4, arg memmove 5.4 — *"~19%+ in
procedure-entry ceremony per pattern callout."* **Two instruments, two seats, same answer**, which is
what the rule asks for before a number is trusted.

⛔ And it **kills a competing hypothesis** rather than merely adding to it: ceo proposed the gap was
capture-copy cost, since json is capture-heavy. Re-measured across hq_C's slice-(b) landing (which
removed the capture copy), json-match-fence moved **0.106x → 0.110x** — unchanged. Capture cost is not
the explanation.

## One cure landed tonight; the rest is design scale

✅ **Landed:** `rt_call_fastpath_ok()` forced `always_inline`. Its body is a single global read, but at
`-O0` a plain `static` compiles to a real call, and the annotation put `call rt_call_fastpath_ok` at
**9.20% of `rt_name_save_push`'s own self time**. Three call sites, all on the callout path.
**Measured: json-match's match phase 2341.1 → 2054.9 ns per match, −12.2%.** Sixth instance in this tree
of the class it already names five times (`rt_defer_merge_on`, `is_protected_pat_lead`,
`_var_find_cached`, `sv_len`, `comm_var_active`).

⛔ **A guess I checked and abandoned, recorded because the method is the point:** I expected
`rt_name_save_grow` — called once per parameter, a real call at `-O0` — to be the win, and had the hoist
half designed. The annotation does not show it in that function's hot instructions at all (it is 1.26%
of the program in its own right, from elsewhere). **Measuring before curing cost one command and saved a
pointless commit.**

⚠️ **The remainder is design scale and is not mine to improvise:** ~31.6% of ceremony cannot be inlined
away. The direction ceo already named is **frame-based DEFINE locals — the ζ discipline applied to
procedures** — which would replace name-keyed save/restore with frame slots. That is `GOAL`-level work
and it is the single largest lever on every callout-driven demo, not just json.

⚠️ **Scope note, stated rather than implied:** ~31.6% of ceremony does not by itself explain a **5x**
gap (json-match-fence 0.194x). Eliminating all of it yields roughly 1.5x. **The rest of json's deficit is
still unattributed** — the emitted boxes themselves are only 15.6%, so the arithmetic does not close, and
I am not claiming it does.
