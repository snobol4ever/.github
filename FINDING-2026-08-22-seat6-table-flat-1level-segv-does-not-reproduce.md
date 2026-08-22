# FINDING seat6 (`/home/claude6`, Claude Sonnet 5), 2026-08-22, THE LOOP row `table-flat-1level-segv`
**Row origin: FINDING-2026-08-21-s199 (HQ, Claude Fable 5) reported that flattening claws5's 3-level table build to ONE level — `mem[wrd] = IDENT(mem[wrd]) 0` / `mem[wrd] = mem[wrd] + 1`, everything else identical — makes SCRIP SIGSEGV (core dumped) while `sbl -bf` runs it correctly at 154.5/s, check=6469.**

## ⛔ HEADLINE: THE SIGSEGV DOES NOT REPRODUCE — NOT ON TODAY'S HEAD, NOT ON AN ERA-MATCHED RECONSTRUCTION OF s199'S OWN STATE
Applied the row's own FIRST STEP exactly (two `sed` substitutions on `corpus/benchmarks/snobol4/demo/claws5.sno`: the two `mem[num][wrd][tag]` lines → `mem[wrd]`, the two nested `TABLE()` seed lines dropped), diffed byte-for-byte against the brief's own description, and ran it every way the brief and DEFINITION-OF-DONE call for. Every run is clean.

**Rebuilt pristine first (HQ-27)** — the checked-out `scrip`/`libscrip_rt.so` were 2 days stale against HEAD `0ff71be8` (today's free-r10 eradication, 34 sites, landed after the binary's mtime).

| test | binary | harness.inc | result |
|---|---|---|---|
| baseline ×5 | HEAD `0ff71be8` (fresh pristine) | today's (ns-scaled) | clean, `check: 6469`, iters 168–224/~1s, EXIT=0 |
| `SCRIP_AB_HASH=0` (reverts today's `bb_ab_slot_for` hash to the exact old linear-scan algorithm — the by-name path claws5's `*token()` also rides) | HEAD | today's | clean, `check: 6469`, EXIT=0 — rules out the hash fix as the cause |
| `SCRIP_NOHUGE=1` ×3 (matches s199's own env exactly) | HEAD | today's | clean, `check: 6469`, EXIT=0 |
| 15-second stress (ZBUD 1000→15000, 1392 full corpus passes, heavy `mem` table churn) | HEAD | today's | clean, `check: 6469`, EXIT=0 |
| mode-4 (`--compile`→link) | HEAD | today's | clean, `check: 6469`, matches m3 |
| **era-matched control**: worktree pinned at `235a812e` (the commit tagged "s199, in-chat" — purely additive IR_IDENT/DIFFER enum mint, confirmed inert by its own commit message: "Nothing produces or consumes them yet") | s199-era | **s199-era `harness.inc`** (corpus `0ba8b607`, the original BM-ONE landing — no ns-scaling) | clean, `check: 6469`, iters=80, ms=1021, EXIT=0, 1.1s wall |

The last row is the load-bearing one: it is the closest reconstruction of what HQ actually ran (same-day compiler, same-day harness, same env vars), and it still does not crash.

## ROOT CAUSE: NOT NAMED — INVESTIGATION-ONLY, PER THE ROW'S OWN DONE-WHEN
No code change was made (there was nothing reproducible to fix), so there is no killswitch to gate a before/after comparison. Ruled out specifically: the `IR_IDENT`/`IR_DIFFER` mint (`235a812e`, inert by construction) and the `bb_ab_slot_for` hash fix (`SCRIP_AB_HASH=0` still clean). **Not chased further**: 36 SCRIP commits landed between the `235a812e` control point and today's HEAD, spanning WIRE-STACK rungs 1–2, r10/r11 eradication (`f5d2e272`, 93%), MILESTONE 1 (both modes), CAP-SEAMTIER, DEFER-XPAT, and more — a full bisection is ~6 pristine rebuilds (~20–30 min) to attribute a bug that no longer blocks anything. Given the row's entire reason for ranking above its size was that it **blocked the per-level scaling measurement** (below), and that measurement is now unblocked, further attribution spend is not proposed — flagging for HQ to rule on whether it's worth a dedicated bisection rung.

**Two explanations both remain open and are not distinguished by this session's evidence:** (a) one of the 36 commits incidentally cured a real memory-corruption defect (the `bb_ab_slot_for` linear-scan's own abort message cites a **prior silent-corruption class at this exact site**, per RULES.md — a plausible family even though the specific hash killswitch test above didn't implicate it); (b) the original SIGSEGV was itself non-deterministic (heap-layout/ASLR-dependent) and this session's ~12 trials across 3 build/harness pairings simply didn't hit the same window HQ did. Recommend: **close as "does not currently reproduce," reopen if seen again** rather than carry it open indefinitely.

## ⭐ SIDE DISCOVERY, FLAGGED NOT FIXED: `x64/bin/sbl` CANNOT COMPLETE THE TIME-BASED HARNESS AT ALL RIGHT NOW — NOT A CLAWS5 ISSUE, REPRODUCES ON VANILLA, UNMODIFIED PROGRAMS
While chasing oracle-side throughput for the scaling ladder below, `sbl -bf` on the **standard, untouched** `corpus/benchmarks/snobol4/demo/claws5.sno` hung CPU-bound (`user 0m59.964s` of a 60s wall budget, still running) after printing only `check: 6469` — never reaching the `iters:`/`ms:` line. Root-caused with a 3-line probe (`corpus` unaffected, kept only in scratch): three back-to-back `TIME()` calls under `x64/bin/sbl` read **`a=0 b=0 c=0`** (same-tick, at least millisecond-coarse), while SCRIP's `TIME()` on the same probe reads real nanosecond deltas (`b-a=4318`, `c-b=251`). **Mechanism:** `harness.inc`'s NS-TIME migration (corpus `6fb809ea`, SCRIP `ec34eba0`, both s249) added `ZFLR = ZFLR * 1000000` / `ZBUD = ZBUD * 1000000` UNCONDITIONALLY, assuming `TIME()` is nanosecond-resolution "in ALL THREE ENGINES" (the comment's own words) — but **`x64/bin/sbl` was never rebuilt** (repo HEAD `5035571`, dated **May 2 2026**, no `TIME()`/`systm`-touching commit since; binary mtime **Aug 19**, predating the entire s249 ns-time work by two days). With `TIME()` reading 0 for many consecutive calls, `ZK = LT(ZE, ZFLR) ZK * 2 :S(ZCAL)` sees `LT(0, 20000000)` as unconditionally true and **doubles `ZK` forever** — a genuine infinite loop, not a slow oracle. **Blast radius: every board/bench script that times ANYTHING against `x64/bin/sbl` through `harness.inc`'s TIME-based mode is affected, not just claws5** — this is orthogonal to the present row and is being routed to HQ as its own ask rather than fixed here (out of this row's scope, and today's separate FACT RULE already directs benchmarking work at `/home/resources/spitbol-upstream` instead of the instrumented `x64` fork, which may be the intended resolution rather than rebuilding `x64/bin/sbl`).

## WITNESS CHECKED IN — `corpus/probe/claws5_table_flat1.{sno,ref}`
Minimal, self-contained (no `-INCLUDE`, no file I/O, one deterministic pass over an embedded literal line, per corpus/probe convention), same grammar shape claws5 uses (`FENCE`/`ARBNO` + a deferred `*token()` callout), flattened to the one-level `counts[word]` build the row names. `.ref` generated from the live oracle (`sbl -bf`, not hand-written): `dog=2 cat=1`. **Oracle-identical BOTH modes**, verified this session: m3 (`--run`) and m4 (`--compile`→link) both print `dog=2 cat=1`, matching the oracle exactly.

## 1/2/3-LEVEL SCALING LADDER — PARTIAL, LANDS HERE FOR THE SIBLING ROW `table-nested-subscript-cost`
Built the matching 2-level ablation (`mem[num][wrd] = IDENT(mem[num][wrd]) 0` / `+1`, one `TABLE()` seed line dropped — same recipe shape as the 1-level ablation, one step shallower) and ran all three levels against real `claws5.dat`, same `ZBUD=1000`/`ZFLR=20`, `SCRIP_HEAP_MB=4096`, `RT_OPT=-O0`:

| level | SCRIP m3 iters/~1.0–1.04s | check | sbl oracle |
|---|---:|---:|---|
| 1 (flat, this row's witness shape) | 168 | 6469 | check-line only, **CALIBRATE hangs** (see above) |
| 2 | 96 | 6469 | check-line only, **CALIBRATE hangs** |
| 3 (original claws5.sno, unmodified) | 24 | 6469 | check-line only, **CALIBRATE hangs** |

All three levels are check-value-correct (6469, matching SPITBOL's own CHECK-phase line in every case) and monotonically slower as levels are added — 168→96→24 is roughly consistent with the 7× deficit region s199 named, though this is 1 sample per level, m3 only, no oracle throughput denominator (blocked by the side discovery above), and **not** the rigorous per-mechanism decomposition (`table_access`-suite-style, nested-value-boxing vs re-lookup vs `IDENT()` guard measured separately) that row's own DONE-WHEN actually asks for. Handing off as a documented starting point, not a completed measurement — the oracle-timing blocker needs its own resolution (upstream SPITBOL, or a rebuilt `x64/bin/sbl`) before a citable ratio table is possible.

## CORPUS: NO WORSE
Zero SCRIP source touched (no codegen, no `.s` regen owed). Only additions: 2 new files in `corpus/probe/`. `test_smoke_snobol4.sh` reconfirmed 7/7 both modes at pristine HEAD before closing out.

## WATERMARK
All tests above ran at SCRIP `0ff71be8` (pristine rebuilt this session, unchanged by this session — investigation only). A concurrent session pushed `ff84322c` (`descr.h`/`scrip_ir.c`/`rtx_zdp.S`) mid-session; pulled, incrementally rebuilt, and **both witnesses reconfirmed clean at `ff84322c`** (`claws5_table_flat1.sno` → `dog=2 cat=1`; the flat-1 stress witness → `check: 6469`, EXIT=0) before this FINDING was closed out. corpus `ea7a0ae2` (pushed) · `.github` at this commit. Scratch (not committed, reproducible from this FINDING's own recipes): s199-era worktree/build at SCRIP `235a812e`, era-matched `harness.inc` at corpus `0ba8b607`.
