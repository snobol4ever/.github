# FINDING — hq_P: MILESTONE 1 IS NOT BROKEN. `board_beauty_m1.sh` reads 0/10 in both modes because it diffs SCRIP's CORRECT output against an ORACLE ERROR MESSAGE — beauty.sno is no longer a program SPITBOL can compile

**Date:** 2026-08-23 · **Seat:** hq_P · **Found:** while A/B-ing an unrelated codegen change (fence0) against the full gate ladder on merged HEAD.
**Class:** the RULES.md-named worst case — *"AN ORACLE THAT ANSWERS WHEN IT SHOULD REFUSE IS WORSE THAN A MISSING ONE."* A missing oracle gives a table you have been warned about; a **refusing** oracle whose refusal text is diffed as if it were output gives a full, plausible, entirely false all-RED board on the project's flagship milestone.

## 1. The measurement that matters

**MILESTONE 1 HOLDS, BOTH MODES, AT MERGED HEAD** (`60e3419e` + the fence0 cure, `make pristine`, RT_OPT `-O0`):

| arm | result |
|---|---|
| m3 `./scrip beauty.sno < beauty.sno` | rc=0, **41,492 bytes — `cmp` byte-identical to the beauty.sno INPUT FILE** ⭐ FIXED POINT |
| m4 (`--compile` → gcc -no-pie → run) | rc=0, **41,492 bytes — byte-identical** ⭐ FIXED POINT |

That is Lon's s117 DoD item 2 verbatim: *the checked-in beauty.sno is ITS OWN ORACLE; beautifying it must be the identity; no md5 is ever pinned.* Both modes satisfy it today. ⛔ The size is **41,492**, not the 40,971 older notes quote — because **beauty.sno itself changed** (the `beauty-cn-convert` promotion). Under a no-md5-pinned rule that is not a discrepancy; the file is the oracle and it moved.

## 2. What the board actually does, and where it breaks

`board_beauty_m1.sh` feeds increasing prefixes of beauty.sno to beauty.sno and judges each rung against **`sbl -bf` run on the same input** (`SBL="$S4A/x64/bin/sbl"`, line 43/59). That judge was correct when beauty.sno was portable SPITBOL. It is not any more:

```
beauty.sno line 9:   &USER_DECLARED_CONSTANTS  =  1
oracle:  sbl -bf beauty.sno  →  rc=0, 393 bytes of ERROR TEXT:
         keyword / in file .../beauty.sno / in line 10
SCRIP :  rung 1 (a 1-line comment) → the correct IDENTITY, 109 bytes
diff   →  DIFF, and identically for all ten rungs
```

The `&`-constant namespace (`&USER_DECLARED_CONSTANTS`, HQ-61's keyword-space split, promoted by `beauty-cn-convert`) is a **SCRIP extension stock SPITBOL has no answer for**. So the oracle refuses the *program*, at line 10, before any input is read — and because it exits **rc=0** while printing its complaint to **stdout**, the harness's `orc` check passes and 393 bytes of error text become "the expected answer". Every rung then diffs, including the 1-line rung, which is the tell: a real codegen regression does not break a lone comment line.

⭐ **This is the exact shape hq_C retracted a claim over on 2026-08-23** (`FINDING-…-hq_C-RETRACTION-the-four-false-green-refs-were-my-oracle-mistake.md`): reading an oracle's *refusal* as its *output*. Same day, same class, opposite sign — there false-GREEN, here false-RED.

## 3. What this invalidates

- ⛔ **Any "M1 regressed" claim resting on this board is unsupported.** PLAN.md's HQ-CORRECTNESS row still carries `C-0: MILESTONE 1 MODE-3 REGRESSED — beauty m3 emits 278 bytes vs the 40,971 fixed point`. Whatever was true when written, **the measured state today is 41,492 bytes byte-identical in BOTH modes.** Re-verify before spending a seat on it.
- ⛔ Any seat handed "beauty is red" from this board is being sent after a defect that is not there — the precise cost the false-signal law exists to prevent.
- ✅ Unaffected: the corpus runner (`test_corpus_snobol4.sh` 360/361 both modes, judged against `.ref`s, not this path) and every fence0 measurement in the sibling FINDING (crash cures, not oracle diffs).

## 4. The cure (row `m1-board-judge-is-a-refusing-oracle`, minted this session)

1. **The full-file rung's judge is the INPUT FILE** — that is the ruled DoD, needs no oracle at all, and is the rung that actually certifies M1. Use `cmp` against `beauty.sno`.
2. **Prefix rungs must either drop the SPITBOL judge or grade a portable witness.** A prefix of a `&`-constant program is not SPITBOL-gradable in principle. Options: keep the ladder but judge each prefix against the *self-host identity property*, or keep a frozen pre-CN `beauty_classic.sno` beside it purely as the oracle-gradable ladder.
3. ⛔ **REFUSE, NEVER DIFF.** The harness must detect that the oracle did not produce beautified output (rc, stderr, or an error-shape sniff) and exit **2 UNPROVEN** per `lib_gate.sh` — never 1 VIOLATION. `lib_gate.sh` already gives three exit codes for exactly this; this board predates its adoption.
4. Negative-test by injection, per V2-5.

## 5. General lesson worth keeping

**When a program acquires a language extension, every oracle-graded harness pointed at it silently changes meaning.** The `beauty-cn-convert` promotion was correct and landed with its own verification; nothing in that work was wrong. What was missing is that *promoting a program out of the oracle's dialect must retire or re-point every judge that grades it* — the same provenance discipline the `.ref` sweep applies to files, applied to harnesses. A grep for other boards judging beauty against `sbl` is the obvious follow-on and is named in the row.
