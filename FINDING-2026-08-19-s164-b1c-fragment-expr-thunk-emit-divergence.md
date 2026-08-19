# FINDING s164 (HQ, Fable 5) — B1c root cause: the runtime fragment compiler emits EXPR$ thunk BODIES with a different emit-context than the main driver; the `jmp_entry` regime record is RULED OUT as the fix

**Front:** GOAL-SNOBOL4-100 · beauty self-host M1 · wall **B1c** (the last named wall before beauty re-measure; see s163/s162/s161 cursors). SCRIP HEAD `e26dbad4`, corpus `6ec20be6`, .github `56484f4d`, pristine build. Oracle `x64/bin/sbl`.

## The construct (Lon's correction, grounded in beauty)
B1c is a **deferred function call inside an EVAL-built pattern**. beauty's real idiom (beauty.sno:63–67) is `SPAN(...) $ tx $ *match(Functions, TxInList)` — immediate-assign a matched piece to a **deferred function-call target** — and beauty.sno:75 `TxInList = (POS(0) | ' ') *upr(tx) (...)` uses the bare `*upr(tx)` where the fn returns a pattern/EXPRESSION. A bare `*PC()` returning the null string is a degenerate stand-in but reproduces the crash identically (the fn's return type is irrelevant to this defect).

## Minimal repro pair (smaller than the checked-in `b1c_cross_medium_concat_seam`)
```
        DEFINE('PC()')  :(PCe)
PC      OUTPUT = 'PC ran'        :(RETURN)
PCe     P = EVAL("'x' *PC()")    ;  <-- EVAL-built  (fragment medium)  => SEGV
        S = 'x'
        S POS(0) P      :S(Y)F(N)
Y       OUTPUT = 'match'         :(END)
N       OUTPUT = 'nomatch'
END
```
Sibling `m_plain` spells the SAME pattern main-built (`S 'x' *PC()`) and is GREEN. Receipts (oracle vs SCRIP m3/m4):

| witness | pattern | oracle | m3 | m4 |
|---|---|---|---|---|
| `m_plain` | `S 'x' *PC()` (main) | `PC ran / match` | **PASS** | **PASS** |
| `e_plain` | `EVAL("'x' *PC()")` | `PC ran / match` | **SEGV** (prints `PC ran`, dies) | **SEGV** |

The deferred body **runs** in the crashing case (`PC ran` is printed) — the SEGV is on match teardown, both modes, guard-independent. This is the residue of the s161 **D-18** work: D-18 fixed the fragment thunk's *entry* (error 22 → "runs then crashes"); the *exit* was never brought to parity.

## Localization (gdb, `SCRIP_NO_SEGV_HANDLER=1`, pristine `-O0 -g`)
Crash: `rt_defer_get_pat_dtp("*EXPR$0F1")` (pattern_match.c:1135) → `rt_call_proc_descr("EXPR$0F1")` (rt.c:905) → **rip=0x1** after the body ran. A/B on the proc struct at the identical call site:

| witness | thunk | dyn_scope | jmp_entry | result |
|---|---|---|---|---|
| `m_plain` (main-emitted) | `EXPR$0`   | 1 | 1 | clean |
| `e_plain` (fragment-emitted) | `EXPR$0F1` | 1 | 0 | rip=0x1 |

Same call path, same `dyn_scope`; the **only** proc-table difference was `jmp_entry` (1 vs 0). The main driver records it (`rt_proc_set_jmpentry`, scrip.c:1217 m3 / :778 m4); the runtime fragment loop (runtime_eval.c ~231–243) does not.

## ⛔ `jmp_entry` is RULED OUT (tested, negative result)
Added the twin of D-18a's "missing line" to the fragment loop — `rt_proc_set_jmpentry(pname, strncmp(pname,"gram__",6)!=0)` behind `SCRIP_FRAG_JMPENTRY` (default ON). Rebuilt. **`jmp_entry` flipped to 1 for `EXPR$0F1` and the SEGV was UNCHANGED** (m3-ON ≡ m3-OFF, byte-for-byte). Reverted; SCRIP tree is clean at HEAD. `jmp_entry` is a correlated marker, not the causal difference.

## The real divergence — the EMITTED THUNK BODY (ASM-diff, m3, in-memory disasm)
`EXPR$0` (main, works) exits with the clean two-wire tail:
```
  ... jmp *%r10        ; γ success wire
      jmp *%r11        ; ω fail wire
```
`EXPR$0F1` (fragment, crashes) has a structurally different body — loads the wires late via `lea` into internal labels (`lea ..,%r10 # +0xbd`, `lea ..,%r11 # +0x128`), `jmp *%rax`, and a trailing `call *%r10`. r10/r11 at the fault point hold valid in-thunk addresses (`fn+0xbd`, `fn+0x128`), so the wild `rip=0x1` is NOT a bad wire jump — the body reaches a `ret`/transfer whose landing was never seated by the fragment's emit context.

**Cause: the fragment loop's emit-context setup is a SUBSET of the main driver's.** For these role-3 EXPR$/PAT$ thunks the main driver (scrip.c ~1273) additionally:
1. sets **`g_flat_frame_floor`** = `zls_g_region(main)` for `IR_GOTO_DEFERRED`/role-3 graphs (SN4-FLAT-PROC s176) — the fragment loop leaves it 0;
2. emits from **`bb_proc_entry(&proc_table[pi])`**, not the raw `->entry` the fragment loop uses;
3. runs the **`_bare`/`proc_role3_kind`** class logic (kind-2 EXPR$ thunk "owns its own γ/ω wire exits").
One or more of these is what gives `EXPR$0` its correct frame/wire-exit shape; the fragment thunk, emitted without them, lands wild on teardown. This is exactly the "B2 record-protocol in the fragment↔main crossing" s162 named.

## Fix target for the next slice (NOT attempted here — needs full gating)
Bring the fragment proc loop (`src/runtime/runtime_eval.c`) to emit-context parity with the main driver (`src/driver/scrip.c`) for role-3 thunks — start with `g_flat_frame_floor`, then `bb_proc_entry`, then the role-3 `_bare` handling — behind a killswitch. This is **runtime-.so only** (fragment emission), so the corpus `.s` md5s must NOT move; gates: OFF-arm byte-identity, md5 blast radius == 0, the b1c witnesses green BOTH modes, then **beauty re-measure** (expect the Shift/Reduce machine to run → then B2c/m3, per s163).

## ⛔ Secondary defect surfaced, ROUTED not fixed
Main-built `S 'x' $ *PC()` (immediate-assign to a deferred target) returns `match` in m3 where the oracle returns `nomatch` — a **silent wrong answer, no EVAL, no crash**. The witness used a null-returning fn (degenerate `$`-to-null-name), so this needs a faithful witness (fn returning a real EXPRESSION/name) to confirm it is a bug vs a degenerate artifact before routing to a rung. m4 SEGVs on the same witness (the fragment path again). Flagged; not claimed.

## ⛔ UPDATE s164b — `g_flat_frame_floor` parity ALSO ruled out (tested)
Replicated the driver's SN4-FLAT-PROC floor block (scrip.c:1272) verbatim in the fragment loop `eval_thunks_emit_from` (source `main`'s `zls_g_region` for role-3/`IR_GOTO_DEFERRED` thunks), behind `SCRIP_B1C_FLOOR` default-OFF. Rebuilt. **`SCRIP_B1C_FLOOR=1` left every b1c witness SEGV, byte-identical to OFF.** Reverted; tree clean. The CLASS-C/floor discriminator (bb_glue_flat.cpp) is NOT the fragment-thunk teardown fault by itself.

**Two hypotheses now eliminated by test: `jmp_entry` (s164) and `g_flat_frame_floor` (s164b).** The remaining divergence is in the emit PATH, not a scalar flag: the fragment loop calls `emit_chain(g_stage2.bbp.table[idx]->entry, ...)` where the driver calls `emit_chain(bb_proc_entry(&proc_table[pi]), ...)` — SN4-FLAT-PROC s176's own note: *"bb_proc_entry, NOT ->entry — a shared-graph proc must bind its α at proc_entry_node; binding at main's entry made the stub re-run the whole program (the m4 recursion SEGV)"* — and it omits the `_bare`/`proc_role3_kind` role-3 class logic. **NEXT SLICE (fresh context, runtime-.so only, same gates):** disasm `EXPR$0F1` ON-vs-OFF to confirm the floor was applied-but-inert, then bring `bb_proc_entry` + the role-3 emit-path to parity and re-measure the witnesses → beauty.
