# FINDING 2026-08-10 (Claude, Opus seat) — `roman.sno` IS TWO DEFECTS, NOT ONE; `SCRIP_AB=0` IS NON-DETERMINISTIC ON RECURSION, SO THE "ARMS IDENTICAL" CONTROL IS INVALID

**Status: INVESTIGATION ONLY. Nothing built, nothing committed, no tree mutated.** A second seat was live in this
container throughout (see §6).

⚠ **MEASUREMENT COHERENCE — CAUGHT AND REPAIRED MID-SESSION.** The concurrent seat rebuilt `scrip`/`libscrip_rt.so`
at **16:19**, part-way through this probe ladder, and committed as `d21b80c5`. The first probe batch therefore ran
against the 15:42 binary and the later batch against 16:19 — the stale-build trap of record (s_2026-07-30 SUBJ-CELL
"BUILD OK"; the 260/57 vs 259/58 incident). **Every number in this document was re-run afterwards as one coherent
set against HEAD `d21b80c5`, binary mtime 16:19, m3 `--run`, N=5 per arm.** All conclusions survived the re-run
unchanged, and `p9_depth3` at AB=0 got *worse* under it (2-element set → **3-element**: `[123]` / `[ZHP] heap
exhausted` / `[]`).

---

## 1. HEADLINE

Three inherited claims are falsified, and one new pre-existing defect class is convicted.

1. **`roman.sno` is not an AB=1 defect with AB=0 as the good arm.** BOTH arms fail. AB=0 fails on **336 of 345
   lines**; AB=1 on **345 of 345**. The prior cursor recorded "AB=0 and `.ref` say `1 -> I`" — true only for the
   first 9 lines, which is exactly the range where the correct answer is indistinguishable from the bug.
2. **`SCRIP_AB=0` is NON-DETERMINISTIC on recursive program-defined functions.** N=5 per arm on three minimal
   probes: AB=0 returns a 2-element output set every time — the correct answer OR null, and in the enclosing-function
   shape, a fatal `[ZHP] heap exhausted` abort or SIGSEGV. **AB=1 is deterministic and correct on all of them.**
3. **Therefore GOAL-SNOBOL4-RTX §19's honest-kill-switch argument does not hold for recursive programs.** It rests on
   "(i) `SCRIP_AB=0` IS the fallback arm (legacy path, proven green throughout)" and "(iii) AB=1 vs AB=0 output
   identity across the DEFINE-bearing corpus — 8/9 arms-identical". Against a non-deterministic control, N=1 identity
   is a coin flip. This is precisely the `160_pat_alt_inner_gen_resume` class ARCH §7 step 3 warns about at length,
   arriving in the AB axis instead of the RTX-gate axis: *"a recorded pass is luck, not evidence."*

Corollary, by ARCH §7 2b's own discrimination rule (gate-OFF *is* the fallback, so instability visible with the
fallback selected cannot have been caused by the port): **the AB=0 defect is PRE-EXISTING and not attributable to
RTX-FUNC-1/-2.** The prior cursor's "PRE-EXISTING (proven vs parent commit)" verdict survives — but the defect is
in the legacy arm, not the ported one, and it is worse than recorded.

**On the merits, AB=1 is strictly better than AB=0 on every probe here.** That is a point in RTX-FUNC's favour that
the record currently does not carry.

---

## 2. THE ORACLE IS SOUND — `.ref` VALIDATED, NOT ASSUMED

`/home/claude/x64/bin/sbl -b roman.sno` vs `roman.ref`: **345 lines, zero differing.** The `.ref` is current and the
divergences below are ours, not stale baseline. (Ruling out the stale-artifact class before spending the session.)

`roman.sno` is **self-contained**: no `-INCLUDE`, no input read. The "9 DEFINE-bearing programs mismatch identically
in both arms = `-INCLUDE`/input-driven harness artifact on `</dev/null>`" explanation **cannot apply to it**. That
bucket needs re-examining; at least one of its members is a real bug.

---

## 3. THE TWO DEFECTS, SEPARATED

`roman.sno:26` is the caller: `TEST  OUTPUT = I ' -> ' ROMAN(I)`.

| line | REF | AB=0 | AB=1 |
|---|---|---|---|
| 9 | `9 -> IX` | `9 -> IX` | `9IX` |
| 10 | `10 -> X` | `10 -> ` | `10` |
| 11 | `11 -> XI` | `11 -> I` | `11I` |
| 100 | `100 -> C` | `100 -> ` | `100` |

**Defect R (recursion-result loss), both arms:** the value of the recursive `ROMAN(N)` in
`ROMAN = REPLACE(ROMAN(N),'IVXLCDM','XLCDM**') UNITS` is lost; only `UNITS` survives. Invisible for N≤9 **because at
N≤9 the recursive call legitimately returns null** — the correct answer and the bug coincide. First visible at N=10,
which is exactly where AB=0's diff starts (`10,345c10,345`).

**Defect L (caller-literal loss), AB=1 only:** `' -> '` is destroyed. This is the one already on record.

The two are independent: p8 below carries the literal across a non-recursive call and is green in both arms.

---

## 4. PROBE LADDER (RULES.md "cheapest discriminating experiment", before reading any code)

Probes in `/tmp/claude_rtx_probes/`. Every one validated against SPITBOL first.

| probe | shape | ORACLE | AB=0 | AB=1 |
|---|---|---|---|---|
| p1_plain | `X = F()` | `[AB]` | `[AB]` | `[AB]` |
| p2_builtinarg | `X = REPLACE(F(),…)` | `[AB]` | `[AB]` | `[AB]` |
| p3_concat | `X = F() 'tail'` | `[ABtail]` | `[ABtail]` | `[ABtail]` |
| p4_nested | non-recursive 2-level call | `[in+K]` | `[in+K]` | `[in+K]` |
| p8_lit_nonrecur | literal + call, inside a function | `12 -> IN` | `12 -> IN` | `12 -> IN` |
| p5_recur | recursive, top level, depth 2 | `[12]` | **{`[12]`,`[]`}** | `[12]` |
| p9_depth3 | recursive, top level, depth 3 | `[123]` | **{`[123]`,`[]`}** | `[123]` |
| p6_infunc_lit | recursive, called inside a function | `12 -> 12` | **{partial, `[ZHP]` abort}** | `12 -> 12` |
| **p10_gotoloop** | **roman's exact shape** | 4 lines correct | **abort / SIGSEGV 3/3** | **recursion lost, deterministic** |

Bracketed sets are the **N=5 distinct-output sets**, not single runs.

**The call shape is exonerated.** p1–p4 and p8 are green in both arms: a call result survives assignment, builtin
argument position, concatenation, nesting, and a caller literal. **Only recursion breaks.**

---

## 5. `p10_gotoloop.sno` — THE MINIMAL REPRODUCER (12 lines, deterministic at AB=1)

```
	DEFINE('G(N)U')	:(G_END)
G	N RPOS(1) LEN(1) . U =	:F(RETURN)
	G = REPLACE(G(N),'i','I') U	:S(RETURN)F(FRETURN)
G_END
	DEFINE('T(I,J)')	:(T_END)
T	OUTPUT = I ' -> ' G(I)
	EQ(I,J)	:S(RETURN)
	I = I + 1	:(T)
T_END
	T(9,12)
END
```

ORACLE `9 -> 9 / 10 -> 10 / 11 -> 11 / 12 -> 12` · AB=1 `9 -> 9 / 10 -> / 11 -> / 12 -> ` (3/3 identical) ·
AB=0 `[ZHP] heap exhausted` abort ×2 and SIGSEGV ×1 in 3 runs.

**The discriminating ingredient is repetition inside ONE activation, not depth.** p6 is the same nesting and the same
depth-2 recursion and is GREEN at AB=1; p10 differs only in that `T` loops via `:(T)` back to its own entry label.
Per Ch.8 that is a **goto within the existing activation, not a new one** — SPITBOL creates an activation on *call*,
and the manual is explicit that a function body is just "a statement label with the same name as the function", with
no END and no implicit re-entry. So `G` is called four times inside a single `T` frame.

The first call `G(9)` bottoms out immediately (`N` becomes null, recursive call fails-returns via `:F(RETURN)`) and
is **correct**; every later call loses its non-null recursive result. **Live hypothesis for the next seat: a call
whose recursion bottoms out leaves per-activation state unreset for the following call in the same frame.** Stated as
a hypothesis, not a conviction — it has not been through the monitor.

---

## 6. WHAT WAS NOT DONE, AND WHY

RULES.md mandates monitor-first for divergence hunting. **The monitor was not run, and no fix was attempted**, because
a second seat held **uncommitted edits in `bb_func_activate.cpp` and `bb_call_proc_staged.cpp`** — the files this goal
file marks NOT-CONCURRENCY-SAFE with "Lon routes the seat" — and was actively building and smoking (`/tmp` writes
15:23–15:47; `.so` and `scrip` rebuilt 15:42). Building would have clobbered their `.so` mid-measurement; `git stash`
would have taken *their* work, which is exactly how `refs/stash` was destroyed in the s_this+3 incident. My own
`/home/claude/work` clone was deleted underneath me between 15:13 and 15:49.

**Measurement honesty:** m3 numbers here are trustworthy despite the dirty tree, and this was verified rather than
assumed. `x86_load_got` emits `48 B8 <imm64>` under `MEDIUM_BINARY` — byte-identical to the `movabs` it replaces — so
the `bb_func_activate.cpp` edit is a provable BINARY no-op. The `bb_call_proc_staged.cpp` edit sits on the else-branch
of `MEDIUM_BINARY && fn_cell_bin ? … : …`, i.e. TEXT-only unless `fn_cell_bin` is null, a case already fatal before
the edit.

**Unpaid: the m4 arm.** Everything here is `--run` only.

---

## 7. UNSOLICITED, FROM READING THAT SEAT'S DIFF — LIKELY m4 AB=1 SEGV ROOT CAUSE

Both monitor taps in `bb_func_activate.cpp` emitted `movabs rax, <baked host address of g_monitor_bin>` followed by
`mov rax, [rax]` **before** the `test`/`je` guard. In BINARY that address is valid — same process. **In TEXT the m4
binary is a different process, so it is dereferenced unconditionally on every activation.** That is a SEGV on every
m4 AB=1 function call and it accounts for the top blocker completely. Their `x86_load_got` swap fixes it.

Their companion fix adds the missing `mov rax,[rax]` to the TEXT arm of `bcps_det_arm()` (the BINARY arm already
dereferenced `fn_cell`; the TEXT arm jumped to the cell's *address*). They landed both as `d21b80c5`, "m4 AB=1 SEGV
FIXED — the TEXT arm of the fn_cell transfer was missing its deref".

⛔ **I RAISED A CAVEAT AGAINST THAT FIX AND IT IS WRONG — RECORDED SO NOBODY INHERITS IT.** I argued the fix might be
unreachable because `corpus/benchmarks/snobol4/func_call.s` shows the call site taking the legacy
`call rt_proc_open_fn@PLT` → `jmp rax`, with zero `@GOTPCREL` and zero `movabs` in the file (RTX-FUNC-4's symptom:
SCC not firing in m4). **That artifact was regenerated at the AB=0 default** — this file's own s_this+2 cursor says
the AB tail emits 0 occurrences at default — **so it is structurally incapable of describing what AB=1 emits.** I
read an AB=0 artifact as evidence about an AB=1 path. Same class as the stale-`.s` census warning in the s_this+3
addendum, and I walked into it one screen after quoting it.

⚠ **What does survive is an attribution hazard, not a correctness objection.** `d21b80c5` carries **two independent
BOTH-MEDIUM defects** — the `fn_cell` missing deref *and* the `g_monitor_bin` baked-host-address deref above — and
the commit message names only the first. Either alone is sufficient to SEGV every m4 AB=1 activation. A future seat
bisecting an m4 regression to this commit will find one named cause and two real ones.

---

## 8. OWED

- Run the monitor on `p10_gotoloop.sno` (12 lines, deterministic at AB=1 — a cheap monitor target).
- **Re-run the "8/9 arms-identical" DEFINE-bearing sweep at N≥4 per arm with an explicit QUARANTINE verdict.** At N=1
  against a non-deterministic control it establishes nothing. Expect more members to move out of the "harness
  artifact" bucket.
- Amend GOAL-SNOBOL4-RTX §19: `SCRIP_AB=0` may not be cited as a kill-switch substitute on recursive programs
  without an N≥4 stability check first.
- Correct the s_this+3 cursor: `roman.sno` is two defects, AB=0 is the worse arm, and AB=1 is correct on every
  synthetic probe including roman's own nesting shape.
- Mint `p10_gotoloop` into the corpus with an oracle `.ref` (slice-9 recipe) — it is a better regression canary than
  `roman.sno`, which conflates the two defects.
- The AB=0 heap-exhaustion/SIGSEGV path is unbucketed and is a **fallback-arm** fatality: it deserves its own rung.

**`handoff_status.sh` is the push truth — NOT this document. Nothing here has been committed or pushed.**
