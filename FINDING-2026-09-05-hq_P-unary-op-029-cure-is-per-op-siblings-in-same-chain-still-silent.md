# FINDING — the unary-`!` 029 cure is a PER-OP cure; four sibling arms in the same chain still swallow silently

**Seat:** hq_P (HQ-PERFORMANCE, verification lane) · **Date:** 2026-09-05 · **Mode:** FLEET-16
**Row reviewed:** `snobol4-testpgms-test1-traps-29...` (CLAIMED:seat08) · **Verdict on the landed cure: CORRECT, and it stays.**
**Tree:** SCRIP `f72ea9426` (cure `6dddcc237` is an ancestor) · corpus `75012904f` · `.github` `38491f02`
**Build graded on:** incremental `make` (RULES.md:118 loosening), `RT_OPT=-O0 …`, RT_TAG `f65f143e2f`, binary rebuilt 11:19 — the 11:05 binary predated the cure and would have graded a world that did not exist.
**Oracle:** `/home/resources/x64/bin/sbl -bf` via `lib_oracle_flags.sh:sbl_correctness_bin()`.

## 1. What was verified about seat08's cure — it is real

`6dddcc237` replaces an unconditional identity-or-first-character guess in `try_call_builtin_by_name_bl`'s
`fn[0]=='!'` arm with an OPSYN-registration check, then raises 029. Identity is `LCherryholmes <lcherryh@yahoo.com>`
author and committer, no trailers. Measured on an isolated witness, both directions:

```
X = !'abc'   oracle: op_21.sno(1) : ERROR 029 -- undefined operator referenced
             SCRIP : (0) : ERROR 029 -- Undefined operator referenced      <- number now correct
```

Bypassing `core_err_msgs[]` with a literal was **necessary and correct**: `core_err_msgs[29]` is
`"Erroneous INCLUDE statement"`. seat08 documented the whole mis-indexing separately and against the manual in
`FINDING-2026-09-05-seat08-core_err_msgs-is-not-indexed-by-official-spitbol-error-numbers.md`; not duplicated here.

## 2. The defect class is NOT cured — measured, not reasoned

`!` is one arm of a chain of unary arms (`+ - * ! / \ ~ ?`) that all share the shape *"unconditional hardcoded
fallback, never consults OPSYN registration"*. Only `!` was changed. Full table, same witness shape
(`X = <op>'abc'` — operand ADJACENT, a space makes SNOBOL4 parse it as binary and every row becomes a parse error):

| op | oracle | SCRIP m3 | |
|---|---|---|---|
| `!` | ERROR 029 undefined operator referenced | ERROR 029 **U**ndefined operator referenced | case-only diff (§3) |
| `%` | ERROR 029 | `RESULT=` — **silent** | ⛔ uncured |
| `/` | ERROR 029 | `RESULT=` — **silent** | ⛔ uncured, arm directly below the cured one |
| `+` | ERROR 004 affirmation operand is not numeric | `RESULT=0` — **invents a value** | ⛔ uncured |
| `-` | ERROR 010 negation operand is not numeric | `RESULT=0` — **invents a value** | ⛔ uncured |
| `#` | ERROR 029 | ERROR **005** Undefined function or operation | wrong code (falls to generic arm) |
| `\|` | ERROR 029 | ERROR **005** Undefined function or operation | wrong code (falls to generic arm) |
| `*` `?` `~` | — | matches | ✅ |

**Control arm proving these are the same defect and not merely unimplemented operators:** OPSYN the operator and
SCRIP matches the oracle byte-exact —

```
OPSYN('/','DOUBLE',1); OUTPUT = 'RESULT=' /'ab'   oracle RESULT=abab   SCRIP RESULT=abab   ✅
OPSYN('%','DOUBLE',1); OUTPUT = 'RESULT=' %'ab'   oracle RESULT=abab   SCRIP RESULT=abab   ✅
```

So the registered path works for the siblings; only the **unregistered** path silently returns instead of raising.
That is precisely the `!` bug, in `%`, `/`, `+`, `-`. Authority: RULES.md § **No per-op filter** — *"A defect
reachable through one member is a class defect: fix the class or leave the class visibly red."* `+` and `-` are the
worse half: they do not fail, they **fabricate `0`** from a non-numeric operand, which no board can see as red.

## 3. Two smaller, separable items

- **Message case (seat08-introduced, latent).** The literal is `"Undefined operator referenced"`; the oracle prints
  lowercase `undefined operator referenced`. No live `.ref` pins it today (the only corpus occurrence is prose in
  `tests/snobol4/config/parser_EXCLUDED.md:95`), so nothing is red — it is a one-character fix now, and a byte-exact
  diff later. It matches `core_err_msgs[]`'s house capitalisation, which is the dialect we do **not** grade against.
- **The range guard, extending seat08's finding.** `core.c:2133` is `if (!msg && code >= 1 && code <= 39)`. SPITBOL
  codes measured in this session alone include **212, 230, 242**; the table holds 40 entries. Every SPITBOL code
  above 39 that reaches the site with `msg==NULL` therefore gets no message at all. Not seat08's row.

## 4. Exonerated by control arm — do NOT chase these

`(0) : ` in place of the oracle's `file(line) : `, and SCRIP writing the error to **both** stdout and stderr where
the oracle writes stdout only, are **pre-existing for every SCRIP runtime error**, not introduced by this cure —
confirmed on an unrelated site (`X = 1 / 0`, which prints the same `(0) : ` prefix on both streams). Recorded so the
next reader does not re-file them against `6dddcc237`. (That same control incidentally shows `ERROR 002` where the
oracle says `ERROR 014` — another instance of seat08's mis-indexing finding, in the arithmetic lane.)

## 5. Ruling routed to seat08

The cure lands and is not to be reverted. The row's DONE-WHEN cannot go green while the class is half-cured: extend
the registration-first check to the whole unary chain, or leave the class **visibly red** with a named witness per
RULES.md. `%` and `/` are the cheapest (identical shape, adjacent arms); `+`/`-` need the numeric-coercion failure to
raise 004/010 instead of yielding `0`.
