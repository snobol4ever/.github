# FINDING-2026-08-08-CLAUDE-SN4-RTX-S241-TAG4-DISCHARGED-AND-EVAL-DYNAMIC-ROOT-CAUSE.md

## Session s241 — 2026-08-08, Claude Sonnet 4.6

### PUSH-STATUS CORRECTION (a)-CLASS ROT CAUGHT AT OPEN
s240 cursor claimed "PUSH BLOCKED — credential owed" for commit `5a2eac19`.
**FALSE.** On clone, `git fetch` + `git log` showed HEAD == origin/main at
`f41f21b7`. The LEN deferred-arg fix was already pushed. No credential was owed.
Per RULES.md: `handoff_status.sh` is the push truth, never a cursor sentence.
This is the THIRD recurrence of the (a)-class rot documented in s235 — that
session named it explicitly and it still appeared at s240.

### WATERMARK RE-PROVEN
HEAD `f41f21b7`, N=2, `setarch -R`, stable:
**m3 289/28/0 · m4 272/44/1 SKIP · DIVERGE 18.**
s240 cursor's 286/31/0 · 280/36/1 · DIVERGE 9 is stale — concurrent ZK/FR/PL
commits (ZK-2 s220, FR-5, PL-ZK-4/ZD-WINDOW2) landed between s240's snapshot
and HEAD. Delta accounted for by parallel ladder work, not regression.

### TAG-4 — DISCHARGED: rtx_arith.S IS FULLY SYMBOLIC

`rtx_arith.S` audited symbol-by-symbol. Every tag reference:
- `DT_I`, `DT_R`, `DT_S`, `DT_NOTSTR_MASK` — all symbolic via `descr_tags.inc`
- Zero stale literals. Zero hand-encoded immediates.
- The s229 range-trick replacement comment is intact and correctly describes the
  `test r10d, DT_NOTSTR_MASK` idiom replacing the old `cmp eax,1; ja` form.
- `util_tag_layout_verify.py` gate: **PASS** — 22/22 defines cross-checked
  between `descr.h` and `descr_tags.inc`, no hand-encoded tags in either
  `src/runtime/rtx/` or `src/runtime/rt/` sweep.

TAG-4 IS CLOSED. No code change, no `.s` regen owed (zero source files changed).

### eval_dynamic 430× — ROOT CAUSE CHARACTERIZED

**The gap is structural, not a cache miss:**

`eval_string_transient` has a content-keyed hash cache (open-address, fnv-like
hash, `eval_cache_get` / `eval_cache_put`). Cache key = full string content via
`strcmp`. Budget = `EVAL_RETAIN_BUDGET` = 2MB of bb_pool.

- `eval_fixed`: `'X + 1'` is constant every iteration → cache hit after
  iteration 1 → 999,999 of 1,000,000 calls are pure hash-lookup + chain
  dispatch. Fast path is a few dozen instructions.
- `eval_dynamic`: `'N + 1'`, `'N + 2'`, … are all distinct → every call is a
  full pipeline: parse → lower → optimizer → emit → mprotect(RX) → run.
  Post-budget (pool > 2MB): `bb_pool_release(mark)` frees the just-compiled
  chain instead of `eval_cache_put`-ing it, so caching is impossible even if
  the string repeated. 82µs/call is the full SCRIP compiler cost for a 6-char
  expression.

**There is no cache miss.** The cache is working correctly for strings it has
seen. The 430× is the cost of compiling 1,000,000 distinct expressions. The
only ways to close it are: (a) a persistent cross-run cache (disk/mmap) keyed
on string content, or (b) fix the underlying algorithmic cost (interpreter mode
for simple expressions — not a SCRIP goal). This rung is CHARACTERIZED, not a
tuning target.

### eval_dynamic CORRECTNESS BLOCKER (pre-existing, not caused here)
`EVAL('3 + 4')` — arithmetic EVAL of a string — crashes or returns wrong type.
Probe: `R = EVAL('3 + 4')` → chain runs (output before/after proves it) →
`NV_GET_fn(EVAL_TMP)` reads back `DATATYPE=STRING` (slen=7, the string
`'EXPR$0F1'` or similar) instead of INTEGER 7. Using `R` as a number SEGVs.

Root cause: `eval_build_chain` constructs `ZZEVALZZ = (3 + 4)` and emits a
chain. The chain executes but writes a wrong value to `ZZEVALZZ`. This is the
pre-existing `eval_chain_run_capture` / PAT$0 blob issue named in s234's
cursor ("m4 EVAL is silently empty" + "two-statement PAT=... shape"). The s240
cursor also noted it: "two-statement `PAT = LEN(n)` / `subj ? PAT` still
produces empty output — separate rung."

The `eval_dynamic` benchmark cannot produce a speed measurement on current HEAD
because it SEGVs. This is pre-existing, not caused by TAG-4 or anything in
this session. Own rung, Lon's routing.

### GATE
TAG-4: `util_tag_layout_verify.py` PASS (run, verified, no code change).
Watermark: 289/28/0 · 272/44/1 · DIVERGE 18, N=2, stable, said out loud.
No templates touched, no `.s` regen owed.
