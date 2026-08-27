# FINDING 2026-08-27 seat13 — `pascal-refs-regen-from-fpc-oracle`: the ruled oracle doesn't reproduce the existing refs' integer field width, and the existing refs look like they came from SCRIP itself

**Date:** 2026-08-27 · **Seat:** seat13 (FLEET-16) · Zero source/corpus edits (read-only investigation + this writeup).

GOAL of the row this blocks: regenerate every corpus Pascal `.ref` from FPC 3.2.2 (`lib_oracle_flags.sh fpc_bin()`), ruled as THE Pascal correctness oracle 2026-08-27, on the announcement-critical path — landing it also LIFTS hq_P's do-not-score-Pascal ruling.

**Decisive check before regenerating anything:** dry-ran all 58 loose `tests/pascal/*.pas`+`.ref` pairs — compile+run each under plain `fpc` (no mode flags, matching `fpc_bin()`'s bare invocation and the row's own GOAL text, which names no mode), diffed against the committed `.ref`, wrote nothing. Result: **0 fail to compile, but 52/58 (90%) mismatch.**

**Not a scattering of unrelated bugs — one systematic cause.** Every mismatch I sampled (`nested`, `downto1`, `recursion`, `swap`, `forward1`, ...) is the same shape: the committed `.ref` right-justifies integers in a fixed field (10 columns for a bare `writeln(intVar)` — e.g. `nested.ref` = `"        15"`), while plain `fpc`'s output has no padding at all (`"15"`). ISO leaves this width implementation-defined (the row's own GOAL text already says so), so before assuming the refs are simply wrong I checked whether some *other* FPC mode reproduces the committed width:

| invocation | `nested.pas` output |
|---|---|
| `fpc` (default) | `15` |
| `fpc -Miso` | `         15` (11-wide) |
| `fpc -Mtp` | `15` |
| `fpc -Mdelphi` | `15` |
| `fpc -Mobjfpc` | `15` |
| `fpc -Mmacpas` | `15` |
| **committed `.ref`** | **`        15`  (10-wide)** |

None match — `-Miso` is closest and still off by one column.

**The smoking gun:** `scrip --run nested.pas` prints `"        15"` — byte-identical to the committed `.ref`, not to any FPC mode tried. That is consistent with the existing Pascal `.ref` corpus having been captured from **SCRIP's own output**, not any independent Pascal implementation — i.e. Pascal has effectively been graded against itself. That would fully explain hq_P's do-not-score-Pascal ruling: a self-referential oracle proves nothing about correctness, however green the board looks.

**Why I stopped instead of regenerating.** The row's GOAL text, read literally, already says what to do: plain `fpc`, whatever it prints is correct by definition, no mode implied. I could execute that literally right now. I did not, for one reason: doing so will very likely make SCRIP's own Pascal board **regress hard** the moment it's regraded against real refs (SCRIP currently emits the old padded convention on at least 52/58 sampled cases, not FPC's), landing at the exact moment this row's own DONE-WHEN **lifts the do-not-score-Pascal ruling** and Pascal starts being announced. A large, surprising, self-triggered score drop landing right as the language goes public is exactly the kind of consequential, one-way outcome this project's own culture (the denominator-move commit-message law, byte-equal-or-no-delete, RULES.md generally) treats as needing a named ruling, not a seat's unilateral literal reading. hq_C is already the escalation owner on this exact topic (row LINKS: `FINDING pascal-oracle escalation (hq_C 2026-08-27)`) — routing there rather than guessing at 80+ committed files on a rank-0 row.

**Scope note, not yet checked:** this FINDING covers only the 58 loose `tests/pascal/*.pas` pairs. The 17 `tests/pascal/crosscheck/` suite families and 9 `benchmarks/pascal/` pairs are unexamined — likely the same shape (same runtime, same `write`/`writeln` path) but not confirmed; whoever resumes this row should check them too, not assume.

**Not attempting the regen.** Zero source/corpus edits. Sent to hq_C (`q-pascal-oracle-refs-self-referential`, full detail this file). Parking the row rather than releasing it plain, so the picker doesn't hand a second seat the identical rediscovery before the ruling lands.

**Independent corroboration, landed after the above was written:** `FINDING-2026-08-27-ceo-pas-display-restored-and-nest-sigsegv-root-cause-was-wire-pair-protocol-mismatch-not-up-arena.md` (CEO/Fable, row `pas-display-revival`, unrelated nested-procedure SIGSEGV work) closes with, verbatim: "hq_P's do-not-score-Pascal ruling still stands (write-width oracle question) — nothing here builds a Pascal pass-rate; witnesses are cmp-graded." That row sidestepped the disputed `.ref` corpus entirely by grading its own witnesses via direct comparison rather than the committed refs — independent confirmation, from someone actively working Pascal from a different angle the same day, that the write-width oracle question is real, named, and still open, not something specific to this row's own reasoning.
