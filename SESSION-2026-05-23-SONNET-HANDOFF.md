# HANDOFF: 2026-05-23 (Sonnet 4.6) — ER-4 INLINE-TEXT Conversions Complete

**Time:** Session end 2026-05-23
**Gate:** PASS=419 FAIL=0 STUB=635 NEW=0 GONE=0 ✅
**Commits:** 2 conversion commits + 2 rule commits
**Status:** Ready for ER-4c (bb_pat_arb) or ER-5 (SM templates)

---

## Summary of Work

### Conversions Completed (This Session)
1. **bb_pat_pos.cpp** — POS/RPOS: JVM+NET arms converted to pure string concat
2. **bb_pat_len.cpp** — LEN: JVM+NET arms converted to pure string concat

### Critical Discovery: UTF-8 Greek Escapes
**Problem:** Repeated mistake of writing `\\316\\261` (octal escape syntax) in C++ string literals.
- In C, `\316` is an octal escape that becomes a byte.
- In C++, `\\` is an escape that becomes a single backslash in the string.
- Result: `\\316\\261` emitted literal backslash-digits, not UTF-8 α.

**Solution:** Write actual UTF-8 characters directly in the source file:
```cpp
// CORRECT (source is UTF-8):
s_directive(".method public α()Lbb/bb_box$Spec;")

// WRONG:
s_directive(".method public \\316\\261()Lbb/bb_box$Spec;")  // emits: \316\261
```

### Rule Added to GOAL-HEADQUARTERS.md
New section: **"⚠️ CRITICAL RULE: UTF-8 Greek Letters in CPP String Literals (ER-4+)"**
- Explains C++ vs C octal escape semantics
- Lists affected characters (α β ω Δ Σ)
- Provides test strategy (run gate, check for literal backslashes)
- Commits: `09727842`, `2a10144e`

---

## Architecture Pattern (Proven)

Every INLINE-TEXT BB template `TEMPLATE_str()` follows this structure:

```cpp
static std::string bb_pat_FOO_str(BB_t * pBB) {
    // ... 
    if (IS_X86) {
        if (IS_BIN) {
            emit_jmp(...); emit_label_define(...);  // imperative, relocation-aware
            return std::string();  // empty string (no text emitted)
        }
        // IS_TEXT arm:
        return s_comment(...) + s_2asm(...) + s_1asm(...) + ...;  // pure concat
    }
    if (IS_JVM) {
        return jvm_class_hdr_str(...) + s_directive(...) + s_1asm(...) + ...;  // pure concat
    }
    if (IS_NET) {
        return net_class_hdr_str(...) + net_α_hdr_str() + s_1asm(...) + ...;  // pure concat
    }
    if (IS_JS) {
        return emit_fmt(...) + "literal string" + ...;  // pure concat
    }
    if (IS_WASM) {
        return emit_fmt("...\\n");  // pure concat
    }
    return std::string();
}

extern "C" void bb_pat_FOO(BB_t * pBB) {
    std::string out = bb_pat_FOO_str(pBB);
    if (!out.empty()) emit_text_n(out.data(), out.size());
}
```

**Key invariants:**
- Every backend arm returns a single `std::string` (concat or empty)
- Relocation-aware arms (IS_BIN) stay imperative, return empty
- Text/bytecode arms (IS_TEXT/IS_JVM/IS_NET/IS_JS/IS_WASM) return pure concat
- One write per opcode via `emit_text_n()`

---

## INLINE-TEXT Boxes Status

| Box | Status | Commits |
|-----|--------|---------|
| bb_pat_abort | ✅ Complete | prior session |
| bb_pat_fence | ✅ Complete | prior session |
| bb_pat_rem | ✅ Complete | prior session |
| bb_pat_tab | ✅ Complete | prior session |
| bb_pat_any | ✅ Complete | prior session |
| bb_pat_pos | ✅ Complete (this session) | d964c628 |
| bb_pat_len | ✅ Complete (this session) | f26ea72d |
| bb_pat_arb | ⏳ TODO (ER-4c) | — |

**Note:** `bb_pat_arb` is last INLINE-TEXT. No x86 arm yet (TODO).

---

## What's NOT Done (Intentionally Deferred)

**DELEGATING boxes** — recursive `emit_flat_ir()`, NOT simple pattern match:
- bb_pat_alt
- bb_pat_cat
- bb_pat_break
- bb_pat_span
- bb_pat_notany
- bb_pat_lit
- bb_arbno

**These require separate rung (CPP-2b)** — different conversion strategy (recursive dispatch, not simple concat).

---

## Next Steps (Priority Order)

1. **ER-4c:** Convert bb_pat_arb JVM+NET arms (identical pattern to pos/len)
2. **ER-2:** Convert jvm_/net_ layer-2 helpers to return std::string
3. **ER-5:** All SM_templates (sm_*.c → pure concat, identical pattern, mechanical)
4. **ER-6:** All XA_templates (xa_*.c → pure concat, identical pattern, mechanical)
5. **ER-7:** Delete FILE* and buffer locals once all templates return string

---

## Testing Strategy (Locked In)

After **every** file conversion:
```bash
cd /home/claude/one4all
make -j4 scrip >/dev/null 2>&1 && bash scripts/test_per_kind_diff.sh
# Expect: PASS=419 FAIL=0 STUB=635 NEW=0 GONE=0
```

If **any** JVM/NET/x86 arm differs:
- Check for literal `\316`, `\262`, or other backslash-digits in output → UTF-8 rule violated
- Check `.maxstack` / `.limit` precision → copy exact values from baseline
- Run per-cell diff to see exact divergence

---

## Code Quality Notes

1. **UTF-8 Rule now enforced:** Future conversions must use actual Greek characters, not octal escapes
2. **Baseline precision:** JVM/NET arms have exact `.maxstack`, `.limit`, `.locals` directives — must match
3. **Spacing:** x86 has precise column alignment; s_1asm/s_2asm/s_L*asm helpers guarantee this
4. **Pattern reuse:** Each new template follows the same structure — low cognitive load

---

## Session Stats

| Metric | Value |
|--------|-------|
| Conversions | 2 (pos, len) |
| Files touched | 2 BB templates + 1 GOAL file |
| Gate runs | 6 (all green) |
| Commits | 4 (2 conversions + 2 rule clarifications) |
| New rule | UTF-8 Greek escapes (critical for future) |
| Context used | ~60% (Sonnet 4.6) |

---

## Handoff Checklist

- [x] Gate is green (PASS=419 FAIL=0 STUB=635)
- [x] All commits pushed (one4all + .github)
- [x] Rule documented in GOAL-HEADQUARTERS.md
- [x] Pattern verified and replicable
- [x] No uncommitted changes
- [x] Next steps clear and prioritized

**Ready for:** Next session or immediate ER-4c (bb_pat_arb).

---

**Session by:** Claude Sonnet 4.6
**Directed by:** Lon Jones Cherryholmes
