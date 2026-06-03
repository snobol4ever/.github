#include <string>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "emit.h"
#include "emit_bb.h"
}
#include "x86_asm.h"
/*--------------------------------------------------------------------------------------------------------------------*/
static std::string bb_logicvar_str(IR_t * pBB) {
    if (PLATFORM_X86) {
        return IF(MEDIUM_TEXT, s_1asm(std::string(_.lbl_α) + ":") + s_1asm(emit_fmt("# BOX RESOLVE_VAR(slot=%d) [stackless pass-through]", (int)(pBB ? pBB->ival : 0))))
             + x86("jmp", PORT_GAMMA)
             + x86("def", PORT_BETA)
             + x86("jmp", PORT_OMEGA);
    }
    return std::string();
}
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" void bb_logicvar(IR_t * pBB) { bb_emit_x86(bb_logicvar_str(pBB)); }
