# FINDING 2026-07-27j (s196) — SCANBASE LANDED (119→113); FLATDISP-5a's PREMISE IS FALSIFIED

**Session goal:** "Finish RSP/RBP conversion" (Lon). **Outcome:** one small sound ratchet landed, and the
NEXT PLANNED RUNG OF THIS LADDER DISPROVEN BEFORE IT COST A SESSION. The second result is the valuable one.

**Watermark, re-proven fresh at session start AND after the change — HELD EXACTLY:**
m3 PASS=221 FAIL=94 · m4 PASS=219 FAIL=94 SKIP=2 · DIVERGE=1 (W06_tab).
**FAIL SETS BYTE-IDENTICAL before/after** (not just equal counts — membership diffed, zero churn).
Icon 4/0 → 4/0. Census ratchet 119 → **113**, baseline lowered in the same commit per the gate's own rule.

---

## 1. ✅ SCANBASE — the last hardcoded-rbp holdout in the SPD-2 scan prologue

`emit.cpp` scan_live arm emitted its two slot stores as `[rbp + kt-32]` / `[rbp + kt-40]`, hand-written in
BOTH media (TEXT snprintf + BINARY `ef_b3(0x4C,0x89,0x85)`). These run **one instruction after the jmp-entry
prologue's `mov rbp, rsp` seed**, so `rsp == rbp == activation base` by construction — the rbp spelling was
pure pre-U3 residue, the same prose-rot class as the s195 FLATDISP mines. Rebased to rsp, both media.

**R10 defect found and fixed while passing through, not carried across:** the rbp form emitted **disp32
unconditionally**, so it diverged from its own TEXT arm whenever the offset fit in a byte (`kt-40` = 120 in
every blob measured — `as` picks disp8 there). New form selects the as-matching short form. All four
encodings byte-verified against `as`:
`4C 89 44 24 dd` / `4C 89 84 24 dddddddd` (r8) · `44 89 74 24 dd` / `44 89 B4 24 dddddddd` (r14d).

Gain: 2 refs × 3 blob-bearing benchmarks = **6**. Per-program: pattern_bt 25→23, string_pattern 25→23,
mixed_workload 36→34, roman 29 (no PAT$ blob).

---

## 2. 🧱 THE HEADLINE — FLATDISP-5a's PREMISE IS WRONG. A PAT$ BLOB IS NOT PINNED BY CONSERVATISM.

`GOAL-SNOBOL4-BB.md` has carried this rung since s193:

> **FLATDISP-5a — frameless invariant PAT$ blobs** … emit invariant pattern inline, no PAT$ proc, no DT_P
> round-trip — retires pattern_bt/string_pattern's 25s and shrinks the flat_pat conjunct's reach.

and `emit_jmp_pin_rbp()`'s own comment asserts the mechanism:

> TODAY an INVARIANT PAT$ blob (pure LIT/SPAN body, no fence/arbno/defer) is exactly that case;
> FLATDISP-5a (inline invariant patterns, no blob) will make the flat_pat conjunct fire less, never wrong.

**Both sentences are true about SUSPENSION and both are IRRELEVANT to why the blob is pinned.** The pin's
actual cause is the **unanchored scan-retry loop**, and it is INDEPENDENT of alternation, suspension, and
invariance. Ground truth, straight out of the emitted blob:

```
proc_PAT$0_scanfail:
        cmp   qword ptr [rbp + 128], 1
        mov   eax, dword ptr [rbp + 120]     ; attempt start
        inc   eax
        cmp   eax, r15d                      ; past subject end?
        lea   rcx, [rip + g_anchor]
        cmp   qword ptr [rcx], 0             ; &ANCHOR tested at RUNTIME
        mov   dword ptr [rbp + 120], eax
        mov   r14d, eax
        mov   rsp, rbp                       ; <<< UNWIND FROM ARBITRARY CARVE DEPTH
        jmp   proc_PAT$0_attempt
```

This is SPITBOL manual Ch.18, pattern-match algorithm **step 6** verbatim: *"If the stack is empty and
keyword &ANCHOR is nonzero, the entire pattern match has failed. If &ANCHOR is zero, advance the starting
cursor position by one and go to step 2."* Restarting at step 2 abandons whatever ζ cells the failed attempt
carved, at whatever depth it died. **Recovering base from a register is the only way back** — you cannot
read a frame slot to find the frame when rsp is at an unknown depth. That is Lon's BRICK WALL, and the
scan-retry is a **fifth member** of the STATEMENT / FUNCTION / ARBNO / FENCE1 family, not a sixth thing.

**MEASURED, not reasoned — the decisive datum.** Box census inside each blob:

| benchmark | PAT$ blob contents | alternation? | still needs pin? |
|---|---|---|---|
| pattern_bt | alternate assign_cond assign_save lit sequence span | **yes** | yes (suspends AND scans) |
| string_pattern | assign_cond assign_save break lit sequence | **no** | **YES — scan retry** |
| mixed_workload | assign_cond assign_save break lit sequence | **no** | **YES — scan retry** |
| roman | (no PAT$ blob at all) | — | — |

string_pattern and mixed_workload are **exactly** 5a's "invariant" class — alternation-free, built from
BREAK/LIT/SEQUENCE, all single-result per the manual (SPAN takes the longest and does not retry shorter;
BREAK is deterministic; **BREAKX is the one that "can extend past first match"** and ARB/BAL match shortest
then extend — those three are the real alternative-generators, alongside `|`, ARBNO, FAIL, and the deferred
`*expr` forms). Inlining them would **not** free the pin. It would relocate the same retry-from-depth
problem into the caller's frame — i.e. straight into the FLATDISP displacement-mine class s195 just spent a
session clearing.

**&ANCHOR IS NOT STATICALLY KNOWABLE.** The retry arm tests `g_anchor` at runtime. Even an anchored program
emits the loop. So no compile-time classifier can retire it; only a design change to how the retry re-enters
could.

### What IS still available (and what the flag conflation costs)

`flat_pat` currently carries **two meanings welded together**, armed NAME-keyed (`strncmp(pname,"PAT$",4)`),
never property-derived — the same defect shape as the s193 FLATDISP-5b root cause (arming, not kind list):

- **(a) "this is a PAT$ blob"** — read by `scan_live` (emit.cpp). **CORRECT as-is**; the scan loop belongs to
  every pattern blob regardless of suspension. Do not narrow this.
- **(b) "this blob's γ RETAINS"** — read by `emit_jmp_pin_rbp()` and xa_flat's suspend epilogue (446/585).
  **Only (b) is property-dependent**, and only the **EPILOGUE** half of it is still addressable: the
  PROLOGUE SEED must stay for the scan retry no matter what.

So the surviving rung is narrower than 5a and should be renamed: **split `flat_pat_susp` off `flat_pat`,
gate ONLY the retaining epilogue on it** (an alternation-free blob can never be resumed, so its `_res`
landing is dead — ~6 refs/blob + a cheaper epilogue). Estimated ≤12 across the corpus. NOT attempted this
session: it needs the `_res`-reachability question answered first (the landing is referenced only by one
`lea rax,[rip+_res]` into the suspend record in BOTH suspending and non-suspending blobs — so the record is
built unconditionally and who consumes it must be traced before the arm is cut).

---

## 3. 📋 REVISED FLOOR — "finish RSP/RBP conversion" does not reach zero, and here is the accounting

The 113 is four populations behind four different gates, not one:

| population | ~n | gate | reducible? |
|---|---|---|---|
| PAT$ blob internals | 40 | `flat_pat` | **NO** — scan-retry unwind (§2). ≤12 via the epilogue split only. |
| proc `_res` resume landings | 22 | `flat_gen` | **NO** — load-bearing: suspending γ retains with rsp at the deep frontier, resume reads pinned rbp (REG-7 U5 record contract). |
| `main` outer frames | 31 | `xaf_deep()` | Partly — fires from DEFER/ARBNO/FENCE1 in the kind list; DEFER's conjunct may relax IF the epilogue split lands, second-order. |
| roman `nN_match_sequence_af` | 12 | ARBNO family | **DO NOT TOUCH** — same family as the 5 crashers; s195 reverted two fixes here for lack of a map. |
| marshal `mov rcx, rbp` | 4 | — | **NO** — a register read, not a frame ref; the census's own class-D logic would exclude it if it were a load. |

**Honest statement of the end state: ~113 → ~90 is the realistic reach of this ladder, not 0.** Anyone
reading "finish the RSP/RBP conversion" as a drive-to-zero will burn a session against a wall the SPITBOL
algorithm puts there. The frame pointer is not ceremony in these five places; it is how backtracking
recovers its base.

---

## 4. ⚠ PROSE-ROT SWEEP (RULES.md STALE-ORIENTATION (a)) — three docs assert a dead register contract

Orientation for THIS goal routes through docs that are wrong about the exact thing the goal is about:

- **`ARCH-ICON.md`** (mandatory per PLAN.md step 6): *"all `FR`/`FRQ` spellings resolve `[rbp+off]`, no depth
  compensation — REG-7 U3, sealed U5 s87."* **FALSE.** `x86_fr32_prefix()` returns `"dword ptr [rsp + "` —
  rsp-only, and depth compensation is exactly what s195's two mines were missing.
- **`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`** (also mandatory step 6): ζ-frame scratch is `[r12+off]` with the
  `x86_frame_*`/`x86_r12_modrm` vocabulary. **Dead since R12-ERAD s65** (`ZC_FRAME_RSP` default; R12 free).
- **`x86_asm.h:841`** — `FR()`'s own comment says *"rbp is depth-immune"* three lines below the rsp-only
  prefix it calls. Corrected in-place this session at the scan_live site only; the FR() comment still stands.

Not fixed wholesale here (blast radius, 3–4 parallel sessions share these files). **Named so the next
session does not re-derive it from scratch a third time.**

---

## 5. NEXT RUNGS (revised, in order)

- (a) **ARBNO-ELEM dig** — unchanged from s195 and still #1: 5 crashers, roman's 12, and the value-spine
  window addressing must be MAPPED before any fix. Monitor-first per RULES.md.
- (b) **`flat_pat_susp` epilogue split** (§2) — the renamed, honest remnant of 5a. Trace `_res` consumption first.
- (c) **fc_cond FIRST-WINS audit** (carried from s195).
- (d) **SYM-VIS-M3** (carried).
- ~~FLATDISP-5a as written~~ — **RETIRED, premise falsified (§2).** Do not re-plan inline invariant blobs as
  an rbp-reduction measure; if it is ever wanted, it is a call-overhead measure and must carry the scan loop.
