# FINDING 2026-08-28 (seat03) — trailing whitespace's root cause: the lexer emits a dangling `T_CONCAT` right before `T_STMT_END`; fixed, verified, marker promoted

## Context
Row `snobol4-trailing-whitespace-parse-error` (minted by hq_C from `FINDING-2026-08-28-hq_C-one-
trailing-space-on-any-snobol4-statement-line-is-a-parse-error-...md`, which fully ablated the
black-box symptom but not the mechanism). This finding is the root cause and the fix, not a repeat
of the ablation.

## Root cause
`src/frontend/snobol4/snobol4.l`'s `BODY` state (mid-statement, after at least one real token has
been lexed) treats a run of whitespace as SNOBOL4's blank-as-concatenation operator:
```
<BODY>{W}  { ...; return T_CONCAT; }
```
(`W` = `({WS}|{CONT})+`, i.e. one-or-more spaces/tabs, optionally spanning a `+`/`.`-continued line.)
For input ending `X \n` (one trailing space then newline), flex's longest-match rule picks this over
the bare `<BODY>\n` rule (which only matches a lone newline, length 1): the single trailing space
alone is length 1 and `CONT` cannot extend it (no `+`/`.` follows), so `{W}` wins by matching first,
consuming the space and emitting `T_CONCAT` — then the very next token is `T_STMT_END` from the
now-adjacent bare newline. The grammar has no rule for a dangling concatenation:
```
expr4 : expr4 T_CONCAT expr5   -- snobol4.y:132, requires an operand on BOTH sides
```
A `T_CONCAT` with nothing following it (because a statement just ended) is a genuine, correctly-
reported syntax error from the grammar's point of view — SCRIP was refusing exactly what its own
grammar says to refuse; the defect is that the LEXER should never have produced that token there.

**Confirms the ablation's own reading exactly**: no code is generated (dies in the frontend before
the emitter), identical in m3/m4, and the reported-line-off-by-one is a pure knock-on of the spurious
syntax error (bison's normal one-token-of-lookahead line attribution), not a separate defect — once
the error stops happening, there is no line to misreport. (Verified a genuinely-unrelated syntax
error's own line-report is unaffected by this fix — pre-existing behavior, out of scope, see LEDGER.)

**Why this exact case was missed before**: the identical problem already existed for `;`-terminated
statements and was already fixed there —
```
<BODY>{W}";"           { ...; return T_STMT_END; }     -- snobol4.l:164, already present
```
— but no equivalent `{W}\n` rule was ever added for the far more common newline-terminated case.

## Fix
One new rule, mirroring the existing `;` pattern exactly (`snobol4.l:163`, now also at :163):
```
<BODY>{W}\n            { for(int _i=0;_i<yyleng;_i++) if(yytext[_i]=='\n') lineno++; gt_angle=0; BEGIN(INITIAL); return T_STMT_END; }
```
Flex's longest-match semantics make this win over the bare `{W}` concat rule whenever whitespace is
immediately followed by a newline (longer match, by construction), while a *continued* line (trailing
ws then `\n+`/`\n.`) still matches the existing `{W}` rule via its `CONT` alternative, which is always
longer still — continuation-line behavior is untouched. Regenerated `snobol4.lex.c` via a locally-
extracted flex 2.6.4 (`/tmp/flexbison/root/usr/bin/flex` — apt is unavailable in this seat, no root;
the .deb was already fetched+extracted in `/tmp/flexbison`, a pre-existing user-space workaround also
found in another seat's scratchpad. `install_system_packages.sh` itself cannot succeed here — `apt-get
update` fails `Permission denied` on the apt lock, and `sudo` needs a password this seat does not have;
worth a PRODUCT flag, not a blocker for this row since the extracted binaries work).

## Verified
- Minimal witness + all 4 ablation variants (plural trailing spaces, trailing ws on either line,
  trailing tab): all now `rc=0`, correct output, matching the oracle.
- Regression set: `genc.sno`/`bench.sno`/`lexcmp.sno` — 0 parse errors (was 2 each); `probe/m1/
  m1_trailing_ws.sno` (now living as suite entry `m1_trailing_ws` in `tests/snobol4/probe/m1.sno`)
  — harness's own `run` reported `XPASS(marker stale, promote it)`, confirming the fix; **promoted**
  (removed the ` XFAIL` banner suffix in both `.sno`/`.ref`, both files, entry #39) — re-ran the board:
  `m3_pass` 37→38, `m3_xpass` 1→0, clean.
- Re-measured (not assumed) the other 4 known-partial-blocker files: `lexical-comparison.sno`,
  `trim1.sno`, `trim0.sno`, `1brc.sno` — all still exactly 1 parse error each, as the task predicted
  (trailing ws was one of several causes for these four; no bonus improvement, no regression).
- Full `make pristine` + `test_corpus_snobol4.sh`: **GATE OK, 1298/1298 both modes, FAIL=0 SKIP=0
  MISSING=0.**
- Shared-node scope check: `git diff --stat` confirms only `src/frontend/snobol4/snobol4.l` (+its
  generated `.lex.c`) changed — each language has its own separate lexer object
  (`icon_lex.o`/`prolog_lex.o`/`raku.lex.o`/`lex.rebus.o`/`pascal.lex.o` are all distinct from
  `snobol4.lex.o`), so this cannot be a shared node by construction. Icon control arm
  (`test_crosscheck_icon.sh`) run anyway per the task's explicit ask: PASS=4 FAIL=0, unaffected.
- Checked (not assumed) that a genuinely different, unrelated parse error's line-number report is
  identical before and after this fix (stashed the change, rebuilt, compared byte-for-byte) — the
  fix is confined to the trailing-whitespace defect and does not touch general error-line reporting.

Pushed: SCRIP (`snobol4.l`, `snobol4.lex.c`), corpus (`tests/snobol4/probe/m1.{sno,ref}` marker
promotion). Task closed via `s4e_msg.sh done` — DONE-WHEN fully met.
