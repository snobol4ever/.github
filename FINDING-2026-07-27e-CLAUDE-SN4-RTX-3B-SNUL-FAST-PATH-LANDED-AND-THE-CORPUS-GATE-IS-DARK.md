# FINDING 2026-07-27e — RTX-3b: the SNUL fast path is landed and measured at 1.236×, and the corpus gate went dark underneath it

**Session s190. Goal `GOAL-SNOBOL4-RTX.md`, rung RTX-3b. SCRIP branch `rtx-3b-s190`, commit `a5ff0a9d` — LOCAL ONLY, NOT PUSHED (see §5).**

---

## 1. WHAT LANDED

`rtx_str.S` gains the null-operand arm of `str_concat_d`, behind the existing `rtx_gate_str`.

The C being reproduced is two lines — `if (IS_NULL_fn(a)) return b; if (IS_NULL_fn(b)) return a;` — implementing the manual's TYPE-PRESERVING null rule (v3.7 p.22: `(20-17) ''` is the INTEGER 3, not `'3'`). At `-O0` those two lines sit behind a `rt_gc_point_arr` call with a 32-byte stack shadow array, four `DT_P`/`DT_X` compares and two `IS_FAIL` compares. The port reaches `ret` in **13 instructions**.

Target shape is `SNUL ⊕ I`, produced by the predicate-guard idiom `LOOP N = LT(N,lim) N + 1` that appears in essentially every SNOBOL4 loop — `LT` returns null, whitespace is concat, and the type-preserving rule is what keeps `N` an integer so the loop's own bound keeps working. RTX-3's fast path excluded this shape BY CONSTRUCTION (it required both operands `DT_S`).

**Guard order is `c_str_concat_d`'s and may not be reordered:** gc_pending → `DT_P`/`DT_X` (pat_cat precedence) → `DT_FAIL` (FAILDESCR precedence) → then the `DT_SNUL` arms. Returning `b` early would hand back a raw pattern, or a fail descriptor whose payload the C would have replaced.

**Only the `DT_SNUL` arm of `IS_NULL_fn` is taken.** Its other arm (`DT_S && slen==0 && !*s`) is the RTX-3 `slen==0`-means-LENGTH-UNKNOWN trap and stays in C.

---

## 2. TWO GAPS THE RUNG WALKED INTO, BOTH OF THE FAMILY THIS LADDER KEEPS NAMING

**(a) `DT_X` was documented but never defined.** `rtx_abi.inc`'s own header comment block reads `... N 9 . K 10 . E 11 . X 15 . FAIL 99`, but the `#define` list below it stopped at `DT_N` and `DT_FAIL`. Writing `cmp edx, DT_X` produced a link failure — `relocation R_X86_64_32S against undefined symbol 'DT_X'` — not an assembler error, because GNU `as` happily emitted a relocation against an undefined external.

⭐ **This is the phantom-symbol family in a NEW place: not a ladder rung and not an inventory script, but a doc comment sitting eight lines above the definitions it describes, in the same file, disagreeing with them.** The tag table is duplicated between `contracts/descr.h` and `rtx_abi.inc` with NOTHING tying them together — no `_Static_assert`, no generation step. A tag whose value silently drifts would not fail to link; it would mis-compare and pass most batteries. **RECOMMENDED (not done, needs Lon's ruling on scope): a `_Static_assert` per tag in `rtx_init.c`, which is C, sees `descr.h`, and is already the RTX TU that owns cross-checks.**

**(b) The RTX-3 battery did not cover the shape RTX-3b targets.** Its 8404 cases include `SNUL+S`, `S+SNUL`, `SNUL+SNUL` and `I+SNUL` — but NOT `SNUL+I`, which is the idiom's own shape and the entire reason this rung exists. Symmetry made it *look* covered. Added `SNUL + int (LT idiom)`, `SNUL + int (negative)`, `SNUL + real (LT idiom)`. **8404 → 8410.**

---

## 3. EVIDENCE

| gate | result |
|---|---|
| differential battery | **8410 cases, 0 mismatches** |
| RTX unit + alloc | 21/21 · 36/36 |
| ⭐ falsification (INVERTED null identity, not corrupted) | **RED — 8 mismatches**, asm returned `v=0` where C returns `v=6`/`v=7` |
| kill-switch A/B on corpus | board byte-identical gate ON vs OFF |
| ⭐ **RAIL — the rung's EXPECTED BOARD, stated in advance** | **`var_access` 1.236×** |

**The falsification is the load-bearing one.** Had the battery stayed green under an inverted identity, every number above would have been an unreachable-code artifact. It went red, so the green is evidence. This is s187's probe rule applied as written: the break was an INVERSION, not a corruption, because returning `a`-instead-of-`b` is a no-op on the `SNUL+SNUL` case and would have read as vacuous there.

**The rail number, `RT_OPT=-O0`, mode 3, R=3 interleaved, medians, output byte-identical across arms:**

| program | STR=0 | STR=1 | ratio |
|---|---|---|---|
| `var_access` (N scaled ×4 to 40M) | 1912 ms | 1547 ms | **1.236×** |

⛔ **N HAD TO BE SCALED FIRST.** At its shipped N=10M `var_access` self-times at **380 ms**, under RTX-0b's `MIN_MS`=800 hard gate — a BOGUS-WINDOW whose ratio must be SUPPRESSED, not printed small. Scaling the dominant `LT(N,·)` bound ×4 put the window at ~1.9 s.

The rung predicted, in writing and before the port: *"`func_call` and `var_access` MUST move well outside the ±3% noise floor. If they do not, the port is not being reached and the rung is falsified."* `var_access` moved **23.6%**, against **1.018** for the same program before this port. The prediction was falsifiable and was not falsified.

---

## 4. WHAT IS STILL OWED, AND WHY IT COULD NOT BE DONE

⛔ **`func_call` (10.0M `SNUL+I`, the rung's other named target) is UNMEASURED**, and ⛔ **`string_pattern` "must NOT regress from 2.016×" is UNDISCHARGED.** `string_pattern` **segfaults** — under BOTH arms, including `SCRIP_RTX_STR=0`, which routes entirely to `c_str_concat_d` and never enters the asm. `func_call` depends on `DEFINE`, which is currently broken (§5). Neither failure is reachable from this port; neither can be cleared until the board recovers.

⛔ **The full corpus crosscheck gate is NOT met** and is deferred, not waived.

---

## 5. THE CORPUS GATE IS DARK — BREAKAGE FROM OUTSIDE THIS LADDER

| | m3 | m4 | DIVERGE |
|---|---|---|---|
| documented, s188 | 314/1 | 312/1 | 0 |
| measured, s190, HEAD `9843ee7e` | **185/130** | **182/131** | **2** |

**Confirmed by Lon mid-session: a parallel session is actively breaking things.** Recorded here so the number is not later mistaken for an RTX regression.

Ruled out mechanically before that was known: not this port (pristine HEAD stashed → identical board); not any RTX gate; not the optimizer. Narrowed to a 4-line repro — **every dummy argument arrives null:**

```
        DEFINE('f(x)')  :(fe)
f       f = x + 1  :(RETURN)
fe
        OUTPUT = f(5)      →  1     (expected 6)
```

A zero-arg function returning a constant works (`h()` → 99), so DEFINE, the call, RETURN and result assignment are all intact — **argument passing alone.** That single defect explains the shape of the failure list: every `define_*`, every `*_pat_fence_fn_*`, every `*_star_var_*`. Per SPITBOL Ch.8 the dummy arguments are saved and THEN the actuals assigned; the save is happening, the assign is not.

⭐ **MY PROCESS ERROR, RECORDED BECAUSE THE RULE EXISTS FOR EXACTLY THIS:** ARCH §7 step 3 says *re-prove the watermark at session start before touching anything.* I did not, and so I found a 129-program hole AFTER writing the port instead of in the first two minutes. Everything in §3 had to be re-established against a moving baseline as a result.

---

## 6. TWO INFRASTRUCTURE HAZARDS MET THIS SESSION

**(a) `.inc` IS NOT A TRACKED DEPENDENCY OF `.S` OBJECTS.** Editing `rtx_abi.inc` did NOT rebuild `out/rt_pic/rtx_str.o`; `make` relinked the stale object and reproduced the *identical* link error, which reads as "my fix didn't work" rather than "my fix wasn't compiled." Cost a full diagnostic cycle. `rm -f out/rt_pic/rtx_str.o` is the workaround; a dependency rule is the fix. **Anyone editing `rtx_abi.inc` must delete the dependent `.o` by hand today.**

**(b) `git checkout` REPORTED "Aborting" AND MOVED HEAD ANYWAY.** A checkout onto a detached HEAD with three modified files printed *"Your local changes would be overwritten … Aborting"*, exited non-zero — and the working tree was nonetheless switched to the target commit with the modifications gone. Recovered only because the diff had been banked to `/tmp` first. **With parallel sessions in flight, bank the patch AND commit to a branch before any checkout; do not trust the abort message.**

---

## 7. NEXT

1. **The board is the blocker, not this rung.** Nothing on this ladder can be corpus-gated until argument binding is back. The 4-line repro in §5 is the cheapest handle on it.
2. Once green: re-run the full crosscheck against `rtx-3b-s190`, plus `func_call` and the `string_pattern` non-regression, then land.
3. `RTX-3b` extension worth measuring separately: the `S + SNUL` direction is ported here but was never independently rail-measured; the s188 histogram found `I + SNUL` less common than `SNUL + I`, but did not say it was rare.
4. Still owed from s187: the **CALL differential unit battery**.
5. Open from s188 and NOT explained by this rung: `string_manip` moves **1.279** under the STR gate with the sign wrong for a slow-path shape. RTX-3b does not touch it. Do not quote a final STR number until it is explained.
