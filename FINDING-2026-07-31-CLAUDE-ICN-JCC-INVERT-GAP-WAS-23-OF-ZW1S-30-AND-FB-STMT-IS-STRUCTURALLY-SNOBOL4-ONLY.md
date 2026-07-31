# FINDING 2026-07-31 CLAUDE ICN — THE JCC-INVERT GAP WAS 23 OF ZW-1's 30, AND FB-STMT IS STRUCTURALLY SNOBOL4-ONLY

**Session:** s204 · **Goal:** GOAL-ICON-BB · **Directive (Lon):** "Get benchmarks working using NON-POPPING
FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary" + "all your
choices" · **RT_OPT = -O0** (no `-O2` directed; O2-DIRECTED-ONLY rule honored).

**Commits:** SCRIP `7b974446` (ICN-JCC), `ed3d95a9` (ZD-2h-ICN). ⚠ **LOCAL ONLY — NOT PUSHED.** No credential
was supplied this session. `scripts/handoff_status.sh` is the only ground truth on push state; run it.

---

## HEADLINE 1 — `x86_jcc_invert` and `x86_jcc_op` are ONE vocabulary spelled twice, and they had drifted

`x86_jcc_op` (the BINARY opcode table) already encodes the full jcc set **including aliases** — `jz/jnz`,
`jb/jc/jnae`, `jae/jnc/jnb`, `jbe/jna`, `ja/jnbe`, and the `jnge/jnl/jng/jnle` signed aliases.
`x86_jcc_invert` knew **four pairs**. Every other condition reached its `abort()` instead of an encoder.

**The consumer is the ζ machinery itself.** `x86_fc_jcc_omega` is the ZB-FC-0 **conditional-omega pop synth**:
a raw `jz OMEGA` cannot carry the `add rsp,K` pop, so the synth inverts the condition and falls through to an
`x86_jmp(OMEGA)` that fires the `X86H_JMP` pop hook. The FORTH RSP ζ pop synth was therefore **unreachable**
for every template spelling `x86_omega("jz")` — `bb_binop_relop`, `bb_case_arm`, `bb_to`,
`bb_match_arbno/defer/value`: Icon's relop and generator families, i.e. the ones Icon leans on hardest.

### MEASURED — Icon `--run`, 293 programs, 2×2 factorial

| | default (ZW-1 active) | `SCRIP_BB_ALLOC=0` |
|---|---|---|
| **control** (4-pair table) | **215 / 48 / 30** | **245 / 18 / 30** |
| **fixed** (full table) | **238 / 25 / 30** | **245 / 18 / 30** |

Both control cells **reproduce the s203 ledger to the digit** — the instrument was validated against the
recorded numbers before the new cells were trusted. Benchmarks **2/10 → 6/10** in BOTH modes
(`deal` `ipxref` `queens` `rsg` newly green against the icont/iconx oracle).

### ⭐⭐ ZW-1 REFRAMED — 23 of the 30-program "universal carve cost" was never a carve cost

s203 bisected Icon's −37 to `f52d5877` (ZW-1 ACTIVATE) and recorded a 30-program cost recoverable by
`SCRIP_BB_ALLOC=0`. **23 of those 30 were an incomplete inversion table that ZW-1 merely made REACHABLE.**
Activating the universal carve made the pop synth live on Icon's relop/generator families, and the synth
aborted. ZW-1 **exposed** a table gap; it did not cause a regression. Genuine residual ZW-1 cost = **7**.

⛔ **THAT 7 IS NOT THE CURSOR'S "RESIDUAL 7".** Mine is 245−238 (ZW-1 cost after this fix). The cursor's is
252−245 (s202 watermark vs HEAD). Two different sevens that coincide numerically. Do not merge them — s203's
own warning against over-attributing to ZW-1 applies here too. The cursor's residual-7 bisect is STILL OPEN.

### INERTNESS — proven two ways, not asserted
(a) All 8 pre-existing spellings return **byte-identical** strings — mechanical check, 0 drift, and the same
harness confirms 0 gaps against `x86_jcc_op`'s vocabulary. (b) Every other input previously called `abort()`,
so the change can only convert FAIL→PASS and **can never convert PASS→FAIL**. Measured inert on Icon under
`BB_ALLOC=0` (245/18/30 both cells). Cross-language (`x86_asm.h` is shared, RULES flags it non-concurrency-safe):
SNOBOL4 m3 278/58 m4 276/54/6; Prolog 5/5/5 all modes green; rbp census ratchet gate GREEN unseeded=0.

**The abort is KEPT.** A missing inverse must never silently emit a wrong-sense branch.

---

## HEADLINE 2 ⭐⭐⭐ — FB-STMT CANNOT CONVERT ICON AT ALL; IT IS A SNOBOL4-ONLY RUNG BY CONSTRUCTION

Lon asked why RBP-indexed operands are still everywhere. **Census, 20 Icon benchmarks compiled fresh:**

| class | count | share |
|---|---|---|
| **C — data refs `[rbp±N]`** | **39,193** | **95.3%** |
| A — ceremony (prologue seed / epilogue / save-to-stack) | ~830 | 2.0% |
| D — rbp as scratch dest | **0** | 0% |

The s22c FB-STMT flip took SNOBOL4 data refs 11,697 → 6,548 (−44%). On Icon it did **nothing**.

**ROOT CAUSE.** `x86_fb_data()` consults `_.flat_fb_refine`, set at `emit.cpp:2662` from
`emit_fb_stmt_scan(g)`. That scan **bails to 0** on a disqualifying-kind list that IS Icon's entire vocabulary:

```
IR_SUSPEND · IR_SCAN · IR_SCAN_ENTER/ALTERNATE/SEQUENCE/UPTO/FIND/BAL/MATCH/MOVE/TAB
IR_TO · IR_TO_BY · IR_LIMIT · IR_REPALT · IR_PROC_GEN · IR_CREATE · IR_ITERATE
IR_DISJUNCTION · IR_CALL_BUILTIN_GEN · IR_KEYWORD_ICON_GEN
```

Any Icon program using a generator, a scan, `to`, `every`, `create` or alternation disqualifies the WHOLE
graph → `flat_fb_refine = 0` → **every data ref speaks rbp**. And the per-node bit map marks only
`IR_MATCH_LIT..IR_MATCH_ADVANCE` — the SNOBOL4 match family; Icon kinds get bit 0 regardless.

**This is not a bug in FB-STMT.** Its eligibility law is "every deep kind present is statement-bracketed
(DEFER/ARBNO/FENCE1/VALUE inside a HEAD..RELEASE/REPLACE range)" — a **SNOBOL4 match-family** bracketing
property. Icon has no `IR_MATCH_HEAD..RELEASE` ranges at all. The rung was correct and complete for the
language it was written against, and it is structurally inapplicable to the other.

**⭐ THE REAL NEXT RUNG (ICN-FB-1): Icon needs its OWN bracketing analysis**, not a widening of this one. The
question FB-STMT answers for SNOBOL4 — "does this deep kind's exit rebalance rsp through a head snapshot, so
nodes outside it arrive at static depth?" — has an Icon answer, and the ground truth for it is already cited
by ARCH-ICON.md: **`refs/jcon-master/tran/irgen.icn`, 43 `ir_a_*` procedures**, each an explicit
`ir_info(start, resume, failure, success)` four-port topology. The generator family's β re-pump edge is the
exact construct whose arrival depth must be classified. ⛔ Do NOT attempt this by relaxing
`emit_fb_stmt_scan`'s bail list — the list is that scan's correctness condition, and the per-node bit map
below it would still return 0 for every Icon kind.

---

## HEADLINE 3 — ZD-2h-ICN landed inert; the pin gate and the jmp-entry decline are in TENSION

The ZD-2h ⛔ is **scoped, not wrong**: its null was measured on the SNOBOL4 corpus and its stated reason is
semantic — SNOBOL4 has no lexical locals. Icon has one (queens: 71 declined `IR_VAR`/`IR_ASSIGN`, **all
pinned=1**). Landed as an env-gated arm (`SCRIP_ZD_PINLOCAL=1`), **OFF by default**, because the prohibition
was written by another session: this makes the widening measurable instead of flipping someone's default.

- **CORRECTED READING:** the failing conjunct is `is_global`, **not** `graph_has_local`. Icon procedure locals
  are lexical frame slots and are never entered in `name_binding.c`'s registered-global table, so the widening
  cannot be spelled as a relaxation of the second conjunct — the shape the carried NEXT item assumed.
- **PREDICATE CORRECTED BEFORE FIRST ARMED RUN:** `x86_fb_data()`, **not** `x86_fb_pinned()`. `fb_pinned` says
  the PROLOGUE established rbp; `fb_data` says a DATA REF resolves against rbp. Under FB-STMT (default-on) data
  refs on a pinned graph speak `rsp+op_flat_disp` outside deep match statements, so gating on the pin would
  admit exactly the locals the arm exists to exclude, and the depth-immunity claim would read true while being
  false.
- **MEASURED:** default 238/25/30 (inert). Armed 238/25/30 — **no delta, structurally explained**:
  `pinned = (flat_pat||flat_gen||flat_deep_arrival)` is the NEGATION of three of `zd_stub_ok()`'s conjuncts, so
  a jmp-entry pinned graph **returns at the top of `zd_plan`** before the arm is consulted (queens: 10/10
  graphs `deep=1`, `stub_ok=0`). Reachable only on `pinned && !flat_jmp_entry` graphs.

---

## Benchmark state (icont/iconx oracle built from source, v9.5.25a)

`deal` `ipxref` `queens` `rsg` `micsum` `version` **OK both modes**. `concord` `geddump` `tgrlink` — moved
PAST the emitter abort, now compile+link and SEGV at runtime (rc=139); geddump/tgrlink are the cursor's known
`git revert 7aade169` pre-pinned pair. `micro` — TIMEOUT (30s harness cap vs a 14.7s oracle); the cap, not
necessarily the program, is the blocker. ⚠ The harness compares a 30-line head, so a "30L OK" is not a
whole-output match — `rsg`'s s164 short-circuit finding is NOT retired by this session.

## Environment notes for the next session
`refs/icon-master` and `refs/jcon-master` do **not** exist in the SCRIP clone; ARCH-ICON.md and this goal file
both cite those paths. They were satisfied this session by symlinking the uploaded archives. Oracle built at
`/home/claude/icon-build` (`make Configure name=linux && make`). `nproc=1` in this container: a both-halves
rebuild is ~4 min, so budget A/B arms accordingly.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
