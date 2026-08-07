# FINDING-2026-08-07-CLAUDE-PL-TAG3-STALE-LITERAL-SINK2-SINK3-WRITE-ARMS-AND-BENCH-9-TO-11.md

**Session:** PL-ZFRAME-RESTORE s4 (Sonnet, 2026-08-07)
**SCRIP HEAD at finding:** `6a87662b` (session start) → fix committed this session

## BUILD FIX: emit.cpp:2096 premature comment-close

`71bda272` (M-1-FIX-3) left a premature `*/` inside a long one-liner comment at `emit.cpp:2096`, ejecting ~860 characters of prose outside the comment block. The C++ compiler saw a bare `'` character as an unterminated char literal (`error: missing terminating ' character` at column 1200). Fixed by collapsing the two comment paragraphs back into one (remove the spurious `*/` between them). Build was broken at HEAD; now clean.

## ROOT CAUSE: TAG-3 stale literals in SINK-2/SINK-3 write arms

**File:** `src/templates/bb_call_fn.cpp` — `sink_kid()` and the SINK-3 WRITE ARM inside `sink_unify_lst_str()`.

**Background:** The TAG-3 commit (`03cecd87`) renumbered the Prolog descriptor tags from old sequential integers to the current hex layout: `DT_PLVAR` moved from `13` → `0x48 = 72`; `DT_PLREF` moved from `14` → `0x50 = 80`. All comparison sites correctly use `(long)DT_PLVAR` and `(long)DT_PLREF` symbolically. But two **write** sites retained the old literal integers:

1. `sink_kid()` unbound arm (lines 138/143): wrote `(long)13` as the `DT_PLVAR` tag — both for the fresh PLVAR kid cell seed and for the source-cell forwarding bind.
2. SINK-3 WRITE ARM (line 334): wrote `(long)14` as the `DT_PLREF` tag when binding the subject cell to the newly built cons cell.

**Effect:** When `$unify_lst(Subject, H, T)` runs in WRITE mode (subject unbound — the `[H|R]` output-construction case in clause heads like `app([H|T], L, [H|R])`):
- The subject cell was written with `v=14` (= `DT_SNUL` range, not recognized as list) instead of `DT_PLREF=80`.
- The H forwarding pointer was written with `v=13` (unrecognized) instead of `DT_PLVAR=72`.
- All subsequent `sink_deref` / `plw_cell_deref` calls test for `DT_PLVAR=72` and `DT_PLREF=80` — neither matched 13 or 14. The bindings were silently invisible.
- `write` on the caller's output variable printed an empty/wrong value or failed silently (rc=1).

**Why it passed READ mode:** The READ arm (`c->v == DT_PLREF && c->slen == dot_sl`) only reads the existing cell — it never writes a tag. The stale literals only corrupt the WRITE (unbound-subject) arm. So clauses that only DESTRUCTURE lists (matching a bound input) were unaffected.

**Diagnosis path:**
- Bisected to `step([H|_], [H|[]]) :- atom_checker(hello)` — output [1] printed blank, rc=0.
- Narrowed: `step([H|_], Out) :- T=[], Out=[H]` passed (body-only build); `aux([_|_]); step([H|T], [H|R]) :- aux(T), R=[]` failed. HEAD-pattern match + output-build + body call = failure.
- IR dump confirmed n22=`$unify_lst(arg0,H,_)` (READ) then n26=`$unify_lst(arg1,H,nil)` (WRITE). Read arm worked; write arm silently dropped the binding.
- Traced through `sink_unify_lst_str` SINK-3 WRITE ARM: the `(long)13`/`(long)14` literals identified as the root cause vs `DT_PLVAR=72`/`DT_PLREF=80`.

**Fix:** Replace `(long)13` → `(long)DT_PLVAR` (two sites in `sink_kid`) and `(long)14` → `(long)DT_PLREF` (one site in SINK-3 WRITE ARM). No logic change.

## WATERMARKS

**Bench correctness (before fix):** 9/22 m3&m4 green.
**Bench correctness (after fix):** 11/22 m3&m4 green. Recovered: `nrev`, `qsort`.
**SN4 byte-identity:** 18/21 demo programs MATCH (3 pre-existing DIFFs: `claws5.sno`, `json.sno`, `pattern_test.sno` — confirmed pre-existing at HEAD before this session's changes, not introduced here).
**Smoke:** 4/5 (unchanged — `clause` still fails, backtracking/disjunction class).

## OPEN: recursion-depth cliff at N≈27

`nreverse([1..30])` fails (rc=1, silent); `nreverse([1..25])` passes. This is a C stack depth issue — O(n²) C frames per Prolog call, one frame per `rt_proc_call_open_det` trampoline crossing. The bench harness requests `ulimit -s unlimited` but the sandbox may not honor it, and the zframe per-activation overhead compounds at depth. Not a tag bug — the 10/15/20/25 element cases all pass. Belongs to PL-FR-3/4/5 (per-activation frames, C-frame-free recursion spine) as the root fix; the immediate next session should diagnose the exact limit and whether `ulimit -s unlimited` is effective in this environment before declaring it a PL-FR-N prerequisite.
