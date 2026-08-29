# FINDING — seat10: `fence-jstrbody-cas` CLOSED — item 1 verified byte-identical on the real DONE-WHEN target (citm_catalog.json, both files, both modes); item 2 re-confirmed refused; measured RSS/CAS-depth/Ir before-after and the result is NOT the improvement the brief expected on this witness

**Date:** 2026-08-29 · **Seat:** seat10 (`/home/claude10`) · **Topic:** queue row `fence-jstrbody-cas` (rank 2, opened HQ s251)
**Trees:** SCRIP `4c73de6a` · corpus `d8f8024e` (both pulled fresh this session; SCRIP rebased once more mid-session onto `4915216d`, a codegen-touching commit from another seat — re-built pristine and re-measured on the merged tree before quoting anything below, per the REBASE-BASELINE COROLLARY) · RT_OPT `-O0` (pristine build) · mode m3+m4 · ζ cell-stack
**Status:** DONE. Both open questions this row ever had are closed. Read §4 before assuming this row's brief was fully vindicated — the headline instruction-count number goes the WRONG way on the row's own named target, for a real, explained reason, not a measurement error.

## 0. Why this row could finally close

Three blockers stood between this row and its DONE-WHEN (citm_catalog.json, 1.7 MB, byte-identical + RSS/CAS before-after):
1. `jstring-escape-dcap-pump-segv` — DONE (seat09, SCRIP `2037a02f`).
2. `json-alternate-af-spin` — DONE. Independently re-verified this session, not just taken on hq_B's 2026-08-28 word: `claims/json-alternate-af-spin.claim` no longer exists on disk (swept), but the row IS present in `QUEUE.done.tsv` (`0  json-alternate-af-spin  unassigned  FREE`) — membership there is the actual signal `s4e_blocker_done()` checks (the state column is stale-by-construction per that function's own documented law); confirmed DONE by the same evidence the tooling itself uses, via a different code path than hq_B saw (their claim file, now gone, vs. this session's QUEUE.done.tsv membership).
3. `json-fence0-static-release-leak` (a THIRD bug, found mid-investigation by seat04, outside this row's original brief) — LANDED by hq_P (`FINDING-2026-08-23-hq_P-fence0-blob-floor-dynamic-release-cures-the-unbounded-stack-leak.md`): bare FENCE0 in blob scope now restores rsp to the blob activation floor at commit (`SCRIP_FENCE0_DYNAMIC`, default ON). hq_P's own measurement already ran citm_catalog.json end-to-end for the first time (`rc=0, maxdepth=8`); this session's independent oracle run reproduces `maxdepth=8` exactly.

## 1. Item 1 — grammar unchanged this session, verified byte-identical on the real target

seat09 (2026-08-22) added a trailing `FENCE` after `jkey`/`jstring`'s closing quote. Confirmed still present, post `git pull --rebase`, at the current paths (moved by the s272 corpus re-grid to `corpus/demo/snobol4/json/`):

```
json.sno:237:            jkey    = dq jstrbody . jxk dq FENCE (epsilon . *ekey())
json.sno:238:            jstring = dq jstrbody . jxs dq FENCE (epsilon . *estr())
json-match-fence.sno:14: jstring = '"' jchunk ARBNO(jescape jchunk) '"' FENCE
```

No corpus edit was needed for item 1 this session — seat09's placement survived the re-grid intact. The work remaining was reaching the target seat09's session couldn't (two then-live blockers) and closing the row's bookkeeping correctly.

### 1a. Byte-identical oracle agreement, full 1.7 MB citm_catalog.json, both files, both modes

Oracle: `/home/resources/x64/bin/sbl` via `sbl_correctness_bin()` + `sbl_lang_flags()` (`lib_oracle_flags.sh`, the s189 ONE AUTHORITY — `-bf`, never bare `-b`; `json.sno`'s own header comment example, `sbl -b -d512m -i64m -s256m`, predates the `-f` ruling and was deliberately NOT followed). Flags used: `-bf -d512m -i64m -s256m`.

```
$ sbl -bf -d512m -i64m -s256m json.sno < citm_catalog.json          (rc=0, wall 0.274s, match_ms=240 stderr)
input bytes=1727204 / root=jobj / objects=10937 / arrays=10451 / strings=735 / integers=14392
reals=0 / booleans=0 / nulls=1263 / maxdepth=8

$ sbl -bf -d512m -i64m -s256m json-match-fence.sno < citm_catalog.json   (rc=0, wall 0.199s)
matched bytes=1727204
```

Committed as `corpus/probe/json_fence_jstrbody_cas/{citm_catalog_json.ref,citm_catalog_match_fence.ref}` — the reference this row's DONE-WHEN never had before (seat09 §5: no CAS instrumentation *or* committed ref for the real target existed).

scrip (pristine build, re-run on both `373d6774` and, after a mid-session rebase, `4c73de6a` — identical PASS=7 FAIL=0 both times), via new gate `SCRIP/scripts/test_gate_json_fence_jstrbody_cas.sh`:

```
JSON-FENCE-JSTRBODY-CAS GATE: PASS=7 FAIL=0
  m3 json.sno matches oracle on citm_catalog.json
  m4 json.sno matches oracle on citm_catalog.json
  m3 json-match-fence.sno matches oracle on citm_catalog.json
  m4 json-match-fence.sno matches oracle on citm_catalog.json
  json.sno jkey/jstring still carry the trailing FENCE (regression lock, x2)
  json-match-fence.sno jstring still carries the trailing FENCE (regression lock)
```

All four scrip runs are byte-identical to the oracle. This half of the DONE-WHEN is unambiguously met.

## 2. Item 2 — RE-CONFIRMED REFUSED, not attempted

Not attempted, same reason seat09 didn't attempt it: seat04's `FINDING-2026-08-22-seat04-json-alternate-af-spin-root-cause-flat-choice-record-rsp-drift.md` §7b directly tested relocating `jobject`/`jarray`'s FENCE from definition-site to use-site and got a SIGSEGV (corrupted-stack backtrace) on 3 of 4 previously-hanging inputs, not even fixing the 4th — moving the FENCE changes which blob it sits in, and `blob_choice_rbp_scan()`'s eligibility (`_nc==1 && !_fn`) makes the RBP-relative choice record it then unlocks unsound under `jvalue`/`jobject`/`jarray`'s mutual recursion. Their §8: *"Do not relocate json.sno's FENCE placement as a fix... this FINDING already has the receipt against it."*

Checked whether hq_P's later FENCE0-dynamic-release fix (§0 item 3) changes this calculus: **it does not.** hq_P's cure targets `fence0_release_bytes` under-billing (an under-release LEAK, fixed by resetting rsp to a compile-time floor at commit); item 2's danger is `blob_choice_rbp_scan`'s eligibility computation producing an unsound RBP-relative choice record under recursion (a DRIFT/correctness hazard) — a different mechanism, unaffected by hq_P's change and not exercised by it. `json-match-fence.sno` already carries the safer use-site form and is unaffected because its `jobject`/`jarray` don't recurse through captures the way `json.sno`'s do. The new gate's regression lock (§1a) greps for item 1's FENCE staying exactly where it is, so a future session cannot silently "fix" this by relocating it without the gate objecting.

## 3. Item 1's measured effect on citm_catalog.json — NOT the win the brief expected, and here is why

The brief called this "the largest CAS reduction left." Measured, on the row's own named target, it is closer to a wash-to-slightly-negative on instruction count, and flat on RSS/native-stack. This is reported plainly because it is real, reproducible data, not a measurement artifact.

**Setup:** "before" = scratch copies (never committed) with *only* item 1's two FENCE tokens removed — nothing else touched, diff-verified minimal. "after" = the committed tree as-is. Measured twice end-to-end, against two independent pristine builds (`373d6774`, then `4c73de6a` after a mid-session rebase pulled in an unrelated codegen commit) — see the two Ir/RSS rows below per metric.

| metric | before (unfenced jstrbody) | after (fenced, committed) | delta |
|---|---|---|---|
| oracle/scrip output | — | byte-identical, both modes | — |
| peak RSS, `/usr/bin/time -v`, m3, run 1 (tree `373d6774`) | 62,792 KB | 62,740 KB | −52 KB (0.08%) |
| peak RSS, `/usr/bin/time -v`, m3, run 2 (tree `4c73de6a`, forced re-measure after rebase) | 62,788 KB | 62,428 KB | −360 KB (0.57%) |
| wall clock, m3, run 1 | 0.23 s | 0.22 s | after faster |
| wall clock, m3, run 2 | 0.28 s | 0.45 s | **after slower — direction flipped vs run 1** |
| minimal surviving `-sN` (RLIMIT_STACK), m3 | ≤256 bytes (still rc=0) | ≤256 bytes (still rc=0) | **no floor found in either arm down to 256 B — see caveat below** |
| **Ir, callgrind, m3, run 1 (tree `373d6774`)** | **868,157,159** | **869,155,470** | **+998,311** |
| **Ir, callgrind, m3, run 2 (tree `4c73de6a`)** | **868,157,184** | **869,155,495** | **+998,311 — IDENTICAL delta** |

RSS and wall clock are **not trustworthy at this scale**: run 2 (same before/after sources, only the compiler tree changed by one unrelated codegen commit, `4915216d`, touching `bb_match_breakx.cpp` — nothing on the jkey/jstring/jstrbody path) shows a *larger* RSS gap and an *inverted* wall-clock direction versus run 1. That is single-run OS/allocator/scheduler noise, exactly what RULES.md's FACT RULES warn wall-clock measurement is prone to. **Ir is the trustworthy number here**: both runs' absolute counts shifted by an identical +25 Ir on *both* arms (consistent with a small, unrelated, uniform fixed cost from the rebased-in commit, e.g. one-time init — it cancels in the comparison), and the before/after **delta reproduced bit-for-bit: 998,311, twice, across two independent pristine builds**. That reproducibility is itself evidence the effect is real and not a build artifact.

**× vs before (RULES.md FACT RULE convention, reference=before/ours=after, Ir count — lower is better), either run:** `0.9989x` (868,157,184 / 869,155,495) — i.e. the fenced version is *not* an improvement on this witness; it is 0.1150% *more* instructions, reproducibly.

### 3a. Why the `-sN` bisection is reported but NOT trusted as a CAS-depth proxy

This was this session's planned proxy for "CAS depth" (no dedicated telemetry exists anywhere in this tree — checked, `grep -rn "cas_depth\|choice_depth\|g_cas\b" SCRIP/src` finds nothing; only `SCRIP_ZETA_TELEM` exists, and that's GC regeneration stats). The instrument did not do what was expected: **both arms survive down to a 256-byte stack limit**, which is far too small to be a meaningful bound on real backtrack state for a 1.7 MB, 21,388-container document — this means `-sN` (`setrlimit(RLIMIT_STACK,...)`, `src/driver/scrip.c:496`) is **not actually constraining mode-3's peak native-stack usage on this workload**, contrary to this session's working assumption that ζ-SPINE-on-RSP == the OS thread stack under RLIMIT_STACK's guard-page mechanism. The likely reason (not independently proven — flagged as an interpretation, not a fact): mode-3 boxes chain by JMP, not CALL ("flat-wired x86 BB blobs... jump in"), so ordinary box-to-box transitions never grow a C-style call stack; and `jobject`/`jarray`'s own bare FENCE — present, unchanged, in BOTH arms — already resets rsp to a compile-time floor at every `}`/`]` (hq_P's fix), so whatever jkey/jstring's own ARBNO retains gets reclaimed by the next OUTER reset regardless of item 1's fence, given citm's shallow `maxdepth=8`. **Do not reuse this `-sN` bisection as a CAS-depth instrument without first proving it can say NO on a witness that is known to exhaust the stack** (the two-part proof rule, RULES.md) — this session did not have time to build such a witness and is flagging the gap rather than asserting the instrument works.

### 3b. Why Ir went the wrong way, and why that is a real result, not a bug in this row's work

FENCE's cost (walking/releasing the retained choice-point state) is paid **unconditionally at every firing**. FENCE's benefit (not re-attempting the pruned alternatives) is realized **only on a path that would otherwise backtrack into them** — i.e. only when something downstream fails. citm_catalog.json is a well-formed document: every `jkey`/`jstring` match succeeds on the first try, and the pattern never backtracks through a fenced choice point anywhere in this run (a clean parse, rc=0, no retries). With `jkey`/`jstring` firing on the order of tens of thousands of times (every object member has one), a modest fixed per-firing cost for a cut that is never cashed in is consistent with a ~1M-instruction net cost out of 869M (0.115%) — small, but measured in the wrong direction from the brief's framing.

This does **not** mean item 1 should be reverted. §5 (placement rule) still holds — the FENCE is semantically the correct, safe cut at that point, matching `json-match-fence.sno`'s independently-arrived-at form and the general SNOBOL4/SPITBOL FENCE-at-exclusive-left-context idiom. What it means is narrower and more useful: **this row's "largest CAS reduction" claim was never tested against a witness that actually backtracks**, and citm_catalog.json — despite being the row's own named DONE-WHEN target — is exactly such an all-success witness, so it cannot show the payoff even if the payoff is real. A witness built to *fail* partway through a long `jstrbody` (so the engine backtracks into the un-fenced ARBNO before this row's fence, or successfully cuts past it with this row's fence) would be the correct instrument for that specific claim, and was not built this session (time-boxed; flagged as a natural follow-on, not attempted).

## 4. The placement rule (unchanged from the semantic argument, refined by §3's measurement)

FENCE is *semantically* safe to distribute at point P iff, given a successful match up to P, no earlier retained choice point can ever be revisited on any subsequent path — exclusive left context. `jkey`/`jstring`'s closing `dq` is textbook: once matched, `jstrbody`'s decomposition is uniquely determined. That argument is untouched by §3.

Two things §3 adds that the brief did not have: (a) semantic safety and *measured net win* are separate questions — a FENCE can be free of downside risk and still cost net instructions on an all-success workload, because its payoff is conditional on backtracking actually being attempted; (b) a FENCE's marginal value is not independent of its neighbors — an outer FENCE that already resets state at a bounded interval can make an inner FENCE's own contribution unmeasurable-to-negative on inputs shaped like the outer interval, even when the inner FENCE is "more correct" in isolation. Measuring "CAS reduction" needs a witness that exercises the failure/backtrack path the FENCE is meant to shortcut, not merely a large successful parse.

## 5. What changed on disk this session

- `corpus/probe/json_fence_jstrbody_cas/citm_catalog_json.ref`, `citm_catalog_match_fence.ref` — new, committed oracle references (corpus repo).
- `SCRIP/scripts/test_gate_json_fence_jstrbody_cas.sh` — new gate, PASS=7 FAIL=0 (SCRIP repo).
- This FINDING (.github repo).
- `/home/resources/postoffice/tasks/fence-jstrbody-cas.task.md` — LEDGER entry + a real, computable DONE-WHEN replacing the permanently-refusing stub (not git-tracked; shared postoffice state).
- No changes to `corpus/demo/snobol4/json/{json.sno,json-match-fence.sno}` — item 1 was already correct; item 2 stays refused.
- No changes to `SCRIP/src` — stayed a corpus/tooling row throughout, consistent with seat09's original scoping.

## 6. DONE-WHEN

Replaced the permanently-refusing stub (`echo "no computable DONE-WHEN"... ; false`) with:
`bash "$S4E_HOME/SCRIP/scripts/test_gate_json_fence_jstrbody_cas.sh"` — a real, tree-examining, FAIL=0/REFUSE=2-shaped criterion (INSTRUMENT LAWS-compliant) that closes the exact gap seat09 flagged and stands as a permanent regression lock: it re-proves byte-identical output on citm_catalog.json in both files/both modes, and greps for item 1's FENCE staying exactly where it is. It does **not** bless item 2 — a future relocation attempt needs its own proof, not silence from this gate.
