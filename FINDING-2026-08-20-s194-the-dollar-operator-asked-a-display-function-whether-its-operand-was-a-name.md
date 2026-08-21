# FINDING s194 — `$` ASKED A *DISPLAY* FUNCTION WHETHER ITS OPERAND WAS A NAME, SO EVERY AGGREGATE WAS SILENTLY ACCEPTED

**Seat1 `/home/claude1`, Claude Opus 5, 2026-08-20. Queue row `indirect-nonname-silent-accept` (rank 1).**
**LANDED: SCRIP `7153ccd7` · corpus `c26738c1`.**

---

## THE BRIEF NAMED THE SMALL HALF

The brief was right that `corpus/programs/snobol4/parser/unary_indirect.sno` line 2 (`y = $name`, `name`
unset) diverges: oracle `ERROR 239 -- indirection operand is not name`, SCRIP silent. It was also right to
exonerate line 1 and to forbid touching `$'='`. **But the null string was the CHEAP half.** The same defect
had a second, worse face the brief did not predict: **every aggregate datatype was ACCEPTED**.

`bn_sno_name` (`by_name_dispatch.c:5212`, the ONE runtime body behind `CALL "SNO$NAME"`) read
`VARVAL_fn(args[0])` and refused only the empty C string. `VARVAL_fn` is the **OUTPUT-side stringifier**: it
answers `"ARRAY('3')"` for an array, `"TABLE(11,11)"` for a table, `"EXPRESSION"`, and the type name for a
programmer-defined datatype. Those are display forms, not name conversions — and they are all NON-EMPTY, so
they sailed through the guard. **`$ARRAY(3) = 'x'` created a variable literally called `ARRAY('3')` and the
program ran on.** That is a silent false accept in an operator whose entire job is to name a variable.

## THE RULE, AND WHY A NAME OPERAND IS EXEMPT

Manual v3.7 **p.83**: *"Indirection may proceed to any depth, provided the null string is never encountered
as a variable name"* — with the worked example `$RUFF` through an unset `RUFF` answering *"Error #239,
Indirection operand is not a name"*. **p.196**: *"$(.A) is the same as using the variable A"* — a NAME is
already a name, so it takes no conversion test at all.

## THE BOUNDARY IS ORACLE-MEASURED, NOT INFERRED

Measured on `sbl -bf` with `&ERRLIMIT` non-zero, so the oracle converts each error to statement failure and
prints the code as ordinary output (Ch.16) instead of a banner it exits 0 from:

| operand | oracle | SCRIP before |
|---|---|---|
| non-null STRING, incl. punctuation `$'='` | accept | accept |
| INTEGER `$3`, `$0` · REAL `$3.5` | accept | accept |
| NAME `$(.ABC)` | accept | accept |
| null string (unset var, `$''`) | **239** | silent statement failure, `&ERRTYPE` 0 |
| ARRAY · TABLE | **239** | **ACCEPTED — variable named `ARRAY('3')`** |
| programmer-defined DATA object | **239** | **ACCEPTED — variable named `PT`** |
| PATTERN · CODE · EXPRESSION | **239** | silent statement failure |

`&ERRLIMIT` is the corroborating count: one credit per refusal, never two (1000→995 over five, 1000→994 over
six). `$3.5` names the variable *literally called* `3.5`, round-tripped through `$'3.5'` — so the accept half
is pinned by VALUE, not by the absence of an error.

## ⛔ THE NULL TEST READS THE DESCRIPTOR, NEVER THE C STRING — AND THAT IS LOAD-BEARING

`&ALPHABET` is 256 bytes whose **first byte is NUL**, and the oracle **ACCEPTS** `$&ALPHABET`. A `!*sv` test
would have raised a **FALSE 239** there — failing the row's own *"and NOWHERE ELSE"* clause on the very first
extra witness. So the decision reads the counted length, with the runtime's own `slen==0 ⇒ use strlen`
convention: **`STRVAL()` sets `slen = 0`**, so a naive `slen == 0` null test refuses every INTEGER and REAL.
That cut was written, measured, and corrected — `$3`/`$0`/`$3.5`/`$(1-1)` all came back as false 239s.

## ⭐ ONE AUTHORITY, TWO FACES — BECAUSE `$` IS SPELLED TWICE

`core.c rt_sno_indirect_name` is the decision. It is asked by:
- **`bn_sno_name`** — serves the value position AND the assignment position; `$X` and `$X = v` both lower to
  `CALL "SNO$NAME"` (verified with `--dump-ir`), so there is no second spelling between them.
- **`rt_goto_resolve`'s `$` arm** (`runtime_eval.c:446`) — the computed-goto position, which spells `$` a
  SECOND time as a string prefix on the label name and had its own hand-written message.

`VARVAL_d_fn` (argval.c) classifies: it already answers `FAILDESCR` for exactly the non-convertible
datatypes, so the refusal set is not spelled a second time here either. The error rides **`kwb_error`**, not
`core_runtime_error`, for the reason the OPSYN rung recorded: the latter's conversion arm needs a pushed
`jmp_buf` only the EVAL boundary supplies, so raising there would print-and-exit where the oracle merely
fails the statement. At the default `&ERRLIMIT` of 0 `kwb_error` calls `core_runtime_error` itself, so the
default arm reports and terminates exactly as SPITBOL does.

## ⛔ THREE THINGS DELIBERATELY NOT DONE, EACH MEASURED AND NAMED

1. **A NAME WHOSE FIRST BYTE IS NUL CANNOT BE SPELLED.** SCRIP's namespace is C-string keyed
   (`NV_GET_fn`/`NV_SET_fn` take `const char *`). `$&ALPHABET` therefore still FAILS the statement — a
   visible refusal, never a false 239 and never a fabricated empty name. Proven a namespace limit rather than
   an error: **no `&ERRLIMIT` credit is spent** (`before=50 … after=50`). Pinned RED at
   `probe/indirect/indirect_nul_prefix_name` so it goes green when names become counted strings.
2. **ERROR 38 IS A DIFFERENT ROW.** `rt_goto_resolve` conflated *"indirection operand is not name"* with
   *"Goto undefined label"* in ONE printf. The oracle separates them: `:($N)` answers **38** for
   `N='NOSUCHLABEL'` and **239** for `N` unset. This rung split the 239 half out and left 38's legacy
   printf+exit alone rather than half-fixing it.
3. **THE GOTO FACE STILL CANNOT TAKE `:F`.** `GOTO_DEFERRED` carries no ω edge (`--dump-ir` prints `.`), so
   under a non-zero `&ERRLIMIT` — where the oracle converts and branches — that face reports and exits
   instead of failing the statement. Loud, not silent. At the DEFAULT `&ERRLIMIT`, which is what the corpus
   and every board see, it is now exact: `** Error 239 … indirection operand is not name`.

## ⭐⭐ TWO ADJACENT DEFECTS THIS ROW MEASURED BUT DID NOT CLAIM

- **`$` THROUGH A NAMETRAP LOSES THE TRAP — A SILENT WRONG ANSWER, STILL LIVE.** The SNOBOL4 stack-push
  idiom `Push = .stk[stk[0]]` then `$Push = x` (this is `crosscheck/control/expr_eval.sno`'s own Push)
  **pushes nothing** in SCRIP: oracle `stk1=hello stk2=world`, SCRIP `stk1= stk2=`. Cause: `bn_sno_name`
  always rebuilds a *string-keyed* NAME from `VARVAL_fn`, which for a `DT_N slen==2` nametrap dereferences to
  the element's VALUE and names THAT — double indirection, and p.196 says a NAME operand is the variable
  itself. **The cure looks like two lines** (`if (v.v == DT_N) { *out = v; return 1; }`) and is a separate
  row; it is NOT taken here because it is a semantic change outside this row's boundary. ⛔ It is also the
  trap this row nearly fell into: the first cut *did* deref `slen==2`, which turned that silent wrong answer
  into a **false 239** and was caught by `expr_eval` regressing m3 in the A/B — the only mover in 340
  programs. Minimal repro checked by hand before the cure, per ASM-DIFF-FIRST step 1.
- **`CODE()` ANSWERS `DATATYPE` STRING.** `CODE(' X = 1;END')` is a CODE object on the oracle and a STRING in
  SCRIP (measured; every other operand datatype — PT, EXPRESSION, ARRAY, TABLE, PATTERN — agrees). So a
  `$CODE(...)` witness would have PASSED FOR THE WRONG REASON (the variable is simply unset), and the line was
  **removed from the witness** rather than banked as a green.

## MEASUREMENTS (pristine, RT_OPT `-O0`, re-proved AFTER rebasing onto seats 3/6/7)

- **Board m3 339/1 · m4 337/2 SKIP 1 — fail-set IDENTICAL to the `SCRIP_IND_NAME=0` control, by name.**
  (Pre-rebase the same equality held at 338/2 · 331/8; the jump to 339/337 is seats 3/6/7's VLIST-ALT and
  DCAP-FRETURN landing under me, not this rung.)
- **beauty AB-IDENTICAL 9/9** one-line inputs, REF-OK 4/8 — the `$'$'` idiom (beauty.sno:104) provably
  untouched, and the 4 rc=139 are the standing M1 wall, identical under both arms.
- `make pristine` EXIT=0 twice. Gates: `emit_no_lang` OK · BOTH-MEDIUM ratchet **0** (ceiling 0).
- **All six RULES step-4 regens `changed=0`** except `util_regen_crosscheck_s_artifacts.sh`, which
  regenerated 4 `.s` — **all four byte-identical across `SCRIP_IND_NAME`, i.e. STANDING DRIFT from seat7's
  s192 direct-goto commit, not this session** (attributed file-by-file per the s192 rule; the rebase then
  dropped my commit as "already upstream", independently confirming it).
- No new global. No template touched. No codegen touched. Killswitch `SCRIP_IND_NAME=0` restores the old
  accept verbatim and is read ONLY on the refusal edge, so the `$` hot path beauty hammers takes no `getenv`.

## ⭐ GENERALISABLE

**A stringifier is not a classifier.** `VARVAL_fn` exists to render a value for OUTPUT; asking it *"is this a
name?"* silently converts "I can display this" into "this is legal", and the answer is non-empty for exactly
the datatypes that should have been refused. Where a rule is about a datatype, test the **descriptor**; where
it is about a length, read the **counted length**, because in this runtime `slen == 0` on a `DT_S` means
*"ask strlen"*, not *"null"* — two conventions one line apart, and each one produced a wrong cut of this fix
before it produced the right one.
