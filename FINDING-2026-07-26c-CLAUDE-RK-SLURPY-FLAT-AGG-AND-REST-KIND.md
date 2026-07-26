# FINDING — 2026-07-26c — Raku slurpy `*@r`: the tail flavour is `rest_kind`, and the m4 replay trap re-confirmed by negative control

**Session:** s2026-07-26c · GOAL-RAKU-BB · RAKU-100 arc · Claude Opus 5
**Commit:** SCRIP `e9a95691` · **Watermark:** m3 681→**695**/0, m4 681→**695**/0 (+14)
**Conflicts:** 93 s/r / 9 r/r — **zero delta**. Peers unchanged: Icon 14/14, SNOBOL4 7/7, Prolog 5/5/5, Rebus 4/4.

---

## PART 0 — WHAT THE PRIOR RECON GOT RIGHT (read this before doubting a recon doc)

`FINDING-2026-07-26b` Part 6 predicted this rung's entire shape: the two existing pieces, the one real decision,
and the canonical citations. **All three held.** The recon saved the whole investigation, exactly as its author
claimed it would. The lesson is not "recon docs are nice" — it is that a recon written at the moment the previous
rung's context is still hot is worth far more than the same investigation done cold, and it is cheap to write then.

---

## PART 1 — CANONICAL GROUNDING (read before designing)

- **`BOOTSTRAP.nqp:888-941`** — the slurpy arm collects all remaining positionals from `$cur_pos_arg` to
  `$num_pos_args`. **When none remain the `while` loop simply does not run**, so the bindee is an EMPTY array.
  Not `Any`, not a Failure. Smoke-locked in both directions (`f(1)` with `($a,*@r)` and `f()` with `(*@r)`).
- **`List.rakumod:271 from-slurpy-flat`** — flattens `Iterable` arguments (`.flat.Slip`) and binds
  non-Iterables as-is. **This is precisely what `__rk_arr`'s fold already did**: splitting every argument on
  `SOH` while concatenating IS the flattening, because a SCRIP Raku array IS a SOH-joined aggregate.
- `BOOTSTRAP.nqp:931-935` distinguishes the three slurpy flavours: `+@` → `from-slurpy-onearg`,
  `*@` → `from-slurpy-flat`, `**@` → `from-slurpy` (non-flattening). Only `*@` landed here; see Part 5.

---

## PART 2 — MEASURED BEFORE BUILDING (three measurements, each of which changed the plan)

1. **`sub f($a, *@r)` is a parse error** — confirms the gap is at the grammar, not the binder.
2. **Extra args to a fixed-arity sub are silently dropped** — no crash, so the args ARE reaching
   `g_call_args`; only the binding decision is missing.
3. **⭐ The variadic binder is LIVE — proven via Icon, not by reading code.** `procedure p(a, b[])` with
   `p(1,2,3)` gives `a`=1, `*b`=2, `!b`→2,3. That single 20-second test established that
   `rt_frame_bind_args` is the correct seam and that nothing in the transfer path needed building. **Prefer
   exercising a neighbouring language's working feature over tracing C to decide whether a seam is live.**

---

## PART 3 — THE ONE REAL DECISION: REPRESENTATION, NAMED BY WHAT DIFFERS

The existing arm builds `rt_make_list` (a `DT_DATA` list). Raku's `@a` is a SOH-joined string aggregate, so a
`rt_make_list` value would break `.elems`, subscripts, `[+]`, and `for`. The rung therefore needed a SECOND
tail flavour. Per the shared-helper FACT RULE it is named by **WHAT differs, never by language**:

```
rt_proc_t.rest_kind :  REST_LIST(0)      = DT_DATA list (rt_make_list)   -- Icon  procedure p(a, b[])
                       REST_FLAT_AGG(1)  = SOH-joined flat aggregate     -- canonical from-slurpy-flat
```

`rt_frame_bind_args` branches on it in one line. **`is_raku_variadic` was never written.**

**NO-DUP-LOGIC:** rather than writing a second SOH-join, `__rk_arr`'s fold was hoisted verbatim into
`rt_make_flat_agg` and `__rk_arr` collapsed to a two-line call. The flattening now exists exactly once and both
consumers share it; the 681 pre-existing smokes are the proof the hoist was behaviour-preserving.

⚠ **Placement gotcha:** `by_name_dispatch.c` has an `#undef SOH` at ~line 4177. A new SOH-using function
must live ABOVE it. The first cut landed below and failed to compile — a cheap, loud failure, but worth knowing.

---

## PART 4 — ⚠ THE M4 REPLAY TRAP, AND THE NEGATIVE CONTROL THAT PROVED IT

The prior session's generalizable lesson — **the mode-4 startup replay is an ALLOWLIST, not a snapshot of the
proc record, so m3 passing tells you NOTHING about m4** — applied verbatim. `rest_kind` needed its own emitter
beside `is_variadic` in `scrip.c`, plus the three in-process sites and the `runtime_eval.c` twin.

Because it was written in the same edit as the m3 path it never became a live bug. **It was therefore falsified
rather than assumed:**

```
$ grep -v rt_proc_set_rest_kind t3.s > t3_noreplay.s && gcc ... && ./t3_nr.bin
[GZ-10] rt_call_proc_descr: procedure 'list__elems' has no stackless slab
$ ./t3.bin
3
10 20 30
```

**Stripping one line from the generated `.s` breaks m4; the unmodified `.s` is correct.** That is the cheapest
possible proof that a replayed fact is load-bearing, and it costs about a minute. **Do this for every new
`rt_proc_set_*` fact** — it converts "I added the replay, it should be fine" into evidence.

**Gating improvement over the pname rung:** the emission is gated on **the fact itself** (`if (pe->rest_kind)`),
not on `is_raku`. Peers never set the fact, so they emit nothing and their `.s` is byte-identical **by
construction** rather than by a language test that has to be argued legal. Verified: 0 emissions for
Icon/SNOBOL4, and **25/25 committed SNOBOL4 `.s` artifacts recompile byte-identical** ⇒ no regen owed.
**Prefer fact-gating to language-gating whenever the fact is available at the emission site.**

---

## PART 5 — ONE MISSTEP, RECORDED (cost ~15 min)

The first cut put the slurpy detection in `lower_raku.c`'s `if (proc->t == TT_PROC_DECL)` block — which
contains a nested `if (proc->t == TT_SUB_DECL)` that **can never be true** and reads exactly like the right
home. Raku subs and methods both register through **`rk_register_proc` (`lower_raku.c:491`)**.

**The tell was clean and worth memorising:** the flag was silently 0, so `f(1,2,3)` against `($a,*@r)` gave
`@r`.elems = 1 with value `2` — i.e. the plain non-variadic path binding arg slot 2. Reproducing the *exact*
non-variadic arithmetic on three different inputs identified the cause before any debugger was opened.
**A per-proc fact that appears not to take effect: check WHICH registration site the language actually uses
before suspecting the runtime.**

---

## PART 6 — DEFERRED, WITH COST NAMED (not faked)

- **`**@r` (SLURPY_LOL, non-flattening)** — one lexer rule (`"**@"`) + a THIRD `rest_kind` value
  (`REST_NESTED`, canonical `from-slurpy` not `from-slurpy-flat`). **The plumbing built this session takes it
  directly; no redesign.** Cheapest next rung.
- **`*%h` (SLURPY_NAMED)** — needs the s2026-07-26b named-arg envelope to survive into the callee, so it pairs
  naturally with the still-open **named args to USER METHODS** (`meth_call` seam after MRO resolution).
- **`multi` + slurpy** — blocked in a NAMED way: `rk_multi_mangle` reads `p->c[0]->v.sval` as the parameter
  TYPE, and the slurpy marker IS a `TT_QLIT` child, so it would mangle as the type `*@`. **Fix = teach the
  mangler to skip the marker; do NOT move the marker**, since `lower_raku_proc`'s `__param_check` loop already
  ignores it correctly (it fails the `:D`/`:U`/modelled-type test and `continue`s).
- **Unspaced `*@` in expression position** (`$x *@a.elems`) is now a **parse error** — a loud failure, never a
  silent wrong answer. Every spaced form is unaffected; three multiplication regression locks were added. Same
  class as the `[*]` metaop vs `@a[*]` collision, and resolved the same way: one token, characterised.

---

## FILES TOUCHED (SCRIP `e9a95691`)

`src/parser/raku/raku.l` (+1) · `raku.y` (+token, +`rk_slurpy_param`, +2 productions) · regen
`.tab.c`/`.tab.h`/`.lex.c` · `src/lower/lower_raku.c` (+3 in `rk_register_proc`) ·
`src/runtime/by_name_dispatch.c` (+`rt_make_flat_agg`, `__rk_arr` collapsed onto it) · `src/runtime/rt/rt.c`
(+`rest_kind`, +`rt_proc_set_rest_kind`, binder branch) · `rt.h` · `src/contracts/stage2.h` ·
`src/runtime/runtime_eval.c` (m3 replay) · `src/driver/scrip.c` (3 in-process + 1 m4 emission) ·
`scripts/test_smoke_raku.sh` (+14).

**Zero emitter/template files in the diff** — which is also what proves the purity/concurrency baselines are
untouched. All builds `-O0` per the O0-DEV FACT RULE. Toolchain provenance (bison 3.8.2 / flex 2.6.4
reproducing the committed generated files byte-for-byte) established BEFORE the first grammar edit.
