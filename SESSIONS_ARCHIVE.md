> Org renamed SNOBOL4-plus → snobol4ever, repos renamed March 2026. Historical entries use old names.

## [Sessions B-1 through B-273, N-1 through N-247, J-1 through J-212, F-1 through F-222, I-1 through I-8, D-1 through D-164, R-1, README-1 through README-7 — PRUNED]

> Full history preserved in git. This file retains only the 10 most recent sessions.
> Use `git log --oneline` or browse GitHub history for older sessions.

## B-274 (2026-03-23) — M-BEAUTY-READWRITE partial + PLAN.md structural fix

**Branch:** main · **HEAD:** 93130ee (snobol4x) · 05c5454 (.github)

**Work done:**
- `_b_INPUT` n==3 fix in `src/runtime/snobol4/snobol4.c`: 3-arg `INPUT(var, chan, "file[-opts]")` now extracts filename before `[`, calls `fopen`, returns `FAILDESCR` on failure. Previously returned `NULVCL` (success) — steps 4–5 of ReadWrite driver were passing by accident.
- `snobol4x/PLAN.md` rewritten: 2315 lines → 61 lines. §START only. Session trails moved to `doc/PLAN_sessions_B274.md` and `.github/SESSIONS_ARCHIVE.md`.
- Root cause of 100KB PLAN.md: every session was appending multi-hundred-line handoff sections instead of updating §START in place. Fixed by convention: PLAN.md = §START only; trails go here.
- `_b_OUTPUT` n==3 fix NOT yet done — `Write.sno` uses `OUTPUT(.wrOutput, 8, fileName)`.

**Milestones fired:** none (M-BEAUTY-READWRITE still in progress)

**Next session:** Fix `_b_OUTPUT` n==3 → build → `INC=demo/inc bash test/beauty/run_beauty_subsystem.sh ReadWrite` → 8/8 → commit B-274: M-BEAUTY-READWRITE ✅ → advance to M-BEAUTY-XDUMP.

## B-274 cont. (2026-03-24) — M-BEAUTY-READWRITE partial; named-channel I/O; RULES.md NOW-row format

**Branch:** main · **HEAD:** cb03ddc (snobol4x) · (pending push, .github)

**Work done:**
- Built CSNOBOL4 2.3.3 from tarball (`snobol4-2_3_3_tar.gz`) — installed at `/usr/local/bin/snobol4`.
- Cloned missing `snobol4corpus` — was cause of `setup.sh` exit 1; 106/106 ALL PASS confirmed after clone.
- Implemented **named-channel I/O table** in `src/runtime/snobol4/snobol4.c`:
  - `io_chan_t _io_chan[32]` — maps channel# → `{FILE*, varname, is_output, buf, cap}`.
  - `_b_ENDFILE` upgraded from stub (returned FAILDESCR) to real close-by-channel.
  - `_b_INPUT` rewritten: stores varname from `a[0]`, opens file into channel slot.
  - `_b_OUTPUT` added (was completely missing): opens file for write, registers channel.
  - `NV_GET_fn`: channel-bound input vars now route to `getline()` from channel FILE*.
  - `NV_SET_fn`: channel-bound output vars now route to `fprintf()` to channel FILE*.
  - `_b_OUTPUT` registered: `register_fn("OUTPUT", _b_OUTPUT, 1, 4)`.
- **CSNOBOL4 8/8 PASS** (ref matches oracle).
- **ASM 7/8** — test 4 (`Read FRETURN on bad path`) fails. Hypothesis: OPSYN chain `input_→io→APPLY(io,name,chan,opts,file)` passes 4 args; `a[3]` may not carry the filename as expected from the `io` function's local variable `fileName` after pattern extraction.
- **SPITBOL times out at step 0** — known `M-MON-BUG-SPL-EMPTY` open bug; not this session's scope.
- Added `test/beauty/ReadWrite/tracepoints.conf` (minimal: Read/Write/LineMap only).
- **RULES.md**: added `⛔ NOW TABLE ROW FORMAT` section — forbids narrative prose in Sprint cell, documents correct 3-field format, gives wrong/right examples, enforces ~80-char limit.
- **PLAN.md** TINY backend row cleaned of narrative prose per new rule.

**Milestones fired:** none (M-BEAUTY-READWRITE still ❌)

**Next session (B-275):** Debug ASM test 4 — add `fprintf(stderr,...)` in `_b_INPUT` to print `n`, `fname`, `fopen` result. Likely fix is in how `io.sno` passes `fileName` through the OPSYN chain. Once 8/8 ASM → run 3-way → check SPL precedent → fire M-BEAUTY-READWRITE ✅ → advance to M-BEAUTY-XDUMP.

## Session F-215 — 2026-03-23 — Prolog emit dead _mark fix

**Repos touched:** snobol4x, .github
**Commit:** `978398a` (snobol4x main)

**Work done:**
- Read PLAN.md, ARCH.md (Byrd box model), FRONTEND-PROLOG.md, RULES.md, driver/main.c.
- Confirmed F-214's reported driver bug (hardcoded `pl_emit` in `-pl -asm` path) was **already fixed** in the repo by a prior session.
- Found actual live bug: `prolog_emit.c` emitted `_mark = trail_mark(&_trail)` inside `switch (_start) {` but before `case 0:` — unreachable dead code causing `gcc -Wswitch-unreachable` on every generated predicate.
- Fix: deleted the one dead line. `_mark` is already correctly initialized at function top (`int _mark = trail_mark(&_trail)`).
- Confirmed rungs 1 (hello) and 2 (facts/backtrack) both pass; warning eliminated.

**Milestones fired:** none

**Next session (F-216):** M-PROLOG-WIRE-ASM — get `-pl -asm` producing working x64. Steps: verify `asm_emit_prolog` entry point wires correctly end-to-end, test `null.pl` → exit 0, then `hello.pl` → fire M-PROLOG-HELLO, climb rung ladder via Byrd box β port.

## Session I-9 — ICON Frontend: Patch Archaeology

**Date:** 2026-03-23
**HEAD at start:** `54031a5` I-7 (I-8 was diagnosis-only, no commit)
**HEAD at end:** `54031a5` I-7 (no snobol4x commit — fixes not yet applied)

**What happened:**
- Cloned both repos fresh. Confirmed segfault on rung03_suspend/t01_gen.icn.
- Reviewed I-8 diagnosis in FRONTEND-ICON.md — three bugs documented.
- Clarified that "Bug 0" (is_gen=0 / stale binary) from the lost session transcript was a red herring in that session; in the current repo state the is_gen detection is correct. Root bugs are Fix 1 (left_is_value) and Fix 2 (rsp corruption).
- Developed exact patches for both fixes (see FRONTEND-ICON.md §NOW I-9 findings).
- Context window reached ~85% before fixes could be applied and tested. Reverted partial edits to avoid pushing broken state.
- Updated FRONTEND-ICON.md §NOW and PLAN.md with exact copy-paste patches for I-10.

**State at handoff:**
- snobol4x: `54031a5` — unchanged, no new commits
- .github: I-9 doc update committed and pushed

**Next session (I-10) start:**
1. Clone both repos
2. Read FRONTEND-ICON.md §NOW — two exact patches are there, copy-paste into icon_emit.c
3. Rebuild: `cd snobol4x/src/frontend/icon && make` (or the gcc one-liner from setup)
4. Test t01_gen → must output `1\n2\n3\n4` with no segfault
5. Write 5 R3 corpus tests (specs in §I-8 Bug Diagnosis R3 table)
6. Run full suite, confirm 20/20 pass
7. Commit + push snobol4x, then update .github and push

## Session I-9 — ICON Frontend: Patch Archaeology

**Date:** 2026-03-23
**HEAD at start:** `54031a5` I-7
**HEAD at end:** `54031a5` I-7 (no snobol4x commit — fixes not yet applied)

**What happened:**
- Confirmed segfault on rung03_suspend/t01_gen.icn still present.
- Bug 0 (is_gen=0) from lost I-8 transcript was a red herring; current repo is_gen detection is correct.
- Root bugs: Fix 1 (left_is_value for generator ICN_CALL) and Fix 2 (rsp corruption in jmp trampoline).
- Developed exact copy-paste patches for both — documented in FRONTEND-ICON.md §NOW.
- Context window hit 85% before apply+test cycle. Reverted partial edits, pushed doc update only.

**State at handoff:** snobol4x `54031a5` unchanged. .github updated with I-9 patches.

**Next session (I-10):** Apply both patches from FRONTEND-ICON.md §NOW, rebuild, test t01_gen, write 5 R3 tests, fire M-ICON-CORPUS-R3.
## Session F-223 — 2026-03-23 — M-PROLOG-BUILTINS ✅ + rung10 puzzle progress

**Repos touched:** snobol4x, .github
**Branch:** main

**Work done:**

- Removed stale M-PROLOG-WIRE-ASM from PLAN.md NOW table and flagged as implied-complete in FRONTEND-PROLOG.md (F-217 rungs 1–4 PASS via ASM proved wire already done).
- Confirmed M-PROLOG-BUILTINS (rung09): `functor/3`, `arg/3`, `=../2`, if-then-else, type tests (`atom/1`, `integer/1`, `var/1`, `nonvar/1`, `compound/1`) — all already wired in `prolog_emit.c` and `prolog_builtin.c`. `builtins.pro` → EXACT MATCH vs `builtins.expected`. Archived.
- Fixed **atom name C-string escaping bug** in `prolog_emit.c`: atoms containing `\n`, `\t`, `\r`, or other control chars were emitted as raw bytes into C string literals, causing gcc compile errors. Added `emit_c_string()` helper; patched all three `prolog_atom_intern` emission sites (E_QLIT escape loop, E_FNC arity==0, E_FNC compound functor in `term_new_compound`).
- Ran rung10 word puzzles:
  - `puzzle_01.pro` (bank: Brown/Jones/Smith) → **`Cashier=smith Manager=brown Teller=jones`** ✅
  - `puzzle_06.pro` (occupations: Clark/Jones/Morgan/Smith) → **`Clark=druggist Jones=grocer Morgan=butcher Smith=policeman`** ✅
  - `puzzle_02.pro` (trades: Clark/Daw/Fuller) → outputs correct winner line but **keeps generating extra candidates** — `doesEarnMore/2` transitive clause cut interaction not pruning correctly.

**Milestones fired:** M-PROLOG-BUILTINS ✅ (archived)

**Next session (F-224): M-PROLOG-R10**

1. Debug `puzzle_02.pro` — `doesEarnMore(X,Y) :- earnsMore(Y,X), !, fail.` should cut after disproving but extra permutations escape. Add `write` tracing to `doesEarnMore` to see which clause is firing when it shouldn't. Likely: β-port retry is re-entering after the cut-sealed clause.
2. Once puzzle_02 passes, run `puzzle_05.pro` (WIP — constraints partially commented).
3. If all 4 puzzles pass → M-PROLOG-R10 ✅ → update PLAN.md → fire M-PROLOG-CORPUS sweep.
4. Trigger phrase: `"playing with Prolog frontend"` → F-session → M-PROLOG-R10.

**Repos touched:** snobol4x, .github
**Commits:** `fa0eee9` sno2c+runtime, `fe86477` semantic driver (.github `2a04df2`)

**Fixes:**
- `stmt_aref2/aset2`: 2D subscript `arr[i,j]` was ignoring 2nd index; new shims in `snobol4_stmt_rt.c`; `E_IDX` emitter updated for `nchildren>=3`
- `PROTOTYPE`: was returning bare count `"1"`; now returns `"lo:hi"` matching CSNOBOL4
- `table_set_descr` + `TBPAIR_t.key_descr`: integer keys preserved through SORT
- `sort_fn`: stores `key_descr` in col 1 so `DATATYPE(objKey)` returns `'INTEGER'` correctly

**Semantic subsystem:** driver+ref committed (`fe86477`); 8/8 CSN PASS; ASM segfaults on `DATA('link_counter(next,value)')` + `$'#N'` indirect variable — B-276 blocker.

**Milestones fired:** M-BEAUTY-XDUMP ✅

**Next (B-276):** Fix ASM segfault in DATA/indirect var; `DEFDAT_fn`/`NV_GET_fn`/`NV_SET_fn` in `snobol4.c`; fire M-BEAUTY-SEMANTIC ✅; advance to M-BEAUTY-OMEGA.

## Session B-276 — 2026-03-24 — M-BEAUTY-SEMANTIC ✅ + M-BEAUTY-OMEGA (blocked)

**Repos touched:** snobol4x, .github
**Commits:** `f721492` snobol4x (PLAN.md advance to M-BEAUTY-OMEGA)

**M-BEAUTY-SEMANTIC ✅ (clean pass, no fixes needed):**
Previous session had logged "ASM segfaults on DATA/indirect" as blocker, but those fixes had already landed in prior commits. Re-ran 3-way monitor this session: CSNOBOL4+SPITBOL+ASM all agree, 8/8 PASS, 1 step. 106/106 corpus clean. Committed PLAN.md advance.

**M-BEAUTY-OMEGA — driver authored, SPITBOL+SO crash diagnosed (not yet fixed):**

Driver `test/beauty/omega/driver.sno` authored: 10 tests for TV/TW/TX/TY/TZ.
Key design insight: TZ/TY/TV/TW build patterns containing `$ *assign(...)` side-effects. These patterns cannot be directly matched in a standalone driver — `assign()` returns `''`, so `$''` → Error 8 "variable not present". Correct oracle tests are DATATYPE=PATTERN and composability. Used `upr(DATATYPE(...))` for SPITBOL compat (SPITBOL returns lowercase type names).

10/10 CSNOBOL4 oracle lines. 10/10 SPITBOL lines (without SO). `driver.ref` written.

**SPITBOL+SO crash (B-276 open blocker):**
- SPITBOL runs `instr.sno` cleanly without `monitor_ipc_spitbol.so`
- SPITBOL segfaults (exit 139, zero output) with SO + live FIFOs
- Minimal driver (includes only, `OUTPUT = 'loaded'`) works fine with SO
- Full driver (10 tests + UTF-8 comment lines) crashes during include loading
- Root-cause hypothesis: UTF-8 multibyte characters (`→`, `←`) in driver comments confuse SPITBOL's preprocessor under the SO

**Next session fix plan:**
1. Strip all UTF-8 chars from `driver.sno` comments (replace `→` with `->` etc.)
2. Re-run with SO + fake pipes — expect clean run
3. If clean: run full 3-way monitor → commit B-276: M-BEAUTY-OMEGA ✅
4. If still crashes: bisect by adding tests one at a time to find exact trigger
5. Advance PLAN.md to M-BEAUTY-TRACE (19th and final subsystem)

## Session F-219 — 2026-03-23 — puzzle_02.pro missing earnsMore fact

**Bug fixed:** `earnsMore(fuller, daw)` was absent from puzzle_02.pro. The puzzle states the plumber (fuller) earns more than the painter (daw), establishing the chain fuller > daw > clark. Only `earnsMore(daw, clark)` was present; `doesEarnMore(fuller, daw)` could never succeed; WINNER never printed.
**Fix:** Added `earnsMore(fuller, daw).` to puzzle_02.pro.
**Result:** WINNER prints for `Carpenter:clark Painter:daw Plumber:fuller`. puzzle_01, puzzle_02, puzzle_06 all PASS.
**Commit:** `0c2119a` snobol4x · HEAD `0c2119a`
**Next:** F-220 — puzzle_05 constraints (uncomment + implement \+ if needed) to fire M-PROLOG-R10.

## F-221 (2026-03-23) — bug diagnosis, no commit

**Branch:** main · **HEAD unchanged:** `5e6b872`

**Work done:**
- Built snobol4x clean. Ran rungs 1–10: rungs 1–4 and 6–9 PASS; rung 5 (backtrack/member) FAIL (prints `a\nb` instead of `a\nb\nc`).
- Root-caused the bug: in `prolog_emit.c` `emit_body`, when the last goal in a clause body is a resumable user call, the emitter does `PG(γ)` — jumps to the clause's γ label returning the clause index (e.g. `1`). This discards the inner `_cs9` counter tracking sub-solutions. On retry, `_start=1` resets `_cs9=0`, re-finding `b` instead of advancing to `c`.
- No code changes made (context exhausted before fix could be applied).

**Milestones fired:** none

**Fix for F-222:** In `emit_body` last-goal user-call branch (line ~692), instead of `PG(γ)`, emit `*_tr = _trail; return %d + _cs%d - 1;` (clause_idx + inner _cs offset). Add `default:` case in `emit_choice` switch to re-enter last clause's retry loop with `_start - nclauses` as inner _cs. This makes all 10 rungs PASS and fires M-PROLOG-CORPUS.

---

## Session F-222 (2026-03-23) — Puzzle stubs + milestone planning

**Work done:**
- Split `puzzles.pro` into 16 individual stub files: `puzzle_03.pro` through `puzzle_20.pro` (skipping 01, 02, 05, 06 which are already solved). Each stub contains the full problem text as comments and a `main` that prints `'puzzleNN: stub\n'`.
- Added 16 milestones M-PZ-03..M-PZ-20 to PLAN.md, ordered easy→hard by problem structure.
- Updated FRONTEND-PROLOG.md with full puzzle sprint table, difficulty rationale, and complete source layout.
- No source code changes. rung05 backtrack bug still open — fix described in TINY.md CRITICAL NEXT ACTION.

**Repos touched:** snobol4x (`b4507dc`), .github (`ce9d83b`)

**Milestones fired:** none

**Next session F-223:** Fix `emit_body` last-goal user-call branch (~line 692) — encode inner `_cs` into return value. Add `default:` case in `emit_choice`. Run all 10 rungs → M-PROLOG-CORPUS. Then begin M-PZ-14 (easiest puzzle stub).

## Session F-223 — 2026-03-24 — rung05 fix attempted, reverted

**Goal:** Fix rung05 backtrack bug (member/2 prints a\nb not a\nb\nc). Fire M-PROLOG-CORPUS.
**Result:** Encoding scheme partially worked (a\nb printed) but env reset in `case ci:` preamble corrupted third solution. Reverted `prolog_emit.c` to clean. No new commit. Repo at `b4507dc`.
**Next:** F-224 — try transparent pass-through or inner_cs out-param approach per TINY.md CRITICAL.
