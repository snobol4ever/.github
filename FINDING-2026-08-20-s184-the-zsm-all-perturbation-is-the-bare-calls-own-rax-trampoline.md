# FINDING — s184 (seat3) · THE ZSM-ALL PERTURBATION IS THE BARE CALL'S OWN TRAMPOLINE: `movabs rax / call rax`

**One sentence:** `SCRIP_ZSM_ALL=1` changed the answer of 65 programs (beauty among them) not because of GVA, the optimizer, the stack, or anything the event *does*, but because the s179 reentrancy cure swapped `x86("call")` for `x86("call_bare")` and thereby left the veneer's **protection** behind too — `x86_call_ro`'s BINARY stub is `movabs rax,ptr / call rax`, so **rax is destroyed at the call site, before `rt_zdp_ev`'s own `push rax` can bank it** — and the defect is MEDIUM-ASYMMETRIC, invisible to any asm diff taken in TEXT.

## 1. WHAT THE ROW ASKED, AND WHAT IS ACTUALLY THERE
The row (rank 2, promoted from the s179 "residual perturbation" loose end) recorded that beauty prints `Parse Error` on `m1_min.in` under `SCRIP_ZSM_ALL=1` while the shipped default SIGSEGVs, and suspected "the event call's effect on GVA/optimizer arms exactly as `MONITOR_BIN` does". Reproduced verbatim at session start. **The suspicion is wrong, and measurably so** (§3). Two facts orient everything else:
* **`SCRIP_ZSM_ALL=1` alone is INERT** — the emission site gates on `x86_zdp_rbp_on()` (`SCRIP_ZSM`), so the perturbing arm is `SCRIP_ZSM=1 SCRIP_ZSM_ALL=1`, which is what `util_autobug.sh` exports.
* **`SCRIP_ZSM=1` ALONE DOES NOT PERTURB BEAUTY** (SIGSEGV, byte-identical to default). The delta is exactly the ZSM-ALL widening: `x86_zdp_rbp_frames()` (only boxes that really `push rbp`) → every box's four ports.

## 2. THE WITNESS — MINTED BY MECHANICAL SWEEP, NOT BY ABLATING BEAUTY
Beauty is a bad discriminator: its shipped default is a wild jump through a corrupted continuation (s183), so *any* perturbation moves it. Instead all 896 `.sno` under `corpus/probe` + `corpus/programs/snobol4` were swept default-vs-armed on stdout+rc: **87 diverged**. Classified, the 87 split into two unrelated things that the row's phrasing conflates:
* **22 BOMB** — the instrument's own `rt_bomb` verdicts (a detected FSM/frame violation). Not perturbation; the instrument aborting on purpose.
* **65 PERTURB** — **rc=0 in BOTH arms and a different answer**, i.e. silent wrong answers.

The smallest PERTURB row is 190 bytes, oracle-refed, and is the session's witness — `corpus/probe/b1/b1c_cross_medium_concat_seam.sno`:
```
	DEFINE('PC()')	:(PCe)
PC	OUTPUT = "PC ran"	:(RETURN)
PCe	F = EVAL("'x' . D2 *PC()")
	R = ("" . D1 *PC()) F
	S = "x"
	S POS(0) R	:S(Y)F(N)
```
`.ref` / default: `PC ran` `PC ran` `match`.  Armed: `PC ran` `nomatch` — **one deferred call is lost and the match flips**. Deterministic (3/3 both arms), and NOT stack-address sensitive (`setarch -R` + env padding of 0/3/34 bytes: unchanged).

## 3. WHAT IT IS NOT — FOUR MEASURED NEGATIVES, KEPT SO THEY ARE NOT RE-DERIVED
1. **NOT codegen / not GVA / not the optimizer.** The witness's `--compile` TEXT was emitted both arms, normalised (labels split out, `;` runs split), and the 158 ZSM blocks removed by shape. **Diff = 0 lines.** The armed emission is the default emission with event blocks spliced in and *nothing else changed*. This is the row's own hypothesis, falsified.
2. **NOT a register clobber by the sink.** `rt_zdp_ev` (`src/runtime/rtx/rtx_zdp.S:89`) is hand asm precisely so it can save rax, rflags, r8–r11, rdi, rsi, rdx, rcx and rbp; `rt_zdp_sm_event` is C, so rbx/r12–r15 are callee-saved. Nothing the emitted code uses is left unsaved — **by the sink**.
3. **NOT the stack.** A throwaway knob moved every byte the block writes (and the whole C frame beneath it) down by a tunable guard. Swept **128 / 512 / 4096 / 65536 / 1048576** bytes: **wrong at every depth, including 1 MB.** Stack clobber is ruled out, not argued away.
4. **NOT stdio interleaving.** The armed run of the witness prints exactly **one** stderr line, at exit. Nothing is written during the run.

The same knob run the other way is what named the culprit: **the block MINUS the sink call — same eight pushes, same argument movs, same pops — is CORRECT.** The stack traffic is innocent; the *call* is the whole perturbation.

## 4. THE MECHANISM
`x86_zsm_ev` reaches the sink through `x86("call_bare", …)` → `x86_call_ro` (`x86_asm.h:307`):
```c
if (MEDIUM_BINARY) { code += 0x48; code += 0xB8; code += u64le(ptr); code += 0xFF; code += 0xD0; ... }   /* movabs rax, imm64 ; call rax */
return x86_align_assert() + x86_rec("call") + sym + "@PLT\n";                                            /* TEXT: touches nothing */
```
**The trampoline is the bug.** `movabs rax, imm64` overwrites rax *in the caller's own instruction stream*, before control ever reaches the sink that would have banked it. Three things make this specific and not a general indictment:
* **The veneer path does NOT have this hole, and knows it.** `x86_rtcc_call`'s BINARY stub is `movabs r10,ptr / call r10` and it compensates for its own trampoline (`if (MEDIUM_BINARY) m |= RTCC_C_R10;`), while `x86_rtcc_clob` returns `RTCC_C_ALL` for any unlisted symbol — so the **pre-s179** ZSM event, and the three sibling instruments (`rt_zdp_anchor` / `rt_zdp_origin` / `rt_zdp_probe`, all still on `x86("call", …)`), bank all nine GPRs including rax. **The siblings are safe; they were never on this road.**
* **Every other `call_bare` customer is immune by contract, not by luck.** `rt_num_arith`, `NV_SET_fn`, `rt_call_arr`, the concat sinks — all are REAL calls whose result comes back *in rax*. Clobbering rax is their point. The ZSM event is the only `call_bare` customer contracted to be **invisible** to the program, so it is the only one the trampoline can convict. This is a contract class, not an op filter.
* **It is MEDIUM-ASYMMETRIC.** TEXT emits `call rt_zdp_ev@PLT` and touches no register. Mode 4 therefore *cannot* show this, which is exactly why §3(1)'s TEXT asm diff came back clean while mode 3 was answering wrong. **An asm diff is only evidence about the medium it was taken in.**

**⭐ THE S179 TRADE, NOW VISIBLE IN FULL.** s179 moved the event off the veneer because the veneer banks r10/r11 in the ONE GLOBAL `rtccb` — non-reentrant, and it flipped 52/106 rows. That diagnosis was right and the cure was right. But the veneer was doing **two** jobs, and only one of them was the hazard: it was also the thing saving rax across the trampoline. Escaping the global bank escaped the register protection with it. The residual perturbation was never "elsewhere" — **it was in the cure**.

## 5. THE CURE — FOUR LINES, TEMPLATE-ONLY, BOTH-MEDIUM
`x86_zsm_ev` banks rax itself, **twice**, so the eight-push `rsp mod-16` parity this function's own header requires is unchanged, and the `rdx` addend moves with the pushes (64 → 80) exactly as that header demands:
```
+ x86("push", "rax") + x86("push", "rax")      /* before the existing eight */
+ x86("add",  "rdx", 80L)                      /* was 64L — the pushes and the addend are ONE FACT */
+ x86("pop",  "rax") + x86("pop",  "rax")      /* after the existing eight pops */
```
Pure `x86(...)` encoders (TEMPLATE-ONLY), no `MEDIUM_*` conjunct (BOTH-MEDIUM — in TEXT the bank is merely redundant), **zero new globals**, no new file-scope state, no per-op filter. The whole function is only reachable under `SCRIP_ZSM=1`, so the default arm is unchanged by construction as well as by measurement (§6).

## 6. GATES — MEASURED
* **THE ROW'S DONE-WHEN, BRANCH 1, MET.** `beauty.sno` on `m1_min.in`: default `rc=139`, armed `rc=139`, **stdout md5 identical**. And on the stronger input where beauty actually emits — **beauty self-host, `beauty.sno < beauty.sno`: 259 bytes, md5 `e883e4b862ba`, IDENTICAL in both arms, same rc.**
* **THE SWEEP, RE-RUN WHOLE:** 896 programs, **87 → 23 divergent**, and the class that matters is **PERTURB 65 → 0**. The 22 BOMB rows are the same 22 as before (the instrument's own verdicts; untouched by this rung, and now trustworthy for the first time).
* **THE ONE REMAINING NON-BOMB ROW IS NOT A DIVERGENCE.** `corpus/programs/snobol4/parser/cf_goto_computed.sno` self-diverges **at a fixed arm with no instrument at all** — four default-build runs returned `rc=133, 139, 132, 139`. A hold-the-arm-fixed control was run before the row was dismissed; it is a wild-jump program whose signal varies, and it is noise in both arms.
* **Corpus board (default arm):** **m3 332/5 · m4 325/11 · SKIP 1** — the s183 watermark exactly, m3 fail-set identical by name (`145_pat_left_assoc_via_arbno_fence`, `160_pat_alt_inner_gen_resume`, `175_pat_bal_generator_retry`, `1110_array_1d`, `216_indirect_goto_computed`).
* **`.s` blast radius, default arm: 0 movers / 286 programs** (`probe/passthru` + `crosscheck/patterns` + `demo`), A/B'd by rebuilding the ORIGINAL header and re-sweeping, not by assuming. **Hold-the-arm-fixed control (same original build swept twice): 0** — so the set is deterministic and the diff means what it says.
* **Independent second path:** all five RULES step-4 regen scripts report **`changed=0`** (623 + 22 programs).
* **RE-PROVEN PRISTINE AFTER A REBASE THAT PULLED OTHER SEATS' RUNTIME WORK.** The push rebased onto `47064a1c`, which carried `src/runtime/core/core.c`, `core.h` and `keywords.c` changes from other seats — so `make pristine` + full rebuild + **the whole board and the whole A/B were re-run on the rebased tree**, not carried over: m3 **332/5** · m4 **325/11** · SKIP 1 unchanged, witness correct, beauty IDENTICAL on both inputs at the same md5s. SCRIP `8d7c5917`.
* **Template gates:** BOTH-MEDIUM code sites in `src/templates/bb_*.cpp` = **0** (ratchet ceiling 0); `test_gate_emit_no_lang.sh` OK. The `xa_flat.cpp(8)` informational WIP baseline is pre-existing and untouched (this rung changed exactly one file, `+5 -3`).

## 7. WHAT THIS UN-RETIRES
`scripts/util_autobug.sh` exports `SCRIP_ZSM=1 SCRIP_ZSM_ALL=1 SCRIP_ZSM_RING=1` — the exact arm cured here — so **Lon's automatic bug finder is returned to the M1 hunt**, along with the ZSM ring and the live census. No fencing header and no banner edit were needed: the row's second branch (name the mechanism and fence the instrument off) was not taken because the first branch (cure it) succeeded. The script's *other* caveat is unaffected and still binds: it drives the IPC monitor, and a `MONITOR_BIN` verdict remains a verdict on a different program (RULES ASM-DIFF-FIRST) — the tool LOCATES, it never GRADES.

## 8. NOT CLAIMED
* **The 22 BOMB rows are not investigated here.** They are the instrument convicting programs — several of them *passing* programs (e.g. `b2c/b2c_eval_pat_release.sno`, 129 bytes, oracle `match`, which the armed arm kills with `ZSM β node=… FRAME LOST`). Whether each is a real law-0b violation or a further instrument over-reach is a separate row; s179's ruling ("an instrument that convicts passing programs cannot testify about failing ones") says that question is now the *next* thing standing between ZSM-ALL and a trustworthy census.
* **The three sibling instruments were read, not swept.** `rt_zdp_anchor` / `rt_zdp_origin` / `rt_zdp_probe` are proven safe from *this* defect by the `RTCC_C_ALL` default (§4); they still carry the s179 global-`rtccb` reentrancy hazard, which this rung does not touch.
* **`x86_call_ro` was NOT changed.** Its rax trampoline is correct for every real call (rax is the return register); the hole exists only for a caller that must be invisible. Widening the fix into `x86_call_ro` would move bytes corpus-wide for no correctness gain.
* **Beauty's SIGSEGV is not fixed and was never this row's target** — it is the pass-thru continuation defect named by the s183 seat1 cursor. This rung only makes the instrument stop lying about it.
