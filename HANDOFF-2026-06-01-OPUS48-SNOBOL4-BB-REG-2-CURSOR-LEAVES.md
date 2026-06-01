# HANDOFF 2026-06-01 (Opus 4.8) — SNOBOL4-BB: REG-2 (5/6) cursor-advancing leaves + REG-RO step

**Repos / HEADs at handoff:** SCRIP `eb4bf7c` (pushed) · .github `<this commit>` (pushed last).
**Goal:** GOAL-SNOBOL4-BB.md — REG ladder (🔴 CURRENT PRIORITY). **Type:** code (5 BB templates) + 1 GOAL step.
**Identity:** `git config user.name LCherryholmes`, `user.email lcherryh@yahoo.com`.
**Build (lockstep):** `cd SCRIP && bash scripts/build_scrip.sh && make libscrip_rt`. ENV: needs `libgc-dev`
(`apt-get install -y libgc-dev` — `core.h`/`raku_nfa_bb.c` include `<gc/gc.h>`).

---

## What this session did

### 1. REG-2 — 5 of 6 cursor-advancing pattern leaves migrated to the ratified registers

Migrated off the legacy subject model (`[r10]`-cursor / `TEMPLATE_ADDR_SIGMA` / `TEMPLATE_ADDR_SIGLEN` movabs
bakes) onto **Σ=R13 / δ=R14d / Δ=R15d** (per REG-0, established by BB_MATCH α). Both BINARY and TEXT arms;
JVM/JS/NET/WASM arms untouched.

| Box | BINARY size | `bin` sites | notes |
|-----|-------------|-------------|-------|
| `bb_pat_len`    | 34B  | {13,25,29,30}       | δ+n vs Δ; β = jmp ω (no restore) |
| `bb_pat_rem`    | 13B  | {4,8,9}             | δ ← Δ (REM ≡ RTAB(0)); β = jmp ω |
| `bb_pat_any`    | 74B  | {8,52,61,65,70}     | je ω on miss; β undoes δ+=1 |
| `bb_pat_notany` | 74B  | {8,52,61,65,70}     | identical to ANY except byte@50 `0F84`→`0F85` (je→jne) |
| `bb_pat_span`   | 195B | {118,143,147,167,191} | greedy loop; internal Δ **jge +62 / je +18 / jmp loop −86**; dropped r11 base-copy + push/pop r11 (Σ=r13 used directly); z_slot/zo_slot scratch kept |

**Method / discipline:** every BINARY byte map was assembled+disassembled with `as`+`objdump` BEFORE writing it,
so each literal offset in `bin` is confirmed against the real encoding (FACT RULE TWO LITERAL FORMS — hand-coded
literal offset map, no `b.size()`). This **caught a real bug**: `movzx esi, byte [r13+rcx]` needs the disp8 SIB
form (`41 0F B6 74 0D 00`, 6 bytes) because r13 as SIB base with mod=00 means disp32 — unlike the original
`[r11+rcx]` (5 bytes). Per-box β semantics were **preserved exactly** (REG-2 is an addressing migration, not a
behavior change): `len`/`rem` do not restore the cursor on β (the combinator does — REG-4); `any`/`notany` undo
their own `δ += 1`; `span` gives back one char at a time. `span`'s `z_slot`/`zo_slot` (process-lifetime deque-int
scratch) stay — per-box local match state, NOT a value stack (REG-4/5 ζ-slot migration is a later rung).

All 5 boxes are **token-clean**: zero `TEMPLATE_ADDR_SIG*` / `[r10]` in code OR comment (forward-clean for the
future REG-FENCE gate). They are cleaner than the REG-1 reference `bb_lit`, which deliberately keeps a
`mov [r10], r14d` mirror.

### 2. NEW STEP — REG-RO (READ-ONLY locals → IP-relative), inserted before REG-FENCE

Lon directive. The SNOBOL pattern **BINARY** arms bake their RO ADDRESSES (`bb_lit` `movabs rsi,&lit` +
`movabs rax,&memcmp`; cset boxes `movabs rdi,&cset` + `movabs rax,&strchr`) as `movabs` imm64 — violating
RULES.md **ICON READ-ONLY LOCALS ARE IP-RELATIVE FACT RULE** ("RO locals are NEVER addressed by an absolute
`movabs` immediate"). The matching TEXT arms already do it right (`lea reg,[rip+label]` / `call …@PLT`). REG-RO
moves each baked address into a sealed RO data trailer adjacent to the box BLOB, reached `[rip+disp]` with a
LITERAL emit-time disp. **Payoff:** (1) RO FACT-RULE conformance; (2) position-independent BINARY (mode-3 JIT)
arm — a 2nd contributor to lifting SNOBOL m4 alongside the `&Σ`/`&Σlen` removal; (3) with RW state in
ζ=R12/Σ=R13/δ=R14/Δ=R15 and RO state `[rip+disp]`, **r10 has no remaining purpose** — the `[r10]` mirror writes
and `push/pop r10` guards become dead and are removed, eliminating r10 from the pattern family. Small literal
INTEGER immediates (e.g. `bb_lit`'s `mov rdx,len`) are out of scope. REG-FENCE + the ladder completion test were
updated to require zero `r10` (any form) and all RO addresses `[rip+disp]`.

---

## Gates (all GREEN; invariant vs prior HEAD `3916054`)

```
make scrip                       rc=0
make libscrip_rt                 rc=0
test_smoke_snobol4.sh            m2 7/7 HARD · m3 5/6 · m4 0/6
test_smoke_icon.sh               m2 12/12 HARD · m3 12/12 · m4 12/12
prove_lower2.sh                  67/0
test_sno_pat_bb_probe.sh         3/3
test_gate_sm_dead.sh             0  (<=1)
test_gate_no_vstack.sh           g_vstack 0
audit_concurrency_invariants.sh  OK (FACT RULES byte-identical x3)
test_gate_no_handencoded_bytes.sh  122 across 24 files (this change adds 0; +1 vs the 121 watermark is the
                                    intervening Prolog commits, confirmed by stashing this session's diff)
```

NOTE: a first Icon-smoke reading of m4 0/12 earlier in the session was an ARTIFACT of running it before
`make libscrip_rt` (mode-4 compile links against `libscrip_rt.so`); with the lib built it is the watermark's
12/12. SNOBOL m4 0/6 is the genuine pre-existing state (process-local address bakes), unchanged by REG-2.

---

## NEXT — priority order

1. **Finish REG-2: `bb_pat_break`** (the last cursor-advancing leaf). Dual-arm — plain BREAK (178B) + BREAKX
   (302B, two scan loops). It is **all-or-nothing for the REG-FENCE grep** (converting only the plain arm leaves
   the file flagged), so do both arms in one focused pass. The plain arm is **pre-computed + objdump-verified**:
   153B, `bin {125,129,149}`, internal Δ **jge +63 / jnz +19 / jmp loop −88**, Σ=r13 direct (drop r11 + push/pop),
   `z` stays in `[zeta+8]`. BREAKX: use the **`as`-transcribe route** — write the REG-2 form as GAS asm, let `as`
   compute the internal short/rel32 jumps, disassemble, and transcribe the literal bytes into the template (the
   assembler as a development-time calculator; the emitted template stays a hand-coded literal map per the FACT
   RULE — exactly how the 5 boxes this session were verified). Preserve the BREAKX extend-past-match semantics
   (ground against `bb_exec.c` IR_PAT_BREAK ival==1 per CONSULT CANONICAL SOURCES). Reached only via the
   (torn-down) brokered path, so verification is bytes + gates, not execution.
2. **REG-RO** (new step, see GOAL): RO addresses → `[rip+disp]`, kills r10. Do AFTER the RW ladder so each box is
   touched once; the `movabs`+imm64 (10B) → `lea [rip+disp]` (7B) shifts offsets — re-derive each byte map with
   `as`+`objdump` exactly as REG-2 did.
3. Then **REG-3** (pos/tab) → **REG-4** (combinators: `bb_pat_alt`/`bb_pat_cat`/`bb_pat_fence`, saved-δ to ζ-slot)
   → **REG-5** (generators + capture, coordinate with BROK-1/2) → **REG-FENCE** (add `test_gate_sno_pat_reg.sh`,
   wire into Session Setup, RE-CHECK SNOBOL m4 — expected liftable once a pattern chain assembles+links+runs).
4. Then PB-RB-4 (STITCH_SEQ/STITCH_ALT) … PB-RB-OPT, BROK-0…3. The PB-RB pattern-engine breadth is the LONG POLE
   for the SNOBOL4 corpus.

**Do NOT regress:** m2 7/7 HARD is the invariant (mode-2 oracle `bb_exec.c` is untouched by the REG ladder);
prove_lower2 67; probes 3/3; g_vstack 0; FACT RULES byte-identical ×3 (LOWER `5097ed94`, EMITTER `307534d6`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
