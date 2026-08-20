# FINDING 2026-08-20 s189 (seat2 `/home/claude2`, Claude Opus 5; queue row `scorecard-oracle-case`, rank 0)

## THE ORACLE FLAG IS A LANGUAGE SWITCH. THE ROW'S PREMISE IS RIGHT AND UNDERSTATED — AND THE CRASH FOUR TREE DOCUMENTS BLAME ON THE SANDBOX IS THIS BUG'S DOWNSTREAM.

**LANDED:** SCRIP `scripts/scorecard_snobol4.sh` — the oracle invocation is now ONE authority, `sbl_flags()`, and it is `-bf` for every suite. The per-suite `beauty_self` flag exception is deleted; only its *input* convention (`in="$prog"`) survives, which is the self-host rule and not a flag.

**MEASURED AT ONE COMMIT — SCRIP `d3251f23`, corpus `d686c91f`, `make pristine`, RT_OPT `-O0`.** Both full boards ran at that same commit deliberately: `origin/main` carried `a2979dc6`, which touches `src/lower/lower_snobol4.c`, so the pull was **held until after both arms**. A compiler moving between arms would have made the delta unreadable.

**⛔ `lon` EXCLUDED BY NAME FROM BOTH ARMS** (RULES.md ABSOLUTE RULES; Lon s186). META is therefore weighted over **12 suites, weight 113, not 118** — *in both arms alike*, so the delta is apples-to-apples. Removing the suite from the script is row `scorecard-drop-lon`'s deliverable and I did not touch the SUITES/weight table.

---

## 1. THE PREMISE IS CONFIRMED, AND IT IS NOT ABOUT LABELS

The brief rests on one witness (labels `Shift`/`shift`). It reproduces exactly. But the case for `-f` does not rest on labels: **SCRIP agrees with `-f` and disagrees with the folding default in THREE independent constructs.**

| construct | witness | `sbl -b` | `sbl -bf` | **SCRIP** |
|---|---|---|---|---|
| names / labels | `Shift` + `shift` | ERROR 217, rc **139** | clean | **clean (m3 AND m4)** |
| special names (p.192) | `output` vs `OUTPUT` | prints **BOTH** lines | prints ONE | **prints ONE** |
| indirect reference (p.182) | `abc` set, then `$('ABC')` | resolves | null | **null** |
| indirect reference (p.182) | `ABC` set, then `$('abc')` | resolves | null | **null** |

Manual v3.7: folding is the **default** (p.23 names, p.28 labels); `-f` turns it off (p.162); and the manual itself names `-f` as the flag to use **"if compatibility with standard SNOBOL4 is desired"** (p.266 note 10). `RULES.md` declares SCRIP **case-sensitive**. Grading a case-sensitive engine against a case-folding oracle scores SCRIP against behaviour it is *required* not to reproduce.

**THE BRIEF'S ARITHMETIC IS OFF BY ONE, AND SO IS seat1's TOOL HEADER.** The SUITES table has **THIRTEEN** rows, not 14. Twelve ran `-b`, one of which is `lon`, so only **ELEVEN** non-`lon` suites actually flipped; `beauty_self` was already `-bf`.

---

## 2. THE SIGSEGV IS THE ERROR-REPORT PATH — NOT THE FLAG, AND NOT THE SANDBOX

The tree has said for months that `sbl -b` SIGSEGVs on `beauty.sno` and treated it as a sandbox quirk. **It is this bug, one step downstream.**

- A **genuine** duplicate label (`shift` / `shift`, both lower) **SIGSEGVs under `-bf` too**. Folding does not crash SPITBOL.
- What folding does is **manufacture phantom duplicate labels**, which then walk into a crashing error-recovery path.
- `beauty.sno`'s `-b` wall is exactly that: `ERROR 217 -- duplicate label` at `semantic.inc(16)`, the `shift`/`Shift` collision.

**AND UNDER `-b` beauty HAS NO STABLE ORACLE AT ALL** (3 runs each, this session):

| arm | rc | bytes | md5 |
|---|---|---|---|
| `sbl -b` ×3 | 139 / 139 / 139 | 1079 | **THREE DIFFERENT** (`b2e66d4be4e7`, `f8315553ef1f`, `8cd7e471883c`) |
| `sbl -bf` ×3 | 0 / 0 / 0 | 40970 | **identical** (`b3f25b24b59e`) |

Same byte count, different bytes — the crash listing carries nondeterministic content. **A board cannot be graded against that.** (seat1 measured the same instability independently at 40971 bytes / a different md5; the one-byte and hash difference is my `printf %s` stripping the trailing newline. The *claim* — unstable under `-b`, stable under `-bf` — reproduces exactly.)

**FOUR DOCUMENTS STATE THE FALSE CAUSE. THREE ARE CORRECTED THIS SESSION** (`RULES.md` §Oracles, `board_beauty_m1.sh:18`, `CLAUDE.md:63`). The fourth, `cmp3_snobol4.sh:31` (*"exits 1 on benign sandbox segfault-on-exit"*), makes a **different** claim (rc=1, not 139) that I did **not** measure — it is NAMED here and deliberately **left alone** rather than "corrected" on inference.

⛔ **AND ONE PROPAGATION FACT THE NEXT SEAT NEEDS: `CLAUDE.md` IS NOT VERSION-CONTROLLED.** It is a per-seat file — nine independent copies (`/home/claude/`, `/home/claude1..8/`), tracked by no repo, so **only my seat's copy is corrected and the other eight still carry the false cause.** `RULES.md` is the tracked authority and its correction *does* propagate; the `CLAUDE.md` line is a digest of it. Any doc fix that lands only in `CLAUDE.md` reaches exactly one seat — HQ owns re-seeding the other eight.

---

## 3. THE BOARD: META 70.2 → 69.9 (Δ **−0.3**)

12 suites, weight 113, 1822 programs each arm.

| SUITE | W | N | SCORE before | SCORE after | UNSCR before→after | Δ |
|---|---|---|---|---|---|---|
| beauty_self | 20 | 1 | 0.0 | 0.0 | 0→0 | +0.0 |
| beauty_suite | 15 | 17 | 97.1 | 97.1 | 0→0 | +0.0 |
| demos | 15 | 22 | 72.7 | 72.7 | 1→1 | +0.0 |
| benchmarks | 10 | 15 | 96.7 | 96.7 | 0→0 | +0.0 |
| bb_probes | 10 | 188 | 100.0 | 100.0 | 0→0 | +0.0 |
| patterns | 10 | 122 | 96.3 | 96.3 | 0→0 | +0.0 |
| crosscheck | 10 | 195 | 99.2 | 99.2 | 1→1 | +0.0 |
| feature_test | 5 | 160 | 97.5 | **94.4** | 1→1 | **−3.1** |
| probes_misc | 5 | 606 | 83.4 | 83.4 | 3→3 | +0.0 |
| csnobol4_suite | 5 | 123 | 32.5 | **27.6** | 1→1 | **−4.9** |
| gimpel | 5 | 84→83 | 39.3 | **39.8** | 135→136 | **+0.5** |
| misc | 3 | 123→121 | 65.9 | **66.9** | 24→26 | **+1.1** |
| **META** | **113** | | **70.2** | **69.9** | | **−0.3** |

**The two "improvements" are not improvements** — `gimpel` and `misc` rise only because programs *left the denominator* into UNSCR. Nothing started passing. **Zero FAIL→PASS transitions in either mode, board-wide.**

---

## 4. ⛔ THE METHOD THAT KEPT THIS BOARD HONEST — AND THE FALSE BOARD IT AVOIDED

The raw A/B diff shows **18** moving programs. **Only 13 are flag movers.** The other **5 are flakes** — programs whose oracle output was byte-identical across a same-flag control arm, so the flag *cannot* have moved them:

`misc/programs/snobol4/parser/cf_goto_computed.sno` (SIG11→SIG5/SIG4) · `misc/programs/snobol4/parser/cf_label_assign.sno` (TIMEOUT→ORACLE_FAIL, oracle timed out under board load) · `probe/fuzz/fz_segv_24.sno` (SIG11→DIFF) · `csnobol4-suite/nqueens.sno` (SIG11→TIMEOUT) · `gimpel/ORBREAK_driver.sno` (DIFF→SIG6)

A two-arm sweep names all 18 as flag movers. **The credit for this is seat1's** (`util_oracle_flag_sweep.sh`, SCRIP `6d4cab2d`): its 3-arm form runs `-b`, `-b` **again as a control**, and `-bf`. My independent run reproduces their split — **same=1719 MOVER=75 FLAKY=28** against seat1's 77/26 (FLAKY is nondeterministic by definition, so the small drift is the measurement agreeing with itself).

**The cross-check is the real instrument:** a board mover whose oracle is byte-identical in all three arms is a flake **by construction**, not by judgement.

---

## 5. ⭐⭐ THE 13 REAL MOVERS ARE **FOUR** CLASSES, AND ONLY ONE IS A "CORRECTION"

The brief predicted *"rows that were passing on a folded name will now fail, and that is a CORRECTION, not a regression."* **That is true of one row in thirteen.** Reporting the other twelve as corrections would be false.

### (a) A GENUINE SCRIP DEFECT, EXPOSED — 1
**`SCRIP/test/snobol4/rung11/1113_table.sno`** — line 30 is `ta = CONVERT(t, 'array')`. Under `-f` a datatype **name string** must be upper-case (p.192, p.199: *"The formal name must be in upper-case (or lower-case if case-folding)"*), so `'array'` is invalid and the oracle raises **ERROR 164**. **SCRIP accepts it and answers `PASS 1113_table (8/8)`.** SCRIP is folding a datatype-name string while being case-sensitive everywhere else.

**⭐ THIS ADJUDICATES QUEUE ROW `datatype-case` (rank 34), WHICH seat1 CORRECTLY SAID COULD NOT BE DECIDED BEFORE THIS RULING.** Minted witness: `DATA('jobj(a,b)')` then `DATATYPE` → `-b` **JOBJ** · `-bf` **jobj** · **SCRIP JOBJ**. With `-bf` as the reference, **SCRIP's `JOBJ` is a bug**, and it is the same mechanism as `CONVERT`'s `'array'`. One class, two faces.

### (b) AN ORACLE BUG WHERE **SCRIP IS RIGHT** — 5 (these are FALSE reds)
`SCRIP/test/snobol4/library/test_{case,math,stack,string}.sno` · `corpus/programs/gimpel/INFINIP.sno`

Under `-f`, **only the all-caps `-INCLUDE` is honored**; `-include` and `-Include` are **silently ignored** (Catspaw drops unrecognized controls) and surface later as **ERROR 022 undefined function** — **and `sbl` exits 0 while printing it**, so the error listing becomes "ground truth". This contradicts the manual verbatim (p.171: *"Controls may be specified in upper- or lower-case, **regardless of the current state of case-folding**"*). **SCRIP honors both cases, matching the manual.** Censused independently: **exactly 18 files** use only lowercase `-include` (9 `csnobol4-suite`, 4 `crosscheck/library`, 4 `SCRIP/test/snobol4/library`, 1 `gimpel/INFINIP.sno`) against 190 using `-INCLUDE`.

⛔ **I DID NOT UPPERCASE THE CORPUS.** Editing 18 corpus programs to accommodate an oracle bug is exactly the anti-pattern seat1 named at s186 — *"Blame the line before editing a corpus program to match our tree."* The corpus is correct; the oracle is not. **Routed, not buried** (see §7).

### (c) A VACUOUS PASS **EXPOSED**, NOT CREATED — 5
`csnobol4-suite/preload{1,2,3,4}.sno` · `csnobol4-suite/longrec.sno`

**`preload1.sno`'s entire source is the 4-byte file `end`.** Its pinned `.ref` says `aa`. Under folding, `end` → `END`, so it is a valid empty program: sbl prints nothing, SCRIP prints nothing, `grade()` matches output-to-**live** and says **PASS — while the pin holds real content that neither engine produced.** All four `preload*.sno` are that same 4-byte file with non-empty pins (`aa`, `aa|bb`, `pa|pb`, `pa|pb`); `longrec.sno` is the same lowercase-`end` shape. **The flip did not break these five. It stopped hiding them.**

### (d) OUT-OF-DIALECT, LABEL ONLY — 2
`csnobol4-suite/setexit2.sno` (lowercase `output`, `setexit(` — SCRIP answers `** Error 5`, which is what a case-sensitive engine **must** do) · `programs/dotnet/1brc.sno` (COMPILE_FAIL→ORACLE_FAIL; SCRIP fails to compile it under **both** arms — only the label moved).

---

## 6. ⭐ THE MECHANISM THAT DECIDES WHETHER A PROGRAM MOVES AT ALL IS **PIN PRESENCE**, AND IT IS VISIBLE IN A MATCHED PAIR

`grade()` passes on `output == pin` **OR** `output == live`, so a pinned program is immune to the oracle flag. The corpus contains a natural control:

| file | pin? | moved? |
|---|---|---|
| `corpus/crosscheck/library/test_{case,math,stack,string}.sno` | **PIN PRESENT** | **no** |
| `SCRIP/test/snobol4/library/test_{case,math,stack,string}.sno` | **NO PIN** | **yes, all four** |

Same four programs, same oracle bug, opposite fates — decided entirely by whether a `.ref` sits beside them. This is why `crosscheck` shows **+0.0** while `feature_test` shows **−3.1**, and it is the honest reason the board's blast radius is small: **2,266 pins are absorbing the oracle.**

---

## 7. ⛔ THREE THINGS THIS ROW FOUND AND DID **NOT** FIX — EACH WANTS A ROW

1. **`include-control-case`** — the oracle silently ignores lowercase `-include` under `-f`, contradicting p.171. 18 files, 5 false reds today. The choice is Lon's/HQ's: uppercase the control word in 18 corpus files (semantically null, a no-op under `-b`, and it masks the oracle bug), or quarantine the class. **Do not let a seat "fix" this by editing corpus on its own initiative.**
2. **`grade-mutual-silence`** — `grade()` scores **two engines producing nothing** as agreement, *even when a pinned `.ref` holds real content*. Proven on `preload1.sno`. Independent of this row, not cured by it, and it inflates PASS counts wherever both engines are silent. Suggested rule: a live-arm match must not count when **both** sides are empty **and** a non-empty pin exists.
3. **`kw-case-keyword`** — **`&CASE` reports 1 while SCRIP behaves as 0.** Measured: `sbl -b` says `&CASE=1` **and** folds (`abc`/`ABC` are one cell); `sbl -bf` says `&CASE=0` **and** does not fold; **SCRIP says `&CASE=1` and does not fold — it contradicts itself.** `probe/kw/kw_defaults.sno` pins `CASE=1`, so **the pin pins the lie.** ⭐ This matters beyond hygiene: those kw probes were the *only* head-to-head evidence anywhere in the sweep that favoured `-b`, and **that evidence dissolves into a SCRIP bug.** `&CASE` must report 0, and the pin must be regenerated **from the live oracle** (this row's own clause), never hand-edited.

**⛔ AND ONE DELIBERATE NON-ACTION:** 52 of the 75 oracle movers are `csnobol4_suite`, a **wholesale lowercase dialect** SCRIP cannot pass under *either* arm. The flag only changes their label (FAIL vs UNSCR) and **UNSCR moves META**. That is Lon's weight knob (HQ-73); seat1's `q-oracle-flag-bf` stands. **I did not redistribute weight and did not drop a suite.**

---

## ⭐ THE GENERALISABLE MOVE

**A harness flag that changes what the ORACLE means is not configuration — it is the definition of the test.** This one sat in a single line, wore a per-suite exception (`beauty_self`) that made it look like a program-specific workaround, and for that reason survived every board, bench and scorecard reading for months while a whole class of results was graded against a language SCRIP is forbidden to speak. **The exception is what hid the rule.** When one member of a family carries its own flags, the question is never "why is that one special" — it is *"what is that flag doing to the other twelve?"*

**Corollary, and it cost seat1 a false board before it cost me one:** *a differential sweep without a same-flag control arm measures nondeterminism and calls it signal.* 5 of my 18 board movers, and 28 of 103 oracle movers, were programs disagreeing with themselves.

**Second corollary:** *when a flip makes rows go red, "correction, not regression" is a hypothesis, not a conclusion.* Here it held for **one** row in thirteen. Five were an oracle bug with SCRIP in the right, five were fake passes losing their cover, and two were relabelling. A number is not a finding until each mover has a named cause.

---

**WITNESSES (scratchpad, not checked in — all reproducible from the two commands below):** `w_case.sno` (labels) · `dup.sno` (genuine duplicate label SIGSEGVs under BOTH arms) · `t_out.sno` (`output`/`OUTPUT`) · `t_ind2/t_ind3.sno` (`$` both directions) · `t_case.sno` (`&CASE` self-contradiction) · `t_data.sno` (`DATA`/`DATATYPE` folding) · `inct/{lower,upper}.sno` (`-include` case).

```bash
bash scripts/scorecard_snobol4.sh run --suites beauty_self,beauty_suite,demos,benchmarks,bb_probes,patterns,crosscheck,feature_test,probes_misc,csnobol4_suite,gimpel,misc --jobs 12 --out <dir>
bash scripts/util_oracle_flag_sweep.sh sweep <dir> 12     # 3-arm; lon-safe by construction
```
