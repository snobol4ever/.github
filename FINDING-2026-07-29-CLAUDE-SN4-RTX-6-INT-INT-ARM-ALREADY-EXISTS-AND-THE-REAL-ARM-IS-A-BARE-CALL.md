# FINDING-2026-07-29-CLAUDE-SN4-RTX-6-INT-INT-ARM-ALREADY-EXISTS-AND-THE-REAL-ARM-IS-A-BARE-CALL

**Session:** s206 · **Repo:** SCRIP @ `dcdb2e0c` (clean, main) · **Status:** MEASURED FROM SOURCE, NOT INFERRED. No code landed.

---

## ⭐⭐ THE FINDING

**RTX-6's remaining named target — "`rt_num_arith` int-int inline fast path" — IS ALREADY BUILT, AND THE
THING THAT IS ACTUALLY MISSING IS THE ARM THE INSTRUMENT MEASURES.**

`src/templates/bb_binop_arith.cpp` has four arms:

| Arm | Lines | Guard | Inline fast path |
|-----|-------|-------|------------------|
| 1 | 22–71 | `vfcb()` (FORTH value-spine) | ✅ int-int tag checks → `add`/`sub`/`imul` |
| 2 | 72–86 | **`_.op_num_real`** | ⛔ **NONE — bare `call rt_num_arith`** |
| 3 | 87–147 | `!op_num_real` ∧ ADD/SUB/MUL/DIV/MOD | ✅ int-int **+ compile-time immediate elision** |
| 4 | 148–164 | POW, CUNION/CDIFF/CINTER | none (correct — genuinely dynamic) |

**Arm 3 already IS the rung, and is strictly better than the rung's own spec.** Lines 92–107 each wrap
their tag check in `IF(!_.op_imm_a_ok, ...)` / `IF(!_.op_imm_b_ok, ...)`, so a statically-known operand
gets **no runtime tag check at all**. It inlines ADD/SUB/MUL/DIV/MOD. This is why s203 measured
`arith_loop` reaching `rt_num_arith` **zero** times — not because "the emitter inlines integer
arithmetic" as a vague property, but because *this specific arm* does it, here.

⇒ **PORTING AN INT-INT FAST PATH WOULD RE-BUILD ARM 3.**

## ⛔ NEW FAILURE-MODE MEMBER: THE PHANTOM RUNG

The phantom family so far has been about *symbols* — names that grep alive and `nm` dead. This is the
same shape one level up: **planned WORK that is already done.** Detection differs and is harder. A
phantom symbol is caught by `nm`. A phantom rung is caught only by reading the emitter arm that would
receive the port and finding the code already there.

⛔ **STANDING RULE (proposed): before porting a fast path, read the emitting template arm and confirm
the fast path is absent. "The runtime does X generically" does NOT imply "the emitter always calls it
generically" — SCRIP has per-arm emission and the arms disagree.**

## ⭐⭐ THE INVERSION — ARM 2 HAS MORE STATIC INFORMATION AND USES LESS OF IT

`op_num_real` is set at `emit.cpp:1201` from `binop_is_num_real(g_emit_cfg, nd)` — a **static** emitter
analysis. So on arm 2 the emitter has *proven reals are involved* and then emits:

```
mov rdi, FRQ(sa)      ; a.tag        <- statically known at the observed site
mov rsi, FRQ(sa+8)    ; a.payload
mov rdx, FRQ(sb)      ; b.tag
mov rcx, FRQ(sb+8)    ; b.payload
mov r8d, <op>         ; compile-time constant shipped as a runtime argument
call rt_num_arith@PLT
cmp  eax, 99          ; DT_FAIL
```

Arm 3, which has proven *nothing*, does more with it. **The arm holding the stronger proof is the arm
that discards it.**

Observed live in `test/snobol4/rung4/413_arith_mixed.s:96` (`n7_binop_α`). At that site `n4_lit_real_α`
stores tag `7` (`DT_R`) as an **immediate** twelve instructions earlier; arm 2 reloads it and ships it
to a callee that re-derives realness.

### What the generic callee then does per call (`arithmetic.c:207-264`)

1. `a.v == DT_I && b.v == DT_I` test — **fails every time on this path**, by construction.
2. `setjmp(g_core_errjmp_stk[my])` — **a full non-local-exit frame set up per arithmetic operation.**
   Int-int returns at :218 *before* this; the real path cannot.
3. `IS_REAL_fn` ×2 + `operand_is_real_str` ×2.
4. `:233-234` computes `ld/rd` **and** `li/ri` unconditionally — the int conversions are performed and
   then discarded on every real operation.
5. `switch (op)` on the argument that was a compile-time constant at the call site.

## ⛔⛔ THE INSTRUMENT AND THE PLANNED PORT WERE POINTING AT DIFFERENT ARMS

`corpus/benchmarks/snobol4/arith_mixed.sno` (RTX-0d, landed s204):

```
LOOP    X = X + 1.5                            <- X is DT_R, 1.5 is DT_R  => R+R, arm 2
    N = LT(N, 40000000) N + 1     :S(LOOP)     <- integer => arm 3, inlined, never reaches runtime
```

**All 40,000,001 calls are `DT_R + DT_R`. The int-int arm receives ZERO.**

⇒ RTX-0d succeeded exactly as designed (it made `rt_num_arith` reachable, and its scaling proof and
pre-predicted checksum both hold) **and in the same stroke made the planned port ungradeable.** Porting
int-int and grading it here is a guaranteed 1.000× — the RTX-0b/0c/0d false-null trap, recurring at the
level of *which arm* rather than *which symbol*.

⭐ **The corrected target needs no new instrument. `arith_mixed` already hammers arm 2 40M times in a
~1570ms window.** The instrument was right; the rung text was wrong.

---

## CORRECTED RUNG — RTX-6 (REMAINDER), RESTATED

**Give arm 2 an inline `DT_R`/`DT_R` SSE path.**

- Runtime predicate: **both tags `== DT_R`** → `movsd` / `addsd`|`subsd`|`mulsd` / store `DT_R` + result.
  No call, no `setjmp`, no switch.
- **ADD/SUB/MUL only.** Deliberate exclusions:
  - **DIV** — `arithmetic.c:239` returns `FAILDESCR` when `rd == 0.0` (SPITBOL manual p.20: `1.0 / 0`
    ⇒ Error #262, real overflow). Needs a zero-test branch; out-of-line for now.
  - **MOD** needs `fmod`; **POW** needs `pow`. Out-of-line.
  - This matches arm 1's own precedent, which inlines only ADD/SUB/MUL (`:39-41`).
- ⛔ **THE NARROW PREDICATE HOLDS UNCHANGED — BOTH-SAME-TAG ONLY.** A string that parses as a real IS a
  real operand (`operand_is_real_str`, `arithmetic.c:232`; manual p.20-21: `14 + '54'` ⇒ 68, blanks
  trimmed leading/trailing only, `14 + ''` ⇒ 14 via null-string→integer-0 at `:229-230`, `'A' + 1` ⇒
  Error #1). **Any string tag goes out-of-line unconditionally.** Misclassification does not crash; it
  silently changes results.
- Port arm 3's **immediate elision** (`op_imm_a_ok`/`op_imm_b_ok`) into arm 2 — an independent win in
  the same arm, and the observed site proves it applies.
- **Per-op RT entries** replace `rt_num_arith(a,b,op)` on the slow path — kills `mov r8d, imm` at every
  site plus the callee switch.
- **COERCE as its own IR/BB** (`IR_COERCE_NUMERIC` + `bb_coerce_numeric.cpp` both already exist; mirror
  `lower_icon.c:342-343`, which emits per arith operand and skips for literals). ⭐ **The payoff not
  previously written down: once the coerce node owns conversion failure and branches to the F-target
  itself, the arith node can DROP THE SETJMP BRACKET ENTIRELY.** That is a non-local-exit frame deleted
  from the hot path, not a micro-optimization.

### PRE-STATED BOARD (so that a null is informative)

**`arith_mixed`: 1.3–2.0×.** Basis: ~39 ns/call today (1570 ms / 40M) against ~4 SSE instructions.
Diluted by loop overhead, the `LT` test, and the assignment sharing the window.
⚠ Per s188's law, **call count does not predict benefit** — operand shape decides. A 1.0× result is an
answer about where the window actually goes, not a failed measurement.
⚠ Per s204's rule, grade with an **ISOLATION ARM**, not the `SCRIP_RTX_ARITH` family gate — that gate
also disables `rt_cmp_d` (landed s203), and the family gate's error has no known sign or bound.

---

## COLLATERAL — OWED EDITS

1. **`GOAL-SNOBOL4-RTX.md` s205 cursor**, RTX-6 remainder: retarget int-int → real-real arm 2. The
   int-int half should be **struck**, with arm 3 named as the reason.
2. **RTX-6 rung text (line 254)**: same correction.
3. ⚠ **`ARCH-SNOBOL4-RTX.md` and `RULES.md` DO NOT EXIST IN ANY CLONE** — `snobol4ever/.github`,
   `corpus`, and `SCRIP` all lack them, and `git log --all --diff-filter=D` across the three finds no
   deletion. They are cited as load-bearing throughout (ARCH §2 register table, ARCH §5 symbol rows,
   ARCH §7 the per-rung protocol "verbatim", RULES.md line 54 quoted by name in the s199 cursor).
   **Every rung claims to follow a protocol that is not in the tree.** Either they live in an unlisted
   repo/branch, or the protocol is being followed from memory across sessions.

## NOT CHASED

- `differ(3.0 / 2, 1.5)` emits a runtime binop rather than const-folding. Per s205 CORRECTION 2 the
  const-fold expression arm is OFF for SNOBOL4 by construction, so this is expected, and for a
  *benchmark* it is desirable — folding would destroy the instrument. **No defect. Do not "fix".**
- `cmp eax, 99` (DT_FAIL) at every arith site is genuine runtime failure-testing, not compile-time
  waste. It belongs to **RTX-11** (S/F in EFLAGS), not this rung.
- ⚠ **Sequencing is unresolved.** This rung touches `x86_asm.h` + `bb_*` and fires `.s` regen ×3.
  `R12-FREE-1` (`87a44f89`) and `Z4-5`/`Z4-6` landed within the last day, and `R12-FREE-1` explicitly
  reserves "post-RTX the top returns to r12". The concurrency warning is live. **Lon's call.**

---

# ADDENDUM — MEASURED THIS SESSION (build + run, not source reading)

## ✅ BUILD AND BASELINE REPRODUCED

`make scrip` clean from a fresh clone at `dcdb2e0c`. Toolchain gcc 13.3.0, **`nproc=1`** — the same
single-core box the s199 cursor flagged for measurement instability. **Any A/B here needs the R=5
interleaved-median harness; naive back-to-back pairs are known to fabricate numbers in BOTH directions
on this box (s200, four runs on `table_access`: 1.340 · 2.497 · 2.606 · 0.510, arms swapping rank).**

`arith_mixed` baseline: **`result: 60000001` — the pre-predicted checksum, matched exactly.**
Window **2553 ms** (doc records 1570 ms at F=1; this box is slower). Clears `MIN_MS=800` at F=1.

## ⭐⭐ THE CENSUS — THE FINDING IS NOW MEASURED, NOT INFERRED

LD_PRELOAD interposer on `rt_num_arith`, counting by operand tag pair (the s199 §7 step-0(d) technique):

```
total calls: 40000001
  R     + R     : 40000001
```

**40,000,001 calls. 100% `DT_R + DT_R`. The int-int arm receives ZERO — measured, not argued.**
The total matches RTX-0d's own recorded count exactly, confirming the interposer sees the real traffic.

⇒ **The int-int port would have graded 1.000× on this instrument. Confirmed by measurement.**

Static cross-check: `--compile` shows exactly **3** `rt_num_arith` sites for the program's 3 binops
(`X + 1.5`, `N + 1`, `T2 - T1`). Site 1 (`n8_binop_α`) is a **bare call, no guard, no inline path** —
arm 2. Sites 2 and 3 each carry `rt_binop_overload` + an `L(2)` slow label above them, i.e. they have
inline fast paths and take them at runtime. **The hot 40M site is the one arm with no fast path.**

## ⛔⛔ BLOCKER FOUND — THE ENCODER CANNOT SPELL THE FAST PATH

`src/templates/x86_asm.h` SSE support is a **stub**:
- `movsd` (`:1422-1425`) handles **only** the `f64:` immediate form → `x86_set_xmm0_double`.
  **Every other form returns an empty string** — i.e. it silently emits nothing.
- `movq xmm, r64` (`:1426-1429`) and `xorps xmm0, xmm0` (`:1421`) exist.
- ⛔ **`addsd` · `subsd` · `mulsd` · `divsd` · `ucomisd` · `cvtsi2sd` DO NOT EXIST.**

⇒ **The real-real fast path CANNOT be written template-only. It requires new encoders in `x86_asm.h`
— the exact file the RTX-11/12 concurrency warning names, where `R12-FREE-1` (`87a44f89`) landed
hours ago.** The sequencing question is therefore not avoidable by clever scoping. **It is Lon's call
and it is now load-bearing, not precautionary.**

⚠ `MEDIUM_BINARY` (`:1447`) means every encoder must emit **both** a text mnemonic and correct raw
bytes — `--run` JITs into a sealed slab. A wrong byte does not fail loudly; it produces the wild-jump
class Z4-6 documented in `fib`.

## ✅ GROUND-TRUTH BYTE ENCODINGS — VERIFIED VIA gas + objdump, NOT HAND-DERIVED

⭐ **THE FRAME BASE CHANGES THE ENCODING, NOT JUST THE OPERAND.** `[rsp+off]` requires a SIB byte
(`44 24`); `[rbp+off]` does not (`45`). Per s205 CORRECTION 1 the base is **per-graph**
(`x86_fb_pinned()` → rbp for suspended generators / pattern blobs / deep-arrival graphs, rsp for
depth-static determinate graphs). **Hand-spelling rsp bytes would silently corrupt every rbp-based
graph.** New encoders MUST reuse the existing modrm/SIB machinery, not hand-roll.

⚠ Real emitted frame offsets observed are **240–456**, so **disp32 is the common case, not disp8.**

| form | disp8 | disp32 |
|------|-------|--------|
| `movsd xmm0, [rsp+off]` | `f2 0f 10 44 24 <d8>` | `f2 0f 10 84 24 <d32>` |
| `movsd xmm1, [rsp+off]` | `f2 0f 10 4c 24 <d8>` | `f2 0f 10 8c 24 <d32>` |
| `movsd [rsp+off], xmm0` | `f2 0f 11 44 24 <d8>` | `f2 0f 11 84 24 <d32>` |
| `movsd xmm0, [rbp+off]` | `f2 0f 10 45 <d8>` | `f2 0f 10 85 <d32>` |
| `movsd [rbp+off], xmm0` | `f2 0f 11 45 <d8>` | `f2 0f 11 85 <d32>` |
| `addsd xmm0, xmm1` | `f2 0f 58 c1` | — |
| `subsd xmm0, xmm1` | `f2 0f 5c c1` | — |
| `mulsd xmm0, xmm1` | `f2 0f 59 c1` | — |
| `ucomisd xmm0, xmm1` | `66 0f 2e c1` | — |

## ⭐ CORRECTION TO THIS DOC'S OWN EARLIER DRAFT

An earlier note in this session claimed the only constants in play were 6/7/99 and that no `100`
appeared. **That was wrong, and it was wrong because it read the emitted `.s` instead of the
template.** `DT_DATA = 100` (`descr.h:23`) is the overload guard at `bb_binop_arith.cpp:26,29,94,98`,
routing to `rt_binop_overload`. ⚠ **In arms 1 and 3 the DT_DATA guard is elided for compile-time
immediates (`IF(!_.op_imm_a_ok, ...)`); arm 2 has NO DT_DATA guard at all**, so arm 2 cannot dispatch
an overload. Whether `binop_is_num_real()` can ever be true for a DT_DATA operand is **unverified** —
if it can, that is a live correctness hole independent of performance. **Not chased; needs the monitor.**

## NEXT STEP — EXACT, ORDERED

1. **Get Lon's sequencing ruling.** `x86_asm.h` is unavoidable (proven above), `R12-FREE-1` is hours old.
2. Add SSE encoders reusing existing modrm/SIB machinery; **both media**; byte-verify each against the
   table above (regenerate with gas rather than trusting the table).
3. Arm 2 (`bb_binop_arith.cpp:72-86`) gains: both-tags-`DT_R` guard → `movsd`/`addsd`|`subsd`|`mulsd`/
   store → `x86_gamma()`. Slow path unchanged initially.
   ⛔ ADD/SUB/MUL only. ⛔ Both-same-tag only; any string tag goes out-of-line (`'1.5'` is a real
   operand — manual p.20-21, `operand_is_real_str`).
4. Gates: crosscheck watermark **re-proven live before any edit**, kill-switch md5, unit/alloc/STR.
5. Two-sided falsification. ⚠ If probe 1 is silent, ESCALATE — s204's rule.
6. **ISOLATION arm, not the `SCRIP_RTX_ARITH` family gate** (which also disables `rt_cmp_d`).
   R=5 interleaved, discard round 1. Board pre-stated: **1.3–2.0× on `arith_mixed`**.

---

# RTX-6r — IMPLEMENTED AND MEASURED (s206, local only, NOT pushed)

## ✅ WHAT LANDED (working tree, `git diff --stat`: 2 files, +57)

**`x86_asm.h`** — two encoders, byte-verified against gas/objdump, not hand-derived:
`x86_movq_r64_xmm()` (XMM→GP, `66 REX 0F 7E modrm`) and `x86_sse_arith()`
(`addsd`/`subsd`/`mulsd`, fixed `F2 0F 58|5C|59 C1`). Wired into the `x86()` mnemonic dispatch.

⭐ **THE MEMORY-OPERAND FORM WAS DELIBERATELY NOT ADDED.** SSE `[base+disp]` encodings differ by base
(`[rsp+off]` needs SIB `44 24`/`84 24`; `[rbp+off]` does not, `45`/`85`) and the frame base is
**per-graph** (s205 CORRECTION 1). Operands therefore travel through GP regs via existing proven `mov`
encoders, leaving only fixed 4-byte reg-reg forms new. **This is what kept the change off the
addressing-mode machinery entirely** — the one place a wrong byte fails silently as a wild jump.

**`bb_binop_arith.cpp` arm 2** — both-tags-`DT_R` guard → `movq`/`addsd|subsd|mulsd`/`movq` → store
`DT_R`. ADD/SUB/MUL only (`rfast()`); DIV/MOD/POW unchanged and still out-of-line.

## ✅ EXECUTION PROVEN BY COUNT, NOT BY TIMING

| | before | after |
|---|---|---|
| `rt_num_arith` calls | **40,000,001** (100% R+R) | **0** |
| checksum | 60000001 | **60000001** |

**An exact count going to zero is stronger than a corruption probe** — the calls are gone AND the
answer is still the pre-predicted one, so the inline path both fires and computes correctly. Verified
in the **JIT/binary medium** (`--run`, default), not only the text medium.

## ✅ CORRECTNESS GATE — WATERMARK NEUTRAL, BASELINE RE-PROVEN ON THIS BOX

Baseline established by `git stash` + full rebuild + same harness, **not** quoted from the doc
(the doc's 268/47 is a different corpus total — 334 here):

```
            ON  : m3 PASS=280 FAIL=54 · m4 PASS=276 FAIL=50 SKIP=8  (334)
            OFF : m3 PASS=280 FAIL=54 · m4 PASS=276 FAIL=50 SKIP=8  (334)
```

**IDENTICAL. Zero movers.** The 54/50 failures are pre-existing (pattern family: `pat_cap_reyield`,
`arbno_defer`, `seq`/`alt`/`tab` W-series) and present in both arms.

## ⚠ PERF — PREDICTION FALSIFIED, IN THE FAVOURABLE DIRECTION

Interleaved A/B, both binaries retained and alternated **within** each round, round 1 discarded:

```
round 1  OFF=2443  ON=810   (discarded — warmup)
round 2  OFF=2688  ON=931
round 3  OFF=2454  ON=763
round 4  OFF=2560  ON=772
round 5  OFF=2526  ON=825
        OFF median 2543 ms · ON median 798 ms  =>  3.19x
```

Arms never swap rank. **Pre-stated board was 1.3–2.0×; measured 3.19×. THE PREDICTION IS FALSIFIED —
IT WAS UNDERSTATED.** Stating this rather than quietly claiming a win: the board was written down
first precisely so a miss in either direction would be informative.

⛔⛔ **THE RATIO IS AGAINST AN `-O0` RUNTIME AND MUST NEVER BE QUOTED WITHOUT THAT CLAUSE.**
`RT_OPT` defaults to `-O0` (Makefile FACT RULE O0-DEV s119; `-O2` is explicit opt-in). The deleted work
— PLT call, `setjmp` bracket, `switch`, and `arithmetic.c:233-234`'s unconditional `to_int` conversions
computed and discarded on every real op — is all C, so **an `-O2` baseline will shrink this number.**
**The `-O2` arm is the next measurement owed. Until it is run, 3.19× is an `-O0` figure only.**

## ⛔ STILL OWED BEFORE THIS CAN LAND

1. **`-O2` baseline re-measure** (above). The headline is provisional without it.
2. **Falsification probe on the arithmetic itself** — swap `addsd`→`subsd` and confirm the checksum
   breaks. Not run (session budget). The 40M→0 census + correct checksum already prove fire-and-correct,
   but the house rule is that an instrument is trusted only after being falsified.
3. **No gate.** This is an unconditional template edit, not a `SCRIP_RTX_*`-gated port. A/B was done by
   retaining both binaries. If the ladder wants a kill-switch, it needs one.
4. **Sequencing / `x86_asm.h`** — still Lon's. Local clone, nothing pushed, `main` untouched.
5. Broader corpus: only the SNOBOL4 gate was run. Icon/Prolog/Pascal share `x86_asm.h`; the dispatch
   additions are new mnemonics only (no existing path altered), but **that is an argument, not a gate.**
