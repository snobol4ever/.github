# HANDOFF 2026-06-01 (Opus 4.8) — SNOBOL4-BB TEMPLATE-REVAMP v2: x86() conversions + NO-pBB / NO-neighbor rule

**Repos at handoff:** SCRIP `d96e1b0` (pushed) · .github this commit (pushed last)
**Goal:** GOAL-SNOBOL4-BB.md · **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus
**Identity:** `git config user.name LCherryholmes`, `user.email lcherryh@yahoo.com`
**Build (lockstep):** `cd SCRIP && make -j4 scrip && make libscrip_rt` (needs `apt-get install -y libgc-dev`).

---

## WHAT THIS SESSION DID

Continued the TEMPLATE-REVAMP PIVOT (v1 = `HANDOFF-2026-06-01-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V1.md`).
Two threads: (A) convert more BB templates to the `x86()` self-encoding form; (B) capture Lon's design
notes into a reviewable rule set, then HARDEN the central operand-access rule by removing `pBB`.

### A. Four more boxes converted to `x86()` + bb_lit hardened — all `pBB`-free, all `_.node`-free

Converted to the self-encoding `x86(mnem, …)` form (one return, pure concat, in-band L/J/D patch records via
`bb_emit_x86`, no `bb_bin_t`): **`bb_pat_rem`, `bb_pat_len`, `bb_pat_any`, `bb_pat_notany`** — plus
**`bb_lit` migrated** off `_.node`. All five are now **`pBB`-free END-TO-END**: the `bb_X_str()` template fn,
the `extern "C" void bb_X(void)` wrapper, the `bb_templates.h` prototype, and the `emit_core.c` dispatch call
are ALL parameterless. Every arm (x86 + the dead JVM/JS/NET/WASM arms) reads `_` only. **grep proof: zero
`pBB` and zero `_.node` in all five files (code AND comments).**

- `bb_pat_rem` / `bb_pat_len`: convert with NO new vocab; BINARY byte-identical to the prior hand map
  (len now uses imm8 short-form = what `as` emits).
- `bb_pat_any` / `bb_pat_notany`: needed two new encoders (below); differ only by `je`↔`jne` after `strchr`.

### x86_asm.h vocabulary added (the toolkit the four sessions inherit)

- `x86_is64` + REX.W in `x86_alu_rr` → 64-bit `test rax,rax` (pointer test after a `call`).
- `x86_movzx_subj_byte(dst)` → `movzx dst, byte [r13+rcx]` (indexed subject-byte load) + `movzx` dispatch case.
- `x86_add`/`x86_sub` now emit the **imm8 short-form** (`0x83 /r`) when the immediate fits int8, else imm32 —
  so the BINARY arm matches `as` byte-for-byte (verified by assembling the TEXT and diffing).

### op_sval / op_ival promotion (enables the no-pBB rule)

- Added `const char *op_sval; int64_t op_ival;` to `sm_emit_t` (`emit_globals.h`).
- At the **single dispatch point** (`emit_core.c`, beside `g_emit.node/nid/sid`): `g_emit.op_sval = nd->sval;
  g_emit.op_ival = nd->ival;` — i.e. promote ONLY the directly-accessible node fields. Templates read
  `_.op_sval` / `_.op_ival` (via pure parameterless accessors), never the node, never a neighbor.

### B. Rules draft + a new FACT RULE (NOT yet folded into the 5 GOAL files)

**`.github/GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`** (NEW) — Lon's notes turned into:
- **R1–R13 (NORMAL rules):** drop MEDIUM_MACRO_DEF; one medium (invisible); one return per PLATFORM_*; string
  concat only; no locals (operands from `_` only); all variance inline (`X + IF(...) + FOR(...) + …`);
  `x86(mnem,…)` keyed on the mnemonic; side-effect-free concat (effects only in `bb_emit_x86`); in-band L/J/D
  patch records (no `bb_bin_t`); BINARY must match `as`; TEXT-first conversion; NO safety net / GROUND ZERO /
  go fast; format+comments deferred.
- **FACT RULE — "a template reads only `_`; `pBB` and node-neighbors are forbidden":** only `nd->FIELD`
  directly-accessible fields are promoted; the template references no `pBB` (REMOVED) and never derefs
  `_.node`; the driver gathers any neighbor fact into a scalar BEFORE the call. **Reasons:** no confusion +
  BB-fusion ("double-indemnity") impossible. **Enforcement = the COMPILER** (no `pBB` in scope ⇒ neighbor
  access doesn't compile) + a one-line `_.node` grep gate. This is the only revamp rule worth being a FACT
  RULE; the style rules stay normal (a grep can't judge "good `IF` folding").

---

## GATES AT HANDOFF (all green / at floor)

```
make scrip / make libscrip_rt   rc=0
PAT-BB probes                   3/3
SNOBOL4 smoke                   m2 7/7 HARD · m3 5/6 (floor 5) · m4 0/6 (floor 0, by design)
Icon smoke                      m2 12/12 HARD (byte-neutral — only SNOBOL pattern boxes touched)
prove_lower2                    67
audit_concurrency_invariants    OK (FACT RULES byte-identical ×3 — the sm_emit_t field add did NOT perturb)
util_template_purity_audit      clean (the 5 converted boxes not flagged)
g_vstack                        0
```

NOTE — `test_gate_no_handencoded_bytes.sh` baseline is **123/24** (informational); the 5 conversions are
b.size()-neutral (they used literal `bin={{}}`, not `b.size()`), so the count is unchanged by this session.

---

## NEXT SESSION — two tracks, in this order

**(1) DESIGN THE INTERNAL-LABEL RECORD (the one open item; gates half the boxes).** The L/J/D records only
encode the FOUR PORTS (α/β/γ/ω). Boxes with INTERNAL loops — `bb_pat_span`, `bb_pat_break`, the combinators
`bb_pat_alt`/`bb_pat_cat`, the generators — jump to labels that are NOT ports ("jmp loop −88"). Add an
internal-label record kind (proposed: `D <id>` define / `J <id>` patch, `id ≥ 4` box-local, a small per-box
local-label allocator) so the four parallel sessions don't invent four incompatible schemes. **Until this
lands, only loop-free leaves are convertible.** `bb_pat_alt`/`bb_pat_cat` ALSO have the variable-length
define/jmp-pair loop (`g_emit.xa_bb_emit_pair_n`) — a second open question (discovered positions for a
variable-length box).

**(2) GRAND-MASTER-REORG — fold the rules in (Lon authorizes).** Move R1–R13 into the goal file prose; make
the no-pBB/no-neighbor FACT RULE byte-identical across the 5 GOAL-*-BB files; reconcile/retire the superseded
TWO-LITERAL-FORMS + TEMPLATE-ONLY-EMISSION FACT-RULE text + RULES.md + the purity/concurrency gates to the
self-encoding model; add `scripts/test_gate_template_no_node.sh` (grep `_.node`/`g_emit.node` in
`BB_templates/*.cpp`, must be 0) and wire it into Session Setup.

**THEN the divvy-up** (already tabulated in the rules draft's "DIVVY-UP MATERIAL" b.size() ledger): each of
the four GOAL-*-BB sessions converts its own boxes TEXT-first per the rules and helps a neighbor with
loop-free leaves. SNOBOL-owned debt is small (`bb_pat_cat`/`alt`/`match` + the already-convertible loop-free
`span`/`break`/`pos`/`tab`/`atp`/`arb`/`fence`/`defer`/`abort`). The internal-label design (track 1) is the
shared prerequisite for every looping box across all four languages.

---

## POINTERS

Rules + divvy ledger: `.github/GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`. Self-encoding header + `x86()` API:
`SCRIP/src/emitter/BB_templates/x86_asm.h`. Consumer: `bb_emit_x86` (in x86_asm.h). Promotion point:
`emit_core.c` (`g_emit.op_sval/op_ival = nd->sval/ival`). Worked exemplars (copy these): `bb_pat_rem`,
`bb_pat_len`, `bb_pat_any`, `bb_pat_notany`, `bb_lit`. v1 handoff:
`HANDOFF-2026-06-01-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V1.md`.
