# FINDING s173 (2026-08-19, seat7 `/home/claude7`, Claude Opus 5) — THE `SCRIP_SPAN_FRAME` FLIP IS **NOT** CLEAN: THE OWED SWEEP FOUND A COUNTEREXAMPLE THE 318-PROGRAM SWEEP COULD NOT SEE, AND IT IS A NONDETERMINISTIC SILENT WRONG ANSWER

**Brief executed:** queue row 7 `span-frame-flip` — *"HQ-59 ruling (fz3-flip precedent, Lon desk delegation 2026-08-20): flip `SCRIP_SPAN_FRAME` default ON … Run the owed 527-program artifact sweep + 6-suite A/B at armed default at HEAD; **flip if clean**, own commit."*
**Verdict: NOT CLEAN — THE FLIP IS NOT LANDED.** The sweep the ruling made a precondition is exactly the instrument that found the blocker. The flip edit was written, then reverted; the trees carry the measurement, the counter-witness, and this record, and nothing else.
**Tree:** SCRIP `1ac779ad` (unmodified), corpus this commit, `.github` this commit. Every number below from a **`make pristine`** build at that HEAD (HQ-27), RT_OPT `-O0` (FACT RULE O0-DEV), oracle `x64/bin/sbl` verified alive before any board was trusted.

## ⛔ THE ONE SENTENCE

Across a 13-suite, 1589-row, two-arm, two-medium board the armed arm **cures 13 rows — every one `SIG11 → PASS`** — and **breaks exactly one**, `programs/snobol4/beauty_suite/TDump_driver.sno`, from `PASS` to a **run-to-run nondeterministic wrong answer in both media**; and the broken row fails at *the very shape the arm exists to fix*, a scratch-cell leaf on an ALT arm.

## THE LEDGER — WHAT THE ARM BUYS AND WHAT IT COSTS

### `.s` blast radius (mode-4 TEXT, `util_s_md5_sweep.sh`, default vs `=1`)

| set | programs | comparable (rc=0) | movers |
|---|---|---|---|
| house list (demo + crosscheck + probe/bb) — **the owed "527" sweep** | 529 | **527** | **30** |
| **every `.sno` in corpus + SCRIP/test** | 1637 | **1359** | **84** |

⛔ **The owed sweep was worth running and the wider one was worth running too.** Seat8's s170 measured **15 movers of 318** and predicted the radius was *"only programs holding an alternation with a scratch-cell-leaf arm."* The prediction is right about the *shape* and wrong about the *size*: the 84 include `probe/leafsib` ×6, `probe/clobarm` ×4, `probe/zd5b` ×5, `probe/m1` ×5, `probe/deferclob` ×2, `probe/ptj` ×2, 7 `beauty_suite` programs, `beauty.sno` and `beauty_c.sno` themselves, 5 `programs/lon`, and the whole claws5/json/porter demo family. **`TDump_driver.sno` and `TDump.sno` are both movers** — the broken program is squarely inside the arm's own blast radius, not collateral.

### Behaviour — the two-arm board (each row graded m3 AND m4 against the live oracle or its pinned `.ref`)

| board | suites | rows/arm | m3 PASS off→on | m4 PASS off→on | verdict movers |
|---|---|---|---|---|---|
| A (the brief's 6-suite) | crosscheck, patterns, bb_probes, feature_test, probes_misc, demos | **1041** | 974 → **985** | 949 → **961** | **13, all `SIG11 → PASS`** |
| B (the other 7, run because 44 of the 84 `.s` movers live there) | beauty_self, beauty_suite, benchmarks, csnobol4_suite, gimpel, lon, misc | **548** | 162 → 161 | 154 → 154 | **3** (below) |

**Board A is unambiguously good — 4164 gradings, 13 movers, every one a cure, zero regressions:**
`leafsib_{span,tab,rtab,rem,break,breakx}` (6, both media) · `clob_altarm_arm2direct_red` · `ptj2_number_leading_digit_segv` · `cn_alt_leaf_{flat,lit}_red` (m4) · **`claws5`, `claws5-match`, `claws5-match-fence`** (m3). Seat8's DONE-WHEN pair reproduces exactly at this HEAD, and **all three claws5 programs cure, not the one seat8 named** — 3/3 deterministic runs per arm, `rc=139 → rc=0` and output equal to `.ref`. `claws5.sno` m4 stays `SIG11` in both arms: that is the separate defect seat8 stated and D-2 still owns, untouched here.

**Board B's 3 movers, graded individually:**

| row | reading | disposition |
|---|---|---|
| `csnobol4-suite/nqueens.sno` m4 `TIMEOUT`→`SIG11` | red→red | crash-flavour change on an already-red row; not a mover |
| `dotnet/code.sno` m3 `TIMEOUT`→`SIG11` | red→red | same |
| **`beauty_suite/TDump_driver.sno` m3 `PASS`→`DIFF`** | **green→WRONG ANSWER** | ⛔ **the blocker** |

## ⛔⭐ THE BLOCKER, MEASURED — AND WHY EVERY EARLIER SWEEP MISSED IT

**`ulimit -s unlimited` is load-bearing.** `scorecard_snobol4.sh`'s `run_one` sets it; an ordinary shell does not. The defect is invisible at the 8 MB default and appears only in the graded environment:

| arm | `ulimit -s` 8 MB | `ulimit -s unlimited` |
|---|---|---|
| default (OFF) | **10/10 PASS** | **10/10 PASS** |
| `SCRIP_SPAN_FRAME=1` | **10/10 PASS** | ⛔ **2/10 PASS · 8/10 WRONG** |

```bash
cd corpus/programs/snobol4/beauty_suite
( ulimit -s unlimited; SCRIP_SPAN_FRAME=1 SNO_LIB=$PWD scrip --run TDump_driver.sno </dev/null )
```

Three consecutive armed runs produced **three different outputs** (md5 `5ab095a4` / `ca281a08` / `475262cd`); the default arm produced one md5 across all 40 runs measured. A serial (`--jobs 1`) `beauty_suite` A/B repeated 3× armed and 2× default confirms `TDump_driver` is the **only** unstable row in the suite, so this is not scorecard parallelism.

**The failing site is the arm's own shape.** `TDump.sno:35`:

```
TDump0         t(x)           POS(0) ANY(&UCASE &LCASE)
+                             (SPAN( digits &UCASE '_' &LCASE) | epsilon) RPOS(0)   :F(TDump1)
```

A **SPAN inside an ALT arm** — the exact leaf-suspension construct `leaf_frame_candidate()` admits and re-homes. Armed, the match **spuriously FAILS**, so control reaches `TDump1` (`t = '"' t(x) '"'`) and the tree prints `("Name")` where the oracle prints `(Name)`. rc=0 throughout. **No crash, no signal, no diagnostic — a different answer, and a different one run to run.**

⛔ **This is a WORSE class than the one the arm cures.** s170 argued the flip's value is that it kills a wild write reachable from ordinary SNOBOL4. It does — 13 times over. But it also converts one green program into a nondeterministic wrong answer, and a wrong answer that varies run to run is precisely what the corpus discipline exists to prevent: a `rc=139` announces itself on every run, while this passes 2 times in 10 and would be re-graded "flaky" by anyone who did not know to set `ulimit -s unlimited`.

**MINIMISATION FAILED INSIDE THE TIME BOX (stated, not hidden).** Per the END-OF-CONTEXT LAW I minted rather than hunted. The bare statement — `t POS(0) ANY(&UCASE &LCASE) (SPAN(digits &UCASE "_" &LCASE) | epsilon) RPOS(0)` with `t = "Name"` — is **green in both arms**, oracle `bare`, and stays green behind **30** and **80** padding assignments under unlimited stack. So coordinate magnitude alone does not arm it; the missing ingredient is something else `TDump_driver` carries (recursion via `TLump`/`TDump`, `$x` indirection, the TREE datatype, `GetLevel()`). **The next seat starts from `TDump_driver` + the recipe above, not from scratch**, and ASM-DIFF-FIRST applies: `TDump.sno` is itself a `.s` mover, so the passing-vs-failing `.s` pair is one `--compile` per arm.

## WHAT ELSE WAS MEASURED, AND CAME BACK CLEAN

- **Named gates.** `test_gate_clobarm.sh` **1/5 → 2/5** (the cured row is the only `rc=139` row; the other three reds are `parse fail`, a different defect, unmoved) · `test_gate_udc.sh` **23/0 in BOTH arms**, unchanged (seat8 read 27/0 — other seats moved the denominator, not the arm).
- **The other six frontends.** `test_smoke_{icon,prolog,snocone,rebus}.sh` are **byte-identical between arms** (Icon 14/14 m3 + 14/14 m4; Prolog 3/5 both modes; Snocone 4/1; Rebus 4/0). The emitter is shared, so this was worth proving rather than assuming.
- **Beauty.** `beauty.sno` is a `.s` mover, and its self-host output is **identical in both arms** (278 bytes, rc=0, `DIVERGE` either way). The arm neither helps nor hurts the M1 wall.
- **The 7 `corpus/benchmarks/snobol4/demo/` rows my first mover-grader flagged are instrument noise, not movers** — those programs print `iters:`/`ms:` and **differ run-to-run within a single arm**; the scorecard's `norm=ms` deletes those lines and grades them identically. Recorded because a seat re-running my grader will see the same 7 and should not re-derive it. (My grader's stdin glob `*/snobol4/demo` also matched the *benchmarks* tree, which has `.dat` not `.input`; the failed redirect produced two empty files that compared "different". Fixed before the numbers above were taken — an instrument that manufactures movers is the s33 class, and it manufactured 7 here before it was caught.)

## ⛔ WHAT I DID NOT DO, AND WHY

**I did not flip.** The ruling's own condition is *"flip if clean"*, and the sweep it mandated is what proved it is not. Landing it would ship a nondeterministic wrong answer into the default arm to cure 13 crashes — a trade only Lon/HQ can price, not a seat. The flip edit was written to the house idiom (`(e && *e == '0') ? 0 : 1`, the KW-6/fz3 precedent) with its comment, measured, and then **reverted**; `sn4_span_frame()` at `emit.cpp:2316` is byte-for-byte as it was, default OFF.

**I did not touch OWED item 2** (`SCRIP_CONST_NEST` becoming the default, `sno_kw_nest_ok()` collapsing to `!sno_kw_chase(nm, 0)`). It is explicitly gated on this flip — `lower_snobol4.c:1342` says so in its own comment — so it stays blocked.

## THE QUESTION ROUTED TO HQ (queue row `span-frame-flip`, question box)

The ledger is 13 cures against 1 nondeterministic wrong answer, and the wrong answer is inside the arm's own class. Three dispositions, HQ's call:

1. **Hold the flip** until `TDump_driver` is root-caused and fixed — the arm then flips as a strict improvement. (My recommendation: the counterexample is in the cured class, so it is likelier a defect *in the re-homing* than an unrelated collision, and fixing it may widen the cure rather than merely unblock the flip.)
2. **Flip anyway and carry `TDump_driver` as a known-red**, on the argument that 13 crashes outweigh one wrong answer. ⛔ This trades a self-announcing failure for a silent one and I would not take it without Lon.
3. **Flip narrowed** — admit fewer leaf ops, or decline the leaf class `TDump` hits, so the cure lands without the counterexample. Needs the root cause first, so it reduces to (1).

## RE-PROOF DISCIPLINE APPLIED

Every claim here is from ONE pristine tree at ONE commit, driver and `out/libscrip_rt.so` built together (the s149 mixed-pair law: a fresh driver on a stale `.so` invents movers). Both arms of every board ran against that same pair, differing only in the env var. The `TDump` result was re-measured four ways before it was believed: parallel board (`--jobs 8`), serial board (`--jobs 1`) repeated 3× armed and 2× default, 10 direct runs per arm at each stack limit, and a 3-run md5 comparison — and the first, contradictory reading (10/10 identical md5s in both arms) was **wrong because I had not set `ulimit -s unlimited`**, which is exactly the mistake that would have let this flip land.

## ⭐⭐⭐ ADDENDUM — TWO-SEAT CONVERGENCE, FOUND AT THE MERGE (seat4's s172, pushed while this seat was sweeping)

Seat4's `claws5-m4-sig11` cursor, landed concurrently, predicted this blocker **from the asm alone and from the opposite direction**:

> *"Defect A's severed unwind wires are unfixed and untracked, and **arming SPAN_FRAME will HIDE them** — `n21_match_arbno_af` emits `cmp r14d,eax; jmp …_pos_β` with its conditional recede `jne n26_match_span_β` DROPPED (a dead compare) … **Wrong-answer risk on the ARBNO-RETREAT path; needs its own witness** (an ARBNO over a multi-element ALT arm that must FAIL and retreat)."*

**`TDump_driver` is that witness.** Its armed failure is exactly a retreat-path wrong answer: the match spuriously FAILS and the `:F(TDump1)` branch runs, which is why the output is *quoted* rather than crashed. Seat4 reasoned forward from a dropped conditional recede to "wrong-answer risk on retreat"; this seat measured a nondeterministic wrong answer on retreat and traced it to a leaf on an ALT arm. Neither of us had the other's result.

**This changes the disposition question's shape, and in HQ's favour on the value side.** Seat4 also raises the cure ledger — *"the flip is worth more than s170 priced it … add two D-2 board rows cured in BOTH modes on the real input"* — and this seat's board independently confirms that (all three claws5 programs, not one). So the honest statement is: **the arm cures more than anyone had priced, AND it exposes a live wrong-answer path that was already there and already predicted.** The two are not in tension — a switch that re-homes leaf cells would naturally both fix the wild write and unmask a severed recede that the wild write's crash had been pre-empting.

⭐ **THEREFORE THE FIRST PLACE TO LOOK IS NAMED, NOT GUESSED:** seat4's dropped `jne n26_match_span_β` conditional recede in `n21_match_arbno_af`. That is a concrete, asm-level starting point for the `TDump_driver` root cause, and it costs the next seat nothing to test first. `TDump.sno` is itself a `.s` mover, so the passing/failing pair is one `--compile` per arm (ASM-DIFF-FIRST).
