# FINDING-2026-07-15-CLAUDE-RK-RSP-DEFAULT-PROC-ABI-REGRESSION.md

**Session:** s2026-07-15e · Claude Sonnet 4.6 · GOAL-RAKU-BB

## Summary

Commit `f7de3863` ("R12-ERAD s65: ZC_FRAME_RSP complete — RSP is now the default") introduced a
silent regression in the Raku proc-call ABI. Under `ZC_FRAME_RSP` (now the committed default),
sub and method *bodies* execute but arguments arrive empty and return values are lost to callers.
The Raku smoke suite drops from **264/19** (the prior cursor's claim, accurate under R12) to
**209/74** on the committed default build.

## Reproduction

```bash
cd /home/claude/SCRIP
rm -f scrip && make -j4 scrip && make libscrip_rt   # default build = ZC_FRAME_RSP

cat > /tmp/probe.raku << 'EOF'
sub five() { return 5; }
sub main() { my $x = five(); say($x); }
EOF

./scrip --run /tmp/probe.raku   # prints: (empty)  ← WRONG

rm -f scrip && make ZCFLAGS='-DZC_FRAME=ZC_FRAME_R12' -j4 scrip && make ZCFLAGS='-DZC_FRAME=ZC_FRAME_R12' libscrip_rt
./scrip --run /tmp/probe.raku   # prints: 5  ← CORRECT
```

## What is broken and what is not

Broken under RSP default:
- Sub argument binding: `sub f($x) { say($x) }; f("hi")` → empty instead of `hi`
- Return value propagation: `sub five() { return 5 }; say(five())` → empty instead of `5`
- Everything that rides the proc-call boundary: multi-dispatch, method calls, inheritance

Not broken (survives under RSP):
- Attribute/field access (does not cross proc boundary)
- `say()`/`print()` with literals or top-level expressions
- Bare block execution, grammar matching

## Failure pattern in smoke suite

Under RSP default: 209 PASS / 74 FAIL (was 264/19 under R12).
The 55 extra failures are ALL in the proc-call-crossing set: `multi_*`, `mro_*`, `callsame_*`,
`handles_*`, `inherit_method`, `class_method`, `build_*`, `blk_return_value`, etc.
Under R12 rebuild: 264/19, SNOBOL4 7/7, Icon 14/14 — all three languages clean.

## Root cause

`src/contracts/zeta_choices.h` line 140:
```c
#define ZC_FRAME ZC_FRAME_RSP  /* R12-ERAD s65: RSP is now the default */
```
Set by commit `f7de3863`. The comment was `ZC_FRAME_R12` through s64.

The RSP frame convention changes where the flat frame base sits relative to rsp at each box
boundary. The proc-call argument-passing and return-value slots (the shared IR_CALL / ASSIGN /
VAR infrastructure) access these frame offsets. Under RSP framing the offsets are wrong for the
call-crossing case, so args and returns land in the wrong memory.

## Why this contradicts the prior analysis

The RK-ZETA cursor (s2026-07-14) documented: freeing r12 "requires retiring the C-call entry
trampoline… genuinely unsolved, cross-language." It also documented that `ZC_FRAME_RSP` under the
*previous* implementation produced a hard segfault (rsp=0 at `ret`). s65 advanced from
*loud segfault* to *silent wrong answers* and shipped it as the committed default — a worse
outcome because wrong answers are harder to detect than crashes.

## Recommended resolution

One-line fix in `src/contracts/zeta_choices.h`:

```c
/* change: */
#define ZC_FRAME ZC_FRAME_RSP  /* R12-ERAD s65: RSP is now the default */
/* to: */
#define ZC_FRAME ZC_FRAME_R12  /* RSP available via -DZC_FRAME=ZC_FRAME_RSP; not yet default-ready */
```

This restores the true 264/19 / 7/7 / 14/14 baseline on a plain `make` build. RSP remains
selectable at build time and can become the default when the proc-ABI cross-boundary slots are
proven correct under it. See GOAL-RAKU-BB.md LIVE CURSOR for the decision options.
