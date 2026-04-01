# MILESTONE-FAST-EMIT-CHECK.md — M-G-EMIT-FAST: Fast Emit-Diff Gate

*Authored DYN-13 session, 2026-04-01, Claude Sonnet 4.6*

---

## Problem — root cause measured

`run_emit_check.sh` took **224s** on a 2-core machine for 1286 checks.

Profiled breakdown per `check_one()` invocation:

| Source | Cost | Count | Total |
|--------|------|-------|-------|
| `bash -c` subprocess spawn (xargs) | ~17ms | 1286 | ~22s |
| `mktemp` + `rm` (temp file I/O) | ~18ms | 1286 | ~23s |
| `scrip-cc` compile | ~2ms | 1286 | ~3s |
| `diff` subprocess | ~3ms | 1286 | ~4s |
| **Parallelism headroom (2 cores)** | ÷2 | — | — |
| **Observed wall time** | — | — | **224s** |

**Root causes:**
1. `xargs -P N -I{} bash -c 'check_one ...'` spawns one **bash subprocess per file** — even with `-P N`, each subprocess starts fresh, re-parses the exported function, and pays full bash startup cost (~17ms).
2. `mktemp` creates a real temp file on disk per invocation; `diff` and `rm` each add a syscall round-trip. On a slow container FS this inflates to ~18ms/call.
3. scrip-cc is **called once per file per backend** — 3 separate processes for the same source. The binary already supports multiple input files internally (loops over `files[]`), but the script never uses this.
4. No output reuse: `-o /dev/stdout` pipes per-call then re-reads; the `.s`/`.j`/`.il` oracle files are stat'd + opened per comparison.

**Result:** ~35ms overhead per invocation × 1286 = ~45s overhead alone, magnified by 2-core serialization.

---

## Goal

`run_emit_check.sh` gate time: **< 15s** on a 2-core machine (15× speedup).

---

## Solution: three-level optimization

### Level 1 — Batch scrip-cc per backend (implemented)

Instead of 1286 separate scrip-cc invocations, run **3 invocations total** — one per backend (`-asm`, `-jvm`, `-net`) — each receiving all source files at once. scrip-cc's existing multi-file loop handles this; output goes to `$WORK/out/{asm,jvm,net}/` via derived filenames.

```bash
# Before: 1286 invocations
xargs -P2 -I{} bash -c 'check_one "$1" -asm s' _ {}

# After: 3 invocations total
scrip-cc -asm "${SNO_FILES[@]}"   # all files, derived output names
scrip-cc -jvm "${SNO_FILES[@]}"
scrip-cc -net "${SNO_FILES[@]}"
```

scrip-cc derives output as `$(basename src .sno).{s,j,il}` next to source. We redirect via a WORK dir by symlinking or using `-o` per-file in a prebuilt manifest. See implementation note below.

### Level 2 — Eliminate mktemp: compare directly in memory

scrip-cc multi-file mode writes output next to source (`.s`, `.j`, `.il`). For diff-gate purposes, use `--update` to write into `$WORK/generated/` then diff the whole directory tree with `diff -rq`. No per-file temp files needed.

### Level 3 — Single bash process for result scanning

Replace `xargs ... bash -c 'check_one'` with a single bash loop in the main process. With batch compilation already done, the inner loop is pure diff — no subprocesses needed.

```bash
# After batch compile, all in one bash process:
for src in "${SNO_FILES[@]}"; do
  base="${src%.sno}"
  for be_ext in "asm s" "jvm j" "net il"; do
    backend="${be_ext% *}"; ext="${be_ext#* }"
    got="$WORK/generated/$(basename $base).$ext"
    expected="$(dirname $src)/$(basename $base).$ext"
    diff -q "$got" "$expected" >/dev/null 2>&1 && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
  done
done
```

Zero subprocess spawns in the diff loop. Zero mktemp calls.

---

## Implementation note: WORK dir output from scrip-cc

scrip-cc's multi-file mode derives output filenames next to source, which we cannot redirect. Two options:

**Option A (simpler):** Copy all corpus source files into `$WORK/src/` first, run scrip-cc there, diff against originals. One `cp -r` per run (~2s) but no source pollution.

**Option B (preferred):** Add `--outdir DIR` flag to scrip-cc `main.c` (trivial: ~10 lines). All derived outputs go to `DIR/` with original basename. No source copying needed.

Option B is the permanent fix. Option A is the interim fallback until scrip-cc gets `--outdir`.

---

## Files

| File | Change |
|------|--------|
| `test/run_emit_check.sh` | Rewrite inner loop — batch compile + in-process diff |
| `src/driver/main.c` | Add `--outdir DIR` option (Option B) |
| `.github/MILESTONE-FAST-EMIT-CHECK.md` | This doc |

---

## Gate

```bash
# Before:  Emit-diff 1286/0 — 224s
# After:   Emit-diff 1286/0 — <15s
CORPUS=/home/claude/corpus bash test/run_emit_check.sh
# Must still show: 1286 pass / 0 fail
```

The pass/fail count must not change. This is a pure performance milestone.

---

## Sprint

`DYN-13` — authors: Lon Jones Cherryholmes · Claude Sonnet 4.6
