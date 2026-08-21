# FINDING s189 (seat5, `/home/claude5`, Claude Opus 5) — queue row `arbno-altsib-residue`

## ⛔ THE BRIEF'S FIRST DISCRIMINATOR ANSWERS **NO**, AND IT WAS THE ROW'S WHOLE PROPOSED ROAD

The brief: *"MONITOR-ARM-INVISIBLE (s189 sweep): under the monitor this witness AGREES TO END — the
bug needs something MONITOR_BIN disables, which **CONVICTS the GVA-on/optimizer-arm road** and rules
autobug OUT for it. First discriminator: reproduce with the same knobs MONITOR_BIN flips (GVA off) —
**if the red goes green, the GVA road is convicted in one command**."

Measured, one command, both witnesses, m3:

```
default        -> nomatch      MONITOR_BIN=1  -> nomatch      SCRIP_OPT=0 -> <empty>
```

**`MONITOR_BIN=1` leaves both witnesses RED.** GVA-off does not cure them, so the GVA/optimizer-arm
road is **ruled OUT, not convicted**, and the ring-census road the brief proposes rests on a premise
that does not hold. ⭐ The brief's *"under the monitor this witness AGREES TO END"* is not wrong — it
is a statement about the monitor's **event stream**, not about the answer. The stream agreeing while
the answer stays wrong means the divergence is **invisible to the monitor's event vocabulary**, which
is the opposite of a conviction: it is RULES.md's own *"a monitor verdict is a verdict on a DIFFERENT
program"* with the difference being that the monitor cannot see this bug at all.

⛔ Noted in passing, **not this row's class and not chased**: `SCRIP_OPT=0` makes both witnesses print
**nothing at all**, rc=0 — neither `match` nor `nomatch`, from a program whose every path writes one
of the two. `SCRIP_OPT=0` is emergency-only and nothing may depend on it, but silently producing no
output is a different failure from being wrong.

## ⭐⭐⭐ ROOT CAUSE — THE PREDICATE ASKS ABOUT THE ARBNO'S **BODY** WHEN THE HAZARD IS TO ITS **RIGHT**, AND IT DOES SO AT **TWO** FACTS

`arbno_frame_candidate()` (`emit.cpp:2314`) decides whether an ARBNO's cursor gets a **per-activation
`rbp` slot** or stays a **flat ζ-SPINE `rsp` cell**, and it decides by scanning **only the ARBNO's own
body span** `[operands[1]..operands[2]]` for defer/container members. Its own comment says so: *"A
body that is SAFE (plain K0, no container/transfer member) does not need a frame slot at all — it
stays on `bb_match_arbno_frameless()`."*

But the hazard the slot exists to answer is **"can an activation re-enter while this ARBNO instance is
still live and RETRYABLE"**, and that is created by everything to the ARBNO's **RIGHT**. The design
already knows this — `frame_slot_scan`'s R-4(b) comment states it outright: per-activation slots are
*"what recursion … requires and what a single shared STANDING slot at a fixed offset can never give."*
The predicate simply looks in the wrong place for it.

**Witness:** `E = ARBNO('a') ('+' *E | '')` on `'a+a+a'`, `POS(0) *E RPOS(0)` — oracle `match`, SCRIP
`nomatch`. The body is the plain literal `'a'`, so both scans refuse, the cursor stays flat, and the
recursive activation between the carve and the reads displaces it: the outer ARBNO never extends and a
matching subject is **rejected**.

### THE PROOF THAT IT IS THE SPAN AND NOTHING ELSE — A SEMANTICALLY INERT TOKEN FLIPS IT

| program | verdict |
|---|---|
| `E = ARBNO('a' '') ('+' *E \| '')` — inert **non-defer** added to the body | **RED** |
| `E = ARBNO('a' *Z) ('+' *E \| '')` with `Z = ''` — inert **defer** added to the body | **GREEN** |

`*Z` where `Z = ''` **cannot change what the pattern matches.** It changes only the predicate's answer,
and the answer is the difference between a correct and an incorrect program. The asm confirms the
mechanism exactly:

```
RED    n0_match_arbno_α:  sub rsp, 16 ; mov [rsp+0], r14d      _as: [rsp+4]   _af: [rsp+0]
GREEN  n0_match_arbno_α:  mov [rbp-48], r14d ; mov [rbp-44]…   _as: [rbp-44]  _af: [rbp-48]
```
`-48` is `frame_slot_off(blob, 0)` = `-(blob_head_bytes()+8)` = `-(40+8)` — slot 0 of the blob
activation frame, per-activation by construction.

### THE FOUR INGREDIENTS, FROM A 22-PROGRAM ABLATION LADDER

All four are required; removing any one turns it green:

1. **`ARBNO` as the left element** — `'a'` / `SPAN` / `ARB` / `LEN(1)` / `ANY` left elements: all GREEN.
2. **The ALT is IMMEDIATELY adjacent** — `ARBNO('a') 'x' ('+' *E | '')` is GREEN, because the ARBNO's
   retry then completes *before* any recursion is entered.
3. **The ALT has a NULL arm** — `('+' *E | 'z')` is GREEN. Arm **order is irrelevant**:
   `('' | '+' *E)` is RED.
4. **Some arm reaches a RE-ENTRANT defer** — a defer to a pattern that does *not* come back is GREEN
   (`(*F | '')` and `('+' *F | '')` both green, F non-recursive), and **mutual** recursion is RED
   (`E = ARBNO('a') ('+' *G | '')` with `G = 'a' ('+' *E | '')`). So the ingredient is **re-entrancy**,
   not deferring, and not arity of the arm.

⛔ **One inherited control is weaker than it looks and should not be leaned on.** The checked-in
witness's own header says *"`FENCE(...)` instead of the bare ALT is GREEN"*. It is green — but the
**oracle also answers `nomatch`** there, so both engines refuse and the row is agreement-by-refusal.
A control that is green because both sides say no is not evidence about the mechanism.

## ⛔⭐⭐ WHAT THE HALF-CURE MEASURED, AND WHY IT IS THE MOST USEFUL RESULT HERE

I widened the predicate (`SCRIP_ARBNO_REENTRY`): inside a blob activation — which is **by definition**
the callee of a `*P` defer (R-4(b)) — any `IR_MATCH_DEFER` anywhere in the graph can lead back here,
directly or mutually, so every ARBNO in a defer-bearing blob claims a per-activation slot. Membership
is **LOCATION, never identity**, which is `leaf_frame_member`'s own stated law.

**First attempt was INERT, and the reason is a law this codebase already has a name for.** Widening
`arbno_frame_candidate` alone allocated the slot and changed nothing: the template steers on a
**second spelling** of the same fact — `_.op_arbno_body_defer_unsafe` (`bb_match_arbno.cpp:302`),
staged at `emit.cpp:1192` from *the same body span*. The registry ALLOCATES; the staged operand
STEERS. That is the s124 two-reader law / the s68 "spelled-twice disease" in one witness. Fixed by
making one authority (`arbno_reentry_hazard`) that both readers call.

**With both readers widened, the cursor moves to `[rbp-48]/[rbp-44]` — and the witness is STILL RED.**
That is the finding. The asm-diff against the green twin names the residue in one line:

```
GREEN  n0_match_arbno_af:  mov eax,[rbp-44] ; cmp r14d,eax ; jne n7_match_defer_β
RED    n0_match_arbno_af:  mov eax,[rbp-44] ; cmp r14d,eax ; jmp PAT$0_ω
```

**The retreat edge is ABSENT and the `cmp` sets flags nothing reads** — seat4's s184 signature
*verbatim*. So the wrong-span error occurs at **two independent facts**:

1. **`op_arbno_body_defer_unsafe`** — *where the cursor lives*. Fixed here, behind the killswitch.
2. **`op_arbno_body_actframe`** (`emit.cpp:1192`) — *whether the `af`→retreat edge is emitted at all*.
   Still body-keyed: it admits the edge only when the **body span** carries exactly one choice carrier
   (an ALT, an unsealed DEFER, or a tail ARBNO). In this witness the choice carrier is **outside the
   body** — it is the following ALT. Storage without the retreat edge cannot retry, so fixing (1)
   alone can never cure it.

⛔ **THEREFORE THIS SHIPS ARMED AND DEFAULT-OFF, DELIBERATELY.** `SCRIP_ARBNO_REENTRY=1` is correct
and necessary and **not sufficient**; landing it ON would move bytes for zero behavioural gain, which
is pure risk. Default output is byte-identical **by construction** (the authority returns 0 at its
first test, so no candidate enters the registry and count/indices/carve are unchanged) and the next
seat inherits the storage half already built, wired to one authority, and measured.

⛔ **I DID NOT WIDEN FACT (2), AND THE REASON IS MEASURED, NOT TIMID.** seat4 recorded at s184 that
the unguarded `_alt>=1` relaxation *"cures the ladder AND reproduces nf3's rc=124 livelock verbatim"*,
and s126's conviction (`ARBNO(FENCE('a'|'ab')|'c')`) stands. Admitting a choice carrier from **outside**
the body is a wider change than either of those and needs its own witness ladder and its own A/B. It
is one rung, stated precisely below, and it is not one I could close in this row's remaining budget
(RULES END-OF-CONTEXT LAW).

## ⭐ `ptw_min_argpat_arbno` IS **SPLIT** — A DIFFERENT MECHANISM, ON THREE INDEPENDENT LINES OF EVIDENCE

The brief: *"Whether argpat_arbno is the same class is UNKNOWN — first job is the twin-or-not call."*
**It is not the same class.**

`P = mk(ARBNO('a'))` / `'aa' POS(0) *P RPOS(0)` — oracle `match`, SCRIP `nomatch`. Ablation:

| program | verdict |
|---|---|
| `P = mk(ARBNO('a'))` | **RED** |
| `P = ARBNO('a')` (no function) | GREEN |
| `P = mk(LEN(2))` / `mk('aa')` / `mk(SPAN('a'))` | GREEN |
| `mk()` building the ARBNO **inside** the body | GREEN |
| `Q = ARBNO('a')` then `P = mk(Q)` | **GREEN** |
| same as baseline but used inline `P`, no `*P` | **RED** |

So it is **not** the parameter (passing the same ARBNO through the same parameter via a variable is
green), **not** the defer (red without it), and **not** ARBNO generally. The ingredient is **an ARBNO
CONSTRUCTED INSIDE A CALL'S ARGUMENT EXPRESSION**, and the failure is sharp: it matches **0 or 1
iterations and never 2 or more** (`''` green, `'a'` green, `'aa'`/`'aaa'`/`'aaaa'` all red).

**Mechanism.** `sno_is_pattern_rhs` (`lower_snobol4.c:~1894`) has **no `TT_FNC` case** and falls to
`default: return 0`, so a call-valued RHS is not a pattern RHS and no `PAT$` blob is built. The
emitted asm proves the consequence — **the red program contains no `match_arbno` box at all**:

```
RED   boxes: assign call define lit_string match_begin match_defer match_end match_pos match_rpos var
GREEN boxes: … match_arbno match_lit …
```

Three independent confirmations of the split: **(a)** disjoint ingredient sets; **(b)** the red never
reaches the compiled ARBNO path, so it cannot be a frame-slot defect; **(c)** `SCRIP_ARBNO_REENTRY=1`
**moves the witness-1 asm and does not move witness 2's by a single byte.** Different subsystem
(lowerer classification + the runtime pattern path), different rung.

## RECEIPTS

- **Pristine** `make pristine` rc=0 at SCRIP `2cf31532` before any measurement, RT_OPT `-O0`; oracle
  verified alive first. Manual read for both constructs: **p.121** (`ARBNO(PAT)` ≡
  `("" | PAT | PAT PAT | …)`, shy, extended on retry), **pp.121–122 Recursive Patterns** — whose own
  worked example, `ITEM = SPAN(…) | *LIST` with `LIST = "(" ITEM ARBNO("," ITEM) ")"`, is structurally
  this witness, so the shape is not exotic; **p.~4787** call-by-value for witness 2.
- **Corpus watermark UNCHANGED, exact: m3 332/5 · m4 325/11 SKIP=1 (337)** — the row's quoted baseline
  to the digit, fail-set identical by name.
- **Blast radius of the ARM: 0 movers / 399** comparable `.s` across `crosscheck` + `probe/passthru` +
  `demo`. **No corpus program carries the shape** — the same reason seat4's s184 arm had zero movers,
  and the reason this class survived 4.5 months.
- All six `ptw_min_arbno_altsib_*` witnesses from s184 stay **GREEN**; `ptw_min_arbno_alt_fence_L1`
  stays **RED** as s184 recorded (its own reserved rung, untouched here).
- **No new global variables.** One function-local `static int` getenv memo, the identical shape every
  killswitch in this file already uses (`sn4_span_frame`, `sn4_pt_frame`, `sn4_blob_casmark`) and the
  shape `sno_defer_resume` (`lower_snobol4.c:1245`) uses — cited, not assumed.

## ⛔ FOUND BY THE MANDATED REGEN, ATTRIBUTED NOT ASSUMED — seat8's `a2979dc6` LANDED WITHOUT ITS STEP-4 FEATURE REGEN

RULES step-4 (`emit.cpp` was touched, so all five regens run). Four report `No changes`. The fifth,
`util_regen_feature_s_artifacts.sh`, committed **2 files, 9 insertions / 9 deletions** — which
directly contradicted this row's "default is byte-identical" claim and had to be resolved, not waved
at.

**It is not this seat's.** Every changed line moves a retreat target from an **earlier** box to a
**later** one (`n4_match_lit_β` → `n5_match_span_β`, `n9` → `n10`) — which is seat8's *"an element's
resume surface was its FIRST box, not its LAST"* (`a2979dc6`, `SCRIP_SEQ_TAIL`), not an ARBNO
frame-slot change at all. **Convicted in one command:** `SCRIP_SEQ_TAIL=0` reproduces the **old
committed `word3.s` byte-for-byte**, while `SCRIP_ARBNO_REENTRY` changes `word3.s` not at all.

So `a2979dc6` landed its codegen without running the step-4 feature regen, and the drift sat in
`test/snobol4/strings/{word3,word4}.s` until the next seat to touch codegen ran one. The commit
carries this row's name only because this row's regen is what swept it up; its message says so.
⭐ **The general point for the fleet: an unrun step-4 regen is invisible until someone else's rung
inherits it, and it then arrives disguised as that seat's own blast radius.** Mine survived only
because the two-arm killswitch check is cheap enough to run on a surprise.

## NEXT RUNG, STATED PRECISELY

**Widen `op_arbno_body_actframe`'s choice-carrier search from the ARBNO's body span to the ARBNO's
right-hand run inside the same blob** — the immediately-following element if it is a choice node — so
the `af`→retreat edge is admitted when the carrier sits to the right, and aim the edge at that
carrier. It must be a **retarget, not a relaxation**: s126's nested-ALT refusal (`nf1`–`nf4`,
`rc=124` livelock) and seat4's measured "unguarded `_alt>=1` reproduces it verbatim" both stand, and
this widening is strictly larger than the one that broke them. Ladder to reuse: the 22 programs in
this FINDING, of which 5 are red and 17 green, plus `ptw_min_arbno_altsib_*`.

**Two rows asked, not worked:** `argpat-arbno-lower` (witness 2 — no `TT_FNC` arm in
`sno_is_pattern_rhs`; decide whether a call-valued RHS should build a blob, or whether the runtime
pattern path must learn to extend past one iteration) · `optzero-silent-empty` (`SCRIP_OPT=0` prints
nothing on a program whose every path outputs).
