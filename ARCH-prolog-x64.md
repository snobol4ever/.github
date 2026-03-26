# ARCH-prolog-x64.md — Prolog × x64: Historical Session Notes

Design notes from early sessions. Operational §NOW → SESSION-prolog-x64.md.

## Session F-212 notes (added 2026-03-22)

### Proebsting PDF — key takeaways

"Simple Translation of Goal-Directed Evaluation" (Todd A. Proebsting, 1996).
Do not re-attach — notes captured here.

The paper's central contribution: every operator in an AST gets four labeled
code chunks (start/resume/fail/succeed = α/β/ω/γ in our notation).
The crucial template for conjunction (`plus(E1, E2)`) is:

```
plus.start   : goto E1.start
plus.resume  : goto E2.resume        ← β port: retry rightmost first
E1.fail      : goto plus.fail        ← ω: all exhausted
E1.succeed   : goto E2.start         ← chain: E1 success starts E2
E2.fail      : goto E1.resume        ← KEY: E2 fail retries E1 (β port)
E2.succeed   : plus.value = E1+E2; goto plus.succeed
```

`E2.fail → E1.resume` is exactly the backtracking wire missing from the
original emit_body. This is what was fixed in the emit_body rewrite.

The `ifstmt(E1,E2,E3)` template (§4.5) uses an **indirect goto** (`gate`
variable) set at runtime — this is the right model for Prolog's `;/2`
disjunction and `->` if-then-else, already implemented in emit_goal.

### What was built in F-212

- `prolog_emit.c` — full C-backend emitter with Byrd box four-port model
- Rung 1 (hello) confirmed running end-to-end
- Rungs 2–4 (facts, unify, arith) output correct but rung 2 only printed
  first solution — backtracking bug identified
- `emit_body` rewritten with proper β-port retry loop for user calls
  (Proebsting plus template). Build/test deferred to F-213.

### emit_body fix summary (for F-213)

Old: all goals chained linearly; fail always jumped to outer omega.
New: `is_user_call()` detects backtrackable goals; `emit_user_call_with_suffix()`
wraps them with a retry loop:

```c
call_β:
    trail_unwind(&_trail, _cm);
    _cr = pl_f_r(args, &_trail, _cs);
    if (_cr < 0) goto omega;
    _cs = _cr + 1;
// suffix goals here — their omega = call_β (retry)
```

This is the direct implementation of E2.fail→E1.resume from Proebsting.

### JCON

JCON (Java Icon) was uploaded but NOT read — context was consumed by
PLAN.md, FRONTEND-PROLOG.md, and prolog_emit.c. Key conceptual note:
JCON's engine uses full unification + backtracking for Icon goal-directed
evaluation — same four-port model. If JCON source is ever examined,
look at how it wires the β port in its conjunction evaluation — likely
directly analogous to the emit_body fix above.

### Session F-214 notes (added 2026-03-22)

**Wrong sandbox — reverted.** F-214 spent context debugging backtracking in `prolog_emit.c` (the C emitter). This was the wrong path. Key findings:

- Rungs 1–4 already PASS via `-pl` C emitter (confirmed this session).
- Rung 5 (backtrack/member) fails because the C emitter's resumable `_r` function loses inner `_cs` state across stack frame returns. Fixing this requires a continuation-passing redesign of `pl_emit.c` — not worth it.
- **The correct path is `-pl -asm`**: wire through `emit_byrd_asm.c` which already has four-port Byrd box stubs (`emit_prolog_choice`, `emit_prolog_clause`, α/β/γ/ω labels). Backtracking is free — β port wires to next clause α, ω port signals exhaustion. No `_cs` state needed.
- The blocker: `driver/main.c` line 144 hardcodes `pl_emit(prog, out)` regardless of `asm_mode`. One-line fix.
- All changes to `prolog_emit.c` were stashed and reverted. Repo is clean at `3ce6673`.

**M-PROLOG-WIRE-ASM — completed (implied by F-217 rungs 1–4 PASS via ASM path)**

1. In `driver/main.c`, replace the hardcoded `pl_emit(prog, out)` with the `asm_mode` branch (call `asm_emit` when `-asm` is set).
2. Link `prolog_atom.c`, `prolog_unify.c`, `prolog_builtin.c` into the ASM binary (add to `Makefile` runtime link or emit inline calls).
3. Test: `sno2c -pl -asm null.pl -o null.s && nasm -f elf64 null.s && ld ... && ./a.out` → exit 0.
4. Then `hello.pl` → M-PROLOG-HELLO fires.
5. Rungs 1–5: Byrd box β port handles backtracking automatically — no C emitter `_cs` hack needed.

---

## Puzzle Corpus — rung10 Sprint Plan (added 2026-03-23)

`puzzles.pro` has been split into individual stub files, one per puzzle.
Each stub contains the full problem text as comments and a `main` that prints `'puzzleNN: stub\n'`.
Milestones are ordered from easiest to hardest based on problem structure:

| ID | File | Puzzle | Status |
|----|------|--------|--------|
| **M-PZ-01** | puzzle_01.pro | Bank positions Brown/Jones/Smith | ✅ real search — swipl PASS |
| **M-PZ-02** | puzzle_02.pro | Clark/Daw/Fuller occupations | ✅ real search — swipl PASS |
| **M-PZ-14** | puzzle_14.pro | Golf scores (Bill/Ed/Tom wives) | ✅ real search — swipl PASS + JVM PASS |
| **M-PZ-17** | puzzle_17.pro | Country Club dance pairings | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-15** | puzzle_15.pro | Vernon/Wilson/Yates offices + secretaries | ✅ real search — swipl PASS |
| **M-PZ-16** | puzzle_16.pro | Train crew relations | ✅ real search — swipl PASS |
| **M-PZ-20** | puzzle_20.pro | Pullman car readers | ✅ real search — 4 valid solutions, swipl PASS (stub was wrong) |
| **M-PZ-13** | puzzle_13.pro | Murder case roles | ✅ real search — swipl PASS |
| **M-PZ-18** | puzzle_18.pro | Shopping day scheduling | ✅ real search — swipl PASS |
| **M-PZ-19** | puzzle_19.pro | Office floors + professions | ✅ real search — swipl PASS |
| **M-PZ-04** | puzzle_04.pro | Milford occupations + salaries | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-05** | puzzle_05.pro | First National Bank chess/proximity | ✅ real search — swipl PASS |
| **M-PZ-06** | puzzle_06.pro | Clark/Jones/Morgan/Smith occupations | ✅ real search — swipl PASS |
| **M-PZ-09** | puzzle_09.pro | Empire Dept Store positions | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-08** | puzzle_08.pro | Dept Store positions (Ames/Brown/Conroy…) | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-11** | puzzle_11.pro | Smith family positions | ✅ real search — swipl PASS; JVM 2L (over-generates) |
| **M-PZ-07** | puzzle_07.pro | Brown/Clark/Jones/Smith professions | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-10** | puzzle_10.pro | Five J-names + last names | ✅ real search — swipl PASS; JVM PASS |
| **M-PZ-03** | puzzle_03.pro | Triple engagement party | ✅ real search — swipl PASS; JVM 20L (over-generates) |
| **M-PZ-12** | puzzle_12.pro | Stillwater High teachers | ✅ real search — swipl PASS |

Each milestone trigger: the puzzle file prints the correct solution and exits 0 via swipl.

### Source layout

```
test/frontend/prolog/corpus/rung10_programs/
    puzzle_01.pro   ✅ solved (bank positions)
    puzzle_02.pro   ✅ solved (trades Clark/Daw/Fuller)
    puzzle_03.pro   ✅ solved (triple engagement party)
    puzzle_04.pro   ✅ solved (Milford occupations)
    puzzle_05.pro   ✅ solved (bank chess Brown/Clark/Jones/Smith)
    puzzle_06.pro   ✅ solved (occupations Clark/Jones/Morgan/Smith)
    puzzle_07.pro   ✅ solved (professions Brown/Clark/Jones/Smith)
    puzzle_08.pro   ✅ solved (dept store Ames/Brown/Conroy…)
    puzzle_09.pro   ✅ solved (Empire dept store)
    puzzle_10.pro   ✅ solved (five J-names)
    puzzle_11.pro   ✅ solved (Smith family)
    puzzle_12.pro   ✅ solved (Stillwater High teachers)
    puzzle_13.pro   ✅ solved (murder case)
    puzzle_14.pro   ✅ solved (golf scores)
    puzzle_15.pro   ✅ solved (Vernon/Wilson/Yates)
    puzzle_16.pro   ✅ solved (train crew)
    puzzle_17.pro   ✅ solved (Country Club dance)
    puzzle_18.pro   ✅ solved (shopping day)
    puzzle_19.pro   ✅ solved (office floors)
    puzzle_20.pro   ✅ solved (Pullman car readers)
    puzzles.pro     source anthology (read-only reference)
```

---

### Recommendation for F-213

1. `cd snobol4x && make -C src` — rebuild with emit_body fix
2. Test rungs 1–5: `./sno2c -pl test/.../rungN.pro -o /tmp/t.c && gcc ... && ./a.out`
3. If rung 5 (backtrack/member) passes, rungs 6–8 likely follow
4. Consider pivot: instead of C backend, target x64 ASM emitter directly
   (emit native NASM α/β/γ/ω labels). Read ARCH.md + BACKEND-X64.md.
   The C path is good for debugging; ASM is what the design spec calls for.
