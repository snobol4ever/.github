# FINDING-2026-07-30 — ICN-RTX-20: THE CORPUS HAS NO RUN PHASE, AND `str_concat_d` BAILS 80,000 OF 80,000

**Session s220-ICN. Lon grant: "All your choices."** Ladder: `GOAL-ICON-RTX.md`. Contract: `ARCH-ICON-RTX.md`.
`-O0` throughout (O2-DIRECTED-ONLY); every timing first-round-discarded per s201/s202.

⛔⛔ **THE DEFECT IS THE WORKLOAD SET, NOT THE LADDER'S PREMISE.** One cause explains every null this
ladder has recorded — and the fix hands it the largest confirmed target it has ever had.

⚠ **THIS DOCUMENT RECORDS A CONCLUSION I DREW AND THEN FALSIFIED MYSELF, IN ONE SESSION.** §1–§3 led me
to draft a recommendation to PARK the ladder. §4 is the control I ran against my own weakest caveat, and
it reversed the recommendation. **The draft is not preserved; the method is: state the weakest point of
your own conclusion as a named experiment, then RUN it before publishing.** Had I stopped at §3 I would
have committed a confident, well-evidenced, wrong strategic call.

---

## 1. FOR THE BENCHMARK CORPUS, WALL TIME IS ~100% COMPILE

Mode 3 compiles and runs in one process. Splitting the phases:

| program | `--compile` only | `--compile` + `--run` |
|---|---:|---:|
| trivial (3 lines) | 7 ms | 6 ms |
| queens | 19 ms | 17 ms |
| tgrlink | 37 ms | 32 ms |
| concord | 19 ms | 18 ms |

**`--compile` costs the SAME AS OR MORE THAN `--run`** (it additionally writes the `.s`). ⇒ **The run
phase of every corpus benchmark is at or below the noise floor.** That corpus is what s218's ranking,
every A/B, and every gradeability judgement on this ladder were derived from.

⭐ **s211's "gradeability floor" and RTX-19's "31 ms window" were never run-phase windows — they were
COMPILE windows.** The floor was not a measurement limitation; it was the absence of the measured thing.
⚠ s218 excluded `ast_attr_int`/`ast_attr_leaf`/`ast_stmt_new` as a "COMPILE-PHASE CONFOUND." Those were
the only rows measuring the phase that dominates the corpus. **The confound was the signal.**

## 2. AN INTEGER LOOP HAS A RUN PHASE BUT DOES NOT ENTER THE RUNTIME

`every i := 1 to N do s := s + i` — compile CONSTANT at 6 ms, run **17 ms → 52 ms at N→4N (4.18×**, a
clean 0(d) scale). Arm census at N=2,000,000, i.e. **2 million iterations: ONE runtime entry total**
(`rt_proc_value` ×1). Cause, read straight out of the emitted code:

```
mov  eax, dword ptr [rbp + 304]   ; descriptor type tag
cmp  eax, 6                       ; integer?
jne  .Lx32_0                      ; ONLY then call the runtime
.Lx32_1:                          ; FAST PATH — inline 16-byte copy, NO CALL
.Lx32_0: call rt_coerce_num2_d@PLT   ; the COLD arm
```

⭐ **s216's 0(g) SUB-RULE, INVERTED AND THEREBY COMPLETED.** s216: *"UNGUARDED CALL ⇒ CHEAP ARM
DOMINANT"* (held twice). The dual: **GUARDED CALL ⇒ THE CALL ITSELF IS THE COLD ARM.** Together they
predict arm liveness from one grep of the emitting template — no build, no interposer, no rebuild.

## 3. ⇒ THE DRAFTED (WRONG) CONCLUSION

From §1+§2 I concluded the C runtime is off Icon's hot path in *both* phases, that this retro-explained
RTX-19's zero delta, RTX-8d's and RTX-9's refusals, s213's dead arms and the six count-as-cost
falsifications, and that the ladder should be PARKED in favour of compile-phase and emitter work. I also
falsified one candidate cause of the ~6–7 ms compile floor: dynamic linking of the 23 MB
`libscrip_rt.so` is only **483,109 cycles (~0.16 ms)** by `LD_DEBUG=statistics` — the size is `-g` debug
info, lazily mapped, and is NOT the cost.

**My own stated weakest point: "measured on integer-typed loops; a string/table-heavy hot loop should be
measured before generalizing."** So I measured it.

## 4. ⭐⭐⭐ THE CONTROL REVERSES IT: A STRING/TABLE LOOP IS 95% RUN PHASE AND BAILS TO C 80,000 TIMES

`s := s || "x"` plus a table insert, 40,000 iterations:

**compile 7 ms · run 160–208 ms** ⇒ **the run phase is ~95% of wall time** — the exact inverse of §1.

```
SYMBOL              ENTRIES  BAILED_C   COMMITS  VERDICT
rt_str_alloc         119999         0    119999  asm handles 119999
rt_agg_alloc          40098         1     40097  asm handles 40097
rt_assign_var         40000        97     39903  asm handles 39903
str_concat_d          80000     80000         0  ⛔ VACUOUS HERE — asm never commits
rt_gcheap_alloc          98     29582    -29484  ⛔ VACUOUS HERE — asm never commits
rt_size_d                 1         0         1
rt_proc_value             1         0         1
```

**⇒ THE LADDER'S PREMISE IS SOUND. ITS WORKLOAD SET WAS NOT.** Icon's C runtime is entered heavily — by
string and aggregate work, which the benchmark corpus barely exercises and which neither the integer
loop nor `--compile`/`--run` splitting could see.

## 5. THE ACTIONABLE RESULT — RTX-17 IS CONFIRMED, WITH A GRADEABLE WINDOW

**`str_concat_d`: 80,000 entries, 80,000 bails, ZERO commits, inside a 160 ms window that is 95% run
phase.** This independently confirms s218's outbound message to SN4-RTX (*"two of your landed ports are
being declined on hot paths"*) with the two things that message lacked: **a workload where the run phase
dominates, and a COMMITS column proving the bail is total, not partial.**

⛔ **It is SN4-RTX's symbol** (`DONE:SN4-RTX:rtx_str.S`, STR gate) and I did not touch it. §7 rule 2
requires Lon to re-assign. **This finding is the case for that re-assignment.** Second target on the same
evidence: **`rt_gcheap_alloc`, 29,582 bails against 98 entries.**

⭐ **AND THE INSTRUMENT DEBT IS NOW NAMED: THIS LADDER HAS NO REPRESENTATIVE WORKLOAD SET.** s218's
"measure once" queue is a COMMITTED ARTIFACT derived from 16 workloads that are ~100% compile ⇒ **the
queue does not rank run-phase cost and must be re-derived on run-phase-dominant programs.** Its rank 1,
`rt_ws_alloc`, is the proof: probed twice (RTX-19's elide, this session's poison) and null both times.
**Building `corpus/benchmarks/icon/` programs whose run phase dominates — string, table, list, set, scan
— is the prerequisite rung for every future `.S` port on this ladder** (⇒ **RTX-21-ICN**).

## 6. ALSO LANDED THIS SESSION (separate commits)

- **RTX-19 debt DISCHARGED.** Its commit recorded execution as UNPROVEN and owed a poison build. Done:
  counter shows the elided branch fires **184–521 times per program** across 9 benchmarks (execution
  PROVEN), and the **293-program Icon gate is unmoved under a hard `0xAA` payload poison** (`252/11/30`),
  so the elide is live AND correct. It is simply not on a hot path. ⚠ Also found: `micro` and `deal` are
  **nondeterministic in both configs** (3 different hashes in 3 runs) — output-md5 differential is not a
  valid instrument on them, and RTX-19's own A/B used that class of program.
- **RTX-18a landed + step 0(c)'s INSTRUMENT IS DEFECTIVE.** The five `g_wsi*` file-statics are now
  `GLOBAL HIDDEN`. s218 diagnosed the block with `nm out/libscrip_rt.so` → lowercase `b`, read as
  "file-static" — but **the linker localizes hidden symbols, so on a linked `.so` `static` and `hidden`
  are indistinguishable** and that command returns identical output before and after the fix. Proven with
  a same-TU control: on the `.o`, the five read `B`/`OBJECT GLOBAL HIDDEN` while still-static
  `g_hp_arena` reads `b`. ⇒ **0(c) MUST be run on the `.o`, never the `.so`.** Contract amendment owed.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## 7. ⭐⭐⭐ THE 80,000 BAILS DECOMPOSED: TWO CAUSES, EXACTLY 50/50, AND ONE OF THEM ALREADY HAS A MINTED FIX

**Measured s220 by histogramming the guards inside `c_str_concat_d`** (temporary probe, reverted; tree
verified clean). Read-only on SN4-RTX's `.S` — no ownership breach.

```
[SCPROBE] tot=80000  tag=40000  nullptr=0  SLEN0=40000  csetm1=0  other=0
```

**Each half maps to exactly one source statement in the workload, and the counts equal the loop count:**

| cause | count | asm guard | statement |
|---|---:|---|---|
| **`SLEN0`** — `a.slen==0 \|\| b.slen==0` | **40,000** | `rtx_str.S` *"slen 0 => unknown length, C strlens"* | `s := s \|\| "x"` |
| **`tag`** — either operand not `DT_S` | **40,000** | *"not two plain strings -> null arm"* | `"k" \|\| (i % 97)` — **integer** operand |
| nullptr / cset-`-1` / unexplained | **0** | — | — |

**⇒ FIX 1 — `SLEN0` (50% of bails): THIS IS RTX-16-ICN, ALREADY MINTED, AND IT IS THE LADDER'S KEYSTONE.**
`RTX-CLAIMS.md` minted RTX-16-ICN (*populate `slen`*) as the root cause of RTX-9's refusal
(*"`arr.slen == 0` on 100% of arrivals"*), and it was already known to *"retroactively activate
`rt_size_d`'s dead arms and remove `strlen` in five other languages."* **s220 adds a third independent
symptom: half of `str_concat_d`'s bails.** ⭐ **THREE SYMPTOMS, ONE DEFECT — and the fix needs NO NEW ASM.
It activates asm that is already written, already linked, already gate-green, in three symbols and five
languages.** Nothing else on this ladder has that leverage. ⛔ **It was never prioritized because it was
discovered on the compile-dominated corpus (§1), where no run-phase win could be measured at all.**

**⇒ FIX 2 — `tag` (50% of bails): A MISSING `DT_S || DT_I` ARM, WHICH IS A DESIGN GAP, NOT A BUG.**
`"k" || (i % 97)` — string concatenated with an integer — is among the most common idioms in Icon, and
`rtx_str.S` has no arm for it, so C performs the coercion every time. ⇒ **RTX-23-ICN: integer-operand
concat arm** (`to_int`'s inverse is already asm, so the pieces exist). ⚠ Sequence it AFTER RTX-16: with
`slen` populated the surviving bail population changes, and the arm should be measured against the real
remainder, not against today's 50%.

⭐ **THE ORDER THIS IMPLIES, AND IT INVERTS THE WHOLE LADDER:** the two highest-leverage rungs on
ICON-RTX are now **(1) a C-side descriptor fix that writes no asm** and **(2) a new arm on a symbol
already ported.** Neither is "port a C function to `.S`" — which is every rung this ladder has attempted
and every rung that came back null. **Lon's directive *"just ASM code not C code"* is best served by
making the ASM THAT ALREADY EXISTS actually execute.**
