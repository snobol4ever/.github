# FINDING 2026-08-19 s161 — THE KW FRONT CLOSES: TWO DEFECTS WERE MIS-ROUTED, AND THE DEFAULT IS FLIPPED

**Seat:** local (Claude Fable 5 → Opus 5), dispatched to `GOAL-SNOBOL4-100.md` **SEAT-KW** (D-3 continuation, ~75% at dispatch).
**Build:** SCRIP `02d96577`, corpus `4ffc0077`, oracle `x64/bin/sbl`. Verdict taken on a **pristine** tree (`make pristine`).
**Brief executed:** KW-5 → kw_bare_shadow analysis → DEFAULT-FLIP PREP. All three items closed; the front is at 100% of its brief.

---

## 0. HEADLINE

| # | what | status |
|---|---|---|
| **KW-5** | `&ERRLIMIT` converts keyword-write errors to statement failure (manual Ch.16) | ✅ landed, `kw_protected_write` green both modes |
| **s161-A** | `kw_bare_shadow` was **NOT B1** — it was `DATATYPE` of an unset variable answering NULL | ✅ fixed, row green, brief's routing was wrong |
| **KW-5b** | block initials seeded **lazily** ⇒ the answer depended on ACCESS ORDER — a live wrong answer | ✅ fixed, new witness minted |
| **KW-6** | **the default flip** — `&keywords` are static/direct-access unless `SCRIP_KW_STATIC=0` | ✅ landed with the full ladder |

Armed/default gate went **10/14 → 16/16** (two new KW-5b rows), with 4 standing pins OK.

---

## 1. KW-5 — THE &ERRLIMIT MECHANISM (the brief's item 1)

**Law (manual Ch.16 p.189, &ERRLIMIT):** *"When zero (the default), an execution error or user interupt results in program termination... When non-zero and either occurs, it is decremented by one, no message is displayed, and execution proceeds as follows: If an error label has been declared with the SETEXIT function... control is transferred to that label. If there is no SETEXIT label, SPITBOL converts the error to statement failure."*

SETEXIT does not exist in SCRIP, so **the no-label arm IS the whole mechanism**. `kwb_error()` (keywords.c) is that arm and is the ONE body both the by-name and by-index writers reach:

- `&ERRLIMIT == 0` ⇒ `core_runtime_error` terminates, **exactly as before** — the default arm is untouched by construction.
- `&ERRLIMIT > 0` ⇒ decrement, store the code in `&ERRTYPE` and the text in `&ERRTEXT` (Ch.16: both are where an execution error deposits its code and message), answer statement failure.

`kwb_write_ent` became tri-state (`-1` = converted); `rt_kw_write_idx` returns the assigned value or `FAILDESCR`; the KW-3b box finally uses the **ω edge the lowerer had already wired** since `lc_build(..., γ, ω)`. The legacy `SNO$KWSET` arm answers `FAILDESCR` the same way, so the fast and slow paths cannot disagree.

⚠ **The value test still fires before the protection test** (`&ALPHABET = 'x'` ⇒ 208, not 209) — oracle-measured at KW-1, unchanged here.

---

## 2. s161-A — `kw_bare_shadow` WAS MIS-ROUTED AS B1. IT WAS `DATATYPE`.

The s158 brief carried this row as **B1-class** (by-name dispatch, blocked behind D-18/T4) and instructed: *"ANALYSis, NOT fix... DOCUMENT the dependency with a witness and move on. Do NOT build the trampoline in this seat."*

**There is no dependency.** KW-2 had already fixed the bare-name hijack half of the witness. The entire surviving residue was **two rows**:

```
DT-STCOUNT=NULL     (oracle: STRING)
DT-ANCHOR=NULL      (oracle: STRING)
```

Minimal witness — no keyword, no dispatch, no trampoline:

```
	OUTPUT = 'DT=' DATATYPE(ZZ_NEVER_SET)     oracle: DT=STRING     SCRIP: DT=NULL
```

**SNOBOL4 has no null datatype.** An unset variable *is* the null string, and the null string is a STRING (manual p.24; the DATATYPE entry p.213 lists REAL/INTEGER/STRING/PATTERN/NAME/EXPRESSION and user datatypes — no NULL). `bn_type_datatype` mapped `DT_SNUL` to `"null"` for every caller; it now answers `"string"` for `DATATYPE` and keeps `"null"` for Icon's `type()`, which is real Icon semantics. Dispatching on the builtin NAME is that function's standing idiom (array/list, function/procedure sit two lines above).

**Blast, measured:** the corpus FAIL set **strictly shrank** — `161_pat_defer_fn_nested_match` (m3+m4) and `omega_driver` (m3) recovered, nothing went red. No `.ref` in the corpus expects a NULL datatype.

⛔ **The lesson is the standing law, again:** RE-MEASURE AN INHERITED BRIEF BEFORE EXECUTING IT. Had this seat obeyed the routing, a two-line fix would have been parked behind a trampoline nobody needed to build.

---

## 3. KW-5b — THE ANSWER DEPENDED ON ACCESS ORDER (found only because the flip was being prepared)

`kwb_init_once()` was reached **only** from `kwb_find` / `rt_kw_{read,write}_idx`. A program that never mentions a keyword therefore ran on the C initializers instead of the block's oracle-true values. That is a **wrong answer**, not a tidiness issue:

| program (armed) | SCRIP before | oracle |
|---|---|---|
| `L = INPUT` — no keyword anywhere | `[hello   ]` size **8** | `[hello]` size **5** |
| same, with one `&ANCHOR` read in front | `[hello]` size **5** | `[hello]` size **5** |

`&TRIM`'s oracle default is **1** (FINDING s146 §3: the oracle disagrees with its own manual p.191 here and the oracle wins), so lines arrive trimmed. Nothing had seeded it.

**Fix:** `rt_kw_seed_defaults()` runs from `core_lib_init` — the ONE hook both modes execute (m3 driver calls it directly; m4's generated `main` calls it via PLT before any blob), so the modes agree by construction. Gated on the killswitch, so the `=0` arm keeps the C initializers verbatim. Protected entries stay unseeded for `kwb_init_once`'s own measured reason (seeding them rewinds the live `&STCOUNT`/`&STNO` counters).

⛔ **THE GATE COULD NOT SEE THIS, AND THAT IS THE TRANSFERABLE POINT.** Every KW witness touches a keyword *by construction* — that is what makes it a keyword witness — so all 14 rows were green while a bare `L = INPUT` was wrong. A gate built from a feature's own witnesses is blind to the feature's effect on programs that do not use it. Witness minted: `corpus/probe/kw/kw_trim_lazy_seed.{sno,ref,dat}`, ref from live `sbl`.

**Gate hygiene:** `kw_unset_datatype` was excluded from the scored loop as an open HQ-owned B1 row; §2 closed it, so it became a STANDING PIN beside `kw_pattern_family` (arm-independent — scoring it would credit this gate with a result arming does not control). Both pins now share one `pin_row` helper.

---

## 4. KW-6 — THE DEFAULT FLIP, AND THE LADDER THAT EARNED IT

`rt_kw_static_on()` inverted: the block is ON unless `SCRIP_KW_STATIC=0`. **The switch inverted rather than disappearing**, so `=0` still restores pre-KW-2 behaviour verbatim and BASELINE-ARM keeps a same-arm baseline. Retiring the legacy arm is its own later step.

### Payoff — from the emitted `.s` of a four-statement keyword program

| | `=0` (legacy) | default |
|---|---:|---:|
| `SNO$KWSET` name strings | 2 | **0** |
| `rt_keyword_read/write@PLT` | 3 | **0** |
| `rt_call_arr@PLT` (by-name dispatch) | 6 | **4** |
| `rt_kw_{read,write}_idx` (rip-relative load + O(1) index) | 0 | **5** |
| emitted lines | 486 | **439** |

Both arms answer `n=5`.

### The ladder, on a pristine tree

⛔ Taken after `make pristine`: this session rebased onto another seat's T4 mid-flight and had only built incrementally, and HQ-27 ABI-mix is precisely the class that voided two prior sessions' conclusions. The pristine numbers match the incremental ones, which retires that concern rather than assuming it away.

- **BASELINE-ARM, legacy≡legacy:** pre-flip default arm ≡ post-flip `=0` — corpus **337 programs row-for-row identical, both modes**.
- **BASELINE-ARM, armed≡armed:** pre-flip armed ≡ post-flip default — **identical**.
- **Arms agree at HEAD:** `=0` ≡ default — **identical**. (Same answers, different route — the rung's whole point.)
- **Probe boards, byte-identical between arms:** m1 35 · cn 14 · arbnostore 10 · b1 5 · opsyn 19 · eval 18 · nret 13 · define 1 · beauty_suite 34.
- **Demos:** 21 of 23 byte-identical; `json` and `calculator-2` are **TIME() self-report noise, proven not arm effects** — the diff direction flips run to run (`match_ms=0` vs `1` in both directions) and the same arm differs from itself.
- **KW gate:** default **16/16**, 4 pins OK; `--legacy` **1/16** — the killswitch truly reverses.
- **UDC 23/23 · icon smoke 14/14 both modes · m3≡m4 on all 10 keyword witnesses.**
- The **7 `probe/kw` movers ARE the feature** — each moves a legacy-wrong answer to the oracle's.

---

## 5. OPEN / OWED

1. **`kwb_own[7]` → 0** (the oracle-251 default for `&USER_DECLARED_CONSTANTS`) — still its own gated step, untouched here.
2. **Legacy special-case retirement list** — the `=0` arm still carries the pre-KW-2 bare-name hijacks and the by-name cascades. Now that the default is flipped, that code is reachable only through the killswitch and can be scheduled for deletion.
3. **SETEXIT** does not exist. KW-5 implements the no-label arm of &ERRLIMIT only; a `SETEXIT`-bearing program still cannot intercept (manual Ch.19 defines the ABORT/CONTINUE/SCONTINUE protocol and the Goto-field loop hazard, &ERRTYPE 20/23/24/38).
4. **`&ERRTYPE` assignment should signal an immediate error** (Ch.16) — not implemented; it is the program-defined-error mechanism and pairs naturally with SETEXIT.
5. The corpus FAIL set at this HEAD is **m3 325/337 · m4 322/337**, unchanged by this front except for the two §2 recoveries.
