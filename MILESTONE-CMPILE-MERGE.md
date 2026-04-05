# MILESTONE-CMPILE-MERGE.md — CMPILE.c → scrip-interp swap

**Track:** C (scrip-interp / SIL)
**Sprint introduced:** 104
**Status:** 🔴 ACTIVE — RT-113 pivot 2026-04-05
**Priority:** TOP — supersedes RUNTIME-6 DT_E blocker

---

## What this milestone is

`CMPILE.c` is the authoritative SIL-faithful SNOBOL4 lex/parser, validated on 500+
corpus files.  The current scrip-interp execution path still uses the old Bison/Flex
parser (`sno_parse`).  This milestone swaps CMPILE in as the live execution parser.

**Two phases:**

1. **Phase 0 — IR tree comparison** (pre-swap safety check): run both parsers on all
   553 corpus `.sno` files, compare their IR S-expression output, classify every
   divergence before touching the execution path.
2. **Phase 1 — Swap + gate**: wire CMPILE as the default parser; gate PASS ≥ 190.

---

## Background: two parsers, same output type

| Parser | Entry point | Output |
|--------|-------------|--------|
| Bison/Flex (current) | `sno_parse(f, path)` → `Program*` | `STMT_t`/`EXPR_t` IR via `snobol4.tab.c` |
| CMPILE (target) | `cmpile_file(f,path)` + `cmpile_lower(cl)` → `Program*` | same `STMT_t`/`EXPR_t` IR via `cmpnd_to_expr()` |

Both produce identical types.  Comparison is IR sexp vs IR sexp using the existing
`ir_print_node()` from `src/ir/ir_print.c` (`ir_print_node_nl(stmt->subject, f)`, etc.).

`--dump-parse` already uses CMPILE and emits CMPILE-sexp (not IR sexp).
We need `--dump-ir` on BOTH paths to get comparable output.

---

## The stype → EKind mapping (complete)

Used by `cmpnd_to_expr()` (already partially implemented) and `cmpile_to_expr()`
(new name for the corrected version):

| CMPILE stype | Value | EKind | Notes |
|---|---|---|---|
| `QLITYP` | 1 | `E_QLIT` | quoted literal |
| `ILITYP` | 2 | `E_ILIT` | integer literal |
| `VARTYP` | 3 | `E_VAR` | variable ref (leaf) |
| `FNCTYP` | 5 | `E_FNC` | function call (nchildren=args) |
| `FLITYP` | 6 | `E_FLIT` | float literal |
| `ARYTYP` | 7 | `E_IDX` | array/table subscript |
| `SELTYP` | 50 | `E_ALT` | alternative eval `(e1,e2,en)` |
| `ADDFN` | 201 | `E_ADD` | binary `+` |
| `SUBFN` | 202 | `E_SUB` | binary `-` |
| `MPYFN` | 203 | `E_MUL` | binary `*` |
| `DIVFN` | 204 | `E_DIV` | binary `/` |
| `EXPFN` | 205 | `E_POW` | binary `**` |
| `ORFN` | 206 | `E_ALT` | pattern alternation `\|` |
| `NAMFN` | 207 | `E_CAPT_COND_ASGN` | conditional capture `.var` |
| `DOLFN` | 208 | `E_CAPT_IMMED_ASGN` | immediate capture `$var` |
| `BIATFN` | 209 | `E_OPSYN` | `@` user-definable binary |
| `BIPDFN` | 210 | `E_OPSYN` | `#` user-definable binary |
| `BIPRFN` | 211 | `E_OPSYN` | `%` user-definable binary |
| `BIAMFN` | 212 | `E_OPSYN` | `&` user-definable binary |
| `BINGFN` | 213 | `E_OPSYN` | `~` user-definable binary |
| `BIQSFN` | 214 | `E_SCAN` | `?` scan/interrogate binary |
| `PLSFN` | 301 | `E_PLS` | unary `+` |
| `MNSFN` | 302 | `E_MNS` | unary `-` |
| `DOTFN` | 303 | `E_NAME` | unary `.X` name-of |
| `INDFN` | 304 | `E_INDIRECT` | unary `$X` indirect ref |
| `STRFN` | 305 | `E_DEFER` | unary `*X` deferred expr |
| `ATFN` | 308 | `E_CAPT_CURSOR` | unary `@X` cursor capture |
| `NEGFN` | 311 | `E_INTERROGATE` | unary `?X` interrogation |
| `NSTTYP` | 4 | *(transparent)* | parenthesized — unwrap single child |
| concatenation | *(implicit)* | `E_CAT` | `VARTYP` node with `nchildren > 1` |

**VARTYP disambiguation:**
- `nchildren == 0` → `E_VAR` leaf (simple variable reference)
- `nchildren > 1`  → `E_CAT` (implicit concatenation of terms)
- `nchildren == 1` → treat as `E_CAT` with one term (degenerate, map to child directly)

**NSTTYP:** always transparent — `return cmpile_to_expr(n->children[0])`.

---

## Phase 0 — IR tree comparison sweep (pre-swap)

### Goal

Confirm that `cmpile_lower()` and `sno_parse()` produce identical IR trees for all
553 corpus `.sno` files.  Classify every divergence.  Fix any `cmpnd_to_expr()` bugs
before the swap.  Do not change the execution path until Phase 0 is clean.

### Step 0a — Add `--dump-ir` to scrip-interp (both paths)

In `scrip-interp.c` `main()`, add flag `--dump-ir`.  When set:

1. Run **CMPILE path**: `cmpile_file()` → `cmpile_lower()` → walk `Program*`, call
   `ir_print_stmt(st, stdout)` for each `STMT_t`.
2. Run **Bison path**: `sno_parse()` → walk `Program*`, call `ir_print_stmt(st, stdout)`.
3. Emit both to separate fds / files; the sweep script diffs them.

Add helper `ir_print_stmt(STMT_t *st, FILE *f)` inline in scrip-interp.c:

```c
/* Print one STMT_t as IR sexp — label, subject, pattern, replacement, gotos */
static void ir_print_stmt(STMT_t *st, FILE *f) {
    fprintf(f, "(STMT");
    if (st->label)   fprintf(f, " :lbl %s", st->label);
    if (st->subject) { fprintf(f, " :subj "); ir_print_node(st->subject, f); }
    if (st->pattern) { fprintf(f, " :pat ");  ir_print_node(st->pattern,  f); }
    if (st->replacement) { fprintf(f, " :repl "); ir_print_node(st->replacement, f); }
    if (st->go) {
        SnoGoto *g = st->go;
        if (g->uncond)    fprintf(f, " :go %s",  g->uncond);
        if (g->onsuccess) fprintf(f, " :goS %s", g->onsuccess);
        if (g->onfailure) fprintf(f, " :goF %s", g->onfailure);
    }
    fprintf(f, ")\n");
}
```

`ir_print_node()` is already in `src/ir/ir_print.c` — add `ir_print.o` to `Makefile`
if not already linked (check: `grep ir_print one4all/Makefile`).

Invocation:
```
./scrip-interp --dump-ir-cmpile  file.sno  > /tmp/cmpile.ir
./scrip-interp --dump-ir-bison   file.sno  > /tmp/bison.ir
diff /tmp/bison.ir /tmp/cmpile.ir
```

Use two separate flags (`--dump-ir-cmpile`, `--dump-ir-bison`) so both paths are
driven from the same binary with no environment switching.

### Step 0b — Write the comparison sweep script

`one4all/test/cmpile_vs_bison.sh`:

```bash
#!/usr/bin/env bash
# cmpile_vs_bison.sh — compare CMPILE IR vs Bison IR across all corpus .sno files
# Usage: CORPUS=/home/claude/corpus bash one4all/test/cmpile_vs_bison.sh
# Output: summary + /tmp/cmpile_vs_bison/ per-file diffs for divergences

set -euo pipefail
INTERP="${INTERP:-/home/claude/one4all/scrip-interp}"
CORPUS="${CORPUS:-/home/claude/corpus}"
OUT=/tmp/cmpile_vs_bison
mkdir -p "$OUT"

TOTAL=0; MATCH=0; DIFF=0; CRASH_C=0; CRASH_B=0

for sno in $(find "$CORPUS" -name "*.sno" | sort); do
    base=$(basename "$sno" .sno)
    TOTAL=$((TOTAL+1))

    # CMPILE path
    if "$INTERP" --dump-ir-cmpile "$sno" > "$OUT/${base}.cmpile" 2>/dev/null; then :
    else CRASH_C=$((CRASH_C+1)); echo "CRASH-C $sno"; continue; fi

    # Bison path
    if "$INTERP" --dump-ir-bison  "$sno" > "$OUT/${base}.bison"  2>/dev/null; then :
    else CRASH_B=$((CRASH_B+1)); echo "CRASH-B $sno"; continue; fi

    if diff -q "$OUT/${base}.bison" "$OUT/${base}.cmpile" > /dev/null 2>&1; then
        MATCH=$((MATCH+1))
    else
        DIFF=$((DIFF+1))
        diff "$OUT/${base}.bison" "$OUT/${base}.cmpile" > "$OUT/${base}.diff" 2>&1 || true
        echo "DIFF $sno"
    fi
done

echo ""
echo "=== cmpile_vs_bison sweep ==="
echo "  Total:       $TOTAL"
echo "  Match:       $MATCH"
echo "  Differ:      $DIFF"
echo "  Crash-C:     $CRASH_C"
echo "  Crash-B:     $CRASH_B"
echo "  Diffs in:    $OUT/*.diff"
```

Check this script in at `one4all/test/cmpile_vs_bison.sh`.

### Step 0c — Triage divergences

For each `.diff` file:

- **Structural mismatch** (wrong EKind) → bug in `cmpnd_to_expr()` stype mapping → fix
- **Value mismatch** (right shape, wrong literal/name) → strdup or text pointer issue → fix
- **Missing node** (CMPILE produces NULL where Bison has a node) → cmpnd_to_expr early return → fix
- **Extra node** (CMPILE wraps where Bison does not) → NSTTYP not unwrapped → fix
- **Known-acceptable** (Bison has bison-specific artefacts CMPILE doesn't emit) → document in §Known Acceptable Divergences below

**Gate for Phase 0:** DIFF == 0 AND CRASH_C == 0 (Bison crashes on its own files are pre-existing, not our problem).

---

## Phase 1 — Swap CMPILE in as execution parser

Only begin Phase 1 after Phase 0 gate is satisfied.

### Step 1a — Wire CMPILE as default in `scrip-interp.c`

In `main()`, replace:
```c
Program *prog = sno_parse(f, input_path);
```
with:
```c
cmpile_init();
/* ... include-dir setup already present above ... */
CMPILE_t *cl = cmpile_file(f, input_path);
fclose(f);
Program *prog = cmpile_lower(cl);
cmpile_free(cl);
```

The include-dir setup block already exists (used by `--dump-parse`).  Move it before
the parse dispatch rather than duplicating.  `sno_parse` call site is removed.

### Step 1b — Build and test

```bash
cd /home/claude/one4all && make scrip-interp 2>&1 | grep "error:" | head -20
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
```

**Gate:** PASS ≥ 190 (no regression from bison baseline).
**Bonus:** PASS ≥ 191 (`expr_eval` passes — ADDFN=201 now routes to E_ADD correctly).

### Step 1c — Commit

```
"RT-1NN: M-CMPILE-MERGE complete — CMPILE.c is execution parser; PASS=NNN"
```

---

## Files to touch

| File | Change |
|---|---|
| `src/driver/scrip-interp.c` | Add `--dump-ir-cmpile` / `--dump-ir-bison` flags; add `ir_print_stmt()`; Phase 1: swap `sno_parse` → `cmpile_lower` |
| `src/runtime/snobol4/snobol4_pattern.c` | Audit/fix `cmpnd_to_expr()` per Phase 0 triage |
| `one4all/test/cmpile_vs_bison.sh` | New — comparison sweep script |
| `one4all/Makefile` | Add `ir_print.o` if missing |

**Do NOT touch:** `ir.h`, `ir_print.c`, `sil_macros.h`, `eval_node()`, `snobol4.tab.c` (Bison stays as oracle for Phase 0).

---

## §Known Acceptable Divergences

*(Populated during Phase 0 triage — append here as found)*

| Pattern | Reason | Acceptable? |
|---|---|---|
| *(none yet)* | | |

---

## Gate summary

| Phase | Condition | Result |
|---|---|---|
| Phase 0 | DIFF == 0, CRASH_C == 0 (all 553 files) | ✅ safe to swap |
| Phase 0 | DIFF > 0 | ❌ fix `cmpnd_to_expr()` bugs first |
| Phase 1 | PASS ≥ 190 | ✅ milestone done |
| Phase 1 | PASS ≥ 191 (`expr_eval` passes) | ✅ bonus — EVAL fixed too |
| Phase 1 | PASS < 190 | ❌ regression — revert, debug with IR diffs |

---

## Why EVAL() is also fixed by Phase 1

The old `node_to_expr()` (used by the EVAL() builtin path) guessed stype integers
without named constants, causing arithmetic nodes (`ADDFN=201`, etc.) to fall through
to a string-concat default.  `cmpnd_to_expr()` uses the named constants directly, so
`EVAL('1 + 2')` produces `E_ADD(E_ILIT(1), E_ILIT(2))` → `eval_node()` returns 3.

---

*Introduced sprint 104 · Track C · Lon Jones Cherryholmes + Claude Sonnet 4.6*
*Phase 0 (IR comparison pre-check) added RT-113 · 2026-04-05*
