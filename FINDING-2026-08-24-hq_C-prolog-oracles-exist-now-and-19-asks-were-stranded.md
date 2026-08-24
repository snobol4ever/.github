# FINDING — the Prolog oracles exist now, and 19 HQ asks were stranded in a retired mailbox

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-24 (s272) · **Mode:** FLEET-12
**Trees:** SCRIP `ab9c087c` / corpus `fea43840f` / `.github` `e813bb4c`

---

## 1. THE PROLOG ORACLES ARE INSTALLED AND FUNCTIONAL — MULTIPLE ROWS REASON FROM THE OPPOSITE

**Measured, and executed rather than merely located:**

| binary | path | version | verified |
|---|---|---|---|
| `swipl` | `/usr/bin/swipl` | SWI-Prolog **9.0.4** | ran a program, printed `ok` |
| `gprolog` | `/usr/bin/gprolog` | GNU Prolog **1.4.5** | present |
| `icont` / `iconx` | — | — | ⛔ **genuinely ABSENT** |

⛔ **Do not generalise this to Icon.** The Icon oracle gap is real and unchanged. This seat's `CLAUDE.md` preflight asserted all four were "not installed on the box at all"; it is corrected, and it has now been wrong **in both directions**, so the standing instruction is to **re-run the preflight rather than trust the prose**.

**Why this is a finding and not a footnote.** `prolog-assertz-retract-abolish-unmasked` — the row carrying Prolog's first honestly-graded numbers — says in bold at STEP 3 that no oracle exists, therefore `.expected` files are the authority, and warns: *"if a `.expected` is itself suspect you must say so rather than quietly conforming to it."*

⭐ **That caveat can now be discharged by measurement instead of carried as a risk.** Its 12 failures must be re-graded against `swipl` **before** any cure. ⛔ **A `.expected` that disagrees with SWI-Prolog is a corpus defect — curing SCRIP to match it would be conforming to a fabricated reference**, precisely what STEP 3 warned against and could not previously test.

⚠️ **Dialect discipline is not optional here.** `RULES.md` already carries *"CHECK WHICH DIALECT THE ORACLE SPEAKS BEFORE YOU GRADE A CORPUS WITH IT"*, written after 30 of 120 `.ref` pairs went false-red against a wrong-dialect oracle. SWI-Prolog and GNU Prolog differ on **exactly** the `assertz`/`retract`/`abolish` semantics this corpus exercises — logical-update-view, `abolish` on predicates with live choicepoints, ISO conformance. **Name the oracle in every number's label.** ⭐ Two oracles is an asset: where they agree the expected behaviour is settled; **where they disagree, the disagreement is itself the finding** — route it, never average it.

⛔ **Sequencing: this comes AFTER the harness repair.** The rung scripts currently SKIP-and-exit-0 (see `FINDING-2026-08-24-hq_C-the-regrid-turned-a-red-board-green.md`), so a grading run today measures nothing at all.

---

## 2. NINETEEN ASKS STRANDED — MEASURED CONSEQUENCES, NOT A HYPOTHETICAL

`s4e_hq()` (`s4e_msg.sh:63-66`) falls back to the **s256-retired `hq/` mailbox** for any seat without an `HQ` file. Seats **01-08 have one; 09-16 do not.** The fleet view now reports **19 unread there, oldest ~30 hours** (it was 17 earlier in this same session — it is still bleeding). Row `hq-asks-stranded-in-retired-unified-mailbox` (rank 1) owns the fix.

**Two consequences confirmed by reading the actual messages, not inferred:**

**(a) A Lon override sat unread for ~30 hours.** seat01 routed it correctly under LOOP rule 6 on 2026-08-23: Lon directed, in chat, that `zeta-frame-rsp-second-wild-write` be finished ahead of the `icon-n1-wire-stack-crossing` doorbell. ⛔ **HQ was blind to a direct Lon instruction for a day and a quarter** — the exact outcome CLAUDE.md names: *"an override HQ never hears about is worse than the contradiction itself."*
✅ **No damage — verified rather than assumed:** both rows show live claims, so seat01 honoured Lon's sequencing regardless. **The channel failed, not the seat**, and seat01's handling was correct on every count (Lon's word taken immediately, override routed same session, resumption correctly identified as a continuation of an existing RUNNING claim rather than a fresh pick).

**(b) seat16 is the worst-affected seat: 4 of the 19 are theirs.** Their `audit-corpus-what-is-ungated` ruling request sat ~29 hours. ⭐ **Four converged audit passes were being read as three silent deferrals.** Ruled this session on all five asks.

---

## 3. THE seat16 RULING, AND THE ONE PART WORTH GENERALISING

Full text in `audit-corpus-what-is-ungated.task.md`. The transferable half:

⛔ **Their exclusion POLICY was adopted; their NUMBER was refused as stale.** Re-measured on the current tree:

| component | seat16 (pre-re-grid) | hq_C (post-re-grid) |
|---|---|---|
| total program files | 5,144 | **4,847** |
| `probe/` | 1,019 | **1,197** |
| IPL archive | 851 | **851** |

**Neither number was wrong when taken; both were overtaken** — the suites pilot alone deleted 248 files while new probe ladders added 178.

⭐ **RULED: the coverage denominator is a COMMAND, never a constant.** It recomputes on the live tree and prints its own inputs. ⛔ **Do not pin an integer into a goal file or README** — the corpus has been re-shaped **three times in four days** (s269 flatten, s271 `lon` move, s272 re-grid), so a pinned coverage figure is wrong within days and gets quoted for weeks. This is `RULES.md:105` (TRANSCRIPTION IS WHERE PROVENANCE DIES) applied to a denominator rather than a benchmark.

Also ruled: **IPL is gated then mined, never preprocessed** — rewriting 851 upstream files to insert semicolons would destroy the third-party provenance CEO's re-grid deliberately preserved, and is the same class as editing a `.ref` to make a board green. And on the sweep-script nomination, hq_C **ruled the criteria and delegated the pick**, explicitly declining to nominate from a list of filenames — the same paper-approval mistake this HQ made and had to withdraw earlier today on the `g_dtax_bid` route.

---

## 4. ROUTING

`CLAUDE.md` preflight + digest corrected (this seat was also 1 of 15 roots stale on the SEGV-handler attribution; corrected, gate went 15 → 14). Law telegram on that retraction sent to all 16 seats + hq_P + ceo. seat01, seat16, seat04, CEO each answered directly. `prolog-assertz-retract-abolish-unmasked` carries the STEP-3 supersession.
