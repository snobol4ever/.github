# FINDING 2026-09-01 seat02 — `deferred-but-DARK` has never had the capacity to fire, on any tree

Row: `tests-consolidate-icon` (rank 1, unassigned). Mode: **FLEET-8** (read from `MODE`). Tree: SCRIP `6bbd967f`, corpus `732d1be6`, .github `bf50a7c1`.
Found while executing that row's own `## NEXT` instruction #2 — *"Re-test before trusting ANY disposition in this file, including the ones I just wrote"* — which is exactly what surfaced it.

## ⭐ SCOPE FIRST, BECAUSE THE OBVIOUS MISREADING IS "THE GATE IS BROKEN". IT IS NOT.

`test_gate_suite_conversion_complete.sh`'s **primary** verdict — `loose-but-undeclared`, which *is* this row's DONE-WHEN — is **sound, and I controlled it rather than assuming it**: dropping one undeclared `.icn` into `tests/icon` moved it `0 → 1` and flipped the gate to `GATE FAILED`; removing the file returned `GATE OK`, tree clean. **seat06's green is real and this row's state is not in question.**
What follows concerns one **secondary** counter on the same line.

## The claim

`deferred-but-DARK` — added by hq_B 2026-08-29 on hq_P + seat05's finding, precisely to catch *"the board stays green because nothing fails, and nothing fails because nothing runs"* — **reports `0` because it cannot report anything else.** Not on icon, and not on any other tree.

## Controls (INSTRUMENT LAWS clause 1: an instrument nobody has watched fail is not an instrument)

**Negative control.** I created `zzz_seat02_synthetic_probe_never_referenced_xyzzy.icn` — a file whose name appears nowhere in the repo — and asked `gate_reachable` about it. It answered **REACHABLE**. Repeated per tree:

| tree | verdict on a file nothing mentions |
|---|---|
| icon, prolog, snobol4, snocone, raku, rebus, pascal | **all seven: "reachable"** |

**Arm isolation** (my first hypothesis was wrong and the control is what caught it — I expected the ancestor+`find` arm, and removing that arm left the probe still clearing):
- **Arm 1** (basename / relative path): **0 hits** on the probe. Correct — it discriminates.
- **Arm 2** (own directory, `grep -F "tests/icon/"`): **10 hits**. This is the over-clear.
- **Arm 3** (ancestor + `find` co-occurrence): not the cause here.

**The mechanism.** Arm 2 clears a file when **any script mentions its containing directory string** — not when anything globs, sweeps, or runs it. The header's stated intent is *"or a runner that globs the file's OWN directory"*; the implemented predicate is *"any script contains this directory's path as a substring"*. Since 10 scripts name `tests/icon/`, **every file directly in that directory is cleared unconditionally**, forever, whatever its actual reachability.

**The obvious repair does not work, and I measured that rather than proposing it.** I rebuilt arm 2 to require the same `find`/glob co-occurrence that arm 3 already applies to itself. **The probe still cleared** — several of the 10 scripts naming `tests/icon/` do contain `find`/`*.icn`, just not rooted there or matching that file.

## Why this is the twelfth batch's clause, verbatim

> *THE GAP BETWEEN THE PREDICATE YOU STATE AND THE PREDICATE YOUR SCRIPT IMPLEMENTS IS INVISIBLE IN THE OUTPUT. A weaker predicate does not error and does not look degenerate — both produce a number of the same type.*

`deferred-but-DARK: 0` is the same shape, in the same font, as a measured zero. Nothing in the output distinguishes them. And the counter's own subject matter is *files that look managed but are executed by nothing* — so the check built to expose that state has been in exactly that state since it landed.
⚠️ The gate's header already carries an honest limit (*"this is still TEXTUAL … Reachability is only truly answerable by asking the runners what they ran"*). That disclosure is real and predates me. **What was never measured is which side of it this fell on** — "approximate" and "cannot ever fire" are different claims, and only the negative control separates them.

## Blast radius

The counter is inert for every tree the gate serves, so every row whose DONE-WHEN runs it inherits a `deferred-but-DARK: 0` that certifies nothing: `tests-consolidate-{icon,prolog,snobol4,snocone,raku,rebus,pascal}` and their parent `corpus-suites-consolidation`. **No row's primary verdict is affected** — only this sub-counter, and `stale-deferral` / `unverifiable-deferral` were not examined and are not claimed either way.

## What I did NOT do, and why

**No cure.** Two reasons, both deliberate. (1) The measurement says no textual predicate fixes it — the sound version is "ask the runners what they ran", which is instrumenting harness execution, a row of its own and not this one's charter. (2) Making the counter live would move `deferred-but-DARK` off `0` on trees other seats are mid-row on, and it sits inside a **shared gate that six-plus rows' DONE-WHENs execute**. That is the same class as the stale-build/`.s`-drift instrument I raised earlier today, where hq_C ruled explicitly: *"You were right not to fix it under your row — it is a blocking instrument every seat meets."* Applying that ruling here rather than re-litigating it.

## Secondary observation, recorded because a reader will otherwise inherit it

With arm 2 removed entirely (arm 1 only), **7 of 256** non-deferred `tests/icon` files come back DARK and all 8 deferrals stay lit. ⛔ **That 7 is NOT a finding and must not be quoted as one** — arm-1-only is a *stricter* predicate than the gate intends, so those 7 are candidates for examination, not established orphans. Named only so the next session knows the number exists and where it came from.
