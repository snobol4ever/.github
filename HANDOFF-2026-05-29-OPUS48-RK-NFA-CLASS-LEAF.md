# HANDOFF 2026-05-29 — Opus 4.8 — RK-NFA-4 G1-1 bb_nfa_class leaf

**Goal:** GOAL-RAKU-BB (TOP PRIORITY). Rung: G1-1 (RK-NFA-4), the isolated `BB_NFA_*` Raku-regex
mode-4 emission family.

## What landed

`bb_nfa_class` — the 32-byte character-set bitset leaf — landed in SCRIP `037be2ce`
(pushed to origin/main; rebased past peer Prolog commit `123878af` conflict-free).

Files touched (all in SCRIP):
- `src/emitter/BB_templates/bb_nfa.cpp` — new `bb_nfa_class_str` + `bb_nfa_class` (MEDIUM_TEXT).
- `src/emitter/BB_templates/bb_templates.h` — `bb_nfa_class` prototype.
- `src/emitter/emit_core.c` — `BB_NFA_CLASS` split off `bb_stub` → `bb_nfa_class(nd)`.

## Design points (for the next implementer)

- **cset travels as rodata, NOT a pointer.** Mode-4 TEXT assembles a SEPARATE native binary
  (`scrip --compile --target=x86` → `.s` → `as` → `gcc` link → run; see
  `scripts/run_raku_via_x86_backend.sh`). A `movabs` of `pBB->sval` (the GC blob from
  `raku_nfa_to_bb`) is valid only inside the compiler process and would DANGLE in the linked
  binary. So the 32-byte cset is emitted inline as `.LnfaccN: .byte 0x.. ×32` in `.section .rodata`,
  reached via `lea rdx, [rip + .LnfaccN]`.
- **Membership test mirrors `raku_cc_test` exactly** (`raku_re.c`): byte = `bits[c>>3]`,
  bit = `c&7`. Emitted: `movzx eax,[r14+r13]; mov ecx,eax; shr ecx,3; lea rdx,[rip+cs];
  movzx edx,[rdx+rcx]; and eax,7; bt edx,eax; jnc ω; inc r13; jmp γ`. Bounds first:
  `cmp r13d,r15d; jae ω`.
- **Register discipline:** scratch eax/ecx/edx only. The walker (`sm_bb_invoke.cpp` NFA arm)
  holds r13=pos, r14=subject base, r15d=slen (callee-saved, saved by the walker); rbx (also
  callee-saved) deliberately avoided so nothing needs preserving inside the leaf.
- **Label uniqueness:** `bb_node_id(pBB)` (= node ptr % 100000) keys `.LnfaccN`, unique per node.

## Verification

Byte-identical to the C-matcher oracle (the proven L1-L15 path) on bare single-class patterns:
- `[a-z]` hits 'h', misses '5'; `[A-Z]` on 'XYZ'; `\d` hits '5', misses 'x'; `\s` in 'hello world'.
- Leftmost sweep: `\d` found at pos 3 in 'abc5'; no `\d` in '___'.

(Quantified classes like `\d+`/`[a-z]+` still need SPLIT — not yet emitted — so they were not
probed through the slab; the C matcher remains the default and handles them.)

## Gates (all HOLD at baseline — work is default-OFF behind RK_NFA_BB)

```
GATE-RK   mode-2 (--interp):      41/42   (only rk_stdio39 fidelity non-bug)
GATE-RK4  mode-4 (--compile x86): 42/42
GATE-RK3  mode-3 native (--run):  41/42   CRASH 0
Smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5
SNOBOL4 pattern-rung suite:       BYTE-IDENTICAL M2 19/0 M4 18/1 (isolation proven)
FACT RULE grep:                   0
Build:                            clean
```

## NEXT CODE RUNG — bb_nfa_split (the HARD one)

`bb_nfa_split` is the last leaf for verdict-level patterns (`*`/`+`/`?`/`||`) and is NOT a simple
template. `nfa_bt` (`raku_nfa_bb.c`) SPLIT is RECURSIVE backtracking: try out1 (γ); if the rest of
the match DOWNSTREAM fails, return to the SPLIT and try out2 (β). The current `nfa_text_box` walker
(`sm_bb_invoke.cpp`) is a LINEAR fall-through — per-node label, ω→sweep-continue — that cannot
express an upstream return. Threading β=out2 alone is insufficient.

Proposed design: an explicit **backtrack-stack**. On SPLIT entry, push {out2-node-label, pos}; a
leaf's ω pops the stack and jumps to the saved {label, pos} instead of advancing the leftmost sweep;
the sweep advances only when the stack is empty. The existing `BB_ALT` MEDIUM_BINARY counter-state
slab (`bb_alt.cpp` / `bb_pl_alt.cpp`) is the live model for a stack-backed choice point. Byte-exact
x86, crash-on-wrong-byte → fresh full-budget session.

After SPLIT: RK-NFA-3 captures (`$0`/`$1`, L13-L15), RK-NFA-5 mode-3 BINARY (byte twins of the TEXT
arms), then G1-3 flip default `~~`→BB.

Repro for the emitted slab: `RK_NFA_BB=1 bash scripts/run_raku_via_x86_backend.sh FILE.raku`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
