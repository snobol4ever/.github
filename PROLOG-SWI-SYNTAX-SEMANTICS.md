# PROLOG-SWI-SYNTAX-SEMANTICS.md — the SWI axis, syntax + semantics, MEASURED

**Companion to** `PROLOG-SYNTAX-TRACKER.md` (three-way operator/flag diff, PL-SYNTAX-1),
`PROLOG-DIALECT-TRACKER.md` (GNU/SWI predicate rows) and `PROLOG-ISO-TRACKER.md` (ISO 13211-1 rows).
Those files are **predicate-census or three-way-diff instruments**. This file is the **SWI axis read
end-to-end as a language**: what the reader accepts, what the writer emits, what the flags mean, and
where SWI is not ISO.

## PROVENANCE — every row below was read from source THIS SESSION

| Axis | Source of truth | Extraction |
|---|---|---|
| Operators | `refs/swipl-devel-master/src/pl-op.c` `operators[]` :667-731 | joined against `src/ATOMS` |
| Atom text | `refs/swipl-devel-master/src/ATOMS` (1005 `A` rows) | `A <name> "<string>"` |
| Flags | `src/os/pl-prologflag.c` + `src/pl-arith.c` + `src/pl-tabling.c` + `boot/*.pl` | 4 admission sites |
| Reader escapes | `src/pl-read.c` `escape_char()` :2353-2480 | switch-arm sweep |
| Numbers | `src/pl-read.c` `scan_number()` :2265, :2825 | switch-arm sweep |
| `format/2` | `src/os/pl-fmt.c` directive switch :536-950 | switch-arm sweep |
| `write_term/2` | `src/pl-write.c` option table :2151-2179 | table read |
| Error terms | `src/pl-error.c` `ERR_*` | 54 classes |
| Dicts | `src/pl-read.c` `read_dict()` :4786-4967 | function read |

**Versions:** SWI-Prolog `10.1.5` · GNU Prolog `1.6.0` (both from the uploaded archives, symlinked at
`SCRIP/refs/`). ⚠ The trackers' GNU rows were taken against **1.4.5** (the `apt` build used s151/s152);
this archive is **1.6.0**. Where a GNU number here disagrees with an older tracker row, THE VERSION
DIFFERENCE IS THE FIRST SUSPECT, not the earlier session's arithmetic.

---

## ⭐⭐ 0. THE FINDING THAT CHANGES PL-SYNTAX-2 — `double_quotes` HAS **FOUR** VALUES IN PLAY, NOT TWO

`PROLOG-SYNTAX-TRACKER.md` §2.1 records the defect as *"SCRIP defaults to `atom`; ISO/GNU both default
`codes`"*. That is correct as far as it goes, but the SWI column is **mode-dependent** and the tracker
does not say so:

```c
/* src/os/pl-prologflag.c:2148 */
setPrologFlag("double_quotes", FT_ATOM, GD->options.traditional ? "codes" : "string");
setPrologFlag("back_quotes",   FT_ATOM, GD->options.traditional ? "symbol_char" : "codes");
```

| System | `double_quotes` default | `back_quotes` default |
|---|---|---|
| ISO 13211-1 | `codes` | (not specified) |
| GNU Prolog 1.6.0 | `codes` (`PF_QUOT_AS_CODES`, `BipsPl/flag_c.c:225`) | — |
| **SWI 10.1.5 default** | **`string`** ← a fourth value, SWI's own type | `codes` |
| **SWI 10.1.5 `--traditional`** | `codes` | `symbol_char` |
| **SCRIP** | **`atom`** ← matches NONE of the four | — |

⭐ **CONSEQUENCE FOR THE RUNG.** PL-SYNTAX-2 is written as a binary choice (`codes` vs keep `atom`).
It is not binary. `"..."` → `string` requires a **distinct string type** that SCRIP does not have; SWI
built one (`PL_STRING`, `src/pl-string.c`) precisely so `"..."` need not be a code list. So:
- Targeting **GNU/ISO parity** → `codes`, and the `dialect=gnu` claim becomes true. Cheap, correct, closes the defect.
- Targeting **SWI parity** → needs the string type FIRST; `double_quotes` is downstream of a type-system rung, not a flag flip.
These are different amounts of work and the ladder should say which one it is buying.

---

## 1. OPERATOR TABLE — SWI 10.1.5, COMPLETE (64 active rows, 61 distinct names)

Extracted by resolving `OP(ATOM_x, OP_t, p)` against `ATOMS` — **not** from the trailing comments that
defeated the s152 first pass. Sorted by precedence descending.

| Operator | Type | Prec |
|---|---|---|
| `:-` | fx | 1200 |
| `?-` | fx | 1200 |
| `-->` | xfx | 1200 |
| `:-` | xfx | 1200 |
| `==>` | xfx | 1200 |
| `=>` | xfx | 1200 |
| `discontiguous` | fx | 1150 |
| `dynamic` | fx | 1150 |
| `initialization` | fx | 1150 |
| `meta_predicate` | fx | 1150 |
| `module_transparent` | fx | 1150 |
| `multifile` | fx | 1150 |
| `public` | fx | 1150 |
| `table` | fx | 1150 |
| `thread_initialization` | fx | 1150 |
| `thread_local` | fx | 1150 |
| `volatile` | fx | 1150 |
| `|` | xfy | 1105 |
| `;` | xfy | 1100 |
| `*->` | xfy | 1050 |
| `->` | xfy | 1050 |
| `,` | xfy | 1000 |
| `\+` | fy | 900 |
| `:<` | xfx | 700 |
| `<` | xfx | 700 |
| `=` | xfx | 700 |
| `=..` | xfx | 700 |
| `=:=` | xfx | 700 |
| `=<` | xfx | 700 |
| `==` | xfx | 700 |
| `=@=` | xfx | 700 |
| `=\=` | xfx | 700 |
| `>` | xfx | 700 |
| `>:<` | xfx | 700 |
| `>=` | xfx | 700 |
| `@<` | xfx | 700 |
| `@=<` | xfx | 700 |
| `@>` | xfx | 700 |
| `@>=` | xfx | 700 |
| `\=` | xfx | 700 |
| `\==` | xfx | 700 |
| `\=@=` | xfx | 700 |
| `as` | xfx | 700 |
| `is` | xfx | 700 |
| `:` | xfy | 600 |
| `+` | yfx | 500 |
| `-` | yfx | 500 |
| `/\` | yfx | 500 |
| `\/` | yfx | 500 |
| `*` | yfx | 400 |
| `/` | yfx | 400 |
| `//` | yfx | 400 |
| `<<` | yfx | 400 |
| `>>` | yfx | 400 |
| `div` | yfx | 400 |
| `mod` | yfx | 400 |
| `rdiv` | yfx | 400 |
| `rem` | yfx | 400 |
| `xor` | yfx | 400 |
| `+` | fy | 200 |
| `-` | fy | 200 |
| `\` | fy | 200 |
| `**` | xfx | 200 |
| `^` | xfy | 200 |

**Plus one commented-out row:** `?=>` xfx 1200 (`ATOM_ssu_choice`, `pl-op.c:685`) — SSU choice-rule
syntax, present in the source but disabled. Counted separately; it is NOT active.

### 1.1 SWI-only operators (absent from GNU 1.6.0's `Pl_Init_Oper`)

| Operator | Type | Prec | What it is |
|---|---|---|---|
| `=>` | xfx | 1200 | SSU (single-sided unification) commit rule |
| `==>` | xfx | 1200 | SSU DCG rule |
| `?=>` | xfx | 1200 | SSU choice rule — **commented out in source** |
| `dynamic` `discontiguous` `initialization` `meta_predicate` `module_transparent` `multifile` `public` `table` `thread_local` `thread_initialization` `volatile` | fx | 1150 | **Directive operators.** GNU parses these as plain compound terms; SWI makes each a prefix operator so `:- dynamic foo/1.` needs no parens. **11 rows — this is the single biggest structural difference between the two tables.** |
| `*->` | xfy | 1050 | soft cut — **also in GNU 1.6.0** (`oper.c:105`), so NOT SWI-only |
| `:<` | xfx | 700 | dict selection |
| `>:<` | xfx | 700 | dict partial unification |
| `=@=` `\=@=` | xfx | 700 | structural equivalence (variant check) |
| `as` | xfx | 700 | used in `dynamic X as shared` etc. |
| `rdiv` | yfx | 400 | rational division |
| `xor` | yfx | 400 | bitwise xor (GNU spells this `#\` in FD, and has no `xor`) |

### 1.2 The `|` and `:` rows — CONFIRMING THE TWO SHIPPED SCRIP DEFECTS ON A SECOND SOURCE

| | GNU 1.6.0 | SWI 10.1.5 | SCRIP |
|---|---|---|---|
| `\|` | xfy 1105 (`oper.c:100`) | xfy 1105 (`pl-op.c:689`) | **ABSENT as operator** — list-tail `TK_PIPE` only |
| `:` | xfy 600 (`oper.c:131`) | xfy 600 (`pl-op.c:682`) | **200** |

Two independent implementations, two independent table encodings, **identical numbers**. The
PL-SYNTAX-3 defects are confirmed against a second reference; there is no dialect ambiguity to hide in.

---

## 2. READER — TERM SYNTAX

### 2.1 Escape sequences (`escape_char()`, `pl-read.c:2353`)

| Escape | Value | Note |
|---|---|---|
| `\a` | 7 | BELL |
| `\b` | 8 | backspace |
| `\c` | — | **skip `\c` + following blanks** (line continuation, not a character) |
| `\e` | 27 | ESC — **gcc extension, NOT ISO** |
| `\f` | 12 | form feed |
| `\n` | 10 | newline |
| `\r` | 13 | carriage return |
| `\s` | 32 | **space — NU-Prolog/Quintus extension, NOT ISO** |
| `\t` | 9 | tab |
| `\v` | 11 | vertical tab |
| `\0..7` | octal | terminated by `\` |
| `\xNN\` | hex | terminated by `\` |
| `\uXXXX` | 4-hex Unicode | **SWI extension, NOT ISO** |
| `\UXXXXXXXX` | 8-hex Unicode | **SWI extension, NOT ISO** |
| `\<newline>` | — | line continuation; `\<CR><LF>` folds to the same |
| `\\` `\'` `\"` `` \` `` | literal | quote escapes |

⚠ **Four of these are non-ISO** (`\e`, `\s`, `\u`, `\U`).

⛔ **CORRECTED 2026-07-27 s155 BY LIVE RUN — THIS ROW IS VERSION-DEPENDENT AND MY FIRST DRAFT WAS
INCOMPLETE.** I originally wrote that GNU has `\s`/`\e` and called this a mere *scope* note on a
closed rung. Running the **actual 1.4.5 binary** falsified the simple version of that: 1.4.5 **rejects
both** as `syntax error`, while the **1.6.0 source** in `refs/` accepts both under `!strict_iso`
(`BipsPl/scan_supp.c:678-685`). Two different GNUs, opposite answers.

**And SCRIP does a third thing: it silently passes the character through** (probed —
`'a\sb'` → `[97,92,115,98]`, `'a\zb'` → `[97,92,122,98]`), matching neither. **PL-SYNTAX-6 is
therefore REOPENED, not scope-corrected** — see
`FINDING-2026-07-27-CLAUDE-PL-SILENT-ACCEPTANCE-CLASS-AND-PL-SYNTAX-6-REOPENED.md` §2.

### 2.2 Number syntax (`scan_number()`, `pl-read.c:2265` / `:2825`)

| Form | Meaning |
|---|---|
| `0b1010` `0o17` `0x1F` | binary / octal / hex (`pl-read.c:2825`) |
| `0'c` | character code; `0'\n` etc. go through `escape_char` (`:2798`) |
| `123_456_789` | **digit group separators — SWI extension** (cf. `~I` format directive) |
| `1r3` | **rational** under `rational_syntax=natural`; `1 rdiv 3` under `compatibility` |
| `1.0e10` `1.0Inf` `nan` | floats + IEEE specials |
| `<radix>'<digits>` | e.g. `16'FF` — general radix |

`rational_syntax` default is `compatibility` unless built `RAT_NATURAL` (`pl-prologflag.c:2118`);
`rationals` is a read-only `true` in this build.

### 2.3 SWI-specific term syntax with NO ISO counterpart

| Syntax | Read as | Source |
|---|---|---|
| `Tag{k:v, ...}` | **dict** | `read_dict()`, `pl-read.c:4786` |
| `"text"` | **string object** (default mode) | `pl-string.c` |
| `` `text` `` | code list (default mode) | `back_quotes` flag |
| `Dict.key` | functional notation on dicts, goal-expanded | `pl-dict.c` |

**None of these exist in GNU Prolog, and none are ISO.** Any SWI-parity claim that reaches the reader
has to decide about dicts and strings explicitly — they are type-system features wearing syntax.

---

## 3. FLAGS — 4 ADMISSION SITES, NOT 1

Applying the tracker's own rule (*enumerate admission MECHANISMS, not admission TABLES*):

| Site | Distinct flags | What lives there |
|---|---|---|
| `src/os/pl-prologflag.c` | **141** (137 unique via `setPrologFlag`) | the main table |
| `src/pl-arith.c` | **11** | `float_*` (overflow, rounding, undefined, zero_div, max, min) |
| `src/pl-tabling.c` | **7** | `max_answers_for_subgoal*`, `max_table_*`, `table_monotonic` |
| `boot/*.pl` | 20+ | `argv`, `stack_limit`, `optimise`, `toplevel_goal`, `sandboxed_load`, … set at Prolog level |

⚠ **A `grep src/*.c` finds 141 and misses 18 C-level flags plus the whole boot-level set.** This is the
s151 path lesson recurring a third time: `src/`, `src/os/` and `boot/` are three different places.
`PROLOG-SYNTAX-TRACKER.md` reports 159 for SWI; my sweep gives 137 unique in the main table and 155
across the three C sites. **The two numbers were produced by different extraction rules and neither is
"the" count** — say which rule produced any flag number you quote.

By type (main table): `FT_BOOL` 70 · `FT_ATOM` 47 · `FT_INTEGER` 17 · `FT_FLOAT` 1.

### 3.1 Flags that change what the READER ACCEPTS (the ones that matter for a parser)

| Flag | Default | Effect on syntax |
|---|---|---|
| `double_quotes` | `string` (`codes` traditional) | type of `"..."` |
| `back_quotes` | `codes` (`symbol_char` traditional) | type of `` `...` `` |
| `rational_syntax` | `compatibility` | whether `1r3` reads |
| `traditional` | `false` (**read-only**) | master switch: dicts+strings off, ISO-ish reader on |
| `allow_dot_in_atom` | — | `a.b` as one atom vs dict access |
| `allow_variable_name_as_functor` | — | `Foo(x)` legality |
| `occurs_check` | `false` | unification semantics, not syntax — listed because it silently changes `=/2` |
| `character_escapes` | — | whether `\` escapes are processed at all |
| `unknown` | `error` | existence_error vs fail on undefined predicate |

⭐ `traditional` is **read-only after startup** — it is a command-line mode (`--traditional`), not a
runtime toggle. A SWI-parity target must pick a mode; there is no single "SWI syntax".

---

## 4. `format/2,3` DIRECTIVES — 29, COMPLETE (`os/pl-fmt.c`)

| Dir | Meaning | | Dir | Meaning |
|---|---|---|---|---|
| `~a` | atomic, unquoted | | `~i` | ignore one argument |
| `~c` | character code (`~Nc` repeats) | | `~k` | `write_canonical` |
| `~d` | integer (`~Nd` inserts decimal point) | | `~p` | `print/1` (portray hook) |
| `~D` | grouped integer (`1,000,000`) | | `~q` | `writeq` |
| `~I` | Prolog group separators (`1_000_000`) | | `~w` | `write` |
| `~e` `~E` | exponential float | | `~W` | `write_term/2` with options |
| `~f` `~F` | fixed float | | `~s` | string / code list |
| `~g` `~G` | shortest of f/e | | `~@` | **call a goal, capture its output** |
| `~h` `~H` | precise float | | `~n` | newline (`~Nn` repeats) |
| `~r` `~R` | radix (`~8r` octal, `~R` uppercase) | | `~N` | newline **only if not already at column 0** |
| `~t` | fill/insert tab | | `~\|` | column stop (absolute) |
| `~+` | column stop (relative) | | `~~` | literal `~` |

**SWI-only vs GNU's 22:** `~I` (group separators), `~@` (goal output capture), `~W`, `~h`/`~H`,
`~F`/`~G`/`~E` uppercase variants. `~t~|~+` column machinery exists in both.

PL-SYNTAX-5 is written as *"audit SCRIP against GNU's 22"*. Against SWI it is **29**, and `~@` in
particular is not a formatting directive at all — it is a **control construct inside a format string**
(it calls a goal). If SCRIP ever targets `~@`, it belongs on a control ladder, not a formatting one.

### 4.1 SCRIP COLUMN — **PROBED LIVE s155** (mode 3, one `format/2` per directive)

**WORKS (14):** `~a` `~w` `~q` `~d` `~s` `~c` `~e` `~f` `~g` `~r` `~p` `~i` `~N` `~~`
**MISSING (12), all producing EMPTY OUTPUT AND NO ERROR:** `~t` `~|` `~+` `~D` `~k` `~W` `~E` `~F`
`~G` `~I` `~h` `~@`

⛔ **`GOAL-PROLOG-BB.md` PL-ISO-9 names 11 directives as OPEN; 8 of them work.** False gap — see the
FINDING §3. The correct OPEN set is `~t ~| ~+` (column stops) plus `~D ~k ~W`.
⛔ **The silent drop is its own defect** (FINDING §0 class 2): an unknown directive must raise, not vanish.

---

## 5. `write_term/2` OPTIONS — 29 (`pl-write.c:2151`)

`quoted` · `quote_non_ascii` · `ignore_ops` · `portable` · `dotlists` · `brace_terms` · `numbervars` ·
`portray` · `portrayed` · `portray_goal` · `character_escapes` · `character_escapes_unicode` ·
`max_depth` · `max_text` · `truncated` · `module` · `back_quotes` · `attributes` · `priority` ·
`partial` · `spacing` · `blobs` · `cycles` · `variable_names` · `nl` · `fullstop` · `no_lists` ·
`integer_format` · `float_format`

Types: `OPT_BOOL` 20 · `OPT_ATOM` 6 · `OPT_INT` 3 · `OPT_TERM` 3 (`portray_goal`, `truncated`, `variable_names`).

**ISO 13211-1 requires only 4:** `quoted`, `ignore_ops`, `numbervars`, plus `variable_names` in the
corrigendum. GNU 1.6.0 has 8. SWI has 29. `PROLOG-SYNTAX-TRACKER.md` PL-SYNTAX-4 records *"all 8 GNU
options ACCEPTED"* — that is an 8-of-29 result on the SWI axis, and `variable_names` is the one that
matters most for parity because `print_message`/toplevel output depends on it.

---

## 6. ERROR TERMS — 54 CLASSES (`pl-error.c`)

ISO shape is `error(Formal, Context)`. SWI's 54 `ERR_*` classes group as:

| Group | Members |
|---|---|
| **ISO core** | `ERR_INSTANTIATION` `ERR_TYPE` `ERR_DOMAIN` `ERR_EXISTENCE` `ERR_PERMISSION` `ERR_REPRESENTATION` `ERR_EVALUATION` `ERR_RESOURCE` `ERR_SYNTAX` |
| **Arithmetic** | `ERR_AR_TYPE` `ERR_AR_DOMAIN` `ERR_AR_UNDEF` `ERR_AR_OVERFLOW` `ERR_AR_UNDERFLOW` `ERR_AR_RAT_OVERFLOW` `ERR_AR_TRIPWIRE` `ERR_DIV_BY_ZERO` `ERR_NOT_EVALUABLE` |
| **Procedure/DB** | `ERR_MODIFY_STATIC_PREDICATE` `ERR_MODIFY_STATIC_PROC` `ERR_MODIFY_THREAD_LOCAL_PROC` `ERR_IMPORT_PROC` `ERR_PERMISSION_PROC` `ERR_NOT_IMPLEMENTED_PROC` `ERR_EXISTENCE3` |
| **Streams/OS** | `ERR_STREAM_OP` `ERR_CLOSED_STREAM` `ERR_FILE_OPERATION` `ERR_SYSCALL` `ERR_SHELL_FAILED` `ERR_SHELL_SIGNALLED` `ERR_SHARED_OBJECT_OP` `ERR_DDE_OP` |
| **SWI-specific** | `ERR_DETERMINISM` `ERR_DET_GOAL` `ERR_OCCURS_CHECK` `ERR_DUPLICATE_KEY` (dicts) `ERR_PERMISSION_SSU_DEF` `ERR_PERMISSION_VMI` `ERR_PERMISSION_YIELD` `ERR_BUSY` `ERR_FORMAT` `ERR_FORMAT_ARG` `ERR_NOMEM` `ERR_SIGNALLED` `ERR_FAILED` `ERR_CHARS_TYPE` `ERR_PTR_TYPE` `ERR_PTR_DOMAIN` `ERR_RANGE` `ERR_NOT_IMPLEMENTED` |

This closes `PROLOG-SYNTAX-TRACKER.md` §6, which was marked **not done** — on the SWI side only.
The SCRIP column is **absent, not zero** (I did not read SCRIP's error shapes this session).

---

## 7. SEMANTICS — WHERE SWI IS NOT ISO, AND WHY IT MATTERS TO A BB ENGINE

These are the SWI behaviours that a four-port/Byrd-box engine must decide about, because each one
changes **port topology**, not just a table entry.

| Feature | Semantics | Port consequence |
|---|---|---|
| `*->` soft cut | `(C *-> T ; E)` — if `C` has ≥1 solution, run `T` for **every** solution and never `E`; else `E`. Unlike `->`, does **not** cut `C`'s choice points. | β of the condition stays LIVE. `->` kills it. **These are structurally different boxes.** Already banked in `GOAL-PROLOG-BB.md` as a known gap. |
| SSU `=>` | Head unification is **single-sided**: caller args must match without binding caller vars; commits like a cut on success. | A **determinism-by-construction** rule — no β at all, which is exactly the `bounded` optimisation ARCH-PROLOG.md describes. `=>` is that idea in the source language. |
| `occurs_check` flag | `false` (default), `true`, or `error` | changes `=/2` itself, engine-wide |
| Tabling (`:- table`) | SLG resolution, answer subsumption, `max_answers_for_subgoal` | a **separate solver**, not a box shape |
| Attributed vars | `freeze/2`, `when/2`, coroutining hooks fire on binding | binding is no longer a simple trail write — every `bind()` becomes a potential goal spawn |
| Dicts | `Tag{k:v}` + functional `.key` goal expansion | a **compile-time term rewrite**, i.e. LOWER work |
| `unknown=error` | undefined predicate → `existence_error` | ⭐ SCRIP has a **banked defect** here: *compiled-path silent-fail on undefined predicates*. SWI's default is the correct reference behaviour, and both GNU and ISO agree. |

⭐⭐ **THE ONE THAT CONNECTS TO A LIVE BANKED BUG.** `GOAL-PROLOG-BB.md`'s BANKED list carries
*"compiled-path silent-fail on undefined predicates"* across s151-s154 with no owning rung. Both
references make this an `existence_error` by default (SWI `unknown=error`, `pl-prologflag.c`; ISO
8.5.1). It is not a dialect nicety — **a silent fail on an undefined predicate turns a program bug into
a wrong answer**, and it is the single most user-visible divergence in the banked list.

---

## 8. WHAT THIS FILE DOES **NOT** CLAIM — HONESTY BOUNDARY

Per the s152 rule (*a false gap is worse than a missing one*):

- **Every SWI and GNU row above was read from source this session.** Counts are reproducible by the
  commands in §PROVENANCE.
- **UPDATED s155 — THE SCRIP COLUMN IS NOW FILLED AND PROBED FOR §2.1 (escapes) AND §4 (format).**
  SCRIP was **built (`-O0`) and run** this session; those two axes are live-probed results, not reads,
  and they are cross-checked against a live GNU 1.4.5. See
  `FINDING-2026-07-27-CLAUDE-PL-SILENT-ACCEPTANCE-CLASS-AND-PL-SYNTAX-6-REOPENED.md`.
- **STILL ABSENT (not zero): §5 `write_term/2` options and §6 error terms.** SCRIP's writer was read
  only far enough to see that `pl_wt()` carries `quoted/ignore_ops/numbervars/max_depth`
  (`src/parser/prolog/prolog_builtin.c:394`) — **4 of SWI's 29**. That is a READ, not a probe, and the
  remaining 25 were not checked at all. **Do not quote a SCRIP write_term gap from this file.**
- **§7 semantics: only the `unknown=error` row was probed** (and it diverges — see the FINDING).
  `*->`, SSU, tabling, attributed vars and dicts were **not** probed.
- **Version skew is real:** this archive is GNU **1.6.0**; the trackers used **1.4.5**.

## 9. SUGGESTED RUNGS (proposed, not adopted — Lon's call)

- [ ] **PL-SWI-SYN-1** — decide the `double_quotes` target (§0): GNU/ISO `codes` (cheap, closes the
      shipped defect) vs SWI `string` (needs a string type first). **Blocks PL-SYNTAX-2, which is
      currently written as a binary choice that does not exist.**
- [ ] **PL-SWI-SYN-2** — read the SCRIP side of §2/§4/§5/§6 and fill the absent columns. Cheap, and
      it converts this file from a reference into a diff.
- [ ] **PL-SWI-SYN-3** — `unknown=error`: give the banked silent-fail defect an owning rung (§7).
      Both references and ISO agree; it is the highest-severity item in the banked list.
- [ ] **PL-SWI-SYN-4** — scope-correct PL-SYNTAX-6 (§2.1): it is CLOSED against GNU, but `\u`/`\U`/`\e`/`\s` are unmeasured against SWI.
