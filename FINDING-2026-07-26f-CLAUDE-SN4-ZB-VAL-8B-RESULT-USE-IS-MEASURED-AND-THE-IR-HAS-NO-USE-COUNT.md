# FINDING-2026-07-26f — SN4 ZB-VAL-8b: THE RESULT-USE PREDICATE IS MEASURED, AND THE IR HAS NO USE COUNT

**Session:** s181 (2026-07-26) · **Baseline:** SCRIP `92e926cf`, corpus `3df944f3` · **Code landed:** NONE by design (survey + measurement, s180 precedent)
**Build:** `rm -f scrip && make -j4 scrip` → rc=0, links `out/libscrip_rt.so`. Tree clean, `git status` empty at entry and exit.
**Directive under test (Lon, this session):** *"Have each BB allocate its RESULT value, IF it has one and if it is used. Have each BB allocate its LOCAL STORAGE needs, IF it has any. One instruction, decrement RSP. Sliding offsets, index operands from RSP not RBP. Continue until a BRICK WALL, then add the RBP/RSP dance."*

---

## ⭐ HEADLINE 1 — THE DIRECTIVE'S "IF IT IS USED" IS REAL, MEASURED, AND DISCRIMINATING

Two minimal programs, compiled `--compile`, emitted asm read directly. Same construct, opposite verdicts.

**`lt1.sno` — predicate consumed as CONTROL (`LT(A,B) :S(YES)F(NO)`)**

```
n15_op77_α:
    lea   rdi, [rbp + 96]           ; C0
    lea   rsi, [rbp + 80]           ; C1
    call  rt_cmp_d@PLT
    test  eax, eax
    jns   n6_lit_string_α           ; result consumed IN EAX
    mov   qword ptr [rbp + 64], 0   ; T cell
    mov   qword ptr [rbp + 72], 0   ; T cell
    jmp   n5_lit_string_α
```

`[rbp+64]` / `[rbp+72]` are the CMP root's result cell. **Both references are WRITES. Zero reads in the entire program** (verified by exhaustive grep of the emitted `.s`). The comparison's result travels in `eax` via `test`/`jns` and never touches memory. The cell and its two stores are dead — the same shape s174 already deleted one level up (ω FAILDESCR stores, redundant with the `eax=99` register signal).

**`lt2.sno` — same predicate consumed as a VALUE (`OUTPUT = LT(A,B) 'yes'`)**

```
155:  mov  qword ptr [rbp + 96], 0        ; write
156:  mov  qword ptr [rbp + 104], 0
170:  mov  rdi, qword ptr [rbp + 96]      ; READ
171:  mov  rsi, qword ptr [rbp + 104]     ; READ
174:  call str_concat_d@PLT
```

Same node kind, cell **read** and fed to the concat. SNOBOL4 predicates return the null string on success (manual p.32 — predicates are functions that succeed/fail), so the value form is legal and live.

⛔ **CONSEQUENCE: "zero-grant the CMP" as a blanket rule is WRONG and would have silently broken the value form.** The grant is a genuine per-instance USE TEST, exactly as the directive words it. Confirmed by contrast, not asserted.

---

## ⛔ HEADLINE 2 — BLOCKER 1 IS SHARPER THAN s180 STATED: THE IR CANNOT EXPRESS "IS USED"

`zeta_storage.c:379` gates the whole value-spine scan on `a->op == IR_ASSIGN`, and its own comment names the constraint: `bb_assign_global` is **"the only vfc release arm."** s180 read the predicate case as "no gate to enter through." The deeper fact:

- **No `n_uses` / `use_count` / `consumed` / `n_consumers` field exists anywhere in `IR.h`.**
- `ir_node_produces_value(IR_e op)` (`scrip_ir.c:216`) is keyed on the **OPCODE** — it answers *"can this kind produce a value,"* never *"is this instance's value read."*

This is why the s174 diet had to proceed by opcode arms plus an entry-rooted reachability walk: use information was never available. **ZB-VAL-8b therefore requires a NEW ANALYSIS PASS, not a predicate tweak.** It must separate two edge classes that the graph currently mixes:

| edge | meaning | grant |
|---|---|---|
| `operands[]` | value use — a consumer reads the producer's cell | **YES** |
| γ / ω wire | control use — successor label only | **NO** |

s180's *"the release owner becomes a GOTO"* is the same fact in different words. The BFS in `zls_build` already walks γ/ω/operand edges separately, so the classification has a home — the pass is small in concept, but it is a pass.

---

## ⭐ HEADLINE 3 — THE SLIDING-OFFSET MECHANISM EXISTS, IS LIVE BY DEFAULT, AND 108 OF 120 TEMPLATES RIDE IT FREE

Lon: *"All of this sliding offset calculation to arbitrary-depth operand access has been done before. At least I was told so."* **Correct, and it is not a prototype — it is the default path.**

- `x86_asm.h:306` — `x86_fc_hit(off)`: true iff FORTH port, box granted, and `off ∈ [op_fc_base, op_fc_base + w)`.
- `x86_asm.h:828/853` — `FR(off)` / `FRQ(off)` emit **`[rsp + off - op_fc_base]`** on hit, `[rbp + off]` otherwise.
- `zeta_choices.h:117` — `#define ZC_PORT ZC_PORT_FORTH`. **Live default.**

**Conversion map (measured by grep, an independent method from s180's read-through — same answer):**

| | count | meaning |
|---|---|---|
| templates calling only `FR()`/`FRQ()` | **108** | convert to rsp with **ZERO edits** — granting the box flips addressing |
| templates hand-writing `rbp` | **12** | the entire job |

The 12: `xa_flat.cpp` (77 refs — FUNCTION wall, dominant) · `bb_save_restore` (10 — statement bracket) · `bb_match_fence1` (9 — fence commit) · `bb_match_arbno` (6) · `bb_call_proc_staged` (4) · head/capture/alternate/replace/release/defer (9 combined — pattern-retry cluster) · `bb_create` (1).

**These land on s180's four wall shapes exactly.** On ARBNO specifically: Lon named it a required-RBP construct and that is right *operationally*, but its 6 refs sit downstream of fence1's 9 and retry's 9 — s180's "ARBNO is a COMPOUND of retry+fence, do not build it a private wall" is supported by the reference distribution.

---

## ⭐ HEADLINE 4 — THE HYBRID ALREADY RUNS IN ONE FRAME TODAY

`lt1.sno` main, measured: `sub rsp,216` → `mov rbp,rsp` (frontier seeded) → **four `sub rsp,16` box self-carves** → `main_γ`/`main_ω` both `mov rsp,rbp` (bulk whack).

Static rsp self-carving and the rbp frontier **coexist in the same emitted function right now.** The answer to *"is everything still looking possible from here"* is not a projection — the hybrid is shipping. This also confirms Lon's own concession empirically: the whack sites are exactly where depth stops being statically knowable. **Frontier = necessity; addressing = convenience** (s180's law, independently re-derived).

---

## ⚠ HEADLINE 5 — WINDOWS MUST BE PER-NODE COMPUTED, NEVER HARDCODED

`lt1` flat layout, measured: **A=128 · B=112 · C0=96 · C1=80 · T=64** — monotonically descending, 16B stride, push order. Window = deepest-operand-flat − own-flat + 16:

- **C0: 48** (reads A@128 → 32) · **C1: 64** (reads A@128 → 48) · **T: 48** (reads C0@96 → 32, verified directly from the `lea rdi,[rbp+96]` above)

Matches s180's 48/64/48 against live geometry. **BUT:** `lt2` allocates the *same construct* at different offsets (frame 200 vs 216; its CMP reads `[rbp+128]`/`[rbp+112]`). Flat layout is per-graph. **Windows must be computed at grant time from the actual flat offsets — any hardcoded 48/64/48 constant is a latent bug.** This reinforces s180's per-node `op_fc_wbytes` plan and rules out a table.

---

## ⚠ HEADLINE 6 — THE FALLBACK IS SILENT (PROCESS HAZARD, WANTS A GATE)

`x86_fc_hit` returns false when an offset falls outside the window, and `FR()` then **quietly emits `[rbp+off]`.** An undersized window does not crash and does not emit a wrong address — it leaves the box on rbp. **"I converted it" and "it converted" are different facts, and nothing in the build distinguishes them.** Given the 48/64/48 spread and per-graph layout, mis-sizing is near-certain at least once.

**PROPOSED:** `test_gate_fc_no_residual_rbp.sh`, in the existing `test_gate_*.sh` family — compile the corpus, assert zero surviving `[rbp+` inside granted regions. Without it, conversion progress is unfalsifiable.

---

## NEXT RUNG

1. **ZB-VAL-8b-USE** — add the operand-vs-wire use analysis (Headline 2). Entry predicate moves from assign-root to statement-root; result grant becomes conditional on a value consumer existing. Prediction to falsify: `lt1` spine carves **64, not 80** (T dropped); `lt2` unchanged.
2. **ZB-VAL-8c** — per-node computed `op_fc_wbytes` (Headline 5). Never a constant.
3. **The gate** (Headline 6) before any bulk template conversion.
4. Release edges: γ and shared ω each spend one `add rsp,K`. s180 notes all five nodes share ONE ω, so the failure landing needs exactly one pop, not five.

**Gate docs read this session:** `PLAN.md`, `GOAL-SNOBOL4-BB.md`, `REPO-SCRIP.md`, `REPO-corpus.md`, `ARCH-ICON.md`. ⛔ **`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` NOT yet read — mandatory before any `x86_asm.h` encoder or `xa_*`/`bb_*` template edit (PLAN.md step 6).** The Headline-2 pass lives in `contracts/`, but the release edges (item 4) touch templates and are gated.

**ARCH note (ARCH-ICON.md, 2026-07-18 register contract):** the two ζ regimes are architecturally distinct — `x86_zr()` = RSP (control-flow-lifetime cells, FORTH carve) vs `x86_fb()` = RBP (value-slot frame, "all FR/FRQ resolve `[rbp+off]`, no depth compensation"). Value slots on rbp are the **ratified contract**, not drift. The directive deliberately migrates value slots from the flat rbp frame onto the rsp spine; `fc_hit` is the sanctioned bridge between the regimes. Worth stating plainly because it makes the ZB-VAL ladder an architecture change, not a cleanup.

**WATERMARK:** unchanged — nothing emitted. `handoff_status.sh` is the push truth, not this block.
