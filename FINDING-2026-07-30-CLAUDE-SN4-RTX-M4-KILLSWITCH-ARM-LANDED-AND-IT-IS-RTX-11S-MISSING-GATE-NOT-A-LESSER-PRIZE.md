# FINDING — s222 (2026-07-30): the m4 kill-switch arm is RTX-11's missing gate, not a lesser prize

**SCRIP `7b6719c1 (post-rebase; a further parallel push could move it again — `handoff_status.sh` is the push truth, NEVER this hash)`.** Lon's grant was "all your choices." I chose the instrument over the port. The
argument is a dependency, not a preference, and it is the whole finding.

## 1. The gap: five sessions claimed "both modes" on m3-only evidence
ARCH §7 step 3 has mandated a both-modes kill-switch since s217. The script minted at s219 had a
`--run` arm only, and no `--compile` arm at all. So s219, s220 and s221 each recorded a suite-wide
PASS that was m3-only while the contract they cited read "both". Nothing lied; the instrument simply
could not perform the clause it was cited for.

## 2. Why that gap was load-bearing rather than cosmetic
Mode 4 is where this tree's worst silent failure class lives. `pattern_match.c:737` records it in the
source: giving `g_cap_gen` hidden visibility cost **173/316 mode-4 LINK failures while mode 3 stayed
green**, because m3 bakes the address in-process and is *structurally incapable* of seeing the defect.
That comment also names an axis ARCH §7 step 0(c) does **not** document — hidden is reachable from a
`.S` *inside* the `.so` and unreachable from emitted code *outside* it, and those are two different
things.

Now look at what the ladder is about to run. RTX-11 edits `bb_match_release` and fires `.s` regen ×3.
`rt_dcap_end_ok_open` needs three `static`→`hidden` promotions. Both are exactly the change class
whose signature failure an m3-only kill-switch cannot detect. **The m4 arm is RTX-11's prerequisite,
so building it is not a detour around the port — it is the thing that makes the port gateable.**

## 3. The arm is cheap, and that was measured before it was written
`--compile` output is byte-identical at gate ON and OFF. Verified by `cmp` on a probe program *before*
any code was written. The reason is structural: `RTX_GATE` is a runtime `.byte` test inside the `.so`
(`rtx_abi.inc:83`) whose value is set by the `.so`'s own constructor (`rtx_init.c:24`), and an m4
binary links that same `.so`. So the arm compiles **once** per program and toggles only the runs.
Suite-wide both modes = **93 s**.

Had this been assumed rather than checked, the honest estimate would have been 2× compiles per
program and the arm would plausibly have been judged too expensive — the same correction as s218
item (3), where the "expensive" hard probe turned out to cost under a minute. **Twice now, a rung was
deferred on a cost model nobody measured.**

## 4. Falsification aimed at the NEW arm, because a gate that cannot fail is worthless
Hard `ud2` planted in the landed slice-7 asm ⇒ **m3 MOVER=9 AND m4 MOVER=9** over the capture suite,
every ON hash collapsing to the single SIGILL rc=132 hash. Reverted three ways: `grep ud2`==0, source
identical to HEAD, `.so` relinked **bit-identical** to baseline `e05ac2f1c192990a`.

## 5. Result: 316 programs, N=4, 93 s
| mode | IDENTICAL | QUARANTINE | MOVER | SKIP |
|---|---|---|---|---|
| m3 `--run` | 315 | 1 | **0** | — |
| m4 `--compile` | 312 | 1 | **0** | 3 |

GATE PASS. Watermark re-proven unchanged at session start: m3 **311/4/0**, m4 **311/2/2**, DIVERGE=**2**,
`140`/`141` red-m3/green-m4 ⇒ latch canary intact.

## 6. Three secondary facts
**(a) `160`'s non-determinism reproduces in m4**, and there its ON and OFF sets are the *same*
two-element set `{6a68d667,d7772c55}` ⇒ mode-independent, on the C path. This strengthens on a second,
independent axis the standing argument that the asm cannot be its cause. Its m3 membership this draw
was a **sixth distinct one in six sessions**: N=4 detects, it still does not characterise.

**(b) m4 SKIP=3 reconciles the crosscheck's SKIP=2.** `test_string` and `1017_arg_local` are the
crosscheck's two; the third is `coverage_sno_nodes`, which the crosscheck excludes upfront for having
no `.ref` and thereby **masks a genuine compile failure**. This gate needs no `.ref`, so it surfaced it.
⇒ **a program can be invisible to one instrument for a reason unrelated to the defect it carries.**

**(c) s221's item (6) is closed: the phantom edit never landed.** The script's history is exactly two
commits (s219 mint, s220 fix); the committed file carries both s220 fixes, zero `--compile`
occurrences and zero of the phantom prose. So the false "m4 arm verified s221" claim is absent from
origin and the arm was genuinely still owed. s221's suite-wide PASS **re-derived against the committed
instrument: 315/1/0, reproducing its numbers exactly** ⇒ that result stands despite the unaccountable
script state.

## 7. Two doc discrepancies, stated rather than smoothed
**(a)** My `.so` is `e05ac2f1c192990a`; s221's artifact of record is `ae2e0bca1e92efcd`. `make -q`
returns 0 against committed source, so this is most likely container/toolchain-dependent — but **I did
not reproduce s221's artifact and do not claim to.**
**(b)** The s221 cursor cites SCRIP `294a0464`, which **does not exist** (`git cat-file -e` fails);
HEAD was `7578378e`. A pre-rebase hash was recorded. ⇒ **RULES (a) needs a sibling: never write a
commit hash into a doc before the push that may rebase it.** Same structural impossibility as a
"PUSH PENDING" banner — a claim about an event later than the text.

## 8. Step 0 run on `rt_dcap_end_ok_open`, and it is BLOCKED — recorded so the next session does not re-walk it
(a) ✓ live at `pattern_match.c:696` · (b) ✓ spelling round-trips · (d) ✓ 43 static sites incl. the
graded workload · (e) ✓ not already asm (only a comment hit in `rtx_match.S`).
**(c) BLOCKS:** `g_dcf` `b`/static · `g_dcf_cap` `b`/static · `rt_dcap_pump` `t`/static — **and that
last one is the unconditional tail call in the hot path** · `rt_cas_carve` `t`/static. Needs three
`static`→`visibility("hidden")` promotions (s215 precedent), verified safe on the mode-4 axis (0
template refs, 0 emitted-`.s` refs; static→hidden cannot break emitted code because emitted code could
never reference a static).
**(f-pre):** four arms, not straight-line — trace / lazy-init / overflow / push+pump. Hot arm mutates
`g_dcf_top++` before the call ⇒ **bail-before-mutate applies**, or a delegation double-pushes a LIFO
that nests by design.
**Ceiling:** ~15 instrs × 8M ≈ **2%, below the ±3% floor**, and the hot path still ends in a C
`rt_dcap_pump` ⇒ **eradication only (RTX-12), never a speed number.**

## 8b. I COMMITTED THE VERY ERROR §7(b) DOCUMENTS — ONE COMMIT LATER
§7(b) above mints the rule "never write a commit hash into a doc before the push that may rebase it."
My own docs then pinned SCRIP `678cacb6`, and a **parallel session pushed mid-session** (`b38e31d8`,
RTX-24-ICN + s21x-e), so `git pull --rebase` rewrote it to `7b6719c1` and every pinned reference was
false the moment it was written. Corrected in the same session, but the lesson is the sharper one:
**writing a rule down does not exempt the author from it, and the rot re-appeared inside ten minutes
of being named.** ⇒ The durable form is to pin NO pre-push hash at all and let
`handoff_status.sh` supply it. ⚠ Also stale by the same push: my "13 family gates" — the parallel
session's `SCRIP_RTX_ICNSUB` makes it 14. **Re-derive, never inherit** (ARCH §5's own warning, now
demonstrated twice in one session).

## 9. Not run, not claimed
No asm landed ⇒ no watermark moved. Beauty still m3-BLOCKED at EMIT (gate-invariant). 15-demo board
not run. 3-arm rail deliberately not run — there is no port to grade. RTX unit batteries and smokes
**not** re-run: the change is script-only with zero codegen reach, and claiming them would be the
unmoved-battery false claim of s165/s187. Prolog/Icon/Snocone/Raku untouched.
