# HANDOFF 2026-06-10 — Pascal BB: Session 34 (downto + repeat..until fixed; gate 93/0)

## State on origin (verified clean)
- **SCRIP `bb04262`** · **corpus `f03cd86f`** · **.github `8b047833`**

## Gate
**m2 93/0** over 94 probes (recursion.pas XFAIL). Up from 89/0 at session start.

## Work done this session

### nl lowerer swap (session 33, already in GOAL-PASCAL-BB.md)
- Removed `src/lower/lower_pascal.c`; `lower_pascal_nl.c` is now the sole Pascal lowerer.
- Makefile updated; dead `lower_pas()` call in `lower.c` → `abort()`; six dead helper declarations removed from `lower_internal.h`. SCRIP `298651c`.

### realparam fix (session 33)
- `writeln(half(r):10:1)` — parser lacked `expr COLON expr COLON expr` arm. Added to `argument` in `pascal.y` with sentinel `ilit(-3)` (skip-write). Runtime `__pas_writeln`: `w == -3 → continue`. Matches pcom error(399) behavior (no `wrr` emitted). SCRIP `298651c`.

### downto fix (session 34) — SCRIP `bb04262`
- `lower_for` in `lower_pascal_nl.c` hardcoded `ival=6` (LE) and `+1` always, ignoring `t->v.ival==1` (downto flag).
- Fix: `is_downto = (t->v.ival == 1)`; `cmp_op = is_downto ? 8 (GE) : 6 (LE)`; `inc_op = is_downto ? 1 (SUB) : 0 (ADD)`. Per P4 comp.p lines 3381/3390.
- Probes added: `downto1.pas`, `downto2.pas`.

### repeat..until fix (session 34) — SCRIP `bb04262`
- Was using `IR_REPEAT` (one-shot forward jump — wrong).
- Attempted `IR_UNTIL` — exits on NOT-fail but only re-calls `IR_interp_node(ucnd)` with `.state=0`; body subgraph children are not re-executed.
- Fix: **pure γ/ω back-edge, no loop-container node** — same model as `lower_for`. `lower(cond, γ, NULL)`; `ω_to(cond_res, body_entry)` wires cond-fail back to body. Entry = `body_entry`. The outer `IR_interp_once` trampoline follows ω edges naturally on each iteration.
- Relop cond: direct. Non-relop cond: NE-wrap (`IR_BINOP ival=10`, lit0=0).
- Probe added: `repeat2.pas`. Also added: `writenl.pas` (write without writeln).

## Key implementation facts pinned

**Execution model (critical — took time to figure out):**
- `IR_interp_once` is a trampoline: follows γ/ω edges returned by `IR_interp_node`.
- `IR_WHILE`/`IR_UNTIL` run their `operands[0]` in an internal C while-loop — they do NOT follow γ edges of that operand. The body runs via the outer trampoline following γ back-edges.
- For-loops and repeat..until use **pure back-edge cycles** (no loop-container node). When cond fails, ω → loop-container OR back to body directly; outer trampoline follows.
- `IR_WHILE` is effectively a sentinel for the cond-fail exit path in lower_while: cond.ω = wnd; wnd.γ = after-loop. When cond fails → outer trampoline hits IR_WHILE → IR_WHILE re-runs cond (already fails) → exits to wnd.γ = after-loop.
- `IR_REPEAT` = one-shot forward jump to operands[0]. NOT a loop. Do not use for Pascal repeat.

**downto:** `t->v.ival == 1` in the AST TT_FOR node (set by parser `forsy IDENT BECOMES expr DOWNTOSY expr DOSY stmt` arm).

## Residues (carried forward)
- `recursion.pas` XFAIL (16-bit maxint overflow — P4 limitation, expected).
- m3/m4 pre-existing failures.
- Case no-match silently continues (no probe yet).
- `__pbt`/`__pct` NV temps clobber under recursive re-entry (no probe yet).

## NEXT — Lon picks
**(a) PB-29** — more constructs: `string` (packed array of char), `with` deeper nesting, `type` aliases, more complex nested procs.
**(b)** Any open residue bug.
**(c)** Any other goal.

## Session setup (next session)
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
cd /home/claude/corpus/programs/pascal && apt-get install -y fpc \
  && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas
```
