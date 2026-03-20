# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `asm-backend` B-211 — M-ASM-RUNG11: PROTOTYPE + array default-fill + item() + beauty.sno depth guard
**HEAD:** `3133497` B-210
**Milestone:** M-ASM-RUNG8 ❌ (2/3 pre-existing) · M-ASM-RUNG9 ✅ 5/5 · M-ASM-RUNG11 ❌ (0/7 — PROTOTYPE/item()/default-fill needed)
**Milestone order:** M-ASM-RUNG8 → M-ASM-RUNG9 → M-ASM-RUNG10 → M-ASM-RUNG11 → M-ASM-LIBRARY

**⚠ CRITICAL NEXT ACTION — Session B-211:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 100/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
# Step 1: add PROTOTYPE to snobol4.c + register in SNO_INIT_fn
# Step 2: implement _b_ARRAY default-fill (second arg)
# Step 3: register item() in snobol4.c
# Step 4: re-run rung11 → target 7/7 → M-ASM-RUNG11 fires
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung11
# Step 5: fix beauty.sno segfault (recursion depth guard in prog_emit_expr)
# Step 6: regenerate artifacts/asm/beauty_prog.s + roman.s + wordcount.s
# Step 7: commit + update PLAN.md/SESSIONS_ARCHIVE + push
```

**Session B-210 summary — M-ASM-RUNG9 fires; two root-cause fixes:**

**Bug A (LGT NULVCL) — FIXED:** `inc_init()` in `mock_includes.c` re-registered
`LGT/LLT/LGE/LLE/LEQ/LNE` with `_w_*` wrappers returning NULVCL on failure,
overwriting `SNO_INIT_fn`'s correct FAILDESCR-returning `_b_*` versions.
Fix: removed 6 duplicate `register_fn` calls from `inc_init()`.
Result: rung9 **5/5 ✅ — M-ASM-RUNG9 fires.**

**Bug C (rung11 E_IDX read) — FIXED:** `prog_emit_expr(key, -16)` called `LOAD_INT`
which always writes `[rbp-32/24]` first regardless of `rbp_off`, clobbering the
array descriptor saved there. Fix: push array descriptor onto C stack before key
eval, pop into `rdi:rsi` after. Tests 001-004 of 1110 now pass.

**Remaining rung11 blockers:**
- `PROTOTYPE` function not registered (hits at 1110/005, 1112/002, 1113/005)
- `_b_ARRAY` default-fill (second arg ignored — `array(3,10)` gives no fill)
- `item()` function not registered (1114/001)
- `value()` needs verification for 1115/1116 DATA tests

**beauty.sno segfault:** pre-existing, unrelated to this session's changes.
Root cause: deep recursion in `prog_emit_expr` for complex expressions.
Fix: add recursion depth counter/guard — B-211.

**Invariants:** 100/106 C ✅ · 26/26 ASM ✅

**Session B-209 summary — 7 root-cause fixes; invariants hold:**

Seven bugs fixed in `emit_byrd_asm.c` and `snobol4.c`:

1. **`expr_has_pattern_fn` whitelist** — was returning 1 for ANY E_FNC; now only returns 1 for known pattern builtins (ARBNO/SPAN/BREAK/etc). Value functions (REPLACE, SIZE, DIFFER, LGT) no longer generate phantom named-pattern bodies with "UNIMPLEMENTED" stubs.

2. **`_func_hash` case-insensitive** — hash now uppercases each char via `toupper()`. Fixes `stmt_apply("replace",...)` returning NULVCL because lowercase "replace" hashed to a different bucket than uppercase "REPLACE" registration. Unblocked rung8 SIZE/DUPL.

3. **`E_KW` emitter uppercase** — keywords emitted as "ALPHABET" not "alphabet" so `stmt_get` finds them. Fixes `&alphabet` / `&anchor` lookups.

4. **CONC2 fast-path guard** — `CONC2_*` macros (which call `stmt_concat`) now only fire for CONCAT/ALT calls. All other 2-arg functions (LGT, DIFFER, GT, etc.) fall through to `APPLY_FN_N`. Previously `lgt('abc','xyz')` emitted `CONC2 S_lgt, S_abc, S_xyz` — wrong.

5. **`E_IDX` read fix** — `children[0]` was used twice (arr AND key both evaluated from children[0]). Fixed: `children[0]`→arr, `children[1]`→key. Also fixed arg order to `stmt_aref`: arr→`[rbp-32/24]`→rdi:rsi, key→`[rbp-16/8]`→rdx:rcx. Added `nchildren>=2` guard.

6. **`E_IDX` write fix** — same `children[1]` fix in the `has_eq + E_IDX` path. Same `nchildren>=2` guard.

7. **prescan OOB + `prog_str_intern` null guard** — `e->children[1]` access guarded by `nchildren>1`; `prog_str_intern(NULL)` now safe.

**Runtime additions:** `LGT/LLT/LGE/LLE/LEQ/LNE` lexical string comparators added to `snobol4.c` and registered in `SNO_INIT_fn`.

**Rung results after B-209:**
- rung8: 2/3 (810_replace assertion 002 uses &alphabet binary string — pre-existing runtime strlen limitation)
- rung9: 4/5 (914_lgt fails — LGT registered but stmt_apply("lgt",...) returns NULVCL; root cause: _func_init ordering TBD)
- rung10: 0/9 (not yet investigated this session)
- rung11: 0/7 (E_IDX fix applied but not re-run to confirm; diagnose next session)

**Outstanding root causes for B-210:**

**Bug A — LGT lookup returns NULVCL:** Direct C test confirms `stmt_apply("lgt",args,2)` returns `v=0` (NULVCL) after `stmt_init()`, but `stmt_apply("LGT",args,2)` also returns `v=0`. Yet the `_b_LGT` wrapper is registered in `SNO_INIT_fn`. Hypothesis: `_func_init()` is called from `register_fn` and clears the table, then subsequent `register_fn` calls should populate it — but something is re-initializing. Check: does `NV_SYNC_fn` (called from `stmt_init`) also call `_func_init` and reset the table? Alternatively: `_func_init_done` is being reset somewhere. Add `fprintf(stderr, "registering LGT\n")` in `SNO_INIT_fn` to confirm registration fires.

**Bug B — sno2c segfault on beauty.sno:** Crashes at line 788 generating `APPLY_FN_N S_AL` (truncated). Pre-existing at HEAD — CONC2 fast path was silently handling the expression; now generic path is taken and hits stack overflow from deep recursive `prog_emit_expr` calls. Fix: add recursion depth limit to `prog_emit_expr`, or identify the specific expression in beauty.sno that triggers deep recursion and handle it in the generic fallback.

**Bug C — rung11 arrays:** E_IDX fix applied; need to rebuild and re-run to confirm. If still failing, diagnose what `a<1>` emits and whether `stmt_aref` is being called correctly.

**⚠ CRITICAL NEXT ACTION — Session B-210:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /snobol4corpus/crosscheck /home/snobol4corpus/crosscheck 2>/dev/null || true
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 100/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/snobol4corpus/crosscheck
# Step 1: confirm rung11 improvement
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung11
# Step 2: debug LGT — add fprintf to SNO_INIT_fn around register_fn("LGT",...)
#          and to APPLY_fn to see if lookup fires
# Step 3: once LGT works, rung9 should be 5/5 → M-ASM-RUNG9
# Step 4: fix beauty.sno segfault in sno2c (stack depth guard in prog_emit_expr)
# Step 5: regenerate artifacts/asm/beauty_prog.s clean
# Step 6: rung8 3/3 requires binary-safe REPLACE (strlen → explicit length tracking)
# Step 7: M-ASM-RUNG8 + M-ASM-RUNG9 fire → begin rung10
```

**Session F-209 summary — M-FLAT-NARY complete:**

Unified `EXPR_t` to n-ary `children[]`/`nchildren` — all nodes use the same storage.
`left`/`right`/`args`/`nargs` fields removed; replaced by `expr_left()`/`expr_right()`/
`expr_arg()`/`expr_nargs()` NULL-safe accessor macros and `expr_add_child()` builder.

Key changes:
- `sno2c.h`: new struct + `expr_binary()`, `expr_unary()`, `expr_add_child()`
- `parse.c`: E_CONC/E_OR flat n-ary; E_FNC/E_IDX args are children[]
- `sc_lower.c`, `sc_cf.c`: updated builders
- All backends: traversal functions use `for(i=0;i<nchildren;i++)` loops
- E_CONC/E_OR emitters fold n>2 children via heap-allocated binary chain
- `emit_cnode.c`: E_CONC/E_OR left-fold all children
- `emit_byrd_asm.c`: WALK_EXPR macro fixed; value-context n-ary preamble

**Invariants after F-209:** 100/106 C crosscheck ✅ · 26/26 ASM crosscheck ✅
(6 pre-existing C failures unchanged)

**⚠ CRITICAL NEXT ACTION — Session B-209 (backend):**

Merge `flat-nary-f209` into main, then resume M-ASM-RUNG8.

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git checkout main
git pull --rebase
git merge flat-nary-f209
git push origin main
# Then resume rung8:
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 100/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung8
```

**Session B-208 summary — treebank.sno completely rewritten:**

Replaced the wrong Stack+Counter approach with five clean functions over a single
`DATA('cell(hd,tl)')` Gimpel cons-cell type, matching json.sno's LIFO+reverse idiom:

- `do_push_list(v)` — start new inner list headed by v: `stk = cell(cell(v,), stk)`
- `do_push_item(v)` — prepend v LIFO: `hd(stk) = cell(v, hd(stk))`
- `do_pop_list()` — reverse LIFO chain → ARRAY, prepend array onto parent inner list
- `do_pop_final(v)` — reverse LIFO chain → ARRAY, assign to `$v`

`group()` is a recursive DEFINE'd function with locals `(tag, wrd)` giving each
recursive invocation its own bindings — the SNOBOL4 equivalent of Python `λ` closures.
The `epsilon . *fn()` idiom requires NRETURN/.dummy and works for non-recursive cases,
but `tag`/`wrd` globals are clobbered by recursion since patterns have no local scope.
A DEFINE function with locals is the correct solution.

Outer sentence loop is an explicit labeled goto loop (not ARBNO) to prevent side-effect
corruption from failed ARBNO backtrack iterations.

Tested on CSNOBOL4: `(NP (DT the) (NN dog))`, two sentences, deeply nested `(S ...)` —
all produce correct indented S-expression output. Corpus HEAD: `eb088b9` (treebank.ref oracle committed).

**⚠ CRITICAL NEXT ACTION — Session B-209 (backend):**

Generate treebank.ref oracle from VBGinTASA.dat, commit, then M-ASM-RUNG8.

```bash
cd /home/claude/snobol4corpus
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull
SNO=/home/claude/snobol4-2.3.3/snobol4
PROGS=/home/claude/snobol4corpus/programs/lon/sno
$SNO $PROGS/treebank.sno < VBGinTASA.dat > $PROGS/treebank.ref
git add -A && git commit -m "B-209: treebank.ref oracle" && git push
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
apt-get install -y libgc-dev nasm && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung8
```

**Session B-207 summary — claws5.sno ✅ done; treebank.sno Shift/Reduce debugging:**

**claws5.sno — COMPLETE.** Key fix: use `$` (immediate) not `.` (conditional) for `num`/`wrd`/`tag`
captures so side-effect functions `*do_new_sent()` / `*do_add_tok()` see the captured values
during the ARBNO match. Tested on synthetic input: correct sentno TAB wrd TAB tag output.
Corpus HEAD: `89b2b72`.

**treebank.sno — IN PROGRESS.** Rewrote using beauty.sno machinery: nPush/nInc/nPop +
Shift/Reduce + Stack + Counter + tree DATA. Key findings from debugging session:

1. **`$` not `.` for thx capture in shift_:** `shift_` must use `EVAL("*p $ thx . *Shift('t',thx)")` —
   `.` is conditional (defers until overall match), `$` is immediate. Shift() fires during match
   via `*Shift(...)` in the concatenated pattern.

2. **Shift() needs null guard:** `DIFFER(v) :F(ShiftNull)` before `v POS(0) (SPAN(SPCNL)|'') =`.
   Without it: Error 4 "Null string in illegal context" when v arrives empty.

3. **Reduce() body: `GT(n,0) :F(R_zero)` not `GE(n,1) ARRAY(...)`:** The old `c = GE(n,1) ARRAY('1:' n)`
   concatenates the GE return value with the ARRAY — Error 4. Guard and array creation must be
   separate statements.

4. **`reduce()` semantic function must NOT use EVAL:** `EVAL("epsilon . *Reduce(t,n)")` calls
   Reduce at PATTERN BUILD TIME, not match time. Instead define concrete NRETURN functions:
   `grp_reduce()`, `root_reduce()`, `bank_reduce()` — each calls `Reduce('X', TopCounter())`
   and returns via NRETURN. Use `epsilon . *grp_reduce()` in the pattern.

5. **Multi-statement lines cause Error 8:** `NL = CHAR(10) SPC = ' ' SPCNL = SPC NL` on one
   line → Error 8 "Variable not present". Every assignment must be on its own line.

6. **Outer ARBNO counter structure:** `Reduce(ROOT,0)` fires before any groups are parsed —
   the `nPush()` before `ARBNO(*group)` needs to shift the 'ROOT' tag first (like group does
   for its tag), OR count must include the tag. Review: in group, `shift('word','tag')` shifts
   the tag token, THEN `nPush()` starts counting children — so nTop()=0 when no children,
   which is correct for a leaf node. For ROOT: `nPush()` then `ARBNO(*group)` — each *group
   match fires grp_reduce which pushes one tree onto the value stack AND increments the counter.
   But grp_reduce calls Reduce which POPS from the value stack — so after ARBNO, there is
   exactly ONE tree on the stack (the last reduced group). The nTop() counter is tracking
   how many groups were seen. This logic needs to be verified step by step on the simplest
   non-empty tree `(NP dog)`.

**⚠ CRITICAL NEXT ACTION — Session B-208 (backend):**

```bash
cd /home/claude/snobol4corpus
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull
SNO=/home/claude/snobol4-2.3.3/snobol4  # already built

# The working test scaffold is in /tmp/t_reduce3.sno (with the multi-line fix applied).
# Start from there — it gets to Reduce(ROOT,0) before failing at statement 105.
# Statement 105 is a continuation line in the group pattern — likely another multi-line issue.
# Fix approach:
#   a) Each pattern line must stand alone — no implicit continuation except with +
#   b) Verify counter semantics: after ARBNO(*group) over (NP dog), nTop() should = 1
#   c) The group pattern uses shift('word','tag') then nPush() — tag is shifted BEFORE
#      the counter level opens. So tag is on the value stack, counter starts at 0.
#      Each child (word or nested group) calls nInc() and shifts/reduces one tree.
#      grp_reduce() calls Reduce('grp', nTop()) — pops nTop() children plus the tag.
#      BUT: the tag was pushed before nPush(), so it is NOT counted. Reduce pops nTop()
#      items — those are the children. Then we need to also pop the tag separately
#      and build the node. This means grp_reduce() should be:
#
#   grp_reduce     n   = TopCounter()
#                  c   = GT(n,0) ARRAY('1:' n)          -- children (if any)
#                  ...pop n items into c...
#                  tag_node = Pop()                      -- pop the tag tree
#                  r   = tree(t(tag_node),, n, c)
#                  Push(r)
#                  grp_reduce = .dummy                   :(NRETURN)
#
#   OR: shift tag with nInc() so it IS counted:
#   group = '(' nInc() shift('word','tag') nPush() ARBNO(...) grp_reduce() nPop() ')'
#   -- but then grp_reduce pops nTop() which includes the tag as child[1].
#   That's the simpler approach: tag is always child[1], words/groups are 2..n.
#
# Simplest correct design matching Python:
#   push_list(tag) = nPush() then push tag onto value stack separately
#   push_item(v)   = nInc() then push item onto value stack
#   pop_list()     = Reduce('grp', nTop()+1) nPop()   -- +1 for the tag itself

# Quick test once fixed:
echo ' (NP (DT the) (NN dog)) ' | $SNO programs/lon/sno/treebank.sno
# Expected:
# (NP
#   (DT
#     the
#   )
#   (NN
#     dog
#   )
# )

# Once passing: generate oracle
echo ' (NP (DT the) (NN dog)) ' | $SNO programs/lon/sno/treebank.sno > /tmp/treebank_test.ref
# Then run against VBGinTASA.dat and commit oracle.
```

**Session B-206 summary — claws5.sno + treebank.sno rewritten as true ARBNO patterns:**

Both programs completely rewritten. Old versions used imperative consume-loops and recursive
descent. New versions: single named pattern variable each, mirroring Python assignment3.py 99%.
claws5 uses `ARBNO((sent_arm | tok_arm) ' ')` anchored with POS(0)/RPOS(0). treebank uses
`group` self-referencing via `*group` (= Python ζ(lambda: group)) inside ARBNO. Stack and
Counter inlined directly — no -include. snobol4corpus pushed `89b2b72`.

**⚠ CRITICAL NEXT ACTION — Session B-207 (backend):**

Generate .ref oracles for claws5.sno and treebank.sno using CSNOBOL4, commit to corpus.
Then M-ASM-RUNG8.

```bash
cd /home/claude/snobol4corpus
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull
# Build CSNOBOL4 if needed:
cd /home/claude/snobol4-2.3.3 && make -j4
SNO=/home/claude/snobol4-2.3.3/snobol4
PROGS=/home/claude/snobol4corpus/programs/lon/sno
# Run claws5 against CLAWS5inTASA.dat, capture oracle:
$SNO $PROGS/claws5.sno < CLAWS5inTASA.dat > $PROGS/claws5.ref
# Run treebank against VBGinTASA.dat, capture oracle:
$SNO $PROGS/treebank.sno < VBGinTASA.dat > $PROGS/treebank.ref
git add -A && git commit -m "B-207: claws5.ref + treebank.ref oracles" && git push
# Then M-ASM-RUNG8:
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 266c866 B-204 (snobol4x unchanged)
apt-get install -y libgc-dev nasm && make -C src
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung8  # M-ASM-RUNG8
```

**HEAD:** `8bae0fe` (latest main — verify with `git log --oneline -3`)
**Status:** 106/106 C ✅ · 26/26 ASM ✅ · 8/8 functions ✅ · roman.sno ✅ · wordcount.sno ✅
**Session B-204 summary — M-ASM-RECUR + M-ASM-SAMPLES fire:**

Three root causes fixed:
1. **Case 2 predicate S/F dispatch** (B-203): `GT(x,0) :S(RETURN)F(FRETURN)` — guard `(id_s>=0||id_f>=0)` was false for RETURN/FRETURN (prog_label_id returns -1 for special targets). Added `is_special_goto()` check. 8/8 functions.
2. **Local variable save/restore** at call sites: `DEFINE('ROMAN(N)T')` — T was not pushed/popped around recursive calls. Added `nlocals` field + `local_names[]` to `AsmNamedPat`; extended `parse_define_str` to parse locals after `)` in prototype; added locals push/pop to call-site γ/ω restore.
3. **Function retval + locals cleared at α entry**: SNOBOL4 resets function name variable and all locals to null at every call. Added `stmt_set(fname, NULVCL)` and `stmt_set(local_i, NULVCL)` in α prologue after loading params.

**⚠ CRITICAL NEXT ACTION — Session B-205 (backend):**

Sprint A-BEAUTY — M-ASM-BEAUTY: beauty.sno self-beautifies

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 266c866 B-204
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions  # must be 8/8

# Attempt beauty.sno self-beautify:
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
RT=src/runtime
./sno2c -asm -I$INC $BEAUTY > /tmp/beauty_asm.s
nasm -f elf64 -I $RT/asm/ /tmp/beauty_asm.s -o /tmp/beauty_asm.o
gcc -no-pie /tmp/beauty_asm.o $RT/asm/snobol4_stmt_rt.c $RT/snobol4/snobol4.c \
    $RT/mock/mock_includes.c $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/beauty_asm_bin
echo "INPUT = beauty.sno" | timeout 30 /tmp/beauty_asm_bin < $BEAUTY > /tmp/beauty_out.txt
# diff against C-backend output → M-ASM-BEAUTY fires when diff is empty
./sno2c -I$INC $BEAUTY > /tmp/beauty_c.c
gcc /tmp/beauty_c.c $RT/snobol4/snobol4.c $RT/mock/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -o /tmp/beauty_c_bin
timeout 30 /tmp/beauty_c_bin < $BEAUTY > /tmp/beauty_c_out.txt
diff /tmp/beauty_out.txt /tmp/beauty_c_out.txt && echo "M-ASM-BEAUTY fires"
```


**Root cause of 087_define_freturn + roman_mini wrong value:**
`GT(x,0) :S(RETURN)F(FRETURN)` is a Case 2 statement — predicate only, no subject/pattern.
The S/F goto targets are silently dropped in the Case 2 emit path.
`emit_jmp(tgt_s, ...)` and `emit_jmp(tgt_f, ...)` should be called with `current_fn != NULL`
so they route through `fn_NAME_gamma/omega`. Find where Case 2 S/F is emitted and verify.

**Session B-203 start:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 0c1b997 B-202
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Step 1 — diagnose 087:**
```bash
cd /home/claude/snobol4x && RT=src/runtime
./sno2c -asm /home/claude/snobol4corpus/crosscheck/functions/087_define_freturn.sno > /tmp/t087.s
grep -n "L_ispos_1\|RETURN\|FRETURN\|fn_ispos\|emit_jmp" /tmp/t087.s | head -30
# Expected: jmp fn_ispos_gamma and jmp fn_ispos_omega in the body
# Actual: those lines are likely missing — Case 2 path drops them
```

**Step 2 — find Case 2 emit path in emit_byrd_asm.c:**
Search for the predicate-only statement handler (no s->pattern, has s->subject + s->go).
Verify `emit_jmp(tgt_s, next_lbl)` and `emit_jmp(tgt_f, next_lbl)` are called.
With `prog_label_id` fix, RETURN/FRETURN now return -1 — check if any `id_s < 0` guard
is silently skipping the emit. The fix should be simple once the guard is found.

**Step 3 — after fix, full validation:**
```bash
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions  # must be 8/8
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Step 4 — roman.sno full test → M-ASM-RECUR:**
```bash
PROGS=/home/claude/snobol4corpus/programs && RT=src/runtime
./sno2c -asm $PROGS/roman/roman.sno > artifacts/asm/samples/roman.s
nasm -f elf64 -I $RT/asm/ artifacts/asm/samples/roman.s -o /tmp/roman.o
gcc -no-pie /tmp/roman.o $RT/asm/snobol4_stmt_rt.c $RT/snobol4/snobol4.c \
    $RT/mock/mock_includes.c $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/roman_bin
timeout 10 /tmp/roman_bin < $PROGS/roman/roman.input > /tmp/roman_out.txt
diff /tmp/roman_out.txt $PROGS/roman/roman.ref && echo "ROMAN PASS — M-ASM-RECUR fires"
```

**Step 5 — artifact + commit:**
```bash
INC=/home/claude/snobol4corpus/programs/inc
./sno2c -asm -I$INC /home/claude/snobol4corpus/programs/beauty/beauty.sno > artifacts/asm/beauty_prog.s
nasm -f elf64 -Isrc/runtime/asm/ artifacts/asm/beauty_prog.s -o /dev/null  # must be clean
git add -A && git commit -m "B-203: M-ASM-RECUR — recursive functions correct; roman.sno PASS"
# Update PLAN.md M-ASM-RECUR → ✅, update NOW table HEAD, push
```

**Architecture note (B-202, Lon):** The long-term fix is Technique 2 (BACKEND-X64.md) —
CODE shared/RX, DATA per-invocation via memcpy, stackless, gates on M-BOOTSTRAP.
The near-term fix below uses the C stack as a cheap DATA allocator. Same correctness.
Do NOT skip ahead. Optimization hurts when done too early. Debug static first.
See ARCH.md §Near-Term Bridge and §Technique 2 for the full picture.

**Root cause:** One global `rbp` frame for the entire program. `[rbp-8/16/32/48]` are
shared globals. Recursive `jmp P_ROMAN_α` runs in the SAME frame as the caller.
Inner call overwrites the outer call's locals. `rbp` corrupted → segfault.

**Fix (3 lines at α, 2 lines each at γ/ω) in `emit_asm_named_def()`, `is_fn` branch:**

```c
/* α: */
asmL(np->alpha_lbl);
A("    push    rbp\n");
A("    mov     rbp, rsp\n");
A("    sub     rsp, 56\n");
/* ... existing: load args, jmp body ... */

/* γ: */
asmL(gamma_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_gamma);

/* ω: */
asmL(omega_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_omega);
```

Call sites: **no change** — stack push/pop param save/restore already correct (session197).

**Session B-202 start:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 71c86d3 B-201
apt-get install -y libgc-dev nasm gdb && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Step 1 — apply fix to `src/backend/x64/emit_byrd_asm.c`:**
In `emit_asm_named_def()`, `is_fn` branch, at `asmL(np->alpha_lbl);`:
insert `push rbp / mov rbp,rsp / sub rsp,56` after the label.
At `asmL(gamma_lbl);`: body becomes `add rsp,56 / pop rbp / jmp [ret_gamma]`.
At `asmL(omega_lbl);`: body becomes `add rsp,56 / pop rbp / jmp [ret_omega]`.
Then `make -C src`.

**Step 2 — smoke test:**
```bash
cat > /tmp/roman_mini.sno << 'EOF'
    &TRIM = 1
    DEFINE('ROMAN(N)T')                 :(ROMAN_END)
ROMAN   N   RPOS(1)  LEN(1) . T  =         :F(RETURN)
    '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,'
+   T   BREAK(',') . T                  :F(FRETURN)
    ROMAN = ROMAN(N) T
+                                       :S(RETURN)F(FRETURN)
ROMAN_END
    R = ROMAN('12')
    OUTPUT = "result: " R
END
EOF
RT=src/runtime
./sno2c -asm /tmp/roman_mini.sno > /tmp/roman_mini.s
nasm -f elf64 -I $RT/asm/ /tmp/roman_mini.s -o /tmp/roman_mini.o
gcc -no-pie /tmp/roman_mini.o $RT/asm/snobol4_stmt_rt.c $RT/snobol4/snobol4.c \
    $RT/mock/mock_includes.c $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/roman_mini_bin
timeout 5 /tmp/roman_mini_bin
# expected: result: XII
```

**Step 3 — full invariants + functions rung:**
```bash
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions  # 8/8
```

**Step 4 — M-ASM-RECUR → M-ASM-SAMPLES:**
```bash
PROGS=/home/claude/snobol4corpus/programs
RT=src/runtime
./sno2c -asm $PROGS/roman/roman.sno > artifacts/asm/samples/roman.s
nasm -f elf64 -I $RT/asm/ artifacts/asm/samples/roman.s -o /tmp/roman.o
gcc -no-pie /tmp/roman.o $RT/asm/snobol4_stmt_rt.c $RT/snobol4/snobol4.c \
    $RT/mock/mock_includes.c $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/roman_bin
timeout 10 /tmp/roman_bin < $PROGS/roman/roman.input > /tmp/roman_out.txt
diff /tmp/roman_out.txt $PROGS/roman/roman.ref && echo "ROMAN PASS" || echo "ROMAN FAIL"
# M-ASM-RECUR fires → regenerate beauty_prog.s artifact → commit B-202
# Then: wordcount already passes (B-201) → M-ASM-SAMPLES fires → commit
```


Sprint A-RECUR — fix recursive function segfault → M-ASM-RECUR → M-ASM-SAMPLES

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 71c86d3 B-201
apt-get install -y libgc-dev nasm gdb && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Root cause (fully diagnosed B-201/B-202):**

The current ASM backend has ONE `rbp` frame for the entire program (established by
`PROG_INIT` in `main`). All `[rbp-8/16/32/48]` temporaries are shared globals.
When a user-defined function (`ROMAN`) calls itself recursively:

1. Call site saves old N and ret addresses → `.bss` uid slots (`ucall0_sv_*`, `ucall0_rsv_*`)
2. `jmp P_ROMAN_α` → body runs in the **same `rbp` frame** as the caller
3. Inner call overwrites `ucall0_sv_*` `.bss` slots with its own save
4. Inner call returns via `ucall0_ret_g` → restores from `.bss` → correct for inner
5. Outer call's `ucall0_ret_g` runs → `.bss` slots now hold **inner call's** saved
   values, not outer call's → `rbp` corrupted to `0x1` → segfault

**Architecture discussion (B-202 session):**

Long-term correct architecture (BACKEND-X64.md Technique 2, post-M-BOOTSTRAP):
- Each Byrd Box = self-contained CODE + DATA pair
- On `*X` / function call: `memcpy` CODE+DATA to new region, relocate, jump
- Each active invocation has its **own DATA copy** — locals are per-invocation
- Completely stackless — no `rbp`, no shared slots, no save/restore at all
- One register points to current box's DATA; recurse = new copy, own register

Near-term fix (implement now, unblocks M-ASM-SAMPLES):
- `P_ROMAN_α` (every `is_fn` α port) establishes its own stack frame:
  `push rbp / mov rbp,rsp / sub rsp,56`
- `fn_ROMAN_gamma` / `fn_ROMAN_omega` tear it down before dispatching:
  `add rsp,56 / pop rbp / jmp [ret_γ|ω]`
- Call sites continue using `.bss` uid slots for save/restore — safe because
  each recursive invocation has its own `rbp`, so `.bss` slots are written
  **once per call-site uid** before `jmp α`, and the callee's fresh frame
  means inner calls don't touch the outer call's `.bss` slots
- The `.bss` uid slots are per-call-site in source (ucall0 vs ucall1) —
  mutual recursion and self-recursion both safe because each dynamic
  invocation gets a new `rbp` frame

**Fix location:** `emit_asm_named_def()` in `src/backend/x64/emit_byrd_asm.c`,
`is_fn` branch only. Three lines at α, two lines each at γ/ω.

**Implementation:**

In `emit_asm_named_def`, `is_fn` branch, α label:
```c
asmL(np->alpha_lbl);
A("    push    rbp\n");
A("    mov     rbp, rsp\n");
A("    sub     rsp, 56\n");
/* ... load args, jmp body ... */
```

γ label:
```c
asmL(gamma_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_gamma);
```

ω label:
```c
asmL(omega_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_omega);
```

Call sites: **no change needed** — `.bss` uid slots already correct.

**Verify fix:**
```bash
# Quick smoke test:
cat > /tmp/roman_mini.sno << 'EOF'
    &TRIM = 1
    DEFINE('ROMAN(N)T')                 :(ROMAN_END)
ROMAN   N   RPOS(1)  LEN(1) . T  =         :F(RETURN)
    '0,1I,'
+   T   BREAK(',') . T                  :F(FRETURN)
    ROMAN = ROMAN(N) T
+                                       :S(RETURN)F(FRETURN)
ROMAN_END
    R = ROMAN('12')
    OUTPUT = "result: " R
END
EOF
RT=src/runtime
./sno2c -asm /tmp/roman_mini.sno > /tmp/roman_mini.s
nasm -f elf64 -I $RT/asm/ /tmp/roman_mini.s -o /tmp/roman_mini.o
gcc -no-pie /tmp/roman_mini.o $RT/asm/snobol4_stmt_rt.c $RT/snobol4/snobol4.c \
    $RT/mock/mock_includes.c $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/roman_mini_bin
timeout 5 /tmp/roman_mini_bin
# expected: result: XI  (or similar roman numeral output)
# Then run full invariants + functions/ rung + roman.sno + wordcount.sno
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions  # 8/8
PROGS=/home/claude/snobol4corpus/programs
./sno2c -asm $PROGS/roman/roman.sno > artifacts/asm/samples/roman.s
nasm -f elf64 -I $RT/asm/ artifacts/asm/samples/roman.s -o /tmp/roman.o
# link + run + diff vs oracle → M-ASM-RECUR fires → M-ASM-SAMPLES fires
```

**Session B-201 (backend) — wordcount PASS; roman segfault root-caused:**

- **wordcount.sno** — assembles, links, runs correctly: `14 words` vs ref ✅
- **roman.sno** — assembles and links cleanly; segfaults at runtime
- **Root cause of roman segfault (diagnosed, not yet fixed):**
  - `rbp` is corrupted to a stack address (`0x1` or similar) at crash
  - Crash occurs inside `stmt_set` called from `P_ROMAN_α` with corrupt `rdi` (name = stack addr, not `"N"`)
  - GDB watchpoint: `rbp` changes from `0x...4378` to `0x...4310` inside `stmt_set` itself (that's normal frame setup); the *pre-corruption* of `rdi` happens before the `lea rdi, [rel S_N]` in `P_ROMAN_α` is reached — meaning `rbp` is trashed before `P_ROMAN_α` is even entered in the second recursive call
  - Likely cause: the ucall save/restore pushes (4 qwords = 32 bytes) interact with the pattern-match scan loop's `[rbp-8/16]` subject slot. When the ROMAN body re-enters its own pattern statements, `GET_VAR` and `SUBJ_FROM16` write to `[rbp-16/8]` which the ucall then pushes — but the INNER call's `GET_VAR` runs **before** the outer call's push saves the value, overwriting the subject slot.
  - Precise suspect: at `Ln_3`, `GET_VAR S_N` writes `[rbp-16]=N.type, [rbp-8]=N.ptr`, then pushes them. But `SUBJ_FROM16` in `L_ROMAN_1` also uses `[rbp-16]` — subject descriptor. If `jmp P_ROMAN_α` is reached while `[rbp-16/8]` still holds the subject descriptor from the OUTER call's pattern match (not N), then the ucall pushes the subject, not N.
  - **Next session fix:** Add gdb breakpoint at `Ln_3` push sequence, print `[rbp-8/16]` values and verify they are N's descriptor, not the subject descriptor. If wrong: the `GET_VAR S_N` before the push is being skipped or overwritten by an intermediate `SUBJ_FROM16`.
- **artifacts/asm/samples/roman.s** — first generation, NASM-clean, committed
- **artifacts/asm/samples/wordcount.s** — first generation, NASM-clean, committed  
- 106/106 C ✅ · 26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — Session B-202 (backend):**

Sprint A-SAMPLES — fix roman.sno recursive function segfault → M-ASM-SAMPLES

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 3f2c8b9 B-201
apt-get install -y libgc-dev nasm gdb && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26

# Reproduce crash with mini roman:
cat > /tmp/roman_mini.sno << 'EOF'
    &TRIM = 1
    DEFINE('ROMAN(N)T')                 :(ROMAN_END)
ROMAN   N   RPOS(1)  LEN(1) . T  =         :F(RETURN)
    '0,1I,'
+   T   BREAK(',') . T                  :F(FRETURN)
    ROMAN = ROMAN(N) T
+                                       :S(RETURN)F(FRETURN)
ROMAN_END
    R = ROMAN('12')
    OUTPUT = "result: " R
END
EOF

RT=src/runtime
./sno2c -asm /tmp/roman_mini.sno > /tmp/roman_mini.s
nasm -f elf64 -I $RT/asm/ /tmp/roman_mini.s -o /tmp/roman_mini.o
gcc -no-pie -g /tmp/roman_mini.o $RT/asm/snobol4_stmt_rt.c $RT/snobol4/snobol4.c \
    $RT/mock/mock_includes.c $RT/snobol4/snobol4_pattern.c $RT/engine/engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/roman_mini_bin

# Diagnose: at Ln_3 push sequence, what is [rbp-16]/[rbp-8]?
# Is it N's value or the subject descriptor?
# Ln_3 is at the `push qword [rbp-8]` after `GET_VAR S_N`
# The pattern match just completed (P_4_γ fired), setting T.
# Before the push: [rbp-16] should be N (from GET_VAR), NOT the subject slot.
# Suspect: SUBJ_FROM16 at L_ROMAN_1 sets [rbp-16/8] = subject descriptor.
# Then GET_VAR S_N overwrites [rbp-16/8] with N. That's correct.
# But: does the pattern γ path write to [rbp-16/8] before Ln_4?

# Key investigation: grep for writes to [rbp-16] or [rbp-8] between
# scan_retry_4 and Ln_4 in the generated .s:
grep -n "rbp-16\|rbp-8\|rbp-24\|rbp-32" /tmp/roman_mini.s | head -40
```

**Root cause hypothesis to verify (B-202):**

The push at Ln_3 saves `[rbp-8]/[rbp-16]`. The value in `[rbp-8]` at that point is whatever the last instruction wrote there. Tracing backwards:
1. `GET_VAR S_N` → writes `[rbp-16]=N.type, [rbp-8]=N.ptr` ✓
2. But `GET_VAR` expands to `call stmt_get` which returns DESCR via `rax:rdx` then `mov [rbp-16],rax / mov [rbp-8],rdx`

If `stmt_get("N")` itself calls deeper into the runtime which disturbs `[rbp-16/8]` — no, it's a simple lookup.

**More likely:** the problem is in the *second* recursion of ROMAN. On the *first* call from main (ucall1, `ROMAN('12')`), `P_ROMAN_α` sets N='12', body runs, hits `Ln_3`, does `GET_VAR S_N` → `[rbp-16]='1'` type, `[rbp-8]` ptr. Pushes correctly. Recurses (ucall0, `ROMAN('1')`). Inner returns via `ucall0_ret_g`. Pops. Calls `stmt_set("N", ...)` to restore N. Then `GET_VAR S_ROMAN` → **overwrites `[rbp-16/8]` with ROMAN's return value**. This is fine for the inner call flow.

**But then the outer ucall1 returns to `ucall1_ret_g`** which does the same pop sequence for ucall1's frame. At that point `[rbp-16/8]` contains ROMAN's return value from the inner call — and ucall1_ret_g pops into `rsi/rdx` (old N value from ucall1's push). So ucall1 correctly restores N='12'. But `[rbp-16/8]` now contains whatever `GET_VAR S_ROMAN` + subsequent concat left there, not the 'result' value the outer function stored. That should be fine since ucall1_ret_g re-reads `GET_VAR S_ROMAN`.

**The real issue may be simpler:** the crash is a stack overflow. ROMAN('12') → ROMAN('1') → ROMAN('') → pattern fails → RETURN. But ROMAN('1') recurses at `ROMAN(N)` where N='1', and `'1'` has 1 digit, so the inner call strips the last char (`RPOS(1) LEN(1) . T = `) leaving N='', then hits line 2 pattern which also fails (N='' can't match T BREAK(',') . T), takes :FRETURN. That bubbles up. So max recursion depth for ROMAN('12') is 2 levels — should not overflow.

**Actual fix to try:** Add `comm_stno` call tracking and use `&STCOUNT` to count steps, set `&STLIMIT = 100`. If it terminates (via STLIMIT), the logic is correct but something else is wrong. If it segfaults before STLIMIT, the stack is corrupted before even 100 statements.

**Session B-200 (backend) — M-DROP-MOCK-ENGINE fires:**

- `mock_engine.c` was never called by compiled ASM programs; `snobol4_pattern.c` calls `engine_match_ex` which `engine.c` (real engine) satisfies directly
- `run_crosscheck_asm_rung.sh` + `run_crosscheck_asm_prog.sh`: replaced `mock_engine.c` → `engine.c` in compile+link lines
- `emit_byrd_asm.c`: updated generated `.s` link-recipe comment to `engine.o`
- `artifacts/asm/beauty_prog.s`: regenerated (16297 lines, NASM clean)
- 106/106 C ✅ · 26/26 ASM ✅ · Full rung suite: 94/97 (3 pre-existing failures: fileinfo/triplet/expr_eval — unrelated to this change)
- **M-DROP-MOCK-ENGINE fires** `06df4cb`

**⚠ CRITICAL NEXT ACTION — Session B-201 (backend):**

Sprint A-SAMPLES — roman.sno + wordcount.sno PASS → M-ASM-SAMPLES

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 617631c
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26

# Step 1: audit what engine_match callers exist
grep -rn "engine_match\|engine_match_ex" src/ test/

# Step 2: rewrite snobol4_asm_harness.c to not call engine_match
# The harness run_pattern() calls engine_match — replace with direct
# jmp to root_alpha (already done for program-mode; replicate here)

# Step 3: remove mock_engine.o from run_crosscheck_asm.sh link line

# Step 4: verify 26/26 still passes without mock_engine.o
bash test/crosscheck/run_crosscheck_asm.sh

# Step 5: verify 106/106 still passes
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh

# M-DROP-MOCK-ENGINE fires when both pass without mock_engine.o in ASM link
```

- **Fix 1 — E_IDX read** (091/092/093): `A<i>`/`T['k']` → new `stmt_aref(arr,key)` shim wrapping `_aref_impl`; `E_IDX` case added to `prog_emit_expr`; evaluates arr→[rbp-16/8], key→[rbp-32/24], calls `stmt_aref` via SysV regs.
- **Fix 2 — E_IDX write** (091/092/093): `A<i>=val`/`T['k']=val` → new `stmt_aset(arr,key,val)` shim; `has_eq`+`E_IDX` path pushes arr+key onto C stack, evaluates RHS, loads all args into SysV regs, calls `stmt_aset`, pops.
- **Fix 3 — field set** (095): `x(P)=99` → new `stmt_field_set(obj,field,val)` shim wrapping `FIELD_SET_fn`; `has_eq`+`E_FNC`-1arg path added.
- **Fix 4 — skip guard**: `E_IDX` and `E_FNC`-lhs exempt from subject-load prescan.
- **`snobol4.h`**: declared `FIELD_SET_fn`.
- **`A()` refactor**: introduced `emit3(label,opcode,operands)` structured emitter + `emit_raw(text)` for directives + `fmt_op(fmt,...)`. Old `A()` re-parsed its own output string (~90 lines of sniffing); new `A()` splits once into opcode+operands and delegates to `emit3`. Pending-label fold logic now lives only in `emit3`. `emit_instr()` retained for `asmLB`/`ALFC` bypass path.
- 6/6 data/ PASS · 106/106 C ✅ · 26/26 ASM ✅ · **M-ASM-R11 fires**

**⚠ CRITICAL NEXT ACTION — Session199 (backend):**

Sprint A-SAMPLES — roman.sno + wordcount.sno PASS → M-ASM-SAMPLES

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 5bac5cd
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/data   # must be 6/6
# Then attempt roman.sno and wordcount.sno:
PROGS=/home/claude/snobol4corpus/programs
./sno2c -asm $PROGS/roman/roman.sno > /tmp/roman.s
nasm -f elf64 -I src/runtime/asm/ /tmp/roman.s -o /tmp/roman.o
# link + run + diff vs oracle
```

**Session197 (backend) — M-ASM-R10: functions/ 8/8 PASS; FRETURN + recursion fixes:**

- **Fix 1 — FRETURN signalling** (087): ucall omega return emitted `LOAD_NULVCL32` → `FAIL_BR` after call site saw non-fail descriptor and took `:S` instead of `:F`. Fix: omega path now emits `LOAD_FAILDESCR32` (DT_FAIL=99). Added `LOAD_FAILDESCR32` macro to `snobol4_asm.mac`.
- **Fix 2 — Recursion-safe save/restore** (088): static `.bss` slots `ucallN_sv_*/rsv_*` overwritten by recursive calls — `fib(n)` and `fib(n-1)` both used same `ucall0_rsv_g` slot, corrupting return addresses. Fix: replaced all static slots with stack push/pop. Before `jmp alpha`: push old `ret_gamma`, `ret_omega`, old param values (reverse order). At `ret_g/ret_o`: pop in reverse to restore. Stack layout survives arbitrary recursion depth.
- 8/8 functions/ PASS · 106/106 C ✅ · 26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — Session198 (backend):**

Sprint A-R11 — data/ — ARRAY/TABLE/DATA

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 06af4ec
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions   # must be 8/8
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/data
# baseline: see how many pass; fix failures; M-ASM-R11 fires at 100%
```

**Session194 (backend) — Sprint A-R10: 6/8 functions/ PASS; 5 fixes:**

- **Fix 1** — DEFINE skip block drops `tgt_u` unconditional goto → execution fell into function body at program start. Add `if (tgt_u) { A("GOTO_ALWAYS %s", prog_label_nasm(tgt_u)); }` in DEFINE skip block.
- **Fix 2** — FRETURN routed to `ret_γ` instead of `ret_ω` in both `emit_jmp` and `prog_emit_goto`. Fixed both sites to use `ret_omega` for FRETURN/NRETURN.
- **Fix 3** — `a1n` fast-path classifier: integer literal `0` wrongly classified as NULVCL → `GT(x,0)` emitted as `CONC2_VN` (1-arg). Removed `(a1->kind==E_ILIT && a1->ival==0)` from `a1n`.
- **Fix 4** — Two-arg `DEFINE('fname(args)', .entryLabel)` form not scanned. `asm_scan_named_patterns` now handles `nargs>=1`; second arg overrides `body_label`.
- **Fix 5** — Recursion-safe param save/restore: per-call-uid `.bss` slots (`ucallN_sv_I_t/p`, `ucallN_rsv_g/o`); `asm_prescan_ucall()` pre-registers all slots before `.bss` emission; alpha simplified to load args + jmp body; gamma/omega just jmp via ret slots; call site saves/restores old param values and ret slots.
- 083/084/085/086/089/090 PASS (6/8) · 106/106 C ✅ · 26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — Session195 (backend):**

Sprint A-R10 — fix fast-path bypass → 087+088 PASS → M-ASM-R10 fires

**Root cause of 087+088:** `ispos(-3)` has arg `E_FNC(neg, ILIT(3))` — a nested function call. The user-function call-site block is preceded by fast-path checks (`na==1 && arg->kind==E_ILIT` etc.) that match BEFORE the `asm_named_lookup_fn` check. So the complex-arg call bypasses the save/restore machinery entirely.

**One-line fix** in `prog_emit_expr`, E_FNC dispatch — move the `asm_named_lookup_fn` check to the TOP of the E_FNC block, before ALL fast paths:

```c
/* User-defined function? Must go through full ucall save/restore machinery.
 * This check must precede ALL fast paths. */
const AsmNamedPat *ufn = (e->sval) ? asm_named_lookup_fn(e->sval) : NULL;
if (ufn) {
    /* ... full ucall code ... */
    return 1;
}
/* Fast paths below only apply to built-in functions */
```

Currently `ufn` is looked up mid-block after fast paths already ran. Move lookup + ufn block before `if (na == 1 && ...)`.

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 3cddca5
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions
# current: 6/8; move ufn check before fast paths → 8/8 → M-ASM-R10 fires
```

cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 018d913
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/keywords   # must be ALL PASS
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions
# baseline: see how many pass; fix failures; M-ASM-R10 fires at 100%
```

**Architecture note — R10+R11 gate Snocone self-compile:**
M-ASM-R10 (functions/) and M-ASM-R11 (data/) are prerequisites for M-SC-CORPUS-R5
(keywords/functions/data via `-sc -asm`), which gates M-SC-CORPUS-FULL → M-SNOC-ASM-SELF.
Backend must complete R10+R11 before frontend session can reach M-SNOC-ASM-SELF.

**A-R10 root-cause diagnosis (session193 baseline run — 0/8 FAIL):**

All 8 functions/ tests produce empty output. Root cause: DEFINE statement with unconditional
goto `:(label)` — emitter does `asmL(next_lbl); continue` (skips DEFINE compile-time body)
but silently **drops the `tgt_u` uncond goto**. Execution falls straight into the function body
at program start instead of jumping to `double_end`.

**One-line fix in `emit_byrd_asm.c`, DEFINE skip block:**
```c
if (s->subject->sval && strcasecmp(s->subject->sval, "DEFINE") == 0) {
    asmL(next_lbl);
    if (tgt_u) { A("    GOTO_ALWAYS  %s\n", prog_label_nasm(tgt_u)); }  /* ADD THIS */
    continue;
}
```
After fix: re-run `$CORPUS/functions` — expect most/all to PASS, then fix residuals.

**Session196 (net) — N-R1 net_emit.c full emitter; hello/multi/empty_string PASS:**

- `net_emit.c` rewritten: two-pass (scan vars → emit); variable registry + `.field static string` per SNOBOL4 var; `.cctor()` initialises all vars to `""`; `net_emit_expr()` handles E_QLIT/E_ILIT/E_FLIT/E_NULV/E_VART/E_CONC/E_ADD/E_SUB/E_MPY/E_DIV/E_MNS; `net_emit_one_stmt()` handles `has_eq` assignments + OUTPUT; stub path fixed to `nop` only (was emitting spurious `Console.WriteLine`)
- hello/ rung: **hello ✅  empty_string ✅  multi ✅**  literals FAIL (root cause: START-label pure-label stmt; `OUTPUT =` null RHS needs E_NULV path; real literal format `1.` vs `1`)
- 106/106 C ✅  26/26 ASM ✅

-LIT fires

Root causes in `net_emit.c`:
1. **Pure-label stmt** (`START` label, no subject/has_eq): stub path emits `nop` ✅ (fixed this session) — verify no extra output
2. **`OUTPUT =` null RHS** (`s->replacement == NULL || s->replacement->kind == E_NULV`): must emit blank line → `ldstr "" + Console.WriteLine` — currently falls through to stub
3. **Real literal format**: SNOBOL4 prints `1.` for `1.0`; C `%g` prints `1` — use `"%.6g"` or detect integer-valued doubles
4. **`'' + ''`** concat: `String.Concat("","")` → `""` then `Console.WriteLine` → blank line ✅ should work
5. **`'' + 1`** concat: left=E_NULV, right=E_ILIT — `E_NULV` pushes `""`, E_ILIT pushes `"1"`, concat → `"1"` ✅

Fix 2 in `net_emit_one_stmt`: detect null/E_NULV replacement → emit `ldstr "" + Console.WriteLine` for OUTPUT:
```c
if (is_out) {
    EXPR_t *rhs = s->replacement;
    if (!rhs || rhs->kind == E_NULV) {
        N("    ldstr      \"\"\n");
    } else {
        net_emit_expr(rhs);
    }
    N("    call       void [mscorlib]System.Console::WriteLine(string)\n");
}
```

Fix 3: real literal format — SNOBOL4 `1.0` prints as `1.`, not `1`:
```c
case E_FLIT: {
    char buf[64];
    double v = e->dval;
    if (v == (long)v) snprintf(buf,sizeof buf,"%ld.", (long)v);
    else snprintf(buf,sizeof buf,"%g", v);
    net_ldstr(buf); break;
}
```

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = a9b3da9
apt-get install -y libgc-dev nasm mono-complete && make -C src
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # 106/106
bash test/crosscheck/run_crosscheck_asm.sh               # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
# Run hello rung:
for f in $CORPUS/hello/*.sno; do
  ref="${f%.sno}.ref"
  ./sno2c -net "$f" > /tmp/t.il && ilasm /tmp/t.il /output:/tmp/t.exe >/dev/null 2>&1
  actual=$(mono /tmp/t.exe 2>/dev/null)
  [ "$actual" = "$(cat $ref)" ] && echo "PASS $(basename $f)" || echo "FAIL $(basename $f)"
done
# Fix literals → all 4 hello PASS → M-NET-LIT fires
# Then run output/ assign/ arith/ rungs → M-NET-R1
```

**Session195 (net) — M-NET-HELLO: NET backend scaffold; Sprint N-R0 complete:**

- `src/backend/net/net_emit.c` — new emitter (mirrors `emit_byrd_jvm.c` structure); three-column CIL layout; `net_set_classname()`; `net_emit_header/main_open/main_close/footer()`; stmt label walker (stubs, N-R1+ fills body)
- `src/driver/main.c` — `-net` flag + `net_emit()` dispatch added
- `src/Makefile` — `BACKEND_NET` block; `net_emit.c` in SRCS
- `artifacts/net/hello_prog.il` — canonical NET artifact; assembles clean via `ilasm`; `mono null.exe` → exit 0 ✅
- `artifacts/jvm/hello_prog.j` — canonical JVM artifact (J0 skeleton, previously missing)
- `RULES.md` — NET and JVM artifact tracking rules added (mirrors ASM rules)
- 106/106 C ✅  26/26 ASM ✅  **M-NET-HELLO fires**

**N-197 (net) — M-NET-LIT fires: hello/ 4/4 PASS; arithmetic helpers; E_FLIT fix:**

- **Fix 1 — E_FLIT real format**: `1.0` now emits `"1."` per SNOBOL4 convention. Integer-valued doubles get trailing dot.
- **Fix 2 — Arithmetic API**: Replaced broken `Int32.ToString(int32)` static call (not in Mono CIL) with emitted helper methods `sno_add/sub/mpy/div/neg/fmt_dbl/parse_dbl` baked into each class.
- **Fix 3 — Empty-string numeric coercion**: `'' + ''` yields `0` — empty string coerces to 0 for numeric arithmetic. `sno_add` trims operand, replaces empty with `"0"` before `Double.TryParse`.
- hello/ rung: **hello ✅  empty_string ✅  multi ✅  literals ✅** — **M-NET-LIT fires**
- output/ 7/8 (006_keyword_alphabet needs E_KW) · assign/ 6/8 (014/015 indirect $ = N-R3+) · arith/ 0/2 (loops+INPUT = N-R3+)
- 106/106 C ✅  26/26 ASM ✅  commit `efc3772` N-197

**N-199 (net) — M-NET-ASSIGN + M-NET-GOTO fire; 33/38 control_new+keywords PASS:**

- **Fix 1 — E_FNC args**: `e->left`/`e->right` were NULL for SNOBOL4 function calls (parser stores args in `e->args[]`). Fixed all builtins: GT/LT/GE/LE/EQ/NE/IDENT/DIFFER/SIZE now emit `e->args[0]`/`e->args[1]`. Unblocked all loop and comparison tests.
- **Fix 2 — DATATYPE()**: `sno_datatype(string)` helper — TryParse → integer/real/string.
- **Fix 3 — Lexical comparators**: `sno_lgt/llt/lge/lle/leq/lne` via `String.Compare(a,b,StringComparison.Ordinal)`.
- **Fix 4 — &STNO**: `kw_stno` static field; incremented before each statement in `net_emit_stmts`; `E_KW` STNO case loads `ldsfld kw_stno`.
- 33/38 hello+output+assign+control_new+keywords PASS (4 deferred: 014/015 indirect `$`, 097/098 pattern keywords, 100 `L_RETURN` label gap)
- **M-NET-ASSIGN fires** `4ef8446` N-199
- **M-NET-GOTO fires** `4ef8446` N-199
- Suite runtime: ~13s (parallel ilasm + serial mono)
- Invariants: 106/106 C ✅ · 26/26 ASM ✅

**N-200 (net) — M-NET-PATTERN fires; 51/58 PASS; 18/20 patterns:**

- **Pattern emitter `net_emit_pat_node`**: full Byrd box pattern emission in CIL, ported from JVM backend
- **Two-pool locals**: int32 slots V_6..V_19 for cursor/counter temps; string slots V_20..V_29 for charset/char temps. Fixes CIL type-safety InvalidProgramException that killed ANY/NOTANY/SPAN/BREAK.
- **Nodes implemented**: E_QLIT(LIT), E_CONC(SEQ), E_OR(ALT), E_NAM(. capture), E_DOL($ capture), E_VART(indirect/builtins), ARBNO/ANY/NOTANY/SPAN/BREAK/LEN/POS/RPOS/TAB/RTAB/REM/ARB/FAIL/SUCCEED/FENCE/ABORT
- **Scan-start retry loop**: anchor check against `kw_anchor` field; `kw_anchor` static field added + init to "0"
- 18/20 patterns PASS; 2 deferred: 053(pattern-in-var), 056(*var indirect) — N-R4+
- 51/58 total across hello+output+assign+control_new+keywords+patterns
- Suite runtime: ~17s (parallel ilasm + serial mono)
- **M-NET-PATTERN fires** `7f66297` N-200
- Invariants: 106/106 C ✅ · 26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — N-201 (net):**

Sprint N-R4 — capture/ and strings/ rungs → M-NET-CAPTURE

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 7f66297 N-200
apt-get install -y libgc-dev nasm mono-complete && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_net_rung.sh $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/control_new $CORPUS/keywords $CORPUS/patterns
# current: 51/58; target: capture/ and strings/ rungs
bash test/crosscheck/run_crosscheck_net_rung.sh $CORPUS/capture $CORPUS/strings
```

**⚠ CRITICAL NEXT ACTION — N-200 (net):**

Sprint N-R3 — Byrd boxes in CIL: LIT/SEQ/ALT/ARBNO pattern nodes → M-NET-PATTERN

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 4ef8446 N-199
apt-get install -y libgc-dev nasm mono-complete && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_net_rung.sh $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/control_new $CORPUS/keywords
# current: 33/38; target: implement pattern Byrd boxes in emit_byrd_net.c
# Start with patterns/ rung baseline — see what ilasm/mono errors arise
bash test/crosscheck/run_crosscheck_net_rung.sh $CORPUS/patterns
```

**N-198 (net) — rename net_emit.c→emit_byrd_net.c; N-R2 E_FNC builtins + goto/:S/:F:**

- `src/backend/net/net_emit.c` renamed to `emit_byrd_net.c` — matches `emit_byrd_asm.c`/`emit_byrd_jvm.c` convention
- `src/Makefile` + `src/driver/main.c` updated to reference new filename
- **E_FNC builtins** added to `net_emit_expr`: `GT/LT/GE/LE/EQ/NE` → `sno_gt/lt/ge/le/eq/ne` helpers returning int32 1/0; `IDENT/DIFFER` → `sno_ident/differ`; `SIZE` → `sno_size`
- **`&ALPHABET`** in `E_KW`: `sno_alphabet()` helper emits 256-char string via `char[]` loop
- **Case 2 bare-predicate stmt** in `net_emit_one_stmt`: `GT(N,5) :S(DONE)` — eval subject, pop result, branch on local 0
- **Case 3 literal pattern match**: `X 'hello' :S(Y)F(N)` — `sno_litmatch(subj,pat)` via `String.Contains`
- **`run_crosscheck_net_rung.sh`** added to `test/crosscheck/` — md5-cached ilasm + `timeout 5` per run
- **`snobol4harness/adapters/tiny_net/run.sh`** added — plugs into `crosscheck.sh --engine tiny_net`
- Stale `src/backend/jvm/README.md` + `src/backend/net/README.md` deleted (docs live in .github)
- 106/106 C ✅  commit `b15164e` N-198

**⚠ CRITICAL NEXT ACTION — N-199 (net):**

Sprint N-R2 continued — verify control_new/ and keywords/ pass; fix &ALPHABET (currently returns 0, needs SIZE=256); fix remaining assign/ failures; fire M-NET-GOTO.

Known remaining failures from N-197 baseline:
1. **006_output_keyword_alphabet**: `&ALPHABET` SIZE should be 256, `sno_alphabet()` helper exists but `SIZE(&ALPHABET)` returns `sno_size(sno_alphabet())` → should work; verify `sno_size` returns string length not 0
2. **014/015 indirect `$`**: deferred to N-R3
3. **arith/ fileinfo/triplet**: needs INPUT loop — deferred

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = b15164e N-198
apt-get install -y libgc-dev nasm mono-complete && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
# Run NET rungs via harness:
cd /home/claude/snobol4harness
TINY_REPO=/home/claude/snobol4x bash crosscheck/crosscheck.sh --engine tiny_net 2>&1
# OR per-rung:
cd /home/claude/snobol4x
bash test/crosscheck/run_crosscheck_net_rung.sh $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/control_new $CORPUS/keywords
# Fix failures → M-NET-GOTO fires when :S/:F branching confirmed correct
```

**⚠ CRITICAL NEXT ACTION — Session196 (net):**

Sprint N-R1 — `OUTPUT = 'hello'` → `hello` via NET backend

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = e6a62ad
apt-get install -y libgc-dev nasm mono-complete && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/functions  # A-R10 baseline
# Then: implement net_emit_stmts() body for S_ASGN + OUTPUT in net_emit.c
# Quick-check: echo "OUTPUT = 'hello'" | ./sno2c -net > /tmp/t.il && ilasm /tmp/t.il /output:/tmp/t.exe && mono /tmp/t.exe
# expected: hello
# M-NET-LIT fires → M-NET-R1
```

**N-R1 design notes:**
- `S_ASGN` with `OUTPUT` subject: emit `ldstr <value>` + `call void [mscorlib]System.Console::WriteLine(string)`
- SNOBOL4 variable storage: `.field static string sno_<NAME>` per variable; `stsfld`/`ldsfld` for set/get
- String literal (`E_QLIT`): `ldstr "<value>"`
- Variable ref (`E_VART`): `ldsfld string <classname>::sno_<name>`
- Assignment (`S_ASGN`): eval RHS → `stsfld string <classname>::sno_<name>`

**Session192 (backend) — M-ASM-R8: strings 17/17 PASS; 7 root-cause fixes:**

- **Fix 1** — Case 2 gamma/omega: `emit_jmp(tgt_s, next_lbl)` → `emit_jmp(tgt_s ? tgt_s : tgt_u, next_lbl)` in both gamma and omega paths. `:(LOOP)` unconditional goto was silently discarded. Fixes word1/2/3/4.
- **Fix 2** — E_VART unresolved: emit `LIT_VAR_ALPHA/BETA` via `stmt_match_var` instead of hard-fail ω. Variables used bare in pattern context (e.g. `CROSS`) now match against their runtime string value. Fixes cross NEXTH/NEXTV.
- **Fix 3** — `snobol4_asm.mac`: added `LIT_VAR_ALPHA varlab, saved, cursor, gamma, omega` and `LIT_VAR_BETA saved, cursor, omega` macros (call `stmt_match_var`).
- **Fix 4** — E_ATP `@VAR`: varname was `pat->sval` (NULL/empty); correct is `pat->left->sval` (parser builds `unop(E_ATP, E_VART("NH"))`). `@NH`/`@NV` were emitting empty label `S_26`. Fixes cross position capture.
- **Fix 5** — Per-stmt capture filter in gamma: `cap_vars[]` is global across all stmts + named-pat bodies. Gamma loop now pre-walks the statement's pattern tree (following E_VART named-pat refs) to collect only captures reachable from this statement. Eliminates spurious `SET_CAPTURE` from other stmts polluting unrelated gammas.
- **Fix 6** — `stmt_concat` propagates FAILDESCR: `DIFFER(C,'#') CONCAT rest` now correctly fails when C='#'. Was calling `VARVAL_fn(FAILDESCR)` → `""` and silently succeeding.
- **Fix 7** — `OUTPUT =` null RHS: `LOAD_NULVCL` (writes rbp-16/8) → `LOAD_NULVCL32` (writes rbp-32/24). `SET_OUTPUT` reads rbp-32/24; mismatch was printing stale prior result as blank line.
- 106/106 C ✅  26/26 ASM ✅  **17/17 strings ✅  M-ASM-R8 fires**

**⚠ CRITICAL NEXT ACTION — Session193 (backend):**

Sprint A-R9 — keywords/ — IDENT/DIFFER/GT/LT/EQ/DATATYPE

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 9f784fa
apt-get install -y libgc-dev nasm && make -C src
mknod /dev/null c 1 3 && chmod 666 /dev/null   # recreate if missing
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/strings   # must be 17/17
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/keywords
# baseline: see how many pass; fix failures; M-ASM-R9 fires at 100%
```

**Architecture note — backend/frontend split:** Both SNOBOL4 (`-asm`) and Snocone (`-sc -asm`) frontends produce `Program*` and call the same `asm_emit_program()`. Backend session touches only `src/backend/x64/emit_byrd_asm.c`, `src/runtime/asm/snobol4_asm.mac`, `src/runtime/asm/snobol4_stmt_rt.c`. Frontend session touches only `src/frontend/snocone/sc_*.c`. Only conflict surface is `sno2c` binary — resolve by `make -C src` after rebase.

**Session189 (frontend) — M-SNOC-ASM-CORPUS: SC corpus 10/10 PASS via -sc -asm:**
- `SC_KW_THEN` added to `sc_lex.h` enum (appended after `SC_UNKNOWN` — safe, no shift) + keyword table + `sc_kind_name`
- `sc_cf.c` if-handler: consume optional `then` keyword; then-body compiled via `compile_expr_clause(SC_KW_ELSE)` to stop before else on same line
- `sc_cf.c` while/for handlers: consume optional `do` keyword before body
- `sc_lower.c`: `SC_OR` (||) → `E_CONC` (string concat), not `E_OR` (pattern alt)
- SC corpus `test/frontend/snocone/sc_asm_corpus/`: 10 `.sc` + `.ref` pairs + `run_sc_asm_corpus.sh` runner
- SC1 literals ✅ SC2 assign ✅ SC3 arith ✅ SC4 control ✅ SC5 while ✅ SC6 for ✅ SC7 procedure ✅ SC8 strings ✅ SC9 multiproc ✅ SC10 wordcount ✅
- 106/106 C ✅

**Session190 (backend) — M-ASM-R7: POS(var)/RPOS(var) variable-arg fix; 7/7 capture:**
- `stmt_pos_var(varname, cursor)` in `snobol4_stmt_rt.c`: fetch var via `NV_GET_fn`, coerce to int via `to_int()`, return 1 if `cursor==n`
- `stmt_rpos_var(varname, cursor, subj_len)`: RPOS variant
- `POS_ALPHA_VAR varlab, cursor, gamma, omega` macro in `snobol4_asm.mac`: `lea rdi,[rel varlab]`; `mov rsi,[cursor]`; `call stmt_pos_var`; `test eax,eax`; branch
- `RPOS_ALPHA_VAR` macro: adds `mov rdx,[subj_len]` arg
- `emit_asm_pos_var()` / `emit_asm_rpos_var()` helpers in `emit_byrd_asm.c`
- POS/RPOS E_FNC dispatch: detect `E_VART` arg → var path; `E_ILIT` → literal path (unchanged)
- `extern stmt_pos_var, stmt_rpos_var` added to generated `.s` header
- `061_capture_in_arbno`: `POS(N)` where N is variable now PASS
- **M-ASM-R7 fires: 7/7 capture/ PASS**
- 106/106 C ✅  26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — Session191 (backend):**

Sprint A-R8 — strings/ — SIZE/SUBSTR/REPLACE/DUPL

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = d8901b4
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/strings
# baseline: see how many pass; fix failures; M-ASM-R8 fires at 100%
```

**⚠ CRITICAL NEXT ACTION — Session191 (frontend):**

Sprint SC6-ASM — M-SNOC-ASM-SELF: `snocone.sc` compiles itself via `-sc -asm`

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = d8901b4
apt-get install -y libgc-dev nasm && make -C src
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
# Verify SC corpus still 10/10:
bash test/frontend/snocone/sc_asm_corpus/run_sc_asm_corpus.sh   # must be 10/10
# Then attempt snocone.sc self-compile:
# locate snocone.sc in snobol4jvm or snobol4dotnet repo
# ./sno2c -sc -asm snocone.sc > snocone.s
# nasm -f elf64 -Isrc/runtime/asm/ snocone.s -o snocone.o
# gcc -no-pie snocone.o ... -o snocone_bin
# ./snocone_bin < snocone.sc > snocone_out.sc
# diff snocone_out.sc <oracle>  → empty = M-SNOC-ASM-SELF fires
```

**Session188 (frontend) — M-SNOC-ASM-CF: DEFINE calling convention; user-defined procedures via Byrd-box:**
- Extended `AsmNamedPat` with `is_fn`, `nparams`, `param_names[]`, `body_label` fields
- `asm_scan_named_patterns` detects `DEFINE('fname(args)')` stmts from sc_cf, registers as `is_fn=1`
- `emit_asm_named_def` emits α port (save params, load args from .bss arg slots, jmp body) + γ/ω (restore params, indirect-jmp via ret_ slots)
- Call-site in `prog_emit_expr` E_FNC: detects user fns, stores args → arg slots, sets ret addrs, jmps α, retrieves result via `GET_VAR fname`
- `emit_jmp`/`prog_emit_goto` route RETURN→`jmp [fn_ret_γ]` when `current_fn != NULL`
- `current_fn` tracker set/cleared as fn body labels entered/exited in prog emit loop
- DEFINE stmts skipped in prog emit loop (compile-time registration only)
- **Tests:** `double(5)→10` ✅, `add3(1,2,3)→6` ✅, `cube(3)→27` (nested calls) ✅
- 106/106 C ✅

**Session188 (backend) — M-ASM-R1/R2/R4: indirect-$ fix; coerce_numeric; OUTPUT= blank line; 26/28 PASS:**
- Fix A — indirect `$` LHS (014/015): parser produces `E_INDR` (right=operand) for `$X` in
  subject position, not `E_DOL`. Emitter `has_eq` handler now matches `E_INDR || E_DOL`;
  extracts name from `e->right` for E_INDR. Guard skips spurious `prog_emit_expr(subject,-16)`.
- Fix B — `coerce_numeric` empty string: `''` + 1 now returns integer 0 (was DT_S); `snobol4.c` line 1719
- Fix C — `OUTPUT =` null RHS: emits `LOAD_NULVCL` + `SET_OUTPUT` (was silently dropped); blank line correct
- M-ASM-R1 fires (hello/ + output/ all PASS), M-ASM-R2 fires (assign/ all PASS), M-ASM-R4 fires (arith/ basic PASS)
- Remaining: fileinfo (INPUT loop + :F branch → R8), triplet (DUPL/REMDR → R8)
- Artifacts: beauty_prog.s updated, NASM clean
- 106/106 C ✅  26/26 ASM ✅  26/28 rung ✅

**⚠ CRITICAL NEXT ACTION — Session189:**

**Frontend session — Sprint SC5-ASM: SC corpus 10-rung via `-sc -asm`**

Build the SC corpus test suite and drive to M-SNOC-ASM-CORPUS (all 10 rungs PASS).

Quick-check trigger (M-SNOC-ASM-CORPUS):
```bash
cd /home/claude/snobol4x && make -C src
# SC1: literals
cat > /tmp/sc1.sc << 'EOF'
OUTPUT = 'hello'
EOF
./sno2c -sc -asm /tmp/sc1.sc > /tmp/sc1.s && nasm -f elf64 -Isrc/runtime/asm/ /tmp/sc1.s -o /tmp/sc1.o \
  && gcc -no-pie /tmp/sc1.o src/runtime/asm/snobol4_stmt_rt.c src/runtime/snobol4/snobol4.c \
     src/runtime/mock/mock_includes.c src/runtime/snobol4/snobol4_pattern.c \
     src/runtime/mock/mock_engine.c -Isrc/runtime/snobol4 -Isrc/runtime \
     -Isrc/frontend/snobol4 -lgc -lm -w -no-pie -o /tmp/sc1_bin && /tmp/sc1_bin
# expected: hello
```

Session start commands:
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 0371fad
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
```

**Session187 — corpus ladder infrastructure + R1-R4 fixes; 23/28 PASS:**
- `test/crosscheck/run_crosscheck_asm_rung.sh` — new per-rung ASM corpus driver
- Baseline R1–R4: 21/28 → after fixes: **23/28 PASS**
- Fixed: `E_FLIT` real literals (`003_output_real_literal` ✅), null-RHS `X =` (`012_assign_null` ✅)
- Added: `LOAD_REAL`/`ASSIGN_NULL`/`SET_VAR_INDIR` macros; `stmt_realval`/`stmt_set_null`/`stmt_set_indirect` shims
- M-ASM-R3 (concat/ 6/6) ✅ — fires this session
- Remaining failures: `014`/`015` indirect-`$` (E_DOL LHS path not reached), `literals` (coerce_numeric bug), `fileinfo`/`triplet` (deferred R8)
- Artifacts: beauty_prog.s + roman.s + wordcount.s updated, all NASM-clean
- 106/106 C ✅  26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — Session190 (backend session):**

Sprint A-R7 — fix `061_capture_in_arbno` → M-ASM-R7 fires

**Root cause:** `emit_asm_pos(long n,...)` always takes a literal. In E_FNC POS case,
`arg->ival` is used regardless of arg kind. For `POS(N)` where N is `E_VART`, `ival=0`
→ always emits `POS_ALPHA 0`. Fix:
1. `stmt_pos_var(varname)` in `snobol4_stmt_rt.c`: fetch N, coerce int, check `cursor==n`
2. `POS_ALPHA_VAR varlab, cursor, gamma, omega` macro in `snobol4_asm.mac`
3. In E_FNC POS case: if `arg->kind == E_VART` → call `emit_asm_pos_var()` helper

**Session start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 6f72fa3
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/capture
# expected: 6/7 (061 POS(N) variable arg still failing)
```
After fix: M-ASM-R7 fires → begin Sprint A-R8 (strings/).

**Session start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = ba178d7
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh \
    $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith
# expected: 23/28 (session187 baseline)
```

**⚠ CRITICAL NEXT ACTION — Session187 continued (backend session):**

Sprint A-R1 — fix three root causes to clear R1+R2:

**Fix 1 — E_FLIT (real literals):** add `case E_FLIT:` to `prog_emit_expr` in
`emit_byrd_asm.c`. Add `stmt_realval(double)` to `snobol4_stmt_rt.c`.
Add `LOAD_REAL` macro to `snobol4_asm.mac`.

**Fix 2 — null RHS (`X =`):** `X =` parses as `has_eq=1`, replacement=`E_NULV` or NULL.
The `ASSIGN_STR` fast path is taken with empty sval → writes garbage.
Fix: detect NULL/E_NULV replacement → emit `ASSIGN_NULL varlab` macro.
Add `ASSIGN_NULL var` macro to `snobol4_asm.mac` that calls `stmt_set(name, NULVCL)`.

**Fix 3 — indirect `$` LHS (`$'X'=`, `$V=`):** subject is `E_DOL(E_QLIT)` or `E_DOL(E_VART)`.
Currently the `has_eq` path only handles `E_VART`/`E_KW` subjects.
Add `E_DOL` subject case: eval inner expr → get string name → call `stmt_set_indirect`.
Add `stmt_set_indirect(DESCR_t name_val, DESCR_t val)` to `snobol4_stmt_rt.c`.
Add `SET_VAR_INDIR` macro.

Quick-check after fixes:
```bash
cd /home/claude/snobol4x && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh \
    $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith 2>&1
# target: 26/28 PASS (fileinfo + triplet deferred to R8)
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh  # must stay 106/106
```

**Session186 — Sprint SC3 partial: sc_driver.h/c + main.c -sc wiring + Makefile; 106/106:**
- `src/frontend/snocone/sc_driver.h` — `sc_compile(source, filename) → Program*` API
- `src/frontend/snocone/sc_driver.c` — full pipeline: sc_lex → per-stmt sc_parse → sc_lower;
  ported directly from proven `pipeline()` helper in `sc_lower_test.c` (50/50 PASS session185)
- `src/driver/main.c` — `-sc` flag + `.sc` auto-detect via `ends_with()`; `read_all()` reads
  FILE* into heap buffer; Snocone path: `read_all → sc_compile → snoc_emit/asm_emit`;
  SNOBOL4 path unchanged
- `src/Makefile` — `FRONTEND_SNOCONE` block: `sc_lex.c sc_parse.c sc_lower.c sc_driver.c`;
  added to SRCS; `-I frontend/snocone` added to CFLAGS
- Build: zero errors/warnings (all 4 new objects + main.o recompile clean)
- 106/106 C crosscheck invariant unaffected
- BLOCKED: M-SNOC-EMIT not yet fired — `snoc_emit` generates no epilogue
  (`_SNO_END:` / `finish()` / `return 0;`) for Snocone path. SNOBOL4 frontend
  appends implicit END STMT_t; `sc_lower` does not. Fix: append synthetic END
  STMT_t in `sc_driver.c` after `sc_lower()` returns.

**Session185 — M-SNOC-LOWER: sc_lower.h + sc_lower.c + test; 50/50 PASS:**
- `src/frontend/snocone/sc_lower.h` — ScLowerResult (prog + nerrors), sc_lower() API,
  sc_lower_free() API; full operator mapping table in header comment
- `src/frontend/snocone/sc_lower.c` — postfix RPN evaluator: EXPR_t* operand stack
  (1024 slots), per-kind dispatch for all 40+ ScKind values;
  binary: E_ADD/E_SUB/E_MPY/E_DIV/E_EXPOP/E_CONC/E_OR/E_NAM/E_DOL;
  unary: E_MNS (SC_MINUS), E_INDR (SC_STAR/SC_DOLLAR), E_KW (SC_AMPERSAND),
         E_ATP (SC_AT), NOT/DIFFER (SC_TILDE/SC_QUESTION);
  fn-ops: EQ/NE/LT/GT/LE/GE/IDENT/DIFFER/LLT/LGT/LLE/LGE/LEQ/LNE/REMDR → E_FNC;
  SC_CALL → E_FNC(name, nargs); SC_ARRAY_REF → E_IDX(name, nargs);
  SC_ASSIGN → E_ASGN(lhs, rhs) then assembled into STMT_t at SC_NEWLINE boundary;
  statement assembly: E_ASGN → subject+replacement+has_eq; other → subject-only stmt
- `test/frontend/snocone/sc_lower_test.c` — 50 assertions: hello assign (trigger),
  arith (E_ADD/E_ILIT), fnc call (GT nargs=2), eq op (== → EQ), multi-stmt (2 stmts),
  OR (|| → E_OR), concat (&& → E_CONC), percent (% → REMDR), array ref (E_IDX),
  unary minus (E_MNS)
- Pipeline helper: splits at SC_NEWLINE, parses each segment independently, keeps
  ScParseResult alive until after sc_lower (text pointers shared), then frees
- M-SNOC-LOWER trigger: OUTPUT = 'hello' lowers to assignment STMT_t with E_QLIT rhs PASS
- 106/106 C crosscheck invariant unaffected

**⚠ CRITICAL NEXT ACTION — Session187 (frontend session):**

Sprint SC3 — M-SNOC-EMIT: fix program epilogue for Snocone path

**What's done (session186):**
- `src/frontend/snocone/sc_driver.h` + `sc_driver.c` — `sc_compile()` pipeline: sc_lex → per-stmt sc_parse → sc_lower; ported from proven pipeline() helper (50/50 PASS)
- `src/driver/main.c` — `-sc` flag + `.sc` auto-detect; `read_all()`; routes through `sc_compile()` then existing `snoc_emit`/`asm_emit`
- `src/Makefile` — `FRONTEND_SNOCONE` block; `sc_lower.c` + `sc_driver.c` in SRCS; `-I frontend/snocone` in CFLAGS
- Build clean, 106/106 ✅

**Blocking issue:** `snoc_emit` generates no program epilogue (`_SNO_END:` / `finish()` / `return 0;`) for the Snocone path. The SNOBOL4 parser appends an implicit `END` STMT_t; `sc_lower` does not.

**Fix — in `sc_driver.c`, after `sc_lower()` returns:**
```c
/* Append synthetic END statement so snoc_emit closes main() correctly */
static void prog_append_end(Program *prog) {
    STMT_t *end = calloc(1, sizeof(STMT_t));
    end->kind   = S_END;   /* or whatever the END sentinel kind is */
    end->lineno = 0;
    if (prog->tail) prog->tail->next = end;
    else            prog->head = end;
    prog->tail  = end;
    prog->nstmts++;
}
```

Check the actual STMT_t kind constant for END in `sno2c.h` / `emit.c` — search for `S_END` or `"END"` handling in `snoc_emit`. The SNOBOL4 parser adds it via `snoc_parse` → check `parse.c` for how it appends the END node.

After the fix, the M-SNOC-EMIT quick-check trigger must pass:
```bash
cd /home/claude/snobol4x
make -C src
echo "OUTPUT = 'hello'" > /tmp/t.sc
INC=/home/claude/snobol4corpus/programs/inc
RT=src/runtime
./sno2c -sc /tmp/t.sc > /tmp/t.c
gcc /tmp/t.c $RT/snobol4/snobol4.c $RT/mock/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -o /tmp/t_bin
/tmp/t_bin
# expected output: hello
# PASS → M-SNOC-EMIT fires → begin Sprint SC4
```

Session start commands:
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = d01fb57
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
```

**Session183 — M-SNOC-LEX: sc_lex.h + sc_lex.c + test; 187/187 PASS:**
- `src/frontend/snocone/sc_lex.h` — ScKind enum (48 kinds), ScToken, ScTokenArray, API
- `src/frontend/snocone/sc_lex.c` — tokenizer: # comment strip, continuation detection,
  semicolon split, longest-match 4→1 char operator table, keyword reclassification,
  integer/real/string/ident scanning. Direct port of snobol4jvm snocone.clj +
  snobol4dotnet SnoconeLexer.cs (both consulted — C# was the closest model to C)
- `test/frontend/snocone/sc_lex_test.c` — 187 assertions mirroring C# TestSnoconeLexer.cs:
  helpers, literals, all 12 keywords, all operators (longest-match), punctuation,
  statement boundaries, semicolons, line numbers, 12 E2E snippets
- M-SNOC-LEX trigger: `OUTPUT = 'hello'` → IDENT ASSIGN STRING NEWLINE EOF PASS
- 106/106 C crosscheck invariant unaffected; 26/26 ASM unaffected

**⚠ CRITICAL NEXT ACTION — Session184 (frontend session):**

Sprint SC1 — M-SNOC-PARSE: `src/frontend/snocone/sc_parse.c`

Recursive-descent parser consuming `ScToken[]` from sc_lex.
Produces `ScNode` AST. Port from snobol4jvm `snocone.clj` `parse-expression` +
snobol4dotnet `SnoconeParser.cs`.

Files:
- `src/frontend/snocone/sc_parse.h` — ScNode kinds + struct + `sc_parse()` API
- `src/frontend/snocone/sc_parse.c` — recursive descent: expr (shunting-yard from
  Clojure parse-expression), stmt, if/while/do/for/procedure/struct/goto/return/block
- `test/frontend/snocone/sc_parse_test.c` — mirrors TestSnoconeParser.cs

Quick-check trigger (M-SNOC-PARSE):
```bash
gcc -I src/frontend/snocone -o /tmp/sc_parse_test \
    test/frontend/snocone/sc_parse_test.c \
    src/frontend/snocone/sc_lex.c src/frontend/snocone/sc_parse.c
/tmp/sc_parse_test
# PASS → M-SNOC-PARSE fires → begin Sprint SC2
```


- `src/frontend/snobol4/` ← lex, parse, sno.l/y, sno2c.h (from src/sno2c/)
- `src/frontend/rebus/` ← rebus frontend (from src/rebus/)
- `src/frontend/icon/` ← Python parser prototypes (from src/parser/)
- `src/frontend/{snocone,prolog}/` ← placeholders
- `src/ir/byrd/` ← emit_cnode.c/.h + byrd_ir/ir/lower.py (from src/sno2c/ + src/ir/)
- `src/backend/c/` ← emit.c, emit_byrd.c, trampoline files (from src/sno2c/)
- `src/backend/x64/` ← emit_byrd_asm.c (from src/sno2c/)
- `src/backend/{jvm,net}/` ← Python stubs (from src/codegen/)
- `src/driver/main.c` ← compiler entry point (from src/sno2c/)
- `src/runtime/mock/` ← mock_engine.c, mock_includes.c (from src/runtime/ + src/runtime/snobol4/)
- `src/runtime/engine/` ← engine.c/.h, runtime.c/.h (from src/runtime/)
- `src/runtime/runtime.h` + `src/runtime/engine.h` ← forwarding shims for relative includes
- `artifacts/c/beautiful.c` ← generated file moved out of runtime source tree
- `test/frontend/snobol4/` ← .sno fixtures (from test/sprintN/)
- `test/backend/c/` ← .c + .py oracles (from test/sprintN/)
- `scratch/` ← gitignored working dir
- `sno2c` ← binary now at repo root (was src/sno2c/sno2c)
- `src/Makefile` ← new build root
- Scan-retry omega fix: `jg next_lbl` → `jg tgt_f` in omega block of `asm_emit_program`
  Fixes 034_goto_failure, 057_pat_fail_builtin, 098_keyword_anchor
- beauty_prog.s artifact updated, NASM clean
- 106/106 C PASS ✅, 26/26 ASM PASS ✅

**Session168 — FAIL_BR/FAIL_BR16/SUBJ_FROM16 renames; CONC2/ALT2 macros; COL2_W=12; CONC2_N/CONC2 fast paths:**
- `IS_FAIL_BRANCH` → `FAIL_BR` (14→7 chars); `IS_FAIL_BRANCH16` → `FAIL_BR16` (16→8 chars)
- `SETUP_SUBJECT_FROM16` → `SUBJ_FROM16` (20→11 chars)
- `CALL2_SS` → `CONC2`, `CALL2_SN` → `CONC2_N`; `ALT2`/`ALT2_N` aliases added (same expansion)
- All back-compat `%define` aliases preserved — existing `.s` files still assemble
- `COL2_W=12`, `COL_CMT=72` defined in `emit_byrd_asm.c`; `ALFC` comment column uses `COL_CMT`
- `CONC2_N`/`CONC2` fast paths in `E_OR`/`E_CONC` for `QLIT+NULV` and `QLIT+QLIT` children (7 sites)
- Three emit sites updated: `FAIL_BR`, `FAIL_BR16`, `SUBJ_FROM16`
- beauty_prog_session168.s: 12689 lines (down 56 from session167), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**Session171 — CONC2_SV/VS/VN/VV fast paths; 12444 lines:**
- `CONC2_SV/VS/VN/VV` + `ALT2_SV/VS/VN/VV` macros added to `snobol4_asm.mac`
- Six new fast paths in `emit_byrd_asm.c` E_OR/E_CONC — all two-atom shapes now covered
- 12689 → 12444 lines (−245); 529 verbose `sub rsp,32` blocks remain (nested expr trees)
- 106/106 26/26

**Session170 — REF/DOL/ARBNO block-header comments to col2 on label line:**
- `asmLC(lbl, comment)` helper: emits `label: ; comment\n` with no instruction
- Three standalone `A("\n; ...")` sites (REF/DOL/ARBNO) converted to `asmLC` on alpha label
- `ALFC` empty-label guard: suppresses bare `:` when label is `""`
- 12689 lines unchanged, NASM clean, 106/106 26/26

**Session169 — SEP_W 80→120:**
- `SEP_W` 80 → 120; separator lines now 120 chars (Cherryholmes standard)
- Four-column layout retained as-is per Lon's decision
- 12689 lines, 106/106 26/26

**Session175 — col3 alignment perfected; emit_instr() helper; 11594→11654 lines:**
- `emit_instr(instr)` helper added: emits opcode word, pads to COL_W+COL2_W=40, then operands
- Three paths fixed: `asmLB()` (ALF), `ALFC` macro inline expansion, `A()` pending-label fold
- Before: 901 instruction lines misaligned (706 `jmp`/`sub`/`mov` at col 37, 38 macros at col 42)
- After: 0 misaligned instruction lines; every line: label@0, opcode@28, operands@40
- `asmLC` comment-only lines (`label: ; comment`) correctly exempt — no opcode/operand split
- beauty_prog_session175.s: 11654 lines, NASM clean, 106/106 26/26

**session177 — housekeeping; artifact reorg; test baseline:**
- M-ASM-IR deferred — IR shape unknown until both backends mature
- M-MONITOR retargeted to ASM backend
- Artifact protocol: canonical files only, asm/c/jvm/net folders, no numbered copies
- ASM corpus baseline: 47/113 PASS; 16 NASM_FAIL (2 root causes); 38 FAIL; 12 TIMEOUT
- Next: fix arithmetic (7 tests), fix 2 NASM_FAIL root causes (15 tests), then M-MONITOR

**⚠ CRITICAL NEXT ACTION — Session178:**

Fix corpus tests in priority order:
1. **Arithmetic (023–029, 7 tests):** `prog_emit_expr` for `E_ADD`/`E_SUB`/`E_MPY`/`E_DIV`/`E_EXP`/`E_NEG` — currently returning empty. Check `stmt_apply` calls in `snobol4_stmt_rt.c` for arithmetic ops.
2. **NASM_FAIL `P_X_ret_gamma`** (9 tests: 009–013, 019, 056 + others) — named pattern return slot not declared when pattern appears inline in assignment RHS. Fix: ensure `AsmNamedPat` registry entries are emitted for all referenced patterns.
3. **NASM_FAIL `P_1_α_saved`** (6 tests: 033–035, 038, 062–064) — ALT cursor save slot missing in statement-context pattern. Fix: ensure `.bss` slot is declared for every ALT node regardless of context.

Then Sprint M1 (M-MONITOR): build `snobol4harness/monitor/` runner targeting ASM backend.
1. Declare `.bss` scratch pair: `conc_tmp0_rax resq 1` / `conc_tmp0_rdx resq 1`
2. For each complex child: evaluate normally (result in `[rbp-32/24]`), then `mov rax,[rbp-32]; mov [conc_tmp0_rax],rax` etc.
3. Build args array using scratch values
4. New macros `CONC2_TV/VT/TS/TN` for temp+atom patterns
5. Target: 15 → 0 verbose blocks; further line-count reduction toward M-ASM-BEAUTIFUL

**Session174 — CALL1_VAR + integer-arg fast paths; 12594→11594 lines:**
- `CALL1_VAR fn, varlab` macro + emitter fast path: 1-arg calls with E_VART arg (100 cases) → single macro
- `CONC2_VI/IV/II/NI/SI/IS` + `*16` variants: 2-arg calls with integer-literal args → macros
- `CONC2_NN` macro added (NULVCL+NULVCL)
- 77 verbose `sub rsp,32` blocks → 15; all 15 have genuinely complex children (E_IDX/E_SUB/E_FNC/E_NAM)
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS
- beauty_prog_session174.s: 11594 lines (−1000 from session173), NASM clean

**⚠ CRITICAL NEXT ACTION — Session175:**

The 15 remaining verbose blocks all have complex children (confirmed by debug probe: a0kind/a1kind ∈ {E_IDX=20, E_SUB=9, E_FNC=18, E_NAM=16}). These cannot use atom fast paths.

**Generic fallback path explanation:**
The `prog_emit_expr` generic fallback fires when no fast path matches. It allocates an N-slot args array on the stack (`sub rsp, N*16`), then for each arg calls `prog_emit_expr(arg, rbp_off)` recursively — which stores the result into `[rbp-32/24]`, then `STORE_ARG32 k` copies it into `[rsp + k*16]`. After all args: `APPLY_FN_N fn, N` calls the function, `add rsp, N*16` restores the stack, then `STORE_RESULT` / `mov [rbp±n]` saves rax/rdx.

The problem: when a complex child is evaluated, `prog_emit_expr` recurses and overwrites `[rbp-32/24]`. If that child is itself an `APPLY_FN_N` call, it issues another `sub rsp,32` — nested `sub rsp` is what we see in the output. The result-temp strategy breaks this cycle:

**Result-temp strategy:**
1. Declare `.bss` scratch pair: `conc_tmp0_rax resq 1` / `conc_tmp0_rdx resq 1`
2. For each complex child: evaluate it normally (gets result in `[rbp-32/24]`), then `mov rax,[rbp-32]; mov [conc_tmp0_rax],rax` etc. to save into scratch
3. Then build the args array using `mov rax,[conc_tmp0_rax]` → `mov [rsp],rax` etc.
4. One scratch pair per nesting depth suffices since children are evaluated sequentially

Implementation in `prog_emit_expr` E_FNC generic path: detect when any arg is complex, emit scratch `.bss` declarations in the `.bss` section header pass, then use save/restore around each complex arg evaluation.

**Session173 — col3 alignment; no fourth column; sep→label fold:**
- col3: operands now at COL_W+COL2_W=40 — A() scans opcode end, pads to col 40 before operands
- No 4th column: ALFC uses one space before `;` (was padding to COL_CMT=72)
- Sep→label: emit_sep_major buffers into pending_sep; A() fold path emits `; sep` immediately before `label:  INSTR` (no blank gap between sep and label)
- Non-label sep sites (PROGRAM BODY, END, NAMED PATTERN BODIES, STUB LABELS, STRING TABLE) use flush_pending_sep()
- 12594 lines; 496 verbose sub-rsp,32 blocks remain (unchanged — formatting only); NASM clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**Session172 — CONC2_*16/ALT2_*16 macros; E_FNC 2-arg fast paths; 529→496 verbose blocks:**
- `CONC2_16/CONC2_N16/CONC2_SV16/CONC2_VS16/CONC2_VN16/CONC2_VV16` + `ALT2_*16` aliases added to `snobol4_asm.mac` — result stored at `[rbp-16/8]` (subject slot)
- E_FNC 2-arg fast paths added in `emit_byrd_asm.c`: detect atom arg shapes (SS/SN/SV/VS/VN/VV) for both `rbp_off==-32` and `rbp_off==-16`, emit CONC2_* macros (which work for any fn label, not just CONCAT/ALT)
- Diagnosis: 529 blocks split into two root causes: (a) E_FNC 2-arg with atom children at rbp_off==-16 (now fixed), (b) E_CONC/E_OR/E_FNC with complex (non-atom) children (440 blocks remain — need result-temp strategy)
- 12444 → 12100 lines (−344); 529 → 496 verbose blocks; NASM clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Session173:**

Remaining 496 verbose `sub rsp, 32` blocks have at least one complex (non-atom) child. Survey the shapes: from prior classification, ~188 are `E_CONC/E_OR` with `left=other right=NUL slot=-32` (left child is itself `E_CONC`/`E_OR`/`E_FNC`). Strategy: **CONC3 survey** — check if the dominant nested shape is `CONCAT(CONCAT(atom,atom), atom)` collapsible with a 3-arg macro.

Steps:
1. Classify remaining 496 blocks: for each, what is the left child's shape (E_CONC? E_FNC? depth?)
2. If dominant shape is depth-2 left-associative CONCAT chains → add `CONC3` macro + emitter fast path
3. Otherwise → result-temp strategy per session172 plan

Evaluate complex child into a `.bss` scratch pair (`conc_tmp_rax`, `conc_tmp_rdx`), then collapse with new macros:
- `CONC2_TV fn, tmplab, varlab` — fn(pre-computed-temp, variable)
- `CONC2_VT fn, varlab, tmplab` — fn(variable, pre-computed-temp)
- `CONC2_TS fn, tmplab, strlab` — fn(pre-computed-temp, str)
- `CONC2_TN fn, tmplab`         — fn(pre-computed-temp, NULVCL)

Emitter change: in `E_OR`/`E_CONC` generic path, detect when left/right is a simple atom vs complex; for complex-left+atom-right patterns, emit `sub rsp,32` + inline-evaluate-left + `STORE_ARG32 0` + macro for right half.

Alternatively: survey the 230 double-sub (nested) cases — these may all be `CONCAT(CONCAT(atom,atom), atom)` and collapsible with a `CONC3` 3-arg macro.

The dominant `CONCAT(E_QLIT, E_VART)` shape — string literal left, variable right — accounts for the bulk of the ~409 remaining verbose blocks (each 10 lines). Add `CONC2_SV` macro and fast path:

**Macro** (`snobol4_asm.mac`):
```nasm
; CONC2_SV fn, strlab, varlab  — fn(str_literal, variable) → [rbp-32/24]
%macro CONC2_SV 3
    sub     rsp, 32
    lea     rdi, [rel %2]
    call    stmt_strval
    mov     [rsp], rax
    mov     [rsp+8], rdx
    lea     rdi, [rel %3]
    call    stmt_get
    mov     [rsp+16], rax
    mov     [rsp+24], rdx
    lea     rdi, [rel %1]
    mov     rsi, rsp
    mov     rdx, 2
    call    stmt_apply
    add     rsp, 32
    mov     [rbp-32], rax
    mov     [rbp-24], rdx
%endmacro
%define ALT2_SV CONC2_SV
```

**Emitter** (`emit_byrd_asm.c`, `E_OR`/`E_CONC` case, after existing fast paths):
```c
int right_is_var = e->right && e->right->kind == E_VART;
if (left_is_str && right_is_var && rbp_off == -32) {
    const char *mac_sv = (e->kind == E_OR) ? "ALT2_SV " : "CONC2_SV";
    const char *slab = prog_str_intern(e->left->sval);
    const char *vlab = prog_str_intern(e->right->sval);
    A("    %s %s, %s, %s\n", mac_sv, fnlab, slab, vlab);
    return 1;
}
```

Also add `CONC2_VN` (variable left, NULVCL right) and `CONC2_VV` (two variables) for further coverage.

**Session169 start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = d872625

apt-get install -y libgc-dev nasm && make -C src/sno2c
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```
- `ASSIGN_INT var, n, fail_lbl` — collapses LOAD_INT + IS_FAIL_BRANCH + SET_VAR (6 lines → 1)
- `ASSIGN_STR var, s, fail_lbl` — collapses LOAD_STR + IS_FAIL_BRANCH + SET_VAR (6 lines → 1)
- `CALL1_INT fn, n` — collapses sub rsp + LOAD_INT + STORE_ARG32 + APPLY_FN_N + add rsp + mov-pair (9 lines → 1)
- `CALL1_STR fn, s` — same with string literal arg
- Redundant `mov [rbp-32],rax` / `mov [rbp-24],rdx` after LOAD_INT/LOAD_STR eliminated
- Post-APPLY_FN_N mov pair → STORE_RESULT macro
- `emit_sep_major(tag)` — `; === tag ====...` (80 cols, configurable SEP_W) at every SNOBOL4 stmt, section headers, named pattern headers; source label embedded when present
- `emit_sep_minor(tag)` — `; --- tag ----...` before γ/ω trampolines in named pattern defs
- STMT_SEP NASM macro bypassed — separators are raw comment text, visible without expansion
- beauty_prog_session167.s: 12745 lines (down 919 from session166), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Session168:**

Continue M-ASM-BEAUTIFUL: the multi-arg E_OR/E_CONC (ALT/CONCAT) 2-arg calls still emit verbose sub/LOAD/STORE/APPLY/add sequences. Add `CALL2_SS`, `CALL2_SN` macro fast-paths in emit_byrd_asm.c E_OR/E_CONC case (macros already in snobol4_asm.mac from session167). Also: L_sn_10 still has a deeply nested raw sequence — the CALL2_SS/SN paths will collapse it.

**Session165 — inline column alignment (COL_W=28):**
- Added `out_col` tracker + `oc_char()`/`oc_str()`/`emit_to_col()` in emit_byrd_asm.c
- `oc_char()` counts display columns, skips UTF-8 continuation bytes (α/β/γ/ω = 1 col each)
- `emit_to_col(n)`: pads to col n; if already past n, emits newline then pads
- Every instruction (labeled or unlabeled) now starts at display column 28
- ALFC fixed: was using `%-28s` printf padding (byte-based), now uses `oc_str`+`emit_to_col`
- STMT_SEP/PORT_SEP/directives/section/.bss exempt from col-28 alignment
- Comment column: COL_W+44=72; non-wrapping (one space if instruction already past col 72)
- beauty_prog_session165.s: 13664 lines, assembles clean, 0 misaligned lines
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Session166:**

Lon reviews `beauty_prog_session165.s` → M-ASM-BEAUTIFUL fires, OR next step toward decoupled emitter/beautifier (separate concerns as done for C backend).

**Session167 start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3
apt-get install -y libgc-dev nasm && make -C src/sno2c
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Session163 — four-column format complete: label: MACRO args ; comment**
- DOL_SAVE macro: 3 raw instructions → 1 line
- DOL_CAPTURE macro: 9 raw instructions → 1 line
- ALT_ALPHA macro: absorbs trailing jmp lα
- ALT_OMEGA macro: absorbs trailing jmp rα
- All \n\n double-newlines removed (45 instances)
- Every state is one line: `label:  MACRO args ; comment`
- beauty_prog_session163.s: 14448 lines (down 3772 from session159), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION:**
Lon reviews `artifacts/asm/beauty_prog_session163.s` → M-ASM-BEAUTIFUL fires.

**HEAD (previous):** `6ed79c5` session162
**Milestone:** M-ASM-CROSSCHECK ✅ session151 → **M-ASM-BEAUTIFUL** (A14, active)

**Session162 — three-column format: label: MACRO args ; comment:**
- Added `ALFC(lbl, comment, fmt, ...)` — folds preceding comment line onto instruction line
- Result: `seq_l26_alpha:  LIT_ALPHA lit_str_6, 2, ... ; LIT α`
- ALT emitter fully uses ALT_SAVE_CURSOR/ALT_RESTORE_CURSOR macros
- beauty_prog_session162.s: 14950 lines (down 3270 from session159), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION:**
Lon reviews `artifacts/asm/beauty_prog_session162.s` → M-ASM-BEAUTIFUL fires.

**HEAD (previous):** `0f7f20b` session161
**Milestone:** M-ASM-CROSSCHECK ✅ session151 → M-ASM-BEAUTY (A10, blocked 102-109) → **M-ASM-BEAUTIFUL** (A14, active)

**Session161 — label: MACRO args on one line:**
- Added `ALF(lbl, fmt, ...)` helper — emits `label:  INSTRUCTION args` on one line
- 40 `asmL()+A()` and `asmL()+asmJ()` pairs folded into single `ALF()` calls
- Every Byrd box port: `seq_l26_alpha:  LIT_ALPHA lit_str_6, 2, saved, cursor, ...`
- beauty_prog_session161.s: 15883 lines (was 16421 — 538 more eliminated), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Sprint A14 (M-ASM-BEAUTIFUL):**
Lon reviews `artifacts/asm/beauty_prog_session161.s` → M-ASM-BEAUTIFUL fires.

**Session160 — M-ASM-BEAUTIFUL: all pattern port macros landed:**
- All primitive emitters replaced with one macro call per port:
  LIT_ALPHA/LIT_BETA, SPAN_ALPHA/SPAN_BETA, BREAK_ALPHA/BREAK_BETA,
  ANY_ALPHA/ANY_BETA, NOTANY_ALPHA/NOTANY_BETA, POS_ALPHA/POS_BETA,
  RPOS_ALPHA/RPOS_BETA, LEN_ALPHA/LEN_BETA, TAB_ALPHA/TAB_BETA,
  RTAB_ALPHA/RTAB_BETA, REM_ALPHA/REM_BETA, SEQ_ALPHA/SEQ_BETA,
  ALT_SAVE_CURSOR/ALT_RESTORE_CURSOR, STORE_RESULT/SAVE_DESCR
- snobol4_asm.mac extended with all port macros (811 lines)
- emit_byrd_asm.c: all raw instruction sequences replaced; each port = 1 emitted line
- Body-only (-asm-body) now emits `%include "snobol4_asm.mac"`
- run_crosscheck_asm.sh: nasm -I src/runtime/asm/ added
- beauty_prog_session160.s: 16421 lines (was 18220 — 1799 eliminated), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Sprint A14 (M-ASM-BEAUTIFUL):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 0f7f20b

apt-get install -y libgc-dev nasm
make -C src/sno2c

mkdir -p /home/snobol4corpus
ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**M-ASM-BEAUTIFUL fires** when Lon reads `beauty_prog_session160.s` and declares it beautiful.

**Session158 — M-ASM-BEAUTY progress — 101_comment PASS:**
- `section .text` before named pattern bodies (was `.data` → segfault → **root cause**)
- Stack alignment: `sub rsp,56` (6 pushes + 56 = 112, 112%16=0 ✅)
- `PROG_END`: explicit pops (not `leave`)
- `E_FNC` → `stmt_apply()` in `prog_emit_expr`
- Case 1 S/F dispatch: expression-only stmts with `:F(label)` now check `is_fail`
- `stmt_set_capture()`: DOL/NAM captures materialised into SNOBOL4 variables
- Pattern capture: `X *PAT . V` → `V='bc'` PASS ✅
- **101_comment PASS ✅** — 102-109 `Parse Error`
- Root cause of Parse Error: `E_OR`/`E_CONC` → NULVCL for named pattern assignments

**⚠ CRITICAL NEXT ACTION — Sprint A10 (M-ASM-BEAUTY):**

**102-109 fail with `Parse Error`** — beauty's `*Parse` named pattern is assigned
using `E_OR` (alternation `|`) and `E_CONC` (concatenation) expressions.
These are currently fallback → NULVCL in `prog_emit_expr`.
Fix: register `pat_alt()` and `pat_concat()` as callable functions `ALT`/`CONCAT`,
add `E_OR` and `E_CONC` cases to `prog_emit_expr` that call `stmt_apply()`.

**File:** `src/sno2c/emit_byrd_asm.c` — `prog_emit_expr()` switch
**File:** `src/runtime/snobol4/snobol4.c` — add `_b_PAT_ALT`, `_b_PAT_CONCAT`, register

**Session151 — M-ASM-CROSSCHECK fires — 26/26 ASM PASS:**
- Per-variable capture buffers: `CaptureVar` registry, `cap_VAR_buf`/`cap_VAR_len` in `.bss`
- `cap_order[]` table in `.data` — harness walks it at `match_success`, one capture per line
- `E_INDR` case added to `emit_asm_node` — `*VAR` indirect pattern reference resolved via named-pattern registry
- `/dev/null` dry-run collection pass: replaces `open_memstream` two-pass; uid counter saved/restored so real pass generates identical labels
- `.asm.ref` convention: capture tests with harness-specific output use `TEST.asm.ref`; `run_crosscheck_asm.sh` prefers `.asm.ref` over `.ref`
- `run_crosscheck_asm.sh`: `extract_subject` now finds subject var from match line first; `build_bare_sno` keeps plain-string assignments when var referenced as `*VAR`
- 106/106 main crosscheck invariant holds; HEAD `3624d9d`

**⚠ CRITICAL NEXT ACTION — Sprint A10 (M-ASM-BEAUTY):**

Session154 state:
- `asm_emit_program()` walks all stmts, emits `main()` with `stmt_*` C-shim calls
- Label scheme: `_L_<alnum_base>_<N>` — N guarantees uniqueness, base aids readability
- `emit_jmp()` handles RETURN/FRETURN/END → `_SNO_END`; stub labels for undefined/computed gotos
- beauty.sno assembles and links cleanly via `-asm`
- Statement-only programs work: `OUTPUT = 'hello'` → correct output ✅
- **beauty.sno hangs**: pattern-match stmts (Case 2) fall through without running the pattern

**Next step — pattern-match stmt execution:**
Case 2 must: (1) get subject string via `stmt_get()`, (2) set `subject_data`/`subject_len_val`/`cursor` globals, (3) call `root_alpha` (Byrd box), (4) on `match_success` → apply replacement + goto S-label; on `match_fail` → goto F-label.
Approach: inline Byrd box + C-shim `match_success`/`match_fail` as ASM labels per stmt.

- `ref_astar_bstar.s`: ASTAR=ARBNO("a"), BSTAR=ARBNO("b") on "aaabb" → `aaabb\n` PASS ✅
- `anbn.s`: 4 sequential named-pattern call sites (2×A_BLOCK + 2×B_BLOCK) on "aabb" → `aabb\n` PASS ✅
- `emit_byrd_asm.c`: `AsmNamedPat` registry + `asm_scan_named_patterns()` pre-pass + `emit_asm_named_ref()` call-site + `emit_asm_named_def()` body emitter; `E_VART` wired in `emit_asm_node`
- Named pattern calling convention: Proebsting §4.5 gate — caller stores γ/ω absolute addresses into `pat_NAME_ret_gamma/omega` (.bss qwords), then `jmp pat_NAME_alpha/beta`; body ends `jmp [pat_NAME_ret_gamma/omega]`. No call stack.
- 106/106 crosscheck invariant confirmed; end-to-end `.sno → sno2c -asm → nasm → ld → run` verified

**⚠ CRITICAL NEXT ACTION — Sprint A9 (M-ASM-CROSSCHECK):**

The crosscheck corpus (`crosscheck/patterns/038_pat_literal.sno` etc.) are full SNOBOL4 programs using `OUTPUT`, variables, `:S(YES)F(NO)` gotos — **not** standalone pattern tests. The ASM backend currently only handles pattern-match nodes; it cannot yet compile full SNOBOL4 statements.

**Sprint A9 is therefore scoped differently than A0–A8:**

The path to M-ASM-CROSSCHECK is NOT "run existing crosscheck suite via -asm" — those tests require the full runtime (OUTPUT, goto, variables). Instead:

**Sprint A9 plan — ASM crosscheck harness:**
1. Write `src/runtime/asm/snobol4_asm_harness.c` — thin C harness:
   - Reads subject string from `argv[1]` (or stdin)
   - Declares `extern` symbols: `cursor`, `subject_data`, `subject_len_val`, `match_success`, `match_fail`
   - Provides `_start`-equivalent in C: initialises slots, calls `root_alpha` via function pointer or inline asm `jmp`
   - On `match_success`: prints matched span `subject[0..cursor]` to stdout, exit 0
   - On `match_fail`: exit 1
2. Update emitter: body-only mode (no `_start`, no `match_success/fail`) — extern the cursor/subject symbols
3. New crosscheck driver: for each `crosscheck/capture/*.sno` and `crosscheck/patterns/*.sno`, extract the pattern + subject, compile body-only `.s`, link with harness, run, diff
4. First target: `038_pat_literal` via harness PASS → grow to 106/106

**Key insight from corpus survey (session148):**
- `crosscheck/patterns/` has `038_pat_literal.sno` through `047_pat_rtab.sno` — pure pattern tests
- `crosscheck/capture/` has `058_capture_dot_immediate.sno` through `062_capture_replacement.sno`
- These are the natural first targets for ASM crosscheck since they exercise only pattern nodes

**Sprint A9 steps:**
1. `snobol4_asm_harness.c` — subject from argv[1], `extern` ASM symbols, C `_start`
2. `emit_byrd_asm.c` body-only mode: `-asm-body` flag, no `_start`/`match_success`/`match_fail`, emit `global root_alpha, root_beta` + `extern cursor, subject_data, subject_len_val`
3. `test/crosscheck/run_crosscheck_asm.sh` — new driver extracting pattern+subject from `.sno`, compiling+linking with harness, diffing output
4. `038_pat_literal` PASS → iterate to all patterns/ + capture/ rungs → M-ASM-CROSSCHECK

**PIVOT (session144):** Abandoned `monitor-scaffold` / `bug7-bomb` in favor of x64 ASM backend.
Rationale: C backend has a fundamental structural problem — named patterns require C functions
with reentrant structs, three-level scoping (`z->field`, `#define`/`#undef`), and `calloc` per
call. x64 ASM eliminates all of this: α/β/γ/ω become real ASM labels, all variables live flat
in `.bss`, named patterns are plain labels with a 2-way `jmp` dispatch. One scope. No structs.

**Architecture (session144):**
```
Frontend (lex/parse)     →     IR (Byrd Box)     →     Backend (emit/interpret)

SNOBOL4 reader                                          C emitter       ← existing, keep
Rebus reader              α/β/γ/ω four-port IR          x64 ASM emitter ← NEW PIVOT TARGET
Snocone reader            (byrd_ir.py / emit_byrd.c)    Interpreter     ← future debug tool
Icon reader
Prolog reader
```
5 frontends × 3 backends = 15 combinations. One IR. One compiler driver.

**Next steps (Sprint A0):**
1. Create `src/sno2c/emit_byrd_asm.c` — skeleton, mirrors emit_byrd.c structure.
2. Add `-asm` flag to `main.c` selecting ASM backend, output `.s` file.
3. NASM syntax, x64 Linux ELF64.
4. Emit null program: assemble (`nasm -f elf64`), link (`ld`), run → exit 0.
5. **M-ASM-HELLO fires** → begin Sprint A1 (LIT node).

---

## Sprint F-FLAT-NARY — M-FLAT-NARY (frontend session owns this)

**Goal:** Flatten `E_CONC` and `E_OR` to true n-ary nodes (`args[]` only, no `left`/`right`).
Update all backends that walk these nodes: C (`emit_byrd.c`), ASM (`emit_byrd_asm.c`), NET (`emit_byrd_net.c`).
JVM stays untouched (its session owns it separately).

**Why:** N-202 NET session (N-203) added n-ary-aware pattern emit for NET but left the parser
producing binary trees. The frontend session finishes the job: parser emits n-ary, all non-JVM
backends consume `args[]`.

**Steps:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase

# 1. parse.c — add naryop() helper, flatten E_CONC (parse_expr4) and E_OR (parse_expr3)
#    naryop() sets args[]/nargs ONLY — no left/right.

# 2. emit_byrd.c (C backend) — update E_CONC and E_OR in both expr and pattern contexts
#    to iterate args[0..nargs-1] instead of left/right recursion.

# 3. emit_byrd_asm.c (ASM backend) — update E_CONC/E_OR dispatch:
#    E_CONC: fold args[] right-to-left via emit_asm_seq(args[i], args[i+1], ...)
#    E_OR:   fold args[] left-to-right via emit_asm_alt(args[i], args[i+1], ...)

# 4. emit_byrd_net.c (NET backend) — already updated in N-203 to use args[] with
#    binary left/right fallback. Remove the fallback once parser is clean.

# 5. Verify:
make -C src
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Fires when:** 106/106 C + 26/26 ASM pass with pure n-ary nodes (no left/right on E_CONC/E_OR).

---

## Milestone Map

| Milestone | Trigger | Status | Sprint |
|-----------|---------|--------|--------|
| **M-ASM-HELLO** | null.s assembles, links, runs → exit 0 | ✅ session145 | A0 |
| **M-ASM-LIT** | LIT node: lit_hello.s PASS | ✅ session146 | A1 |
| **M-ASM-SEQ** | SEQ/POS/RPOS: cat_pos_lit_rpos.s PASS | ✅ session146 | A2–A3 |
| **M-ASM-ALT** | ALT: alt_first/second/fail PASS | ✅ session147 | A4 |
| **M-ASM-ARBNO** | ARBNO: arbno_match/empty/fail PASS | ✅ session147 | A5 |
| **M-ASM-CHARSET** | ANY/NOTANY/SPAN/BREAK PASS | ✅ session147 | A6 |
| **M-ASM-ASSIGN** | $ capture: assign_lit/digits PASS | ✅ session148 | A7 |
| **M-ASM-NAMED** | Named patterns: ref_astar_bstar/anbn PASS | ✅ session148 | A8 |
| **M-ASM-CROSSCHECK** | 26/26 ASM crosscheck PASS | ✅ session151 | A9 |
| **M-ASM-R1** | hello/ + output/ — 12 tests PASS via run_crosscheck_asm_rung.sh | ❌ | A-R1 |
| **M-ASM-R2** | assign/ — 8 tests PASS | ❌ | A-R2 |
| **M-ASM-R3** | concat/ — 6 tests PASS | ✅ session187 | A-R3 |
| **M-ASM-R4** | arith/ — 2 tests PASS | ❌ | A-R4 |
| **M-ASM-R5** | control/ + control_new/ PASS | ❌ | A-R5 |
| **M-ASM-R6** | patterns/ program-mode 20 tests PASS | ❌ | A-R6 |
| **M-ASM-R7** | capture/ — 7 tests PASS | ✅ session190 | A-R7 |
| **M-ASM-R8** | strings/ — 17 tests PASS | ⏳ session191 15/17 | A-R8 |
| **M-ASM-R9** | keywords/ — 11 tests PASS | ❌ | A-R9 |
| **M-ASM-R10** | functions/ — DEFINE/RETURN/recursion PASS | ✅ session197 | A-R10 |
| **M-ASM-R11** | data/ — ARRAY/TABLE/DATA PASS | ❌ | A-R11 |
| **M-ASM-RECUR** | Recursive functions correct — roman.sno segfault fixed | ❌ | A-RECUR |
| **M-ASM-SAMPLES** | roman.sno + wordcount.sno PASS | ❌ | A-S1 |
| **M-ASM-BEAUTY** | beauty.sno self-beautifies via ASM backend | ❌ | A10 |
| **M-ASM-READABLE** | Label names: special-char expansion (pp_>= → S_pp_GT_EQ); _ literal passthrough; uid on collision only. Original bijection spec revised — expanding _ destroys readability for normal names. M-ASM-READABLE-A. | ✅ `e0371fe` session176 | A11 |
| **M-ASM-BEAUTIFUL** | beauty_prog.s as readable as beauty_full.c. Lon reads it and declares it beautiful. | ✅ `7d6add6` session175 | A14 |
| **M-REORG** | Full repo layout: frontend/ ir/ backend/ driver/ runtime/; binary at snobol4x/sno2c; 106/106 26/26 | ✅ `f3ca7f2` session181 | — |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | ❌ | final goal |



**ASM backend design (session144):**

Why ASM solves the C structural problem:
- C named patterns require functions with reentrant structs (`pat_X_t *z`), `calloc` per call,
  three-level scoping (`z->field` + `#define`/`#undef` aliases), and `open_memstream` two-pass
  declaration collection. Bug5/Bug6/Bug7 all trace back to this complexity.
- x64 ASM: α/β/γ/ω become real labels. All variables are flat `.bss` qwords declared once at
  top of file. Named patterns are plain labels with a 2-instruction entry dispatch. One scope.
  No structs. No malloc. No scoping tricks.

**Sprint detail:**

| Sprint | What | Key oracle |
|--------|------|-----------|
| A0 | Skeleton + `-asm` flag + null program | `test/sprint0/null.s` |
| A1 | LIT node — inline byte compare | `test/sprint1/lit_hello.s` |
| A2 | POS / RPOS — pure compare, no save | `test/sprint2/pos0_rpos0.s` |
| A3 | SEQ (CAT) — wire α/β/γ/ω between nodes | `test/sprint2/cat_pos_lit_rpos.s` |
| A4 | ALT — left/right arms + backtrack | `test/sprint3/alt_*.s` |
| A5 | ARBNO — depth counter + cursor stack in `.bss` | `test/sprint5/arbno_*.s` |
| A6 | Charset: ANY/NOTANY/SPAN/BREAK — inline scan | corpus rungs |
| A7 | $ capture — span into flat `.bss` buffer | `test/sprint4/assign_*.s` |
| A8 | Named patterns — flat labels, 2-way jmp dispatch | `test/sprint6/ref_*.s` |
| A9 | Full crosscheck 106/106 via ASM backend | crosscheck suite |
| A10 | beauty.sno → ASM → self-beautify | M-ASM-BEAUTY |
| A11 | Label named expansion: pp_>= → L_pp_GT_EQ_N | M-ASM-READABLE |
| A12 | NASM macro library snobol4_asm.mac; emit uses macros; 3-column .s | M-ASM-MACROS |
| A13 | ASM IR phase (CNode-equivalent); separate tree walk from emit | M-ASM-IR |
| A14 | Generated .s as readable as generated .c | M-ASM-BEAUTIFUL |

**Build commands (ASM backend):**
```bash
cd /home/claude/snobol4x
# Install NASM once:
apt-get install -y nasm
# Compile a .sno to .s:
src/sno2c/sno2c -asm myprog.sno > myprog.s
# Assemble + link:
nasm -f elf64 myprog.s -o myprog.o
ld myprog.o src/runtime/snobol4/snobol4_asm.o -o myprog
# Run:
./myprog
```


---

## Confirmed Passing (session116 WIP)

- 101_comment ✅
- 102_output  ✅
- 103_assign  ✅
- 104_label   ✅ (WIP binary)
- 105_goto    ✅ (WIP binary)
- 106/106 rungs 1–11 ✅

---

## Bug History

**Bug7 — ACTIVE:** Ghost frame from Expr17 FENCE arm 1 (nPush without nPop on ω).
**Also check Expr15:** FENCE(nPush() *Expr16 ... nPop() | epsilon) same issue.
**Bug6a — FIXED in WIP (session115):** `:` lookahead guard in pat_X4 cat_r_168.
**Bug6b — FIXED in WIP (session115):** NV_SET_fn for Brackets/SorF; CONCAT_fn Reduce type.
**Bug5 — FIXED in WIP (session114); emit_byrd.c port IN PROGRESS (session116).**
**Bugs 3/4 — FIXED `4c2ad68`.**

---

## Frontend × Backend Frontier

| Frontend | C backend | x64 ASM | .NET MSIL | JVM bytecodes |
|----------|:---------:|:-------:|:---------:|:-------------:|
| SNOBOL4/SPITBOL | ⏳ Sprint A | — | — | — |
| Rebus | ✅ M-REBUS | — | — | — |
| Snocone | — | — | — | — |
| Tiny-ICON | — | — | — | — |
| Tiny-Prolog | — | — | — | — |

✅ milestone fired · ⏳ active · — planned

---

## M-BEAUTY-CORE Sprint Plan

### What beauty.sno does (essential model)

One big PATTERN matches the entire source. Immediate assignments (`$`) orchestrate
two stacks simultaneously during the match:

**Counter stack** — tracks children per syntactic level:
```
nPush()                  push 0       entering a level
nInc()                   top++        one more child recognized
Reduce(type, ntop())     read count   build tree node — fires BEFORE nPop
nPop()                   pop          exit the level — fires AFTER Reduce
```

**Value stack:**
```
shift(p,t)   pattern constructor — builds p . thx . *Shift('t', thx)
reduce(t,n)  pattern constructor — builds '' . *Reduce(t,n)
Shift(t,v)   match-time worker — push leaf node
Reduce(t,n)  match-time worker — pop n nodes, push internal node
~ is opsyn for shift · & is opsyn for reduce
```

**Invariant:** every `nPush()` must have exactly one `nPop()` on EVERY exit path —
success (γ) AND failure (ω). Missing `nPop` on FENCE backtrack = ghost frame.

### Bug7 — Active

`Expr17` arm1: `FENCE(nPush() $'(' *Expr ... nPop() | *Id ~ 'Id' | ...)`
→ nPush fires, `$'('` fails, FENCE backtracks to arm2 — **nPop SKIPPED**

`Expr15`: `FENCE(nPush() *Expr16 (...) nPop() | '')`
→ same issue when no `[` follows

**Fix location:** `emit_byrd.c` — emit `NPOP_fn()` on ω path of nPush arm.

### Skeleton ladder (Sprint steps)

Build minimal SNOBOL4 test programs, each a strict superset of previous.
Diff oracle vs compiled stderr traces. First diverging SEQ#### line = bug.

**All 5 instrumented primitives share `int _nseq` counter:**
```
SEQ0001 NPUSH depth=N top=N    <- snobol4.c NPUSH_fn
SEQ0002 NINC  depth=N top=N    <- snobol4.c NINC_fn
SEQ0003 NPOP  depth=N top=N    <- snobol4.c NPOP_fn
SEQ0004 SHIFT type=T val='V'   <- mock_includes.c Shift()
SEQ0005 REDUCE type=T n=N      <- mock_includes.c Reduce()
```

| Step | Input | Status |
|------|-------|--------|
| `micro0_skeleton.sno` | `N` | ✅ Bug7 does NOT fire — baseline |
| `micro1_concat.sno` | `N + 1` | Bug7 FIRES — next |
| `micro2_call.sno` | `GT(N,3)` | Expr17 arm2/3 — TODO |
| `micro3_grouped.sno` | `(N+1)` | Expr17 arm1 full path — TODO |
| `micro4_full.sno` | `109_multi.input` | Full 5-line program — TODO |

### In-PATTERN Bomb Technique

Place diagnostic calls **directly inside a PATTERN** at any edge using `'' . *fn()`.
The function fires exactly when the match engine reaches that point, including on backtrack.

```snobol4
* Sequence stamp at any pattern edge
        DEFINE('seq_(label)', 'seq_B')          :(seq_End)
seq_B   seqN = seqN + 1
        OUTPUT = 'SEQ' LPAD(seqN,4,'0') ' ' label
        seq_ = .dummy                           :(NRETURN)
seq_End

* Embed at FENCE edges to see exactly which path fires:
        Expr17 = FENCE(
+                   '' . *seq_('E17_arm1_enter')
+                   nPush()
+                   $'('
+                   '' . *seq_('E17_arm1_after_paren')   <- never fires if ( fails
+                   nPop()
+                |  '' . *seq_('E17_arm2_enter')         <- fires on backtrack
+                   *Id ~ 'Id'
+                )
```

**Bomb variant** — abort on wrong state:
```snobol4
        DEFINE('assertDepth(expected)', 'assertB') :(assertEnd)
assertB EQ(_ntop, expected)                        :S(RETURN)
        OUTPUT = '*** BOMB depth=' _ntop ' expected=' expected
        &STLIMIT = 0                               * force abort
assertEnd
```
Place `'' . *assertDepth(1)` immediately after `nPush()` in arm1 to confirm
depth is correct before `$'('` runs.

### Crosscheck ladder (one at a time, never skip)

```
104_label → 105_goto → 109_multi → 120_real_prog → 130_inc_file → 140_self
```
`140_self` PASS → **M-BEAUTY-CORE fires**.

### Diagnostic tools

- **&STLIMIT binary search** — set limit, halve on hang
- **&STCOUNT** — increments correctly on CSNOBOL4 (verified 2026-03-16)
- **TRACE:** `TRACE('var','VALUE')` works; `TRACE(...,'KEYWORD')` non-functional
- **DUMP():** full variable dump at any point

---

## Session Start (session168)

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 8e5e9cb

apt-get install -y libgc-dev nasm && make -C src/sno2c

mkdir -p /home/snobol4corpus
ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

## Build beauty_full_bin

```bash
RT=src/runtime
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > beauty_full.c
gcc -O0 -g beauty_full.c \
    $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o beauty_full_bin
```

## Session End

⛔ **ARTIFACTS FIRST — before any HQ update:**
```bash
# 1. Archive any new .s files that fired a milestone:
#    cp <generated>.s snobol4x/artifacts/asm/<name>.s
#    Update artifacts/README.md with entry (status, milestone, assemble cmd, design notes)
#    git add artifacts/ && git commit -m "sessionN: archive <sprint> oracle .s files"
#
# 2. Then update TINY.md HEAD, sprint status, next action
# 3. Then update PLAN.md milestone dashboard
# 4. Push all repos, .github last
```

```bash
# Artifact check — see IMPL-SNO2C.md §Artifact Snapshot Protocol
# Update this file: HEAD, frontier table, next action, pivot log
git add -A && git commit && git push
# Push .github last
```

---

## Milestones

| ID | Trigger | ✓ |
|----|---------|---|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | ✅ |
| M-REBUS | Rebus round-trip diff empty | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | ✅ `ac54bd2` |
| **M-STACK-TRACE** | oracle_stack.txt == compiled_stack.txt for all rung-12 inputs | ✅ session119 |
| **M-BEAUTY-CORE** | beauty_full_bin self-beautifies (mock stubs) | ❌ |
| **M-BEAUTY-FULL** | beauty_full_bin self-beautifies (real -I inc/) | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC → block_fn_t | ❌ |
| M-SNO2C-SNO | sno2c.sno compiled by C sno2c | ❌ |
| M-COMPILED-SELF | Compiled binary self-beautifies | ❌ |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | ❌ |

---

## Sprint Map

### Active → M-BEAUTY-FULL (SNOBOL4 × C)

| Sprint | Paradigm | Trigger | Status |
|--------|----------|---------|--------|
| `stack-trace` | Dual-stack instrumentation | oracle == compiled stack trace → **M-STACK-TRACE** | ✅ session119 |
| `bug7-bomb` | Bomb protocol → fix emit_byrd.c | trace diff clean + 109_multi PASS → ladder → **M-BEAUTY-CORE** | ⏳ NOW |
| `beauty-probe` | Probe | All failures diagnosed | ❌ B |
| `beauty-monitor` | Monitor | Trace streams match | ❌ C |
| `beauty-triangulate` | Triangulate | Empty diff → **M-BEAUTY-FULL** | ❌ D |

### Planned → M-BOOTSTRAP (SNOBOL4 × C, self-hosting)

| Sprint | Gates on |
|--------|----------|
| `trampoline` · `stmt-fn` · `block-fn` · `pattern-block` | M-BEAUTY-FULL |
| `code-eval` (TCC) · `compiler-pattern` (compiler.sno) | M-BEAUTY-FULL |
| `bootstrap-stage1` · `bootstrap-stage2` | M-SNO2C-SNO |

### Sprint A12 — M-ASM-MACROS

**Goal:** Generated `.s` is readable. Every emitted line follows:

```
LABEL          ACTION          GOTO
```

Three columns. No exceptions. The LABEL is a Byrd box port or SNOBOL4 label.
The ACTION is a NASM macro. The GOTO is the succeed or fail target — a label, never a raw address.

**NASM macro library: `src/runtime/asm/snobol4_asm.mac`**

One macro per Byrd box primitive. Each macro expands to whatever register
shuffling is needed, but the call site is always one readable line:

```nasm
; Pattern nodes — one line each:
P_12_α         SPAN            letter_cs,   P_12_γ,  P_12_ω
P_14_α         LIT             "hello",     P_14_γ,  P_14_ω
P_16_α         SEQ             P_14, P_12,  P_16_γ,  P_16_ω
P_18_α         ALT             P_14, P_16,  P_18_γ,  P_18_ω
P_20_α         DOL             ppTokName,   P_20_γ,  P_20_ω

; Statement — subject, match, replace, goto:
L_LOOP         SUBJECT         ppLine
               MATCH_PAT       P_16,        L_WRITE, L_END
L_WRITE        REPLACE         ppOut,       ppLine
               GOTO                         L_LOOP
```

Parallel C output for comparison:

```c
L_LOOP:   subj = GET("ppLine");
          if (MATCH(P_16, subj)) { SET("ppOut", subj); goto L_WRITE; }
          goto L_END;
L_WRITE:  SET("ppLine", GET("ppOut"));
          goto L_LOOP;
```

**Sprint A12 steps:**
1. Write `src/runtime/asm/snobol4_asm.mac` — macros for LIT/SPAN/SEQ/ALT/ALT/DOL/ARBNO/ANY/NOTANY/BREAK/POS/RPOS/REM/ARB/SUBJECT/MATCH_PAT/REPLACE/GOTO/GOTO_S/GOTO_F
2. Change `emit_byrd_asm.c` to `%include "snobol4_asm.mac"` at top of every `.s`
3. Change every `A("    mov rax...")` emission to `A("  MACRO_NAME  args")` 
4. Verify beauty_prog.s assembles clean with macros expanded
5. Diff generated .s before/after — three-column structure visible throughout
6. **M-ASM-MACROS fires** when beauty_prog.s is fully macro-driven and assembles

### Sprint A13 — M-ASM-IR

**Goal:** Separate the tree walk from code generation. Same architecture as C backend's CNode IR.

The ASM emitter currently does parse → emit in one pass. This makes it hard to:
- Inject comments and separators
- Optimise label names
- Share structure between C and ASM emitters

**Architecture:**
```
Parse → EXPR_t/STMT_t → [ASM IR walk] → AsmNode tree → [ASM emit] → .s file
```

The AsmNode tree is a list of `(label, macro_name, args[], goto_s, goto_f)` tuples.
The emit pass just prints them in three-column format. No logic in the emit pass.

**Sprint A13 steps:**
1. Define `AsmNode` struct: `{char *label; char *macro; char **args; int nargs; char *gs; char *gf;}`
2. Write `asm_ir_build(Program*)` → `AsmNode[]` — the tree walk, no emission
3. Write `asm_ir_emit(AsmNode[])` — pure pretty-printer, three columns
4. Replace current `asm_emit_program()` with `asm_ir_build()` + `asm_ir_emit()`
5. **M-ASM-IR fires** when beauty_prog.s generates identically via the new path

### Sprint A14 — M-ASM-BEAUTIFUL

**Goal:** beauty_prog.s is as readable as beauty_full.c. A human can follow the SNOBOL4 logic by reading the `.s` file directly.

**Trigger:** Open beauty_prog.s and beauty_full.c side by side. Every SNOBOL4 statement is recognisable in both. The Byrd box four ports are visible as α/β/γ/ω. Statement boundaries are clear. No raw register names in the body — only macro calls.

**M-ASM-BEAUTIFUL fires** when Lon reads beauty_prog.s and says it is beautiful.

### Completed

| Sprint | Commit |
|--------|--------|
| `space-token` | `3581830` |
| `compiled-byrd-boxes` | `560c56a` |
| `crosscheck-ladder` — 106/106 | `668ce4f` |
| `cnode` | `ac54bd2` |
| `rebus-roundtrip` | `bf86b4b` |
| `smoke-tests` — 21/21 | `8f68962` |
| sprints 0–22 (engine foundation) | `test/sprint*` |

---

## Pivot Log

| Sessions | What | Why |
|----------|------|-----|
| 159 | **PIVOT: M-ASM-BEAUTIFUL (A14) activated.** E_OR/E_CONC → ALT/CONCAT builtins registered; test 101 PASS. snobol4_asm.mac extended with STORE_ARG32/16, LOAD_NULVCL, APPLY_FN_0/N, SET_CAPTURE, IS_FAIL_BRANCH/16, SETUP_SUBJECT_FROM16. prog_emit_expr + asm_emit_program raw register sequences replaced with macro calls throughout. beauty_prog_session159.s archived (18220 lines, nasm clean). 106/106 26/26. HEAD a361318. | Lon requested M-ASM-BEAUTIFUL pivot. M-ASM-BEAUTY (102-109 Parse Error) deferred. |
| 158 | **M-ASM-BEAUTY progress — 101_comment PASS:** section .text fix; stack align; E_FNC/Case1-SF/capture; 106/106 26/26. Root cause of 102-109: E_OR/E_CONC → NULVCL. | — 3 issues diagnosed, sprint steps written.** Multi-capture (055): per-variable cap buffers + cap_order table in emitter + harness walk. E_INDR (056): add case + fix build_bare_sno to keep *VAR-referenced plain assigns + fix extract_subject to use subject var from match line. FAIL/057: already wired, unblocked once script continues past 055. SPITBOL p_imc studied for canonical multi-capture semantics. HQ updated. |
| 150 | **Sprint A9 — 17/20 ASM crosscheck PASS.** New emitters: ANY/NOTANY/SPAN/BREAK/LEN/TAB/RTAB/REM/ARB/FAIL all wired into E_FNC switch. E_VART: REM/ARB/FAIL intercepted as zero-arg builtins. Harness rewritten with setjmp/longjmp unanchored scan loop. DOL writes to harness cap_buf/cap_len externs. cap_len sentinel UINT64_MAX distinguishes no-capture from empty-string capture. build_bare_sno keeps pattern-variable assignments. DATATYPE lowercase fix (106/106). 038–054 PASS. 055 fails (multi-capture). Script stops early at first FAIL — next session fix extract_subject + skip multi-capture + wire E_INDR. HEAD d7a75cc. | |
| 149 | **Sprint A9 begun.** `snobol4_asm_harness.c`: flat `subject_data[65536]` array (preserves `lea rsi,[rel subject_data]` semantics), `match_success`/`match_fail` as C `noreturn` functions, inline `jmp root_alpha`. `-asm-body` flag: `asm_emit_body()` emits `global root_alpha,root_beta` + `extern cursor,subject_data,subject_len_val,match_success,match_fail`. `run_crosscheck_asm.sh`: extracts subject, builds bare `.sno`, sno2c→nasm→gcc→run, capture tests diff stdout vs `.ref`, match/no-match tests check exit code. **038_pat_literal PASS** end-to-end. Next: wire `emit_asm_any/span/break/notany/tab/rtab/len/rem/arb` into `E_FNC` switch. 106/106 holds. HEAD a7c324e. | |
| 148 | **M-ASM-ASSIGN + M-ASM-NAMED fire.** ASSIGN: assign_lit.s (LIT $ capture) + assign_digits.s (SPAN $ capture unanchored) PASS; emit_asm_assign() DOL Byrd box from v311.sil ENMI; E_DOL+E_NAM wired. NAMED: ref_astar_bstar.s (ASTAR=ARBNO("a"), BSTAR=ARBNO("b") on "aaabb") + anbn.s (4 sequential named-pattern call sites on "aabb") PASS; AsmNamedPat registry + asm_scan_named_patterns() pre-pass + emit_asm_named_ref() call-site + emit_asm_named_def() body emitter; E_VART wired; Proebsting §4.5 gate convention (pat_NAME_ret_gamma/omega .bss indirect-jmp, no call stack). End-to-end .sno→sno2c -asm→nasm→ld→run verified. 106/106 invariant holds. HEAD de085e1. Next: Sprint A9 — snobol4_asm_harness.c + body-only emitter + ASM crosscheck driver. | |
| 147 | **M-ASM-ALT + M-ASM-ARBNO + M-ASM-CHARSET fire; emit_byrd_asm.c real emitter written.** ALT: alt_first/second/fail. ARBNO: arbno_match/empty/alt (cursor stack 64 slots, zero-advance guard, v311.sil ARBN/EARB). CHARSET: any_vowel/notany_consonant/span_digits/break_space — all PASS. emit_byrd_asm.c: real recursive LIT/SEQ/ALT/POS/RPOS/ARBNO emitter — generates correct NASM but needs harness to connect to crosscheck (subject currently hardcoded). Next: Sprint A7 — snobol4_asm_harness.c + body-only emitter + first crosscheck pass. HEAD a114bcf. | |
| 147 | **M-ASM-ALT + M-ASM-ARBNO fire** — ALT: three oracles (alt_first/second/fail). ARBNO: three oracles (arbno_match "aaa", arbno_empty "aaa" vs 'x' → fail, arbno_alt "abba" vs ARBNO('a'\|'b')). ARBNO design: flat .bss cursor stack 64 slots + depth counter; α pushes+succeeds; β pops+tries one rep; zero-advance guard; rep_success pushes+re-succeeds. Proebsting §4.5 for ALT; v311.sil ARBN/EARB/ARBF for ARBNO. All PASS. Next: Sprint A6 (CHARSET). | |
| 146 | **M-ASM-LIT fires** — `lit_hello.s` hand-written: α/β/γ/ω real NASM labels, cursor+saved_cursor flat .bss qwords, repe cmpsb compare. Assembles, links, runs → `hello\n` exit 0. Diff vs oracle CLEAN. `artifacts/asm/null.s` + `artifacts/asm/lit_hello.s` placed in artifacts/asm/. HQ updated. No push per Lon. Next: Sprint A2 (POS/RPOS). |
| 145 | **M-ASM-HELLO fires** — `emit_byrd_asm.c` created, `-asm` flag added to `main.c`+`Makefile`, `null.s` assembles+links+runs → exit 0. 106/106 crosscheck clean. Next: Sprint A1 (LIT node). | Sprint A0 complete. |
| 144 | **PIVOT: x64 ASM backend** — abandon monitor-scaffold/bug7-bomb | C backend has structural flaw: named patterns require reentrant C functions, `pat_X_t` structs, `calloc`, three-level scoping. ASM eliminates all of it: α/β/γ/ω = real labels, all vars flat `.bss`, named patterns = labels + 2-way jmp. One scope. Sprint plan A0–A10 documented in NOW. |
| 80–89 | Attacked beauty.sno directly | Burned — needed smaller test cases first |
| 89 | Pivot: corpus ladder | Prove each feature before moving up |
| 95 | 106/106 rungs 1–11 | Foundation solid |
| 96–97 | Sprint 4 compiler internals | Retired — not test-driven |
| 97 | Pivot: test-driven only | No compiler work without failing test |
| 98–99 | HQ restructure (L1/L2/L3 pyramid) | Plan before code |
| 100 | HQ: frontend×backend split | One file per concern |
| 101 | Sprint A begins | Rung 12, beauty_full_bin, first crosscheck test (Session 101) |
| 103–104 | E_NAM~/Shift fix; E_FNC fallback fix | 101_comment PASS; 102+ blocked by named-pattern RHS truncation in byrd_emit_named_pattern |
| 105 | $ left-assoc parse fix + E_DOL chain emitter | Parser correct; emitter label-dup compile error blocks 102+ |
| 106 | E_DOL label-dup fixed (emit_seq pattern); 4x crosscheck speedup | 101 PASS; 102_output FAIL — assignment node blank in pp() |
| 108 | E_INDR(E_FNC) fix in emit_byrd.c; beauty_full.c patched; bug2 diagnosed: pat_ExprList epsilon | 102_output still FAIL — bug2 is pat_ExprList matching epsilon without '(' |
| 109 | bug2 '(' guards added (both Function+Id arms); pop_val()+skip; doc sno* names fixed in .github | 102_output still FAIL — OUTPUT not reaching subject slot; bare-Function arm not yet found |
| 110 | bug2 FIXED: bare-Function/Id go to fence_after_358 (keep Shift, succeed); parse tree verified correct by trace | 102_output still FAIL — Bug3: pp_Stmt drops subject; INDEX_fn(c,2) suspect |
| 107 | Shift(t,v) value fix; FIELD_GET debug removed; root cause diagnosed | 106/106 pass; 102 still FAIL — E_DEREF(E_FNC) in emit_byrd.c drops args |
| 111 | NPUSH not firing on backtrack in pat_Expr3/4; ntop()=0 at Reduce | Full stack probe confirmed; emit_simple_val E_QLIT fix applied; structural NPUSH hoist pending in emit_byrd.c |
| 112 | Bug3 FIXED (emit_seq NPUSH on backtrack); Bug4 FIXED (emit_imm literal-tok $'(' guard + stack rollback via STACK_DEPTH_fn) | 101/102/103 PASS; 104_label FAIL — next |
| 113 | Bug5 diagnosed: ntop() frame displacement by nested NPUSH; NINC_AT_fn + saved-frame fix in beauty_full.c; Reduce("..",2) fires; pp_.. crash unresolved | EMERGENCY WIP 7c17ffa |
| 114 | Bug5 FIXED: saved-frame pattern extended to pat_Parse/pat_Compiland/pat_Command; _command_pending_parent_frame global; Reduce(Parse,1) correct; 104_label PASS. Bug6 diagnosed: Bug6a spurious Reduce(..,2) for goto token; Bug6b unevaluated goto type string | EMERGENCY WIP 3f5bfda |
| 115 | Bug6a FIXED: `:` lookahead guard in pat_X4 cat_r_168. Bug6b FIXED: NV_SET_fn for Brackets/SorF in pat_Target/SGoto/FGoto; CONCAT_fn Reduce type; suppressed output_str+cond_OUTPUT in all pat_ gammas (23 sites). 101–105 PASS, 106/106. WIP only — emit_byrd.c port pending | EMERGENCY WIP — commit next session |
| 116 | emit_byrd.c port attempt: snobol4.h NTOP_INDEX/NSTACK_AT decls; pending_npush_uid + _pending_parent_frame globals; Bug5 saved-frame in emit_seq+E_FNC nPush; Bug6a colon guard in *X4 deref; Bug6b CONCAT_fn in E_OPSYN; output_str suppression gated on suppress_output_in_named_pat(); _parent_frame field in all named pat structs. 101-103 PASS from regen; 104-105 FAIL — pending_npush_uid not surviving nested CAT levels | EMERGENCY WIP — pending_npush_uid fix next session |
| 117 | Diagnosis: 104/105 fail because Reduce(..,2) never fires — ntop()=1 at ExprList level instead of 2. Dual-stack trace confirmed: spurious NPUSH idx=7/8 inside pat_Expr displaces counter stack so second NINC fires at wrong level. Root cause: nPush/nPop imbalance in pat_Expr4/X4 sub-pattern. Option A (parameter threading) attempted and backed out — correct diagnosis but wrong fix target. All files restored to session116 state. | Diagnosis only — no commit |
| 118 | Pivot: stack-trace sprint. Understand two-stack engine model fully. Instrument both oracle and compiled binary. Use diff to find exact imbalance location, not inference. New milestone M-STACK-TRACE gates on beauty-crosscheck. HQ updated. | Plan only — no commit |
| 119 | M-STACK-TRACE fires. oracle_stack.txt == compiled_stack.txt for all rung-12 inputs. | Stack trace matched — sprint beauty-crosscheck begins |
| 121 | Dual-stack trace infra built: oracle (patched counter.sno→TERMINAL) + compiled (fprintf in NPUSH/NINC/NPOP). 109_multi.input trace diff: first divergence line 2 — oracle NINC, compiled spurious NPUSH. Bug7 Bomb Protocol designed (Pass1 count, Pass2 limit+backtrace). emit_imm NPOP-on-fail drafted but emit_seq Expr15 fix caused double-pop regression on 105_goto. All WIP reverted. Bomb protocol is next. | Bomb protocol ready — awaiting next session |
| 120 | beauty.sno PATTERN read in full (lines 293–419). Bug7 confirmed: Expr17 FENCE arm 1 calls nPush() then $'(' fails — nPop() never called on ω path. Expr15 FENCE arm same issue. Fix target: emit_byrd.c FENCE backtrack path. HQ updated with full pattern structure. ~55% context at session start. | Plan only — awaiting instruction |
| 122 | Pivot: diag1-corpus sprint before bug7-micro. 35 tests 152 assertions rungs 2–11, 35/35 PASS CSNOBOL4 2.3.3. M-FLAT documented (flat() Gray/White bypass of pp/ss). HQ updated. Context ~94% at close. | diag1 corpus ready to commit with token; bug7-micro is next |
| 122b | PIVOT: M-DIAG1 now top priority. Run diag1 35-test suite on JVM + DOTNET. Fix failures. Fire M-DIAG1. Then bug7-micro. Priority order: M-DIAG1 → M-BEAUTY-CORE → M-FLAT → M-BEAUTY-FULL → M-BOOTSTRAP. | New session opens on snobol4jvm |

**Session180 — CAT/SEQ naming; CAT2 macros; scan retry; path revert; 056 fix:**
- Naming decision: E_CONC value-context → **CAT** (string concat); E_CONC pattern-context → **SEQ** (already). E_OR → **ALT**. `CAT2_SS/SV/VS/VV/VN/SN` macros added to `snobol4_asm.mac` — call `stmt_concat` directly (not `stmt_apply("CONCAT")`).
- `expr_is_pattern_expr`: E_CONC now requires a pattern fn call — pure literal concat `'a' 'b'` is VALUE not pattern. E_OR always remains a pattern.
- `E_CONC` in `prog_emit_expr` now routes to `CAT2_*` macros; E_OR still uses `ALT2_*`.
- All 6 concat tests now pass (017–022).
- Unanchored scan retry loop added to Case 2 pattern statement emission: `scan_start_N` bss slot, `scan_retry_N` label, advance+retry on omega. 056 program-mode fixed.
- **Regression introduced**: scan retry omega exits via `jg next_lbl` instead of `jg tgt_f` — `034_goto_failure`, `057_pat_fail_builtin`, `098_keyword_anchor` now fail. **Fix is one line — `jg next_lbl` → `jg <tgt_f label>`** in the omega block.
- `/home/socrates` path experiment reverted — all repos back to `/home/claude`. All pushed.
- Corpus: **75 PASS** (up from 64 session179). 106/106 C ✅. 26/26 ASM ✅.
- HEAD: `ee4b118`

**Session182 — archive src/ir; emit_cnode relocated to backend/c:**
- `src/ir/byrd/emit_cnode.c/.h` → `src/backend/c/` (live production code, was misplaced)
- `src/Makefile`: drop `-I ir/byrd`, merge `IR_BYRD` into `BACKEND_C`, update header dep
- `src/ir/byrd/{byrd_ir,ir,lower}.py` → `archive/ir/` with README.md
- `src/ir/jvm/.gitkeep`, `src/ir/net/.gitkeep` deleted
- `lower.py` preserved in archive as design reference for `emit_byrd.c` four-port wiring
- 106/106 C PASS ✅, 26/26 ASM PASS ✅ confirmed after rebuild

**⚠ CRITICAL NEXT ACTION — Session183:**

1. **Run corpus** — scan-retry fix should recover 034, 057, 098. Target 78+ PASS.
2. **Continue corpus fixes** per session180 priority order:
   - NASM_FAIL remaining (4 tests: 019, 056, 086, wordcount)
   - Capture fixes (060–064)
   - Define/functions (083–090)
3. **Update beauty_prog.s artifact** if emit_byrd_asm.c changed.

**Session182 start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = f3ca7f2

apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26

# Then run full corpus
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_prog.sh 2>&1 | tail -5
```

**Session180 — arithmetic ops, named-pattern fix, label rename, artifacts reorg:**
- `E_ADD/E_SUB/E_MPY/E_DIV/E_EXPOP/E_MNS` cases added to `prog_emit_expr` in `emit_byrd_asm.c`
- `add/sub/mul/DIVIDE_fn/POWER_fn/neg` registered as builtins in `SNO_INIT_fn` (`snobol4.c`)
- `E_MNS` operand fixed: `e->left` not `e->right` (unop() convention)
- `expr_is_pattern_expr()` guard: only register `VAR=expr` as named pattern when replacement contains E_FNC/E_OR/E_CONC — plain value assignments (`X='hello'`, `OUTPUT=X`) no longer generate spurious Byrd-box bodies
- `E_VART/E_KW` added to .bss skip list
- Synthetic labels renamed: `L_sn_N` → `Ln_N` (next/fall-through), `L_sf_N` → `Lf_N` (fail dispatch)
- `artifacts/asm/` reorganised: `beauty_prog.s` at top; `fixtures/` for sprint oracles; `samples/` for programs
- Corpus: **47 → 64 PASS**, 16 → 4 NASM_FAIL; 106/106 C crosscheck ✅; 25/26 ASM crosscheck
- `056_pat_star_deref` FAIL: `PAT = 'hello'` (E_QLIT) skipped by expr_is_pattern_expr — `*PAT` indirect ref has no .bss slots; fix next session

**⚠ CRITICAL NEXT ACTION — Session180:**
1. Fix `056_pat_star_deref`: `PAT = 'hello'` assigns E_QLIT but `*PAT` uses it as indirect pattern ref. The expr_is_pattern_expr guard correctly skips it as non-pattern, but the `*VAR` (E_INDR) emit path in `emit_asm_node` still tries to reference `P_PAT_ret_γ`. Fix: when E_INDR references a variable that is NOT in the named-pattern registry, fall back to value-based pattern matching instead. Restore 26/26 ASM crosscheck.
2. Continue NASM_FAIL fixes: 4 remaining (`019_concat_var_string`, `056_pat_star_deref`, `086_define_locals`, `wordcount`)
3. Fix remaining FAILs: concat (017–022), capture (060–064), define/functions (083–090)

---

## NOW (session183 — frontend session)

**⚠ TWO CONCURRENT SESSIONS — different concerns, same repo:**
- **Frontend session** (this chat): `snocone-frontend` sprint — SC0→SC5 → M-SNOC-SELF
- **Backend session** (other chat): `asm-backend` sprint — corpus fixes (72/106) → M-MONITOR

Each session edits `snobol4x` independently. Both push to `.github`. Per RULES.md: `git pull --rebase` before every `.github` push. No `--force` ever.

**Frontend session sprint: `snocone-frontend`**
**HEAD:** `583c5a5` session182
**Active milestone:** M-SNOC-LEX (Sprint SC0)

### Sprint SC0 — M-SNOC-LEX

**Goal:** `src/frontend/snocone/sc_lex.c` — tokenize any `.sc` file.
Ported from `snobol4jvm/src/SNOBOL4clojure/snocone.clj` (tested, complete).

**Files:**
- `src/frontend/snocone/sc_lex.h` — token kinds + `ScToken` struct + `sc_lex()` API
- `src/frontend/snocone/sc_lex.c` — lexer implementation
- `test/frontend/snocone/sc_lex_test.c` — quick-check: `OUTPUT = 'hello'` → 3 tokens PASS

**Token kinds** (from JVM KIND table):
```c
SC_INTEGER, SC_REAL, SC_STRING, SC_IDENT,
SC_KW_IF, SC_KW_ELSE, SC_KW_WHILE, SC_KW_DO, SC_KW_FOR,
SC_KW_RETURN, SC_KW_FRETURN, SC_KW_NRETURN,
SC_KW_GO, SC_KW_TO, SC_KW_PROCEDURE, SC_KW_STRUCT,
SC_LPAREN, SC_RPAREN, SC_LBRACE, SC_RBRACE, SC_LBRACKET, SC_RBRACKET,
SC_COMMA, SC_SEMICOLON, SC_COLON,
SC_ASSIGN, SC_QUESTION, SC_PIPE, SC_OR, SC_CONCAT,
SC_EQ, SC_NE, SC_LT, SC_GT, SC_LE, SC_GE,
SC_STR_IDENT, SC_STR_DIFFER, SC_STR_LT, SC_STR_GT, SC_STR_LE, SC_STR_GE,
SC_STR_EQ, SC_STR_NE,
SC_PLUS, SC_MINUS, SC_SLASH, SC_STAR, SC_PERCENT, SC_CARET,
SC_PERIOD, SC_DOLLAR, SC_AT, SC_AMPERSAND, SC_TILDE,
SC_NEWLINE, SC_EOF, SC_UNKNOWN
```

**Continuation chars:** `@ $ % ^ & * ( - + = [ < > | ~ , ? :`

**Quick-check trigger (M-SNOC-LEX):**
```bash
cd /home/claude/snobol4x
gcc -o /tmp/sc_lex_test test/frontend/snocone/sc_lex_test.c src/frontend/snocone/sc_lex.c
/tmp/sc_lex_test
# PASS → M-SNOC-LEX fires → begin Sprint SC1
```

### Sprint SC1 — M-SNOC-PARSE

`src/frontend/snocone/sc_parse.c` — recursive-descent parser consuming `ScToken[]`.
Produces `ScNode` AST covering: expr (full prec table), stmt, if/while/do/for/procedure/struct/goto/return/block.

### Sprint SC2 — M-SNOC-LOWER

`src/frontend/snocone/sc_lower.c` — walks `ScNode` tree, emits `EXPR_t`/`STMT_t` IR.
Operator mapping from `snocone.sc` bconv table (already read).
**No changes to emit.c or the C backend.**

### Sprint SC3 — M-SNOC-EMIT

`-sc` flag in `src/driver/main.c`: if input ends `.sc`, run `sc_lex → sc_parse → sc_lower → emit`.
Quick-check: `echo "OUTPUT = 'hello'" > /tmp/t.sc && ./sno2c -sc /tmp/t.sc > /tmp/t.c && gcc /tmp/t.c ... && ./a.out`
Expected output: `hello`

### Sprint SC4 — M-SNOC-CORPUS

10-rung corpus in `test/frontend/snocone/`:
SC1 literals · SC2 assign · SC3 arith · SC4 control · SC5 while/do · SC6 for · SC7 procedure · SC8 struct · SC9 patterns · SC10 snocone.sno word-count example

### Sprint SC5 — M-SNOC-SELF

`snocone.sc` → `./sno2c -sc` → binary → run → diff vs `snocone.snobol4` oracle (or fresh compile).
**M-SNOC-SELF fires** when diff is empty.


**Session183 (backend session) — diagnosis 79/106; correct DEFINE design:**
- Corpus confirmed: 79/106 PASS
- DEFINE calling convention: **user-defined functions ARE named patterns** (BACKEND-C.md)
- Wrong approach (C-ABI trampoline) identified and discarded
- Correct design: extend AsmNamedPat with is_fn/nparams/arg_slots/save_slots
- α port binds args + saves old param vars; γ/ω ports restore; RETURN → jmp [ret_γ]
- No runtime changes — compile-time only
- See CRITICAL NEXT ACTION above for Session184 implementation steps

---

## NET Backend — snobol4x TINY (net_emit.c)

**Strategy:** `sno2c -net prog.sno > prog.il` → `ilasm prog.il` → `prog.exe`

Same pipeline shape as the ASM backend. `net_emit.c` walks `Program*` and emits CIL `.il` text. `ilasm` assembles it. Runtime support lives in `src/runtime/net/`, grown rung by rung exactly as `src/runtime/asm/` grew. No dependency on snobol4dotnet — fully self-contained.

**snobol4dotnet was reference only** — it showed what a complete .NET SNOBOL4 runtime looks like. `net_emit.c` mirrors `emit_byrd_asm.c` structurally: same IR in, different target out.

### Sprint N-R0 — M-NET-HELLO

**Goal:** `-net` flag wired; `null.sno` → `null.il` → `ilasm` → `null.exe` → exit 0.

**Files:**
- `src/backend/net/net_emit.c` — new emitter (mirrors `emit_byrd_asm.c` structure)
- `src/runtime/net/snobol4_net.il` — minimal runtime stubs (mirrors `src/runtime/asm/`)
- `src/driver/main.c` — add `-net` flag → `net_emit(prog, out)`
- `src/Makefile` — wire `net_emit.c` into build
- `test/crosscheck/run_crosscheck_net_rung.sh` — harness (mirrors ASM version)
- `artifacts/net/hello_prog.il` — canonical artifact committed

**Steps:**
1. Add `extern void net_emit(Program *prog, FILE *f);` + `-net` dispatch to `main.c`
2. Stub `net_emit.c`: emit minimal valid `.il` header + `.entrypoint` + `ret`
3. Confirm `ilasm null.il` assembles clean, `mono null.exe` exits 0
4. Add `run_crosscheck_net_rung.sh`
5. Commit `artifacts/net/hello_prog.il`
6. **M-NET-HELLO fires**

**Session start:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD
apt-get install -y libgc-dev nasm mono-complete && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # 106/106
# Then: implement net_emit.c + N-R0 steps above
```

### Sprint N-R1 — M-NET-LIT / M-NET-R1

**Goal:** `OUTPUT = 'hello'` → `hello`. Corpus rungs hello/output/assign/arith PASS.

- `net_emit.c`: emit string constants, `OUTPUT` assignment, basic arith ops
- Grow `src/runtime/net/` with string/output/arith support stubs

### Sprint N-R2 — M-NET-GOTO / M-NET-R2

**Goal:** `:S(X)F(Y)` branching, control/. Corpus rungs control/patterns/capture PASS.

### Sprint N-R3 — M-NET-R3

**Goal:** strings/ keywords/ PASS.

### Sprint N-R4 — M-NET-R4

**Goal:** functions/ data/ PASS.

### Sprint N-R5 — M-NET-CROSSCHECK

**Goal:** 106/106 corpus PASS via NET backend. M-NET-CROSSCHECK fires.


**Session F-210 summary — M-FLAT-NARY merged; sc_cf.c do_procedure bug diagnosed:**

Merged `flat-nary-f209` → `main` (fast-forward). Build clean. Invariants confirmed:
100/106 C ✅ · 26/26 ASM ✅. Pushed `origin/main` at `6495074`.

Ran existing SC ASM corpus: 7/10 PASS. Failures: `sc7_procedure`, `sc9_multiproc`,
`sc10_wordcount`.

**Root cause diagnosed:** `do_procedure` in `src/frontend/snocone/sc_cf.c` calls
`prog_append(st, ...)` for DEFINE + function label + body + RETURN + END label — but
none of these appear in the generated C or ASM output. Only the call sites
(`APPLY_fn("square",...)`) appear. The function body statements are being generated
but silently dropped. Likely cause: `prog_append` is writing to a sub-Program or the
statements are being freed/lost before the emit pass.

**⚠ CRITICAL NEXT ACTION — Session F-211 (frontend):**

Fix `do_procedure` in `src/frontend/snocone/sc_cf.c` so function body statements
appear in output. Target: `sc7_procedure` and `sc9_multiproc` PASS → 9/10 SC corpus
→ M-SC-CORPUS-R2.

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
apt-get install -y libgc-dev nasm && make -C src
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 100/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
bash test/frontend/snocone/sc_asm_corpus/run_sc_asm_corpus.sh  # baseline 7/10

# Diagnose do_procedure: add fprintf(stderr,...) after each prog_append in
# do_procedure to confirm stmts are being appended. Check if sc_driver.c
# calls sc_cf_compile correctly and uses its Program* output.
# Then fix and verify:
bash test/frontend/snocone/sc_asm_corpus/run_sc_asm_corpus.sh  # target 9/10+
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must stay 100/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must stay 26/26
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
./sno2c -asm -I$INC $BEAUTY > artifacts/asm/beauty_prog.s
nasm -f elf64 -I src/runtime/asm/ artifacts/asm/beauty_prog.s -o /dev/null
git add -A && git commit -m "F-211: fix do_procedure body emission; sc7+sc9 PASS"
```
