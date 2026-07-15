# FINDING 2026-07-14 s61 — PROC-CONV: the epilogue is a BOTH-EDGES obligation; the s59 corrections do not cover it

AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
GOAL: GOAL-SNOBOL4-BB.md RUNG ZS → PROC-CONV (R12-FREE ladder rung 2). Base: SCRIP `a15b82ad` → `f6b1d7a4`.
READ FIRST: FINDING-2026-07-14-CLAUDE-ZS2-LANDED-JMP-ENTRY-DEFER.md (the reference implementation).

## THE GAP — new, not a re-derivation of the s59 pair

The rung spec says the s59 FINDING's two measured corrections (frontier resume record; ABSOLUTE ω unwind)
"apply to procs verbatim — do not re-derive." **They do, and they are not the whole story.** A proc has a
THIRD problem the pattern-blob conversions never hit, because DEFER/EVAL have no prologue/epilogue bracket
straddling the transfer and a proc does:

```
_wn = rt_g_want_name; rt_g_want_name = 0;          /* save want-name                     */
p = rt_proc_find(name);                            /* RESOLVE — a C call, never the transfer */
fbytes = rt_proc_call_prologue(p, args, nargs, _wn);/* bind args, push save-cells        */
fb = alloca(fbytes) | rt_zls2_push(fbytes);        /* CALLER-side alloc — dies this rung */
memset(fb, 0, fbytes);                             /* → blob rep-stosb                   */
fret = p->fn(fb, 0);                               /* THE CALL → wire + jmp              */
rt_zls2_release_to(fb + fbytes);                   /* → ABSOLUTE unwind (s59 correction) */
return rt_proc_call_epilogue(fret);                /* ⚠ BOTH-EDGES OBLIGATION            */
```

`rt_proc_call_epilogue` is **not** bookkeeping that can ride one edge. It pops `g_pcall` exactly once,
restores Σ/Σlen (the SUBJECT registers — R13/R15 in the ratified layout), runs `rt_nret_fix`, and calls
`rt_name_restore(c.save_base)` (SNOBOL4's dynamic-scope discipline, manual Ch.8 "Local variables"). Under
`call`/`ret` **both RETURN and FRETURN funnel through one `ret`**, so the epilogue runs unconditionally and
the obligation is invisible. Under jmp-entry with split wires it is not: each edge must still pop once and
restore once, or the pcall stack and Σ desynchronize.

⚠ **`rt_chain_enter` DOES NOT GENERALIZE HERE — do not copy it.** It wires γ and ω to the SAME landing:
```
  leaq 1f(%rip), %rcx        /* γ wire  */
  movq %rcx, %rdx            /* ω wire ← the SAME address */
```
EVAL can share one landing because it does not care which port fired. **A proc cares**: RETURN vs FRETURN is
observable at the call site via `:S()F()`. Copying the shared-landing trick loses the distinction.

## RULING 1 (recorded) — TWO LANDINGS, ONE BODY, TWO ENTRIES; NO DISCRIMINATOR FLAG

Converging both wires on one landing and re-dispersing needs a "which edge was I on?" flag — which is exactly
the `LAST_OK` pathology ARCH-ICON.md indicts for relops ("SCRIP historically reified a LAST_OK flag + a BB_IF
router instead"). **`FAILDESCR`-as-return-value IS the proc-level LAST_OK.** Instead: each landing is its own
address and therefore *statically knows its port*; both call ONE shared epilogue body (a C call is fine —
bookkeeping, never the transfer), then each jumps its own caller wire.

**The manual settles it.** Ch.8 reserved-label table: RETURN = "Return success from function", FRETURN =
"Return failing from function"; and the FRETURN passage verbatim: *"Transferring to the special label FRETURN
returns from a function signaling failure to the caller. **No value is returned as the function result.**"*
So `IS_FAIL_fn(fret)` encodes a fact the port already carries. Under two wires the discriminator DELETES
ITSELF — arriving at ω *is* the failure signal.

## RULING 2 (recorded) — NRETURN IS A γ CITIZEN; NO FIFTH PORT. Already true in the lowering.

The manual gives THREE return paths (Ch.9 NRETURN: "a third way that a function may return... returning the
name (i.e., address) of a variable"). This is NOT a third port. `lower_snobol4.c` already routes all three
into the four-port model — verified live, not inferred:
```
if (!bb_label_landing("RETURN"))  bb_label_registry_add("RETURN",  exitnd);   /* → γ */
if (!bb_label_landing("FRETURN")) bb_label_registry_add("FRETURN", failnd);   /* → ω */
if (!bb_label_landing("NRETURN")) { ... IR_CALL "SNO$NRET" → exitnd ... }     /* → γ + flag */
```
`SNO$NRET` (by_name_dispatch.c:4786) sets `rt_g_ret_by_name = 1` and falls to `exitnd` — the SAME γ as RETURN.
RULES.md ("FOUR PORTS = FOUR GREEK NAMES ALWAYS") forbids a fifth port anyway; the lowering already agrees.
**⇒ The IR has spoken γ/ω all along. The call regime is an emitter/runtime artifact flattening a structural
fact into a sentinel. PROC-CONV is not adding ports — it is deleting a round-trip.**

⚠ `rt_g_ret_by_name` is NOT redundant with the DESCR tag — do not "simplify" it away. `rt_nret_fix` derefs
only when the flag is set AND `r.v == DT_N`; the flag distinguishes "DT_N because NRETURN put it there" from
"DT_N because the proc legitimately returned a name-valued datum." Only the former derefs.

## OPEN — NEEDS A LON RULING BEFORE THE TRANSFER CONVERTS

**The `c.lex` arm is PORT-AGNOSTIC today.** `if (c.lex) return rt_nret_fix(*(DESCR_t *)c.fb, c.wn);` runs
BEFORE the Σ restore and reads the result from `[fb+0]` **whether the callee reached RETURN or FRETURN — the
port is ignored entirely**, and `fret` is discarded. Preserved verbatim this rung (that is what makes it
watermark-neutral), but under two wires the ω landing must be told what a lexical proc's failure means:
does the lex arm (a) stay port-agnostic, (b) return FAILDESCR on ω, or (c) is a failing lex proc currently
a latent bug the call regime is masking? Note it also skips `rt_name_restore` and the monitor event.

## WHAT LANDED (SCRIP `f6b1d7a4`) — REFACTOR ONLY, WATERMARK-NEUTRAL BY CONSTRUCTION

`rt_proc_call_epilogue` split in `src/runtime/rt/rt.c`:
- `rt_proc_epilogue_body(rt_pcall_t c, int failed)` — static, the one body. `failed` replaces `IS_FAIL_fn`
  and is a CONSTANT at each entry, not a flag consulted from a global.
- `rt_proc_call_epilogue_γ(void)` / `rt_proc_call_epilogue_ω(void)` — the two entries PROC-CONV's landings
  will reach directly. Greek names per RULES.md (precedent: `lc_γ_to`, 54 uses).
- `rt_proc_call_epilogue(DESCR_t fret)` — RETAINED as a shim dispatching on `IS_FAIL_fn`, so every existing
  call site behaves verbatim. **This shim + IS_FAIL_fn are what PROC-CONV deletes.**

## GATES (all green, this tree)
- Crosscheck m3 305/2 (expr_eval, 141) · m4 304/2/1 (expr_eval, 1017) · DIVERGE=1(1017) — **IDENTICAL to the
  s60 watermark.** Smoke sno 7/7×2 · icon 14/0 · prolog 5/0 · raku 234/20 (the documented pre-existing 20).
- **Codegen-neutrality PROVEN, not asserted:** all three `.s` regen scripts (benchmark / feature / demo) report
  0 changed artifacts. `scrip --compile` is deterministic, so byte-identical artifacts ⇒ the emitter was not
  perturbed. (Demo SKIPs = the pre-existing mid-design bombs; committed `.s` untouched, per the script's rule.)

## LADDER STATE
PROC-CONV remains the NEXT RUNG — this landed its prerequisite only. Still to do: the name gate
(`emit_jmp_entry_for_patproc` is `PAT$`-prefix-gated at emit.cpp:1897 and the regime machinery already exists —
`g_emit.flat_jmp_entry` + `flat_frame_bytes`, K_total = `(32 + zls_g_region(g) + 15) & ~15`); the four rt.c
call sites (549 · 878 · 892 · 980) + the 591/608 frame_prep/release family; wiring exitnd/failnd to rcx/rdx;
the two landings calling `_γ`/`_ω`; the `c.lex` ruling above. **Big-bang caveat: a proc speaks call-regime OR
jmp-regime, never half — every proc call site converts in ONE commit.** Then SLOT-MIGRATE → FLIP.
