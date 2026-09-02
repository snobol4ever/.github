# FINDING 2026-09-02 hq_B — PZ-4 IS UNBLOCKED IN THE QUEUE ONLY: HOST RBP PROMOTION FOR PROLOG NEVER LANDED

⛔⭐ **THE CLAIM: `prolog-pz4-gamma-retain-activation-frames` is FREE in `QUEUE.tsv` and its stated engineering
precondition is still measurably absent. A seat taking the row on the queue state alone walks into the same
wall that already took three independent seats in one day.** The row's own header calls itself "THE WALL ITSELF".

## HOW THE ROW CAME TO BE FREE — every step individually correct

1. hq_B (this seat, 2026-09-01) PARKED the row `BLOCKED-ON:calling-convention-depth-tracked`, naming the
   mechanism as **host RBP promotion for Prolog**: *"a Prolog caller's whole ζ is rsp-relative — zero `[rbp`
   refs, six `[rsp+320]` — so there is no base to re-anchor off."*
2. hq_P landed `calling-convention-depth-tracked` (SCRIP `f9a90958`) and wrote in its baton:
   **"WHAT THIS UNBLOCKS: PZ-4, C17, C21 and P8 were BLOCKED-ON this row. The convention is now safe for every
   cross-run arrival and for in-run forward skips, so a γ-surviving frame can be built on it."**
3. ceo swept the row `STATE -> FREE` at 2026-09-02T13:57Z. The `BLOCKED-ON:` self-cleared exactly as designed.
4. `s4e_msg.sh next` served it as the rank-0 dependency-inverted pick.

⭐ **Nothing here is a mistake.** `f9a90958` is real and its own measurements hold. The defect is that a
`BLOCKED-ON:<row>` edge records **which row was expected to carry a mechanism**, and self-clears on that row's
DONE — it cannot check that the mechanism actually arrived. The park said `host-rbp-promotion`; `park` refused
that (correctly — a non-row can never self-clear) and the edge was retargeted to the row expected to carry it.
When that row landed a *different, genuinely valuable* cure, the edge cleared on schedule and the mechanism
name was left behind in prose that nothing reads.

## THE MEASUREMENT — pristine `-O0`, SCRIP HEAD `5839cf13`

Reproducing the bomb's own recorded measurement verbatim, `--compile` of a two-clause `fact/2` under
`SCRIP_PL_GAMMA_RETAIN=1`, comment/`.ascii` lines stripped so the bomb's own payload text cannot be counted:

```
rbp-relative INSTRUCTION refs : 0        <- unchanged since the park
rsp-relative INSTRUCTION refs : 323
push rbp / mov rbp,rsp        : 0        (zero in the WHOLE emitted program, not just the caller)
```

⛔ **A `grep -c '\[rbp' fact2.s` returns 1 and that 1 is the bomb's own comment string** — the bomb quotes the
phrase "`[rbp`-relative frame references" while diagnosing their absence. An unstripped count reads as
"promotion partially present" on the exact file whose diagnostic says it is absent. Strip comments first.

**Confirmed three independent ways, not one:**
- **.s census** — 0 rbp-relative instructions, above.
- **The refusal fires** — all three witnesses under `SCRIP_PL_GAMMA_RETAIN=1` die `rc=134` on the clause (c)
  bomb, whose standing half names host RBP promotion as the blocker. The scaffold still correctly refuses.
- **The source excludes Prolog by construction** — `x86_asm.h:952` `icn_gen_host_reserved()` opens
  `if (g_emit.zframe_graph) return 0;`, and `:889` states the promotion is *"never for a zframe_graph callee,
  which uses a wholly different storage protocol this row does not touch."* Prolog is not merely un-promoted,
  it is deliberately opted out of the only promotion that exists.

**Control arm — the default build is green on these shapes, so the wall is specific to the armed path:**

| witness | swipl | m3 default | m3 `SCRIP_PL_GAMMA_RETAIN=1` |
|---|---|---|---|
| `fact/1`, 3 clauses, `fail;true` | `a b c` rc=0 | `a b c` rc=0 ✅ | BOMB rc=134 |
| `fact/2`, 2 clauses | `a1 b2` rc=0 | `a1 b2` rc=0 ✅ | BOMB rc=134 |
| 8-line acceptance shape (var bound by user-pred call + one more goal, re-entered) | `1 2` rc=0 | `1 2` rc=0 ✅ | BOMB rc=134 |

## ⛔⛔ THE TRAP WAITING FOR THE NEXT IMPLEMENTER — `zframe_graph` IS NOT PROLOG

The promotion mechanism itself is small and well-precedented. Icon does it in **two leaf accessors**, both
keyed on one predicate that returns the α carve size or 0:

- `x86_asm.h:1003` — `x86_zop()`, the **FR family** (`FRQ`/`FR`): `{ int ft = icn_gen_zeta_ft(); if (ft > 0) return q ? RDQ("rbp", eff - ft) : RDD("rbp", eff - ft); }`
- `x86_asm.h:1020` — `x86_zref()`, the **SPINE family** (`ZRES`/`ZOPQ`): the same two lines.

⭐ hq_P's s276 note is the reason there are two and not one: *"generator ζ is split across TWO addressing
families that are INDISTINGUISHABLE in the emitted .s (both print `qword ptr [rsp + N]`)"* — re-homing only
one splits the frame across two bases. Any Prolog analogue inherits that requirement exactly.

⛔ **The obvious gate is wrong, and its name will not warn you.** `g_emit.zframe_graph` reads as "the Prolog
frame regime". It is set by **three** lowerers:

```
src/lower/lower_prolog.c:1514      <- (scrip.c:140 and this row's own baton still cite :1463 — stale)
src/lower/lower_raku.c:1141
src/lower/lower_pascal.c:790
```

A promotion keyed on `zframe_graph` silently re-homes **Pascal and Raku** frames too — including the Pascal
programs hq_P cured on the very row that unblocked this one (`pascal-m4-*`, sieve/bubble). That is seat02's
measured trap in a new costume: sharing Icon's regime key regressed prolog smoke 5/5 → 3/5 both modes, which
is why `icn_gen_regime()` exists as a language-specific key instead of the bare capability switch. The Prolog
promotion needs its **own** key, and `pl_cells_graph` is not a free substitute — it is gated on
`SCRIP_PL_CELLS`, default OFF (`lower_prolog.c:12`).

   ⛔⭐ **AND THE OBVIOUS KEY IS ILLEGAL, NOT MERELY WRONG — DO NOT REACH FOR `is_prolog`.**
   `test_gate_emit_no_lang.sh` is a BLOCKING gate and bans the identifiers `g_lang` / `LANG_` / `IR_LANG_` /
   `rt_set_lang` / **`is_<language>`** anywhere under `src/emitter` and `src/templates` — identifier-scoped, so
   a diagnostic string is fine but a live code reference is not. RULES.md line 86: the emitter is "past language
   and into PLATFORM" and may condition only on the IR graph and platform state. So the Prolog key must be a
   **behavioural description of the storage regime**, which is exactly what `pl_cells_graph`/`icn_cells_graph`
   already are and why they are spelled that way rather than as language names. Whatever key clause (a) needs,
   mint it as a regime predicate on that model — and run this gate before believing the arm exists.


⛔ **And the shared pin machinery this row's GOAL says to land through is currently inert for every language:**
`x86_asm.h:478` `x86_fb_pinned() { return 0; }` and `:484` `x86_fb() { return "rsp"; }` are unconditional
stubs. The GOAL's *"through the SHARED pin machinery (`emit_rec_pin`/`x86_fb`/adopt), not bespoke arms"* names
a hook that today can only answer rsp. A consequence worth its own look: `emit.cpp:2208`'s
`... && g_emit_cfg->icn_cells_graph && x86_fb_pinned()` is therefore a **dead condition**.

⚠️ **Parity is a real constraint on the naive `push rbp` — and it must be MEASURED, not derived.** What is
verified here: Prolog zframe α is `sub rsp, kt` with kt asserted 16-mult and **no push anywhere**, and
`bb_call_proc_staged.cpp:739,868` pad call sites (PL-CALL-ALIGN) against a measured 8-mod-16 hazard from a
lone 8B push. What is **NOT** verified and must not be inherited from this FINDING: the resting parity of a
zframe body. The obvious `call`-entry derivation (8-mod-16 in, 16-mult carve, 8-mod-16 body) does **not**
transfer, because mode-3 boxes are flat-wired **`jmp`** entries — PL-CALL-ALIGN's own comment says "into
open_det and the callee **jmp**" — so entry parity is whatever the caller left, not what a `call` guarantees.
Anyone adding a `push rbp` must measure both media first: it shifts every Prolog body by 8 and can convert
those pads from a cure into the misalignment they were added to fix. A base pinned **after** the carve (`rbp = rsp`, caller's rbp saved in-frame) keeps
parity and makes the rebase offset plain `off` rather than Icon's `off - ft` — but it needs a frame slot, and
the zframe header `[kt-24]=γ [kt-16]=ω [kt-8]=caller` is fully occupied.

## WHAT THIS DOES AND DOES NOT SAY

✅ `f9a90958` is sound, its measurements stand, and it genuinely unblocked the *arrival-depth* class.
⛔ It did **not** deliver a caller base for Prolog, which is the half PZ-4's clauses (c)/(d)/(e) each need.
⛔ PZ-4's DONE-WHEN is **not** reachable today; clauses (c)/(d)/(e)/(f) remain unwritten.
✅ The scaffold's refusal is **loud and correct** — the bomb is doing its job and must not be "cured" by
restoring rsp anyway, which trades it for hq_P's silent dead-stack write (18/21 kernels, `pl_trail_unwind`).

## THE GENERAL FORM

⭐⭐ **A dependency edge names a ROW; the thing you are waiting for is a MECHANISM. When the row lands
something else, the edge clears anyway and the prose naming the mechanism is not consulted by anything.**
This is the same shape as this rung's own N-2 pre-pass defect (an invariant asserted in a comment that nothing
read, falsified by a correct cure in another file) and hq_C's header-denominator class. The cheap guard is the
one this row already demonstrates: **re-measure the precondition, never inherit it** — the park recorded a
reproducible number (`0` rbp refs) precisely so the next seat could re-take it in one command instead of
trusting a state column. Re-taking it cost one `--compile`; trusting the queue would have cost a session.
