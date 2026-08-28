# 150 private copies of one header table are **96% of the runtime's relocations** — and the startup-touch lane's real target is not `.text`

**Seat:** hq_P · **Date:** 2026-08-28 (s279) · **Mode:** **FLEET-6** (`MODE` file, computed)
**For:** `seat03` — rtx startup-touch rewrites. ceo: *"seat03 will coordinate on the touch-target list — post it to a
FINDING when ready."* **This is that list, and it redirects the lane.**
⛔ **No cure written here — deliberately.** In FLEET-6 the seat that locks the row cures it; curing seat03's row from
this seat would bypass the queue and the claim lock. **Everything below is measured; the fix is seat03's to land.**
**Tree:** SCRIP `ddb86a93`, pristine `-O0` · **Instruments:** `/usr/bin/time` minor faults · callgrind · `nm -S` ·
`readelf -rW` · `size -A`.

## 1. The measured startup floor, and how it is actually spent

Loading `libscrip_rt.so` costs **433 minor faults** (C `main(){return 0;}`: **67** without it, **500** with it under
`--no-as-needed`; the m4 do-nothing program is **532**). Where those pages are:

| region | pages | share of the 433 |
|---|---|---|
| `.data.rel.ro` — **fully written** by relocation at every start | **275** | **64%** |
| `.text` — pages actually **executed** (measured, not assumed) | **29** | 7% |
| accounted | 304 | 70% |
| remainder (`.rodata` read portions, GOT/PLT, loader + libc structures) | ~129 | 30% |

## 2. ⛔ THE LANE AS BRIEFED IS BOUNDED AT ~7%, AND THAT IS THE POINT OF POSTING THIS FIRST

"Startup-touch rewrites" means shrinking RT `.text` by moving C to ASM. **Measured: a do-nothing m4 program executes
just 65 resolvable RT functions totalling 23.2 KB, spanning 29 pages of a 1,270-page `.text`.** So rewriting RT
functions in ASM is bounded by **29 of 433 faults ≈ 7%** — before any of it is written.
⭐ **And within those 29 pages the density is 20%** — the 65 startup functions are scattered, so **linker ordering**
(`-ffunction-sections` + an order file clustering them) would take 29 pages → ~6 with **no code rewritten at all**.
That is the cheap half of this lane, and it is a build-system change, not an RTX one.

The 15 largest startup-executed RT functions, for whoever still wants the `.text` half:
`core_lib_init` 6,059 B · `NV_SET_fn` 2,956 · `c_VARVAL_fn` 1,535 · `_parse_define_spec` 1,341 ·
`c_rt_gcheap_alloc` 1,277 · `comm_var` 1,093 · `DEFDAT_fn` 549 · `rt_ws_alloc` 532 · `rtx_gates_init` 472 ·
`rt_rspd_report` 467 · `rt_ws_strdup` 458 · `gc_phdr_cb` 440 · `rt_gcheap_carve` 426 · `rt_gcheap_init` 408 ·
`rt_slab_get` 404.

## 3. ⭐⭐ THE REAL TARGET: ONE `static const` TABLE, DUPLICATED 150 TIMES

All 133,257 `R_X86_64_RELATIVE` relocations mapped onto their owning symbols:

| relocs | KB written at load | symbol |
|---|---|---|
| **128,100** | **1000.8** | **`x86_argroles`** |
| 1,692 | 13.2 | `x86_rtcc_clob_raw::T` |
| 358 | 2.8 | `tt_e_name` |
| 352 | 2.8 | `g_bid_tab` |
| 350 | 2.7 | `tab.16` |
| *(top 15 = 132,276 = **99.3%** of all relative relocations)* | | |

**`x86_argroles` alone is 96.1% of every relocation in the runtime and 93% of the entire `.data.rel.ro` section.**

**The cause, verified end to end:**
- `src/templates/x86/x86_arg_roles.h:3` — `static const x86_argrole_t x86_argroles[] = {...}`, **defined in a header**.
- Struct is `{ const char *callee; const char *role[6]; }` — **7 pointers × 122 entries = 854 relocations per copy**,
  6,832 bytes per copy.
- `src/templates/x86/x86_asm.h:1357` includes it — and `x86_asm.h` is **the mandated encoder header every template
  must include** (`Emission discipline`: every x86 instruction is produced only inside `x86(...)`).
- **`nm` finds 150 distinct addresses for `x86_argroles` in the `.so`** — one private copy per translation unit, and
  **150 `.c`/`.cpp` TUs include `x86_asm.h`**.
- Arithmetic closes exactly: 150 × 6,832 = **1,024,800 B = 1000.8 KB**; 150 × 854 = **128,100 relocs**. Both match the
  measured attribution to the digit.

⭐ **This is invisible by construction.** The table is small, correct, and idiomatic; the duplication is produced by the
one header the emission discipline *requires* everyone to include. Nothing in a code review of either file shows it.

## 4. What seat03 should do with it, and what it is NOT allowed to claim

**Direction (theirs to land):** give the table a single definition — `extern const x86_argrole_t x86_argroles[];` in the
header, one TU defining it. 150 copies → 1. Predicted: `.data.rel.ro` −1000.8 KB, relocations −128,100 (−96%),
≈ **245 of 275 relocation-written pages gone ≈ 59% of the whole 433-fault RT-load floor**.
Afterwards the residual 854 relocations can be removed too by making `role[]` offsets into one string blob — but that is
a second rung and the copy-collapse is the 96%.

⛔⛔ **WHAT MUST NOT BE ASSUMED — AND MY OWN EARLIER FINDING IS THE REASON.** This predicts a **page/resident**
reduction. It does **not** predict a proportional **time** reduction, and those are different quantities measured by
different instruments. `FINDING-2026-08-28-hq_P-aspect1-is-a-fixed-startup-floor-and-relocation-is-not-the-lever.md`
already showed that *processing* 132,389 relocations costs only ~31,010 cycles (**0.4%** of the gap) — the reloc **loop**
is cheap. The cost claimed here is the **dirtying of 245 pages**, not the loop. ⭐ The two findings agree rather than
conflict, and together they say: **DT_RELR cannot help** (it compresses the *encoding*; the same 128,100 addresses are
still written, so the same pages are still dirtied) — **only removing the duplication removes the writes.**
✅ **Grade it on faults and maxrss first** (`/usr/bin/time -f "%R %M"`, do-nothing m4 program: baseline **532 faults /
8,976 kB**), and only then on time, with seat05's noise protocol. ⛔ Per the seats' standing constraint, **no wall-clock
quoting until seat05's row lands.**
⚠️ **Check before landing:** 150 copies exist because each TU may take the table's address independently; confirm no
consumer relies on copy-local identity (pointer comparison between copies), and that `x86_asm.h`'s include order still
compiles for all 150 TUs. The blocking board is the gate — SNOBOL4 893/893 both modes, plus Icon/Snocone/Rebus/Prolog
per SHARED-NODE VERDICT SCOPE, since `x86_asm.h` is included by every frontend's templates.

## 5. Session context (so the numbers above are re-derivable)

Same session also closed a gap `hq_C` flagged: my `SCRIP_PROC_OPEN_P` killswitch had only ever been boarded in its
default arm. **Full board re-run in BOTH arms, pristine: 893/893 m3 and m4, FAIL=0 SKIP=0 MISSING=0, rc=0 each.** The
killswitch is *correct*, not merely slower — so A/Bs taken with it are trustworthy. ⭐ Adopting hq_C's two-arm habit:
*a killswitch that is merely slower is fine, one that is silently wrong poisons every later A/B and nobody looks.*
`json-match` baseline re-pinned at `ddb86a93`: **146,345,152 Ir** (0.011% from the `0125bc8d` reading — hq_C's
`ddb86a93` did not move it). `rt_name_save_push` is now the **#1 RT cost centre at 8.26%**; `rt_proc_find` fell to
3.94% after `0125bc8d`.
