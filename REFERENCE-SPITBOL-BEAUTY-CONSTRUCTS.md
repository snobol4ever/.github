# REFERENCE — SPITBOL semantics for every construct beauty uses

**Built 2026-08-22 (HQ)** from `/home/claude/.tools/docs/spitbol-manual-v3.7.txt` (958 KB, **greppable** — far better than the PDFs) + `green-book.txt`, against `corpus/programs/snobol4/demo/beauty/beauty.sno` (622 lines) and its 17 `-INCLUDE` modules. Cited by manual heading so you can go straight there.

## 1. Lexing — the rule everything rests on
beauty overloads `$ . * ~ & @ + -` in BOTH arities. Disambiguation is purely lexical (*Fundamentals*): **"Unary operators are placed immediately to the left of their operand. No blank or tab character may appear between operator and operand."** Binary needs whitespace both sides. So `$'='` is indirection but `x $ y` is immediate assignment; `.dummy` is name-of but `p . thx` is conditional assignment. **A dropped space silently changes arity — no error.**

## 2. Precedence (*Operators*)
`= 0(R) · ? 1(L) · & 2(L) · | 3(R) · space 4(R) · @ 5(R) · + − 6(L) · # 7(L) · / 8(L) · * 9(L) · % 10(L) · ^ ! ** 11(R) · $ . 12(L) · ~ 13(R)`. Unary outranks every binary, right-to-left. **Subtle:** `$` and `.` share priority 12 **left**-associative, so `SPAN(…) $ tx $ *match(...)` is `((SPAN $ tx) $ *match)` — `tx` is set **before** `match()` runs, which is exactly what beauty's `TxInList` guard requires.

## 3. OPSYN'd operators
`semantic.inc` does `OPSYN('~','shift',2)` and `OPSYN('&','reduce',2)`. Third arg 2 ⇒ first arg must be an *unused binary* (`& @ # % ~`). So `~` is priority 13 right-assoc and `&` priority 2 left-assoc — **not** SPITBOL meanings. Redefining a defined operator is error 156. Unary `&` (keyword) and unary `~` (negation) coexist untouched.

## 4. Pattern primitives beauty actually uses
`SPAN BREAK ANY NOTANY LEN POS RPOS RTAB REM ARBNO FENCE(P)`, `|`, concatenation, and **the null string as a pattern** (`epsilon` is never assigned; a new variable's initial value is the null string). `ARB/BAL/TAB/BREAKX/SUCCEED/FAIL/ABORT` appear only inside beauty's *data strings*, never as live patterns.
- **SPAN/BREAK:** "SPAN must match at least one subject character, and will match the longest subject string possible." "BREAK(S) matches up to but not including any character in S… **Unlike SPAN and NOTANY, BREAK will match the null string.**" ⇒ `Comment = '*' BREAK(nl)` **fails on an unterminated last line** — that is why `main02` appends `nl`. SPAN never yields zero-length and never retries shorter.
- **LEN(0)** matches null. **POS/RPOS** consume nothing, only test the cursor.
- **ARBNO** matches the shortest string possible, initially null, extending **only when a subsequent forces a retry** — each retry supplies one *more* instance. `ARBNO(*Command)` grows one Command per backtrack and never re-partitions earlier instances.

## 5. FENCE — two different things, both in beauty
- **`FENCE` (pattern):** "Matches the null string and succeeds when the scanner is moving left to right… but fails if the scanner has to back up through it… FENCE as the first component of a pattern effectively anchors the match, regardless of &ANCHOR."
- **`FENCE(P)` (function, 31 uses — the load-bearing one):** "alternatives within the pattern are only seen by the scanner when it is moving forward. **Pattern backup will always pass through FENCE().**" ⛔ **Commonly got wrong:** backing through `FENCE(P)` does **not** fail the match (unlike the FENCE pattern) — it only makes P's internal alternatives invisible. beauty's whole recursive-descent grammar is committed-choice via this. **Not present in SNOBOL4.**

## 6. Assignment operators — timing is the crux
- **Immediate `$`:** "Immediate assignment occurs whenever a subpattern matches, **even if the entire pattern match ultimately fails.**" Fires on every retry; **never undone** on backtracking.
- **Conditional `.`:** "assignment occurs only if the pattern match is successful", and is performed **before** the replacement field is evaluated — beauty relies on this in `Gen` and `ReadWrite`.
- **`@` cursor:** "Cursor assignment is performed whenever the pattern match encounters the operator, including retries. It occurs even if the pattern ultimately fails." Behaves as the null string; 0-origin; may never exceed subject size.

## 7. Deferred `*expr`
Evaluated at **use** time, not construction time. Legal as a direct argument only to `ANY BREAK BREAKX LEN NOTANY POS RPOS RTAB SPAN TAB`; otherwise `*` moves out a level (`*EQ(I,4)`, not `EQ(*I,4)` — the latter is error 101). beauty's entire grammar is `*Expr0…*Expr17` forward references. ⛔ **Critical for an optimizer** (*Features Not Implemented*): "only Fullscan matching is provided and no heuristics are applied. **In particular deferred expressions are not assumed to match at least one character.**" A deferred recursive nonterminal may legitimately match null — **any length-based pruning is wrong.**

## 8. Anchoring / keywords
beauty sets **only** `&FULLSCAN = 1` and `&MAXLNGTH = 524288`; it never touches `&ANCHOR` or `&TRIM`, so matching is **unanchored** and anchoring comes from explicit `POS(0)`/`FENCE(...)`. "In SPITBOL the value of &ANCHOR is obtained **only at the start of the match**." Setting `&FULLSCAN` to 0 is an error. Unanchored failure advances the start cursor one position at a time. `&ALPHABET` is used as a *subject* to mint control characters; `&UCASE`/`&LCASE` drive `REPLACE`-based folding.

## 9. Function machinery
- **`NRETURN`** returns the **name** of a variable. beauty's `match/assign/Shift/Reduce/Push/IncLevel/Gen` all `NRETURN .dummy`; the manual blesses the idiom: *"It's just a ploy to use conditional assignment to get them called at precisely the right moment in the pattern match."* Non-name result ⇒ error 243.
- **`FRETURN`** from such a function is beauty's *predicate* mechanism (`match.inc`, `assign.inc`).
- **`EVAL(string)`** compiles an *expression* at runtime. ⛔ **`&CASE` is where `-f` bites:** "Setting it to zero will prevent case-folding during compilation with the functions CODE and EVAL. Initially 1." With folding on, `EVAL("p . thx . *Shift(...)")` resolves `thx`→`THX`. `CODE` is never called by beauty.
- `DATA('tree(t,v,n,c)')` field functions usable as **names** and assignment targets. `APPLY`, `ARRAY`, `TABLE`, `SORT`→N×2 array, `PROTOTYPE`, `CONVERT`, `FIELD`, `DATATYPE`. Redefining a builtin ⇒ error 248.
- **Indirect goto** `:S($('pp_' t))` — legal in the goto field, illegal in the label field.
- **Alternative evaluation** `(pred a, pred b, '')` — SPITBOL extension, evaluated left to right until one **succeeds**. ⛔ Trap: a called function returning failure makes SPITBOL fall through to the next alternative; both the comma and the parens are required. (**This is the construct `demo_treebank` needs and SCRIP has never implemented** — row `vlist-expr-alternation`.)
- **Predicate-chain assignment** `X = P1() P2() value`: "If failure occurs when evaluating the subject or replacement components, the assignment does not occur."

## 10. I/O
Statement-level `INPUT`/`OUTPUT`; `INPUT(.rdInput, 8, name '[-m10 -l131072]')`, `OUTPUT(.wrOutput, 8, name)`, `ENDFILE(8)`. Dynamic association may **fail** if the file is absent — beauty'

⛔⭐ **THE THIRD ARGUMENT IS A FILE SPEC IN SPITBOL, AND A FORTRAN FORMAT IN VANILLA SNOBOL4 — THEY ARE NOT THE SAME ARGUMENT (routed hq_P s274 at `ceo`'s instruction).** The examples above already *show* the SPITBOL form, but never state the contrast, and that gap cost two readers in one session. Vanilla SNOBOL4's `OUTPUT('OUT',6,'(121A1)')` passes a FORTRAN format that the implementation may ignore; **SPITBOL reads that same third argument as a FILE SPEC and opens a file named `(121A1)`**. ⭐ So a program doing this legitimately creates oddly-named files in its working directory under SPITBOL **and under SCRIP** — that is CORRECT dialect behaviour, ⛔ **not a SCRIP defect, and not a nit to mint.** The evidence is that `scrip` and `sbl` fail the snoflake suite's output-format-ignored fixture **identically** — two instruments agreeing. ⚠️ Operationally: run any harness arm from a **scratch cwd**, or a fixture like `corpus/benchmarks/snobol4/testpgms.spt:978` will drop stray files into a repo and dirty the tree (cured this way in `test_snoflake_suite.sh`, `5991cebd`).s `:F(FRETURN)` depends on that. Default record length 1024 unless `-l` overrides. ⚠ beauty's live input path is the **bare `INPUT` keyword on plain stdin** (`beauty.sno:604`/`609`); the `-l131072` named-file reader in `ReadWrite.inc:9` is **defined and never called**.

## 11. ⛔ Genuinely ambiguous in the manual — flagged, not guessed
1. **Ordering and firing point of multiple conditional assignments.** The manual says they happen after match success, and separately "at precisely the right moment", but **never states** that pending `.` assignments fire left-to-right in match order, nor when the RHS of `. *fn()` is evaluated. beauty's shift-reduce stack is only correct under "all pending `.` fire at end of match, in match order".
2. **Failure of the name-producing expression on the right of `$` or `.`.** beauty's `match()`/`notmatch()` FRETURN to veto an element. Documented for a *standalone* `*expr`, never as the right operand of `$`/`.`. Whether that fails the element, fails the match, or raises an error is **unspecified**.
3. **Whether conditional assignments made inside `FENCE(P)` survive** when the scanner later backs through the fence. Not addressed anywhere.
4. **`ARBNO(*P)` when `*P` matches null** — with heuristics disabled and no "at least one character" assumption, the manual gives **no termination rule**.
