# FINDING 2026-10-22 cfo -- the home pass's per-predicate retains fact is not sound for Prolog

The cto's ask of 2026-10-22 13:0x CDT, on the Prolog switch row (prolog-the-frame-regime-switches-onto-the-home-set-...-ceo-1884): before planner_retains lands, measure the per-predicate retains fact against the blanket. The blanket is `bb_proc_target_retains`, which reads `zls_g_resumable_frame` and so answers 1 for every Prolog predicate (lower_prolog.c line 5622 sets `resumable_callable` on every Prolog graph). The per-predicate fact is the home pass's transitive `rt` in `zls_home_callees_mark`, flagged at a call site as `FCN_HRET`, code 5 in `zls_home_dyn`.

How it was read: a scratch print on origin SCRIP bcd2ef252 (worktree `.scratch/base`, never landed), gated on `CFO_RETAINS`. It prints one `[RT-HOME]` line per graph (local and transitive rt, plus counts of DISJUNCTION, TO and TO db, holding GATE, CALL_VALUE, SUCCEED), one `[RT-SITE]` line per call site (code hret, det or unres), and one `[RT-PROC]` line per proc (blanket, rt_redefinable). It ran compile-only over `util_spine_population.sh --lang prolog` (58 programs, all rc 0, about 80 s at load 6-8). User predicates are the clause heads `out/parser_prolog` reads in the source; every other proc is library.

## The verdict

`zls_home_local_retain` counts a graph retaining only for SUSPEND, CREATE, ACTIVATE, CORET, COFAIL, CALL_VALUE, CALL_GEN or PROC_GEN, or for more than one SUCCEED. Five Prolog classes that leave a choice point at the predicate's exit pass that test. Each is witnessed nondeterministic against swipl. SCRIP prints swipl's answers today only because the blanket marks every predicate retaining.

1. **dyn** -- a dynamic predicate's static graph is the empty stub `GOTO -> FAIL` (`rt_redefinable = 1`), so it reads as det, and so does every caller that reaches it.
2. **dj** -- a single clause with an in-body disjunction whose arms resume to the DISJUNCTION itself. That DISJUNCTION is not `zls_dj_retains` and not `zd_pl_dj_holds`.
3. **to-db** -- `clause/2` or `retract/1` enumeration inline (TO `db:trl`).
4. **to-gen** -- the `ag:trl` generators: `atom_concat/3`, `sub_atom/5`, `bagof`/`setof` with free variables, `between`/`for`.
5. **gate** -- a GATE that `zd_gate_holds` reads as holding.

For Prolog, the local test needs `rt_redefinable`, any DISJUNCTION of two or more arms, any TO and `zd_gate_holds` folded into it, and the callee walk has to pass through them. Within one graph the planner's `zd_edge_retains` already lists the GATE, DISJUNCTION, CALL_VALUE and TO db edges.

### The witness (`/usr/bin/swipl` 9.0.4 `-q`, SCRIP mode 3 at bcd2ef252: identical output)

```prolog
:- dynamic f2/1.
f(1).
f(2).
m(1, a).
m(2, b).
q(X) :- ( X = a ; X = b ).
c(X, Y) :- atom_concat(X, Y, ab).
d(H) :- clause(f(H), true).
e(X) :- f2(X).
s(X) :- sub_atom(ab, _, 1, _, X).
b(L) :- bagof(X, m(X, _), L).
main :- assertz(f2(x)), assertz(f2(y)),
    forall(q(A), (write(q(A)), nl)),
    forall(c(B, C), (write(c(B, C)), nl)),
    forall(d(D), (write(d(D)), nl)),
    forall(e(E), (write(e(E)), nl)),
    forall(s(F), (write(s(F)), nl)),
    forall(b(G), (write(b(G)), nl)).
:- initialization(main).
```

Output: `q(a) q(b) c(,ab) c(a,b) c(ab,) d(1) d(2) e(x) e(y) s(a) s(b) b([1]) b([2])`, one per line. The home pass reads `q/1`, `c/2`, `d/1`, `e/1`, `s/1` and `f2/1` as trans=0 (det). It reads `b/1` as retaining only because `m/2` has two clauses.

## The counts (58 programs)

| population | n | home-retaining | home-det | clean det | unsound det (class=n) |
|---|---|---|---|---|---|
| user predicates | 975 | 850 | 125 | 113 | 12 (dyn 3, reach-dyn 4, dj 2, to-gen 2, gate 1), in 7 programs |
| user CALL_PROC_STAGED sites | 2,229 | 1,982 | 247 | 182 | 65 (dyn 52, reach-dyn 5, gate 4, to-gen 2, dj 2), in 8 programs |
| every proc of every compile unit, library included | 17,768 | 6,612 | 11,156 | 10,849 | 307 (dyn 138, to-gen 64, to-db 59, gate 22, dj 11, reach-gate 9, reach-dyn 4) |
| every CALL_PROC_STAGED site | 13,126 | 11,932 | 1,194 | 1,033 | 161 (dyn 60, gate 47, dj 26, reach-gate 18, reach-dyn 5, to-gen 5) |

Unresolved callees: 0. The blanket answers 1 for all 17,826 procs, the 58 root graphs included.

I read the 113 clean user predicates by eye. All are deterministic: single facts (`houses/1`, `successors/2`, `virtual/3`), arithmetic tests (`nd/2`, `before/2`, `sumdigit/5`, an if-then-else that commits), assert wrappers, and the Logtalk adapter's stubs that fail (`clause/3`, `current_module/1`, `with_mutex/2`). What a sound per-predicate fact would buy over the blanket: **182 of 2,229 user sites (8.2%) and 1,033 of 13,126 sites (7.9%) become definite, in 20 programs.**

The real-program cases each check against their source:
- `prolog_parser.pl`: `is_alpha(C) :- is_lower(C) ; is_upper(C).` and `is_alnum/1` (dj).
- `eliza.pl`: `resID/2` is `:- dynamic` and retracted (dyn).
- `nand.pl`: `access(N, A) :- state_(N, A).` reaches the dynamic `state_/2` (reach-dyn).
- `family_prolog.pl`: `grandparent/2` reaches the dynamic `parent/2`, and `gp_line/1` holds two `atom_concat` TOs.
- `reducer.pl`: `list_functor_name/1` is a holding GATE.

## Per program

| program | user preds | home-det | unsound (class=n) | user sites | det sites | unsound det sites |
|---|---|---|---|---|---|---|
| boyer.pl | 27 | 1 | - | 38 | 1 | - |
| browse.pl | 18 | 0 | - | 34 | 0 | - |
| cal.pl | 7 | 0 | - | 9 | 0 | - |
| chat_parser.pl | 159 | 19 | - | 367 | 70 | - |
| crypt.pl | 11 | 0 | - | 29 | 0 | - |
| deriv.pl | 3 | 0 | - | 14 | 0 | - |
| derive.pl | 7 | 0 | - | 20 | 0 | - |
| det.pl | 4 | 1 | - | 5 | 0 | - |
| divide10.pl | 5 | 0 | - | 16 | 0 | - |
| eval.pl | 7 | 0 | - | 8 | 0 | - |
| fast_mu.pl | 11 | 0 | - | 14 | 0 | - |
| fib.pl | 3 | 0 | - | 4 | 0 | - |
| flatten.pl | 30 | 0 | - | 57 | 0 | - |
| ham.pl | 9 | 0 | - | 12 | 0 | - |
| log10.pl | 5 | 0 | - | 16 | 0 | - |
| meta_qsort.pl | 9 | 0 | - | 19 | 0 | - |
| moded_path.pl | 8 | 0 | - | 7 | 0 | - |
| mu.pl | 10 | 0 | - | 14 | 0 | - |
| nand.pl | 44 | 10 | reach-dyn=2 | 190 | 50 | dyn=1, reach-dyn=3 |
| nrev.pl | 6 | 0 | - | 8 | 0 | - |
| nreverse.pl | 4 | 0 | - | 5 | 0 | - |
| ops8.pl | 5 | 0 | - | 16 | 0 | - |
| perfect.pl | 11 | 1 | - | 16 | 1 | - |
| pingpong.pl | 6 | 1 | - | 6 | 0 | - |
| poly_10.pl | 14 | 0 | - | 33 | 0 | - |
| prover.pl | 12 | 0 | - | 30 | 0 | - |
| qsort.pl | 4 | 0 | - | 7 | 0 | - |
| queens.pl | 8 | 0 | - | 11 | 0 | - |
| queens_8.pl | 7 | 0 | - | 9 | 0 | - |
| queensn.pl | 10 | 1 | - | 14 | 1 | - |
| query.pl | 6 | 0 | - | 6 | 0 | - |
| reducer.pl | 45 | 2 | gate=1 | 112 | 5 | gate=4 |
| sendmore.pl | 6 | 1 | - | 13 | 4 | - |
| serialise.pl | 10 | 1 | - | 18 | 2 | - |
| sieve.pl | 8 | 1 | - | 10 | 1 | - |
| simple_analyzer.pl | 73 | 2 | - | 147 | 4 | - |
| tak.pl | 3 | 0 | - | 6 | 0 | - |
| times10.pl | 5 | 0 | - | 16 | 0 | - |
| witness_depth_nrev8.pl | 5 | 0 | - | 7 | 0 | - |
| zebra.pl | 7 | 1 | - | 20 | 1 | - |
| advent__advent.pl | 49 | 0 | - | 113 | 9 | dyn=2 |
| eliza__eliza.pl | 25 | 3 | dyn=1 | 81 | 15 | dyn=3 |
| family_net__family_prolog.pl | 22 | 4 | reach-dyn=1, to-gen=1 | 41 | 21 | dyn=19, reach-dyn=1, to-gen=1 |
| family_prolog.pl | 22 | 4 | reach-dyn=1, to-gen=1 | 41 | 21 | dyn=19, reach-dyn=1, to-gen=1 |
| leancop__leancop.pl | 56 | 2 | dyn=1 | 269 | 6 | dyn=5 |
| logtalk__adapters__scrip.pl | 72 | 56 | - | 19 | 0 | - |
| logtalk__integration__gp145_format_shim.pl | 0 | 0 | - | 0 | 0 | - |
| logtalk__integration__logtalk_gp_scrip.pl | 0 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_contributions.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_core.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_examples.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_libraries.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_packs.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_ports.pl | 1 | 0 | - | 0 | 0 | - |
| logtalk__paths__paths_tools.pl | 1 | 0 | - | 0 | 0 | - |
| prolog_parser.pl | 39 | 8 | dj=2, dyn=1 | 124 | 13 | dj=2, dyn=3 |
| prolog_recognizer.pl | 50 | 6 | - | 158 | 22 | - |

## The scratch print (never landed; for a re-read)

```diff
diff --git a/src/driver/scrip.c b/src/driver/scrip.c
index e1cec49ac..55c9a188d 100644
--- a/src/driver/scrip.c
+++ b/src/driver/scrip.c
@@ -696,6 +696,8 @@ static void drive_slots_all(stage2_t * s2) {
     }
     for (int i = 0; i < s2->proc_count; i++) if (s2->proc_table[i].is_generator && s2->proc_table[i].bb_idx >= 0 && s2->proc_table[i].bb_idx < s2->bbp.count)
         zls_g_generator_set(s2->bbp.table[s2->proc_table[i].bb_idx]);
+    if (getenv("CFO_RETAINS")) { extern int bb_proc_target_retains(const char *); for (int i = 0; i < s2->proc_count; i++) { int bi = s2->proc_table[i].bb_idx; IR_graph_t * g = (bi >= 0 && bi < s2->bbp.count) ? s2->bbp.table[bi] : (IR_graph_t *)0;
+        fprintf(stderr, "[RT-PROC] g=%d name=%s blanket=%d zf=%d cf=%d rc=%d root=%d n=%d rd=%d\n", bi, s2->proc_table[i].name ? s2->proc_table[i].name : "?", bb_proc_target_retains(s2->proc_table[i].name), g ? g->zframe_graph : -1, g ? g->cell_frame : -1, g ? g->resumable_callable : -1, g ? g->root_graph : -1, g ? g->n : -1, g ? g->rt_redefinable : -1); } }
 }
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
 static long parse_mem_arg(const char *s) {
diff --git a/src/ir/frame_layout.c b/src/ir/frame_layout.c
index 5c3ecb9d8..97c2aba67 100644
--- a/src/ir/frame_layout.c
+++ b/src/ir/frame_layout.c
@@ -1783,6 +1783,7 @@ static int zls_home_callee(const char * const * nm, const int * gx, int cap, con
     while (nm[h] && strcmp(nm[h], s)) h = (h + 1) & (uint32_t)(cap - 1);
     return nm[h] ? gx[h] : -1;
 }
+static const IR_t * zls_chase_fwd(const IR_t * t) { int g = 0; while (t && (t->op == IR_GOTO || (t->op == IR_SUCCEED && t->γ.node)) && g++ < 4096) t = t->γ.node; return t; }
 void zls_home_callees_mark(IR_graph_t ** gs, int n, const char ** pn, const int * px, int np) {
     int cap = 16;
     while (cap < 2 * np + 2) cap <<= 1;
@@ -1798,6 +1799,7 @@ void zls_home_callees_mark(IR_graph_t ** gs, int n, const char ** pn, const int
         gx[h] = px[k];
     }
     for (int k = 0; k < n; k++) { rt[k] = gs[k] ? (unsigned char)zls_home_local_retain(gs[k]) : 0; hs[k] = gs[k] ? (unsigned char)zls_home_holds_retain(gs[k]) : 0; }
+    unsigned char rt0[n > 0 ? n : 1]; for (int k = 0; k < n; k++) rt0[k] = rt[k];
     for (int changed = 1; changed;) {
         changed = 0;
         for (int k = 0; k < n; k++) for (int i = 0; gs[k] && !rt[k] && i < gs[k]->n; i++) {
@@ -1813,7 +1815,18 @@ void zls_home_callees_mark(IR_graph_t ** gs, int n, const char ** pn, const int
         int h = zls_home_callee(nm, gx, cap, IR_LIT(x).sval);
         if (h < 0) fcn_flag(x, FCN_HUNRES);
         else if (rt[h] && !(gs[h]->cell_frame && !hs[h])) fcn_flag(x, FCN_HRET);
-    }
+        if (getenv("CFO_RETAINS")) fprintf(stderr, "[RT-SITE] g=%d kind=%s callee=%s h=%d code=%s\n", k, bb_op_name(ir_kind0(x)), IR_LIT(x).sval, h, h < 0 ? "unres" : (rt[h] && !(gs[h]->cell_frame && !hs[h])) ? "hret" : "det");
+    }
+    if (getenv("CFO_RETAINS")) for (int k = 0; k < n; k++) if (gs[k]) {
+        int c_to = 0, c_todb = 0, c_dj = 0, c_djr = 0, c_gate = 0, c_gater = 0, c_cv = 0, c_succ = 0, c_cut = 0;
+        for (int i = 0; i < gs[k]->n; i++) { const IR_t * x = gs[k]->all[i]; if (!x) continue; int o = (int)ir_kind0(x);
+            if (x->op == IR_TO) { c_to++; if (ir_range_kind_is(x, "db")) c_todb++; }
+            if (x->op == IR_DISJUNCTION) { c_dj++; int na = (int)IR_LIT(x).ival, r = 0; for (int a = 0; na > 0 && x->n_operands >= 2 * na && a < na; a++) { const IR_t * t = zls_chase_fwd(x->operands[2 * a + 1]); if (t && t != x && t->op != IR_FAIL && t->op != IR_SUCCEED && t->op != IR_UNMARK && t->op != IR_CUT) r = 1; } c_djr += r; }
+            if (x->op == IR_GATE) { c_gate++; int r = 0; for (int j = 0; j < x->n_operands; j++) { const IR_t * a = x->operands[j]; if (!a || a->op != IR_GATE_ARM || !(int)a->seal || a->n_operands < 1) continue; const IR_t * t = zls_chase_fwd(a->operands[0]); if (t && t != x && t->op != IR_SUCCEED && t->op != IR_FAIL && t->op != IR_UNMARK && t->op != IR_CUT) r = 1; } c_gater += r; }
+            if (o == IR_CALL_VALUE) c_cv++;
+            if (x->op == IR_SUCCEED) c_succ++;
+            if (x->op == IR_CUT) c_cut++; }
+        fprintf(stderr, "[RT-HOME] g=%d local=%d trans=%d hs=%d cf=%d to=%d todb=%d dj=%d djr=%d gate=%d gater=%d cv=%d succ=%d cut=%d\n", k, rt0[k], rt[k], hs[k], gs[k]->cell_frame, c_to, c_todb, c_dj, c_djr, c_gate, c_gater, c_cv, c_succ, c_cut); }
 }
 static int zls_home_dyn(const IR_graph_t * g, const IR_t * nd) {
     switch ((int)ir_kind0(nd)) {
```
