# FINDING 2026-08-24 seat10 — `six-owed-verifier`: verifier landed, first measurement, and the fleet outran the first draft of this FINDING while it was being written

## What landed
`SCRIP/scripts/util_verify_s_artifacts_owed.sh` — a DRY drift check for the `.s` artifact
regen chain named in RULES.md handoff step 4. It never writes to the real corpus or SCRIP
checkouts: it clones corpus locally into a disposable scratch dir (`--no-hardlinks`, since
`/tmp` and the workspace are on different filesystems here — a plain `--local` clone fails
cross-device), runs each in-scope regen script against the clone with `CORPUS`/`BENCH_DIR`
env overrides those scripts already respect, diffs the clone's HEAD before/after, and
discards the clone. `update_icon_bench_asm.sh` needs no clone — `CHECK=1` is its own native
non-mutating dry-run. Wired into `handoff_status.sh` as a WARN-ONLY section (see below).

Exit codes: 0 = nothing owed, every check actually ran. 1 = something owed, or a checked
script hit trouble (compile/assemble failure, or found zero of its expected inputs — see
"never a false clean" below). 2 = environment error (no verdict possible at all).

## Scope correction: "six" → three required + one conditional
The task brief said "RULES.md handoff step 4 names six regen scripts." That was true of
RULES.md's **pre-s269** text. RULES.md line 96, dated **2026-08-24 s269** — three sessions
*before* this row was minted at s272 — records Lon's ARTIFACT POLICY ruling in-chat to CEO,
verbatim in substance: *"We will abandon the idea of having artifacts for tests. We have
come far enough now we do not need that. But we want artifacts for benchmarks and demos."*
The current step-4 text names exactly three scripts (`util_regen_benchmark_s_artifacts.sh`,
`util_regen_demo_s_artifacts.sh`, `util_regen_prolog_bench_s_artifacts.sh`) plus
`update_icon_bench_asm.sh` when Icon emitter/lowerer is touched, and explicitly retires
`util_regen_feature_s_artifacts.sh`, `util_regen_crosscheck_s_artifacts.sh`, and
`util_regen_programs_s_artifacts.sh` from the required chain. A same-day CEO law-telegram
(s272, on Lon's order) independently reconfirmed the same point fleet-wide while this row
was in progress.

This verifier checks the **current** RULES.md chain — three scripts, always — plus
`update_icon_bench_asm.sh CHECK=1`, checked **unconditionally on every run** rather than
conditioned on "was Icon touched this session," since a standalone verifier has no way to
know what a past session touched and unconditional checking is strictly the more honest
default for a mechanical drift check. The three retired scripts are named, not silently
dropped, in the verifier's own header comment. `util_regen_feature_s_artifacts.sh` and
`util_regen_crosscheck_s_artifacts.sh` were in fact **deleted outright** mid-session by an
unrelated row (`strip-mechanical-carve`, SCRIP `4a5f88e9` / corpus `dfc75192`+`cbf12d7b`) —
confirmed by re-`git pull --rebase` before this FINDING was finalized (see "the fleet
outran this FINDING" below). `util_regen_programs_s_artifacts.sh` still exists, undeleted,
as of this writing.

Per THE LOOP protocol (non-blocking scope mismatch — "a brief whose numbers turn out wrong
is still a brief, the corrected number IS a deliverable"), this was corrected and the row
carried on rather than stalled on a question. Routed to HQ via `s4e_msg.sh ask` and this
row's own QA block.

## The fleet outran this FINDING while it was being written — measure, don't trust a stale draft
RULES.md's own FACT RULE, "MEASURE-THEN-REBASE PUBLISHES A STALE VERDICT," predicts exactly
what happened here: the first full measurement (below, superseded) was taken, a routine
`git pull --rebase` before push then pulled in **eight new corpus commits and two new SCRIP
commits** from other concurrently-running seats — including `seat14`'s
`sweep-s-artifact-drift` row (real, non-dry-run runs of benchmark/prolog_bench/
programs/crosscheck regen) and, most relevantly to this row, **`ef18421e
update_icon_bench_asm.sh: narrow the refusal guard, it was blocking its own default`** —
another seat independently found and fixed the exact `*/icon`-self-match bug this row's
first draft had just finished documenting as a live, unfixed, flagged-to-HQ bug. The
verifier was re-run fresh after the rebase, per the same FACT RULE, and **that** run is the
one reported below. The stale intermediate finding (icon script REFUSED, could not run at
all) is preserved in this row's LEDGER for the record, not repeated here as current.

## First (truly-final) measurement at HEAD
**Provenance:** SCRIP `593ca9e2` (this row's own commit, rebased onto `9960787d`) / corpus
`0f8b0e2d`, both fetched and confirmed fully synced with origin immediately before this run.
Pristine build this session, RT_OPT `-O0` per the NO-O2-EVER rule, via the verifier's own
internal `make pristine` (not `--skip-pristine` — this is the real, by-the-book path).

```
S-ARTIFACTS-OWED-TOTAL: 20
S-ARTIFACTS-TROUBLE-TOTAL: 24
VERDICT: OWED — 44 item(s) need attention before this counts as current
```

**`benchmark` and `prolog_bench`: byte-clean, zero owed, zero trouble.** Consistent across
every run this session, including after seat14's real sweep landed — the compiler's current
output matches what's committed for both trees, exactly.

**`demo`: still finds 0/21 sources — a live, unfixed script bug, unrelated to this row.**
`corpus/demo` was reorganized into 12 per-family subfolders at s272 (commit `db20f3cf` —
e.g. `demo/roman.sno` → `demo/roman/roman.sno`, `demo/calculator-1.sno` →
`demo/calculator/calculator-1.sno`). `util_regen_demo_s_artifacts.sh` still does
`cd "$DEMO"` (flat `corpus/demo/`) and checks `[ -f "$f.sno" ]` per whitelisted name — every
one SKIPs, and the script reports **"No changes — demo artifacts already current"** having
looked at nothing. This is the exact `make test` false-green trap this row's DONE-WHEN
calls out by name, caught for real. The verifier does not trust "No changes" at face value —
it independently counts "no .sno" skip lines and refuses to call that clean. Unlike the icon
guard bug (below), nothing in this session's pulls touched this script — it remains broken
as of this FINDING and is flagged to HQ as a follow-up row (repair the path assumption to
match the per-family layout).

**`icon_bench`: now functional (bug fixed concurrently, mid-session, by another seat) and
finds real, actionable drift.** This row's own investigation found that
`update_icon_bench_asm.sh`'s refusal guard — `case "$CORPUS" in */icon|*/icon/*)`, meant to
reject only the Icon rung-test suite — matched **any** path ending `/icon`, including its
own correct default `corpus/benchmarks/icon`; confirmed with zero env override, its true
documented default, hitting the identical REFUSED. **Independent same-day corroboration:**
`conform-defer-tab-span-crash`'s own LEDGER (seat01, unrelated row) records hitting the
identical wall in near-identical words. Before this FINDING could be finalized, commit
`ef18421e` (`update_icon_bench_asm.sh: narrow the refusal guard, it was blocking its own
default`) landed on origin from a third seat and narrowed the pattern to
`*/corpus/icon|*/corpus/icon/*` — correctly excluding only the rung-test suite. Re-running
the verifier after pulling that fix: the script now runs to completion and reports **20
benchmarks with stale `.s`** (`bench_icnint_loop`, `bench_icnint_mod_isolate`,
`bench_icnstr_concat_{dispatch,int_dispatch,intvar,strvar,table}`,
`bench_icnsub_{list_dispatch,table_miss_dispatch,table_miss_semantics}`, `concord`, `deal`,
`geddump`, `ipxref`, `micro`, `micsum`, `queens`, `rsg`, `tgrlink`, `version`) plus **3
genuine compile errors** (`options`, `post`, `shuffle` — CERR, not a refusal or
non-determinism flag). This is now **real, actionable signal** rather than a "cannot check"
condition — flagged to HQ as a follow-up (run `update_icon_bench_asm.sh` for real to clear
the 20, investigate the 3 CERR names as possible genuine compiler bugs or fenced-shape
gaps). Neither is this row's job to fix — the verifier's job is to surface it, which it did,
the first time anyone could see it clearly since the guard bug was blocking that visibility.

**One near-miss in this row's own verifier, corrected before any measurement shipped:** the
first working draft captured `icon_rc` but only converted it to "trouble" via two text
greps (`WOULD-`, `CERR`) — neither of which matches a REFUSED/FATAL exit that happens
*before* the script examines any file. That draft reported `[icon_bench] rc=2 owed=0
trouble=0` against the then-current (buggy) icon script, i.e. clean, for a check that had
not run at all — the exact false-green shape this row exists to close, reproduced inside
the tool meant to prevent it. Caught by re-reading the actual captured output rather than
trusting the counters. Fixed: a `rc≠0` with zero owed and zero trouble lines is now its own
explicit trouble category, so a *future* regression of this kind (a different script
refusing outright) is still caught even though today's specific instance was fixed by
someone else before it mattered.

### A related, separate gap — now partially closed, one tree still open
An earlier draft of this FINDING flagged that RULES.md's s269 text says the three retired
trees "are DELETED" when, measured at that time, they were not (1338 files: crosscheck 489,
feature 155, programs 681, probe 13). Mid-session, `strip-mechanical-carve` (SCRIP
`4a5f88e9`, corpus `dfc75192`+`cbf12d7b`) deleted the feature tree (155 files, SCRIP
`test/snobol4`) and crosscheck (corpus, count not re-verified post-deletion) and retired
both regen scripts outright (file deletion, not just chain removal). **`corpus/probe` (13)
and the "programs" trees (`corpus/{icon,prolog,rebus}`, 681 files,
`util_regen_programs_s_artifacts.sh` still present) remain undeleted** as of this FINDING —
narrower gap than first measured, still open, still not this row's job, still flagged.

## WARN, not BLOCK — deliberate, and now measured rather than assumed
The task's QA anticipated this exact question and pre-ruled the default: WARN with a loud
banner and an exact count, not a hard block, because a block would wedge every seat's
handoff before a large standing count is cleared. That default holds even more clearly now
that the number is real, actionable drift (20 stale + 3 errors, entirely Icon-side) plus one
broken script (demo) — neither is something a session touching only, say, Prolog or SNOBOL4
codegen could fix, so blocking today would wedge unrelated handoffs on a problem outside
their lane. `handoff_status.sh` prints the full detail under a `⛔⛔⛔` banner
unconditionally, but does not set `blocked`/`unknown` — the CHAT SESSION verdict is driven
only by the existing per-repo git checks, confirmed unchanged by a real end-to-end run
(merged cleanly with a concurrent, larger rewrite of that same script by hq_P — see LEDGER).
A follow-up row should flip this to BLOCK once demo is repaired and the icon backlog is
cleared, and the measured count is genuinely zero.

## RULES.md
Addended at the end of the existing handoff step-4 paragraph (line 96): the verifier's
existence, how it's wired, and this measurement's headline numbers, with a pointer to this
FINDING for full detail — per the task's STEP 4 ("if the verifier changes what handoff
means, that belongs in RULES.md, routed the same session").
