# FINDING — seat09: `fence-jstrbody-cas` — item 1 LANDED (narrowly verified), item 2 REFUSED (proven unsafe by a sibling seat mid-session)

**Date:** 2026-08-22 · **Seat:** seat09 (`/home/claude09`) · **Topic:** queue row `fence-jstrbody-cas` (rank 2, opened HQ s251)
**Status:** PARTIALLY LANDED. Claim left OPEN, not `done` — the row's own DONE-WHEN (byte-identical + CAS/RSS measurement on the full 1.7 MB `citm_catalog.json`) is unreachable this session, now for **two independent reasons** (see §4).

## 0. WHAT CHANGED MID-INVESTIGATION — READ THIS FIRST

The brief's own FIRST STEP said this row is blocked behind `json-alternate-af-spin` and to wait. While building comma-free witnesses to make partial progress anyway, this session (a) found a second, unrelated, unclaimed defect (`FINDING-2026-08-22-seat09-jstring-capture-with-any-escape-segvs-rt-dcap-pump.md` — captured JSON strings with ANY escape SEGV `rt_dcap_pump()`), then (b) pulled `.github` mid-session and found seat04 had landed the `json-alternate-af-spin` **root cause** (`FINDING-2026-08-22-seat04-json-alternate-af-spin-root-cause-flat-choice-record-rsp-drift.md`) — including an experiment that **directly tested this row's own item 2** and found it unsafe. That changed this row's shape from "one blocked row, two independent sub-items" to "one item landable now, one item refused with a receipt." Both are recorded below rather than silently dropping item 2.

## 1. ITEM 1 — LANDED: `jstrbody` FENCE after `jkey`/`jstring`'s closing quote

**Change**, all four corpus files (`corpus/programs/snobol4/demo/{json.sno,json-match-fence.sno}` and their `corpus/benchmarks/snobol4/demo/` twins):
```
- jkey    = dq jstrbody . jxk dq (epsilon . *ekey())
+ jkey    = dq jstrbody . jxk dq FENCE (epsilon . *ekey())
- jstring = dq jstrbody . jxs dq (epsilon . *estr())
+ jstring = dq jstrbody . jxs dq FENCE (epsilon . *estr())
```
(`json-match-fence.sno` has no separate `jkey`; only its one `jstring = '"' jchunk ARBNO(jescape jchunk) '"'` gained the trailing `FENCE`.)

**Rationale, unchanged from the brief:** once the closing quote is matched, a concrete byte sequence has exactly one valid `jchunk`/`jescape` decomposition — `jstrbody`'s `ARBNO` choice points are retained but structurally can never be used again on a successful parse. FENCE prunes them at the earliest point they're provably dead. Textbook exclusive-left-context placement, per Lon's own stated criterion (brief, HQ s251).

### 1a. Why item 1 does NOT inherit item 2's danger — checked, not assumed

Seat04's finding (§4 there) roots the `af`-spin hang in `blob_choice_rbp_scan()` (`emit.cpp:2305`): a `match_alternate` box gets the safe, drift-immune RBP-relative choice record only if its blob has **exactly one choice point and no FENCE** (`_nc==1 && !_fn`); otherwise it falls back to the FLAT/stack-carved mode their FINDING proves unsound under recursion+backtrack. Item 2 of this row's own brief (move `jobject`/`jarray`'s trailing FENCE from definition-site to use-site) directly flips which blob a FENCE sits in for `jarray`'s own 2-arm alternation — seat04 tested exactly that edit and got a `SIGSEGV` on 3 of 4 previously-hanging inputs (§7b there). **Before landing item 1, this session checked whether adding FENCE to `jkey`/`jstring` — textually nested inside `jvalue`'s 7-arm alternation, but touching no `|` of its own — perturbs any `match_alternate` box's `_nc`/`_fn` anywhere in the program:**

- **Static, `--compile`d asm, both real target files, scratch copies, baseline vs FENCE-added:** every `_match_alternate_af:` site (8 in `json.sno`, 8 in `json-match-fence.sno`) has the **identical RBP-vs-FLAT mode and identical relative offset**, same order, before and after — only box/label *numbers* shift (mechanical renumbering from 2 new boxes in `json.sno`, 1 in `json-match-fence.sno`). A normalized (`sN_`→`nX_`) full-file diff shows every remaining delta is either that renumbering or the two new `match_fence0` boxes at the edit site itself — nothing structural moves elsewhere in the file, including inside `jvalue`/`jobject`/`jarray`'s own boxes.
- **Dynamic, both modes, both real target files (post-edit, in place, not scratch):** 6 witnesses (`{}`, `[]`, `{"a":1}`, `[{"a":1}]`, a long bare string, and a 3-level-deep nested object→object→array→string, all comma-free at the *structural* level and escape-free — see §4 for why both restrictions were necessary) — **12/12 OK**, byte-identical to `sbl -bf` (modulo the pre-existing, separately-tracked `JOBJ`/`jobj` datatype-case mismatch, normalized out of the diff and unaffected either way). The deep-nested witness specifically exercises recursive `jobject`→`jarray`→`jstring` invocation (the same *kind* of recursion seat04 flagged as the hazard for item 2) with the new FENCE firing at the innermost level while outer frames are still open — no wrong answer, no crash, in either witness set.
- **Full corpus, direct A/B via `git stash`, same build, same run:** `test_corpus_snobol4.sh` — **PASS=357 FAIL=2 (m3) / PASS=355 FAIL=2 SKIP=2 (m4), IDENTICAL failing/skipped test names, with and without this edit.** `test_gate_emit_no_lang.sh` and `test_gate_template_medium_invisible.sh` both rc=0 (unaffected — this is a corpus-only change, no compiler code touched).

None of this constitutes the row's real DONE-WHEN (see §4), and none of it exercises the ARBNO-then-recede-into-alternation path that seat04's mechanism actually requires (my witnesses never backtrack — every match succeeds on the first try, by construction, same limitation §4 explains). It is real evidence against the *specific, named* danger this row now knows to check for, on the *specific* files this row targets — not a general safety proof.

## 2. ITEM 2 — REFUSED: do NOT relocate `jobject`/`jarray`'s FENCE from definition-site to use-site

**Not attempted.** Seat04 already ran this exact experiment (their FINDING §7b, same session, landed to `.github` while this row was in progress) and found it trades the `af`-spin hang for a `SIGSEGV` with a corrupted-stack backtrace on 3 of 4 previously-hanging inputs, and doesn't even fix the 4th. Their own §8 item 3: *"Do not relocate `json.sno`'s FENCE placement as a fix... If someone independently rediscovers this idea, this FINDING already has the receipt against it."* This session is that someone, and did not need to re-spend the experiment — it re-read the receipt instead. **The row's brief is wrong on this half** (LAW 17: a seat falsifying an HQ-authored brief hypothesis has delivered, not deviated) and should be corrected before anyone else attempts it fresh.

The row's own justification for item 2 ("the safer use-site form... rests on an invariant nothing checks") is not itself wrong as a *correctness* argument — `json-match-fence.sno` really does use the safer form, and really does avoid `json.sno`'s specific hang (seat04 §7a). What's now known that the brief didn't have: the reason the two forms behave differently isn't only the correctness invariant the brief named, it's that FENCE placement gates `blob_choice_rbp_scan` eligibility, and `jvalue`/`jobject`/`jarray`'s mutual recursion makes the RBP-relative slot this eligibility unlocks **unsound for a recursive box** (seat04 §7b's closing analysis) — so relocating the FENCE doesn't safely reproduce the sibling's good behavior, it trades one failure mode for a worse one.

## 3. WHAT THIS ROW'S BRIEF GOT RIGHT, STILL TRUE

`jstrbody`'s lack of a FENCE is real, is exactly the CAS-retention shape the brief described, and item 1's fix is the correct, safe cure for it — the file-scoped static+dynamic evidence in §1a is meaningfully stronger than "it compiles," even though it can't reach the full citm_catalog.json target this session.

## 4. WHY THE ROW'S DONE-WHEN IS STILL UNREACHABLE — TWO BLOCKERS NOW, NOT ONE

1. **`json-alternate-af-spin`** (unchanged from the brief): `json.sno` still hangs on any *structurally* comma-bearing input (multiple object members / array elements) — root-caused by seat04, not yet fixed (their own claim stays open too). `citm_catalog.json` is comma-saturated.
2. **NEW, this session: `rt_dcap_pump()` SEGVs on any captured string containing an escape sequence** (`FINDING-2026-08-22-seat09-jstring-capture-with-any-escape-segvs-rt-dcap-pump.md`), deterministic under `setarch $(uname -m) -R`, minimal witness `"\t"` (4 bytes). `citm_catalog.json` is "mostly strings" per this row's own brief and almost certainly contains escapes. **Even if af-spin were fixed today, this row's target file would likely still be unrunnable on `json.sno`** (the WORK member — `json-match.sno`/`json-match-fence.sno` have no captures and are confirmed unaffected by the SEGV, matching seat04's independent finding that they're also unaffected by the hang).

This is why item 1's verification in §1a is deliberately restricted to comma-free (structural) *and* escape-free witnesses — both restrictions are load-bearing, not stylistic; either kind of input in a witness would have confounded the fence measurement with one of these two unrelated, still-open bugs.

## 5. FOR WHOEVER CONTINUES THIS ROW

- Re-run `FINDING §1a`'s exact witness set (6 comma-free/escape-free cases, both modes, both target files) as the fastest regression check before touching anything further here — reproducible from this FINDING plus the corpus files as committed.
- Do not re-attempt item 2 without first reading `FINDING-2026-08-22-seat04-...-rsp-drift.md` §5/§7b in full — the fix directions named there (widen `blob_choice_rbp_scan`'s FENCE exclusion with recursion-safety accounted for, or make FLAT mode itself drift-safe) are compiler changes, out of a corpus-only row's scope, and belong to `json-alternate-af-spin` or a follow-on row, not here.
- Once `json-alternate-af-spin` is actually fixed (not just diagnosed) **and** the escape/SEGV defect is resolved, this row's real DONE-WHEN (`citm_catalog.json`, byte-identical, peak RSS + CAS depth before/after item 1's fence) becomes reachable in roughly the shape the brief already describes — item 1 is already landed, so that measurement is a rerun, not new development.
- CAS-depth instrumentation itself was not located/used this session (time-boxed in favor of the static asm-mode check, which answered the more urgent safety question first) — worth checking whether one exists before assuming it needs building.

## 6. WHAT I DID NOT DO, AND WHY

Did not attempt the `citm_catalog.json` measurement (blocked, §4). Did not touch `emit.cpp` or any compiler code (out of this row's scope; the relevant fix directions are seat04's to hand off, not mine to freelance). Did not investigate the new escape/SEGV defect's root cause beyond what's in its own FINDING (filed separately, not claimed). Did not mark this row `done` — DONE-WHEN is explicitly unmet.
