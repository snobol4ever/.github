# HANDOFF 2026-06-01 (Opus 4.8) — SNOBOL4-BB: SEAL-BOUNDARY HOOKS (BB_LINK + HEAD BLOCK) — DESIGN ONLY

**Repos / HEADs at handoff:** SCRIP `86c265e` (UNCHANGED — no SCRIP code this session) · .github `<this commit>` (pushed last).
**Goal:** GOAL-SNOBOL4-BB.md (SESSION RUNG #0). **Type:** DESIGN — no code committed to SCRIP; nothing compiled against new logic.
**Identity:** `git config user.name LCherryholmes`, `user.email lcherryh@yahoo.com`.
**Build (lockstep, when code resumes):** `cd SCRIP && bash scripts/build_scrip.sh && make libscrip_rt`.

---

## What happened

A design conversation with Lon resolved the ONE thing element-granularity sealing had not yet answered: **how the
OUTERMOST edges of a SEALED pattern graph (the head's OUTSIDE-γ success-out and OUTSIDE-ω fail-out) reach a target
that DIFFERS PER CALL SITE.** When `DT_P` becomes a real SHARED sealed head (`COLOR = 'GOLD' | 'BLUE'` driven from
`B ? COLOR` and `C ? COLOR`), the bytes are identical but the outward targets differ — so they cannot be baked
`jmp rel32`. The current PB-RB-3 inline-emit dodges this (element emitted inline per statement, OUTSIDE-γ/ω
hardwired); the dodge expires when `DT_P` is shared. The answer was written into the GOAL's CORRECTED PATTERN
ARCHITECTURE section (no code).

### The design, as recorded (two coupled ideas + one refinement)

1. **`BB_LINK` — the universal seal-boundary external edge (ζ-slot indirect jump).** A sealed graph reaches OUTSIDE
   only through a `BB_LINK`: a SINGLE-ENTRY PURE-TAIL box whose only emitted code is `jmp qword [r12 + link_off]`
   (~5 bytes). No β, no γ/ω of its own, no state, never returns to itself — that degeneracy is the guardrail
   against it re-growing into the deleted broker. The DRIVER writes the per-call-site targets into the `ζ` slots
   BEFORE entering the sealed head; sealed bytes stay immutable + re-entrant (instruction fixed, only the slot DATA
   is per-call-site — the dual of a return-address slot, one γ one ω). It allocates its own `ζ` slot(s) via
   `bb_slot_alloc` and the wiring/STITCH step FILLS them — parallel to `bb_match` α allocating start-cursor +
   subject slots today. "Two fixed slots (γ,ω)" is the degenerate one-head case; general form is a VECTOR of link
   slots, one per `BB_LINK`. This is Fork D's ε-boundary made concrete (the ε-merge role and the external-hook role
   were the same problem). Matcher templates stay SEAL-PURE — only direct jumps; if a label is a `BB_LINK`, the box
   neither knows nor cares.

2. **Every GLOB has a HEAD BLOCK; glob→glob is the SAME boundary (recovered prior design).** Going BB-BLOCK-1 →
   BB-BLOCK-2 is the same external-edge case as head→outside; the HEAD BLOCK is the universal transition node where
   a `BB_LINK` lives. **`BB_MATCH` ↔ `BB_LINK` ↔ dynamic land:** `BB_MATCH` DRIVES (establishes the frame, sets the
   slots, jumps off into the element AND is jumped back into — the ch.18 outer-loop), `BB_LINK` is the pure edge,
   "dynamic land" is the per-call-site continuation. `BB_MATCH` is *kinda* a `BB_LINK` but not — it returns to
   itself; `BB_LINK` never does. A sealed interior NEVER holds an outward `rel32`.

3. **REFINEMENT — a HEAD BLOCK is HALF a Byrd box, and that half IS `DT_P`.** A full BB has four ports (α/β inbound,
   γ/ω outbound); a HEAD BLOCK has ONLY the two OUTBOUND hooks (OUTSIDE-γ, OUTSIDE-ω) — no α/β, because it is not a
   matcher, it is what the sealed body flows INTO and back OUT from. Identity: **`DT_P` ≡ HEAD BLOCK ≡ { entry,
   OUTSIDE-γ slot, OUTSIDE-ω slot }** — two hooks, not four. `BB_LINK` is therefore NOT free-floating; it IS the
   outbound half of the head. Collapses an apparent third concept: STITCH's build-time `{entry, exit, fail}`
   descriptor (runtime twin of lower2's α_out/β_out↑ γ_in/ω_in↓) is the SAME object as the run-time HEAD BLOCK
   (`exit`=OUTSIDE-γ, `fail`=OUTSIDE-ω, `entry`=jump-in).

### Why NO REGISTERS for the continuations (decided — Lon)

The continuations must SURVIVE `call memcmp@PLT` inside element matchers. Under SysV, r8–r11/rax/rcx/rdx/rsi/rdi
are caller-saved (clobbered — the reason `bb_lit` does `push r10;call;pop r10` and `bb_match` α re-establishes r10
after `rt_sno_subject_load`). The callee-saved set (rbx/rbp/r12–r15) survives but is fully allocated
(ζ/Σ/δ/Δ/DESCR-base/hash-base) — no free register. The ζ-frame is the only correct home. **Concurrency-free by
construction:** sealed code is never mutated; every per-activation datum (continuations included) rides the
per-sequence R12 frame, which switches per sequence and survives calls — two concurrent drives of one sealed
`COLOR` use their own frames. (Unseal/reseal was the only design WITH a concurrency hazard; this dissolves it.)

### Two pins flagged for implementation time (not yet code)

- **ONE FRAME PER MATCH** so `[r12+off]` is unambiguous: a stitched pattern runs in ONE frame for the whole match —
  per-element SLOTS in the one statement frame, NOT per-element frames. A FRESH frame appears only at a genuine
  subroutine seam (pattern-valued variable invoked as a callee, or `*E`/EVAL), which is exactly where an explicit
  continuation hand-off is wanted anyway.
- **`BB_LINK` IS PURE TAIL, NOT PORTED** (α loads-and-jumps; no β/γ/ω) so it can never become a re-dispatch point.
  The all-invariant frozen pattern (PB-OPT) keeps HARDWIRING (own statement, not shared → continuations known at
  emit time, zero indirection). You buy `jmp [r12+off]` ONLY when you seal-and-share.

---

## Actions taken

- `.github` `1f87568f` — added the SEAL-BOUNDARY HOOKS note (ideas 1 + 2 + NO-REGISTERS + two pins) after the
  CORRECTED PATTERN ARCHITECTURE two-new-boxes block.
- `.github` `f0575d3d` — refinement (HEAD BLOCK = half a BB; `DT_P` ≡ HEAD BLOCK; STITCH descriptor is the same
  object).
- `.github` `<this commit>` — watermark update (design-only; SCRIP HEAD corrected `e39c329`→`86c265e` — a Prolog
  commit landed after the prior SNOBOL handoff was written and this session added no SCRIP code) + this handoff doc.
- **No SCRIP changes. No corpus changes.** FACT RULES byte-identical-×3 re-verified GREEN
  (`audit_concurrency_invariants.sh` OK) after every doc edit.

## Gates (inherited `86c265e`, re-confirmed at session start; UNCHANGED — no new code)

```
make scrip                       rc=0   (needs libgc-dev: apt-get install -y libgc-dev — core.h/raku_nfa_bb.c <gc/gc.h>)
make libscrip_rt                 rc=0
test_smoke_snobol4.sh            m2 7/7 HARD · m3 5/6 (define lone fail) · m4 0/6 (REG ladder unblocks)
test_smoke_icon.sh               m2 12/12 HARD · m3 12/12 · m4 12/12
prove_lower2.sh                  67/0
test_sno_pat_bb_probe.sh         3/3
test_gate_sm_dead.sh             0  (<=1)
test_gate_no_vstack.sh           g_vstack 0
audit_concurrency_invariants.sh  OK (FACT RULES byte-identical x3; LOWER 5097ed94, EMITTER 307534d6)
```

---

## NEXT — PRIORITY ORDER (unchanged from Lon 2026-06-01)

**(1) REG LADDER FIRST** (🔴 CURRENT PRIORITY section at top of the GOAL). REG-0 folded into the landed PB-RB-3,
so **REG-1 (`bb_lit`) is the first code step**: migrate BINARY+TEXT off the legacy subject model
(`[r10]`-cursor / `movabs &Σ;deref` / `movabs &Σlen;deref`) to the ratified registers Σ=R13 / δ=R14 / Δ=R15
(`bb_regs.h` `BBREG_*`/`BBREGN_*`). Cursor read `mov eax,[r10]`→`mov eax,r14d`; write `mov [r10],eax`→
`mov r14d,eax`; Σ-base→use `r13`; Δ-compare→`cmp eax,r15d`; β `sub`→on `r14d`. The two `movabs`+deref blocks vanish
(patch tuple shrinks); removes both `TEMPLATE_ADDR_SIG*` bakes from `bb_lit`. Convention compliance AND the SNOBOL
mode-4 unblocker (m4 0/6 cause = baked process-local addresses). Prove: prove_lower2 topology unchanged; mode-3
`S 'b'` in `'abc'` under REG-0; disasm shows cursor=r14/Σ=r13/Δ=r15, no `&Σ`/`&Σlen` imm64; **m2 7/7 HARD must
stay invariant** (mode-2 oracle `bb_exec.c` is UNTOUCHED). Then REG-2 (cursor-advancing leaves) → REG-3 (position
leaves) → REG-4 (combinators — saved-δ slot moves `[r10]`→ζ-slot of R14) → REG-5 (generators+capture, coordinate
with BROK-1/2) → REG-FENCE (add `scripts/test_gate_sno_pat_reg.sh`; re-measure SNOBOL m4 — expected > 0/6).

**(2) THEN** PB-RB-4 (STITCH_SEQ/STITCH_ALT — topology already proven `e39c329`, only emitter wiring + drive;
mode-3 `S ('a'|'b')` / `S 'a' 'b'`), PB-RB-5…OPT, BROK-0…BROK-3.

**BB_LINK / HEAD BLOCK is PB-RB-4+/PB-OPT-era** (shared sealed heads), NOT a REG blocker — the REG ladder ships
first. When it lands, the concrete touchpoint is the `g_match_*` emit-globals + `bb_slot_alloc` path that today
passes `g_match_elem_p`/`g_match_advance_p` into `bb_match` α — that is where a `BB_LINK` instance allocates its
slot and the driver fills it.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
