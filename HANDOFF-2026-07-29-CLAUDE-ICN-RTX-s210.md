# HANDOFF-2026-07-29-CLAUDE-ICN-RTX-s210 — THE ELEPHANT IS `rt_parse_num_d` (480k, `static`), AND 42–64% OF THE BOARD WAS INVISIBLE UNTIL THE LAST HOUR

**Session:** s210-ICN · **Ladder:** `GOAL-ICON-RTX.md` · **Landed:** MEASUREMENT ONLY — no asm, no `src/` edit.
**Gate at close:** Icon **252/11/30** (re-derived fresh 3×, unchanged) · `out/libscrip_rt.so` md5
**`93498e12f6075fad7e1836ee6b818679`** == pristine · `git status` on SCRIP = two untracked `tools/` files.

---

## ⛔ READ THIS FIRST — I CORRECTED MYSELF TWICE. THE THIRD RANK IS THE ONE TO USE.

Three ranks were produced this session. **Only the third is valid.** The first two are recorded because
the corrections are the transferable content:

| # | rank taken over | why it was WRONG | corrected by |
|---|---|---|---|
| 1 | `queens`/`deal` whole-process | **compile-phase dominated ~20:1** — top three were the EMITTER (`rt_zeta_storage_get` &c.) | scale run work 4×, hold compile fixed; rank by `count(4N)−count(N)` |
| 2 | delta, names via `dladdr` | **`dladdr` reads `.dynsym` only ⇒ CANNOT SEE `static` FUNCTIONS. 42–64% of all traffic was reported as `?`** | emit load-relative offset, symbolize against full `.symtab` (`nm`, no `-g`) |
| **3** | **delta + offset-symbolized** | ✅ **USE THIS** | — |

---

## ⭐⭐ THE CORRECTED RUN-PHASE RANK (compile-phase cancelled, statics resolved)

| run-phase Δ | symbol | scan | list | note |
|---:|---|---:|---:|---|
| **480,000** | **`rt_parse_num_d`** | 480,000 | 0 | ⭐⭐ **`static` in `rt.c` — THE ELEPHANT. Was invisible to every prior instrument.** |
| 315,000 | `rt_subscript_var` | 0 | 315,000 | ⛔ **SN4-RTX's** (`OUT:SN4-RTX:s204`) |
| 315,000 | `rt_list_view` | 0 | 315,000 | `static`; same subscript path |
| 315,000 | `IS_VARREF_fn` | 0 | 315,000 | same subscript path |
| 240,000 | `rt_substr` | 240,000 | 0 | ⭐ **ICON-OWN, SCAN family, UNCONTESTED** |
| 240,000 | `rt_coerce_num2_d` | 240,000 | 0 | ICON-RTX `FREE` — **but see below, it is a WRAPPER** |
| 135,000 | `rt_add` | 120,000 | 15,000 | ARITH |
| 15,000 | `rt_scan_enter` / `rt_scan_leave` | 15,000 ea | 0 | once per scan ENV, not per OP — **16× colder than `rt_substr`** |

**⭐ THE BOARD IS ANALYTICALLY SELF-CONSISTENT — check it yourself before trusting it:**
- `rt_parse_num_d` 480,000 = **exactly 2 ×** `rt_coerce_num2_d` 240,000. `rt.c:289-290` calls it **twice**. ✓
- subscript trio = 315,000 = **21 × 15,000 iterations** = the workload's 20 writes + 1 read. ✓
- `rt_substr` = 16/iteration = 8 words × (`tab` + `move`). ✓
Every top entry has a closed-form explanation. **A rank without one is not finished.**

---

## ⭐⭐ THE CONSEQUENCE THAT MATTERS MOST

**`rt_coerce_num2_d` IS A 10-LINE WRAPPER AND ITS CALLEE IS 2× HOTTER.** `rt.c:285-294` is two
`rt_parse_num_d` calls plus a `DT_R`/`DT_I` select. ⇒ **RTX-6-ICN as written would port the wrapper and
leave the elephant in C**, winning only `-O0` frame ceremony. This is inbox gap #1 ("the PORTABLE fraction
is UNMEASURED") answered concretely for one symbol: **the portable fraction is the small half.**

⇒ **THE REAL TARGET IS `rt_parse_num_d`.** It is `static`, so it has **no `@PLT` boundary and no exported
symbol** — the existing kill-switch idiom (`RTX_GATE`, C body → `c_*`) assumes an exported symbol and
**does not apply unchanged.** Porting it requires either exposing it or porting it together with its two
callers. ⛔ **That is a contract question for `ARCH-ICON-RTX.md` §4, not a session's improvisation.**

---

## ⛔ TWO ITEMS FOR LON

1. **`rt_subscript_var` is Icon's #1 *exported* run-phase symbol (315k) and is checked out to SN4-RTX**,
   allocated on a **static** near-tie (Icon 177 / SN4 195). **The allocation rule in `RTX-CLAIMS.md` is
   written over static counts, which this ladder has now falsified FOUR times** (s188; s203-ICN top-three;
   s210 compile-phase; s210 static-invisibility). **Recommend: allocate on DYNAMIC count where one exists,
   static as prior only.** I did not open the symbol.
2. **RTX-0-RULING(b)** (SCAN family → `.S` vs BB template) is **still open and now blocks RTX-2-ICN**,
   because the recommended target `rt_substr` is in that family.

---

## ▶ NEXT SESSION — DO THESE IN ORDER

1. **`bash scripts/test_icon_all_rungs.sh` — expect 252/11/30.** Re-derive, never hand-copy.
2. ⭐ **NEW STEP 0(h) (proposed, in the ladder): `grep -l "Rung:.*<RUNG>" FINDING-*.md` BEFORE opening any
   rung.** This session re-did RTX-0d in full because the checkbox was stale. The FINDING set is truth.
3. **Re-run the rank with `tools/rtx_icn_profile.c`** — it is complete and works; recipe below. **Extend
   it past scan/list**: the proc and I/O shapes have not been offset-symbolized, so **their statics are
   still unmeasured** and there may be a second elephant there.
4. **THEN** pick the target. Do not open `rt_arg_stage` (ledger: `BLOCKED:MEASURED-ZERO`), and do not open
   `rt_call_arr` (closed twice: scales with `write`, not with calls).

### Recipe — the instrument, end to end (no Makefile edit, no `src/` edit)
```bash
gcc -O2 -fPIC -shared -o /tmp/rtxp.so tools/rtx_icn_profile.c -ldl
rm -rf out/rt_pic
make libscrip_rt RT_OPT="-O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer \
     -finstrument-functions" -j4                       # RT_OPT is ?= , so this overrides cleanly
# run the SAME program at N and 4N; the delta cancels compile-phase exactly
RTXP_OUT=/tmp/a.tsv LD_PRELOAD=/tmp/rtxp.so ./scrip --run prog_N.icn
RTXP_OUT=/tmp/b.tsv LD_PRELOAD=/tmp/rtxp.so ./scrip --run prog_4N.icn
nm --defined-only -n out/libscrip_rt.so | awk '$2=="t"||$2=="T"{print $1"\t"$3}' > /tmp/symtab.tsv
# symbolize col-3 offset against symtab (bisect); rank by b-a.  ⛔ NOT by the dladdr name in col 2.
rm -rf out/rt_pic && make libscrip_rt -j4              # ⛔ RESTORE, then md5 vs pristine
```
⚠ **COUNTS ONLY, NEVER TIME** — instrumentation inflates every body; no ratio may be quoted from it.
⚠ **ALWAYS restore and md5-check the `.so`.** It was verified byte-identical twice this session.

---

## ⛔ STILL BLOCKING, UNCHANGED — RTX-0b-ICN

**The Icon corpus has no legal window AND no profilable program.** All 10 runnable benchmarks are
**6–30 ms vs `MIN_MS=800`**; at that size compilation dominates a profile ~20:1. `scrip --run p.icn -n8`
⇒ `cannot open '-n8'` — **mode 3 does not forward argv**, so the corpus's own scaling knobs are
unreachable (s203-ICN could scale `queens` only because it drove mode-4 linked binaries). ⇒ 0b owes
**(a)** argv forwarding in mode 3 *or* famsets carrying N internally, and **(b)** authored scaled
workloads. Until then: counts yes, time no. Every workload used this session is hand-written
(`/tmp/icn/*.icn`, recreate from the FINDINGs) — **none came from the corpus.**

---

## FILES

**New (untracked, SCRIP):** `tools/rtx_icn_profile.c` (signature-free `-finstrument-functions` ranker —
**use this one**) · `tools/rtx_icn_interpose.c` (LD_PRELOAD per-symbol counter; superseded for ranking,
still fine for a single known symbol).
**New (.github):** `FINDING-2026-07-29b-…-CALL-ARR-SCALES-WITH-WRITE-…` ·
`FINDING-2026-07-29c-…-COMPILE-PHASE-CONFOUND-AND-THE-RUN-PHASE-RANK` (⚠ **its rank is version 2 — the
statics correction above supersedes its table; the method sections stand**).
**Modified (.github):** `GOAL-ICON-RTX.md` — RTX-0d closed, LIVE CURSOR rewritten, step 0(h) proposed.

⛔ **NOTHING PUSHED.** No credential was supplied and `scripts/handoff_status.sh` verbatim stdout is the
only sanctioned completion claim — it was not run.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
