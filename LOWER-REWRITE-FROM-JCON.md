# LOWER REWRITE FROM JCON irgen.icn — DO THIS, NOT INCREMENTAL PATCHING

**Lon has asked for this THREE TIMES. Stop misreading it as incremental migration.**

## What this is

A wholesale rewrite of `src/lower/lower_icn.c` (and the operand-recursion patterns
in `src/lower/bb_exec.c`) by **transcribing JCON's `irgen.icn` procedures directly
into C**, one `ir_a_*` procedure at a time. Every `ir_a_*` in irgen.icn is the
authoritative spec for that construct's 4-port wiring. Do NOT invent. Do NOT
incrementally patch the existing `lower_icn_expr_node` switch tree.

JCON is at `/home/claude/jcon-master/tran/irgen.icn` (clone from the user's
upload, or fetch from JCON master). 1559 lines.

## What this is NOT

- NOT a family-by-family migration of the existing code.
- NOT bit-flag discriminators in `nd->ival`.
- NOT "deep-threaded mode coexisting with legacy mode."
- NOT preserving `lower_icn_expr_node` and bolting threading on top.

If you find yourself adding a discriminator flag, a "is_deep" check, or a
"fallback to legacy path" branch — **STOP**. That is the wrong lane. Re-read
this file.

## How to do it

1. **Read `irgen.icn` cover-to-cover before writing any C.** Especially:
   `ir_init`, `ir_a_NoOp`, `ir_a_Compound`, `ir_a_ProcBody`, `ir_a_Binop`,
   `ir_binary`, `ir_a_Call`, `ir_a_If`, `ir_a_Every`, `ir_a_Alt`, `ir_a_ToBy`,
   `ir_conjunction`, `ir_a_Field`, `ir_a_Scan`, `ir_a_Limitation`, `ir_a_Not`,
   `ir_a_Case`, `ir_a_Repeat`, `ir_a_Return`, `ir_a_Suspend`, `ir_a_Until`,
   `ir_a_While`, `ir_a_Create`, `ir_a_Ident`, `ir_a_Next`, `ir_a_Break`,
   `ir_a_Mutual`, `ir_a_Key`, `ir_a_ListConstructor`.

2. **Each `ir_a_*` translates to a SCRIP builder function** that returns:
   - α_out (entry into the construct's subgraph)
   - β_out (retry entry — `nd` itself for resumable kinds, ω_in for bounded)
   - synthesizes γ/ω as ports on the constructed apply node

3. **Operand subgraphs are built as PEERS in cfg->all[]**. The apply node is
   reached via the control-flow port chain (e.g. for binop: left.γ → right.α →
   right.γ → apply node). Operand values are read from the sidecar (PEERS RULE,
   HQ Invariant 17, already in place — see BB.h, scrip_ir.c, bb_exec.c).

4. **The existing `lower_icn_expr_node` mega-switch is REPLACED, not edited.**
   Build the new `lower_icn.c` in a new file, validate, then swap.

## Pre-existing infrastructure (already in place — DO USE)

- **PEERS RULE** in `src/include/BB.h` (HQ Invariant 17): BB_t is lean; operand
  references live in `BB_graph_t.operand_aux` sidecar keyed by BB_t*.
- **API**: `bb_operand_aux_set(cfg, nd, src, n)` / `bb_operand_aux_get(cfg, nd, &n)`
  in `src/lower/scrip_ir.c`.
- **`g_current_cfg`** module-static in `bb_exec.c` (save/restore around recursive
  `bb_exec_once` calls) so sidecar lookups work from anywhere.
- **`bb_exec_once`** outer driver is ALREADY a port-follower:
  `while (cur) cur = bb_exec_node(cur);`. Just stop the operand-recursion
  inside composite cases.
- **ICN-Z-0/Z-1/Z-2b** (in `lower_icn.c`): leaf-threading and proc-body
  statement chaining. Use as a model for the new builders.

## Anti-patterns committed in 2026-05-27 Opus session (DO NOT REPEAT)

- `nd->ival = 1` as "deep-threaded" flag (BB_ASSIGN, commits 8470259b / b8c25cd3).
- `nd->ival |= (1LL << 31)` as "deep-threaded" flag (BB_CALL, commit 4535363d /
  b8c25cd3).
- "Legacy mode" fallback in `bb_exec.c` apply cases.

These exist in HEAD because the migration was done family-by-family with
discriminator flags. The clean rewrite REMOVES them — every apply case
reads ONLY from the sidecar; no legacy α/β operand storage; no flags.

## Sanity check before starting

If you are about to write `if (e->t == TT_ASSIGN ... )` as the FIRST thing
in the rewrite, you are doing it wrong. The FIRST thing is a top-level
recursive lowerer that mirrors `irgen.icn`'s `ir(p, st, inuse, target, bounded, rval)`
dispatcher, with each construct's lowerer being a faithful C transcription of
its `ir_a_*` procedure.

## Why this matters

Lon directed us to JCON's irgen.icn specifically because that file IS the
specification. Every chunk emission in `ir_a_Binop` corresponds to an edge in
the BB graph. Every `ir_Goto(L)` is a port assignment. Every `ir_opfn(target,
op, [args], failLabel)` is an apply-node specification. The mapping is
mechanical IF you transcribe instead of inventing.

Patching the existing `lower_icn_expr_node` does NOT yield this. It yields
incremental progress that never converges to the JCON shape. That's why
the previous incremental attempts kept hitting "discriminator bit" smells —
the substrate is wrong.

## Acceptance

1. New `lower_icn.c` (or `lower_icn_new.c` then swap) is structured procedure-
   by-procedure, mirroring `irgen.icn`.
2. Zero discriminator flags in `nd->ival` for "deep-threaded" mode.
3. Zero `bb_exec_node(nd->α)` or `bb_exec_node(nd->β)` operand recursions in
   composite cases (BINOP, CALL, ASSIGN, IF, CONJ, ALT, EVERY, TO, TO_BY,
   BINOP_GEN). `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c` returns
   only legitimate non-operand uses.
4. `icn_kind_owns_omega_operand` deleted (no kind owns ω as an operand).
5. Gates: smoke_icon 5/5, smoke_prolog 5/5, icon_all_rungs PASS ≥ 198,
   FACT RULE grep == 0.

## Last words

If you are tempted to "do this incrementally in the existing file as a first
step," resist. That has been tried, three times. It does not converge.
Open a new file. Transcribe `irgen.icn`. THAT is the BIG SHOT.
