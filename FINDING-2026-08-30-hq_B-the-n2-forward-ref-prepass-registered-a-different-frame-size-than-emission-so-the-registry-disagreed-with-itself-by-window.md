# FINDING 2026-08-30 hq_B — the N-2 forward-ref pre-pass registered a different frame size than emission, so the registry disagreed with itself by window

**Seat:** hq_B (HQ-BEAUTIFY) · **Mode:** TRIO · **Row:** `prolog-pz4-gamma-retain-activation-frames` (sixteenth pass)
**Receipts:** SCRIP `3418a610` (pre-pass zframe arm + comment correction) · SCRIP `4886b326` (clause (c) bomb re-diagnosed)
⚠️ `4886b326`'s own message cites the pre-pass commit as `8718ea69` — that was its pre-rebase hash. The pushed
hash is **`3418a610`**. History rewrite is forbidden, so the message stands as written and this line is the mapping.

## 1. THE DEFECT: ONE REGISTRY, TWO WRITERS, TWO DIFFERENT ANSWERS

`emit_patzeta_frame_reserve()` answers "how many bytes is this callee's frame?" over the `pz[]` registry. **Two
different code paths write that registry**, and after a cure landed in one of them on 2026-08-30 they stopped agreeing:

| writer | where | fp term it registered |
|---|---|---|
| per-emission | `emit.cpp:3639` (`g_last_flat_fp`) | `zframe ? 0 : …` — **cured in SCRIP `3fe34608`** |
| forward-ref pre-pass | `scrip.c` `n2_fb_prepass_register()` | `(np+nl)*16` **unconditionally** — still Icon-shaped |

`lower_prolog.c:1463` marks **every** Prolog graph `zframe_graph`, and the pre-pass registers every `is_generator`
proc — so every Prolog predicate was registered through the un-cured writer.

**MEASURED, `fact/2` (np=2 nl=4), pristine -O0:**

```
[N2-PREPASS] proc=fact/2  np=2 nl=4 zframeA=1 icncells=0 rg=1184 fp=96 ft=1328     <- pre-pass
[N2-FT] EMIT  gen=1 zframeA=1 icncells=0 region=1184 ffb=1232 np=2 nl=4 ft=1232    <- per-emission
FN__fact$2F2:  sub  rsp, 1232                                                       <- what the callee ACTUALLY carves
```

Over by exactly **96 == (np+nl)*16**. After the cure all three read **1232**.

⭐ **THE HAZARD IS THAT IT WAS WINDOW-DEPENDENT, NOT THAT IT WAS WRONG.** A host emitted *after* its callee read the
corrected 1232; a host emitted *before* it — the forward reference this pre-pass exists to serve — read 1328. The same
callee had two different sizes depending on emission order, and neither reading announces which one you got.

## 2. THE COMMENT THAT ASSERTED THE INVARIANT, AND WHY NOTHING CAUGHT IT

The pre-pass carried, in its own header: *"the two calls agree once real emission reaches this proc and re-registers
it … so a pre-pass value is never stale, only ever superseded by an identical one."*

**That was true when written and went false under a cure landed in a different file.** Both commits were correct in
their own file. The invariant spanned two files, **nothing read it**, and it decayed silently in the gap between them.

⭐ This is hq_C's class from the other side. Their eight false greens each declared a denominator in a header comment
no code read (`# Gate: PASS=5 FAIL=0`). This one declared a *cross-file invariant* no code read. **A declared
expectation nothing reads is a comment, not a gate** — and a comment cannot notice that the code it describes moved.
Cured by making `SCRIP_N2_FT_PROBE=1` print **both sides** (`[N2-PREPASS]` and `[N2-FT] EMIT`), so a future
divergence is one run rather than a re-derivation.

⛔ The `_zfA` key is the α-SELECTION STATE (`zframe_graph && !icn_cells_graph`), never the bare field: a both-flags
graph takes an `icn_cells` α that DOES add the term back, so keying on the field alone registers a frame **silently
too small** — the silent-overflow direction ceo refused worst-case reservation over.

## 3. THE CURE UNBLOCKS PZ-4 CLAUSE (c)'s ARITHMETIC — AND EXPOSES THE REAL BLOCKER

The clause (c) landing bomb refused on precisely this arithmetic. It is now cured on both windows, so
`rsp = rax + emit_patzeta_frame_reserve(callee)` **is** the correct restore. The mechanism, read out of the emitted
`.s` rather than inferred: the callee's γ-retain epilogue does `mov rax, rsp` with **no** `add rsp, kt`, so
`rax = E − kt` and `E = rax + kt`; `kt == flat_frame_bytes == 1232 ==` the registry value.

⛔ **I DID NOT LAND IT, AND THE REASON IS A SECOND BLOCKER THAT THE FIRST ONE WAS HIDING.** Restoring rsp to `rax+ft`
puts rsp back **above** the retained frame, leaving that frame below rsp and unprotected against the next call.
hq_P measured exactly that class the same day: 18 of 21 van Roy kernels, first invalid access at `pl_trail_unwind`
(`src/parsers/prolog/pl_cell.h:81`), dead-stack writes 1672/1680 bytes below rsp (FINDING `3b349119`).

ceo's ruling on this row already names the missing half — *"once host ζ is rbp-relative, rsp may sit below the
retained frame and the landing protects it"*. **MEASURED at HEAD, not assumed:** a `--compile` of two-clause `fact/2`
under `SCRIP_PL_GAMMA_RETAIN=1` emits **zero** `[rbp`-relative frame references and six `qword ptr [rsp + 320]`.
The caller's whole ζ is rsp-relative, so **there is no base to re-anchor off**. Host RBP promotion for Prolog is the
prerequisite; then the landing is two instructions.

⭐ **A BOMB WHOSE STATED CAUSE HAS BEEN FIXED IS THE STALE-COMMENT CLASS WEARING A DIAGNOSTIC'S CLOTHES** — the next
reader clears the named blocker, deletes the bomb, and lands a silent corruption. The bomb text now names the cured
half as cured and the standing half as standing.

## 4. CONTROL ARMS — BOTH HALVES PRESENT

- Emitted `.s` **byte-identical** across the registry cure **while the probe moved 1328 → 1232**. The moving probe
  proves the two builds genuinely differ, so the identical `.s` is real inertness and not hq_C's s280 no-op-stash trap.
- All three owed `.s` regens (`benchmark`, `demo`, `prolog_bench`) were **no-ops** — independent confirmation across
  three corpora that codegen did not move.
- Default-path `.s` byte-identical across the bomb-text commit (armed path is default-OFF).

**Verdict scope, pristine -O0, run against the FINAL source:** SNOBOL4 `GATE OK` m3 PASS=1672 FAIL=0 · m4 PASS=1672
FAIL=0 · SKIP=0 · MISSING=0 · icon smoke 14/14 both modes (watermark unmoved) · prolog smoke 5/5 m2/m3/m4 · snobol4
smoke 7/7 · rung13 1/4 · rung14 3/2 · rung15 3/2 — **every Prolog arm identical to the baseline measured BEFORE
touching source** (hq_C's PROCEED condition 3) · all three blocking gates green.

## 5. THE SHAPE FOR THE POOL

**AN INVARIANT THAT SPANS TWO FILES DECAYS IN THE GAP BETWEEN THEM, AND BOTH COMMITS LOOK CORRECT LOCALLY.** The
per-emission cure was right. The pre-pass was right when written. Neither author could see the break from inside
their own file, and the prose asserting the link was not executable. The durable cure is not a better comment —
it is **making both sides printable from one command**, so the check costs a run instead of a re-derivation.
