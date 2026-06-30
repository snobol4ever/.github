# HANDOFF — 2026-06-29 — Sonnet 4.6 — GZ#5 cleanup (dead TUs, emit.cpp format, template flatten, IR_e alphabetize, IR_OP_COUNT residue)

## SCRIP HEAD: `f54777b6` — pushed to origin/main ✅
## .github HEAD: this doc + GOAL watermark — pushed ✅

---

## Session arc

User-directed cleanup pass on top of the consolidated `emit.cpp` (a4f51066). Five
behavior-preserving units, each built + verified + committed separately. No goal-ladder
rung was closed; this is hygiene that de-risks the upcoming R2/R4 work. Lon provided the
credential at the end and directed the handoff.

**Standing-directive compliance:** per GOAL-IR-IMMUTABLE-EMIT.md (NO artifact regen, NO full
regression, `.s` byte-identity is NOT a gate), no `.s` artifact regen was run. Every change
was independently PROVEN `.s` byte-identical on representative programs anyway (so regen would
have produced zero commits — idempotent). Verification gate each step: official Icon suite
`scripts/test_icon_all_rungs.sh` = **PASS=62 / XFAIL=36** and mutation gate
`scripts/test_gate_emit_no_ir_mutation.sh` = **HARD=4**, both unchanged throughout.

---

## What landed (6 commits over a4f51066)

1. **`5b6d21db`** — remove 6 dead emitter TUs: the 4 hibernating backend driver stubs
   `emit_{wasm,js,jvm,net}_drive.c` (identical 11-line abort skeletons, 0 build refs),
   the 1-line orphan `sm_codegen_x64_emit.c`, and the Prolog `emit_term_build.cpp`
   (`is`/`=:=` term builder, 0 build refs). X86-ONLY + Icon-only ⇒ all dead.

2. **`3f46d8ca`** — emit.cpp textual formatting to house style. The file-consolidation that
   produced emit.cpp had fused 14 separator comments onto the next function
   (`/*---*/static void f(){…}`), fused 2 global decls onto the next function
   (`= 0;void g(){…}`), left 5 blank lines and 3 stacked-separator runs, and had 28
   byte-over-200 lines (Greek α/β/γ/ω are 2-byte UTF-8; 28 genuine >200-CHAR lines confirmed).
   Un-fused all, removed blanks, collapsed stacked separators, wrapped every >200 line at
   logical boundaries, and stripped 16 always-false `IR_OP_COUNT` disjuncts on the two
   `wintexpr` lines. Proven byte-identical (hello/generators/fact `.s`).

3. **`44831d09`** — flatten `src/emitter/{BB,XA}_templates/` → `src/templates/` (155 .cpp + 6 .h,
   NO filename collisions). The move is 3-deep→2-deep, so depth-dependent relative includes
   were corrected: `../../runtime/` → `../runtime/`, `../BB_templates/x86_asm.h` → `x86_asm.h`
   (now same dir), `../emit_bb.h` → `../emitter/emit_bb.h` (and `../emit_form.h`,
   `../x86_opcodes.h` likewise). Repointed emit.cpp includes (`templates/…`, resolves via
   `-I$(SRC)`), the Makefile source list + per-file compile rules + `-I` flags
   (`-I$(SRC)/emitter/XA_templates` → `-I$(SRC)/templates`), and **19 gate/util scripts** that
   scan the template dir (uniform substitution `emitter/{BB,XA}_templates` → `templates`).
   82 template objects rebuild clean from the new path; template-purity gate correctly follows
   the new path (found `src/templates/xa_flat.cpp(34)`, a pre-existing WIP count).

4. **`a0b2d18e`** — alphabetize the `IR_e` enum in `IR.h`, `IR_OP_COUNT` kept LAST (it is the
   array-sizing sentinel + the `k < IR_OP_COUNT` bound). Reorder-safety was PROVEN before
   touching it: `kind_names[]` uses designated initializers, `ir_is_call_kind` /
   `ir_node_produces_value` use explicit `==` (no range checks), there are ZERO numeric op
   comparisons anywhere, `--dump-ir` is name-based, and `IR_node_alloc` sets `op` explicitly
   (nothing relies on `op==0==IR_LIT_I`). x86 output does not encode enum values ⇒ `.s`
   byte-identical, confirming nothing depends on the numeric ordering.
   NOTE: `scrip_ir.c`'s designated-initializer arrays are reorder-safe and were left in source
   order (the user scoped alphabetization to `IR.h`); reordering them to match is optional.

5. **`f54777b6`** — remove ALL `IR_OP_COUNT` dead-comparison residue from emit.cpp (44 lines:
   1255→1211). `IR_OP_COUNT` is never assigned to any node (0 assignments), so every
   `op == IR_OP_COUNT` is always-false and every `op != IR_OP_COUNT` is always-true — pure
   leftovers from the enum amputation (where real ops IR_EVERY/IR_WHILE/IR_IF/IR_LIMIT/IR_DEREF
   etc. were collapsed to the placeholder). Removed: `bb_fill_alpha`'s 5 dead GVA/IDX/define
   label blocks (21 lines), 9 always-false `||` disjuncts, 2 always-true `!=` conjuncts, 12
   single-line dead `if`s, 2 multi-line dead blocks (the IR_LIMIT slot-init for-loop + an inner
   ω-resolve block), 1 two-line varslot dead-`if`. The live generator ω/stack-chain logic
   around them (which uses `ir_is_generator_kind`, IR_CALL, IR_PROC_GEN, IR_BINOP) was kept
   intact. Proven byte-identical.

---

## Verification (every step)
- Build: `make -s scrip` + `make -s libscrip_rt` clean (pre-existing INTVAL/REALVAL warnings only).
- Icon suite: `scripts/test_icon_all_rungs.sh` = **PASS=62 FAIL=191 XFAIL=36 TOTAL=289** — unchanged.
- Mutation gate: `scripts/test_gate_emit_no_ir_mutation.sh` = **HARD=4** (A op-writes=4, B=0) — unchanged.
- `.s` byte-identity vs a pre-session baseline (`/tmp/sbase/{hello,generators,fact}.s`) verified
  after commits 2, 4, 5 — all IDENTICAL. (commits 1 and 3 are build-structure only.)
- Generator spot-checks confirm the still-stubbed baseline: `every write(1 to 3)` → (nothing),
  `write(1 to 5)` → `1`, `every write((1 to 3)+(1 to 2))` → (nothing). This is the PRE-EXISTING
  IR_FAIL-stub behavior for every/to-by — the byte-identity proves this session did not change it.

## Build / verify recipe (sandbox)
```
apt-get install -y libgc-dev
make -s scrip && make -s libscrip_rt
SCRIP_ICN_BB=1 ./scrip --run file.icn                     # mode-3
SCRIP_ICN_BB=1 ./scrip --compile --target=x86 file.icn    # mode-4
bash scripts/test_icon_all_rungs.sh                        # PASS=62/XFAIL=36
bash scripts/test_gate_emit_no_ir_mutation.sh             # HARD=4
```

---

## What is NOT done / next session (dependency order)

1. **R2 (trivial, teed up):** delete 10 abort stubs from emit.cpp + their `emit_bb.h` decls.
   ALL confirmed to have ZERO callers in the 157 live-compiled TUs (verified this session); the
   only in-file references are their own multi-line def bodies plus one stale comment for
   `walk_bb_flat` (line ~1039). The 10: `walk_bb_flat`, `bb_build_flat`, `codegen_flat_build`,
   `gz_emit_catch`, `resolve_choice_clause_label`, `gva_collect_graph`,
   `gvar_flat_chain_build`, `gvar_flat_chain_build_at`, `gvar_flat_chain_build_text`,
   `gvar_flat_chain_build_text_at`. (Do NOT remove `bb_emit_limit_init`, `child_cache_get_lbl`,
   `emit_intern_str`, `bb_kind_is_driver_owned` without re-checking — not verified dead.)

2. **R4 (the real goal):** grow `emit_drive` to own IR_IF / IR_EVERY / IR_TO_BY. `lower_every`
   and `lower_if` in `lower_icon.c` currently emit IR_FAIL stubs (that is why `every`/`to`
   produce nothing). JCON references: `tran/irgen.icn` `ir_a_If` / `ir_a_Every` / `ir_a_ToBy`
   (4-port chunk threading; resume port = β in SCRIP) and `tran/gen_bc.icn` for the templates.
   Use the CONVERSION-METHOD recipe (Lower → Driver → Template → Verify).

3. **B4 / gate strict-0:** move `resolve_call_kinds_descr` classification (the last 4 `->op`
   mutations) into LOWER.

4. Other enum/dead-template cleanup per the prior enum-amputation handoff still applies
   (dead BB templates compiled but op-deleted; IR_OP_COUNT recount).

## NOTE on docs
`.md` references to `src/emitter/BB_templates/` / `XA_templates/` in SCRIP and `.github` were
NOT mass-updated (non-build-critical, historical). Build-critical refs (Makefile, scripts, src)
are all repointed to `src/templates/`.

## PUSH STATUS
Reported by `scripts/handoff_status.sh` — see session transcript for verbatim output.
Note: that script's repo discovery globs `$WS/*/`, which SKIPS the dot-named `.github` repo;
`.github` was pushed and HEAD==origin/main verified MANUALLY this session.
