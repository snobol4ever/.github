# FINDING 2026-08-13g — CLAUDE-OP5 — THE RTCC VENEER IS CATEGORIZED, THE CLASSIFICATION SURFACE IS EXHAUSTED AT 13 OF 38, AND FOUR OF MY OWN INSTRUMENTS WERE DARK BEFORE ANY REAL WORK STARTED

**Session:** s65 · GOAL-RBP-EARN · Claude Opus 5
**Landed:** SCRIP `cf3f1cd9` `d29fd3c8` `d105701b` `bffceb60` + feature regen `ea8301e9` · corpus `2621469a` `21a1b9e6` · .github `78c2389d` `4438be87` `e2fc3184`
**Lon directives, verbatim:** *"This line `mov rax, qword ptr [rip + g_rtcc_block@GOTPCREL]` is too long. shorten the name and make it a generated static versus a RT, runtime, global."* · *"DO NOT do the dance when the rt_* routine is an ASM optimized by RTX GOAL. We have several that are PURE ASM. So categorize and do not do what is unnecessary."* · *"So make the ones that can be unconditional. Are you saying some are half and half solutions with combo ASM and C? If a C has an ASM counter part. Then DELETE the duplicate C code."*

---

## 1. THE BLOCK IS GENERATED-SIDE WITHOUT BEING A SECOND BLOCK — COPY RELOCATION IS THE MECHANISM

`g_rtcc_block` → `rtccb`, and TEXT drops `@GOTPCREL` to address each slot straight off rip.

```
was   mov rax, qword ptr [rip + g_rtcc_block@GOTPCREL]     85 cols, 4 insn in / 5 out
      mov qword ptr [rax + 40], r8
now   mov qword ptr [rip + rtccb+40], r8                   46 cols, 3 insn in / 4 out
```

**A LITERAL generated static would have been the wrong answer and would have rebuilt the H2 SIGSEGV class.** The C runtime reads and writes this block from six places (the `rtcc_init` R9/`RT_GVA_VA` seed, `rtcc_load_scratch`, `rtcc_load_all`, the coexpr save/restore memcpy pair, the ANCHOR companion writes, and four hand-written inline-asm sites in `rt.c`/`runtime_eval.c`). Give the generated program its own block and C and generated code disagree about where `RT_GVA_VA` lives — which is precisely the failure documented above `x86_rtcc_wb_bin`.

In a `-no-pie` link a reference to a `.so`-defined object makes the linker emit a **COPY RELOCATION**: the 256B is allocated in the *executable's* `.bss` and every module — including the `.so` — is rebound to it. Generated-side storage, one block, no source change on the runtime side beyond the rename.

**VERIFIED BEFORE BEING CHOSEN,** on a faithful reproduction of the mode-4 link (`-no-pie` exe + `.so`, matching Makefile:389): block resolves at `0x404040`, inside the exe image; exe writes slot 7 → `.so` reads `12345`; `.so` seeds slot 6 → exe reads `0xC0FFEE`. Both directions, before a line of tree code changed.

BINARY untouched: mode 3 JITs into a slab that can sit >2GB from the `.so`, so it keeps `movabs`. That is the already-sanctioned R10 RO-load divergence, not a new one.

**Second-order effects worth knowing:** no base register means the veneer no longer clobbers `rax` in TEXT, and the *"restore r11 LAST"* ordering constraint in the reload is gone. `rax` surviving in TEXT but not BINARY is not a new divergence — BINARY already clobbered it, so any template depending on `rax` across a crossing was already broken in mode 3.

---

## 2. THE ANSWER TO "ARE SOME HALF AND HALF?" IS YES, AND IT IS THE MAJORITY

Of 38 RTX asm entries: **15 self-contained · 20 fast-path-asm-plus-cold-delegate · 3 trampolines by shape.**

`rt_add` is the archetype of the middle class:

```
rt_add:  int+int   → lea rdx,[rsi+rcx]; mov eax,DT_I; ret     ← asm
         real+real → addsd xmm0,xmm1;   mov eax,DT_R; ret     ← asm
.Ladd_slow:  jmp c_rt_add          /* everything else */      ← C
```

**For those twenty the C twin is the COLD PATH, not duplicate code.** Deleting it is a cliff, not a cleanup. The delete only applies where the asm is complete, or — in six cases — where the *asm* was the duplicate half:

```
rt_gen_get_fb:  RTX_GATE(icngen, c_rt_gen_get_fb)   /* RTX disabled: jmp C twin */
                jmp c_rt_gen_get_fb                 /* RTX enabled: also C twin */
```

Both arms to C. The file's own comment says why — *"No asm shortcut: reading g_pcall (a C struct pointer) requires the C body. Always delegate."* Those six bought a compare, a branch and a PLT hop to land exactly where a direct call lands. Deleted; twins renamed back to the public names.

**KEPT ON PURPOSE:** `c_rt_faildescr` and `c_rt_is_truthy`. `rtx_unit_test.c` calls both *differentially* against their asm — they are the equivalence oracle, not dead duplication, and deleting them deletes the only mechanical proof the two implementations agree. Lon's call whether they go and the test with them.

---

## 3. DELETING THE GATE IS WHAT MAKES THE CATEGORIZATION SOUND — IT IS THE ENABLING STEP, NOT A CLEANUP

I raised a blocker in-chat before starting: 18 of the 19 routines I had (wrongly, see §4) classed as state-neutral opened with `RTX_GATE(fam, c_rt_*)`, whose OFF arm tail-jumps into the C body. While that arm exists, **register discipline is a RUNTIME property** — `SCRIP_RTX_ARITH=0` flips it — so no compile-time claim about it can be sound, and skipping the veneer would reintroduce the H2 class in a new place. I proposed a preserving shim on the gate-off path.

Lon's answer — *"make the ones that can be unconditional"* — dissolved it. Delete the gate and the ambiguity is removed at the source rather than worked around. The shim was unnecessary.

⇒ **`x86_rtcc_clob(sym)`**, one authority at the two existing chokes: CLASS N (mask 0) emits no veneer at all · CLASS P emits only the clobbered slots · unlisted defaults to `RTCC_C_ALL`, so an unknown or renamed callee **keeps its guard instead of silently losing it**. Killswitch `SCRIP_RTCC_CAT=0`.

⛔ **BINARY ALWAYS ROUND-TRIPS R10 REGARDLESS OF THE MASK.** The mode-3 call stub is `movabs r10,ptr; call r10` — the veneer clobbers r10 *itself*, so `m |= RTCC_C_R10` under `MEDIUM_BINARY`. TEXT calls via `@PLT`, needs no scratch, and honours the true mask. The two media touch different registers and both preserve the same architectural state; the 1:1 contract is behavioural, not instruction-identity, which is already divergent by the sanctioned RO-load rule.

---

## 4. ⛔⛔ FOUR OF MY OWN INSTRUMENTS WERE DARK, AND THREE HAD ONE ROOT

Recorded at length because every one of them produced a *confident, plausible, wrong* number that I reported or nearly reported.

**(a) ASCII census in a tree that names its ports in Greek — three separate failures.**
- `RTX_FUNC\(([A-Za-z0-9_]+)\)` could not see `rt_gen_spine_pass_γ` and `rt_gen_spine_pass_ω`. **2 of 38 entries were invisible to every scan I ran**, and I found them by eye only *after* deleting neighbouring blocks. The self-contained class is 15, not 13.
- `grep -c "\bc_rt_gen_spine_pass_γ\b"` returned **0** for a symbol defined at `rt.c:1319` — `\b` does not close against a Greek suffix. I nearly filed *"the gate referenced a C twin that never existed"* as a latent-bug finding. Caught only by checking `git show` before believing it.
⇒ **USE `grep -F` AND UNICODE-AWARE PATTERNS FOR ANY RTX CENSUS.** Same class as s63's *"a grep over literals is not a census of producers"* — an ASCII-only one is not either.

**(b) Counted `call` into C but not `jmp`.** The cold delegate is *always* a tail `jmp`. That single omission turned 8 state-neutral routines into a reported 19, and a 30% saving into a reported 48%. I gave Lon the wrong number in-chat and corrected it the next turn.

**(c) An Icon board that read all-green.** `rc` was captured after piping into `md5sum`, so every row said `rc=0` when the truth was 139. The STANDING INSTRUMENT RULE caught it. Fixed harness + `hello.icn` as the control row — it references *none* of the changed symbols and fails identically, which is what exonerates the rung.

**(d) A final sweep read 18 PASS / 5 FAIL.** Not reported as a gain: re-running the **same binary** 8 times gives `treebank-array` MATCH on **2 of 8**. The honest board is 17/6. This file already warned the class oscillates `0/134/139` on identical binaries; a single run is noise in *either* direction. ⛔ Any board carrying `treebank-array` must state its run count.

---

## 5. THE GATE — WRITTEN, THEN FALSIFIED BEFORE BEING TRUSTED

`scripts/test_gate_rtcc_callee_class.sh` re-derives the census from `src/runtime/rtx/*.S` and diffs it against `x86_rtcc_clob()`. Three invariants: no listed symbol carries `RTX_GATE` · none exits to a `c_*` twin or `@PLT` · every r8/r9/r10/r11 destination write (incl. `r8d/r8w/r8b`) is in its mask.

Reachability follows local `.L` labels **across `RTX_FUNC` boundaries**, because `rtx_alloc.S` genuinely shares a tail — `rt_str_alloc` falls into `rt_agg_alloc`'s `.Lga_armed`, and a per-block scan reads that body as having no `ret` and misclassifies it as a trampoline. **That is how my own first classifier got `rt_str_alloc` wrong.** An unresolvable jump is UNANALYZABLE and FAILS: the gate refuses to certify a body it could not read.

A gate that has only ever passed measures nothing, so one defect per class was injected and confirmed caught, then reverted: `r11` write into `rt_cap_top` → *writes r11 but mask says r10* · gate back onto `rt_cap_pop` → *carries RTX_GATE* · `jne c_*` into `rt_dcap_end_ok_close` → *exits to c_rt_dcap_end_ok_close*. Green at HEAD, 13/13.

---

## 6. ⭐ THE CLASSIFICATION SURFACE IS EXHAUSTED — DO NOT SEND THE NEXT SEAT LOOKING FOR MORE MASKS

Of 15 self-contained routines, 13 are classifiable and **all 13 are done**. The other two (`rt_list_bang_at`, `rt_pl_dop_unify`) are self-contained but call into C, so they stay CLASS F and keep gate + twin.

The remaining veneer cost is **structural, not a gap in the table**. The heaviest consumers in the demo corpus are `rt_call_arr` (51 sites), `str_concat_d`, `rt_match_ctx_restore`, `rt_dcap_step`, `NV_SET_fn` — all C or mixed. `rt_call_arr` in particular is a thin wrapper over `rt_call_arr_impl`, which dispatches to arbitrary builtins: **its class cannot improve until the entire callee set does**, which is GOAL-RTCC's own thesis (*"we always want protection and C runtime is going away"*).

⇒ The next lever is **reducing the NUMBER of C crossings, not the cost per crossing.** Adding rows to `x86_rtcc_clob()` will not move the board again.

---

## 7. NUMBERS

| | |
|---|---|
| Veneer instructions, 24-demo corpus | ~45.9k → 34.1k (~26%) |
| — from rip-relative addressing | 9 → 7 insn per site (22%) |
| — from categorization | 35707 → 34077 (4.6% more) |
| Offending line width | 85 → 46 cols |
| RTX gates deleted | 12 |
| C twins deleted | 10 (+6 asm trampolines) |
| mode-3 output+rc | IDENTICAL to session baseline, 24/24 |
| mode-4 end-to-end vs `x64/bin/sbl` | 17 PASS / 6 FAIL, set constant by name across 5 measurements incl. a stash+rebuild control |
| Icon 15-row board | unchanged; control row `hello.icn` red = pre-existing crater |

NO NEW GLOBALS: `rtccb` is the same object renamed; the killswitch is a function-local static `getenv` cache, the sanctioned `x86_4col_joinon` kind.

⛔ **OWED AT WRITE TIME: PUSH CREDENTIAL.** 5 SCRIP + 2 corpus + 3 `.github` commits local-only; `handoff_status.sh` reads CHAT SESSION WAITING. Asked in chat, twice.
