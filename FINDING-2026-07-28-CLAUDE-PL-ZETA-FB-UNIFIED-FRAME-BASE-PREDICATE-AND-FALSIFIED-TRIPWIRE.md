# FINDING 2026-07-28 (s160) — ζ FRAME-BASE: THE TWO PREDICATES ARE NOW ONE, AND THE SEAM WAS REACHABLE BY CONSTRUCTION

**SCRIP watermark:** baseline `56cc4f09` → this work (local commit, see LIVE CURSOR).
**Level:** `-O0` throughout, full-clean. No `-O2` used or sought.
**Rungs:** ZETA-FB-1 (divergence instrument + tripwire gate) · ZETA-FB-2 (unification) · suite mode-count correction.

---

## 0. The one-line result

The ζ frame base was chosen by TWO predicates where the prologue establishes it in TWO arms whose
union is a THIRD thing. ZETA-FB-2 makes the data-reference selector name exactly that union, so the
base a reference NAMES, the base the record protocol NAMES, and the base the prologue ESTABLISHES are
now one decision. **Measured byte-identical on 267 `.s` artifacts across three frontends; suite
164/164 both modes; the new gate is falsified (it fires on an injected defect and the injected build
drops to 107/164 with a segfault).**

---

## 1. What the seam actually was — and why "measured non-divergent" was not safety

s159 banked the split and correctly refused to unify blind. Its evidence was that member/2's emitted
asm was coherent. That is evidence about ONE graph, and the reason it was coherent is that for that
graph both predicates happened to be true. It says nothing about whether a graph exists where they
differ.

The gap is not hypothetical — it is **reachable by construction**, and the construction is two lines
apart in the source:

| symbol | definition | site |
|---|---|---|
| `flat_gen` | `is_generator && emit_graph_has_suspend(g)` | `emit.cpp:2399` |
| `g_gen_proc_active` | `is_generator` | `scrip.c:880` |

So `flat_gen ⟹ g_gen_proc_active` but **not** the converse, and the residue is exactly
**`is_generator && !has_suspend`** — a SUSPEND-FREE GENERATOR GRAPH. `emit.cpp:2399`'s own comment
names that class as real and says who mints it: *"lower_prolog sets is_generator=1 on suspend-free
graphs."*

For such a graph, before ZETA-FB-2:
- the prologue took `xa_flat.cpp:281`'s **heap-frame adopt** — `push rbp; mov rbp,rdi` — gated on
  `g_gen_proc_active || g_resumable_callable_active`, carving **no rsp frame at all**;
- every data reference spelled **rsp**, because `x86_fb_pinned()` read only `emit_jmp_pin_rbp()`.

That is the s158 land mine verbatim: the prologue establishes rbp, the data plane reads rsp.

⭐ **THE GENERAL LESSON.** s158 fixed the *record protocol* by widening its predicate and left the
*data plane* on the narrow one. s159 saw the split and banked it. Neither was wrong, but the framing
"two predicates that should be one" understates it: there were **three** consumers (prologue, data
refs, record protocol) and **two** predicates, so one consumer was always going to be mismatched. The
question to ask of a gated pair is never "do these two agree today" but **"how many places consume
this decision, and do they all read the same expression?"**

---

## 2. ZETA-FB-1 — the instrument, and why it is hooked where it is

`emit_fb_divergence_check()` (`emit.cpp`, file-static counter, `SCRIP_FB_DIVERGE=1` to report) is
called from `emit.cpp` immediately after `g_resumable_callable_active` is computed and immediately
before `xa_dispatch(XA_FLAT_PROLOGUE)`. That is the **last instant at which every input to both
predicates is final for this graph and the prologue has not yet run** — i.e. the exact frame in which
"what will be established" and "what will be named" are both knowable and neither has happened.

It is emit-time only and reports nothing unless asked, so it is not a `g_*` runtime structure and
does not touch the DESIGN §10 list. `test_gate_pl_no_new_global.sh` PASSes (14 / floor 14).

`scripts/test_gate_fb_predicate_tripwire.sh` sweeps four language corpora and reports every graph
where the wide predicate exceeds the narrow one.

**Measured: 1911 programs swept, 0 hits.** The reachable class is, today, empty.

---

## 3. ZETA-FB-2 — the unification, and why it is NOT the change s158 rejected

`x86_fb_pinned()` now returns `emit_rec_pin()` instead of `emit_jmp_pin_rbp()`.

s158 recorded "MEASURED AND REJECTED — DO NOT RETRY BLIND" against making `x86_fb()` pin-aware, and
that record is **correct for the tree it was measured on**: the FR/FRQ offsets still carried s188's
rsp-relative `op_flat_disp` compensation, so rebasing the register double-counted the depth. What
changed is not the reasoning but the substrate — **FLATDISP-8 gated the compensation**
(`x86_frame_off()` = `pinned ? off : off + op_flat_disp`), so under a pinned base the compensation is
identically zero and the union no longer double-counts.

This is the s159 rule applied to itself: *a "MEASURED AND REJECTED" claim must carry the SHA it was
measured on, because it silently expires when the substrate moves.* s158's claim expired at
FLATDISP-8. It was retired here **by re-measurement, not by argument.**

---

## 4. Evidence

**Byte-identity (the strongest available claim — the change is provably neutral on everything
currently exercised):** 267 `.s` artifacts regenerated across Prolog / Icon / SNOBOL4,
**267 byte-identical, 1 excluded** — see §6.

**Gates, after (all full-clean `-O0`):**

| gate | result |
|---|---|
| Prolog rung suite `interp` | **164 / 164** FAIL=0 |
| Prolog rung suite `compile` | **164 / 164** FAIL=0 |
| `test_smoke_icon.sh` | 14/14 m3 · 14/14 m4 |
| `test_smoke_compile_hello_all_langs.sh` | PASS=6 FAIL=0 ROWS_DRIFT=0 |
| `test_gate_emit_no_lang.sh` | OK (lang-blind) |
| `test_gate_pl_no_new_global.sh` | PASS · ratchet 14 / floor 14 |
| `test_gate_fb_predicate_tripwire.sh` | PASS · 1911 programs · 0 hits |
| `test_gate_template_medium_invisible.sh --strict` | FAIL `xa_flat.cpp(106)` — **pre-existing WIP baseline, count unchanged**, owned by XA-FLAT-CONVERT |

---

## 5. ⭐⭐ THE GATE IS FALSIFIED — a gate that cannot fail is not a gate

A passing gate proves nothing until it has been shown to fail on the defect it claims to catch. Two
injections into `emit_jmp_pin_rbp()`, each built and measured:

| injection | tripwire | suite (interp) | notes |
|---|---|---|---|
| *(none — HEAD)* | 0 hits | **164 / 164** | healthy |
| drop `flat_gen` conjunct | **0 hits** | — | ⚠ **INSUFFICIENT** — those graphs also carry `flat_deep_arrival=1`, so the narrow predicate stayed true and no gap opened. A negative result from a probe that does not reach the class is not evidence. |
| `return 0` | **FIRES** — `data_fb=rsp rec_fb=rbp deep=1 gen=1 genproc=1` | **107 / 164** FAIL=57 + SIGSEGV | the s158 signature exactly |

The middle row is the useful one and it was **my own error, caught by continuing rather than by
stopping at a green result**: the first falsification attempt reported 0 hits and I nearly read that
as "gate works, class empty," when it actually meant "probe never entered the class." **A tripwire
that reports 0 is indistinguishable from a tripwire that is not wired, until you make it fire.**

The third row also independently corroborates the s157/s158 diagnosis: breaking exactly this
predicate reproduces a 57-test failure of exactly that character (s157 saw 116/164, s158 120/164).

---

## 6. Banked defects

**(NEW) `corpus/programs/snobol4/parser/unary_not.sno` emits a `.string` from uninitialised memory.**
Two compiles **by the same binary** differ: `.S0: .string "t\242A>"` vs `.string ":pd-"`. Pre-existing
and unrelated to this rung, but it has an instrument consequence beyond its own wrongness: **it is a
false-positive source for every `.s` byte-identity sweep**, so any future sweep must either exclude it
or re-run to distinguish nondeterminism from a real diff. It was found only because ZETA-FB-2's
byte-identity claim required explaining all 268 files rather than most of them.

**(CORRECTED INSTRUMENT) the suite's mode count was lying and now does not.** `run_prog`'s `interp`
and `run` arms are the identical command (`$SCRIP --run`); SCRIP has had exactly two modes since 1
and 2 were deleted. The `all` sweep ran `interp run compile` and reported three. It now runs the two
distinct paths; `run` remains an accepted explicit alias. **Every "164/164 ×3 modes" in this goal
file's history was really ×2** — the ratchet floor is unaffected, but the coverage claim was inflated.

**(CARRIED, +0)** predicate-divergence seam — **CLOSED by this rung**, tripwire standing ·
engine-wide silent-fail on undefined predicates · int/float standard-order conflation (two-oracle) ·
lexer escape three-site/two-behaviour · NO-LCO segfault · nested-`\+` binding leak · retractall/1 gaps.

---

## 7. Also true at HEAD, contradicting the s159 NEXT list

s159 named the Makefile as "the TOP blocker, two sessions running have paid full-clean cost for it."
**It is already fixed at HEAD** (`-MMD -MP` + `-include $(shell find …)` + `clean: rm -rf $(OBJ) out
scrip`), landed by a parallel session. Same shape as the s159 convergence finding: a blocker recorded
in one session's cursor was cleared in another's, and only a live check tells you which. **Check the
tree before working a cursor's NEXT item.**

---

## 8. Next

1. **The `xa_flat.cpp:281` adopt arm and `emit_jmp_pin_rbp` still gate on different expressions** —
   ZETA-FB-2 unified the CONSUMERS; the two prologue arms remain separately gated. They currently
   union correctly, but that is the same shape of latent split, one level down. Consider routing
   line 281's condition through a named predicate so the union is written once.
2. Retire the `interp` label itself (it names a deleted mode-2 interpreter) — deferred, since the
   HARD-GATE semantics and every historical cursor reference hang off that string.
3. `xa_flat.cpp(106)` medium-invisible residue — owned by XA-FLAT-CONVERT, untouched here.
4. Then LADDER A features or the PL-SPEED ladder; ζ storage no longer blocks either.
