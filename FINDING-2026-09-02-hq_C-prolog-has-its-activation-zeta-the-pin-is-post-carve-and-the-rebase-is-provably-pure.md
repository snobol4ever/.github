# FINDING-2026-09-02-hq_C-prolog-has-its-activation-zeta-the-pin-is-post-carve-and-the-rebase-is-provably-pure.md

⛔⛔ **PZ-4 CLAUSE (a) IS LANDED. Prolog predicate activations now carry a ζ-ACTIVATION-FRAME in a pinned
base register.** Lon, in-chat to ceo 2026-09-02 09:55, verbatim: *"So what are we waiting for, give Prolog its
activation ZETA like all the rest. OMG! Go fix it."* This is the mechanism, the measured reason for the storage
choice `ARCH-PROLOG-THREE-ZETAS.md` § 3 left to this seat, and the control arm.

## THE HEADLINE NUMBER — the acceptance criterion ceo named, met

hq_B's two-clause `fact/2` witness, `--compile`, comment/`.ascii` lines stripped, pristine `-O0`:

| | rbp-relative lines | rsp-relative lines |
|---|---|---|
| before (SCRIP `cd0ea5a8`, and `SCRIP_PL_ZA=0` on the new binary) | **0** | 173 |
| after (default) | **164** | 13 |

⭐ The 13 survivors are the α carve, the wire-header stores and the ω/γ releases — the instructions that
legitimately speak to the spine. Every ζ operand moved.

## ⭐⭐ THE PROOF THAT MATTERS IS NOT THE CENSUS — IT IS THE PURE-REBASE DIFF

A census says a base register changed. It cannot say the *addresses* did not. Normalising `[rbp ` → `[rsp `
in the pinned `.s` and diffing against the killswitch arm of the SAME binary yields **exactly 10 lines, all of
them the pin itself** — 2 predicate graphs × (1 changed header store + 1 new `mov rbp,rsp`) + 2 graphs × 2 exits
× 1 caller-base restore:

```
<   mov qword ptr [rsp + 552], rbp      >   mov qword ptr [rsp + 552], rsp
<   mov rbp, rsp
<   mov rbp, qword ptr [rsp + 552]      (×2: the γ and ω exits)
```

**Not one ζ offset changed.** The re-homing is an addressing change and nothing else, which is what makes it
gradeable at all — and it is the two-part proof the census alone would have skipped.

## ⛔⭐ THE STORAGE CHOICE, AND THE MEASURED REASON THE DESIGN PAGE ASKED FOR

`ARCH-PROLOG-THREE-ZETAS.md` § 3: *"hq_C decides whether the frame's storage rides the enclosing frame's reserve
(as Icon) or the machine stack directly under RBP, and records the measured reason."*

**Chosen: the machine stack directly under RBP, with the pin taken AFTER the α carve.** The reason is hq_P's
measurement, not a preference. **Icon's rebase is `[rbp + off - ft]` and its exactness rests on one stated
invariant** — `icn_gen_zeta_ft()`'s own comment: *"rsp does NOT move again between α and γ … so `[rsp+off]` and
`[rbp+off-frame_total]` are THE SAME ADDRESS."* hq_P measured that invariant **FALSE** in a Prolog zframe body
(`FINDING-2026-09-02-hq_P-prolog-zframe-breaks-the-pure-rebase-premise…`, `adc17766`): rsp moves **34 times** on
the witness (14 `push`, 1 `pop`, 11 `add rsp`, 8 `sub rsp`) and one of them is a **`pop rsp`** — rsp loaded from
memory — past which the displacement is not merely different, it is **not statically derivable at all**.

⭐ **Pinning AFTER the carve dissolves that whole problem instead of solving it.** `rbp = rsp` at α makes the
rebase plain `off`, with no `ft` term and no per-site rsp-delta to thread through the graph — the "new work, not
a port" hq_B correctly flagged is *not needed* under this arithmetic. It also **dodges parity entirely**: there
is **no `push`**, so the body does not shift by 8 and the two PL-CALL-ALIGN pads
(`bb_call_proc_staged.cpp:739,868`) stay correct rather than being converted from cure into defect.

⭐ **The frame slot the design decision needed was already there and already paid for.** The zframe header is
`[kt-24]=γ [kt-16]=ω [kt-8]=caller`, and `[kt-8]` held this frame's **own** base — a self-anchor that **no code
ever read**. Both epilogues said so in their own comments: *"the [kt-8] slot is WRITE-ONLY on every arm that
fills it (s247)"*. It now holds the **caller's** base. **kt did not grow, no slot was minted, and the parity
question never arises.** The sibling CLASS-C prologue (`xa_flat.cpp:293-297`) had been storing `rbp` there all
along without pinning — the shape was half-built and waiting.

## ⛔ THE KEY IS A REGIME, NOT A LANGUAGE — AND NOT `zframe_graph`

The pin is keyed on a new IR graph property `zframe_pinned_base`, set by `lower_prolog.c` alone.

- ⛔ **Not `zframe_graph`**: three lowerers set it (`lower_prolog.c`, `lower_raku.c`, `lower_pascal.c`). Keying
  the pin there would have silently re-homed **Raku and Pascal** frames to give Prolog its ζ — hq_B's trap 2,
  and the same language-blind widening that cost 47 Icon programs at s272.
- ⛔ **Not `is_prolog`**: `test_gate_emit_no_lang.sh` is blocking and bans that identifier outright.
- ⛔ **Not the design page's `cells_graph` rename either, and this is a deliberate divergence I am flagging
  rather than burying.** § 3 proposes renaming `icn_cells_graph` → `cells_graph` and setting it for every Prolog
  predicate graph so both languages share `icn_gen_zeta_ft()`'s one rebase point. That grant does not carry only
  the rebase — it carries Icon's **region-resident α**, its host reserve and its bcps generator arm, which is
  precisely the widening the page's own ⚠ hazard note at `x86_asm.h:2111` records as having dropped Prolog smoke
  **5/5 → 3/5 both modes**. Prolog's frame and Icon's frame now differ in the one thing the shared arithmetic
  depends on (pre- vs post-carve pin), so one `ft` cannot serve both. **Two regimes, two keys, one shared
  accessor.** If ceo wants the rename anyway, the rebase arms are already separated and it is a mechanical follow-on.

## ✅ THE STUBS ANSWER — which is what § 3 ordered

§ 3: *"a stub that can only say rsp must not remain as a 'shared pin machinery' anyone designs against."*
`x86_fb_pinned()` was `return 0;` and `x86_fb()` was `return "rsp";` — the GOAL named this machinery as PZ-4's
vehicle while it could only ever answer "not pinned". Both now answer, and ⭐ **the spelling is DERIVED from the
number** (`x86_fb() = x86_fb_num() == 5 ? "rbp" : "rsp"`) rather than written twice, which is emit.h's own ONE
DECIDER law — the split that let TEXT and BINARY pick different base registers for one cell at s277.

⭐ **Both ζ addressing families moved together.** hq_P measured at s276 that generator ζ is split across two
families that print **identically** as `qword ptr [rsp + N]`: FR (`FRQ`/`FR`, through `x86_fb`) and SPINE
(`ZRES`/`ZOPQ`, through `x86_zref`). Re-homing one leaves the frame straddling two bases with the half carrying
the value on the wrong one. Both arms are keyed on the same `x86_fb_pinned()`. ⛔ The frame-cache window
(`x86_zop`'s `r == 2`) is deliberately excluded — its offsets are measured from `op_fc_base`, a live rsp anchor,
so rebasing it would be a *different address*, not the same one spelled differently.

⛔ **`x86_frame_off()` drops `op_zdepth` under the pin, and that is the point, not an omission.** `op_zdepth`
compensates for how far the spine has slid below the frame base at a site; under a pinned base it would
double-count. Measured consequence on this witness: **zero offsets changed**, so the term was 0 here — the
correctness argument stands on its own, and the diff proves the arithmetic did not move.

## ✅ CONTROL ARM — a real one, and I am naming why it is real

`SCRIP_PL_ZA=0` on the **same binary** produces a `.s` **byte-identical to the pre-change `cd0ea5a8` build**.
⛔ This is deliberately *not* a two-tree before/after: SCRIP moved `cd0ea5a8` → `d42e7613` mid-session, which
VOIDS a cross-tree arm under the REBASE-BASELINE COROLLARY. A killswitch on one binary is immune to that, and it
is immune to my own s280 mistake — a `git stash` of already-committed files is a no-op, so both arms run the same
tree and two identical numbers read as a false clean confirmation.

## ✅ THE BOARDS — pin ON vs the same binary with the pin OFF, pristine `-O0`, SCRIP `309f5414` (tree `d42e7613` + this change)

| instrument | pin ON | pin OFF (`SCRIP_PL_ZA=0`, same binary) / recorded floor |
|---|---|---|
| `test_smoke_prolog.sh` | **5/5 · 5/5 · 5/5** (m2/m3/m4) | 5/5 · 5/5 · 5/5 |
| `test_prolog_rung13.sh` | PASS=5 FAIL=0 | PASS=5 FAIL=0 (`cd0ea5a8` baseline) |
| `test_prolog_rung14.sh` | PASS=3 FAIL=2 | PASS=3 FAIL=2 |
| `test_prolog_rung15.sh` | PASS=4 FAIL=1 | PASS=4 FAIL=1 |
| `test_gate_pl_m34_parity.sh` | PASS=10 FAIL=2 SKIP=19 | PASS=10 FAIL=2 SKIP=19 |
| Prolog master `ALL.pl` m3 | pass=348 fail=11 crash=3 xfail=1 xpass=8 | **identical** (pin OFF, same binary) |
| Prolog master `ALL.pl` m4 | pass=348 fail=11 crash=3 xfail=1 xpass=8 | **identical** |
| SNOBOL4 board (shared-node arm) | **GATE OK** m3 1679/0 · m4 1679/0 SKIP=0 MISSING=0 | `cd0ea5a8`: m3 1679/0 · m4 1679/0 GATE OK |
| `test_gate_emit_no_lang.sh` | **OK: LANG-BLIND** | — |

⭐ **The pin changes ZERO verdicts on 371 master entries in either mode** — the killswitch arm on the same binary is
the proof, and it is the arm a two-tree before/after could not have given.

⚠ **ceo's 351/351 (fail 8, crash 3, xfail 9) was measured on `9c2c962f`; this tree reads 348/348 (fail 11, xfail 1,
xpass 8) in BOTH arms.** The 3-entry pass→fail delta and the 8 xfail→xpass flips sit in the commits between
`9c2c962f` and `d42e7613` (seat14's exception/static-predicate landings, seat01's builder), **not in this change** —
the pin-OFF arm is byte-for-byte the pre-change emitter and reads the same 348. Attribute by entry on that range;
the names are in the m3 FAIL list below.

**Master m3 entry list on this tree (pin ON; the pin-OFF list is identical by the board above):**

```
FAIL m3 list_directive_2: output mismatch
  FAIL m3 dcg_directive_1: output mismatch
  FAIL m3 assertz_directive_2: output matched but rc=0, expected 1 (declare want_rc if this is correct)
  FAIL m3 assertz_directive_3: output matched but rc=0, expected 1 (declare want_rc if this is correct)
  FAIL m3 assertz_directive_4: output matched but rc=0, expected 1 (declare want_rc if this is correct)
  FAIL m3 dcg_ite_directive_1: output mismatch
  FAIL m3 asserta_assertz_directive_1: output matched but rc=0, expected 1 (declare want_rc if this is correct)
  FAIL m3 dcg_ite_directive_2: output mismatch
  FAIL m3 forall_ite_directive_1: output mismatch
  CRASH m3 findall_directive_replace_3: signal 11
  FAIL m3 findall_directive_replace_5: output mismatch
  CRASH m3 findall_directive_replace_2: signal 11
  CRASH m3 findall_directive_replace_4: signal 11
  FAIL m3 between_ite_naf_1: output mismatch
  XPASS(marker stale, promote it) m3 directive_12: 
  XPASS(marker stale, promote it) m3 directive_13: 
  XPASS(marker stale, promote it) m3 directive_14: 
  XPASS(marker stale, promote it) m3 directive_15: 
  XPASS(marker stale, promote it) m3 cut_directive_2: 
  XPASS(marker stale, promote it) m3 cut_directive_3: 
  XPASS(marker stale, promote it) m3 cut_directive_4: 
  XPASS(marker stale, promote it) m3 cut_ite_directive_1: 
SUITE_BOARD family=ALL total=371 m3_pass=348 m3_fail=11 m3_crash=3 m3_hang=0 m3_unproven=0 m3_skip=0 m3_xfail=1 m3_xpass=8
```

⭐ Four of the eleven FAILs are *"output matched but rc=0, expected 1"* on `assertz_directive_2/3/4` and
`asserta_assertz_directive_1` — the rung13 rc class this row's DONE-WHEN-PROSE already records as PZ-4's
multi-solution family. ⚠ The eight `XPASS(marker stale, promote it)` entries (`directive_12..15`,
`cut_directive_2..4`, `cut_ite_directive_1`) are xfail markers that no longer fail — a corpus promotion owed to
whoever landed the cure, not to this change (both arms read the same 8).

## ⚠ WHAT IS NOT DONE — clause (a) is not the row

⛔ **(a) alone does NOT satisfy this row's DONE-WHEN and must not be read as closing it** (seat02's routing note,
restated). Still unwritten:

- **(c)** the caller's staged-call γ/β landing re-anchoring off its own pinned base — the `x86_bomb` at
  `bb_call_proc_staged.cpp:773` still stands, and its stated blocker (*"the host is still rsp-relative … there is
  no base to re-anchor off"*) is **now false**: the base exists. The bomb text needs updating with (c).
- **(d)** the backtrack path restoring its own base. ⚠ `rt_pl_cp_push`/`rt_pl_cp_pop` (`rt.c:1746-1765`) store a
  **bare code address and no frame base**, so a CP resume into a *different* activation lands with the wrong pin.
  It is no worse than today (rsp was equally wrong) but it is the next real hazard, and it is where clause (d)
  goes: the CP entry becomes {address, base}.
- **(f)** terminal top-graph exclusion, and the `SCRIP_PL_GAMMA_RETAIN` default flip.
- ⚠ The γ/ω releases still `add rsp, kt`, which assumes rsp sits at α at the exit. With a pin available,
  `lea rsp, [rbp + kt]` is exact regardless — deliberately NOT taken in this landing, because it is a behaviour
  change and would have cost the pure-rebase diff that makes this gradeable. It is the cheapest next instruction
  in the rung.

## ⭐ THE GENERAL FORM, for RULES.md if ceo wants it

*A shared accessor is not the same thing as a shared invariant.* Icon and Prolog reach ζ through one pair of leaf
accessors, and it was reasonable to read that as "port Icon's promotion". But the promotion's exactness rested on
a stated premise about rsp that was true for Icon and measurably false for Prolog — and the premise was written in
a comment, not in a check. The port would have compiled, emitted plausible addresses, and been wrong past the
`pop rsp`. **When you inherit a mechanism, inherit its premise explicitly and re-measure it in the new regime;
a premise that lives only in the comment of the function you are copying is the one nobody re-tests.**
