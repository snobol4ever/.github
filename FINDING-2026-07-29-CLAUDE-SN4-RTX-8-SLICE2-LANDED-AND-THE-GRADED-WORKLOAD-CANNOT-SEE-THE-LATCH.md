# FINDING — s215 (2026-07-29): RTX-8 SLICE 2 LANDED. THE ARM CENSUS PICKED THE TARGET, AND IT ALSO PROVED THE RUNG'S OWN LATCH CLAUSE UNGRADEABLE ON THE GRADED WORKLOAD.

**SCRIP `0410aa72`. RT_OPT=`-O0`. Gate `SCRIP_RTX_MATCH` (slice 1's, reused).**

---

## 1. WHAT LANDED

`rt_defer_open` (plain arm) and `rt_defer_close` (DT_S/DT_SNUL arm) in `src/runtime/rtx/rtx_match.S`, C bodies renamed `c_*` in the same commit. Plus the step-0(c) prerequisite (four globals promoted off `static`) and a new instrument.

## 2. ⭐⭐ THE INSTRUMENT IS THE FINDING: A CALL COUNT CANNOT NAME AN ARM, AND s214's CENSUS ONLY COUNTS CALLS

s214 discharged 0(d) for this family and its numbers are correct. They are also **insufficient**, and the gap is exactly s212's WRONG-TEMPLATE-ARM lesson one level down: `rt_defer_open` has **four** arms (NULL · `'*'` star · `"FAIL"` · plain NV_GET) and a per-symbol call count cannot distinguish them. Committed `scripts/util_rtx_defer_arm_census.c` splits the traffic by the same predicates the C body branches on, in the same order.

**MEASURED, json.sno + twitter.json (631 KB), mode 3:**
```
open:  plain=402121   star=0   fail=0   null=0   ival_nonzero=0
close=402121 (exactly balanced with open)        step=0
close arms: fail=363155 (90.3%)  advance-by-1=38966  adv0=0  adv2-8=0  adv>8=0
get_pat_fn: star=0  plain=29573  ->  fn=29573  null=0   (100% hit, so those sites never reach open)
```

Three results, each load-bearing:

**(a) The hot arm is the plain arm.** Had I ported the star path — the one the rung's own text spends its warning budget on — the port would have graded a **guaranteed 1.000×** and the probe would have come back SILENT. That is precisely the batch s213 lost. **Static rank chose s213's batch; a call count would not have saved this rung either. Only an ARM count did.**

**(b) `ival_flag` is provably 0 on every call**, matching `bb_match_defer`'s `xor esi, esi` at both sites. Read from the tree AND confirmed dynamically, because §5-caveat-(a) reasoning from emitted text alone is what this ladder keeps getting burned by.

**(c) `close`'s hot work is a ONE-BYTE compare, and 90.3% of it FAILS.** C reaches that single byte through a `strncmp@PLT` call inside an `-O0` frame that also carries a 40-byte `char nb[40]` scratch buffer it never touches on this arm. That is the whole target: 402,121 × (one PLT call + one unused stack buffer + `-O0` ceremony) to compare one character.

**`rt_defer_step` re-confirmed DEAD:** 432 static sites tree-wide, 82 in `json.s`, **zero dynamic calls**. Re-measured rather than cited, per the s210 STALE-CENSUS rule. The #2 symbol by static count on the unported board remains cold.

## 3. ⛔⛔ THE RUNG'S LATCH CLAUSE IS UNGRADEABLE BY THE RUNG'S OWN BENCHMARK — AND THE TWO DELIVERABLES MUST STAY APART

The rung requires this rung to **fix** `rt_defer_get_pat_fn`'s one-entry latch (`g_star_peek`, the s161 EVAL/deferred slot collision), not transliterate it. But `g_star_peek` serves **only** the star path, and the star path measures **star=0 of 402,121 opens** on the workload the same rung designates for grading. So:

- the latch fix **cannot** be graded by json.sno/twitter.json — it would show 1.000× by construction;
- the port **cannot** be graded by the latch's canaries (`140`/`141`), which are pure correctness.

⭐ **Bundling them would let a correctness fix borrow a speed number and a speed port borrow a correctness gate — the same category error as citing an unmoved Prolog battery as asm evidence (s187).** They are therefore split: this commit is the port; the latch fix keeps its own already-red canaries and its own rung. **A rung clause can be internally inconsistent even when every fact inside it is true.**

⭐ AND THE MANUAL EXPLAINS *WHY* THE LATCH IS STRUCTURALLY WRONG, NOT MERELY EMPIRICALLY BUGGY. Ch.7 p.86: the `*` operator constructs the pattern once and **fetches the then-current value when the pattern is later referenced in a match**; deferred evaluation is legal on a pattern's alternate or subsequent clause, or on the whole pattern. Ch.9 p.122–123: a deferred value may itself be a pattern, SPITBOL **saves information on a stack during the match**, and recursion that consumes no subject characters produces a recursive plunge. ⇒ **a deferred evaluation can re-enter deferred evaluation, so a ONE-ENTRY latch keyed by name is guaranteed to be clobbered by a nested reference before the outer one consumes it.** The nesting is by design, not an edge case — which is also why `g_dfx` is a LIFO and why open/close measure exactly balanced.

## 4. ⛔ NO SPEED NUMBER. THE WINDOW IS 176 ms AND THE HARNESS'S OWN FLOOR IS 800 ms

`json.sno` self-times its match window at **176 ms** on twitter.json. `MIN_MS=800` (RTX-0b) suppresses any ratio below that as `BOGUS-WINDOW`. **Quoting 176 ms as a board would be the RTX-0b/0c/0d mistake for the fourth time, and the rung's own designated benchmark is the thing that is too short.** ⇒ **OWED, AND IT IS THE NEXT RUNG: a longer-window defer benchmark** (an RTX-0-class instrument rung), built to the RTX-0c/0d requirements — self-timed `ms:` ≥ 800, one scalable `LT(VAR,≥1000)` literal, deterministic checksum **predicted in advance**, 0(d) count proven to SCALE at two loop counts, and the count must track STRUCTURE (citm is 2.7× the bytes and makes FEWER calls, so bytes are the wrong scaling axis here).
⚠ Do NOT reach for `citm_catalog.json` as the fix without measuring: it is bigger and makes **fewer** defer calls.

## 5. WHAT THE GATES DO AND DO NOT PROVE

**Falsification TWO-SIDED (the only reason this rung is evidence at all):** corrupted single-byte verdict + gate ON ⇒ `Pattern match failed`; the SAME corruption + gate OFF ⇒ correct output. So the asm executes and the kill-switch genuinely routes to C. Revert verified by **md5 AND grep** before rebuilding — s212 records a revert that silently did not apply and left the `.so` corrupt for a cycle.
**Kill-switch ON == OFF byte-identical over all 315 programs, both modes.** Crosscheck **m3 311/4 · m4 311/2 · DIVERGE=2**, failure sets identical to s214 line-by-line, zero movers. unit 21/21 + 36/36 + 8426/0. smokes 7/7×2. `test_gate_no_hidden_global_in_emitted.sh` CLEAN, now enumerating all four new hidden globals under test.
⚠ **Prolog 5/5×2 and Icon 14/14×2 are no-regression evidence for the C-side visibility edit ONLY.** They do not move under the probe; citing them as asm evidence would be a FALSE CLAIM (s187).
⚠ **NOT RUN:** beauty, 15-demo board. Owed at the next landing.

## 6. TWO SMALLER THINGS, RECORDED SO THEY ARE NOT REDISCOVERED

**(a) STEP 0b EARNED ITS KEEP ON ME.** My first draft wrote `Sigma`/`Sigma_len`. The tree spells them with literal Greek codepoints, and `nm` shows capital **`B`** ⇒ exported ⇒ preemptible ⇒ **`@GOTPCREL`**, not `[rip+sym]`. Both halves of the error were caught by running step 0b instead of trusting the draft.

**(b) ⛔ `rtx_abi.inc` CARRIES THE STALE r12 ENTRY THAT ARCH §2 CORRECTED AT s205.** Lines 10–15 still read `r12  conditional-assignment stack pointer (own mmap area)`. ARCH §2 says r12 is **FREE — NOT A PIN** (`ZC_FRAME_R12` deleted at `da8c2347`, zero `#if` consumers), and this same header says "if the two disagree, the document wins." **This is the (a)-class rot from RULES' STALE-ORIENTATION rule sitting inside the executable half of the contract, where an asm author is most likely to trust it and needlessly avoid a free register.** NOT fixed in this commit (out of scope, and it changes no emitted byte) — flagged for the next RTX session, which should fix the header in the same commit that first uses r12.

## 7. STRUCTURAL RULE THE PORT IS BUILT ON, WORTH REUSING

**BAIL-BEFORE-MUTATE.** Both C bodies mutate the LIFO top (open pushes, close pops) and the `c_*` fallback repeats that mutation, so **every tail jump to C must happen while `g_dfx_top` is still untouched.** `open` therefore tests all bail conditions BEFORE the push; `close` **PEEKS** at `g_dfx[top-1]` and decrements only once committed to an arm it handles end to end. Getting this backwards double-pushes or double-pops a recursion stack that §3 shows nests by design — and it would link fine and pass short tests. Any future port of a stack-mutating C body inherits this rule.

RTX-3's `slen` traps are reproduced, not simplified: `slen==0` means **LENGTH UNKNOWN** (strlen owed) and `slen==0xFFFFFFFF` means **CSET — carrying tag DT_S**, so the tag alone never means "plain string". Both bail to C, as do DT_I/DT_R (they stringify through `snprintf`).

## 8. NEXT

1. **RTX-0f — the longer-window defer benchmark (§4).** Blocks any ratio for this slice. Highest value; it retro-qualifies this landing.
2. **The latch fix** as its own rung, graded on `140`/`141`, never on json.
3. Then RTX-8's remaining MATCH sinks (`match_enter`/`variant`/`value`/`replace`, cap/dcap).
4. `rtx_abi.inc` r12 correction (§6b).

`handoff_status.sh` is the push truth — not this document.
