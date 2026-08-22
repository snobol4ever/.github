# FINDING — seat11: `cond-assign-double-fire` was one `continue` that should have been `break`

**Date:** 2026-08-22 · **Seat:** seat11 (`/home/claude11`) · **Topic:** queue row `cond-assign-double-fire` (opened s251, `FINDING-2026-08-21-s251-json-deserializer-hangs-on-every-comma-and-has-no-corpus-coverage.md` §7)
**Status:** FIXED, both modes, pristine-verified, zero corpus regressions, zero `.s` drift.

## 1. THE DEFECT

SCRIP fires a `.` conditional-assignment action **twice** where SPITBOL fires it **once**, whenever a pattern contains two or more `PATTERN . *DEFERRED_CALL()` sites and the first one is reached. Same input, same overall match verdict (NOMATCH) in both engines — only the side-effect count diverges.

Minimal witness (`185_pat_cond_assign_defer_seq_minimal.sno`, no ARBNO/SPAN needed at all):

```
pattern = (epsilon . *mark_fire()) (epsilon . *mark_fire())
'X' ? pattern                                  :S(matched)F(no_match)
```

| engine | result |
|---|---|
| SPITBOL (`x64/bin/sbl -bf`) | `NOMATCH fire_count=1` |
| SCRIP (m3 and m4, pre-fix) | `NOMATCH fire_count=2` |
| SCRIP (m3 and m4, post-fix) | `NOMATCH fire_count=1` |

The queue row's own witness shape (`184_pat_cond_assign_defer_double_fire.sno`, ARBNO + SPAN, matches the brief verbatim) reproduces identically: SPITBOL/SCRIP-fixed both `NOMATCH fire_count=1`; SCRIP pre-fix `NOMATCH fire_count=2`.

## 2. WHAT IS RULED OUT — ARBNO IS NOT THE INGREDIENT

The brief's opening hypothesis ("does the action re-fire when ARBNO retries?") is **false**. Ablation ladder (all against the live oracle and pre-fix SCRIP):

| witness | shape | oracle | SCRIP pre-fix |
|---|---|---|---|
| `ctrl3` | `. NAME` (plain capture, no defer, no ARBNO) | MATCH x1=1 x2=2 | MATCH x1=1 x2=2 (agrees) |
| `ctrl5` | ARBNO + `. NAME` (no defer) | MATCH x0=1 xn=2 | MATCH x0=1 xn=2 (agrees) — this is `166_pat_arbno_cond_assign_commit.sno`'s shape, already gated, still green |
| `ctrl4` | `. *f()` twice, **no ARBNO**, hardcoded single comma | NOMATCH fire_count=1 | NOMATCH fire_count=**2** (diverges) |
| `185` (testC) | `. *f()` twice, **nothing else at all** | NOMATCH fire_count=1 | NOMATCH fire_count=**2** (diverges) |

Plain conditional-assignment (`.` to a simple name) is correct with or without ARBNO. The divergence needs exactly one ingredient: **a second `. *DEFERRED_CALL()` site reached after a first one.** ARBNO in the original queue witness is incidental — it's one way to reach a second site, not the mechanism.

## 3. THE REAL SPITBOL RULE, FROM THE MANUAL

SPITBOL manual v3.7 (`/home/resources/spitbol-manual-v3.7.pdf`), p.62: *"The [conditional assignment] operator is called conditional, because assignment occurs only if the pattern match is successful."* Empirically (single-site witness `testA` = `(epsilon . *mark_fire())` alone on `'X'`), both engines agree: `NOMATCH fire_count=1` — the deferred call itself fires unconditionally when its component is reached (it isn't gated on overall success), but the **component's own match result is a rejection** once its target fails to resolve "by name" (a plain `RETURN`-based function, `mark_fire()` here, doesn't qualify; `NRETURN`-based functions like `json.sno`'s `pobj()`/`ekey()` do — see §5). A `testB` witness (`(epsilon . *mark_fire()) 'ZZZ_NEVER'`, a literal that structurally can never be reached) drops the count to 0 in both engines — confirming the call is queued and only replayed if the engine actually walks that far into the queue, never invoked past a point that's provably unreachable.

## 4. ROOT CAUSE — `src/runtime/pattern_match.c:rt_dcap_pump()`

Every `. *EXPR` site pushes a 24-byte entry (`rt_dcap_e {varname, saved_delta, len}`) onto a per-match deferred-capture queue (`g_dcf[...].cur..top`, the "CAS"/dcap island off `r12`). At match end, `rt_dcap_pump()` walks the queue and, for a computed-name (`*`-prefixed) entry, calls the target and checks whether the call both succeeded **and** returned "by name" (`rt_g_ret_by_name`, set only by `NRETURN`-style returns — confirmed at `src/runtime/by_name_dispatch.c:5303,6914`, `BID_SNOx24NRET`). When either check fails, this is a **strict refuse**: `rc = 1` is set to fail the match — but the two refuse sites then did `continue`, which resumes the `while (c->cur < c->top)` loop and walks (and invokes) every remaining queued entry anyway:

```c
if (IS_FAIL_fn(nm)) { if (strict) { ...; rc = 1; continue; } ...; continue; }
if (strict && !by_name) { ...; rc = 1; continue; }
```

Real SPITBOL stops at the first rejection (§3); nothing after it is ever reached. The fix is the two-token change `rc = 1; continue;` → `rc = 1; break;` at both sites (lines 664–665). `g_dcf_top--` and the rest of `rt_match_end_all`'s cleanup run unconditionally right after the loop either way, so breaking early skips no cleanup — it only stops invoking further deferred calls once the match's fate (`rc=1`) is already decided.

## 5. WHY THIS DOESN'T TOUCH `json.sno`

`json.sno`'s deferred actions (`pobj()`, `parr()`, `ekey()`, …) all return via `NRETURN`, which sets `rt_g_ret_by_name = 1` before the pump ever inspects it — `by_name` is true, so neither strict-refuse branch is taken and the changed lines never execute for that program. Regression evidence: `json.sno` on `[]`/`{}`/`{"a":1}`/`[{"a":1}]` produces byte-identical `check:` lines before and after the fix (the `{}`/`{"a":1}`/`[{"a":1}]` heap-exhaustion abort under the benchmark harness's fixed-iteration-budget loop is **pre-existing** — reproduced identically on the unfixed binary, same block count (387234), unrelated to this row and not investigated further here).

## 6. VERIFICATION

- Minted `184`/`185` above, confirmed against `x64/bin/sbl -bf` (correctness oracle, s255 two-oracle ruling), both modes.
- `scripts/test_corpus_snobol4.sh`, pristine build (`make pristine`, HQ-27): **355/357 m3, 353/357 m4** before AND after the fix — identical failure set both times (`160_pat_alt_inner_gen_resume`, `demo_treebank`, both pre-existing per a stash/rebuild A-B; not this row's).
- `.s` emitted for `184`/`185` (and for the original witness compiled before/after the fix) is **byte-identical** pre- and post-fix — this is a pure runtime-logic change, zero codegen impact, so the codegen-touched `.s`-artifact regen sequence (RULES.md handoff step 4) does not apply; confirmed by direct diff rather than skipped by assumption.
- `166_pat_arbno_cond_assign_commit.sno` (existing ARBNO + plain-`.` witness) still matches its `.ref`.
- `corpus/probe/ab_defer_call.sno` (bare `*MK()` + plain-name `. R`) unaffected — neither construct it uses touches the changed branch.

## 7. WHEN A `.` ACTION IS ALLOWED TO FIRE (the rule this row asked for)

A `PATTERN . *DEFERRED_CALL()` site's call fires **at most once per site actually reached** while the engine walks the dcap queue in order, and the walk **stops permanently at the first site whose call fails or does not resolve by-name** (plain `RETURN`) — no site after that point is ever invoked, regardless of how many more the source text contains. A site is "reached" only if nothing earlier in the same queue already rejected the match. `NRETURN`-returning targets never trigger a refuse and so behave as ordinary conditional captures (fire once, commit on success) — this is the json.sno idiom and is unaffected by this fix.

## 8. NOT DONE HERE

- The pre-existing `{}`/`{"a":1}`/`[{"a":1}]` heap-exhaustion under `json.sno`'s benchmark-iteration harness (§5) — reproduced, not investigated; may already be covered by `FINDING-2026-08-19-s169-ptj-json-has-no-curve-it-has-two-walls.md`, not cross-checked here.
- `json-alternate-af-spin` (the comma-hang row) — independent, untouched, still open.
- Whether entries committed *before* a rejected one in the same pump call should themselves be rolled back on overall match failure — out of scope for this row (no witness here exercises mixed plain+computed-name queues), flagged for whoever owns full dcap-transaction semantics next.
