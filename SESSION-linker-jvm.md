
---

## LP-JVM-3 Handoff update (2026-03-27, Claude Sonnet 4.6) — commit c3e3ab3

### Demos 1-3: ✅ PASS (3/3 JVM frontends)

`run_demo.sh` was using the retired `icon_driver` binary for ICON-JVM. Fixed to use
`sno2c -icn -jvm` (Icon was merged into sno2c in LP-JVM-2). All three demos now:

```
demo1 (hello):     SNO2C-JVM ✅  ICON-JVM ✅  PROLOG-JVM ✅
demo2 (wordcount): SNO2C-JVM ✅  ICON-JVM ✅  PROLOG-JVM ✅
demo3 (roman):     SNO2C-JVM ✅  ICON-JVM ✅  PROLOG-JVM ✅
```

Reference interpreters (snobol4, swipl, icont) SKIP — not installed in this env.

### Export wrapper bug — RESOLVED (was misdiagnosed in prior handoff)

Prior handoff said "export wrapper loop not firing / jvm_fn_count==0". **Not true.**
Debug confirmed `jvm_fn_count=3` for `family_snobol4.sno` — the loop runs fine.
Real issue: **`prog->exports == NULL`** because `family_snobol4.sno` has no `EXPORT`
directives at all. The EXPORT wrapper code in `emit_byrd_jvm.c` is correct.

### Remaining work for M-SCRIP-DEMO

Two blockers:

**1. `family_snobol4.sno` needs EXPORT directives.**
The SNOBOL4 EXPORT syntax is label-style (column 1):
```
EXPORT  PARSE_CSV
```
Functions to export: whatever Icon calls cross-language. Currently `family_icon.icn`
calls only stubs (all return "" or "0") — no actual cross-language calls yet wired.
Decision needed: does M-SCRIP-DEMO require real cross-language calls, or just the
family demo running end-to-end with each language self-contained?

**2. `ByrdBoxLinkage.j` is missing from `src/runtime/jvm/` (directory is empty/.gitkeep).**
Restore from LP-JVM-1 commit:
```bash
cd snobol4x
git show 92006e7:src/runtime/jvm/ByrdBoxLinkage.j > src/runtime/jvm/ByrdBoxLinkage.j
```
Or check if `demo/scrip/ScripFamily.j` contains the linkage class inline.

**Read only:** `ARCH-scrip-abi.md` + `SESSION-linker-jvm.md`. No other docs.



**Commit:** `d3ac6f0` snobol4x

### All fixes applied and confirmed in source:

1. **`src/frontend/snobol4/lex.c`** — `handle_export`/`handle_import` verbatim case (no toupper)
2. **`src/frontend/icon/icon_lex.c`** — `skip_ws` skips `$import`/`$export`/`-IMPORT`/`-EXPORT`; `#include <strings.h>`
3. **`src/frontend/icon/icon_emit_jvm.c`** — lowercase classnames; `'P'` type for Object[] fields; `ij_find_import` case-sensitive; import dispatch correct relay labels/stack; `JBarrier()` restored; `ij_expr_is_string` returns 1 for imports
4. **`src/frontend/prolog/prolog_emit_jvm.c`** — lowercase classnames; export wrapper block (null-check args, pj_term_var fallback); `pj_db_call` for findall on dynamic facts; `pj_rc_swallow` → `pj_db_call`; `assertz/1` case in `pj_call_goal`
5. **`src/backend/jvm/emit_byrd_jvm.c`** — lowercase classnames; `jvm_is_exported` (strcasecmp); `jvm_find_import`; EXPORT wrapper loop emitting `public static export_name(...)V`
6. **`demo/scrip/family_net/family_prolog.pro`** — restored from LP-JVM-1 commit

### ONE REMAINING BUG — EXPORT WRAPPER LOOP NOT FIRING

**Symptom:** `family_snobol4.j` has `sno_userfn_parse_csv()` but NO `.method public static parse_csv(...)V` wrapper. `parse_csv` is not a public export. The Icon import call to `family_snobol4/parse_csv(...)` throws NoSuchMethodError.

**What to try first:**
```c
/* Add at top of the export wrapper loop in emit_byrd_jvm.c, around line 4786: */
fprintf(stderr, "DEBUG export loop: jvm_fn_count=%d prog->exports=%p\n",
        jvm_fn_count, (void*)(prog ? prog->exports : NULL));
for (int i = 0; i < jvm_fn_count; i++)
    fprintf(stderr, "  fn[%d].name=%s\n", i, jvm_fn_table[i].name ? jvm_fn_table[i].name : "(null)");
if (prog) for (ExportEntry *e = prog->exports; e; e = e->next)
    fprintf(stderr, "  export: %s\n", e->name);
```

**Most likely cause:** `jvm_fn_count == 0` at the wrapper emission point. The `jvm_collect_functions` call at line ~4717 resets count to 0, then scans for `E_FNC/DEFINE`. If `family_snobol4.sno` uses the DEFINE pattern that the scanner misses (e.g. DEFINE body starts with label, not a DEFINE statement), count stays 0.

**Alternative fix if jvm_fn_count==0:** Use `prog->head` to scan for `E_FNC` nodes matching export names directly, instead of relying on `jvm_fn_table`:
```c
for (ExportEntry *e = prog->exports; e; e = e->next) {
    /* find nargs by scanning DEFINE stmts */
    int nargs = 0;
    for (STMT_t *s = prog->head; s; s = s->next) {
        if (!s->subject || s->subject->kind != E_FNC) continue;
        if (!s->subject->sval || strcasecmp(s->subject->sval, "DEFINE") != 0) continue;
        /* parse proto to get name and nargs */
        ...
    }
    /* emit wrapper with found nargs */
}
```

**After fixing the export wrapper — run in order:**
```bash
cd snobol4x && make -C src
cd demo/scrip/family_net
SNO2C=../../sno2c; JASMIN=../../src/backend/jvm/jasmin.jar; BYRD=../../src/runtime/jvm/ByrdBoxLinkage.j (CHECK IF EXISTS — may need to hand-author)

$SNO2C -pl -jvm family_prolog.pro > out/family_prolog.j
$SNO2C -jvm family_snobol4.sno > out/family_snobol4.j  
$SNO2C -jvm family_icon.icn > out/family_icon.j

java -jar $JASMIN out/ByrdBoxLinkage.j out/family_prolog.j out/family_snobol4.j out/family_icon.j -d out
java -cp out family_icon < family.csv 2>&1
diff <(java -cp out family_icon < family.csv 2>/dev/null) family.expected
```

**NOTE on ByrdBoxLinkage.j:** `src/runtime/jvm/ByrdBoxLinkage.j` may be missing (lost in cherry-pick). Check `test/linker/jvm/out/ByrdBoxLinkage.class` — if .class exists, use it directly. Otherwise restore from LP-JVM-1 commit:
```bash
git show 92006e7:src/runtime/jvm/ByrdBoxLinkage.j > src/runtime/jvm/ByrdBoxLinkage.j
```

**After M-SCRIP-DEMO passes:**
- Run regression: `bash test/crosscheck/run_crosscheck_jvm_rung.sh /home/claude/snobol4corpus/crosscheck/*/` → expect 127 pass
- Commit: `LP-JVM-3: M-SCRIP-DEMO ✅`
- Update this SESSION doc + PLAN.md

**Read only:** `ARCH-scrip-abi.md` + `SESSION-linker-jvm.md`. No other docs.
