# FINDING s206 (2026-07-28) — ZHEAP: THE PORT WAS UNSELECTABLE, THE GRANT PREDICATES DISAGREE, AND THE "PROVING CONFIGURATION" IS NOT REACHABLE BY A PREDICATE FLIP

**SCRIP `cca948c5`** (defect fixes, landed). One experiment TRIED AND REVERTED with measurements. RT_OPT=`-O0` per O2-DIRECTED-ONLY. Basis: s205 pivot, `GOAL-SNOBOL4-BB.md` LIVE CURSOR.

---

## 0. INSTRUMENT — the s205 six-program tripwire, independently reproduced

Rebuilt from the s205 description and confirmed at HEAD before any edit. `--run`, default port vs port 7:

| program | carves ζ? | FORTH (6) | HEAP (7) |
|---|---|---|---|
| `t1_nomatch` `'ABC' 'ZZZ'` | lit cells | OK | OK |
| `t2_lit` `'ABCDE' 'BCD'` | lit cells | OK | OK |
| `t3_at` `@OUTPUT` | no | OK | OK |
| `t4_len` `LEN(3) . X` | yes | OK | **SEGV** |
| `t5_dollar` `ARB $ OUTPUT` | yes | OK | **SEGV** |
| `t6_arbno` `ARBNO('a')` | yes | OK | **SEGV** |

s205's split ("OK on every box that carves NO ζ") is directionally right but **imprecise**: `t1`/`t2` DO carve (`fc_vlit_active` grants IR_LIT_STRING a 16B cell, ZB-VAL) and are OK. The true split is not "carves" but "does a carving box also drive a path that consults the grant a second time" — see §2.

---

## 1. TWO SILENT DEFECTS — PORT 7 WAS NOT ACTUALLY SELECTABLE (both fixed, `cca948c5`)

**(a) STALE CLAMP — the real one.** `rt_zeta_port_set_mode()` (`zeta_alloc.c:266`) read
`g_zeta_port = (m >= ZC_PORT_PLAIN && m <= ZC_PORT_FORTH) ? m : (int)ZC_PORT;`
The upper bound was never raised when `ZC_PORT_HEAP` (7) was added, so **7 was silently reset to the compiled default** — no error, no telemetry. The getter (`rt_zeta_port_mode`, `atoi`, unclamped) is why `SCRIP_ZETA_PORT=7` reached the arm while every setter call did not.

⭐ **CONSEQUENCE BEYOND THE CLI, and it is the one that matters for ZHEAP-8.** `scrip.c:1216/1407` BAKE `mov edi,N; call rt_zeta_port_set_mode` into **mode-4 output** (the ZETA PORT bake, Lon 2026-07-10). So a mode-4 binary emitted WITH heap carves called the clamp at startup and ran with port mode **FORTH** — emitted code and runtime mode disagreeing. That is the same storage-at-X / addressing-at-Y class this rung exists to cure, sitting undetected inside the arm meant to prove it. **Any mode-3 vs mode-4 A/B run on port 7 before this fix was invalid.**

**(b) MISSING CLI NAME.** `--zeta-port=` accepted plain/instrumented/alloc/inline/cstack/forth; `heap` was absent, so the #1 rung's target port was reachable only as an env integer. Added. (`owned` stays env-only per the existing recorded decision.)

**VERIFIED:** `--zeta-port=heap` now byte-identical to `SCRIP_ZETA_PORT=7` (287 lines, 4 carves); default-port `.s` byte-identical pre/post on a NON-EMPTY 256-line artifact (s163 empty-file guard honored); bad names still rejected; tripwire unchanged on the default port. Before the fix the CLI path silently ran FORTH and therefore **hid all three SEGVs** — it now reproduces them.

---

## 2. ROOT CAUSE OF THE SEGV — TWO CONSUMERS, ONE BOX, CONTRADICTORY ANSWERS

**MEASURED (gdb, per RULES.md monitor/bracket discipline), `t4_len` port 7:**
`rt_cap_push (slot=0x7fffffff9c20, delta=0)` at `pattern_match.c:755`, `if (s->sp == s->buf[0])`, faulting `mov (%rax),%eax` with **`rax = 3`** — a garbage capture slot, never initialized.

**THE DISAGREEMENT.** `fc_geom()` (`zeta_storage.c:682`) is **PORT-BLIND** — it grants SAVE/SPAN/TAB/RTAB/BREAK/BREAKX/BAL/REM/ARB/value-literals a 16B cell on every port. Every `x86_fc_*` consumer was **FORTH-ONLY** (`x86_fc_on`, `x86_fc_hit` = `x86_port_mode() == ZC_PORT_FORTH && …`). Under HEAP therefore:

| consumer | answer under HEAP | effect |
|---|---|---|
| `fc_geom` (geometry + `hk` carve size) | **granted** | heap carve fires, `rax = block base` |
| `x86_fc_on` (push/pop `sub/add rsp,K`) | not granted | no cell on rsp |
| `x86_fc_hit` (FR/FRQ window rebase) | not granted | locals spelled FLAT `[rsp+off+op_flat_disp]` |
| `fc_save_active` path selection | granted | SAVE emits the **`rt_cap_push/pop/top` C path** |
| flat prefix sum (`fc_leaf_disp`) | port-blind, counts the cell | offsets assume a carve that never happened |

Asm diff confirms all of it: FORTH `sub rsp,16` / `[rsp+0]` / `[rsp+8]` / `add rsp,16` becomes HEAP carve + `[rsp+16]` / `[rsp+24]` and **no pop**; SAVE's inline `mov [rsp+48], r14d` becomes `lea rdi,[rsp+224]; call rt_cap_push@PLT`.

⭐ **AND THE BLOCK BASE IS DROPPED ON THE FLOOR.** The carve emits `mov rax, rbx` and **the very next instruction overwrites `rax`**. Nothing parks it. So today port 7 allocates a heap block per box and never once addresses it — s205's "allocation-only" is exactly right, and the reason is one unparked register.

---

## 3. TRIED AND REVERTED (with measurements) — "KEEP THE CELLS, ADD THE CARVE" IS NOT THE PROVING CONFIGURATION

`ZC_PORT_HEAP`'s own header claims: *"the pops stay silent and the locals stay FLAT-FRAME … the PROVING configuration: frontier arithmetic + slow refills exercised corpus-wide, semantics untouched."* **That claim is false as written** — the pops went silent but the port-blind accounting did not, which is §2.

**EXPERIMENT.** Introduce ONE cell-residence predicate `x86_fc_cells() = (FORTH || HEAP)` and route `x86_fc_on` + `x86_fc_hit` through it, so grant and emission cannot drift: cells on rsp exactly as FORTH, PLUS the heap carve — semantics identical, allocator exercised.

**RESULT: REGRESSION, 3 OK → 0 OK.** All six tripwire programs SEGV under port 7, including the three that previously passed. **gdb: `#0 0x0000000000000000` — a WILD CONTROL TRANSFER, not a data fault**, i.e. rsp imbalance (`ret` into garbage), the α push landing without its matching ω pop.

**WHY, and this is the transferable lesson:** the FORTH cell is **not two instructions, it is a coupled protocol**. The pop lives at the `X86H_JMP`/`X86P_OMEGA` hook (`x86_asm.h:1806`) and reaches conditional-ω exits only through the **`x86_fc_jcc_omega` invert+pop+jmp synth** (gated at :280 on `x86_fc_on()`), with chained trampoline cells folded via `op_wpop`. Turning cells on for a port turns on the push immediately; the ω-side routing has further FORTH-shaped dependencies that do not follow. **Reverted clean (`git checkout`); tripwire restored to 3 OK / 3 SEGV, tree clean.**

⇒ **There are exactly TWO self-consistent configurations, not three.** (a) FORTH: cells on rsp, every consumer agrees. (b) TRUE HEAP RESIDENCE: cells on the heap with FR/FRQ retargeted to the block base. **The intermediate the port header describes does not exist**, because `fc_geom`'s port-blind grant leaks into the flat accounting. Do not attempt it again as a predicate flip.

---

## 4. 🔴 THE BLOCKER IS A REGISTER RULING, AND IT IS STRUCTURAL, NOT A PREFERENCE

`A-1`'s "addressing form unchanged" is **not free and not a spelling change.**

- The addressing contract requires `[ζ_self+k]` where ζ_self "must survive the box's own α→β→γ span." Arbitrary boxes and C calls run inside that span, so **no caller-saved register survives it.**
- All callee-saved are spoken for: **RBX** frontier · **RBP** control-frame base · **R12** capture · **R13/R14/R15** Σ/δ/Δ.
- **A parked handle cannot rescue it: `FR`/`FRQ` return an OPERAND STRING, and x86 has no `[[rsp+k]+off]` double-indirect addressing mode.** A memory-resident ζ_self therefore cannot be dereferenced by any change confined to the operand spelling — it requires an instruction-level reload.

**TWO SHAPES, LON'S CALL:**
- **(A) DEDICATE A REGISTER** to ζ_self. Requires releasing one of the six. Σ (R13) is the natural candidate — constant for a match, reloadable — and is *the same register `RUN B` B-0 already names as the VSP candidate.*
- **(B) RELOAD AT EACH PORT DEFINE** into a scratch, FR/FRQ spelling `[scratch+k]`. Templates stay mode-blind (the port hook emits it, R2-conformant). Cost: any C call inside a box invalidates the scratch, and §3 is the warning that ω-side routing is where these things break.

⭐ **RECOMMENDATION: RULE ON ζ_self AND VSP TOGETHER.** They are one question — two regions needing a base, at most one register to give — and deciding them separately risks spending the last free register on the first one to be implemented. `ZHEAP-6` already says VSP starts as a known global cell behind `x86("vsp_carve"/"vsp_operand")`; the same deferral works for ζ_self **only under (A)**, since under (B) the reload is real code from day one.

---

## 5. CORRECTION TO s205 — THE `@` GATE WITNESS'S EXPECTED OUTPUT MUST COME FROM `sbl`, NOT THE MANUAL

s205 proposed the manual's own worked example as a cheaper gate than ZHEAP-8's. **It is a good gate — but its printed transcript is wrong.**

SPITBOL v3.7 manual p.65–66 shows `'FIX' ? @OUTPUT 'B'` printing `0` `1` `2` then **Failure** (three cursor values). **Measured against the real oracle** (`/home/claude/x64/bin/sbl -b`): `0 1 2 3 Failure` — **four**. SCRIP matches the oracle byte-for-byte in BOTH ports. (The companion `'DOUBT' ? @OUTPUT 'B'` → `0 1 2 3 Success` is consistent with four.)

⇒ **Baking the manual's transcript into a `.ref` would have produced a permanently-red gate against a correct compiler.** The manual's *prose* — *"Cursor assignment is performed whenever the pattern match encounters the operator, including retries. It occurs even if the pattern ultimately fails"* (verified verbatim, p.66) — is sound and still the load-bearing premise for `ZHEAP-7`. The *transcript* is not. Oracle over tutorial, per RULES.md.

**ALSO RE-CONFIRMED AT HEAD:** the `$` capture-START defect s205 reported is live — `'ABCDE' ARB $ OUTPUT 'E'` yields `A/AB/ABC/ABCD` where `sbl` yields `⟨null⟩/B/BC/BCD`. Every START is 0 instead of 1; counts and END cursors correct. So `$` remains unusable as a gate witness and `@` (oracle-derived) is the right one.

---

## 6. NEXT RUNGS IN ORDER

(a) ⛔ **LON RULING — ζ_self register, jointly with VSP** (§4). Everything in clause (1) is behind it.
(b) **After the ruling: FR/FRQ heap retarget** — ONE predicate (`x86_fc_cells`-shaped, the §3 experiment's *form* was right even though its *content* was falsified), and the ω-routing census FIRST this time (`x86_fc_jcc_omega`, `op_wpop`, `fc_save_active`), not after.
(c) **`fc_geom` port-awareness** — whatever the ruling, the port-blind grant vs port-gated consumption in §2 must become ONE decision. That is the actual defect; the SEGV is its symptom.
(d) **ZHEAP-6 mmap value stack** — unblocked independently of (a) only if VSP stays a global cell.
(e) `$` capture-START (MARKER-CAPTURE) — pre-existing, blocks the natural ZHEAP-7 witness.

**NOT DONE THIS SESSION:** watermark not re-proven (no emitter change survived; the only landed edits are the driver + runtime setter, and default-port `.s` byte-identity was verified instead). No `.s` artifact regen — handoff step 4 not triggered, since `cca948c5` touches neither `emit.cpp`/`emit.h`/`src/templates/*` nor `lower_snobol4.c`.

---

## 7. LATE MEASUREMENT (same session) — 🔴 MODE-3/MODE-4 DIVERGE ON PORT 7, AND THE DEFECT IS A **FAMILY**

Verifying §1(a)'s mode-4 claim end-to-end (it was asserted from the `.s` bake, never run) produced NEW information that changes the diagnosis.

**MEASURED.** `--zeta-port=heap`, `.s` → `gcc -no-pie` + `libscrip_rt.so`, `-O0`:

| program | m3 (`--run`) | m4 (linked binary) | bake present |
|---|---|---|---|
| `t1_nomatch` | rc=0 | rc=0 | yes |
| `t4_len` | **rc=139 SEGV** | **rc=0, output `ABC` (CORRECT)** | yes |

**The mode-4 binary really is in port 7** — `SCRIP_ZETA_TELEM=1` prints `[ZETA] port=7`, which ALSO confirms the `cca948c5` clamp fix is live in the `.so` (pre-fix it would have printed 6). So this is not a stale-artifact illusion.

⇒ **`GOAL-MODE34-IDENTICAL.md`'s 1:1 correspondence is BROKEN on port 7**, and in the surprising direction: the *standalone* mode is correct and the *in-process* mode crashes. Since the emitted code is byte-identical modulo the bake, the differing variable is **process/workspace state**: m3 runs the heap-carved code inside the compiler process (workspace already populated, `RT_WS_TOP`/`RT_WS_LIMIT` mid-flight), m4 in a fresh process. **⇒ the SEGV is plausibly workspace-INITIALIZATION-dependent, not purely a codegen displacement bug.** That is a different hypothesis from §2 and it is cheap to separate: run m3 on port 7 with a forced-fresh workspace, and re-check whether `rt_cap_push`'s slot is garbage because it was never written or because the frontier moved under it.

**⭐ AND THE UNIFYING DEFECT — THIS IS A FAMILY, NOT THREE COINCIDENCES.** `rt_zeta_cstack()` (`zeta_alloc.c:270`) reads
`return (rt_zeta_port_mode() == ZC_PORT_CSTACK || rt_zeta_port_mode() == ZC_PORT_FORTH) ? 1 : 0;`
— **HEAP(7) is omitted**, exactly like the setter clamp (§1a) and exactly like the `x86_fc_*` gates (§2). Three sites, one disease: **port predicates that ENUMERATE PORTS BY NAME and were never revisited when `ZC_PORT_HEAP` was added.** Each fails SILENTLY (clamps, or answers "not a stack port"), and each makes the runtime disagree with the emitted code.

**⇒ REVISED NEXT RUNG, AHEAD OF (c): CENSUS EVERY PORT PREDICATE.** `grep -rn 'ZC_PORT_' src/` and classify each site as (i) correctly port-specific or (ii) a stale enumeration missing HEAP. Do this BEFORE the ζ_self ruling is implemented — otherwise the register work lands on a runtime that still disagrees with it in an unknown number of places, and the next SEGV will be misattributed to the addressing change. This census is rulings-free and is now the cheapest high-value act on the ladder.
