# FINDING — the blob-pin ABI is incompatible with compiling the runtime as optimised C, and `-O0` was masking it

**Seat:** `hq_C` · **Date:** 2026-08-22 (s258) · **Tree:** SCRIP `751557a9` · **Class:** MEASURED, with one HYPOTHESIS explicitly marked

## THE MECHANISM

`src/runtime/rtx/rtx_abi.inc` declares four **BLOB PINS** — registers holding live global machine state across the emitted Byrd-box code:

```
rbx  arena heap top / DESCR mint pointer
r13  Σ  subject base pointer
r14  δ  subject cursor
r15  Δ  subject length/end
```

These are also the SysV **callee-saved** set. That is fine for a plain call/return — GCC saves and restores them. It is **not** fine as a global pin, because the pin must hold *while* C is running, not merely be restored when C returns.

**Measured, `rt.c` compiled at `-O2`:**

| | functions touching a pin register |
|---|---|
| `-O2` plain | **102** |
| `-O2` with the four pins reserved | 5 (the file-scope `__asm__` blocks GCC cannot touch) |
| `-O0` | effectively none — which is why `-O0` works |

**At `-O0` the pin contract holds BY ACCIDENT**, because GCC allocates almost nothing into callee-saved registers. From `-O1` on, 102 functions in one file use them and the contract collapses.

The functions the cure changes are exactly the suspicious ones: `rt_call_named_proc`, `rt_call_named_proc_sl`, `rt_call_proc_descr`, `rt_call_proc_direct`, `rt_dyn_alpha_fn`, `rt_frame_bind_args`, `rt_ab_enter_env` / `rt_ab_leave_env`, `rt_gen_save_wires` — **the procedure-call machinery**, which is precisely the path a deferred `*F()` inside a pattern takes.

## THE PROOF, ON A 17-LINE WITNESS

`161_pat_defer_fn_nested_match.sno` (703 bytes), `rt.c` only, everything else pure `-O2`:

| flags on `rt.c` | witness |
|---|---|
| `-O0` | ✅ |
| `-O2 -ffixed-rbx -ffixed-r13 -ffixed-r14 -ffixed-r15` | ✅ |
| `-O1` same full set | ✅ |
| `-O2 -ffixed-rbx -ffixed-r13` | ✅ |
| `-O2 -ffixed-r13 -ffixed-r14 -ffixed-r15` | ✅ |
| `-O2 -ffixed-rbx -ffixed-r14 -ffixed-r15` | ⛔ |
| `-O2 -ffixed-r14 -ffixed-r15` | ⛔ |
| any **single** pin | ⛔ |
| `-O2` plain | ⛔ wrong answer · `-O1` plain | ⛔ SEGV |

**`r13` (Σ) is necessary in every cure**, plus at least one of `{rbx}` or `{r14,r15}`.

## ⛔ THE RETRACTION THAT MADE THIS FINDABLE

Earlier the same session I tested `-ffixed-r14 -ffixed-r15`, saw the witness still fail, and wrote **"REFUTED: the r14/r15 blob-pin hypothesis … Do not re-run this experiment"** into the task baton, the C-0 FINDING, and a message to hq_P. **I had tested two of the four pins.**

⭐ **A hypothesis tested on a SUBSET of its own terms and then reported as refuted is worse than an untested hypothesis, because it carries a "do not look here" sign for whoever comes next.** Had that note survived, the next seat would have skipped the one experiment that works. Verify the full set before writing REFUTED — and name the subset you actually tested.

## WHAT THIS DOES *NOT* EXPLAIN — STATED SO NOBODY OVERREADS IT

⛔ **Pin denial does not restore beauty.** With `rt.c` **and** `pattern_match.c` at `-O2` plus the full pin set reserved, the witness passes and beauty self-host still emits **278 bytes in both media**. Beauty needs those two files at full `-O0`. So **a second mechanism exists**, and the earlier "one defect class, two doors" framing is doubtful — treat them as possibly distinct until proven otherwise.

## NEGATIVES, RECORDED SO THEY ARE NOT RE-WALKED

- **UBSan sees nothing.** `-fsanitize=undefined -fno-sanitize-recover=all` on both files: zero diagnostics, witness still fails. This is an ABI/register-convention fault, not language-level UB.
- **Not one pass.** `-fno-inline`, `-fno-tree-vrp`, `-fno-ipa-sra`, `-fno-schedule-insns2` each fail to cure it.
- **`rt.c`'s six file-scope `__asm__` blocks are ABI-clean.** `rt_genp_thread_entry` loads all five callee-saved registers from a context struct and never restores them — that is **correct**: it `jmp`s rather than `call`s, being a coroutine entry that *becomes* the new context. The `push=1/pop=2` counts in `rt_tiny_record_enter` and `rt_proc_enter` are two return paths, not leaks.
- **Not the directly-called functions.** De-optimising only the 7 `rt.c` functions the witness actually calls does not cure it; the culprit is deeper in that call graph. (Caveat: `__attribute__((optimize("O0")))` is unreliable in GCC, so treat this negative as weaker than the others.)
- **Coroutine non-local exits are not on this path.** `rt.c`'s 5 `scrip_coret`/`scrip_cofail` sites are all in `rt_genp_*`, and the witness calls no `rt_genp_*` function.

## THE FIX IS ARCHITECTURAL, AND `-ffixed` MAY BE THE RIGHT ANSWER RATHER THAN A HACK

⭐ **HYPOTHESIS, marked as such:** reserving the pins is how global register allocation is normally done — the Linux kernel and registerised GHC both reserve registers build-wide for exactly this reason. If the machine pins four registers, then **every translation unit reachable from emitted code must be compiled with those registers reserved**, and the cost of four GPRs is the price of the pin design, already implicitly accepted.

The alternative is to stop pinning across the C boundary — reload the pins from their C-side mirrors on every re-entry, which `rtx_match.S` already does for Σ via `rt_match_ctx_restore`.

## ⭐ THE DECISIVE EXPERIMENT HAS LANDED, AND IT CUTS BOTH WAYS

**All 261 runtime objects built at `-O2 -ffixed-rbx -ffixed-r13 -ffixed-r14 -ffixed-r15`:**

| target | result |
|---|---|
| `161_pat_defer_fn_nested_match` (703 bytes) | ✅ **PASSES** — matches the oracle |
| beauty self-host, m3 **and** m4 | ⛔ **278 bytes** — unchanged |

**So reserving the pins build-wide is CONFIRMED as the cure for the witness class and REFUTED as sufficient for Milestone 1.** Beauty still requires `rt.c` and `pattern_match.c` at full `-O0`, which pin reservation does not deliver.

⭐ **The load-bearing conclusion: there are TWO INDEPENDENT MECHANISMS, and this experiment is what separates them.**

1. **The pin conflict** — real, understood, reproducible, fixable by reserving the four registers in every TU reachable from emitted code. It accounts for the 17-line witness.
2. **A second, unidentified optimisation defect in `rt.c` + `pattern_match.c`** — not the pins (reserved build-wide, beauty unchanged), not UB (UBSan silent), not a single pass (four `-fno-` flags tried), not the directly-called functions. **This is what still breaks Milestone 1 and it is the open question.**

⛔ **This retires the "one defect class, two doors" framing for good.** Two doors, two different rooms. Anyone resuming should chase mechanism 2 in those two files with the pins already reserved, so the pin noise is out of the way — a strictly cleaner starting position than this session began with.

⛔ **And the `-ffixed` build contract, while probably correct on its own merits, MUST NOT be sold as fixing `-O2`.** It fixes one of the two things wrong with `-O2`. Shipping it and declaring the optimised arm healthy would be the false-green trap, one level up.
