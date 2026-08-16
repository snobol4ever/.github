# FINDING — TOP-PORTS (s118): hoist RETURN/FRETURN/main_β/γ/ω to the top region — BUILT TWICE, MEASURED BROKEN TWICE, REVERTED CLEAN

**Ask (Lon s118 in-chat):** "Can the code labeled RETURN, FRETURN, main_β, main_γ, and main_ω be also put at the top next to its counterparts?" — i.e., adjacent to `main`/`main_init` after the s116 main-first reorder (`bfca479c`). Note the 2026-08-13 floater law's own comment (emit.cpp ~2635) states the original intent "output once, near main, **main at the bottom**" — s116 moved main to the top and stranded the family; the ask restores the intent.

## Mechanism map (all located and verified this seat; emit.cpp = src/emitter/emit.cpp @ fd8ffbf9)

- **Ports (`main_β/γ/ω`)** emit at `emit_chain`'s tail: β group ~3092 (resume-target scan over `nodes[]`/`betas[]`), γ ~3107, ω ~3119 — a multi-class dispatch (zframe / _blob_wire / cells / CLASS-C-epilogue / glue twins `bb_glue_outer_γ/ω`). For the CLASS-O outer main the arms reduce to: β=`jmp ω`, γ=`exit 0`, ω=`exit 1`.
- **Floaters (`RETURN`/`FRETURN`/`NRETURN`)** are seeded as the graph-root call's FINAL root blocks (~2638–2643, referenced-scan) — deliberately bottom-of-file. `RPO_PUSH` (~2588) excludes them and SUCCEED/FAIL from the body walk.
- **Fall-in is real:** `main_α_body` (define ~2762) falls through the optional GLUE-O enter (~2765, often suppressed via `g_glue_o_sup`) into the first-emitted node — no jmp. Any block inserted there executes at startup.
- **uid stream:** label mint pass (~2787) consumes `g_flat_node_id++` in `nodes[]` order; templates (e.g. `bb_call_fn.cpp:530` `.Lrkfnzd`) consume the SAME stream **at emission time in emission order**. Any early emission shifts every later id (measured: uniform `.Lx`/`.Lrkfnzd` renumber, +2 for the two hoisted glue blocks).
- **⛔ Floaters are not layout-free citizens:** RETURN/FRETURN are `IR_DEFINE ival=1/2` — the SAME values `zd_sr_role` (emit.cpp ~973, ~2111) claims as ZD SAVE_RESTORE roles, and the drive loop mutates per-node staging accumulators (`op_zgpop/op_wpop` etc., ~1008) in emission order.

## What was built (both behind killswitch `SCRIP_TOP_PORTS`, OFF byte-identical — verified on fibonacci)

1. **Full variant:** early CLASS-O port emission before the α defines (gate: `entry_is_own_graph_root && !bare && !flat_jmp_entry && !zframe && !stmt_frame && !lcl_proc && !flat_pat && !flat_gen && !icn_cells && !pl_cells && !body_root && no IR_SUSPEND` — an equivalence proof making β≡`jmp ω`), tail groups gated off with `!_hoist` (moved, not copied), plus emission-order index map putting floaters first (uids untouched) and a one-jmp α_body bridge to `lbls[first_non_floater]`.
2. **Ports-only variant:** same minus the floater reorder/bridge.

**Resulting layout (full variant, fibonacci):** main@4, main_init, pool, main_β@41, main_γ@44, main_ω@49, main_α@53, α_body@54, RETURN@57, statements@81 — exactly the ask.

## Measured failures (witnesses in corpus/benchmarks/snobol4)

- **Full variant:** `fibonacci` m3 rc=0 ✔, but `cap_imm_nret` (NRETURN class) OFF rc=0/3-lines → ON rc=1/0-lines (m3, silent), and m4 links but dies `** Error 22 in statement 0 / Undefined function called` = `rt_ab_undef_fn_stub` (rt.c:511, the LADDER-AB fn_cell initial stub) — the DEFINE activation never bound its fn cell. `cap_imm_nret2` OFF rc=139 (pre-existing) → ON rc=1 (changed failure mode).
- **Ports-only variant:** WORSE — `fibonacci` m3 itself rc=1. So the breakage is not (only) the floater/SR-staging interaction: the early glue emission alone perturbs something the full variant accidentally masked on fib. Two interleaved mechanisms; each probe raised a new question — END-OF-CONTEXT law invoked at ~90%.

## Suspects for the next seat, in order

1. **uid-stream perturbation as semantic, not cosmetic:** something keys on `g_flat_node_id`-derived ids across regions (m3 registration? `dentry_name` NATURAL-LABEL deposits? `.Lrkfnzd` id reuse between driver passes?). The ports-only fib m3 rc=1 with only-glue-early is the cleanest repro for this.
2. **ZD SR-role staging order** (IR_DEFINE ival1/2 floaters mutating accumulators before body) — explains cap_imm_nret under the full variant but NOT ports-only fib.
3. The `g_emit_pos += 7` bookkeeping right after the α define (~2732) — early text emitted before it shifts whatever that 7 compensates.

**Cheapest next experiments:** (a) ports-only + `SCRIP_TOP_PORTS=1` on fib m3 under the s112 monitor to see WHERE it dies; (b) burn two dummy uids at the old tail position when hoisting (keep stream identical) and re-test; (c) grep every consumer of `g_flat_node_id` for cross-region equality assumptions.

## State

emit.cpp reverted (`git checkout`); stock verified: fib m3 rc=0, cap_imm_nret m3 == oracle, fibonacci emission byte-identical to committed artifact. No repo carries any TOP-PORTS code. Exact patch texts live in the s118 transcript.
