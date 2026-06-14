# HANDOFF-2026-06-13-SONNET-RAKU-BB-MAPGREP-31-31.md

## Session: GOAL-RAKU-BB — GROUP A closed; Raku m3/m4 now 31/31 (parity with m2)

**SCRIP HEAD at open: `a6f9d65`. At close: `63fec78`** (1 commit landed, rebased cleanly over peer
`763938b`). `.github` updated (this doc + watermark).

**Gates at close — Raku m2 31/31 (HARD ✓); m3 31 PASS / 0 FAIL / 0 EXCISED; m4 31 PASS / 0 FAIL / 0
EXCISED.** The 31/31 target set by Lon's 2026-06-12 pivot is HIT. Peers invariant: Icon m2/m3/m4 = 12/12/12,
SNOBOL4 m4 7/7 (HARD ✓), NFA oracle 5/5. `no_bb_bin_t` gate = 0. New files add zero value-stack references.

---

## LANDED — commit `63fec78`: GROUP A (gather_take / map_range / grep_range / map_over_gather / grep_over_gather)

The prior watermark deferred GROUP A as "blocked on Icon GZ-7." That was not the real blocker. Two distinct
gaps, both closed this session.

### Part 1 — GATHER was a latent indexed-load bug (NOT GZ-7)

`bb_gather.cpp` emitted `mov rsi, rdx` — loading the **base address** of the baked takes array — instead of
`mov rsi, [rdx + rcx*8]` (the element at cursor `rcx`). Symptom: `gather_take` m3/m4 printed the array
pointer three times (`7855648`) instead of `10 20 30`. ROOT CAUSE: the 4-arg call
`x86("mov","rsi","rdx","rcx")` parses `a="rsi"(REG)`, `b="rdx"(REG)`; the `mov` dispatch reads only operands
a,b → emits `mov rsi, rdx` and **silently drops** the 4th arg `"rcx"`. The encoder DOES support scaled-index
loads, but only when the SECOND operand is the string form `"[rdx + rcx*8]"` (parsed to `XK_MEMIDX8` →
`x86_load_indexed8` → SIB byte `48 8B 34 CA`). FIX: one line in `bb_gather.cpp` —
`x86("mov","rsi","[rdx + rcx*8]")`. (The SIB encoder is correct for low registers; rsi/rdx/rcx need no REX
extension.) This bug had masked GATHER the whole time; the gate had never let it through to be observed.

### Part 2 — MAP/GREP: new `bb_rk_mapgrep.cpp` via compile-time materialization of pure generators

`IR_MAP`/`IR_GREP` carry the body sub-graph in `IR_LIT(nd).ival` and the source sub-graph in
`IR_EXEC(nd).counter` (both full `IR_graph_t*`). All 5 GROUP A tests have PURE source+body (ranges,
literal-take gathers, arithmetic/comparison on `$_` — no side effects, no external input). The new template's
**prepare** function drives those sub-graphs through the m2 interpreter **at emit time** — this is
constant-folding of pure generators (legitimate: the emitter runs before `ir_delete_all`, IR is live), NOT
runtime IR walking (m3/m4 run paths never touch IR). It bakes the resulting integer sequence as RO data and
emits the identical cursor-walk GATHER uses. Mechanism mirrors the m2 MAP/GREP handler
(`NV_SET("_",v)`; drive body; MAP keeps body output, GREP keeps source value when body ≠ FAIL).

**This is NOT the generator PUMP** the prior handoffs scoped as "the real work." It is a narrower, sound
solution for pure generators. The PUMP (emit source+body as native blobs invoked per element) remains the
answer for any future side-effecting or string/non-integer map/grep — that machinery is shared with RK-GRAM-3.

### Wiring (the part the prior excise-analysis missed)

The flat-chain walker `walk_bb_flat` (`emit_bb.c`) is a SEPARATE dispatch from `walk_bb_node` (`emit_core.c`).
GATHER was special-cased in BOTH; MAP/GREP needed the same in both plus the chain-traversal helpers:
- `src/driver/scrip.c`: `icn_rhs_kind_ok` + `icn_assign_safe_kind` admit IR_GATHER/IR_MAP/IR_GREP (the EXCISE
  gate rejected the loop-variable ASSIGN whose γ-producer is the generator). (`icn_kind_native_stub` is DEAD
  code — defined, never called — so its MAP/GREP entries were irrelevant; left as-is.)
- `src/emitter/emit_core.c` `walk_bb_node`: `case IR_MAP: case IR_GREP: bb_prepare(nd); bb_emit_x86(bb_rk_mapgrep());`
- `src/emitter/emit_bb.c`:
  - `bb_prepare`: MAP/GREP → `bb_rk_mapgrep_prepare(nd)`.
  - `walk_bb_flat` switch: `case IR_MAP: case IR_GREP: FILL(...)` (FILL routes to `walk_bb_node`).
  - `codegen_flat_chain_body` queue builder + `descr_chain_operand_refs`: follow MAP/GREP `ω.node` (else the
    post-loop chain — the `say('done')` tail — is never enqueued → empty output past the loop).
  - `ir_is_generator_kind` + `gen_bb_is_gen_arg`: add MAP/GREP. **Critical** — this is what makes the loop
    body's back-edge resolve to the generator's β (resume) label instead of α (restart). Without it the loop
    re-enters MAP at α every iteration and never advances.
  - `descr_chain_arity`: MAP/GREP return 0 (leaf value-producers; sub-graphs hidden in ival/counter).
- `src/emitter/BB_templates/bb_templates.h`: declare `bb_rk_mapgrep()`.
- `Makefile`: `bb_rk_mapgrep.cpp` added to `RT_PIC_SRCS` (libscrip_rt) + a compile rule in the `scrip` target
  (picked up by the `$(OBJ)/*.o` link).

### Files touched (committed `63fec78`)
- `src/driver/scrip.c`, `src/emitter/emit_core.c`, `src/emitter/emit_bb.c`,
  `src/emitter/BB_templates/bb_gather.cpp`, `src/emitter/BB_templates/bb_rk_mapgrep.cpp` (NEW),
  `src/emitter/BB_templates/bb_templates.h`, `Makefile`.

### Compliance
No `bb_bin_t`, no `bb_emit_asm_result`, no `.size()` patch offset, no language guards in the template
(dispatch is on IR kind/shape only), no AST walking on run paths, no value stack. The single `IF(MEDIUM_TEXT,…)`
in `bb_rk_mapgrep.cpp` is the SAME data-section carve-out `bb_gather.cpp` already uses (`.rodata` directives
can only exist in TEXT; in BINARY the baked array lives at an absolute pointer referenced by `lea`). The
medium-invisible `--strict` gate's REMAINING list (`bb_is_cmp`, `bb_list`, `bb_resolve`) is the pre-existing
WIP baseline — neither `bb_gather` nor `bb_rk_mapgrep` appears in it.

---

## PRE-EXISTING BASELINES (verified NOT introduced — do not chase)
- `audit_concurrency_invariants.sh` VIOLATIONs (FACT-RULE md5 drift + stale `src/lower/lower.c` path) — same
  as prior sessions.
- value-stack gate "TOTAL 3" — 1 in `rt.h` + pre-existing; the new files add 0.
- `prove_lower.sh` "0 cases — DEAD GATE", `util_template_purity_audit.sh` 1 site in `bb_call_write_slot.cpp`
  (SNOBOL4/Icon box), SNOBOL4 `define` corpus m3/m4 6/1 — all pre-existing per prior handoffs.

---

## Session Setup
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh      # m2 31/31 HARD; m3 31/0/0; m4 31/0/0
bash scripts/test_smoke_icon.sh      # 12/12/12 HARD
bash scripts/test_smoke_snobol4.sh   # m4 7/7 HARD
bash scripts/test_gate_raku_nfa_oracle.sh   # 5/5
```

## ORDER OF WORK for next session
1. **RK-GRAM-3 (THE SEAM)** — subrule `<name>` backtracking via the generator PUMP; resume-and-yield-next
   across the subrule call boundary; Match-tree build. Routes through IR_* SUSPEND/ALT/PUMP.
2. (Only if a new test demands it) the real non-materialized map/grep PUMP — emit source+body as native
   per-element blobs; shares RK-GRAM-3's PUMP machinery.

## Commit this session (pushed + verified on origin/main)
| Commit | Repo | What |
|---|---|---|
| `63fec78` | SCRIP | Raku map/grep/gather m3+m4 — GROUP A closed, m3/m4 31/31 |
