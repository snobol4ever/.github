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
| **Arithmetic (s156)** | `src/pl-arith.c` `ar_funcdefs[]` :4848-4937 | joined vs `ATOMS`; single-site proven |
| **Standard order (s156)** | `src/pl-prims.c` :1759/:1804/:1950 + `pl-data.h` :155-163 | function + tag read |
| **Char classes (s156)** | `src/os/pl-ctype.c` `_PL_char_types[]` :1007+ · `pl-read.c` :77-91 | table decode |
| **Control (s156)** | `src/pl-comp.c` `compileBody()` :2287-2410, :966, :1070 | switch-arm sweep |
| **DCG (s156)** | `src/boot/dcg.pl` :58-132 | clause read |

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

#### 2.1.1 ⭐ ADDED s156 — **PL-SWI-SYN-4 CLOSED**: the four escapes measured against SWI, and the mechanism is THREE CALL SITES, not one arm

`PL-SWI-SYN-4` asked whether `\u`/`\U`/`\e`/`\s` were ever compared to the SWI axis. **Answered by
source read of `SCRIP/src/parser/prolog/prolog_lex.c` `decode_escape()` :70-100 vs SWI
`escape_char()`:**

| Escape | SWI 10.1.5 | GNU 1.4.5 | SCRIP | verdict |
|---|---|---|---|---|
| `\e` | 27 | **syntax error** | **27** | ⭐ **SCRIP MATCHES SWI, NOT GNU 1.4.5** |
| `\s` | 32 (space) | syntax error | `\`+`s` (2 chars) | diverges from both |
| `\u`XXXX | 4-hex codepoint | not supported | `\`+`u` (2 chars) | diverges |
| `\U`XXXXXXXX | 8-hex codepoint | not supported | `\`+`U` (2 chars) | diverges |
| `\c` | skip `\c`+blanks | — | `\`+`c` (2 chars) | diverges |

So SCRIP is **not uniformly "GNU-flavoured"** here: on `\e` it already agrees with SWI while the
installed GNU 1.4.5 rejects it. Any rung that "aligns escapes to GNU" would *regress* `\e`.

⛔ **THE BANKED MECHANISM DESCRIPTION IS WRONG IN A WAY THAT MATTERS FOR THE FIX.** The banked entry
reads *"`prolog_lex.c:98` default arm passes char through, never raises"* — one arm, one behaviour.
Source says `decode_escape` returns a **three-valued** status (`1` recognised · `0` line-continuation ·
`-1` unknown) and it has **THREE call sites that treat `-1` in TWO different ways**:

| Call site | Context | On unknown escape `\q` |
|---|---|---|
| :116 | quoted atom `'...'` | pushes **`\` AND `q`** → 2 chars ✔ matches s155's probe |
| :138 | double-quoted `"..."` | pushes **`\` AND `q`** → 2 chars ✔ matches s155's probe |
| :157 | char-code `0'\q` | yields **`(long)'\\'` = 92**; the `q` is consumed and **DISCARDED** |

**The third row is a DIFFERENT defect from the other two and was never probed.** `0'\q` does not
"pass the char through" — it *loses* it and returns backslash. SWI raises `undefined_char_escape`
(`pl-read.c` `undef:` label, `errorWarningA1(...)` → `ESC_ERROR`) in all three positions.

⚠ **STATUS OF THIS ROW: READ, NOT PROBED.** Rows :116/:138 are cross-validated — my source read
predicts exactly the byte sequences s155 measured live, which is why I trust the read for :157. But
**:157 itself has not been run.** Probe `X is 0'\q` before closing anything on it. Fixing only the
`default:` arm would leave the `0'` path returning 92 unless the call site is fixed too.

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
| SSU `=>` | Head unification is **single-sided**: caller args must match without binding caller vars; commits like a cut on success. | A **determinism-by-construction** rule — no β at all, which is exactly the `bounded` optimisation ARCH-LANGUAGES.md describes. `=>` is that idea in the source language. |
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
- **⚠ UPDATED s156 — THIS SECTION NO LONGER COVERS THE WHOLE FILE.** Sections **10-15 were added
  after it.** §10-§14 are SWI **source reads**; §15 is the **SCRIP side, ALSO A SOURCE READ, NOT A
  PROBE** — nothing in §15 was executed, so **every §15 row is a hypothesis with a file:line to aim a
  probe at**, and §15.4 lists what was not read at all (§10/§13/§14 SCRIP columns). Two genuinely new
  conclusions: **§11.2** — SWI's source independently confirms both halves of the banked int/float
  defect, upgrading it from one oracle to two; and **§15.1** — that defect localises to ONE function
  (`rt_pl_term_compare`) whose single missing tie-break explains BOTH reported symptoms.
  **§15.2 records a near-miss on purpose:** the naive set-diff predicted a suite-wide cut breakage that
  the lexer's dispatch order refutes — checked before reporting, per the s152 false-gap rule.

## 9. SUGGESTED RUNGS (proposed, not adopted — Lon's call)

- [ ] **PL-SWI-SYN-1** — decide the `double_quotes` target (§0): GNU/ISO `codes` (cheap, closes the
      shipped defect) vs SWI `string` (needs a string type first). **Blocks PL-SYNTAX-2, which is
      currently written as a binary choice that does not exist.**
- [ ] **PL-SWI-SYN-2** — read the SCRIP side of §2/§4/§5/§6 and fill the absent columns. Cheap, and
      it converts this file from a reference into a diff.
- [ ] **PL-SWI-SYN-3** — `unknown=error`: give the banked silent-fail defect an owning rung (§7).
      Both references and ISO agree; it is the highest-severity item in the banked list.
- [x] **PL-SWI-SYN-4** — ✅ **CLOSED s156.** `\e` SCRIP=27 matches SWI while GNU 1.4.5 rejects it;
      `\s`/`\u`/`\U`/`\c` diverge from both. See §2.1.1 and
      `FINDING-2026-07-27b-CLAUDE-PL-ESCAPE-THREE-CALL-SITES-TWO-BEHAVIOURS-AND-SWI-SYN-4-CLOSED.md`.
      ⛔ Its real output is a **warning about PL-SYNTAX-2/3**: SCRIP is not uniformly GNU-flavoured, so
      the dialect ruling must be **per-axis** — "align to GNU" would regress `\e`.
- [ ] **PL-SWI-SYN-5** (new s156) — probe `X is 0'\q`. The `0'` escape call site (`prolog_lex.c:157`)
      is READ-only and behaves **differently from the other two** (yields 92, discards the char).
      It changes the shape of any escape fix.
- [ ] **PL-SWI-SYN-6** (new s156) — diff SCRIP's lexer character classifier against §12's
      `_PL_char_types` table. Cheap, and it is the actual spec the reopened PL-SYNTAX-6 needs.

---

# ADDED s156 — SECTIONS 10-14: THE AXES §8 DID NOT COVER

**Read from `refs/swipl-devel-master/` = SWI-Prolog `10.1.5`, this session.** Same provenance
discipline as §1-§7: every row below is a source read, each with the file:line it came from. The
SCRIP column is **absent by default** and is marked ABSENT where it was not probed — per the s152
rule, a false gap is worse than a missing one.

## ⭐⭐ 10. ARITHMETIC — THE EVALUABLE FUNCTOR SET, COMPLETE (79 rows)

**Source:** `src/pl-arith.c` `ar_funcdefs[]` :4848-4937, joined against `src/ATOMS`.

**ADMISSION SITE PROVEN SINGLE.** Raw `ADD(` count in the table range == 79 == resolved rows, and
`registerFunction()` (:4942) is called from exactly one place — a loop over `ar_funcdefs` (:4978-4982).
There is no second table, no `PL_register_arith` foreign hook, no library-registered arithmetic.
**This is the whole evaluable-functor set for `is/2`, `=:=/2` and friends.** (s152's rule applied: the
site list was checked before the count was trusted.)

`*` = SWI's own `F_ISO` flag · `†` = `#ifdef O_BIGNUM` (absent in a non-GMP build)

**arity 0** (7: 1 ISO, 6 SWI-only)
  `cputime`, `e`, `epsilon`, `inf`, `nan`, `pi`*, `random_float`

**arity 1** (42: 23 ISO, 19 SWI-only)
  `+`*, `-`*, `\`*, `abs`*, `acos`*, `acosh`, `asin`*, `asinh`, `atan`*, `atanh`, `ceil`*,
  `ceiling`*, `cos`*, `cosh`, `denominator`†, `erf`, `erfc`, `eval`, `exp`*, `float`*,
  `float_fractional_part`*, `float_integer_part`*, `floor`*, `integer`*, `lgamma`, `log`*, `log10`,
  `lsb`, `msb`, `numerator`†, `popcount`, `random`, `rational`†, `rationalize`†, `round`*, `sign`*,
  `sin`*, `sinh`, `sqrt`*, `tan`*, `tanh`, `truncate`*

**arity 2** (29: 17 ISO, 12 SWI-only)
  `*`*, `**`*, `+`*, `-`*, `/`*, `//`, `/\`*, `<<`*, `>>`*, `\/`*, `^`*, `atan`, `atan2`*, `cmpr`,
  `copysign`, `div`*, `gcd`, `getbit`, `lcm`, `max`*, `maxr`, `min`*, `minr`, `mod`*, `nexttoward`,
  `rdiv`†, `rem`*, `roundtoward`, `xor`*

**arity 3** (1: 0 ISO, 1 SWI-only)
  `powm`

### 10.1 Three traps in this table

1. **`atan` is BOTH arity 1 and arity 2, and `atan2/2` is a separate ISO-flagged alias** — `atan/2`
   (non-ISO) and `atan2/2` (ISO) both dispatch to the SAME C function `ar_atan2`. A name-keyed
   admission table that assumes one arity per name silently loses one of them.
2. **⚠ `F_ISO` IS SWI'S OWN ANNOTATION, NOT A VERIFIED ISO CONFORMANCE CLAIM.** `//`/2 (integer
   division) carries NO `F_ISO` flag here although ISO 13211-1 defines it as evaluable. **Do not use
   this column as the ISO axis** — `PROLOG-ISO-TRACKER.md` is that axis. Use it only as "what SWI
   believes about itself."
3. **The comparison operators are NOT in this table.** `< > =< >= =:= =\=` are `PRED_IMPL(..., PL_FA_ISO)`
   predicates at `pl-arith.c:672-702`, not evaluable functors. **This is structurally the same split
   s152 found on the GNU axis** (where the comparisons were admitted only in `lower_prolog.c`'s name
   arrays and both audits wrongly reported them as gaps). An arithmetic audit that reads only the
   functor table will report all six as missing on the SWI axis too — they are not.

**SCRIP column: ABSENT.** Not probed this session.

## ⭐⭐ 11. STANDARD ORDER OF TERMS — AND A **SECOND-ORACLE CONFIRMATION** OF THE BANKED s152 DEFECT

**Source:** `src/pl-prims.c` `compareStandard()` :1950, `compare_primitives()` :1804,
`compare_mixed_float_rational()` :1759; tags `src/pl-data.h` :155-163.

### 11.1 The order

    Var @< AttVar @< Number @< String @< Atom @< Compound

Implemented as raw tag order: `TAG_VAR(0) < TAG_ATTVAR(1) < TAG_FLOAT(2) < TAG_INTEGER(3) <
TAG_STRING(4) < TAG_ATOM(5) < TAG_COMPOUND(6)`. Within class: atoms and strings alphabetically,
numbers by value, compounds by **arity, then name, then recursively left-to-right**.

⚠ **`String` is a distinct class BETWEEN Number and Atom.** This is SWI-only; ISO/GNU have no string
type. It is a direct consequence of the `double_quotes=string` default and therefore **couples to the
§0 `double_quotes` decision**: adopting SWI strings means adopting a new standard-order class, not
just a new literal type.

### 11.2 ⛔ THE MIXED INT/FLOAT RULE — FLAG-DEPENDENT, AND IT SETTLES THE BANKED DEFECT

`compare_primitives()` :1824-1830 takes a special path when one side is float and the other integer,
**but only when the `iso` flag is FALSE**:

- **`iso=false` (THE DEFAULT — `os/pl-prologflag.c:1996` `setPrologFlag("iso", FT_BOOL, false, ...)`)**:
  mixed int/float compares **BY VALUE** via `compare_mixed_float_rational()`. At equal value it
  tie-breaks: `rc = (tag(w1) == TAG_FLOAT) ? CMP_LESS : CMP_GREATER` — **Float sorts BEFORE Int.**
  NaN is special-cased FIRST and sorts less than everything.
- **`iso=true`**: no value comparison at all — pure tag order, so `TAG_FLOAT(2) < TAG_INTEGER(3)`
  means **every float precedes every integer regardless of value** (`2.0 @< 1` succeeds).

**`==/2` is unaffected by the flag.** With `eq=true` the tag mismatch returns `CMP_NOTEQ` at :1821
*before* the float/rational path is reached — so `1 == 1.0` is **false** in SWI under both settings.

**⭐⭐ CONSEQUENCE FOR THE BANKED DEFECT.** s152 banked *"`rt_pl_term_compare` conflates int and
float"* on a single oracle (gprolog 1.4.5: `1 == 1.0` false, `1.0 @< 1` true). **SWI 10.1.5 agrees
with gprolog on BOTH cases, by source, under its default flags** — `1 == 1.0` false (eq short-circuit),
`1.0 @< 1` true (equal value → Float tie-breaks LESS). SCRIP reportedly returns true / false
respectively, i.e. **wrong on both against BOTH references.** The banked entry was a one-oracle
observation; it is now a **two-oracle agreement**, which per this repo's own methodology is the
strong form. It also means the fix is unambiguous — there is no dialect choice to make here, both
references and ISO want the same thing.

**SCRIP column: NOT re-probed this session** — the above restates s152's probe and adds the SWI
source ruling. Re-probe before closing any rung on it.

## 12. TOKENIZER — THE CHARACTER ALPHABET

**Source:** `src/os/pl-ctype.c` `_PL_char_types[]` :1007+; classifier macros `src/pl-read.c` :77-91.

Every byte ≤ 0xFF gets exactly one class; above 0xFF SWI falls through to Unicode properties
(`uflagsW`, `U_SYMBOL`/`U_ID_START`/`U_ID_CONTINUE`/`U_SEPARATOR`/`U_DECIMAL`/`U_OTHER`).

| Class | Members (ASCII) | Role |
|---|---|---|
| `SY` symbol (17) | ``#  $  &  *  +  -  .  /  :  <  =  >  ?  @  \  ^  ~`` | **glue together** into one unquoted symbol atom |
| `SO` solo (3) | `!`  `%`  `;` | stand alone; never glue. `%` starts a line comment |
| `PU` punct (8) | `(`  `)`  `,`  `[`  `]`  `{`  `\|`  `}` | structural, single-char |
| `UC` (27) | `A`-`Z` **and `_`** | variable start |
| `LC` (26) | `a`-`z` | atom start |
| `DI` | `0`-`9` | digits |
| `SP` | space, `\t`(9), `\n`(10), `\v`(11), `\f`(12), `\r`(13) | layout |
| `CT` | 0-8, 14-31, 127 | control (not layout) |
| `DQ` / `SQ` / `BQ` | `"` / `'` / `` ` `` | the three quote classes |

**Why the SY set is the load-bearing row:** it is exactly why `=..` , `:-` , `-->` , `*->` and `@=<`
lex as SINGLE tokens without being listed anywhere as operators — the tokenizer maximal-munches a run
of SY chars, and only THEN is the resulting atom looked up in the operator table. A tokenizer that
instead pattern-matches known operator spellings will accept the same programs but produce different
errors on unknown symbol runs, and will mis-lex user-defined symbol operators.

**Note `_` is classified `UC`, not its own class** — `PlIdStartW` then special-cases it
(`isLower(c)||isUpper(c)||c=='_'`), and `f_is_prolog_var_start` is `PlUpperW(c) || c=='_'`. So
"variable" = uppercase-or-underscore start, falling straight out of this table.

**SCRIP column: ABSENT.** s155 probed escapes (§2.1) but not the class table. ⚠ **This is the table
`prolog_lex.c` should be diffed against** — s155 found its default arm passes unknown chars through
silently (PL-SYNTAX-6 reopened); the class table is the specification that arm is missing.

## 13. CONTROL CONSTRUCTS — WHAT IS COMPILED INLINE, AND THE TRANSPARENCY CONDITION

**Source:** `src/pl-comp.c` `compileBody()` :2287-2410; atom text from `src/ATOMS`.

| Construct | Functor | Compiled inline at |
|---|---|---|
| conjunction | `,`/2 | :2287 |
| disjunction | `;`/2 | :2295 |
| if-then-else | `;`/2 with `->`/2 left arg | :2312 (`hard=true`) |
| soft-cut-else | `;`/2 with `*->`/2 left arg | :2313 (`hard=false`) |
| if-then | `->`/2 | :2375 |
| soft-cut | `*->`/2 | :2376 |
| negation | `\+`/1 | :2400 |
| cut | `!`/0 | :3056 |
| call/N | `call`/1..8 | :3122, `I_CALLN` :6130 |

**⭐ THE TRANSPARENCY CONDITION IS THE INTERESTING PART.** The inline compilation is gated on
`control && !ci->islocal` (:966 for `;`, :1070 for `\+`). When that guard is false — inside `call/1`,
a meta-called goal, or a local/lambda context — the SAME term is **not** compiled inline; it becomes a
real predicate call. **That single flag IS the cut barrier**: `!` inside an inlined `;` cuts the parent
clause, while `!` inside `call((a;!))` cuts only the `call/1` goal, because the latter was never
inlined. SWI does not implement the barrier as a separate runtime mechanism — it falls out of whether
the construct got inlined.

**Relevance to `GOAL-PROLOG-BB.md`'s port-wiring table:** SCRIP's per-construct α/β/γ/ω wiring covers
`IR_GCONJ` / `IR_CHOICE` / `IR_ITE` / `IR_CUT` — i.e. `,` `;` `->` `!`. **`*->`/2 (soft cut) is a
DISTINCT row here with its own `hard=false` compile arm, and `\+/1` is a third.** s155's cursor already
banked a *"softcut gap"* and a *"nested-`\+` binding leak"*; this table is the source-side confirmation
that they are two separate constructs, not variants of `IR_ITE`, and that the `hard` boolean is exactly
the α/ω difference between them.

**SCRIP column: ABSENT.** Not probed this session.

## 14. DCG TRANSLATION

**Source:** `src/boot/dcg.pl` `dcg_translate_rule/4` :58-100, `dcg_body/7` :102+.

Five rule shapes, not one:

| Shape | Line | Meaning |
|---|---|---|
| `H --> B` | :70 | plain DCG rule |
| `H, PB --> B` | :61 | **pushback** / right-hand context |
| `H ==> B` | :94 | **SSU DCG** (single-sided unification) |
| `H, Grd ==> B` | :86 | SSU DCG with a guard |
| `H, PB ==> B` | :77 | SSU DCG with pushback (`is_list(PB)` guard) |

Body translation (`dcg_body/7`) terminal cases: `[]` → `S=SR` (:114), a list → terminal match (:117),
`!` → `(!, SR=S)` (:132) — note the cut **also threads the difference list**, and a variable body →
`phrase(QVar,S,SR)` (:106), i.e. deferred to runtime. Module qualification `M:X` is peeled at :110
and re-applied via the `Qualify` argument, so DCG bodies are module-transparent.

⚠ **`==>` is SWI-only** (SSU), as is the `,Grd` guard form. `-->` with pushback is ISO-adjacent but
rarely implemented. A DCG implementation that handles only `H --> B` covers ONE of five shapes.

**SCRIP column: ABSENT.** Not probed this session.

## ⭐⭐ 15. THE SCRIP COLUMN — READ s156 (this is the `PL-SWI-SYN-2` rung, partially discharged)

**Method: SOURCE READ of SCRIP, not a probe.** Nothing here was executed. Per the s152 rule
(*static extraction found 15 ISO gaps, running the compiler proved 7 false*), **every row below is a
HYPOTHESIS until probed**, with one exception noted inline. Rows are given with file:line so a probe
can be aimed precisely.

### 15.1 ⛔ STANDARD ORDER (§11) — THE DEFECT IS ONE FUNCTION, AND THE FIX IS ONE TIE-BREAK

**Site:** `src/runtime/unification.c` `rt_pl_term_class()` :617-626 and `rt_pl_term_compare()` :628-647.

**Mechanism, exactly:**

    rt_pl_term_class: TERM_VAR→0 · TERM_FLOAT→1 · TERM_INT→1 · TERM_ATOM→2 · TERM_COMPOUND→3

`TERM_FLOAT` and `TERM_INT` are **the same class (1)**, so the `if (ca != cb)` guard at :632 never
fires between a float and an int. Control falls into the `switch`, where both the `TERM_INT` (:635)
and `TERM_FLOAT` (:636) arms widen to `double` and return `x<y ? -1 : (x>y ? 1 : 0)` — **a pure value
comparison with no type tie-break.** At equal value both arms return `0` = EQUAL.

**Blast radius is the whole standard-order family, through ONE function.** `rt_pl_atop_cell()`
:650-662 maps `op 0..5` → `@<` `@=<` `@>` `@>=` `==` `\==` and every one of them is
`rt_pl_term_compare`'s return re-thresholded; `rt_pl_compare_cell()` :664 is `compare/3`; and
`sort/msort/keysort/setof/predsort` call it directly (:742, :747, :796-797, :802, :821).

**⭐ THE FIX IS A SINGLE TIE-BREAK, AND IT CORRECTS BOTH REPORTED SYMPTOMS AT ONCE.** Per §11.2 all
three references (ISO, GNU 1.4.5 probed s152, SWI 10.1.5 by source this session) agree: **at equal
value, Float precedes Int.** Adding that tie-break to the two numeric arms makes
`1.0 @< 1` return `-1` (true, was false) **and** makes `1 == 1.0` return non-zero (false, was true) —
because `==` is just `c == 0` at :660. One edit, both symptoms, no dialect choice to make.

    case TERM_INT:   ... if (x<y) return -1; if (x>y) return 1;
                     return (b->tag == TERM_FLOAT) ?  1 : 0;   /* Float @< Int */
    case TERM_FLOAT: ... if (x<y) return -1; if (x>y) return 1;
                     return (b->tag == TERM_INT)   ? -1 : 0;   /* Float @< Int */

⚠ **NOT LANDED — no code was modified this session.** This is a located fix, not a rung. It needs the
full gate board (rung suite 164/164 × 3 modes, `no_new_global`, `no_value_stack`) and s152 explicitly
ruled it *"its own rung, NOT folded into"* another. Landing it also **changes sort order**, so every
`.expected` involving mixed-type sorts must be re-verified, not assumed.

⚠ **SECOND-ORDER NOTE:** SCRIP's class ladder has **no AttVar and no String class**, consistent with
having no attributed variables and `double_quotes=atom`. If §0's decision ever adopts SWI strings, a
String class must be inserted **between Number and Atom** (§11.1) — the ladder is not just a literal
type change.

### 15.2 LEXER SYMBOL-CHAR SET (§12) — 17 vs 17, TWO DIFFERENCES

**Site:** `src/parser/prolog/prolog_lex.c` `is_graphic()` :234-239, consumed by `scan_graphic()` :241-250.

| | set |
|---|---|
| SWI `SY` (17) | ``#  $  &  *  +  -  .  /  :  <  =  >  ?  @  \  ^  ~`` |
| SCRIP `is_graphic` (17) | ``#  &  *  +  -  .  /  :  <  =  >  ?  @  \  ^  ~  !`` |

Set difference is exactly two: **SWI-only `$`** · **SCRIP-only `!`**.

- **`!` — VERIFIED NOT the catastrophic case, scope is narrow.** SWI classifies `!` as `SO` (solo), so
  it can never join a symbol run. SCRIP lists it in `is_graphic`, which *would* mean `!.` lexes as one
  token and every clause-final cut breaks — **so I checked before reporting it, and it does not.**
  `lexer_next()`'s `switch (c)` intercepts `case '!': return TK_CUT` **before** the default arm reaches
  `scan_graphic()`. So `!` never STARTS a run. It can still **CONTINUE** one, because `scan_graphic`'s
  while-loop calls `is_graphic` on every subsequent char: **`=!` lexes as the single atom `=!` in SCRIP
  and as `=` then `!` in SWI.** Latent and low-traffic, but real. (Recording the near-miss deliberately:
  the naive set-diff reading predicted a suite-wide breakage that the dispatch order refutes — this is
  the s152 false-gap trap caught in the act.)
- **`$` — absent from SCRIP's set.** Note SCRIP uses `$`-prefixed names internally (`$compare`,
  `$VAR`); those are minted by `prolog_atom_intern()` in C and never lexed from source, so this is
  **not** obviously a live defect. **UNPROBED — do not quote it as a gap** until a probe shows what
  SCRIP does with a source-level `$` token.

⚠ `scan_graphic` additionally breaks the run on `,` and `|` (:244) — both are `PU` in SWI, so this
agrees with SWI by a different route (SWI never had them in `SY` to begin with).

### 15.3 ⭐ ESCAPES (§2.1) — A REFINEMENT OF s155'S FINDING, AND A THIRD BEHAVIOUR IT MISSED

s155 recorded *"reader lexer (unknown escape silently passes char through), `prolog_lex.c:98` default
arm passes char through, never raises."* **Read this session, that is close but not exact, in a way
that changes what a fix and a test must expect.**

`decode_escape()` :70-99 returns a **three-valued** signal, and the `default` arm at :98 returns
**`-1`**, not a success code: `default: *code = (unsigned char)e; return -1;`. So the unknown-escape
condition **is** signalled and the callers **do** act on it — it is not ignored. What they do with it
is the defect, and **the three call sites do not agree**:

| Call site | :line | On unknown escape `\q` | Result |
|---|---|---|---|
| quoted atom | :116-119 | `buf_push('\\')` **then** `buf_push(code)` | **two chars** `\q` |
| string | :138-141 | `buf_push('\\')` **then** `buf_push(code)` | **two chars** `\q` |
| char-code `0'\q` | :157 | `t.ival = (st==1) ? code : '\\'` | **one char**, `92` — **the `q` is discarded** |

So: not "passes the char through" but **"preserves the escape as literal text"** in two sites, and
**"yields backslash, dropping the escaped char"** in the third. Both references raise a syntax error
instead. **Consequence for the rung:** a test asserting `'\q' == q` fails against SCRIP's *current*
behaviour for the wrong reason (it yields `\q`, not `q`), and the `0'\q` site needs its own assertion
because it diverges from its two siblings. `st == 0` (line continuation, `case '\n'`) is handled
correctly by omission at all three sites.

### 15.4 STILL ABSENT — SCRIP columns NOT read this session

**§10 arithmetic functor set · §13 control constructs · §14 DCG.** Not read, not probed, **no gap is
claimed for any of them.** For §10 the admission sites to read are `lower_prolog.c`'s
`g_pl_nl_arith[]`/`g_pl_nl_builtins[]` plus the det `extra[]` table — and s152's warning applies with
full force: that audit already reported six arithmetic comparisons as gaps **which SCRIP implements
correctly**, because they are admitted only in a name array and never as a strcmp arm.
