# FINDING — 5b root-caused: SPAN(var)'s INLINE arm reads a stale legacy-frame offset inside
# MATCH_BEGIN nesting; NOT the bug 12o described. A SEPARATE, unrelated "unhandled" stub for
# `var = subject ? pattern` was initially misattributed to SPAN — corrected in-session, see below.

**Session:** Claude Sonnet 5, 2026-08-12c, GOAL-MODE34-IDENTICAL, following FINDING-2026-08-12o.
**Fingerprint:** SCRIP HEAD at session start `f16775ff`, unchanged by this finding (root-caused, NOT
yet fixed — see "What's not done" below). x64 oracle unchanged (`5035571`).
**Correction note:** this finding was revised in place, before push, after two of its own initial
conclusions ("literal SPAN also crashes" and "LEN(*var) is independently broken") turned out to be
artifacts of a shared test-wrapper bug rather than properties of SPAN or LEN — see the "RETRACTED"
sections below. Left visible rather than silently rewritten so the reasoning trail is honest.

## What this corrects

12o's LIVE CURSOR handed off 5b as: "`POS(0) (SPAN(ws) | '') REM . r` yields `   hello` not `hello`,
identically in both modes post-5a-fix; re-grounded against the manual, unambiguous, SCRIP is wrong."
That framing suggested one bug living somewhere in the `POS`/alternation/`REM`/`.`-capture chain. It
does not. Isolated with minimal probes (all mode-3, oracle-crosschecked; the last two rows use a
DIFFERENT statement wrapper than the first two — see the retraction below for why that matters):

| probe | shape | oracle | mode-3 | verdict |
|---|---|---|---|---|
| `'   hello' ? SPAN(ws) . r` (ws=' ') | bare dynamic SPAN, no alternation, no POS | `r='   '` | **fails to match at all** | SPAN(var) never succeeds — Bug A, this is 5b's actual cause |
| `'   hello' SPAN(' ') . r` (bare match, no `var=` wrapper) | bare **literal** SPAN | `r='   '` | matches correctly | literal SPAN is fine |
| `X = 'ABCDEFG' ? 'ABC' . r` (wrapped, SPAN-free control) | trivial literal match, `var=subject?pattern` wrapper | `r='ABC'` | **crashes** (`BOMB`, abort) | the wrapper is broken, not any pattern primitive |
| `'   hello' ? SPAN('x') . r` | literal, non-matching (clean fail path) | fails | fails, correctly | exonerates alternation/anchoring/capture |

So the 5b repro's `(SPAN(ws)|'')` is masking exactly ONE defect, not two: `SPAN(ws)` (dynamic
charset) always fails outright, so the `|''` alternative always fires and `REM` grabs the whole
subject from position 0 — exactly the `   hello` symptom. **The bug is in `SPAN`, not in `POS`,
`REM`, `.`, or the alternation operator** — those are exonerated by the clean literal-fail case above.
A second, real bug exists (the `var=subject?pattern` wrapper crash) but it is unrelated to SPAN, to
5b, and to any pattern primitive — see the corrected "Bug B" section far below; my first pass
conflated the two because every one of my initial SPAN probes happened to share that wrapper.

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

## The obvious fix direction: retracted a false negative here too — LEN(*var) is fine

An earlier pass reported `LEN(*N)` as *also* crashing in this nesting shape, which would have ruled
out copying its `zls_off`/`op_zres` fallback pattern to `SPAN`. **That test was contaminated by the
same `var = subject ? pattern` wrapper bug documented in the corrected "Bug B" section below — not a
LEN defect.** Retested with the wrapper removed:
```
N = 3
'ABCDEFG' ? LEN(*N) . r    :F(FAIL)
OUTPUT = 'r=' r
```
mode-3: `r=ABC`, **matches the oracle exactly**. `LEN(*var)`'s deferred arm (the by-NAME
`rt_pat_prim_int(varname)` runtime fetch, `bb_match_len.cpp`) is correct and uninvolved in either bug
in this finding. So the fix-direction question is open again in a more favorable state than the
retracted paragraph suggested: `LEN`'s fallback is a validated-working reference implementation,
not a second broken thing to route around. Whoever picks up `SPAN`'s fix should look closely at why
`LEN`'s by-NAME approach sidesteps the stack-offset problem entirely (it never touches `_.op_sa`/`FRQ`
for the deferred case) and whether the same by-name strategy — rather than `zls_off`/`op_zres`
specifically — is the more directly applicable pattern for `SPAN`'s dynamic charset.

## Bug B RETRACTED — was a misdiagnosis, corrected within this same session before push

An earlier draft of this finding reported literal `SPAN('...')` as crashing on match-success and
filed it as an independent "Bug B." **That is wrong and is retracted here** (caught before push —
no one built on the bad framing). All of the Bug-B probes (`'aabbcc' ? SPAN('ab') . r`,
`'   hello' ? SPAN(' ') . r`) share a detail I didn't control for: they all wrap the match in
`var = subject ? pattern` — the SPITBOL/SPITBOL+ "?" expression form used as an assignment RHS.
Control probe, SPAN removed entirely:
```
X = 'ABCDEFG' ? 'ABC' . r    :F(FAIL)
```
**crashes identically** — same `BOMB`, same `n7_assign_α` site, same garbage message bytes — with
the simplest possible literal pattern and zero SPAN involvement. And the SPAN-only control with the
`var=` wrapper removed:
```
'   hello' SPAN(' ') . r    :F(FAIL)
```
**matches the oracle exactly** (`r='   '`). So literal `SPAN` was never broken; the crash is 100%
attributable to `var = subject ? pattern`, independent of which pattern is used. See the new section
below for the actual root cause. Lesson for future probes in this file's tradition: when isolating a
suspected primitive's bug, vary the WRAPPER (assignment idiom, statement shape) independently of the
primitive, not just the primitive's arguments — my first pass held the wrapper constant across all
SPAN probes and mistook a wrapper-level defect for a SPAN-level one.

## The real Bug B: `var = subject ? pattern` (assign a match-expression's result) is an unimplemented arm, not a subtle bug

Root cause, precisely, no inference needed — this is a self-documenting stub, not a memory bug:

`bb_assign_global.cpp` (identical shape in `bb_assign_var.cpp`/`bb_assign_local.cpp`):
```c
if (!(PLATFORM_X86 && (_.op_zres || (_.op_a_slot >= 0 && _.op_off >= 0))))
    return x86_alpha() + x86_bomb((std::string("bb_assign_global: unhandled ...") + ...).c_str());
```
For `X = 'ABCDEFG' ? 'ABC' . r`, neither disjunct is ever true: nothing upstream (LOWER / the
emit-drive operand-staging pass) ever grants an operand slot for a match-expression used as an
assignment's RHS value — not the ZD cell path (`op_zres`), not the legacy flat path (`op_a_slot`/
`op_off`). `x86_bomb` is the codebase's own established, deliberate "declined to emit an unsound or
unimplemented arm" convention (dozens of call sites across `src/templates/`, e.g. `bb_activate.cpp`,
`bb_bound.cpp`, `bb_call.cpp` — this is not special to assign or to patterns). The `n7_assign_α` label
in the compiled `.s` is a literal, unconditional `lea rdi,[rip+.S1]; call rt_bomb@PLT; ud2` — an
intentional trap, confirmed by reading the emitted text directly, not inferred from behavior.

**This is architecturally a missing feature** (`var = subject ? pattern` was apparently never wired
into the operand-slot-resolution machinery for ANY pattern shape), not a memory-safety or
offset-computation defect like Bug A above. It fires identically for mode-3 and mode-4 (both share
the same `bb_assign_global`/`x86_bomb` code), for global and local targets (t8: `OUTPUT=`, t9: plain
global `X=` — same crash), and independent of pattern complexity (literal 3-char match is enough).

**Secondary, lower-priority bug found along the way:** the bomb's own diagnostic message is garbage
bytes (`"\242\340\003"` observed, not `"bb_assign_global: unhandled ... var=X"` as the source implies
it should read) — something is passing a bad pointer into `x86_bomb`/`bomb_text`/`bomb_bytes` for
this call site specifically. Not investigated (it only affects error-message readability, not
program correctness — the bomb still correctly aborts either way), but worth a `grep -rn` sweep of
`x86_bomb` call sites building a message via `std::string(...).c_str()` if the pattern recurs
elsewhere, since a garbled diagnostic wastes the NEXT session's time re-deriving what should have
been printed for free.

**Not the 5b repro's mechanism.** `repro_5b.sno` uses replacement syntax
(`s POS(0) (SPAN(ws)|'') REM . r  =`, an implicit-empty-RHS replacement assigning into `s` via the
match's side effect), not the `var = subject ? pattern` expression form — confirmed by the fact 5b
never crashes, it silently miscaptures (Bug A's actual symptom). The two bugs are independent; 5b's
fix path runs through Bug A only.

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

1. Fix `SPAN`'s dynamic-charset INLINE arm: either give it a by-NAME fetch like `LEN(*var)`'s
   `rt_pat_prim_int`-style mechanism (validated working, see above), or a properly depth-compensated
   stack read. Either way, validate against `LEN`'s working reference rather than assuming.
2. Re-run `repro_5b.sno` once `SPAN(var)` is fixed; expect it to pass without further changes (`POS`/
   `REM`/`.`/alternation are all exonerated by probe `t4`/`t10`).
3. Separately: wire operand-slot resolution for `var = subject ? pattern` (the real "Bug B",
   `bb_assign_global.cpp`/`bb_assign_var.cpp`/`bb_assign_local.cpp`'s `x86_bomb` "unhandled" arm) —
   independent of item 1, can be done in parallel by a different seat. Low-priority side item: fix the
   garbled bomb-message pointer at the same call site while in the file.
4. Full crosscheck (both modes) before calling any of the above done, per GATE PHILOSOPHY.

## Session bookkeeping

M34-2/D1 also closed this session (separate, see `GOAL-MODE34-IDENTICAL.md` M34-2 section and its
LIVE CURSOR) — measured, not assumed: `arith_loop.sno` mode-3 vs mode-4 timings agree within noise
(~22-24ms both, `RT_OPT` default `-O0`), the old ~7-8× claim is gone, `rt_gva_island()` already covers
SNOBOL4 mode-3, no driver edit needed.

**⛔ .github repo committed but UNPUSHED at time of writing — credential needed (RULES.md 6b).**
