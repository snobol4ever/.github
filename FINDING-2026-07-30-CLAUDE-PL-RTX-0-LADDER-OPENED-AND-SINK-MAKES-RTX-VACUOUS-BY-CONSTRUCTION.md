# FINDING 2026-07-30 — PL-RTX-0: THE THIRD RTX LADDER IS OPEN, STATIC RANKING IS FALSIFIED A SIXTH TIME, AND FOR PROLOG THE **SINK LADDER MAKES THE RTX LADDER VACUOUS BY CONSTRUCTION**

**Session:** s221-PL (first session of `GOAL-PROLOG-RTX.md`)
**Ladder:** `PL-RTX` — third RTX ladder, joining `SN4-RTX` and `ICON-RTX`
**Lon directive of record:** *"Notice how GOAL-SNOBOL4-RTX and GOAL-ICON-RTX are proceding with replacing the C runtime with highly optimized register-aware ASM code. You do the same. Join the coordination that is setup by the two, and y'all will be come three."*
**SCRIP baseline:** `b1ca896e` (unmodified this session — **zero source edits, measurement only**)
**RT_OPT:** `-O0` throughout. No `-O1`/`-O2` used or sought (O2-DIRECTED-ONLY).

---

## 0. WHAT THIS SESSION DID AND DID NOT DO

**DID:** opened the ladder, joined the ledger, ran step 0(a)–(d) on the whole Prolog surface, produced the committed ranking artifact, found two phantoms, and identified the correct first target.
**DID NOT:** write one byte of assembly. **This is deliberate and it is the protocol working**, not a session running short — s216-ICN and s217-ICN both refused rungs on step-0 measurement, and this session's measurement produces a **scope question that belongs to Lon** before any asm is justified (§5).

---

## 1. ⭐⭐ THE HEADLINE: FOR PROLOG, AN RTX PORT AND A SINK RUNG COMPETE FOR THE SAME SYMBOL BY OPPOSITE MEANS — AND SINK WINS BY CONSTRUCTION

`GOAL-PROLOG-BB.md` carries the **PL-SINK ladder**: rungs that make the EMITTER emit an *inline fast path* for a lowered `$op`, leaving the runtime `rt_pl_dop_*` function as a slow-path oracle. `PL-RTX` would instead rewrite that runtime function's BODY in asm.

**These are not complementary. An emitted inline fast path REMOVES the arrivals that an asm port of the callee would have accelerated.** Therefore:

> ⛔ **EVERY LANDED PL-SINK RUNG MAKES THE CORRESPONDING PL-RTX RUNG VACUOUS.**

**MEASURED PROOF — `rt_pl_dop_trail_mark`:**
- **5,814 static call sites** (rank 5 on the static surface — a static ranking would have made it an early rung)
- **22 dynamic calls across all 22 van Roy benchmarks** — exactly **1 per program**
- `hello.pl` also measures **1** ⇒ that single call is the **setup floor**, not run-phase work
- CAUSE, confirmed in the tree, not inferred: `src/templates/bb_call_fn.cpp:347` is the **PL-SINK-8 emitted `$trail_mark` fast path**, whose own comment names `rt_pl_dop_trail_mark` as *"the slow-path oracle."* PL-SINK-8's rung text predicted this exactly: *"Self-priming: the first call necessarily defers and resolves the cell."*
- ⇒ **An RTX port of this symbol moves the board by ZERO by construction.** 5,814 static sites of pure vestige.

⭐ **THIS IS THE FOURTH SHAPE OF THE BYPASSED-FAMILY DISEASE, AND IT IS NEW.** The three on record are: SN4's GVA slot island removing `NV_GET_fn`'s call sites; SN4's integer inlining bypassing `rt_num_arith`; and s211-ICN's `bb_coerce_numeric.cpp` inlining the cheap arms so `rt_coerce_num2_d` held **only the expensive arm**. s211 drew the rule *"port the arm the guard REJECTS."* **Prolog's trail family is a fourth case that rule does not cover: the callee is left holding NOTHING — not the expensive arm, but a once-per-process priming call.** It is not "port a different arm," it is "there is no rung here at all."

⛔ **AND IT FALSIFIES A CLAIM IN `GOAL-PROLOG-BB.md`:** PL-SINK-8's text says *"`$trail_mark` … pairs 1:1 with SINK-9 — take them together."* **Measured: 22 vs 2,114,931.** The 1:1 property held for *minting* (both are minted per predicate activation) and was destroyed the moment SINK-8 landed and SINK-9 did not. **A pairing claim between two rungs decays when one of them ships.** Same class as ARCH-SNOBOL4-RTX §5's *"a rung's premise decays when an unrelated rung succeeds"* — here the unrelated rung is the ladder's own sibling.

---

## 2. ⭐⭐ STATIC RANKING FALSIFIED AGAIN — SIXTH TIME ON THIS PROJECT, FIRST FOR PROLOG, AND THE WORST SPREAD YET

Corpus-wide dynamic counts, 22 van Roy/Aquarius benchmarks, mode 3, `RT_OPT=-O0`, counted with `scripts/util_rtx_count_syms.sh` (s217, SN4-RTX — **it transferred to Prolog with zero edits**, same result ICON-RTX reported for `util_rtx_arm_census.sh`).

| rank | symbol | corpus calls | reach | static sites | static rank |
|---:|---|---:|---|---:|---:|
| 1 | `rt_pl_dop_trail_unwind` | **2,114,931** | 10/22 | 5,666 | 6 |
| 2 | `rt_proc_call_open_det` | **2,060,043** | **19/22** | 5,291 | 8 |
| 3 | `rt_pl_dop_unify` | 1,108,786 | **22/22** | 15,240 | 2 |
| 4 | `rt_pl_dop_mkc` | 1,018,100 | 19/22 | **40,854** | **1** |
| 5 | `rt_pl_dop_cmp_ne` | **880,792** | 5/22 | **102** | **19** |
| 6 | `rt_pl_dop_unwind_nothrow` | 873,060 | 16/22 | 7,904 | 4 |
| 7 | `rt_pl_dop_is_v` | 735,898 | 14/22 | 779 | 13 |
| 8 | `rt_pl_dop_ax_sub` | 731,498 | 12/22 | 176 | 16 |
| 9 | `rt_pl_dop_unify_cs` | 622,812 | 12/22 | 11,021 | 3 |
| 10 | `rt_pl_dop_ax_add` | 573,678 | 6/22 | 348 | 15 |
| 11 | `rt_pl_dop_ix_g` | 289,004 | 15/22 | 1,800 | 10 |
| — | `rt_pl_dop_trail_mark` | **22** | 22/22 | 5,814 | 5 |
| — | `rt_proc_call_open` | **0** | **0/22** | 5,626 | 7 |
| — | `rt_faildescr` | **0** | 0/22 | 171 | — |
| — | `rt_call_arr_gen` | **0** | 0/22 | 498 | 14 |

**THE TWO EXTREMES, STATED PLAINLY:**
- **`rt_pl_dop_cmp_ne`: 102 static sites → RANK 5 by execution (880,792 calls).** Static rank 19 of 20.
- **`rt_pl_dop_mkc`: 40,854 static sites (rank 1, and 400× `cmp_ne`'s) → RANK 4 by execution.**
- ⇒ **the static surface is not merely noisy, it is INVERTED across a 400× site-count spread.**

**THREE MORE PHANTOMS-BY-EXECUTION, ~11,300 static sites between them:** `rt_proc_call_open` (5,626 sites, **zero calls in all 22 programs**), `rt_call_arr_gen` (498, zero), `rt_faildescr` (171, zero — note the ledger lists this as `DONE:SN4-RTX:416190f5` with **Prolog as beneficiary**; the beneficiary claim is real for correctness and **worth nothing for Prolog speed**).

---

## 3. ⛔⛔ TWO OF THE FOUR SYMBOLS `RTX-CLAIMS.md` NAMES AS PROLOG'S TOP SURFACE ARE DECLARATION-ONLY PHANTOMS

The ledger's prose (twice: the PROLOG section and the GATE section) ranks the Prolog surface as
*"`rt_pl_dop_mkc` **655** · `rt_pl_dop_unify` **495** · `rt_node_to_term` **378** · `resolve_cp_current` **348** · …"*

**MEASURED — step 0(a)/0(b), `grep` with `--include=*.S` and `nm -D --defined-only`:**
- **`rt_node_to_term`** — **2 occurrences in the entire tree, both declarations** (`src/runtime/rt/rt.h:60`, `src/templates/bb_common.h:24`). Zero definitions. Zero call sites. Absent from the `.so`.
- **`resolve_cp_current`** — **1 occurrence, a declaration** (`src/runtime/builtins/resolution.h:52`). Zero definitions. Zero call sites. Absent from the `.so`.

⇒ **A Prolog ladder that trusted the ledger's prose would have aimed rungs #3 and #4 at symbols that do not exist.** This is verbatim the RTX-3 class (`rt_concat`/`rt_lcomp`/`rt_acomp`, declaration-only in `rt/rt.h`) and the s204 NV class — **the sixth and seventh members of the phantom family, and the fifth time a rung's symbol list came from a DOCUMENT rather than the tree.**

⭐⭐ **AND IT FALSIFIES THE CAVEAT THAT WAS SUPPOSED TO CONTAIN IT.** The ledger annotates these very counts: *"COUNTS APPROXIMATE AND NOT TO BE QUOTED … **Presence is robust** (corruption drops matches, it does not invent symbol names)."* **Presence was NOT robust.** The reasoning was sound for the failure mode it modelled (pipe corruption) and blind to the one that actually occurred: the sweep matched **header declarations**, so it manufactured names that were never defined. ⇒ **"corruption cannot invent a name" is true; "therefore presence is robust" does not follow, because a DIFFERENT defect can.** A caveat that names one failure mode licenses nothing about the others.

✅ **THE REPAIRED GATE IS ALREADY CORRECT** — `scripts/util_rtx_claims.sh` (s216) uses `nm --defined-only` + `scrip --compile` and lists **neither phantom** in its UNLEDGERED-HOT output. **The tool was fixed; the PROSE IN THE SAME FILE was never re-derived from it.** Exactly RULES.md's stale-orientation class: *a document asserting a fact that nothing checks and nobody updates.*

---

## 4. ⭐ METHOD RESULTS THE OTHER TWO LADDERS SHOULD HAVE

**(a) ⭐⭐ THE COMPILE-PHASE CONFOUND DOES NOT EXIST FOR PROLOG'S `dop` FAMILY — MEASURED, NOT ASSUMED.**
ICON-RTX burned two sessions on it (s218 ranking voided at s220 as *"~100% compile"*), and its method of record is *rank by `count(4N) − count(N)`, the delta cancels compile phase exactly.* I adopted the delta method and then **measured the floor directly**: on `hello.pl` **every `rt_pl_dop_*` symbol counts ZERO** (`trail_mark` is the sole 1, and that 1 is the setup floor, §1). ⇒ **the `dop` family is emitted-code-only; the compile phase never reaches it, so for Prolog absolute counts ARE run-phase counts.** The delta method is still correct and still what I used for scaling; it is **not load-bearing for this family**. ⇒ **The confound is FAMILY-SPECIFIC, not universal** — Icon's contamination came from `rt_zeta_storage_get`/`rt_zc_frame_live`, which ARE the emitter. **Do not generalize either result across languages; measure the floor, it costs one `hello` run.**

**(b) ⛔⛔ A SINGLE-WORKLOAD RANKING WOULD HAVE MISSED THE RANK-1 SYMBOL ENTIRELY.**
I ranked twice before sweeping the corpus, on two hand-picked "representative" workloads with **exactly-4× scaling verified on both**:

| symbol | nrev N=25→100 | fib N=16→18 | corpus rank |
|---|---|---|---:|
| `rt_proc_call_open_det` | 13,226 → 52,901 (**4.00×**) | **0** | 2 |
| `rt_pl_dop_is_v` | (not in set) | 4,788 → 12,540 (**2.62×** = φ², exact) | 7 |
| `rt_pl_dop_mkc` | 750 → 3,000 (4.00×) | **0** | 4 |
| `rt_pl_dop_unify_cs` | 1,575 → 6,300 (4.00×) | **0** | 9 |
| **`rt_pl_dop_trail_unwind`** | **0** | **0** | ⭐ **1** |

**The corpus rank-1 symbol measures ZERO on BOTH of my scaled workloads, each of which passed 0(d) cleanly at exact scaling.** ⇒ **0(d) SCALING IS A PROPERTY OF THE (SYMBOL, WORKLOAD) PAIR, NOT OF THE SYMBOL.** A clean 4.00× is not evidence the symbol matters; it is evidence it matters *there*. **Both ladders' 0(d) practice ranks on one workload — this is the failure mode that produces, and it is silent.**

**(c) SCALED DRIVERS MUST DIFFER IN ONE TOKEN.** My N/4N drivers differ **only** in the loop count (`diff` = one line), so the compile phase is identical by construction rather than by argument. Cheap, and it makes (a)'s floor measurement interpretable.

**(d) ⚠ THE CORPUS IS CONCENTRATED — SAY SO WITH EVERY NUMBER.** `queensn` (7,806,872) + `queens` (2,642,243) are **~78% of all counted arrivals across 22 programs.** Third and fourth are `tak` (206,731) and `sendmore` (164,694) — an order of magnitude down. ⇒ **the ranking is substantially a statement about two backtracking-search programs.** Reach (programs-touched) is reported beside every count in §2 for exactly this reason, and it is why rank 2 outranks rank 1 in §5.

---

## 5. ⛔⛔ THE SCOPE QUESTION FOR LON — AND WHY NO ASM WAS WRITTEN

**Collision map, RTX ranking against `GOAL-PROLOG-BB.md`'s PL-SINK ladder:**

| RTX rank | symbol | PL-SINK rung | SINK status | consequence for PL-RTX |
|---:|---|---|---|---|
| 1 | `rt_pl_dop_trail_unwind` | **SINK-9** | ⏳ **OPEN** | ⛔ **COLLISION** |
| 2 | `rt_proc_call_open_det` | **none** | — | ✅ **CLEAR** |
| 3 | `rt_pl_dop_unify` | SINK-1 | ✅ landed s142 | ⚠ arrivals already reduced |
| 4 | `rt_pl_dop_mkc` | SINK-3 | ✅ landed s145 | ⚠ arrivals already reduced |
| 5 | `rt_pl_dop_cmp_ne` | **SINK-7** | ⏳ **OPEN** | ⛔ **COLLISION** |
| 6 | `rt_pl_dop_unwind_nothrow` | **SINK-9** | ⏳ **OPEN** | ⛔ **COLLISION** |
| 7 | `rt_pl_dop_is_v` | **SINK-5** | ⏳ **OPEN** | ⛔ **COLLISION** |
| 8/10 | `rt_pl_dop_ax_sub` / `_add` | **SINK-6** | ⏳ **OPEN** | ⛔ **COLLISION** |
| 11 | `rt_pl_dop_ix_g` | SINK-4 | ✅ landed s148, **kk==4 deferred** | ✅ the deferred arm is CLEAR |
| — | `rt_pl_dop_trail_mark` | SINK-8 | ✅ landed s146 | ⛔ **VESTIGIAL (§1)** |

**NINE of the top ELEVEN are either already-SINK'd or claimed by an OPEN SINK rung.** `GOAL-PROLOG-BB.md` is a **concurrently-running session** (RULES.md: 3–4 parallel sessions), so this is a live two-ladder collision on one symbol set — **precisely what `RTX-CLAIMS.md` was minted to prevent, arriving from a direction the ledger does not model: the contending ladder is not another RTX ladder, it is the same language's BB ladder.**

⭐ **QUESTION FOR LON (one ruling settles the ladder's whole scope):** for Prolog, when a symbol is hot and has an open SINK rung, does it get
**(a)** the SINK treatment (emitter inline fast path, `GOAL-PROLOG-BB.md`), or
**(b)** the RTX treatment (runtime body in asm, `GOAL-PROLOG-RTX.md`), or
**(c)** SINK for the fast arm + RTX for the arm SINK deliberately defers to C (SINK-4's `kk==4`, SINK-7's out-of-2⁵³ range, SINK-6's `div`/`idiv` guards)?

**I recommend (c), and it is the only option under which both ladders keep working:** SINK's inline path takes the arrivals it guards, so **RTX's honest scope is the residue SINK refuses** — plus symbols with no SINK rung at all. Under (a) the PL-RTX ladder has ~2 live rungs; under (b) two sessions would fight over one emitter/runtime boundary per symbol.

**⇒ FIRST RUNG, AND IT IS CLEAR UNDER EVERY OPTION: `rt_proc_call_open_det`.**
Rank **2** by execution (2,060,043), rank **1 by reach (19/22 programs — the broadest of any Prolog symbol)**, **no SINK rung**, **not a `dop`** (so structurally outside SINK's `$op` territory), Prolog-dominant (5,291 sites), **absent from the ledger entirely**, and in the CALL family where SN4-RTX has already paid for the lessons. Its sibling `rt_proc_call_open` measures **zero** for Prolog, so the `_det` variant takes the whole path — a fact only the dynamic sweep could show.
⛔ **Step 0 is NOT complete on it:** 0(c) (`nm` the OBJECT file, not the `.so`), 0(f-pre) (read the C body, enumerate arms, and check for the straight-line shape that discharges 0(f) in advance), and the emitter-side 0(g) read (does `bb_*` already inline a guard that steers arrivals away from the arm I would port?) are all owed **before** any asm.

---

## 6. GATES — ALL AT `b1ca896e`, ZERO SOURCE EDITS

- **Prolog watermark ESTABLISHED GREEN:** `test_prolog_rung_suite.sh` **164/164 interp + 164/164 compile, FAIL=0**, full build at `-O0`.
- **`scripts/util_rtx_claims.sh`** (`CUR_SESSION=221`): **3 FATAL / 36 WARN**, exit 1. ⛔ **All 3 fatals are pre-existing and belong to OTHER ladders' rows; I edited none of them** (protocol §"I did not edit your rows"):
  1. `rt_frame` — no definition in the `.so` AND no live call site ⇒ ledger rot. **ICON-RTX's row.** s216-ICN's own repair predicted this would fire on the first run and it does.
  2. `rt_defer_close` — assembly in `src/**/*.S`, row not `DONE` (step 0(e)). **SN4-RTX's row.** ⚠ **s216-ICN reported this to SN4-RTX five sessions ago and it is still open.**
  3. `rt_defer_open` — same.
- Surface swept: **1,367 Icon / 211 SNOBOL4 / 839 Prolog** programs, 204 call-surface rows.
- ⚠ `rt_binop_overload`: gate reports **zero live `@PLT` sites across all three surfaces** — the ledger allocates it to SN4-RTX as `FREE`. **Not my row; flagged, not marked.** (s216 already cautioned this warning was UNVERIFIED from the corrupted run — **it now reproduces on the repaired gate**, which upgrades it from unverified to confirmed-on-one-clean-run.)

### 6b. ⭐ A DEFECT I INTRODUCED, AND THE GATE CAUGHT IT IN ONE RUN — **THERE IS NO SUCH THING AS A DOCUMENTATION-ONLY LEDGER ROW**

Building the PL-RTX section I added a row for **`putchar`** annotated *"libc, stays libc (Ruling 2)"* —
purely to document why it appears at 197 static sites and is not a target. The gate went **FATAL**
immediately: *"putchar: no definition in the built .so AND no live @PLT call site — ledger rot"*, taking
the run from 3 fatal to 4. **It is right:** a libc symbol has no definition in `libscrip_rt.so`, and the
PHANTOM check polices **every row in the table** without caring why the row was added.
⇒ **ANYTHING THAT IS NOT A REAL PORT TARGET MUST LIVE IN PROSE, NOT IN A ROW.** Moved to prose; gate back
to the 3 inherited fatals. ⭐ **The useful part is the shape: I reached for the table to make a fact
VISIBLE and thereby made a false assertion the gate could see — which is exactly the anti-rot machinery
working on its author in its first session.** Both other ladders should know before annotating a libc or
declaration-only name into a table.

**WATERMARK:** SCRIP `b1ca896e` **UNMODIFIED** (measurement only) / corpus `<none>` / `.github` this FINDING + `GOAL-PROLOG-RTX.md` + `ARCH-PROLOG-RTX.md` + `RTX-CLAIMS.md` (Prolog rows, unledgered-line deletion, message board) — **PUSH BLOCKED, credential needed.**

---

## 7. HANDED TO THE OTHER TWO LADDERS (mirrored to `RTX-CLAIMS.md`'s message board)

**→ ICON-RTX:** your compile-phase confound is **family-specific, not universal** — measured zero for Prolog's `dop` family (§4a). Your delta method is right and I used it; **the floor measurement is one `hello` run and it tells you whether the delta is load-bearing.** And **your `util_rtx_arm_census.sh` transfer result now has a sibling: SN4's `util_rtx_count_syms.sh` also ran on Prolog with zero edits.** Deriving symbol lists from the tree is why both transferred — that design choice has now paid off across three languages.
**→ SN4-RTX:** your `rt_faildescr` port lists Prolog as beneficiary; **it measures ZERO calls in all 22 Prolog benchmarks** — the beneficiary claim is sound for correctness and worth nothing for Prolog speed. Same shape as your own `NV_GET_fn` finding, in a third language. **And two of your `rt_defer_*` rows have been FATAL on the ledger gate since s216.**
**→ BOTH:** §4b is the one that should change your practice — **0(d) scaling is a property of the (symbol, workload) PAIR.** My corpus rank-1 symbol measured ZERO on two independent workloads that each passed 0(d) at exact scaling.
**→ BOTH:** §3 — **"presence is robust" is falsified**; the ledger's own prose carries two declaration-only phantoms that the repaired gate correctly omits. Re-derive prose from the gate, or delete it.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
