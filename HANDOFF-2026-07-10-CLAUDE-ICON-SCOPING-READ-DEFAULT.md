# HANDOFF 2026-07-10 s14 — Icon `local`-shadows-global scoping + read/reads null→&input (ipxref truncation killed)

**SCRIP `6c2f043f` · corpus unchanged · .github this commit.**
Full detail lives in the s14 watermark in `GOAL-ICON-BB.md`; this file is the narrative + traps.

## What landed
1. **Scoping (the ipxref root cause):** a procedure `local x` where `x` is also program-global now shadows it, per canonical Icon. `IR_graph_t` +`nlocals/lnames`; `graph_has_local()` consulted at 7 sites (drive VAR/VAR_REF/ASSIGN + gva_k promotion + binop operand slot + BOTH walk_bb_node template routers) and zls ζ-slot collection. Other languages untouched by construction (lnames NULL).
2. **read/reads:** null file → `&input` per `fsys.r` (`by_name_dispatch.c`).

## Traps that cost this session time — do not repeat
- **Drive arms and template routers BOTH derive is_global.** A drive-only fix "works" in debug prints while emitted `.s` still says `IR_ASSIGN global`. Grep every `is_global(` under `src/emitter` when touching name routing; there were seven, not four.
- **`OUTPUT=1` on both sides** of any benchmark diff or `post.icn`'s Init__ replaces `write` with `1` and the run is silent.
- **Small synthetic repros lie for scoping bugs.** Literal-key probes, verbatim-transplant probes all passed; only the whole program failed. The flip variable was one `global … lin` line. Reduce the real program (delete-and-retest); don't build up from scratch.
- **Debug-strip regexes eat shared lines.** My `getenv("SCRIP_DBG…")` sweep deleted a code-bearing line; build both binaries after any mechanical strip.
- **Strict-vs-official comparator:** official rung suite compares `$(…)`-substituted strings (trailing newlines stripped); a raw `cmp` harness reports 90 "fails" on a tree the suite scores 229/24/36. Diff fail-SETS across a stash bracket, not counts vs prose.

## State of ipxref (the #1 benchmark rung)
Accumulation rows byte-identical to fresh iconx oracle. Remaining diff = **BENCH-F3 bare shape**: `x == !L` / `x == (a|b)` never resumes the RHS generator (repro in watermark). That single gap produces BOTH residual symptom families (resword leak + `"` proc junk via getword's quote-skip). The 2026-07-04 F3 work cracked conjunction/reversible-assign topologies only — read that commit as in-tree precedent, and `refs/jcon-master/tran/irgen.icn` invocation ports first, per the F3 rung protocol.

## Next session, in order
1. BENCH-F3 bare-relop-RHS resume (canonical-first protocol above), then re-score ipxref.
2. geddump / rsg / tgrlink per the s12 blocker map.
3. BUG-2 (true-global α-snapshot staleness, `every G ||:= gen` → `G3`) — direction: wire `op_gva_k1/k2` per-operand GVA reads (unwired `bb_binop_gvar_*` templates show the idiom). Only if a benchmark demands it.
