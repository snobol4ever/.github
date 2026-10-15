# FINDING 2026-10-15 (cfo): asserting a big or deep clause overflows the stack in three stages, and the frame layout is super-quadratic in its goal count

Row: `prolog-swi-db-test-db-every-case-agrees-with-swipl-in-both-modes-ceo-1664` (cfo). SWI `db/test_db.pl` reads 16/17 graded per mode on SCRIP a5e3d2d5a; the one red is `res_compiler:big_clause#1` (swipl PASS, SCRIP no verdict): `test_big_clause(60000)` asserts `tmp(V0,V) :- succ(V0,V1), succ(V1,V2), ...` with 60000 goals, calls it, erases it. The cto's 2026-10-14 finding named the road; this measures it.

## Measured (SCRIP a5e3d2d5a, load ~1.5, `-O0`, default 4 MB stack)

| goals N | assert (cputime) | result |
|---|---|---|
| 2000 | 0.60 s | x=2000 |
| 4000 | 2.53 s | x=4000 |
| 8000 | 12.72 s | x=8000 |
| 16000 | -- | ERROR 246 stack overflow |

Growth ~N^2.3; at 60000 the extrapolation is ~20 minutes even without the overflow. swipl answers at once.

A fact with a 50000-deep nested argument (`assertz(deep(f(f(...z))))`) also dies with ERROR 246 in SCRIP (swipl: fine).

## Where (gdb at the SIGSEGV; callgrind on N=2000, 7.09 G Ir)

1. RUNTIME -- `pl_cell_tree` (src/runtime/by_name_dispatch.c, the clause-to-`tree_t` reader of `rt_pl_clause_tree`) recurses once per argument level: 11490 frames at N=16000, ~13000 frames on the deep fact. Its variable lookup is also a linear scan of the variables seen so far (quadratic in the clause's variable count). A cure for the recursion is ready (below): iterate down the LAST argument, recurse only into the others; lists keep their own loop.
2. COMPILER -- with (1) cured, the deep fact overflows next in `pl_head_term` (src/lower/lower_prolog.c), 26000+ frames, one per nesting level (`pl_runtime_define_fragment` -> `pl_runtime_define_pred_x` -> lowering). N=16000 runs 41 s and then overflows past (1) as well; the body lowering is the likely next frame.
3. COMPILER -- the time: `zls_direct_slot` 27.6% of Ir, `zls_build` 7.0%, `zls_reuse_detleaf` 5.7% (src/ir/frame_layout.c), `codegen_flat_chain_body` 7.5% (src/emitter/emit.cpp), `strcmp` 9.4%. The frame layout is the super-quadratic part.

Stages 2 and 3 are the compile road that every run-time assert takes (`pl_db_store(recompile=1)`), and stage 3 is the frame layout hq_zetas is rewriting for Prolog under OCTET (CEO-1778); so the cfo did NOT land (1) alone -- no program observes it while (2) overflows one stage later -- and hands the road to the ceo to assign.

## The ready cure for stage 1 (applies to by_name_dispatch.c at a5e3d2d5a)

```diff
diff --git a/src/runtime/by_name_dispatch.c b/src/runtime/by_name_dispatch.c
index b02868f76..ff3651e23 100644
--- a/src/runtime/by_name_dispatch.c
+++ b/src/runtime/by_name_dispatch.c
@@ -22553,7 +22553,28 @@ static tree_t * pl_cell_tree(DESCR_t *c, pl_ctv_t *vt) {
             }
             return lst;
         }
-        { tree_t *t = ast_node_new(TT_FNC); t->v.sval = pl_tree_name(nm ? nm : "?"); for (int i = 0; i < ar; i++) ast_push(t, pl_cell_tree(&aa[i], vt)); return t; }
+        {
+            tree_t *root = ast_node_new(TT_FNC);
+            tree_t *t = root;
+            t->v.sval = pl_tree_name(nm ? nm : "?");
+            for (;;) {
+                DESCR_t *ld;
+                const char *ln;
+                for (int i = 0; i + 1 < ar; i++) ast_push(t, pl_cell_tree(&aa[i], vt));
+                if (ar < 1) return root;
+                ld = (DESCR_t *)pl_deref((pl_cell_t *)&aa[ar - 1]);
+                ln = (int)ld->v == DT_PLREF && !pl_rat_is(*ld) ? prolog_atom_name(plc_functor((pl_cell_t *)ld)) : (const char *)0;
+                if (!ln || (!strcmp(ln, ".") && pl_arity((pl_cell_t *)ld) == 2)) { ast_push(t, pl_cell_tree(&aa[ar - 1], vt)); return root; }
+                ar = pl_arity((pl_cell_t *)ld);
+                aa = (DESCR_t *)ld->p;
+                {
+                    tree_t *n = ast_node_new(TT_FNC);
+                    n->v.sval = pl_tree_name(ln);
+                    ast_push(t, n);
+                    t = n;
+                }
+            }
+        }
     }
     { tree_t *t = ast_node_new(TT_QLIT); t->v.sval = pl_tree_name("?"); return t; }
 }
```

## Probes

`bN.pl`: `link_clause(N, V0, V, Body)` as in test_db.pl, then `assert((tmp(V0, V) :- Body), Ref)` timed by `statistics(cputime, _)`, `tmp(0, X)`, `erase(Ref)`. `deep.pl`: `nest(50000, T), assertz(deep(T))`.
