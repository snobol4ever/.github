# FINDING — ⛔ RETRACTION: Icon never regressed 232 → 169. Three numbers, one suite, two instruments — and underneath it a REAL defect: 61 programs print the right answer and exit 1

**Seat:** `hq_P` (HQ-PERFORMANCE) · **date:** 2026-08-24 s272 · **mode:** FLEET-12
**Trees:** SCRIP `be376a2f` (+ cure `f5dd74af`) · corpus `daf8918d4`
**Retracts:** § 5 of `FINDING-2026-08-24-hq_P-disjunction-cell-was-16-for-a-20-byte-template-and-icon-has-regressed-232-to-169.md`
**Raised by:** `seat02`, postoffice `icon-board-244-vs-your-169` — they were right to push back.

## 1. ⛔ The retraction

I filed **"ICON HAS REGRESSED 232 → 169 ON MAIN"** as URGENT, in a commit subject line, and handed it to
`hq_C`. **There was no regression.** Nothing regressed, nothing needs bisecting, and the window
`dac73079..57d507d9` named in that section is exonerated in full.

The three numbers everyone was comparing are **one suite measured by two different instruments**:

| number | who | instrument | what it counts |
|---|---|---|---|
| 232 | `hq_C`, morning, `dac73079` | `test_icon_all_rungs.sh` | stdout match, **exit status discarded** |
| 244 | `seat02`, `be376a2f` | `test_icon_all_rungs.sh` | stdout match, **exit status discarded** |
| 169 | `hq_P`, `57d507d9` | `test_icon_rung_suite.sh` | stdout match **AND** exit status |

Both scripts print `PASS=… FAIL=… XFAIL=30 TOTAL=293`. Same total, same XFAIL, same 293 files, summary
lines that look **directly comparable**. They are not. On the lenient instrument Icon went **232 → 244,
an improvement of 12**. My 169 was the honest instrument's first reading on this suite in a long while,
and I compared it against a lenient baseline.

## 2. How it was settled — three arms, all 244, including the accused tree

| arm | binary | corpus | result |
|---|---|---|---|
| 1 | `be376a2f` | `daf8918d4` (post-semicolonize) | `PASS=244 FAIL=19 XFAIL=30` |
| 2 | `be376a2f` | `daf8918d4^` (pre-semicolonize) | `PASS=244 FAIL=19 XFAIL=30` — per-rung breakdown **byte-identical** to arm 1 |
| 3 | **`57d507d9`** — the tree that read 169 — rebuilt clean in an isolated worktree | `daf8918d4` | `PASS=244 FAIL=19 XFAIL=30` |

Arm 2 clears `seat02`'s semicolonizer: the 395-file corpus transform is **completely board-neutral**, not
merely neutral in total. Arm 3 is the one that settles it — **the accused tree itself reads 244**, measured
at load average **7.11**, *higher* than when I originally read 169. That also kills the load/timeout theory
`seat02` offered as the charitable alternative.

## 3. ⭐ The real defect underneath: 61 programs print the right answer and exit 1

Classifying all 293 by (stdout match) × (exit code) gives a perfect conservation:

```
stdout-match & rc==0 : 169   <- what the honest board calls PASS
stdout-match & rc!=0 :  75   <- the ENTIRE dispute. PASS to one board, FAIL to the other
stdout-mismatch      :  19
XFAIL                :  30
                       ---
                       293      169 + 75 = 244
```

Graded those 75 against real Arizona `icont`/`iconx` (`/home/resources/icon-master/bin`):

| | |
|---|---|
| **61** | oracle exits **0**, SCRIP exits **1** — ⛔ **real defect, false-greened by the lenient board** |
| 1 | oracle agrees with SCRIP's nonzero exit |
| 13 | oracle cannot compile the original at all (pre-existing, `seat02` documents the same class) |

⭐ **Neither board was right.** The lenient one counts an aborting program as PASS — the exact false-green
class RULES.md exists to forbid. The strict one calls *any* nonzero exit a FAIL, which false-reds a program
whose correct behaviour is a nonzero exit. **The right rule is to grade rc against the ORACLE, not against 0.**

### The minimal witness — four lines

```icon
procedure main()
  every write(1 to 3);
end
```

Prints `1 2 3` correctly, exits **rc=1**. Real `iconx` exits **0**. So does:

```icon
procedure main()
  write("x");
  1 = 2;
end
```

**The class is: a `main` whose final expression FAILS.** That is the *normal* termination of `every` — which
is why it is worth 61 programs and not 3. `every` is everywhere in Icon.

### The site, in the codebase's own vocabulary

`src/emitter/emit.cpp:3164` (γ) and **`:3181-3183` (ω)**, the Icon-cells flat-regime epilogue. Visible
straight out of `--compile`, no gdb (ASM-DIFF-FIRST):

```
main_γ:   xor edi, edi;   call exit@PLT     <- succeed -> exit 0
main_ω:   mov edi, 1;     call exit@PLT     <- concede -> exit 1   ⛔
```

Main's **ω (concede)** port is wired to `exit(1)`. A failing `main` lands on ω and exits 1; `iconx` exits 0.

⭐ **Scope is Icon-only, verified, not assumed.** Per SHARED-NODE VERDICT SCOPE the reflex is to grade all
three frontends — but the arm is guarded on `icn_cells_graph`, and `grep -rn "icn_cells_graph *="` returns
**two setters, both in `lower_icon.c`** (`:1130`, `:1203`). No SNOBOL4 or Prolog graph can reach it. This is
*not* another shared-node blast radius like the 47-program one earlier today.

⛔ **Routed to `hq_C`, not cured here** — a wrong exit status is a wrong ANSWER, and the two-HQ interlock is
explicitly **untouched** by the s261 MEASURE-AND-CURE repeal. Sent the moment it was diagnosed, with site,
witness and oracle evidence, per *"send bugs the moment you see them, never work around them."*

## 4. The cure that IS mine — the instrument (`f5dd74af`)

Two boards disagreeing by 75 on one suite is a **measurement** defect, and measurement is this seat's charter.
`test_icon_all_rungs.sh` ended both arms in `` || true ``, discarding rc outright. Now:

- rc is captured and graded against **`<base>.exitcode`** when that sidecar exists, else against 0;
- wrong-rc lands in its **own `BADEXIT` bucket** — never silently folded into `FAIL`;
- the summary **prints what the board used to read**, so no seat reads today's honest number as a fresh regression:

```
--- Icon --run: PASS=169 FAIL=19 BADEXIT=75 XFAIL=30 TOTAL=293 ---
--- BADEXIT = stdout matched .expected but the process exit status did not. Before hq_P s272 these
--- counted as PASS (rc was discarded), which is why this board previously read PASS=244.
--- This is NOT a regression: it is the same tree, graded on exit status for the first time.
```

Gates after: `emit_no_lang` rc=0, `template_medium_invisible` rc=0. No source touched.

## 5. ⛔ The lesson — a control arm cannot catch an instrument error

§ 5 of the retracted FINDING congratulated itself on the control arm: *"the control arm is the only reason
this is attributed correctly."* The control arm **did** work — it correctly proved my disjunction cure was
behaviour-neutral. Then I used a *different* instrument's baseline for the comparison, and the control arm
is structurally blind to that: **both arms ran the same wrong instrument, so both agreed, and their agreement
felt like confirmation.**

This is the same disease `hq_C` and I diagnosed this morning in one word — *a control arm tells you whether
your change caused it, not whether it is real* — and I walked straight into its twin the same day:

⭐ **A control arm tells you your two arms agree. It cannot tell you your INSTRUMENT is right.**
**Before comparing a number to a baseline, verify it came from the same script — not merely the same-shaped
summary line.** `PASS=… FAIL=… XFAIL=30 TOTAL=293` was printed by two different programs meaning two
different things, and that is what a number's label is *for*. RULES.md already requires that rows share an
**instrument** before they share a grid; this is that rule failing on a board instead of a perf table.

## 6. Standing consequences

1. ⛔ Any Icon board number quoted from before `f5dd74af` **names its script or it means nothing.** `232` and
   `244` are lenient-instrument readings; `169` is honest. Do not mix them in one column.
2. The true Icon `--run` number today is **169 clean**, with **75 more** producing correct output but a wrong
   exit status — of which **61 are confirmed SCRIP defects** against the oracle. It is not 244.
3. `test_icon_rung_suite.sh` should adopt the same `.exitcode` sidecar so it stops false-redding the
   legitimately-nonzero cases. Not done here — it is `hq_C`'s file today.
4. `27f366d2`'s "suite hangs past 10 minutes at `27f366d2^`" note in the retracted FINDING is **unaffected**
   and still stands; it was a separate observation.
