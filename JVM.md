# JVM.md — snobol4jvm (L2)

JVM/Clojure backend: SNOBOL4 → JVM bytecode via multi-stage pipeline.

→ Backend reference: [BACKEND-JVM.md](BACKEND-JVM.md)
→ Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `jvm-backend` J-212 — M-JVM-BEAUTY continued: fix cross-scope goto (out-of-fn label → freturn)
**HEAD:** `d4012e0` J-211
**Milestone:** M-JVM-SAMPLES ✅ J-210 · M-JVM-BEAUTY ❌ (1 Jasmin error remaining)

**J-211 — M-JVM-BEAUTY WIP — 3 fixes, 1 error remaining:**
- Fix 1: `jvm_expand_label()` — sanitize `$:\'<>=()` in SNOBOL4 labels for Jasmin. 26 errors → 1.
- Fix 2: DEFINE `end_label` fallback — when DEFINE has no goto, use next stmt's goto. Fixes `findRefs` scope in beauty.sno.
- Fix 3: Computed goto dispatch (`$COMPUTED:expr`) — if-chain over in-scope labels via `sno_str_eq`. `jvm_cur_prog` wired.
- **Remaining:** `L_error` — main-level label referenced via `:F(error)` from inside `pp` function body. Cross-scope goto to main label from function method → route to `Jfn%d_freturn`.
- Invariants: 102/106 C · 89/92 JVM (unchanged)

**⚠ CRITICAL NEXT ACTION — Session J-212 (JVM):**

Sprint J10 continued — fix cross-scope goto → M-JVM-BEAUTY

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git pull && apt-get install -y libgc-dev nasm default-jdk && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 CORPUS=$CORPUS bash test/crosscheck/run_crosscheck.sh 2>&1 | tail -2   # 102/106
bash test/crosscheck/run_crosscheck_jvm_rung.sh \
  $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/arith \
  $CORPUS/control $CORPUS/patterns $CORPUS/capture \
  $CORPUS/strings $CORPUS/keywords $CORPUS/functions $CORPUS/data 2>&1 | tail -2
# Expected: 89/92

# Reproduce the beauty.j error:
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
TMPD=/tmp/beauty_jvm && mkdir -p $TMPD
./sno2c -jvm -I$INC $BEAUTY > $TMPD/beauty.j
java -jar src/backend/jvm/jasmin.jar $TMPD/beauty.j -d $TMPD/ 2>&1 | grep -iv "generated\|picked"
# Expected: "L_error has not been added to the code" (1 error)

# Fix: in jvm_emit_goto, after expanding label, check if it is a main-level label
# being jumped to from inside a function. If so, route to Jfn%d_freturn instead.
# Location: end of jvm_emit_goto(), just before the final JI("goto", glbl) call.
# Logic:
#   if (jvm_cur_fn) {
#       /* check if 'safe' label exists in current fn scope */
#       int found_in_fn = 0;
#       const char *entry = jvm_cur_fn->entry_label ? jvm_cur_fn->entry_label : jvm_cur_fn->name;
#       int in_body = 0;
#       for (STMT_t *t = jvm_cur_prog->head; t; t = t->next) {
#           if (t->label && strcasecmp(t->label, entry)==0) in_body=1;
#           if (in_body && jvm_cur_fn->end_label && t->label &&
#               strcasecmp(t->label, jvm_cur_fn->end_label)==0) break;
#           if (in_body && t->label) {
#               char ts[128]; jvm_expand_label(t->label, ts, sizeof ts);
#               if (strcmp(ts, safe)==0) { found_in_fn=1; break; }
#           }
#       }
#       if (!found_in_fn) {
#           /* out-of-scope: SNOBOL4 semantics = FRETURN */
#           int fn_idx = (int)(jvm_cur_fn - jvm_fn_table_fwd);
#           char lbl[64]; snprintf(lbl, sizeof lbl, "Jfn%d_freturn", fn_idx);
#           J("    goto %s\n", lbl); return;
#       }
#   }
#   JI("goto", glbl);   <- existing line
```

After any `emit_byrd_jvm.c` change, run the mandatory artifact check:
```bash
bash test/crosscheck/jvm_artifact_check.sh
# exits nonzero if artifacts changed → add staged files to your commit
```

**J-204 — functions/ 8/8 PASS, data/ 3/6 PASS:**
- Three fixes: fn-body skip in main walk, jvm_arith_local_base, Case 2 :S/:F routing
- functions/ 083–090: all 8 PASS (DEFINE/RETURN/FRETURN/recursion/entry-label/pattern)
- data/ 091–093: PASS (ARRAY/TABLE). 094–096: FAIL — DATA constructor/field bug
- Pre-existing xfails: expr_eval, 053_pat_alt_commit (unchanged)
- Artifact: artifacts/jvm/hello_prog.j updated

**⚠ CRITICAL NEXT ACTION — Session J-205 (JVM):**

Sprint J-R4 continued — fix DATA tests 094/095/096 → M-JVM-R4

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git pull && apt-get install -y libgc-dev nasm default-jdk && make -C src
git log --oneline -3   # verify HEAD = c2e7a0e
CORPUS=/home/claude/snobol4corpus/crosscheck
bash test/crosscheck/run_crosscheck_jvm_rung.sh $CORPUS/functions $CORPUS/data 2>&1
# Expected: 11/14 — fix 3 remaining DATA failures
```

### Known gaps for J-R4 (remaining — DATA 094/095/096)
1. `sno_data_get_field` VerifyError — stack height inconsistency. Fix helper emitter
   in `jvm_emit_runtime_helpers()` around sno_data_get_field (~line 2780 emit_byrd_jvm.c).
2. DATA constructor calls (`complex(3,-2)`) must be recognised as constructors not user fns.
   In E_FNC: after checking user fns, check `jvm_find_data_type(fname)` — if found, create
   HashMap via `sno_array_new`, store each field value keyed by field name plus `__type__`.
3. Field accessor calls (`real(X)`) — `jvm_find_data_field(fname)` finds the type; emit
   `sno_data_get_field(instance_id, field_name)`.
4. Field setter `x(P) = 99` — subject E_FNC(field,[instance]); map to
   `sno_array_put(instance_id, field_name, value)`.
5. `DATATYPE(N)` for DATA instances — check `__type__` key; return type name not "STRING".
- **pattern-valued variables** (xfailed word*/cross/wordcount): deferred to J-R5+


## Session Start

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = f24fb97
git remote set-url origin https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
apt-get install -y libgc-dev nasm && make -C src
# J3 smoke baseline:
TMPD=$(mktemp -d); JASMIN=src/backend/jvm/jasmin.jar
for t in size_test dupl_test remdr_test goto_s goto_f; do
  ./sno2c -jvm test/jvm_j3/${t}.sno > $TMPD/p.j
  java -jar $JASMIN $TMPD/p.j -d $TMPD/ 2>/dev/null
  cls=$(ls $TMPD/*.class | head -1 | xargs basename | sed 's/.class//')
  echo "$t: $(java -cp $TMPD $cls 2>/dev/null)"; rm -f $TMPD/*.class
done; rm -rf $TMPD
# Then implement J4: LIT/SEQ/ALT/ARBNO Byrd box pattern emitter
```
# Then Sprint J2: assign/ + arith/ rungs
```

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-JVM-EVAL** | Inline EVAL! — arithmetic no longer calls interpreter | ❌ |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

---

## Sprint Map

### Active → M-JVM-EVAL

| Sprint | What | Status |
|--------|------|--------|
| `jvm-edn-cache` | EDN cache — 22× per-program | ✅ `b30f383` |
| `jvm-transpiler` | SNOBOL4 IR → Clojure loop/case — 3.5–6× | ✅ `4ed6b7e` |
| `jvm-stack-vm` | Flat bytecode stack VM — 2–6× | ✅ `d9e4203` |
| `jvm-bytecode` | ASM .class gen — 7.6× | ✅ `c185893` |
| **`jvm-inline-eval`** | Emit arith/assign/cmp into JVM bytecode | ← active |
| `jvm-pattern-engine` | Compile patterns to Java methods | ❌ |

### → M-JVM-SNOCONE

| Sprint | Status |
|--------|--------|
| `jvm-snocone-corpus` | ✅ `ab5f629` |
| `jvm-snocone-lexer` | ✅ `d1dec27` |
| `jvm-snocone-expr` | ✅ `9cf0af3` |
| `jvm-snocone-control` | ❌ |
| `jvm-snocone-selftest` | ❌ |

---

## Pivot Log

| Date | What | Why |
|------|------|-----|
| 2026-03-12 | `jvm-inline-eval` declared active | Sprint 23D complete, 23E next |
| 2026-03-16 | Pivot from HARNESS `monitor-scaffold` to JVM `jvm-inline-eval` | Polish current M-JVM-EVAL milestone; harness M1 parked |
