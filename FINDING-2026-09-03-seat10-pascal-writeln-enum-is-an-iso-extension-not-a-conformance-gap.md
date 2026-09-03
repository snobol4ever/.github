# FINDING: ISO 7185 forbids `writeln(<enum>)` — SCRIP's support for it is a non-standard extension, sourced and settled

**Who/when:** seat10, 2026-09-03, FLEET-12, working row `pascal-writeln-enum-iso-conformance-unresolved`
(third of three assigned rows this session).

## The question

Two Pascal crosscheck witnesses (`pb:1 pb36`, loose `pb37.pas`) write an enumerated value directly
(`writeln(chartp[ch])`), which `fpc -Miso` refuses to compile (`Fatal: Unknown compilerproc
"fpc_write_text_enum_iso"`), leaving their refs SCRIP-self-derived and unproven. `corpus/tests/pascal/KEEP.md`
§4 asserted, without a citation, that this was "a real gap in this fpc build's `-Miso` RTL, not a SCRIP or
ref defect" — flagged by a prior session as the same unsourced-assertion shape that produced (and then
retracted) an incorrect ruling on ISO's exponent-case rule days earlier.

## Method

1. Reproduced the refusal directly: `fpc -Miso pb37.pas` → `Fatal: Unknown compilerproc
   "fpc_write_text_enum_iso"` (measured this session, current environment).
2. Read the two pieces of circumstantial evidence the task itself named, directly: the ISO 7185 acceptance
   test (`/home/resources/Pascal-P5/standard_tests/iso7185pat.pas:559-570`) writes every enum exclusively via
   `ord(e):1` — never `writeln(e)` — across five separate occurrences in one procedure. And the local FPC RTL
   source (`/usr/share/fpcsrc/3.2.2/rtl/inc/text.inc:1191`, `/home/resources/FPCSource/rtl/`) confirms
   `fpc_write_text_enum` (the default-mode routine, writing the enum's *name*) is implemented, while no
   `_iso`-suffixed variant exists anywhere in the RTL source tree — and a grep of the FPC *compiler* source
   (`/home/resources/FPCSource/compiler/`) found no literal callsite constructing that name either, so the
   exact mode-suffix mechanism is unconfirmed (not pursued further — see "What was not done").
3. Both of those are circumstantial, as the task itself said. Fetched the source the task named as the
   accepted precedent (CEO-74 established *Moore's Rules of ISO 7185*,
   <https://standardpascal.org/iso7185rules.html>, as a citable secondary source for exactly this kind of
   question — already load-bearing in `ARCH-LANGUAGES.md`'s real-number-formatting ruling). Its "Predefined
   procedures and text files" section states directly: *"Integers and reals can be read from a text file, and
   integers, reals, booleans, and strings can be written to text files."* A closed enumeration, not an
   illustrative one — enumerated/scalar types are absent from it.

## Verdict

**ISO 7185 forbids `writeln(<enum>)`.** SCRIP's support for it is a **non-standard extension** — allowed, not
a defect, but the two witnesses test an extension and must not sit in a suite that reads as ISO conformance.
Re-marked `ISO-EXTENSION` (not `ISO-DELEGATED-SCRIP-DEFAULT`, which is reserved for axes ISO explicitly
declines to mandate — this axis ISO mandates *against*). The refs stay SCRIP-self-derived, now understood as
*permanently* correct provenance rather than *pending* an oracle that cannot exist for this construct.

`fpc -Miso`'s crash is best read as fpc still parsing/accepting the extension under strict mode (routing it
to a mode-specific compilerproc distinct from the implemented default-mode one) but never finishing that
routine's RTL — its own incompleteness handling a non-ISO construct, not evidence about the standard's text
either way, and not the basis for the ruling above (which rests on Moore's Rules + the acceptance test, not
on fpc's own failure mode).

## Files updated (three, per the row's fuller original intent — not just the narrower computable DONE-WHEN)

- `.github/ARCH-LANGUAGES.md` § PASCAL: `### ⛔ NOT settled...` → `### ✅ SETTLED...`, full citation and
  consequence.
- `corpus/tests/pascal/KEEP.md` §4: the unsourced sentence corrected in place, plus the standing warning box
  beneath it (which referenced "open in both directions") updated to point at the ruling instead.
- `corpus/tests/pascal/config/crosscheck_PROVENANCE.md` (relocated from the `crosscheck/PROVENANCE.md` path
  both the task file and `KEEP.md` cite — that path no longer exists; the master-suite consolidation moved it
  under `config/` with a `crosscheck_` prefix, same shape as this fleet's other tree-churn drift. Found via
  `find`, not assumed from either doc): "1 block — NO ORACLE, and the ISO question is OPEN" → "1 block — NO
  ORACLE, permanently — `ISO-EXTENSION` (✅ SETTLED)", full citation.

## What was NOT done

Did not trace the FPC compiler's exact mode-suffix-selection mechanism for compilerproc names (the grep for
a literal `write_text_enum_iso` callsite in the compiler source came back empty — likely constructed
dynamically from a mode flag rather than written as a literal string; not pursued, since it is circumstantial
color, not load-bearing for the citation-based ruling the row asked for). Did not attempt to locate the
formal ISO 7185 standard text itself (not available on this machine, per the existing delegation ruling's own
note, unchanged by this session) — Moore's Rules is used exactly as CEO-74 already established it may be:
explicitly as a secondary source, with its own disclaimer quoted in both updated files rather than elided.
