# HANDOFF 2026-06-14 — GOAL-PROLOG-BB
## δ/ε port eradication + bounded-determinacy collapse (PL-BB-0, PL-BB-1a)

Author: Claude Sonnet (this session) · with LCherryholmes
Owner goal: GOAL-PROLOG-BB · Track: PL-BB correction ladder

---

## TL;DR

Three Prolog commits landed this session, **all byte-/behaviour-transparent** (GATE-3 held at
m2 114 / m3 91 / m4 91 throughout; GATE-1 5/5/5 hard):

| commit  | what | ladder |
|---------|------|--------|
| `b7272f6` | **Eradicate δ/ε as ports** — only α/β/γ/ω are ports (four-ports FACT RULE) | WRONG-1, port-identity half |
| `58c6d5d` | **PL-BB-0** bounded collapse in conjunction chains (interior bounded boxes emit no β) | WRONG-2, first cut |
| `0494c45` | **PL-BB-1a** extend bounded collapse to callee-clause + query chains; **cut-barrier fix** | WRONG-2, completion |

HEAD = `0494c45`, origin/main in sync, working tree clean. **Stop point is green** — pick up
freely.

The session ended on a **reconnaissance finding that forks the ladder** — see §6 (PL-BB-1b). The
four-ports rule is *already satisfied*; the residual gap to DESIGN is narrow and optional, and
trades codegen quality for letter-fidelity. **That fork is a decision for the owner, not the next
window to assume.**

---

## 1. Green baseline (how to reproduce)

```
cd SCRIP
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh          # GATE-1: 5/5/5 (mode-2 HARD)
bash scripts/test_prolog_rung_suite.sh     # GATE-3: m2 114 / m3 91 / m4 91
bash scripts/test_gate_pl_no_new_global.sh # floor 17, doomed-ratchet 17/17
```
Cross-language (shared spine — must stay green after any emit_bb.c / emit_globals.h / x86_asm.h
touch): Icon smoke 12/12/12, SNOBOL4 smoke 7/7, Raku smoke green (observed PASS=31 across
interp/run/compile; a mode-4 tail showed 35 — suite size varies, just confirm all-PASS).

**Regression-isolation technique** (used this session, recommended): when a count drops,
```
VERBOSE=1 bash scripts/test_prolog_rung_suite.sh --mode compile 2>&1 | grep '^FAIL' | sort > /tmp/now.txt
git stash && make -j4 scrip >/dev/null && make libscrip_rt >/dev/null
VERBOSE=1 bash scripts/test_prolog_rung_suite.sh --mode compile 2>&1 | grep '^FAIL' | sort > /tmp/base.txt
git stash pop
comm -13 /tmp/base.txt /tmp/now.txt   # the NEW failure(s), pinned in one step
```

---

## 2. WRONG-1 (port-identity half) — `b7272f6`

**Where δ/ε came from:** they were a 5th/6th port (`X86P_DELTA=4`, `X86P_EPSILON=5`,
`PORT_DELTA/EPSILON`, `lbl_δ/ε`) — a four-ports FACT RULE violation. The recon finding:
**δ/ε were never a control concept.** They were two *driver-staged destination slots* that three
boxes reuse because one template body serves multiple aspects and must name a jump/call target
that is not its own α/β/γ/ω:
- `bb_cell_call` / `bb_cell_findall`: closure **call** (callee α) and **resume** (callee β);
- `bb_cell_ite`: the then/else **arm entries**;
- `bb_callee_frame` / `bb_query_frame`: aspect-selected **redo/advance** targets.

DESIGN §0 law 2 already says these are "a call opcode's target" and "`closure.Resume()`", **not
ports**.

**Fix (byte-identical):** neutralised the port identity, kept the slots as honest staged targets.
- `x86_asm.h`: deleted `X86P_DELTA/EPSILON` from the port enum; deleted `PORT_DELTA/EPSILON`
  macros; deleted the `0xB4`/`0xB5` arms from `x86_port_of` (those bytes are no longer decoded as
  ports); deleted the δ/ε arms in `x86_portname`/`x86_portlbl`. Added `X86T_TGT0=4`/`X86T_TGT1=5`
  (**ids, not ports**) + `x86_jmp_tgt` / `x86_jcc_tgt` / `x86_call_tgt` emitters +
  `x86_label_for` resolves id 4→`lbl_t0_p`, 5→`lbl_t1_p`. The emitted record stream is the SAME
  `J\x04`/`J\x05` → same `bb_label_t*` → same rel32 → identical bytes.
- `emit_globals.h`: `lbl_δ/ε(_p)` → `lbl_t0/t1(_p)`.
- `emit_bb.c`: 13 staging sites renamed (same labels staged).
- `bb_cell_call`, `bb_cell_findall`, `bb_cell_ite`, `bb_callee_frame`, `bb_query_frame`: jump/call
  the staged target via the new helpers, no Greek-port string.

**Justified survivors (DO NOT touch — not δ ports):**
- `TEMPLATE_ADDR_DELTA` (`xa_flat.cpp`) = `&Δ`, the subject-string **length** global (capital Δ,
  the string-language register).
- `DELTA_LOAD` (`xa_bb_macro_library.cpp`) = subject-**cursor** load macro (`mov eax,[r10]`).

---

## 3. PL-BB-0 — bounded collapse, conjunction chains — `58c6d5d`

Determinacy is now first-class in the GZ chain wiring (mirrors JCON `/bounded`, DESIGN §0 law 1:
"bounded ⇒ no β chunk").

- `gz_node_bounded(IR_t*)` (emit_bb.c): **bounded** unless the op is a genuine generator OR a cut
  barrier — see §5 for the exact class (the cut entry was added in `0494c45`, §4).
- **Half A (wiring):** in `gz_emit_chain`, a goal's failure target skips **back** past consecutive
  bounded predecessors to the first non-bounded predecessor's β (or `chain_ω`). The bounded box's
  `def β; jmp ω` was a dead trampoline to exactly that label, so the direct edge is identical.
- **Half B (template):** every `bb_det_*` (23 sites) and `bb_cell_unify` (6 arms) β-tail wrapped
  `IF(!_.op_bounded, x86("def","β") + x86("jmp","ω"))`. `op_bounded` is a **`g_emit` field**
  (compile/emit-time, **NOT a global** — NO-NEW-GLOBAL gate stays green), staged in the chain
  loop as `(bounded && not-last)`.

Verified firing: a 5-goal bounded conjunction emits **0** interior `gzi…_β` labels.

---

## 4. PL-BB-1a — extend collapse to callee + query chains; cut fix — `0494c45`

Same proven `gz_node_bounded` skip-back, applied to the two remaining backtrack-wiring sites.

- **Site 2 (`gz_emit_callee`, clause bodies):** skip-back is **clause-boundary-aware** — a goal
  skips past bounded predecessors only within its own clause (`jj`-relative); the first goal of a
  clause fails to `failtgt`. Each clause's **last** goal keeps its β (it is `redo[c]`, the clause
  resume target).
- **Site 3 (`flat_drive_gz_query`, both segments):** interior bounded goals collapse; here **even
  the last goal collapses**, because `gb[]`/`hb[]` are referenced ONLY by the next goal's fail
  edge (verified) — nothing resumes the query's last goal (the frame β prologue handles top redo).

**Bug caught by GATE-3 and fixed (this is the case for incremental gating):** the first cut of
1a dropped m3/m4 91→90 on **`rung07_cut_cut`** (`differ(X,X) :- !, fail.`). Root cause:
`gz_node_bounded` treated `IR_CELL_CUT`/`IR_CUT` as bounded (default arm), so the skip-back jumped
**over the cut barrier** and `fail`'s backtrack bypassed cut's choice-point pruning. Fix: **cut is
never bounded** — it is a backtrack barrier, same non-collapse class as the generators. This bug
was *latent since PL-BB-0* (conjunction chain used the same predicate) and only surfaced once a
clause-body cut was routed through the collapse; the fix retroactively hardens PL-BB-0 too.

---

## 5. The collapse invariants (internalise before touching the wiring)

`gz_node_bounded` returns **0 (never collapse the β)** for:
`IR_CELL_CALL`, `IR_CELL_CHOICE`, `IR_CELL_FINDALL`, `IR_CELL_ITE` (genuine generators) **and**
`IR_CELL_CUT`, `IR_CUT` (backtrack barriers). Everything else (all `IR_DET_*`, `IR_CELL_UNIFY`,
leaves) is bounded → collapsible.

Which β labels are **kept** (resume targets — must stay defined):
- Conjunction chain (`gz_emit_chain`): the **last** goal's β.
- Callee clause chain (`gz_emit_callee`): **each clause's last** goal β (= `redo[c]`).
- Query chain (`flat_drive_gz_query`): **none required** (last collapses too; β only referenced
  by next goal's fail edge).
- Cut: its β is always kept (barrier).

`op_bounded` is reset to 0 on the ITE-node FILL and the callee/query frame FILLs so it never leaks
into a non-collapsible box.

---

## 6. ★ THE FORK: PL-BB-1b (closure-resume "carried by the frame") — OWNER DECISION

This is the session's main intellectual deliverable. **Read before doing anything on 1b.**

**Recon finding.** The DESIGN (§1.5 lines 124–127, §3 line 277) says: `callee.α` is "a call
opcode's target"; `call.β` is a closure-resume where "the resume entry is the callee's own β,
**carried by `CLO` (its frame)**", and this should "retire the caller-side resume-port notion
entirely."

After `b7272f6`, the **port** notion is already retired: `lbl_t0`/`lbl_t1` are not in the port
enum, not Greek letters, not byte-decoded — they are a call-target and a closure-resume named as
honest staged labels. Behaviourally the frame **is** the closure (frame ptr in `rdi`/`r12`), resume
**does** re-enter via the C call stack to the callee's own β, and the callee β **self-dispatches**
from frame state (`FR(4)` clause index). **All of the DESIGN's semantic intent already holds.**

The ONLY remaining gap to the DESIGN's letter: today `call.β` reaches the callee β via a
**statically-named label** (`x86_call_tgt(TGT1)` → `call <callee_β rel32>`), not via a
**frame-carried address**. Closing it = add a frame resume-IP slot, callee stores its β address at
setup, caller's `call.β` becomes `call [frame+resume_off]`, then `lbl_t1`/`X86T_TGT1` dissolves.

**The honest tension:** that change is a measurable **pessimisation** — an extra frame store per
callee entry + an indirect `call [mem]` (slower, larger) replacing a direct `call rel32` — purely
to relocate a statically-known address into the frame. Behaviour is identical (gates stay
114/91/91); generated code is strictly worse; payoff is fidelity to "carried by the frame" + losing
one staged-target slot. (`lbl_t0`/TGT0 stays regardless — the DESIGN explicitly blesses callee α as
"a call opcode's target".)

**Three options (owner picks):**
1. **PL-BB-1b-min** — do the frame-carried resume for TGT1 only; faithful to DESIGN line 126/277;
   dissolves `lbl_t1`; mild pessimisation.
2. **Declare WRONG-1 closed; amend the ladder** — record that `b7272f6` already satisfied
   "no fifth/sixth port", that callee α/β are a legitimate call-target + closure-resume named as
   honest staged labels, and that the residual `call [frame]` indirection is an *optional fidelity
   refinement not worth the codegen cost*. Then proceed to **PL-BB-5** (§7).
3. **Park** — this handoff is the record; execute 1b-min later with the analysis in hand.

**This session's recommendation: (2).** The rule violation is genuinely fixed; option 1 trades
real performance for letter-fidelity the DESIGN's own "call opcode's target" language already
concedes for α; PL-BB-5 is a better use of effort (an actual score gain off the 91 plateau). But
"carried by the frame" may be load-bearing design intent — that judgement is the owner's.

---

## 7. PL-BB-5 — the clean independent next rung (if fork option 2)

Aggregate `sum`/`max`/`min`. Contained to `bb_cell_findall.cpp` + `unification.c`, independent of
1b. Same `IR_CELL_FINDALL` box already built; add `agg_mode` 2/3/4 + three
`rt_pl_agg_{sum,max,min}_finish` helpers. Expected **+2 rungs**, m3/m4 91→93 — the first move off
the plateau. (DESIGN §3 line 281: findall landed → aggregate → `\+`/once/forall.)

---

## 8. Mechanism map (so 1b/1c doesn't need a re-recon)

**Caller — `bb_cell_call.cpp`:**
- `α`: `rt_enter` (alloc frame) → `mov rdi,rax` → load args (`rsi/rdx/rcx` from cell slots) →
  `call_tgt(TGT0)` (callee α) → `L(0)`: `test eax,eax; jne γ` (success) / `jmp ω` (none).
- `β` (caller redo): `mov rdi,[frame slot]` (frame ptr = closure, in `GZ_CELL_OFF(parts_ival[0])`)
  → `call_tgt(TGT1)` (callee β resume) → `jmp L(0)` (re-test).

**Callee frame — `bb_callee_frame.cpp`** (one body, 5 aspects via `op_sa`):
- `op_sa==0` setup: `push r12; mov r12,rdi`; save args to cells; `rt_trail_mark`→`FR(0)`; if
  multi-clause `FR(4)=1`; `rt_pl_cells_init`; `jmp γ`.
- `op_sa==1`: define `γ` (eax=1; pop r12; ret), `ω` (unwind `FR(0)`; eax=0; pop r12; ret),
  `β` (push r12; mov r12,rdi; if single-clause `jmp TGT0`).
- `op_sa==2`: clause-dispatch cmp-chain — `cmp FR(4), op_off; je TGT0`.
- `op_sa==3`: last-clause redo — `jmp TGT0`.
- `op_sa==4`: clause advance — `FR(4)=op_off`; unwind; `jmp TGT0` (next clause α).

**Frame layout:** `FR(0)`=trail mark · `FR(4)`=clause index · `GZ_CELL_OFF(i)`=cell slots (args +
locals). **No resume-IP slot today** — adding one is exactly PL-BB-1b-min.

**Driver — `emit_bb.c`:** `gz_emit_chain` (conjunction / site 1) · `gz_emit_callee` (clause bodies
/ site 2) · `flat_drive_gz_query` (query / site 3, supports 2-segment findall-style) ·
`gz_node_bounded` predicate · `op_bounded` g_emit flag · `FILL` macro stages
`lbl_γ/ω/β(_p)` before `walk_bb_node`.

**x86 spine — `x86_asm.h`:** port enum = α/β/γ/ω **only**. `X86T_TGT0=4`/`TGT1=5` are staged-target
ids (not ports). Helpers `x86_jmp_tgt`/`x86_jcc_tgt`/`x86_call_tgt`. `x86_label_for` resolves
4→`lbl_t0_p`, 5→`lbl_t1_p`, ports via `x86_portlbl`, ≥6 via internal `L<n>`. TEXT emits the slot
name; BINARY emits `J<id>` for the in-band patcher.

---

## 9. Discipline notes for the next window

- **One box whole per rung, gated green at every step.** No `_v2` forks (FACT RULE: one box, one
  version, edit in place). The δ/ε symbols live in *shared spine* — any change is one atomic
  cross-cutting edit, validated by all-language smoke.
- **Counts are the transparency proof.** A "refactor" that moves m2/m3/m4 is not a refactor —
  back out and find why (the cut bug in §4 is the worked example).
- **m3 ≡ m4 by construction** — they should always match; a split means a medium-specific bug.
- Push order (RULES): code repos first, `.github` last.
- Build/test outputs are large — pipe through `grep`/`tail`; don't re-ingest the object-file
  link line.
