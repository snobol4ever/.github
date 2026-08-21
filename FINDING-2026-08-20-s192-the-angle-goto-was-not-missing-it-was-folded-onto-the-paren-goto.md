# FINDING — s192 (seat7, `/home/claude7`, Claude Opus 5) — queue row `goto-code-object-parse`

## ⭐ THE HEADLINE: THE FORM WAS NOT MISSING FROM THE GRAMMAR. IT WAS **FOLDED ONTO THE PAREN GOTO**, AND THE FOLD WAS WRONG IN BOTH DIRECTIONS.

The brief said *"a grep of `src/parser/snobol4/` finds no angle-bracket goto form anywhere."* The grep was for the
form; the lexer had the **characters** all along:

```
<GT>"<"   { gt_depth++;                 return T_GOTO_LPAREN; }     <-- `<` lexed AS `(`
<GT>">"   { if (gt_depth > 0) gt_depth--; return T_GOTO_RPAREN; }   <-- `>` lexed AS `)`
```

One token pair for two different constructs. `rt_goto_resolve` then carried a fifth resolution arm whose own
comment named the deal out loud — *"a variable holding a CODE value (**the lexer folds direct-goto `:<C>` onto
the plain-name form**, so `C` here may be the variable)"*. So the fold was deliberate, documented, and **broken
in both directions**:

| written | oracle (`sbl -bf`) | SCRIP *before* | verdict |
|---|---|---|---|
| `:<C>` | enters the code object | enters the code object | accidentally right |
| `:< C >` | enters the code object | **parse error** | the f13 spelling — dead |
| `:<CODE(S)>`, `:<A<1>>`, `:<C D>` | enters the code object | **parse error / silent token drop** | dead |
| `:(C)`, C holding CODE, no label C | **ERROR 038 goto undefined label** | **enters the code object** | ⛔ **SILENTLY WRONG** |

The last row is the one that matters. **A program the oracle REFUSES, SCRIP RAN** — and no board could ever
see it, because the fold made the wrong answer look like the right one.

## THE SPLIT AS MEASURED (oracle first, then grammar — the brief's order)

Manual v3.7 p.178 §"The direct Goto" + p.133: the operand goes in angle brackets; `S`/`F` may precede it;
lower-case `s`/`f` are interchangeable "regardless of case-folding"; a direct Goto may sit beside a regular one.
The manual says *"the name of the variable"* — **the live oracle says more**, and the oracle is the authority:

* `:<CODE(S)>` — a **function-call expression** — enters the block. ✅
* `:<A<1>>` — an **array element**, angles nesting inside the goto's angles — enters the block. ✅
* `:<C D>` — a **concatenation** — enters the block. ✅
* operand is a string / an integer / unassigned ⇒ **ERROR 024 "goto operand in direct goto is not code"**, at
  RUN time, after the statement's own output has been produced. All three measured, all three identical.

So the angle form takes a **general expression**, not a variable name. The grammar landed accordingly.

## THE CURE — TWO BRACKETS, TWO ROADS

1. **Lexer** (`snobol4.l`): `<` in the goto field at top level emits a new `T_GOTO_LANGLE`, switches the scanner
   into `BODY` so the **full expression lexer** runs on the interior, and counts angle depth (`gt_angle`) so the
   matching `>` — and only that one — emits `T_GOTO_RANGLE` and returns to `GT`. Nested `A<1>` therefore works by
   construction. At `gt_depth > 0` the rule `yyless(1)`s and behaves exactly as before, so nothing that parsed
   yesterday parses differently today.
2. **Grammar** (`snobol4.y`): one production — `goto_label_expr : T_GOTO_LANGLE expr0 T_GOTO_RANGLE` — building a
   new `TT_GOTO_DIRECT` wrapper. Bison conflict count **unchanged (1 s/r, the pre-existing one)**.
3. **Lowerer** (`lower_snobol4.c`): `sgoto_direct()` is the ONE reader of the form; `sno_goto_direct_target()` is
   the exact shape of the computed-goto function beside it — evaluate the operand into a hidden `DGT$n` at
   TRANSFER time, then `IR_GOTO_DEFERRED("<DGT$n")`. The three-way S/F/U cascade moved into one
   `sno_goto_branch()` reader so the site stays under the line limit and the construction ORDER is provably the
   order it had before the direct form existed.
4. **Runtime** (`runtime_eval.c`): `rt_goto_resolve` gains arm 2, the `<` prefix — the exact parallel of the `$`
   prefix the indirect road already uses — and **the unsound arm 5 is deleted**. `:(C)` is a label lookup again.

## ⛔ THE ONE CLAUSE OF DONE-WHEN THAT IS NOT MET, AND WHY IT IS NOT THIS ROW

`f13_eval_code.sno` is **m3 PASS / m4 SIGSEGV**. The m4 crash is **PRE-EXISTING AND UNRELATED**, proven twice:

* **built the tree WITHOUT this patch** and the crash reproduces identically;
* a control witness that contains **no angle goto at all** — the fragment entered by an ordinary `:(LABEL)` —
  crashes the same way.

The class: **a `CODE()` fragment whose own Goto is `:(END)` — one that TERMINATES rather than transferring back
into main — crashes in mode-4 only.** `rip = _rtld_global`, which is the landing/record-depth signature
`bb_goto_deferred.cpp` already names in its own comment. Checked in RED, with its passing sibling one ingredient
away, at `corpus/probe/eval/`:

| witness | m3 | m4 | what it isolates |
|---|---|---|---|
| `ev_code_end_terminates.sno` | PASS | **SIGSEGV** | direct goto into a fragment that ends `:(END)` |
| `ev_code_end_label_ctl.sno` | PASS | **SIGSEGV** | same fragment, entered by a plain label goto — no angle form |
| `ev_code_back_ctl.sno` | PASS | PASS | same, but the fragment ends by transferring BACK into main |

Routed to HQ (`s4e_msg.sh ask goto-code-object-parse`). Not opened here: END-OF-CONTEXT LAW.

## EVIDENCE

**Witnesses (live-oracle `.ref`, `sbl -bf`), green BOTH modes:** `corpus/crosscheck/rung2/217_direct_goto.sno`
(bare `:<C>`, the spaced `:< C >` f13 spelling, and a labelled fragment) · `218_direct_goto_cond.sno`
(`:S<C>`, `:F<C>`, `:s<C>`, `:f<C>`, and an S-branch correctly NOT taken on failure) · `219_direct_goto_mixed.sno`
(`:S<C>F(LBL)`, `:F<C>S(LBL)`).

**Emitted-code A/B, 2017 SNOBOL4 programs, mode-4 `.s` md5, base vs new** (`programs/lon/` and
`programs/include/` excluded BY CONSTRUCTION, never opened). The rig was proven non-vacuous first — the base arm
*rejects* the spaced form, and all four binary md5s differ, so `LD_LIBRARY_PATH` really swaps the `.so` and not
just the driver (the s68 vacuous-gate conviction).

* **noise floor measured first: 1** — `corpus/programs/snobol4/parser/unary_not.sno` emits a **different `.s` on
  two runs of the SAME binary**. Nondeterministic emission, pre-existing, wants its own row. Reported to HQ.
* **39 real movers. Every single one carries the angle form in its `-INCLUDE` closure. Zero collateral.**
* **Graded (both modes vs `.ref`): 28 unchanged · 2 improved · 0 regressed.** The two: `217` FF→PP, `f13` FF→**PF**.

**Boards, base vs new, same box:** crosscheck m3 **315/5 → 316/4**, m4 **311/7 SKIP 2 → 312/7 SKIP 1**, DIVERGE
**3 → 3** — **the only mover is `217_direct_goto`, the test named for this construct**, m4 fail-set and DIVERGE-set
identical BY NAME. Broad corpus m3 336/4, m4 329/10 SKIP 1.

**Pristine (HQ-27):** `make pristine` reproduces the incremental binary md5 for md5 (`scrip da2bf057…`,
`libscrip_rt.so 6ba01518…`). Gates green: `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` ·
`icn_one_reg_frame` · `icn_semicolon_required`. RULES step-4 regens ×5 all `changed=0` — an independent second
path to the same zero-collateral answer. RT_OPT `-O0` (FACT RULE O0-DEV).

## ⭐⭐ A BLOCKER THE WHOLE FLEET INHERITED, AND IT WAS NEVER REAL

`src/parser/snobol4/Makefile` says bison/flex *"are never installed in the session env"*, and
`install_system_packages.sh` needs a `sudo` password this seat does not have. **The parser has therefore been
un-regenerable — and it did not have to be.** `apt-get download` needs no root:

```bash
apt-get download bison flex m4 libbison-dev && for d in *.deb; do dpkg-deb -x "$d" root; done
export PATH=$PWD/root/usr/bin:$PATH BISON_PKGDATADIR=$PWD/root/usr/share/bison
```

Regeneration **from the SCRIP root** (`bison -d -o src/parser/snobol4/snobol4.tab.c src/parser/snobol4/snobol4.y`;
`flex -o src/parser/snobol4/snobol4.lex.c src/parser/snobol4/snobol4.l`) reproduces the committed
`.tab.c`/`.tab.h`/`.lex.c` **BYTE-IDENTICALLY** — verified before a single character was changed, which is what
made every later diff trustworthy. ⛔ Run from the repo ROOT: bison bakes the invocation path into the header
guard and the `#line` directives, so running it in the parser directory rewrites 944 lines of noise.

**VERIFY-INHERITED-BLOCKERS earned its keep: one command retired a blocker that had stood for sessions.**

## SIDE OBSERVATIONS (named, not acted on)

* **`--dump-ast` under-reports gotos.** `goto_node_str` returns NULL for any non-`TT_QLIT` child, so a computed
  `:($(expr))` goto — and now a direct one — prints **no `:go` at all**. The dump is a lossy regression proxy;
  this is why the sweep above measures emitted `.s`, not the dump.
* **`corpus/programs/snobol4/feat/*.s` are pre-mode-3/4 fossils.** `f13_eval_code.s` still opens
  `; generated by scrip-cc -asm` + `%include "snobol4_asm.mac"` — the deleted NASM world. **No regen script covers
  `feat/`** (RULES step 4 names benchmark/feature/demo/programs/prolog-bench; `feature` means `SCRIP/test/snobol4`,
  and `programs` means `programs/{icon,prolog,rebus}`). Left untouched rather than silently rewriting one file in
  an unowned tree.
