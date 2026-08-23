# FINDING: claws5 1.69x → 1.36x and json 3.28x → 2.37x — four resolutions redone on every call that the COMPILER already knew the answer to; plus json's real input is measurable and always was

**Seat:** hq_P · **Date:** 2026-08-23 (s266) · **Trees:** SCRIP `80a01c63` → `05f11c4c` → `e64adaeb`, corpus `1267f605f`. All pushed.
**Lon, in-chat:** *"Get CLAWS5 and JSON SNOBOL4 working faster than SPITBOL by 2x-3x. The theory SPITBOL is a thread-code interpreter."*

**Instrument:** callgrind Ir at FIXED WORK, **SLOPE** method — Ir(N=k) − Ir(N=1), ÷(k−1) — so process startup, dynamic linking, input read and (for SPITBOL) compile are removed from BOTH engines by construction. RT_OPT=**`-O0`** (FACT RULE). SCRIP **mode-4 native binary** vs `/home/resources/spitbol-bench-oracle/sbl -bf -d512m -i64m -s16m`. **Both engines on the REAL corpus input**, and every arm's output diffed against the committed `.ref` before any number was believed.

## THE RESULT

⛔⛔⭐ **REPORTED IN THE FORM LON RULED THE SAME SESSION (s266 FACT RULE, `.github/RULES.md`): ONE AXIS, ONE WORD, DECLARED ONCE.** The multiple is `SPITBOL / SCRIP` — one divisor, **above 1 faster, below 1 slower** — and the word lives in the header, never both words down a column.
**SHARED AXES:** callgrind **Ir**, **SLOPE** basis (N=k minus N=1 — no totals, no startup), **RT_OPT=`-O0`**, SCRIP **mode-4 native**, ζ **cell-stack**, oracle `/home/resources/spitbol-bench-oracle/sbl -bf -d512m -i64m -s16m`, every arm output-diffed against its `.ref`. Input is per-row; all three rows are throughput runs on the real corpus file, no grading `.input` run.

| workload | SPITBOL Ir/iter | SCRIP before | SCRIP after | **× FASTER than SPITBOL, before → after** |
|---|---|---|---|---|
| **claws5** (66,757-byte CLAWS5inTASA) | 35,979,478 | 60,935,438 | **49,020,916** | 0.590 → **0.734** |
| **json** (631,514-byte json.dat) | 70,808,401 | 232,405,141 | **167,757,920** | 0.305 → **0.422** |
| claws5 grammar only (`-match`) | 1,770,544 | 1,087,882 | 1,087,891 | 1.628 → **1.628** |

−19.6% and −27.8% of our own instruction count. ⛔ **The ruled target is `2.000`–`3.000` on that column; we are at 0.734 and 0.422** — claws5 needs 18.0M Ir/iter and json 35.4M to reach 2.000.
⛔ **`beauty` is NOT in this table and must never be added to it:** it is one shot, a whole-program TOTAL carrying process startup, and a total may not share a column with a slope. RUNG P-0 below carries it in its own grid for that reason.

## ⭐⭐ THE INSTRUMENT FIRST: json's REAL INPUT IS CALLGRIND-MEASURABLE, AND THE FINDING THAT SAID OTHERWISE WAS WRONG ABOUT THE MECHANISM

`FINDING-2026-08-23-hq_P-claws5-is-not-a-pattern-problem-and-json-is-4x-not-2x.md` § 4 recorded json on the 631 KB input as NOT measurable: *"N=1 and N=3 return the same Ir … the signature of a program that quit early, not a fast one."* The observation was right and the diagnosis was wrong. It is a **valgrind stack overflow** — SCRIP's recursive-descent json blows valgrind's 64 MB simulated main stack:

```
==753558== Stack overflow in thread #1: can't grow stack to 0x1ffe001000
==753558==  ... try to increase the size of the main thread stack using the --main-stacksize= flag.
```

`valgrind --main-stacksize=4000000000` and it runs to completion, answering `check: 1264/1050/4754/2108/1/2791/1946/10` — byte-identical to the oracle and to `json.ref`. ⭐ **The 400-nested-single-member-object proxy is RETIRED.** Every json number in this file is the real deserializer on the real document, facing SPITBOL's own real-input slope.

⛔ **THE TRANSFERABLE LESSON, AND IT IS THE SIBLING OF "non-empty is not alive": THE PROGRAM PRINTED ITS CHECK LINE ANYWAY.** A truncated run under valgrind still emitted plausible stdout, so the only tell was the equal-Ir pair. When two N's disagree with the slope model, suspect the INSTRUMENT before concluding anything about the program.

## THE DEFECT CLASS LON'S THEORY NAMED

A threaded-code interpreter binds a name to a code address **once**. SCRIP was re-deriving four separate bindings **from strings, on every call**. Every cure below is the same shape: *the answer cannot change, so stop asking.*

### 1. The alpha cell is resolved once per PROCEDURE, not once per call — claws5 −5.1%, json −5.7%
`rt_call_proc_descr` called `rt_dyn_alpha_fn` on every SNOBOL4 function call. That rebuilt `"alpha$<name>"` into a stack buffer, FNV-hashed the concatenation, and linear-probed the emitter's cell table: **402 Ir per call** (json 29,573 calls/parse, claws5 6,469). The cell table is a fixed-extent file-static, so a name maps to ONE slot forever; only the slot's CONTENTS are mutable (OPSYN, re-DEFINE), and those are still re-read every call. The slot index is now cached in the proc record. **402 → 83 Ir.**
⭐ `alpha_slot` occupies the 4-byte alignment **hole** that already sat between `decl_level` and `byref_mask`, so `sizeof(rt_proc_t)` stays 128 and every offset `rtx_call.S`/`rtx_plcall.S` bakes is unmoved — asserted at build time, not assumed.

### 2. `rt_proc_find`'s memo could never hit — claws5 & json, folded into the above
The pointer-keyed memo validated with `g_rt_gen_procs[ci].name == name`. That can only hold when the CALLER's string literal is the same object as the REGISTRATION literal — it never is. So the memo missed 100% of the time and every call paid a full FNV hash plus probe. Validated by `strcmp` now, exactly as `core.c`'s NV memo already was (and for the same stack-buffer hazard it documents). **203 → 75 Ir.**

### 3. ⭐⭐ `.VAR` is a CONSTANT and is now lowered as one — **json −12.8% of the whole program**, claws5 −7%
`.dummy` lowered to a runtime `IR_CALL` of the builtin `SNO$NAME` with the name as a string-literal operand. That paid the entire by-name dispatch chain (`rt_call_arr_bl` → `setjmp` → `rt_call_arr_impl` → `try_call_builtin_by_name_bl`) and then `bn_sno_name`, whose whole body is `rt_ws_strdup` of a name **the compiler already had in `.rodata`**. **644 Ir per evaluation.** `x = .dummy` is the SNOBOL4 return-by-name idiom, so it sits in the body of EVERY deferred action: **43,487 evaluations per json parse**, 6,469 per claws5 parse.
New `IR_LIT_NAME` joins the existing LITERAL family in `bb_lit_scalar` (INTEGER/STRING/CHARSET/REAL) rather than getting a private path, and emits the identical descriptor `bn_sno_name` built — `{ v = DT_N, slen = 0, s = <name text> }` — with the text now the permanent literal instead of a fresh workspace copy per call.
⭐ Side effect worth noting: the old path minted a NEW pointer for the same name on every call, which is why the NV memo downstream could never hit on it either.

### 4. The table READ half is asm — claws5 −6.5%
`rt_subscript_var_container_only` is the read half of every SNOBOL4 table subscript — `mem[num][wrd][tag]` is **fourteen of them per CLAWS5 token** — and at `-O0` the C wrapper cost **55 Ir to reach a lookup that then cost 79**: two 16-byte struct copies gcc makes because `DESCR_t` is passed by value, the spill of all four incoming registers, and a tag chain. 42% of a hit, none of it the lookup. Now in `rtx_table.S` beside the lookup it wraps: **55 → 18.75 Ir**. Narrow guard, the standard RTX shape — only a plain `DT_T` base runs there; `DT_A` tail-jumps to `rt_subscript_var` (already asm, and exactly the C's own tail call), a VARREF base and the error arm tail-jump to the unchanged C of record.
⛔ The MISS arm tail-jumps to a new C leaf `c_rt_svco_miss_d` rather than copying `TBBLK_t.dflt`'s offset and NULVCL's bit pattern into the `.S`. **A copied constant has no build-time witness.**

### 5. ⭐ Charset membership is a 256-bit map, not a rescan of the needle — json −5.9%
`rt_sg_scan_member`/`nonmember` walked the WHOLE needle for EVERY subject byte — **O(subject × needle)**, 6 + 5·len instructions per byte. On json that was **7.7% of the program**: `BREAK` over a 4-character cset touches essentially every one of the 631,514 input bytes. The needle is now burned once into 32 bytes of the leaf's own frame (`btsq`, bit-string form) and each subject byte costs a load, a shift and one register `bt`: **10 instructions, independent of needle length.**
⛔ The linear arms are KEPT and still run below the crossover (len < 3, or fewer than 2 bytes left) — building the map costs ~4 + 5·len before the first byte is read. **A size crossover, not an op filter.**
⛔ The leaf now touches 32 bytes of its own stack, which its header note said it never did; the note is corrected in place. NUL-safety is unchanged — the map is indexed by byte VALUE, so 0 is an ordinary member and nothing is length-terminated.

### 6. The pattern-variable snapshot slot is read in place — json −3.2%
Every `*jvalue`/`*jelement` reference re-resolves the pattern variable at match time: `patv_slot` was entered **316,517 times per parse** (17 per value node), and `rt_patv_defer_get_pat_dtp` then called `dtp_fn_of` on top of it — three call frames to hand back a pointer already sitting in a snapshot slot. `patv_slot` remains the C of record and still owns every arm; only its FIRST LINE, the three-load snapshot hit, is hoisted into its three callers.
⭐ The `dtp_fn_of` skip is an **identity**: the head is what gets returned, `dtp_fn_of` is called purely for its side effect (compile the blob on first use) and its result is discarded — so with `->fn` already non-null, which is `dtp_fn_of`'s own "nothing to do" condition, the call cannot change the answer.
⛔ Written out rather than made `always_inline` **on purpose**: s264 measured that `always_inline` on the descr.h/core.h tag predicates broke three deferred-capture tests by moving descriptors out of memory where the GC's stack scan could no longer see them — and `pattern_match.c` IS the deferred-capture engine. Three lines of stated duplication is the cheaper risk.

## GATES

Every commit gated on a **`make pristine` EXIT=0** build: corpus **m3 359/1, m4 359/1 SKIP=0** — the single fail is the deliberate `demo_treebank` red, in both modes. `test_gate_emit_no_lang` rc=0, `test_gate_template_medium_invisible` rc=0. The RTX killswitch `SCRIP_RTX_TABLE=0` was negative-tested: both demos answer identically with the asm off. `.s` artifacts regenerated in RULES order (corpus `1267f605f` and its four parents).

## ⭐⭐ WHERE THE REMAINING TIME GOES — MEASURED, RANKED, AND THIS IS WHERE THE NEXT SESSION STARTS

Object-file split of the slope, which is the number that decides strategy:

| | claws5 49.0M (0.734 FASTER) | json 167.8M (0.422 FASTER) |
|---|---|---|
| **runtime `libscrip_rt.so`** | **77.8%** | **63.1%** |
| emitted BB code | 17.2% | 32.5% |
| libc | 5.0% | 4.4% |

⭐ **SPITBOL HAS NO EMITTED CODE AT ALL, AND STILL WINS — SO THE GAP IS ENTIRELY THE RUNTIME SERVICES, NOT THE CODEGEN.** This confirms RUNG P-0's shape at a much finer grain and it is the whole strategy: the emitted code is not where the multiple lives.

**claws5 self/iter, top of the list:**
| Ir/iter | share | what |
|---|---|---|
| 7,513,796 | 15.3% | emitted blob `0x401951` (the token() body) |
| **7,188,359** | **14.7%** | `table_find_pair_d` — already asm, 79 Ir × 90,566 calls |
| **4,539,549** | **9.3%** | `table_set_descr_d` — **C at -O0, 253 Ir/call. THE NEXT RUNG.** |
| 2,495,163 | 5.1% | `NV_SET_fn` |
| 2,333,839 | 4.8% | `rt_dcap_pump` |
| 2,044,204 | 4.2% | `c_rt_subscript_var` |
| 1,697,746 | 3.5% | `rt_subscript_var_container_only` (was 4,982,596) |

**json self/iter, top of the list:** emitted action bodies `ekey_α` 13.2M / `estr_α` 10.8M / `eobj_α` 6.7M and two `match_defer` regions 9.6M + 8.7M; then `rt_patv_defer_get_pat_dtp` 11.0M (6.5%, now carrying patv_slot's work — **46 Ir/call for four loads and three compares, a prime asm target**), `NV_SET_fn` 8.7M (5.2%), `c_rt_defer_close` 7.0M (4.2%), `rt_dcap_pump` 6.1M (3.6%), `rt_subscript_var` 5.1M, `rt_sg_scan_member` 4.9M (down from 14.0M), `rt_agg_alloc` 4.7M.

**RANKED NEXT RUNGS:**
1. ⭐⭐ **`table_set_descr_d` in asm — 9.3% of claws5, 2.2% of json.** ⛔ It needs the HASH SHARED with `table_find_pair_d`, not a call to it: an update-only fast path built on the existing find was costed and is a NET LOSS (claws5 is ~62% inserts, and each insert would pay the hash twice — +0.88M against −1.05M). Factor the hash arms into a callable `rt_tbl_hkey_d` first; that is the rung, and it also cheapens the find.
2. **`rt_patv_defer_get_pat_dtp` in asm — 6.5% of json.** Four loads and three compares should not cost 46 Ir; it is the `-O0` `DESCR_t`-by-value tax again, the identical shape cure 4 just removed from the table read.
3. **`NV_SET_fn` — 5.1% claws5 / 5.2% json, 139 Ir/call.** Its fast path is a memo hit and a store. The `strcmp` validation inside `_var_find_cached` is a PLT hop; the protected-pat-vars filter and `rt_sxt_break` are two more calls before the store. ⛔ An asm port is blocked by NO-NEW-GLOBALS (the memo arrays are file-statics in core.c with no exported cell) — so this one is a C-level cure or it needs an in-chat grant.
4. **The by-name builtin dispatch scaffolding — ~370 Ir per call** (`rt_call_arr_bl`'s `setjmp` + `rt_call_arr_impl` + `try_call_builtin_by_name_bl`'s preamble), 5,857 calls/iter claws5 and 6,951 json. The bid is already resolved at COMPILE time and passed in `bidlen`; the preamble still re-derives the dtax probe (including a `memcmp` that is redundant when the slot was indexed BY bid). Worth ~150 Ir/call, class-wide, no per-op filter needed.
5. **`_tbl_grow` fires on 59% of claws5 inserts** and is STILL not to be touched blind — `aggregates.c:342`'s floor-1-vs-floor-4 measurement stands, Ir and cache-misses disagree in opposite directions, and Ir is the only instrument here. Unchanged from s264.

## ⛔ TWO DEFECTS STANDING, BOTH hq_C's, BOTH UNAFFECTED BY THIS WORK
- `rt_dcap_pump` floods `CORRUPT CAPTURE ENTRY refused — … (target 'seg', frame depth 2)` on stderr for the real `json.dat`, in **BOTH m3 and m4** (`jdec`'s escape-decode path). stdout's census is still byte-correct, so it does not block a number — but it is a live wrong-answer risk on string CONTENT, which the census cannot see. ⭐ Newly reachable, not newly broken.
- `SCRIP_GC_STRESS=7` SIGSEGV on the 5-byte witness `[1,2]` (passes at off / 25 / 1).
