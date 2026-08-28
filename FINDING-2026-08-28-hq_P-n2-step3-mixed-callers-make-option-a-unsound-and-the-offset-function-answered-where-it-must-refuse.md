# N-2 step 3: mixed callers make the "scope it to flat_lcl_proc hosts" option UNSOUND, and the offset function was answering where it must refuse

**hq_P · 2026-08-28 (s282) · row `icon-n2-generator-activation-frames` · SCRIP `f5c2fd83` · MODE TRIO**

seat01 reached a real scope gap before writing the risky code and routed it for a ruling rather than deciding it
under time pressure. That was the right call and this FINDING is the ruling, plus a defect found while making it.

## 1. THE FORK AS ROUTED

`suspend_nested` (`outer()` calling `inner()`, both generators) has no reservation mechanism at all: the host
`outer()` is `flat_gen`, and `icn_gen_host_reserve()` is called **only** from the `flat_lcl_proc` prologue arm.
Two options were routed:

- **(a)** scope step 3 to `flat_lcl_proc`-hosted calls only — 4/5 D2 shapes; `suspend_nested` *"stays at baseline
  CRASH, unchanged, not worse"*, becoming its own follow-on row.
- **(b)** extend `icn_gen_host_reserve()` to the `flat_gen` arm first, so step 3 covers all five in one slice.

## 2. ⛔ (a) IS UNSOUND, AND THE REASON IS MEASURED, NOT ARGUED

**A generator's prologue is emitted ONCE per generator; the call sites are many.** Scoping the *call sites* therefore
does not scope the *prologue*. The failure needs a generator reached from both host kinds — so I built one:

```icon
procedure leaf()   suspend 1 | 2;   end
procedure mid()    suspend leaf();  end          # flat_gen host
procedure main()   every write(leaf()); every write(mid());  end   # flat_lcl_proc host
```

```
[N2-STEP3-DBG] callee=leaf host_flat_lcl_proc=0 off=0   base=128     <- from mid(),  a flat_gen host
[N2-STEP3-DBG] callee=leaf host_flat_lcl_proc=1 off=128 base=240     <- from main(), a flat_lcl_proc host
[N2-STEP3-DBG] callee=mid  host_flat_lcl_proc=1 off=0   base=240
```

One generator, one prologue, two incompatible call sites. Under (a) `leaf`'s prologue would be redirected to consume
a caller-supplied region while its `flat_gen`-hosted call site supplies none — **a wild rbp on a path that may
currently be correct.** That is not "unchanged, not worse"; it converts a contained crash into an unbounded wild
write, and it reaches generators that work today. Making (a) safe requires excluding every generator with a
non-reserving caller — i.e. the **reverse-callgraph query** ("given a generator, find all its callers") that seat01
correctly identified as absent. ⛔ **So (a) is not the cheap option: it needs strictly MORE machinery than (b).**

## 3. ✅ RULING: (b) — AND IT IS SMALLER THAN IT WAS FRAMED

Two structural facts, both verified in the tree:

- **The carve is the mirror of a change already landed and proven.** The `flat_gen` arm (`emit.cpp:2832`) carves
  `push rbp; mov rbp,rsp; sub rsp,frame_total` — the same shape as the `flat_lcl_proc` arm that step 2b already
  extended. Adding the reservation there is the sibling of a proven edit, not new ground.
- ⭐ **It needs NO release mirror, and the drift class is structurally absent.** The `flat_gen` retire epilogue
  (`emit.cpp:3318`) is `mov rsp,rbp; pop rbp` — **base-pointer-relative, size-independent.** The 240-vs-144
  carve/release drift that bit step 2b **cannot occur here**, because the release never references the size.

⭐ **A third option was considered and REJECTED, recorded so nobody re-derives it:** a universal 4-word protocol with
a `0` sentinel meaning "no region, self-carve", letting the prologue branch at runtime. It is sound and needs no
reverse query, but it buys nothing (b) does not — and it puts a test-and-branch in every generator activation on a
**speed** row, which (b) does not. Since (b)'s cost is one carve extension with no release mirror, the sentinel's
runtime cost is unjustified.

## 4. ⛔⛔ A DEFECT FOUND WHILE RULING — `icn_gen_host_reserve_offset()` ANSWERED WHERE IT MUST REFUSE (CURED)

The function's own comment promises *"-1 (never a guessed offset)"*. It was not keeping that promise: its scan of
`g_emit_cfg->all[]` is **host-kind-blind**, so a host that carved nothing still got an answer.

```
suspend_nested   callee=inner  host_flat_lcl_proc=0   off=0  base=128     <- BEFORE: nothing was ever reserved
mixed_caller     callee=leaf   host_flat_lcl_proc=0   off=0  base=128     <- BEFORE
```

⛔ **Zero is the most dangerous answer available here** — indistinguishable from a correct first-slot answer. A step-3
consumer would carve at `base+0` of a region that does not exist and corrupt the host frame, surfacing three layers
from the edit. **Third instance of the plausible-zero class on this rung** (step 1 `hosts=0`; step 1b `ft`
"obviously" 0, measured 96).

⚠️ **THE RECORD SAID THE OPPOSITE.** `LEDGER-seat01-2026-08-28-dedicated-sitting` states the function *"correctly
returns -1 for the `inner()` call site because nothing was ever reserved for it, not because the lookup is broken."*
**It does not, and did not.** The claim is retracted here; the refusal is now real. No blame attaches — it is the
same "described what the code was FOR, not what it DID" shape I logged against my own work three times this week.

**CURED** (`f5c2fd83`): `icn_gen_host_reserved()` mirrors the three-arm chain — `if (zframe_graph)` :2829 /
`else if (icn_genframe2() && flat_gen)` :2832 / `else if (flat_lcl_proc)` :2845. ⛔ **`flat_lcl_proc` alone is NOT
the predicate**: a graph can be `flat_gen` AND `flat_lcl_proc` at once (`emit.cpp:3535-3536`, under
`_gfr && icn_cells_graph`) and the `flat_gen` arm wins because it is tested first — so the naive predicate is wrong
for exactly the graphs this row is about.

⛔ **The predicate mirrors an else-if chain in another translation unit with no compiler check that it still does**,
so the canary ships with it: `scripts/test_icn_n2_host_reserved_agrees.sh`. Its witness set deliberately contains one
generator reached from **both** host kinds, and it **REFUSES `rc=2`** rather than passing when either host class is
absent — untested-where-it-matters is not a pass.

**PROVEN BEFORE TRUSTED:** `rc=2` with no `./scrip`; **`rc=1` against a rebuild with the refusal line disabled**,
catching both plausible-zero sites by name. **INERT:** `.s` byte-identical pre/post on all three witnesses including
the armed arm (the function has no emission consumer yet — a getenv diagnostic and the selftest).

## 5. ARMS (-O0, incremental — not a pristine gate verdict)

SNOBOL4 **m3 1299/1299 · m4 1299/1299 FAIL=0 SKIP=0 MISSING=0 rc=0** · `emit_no_lang` rc=0 · `template_medium` rc=0 ·
Icon smoke **m3 14/14 m4 14/14** · `n2_ft_formula` **1638/1638 AGREE** rc=0 · `n2_fb_prepass` **429/429 AGREE** rc=0 ·
**D2 OFF and ARMED both = pinned baseline at REPS=10**, m3=m4 throughout (OFF: 5 shapes CRASH 10/10, controls CORRECT;
ARMED: `suspend_single` WRONG crash 0/10, other four CRASH, controls CORRECT). Unmoved is the correct result for an
inert change. ⚠️ Armed `suspend_multi` m4 9/10 and `suspend_after` 9/10 / 8/10 are the known intermittency — s274
stands unretracted, and a REPS=5 comparison remains untrustworthy on this witness.

## 6. NEXT

Step 3 under ruling (b): extend the reservation to the `flat_gen` arm (no release mirror needed), then the fourth
pushed word at `[rbp+32]`, `+32`→`+40` at the landing **and its retire-arm mirror**, plus the per-callee partition of
`icn_gen_host_reserve()`'s sum. ⛔ Grep for `x86("lea", "rsp", RDQ("rax", 32))`, never a line number — it has already
moved once (`:733`→`:755`). ⛔ Never accept a REPS=5 comparison here, including your own.
