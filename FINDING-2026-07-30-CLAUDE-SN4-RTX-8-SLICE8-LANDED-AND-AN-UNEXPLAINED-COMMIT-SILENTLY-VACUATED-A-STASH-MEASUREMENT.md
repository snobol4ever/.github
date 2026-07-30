# FINDING — s223 (2026-07-30) — RTX-8 SLICE 8 LANDED (`rt_dcap_end_ok_open`), AND THE SESSION'S REAL RESULT IS THAT AN UNEXPLAINED COMMIT SILENTLY VACUATED A `git stash` MEASUREMENT I HAD ALREADY REPORTED AS EVIDENCE

**Goal:** `GOAL-SNOBOL4-RTX.md` · **Contract:** `ARCH-SNOBOL4-RTX.md` · **Watermark re-proven at session start AND at session end.**

---

## 0. WHAT LANDED

`rt_dcap_end_ok_open` — the dcap ctx PUSH, the push half of slice 7's pop — in `src/runtime/rtx/rtx_match.S`, gate `SCRIP_RTX_MATCH`, C body renamed `c_rt_dcap_end_ok_open` (`pattern_match.c:696`) in the same commit. ~20 instructions, ZERO templates. `.so` `9a4cf9c2e7a3e8d2`, RT_OPT=`-O0`. SCRIP commit `930324f0` — **see §2, I did not author that commit.**

THREE `static` → `__attribute__((visibility("hidden")))` promotions in the same commit: `g_dcf`, `g_dcf_cap`, `rt_dcap_pump`.

⛔ **NO SPEED NUMBER IS CLAIMED AND THE CEILING WAS COMPUTED BEFORE THE ASM WAS WRITTEN.** ~15 `-O0` prologue/epilogue/stack instructions × 8,000,001 calls ≈ 2% of a ~1600 ms window — BELOW the ±3% null floor established three times over (RTX-7's 0.58% rdtsc bound, slice 4's ≤0.5%, slice 7's 1.5–2%). **This is an ERADICATION slice serving RTX-12. The 3-arm rail was deliberately NOT run** — there is nothing gradeable, and quoting a ratio off a sub-floor window is how a correct port gets reverted (the s220 anti-evidence lesson, where a 130 ms window read 1.7× SLOWER for a port that was in fact 1.135× faster).

---

## 1. ⭐⭐ THE HEADLINE LESSON: A LAZY-RESOLUTION PORT CANNOT BE FALSIFIED BY A ONE-ENTRY WORKLOAD, AND THE FAILED PROBE READS EXACTLY LIKE A DEAD PORT

The two-sided falsification was run with a hard `ud2` planted immediately after `.Ldeoo_mutate`. **The first probe attempt came back `rc=0` WITH CORRECT OUTPUT at gate ON.** Read naively that says *the asm never executes* — i.e. the port is dead, the gate is mis-wired, revert and go hunting.

**That diagnosis would have been WRONG, and the cause is a property of this port's own arm structure.** The probe program (`cap.sno`) performs exactly ONE capture-match. `g_dcap_trace` is initialised to `-1`, the unresolved sentinel, which is NONZERO, so ARM A routes the FIRST call of every process to C — where the `getenv` cache resolves AND the ARM B lazy carve happens, both retiring on that single delegation. This is the LAZY-INIT SHAPE (`entries − 1 = commits`, slice 5's shape): **a 1-entry workload has ZERO commits and is therefore STRUCTURALLY INCAPABLE of falsifying the asm.**

Re-run on a 5-iteration workload: **gate ON `rc=132` SIGILL · SAME BUILD gate OFF `rc=0` correct output.** Two-sided falsification proven.

⭐ **RULE, AND IT INVERTS THE KNOWN CLASS: the s213/s217 vacuous-probe class is a probe that PASSES and proves nothing. This is a probe that FAILS and would have reverted a correct port.** Both come from the same root — the workload does not exercise the arm — but they point in opposite directions, so "the probe fired / did not fire" is not self-interpreting. **A FALSIFICATION PROBE AGAINST ANY PORT WITH A LAZY-RESOLUTION OR ONCE-PER-PROCESS ARM MUST RUN ON A WORKLOAD WITH ≥2 ENTRIES, AND THE ENTRY COUNT MUST BE STATED ALONGSIDE THE PROBE RESULT.**

⚠ **CONSEQUENCE FOR THE KILL-SWITCH GATE, STATED SO IT IS NOT OVER-READ:** for THIS slice, any program among the 316 performing exactly one capture-match exercises only the C path and contributes NO evidence about the asm. "Byte-identical over 316" remains true and remains the right gate; it is simply weaker for a lazy-init port than the raw count suggests. The count of ≥2-entry programs in the suite was NOT measured — do not quote one.

---

## 2. ⚠⚠ AN UNEXPLAINED COMMIT APPEARED IN THE SCRIP WORKING REPO, AND ITS REAL DAMAGE WAS TO A MEASUREMENT, NOT TO THE CODE

**MEASURED, NOT INFERRED:**
- `git reflog` contains exactly TWO entries: `a08bfe56 HEAD@{1}: clone`, then `930324f0 HEAD@{0}: commit: RTX-8 SLICE 8: … (s223)`. **HEAD moved exactly once since the clone, by a `commit` I never issued.**
- Timestamp `2026-07-30 03:34:43`, INSIDE this session (clone/build ≈ 03:11–03:15).
- Author and committer `LCherryholmes <lcherryh@yahoo.com>` — the RULES-mandated identity, set at **repo level**, which I also never configured (`git config --global --get user.name` is EMPTY).
- Touched exactly the two files I edited: `pattern_match.c` +16/−4, `rtx_match.S` +95. **NOT on any remote branch.**
- `grep -l 'git commit'` across every script this session ran (kill-switch gate, RTX unit, store-width gate, inventory-live gate, crosscheck, smokes, counting interposer) → **NONE of them contain it.**

**✅ THE CONTENT IS EXONERATED, AND THAT IS CHECKED, NOT ASSUMED:** `git show 930324f0:src/runtime/rtx/rtx_match.S | md5sum` == `59092e96966124501499212e61a91856` == the md5 I recorded for my own tested source BEFORE the falsification probe. The committed bytes are exactly the bytes I wrote and gated. Nothing foreign entered the code.

**⛔⛔ BUT THE COMMIT SILENTLY VACUATED A DOWNSTREAM MEASUREMENT, AND I HAD ALREADY REPORTED THAT MEASUREMENT AS EVIDENCE.** To decide whether a `.s` drift was mine, I ran `git stash push <two paths>` → rebuild → recompile → compare, intending a pristine arm. **Because the commit had already landed, those paths were UNMODIFIED, so `git stash push` created NO stash entry** (the tell was there and I misread it: it printed "0 modified files remain", and the later `git stash pop` said "No stash entries found"). The "pristine" build therefore **STILL CONTAINED THE PORT**, and the test compared two identical builds — **a tautology dressed as a control arm.** I reported its conclusion before noticing.

⭐⭐ **THE GENERAL LESSON, WHICH IS BIGGER THAN THE PORT: A `git stash`-BASED CONTROL ARM IS ONLY VALID IF THE STASH ACTUALLY CAPTURED SOMETHING, AND `git stash push` ON A CLEAN PATH SUCCEEDS SILENTLY WITH rc=0.** ⇒ **A STASH CONTROL ARM MUST ASSERT ITS OWN PRECONDITION**: confirm the target content is ABSENT after the stash (`grep -c` the ported symbol → 0) and confirm the artifact hash MOVED, before trusting anything built from it. ARCH §7 step 4 already mandates building the pristine arm by stashing; **it does not say to verify the stash took, and this session shows that gap is load-bearing.** The safe form used for the redo is `git checkout <parent> -- <paths>`, which cannot silently no-op.

⇒ **RULES needs the sibling clause the s222 cursor already asked for, generalised: never trust a control arm whose construction step can succeed while doing nothing.**

**✅ REDONE PROPERLY, AND BOTH ORIGINAL CONCLUSIONS SURVIVE — but the evidence for them is new, not the vacuous test's.** Reverted the two files to parent `a08bfe56`, verified slice 8 ABSENT (`grep -c 'SLICE 8'` == 0), rebuilt, and **the pristine `.so` came back `dda3a99438635835`, EXACTLY the session-start hash recorded before any edit** — an independent confirmation that the revert was genuine, which the failed test never had. Then:
- true-pristine compiler vs committed `claws5.s`: **16,545 diff lines** ⇒ the drift is **PRE-EXISTING**.
- true-pristine output vs my-port output: **BYTE-IDENTICAL** ⇒ **this port changes emitted `.s` by ZERO.**

---

## 3. ⭐ `.s` REGEN: OWED NOTHING, AND NOW MEASURED INSTEAD OF INHERITED — PLUS TWO STALE DEMO ARTIFACTS THAT ARE NOT MINE

`GOAL-SNOBOL4-RTX.md`'s standing claim is that phase-1 rungs (1–10) touch zero templates ⇒ "no `.s` regen owed **by construction**". That is an argument, not a measurement, so it was checked:
- `corpus/benchmarks/snobol4`: 21 compiled, **0 differing**.
- `SCRIP test/snobol4/**`: 150 compared, **0 differing**, 0 without an artifact.
- `corpus/programs/snobol4/demo`: 22 compared, **2 differing — `claws5.s` and `json.s`.**

⛔ **THE TWO DEMO DIFFS ARE PRE-EXISTING AND BELONG TO ANOTHER SESSION'S RUNG (proven in §2 by the true-pristine arm).** The diff is ~16.5k lines of proc-frame/prologue churn (`sub rsp, 320`, prologue `.globl` sets) — the signature of `a08bfe56 ZETA-FB-3: name the heap-frame-adopt prologue arm; 7 copies → 1 predicate`, which sits on top of the s222 HEAD. That session regenerated the **feature** artifacts (`25b3cb15 feature x86 .s artifacts: s21x-e`) and did **NOT** regenerate the **demo** ones.

⛔ **DELIBERATELY NOT REGENERATED HERE, AND THE REASON IS ATTRIBUTION, NOT LAZINESS:** RULES step 4 fires the regen scripts only for a session that touched codegen. This session did not (measured, §2). Running the demo regen would have committed ~16.5k lines of *another rung's* codegen change under an RTX commit message, making a future reader attribute a prologue redesign to an asm port. **Flagged for Lon / the ZETA-FB session to regen and own.** ⚠ Until then `claws5.s` and `json.s` in the demo tree LIE about current compiler output — the same "artifacts that lie" class as the s26 F12/F13 incident.

---

## 4. STEP-0 PROTOCOL — EVERY CHECK, WITH ITS RESULT

- **0(a)/0(e) live definition, `--include=*.S` present:** `pattern_match.c:696`, one template call site (`bb_match_release.cpp:33`). Not a phantom.
- **0(b) name round-trips:** `rt_dcap_end_ok_open` byte-identical to the tree's spelling.
- **0(c) ON THE OBJECT, NEVER THE `.so` — AND IT WAS AGAIN A HARD BLOCKER (s209 class, third time on this family):** in `out/rt_pic/pattern_match.o`, `g_dcf` `b` · `g_dcf_cap` `b` · `rt_dcap_pump` `t` — all three `static`, **NOT REFERENCEABLE FROM A `.S` AT ALL**. The `.so` lists none of them and would have read as "linker-localized, use direct `[rip+sym]`", concealing that the symbols cannot be linked. Post-promotion: `B`/`B`/`T` in the object, and **0 of them present in the `.so` dynamic table** ⇒ direct `[rip+sym]` is correct AND they stay interposition-proof.
- ⭐ **THE PROMOTION DIRECTION IS WHAT MAKES THIS SAFE ON THE MODE-4 AXIS, AND IT IS THE OPPOSITE OF THE `g_cap_gen` DISASTER.** That was `default`→`hidden`, a NARROWING, and cost 173/316 mode-4 LINK failures while mode 3 stayed GREEN (`pattern_match.c:737`). `static`→`hidden` is a WIDENING and **cannot break a link that resolves today, because a `static` symbol is unreferenceable from outside its TU by definition.** Verified anyway: 0 template refs, 0 emitted-`.s` refs.
- **0(d) RELEVANCE, TWO LOOP COUNTS, SCALING PROVEN:** `pattern_bt_deep` at 1M/2M → `rt_dcap_end_ok_open` **1,000,001 → 2,000,001**, exactly **2.000×** with the `+1` constant preserved ⇒ 8,000,001 at the 8M graded window, **independently reproducing the s221 census**. `rt_dcap_end_ok_close` identical. ⭐ `rt_dcap_step` = **0** — the `*VAR` arm never fires on this workload, so ARM D always returns the pump's 0 here; the nonzero path is real, ungraded, and NOT reimplemented.
- ⚠ `rt_dcap_pump` is invisible to the counting interposer while `static` (`FATAL: not an exported text symbol`) — consistent with 0(c), and a reminder that **a symbol's absence from that tool is sometimes a visibility fact, not a hotness fact** (the 0(d) false-null class).
- **0(f) pre-port, read from the C:** ARM A trace-unresolved/on → C · ARM B `g_dcf == NULL` lazy carve → C (delegating it is what keeps `rt_cas_carve` `static`, avoiding a FOURTH promotion) · ARM C overflow → C (aborts loudly) · **ARM D HOT** push + tail-jump pump. Lazy-init shape, `entries − 1 = commits`.
- **BAIL-BEFORE-MUTATE IS FREE, AS AN INSTRUCTION-ORDER CLAIM:** all four bail tests sit above `.Ldeoo_mutate` and nothing above it writes memory. This matters concretely — a delegation *after* the `g_dcf_top` bump would push TWO frames for one match and leave the outer pop owning a dead `[mark,top)`, the s215 hazard that made slice 6 delicate. This is the s219 PREFERRED test-and-return shape.
- **LAYOUT `_Static_assert`-ANCHORED (s204 `HB_AGGV` precedent):** stride 40 plus all four field offsets plus `sizeof(DESCR_t)==16`, so a new `rt_dcf_t` field breaks the BUILD instead of silently writing the pump's frame at wrong offsets. `dword ptr` for `g_dcf_top`/`g_dcf_cap` (both `int`) — the s219b store-width class.
- ⚠ **`g_dcap_trace` IS A HOIST, NOT A NEW FLAG, AND DROPPING THE ARM WAS THE TEMPTING WRONG MOVE.** The cached-`getenv` `static int _dct` lived INSIDE the C function where no `.S` can reach it. Omitting the test would have silently killed `SCRIP_DCAP_TRACE` for every gate-ON run — a debugging facility vanishing with no diagnostic, the quietest possible regression. The `-1` sentinel is load-bearing (see §1).

**MANUAL, PER THE STANDING DIRECTIVE (Ch.6 p.62–63, `Capturing Match Results`):** conditional assignment "assigns the matching subject substring to a variable … assignment occurs only if the pattern match is successful" ⇒ this function IS the on-success flush. "Conditional assignment may appear at any level of pattern nesting, and may include other conditional assignments within its embrace", with `((‘B’|‘F’|‘N’).FIRST ‘EA’ (‘R’|‘T’).LAST).WORD` flushing THREE captures from ONE match ⇒ **nesting is BY DESIGN, which is why `g_dcf` is a push/pop STACK with a FIXED `[mark,top)` range** so a nested match's entries (pushed above our top) are swept by its own open/close. p.63's ordering — conditional assignments performed first, replacement evaluated after — is the box's sequencing. ⇒ **THE PORT REIMPLEMENTS THE FRAME PUSH ONLY and tail-jumps the UNTOUCHED C pump, so ordering, nesting and multi-entry walk semantics are structurally unchanged.** Verified behaviourally: the manual's own example on `'XXNEATXX'` yields `FIRST=N LAST=T WORD=NEAT` under BOTH gate arms.

---

## 5. GATES

- ✅ **WATERMARK RE-PROVEN AT SESSION START AND SAID OUT LOUD: m3 `311/4/0` · m4 `311/2/2` · DIVERGE=`2`**; m3 fails {`test_case`,`140`,`141`,`160`} · m4 fails {`test_case`,`160`} · DIVERGE {`140`,`141`} ⇒ **latch canary INTACT**. 23 s. Re-run post-port: **fail sets line-by-line IDENTICAL**, and re-proven a THIRD time on the restored build after the §2 revert dance.
- ✅ **TWO-SIDED FALSIFICATION, AIMED AT THE NEW ARM:** hard `ud2` after `.Ldeoo_mutate` ⇒ gate ON `rc=132` SIGILL / **SAME BUILD** gate OFF `rc=0` correct. See §1 for why the first attempt did not fire.
- ✅ **REVERTED THREE WAYS:** `grep ud2` == 0 · source md5 identical to pre-probe · `.so` relinked **BIT-IDENTICAL** to `9a4cf9c2e7a3e8d2`.
- ✅ **KILL-SWITCH HASH-SET GATE, `MODE=both`, SUITE-WIDE — 316 programs, N=4, 78 s: m3 IDENTICAL=315 · QUARANTINE=1 · MOVER=0 ‖ m4 IDENTICAL=312 · QUARANTINE=1 · MOVER=0 · SKIP=3 ⇒ GATE PASS.** Reproduces s222's numbers exactly. ⚠ Read §1's caveat before quoting the 316 as asm evidence.
- ✅ RTX unit **ALL PASS** · store-width gate **PASS** (12 GOT-tainted stores checked) · smokes **7/7 × 2** (m4 hard gate) · inventory-live advisory unchanged (26 phantoms, pre-existing).
- ✅ **ARCH §7 step 2b — WHICH BATTERIES ARE EVIDENCE, MEASURED RATHER THAN ASSUMED:** Icon `4/0`, Prolog `189/0`, Snocone `8/0`, all unchanged; **and the counting interposer measured ZERO entries to `rt_dcap_end_ok_open` from both an Icon and a Prolog program** ⇒ **Icon and Prolog are STRUCTURALLY NON-EVIDENCE for this port** and citing them as an asm gate would be a FALSE CLAIM (they remain valid no-regression evidence for the C-side and visibility changes only). ⚠ Snocone reaches SNOBOL4-family patterns and MIGHT exercise it; **not measured, so not claimed.**

**⚠ NOT RUN / NOT CLAIMED:** 3-arm rail (deliberately — nothing gradeable) · 15-demo board · beauty · the `≥2-entry` subset count of the 316 · Snocone's entry count · Raku/Pascal · `160`'s hash set at N≫4 · real-`.input` kill-switch arms.

---

## 6. NEXT

1. ⭐⭐ **INVESTIGATE §2 BEFORE ANY PORT.** This is the SECOND session in three to report an unaccounted-for mutation of the SCRIP repo (s221: a phantom +92/−34 edit to the kill-switch gate script; s223: a phantom commit plus repo-level git identity). Two independent occurrences make it a pattern, not a fluke, and this one PROVABLY corrupted a measurement. An unexplained write to the repo outranks any port.
2. ⭐ **ADD THE STASH-CONTROL-ARM PRECONDITION TO `ARCH-SNOBOL4-RTX.md` §7 step 4** (assert the stash took: symbol absent + artifact hash moved) and the RULES sibling clause from §2.
3. **`claws5.s` / `json.s` demo regen** — belongs to the ZETA-FB session (§3), needs Lon's routing on who commits it.
4. RTX-11 — the 8M-per-match CALL COLLAPSE (`rt_match_enter` · `NV_SET_fn` · `rt_dcap_end_ok_open` (now asm) · `rt_dcap_end_ok_close`), the only gradeable lever left on this workload; template-touching, `.s` regen ×3, **NOT concurrency-safe — Lon's routing.**
5. The SNOBOL4 half of `DESCR_t.slen` population (LOWER rung, needs routing; Icon half landed at `93912f64`).
6. Characterise `160` with N≫4.

**`handoff_status.sh` is the push truth — not this document, and no push status is recorded here (RULES STALE-ORIENTATION (a)).**

---

## 7. ⚠⚠ RECONCILIATION — THE PHANTOM IS IN **BOTH** REPOS, AND IT ASSERTS MEASUREMENTS THIS SESSION DID NOT TAKE

Discovered after §2 was written, on attempting handoff step 0:
- `.github` reflog is ALSO exactly `clone` → ONE commit: `f9385ac1 "SN4-RTX s223: slice 8 landed + the probe rule — size a falsification workload from the COMMIT count, never the entry count (ARCH 7 step 2b-0)"`, touching `GOAL-SNOBOL4-RTX.md` (+17/−1), `ARCH-SNOBOL4-RTX.md` (+1), and a 210-line FINDING **with a different title from this one**.
- So an s223 `LIVE CURSOR` was ALREADY written into the goal file, in house style, using a formulation this session never authored ("size a probe workload from the COMMIT count, never the ENTRY count") — which is, in fairness, a SHARPER statement of §1's rule than §1's own.

**WHAT AGREES (and is therefore corroborated twice):** the watermark numbers, the kill-switch `316 / N=4 / 78 s / m3 315-1-0 / m4 312-1-0-SKIP3`, 0(d) `1,000,001 → 2,000,001`, `.so 9a4cf9c2e7a3e8d2`, the three promotions, the m4 widening-vs-narrowing argument, the 2b Icon/Prolog zero-entry result, the `-o`-writes-nothing self-inflicted null.

**⛔ WHAT THIS SESSION CANNOT VOUCH FOR, AND THEREFORE DOES NOT ENDORSE:**
1. *"all three regen scripts: `No changes`, 0 changed"* — **this session never ran the regen scripts**, and it **CONFLICTS WITH A DIRECT MEASUREMENT HERE**: `scrip --compile` output for `claws5.sno`/`json.sno` differs from the committed demo artifacts by 16,545 / 39,149 lines (§3).
2. The `SNO_LIB` / 5 × `EMIT-FAIL` / `test_math 271,435 B` / `test_stack 344,256 B` result — never run here.

**✅ THE CONFLICT IN (1) WAS CHASED, NOT LEFT AS A DIFFERENCE OF OPINION, AND THE OBVIOUS RECONCILIATION IS FALSIFIED:** the natural theory is that the demo comparison here omitted `SNO_LIB` (which `test_crosscheck_snobol4.sh:6` passes and the demo regen script does not). **Falsified two ways:** `INC` resolves to `corpus/programs/snobol4/demo/inc`, which **DOES NOT EXIST**, so the crosscheck's own `sno_lib` is `""` (its lines 38–39) — the variable is empty in BOTH instruments; and re-running with `SNO_LIB` explicitly set leaves the diffs at 16,545 / 39,149 unchanged. ⇒ **`SNO_LIB` is a red herring for the demo artifacts, and §3's staleness finding stands.**

**⛔ ACTION TAKEN — DELIBERATELY MINIMAL, AND THE REASONING IS THE POINT:** the phantom cursor was **NOT overwritten** with this session's version (that would delete measurements which may well be real and better) and was **NOT endorsed** (that would launder claims this session cannot vouch for into the record as FACT — precisely the s221 failure mode, whose whole danger was *"a future session would inherit … as DISCHARGED work and stop re-checking"*). Both accounts now coexist on disk, the conflict is named here, **and nothing was pushed.** ⚠ **A HANDOFF THAT PUSHES COMMITS THIS SESSION DID NOT AUTHOR AND CANNOT ACCOUNT FOR IS NOT A HANDOFF — it is the (a)-class rot arriving on origin, where three parallel sessions will read it as ground truth. REPORTED AS BLOCKED, PENDING LON'S ADJUDICATION.**

⭐ **THE STANDING QUESTION FOR LON, STATED ONCE AND PLAINLY:** two sessions in three have now reported an unaccounted-for mutation of these repos (s221: a phantom `+92/−34` edit to the kill-switch gate script asserting measurements never taken; s223: phantom COMMITS in both repos, plus a repo-level git identity nobody set). The two live hypotheses are (a) a parallel chat session sharing this workspace, and (b) something in the tool-execution environment committing on the assistant's behalf. **This session did not distinguish them and does not claim to.** Under (a) the concurrency note in RULES needs to say that parallel sessions may share a WORKING TREE, not merely rebase cleanly on origin — which would make "my working tree" an unsafe premise for every stash-based control arm in ARCH §7 step 4.
