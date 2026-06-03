#include <string>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "emit.h"
#include "emit_bb.h"
}
#include "x86_asm.h"
/*--------------------------------------------------------------------------------------------------------------------*/
static std::string bb_atom_str(IR_t * pBB) {
    if (PLATFORM_X86) {
        const char *atom = pBB && pBB->sval ? pBB->sval : "";
        return IF(MEDIUM_TEXT, s_1asm(std::string(_.lbl_α) + ":") + s_comment(emit_fmt("# BOX RESOLVE_ATOM('%s') [stackless pass-through]", atom)))
             + x86("jmp", PORT_GAMMA)
             + x86("def", PORT_BETA)
             + x86("jmp", PORT_OMEGA);
    }
    return std::string();
}
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" void bb_atom(IR_t * pBB) { bb_emit_x86(bb_atom_str(pBB)); }
