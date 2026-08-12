# FINDING — WIRES W-2: push/pop guard census — `bb_glue_*.cpp` is EMPTY of the push/pop; it lives
# raw in emit.cpp; the guard asymmetry the stale rung text worried about is NOT reachable, but a
# genuine TEMPLATE-ONLY violation is confirmed and unrelated to W-2's original concern

**Session:** Claude Sonnet 5, 2026-08-12, continuing after the RTX census (FINDING-2026-08-12h).
**SCRIP HEAD at read time:** `2913c6a4` (unchanged — read-only session, zero code touched).

## WHAT THIS FINDING IS

W-2's rung text says: "push guard `flat_jmp_entry` (emit.cpp:2373) vs pop guard `!_wire_stub &&
flat_jmp_entry && flat_pat` (:2806): any graph outside the intersection pushes and never pops =
POP DEBT." The s35 cursor already flagged those line numbers as DRIFTED and gave corrected ones:
"Current guards: pop-side `_blob_wire` at `:2717` (`!_wire_stub && flat_jmp_entry && flat_pat`),
push at `:2716`; related `op_zgpop` at `:842`." Neither prior note had actually opened
`bb_glue_flat.cpp`/`bb_glue_framed.cpp` per the rung's own next-step instruction ("start with a
grep census in `bb_glue_*.cpp`, not emit.cpp"). This session did that.

## STEP 1 — THE CENSUS COMES BACK EMPTY

Read both files in full:
- `src/templates/bb_glue_flat.cpp` (161 lines): `bb_glue_flat_enter/leave`, `bb_glue_outer_γ/ω`,
  `bb_glue_wire_exit` (+ `_γ`/`_ω` wrappers), `bb_glue_pass_wires`, `bb_glue_pass_wires_blob`.
- `src/templates/bb_glue_framed.cpp` (39 lines): `bb_glue_framed_enter/leave`.

**Neither file contains a push or pop of r10 or r11, or of anything else besides `rbp`.**
`bb_glue_pass_wires_blob` (the WREG-mechanism function, dormant/killswitched, W-3's future
customer) uses r10/r11 as `lea` destinations only — no push, no pop, no scratch use. Confirmed by
direct read, not by grep alone (grep for `push`/`pop` mnemonics inside these two files: zero
hits, matching the read).

**The actual r10/r11 push lives as a raw string literal directly inside `emit.cpp`:**
```
emit.cpp:2721   "sub rsp, 8\npush r11\npush r10\n"   -- inside `else if (_blob_wire) { ... }`
```
This is a template-only-law violation in its own right — RULES.md: "Every x86 instruction... 
produced ONLY inside `x86(...)` encoder internals... Templates speak ONLY `x86(...)`, emit ZERO
binary" and separately "Push/pop EMISSION is template-side (TEMPLATE-ONLY law), not emit.cpp." But
it is a PRE-EXISTING violation, not something this census introduces, and W-2's own framing already
anticipated finding it there ("start with a grep census in bb_glue_*.cpp" implies expecting to find
nothing and needing to look elsewhere next — which is exactly what happened).

## STEP 2 — WHERE THE MATCHING POP ACTUALLY IS, AND WHETHER IT'S ASYMMETRIC

The pop is NOT literally `pop r10`/`pop r11` — it is a `mov`-based reload, also raw in `emit.cpp`:
```
emit.cpp:2687-2691   if (g_emit.flat_pat) {
                         "mov r10, qword ptr [rsp + 8]\nmov r11, qword ptr [rsp + 16]\nadd rsp, 32\n"
                     } else { ... pops the frame register instead, a DIFFERENT resume shape ... }
```
Comment at 2687 confirms intent: *"Reload BOTH wires and drop 32B so the resumed interior speaks
the same r10/r11 it was entered with. r10/r11 are DESTINATIONS ONLY — using either as scratch
would destroy the wire it must return through."*

**The guard on the pop (`flat_pat` alone) is textually BROADER than the guard on the push
(`_blob_wire = !_wire_stub && flat_jmp_entry && flat_pat`).** Read naively, this is exactly W-2's
named disease shape — a graph with `flat_pat=1` but `_wire_stub=1` (e.g. a DEFINE-stub proc whose
body carries a pattern, per line 2717's own comment: "a DEFINE'd proc whose body carries a pattern
is pcall-entered, not blob-entered") would never execute the push at line 2721, but naively could
still land at the pop arm and read two uninitialized qwords into r10/r11.

**Traced further, this is NOT reachable — confirmed by checking where `lbl_res` is ever jumped
to, not just where the guard is textually true.** `lbl_res`'s address is pushed onto the stack
(as the resume record's "landing" word) at exactly ONE site in the entire emitter:
```
emit.cpp:2722   "lea rax, [rip + %s]\npush rax\njmp r10\n"   (%s = lbl_res.name)
```
— and that line is itself inside the same `else if (_blob_wire)` branch as the push at 2721. A
grep of every other reference to `lbl_res`/`flat_res_p` in `emit.cpp` and every `src/templates/*.cpp`
file turns up no second site that pushes or jumps to that address. **So the ONLY way execution can
ever arrive at `lbl_res` (and therefore at the `flat_pat`-gated pop arm) is by having first executed
the `_blob_wire` branch's push.** The textual guard asymmetry exists, but the control-flow graph
collapses it: nothing can read the pop arm's stack slots without first having written them via the
exact same branch. **Not a POP DEBT in the sense the rung named it.**

⛔ **THIS IS A STATIC/STRUCTURAL CLAIM, NOT A RUNTIME-VERIFIED ONE.** Per RULES.md's MONITOR-FIRST
doctrine, any actual divergence should be confirmed with the 2-way sync-step monitor, not settled
by reading code alone. What this session did is closer to the RULES.md step (3)-adjacent groundwork
— establishing where to look and what the cheapest discriminating experiment would be — not the
full monitor-based proof. If Lon or a future seat wants certainty rather than a structural argument,
the check is: does any corpus program have `flat_pat=1 && _wire_stub=1` at all? (`_wire_stub`'s
`floor>0` disjunct is specifically DEFINE-stub emission; whether a DEFINE'd proc's body can itself
contain `IR_MATCH_*` nodes making `flat_pat=1` true is a parser/lowerer question this session did
not chase down.) If that combination is unreachable by construction elsewhere in the pipeline, the
grep-based argument above is airtight; if it's reachable, `_wire_stub`'s graphs need to be traced
through to confirm they never reach `lbl_res` some OTHER way this session didn't find.

## STEP 3 — `op_zgpop` (the rung's third named guard, line 842)

Re-read in context (see the RTX census session's earlier full-file read of the region around line
842, unchanged this session). `op_zgpop` is a hand-counted-pop suppression flag, not itself a
push/pop of r10/r11 — it zeroes the "pops owed" count for STF-armed and CLASS-D-blob graphs so a
bracket cut (or the blob's absolute `lea rsp,[rbp+kt]` unwind) does the reclaiming instead of a
per-node counted pop. Not implicated in the r10/r11 asymmetry question; the rung's own text listed
it as "related," which holds, but it is not itself a push/pop guard to unify.

## WHAT THIS DOES AND DOES NOT SETTLE FOR W-2

- **The `bb_glue_*.cpp` census W-2 asked for is DONE and comes back EMPTY** — the push/pop this
  rung is about does not live in template files, contradicting the assumption (shared by the
  original rung text and both s34/s35's citations) that it was a template-side asymmetry to fix by
  aligning two guard expressions inside `bb_glue_flat.cpp`.
- **The specific asymmetry the rung named (push guard narrower than pop guard) is real in the
  guard TEXT but appears unreachable in the control-flow graph**, once `lbl_res`'s single point of
  address-taking is traced. This is a materially different finding than "fix the guard mismatch" —
  if confirmed by a live check, there may be nothing here to fix at all, only a stale/misleading
  pair of guard expressions that happen to never diverge in practice.
- **A genuine, separate TEMPLATE-ONLY law violation is confirmed**: the r10/r11 push/pop (and the
  `lbl_res` address-take, and the DEFINE-stub wire-adopt sequence, and several other raw literal
  x86 fragments in this same region of `emit.cpp`) are emitted as hand-built strings directly in
  the emitter, not through `x86(...)` calls in a template file. This predates this session and
  is far larger in scope than W-2 alone (the whole CLASS-D/CLASS-P/CLASS-ZF exit-glue machinery
  around lines 2680-2900 is written this way) — flagging it here because it's exactly the kind of
  fact a W-2-scoped read would otherwise miss by only checking `bb_glue_*.cpp` and stopping.
- **Not fixed, not touched.** This session made no code changes — matching W-2's own framing
  ("If the CLASS-O/`_wire_stub` design call is still ambiguous after the census, route both arms
  to Lon") — this is exactly that census, with a result that needs a design call, not a quick fix.

## FOR LON — WHAT NEEDS A DECISION HERE

1. **Is the reachability argument above sufficient, or does W-2 want a monitor-based runtime
   confirmation before considering the pop-guard question closed?** The grep-based argument is
   solid on its own terms (traced every reference to `lbl_res`) but doesn't carry MONITOR-FIRST's
   full weight.
2. **Is the raw-literal-asm-in-emit.cpp pattern around lines 2680-2900 something W-2 should also
   own** (moving CLASS-D/CLASS-P/CLASS-ZF exit glue into `bb_glue_*.cpp` or a new template file,
   satisfying TEMPLATE-ONLY), **or is that out of scope for this rung** (a pre-existing, larger,
   separately-tracked debt)? The rung's own charter line only mentions "push/pop guard
   unification," not a full TEMPLATE-ONLY migration of this region.

## NEXT SEAT, IN ORDER

1. **If pursuing W-2 further:** confirm reachability of `flat_pat=1 && _wire_stub=1` (specifically
   `floor>0`, the DEFINE-stub disjunct) via the parser/lowerer — can a DEFINE'd proc's body lower
   to nodes that set `flat_pat=1`? If genuinely unreachable, W-2 may be closeable with this
   FINDING as the record; if reachable, trace those graphs' actual `lbl_res` handling before
   concluding anything.
2. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
3. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout. RTX census complete (see
   FINDING-2026-08-12h) — 193 SN4-reachable / 30 confirmed-excused occurrences, ready as input for
   the register-reassignment design call.
4. **⭐ W-0 whitelist-policy question for Lon** — still open, now answerable with exact numbers
   (see FINDING-2026-08-12h's final summary).

**UNBLOCKS: nothing new** (W-2 census done, design call owed before any code change; W-5's
predicate — `frame_need_of` grep — still empty, unchanged).
