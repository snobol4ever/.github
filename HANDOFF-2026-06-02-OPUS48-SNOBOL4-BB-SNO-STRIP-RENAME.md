# HANDOFF — SNOBOL4 BB: strip SNO/sno from runtime fns + BB templates (language-independent naming)

**Author:** Opus 4.8 (third developer). **Date:** 2026-06-02. **Repo tips after this session:**
SCRIP `origin/main` = `703eb83` (rebased onto peer `06826c8` PL-RV-5 bb_unify); `.github` = the commit
carrying this file.

PIVOT directive (Lon, this session): the SCRIP **runtime is language-independent** — it offers all
features so every frontend can implement on it. Tagging runtime functions / BB templates with `sno`
falsely implies single-language ownership. Strip `SNO`/`sno` from runtime functions and from BB template
names, variables, functions, and filenames; use the proper (language-independent) concept instead.

## 1. What landed (SCRIP `703eb83`) — RENAME-ONLY (84 ins / 84 del, symmetric; behavior unchanged)

Mapped each symbol to the codebase's EXISTING language-independent vocabulary (not invented names):

**Name-value subsystem** (the global associative variable store — matches the existing
`rt_nv_get`/`rt_nv_set`/`NV_SET_fn`/`NV_GET_fn` vocab; this is precisely what distinguishes it from
Icon's frame-slot `bb_assign`, which was LEFT untouched):
- `rt_sno_assign_lit_s` → `rt_nv_assign_str`
- `rt_sno_assign_int`   → `rt_nv_assign_int`
- `rt_sno_assign_var`   → `rt_nv_assign_var`
- `rt_sno_assign_concat`→ `rt_nv_assign_concat`  (this one is DEFINED in `src/lower/bb_exec.c`, not rt.c)
- `bb_sno_assign*`       → `bb_nv_assign*`  (incl. `_str`/`_var`/`_concat` suffixes)
- `flat_drive_sno_assign*` → `flat_drive_nv_assign*`  (incl. `_binop`)
- `g_sno_flat_chain`    → `g_nv_flat_chain`
- file `bb_sno_assign.cpp` → `bb_nv_assign.cpp`

**Pattern-matching subsystem** (subject / scan / match = shared SNOBOL+Icon scanning vocabulary):
- `rt_sno_subject_load` → `rt_subject_load`
- `rt_sno_match_lit`    → `rt_match_lit`
- `rt_sno_exec_scan`    → `rt_scan_exec`   (defined in `bb_exec.c`)
- `bb_sno_subject`      → `bb_subject`
- `bb_sno_scan`         → `bb_scan_stmt`   (**`bb_scan` is taken** — it's a `BrokerMode` enum in `bb_box.h`)
- `flat_drive_sno_subject`       → `flat_drive_subject`
- `flat_drive_sno_scan`          → `flat_drive_scan_stmt`
- `flat_drive_sno_ref_invariant` → `flat_drive_ref_invariant`
- `flat_drive_sno_program`       → `flat_drive_program`
- `g_sno_subject*` (slot + dbg_base/len) → `g_subject*`
- files `bb_sno_scan.cpp` → `bb_scan_stmt.cpp`, `bb_sno_subject.cpp` → `bb_subject.cpp`

**Build/aux updated:** `Makefile` source-list (113–115) + per-object compile rules (316–318) + the `.o`
object names; `scripts/audit_concurrency_invariants.sh` comment. 3 files tracked as `git mv`.

## 2. Deliberately LEFT (out of the stated scope — flagged for Lon's decision)
- **`IR_SNO_PROG`** — an IR node-kind enum (the SNOBOL program node), not a runtime fn or BB template.
  Its *handler* `flat_drive_sno_program` WAS renamed (`→ flat_drive_program`).
- **`src/lower/bb_exec.c` mode-2 statics** — `g_sno_save` / `g_sno_save_top` / `g_sno_cur_func` +
  `SnoSaveEnt` / `SNO_SAVE_MAX` (a SNOBOL dynamic-scoping save-stack inside the *mode-2 interpreter*,
  which is neither a runtime fn nor a BB template, and is being phased out). The repo-wide sanity grep
  also surfaced a broad `SNO_*` / `Sno*` family (`SNO_ABORT_*`, `SNO_RETURN_*`, `SnoEvalCtx`, `SnoRuntime`,
  `SnoLine`, `g_sno_err_active`, `Snocone*`, …) — these live in the SNOBOL4/Snocone *frontend + mode-2
  runtime*, again outside "runtime fns + BB templates." **If Lon wants a deeper sweep (mode-2 + frontend),
  that's a follow-on `grand-master-reorg`-class pass; not done here.**
- Historical session blocks / HANDOFF prose mentioning the old names were NOT rewritten (rewriting the
  work-log history would be wrong); only live CURRENT-PRIORITY / NEXT references were updated.

## 3. Verification (all GREEN on the merged tree, before push)
- Repo-wide grep (all `.c/.cpp/.h/.sh/.py/Makefile`): **zero** orphaned references to any renamed symbol.
- `make scrip` + `make libscrip_rt` rebuild clean (no undefined symbols) — incl. after rebasing onto the
  concurrent peer commit `06826c8`, which introduced no orphaned old-name refs.
- Diff proven **rename-only** (strip the identifier substitutions + file-path lines → empty residue).
  Therefore every gate result equals the pre-change baseline by construction.
- Mode-3 spot checks preserved: `OUTPUT = "hello"` → `hello`; `S='hi'; OUTPUT = S` → `hi`.
- Gates: `test_gate_no_bb_bin_t` 0 · `test_gate_sm_dead` 0 · `audit_concurrency_invariants` rc=0
  (FACT-RULE byte-identical-×3 unperturbed — rename touched no encoder-byte logic) · `prove_lower2`
  firewall OK. Byte-identity (3 fails halt_after_arith/loop/match) + medium-invisible (61, mostly
  `bb_call.cpp` 60 + `bb_unop` 1) are the PRE-EXISTING WIP baseline (unrelated to the rename; `bb_call.cpp`
  was not touched).

## 4. NEXT (SNOBOL4) — `OUTPUT = 2 + 3` end-to-end in mode-3 (investigated this session, NOT yet coded)
Investigation found the runtime side already exists: **`rt_nv_assign_int(name, int64_t)`** (rt.c, formerly
`rt_sno_assign_int`) builds a `DT_I` DESCR and hits the OUTPUT hook. Path trace for `OUTPUT = 2 + 3`:
`IR_ASSIGN(OUTPUT, IR_BINOP(ADD,2,3))` → `flat_drive_nv_assign_binop` (NOT `g_icn_flat_chain`) → walks the
binop → `flat_drive_binop_tree` GZ-3 short-circuit (both `IR_LIT_I`) → `EMIT_PAIR_FILL(binop)` → `bb_binop`
router → relop/arith/concat arms ALL gated on `g_icn_flat_chain` → none fire → **BOMB #1** (before
`bb_nv_assign` is even reached).

Two fixes, byte-verify-vs-`as` discipline required (this is the part I stopped short of, on context budget):
1. **A name-value integer-arith arm in `bb_binop`** gated on `g_nv_flat_chain` (separate file
   `bb_binop_nv_arith.cpp` preferred, per one-box-one-file — OPEN: confirm structure with Lon). SNOBOL's
   `rt_nv_assign_int` takes a RAW int64 (not Icon's 16-byte DESCR) → bake both literals self-contained and
   write only an **8-byte** result slot (`bb_slot_claim(8)`), sidestepping Icon's operand-promotion. Mirror
   the `opb` switch in `bb_binop_arith.cpp:38` for ADD/SUB/MUL/DIV/MOD.
2. **`bb_nv_assign` int-binop arm** (currently a documented bomb): load the binop's int64 result from its
   ζ-slot into `rsi`, dst-name ptr into `rdi`, `call rt_nv_assign_int`, ports. Needs the binop's slot offset
   promoted onto `_`: add `int op_a_slot;` to `sm_emit_t` (`emit_globals.h`) + set
   `g_emit.op_a_slot = nd->α ? bb_slot_get(nd->α) : -1;` in the `walk_bb_node` prologue (`emit_core.c`,
   parallel to `op_a_sval`). Timing OK: `flat_drive_nv_assign_binop` walks/emits the binop FIRST, then FILLs
   the assign, so `bb_slot_get(nd->α)` resolves at FILL time.

Encoders confirmed present in `x86_asm.h`: `FRQ(off)` load/store64, `x86_movimm`, the arith opb, `x86_load_ro`,
`x86_call_ro`, ports, `bb_slot_claim`. After: `OUTPUT = 2 + 3` → `5`; then `bb_subject` + `bb_match` together
(the `pattern` smoke), then `bb_capture`/`bb_arbno`.

**Method note:** mode-3 `--run` runs the EMITTER inside the `scrip` driver — after editing a template you MUST
`make scrip` (not only `make libscrip_rt`). emit_core.c/emit_bb.c compile into BOTH → rebuild both.
SPITBOL source format: statements TAB-indented (col-0 = label): `printf '\tOUTPUT = 2 + 3\n\tEND\n'`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
