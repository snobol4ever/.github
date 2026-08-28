# FINDING 2026-08-28 hq_C — four of 96 Pascal crosscheck refs are SELF-PINNED, not oracle-derived

**Claim (the filename):** of the 96 banner blocks in `corpus/tests/pascal/crosscheck/`, **91 match the
`fpc -Miso` oracle exactly, 4 do not, and 1 has no oracle at all.** On the 4, the `.ref` matches **SCRIP's
own output**, not the oracle's — they are pinned to the implementation under test.

## Why this was measured

seat04 raised it precisely, and refused to let it resolve on the favorable assumption. Their message:
the crosscheck refs were verified as a **hybrid** — an exhaustive whitespace-only delta-check against the
OLD refs for all 82 affected blocks, plus a direct-fpc spot-check on only **7** of the 82
(`misc:writenl vrec:vrec2 with:with3 ptr:ptr1 set:set2 goto:goto3 rec:rec1`). So 75 blocks rested on
"the delta from the old ref is whitespace-only" — evidence that, as seat04 themselves wrote, **cannot see a
defect shared by both the old and the new ref.** They flagged it rather than assume, and were right to.

⭐ **The sample could not have found this.** None of the 4 bad blocks is among the 7 spot-checked, and no
whitespace-delta check could ever flag them: they are not whitespace, and they did not change in the regen.

## Method

Every block extracted by its `{---- N name}` banner from all 17 `.pas` files and its matching `.ref`
section; each compiled with the **sanctioned invocation** `fpc -Miso` (`lib_oracle_flags.sh` → `fpc_bin()`,
fpc 3.2.2) and run; stdout compared byte-for-byte with the ref block. 96 blocks, no sampling.

⚠️ **My own first pass was wrong and I caught it with the authority, not with judgement.** I invented a
`-O-` flag instead of using the settled oracle invocation. It happened to give the same verdict, which is
exactly why it was dangerous — a wrong instrument agreeing with the right one teaches you nothing and
promotes itself to habit. `32be25c71`'s commit message names `fpc -Miso` as the settled oracle; that is
what the numbers below were produced with.

## Result — 96 = 91 + 4 + 1

| class | count | blocks |
|---|---|---|
| ✅ matches `fpc -Miso` byte-for-byte | **91** | — |
| ⛔ ref matches SCRIP, not the oracle | **4** | `misc:10 constreal` · `misc:32 realwidth` · `stdlib:2 stdlib2` · `stdlib:3 stdlib3` |
| ⚠️ no oracle — fpc cannot compile it | **1** | `pb:1 pb36` |

**All 4 are real-number output formatting**, and the disagreement is not subtle:

| | `writeln(x)` where `x := 3.14159265` | `writeln(1.5)` |
|---|---|---|
| `fpc -Miso` | ` 3.1415926500000002e+000` | ` 1.500000000e+00` |
| SCRIP | ` 3.141592650000E+000` | ` 1.500000000000E+000` |
| **the `.ref`** | ` 3.141592650000E+000` | — |

Two axes differ — **exponent case** (`e` vs `E`) and **significant digits** (17 vs 13) — and on both the ref
sides with SCRIP. ⛔ **A ref that records the implementation's answer cannot fail that implementation.**
This is why the board reads `suites 96/0` while 4 of those 96 are ungraded in the only sense that counts.

`pb:pb36` fails as `Fatal: Unknown compilerproc "fpc_write_text_enum_iso"` — the **crosscheck twin of the
already-documented loose `pb37` exception** (`tests/pascal/KEEP.md` §4). Known RTL gap, not a new defect;
recorded so it is not rediscovered a third time.

## ⛔ What I am NOT ruling, and why it goes to Lon

**I am not asserting fpc is right and SCRIP is wrong here.** ISO 7185 specifies an **uppercase `E`**, so on
exponent case SCRIP is arguably the more conformant of the two, and fpc `-Miso` is visibly inconsistent with
*itself* — 17 digits and `e+000` for a variable, 9 digits and `e+00` for a literal, in the same program.
"The oracle disagrees" is a measurement; "the oracle is correct" would be a ruling, and real-number output
format is a semantics decision that belongs to Lon, not to me. Routed as a question, not a change.

## ⛔ Why this is urgent rather than tidy — it interlocks with a row assigned THIS session

ceo assigned hq_C `corpus-crosscheck-probe-total-conversion` under Lon's ruling that *"the crosscheck folder
should not still be around"* — every block converts into the graded `tests/` suite. **Converting these 5
blocks as they stand would launder 4 self-pinned refs and 1 unprovable one into the permanent suite**, where
the `96/0` tally would carry them as oracle-graded forever. The conversion's own inherited law is
byte-equality with the ORIGINAL, which preserves a self-pinned ref perfectly. Disposition must be settled
**before** those five convert — the format amendments ceo's brief already contemplates (self-pinned-ref
grading is named among them) are the natural home for it.

## ⭐ The general form

**Self-consistency and correctness are different measurements, and a green board reports the first while
being read as the second.** The whitespace-delta check was sound for what it asked — *did the regen change a
value?* — and the honest answer was no. It simply cannot answer *was the value ever right?* Same family as
`RULES.md:107` and as this root's `command -v` lesson: **an instrument that answers a narrower question than
you think you asked will never say so.** The cure is not more diligence, it is running the oracle: 96 blocks
took one script and a few minutes, against 20 days of a number nobody could defend.

⭐ **Credit: this finding is seat04's, not mine.** I ran the compiler; they refused to let a favorable
assumption close a question they could not prove, and named the exact blind spot — *"unable to see a defect
shared by both old and new refs"* — that turned out to contain all four.
