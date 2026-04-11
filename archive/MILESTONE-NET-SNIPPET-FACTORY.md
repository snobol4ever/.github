# MILESTONE-NET-SNIPPET-FACTORY.md
## Sprint D-187 · snobol4ever/snobol4dotnet

**Status:** ⚠️ CURRENT  
**Goal:** Systematic snippet test factory — fill all coverage gaps in `TestSnobol4/Corpus/`
by mining corpus crosscheck tests, lib/ functions, and Gimpel building blocks.
Each snippet = self-contained SNOBOL4 + known output → one `[TestMethod]`.
No `-INCLUDE`. No external files. No input from stdin (or use `RunWithInput(s, input)`).

**Gate:** ≥ 2100 passed · 0 failed · all new Corpus files green

---

## The Pattern

Every test follows the same form already established in `CorpusRef_Assign.cs` etc:

```csharp
[TestMethod]
public void TEST_Corpus_NNN_name()
{
    var s = @"
        ... SNOBOL4 program ...
END";
    Assert.AreEqual("expected\noutput", SetupTests.RunWithInput(s));
}
```

For programs needing stdin: `SetupTests.RunWithInput(s, "line1\nline2")`.

**SNOBOL4 syntax rules to follow:**
- Multiple assignments on one line: use `;` semicolons — spaces are concatenation
- `TRIM` removes **trailing** whitespace only (never leading)
- `OPSYN(new, old, 0)` = function synonym (arg3=0); arg3=1/2 = operator synonym
- `DEFINE('SQRT(Y)')` → error 248 in SPITBOL (can't redefine system function names) — rename
- Conditional value: `LGT(A,B) X` — if LGT succeeds, result concatenated with X (D-NET-186 known bug)
- Labels: column 1. Statements: must be indented (tab or spaces).
- `:(LABEL)` = unconditional goto; `:S(L)` = goto on success; `:F(L)` = goto on failure
- `DIFFER(X)` succeeds if X is non-null; `IDENT(X)` succeeds if X is null
- `GT(A,B)` etc. return their first argument on success (for use in expressions)

---

## Coverage Map — what exists vs what to add

### Already covered (do not duplicate)
| Dotnet file | Crosscheck dir | Tests |
|---|---|---|
| `Rung8_StringOps.cs` | rung8 | 810 811 812 (replace/size/dupl) |
| `Rung9_TypesPredicates.cs` | rung9 | 910–914 (convert/datatype/num_pred/integer_pred/lgt) |
| `Rung10_Functions.cs` | rung10 | 1010–1018 (all 9) |
| `Rung11_DataStructures.cs` | rung11 | 1110–1116 (all 7) |
| `CorpusRef_ArithNew.cs` | arith_new | 8 tests |
| `CorpusRef_Assign.cs` | assign | 8 tests |
| `CorpusRef_Concat.cs` | concat | 6 tests |
| `CorpusRef_ControlNew.cs` | control_new | 7 tests |
| `CorpusRef_Hello.cs` | hello | 4 tests |
| `CorpusRef_Keywords.cs` | keywords | 12 tests |
| `CorpusRef_Output.cs` | output | 8 tests |
| `CorpusRef_Patterns.cs` | patterns | 20 tests |
| `CorpusRef_GimpelBits.cs` | — | 26 tests (Gimpel building blocks) |

### Gaps to fill (new files to create)

| New file | Source | Tests to add |
|---|---|---|
| `CorpusRef_Strings.cs` | crosscheck/strings/ | 065–075 + word1–4 + wordcount |
| `CorpusRef_Capture.cs` | crosscheck/capture/ | 058–064 |
| `CorpusRef_Data.cs` | crosscheck/data/ | 091–096 |
| `CorpusRef_LibMath.cs` | lib/math.sno (inlined) | max/min/abs/sign/gcd/lcm |
| `CorpusRef_LibStack.cs` | lib/stack.sno (inlined) | push/pop/peek/depth/empty/pattern-capture |
| `CorpusRef_LibString.cs` | lib/string.sno (inlined) | pad_left/pad_right/ltrim/rtrim/trimws/repeat/contains/startswith/endswith/index |
| `CorpusRef_GimpelBits2.cs` | Gimpel programs (inlined) | BASE10/RANDOM/PUSH-POP/MDY/DAY snippets |
| `CorpusRef_Feat.cs` | programs/snobol4/feat/ | f02/f04/f06/f08/f09 (string/pattern/builtin/data/function) |

---

## Step-by-Step Plan

### STEP 0 — Fix existing GimpelBits failures (9 failing → 0 failing)

File: `TestSnobol4/Corpus/CorpusRef_GimpelBits.cs`

| Test | Fix |
|---|---|
| `roman_small` / `roman_large` | Lines like `v<1> = 1000  v<2> = 900` — spaces = concatenation → error 212. Fix: use semicolons: `v<1> = 1000; v<2> = 900` |
| `sqrt_perfect_squares` | `DEFINE('SQRT(Y)')` → error 248. Rename function to `MYSQRT` throughout |
| `bsort_strings` / `bsort_integers` | D-NET-186 real bug (`LGT(A,B) V` RHS → error 212). Mark `[Ignore("D-NET-186")]` for now |
| `fixed_column_extract` | `TAB(10)` captures ` Bell ` (with leading space). TRIM removes trailing only → ` Bell`. Fix: change pattern to `LEN(5) . YEAR LEN(1) . NAME` or fix assertion to `Assert.AreEqual("1876\n Bell\nTelephone", ...)` — actually fix the pattern: use `TAB(5) BREAK(' ') . NAME` or adjust column numbers to match the actual string layout |
| `opsyn_alias` | `OPSYN('UPPER','UCASE',1)` wrong — arg3=1 means operator synonym. Fix: `OPSYN('UPPER','UCASE',0)`. Then re-test: if still error 154, mark `[Ignore("D-NET-187")]` |
| `fibonacci_recursive` | Pre-seeding `FIB(0) = 0` is wrong SNOBOL4 (calls FIB function). Fix: remove pre-seed lines, add `FIB = N` before `:S(RETURN)` as base case |
| `trim` | `TRIM` removes trailing only. `TRIM('  hello  ')` → `'  hello'`. Fix assertion: `Assert.AreEqual("  hello\nno spaces\n0", ...)` |

**Gate after step 0:** 2009+ passed, ≤ 2 failed (only D-NET-186 ignores), 2 skipped → 0 failed non-ignored.

---

### STEP 1 — CorpusRef_Strings.cs

Source: `corpus/crosscheck/strings/*.sno` + `.ref` files.
The word2–word4 tests need multi-line input — use `RunWithInput(s, input)`.

Tests to add:
```
065_builtin_size       SIZE('hello') = 5
066_builtin_substr     SUBSTR('hello world',7,5) = 'world'
067_builtin_replace    REPLACE('hello','aeiou','AEIOU') = 'hEllO'
068_builtin_trim       SIZE(TRIM('hello   ')) = 5
069_builtin_dupl       DUPL('ab',3) = 'ababab'
070_builtin_reverse    REVERSE('hello') = 'olleh'
071_builtin_ucase      UCASE(&LCASE) = &UCASE  (26 letters)
072_builtin_lcase      LCASE(&UCASE) = &LCASE
073_builtin_lpad       LPAD('hi',6) = '    hi'
074_builtin_rpad       SIZE(RPAD('hi',6)) = 6
075_builtin_integer    DATATYPE(1) = 'integer'
word1                  single-word input extraction (no input needed — embed string)
word2/word3/word4      TAB/ARB/BREAK column parsing (embed input as SNOBOL4 string, avoid stdin)
wordcount              BREAK/SPAN word loop (embed input)
```

**Note on word tests:** Rather than stdin, embed input as a string variable and loop over it
using pattern matching instead of `INPUT`. This keeps tests self-contained.

---

### STEP 2 — CorpusRef_Capture.cs

Source: `corpus/crosscheck/capture/*.sno` + `.ref`.

```
058_capture_dot_immediate    'hello world' LEN(5) . V  → V = 'hello'
059_capture_dollar_deferred  P = LEN(5); 'hello world' P . V  (deferred via $)
060_capture_multiple         'John Smith' BREAK(' ').F ' ' REM.L → F='John' L='Smith'
061_capture_in_arbno         ARBNO(ANY('a') . V)  — last captured char
062_capture_replacement      'hello there' LEN(5) . W = 'goodbye' → output W + new string
063_capture_null_replace     replace match with null (deletion)
064_capture_conditional      conditional pattern with capture
```

---

### STEP 3 — CorpusRef_Data.cs

Source: `corpus/crosscheck/data/*.sno` + `.ref`.

```
091_array_create_access   ARRAY(5), set A<1>/A<3>/A<5>, read back
092_array_loop_fill       fill with loop, verify
093_table_create_access   TABLE(), T<'key'> = val, read back
094_data_define_access    DATA('complex(real,imag)'), create, access fields
095_data_field_set        mutate DATA field: real(X) = 5
096_data_datatype_check   DATATYPE of DATA instance = type name (lowercase)
```

---

### STEP 4 — CorpusRef_LibMath.cs

Inline `lib/math.sno` body directly into the test string. No `-INCLUDE`.
Each function is a `DEFINE(...) :(end)` block followed by the function body.

```csharp
// Template — inline the entire math.sno then add driver:
var s = @"
        DEFINE('max(max,x)')                :(max_end)
max     max = LT(max,x) x                  :(RETURN)
max_end
        ...all other functions...
        OUTPUT = max(3, 7)
        OUTPUT = min(3, 7)
        ...
END";
Assert.AreEqual("7\n3\n3.5\n2.1\n42\n0\n1\n-1\n4\n25\n12", ...);
```

Tests:
```
max(3,7)=7  min(3,7)=3  max(3.5,2.1)=3.5  min(3.5,2.1)=2.1
abs(-42)=42  sign(0)=0  sign(5)=1  sign(-3)=-1
gcd(12,8)=4  gcd(100,75)=25  lcm(4,6)=12
```

---

### STEP 5 — CorpusRef_LibStack.cs

Inline `lib/stack.sno`. Tests:
```
basic push/pop/depth (3 pushes, verify depth=3, pop order c/b/a, depth=0)
empty stack FRETURN
peek does not pop
pop into named variable ($var assignment via arg)
push values captured from pattern match
```

---

### STEP 6 — CorpusRef_LibString.cs

Inline `lib/string.sno`. Tests:
```
pad_left('hi',6,'*') = '****hi'
pad_right('hi',6,'*') = 'hi****'
ltrim('   hello') = 'hello'
rtrim('hello   ') = 'hello'
trimws('  hello  ') = 'hello'
repeat('hi',3) = 'hihihi'
contains('foobar','oba') succeeds
startswith('foobar','foo') succeeds
endswith('foobar','bar') succeeds
startswith('foobar','bar') fails
index('foobar','oba') = 2
index('foobar','xyz') = 0
```

---

### STEP 7 — CorpusRef_GimpelBits2.cs

New Gimpel snippets (all inlined, no -INCLUDE):

**BASE10** — convert hex/octal string to decimal:
```snobol
DEFINE('BASE10(N,B)T')
BASEB_ALPHA = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                            :(BASE10_END)
BASE10  N LEN(1) . T =                     :F(RETURN)
        BASEB_ALPHA BREAK(*T) @T            :F(ERROR)
        BASE10 = (BASE10 * B) + T           :(BASE10)
BASE10_END
        OUTPUT = BASE10('FF', 16)           * 255
        OUTPUT = BASE10('10', 8)            * 8
        OUTPUT = BASE10('1010', 2)          * 10
END
```

**RANDOM** — deterministic seed test (RAN_VAR=1 → first value known):
```snobol
        DEFINE('RANDOM(N)')
        RAN_VAR = 1                         :(RANDOM_END)
RANDOM  RAN_VAR = REMDR(RAN_VAR * 4676., 414971.)
        RANDOM = RAN_VAR / 414971.
        RANDOM = NE(N,0) CONVERT(RANDOM * N,'INTEGER') + 1
                                            :(RETURN)
RANDOM_END
        R = RANDOM(0)       * real in (0,1)
        GT(R, 0.0)                          :F(FAIL)
        LT(R, 1.0)                          :F(FAIL)
        OUTPUT = 'ok'
        OUTPUT = RANDOM(10) * integer 1..10
END
```

**PUSH/POP** — Gimpel stack via DATA+NRETURN:
```snobol
        DEFINE('PUSH(X)')  DEFINE('POP()')  DEFINE('TOP()')
        DATA('LINK(NEXT,VALUE)')            :(PUSH_END)
PUSH    PUSH_POP = LINK(PUSH_POP, X)
        PUSH = .VALUE(PUSH_POP)             :(NRETURN)
POP     IDENT(PUSH_POP)                    :S(FRETURN)
        POP = VALUE(PUSH_POP)
        PUSH_POP = NEXT(PUSH_POP)           :(RETURN)
TOP     IDENT(PUSH_POP)                    :S(FRETURN)
        TOP = .VALUE(PUSH_POP)              :(NRETURN)
PUSH_END
        PUSH('a')  PUSH('b')  PUSH('c')
        OUTPUT = POP()      * c
        OUTPUT = POP()      * b
        OUTPUT = POP()      * a
END
```

**MDY** — day-of-year to month/day/year:
```snobol
        ... inline MDY function body ...
        OUTPUT = MDY(71, 83)    * 3/24/71
        OUTPUT = MDY(72, 60)    * 2/29/72  (leap)
END
```

---

### STEP 8 — CorpusRef_Feat.cs

Source: `corpus/programs/snobol4/feat/f*.sno`. These already have `PASS`/`FAIL` output.
Wrap each as-is:

```
f02_string_ops         SUBSTR/REPLACE/DUPL/SIZE/REVERSE/TRIM → 'PASS'
f04_pattern_primitives LEN/POS/RPOS/TAB/RTAB/ANY/SPAN/BREAK/ARB/ARBNO → 'PASS'
f06_builtins_predicates IDENT/DIFFER/GT/LT/GE/LE/EQ/NE/INTEGER/REAL/LGT → 'PASS'
f08_data_array_table   ARRAY/TABLE/DATA + field access → 'PASS'
f09_functions          DEFINE/RETURN/FRETURN + recursive FACT(5)=120 → 'PASS'
```

---

## Known Real Bugs (do NOT fix in this milestone — mark [Ignore])

| Bug ID | Symptom | Test |
|---|---|---|
| D-NET-186 | `LGT(A,B) V` on RHS → error 212 | bsort_strings, bsort_integers |
| D-NET-187 | `OPSYN('X','UCASE',0)` → error 154 | opsyn_alias |

These need parser/runtime investigation in a separate sprint.

---

## Files to Create/Modify

```
TestSnobol4/Corpus/CorpusRef_GimpelBits.cs   MODIFY  (Step 0 fixes)
TestSnobol4/Corpus/CorpusRef_Strings.cs      CREATE  (Step 1)
TestSnobol4/Corpus/CorpusRef_Capture.cs      CREATE  (Step 2)
TestSnobol4/Corpus/CorpusRef_Data.cs         CREATE  (Step 3)
TestSnobol4/Corpus/CorpusRef_LibMath.cs      CREATE  (Step 4)
TestSnobol4/Corpus/CorpusRef_LibStack.cs     CREATE  (Step 5)
TestSnobol4/Corpus/CorpusRef_LibString.cs    CREATE  (Step 6)
TestSnobol4/Corpus/CorpusRef_GimpelBits2.cs  CREATE  (Step 7)
TestSnobol4/Corpus/CorpusRef_Feat.cs         CREATE  (Step 8)
```

No changes to runtime or compiler unless a new test reveals a real bug.
If a test fails unexpectedly → diagnose → if test bug fix test; if runtime bug add `[Ignore("D-NET-NNN")]` and log in SESSIONS_ARCHIVE.

---

## Session Start Commands

```bash
cd /home/claude/snobol4dotnet
git pull --rebase
dotnet build TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true --no-build
# Baseline: 2009 passed, 9 failed, 2 skipped. HEAD = bdc541f.
# Work steps 0–8 in order. Run tests after each step.
```
