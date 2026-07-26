# PROLOG-SYNTAX-TRACKER.md — the syntax axis (PL-SYNTAX-1)

Companion to `PROLOG-ISO-TRACKER.md` (ISO 13211-1 predicate rows) and `PROLOG-DIALECT-TRACKER.md`
(GNU/SWI predicate rows). **Those two are structurally blind to everything in this file** — operator
tables, reader escapes, flags, format directives, `write_term/2` options and error-term shapes are not
`set_bip_name` rows, so no predicate-census instrument can see them. s152 named this gap and STOPPED
rather than ship a wrong number. This file closes the operator half of it.

Sources of truth, read directly this session (symlinked at `SCRIP/refs/`):
- GNU Prolog: `refs/gprolog-master/src/EnginePl/oper.c` (`Pl_Init_Oper`), `src/BipsPl/flag_c.c`,
  `src/BipsPl/format_c.c`, `src/BipsPl/write_supp.{c,h}`
- SWI-Prolog: `refs/swipl-devel-master/src/pl-op.c` (`operators[]`), `src/os/pl-prologflag.c`,
  `src/os/pl-fmt.c`, `src/pl-write.c`
- SCRIP: `src/parser/prolog/prolog_parse.c` (`BIN_OPS[]` + hardcoded prefix arms),
  `src/parser/prolog/prolog_lex.c`, `src/runtime/unification.c` (`g_pl_flags[]`)

---

## ⭐⭐ THE INSTRUMENT FINDING — WHY s152's FIRST PASS RETURNED `gprolog=0 swi=1 SCRIP=0`

All three tables exist and are large. The zero/one counts were **pure extraction failure**, three
different causes, one per system — the s152 harness-tell rule (*a uniform result across a diverse set
is a harness tell, not a finding*) applied and was correctly obeyed.

| System | Why the naive grep found nothing | Real shape |
|---|---|---|
| **GNU** | Operators are **not** `op/3` directives in a `.pl` file. They are a C macro table `ADD_OPER(prec, TYPE, "name")` inside `Pl_Init_Oper()`, in `EnginePl/` — the *engine*, not `BipsPl/`. | 67 `ADD_OPER` rows = **45 core + 22 FD** |
| **SWI** | `OP(ATOM_star, OP_YFX, 400)` — the operator **text appears only in a trailing `/* * */` comment**; the C token is an atom constant. Grepping for operator literals matches the comment at best, nothing at worst. | **64 active rows** (+1 commented-out `?=>`), 61 distinct names |
| **SCRIP** | `BIN_OPS[]` is found easily — but **prefix operators are not in any table**. They are hardcoded `strcmp` arms in `parse_term`. A table-only diff reports SCRIP as having zero prefix operators, which is false. | **43 infix (table) + 13 prefix (hardcoded strcmp)** |

⭐ **RULE (direct sibling of s152's admission-site rule, now proven on a second instrument):
AN OPERATOR CENSUS MUST ENUMERATE ADMISSION *MECHANISMS*, NOT ADMISSION *TABLES*.** SCRIP admits
prefix operators by `strcmp` exactly as `lower_prolog.c` admits `< > =< >= =:= =\=` by static
name-array — same defect class, different file. Any future syntax audit must sweep: static table,
`strcmp` arm, lexer special-case, and parser-level hardcoding.

⚠ **PATH LESSON REPEATED (s151's rule, hit twice more this session).** SWI's flag table is in
`src/os/pl-prologflag.c` and its format engine in `src/os/pl-fmt.c` — **`grep src/*.c` misses both.**
First pass returned 18 flags; the real count is 159. `src/` and `src/os/` are different directories.

---

## 1. OPERATOR TABLE — THREE-WAY DIFF (the PL-SYNTAX-1 deliverable)

**Totals (distinct names):** GNU core **41** · SWI **61** · SCRIP **54** (43 infix + 13 prefix).
GNU additionally ships 22 FD (finite-domain) operators — `#=`, `#<`, `#\/` etc. — which are a solver
extension, out of scope for SCRIP and excluded from the core count.

### 1.1 ⛔ DEFECT — `:` HAS THE WRONG PRECEDENCE IN SCRIP (200 vs 600)

```
GNU:    ADD_OPER(600, XFY, ":")
SWI:    OP(ATOM_colon, OP_XFY, 600)
SCRIP:  { ":", 200, ASSOC_RIGHT }
```

**Both references agree on 600; SCRIP says 200.** This is a real, shipped parse divergence, not a
cosmetic one — 200 binds tighter than `**`/`^`, so any term mixing `:` with arithmetic or comparison
parses differently from both references. `lists:append(X,Y,Z)` still parses (single qualification),
but `M:F/A`, `M:G :- B`, and module-qualified goals inside arithmetic will not. Blast radius is the
module-qualification syntax generally.

### 1.2 ⛔ DEFECT — `|` IS NOT AN OPERATOR IN SCRIP AT ALL

```
GNU:    ADD_OPER(1105, XFY, "|")
SWI:    OP(ATOM_bar, OP_XFY, 1105)   + a special-case guard at pl-op.c
SCRIP:  lexed as TK_PIPE (prolog_lex.c:290); ZERO occurrences in prolog_parse.c
```

`|` is tokenised for list-tail syntax `[H|T]` only. As an **infix operator at 1105** — i.e. `(a | b)`
as a synonym for disjunction, which ISO permits and both references implement — it does not exist.
Any source using bare `|` as disjunction outside a list will not parse.

### 1.3 Missing from SCRIP, present in BOTH references
`?-` (1200 fx) · `|` (1105 xfy)

`?-` is likely benign — SCRIP parses directives structurally rather than as a prefix operator — but it
is **unverified**, and the `\+`-by-strcmp precedent says "handled elsewhere" must be *probed*, not
assumed. Flagged, not claimed.

### 1.4 Missing from SCRIP, SWI-only (all legitimately optional)
`=>` `==>` (SSU) · `:<` `>:<` (dicts) · `as` · `initialization` `public` `table` `thread_local`
`thread_initialization` `volatile` (1150 fx declaration operators)

⚠ Note the axis asymmetry these expose: **GNU does not put `dynamic`/`discontiguous`/`multifile` in
its operator table at all** (they are handled by the directive reader), whereas SWI declares them as
1150 fx operators. SCRIP follows the **SWI** shape (hardcoded 1150 prefix arms) while its `dialect`
flag reports `gnu`. Not a defect — but the two axes genuinely differ here, and a "GNU-compatible"
claim should not be read as covering this.

### 1.5 Present in SCRIP, absent from GNU (SWI-side or SCRIP-local)
Legitimately SWI-tracking: `=@=` `\=@=` `rdiv` `xor` `discontiguous` `dynamic` `meta_predicate`
`module_transparent` `multifile`
SCRIP-local, in **neither** reference: **`@` at 900 xfx** · **`?=`** · `not` · `use_module`
`ensure_loaded` `mode` (the last three as 1150 prefix)

⚠ **`@` at 900 is in no reference operator table and should be justified or removed** — it occupies a
priority band between `\+` (900 fy) and `=` (700), and nothing in ISO, GNU or SWI puts a bare `@`
there. `?=` is a real SWI *predicate* (`?=/2`) but is **not an operator** in SWI's table.

---

## 2. PROLOG FLAGS

| | count | source |
|---|---|---|
| GNU | **42** | `flag_c.c`, `NEW_FLAG_*` macros |
| SWI | **159** tree-wide (**141** in `os/pl-prologflag.c`) | `setPrologFlag(...)` |
| SCRIP | **7** | `unification.c:1588` `g_pl_flags[]` |

SCRIP's seven: `bounded` `max_integer` `min_integer` `double_quotes` `unknown` `occurs_check` `dialect`.

### 2.1 ⛔ DEFECT — `double_quotes` DEFAULT CONTRADICTS BOTH THE DIALECT FLAG AND ISO

```
ISO 13211-1 default:  codes
GNU default:          PF_QUOT_AS_CODES          -> codes
SWI default:          traditional ? codes : string
SCRIP default:        "atom"                    <-- neither
SCRIP dialect flag:   "gnu"                     <-- claims GNU
```

SCRIP reports `dialect = gnu` while defaulting `double_quotes` to `atom`, which GNU sets to `codes`.
**A conforming GNU program whose double-quoted strings are consumed as code lists will silently get
atoms instead** — silent wrong behaviour, not a parse error. This is the highest-severity item found
this session, above the `:` precedence bug, because it is silent and affects every string literal.

⚠ Also note GNU supports six `double_quotes` values (`codes chars atom codes_no_escape
chars_no_escape atom_no_escape`) and a `back_quotes` flag; SCRIP's entry is a plain 4-field row with
no value-set validation visible at the table.

---

## 3. FORMAT DIRECTIVES

| | count | set |
|---|---|---|
| GNU | 22 | `% ? D E G N R S W d f g i k n p q r w ~` |
| SWI | 29 | `+ @ D E F G H I N R W a c d e f g h i k n p q r s t w \| ~` |

SWI-only: `+ @ F H I a c e h s t |` · GNU-only: `% ? S`
SCRIP: **not audited this session** — `format/2` directive handling was not located in the time
available. This row is OPEN, and is explicitly *unmeasured* rather than zero.

---

## 4. `write_term/2` OPTIONS

| | count |
|---|---|
| GNU | **8** — `ignore_ops max_depth numbervars portrayed priority quoted space_args variable_names` |
| SWI | **29** — adds `attributes back_quotes blobs brace_terms character_escapes character_escapes_unicode cycles dotlists float_format fullstop integer_format max_text module nl no_lists partial portable portray portray_goal quote_non_ascii spacing truncated` |
| SCRIP | **8/8 ACCEPTED** — probed live, see below |

GNU's 8 is effectively the ISO set. **SCRIP accepts all 8 without error or failure** — no option is
rejected. Observable effect, writing `'it''s'+f(A,B)`:

| Option | Effect observed | |
|---|---|---|
| `quoted(true)` | `'it''s'+f(...)` — quoting applied | ✅ demonstrated |
| `ignore_ops(true)` | `+(it's,f(...))` — canonical form | ✅ demonstrated |
| `max_depth(2)` | `it's+f(...,...)` — elided | ✅ demonstrated |
| `space_args(true)` | `f(_G0,_G1)` — **no space inserted** | ⚠ accepted, no visible effect |
| `numbervars` `portrayed` `priority` `variable_names` | no change | ➖ inconclusive — probe lacked a `'$VAR'` term, portray hook, and matching var name |

⚠ **`space_args` is a SUSPECTED gap, NOT a finding.** GNU writes `f(a, b)` with a space after the
comma under this option; SCRIP emitted none. One probe, one term — insufficient. The four
inconclusive rows are **probe-design limits, not evidence of absence**; a targeted probe per option
is the PL-SYNTAX-4 rung, and it should not assume any of the five are broken.

GNU's 8 is effectively the ISO set. This is the cleanest sub-axis to close next: 8 rows, a single
reference, and s151 already touched the writer (`pl_write`/`pl_writeq_term`,
`src/parser/prolog/prolog_builtin.c` — note the directory, per §0's path lesson).

---

## 5. READER ESCAPES / NUMBER SYNTAX — **MEASURED, ALL GREEN**

String escapes (`prolog_lex.c`): `\a \b \e \f \n \r \t \v`, `\xHH`, octal `\NNN`, literal
`! " ( ) , . ; [ ] ` { } |` and `\\`.

**Probed live — every construct correct:**

| Construct | Expected | SCRIP | |
|---|---|---|---|
| `0'a` | 97 | 97 | ✅ |
| `0x1F` | 31 | 31 | ✅ |
| `0o17` | 15 | 15 | ✅ |
| `0b101` | 5 | 5 | ✅ |
| `0'\n` | 10 | 10 | ✅ |
| `0'\\` | 92 | 92 | ✅ |
| `0' ` (space) | 32 | 32 | ✅ |
| `{a,b}` | `{a,b}` | `{a,b}` | ✅ |

**No gap on this axis.** `\e` is a GNU/SWI extension beyond ISO and is present — consistent with both
references, so not flagged.

⚠⚠ **HARNESS ERROR CAUGHT ON MYSELF — THE RULE APPLIES TO THE AUDITOR TOO.** The first pass reported
`0'\n` as a **parse error** and very nearly entered this file as a defect. It was shell escaping: a
`printf` probe emitted `0'\\n` (double backslash) into the test file, so SCRIP correctly rejected
malformed input. The tell was visible in the probe's own echoed value and nowhere else. Re-run via
heredoc, it returns 10. ⭐ **RULE: WHEN A PROBE REPORTS A DEFECT, VERIFY THE PROBE EMITTED WHAT YOU
THINK IT EMITTED — echo the generated source, not just the result.** A false gap manufactured by the
instrument is indistinguishable from a real one in the output, which is precisely s152's lesson
pointed back at the measuring apparatus rather than the tree.

---

## 6. ERROR-TERM SHAPES

Not audited. s151/s152 both observed the standing cosmetic divergence — SCRIP emits `_G0` where GNU
emits `Name/Arity` in the context argument of ISO error terms — carried across every error family.
Tracked there; not re-derived here.

---

## 7. BEHAVIOURAL PROBE — ALL THREE DEFECTS CONFIRMED LIVE

Built `scrip` from clean tree, `-O0` (Makefile default, no `-O2` directive), zero build errors.
Ran mode-3 (`--run`). **Every static finding survived; nothing was falsified.** This is the step s152's
rule demands and it changed nothing — which is itself the useful result, since the same rule's prior
application disproved 7 of 15 static gaps.

| # | Probe | Result | Verdict |
|---|---|---|---|
| 1 | `X = (a:b+c)` | prints `:(a,b)+c` → parsed `(a:b)+c` | ⛔ **CONFIRMED.** `:` binds tighter than `+`. Both references (600) give `a:(b+c)`. |
| 2 | `( t(9) \| t(1) )` | `parse error: expected . at end of clause` | ⛔ **CONFIRMED.** Hard parse failure, not a semantic difference. |
| 3 | `X = "ab"` | `atom_SCRIP_divergent` / `ab` / `flag(atom)` / `dialect(gnu)` | ⛔ **CONFIRMED.** Double-quoted literal is an atom; flag reports `atom`; dialect reports `gnu`. GNU itself defaults `codes`. |

**Supplementary probes (§1.5 questions, now answered):**
- `a @ b` → `@(a,b)` — **`@` at 900 is live and parses.** Present in no reference operator table.
- `a ?= b` → `?=(a,b)` — **`?=` is live as an operator.** SWI has `?=/2` as a *predicate*, not an operator.
- `a:b:c` → `:(a,:(b,c))` — **associativity is correct (xfy).** Only the *priority* is wrong, so the
  fix in PL-SYNTAX-3 is a one-token change `200 → 600`, not a restructure.
- `?-` directive form loads and runs — the §1.3 "unverified" flag on `?-` is **cleared**; its absence
  from the operator table is benign, directives are handled structurally as suspected.

⭐ **CONSEQUENCE FOR PL-SYNTAX-3: the `:` fix is now known to be one edit** —
`prolog_parse.c` `{ ":", 200, ASSOC_RIGHT }` → `{ ":", 600, ASSOC_RIGHT }`. Not attempted this
session: changing a priority in `BIN_OPS[]` reorders parses tree-wide, so it needs the rung's full
gate board (164/164 x3 modes) behind it, not a drive-by edit.

## RUNG LADDER

- [x] **PL-SYNTAX-1** — operator table three-way diff. **DONE this session, STATIC + PROBED.** Three
      shipped defects found and all three confirmed live (§7); two unjustified local operators (`@`,
      `?=`) confirmed live; instrument failure root-caused for all three systems.
- [ ] **PL-SYNTAX-2** — `double_quotes` default: decide `codes` (ISO+GNU, matches the `dialect=gnu`
      claim) vs keeping `atom`. **Highest severity open item; silent-wrong-behaviour class.**
- [ ] **PL-SYNTAX-3** — fix `:` to 600 xfy; add `|` as 1105 xfy; justify-or-remove `@`/`?=`.
- [~] **PL-SYNTAX-4** — `write_term/2`: all 8 GNU options ACCEPTED (probed). `space_args` suspected no-op; 4 options inconclusive under this probe. Needs one targeted probe per option.
- [ ] **PL-SYNTAX-5** — format directives: audit SCRIP against GNU's 22.
- [x] **PL-SYNTAX-6** — reader: `0'c` `0x` `0o` `0b` escaped-char-codes `{}/1` ALL CORRECT (probed). **CLOSED, no gap.**
- [ ] **PL-SYNTAX-7** — flags: SCRIP 7 vs GNU 42; triage which of GNU's are load-bearing.

## ⚠ HONESTY BOUNDARY ON THIS FILE

§1 and §2 are **measured** — every number came from reading the named source this session, and the
two defects were each confirmed by a direct three-way spot-check before being written down.
§3 GNU/SWI columns are measured; the SCRIP column is **absent, not zero**. §4 GNU/SWI measured,
SCRIP absent. §5 is **partial and explicitly unverified**. §6 is **not done**.

Per the s152 rule (*a false gap is worse than a missing one*), nothing above is marked as a SCRIP gap
unless the SCRIP side was actually read. Where it was not read, the row says so.

**BEHAVIOURAL PROBE RUN — see §7. All three defects CONFIRMED LIVE, none falsified.** The static
findings in §1 and §2 survived contact with the compiler; §3–§6 remain static/absent as stated above.
