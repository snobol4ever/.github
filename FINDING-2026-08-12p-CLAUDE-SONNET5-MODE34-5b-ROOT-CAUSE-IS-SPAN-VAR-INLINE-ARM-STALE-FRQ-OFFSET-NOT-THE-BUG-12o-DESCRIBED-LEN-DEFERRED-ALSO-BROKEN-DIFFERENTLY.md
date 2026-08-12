# FINDING — 5b root-caused: SPAN(var)'s INLINE arm reads a stale legacy-frame offset inside
# MATCH_BEGIN nesting; NOT the bug 12o described. LEN(*var) independently broken too (crash, not miscapture).

**Session:** Claude Sonnet 5, 2026-08-12c, GOAL-MODE34-IDENTICAL, following FINDING-2026-08-12o.
**Fingerprint:** SCRIP HEAD at session start `f16775ff`, unchanged by this finding (root-caused, NOT
yet fixed — see "What's not done" below). x64 oracle unchanged (`5035571`).

## What this corrects

12o's LIVE CURSOR handed off 5b as: "`POS(0) (SPAN(ws) | '') REM . r` yields `   hello` not `hello`,
identically in both modes post-5a-fix; re-grounded against the manual, unambiguous, SCRIP is wrong."
That framing suggested one bug living somewhere in the `POS`/alternation/`REM`/`.`-capture chain. It
does not. Isolated with minimal probes (all mode-3, oracle-crosschecked):

| probe | shape | oracle | mode-3 | verdict |
|---|---|---|---|---|
| `'   hello' ? SPAN(ws) . r` (ws=' ') | bare dynamic SPAN, no alternation, no POS | `r='   '` | **fails to match at all** | SPAN(var) never succeeds |
| `'   hello' ? SPAN(' ') . r` | bare **literal** SPAN | `r='   '` | **crashes** (`BOMB`, abort) | different bug, masked in the 5b repro |
| `'aabbcc' ? SPAN('ab') . r` | literal, 2-char set | `r='aabb'` | **crashes** (`BOMB`, abort) | same crash class as above |
| `'   hello' ? SPAN('x') . r` | literal, non-matching (clean fail path) | fails | fails, correctly | literal SPAN is fine when it *doesn't* match |

So the 5b repro's `(SPAN(ws)|'')` was masking two separate, independent defects: `SPAN(ws)` (dynamic
charset) always fails outright, so the `|''` alternative always fires and `REM` grabs the whole
subject from position 0 — exactly the `   hello` symptom. The literal-SPAN crash never surfaces in
the 5b repro because the dynamic-arg failure happens first and the literal path is never reached.
**Both are bugs in `SPAN`, not in `POS`, `REM`, `.`, or the alternation operator** — those are exonerated
by the isolation above (t4's clean literal-fail case proves the alternation/anchoring/capture
machinery around SPAN is fine).

## Not a duplicate of FINDING-2026-08-12i

`FINDING-2026-08-12i-...-MATCH-SPAN-ZD-ARM-EAX-CLOBBER...` already fixed a real, different bug in
`bb_match_span.cpp`'s **ZD arm** (`if (_.op_zres && _.op_sa >= 0)`, the `call rt_sg_member` path used
when the SPAN node is cell-armed by the ZD staging system — e.g. inside FENCE/ARBNO-style patterns).
**That fix is confirmed present in the current tree** — I read the live source and it matches 12i's
described fix exactly (position kept in `FR(_.x86_scratch_off)` across the call, `jge L(1)` not
`jge omega` on subject exhaustion) even though `git merge-base --is-ancestor af207c9e HEAD` reports
the literal hash as unknown (the commit evidently landed under a different hash after rebase/push —
the content is what matters and it is live).

**My probe never reaches that arm.** `--compile`'ing t1 (`'   hello' ? SPAN(ws) . r`, a bare top-level
statement, no ARBNO/FENCE) and reading the emitted `.s` shows a *third* code path: the **INLINE guts
arm** (`sp_gi()`, active whenever `ZC_SPAN_GUTS == ZC_SPAN_GUTS_INLINE`, which is the compile-time
default) — a hand-unrolled comparison loop with **no runtime call at all**, structurally unrelated to
the `rt_sg_member`/ZD arm 12i fixed. `op_zres` is 0 for this node (confirmed: the ZD arm's
`x86("comment", "IR_MATCH_SPAN zd")` marker is absent from the emitted text). This is new territory —
12i's own witness set (`063_pat_fence_fn_optional` etc.) all happen to be complex enough to land in
the ZD arm; a bare `SPAN(var)` statement does not.

## Root cause of the "SPAN(var) never matches" defect — measured with gdb, not inferred

`bb_match_span.cpp`'s INLINE arm reads the charset operand via `sp_ndl_r8()`/`sp_ndl_rsi()`, which for
the dynamic case (`_.op_sa >= 0`) spell `FRQ(_.op_sa + 8)` / `FR(_.op_sa + 4)` — the **legacy flat-frame**
accessor family. `x86_asm.h`'s own "ZD-1 — THE FOUR MODES" block-comment names exactly what this means:
mode 4, "LEGACY FRAME — FR/FRQ/FRQB, the whole-graph flat authority for **unconverted families,
untouched**" — i.e. no depth compensation; valid only when nothing has pushed extra stack between
where the operand's cell was written and where it is read.

`IR_MATCH_SPAN` (like every pattern primitive) executes **inside** a `MATCH_BEGIN`/`MATCH_ASSIGN_SAVE`
nesting that legitimately does push transient scratch stack: `MATCH_BEGIN`'s fast path does
`sub rsp, 32` (rsp_mark + start_δ), `MATCH_ASSIGN_SAVE` does `sub rsp, 16`, and `SPAN`'s own preamble
does `sub rsp, 16` before reading its operand — **64 bytes of stack growth between the operand's home
and SPAN's read of it**, none of which `_.op_sa` (computed once via `bb_slot_get(a0)`, a flat-frame
slot number) is adjusted for.

**Measured directly with gdb on the compiled `t1.bin`:**
- Right after `rt_coerce_str_d` writes `ws`'s coerced-string DESCR: address `0x7fffffffea30`,
  contents `{v=0x2, slen=0x1, ptr→0x40128e}` — `x/s` at that pointer prints `" "`. **Correct.**
- At the SPAN loop's `mov r8, [rsp+184]` / `mov r9d, [rsp+180]`: `rsp` has since dropped by exactly
  64 bytes (`0x7fffffffe980` → `0x7fffffffe940`, matching the three `sub rsp` instructions above), so
  `[rsp+184]` resolves to `0x7fffffffe9f8` — **56 bytes short of the actual DESCR at `0x7fffffffea30`**.
  The bytes read there are stack garbage (`0x4210f8108b1b1f8c` / `0x4210efea1b591f8c` — not a valid
  `{v,slen,ptr}` triple by construction). The inner membership loop compares subject bytes against
  this garbage "needle," never matches, and SPAN reports 0 characters — a clean, silent failure on
  every input, independent of subject or charset content.

This is the exact class of defect this codebase's own commentary elsewhere warns about by name
(`emit.cpp`'s C-9 REPL-ZDEPTH note: *"With zdepth=0 all frame reads were short by exactly the subtree
footprint and read stale stack... NOT a constant but the subtree's own zeta depth"*) — except here it
is not `op_zdepth` being wrong, it is that **the accessor used (`FR`/`FRQ`) never consults
`op_zdepth` at all**, by design, per the ZD-1 comment. `IR_MATCH_SPAN`'s `bb_prepare` case
(`emit.cpp` ~1460) sets `op_sa = bb_slot_get(a0)` with no fallback; contrast `IR_MATCH_LEN`'s case
(~1439) which, when `bb_slot_get` fails, falls back to `zls_off(a0)` + `op_zres=1` — a depth-aware
path. `IR_MATCH_SPAN`/`ANY`/`NOTANY`/`BREAK`/`BREAKX` all lack this fallback; in my probe
`bb_slot_get` did **not** fail (it returned 176, a plausible-looking but stale value), so the fallback
would not even have fired had it existed — the bug is not "the fallback is missing," it is that the
primary path silently succeeds with an offset that is only valid outside pattern-match nesting.

## The obvious fix direction is NOT confirmed safe — tested, and it fails differently

The natural hypothesis — give `SPAN` the same `zls_off`/`op_zres` fallback `LEN` already has — is
**not validated by LEN's own behavior in this exact nesting shape**:

```
N = 3
OUTPUT = 'ABCDEFG' ? LEN(*N) . r    :F(FAIL)
```
oracle: `r='ABC'`. mode-3: **crashes** (`BOMB`, abort) — same nesting depth (inside
`MATCH_BEGIN`/`MATCH_ASSIGN_SAVE`), same general shape (dynamic/deferred argument), different failure
mode (crash instead of silent non-match). So `LEN`'s `zls_off`+`op_zres` path is *also* broken in this
context — copying it verbatim to `SPAN` would likely trade a silent-wrong-answer bug for a crash, not
fix anything. Whoever picks this up should root-cause the `LEN(*var)` crash **first** (it's the same
general class, a call-free reproducer, and settles whether `op_zres`/`zls_off` is a safe target for
`SPAN` before spending a session wiring it in).

## Bug B — literal `SPAN('...')` crash — NOT root-caused this session

`'aabbcc' ? SPAN('ab') . r` and `'   hello' ? SPAN(' ') . r` (both go through `sp_gu()`'s
UNROLL/table/chain machinery, `_.op_sa < 0`, the *static* charset arm — completely different code
from the dynamic-arg bug above) both crash with `libscrip_rt: BOMB` in mode-3 whenever the match
actually succeeds; `SPAN('x')` (charset that legitimately fails to match at position 0) runs clean.
So the crash is specific to the **match-succeeds** exit of the static/literal arm. Not investigated
further this session — flagging so the next seat doesn't re-derive the repro from scratch. Minimal
reproducer: `OUTPUT = 'aabbcc' ? SPAN('ab') . r` (single statement, no DEFINE, no alternation).

## What's not done

- **No code fix landed.** This session is root-cause-and-differentiate only, on purpose — the "obvious"
  fix direction (LEN's fallback pattern) is empirically NOT safe to copy without its own investigation
  (see above), and RULES.md's GATE PHILOSOPHY requires crosscheck byte-identity before any codegen
  change is considered done; a hasty patch here risks trading one silent-wrong-answer bug for a crash
  across a wider surface (SPAN/ANY/NOTANY/BREAK/BREAKX all share the pattern).
- Bug B (literal-SPAN-succeeds-then-crashes) is reproduced but not diagnosed.
- The original 5b repro (`repro_5b.sno`, from 12o) itself is not re-tested post-any-fix, because no
  fix has landed; once SPAN(var) is repaired, re-run it — the `POS`/`REM`/`.`-capture machinery
  around it is exonerated by probe `t4` above, so a correct SPAN(var) should make 5b pass outright.

## Next seat, in order

1. Root-cause the `LEN(*N)` crash in this exact nesting shape (cheapest, same-class lead).
2. Only then decide whether `zls_off`/`op_zres` is the right depth-aware target for `SPAN`'s dynamic
   arm, or whether a narrower fix (e.g. carrying `op_zdepth`-style compensation into the legacy `op_sa`
   read specifically for pattern-primitive operands) is safer.
3. Root-cause Bug B (literal SPAN crash on match-success) — independent, can be done in parallel.
4. Re-run `repro_5b.sno` once SPAN(var) is fixed; expect it to pass without further changes.
5. Full crosscheck (both modes) before calling any of the above done, per GATE PHILOSOPHY.

## Session bookkeeping

M34-2/D1 also closed this session (separate, see `GOAL-MODE34-IDENTICAL.md` M34-2 section and its
LIVE CURSOR) — measured, not assumed: `arith_loop.sno` mode-3 vs mode-4 timings agree within noise
(~22-24ms both, `RT_OPT` default `-O0`), the old ~7-8× claim is gone, `rt_gva_island()` already covers
SNOBOL4 mode-3, no driver edit needed.

**⛔ .github repo committed but UNPUSHED at time of writing — credential needed (RULES.md 6b).**
