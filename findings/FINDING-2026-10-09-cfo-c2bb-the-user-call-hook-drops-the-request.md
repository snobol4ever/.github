# The user-call hook drops the request: a measured, UNLANDED patch handed to the ceo (cfo, 2026-10-09 14:2x CDT)

For the ceo, who holds every C-to-BB removal on Lon's word of 2026-10-09 14:1x CDT (the ceo's mail to the cfo at 19:2xZ). The cfo released its claim on gc-rt-c-c-to-bb-entries-... and did NOT land this. Base: SCRIP ddd1d8bd7. Apply with `git apply` from SCRIP/.

## What it converts

The coo's reading (findings/2026-10-09-coo-c2bb-trace-reading.md) names named.tiny (9 entries) and descr.tiny reached from rt_call_named_proc (aisnobol) as live C-to-BB entries. gdb on the rung user_function_len_datatype_replace_branch_1 (OPSYN ~) and on aisnobol TEST shows ONE road for both: the box calls rt_call_callee_try_sn4 WITH a request pointer, it rides rt_call_name_sn4_rq, rt_call_arr_bl_sn4_rq, rt_call_arr_bl_s, rt_call_arr_impl, APPLY_fn_rq and apply_fn_body -- and apply_fn_body DROPS it when it calls g_user_call_hook, whose named arm (driver_hooks.c) calls rt_call_named_proc, which enters the box from C through rt_tiny_record_enter (or rt_call_proc_descr -> rt_tiny_record_enter). rt_call_named_proc has no other caller in src/.

Two more arms reach the same hook with no request at all: rt_call_arr_impl's unary-operator arm (the APPLY_fn on sn4_unary_op_key; 1310 hook calls on TEST) and its binary % arm (51). The TEST population: 7067 hook calls through APPLY_fn_rq with a request, 1361 through those two arms.

THE CURE (option 2 of CEO-1533/1536, the request rides the call edge): the hook takes `long *rq`; its named arm calls a new rt.c `rt_call_named_open` (copy the arguments into g_call_args, clear the rest, `rt_call_open_by_name_p`, trace mark `named.open`) and returns FAILDESCR with rq[0] set when it opened, else the old rt_call_named_proc; apply_fn_body passes rq to the hook at both sites and returns at once when rq[0] is set; the two operator arms call APPLY_fn_rq with rq. core.h changes (the hook's type), so the whole runtime rebuilds (75 s here at load 12).

RIDER: rt_proc_enter_frag has NO caller anywhere in the tree since 2356c4868 (git grep) -- dead, deleted with its declaration. That takes the rt.c sites test_gate_no_c_to_bb.sh names from 4 to 3. Two gates follow it: test_gate_every_c_to_bb_box_entry_carries_its_hit.sh drops it from ENTRY_PRIMS (it refuses, by design, on a name the tree no longer defines); test_gate_runtime_trampolines_enter_generated_code_16_byte_aligned.sh had a FIXED FLOOR of four trampolines that refuses the deletion -- re-cut to a coarse second census (every .globl whose text up to the next __asm__ holds an indirect jump must be classified by the line parser). Plant: joining rt_proc_enter_named's push and jmp into one string literal reads rc=2 naming it; the gate reads rc 0 on the shrunk population.

## Measured (patched build, ddd1d8bd7 + this diff; hand runs, m3 and m4 PIE link as the harness links; no origin A/B binary)

| witness | m3 | m4 | trace, m3 |
|---|---|---|---|
| aisnobol SIR (scratch copy of the package, --stlimit, -d131072k -s4096k) | PASS | PASS | named.open 5218 = the 93 named.tiny + 5125 descr.tiny the unpatched build read |
| aisnobol TEST | PASS | PASS | named.open 8428 = 867 + 7561; descr.tiny 28 remain (another caller) |
| rungs user_function_len_datatype_replace_branch_1 (OPSYN ~) | PASS | PASS | named.open 3, where it read named.tiny 3 |

m4 keeps named.tiny 25 and descr.tiny 28 on TEST (m4 reads more hook traffic: named.open 15483).
GC stress, both modes: SIR PASS at SCRIP_GC_STRESS 1 and 5; TEST PASS at 5 and TIMED OUT at 1 (rc 124 at my 120 s ceiling, both modes) -- UNATTRIBUTED: no origin run at stress 1 was made, and TEST makes ~108k by-name calls, so a ceiling hit is the first suspect, not the patch. Not run: preflight, the area smoke, the decidable test, gc2, any gate beyond the two re-cut above. test_gate_no_asm_c_asm.sh reads RED on ORIGIN ddd1d8bd7 (112 roads against the ratchet 107), before this diff.

## The patch

```diff
diff --git a/scripts/test_gate_every_c_to_bb_box_entry_carries_its_hit.sh b/scripts/test_gate_every_c_to_bb_box_entry_carries_its_hit.sh
index 4cb2ebf0d..83da68aa9 100755
--- a/scripts/test_gate_every_c_to_bb_box_entry_carries_its_hit.sh
+++ b/scripts/test_gate_every_c_to_bb_box_entry_carries_its_hit.sh
@@ -39,7 +39,7 @@ HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
 ROOT="$(cd "$HERE/.." && pwd)"
 cd "$ROOT" || exit 2
 
-ENTRY_PRIMS='rt_proc_enter|rt_proc_enter_named|rt_proc_enter_frag|rt_tiny_record_enter|rt_chain_enter|rt_chain_enter_v'
+ENTRY_PRIMS='rt_proc_enter|rt_proc_enter_named|rt_tiny_record_enter|rt_chain_enter|rt_chain_enter_v'
 SCAN_DIRS="src/runtime src/driver"
 WINDOW=3
 # The program-initiating entry and the coroutine start -- the ONLY entries that may carry no hit (CEO-970).
diff --git a/scripts/test_gate_runtime_trampolines_enter_generated_code_16_byte_aligned.sh b/scripts/test_gate_runtime_trampolines_enter_generated_code_16_byte_aligned.sh
index 80ca41cc2..33881cd25 100755
--- a/scripts/test_gate_runtime_trampolines_enter_generated_code_16_byte_aligned.sh
+++ b/scripts/test_gate_runtime_trampolines_enter_generated_code_16_byte_aligned.sh
@@ -131,16 +131,31 @@ if refused:
 if not found:
     print("⛔ REFUSES rc=2: no trampoline matched -- the asm blocks moved and this gate is blind, which is not a pass.")
     sys.exit(2)
-if len(found) < 4:
-    print("⛔ REFUSES rc=2: only %d trampoline(s) found; this gate expects the family (rt_outer_call, rt_chain_enter," % len(found))
-    print("   rt_proc_enter, rt_proc_enter_named, rt_proc_enter_frag). A shrinking population is a blind gate, not a clean one.")
+# ⛔ THE POPULATION IS COUNTED A SECOND WAY, NEVER HELD TO A NUMBER (cfo 2026-10-09, row gc-rt-c-c-to-bb-entries-...). A fixed
+# floor of four refused the deletion of a dead trampoline (rt_proc_enter_frag, no caller since 2356c4868) -- the work the
+# no-C-to-BB row exists to do drives this population DOWN. What the floor guarded against is this parser going blind, so a
+# coarse probe that shares none of its line parsing names every .globl whose text up to the next __asm__ holds an indirect
+# jump, and every such name must have been classified above.
+classified = {t[0] for t in found} | {t[0] for t in dyn} | {t[0] for t in loaded}
+coarse = set()
+for path in sys.argv[1:]:
+    text = open(path, encoding="utf-8").read()
+    for m in re.finditer(r'\.globl\s+(\w+)', text):
+        nxt = text.find('__asm__', m.end())
+        seg = text[m.end():nxt if nxt >= 0 else len(text)]
+        if 'jmp *%' in seg or 'jmp .Lrt_chain_seed' in seg:
+            coarse.add(m.group(1))
+missed = sorted(coarse - classified)
+if missed:
+    print("⛔ REFUSES rc=2: the coarse probe sees %d trampoline(s) this gate's parser did not classify: %s." % (len(missed), ", ".join(missed)))
+    print("   The parser is blind to them, which is not a pass.")
     sys.exit(2)
 if bad:
     print()
     print("⛔ GATE FAILED: %d trampoline(s) enter generated code on the wrong 16-byte parity." % len(bad))
     for name, n, s, got, path in bad:
         print("   %s (%s): %d pushes + %d sub bytes leaves RSP ≡ %d (mod 16), want %d." % (name, path.split('/')[-1], n, s, got, want))
-    print("   ⭐ THE CURE IS THE ONE ITS OWN SIBLING ALREADY USES: rt_proc_enter_frag compensates six pushes with")
+    print("   ⭐ THE CURE IS THE ONE ITS OWN SIBLING ALREADY USES: rt_proc_enter_named compensates six pushes with")
     print("      `subq $8, %rsp` and undoes it with `addq $8, %rsp` in EVERY exit path. Add both halves or neither --")
     print("      a sub with no matching add corrupts the return instead of the callee.")
     print("   ⛔ DO NOT 'fix' this by aligning at the call sites in emitted code: that masks an already-odd spine and")
diff --git a/src/driver/driver.h b/src/driver/driver.h
index 76749d9ee..22b491c50 100644
--- a/src/driver/driver.h
+++ b/src/driver/driver.h
@@ -22,7 +22,7 @@ DESCR_t _builtin_EVAL (DESCR_t *args, int nargs);
 DESCR_t _builtin_CODE (DESCR_t *args, int nargs);
 DESCR_t _builtin_DATA (DESCR_t *args, int nargs);
 DESCR_t _builtin_print (DESCR_t *args, int nargs);
-DESCR_t _usercall_hook (const char *name, DESCR_t *args, int nargs);
+DESCR_t _usercall_hook (const char *name, DESCR_t *args, int nargs, long *rq);
 int _label_exists_fn(const char *name);
 void rt_label_table_install(const char *const *names, int count);
 DESCR_t _eval_str_impl_fn(const char *s);
diff --git a/src/driver/driver_hooks.c b/src/driver/driver_hooks.c
index 423095b8a..708e76df5 100644
--- a/src/driver/driver_hooks.c
+++ b/src/driver/driver_hooks.c
@@ -14,7 +14,7 @@ DESCR_t _builtin_IDENT(DESCR_t *args, int nargs);
 DESCR_t _builtin_DIFFER(DESCR_t *args, int nargs);
 DESCR_t _builtin_DATA(DESCR_t *args, int nargs);
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
-DESCR_t _usercall_hook(const char *name, DESCR_t *args, int nargs) {
+DESCR_t _usercall_hook(const char *name, DESCR_t *args, int nargs, long *rq) {
     if (strcmp(name, "IDENT") == 0) return _builtin_IDENT(args, nargs);
     if (strcmp(name, "DIFFER") == 0) return _builtin_DIFFER(args, nargs);
     if (strcmp(name, "DATA") == 0) return _builtin_DATA(args, nargs);
@@ -48,9 +48,10 @@ DESCR_t _usercall_hook(const char *name, DESCR_t *args, int nargs) {
     int _wn_pre = rt_g_want_name;
     if (FNCEX_fn(name)) {
         extern int rt_proc_named_runs(const char *);
-        if (rt_proc_named_runs(name)) return rt_call_named_proc(name, args, nargs);
-        const char *_ent = FUNC_ENTRY_fn(name);
-        if (_ent && strcmp(_ent, name) != 0 && rt_proc_named_runs(_ent)) return rt_call_named_proc(_ent, args, nargs);
+        extern int rt_call_named_open(const char *, DESCR_t *, int, long *);
+        const char *_run = name;
+        if (!rt_proc_named_runs(_run)) { const char *_ent = FUNC_ENTRY_fn(name); _run = (_ent && strcmp(_ent, name) != 0 && rt_proc_named_runs(_ent)) ? _ent : (const char *)0; }
+        if (_run) return rt_call_named_open(_run, args, nargs, rq) ? FAILDESCR : rt_call_named_proc(_run, args, nargs);
     }
     rt_g_want_name = _wn_pre;
     return call_user_function(name, args, nargs);
diff --git a/src/driver/scrip.c b/src/driver/scrip.c
index 29c6c8340..41d9e116b 100644
--- a/src/driver/scrip.c
+++ b/src/driver/scrip.c
@@ -1999,7 +1999,7 @@ int main(int argc, char **argv) {
     register_fn("CODE", _builtin_CODE, 1, 1);
     register_fn("DATA", _builtin_DATA, 1, 1);
     register_fn("print", _builtin_print, 0, 99);
-    extern DESCR_t (*g_user_call_hook)(const char *, DESCR_t *, int);
+    extern DESCR_t (*g_user_call_hook)(const char *, DESCR_t *, int, long *);
     g_user_call_hook = _usercall_hook;
     {
         extern void sno_preeval_program(const tree_t *);
diff --git a/src/runtime/by_name_dispatch.c b/src/runtime/by_name_dispatch.c
index 6b4b34544..2086a4210 100644
--- a/src/runtime/by_name_dispatch.c
+++ b/src/runtime/by_name_dispatch.c
@@ -13670,7 +13670,7 @@ static DESCR_t rt_call_arr_impl(const char *fn, DESCR_t *args, int nargs, int bi
                 extern const char *sn4_unary_op_key(const char *);
                 const char *uk = sn4_unary_op_key(fn);
                 if (core_call_registered_fn(uk, args, nargs, &out)) return out;
-                if (FNCEX_fn(uk)) return RT_GC_CALLBACK(APPLY_fn(uk, args, nargs));
+                if (FNCEX_fn(uk)) return RT_GC_CALLBACK(APPLY_fn_rq(uk, args, nargs, rq));
                 core_runtime_error(29, "undefined operator referenced");
                 return FAILDESCR;
             }
@@ -13705,7 +13705,7 @@ static DESCR_t rt_call_arr_impl(const char *fn, DESCR_t *args, int nargs, int bi
         if (!strcmp(fn, "/")) return na(a, b, BINOP_DIV);
         if (!strcmp(fn, "%")) {
             extern int FNCEX_fn(const char *);
-            if (FNCEX_fn(fn)) return RT_GC_CALLBACK(APPLY_fn(fn, args, nargs));
+            if (FNCEX_fn(fn)) return RT_GC_CALLBACK(APPLY_fn_rq(fn, args, nargs, rq));
             if (sn4) { core_runtime_error(29, "undefined operator referenced"); return FAILDESCR; }
             return na(a, b, BINOP_MOD);
         }
diff --git a/src/runtime/core/core.c b/src/runtime/core/core.c
index bb036bef8..b2e174abb 100644
--- a/src/runtime/core/core.c
+++ b/src/runtime/core/core.c
@@ -2741,7 +2741,7 @@ void core_lib_init(void) {
     for (int i = 0; i < 256; i++) alphabet[i] = (char)i;
     alphabet[256] = '\0';
     { extern void rt_kw_seed_defaults(void); rt_kw_seed_defaults(); }
-    if (!g_user_call_hook) { extern DESCR_t _usercall_hook(const char *name, DESCR_t *args, int nargs); g_user_call_hook = _usercall_hook; }
+    if (!g_user_call_hook) { extern DESCR_t _usercall_hook(const char *name, DESCR_t *args, int nargs, long *rq); g_user_call_hook = _usercall_hook; }
     { struct timespec _ts; clock_gettime(CLOCK_MONOTONIC, &_ts); _g_start_ns = (int64_t)_ts.tv_sec * 1000000000LL + (int64_t)_ts.tv_nsec; }
 #if RT_DIAG
     const char *mon_fifo = getenv("MONITOR_READY_PIPE");
@@ -4728,7 +4728,7 @@ void core_undefined_call_error(const char *name) {
     else core_runtime_error(22, "undefined function called");
 }
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
-DESCR_t (*g_user_call_hook)(const char *name, DESCR_t *args, int nargs) = NULL;
+DESCR_t (*g_user_call_hook)(const char *name, DESCR_t *args, int nargs, long *rq) = NULL;
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
 static int core_apply_runtime_proc(const char *name, DESCR_t *args, int nargs, DESCR_t *out, long *rq) {
     extern int rt_proc_is_registered(const char *);
@@ -4767,12 +4767,12 @@ static DESCR_t apply_fn_body(const char *name, DESCR_t *args, int nargs, long *r
                 return e->fn(args, nargs);
             }
             { DESCR_t pr; if (core_apply_runtime_proc(name, args, nargs, &pr, rq)) return pr; }
-            if (g_user_call_hook) return g_user_call_hook(name, args, nargs);
+            if (g_user_call_hook) return g_user_call_hook(name, args, nargs, rq);
             return NULVCL;
         }
     }
     { DESCR_t pr; if (core_apply_runtime_proc(name, args, nargs, &pr, rq)) return pr; }
-    if (g_user_call_hook) { DESCR_t r = g_user_call_hook(name, args, nargs); if (!IS_FAIL_fn(r)) return r; }
+    if (g_user_call_hook) { DESCR_t r = g_user_call_hook(name, args, nargs, rq); if ((rq && rq[0]) || !IS_FAIL_fn(r)) return r; }
 #if RT_DIAG
     if (getenv("SCRIP_DEBUG_APPLY")) fprintf(stderr, "[apply-err5] unresolved '%s' (nargs=%d)\n", name ? name : "(null)", nargs);
 #endif
diff --git a/src/runtime/core/core.h b/src/runtime/core/core.h
index bf10968db..1997a3d27 100644
--- a/src/runtime/core/core.h
+++ b/src/runtime/core/core.h
@@ -363,7 +363,7 @@ DESCR_t *gva_register(const char **names, DESCR_t *cells, int n);
 const char *NV_name_from_ptr(const DESCR_t *ptr);
 extern DESCR_t (*g_eval_str_hook)(const char *s);
 DESCR_t *array_ptr(ARBLK_t *a, int i);
-extern DESCR_t (*g_user_call_hook)(const char *name, DESCR_t *args, int nargs);
+extern DESCR_t (*g_user_call_hook)(const char *name, DESCR_t *args, int nargs, long *rq);
 int subscript_set(DESCR_t arr, DESCR_t idx, DESCR_t val);
 DESCR_t subscript_get2(DESCR_t arr, DESCR_t i, DESCR_t j);
 DESCR_t subscript_get2_ext(DESCR_t arr, DESCR_t i, DESCR_t end);
diff --git a/src/runtime/rt/rt.c b/src/runtime/rt/rt.c
index d1d31f03d..18485e3a9 100644
--- a/src/runtime/rt/rt.c
+++ b/src/runtime/rt/rt.c
@@ -91,7 +91,7 @@ extern DESCR_t pat_assign_imm(DESCR_t child, DESCR_t var);
 extern DESCR_t pat_assign_cond(DESCR_t child, DESCR_t var);
 extern DESCR_t pat_at_cursor(const char *varname);
 extern DESCR_t pat_user_call(const char *name, DESCR_t *args, int nargs);
-extern DESCR_t (*g_user_call_hook)(const char *, DESCR_t *, int);
+extern DESCR_t (*g_user_call_hook)(const char *, DESCR_t *, int, long *);
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
 int rt_case_eq(const DESCR_t *sel, const DESCR_t *key) {
     if (!sel || !key) return 0;
@@ -1133,7 +1133,6 @@ void *rt_proc_open_fn(void);
 DESCR_t rt_pl_enter(void *fn, long nargs);
 DESCR_t rt_proc_enter(void *fn, long nargs, long touched);
 DESCR_t rt_proc_enter_named(void *fn, long idx);
-DESCR_t rt_proc_enter_frag(void *fn, long idx);
 int rt_proc_call_prologue(rt_proc_t **pp, DESCR_t *args, int nargs, int wn);
 DESCR_t rt_proc_call_epilogue_γ(DESCR_t frame0, long touched);
 DESCR_t rt_proc_call_epilogue_ω(long touched);
@@ -1372,6 +1371,23 @@ int rt_call_open_tail_lex(const char *name, int nargs, long *rq) {
         return 1;
     }
 }
+int rt_call_named_open(const char *name, DESCR_t *args, int nargs, long *rq) {
+    rt_proc_t *p = name ? rt_proc_find(name) : (rt_proc_t *)0;
+    if (!rq || !p || !p->dyn_scope) return 0;
+    {
+        int _n = nargs < 0 ? 0 : nargs;
+        rt_call_args_need(_n);
+        for (int i = 0; i < _n; i++) CALL_ARGS[i] = args[i];
+        rt_call_args_clear_from(_n);
+        rt_call_next_t n = rt_call_open_by_name_p(p, name, _n);
+        rq[0] = n.fn;
+        rq[1] = n.how;
+#if RT_DIAG
+        if (n.fn) rt_c2bb_hit("named.open", name);
+#endif
+        return 1;
+    }
+}
 int rt_dtx_open_tail(sno_dstar_rec_t *r, long *rq) {
     rt_proc_t *p = (r && !(r->flags & SNO_DSTAR_VARREF)) ? rt_proc_of_rec(r) : (rt_proc_t *)0;
     if (!p || !p->dyn_scope || !p->fn) return 0;
@@ -1802,7 +1818,7 @@ _Static_assert(sizeof(long) == 8,
     "THE EPILOGUE TAKES THE PROCEDURE THE CALL OPENED (ceo CEO-1263): g_rt_gen_procs[idx] is the called record itself -- its slots are fixed and a redefinition rewrites the slot in place -- so the i"
     "dx epilogues and the land restore the names its prologue saved without finding the procedure by name a second time, which SPITBOL never does either");
 _Static_assert(sizeof(long) == 8,
-    "rt_proc_enter_named and rt_proc_enter_frag park the callee's TABLE INDEX (an integer) across the body and re-derive its name here from the rooted, slot-fixed g_rt_gen_procs at the epilogue; par"
+    "rt_proc_enter_named parks the callee's TABLE INDEX (an integer) across the body and re-derive its name here from the rooted, slot-fixed g_rt_gen_procs at the epilogue; par"
     "king the name POINTER raw on the C stack left it stale after a collection that slid the block (cto 2026-09-23, user_function_opsyn_8 under the association tap's poll; row 867's holder)");
 static int rt_proc_call_prologue_lex(rt_proc_t **pp, int nargs, int wn);
 #define RT_DC_CHUNK 64
@@ -1876,12 +1892,6 @@ __asm__( ".text\n" ".globl rt_proc_enter_named\n" "rt_proc_enter_named:\n" "  pu
     "  movq 48(%r10), %r9\n" "  movq 56(%r10), %r10\n" "4:\n" "  pushq %rdx\n" "  pushq %rcx\n" "  jmp *%rax\n" "2:\n" "  addq $8, %rsp\n" "  movl 4(%rsp), %r15d\n" "  movq 8(%rsp), %r13\n"
     "  addq $16, %rsp\n" "  popq %r14\n" "  popq %r12\n" "  popq %rbx\n" "  popq %rdi\n" "  jmp rt_proc_call_epilogue_idx_γ\n" "3:\n" "  addq $8, %rsp\n" "  movl 4(%rsp), %r15d\n"
     "  movq 8(%rsp), %r13\n" "  addq $16, %rsp\n" "  popq %r14\n" "  popq %r12\n" "  popq %rbx\n" "  popq %rdi\n" "  jmp rt_proc_call_epilogue_idx_ω\n" );
-__asm__( ".text\n" ".globl rt_proc_enter_frag\n" "rt_proc_enter_frag:\n" "  pushq %rsi\n" "  pushq %rbx\n" "  pushq %r12\n" "  pushq %r14\n" "  subq $16, %rsp\n" "  movl $2, (%rsp)\n"
-    "  movl %r15d, 4(%rsp)\n" "  movq %r13, 8(%rsp)\n" "  subq $8, %rsp\n" "  movq %rdi, %rax\n" "  leaq 7f(%rip), %rcx\n" "  leaq 8f(%rip), %rdx\n" "  movq g_rtcc_on@GOTPCREL(%rip), %r10\n"
-    "  cmpb $0, (%r10)\n" "  je 9f\n" "  movq rtccb@GOTPCREL(%rip), %r10\n" "  movq 24(%r10), %rsi\n" "  movq 32(%r10), %rdi\n" "  movq 64(%r10), %r11\n" "  movq 40(%r10), %r8\n"
-    "  movq 48(%r10), %r9\n" "  movq 56(%r10), %r10\n" "9:\n" "  pushq %rdx\n" "  pushq %rcx\n" "  jmp *%rax\n" "7:\n" "  addq $8, %rsp\n" "  movl 4(%rsp), %r15d\n" "  movq 8(%rsp), %r13\n"
-    "  addq $16, %rsp\n" "  popq %r14\n" "  popq %r12\n" "  popq %rbx\n" "  popq %rdi\n" "  jmp rt_proc_call_epilogue_idx_γ\n" "8:\n" "  addq $8, %rsp\n" "  movl 4(%rsp), %r15d\n"
-    "  movq 8(%rsp), %r13\n" "  addq $16, %rsp\n" "  popq %r14\n" "  popq %r12\n" "  popq %rbx\n" "  popq %rdi\n" "  jmp rt_proc_call_epilogue_idx_ω\n" );
 DESCR_t rt_proc_enter_named(void *fn, long idx);
 /*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
 void *rt_proc_open_fn(void) { return (void *)0; }
```
