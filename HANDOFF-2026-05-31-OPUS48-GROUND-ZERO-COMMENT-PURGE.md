# HANDOFF 2026-05-31 — Opus 4.8 — GROUND ZERO: gen_ rascal strip + comment/blank-line purge

## 🔀 PIVOT — READ FIRST (end of 2026-05-31 session)

Lon called a **PIVOT**: he wants to **start over / do it "completely different."** Direction is TBD — **ask him before resuming the old plan below.** Two drivers:
- **Dates flattened (his main complaint).** The repo-wide comment strip rewrote all 187 source files in one commit, so every file's GitHub "last modified" now reads 2026-05-31 and `git blame` points nearly every line at the Ground Zero commit. The old `DATE:` header comments were stripped out. Not recoverable without a history rewrite.
- **Git history is low forward-value.** No force-push/rewrite occurred (timeline is linear: `df3551a7 → c5cf417c → a0bb9be4`), and the repo is whole — but as a blame/forensic record it's spent, and the recovery net is mostly cashed (deleted files restored, references pulled). The **content** is what matters and it is fully portable.

**Size facts (for the restart decision):** total repo **97 MB** (`.git` 42 MB; `refs/` vendored Icon/Jcon **19 MB**; `archive/` 3.8 MB). **Actual SCRIP source `src/` = 5.9 MB; source files only (.c/.h/.cpp/.y/.l) ≈ 3.6 MB, ~78.8K lines, 271 files** — and the `.c` total is heavily inflated by the 12 generated flex/bison files. The code that matters is small.

**Recommended clean start (NOT executed — do it in a FRESH `/root` full clone, never the flaky FUSE working tree):** one fresh "Ground Zero" root commit holding the seed + reference material + docs (orphan branch promoted to `main`), keeping the old history reachable as tag `pre-ground-zero`. Same repo, clean dates, nothing of value lost; a brand-new repo only adds a psychological reset on top. **Do NOT run this force-push/rewrite at the tail of a near-full, error-prone session — start it fresh.**

---

**State (as of this session): build GREEN, seed intact — `scrip --interp` prints `hello`. No smoke/gates run (per Lon's directive).**

## What landed (one4all)
History: `df3551a7` → `c5cf417c` (Ground Zero work + an accidental mass-deletion, see incident) → **`a0bb9be4`** (restoration; current `origin/main`, 6982 files).

1. **icn-derived `gen_` rascal strip** — corrects the earlier botched `icn_→gen_` rename. The `icn` token was meant to be *deleted*, not replaced with `gen`. Deleted that token wherever it was icn-derived:
   - prefix `gen_X → X`
   - infix families `g_gen_* → g_*`, `lower_gen_* → lower_*`, `rt_gen_* → rt_*`, and `bb_gen_rnd_seed → bb_rnd_seed`. Example asked by Lon: `g_gen_frame_active → g_frame_active` (the Icon one-register-frame flag; was `g_icn_frame_active`).
   - **Preserved (genuine generator, NOT icn-derived):** the 7 pre-existing `gen_*` (`gen_a/b/assign/ast/chain_entry/depth/resume`), `bb_gen_scan/alt(_str)`, the `BB_GEN_*` enum kinds, `binop_gen_state_t`, etc.

2. **Comment & blank-line purge** — every `.c/.h/.y/.l` under `one4all/src`: all `/* */` and `//` comments stripped, **all blank lines deleted**, **200-char `/*----…----*/`** separators inserted between functions / top-level partitions. 187 files, 72,442 → 60,455 lines. Stripper is string/char-literal aware.
   - **EXCLUDED (do not strip):** the 12 checked-in flex/bison generated files (`*.lex.c`, `*.tab.c`, `*.tab.h`, `lex.*.c` under `src/frontend/*/`) — the Makefile compiles them directly and stripping breaks flex's macro scaffolding. Restored from HEAD.
   - **`.cpp` NOT included** — Lon's spec was C/H/Y/L. `src/emitter/**/*.cpp` still carry comments; extend with the same stripper if wanted.

3. **.github bookkeeping** — deleted bogus `GOAL-LANG-INDEPENDENT-RENAME.md`; prepended the #1 purge task to `GOAL-ICON-BB.md`; fixed two dangling refs in `PLAN.md` (step 1 + goals-table row).

## 🔴 Incident & recovery (read before touching git)
The original `one4all` working copy lived on the rclone FUSE mount and was a **partial checkout** (only `src/scripts/Makefile` materialized). A FUSE **I/O error** during `git add` produced **`c5cf417c`, which committed 6381 non-src files as DELETED** (`.gitignore`, `LICENSE`, `README`, `archive/`, `refs/icon-master`, `refs/jcon-master`, all HANDOFF/SESSION docs, `tools/`) — and it was pushed. Recovered by: full clone to local disk `/root/fix`, `git checkout df3551a7 -- <6381 paths>`, overlay the complete stripped `src/`, commit `a0bb9be4`, push. `origin/main` verified back to 6982 files.

## ⚠️ Environment rules for next session
- **rclone FUSE mount** (`/mnt/user-data/outputs`) **does not honor the exec bit** — copy `scrip` to `/root` + `chmod +x` to run it. It is also **flaky for git** (caused this incident).
- **Do git work in a FRESH full clone on `/root`**, not in the FUSE working tree. **Never** `git add -A` / `git add src/` in a partial-checkout clone.
- Shell is `/bin/sh` (no `mapfile`/process-substitution); gate scripts need `bash script.sh`. Use `grep -a` on post-AST source (UTF-8 α/β/γ/ω trips binary detection).

## FLAGGED — `gen_` collisions deliberately NOT stripped (kept to keep build green; need a naming decision)
- **`gen_bb_*` constructor family (~43)** in `lower_graph.c` — stripping to `bb_*` collides with emitter `bb_*` templates (`bb_to`, `bb_every`, `bb_not`, `bb_unop`, `bb_build`, `bb_initial`). Needs one consistent namespace decision.
- **Generic stems**: `gen_value`, `gen_type` (also a runtime field-name string), `gen_leaf`, `gen_runtime`, `gen_out`, `gen_gen_enter`; and camel `GenFrame`.
- **Uppercase icn-derived** left intact: `GEN_ENTER`, `FAIL_GEN_NODE`.
- **`bb_binop.cpp` statics**: `gen_is_numrel/strrel`, `gen_rel_to_tt`, `gen_to_sm`; plus `rt_gen_concat`.
- **4 files** still carry the token: `gen.h` (strips to an empty name — degenerate), `gen_runtime.c/.h`, `gen_value.h`.

## Suggested next steps
1. Decide the flagged `gen_`/file naming (esp. the `gen_bb_*` family vs emitter `bb_*`).
2. Optionally extend the comment purge to `.cpp`.
3. Resume GROUND ZERO 3 (Icon stackless, per `GOAL-ICON-BB.md`); rebuild gates if/when wanted (m2 was 6/6, FACT 20≤20, sm_dead 1≤1 earlier this session).
