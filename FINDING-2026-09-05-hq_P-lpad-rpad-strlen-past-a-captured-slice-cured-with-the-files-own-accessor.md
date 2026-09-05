# FINDING 2026-09-05 hq_P — LPAD/RPAD called `strlen()` on a captured slice; cured with the accessor the same file already used five times

**Measured:** hq_P, 2026-09-05, SCRIP `23f342b4d` + this cure, incremental `make`, **both modes**, oracle `/home/resources/x64/bin/sbl -bf`.
**Row:** `snobol4-lpad-rpad-noop-path-leaks-past-a-captured-slices-boundary` (rank 1, hq_P lane).
⭐ **Root-caused by seat11**, who unclaimed it rather than land a shared-runtime change — the correct FLEET-20 split (seats walk, census and witness; HQs cure). The diagnosis was exact and is credited in the commit.

## 1. The defect

`lpad_fn` / `rpad_fn` (`src/runtime/string_builtins.c`) took the subject's length with `strlen()` on the descriptor's char pointer:

    int64_t slen = (int64_t)strlen(STRVAL_fn);
    if (width <= slen) return STRVAL(rt_str_dup(STRVAL_fn));

A **captured slice** — `S LEN(3) . T` — is a descriptor pointing *into* the larger buffer with its own `slen`; there is no NUL at the slice boundary. So `strlen()` runs past the slice to the end of the whole subject, the `width <= slen` no-op branch is taken on a string that was never that long, and LPAD/RPAD return the **entire backing string**.

    	S = 'abcdefgh'
    	S LEN(3) . T
    	OUTPUT = '[' LPAD(T,5) ']'      oracle [  abc]      SCRIP [abcdefgh]
    	OUTPUT = '[' RPAD(T,5) ']'      oracle [abc  ]      SCRIP [abcdefgh]
    	OUTPUT = '[' T ']'              oracle [abc]        SCRIP [abc]      ← agrees
    	OUTPUT = SIZE(T)                oracle 3            SCRIP 3          ← agrees

⭐ **The last two lines are the whole diagnosis in two prints: the descriptor knew its length the entire time.** `T` printed correctly and `SIZE(T)` was right; only LPAD/RPAD threw that knowledge away and re-derived it from the bytes. This is not a slice bug — it is two functions declining to ask.

## 2. The cure — the file's own accessor, not a new one

`descr_slen()` (`core/core.h:12`) is the project's bounded-length accessor and **`string_builtins.c` already used it five times** (`:25`, `:28`, `:123`, `:124`, `:131`) — `REPLACE_fn` and the comparison helpers were correct all along. `REVERS_fn`, fifteen lines below the bug, carries the same logic inline. So the cure adds nothing new; it makes two functions consistent with their own neighbours:

    size_t slen_v = descr_slen(s);
    if (slen_v == 0 && STRVAL_fn && STRVAL_fn[0]) slen_v = strlen(STRVAL_fn);

⭐ **The `slen_v == 0` fallback is deliberate and is the conservative half.** The tree carries *two* conventions for `slen == 0` — `descr_slen` reads it as a genuine empty string, while `by_name_dispatch.c:9` and `REVERS_fn` treat 0 as "unset, go measure". Rather than rule on which is right (that is a wider question than this row), the fallback makes the change touch **only** descriptors with `slen > 0` — exactly the slice case — so a producer that leaves `slen` unset keeps today's behaviour and cannot regress.

Both returns also became `BSTRVAL(r, len)` instead of `STRVAL(r)`, matching `REVERS_fn`: `STRVAL` re-derives the length with `strlen`, which would truncate a result padded with a NUL pad character.

## 3. Verification

All four call paths seat11 named converge on these two functions — `core.c` `_LPAD_`/`_RPAD_` and `by_name_dispatch.c` `bn_lpad`/`bn_rpad` — and all four were exercised:

- slice witness, **m3 and m4**: `[  abc]` / `[abc  ]` — matches oracle.
- the row's own DONE-WHEN witness (75-char subject, `LEN(72)` capture, `RPAD(T,72)`): `SIZE(T)` = **72**, oracle 72. Before the cure this returned 75.
- **by-name path** via `APPLY('LPAD',T,5)` / `APPLY('RPAD',T,5)`: byte-identical to oracle.
- plain-string regression set (pad up, width ≤ length truncation no-op, empty subject, explicit pad char, exact-width): **byte-identical to `sbl -bf`, diff empty.**
- Icon smoke 15/15 both modes; Prolog smoke 5/5 both modes.

## 4. Why this needed a shared-node control arm

`string_builtins.c` is shared runtime — `lpad_fn`/`rpad_fn` are reachable from every frontend that exposes the builtins, which is why seat11 was right not to land it from a seat row. Control arm is the full SNOBOL4 master both modes plus the Icon master watermark, recorded below.

## 5. Control arm (measured, with the one red attributed)

- **Icon master board: m3 PASS=601 FAIL=0 / 601, m4 PASS=601 FAIL=0 / 601, ast 153/153, watermarks held.** ⛔ The board reports the watermark moved 596→601; that is **hq_B's** landing earlier today, **not this cure** — I am not re-pinning a floor I did not earn.
- Icon smoke 15/15 both modes · Prolog smoke 5/5 both modes.
- **SNOBOL4 master: total=1842, m3 PASS=1818 FAIL=1, m4 PASS=1818 FAIL=1** (m4_pass=1795 + 39 xfail + 7 xpass over the run-graded 1842), master-ast 28/28.

⚠️ **The one red is NOT this cure, and here is the argument rather than an assertion.** The diff touches exactly two functions, so every entry that never calls LPAD or RPAD compiles and runs bit-identically. **All four master entries that do call them — `simple_output_179`, `simple_output_40`, `simple_output_42`, `size_8` — PASS.** Independently, the ceo's own pre-change reading of this board (13:44, repaired corpus) was **m4 FAIL=1**, the same count.
⛔ **Labelled honestly: this is CONSISTENT WITH pre-existing, not PROVEN by a stash-and-rebuild A/B, which I did not run.** Naming the difference matters — the A/B is the stronger instrument and I am not claiming it.
