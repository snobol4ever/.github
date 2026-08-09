# FINDING — 2026-08-09 — Claude Opus 5 — RTCC s6: RC-5 candidate census CORRECTED + fibonacci RTCC=1 SIGSEGV at HEAD (UNATTRIBUTED)

**Session:** s6 of GOAL-RTCC.md (Opus 5)
**SCRIP HEAD at session open:** `79cf3d1d` — **NOT** the `979f0db7` claimed by the LIVE CURSOR
**SCRIP HEAD at close:** `79cf3d1d` (unchanged — **this session made zero code changes**)
**Deliverable:** docs-only. No rung attempted, no rung landed, no revert.

---

## 0. Why no rung landed

Two blockers surfaced before any implementation could honestly begin:

1. The RC-5 candidate list in the LIVE CURSOR is **wrong on all three candidates** when
   measured against emitted code (§2). Selecting from it would have repeated the
   static-rank-is-not-hotness trap already recorded twice in this goal's history.
2. A **reproducible SIGSEGV under `SCRIP_RTCC=1` at HEAD** (§3) means the rail
   baseline is not currently trustworthy. Landing a perf rung on top of a crashing
   arm would measure noise.

Per RULES.md (no unproved claims, crater attribution requires builds), this session
stopped and documented rather than pushing a rung through.

---

## 1. Orientation drift — LIVE CURSOR was six commits stale

The cursor stamped `979f0db7`. Actual `main` HEAD at open was `79cf3d1d`, six commits
later, including work from **concurrent seats on other goals**:

| commit | subject (truncated) |
|--------|---------------------|
| `79cf3d1d` | AB-2: ACT-ANCHOR + native floaters (dual-arm) + monitor-tap relocation |
| `2d2c2cf5` | feature x86 .s artifacts: regen |
| `befbe212` | N02-FIX: zls_fct_finalize span/rspan gate on pfield presence |
| `6c34731f` | feature x86 .s artifacts: regen |
| `ada979eb` | ICN-FR-5: fix CALL_VALUE apply path + DT_E=0x38 in rtx_icncall.S — PASS 243→246 |
| `1eeb4f16` | feature x86 .s artifacts: regen |

This is the documented cost of the concurrent-seat model, not a fault of s5. It does
mean **the RC-5-GVA 1.036x/1.028x rail numbers were measured on a tree that no longer
exists**, and have not been re-proved at `79cf3d1d`.

---

## 2. CENSUS — the RC-5 candidate list is wrong on all three candidates

**Method.** All 21 SNOBOL4 benchmarks at `/home/claude/corpus/benchmarks/snobol4/*.sno`
compiled with `SCRIP_RTCC=1 ./scrip --compile F` (**note: asm goes to stdout; the `-o`
flag silently produced nothing in this session — redirect instead**), then counted in
the emitted `.s`.

**Calibration:** `[r9`-relative GVA accesses = **1052** (s5 reported 1038 on its tree).
Close enough to confirm the method matches s5's; the +14 is drift from the six commits.

| Cursor candidate | Cursor's claim | **Measured in emitted code** | Verdict |
|---|---|---|---|
| NV dict base | "43 NV_SET sites" | **18** NV-related call sites, all 21 files | Overstated ~2.4x |
| `&STCOUNT` | "per-statement increment — hot" | **0** `rt_stmt_enter` sites | **Structurally absent** |
| subject char cache | "inner scan loop" | **0** subject-related call sites | **Structurally absent** |

### 2a. `&STCOUNT` is not hot — it is *absent*, and this is by design

`src/lower/lower_snobol4.c:29-33` gates the per-statement hook on whether the program
text references `&STNO`/`&STCOUNT`/`&LASTNO`. **No benchmark in the corpus references
any of them**, so `rt_stmt_enter` is never emitted. A register rung on `g_stcount`
would be measured by a rail that never executes the increment — guaranteed 1.00x, or
worse, indistinguishable noise scored as a win.

**Manual grounding** (SPITBOL manual §keywords, read this session): `&STCOUNT` is
incremented at the *start* of each statement, **but stops incrementing entirely once
`&STLIMIT` is set negative** (unlimited-execution mode). Any register-resident
`g_stcount` must preserve that conditional — it is not an unconditional tick. This
raises the arm's complexity while §2a shows the corpus cannot reward it.

### 2b. subject char cache — zero sites, same shape as prior ungradeable candidates

No `subj`-matching call sites in emitted benchmark code. `g_subject` /
`rt_subject_load_nv` / `rt_keyword_subject` exist in the templates but the benchmark
corpus does not drive them. Ungradeable on this corpus.

### 2c. What the corpus *actually* shows as hot

Top emitted `rt_*` call targets (static, all 21 files) — the honest RC-6 ranking input:

```
  99 rt_call_arr        31 rt_cmp_d                 26 rt_proc_call_epilogue_slim_
  62 rt_coerce_num2_d   28 rt_sub                   26 rt_flat_ret_snap
  50 rt_add             28 rt_proc_call_epilogue_   21 rt_gva_island
                        27 rt_proc_open_fn          16 rt_proc_set_nparams
```

RIP-relative global accesses (post-RC-5-GVA, so GVA traffic already lives on `[r9+`):

```
1362 g_rtcc_block    13 g_call_args    12 rt_anchor_g    8 g_scan_hit_start
                                                          8 g_cap_gen    6 fn_cell
```

`g_rtcc_block` at 1362 is the block itself (expected — it is the canonical home).
The genuine remaining candidates are **`g_call_args` (13)** and **`g_scan_hit_start`
/ `g_cap_gen` (8 each)** — all an order of magnitude thinner than the 1038-site GVA
base that made RC-5-GVA worth doing. **RC-5's well may simply be dry**, and the next
honest move may be RC-6 (a different axis) rather than another RC-5 sub-rung.

---

## 3. DEFECT — fibonacci SIGSEGVs under `SCRIP_RTCC=1` at HEAD `79cf3d1d`

Reproduced at restored HEAD, clean build (`make scrip` + `make libscrip_rt`):

| program | RTCC=0 | RTCC=1 |
|---|---|---|
| **fibonacci.sno** | exit 1, `result: 832040` (correct) | **exit 139 — Segmentation fault** |
| var_access.sno | — | exit 1, `result: 60000012` (correct) |
| arith_loop.sno | — | exit 1, `iterations: 1000000` (correct) |

Deterministic across repeats. Controls pass on the same arm, so this is
fibonacci-specific, not a blanket RTCC=1 failure.

**Severity:** fibonacci is **one of the two rail benchmarks** RC-5-GVA used to claim
1.036x. The rung's headline number is now measured on a program that crashes on the
same arm at current HEAD.

### ATTRIBUTION IS INCOMPLETE — do not blame RTCC yet

A bisect over `979f0db7 → befbe212 → ada979eb → 79cf3d1d` was started and **timed out
partway**, leaving the worktree detached at `ada979eb` (tree was clean; restored to
`main` @ `79cf3d1d` and rebuilt — verified `git status` clean, `BUILD_OK`). **No
attribution conclusion was reached.** Per the CRATER ATTRIBUTION law this must not be
recorded as an RTCC regression until proved by builds.

Live hypotheses, untested:
- a genuine RTCC arm defect exposed by fibonacci's recursion depth;
- interaction with `AB-2` (`79cf3d1d`, dual-arm ACT-ANCHOR + monitor-tap relocation),
  which touched arm-adjacent machinery from a concurrent seat;
- a pre-existing RTCC=1 fibonacci fault that s5 never hit because its rail ran on
  `979f0db7`.

**Next session's first task** — cheaper than any rung: rebuild at `979f0db7` and run
fibonacci RTCC=1. Crash there ⇒ pre-existing, s5's rail number is suspect. Pass there
⇒ bisect the four-commit window. **Budget the bisect as its own step with a per-build
timeout**; a full rebuild per commit does not fit in one command window.

---

## 4. Method note for future sessions (cost me ~15 min)

`./scrip --compile F -o F.s` **silently emits nothing** — `-o` did not take on this
build. Asm goes to **stdout**. Correct census invocation:

```sh
for f in *.sno; do SCRIP_RTCC=1 scrip --compile "$f" < /dev/null > "${f%.sno}.s" 2>/dev/null; done
```

Also: `--run` returns **exit 1 on success** for these benchmarks (exit code is not a
pass signal — compare filtered stdout, dropping the `ms:` timing line, or arms always
"differ").

---

## Gate

No code changed → no regen, no board sweep, no rail required. SCRIP tree verified
clean at `79cf3d1d` with `scrip` and `libscrip_rt` rebuilt and `BUILD_OK`. Census
reproducible by §4. Defect §3 reproduced at restored HEAD with controls. Attribution
of §3 explicitly **left open**.
