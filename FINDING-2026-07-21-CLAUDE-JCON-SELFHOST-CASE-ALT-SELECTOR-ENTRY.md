# FINDING-2026-07-21-CLAUDE-JCON-SELFHOST-CASE-ALT-SELECTOR-ENTRY.md

## Summary

Root-caused the ICN-CASE-ALT-SELECTOR bug that blocked SCRIP-jtran from parsing `if`/`every`/`to`.
Fix is oracle-correct and corpus-clean but breaks the self-host binary (scan-context SEGV, see below).
Fix NOT landed. Patch at `/home/claude/ICN-CASE-ALT-SELECTOR-WIP.patch`.

---

## What was built this session

- `icont`/`iconx` oracle built from `icon-master` (NoGraphics, v9.5.25a) — now at `/home/claude/icon-master/bin/`
- Full jtran toolchain rebuilt: SCRIP-jtran (505K asm, 0 bombs), SCRIP-jlink, jcon.zip (382 classes)
- `/home/claude/jt/jtran_base` — the BASELINE compiled jtran binary (healthy, hello green)
- WIP patch + repros saved to `/home/claude/`: `ICN-CASE-ALT-SELECTOR-WIP.patch`, `rep4-9.icn`

---

## Bug: ICN-CASE-ALT-SELECTOR — a value-alternation case selector enters at β (arm 1), skipping arm 0

**Symptom:** SCRIP-jtran bombs `Expecting parse_expression` on `if`/`every`/`to`. `local`/`:=`/`write`
work. `parse_expr11` dispatches on `case parse_tok_rec of { lex_CSETLIT | lex_INTLIT | … : … ; lex_IF : … ; lex_EVERY : … ; default : … }`.

**Minimal repro** (`/home/claude/rep5.icn`):
```icon
record tok(sym);
global A, B, C, D;
procedure setup(); A:=tok("A");B:=tok("B");C:=tok("C");D:=tok("D"); end
procedure cl(cur);
    case cur of { A | B | C : return "ABC"; default : return "DEF"; };
end
procedure main();
    setup();
    write("cur=A -> ", cl(A)); write("cur=D -> ", cl(D));
end
```
SCRIP: `A→DEF, D→DEF`. Oracle (icont): `A→ABC, D→DEF`.

**Root cause (gdb confirmed):** The `IDENTICAL` builtin receives `args[1]` (disjunction result) = record B's pointer, not A's. The disjunction entered at β (arm 1), skipping α (arm 0). Third sibling of ICN-CASE-ALT-CLOSE (2026-07-19) and ICN-CASE-ALT-BODY (2026-07-21) — the selector's own ENTRY EDGE into the disjunction is β-stamped by the default `γ_to`/`ω_to` wiring.

Proof: with cur=B (second arm), the test accidentally "matches" because the disjunction's first-product IS B. `gdb: args[1].ptr == global_B.ptr` for cur=A, confirming arm-1 entry.

---

## The WIP fix (`ICN-CASE-ALT-SELECTOR-WIP.patch`)

In `lower_icon.c` TT_CASE: track `chain_next_res` — whether the current `chain_next` (next clause's selector entry) is a value-alternation (all-non-resumable-alternand `TT_ALTERNATE`, plain subject). When true:
- α-force `idc.ω` (prev-clause mismatch → next-clause selector entry) via `lc_ω_to_α`.
- α-force the subject→first-clause edge via `lc_γ_to_α`.

**Fix passes:** all minimal repros (2-alt, 3-alt, mixed, alternation-not-first), both modes (m3/m4), full corpus gate 241/20/32 (zero regression).

---

## Why the fix was NOT landed: scan-context SEGV in jtran

When the fixed scrip recompiles the 505K-line jtran binary, hello SEGVs at preproc stage.

**gdb backtrace:**
```
#0  rt_gcheap_carve (at="", total=32) at gc_heap.c:120   ← garbage 'at' pointer
#4  try_call_builtin_by_name (fn="upto", ...)
#8  xchain2833_n76_α ()
#9  0x000000000000000a in ?? ()    ← return address trashed
```

**Root site:** `proc_preproc_scan_text` (preprocessor.icn ~line 292):
```icon
while tab(upto(interesting_chars)) do {
    case move(1) of {
        "\"" | "'": {           ← alternation selector inside scan context
            while tab(upto(interesting_in_quotes)) do { … }
        };
    };
};
```
The fix's α-force on `"\""  | "'"` (a value-alternation — passes the guard) physically chains into the adjacent `upto` box in the emitted code. α-forcing it restarts `upto` without the scan environment (δ/Σ/Δ).

**Three narrowing attempts failed** — flip count stayed exactly 38 in all cases:
1. `is_alt_selector` = bare `TT_ALTERNATE` (not any resumable selector)
2. + all alternands non-resumable
3. + plain (non-resumable) case subject

The 38 flipped cases all pass every AST-level guard, yet one of them physically neighbors a scan box in the emitter's chain. **AST classification alone cannot distinguish them.**

---

## Recommended fix shape for next session

**Option B (likely cleanest):** give the alternation selector its own `IR_GOTO` α-entry trampoline, exactly as `lower_every`/`lower_while` do at lower_icon.c:826/840/1112:
```c
IR_t * CENT = build(cx, IR_GOTO, NULL, NULL);
lc_γ_to_α(CENT, ke);   // α-force through the trampoline
lc_ω_to_α(CENT, ke);
```
Then wire the subject/mismatch edges to `CENT` (not directly to `ke`). The trampoline is a dedicated node that the chain-BFS schedules separately, so it cannot be physically fused with a scan box's slot. This isolates the forced-fresh entry from the emitter's chain layout, which is what the AST-gate approach couldn't achieve.

**Option A (alternative):** resolve at emit time: when the emitter walks a DISJUNCTION whose immediate predecessor is a case-selector wiring (detectable from the edge tag), force α-entry there. Harder because the emitter is not supposed to know context (RULES.md FACT RULE no lang globals past first dispatch).

**Start with Option B.** Gate: corpus 241/20/32 green; jtran hello green at baseline. `jtran_base` at `/home/claude/jt/jtran_base` for regression comparison.

---

## Session artifact locations

| File | Description |
|------|-------------|
| `/home/claude/ICN-CASE-ALT-SELECTOR-WIP.patch` | The WIP fix (reverted from SCRIP HEAD) |
| `/home/claude/rep4.icn` | Mixed alt+singles case repro |
| `/home/claude/rep5.icn` | 3-alternative case repro (canonical minimal) |
| `/home/claude/rep8.icn` | 2-alternative case repro |
| `/home/claude/rep9.icn` | Alternation-not-first clause repro |
| `/home/claude/icon-master/bin/icont` | Oracle icont v9.5.25a (NoGraphics) |
| `/home/claude/jt/jtran_base` | Baseline SCRIP-jtran binary (hello green) |
| `/home/claude/jt/jtran_base.s` | Baseline jtran .s for diff comparison |

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
