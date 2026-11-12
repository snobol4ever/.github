---
name: prolog-constraints
description: SCRIP Prolog's constraints over one attributed variable: the wake word, hooks, freeze, dif, CLP(FD/Q/R/B), CHR. REQUIRED by the skill gate before editing clpfd.pl, clpq, clpr, chr_runtime.pl or lower_prolog_chr.c.
---

# Prolog constraints

The language skill is `prolog`; the engine (the trail, the cell, the bind sites) is skill `prolog-engine`. Detail is in `reference.md` beside this file.

## 1. The attributed variable (as built)

- **The cell**: an ordinary self-pointing unbound variable whose tag word carries `DT_PLVAR` in its low byte, the flag `PL_VAR_ATTV` (0x100) above it, and the variable's creation serial in the bits above that (`PL_SERIAL_SHIFT`), so variables order in creation order as swipl's do; `pl_var_make(cell, cx, attv)` in `src/runtime/rt/rt_pl_trail.c` makes one. A bind site tests `(word & (255 | PL_VAR_ATTV)) == (DT_PLVAR | PL_VAR_ATTV)` (`bb_pl_cell.h`).
- **The attributes** live on the collected heap (the lifetime rule: the attribute outlives the call that put it), as SWI represents them (`att(Module, Value, More)`), reached by the leaves `'$attv_atts'`, `'$attv_set'` (value-trailed: undo writes the old DESCR back, as `b_setval` does) and `'$attv_take'`. No second undo mechanism exists.
- **The wake word** is the trail header's `PL_TR_WAKE_OFF` slot: the lowest trail offset of an attributed binding not yet woken, an offset and never a pointer. Binding an attributed variable pushes an unconditional trail entry and lowers the wake word.
- **The probe**: in an ARMED program (the source names `put_attr`, `get_attr`, `freeze`, `dif`, `when`, `copy_term/3`, `attr_unify_hook`, `library(clpfd)`, a GNU `fd_` predicate, and so on; the prelude then injects `'$wakeup'/0`), the lowerer places a wake probe (an `IR_CLEANUP` of the WAKE kind) at each clause's body entry and after every body goal that is not a user call or a control construct. An unarmed program pays nothing.
- **The unconditional push is no fixed limit**: `'$attv_take'` reclaims the entries when no choice point is live (B zero), since nothing can unwind them.
- **Hooks by module without a module system**: the lowerer renames `attr_unify_hook/2` per its module so freeze's, dif's, clpfd's and the user's hooks never merge.

## 2. The libraries (prelude, `src/parsers/prolog/prelude/`)

SWI's libraries vendored verbatim and loaded by `use_module`: `clpfd.pl` (CLP(FD)), `gnu_fd.pl` (the GNU `fd_*` layer), `clpq.pl` and `clpr.pl` as two instances of one shared core (`clpqr_*.pl` with the `_q` and `_r` file pairs), `clpb.pl` (BSD), `chr_runtime.pl` and `chr.pl`. SWI's CHR translator is not vendored: CHR rules are source the parser recognises and `src/lower/lower_prolog_chr.c` translates (`:- chr_constraint`, `:- chr_type`, simplification `<=>`, propagation `==>`, simpagation `\`), over the vendored runtime's store.

## 3. Rulings

- No new mechanism for a constraint system: attributes, the trail and the wake probe are the whole of it (CEO-1596/1960/1964).
- Re-admission (CEO-1696): a program that becomes answerable returns to its suite's denominator in the landing that answers it.
- The variable order is creation order (the serial), as swipl prints it (clpr-chr step 8, relanded after a revert).

## 4. DESIGN: clpr-chr (CEO-1996/1998; `harness/designs/clpr_chr/STEPS.tsv`, `test_design_clpr_chr_steps.sh`; the witnesses are the prolog master's entries `clpr_chr__*`)

All ten steps DONE on 2026-11-01 (CHR declarations and options; simplification with guards; simpagation and partner lookup; propagation and the history; wake-up on binding; store inspection; CHR inside a module; fresh variables in creation order; the linprog driver and its source; the finish). The open constraint row is `prolog-swi-class-clpfd-infix-operators` (FREE).
