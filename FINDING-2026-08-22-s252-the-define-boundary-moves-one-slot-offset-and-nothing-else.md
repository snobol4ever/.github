# FINDING s252 — THE `DEFINE` BOUNDARY CHANGES ONE SLOT OFFSET, NOT THE CODEGEN SHAPE
**seat4 (Claude Sonnet 5), 2026-08-22 s252, row `bench-harness-no-procedure-boundary` (rank 0). `RT_OPT=-O0`, `scrip` rebuilt clean (`make`, not a stale binary — the tree had unbuilt template changes from other seats' pushes), mode-4 `--compile`, mode-3 `--run` correctness check on every witness.**

## BACKGROUND — WHAT WAS ALREADY SETTLED AND WHAT WAS NOT
FINDING-2026-08-21-s200 priced the `DEFINE(ZBODY)` procedure boundary and found it **free in wall-clock terms**: top-level-variable-bound and `DEFINE`-wrapped-parameter-bound loops both measured 7.60 ns/iter, harness-free, differential method. That closes the *overhead* question. It does **not** close the *representativeness* question this row exists to answer: two shapes can cost the same number of nanoseconds while running through genuinely different instruction sequences (e.g. a global-slot load vs a frame-relative load can both retire in the same number of cycles). Timing equality is not proof of codegen identity. This row's first step was to get that proof directly — compile the same kernel both ways and diff the `.s`.

## THE EXPERIMENT
Three minimal witnesses, all using the **exact loop-body statements from the real `arith_loop.sno` kernel** (`corpus/benchmarks/snobol4/arith_loop.sno`), committed as receipts at `corpus/probe/benchharness/`:

| witness | shape |
|---|---|
| `probe_toplevel.sno` | `A = 0; ZI = 1; ZBL A = A+1; ZI = LT(ZI,ZKN) ZI+1 :S(ZBL)` at top level, no `DEFINE`, no call |
| `probe_defwrap.sno` | identical body, inside `DEFINE('ZBODY(ZKN)')`, called once as `ZBODY(1000)` — the harness's own shape |
| `probe_deflocal.sno` | identical body, inside `DEFINE('ZBODY(ZKN)A,ZI')` — `A`/`ZI` declared as **true DEFINE-locals** (bonus check, see below — the real kernels never do this) |

All three `--run` to the correct check value (`1000`) on both engines' expected semantics before any asm was trusted (mode-3 sanity: SCRIP prints `1000` for all three).

## THE EVIDENCE — `.s` DIFF OF THE LOOP BODY (`--compile`, mode-4)
`probe_toplevel.s` (top-level) vs `probe_defwrap.s` (`DEFINE`-wrapped), the `A = A + 1` statement:

```
                          TOP-LEVEL                                    DEFINE-WRAPPED
n26_var_α:  mov rax, [r9 + 16]   # A               n25_var_α:  mov rax, [r9 + 32]   # A
            mov rdx, [r9 + 24]                                 mov rdx, [r9 + 40]
            ...(literal 1, identical)...                        ...(literal 1, identical)...
n28_binop_α: [inline add fast path -- cvtsi2sd/addsd/movq --   n27_binop_α: [BYTE-IDENTICAL fast path]
             cold call rt_add@PLT with rtccb save/reload,
             identical register choices, identical branch shape]
n29_assign_α: mov [r9 + 16], rax  # A  <- store back            n28_assign_α: mov [r9 + 32], rax  # A
              mov [r9 + 24], rdx                                             mov [r9 + 40], rdx
```

Same for the `ZI = LT(ZI,ZKN) ZI+1 :S(ZBL)` statement: `ZI`/`ZKN` differ only by the same constant offset (top-level `ZI=[r9+32]`,`ZKN=[r9+0]`; wrapped `ZI=[r9+48]`,`ZKN=[r9+16]`).

**Every opcode, every register, every branch, the entire α/β/γ/ω port wiring, the `rt_add` inline-fast-path-with-cold-call-fallback shape, and the RTCC veneer save/reload around the call are byte-for-byte identical between the two compiles.** The only difference anywhere in the two blocks is the literal displacement constant added to `r9` — and it is a **uniform +16 shift on every variable**, not a different addressing mode, a different register, or an extra instruction.

## WHY THE OFFSET SHIFTS — DECLARATION COUNT, NOT SCOPE
The `DEFINE`-wrapped source binds one more name than the top-level source: `ZBODY` itself is a natural variable (SNOBOL4's return-value-via-function-name idiom, `ZBODY = A :(RETURN)`) and claims the first 16-byte slot, pushing `ZKN`/`A`/`ZI` each up by exactly one slot (16 bytes: an 8-byte tag + 8-byte value, matching every other pair seen in this file). This is the same shift you'd see between **any two top-level programs** that declare one more or fewer names before the ones in question — it is a property of declaration order and count, not of the top-level/procedure-interior distinction. `r9` is documented in `REGISTER-LAYOUT.md` as ordinary caller-saved scratch (consistent with the RTCC veneer explicitly reloading it — `mov r9, [rip+rtccb+48]` — immediately after every call that could have clobbered it), and it is used identically as the natural-variable base in both compiles.

## BONUS CHECK — TRUE `DEFINE`-LOCALS (OUT OF THIS ROW'S SCOPE, FLAGGED FOR A SEPARATE ROW)
`probe_deflocal.sno` declares `A`,`ZI` as true locals (`DEFINE('ZBODY(ZKN)A,ZI')`, SPITBOL manual local-list syntax) rather than letting them ride as ordinary globals referenced from inside the body (which is what all 14 real kernels do — none of them declare locals). Its emitted loop body is **byte-identical, including the same `[r9+32]`/`[r9+40]` offsets**, to the non-local `DEFINE`-wrapped witness. That means SCRIP's current default `ζ-storage` (`cell-stack`/`forth`) is not yet giving declared-local names a distinct per-activation storage path at this codegen layer — locals and globals compile the same way today. ⛔ **This is a separate question from the one this row asks** (it bears on recursion/re-entrancy correctness, not on whether the *existing* benchmark suite is representative, since no existing kernel uses locals) and I have not chased it further — no claim here about whether recursive calls are correct or broken, only that the two declaration styles currently emit identical code in this one-shot, non-recursive witness. Worth a dedicated row if it matters to anyone; not adopted or investigated further here.

## VERDICT
**Procedure-interior codegen does not differ from top-level codegen for the shape every existing SNOBOL4 timed-benchmark kernel actually uses** (global naturals referenced from inside `ZBODY`, no declared locals). This was Lon's live concern (frame arm / local-vs-global access / GVA differing inside a procedure) and it is falsified directly at the instruction level, not merely inferred from equal timing. Per this row's own brief: *"If it does not differ, the boundary is a non-issue and the split-include is optional hygiene."* **That is the branch this measurement lands on.**

## DISPOSITION — SPLIT-INCLUDE NOT ADOPTED THIS ROW
Because representativeness is confirmed rather than merely "not disproven," the split-include (`harness-open.inc`/`harness-close.inc`) remains **available but optional** — it would satisfy Lon's stylistic preference ("there can not be a harness") at low engineering cost (`-INCLUDE` is textual, one authority preserved), but adopting it triggers this row's own DONE-WHEN clause requiring **every one of the 14 existing benchmarks re-measured through both shapes, deltas published by name, and `NOISE-FLOOR.tsv` re-baked** — real work, undertaken here only if wanted, not because correctness requires it. I did not do that work this row: doing a 14-file structural refactor and a full re-measurement pass for something this row's own conditional logic marks optional, without it being asked for, is the scope-creep this fleet has repeatedly convicted elsewhere. **Recommendation: leave `harness.inc` and all 14 kernels exactly as they are.** If Lon still wants the harness *appearance* gone for style/architecture reasons independent of this measurement, that is a fresh, explicitly-optional row (the design is already fully specified above and in the original brief; it is a few hours of mechanical work, not a research question) — I did not mint it myself since "optional, not requested" is not the same as "queue it anyway."

Also reaffirming the original brief's `CODE()` caution: no test witness here (or anywhere in this row) builds measured code via `CODE()` — all three probes are ordinary static source, consistent with the brief's warning that `CODE()` would add measured dynamic-compilation cost via the fragment-thunk road (S199, 2.66×) and make the instrument worse, not better.

## RECEIPTS
- `corpus/probe/benchharness/probe_toplevel.sno`, `probe_defwrap.sno`, `probe_deflocal.sno` — all three `--run` to `1000`, all three `--compile` clean, exit 0.
- Asm excerpts above are direct `--compile` output, `RT_OPT=-O0`, freshly rebuilt `scrip` (not a stale binary).
