# HANDOFF — 2026-06-29 — Sonnet 4.6 — GZ#5 R1 (Icon off legacy fat driver) + mode-4 text path restored

## SCRIP HEAD: `4d31aff0` (R1) + one follow-up commit (mode-4 restore) — pushed to origin/main
## .github HEAD: this doc + GOAL-IR-IMMUTABLE-EMIT.md watermark — pushed

---

## Session arc

Orientation → measurement → two landed rungs, both verified on the full pass set.

### 0 — Measurement (grounded the stale "87")
The Icon corpus has grown. Under `SCRIP_ICN_BB=1 --run` with a multiline-safe expected-comparison,
**162** programs pass (the "87" in prior handoffs was the official rung-suite snapshot at an older commit).
`--dump-ir` over all 162 → **16 distinct LOWER-produced ops**:
`IR_LIT_{S,I,F}`, `IR_VAR`, `IR_KEYWORD`, `IR_BINOP`, `IR_NOT`, `IR_ASSIGN`, `IR_CALL`, `IR_TO`, `IR_EVERY`,
`IR_CONJ`, `IR_IF`, `IR_SUCCEED`, `IR_FAIL`, `IR_RETURN`.
The emit-time resolver `resolve_call_kinds_descr` (emit_bb.c:1071-1074) fans `IR_CALL` →
`IR_CALL_BUILTIN` / `IR_CALL_PROC_STAGED` / `IR_PROC_GEN`, so **19 ops are actually dispatched** out of
**222** defined in `IR.h`.

**Enum-amputation gating (the decision-relevant fact):** deleting `IR.h` to the 19-op floor breaks
**159 enum members** still bare-referenced across the live build —
- `emit_bb.c` = 115 (SNOBOL pattern + Prolog `gz_*`/`pl_gz_*` clusters)
- `scrip.c` = 70 (`pl_gz_*` subsystem)
- `opt/ir_query.c` = 40
- `lower_icon.c` = 36 (Icon lower still emitting ops `emit_drive` doesn't own: IF/WHILE/EVERY/ALT/SCAN/SUSPEND)
- templates + misc ≈ 38.
So the amputation cannot be done by editing `IR.h` first — it is GATED on removing the non-Icon emitter code
(R2/R3). After that, the delete falls out as a ~36-site Icon-only edit. (This re-confirms the prior
enum-amputation handoff's dependency analysis with current numbers.)

### 1 — R1: Icon dispatch flipped off the legacy `bb_build_flat` path (`4d31aff0`)
`ring_to_tree` (scrip.c, the stack-reconstruction reconstructor) returns NULL for any chain containing a
literal or binop (scrip.c:75) — i.e. every real program — so all 162 already flowed through
`descr_flat_chain_build` → `emit_drive`. The `root_node != NULL` branch only reached the GROUND-ZERO abort
stubs `bb_build_flat` (emit_bb.c:1130) / `codegen_flat_build` (emit_bb.c:1131).
Proved dead empirically: instrumented the branch with a stderr marker, rebuilt, ran all 162 → **0 hits**.
Then made the flip explicit on BOTH the mode-3 (`--run`) and mode-4 (`--compile`) dispatches (unconditional
`descr_flat_chain_build`), and deleted the now-dead `ring_to_tree` + its sole helper `node_arity` (43 lines).
This severs Icon from `walk_bb_flat` / `bb_build_flat` / `codegen_flat_build` — the **R2 prerequisite**.

### 2 — Mode-4 text path RESTORED (0 → 161/162)
Per Lon's directive that both modes work on the pass set. Mode-4 was at **0/162** — it aborted on the first
call for every program because the GROUND-ZERO reduction `a7958465` had DELETED the entire mode-4 text-emit
path and replaced it with abort stubs. (The "mode-4 green" claim was from `6058d6f8`, before that reduction.)

Restoration was small, because **the text path reuses the mode-3 driver**: `descr_flat_chain_build_text`
calls the same medium-agnostic `codegen_flat_chain_body` → `emit_drive` loop. Restored five thin wrappers to
their pre-reduction bodies + re-added one deleted helper:
- `g_bb_alpha_seq_reset` (trivial counter reset)
- `descr_flat_chain_build_text` (main builder)
- `descr_flat_chain_build_proc_text` (proc builder)
- `data_buf_reset` + `data_buf_flush_pending_label` (text data-block state)
- `data_buf_appendf` (re-added; was deleted, `static`, caller of the above)

No new driver logic. The SNOBOL-only `pre_build_children_text` stays stubbed (the Icon chain body never calls
it — confirmed). Then the `.so` link gap surfaced: `libscrip_rt.so` had 4 undefined non-Icon symbols
(`prolog_lower`, `rebus_compile`, `bb_gather_prepare`, `bb_mapgrep_prepare`) from the Icon-only Makefile trim
(non-Icon TUs pulled from the `.so` source list `RT_PIC_SRCS`).

**KEY GOTCHA (recorded so it isn't re-hit):** a first attempt stubbed those 4 in the SHARED
`src/lower/lower_noicon_stubs.c` — which **multiply-defined** in the `scrip` binary build, because that
recipe DOES compile the real `prolog_lower.c` / `rebus_lower.c` / `bb_gather.cpp` / `bb_mapgrep.cpp`. Reverted.
The fix is a SEPARATE TU `src/lower/rt_noicon_stubs.c` added to **`RT_PIC_SRCS` ONLY** (the `.so` source
list), never the `scrip` binary recipe. Two build configs with different TU sets — stub only in the one that
lacks the real definitions.

The sole mode-4 holdout is `corpus/programs/icon/parser/cset_lit.icn` (`x := 'aeiou'`) — a PRE-EXISTING
cset-literal segfault that hits `--dump-ir` and `--compile` even on the R1-only tree (verified by stash +
rebuild + retest); it passes mode-3 `--run`. Not introduced this session. A cset-lit lowering/codegen bug =
its own future rung (relates to Track C / `IR_CSET_LIT`).

---

## Verification (all measured, all on the full pass set)
- **mode-3 `--run`: 162/162** — zero regression vs baseline (re-verified AFTER the emit_bb.c edits AND after
  the rt-stub relocation).
- **mode-4 `--compile` → as → ld → run: 161/162** — 0 assemble-fails, 0 run-fails, 0 output-mismatches; the 1
  fail is the pre-existing cset_lit compile segfault.
- Both gate programs full mode-4 cycle: `write("hello world")` → `hello world`, `write(1+2)` → `3`.
- **Mutation gate unchanged: HARD=4** (the 4 `->op` writes still in `resolve_call_kinds_descr`; that's B4).

## Files touched
- `src/driver/scrip.c` — R1 flip + delete `ring_to_tree`/`node_arity` (in commit `4d31aff0`).
- `src/emitter/emit_bb.c` — restore 5 text-path wrappers + `data_buf_appendf`.
- `src/lower/rt_noicon_stubs.c` — NEW; 4 `.so`-only stubs.
- `Makefile` — add `rt_noicon_stubs.c` to `RT_PIC_SRCS` (only).
- `.github/GOAL-IR-IMMUTABLE-EMIT.md` — watermark.

## Build / verify recipe (sandbox)
```
apt-get install -y libgc-dev
make -s scrip && make -s libscrip_rt
# mode-3: SCRIP_ICN_BB=1 ./scrip --run file.icn
# mode-4: SCRIP_ICN_BB=1 ./scrip --compile --target=x86 file.icn > f.s
#         gcc -no-pie -x assembler f.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out -o f.bin && ./f.bin
```
Sandbox tooling left behind: `/tmp/passers.txt` (the 162), `/tmp/reverify.sh` (mode-3 sweep),
`/tmp/mode4_sweep.sh` (mode-4 full-cycle sweep), `/tmp/find_passers.sh`, `/tmp/collect_ops.sh`.

## NEXT (dependency order — the enum amputation is the goal, R2/R3 unblock it)
1. **R2** — remove the now-dead SNOBOL pattern cluster + `walk_bb_flat`/`bb_build_flat`/`codegen_flat_build`
   + Prolog `gz_*`/`pl_gz_*` from `emit_bb.c` (the 115 break-refs). Build green, both modes hold.
2. **R3** — remove the `pl_gz_*` subsystem from `scrip.c` (~699 lines, interleaved with `main()`; the 70
   break-refs).
3. **R4** — trim `lower_icon.c` of emission for ops `emit_drive` doesn't own (the 36 break-refs), OR grow
   `emit_drive` to own them (IF/WHILE/EVERY/TO_BY/SUSPEND — JCON `ir_a_If`/`ir_a_Every`/`ir_a_ToBy`).
4. **R5** — delete the now-unreferenced enums from `IR.h` + `kind_names[]`/`bb_op_name`/
   `ir_node_produces_value` (lockstep). Target the 19 dispatched + whatever R4 hasn't freed.
5. Then the `rt_noicon_stubs.c` + `lower_noicon_stubs.c` TUs delete once their non-Icon callers are gone.
6. `cset_lit` segfault (Track C `IR_CSET_LIT`) — independent.
7. B4 / gate strict-0 — move `resolve_call_kinds_descr` classification into LOWER (the last 4 mutations).

## PUSH STATUS
Reported by `scripts/handoff_status.sh` — see session transcript for the verbatim output.
