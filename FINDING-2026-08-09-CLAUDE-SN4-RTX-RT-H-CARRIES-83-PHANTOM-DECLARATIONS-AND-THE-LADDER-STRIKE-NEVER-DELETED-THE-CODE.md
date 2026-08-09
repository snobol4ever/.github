# FINDING 2026-08-09 — `rt/rt.h` CARRIES 83 PHANTOM DECLARATIONS, AND A LADDER STRIKE IS NOT A CODE DELETION

**Session:** s_this (2026-08-09, Sonnet 4.6). **Goal:** `GOAL-SNOBOL4-RTX.md`. **HEAD at open:** `64e1bcbf`.
**Status: CENSUS LANDED AS DOCUMENT ONLY. THE DELETION WAS ATTEMPTED, COULD NOT BE PROVEN, AND WAS REVERTED. WORKING TREE CLEAN.**

---

## 1. WHAT WAS SOUGHT

RTX-10's row says the vstack audit is discharged and that the remaining work is
"the live MISC/IO surface plus deleting the dead declarations." That deletion half
looked like a clean, concurrency-safe, template-free eradication slice. It was taken.

## 2. RTX-10's DELETION HALF IS ALREADY DONE — THE ROW IS STALE

Step 0 at HEAD, re-proved rather than inherited:

- `nm out/libscrip_rt.so` — **zero** `rt_push_*` / `rt_pop_*` / `rt_halt_tos`, in the full
  symbol table, not merely the dynamic one.
- `grep -rn 'rt_push_\|rt_pop_\|rt_halt_tos' src/ --include=*.c --include=*.h --include=*.cpp --include=*.S`
  — **zero hits, including the declarations themselves.**

`git log -S` names the commit: **SCRIP `1b251a7d`**, "DELETE 42 phantom declarations from
rt/rt.h: 30 `rt_pat_*` … + 12 vstack `rt_push_*`/`rt_pop_*`/`rt_halt_tos`".

⇒ **RTX-10's deletion half was completed and the ladder row was never updated.** This is the
PHANTOM RUNG shape RTX-6 already recorded once ("planned work that is already done"), and it
cost this session the first half of its budget. **`nm` cannot catch it; only reading git history can.**

## 3. THE `rt_pat_*` POINTER IS NOW WRONG IN BOTH DIRECTIONS

RTX-9's row reads: *"all 30 `rt_pat_*` spellings are declaration-only in `rt/rt.h:38-67`
with zero definitions."* At HEAD both halves of that sentence are false:

- The 30 were **deleted** at `1b251a7d`. `rt/rt.h:38-67` today holds `rt_acomp`,
  `rt_lcomp`, `rt_define_entry` — unrelated symbols. A session following the line number
  lands on the wrong text.
- There is now **exactly one live `rt_pat_*`**: `rt_pat_prim_int`, `T` in the `.so`,
  added by the concurrent D08-FIX (`e3ef8f7d`) for `LEN(*var)` deferred-integer fetch.
  A future session that "knows" `rt_pat_*` is a dead family will misread a live symbol.

⭐ **A line-number pointer into a file another seat is editing has the same rot as a symbol
name copied from prose** — the (a)-class rot ARCH §1 already names, one level down.

**The rest of RTX-9's row survives step 0(b) intact:** `pat_lit`, `pat_alt`, `pat_break_`
(trailing underscore) and `pat_any_cs` all round-trip **byte-identically** against `nm`,
and the family is **32 defined constructors**, exactly as the row claims.

## 4. THE CENSUS — 83 DECLARED-BUT-NEVER-DEFINED SYMBOLS IN `rt/rt.h`

Method: extract every function declared in `rt/rt.h` (185 total); subtract every symbol
defined (`T`/`t`) across **the `.so`, the `scrip` binary, and every `.o`** — not the `.so`
alone, per ARCH §7 step 0(c); then cross-check against definition-shaped lines in `src/`
to catch unbuilt code (the `blk_alloc` class).

| | count |
|---|---|
| declared in `rt/rt.h` | 185 |
| **declared, never defined anywhere** | **83** |
| of those, **zero references outside their own declaration** | **51** |
| of those 51, non-Prolog (RTX/SNOBOL4 territory) | **36** |
| of those 51, Prolog-family | **15** |

⚠ Two symbols (`rt_last_ok`, `rt_set_last_ok`) initially read as "has a source definition."
They do not — the matching lines are `extern` **re-declarations** in `rt.c` and
`unification.c`. **A definition-shaped regex matches `extern`; tighten it or verify by `nm`.**

### 4a. ⭐⭐ THE HEADLINE: THE LADDER STRUCK THESE NAMES IN PROSE AND NEVER DELETED THE CODE

Among the 36 non-Prolog phantoms are names this ladder **already declared dead in writing**:

- `rt_nv_get`, `rt_nv_set` — RTX-7: *"BOTH PHANTOMS, struck s204, re-confirmed s208 by `nm`."*
- `rt_match_variant` — RTX-8: *"STRUCK s216 — PHANTOM (decl-only `rt/rt.h:30`, zero definitions, zero call sites)."*
- `rt_incr`, `rt_decr`, `rt_neg`, `rt_exp` — RTX-6: *"ARE PHANTOMS — struck s204 per ARCH §7."*
- `rt_concat`, `rt_lcomp`, `rt_acomp` — RTX-3's three, ARCH §7 step 0's founding example.

ARCH §7 step 0 requires striking dead names out of **the ladder rung text and the table**.
Every one of those strikes was performed. **None of them removed the declaration.** The
symbols have therefore been re-discovered, re-`nm`-ed and re-confirmed across s164, s204,
s208 and s216 — because the artifact that makes them look alive was never touched.

⇒ **PROPOSED AMENDMENT TO ARCH §7 STEP 0:** the strike clause should read *"strike the dead
names out of the ladder rung text, this table, **and the header that declares them**, in the
SAME commit."* A name struck only in prose remains discoverable, and each rediscovery costs a
step-0 sweep. `rtx_str.S:6` even carries a **comment** explaining that `rt_concat`/`rt_lcomp`/
`rt_acomp` are phantoms — documentation of dead code that could have been deleted instead.

### 4b. THE 36 (non-Prolog, zero-reference, safe by inspection)

```
rt_arith_cmp_nodes  rt_call            rt_call_builtin   rt_cap_assign
rt_coerce_num       rt_decr            rt_define         rt_define_entry
rt_do_nreturn       rt_do_return       rt_exec_stmt_pat  rt_exp
rt_field_get        rt_field_set       rt_frame_enter    rt_frame_leave
rt_idx_get          rt_idx_set         rt_incr           rt_init
rt_limit_begin      rt_limit_inc       rt_limit_more     rt_load_frame
rt_main_init        rt_match_blob      rt_match_variant  rt_neg
rt_nv_get           rt_nv_set          rt_set_stno       rt_store_frame
rt_toby_real        rt_unhandled_op    rt_unhandled_sm   size_value
```

⚠ `rt_match_blob` is a **three-line** declaration. A line-oriented delete leaves orphaned
continuation lines that still compile as part of the next declaration. Delete by full
declaration (to the terminating `;`), never by line number.

### 4c. THE 15 PROLOG-FAMILY PHANTOMS WERE DELIBERATELY LEFT ALONE

`rt_atom_length` `rt_atom_string_pair` `rt_choice_cut_enter` `rt_choice_cut_exit`
`rt_choice_cut_unwind` `rt_copy_term` `rt_cp_save_caller_env` `rt_downcase_atom`
`rt_env_alloc` `rt_get_cut_flag` `rt_pl_arith_cmp_cells` `rt_pl_is_cell`
`rt_term_cmp_nodes` `rt_trail_mark_pop` `rt_upcase_atom`

`PL-FR-4` and `PL-ZETA-CELLS` are both in the active concurrent set and may be about to
*implement* these. A dead declaration costs nothing at runtime; deleting one out from under
a seat that is mid-implementation costs a rebase collision. **Left to the Prolog seats.**

## 5. ⛔ THE DELETION WAS ATTEMPTED AND COULD NOT BE PROVEN — SO IT WAS REVERTED

The 36 were deleted (222 → 184 lines, 38 physical lines, header structure verified intact,
all 36 confirmed absent). Build clean, zero errors, `.so` mtime moved. Then:

| | m3 | m4 | DIVERGE |
|---|---|---|---|
| baseline, session open | **260/57/0** | 222/66/29 SKIP | 14 |
| after deletion + full rebuild | **259/58/0** | 222/66/29 SKIP | 14 |

**One program moved: `161_pat_defer_fn_nested_match`, PASS → FAIL.** Deleting an unreferenced
declaration cannot change behavior, so one of two things was true, and **the difference matters
more than the rung**:

1. the deletion was not as inert as the census said, or
2. **the BASELINE was measured against a stale `.so`.**

Hypothesis 2 has direct evidence: at session open `make libscrip_rt` printed
**"Nothing to be done"**, so the baseline crosscheck graded a `.so` that was never rebuilt
in this session, while the post-deletion run followed a `touch` + **full** rebuild of every
template and runtime object. That is precisely the **STALE BINARY / BUILD OK trap** already on
record (s_2026-07-30 SUBJ-CELL FINDING).

Discrimination attempted: `161` is **deterministic** at the post-deletion build — 10/10
identical md5 — and its output genuinely differs from `.ref` (`fail2/calls=3` vs
`match2/calls=2`), so it is **not** the `160`-class non-determinism. The decisive A/B
(restore pristine header → **full** rebuild → re-run `161`) **did not complete: the rebuild
exceeds the container's command timeout, and a detached `nohup make` is killed with the tool
session.** The question is therefore OPEN.

⇒ **Nothing was committed. `git status` clean, `rt.h` back to 222 lines, zero diff vs HEAD.**
An unproven eradication that moves a program is exactly the shipped-unexercised-port class
ARCH §7 step 2b warns about, read from the other side. **The census is the deliverable; the
deletion is not.**

## 6. ⛔ WHAT THE NEXT SESSION MUST DO FIRST — AND IT IS NOT THE DELETION

**Re-baseline against a FULL rebuild before trusting any watermark in this file.**
If `161_pat_defer_fn_nested_match` fails at pristine HEAD after `touch src/runtime/rt/rt.h &&
make libscrip_rt`, then the **cursor watermark of 260/57/0 is an artifact of an incremental
build** and the true m3 figure is 259/58/0 — which would mean every seat quoting 260 is
quoting a stale number, not just this one. That is a shared-state defect and outranks RTX-10.

Mechanics for whoever runs it: the full `libscrip_rt` link is ~4-5 minutes here, longer than
one command window, and `nohup` does not survive. Build in **polled segments** (`make -j4`,
then re-invoke `make` to resume; it is incremental and converges), or ask Lon for a longer
window. **Do not conclude anything from a build you did not watch reach "Built:".**

Only after that: re-attempt the 36-symbol deletion, and if `161` moves again with a
*genuinely* pristine baseline, the census in §4 is wrong somewhere and the symbol that
matters is in that list.

## 7. LEDGER

- ✅ RTX-10 deletion half — **ALREADY DONE at `1b251a7d`**; row is stale, strike it.
- ✅ RTX-9 `rt_pat_*` pointer — **stale in both directions**; correct it (§3).
- ✅ Census — 83 phantoms, 51 zero-reference, split 36 / 15 by owning family.
- ✅ ARCH §7 step 0 amendment proposed — strike in prose **and** in the header.
- ⛔ Deletion — attempted, unproven, **reverted**. Tree clean.
- ⛔ **OPEN AND OUTRANKING: is the 260/57/0 watermark a stale-build artifact?**
- ⛔ Container limitation of record: full `libscrip_rt` rebuild exceeds one command window and
  detached builds are killed with the session. **Any rung needing a from-scratch runtime
  rebuild needs Lon's routing or a longer window.**
