# SB-6.E.7-J pass #2 — Consolidated findings (2026-05-02 #13)

**Session:** 2026-05-02 #13, Claude Sonnet
**Files audited line-by-line against .inc/.sno:** 12 of 17
**Files remaining:** XDump.sc, TDump.sc, tree.sc, global.sc, beauty.sc

This document is the working record for SB-6.E.7-J pass #2. It captures the
corrected translation principle, the systemic findings, and per-file deltas.
It exists so the next session does not re-derive the work already done.

---

## The translation principle (per Lon, session 2026-05-02 #13)

Take the .sno/.inc source. Mentally erase `:F()` / `:S()` / `:(label)` /
goto-label control plumbing — what remains is a stream of **code body parts**:
assignments, expressions, pattern matches, function calls, conditional-RHS
forms. Those body parts go into the .sc port **unchanged in name and content**.
Then wrap them with structured control: `if/else`, `while`, `for`, `break`,
`return`, `freturn`, `nreturn`. Drop the `:F()/:S()` statement-based branching.

This is a **one-to-one body-part correspondence**, not a reinterpretation.
The control envelope is new and shiny; the bodies are identical.

**Implication for IR:** the IR for *expressions* should be byte-identical
between .sc and .inc. The IR for *control flow* may differ (different
envelope). Sync-step tracing between the two is not required for SB-6 to
land; it remains a future option if non-byte-identical IR proves hard to
converge.

**Implication for niceness:** "faithful AND nice." Drop SNOBOL4 cosmetic
spacing/alignment. Strip braces around single-statement bodies. Use natural
Snocone idioms. But never restructure expressions, never rename identifiers,
never invent helpers without flagging them.

---

## Systemic findings — runtime / capability gaps surfaced by the audit

These are NOT .sc bugs. They are runtime / Snocone-language capability gaps
that the .sc port papered over. Per RULES.md ("never patch corpus source to
work around runtime bugs"), each is a **runtime work item**.

### G-1. `REPLACE(DATATYPE(x), &LCASE, &UCASE)` wrapper

**3 sites:** `assign.sc:5`, `ShiftReduce.sc:46`, `ShiftReduce.sc:49`.

The .inc form is plain `IDENT(DATATYPE(t), 'EXPRESSION')`. The .sc wraps
DATATYPE in a REPLACE-to-uppercase. scrip's runtime `datatype()` already
returns uppercase strings (`"EXPRESSION"`, `"INTEGER"`, etc., per
`src/runtime/x86/snobol4.c:2427`). So the REPLACE is either:

(a) Doing nothing useful — strip with no functional change.
(b) Compensating for the Snocone lex layer case-folding the string literal
    `'EXPRESSION'` → `'expression'` at parse time.

**Verify:** build scrip, run `OUTPUT = IDENT(DATATYPE(2.0), 'REAL') 'YES'`
and observe whether 'REAL' literal survives lex. If yes, strip all REPLACE
wrappers. If no, fix lex to preserve string-literal case (per RULES.md
"Casing belongs at the ingress layer").

### G-2. Predicate-form `?` discards captures

**Drives the 2-step capture-then-consume idiom in:**
- `ReadWrite.sc::Write` (lines 50-51, 56-57)
- `ReadWrite.sc::LineMap` (lines 74-75)
- Several sites in `Gen.sc`, `Qize.sc`, others

The .inc form is one statement: `subj POS(0) PAT . capvar = :S(...)F(...)` —
pattern-match-with-capture-and-replace, with statement-success/failure
flow. Snocone's emitter property: `if (subj ? PAT)` tests match success
but **discards** the capture-into-name (`. capvar`) even on success. So
the .sc port writes two statements: first a predicate-form match (capture
visible in scope), then a destructive replace.

**Documented as "Snocone emitter property" in ReadWrite.sc:6-12, Qize.sc:13-16.**
Needs Lon's call: intentional or runtime bug?

If intentional → leave the 2-step idiom, document it once in ARCH-SNOCONE.md,
remove the per-file repeat-comments.
If bug → fix the emitter to preserve captures in predicate-form, restore
single-statement form in .sc.

### G-3. Deferred-`*assign(.var, *value)` inside pattern alternations

**1 site:** `Qize.sc::Qize` branch 1 (lines 40-48).

The .inc form embeds `*assign(.part, *'bSlash')` etc. inside a pattern
alternation, capturing the **name string** directly via deferred-call. The
.sc port matches the **char value** then dispatches in code with
`if (IDENT(part, bSlash)) Qize = Qize 'bSlash'` etc.

This is an expression-level translation deviation. The .inc form is more
elegant but requires runtime support for deferred-`*assign` inside
alternations. May be the same root issue as G-2 (predicate-context capture).

### G-4. SPITBOL builtin `LEQ` not in scrip Snocone

**Defined in:** `Qize.sc:21-25`, used in: `Qize.sc`, `omega.sc`, `beauty.sc`.

`LEQ(a, b)` (lexical-EQual or less-than-or-equal) is a SPITBOL builtin
(listed at beauty.sno:88 alongside IDENT, INTEGER, ITEM, etc.). It is
referenced in patterns via `*LEQ(...)` but never DEFINEd in canonical .inc
files because canonical assumes the SPITBOL runtime provides it.

The .sc port provides a user-defined `LEQ` to fill the gap. **Justified
as a runtime helper** per the audit table.

### G-5. `Ucvt` referenced in canonical, never defined

**Defined in:** `Qize.sc:27-30`, referenced in `Qize.inc:69`.

Canonical Qize.inc references `Ucvt(iq)` to convert a 2-hex-char string
to a CHAR. Never DEFINEd in canonical .inc/.sno. Either the canonical
relies on an external .inc not in the beauty/ folder, or it's a known
gap. **Justified as a runtime helper** per the audit table.

### G-6. Snocone has no infix-operator OPSYN

**Tracked as SB-6.E.7-B (open).** Affects: `semantic.inc:7-8`:
```
OPSYN('~', 'shift', 2)
OPSYN('&', 'reduce', 2)
```

Per Lon (session 2026-05-02 #13): **DO NOT drop these. Keep all OPSYN
processing.** The current `semantic.sc` omits them entirely; that's wrong.
Either keep the OPSYN calls so they survive to the day SB-6.E.7-B lands,
or carry as commented-out lines with a `// TODO SB-6.E.7-B` marker.

Function-form fallback (`shift(p, t)` instead of `pat ~ 't'`) is a
caller-side workaround, not a reason to delete the OPSYN definitions.

---

## Translation infidelities (NOT systemic — per-file fixes)

### F-1. `trace.sc:15` — polarity inversion still present

Pass #1 (session #11) thought it fixed the doDebug==1 branch by replacing
the workaround `if (str ? PAT) { } else { nreturn; }` with the
"natural form" `if (~(str ? PAT)) { nreturn; }`. **Both forms have the
same (wrong) polarity.**

The .inc says: when `doDebug == 1` and `str matches POS(0) '?'`,
`:S(NRETURN)` — i.e., **suppress `?`-lines**.

The .sc says: `if (~(str ? PAT)) nreturn;` — i.e., suppress non-`?`-lines.

**Faithful form** (after SB-6.E.7-A bare-if landed):
```snocone
if (str ? (POS(0) '?')) nreturn;   // suppress ?-lines, .inc :S(NRETURN)
```

The wrong-polarity comment on .sc line 14 (`"// doDebug == 1: only show
'?' lines"`) corroborates the inversion.

**Test impact:** session #6 originally noted that fixing the polarity
caused fingerprint regression to lines=785. SB-6.E.7-A has since landed
(session #82) and current fingerprint is already lines=785. Fix should
now be safe to apply.

### F-2. `Gen.sc::GenTab` — reimplemented, not ported

**.inc:**
```
GenTab         GenTab         =  .dummy
               pos            =  IDENT(pos) $'#L'
               $'$B'          =  $'$B' ' ' DUPL(' ', pos - SIZE($'$B') - 1)         :S(NRETURN)
               $'$B'          =  $'$B' ' '                                          :(NRETURN)
```

Two body parts:
1. `$'$B' = $'$B' ' ' DUPL(' ', pos - SIZE($'$B') - 1)` — try-extend statement
   that fails when DUPL gets negative arg.
2. `$'$B' = $'$B' ' '` — fallback append.

Wrapped: try part 1; if it succeeds, NRETURN; else do part 2 and NRETURN.

**.sc current (53-66):** invents an `IDENT($'$B')` first-time branch
substituting `$'$X'` for `$'$B'`, plus an explicit `LE(SIZE($'$B'), pos - 1)`
test reasoning about WHEN the .inc statement would fail. Not in canonical.
A reimplementation, not a port.

**Faithful port** (per body-part principle):
```snocone
function GenTab(pos) {
    GenTab = .dummy;
    if (IDENT(pos)) pos = $'#L';
    // Try part 1 — succeeds only when pos - SIZE($'$B') - 1 >= 0
    if (LE(SIZE($'$B'), pos - 1)) {
        $'$B' = $'$B' ' ' DUPL(' ', pos - SIZE($'$B') - 1);
        nreturn;
    }
    // Part 2 fallback
    $'$B' = $'$B' ' ';
    nreturn;
}
```

The `IDENT($'$B')` branch and the `$'$X'`-substitution must be removed —
they have no analog in .inc. **Note:** even the `LE(SIZE, pos-1)` guard is
arguably an interpretation; ideally Snocone supports SNOBOL4-style
statement-fail-on-DUPL-underflow directly so that the if-guard can be
elided and we get exactly the .inc body-part flow.

### F-3. `ShiftReduce.sc::Reduce` — added `else { c = ''; }` branch

**.inc 26:** `c = GE(n, 1) ARRAY('1:' n)` — conditional assign; on
GE-fail, statement fails, c keeps prior value (incoming param value, null).

**.sc 53-54:**
```
if (GE(n, 1)) { c = ARRAY('1:' n); }
else { c = ''; }
```

The `else { c = ''; }` is not in .inc. Should be:
```snocone
if (GE(n, 1)) c = ARRAY('1:' n);
```

(no else; let c keep its incoming-param value, which is null).

---

## Name-parity violations

Per the body-part principle, identifier names in .sc must match .inc/.sno
exactly. The "no rename" rule is strict.

### N-1. `case.sc` — function param shadows: `lwr(lwr)` → `lwr(s)`, etc.

**Per Lon (sessions earlier):** function-name shadowing of params is the
ONE permitted rename — required by Snocone grammar (a function cannot have
a param named the same as the function). So `lwr(lwr)` → `lwr(s)` is
**allowed** and correctly applied.

✅ Approved exception to the rename rule.

### N-2. `semantic.sc::shift(p, t, omega)` — extra `omega` param

**.inc:** `DEFINE('shift(p,t)')` — no locals.
**.sc:** `function shift(p, t, omega) { omega = "..."; shift = EVAL(omega); ... }`

The `omega` intermediate is a .sc-side invention. The body-part principle
says: keep the body parts identical. .inc has ONE body part:
```
shift = EVAL("p . thx . *Shift('" t "', thx)")
```

Faithful port:
```snocone
function shift(p, t) {
    shift = EVAL("p . thx . *Shift('" t "', thx)");
    return;
}
```

🔴 Same issue with `reduce(t, n, omega)`. Drop the omega intermediate.

### N-3. `Gen.sc::indent` renamed to `_indent`

**.inc 39:** `indent = DUPL(' ', 120)` (top-level global).
**.sc 3:** `_indent = DUPL(' ', 120);`

**Unjustified rename.** `indent` is not a Snocone reserved word. The
underscore prefix is a .sc-side stylistic addition with no .inc analog.

🔴 Restore to bare `indent`.

### N-4. `Gen.sc::Gen` — extra `_rest` local

**.inc 36:** `DEFINE('Gen(str,outNm)ind,outline')` — locals: ind, outline.
**.sc 24:** `function Gen(str, outNm, ind, outline, _rest)` — extra `_rest`.

`_rest` is .sc-side, introduced for the 2-step `?`-predicate workaround
(G-2). When G-2 is fixed, `_rest` should disappear and the .inc's destructive
in-place capture (`REM . $'$B'`) becomes the .sc form too.

🔴 Bound to G-2 — fix together.

### N-5. `ShiftReduce.sc::Shift` and `Reduce` — locals match

**.inc:** `Shift(t,v)s` — local: s. `Reduce(t,n)c,i,r` — locals: c, i, r.
**.sc:** `Shift(t, v, s)` — ✅ matches. `Reduce(t, n, c, i, r)` — ✅ matches.

✅ Name parity preserved.

### N-6. `counter.sc::DumpBegTag` — locals as params

**.inc 42:** `DEFINE('DumpBegTag()b,list,v')` — zero params, three locals.
**.sc 95:** `function DumpBegTag(b, list, v)` — locals declared as params.

Documented in .sc comment 16-20: "Snocone parser does not accept a leading-
comma `(,locals)` form; we declare the locals as ordinary parameters."

⚠ Acceptable workaround for grammar gap, but **note this is a parser gap**.
SB-6 grammar should grow `(,locals)` syntax — add as a new sub-rung. The
caller-side invocation is unchanged (zero args), and Snocone params init
to null on entry, so semantics match. ⚠ Future grammar work item.

### N-7. `Gen.sc` — globals init redundancy

**.sc 4-7:** `$'#L' = 0; $'$B' = ''; $'$C' = ''; $'$X' = '';`
**.inc:** no analog — relies on globals being null/zero by default.

🔴 Drop these inits. Snocone globals are null by default, same as SNOBOL4.

### N-8. `stack.sc` — `xTrace = 0` init

**.sc 4:** `xTrace = 0;`
**.inc:** no analog. global.inc/global.sc owns xTrace as a global.

🔴 Drop. xTrace is owned by global.sc.

---

## Style violations (mechanical fix)

### S-1. Single-statement brace bodies

Per SB-6.E.7-A landed: bare-if works. `{ stmt; }` single-stmt bodies should
be stripped to `stmt;`. Same for `else { stmt; }` → `else stmt;`.

**Count by file** (approximate, naive grep):

| File | Count |
|---|---|
| match.sc | 4 |
| stack.sc | 2 |
| case.sc | 2 |
| counter.sc | ~12 |
| ShiftReduce.sc | 4 |
| trace.sc | ~11 |
| omega.sc | ~15 |
| ReadWrite.sc | ~5 |
| Gen.sc | ~7 |
| Qize.sc | ~20 |
| **Total (12 files)** | **~80+** |

Tree.sc, beauty.sc, XDump.sc, TDump.sc, global.sc not yet counted.

**Mechanical fix only — do NOT use automated regex sweep**. Session #10's
automated debrace introduced broken code (e.g. `else Shift = .dummy; nreturn;`
where braces were stripped from a multi-stmt else). Hand-verify each file.

### S-2. Dropped `.inc` commented-out lines

**Sites found so far:**
- `ShiftReduce.inc:14` `*  OUTPUT = GT(xTrace, 4) ' = ' TLump(s, 1024)` — dropped
- `ShiftReduce.inc:31` `*--  (GT(xTrace, 4) TDump(r))` — dropped
- `omega.inc` x3 sites: trailing `;* Conflict TY also used here` — dropped

Per "no dead code pruning" rule (Lon, session #66): preserve as `// ...`
comments in .sc.

### S-3. Inconsistent function-on-one-line style

**Gen.sc:** SetLevel and GetLevel on one line (21-22), IncLevel/DecLevel
multi-line (9-20). Inconsistent. Pick one.

---

## Per-file pass #2 status (12 of 17)

| # | File | Pass #1 | Pass #2 | Action items |
|---|------|---------|---------|--------------|
| 1 | assign.sc | ✅ | 🔴 | Drop REPLACE wrapper (G-1); strip 0 brace |
| 2 | match.sc | ✅ | 🟡 | Strip 4 brace (S-1) |
| 3 | stack.sc | ✅ | 🔴 | Drop `xTrace=0` (N-8); strip 2 brace |
| 4 | case.sc | ⚠ fixed | 🟡 | Strip 2 brace |
| 5 | counter.sc | ✅ | 🟡⚠ | Strip ~12 brace; investigate `(X \| 'FAIL')` vs `(X, 'FAIL')` translation |
| 6 | ShiftReduce.sc | ✅ MISSED | 🔴 | Drop REPLACE×2 (G-1); drop `else { c = ''; }` (F-3); strip 4 brace; preserve dropped comments (S-2) |
| 7 | semantic.sc | ✅ | 🔴 | **Restore OPSYN calls (G-6) per Lon**; drop `omega` intermediates (N-2) |
| 8 | trace.sc | ⚠ fixed | 🔴🔴 | **Fix polarity inversion line 15 (F-1)**; strip 11 brace; fix wrong comment line 14 |
| 9 | omega.sc | ✅ | 🟡⚠ | Strip 15 brace; preserve dropped `;* Conflict` comments |
| 10 | ReadWrite.sc | ✅ | 🔴 | G-2 systemic (3 sites); strip 5 brace |
| 11 | Gen.sc | ✅ | 🔴 | Reimplement GenTab faithfully (F-2); restore `indent` name (N-3); drop globals init (N-7); drop `_rest` (bound to G-2); strip 7 brace |
| 12 | Qize.sc | ✅ | 🔴 | Qize branch 1 deferred-`*assign` (G-3); strip ~20 brace |
| 13-17 | XDump.sc, TDump.sc, tree.sc, global.sc, beauty.sc | various | **NOT YET AUDITED — pass #2** | Do in next session |

---

## Recommended fix order for next session

1. **Fix runtime gaps first** (G-1, G-2 if classified as bug, G-3 if classified
   as bug). These unblock multiple files and preserve byte-identical
   expression IR.

2. **Fix translation infidelities** (F-1 trace.sc polarity, F-2 GenTab,
   F-3 ShiftReduce else). These are semantic bugs in the .sc port —
   highest priority among non-runtime fixes.

3. **Restore name parity** (N-2, N-3, N-4 if G-2 fixed, N-7, N-8). Mechanical.
   Once names are aligned, the .sc reads as a body-part-faithful port of .inc.

4. **Restore OPSYN** (G-6 per Lon). Semantic.sc currently drops both OPSYN
   calls — that violates "keep all OPSYN processing." Carry them through;
   actual operator support arrives via SB-6.E.7-B.

5. **Audit remaining 5 files** (XDump.sc, TDump.sc, tree.sc, global.sc,
   beauty.sc) under the corrected body-part principle.

6. **Strip braces** (S-1) per file, hand-verified, after all above.

7. **Restore dropped comments** (S-2). Trivial.

8. **Re-gate** — three baseline gates green, fingerprint reviewed against
   .inc-faithful expectation.

---

## Repos state at end of session 2026-05-02 #13

- `corpus`: clean at HEAD `6a30100` (no .sc edits this session)
- `SCRIP`: clean at HEAD `31d8bb30` (no runtime edits this session)
- `.github`: this session adds this findings doc + GOAL update
- Fingerprint: `lines=785 stderr=0 parse_err=3 internal_err=232 rc=0` (unchanged)
- Three baseline gates green

**Active blocker for SB-6:** SB-6.E.7-J pass #2 — 12 of 17 files audited;
5 files remaining + fix execution.

---

## Translation principle — quick reference card for next session

**The mental model:**
1. Read the .inc/.sno block.
2. Identify the body parts (assignments, expressions, matches, calls).
   Mentally erase `:F() :S() :(label)` and label-targets.
3. Wrap the body parts with `if/else/while/for/break/return/freturn/nreturn`.
4. Names of variables and functions stay identical.
5. Helpers introduced for runtime gaps must be flagged separately, not
   silently inlined.

**Forbidden moves:**
- ❌ Renaming variables (except function-name-shadow case).
- ❌ Adding `_rest`, `omega`, `_indent` intermediates not in .inc.
- ❌ Adding `else { c = ''; }` branches not in .inc.
- ❌ Reasoning about WHEN .inc statements fail and reimplementing the logic.
- ❌ Dropping comments (`*` or `;*` trailers).
- ❌ Dropping OPSYN definitions.
- ❌ Patching corpus to work around runtime bugs.

**Permitted moves:**
- ✅ Restructure control flow (if/while/for/break instead of :F:S/labels).
- ✅ Strip `{ single_stmt; }` braces per SB-6.E.7-A bare-if.
- ✅ Use Snocone-natural idioms when expression-equivalent.
- ✅ Function-name-shadowing renames (`lwr(lwr)` → `lwr(s)`, etc.).
- ✅ Multi-line concat fragment regrouping when EVAL output is identical.
