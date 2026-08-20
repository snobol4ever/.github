# FINDING s184 (seat8, row 13 `pat-eval-double-fn-arbno`) — THE TWO FACES ARE ONE CROSSING, AND ALL THREE STANDING DIVERGE ROWS RETIRE ON ONE UNSEALED CELL

**Tree:** SCRIP `ffbc1425`, corpus `cdcebe25`, `.github` `a0f960b2`. Pristine rebuild before every verdict (HQ-27). RT_OPT `-O0` (FACT RULE O0-DEV) — no perf claim in this FINDING.

## Verdict on the row's question

Row 13 asked: root-cause both faces of `141_pat_eval_double_fn_arbno`, **or prove them one class**. They are **one class**, proven by measurement, not by resemblance: both faces enter at the same runtime function on the same crossing, and the passing sibling that differs by exactly one ingredient is immune to every disarm that fires either face.

**The crossing is `EVAL-fragment → main-image proc`.** Face 1 (m4) dies on the *outbound* leg; face 2 (m3) dies on the *return* leg. Nothing else about the two faces differs.

## ⛔ The headline: the DIVERGE was never one row, and it is one write

`141` was carried as the standing `DIVERGE=1`. At `ffbc1425` the SNOBOL4 crosscheck reads:

```
  --run      PASS=312 FAIL=5 SKIP=0
  --compile  PASS=308 FAIL=8 SKIP=1
  DIVERGE (mode-3 != mode-4 vs ref): 3
  DIVERGE: expr_eval 140_pat_eval_double_fn_trick 141_pat_eval_double_fn_arbno
```

**All three are one root cause and one cure.** Each was cured in m4, to byte-identical `.ref` output, by writing the ELF's `<FN>_α` address into the AB fn_cell `alpha$<FN>` — nothing else touched, the compiler unmodified, the store applied from gdb at run time:

| DIVERGE row | m4 before | cells sealed | m4 after | `.ref` |
|---|---|---|---|---|
| `probe/b1/b1c_e_plain` (the 8-line isolator) | `Error 22` | `alpha$PC` | `PC ran` / `match` | ✔ |
| `140_pat_eval_double_fn_trick` | `Error 22` | `alpha$inner` | `stk=B` | ✔ |
| `141_pat_eval_double_fn_arbno` | `Error 22` | `alpha$grab` | `out=e` | ✔ |
| `expr_eval` | **SIGSEGV** | `alpha$`×{Push,Pop,Unary,Binary} | `7 / 9 / 25.5 / 7 / 26` | ✔ |

`expr_eval` is the row that says this is a class and not a coincidence: it presents as a **SEGV, not Error 22**, it has four procs instead of one, and its EVAL evaluates *arithmetic*, not a pattern — and it still falls to the same seal.

## Face 1, root cause — measured, not inferred

The m4 startup bake registers proc **names** (`rt_define_site`) and GVA names (`gva_register@PLT`) and **never seals a single AB fn_cell**. `PC_α` lives in the ELF; nothing ever writes its address into `alpha$PC`. The cell therefore still holds its `.data` initialiser, `rt_ab_undef_fn_stub` — which *is* error 22 (`rt.c:511`).

Read at the identical breakpoint (`rt_proc_call_open`, first hit, on `b1c_e_plain`):

```
##### m4 #####                                         ##### m3 #####
$1 = (void *) 0x7ffff4123c2d <rt_ab_undef_fn_stub>      $1 = (void *) 0x7fffee000014
$2 = (void *) 0x7ffff4123c2d <rt_ab_undef_fn_stub>      $2 = (void *) 0x7ffff4123c2d <rt_ab_undef_fn_stub>
```

m3's driver seals `alpha$PC` to its pool-resident `PC_α` (the R-1 s94 loop). m4 has no seal road at all.

### Two things the s170 cold-start expected that the measurement does NOT support

1. **The `[SEAL] MISS` diagnostic is not the discriminator.** `SCRIP_SEAL_DIAG=1` prints the *same two misses in both modes* — `alpha$EXPR$0F1` and `alpha$PAT$0` — and m3 passes anyway (the `g_rt_fragment_emit` D-18b refusal sends those sites down the slim road). The unsealed cell that matters is the **main-image callee's**, `alpha$PC`, which the diagnostic does not name.
2. **"Sealing the cell makes it SEGV" no longer holds.** That was §5b's verdict at s170. At `ffbc1425` sealing completes the match cleanly on all four witnesses above. The tree moved underneath the claim (PF-1a…1d, `B1C_LAND`, `CAP_SEAMTIER`, `BLOB_CASMARK`, `DEFER_XPAT`, RT-CARRIER). **A seat taking the fix rung should re-measure §5b rather than inherit it.**

## Face 2 — NOT REPRODUCIBLE at HEAD, and the honest number

The intermittent load-dependent m3 `rc=139` **did not reproduce once** in **>1,600 runs across two trees and four independent load/layout models**:

| model | runs | result |
|---|---|---|
| quiet serial, HEAD | 28 | 28 × rc=0 |
| 16-way parallel, HEAD | 400 | 400 × rc=0 |
| **the real `util_out_sweep.sh`**, HEAD, ×3 full sweeps (583 rows each) | 3 | identical md5 `027851e5…` all three, never `RUN_RC_139` |
| sweep-identical invocation (`cd $d` + `SNO_LIB` + `--run`) interleaved with demo programs at `-P 16` | 300 | 300 × rc=0 |
| **the s170 tree itself** (`3a4ca273`, seat1's own arm), 16-way | 400 | 400 × rc=0 |
| address-layout perturbation (env pad 0…3000 step 37 — shifts stack/heap base) | 82 | 82 × rc=0 |
| historic retain arm `SCRIP_EVAL_RETAIN=2097152`, quiet + 16-way | 420 | 420 × rc=0 |

⛔ **This is a negative result, not a cure claim.** I cannot name the landing that closed it, because it does not reproduce on the s170 tree either — so the trigger was never the load model I can build here. It is recorded as **DORMANT, not fixed**.

## …but the program still sits one disarm from a deterministic SEGV, and that is what proves the class

The m3 face is *held* green by armed cures, and disarming either one returns it to a **deterministic** crash — while the main-built control is immune to both:

| witness | default | `SCRIP_B1C_PARITY=0` | `SCRIP_EVAL_RETAIN=0` |
|---|---|---|---|
| `b1c_e_plain` (**EVAL-built**) | rc=0 | **rc=139** | **rc=139** |
| `b1c_m_plain` (**main-built**, identical semantics) | rc=0 | rc=0 | rc=0 |

`141` itself: `SCRIP_B1C_PARITY=0` → 5/5 rc=139; `SCRIP_EVAL_RETAIN=0` → 12/12 rc=139. Every other killswitch on the tree is inert on it (`B1C_LAND`, `CODE_THUNKS`, `CAP_NAME_STRICT`, `PT_FRAME`, `BLOB_CASMARK`, `DEFER_XPAT`, `CAP_SEAMTIER`, `FENCE0_WHACK`, `PT_OPFRAME`, `CHOICE_RBP` — all 5/5 rc=0).

**The one-class proof.** The m3 crash under `SCRIP_B1C_PARITY=0` and the m4 Error 22 arrive at the *same function on the same call*:

```
m4:  rt_defer_get_pat_dtp("*EXPR$0F1") -> rt_call_proc_descr("EXPR$0F1") -> rt_proc_call_open -> rt_ab_undef_fn_stub
m3:  rt_defer_get_pat_dtp("*EXPR$0F1") -> rt_call_proc_descr("EXPR$0F1")  [rt.c:908]  -> "PC ran" -> SIGSEGV, rip = 0x1
```

Same entry, same thunk, one ingredient apart from a sibling that never enters the road at all. m4 never gets *out* (callee entry address absent); disarmed m3 never gets *back* (return leg). **One crossing, two legs, two media.**

## The witness pair the row asked for — it already existed, and it is the right one

`corpus/probe/b1/b1c_e_plain.sno` (EVAL-built, 8 lines) and `corpus/probe/b1/b1c_m_plain.sno` (main-built control) are the minimal discriminator; no new witness improves on them, so none was minted. What is new is the **disarm table above**, which converts the pair from a pass/fail pair into a *class* instrument: the control is immune to both disarms, the EVAL twin is fatal under either.

⛔ **And the row's own shape description is wrong: ARBNO is not load-bearing.** `140_pat_eval_double_fn_trick` has no ARBNO — plain concatenation of two EVAL-built patterns — and fails m4 identically. The class is `eval + deferred call to a main-image proc`. The ARBNO in `141` is decoration.

## The fix, named and pre-measured (NOT landed here)

**Seal `alpha$<FN>` for every main-image proc in the m4 image**, the twin of the m3 driver's R-1 s94 loop. The natural site is `bb_define_bind` (`src/templates/bb_define.cpp:396`), beside its existing `rt_define_site` call — but note the argument it already carries is **not** the one needed: `rt_define_site` receives the *body* entry (`n3_statement_begin_α`), whereas the cell must hold the *alpha face* (`PC_α`, a separate emitted block that prologues and then jumps to the body). So the rung is a second, alpha-face-carrying store, not a re-use of the existing lea.

Constraints for the taking seat: it is a codegen change ⇒ **nonzero `.s` blast radius on every SNOBOL4 m4 program with a DEFINE** ⇒ RULES step-4 regen is mandatory, and it needs a killswitch with a proven byte-identical `=0` arm. Expected payoff, already measured above: **SNOBOL4 crosscheck DIVERGE 3 → 0** and m4 `PASS 308 → 311`, restoring the **m3 ≡ m4** design invariant that has stood breached since s169.

## Routing

- **Row 13 closes as an investigation**, per its own DONE-WHEN (`FINDING; fix only if killswitch-clean`) — the fix is a codegen rung with a corpus-wide `.s` blast radius and is not killswitch-clean inside this row.
- **Row 5 `m4-fragment-landing` should be re-scoped, not merely resumed**: its §7(a)/(b) framing ("fix the fragment TINY landing" vs "admit TINY only for same-medium callees") is aimed at the *fragment's own* thunk cells. The measurement here says those miss identically in both media and are harmless; the live wall is the **main-image callee's** cell, which neither (a) nor (b) addresses.
- **Row 14 `sweep-false-mover-defence` keeps its value regardless of face 2 being dormant** — the instrument gap it names is real and this FINDING's negative result is exactly the shape a control-arm repetition would have settled at s170 in minutes.
