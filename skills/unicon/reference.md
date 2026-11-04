# Unicon reference, distilled from the Unicon documentation

Sources: the book chapters `/home/resources/manuals/icon/unicon-book-<chapter>.txt` (31 files; the eight that decide a SCRIP landing are cited below), `unicon-utr8.txt` (the language reference, UTR 8b), `unicon-utr2.txt`, `unicon-utr3.txt` (iyacc), `unicon-utr5.txt`, the book's .tex and the UTRs under `/home/resources/unicon/doc`, and the translator `/home/resources/unicon/uni/unicon/` (`idol.icn` the class emission, `unilex.icn` the reserved words). The oracle is `unicon_bin()` (skill `unicon` § 1). Every section ends with a status table: what SCRIP does today, measured 2026-11-04 on origin by running the same five-line probe through `unicon` and `scrip --dialect=unicon` (the battery is rebuilt in minutes: write the probe, run both, compare; a probe the oracle rejects is not a fact). GREEN = byte-identical; RED = named; the witness is a design witness (`corpus/tests/icon/unicon/`), a rung (`ladder__rungNN_*`) or a UniTests entry (`corpus/packages/icon/unicon_tests/<category>/<name>`). A fact the book states and the oracle contradicts is recorded as the oracle's.

## 1. langref (`unicon-book-langref.txt`, and UTR 8)

- **Literals.** Integers are arbitrary magnitude (large integers promote automatically); the suffixes `K M G T P` multiply a decimal literal by 1024^n (`2K` = 2048, `1M` = 1048576); radix literals `16rFF`, case insensitive. **Pattern literals** are regular expressions in `< >`; inside the marks operators and reserved words lose their meaning, concatenation is implicit, and `* + ? { } [ ] .` are special. A triple-quoted string `"""..."""` spans lines (the oracle reports `*x` = 7 for `"""one\ntwo"""`).
- **Reserved words Unicon adds** (a variable can no longer have these names; in SCRIP they are reserved only in a Unicon program, skill `unicon` R1): `class method initially import package thread critical abstract` (and `end` closes a class). `abstract` precedes a method header in place of its body; a class with an abstract method is itself abstract. `critical x : expr` serialises `expr` on a mutex or on an object that has one. `thread expr` runs `expr` in a new thread and yields the thread handle.
- **Operators Unicon adds.** `::` (global or package qualification, § 4); `??` the pattern match control structure and `=p` the unary match inside a scan (§ 5); the pattern operators `||` (follows), `.|` (alternation), `->` (assign on whole-match success), `=>` (immediate assign), unary `.` + name as `.> v` (assign the current position), backquotes `` `expr` `` (evaluate at match time), `&&`; `@>` send and `<@` receive between threads (§ 6); the list comprehension `[: expr :]` and the multi-subscript `L[2,3]`; `|||` list concatenation already in Icon is kept.
- **Keywords.** `&clock` and `&dateline` carry time-zone information (diffs); `&now`, `&errno`, `&pick` (SCRIP's skill lists them as R5); `&features` lists `concurrent threads` in Unicon 13.3; `&current &source &main &level` for co-expressions and multiple programs.
- **Built-in functions.** `function()` generates 292 names in unicon 13.3 against Arizona's 91. The additions are, by family: **patterns** `Abort Any Arb Arbno Bal Break Breakx Fail Fence Len NotAny Nspan Pos Rem Rpos Rtab Span Succeed Tab Pattern pattern_*`; **reflection** `classname constructor fieldnames globalnames localnames staticnames paramnames membernames methodnames methods oprec parent structure keyword Clone`; **threads** `mutex lock unlock trylock condvar signal wait spawn send receive Attrib`; **system and POSIX** `chmod chown chroot crypt ctime exec fcntl fdup fetch filepair flock fork getegid geteuid getgid getgr gethost getpgrp getpid getppid getpw getrusage getserv gettimeofday getuid gtime hardlink ioctl kill lstat mkdir pipe readlink ready rmdir select setenv setgid setgrent sethostent setpgrp setpwent setservent setuid signal stat symlink sys_errstr syswrite truncate umask utime`; **extras** `array atanh callout cofail istate load max min pindex_image trap Pending Event EvGet EvSend eventmask`; **graphics** (`Draw* Fill* Win* Font Color* Texture ...`, about 100 names; excluded by class CEO-1315). `chdir()` with no argument returns the current directory; `system(x, f1, f2, f3, mode)` takes a list, three redirections and a mode.

| Feature | SCRIP today | Witness |
|---|---|---|
| `K M G T P` suffixes, `numeric("3k")` | RED: parse error `1k` | UniTests general/numeric, thread/gc, thread/talloc |
| triple-quoted strings | RED: parse error | unicon/triple_strings |
| regex literals `<...>` | RED: parse error | pattern/ralternate rasterisk rbasic rcurly rplus rquestion |
| the eight reserved words | GREEN (marker) | design step 1, rung 43 |
| `::name`, class and package qualification | GREEN | uni_global_qualify, rung 44 qualified_global |
| `[: e :]`, `[,]` | RED: parse error | lib/jsontests, general/proto |
| `function()` of Unicon's 292 | RED: SCRIP lists Arizona's 91 | probe `every write(function())` |
| `&features` `concurrent threads`, `&now` an integer | RED (`&now` reads null) | probe |
| pattern functions Len..Tab | GREEN (inline boxes and values, § 5) | design step 4, rung 46 |
| posix functions (`stat getpid gettimeofday mkdir rmdir chdir()` no-arg) | RED: error 106 | UniTests posix/* (17 entries) |

## 2. diffs (`unicon-book-diffs.txt`)

The book's own list of what breaks an Icon program, in full: (1) functions Unicon broadens where it is consistent and unambiguous, chiefly on lists (`insert()` into the middle, `reverse()` of a list, `key()` of a list); (2) `&clock` and `&dateline` extended with time-zone information, which can change a program that uses them where failure is possible; (3) objects: `class`, `package` and `import` are no longer variable names; (4) the system interface presumes a hierarchical file system and Internet protocols; (5) graphics, including 3D, and more image formats; (6) GDBM and SQL databases (ODBC or the SQLite plugin); (7) multiple programs loaded at once and execution monitoring (`load`, `&main`, `&level`). The list a lander checks, with SCRIP's rule: a difference that changes an Icon program's answer is selected by the program's Unicon state in lower, never in the runtime (skill `unicon` § 1): `name()` of an element (`ICN$UNAME`), `key(list)` (`ukey`), `system()` status (`ICN$USYSTEM`). Differences measured on the oracle beyond the book: integers and reals sort as one numeric class; `system("exit 3")` is 3 not 768; reals print at 16 digits (`%.16g`) not 10 (blocked on Lon's `real_digits` grant); the error text for `--` on mismatched operands reads "two csets, two sets, or two tables expected" (Arizona: "two csets or two sets expected").

| Difference | SCRIP today | Witness |
|---|---|---|
| list `insert`/`delete`/`reverse`/`sortf` | GREEN | uni_list_ext, rung 45 list_ops |
| `key(list)` indices | GREEN (Unicon state only) | rung 45 key_list |
| `system()` exit status | GREEN (Unicon state only) | rung 47 system_status |
| `name()` forms `table_1[...]` `list_1[3]` `record C_1.f` | GREEN (Unicon state) | the harness name-form gate, UniTests general/var |
| 16-digit reals | RED (grant) | uni_class_hello, checkc checkx ck checkfpc checkfpx overflow tprintf ilib |
| mixed int/real sort order, `min`/`max` lists | RED | general/sort |
| `&clock`/`&dateline` time zone | not probed | none yet |

## 3. classes (`unicon-book-classes.txt`, chapter 10, and the inheritance chapter in `unicon-book-large.txt`)

- A class is a record type with associated procedures called methods; an instance is an object. Syntax: `class name [: super]* (fields) methods [initially [(params)] code] end`. A class may also contain `global` and `record` declarations (they live in the global space). `method name(params) ... end` runs against an object through the implicit `self`; fields and methods are used by bare name inside a method; `self.f` and `self.m()` are the explicit forms and are rare.
- **Constructor and `initially` (three rules).** (a) No `initially`: the constructor is a record constructor, arguments fill the fields in order, missing ones are null. (b) `initially(p1, p2)` with a parameter list: NO implicit field assignment; the constructor's arguments bind the `initially` parameters and the section assigns what it likes. (c) `initially` without a list: record-like assignment first, then the section runs, so declare auto-initialised fields after the parameter-initialised ones. A subclass `initially` normally calls its superclass `initially` (`self.A.initially(v)`).
- **Invocation.** `obj.m(args)` handles inheritance and polymorphism. Called as a procedure, a method is `Class_method(obj, args)` (class name, underscore, method name; the object is the first argument) and ignores overriding. Fields of an object may be read as a record's (`o.a`, `o["a"]`) but that is deprecated outside methods.
- **Inheritance.** `class B : A : C (y)`: superclasses are listed after colons, fields of every superclass are visible by name, methods resolve through the superclass graph (the graph need not be acyclic by the book's wording; the oracle resolved `class C : A : B()` calling `m` to A's); `abstract method area()` leaves the body to subclasses.
- **Names the compiler reserves** (large, § 4): field names `s` and `m`; identifiers consisting of `n` plus an integer; for each class `foo`: `foo`, `foostate`, `foomethods`, `foooprec`, and `foo_bar` for each method `bar`.
- SCRIP translates a class the way unicon does, in lower (`lower_icon_class.c`: the state and operations records, the constructor, dispatch, `initially` chaining, the reflection prelude), so `image(o)` reads `object Foo_1(1)`, `type(o)` reads `Foo__state`, `C_get(o)` and `o.get()` agree.

| Feature | SCRIP today | Witness |
|---|---|---|
| fields, methods, `initially`, `self`, constructor defaults | GREEN | design step 2, rung 43 |
| `initially(x)` parameters; defaults `/a := ...` | GREEN | probe, rung 43 initially |
| inheritance, super `initially`, polymorphic `(a \| d).speak()` | GREEN | rung 43 inherit_override, probe |
| multiple inheritance order | GREEN (A first) | probe |
| abstract methods, `Class_method(obj)` call form | GREEN | probe |
| operator-overloading classes (`unicon/ovld`) | GREEN | UniTests unicon/ovld |
| class fields with `:` types (`clin_err`) | RED: parse error `expected ) (got :)` | unicon/clin_err |
| the `lang` library classes (Object, Class ...) via `import lang` | RED: cannot find package | lib/class_static objecttests property_demo singleton unittest |

## 4. large (`unicon-book-large.txt`, "Writing Large Programs")

- **Abstract classes and patterns of design.** An abstract class is never instantiated; its abstract methods are implemented by subclasses (Singleton, Proxy, Chain of Responsibility, Visitor: the book's examples are plain classes and need nothing beyond § 3).
- **Packages.** `package foo` (or `package "/path/foo"`) puts every global of the file (variables, procedures, records, classes) in package `foo`; one package declaration per file, conventionally first. The compiler records the package's symbols in a database (`uniclass.dir/.pag`) and applying `import foo` links `foo.u` and the package's other files. `import foo, bar` follows the `link` rules and uses `IPATH`. Under the hood a name is mangled to `foo__name`; `foo::name` selects a package explicitly and `::name` the unmangled global (e.g. a method called `write` calls the built-in with `::write`; omitting `::` recurses until memory runs out). Declaring a global with a built-in's name warns (silenced by `-n`). A package file is not a program: its `main` is `foo__main`. Compile all files of a package before importing it; with several files the order matters (`unidep` computes it).
- **Link.** `link name` pulls an IPL module (`strings numbers ...`) by `IPATH`; an `import` is a link plus scope information.

| Feature | SCRIP today | Witness |
|---|---|---|
| `package p` mangling to `p__name` and `p::name` | GREEN | design step 3 uni_pkg_import, uni_global_qualify |
| `import p` of a sibling package file or directory, and `IPATH`/`ICONPATH` | GREEN | uni_pkg_import |
| `::name` inside a class | GREEN | rung 44 qualified_global |
| `link strings` (IPL) | GREEN | rung 44 link_strings |
| a single-file program with `package` (no importer) | both oracles refuse: missing main | none (not a witness) |
| `import lang` (the library's classes: `/home/resources/unicon/uni/lib/*.icn` that declare `package lang`) | RED: `cannot find package lang`; `icn_resolve_imports` searches IPATH, so the harness needs the path or the package vendored | the five lib/ entries above |
| `link cfunc` (loadfunc) | RED | general/cfuncs |

## 5. string (`unicon-book-string.txt`, "String Processing", and UTR 18 as the book cites it)

- **Scanning** is Icon's (`s ? e`, `tab`, `move`, `match`, `bal`, `upto`, `find`, `many`, `any`, `pos`) and unchanged.
- **The pattern type** (the book's "scanning on steroids"; the concepts translate from SNOBOL4). Patterns are values. Two notations use them: the unary `=p` inside a scan (matches `p` at the cursor and moves it) and `s ?? p`, which opens a new scanning environment on `s` and looks for `p` from left to right. Composers: `p1 || p2` follows, `p1 .| p2` alternation, `p -> v` assigns the matched substring to `v` if the whole match succeeds, `p => v` assigns when the match reaches it (immediately), `.> v` assigns the current position, `` `v` `` evaluates `v` at match time (variables, function calls and simple method invocations), `&&`; the functions are the table in § 1: `Any Arb Arbno Bal Break Breakx Fail Fence Len NotAny Nspan Pos Rem Rpos Rtab Span Succeed Tab Abort`. A cset argument means "any one of", a string argument matches itself, anything else converts to a string. **Variables in a pattern are evaluated in the scope of the MATCH, not of the construction**: a pattern built in one procedure and matched in another reads (and assigns) the matching procedure's variables; declare such variables explicitly. (This is exactly SCRIP's scan marker: `skill unicon` § 2.)
- measured on the oracle: matches are non-overlapping and `?? ` restarts at the previous END; an empty match repeats forever; `Pos(n)` is cursor n-1 and a non-positive n counts from the end; `.>` yields 1-based positions; a deferred CALL in backquotes is a success test (its value is not matched) while a deferred variable is matched as its value.

| Feature | SCRIP today | Witness |
|---|---|---|
| `s ?? p`, value patterns, `\|\|`, `.\|`, `->`, `Len Pos Rpos Tab Rtab Any NotAny Span Break Breakx Rem Arb Bal Arbno` | GREEN | design step 4 uni_pm_*, UniTests pattern/lenss plen assignss ABCss bigpss expss nspantst pairss parbno setcur breaks parb |
| `=>` immediate assign to a local, a file target | GREEN | uni_pm_immed_local, rung 46 concat_assign, span_break |
| `.>` cursor | GREEN | uni_pm_cursor, pattern/setcur |
| backquote variable, call, parameter, recursive deferred call | GREEN | uni_pm_defer_var, uni_pm_defer_param, uni_pm_defer_rec |
| `s ?? p := x` replacement; `pattern_match(s, p)`; `type(p)` is `pattern` | GREEN | pattern/lenss, assignss, plen |
| alternation or any variable pattern inside an `every` loop | RED (planner row to hq_zetas) | rung 46 alternation, UniTests pattern/failss balss |
| `Fail`/`Abort` inside a deferred alternation; `Bal`; `Len` of a backquoted value | RED | pattern/failss, balss, nest4, pimmed |
| `Pos`/`Tab` crashes | RED rc -11 | pattern/ppos, ptab |
| regex literals `<...>` | RED parse | pattern/r* |
| `pimgtest` (image of patterns), `peval`, `sawss`, `unevalcharss`, `unevalintss` | RED | the entries named |

## 6. thread (`unicon-book-thread.txt`, "Threads", Unicon 13.3)

- **Creation.** `thread expr` creates a thread and starts it; `spawn(co [, params])` turns a previously created co-expression into a thread (`thread E` is `spawn(create E)`); both return the thread handle; `wait(t)` blocks the caller until `t` finishes (`every wait(!L)` joins a list); the program ends when the main thread ends, so the main thread must wait.
- **Evaluation context.** A thread starts from a SNAPSHOT of the parameters and local variables at creation (like a co-expression), so threads do not race over the creator's locals; globals and structures are shared.
- **Thread safety.** Structures are not thread-safe by default; `mutex()` makes a mutex object and `mutex(L)` / `mutex(T, mtx)` makes a structure that is protected by one. `lock(m)`, `unlock(m)` (both return the mutex or fail), `trylock(m)` (fails instead of blocking); `critical m : expr` locks, evaluates and unlocks. Release 13.3 changed two rules: the mutex is released however the region is left (`return`, `break`, failure), and `critical m: e` yields the value of `e`, not of `m`. An `initial` clause is thread-safe (run once).
- **Condition variables.** `condvar()`, `wait(cv)` and `signal(cv[, n])` (wake one or n waiters); use `while` around the wait.
- **Messages.** Each thread has an inbox and an outbox (default limit 1024 values; `Attrib(T, INBOXLIMIT, n, OUTBOXLIMIT, m)` changes them; `INBOXSIZE`/`OUTBOXSIZE` read them). `x @> T` puts `x` in `T`'s inbox (`x @> main` for the main thread; `x @>` with no destination puts it in the sender's outbox: "produce x"); `<@` takes from the thread's own inbox, `<@ T` from `T`'s outbox; both succeed or fail at once (a full queue fails the send, an empty one fails the receive) and a blocking form waits. Thread-local storage, thread pools and the producer-consumer idioms follow in the chapter.
- The word `thread` (and `critical`) is a marker word: a file that uses it is a Unicon program (R1).

| Feature | SCRIP today | Witness |
|---|---|---|
| `thread E`, `wait(t)` | RED: parse error (`expected expression (got thread)`) | rung 48 thread_wait; UniTests thread/hellothr sum |
| `mutex()`, `critical m: e`, `lock/unlock/trylock` | RED: parse error and error 106 | rung 48 critical; thread/mutexfun |
| `condvar`, `signal`, `wait(cv)` | RED: error 106 | thread/queue sharelist |
| `@>`, `<@`, `Attrib`, `spawn` | RED | thread/channel tcom error critter |
| the thread-safe structure forms | RED | thread/sharelist stress |
| `&features` `concurrent threads` | RED | probe |
| design in hand | none built; a green-thread scheduler over the co-expression switch (`rt_coexpr.c`, `scrip_coexpr_activate`) gives a deterministic subset; real parallelism needs a thread-safe collector, which is not designed; ask the cto before building | skill `unicon` § 3 |

## 7. system (`unicon-book-system.txt`, "The System Interface")

- **Files.** `open(name [, mode])` (modes `r w a b c ...`, `"p"`/`"pr"` a pipe read from a command, `"pw"` a pipe written to one, `"n"`/`"nu"` network); `read`, `write`, `reads`, `close`; `open(dirname)` reads a directory (every `read` returns one name, unordered; `every write(!open("."))` lists it); `chdir()` returns the current directory and `chdir(s)` changes it; `mkdir`, `rmdir`, `remove`, `rename`; `stat(f)` returns a `posix_stat` record (fields `ino blocks mode nlink uid gid size mtime symlink ...`; `mode` is a string such as `drwxr-xr-x`); `chmod(f, mode)`, `chown`, `umask`, `utime`, `truncate`, `symlink`, `hardlink`, `readlink`, `lstat`; `flock(f, "s"/"x")` locks. A failing system call sets `&errno` and `errortext` explains it.
- **Processes.** `system(x, f1, f2, f3, mode)` runs a command (a string parsed on spaces with double quotes, or a list whose head is the program), redirects stdin, stdout, stderr to the three files, and returns the command's exit STATUS (a trailing `&` or mode `1`/`"nowait"` returns the pid instead); `exec`, `fork`, `wait(pid)`, `kill(pid, sig)`, `getpid()`, `getppid()`, `getuid()`..., `signal(sig, handler)`, `getrusage()`, `gettimeofday()` (a `posix_timeval`), `delay(ms)`, `getenv`/`setenv`; `select(files, ms)` and `ready(f, n)` for non-blocking input.
- **Networking.** `open(host:port, "n")` TCP client; a server opens `"na"` and accepts; `"nu"` UDP with `receive()` records; multicast and raw sockets through socket attributes in the open string (`proto=`); `getserv`, `gethost`, `getpw`, `getgr` look names up.

| Feature | SCRIP today | Witness |
|---|---|---|
| `open`/`read`/`write`/`close`/`remove`/`getenv`, append mode | GREEN | rung 47 file_io, UniTests posix/system (racy) |
| `open(dir)` reading names | GREEN | probe |
| `system()` exit status; pipe open `"p"` | GREEN (Unicon state selects the status) | rung 47 system_status |
| `stat`, `getpid`, `gettimeofday`, `mkdir`, `rmdir`, `chdir()` no-arg, `chmod`, `umask`, `utime` | RED: error 106 (no builtin) | posix/chdir chmod dir gettimeofday ls umask |
| `fork exec wait kill signal spawn` | RED | posix/fork exec wait kill spawn |
| `select ready fdup filepair fcntl` | RED | posix/select select-io pipe-select fdup filepair fcntl |
| sockets, `getserv getpw` | RED | posix/tcp udp mcast raw_sock uxsocket sockpeek getserv getpw ssh |
| `rusage`, `setenv` | RED | posix/rusage setenv |

## 8. struct (`unicon-book-struct.txt`, "Structures")

- **Lists.** `[]`, `list(n, x)`, `[e1, e2]`, and the comprehension `[: expr :]` (all results of `expr` in order; it fails if `expr` fails); `put` takes several arguments; `push`, `pop`, `pull`, `get`; `insert(L, i, x)` and `delete(L, i)` at a position; `L[i:j]` and `L[i+:n]` copy a sublist; `L1 ||| L2` concatenates copies; `L[2][3]` is `L[2,3]`; `*L`, `!L`, `?L`; `member(L, k)` succeeds for an index in range; `key(L)` is `1 to *L`; `reverse(L)`; `sort(L)`, `sortf(L, field)`. Lists are like tables whose keys are the positive integers.
- **Records.** `record complex(re, im)`; fields by `.name`, by string subscript `r["re"]` or by index `r[2]`; `member(R, s)` tests a field, `key(R)` generates the field names; no `insert`/`push` on records; `constructor("pt", "x", "y")` builds a record type at run time and returns its constructor.
- **Tables and sets.** `table(default)`, `T[k]`, `delete(T, k)`, `key(T)`, `member`, `sort(T, 1..4)` (pairs by key or value, or the flattened list); `set(L)`, `insert`, `delete`, `member`, `~`/`++`/`**`/`--` set operations; to put a list in a set write `set([L])` (the book's rule for the argument) and the oracle agreed (`set([[1,2],3])` has two elements).
- Unicon has no pointers; assignment of a structure copies a reference, `copy` is shallow, a deep copy is a user procedure (the book builds one with `key` and recursion).

| Feature | SCRIP today | Witness |
|---|---|---|
| list `insert`/`delete`/`reverse`/slice/`|||`/multi-subscript/`put` several | GREEN | probes, rung 45 list_ops |
| `sort(T, 3)`, table delete and key order, sets | GREEN | rung 45 set_ops, probes |
| `key(L)` indices | GREEN (Unicon state only) | rung 45 key_list |
| `member(L, k)` | RED: error 122 | probe |
| `key(R)`, `member(R, s)` over a record | RED: error 124 | probe |
| `constructor(name, fields...)` | RED: error 106 | probe |
| list comprehension `[: e :]` | RED: parse | lib/jsontests |
| `[,]` omitted elements | RED: parse | general/proto |
| `image` of structures `list_1(3)`, `table_1(0)`, `set_1(0)` | GREEN | probe, general/var |
| mixed numeric sort order (`sort` of ints and reals) | RED | general/sort |

## 9. The other chapters worth knowing

`unicon-book-advanced.txt` (Advanced Language Features), `unicon-book-programs.txt` (Programs and Expressions), `unicon-book-assoc.txt` (Inheritance and Associations, the UML side of § 3), `unicon-book-usecase.txt` (use cases), `unicon-book-database.txt` (excluded class: no SQL in the oracle build), `unicon-book-graphics.txt` and `-gui.txt` (excluded, CEO-1315), `unicon-book-monitor.txt` and `-experimental.txt` (execution monitoring, `load`, multiple programs; UniTests mt/*), `unicon-book-ipl.txt` and `unicon-book-ucl.txt` (the Icon Program Library, which SCRIP's `link` already serves, and the Unicon Component Library), `unicon-book-internet.txt` and `-cgi.txt` (sockets and CGI, mostly § 7), `unicon-book-lexyacc.txt` (Scanning and Parsing: iyacc, which the Unicon translator itself is written in), `unicon-book-referenc.txt` (bibliography). Co-expression witnesses: rung 49 (`coexp_refresh`, `coexp_gen`, both GREEN) and UniTests coexpr/*.
