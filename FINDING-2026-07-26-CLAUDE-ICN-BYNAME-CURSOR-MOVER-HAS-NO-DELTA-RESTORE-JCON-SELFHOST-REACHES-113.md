# FINDING (2026-07-26) — BY-NAME CURSOR-MOVERS HAVE NO δ-RESTORE PORT; FIXED; JCON SELF-HOST GOES 0 → 113/113 CLASSES

**SCRIP `048cd87a` + this fix · RT_OPT=-O0 · oracle iconx/icont 9.5.25a (built from source this session)**

## ⛔ THE PRIOR DIAGNOSIS WAS WRONG — CORRECTED HERE

`GOAL-JCON-IN-SCRIP.md`'s LIVE CURSOR blamed the **TT_IDX/TT_SECTION rev-assign `if (rbeta)` hole**
(`t[i] <- ="."`). **MEASURED FALSE.** Removing `<-` entirely still reproduces; removing `suspend` still
reproduces. Neither is an ingredient. The real discriminator is whether the matching code is **lexically
inside a `?`**.

| shape | verdict |
|---|---|
| `"p.coord" ? { … match … }` (same proc) | ✅ SAME |
| `"zzz" ? { &subject := "p.coord"; … }` | ✅ SAME |
| `&subject := "p.coord"; … match …` (no `?`) | ❌ `pos=3`, oracle `pos=2` |
| `"" ? w()` — env in caller, match in callee | ❌ `pos=3` |

## THE 4-LINE REPRO (mode-3 and mode-4 identical)

```icon
procedure main();
   &subject := "p.coord";
   tab(many(&letters));
   if ="." & tab(many(&digits)) then write("Y") else write("N pos=", &pos);
end
```
iconx `N pos=2` · SCRIP (pre-fix) `N pos=3`.

## ROOT CAUSE — READ OFF THE EMITTED `.s`, NOT INFERRED

Outside a lexical `?` the node carries `in_scan=0`, so scan primitives do **not** emit as inline
register-world boxes; they degrade to by-name `rt_call_arr` dispatch (`bb_call_byname_str`). In that path
the box's β port was **`jmp ω` and nothing else**:

```
n12_call_β:                     jmp   n5_disjunction_af      <- tab() for ="." : NO cursor restore
```

Compare the inline contract in `bb_scan_tab.cpp`: `mov FRQ(op_off+16), r14` at α … `x86_beta()` +
`mov r14, FRQ(op_off+16)` + ω. **Only the inline path ever had a saved-δ slot.** `tab`/`move` are the only
two δ-writing primitives (ARCH-ICON.md two-family split), and `=s` desugars to `tab(match(s))`, so every
`=s` reached by-name advanced δ with no way to unwind it.

The `_force` sync brackets added 2026-07-22 (`x86_scan_sync_out_force`/`_in_rr_force`) were necessary but
**not sufficient**: they keep r14 ↔ `scan_pos` in lock-step — in lock-step on the *advanced* value. Nothing
saved the pre-call δ.

**WHY IT KILLED THE SELF-HOST:** JCON's `lex_yylex0` is a textbook `?`-less callee — the governing
`"" ? {…}` lives in its caller `yylex`. Its dot path is
`if str <- ="." & str ||:= tab(many(&digits))`. On `\p.coord` (irgen.icn:29) the digit match fails, δ is
never unwound, `do_ops()` starts at `c` → **`invalid character: "c"`**. Every `IDENT.IDENT` in Icon.

## THE FIX (2 files, mirrors the existing `callgen.act` extra-quad precedent)

- `src/contracts/zeta_storage.c` — `zls_node_bytes` grants a by-name **cursor-mover** call one extra quad
  (`scan.saved_delta`) at `off + 16*(1+n_operands)`, returning `2 + n_operands`. Same shape as
  `IR_CALL_PROC_STAGED`'s `callgen.act`.
- `src/templates/bb_call.cpp` — `bb_call_byname_str` writes `r14` to that slot at α (before sync-out) and
  reloads it in the β port before ω, for `tab`/`move` only.

Predicate is on the **callee name** (operand data), not a language token — no FACT-RULE exposure.

## PROOFS

- **12/12 repros now match iconx** (D E F G H I A B C rev1 rev2 rev3), both modes.
- **Suite 249/12/32 → 250/11/32.** One FAIL→PASS, zero regression.
  Live fail set (11): `args endetab fncs1 kwds mathfunc mindfa scan scan1 scan2 subjpos var`.
  ⚠ `GOAL-ICON-BB.md`'s FZ cluster list is STALE — `coerce mffsol string htprep prepro` no longer fail;
  `mathfunc`/`subjpos` are not in it.
- **JCON SELF-HOST: 0 → 113 class files.** `SCRIP-jtran preproc irgen.icn : yylex : parse : ast2ir : bc_File`
  previously died at line 29 producing nothing; it now runs the whole pipeline.
- **Oracle emits 113 too — not 114.** The goal file's "114" counted the `links` file. **File sets are
  IDENTICAL** (empty `diff` of listings) and **`links` is BYTE-IDENTICAL**.
- **SCRIP regenerates `interface.icn` BYTE-IDENTICAL** to oracle-jtran (415 lines, 0 diff lines).

## WHAT REMAINS — ONE NAMED DEFECT, NOT A CODEGEN GAP

All 113 `.class` bodies still differ. **The `do_ops.icn` confound was tested and EXCLUDED:** rebuilding
SCRIP-jtran from the *oracle-generated* `do_ops.icn` gives the same 0/113. The cause is the already-documented
**TABLE `key()` ORDER** defect:

```
iconx : key order: @-*$!+%/
SCRIP : key order: %$!-/+*@
```

`gen_bc.icn:1495 bc_initialize_tmps` walks `key(bc_tmp_table)`, so constant-pool/`astore` assignment order
differs in essentially every method — consistent with `ir_a_Ident.class` (same size, 3515 both) first
differing at **char 253**, inside the constant pool. Canonical spec is already known:
`rmisc.r:175` hash = Σ(char × 37^k) over the first ≤10 chars + length; `rstruct.r:263` walks slots in index
order with chains sorted ascending by hashnum. **That is the next rung, and it is fully specified.**

## ALSO OPEN

- **SEGV rc=139 at teardown.** It fires *after* all 113 classes and `links` are written (output is complete
  and set-identical), so it is a shutdown-path fault, not a translation fault. Needs its own bracket.
