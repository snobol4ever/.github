# DESIGN-SN4-ARITH-INLINE-AND-DT-BITS.md — Inline Arithmetic BBs, the Tag Bit Layout, and the Juxtaposed Dispatch

**Drafted s212 (2026-07-29, Claude + Lon), on Lon's directive: *"Make it where the actual arithmetic
instruction is INLINE within the template. Also make a super fast way to check for need for coercion. Make
the number of instructions for these INLINE BB's as small as possible. Use special shift and bit-wise
operators by redesigning the bits in DT_t type of the DESCR. Also consider dispatch tables indexed by a
combined calculation of the two types juxtaposed together."***

**Design only. Nothing landed. Nothing measured beyond the lines explicitly marked MEASURED.**
Supersedes §3.2/§3.4 of `DESIGN-SN4-NUMERIC-COERCION.md` — see §2, which **corrects that document's central
recommendation**. Companion to `ARCH-SNOBOL4-RTX.md` (§2 register contract, §7 protocol).

---

## 0. THE FOUR ASKS, ANSWERED UP FRONT

| Lon's ask | Verdict | Where |
|---|---|---|
| Arithmetic instruction INLINE in the template | **YES — 18 instructions + call/ret ⇒ 8.** Removes the call, the PLT hop, and the per-call gate branch entirely. | §1 |
| Super-fast coercion-need check | **YES — and it is IMPOSSIBLE under the current numbering.** Proven exhaustively, not argued. | §2 |
| Minimum instruction count | **8 (hoisted) / 13 (self-contained).** Both beat today's 18+call. | §1, §3 |
| Redesign DT_t bits | **YES — and this REVERSES my own s211 recommendation.** The prior doc measured the wrong path. | §2 |
| Dispatch table on juxtaposed types | **NO for the binop, YES inside COERCE.** Prediction pre-stated for falsification. | §4 |

⛔ **THE DIRECTIVE ITSELF REVERSES AN EARLIER ONE, AND THAT SHOULD BE ON THE RECORD:** s207's Lon directive
was *"for now all these should be ONE CALL into the runtime. We'll optimize the inline later."* The RTX-6
residual rung records the inline work as **DEFERRED BY DIRECTION, not abandoned**, and records the measured
cost of that deferral (`arith_loop` **0.64×**, `arith_mixed` **0.80×**, RT_OPT=-O0). **This directive is
"later" arriving.** The 0.64×/0.80× is the floor this work must beat, and it is an honest floor because the
deferral's cost was measured at the time rather than estimated now.

---

## 1. THE INLINE ARITHMETIC BB

### 1.1 What is emitted today — MEASURED, read from the tree

`src/templates/bb_binop_arith.cpp:78-92` (the `op_off` arm) emits **9** instructions:

```asm
mov  rdi, FRQ(sa)        ; a.v | a.slen
mov  rsi, FRQ(sa+8)      ; a.payload
mov  rdx, FRQ(sb)        ; b.v | b.slen
mov  rcx, FRQ(sb+8)      ; b.payload
call rt_add
cmp  eax, DT_FAIL
je   omega
mov  FRQ(off),   rax
mov  FRQ(off+8), rdx
```

and `rt_add` (`src/runtime/rtx/rtx_arith.S:180`) adds **9** more on the int-int path — the gate
(`RTX_GATE` = `cmp byte ptr [rip+rtx_gate_arith], 0` + `je`, from `rtx_abi.inc:70`), four tag
compare/branches, the `lea`, the `mov eax, DT_I`, and the `ret`:

```asm
cmp byte ptr [rip+rtx_gate_arith], 0
je  c_rt_add
cmp edi, DT_I
jne .Ladd_notii
cmp edx, DT_I
jne .Ladd_notii
lea rdx, [rsi + rcx]
mov eax, DT_I
ret
```

**⇒ 18 instructions + `call`/`ret` + a PLT/GOT indirection, to perform one `lea`.**

### 1.2 ⭐ THE KEY IDENTITY — THE `or` COMPUTES THE RESULT TAG *AND* THE BRANCH CONDITION

SPITBOL Ch. 2, read this session per the ARCH §7 step-1 standing directive, verbatim from the manual:

> *"The operands may be integers or real numbers, or a mixture of both. If both operands are integers, the
> result will be an integer. If either operand is real, the result will be real."*

That is a **bitwise OR** over a one-bit REAL flag. With today's tags (`DT_I=6=0b110`, `DT_R=7=0b111`):

| a\|b | value | tag | correct? |
|---|---|---|---|
| I\|I | 6\|6 = 6 | DT_I | ✓ |
| I\|R | 6\|7 = 7 | DT_R | ✓ |
| R\|R | 7\|7 = 7 | DT_R | ✓ |

**The OR of the two tags IS the result tag, exactly, with no correction.** So the `mov eax, DT_I` in the
landed asm is redundant work — the value is already sitting in the register that computed the branch
condition. This holds in the current numbering AND in the proposed one (§2), so it is free either way and
should be taken regardless of what Lon decides about renumbering.

### 1.3 The emitted BB — HOISTED form (operands guaranteed numeric)

```asm
mov  eax, FR32(sa)       ; 1  a.v          (32-bit load zeroes rax[63:32] ⇒ slen=0 for free)
or   eax, FR32(sb)       ; 2  eax = JOINT RESULT TAG, and bit0 = either-real
test al, 1               ; 3  ZF=1 ⇒ both integer          (macro-fuses with the jnz)
jnz  .Lreal              ; 4  COLD, out-of-line
mov  rdx, FRQ(sa+8)      ; 5
add  rdx, FRQ(sb+8)      ; 6  a.i + b.i    (memory operand — no third register needed)
mov  FRQ(off),   rax     ; 7  tag already correct, slen already zero
mov  FRQ(off+8), rdx     ; 8
```

**8 instructions. Zero calls. Zero PLT. Zero gate branch. One branch, statically never-taken on
`arith_int` (MEASURED s210: 100% integer over 100,000,000 calls).**

`test`+`jnz` macro-fuse, so this is ~7 uops against today's 18 + call/ret + indirect-call overhead.

⚠ `SUB` uses `sub rdx, FRQ(sb+8)` (load `a` first — non-commutative). `MUL` uses `imul rdx, FRQ(sb+8)`.
`DIV`/`MOD` need the zero test and the `INT64_MIN / -1` test made explicit and local — which is precisely
what `DESIGN-SN4-NUMERIC-COERCION.md` §5.1 says the hoist unblocks, and it retires the s207 defect where the
old inline `idiv` had **no zero-divisor test** (SIGFPE instead of statement failure) in 5 committed artifacts.

### 1.4 ⛔⛔ STRUCK s212 — THIS SECTION WAS WRONG. THE "BLOCKER" DID NOT EXIST.

**MEASURED s212: the inline int-int arm landed with ZERO `x86_asm.h` changes.** Every encoder this section
declared missing for the int path was already live and already in use by `GVA_LD` in
`bb_binop_gvar_arith.cpp` (`mov r32,m32` · `cmp r32,imm` · `jne L(n)` · `def L(n)` · `add`/`sub`/`imul`
r64,r64 · `mov m64,imm`). **The RTX-11/12 concurrency collision was never opened, and Lon's ruling was never
needed.**

⭐ **ROOT CAUSE, AND IT IS THE MIRROR IMAGE OF THE PHANTOM-SYMBOL FAMILY: this gap was costed FROM THE
DESIGN, NOT FROM THE TREE.** I enumerated the instructions my §1.3 sequence wanted and grepped for those
exact mnemonics, instead of asking whether any template already emits this shape. The phantom shapes are
capabilities *declared live that are dead*; this is a capability **declared dead that was live** — same
error, opposite sign, and it costs a rung by making it look BLOCKED rather than by making it look done.
⇒ **grep the templates for a working precedent before declaring an encoder gap**, exactly as step 0(e) greps
`.S` before declaring a symbol dead.

⚠ **STILL TRUE:** the **SSE** set (`addsd` `subsd` `mulsd` `divsd` `ucomisd` `cvtsi2sd`) genuinely does not
exist, so the REAL arm (AI-4) does still fire the collision. The original text follows for that reason only.

### 1.4-orig (retained for the SSE arm) — THE ENCODER GAP

RULES.md **TEMPLATE-ONLY EMISSION** is absolute: every instruction, both media, only inside `x86(...)` in
`x86_asm.h`. **MEASURED this session by grepping `x86_asm.h` — the following do not exist:**

| Needed for | Missing encoder |
|---|---|
| §1.3 int path | `or r32, m32` · `test r8, imm8` · `add r64, m64` · `sub r64, m64` · `imul r64, m64` |
| real path | `addsd` `subsd` `mulsd` `divsd` `ucomisd` `cvtsi2sd` (`movq xmm,r64` EXISTS; `movsd` handles only the `f64:` immediate form) |
| §4 table | `shl` · `sar` · `or r32,r32` · indexed `jmp [tab + r*8]` |

⛔⛔ **THIS FIRES THE RTX-11/12 CONCURRENCY COLLISION THAT `GOAL-SNOBOL4-RTX.md` EXPLICITLY RESERVES TO LON:**
*"⛔ RTX-11/12 are NOT concurrency-safe — they touch `x86_asm.h` + fire `.s` regen ×3."* With 3–4 parallel
chat sessions live (RULES concurrency note), `x86_asm.h` is the one file that cannot be edited blind.
**Nothing in §1 or §3 can be built until Lon rules on serializing this.**

⚠ And every new encoder is governed by `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` R2/R7/R9/R10 + the
**"ONE MEDIUM, INVISIBLE"** FACT RULE: one `x86(...)` concatenation, medium switched *inside* the encoder,
never a hand-written `IF(MEDIUM_TEXT,…)+IF(MEDIUM_BINARY,…)` pair. PLAN.md step 6 records that this exact
mistake was made twice in one SNOBOL4-BB session before being caught.

---

## 2. THE DT_t BIT REDESIGN — ⭐⭐ AND A CORRECTION TO MY OWN s211 DOCUMENT

### 2.1 ⛔ WHAT s211 GOT WRONG

`DESIGN-SN4-NUMERIC-COERCION.md` §3.2 states the renumber's benefit as:

> *"would reduce the uncoerced 'is this numeric?' test from 3 instructions to 1. That test lives inside
> COERCE — the cold path by construction. **Two instructions saved on the slow path.**"*

and §3.4 concludes **"DO NOT RENUMBER `DT_t` — not now."**

**That analysis is wrong, and it is wrong in a specific and instructive way: it silently assumed the hoist.**
It costed the renumber *conditional on `IR_COERCE_NUMERIC` already being wired*, under which the binop has no
class test left to accelerate — so of course the renumber looked worthless. It never costed the renumber on
the **self-contained inline binop**, which is the shape Lon has now asked for and the shape that does not
require the DAG-shaped two-node COERCE wiring at all.

⭐ **THE GENERAL SHAPE, AND IT BELONGS IN RULES: A DESIGN DOC THAT EVALUATES OPTION B ONLY IN THE WORLD WHERE
OPTION A HAS ALREADY LANDED WILL ALWAYS CONCLUDE THAT B IS WORTHLESS.** This is the design-level twin of the
s188 blind-instrument defect (`RTX-12`'s board is blind to RTX-1…7) and of the s207→s210 **stale census**
(the ninth phantom shape): in all three, the *instrument* — here, the assumed baseline — was the thing at
fault, not the thing being measured. **State the baseline a comparison is taken against, or the comparison
is unreadable.**

### 2.2 THE CLAIM THAT DECIDES IT — PROVEN EXHAUSTIVELY, NOT ARGUED

**Question: under the current numbering, is there ANY two-operand form `(a OP b) & m == k` that tests "both
operands numeric" exactly?**

Brute-forced this session over `OP ∈ {and, or, add, xor}` × all 256 masks × all 256 constants, against the
full live tag set from `descr.h`:

```
current numbering, 2-op both-numeric tests found: 0
```

**ZERO.** The current numbering *cannot* express a combined both-numeric test at any width. The reason is
concrete: `DT_X = 15 = 0b1111` and `DT_I = 6 = 0b110` give `15 & 6 = 6` — a `DT_X` operand is
indistinguishable from `DT_I` under `and`. So today each operand must be tested **separately**, at 3
instructions each.

⇒ s211's "2 instructions on the cold path" is not an understatement, it is the wrong quantity. The correct
statement is: **the renumber makes possible a test that is currently impossible, and that test is on the hot
path of the self-contained inline binop.**

### 2.3 THE LAYOUT — every invariant verified computationally this session

```c
/* bit0 = NUMERIC · bit1 = REAL · bit2 = STRING · bits 3+ = ordinal */
typedef enum {
    DT_I     = 0x01,   /* 0b00000001  NUMERIC                     */
    DT_R     = 0x03,   /* 0b00000011  NUMERIC | REAL              */
    DT_SNUL  = 0x04,   /* 0b00000100  STRING                      */
    DT_S     = 0x0C,   /* 0b00001100  STRING | ordinal 1          */
    DT_P     = 0x10, DT_A  = 0x18, DT_T    = 0x20, DT_C    = 0x28,
    DT_N     = 0x30, DT_K  = 0x38, DT_E    = 0x40, DT_FH   = 0x48,
    DT_PLVAR = 0x50, DT_PLREF = 0x58, DT_X = 0x60, DT_BLK  = 0x68,
    DT_FAIL  = 0x70,
    DT_DATA  = 0x80,   /* user datatype n  ==  DT_DATA + 8*n  (STRIDE 8, class bits 0) */
} DTYPE_t;
```

| Invariant | Verified |
|---|---|
| `(a & b) & 1` ⟺ both operands numeric — **exact over the full tag set** | ✓ |
| `a \| b` == the joint result tag (SPITBOL Ch. 2 rule) | ✓ |
| `(a \| b) >> 1 & 1` == either-operand-real | ✓ |
| DATA stride-8 never sets the NUMERIC bit, for all 64 user types | ✓ |
| no string tag sets the NUMERIC bit | ✓ |
| every tag fits in one byte ⇒ `cmp r8, imm8` forms stay available | ✓ |

Pin them so a later edit breaks the **build**, not the runtime (the `rt.c:354` `_Static_assert` precedent):

```c
_Static_assert((DT_I & 1) && (DT_R & 1),                      "NUMERIC is bit0");
_Static_assert(!(DT_I & 2) && (DT_R & 2),                     "REAL is bit1");
_Static_assert(!(DT_S & 1) && !(DT_SNUL & 1),                 "strings never read numeric");
_Static_assert(!(DT_DATA & 7),                                "DATA base carries class 0");
_Static_assert((DT_I | DT_R) == DT_R && (DT_I | DT_I) == DT_I, "OR is the joint-real rule");
```

### 2.4 ⛔ THE `DT_DATA` RANGE IS STILL THE CORRECTNESS TRAP — RE-MEASURED, STILL EXACTLY TWO SITES

```
src/driver/driver_data.c:392:  if (obj.v >= DT_DATA && obj.u)
src/driver/driver_data.c:420:  if (inst.v < DT_DATA || !inst.u) return NULL;
```

Every other DT_DATA use in the tree is `==`. **With class bits in the LOW bits and an unstrided range, a
user datatype at `DT_DATA + k` with odd `k` would set the NUMERIC bit and be silently accepted by the
arithmetic fast path** — a wrong-answer defect, not a crash. **Stride 8 (§2.3) removes it structurally**, and
the two `>=`/`<` sites convert to a mask test (`(v & ~7) == DT_DATA`) **in the same commit that renumbers**.

### 2.5 Blast radius — MEASURED

1,483 `DT_*` references across 90 files in `src/`. Nearly all are symbolic and survive a renumber by
recompiling. The real churn is that **templates emit `(long)DT_I` as a literal immediate**
(`bb_binop_relop.cpp:29`, `bb_coerce_numeric.cpp`, `bb_binop_gvar_arith*.cpp`), so **emitted bytes change
tree-wide ⇒ `.s` regen ×3 fires**, plus the four dormant backends' `.il/.j/.js/.wat` artifacts beside every
crosscheck program.

⛔ **AND THE WATERMARK IS FALSE AT HEAD** (s210 recorded 314/1, measured 268/47; s211 localized the symptom
to TAB/RTAB and has an unfinished bisect). **A tree-wide artifact regen against a broken baseline cannot be
graded.** ⇒ **the renumber must not land before the TAB/RTAB bisect closes.** The inline work of §1/§3 does
not have this dependency — it is gradeable by the three-way ON/OFF/PRISTINE differential, which survives a
broken absolute baseline.

---

## 3. THE SELF-CONTAINED INLINE BB — WHERE THE RENUMBER ACTUALLY PAYS

This is the variant that needs **no** `IR_COERCE_NUMERIC` wiring, and therefore dodges trap 2 of the s211
doc (*"the joint decision needs BOTH operands, so the two COERCE nodes are a DAG, not a tree"*).

**Under the PROPOSED numbering — 13 instructions:**

```asm
mov  eax, FR32(sa)     ; 1   a.v
mov  ecx, FR32(sb)     ; 2   b.v
mov  edx, eax          ; 3
and  edx, ecx          ; 4   bit0 = BOTH numeric
or   eax, ecx          ; 5   eax = JOINT RESULT TAG; bit1 = either-real
test dl, 1             ; 6
jz   .Lcoerce          ; 7   COLD — out-of-line, calls the existing C
test al, 2             ; 8
jnz  .Lreal            ; 9   COLD — out-of-line
mov  rdx, FRQ(sa+8)    ; 10
add  rdx, FRQ(sb+8)    ; 11
mov  FRQ(off),   rax   ; 12
mov  FRQ(off+8), rdx   ; 13
```

**Under the CURRENT numbering the same BB needs 17**, because §2.2 proves the two operands must be tested
separately (`mov/and 0xFE/cmp 6/jne` twice = 8 instructions where the proposal uses 4).

### ⇒ THE STRUCTURAL POINT LON SHOULD DECIDE ON

**The hoist and the renumber are ALTERNATIVES for the same problem, not complements.**

| Route | Hot binop | Needs | Risk |
|---|---|---|---|
| **A — Hoist only** (s211's NC-1/NC-2) | **8** | `IR_COERCE_NUMERIC` wiring + OPT-CP fold; DAG order-independence proof | Trap 1: every `N = N + 1` pays a coercion node unless the literal fold lands in the same commit |
| **B — Renumber only** (this doc) | **13** | `DT_t` renumber + `.s` regen ×3 + `driver_data.c` | Blocked on the TAB/RTAB watermark |
| **C — Both** | **8**, and COERCE's own class test drops 3→1 | everything above | highest churn |

⭐ **A and B buy overlapping instructions, so C does NOT buy 8+4.** Route A gets the hot path to its floor
with zero artifact churn and is the only one of the three that is **not blocked on the TAB/RTAB bisect**.
Route B's distinct advantage is that it is *local* — no new IR edges, no DAG, no optimizer fold.

**My recommendation: A first, measure, then B on its own merits** (the COERCE class test, and the ~40 other
class tests across the runtime that §2.2's impossibility result also constrains) — **not** as an arithmetic
speed rung. But this is a design preference over a measured floor of 0.64×/0.80×, and Lon owns the call.

---

## 4. THE JUXTAPOSED DISPATCH TABLE — NO FOR THE BINOP, YES INSIDE COERCE

### 4.1 The index is formable in 3 instructions under the proposed layout — but not 1

The attractive form is a single `lea`:

```asm
lea eax, [rdi + rdx*8]      ; eax = a.v + 8*b.v
```

This **works arithmetically** — `rdi[63:32]` holds `a.slen` and `rdx*8` shifts `b.slen` entirely above bit
32, so the 32-bit destination truncates both away cleanly. ⛔ **But it is only correct if the tag IS the
class**, i.e. every tag < 8. With an ordinal in bits 3+, `a`'s ordinal contaminates `b`'s class field. So
masking is unavoidable:

```asm
and eax, 7                  ; a class
and ecx, 7                  ; b class
lea eax, [rax + rcx*8]      ; 6-bit juxtaposed index, 64 entries
jmp [.Ltab + rax*8]         ; INDIRECT
```

### 4.2 ⛔ WHY IT LOSES IN THE BINOP — AND THE PREDICTION IS PRE-STATED SO IT CAN BE FALSIFIED

4 instructions + an **indirect branch**, against §1.3's 3 instructions + a **statically-predicted** branch.
Worse on both counts, and the branch difference is the larger one: `arith_int` is 100% integer over
100,000,000 calls and `arith_mixed` is 50/50 over 80,000,001 (**MEASURED s210**,
`util_rtx_arith_census.c`). A `test`+`jz` that resolves one way ~100% of the time folds into the pipeline;
an indirect `jmp` consumes BTB capacity and, on `arith_mixed`, alternates between two targets 40,000,000
times.

⚠ **PRE-STATED, carried forward from `DESIGN-SN4-NUMERIC-COERCION.md` §4 unchanged so the two documents
agree and the prediction stays gradeable: if the 16-way (or 64-way) table is built for ADD anyway, I predict
`arith_int` **0.95×–1.00×** and `arith_mixed` **0.90×–1.00×** — neutral-to-negative. If it measures a win,
this section is WRONG and the FINDING must say so in those words.**

### 4.3 ⭐ WHERE IT WINS: INSIDE COERCE, WHERE THE DECISION IS GENUINELY 4×4 AND COLD

`IR_COERCE_NUMERIC`'s decision is over `{numeric-int, numeric-real, string, other}²` = 16 real cases, each
with a different conversion action, and the manual makes the string cases non-trivial:

> Ch. 17 / Summary-of-Differences item 9: *"SPITBOL permits leading and trailing blanks on numeric strings
> which are converted to integer or real numbers."*

⇒ `'1.5'` **is** a real operand, `''` **is** integer 0, and `' 42 '` **is** integer 42. **Any fast path that
reads "tag is not DT_I/DT_R" as "not a number" is WRONG — it may only mean "not YET a number, go convert."**
A 64-entry table indexed by `(a.class, b.class)` is the right instrument for exactly this decision: 16 live
cases, a cold path, and no branch predictor to spoil. **Build the table here, not in ADD.**

---

## 5. LADDER (ARCH §7 protocol verbatim on every rung)

- [ ] **AI-0 — LON'S TWO RULINGS, BEFORE ANY CODE.** (a) Serialize `x86_asm.h` against the parallel sessions
      (§1.4 — this is the RTX-11/12 collision the goal file reserves to Lon). (b) Route A / B / C (§3).
- [ ] **AI-1 — STEP 0(d) FIRST, NO EXCEPTIONS.** The instrument for this rung is `arith_int` / `arith_mixed`
      / the **new** `corpus/benchmarks/snobol4/arith_str.sno` delivered s211 (census `other=4,000,000` at
      N=2M, **exact 2× scaling**, oracle-exact checksum). ⛔ **`arith_str.sno` is the ONLY existing window on
      the string-operand path** — without it a coercion rung is graded by a blind instrument (RTX-12 class).
- [ ] **AI-2 — ENCODERS.** Add the §1.4 set to `x86_asm.h` under `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`
      R2/R7/R9/R10 + ONE MEDIUM INVISIBLE. Gate `scripts/test_gate_template_medium_invisible.sh --strict`.
- [ ] **AI-3 — INLINE INT ARM** (§1.3 or §3). ⛔ `.s` regen ×3 owed — templates change emitted bytes.
      Falsification must be **output-sensitive and aimed at the JOINT rule**: corrupt `or`→`and`, under which
      int+real must then wrongly yield an integer. ⛔ **Do NOT grade on `arith_loop` — s210 proved it is a
      fixed point that absorbs corruption silently.**
- [ ] **AI-4 — REAL ARM.** Needs the SSE encoder set. ⛔ NaN discipline: `rtx_arith.S`'s own header records
      that a single `comisd`+`setb` is WRONG because CF=1 for unordered as well as below.
- [ ] **AI-5 — DIV/MOD/POW.** Now writable: zero test + `INT64_MIN / -1` test, explicit and local. Closes
      the s207 no-zero-divisor-test defect (SIGFPE where SPITBOL specifies statement failure).
- [ ] **AI-6 — COERCE 4×4 TABLE** (§4.3), cold path only.
- [ ] **AI-7 — RENUMBER** (§2.3), *if* Lon takes route B or C. ⛔ **BLOCKED on the TAB/RTAB bisect closing**
      (§2.5) — a tree-wide regen cannot be graded against a false watermark. `driver_data.c`'s two range
      sites + the `_Static_assert` set land in the SAME commit.

**BENEFICIARY NOTIFICATION (ARCH §7 trap 4):** `arithmetic.c` is **Prolog's and Icon's** arithmetic path too
(s210 required this). Any change gets both batteries at gate ON *and* OFF — and per ARCH §7 2b, **an unmoved
battery is NOT asm evidence, only no-regression evidence.**

**PRE-STATED BANDS (gradeable; s210's under-prediction proves this cuts both ways):** `arith_int`
**1.15×–1.45×** vs the current one-call build — this is the rung's real target, since the deferral cost
0.64× there and the call/PLT/gate is the whole deleted quantity · `arith_mixed` **1.05×–1.25×** ·
`arith_str.sno` **0.98×–1.05×** (the string path still calls out; the inline arm should not move it, and if
it *does* move, distrust the harness before believing the rung).
