# FINDING — the 24 Icon JCON markers: the converted sources are UNBUILDABLE by the oracle, the upstream twin makes them gradeable, and my own first grading of them was wrong in the flattering direction

**Seat:** hq_B · **Date:** 2026-09-04 · **Row:** `icon-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect` (PARKED — this is a census, not a close) · **Prompted by:** ceo audit of corpus `1520d35d1` — *"files=24: the loose markers `corpus/tests/icon/rung36_jcon_*.xfail` still count as red on the gate, yours to fix against the oracle or delete with the reason in the commit"* · **Law:** Lon 2026-09-03 21:30, RULES.md § THERE IS NO SUCH THING AS XFAIL

## The claim in one line

"Fix it against the oracle" could not be done on these files at all — `icont` **rejects 24 of the 31** `rung36_jcon_*.icn` in our tree — and the reason is our own semicolon conversion; the fix is to grade through the unconverted upstream twin, which exists, builds, and is byte-identical modulo trailing semicolons. Then, having found that path, **my first grading run down it produced a false green**, and the fix for that is written here beside the path so the next person does not repeat it.

## Fact 1 — the oracle cannot build our copies, and the error is our conversion

```
$ icont -s -o t.x corpus/tests/icon/rung36_jcon_arith.icn        # rc captured, not read off a pipe
File .../rung36_jcon_arith.icn; Line 94 # "else": invalid expression
rc=1
```

Line 92–94 is `return integer(v * 10 + 0.5) / 10.0;` followed by `else`. `icont` inserts a semicolon at a newline (Beginner/Ender); our conversion already put one there; the `if` expression is therefore closed before `else` is seen. The other shape is `local i, j;` inside a declaration, reported as `";": invalid declaration`. **Measured across the family: `icont` builds 7, rejects 24 of 31.** Every marked entry is in the rejected set.

⛔ So the ceo's instruction, taken literally on these files, is unexecutable — and it is unexecutable for a reason nobody had written down: the semicolon-required dialect makes our Icon corpus **oracle-unbuildable**, which is a much larger fact than 24 markers. It does not affect the master (`ALL.icn` entries are graded against `ALL.ref`), but it does mean any "re-cut this Icon test from icont" instruction must say *from which source*.

## Fact 2 — the upstream twin is the grading path, and it works

`corpus/packages/icon/jcon_tests/<name>.icn` is the unconverted original. Measured:

- `icont` builds **23 of 24** of them (`geddump` is rejected upstream too, at its own line 139 — an upstream defect, not ours).
- Converted vs upstream are **identical modulo trailing semicolons**: `diff <(sed 's/;[[:space:]]*$//' converted) <(sed 's/;[[:space:]]*$//' upstream)` is empty for the ones checked.

So the family is gradeable: build the **upstream** twin with `icont`, run it, and compare against SCRIP running **our** converted copy. That is the honest oracle cut, and it is available today with no new tooling.

## Fact 3 — ⛔ and my first grading run down that path was WRONG, in the flattering direction

I graded all 23 with `</dev/null` on both sides and read out a table. It said `btrees: SCRIP == ORACLE, ref is STALE` — which would have justified re-cutting a correct answer key to match a broken compiler.

**What actually happened:** `btrees` line 15 is `while line := read() do ...`. Fed `/dev/null` it reads EOF immediately and prints **nothing**. The oracle printed 0 bytes; SCRIP printed 0 bytes on stdout (its `[GENHOST] … RESERVES NOTHING` diagnostic goes to **stderr**); the two agreed on emptiness and my comparison called that agreement. Fed its real sidecar, `corpus/tests/icon/config/rung36_jcon_btrees.stdin`, the oracle reproduces the stored `.expected` **exactly** — the ref was never stale, and SCRIP still fails the entry on the routed `[GENHOST]` mechanism.

This is CLAUDE.md's own rule (`< /dev/null` never on a run fed by a pipe or a file) meeting the narrow-instrument law, and it cost a wrong conclusion about an answer key. **10 of the 24 marked programs read stdin** (`btrees errors fncs geddump io others profsum recent sorting struct`) and **only 4 stdin sidecars exist** (`config/rung36_jcon_{btrees,geddump,io,others}.stdin`), so six of them are fed EOF by the suite itself and are being graded on truncated behaviour today.

⭐ The reusable form: **when two implementations agree on empty output, that is not agreement, it is a shared absence of input.** Any grading harness comparing outputs must treat "both empty" as a refusal to grade, not a pass.

## Fact 4 — some refs embed values no implementation can reproduce

Not all disagreement is staleness or defect. With the oracle fed the same way the suite feeds it:

- `struct` — ref says `sort(t) ----> list_34(26)`, oracle says `list_8(26)`: an allocation **serial number**.
- `nargs` — ref says ` -3 open`, oracle says `  2 open`: a **file-descriptor** number.

Those refs pin implementation-dependent values, so the entries cannot pass deterministically for anybody, and **re-cutting them would bake today's serial numbers in as tomorrow's oracle** — a faulty test that survives its own repair. The cure for that class is to normalise the values in the comparison or to drop those lines from the witness, and it belongs to whoever takes the class, stated here so the next person does not "fix" it with a re-cut.

## What I deliberately did NOT do

- **No ref was re-cut and no marker was deleted.** After Fact 3, every number I had was suspect until the stdin question was settled per program, and 6 of the 10 stdin-readers have no sidecar to settle it with. Re-cutting on that evidence would have replaced a correct answer key with a wrong one, silently — the exact failure the markers' own re-classing was about (a description that describes something other than what it saw).
- **`btrees`'s marker stands, with one correction owed:** it says `rc=134 SIGABRT`; today the program exits **rc=0** with the `[GENHOST]` diagnostic on stderr and empty stdout. The mechanism and the routing (`icon-jcon-class-genhost-recursive-generator`) are unchanged and correct; only the exit code moved. Same stale-in-the-dangerous-direction shape already recorded for five markers on 2026-09-03, one layer down.

## The residue, measured today, for whoever resumes the row

| population | measured |
| --- | --- |
| loose markers | 24, all `corpus/tests/icon/rung36_jcon_*.xfail` |
| `ALL.csv` xfail column | 0 (cured, corpus `1520d35d1`) |
| `ALL.xfail` lines | 0 (file deleted, same commit) |
| oracle-buildable in our tree | 0 of 24 (converted); 23 of 24 via the upstream twin |
| marked programs that read stdin | 10 |
| stdin sidecars that exist | 4 |

**Next concrete step, in this order:** (1) mint the 6 missing stdin sidecars from the upstream suite's own inputs, because six entries are being graded on truncated runs and no number about them means anything until that is fixed; (2) grade the family through the upstream twin and re-cut only the refs that then disagree for a NON-environment-dependent reason; (3) the crash classes (`errors` `evalx` `collate` rc=134, `iobig` `misc` rc=139) keep their existing owning rows — three of five already had one before this row existed.
