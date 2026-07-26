# FINDING 2026-07-26 — THREE-AXIS DIALECT AUDIT (ISO/GNU/SWI) AND FIVE DEFECTS IN THE COVERAGE INSTRUMENT

**Session:** s152 · **Goal:** GOAL-PROLOG-BB.md LADDER A (PL-100) · **Rung:** PL-ISO-10 (audit), new tool
**Ask (Lon):** "provide all GNU, SWI, and industry standard Prolog syntax and semantics"
**Landed:** `SCRIP/scripts/audit_prolog_dialect_coverage.sh` + `.github/PROLOG-DIALECT-TRACKER.md`
**No compiler change. No IR/lower/template/codegen touched.** RT `-O0`, no `-O2` directive.

---

## 0. HEADLINE

The existing `PROLOG-ISO-TRACKER.md` measures ONE axis (gprolog `set_bip_name/2`) and answers one
question: *how much of gprolog do we have?* The ask names THREE targets. Building the other two axes
surfaced **five defects in how coverage is measured** — four of which inflate the reported gap, one of
which truncates the denominator. Every one was caught by cross-checking a second signal or by RUNNING
the compiler, never by reading code.

**Corrected ISO 13211-1 axis: 107 predicates, 9 open (91% done).** The first cut of the same axis said
**36 open**. Three quarters of that gap was instrument error.

| axis | source of truth | total | SCRIP admits | open |
|------|-----------------|-------|--------------|------|
| **ISO 13211-1** | `PL_FA_ISO` ∪ gprolog doc prose | 107 | 98 | **9** |
| GNU | `set_bip_name/2` **+ `*_inl.pl` inline family** | 386 | 171 | 215 |
| SWI | `PRED_IMPL`/`PRED_DEF` + `boot/*.pl` | 1476 | 125 | 1351 |
| ISO 13211-5 (threads DTR) | `PL_FA_ISO` in `pl-thread.c`/`pl-mutex.c` | 19 | 0 | 19 |

---

## 1. ⭐⭐ DEFECT 1 — THE FOUR ADMISSION SITES ARE FIVE. THE AUDIT REPORTS PREDICATES WE SHIP AS GAPS.

`audit_prolog_iso_coverage.sh` reads SCRIP's admitted set from four sites (det table, GEN rail,
`goal()` strcmp arms, `pb_expand_goal` arms). There is a **FIFTH**: static **name-array tables** in
`lower_prolog.c` — `g_pl_nl_builtins[]` (:52), the det `extra[]` list (:1139), the relop→suffix maps
(:251, :1184).

**The arithmetic comparisons `< > =< >= =:= =\=` are admitted ONLY there.** They are never strcmp
arms, never `pl_ensure_gen_builtin_pred` calls, never det-table rows. The four-site audit therefore
reported all six as ISO gaps — **while SCRIP runs them correctly**, verified live:

```
:- initialization(main, main).
main :- ( 1+1 =:= 2 -> write('OKM') ; write(no) ), nl.     ->  OKM
```

⚠ **THIS AFFECTS THE COMMITTED TRACKER, NOT JUST THE NEW ONE.** `PROLOG-ISO-TRACKER.md`'s
`core-open 99` uses the same four sites and is **overstated by the same class**. Its DONE=139 is a
floor, not a count. The new script reads all five; re-running the old one after porting the fifth
site is a follow-on (deliberately NOT done here — that tracker belongs to PL-ISO-10 and changing its
numbers mid-session without its own gate would be the stale-doc failure class in reverse).

⭐ **RULE EARNED (sibling of s150's "a reachability measurement is only as broad as its corpus"):**
**AN ADMISSION AUDIT IS ONLY AS COMPLETE AS ITS SITE LIST, AND A SITE LIST IS A GUESS UNTIL A
BEHAVIOURAL PROBE CONTRADICTS IT.** Static extraction found 15 gaps; running the compiler proved 7 of
them false. The asymmetry is the reason to care: a false gap wastes a rung implementing what already
exists, and it does so *silently*, because the implementation "succeeds" immediately.

## 2. ⭐⭐ DEFECT 2 — THE GNU DENOMINATOR OMITS THE LANGUAGE'S MOST-USED PREDICATES.

gprolog's **inlined** builtins are compiled straight to WAM instructions by Pl2Wam and **never call
`set_bip_name`**. Measured: `set_bip_name` occurrences for `is/2`, `var/1`, `atom/1`, `functor/3`,
`arg/3`, `=../2`, `call/1` — **zero, all of them**. `BipsPl/type_inl.pl` declares `var/1 nonvar/1
atom/1 integer/1 float/1 number/1 atomic/1 compound/1 callable/1 ground/1 is_list/1` as plain clause
heads with no bip-name goal; `inl_protos.h` carries 56 such prototypes.

So `PROLOG-ISO-TRACKER.md`'s **"312 gprolog public exports" excludes type tests, term
construction/inspection, arithmetic and arithmetic comparison** — the core of Prolog. Reading the
`*_inl.pl` heads back in takes the GNU axis 312 → **386 (+74)**.

**Direction of the error matters:** SCRIP already admits most of the inline family, so this
**truncates the denominator, it does not overstate the numerator**. The "44% done" figure is computed
against a universe missing the predicates every program uses.

## 3. ⚠ DEFECT 3 — `PL_FA_ISO` IS NOT 13211-1. SWI TAGS ITS THREADING PREDICATES ISO TOO.

`PRED_IMPL("thread_send_message", 2, thread_send_message, PL_FA_ISO)` (`pl-thread.c:5334`) is SWI's
own source, not a regex artifact — those predicates conform to the **ISO 13211-5 threads DTR**, a
different part of the standard. Folding them into the core axis inflated it by 19 and reported
mutexes/message queues as ISO-core gaps. Partitioned by defining file (`pl-thread.c`, `pl-mutex.c`)
into a separate axis. ⚠ The first partition keyed on `pl-thread.c` alone and **missed `pl-mutex.c`** —
the mutex rows survived one full regeneration before a second read caught them.

## 4. ⚠ DEFECT 4 — DOC-PROSE ISO ATTRIBUTION WAS GROUP-WIDE.

gprolog's `pl-bips.tex` marks conformance in prose ("ISO predicate."), and a `\subsubsection`
routinely documents an ISO predicate **alongside gprolog extensions**. Attributing the claim to every
`\IdxPBD{}` in the block marked `call_det/2`, `call_nth/2`, `countall/2` — all gprolog extensions — as
ISO. Now scoped to the **sentence**, with explicit mentions preferred and the weaker group-inferred
share counted separately so the inference is visible instead of assumed.

## 5. ⚠ DEFECT 5 — OPERATOR-FORM AND ARITY-0 HEADS ARE INVISIBLE TO A `name(` REGEX.

`arith_inl.pl` declares comparisons in **infix operator form** (`X =:= Y :-`, `X < Y :-`), and
arity-0 builtins have no parens at all (`repeat.`). A canonical-form head regex silently misses both.
This is the same silent-drop class as s143's `cmp reg,[mem]` encoder landmine: **the extraction did
not fail, it returned a smaller set.**

---

## 6. THE HONEST REMAINING GAP — 9 ISO-CORE PREDICATES, BEHAVIOURALLY CONFIRMED

Each was run against a live `--run` build, not inferred:

| predicate | status | note |
|-----------|--------|------|
| `compare/3` | **MISSING** | goal produced NO output — matches the banked *compiled-path silent-fail on undefined predicates* defect |
| `repeat/0` | **MISSING** | same silent-fail signature |
| `unify_with_occurs_check/2` | MISSING | fails cleanly |
| `atomic_concat/3` | MISSING | SWI-side name; gprolog spells it differently |
| `char_conversion/2` | MISSING | reader-level, pairs with the syntax axis below |
| `read_line_to_codes/2` | MISSING | GNU-side |
| `read_line_to_chars/2` | MISSING | GNU-side |
| `set_stream_position/2` | MISSING | stream axis, `stream.pl` (29 open) |
| `current_char_conversion/2` | **DISPUTED** | static says open, probe says admits — **probe was too lenient** (`;true` inside `catch` passes on mere failure). Needs a stricter probe; do NOT count it either way yet. |

⚠ `compare/3` and `repeat/0` returning **empty output rather than an error** is independent
corroboration of the banked silent-fail defect, on two fresh predicates.

---

## 7. ⛔ NOT MEASURED — THE SYNTAX/SEMANTICS HALF OF THE ASK IS STILL OPEN

The ask says "syntax **and** semantics". Everything above is **predicates only**. These surfaces are
not predicate rows and are structurally invisible to both trackers — the same blindness s151 named:

- **Operator table** (`op/3` defaults: priority × type × name)
- **Reader syntax**: `0'c` char codes, `0x/0o/0b`, escape sequences, block comments, `{}/1` curly
  terms, back-quoted strings, `double_quotes` flag behaviour
- **`format/2,3` directive set** — `~p ~q ~e ~f ~g ~r ~c ~s ~t~| ~+` column stops (already named open
  in PL-ISO-9 prose)
- **`write_term/2` options** — `quoted(true)`, `ignore_ops`, `max_depth`, `variable_names`
- **Prolog flags** (`flag.pl` 4 open) and **ISO error-term shapes**

**Attempted and deliberately stopped.** The three operator tables use three different encodings —
SCRIP `FIX_*`/`ASSOC_*` enums in `src/parser/prolog/` (:140,:151), SWI `pl-op.c`, gprolog a C table —
and the first extraction pass returned `gprolog=0 swi=1 SCRIP=0`, i.e. **nothing**. Shipping a number
from that would have been the sixth wrong measurement of one session. Locations are recorded here so
the next session starts from the shapes, not from a guess.

⭐ **This is the rung to open next: `PL-SYNTAX-1` — operator table three-way diff.** It is the
prerequisite for any honest claim about "syntax", and it is cheap once the three encodings are read
directly instead of pattern-matched.

---

## 8. GATES

No compiler change, so no rung suite was required or run. Tooling verified:
`audit_prolog_iso_coverage.sh` re-run live → **byte-identical to the committed
`PROLOG-ISO-TRACKER.md`** (proves the GNU axis was already current, and that this session's numbers
differ because the INSTRUMENT changed, not the tree). `scrip` built clean (`make -j4 scrip`, rc=0).
All 15 behavioural probes run in mode-3 `--run`.

⚠ **The first probe harness reported all 15 MISSING with an identical
`mode-3 driver: main BB graph not found`** — bare `:- Goal.` directives, not SCRIP's
`:- initialization(main, main).` + `main :-` shape. **A uniform result across a diverse set is a
harness tell, not a finding**; re-running with the corrected shape flipped 7 of the 15.

## 9. NEXT

1. **`PL-SYNTAX-1`** — operator table three-way diff (§7), then format directives / `write_term`
   options / flags / error terms.
2. **Port the fifth admission site into `audit_prolog_iso_coverage.sh`** and re-baseline
   `core-open 99` under PL-ISO-10's own gate.
3. **The 9 ISO-core predicates** (§6) — `compare/3` and `repeat/0` first; both are small and both
   currently exhibit the silent-fail signature, so they double as probes of that banked defect.
4. Tighten the `current_char_conversion/2` probe before counting it.

**WATERMARK (files touched — push state NOT recorded here per the stale-orientation FACT RULE;
`scripts/handoff_status.sh` is the only ground truth):** SCRIP
`scripts/audit_prolog_dialect_coverage.sh` (new) / corpus `<none>` / .github
`PROLOG-DIALECT-TRACKER.md` (new) + this FINDING.
**BANKED (carried, none resolved):** NO-LCO deep-recursion segfault + cumulative exhaustion;
nested-`\+` binding leak; `retractall/1` gaps; compiled-path silent-fail on undefined predicates
(**corroborated twice this session**).

---

## 10. ADDENDUM — `compare/3` LANDED, AND IT SURFACED A WIDER PRE-EXISTING DEFECT

`compare/3` is in (`rt_pl_compare_cell`, `src/runtime/unification.c`, placed beside `rt_pl_atop_cell`
so it reuses the same `pl_cell_copy_walk` + `rt_pl_term_compare` path; `$compare` dispatch arm +
det-target classifier entry + det-table row in `by_name_dispatch.c`). Verified against **gprolog 1.4.5,
installed this session** — 5 of 6 cases byte-identical:

| case | gprolog | SCRIP |
|------|---------|-------|
| `compare(A,1,2)` | `<` | `<` ✓ |
| `compare(B,2,1)` | `>` | `>` ✓ |
| `compare(C,foo,foo)` | `=` | `=` ✓ |
| `compare(D,f(1,2),f(1,3))` | `<` | `<` ✓ |
| `compare(F,abc,f(x))` | `<` | `<` ✓ |
| **`compare(E,1,1.0)`** | **`>`** | **`=`** ✗ |

### ⚠⚠ BANKED DEFECT (NEW) — `rt_pl_term_compare` CONFLATES INT AND FLOAT

The single divergence is **not** in `compare/3`. Probed directly:

```
1 == 1.0    ->  SCRIP: true    gprolog: false     ISO: false (==/2 is STRUCTURAL identity)
1.0 @< 1    ->  SCRIP: false   gprolog: true      ISO: Float < Int at equal value
```

**PROVABLY PRE-EXISTING BY CONSTRUCTION:** this rung's diff *adds* a function and never modifies
`rt_pl_term_compare`. That primitive is already the engine for `==/2`, `\==/2`, `@</2`, `@=</2`,
`@>/2`, `@>=/2`, `sort/2`, `msort/2`, `keysort/2`, `predsort/3` — all shipped. `compare/3` merely made
it *visible*, because it is the first predicate to report the ordering as a value rather than as a
yes/no.

`1 == 1.0` succeeding is the more serious half: `==/2` is structural identity and must be false for
an int and a float in every conforming Prolog. **Blast radius is wide, so this gets its own rung and
is NOT folded in here** — changing standard order under `sort/2` and `keysort/2` demands the full
suite plus corpus regeneration, which this session had no budget to gate honestly.

### GATES (this addendum)

Rung suite **164/164 × 3 modes**; **mode-3 ≡ mode-4 byte-identical** on the `compare/3` smoke
(including the `compare(<,1,2)` gate form and a negative case); `no_new_global` **PASS, ratchet
14 / floor 14 UNMOVED**; `no_value_stack` PASS. `make scrip` and `make libscrip_rt` both rc=0.
RT `-O0`, no `-O2` directive. No IR / lower / template / codegen touched.

ISO 13211-1 axis moves **9 open → 8 open**.
