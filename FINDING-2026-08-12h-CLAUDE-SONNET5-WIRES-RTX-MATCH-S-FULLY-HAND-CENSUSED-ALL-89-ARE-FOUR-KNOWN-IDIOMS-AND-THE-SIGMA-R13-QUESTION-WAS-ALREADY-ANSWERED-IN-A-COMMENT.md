# FINDING — WIRES: `rtx_match.S` fully hand-censused, all 89 occurrences map to the four known
# idioms, and the Σ/r13 open question was already answered in the file's own comment

**Session:** Claude Sonnet 5, 2026-08-12, continuing GOAL-SN4-HOME-WIRES.md s35 cursor.
**SCRIP HEAD at read time:** `2913c6a4` (unchanged — read-only session, zero code touched).

## WHAT THIS FINDING IS

s34/s35 left `rtx_match.S` "OPENED, PARTIAL CLASSIFICATION, NOT FINISHED" — ~65 of 89 occurrences
scanned in one pass, not all read by hand, with two things flagged as unresolved: (1) finish the
remaining ~24 occurrences, (2) settle whether the Σ/Σlen GOT-global accesses at lines 296-303,
390-392, 536-538 contradict `GOAL-SN4-HOME.md`'s register contract naming r13 as Σ's home.

This session read the file in full (1182 lines, all functions, all comments) and hand-verified
**every one of the 89 code occurrences** the gate counts (`test_gate_wreg_claim.sh`, re-run first
per the standing INSTRUMENT RULE — confirmed 89 occ / 74 lines, matching the cursor's number
exactly, before doing any hand work). Also confirmed 12 additional occurrences exist only inside
comments (101 raw grep vs 89 code) — expected, not a gate discrepancy.

## METHOD

Extracted every occurrence with a small Python scan against the comment-stripped file (same
`strip_comments` logic the gate script uses), then mapped each stripped-file line back to its
original line number by sequential exact-text matching. Cross-checked the total (89) and spot
locations against the gate's own count before trusting the enumeration.

## CLASSIFICATION — ALL 89, NO NEW IDIOM FOUND

s34's four-idiom taxonomy (momentary GOT-global accessor · GOT-indirect call/tail-call ·
capture-stack block address arithmetic · longer-lived carry) is **exhaustive**. Every occurrence
in the file lands in one of these four buckets, function by function:

| Function | Lines | Occ | Idiom |
|---|---|---|---|
| `rt_cap_match_begin` | 67-74 | 4 | momentary GOT accessor (`g_cap_gen`) |
| `rt_cap_pop` | 88-89 | 2 | momentary GOT accessor (`g_cap_gen`) |
| `rt_cap_top` | 115-116 | 2 | momentary GOT accessor (`g_cap_gen`) |
| `rt_defer_open` | 195-247 | 15 | capture/defer-stack block — r10=`&g_dfx` base, r11=computed slot addr (stride 24), pushed/popped around `NV_GET_fn`/`rt_proc_call_open` |
| `rt_defer_close` | 270-314 | 15 | capture/defer-stack block (r11=peeked slot addr) + 3 sequential momentary GOT accessors (`g_dfx`,`Σlen`,`Σ`) |
| `rt_match_ctx_restore` | 390-393 | 4 | momentary GOT accessor ×2 (`Σ`,`Σlen`) |
| `rt_match_enter` | 522-539 | 6 | momentary GOT accessor ×2 (`g_cap_gen`) + ×4 (`Σ`,`Σlen`) |
| `rt_match_replace` | 777-830 | 11 | longer-lived carry — r11=`sv.slen` extracted early, moved to r12 for the whole analysis block (deliberately not rax, per an in-file bug note); r10=scratch "rs or 0" sentinel |
| `rt_dcap_step` | 958-959 | 2 | momentary GOT accessor (`rt_g_want_name`, exported+preemptible) |
| `rt_defer_get_pat_fn` | 1027-1036 | 4 | GOT-indirect call/tail-call ×2 (`NV_GET_fn`, `dtp_fn_of`) |
| `rt_cap_open` | 1128-1164 | 5 | longer-lived carry (r11=`varname`, popped once, read 36 lines later across an alloc+memcpy) + momentary GOT accessor (`Σ`) |

**Total: 89. Every function accounted for, nothing left unscanned.**

## THE Σ/r13 QUESTION — ALREADY ANSWERED, NOT A CONTRACT DISAGREEMENT

s35 flagged this as "cannot be settled by grep — needs function boundaries + r13 liveness." It
doesn't need a liveness check: `rt_match_ctx_restore`'s own header comment (lines 378-381) states
the design directly:

> "WHAT IT DOES NOT TOUCH: the Σ PIN. r13 is the subject base pointer and the template restores
> it directly; this function syncs only the C-side global mirror that pattern_match.c /
> runtime_eval.c read. Two different stores of the same logical value, and this one is the C
> half. Every blob pin (rbx r13 r14 r15 rbp rsp) is preserved here by construction: the body
> touches rax-class scratch only (r10), never a pin, never the stack."

This is a **deliberate two-copy design**, not a drift between contract and shipping code: r13 is
the hot inlined-path register pin; the GOT-global `Σ`/`Σlen` pair is a C-readable mirror kept in
sync for (a) slow/leaf paths and (b) cross-TU C code that cannot see a register pin at all
(`pattern_match.c`, `runtime_eval.c` — plain C, no access to the emitted graph's register
allocation). r10 touching the mirror in `rt_defer_close`/`rt_match_ctx_restore`/`rt_match_enter`
is momentary scratch that writes the mirror and dies immediately — it never carries Σ anywhere,
never lives across a call, and does not compete with r13's role. Same story applies to the
`rt_cap_open` Σ read at line 1136-1143: one GOT deref, one add, done within a few instructions.

**Conclusion: no contract violation, no drift, nothing for Lon to arbitrate on this specific
question.** The open item can close.

## WHAT THIS DOES AND DOES NOT UNBLOCK

- **`rtx_match.S` census: DONE.** 89/89 hand-classified, matches the gate exactly, no new idiom,
  Σ/r13 question resolved by an in-file comment rather than requiring new investigation.
- **Does NOT change the sweep-surface numbers.** No code touched; `test_gate_wreg_claim.sh --strict`
  still fails the same way (glue emitters don't exist yet, W-3 territory). This is a map, like
  s34/s35's template-side work, not a smaller number.
- **Does NOT resolve the W-0 whitelist-policy question** (product-wide vs. reachability-gated) —
  that is still Lon's call per s35, and this file's occurrences are SN4-reachable so they sit on
  the "must eventually move" side of that question regardless of how it's answered for Prolog.
- **Every occurrence here will need to move off r10/r11 once WREG goes live (W-5 flip).** None is
  currently whitelisted; this file is explicitly the highest-blast-radius surface per the gate's
  own comment ("rtx_match.S is the sharpest edge: it executes DURING a match, i.e. while the
  wires are live").

## NEXT SEAT, IN ORDER (supersedes s35's list item 1, which is now done)

1. **The other 9 RTX `.S` files** (134 occ per the gate: `rtx_icnsub.S` 33, `rtx_alloc.S` 20,
   `rtx_str.S` 19, `rtx_icnvar.S` 13, `rtx_arith.S` 9, `rtx_plcall.S` 10, `rtx_icnagg.S` 11,
   `rtx_icnrel.S` 8, `rtx_icnnum.S` 11) — same hand-census treatment. Note these are mostly
   non-SNOBOL4 (Icon/Prolog) by filename, so the REACHABILITY axis (FINDING-12g) likely applies
   to most of them — check per file, don't assume from the RTX-match precedent that all RTX asm
   is SN4-reachable.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

⛔ W-5 REQUIRES (predicate): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND
`UNBLOCKS: WIRES W-5` on origin. Still FALSE, unchanged this session.

**UNBLOCKS: nothing new for other seats** (this is a completed sub-item of the ongoing RTX census,
not a rung boundary). WIRES W-6 leaf-half proof from s35 still stands, still narrowed to
re-entrant case only.

## ADDENDUM (same session, continued) — `rtx_icnsub.S` (33/33 done) + a REACHABILITY CORRECTION

Read `rtx_icnsub.S` in full (760 lines) and hand-classified all 33 occurrences the gate counts
(verified 33 by independent script, matching `test_gate_wreg_claim.sh` exactly). All five arms
of `rt_subscript_var` covered: RTX-24 (DT_DATA list), RTX-26 (DT_T table by DT_S key), RTX-27
(DT_S substring trap), RTX-28 (DT_A array), RTX-29 (DT_T table by DT_I key), RTX-30 (table-miss
insert trap).

**Classification — one NEW idiom beyond `rtx_match.S`'s four:**

| Region | Occ | Idiom | Role |
|---|---|---|---|
| list-view inline struct walk | 8 | short-lived pointer (struct-field load, not a GOT global) | `t->fields[0]`, list-tag pointer — one load, one deref, dead |
| list-arm bounds check | 3 | local scalar (r11d = element count `n`) | live a few instructions, dead |
| hash-chain walk (`.Lsub_hash`/`.Lsub_chain`) | 10 | **loop-carried pointer** (NEW) — r10=chain link, r11=key cursor, live across loop iterations but NEVER across a `call` | same risk shape as a capture-stack block, but call-free, so arguably lower WREG-flip risk |
| array-arm bounds check | 3 | local scalar (r10d = `a->lo`) | one load, immediate use, dead |
| `.Lsub_table_int` itoa loop | 6 | local scalar/flag (r11d = sign flag) | classic short-lived boolean |

No occurrence touches a wire-relevant global (`g_dfx`, `g_cap_gen`, `Σ`) — this file is aggregate
(list/table/array) cell-carving bookkeeping, one layer below the pattern-match machinery proper.

**⭐ REACHABILITY CORRECTION, SECOND INSTANCE OF THE FINDING-12g PATTERN:** despite the filename
and the header's own "RELEASED to ICON-RTX at s214" ledger language, `rt_subscript_var` is
**SNOBOL4-reachable**. Confirmed structurally, not by name: `src/lower/lower_snobol4.c:376` and
`:779` both emit `IR_SUBSCRIPT` for ordinary SNOBOL4 `X[i]` array/table subscripting (manual
Ch.7). The file's own RTX-28 header independently confirms this in passing ("arrays, which are
SNOBOL4's"). **Filenames and gate-ledger allocation notes are not reliable reachability proxies —
only the lowerer call graph is.** Worth folding into any future W-0 reachability statement
alongside FINDING-12g's `zframe_graph` finding; this is a second, independently-discovered
instance of the same class of error, this time in RTX asm rather than a template.

### NEXT SEAT, IN ORDER (supersedes the list above — `rtx_match.S` and `rtx_icnsub.S` both done)

1. **The other 8 RTX `.S` files** (101 occ remaining per the gate: `rtx_alloc.S` 20, `rtx_str.S`
   19, `rtx_icnvar.S` 13, `rtx_arith.S` 9, `rtx_plcall.S` 10, `rtx_icnagg.S` 11, `rtx_icnrel.S` 8,
   `rtx_icnnum.S` 11). ⛔ Do NOT assume "icn"/"pl" filenames mean not-SN4-reachable — check each
   file's own header for a "C of record" pointer and grep the relevant `lower_*.c` for who calls
   it, the way this addendum did, before treating any of them as excusable by name alone.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

## ADDENDUM 2 (same session, continued) — `rtx_alloc.S` (20/20 done, cleanest file so far)

Read `rtx_alloc.S` in full (173 lines — small file, three functions: `rt_gcheap_alloc`,
`rt_str_alloc`, `rt_agg_alloc`). Verified 20 occurrences by script, matching the gate. No
reachability question here at all — this is the SIL bump allocator every string/aggregate/
workspace block in the runtime is carved from (`rt_agg_alloc` is what `rtx_icnsub.S` calls to
mint every VCELL trap; `rt_str_alloc` backs `rtx_match.S`'s `rt_cap_open`), so it's reachable by
construction from every language, not something to check via a lowerer grep.

**Classification — ONE idiom, simplest file read so far:**

| Function | Occ | Idiom | Role |
|---|---|---|---|
| `rt_gcheap_alloc` | 14 | GOT-global accessor (long-lived within-function) + local scalar | r10=`&g_hp_fr` loaded once, held for the whole fast-path bump sequence but NEVER across a call (function is a leaf); r11=`at`/bump cursor, local scalar, dead by `ret`. |
| `rt_str_alloc` | 3 | same GOT-global accessor, truncated | r10 loaded, then handed off via a same-function tail-jump (`jmp .Lga_armed`), not a call. |
| `rt_agg_alloc` | 3 | same pattern | identical shape. |

Zero calls inside any of the three functions — this file is entirely leaf carve logic. That makes
it the **lowest-risk file of the three read so far** for the WREG flip: r10/r11 here can never
collide with a callee's use of the wires because nothing here calls anything.

### NEXT SEAT, IN ORDER (supersedes the list above — 3 of 10 RTX files now done)

1. **The other 7 RTX `.S` files** (81 occ remaining: `rtx_str.S` 19, `rtx_icnvar.S` 13,
   `rtx_arith.S` 9, `rtx_plcall.S` 10, `rtx_icnagg.S` 11, `rtx_icnrel.S` 8, `rtx_icnnum.S` 11).
   Same treatment — check reachability per file, don't assume from name or from either prior
   file's result.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

**PROGRESS: 142 of 223 total RTX occurrences classified (3 of 10 files: rtx_match.S 89 +
rtx_icnsub.S 33 + rtx_alloc.S 20), 81 remaining across 7 files.**

## ADDENDUM 3 (same session, continued) — `rtx_str.S` (19/19 done) — LONGEST SAME-FUNCTION CARRY FOUND

Read `rtx_str.S` in full (324 lines: `str_concat_d`, its `RTX_MEMCPY` macro, `VARVAL_fn`). Verified
19 occurrences by script, matching the gate exactly. No reachability question — `str_concat_d`
backs ordinary SNOBOL4 string concatenation (`A B`), manual Ch.3 p.21-22 (cited in the file's own
header, including the type-preserving null-identity rule: `(20-17) ''` returns the INTEGER 3, not
a string — confirmed against the same manual section read during orientation).

**Gate-counting note, not a discrepancy:** `RTX_MEMCPY` is invoked twice (lines 175, 179) but its
6 r11 occurrences are counted ONCE by the gate, since it operates on source text before macro
expansion. Correct per the gate's stated scope; worth recording so a future `objdump`-vs-gate diff
isn't misread as drift.

**Classification:**

| Location | Occ | Idiom | Role |
|---|---|---|---|
| `RTX_MEMCPY` macro (8/4/1-byte branches) | 6 | local scalar, copy-primitive half-pair | 2-instruction lifetime, textually once, expands 2x at assembly |
| SXT-token check | 3 | hidden-global accessor + local scalar | momentary |
| **carve/copy sequence (lines 165-207)** | 7 | **⭐ longest same-function carry found so far** | r10=`buf`, r11=`len(al+bl)`, live from just after the ONE `rt_str_alloc` call through to `ret` (~42 lines) — but crossing exactly one call, and that callee (verified in the `rtx_alloc.S` addendum) never touches r10/r11 in a way that would clobber a caller's value across it. |
| SXT re-arm tail | 3 | same carry, tail read-back | same `buf`/`len` |

**Risk note for W-4/W-5:** this carve/copy shape (alloc call → carry ptr+len across the copy →
return) recurs across the family — also in `rtx_match.S`'s `rt_cap_open` and `rt_match_replace`.
Any WREG wire-preservation design that assumes r10/r11 are free to reuse immediately after a call
returns will break this pattern; it needs to be named explicitly as a shape the arena slot or
template save/restore must cover, not just treated as "crosses a call" in the abstract. Folded
into the goal file's W-3/W-4 next-seat note.

### NEXT SEAT, IN ORDER (supersedes the list above — 4 of 10 RTX files now done)

1. **The other 6 RTX `.S` files** (62 occ remaining: `rtx_icnvar.S` 13, `rtx_arith.S` 9,
   `rtx_plcall.S` 10, `rtx_icnagg.S` 11, `rtx_icnrel.S` 8, `rtx_icnnum.S` 11). Same treatment.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout (account for the
   carve/copy carry shape above).

**PROGRESS: 161 of 223 total RTX occurrences classified (4 of 10 files), 62 remaining across
6 files.**

## ADDENDUM 4 (same session, continued) — `rtx_icnvar.S` (13/13 done) — ONE SYMBOL, TWO LANGUAGES, DIFFERENT LIVE ARMS

Read `rtx_icnvar.S` in full (178 lines, single function `rt_assign_var`). Verified 13 occurrences
by script, matching the gate. No reachability question despite the "icnvar" name and the file's
own "RTX-1-ICN" rung label: `bb_assign_var.cpp` — the SNOBOL4 assignment template for ordinary
`X = expr` statements — calls this exact symbol, confirmed via `grep -rln rt_assign_var
src/templates/`.

**Classification — no new idiom, all three prior buckets:**

| Location | Occ | Idiom | Role |
|---|---|---|---|
| GC safepoint check | 2 | momentary GOT-global accessor (`g_gc_pending`) | one deref, dead |
| var-descriptor slen dispatch | 6 | local scalar, reused across 3 compares | r11=`var.slen`, extracted once, tested three times (1/0/2) to pick the arm, dead after |
| `.Lav_nametrap` VCELL cellp store | 5 | short-lived struct-field pointer | r10=`vc->cellp`, loaded/tested/stored-through twice, dead by `ret` |

**Worth recording, not a risk finding but a reachability nuance:** the file's own comments say
Icon's traffic (measured s209b) exclusively drives the `.Lav_nametrap` arm (subscript-lvalue
assignment via VCELL). But since SNOBOL4 shares this same symbol through `bb_assign_var.cpp` for
plain `X = val` on a named global, SNOBOL4 traffic would drive `.Lav_named` instead — a DIFFERENT
arm of the same function. **One shared symbol, two languages, two different live arms.** Neither
arm's r10/r11 usage crosses a call (the two arms that DO call out — `.Lav_named`→`NV_SET_fn`,
`.Lav_sxt`→`rt_sxt_break` — use zero r10/r11, only argument/return registers and explicit
push/pop), so this doesn't change the risk picture, but it's a data point for anyone trying to
build a per-language reachability map of this file rather than a whole-function yes/no.

### NEXT SEAT, IN ORDER (supersedes the list above — 5 of 10 RTX files now done)

1. **The other 5 RTX `.S` files** (49 occ remaining: `rtx_arith.S` 9, `rtx_plcall.S` 10,
   `rtx_icnagg.S` 11, `rtx_icnrel.S` 8, `rtx_icnnum.S` 11). Same treatment.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout (account for the
   carve/copy carry shape from addendum 3).

**PROGRESS: 174 of 223 total RTX occurrences classified (5 of 10 files), 49 remaining across
5 files.**

## ADDENDUM 5 (same session, continued) — `rtx_arith.S` (9/9 done) — SIMPLEST FILE YET, ZERO r11

Read `rtx_arith.S` in full (260 lines: `rt_cmp_d`, `rt_add`, `rt_sub`, `rt_mul`). Verified 9
occurrences by script, matching the gate. `rt_cmp_d` backs SNOBOL4 comparison functions (LT/GT/
EQ/etc.) and is confirmed the #1 hottest C runtime call across every stable benchmark per the
file's own header — no reachability question. `rt_add`/`rt_sub`/`rt_mul` have ZERO r10/r11
occurrences — their DT_I/DT_R fast paths use only rax/rdx/rsi/rcx and xmm registers.

**Classification — one idiom, three repetitions, no new shape:**

| Location | Occ | Idiom | Role |
|---|---|---|---|
| DT_I compare result | 2 | local scalar, branchless sign | r10b=`setl` flag, consumed by `sub r9b,r10b` next instruction |
| string-family combined tag test | 3 | local scalar | r10d=`a.v\|b.v`, tested once, dead |
| string-compare result | 2 | same branchless-sign pattern | r10b=`setb` flag, consumed immediately |
| real-compare result | 2 | same branchless-sign pattern | r10b=`seta` flag, consumed immediately |

**Zero r11 occurrences in this entire file** — everything is r10/r10b/r10d. Every use has a 1-2
instruction lifetime, no pointers, no globals, no calls anywhere near a wire register. Along with
`rtx_alloc.S`, this is one of the two lowest-risk files for the WREG flip.

### NEXT SEAT, IN ORDER (supersedes the list above — 6 of 10 RTX files now done)

1. **The other 4 RTX `.S` files** (40 occ remaining: `rtx_plcall.S` 10, `rtx_icnagg.S` 11,
   `rtx_icnrel.S` 8, `rtx_icnnum.S` 11). Same treatment.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout (account for the
   carve/copy carry shape from addendum 3).

**PROGRESS: 183 of 223 total RTX occurrences classified (6 of 10 files), 40 remaining across
4 files.**

## ADDENDUM 6 (same session, continued) — `rtx_plcall.S` (10/10 done) — FIRST GENUINELY EXCUSED FILE

Read `rtx_plcall.S` in full (202 lines, single function `rt_proc_call_open_det`). Verified 10
occurrences by script, matching the gate.

**⭐ This is the first file in the census where the "Icon/Prolog name means not-SN4-reachable"
assumption actually HOLDS — confirmed structurally, not assumed from the name, precisely because
the two prior corrections (addenda 2 and 4) showed that assumption fails elsewhere.** Checked via
the same method as those corrections: `rt_proc_call_open_det` backs `IR_CALL_PROC_STAGED`, and a
grep of every lowerer confirms that IR kind is emitted ONLY by `lower_prolog.c`, `lower_icon.c`,
and `lower_raku.c` — `lower_snobol4.c` and `lower_pascal.c` have zero references. Also checked
`src/optimizer/proc_collect.c`, the one place `IR_CALL` and `IR_CALL_PROC_STAGED` appear together
in non-lowerer code, to rule out a rewrite path from one to the other — it only reads both kinds
uniformly for name-collection bookkeeping, never converts one into the other. So this file is
confirmed dead for SNOBOL4 by construction, not by filename.

**Classification:**

| Location | Occ | Idiom | Role |
|---|---|---|---|
| `wn` (want-name) extraction/store | 2 | longer-lived local scalar | carried ~26 lines within the function, never across a call in the fast path |
| wire-array offset computation | 6 | local scalar arithmetic chain | `top` scaled by 40 to an array offset, used once, dead |
| cold-arm frame spill around `call rt_pcall_grow` | 2 | **explicit stack-spilled preserver across a call** | r10d pushed to `[rbp-24]`/restored via an explicit frame rather than push/pop, in the rare growth arm only — a new micro-variant of the "preserver" idiom, using a frame slot instead of the stack pointer directly |

**Note for the still-open W-0 whitelist-policy question (s35's "OPEN QUESTION"):** this file is
now a clean, fully-verified test case for whichever way that question gets decided — it is
provably dead for SNOBOL4 (not merely presumed), so if the policy ultimately requires "product-
wide" to mean physically clearing every register mention regardless of reachability, this file's
10 occurrences are unambiguous work items; if reachability-gated licensing is acceptable, this
file is a clean example of what that licensing class would look like.

### NEXT SEAT, IN ORDER (supersedes the list above — 7 of 10 RTX files now done)

1. **The other 3 RTX `.S` files** (30 occ remaining: `rtx_icnagg.S` 11, `rtx_icnrel.S` 8,
   `rtx_icnnum.S` 11). Filenames say Icon — CHECK per-file, don't pattern-match from either
   direction (icnsub/icnvar were reachable; plcall was not).
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

**PROGRESS: 193 of 223 total RTX occurrences classified (7 of 10 files), 30 remaining across
3 files.**

## ADDENDUM 7 (same session, continued) — `rtx_icnnum.S` (11/11 done) — SUBTLER REACHABILITY TRAP

Read `rtx_icnnum.S` in full (157 lines: `rt_coerce_num2_d`, its `SCAN_SIMPLE_INT` macro expanded
twice). Verified 11 occurrences by script, matching the gate.

**⭐ SNOBOL4-REACHABLE — a subtler instance of the reachability trap than addenda 2/4, worth
recording precisely because the mechanism of error is different.** Unlike `rtx_icnrel.S` (whose
header explicitly and correctly claims "Icon-EXCLUSIVE row: zero SNOBOL4... static call sites" —
verified true), this file's header never makes an exclusivity claim at all; it only describes
Icon-corpus measurements and an Icon ledger rung name. I initially read the Icon framing as
implying exclusivity and checked anyway per standing practice: `lower_snobol4.c:181-182` emits
`IR_COERCE_NUMERIC` directly, and `bb_coerce_numeric.cpp` — the template calling
`rt_coerce_num2_d` — has NO language gate before the call. So this file **is SNOBOL4-reachable**.
**The lesson: Icon-flavored measurement data in a header is not an exclusivity claim, and only an
explicit "zero SNOBOL4 call sites" statement (independently verified, as done for `rtx_icnrel.S`
below) should be trusted without its own lowerer check.** Three of four "icn"-named files checked
this session turned out reachable (icnsub, icnvar, icnnum); only `rtx_plcall.S`, whose header made
an explicit and verified exclusivity claim, was genuinely excused.

**Classification — no new idiom:**

| Location | Occ | Idiom | Role |
|---|---|---|---|
| `SCAN_SIMPLE_INT(self)` expansion | 3 | local scalar/pointer | r11=scan pointer, r10b/r10d=sign flag |
| `SCAN_SIMPLE_INT(other)` expansion | 3 | same shape | identical roles, second operand |
| combine/dispatch logic | 5 | local scalar (realness flag) | r10d live across ~10 instructions, dead before either exit |

Zero calls crossed anywhere in the function — every path is straight-line to a `ret`, or a bare
untouched-argument bail to C.

### NEXT SEAT, IN ORDER (supersedes the list above — 8 of 10 RTX files now done)

1. **The other 2 RTX `.S` files** (19 occ remaining: `rtx_icnagg.S` 11, `rtx_icnrel.S` 8). Both
   pre-checked this session and CONFIRMED Icon-exclusive (unlike icnnum): `rtx_icnagg.S`'s
   `rt_size_d` backs `TT_SIZE`, confirmed emitted only by `src/parser/icon/icon_parse.c`;
   `rtx_icnrel.S`'s `rt_jct_relop` backs `IR_BINOP_TEST`, confirmed emitted only by
   `lower_icon.c` (`lower_snobol4.c` has zero references to either). Files themselves still
   need a full hand-read for classification — the reachability check does not substitute for it.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

**PROGRESS: 204 of 223 total RTX occurrences classified (8 of 10 files), 19 remaining across
2 files — both pre-verified reachability, hand-read still owed.**
