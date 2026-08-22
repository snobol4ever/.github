# FINDING — `rtcc-veneer-strip-pure-asm` FIRST STEP LANDED: A GATE-VERIFIED "NON-CLOBBERING LEAF" PROPERTY, NOT A NAME LIST, AND `rt_cmp_d` IS ITS FIRST REAL TENANT

**seat03, 2026-08-22. Picked up via THE LOOP (`s4e_msg.sh next`), row `rtcc-veneer-strip-pure-asm` (GOAL-RTCC.md), brief citing Lon s200 in-chat ("remove the RTXX veneer around ALL RT calls that are pure ASM") and FINDING-2026-08-21-s200. FIRST STEP only, per the brief's own DoD — mechanism proved end-to-end on one real, hot, delicate callee (`rt_cmp_d`), not a sweep of every candidate.**

## THE PREMISE CHECK, FIRST (rule 3 of THE LOOP: a brief's numbers can be wrong and it is still a brief)

The brief's "FIRST STEP" text says define the property "NOT a per-callee name list, which is a per-op filter under another name." **`x86_rtcc_clob()` (`src/templates/x86_asm.h`) already had exactly such a table when this session opened** — 13 symbols, built under **GOAL-RBP-EARN, s65** (a sibling goal, per its own gate's header), and it was already MECHANICALLY VERIFIED by `scripts/test_gate_rtcc_callee_class.sh`: that gate re-parses the table out of the C++ source, walks the named symbol's actual `RTX_FUNC` body in `src/runtime/rtx/*.S` (following local-label fallthrough), and FAILS if the symbol carries a live `RTX_GATE`, exits to C, or writes a claimed register the table doesn't cover. **This is the difference that matters**: a per-op filter (RULES) is an *unverified* editorial exception that can silently drift from the code it describes; this table is a *cached, continuously re-derived fact*, and lying in it is a build-breaking FAIL, not a code-review nit. So "the property" already existed — what did not exist was (a) a **separate, killswitch-gated authority** so a new entry's off-arm is provably byte-identical to pre-row HEAD without touching the 8 pre-existing zero-mask entries, and (b) any symbol actually converted to **exploit** it on the hot side named in s200 (`rt_cmp_d` / `str_concat_d` / `NV_SET_fn`) — the existing 13 were all cold-path or already-narrow. That gap is this row's real first step, and it is now closed for one symbol.

## WHAT LANDED

**1. `x86_rtcc_noclob_on()` + a new `LEAF[]` table, checked *before* the pre-existing `T[]`, both inside `x86_rtcc_clob()`** (`src/templates/x86_asm.h`):
```c
static inline bool x86_rtcc_noclob_on(void) { const char * e = getenv("SCRIP_RTCC_NOCLOB"); return !(e && *e == '0'); }
...
static const struct { const char * n; unsigned m; } LEAF[] = {
    { "rt_cmp_d", RTCC_C_R10 | RTCC_C_R11 },
};
if (x86_rtcc_noclob_on()) for (...) if (strcmp(sym, LEAF[i].n) == 0) return x86_rtcc_nowire(LEAF[i].m);
```
Killswitch `SCRIP_RTCC_NOCLOB`, **default ON**. The pre-existing, dead-since-s195 `{ "rt_cmp_d", RTCC_C_R8|RTCC_C_R9|RTCC_C_R10 }` line in `T[]` was **deleted, not edited** — it is mathematically a no-op (`x86_rtcc_nowire(7) == x86_rtcc_nowire(RTCC_C_ALL) == 3`, proven by hand and by the byte-identical off-arm sweep below), so removing it changes nothing and the killswitch-OFF path is exactly pre-row behaviour by construction, not by re-testing every combination.

**2. `rt_cmp_d` (`src/runtime/rtx/rtx_arith.S`) rewritten to never touch r8/r9, across *every* reachable arm** — a pure register rename, zero instructions added/removed/reordered: `r9b`→`r11b` (int, string-diff, real arms) and the string arm's `ptr_b` role moved `r8`→`r10` (r10's only prior use in the function, the `DT_NOTSTR_MASK` combine, is provably dead by the point `ptr_b` needs a register — same reuse idiom the file already used for `r10b` in two other arms). r8/r9 are the only two slots the veneer still tracks by default (r10/r11 were freed fleet-wide at s195 — `ARCH-SNOBOL4-RTX.md`'s WREG-RETIRED entry, Lon 2026-08-22: *"R10 and R11 are free, they used to be reserved for GAMMA and OMEGA which is now replaced by PUSH-PUSH at RBP"* — confirming r10/r11 reuse here carries zero correctness risk against any live wire convention).

**3. New declared mask**: `RTCC_C_R10 | RTCC_C_R11`. Both bits are stripped by `x86_rtcc_nowire()` under the default (non-`SCRIP_RTCC_BANK_WIRES`) policy, so the **emitted veneer is fully zero** — `x86_rtcc_call` takes its `m==0` early return (`x86_call_ro`), not merely a narrowed one.

**4. New permanent gate — `scripts/test_gate_rtcc_noclob_injection.sh`** — the negative-test leg. It builds a throwaway scratch tree (never touches the real one) shaped like the callee-class gate expects, with two synthetic RTX bodies: `rt_test_true_leaf` (truthfully claims mask 0) and `rt_test_false_leaf` (**falsely** claims mask 0 while its body writes r9). Running `test_gate_rtcc_callee_class.sh` against that scratch tree must PASS the first and FAIL the second, naming the exact clobbered register. Both fire correctly (verified below) — proof the verifier catches a lie, not just accepts the truth.

## CORRECTNESS

- **Direct unit test** (`rt_cmp_d`, all three arms + edge cases: negative ints, empty/null strings, prefix ordering, mixed int/real, NaN both operand positions): **18/18 PASS**, and re-run against a `git stash`-restored pristine build of the *unmodified* `rt_cmp_d`: **byte-identical 18/18 PASS** — the rename changes no observable behaviour.
- **`test_gate_rtcc_callee_class.sh`**: 13 classified symbols (same count as before — one moved from `T[]` to `LEAF[]`), **PASS**. The gate independently re-derived that the rewritten body never writes r8 or r9 on any reachable path.
- **`test_gate_rtcc_noclob_injection.sh`**: both controls fire (positive: no false alarm; negative: `rt_test_false_leaf`'s lie caught, `writes r9 but mask says <none>`).
- **SNOBOL4 crosscheck** (`test_crosscheck_snobol4.sh`, both modes): `--run` 322/323 PASS, `--compile` 321/323 PASS + 1 skip, **DIVERGE=0**, single failure `160_pat_alt_inner_gen_resume` in **both** modes — a pre-existing pattern-ALT-resume defect (unrelated; same name/shape the s249 loopctl-inline FINDING already recorded as standing-red).
- **M1 ladder** (`board_beauty_m1.sh --modes both`): m4 **10/10, M1-FIXED-POINT held**; m3 **3/10, first red at line 10** — identical to the pre-existing, separately-tracked m3 defect (pattern/SEGV class, `GOAL-SCRIP-HQ.md`), **not moved**. Read against the brief's "STAYS 10/10 both modes" the same way the sibling s249 row read it: no *new* regression, since m3 was never 10/10 at this HEAD to begin with.

## THE WITNESS — VENEER GONE AT THE LICENSED SITE, PRESENT AT THE UNLICENSED ONE, SAME FILE

`corpus/crosscheck/arith/triplet.s` (real corpus program, not contrived), compiled `--compile` at default settings:
```
.Lx102_0:               lea              rdi, [rsp + 32]                      # coerce_numeric
                        lea              rsi, [rsp + 16]                      # b
                        call             rt_cmp_d@PLT              <-- LICENSED: zero veneer
                        test             eax, eax;                            je    .Lx102_240
...
                        mov              rcx, qword ptr [rsp + 24]
                        mov              qword ptr [rip + rtccb+40], r8
                        call             str_concat_d@PLT          <-- UNLICENSED: veneer intact
                        mov              qword ptr [rsp + 0], rax
...
                        mov              qword ptr [rip + rtccb+40], r8
                        call             NV_SET_fn@PLT              <-- UNLICENSED: veneer intact
                        mov              r8,  qword ptr [rip + rtccb+40]
                        mov              r9,  qword ptr [rip + rtccb+48]
```
**Incidental side effect, both-medium-safe (TEXT-only cosmetic)**: `x86_argnote()`'s backward scan for `# a`/`# b` argument-role comments stops at the first `mov` whose destination isn't a recognised arg register. The old `mov qword ptr [rip+rtccb+40], r8` (destination = memory, not a register) tripped that stop, so it silently annotated *nothing* for veneered `rt_cmp_d` sites. With the veneer gone the scan reaches the real `lea rdi`/`lea rsi` and annotates them correctly (visible above). Purely a TEXT-medium readability improvement; BINARY medium and execution are untouched.

## OFF-ARM / ON-ARM SWEEP — FAR PAST THE ≥80-PROGRAM DoD

Full `corpus/crosscheck` SNOBOL4 set (the same 324-file set `test_crosscheck_snobol4.sh` uses, sorted, `--compile` each): pristine-original vs mine-with-`SCRIP_RTCC_NOCLOB=0` vs mine-default.
- **Off-arm (killswitch OFF) vs pristine original: `diff -rq` over all 324 files → ZERO differences.** (4× the DoD's ≥80-program bar, exact, not sampled.)
- **On-arm (default) vs pristine original: 40/324 files differ**, every one attributable to (a) the `rt_cmp_d`-veneer removal and/or (b) the argnote cosmetic above — spot-checked several (`keywords/099_lexical_compare`, `functions/088_define_recursive_fib`, `gc/200_gc_churn_live_anchor`, `rung2/215_indirect_goto_cond`) and confirmed no other line moves. The changed-file list itself is informative: it includes `rung9/914_lgt.s` / `915_llt.s` / `916_leq.s` / `917_lne.s` / `918_lge.s` / `919_lle.s` — SNOBOL4's `L*` **lexical (string) comparison** builtins, i.e. `rt_cmp_d`'s STRING arm, confirming it independently of the arithmetic-loop framing s200 used.

## PRICING — RECONCILED ACROSS TWO MEDIA, ONE EMPIRICALLY EXACT

**Static, TEXT medium (`--compile`, mode 4)**: veneer = 1 store + 2 loads = **3 instructions removed per call site** (matches s200's own count exactly: *"one store before and one-to-two loads after"*).

**Static, BINARY medium (`--run`, mode 3) is MORE expensive than s200's framing assumed, and this is the number that matters for the shipped default mode**: `x86_rtcc_wb_bin`/`x86_rtcc_rl_bin` each pay an extra `movabs <reg>, block` (10 bytes) to materialize the RTCC block's absolute address (TEXT medium gets this for free via `[rip+rtccb+N]`), and `x86_rtcc_call` unconditionally ORs `RTCC_C_R10` into the mask **in BINARY medium only** (`if (MEDIUM_BINARY) m |= RTCC_C_R10;`) for any non-zero mask — so the pre-existing (default/unclassified) veneer for `rt_cmp_d` in mode 3 was actually **9 instructions** (2×movabs + 1 store + 3 loads across r8/r9/r10), against **2** for the licensed `x86_call_ro` path (movabs ptr + indirect call) — **7 instructions removed per call site**, not 3.

**Empirically confirmed to the instruction, not estimated**: a dedicated witness (`cmp_price.sno`, forces the REAL-number arm 50,001 times — the shape s200's own methodology used, unconditional call, no int fast path) under `callgrind` (Ir, deterministic, no timing rail needed):
| | Ir (whole process) | delta |
|---|---:|---:|
| pristine original | 20,573,464 | |
| this row (default) | 20,252,871 | **−320,593 (−1.56%)** |

`rt_cmp_d`'s own body cost is **unchanged**, 1,100,022 Ir both builds (confirmed via `callgrind_annotate`, and `calls=50001` confirms the call count itself is exactly as designed) — proving the entire delta is caller-side. The JIT-generated-code region (`???:0x...` in the annotation, i.e. the actual emitted call sites) shows **350,007 = 7 × 50,001 exactly**, closing the loop between the static BINARY-medium accounting and the dynamic measurement with zero residual. (The whole-process total is ~29K lower than the pure JIT delta because the argnote cosmetic above costs a handful more `strcmp` calls at *compile* time — a one-time, not per-iteration, offset.) Both callgrind runs produced identical, correct output (`iters=50001`) — the price was measured on a correct program, not just a fast one.

**⛔ QUALIFICATION s200 DIDN'T HAVE — read this before ranking this row against its siblings.** `FINDING-2026-08-22-seat03-loopctl-inline-lt-concat-store-was-already-landed-at-s249.md` (one day after s200) shows `bb_cmp_test.cpp` now inlines the DT_I/DT_I case, so `rt_cmp_d`'s call **for pure-integer loop-control comparisons specifically** is on a *cold* branch post-s249 — the same shape s200 already conceded for `rt_add`. **This does not moot the row**: s200's own ranked list named the veneer's value as applying to "the remaining unconditional calls" *after* items 1–3 landed, and `rt_cmp_d`'s string/real/mixed arms (never touched by the s249 int-only fast path) are exactly that remainder — confirmed live in this session's own crosscheck sweep (the six `L*` lexical-compare programs above) and in `rtx_arith.S`'s own header census (`var_access`/`table_access`/`func_call` millions-of-calls counts, pre-dating s249 and not re-measured this session for the post-s249 world). Recorded so the next seat prices `str_concat_d`/`NV_SET_fn` against the *current* call-site shape, not s200's snapshot.

## REGEN (RULES §4 — codegen touched: `x86_asm.h`, a runtime sink)

Ran in order: benchmark (SCRIP `→` corpus `c30f04c4`, 15 files, all shrink) → feature (SCRIP `e6e62699`, 18 files, all shrink, 1 pre-existing EMIT-FAIL — `coverage_sno_nodes`, A/B-verified byte-identical FATAL against pristine original, a standing GZ#5-pattern-subset limitation, `GOAL-SNOBOL4-BB.md`, unrelated) → demo (corpus `01fdd694`, 4 files) → programs (all 4 languages, **changed=0**, 15 EMIT-FAIL + 42 AS-FAIL all Prolog/Rebus, pre-existing, unrelated) → prolog-bench (**changed=0**, 3 pre-existing REJECTED-BY-AS, unrelated) → crosscheck (corpus `03ff69eb`, **83/490 changed** — the extra 43 over the SNOBOL4-only 40 are Snocone programs sharing the same relational-operator lowering; 15 EMIT-FAIL, same GZ#5-subset class as above, spot-checked one Snocone instance directly against pristine — identical FATAL, confirmed unrelated).

## ⛔ CORRECTION AT PUSH TIME — ORIGIN MOVED MID-SESSION, THE PRICING ABOVE IS PRE-REBASE AND ITS EXACT NUMBERS ARE STALE

`git pull --rebase` (required before push) landed FIVE other seats' commits on top of `2e601a2e`, including **`3cf83181` `rung-E6-x86-asm-h`** (a different, concurrent RTCC row): it retired R10/R11 from RTCC's protected set entirely — `RTCC_C_R10`/`RTCC_C_R11` **deleted**, `RTCC_C_ALL` narrowed to `RTCC_C_R8|RTCC_C_R9`, `x86_rtcc_wire_bank()`/`x86_rtcc_nowire()` deleted, and (load-bearing for the pricing above) **the BINARY-medium call stub's forced `m |= RTCC_C_R10` is gone** — their commit message: *"the self-inflicted clobber RTCC_C_R10 existed to protect against is gone."* This is the exact mechanism that made this session's "7 instructions/call, BINARY medium" measurement come out higher than the naive TEXT-medium "3" — that extra R10 tax **no longer exists on HEAD**, for any callee, independent of this row. Rebasing this row's own change onto it: `x86_rtcc_clob()`'s `LEAF[]`/`T[]` masks are now bare `0`/`RTCC_C_ALL` values (no `RTCC_C_R10|R11` — those symbols don't exist to write), `rt_cmp_d`'s entry becomes `{ "rt_cmp_d", 0 }`, and the mechanism, killswitch, and off-arm-byte-identical property all carry over unchanged in spirit — **re-verified green post-rebase**: `test_gate_rtcc_callee_class.sh` PASS (13 symbols), `test_gate_rtcc_noclob_injection.sh` both controls fire, crosscheck both modes unchanged (322/323, 321/323+1skip, same single pre-existing failure), M1 ladder unchanged (m4 10/10, m3 3/10), `cmp_price.sno` still correct (`iters=50001`).

**A SECOND, INDEPENDENT DEFECT SURFACED BY THE REBASE, NOT BY THIS ROW, AND FIXED IN THE SAME COMMIT:** `test_gate_rtcc_callee_class.sh` (GOAL-RBP-EARN, s65) hardcoded its protected-register set as a Python literal `{'RTCC_C_R8':'r8', ..., 'RTCC_C_R10':'r10', 'RTCC_C_R11':'r11'}`, independent of `x86_asm.h`'s own `#define`s. Once rung-E6 deleted the R10/R11 defines, the gate started FALSE-FAILING five symbols (`rt_cap_match_begin`/`rt_cap_pop`/`rt_cap_top`/`rt_match_ctx_restore`, all correctly re-classified `0` by rung-E6, plus this row's own `rt_cmp_d`) with `"writes r10 but mask says <none>"` — the gate was checking a register RTCC no longer tracks. Fixed by re-deriving the protected set from `x86_asm.h`'s actual `#define RTCC_C_R<n>` lines every run instead of a second, independent hardcoded copy — the same "re-derive from source, never trust a cached copy" principle the gate itself exists to enforce, now applied to the gate's own assumptions. `test_gate_rtcc_noclob_injection.sh`'s scratch header updated to carry the `#define`s its scratch tree now needs.

**WHAT WAS NOT RE-DONE, IN THE INTEREST OF CLOSING THIS ROW: the ~320,593-Ir / 350,007-JIT-region / "7 instructions/call" callgrind numbers above were measured PRE-rebase and are NOT re-derived against the new HEAD** (rung-E6's own removal of the forced-R10 tax means the true post-rebase BINARY-medium veneer cost for an unclassified callee is **5 instructions/call, not 7** — 2×movabs + 1 store + 2 loads, no more forced-R10 store/load pair — by the same static accounting method used above, not re-measured empirically). The STATIC TEXT-medium price (3 instructions/call, exact) and the qualitative results (mechanism sound, veneer fully eliminated at licensed sites, off-arm byte-identical, correctness proven, no regression) all stand and were re-verified post-rebase as listed above. **Re-price BINARY medium empirically before quoting a dynamic number for this row** — the next seat should not cite the 320,593/350,007/7-per-call figures above as current; they describe a HEAD that no longer exists.

## DISPOSITION

Mechanism proven, gate-verified, killswitch-protected, one real hot-adjacent production callee converted and measured both statically and dynamically. **Not done**: `str_concat_d` and `NV_SET_fn` (s200's other two named hot callees) are NOT converted this rung — each needs its own register-usage audit and is real, separately-scoped follow-on work, now with a proven mechanism and a working template (`LEAF[]` + the injection gate) to extend rather than invent. Recommend the next seat on this row (a) re-measure the current post-s249 hot/cold shape for all three before ranking further work, per the qualification above, and (b) audit `str_concat_d`/`NV_SET_fn` for r8/r9 touches the same way this session did for `rt_cmp_d` (grep + `test_gate_rtcc_callee_class.sh` re-derivation) before attempting a rename.

Files: SCRIP `src/templates/x86_asm.h`, `src/runtime/rtx/rtx_arith.S`, new `scripts/test_gate_rtcc_noclob_injection.sh`. corpus: benchmark/demo/crosscheck `.s` regen (3 commits, listed above). `.github`: this FINDING + `GOAL-RTCC.md` cursor move.
