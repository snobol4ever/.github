# FINDING s173 — EVAL FAILS (p.131 made true for the RUN half), and the `$()` ruling's PREMISE is falsified by the oracle

**Seat:** seat2 (`/home/claude2`, Claude Opus 5, CN front) · **Queue row:** `cn-oracle-rulings` (rank 9)
**Brief:** HQ ruling per Lon s168 *"use SPITBOL as an Oracle"* — (4) `$()` = ORACLE-READS (option (b), supersedes the HQ-35 consistent-strict recommendation) and (5) EVAL-vs-342 = whatever live sbl does. Unblocks `SEAT-CN-3` item 4.
**Baseline:** SCRIP `1ac779ad` · corpus `fa84039e` · oracle `x64/bin/sbl -b` (live, every receipt below is a run, not a recollection).

## Verdict in one line

**Ruling (5) is DELIVERED and green in both modes. Ruling (4) is HALF-DELIVERED and half-BLOCKED — because the probe the brief ordered falsifies the truth table option (b) was phrased against, and the faithful answer is bigger than the ruling's own words.** A question is with HQ; nothing was freelanced past it.

## 1. The `$()` premise is FALSE — measured

s153's truth table opened with `read declared $("&N") -> 42 (same cell as &N: correct)` and called the undeclared row an *asymmetry* needing a seal ruling. **There is no shared cell.** Live sbl, verbatim:

| probe | oracle answer | what it proves |
|---|---|---|
| `&ANCHOR = 1` then `$('&ANCHOR')` | **`[]`** (null) while direct `&ANCHOR` reads `1` | two different cells |
| `$('&ANCHOR') = 'HELLO'` then direct `&ANCHOR` | **`1`, unchanged**; `$('&ANCHOR')` reads `HELLO` | an indirect write never reaches keyword space |
| `$('&NEVERSET') = 99` | accepted **silently**, reads back `99` | no seal, no diagnostic, no keyword involved |

**LAW: in SPITBOL `$('&X')` names an ORDINARY VARIABLE literally spelled `&X`, a namespace wholly DISJOINT from the keyword `&X`, in BOTH directions.** ARCH-SN4-CONSTANTS's *"No bypass via `OPSYN`/`$('&X')`/aliasing"* is therefore **VACUOUS for the `$()` clause, not merely "narrow to writes"**: the seal lives on the cell and `$()` addresses a different one. Option (b) told this seat to narrow a sentence about a bypass that does not exist.

**Where SCRIP actually stands** (this is the part the s153 table never separated):
- **UDC OFF (default): SCRIP IS ALREADY ORACLE-EXACT.** The whole `o_write` probe reproduces byte-for-byte. Pinned now in `probe/cn/cn_indirect_is_ordinary_var.{sno,ref}` — **.ref minted from the live oracle**, green m3+m4. This is ruling (4)'s read half: it needed no code, and it now has a regression guard it never had.
- **UDC ARMED: BOTH halves diverge.** `$('&N')` returns `42` (routed to the constant CELL, oracle says null) and `$('&N') = 99` raises **341** (oracle assigns silently).

## 2. Why the `$()` code change is BLOCKED and not guessed — ⛔ CLOSED s174: HQ-61 RULED **(i) faithful**, and it is LANDED

**This section is history, not orientation.** HQ-61: *"your probe governs — ORACLE-FAITHFUL CONFIRMED … BOTH halves; drop 341-on-indirect-write; the ARCH-SN4-CONSTANTS `$()` clause goes VACUOUS."* Delivered the next session at this seat — `is_const` turned out to be the namespace tag already, so the split needed no key mangling; 40/0 gate, 0 `.s` movers, corpus identical. Receipts, mechanism, and the one silent-wrong-answer trap it exposed: `FINDING-2026-08-20-s174-dollar-indirect-is-a-disjoint-namespace-and-is_const-is-the-tag.md`. The costing below is kept because it is what the ruling chose between.

"ORACLE-READS" taken literally directs `$('&N')` to answer **null**, not `42` — so the ruling's own name calls for a read-side routing change that option (b)'s body does not mention. And the two halves cannot be split the way (b) implies: routing reads to the ordinary variable while writes keep hitting the sealed keyword cell yields a program where `$('&X') = 1` errors 341 and `$('&X')` then reads a *different, untouched* cell. That is not "the two halves agreeing", it is a new incoherence. **Question routed to HQ via the QUESTION BOX with these receipts; per RULES.md this seat did not freelance past it.** Both candidate outcomes are cheap once ruled:
- **(i) faithful** — route `$()` wholly to the ordinary-variable namespace; both halves agree trivially; the ARCH sentence's `$()` clause is struck as vacuous.
- **(ii) (b)'s letter** — keep 341 on the indirect write as a knowingly non-oracle divergence; narrow the sentence to WRITES; accept that the read half must then also stay non-oracle (`42`) or the split above appears.

## 3. Ruling (5) — EVAL FAILS, and it is now true

Manual v3.7 **p.131: "EVAL fails if evaluation of its argument fails."** Live sbl, measured:

| fragment | oracle | `&ERRTYPE` | `&ERRTEXT` |
|---|---|---|---|
| `EVAL('&NEVERSET')` | **FAILS**, runs on | 251 | `keyword operand is not name of defined keyword` |
| `EVAL('UNDEFINEDFN(3)')` | **FAILS**, runs on | 22 | `undefined function called` |
| `EVAL('1 / 0')` | **FAILS**, runs on | 14 | `division caused integer overflow` |
| `EVAL('3 +')` | **FAILS**, runs on | 221 | `syntax error: missing operand` |

`reached-end` prints in every case. **SCRIP terminated the whole program with 342.**

**SCRIP already honoured p.131 for the COMPILE half** — a fragment that will not parse returns a NULL chain and the EVAL takes `:F` (`EVAL('3 +')` fails on both engines at HEAD). Only the **RUN** half was missing. Three edits, no new global, killswitch `SCRIP_EVAL_FAILS=0`:

1. **`runtime_eval.c` — `eval_chain_run_guarded()`**, the boundary. Pushes `g_core_errjmp_stk` and BORROWS `g_error` (the arm `core_runtime_error`'s conversion is already gated on), saving and restoring it on every exit so the borrow is invisible outside the frame; `-1` because the conversion arm decrements only `g_error > 0`, so it spends no credit and cannot perturb a program that set the cell. Push/pop discipline copied from `by_name_dispatch.c:1483` (restore to the `my` snapshot, never a decrement) so a longjmp from a deeper frame cannot strand it. Pool and cache are deliberately untouched by failure — a chain that failed at RUN time is a valid artifact that failed on program state, so it caches exactly as a successful one does; **releasing the blob on the failure path is the s172 B2c use-after-free wearing a different hat.**
2. **`core.c` — the conversion test moved ABOVE the report and ABOVE both `exit(1)`s**, and narrowed `g_error != 0` → `g_error != 0 && g_core_errjmp_n > 0` in the same breath so nothing else moves. Both moves are load-bearing: **above the print** because a caught error has no business on stderr (KW-5's `&ERRLIMIT` arm already spells that rule — *"no message is displayed"* — and the oracle fails in total silence); **above `core_err_is_terminal`** because error 22 is ON that list and the oracle FAILS `EVAL('UNDEFINEDFN(3)')`, so a boundary catching behind the terminal exit cannot implement p.131 at all.
3. **`keywords.c` — `rt_kw_publish_error()`**, the publish half `kwb_error` cannot lend: `kwb_error` welds DECIDING (its `&ERRLIMIT` test) to publishing, and EVAL's conversion is unconditional — the oracle converts with `&ERRLIMIT` untouched at its default 0 — so calling it would have silently spent a credit the manual never charges for.

**⛔ A LIFETIME BUG THIS COST A CYCLE, RECORDED SO THE NEXT BOUNDARY DOES NOT REPAY IT:** publishing at the CATCH site read freed stack and `&ERRTEXT` came back null. Nearly every caller builds its message in a stack buffer (`char eb[192]; snprintf(eb, ...); core_runtime_error(342, eb)` is the tier-3 keyword arm verbatim) and longjmp unwinds that frame. **The publish must happen one frame before the jump, while `msg` is still live.**

## 4. The pinned gate event fired — as designed

s153 minted `cn_t1_eval_undecl.err_sno` as an abort lane and said why: *"This witness pins TODAY'S behaviour in both media so KW-5 moves it deliberately rather than silently."* The CN-4 gate carried the matching assertion `grep 342 <stderr>`. **This ruling moved it, and the gate went red on the first run — the pin did exactly its job.** Promoted `.err_sno` → `cn_t1_eval_undecl.{sno,ref}` (it no longer aborts, so the abort-lane convention no longer fits), and the gate's three CN witnesses now ride one loop asserting **.ref match in both media AND an EMPTY stderr**. The silence assertion is not decoration: `core_runtime_error` printing before the conversion leaves stdout perfect and stderr full of errors the oracle never emits — a regression the `.ref` structurally cannot see.

**⛔ The `cn_t1_eval_undecl.ref` is ORACLE-LAW-DERIVED, not an oracle run, and the file says so.** `&USER_DECLARED_CONSTANTS` has no sbl counterpart, so that exact program cannot run on the oracle; the control flow it pins is oracle-run byte-for-byte in the sibling `cn_eval_fails_not_aborts.{sno,ref}`. The two are meant to be read together.

## 5. Measurements — every claim A/B'd against ORIGIN HEAD in a separate worktree (s149 standing law)

| instrument | baseline `1ac779ad` | this seat | verdict |
|---|---|---|---|
| SNOBOL4 crosscheck m3 | PASS=308 FAIL=9 | PASS=308 FAIL=9 | **identical, same 9 names** |
| SNOBOL4 crosscheck m4 | PASS=306 FAIL=10 SKIP=1 | PASS=306 FAIL=10 SKIP=1 | **identical, same 10 names** |
| DIVERGE (m3 vs m4) | 1 (`141_pat_eval_double_fn_arbno`) | 1 (same) | **identical** |
| CN-4 / UDC gate | 22 PASS **1 FAIL** (the pin) | **32 PASS 0 FAIL** | pin retired, 10 assertions added |
| Icon smoke m3/m4 | 14/14, 0 FAIL | 14/14, 0 FAIL | identical |
| Prolog smoke | 3 PASS 2 FAIL | 3 PASS 2 FAIL | identical |
| `.s` md5 sweep | — | **0 movers / 80 comparable** | codegen byte-identical; no artifact regen owed |
| new witnesses | — | 3 witnesses, **m3+m4 green, 0 DIVERGE** | |

**Revert probe (the gate is not vacuous):** `SCRIP_EVAL_FAILS=0` takes the CN-4 gate to **8 FAIL**, naming both new witnesses in both media plus the stderr-silence assertions.

**The SNOBOL4 smoke's `define` FAIL is PRE-EXISTING and was proven so, not assumed:** stashed to bare origin HEAD, rebuilt, and `define` emits the same empty output there. Not this seat's.

**⛔ `test_crosscheck_prolog.sh` IS FLAKY IN THIS CONTAINER — a trap for the next A/B.** Repeated runs of the SAME binary read PASS=112/FAIL=1/SKIP=76, then 111/2/76, then 110/2/77. This seat's first reading looked like a one-program IMPROVEMENT over baseline and was **noise**; re-running is what caught it. Baseline sits in the same band. **Treat any single Prolog-crosscheck delta of ±1–2 as unmeasured until it repeats.** (Also note the suite silently reads PASS=0 FAIL=0 from a worktree without `S4E_HOME` set — the s149 "board prints a plausible FALSE table when it cannot see the corpus" class, alive in this script too.)

## 6. Divergences found while minting, deliberately NOT ridden — each is upstream of EVAL

Riding any of these would have gated this ruling behind an unrelated repair, so they are named here and left:

1. **Undefined function: SCRIP answers code 5 at top level where the oracle answers 22** — and **inside a fragment it answers NOTHING AT ALL**: `EVAL('UNDEFINEDFN(3)')` SUCCEEDS with null where the oracle fails. The fragment path never raises, so the EVAL boundary has nothing to catch.
2. **Integer division by zero does not raise at any level in SCRIP** (`X = 1 / 0` yields null, top level and fragment alike); the oracle raises 14.
3. **The 342-vs-251 code split is alive on the DEFAULT arm.** A direct `&NEVERSET` read answers 342 with UDC unset — `rt_udc_on()` is true by default, so the CN-4 namespace-close arm at `keywords.c:377` (which answers the oracle's 251) is not the default path. The new witness pins control flow and `DIFFER(&ERRTEXT)` rather than `&ERRTYPE` precisely so this ruling is not gated behind that one.
4. **`&ERRTEXT` wording and `&ERRTYPE` codes are not oracle-verbatim for the compile half** — SCRIP says `parse error: syntax error` / `&ERRTYPE` 0 where the oracle says `syntax error: missing operand` / 221.

## 7. State of `SEAT-CN-3` item 4

- **EVAL-vs-342 half: CLOSED.** Implemented, witnessed on the live oracle, green m3+m4, gate assertion added, revert-probed, 0 movers everywhere else.
- **`$()` half: CLOSED s174** (was BLOCKED ON HQ when this FINDING was written). HQ-61 ruled option (i); landed, witnessed, gated, revert-probed — see the s174 FINDING. **`SEAT-CN-3` item 4 is now closed in BOTH halves.**
