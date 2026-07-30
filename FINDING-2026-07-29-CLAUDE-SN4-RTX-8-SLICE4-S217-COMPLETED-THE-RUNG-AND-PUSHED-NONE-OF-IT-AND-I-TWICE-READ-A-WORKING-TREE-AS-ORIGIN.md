# FINDING — s218 (2026-07-29, Claude + Lon): **s217 COMPLETED RTX-8 SLICE 4 IN FULL — PORT, GATES, FINDING, CURSOR MOVE, ARCH EDIT — AND PUSHED NONE OF IT. AND I READ ITS UNCOMMITTED WORKING TREE AS `origin` TWICE, IN OPPOSITE DIRECTIONS, BEFORE MEASURING WHICH TREE I WAS IN.**

**Session:** s218 · **Ladder:** `GOAL-SNOBOL4-RTX.md` · **Rung:** RTX-8 slice 4 (`rt_match_ctx_restore`)
**Recovered:** SCRIP `e0e69923` → rebased onto `origin/main` as **`6c22955f`** · orphan preserved as tag **`orphan-s217-preserve`**
**Baseline `.so` md5** `9fd91f67b711e7e8124814d625631331` (= s217's post-port build, its FINDING agrees) · **`RT_OPT=-O0`** · reproduced bit-for-bit after two probe cycles.

---

## ⭐⭐ THE FINDING, PART 1: A COMPLETE, WELL-EXECUTED RUNG THAT EXISTED NOWHERE BUT ONE CONTAINER'S WORKING TREE

s217 did everything the protocol asks, and did it well: the asm, both-tier 0(c), a `ud2` two-sided falsification, a three-way revert proof, the per-program kill-switch md5 sweep, a new pre-port instrument (`util_rtx_count_syms.sh`), a FINDING, a cursor move, an ARCH §7 edit, and a *new rung split out on measurement*. **Its entire output was unpushed.** Measured with the project's own ground-truth instrument, not inferred:

```
$ bash scripts/handoff_status.sh
  .github [main]         DIRTY      local=42826c711 origin=42826c711
  SCRIP [main]           UNPUSHED   local=6c22955f7 origin=3feab736f
```

Inventory of s217's output as found, by tree location — **this is the part that matters**:

| artifact | state as found |
|---|---|
| `rtx_match.S` + `gen_runtime.c` port | **1 unpushed commit** `e0e69923` |
| its FINDING (`…KILLSWITCH-MD5-GATE-IS-BLIND…`) | **untracked file**, never `git add`-ed |
| `GOAL-SNOBOL4-RTX.md` cursor move + rung `- [x]` | **uncommitted working-tree modification** |
| `ARCH-SNOBOL4-RTX.md` §7 step-0 edit | **uncommitted working-tree modification** |
| on any remote | **NOTHING.** `git show origin/main:…rtx_match.S \| grep -c RTX_FUNC(rt_match_ctx_restore)` ⇒ **0**, at two fetches spanning this session (`26e38f9d`, `3feab736`). Origin's LIVE CURSOR is still **s216**. Origin's ARCH has **zero** mentions. |

⛔⛔ **HAD THIS CONTAINER RESET, ALL OF IT WOULD HAVE BEEN LOST — AND ORIGIN WOULD STILL HAVE READ "NEXT RUNG: `rt_match_ctx_restore`, PRE-FLIGHT DONE, WRITE ASM IMMEDIATELY."** The next session would have rebuilt the port, re-derived every gate, and re-written the FINDING, with no way to know it was the second time. That is the full cost of a missing push, and it is **strictly larger** than the (a)-class rot `RULES.md` already names: rule (a) protects against a doc that over-claims a push; **nothing protects against work that never claims anything at all.** RULES (b) ("THE HANDOFF MUST MOVE THE CURSOR") is the rule violated — s217 *wrote* the cursor move and never committed it, which is the same failure one layer out.

⭐ **THE RECOVERY DEPENDED ENTIRELY ON STEP 0(e), AND THE RUNG TEXT ARGUED AGAINST RUNNING IT.** The s216 cursor and its dedicated addendum `640b765c` say *"PRE-FLIGHT DONE, WRITE ASM IMMEDIATELY"*, *"0(f) SATISFIED BY CONSTRUCTION"*, *"0(c) discharged by precedent"*. Every one of those statements is **true**, and together they dissolve the reader's reason to run step 0 at all — while 0(e) is the one check whose entire purpose is to distrust the plan. ⇒ **RULE: A RUNG MAY STATE PRE-FLIGHT EVIDENCE; IT MAY NEVER STATE A CONCLUSION THAT AUTHORIZES SKIPPING A STEP-0 CHECK.** Step 0 is re-run by the session that writes the code, on the tree that session actually holds, or it was not run. ARCH §7 0(e) already warns that this family's failure mode is *duplicated work that succeeds*; this instance adds that the duplicate would also have been **unrecoverable and uncountable**.

---

## ⭐⭐ THE FINDING, PART 2 — MINE, AND IT COST MORE THAN THE FIRST: **I ASSERTED FACTS ABOUT `origin` WHILE READING A WORKING TREE THAT A CONCURRENT WRITER WAS MUTATING. TWICE. IN OPPOSITE DIRECTIONS.**

| # | what I asserted | how I got it | truth |
|---|---|---|---|
| 1 | "No FINDING exists anywhere; s217 left no doc." | `ls \| grep -i s217` on a `.github` clone **3 commits stale**, with no check for untracked files | FALSE — the FINDING was sitting in that very directory, untracked |
| 2 | "The FINDING is **on origin** claiming LANDED while the code is not — a doc asserting its own push." | after `git pull`, `grep 'LIVE CURSOR' GOAL-SNOBOL4-RTX.md` — **a bare file read**, which returned s217's *uncommitted* edit | FALSE — origin's cursor is still s216; the "LANDED" text was local-only, and my own `git stash pop` had handed it back to me |

Both errors have one cause: **a bare `grep`/`ls` on a path answers "what is in the working tree right now," which in a shared container is a question about a concurrent writer, not about the project.** I then reported the answer as if it were about the repository. The second error is worse than the first because I had *already been burned once* and still reached for a bare file read.

⇒ **RULE, AND IT IS THE OPERATIONAL FORM OF THE STALE-ORIENTATION RULE FOR CONCURRENT CONTAINERS: WHEN A CLAIM IS ABOUT THE PROJECT, NAME THE REF AND READ THROUGH GIT — `git show <ref>:<path>` — NEVER A BARE FILE READ.** Four distinct trees are in play (working, index, local `HEAD`, `origin/main`) and they disagreed on *this exact file* all session. Corollaries paid for here:
- **`git fetch` before any negative claim about origin.** "X does not exist" from a stale clone is not a measurement.
- **`git status --porcelain` before believing any file you did not write** — `??` and ` M` are the tells that separate "the project says" from "somebody's unsaved work says."
- ⚠ **`git stash -u` / `git stash pop` silently reintroduced another agent's uncommitted work into my tree, after which it was indistinguishable from committed content.** I stashed to pull cleanly and did not consider that the stash was not all mine.
- ⭐ **This is the ladder's own "BEFORE QUOTING ANY SWEEP, HAND-RUN ITS OWN FIRST FAILURE" (s214) at one level up: before quoting any *tree fact*, name the ref it came from.** s214 minted its rule after an ASCII-only `grep -oP` miscounted symbols; same shape — a read whose scope was narrower than the claim built on it.

**Recorded at length and unhedged because this project's findings are its instruments, and a defect in how a session reads the tree contaminates every fact it reports.** Three of my own instrument defects this session, all caught from measurement: the two above, plus an initial `.so`-provenance conclusion drawn from `mtime` before checking `git status` and `make -q`.

---

## ✅ WHAT s218 ADDS THAT s217 DID NOT DO — THREE MEASURED FACTS

s217's technical claims were **independently re-derived on this tree and all hold** (0(a) two template sites · 0(b) round-trips · 0(c) `Σ` `B`@0x0 + `Σlen` `B`@0x14 in `stmt_exec.o`, `g_cap_gen` `D`@0x0 in `pattern_match.o`, all three in the dynamic table, control `g_cap_gen_next` absent · 0(d) **250,001 → 500,001 = exactly 2.000×** · `ud2` ON ⇒ rc=132 / same build OFF ⇒ rc=0 · revert md5+grep+`git diff`, `.so` back to `9fd91f67…`). That is replication, not news. **The new material is:**

### 1. ⭐⭐ THE STEP-2b COVERAGE SWEEP s217 OWED — AND THIS PORT'S COVERAGE SET IS ~40× SLICE 2's
ARCH §7 step 2b requires running the falsification build across **every** battery, because "the probe also names the exact coverage set." s217 ran its `ud2` on `pattern_bt.sno` only. Run across the full suite, the probe is an exact coverage instrument — every SIGILL is a program that reaches the port:

| arm | baseline | probe build | ⇒ programs reaching the port |
|---|---|---|---|
| m3 | PASS=311 FAIL=4 | **PASS=153 FAIL=162** | **~158 of 315** |
| m4 | PASS=311 FAIL=2 | **PASS=149 FAIL=164** | **~162 of 313** |

⇒ **roughly HALF the SNOBOL4 corpus executes `rt_match_ctx_restore`**, against **4 of 315** for slice 2 — and every one of those programs is verdict-identical gate ON vs OFF. **This breadth is the strongest correctness evidence any MATCH slice carries, and it is the argument for landing.** ⚠ It is *not* a speed argument: `pattern_bt` self-times **`ms: 179`** vs `MIN_MS=800` ⇒ BOGUS-WINDOW, the RTX-0f class a fourth time. s217 correctly grades the slice as **eradication (RTX-12), not speed** — that refusal is why it survives audit.

### 2. ⭐⭐ A CORRECTNESS HAZARD IN THE PORT THAT s217's OWN COMMENT MISSED — AND IT IS THE SEVERE HALF OF THE CLASS IT NAMES
The header justifies its 4-byte stores via the benign case (*"an 8-byte store would clobber the adjacent global (`Σlen` sits at +0x14…)"*). Measured on the object, the `g_cap_gen` case is **worse and unmentioned** — s217 cites `g_cap_gen_next` only as a *visibility control* for 0(c) and never notices where it sits:

```
pattern_match.o:  0000000000000000 D g_cap_gen
                  0000000000000004 D g_cap_gen_next     <-- ADJACENT, +4
```

`g_cap_gen_next` is the **monotonic capture-generation well.** An 8-byte `mov qword ptr [r10], rdx` on `g_cap_gen` would silently overwrite the well with the high half of a generation id — corrupting generation *allocation* downstream of every nested match, with **no diagnostic at any stage**, and it would link fine and pass short tests. ⇒ **`mov dword ptr [r10], edx` is the entire correctness of the third store.** ⛔ **Nothing in the tree defends this adjacency: no `_Static_assert`, no offset anchor, no test.** Anything that later widens those stores, or reorders the two globals in `pattern_match.c`, breaks capture generation silently. Minted as a rung below.

### 3. ⭐⭐ THE §ENVIRONMENT FACTS COST MODEL IS WRONG FOR THE OPERATION EVERY RUNG PERFORMS — AND IT HAS BEEN SHAPING RUNG DESIGN
That block reads *"`scrip` links `libscrip_rt.so` ⇒ a bisect step is BOTH builds (~9 min)."* True for a **full** runtime rebuild (measured: **~8.5 min**, 248 objects, 1 core). But the operation an RTX rung actually performs — **edit one `.S`, reassemble, relink** — is **3 SECONDS**, and the **full both-modes 315-program crosscheck is 25 SECONDS**.
⇒ **A COMPLETE HARD-PROBE CYCLE — PLANT `ud2`, BUILD, RUN BOTH ARMS, REVERT, REBUILD, RE-VERIFY MD5 — COSTS UNDER A MINUTE. THE FULL 2b COVERAGE SWEEP COSTS ANOTHER 25 SECONDS.** The ladder has repeatedly treated probe rebuilds as expensive and reached for silent value-probes instead; s216 paid for exactly that ambiguity and minted the `ud2` preference in response. **The hard probe was never the expensive option.** ⇒ **hard-probe two-sided falsification AND the 2b coverage sweep should be DEFAULT at every rung**, not budgeted. Corrected in the goal file's §ENVIRONMENT FACTS.

---

## ⚠ NOT RUN / BLOCKED — STATED, NOT BURIED
- **beauty: BLOCKED, and not by this port.** `beauty.sno` m3 dies `[IBB] FATAL: mode-3 driver: emit_chain returned NULL — BB template(s) lack MEDIUM_BINARY arm`, rc=134, **identical with the gate OFF**, at **emit** time before any runtime call is reachable ⇒ gate-invariant, **cannot be evidence either way**. Milestone-1 identity (`abfd19a7…`) is unverifiable on this tree until that template gap closes. Pre-existing, logged, not chased.
- **15-demo board:** not run.
- **My kill-switch gate was WEAKER than s217's and I should not be credited with it:** I diffed the crosscheck *verdict log* (ON == OFF, md5 `345db6572f7d2bc245da63243bfccd24`, both modes). s217 md5'd **stdout+rc per program across all 316** and thereby found that **`160_pat_alt_inner_gen_resume` is NON-DETERMINISTIC**, making byte-identity unfalsifiable there — a defect my coarser instrument is structurally blind to. Its split-out rung (N≥4 hashes per arm, explicit non-determinism report) is the correct fix and stands.
- **Prolog 189/0/0 · Icon 4/0/0 · RTX unit ALL PASS (8426 cases, 0 mismatches)** — ⚠ Prolog/Icon are **no-regression evidence for the C-side rename ONLY**; they do not move under the probe and citing them as asm gates is the s165/s187 FALSE CLAIM.
- **Watermark re-proven: m3 311/4 · m4 311/2/2 · DIVERGE=2**, failure sets line-by-line identical to s215, **zero movers**; `140`/`141` still **red m3 / green m4** ⇒ the DEFER-LATCH rung's free two-sided canary is intact and unconsumed.

## ⚠ AN UNEXPLAINED WRITER IN THIS CONTAINER — NAMED, NOT HIDDEN
The runtime built itself 23:04→23:12 and `e0e69923` plus three doc edits appeared in my working tree at ~23:22. **I invoked none of it and will not invent an agent.** Artifact verified sound every available way (clean tree at the time of check · no tracked source newer than the `.so` · `make -q` rc=0 · independent rebuild reproduced the md5 exactly). ⇒ **`git log --oneline -1` at orientation is NOT STABLE in this container: this session's HEAD moved between the first `git log` and the first build.** Re-read `HEAD` and diff against `origin/main` immediately before committing. Recorded because an unexplained writer is precisely the condition that later gets mis-attributed to a real bug — the s188 "a plausible neighbouring anomaly absorbs the blame" class.

---

## VERDICT — **LAND ALL OF IT, AND CREDIT s217 FOR THE RUNG.**

The port is well-formed, ABI-conformant (`r10` is in the documented RTX working set; blob pins untouched; gate `cmp`/`je` before any store ⇒ bail-before-mutate trivially satisfied; `endbr64` planted; `@GOTPCREL` correct per s214), arm-proven (**500,001 entries · 0 bailed · 500,001 commits**), two-sided falsified, watermark-neutral, and now **coverage-proven across ~half the corpus**. It needs no code change. **It needed its push**, and s218's contribution is that push plus the three facts above.

s217's FINDING, cursor move and ARCH edit are committed **as s217 wrote them**, with this document layered on top — not overwritten. Its split-out kill-switch rung is preserved intact.

**NEXT RUNG:**
1. **RTX-0f longer-window defer benchmark** — still blocks every MATCH ratio, and now cheap (3 s rebuild / 25 s crosscheck). `pattern_bt` reads 179 ms at `LT(N,500000)` ⇒ **~4.5× the literal** is the arithmetic-first estimate for the 800 ms floor; verify at two counts and **predict the checksum in advance** per RTX-0c/0d.
2. **FIX THE KILL-SWITCH BYTE-IDENTITY GATE** (s217's split-out rung): N≥4 hashes per arm, compare the SET, report non-determinism explicitly. `160` is the known instance.
3. **THE DEFER LATCH FIX** — graded on `140`/`141`, confirmed red-m3/green-m4 this session, never on json. Correctness rung; must never quote a speed number.
4. **RTX-8 remaining MATCH sinks** — NOT `rt_match_enter` first (multi-arm, call-heavy). Run the arm census on the grading workload **before** choosing; mandatory by 0(f).
5. ⭐ **NEW: `_Static_assert` the `g_cap_gen` / `g_cap_gen_next` adjacency** (and the `Σ`/`Σlen` pair) so a widened store or a reordered declaration fails the build instead of corrupting capture generation silently.
6. **`rtx_abi.inc` lines 10-15 stale r12 pin** — still uncorrected since s215; ARCH §2 has said "r12 is FREE — NOT A PIN" since s205. Not triggered this session (this port uses `r10`). ⛔ It sits inside the *executable* half of the contract, where an asm author will trust it.

**⚠ `scripts/handoff_status.sh` is the push truth — not this block.**
