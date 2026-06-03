/* bb_goal.cpp — BB template for IR_GOAL: Prolog predicate call (WAM-CP-5).
   WAM-CP-5 (2026-05-28, Sonnet 4.6): IR_GOAL owns NO CP record.  The CP is owned by the
   CALLEE's IR_CHOICE, which handles trail unwind between clauses in pre[i>0].  IR_CALL's beta
   calls _redo WITHOUT pre-unwinding (arg-alias bindings survive; CHOICE pre[i] handles it).
   caller_env saved into g_resolve_bfr->saved_args via rt_cp_save_caller_env() on first success.
   IR_STRUCT compound args built via emit_build_compound_term (post-order BB walker).
   x86 TEXT only per RULES "X86 ONLY". */
#include <string>
#include <vector>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "emit.h"
#include "emit_bb.h"
#include "emit_core.h"
#include "IR.h"
#include "IR_interp_state.h"
}
#include "x86_asm.h"
extern std::string emit_build_compound_term(const IR_t *nd);
extern "C" {
void  *rt_node_to_term(int kind, long ival, const char *sval, double dval);
void **resolve_bb_env_save_push(int nslots);
void   resolve_bb_bind_arg(int slot, void *caller_term);
int    rt_last_ok(void);
void **resolve_bb_env_install(void **env);
void   rt_cp_save_caller_env(void *caller_env);
void   resolve_bb_env_pop(void **saved);
void  *resolve_cp_current(void);
}
/*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
/*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
static std::string build_arg(IR_t *a) {
    if (!a) return s_2asm("xor", "eax, eax");
    if (a->t == IR_STRUCT) return emit_build_compound_term(a);
    int kind = (int)a->t;
    long ival = (long)a->ival;
    const char *sval = a->sval;
    char slbl[64]; slbl[0] = 0;
    if (sval && *sval) strtab_label(slbl, sizeof slbl, sval);
    return s_2asm("mov", emit_fmt("edi, %d", kind))
         + s_2asm("mov", emit_fmt("rsi, %ld", ival))
         + (slbl[0] ? s_2asm("lea", emit_fmt("rdx, [rip + %s]", slbl))
                    : s_2asm("xor", "edx, edx"))
         + s_2asm("xorps", "xmm0, xmm0")
         + s_2asm("call", "rt_node_to_term@PLT");
}
/*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
static std::string bb_goal_str(IR_t * pBB) {
    (void)pBB;
    if (PLATFORM_X86) {
        if (MEDIUM_MACRO_DEF) return s_comment("# no macro form — RESOLVE_CALL");
        if (MEDIUM_TEXT) {
            const char *callee = pBB && pBB->sval ? pBB->sval : "";
            int arity = 0;
            bb_goal_state_t *zc = NULL;
            if (pBB && pBB->ival) {
                zc = (bb_goal_state_t *)(intptr_t)pBB->ival;
                arity = zc->arity;
            }
            int n_args = (zc && zc->args) ? zc->nargs : 0;
            if (n_args > arity) n_args = arity;
            char blbl[160]; resolve_call_block_label(blbl, sizeof blbl, callee, arity);
            char redo_lbl[200]; snprintf(redo_lbl, sizeof redo_lbl, "%s_redo", blbl);
            std::string out = s_1asm(emit_fmt("%s:", _.lbl_α))
                            + s_comment(emit_fmt("# BOX RESOLVE_CALL %s/%d (WAM-CP-5, n_args=%d)", callee, arity, n_args));
            /* Phase 1: build caller-side arg Terms via build_arg (handles IR_STRUCT compound),    */
            /* push each on stack.  emit_build_compound_term may sub/add rsp internally but restores  */
            /* it; rax = Term* on exit from each build_arg call.                                       */
            for (int i = 0; i < n_args; i++) {
                IR_t *a = (zc && zc->args) ? zc->args[i] : NULL;
                out += build_arg(a)
                     + s_2asm("push", "rax");
            }
            /* Phase 2: push callee env.  resolve_bb_env_save_push allocates callee env, sets g_resolve_env,    */
            /* returns caller_env in rax.  Push caller_env on stack.                                   */
            int nslots = arity + 16;
            out += s_2asm("mov", emit_fmt("edi, %d", nslots))
                 + s_2asm("call", "resolve_bb_env_save_push@PLT")
                 + s_2asm("push", "rax");
            /* Alignment: (n_args+1) qwords pushed since frame entry.  Pad if odd.                   */
            int push_count = n_args + 1;
            int need_pad   = (push_count & 1) ? 1 : 0;
            if (need_pad) out += s_2asm("sub", "rsp, 8");
            /* Phase 3: bind callee slots.  Arg-alias bindings made here survive redo because CHOICE  */
            /* pre[i>0] only unwinds back to CHOICE's own trail mark (taken after these bindings).     */
            for (int i = n_args - 1; i >= 0; i--) {
                int off = 8 * (need_pad + 1 + (n_args - 1 - i));
                out += s_2asm("mov", emit_fmt("rsi, [rsp + %d]", off))
                     + s_2asm("mov", emit_fmt("edi, %d", i))
                     + s_2asm("call", "resolve_bb_bind_arg@PLT");
            }
            /* Phase 4: fresh call. */
            out += s_2asm("call", blbl);
            /* Phase 5: restore stack, test last_ok. */
            if (need_pad) out += s_2asm("add", "rsp, 8");
            out += s_2asm("pop",  "rdi");
            if (n_args > 0) out += s_2asm("add", emit_fmt("rsp, %d", 8 * n_args));
            out += s_2asm("call", "rt_last_ok@PLT")
                 + s_2asm("test", "eax, eax")
                 + s_2asm("je",   emit_fmt("%s_fail5", _.lbl_α));
            /* SUCCESS: restore caller_env; save into CHOICE's CP for beta. */
            out += s_2asm("call", "resolve_bb_env_install@PLT")
                 + s_2asm("mov",  "rdi, rax")
                 + s_2asm("call", "rt_cp_save_caller_env@PLT")
                 + s_2asm("jmp",  _.lbl_γ);
            /* fail5: free callee env; CHOICE already popped its CP on exhausted path. */
            out += s_L1asm(emit_fmt("%s_fail5:", _.lbl_α), "")
                 + s_2asm("call", "resolve_bb_env_pop@PLT")
                 + s_2asm("jmp",  _.lbl_ω);
            /* beta: redo.  g_resolve_bfr = CHOICE's CP.  Reinstall callee_env (cp->env=24).              */
            /* Call _redo — no trail_unwind: CHOICE pre[i>0] handles it.                              */
            out += s_1asm(emit_fmt("%s:", _.lbl_β))
                 + s_2asm("call", "resolve_cp_current@PLT")
                 + s_2asm("test", "rax, rax")
                 + s_2asm("je",   emit_fmt("%s_nosol", _.lbl_α))
                 + s_2asm("mov",  "rdi, [rax + 24]")
                 + s_2asm("call", "resolve_bb_env_install@PLT")
                 + s_2asm("call", redo_lbl)
                 + s_2asm("call", "rt_last_ok@PLT")
                 + s_2asm("test", "eax, eax")
                 + s_2asm("je",   emit_fmt("%s_nosol", _.lbl_α))
                 + s_2asm("call", "resolve_cp_current@PLT")
                 + s_2asm("mov",  "rdi, [rax + 40]")
                 + s_2asm("call", "resolve_bb_env_install@PLT")
                 + s_2asm("jmp",  _.lbl_γ);
            out += s_L2asm(emit_fmt("%s_nosol:", _.lbl_α), "jmp", _.lbl_ω);
            return out;
        }
    }
    return std::string();
}
/*----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/
extern "C" void bb_goal(IR_t * pBB) { bb_emit_x86(bb_goal_str(pBB)); }
