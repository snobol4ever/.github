# HANDOFF 2026-06-04 (Opus 4.8) — ICN-SCAN-12 + ICN-SCAN-13a (+ 13b scoped out)

**SCRIP HEAD: `b59c9e6`** (two gated rungs: `84ea1ca` ICN-SCAN-12 → `b59c9e6` ICN-SCAN-13a, individually
gated/committed/pushed; three peer rebase waves absorbed with merged-HEAD re-verification each time — Prolog
PL-GZ-1/1b + **LOWER-SPLIT `d6d93c6`** which extracted lower_prolog.c FROM lower.c, the file both rungs edit;
SNOBOL4 PB-RB `fc10199`/`55ec228`/`2704f2e`; all orthogonal, all clean).
**.github HEAD: `ed2b8e1a`** (ladder + watermark) + this handoff.
**Full detail = the two DONE entries + the 13b DEFERRED entry + Watermark in `GOAL-ICON-BB.md` (single source
of truth).**

## Landed

1. **ICN-SCAN-12 (`84ea1ca`) — `=s` sugar.** Lowerer `TT_MATCH_UNARY` own-case in `lower_value` synthesizes
   `TT_FNC{tab, TT_FNC{match, operand}}` via `ast_node_new`/`ast_push` → `v_det_call`. **Dump byte-identical
   to hand-written `tab(match(s))`** — all downstream machinery (safe-set admission, driver digs, native
   boxes, oracle) exercised identically, zero shape risk. Canonical grounding: `omisc.r` `tabmat` doc string
   literally reads *"=x - tab(match(x))"*. **Rode the rung (baseline-free, SCAN-11 precedent): oracle `match`
   canon fix at BOTH dispatch sites** (`by_name_dispatch.c` ~645 site-1, ~2708 site-2) — `match` no longer
   moves `scan_pos` (fstranl.r: `&pos`-read-only; return = i+*s1). This was the SCAN-3-flagged divergence and
   the hard blocker for ANY `tab(match(…))` composition in m2. Probes: `"hello" ? write(="he")` → `he`
   **m2==m3==m4**; `="x"` fails clean; `{ ="he"; write(tab(0)) }` → `llo`; `=s` var-operand → m2 `he`,
   m3 LOUD `[SMX]`.

2. **ICN-SCAN-13a (`b59c9e6`) — `?:=` EXISTS.** Pre-switch rewrite at `lower_value` entry (lang==ICN ∧
   `AUGOP_SCAN` ∧ TT_VAR lhs): `lhs ?:= rhs` → `lhs := lhs ? rhs`; the desugared TT_ASSIGN flows through the
   existing case, zero behavior change elsewhere. Canonical-equivalent to `ir_a_Scan`'s `"?:="` arm
   (irgen.icn ~102-109) for a plain-variable lhs — assign-before-ScanSwap is observationally identical for a
   simple var. Probes m2: `s ?:= tab(3)` → `he` (the goal probe); `tab(99)` fail keeps `s == "hello"`; combo
   `s ?:= ="he"` → `he` (12+13a composed). m3/m4 EXCISE LOUD, symmetric with the hand-written desugar.

3. **ICN-SCAN-13b SCOPED OUT → the `bb_var` tier** (recorded in the ladder with the full design). Two
   blockers, both the standing bb_var operand-slot gap, NOT scan machinery: (a) `icn_scan_subgraph_safe`
   rejects every non-`&` `IR_VAR` → any var-subject scan declines, and the desugared `?:=` always has a var
   subject; (b) admission's `IR_ASSIGN` arm: local/varslot store box not built (only NV-global
   `bb_gvar_assign_icn`). The scan-side piece is SMALL and written up: in `flat_drive_gen_scan`, adopt the
   body-terminal slot as the GEN_SCAN node's value (`descr_chain_terminal(body_sg->entry)` + `bb_slot_get`,
   the exact subject pattern at emit_bb.c ~1208-1210; slotmap-alias or 16B copy into `bb_slot_alloc16(pBB)`
   at `body_done` before the LEAVE-γ glue) → GEN_SCAN becomes an arity-0 slot producer.

## Bug found and fixed

**The oracle has TWO icon scan-builtin dispatch sites and only site-2 is live.** Fixing site-1 `match`
(~645) changed nothing observable; the live path is the icon-flavor block at ~2618+ (site-2, ~2708 for
match). Diagnostic that exposed it: split probe `x := match("he"); write(x); write(tab(x))` printed `3` then
EMPTY — match's return was right but its `scan_pos += nl` side effect made the subsequent `tab` span 3→3.
Both sites now canon (site-1 fix kept as hygiene; site-1 is dead anyway — see flags).

## Key transferable findings

- **AST-synthesis desugar is the zero-risk rewrite pattern**: build the exact parser shape with
  `ast_node_new`/`ast_push` (in-file precedent at lower.c ~374/~1105), route through the existing lowering
  fn, then PROVE byte-identical `--dump-bb` against the hand-written form. Both rungs gated on that parity.
- **Pre-switch rewrite at `lower_value` entry** is the clean hook for augop-style desugars — the rewritten
  node falls into the normal case, nothing else moves. This is the template for the TT_AUGOP family rung.
- **Probe in corpus layout**: the mini Icon parser needs `;` statement terminators and `local` decls
  (corpus rung05 style); bare multi-statement bodies parse-error misleadingly.
- Corpus `=s`/`?:=` usage is confined to the rung36 jcon megas (9 files), all multi-blocked → construct-level
  probes are the rung evidence; zero set-diff is the expected gate result for these two rungs.

## Flags for Lon

1. **Icon `TT_AUGOP` family is otherwise UNCONSUMED** — `x +:= 2` falls into the TT_FNC group, misroutes to
   `v_det_call("x")`, silently no-ops (prints `1`). Pre-existing, now load-bearing knowledge. Wants one
   desugar rung (Rebus precedent `rebus_lower.c` TT_AUGOP arm; the 13a pre-switch hook is the place).
2. **`scan_try_call_builtin` (by_name_dispatch.c:531, site-1) has ZERO call sites** (only two header decls)
   — dead-code deletion candidate, incl. its divergent tab `newp < scan_pos` no-backward arm.
3. Carried from SCAN-7-11: oracle scan-fn GENERATIVITY decision still pending (m2 one-shot vs canonical
   `function{*}`; shifts the 129 baseline).

## Gates (held at EVERY rung)

Corpus ALL THREE columns byte-identical set-diff at each rung vs session-start baseline: **m2 129 HARD /
m3 18 PASS+147E / m4 25 PASS+86E — zero PASS-set drift any mode any rung**. Smokes Icon m2 12/12 HARD ·
Prolog m2 5/5 HARD (m3 2/0/3E is the peer PL-GZ-1b re-baseline; m4 5/5) · broker 32. Structural green:
bb_bin_t=0 · no-handencoded `--strict` 0 · g_vstack 3 (standing) · no-stack 10≤127 · one-reg-frame 0≤21 ·
prove_lower2 PASS · FACT (bytes outside templates) 0.

## NEXT — Lon's call between:

- **ICN-SCAN-FENCE** — gate script `scripts/test_gate_icn_scan.sh` + scan-bucket sweep ((a) nine kinds off
  the stub list — ALREADY TRUE; (b) probe battery m2==m3==m4, 13b clause deferred; (c) the 27
  IR_GEN_SCAN-gated programs' EXCISED→PASS deltas recorded; (d) standing gates). Closes the ladder modulo 13b.
- **The `bb_var` tier** — one stroke unblocks 13b, var-subject scans, and the relop/`if_expr`/`while`/`until`
  tiers (the watermark's standing largest-blocker). Higher value, bigger slice.

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
# canonical sources (CONSULT-CANONICAL-SOURCES):
git clone https://github.com/proebsting/jcon refs/jcon-master
git clone https://github.com/gtownsend/icon refs/icon-master
bash scripts/test_smoke_icon.sh       # m2 12/12 HARD
bash scripts/test_icon_rung_suite.sh  # m2 129 HARD / m3 18+147E / m4 25+86E
# then: GOAL-ICON-BB.md → Watermark → NEXT (SCAN-FENCE or bb_var tier per Lon)
```
