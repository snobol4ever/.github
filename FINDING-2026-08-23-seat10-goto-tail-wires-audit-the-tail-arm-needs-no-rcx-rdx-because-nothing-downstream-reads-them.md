# FINDING seat10 — GOTO-TAIL-WIRES-AUDIT: THE SCRIP_GOTO_TAIL ARM'S MISSING rcx/rdx IS PROVEN SAFE, NOT A LATENT BUG — AND A SEPARATE, ARM-INDEPENDENT CRASH WAS FOUND ALONG THE WAY

**Session:** seat10 (`/home/claude10`, Claude Sonnet 5) · **Date:** 2026-08-23 · **Queue row:** `goto-tail-wires-audit` (rank 2)
**Tree:** corpus additive only (`corpus/probe/igt/igt_computed_goto_falloff.{sno,ref}`). No SCRIP code changed — this row closes as PROVEN SAFE, not as a fix.

---

## 1. THE ROW'S QUESTION AND THE ANSWER

The row (seat3 s190, deliberately not taken when landing `beauty-return-pair-shift`): `IR_GOTO_DEFERRED`'s `SCRIP_GOTO_TAIL` arm (`bb_goto_deferred.cpp:24-39`, default ON) resolves a computed goto's target at runtime and **tail-jumps** straight to it (`add rsp, op_zgpop; jmp rax`) instead of `CALL`-ing into a nested activation the old way. That tail-jmp supplies no `rcx`/`rdx`. The old arm's replaced `rt_chain_enter` path *did* wire `rcx`/`rdx` (as the nested chain's own γ/ω landing pair) before entering the transferee. Question: is the tail arm's omission safe for a transferee that never reaches `:(RETURN)` at all, but simply runs out of statements ("falls off its end")?

**Answer: SAFE, by construction, and provably so — not merely untested-and-lucky.**

## 2. WHY, STRUCTURALLY (not just empirically)

`x86_return_floater()`/`x86_freturn_floater()` (`x86_asm.h:1760-1769`, `x86_srf_floater`) — the RETURN/FRETURN mechanism every `:(RETURN)` compiles into — load their landing address from a **fixed stack slot**:
```
rcx = qword ptr [rsp + 16]      # NOT the live rcx register
rsp = qword ptr [rsp + 8]
rsp += 32
jmp rcx
```
That slot is populated once, at **CALL time**, by the procedure's own entry sequence (`f_α`, which saves its incoming call-descriptor-derived `rcx` to `[rsp+32]` — see `bb_define.cpp:527`'s frame-contract comment, "RESTORE4 rederives rcx=K and r8 from rsp"). RETURN's correctness therefore never depends on whatever the *live* `rcx`/`rdx` registers hold at the moment some *interior* computed goto fires — it was already "correct for a RETURN exit" not by luck but because RETURN doesn't consult live rcx/rdx at all.

The complementary half: a transferee that reaches no explicit transfer at all "falls off" onto whatever the compiler wired **at compile time** as that statement's γ continuation — a plain, unconditional `jmp` to either (a) the next statement's box (which builds its own operands from literals/named-values, never consuming ambient rcx/rdx), or (b) at the true end of the compiled statement list, `jmp main_γ`, which is `xor edi,edi; call exit@PLT` — zero register reads. Byrd-box continuations are static, compile-time-wired jumps (CLAUDE.md's own architecture note), not runtime register-mediated dispatch, so there is no site downstream of a "falls off the end" landing that could read a wire the tail arm never supplied.

## 3. EMPIRICAL CONFIRMATION — THREE WITNESSES, ALL OF-COURSE-IT-MATCHES BUT WORTH HAVING

Constructed and diffed against `/home/resources/x64/bin/sbl -bf` (live oracle, verified alive first):
1. Mainline goto to a label with no `:(...)`, falling through to the next mainline statement — MATCH.
2. From inside a **normally CALLed** activation (`f('ADD')`), an internal computed goto to `LADD` (no `:(RETURN)`) falling through first to another mainline statement, then off the true end of the program — MATCH, both `SCRIP_GOTO_TAIL=1` (default) and `=0`, and in mode-4 (compiled, linked, run). **Checked in** as `corpus/probe/igt/igt_computed_goto_falloff.{sno,ref}` — this is witness (2), the sharpest of the three and the one that mirrors the existing `igt_computed_goto*` family's shape (proc entered normally, computed goto internally) with the one deliberate difference being the *absence* of `:(RETURN)`.
3. Regression lock re-verified: `igt_computed_goto_end.sno` (the NULL-resolve/`main_γ` fallback landing) and the whole `igt_*` family plus `216_indirect_goto_computed` all still PASS. Broad crosscheck corpus re-run: **355/357 m3, 353/357 m4**, identical to the pre-existing baseline — the 2 fails/skips (`160_pat_alt_inner_gen_resume`, `demo_treebank`, `132_pat_fence_eps_recur_shallow`, `demo_porter`) are named, pre-existing, unrelated (see `GOAL-SNOBOL4-100.md`'s `blob-resume-refusals` lane and the `vlist-expr-alternation` row). Zero new reds.

## 4. ⭐ A DIFFERENT, ARM-INDEPENDENT DEFECT FOUND ALONG THE WAY, NOT FIXED HERE — NOT MINE TO CHASE

While probing the boundary I tried a computed goto landing **directly on a `DEFINE`'d procedure's own primary label** (`f`, not an internal label like `LADD`) from outside any call — i.e. `X = 'f'` then `:($X)`. This is a materially different shape from "falls off its end": `f_α` (the procedure's real entry, unlike an ordinary internal label) reads its **incoming** `rcx` as a live pointer to a call descriptor (`{nargs, gamma, omega, args_ptr}` — see `f_α`'s `mov rdx, [rcx+0]` in the compiled `.s`, consumed with no prior local write), and nothing sets that up when you goto straight to it.

Result: **oracle** prints the label's own output then cleanly reports `ERROR 242 -- function return from level zero` and exits 0 (SPITBOL detects there is no real call level to return from). **SCRIP segfaults (rc=139) — identically under both `SCRIP_GOTO_TAIL=1` and `=0`.** Since both arms crash the same way, this is **not** the tail arm's doing and **not** this row's scope — it's a pre-existing gap (no bounds-check on RETURN's frame, or no error-243-equivalent path) that predates the s190 fix entirely. Witness kept only as a scratch file (`falloff_procentry.sno`, not checked in — it is a crash reproducer, not a green control, and doesn't belong in `corpus/probe/igt/` per that directory's GREEN-controls convention). Flagging for HQ to triage into its own row rather than freelancing a fix here — plausibly related to the already-open `setexit-write-only-stub` row's "no error-recovery mechanism in the engine at all" diagnosis, but I have not verified that connection.

## 5. SCOPE / WHAT WAS NOT DONE

No code in `src/` changed — `bb_goto_deferred.cpp` is untouched, so none of RULES.md's codegen-touched handoff steps (the `util_regen_*` chain) apply. `corpus no worse` verified directly (§3) rather than inferred.
