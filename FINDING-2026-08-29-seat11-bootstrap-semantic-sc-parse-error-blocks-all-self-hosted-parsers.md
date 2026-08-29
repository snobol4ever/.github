# FINDING 2026-08-29 seat11 — bootstrap/semantic.sc fails to parse on pristine HEAD, blocking every self-hosted parser driver

**Context:** readme-scrip row — verifying ruling #2's claim ("the language parsers are written in
Snocone, `parser_*.sc`") actually runs before citing it in SCRIP/README.md.

**Repro** (SCRIP `7817f370`, `make pristine` clean, RT_OPT=-O0 per NO-O2-BUILDS):
```
cd SCRIP
printf 'OUTPUT = "HELLO"\nEND\n' > /tmp/mini.sno
bash scripts/run_scrip_parser.sh snobol4 /tmp/mini.sno
```
Output:
```
/home/claude11/SCRIP/bootstrap/semantic.sc:38: snocone parse error: syntax error
SEQ0001 NINC  depth=-1 top=0
SEQ0002 NINC  depth=-1 top=0
SEQ0003 NPUSH depth=0 top=0

** Error 5 in statement 0
   Undefined function or operation
```
Same failure for `icon` (`run_scrip_parser.sh icon /tmp/mini.icn`) — `semantic.sc` is shared
runtime loaded by all six `parser_<lang>.sc` drivers, so this looks universal, not per-language.

Line 38 is `function qtag(t) {` — the first function head after the file's opening block comment.

**Not root-caused, not fixed** — out of scope for the readme-scrip row and not chased further
under time-boxing. `git log 48234f90..7817f370 -- src/frontend/snocone/ src/lower/` shows only
one touching commit (`a3275c6f`, arbno-chain dead-guard collapse) — plausible but unconfirmed;
the bug may predate this pull entirely (bootstrap/ arrived s267 2026-08-23 and no gate script
exercises `run_scrip_parser.sh` per a scripts/ grep, so a regression here could have sat unnoticed
for days).

**Effect on readme-scrip:** README states the Snocone-hosted parsers as an architecture/identity
fact (real files, real purpose, verified to exist) but does NOT publish a "run this and it works"
snippet for them, since that is currently false. Revisit the README's bootstrap section if/when
this is cured.
