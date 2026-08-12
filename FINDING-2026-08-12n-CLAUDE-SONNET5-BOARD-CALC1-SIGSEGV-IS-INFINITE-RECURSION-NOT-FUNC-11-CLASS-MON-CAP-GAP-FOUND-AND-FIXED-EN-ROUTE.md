# FINDING 2026-08-12n — "13/15 BROKEN DEMO BOARD" IS AT LEAST THREE DISTINCT BUGS. (A) calculator-1/2 = ALREADY-KNOWN, SOURCE-DOCUMENTED "RESUME THROUGH A DEFER IS UNIMPLEMENTED" CLASS (lower_snobol4.c:1182, witnesses 178/179/182 — VERIFIED witness 178 still hangs today) — NOT A NEW BUG, TWO NEW REAL-PROGRAM REPROS FOR THE SET. (B) treebank-array = UNCHECKED R12 ARENA EXHAUSTION (DETERMINISTIC ONE-PAST-THE-END WRITE). (C) RTX-FUNC-11 (ALREADY DOCUMENTED) = WILD RBX. TWO MON-CAP FIXES LANDED EN ROUTE.

**Seat:** Claude Sonnet 5, BOARD, 2026-08-12 s43. Fresh three-repo clone + `install_system_packages.sh` (gdb live, s33–s39 apt trap not hit).
**Fingerprint:** SCRIP `73c1ac33` at session start; `e00a482f` after this session's commit. corpus `b80af33c`. `.github` `b58b4249`.
**Scope:** BOARD's s41b-assigned demo/bench repair — the calculator-1/calculator-2/treebank-array minimal SIGSEGV named in that cursor.

---

## 0. WHY THIS RUNG

BOARD s41b left two things for the next session: (1) fix a stale §SEATS row in `GOAL-SN4-HOME.md` (done, trivial, see commit history), (2) start the demo/bench SIGSEGV repair on `calculator-1.sno` et al. This finding covers (2).

## 1. REPRODUCED EXACTLY AS DESCRIBED

`echo "1/3" | ./scrip --run corpus/programs/snobol4/demo/calculator-1.sno` → SIGSEGV, rc=139.
Oracle: `/home/claude/x64/bin/sbl -b -f corpus/programs/snobol4/demo/calculator-1.sno` (same stdin) → prints `0`, rc=0. (Note: `-CASE 0` is a **control statement**, manual Ch.14 p.172, not a CLI flag as an earlier demo-header note assumed — the CLI equivalent is `-f`.)

## 2. MONITOR-FIRST — BLOCKED AT STEP 2 BY A GENUINE MON-CAP GAP, NOT THE REAL BUG

`PARTICIPANTS="spl scr"` sync-step monitor DIVERGEs at step 2 on *any* program using the `DEFINE('X()') :(X_x) ... X_x` skip-target idiom (8 occurrences in calculator-1.sno — one per function). Built a minimal 2-line reproducer (`DEFINE('EMIT()') :(EMIT_x) / EMIT_x`) and confirmed: **both engines execute it identically and correctly** (same output, exit 0) — yet the monitor still reports DIVERGE. Root cause: SPITBOL's oracle bridge counts a bare label-only line as its own null statement (manual Ch.4 p.28: "a program line consisting of just a label"), so it emits a LABEL event at that stno; scrip's bridge does not, landing directly on the next real statement's stno instead. Constant off-by-one from that point forward — a monitor instrumentation gap, not a control-flow bug.

**Fixed:** `MONITOR_SKIP_BARE_LABEL_STNO=1` (opt-in, off by default) in `scripts/monitor/monitor_sync_bin.py` — bounded, stno-map-verified read-ahead past a *specific, identified* bare-label statement only. This is deliberately narrower than a blanket LABEL filter, which the file's own docstrings explicitly forbid ("silently filtering LABEL would hide exactly the class of bug the monitor exists to catch"). Verified: minimal repro now reaches clean EOF with the flag on; baseline (flag off) still shows the original divergence — proves the fix is surgical, not a mask.

## 3. SECOND MON-CAP GAP FOUND: UNCAUGHT CONTROLLER CRASH ON A DYING PARTICIPANT

With the bare-label gap patched, re-running the monitor on the real calculator-1 repro didn't produce a clean DIVERGE — it crashed the **controller** with an uncaught `MemoryError` inside `read_exact()`. Cause: `scr` (scrip) SIGSEGVs mid-write of a wire record, leaving a torn/garbage header on the pipe; the `value_len` field (a raw u32) decodes as `4294967295` (all-bits-set), and the controller tries to `os.read()` that many bytes.

**Fixed:** capped `value_len` in `read_record()` at 16MB, raising the same `ValueError` the existing short-read path already uses — which the existing per-step `try/except` in `run()` already handles gracefully (`PROTOCOL ERR step N on <participant>: ...`). This is exactly the forensic information the instrument exists to preserve (which participant died, after which last-agreed event), and it was previously destroyed by the crash.

**Both fixes landed:** SCRIP `e00a482f`, pushed.

## 4. WITH BOTH FIXES: THE MONITOR NOW LOCALIZES THE DEATH — BUT gdb FORENSICS SHOW THIS IS A DIFFERENT BUG CLASS THAN IT LOOKS

Trace log (both engines) walks cleanly through all 8 DEFINE blocks (steps 1–9, each with one bare-label skip on the spl side), agrees at step 10 (`S = ARRAY(65536)`, stno 43 — type mismatch STRING/ARRAY is UNKNOWN-wildcarded per existing `keys_match` convention, so no false alarm) and step 11 (`LABEL stno=44`, i.e. reaching `LCASE = &LCASE`, line 68). **`scr`'s trace log ends there** — no VALUE event ever appears for statement 44 on the scr side; `spl` continues normally. Controller reports `PROTOCOL ERR step 12 on scr: insane value_len 4294967295` — scrip died mid-write, right after crossing into statement 44.

**This localization is misleading if taken as "the bug is at line 68."** Minimal-reproducer isolation immediately falsified that:
- `X = &LCASE / OUTPUT = X` alone: clean, both engines, identical output.
- `S = ARRAY(65536) / LCASE = &LCASE / OUTPUT = LCASE` alone: clean, both engines, identical output.
- The full 8-DEFINE block + `S = ARRAY(65536)` + `LCASE = &LCASE` + `OUTPUT = LCASE`, i.e. every statement calculator-1.sno executes up to and including the monitor's death point, **run to completion cleanly** under plain `./scrip --run` (no monitor).

So statement 44 itself is not the defect. This is the same "death point is not statement-deterministic" signature already documented for RTX-FUNC-11 (FINDING-2026-08-11-...-FOUR-HYPOTHESES-DIED...): monitor instrumentation changes allocation/timing enough to shift *when* a pre-existing problem manifests, without being the problem's cause.

## 5. ⭐⭐ gdb ON THE PLAIN (UNMONITORED) CRASH: GENUINE INFINITE RECURSION, NOT WILD rbx

`gdb --batch` on `./scrip --run calculator-1.sno < "1/3"`:

- `rip = 0x7ffff1652bf1`, in the anonymous executable JIT/RX slab (no objfile) — **same as FUNC-11's signature** ("crash PC is in emitted code").
- `rsp = 0x7ffffbfff000` — **the exact lower boundary of the mapped `[stack]` region** (`0x7ffffbfff000`–`0x7ffffffff000`, 64MB). The faulting instruction is `push %r10` — a push that decrements rsp by 8 and writes, landing 8 bytes below the mapped region. Classic stack-overflow signature.
- `rbx = 0x448b28` — **inside the process `[heap]` mapping** (`0x41c000`–`0x4a7000`), i.e. NOT wild, NOT unmapped. **This is the opposite of FUNC-11's `rbx` reading** ("in no mapping at all"). ⇒ **Different bug class from RTX-FUNC-11**, despite the superficially similar "crash PC in the RX slab" symptom. Do not conflate the two.
- Stack contents (`x/40gx $rsp`) are **perfectly periodic**: the 4 quadwords `{0x...2568, 0x0, 0x...2bd8, 0x...2563}` repeat identically, in lockstep, for the entire dumped range (checked 64 repetitions, all byte-identical). This is not a deep-but-finite call chain with big frames — it is the **same tiny code cycle calling itself with the same return addresses, making zero progress**, until the 64MB stack is exhausted.

**⇒ This is genuine infinite (unbounded) recursion in emitted pattern-matching code, not an allocation-frontier/rbx corruption.**

## 6. STRUCTURAL SUSPECT: FENCE-WRAPPED DEFERRED RECURSION (F/T/X MUTUAL RECURSION)

calculator-1.sno's grammar (lines 70–77) is built entirely from the `FENCE(op *SELF ...)` idiom:
```
F = A | FENCE('+' *F) | FENCE('-' *F . *NEG())
T = F ( FENCE('*' *T . *MUL()) | FENCE('/' *T . *DIV()) | '' )
X = T ( FENCE('+' *X . *ADD()) | FENCE('-' *X . *SUB()) | '' )
```
Per the manual's own "Recursive Patterns" section (p.122–123), a self-referencing pattern is safe from recursive-plunge stack overflow **iff a subject character is consumed before the recursive reference is reached** — the manual's own worked example is exactly this shape (`EXPRESSION = TERM | "(" *EXPRESSION ")"`, safe, vs. `EXPRESSION = *EXPRESSION | ...`, unsafe). Every recursive arm here (`FENCE('+' *F)`, `FENCE('*' *T ...)`, `FENCE('+' *X ...)`) matches a literal operator character **before** referencing `*F`/`*T`/`*X` — i.e. it is written in the manual's documented-safe form. On the trivial input `"1/3"`, the actual recursion depth needed is tiny (X→T→F→A→digit, then one more T level for the `/`). **There is no structural reason in the source grammar for this to recurse unboundedly on this input** — which points at the compiler/runtime, not the program, and specifically at how `FENCE(P)` and/or the deferred-pattern-call (`*F`/`*T`/`*X`) machinery is emitted/handled at backtrack.

**Not yet proven, deliberately not claimed as diagnosed** (MONITOR-FIRST's own discipline: naming the mechanism without discharging it is exactly the guess this project keeps paying for). But worth flagging: `FINDING-2026-08-07g-CLAUDE-SN4-ZWS-FENCE0-INTERIOR-SYNC-PREMATURE-WHACK-DOUBLE-RELEASES-STMT-CLAIM-AND-SIX-PROBES-FLIP.md` already documents a FENCE-adjacent defect class, and `GOAL-RBP-EARN.md`'s SEATS-table scope explicitly owns "ARBNO, FENCE rows." **This crash's structural surface is RBP-EARN's owned territory, not a generic BOARD-instrument issue** — named here rather than pursued further this session, per the seat partition in `GOAL-SN4-HOME.md` §SEATS.

## 7. NOT YET DONE (AT FIRST WRITING) — NOW DONE, SEE §8/§9

- calculator-2.sno and treebank-array.sno (named alongside calculator-1 in s41b) not yet independently confirmed to share this exact signature — same repro shape, not yet gdb-forensicked individually. Worth a quick confirm before assuming all three are one bug.
- No bisect run.
- Floors not re-swept this session (this rung is diagnostic depth, not a floor re-measurement).

## 8. ⭐ calculator-2.sno: CONFIRMED IDENTICAL CRASH — SAME CODE PATH, NOT JUST SAME CLASS

`echo "1/3" | ./scrip --run calculator-2.sno` → SIGSEGV rc=139; oracle → `0` rc=0 (same as calculator-1). gdb: `rip = 0x7ffff1652bf1` — **byte-identical to calculator-1's crash PC.** Same faulting `push %r10`. Same periodic stack pattern (`{0x...2568, 0x0, 0x...2bd8, 0x...2563}` repeating). `rbx = 0x44d4b8`, again inside the `[heap]` mapping (`0x41c000`-`0x4a8000`), again in-bounds. **This is not merely the same bug class — it is the same emitted code path crashing at the identical instruction address.** Expected: calculator-2.sno uses the mirror-image LEFT-associative grammar (ARBNO instead of right-recursion — see its header comment), but apparently drives the same shared FENCE/deferred-recursion runtime machinery into the same infinite loop.

## 9. ⭐⭐ treebank-array.sno: A THIRD, DIFFERENT, FULLY-CHARACTERIZED MECHANISM — UNCHECKED ARENA EXHAUSTION, NOT INFINITE RECURSION

`head -1 demo/treebank.input | ./scrip --run treebank-array.sno` → SIGSEGV rc=139 on the *first* (simplest) of 4 treebank lines; oracle on the same single line → correct Python-tuple-literal output, rc=0.

gdb: **completely different crash shape from calculator-1/2:**
- `rip = 0x7ffff17283ad` (different code address; `mov %rsi,0x8(%r12)`) — a write **through r12**.
- `rsp = 0x7ffffeaa3020`, well inside its `[stack]` mapping (`0x7ffffeaa3000`-`0x7ffffffff000`) — **not** at a boundary. Stack overflow is excluded for this one.
- `r12 = 0x7ffff3bffff8`. Per the product's own register contract (`GOAL-SN4-HOME.md` §REGISTER CONTRACT), **r12 is the capture-pending arena TOP** (mmap'd, STACK discipline, GC-visible). The write target is `r12+8 = 0x7ffff3c00000`.
- The containing mapping is `[0x7ffff2bff000, 0x7ffff3c00000)` — **exactly 16,781,312 bytes (16.0039 MB)**. `0x7ffff3c00000` is precisely the mapping's end address — **one byte past the last valid byte.** `r12` sits exactly 8 bytes before that boundary.

**⇒ This is not a wild pointer (it's not FUNC-11's class either) and not infinite recursion (it's not calculator-1/2's class). It is a clean, deterministic, unchecked-bounds arena exhaustion: the capture-pending arena is a fixed ~16MB region with no growth and no bounds check on the bump-allocation write, and treebank-array's pending-capture workload (nested parenthesized tree structure, `.`-captured under backtracking — exactly the R12/EARN-5 class BOARD's own B-1(a) finding already named for the probe suite: "a pending-capture record that must survive a backtrack boundary") fills it completely on this input.** This crashes on the *simplest* of the 4 treebank lines, so "16MB is enough for real workloads" does not hold even at small scale — worth flagging as more urgent than a corner case.

**⇒ "13/15 broken demo board" is not one bug. It is at minimum THREE independently-characterized mechanisms**, now cleanly separated: (a) calculator-1/calculator-2 — infinite FENCE/deferred-recursion, JIT-slab `rip`, in-bounds `rbx`, periodic stack overflow; (b) treebank-array — unchecked r12 arena exhaustion, deterministic one-past-the-end write; (c) the previously-documented RTX-FUNC-11 — wild/unmapped `rbx`, scale-triggered, beauty_suite's 17/17. All three happen to be capable of landing `rip` in the anonymous JIT slab, which is why they look superficially alike — **`rbx`/`r12` mapping status is the actual discriminator, not the crash PC's section.**

Both (a) and (b) land on RBP-EARN's owned surface (FENCE/ARBNO and the R12 arena/EARN-5 respectively) — named and evidenced here, not pursued into fixes this session, per the seat partition.

## 11. ⭐⭐⭐ ROOT CAUSE FOUND: THIS IS AN ALREADY-KNOWN, ALREADY-NAMED, SOURCE-DOCUMENTED LIMITATION — NOT A NEW BUG

Traced (a) into `src/lower/lower_snobol4.c:1182` (SEQ-RESUME-GATE). The comment there, in full candor, documents: `IR_MATCH_DEFER`'s emitted form (`bb_match_defer`, a jmp-entry TRANSFER box, not a stateful generator) cannot correctly resume on backtrack — "resuming it re-transfers into the target from scratch and can succeed identically on replay, an infinite loop with no progress." The comment explicitly states this was scoped, not fixed: **"true nested-generator resume through a defer is unimplemented and out of scope for this fix"** — and names three witnesses as still broken by it: **178/179/182, "manual p.122 shape," "move SIG11→HANG, still wrong either way."**

**Verified directly:** `crosscheck/patterns/178_pat_recursive_star_list_zs2.sno` is the manual's own p.122 worked example verbatim (`ITEM = SPAN("0123456789") | *LIST` / `LIST = "(" ITEM ARBNO(",",ITEM) ")"`). At current HEAD: oracle → `T1 MATCH` / `T2 CORRECT-FAIL`, exit 0. `scrip --run` → **exit 124 (timeout/hang)**, exactly as the comment predicts.

**⇒ calculator-1/2 are not a new defect.** They are real-world (not synthetic-witness) instances of this same, already-tracked, self-documented-as-unimplemented class: a pattern defined via a deferred self/mutual reference (`*F`/`*T`/`*X` here; `*LIST` in witness 178) that needs to be genuinely re-entered with retained backtrack state cannot do so — every retry re-transfers into the target pattern from scratch. calculator-1/2 additionally *crash* rather than *hang* (witness 178's failure mode) because their specific recursive shape apparently keeps pushing new stack frames on each from-scratch re-transfer rather than spinning at constant stack depth — worth noting as a variant of the same mechanism, not a different one.

**This is a compiler-feature gap, not a quick fix** — implementing correct resumable-generator semantics through a deferred pattern reference is exactly the kind of work the comment scoped out of its own rung. It sits on RBP-EARN's owned surface (`GOAL-RBP-EARN.md`'s own scope line already lists "ARBNO, FENCE rows... D12/D13 recursion class"), and 178/179/182 are RBP-EARN's own named witnesses for it. calculator-1.sno and calculator-2.sno should be added to that witness set as real-program instances of the same class — they're more likely to be hit by actual programs than the synthetic probes, which raises the practical stakes of landing it.

## 13. QUICK CONFIRMATION: THE FOUR -match/-match-fence VARIANTS

`calculator-1-match`, `calculator-1-match-fence`, `calculator-2-match`, `calculator-2-match-fence` all SIGSEGV (rc=139) on the same repro. Spot-checked `calculator-1-match`: `rip=0x7ffff1602bef` (differs from calculator-1's — expected, different program/layout) with `rbx=0x43ba58`, a small in-range value consistent with class (a) rather than FUNC-11's wild-pointer signature. Not full periodicity-verified like the two primary cases; reasonable-confidence extension, not a third independent gdb forensic. **⇒ likely 6 real programs (calc-1/2 + their 4 match variants) affected by the same already-known "resume through a defer" limitation, not 2.**

## 14. FINAL SUMMARY

"13/15 broken demo board" is at least three mechanisms:
1. **calculator-1, calculator-2, and (likely) their 4 -match/-match-fence variants** — recursive-pattern-via-deferred-reference resume is unimplemented (already known: `lower_snobol4.c:1182`, witnesses 178/179/182). RBP-EARN surface. Up to 6 new real-program repros to add to the witness set.
2. **treebank-array** — unchecked ~16MB R12 capture-arena exhaustion, deterministic one-past-the-end write. RBP-EARN surface (EARN-5).
3. **RTX-FUNC-11** (beauty_suite, 17/17, already on record) — wild/unmapped `rbx`, scale-triggered. RBX surface.

No code fix attempted on (1) or (2) this session — both require work on RBP-EARN's owned surface, and (1)'s own prior authors already scoped it as a real feature project, not a quick patch. Two real, tested, low-risk MON-CAP fixes landed and committed (SCRIP `e00a482f`). Full BOARD/plan-doc updates committed (`.github`, local, awaiting push credential).

## UNBLOCKS

**RBP-EARN:** a third data point for FENCE/deferred-recursion correctness, independent of the ARBNO probe-suite class already tracked — worth checking whether a fix there also clears this. **ANY SEAT chasing demo-board SIGSEGVs:** do not assume "crash PC in the RX slab" alone means RTX-FUNC-11 — check `rbx` mapping status specifically; FUNC-11's is wild/unmapped, this one's is a valid heap address. Two different symptom classes can share a JIT-slab crash PC.
