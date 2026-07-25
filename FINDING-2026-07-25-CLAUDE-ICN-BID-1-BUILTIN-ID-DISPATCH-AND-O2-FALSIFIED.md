# FINDING-2026-07-25-CLAUDE-ICN-BID-1-BUILTIN-ID-DISPATCH-AND-O2-FALSIFIED

**Session:** s159 · **Author:** Claude Opus 4.5 · **Goal:** GOAL-ICON-BB (perf)
**SCRIP tree:** BID-1 landed on top of `0620ed86`. Icon suite **PASS=249 FAIL=12 XFAIL=32** at
BOTH `RT_OPT=-O0` and `RT_OPT=-O2` — zero regression, byte-identical to the s158 baseline.

---

## ⛔ HEADLINE — `-O2` ON THE RUNTIME `.so` IS **NOT** THE BIG LEVER. IT IS 1.15×.

Three separate LIVE CURSOR entries (s156, s157, s158) named `-O2` on `libscrip_rt.so` as
"the biggest untried lever" and deferred it pending a Lon directive. **It has now been tried
and MEASURED, and the claim is FALSIFIED.** Directed by Lon in-session; run under the full
s126 protocol (forced `rm -rf out/rt_pic`, detached + polled, worktree verified populated at
5,113 files BEFORE, `.so` mtime verified moved 14:59:49 → 15:16:44 and size 22MB → 215MB AFTER,
build log contains zero `O0`).

| Configuration | honest geomean vs iconx | gain |
|---|---|---|
| s158 HEAD, `RT_OPT=-O0` | **0.566×** | — |
| + BID-1, `RT_OPT=-O0` | **0.644×** | 1.14× |
| + BID-1, `RT_OPT=-O2` | **0.742×** | 1.15× |

**WHY IT IS ONLY 1.15×:** the dominant cost is an **O(n) algorithm**, not slow instructions.
`-O2` makes each step of a linear scan cheaper; it cannot make the scan not-linear. Callgrind
on `tgrlink` AT `-O2` still shows `try_call_builtin_by_name` as the #1 cost at **20.13%** with
`__strcmp_avx2` #2 at **13.90%** — i.e. **~34% of the program is STILL by-name dispatch after
`-O2`.** Every future perf claim must be labeled with its `RT_OPT` level (s126 rule); the
Makefile default REMAINS `-O0` and was not touched.

**COROLLARY — do not spend another session hunting `-O0` micro-levers.** s156/s157/s158 falsified
eight of them (alloc-pool, subscript-deref fusion, accessor-inline, asm-rt_subscript_var,
setjmp, arithmetic dispatch, global hash, GC churn). This session adds `-O2` itself to that
list. The remaining gap is STRUCTURAL and is named below.

---

## ✅ BID-1 LANDED — integer-ID builtin dispatch (`scripts/gen_builtin_ids.py`)

**MEASURED MOTIVATION (callgrind, `tgrlink`, `RT_OPT=-O0`):**

| | Ir | share |
|---|---|---|
| `__strcmp_avx2` | 1,155,365,976 | **34.46%** |
| `try_call_builtin_by_name` | 745,785,777 | **22.24%** |

**≈52% of the whole program was linear builtin-name lookup.** `try_call_builtin_by_name` is a
~1,730-line function containing **197 `!strcmp(fn, "literal")` tests over 176 distinct names**.
The pre-existing `g_dtax` 256-entry cache short-circuits ONLY constructors/synonyms (kinds
1/2/4/5); a real builtin (kind 0/3) sets `_dx_hit` and then **falls through the entire chain
anyway**. Measured: **41,603,682 `strcmp` calls**, ~9.7 per invocation surviving even the
early arms, from only **533,135 invocations**.

**THE TRANSFORM (mechanical, semantics-preserving by construction):**
`scripts/gen_builtin_ids.py` rewrites every `!strcmp(fn, "X")` → `(_bid == BID_X)` and emits
`src/runtime/builtin_ids.h`: a **compile-time-generated open-addressed table** (176 names,
1024 slots, max probe 6, djb2) plus `bid_of()`. One hash at function entry replaces up to 197
string compares. **A name absent from the table hashes to id 0, which equals no `BID_*`
constant, so an unknown name falls through the chain exactly as before** — that is the
correctness argument, and it is structural rather than empirical.

Non-`fn` comparisons (`strcmp(tag.s,"list")`, `strcmp(idb->fields[fi], fn)`, etc. — 26 sites)
were deliberately left alone; the generator only matches the exact `!strcmp(fn, "…")` form and
**refuses to run** if a name contains an escape sequence (sanitizer not proven for that case).

**RESULT at `RT_OPT=-O0`:** Ir **3,353,115,596 → 2,319,397,549 (−31%)**.

| program | before | after | speedup |
|---|---|---|---|
| tgrlink | 434ms | 296ms | **1.47×** |
| rsg | 7ms | 5ms | 1.40× |
| ipxref | 76ms | 61ms | 1.25× |
| geddump | 307ms | 256ms | 1.20× |
| deal | 73ms | 68ms | 1.07× |
| concord | 91ms | 87ms | 1.05× |
| queens | 67ms | 67ms | 1.00× |

`queens` is flat because its inner loop is subscript/alloc-bound, not dispatch-bound — which is
also why the s158 cursor's `rt_subscript_var` lead pointed at a function that is only **0.60%**
of `tgrlink`. **Profile the program you are actually trying to speed up.**

---

## ▶ NEXT RUNG — THE ONLY STRUCTURAL LEVER LEFT: COMPILE-TIME BUILTIN/FIELD RESOLUTION

At `-O2` post-BID-1, `tgrlink` = 1,805,514,281 Ir:

| function | share | note |
|---|---|---|
| `try_call_builtin_by_name` | 20.13% | chain is now 197 **integer** compares — cheap per step, still **O(n)** |
| `__strcmp_avx2` | 13.90% | record-field scan at dispatcher entry + `strcasecmp` siblings |
| `VARVAL_fn` | 13.20% | 6,630,400 calls, all from guarded arms — real work, not waste |
| `__strcasecmp_avx2` | 5.81% | by-name field/type lookup |

**BID-1 made each chain step ~6× cheaper (24 instr → ~4). It did not make the chain O(1).**
The real fix is the one the LIST-SLOT-ACCESS cursor already named for fields, generalized to
builtins: **resolve the name to an integer at COMPILE time in the lowerer and emit the
integer**, so the runtime never sees a name at all. Two halves:

1. **Builtins** — `lower_icon.c` resolves a call whose callee is a known builtin to its `BID_*`
   at lower time; the emitted box passes the int. `try_call_builtin_by_name` keeps the string
   path only for genuinely dynamic callees. Removes most of the 20.13% + a large share of 13.90%.
2. **Record fields** — Icon's classic global field numbers. `bb_field_get.cpp` currently emits
   `dat_field_get(fname, obj)` BY NAME; needs a per-record-type field-number table so
   `dat_field_get` is an int index, not a `strcasecmp` scan.

**A goto/label switch-dispatch over the existing chain was CONSIDERED AND REJECTED this
session:** the chain's top level is not a clean run of `if` blocks (there is an unconditional
`{ size_t _fl = strlen(fn); switch(((unsigned)_fl<<8)|fn[0]) … }` SNOBOL4-uppercase block plus
other top-level statements), so a blind `goto` past them would skip live code. Do not attempt it
without first proving the top level contains no unconditional statements.

**ALSO CONSIDERED AND REVERTED (deliberately, not by failure):** a direct-mapped memo cache over
the record-field scan at dispatcher entry, keyed on `(DATBLK_t*, fn)` **pointers**. Correct only
if a `fn` buffer's CONTENTS can never change under a stable address. That could not be proven
here, a stale hit would be silently wrong, and the 293-program suite would not reliably catch it.
Keyed on content instead it costs a hash + one `strcmp`, which only pays when `nfields > ~2`.
**If someone revives this, key it on CONTENT and verify on every hit.**

---

## Measurement notes

- Oracle: Arizona Icon **v9.5.25a**, built from the uploaded `icon-master` source
  (`make Configure name=linux && make`) → `bin/icont`, `bin/iconx`. Confirmed a **bytecode
  interpreter** (`iconx` = `switch((int)lastop)` over `Op_*` in `interp.r`); no `iconc` in this distro.
- Runner: `scripts/honest_icon_bench.sh` (s158) — DIFFS output against the oracle. Use it, never
  `test_icon_bench_corpus.sh`, which grades `rc==0 && non-empty` and cannot tell "ran fast" from
  "skipped the workload."
- Startup floor measured, NOT a factor: `hello.icn` = SCRIP ~4-6ms vs iconx ~1ms vs `/bin/true`
  ~1ms. The gap on the corpus is compute, not process startup.
- `geddump` emits 13,645L vs oracle 12,568L — a **pre-existing real divergence at HEAD**,
  unrelated to this work; its timing is therefore not a valid comparison.
- Container: **1 core**. The `-O2` runtime build took ~16 minutes wall (234 TUs).
