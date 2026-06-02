# HANDOFF — SNOBOL4 BB x86() template-revamp V4: ABORT + TAB + ATP converted, x86_movimm32 added

**Author:** Opus 4.8 (third developer). **Date:** 2026-06-02. **Repo tips after this session:**
SCRIP `origin/main` = `52daa2e`; `.github` = the commit carrying this file.

Continues the x86()-self-encoding revamp (V1, V2-NO-PBB, V3-KEYSTONE-POS-SPAN). This session converts three
loop-free leaves — **ABORT**, **TAB/RTAB**, **ATP (@var)** — and adds ONE new encoder (`x86_movimm32`).
No looping/variable-length work this turn; the keystone (`a1779e6`/`30e8422`) was already in place.

---

## 1. What landed (all on SCRIP `main`, code repo pushed first per RULES.md)

### `bb_pat_abort` — `66eb967` (TRIVIAL, loop-free)
Whole x86 arm is `x86("jmp",PORT_OMEGA) + x86("def",PORT_BETA) + x86("jmp",PORT_OMEGA)`. ABORT
unconditionally fails the match (SPITBOL Manual ch.18). pBB-free; prototype + dispatch parameterless.
Verified mode-3: a pattern hitting ABORT fails (`S ABORT = "X"` → F branch taken).

### `bb_pat_tab` — `66eb967` (loop-free, like POS)
TAB(N): `cmp r14d,N / jg ω / mov32 r14d,N / jmp γ / def β / jmp ω`.
RTAB(N): `mov ecx,r15d / sub ecx,N / cmp r14d,ecx / jg ω / mov r14d,ecx / jmp γ / def β / jmp ω`.
On the ratified registers δ=R14d / Δ=R15d (legacy `[r10]` cursor cell + `lea[rip+Σlen]` bake GONE).
RTAB distinguished by `sval[0]=='r'` (NOT `ival!=0` — that misclassifies RTAB(0)/TAB(N>0)).
Semantics matched to the mode-2 oracle (`bb_exec.c` IR_PAT_TAB): target = N (TAB) | Σlen−N (RTAB);
FAIL (→ω) if δ > target; on success advance δ=target; β fails restoring δ.
**mode-3 == mode-2** verified for TAB(2), TAB(0), RTAB(2), RTAB(0), and the cursor-past-target failure
path (`LEN(3) TAB(1)` and `LEN(3) RTAB(4)` both correctly fail).

### `bb_pat_atp` — `52daa2e` (loop-free, single-shot, X86-only)
@var cursor capture. α writes δ to the variable via `rt_at_cursor(varname, δ)` then → γ; β fails → ω
(single attempt, like a leaf POS). x86 arm:
`mov esi,r14d / lea rdi,[rip+varname] / push r10 / push r10 / call rt_at_cursor / pop r10 / pop r10 /
jmp γ / def β / jmp ω`. Cursor δ from R14d (REG-3). Varname is RO via `x86_load_ro` (lea[rip] TEXT /
movabs BINARY); call via `x86_call_ro`. Double `push/pop r10` guards the side-effecting NV_SET print
path (clobbers caller-saved r10) AND keeps rsp 16-aligned. varname = `_.op_sval` — identical to the
`op_name1` the driver fills for IR_PAT_ATP (`emit_bb.c:1570`), so no neighbor read. Other backends
already stubbed; only the X86 arm exists. **mode-3 == mode-2** verified: `LEN(3)@P`→P=3,
`@Q LEN(2)@R`→Q=0/R=2, `BREAK(' ')@W` in "hello world"→W=5.

### NEW ENCODER `x86_movimm32` (+ `"mov32"` front-end mnemonic) — `66eb967`, in `x86_asm.h`
32-bit `mov reg, imm32` = `B8+rd` (REX.B when reg≥8); 5 bytes (reg<8) / 6 bytes (reg≥8).
`mov r14d,N` = `41 BE imm32`. Byte-verified vs `as` BEFORE use. **ADDITIVE** — the 64-bit
`x86_movimm`/movabs path (operand-constant loads, e.g. LEN) is untouched. The `mov` (64-bit movabs)
vs `mov32` (32-bit imm) mnemonic split is the R7-sanctioned way to pick immediate width at the call
site; both TEXT arms print `mov reg,imm` (only BINARY differs).

---

## 2. Per-box recipe (followed by all three; matches V3)
1. pBB-free `bb_pat_X_str()` reading `_` (accessors for op_ival/op_sval/nid). x86 arm = an
   `IF(MEDIUM_TEXT, s_1asm(α:)+s_comment(...))` header + a chain of `x86(...)` calls on ratified regs
   δ=r14d / Δ=r15d / Σ=r13. Translate `pBB->X` → `_.X` in any non-x86 arm that remains.
2. Extern `void bb_pat_X(void){ bb_emit_x86(bb_pat_X_str()); }` (no x86_begin/slot_claim — none of these
   three loops or carries ζ-scratch).
3. `bb_templates.h` decl → `(void)`; `emit_core.c` dispatch → `bb_pat_X();` (SNOBOL4-owned lines).
4. Any new encoder → add to `x86_asm.h`, byte-verify vs `as` FIRST (caught nothing this turn — all three
   reused existing encoders except TAB's `mov32`, which was verified clean).
5. `make scrip && make libscrip_rt`; verify semantics by direct `./scrip --run` vs `./scrip --interp`
   (the oracle); run all gates; commit; `git pull --rebase && git push`.

---

## 3. Gate state (GREEN throughout)
- SNOBOL4: m2 **7/7 HARD**, m3 5/6 (`define` lone fail — needs DEFINE registration + a SNOBOL4 call
  frame + RETURN; unchanged this session), m4 0/6 (floor 0 — pending the LOWER four-port-graph wiring,
  NOT "by design").
- PAT-BB rung 18/19 m2 (`053_pat_alt_commit` pre-existing fail). g_vstack **0**. prove_lower2 PASS.
- concurrency invariants OK (FACT RULES byte-identical ×3 — the shared `x86_asm.h` `x86_movimm32` add did
  NOT perturb the byte-identical blocks). Icon smoke 2/2 (no regression from the shared-header edit).
- All three converted boxes: pBB=0, `_.node`=0 (compiler-enforced + grep-clean).

**Parallel-session note:** mid-session a Prolog session pushed `bb_cut` (`ed42331`) and an Icon session
pushed `bb_binop_arith` (`b8db625`). Both touched the SHARED `bb_templates.h` + `emit_core.c`; my
`git pull --rebase` composed cleanly with NO conflict (the divvy-up holds — each session edits its own
boxes on different lines). I rebuilt + re-verified m2/ATP after the rebase before pushing. Build from the
tip; intermediate single-commit checkouts may not reflect the merged shared files.

---

## 4. NEXT STEPS (SNOBOL4 x86() conversion remainder), priority order
Remaining loop-free leaves first, then looping, then variable-length.

1. **`bb_pat_arb`** (183 lines) — a GENERATOR: ARB matches 0,1,2,… chars, re-pumping on β (grows the
   match by one each retry until it would exceed Σlen, then fails). NOT trivial — it has a retry loop, so
   it is closer to SPAN than to the three converted this turn. Read the box + the mode-2 oracle
   (`bb_exec.c` IR_PAT_ARB) for the exact re-pump/fail topology; the matched length is per-activation RW
   state → ζ-frame via `bb_slot_claim` + internal labels (follow SPAN). Cursor δ=R14d, Δ=R15d.
2. **`bb_pat_defer`** (94 lines) — deferred `*expr` evaluation: at match time it evaluates the deferred
   subject expression and matches the result. Read the box + oracle for whether it calls a runtime
   evaluator (RO call, like ATP) or splices a child graph; likely an RO-call leaf if it defers to a
   runtime thunk. Ground in `bb_exec.c` IR_PAT_DEFER before converting.
3. **`bb_pat_break`** (LOOPING) — follow SPAN. Plain BREAK ≈ SPAN with one loop; BREAKX is a TWO-loop
   scanner needing `L(0..3)`. Move z (+ BREAKX z_orig) to the ζ-frame via `bb_slot_claim`. NOTE break
   still legitimately sets `bb_cs_zeta`; decide whether to keep the cset object or switch to raw-sval +
   ζ-frame as SPAN did. (This is the V3 handoff's item #4 — still open.)
4. **VARIABLE-LENGTH (shared define/jmp-pair design — the STILL-OPEN item across all four sessions):**
   `bb_pat_fence` (niladic path trivial `α:jmp γ; β:jmp ω`; pair path not), then `bb_pat_cat`,
   `bb_pat_alt`, `bb_match`. The open question is expressing the driver-supplied pair arrays
   (`g_emit.xa_bb_emit_pair_n/_jmp/_define`) as a runtime-count loop of `D`/`J` records in the `x86()`
   concat. Whoever reaches a combinator first designs this ONCE and records it in
   `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` ("STILL OPEN" section), same as the internal-label item.

---

## 5. Divvy-up (conflict-free; this session = SNOBOL4)
- **SNOBOL4:** abort✅/tab✅/atp✅/pos✅/span✅ DONE; remaining arb/defer (loop-free-ish) + break (looping)
  + cat/alt/match/fence (variable-length).
- **Icon:** bb_iterate, bb_binop_gen, bb_upto, bb_to/to_by, bb_alt, bb_seq, bb_every, bb_suspend,
  bb_succeed, bb_unop (bb_binop_arith landed `b8db625`).
- **Prolog:** bb_builtin, bb_goal, bb_choice, bb_ite, bb_disj, bb_conj, bb_unify, bb_catch, bb_arith
  (bb_cut landed `ed42331`).
- **Raku:** bb_rk_gather, bb_nfa.

Each session edits only its own boxes; dispatch/decl inserts land on different lines; `x86_asm.h` is
shared but additive. `git pull --rebase` before every push.

## 6. Handoff sequence reminder (RULES.md)
Mark GOAL steps `[x]`; update the watermark in the GOAL file ONLY; commit; `git pull --rebase && git push`
(code repos FIRST, `.github` LAST). Build: `make scrip && make libscrip_rt`. ENV: `apt-get install -y
libgc-dev` (core.h / raku_nfa_bb.c include `<gc/gc.h>`).
