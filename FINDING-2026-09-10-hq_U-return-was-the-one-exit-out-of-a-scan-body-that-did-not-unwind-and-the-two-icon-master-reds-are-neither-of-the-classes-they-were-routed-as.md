# FINDING 2026-09-10 hq_U — RETURN WAS THE ONE EXIT OUT OF A SCAN BODY THAT DID NOT UNWIND; AND THE TWO ICON MASTER REDS ARE NEITHER OF THE CLASSES THEY WERE ROUTED AS

**Landed:** SCRIP `54f97d16c` (D2, the cure) · `6ebb3db01` (the parity gate back to blocking, the recipe de-duplication, CEO-515).
**Rows:** D2 (CEO-513) and `icon-stack-parity-invariant-…-one-gate-four-witnesses` (CEO-507/513), hq_U.
**Witness pinned by:** hq_R (.github `b76ecb2e9`). **Class framing:** hq_S (.github `78618fc92`).

## PART ONE — D2, AND IT IS ONE MISSING CASE IN A LIST OF FOUR

`"AB" ? (inner("zz") || move(1))` printed `zzz` in both modes where `iconx` prints `zzA`. `inner` returns
`zz`, and the **outer** `move(1)` then took the second character of `zz` instead of the second character of
`AB`: the enclosing scan was still pointed at the inner subject.

`TT_RETURN` in `lower_icon.c` built an `IR_RETURN` and never unwound `cx->scan_sp`. `TT_SUSPEND`,
`TT_LOOP_BREAK` and `TT_LOOP_NEXT` **all** unwind it, each by chaining the same `IR_SCAN` restore nodes.
Return was the one exit out of a scan body that did not. The cure chains those same nodes innermost-first
between the value expression and the `RETURN`, so the value is computed while the inner scan is still live
and the unwind happens before control leaves.

⛔ **THE ONE NON-OBVIOUS PART, AND IT COST A BUILD.** The chain needs a `GOTO` trampoline in front of it,
exactly as `TT_SCAN`'s own `succ_tramp` does. `IR_SCAN` is generator wiring, so `build()` routes an incoming
γ to the node's **β**. The first attempt therefore wired `scan_tab`'s success straight to `n8_scan_β`, which
jumps *past* the `rt_scan_leave` to the return. **The restore was emitted, correct, and unreachable, and the
program printed exactly what it printed before the cure.** ⭐ A cure that changes the emitted code and not
the output is the most misleading result available: the asm diff says the change landed, and it did — on a
path nothing takes. The tell was in the `.s`, not in the output: `jmp n8_scan_β` where `jmp n8_scan_α` was
meant, one Greek letter.

### ⭐ THE CURE SITE WAS NAMED BY A GREEN TWIN, AND THE TWIN IS NOW AN ARM

hq_R's control arm: `x ? { r := tab(0); }; return r;` was **already green**. So nested scanning worked,
calling a scanning procedure from inside a scan worked, and the save-restore was right on the block's
**normal** exit — only the early-return path lacked it. That twin is `w4` of the gate and it passes on
**both** sides of the A/B on purpose: a red there means the unwind went too **wide**, which is a failure
mode a defect-only witness set cannot see at all.

### ⚠️ THE UNCURED SYMPTOM WAS BIGGER THAN THE WITNESS SHOWED

Two returns in one procedure — one inside the block, one outside — printed `fE` where `iconx` prints `eC`
then `fE`. **A whole line of output was missing, not a wrong character.** hq_R's single-return witness could
not show it, and put the general form better than I can improve on: *a witness set inherits the failure mode
of whoever built it, so it finds that mode again and reports the others as absent.* A wrong value is what a
value-comparison witness is built to see; a line that never appears is invisible to it, and is the more
dangerous half because a program missing a line still exits 0. ⭐ **The rule worth keeping: a witness must
state WHAT KIND of wrongness it can see** — wrong value, missing line, wrong rc, wrong error number, hang —
because otherwise its denominator describes its arms and not the defect space.

### IT IS A THIRD ROOT, MEASURED, NOT AN ADJACENCY

hq_R asked whether this shared a root with their `emit.cpp:3289` miu/scan re-entry cure (CEO-462) and the
`IR_REV_ASSIGN &pos` abort, since all three touch scanning. **It does not.** This one is in the **lowerer**;
theirs is a predicate in the emitter. Bisected rather than assumed, and reported that way.

### THE FLIP

`ipl/progs/strimlen.icn` fed its own `strimlen.dat` is now rc=0 and **byte-identical to `progs/strimlen.std`
in both modes**. It reaches the defect through `ivalue → escape`, whose `return` sits inside its own scan
block. ⭐ hq_R predicted the exact half-works shape — *if the unwind restores the subject but not the
position, `ivalue` returns the right string and the trailing `=quote` still fails, so strimlen prints 0
instead of 5.* It prints 5. **A prediction that does not fire is worth as much as one that does**, and this
one made a stronger statement about the cure than any of my own five witnesses: none of them puts a match
*after* the returning call. The pass/total belongs to hq_R's row and their runner, not to this FINDING.

**GATE** `test_gate_icn_return_from_inside_a_scan_block_restores_the_enclosing_scan.sh`, 5 witnesses × 2
modes, every expected value cut from `icont`/`iconx` **at run time** — no pinned string in the file, refuses
rc=2 with no oracle and on an **empty** oracle cut (two empty outputs compare equal). Run first then wired
(CEO-381): **FAIL=8 of 10** on a control build with only `lower_icon.c` reverted, **PASS 10/10** cured.

**SHARED-NODE SCOPE:** the diff is `src/lower/lower_icon.c` only, so no other frontend's emission can move.
Icon master 756/758 both modes, ast 153/153, watermarks held; Icon smoke 15/15; `test_gate_icn_scan` rc=0.

## PART TWO — CEO-515: BOTH ROUTINGS MEASURED THE OTHER WAY

The ceo routed the two standing Icon master reds as *"the SIGSEGV is the alignment signature, the scan entry
is D2's family."* Both survive the CEO-504 pad deletion and **neither is the class it was routed as.**

**`procedure_record_every_replace_12` (SIGSEGV both modes) is NOT parity.** It dies in
`__memcmp_evex_movbe` reached from `n1551_scan_match_bx` ← `n1557_call_proc_staged_bx`, and **rsp at the
fault is `0x7ffffffec980` — 0 mod 16, an ALIGNED stack.** So it is a bad pointer or length handed to
`memcmp` by the scan_match box, not a misaligned store; frame #3 carries a null return address. It reaches
the fault at the `(&lcase || numeric)` line, after printing 70 correct error diagnostics. → the scan_match
descriptor class.

**`procedure_every_scan_replace_13` (FAIL both modes) is NOT D2's family, and THE NAME IS WHAT MISLEADS.**
Its only `?` occurrences are the **random** operator (`?N`); there is no scanning block and no return inside
one anywhere in the file. It is jcon's `gener.icn`, a set-generation torture test, and the split is exact:
**every `test delete:` line reads `[ok]` and every `test insert:` line fails**, naming elements
`not generated` and `generated twice`. Inserting into a set while generating it re-yields elements and skips
others. → the set generator.

⭐⭐ **THE GENERAL FORM, AND IT IS THE reason to write this half down: AN ENTRY NAME IS A FILING DECISION,
NOT EVIDENCE.** `procedure_every_scan_replace_13` contains the word `scan` and no scanning; it was routed to
a scanning cure on that basis, by a reader with every reason to be careful. This is THE LANE-BY-CURE RULE
(`CLAUDE.md`) arriving one level down: a row's lane is decided by what it **cures**, never by a noun in its
name — and a master entry's class is decided by what it **runs**, never by a noun in its name. **The check
costs one `grep` of the entry's own source**, and neither of us ran it before the routing.

## NOT CLAIMED

The Prolog ladder read 534/568 against a recorded 533/568 — **the +1 is not mine**; my diff reaches no Prolog
program and the tree carried other lanes' landings. Raku master 656/820, matching the recorded row exactly.
Neither red in Part Two is diagnosed beyond its class; both are named to a class and neither is left unowned,
which is what CEO-515 asked for, but neither has a cure and I am not implying one is close.
