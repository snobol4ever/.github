# FINDING — LOWER L-3b STEP-0′: the op_zfc wire really was missing (confirmed), but wiring
# it in with the additive formula the s37 comment describes is NOT sufficient — the RSP
# unwind between MATCH_END's write and MATCH_REPLACE's read targets a runtime-saved mark,
# not a static compile-time delta, and no currently-staged field captures the difference.

**Session:** Claude Sonnet 5, 2026-08-12, LOWER seat only (single session, per s37 resolution).
**Rung:** L-3b STEP-0′ (instrument runtime RSP at MATCH_END's store vs MATCH_REPLACE's load).
**SCRIP HEAD at start:** `05e6b1ae`. **HEAD at end: same — no commit landed, tree clean.**
**corpus/x64 unchanged.**

## 1. Confirmed: `op_zfc` was computed, staged, and printed — but never read

`src/templates/bb_match_replace.cpp`'s cursor/end read formula was, at s37 HEAD:
```cpp
std::string _cur = FR(_.op_off - _.op_zpat);
std::string _end = FRQ(_.op_off + 24 - _.op_zpat);
```
`op_zfc` appears ONLY inside the `SCRIP_REPL_ADDR_DIAG` fprintf on the next line — never in the
arithmetic. The adjacent comment (STEP-6, prior session) describes an "ADDITIVE... matching the
writer's own +op_fc_disp+32 formula" fix, but that description was never translated into code.
This matches the LIVE CURSOR's own honest note — "s37 changed none" — but the comment's framing
("L-3b STEP-6 FIX") reads as though the fix landed. It did not. Flagging this so no later
session re-reads that comment as confirmation the mechanism is wired.

## 2. Traced the real address chain via `--compile` .s output (no gdb, per container limits)

Compiled `l3_spl_len_pure` (PASS, `op_zfc=0`) and `l3_spl_span_nonterm` (FAIL, `op_zfc=16`) to
mode-4 asm and read the raw operands at both the writer (`bb_match_end.cpp`, before its
`mov rsp, [r8+8]` unwind) and the reader (`bb_match_replace.cpp`, after the intervening
replacement-literal node's own `sub rsp, K` push):

| witness | write site (pre-unwind RSP_A) | read site (post-unwind+push RSP_C) |
|---|---|---|
| `len_pure` (PASS) | `[rsp+80]` / `[rsp+104]` | `[rsp+64]` / `[rsp+88]` |
| `span_nonterm` (FAIL) | `[rsp+96]` / `[rsp+120]` | `[rsp+48]` / `[rsp+72]` (old code) |

Both cases have an identical intervening K=16 push (`n{10,11}_lit_string_α`'s `sub rsp,16` for
the one-character replacement literal `'*'`). Using `len_pure` as a **known-correct anchor**
(it passes, so its write and read addresses must be the same absolute byte), I solved:
`RSP_A(len_pure) + 80 == RSP_C(len_pure) + 64` ⇒ the RSP_A→RSP_C delta is `+16` for that witness.

## 3. Applied that delta to span_nonterm — got a plausible-looking, but WRONG, formula

Naively carrying the len_pure-derived delta to span_nonterm predicted the correct read offset
is `op_off + op_zfc` (= 64), which `FR()`'s regime-4 `x86_frame_off` then bumps by `op_zdepth`
(16) to 80 — and 80 is exactly `RSP_A(span_nonterm) + 96 − 16`, i.e. internally consistent with
the SAME `+16` delta. I wired `FR(op_off + op_zfc)` / `FRQ(op_off + 24 + op_zfc)` (falling back
to the untouched `-op_zpat` legacy expression when `op_zfc==0`, so carving-class and every
`op_zfc==0` control stays byte-identical by construction — confirmed: `len_pure`/`len_nonterm`/
`lit_len` stayed PASS through this experiment).

**Built, ran the l3 board: still 3 PASS / 10 FAIL — no net PASS gain.** The failure signature on
the non-carving class changed (e.g. `span_nonterm` moved from a flat DT_I tag misread, `raw_start=3`,
to reading uninitialized/adjacent stack, `raw_start=2044325888`), confirming the *address itself*
did move to where I predicted (`[rsp+80]`/`[rsp+104]`, verified in the recompiled `.s`) — but
**nothing in the emitted instruction stream ever writes to that address.** The writer still only
ever stores at `[rsp+96]`/`[rsp+120]` (RSP_A-relative, unchanged, correctly so). So the predicted
read address, while numerically satisfying the `len_pure`-derived equation, is NOT the byte the
writer produced for `span_nonterm`.

## 4. Root cause of the previous derivation's error — the delta is NOT a constant

Checked why: `len_pure`'s pattern is `LEN(2) LEN(3)` — both `IR_MATCH_LEN` nodes are pure
register arithmetic on `r14d`/`r15d`, **zero RSP touches** between MATCH_BEGIN and MATCH_END.
`span_nonterm`'s pattern is `ANY('+') SPAN('ef') 'g'` — `IR_MATCH_SPAN` does its own
`sub rsp, 16` at its α (to hold its own backtrack-extent save cell, the implicit-alternative
mechanism SPITBOL manual Ch.18 pp.207–8 describes for ARB/BAL-family primitives — SPAN's
"matches longest, shrinks on backtrack" search needs the same kind of retry state) and — on the
success edge to the next primitive — **does not pop that cell**; it rides live all the way to
MATCH_END. `fc_head_fp`/`op_fc_disp` already measures exactly this (16 for span_nonterm, 0 for
len_pure) — but it measures it **only for the WRITE side's own compile-time base** (`op_off +
op_fc_disp + 32`), not for whatever *additional*, differently-shaped RSP growth accumulates
between the write and the read on the OTHER side of the unwind.

The unwind itself (`mov rsp, [r8+8]`) targets `cas_rsp_mark`, a **runtime value** saved once at
MATCH_BEGIN's α (before ITS OWN `sub rsp,32`) — it restores RSP to "however deep the stack was
right after `rt_match_enter` returned," which is graph-shape-independent by design (that's the
whole point of the CAS/pump mechanism: unwind to a fixed mark regardless of how much backtrack
state piled up above it during the match). So RSP_B (post-unwind) is the SAME distance from
RSP_A(match-begin-time) on every witness with the same `op_off` header shape — but RSP_A (the
address the WRITER stores its cursor at) is NOT the same distance from RSP_B, because RSP_A is
measured at MATCH_END time, deep inside however many match-primitive `sub rsp` calls fired
during the match. `len_pure`'s zero and `span_nonterm`'s one (SPAN's uncompensated 16) happened
to let the naive `op_off+op_zfc` formula reproduce the write address by cancellation — but that
cancellation is a coincidence of this SPECIFIC pair, not a general law. A three-primitive or
zero-extra-carve non-carving witness would very likely expose a different residual.

**REVERTED.** `git checkout -- src/templates/bb_match_replace.cpp`; rebuilt; confirmed HEAD
`05e6b1ae` tree clean, l3 board back to 3/10 baseline, byte-identical to session start.

## 5. What the next session needs (do not re-derive)

- **The op_zfc wire genuinely needs writing**, but `op_off + op_zfc` alone is proven
  insufficient by direct counter-example (span_nonterm), not merely unconvincing.
- **The missing term is the WRITE-side's own accumulated match-primitive RSP growth
  BETWEEN MATCH_BEGIN and MATCH_END** — i.e. the sum of `sub rsp,K` from every
  intervening match-primitive node that does NOT pop on its success edge (SPAN confirmed
  one instance; ARB/BAL — per the manual's implicit-alternative mechanism, Ch.18 — are
  the leading suspects for needing the same accounting, and are two of this board's other
  FAIL rows). This is a genuinely different quantity from `op_fc_disp`/`fc_head_fp` (which is
  read at MATCH_END's own emission, reflecting head-level FC-window state) and from `op_zpat`
  (documented for the disjoint carving class). It may need a NEW staged field — a running sum
  computed the same way `g_zd_zunder`/`g_zd_zpat` already backward-scan from IR_MATCH_REPLACE
  to IR_MATCH_BEGIN (emit.cpp:2661's choke), but keyed on match-primitive K rather than
  zd_k of armed ZD nodes.
- **Cheapest next falsifying probe:** find or mint an l3 witness with TWO variable-length
  primitives that each carve their own backtrack cell WITHOUT popping (e.g. `SPAN('a') SPAN('b')`
  chained), and check whether the residual scales with the COUNT of such primitives or is a
  fixed per-graph constant — that discriminates "sum over intervening carvers" from "one
  fixed correction" before spending on the general fix.
- **Do not trust a two-witness A/B as proof of a formula** — the s35 "7th conviction" rule
  (never compare `[rsp+N]` across program points without proving RSP is unchanged between
  them) extends here to: never accept a delta derived from ONE control witness as a constant
  without at least one more witness of a DIFFERENT internal shape to falsify against. This
  session's near-miss is exactly that failure mode, caught only because the emitted `.s` was
  checked before declaring victory rather than trusting the board's PASS count alone (the
  board's FAIL count didn't even change, which is itself the tell — a correct partial fix
  should have flipped at least the single-primitive non-carving rows even if SPAN's extra
  carve remained unaccounted).

## GATE / BOARD STATE (unchanged from s37)
`corpus/probe/l3/` board, m3, SCRIP `05e6b1ae`, x64 oracle newly cloned this session
(`git clone https://github.com/snobol4ever/x64`, binary at `x64/bin/sbl`) —
**3 PASS / 10 FAIL**, controls (`len_nonterm`, `len_pure`, `lit_len`) green throughout.
ZERO emitted-byte change at session end (reverted). m3 only — m4 arm still unmeasured,
BOARD B-0 still owns it.
