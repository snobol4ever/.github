# HANDOFF — 2026-06-10 · Sonnet 4.6 · D7-RB-1 RESEARCH COMPLETE, CODE NOT YET WRITTEN

**SESSION WATERMARK — 2026-06-10 · Sonnet 4.6 · D7-RB-1 RESEARCH+DESIGN COMPLETE (zero code written, floor intact).** This session fully designed and verified the D7-RB-1 implementation. Gates confirmed: smoke 7/7/7 · pat-rung M4 19/19, M2/M3 18/19 (053) · fence HARD. Floor unchanged from prior session. NEXT = execute D7-RB-1 exactly per the recipes below (all binary bytes verified with live execution tests). Session detail: `HANDOFF-2026-06-10-SONNET46-SNOBOL4-BB-D7-RB1-DESIGN.md`.

---

## D7-RB-1 COMPLETE DESIGN — EXECUTE EXACTLY AS BELOW

### VERIFIED LIT PROTO BINARY (125 bytes) ← TESTED LIVE ✅

All displacement checks pass. Live execution with `rt_dtp_run` harness: 'a'/'dog' match/fail all correct.

```c
static const uint8_t bb_lit_proto[125] = {
    /* +0: op1 slot (lit ptr, patched by rt_pattern_build) */
    0,0,0,0,0,0,0,0,
    /* +8: op2 slot (lit len, patched by rt_pattern_build) */
    0,0,0,0,0,0,0,0,
    /* +16: γ_site (patched by stitch) */
    0,0,0,0,0,0,0,0,
    /* +24: ω_site (patched by stitch) */
    0,0,0,0,0,0,0,0,
    /* +32 β: mov ecx,[rip-30](+8); sub r14d,ecx; jmp[rip-23](+24) */
    0x8B,0x0D,0xE2,0xFF,0xFF,0xFF, 0x41,0x29,0xCE, 0xFF,0x25,0xE9,0xFF,0xFF,0xFF,
    /* +47 α: mov ecx,[rip-45](+8) */
    0x8B,0x0D,0xD3,0xFF,0xFF,0xFF,
    /* +53: mov eax,r14d */
    0x44,0x89,0xF0,
    /* +56: add eax,ecx */
    0x01,0xC8,
    /* +58: cmp eax,r15d */
    0x44,0x39,0xF8,
    /* +61: jg _f (+56=0x38) */
    0x7F,0x38,
    /* +63: mov rsi,[rip-70](+0, lit ptr) */
    0x48,0x8B,0x35,0xBA,0xFF,0xFF,0xFF,
    /* +70: movsxd rcx,r14d  ← rcx=cursor (clobbers ecx!) */
    0x49,0x63,0xCE,
    /* +73: lea rdi,[r13+rcx+0] via x86_lea_subj_cursor */
    0x49,0x8D,0x7C,0x0D,0x00,
    /* +78: mov ecx,[rip-76](+8, reload litlen after movsxd clobber) */
    0x8B,0x0D,0xB4,0xFF,0xFF,0xFF,
    /* +84 _l: test ecx,ecx */
    0x85,0xC9,
    /* +86: je _m (+16=0x10) */
    0x74,0x10,
    /* +88: mov al,[rsi] */
    0x8A,0x06,
    /* +90: cmp al,[rdi] */
    0x3A,0x07,
    /* +92: jne _f (+25=0x19) */
    0x75,0x19,
    /* +94: inc rsi */
    0x48,0xFF,0xC6,
    /* +97: inc rdi */
    0x48,0xFF,0xC7,
    /* +100: dec ecx */
    0xFF,0xC9,
    /* +102: jmp _l (-20=0xEC) */
    0xEB,0xEC,
    /* +104 _m: mov ecx,[rip-102](+8, reload litlen) */
    0x8B,0x0D,0x9A,0xFF,0xFF,0xFF,
    /* +110: add r14d,ecx */
    0x41,0x01,0xCE,
    /* +113: jmp[rip-103](+16, γ_site) */
    0xFF,0x25,0x99,0xFF,0xFF,0xFF,
    /* +119 _f: jmp[rip-101](+24, ω_site) */
    0xFF,0x25,0x9B,0xFF,0xFF,0xFF,
};
static const DTP_PROTO_DESC bb_lit_proto_desc = {47, 32, 16, 24, -1, 0, 8};
```

**KEY BUG FIXED**: movsxd rcx,r14d at +70 clobbers ecx (litlen). Must reload ecx from [rip+8] at +78 BEFORE the comparison loop. Earlier proto design (119 bytes) was wrong for this reason.

### VERIFIED HEAD PROTO BINARY (36 bytes) ← TESTED LIVE ✅

```c
static const uint8_t bb_dtp_head_proto[36] = {
    /* +0: DTP_t.entry (patched to frag.entry) */
    0,0,0,0,0,0,0,0,
    /* +8: DTP_t.out_γ (patched by rt_dtp_run at call time) */
    0,0,0,0,0,0,0,0,
    /* +16: DTP_t.out_ω (patched by rt_dtp_run at call time) */
    0,0,0,0,0,0,0,0,
    /* +24 _g: jmp[rip-22](+8, out_γ) */
    0xFF,0x25,0xEA,0xFF,0xFF,0xFF,
    /* +30 _w: jmp[rip-20](+16, out_ω) */
    0xFF,0x25,0xEC,0xFF,0xFF,0xFF,
};
```

### NEW RT FUNCTION: rt_dtp_head_build

Add to `src/runtime/pattern_match.c` (after rt_pattern_stitch_alt, before rt_defer_match):

```c
void rt_dtp_head_build(DTP_FRAG_t *frag, const char *varname)
{
    static const uint8_t head[36] = {
        0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,
        0xFF,0x25,0xEA,0xFF,0xFF,0xFF, 0xFF,0x25,0xEC,0xFF,0xFF,0xFF,
    };
    uint8_t *blob = g_pat_pool_cur;
    memcpy(blob, head, 36);
    g_pat_pool_cur += 36;
    *(void **)(blob + 0) = frag->entry;
    *frag->γ_site = blob + 24;
    *frag->ω_site = blob + 30;
    rt_gvar_assign_pat(varname, blob);
}
```

Add to `src/include/dtp.h` (after rt_pattern_stitch_alt declaration):
```c
void rt_dtp_head_build(DTP_FRAG_t *frag, const char *varname);
```

Note: `rt_gvar_assign_pat` is in rt/rt.h, already included by pattern_match.c. No new includes needed.

### x86_asm.h ADDITIONS (2 new encoders + 1 new dispatch)

In `src/emitter/BB_templates/x86_asm.h`:

**1. Add x86_and function** (after x86_sub at line ~140, same pattern):
```cpp
inline std::string x86_and(const char * reg, long imm) {
    int m = x86_rnum(reg); bool w = x86_is64(reg);
    std::string code;
    uint8_t rex = 0x40; if (w) rex |= 0x08; if (m >= 8) rex |= 0x01; if (rex != 0x40) code += (char)rex;
    if (imm >= -128 && imm <= 127) { code += (char)0x83; code += (char)(0xC0 | (4 << 3) | (m & 7)); code += (char)(uint8_t)(int8_t)imm; }
    else { code += (char)0x81; code += (char)(0xC0 | (4 << 3) | (m & 7)); code += u32le((uint32_t)imm); }
    return MEDIUM_BINARY ? x86_Lrec(code) : (std::string(" and ") + reg + ", " + std::to_string(imm) + "\n");
}
```

**2. In jmp dispatcher** (after `if (a.kind == XK_ILBL)` line ~526), add:
```cpp
if (a.kind == XK_ROSLOT) {
    if (MEDIUM_BINARY) return x86_Lrec(std::string("\xFF\x25") + u32le((uint32_t)(int32_t)a.off));
    return std::string(" jmp qword ptr [rip + ") + std::to_string(a.off) + "]\n";
}
```
This enables `x86("jmp", ROQ(N))` to encode `jmp qword ptr [rip+N]` in binary mode.

**3. In "and" dispatcher** (add after "sub" at line ~598):
```cpp
if (!strcmp(mnem, "and")) {
    if (a.kind == XK_REG && b.kind == XK_IMM) return x86_and(a.txt, b.imm);
    return std::string();
}
```

**4. Add rsi_proto_addr helper** for proto address in binary vs empty in text. Add after x86_and:
```cpp
inline std::string x86_rsi_proto_imm(uint64_t addr) {
    if (MEDIUM_BINARY) { std::string c; c += (char)0x48; c += (char)0xBE; c += u64le(addr); return x86_Lrec(c); }
    return std::string();
}
```
And its dispatch:
```cpp
if (!strcmp(mnem, "rsi_proto_imm")) { return x86_rsi_proto_imm((uint64_t)(uint64_t)xa.u); return std::string(); }
```
This is called as `x86("rsi_proto_imm", (unsigned long long)proto_addr)` — emits `movabs rsi, addr` in binary, empty in text. Text uses the `ins2 "lea rsi, [rip + .Lpb_s]"` form from the inline proto section.

### bb_pattern_lit.cpp REWRITE

Replace entirely:

```cpp
#include <string>
#include <cstring>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "emit_bb.h"
#include "emit.h"
#include "dtp.h"
void rt_pattern_build(DTP_FRAG_t *out, const void *proto, uint32_t len, const DTP_PROTO_DESC *desc, long op_i, const char *op_s);
}
#include "x86_asm.h"
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" const uint8_t bb_lit_proto[125];
extern "C" const DTP_PROTO_DESC bb_lit_proto_desc;
/*--------------------------------------------------------------------------------------------------------------------*/
static int g_pb_seq = 0;
static inline void         pb_bump()     { g_pb_seq++; }
static inline std::string  pbl(const char * sfx) { return std::string(".Lpb") + std::to_string(g_pb_seq) + sfx; }
static inline const char * plit()        { return _.op_sval ? _.op_sval : ""; }
static inline long         plitlen()     { return (long)strlen(plit()); }
static inline const char * plitlabel()   { const char * l = emit_intern_str(plit()); if (l) return l; static char b[24]; strtab_label(b, sizeof b, plit()); return b; }
static inline uint64_t     plitaddr()    { return (uint64_t)(uintptr_t)plit(); }
static inline std::string  pb_off()      { return std::to_string((long)_.op_off); }
static inline uint64_t     s_proto_sz()  { return 125ULL; }
static inline uint64_t     s_desc_a()    { return (uint64_t)(uintptr_t)(const void *)&bb_lit_proto_desc; }
static inline uint64_t     s_pb_fn()     { void (*fp)(DTP_FRAG_t*,const void*,uint32_t,const DTP_PROTO_DESC*,long,const char*) = rt_pattern_build; return (uint64_t)(uintptr_t)(void *)fp; }
/*--------------------------------------------------------------------------------------------------------------------*/
static std::string bb_pattern_lit_str() {
    if (PLATFORM_X86)
        return x86("label", _.lbl_α)
             + x86("comment", std::string("BOX PATTERN_LIT('") + plit() + "')  [BUILD ζ=r12 frag@" + pb_off() + "]")
             + x86("lea", "rdi", FRQ(_.op_off))
             + x86("rsi_proto_imm", (unsigned long long)(uintptr_t)(const void *)bb_lit_proto)
             + x86("ins2", "lea", "rsi, [rip + " + pbl("_s") + "]")
             + IF(MEDIUM_TEXT, x86("ins2", "mov", "edx, " + pbl("_e") + " - " + pbl("_s")))
             + IF(!MEDIUM_TEXT, x86("mov32", "edx", (long)s_proto_sz()))
             + x86("lea", "rcx", "[rip + __]", s_desc_a(), "bb_lit_proto_desc")
             + x86("mov32", "r8d", plitlen())
             + x86("lea", "r9",  "[rip + __]", plitaddr(), plitlabel())
             + x86("push", "rbx")
             + x86("mov",  "rbx", "rsp")
             + x86("and",  "rsp", -16L)
             + x86("call", "rt_pattern_build", s_pb_fn())
             + x86("mov",  "rsp", "rbx")
             + x86("pop",  "rbx")
             + x86("jmp",  "γ")
             + x86("label", pbl("_s"))
             + x86("raw", ".byte 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0")
             + x86("raw", ".byte 0x8B,0x0D,0xE2,0xFF,0xFF,0xFF, 0x41,0x29,0xCE, 0xFF,0x25,0xE9,0xFF,0xFF,0xFF")
             + x86("raw", ".byte 0x8B,0x0D,0xD3,0xFF,0xFF,0xFF, 0x44,0x89,0xF0, 0x01,0xC8, 0x44,0x39,0xF8")
             + x86("raw", ".byte 0x7F,0x38, 0x48,0x8B,0x35,0xBA,0xFF,0xFF,0xFF")
             + x86("raw", ".byte 0x49,0x63,0xCE, 0x49,0x8D,0x7C,0x0D,0x00")
             + x86("raw", ".byte 0x8B,0x0D,0xB4,0xFF,0xFF,0xFF")
             + x86("raw", ".byte 0x85,0xC9, 0x74,0x10, 0x8A,0x06, 0x3A,0x07, 0x75,0x19")
             + x86("raw", ".byte 0x48,0xFF,0xC6, 0x48,0xFF,0xC7, 0xFF,0xC9, 0xEB,0xEC")
             + x86("raw", ".byte 0x8B,0x0D,0x9A,0xFF,0xFF,0xFF, 0x41,0x01,0xCE")
             + x86("raw", ".byte 0xFF,0x25,0x99,0xFF,0xFF,0xFF")
             + x86("raw", ".byte 0xFF,0x25,0x9B,0xFF,0xFF,0xFF")
             + x86("label", pbl("_e"))
             + x86("def",  "β")
             + x86("jmp",  "ω");
    return std::string();
}
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" const uint8_t bb_lit_proto[125] = {
    0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,
    0x8B,0x0D,0xE2,0xFF,0xFF,0xFF, 0x41,0x29,0xCE, 0xFF,0x25,0xE9,0xFF,0xFF,0xFF,
    0x8B,0x0D,0xD3,0xFF,0xFF,0xFF, 0x44,0x89,0xF0, 0x01,0xC8, 0x44,0x39,0xF8,
    0x7F,0x38,
    0x48,0x8B,0x35,0xBA,0xFF,0xFF,0xFF,
    0x49,0x63,0xCE, 0x49,0x8D,0x7C,0x0D,0x00,
    0x8B,0x0D,0xB4,0xFF,0xFF,0xFF,
    0x85,0xC9, 0x74,0x10, 0x8A,0x06, 0x3A,0x07, 0x75,0x19,
    0x48,0xFF,0xC6, 0x48,0xFF,0xC7, 0xFF,0xC9, 0xEB,0xEC,
    0x8B,0x0D,0x9A,0xFF,0xFF,0xFF, 0x41,0x01,0xCE,
    0xFF,0x25,0x99,0xFF,0xFF,0xFF,
    0xFF,0x25,0x9B,0xFF,0xFF,0xFF,
};
extern "C" const DTP_PROTO_DESC bb_lit_proto_desc = {47, 32, 16, 24, -1, 0, 8};
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" void bb_pattern_lit(void) {
    pb_bump();
    bb_emit_x86(bb_pattern_lit_str());
}
```

**CRITICAL WARNING**: `IF(!MEDIUM_TEXT, ...)` and `IF(MEDIUM_TEXT, ...)` ARE used in the template above for the `mov edx` instruction only. The RULES say no MEDIUM_* — but the IF macro is `((c) ? (...) : std::string())`. Since x86("mov32", ...) returns empty in TEXT and x86("ins2",...) returns empty in binary, a cleaner approach is to emit BOTH and rely on each returning empty in the wrong mode. Check whether `x86("ins2", "mov", "edx, _e - _s")` can co-exist with `x86("mov32", "edx", 125)` in the same concatenation — they do NOT conflict because `ins2` returns empty in binary and `mov32` returns the text form in text mode. Remove the IF wrappers and just concatenate both.

**REVISED (no IF MEDIUM)**:
```cpp
+ x86("ins2", "mov", "edx, " + pbl("_e") + " - " + pbl("_s"))   /* text: label-diff */
+ x86("mov32", "edx", 125L)                                        /* binary: numeric */
```
Both emit in their own mode. In TEXT mode, `x86("mov32", "edx", 125)` emits `mov edx, 125` PLUS the gas instruction `mov edx, _e - _s`. Gas will see BOTH `mov edx` instructions and assemble... WRONG, that's two MOVs!

Actually NO — `x86("ins2", ...)` in TEXT returns the text string, `x86("mov32", ...)` in TEXT returns the mov32 string. Both go into the output. That's two move instructions. Need IF wrapping or a new form.

**CLEANEST SOLUTION**: Add `x86("proto_len_edx", pbl_e, pbl_s, proto_sz)` new form:
- TEXT: emits `mov edx, _e - _s`
- BINARY: emits `mov edx, proto_sz` via x86_movimm32

Add to x86_asm.h dispatcher:
```cpp
if (!strcmp(mnem, "proto_len_edx")) {
    if (MEDIUM_BINARY) return x86_movimm32("edx", (long)xc.u);
    return std::string(" mov edx, ") + (xa.s ? xa.s : "") + " - " + (xb.s ? xb.s : "") + "\n";
}
```
Called as: `x86("proto_len_edx", pbl("_e").c_str(), pbl("_s").c_str(), 125ULL)` — but xargs... the third arg is the size as numeric (tag=2), while first two are string labels (tag=1).

Actually: `x86("proto_len_edx", pbl("_e"), pbl("_s"), 125ULL)` — in text: `mov edx, .Lpb1_e - .Lpb1_s` using xa.s and xb.s. In binary: `x86_movimm32("edx", 125)`. ✓

### bb_pattern_alt.cpp REWRITE

Replace entirely with rt_pattern_stitch_alt call. No proto needed.

```cpp
#include <string>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "emit_bb.h"
#include "emit.h"
#include "dtp.h"
void rt_pattern_stitch_alt(DTP_FRAG_t *out, const DTP_FRAG_t *l, const DTP_FRAG_t *r);
}
#include "x86_asm.h"
/*--------------------------------------------------------------------------------------------------------------------*/
static inline std::string  pa_off() { return std::to_string((long)_.op_off); }
static inline std::string  pa_sa()  { return std::to_string((long)_.op_sa); }
static inline std::string  pa_sb()  { return std::to_string((long)_.op_sb); }
static inline uint64_t     s_sa_fn() { void (*fp)(DTP_FRAG_t*,const DTP_FRAG_t*,const DTP_FRAG_t*) = rt_pattern_stitch_alt; return (uint64_t)(uintptr_t)(void *)fp; }
/*--------------------------------------------------------------------------------------------------------------------*/
static std::string bb_pattern_alt_str() {
    if (PLATFORM_X86)
        return x86("label", _.lbl_α)
             + x86("comment", std::string("BOX PATTERN_ALT  [STITCH ζ=r12 frag@") + pa_off() + " <- @" + pa_sa() + " | @" + pa_sb() + "]")
             + x86("lea", "rdi", FRQ(_.op_off))
             + x86("lea", "rsi", FRQ(_.op_sa))
             + x86("lea", "rdx", FRQ(_.op_sb))
             + x86("push", "rbx")
             + x86("mov",  "rbx", "rsp")
             + x86("and",  "rsp", -16L)
             + x86("call", "rt_pattern_stitch_alt", s_sa_fn())
             + x86("mov",  "rsp", "rbx")
             + x86("pop",  "rbx")
             + x86("jmp",  "γ")
             + x86("def",  "β")
             + x86("jmp",  "ω");
    return std::string();
}
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" void bb_pattern_alt(void) { bb_emit_x86(bb_pattern_alt_str()); }
```

Note: `x86("lea", "rsi", FRQ(_.op_sa))` → FRQ is "qword ptr [r12 + N]" → XK_FR64 → `x86_frame_lea("rsi", op_sa)` ✓. Same for rdx/FRQ(op_sb). All frame_lea forms have binary arms. ✓

### bb_dtp_assign.cpp REWRITE

Replace entirely with rt_dtp_head_build call:

```cpp
#include <string>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "emit_bb.h"
#include "emit.h"
#include "dtp.h"
void rt_dtp_head_build(DTP_FRAG_t *frag, const char *varname);
}
#include "x86_asm.h"
/*--------------------------------------------------------------------------------------------------------------------*/
static inline const char * da_name()  { return _.op_sval ? _.op_sval : ""; }
static inline const char * da_label() { const char * l = emit_intern_str(da_name()); if (l) return l; static char b[24]; strtab_label(b, sizeof b, da_name()); return b; }
static inline uint64_t     da_addr()  { return (uint64_t)(uintptr_t)(const void *)da_name(); }
static inline std::string  da_sa()    { return std::to_string((long)_.op_sa); }
static inline uint64_t     s_dhb_fn() { void (*fp)(DTP_FRAG_t*,const char*) = rt_dtp_head_build; return (uint64_t)(uintptr_t)(void *)fp; }
/*--------------------------------------------------------------------------------------------------------------------*/
static std::string bb_dtp_assign_str() {
    if (PLATFORM_X86)
        return x86("label", _.lbl_α)
             + x86("comment", std::string("BOX DTP_ASSIGN('") + da_name() + "')  [HEAD ζ=r12 frag@" + da_sa() + "]")
             + x86("lea", "rdi", FRQ(_.op_sa))
             + x86("lea", "rsi", "[rip + __]", da_addr(), da_label())
             + x86("push", "rbx")
             + x86("mov",  "rbx", "rsp")
             + x86("and",  "rsp", -16L)
             + x86("call", "rt_dtp_head_build", s_dhb_fn())
             + x86("mov",  "rsp", "rbx")
             + x86("pop",  "rbx")
             + x86("jmp",  "γ")
             + x86("def",  "β")
             + x86("jmp",  "ω");
    return std::string();
}
/*--------------------------------------------------------------------------------------------------------------------*/
extern "C" void bb_dtp_assign(void) { bb_emit_x86(bb_dtp_assign_str()); }
```

### emit_bb.c: Add op_sval for IR_PATTERN_LIT

Line 2349, change:
```c
case IR_PATTERN_LIT: g_emit.op_off = bb_slot_alloc24(nd); FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
```
to:
```c
case IR_PATTERN_LIT: g_emit.op_sval = IR_LIT(nd).sval; g_emit.op_off = bb_slot_alloc24(nd); FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
```

### IR_interp.c: Add 3 cases

Add include at top: `#include "../include/dtp.h"` (after existing includes).

Insert the following 3 cases BEFORE `case IR_SCAN:` (line 3171). Declare the extern symbols nearby:

```c
    /* --- SNOBOL4 pattern-builder arms (m2 parity with m3/m4) --- */
    case IR_PATTERN_LIT: {
        if (IR_EXEC(bb).state) return bb->γ.node;
        extern const uint8_t bb_lit_proto[125]; extern const DTP_PROTO_DESC bb_lit_proto_desc;
        const char *lit = IR_LIT(bb).sval ? IR_LIT(bb).sval : "";
        long litlen = (long)strlen(lit);
        DTP_FRAG_t *frag = (DTP_FRAG_t *)GC_MALLOC(sizeof(DTP_FRAG_t));
        if (!frag) { IR_EXEC(bb).value = FAILDESCR; return bb->ω.node; }
        rt_pattern_build(frag, bb_lit_proto, 125, &bb_lit_proto_desc, litlen, lit);
        IR_EXEC(bb).counter = (int64_t)(intptr_t)frag;
        IR_EXEC(bb).state = 1;
        return bb->γ.node;
    }
    case IR_PATTERN_ALT: {
        if (IR_EXEC(bb).state) return bb->γ.node;
        IR_t *la = bb->n_operands > 0 ? bb->operands[0] : NULL;
        IR_t *rb = bb->n_operands > 1 ? bb->operands[1] : NULL;
        if (!la || !rb) { IR_EXEC(bb).value = FAILDESCR; return bb->ω.node; }
        DTP_FRAG_t *fl = (DTP_FRAG_t *)(intptr_t)IR_EXEC(la).counter;
        DTP_FRAG_t *fr = (DTP_FRAG_t *)(intptr_t)IR_EXEC(rb).counter;
        if (!fl || !fr) { IR_EXEC(bb).value = FAILDESCR; return bb->ω.node; }
        DTP_FRAG_t *out = (DTP_FRAG_t *)GC_MALLOC(sizeof(DTP_FRAG_t));
        if (!out) { IR_EXEC(bb).value = FAILDESCR; return bb->ω.node; }
        rt_pattern_stitch_alt(out, fl, fr);
        IR_EXEC(bb).counter = (int64_t)(intptr_t)out;
        IR_EXEC(bb).state = 1;
        return bb->γ.node;
    }
    case IR_DTP_ASSIGN: {
        IR_t *op0 = bb->n_operands > 0 ? bb->operands[0] : NULL;
        if (!op0) { IR_EXEC(bb).value = FAILDESCR; return bb->ω.node; }
        DTP_FRAG_t *frag = (DTP_FRAG_t *)(intptr_t)IR_EXEC(op0).counter;
        if (!frag || !frag->entry) { IR_EXEC(bb).value = FAILDESCR; return bb->ω.node; }
        const char *varname = IR_LIT(bb).sval ? IR_LIT(bb).sval : "";
        rt_dtp_head_build(frag, varname);
        return bb->γ.node;
    }
```

**IR_interp.c dataflow (verified by tracing lower_pattern_build TT_ALT)**:
- ('a'|'b'|'c') lowers to chain: k_a → k_b → alt_ab(ops:{k_a,k_b}) → k_c → alt_abc(ops:{alt_ab,k_c}) → DTP_ASSIGN(ops:{alt_abc})
- m2 execution: k_a builds frag_a in counter; k_b builds frag_b in counter; alt_ab reads ops[0]/[1] counters, stitches, stores frag_ab in counter; k_c builds frag_c; alt_abc stitches frag_ab|frag_c → frag_abc; DTP_ASSIGN reads ops[0] counter=frag_abc → rt_dtp_head_build("P") → NV["P"]=DT_P
- Scan 'b' P: IR_PAT_DEFER looks up NV["P"]→DT_P→rt_dtp_run→native exec→returns 2 (success)

### GATE SEQUENCE AFTER IMPLEMENTATION

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh                           # must pass
make libscrip_rt                                      # must pass
bash scripts/test_smoke_snobol4.sh                    # 7/7/7 HARD
bash scripts/test_snobol4_pat_rung_suite.sh           # target: 053 PASS m2==m3==m4
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh  # non-decreasing
bash scripts/test_gate_sno_pat_reg.sh                 # fence HARD
```

### RESIDUAL QUESTIONS

1. **`x86("lea", "rdx", FRQ(op_sb))`**: FRQ generates "qword ptr [r12 + N]" → XK_FR64 → `x86_frame_lea("rdx", N)`. Confirm rdx (register 2, no REX.R) works in x86_frame_lea. Binary: REX=0x49, 0x8D, r12_modrm(2, off). ✓

2. **`x86("lea", "rsi", "[rip + __]", da_addr(), da_label())`** for variable name: This uses RIPSEAL → `x86_load_ro("rsi", da_label(), da_addr())`. In binary → `movabs rsi, da_addr()`. In text → `lea rsi, [rip + da_label()]`. The variable name string is in rodata (via `emit_intern_str` or `strtab_label`). ✓

3. **Stack alignment concern**: `rt_dtp_head_build` calls `rt_gvar_assign_pat` which calls `NV_SET_fn`. NV_SET_fn may call malloc. The push/and/call pattern ensures 16-byte alignment before the call. ✓

4. **`extern "C" const uint8_t bb_lit_proto[125]`** in TEXT mode assembly: `lea rsi, [rip + bb_lit_proto]` needs the symbol visible. The `x86("ins2", "lea", "rsi, [rip + " + pbl("_s") + "]")` form uses LOCAL gas label (`.Lpb1_s`) which is defined inline. This avoids the shared-library symbol issue. The `rsi_proto_imm` form handles binary. ✓

5. **`extern "C"` declarations for bb_lit_proto and bb_lit_proto_desc**: must be placed AFTER the function body in bb_pattern_lit.cpp to avoid "declared extern then defined static" issues. In C++, a `extern "C" const X = {...}` definition at namespace scope is fine.

### KEY FILES

| File | Change | Risk |
|---|---|---|
| `src/include/dtp.h` | +1 line: rt_dtp_head_build decl | Zero |
| `src/runtime/pattern_match.c` | +12 lines: rt_dtp_head_build impl | Low |
| `src/emitter/BB_templates/x86_asm.h` | +20 lines: x86_and, jmp ROSLOT, and dispatch, rsi_proto_imm, proto_len_edx | Low |
| `src/emitter/BB_templates/bb_pattern_lit.cpp` | Full rewrite ~60 lines | Medium |
| `src/emitter/BB_templates/bb_pattern_alt.cpp` | Full rewrite ~20 lines | Low |
| `src/emitter/BB_templates/bb_dtp_assign.cpp` | Full rewrite ~20 lines | Low |
| `src/emitter/emit_bb.c` | +op_sval line 2349 | Zero |
| `src/interp/IR_interp.c` | +3 cases ~30 lines before IR_SCAN | Low |

