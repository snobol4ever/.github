# FINDING s217-ICN — `subscript_get2`'s FAST ARM WOULD HAVE BEEN VACUOUS, AND THE ROOT CAUSE IS THAT `DESCR_t.slen` IS NEVER POPULATED FOR ICON STRINGS

**Session:** s217-ICN (2026-07-29) · **Ladder:** `GOAL-ICON-RTX.md` · **Contract:** `ARCH-ICON-RTX.md`
**Rung:** RTX-9-ICN (`subscript_get2`, Icon section `x[i:j]`) · **Result: NO ASM WRITTEN, BY MEASUREMENT**
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

---

## ⭐⭐ HEADLINE — THE ARM CHECK PAID FOR ITSELF ON A VIRGIN SYMBOL, ONE SESSION AFTER BEING ADOPTED

`subscript_get2` passed **every** step-0 check, including the two that matter most, and the port was
still refused — because the arm the asm would have covered **cannot commit even once**.

| check | result | verdict |
|---|---|---|
| 0(a) definition | `pattern_match.c:350` | PASS |
| 0(b) spelling | plain ASCII, no Greek | PASS |
| 0(c) `nm` linkage | `T subscript_get2`; callees `T rt_str_alloc` / `T VARVAL_fn` / `T rt_ws_alloc` | PASS |
| 0(e) not-already-asm | 0 hits in `src/**/*.S` | PASS |
| 0(f) `call …@PLT` | 52 sites | PASS |
| 0(i) compiler sweep | **52**, re-derived (sharded, byte-class, 316 programs) | PASS |
| **0(d) scaling** | **50,000 → 200,000 at N → 4N, exactly 4×** | **PASS** |
| **0(g) arm dist** | **DT_S 100%** synthetic / **97.2%** corpus | **PASS** |
| **⛔ commit-ability** | **`arr.slen == 0` on 100% of arrivals ⇒ fast arm bails to C every time** | **REFUSE** |

⇒ **A SYMBOL CAN PASS 0(d) AND 0(g) TOGETHER AND STILL HAVE A DEAD PORTABLE ARM.** 0(d) says the symbol
is hot and scaling. 0(g) says which *tag* arm arrivals take. **Neither asks whether the arm's own
internal preconditions hold.** Here the tag arm is 100% correct — `DT_S` — and the *sub*-condition
inside it (`slen` usable without a `strlen`) is 0%.

---

## 1. THE MEASUREMENT

Instrument: private LD_PRELOAD interposer (`/tmp/icnsect_interpose.c`), **not** the shared
`tools/rtx_icn_interpose.c` — that file is a documented rebase point (`ARCH-ICON-RTX.md` §7 item 4) and
this rung needed a different measurement anyway. The interposer bins arrivals by
`arr.v = lo & 0xFFFFFFFF`, which is the dispatch variable itself, so **0(g) is obtained mechanically
with no source edit and no guessing.**

```
synthetic (50,000 sections)   arrivals=50000  DT_S=50000  slen==0 = 50000  slen usable = 0
real corpus (jcon_substring)  arrivals=   37  DT_S=   37  slen==0 =    37  slen usable = 0
                              i.v==DT_I = 100%      j.v==DT_I = 100%
```

Cost decomposition (the virgin-symbol form of 0(j), per the s216 amendment — the census cannot run
before a `c_*` body exists):

```
rt_str_alloc  50,000 -> 200,000   exactly ONE per call, scales with the symbol
rt_ws_alloc      185 ->      185  FLAT: startup only, the list arm is never taken
rt_list_view       0 ->        0  dead
array_get2         0 ->        0  dead
```

⭐ **This is the INVERSE of `rt_make_list` (RTX-8d, refused s216).** There `rt_ws_alloc` fired **3× per
call** with two hidden inside variadic `DATCON_fn`, so the portable fraction was ~nil. Here there is
**exactly one** callee allocation and the rest of the body is integer arithmetic. **The portable
fraction was GOOD. The rung still failed, on a different axis entirely** — which is why the two
refusals must be recorded as different diseases and not merged into "small symbols aren't worth it."

---

## 2. ⛔⛔ THE ROOT CAUSE, AND IT IS BIGGER THAN THIS RUNG: `slen` IS DEAD WEIGHT

`DESCR_t` carries `uint32_t slen` at offset 4 (`src/contracts/descr.h:30`). The convention is
**`slen == 0` means "length unknown, call `strlen`"** and `slen == 0xFFFFFFFF` means CSET.

**Measured: Icon strings carry `slen == 0` universally.** Not "usually" — 50,000/50,000 synthetic and
37/37 in a real corpus program, across a string literal, a subscripted section, and a concatenation
result.

**THIS IS THE SAME ROOT CAUSE THAT KILLED `rt_size_d`'s PORTED ARMS AT s213** — that rung recorded
*"Real Icon strings carry `slen==0` (lazy) ⇒ bail to C"* and its DT_S arm was measured DEAD. **The
finding was written down and the ladder did not generalize it.** One session later it was about to
consume a second rung. ⇒ **A ROOT CAUSE RECORDED AS A PER-RUNG FOOTNOTE WILL BE PAID FOR AGAIN.**

**CONSEQUENCE, WHICH IS THE REAL PRIZE:** every string operation in the shared runtime that consults
`slen` takes the `strlen` path. `slen` is a 4-byte field in every one of millions of descriptors,
maintained by nobody and trusted by no one. **Populating it at string-construction time would:**
- make `rt_size_d`'s **already-written, already-landed, currently-dead** asm arms LIVE (s213's rung
  becomes retroactively real at zero asm cost);
- give this rung's fast arm a 100% commit rate instead of 0%;
- delete `strlen` calls across SNOBOL4, Prolog, Snocone, Raku and Pascal, not just Icon.
⇒ minted as **RTX-16-ICN** below. ⚠ Shared runtime, so it owes all three watermarks, and any consumer
that currently relies on NUL-termination while ignoring `slen` must be audited first.

---

## 3. ⭐ WHAT CANONICAL ICON AND JCON DO — NEITHER COPIES, AND SCRIP ALWAYS COPIES

Read per `ARCH-ICON-RTX.md` §7 step 1 (the ICON and JCON sources for every construct the family
implements):

| | string section `s[i:j]` |
|---|---|
| **ICON** `src/runtime/oref.r:571` | `return string(j, StrLoc(dx)+i-1)` — a descriptor **into the parent**. Zero copy, zero allocation. Immutability makes it safe. |
| **JCON** `jcon/vString.java:70` | `vString.New(s,i,j)`: **reuses `s` outright** if the section is full-length; returns interned `nullstring` if empty; returns an **interned single character** from `strlist[]` if `len==1`; only otherwise constructs. |
| **SCRIP** `pattern_match.c:388` | `rt_str_alloc(len)` + `memcpy` + NUL — **unconditionally copies, every time.** |

⛔ **PORT ≠ FIX, for the third time on this ladder** (RTX-8c's `dat_field_get` name scan, RTX-8d's
3-allocs-per-list, now this). **An asm port makes the copy fast; adopting either reference design
deletes the copy.** ⇒ minted as **RTX-15-ICN**.

⚠ **BUT NOT A FREE LUNCH, AND THIS IS WHY IT IS A DESIGN RUNG AND NOT A PATCH:** SCRIP's zero-copy
section is only sound if `slen` is authoritative, because a view is not NUL-terminated at its own end.
**RTX-15 is therefore GATED ON RTX-16** — the same `slen` defect blocks both. JCON's three fast paths
(full-length reuse, empty, interned single char) are the cheap subset and need no `slen` work, but
this rung's corpus showed **len==0/1/whole = 0 occurrences**, so their measured value here is nil.

---

## 4. THE RUNG'S DISPOSITION, STATED PLAINLY

**`subscript_get2` is RELEASED to `FREE` in the same session (ABANDON rule).** Not abandoned for lack
of time — **refused on measurement**, like RTX-8d.

⛔ **AND A SECOND, INDEPENDENT REASON TO REFUSE, WHICH WOULD STAND EVEN IF `slen` WERE FIXED:**
**corpus reach is 141 arrivals across all 303 Icon programs**, in 10 programs. For scale, on this same
ladder: `dat_field_get` 320,000 in one bench · `rt_list_bang_at` 21,086 · `rt_jct_relop` **4,308, and
at that number the ladder already declined to make a corpus-wide claim.** 141 is an order of magnitude
below the weakest figure this ladder has ever accepted.

⭐ **THE TRAP I ALMOST WALKED INTO, RECORDED BECAUSE IT IS STRUCTURAL AND WILL RECUR: I WROTE THE HOT
WINDOW MYSELF.** My synthetic loop drove 200,000 arrivals and looked like a strong 0(d). It was hot
**because I chose the construct and the loop count.** The corpus says 141. ⇒ **0(d) ON A
SELF-AUTHORED BENCHMARK MEASURES THE BENCHMARK, NOT THE SYMBOL.** s208's inbox gap #3 said this about
inheriting *another language's* window; it is sharper when the window is your own. **0(d) needs a
corpus-derived denominator, not just a scaling ratio.** Proposed as a step-0 amendment: report
`arrivals_in_corpus` beside the scaling factor, and refuse a *speed* rung below a stated floor.

---

## 5. ⭐ THE ONE PREDICTION THAT HELD: 0(g)'s SUB-RULE IS NOW THREE-FOR-THREE

`bb_section.cpp` emits six register loads, `call subscript_get2`, and tests `eax == DT_FAIL` only
**after** — **no inline tag guard**, the same shape as `bb_field_get.cpp` and `bb_unop`.
**Prediction was stated in this session's log BEFORE measuring** (RTX-4's "state the expectation so a
null is informative", used prospectively): the cheap/string arm would dominate. Measured **100%**.

| rung | symbol | guard | cheap arm |
|---|---|---|---|
| s214 | `rt_str_coerce` | none | 93.1% |
| s216 | `dat_field_get` | none | 100% |
| **s217** | **`subscript_get2`** | **none** | **100%** |

⇒ **"UNGUARDED CALL ⇒ CHEAP ARM DOMINANT" has now held three times and may be treated as
predictive.** Guarded calls remain unpredictable in both directions (RTX-6 first-arms-dead vs RTX-6b
both-ends-live). ⚠ **AND THE NEW LIMIT OF THE SUB-RULE, PAID FOR HERE: it predicts which TAG arm
arrivals take. It says NOTHING about whether that arm's internal preconditions hold.** 100% cheap-arm
and 0% commit-able are compatible, and this rung is the proof.

---

## 6. LEDGER / GATE STATE

- `RTX-CLAIMS.md`: `subscript_get2` checked out `OUT:ICON-RTX:s217`, then released `FREE` same session
  with the refusal recorded. No gate added; no eleventh family gate; **not a ledger event.**
- **Icon watermark, re-derived fresh pre-edit: `test_icon_all_rungs.sh` = 252 PASS / 11 FAIL / 30 XFAIL
  (293 total).** Baseline `.so` md5 **`6f71f2b5843c2057c7b940347f61b1ff`**, recorded at session start
  per s216's own owed action. **No source file was modified, so no post-edit gate is owed.**
- ⚠ **`util_rtx_claims.sh` reports BLOCKED — 3 FATAL, all pre-existing and all already documented:**
  `rt_frame` (ledger rot, no definition — s213 diagnosed, still unfixed) and `rt_defer_open` /
  `rt_defer_close` (**SN4-RTX's** rows, asm but not `DONE`; s216 already notified them and I likewise
  **did not edit another ladder's rows**).
- ⚠ Segfaults/aborts observed during corpus interposer sweeps — the documented harness blind spot
  (`test_icon_all_rungs.sh` grades stdout, discards exit code). Watermark unchanged; **not bisected.**
- ⚠ **PROTOCOL DEVIATION (SIXTH session running): no credential ⇒ the check-out commit
  (`.github ad1fc79f`) is LOCAL ONLY and was NOT pushed before the work.** The protective property of
  the claim was not obtained. The s202 ancestry check is not satisfiable.
  **`scripts/handoff_status.sh` is the only completion truth and it will say BLOCKED.**

---

## 7. RUNGS MINTED HERE

- **RTX-16-ICN — POPULATE `DESCR_t.slen` AT STRING CONSTRUCTION.** ⭐⭐ Outranks every remaining `.S`
  port on this ladder: it retroactively activates `rt_size_d`'s already-landed dead arms, unblocks
  RTX-15, and removes `strlen` calls in five other languages. Runtime-side ⇒ **no `.s` regen, no
  collision with the ζ ladder.** ⚠ Audit every consumer that reads the pointer and ignores `slen`
  first; `IS_CSET_fn` (`DT_S && slen==0xFFFFFFFF`) shares the field and must be tested before `DT_S`
  (the bug s213 introduced and fixed inside `rt_size_d`).
- **RTX-15-ICN — ZERO-COPY STRING SECTION.** Adopt ICON's view (`string(j, StrLoc+i-1)`) or JCON's
  three fast paths. ⛔ **GATED ON RTX-16** — a view is not NUL-terminated at its own end.
- **`subscript_get2` itself: NOT-A-SPEED-TARGET** at 141 corpus arrivals. Revisit only as a
  *completeness* rung after RTX-16, when the fast arm can actually commit.
