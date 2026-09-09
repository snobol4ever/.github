# CONVERT(x,'EXPRESSION') built Icon's PROCEDURE descriptor, and a by-name call could not reach a CODE()-built function

**Seat:** hq_S (HQ-SUSTAIN, SNOBOL4 runtime) · **Date:** 2026-09-08 · **Mode:** NONET
**Found by:** reducing `corpus/packages/snobol4/aisnobol` SIR and TEST to witnesses the oracle answers differently.
**Oracle:** `/home/resources/x64/bin/sbl -bf` · **Build:** incremental `make`, `RT_OPT=-O0`

## The two defects

### 1. `CONVE_fn` returned `DT_E` (Icon's procedure) where SNOBOL4 wants `DT_X` (the unevaluated expression)

`src/runtime/runtime_eval.c:CONVE_fn` built a descriptor with `v = DT_E`. Two different
things live in `DT_E`: `proc_as_value()` builds one for an Icon procedure and puts the
**stage2 proc-table index** in `.slen`, and `CONVE_fn` built one carrying a compiled eval
chain with the constant `3` in the same field. `bn_type_datatype()` therefore answered
`PROCEDURE`, and procedure #3 and a converted expression were literally indistinguishable.

The visible half was `DATATYPE`. The half that mattered was **deferral**. `DT_X` is the
descriptor `*NAME` produces, and `pattern_match.c` turns it into a `TT_DEFER` node — a
pattern element that resolves its reference **at match time**, not at build time. A `DT_E`
carries no such wiring, so a converted expression placed inside a pattern resolved once,
against whatever the variable held at that instant.

That is exactly SPITCORE's `FASTBAL` (Gimpel, *Algorithms in SNOBOL4*, ch. 9):

```
FASTBAL NAME  = 'FASTBAL...' &STCOUNT '.'
        IBAL = CONVERT(NAME,'EXPRESSION')
        ...
        ELEM = LP IBAL RP | ELEM
FASTBAL3 FASTBAL = BREAK(SPCHARS) ARBNO(ELEM)
        $NAME = FASTBAL    :(RETURN)
```

`IBAL` goes **inside** the pattern that is still being built, and `$NAME = FASTBAL` closes
the knot on the last line. Resolved eagerly, `IBAL` was empty, so every recursive
balanced-paren pattern in the SNOLISP reader matched nothing.

**Cure.** A bare name now yields the `DT_X` name descriptor `SNO$MKEXPR` builds. A general
expression keeps the compiled chain but wears `RT_CONVE_CHAIN_MARK` (`0xFFFFFFFD`,
neighbouring the Icon by-name marker `0xFFFFFFFE`) in `.slen`, so `DATATYPE` can separate it
from a proc-table index. A runtime-built `DT_X` names a plain **variable**, where a
compiler-built one names a lowerer-emitted thunk (`*X` lowers to `SNO$MKEXPR("EXPR$0")` plus
a `proc EXPR$0`), so `rt_sno_dtx_value()` resolves a `DT_X` name: the thunk when one is
registered, else the variable. Every `DT_X` the compiler builds takes the first arm and is
bit-for-bit unaffected.

### 2. `rt_call_named_proc()` could not call a function `CODE()` built at run time

A function created by `CODE()` has `p->fn == NULL` and `p->dyn_scope == 1`; its body is a
dynamic entry label. `rt_call_named_proc()` bailed on `if (!p || !p->fn) return FAILDESCR`,
while `rt_call_proc_descr()` already carried the entry-label arm. **That is why a DIRECT
call to such a function has always worked and a BY-NAME call never did** — measured under
gdb: the direct call reaches `rt_call_proc_descr`, the by-name call reaches
`_usercall_hook` → `rt_call_named_proc` → `call_user_function`, which then looks for an AST
body that a runtime-compiled label does not have, and returns the null string.

**Every OPSYN'd operator is a by-name call.** SPITCORE defines `LIST` through `DEXP`
(which is `CODE(...)` + `DEFINE(...)`) and then `OPSYN("~",.LIST,2)`, so `PCAR ~ RLIST` —
the cons constructor the whole reader is built on — returned the null string. `MAPCARV`
then reported `illegal datatype STRING, CONS was expected`, which is where SIR died.

**Cure.** `rt_call_named_proc()` delegates that case to `rt_call_proc_descr()` after
loading `g_call_args`. Delegated, never re-implemented: one authority for the dynamic-entry
route.

## Witnesses

Each was byte-different from `sbl -bf` before and is byte-equal after:

| witness | before | after (= oracle) |
|---|---|---|
| `DATATYPE(CONVERT('A','EXPRESSION'))` | `PROCEDURE` | `EXPRESSION` |
| `DATATYPE(CONVERT('A + B','EXPRESSION'))` | `PROCEDURE` | `EXPRESSION` |
| recursive balanced-paren pattern via `CONVERT` | `NOMATCH` | `MATCH` |
| binary `OPSYN` onto a `CODE()`-built function, string result | *(null string)* | `s(x,y)` |
| binary `OPSYN` onto a `CODE()`-built function, DATA result | `STRING` | `PAIR` |
| SPITCORE `READ('(A B C)')` | dies in `MAPCARV` | `CONS`, prints `(A B C)` |

⭐ **One measurement in this reduction was a false green and is worth recording**, because it
is this project's own trap wearing a new hat. Running `scrip $D/SIR.sno` and `sbl -bf
$D/SIR.sno` from a scratch directory by ABSOLUTE path produced a **zero-line diff**, which
reads as "SIR already passes". Both had failed identically: `-INCLUDE "SPITCORE.sno"`
resolves against the *running file's* directory, so neither could open it. The instrument
answered a narrower question than the one asked — *do these two agree*, not *are they right*
— and agreement between two failures is not evidence. A diff-vs-oracle is only a verdict when
at least one side is known to have produced real output.

## Control arms

SNOBOL4 master **1894/1894** both modes FAIL=0 (ast 28/28) · Icon master **704/704** both
modes FAIL=0, watermark held · smoke icon 15/15, prolog 5/5, snocone 5/5, rebus ok ·
aisnobol board 4/7 unchanged.

## What is NOT cured — the next row

SIR and TEST move `FAIL` → `CRASH`: they now build cons cells correctly and run far enough
to reach a **third defect, which is PRE-EXISTING**. Verified by stashing this change,
rebuilding, and re-running the same witness: it crashes identically without any of it.

Reduced so far to — SPITCORE loaded, a failing `(~ATOM(L) ATOM( CDR(L)))` inside a `DEFINE`'d
function, then `FRETURN`. The crash is an indirect jump into a **non-executable page**
(`libscrip_rt.so`'s `r--p` mapping), in **both** modes, called straight from `main`. It does
**not** reproduce standalone with an equivalent hand-built DATA type and predicate — it needs
SPITCORE's scale — and each ingredient alone is green: `(~ATOM(L))` alone, `(ATOM(L)
ATOM(CDR(L)))` alone, and the same shape with the locals list all return correctly.
