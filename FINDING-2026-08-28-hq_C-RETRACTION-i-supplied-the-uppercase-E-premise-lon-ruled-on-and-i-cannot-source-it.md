# ⛔ FINDING 2026-08-28 (hq_C) — RETRACTION: I supplied the "ISO 7185 specifies uppercase `E`" premise that Lon's ruling rests on, and I cannot source it. Every ISO 7185 artifact on this machine says lowercase `e`.

**HOLDING the 4 ref regens and the pb36 grade. Not executing CEO-72's format half until this is re-ruled.** Escalated to ceo the same session it was found.

## What I claimed, and where it went

`FINDING-2026-08-28-hq_C-four-of-96-pascal-crosscheck-refs-are-self-pinned-not-oracle-derived.md:57` states, flatly and without a citation:

> ISO 7185 specifies an **uppercase `E`**, so on exponent case SCRIP is arguably the more conformant of the two…

I hedged the *conclusion* ("arguably") but asserted the *premise* as fact. **I produced it from memory and never sourced it.** It then travelled exactly as an unsourced claim does: into ceo's brief, into the question put to Lon, and back as CEO-72 — "use ISO 7185 for both answers", with the operative consequence that SCRIP's current uppercase-`E` shape is the ISO-conformant one, that the 4 self-pinned refs regenerate to it, and that each is **provenance-marked `ISO-RULED, not fpc-derived`**.

That last part is why this cannot wait: the label would assert a provenance I cannot support, permanently, under a byte-equality law, in an irreversible-by-design conversion. **It would be the self-pinned-ref defect again wearing a better label** — which is the precise thing this row's QA exists to prevent.

## The measured evidence — three-way, same program, `writeln(1.554:15)`

| source | output |
|---|---|
| fpc 3.2.2 `-Miso` (THE Pascal oracle) | ` 1.5540000e+000` |
| SCRIP | ` 1.5540000E+000` |
| ISO 7185 acceptance test, "s/b" | `  1.554000e+00` |

⭐ **fpc and SCRIP differ by EXACTLY ONE CHARACTER — the case of the `e`.** Mantissa digits, 3-digit exponent, sign and field width are byte-identical. The disagreement is far narrower than my original FINDING implied.

**Both independent ISO 7185 acceptance suites on this machine use lowercase `e`** in their own should-be strings:
- `/home/resources/Pascal-P5/standard_tests/iso7185pat.pas:1844` — `' s/b  1.554000e+00'`
- `/home/resources/StanfordPascal-Pascal/testpgm/iso7185.pas:1343` — same string

Two separately-maintained ISO 7185 conformance tests agreeing is not proof of the normative text, but it is the best available proxy, and it points **against** my premise, not for it.

⛔ **ISO 7185's normative text is NOT on this machine.** I searched; what exists is conformance *test programs*, not the standard. So CEO-72's instruction — "verify SCRIP's exact shape against the standard's real write-parameter clauses (verify against the text, not this summary)" — **cannot be carried out here.** Reporting that rather than substituting my memory for the text a second time.

## What survives, and is now STRONGER

The **digit-count axis is unchanged and better evidenced**. fpc is self-inconsistent *within a single program at one width* — measured just now, same `:15` field:

```
 1.5540000e+000     <- 3-digit exponent
 3.141593e+0000     <- 4-digit exponent
 3.340000e-0003     <- 4-digit exponent
```

Not the 17-vs-9 significant-digits inconsistency I originally reported, but a **second, independent** self-inconsistency in exponent width. So "fpc is not a stable target on real formatting" is confirmed twice over, and Lon's instinct to reach for a standard rather than the oracle is well-founded. **Neither** fpc nor SCRIP matches the acceptance test's `1.554000e+00` (7 mantissa digits, 2-digit exponent) — so on digits, *both* implementations deviate from the ISO proxy, and SCRIP's "fixed self-consistent default" is at least self-consistent, which fpc's is not.

**The ruling's shape is sound. Its mapping to a concrete byte string is what I got wrong**, on one axis, and I am the source of the error.

## What I am asking

Re-rule axis (1) on sourced facts, or authorise a substitute authority:
1. **If ISO 7185's text says uppercase `E`** — CEO-72 executes exactly as written, and this retraction only costs a delay. Someone with the text must confirm the clause; I cannot.
2. **If it says lowercase `e`** — then SCRIP is the deviant on case, fpc and SCRIP agree except for it, and the 4 refs must regen to lowercase — the opposite byte string from CEO-72's instruction.
3. **If it delegates case** — then per CEO-72's own logic ("where ISO delegates, SCRIP's fixed self-consistent default is the sanctioned implementation definition") uppercase `E` stands, and CEO-72 executes as written **but the provenance label must say `ISO-DELEGATED, SCRIP-default`, not `ISO-RULED`** — a materially different claim about where the byte came from.

⛔ **The 4 refs and pb36 stay held.** Everything not gated on this axis continued (see the row baton).

## ⭐ The lesson, and it is mine

**An unsourced specification claim is the most portable kind of error there is.** A wrong measurement gets re-measured; a wrong *citation* gets quoted. This one crossed three seats and reached a Lon ruling in under a day, gathering authority at every hop, and would have been laundered into the permanent graded corpus with a provenance label asserting the very thing that was never checked.

This root's law already covers it — `RULES.md:105` TRANSCRIPTION IS WHERE PROVENANCE DIES, and its own corollary **never quote a number you did not produce**. ⭐ **The rule needs its obvious extension made explicit, because I did not apply it to myself: a SPECIFICATION CLAUSE is a number.** "ISO 7185 says X" is exactly as much a measurement as "the board reads 1086" — it has a source, that source is checkable, and quoting it without producing it is the same failure. The tell was there in my own sentence: I wrote `**uppercase `E`**` in bold with no file path beside it, in a FINDING where every other claim carries one.
