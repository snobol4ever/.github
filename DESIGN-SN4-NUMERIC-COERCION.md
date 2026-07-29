# DESIGN-SN4-NUMERIC-COERCION.md — Hoisting Coercion Out Of Arithmetic, And The DT_t Bit Layout

**Drafted s211 (2026-07-29, Claude + Lon). Design only — nothing landed, nothing measured beyond what is
explicitly labelled MEASURED below.** Companion to `ARCH-SNOBOL4-RTX.md` (§5 ARITH row, §7 protocol) and
`GOAL-SNOBOL4-RTX.md` (RTX-6 residual).

---

## 0. THE HEADLINE, STATED BEFORE THE DESIGN SO IT CANNOT BE MISREAD

**This is an ENABLING / STRUCTURAL rung, not a speed rung.** The coercion hoist does not delete work — it
MOVES work out of the binop and into a node that runs once per operand-edge. Its payoff is that it lets the
arithmetic BB drop `setjmp`, which is what unblocks the DIV/MOD/POW ports that RTX-6 deliberately refused.

⛔ **DO NOT quote a speed number for the hoist itself until one is measured on a program that exercises the
path.** The ladder has nine recorded phantom shapes and s209/s210 spent two whole sessions discovering that
its instruments lie. The prior on "restructuring rung reports a large win" is bad.

⭐ **AND THE HOT PATH NEEDS NO RENUMBERING — THE BIT TRICK ALREADY EXISTS IN THE CURRENT TAGS.** See §3.
This is the single most consequential finding in this document and it argues AGAINST the larger half of the
proposal.

---

## 1. WHAT IS IN THE TREE TODAY (MEASURED, not inherited from prose)

| Fact | Source |
|---|---|
| `IR_COERCE_NUMERIC` EXISTS, with the joint-decision contract already written | `src/contracts/IR.h:96` |
| Its comment already states the rule: *operands[0]=self [1]=other; either real → both real* | same |
| It has a live BB template | `src/templates/bb_coerce_numeric.cpp` |
| Siblings exist: `IR_COERCE_STRING` / `_INTEGER` / `_REAL` + templates | `IR.h:94-97`, `src/templates/` |
| ⛔ **It is wired ONLY into the relop/predicate path — NOT arithmetic** | `lower_snobol4.c:168-169` |
| `IR_COERCE_INTEGER` is wired into builtin prototype args only | `lower_snobol4.c:1773, 2146` |
| Arithmetic entries pay: int-int inline test → `DT_DATA` overload test → **`setjmp`** → impl | `arithmetic.c:228-240` |
| The C conversion core already exists and is correct | `rt_coerce_num2_d`, `operand_is_real_str` (`arithmetic.c:199`) |

**⇒ The gap is exactly one edge.** The coercion node, its template, its runtime, and its joint-decision
contract are all built. Nothing routes arithmetic operands through it. This is a WIRING rung, not a
construction rung — which is a much cheaper and much lower-risk shape than the ladder usually gets.

⚠ **STEP 0(e) NOTE, per ARCH §7:** this document's claim "COERCE_NUMERIC exists and is unwired" was taken
from the tree (`grep` of `IR.h` + `lower_snobol4.c` + `ls src/templates/`), not from a ladder rung's prose.
The next session must still re-verify before coding — `IR.h` comments are prose too.

---

## 2. THE SEMANTIC CONTRACT (SPITBOL manual, read this session per Lon's standing directive)

1. **Joint-real rule.** *"If both operands are integers, the result will be an integer. If either operand is
   real, the result will be real."* (Ch. 2, operators)
2. **String operands are numeric operands.** *"If the operand is a string, SPITBOL will try to convert it to
   a number. The null string is converted to integer 0."*
3. **Blanks are legal.** *"SPITBOL permits leading and trailing blanks on numeric strings which are converted
   to integer or real numbers."* — already honored by `operand_is_real_str`'s blank-skip.

⇒ `'1.5'` IS a real operand and `''` IS integer 0. **Any fast path that treats "tag is not DT_I/DT_R" as
"not a number" is WRONG** — it is only allowed to mean "not YET a number, go convert." This is the exact
distinction the hoist formalizes: after COERCE_NUMBER, the tag IS the truth; before it, the tag is a hint.

---

## 3. THE BIT LAYOUT — AND WHY THE HOT PATH NEEDS NO RENUMBERING

### 3.1 ⭐ The trick already exists

Current tags (`src/contracts/descr.h:5-24`):

```
DT_SNUL = 0    DT_I = 6  = 0b110
DT_S    = 1    DT_R = 7  = 0b111
```

**`DT_I` and `DT_R` differ in EXACTLY ONE BIT (bit 0), and no other numeric tag exists.** Therefore, *given
the operands are guaranteed numeric*, the entire mixed-mode rule of §2.1 is:

```asm
mov  eax, [a_tag]
or   eax, [b_tag]     ; 6|6=6 (both int) · 6|7=7 · 7|7=7 (either real)
test eax, 1           ; ZF=1 -> both INTEGER · ZF=0 -> result REAL
```

**Two instructions, no table, no indirect branch, no renumbering.** The guarantee that makes it sound is
precisely what `IR_COERCE_NUMBER` supplies. The two halves of the proposal compose — but the second half is
already paid for.

### 3.2 What renumbering would actually buy

A one-hot low-bit layout (bit0=NUMERIC, bit1=REAL, bit2=STRING) would reduce the *uncoerced* "is this
numeric?" test from 3 instructions (`sub eax,6 / cmp eax,1 / jbe`) to 1 (`test al,1`). That test lives
**inside COERCE — the cold path by construction.** Two instructions saved on the slow path.

### 3.3 What renumbering would cost — MEASURED blast radius

| Cost | Evidence |
|---|---|
| Every template emits `(long)DT_I` as an **immediate** ⇒ emitted bytes change tree-wide | `bb_binop_relop.cpp:29`, `bb_coerce_numeric.cpp`, `bb_binop_gvar_arith*.cpp` |
| `.s` regen ×3 fires (RULES step 4) + demo + benchmark artifacts | RULES.md step 4 |
| ⛔ **`DT_DATA` is used as an OPEN-ENDED RANGE BASE in two places** — `obj.v >= DT_DATA`, `inst.v < DT_DATA` | `driver_data.c:392, 420` |
| Four dormant backends carry their own artifacts (`.il .j .js .wat`) beside every crosscheck program | `corpus/crosscheck/patterns/*` |

⛔ **THE `DT_DATA` RANGE IS THE TRAP AND IT IS A CORRECTNESS TRAP, NOT A CHURN TRAP.** With class bits in the
LOW bits, a user datatype at `DT_DATA + k` has arbitrary low bits — so a `DATA()` instance could set the
NUMERIC bit and be silently accepted by an arithmetic fast path. Everything else in the tree compares
`== DT_DATA`, so the range is nearly vestigial; **but "nearly" is what mints phantoms.** If we renumber,
those two sites convert to `==` in the SAME commit, or the DATA range is strided by 8 with class 0.

### 3.4 RECOMMENDATION

**DO NOT RENUMBER `DT_t` — not now.** The hot path's win is already available at zero cost (§3.1); the
renumbering's win is 2 instructions on the cold path, against a tree-wide artifact churn and one live
correctness trap. **Take §3.1 for free, ship the hoist, MEASURE, and revisit renumbering only if a measured
profile puts the uncoerced class test in a hot window.** That ordering is ARCH §7 step 0(d) applied to a
design decision instead of a symbol.

**IF Lon directs the renumber anyway**, the safe layout is class-in-low-3-bits, ordinal above, with the
invariants pinned by `_Static_assert` (the `rt.c:354` precedent) so a later edit breaks the BUILD, not the
runtime:

```c
/* bit0 = NUMERIC · bit1 = REAL · bit2 = STRING · bits 3+ = ordinal */
DT_I = 0x01, DT_R = 0x03, DT_SNUL = 0x04, DT_S = 0x0C, DT_P = 0x08, DT_A = 0x10, ...
_Static_assert((DT_R & 1) && (DT_I & 1),            "NUMERIC bit0 invariant");
_Static_assert((DT_R & 2) && !(DT_I & 2),           "REAL bit1 invariant");
_Static_assert(!(DT_S & 1) && !(DT_SNUL & 1),       "strings must never read as numeric");
_Static_assert(!(DT_DATA & 7),                      "DATA range must carry class 0");
```

---

## 4. THE DISPATCH MATRIX — RIGHT FOR COERCE, WRONG FOR ADD

The 3×3 / 4×4 indexed-call matrix is a good instrument **inside `IR_COERCE_NUMBER`**, where the operand pair
really is a 4-class × 4-class decision and the path is cold enough that a `movzx` through a class LUT plus an
indexed call costs nothing that matters.

⛔ **It is a PESSIMIZATION inside `IR_ADD`, and this is a prediction that should be falsified rather than
believed.** After the hoist, ADD's decision is 2×2, not 4×4 — and the shape of the decision is a *biased*
branch, not a uniform one. `arith_int` is 100% integer over 100,000,000 calls; `arith_mixed` is 50/50 over
80,000,001 (MEASURED s210, `util_rtx_arith_census.c`). A `test`+`jz` that resolves one way ~100% of the time
costs ~1 cycle and folds into the pipeline. An indexed `jmp [table + rax*8]` is an **indirect branch**: it
consumes BTB capacity, and on the mixed program it alternates between two targets 40,000,000 times.

⇒ **Use the matrix where the classes are genuinely 4-wide and cold (COERCE). Use the two-instruction
`or`/`test` of §3.1 where the classes are 2-wide and hot (ADD/SUB/MUL/DIV/MOD).**

⚠ Pre-stated so it can be graded: if someone builds the 16-way table for ADD anyway, I predict it measures
**0.95×–1.00× on `arith_int` and 0.90×–1.00× on `arith_mixed`** — i.e. neutral-to-negative. If it measures a
win, this section is wrong and the FINDING must say so.

---

## 5. THE ARCHITECTURE

```
BEFORE:   [operand a] ──┐
                        ├──> IR_BINOP_ARITH ──> rt_add ──> int-int? ──> DT_DATA overload? ──> setjmp ──> impl
          [operand b] ──┘                                                                     ^^^^^^
                                                                          the 3.710x that RTX-6 bought by
                                                                          bypassing it for ADD/SUB/MUL only

AFTER:    [operand a] ──> IR_COERCE_NUMBER(self=a, other=b) ──┐
                                                              ├──> IR_BINOP_ARITH  (tags ∈ {DT_I, DT_R})
          [operand b] ──> IR_COERCE_NUMBER(self=b, other=a) ──┘         or / test / 2-way branch
```

**Contract established by the hoist, and it is the whole point:**
> On entry to any arithmetic BB, both operand slots carry `DT_I` or `DT_R`. No string. No DATA. No error
> path reachable from conversion.

**What that contract deletes from the binop:** the string test, the `DT_DATA` overload probe, the
unconvertible-operand error, and therefore `setjmp`. What it leaves is the genuine domain failures —
divide-by-zero, `INT64_MIN / -1` — which are explicit compares, not longjmp targets.

### ⭐ 5.1 The payoff that connects this to the parked ladder

RTX-6 refused DIV/MOD/POW with a specific reason: *"the setjmp-bypass soundness argument does not cover
them."* That argument was about **conversion** failures. Once conversion is hoisted, the only failures left
in DIV/MOD are a zero test and one overflow test — both cheap, both local, neither needing `setjmp`.

**⇒ The hoist is the prerequisite that unblocks RTX-6's DIV/MOD/POW.** That is a structural claim, gradeable
by whether those ports become writable, and it should be stated that way rather than as a speed number.

⭐ It also retires a real defect class: s207 recorded that the old inline `idiv` had **no zero-divisor test**
(SIGFPE instead of statement failure) in 5 committed artifacts. A hoisted design makes the zero test the
binop's ONLY guard, in one place, instead of a condition scattered across template arms.

---

## 6. TRAPS — READ BEFORE CODING

1. ⛔ **LITERALS MUST NOT PAY COERCION.** `GOAL-OPTIMIZER.md:28-29` records OPT-CP copy_prop seeing through
   `IR_COERCE_STRING` over `LIT_STRING` and `IR_COERCE_INTEGER` over `LIT_INTEGER` — **`IR_COERCE_NUMERIC` is
   NOT in that list.** Wire the hoist without adding the fold and every `N = N + 1` pays a coercion node on a
   compile-time-known integer. **Add the fold in the same commit.** This is the likeliest way for this rung
   to land correct and measure a REGRESSION.
2. ⛔ **The joint decision needs BOTH operands, so the two COERCE nodes are a DAG, not a tree.**
   `FINDING-2026-07-26e` already records ZB-VAL-8 being a DAG not a tree. Each operand's COERCE reads the
   other's tag; neither may consume the other's *converted* value. Order-independence must be proven, not
   assumed.
3. ⚠ **`bb_coerce_numeric.cpp`'s existing fast path passes `self` through when `self` is `DT_R` without
   consulting `other`.** Correct (real stays real), but it means the template is already asymmetric — do not
   "fix" that asymmetry into a symmetric probe without re-reading §2.1.
4. ⚠ **Shared runtime.** `arithmetic.c` is Prolog's and Icon's arithmetic path too (s210 required
   beneficiary notification to ICON-RTX + PROLOG). Any change gets both batteries at gate ON *and* OFF —
   and per ARCH §7 2b, an unmoved battery is NOT asm evidence, only no-regression evidence.
5. ⛔ **The watermark is FALSE at HEAD** (s210: recorded 314/1, measured 268/47) and s211 localized the
   cause's *symptom* to TAB/RTAB. **Do not grade this rung's absolute gate until that is closed** — use the
   three-way ON/OFF/PRISTINE differential, which survives a broken baseline.

---

## 7. LADDER (each rung: ARCH §7 protocol verbatim)

- [ ] **NC-0 — STEP 0(d) FIRST.** Count `rt_coerce_num2_d` and `rt_num_arith` dynamically under
      `arith_int` / `arith_mixed` / a NEW string-operand benchmark, at two loop counts, confirm scaling.
      ⛔ **There is no string-operand arithmetic benchmark in the corpus today — one must be written, or this
      rung is graded on programs that never execute its path** (the RTX-12 blind-instrument defect).
- [ ] **NC-1 — WIRE.** Lower arithmetic operands through `IR_COERCE_NUMERIC` (mirror `lower_snobol4.c:168`).
      Add the OPT-CP fold for `COERCE_NUMERIC` over `LIT_INTEGER`/`LIT_REAL` in the SAME commit (trap 1).
      Gate: crosscheck ON/OFF/PRISTINE identical; `.s` regen ×3 owed (templates + lower change emitted bytes).
- [ ] **NC-2 — NARROW THE BINOP.** With the contract proven, delete the string/DATA/`setjmp` arms from the
      arithmetic entries; adopt the §3.1 `or`/`test`. Two-sided falsification aimed at the JOINT rule
      (corrupt `or`→`and`: int+real must then wrongly yield integer — output-sensitive, unlike `arith_loop`
      which s210 proved is a fixed point that absorbs corruption).
- [ ] **NC-3 — DIV/MOD/POW.** Now writable. Zero test and `INT64_MIN/-1` test explicit and local.
- [ ] **NC-4 (OPTIONAL, GATED ON MEASUREMENT) — the class LUT + 4×4 matrix inside COERCE only.** §4.
- [ ] **NC-5 (LON'S CALL, NOT RECOMMENDED) — `DT_t` renumber.** §3.4, with the `driver_data.c` `>=`/`<`
      conversion and the `_Static_assert` set in the same commit.

**PRE-STATED BANDS (so they can be falsified — s210's under-prediction proves this cuts both ways):**
`arith_int` **0.98–1.05×** (already had an inline int arm; hoist removes little it actually pays) ·
`arith_mixed` **0.98–1.10×** *against the RTX-6 asm build* (ADD/SUB/MUL already bypass setjmp, so the hoist
adds little there) · a NEW string-operand benchmark **1.5×–4×** (this is where the deleted ceremony lives,
and it is the only place I expect a large number). **If the first two come back large, distrust the
harness before believing the rung.**
