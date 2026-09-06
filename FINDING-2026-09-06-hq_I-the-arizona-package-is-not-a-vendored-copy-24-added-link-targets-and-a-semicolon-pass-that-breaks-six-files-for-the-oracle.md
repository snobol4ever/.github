# FINDING 2026-09-06 hq_I — the arizona package is not a vendored copy: 24 added link targets, and a semicolon pass that breaks six files for the oracle (two of them graded)

**Measured** 2026-09-06 ~08:3x–09:1x CDT by hq_I under THE PACKAGE LOCKDOWN (MASTER-PLAN § THE PACKAGE LOCKDOWN, Lon 2026-09-06 08:2x: *"Fix the never graded business. Let's lock down our package testing and make it complete."*), on corpus `c72fc4082`+ / SCRIP `44f9e17ce`, oracle icont/iconx **9.5.25a** at `/home/resources/icon-master/bin`. Landed as corpus `a284bcdbb`.

**THE CONTRACT USED THROUGHOUT** is upstream's own `tests/general/Test-icon`, not an invention: `icont -s NAME.icn` ; `./NAME` (or `./NAME.exe`) `< NAME.dat`-if-present-else-`/dev/null` `> out 2>&1` ; `diff NAME.std out`.

## 1. 24 of arizona's 124 "shipped programs" are IPL library modules we added, not arizona tests

Upstream `icon-master/tests/general` ships **99** `.icn`. We ship **123** there. The 24 extras are exactly the set, with **zero** `procedure main` in every one:

`cfunc convert core datetime echo equiv factors hexcvt indices io_lib levensht lists_lib math numbers options printf random_lib rational records scan_lib sets_lib sort strings tables`

They are IPL procedures (`ipl/procs/*.icn`, plus `ipl/cfuncs/cfunc.icn`) vendored in as **link targets** so arizona tests that `link` them could compile (corpus `8f29d1dc3` *"vendor 17 missing link-target IPL files"*; `08761174b` renamed five to `*_lib` to break a collision with same-named arizona tests). Five are renamed: `io_lib ← procs/io`, `lists_lib ← procs/lists`, `random_lib ← procs/random`, `scan_lib ← procs/scan`, `sets_lib ← procs/sets`.

⛔ They are 24 of arizona's 35 ungraded. Under the POPULATION LAW they stay in the denominator, so they are now named `CONTAINER_OR_LIBRARY` in `arizona_tests/UNGRADABLE.tsv` — but **arizona's 124 is not 124 arizona programs**, and a reader of the cell should know that. ⭐ Same shape as the `ALL.icn` container that contaminated ipl's count on 09-05: *a structural count is only as right as the population it walks*, and `find -name '*.icn'` answers "how many Icon files are under this directory", never "how many vendored programs are here".

## 2. A blanket semicolon pass broke six files for the oracle — and the reason column must not blame the oracle for it

SCRIP's Icon is semicolon-required (RULES.md FACT RULE), so a mechanical pass added `;` to these sources. It also hit **`$`-preprocessor directives and declarations, which take no `;`**:

```
link rational;              ->  icont: File ilib.icn; Line 8 # ";": invalid declaration
$define LSIZE 16;           ->  the macro BODY becomes `16;`  (a semantic corruption, not just syntax)
$undef ghi;                 ->  icont: $undef: too many arguments
$ifdef _UNIX;               ->  icont: $ifdef/$ifndef: too many arguments
$include "tpp2.icn";        ->  icont: $include: too many arguments
```

**CONTROL, run per file with `icont -s -c` (compile only, so the link cascade cannot confound it):** upstream's `ipl/procs/io.icn`, `rational.icn`, `echo.icn` and `cfuncs/cfunc.icn` compile **cleanly**; our copies are **REFUSED**. `lists`, `random`, `scan`, `sets`, `convert` were also modified and still compile — so the pass was harmless in most files and lethal in a few, which is why it survived.

Blast radius, `.icn` files with a `$`-directive line ending in `;`: **arizona_tests 10 · jcon_tests 8 · ipl 2**.

⭐ **The reusable half is about the reason column, not the semicolons.** Writing *"the oracle refuses it"* on these rows would have been true as a sentence and false as a cause — **we** broke them. That is the same shape as the diagnostics this lane keeps meeting (`no /dev/null` when `/dev/null` opened fine; `Implement op=122` when op 122 has a case): **a stated cause that was never tested.** Every affected row in the landed census names the control instead.

## 3. TWO GRADED arizona tests are scored against refs their own source can no longer reach

Of the **90** graded arizona files (89 shipped + `hello.std` cut this sitting), **all 90 differ from upstream** — but only **5** are broken by it:

| file | oracle, OUR source | oracle, UPSTREAM source | why |
|---|---|---|---|
| `prepro` | **does not compile** (`$undef: too many arguments`) | reproduces `prepro.std` **exactly** | our `;` on `$define`/`$undef` |
| `ilib` | **does not compile** (`";": invalid declaration`) | reproduces `ilib.std` **exactly** | our `;` on `link rational` |
| `fncs1` | differs | — | the test **writes its own source text reversed**; our added `;` appears in the output |
| `io` | differs | — | the test **echoes its own source lines**; same cause |
| `recent` | differs | — | lists the **directory contents** (`found file: Makefile`) — depends on package layout |

⛔ **`prepro` and `ilib` cannot pass in any implementation.** They are counted among arizona's 43 FAILs and they are charged to SCRIP, but no compiler change can fix them: the shipped source does not compile in the oracle that cut the ref. `fncs1` and `io` are self-referential and can only ever be graded against a ref **re-cut from the source we actually ship**.

⭐ **This is the inverse of "never graded", and it is worse:** a program that is never graded is at least visibly a debt. A program graded against an unreachable ref is a **permanent false FAIL wearing the costume of a real one** — it depresses the cell, and every seat who tries to cure it is chasing a defect that is not in the compiler.

## 4. `link1.icn` was declared ungradable and is not

Landed concurrently in corpus `a1623cf8f`, all ten jcon gap entries read `NO-ORACLE-SHIPPED` — *"upstream jcon ships no link1.std, so … ungradable against its own oracle, **not work owed**"*. Nine are right in substance. `link1.icn` is not: with a **two-file compile** (`icont -s link1.icn link2.icn`; a one-file compile cannot resolve `link2.u1`, because `link link2` names a *compiled unit* and icont only compiles what is on its command line) and args `a b c`, the oracle prints `{{ a }}` / `{{ b }}` / `{{ c }}`, rc=0, deterministic. It needs the **argv sidecar** that landed today (SCRIP `44f9e17ce`).

⭐ **"We hold no ref" is the SYMPTOM; the lockdown asks for the oracle's own REASON, and the two coincide only when the oracle has actually been asked.** Declaring the symptom *"not work owed"* retires a live debt with a receipt saying it was checked. Exactly the class seat03 found the same morning in csnobol4 (`preload1`/`preload2` assumed ungradable, in fact gradable — *a wiring gap, not a fixture gap*). Two lanes, one day, same defect: **it is cheaper to write a plausible reason than to run the oracle once, so that is what happens unless the row demands evidence.**

## 5. An instrument correction I had to make to my own walker, twice

- **The contract.** My first walk used `icont -s -o NAME.exe` + `iconx NAME.exe` instead of upstream's `icont -s NAME.icn` + `./NAME`. It agreed with the correct contract on most files and disagreed on the ones that mattered (`prepro`, `ilib` reported "cannot open interpreter file" — a *harness* failure that reads exactly like a program failure). ⭐ **I nearly concluded "neither our source nor upstream's reproduces the .std", which would have hidden finding 3 entirely.**
- **The determinism check.** Two runs **back-to-back** passed `env.icn`; two runs **one second apart** fail it (`&clock 08:42:59` vs `08:43:02`). ⭐ Same family as this lane's `/dev/null` and 200k-activation lessons: **ask not only what the instrument measures, but whether its magnitude lets a negative mean anything.** A back-to-back pair cannot detect clock dependence — it is not a weak check, it is a check that *cannot fail* for the reason you are asking about.

## What landed, and what is owed

Landed (corpus `a284bcdbb`), every reason measured, the four numbers summing in both complete packages:

| package | shipped | graded | ungraded | ungradable | sums |
|---|---|---|---|---|---|
| arizona_tests | 124 | 90 | 0 | 34 | ✅ |
| jcon_tests | 91 | 81 | 1 | 9 | ✅ |
| ipl | 851 | 64 | 211 | 390 | ⛔ **186 unaccounted** — seat07's live row |

`hello.std` cut from the oracle; SCRIP matches **byte-for-byte in both modes** (md5 `abe20785` for oracle, m3 and m4). arizona graded 89→90, so the next arizona run should read **47/124, not 46/124** — ⚠ a POPULATION correction, not a gain.

**OWED, and it is a decision above one lane:** findings 2 and 3 mean the arizona sources are **not vendored copies**. The lockdown's own rule (1) says refs are cut from the oracle and *never through our own shims* — a vendor source rewritten to suit our frontend is a shim. Restoring them verbatim is the principled cure and it would move the arizona board hard (many would become REJECT, which is what the runner's REJECT bucket exists to count). ⛔ **Not taken unilaterally:** it is a vendoring-policy call with board-wide consequences, routed to the ceo, hq_B and hq_T rather than landed.
