# FINDING — s214 (2026-07-29, Claude): MODE 4 WAS DEAD TREE-WIDE ON ONE HIDDEN SYMBOL, AND THE TAB/RTAB BLOCKER THAT PARKED THREE SESSIONS IS ALREADY GONE

**Session:** s214-SN4 · **Ladder:** `GOAL-SNOBOL4-RTX.md` · **Landed:** SCRIP `488ecb73`
**Gates re-derived live on this tree (never hand-copied):** m3 **311/4/1 of 316** · m4 **141 → 311/4** ·
Prolog **188/0/1** · Icon **4/0** · RT_OPT=`-O0` · `.so` md5 `718277e8bbce472ff1d8277fb9bd0d3f`

---

## ▶ 1. THE HEADLINE: TWO INHERITED BLOCKERS WERE BOTH FALSE AT HEAD

**(a) `047_pat_rtab` PASSES.** The live cursor of s211 and s212 says TAB/RTAB segv at rc=139 on both
arms and calls that bisect *"STILL THE BLOCKER for anything needing a tree-wide regen."* Measured at
HEAD: `047_pat_rtab` → `abcd` rc=0, `046_pat_tab` → `de` rc=0. **Both green.**

HEAD is **11 commits ahead** of `57a7b598`, the commit s212 measured as bad. `3ea60fc2`
("PATCTX + FLATDISP-9, RSP zeta regime re-armed") is **precisely the frame-base axis s211 nominated
as its lead.** ⭐ **s211's LEAD WAS CORRECT ON AXIS AND WAS FIXED BY THE PARALLEL ζ LADDER, NOT BY
THIS ONE.** s211 deliberately recorded it as a LEAD rather than a CAUSE, and that restraint is what
kept it from being closed as "fixed" by the wrong commit — the discipline worked exactly as intended.

**(b) The recorded watermark was wrong by 34 programs.** s212 recorded m3 277/38. Measured **311/4**.
Three sessions carried three different numbers (314/1 · 268/47 · 277/38) against three different suite
sizes; the honest answer is that **none of them was re-derived on the tree it was quoted against.**

⇒ **NEITHER BLOCKER NEEDED A BISECT. BOTH NEEDED ONE MEASUREMENT.** Two sessions were ordered to
"FINISH THE BISECT" on a defect that a 6-line program run at HEAD disproves in one second.

---

## ▶ 2. THE REAL DEFECT: MODE 4 COULD NOT LINK — 173 OF 316 PROGRAMS

Re-deriving the *other half* of the watermark (m4, which no recent session had run) gave
**PASS=141 FAIL=174** — and **all 174 were LINK failures with ZERO runtime failures.** That signature
is never a codegen bug; it is one missing symbol. 24 of 25 sampled failures named exactly one:

```
undefined reference to `g_cap_gen'
```

### The mechanism — a THIRD visibility tier that no document names

`PATCTX-2` promoted `g_cap_gen` from `static` to `__attribute__((visibility("hidden")))` so
`rtx_match.S` could reach it. Three tiers exist, not two:

| linkage | reachable from `.S` INSIDE the `.so` | reachable from EMITTED mode-4 code OUTSIDE it |
|---|---|---|
| `static` | ✗ | ✗ |
| `hidden` | ✓ | **✗ — absent from the dynamic table** |
| default (exported) | ✓ (via GOT) | ✓ |

**ARCH §7 step 0(c) documents only the first column.** It is entirely about `B`/`D` vs `b`/`d` and
`.S`-reachability *within* the shared object. `hidden` is the correct answer to that question and the
wrong answer to the mode-4 question, so a session following 0(c) exactly lands on the defect.

⭐⭐ **THE BUG WAS WRITTEN DOWN, IN THE SAME LINE, AND READ AS DOCUMENTATION.** The declaration's own
comment says the α template reads it *"via [rip+g_cap_gen] **(both media)**"*. **"Both media" and
`hidden` are contradictory by construction** — TEXT medium *is* the separate object. The comment
asserts the requirement and the attribute violates it, eight words apart.

⛔ **AND MODE 3 IS STRUCTURALLY BLIND TO IT.** Mode 3 bakes the address in-process, so it cannot fail
this way at any severity. **A defect that only one medium can express will be invisible to any session
that re-derives only that medium** — and m3 is the cheap one, so m3 is the one that gets re-derived.
This is the `MODE34-IDENTICAL` invariant failing silently for at least 11 commits while every
session-state block reported gates as green.

### The fix — and why half (b) is CORRECTNESS, not linker appeasement

- **(a)** `g_cap_gen` → default visibility (now `D` in the dynamic table). `g_cap_gen_next` stays
  `hidden`; the template never references it, and confirming that is what keeps the fast path intact.
- **(b)** `rtx_match.S`'s three accesses → `[rip + g_cap_gen@GOTPCREL]`.

`ld` forces (b) — `R_X86_64_PC32 against symbol g_cap_gen can not be used when making a shared
object`, exactly as ARCH §7 step 0(c) predicts for an exported symbol. **But the linker error is the
lucky half.** An exported data symbol referenced from a **non-PIE** executable gets a **COPY
RELOCATION**: the executable owns the storage and the `.so`'s GOT is redirected to it. Had the
internal access stayed direct PC-relative, the `.so` and the emitted program would have been reading
and writing **two different variables** — a silent capture-generation divergence under `-no-pie`, with
no diagnostic at any stage. ⇒ **exporting a data symbol that asm also touches is never a one-line
change; the GOT conversion is part of the same edit.**

---

## ▶ 3. RESULT

| gate | before | after |
|---|---|---|
| m3 | 311/4/1 | **311/4/1 — failure set diffed LINE-BY-LINE, zero movers** |
| m4 | 141/174 (174 = link) | **311/4** (2 build, 2 run) |
| Prolog | 188/0/1 | 188/0/1 |
| Icon | 4/0 | 4/0 |

**Batteries are the RIGHT instrument here, and that needs saying because §7 step 2b usually forbids
citing them:** 2b's prohibition is on citing an unmoved battery as proof that *asm executes*. It
explicitly preserves them as valid evidence for **"C-side and visibility changes"** — which is exactly
what this is. The instrument is correct for this rung and would be a false claim on a port.

**m3 and m4 now agree at 311/4 but DIVERGE=4, not 0** — the sets are not the same four:
`140_pat_eval_double_fn_trick` and `141_pat_eval_double_fn_arbno` fail m3 (rc=139) and **pass m4**;
`test_string.sno` and `1017_arg_local.sno` fail m4 (build) and pass m3. `160_pat_alt_inner_gen_resume`
fails both but *differently* (m3 rc=0 wrong output, m4 rc=134 abort), which is itself a divergence in
manner that a pass/fail count cannot show.

⛔ **COLLATERAL, LOGGED NOT CHASED (per RULES — the monitor, not guesswork):** the 2 remaining m4 build
failures are a **different class** — the by-name-function path emits a duplicate local label,
`Error: symbol '.Lbynamefn53' is already defined` (`library/test_string.sno`,
`rung10/1017_arg_local.sno`). TEXT-medium only, so mode 3 cannot see it either. **Same blindness axis,
second instance, found in the same sweep** — which is the argument for making m4 a standing gate rather
than an occasional one.

---

## ▶ 4. THE SCORE, MEASURED FROM THE TREE (no prose inherited)

**30 symbols are asm:** 24 gated `RTX_FUNC` across 10 `rtx_*.S` · 2 gated legacy (`rt_deref`, `to_int`)
· 4 ungated legacy still in AT&T syntax and outside the contract (`rt_sg_*` ×3, `rk_gram_enter_box`).
11 family gates · 22 `c_*` fallback bodies retained as bisection oracles.

**Against SNOBOL4's live-called surface** — 115 distinct symbols across the 47 `.s` artifacts (git-dated
today, so valid as a call-boundary oracle): **17 converted · 98 remaining ≈ 15%.** The other 13 ports
are Icon/Raku-side. **By size: 2,234 asm LOC vs 20,006 C LOC ≈ 10%.** By rung: 14 done, 9 open.

Top unported by static call site: `rt_call_arr` 582 · `rt_defer_step` 432 · `rt_proc_set_*` 238×4 ·
`rt_defer_close` 229 · `rt_defer_open` 216 · `dtp_fn_of` 200 · `rt_subscript_var` 195 · `rt_arg_stage`
149 · `rt_proc_call_open{,_slim}` 132 each.

⛔ **THE s213 DIRECTIVE POINTS AT A DOCUMENT THAT IS NOT IN THE TREE.** The rung banner says the
0(d)-prefiltered queue of 40 symbols *"is at the s213 FINDING"*; no such FINDING exists in `.github`
(s213 was an ICON-RTX session and its SN4 half was never written or never pushed). **This is the (a)-class
rot RULES.md names, one turn later: a pointer asserting a location it cannot know.** The census above
was therefore re-derived rather than inherited, and the command is recorded here so the next session
does not have to trust this paragraph either:

```bash
cat corpus/benchmarks/snobol4/*.s corpus/programs/snobol4/demo/*.s \
 | grep -oP 'call\s+[^\s,@]+@PLT' | sed -E 's/call\s+//; s/@PLT//' | sort | uniq -c | sort -rn
```

⚠ **`grep -oP` WITH A NON-ASCII-SAFE CHARACTER CLASS IS THE STEP-0b TRAP, AND I WALKED INTO IT.** My
first census used `[a-zA-Z_][a-zA-Z0-9_]*` and returned 111 symbols. The UTF-8-safe `[^\s,@]+` returns
**115**. The four it missed were `rt_proc_call_epilogue_{,slim_}{γ,ω}` — **the exact four symbols
ARCH §7 step 0b was minted for.** They are already ported, so the score was unaffected; had they not
been, a "dead family" conclusion was one step away. **The trap is in the instrument, not the doc, and
the doc cannot catch it.**

---

## ▶ 5. TWO OTHER INSTRUMENT DEFECTS, BOTH MINE, BOTH CAUGHT BY DISBELIEVING A NUMBER

1. **`-I` is not a mode-3 flag.** My first m3 sweep passed `-I<inc>` and read **5/310**. mode 3 treats
   it as a filename (`scrip: cannot open '-I...'`). Includes go through **`SNO_LIB`**. This is s211's
   *"mode 3 does not forward argv"* one level over. ⭐ **The tell was that the number was ABSURD, not
   that anything errored** — every run exited rc=0.
2. **All 174 m4 failures being BUILD failures is itself a diagnosis.** A codegen regression produces
   wrong output; a uniform build failure produces one missing symbol. **I nearly filed it as "my
   harness" a second time** — the discriminator was that the standalone compile+assemble of the same
   program succeeded, so only the link differed.

⭐ **RULE THIS SUGGESTS: BEFORE QUOTING ANY SWEEP, RUN ITS OWN FIRST FAILURE BY HAND.** All three
defects above surfaced in under a minute that way, and two of the three were in my instrument rather
than the tree. A sweep that disagrees with a hand-run of one of its own members is not evidence yet.

---

## ▶ 6. DECISIONS TAKEN UNDER LON'S "ALL YOUR CHOICES" GRANT (s214)

1. **RTX UNPARKED.** `PLAN.md` carried *"PARKED since s171 — unparking is Lon's call"* while the goal
   file advanced through s213. Grant exercised; the stale banner is removed rather than left to
   contradict the cursor.
2. **BOTH STALE CHECKOUTS RELEASED.** `rt_subscript_var` (`OUT:SN4-RTX:s204`, ten sessions, 195 static
   sites, **Icon's #1 run-phase symbol at 315k dynamic**) → **released to ICON-RTX**, which has been
   blocked on it since s210. `rt_num_arith` (`OUT:SN4-RTX:s205`, nine sessions, 49 sites, and
   **bypassed by integer inlining since s203**) → **released, unclaimed.** The ledger's own ABANDON
   rule was written for exactly this and had never once been applied. **A ladder that has not touched a
   symbol in nine sessions does not own it.**
3. **THE WATERMARK CORRECTION OUTRANKED THE NEXT PORT.** With ~15% of the surface converted, one more
   port moves the score by <1%. Restoring `MODE34-IDENTICAL` unblocks every tree-wide `.s` regen for
   **all** ladders, and no port landed while m4 was dead could have been trusted anyway.

---

## ▶ 7. NEXT SESSION

1. **Push** (`488ecb73` + this doc; no credential was available at close — `handoff_status.sh` is the
   only truth on push state, not this block).
2. **MAKE m4 A STANDING GATE.** It was not run for at least 11 commits and it is the only medium that
   can express two of the defects above. `scripts/test_crosscheck_snobol4.sh` runs both; the m4 half
   costs ~315 gcc invocations (~8 min on this 1-core box, sliceable).
3. **`grep -rn 'visibility("hidden")' src/runtime/` AND CROSS-CHECK EVERY HIT AGAINST THE TEMPLATES.**
   Any hidden global that a template names in emitted text is this same defect, unfired. This is a
   ten-second sweep for a class that just cost 173 programs.
4. **RTX-8 MATCH remaining slices** (`rt_defer_step` 432 · `rt_defer_close` 229 · `rt_defer_open` 216),
   with `140`/`141_pat_eval_double_fn_*` as the **built-in canary** — they already fail m3 at rc=139 in
   exactly the deferred-evaluation family whose one-entry `rt_defer_get_pat_fn` latch RTX-8's rung text
   says the port must FIX rather than transliterate. ⭐ **A rung whose target is already red is worth
   more than one whose probe comes back silent** (the s204 lesson).
5. Do **not** re-open the TAB/RTAB bisect. It is closed by measurement, above.


---

## ▶ 8. THE CLASS IS BOUNDED AT ONE INSTANCE, AND IS NOW GATED STATICALLY (added later in s214)

Ran the sweep this FINDING recommended, rather than leaving it as advice. **18 hidden-visibility globals
exist in the runtime; exactly ONE was named in emitted text** — `g_cap_gen`, fixed at `488ecb73`. No
unfired second instance. Recorded because a bounded class is worth much more than an open worry.

⚠ **`g_pcall` / `g_pcall_top` LOOK LIKE A SECOND INSTANCE AND ARE NOT.** Both are hidden AND both are
named in `bb_call_proc_staged.cpp` — a template. **The reference is a COMMENT, at line 375.** The grep
that finds it cannot tell a comment from an emitted operand; only reading the line can. ⭐ These are the
same two globals ARCH §7 step 0(c) already singles out as *"differ only in an attribute you cannot see
at the use site"* — so the near-miss landed on exactly the pair the doc warns about, which is either
a good sign for the doc or a bad sign for my luck.

**GATE LANDED — SCRIP `e72da270`, `scripts/test_gate_no_hidden_global_in_emitted.sho`:** ~1 second,
static, runnable every session. **Static is the point.** The dynamic instrument for this class is the
mode-4 crosscheck, mode 4 is the expensive half, and skipping it is precisely how the defect survived
≥11 commits. A class only one medium can express needs a gate that does not require running that medium.

⛔⛔ **THE GATE'S FIRST VERSION FALSE-POSITIVED ON ITS OWN FIX — FIFTH INSTRUMENT DEFECT OF s214, AND THE
SECOND CAUSED BY MY OWN TEXT RATHER THAN THE TREE.** It harvested by grepping `visibility("hidden")`
across the `.c` files. My warning comment on `g_cap_gen`'s declaration — *"DO NOT re-add
visibility(\"hidden\")"* — contains that exact string, so the gate reported the one symbol it had been
written to protect. Now harvested from ELF:

```bash
readelf -sW out/rt_pic/*.o | awk '$4=="OBJECT" && $5=="GLOBAL" && $6=="HIDDEN" {print $8}'
```

⭐ **A GATE THAT READS PROSE INHERITS EVERY DEFECT PROSE HAS.** This project has documented prose rot
at least six times; the fix is never a better-worded document, it is deriving the answer from the
artifact. The ELF symbol table cannot be made stale by a comment.

**FALSIFICATION TWO-SIDED, because a gate never observed to fail is not a gate:** re-added
`visibility("hidden")` to `g_cap_gen`, recompiled `pattern_match.o` → **GATE FAILED**, naming the symbol
and the required fix. Restored → **GATE CLEAN**, source byte-identical (`git diff` empty), and
`libscrip_rt.so` relinked to md5 `718277e8bbce472ff1d8277fb9bd0d3f` — **identical to the pre-probe
build**, which is the kill-switch byte-identity discipline applied to a probe rather than a port.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
