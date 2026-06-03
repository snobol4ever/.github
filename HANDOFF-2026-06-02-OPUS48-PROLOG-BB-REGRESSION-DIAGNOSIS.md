# HANDOFF 2026-06-02 (Opus 4.8) — Prolog BB mode-3/mode-4 REGRESSION: diagnosis + landed-ready fix

## TL;DR

A **two-stage regression** silently broke the Prolog mode-3 and mode-4 gates between the
GOAL-PROLOG-BB watermark (`fc8f25d`) and current SCRIP `origin/main` (`c83de6d`).
Neither offending commit ran the Prolog gate; both verified only SNOBOL4 + Icon.

- **GATE-3 m3: 111/111 → 99/111** (12 flat-path rungs broken)
- **GATE-3 m4:  86 PASS → 0 PASS** (total)
- GATE-1 m3: 5/5 → 2/5 ; GATE-1 m4: 5/5 → 0/5
- GATE-3 **m2 stays 111/111** (the mode-2 oracle `IR_interp.c` is untouched — HARD gate intact).

This session **fully root-caused** it and prepared a **validated, mechanical fix**. The fix is
captured as an appliable patch + converted source files in `wip-patches/` (see "Landing the fix"
below). SCRIP `origin/main` was left at `c83de6d` (clean, compiling) — no broken commit was pushed,
per RULES "No broken commits". The remaining work (one box) is mechanical and specified exactly here.

---

## Root cause — the two-stage break

### Stage 1 — `06826c8` (PL-RV-5) wrongly re-bombed a LIVE box
The PL-RV-5 commit message asserted that `bb_builtin`/`bb_goal`/`bb_choice` were "all still
`x86_bomb` stubs from `9afac84`." **That was factually wrong.** At the watermark `fc8f25d` those were
the *real* boxes (`bb_builtin.cpp` = 2427 lines, `bb_goal` = 264, `bb_choice` = 318), restored by the
`ced1acd…fc8f25d` series. PL-RV-5 (converting `bb_unify`) reduced `bb_builtin.cpp` back to an 18-line
`x86_bomb` stub on the false belief it was already a stub. (Line-count proof: `bb_builtin.cpp` is
18L@`9afac84`, **2427L@`fc8f25d`**, 18L@`06826c8`.)

### Stage 2 — `cd10224` (STUB CLEANUP) deleted the boxes AND their dispatch
`cd10224` deleted 54 "stub" `bb_*.cpp` files — including the now-bombed `bb_builtin.cpp`,
`bb_goal.cpp`, `bb_choice.cpp`, plus `bb_atom.cpp` and `bb_logicvar.cpp` — and **stripped 78 lines
from `emit_core.c`'s `walk_bb_node` dispatch**, removing these cases:
```
    case IR_GOAL:     bb_prepare_pl(nd); bb_goal(nd);    return 0;
    case IR_BUILTIN:  bb_prepare_pl(nd); bb_builtin(nd); return 0;
    case IR_LOGICVAR: bb_logicvar(nd);                   return 0;
    case IR_ATOM:     bb_prepare_pl(nd); bb_atom(nd);    return 0;
    case IR_CHOICE:   bb_choice(nd);                     return 0;
```

### Why the "safety" argument was wrong (the silent-miscompile mechanism)
`cd10224`'s justification: *"a pure x86_bomb stub aborts the generated program when reached, so no
mode-3/4 test passing today reaches one."* True for a bomb that still emits an abort blob. **But once
the dispatch case is ALSO removed**, the IR kind falls to `walk_bb_node`'s `default:` which does
`fprintf(out, "; [walk_bb_node: kind=%d unhandled]\n", ...); return 1;`. In the mode-3 BINARY flat
path this writes a **stray text comment into the byte stream** and `bb_build_flat` still returns a
non-NULL buffer — so the program runs, prints garbage, and produces no output. That is a **silent
miscompile, not a loud abort.** Mode-3 `rung01_hello_hello` shows it: emits `; [walk_bb_node: kind=55
unhandled]` (kind 55 = `IR_BUILTIN`) instead of `hello`.

The 12 broken m3 rungs are exactly the **flat-path** ones (`pl_flat_body_root` accepts a single GCONJ
of simple goals → `bb_build_flat` → `walk_bb_node`): `rung01_hello`, `rung22_write_canonical_print`,
`rung23_arith_ext_*` (5), `rung29_number_ops_*` (5). Multi-clause / call programs were unaffected in
m3 because they route to the oracle (`IR_interp_once`).

---

## The fix (validated this session)

Restore all five Prolog boxes, **converted to the `bb_emit_x86`/`x86()` idiom** (the `bb_bin_t` type
is ABOLISHED — a faithful restore would not compile and would trip `test_gate_no_bb_bin_t.sh`), and
re-add the five `walk_bb_node` dispatch cases (using the renamed `bb_prepare`, see renames below).

### Post-watermark renames that MUST be applied to the restored boxes
The LI-3 rename (`12b820d`/`99fa787`) stripped the `pl_` infix from the runtime ABI, and `a822f80`
renamed two emitter helpers. All targets confirmed present at HEAD. Apply mechanically:
- `rt_pl_*`  →  `rt_*`   (e.g. `rt_pl_write_atom`→`rt_write_atom`, `rt_pl_is`→`rt_is`,
  `rt_pl_node_to_term`→`rt_node_to_term`, `rt_pl_unify_const`→`rt_unify_const`, …)
- `bb_prepare_pl`  →  `bb_prepare`
- `flat_drive_pl_choice`  →  `flat_drive_choice`
- (The deleted value-stack helpers `rt_pl_atom_push`/`rt_pl_var_push` appear ONLY in comments at
  `fc8f25d` — they vanish with comment-stripping; do NOT resurrect them. NO-RESURRECT rule.)
- Add `#include "IR_interp_state.h"` to `bb_goal.cpp` (the `bb_goal_state_t` struct moved there in the
  RS-2 reorg; `emit_bb.c` includes it the same way).

### Per-box conversion (4 of 5 DONE this session — see `wip-patches/converted-boxes/`)

**`bb_atom` / `bb_logicvar` — DONE.** Trivial four-port pass-throughs (α→γ, β→ω), no `bb_bin_t`:
```cpp
return IF(MEDIUM_TEXT, s_1asm(std::string(_.lbl_α) + ":") + s_comment("# BOX RESOLVE_ATOM(...) [pass-through]"))
     + x86("jmp", PORT_GAMMA) + x86("def", PORT_BETA) + x86("jmp", PORT_OMEGA);
...
extern "C" void bb_atom(IR_t * pBB) { bb_emit_x86(bb_atom_str(pBB)); }
```
Both compile clean.

**`bb_choice` / `bb_goal` — DONE (dead-twin conversions).** PROVEN that the mode-3 flat path can never
emit these: `pl_flat_goal_is_simple` only admits `IR_SUCCEED/IR_CUT/IR_ATOM/IR_BUILTIN/IR_UNIFY`, and
`pl_flat_body_root` returns NULL for any graph containing `IR_CHOICE`/`IR_GOAL` → multi-clause/call
programs route to the mode-2 oracle. So each box's `MEDIUM_BINARY` arm is **dead** (same situation as
`bb_disj` in PL-RV-4). Conversion = **drop the entire `MEDIUM_BINARY` block** (and the DUP-FORM-1
`build_arg_bin` walker + the `emit_build_compound_term_bin` extern in `bb_goal`), **keep the
`MEDIUM_TEXT` mode-4 scaffold verbatim**, and change the wrapper to `bb_emit_x86(...)`. Both compile
clean. Zero `bb_bin_t`/`b.size()`/`bb_emit_asm_result`.

**`bb_builtin` — NOT DONE (the one remaining item; the PL-RV-6 deliverable).**
Its `MEDIUM_BINARY` arm is **LIVE** (mode-3 flat emits it for `write`/`writeln`/`print`/`nl`/`halt`,
`is` with simple arith, and the arith comparisons), so it CANNOT be dropped — it needs a
**byte-identical** conversion. The transform is mechanical and fully validated:

1. **Helper** (add to `x86_asm.h`, additive — it is the private home of the record producers):
   ```cpp
   inline std::string x86_lit_bytes(const std::string & b) {   // chunk raw straight-line bytes into Lrecs
       if (!MEDIUM_BINARY) return b;
       std::string r; size_t i = 0;
       while (i < b.size()) { size_t k = b.size()-i; if (k > 255) k = 255; r += x86_Lrec(b.substr(i,k)); i += k; }
       return r;
   }
   ```
   Each arm builds a straight-line body `std::string b` (no internal patch sites — every `bin.site`
   in the original is in the *tail*, all offsets ≥ `b.size()`), so wrapping the whole body is safe.

2. **Three tail shapes** — replace `int j=(int)b.size(); bin={...}; return b + <tail bytes>;` with
   `return x86_lit_bytes(b) + <x86 tail>;`. The three (distinguishable by the return's byte string,
   verified byte-identical against `x86_jmp`/`x86_jcc`/`x86_deflabel`):
   - **Type 1** (`bin={{j+1,j+5,j+6},{γ,β,γ},{false,true,false}}`,
     `return b + "\xE9"+u32le(0) + "\xE9"+u32le(0)`):
     → `x86_lit_bytes(b) + x86("jmp",PORT_GAMMA) + x86("def",PORT_BETA) + x86("jmp",PORT_GAMMA)`
   - **Type 2 / halt** (`bin={{j,j+1},{β,γ},{true,false}}`, `return b + "\xE9"+u32le(0)`):
     → `x86_lit_bytes(b) + x86("def",PORT_BETA) + x86("jmp",PORT_GAMMA)`
   - **Type 3 / type-test+compare** (`bin={{j+2,j+6+1,j+6+5+1},{ω,γ,ω},{false,false,false}}` — NOTE: **no β define**,
     `return b + "\x0F\x84"+u32le(0) + "\xE9"+u32le(0) + "\xE9"+u32le(0)`):
     → `x86_lit_bytes(b) + x86("je",PORT_OMEGA) + x86("jmp",PORT_GAMMA) + x86("jmp",PORT_OMEGA)`
     (do **NOT** insert `x86("def",PORT_BETA)` — Type 3 defines no β).

3. **Wrapper**: `bb_builtin_str(IR_t*, bb_bin_t&)` → `bb_builtin_str(IR_t*)`; delete the leading
   `bin = {};`; `extern "C" void bb_builtin(IR_t* pBB){ bb_emit_x86(bb_builtin_str(pBB)); }`.

4. **OPEN QUESTION to verify first** (the one place I did not fully confirm before handing off):
   who defines the box's **α label** in BINARY mode, and the **β label** for Type-3 arms? The
   original `bin` tables for these arms define β (Type 1/2) but NOT α, and Type 3 defines neither
   α nor β. Confirm against the converted **`bb_unify.cpp`** (PL-RV-5, the live converted reference):
   read how it emits/omits the `α:`/`β:` definitions and mirror it. If `bb_unify` emits a leading
   `x86("def", PORT_ALPHA)` (or relies on the flat driver to define α), do the same in `bb_builtin`.
   Also leave `emit_build_compound_term` (TEXT) DEFINED in `bb_builtin.cpp` — `bb_goal` (and mode-4
   generally) externs it. The `emit_build_compound_term_bin` (the BINARY twin) is dead on the flat
   path and SHOULD be deleted (DUP FORM 1), but only after confirming no live binary arm calls it
   (the compound `write` arm is dead because `pl_flat_goal_is_simple` admits only atom/int/var args).

### Infrastructure (DONE this session, included in the patch)
- `emit_core.c`: 5 dispatch cases re-added to `walk_bb_node` (Prolog block, contiguous), using `bb_prepare`.
- `bb_templates.h`: prototypes `void bb_goal/bb_builtin/bb_choice/bb_atom/bb_logicvar (IR_t*)`.
- `Makefile`: 5 files added to `RT_PIC_SRCS` AND to the explicit `scrip` recipe compile block
  (scrip does NOT glob template objects — each `bb_*.cpp` has its own `$(CXX) -c … -o …` line).

---

## Landing the fix (next session, ~15 calls)

```bash
cd /home/claude/SCRIP
git apply /home/claude/.github/wip-patches/2026-06-02-prolog-bb-regression-restore-WIP.patch
# bb_atom/logicvar/choice/goal + dispatch + Makefile + prototypes are now in place and COMPILE.
# bb_builtin.cpp from the patch STILL uses bb_bin_t (won't compile) — convert it per "bb_builtin" above:
#   1) add x86_lit_bytes to x86_asm.h
#   2) verify α/β contract against bb_unify.cpp
#   3) apply the 3 tail-shape replacements across the 28 arms (sed/python; they are exact-match)
#   4) delete `int j=(int)b.size();` + `bin={...};` lines + the bb_bin_t wrapper; delete emit_build_compound_term_bin
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh                       # GATE-1 → expect 5/5/5
bash scripts/test_prolog_rung_suite.sh                  # GATE-3 → expect m2 111/111, m3 111/111, m4 86
bash scripts/test_gate_no_bb_bin_t.sh                   # must read 0
```
Target = the watermark numbers (m2 111/111 byte-identical, m3 111/111, m4 86 PASS / 25 EXCISED).
If green, commit SCRIP + push (code repo first), then update the GOAL watermark.

The 4 already-converted box files are also stored verbatim at
`wip-patches/converted-boxes/` (in case the patch context drifts after future SCRIP commits).

---

## Files in this handoff
- `HANDOFF-2026-06-02-OPUS48-PROLOG-BB-REGRESSION-DIAGNOSIS.md` (this file)
- `wip-patches/2026-06-02-prolog-bb-regression-restore-WIP.patch` (full appliable WIP: 5 boxes restored+converted, dispatch, Makefile, prototypes)
- `wip-patches/converted-boxes/{bb_atom,bb_logicvar,bb_choice,bb_goal}.cpp` (the 4 DONE, compiling boxes)
- `wip-patches/converted-boxes/bb_builtin.cpp.UNCONVERTED-still-uses-bb_bin_t` (restored 2427L box, renames applied, awaiting the tail/shell conversion above)
- `GOAL-PROLOG-BB.md` watermark updated.

Authors: LCherryholmes · Claude Opus 4.8
