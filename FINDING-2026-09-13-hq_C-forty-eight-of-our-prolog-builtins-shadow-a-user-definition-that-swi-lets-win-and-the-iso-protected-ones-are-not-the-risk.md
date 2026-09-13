# FINDING 2026-09-13 hq_C — 48 of our Prolog det-leaf builtins shadow a user definition that SWI lets win, and the ISO-protected ones are exactly the ones that are safe

**Seat:** hq_C (Prolog breadth, the nine Logtalk ISO families) · **Tree:** SCRIP `671d458c2` · **Oracle:** `/usr/bin/swipl`
**Found while:** closing `atomic_concat_3` (0/8 → 8/8) on row `prolog-logtalk-number-and-atom-conversion-family`.
**Status:** NOT A BLOCKER, NOT CURED, zero corpus exposure today. Filed as an ASK to the ceo. Nothing in this
finding argues against the landing that produced it.

## The witness

Adding `atomic_concat/3` to `pl_rung6_builtins` and `pl_det_leaves` makes every call to that name lower to the
builtin leaf. A program that defines its own `atomic_concat/3` therefore never reaches its own clause:

```prolog
atomic_concat(A,B,C) :- C = mine(A,B).
:- (catch(atomic_concat(x,y,R),E,(R=err(E))) -> write(R) ; write(failed)), nl.
```

    scrip m3   xy            <- our builtin ran; the user's clause was never consulted
    swipl      mine(x,y)     <- the user's definition won

## Why this is not the alarm it first looks like, and where the real edge is

The same probe against `atom_concat/3` — a builtin we have had all along — AGREES with the oracle:

    scrip m3   xy
    swipl      ERROR: No permission to modify static procedure `atom_concat/3'
               xy

⭐ **The distinction is ISO protection, and it is the whole finding.** For an ISO-protected predicate SWI
*refuses the redefinition* and then runs its own builtin, which is bit-for-bit what we do — so our flat
namespace and SWI's module system cannot be told apart. For a non-ISO predicate SWI resolves the call as
`user:Name` shadowing `system:Name` and the user wins, while we have no notion of a module and the builtin
wins. **We diverge on exactly the set of builtins the standard does not protect, and nowhere else.**

## The measured class

Census of the 134 name/arity pairs in `pl_det_leaves` (`src/lower/lower_prolog.c`) against SWI, asking
`predicate_property(H, iso)` per pair:

| bucket | count | meaning |
|---|---|---|
| ISO-protected in SWI | **78** | we agree with the oracle; redefinition is refused on both sides |
| redefinable in SWI | **48** | **the divergence class** — SWI lets a user clause win, we do not |
| absent from SWI | 8 | `wall_us/1`, `wall_ms/1`, `unget_{byte,char,code}/{1,2}` — ours, no oracle opinion |

⛔ **One row in my first run was my own instrument, not a fact, and it would have read as a real gap:** the
extractor pulled the C string `"\\=="` verbatim out of the source, so `\==/2` printed ABSENT. It is ISO in
SWI (checked separately). A regex reading C source gets C escapes, and an ABSENT bucket is where that lands
looking exactly like a missing builtin. The corrected totals are the ones in the table.

The 48: `is_list/1 numbervars/1 succ/2 plus/3 msort/2 char_type/2 term_string/2 term_to_atom/2 atom_number/2
atom_string/2 upcase_atom/2 downcase_atom/2 string_concat/3 string_length/2 string_lower/2 string_upper/2
string_to_atom/2 number_string/2 string_chars/2 string_codes/2 atomic_concat/3 atomic_list_concat/2
atomic_list_concat/3 concat_atom/2 concat_atom/3 name/2 telling/1 seeing/1 tell/1 append/1 see/1 told/0
seen/0 put/1 get0/1 get/1 skip/1 atom_to_term/3 read_term_from_atom/3 read_term_from_chars/3
read_term_from_codes/3 print/1 writeln/1 format/1 format/2 print/2 writeln/2 format/3`

⭐ **`append/1` is the one to look at twice.** `append/3` is the single most redefined predicate in real Prolog
code, and `append/1` sits in our builtin list one arity away from it.

## What I did NOT do, and why

I did not cure it. A fix is a namespace or a user-clauses-win policy in the shared dispatch path — that is a
change to how every Prolog call resolves, which is an ASK to the HQ and never a landing from this lane
(row GOAL: *a shared node is an ASK to the cto, never a landing*). I also did not treat it as a reason to
hold `atomic_concat/3` back: the group went 0/8 → 8/8, the exposure is zero (below), and 47 of the 48 names
were already in this class before I touched anything. **My change extended a pre-existing class by one; it
did not create it.**

## Exposure today: zero, and that is the uncomfortable part

No file under `corpus/` defines any of these in head position — `grep -rn '^atomic_concat('` over the corpus
is empty, and the only other mention is `packages/prolog/swi_tests/thread/thread_agc_queue.pl:71`, which
CALLS `atomic_concat/3` inside an `assertion/1` and therefore went from `existence_error` to working at this
landing. So no suite can see this, no board can go red on it, and no gate will ever catch it. ⛔ **A defect
with zero corpus exposure is not a small defect, it is an unmeasured one** — it will arrive as a package red
in somebody else's lane, wearing the name of whatever program happens to define `append/1` or `format/2`
first, and the seat who gets it will diagnose a formatting bug rather than a resolution-policy bug.

## The neighbour this rhymes with

SNOBOL4 has the same disease in a different language and it is already filed twice:
`FINDING-2026-09-05-hq_P-define-redefinition-is-deduped-at-compile-time-so-the-last-define-wins-retroactively.md`
and `FINDING-2026-09-05-seat03-define-redefinition-is-resolved-statically-per-name-arity-not-dynamically.md`.
Both are the same shape as this one: **a name resolved once at compile time, in a language whose users expect
it resolved at call time.** Three findings across two frontends is a pattern, not three coincidences, and it
is worth someone asking whether the shared lower/dispatch layer should have one answer to this rather than
three.

## Reproduce

```bash
cd SCRIP && printf 'atomic_concat(A,B,C) :- C = mine(A,B).\n:- (catch(atomic_concat(x,y,R),E,(R=err(E))) -> write(R) ; write(failed)), nl.\n' > /tmp/w.pl
./scrip /tmp/w.pl < /dev/null      # xy
swipl -q -g "consult('/tmp/w.pl'),halt"   # mine(x,y)
```
