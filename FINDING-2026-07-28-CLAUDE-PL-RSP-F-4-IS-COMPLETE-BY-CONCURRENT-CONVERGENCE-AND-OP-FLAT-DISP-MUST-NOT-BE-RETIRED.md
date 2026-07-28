# FINDING 2026-07-28 (s159) — PL RSP-F-4 IS ALREADY COMPLETE AT HEAD BY CONCURRENT CONVERGENCE; `op_flat_disp` MUST **NOT** BE RETIRED

**SCRIP watermark measured:** `0831facc` (unmodified — **zero source changes this session**)
**Build discipline:** full-clean `rm -rf out/ scrip`, `-O0` throughout. No `-O2` (no Lon directive).

---

## 1. HEADLINE — THE RUNG IS DONE, AND NOBODY HAD MEASURED IT

| Instrument | s157 | s158 (claimed) | **s159 MEASURED at HEAD** |
|---|---|---|---|
| Prolog rung suite `--mode interp` | 116/164 | 122/164 | **164/164 PASS, FAIL=0** |
| Prolog rung suite `--mode compile` (mode-4) | 116/164 | 121/164 | **164/164 PASS, FAIL=0** |
| `rung02_facts` (facts + fail-loop) | SIGSEGV | runs, **prints EMPTY** | **`brown`/`jones`/`smith`, rc=0** |
| `rung05` (member/2) | SIGSEGV | **still SIGSEGV** | **`a`/`b`/`c`, rc=0** |
| Icon smoke | — | 12/14 (flagged UNVERIFIED) | **14/14 m3, 14/14 m4** |
| all-lang hello matrix | — | 6/6 | **6/6, ROWS_DRIFT=0** |

Both named residual failures of the s158 cursor are GREEN. The "data plane still reads frame
slots rsp-relative" half of RSP-F-4 **closed itself**.

## 2. ROOT CAUSE OF THE MISREPORT — A CONCURRENCY CONVERGENCE NEITHER SESSION MEASURED

`git log` on `src/templates/x86_asm.h` + `src/emitter/emit.h` gives the true order:

```
c8424718  FLATDISP-1b (s189): delete ZC_FLATDISP; rsp frame base is unconditional   <- the collapse
62aaf9ff  FLATDISP capture/call displacement fixes (s195)                            <- s157's BAD HEAD
8d0665c8  FLATDISP-8 (s197): FRAME BASE FOLLOWS THE RBP PIN                          <- THE GLOBAL REBASE
0831facc  PL RSP/RBP record-protocol (s158): emit_rec_pin/fb/fb_num                  <- HEAD
```

**FLATDISP-8 — the exact "global rebase" the s158 cursor recorded as MEASURED AND REJECTED — was
landed by the PARALLEL SNOBOL4/Icon session, and it landed BEFORE s158's own commit.** s158 tried
the rebase by hand on a tree that did *not* yet contain FLATDISP-8, saw `rung02` regress, correctly
reverted, and wrote "DO NOT RETRY BLIND". At handoff `git pull --rebase` then replayed s158's
commit **on top of** a tree where that same rebase had already landed *with its compensation
correctly gated*. Each session measured only its own half; the combination was measured for the
first time today.

⚠ **THIS IS THE STALE-ORIENTATION DEFECT CLASS FROM `RULES.md`, IN ITS MOST EXPENSIVE FORM.** Not a
prose banner asserting an unknowable push state — a **measurement rendered false by a rebase**. The
number was true when written and false when read, and nothing in the pipeline re-checks it. A
cursor's "MEASURED AND REJECTED" carries no watermark of the tree it was measured on, so a later
session cannot tell whether the rejection still applies.
**RULE PROPOSED: every "MEASURED AND REJECTED" claim must carry the SCRIP SHA it was measured on.**
Without the SHA the claim is unfalsifiable and, under parallel sessions, silently expires.

## 3. ⛔ FALSIFIED — "NEXT: retire `op_flat_disp`" IS THE WRONG NEXT ACTION

The s158 cursor's stated next step was *"retire `op_flat_disp` + rebase FR/FRQ to the pinned rbp in
ONE step"*. **Measured: `op_flat_disp` is LIVE, not dead residue.**

```c
x86_asm.h:360  x86_frame_off(off) = x86_fb_pinned() ? off : off + _.op_flat_disp;
```

Under a pin the compensation is already identically zero; under **no** pin it is the real
displacement. Unpinned graphs still exist and are not rare:

| program | `[rbp+…]` refs | `[rsp+…]` refs | regime |
|---|---|---|---|
| `test/snobol4/hello/hello.sno` | **0** | 4 | **UNPINNED — rsp + `op_flat_disp`** |
| `det.pl` (deterministic Prolog) | 160 | 13 | pinned |
| `rung05.pl` (member/2, gen-proc) | 273 | 8 | pinned |

Retiring `op_flat_disp` therefore means **making the rbp pin universal**, which costs rbp as a free
GPR in every flat/leaf graph — precisely what `x86_asm.h:359` says the unpinned arm exists to
preserve (*"unpinned graphs never touch rbp (free GPR)"*). FLATDISP-8's engineering is correct as
landed: **GATE the compensation, do not retire it.** Retiring it is a separate, optional
register-pressure trade with no failing test to justify it — not the finish of RSP-F-4.

## 4. LATENT SEAM — BANKED, NOT LIVE: THE TWO PREDICATES ARE TWO AGAIN

```c
emit.h:599  emit_jmp_pin_rbp() = flat_deep_arrival || flat_pat || flat_gen      // ALL DATA REFS (via x86_fb_pinned)
emit.h:600  emit_rec_pin()     = emit_jmp_pin_rbp() || g_gen_proc_active || g_resumable_callable_active   // RECORD PROTOCOL ONLY
```

s158's own comment states the principle — *"keeping the two predicates apart is what let the store
and the load pick different base registers"* — and then closes the seam by introducing a **second,
strictly wider predicate**, re-opening the same split one seam over. A graph with
`g_gen_proc_active` true and all three `flat_*` false would name **rbp** in its record protocol and
**rsp + op_flat_disp** in its ordinary frame refs: the identical defect shape as the 44-test SIGSEGV.

**MEASURED NON-DIVERGENT TODAY**, so this is BANKED, not a live bug. `member/2`'s emitted mode-4 asm
is internally coherent — every data ref is `[rbp+…]`, and the β port recovers rsp *as data* from the
pinned frame before dispatching:

```asm
n20_call_proc_staged_β:
        mov   rsp, qword ptr [rbp + 168]
        jmp   qword ptr [rsp]
```

In practice `g_gen_proc_active` implies `flat_gen`, so the predicates coincide. ⛔ **DO NOT unify them
blind** — there is no failing test, the suite is 164/164, and a blind widening of the data-ref base
is exactly the move s158 measured as a regression. What this needs is a **gate that fires when the
two predicates disagree**, converting a latent hazard into a measured one. Unification only after
that gate has been seen to fire.

## 5. INSTRUMENT DEFECTS — CONFIRMED, STILL UNFIXED

1. **`test_prolog_rung_suite.sh` `interp` and `run` arms invoke the identical command** (`$SCRIP --run`).
   "164/164 × 3 modes" is really **× 2 distinct paths** (`--run`, `--compile`). Confirmed again today;
   this session reports only the two distinct arms.
2. **Makefile still has no `-MMD -MP`**, and `clean:` still misses `out/`. Every incremental
   measurement remains untrustworthy; all numbers above are full-clean.
3. **Background builds die between tool calls** — the s126 fragility reproduced exactly: a
   `nohup make &` was gone at the next poll with a 4-line log and no `scrip`. At `-O0` the
   foreground build finishes inside one tool call; **do not detach `-O0` builds, just run them.**

## 6. GATES RUN

- Prolog rung suite `--mode interp`: **164/164** · `--mode compile`: **164/164**
- `test_smoke_icon.sh`: **14/14 m3, 14/14 m4** (resolves s158's unverified cross-language risk, GREEN)
- `test_smoke_compile_hello_all_langs.sh`: **PASS=6 FAIL=0 ROWS_DRIFT=0**
- `test_gate_emit_no_lang.sh`: **OK — lang-blind**
- `test_gate_pl_no_new_global.sh`: **PASS**, doomed-ratchet 14/floor 14 held
- `test_gate_template_medium_invisible.sh --strict`: **FAIL — `xa_flat.cpp(106)`, PRE-EXISTING WIP
  baseline**, unchanged by this session (zero source edits); owned by XA-FLAT-CONVERT.

## 7. NEXT

1. **Makefile `-MMD -MP` + `clean: rm -rf out/`** — now the top blocker; until it lands every
   incremental watermark in this goal file is suspect, and this session is the second in a row to
   pay full-clean rebuild cost for it.
2. **De-duplicate the suite's `interp`/`run` arms** (one line) so the mode count stops lying.
3. **Predicate-divergence gate** for §4 before any unification.
4. `op_flat_disp` retirement is **CLOSED as a next action** — reopen only as a deliberate
   universal-pin register-pressure trade, with the SNOBOL4 unpinned-graph cost measured first.
