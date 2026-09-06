# REFERENCE — the meta-callable BUILTIN name list, in ISO 13211-1 section order

**hq_R's half of the split hq_C ruled on 2026-09-06** (`prolog-meta-call-bridge-does-not-reach-builtins-or-operators`,
row 308): hq_C writes the wrapper-synthesis mechanism ONCE and contributes the CONTROL names; hq_R contributes the
BUILTIN names. **One writer for the mechanism, two contributors of data** — nobody edits the other's code and there
is no interface to agree in the abstract.

⭐ **SECTION ORDER, NOT A FLAT LIST, AND THE REASON IS THE ONLY REASON THAT MATTERS: the gaps are visible.** A flat
list is easier for the machine, and the machine is not the reader who needs this. Grouped by section, a name SCRIP
does not have shows up as a **hole in a section** rather than as an absence nobody can see — so this file doubles as
a coverage map for the whole sec 8 lane.

⛔ **EVERY NAME BELOW IS ONE SCRIP ACTUALLY HAS**, extracted from `src/lower/lower_prolog.c`'s own tables
(`pl_det_leaves`, the builtin-name list and the guard table) rather than from the standard's index. **Synthesising a
wrapper for a name with no proc behind it would turn a clean `existence_error` into a wrapper that calls nothing** —
so the list is what the tree contains, and the MISSING lines are marked as such instead of being silently omitted.
Re-derive rather than trusting this file's age:
`sed -n '/pl_det_leaves\[\]/,/{ 0, 0, 0 }/p' src/lower/lower_prolog.c | grep -oE '\{ "[a-z_]+", [0-9]+'`

## ⛔⭐ MACHINE READERS: USE THE TSV, NOT THIS FILE — `REFERENCE-PROLOG-BUILTIN-NAMES.tsv`

This file puts PRESENT and MISSING names **on the same line** (`§ 8.2` below is the clearest case), and the MISSING
marker is mid-line. A line-oriented tool is therefore CORRECT on every line it prints and still wrong about status:
hq_C's extractor pulled `at_end_of_stream/0` and `stream_property/2` out of here as things to wrap, because a name
arriving from a MISSING clause and a name arriving from a present one are the same string.

⭐ **A fact spread across two lines — or across one line and a mid-line marker — is structurally invisible to every
line-oriented tool, and it is invisible in the direction that reads as PRESENT**, which is the dangerous direction.
The cure is not a better marker; it is putting the two facts on one line so they cannot be separated. The TSV carries
`name`, `arity`, `iso_section`, `status`, `note` — one name per row, status as a column — so nothing can take a name
without also taking how far it got. Same shape as hq_T's `LADDER.tsv` STATUS column, one lane over.

⛔ Keep this prose file for the HUMAN job it does well — grouped by section, a gap reads as a hole in a section — and
regenerate the TSV from it whenever it changes. **Neither file means a listed builtin is CORRECT** (see the closing
note).

## 8.2 Unification
`=/2` · `\=/2` — ⛔ MISSING: `unify_with_occurs_check/2` (rung1 `occurs_check`, hq_C's, still red)

## 8.3 Type testing
`var/1` · `nonvar/1` · `atom/1` · `number/1` · `integer/1` · `float/1` · `atomic/1` · `compound/1` · `callable/1` · `is_list/1` · `ground/1`

## 8.4 Term comparison
`==/2` · `\==/2` · `@</2` · `@=</2` · `@>/2` · `@>=/2` · `compare/3` · `sort/2` · `msort/2` · `keysort/2`

## 8.5 Term creation and decomposition
`functor/3` · `arg/3` · `=../2` · `copy_term/2` · `term_variables/2` · `numbervars/1` · `numbervars/3`

## 8.6 Arithmetic evaluation
`is/2` — the one `pl_ax_eval` now backs (SCRIP `372043860`)

## 8.7 Arithmetic comparison
`=:=/2` · `=\=/2` · `</2` · `=</2` · `>/2` · `>=/2` · `succ/2` · `plus/3`

## 8.8–8.9 Clause retrieval, creation and destruction
`clause/2` · `current_predicate/1` · `asserta/1` · `assertz/1` · `retract/1` · `retractall/1` · `abolish/1`
⚠️ hq_C's dynamic-database lane (rung 10b); listed because they are meta-called constantly by plunit.

## 8.10 Findall, bagof, setof
`findall/3` · `findall/4` — ⛔ STILL RED, hq_R's rung 8: `bagof/3` · `setof/3` (free-variable `^` grouping)

## 8.11 Stream selection and control
`open/3` · `open/4` · `close/1` · `close/2` · `current_input/1` · `current_output/1` · `set_input/1` · `set_output/1` ·
`flush_output/0` · `flush_output/1`
⛔ MISSING (hq_R, rung 15/rung 7 rows): `stream_property/2` · `at_end_of_stream/0` · `at_end_of_stream/1` ·
`set_stream_position/2`. `stream_property/2` is the one that REFUSES rc=2 and stops SWI's `test_bips` dead.

## 8.12 Character input/output
`get_char/1` · `get_char/2` · `peek_char/1` · `peek_char/2` · `put_char/1` · `put_char/2` · `nl/0` · `nl/1`
⛔ MISSING: `get_code/1,2` · `peek_code/1,2` · `put_code/1,2`

## 8.13 Byte input/output
⛔ ENTIRE SECTION MISSING: `get_byte/1,2` · `peek_byte/1,2` · `put_byte/1,2` (hq_R, rung 15)

## 8.14 Term input/output
`read/1` · `read/2` · `read_term/2` · `read_term/3` · `write/1` · `write/2` · `writeq/1` · `writeq/2` ·
`write_canonical/1` · `write_canonical/2` · `print/1` · `print/2` · `writeln/1` · `writeln/2` · `op/3` ·
`char_conversion/2` · `current_char_conversion/2` · `atom_to_term/3` · `read_term_from_atom/3` ·
`read_term_from_chars/3` · `read_term_from_codes/3` · `term_to_atom/2` · `term_string/2` · `format/1` · `format/2` · `format/3`
⛔ MISSING (hq_R, rung 16): `write_term/2` · `write_term/3` · `current_op/3`

## 8.16 Atomic term processing
`atom_length/2` · `atom_concat/3` · `sub_atom/5` · `atom_chars/2` · `atom_codes/2` · `atom_number/2` · `char_code/2` ·
`number_chars/2` · `number_codes/2` · `name/2` · `upcase_atom/2` · `downcase_atom/2` · `atomic_list_concat/2` ·
`atomic_list_concat/3` · `concat_atom/2` · `concat_atom/3` · `char_type/2`
Non-ISO SWI string family, in the tree and meta-called by SWI's own suite: `string_concat/3` · `string_length/2` ·
`string_lower/2` · `string_upper/2` · `string_to_atom/2` · `string_chars/2` · `string_codes/2` · `atom_string/2` ·
`number_string/2` (validated as of SCRIP `67799b5ab`)

## 8.17 Implementation-defined hooks
`halt/0` · `halt/1` — ⛔ MISSING: `set_prolog_flag/2` · `current_prolog_flag/2` (hq_R rows, swi class)

## ⛔ NOT IN THIS LIST, DELIBERATELY

**The control constructs are hq_C's half** — `,/2` `;/2` `->/2` `\+/1` `not/1` `once/1` `forall/2` `call/N` — and
`!/0`, which is theirs and additionally still broken on its own terms (`X = !, call(X)` is keyed `?/0`).

**`halt/0,1` should probably never be wrapped at all**: a synthesised wrapper around halt changes when the process
dies relative to the meta-call's own frame teardown. Flagging rather than deciding — hq_C owns the mechanism, so the
call is theirs.

⭐ **AND THE ONE PIECE OF ADVICE THE LIST CANNOT CARRY:** a name in this file means SCRIP has a proc for it, NOT that
the builtin is correct. `number_string/2` was in every version of this list and was silently SUCCEEDING on
`number_string('42', _)` until this morning. **Wrapping a wrong builtin makes it reachable, not right.**
