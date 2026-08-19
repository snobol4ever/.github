# FINDING 2026-08-19 s149 — CN-6 LANDED (CLEAR no longer un-seals a &constant), THE HQ-21 INDICTMENT IS VOID AT HEAD, AND CLEAR() TURNS OUT TO BE A NO-OP FOR EVERY ORDINARY VARIABLE

**Seat:** web (Claude Opus 5). **Baseline:** SCRIP `f80c3f4d` (CN-4b + CN-5), corpus `a51c7d25`, x64 oracle live.
**Goal:** `GOAL-SNOBOL4-100.md` — finish `&USER_DECLARED_CONSTANTS`.

---

## 1. THE HQ-21 INDICTMENT DOES NOT REPRODUCE AT HEAD — MEASURED, FOUR ARMS

HQ (2026-08-19, HQ-21) convicted `746f0757` (KW-3b) of breaking the default arm: *"a WRITE `&W = "hi"` dies with READ error 342 at statement 0"*, *"the UDC gate reads 2/12 (claimed 12/12)"*, *"all 529 sweep md5s moved"*. **None of it reproduces on the pushed HEAD.**

| measurement at `f80c3f4d` | result |
|---|---|
| `&W = "hi"` / `OUTPUT = &W`, m3, KW_STATIC=0 | prints `hi` — no 342 |
| same, KW_STATIC=1 (armed) | prints `hi` — no 342 |
| `scripts/test_gate_udc.sh` | **PASS=12 FAIL=0** |
| `cn_udc_closed.err_sno` (namespace closed) | error **251**, oracle-verbatim text |
| `scripts/test_gate_kw_static.sh` armed | **10 PASS / 14** (last recorded watermark was 6/10) |

**Why HQ saw it and HEAD does not:** HQ bisected to `746f0757`, but **`4bbc8c4b` (CN-4) landed two commits later and is itself the repair HQ asked for.** HQ's repair item (1) was *"KW-3b's emit-time index resolution must FALL BACK … for any name not in the canonical keyword block"*; CN-4 placed the tier-2 `&USER_DECLARED_CONSTANTS` gate **above** the tier-3 fallthrough and restructured exactly that resolution order (`keywords.c:357` read side, `:424` write side). HQ measured a real defect at a real commit and then wrote the brief against a HEAD that already contained its fix. **The lesson is not that HQ was careless — it is that a bisect verdict expires the moment later commits land, and the brief must be re-measured at HEAD before it is executed.**

⛔ **Residue for HQ:** the LIVE CURSOR names SCRIP `d68ec482`, which **is not a valid object in the repo** (`git cat-file` fatal). HEAD is `f80c3f4d` with matching commit subjects. A cursor hash that was never pushed is the STALE-ORIENTATION (a) failure mode in a new place — the doc, not the push status, carried the fiction.

---

## 2. CN-6 LANDED — CLEAR SKIPS A SEALED &constant

**Defect (pre-existing, from CN-2):** `NV_CLEAR_fn` (`core.c:2378`) walked every bucket and nulled `e->val` without consulting `e->is_const`. A declared constant therefore went `PATTERN -> NULL` on `CLEAR()`, the read-side 342 could not fire (the ENTRY survives, so `NV_EXISTS_fn` stays true), and 341 then refused every restore: **permanently null AND permanently unwritable.**

**Contract, ORACLE-MEASURED not inferred.** Manual Ch.19 CLEAR: SPITBOL *"differs from SNOBOL4 by not clearing protected variables, such as ARB"*. Measured on `sbl`:

```
        OUTPUT = "before=" DATATYPE(ARB)   ->  before=PATTERN
        X = "gone"  ;  CLEAR()
        OUTPUT = "after=" DATATYPE(ARB)    ->  after=PATTERN     (protected: survives)
        OUTPUT = "X=[" X "]"               ->  X=[]              (ordinary: nulled)
```

A CN-2 cell raises 341 on any later write, so it **is** protected under SCRIP's own regime and must survive CLEAR by the same rule the oracle applies to `ARB`.

**Fix:** one arm in `NV_CLEAR_fn` — `if (!_e->is_const) _e->val = NULVCL;`. Keyed on `is_const` rather than on `name[0]=='&'` so the seal is enforced at the cell, matching the 341 site at `core.c:2301` and staying immune to OPSYN/indirect/FIELD aliasing. The primitive-pattern family (`&ARB`/`&BAL`/`&REM`/`&FAIL`/`&FENCE`/`&ABORT`/`&SUCCEED`) is untouched: it reaches its value through the BARE name via the tier-1 arm at `keywords.c:355` and owns no `&`-keyed NV cell.

**Witness `cn_clear_unseal.err_sno`, before → after:**

| | before | after |
|---|---|---|
| `DATATYPE(&Word)` pre-CLEAR | PATTERN | PATTERN |
| `DATATYPE(&Word)` post-CLEAR | **NULL** | **PATTERN** |
| `&Word = SPAN("xyz")` | 341 | 341 *(correct — still sealed)* |

Verified in **BOTH media** (m3 `--run`, m4 `--compile` + `gcc -no-pie`).

### BLAST RADIUS — PROVEN BY REACHABILITY, NOT BY THE UNSOUND md5 INSTRUMENT
`grep -rln "CLEAR(" corpus/ SCRIP/test/` (excluding `.ref`/`.md`/`.s`) returns **exactly one file: `corpus/probe/cn/cn_clear_unseal.err_sno`** — the witness this fix repairs. Zero programs in `corpus/programs/snobol4/` call `CLEAR(` at all. The changed code is unreachable everywhere else in the tree **by construction**, which is a strictly stronger statement than a 529-file md5 sweep and does not depend on the instrument the previous seat measured as unsound (7 of 510 programs unstable run-to-run under a fixed `.so`, five of them already crashing). Gates after the fix: **UDC 12/12**, **KW-STATIC armed 10/14** (unchanged failures: `kw_bare_shadow`, `kw_protected_write`).

---

## 3. ⭐⭐⭐ CN-7 LANDED — `CLEAR()` WAS A NO-OP FOR EVERY ORDINARY VARIABLE

Found while establishing the CN-6 contract; **A/B-proven pre-existing** — identical output with the CN-6 fix stashed and unstashed, so CN-6 neither caused nor masked it.

```
        X = "gone"
        CLEAR()
        OUTPUT = "direct=["   X      "]"
        OUTPUT = "indirect=[" $("X") "]"
```

| | oracle | SCRIP before | SCRIP after |
|---|---|---|---|
| direct | `[]` | `[gone]` | `[]` |
| indirect | `[]` | `[gone]` | `[]` |

**Mechanism — and it is NOT the design question this seat first thought it was.** My initial read routed this to a ruling ("does CLEAR walk the GVA plane, or do NV and GVA stop being two homes for one fact?"). Reading the file falsified that. `NV_t` already carries `cell` + `is_gva`, and **five sites spell the same store convention** — `is_gva ? *cell : val` at 2185 (GET fastpath), 2227 (GET), 2242 (SET fastpath), 2302 (SET), 2345 (PTR). `NV_CLEAR_fn` was **the only writer in the file that ignored it**, storing to `val` unconditionally. So CLEAR nulled a copy the compiled program never reads. There is no second plane to walk and no ownership question: the entry already knows where its storage is, and CLEAR simply never asked.

**Fix:** `if (!_e->is_const && !is_protected_pat_name(_e->name)) { if (_e->is_gva) *_e->cell = NULVCL; else _e->val = NULVCL; }` — the same two arms as 2242/2302, plus the two skip classes the manual names (CN-6's sealed constants, and the protected pattern family `ARB`/`ABORT`/`BAL`/`FENCE`/`FAIL`/`REM`/`SUCCEED`).

**Two things deliberately NOT done, each for a measured reason:**
- **Not routed through `NV_SET_fn`**, even though that is the store authority. `g_call_fastpath_off` is set to 1 exactly when a variable acquires an I/O association (`core.c:2912/2940`), which sends every subsequent `NV_SET_fn` down the slow path into `_io_chan_find_by_var`. A bulk reset must not fire I/O associations, and must not raise error 42 on a protected name the way an ordinary assignment does. CLEAR is not a series of user assignments.
- **`_var_reg` not updated.** `_var_reg_n` is **never incremented anywhere in the file** — it is declared, initialized to 0, looped over at 2242/2303/2318 and GC-visited at 2954, but nothing ever adds an entry. Those loops are already no-ops over empty storage, so there is no third home to keep in sync. (Flagged as dead storage; not removed this seat.)

### BLAST RADIUS — REACHABILITY, PROVEN AGAINST ALIASING
`NV_CLEAR_fn` has **exactly one caller** (`_CLEAR_`, `core.c:1205`). Across `corpus/programs/`, `corpus/probe/`, `corpus/crosscheck/` and `SCRIP/test/`, nine files mention the token `CLEAR` and **not one invokes the builtin**: `beauty/expression.sno` and `lon/sno/bootstrap.sno` carry it inside a builtin-*name string table*; `lon/sno/snobol4.sno:61` assigns `snoCLEAR = 'CLEAR'` once as a lexicon entry and never references it again (checked for OPSYN/indirect invocation — none); `csnobol4-suite/bench.sno`'s hits are a user-defined `CLEAR_D_VF`. The changed code is therefore unreachable from every corpus program **by construction** — stronger than an md5 sweep, and independent of the instrument s148 measured unsound. Gates after both fixes: **UDC 12/12**, **KW-STATIC armed 10/14** (unchanged failures `kw_bare_shadow`, `kw_protected_write`). Both fixes verified in **BOTH media**.

`g_sno_fz_unsafe`'s whole-program CLEAR poison in `lower_snobol4.c` is a *lowering* decision keyed on source text and is unaffected by this runtime change — but it is now poisoning against a CLEAR that finally does something.

---

## 4. THE INSTRUMENT — HARDENED, AND ONE CLAIM THAT DID NOT REPRODUCE

s148's item (1) was *"record `rc` beside the md5 and compare only `rc==0` programs"*. Done in `scripts/util_s_md5_sweep.sh`, **but the measurement first contradicted the diagnosis and that matters for the next seat.**

**The structural defect was real and is now fixed.** The old row test was `[ -s "$W/p.s" ]` alone: a compiler that dies partway still leaves a **non-empty truncated** `.s`, which was then hashed as a legitimate result — the s33 *"non-empty is not alive"* class living inside the instrument every codegen rung is validated against. Two truncated arms hash to two different md5s and masquerade as blast radius. Now `rc!=0` emits `COMPILE_RC_<rc>`, a **stable label**: a compile that segfaults reads `COMPILE_RC_139` in *both* arms and correctly shows as zero movers instead of two random hashes. `rc==0` with empty output emits `COMPILE_EMPTY`. Only rows carrying a real md5 are byte-identity claims.

**Validation (the instrument must prove itself):** 529 programs, before vs after — **527 md5-carrying rows byte-identical, 0 movers**; exactly the 2 failing rows relabeled `COMPILE_FAIL` → `COMPILE_RC_1` (`crosscheck/coverage/coverage_sno_nodes.sno`, `programs/snobol4/demo/expression.sno`).

⛔ **What did NOT reproduce, stated plainly.** s148 reported *"7 of 510 programs differ run-to-run under a FIXED `.so`"*. On this build: **two full sweeps, 529 programs, 0 movers.** And **zero** failed compiles emitted any bytes, so the spurious-md5 hazard has **no live instance on this tree today** — the hardening is byte-identical in effect here and was landed as insurance, not as a repair of an observed break.

⛔ **AND THE SYMPTOMS POINT AT A DIFFERENT INSTRUMENT.** s148's named evidence — rc **139/139/139/132/134** and *"the other two print `TIME()` deltas (`demo/calculator-1`, `demo/calculator-2`)"* — is **runtime** crash and **program-output** drift. `util_s_md5_sweep.sh` hashes `--compile` output; a `TIME()` delta cannot appear in a `.s`, and rc 139 there would be the *compiler* segfaulting, not the program. So s148 was measuring a sweep of **program output**, which this file is not. `ab_board_sweep.sh` — the obvious candidate — **already classifies rc correctly** (`TIMEOUT`/`LINKFAIL`/`ERROR` at lines 50–52) and is not the culprit either. **The unsound output-sweep s148 actually used has not been identified.** Whoever picks this up should get its name from s148 before assuming the instrument question is closed: this seat hardened the `.s` sweep, which is a real improvement and not the thing s148 measured breaking.

## 5. NEXT SEAT

1. **Identify s148's output sweep** (see §4). The `.s` sweep is hardened; the sweep that actually showed 7/510 instability is still unnamed. Do not treat the instrument item as closed.
2. **`NV_EXISTS_fn` as the 342 predicate** (`keywords.c:360`) — it tests entry existence, not assignment. CN-6 closes the one reachable hole (CLEAR-created null-with-live-entry); the predicate is still the wrong shape and should be revisited if any other path can null a cell without removing its entry.
3. **`_var_reg` is dead storage** — `_var_reg_n` is never incremented; the loops at 2242/2303/2318 and the GC visit at 2954 operate on permanently empty storage. Either it lost its producer in a refactor (in which case something that should be registering is not, and that is a latent bug) or it is vestigial and should be deleted. One history grep decides. NOT investigated this seat.
4. **ONE-AUTHORITY candidate, deliberately deferred:** the store shape is spelled at 2242/2302/2318 and the read shape at 2185/2227/2345. Collapsing them into one `_nv_store(NV_t*, DESCR_t)` is the right move **if** `_var_reg` proves live — but it touches the hottest path in the runtime and needs a corpus sweep to validate.
5. **CN-5 stays parked** pending `&`-in-GVA vs RTCC pricing. **T2 ruling still open.**
6. **Two inherited claims in a row failed to re-measure at HEAD** (HQ-21 §1, and the instrument instability §4). Neither author was careless — both measured something real at the time. The lesson is procedural: **re-measure an inherited verdict at HEAD before executing against it**, because later commits expire it.
