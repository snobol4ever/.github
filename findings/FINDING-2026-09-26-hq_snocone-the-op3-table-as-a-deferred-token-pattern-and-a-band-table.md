# FINDING 2026-09-26 hq_snocone -- the op/3 table as one deferred token pattern and a band table, measured on every arm, awaiting its landing

**Tree:** SCRIP `0dd682acd` (shipped `bootstrap/parser_prolog.sc` last touched at `de51fb0c3`) · corpus `fe923331e` · .github `c6cb33bc4` · RT_OPT=-O0 · incremental `make`. **Order:** Lon 2026-09-26 ~16:3x CDT, in-chat to hq_snocone: *"Build the op/3 table as deferred patterns"* (GOAL-SNOCONE-100.md § LIVE CURSOR SC-PARSERS-TENET-2026-09-26b, NEXT (a)).

## The claim

`parser_prolog.sc` reads a Prolog `:- op(P, T, Name).` directive at match time and thereafter parses `X Name Y`, `Name X` and `X Name` into the same `(TT_COMPOUND (TT_FNC Name) ...)` the ordinary compound path builds, functor first, on SPITBOL and on SCRIP in both modes.

| arm | population | shipped `de51fb0c3` | with the patch | flips | losses |
|---|---|---|---|---|---|
| `sbl -bf -s2000m -d4000m`, the transpiled `.sno` | 522 corpus `.pl` | 415 parsed / 107 refused / 0 timeout | **423** / 99 / 0 | 8 | 0 |
| SCRIP mode 3, the 14-file chain + parser concatenated (`-s4096m -d16384m`) | 522 | 350 / 171 / 1 timeout | **358** / 163 / 1 (the pre-existing `programs/prolog/rung10_programs_puzzles.pl`) | 8 | 0 |
| the `.sno` on SCRIP mode 3 · the chain on mode 3 · the chain compiled (mode 4, `--compile`, `as`, `gcc -lscrip_rt`) | the 8 flips + `test_op.pl` + 3 witnesses | -- | byte-identical to SPITBOL on every one | | |
| `monitor_run.sh <.sno> --oracle --input` on the witness | 1 | | AGREE=2638 DIVERGE=1 UNGRADED=239: the one divergence is `InitStack`'s `$'@S' = ''` (STRING on SPITBOL, ARRAY on SCRIP), the bracket already with the officers | | |

The eight flips: `benchmarks/prolog/src/gnu-examplespl/poly_10.pl`, `swi-bench/poly_10.pl`, `swi-bench/prover.pl`, `swi-vanroy/poly_10.pl`, `swi-vanroy/prover.pl`, `packages/prolog/inriasuite/inriasuite.pl`, `packages/prolog/logtalk_iso/directives/op_3/file.pl`, `packages/prolog/swi_tests/core/test_qcall.pl`.

## The design, and the two spellings measurement rejected

A `.` action fires only after the WHOLE file matches (PRIMER § the `.` vs `$` model), so a table filled from the tree could never affect the clauses after the directive: the `op(P, T, Name)` goal captures its three arguments with `$` and fires `DeclareOp` immediately, while still shifting and reducing the same `TT_COMPOUND` the ordinary path would. `uop_band[Name]` holds a key (`in700`, `pre500`, `post`; the band is the grammar level at or above P: 200 400 500 600 700 900); `uop_on` is `FAIL` until the first declaration and then ONE token pattern `(Atom | Graphic_atom) $ uop_tx . thx . *Shift('TT_FNC', thx)`; each of thirteen grammar sites checks its own key with `*IDENT(uop_band[uop_tx], key)` at match time; infix and postfix applications reduce then `OpSwap` moves the functor first; `op(0, T, Name)` clears the entry. Prefix arms sit after the compound and negative-literal arms and BEFORE every leaf arm, because a leaf arm that shifts `++` as a bare atom inside a FENCE'd conjunction tail cannot be retried (`a :- foo, ++ X.` refused while `a :- ++ X.` parsed).

Rejected: (1) per-band alternations rebuilt with `|` on every declaration -- `test_op.pl` (84 op/3) SPITBOL 0.12 s, SCRIP 7.5 s against 3.3 s shipped, past the census's 10 s cap at 8 jobs; the 84 declarations alone cost SCRIP 0.47 s and the rest of the file 2.3 s, so it is SCRIP's matching of long alternations, not their construction; (2) an incremental append -- SPITBOL 0.05 s, SCRIP still 7.5 s. The table form: SPITBOL 0.02 s, SCRIP 1.78 s against 1.67 s shipped.

## Why it is not landed

The copy into `SCRIP/bootstrap/parser_prolog.sc` was refused by this sitting's harness permission classifier ("Modify Shared Resources"), and the classifier's rule is not to pursue that outcome again in the session. The landing is: `git -C SCRIP apply <this patch>` (or `cp` the draft), one commit, one push, then `python3 scripts/util_parser_sc_census.py --lang prolog --population corpus --jobs 8` (expected 358 parsed / 163 refused / 1 crash of 522) and the prolog line of the cursor rewritten.

## The patch (`git apply --check` clean on `0dd682acd`)

```diff
--- a/bootstrap/parser_prolog.sc
+++ b/bootstrap/parser_prolog.sc
@@ -125,6 +125,32 @@
     return;
 }
 /* ==================================================================================================================== */
+/* op/3: the user operator table -- uop_band[name] is the band key ('in700', 'pre500', 'post'); uop_on is FAIL until the first */
+/* op/3 goal declares, then the one token pattern, and each site checks its own key by *IDENT at match time; no pattern is built */
+uop_band = TABLE();
+uop_tok  = $' ' ((((Atom | Graphic_atom) $ uop_tx) . thx) . *Shift('TT_FNC', thx)) $' ';
+uop_on   = FAIL;
+op_infix   = epsilon . *OpSwap(3);
+op_postfix = epsilon . *OpSwap(2);
+/* ==================================================================================================================== */
+function OpSwap(n, x, k, f) {
+    Reduce('TT_COMPOUND', n);
+    x = Pop();  k = c(x);  f = k[1];  k[1] = k[2];  k[2] = f;  Push(x);
+    OpSwap = .dummy;
+    nreturn;
+}
+/* ==================================================================================================================== */
+function DeclareOp(p, t, n, b) {
+    DeclareOp = .dummy;
+    if (LE(p, 0)) { uop_band[n] = ;  nreturn; }
+    b = 900;  b = LE(p, 700) 700;  b = LE(p, 600) 600;  b = LE(p, 500) 500;  b = LE(p, 400) 400;  b = LE(p, 200) 200;
+    if (EQ(SIZE(t), 3))                    uop_band[n] = 'in' b;
+    else if (IDENT(SUBSTR(t, 1, 1), 'f'))  uop_band[n] = 'pre' b;
+    else                                   uop_band[n] = 'post';
+    uop_on = uop_tok;
+    nreturn;
+}
+/* ==================================================================================================================== */
 arg       = ( *unify_expr | Graphic_atom . b_name epsilon . *Shift('TT_FNC', b_name) );
 args      = ( nInc() *arg FENCE(*args_tail | epsilon) );
 args_tail = ( $',' nInc() *arg FENCE(*args_tail | epsilon) );
@@ -158,6 +184,16 @@
                   *args $')'
                   reduce("'TT_COMPOUND'", 'nTop()')
               nPop()
+          |   $' ' '-' Float . p_negf
+                  epsilon . *Shift('TT_FLIT', '-' p_negf)
+          |   $' ' '-' Int . p_negi
+                  epsilon . *Shift('TT_ILIT', '-' p_negi)
+          |   *uop_on *IDENT(uop_band[uop_tx], 'pre200') *primary     reduce("'TT_COMPOUND'", 2)
+          |   *uop_on *IDENT(uop_band[uop_tx], 'pre400') *pow_expr    reduce("'TT_COMPOUND'", 2)
+          |   *uop_on *IDENT(uop_band[uop_tx], 'pre500') *mul_expr    reduce("'TT_COMPOUND'", 2)
+          |   *uop_on *IDENT(uop_band[uop_tx], 'pre600') *add_expr    reduce("'TT_COMPOUND'", 2)
+          |   *uop_on *IDENT(uop_band[uop_tx], 'pre700') *colon_expr  reduce("'TT_COMPOUND'", 2)
+          |   *uop_on *IDENT(uop_band[uop_tx], 'pre900') *unify_expr  reduce("'TT_COMPOUND'", 2)
           |   shift(Graphic_atom2, 'TT_FNC')
           |   Tk_cut                  reduce("'TT_CUT'", 0)
           |   "0'" ("''" | '\' LEN(1) | NOTANY(nl)) . p_cc
@@ -190,10 +226,6 @@
           |   $'{' $'}'             reduce("'TT_DCG_IL'", 0)
           |   $'{' *body $'}'       reduce("'TT_DCG_IL'", 1)
           |   *list
-          |   $' ' '-' Float . p_negf
-                  epsilon . *Shift('TT_FLIT', '-' p_negf)
-          |   $' ' '-' Int . p_negi
-                  epsilon . *Shift('TT_ILIT', '-' p_negi)
           |   $'\' $' ' *primary            reduce("'TT_BINOP'", 2)
           |   $' ' '-' $' ' *primary   reduce("'TT_UMINUS'", 1)
           |   $' ' '+' $' ' *primary   reduce("'TT_UPLUS'", 1)
@@ -201,6 +233,8 @@
 pow_expr  = (   *primary
                 FENCE( $'^'  *pow_expr  reduce("'TT_BINOP'", 2)
                      | $'**' *primary   reduce("'TT_BINOP'", 2)
+                     | *uop_on *IDENT(uop_band[uop_tx], 'in200') *pow_expr op_infix
+                     | *uop_on *IDENT(uop_band[uop_tx], 'post') op_postfix
                      | epsilon
                      )
             );
@@ -215,15 +249,18 @@
                          | $'//'  *pow_expr  reduce("'TT_IDIV'",  2)
                          | $'/\'  *pow_expr  reduce("'TT_BINOP'", 2)
                          | $'/'   *pow_expr  reduce("'TT_DIV'",   2)
+                         | *uop_on *IDENT(uop_band[uop_tx], 'in400') *pow_expr op_infix
                          ) *mul_tail | epsilon );
 add_expr  = (   *mul_expr *add_tail );
 add_tail  = FENCE( FENCE( $'+' *mul_expr  reduce("'TT_ADD'",   2)
                          | $'-' *mul_expr  reduce("'TT_SUB'",   2)
                          | $'\/' *mul_expr reduce("'TT_BINOP'", 2)
                          | $'xor' *mul_expr reduce("'TT_BINOP'", 2)
+                         | *uop_on *IDENT(uop_band[uop_tx], 'in500') *mul_expr op_infix
                          ) *add_tail | epsilon );
 colon_expr = (  *add_expr
                 FENCE( $':' *colon_expr  reduce("'TT_BINOP'", 2)
+                     | *uop_on *IDENT(uop_band[uop_tx], 'in600') *colon_expr op_infix
                      | epsilon
                      )
              );
@@ -249,24 +286,36 @@
                      | $'<'   *is_expr  reduce("'TT_LT'",   2)
                      | $'\='  *is_expr  reduce("'TT_NE1'",  2)
                      | $'=='  *is_expr  reduce("'TT_ID'",   2)
+                     | *uop_on *IDENT(uop_band[uop_tx], 'in700') *is_expr  op_infix
                      | epsilon
                      )
             );
-unify_expr = (  *cmp_expr
+eq_expr    = (  *cmp_expr
                 FENCE( $'=..' *cmp_expr  reduce("'TT_UNIV'",  2)
                      | $'='   *cmp_expr  reduce("'TT_UNIFY'", 2)
                      | epsilon
                      )
              );
+unify_expr = ( *eq_expr *op_tail );
+op_tail    = FENCE( *uop_on *IDENT(uop_band[uop_tx], 'in900') *eq_expr op_infix *op_tail | epsilon );
 /* ==================================================================================================================== */
 pfx_kw_name = (   "dynamic" | "discontiguous" | "meta_predicate" | "multifile"
               |   "module_transparent" | "thread_local" | "volatile"
               |   "initialization" | "thread_initialization" | "public" | "table"
               );
+op_type = ( 'xfx' | 'xfy' | 'yfx' | 'fy' | 'fx' | 'xf' | 'yf' );
+op_goal = (   $' ' 'op' $'(' nPush() epsilon . *Shift('TT_FNC', 'op') nInc()
+              shift(Int $ op_p, 'TT_ILIT') nInc() $','
+              shift(op_type $ op_t, 'TT_FNC') nInc() $','
+              $' ' ( "'" (BREAK("'") $ op_n . thx) "'" | (Atom | Graphic_atom) $ op_n . thx ) . *Shift('TT_FNC', thx) nInc()
+              $')' epsilon $ *DeclareOp(op_p, op_t, op_n)
+              reduce("'TT_COMPOUND'", 'nTop()') nPop()
+          );
 body_goal = (   $'(' *body $')'
             |   $' ' pfx_kw_name . pfx_kw $'  ' *unify_expr
                     reduce("'TT_PFX'", 1)
             |   $' ' '\+' $' ' *body_goal  reduce("'TT_NAF'", 1)
+            |   *op_goal
             |   *unify_expr
             );
 conj = (    nPush()
```
