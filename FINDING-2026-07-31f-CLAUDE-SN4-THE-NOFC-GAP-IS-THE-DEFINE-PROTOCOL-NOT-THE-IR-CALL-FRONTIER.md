# FINDING 2026-07-31f — CLAUDE — SN4: THE NOFC GAP IS THE **DEFINE PROTOCOL**, NOT THE `IR_CALL` FRONTIER. ZD-7 SLICE 2 CLEARED 461 DECLINES AND MOVED THE NON-POPPING GAP BY **ONE PROGRAM**.

**Session:** s22j (2026-07-31). **HEAD measured:** SCRIP `e26d4584` (one commit past the s22i cursor's `a70f0632` — a CELL-MACHINE prose scrub).
**Status:** MEASUREMENT + REFRAMING ONLY. **ZERO code changes. Tree untouched, watermark re-proven at both ends of the session.**

---

## 1. WATERMARK RE-PROVEN LIVE AT HEAD (census shelf-life law honoured — re-run, never cited)

| runner | m3 | m4 | DIV |
|---|---|---|---|
| crosscheck (317), HEAD default | 231/86 | **230/86/1** | 1 {W04_arbno_basic} |

m4 is **EXACT** vs the s22i cursor (230/86/1). The m3 −1 vs the recorded 232 is the known
`test_string` nondeterministic segv — it is present in the m3 FAIL set and **absent from m4**, which is
precisely why the law is COMPARE m4, NEVER m3. No regression; the baseline is intact.

---

## 2. ⭐⭐⭐ THE HEADLINE — s22f's PREMISE IS FALSIFIED BY ITS OWN SUCCESS METRIC

s22f defined the non-popping rung's success metric: **`SCRIP_NOFC=1` reaching the watermark proves the
Gen-1 FC arm is dead and its deletion (with all five pops) is mechanical.** It measured the gap at
**m4 229→209 (−20)** and concluded the pops are *"a shadow cast by the `IR_CALL` frontier"* (519 declines).

ZD-7 SLICE 2 (s22h/s22i) then admitted `IR_CALL` to the ZD regime: **decline census 519 → 58, i.e. 461
declines cleared.** If the premise were right, the NOFC gap should have collapsed.

**MEASURED AT HEAD:** `SCRIP_NOFC=1` → **m4 211/105 = −19.**

> **461 cleared declines bought exactly ONE program.** (−20 → −19; the single rescue is
> `087_define_freturn`.)

⛔ **THE PREMISE WAS WRONG IN ITS QUANTIFIER, NOT ITS FAMILY.** The pops are not a shadow of *`IR_CALL`*;
they are a shadow of the **DEFINE CALL PROTOCOL**, which was only ~11% of the `IR_CALL` census but is
**100% of the NOFC break set**. A decline census over an op-code is not a census over a *construct* —
519 `IR_CALL` declines were 461 builtins (irrelevant to FC) + 58 proc calls (the entire gap).

⚠ **INSTRUMENT LAW EARNED — A DECLINE CENSUS RANKS OPCODES, NOT BLOCKERS. RANK BY BREAK SET, NOT BY COUNT.**
The 519 was the largest number on the board and it directed a slice that moved the actual gate by one
program. The discriminating instrument was never the census — it was the **A/B break-set diff under the
killswitch**, which was available the whole time and costs two runner invocations. Diff the SET.

---

## 3. THE BREAK SET IS 19 PROGRAMS AND PARTITIONS INTO EXACTLY TWO FAMILIES

`comm` of the m4 FAIL sets, default vs `SCRIP_NOFC=1`. **NEWLY FIXED = 0** (the arm is purely load-bearing).

**FAMILY A — DEFINE call protocol (15):** `083_define_simple_return` `084_define_loop_call`
`085_define_two_args` `086_define_locals` `088_define_recursive_fib` `090_define_entry_label`
`097_define_capture_return_d2probe` `100_roman_numeral` `1012_func_locals` `204_gc_recursive_frames`
`212_gc_args_in_flight` `216_indirect_goto_computed` `test_math` `test_stack` (+`1019_eval_string`, §4).

**FAMILY B — deferred goto (4):** `1020_code_label_transfer` `1021_code_direct_goto`
`215_indirect_goto_cond` `216_indirect_goto_computed` (216 is in both).

**Per-program blocker partition (`SCRIP_CALL_DIAG=1`, live compiler, never artifacts):**

```
083_define_simple_return    IR_CALL(double) x2   IR_SAVE_RESTORE x1
088_define_recursive_fib    IR_CALL(fib)    x5   IR_SAVE_RESTORE x1
100_roman_numeral           IR_CALL(roman)  x6   IR_SAVE_RESTORE x1
204_gc_recursive_frames     IR_CALL(build)  x3   IR_SAVE_RESTORE x1
214/215/1020/1021           IR_GOTO_DEFERRED
216_indirect_goto_computed  IR_CALL + IR_SAVE_RESTORE + IR_GOTO_DEFERRED
```

⭐⭐ **`IR_CALL`(proc) AND `IR_SAVE_RESTORE` APPEAR TOGETHER IN ALL 15 AND NEVER APART.** That is not a
correlation to explain — it is **Lon's law 6 rendered as a measurement**: *"DEFINE, constant-folded, emits
exactly TWO BBs: `IR_SAVE_RESTORE` + `IR_CALL`."* The census is the law's own fingerprint.

---

## 4. THE RESIDUAL `IR_CALL` 58 ARE 100% USER PROCS — THE BUILTIN FRONTIER IS FULLY CLEARED

Live callee partition of the 58: `roman` 6 · `Pop` 6 · `fib` 5 · `dispatch` 4 · `myfunc` 3 · `build` 3 ·
`upcase` 2 · `ref_a` 2 · `ispos` 2 · `fact2` 2 · `fact` 2 · `double` 2 · `add` 2 · `Push` 2 · `swap` 1 · …

**ZERO builtins.** Every one is a `DEFINE`'d procedure routing `CALL_ROUTE_PROC_STAGED`
(`bb_call.cpp:524` → `bb_call_proc_staged_str`). The s22i exclusion `rt_proc_is_registered(fn) → decline`
is therefore **exactly and only** the DEFINE family, and the 58 is not residue to be trimmed — it is the
whole remaining construct.

**Full HEAD census (live, all 317):** `IR_MATCH_HEAD` **247** · `IR_CALL` **58** · `IR_SAVE_RESTORE` **25**
· `IR_GOTO_DEFERRED` **8**. Matches the s22i cursor to the digit.

`1019_eval_string` declines on **nothing** — `flat_jmp_entry` declines EVAL/CODE chains WHOLESALE at graph
level, so it never enters `zd_plan`. It breaks under NOFC without ever appearing in a decline census.
⚠ **A GRAPH-LEVEL WHOLESALE DECLINE IS INVISIBLE TO A PER-RUN CENSUS.** Any "have we cleared X?" gate read
off `zd_plan` alone will silently omit this class.

---

## 5. ⛔⭐⭐ THE NEXT RUNG IS THE **PROTOCOL RUNG**, AND THE TREE ALREADY SAYS SO — DO NOT CLONE A VALUE-SPINE ARM

`emit.cpp:1847` (written by an earlier session, verified against live source this session) already
adjudicates the move this finding's partition would otherwise invite:

> *"Admitted ALONE rather than with the rest of the tail: `IR_SAVE_RESTORE` carries a conditional
> g_emit-mutating preamble that is the CALL2BB arg-window linkage (:989), and `IR_GOTO_DEFERRED` is the
> EVAL/CODE runtime label transfer that `flat_jmp_entry` declines WHOLESALE by design — **both belong to
> the protocol rung**, and cloning a value-spine arm onto either would be **the 017 shape with extra steps**."*

**THE SPITBOL SEMANTICS SAY THE SAME THING (manual Ch.19 `DEFINE`, read this session, reference text):**
the values of the variables in the locals list are **saved prior to function entry and restored upon
return**; a function returns a value **by assigning to a variable with the same name as the function**,
and returns by transferring to **`RETURN` / `NRETURN` / `FRETURN`** — by value, by name, or to fail.
Ch.4/Ch.8: calls are **call-by-value**, and *"all local variables should be declared in the DEFINE
function so they will be saved and restored during recursive calls."*

⛔⭐⭐ **CORRECTION — I DERIVED A TEMPLATE CLAIM FROM LANGUAGE SEMANTICS AND IT WAS WRONG. MEASURED, THEN
RETRACTED, IN THIS SESSION.** I first concluded from the manual that a DEFINE'd proc call *"has no
return-value descriptor to marshal into a ζ cell"* because SPITBOL delivers the result through the NV
global. **FALSE AT THE TEMPLATE LAYER.** `bb_call_proc_staged.cpp:399` is:

```
+ x86("mov", FRQ(off),     "rax")
+ x86("mov", FRQ(off + 8), "rdx")
```

`rt_proc_call_epilogue_γ` **implements the fname-global semantics inside the runtime and returns an
ordinary DESCR_t in rax/rdx.** The template sees a plain C-ABI return, structurally identical to the
builtin arm, at a SINGLE convergence tail (`L(2)`) that every arm — γ epilogue, ω epilogue, ret epilogue,
fail — jumps to. The result side of a proc ZD arm is therefore a **two-line** change, not an impossibility.

⚠ **LAW EARNED — THE MANUAL DESCRIBES THE LANGUAGE; THE RUNTIME ALREADY IMPLEMENTS IT; THE TEMPLATE SEES
THE C ABI. DO NOT REASON FROM CH.19 STRAIGHT TO A TEMPLATE SHAPE — READ THE EMISSION.** Reading the
manual was correct and necessary; using it to predict template structure skipped a whole layer.

⭐⭐ **WHAT ACTUALLY BLOCKS FAMILY A IS THE ARG SIDE, NOT THE RESULT SIDE.** Args reach the callee through
`bcps_arg_slot(...)` → `FRQ(slot)` reads across **five distinct arms** (the SCC dyn-scope arm, the fused
`open_detN` lea-the-cell-address arm, the classic `stage_arg_inline` chain, the `dc` arm, and the legacy
non-RSP arm). Under ZD every one shifts by `op_zdepth`. **s22g already measured this exact conversion at
m3 232→169 (−63).** Family A is a five-arm conversion, not a two-line one, and it is correctly sized as
its own rung.

Mapping the construct onto the four ports (this is the design content of the rung):
**γ = `RETURN`** · **ω = `FRETURN`** · the result is the fname global read by the *consumer* ·
`IR_SAVE_RESTORE` is the save/restore of formals+locals as ordinary globals on the pushdown stack —
**itself a BB, carving its own slots (law 1), which is the ONLY ζ permitted in the call path (law 7).**

---

## 5b. ⛔⭐⭐ ZD-8 ATTEMPTED ON FAMILY B AND **REVERTED RED**. TWO HYPOTHESES FALSIFIED, THE BLOCKER LOCALIZED.

Family B (`IR_GOTO_DEFERRED`) looked like the cheap half: `bb_goto_dyn.cpp` is **14 lines** and makes
**zero contact with the flat frame** — no `FR`, no `FRQ`, no `zoff`, no slot grant. It seals `op_sval` in
.rodata, calls `rt_goto_transfer`, wires γ. No reader to convert, no result to place.

**ZD-8 (a)+(b) — admit to `zd_wl_kind`, `K=0` (the `IR_ASSIGN` sink spelling), template untouched.**
**MEASURED: m4 230/86 → 226/90, DIVERGE 1 → 5.** Newly broken = **exactly the four admitted programs**
(`1020` `1021` `214` `215`), all m4-only (m3 passes → hence the 4 new divergences).

⛔ **H1 FALSIFIED — "ZERO FLAT-FRAME CONTACT ⇒ FREE ADMISSION" IS FALSE, AND THE REASON IS ALL-OR-NOTHING
PER STATEMENT.** The `.s` diff shows the break is **not in the goto box at all**: the sibling `CODE(...)`
call in the same statement flips from the flat arm to the **Slice-2 ZD by-name arm** (`.Lbynamefn9` →
`.Lbynamefnzd9`). Admitting a node does not just change that node — it arms its whole STATEMENT and
re-routes every sibling. **A template with no frame contact can still be the trigger for someone else's
defect.** Any future "this kind is free to admit" argument must diff the statement, not the box.

⛔ **H2 FALSIFIED — THE POP ELECTION IS NOT THE DEFECT.** Hypothesis: `zd_plan` elects the release
authority by `gin`/`oin` ("is my γ/ω target inside this run?"), and for `IR_GOTO_DEFERRED` both are outside
BY CONSTRUCTION (γ is wired at lower time to the graph exit), so the one node that can *never* execute a
release — `rt_goto_transfer` runs the transferee nested and never returns to this statement — gets elected
to carry the whole statement's terminal pop. `emit.cpp:2617` states the same fact from the fc side
(*"abandoned bracket depth is by-design"*). **ZD-8 (c) suppressed `zgpop`/`zwpop` on the kind.
MEASURED: byte-for-byte the same result — 226/90, DIVERGE 5, same four programs.** The election is not it.

✅ **LOCALIZED:** the Slice-2 by-name ZD arm fires in **2 of 318** programs at baseline (`1015_opsyn`,
`1017_arg_local`) and **both pass**, including the full `narg=2` ZOPQ arg-copy loop. So the arm is *not*
generically broken and is *not* dead code — it is **narrowly exercised**, and these four statements are a
shape it has never seen. ⚠ **A 2-of-318 exercise rate is not a validated arm.** Slice 2 landed green on a
watermark that could barely see this arm; the goto admission is the instrument that revealed it.

⛔ **NEXT INSTRUMENT IS THE MONITOR, NOT MORE `.s` READING.** RULES.md is explicit: a diverging program is
bracketed by the 2-way sync-step monitor, then gdb with a hit-count. I stopped the hunt here rather than
keep guessing at asm — two hypotheses had already been falsified by inspection-driven reasoning, which is
the signal to switch instruments.

✅ **REVERTED. WATERMARK RE-PROVEN AT CLOSE: m3 232/85 · m4 230/86/1 · DIV=1 {W04_arbno_basic}, m4 fail set
IDENTICAL BY SET to session start. `git status` clean; zero commits from the ZD-8 attempt.**

---

## 6. ⭐ NEXT — ORDERED

1. ⭐⭐⭐ **THE PROTOCOL RUNG (Family A, 15 programs / 58+25 declines).** `IR_CALL`(proc-staged) +
   `IR_SAVE_RESTORE` land **TOGETHER as one construct** or not at all — the census proves they never occur
   apart, and law 6 says they are two BBs of one DEFINE. ⛔ **NOT a `bb_call_fn_str` ZD-arm clone** (§5).
   ⚠ **NEEDS A LON RULING BEFORE CODE:** law 7 says *"`IR_CALL` sets up the frame, nothing else"* and
   *"slot0 result protocol DIES (return value = the fname global at RETURN)"* — the open question is
   whether the consumer's read of the fname global is a ZD-staged cell or an NV load, i.e. whether this
   rung produces a ζ arm at all or **deletes the need for one**. The second reading is the one law 7's
   "per-function/graph storage planning DIES" sentence implies, and it would make Family A drop out of the
   FC census without any value-spine arm being written.
2. ⭐⭐ **Family B — `IR_GOTO_DEFERRED`, NOW BLOCKED ON A NAMED PRE-EXISTING DEFECT (§5b).** s22f's "DO NOT
   open as a standalone rung" is retired for the right reason but the rung is **not** cheap: admission is
   three lines and correct, and it fails on the Slice-2 by-name ZD arm in the sibling `CODE(...)` call.
   **THE REAL NEXT STEP IS TO FIX THAT ARM FIRST, VIA THE MONITOR**, with `1020_code_label_transfer` as the
   witness (m3 passes, m4 fails — a clean 2-way divergence, ideal for the sync-step bracket). ZD-8 (a)(b)(c)
   is written up in §5b and can be re-applied verbatim once the arm is sound.
3. ⭐⭐ **ZD-5 / `IR_MATCH_HEAD` (247)** — untouched by this session and still the largest family and the
   85/86-red mass (the m4 fail set is almost entirely `pat_*`).
4. **THEN** `SCRIP_NOFC=1` reaches the watermark ⇒ delete the FC arm + all five pops. Unchanged; the gate
   is now known to be Families A+B, **19 programs**, not a 519-entry frontier.
5. CARVE-ERAD per THE MODEL's three-step order · `claws5`/`json` assembler-rejected codegen · the 130/131
   clean-HEAD segv — all unchanged, all still open.

---

## 7. TRAPS AND LAWS EARNED THIS SESSION

- ⚠ **RANK BY BREAK SET, NOT BY DECLINE COUNT** (§2). An opcode census is not a construct census. The
  killswitch A/B set-diff is two runner invocations and is the discriminating instrument; the count is not.
- ⚠ **A WHOLESALE GRAPH-LEVEL DECLINE IS INVISIBLE TO A PER-RUN CENSUS** (§4, `1019_eval_string`).
- ✅ **m3/m4 DISAGREEMENT WAS THE KNOWN `test_string` PHANTOM, NOT A REGRESSION** — resolved by the
  standing law (gate on m4) plus checking set membership, not counts. The law paid for itself immediately.
- ✅ **THE TREE'S OWN COMMENTS ARE A PRIMARY SOURCE.** `emit.cpp:1847` had already adjudicated the
  §5 question before this session asked it. Grepping the blocker's own dispatch site for prior reasoning
  is cheaper than re-deriving the ruling — and in this case it agreed with the manual.
