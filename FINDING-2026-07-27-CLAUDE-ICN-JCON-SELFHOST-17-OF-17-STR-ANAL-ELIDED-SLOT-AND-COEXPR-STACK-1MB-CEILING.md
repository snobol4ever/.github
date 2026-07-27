# FINDING (2026-07-27, s168 Opus 4.5) — JCON self-host 10/17 → **17/17**; two root causes closed

**SCRIP `72da0cab` + 2 runtime fixes · Icon suite 250/11/32 UNCHANGED (zero regression, measured twice) · RT_OPT=-O0**
**Oracle: Arizona Icon 9.5.25a built from uploaded source. NO JAVA USED — bytecode compared as DATA per the 2026-07-21 Lon directive.**

---

## HEADLINE

Every one of the **17 JCON translator modules now compiles under SCRIP-jtran to the same class count as the
`icont`/`iconx` oracle**, up from 10/17 at s167. SCRIP-jtran compiles its own 17 sources — self-host at
class-count parity.

| | s167 | s168 |
|---|---|---|
| Modules at oracle class-count parity | 10/17 | **17/17** |
| Icon suite | 250/11/32 | 250/11/32 (unchanged) |

⚠ **PARITY IS CLASS-COUNT + SIZE, NOT BYTE-IDENTITY.** Every module still reports `SAMECOUNT_DIFF`. Total
emitted bytecode 2,103,240 (SCRIP) vs 1,904,811 (oracle) = **1.10×**. `ast` and `ir` are byte-for-byte
EQUAL IN SIZE (3505/3505, 3005/3005) yet still differ — consistent with the known `key()` constant-pool
ordering defect, which is NOT fixed here. Do not call this a completed self-host.

---

## ROOT CAUSE 1 — `str_anal` elided-slot defaulting (the s167-named blocker, plus a piece it missed)

s167 named "elided start-position argument in `many`/`any`". Confirmed, and it is a **general `str_anal`
defect**, not a `many`/`any` quirk.

**MEASURED, NOT INFERRED.** Instrumented the dispatch arms and read the descriptors:

```
many('ab',"aab",,0)  -> nargs=4  a[2].v=0 (DT_SNUL)  <- elided slot arrives as a genuine null descriptor
upto('b',"aab",,0)   -> nargs=4  a[2].v=6 (DT_I) .i=1 <- arrives pre-materialized, which MASKED the bug
```

The arms tested only POSITIONAL presence (`nargs >= 3`) then read `args[2].i` → `i1 = 0` → tripped the
`i1 <= 0` guard → fail. `upto` "worked" only by accident of its slot arriving as integer 1; it carried the
same latent defect.

**⭐ THE PIECE s167 MISSED: the two blocked modules elide the SUBJECT, not just the position.**
- `lexer.icn` L218/L234: `many('0123...',,,&pos+2|0)` — s null, i null, j given
- `preprocessor.icn` L312/L400: `match("_",,-1)` — s null, i given

Canonical `str_anal` (`refs/icon-master/src/runtime/fstranl.r` L11-62) requires **s null → s = `&subject`,
and if i also null → i = `&pos`**. SCRIP had no such path at all. So `match` needed the same fix — s167's
write-up scoped the defect to `many`/`any` and would not have closed `preprocessor`.

### Fix (`src/runtime/by_name_dispatch.c`)

Two static helpers transcribed from canonical source, then `any`/`many`/`upto`/`match` routed through them:
- `bn_cvpos()` — faithful `cvpos` (`refs/icon-master/src/runtime/cnv.r` L880): range-check `-len..len+1`,
  non-positive maps `len + p + 1`. The old code's `if (i2 <= 0) i2 = slen + 1` was correct only for 0.
- `bn_str_anal()` — null-descriptor slots treated as ABSENT (`DT_SNUL`, the idiom already used by `list()`
  at the same file); s-null → scan env; j default `StrLen(s)+1`; the canonical `i > j` swap.

`match` already had the `DT_SNUL` guard for i/j (from FINDING-2026-07-24) but not the s-null path — that
partial fix is why the defect looked narrower than it was.

### Verification
| | pre | post | oracle |
|---|---|---|---|
| 9-form argument matrix | 7/9 | **9/9** | — |
| 5 JCON-shaped elided-subject cases | 0/5 | **5/5** | — |
| Icon suite | 250/11/32 | 250/11/32 | — |

Modules closed by this fix alone: **preprocessor 8→29, lexer 6→8, gen_bc 42→87, optimize 3→17.**

---

## ROOT CAUSE 2 — **NEW, in no prior doc: the 1 MB co-expression stack ceiling**

After fix 1, three modules still failed: `do_ops` (0 classes, SEGV), `interface` (0, SEGV), `bytecode` (9/50).

`gdb` backtrace on `do_ops`:
```
Thread 2 "jtran" received signal SIGSEGV
#0  bid_of (s=0x60d639 "IDENTICAL", len=9) at builtin_ids.h:321
#1  try_call_builtin_by_name ... #3 rt_call_arr ... #4 n78921_call_builtin_α
```
`bid_of` is a bounds-masked lookup into a `static const` table — **it cannot fault on its own.** Faulting
there, in a co-expression pthread, at an arbitrary leaf, is the **stack-overflow signature**.

`src/runtime/rt/rt_coexpr.c` L18: `static long g_coexp_stksize = 1024 * 1024;` — **1 MB, hardcoded, no
override.** SCRIP boxes recurse on the native C stack, so deep Icon recursion inside a co-expression
exhausts it. `jcont` gives the oracle `COEXPSIZE=1000000`, but that sizes an INTERPRETER stack, not a
native one — the two are not comparable budgets.

### Decisive sweep (correctness is monotonic in stack size)
| stack | do_ops | interface | bytecode |
|---|---|---|---|
| 1 MB | 0 | 0 | 9 |
| 2 MB | 0 | **65** | 9 |
| 4 MB | **4** | 65 | 9 |
| 8 MB | 4 | 65 | **50** |

### Fix
Default 1 MB → **8 MB**, plus a `SCRIP_COEXP_STACK` (bytes) env override, floored at `PTHREAD_STACK_MIN`.

⚠ **DO NOT JUST MAKE IT HUGE.** 64 MB was tried first: correct, but `irgen` went **3410 → 26140 ms (7.7×
WORSE)**. Under the default `ZC_COEXPR_STACK_GCHEAP=1` each coexpr stack is carved from the GC heap AND
registered as a **GC root range** (`rt_gc_root_range_add`), so the collector scans the whole stack every
cycle. Stack size is a direct GC-scan cost. At 8 MB the cost is nil (`irgen` 3896 vs 4258 ms at 1 MB — noise).

---

## PERFORMANCE — SCRIP vs Arizona Icon, all 17 modules

Best-of-3 wall clock. **SCRIP `RT_OPT=-O0`; `iconx` built `-O`. Asymmetric in SCRIP's disfavor.**

| Module | SCRIP ms | iconx ms | ratio |
|---|---|---|---|
| ast | 22 | 13 | 1.69× |
| ir | 19 | 11 | 1.73× |
| keyword | 18 | 9 | 2.00× |
| gen_symbolic | 67 | 31 | 2.16× |
| jtran_main | 55 | 24 | 2.29× |
| parse | 571 | 249 | 2.29× |
| gen_ucode | 829 | 339 | 2.45× |
| dump | 88 | 35 | 2.51× |
| gen_dot | 81 | 32 | 2.53× |
| gen_bc | 1779 | 687 | 2.59× |
| optimize | 367 | 130 | 2.82× |
| preprocessor | 404 | 140 | 2.89× |
| do_ops | 611 | 188 | 3.25× |
| interface | 907 | 265 | 3.42× |
| lexer | 276 | 76 | 3.63× |
| irgen | 3537 | 842 | 4.20× |
| bytecode | 2908 | 530 | 5.49× |
| **GEOMEAN** | | | **2.69× slower** |
| **TOTAL** | 12,539 | 3,601 | **3.48× slower** |

s167 reported 2.22× geomean over 10 modules. The 17-module geomean is 2.69×; the seven newly-working
modules are among the slower ones, so **this is not a regression — it is a larger, more honest sample.**
Cross-session geomean comparison over different module sets is invalid.

Translator build: `scrip --compile` 17 mods = **3.98 s → 514,385 asm lines, 0 bombs**; `icont -u -s` 17 mods
= **74 ms** (bytecode, not native — not a like-for-like number).

---

## STILL OPEN

- [ ] **`ir.class` 9.59× blowup PERSISTS** — 142,497 (SCRIP) vs 14,860 (oracle) inside `irgen`. Next worst:
      `ir_a_Case` 1.79×, `ir_a_Key` 2.01×. Untouched by this session, matches s167's 9.6× exactly. Separate
      JVM-bytecode-generation defect; this is the single biggest remaining divergence.
- [ ] **Byte-identity** — every module `SAMECOUNT_DIFF`. `key()` constant-pool ordering still the prime suspect
      (`ast`/`ir` differ at IDENTICAL size, which is that signature).
- [ ] **rc=139 at EXIT on 5 modules** (preprocessor, lexer, gen_bc, bytecode, irgen) — all write their FULL
      correct class set, then segfault on the way out. Post-output teardown, not a codegen fault. Likely a
      second, smaller instance of the coexpr-teardown path; `bytecode` still crashes at 8 MB while producing
      all 50 classes, so it is NOT simply "needs more stack".

## FILES TOUCHED
- `src/runtime/by_name_dispatch.c` — `bn_cvpos` + `bn_str_anal` added; `any`/`many`/`upto`/`match` rewritten
- `src/runtime/rt/rt_coexpr.c` — coexpr stack 1 MB → 8 MB + `SCRIP_COEXP_STACK` override

## REPRO
```bash
bash scripts/jcon_selfhost_build.sh          # SKIP its step 7 (javac) — banned
bash /home/claude/sh1.sh <module>...         # per-module SCRIP-vs-oracle class-count + byte compare
bash /home/claude/bench.sh <module>...        # best-of-3 timing
# oracle needs jcont's regions: BLKSIZE=6000000 STRSIZE=1000000 COEXPSIZE=1000000
```
⚠ **The oracle jtran CRASHES (error 302 / heap corruption) without those three env vars.** An oracle that
crashes is not an oracle; a sweep that does not set them silently grades SCRIP against nothing.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus
