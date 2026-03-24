# FRONTEND-PROLOG-JVM.md — Prolog → JVM Backend (L3)

Prolog frontend targeting JVM bytecode via Jasmin.
Reuses the existing Prolog IR pipeline (lex → parse → lower) unchanged.
New layer: `prolog_emit_jvm.c` — consumes `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*`
and emits Jasmin `.j` files, assembled by `jasmin.jar`.

**Session trigger phrase:** `"I'm working on Prolog JVM"`
**Session prefix:** `PJ` (e.g. PJ-5, PJ-6, ...)`
**Driver flag:** `snobol4x -pl -jvm foo.pl → foo.j → java -jar jasmin.jar foo.j`
**Oracle:** `snobol4x -pl -asm foo.pl` (ASM emitter, rungs 1–9 known good)
**Design reference:** BACKEND-JVM-PROLOG.md (term encoding, runtime helpers, Jasmin patterns)

*Session state → this file §NOW. Backend reference → BACKEND-JVM-PROLOG.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `main` PJ-6 — Fix2+Fix3b applied; rung05 a,b only — cs encoding cannot reach c; see CRITICAL below | `0fb717c` PJ-6 | M-PJ-BACKTRACK |

### CRITICAL NEXT ACTION (PJ-7)

**Bug:** `member/2` outputs `a
b
` only. `c` not printed.

**What was done in PJ-6 (all committed at `0fb717c`):**
- Fix 1 (PJ-5): removed `istore init_cs_local` from `call_sfail` (prevents outer clause cs clobbering)
- Fix 2 (PJ-6): removed spurious `+1` from `local_cs` update after γ extraction — `local_cs = sub_cs_out` (not `+1`)
- Fix 3b (PJ-6): var init loops in `pj_emit_choice` now only load from JVM arg register when the head position is a pure `E_VART` pointing at that slot; otherwise allocates a fresh unbound var cell. This fixed `a,b` (T in `member(X,[_|T])` was getting pre-loaded with the full list arg).
- Result: `a` and `b` now print correctly.

**Root cause of missing `c` — cs encoding problem:**

The current `γ = base[ci] + sub_cs_out + 1` encoding cannot distinguish the 3rd solution. Trace:
- `cs=0 → clause0 → X=a, γ=1`
- `cs=1 → clause1, init_cs=0, inner cs=0 → clause0 → X=b, inner_γ=1, outer_γ=1+1+1=3`
- `cs=3 → clause1, init_cs=2, inner cs=2 → clause1, inner-inner cs=1 → clause1, inner^3 cs=0 → [] → ω`

For `c`, caller needs `cs=2`:
- `cs=2 → clause1, init_cs=1, inner cs=1 → clause1, inner-inner cs=0 → clause0 → X=c ✓`

But `γ(b)=3`, so the next call is `cs=3` which gives ω. `c` is never tried.

**The fundamental issue:**

The γ encoding `base[ci] + sub_cs_out + 1` makes `b` return `γ=3` but `c` requires `cs=2`. The gap (cs=2 is skipped) means `c` is unreachable.

In ASM, this works because member is called through a **conjunction predicate** (`pl__cm__sl_4_r`) that retries member with **cs=0,1,2,3** sequentially (cs += 1 each retry, not cs = γ). The body ucall β → ω immediately (not retry). The conjunction handles all the retry logic externally.

**The fix — two-part:**

**Part A: β from body ucall → ω (not retry).** In `pj_emit_body`, the `call_sfail` label should go to `lbl_outer_omega` (the predicate's ω port), NOT loop back to `call_try`. The body ucall gets ONE chance.

**Part B: γ formula change.** Currently `γ = base[ci] + sub_cs_out + 1`. Change to `γ = base[ci] + 1` for clause0 (no body ucalls) and `γ = base[ci] + sub_cs_out` for clause1 (so that after `b` where inner returned `γ=1`, outer returns `γ = 1 + 1 = 2` — the cs value that will give `c`).

Actually more precisely: the formula should be `γ = base[ci] + local_cs` where `local_cs` is the CURRENT value of local_cs when we hit the γ port (NOT `sub_cs_out + 1`). After `b`, `local_cs=1` (the γ returned by inner), so `outer_γ = 1+1=2`. Caller uses `cs=2` → gives `c`. After `c`, inner returns `γ=1` again but... wait, this still collides.

**Correct derivation:**

Actually the RIGHT fix matches ASM exactly: **β goes to ω, caller always does cs += 1**.

In the caller (main/0 or outer disjunct), after γ is received, we do `local_cs = returned_γ` (current behavior). But if β goes to ω and γ is never returned when inner fails, then the γ value only comes when there IS a solution. For a 2-clause predicate with list [a,b,c]:

- Main caller: `cs=0` → γ=? After success, `cs = γ`. Then on sfail, `cs += 1`.
  - cs=0 → a, γ=1 → store γ → cs=1 on next call
  - cs=1 → b, γ=? If γ = base[1] + 0 + 1 = 2 → store γ → cs=2 on next call ✓
  - cs=2 → c, γ=? = base[1] + 1 + 1 = 3 → cs=3 on next call
  - cs=3 → ω ✓

For `b`: clause1, init_cs=0. Inner call cs=0 → clause0 → b. Inner β goes to clause1's ω. Clause1 returns γ = base[1] + `sub_cs_out` = 1 + 0 = 1. Wait that's 1 not 2.

**The KEY insight from deeper analysis:** The `sub_cs_out` at the clause1 γ port should be `init_cs` (= the cs we entered with minus base[ci]), NOT what the inner call returned. Because on NEXT entry, caller will provide `cs = γ = base[ci] + init_cs + 1`, and clause1 will compute `init_cs_new = cs - base[ci] = init_cs + 1`, which increments the inner call's cs by 1. This is exactly the "cs += 1" behavior.

So the correct γ formula is: **`γ = base[ci] + init_cs + 1`** (using `init_cs_local`, not `sub_cs_out`).

Currently the code uses `sub_cs_out` at the γ port (which equals the γ returned by the inner call, potentially > init_cs). This is wrong for recursive predicates.

**Implementation:**

In `pj_emit_choice`, at the γ port (around line 1322):
```c
// CHANGE: use init_cs_local instead of sub_cs_out_local
J("    ldc %d
", base[ci]);
J("    iload %d
", init_cs_local);   // ← was sub_cs_out_local
J("    iadd
");
J("    iconst_1
");
J("    iadd
");
```

AND in `pj_emit_body`, `call_sfail` should go to `lbl_outer_omega` instead of `call_try`.

**Verify:**
- member(X,[a,b,c]): cs=0→a(γ=1), cs=1→b(γ=1+0+1=2), cs=2→c(γ=1+1+1=3), cs=3→ω ✓
- Expected output: `a
b
c
`

```bash
# Bootstrap PJ-7:
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read §NOW. Start at CRITICAL NEXT ACTION.
# Test:
./sno2c -pl -jvm test/frontend/prolog/corpus/rung05_backtrack/backtrack.pro -o /tmp/bt.j
java -jar src/backend/jvm/jasmin.jar /tmp/bt.j -d /tmp/ && timeout 5 java -cp /tmp Backtrack
# Expected: a
b
c
  — currently: a
b

```

**Token:** `TOKEN_SEE_LON`


## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ❌ |
| **M-PJ-LISTS** | Rung 6: `append/3`, `length/2`, `reverse/2` | ❌ |
| **M-PJ-CUT** | Rung 7: `differ/N`, closed-world `!, fail` | ❌ |
| **M-PJ-RECUR** | Rung 8: `fibonacci/2`, `factorial/2` | ❌ |
| **M-PJ-BUILTINS** | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | ❌ |
| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus PASS | ❌ |

---

## Session Bootstrap (every PJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

---

*FRONTEND-PROLOG-JVM.md = L3. ~3KB sprint content max. Archive ✅ milestones to MILESTONE_ARCHIVE.md on session end.*
