# FINDING — s211: THE WATERMARK REGRESSION IS TAB/RTAB ONLY, `d79a427a` IS EXONERATED, AND THE BISECT NEEDS `libgc-dev`

**Session:** s211 (2026-07-29) · **SCRIP at HEAD:** `6943f349` · **Goal:** `GOAL-SNOBOL4-RTX.md`
**Headline:** s210 handed over "46 programs fail at HEAD, no culprit asserted." The failure is localized to
**TAB and RTAB — the absolute-cursor BINDING patterns — and nothing else.** `LEN`, `POS`, `RPOS`, literal,
`REM`, `SPAN`, `BREAK`, `ARB` are all green and oracle-identical.
**⛔ NO CULPRIT ASSERTED. The bisect had not converged when this was written.** My one named suspect was
built and **falsified**.

---

## 1. MEASURED — the family isolation

Probe matrix, SCRIP m3 vs SPITBOL x64 oracle, 6-line programs, no `.input` required:

| construct | m3 | oracle | verdict |
|---|---|---|---|
| `X RTAB(2) . V` | **rc=139** | `abcd` | SEGV |
| `X RTAB(2)` (no capture) | **rc=139** *(prints `matched` first)* | `matched` | SEGV |
| `X RTAB(0) . V` | **rc=139** | `abcdef` | SEGV |
| `X TAB(4) . V` | **rc=139** | `abcd` | SEGV |
| `X TAB(4)` (no capture) | **rc=139** *(prints `tab-bare` first)* | `tab-bare` | SEGV |
| `X LEN(2) . V` | 0 `ab` | `ab` | OK |
| `X REM . V` · `X SPAN('abc') . V` · `X BREAK('d') . V` · `X ARB . V 'cd'` | 0 | same | OK |
| `X 'cd'` · `X 'cd' . V` · `X POS(0) 'ab'` · `X RPOS(2)` | 0 | same | OK |
| `OUTPUT = 'abcdef' RTAB(2)` (pattern VALUE, no match) | 0 `PATTERN` | `PATTERN` | OK |

⭐ **THE CUT IS SEMANTIC, NOT INCIDENTAL: the broken pair is exactly the ABSOLUTE-CURSOR BINDING patterns.**
`POS`/`RPOS` are absolute but NON-binding (pure assertions, no cursor movement, no RW data — and `d79a427a`
excluded `POS` from the scratch quad for exactly that reason). `LEN` is binding but RELATIVE, so it restores
the cursor arithmetically (`sub r14d, 2`) and needs no save slot. **TAB/RTAB are the only patterns that are
both absolute and binding, i.e. the only ones that must SAVE and RESTORE the cursor through a frame slot.**

⚠ **The two crash SHAPES differ and both are real:** with `. V` capture, nothing is printed; bare, the
correct output IS printed and the process dies after. Do not treat "it printed the right answer" as partial
success — the bare form is still rc=139.

## 2. MEASURED — what it is NOT

- **NOT the scratch-quad mechanism.** Nine templates reference `x86_scratch_off`
  (`bb_match_{arb,bal,break,breakx,rem,rtab,span,span_var,tab}.cpp`). **Seven work.** Only TAB/RTAB fail.
- **NOT `d79a427a` ("TAB/RTAB granted a 16B cursor-save quad", 2026-07-11) — BUILT AND FALSIFIED.**
  It was the attractive suspect: the only commit touching the SNOBOL4 TAB/RTAB matchers, and named in a
  LATER commit message as the start of a "capture DIFF pre-existing `d79a427a..cca948c5`" range. Built it in
  an isolated worktree: **`047_pat_rtab` → `abcd` rc=0, `TAB` bare → `tab-bare` rc=0.** It is GOOD.
  ⭐ **I am recording my own falsified suspect on purpose.** s210's cursor says a third confident guess here
  is the s209 mistake; this one was measured before it was written down, and that is the only reason it did
  not become the fourth wrong culprit in this diagnosis.
- **NOT the pinned-VA capture cell.** The emitted capture box loads `[0x70000000]` (`RT_PIN_BASE`,
  `RT_CAS_TOP`, the R12-FREE-1 cell). It reads as a wild absolute address and is not — `LEN . V` and
  `REM . V` go through the same cell and pass.

## 3. THE EMITTED SHAPE (recorded for the next session, NOT a diagnosis)

```asm
n11_match_rtab_α:  sub rsp,16 · mov [rsp+48],r14d · … · jle .L → mov r14d,ecx · jmp <capture>α
                                                          fail → add rsp,16 · jmp <prev>β
n11_match_rtab_β:  mov r14d,[rsp+48] · add rsp,16 · jmp <prev>β
n13_match_release_α: … · mov rsp, qword ptr [rsp+32]     ← displacement-addressed rsp RESTORE
```
The α SUCCESS edge leaves the 16-byte carve live across γ (β is expected to pop it later); the FAIL edge and
β each pop it once. `match_release` then restores `rsp` from a *displacement-addressed* slot.
⚠ **STATED AS GEOMETRY, NOT AS CAUSE.** Whether that composition is sound depends on the frame-base
selection, which `FINDING-2026-07-27k` (FLATDISP-8) made **per-graph**: `x86_fb()` returns rbp when pinned,
rsp otherwise, and its point 3 records `FRQB()` suppressing its live rsp bump when pinned **because a
template-local `sub rsp,K` does not displace an rbp-relative read.** TAB/RTAB are the `sub rsp,K` + `FR(off)`
shape that predicate governs. That is the axis I would look at first — **and it is a lead, not a finding.**

## 4. ⚠ WINDOW NARROWED BY A RECORDED NUMBER, WITH THE CAVEAT ATTACHED

`FINDING-2026-07-27k` records SNOBOL4 crosscheck at **`295/294 FAIL=20/19` on 2026-07-27**. HEAD measures
**FAIL=47**. If both are comparable, the regression lands in the last ~2 days of commits, not the 18-day
window I bisected. ⛔ **DO NOT TREAT THAT AS PROVEN: the suite TOTAL differs (295 vs 315), and s209 already
recorded a "recorded-vs-measured board disagreement … Suite-size, not regression" as the FOURTH such event
on this ladder.** Comparing raw counts across sessions is exactly the trap. Verify by testing `0e008a85`
(s197 head) directly — one build — before trusting the narrowing.

## 5. ⭐ ENVIRONMENTAL FACTS THE NEXT SESSION NEEDS (these cost me two builds)

1. ⛔ **COMMITS BEFORE THE GC-U REMOVAL DO NOT BUILD WITHOUT `libgc-dev`, AND
   `install_system_packages.sh` NO LONGER INSTALLS IT.** `REPO-SCRIP.md` correctly says Boehm was removed as
   a dependency at GC-U-4 — but that is a statement about HEAD, and **a bisect runs on commits where it was
   still required.** First build of `d79a427a` died on `gc/gc.h: No such file or directory`. Fix:
   `apt-get install -y libgc-dev` before any bisect. **A doc that is true of HEAD can be false of the
   history you are about to compile — same class as the (a)-rot in RULES' STALE-ORIENTATION rule.**
2. ⛔ **`gdb` CANNOT BE INSTALLED HERE — VERIFIED, NOT INHERITED.** `apt-get install gdb` → rc=100. ARCH §7
   asserts gdb is absent; it now has a measurement behind it. ⇒ RULES' step-3 "single-step until you step on
   the land mine" **has no instrument in this container for emitted code**; the working substitute is
   reading `scrip --compile` output, which is how §3 above was obtained.
3. ⚠ **`scrip` LINKS `libscrip_rt.so`** ⇒ every bisect step costs BOTH `make scrip` and `make libscrip_rt`
   (~9 min on this 1-core box, longer under contention). Budget ~90 min for a 9-step bisect and **do not run
   benchmarks concurrently** — s211 starved its own bisect doing exactly that.
4. ⚠ **`corpus/crosscheck/**/*.s` ARTIFACTS ARE STALE SINCE 2026-04-02** (RULES step 4 scopes `.s` regen to
   the DEMO and BENCHMARK corpora only). They are NOT a usable oracle for current codegen — do not diff
   against them to date a codegen change. Sweep the compiler, never the artifacts.

## 6. THE BISECT, HANDED OVER WELL-POSED

- **GOOD:** `d79a427a` (2026-07-11) — **verified by build+run**, not assumed.
- **BAD:** `6943f349` (HEAD) — verified.
- **Range:** 704 commits, ~9 steps. **Predicate (fast, no `.input`, no oracle needed):**
  `scrip --run corpus/crosscheck/patterns/047_pat_rtab.sno` → rc 0 = GOOD, rc 139 = BAD.
- **Runner:** `/tmp/bisect_test.sh` shape — `make scrip` + `make libscrip_rt`, `exit 125` on build failure so
  unbuildable commits are skipped rather than mis-scored.
- ⭐ **CHEAPER FIRST MOVE:** test `0e008a85` (s197) directly per §4. If GOOD, the range collapses from 704
  commits to ~100 and the bisect drops to ~7 steps.

## 7. WHAT THIS DOES NOT CLOSE

The watermark is still FALSE at HEAD and every RTX rung's absolute gate is still ungradeable. The
three-way ON/OFF/PRISTINE differential remains the substitute that survives a broken baseline (s210).
**This finding narrows the question from "46 programs" to "one pattern family"; it does not answer it.**

---

## 8. ⛔ ADDENDUM (same session, after `git pull --rebase`): THE UPSTREAM FLATDISP FIX DOES **NOT** CLOSE THIS

Mid-session a parallel session pushed SCRIP `30ee3fe6` / `57a7b598` — **"Z4 s8 fix 1: capture-start
regression — FLATDISP parse prefix collision. Unpinned `x86_fr32_prefix()` IS the plain `[rsp + ` spelling,
so raw FORTH-cell operands parsed `XK_FR32` and gained `op_flat_disp` … capture `COND(64)->SAVE(48)`
double-counted the 16"** — and it explicitly claims to close the `d79a427a..cca948c5` range.

**It looked like a direct hit on §3's lead**: same axis (`op_flat_disp` vs a template-local `sub rsp,K`), and
`64`/`48` are the exact offsets in REM's and RTAB's emitted scratch stores. **Rebuilt at `57a7b598` and
MEASURED — TAB/RTAB STILL SEGV:**

| program | rc at `57a7b598` |
|---|---|
| `RTAB(2) . V` · `RTAB(0) . V` | **139** |
| `TAB(4)` bare · `RTAB(2)` bare | **139** (correct output printed first, then death) |
| `LEN(2) . V` · `REM . V` | 0, oracle-identical |

⭐ **SECOND FALSIFIED SUSPECT THIS SESSION, AND THE MORE INSTRUCTIVE ONE: it was not my guess — it was a
LANDED FIX ON THE EXACT AXIS I HAD NOMINATED, WITH MATCHING MAGIC NUMBERS, AND IT IS STILL NOT THIS BUG.**
Had I written §3's lead as a cause instead of a lead, this commit would have "confirmed" it and the real
defect would have been closed as fixed while 46 programs kept failing. **The `sub rsp,K` + `FR(off)` shape
evidently hosts MORE THAN ONE defect; sharing a mechanism class is not sharing a bug.**

⇒ **BISECT ENDPOINTS UPDATED: GOOD `d79a427a` (verified) · BAD `57a7b598` (verified, this addendum).**
⚠ And note what this does to §4's narrowing: the upstream fix landed AFTER `FINDING-2026-07-27k`'s
`FAIL=20/19`, so that count cannot be reconciled with `FAIL=47` by pointing at this commit either.
