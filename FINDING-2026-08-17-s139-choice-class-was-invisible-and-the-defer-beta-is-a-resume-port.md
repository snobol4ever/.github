# FINDING 2026-08-17 s139 — THE ζ CHECKER WAS BLIND TO THE CLASS THIS GOAL CALLS R-0, AND THE UNSEALED DEFER'S β IS A RESUME PORT, NOT A FAIL EXIT

**Seat:** Claude Opus 5. **Trees:** SCRIP `b470f84e`+ (2 templates touched), corpus untouched.
**All rungs DEFAULT-INERT — 1557/1557 real programs byte-identical, regens ×3 report zero changed bytes, `test_gate_zdp_on_null.sh SCRIP_ZONE=1` PASS (659, movers=0).**

---

## 1 ⭐⭐⭐⭐⭐ THE INSTRUMENT COULD NOT SEE THE CHOICE CUSTOMER AT ALL — AND CHOICE IS 52% OF BEAUTY'S ζ TRAFFIC

`ZREFC` (s138) hardwired ONE decline spelling: `FR/FRQ(x86_scratch_off + d)`, the leaf family's flat ZLS coordinate. The ALT choice record's declined arm is a **different address** — bare `[rsp+d]` — so `bb_match_alternate` could not call the accessor on that arm and guarded **outside** it: `cro ? CROQ(..) : RSP(..)`.

`sn4_choice_rbp_off()` returns 0 for every blob in beauty (the s128 admission is `_nc==1 && !_lf && !_fn`, very narrow), so **every** choice-record access took the unrouted arm. Measured consequence, s138 census vs this seat's:

| | s138 census | s139 census |
|---|---|---|
| CAPTURE | 58 homed | 58 homed |
| FENCE | 24 homed | 24 homed |
| ARBNO | 5 homed | 5 homed |
| LEAF | 192 spine | 192 spine |
| **CHOICE** | **absent — 0 entries** | **300, ALL spine, none homed** |
| **total** | **279** | **579** |

⛔ **The class the goal file names as R-0 / the M1 root cause — "ALT-arm-interior capture has no home" — was the one class the displacement checker could not observe.** s138's census on beauty ("279 resolutions, ZERO disagreements") was true and also 52% blind.

**CURE (landed, inert): `ZSP_SCRATCH`/`ZSP_RAW`, the DECLINE-SPELLING AXIS.** `ZREFS(reg_off, d, w, customer, spine)` is the dispatcher; `ZREFC` is its `ZSP_SCRATCH` wrapper (all four existing customers unchanged by construction); `CROQ`/`CROD` become `ZSP_RAW`. All 7 address sites in `bb_match_alternate.cpp` now call the accessor unconditionally. Byte-identical because `RSP(d)` **is** `RDQ("rsp", d)` verbatim (x86_asm.h:1424) and the dword site already spelled `RDD("rsp", d)` by hand. The `sub rsp,32`/`add rsp,32` carve/release pair stays guarded on `cro` — that one is behaviour, not an address.

⛔ **THE AXIS IS NOT A TIER.** Tier = which base the planner chose. Customer = which cell of that base. Spine spelling = how this customer addresses the spine *when it has no rbp home*. Conflating the third with the first is what would re-base a raw `[rsp]` record onto the leaf scratch coordinate — a different address.

---

## 2 ⛔⭐⭐⭐ THE INHERITED s137 DISCRIMINATOR CHAIN WAS MEASURED ON ORACLE-**FAIL** PROGRAMS

s137's cursor states the discriminator as: *"inner defer to `LEN(0)` (carves nothing) **ok**; to `SPAN(' ')` (carves) **FAIL**; the same alternation written INLINE **ok**."* Re-measured this seat against the live oracle:

| ablation | oracle | scrip | verdict |
|---|---|---|---|
| `Sp=SPAN(' ')`, subject `'START HERE'` | **FAIL** | FAIL | **agree — SCRIP IS CORRECT; unusable as a discriminator** |
| `Sp=LEN(0)`, subject `'START HERE'` | **FAIL** | FAIL | **agree — unusable** |
| inline `SPAN(' ')`, subject `'START HERE'` | **FAIL** | FAIL | **agree — unusable** |

Those three patterns genuinely do not match, so SCRIP's FAIL was the **right answer**, not a defect. **A red/green pair is only a discriminator if the oracle says `ok` on both arms.**

**REBUILT, every arm oracle-`ok`** (`/tmp/ab2_*.sno` shape; mint these into `corpus/probe/m1/` next seat):

| witness | subject | `Sp` | body | oracle | scrip |
|---|---|---|---|---|---|
| `defer_ALT` | `START HERE` | `SPAN(' ') \| LEN(0)` | `L *Sp` | ok | **FAIL** |
| `defer_SPAN` | `START HERE ` | `SPAN(' ')` | `L *Sp` | ok | **FAIL** |
| `defer_LEN0` | `STARTHERE` | `LEN(0)` | `L *Sp` | ok | ok |
| `inline_ALT` | `START HERE` | — | `L (SPAN(' ') \| LEN(0))` | ok | ok |
| `nodefer_ALT` | `START HERE` | `SPAN(' ') \| LEN(0)` | `L Sp` | ok | ok |

⭐ **THE DISCRIMINATOR SURVIVES, BETTER FOUNDED: an ARBNO body defer whose target CARVES.** `defer_SPAN` fails with **no alternation present at all**, so the ALT is an *instance* of "carves", not the cause. Defect C's naming (`emit_defer_rbp()`'s own comment, emit.cpp:2233) is confirmed — now on witnesses that can testify.

---

## 3 ⭐⭐⭐⭐⭐ FIX SHAPE (A) IS NOT "NECESSARY BUT NOT SUFFICIENT" — AS LANDED IT WAS GLOBALLY DESTRUCTIVE, FOR A LOCATABLE REASON

s137 recorded only *"red goes from a clean FAIL to a SEGV."* Measured this seat, `SCRIP_DEFER_CARVE_RBP=1` **SEGVs `defer_LEN0` and `inline_ALT` too — programs that PASS on the default arm.** That is a different and worse verdict than "insufficient", and it has a named cause:

**`bb_match_defer.cpp:254` still tested `_.op_seal == 1` while α (line 55) tested `dfrm()`.** s137 introduced `dfrm()` *precisely* so "α and its exits cannot drift apart" and converted 53/131/147 — this exit was missed. Under the widened gate α pushed a frame that β never popped; every backtrack leaked one.

**But converting β to `dfrm()` is ALSO wrong, and the asm says why.** Default arm:
```
n5_match_defer_β:   jmp qword ptr [rsp]          ← a RECORD-RESUME
```
Converted arm:
```
n5_match_defer_β:   mov rsp,rbp; pop rbp; add rsp,16; jmp PAT$2_ω    ← a FAIL EXIT
```
⛔ **An UNSEALED defer's β is a RESUME PORT; a SEALED defer's β is a fail exit (the fence demarcation).** They cannot share one arm, which is why `op_seal` — not `dfrm()` — must keep selecting between them. s137 measured exactly two shapes (include β, exclude β) and both are wrong for this one reason: including it destroys the resume, excluding it leaves α's `push rbp` unmatched on the resume path so rsp is one frame low when the record is read.

**THE COMPOSITION NEITHER CUT TRIED (landed, default OFF): restore the frame, THEN resume the record.**
```
n5_match_defer_β:   mov rsp,rbp; pop rbp; jmp qword ptr [rsp]
```
Result: `m1_arbno_nested_defer_grn` now holds under the widening; **the carve witnesses still SEGV.**

---

## 4 ⭐⭐⭐ WHERE THE RESIDUE NOW IS — SMALLER AND NAMED

The composition is the right *shape* and still SEGVs, which localises the remainder precisely: **β cannot trust the ambient `rbp`.** The defer suspends at γ still holding its activation frame; by the time β resumes, other activations (an enclosing MATCH_BEGIN's ζ-STANDING, a sibling defer, the next ARBNO instance) may have pushed their own. rbp being callee-saved protects it across *C* crossings, not across a *suspension*.

⭐ This is s137's residue restated with evidence rather than inference — *"the frame must survive the suspension and be re-established per instance"* — and it is now the **only** unexplained step: α is right, the exits are paired, the resume composition is right, and the failure is that `rbp` at β is not provably OUR frame.

**NEXT SEAT, pick up exactly here:**
1. **The frame must be recoverable from the RECORD, not from ambient rbp.** The record already carries the resume address at `[rsp+0]`; the activation's frame base belongs beside it. Widen the defer record and have β restore rbp **from the record** before the resume.
2. ⛔ **Do NOT land on a single-witness green.** `defer_LEN0`/`inline_ALT` are the standing counter-witnesses this seat added *because* they pass by default — the 150/151 pair and `probe/arbnofence/` punished the last two widenings.
3. **Mint the §2 table into `corpus/probe/m1/` with `.ref` files.** Every arm oracle-`ok`, so any FAIL is a defect by construction.
4. **The CHOICE census is now free** — `SCRIP_ZONE=1 SCRIP_ZONE_BOMB=2` shows all 300 of beauty's choice records and no prior seat could see one.

## 5 OWED AND PAID
1557/1557 byte-identical (only `unary_not.sno` moves — **re-proven self-nondeterministic this seat: 5 runs, 5 distinct md5s, same binary**) · `test_gate_zdp_on_null.sh SCRIP_ZONE=1` PASS 659/0 · regens ×3 zero changed bytes · medium-invisible strict FAILs on the **inherited** `bb_glue_flat(4)`/`xa_flat(8)` baseline, touched files contribute 0, diff adds 0 · beauty unmoved (10 lines vs oracle 622) **as expected — this rung is instrumentation and localisation, not the cure.**
