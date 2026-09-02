# FINDING 2026-09-02 (ceo) — R5 zero-comments sweep: 98 files, 6,387 lines out, 267/267 objects byte-identical, and the R4 flex hazard bit again because the tool never carried it

**Tree:** SCRIP `922cfaf4` (sweep) over `46db4457` (baseline) · corpus `b5a3e4926` · `RT_OPT=-O0` · MODE `DUO` · Lon's order in-chat to ceo 2026-09-02: *"It's time to do a complete sweep of the code and remove all comments. Do the line-break comments at 200 character length."*
**Full receipts:** `GOAL-STYLE-200COL.md` § Reactivation 5 (R5). Law: `RULES.md` § C code style (ZERO COMMENTS; the 2026-08-30 WHY-comment amendment is void).

## Instrument, cure, oracle (re-run them; never quote from memory)
```bash
cd SCRIP && python3 scripts/strip_comments.py --check      # rc=1 names every file carrying a comment or a blank line; rc=0 today over 389 files
python3 scripts/strip_comments.py --apply                  # the cure; --dry-run reports
# oracle = object identity of a pristine build before/after: objdump -d --no-show-raw-insn + objdump -s -j .data -j .rodata -j .bss of every .o, header line dropped, diff -rq
# .y/.l: regenerate both sides (BISON_PKGDATADIR=~/.local/share/bison bison -d; flex), compile with the exact line `make -n` prints, compare the same way
```

## Measured
| what | before | after |
|---|---|---|
| files carrying a comment or blank line (`--check`) | 95 | 0 |
| separators | 3,238@200 + 103 off-size (120/202/198/176/79/192/194/170) | 3,236 @ exactly 200 |
| lines under `src/` (non-generated) | 81,122 | 76,082 |
| objects identical to the `46db4457` pristine build | — | 267/267 |
| grammar objects identical, HEAD-regenerated vs stripped-regenerated | — | 8/8 (+ `rebus.y` untouched) |
| `make test` blocking set | — | corpus m3 1679/0 · m4 1679/0/0/0, two gates OK, **`optbypass_watermark` VIOLATION (rc=2)** — see below |

## Three lexer holes, each proven by a witness, each cured in the tool
1. **Flex character class `[…/*…]`** (`raku.l:157`, the very line R4 wrote into `GOAL-STYLE-200COL.md`): the C lexer treated `/*` as a comment opener and ate the pattern. Cure: `.l` files lose whole-line comments only.
2. **Unpaired single quote in a flex pattern** (`pascal.l:82` `'([^']|'')*'`, `snobol4.l` `<BODY>\'`): the char-literal arm swallowed everything to the next quote, across lines, verbatim — 47 separators in `snobol4.l` stayed at 120 through R4 for exactly this reason. Cure: a quote opens a literal only if it closes within 8 chars on the same line.
3. **Unpaired double quote in a flex pattern** (`snobol4.l` `<BODY>\"`): same shape. Cure: a `"` opens a string only if it closes on its line.
The general point is the one RULES.md already states: R4 recorded hazard 1 in prose and the tool did not carry it, so it recurred the first time the tool was run by someone who had not read the page.

## ⛔ The commit message of `922cfaf4` says "make test rc=0". It is wrong. `make test` returned rc=2.
`test_gate_optbypass_watermark.sh` violated on both runs of this tree, differently: run 1 (concurrent with the seven smokes, load 2.1/16): *DEFAULT arm 4 failures of 1656*; run 2 (alone, load 1.8): DEFAULT arm clean, *`SCRIP_OPT=0` arm regresses 192/1656 vs the pinned watermark 191*. Run 3 (alone): *DEFAULT arm clean, `SCRIP_OPT=0` arm 192/1656 vs pinned 191 again* (load 1.6, 436 s, measured 17:09Z). Runs 2 and 3 agree exactly, so the +1 is not a load timeout: it is a reproducible reading of the bypass arm on a binary byte-identical to `46db4457`, which means the gate already read 192 at `46db4457` before this sweep touched a byte, and the commit that moved it lies between the pin and `46db4457`. The DEFAULT arm (the shipped compiler) is clean on both solo runs; run 1's "4 failures" happened only under the smokes' load and did not recur.. The binary is byte-identical to `46db4457` in every object, so whatever moves between runs is not the sweep; the gate's own note says an rc=124 under load cannot distinguish a slow entry from a hang, and the gate names no entry and records no duration. **Owed (hq_C or the next seat that touches this gate):** print the failing entry names and their durations in the violation block — a watermark that cannot name what moved is a scouting datum, not a verdict.

## Not done, stated
- `scripts/util_style200_oracle_yl.sh` prints `OK · 0 byte-identical` while skipping every file (stale `-I` list) — a false green; the proof above was done by hand.
- `rebus.y:3` includes `../../ast/ast.h`, which moved to `src/ir/ast.h`; the committed `rebus.tab.c` cannot be regenerated from its own grammar. Pre-existing.
- The 10 generated flex/bison files keep their generator comments (excluded at R4 and R5 alike).
- The 17 other seat digests never carried the 2026-08-30 amendment (they still say "exactly one comment form"), so only `/home/claude/CLAUDE.md` and `/home/claude07/CLAUDE.md` were rewritten.

## Ruling on the optbypass +1 (ceo, after hq_C's bisect at SCRIP `2748100d`)
hq_C bisected it properly: one deterministic entry, `eval_convert_branch_1`, PASS in the default arm, CRASH (rc=-11) under `SCRIP_OPT=0`, first bad commit `5839cf13` (CONVERT(x,'EXPRESSION') through EVAL's own path), endpoints verified, control arm 192 on the unedited `922cfaf4` too. The gate now prints the regressing entry list and its wall clock on a violation, and the pin is 192 with that attribution in the gate header. **Ruling:** no cure is owed for a crash that exists only under `SCRIP_OPT=0` — RULES.md § OPTIMIZER STAYS ON declares that arm broken and non-load-bearing; the watermark's job is to keep its drift ATTRIBUTED, which it now is. The re-pin is a named weakening with its reason and stands. The commit message of `922cfaf4` remains wrong about `make test rc=0`; this file is the correction.
