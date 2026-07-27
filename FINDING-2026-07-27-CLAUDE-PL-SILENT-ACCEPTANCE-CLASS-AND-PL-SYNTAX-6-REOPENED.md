# FINDING-2026-07-27-CLAUDE-PL-SILENT-ACCEPTANCE-IS-ONE-CLASS-ACROSS-THREE-SUBSYSTEMS-AND-PL-SYNTAX-6-REOPENED

**Session:** s155 (Prolog / GOAL-PROLOG-BB) · **Mode:** measurement + live probe, **NO SOURCE MODIFIED**
**Instruments:** SCRIP built `-O0` (`scrip` + `libscrip_rt`, both rc=0, no `-O2` and none sought) ·
GNU Prolog **1.4.5** installed live via apt · gprolog **1.6.0** + SWI **10.1.5** sources read from the
uploaded archives, symlinked at `SCRIP/refs/{gprolog-master,swipl-devel-master}`.

---

## 0. ⭐⭐ THE HEADLINE — THREE BANKED/OPEN ITEMS ARE ONE DEFECT CLASS

`GOAL-PROLOG-BB.md` carries *"compiled-path silent-fail on undefined predicates"* in BANKED across
s151-s154, corroborated twice, owned by no rung. This session probed it and found **the same failure
mode in two more subsystems that no one had connected to it**:

| # | Subsystem | Stage | SCRIP behaviour | GNU 1.4.5 behaviour | Class |
|---|---|---|---|---|---|
| 1 | Predicate dispatch | runtime | undefined predicate **silently fails** | `existence_error(procedure, F/A)` | accept-and-continue |
| 2 | `format/2` engine | runtime | unknown directive **silently emits nothing** | format error | accept-and-continue |
| 3 | Reader escapes | **lexer** | unknown escape **silently passes the char through** | `syntax error: unknown escape sequence` | accept-and-continue |

Three different files, three different pipeline stages, **one discipline gap: SCRIP accepts and
continues where both references raise.** Each was previously either banked as a one-off (1), listed as
a coverage gap (2), or believed CLOSED (3).

⭐ **RULE (sibling of s152's admission-site rule and s153's instrument rule): A SILENT-ACCEPTANCE
DEFECT IS INVISIBLE TO A COVERAGE CENSUS, BECAUSE COVERAGE ASKS "IS IT ADMITTED?" AND THE ANSWER IS
YES.** All three of these pass an admission audit — the predicate is dispatched, the directive is
consumed, the escape is lexed. What differs is the ERROR EDGE, and no predicate-row tracker has an
error-edge column. This is why three instances sat in three different states for four sessions without
anyone seeing them as one thing.

**PROPOSED RUNG — `PL-STRICT-1` (one rung, three sites):** make each of the three raise the reference
error. They share no code, but they share a spec, a test shape, and a reviewer's mental model, and
fixing them together is what makes the CLASS visible in the tracker instead of three unrelated rows.

---

## 1. VERIFIED DIVERGENCE — UNDEFINED PREDICATE (the banked defect), **BOTH MODES, NOT JUST COMPILED**

Probe (`/tmp/p_undef.pl`), identical source both engines:
```prolog
main :- write(before), nl,
    ( catch(no_such_predicate_xyz(1), E, (write(caught(E)), nl)) -> true
    ; write(goal_FAILED_silently), nl ),
    write(after), nl.
```

| Engine | Output |
|---|---|
| **GNU Prolog 1.4.5** | `caught(error(existence_error(procedure,no_such_predicate_xyz/1),main/0))` |
| **SCRIP mode 3 (`--run`)** | `goal_FAILED_silently` |
| **SCRIP mode 4 (`--compile`, via `scripts/run_prolog_via_x86_backend.sh`)** | `goal_FAILED_silently` |

⛔ **THE BANKED ENTRY'S NAME IS WRONG AND HAS BEEN FOR FOUR SESSIONS.** It reads *"**compiled-path**
silent-fail"*. **Mode 3 and mode 4 fail IDENTICALLY.** This is not a codegen defect and not a mode-4
defect — it is engine-wide, which makes it *cheaper* to fix (one runtime site, not a template) and
*more severe* (it was never mode-limited). Modes 3 and 4 agreeing is also, in itself, a
GOAL-MODE34-IDENTICAL green: they diverge from the reference **together**.

⚠⚠ **AND SCRIP'S OWN FLAG CONTRADICTS ITS OWN BEHAVIOUR:**
```
current_prolog_flag(unknown, X)  ->  X = error        % SCRIP claims error
                                     ...and then silently fails anyway
```
This is the **exact shape** of the s153 `double_quotes`/`dialect` contradiction (`dialect=gnu` while
`double_quotes=atom`). **Two independent instances of "the flag reports the standard behaviour while
the engine does something else."** A flag that lies is worse than a missing flag: `current_prolog_flag/2`
is what portable library code branches on.

---

## 2. ⛔ PL-SYNTAX-6 IS **REOPENED** — IT WAS CLOSED ON AN INCOMPLETE PROBE

`PROLOG-SYNTAX-TRACKER.md` marks **PL-SYNTAX-6 CLOSED, no gap** — *"`0'c` `0x` `0o` `0b` escaped-char-codes `{}/1` ALL CORRECT (probed)"*. Those specific forms **are** correct; I re-probed and confirm them. But the rung's name is *"reader escapes"* and the probe set never included an
**unknown** escape or `\s`. Both diverge:

| Input | GNU 1.4.5 | GNU 1.6.0 (source) | SWI 10.1.5 | **SCRIP (probed live)** |
|---|---|---|---|---|
| `'a\sb'` | **syntax error** | space (`!strict_iso`) | space | **`[97,92,115,98]`** = `a` `\` `s` `b` |
| `'a\zb'` (unknown) | **`syntax error: unknown escape sequence`** | syntax error | syntax error | **`[97,92,122,98]`** = `a` `\` `z` `b` |
| `'a\eb'` | **syntax error** | 27 (`!strict_iso`) | 27 | `[97,27,98]` ✓ (matches 1.6.0/SWI) |
| `'a\tb'` | 9 | 9 | 9 | `[97,9,98]` ✓ |
| `'a\x41\b'` | `aAb` | `aAb` | `aAb` | `aAb` ✓ |
| `'a\101\b'` | `aAb` | `aAb` | `aAb` | `aAb` ✓ |

Root cause is one line — `src/parser/prolog/prolog_lex.c:98`, `decode_escape()`:
```c
default:   *code = (unsigned char)e; return -1;   /* unknown escape -> pass the char through */
```
There is **no `case 's'`**, and the `default` arm never raises.

⭐⭐ **VERSION SKEW IS REAL AND IT BIT THIS ROW — THE DOC CAVEAT EARNED ITS KEEP.**
`\s` and `\e` are accepted by gprolog **1.6.0** (`BipsPl/scan_supp.c:678-685`, gated
`if (!Flag_Value(strict_iso))`) and **rejected by the 1.4.5 binary** that s151/s152/this session
actually run. **The archive Lon uploaded is a DIFFERENT GNU than the apt oracle.** Any GNU row in any
tracker must name its version. `PROLOG-SYNTAX-TRACKER.md`'s GNU columns were measured against 1.4.5;
`PROLOG-SWI-SYNTAX-SEMANTICS.md`'s were read from 1.6.0 source. **They are not directly comparable and
neither is wrong.**

---

## 3. ⛔ FALSE GAP CONFIRMED — 8 FORMAT DIRECTIVES THE GOAL FILE CALLS OPEN ARE **IMPLEMENTED AND WORKING**

`GOAL-PROLOG-BB.md` PL-ISO-9 prose lists as OPEN:
> format directives `~p ~q ~e ~f ~g ~r ~c ~s ~t~| ~+` (column stops)

Probed live, mode 3, one `format/2` call each:

| Directive | Result | Verdict |
|---|---|---|
| `~a` | `A[foo]` | works |
| `~w` | `W[bar(1)]` | works |
| `~q` | `Q['it''s']` | works — **listed OPEN** |
| `~d` | `D[42]` | works |
| `~s` | `S[hi]` | works — **listed OPEN** |
| `~c` | `C[A]` | works — **listed OPEN** |
| `~e` | `E[1.500000e+00]` | works — **listed OPEN** |
| `~f` | `F[1.500000]` | works — **listed OPEN** |
| `~g` | `G[1.5]` | works — **listed OPEN** |
| `~8r` | `R[100]` | works — **listed OPEN** |
| `~p` | `P[zip]` | works — **listed OPEN** |
| `~i` | `I[shown]` | works |
| `~~` | `TILDE[~]` | works |
| `~N` | emits newline | works |

**8 of the 11 directives named OPEN are shipped and correct.** Exactly the s152 hazard: *a false gap
wastes a rung implementing what already exists, and does so silently.*

**Genuinely missing (probed, all produce EMPTY output, no error):**
`~t` `~|` `~+` (the column-stop machinery — the goal file is RIGHT about these three) · `~D` `~k` `~W`
`~E` `~F` `~G` `~I` `~h` `~@`.

So PL-ISO-9's format line should read: **OPEN = `~t ~| ~+` (column stops) + `~D ~k ~W` — and the
silent-drop of every unknown directive (§0 class 2).** Not the 11 currently named.

---

## 4. `double_quotes` — THE DEFECT IS CONFIRMED, AND THE RUNG'S FRAMING IS WRONG (carried from §0 of the new reference doc)

Probed: `double_quotes = atom`, `dialect = gnu`, and `X = "ab"` yields an **atom**.
Confirms s153. But `PROLOG-SWI-SYNTAX-SEMANTICS.md` §0 shows the target is **not binary**:

| System | default |
|---|---|
| ISO / GNU (both versions) | `codes` |
| **SWI 10.1.5 default** | **`string`** (its own type) |
| SWI `--traditional` | `codes` |
| **SCRIP** | **`atom`** — matches none |

PL-SYNTAX-2 is written as *`codes` vs keep `atom`*. Choosing SWI parity instead means **building a
string type first** (`pl-string.c`); it is downstream of a type rung, not a flag flip. **The rung must
say which dialect it is buying.**

---

## 5. GATES / HYGIENE

- `make -j4 scrip` rc=0, `make libscrip_rt` rc=0, **`-O0`**, zero errors. **No `-O2`, none sought, no Lon directive needed or quoted.**
- **NO SOURCE MODIFIED** — measurement + probe only. Therefore **no rung suite, no `no_new_global`, no
  medium-invisible gate, and the BB-CODEGEN DESIGN SET (PLAN step 6) did not apply.** Nothing in this
  session touched IR, lower, templates or codegen.
- Foreground `timeout 280 make -j4` used throughout. **No detached build attempted** (s126/s154 trap).
- gprolog install hit the **same broken-mirror doc-package failure s151 documented**; same fix worked
  (`apt-get update` + `--no-install-recommends`). That note in the tracker paid for itself.

## 6. WHAT THIS FINDING DOES **NOT** CLAIM

- **Every SCRIP row above is PROBED LIVE**, not read. Every GNU 1.4.5 row is a live run of the same
  source. GNU 1.6.0 and SWI 10.1.5 rows are **source reads, not runs** — no 1.6.0 or SWI binary exists
  in this container.
- **No fix was attempted or landed.** §0's `PL-STRICT-1` is a PROPOSAL for Lon, not an adopted rung.
- The `~t~|~+` column-stop family is confirmed missing but **its correct output was not specified** —
  that needs a reference run, which needs a 1.6.0 or SWI binary.
- I did **not** re-run the 164/164 rung suite (no source changed, so it proves nothing new about this
  session; the last green is s152's).
