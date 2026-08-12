# FINDING — HOME-WIRES s39 (Claude Sonnet 5) — X01's s38-suggested widening is FALSIFIED; no existing
# staged field distinguishes X01 from 10 currently-passing nested-ARBNO probes

**SCRIP `0bbf092b`, corpus `7814057e`, .github `2f3cdae5` (pre-session, unchanged — read-only session,
zero source edits landed).**

## What this session did
Picked up s38's own "suggested next step" for X01 (GOAL-SN4-HOME-WIRES.md LIVE CURSOR): *"widen the
dispatcher gate from `op_arbno_body_defer_unsafe` to the general `!op_arbno_body_k0` case ... a one-line
change at the `bb_match_arbno()` ternary."* Investigated both the literal suggestion and the more targeted
alternative before writing any code, and **falsified both** before landing anything. Net result: zero
source bytes changed, floor re-confirmed identical (`160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,
X10}` — same set as s38, count only moved 159→160 from unrelated LOWER work per s38's own note).

## Finding 1 — the literal `!op_arbno_body_k0` widening is a severe regression, not a one-liner
Checked `op_arbno_body_k0` (the field s38's cursor named) against the 16-probe pat_static=1 passer set
(D09 D10 D11 G19 G20 H21 H24 H25 N12 N17 X02 X03 X04 X05 X06 X11). **Nearly all of them have `k0=0` on at
least one ARBNO node in the statement** (G19 G20 H24 H25 X02 X03 X04 X05 X06 X11 — 10 of 16). `k0=0` is
produced by ANY body member with nonzero `zd_k` — DEFER cells (D09's class, correctly excluded already)
AND nested ARBNO (X02/X03/etc.'s class) both set it, because `zd_k(IR_MATCH_ARBNO)` is unconditionally 16
(confirmed: `zd_k` is in the K16 prelude's own `_sq` exclusion list — emit.cpp ~955, same list W-7's finding
already named). A blanket `!k0` bomb would break 10 of 16 currently-green probes to fix 1 (X01). **s38's
"one-line change" framing undersold the risk; the field is not the right lever.**

## Finding 2 — the more targeted candidate (`op_body_has_arbno`) is ALSO falsified, for a subtler reason
Before abandoning the widen-the-guard approach, checked whether a narrower, purpose-built predicate already
existed: `op_body_has_arbno` (emit.h:601, "SEQ-ERAD s9 nested-ARBNO view-restore gate") — computed by its
own containment scan, semantically exactly "does this ARBNO's body span contain a nested `IR_MATCH_ARBNO`
node." It is currently **staged but orphaned** — computed at emit.cpp:993 inside the `_chain` branch, but
its own consumer (the file-header comment at bb_match_arbno.cpp:12-14) says the mechanism it used to gate
was made UNCONDITIONAL and "arbno_u2_frame() deleted — its guards fire unconditionally," leaving the field
computed with no template-level reader (`grep op_body_has_arbno src/templates/*.cpp` → 0 hits).

Instrumented it directly (temporary diagnostic, reverted before end of session — see below) and confirmed
it IS reliably staged and IS `1` for X01's outer node, `0` for its safe inner node. Looked like exactly the
right lever. **Then checked it against the same 16-passer set and found it is `1` for 10 of them too**
(G19 G20 H24 H25 X02 X03 X04 X05 X06 X11 — the SAME ten probes as Finding 1, because they all genuinely do
contain a nested ARBNO in their body). A blanket `if (op_body_has_arbno) bomb` guard would be the identical
regression as Finding 1, just derived from a different-looking field.

## Finding 3 — X01 and the passing X02/X03/etc. are trace-IDENTICAL on every currently-staged field
Full diagnostic trace comparison (`SCRIP_ARBNO_DIAG=1`, all fields):
```
X01 outer: framed=0 k0=0 sq=0 kk=16 osv=0 | body_has_arbno=1 defer_unsafe=0
X02 outer: framed=0 k0=0 sq=0 kk=16 osv=0 | body_has_arbno=1 defer_unsafe=0
X04 outer: framed=0 k0=0 sq=0 kk=32 osv=0 | body_has_arbno=1 defer_unsafe=0
X06 outer: framed=0 k0=0 sq=0 kk=16 osv=0 | body_has_arbno=1 defer_unsafe=0
G19 outer: framed=0 k0=0 sq=0 kk=16 osv=0 | body_has_arbno=1 defer_unsafe=0
```
X01 is not an outlier on any axis the emitter currently measures. **There is no staged field, alone or in
combination, that separates X01 from its passing nested-ARBNO siblings.** The actual distinguishing
property is structural/semantic, not yet captured by any scan: X01's outer body is `ARBNO(ARBNO(LEN(1)))`
— the outer body span consists SOLELY of the nested ARBNO node, nothing else. X02/X04/X06/G19's outer
bodies wrap the nested ARBNO in other K=0 members (literal delimiters, e.g. `'(' ARBNO(...) ')'`) that
consume frontier in a bounded, single-shot way around it. Whether "body span is purely a single nested
ARBNO with no bracketing K=0 members" is actually the correct discriminator, or merely correlated with the
7 probes sampled, is **not established** — X01 is currently the ONLY probe in the suite with that exact
shape, so there is no positive example to test the hypothesis against, and no negative example among
"purely-nested, should still be safe" to rule it out either.

## Why this seat stopped here rather than writing a narrower scan
Designing and landing a new containment-scan field (a purity check: "is the ENTIRE body span exactly one
IR_MATCH_ARBNO node and nothing else") is possible and would be a small, mechanical addition parallel to
the existing `op_arbno_body_defer_unsafe` idiom (same span, same walk shape) — but:
1. It is unvalidated against more than one positive witness (X01 alone). RULES.md MONITOR-FIRST wants a
   mechanical hunt via the 2-way sync-step monitor before landing a fix; **the monitor is dark in this
   container** (`csnobol4` not built — same MON-CAP gap s38 already flagged, and X01 is precisely the
   wrong-answer-rc-0 class the monitor exists to catch). Diagnosing further by source-reading alone repeats
   s38's own caveat about this exact probe.
2. Per W-4's own status (unstarted, blocks two seats), the *actual* semantically-correct fix for X01 is the
   same anchor-relative-cell layout work W-7's DEFER case needs — a purity-check bomb-guard would be another
   interim honesty patch on top of an already-interim patch, not a fix, and W-4's owner should decide whether
   that's worth doing before the real layout lands or whether it's better to just leave X01 as a known
   silent-wrong-answer regression until W-4 makes it moot.
3. This seat's own s38 scrutiny item 1 is unresolved (ARBNO work routed here vs. belonging to the ARBNO
   template owner) — landing a second guard mid-ambiguity would be the fifth consecutive session on ARBNO
   territory, which s38 itself flagged as needing a Lon decision, not another unilateral session of it.

## Diagnostic instrumentation used this session (added, verified, REVERTED before handoff)
One temporary `fprintf` line added to `bb_match_arbno()` printing `op_body_has_arbno`/`op_arbno_body_k0`/
`op_arbno_body_defer_unsafe` under the existing `SCRIP_ARBNO_DIAG=1` gate. Used to produce Findings 2-3
above, then removed. `git diff` against `SCRIP@0bbf092b` is empty; binary rebuilt clean at HEAD after
revert. No commit made — there is nothing to commit.

## Recommended next steps (not mine to pick unilaterally, per point 3 above)
- **(a)** If Lon confirms this seat should keep the ARBNO thread: land the purity-check field
  (`op_arbno_body_only_arbno` or similar) as a NEW bomb-guard arm parallel to W-7's, same interim-honesty
  shape, same "converts silent wrong-answer to loud refusal" trade — but note X01 is rc=0/wrong-output, not
  a crash, so unlike D12/D13 there is no user-visible harm being prevented by bombing it (the current
  behavior is already silently wrong; a bomb would just make the wrongness loud instead of quiet — a real
  but smaller win than W-7's SIGSEGV-to-abort conversion).
- **(b)** MON-RE (get `csnobol4` building, per s38's standing recommendation) before landing (a) — this is
  now the second session in a row where the wrong-answer-rc-0 blind spot blocked a mechanical hunt.
- **(c)** Defer X01 entirely until W-4 lands, since (per s38) the real fix is the same layout work either
  way and a second bomb-guard is strictly transitional.
- **(d)** Escalate the seat-routing question from s38 (still unanswered) rather than making a sixth
  ARBNO-adjacent judgment call from this seat without it.

## LIVE CURSOR — this session did NOT move the watermark or touch the charter
Floor: **160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}** — identical set to s38, unchanged by
this session (read-only). W-3/W-4/W-6 (the seat's actual charter) remain untouched, now five sessions
running. No commits, no push needed for this session's work (nothing to push — pure investigation,
falsified before landing).
