# FINDING 2026-09-05 hq_U — the gimpel `ERROR 246` class is a PATTERN-OPERAND GLOBAL clobber (independently bisected, converging with hq_C), and the RTCC veneer is ELIMINATED as its cause

**Seat:** hq_U · **Mode:** FLEET-20 · **Tree:** SCRIP `674319235` · corpus `4e11cb9ee` · oracle `/home/resources/x64/bin/sbl -bf`
**Found while:** curing both remaining gimpel `ERROR 246` stack overflows (`HYPHENAT_driver`, `LINE_driver`).

⛔ **THIS DOCUMENT WAS REWRITTEN AFTER ITS OWN FIRST HYPOTHESIS WAS KILLED BY ITS CONTROL ARM.** It first
named the RTCC call veneer's global save block as the cause. That is **measured false** — §7 — and the
section is kept as an elimination rather than deleted, because the hypothesis is structurally attractive and
the next person will otherwise re-derive it.

## 0. The confirmed cause, and the credit

**Pattern operands are parked in ONE GLOBAL PER SYNTACTIC SITE (`PAT$n$V<i>`), and `rt_patv_freeze()`
(`src/runtime/pattern_match.c:1094`) reads them back BY NAME at `SNO$MKPAT` time:**

```c
for (long i = 0; i < n; i++) { char nb[64]; snprintf(nb, sizeof nb, "%s$V%ld", bn, i); v[i] = NV_GET_fn(nb); }
```

An operand whose evaluation **re-enters the same statement** overwrites an earlier operand of the enclosing
activation before that activation's freeze runs. hq_C reached this independently and handed it over as
`pattern-operand-globals-are-one-per-site`
(`FINDING-2026-09-05-hq_C-pattern-operand-globals-are-one-per-site-so-a-recursive-operand-clobbers-the-enclosing-pattern.md`).

⭐ **Two seats bisected to the same statement from opposite ends** — hq_C from a minted witness, hq_U from
the gimpel crash backwards — and the witnesses agree. That convergence is the reason to trust it, and it is
worth more than either bisection alone.

## 0b. ⛔ The cure is NOT written. Two candidates, one already refuted

- **REFUTED, DO NOT REBUILD (hq_C, reverted whole):** freeze from `SNO$MKPAT` call arguments (per-activation
  slots). It cured every witness and kept Icon 15/15 and Snocone 5/5 — **and corrupted `demo_porter`**. A
  diagnostic at a 19-operand site printed `PAT$6$V4 glob(v=2 slen=0) arg(v=86 slen=32766)`: a value node's
  slot is not live for a second consumer. Only the demo set caught it, which is why that control arm is now
  law.
- **UNTRIED (hq_C's candidate):** make the `$V` temps locals of the enclosing `DEFINE` so the existing
  per-activation save/restore covers them. ⚠️ `sno_prologue_add()` (`lower_snobol4.c:1145`) is only an
  emitter **query** (`sno_name_prologue_bound`), not the save/restore, so this means touching the DEFINE
  prototype.
- **A third shape hq_U proposes, not yet built:** leave the stores alone and make the *site* a critical
  region — push `$V0..$V<n-1>` on entry to the pattern-build sequence and pop them after the freeze. The
  inner activation then restores the outer's values on exit, so the outer freeze reads its own operands, and
  the nesting is LIFO by construction. It needs no DEFINE change; it needs two runtime calls emitted around
  the sequence. **Unproven — offered as a candidate, not a recommendation.**

## 1. ELIMINATED HYPOTHESIS — the RTCC veneer's global save block (kept because it is attractive and wrong)

`src/templates/x86/x86_asm.h:12`

```c
extern uint64_t rtccb[32];
```

`x86_rtcc_call()` wraps a runtime call in a veneer that spills the caller's live `r8/r10/r11` **into fixed
offsets of that one global array** and reloads them after the call:

```
mov qword ptr [rip + rtccb+40], r8      ; save
mov qword ptr [rip + rtccb+56], r10
mov qword ptr [rip + rtccb+64], r11
call <target>@PLT
mov r8,  qword ptr [rip + rtccb+40]     ; restore
...
```

⛔ **One block, one instance, for the whole process.** If the callee — directly or through any depth of
indirection — reaches another RTCC-wrapped call, it writes the *same* `rtccb+40/56/64` slots. The outer
frame's reload then reads the **inner** invocation's values. The veneer is not reentrant, and every
recursive SNOBOL4 or Icon program runs through it.

⭐ This is a textbook violation of **THE BB FRAME-PLACEMENT CRITERION** (Lon 2026-08-27): a value stays at a
fixed compile-time offset only while no unbounded growth can intervene between its store and its consumer.
A *call* is exactly such a window — and `rtccb` is worse than a fixed spine offset, because a spine offset is
at least per-invocation while a global is per-process.

## 2. The minimal witness — 12 lines, no patterns beyond `|`, no includes

```
	DEFINE('F(N)')			:(F_END)
F	F = "v" N
	LE(N,0)				:S(RETURN)
	F = F | G(N)			:(RETURN)
F_END
	DEFINE('G(N)Z')			:(G_END)
G	Z = F(N - 1)
	G = "c" N			:(RETURN)
G_END
	P = F(2)
```

`F(2)` must be the pattern `"v2" | "c2"`. Matched at `POS(0)`:

| subject | SPITBOL | SCRIP m3 |
|---|---|---|
| `v2` | matches | **FAILS** ⛔ |
| `c2` | matches | matches |
| `v1` | fails | **MATCHES** ⛔ |
| `c1` | fails | fails |

SCRIP builds **`"v1" | "c2"`**. The left operand of the alternation — `"v2"`, live in an RTCC-saved register
across the `G(N)` call — was overwritten by the recursive inner invocation of `F`, which stored its own `"v1"`
into the same global slot. The wrong value is not garbage; it is *the inner frame's value*, which is the
signature of a shared save area rather than of a stray write.

## 3. Why it is `|` and not the rest of the binary family — and why that is NOT a per-op exemption

`TT_ADD/SUB/MUL/DIV/POW/SEQ/CAT` lower through `sx_binop` to `IR_BINOP`; `TT_ALT` alone lowers to an
`IR_CALL` of `SNO$PBALT` (`src/lower/lower_snobol4.c:402`). Measured with the same recursion shape:
**concatenation and arithmetic are correct, alternation is not.**

⛔ **Do not read that as "the alternation box has a bug."** The defect is in the shared veneer; `|` is merely
the operator whose site happens to keep a live value in `r8/r10/r11` across a wrapped call. Any site with
that register pressure is exposed, in every language. Curing it in `bb_disjunction` would be the
per-op filter RULES.md forbids, and would leave the class open for every other site.

## 4. The chain from here to `ERROR 246`, all measured

The two gimpel crashes are four levels downstream, which is why they were triaged as a stack-overflow class
for so long:

1. `OR(',BLE,CTOR')` accumulates `OR = OR | OR_EXTRACT()` — the witness shape above, with the recursion
   running `OR → OR_EXTRACT → OR`.
2. The clobber makes the accumulated alternation **match the null string**: measured `OR(',BLE,CTOR')` matches
   `""` in SCRIP, and refuses it in SPITBOL.
3. `HYPH_SUFF = OR(UPLO(BALREV(...)))` therefore matches null. Measured directly: SPITBOL's `HYPH_SUFF`
   matches `"noit"` on `"noitanehpyh"` and refuses null; **SCRIP's matches `""` and accepts null.**
4. `HYPH_PAT = HYPH_SUFF @K (*GT(K,MIN) | FENCE *HYPH_PAT) | …` is self-recursive through `*HYPH_PAT` and
   terminates only because each level *consumes input*. With a null-matching `HYPH_SUFF` it recurses at the
   same cursor forever → `ERROR 246 -- stack overflow`.

⭐ **The crash is four levels from its cause, and every level in between looked healthy.** `OR_EXTRACT`'s own
trace (`IC`, `COMMON`, `SUBLIST`, `LIST`) is **byte-identical between SCRIP and SPITBOL at every recursion
level**, and so are the datatypes of every intermediate. Only the *matching behaviour* of the finished
pattern differs. An instrumentation pass that prints values and types — the obvious first move, and the one
already on file — cannot see this defect at all.

## 5. The bisection that isolated it, kept because it is the cheap reproduction

Splitting the accumulator statement **cures the program with no compiler change**:

| variant of `OR`'s loop | SCRIP result |
|---|---|
| `OR = OR \| OR_EXTRACT()  :S(OR_LOOP)F(RETURN)` (shipped) | `OR(',BLE,CTOR')` matches `""` ⛔ |
| `RT_ = OR_EXTRACT() :F(RETURN)` then `OR = OR \| RT_` | correct ✅ |
| splitting the *seed* assignment only | still wrong ⛔ |

Hoisting the call out of the expression removes the live-register-across-a-call window. That is a diagnostic,
**not a cure** — it fixes one source program and leaves the veneer broken for every other.

## 6. Hypotheses measured and ELIMINATED — recorded so they are not re-spent

Each was built, run against both oracles, and killed:

- **Function return-variable save/restore across recursion is broken.** No: `G = "a"; Z = G(N-1); G = G "b"`
  returns `ab` in both, and the pattern-valued twin agrees.
- **A failing function call on the RHS still performs the assignment.** No: `V = V "x" FAILS()` leaves `V`
  intact in both, for string and pattern left operands alike.
- **The alternation captures its left operand by reference, so the self-assignment makes it self-referential.**
  No: plain and function-nested accumulations agree in both.
- **hq_C's ζ-depth collapse in `bb_match_capture`.** Its own §1 witness passes on today's tree, and the
  outer-capture-over-inner-capture shape from `OR_EXTRACT` (`LIST ANC (BAL . IC SEIZE) . COMMON`) is correct
  in both — while the crashes persist.

## 7. ⛔ THE RTCC ELIMINATION — built, measured, reverted

The §1 hypothesis was implemented in full and killed by its own control arm. Recorded so nobody rebuilds it.

**What was built:** `x86_rtcc_wb_*`/`x86_rtcc_rl_*` rewritten to spill `r8/r10/r11` to the caller's own stack
(`sub rsp, 32` / `mov [rsp+N], rN` / call / reload / `add rsp, 32`; 32 bytes keeps the 16-byte alignment
`x86_align_assert()` depends on for any subset of the mask), both media, with `r9` deliberately left on the
global block because it carries the GVA base — a program-wide constant, not per-invocation state. Shipped
behind `SCRIP_RTCC_STACK=0` so the control arm could be a killswitch A/B.

**Proof the arms were real, not a no-op:** the toggle changes the emitted `.s` — 40 stack-save instructions
appear and `rtccb+40` references drop from 50 to 12 (the residue being the r9 GVA reloads).

**The measurement:** the witness of §2 is **byte-identical on both arms, in both modes.**

| | `v2` | `c2` | `v1` | `c1` |
|---|---|---|---|---|
| oracle | match | match | fail | fail |
| m3 and m4, `SCRIP_RTCC_STACK` unset (cure) | **FAIL** | match | **MATCH** | fail |
| m3 and m4, `SCRIP_RTCC_STACK=0` (baseline) | **FAIL** | match | **MATCH** | fail |

**Reverted whole** (`git checkout -- src/templates/x86/x86_asm.h`); no edit stands.

⭐ **Why it was worth killing explicitly rather than quietly dropping.** `rtccb[32]` *is* a process-wide save
area written across calls, and "therefore recursion clobbers it" is a sound-sounding inference that predicts
exactly the observed symptom. It is still not the cause here. The general form is this project's own
recurring lesson in a new place: **a mechanism that could produce the symptom is not evidence that it did.**
The only thing that separated them was building it and running the witness — reading the code could not, and
did not.

⚠️ **A real hazard is nonetheless on file, and it is NOT this row.** Whether `rtccb` is reentrant at all is an
open question this measurement did not answer — it showed only that the alternation witness does not depend
on it. If some other site does keep a live value in `r8/r10/r11` across a recursive wrapped call, the global
block would corrupt it. That wants its own witness before anyone calls it safe **or** broken; no row is
minted for it here because no witness exists, and a row without one would be a guess wearing a topic name.

