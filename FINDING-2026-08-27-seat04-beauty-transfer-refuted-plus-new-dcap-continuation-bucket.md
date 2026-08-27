# FINDING seat04 — `perf-nv-set-capture-pump`'s WRITE-side mechanism does NOT transfer to beauty; a new, undecomposed 5.52% pattern-continuation bucket found instead

**Session:** 2026-08-27 seat04, THE LOOP queue row `perf-roman-8x` (STEP 2(b) — the BEAUTY-TRANSFER empirical confirmation, open since 2026-08-24, never previously attempted by any seat — three other seats/HQs claimed and released this umbrella row earlier the same day without touching STEP 2(b)).
**SCRIP HEAD:** `e637707d` · **corpus HEAD:** `8e85e50d`. `make pristine` (RT_OPT=`-O0`, mandatory per the s262 FACT RULE — no `-O2` arm exists or will exist). M1 fixed point re-verified byte-identical, both plain and under callgrind.

## 1. The question

STEP 2(b) of `perf-roman-8x`, and the beauty-transfer note inside `perf-nv-set-capture-pump`, both flag the same open gap: seat11's fresh roman profile (2026-08-24) found `NV_SET_fn` (13.54% of kernel) plus its dominant caller chain `rt_dcap_pump`/`c_rt_dcap_end_ok_open` (8.88% combined) as roman's #1 uncured cost bucket — the WRITE-side counterpart of the read-side by-name-lookup defect already cured. Structural reasoning (beauty's `NRETURN` idiom is said to share the capture mechanism) suggested this would also dominate beauty, but nobody had run a real profile to check: *"this is inference from a code-shape argument, not a profile"* (task file, verbatim, both `perf-roman-8x` and `perf-nv-set-capture-pump`). This FINDING is that profile.

## 2. Method

```
corpus/demo/snobol4/beauty/beauty.sno (40,943 bytes) -- CONFIRMED as the correct current live file via corpus git
history, not assumed from any doc: b131a913 deleted the short-lived BEAUTY-CN &-constant variant outright and
promoted the classic form to be THE beauty.sno, moved to demo/; e63689fa is its latest hand-edit (2026-08-24).
Includes resolve from corpus/include/ (moved out of the beauty dir per Lon s269); confirmed empirically by running
scrip from the beauty directory rather than trusting either stale script below.
cd into that directory; valgrind --tool=callgrind --separate-callers=2 ./scrip beauty.sno < beauty.sno
  (mode-3, compile+run bundled -- same basis as FINDING-2026-08-24-seat06-string-runtime-vs-beauty-cross-
  reference.md's 15,321,076,349 Ir arm, chosen for direct comparability)
Correctness: diff vs beauty.sno itself -- IDENTICAL, both plain and under callgrind (M1's own fixed-point law, s117).
callgrind_annotate --auto=no for the self-cost table (flat, no inline source annotation -- see §4 for why).
```

| | Ir |
|---|---:|
| beauty self-host (m3, compile+run), fresh this session | 15,315,858,258 |
| seat06's figure, 3 days earlier, same recipe | 15,321,076,349 |
| delta | -5,218,091 (-0.034%) |

The delta is small and plausibly explained by the one hand-curated 4-line beauty edit (`e63689fa`) landing in between — not chased further, not this row's concern. Top-of-profile self-cost is dominated by the same compile-phase emitter functions seat06 found (`codegen_flat_chain_body` 21.53% vs their 21.55%, `zd_plan` 10.15% vs 10.15%, `zls_node_bytes` 6.79% vs 6.79%) — strong corroboration this is the same instrument and methodology, reproducible three days apart.

## 3. The transfer question, answered: NO

| function | beauty self-Ir | beauty share | roman self-Ir (seat11, 2026-08-24) | roman share |
|---|---:|---:|---:|---:|
| `NV_SET_fn` | 12,614,803 | 0.082% | 50,491,121 | 13.54% |
| `rt_dcap_pump` | 4,157,167 | 0.027% | 23,738,036 | 6.37% |
| `c_rt_dcap_end_ok_open` | 64 | ~0.0000004% | 9,363,715 | 2.51% |
| **combined** | **16,772,034** | **0.11%** | **83,592,872** | **22.4%** |

⛔ **The structural inference does not hold.** The mechanism that is roman's single biggest uncured bucket (22.4% combined, bigger than the already-attributed `bn_replace`/by-name-dispatch families) is statistical noise on beauty (0.11% combined) — three orders of magnitude apart in share, not merely "smaller." **Whoever eventually cures `perf-nv-set-capture-pump` or `perf-nv-set-fn-o0-overhead` should not expect it to move beauty's numbers measurably.** This corrects the task file's own "if `NRETURN` routes through this SAME capture-pump... this row's cure likely moves beauty too" inference — plausible-sounding, not measured, and now measured false.

## 4. A found-not-sought bucket: 5.52% sitting behind one call arc, undecomposed

⛔ **Methodology note kept deliberately, because it nearly produced a false positive in this very FINDING.** My first pass grepped `callgrind_annotate`'s DEFAULT output (auto-annotation on), which inlines both flat self-cost rows and per-source-line call-arc rows in the identical `function'caller1'caller2 (Ir, pct)` text shape. Summing every matching line double-counted an INCLUSIVE call-arc annotation as if it were more SELF-cost rows — it produced a fake `rt_dcap_pump` figure of 848,832,601 (5.54%), which would have reversed §3's headline. Re-running with `--auto=no` (flat self-cost only, no source inlining) is what produced the correct table above. **Same disease as this project's own TRANSCRIPTION and CORRECT-PROCEDURE-WITH-A-FALSE-EXPLANATION FACT RULES: a tool's default output shape silently mixed two different cost bases under one visually identical row format.** Caught before publishing, not after — flagging the shape so the next seat parsing `callgrind_annotate` by hand knows to pass `--auto=no`, or otherwise keep the two views separate.

The real arc, isolated correctly: `rt_dcap_end_ok_open` (box-driven — `extern`-declared at `pattern_match.c:725`, actual body is Byrd-box-emitted machine code per the NCB-1c M3 comment at `pattern_match.c:734`, not a plain C function) calls into `rt_dcap_pump` **4,585 times**, and that call's INCLUSIVE subtree costs **844,673,668 Ir — 5.52% of beauty's entire run**. `rt_dcap_pump`'s own self-cost under that same arc is only 3,949,357 Ir, so ~840M Ir (98.6% of the arc) is spent in whatever the box-wired continuation does after the pump returns — not in the pump itself and not in `NV_SET_fn`. Architecturally this reads as a pattern-match CONTINUATION wired as a direct jump (Byrd-box ports, no runtime dispatch), consistent with "the rest of a deeply-nested MATCH/ARBNO-shaped statement" — but that is a plausible reading of the architecture, not a decomposition I performed. **Not chased further: this is a different mechanism from the one this row asked about, and ROW FACTORY discipline says measure and route, not cure-in-the-discovery-pass.**

⭐ **Why this matters beyond curiosity:** `FINDING-2026-08-24-seat06-string-runtime-vs-beauty-cross-reference.md` §3 summed "every clearly-runtime symbol" it could find to ≈5% of beauty's total and concluded compile-phase owns essentially all the rest. That sum did not include `rt_dcap_pump`/`rt_dcap_end_ok_open` by name — both because they were not yet flagged as an interesting mechanism (seat11's roman discovery was the same day, ordering unclear) and because the true cost sits in an unnamed box-driven continuation, which a symbol grep would not catch. By inspection the two mechanisms don't structurally nest (capture-continuation vs. by-name-dispatch/defer-read), so this 5.52% likely sits ADDITIONAL to that ≈5%. **Flagged, not re-derived: beauty's real non-compile share may be closer to ~10-11% than the ~5% previously characterized.** Stated here as a flag per the FACT RULE against turning an inference into a measurement — whoever picks this up next should re-sum both lists on one fresh profile before quoting a corrected total.

## 5. Incidental: `board_beauty_m1.sh`'s live M1 rung is currently unmeasurable (stale path, empirically confirmed)

While confirming which `beauty.sno` to trust (§2), found `scripts/board_beauty_m1.sh` hardcodes `BDIR="$S4E/corpus/crosscheck/beauty"` and `SRC="$BDIR/beauty.sno"` for the milestone's own full-file rung — that file does not exist there (`corpus/crosscheck/beauty/` holds only the M1 ladder witness fixtures, `m1_lad_*.in/.ref`; the live `beauty.sno` sits at `corpus/demo/snobol4/beauty/`, moved there by the same `b131a913`/re-grid history in §2). **Empirically confirmed broken, not inferred from reading:**

```
$ bash scripts/board_beauty_m1.sh --rungs "1"
scripts/board_beauty_m1.sh: line 74: /home/claude04/corpus/crosscheck/beauty/beauty.sno: No such file or directory
scripts/board_beauty_m1.sh: line 139: [: : integer expression expected
GATE UNPROVEN(2) [board_beauty_m1]: examined 0 gradable prefix rungs ...
```

The script's own V2-5 discipline correctly refuses (`rc=2`, not a false green) rather than silently passing — but this means MILESTONE 1's own progress board has been unmeasurable since whichever corpus commit orphaned the path, and nothing surfaced that until this session. The script's header comments describe a `BDIR`/`CLASSIC` split (live BEAUTY-CN file vs. frozen classic) that itself predates `b131a913`'s ruling deleting BEAUTY-CN entirely — the whole premise the script's path logic was built on no longer exists. Not fixed here (zero script edits this session, per the same measure-and-route discipline as §4) — minted as `board-beauty-m1-stale-src-path` (QUEUE.tsv rank 4, task file created) for whoever picks it up. The M1 probe (`​.github/probes/m1-bisect/check_m1_fixedpoint.sh`) has the same disease one layer further back (`M1_BEAUTY_DIR` defaults to `corpus/programs/snobol4/demo/beauty`, which no longer exists at all post-flatten) — flagged in the new row rather than duplicated here.

## 6. Not chased (honest boundary)

- Decomposing the 844.7M/5.52% arc into its own named functions — needs deeper `--separate-callers` depth or a source-level walk of what `rt_dcap_end_ok_open`'s box body actually wires to; bigger than any single bucket in seat06's runtime-5% list, big enough to be its own row rather than a paragraph here.
- Re-verifying the READ-side (`NV_GET_fn`/`rt_defer_nv_read`/`rt_defer_cell_read`) on this fresh profile — not this row's question, already established negligible-and-cured twice independently (seat06 3 days ago, seat11's roman call-table same day); spot-checked `NV_GET_fn` still appears at similar magnitude to 3 days ago on this fresh profile, not re-tabulated in full.
- Whether the -0.034% total-Ir delta from seat06's figure is fully explained by `e63689fa` alone — plausible, not isolated.
- A runtime-only (compile-subtracted) beauty split — same boundary seat06 drew for the same reason; this row's question did not need it.
- Fixing `board_beauty_m1.sh` or the M1 probe — routed to the new row (§5), not cured here.

No cure attempted, zero edits to any `.c`/`.h`/`.S`/`.cpp`/`.sno`/`.sh` source this session — ROW FACTORY discipline, measure and route.
