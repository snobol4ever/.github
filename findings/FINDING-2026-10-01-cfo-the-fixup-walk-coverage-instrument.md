# FINDING 2026-10-01 cfo -- a sequential per-block fixup walk reaches every heap slot the mark registers, except ~500 slots in root-held HB_WSB tables

Measured 12:08 CDT on SCRIP c798131e2 + the patch below (RT_DIAG, env SCRIP_GC_FIXWALK_AUDIT=1, NOT landed).

After the mark, every marked block of a moving type has its content visitor re-run, bypassing the HBF_VIS gate. Its slots
are appended to g_gc_slots after the mark's own, the heap-located slots of the two halves are sorted and diffed, and
g_gc_nslot is cut back. Blocks are already marked and aggregates already flagged, so nothing recurses and nothing
new is marked.

READINGS (every collection of each run, outputs MATCH their refs):
- treebank x1024 -d512m -i1m -s256m: 19 collections, missing=528 or 529, extra=0, newly_marked=0.
- concord: 129 collections, missing=464, newly_marked=0.
- geddump: 19 collections, missing=476 or 480, newly_marked=0.
Every missing slot is inside an HB_WSB block, starting at the arena's first block (arena+16, +24, +32 ...). That is a
root-held table whose slots the root walkers register. No slot inside a moving block is missed.

WHAT IT MEANS FOR THE ROW gc-speed-the-mark-phase-...: the SPITBOL-shaped fixup is feasible. Record slots in the
root phase and skip them in the mhead drain; run the per-block walk BEFORE the recorded fixup, which is idempotent
since f6177b6e2, so an overlap costs a rewrite of the same word and never a wrong one. ⛔ THE GAIN IS UNPROVEN: the
walk must find each target again (a pmap read, or header = p - 16 when p is a payload start) in exchange for the
random store into the holder that it saves. Measure a prototype before landing.

THE PATCH (gc_heap.c, placed before gc_collect_ex, called after the mark drain under RT_DIAG and the env):
```diff
diff --git a/src/runtime/rt/gc_heap.c b/src/runtime/rt/gc_heap.c
index 14721d252..f7986e4e0 100644
--- a/src/runtime/rt/gc_heap.c
+++ b/src/runtime/rt/gc_heap.c
@@ -1801,6 +1801,41 @@ static void gc_assert_check(void)
 }
 #endif
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
+#if RT_DIAG
+static int gc_fixwalk_cmp(const void *x, const void *y) { uintptr_t a = *(const uintptr_t *)x, b = *(const uintptr_t *)y; return a < b ? -1 : (a > b ? 1 : 0); }
+static void gc_fixwalk_audit(void)
+{
+    extern void pl_db_gc_visit(uint16_t, void *, size_t); extern void pm_struct_gc_visit(uint16_t, void *, size_t);
+    long n0 = g_gc_nslot, i, nb = 0, nm = 0, nw = 0, miss = 0, extra = 0, fresh = 0, shown = 0, j, k;
+    for (i = 0; i < g_gc_nblk; i++) { rt_hblk_t *h = g_gc_idx[i]; void *b = (void *)(h + 1); size_t pb = (size_t)h->size - sizeof(rt_hblk_t);
+        if (!(h->flags & HBF_MARK) || !gc_type_moves(h->type)) continue;
+        nb++;
+        if (h->type == HB_DVEC) { DESCR_t *v = (DESCR_t *)b; long n = (long)(pb / sizeof(DESCR_t)); for (long q = 0; q < n; q++) gc_wl_push(&v[q]); }
+        else if (h->type == HB_ARR) gc_visit_arblk((ARBLK_t *)b);
+        else if (h->type == HB_DINST) gc_visit_datinst((DATINST_t *)b);
+        else if (h->type >= HB_PLDB && h->type <= HB_PLDBK) pl_db_gc_visit(h->type, b, pb);
+        else if (h->type == HB_DTP || h->type == HB_DTPRCP) pm_struct_gc_visit(h->type, b, pb);
+        else if (h->type == HB_PVEC) { const char **v = (const char **)b; long n = (long)(pb / sizeof(void *)); for (long q = 0; q < n; q++) if (v[q]) rt_gc_visit_raw(&v[q]); }
+        else if (h->type == HB_AGGV) gc_visit_vcell((VCELL_t *)b);
+        else if (h->type == HB_AGGP) { TBPAIR_t *e = (TBPAIR_t *)b; rt_gc_visit_descr(&e->key_descr); rt_gc_visit_descr(&e->val); }
+        else if (h->type == HB_AGGT) gc_visit_tbblk((struct _TBBLK_t *)b);
+        g_gc_wl_draining = 1; while (g_gc_wln > 0) gc_visit_one(g_gc_wl[--g_gc_wln]); g_gc_wl_draining = 0; }
+    while (g_gc_mhead) { rt_hblk_t *h = g_gc_mhead; g_gc_mhead = (rt_hblk_t *)(uintptr_t)h->fwd; h->fwd = 0; fresh++; }
+    { long n1 = g_gc_nslot; uintptr_t *a = (uintptr_t *)gcbk_alloc((size_t)(n1 + 1) * sizeof(uintptr_t));
+      for (i = 0; i < n0; i++) { const char *l = (const char *)g_gc_slots[i].loc; if (l >= g_hp_arena && l < g_hp_top) a[nm++] = (uintptr_t)l; }
+      for (i = n0; i < n1; i++) { const char *l = (const char *)g_gc_slots[i].loc; if (l >= g_hp_arena && l < g_hp_top) a[nm + nw++] = (uintptr_t)l; }
+      qsort(a, (size_t)nm, sizeof *a, gc_fixwalk_cmp); qsort(a + nm, (size_t)nw, sizeof *a, gc_fixwalk_cmp);
+      for (j = 0, k = 0; j < nm || k < nw;) { uintptr_t x = j < nm ? a[j] : UINTPTR_MAX, y = k < nw ? a[nm + k] : UINTPTR_MAX;
+          if (x == y) { while (j < nm && a[j] == x) j++; while (k < nw && a[nm + k] == y) k++; continue; }
+          if (x < y) { rt_hblk_t *hh = gc_blk_of((const char *)x); miss++;
+              if (shown++ < 8) fprintf(stderr, "[GC-FIXWALK] MISSING slot arena+%ld in kind=%u/%s at +%ld -- the mark registered it and no per-block walk reaches it\n", (long)((const char *)x - g_hp_arena), hh ? (unsigned)hh->type : 0u, hh ? HB_KIND_NAME(hh->type) : "-", hh ? (long)((const char *)x - (const char *)(hh + 1)) : -1L);
+              while (j < nm && a[j] == x) j++; continue; }
+          extra++; while (k < nw && a[nm + k] == y) k++; }
+      gcbk_drop((void *)a); }
+    g_gc_nslot = n0;
+    fprintf(stderr, "[GC-FIXWALK] run=%ld moving_blocks=%ld mark_heap_slots=%ld walk_heap_slots=%ld missing=%ld extra=%ld newly_marked=%ld\n", g_gc_runs + 1, nb, nm, nw, miss, extra, fresh);
+}
+#endif
 static long gc_collect_ex(void)
 {
     extern void kw_cset_gc_roots(void); extern void core_gc_roots(void); extern void dat_gc_roots(void); extern void gen_gc_roots(void); extern void pas_gc_roots(void); extern void pl_gc_roots(void); extern void rt_gc_root_args(void); extern void rt_gc_ws_roots(void); extern void eval_gc_roots(void); extern void lower_gc_roots(void); extern void bnd_gc_roots(void); extern void drv_gc_roots(void); extern int rt_scan_active(void);
@@ -1926,6 +1961,9 @@ static long gc_collect_ex(void)
       if (w_tel) { n_mrk = gc_walk_ns() - n_t0; n_t0 = gc_walk_ns(); fprintf(stderr, "[ZGC-MARK] arm=%s titles-walked=%ld blocks-scanned=%ld rounds=%ld nblk=%ld\n", "WL", walked, nscan, rounds, g_gc_nblk); n_t0 = gc_walk_ns(); }
 #endif
     }
+#if RT_DIAG
+    if (getenv("SCRIP_GC_FIXWALK_AUDIT")) gc_fixwalk_audit();
+#endif
     { extern void kw_cset_gc_weak(void); kw_cset_gc_weak(); }
 #ifdef SCRIP_GC_AUDIT_B
 #if RT_DIAG
```
