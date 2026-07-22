# FINDING 2026-07-22 (Claude) — SN4: loop unrolling on literal paths yields zero delta; strchr on variable-needle path is the real target

**Goal:** GOAL-SNOBOL4-BB.  **Session directive:** "Implement loop un-rolling fully for literal, ANY, NOTANY, SPAN, BREAK, and BREAKX."

---

## WHAT WAS DONE

Six templates rewritten; one new x86 encoder added to x86_asm.h:

**bb_match_span.cpp / bb_match_break.cpp / bb_match_breakx.cpp** — for the emit-time literal-needle arm (`op_sa < 0`): replaced the FR-counter loop with a register-cursor design (`movsxd rcx,r14d` at entry; `add ecx,1` per character; ecx compared to r15d for bounds). The loop body is unrolled ×4 before jumping back. Membership test: for needles 1–8 chars, an inline `cmp esi,imm8` + je/jne chain; for needles >8 chars, the existing 256-byte RO cset-table. The `op_sa >= 0` (variable-needle, strchr) arm is unchanged in all three.

**bb_match_any.cpp / bb_match_notany.cpp** — for literal needles 2–8 chars: inline compare chain with a shared hit-label (ANY) or per-char je-to-omega (NOTANY). Single-char and table paths unchanged.

**bb_match_lit.cpp** — added 4-byte dword chunk arm (`k+4 <= n`: `mov edx,LIDX(k)` + `cmp edx,imm32` + omega jne), filling the gap between byte-by-byte and the existing 8-byte qword arm. The `n > 10` gate suppressing the qword arm for short literals was also dropped (qwords fire whenever 8 bytes remain).

**x86_asm.h** — added `x86_mov_subj_d` (32-bit `mov dst,[r13+rcx+disp]`) beside the existing 64-bit `x86_mov_subj_q`. Encoder mirrors the q form: REX.R=0x41, opcode 0x8B, ModRM disp8, SIB r13+rcx. Dispatch case added at line ~1214: `XK_REG × XK_R13RCX` with 32-bit destination (the existing arm already routed 64-bit-dest). Required to compile the register-cursor templates (BREAK/BREAKX use `mov edx,[r13+rcx+k]`).

---

## MEASUREMENT RESULTS (interleaved A/B, same -O0 libscrip_rt.so, 5 reps each)

### 16-benchmark suite (mode-4, self-reported ms)

| bench | HEAD min | unroll min | delta |
|---|---|---|---|
| pattern_bt | 170 | 171 | ≈0 |
| string_pattern | 3445 | 3405 | noise |
| string_manip | 1927 | 1962 | ≈0 |
| mixed_workload | 894 | 932 | **+4% slower** |

All 16 output-identical. All others unchanged.

### CLAWS5 / TREEBANK real programs (mode-3, interleaved 5 reps)

| program | HEAD min | unroll min | delta |
|---|---|---|---|
| claws5 | 30 ms | 29 ms | noise |
| treebank-array | 149 ms | 149 ms | 0 |
| treebank-list | 88 ms | 88 ms | 0 |

All output-identical. Emitted .s byte sizes changed by ≤422 bytes on any program (within text-layout noise).

**VERDICT: zero measurable improvement. The unroll is correct and C-call-free on the paths it covers, but those paths are not where the time is spent.**

---

## ROOT CAUSE DIAGNOSIS

**The bottleneck is strchr on the variable-needle path, not the loop itself.**

Every cset primitive has two arms:
- `op_sa < 0` (emit-time literal needle) — THIS is what the unroll covers. HEAD *already* emits a 256-byte RO cset-table + `cmpb0 [rdi+rsi]` here; zero C calls. The unroll replaced that with inline compares for small needles and ×4 body replication.
- `op_sa >= 0` (variable needle — a runtime DESCR in a frame slot) — calls `strchr(needle, char)` **per character scanned**. THIS is the hot path.

Real SNOBOL4 uses named character classes: `SPAN(DIGITS)`, `ANY(UCASE)`, `BREAK(PUNCT)`. These lower as variable needles. CLAWS5 and TREEBANK confirm: zero inline compare chains in their emitted .s; strchr present in treebank-array/list (3 calls each).

**The emitted .s size is the diagnostic.** If the unroll had fired for these programs, the .s would be substantially larger (×4 unrolled bodies + up to 8 compare instructions per needle character). Instead: ±2 bytes on treebank, -422 bytes on claws5. The unroll is dead code for all programs measured.

---

## CORRECTION: membership-chain threshold may be a regression

The chain arm fires for literal needles 1–8 chars. For a 6–8 char literal needle, this emits up to 8 `cmp`/`je` pairs (ANY) or `cmp`/`je-to-omega` pairs (NOTANY/BREAK), where HEAD emitted one table load + `cmpb0`. 8 compares vs 1 lookup is plausibly slower on any branch-predictor-friendly workload. mixed_workload's +4% points here. The threshold should be 2–3, not 8, or the chain arm removed entirely. Recommend reverting to table-only on the literal path unless a controlled probe with a known 2–4 char literal needle shows improvement.

---

## MISSING: NO ZC_UNROLL SWITCH

The unroll factor (4) and chain threshold (8) are hardcoded in three separate files. Per the Lon directive on ZC_FRAME (ARCH-ICON): measurement requires side-by-side selectable variants. These should be:

```c
// zeta_choices.h
#ifndef ZC_UNROLL_FACTOR
#define ZC_UNROLL_FACTOR 0   /* 0 = disabled (loop back immediately); 4 = quad-unroll */
#endif
#ifndef ZC_CSET_CHAIN_MAX
#define ZC_CSET_CHAIN_MAX 2  /* literal needles <= this use inline chain; else cset-table */
#endif
```

Without these, A/B requires staging two compiler binaries (done this session but laborious).

---

## THE REAL TARGET: eliminate strchr on the variable-needle path

**Fix shape:** at α, build a 256-byte membership table into the ζ frame from the needle DESCR. The scan loop then uses `movzx esi,[r13+rcx]` + `cmpb0 [rbp+rsi]` (or `[rsp+rsi]` under ZC_FRAME_RSP) — one load per character, no call, same code shape as the existing literal-path table. Works for any needle length. Cost: 256 bytes of ζ-frame per match activation (already granted for other purposes; an additional `bb_slot_claim(256)` covers it) + one α-time fill loop (~256 iterations, amortized over the scan).

This is the same idea as `csettab_label` for literals, but filled at runtime from the needle DESCR instead of at emit-time from `_.op_sval`. For patterns that run thousands of times per program (CLAWS5 scans 90k+ tokens), the one-time fill cost is invisible.

---

## CORRECTNESS STATUS AT HANDOFF

- Crosscheck m3 302/302, m4 302/302, DIVERGE=0 — stash-verified byte-identical to HEAD
- Fail set: test_case 140/141/214/215/216/1020/1021 — ALL pre-existing (stash-verified)
- Smokes 7/7 ×2 modes
- Template byte-identity gate: PASS=4 FAIL=0
- Strict medium gate: GATE FAIL on xa_flat.cpp(117) — pre-existing (stash-verified)
- Oracle-identical semantic probe (both modes): BREAK/BREAKX/SPAN/ANY/NOTANY/LIT all paths covered including chain/table/hit/miss/EOS/beta-backtrack

## TREEBANK REF-DIFF (pre-existing, not this session)

treebank-array.ref and treebank-list.ref diverge from SCRIP m3 output at HEAD. stash-verify shows this predates this session. A SPITBOL oracle re-run of `.ref` is owed.

## KEY PATHS

- `src/templates/bb_match_{span,break,breakx,any,notany,lit}.cpp` — the six rewritten templates
- `src/templates/x86_asm.h` ~line 1023+11 — `x86_mov_subj_d` encoder + dispatch case at ~1214
- `src/contracts/zeta_choices.h` — where ZC_UNROLL_FACTOR / ZC_CSET_CHAIN_MAX belong (not yet added)
- `scripts/test_gate_template_medium_invisible.sh --strict` — pre-existing FAIL on xa_flat.cpp; not introduced here
