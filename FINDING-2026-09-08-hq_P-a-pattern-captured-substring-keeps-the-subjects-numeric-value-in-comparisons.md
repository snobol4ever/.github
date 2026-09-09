# FINDING 2026-09-08 hq_P — ⛔ a pattern-captured SUBSTRING keeps the SUBJECT's numeric value in every comparison predicate

## Claim

After `subject PATTERN . var`, the captured `var` prints, sizes, concatenates and does **arithmetic**
correctly — but `LT LE GT GE EQ NE` compare it as though it still held the **whole subject's** numeric
value. Wrong in **both modes**. It is a **silent wrong answer that decides control flow**.

## Witness — 5 lines, no include, both modes

```
        subject  =  '100'
        subject  LEN(1) . captured
        OUTPUT  =  'captured = ' captured
        OUTPUT  =  LT(captured, 100)  'LT(captured,100) fired -- correct'
        OUTPUT  =  GE(captured, 100)  'GE(captured,100) fired -- WRONG'
END
```

| | `sbl -bf` | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `captured = ` | `1` | `1` | `1` |
| which branch fires | **LT** | **GE** | **GE** |

## Every other view of the value is CORRECT — that is what makes it dangerous

With `B = '100'` then `B LEN(1) . Q =`:

| probe | SCRIP | correct? |
|---|---|---|
| `Q` printed | `1` | ✅ |
| `SIZE(Q)` | `1` | ✅ |
| `Q + 0` | `1` | ✅ |
| `DATATYPE(Q)` | `STRING` | ✅ |
| `GE(Q,100)` | **fires** | ❌ |
| `LT(Q,100)` | **fails** | ❌ |
| `EQ(Q,1)` | **fails** | ❌ |
| `NE(Q,1)` | **fires** | ❌ |
| `LE(Q,100)` | fires | ✅ (coincides) |
| `GT(Q,100)` | fails | ✅ (coincides) |

⭐ **Arithmetic is right and comparison is wrong on the same value.** Every instrument a person would
reach for to check the value — print it, size it, add zero to it, ask its datatype — agrees it is `1`.
Only the operators that pick a branch disagree. **`Q + 0` returning `1` while `EQ(Q,1)` fails is the
whole finding in one line.**

## Mechanism, established by control arm rather than asserted

The comparisons behave as if the captured value were the **subject**:

| subject | capture | is capture the whole subject? | SCRIP comparison |
|---|---|---|---|
| `'5'` | `LEN(1) . P` → `5` | yes | ✅ correct |
| `'42'` | `LEN(2) . T` → `42` | yes | ✅ correct |
| `'zz9'` | `LEN(3) . S` → `zz9` | yes | ✅ correct |
| `'100'` | `LEN(1) . Q` → `1` | **no, proper substring** | ❌ compares as 100 |

**A capture equal to the whole subject is correct; a PROPER SUBSTRING carries the subject's numeric
view.** So the captured descriptor inherits a numeric field from the subject instead of deriving it
from the captured bytes.

## Scope — wider than the first symptom suggested

- ⛔ **Plain match capture is affected, not only match-with-replacement.** Both `A LEN(1) . P` and
  `B LEN(1) . Q =` are wrong. My first two witnesses used the replacement form and I nearly filed it
  as a replacement bug; it is not.
- ⛔ **The staleness survives copying.** After `Z = Z` the comparisons are still wrong, so an
  assignment does not normalise the descriptor and no defensive re-assignment works around it.
- Wrong in **mode 3 and mode 4** alike, so it is not a mode-specific wiring issue.

## What it costs today

`packages/snobol4/gimpel/SPELL_driver` — currently RED, dies at ERROR 246 stack overflow after
emitting 9 of 14 correct lines. Gimpel's `SPELL.sno` does:

```
SPELL_100	N  LEN(1) . M  =
	SPELL  =  SPELL(M)  ' HUNDRED'
```

`SPELL(M)` recurses with `M`; the callee's `GE(N,100)` is asked about a value that prints as `1` and
compares as `100`, so it takes the hundreds branch again — **unbounded recursion**. The stack
overflow is a *symptom two levels downstream* of a wrong comparison.

⚠️ The board reports this as `RC1`/stack overflow, which reads as a depth or frame-size problem —
i.e. as **hq_P performance work**. It is a correctness defect in the pattern engine. Anyone who takes
that row from the board alone will tune stack limits and never find it.

## Why nothing caught it

`SUBJECT PATTERN . VAR` then branching on `VAR` numerically is one of SNOBOL4's most ordinary idioms,
and the SNOBOL4 master reads **1894/1894 FAIL=0** on this tree. The corpus mostly compares captured
values as *strings*, or captures whole subjects, both of which are correct. ⭐ This is the sharpest
argument yet for the ladder walk: a green board over 1894 entries did not contain **one** program
that captures a proper substring and compares it as a number.

## Routing

Pattern engine / descriptor construction → **`hq_U`** (shared engine). ⛔ **Control arms are owed on
Icon and Prolog**: this is a DESCR-level numeric field, and per the corrected shared-node law
(CEO-405) the carriers — descriptor construction and the comparison builtins — are reached by every
frontend, so the lowerer census will under-report the owed set.

## Provenance

SCRIP `0567aba18`, corpus `34c90a593`, `RT_OPT=-O0`, oracle `/home/resources/x64/bin/sbl -bf`.
Found walking hq_P's NONET Q-Z gimpel slice, from `SPELL_driver`'s stack overflow, by ablating the
recursion until the failing ingredient was a single capture.
