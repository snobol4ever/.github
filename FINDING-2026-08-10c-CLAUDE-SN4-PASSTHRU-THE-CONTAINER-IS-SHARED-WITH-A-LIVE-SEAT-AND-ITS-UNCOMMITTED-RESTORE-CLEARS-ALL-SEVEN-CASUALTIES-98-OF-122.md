# FINDING 2026-08-10c — PASSTHRU s11: THE CONTAINER IS SHARED WITH A LIVE SEAT, AND ITS UNCOMMITTED WORK CLEARS ALL SEVEN CASUALTIES (98/122)

**Seat:** GOAL-PASSTHRU-RBP-ERAD, session 11 (Claude Opus 5).  **Code touched: ZERO.**  SCRIP and corpus carry no commits of mine and no edits of mine.

---

## §1 ⛔⭐⭐⭐ THE CONCURRENCY PROTOCOL'S UNSTATED CASE: TWO SEATS, ONE CONTAINER, ONE WORKING TREE

The protocol banner in `GOAL-PASSTHRU-RBP-ERAD.md` describes concurrency as *"other seats are pushing to origin WHILE your session runs"* — i.e. separate containers reconciled through origin, absorbed by `git pull --rebase`.  **That is not the only case, and it is not the case I opened into.**

Measured, this container, this session:

| evidence | value |
|---|---|
| `git status --porcelain` in `/home/claude/SCRIP` at my open | `M src/emitter/emit.cpp` · `M src/emitter/emit.h` · `M src/runtime/pattern_match.c` — **staged, uncommitted, not mine** |
| `/home/claude/pt_probe.sh` | present, mtime 19:56, **not written by me**; its header cites this goal file's s8 ENVIRONMENT TRAPS (a) |
| `out/rt_pic/*.o` (256 objects) | compiled 19:39:46 → 20:03:44 — **a full runtime build I did not start** |
| `/tmp/pt_pass.txt` `/tmp/pt_fail.txt` | a completed BY-SET probe run, mtime 19:58, **not mine** |
| `ps -eo pid,etimes,cmd` | no user processes at my open — the seat is idle between turns, not dead |

The three staged files are **precisely the zone this goal file marks NOT-CONCURRENCY-SAFE** (`emit.cpp` frame arms; `emit.h:630 emit_jmp_pin_rbp`; `pattern_match.c:624 g_blob_ctx`).  The `.github` landings `232f2850` / `2ee9f596` (MECH s36 / s36b, "fix-forward ratified", M-1b ZCTX-STACK rung) arrived at origin **during** my session and are the same work.  Conclusion: **the MECH seat is live in this container, mid-edit, and the PT-4 window is demonstrably occupied.**

### §1a THE LANDMINE THIS CREATES — `git add -A` IS UNSAFE UNDER A SHARED TREE

`RULES.md` handoff step 5 reads `git add -A && git commit` **each touched repo**.  Under a shared tree that command **sweeps another seat's uncommitted work into your commit, under your message**, and the victim seat discovers it only when their own `git status` comes back clean.  This is a strictly worse failure than the rebase-hash confusion s8/s9/s10 kept hitting, because it is silent and it *looks* like a normal handoff.

**Recommended amendment (Lon's call):** at handoff, commit **named paths only** (`git add <path> && git commit`), never `-A`, whenever `git status` shows modifications the session cannot account for — and check `git status` for foreign edits at session OPEN, not just at close.  A one-line open-time tripwire pays for itself: *if the tree is dirty and you did not dirty it, another seat is live; do not commit that repo and do not take a NOT-CONCURRENCY-SAFE window.*

### §1b THE SECOND-ORDER TRAP: THE BINARY YOU BUILD IS NOT HEAD

`make scrip` in a shared dirty tree compiles **HEAD + the other seat's staged diff**.  My `scrip` (20:06:41) links `out/libscrip_rt.so` (20:03:45) built from that mixed state.  Every number in §2 is therefore a measurement of **the in-flight state, not of HEAD and not of any commit that exists anywhere.**  A seat that did not check `git status` first would have recorded these as HEAD numbers and reported the defect fixed at a commit where it is not.  This is the STALE-BINARY BUILD-OK trap wearing new clothes: the build is fresh and honest, the *tree* is the thing that is not what the cursor says.

---

## §2 MEASURED: THE IN-FLIGHT WORK CLEARS ALL SEVEN CASUALTIES AND RESTORES THE 29

Same container, same runner (`pt_probe.sh`, the s8-trap-safe `$(cat ref)` vs `$(cmd)` semantics), mode 3.

**Probe suite — BY SET, A/B:**

| arm | PASS | FAIL |
|---|---|---|
| **A** — leftover run, mtime 19:58 (pre-staged state; provenance INFERRED, see caveat) | 26 | 11 |
| **B** — HEAD + staged in-flight edits (my build) | **33** | **4** |

**REPAIRED by B (7):** `dc_recur` · `mv_arbno_callcap` · `w_cap_ay` · `w_cap_group` · `w_cap_novowel` · `w_cap_stored` · `w_cap_xxay`.  **BROKEN by B: ZERO.**
Arm A's fail set is exactly s9/s10's **7 casualties + 4 pre-existing**; arm B's residue is the 4 pre-existing alone (`ab_freturn` rc=0 · `ab_nret_lvalue` rc=1 · `ab_redefine` rc=0 · `z4_arbno` rc=139).

**crosscheck/patterns (122) — mode 3, arm B:** **98 PASS / 24 FAIL** (rc breakdown: 15×rc=0 diff-only · 8×139 · 1×124).
Against this goal file's own recorded numbers: broken HEAD **68/54/6**, pre-D-1 **97/25/1**.  **The in-flight work restores the 29 and lands one program better than the pre-deletion baseline.**

⚠ **CAVEATS, stated so nobody over-claims this:**
1. **Arm A's provenance is inferred, not proven** — I did not build it and cannot attest which tree state produced it.  Its fail set matching s9/s10's recorded casualties exactly is strong corroboration, not proof.  A rigorous A/B needs both arms built by one seat.
2. **m4 NOT measured** — mode 4 is compile→gcc-link→**run the binary** (s8 trap (b)); `--compile` alone is void.  Still OWED, as it has been since s8.
3. **These numbers grade uncommitted work belonging to another seat.**  They are offered as evidence *for that seat and for Lon*, not as a PASSTHRU watermark.  Nothing here is a green rung and no ratchet moves.
4. The 15 `rc=0` failures in crosscheck are **output diffs, not crashes** — uncharacterized here, and not obviously in this goal's family.

---

## §3 SEMANTIC COLLISION, RESOLVED BY THE REBASING SESSION (protocol §CONCURRENCY): DEPTH vs BLOB-PRESENCE

The protocol requires a collision be *resolved by the rebasing session and noted, never silently dominated*.  Here it is.

- **PASSTHRU s10 (this file):** *"Frontier restated: every PAT$ blob on the pass-thru path fails — non-nested ⇒ hang, nested ⇒ SEGV."*  Correlation with blob presence 4/4; correlation with capture, none.
- **MECH s36 (`232f2850`, landed mid-session):** *"DEPTH not blob-presence is the DEL-T1 discriminator; s35 bisect VOIDED; repair is save-by-value."*

**These are reconcilable, and the manual adjudicates them.**  s10's own §7 self-correction is the hinge: `A_stored_nocap` **does not nest**, D-2's NON-NESTING precondition therefore holds for it, and it hangs anyway — s10 filed that as *"a second, unexplained defect."*  It is not a second defect if **"depth" means run-time backtrack depth, not syntactic nesting.**

SPITBOL manual, Ch.18 p.204–207 (Pattern Match Algorithm): on reaching any element with an alternative, the matcher **pushes the alternative and the subject cursor onto a stack**, and pops it on failure — the bead-diagram walk shows the stack holding `{0, LEN(3)}` then `{1, 'E'}` for a two-element pattern with no nesting whatsoever.  **Every alternative is a stack entry.**  Ch.9 p.123 makes the consequence explicit for patterns that recurse: heavily recursive patterns *"result in stack overflow"* because depth is consumed per alternative, and Ch.9 p.123 further records that SPITBOL applies **no Quickscan heuristics** — matching is exhaustive, so alternatives are not pruned away.

So a stored pattern containing `SPAN`/`BREAK`/alternation reaches **backtrack depth > 1 with zero syntactic nesting**, which is exactly the `A_stored_nocap` shape (s10: `VOWEL 'Y'` → 0 blobs and passes; every SPAN/BREAK/ARBNO/ANY/LEN variant → fails).  A **single process-global cell** (`g_blob_ctx`, `pattern_match.c:624`, whose stated soundness condition is *"NON-NESTING … so a single cell suffices"*) is clobbered by depth from ordinary alternation, not just by recursion.

**Resolution:** MECH's DEPTH framing is the more accurate discriminator and **subsumes** s10's blob-presence correlation — blob presence correlated 4/4 only because in that witness set every blob-bearing program also carried an alternative-bearing element.  s10's "second, unexplained defect" is **explained and closed by this reading**, and MECH's *save-by-value* repair is the shape the manual's pushdown semantics require.  **PASSTHRU concedes the framing to MECH; §2 above is the empirical corroboration.**  ⚠ This reconciliation is *analysis grounded in the manual plus the two cursors' own measurements* — it is not a runtime measurement of depth, and it should be treated as a strong hypothesis until MECH's M-1b POP-MODEL check either confirms or falsifies it.

---

## §4 WHAT THIS SEAT DID NOT DO, AND WHY

- **No code.** The repair lives in `emit.cpp`/`emit.h`/`pattern_match.c`; the zone is occupied by a live seat with staged edits, and this file's own banner makes PT-4 surgery NOT-CONCURRENCY-SAFE with Lon routing the window.  The window is not mine.
- **No regen ×3.** Mandated only when lower/emitter is touched; I touched neither.  Still owed by s8/s10 + the RTX-FUNC seat, still entangled with the §0 provenance question, still NOT-CONCURRENCY-SAFE.
- **No SCRIP or corpus commit.** SCRIP's dirty state is another seat's; committing it — by `-A` or otherwise — would steal their work.
- **No PLAN.md edit.** GOAL-PASSTHRU-RBP-ERAD remains absent from the Active Goals table (flagged by MECH's cursor and again at my open).  `RULES.md` handoff step 3 forbids editing the table on routine handoff, so this stays **Lon's call**: add it, or retract the goal.

---

## §5 ADDENDUM (same session, after the co-seat committed) — THE WORK IS NOW A REAL COMMIT, /tmp IS ALSO SHARED, AND m4 CHANGES THE VERDICT

### §5a The measured state is no longer uncommitted
The co-seat committed as SCRIP **`c4ef2176`** *"DEL-T1 REVERT (D-1+D-2+D-3): the delete landed ahead of its own prerequisite — restore the 30 programs, keep the destination."* Its diff is byte-for-byte the stat I measured (3 files, 32(+)/73(−)), and `out/libscrip_rt.so` never moved under my runs (mtime `20:03:45` throughout). **§2's numbers therefore attach to `c4ef2176`, not to a state that exists nowhere.** They also now stand as an *independent* reproduction: the co-seat measured probe 33/4 and crosscheck 98/24 separately and we agree to the digit.

### §5b `/tmp` IS SHARED TOO — AND THE GOAL'S OWN RUNNER HARDCODES IT
`pt_probe.sh` writes `/tmp/pt_pass.txt` and `/tmp/pt_fail.txt` with no seat namespace. The co-seat re-ran it mid-session and **overwrote my crosscheck m3 fail set** (mtime `20:14:57`, content = the 4-line probe set where mine had written 24). I caught it only because the resulting by-set diff was nonsense — probe program names on one side, crosscheck names on the other. **Had both sets come from the same corpus, the clobber would have been invisible and the diff entirely plausible.** The corrupted comparison was discarded; m3 was re-measured into `/tmp/s11_*` and reproduced 98/24 exactly. **Recommend seat-namespaced result paths (`${SEAT:-$$}`) and copying any `/tmp` evidence the instant it is produced.** §1's rule generalises: under a shared container, *nothing* outside your own repo checkout is private — not the tree, not the build outputs, not `/tmp`.

### §5c m4 MEASURED (owed since s8) — AND IT QUALIFIES THE RESTORATION CLAIM
Recipe copied verbatim from `scripts/test_broad_corpus_snobol4.sh` `compile_mode4` (lines 33–36): `--compile` → `gcc -c` → link → **run the binary**, because ENV-TRAP (b) voids any m4 column built from `--compile` alone. Runner: `/home/claude/pt_probe_m4.sh`. At `c4ef2176`:

| suite | m3 | m4 |
|---|---|---|
| probe (37) | 33 / 4 | **33 / 3 / 1 SKIP** — failing set identical to m3; `ab_nret_lvalue` SKIPs because `--compile` itself fails (m3 runs and fails rc=1) |
| crosscheck/patterns (122) | 98 / 24 | **93 / 29 / 0 SKIP** |

**Five MODE34-IDENTICAL violations, strictly one-directional — pass in m3, SIGSEGV(139) in m4, none in reverse:** `064_replace_multi_arm` · `121_pat_calc_op_dispatch` · `156_pat_cap_alt_abandon_pop` · `181_pat_arbno_defer_tail_stressors` · `182_pat_arbno_defer_windowed_leaf`. m4's failure set is a strict superset of m3's.

⭐ **The consequence that matters:** `121`, `181`, `182` are three of the six s7 net-negative programs the co-seat's cursor lists as restored. **They are restored in m3 only.** (`070`, `180`, `183` are clean in both.) The revert is still the right call and the restoration is real — but it is **not two-medium green**, and no watermark should be written as if it were.

⚠ **Attribution UNMEASURED.** Whether these five are pre-existing or introduced by the revert requires a pristine-parent (`a5533659`) build; I did not take one because a build contends for the single CPU with a live seat. **Do not read this as caused by `c4ef2176`.** Resolving it is the cheapest remaining step toward a defensible two-medium claim, and it is the first item I hand forward.

### §5d Correction to §2 of this finding
§2 compared **absolute counts across containers** ("restores the 29 and lands one better than pre-deletion") — exactly what s7's law forbids, since `599601e8` scored 258/253 in one container and 278/273 in another. The co-seat's phrasing is the correct one: the **set-level** claim transfers (every family s10 named broken now passes; `128` still fails as its own defect), the absolute delta is indicative only. §2's measurement stands; §2's phrasing of it does not.

### §5e The five are DETERMINISTIC, and the attribution question has a leading hypothesis already in this file
**Determinism:** all five reproduce `rc=139` identically on repeated passes (2×, same binary, same container). Not flake — this matters because this project has been burned by nondeterministic witnesses (`AB0` on recursion, the M4 watermark oscillating on a 151 flake), and a flaky signal would not have been safe to hand forward.

**Leading hypothesis — a PRE-EXISTING mode gap, not damage from the revert.** This goal file already records m3-vs-m4 gaps of the same magnitude, measured at **s7, before D-1 ever existed**, on broad-336 and in BOTH killswitch arms:
- default-ON: m3 **278**/58 · m4 **273**/57+6skip → **5-program gap**
- KS-OFF: m3 **284**/52 · m4 **278**/52 → **6-program gap**

My measured crosscheck gap is **exactly 5**, one-directional in the same sense (m4 strictly worse). Different corpus, so the sets are not comparable program-for-program — but the magnitude and the direction both match a gap that predates the deletion. Reinforcing it: `c4ef2176` is a *faithful* revert (it restores the deleted arms verbatim), so its emitter output should approximate pre-D-1, which is the regime s7 was measuring. **This does not discharge the attribution — a pristine-parent build still settles it — but it moves the burden: the null hypothesis should now be "long-standing m3/m4 gap," not "the revert broke five programs."** Whoever takes it needs one build of `a5533659` and one m4 crosscheck run.
