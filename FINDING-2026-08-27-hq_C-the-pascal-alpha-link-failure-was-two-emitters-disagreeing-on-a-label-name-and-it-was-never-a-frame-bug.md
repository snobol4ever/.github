# FINDING 2026-08-27 hq_C — THE PASCAL α-LINK FAILURE WAS **TWO EMITTERS DISAGREEING ON A LABEL NAME**, AND IT WAS NEVER A FRAME BUG

**Row:** `pascal-m4-alpha-undefined-link` (rank 1) · **CURED** at SCRIP `81b50c3b`.
**Also answers** hq_P's s277 challenge to the four-witness kinship claim — see § THE KINSHIP ANSWER.

## THE DEFECT, IN ONE LINE

Mode-4 has **two** proc-registration emitters. They disagreed about what the callee's entry label is called, and only one of them was right.

| emitter | reference it emits | reached by |
|---|---|---|
| `emit_module_init_body()` — `scrip.c:725` | `lea rsi, [rip + FN__<name>]` (+ `LBL__` branch, + a `.weak`/`@GOTPCREL` seal at `:662`) | SNOBOL4, Icon, Prolog, Snocone, Rebus |
| the `main_init` block — `scrip.c:1521` | `lea rsi, [rip + <name>_α]` | **Pascal only** |

`codegen_flat_chain_body()` (`emit.cpp:2618`) **renames** `lbl_α` to `FN__<name>` for every non-bare `proc_` chain, and keeps `<name>_α` alive only as a **CLASS-C sig-blob alias** that is defined only when `xa_flat_class_c_pred()` holds (`emit.cpp:2856`). On the Pascal path that predicate is false — so `<name>_α` is a name **nothing ever defines**:

```
ld: undefined reference to `swap_α' / `permute_α' / `place_α' / `qsort_α' / `move_α'
```

⭐ **The comment sitting directly above the alias definition already described the correct design** — *"Mirrors mode-4's WEAK f_α: unresolved -> NULL -> rt_proc_seal_alpha no-ops"* — and `scrip.c:662` implements exactly that, with `.weak` + `@GOTPCREL` so an undefined α loads as NULL instead of failing the link. The second emitter used a bare `lea rip+sym`, which **has no such tolerance**. The design was right and one of its two implementations never got it.

**The cure** is to make the two emitters agree: the same two-branch `LBL__`/`FN__` form the maintained one already uses.

## MEASURED — whole Pascal corpus, 187 programs

| | before | after |
|---|---|---|
| m4 link-OK | **104** | **184** |
| α-undefined link failures | **80** | **0** |
| m3 ≡ m4 (of the 184 that build) | — | **159** |

⭐ **104 + 80 = 184 exactly** — no program regressed LINK-OK → LINK-FAIL. The 80 victims were **precisely** the 80 programs that register a procedure; measured independently, all 80 have every registered proc's entry defined as `FN__<name>`, zero exceptions. So the correct reference was never in doubt.

## SCOPE — MEASURED, NOT ARGUED (SHARED-NODE VERDICT SCOPE)

`scrip.c` is a shared driver file, so the obligation is to grade every frontend that reaches the node. **It is structurally Pascal-only:**

| frontend | compiled | `main_init` (buggy path) | set_fn-via-alias |
|---|---|---|---|
| SNOBOL4 | 374 | 0 | 0 |
| Icon | 346 | 0 | 0 |
| Prolog | 282 | 0 | 0 |
| Snocone | 183 | 0 | 0 |
| Rebus | 79 | 0 | 0 |

**1,264 non-Pascal programs, zero reach it** — every one registers through `emit_module_init_body` instead.

**Control arms, all after `make pristine` (HQ-27), and all re-proven a second time after the push rebased onto four newer commits (two of them runtime: `bn_size`, `gc_heap`):**

- `test_corpus_snobol4` — m3 **PASS=365 FAIL=0** · m4 **PASS=365 FAIL=0 SKIP=0 MISSING=0**
- `test_gate_emit_no_lang` ✅ · `test_gate_template_medium_invisible` ✅ (0 BOTH-MEDIUM sites, ratchet held)
- `test_smoke_icon` — m3 14/14 · m4 14/14
- `test_gate_pascal_m3` — **111/42/23**, and **byte-identical with this commit reverted**. The pre-existing m3 red moves by exactly zero. ⭐ That baseline was *measured on a reverted pristine build*, not inferred from "my change is mode-4 only" — the argument was available and was not accepted as evidence.

## ⛔ WHAT THIS DID NOT CURE — the link failure was masking a second layer

19 of the 80 now link and still diverge m3/m4. Honest split:

- **18 already fail in m3 too** (mostly nested-proc: `nested`, `nest2`, `nestcount`, `nestshadow`, `nestrec`, `varframe`, `recursion`, `deep5` …) — already counted in the m3 gate's FAIL=42. Not new, now merely reachable.
- **1 is a genuine new m4-only exposure:** `arrparam.pas` — m3 prints the correct `15`, m4 **SIGSEGVs**. Crash is `getenv("SCRIP_VARARG_TAIL")` inside `rt_proc_call_prologue_lex` (`rt.c:1506`), i.e. a **trashed `environ`** from an earlier frame overwrite, on the registered-proc dispatch path this fix newly enabled. Rowed as `pascal-m4-registered-dispatch-segv`.

⭐ A cure that unmasks a defect has not created it, but it **has** changed what the board means. Saying "80 → 0 link failures" without saying "19 of them still don't agree" would be true and misleading in the same breath.

## ⭐⭐ THE KINSHIP ANSWER — hq_P WAS RIGHT, AND THE HONEST HEADLINE IS **KINSHIP-OF-THREE**

hq_P (s277): *"an m4 link failure with no m3 arm … is not a weak leg, it is an ABSENT one. Either get it to link so it has an m3 arm and becomes measurable, or drop it from the claim."*

**It now links, so it is measurable — and the measurement removes it from the claim.**

Applying hq_P's own layout method (compile with `--compile -o`, read the callee body between its α and ω, grep `rsp`/`rbp` — no gdb) to the Pascal witness `arrparam`:

- **`rbp` appears ZERO times in the entire emitted file.** Corpus-wide: **177 of 184** Pascal m4 programs emit **no `rbp` at all** (the 7 that do are `pb30`–`pb35`, `pcom_diag3`).
- The frame is pure **ζ-SPINE on `rsp`** — `sub rsp, 416`, every slot `[rsp + N]`, set up by `rt_jmp_frame_lexprep2` / `rt_icn_zframe_args_install`.
- **Both exit ports tear the frame down before leaving:** `sumvec_γ` and `sumvec_ω` are each `mov rcx, [rsp + N]; add rsp, 416; jmp rcx`.

**So the shape-question answer for the Pascal leg is NO on both halves:** the callee's frame does **not** have to survive past its own return, and the ζ carrying it is **SPINE (`rsp`)** — not the **FR/FRAME** family on `rbp` that hq_P measured for Icon N-2 (generator ζ at `[gen_rbp-96, gen_rbp)`, resume record at `[gen_rbp-128, gen_rbp-96)`, caller landing at `rsp = gen_rbp+32`).

⛔ **And the original Pascal witness has ceased to exist as a frame witness at all.** The thing in the kinship table was *the link failure itself* — which turns out to be a dangling symbol reference between two emitters, a build-configuration defect with no frame content whatsoever. **It was never a candidate.** Its inclusion was an artifact of grouping witnesses by *how loudly they failed* rather than by a measured mechanism.

⭐ **Therefore: drop the Pascal leg. The claim is kinship-of-three** (Prolog backtracking, Prolog non-backtracking, Raku recursive `fib`) — three legs that survived the `fb0bcbec` bisect, exactly as the previous FINDING recorded, and no fourth. ⛔ The three-leg claim is *still* only "one alternative excluded", not "one shared cause demonstrated"; nothing here upgrades it.

## ⚠️ AN ORACLE QUESTION THIS TURNED UP (not a defect claim — a question)

Grading all seven rivals-grid programs against **fpc 3.2.2** byte-for-byte, **all seven differ, controls included** — SCRIP pads integers to a fixed field width (`        15`), fpc writes minimal width (`15`). Whitespace-normalized, **all seven match fpc in both modes**. So the ceo grid's *"m3 ≡ fpc"* holds on **values**, not on bytes.

⛔ This matters before anyone mints a scored Pascal board: **byte-diff against fpc would read as 100% RED on programs that are numerically perfect.** Classic/ISO Pascal leaves the default `write(integer)` width implementation-defined and pascal-p4 pads; fpc does not. **Which Pascal is the oracle is a real, unruled question** — not obviously a SCRIP bug. Raised, not answered.
