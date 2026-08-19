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

## 3. ⛔ NEW — `CLEAR()` IS A NO-OP FOR EVERY ORDINARY VARIABLE (routed CN-7, NOT fixed)

Found while establishing the CN-6 contract; **A/B-proven pre-existing** — identical output with the fix stashed and unstashed, so CN-6 neither caused nor masks it.

```
        X = "gone"
        CLEAR()
        OUTPUT = "direct=["   X      "]"
        OUTPUT = "indirect=[" $("X") "]"
```

| | oracle | SCRIP |
|---|---|---|
| direct | `[]` | `[gone]` |
| indirect | `[]` | `[gone]` |

**Mechanism:** `_CLEAR_` (`core.c:1203`) calls only `NV_CLEAR_fn`, which nulls `NV_t.val` in the hash buckets. The compiled program reads the **GVA-bound cell**, which CLEAR never reaches, so the null is written somewhere the program does not look. The direct and indirect reads **agree with each other in both engines** — that pairing is the point of the witness: this is not an indirection defect and not a read-path split, it is CLEAR failing to reach the storage the program actually uses. Manual Ch.19 is unambiguous that the null string is assigned to *all* user variables.

This is also the honest reason `lower_snobol4.c`'s `g_sno_fz_unsafe` treats a single `CLEAR` anywhere as a whole-program poison for static pattern staging: **the poison is correct, the clear is not.**

Witness minted: `corpus/probe/cn/cn_clear_user_var.{sno,ref}` (`.ref` generated from the live oracle). **Deliberately not fixed this seat** — the fix must decide whether CLEAR walks the GVA plane or whether NV and GVA stop being two homes for one fact (which is ONE-AUTHORITY territory and touches RTCC/GVA ownership), and that is a hunt, not a rung. END-OF-CONTEXT LAW: repro minted, routed, stopped.

---

## 4. NEXT SEAT

1. **CN-7** — the CLEAR/GVA split above. Start from `NV_bind_gva` (the s144 cursor already flagged it as unexamined) and decide the ownership question before writing code; do **not** simply add a second walk, which would spell one fact in two homes.
2. **Instrument** — s148's item (1) still stands: record `rc` beside the md5 in the sweep and compare only `rc==0` programs. CN-6 sidestepped it via reachability, but the next codegen rung cannot.
3. **`NV_EXISTS_fn` as the 342 predicate** (`keywords.c:360`) — it tests entry existence, not assignment. CN-6 closes the one reachable hole (CLEAR-created null-with-live-entry); the predicate is still the wrong shape and should be revisited if any other path can null a cell without removing its entry.
4. **HQ-21 brief is closed as VOID** — re-measure at HEAD before executing any inherited repair brief.
