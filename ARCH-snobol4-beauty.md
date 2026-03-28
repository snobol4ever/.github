# ARCH-snobol4-beauty.md — beauty.sno Deep Reference
Two-stack engine, TDD protocol, diagnostics. Operational → SESSION-snobol4-x64.md.
## How beauty.sno Works — The Two-Stack Engine

beauty.sno is a **pattern-driven tree builder**. One big PATTERN matches the
entire source. Immediate assignments (`$`) fire mid-match to maintain two stacks:

### Counter Stack — tracks children per level

```
nPush()          push 0          entering a new syntactic level
nInc()           top++           one more child recognized at the current level
Reduce(type, ntop())             build tree node with ntop() children (read before pop)
nPop()           pop             exit the level — ALWAYS after Reduce
```

**Discipline:** `nPush` and `nPop` must bracket every syntactic level on ALL
exit paths — both γ (success) and ω (failure). Every sub-pattern that calls
`nPush` must call `nPop` before returning on every path. A missing `nPop` on
the γ path leaves a ghost frame that displaces all subsequent `nInc` calls.

**Reduce fires directly before nPop.** The invariant sequence is always:
```
nPush() → ... nInc() ... nInc() ... Reduce(type, ntop()) → nPop()
```
`ntop()` is read inside `Reduce` to know the child count. `nPop` discards the
frame **after**. Never nPop before Reduce — the count is gone.

### Value Stack — the tree nodes

```
Shift(type, val)       push one leaf node
Reduce(type, n)        pop n nodes, push one internal node with n children
```

**Source-level encoding:** `val ~ 'Type'` fires `Shift('Type', val)`.
`("'Type'" & n)` fires `Reduce('Type', n)`. The pattern is simultaneously
the recognizer and the tree builder — every `~` is a Shift, every
`("type" & count)` is a Reduce.

`pp(x)` and `ss(x,len)` walk the resulting tree after the full match.

### Seven Stmt Children

The `Stmt` pattern builds a node with exactly 7 children (some may be null/empty):

| Slot | Name | Content |
|------|------|---------|
| 1 | Label | label string, or empty |
| 2 | Subject | Expr14 — leftmost expression |
| 3 | Pattern | pattern expression, or empty |
| 4 | `=` indicator | literal `=`, or empty |
| 5 | Replacement | Expr — right side of `=`, or empty |
| 6 | goto1 | success goto, or empty |
| 7 | goto2 | failure goto, or empty |

**The count 7 is structurally guaranteed, not checked.** Every branch of every
`|` inside `Stmt` pushes the same number of items via `epsilon ~ ''` placeholders
for absent fields. If `emit_byrd.c` ever drops one of those `epsilon ~ ''` Shifts
on any branch, the count silently goes wrong — no runtime error, just a misbuilt
tree. The placeholders are load-bearing.

`nInc()` is called once per `Command` (one statement or directive).
`nPush()`/`nPop()` bracket `Parse` and `Compiland`.

### Key Pattern Structure (from beauty.sno lines 293–419)

The patterns that carry nPush/nPop/nInc calls — the complete set:

```snobol4
* --- Counter-stack patterns ---
ExprList  = nPush()
              *XList
              ("'ExprList'" & '*(GT(nTop(), 1) nTop())')
              nPop()
XList     = nInc() (*Expr | epsilon ~ '') FENCE($',' *XList | epsilon)

Expr3     = nPush() *X3  ("'|'"  & '*(GT(nTop(), 1) nTop())') nPop()
X3        = nInc() *Expr4 FENCE($'|' *X3 | epsilon)

Expr4     = nPush() *X4  ("'..'." & '*(GT(nTop(), 1) nTop())') nPop()
X4        = nInc() *Expr5 FENCE(*White *X4 | epsilon)

Expr15    = *Expr17
              FENCE(nPush() *Expr16 ("'[]'" & 'nTop() + 1') nPop() | epsilon)
Expr16    = nInc()
              ($'[' *ExprList $']' | $'<' *ExprList $'>')
              FENCE(*Expr16 | epsilon)

Expr17    = FENCE(
               nPush()
               $'('
               *Expr
               (  $',' *XList ("','" & 'nTop() + 1')
               |  epsilon    ("'()'" & 1)
               )
               $')'
               nPop()
            |  *Function ~ 'Function' $'(' *ExprList $')' ("'Call'" & 2)
            |  *Id       ~ 'Id'       $'(' *ExprList $')' ("'Call'" & 2)
            |  ...
            )

Command   = nInc()
              FENCE(
                 *Comment ~ 'Comment' ("'Comment'" & 1) nl
              |  *Control ~ 'Control' ("'Control'" & 1) (nl | ';')
              |  *Stmt              ("'Stmt'"    & 7) (nl | ';')
              )

Parse     = nPush()
              ARBNO(*Command)
              ("'Parse'" & 'nTop()')
              nPop()

Compiland = nPush()
              ARBNO(*Command)
              ("'Parse'" & 'nTop()')
              (icase('END') (...) | epsilon)
              nPop()
```

**Critical observation:** `Expr3`, `Expr4`, `Expr15`, and `Expr17` all contain
`nPush`/`nPop` pairs. The ω (failure) paths of `FENCE(nPush() ... nPop() | epsilon)`
must ensure `nPop` fires on backtrack. The `epsilon` branch is taken on failure
of the outer FENCE alternative — if the inner nPush fired before the inner match
failed, the nPop must still fire.

---

## Bug Diagnosis — Current Active Bug (session117)

**Symptom:** For `X 1` (two concat atoms), counter stack trace shows:
```
NPUSH idx=6   ExprList frame
NINC  idx=6 count=1   atom X
NPUSH idx=7   ← spurious — from inside pat_Expr parsing X
NPUSH idx=8   ← another spurious
NPOP  idx=8
NPOP  idx=7
              ← second NINC fires at wrong level — idx=6 stays at 1
              ← ntop()=1, guard (>1) skips Reduce(..,2)
```

**Root cause:** `Expr4`/`X4` pattern: `X4 = nInc() *Expr5 FENCE(*White *X4 | epsilon)`.
When matching the first atom `X`, `X4` fires `nInc()`, then `*Expr5` recurses
into `*Expr15 → *Expr17` which tries `FENCE(nPush() $'(' ... nPop() | ...)`.
The `nPush()` fires inside `Expr17`'s grouped-expr alternative, the inner match
fails (no `(`), but `nPop()` is **not called on the backtrack path** before
`Expr17` falls through to the `*Id` arm. Ghost frame remains.

**Fix location:** `emit_byrd.c` — the emitted C for `Expr17`'s first FENCE arm
must call `nPop()` on failure before falling to the next alternative.

**Do NOT touch `_saved_frame` or `pending_npush_uid`** until imbalance is fixed.

---

## Four-Paradigm TDD Protocol (TINY → M-BEAUTY-FULL)

| Sprint | Paradigm | Catches | Trigger |
|--------|----------|---------|---------||
| `stack-trace` | Dual-stack instrumentation | nPush/nPop/nInc imbalances | M-STACK-TRACE ✅ |
| `beauty-crosscheck` | Crosscheck — diff vs oracle | Wrong output | beauty/140_self → **M-BEAUTY-CORE** |
| `beauty-probe` | Probe — &STLIMIT frame-by-frame | WHERE divergence first appears | All failures diagnosed |
| `beauty-monitor` | Monitor — TRACE double-trace | Deep recursion / call-return bugs | Trace streams match |
| `beauty-triangulate` | Triangulate — cross-engine | Edge cases, oracle quirks | Empty diff → **M-BEAUTY-FULL** |

---

## Rung 12 Test Format (TINY crosscheck)

Tests in `corpus/crosscheck/beauty/`:
- `NNN_name.input` — SNOBOL4 snippet piped into beauty_full_bin
- `NNN_name.ref` — oracle: `snobol4 -f -P256k -I$INC $BEAUTY < NNN_name.input`

Runner: `snobol4x/test/crosscheck/run_beauty.sh` (pre-compiled binary).

Test progression (one at a time, never skip):
```
101_comment      * a comment
102_output           OUTPUT = 'hello'
103_assign           X = 'foo'
104_label        LOOP    X = X 1
105_goto             :(END)
109_multi        5-line program
120_real_prog    20-line program
130_inc_file     program using -INCLUDE
140_self         full beauty.sno → M-BEAUTY-CORE
```

Generate oracle: `snobol4 -f -P256k -I$INC $BEAUTY < NNN.input > NNN.ref`

---

## Stack-Trace Diagnostic Protocol (Sprint `stack-trace`) ✅ COMPLETE

M-STACK-TRACE fired session119. Protocol preserved for reference:

### Microscope Approach — beauty_micro.sno

The key diagnostic tool: strip beauty.sno to **PATTERN skeleton only** —
`Parse`, `Compiland`, `Command`, `Stmt`, `Label`, `Expr` through `Expr17`,
`ExprList`, `XList`, `X3`, `X4`, `Expr16`, `Goto`, `Target`, `SorF` —
with every `nPush`/`nInc`/`nPop` replaced by tracing wrappers:

```snobol4
* Tracing wrappers (replace library calls)
* tPush: nPush() equivalent with trace output
tPush   OUTPUT = 'NPUSH depth=' nDepth ' top=' nTop()
        ...real nPush logic...   :(RETURN)

* tInc: nInc() equivalent
tInc    OUTPUT = 'NINC  depth=' nDepth ' top=' nTop()
        ...real nInc logic...    :(RETURN)

* tPop: nPop() equivalent
tPop    OUTPUT = 'NPOP  depth=' nDepth ' top=' nTop()
        ...real nPop logic...    :(RETURN)
```

Run under CSNOBOL4 → `oracle_stack.txt` (ground truth).
Run compiled binary with instrumented runtime → `compiled_stack.txt`.
`diff oracle_stack.txt compiled_stack.txt` — first line = exact imbalance location.

### Finding the Ghost Frame

Given first divergence line N in the diff:
1. The previous matching line (N-1) is the last correct operation.
2. The diverging line N shows the first incorrect state.
3. Binary-search `emit_byrd.c` between those two events.
4. Look for a `FENCE(nPush() ... | ...)` where the failure path skips `nPop()`.

---

## Probe Script (Paradigm 2)

```bash
python3 /home/claude/harness/probe/probe.py \
    --oracle csnobol4 --max 200 failing.sno
```
Probe targets: `pp`, `Command`, `Label`, `ss`, `pp_Parse`.
TRACE gotcha: `TRACE(...,'KEYWORD')` non-functional — use `TRACE('var','VALUE')`.
`&STCOUNT` increments correctly on CSNOBOL4 (verified 2026-03-16 — prior "always 0" claim was wrong).

---

## Monitor Script (Paradigm 3)

Prepend to beauty.sno:
```snobol4
        TRACE('pp','CALL')    TRACE('pp','RETURN')
        TRACE('ss','CALL')    TRACE('ss','RETURN')
        TRACE('pp_Parse','CALL')  TRACE('Command','CALL')
```
```bash
snobol4 -f -P256k -I$INC beauty_trace.sno < input.sno 2>oracle_trace.txt
./beauty_full_bin_trace < input.sno 2>compiled_trace.txt
diff oracle_trace.txt compiled_trace.txt | head -20
```

---

## Triangulate Script (Paradigm 4 — M-BEAUTY-FULL trigger)

```bash
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle_csn.txt
./beauty_full_bin < $BEAUTY > compiled_out.txt
diff oracle_csn.txt compiled_out.txt   # empty = M-BEAUTY-FULL FIRES
```
SPITBOL excluded from full beauty.sno (error 021 at END).
Two oracles agree, compiled differs → our bug. Oracles disagree → check Gimpel §7.

---

## compiler.sno (post-M-BEAUTY-FULL bootstrap path)

`compiler.sno` = `beauty.sno` + `compile(x)` replacing `pp(x)`.
Same parse tree, same grammar (`Parse`/`Compiland`/`Stmt`/`Command`). Final action emits C Byrd boxes instead of SNOBOL4.
Proof: M-BEAUTY-FULL proves tree correct; `compile()` just walks it differently.

Architecture A (future): sprinkle emit actions into pattern alternations via
`epsilon . *action(...)` — like `iniParse` in `programs/inc/ini.sno`. Post-M-BOOTSTRAP.

---

## Beautifier Output Styles (session122)

beauty.sno has a **style switch** controlling how the parsed tree is emitted.
Two styles are defined. Both operate on the same parse tree — the switch
selects which emitter walks it.

### Style A — Ruler-aligned three columns (current pp/ss path)

Three fixed-position columns across every line: label, action, goto.
The widest entry in each column sets the ruler; all lines pad to it.
Colons line up vertically. Subjects line up vertically. Readable at a glance.

```
lfunc   ident( a , 'p' )                               :s( e001 )
        output = 'FAIL 1012/001: arg a should be p'    :( end )
e001    ident( b , 'q' )                               :s( e002 )
```

Implemented by `pp(x)` and `ss(x,len)` — tree walk with CNode IR width
measurement to decide inline vs multiline layout.

### Style B — Flat token stream (pp/ss BYPASS)

Tokens separated by a space **only where required**. No indentation. No padding.
Label is just the first token on its line. No column alignment at all.
Fast, deterministic, zero recursion — does NOT call `pp` or `ss`.

Spacing is governed by the **Gray/White** classification already defined in
beauty.sno (see `Gray` and `White` pattern variables):

- **White** tokens (identifiers, literals, keywords) — require a separating
  space from any adjacent white token.
- **Gray** tokens (operators, punctuation: `(` `)` `,` `:` `=` etc.) — attach
  directly to their neighbor with no space required.

So `ident(a,'p')` not `ident( a , 'p' )` — parens and commas are gray.
But `a b d` not `abd` — adjacent identifiers are white and must be separated.

```
lfunc ident(a,'p') :s(e001)
output = 'FAIL 1012/001: arg a should be p' :(end)
e001 ident(b,'q') :s(e002)
```

Implemented by a new `flat(x)` emitter that walks the same parse tree nodes,
applies Gray/White rules at each token boundary, and emits a space only where
required. No width measurement, no CNode IR, no multiline logic.
One pass, O(n) in token count.

**CRITICAL:** `flat()` must import or replicate the exact same Gray/White
definitions from beauty.sno — not approximate them. Any divergence produces
output that does not round-trip correctly through the parser.

**Use case:** generated C through the sno2c emitter and beautifier pipeline —
where machine-readable regularity matters more than human column alignment.
Also useful as a canonical normalized form for diffing and testing.

### Switch

```snobol4
*       &STYLE = 0  →  Style A (ruler columns, pp/ss)
*       &STYLE = 1  →  Style B (flat tokens, flat() bypass)
        eq( &style , 1 ) :s( use_flat )
        pp( tree ) :( done )
use_flat flat( tree )
done
```

M-FLAT milestone: `flat()` implemented, style switch wired, Style B output
verified against hand-tokenized oracle for all rung 1–11 crosscheck inputs.
