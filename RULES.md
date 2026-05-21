# RULES.md — snobol4ever Working Rules

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — NEVER RESTORE DELETED INTERPRETER CODE (SJ4-JS-BB0)                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  Session (Claude, 2026-05-16) deleted sno_engine.js and pattern-interpreter sections from      ║
║  sno_runtime.js. These files are GONE FOREVER. Do NOT restore them, do NOT re-add pattern      ║
║  interpreter code, do NOT call back to an interpreter from emitted JS code.                    ║
║                                                                                                  ║
║  Pattern matching in JS emitter MUST emit actual Byrd-box-style factories that implement       ║
║  α/β/γ/ω ports as closures / function methods. Every SM_PAT_* opcode emits a factory function. ║
║  SM_EXEC_STMT pops the factory from stack and emits code that wires and runs the match         ║
║  engine. No data structures. No interpreter. Only Byrd semantics.                              ║
║                                                                                                  ║
║  This rule is binding on every future JS emitter work, including GOAL-SN4-JS-EMIT-*,           ║
║  and by extension applies to JVM, .NET, WASM emitters too (NO DATA-DRIVEN PATTERN MATCHING).    ║
║                                                                                                  ║
║  Violation: commit a file that re-adds sno_engine.js or pattern interpreter code = REJECTION.  ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C function with (void *zeta, int entry) signature is:                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║  (icn_lazy_box, formerly named here as a permitted shim, was deleted in DAI-7b 2026-05-17       ║
║   after empirical proof of zero callers — the reservation outlived its inhabitant.)             ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — NO AST WALKING IN MODES 2, 3, OR 4 — NEVER RESTORE — READ BEFORE WRITING    ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  Modes 2 (SM interp), 3 (SM → x86 in-memory JIT), and 4 (SM → GAS asm text) are AST-free.       ║
║  No code reached from sm_interp_run, sm_jit_run, or any src/emitter/*.c template may walk        ║
║  a tree_t* node — no dereference, no ->t, ->c[], ->n, ->v access; no calls to                   ║
║  interp_eval, bb_eval_value, icn_bb_build, pl_unified_term_from_expr, icn_scope_patch,           ║
║  interp_exec_pl_builtin, pl_pred_table_lookup_global, or any other AST-walking helper            ║
║  from modes 2/3/4.                                                                               ║
║                                                                                                  ║
║  Sess 2026-05-15g (Lon directive) stubbed all such sites with                                    ║
║      fprintf(stderr, "[NO-AST] <opcode> stub: needs fresh SM/BB lowering\n");                    ║
║      st->last_ok = 0;   (or STATE->last_ok = 0 in mode 3)                                        ║
║  Each stub fingerprint names the exact opcode that still needs fresh SM/BB lowering.            ║
║                                                                                                  ║
║  If your gate fails with a `[NO-AST] FOO` line: write fresh SM/BB code for FOO.                 ║
║  Do NOT "fix" it by restoring the AST-walking call — that is the violation.                     ║
║  Do NOT route through proc_table_call, _usercall_hook AST fallback, or any other                 ║
║  back-door that hands a tree_t* to mode-2/3/4 code.                                              ║
║                                                                                                  ║
║  Mode 1 (`--ast-run` / `--ir-run`) is DELETED (CLI-3M-9, 2026-05-18). Flag deleted CLI-3M-10.   ║
║  interp_exec.c deleted. interp_eval() deleted. interp_eval.c deleted — contents moved to        ║
║  icn_runtime.c (builtins/kw), interp_globals.c, interp_hooks.c, interp_data.c.                  ║
║  Mode 1 no longer exists in the codebase or binary. Modes 2/3/4 remain AST-free.                ║
║  The `--interp` flag is mode 2 (SM dispatch loop). There is no mode 1.                          ║
║                                                                                                  ║
║  This rule applies to every language session — Icon, Prolog, Snocone, SNOBOL4, Rebus, Raku.     ║
║  No language-specific exception. If your frontend lowers to SM_Program / IR_block_t, that       ║
║  lowered form is what mode 2/3/4 sees; the AST is invisible to them.                            ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

### Icon-specific addendum (2026-05-17, IJ-DEL-ICN-AST + CLI-3M-10; updated CLI-3M-9 2026-05-18)

The Icon-specific `tree_t *` AST walker (`bb_eval_value` /
`bb_exec_stmt` / `icn_bb_build`) is amputated. Mode 1 (`interp_eval`)
is deleted (CLI-3M-9, 2026-05-18) — `interp_eval.c` no longer exists.
Reference path for Icon is `--interp` (mode 2) — the only flag-reachable
execution mode besides `--run` (JIT) and `--compile` (x86 asm). Icon
rung floor is `scripts/test_icon_all_rungs.sh` under `--interp` at
PASS=194 FAIL=36 XFAIL=35 TOTAL=265.


## Where rules belong

⛔ Rules live in `RULES.md` only. `PLAN.md` is navigation and state.
Watermarks and step state live in their Goal file — the Goal file is the
sole authority. Other docs and commit messages are potentially stale.

Before asserting anything about how a component works — build commands,
calling conventions, oracle location, file layout — check the relevant
REPO or Goal file first. Training data is wrong. Verify before asserting.

---

## Read the Goal's spec sections, not just the active rung

⛔ The active rung is the **next step**, not the destination. Before working, read every spec section in the Goal file — goal statement, "Done when", architecture, invariants, closed-rung trail. Properties named in any section are binding on every sub-rung touching that subsystem.

---

## Commit identity — always Lon, never Claude

```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

Set in every repo at session start. Every commit in every repo.

---

## Token — never on disk

Never write the token to disk.

---

## Handoff — commit → push → confirm hash → done

One sequence, no matter the trigger phrase:

1. Mark completed steps in Goal file (`- [x]`)
2. Update state variables (watermark, HEAD hash, pass counts, current step)
3. Update step ID in PLAN.md goals table
4. `git add -A && git commit -m "<clear description>"` on each touched repo
5. `git pull --rebase && git push` — code repos first, `.github` last
6. Confirm: `git log origin/main --oneline -1` shows your hash on remote
7. Done — the commit message IS the session record

Multiple sessions may push `.github` simultaneously. Always rebase before
pushing. Never `git push --force`.

**Emergency handoff** — same sequence, but note the breakage explicitly
at the top of the commit message and leave the incomplete step as `- [ ]`
with a note below it. Still push everything — a broken push is better than
no push.

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — SCRIP'S SNOBOL4 AND SNOCONE SEMANTICS FOLLOW SPITBOL — Lon, 2026-05-17       ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  **We strive to be like SPITBOL.** SCRIP's SNOBOL4 frontend and runtime, and SCRIP's Snocone     ║
║  frontend and runtime, follow SPITBOL semantics wherever a semantic choice exists. The case-    ║
║  sensitivity rule below is one specific instance of this principle; the principle applies to    ║
║  every choice of operator priority, built-in function argument validation, keyword behavior,    ║
║  pattern primitive semantics, data type coercion, and runtime error reporting.                  ║
║                                                                                                  ║
║  Why SPITBOL and not CSNOBOL4 / standard SNOBOL4: SPITBOL is the fastest, most polished, and    ║
║  most actively-used SNOBOL4 variant in the modern era. It is also our primary oracle (see       ║
║  "Oracles" section below). Aligning runtime semantics with the oracle keeps the byte-identity   ║
║  test honest and avoids divergence-by-design.                                                   ║
║                                                                                                  ║
║  Operational rules:                                                                              ║
║    • When SCRIP and SPITBOL produce different output on the same input AND we believe SCRIP is   ║
║      "right" by some other criterion, the burden of proof is on the other criterion. Default    ║
║      answer: fix SCRIP to match SPITBOL.                                                        ║
║    • When SCRIP's runtime behavior differs from SPITBOL because of an explicit design choice,   ║
║      that choice must be documented as a row in this rule's "Permitted divergences" table       ║
║      below. Undocumented divergences are bugs.                                                  ║
║    • When SPITBOL itself has a documented bug (Appendix D of the manual) and SCRIP fixes it,    ║
║      that's a permitted divergence — but the bug ID and the fix rationale must appear in        ║
║      "Permitted divergences" too.                                                               ║
║    • Library code shared across languages (e.g. `corpus/SCRIP/semantic.sc`) MUST be portable to  ║
║      SPITBOL — if the code only runs on SCRIP's Snocone runtime but errors out under SPITBOL,   ║
║      the code is wrong. (Example: 2026-05-17 — `qtag()` called `REPLACE(t, "'", "")` with       ║
║      unequal-length args; works in SCRIP's `REPLACE` but is ERROR 171 in SPITBOL. Source        ║
║      fix required: rewrite using portable pattern-strip idiom.)                                 ║
║                                                                                                  ║
║  Permitted divergences (must be enumerated explicitly; this list is the only authority):       ║
║    • DATATYPE case — see "DATATYPE case" section below. Open SN-27 will unify on UPPERCASE.    ║
║    • Case sensitivity — SCRIP is always case-sensitive (no `&CASE`); SPITBOL defaults to fold-  ║
║      to-upper. See the next ABSOLUTE RULE for the binding cross-language story.                 ║
║    • TBD: add rows as new divergences are explicitly chosen.                                    ║
║                                                                                                  ║
║  Known OPEN divergences (bugs to close — distinct from permitted divergences):                  ║
║    • REPLACE 2nd/3rd-arg length — SCRIP's `REPLACE(s, X, Y)` today accepts unequal-length X     ║
║      and Y (e.g. `REPLACE(t, "'", "")` removes apostrophes). SPITBOL's REPLACE is a character-   ║
║      mapping translation that requires `SIZE(X) == SIZE(Y)` and ERROR 171s on mismatch.         ║
║      Discovered 2026-05-17 by SCT-2 via parser_rebus.sc/parser_icon.sc/parser_raku.sc all       ║
║      breaking on transpiled `qtag`'s REPLACE call.  Workaround landed in corpus/SCRIP/          ║
║      semantic.sc (use `REPLACE(t, "'", 'x')` — same length).  Permanent fix needed: tighten     ║
║      SCRIP's REPLACE to match SPITBOL's character-mapping semantics and ERROR 171 on            ║
║      unequal lengths.  Tracked as GOAL-LANG-SNOBOL4 follow-up SN-REPLACE-EQ.                    ║
║                                                                                                  ║
║  Languages OUTSIDE this rule: Icon, Prolog, Rebus, Raku follow their own native semantics       ║
║  (ISO Prolog, Icon Programming Language reference, etc.) — SPITBOL conformance applies only to  ║
║  the SNOBOL4 lineage and Snocone (which lowers to a SNOBOL4-shaped runtime). The transpiler     ║
║  output for ALL six languages is portable SNOBOL4 and therefore inherits SPITBOL semantics by   ║
║  transitivity, per GOAL-PARSER-SC-TRANSPILE.md.                                                 ║
║                                                                                                  ║
║  Violation: a commit that introduces non-SPITBOL semantics in SCRIP's SNOBOL4 or Snocone        ║
║  runtime without an entry in "Permitted divergences" = rejection.                               ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — SCRIP IS CASE-SENSITIVE. NO FOLDING. ANYWHERE. — Lon, 2026-05-17            ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  All six SCRIP-supported languages are case-sensitive: SNOBOL4, Snocone, Rebus, Icon, Prolog,    ║
║  Raku. This is the cross-language compatibility story we tell the community.                    ║
║                                                                                                  ║
║  Historical SNOBOL4 programs that rely on automatic case-folding (`&CASE = 0`, `CASECL`,         ║
║  GTNVR folding, etc.) are NOT supported by SCRIP directly. A separate, standalone               ║
║  pre-processing tool is the right answer for those users — it will canonicalize identifiers     ║
║  before SCRIP sees them. SCRIP itself does ZERO folding.                                        ║
║                                                                                                  ║
║  Forbidden inside `one4all`:                                                                    ║
║    • Calls to `sno_fold_name`, `fold_strbuf`, or any equivalent on identifier paths             ║
║    • `strcasecmp` / `strncasecmp` for identifier comparison                                     ║
║    • `tolower` / `toupper` loops in lookup, register_fn, label resolution, DATA registration,   ║
║      OPSYN handling, _usercall_hook label-uppercase fallback (interp_hooks.c lines 64-68),      ║
║      sc_dat_find_type / sc_dat_find_field, or any function-table / variable-table site         ║
║    • `--case-sensitive` and `--fold-case` CLI flags — both removed. Case-sensitive is the      ║
║      only mode. No flag, no toggle, no keyword. `sno_fold_on` and its companion functions      ║
║      (`sno_set_case_sensitive`, `sno_get_case_sensitive`) are removed.                          ║
║    • `&CASE` keyword in scrip — assignment to `&CASE` is a no-op or an error                   ║
║                                                                                                  ║
║  SPITBOL (x64, x32) and CSNOBOL4 are exempt — those are legacy reference runtimes for           ║
║  oracle comparison, owned upstream, NEVER patched in one4all. See the "Source-of-truth"        ║
║  table at the end of this rule.                                                                 ║
║                                                                                                  ║
║  Cross-language imports: When SCRIP's Snocone or Rebus or Icon code references something       ║
║  declared in another language, the identifier must match byte-for-byte. No transparent         ║
║  rewrite. No silent fold. If the case is wrong, it's a compile error.                          ║
║                                                                                                  ║
║  Rationale: 60 years of SNOBOL4 case-folding has been a continuous source of bugs at the       ║
║  boundary between languages, between user code and runtime, between hand-typed source and       ║
║  EVAL'd strings, between the lex layer and the runtime layer. Snocone, Rebus, Icon, Prolog,    ║
║  and Raku are all natively case-sensitive. Folding only existed to placate one ancestor.       ║
║  The cost of supporting it crosses every codebase boundary; the benefit is zero modern         ║
║  programs that couldn't be served by a 50-line preprocessor.                                    ║
║                                                                                                  ║
║  Violation: any commit that re-introduces folding logic in one4all = rejection.                ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

### Implementation sweep (one rung's work, owned by next session)

The pivot above is binding immediately. The code sweep to enforce it is its
own rung; until that rung lands, existing fold call sites continue to exist
as no-ops (they have been no-ops under default `--case-sensitive` mode
anyway since SN-31). Sites to remove, by file:

| File | Sites |
|------|-------|
| `src/frontend/snobol4/snobol4.l` | `sno_fold_on`, `sno_set_case_sensitive`, `sno_get_case_sensitive`, `sno_fold_name`, `fold_strbuf`, every call into them. The lex layer hands identifiers downstream verbatim. |
| `src/runtime/snobol4/snobol4.c` | Every `sno_fold_name` call in `_DATA_` / `sno_DATA_register` (lines ~1502, 1518, 1527), `_VALUE_` (line ~1671), and the function-table population path (line ~2793, ~2805). |
| `src/runtime/snobol4/eval_code.c` | `sno_fold_name` calls at lines 118, 129, 239, 281. |
| `src/runtime/rt/rt.c` | `sno_fold_name` calls at lines 933, 940, 962, 976, 1109. |
| `src/driver/interp_data.c` | `_builtin_DATA` — already done; remaining: change `strcasecmp` to `strcmp` in `sc_dat_find_type` and `sc_dat_find_field` (lines 48, 55). |
| `src/driver/interp_hooks.c` | `_usercall_hook` uppercase-fallback at lines 64-68. Delete the toupper loop and the second `label_lookup(_uf)`. |
| `src/driver/scrip.c` | Remove `--case-sensitive` and `--fold-case` argument parsing and the `sno_set_case_sensitive(opt_case_sensitive)` call. |
| `src/runtime/snobol4/snobol4.c` keyword `&CASE` | Remove `&CASE` from the keyword set or make assignment a no-op with a one-time stderr warning. |

After sweep, `grep -rn "sno_fold_name\|strcasecmp\|fold_case\|case_sensitive" src/` returns ONLY:
* References inside SPITBOL/CSNOBOL4 oracle build directories (exempt).
* The removal commit's own comment trail saying "removed per ABSOLUTE RULE — SCRIP is case-sensitive."

### Source-of-truth for legacy oracle runtimes (unchanged)

SPITBOL and CSNOBOL4 are reference oracles for byte-identity comparison.
We do not patch them. If a future bug in them ever warrants a patch,
patch the source of truth, never the generated artifact:

| Runtime | Source of truth | Never patch |
|---------|----------------|-------------|
| SPITBOL x64 | `sbl.min` (processed via `asm.sbl`, `lex.sbl`, `err.sbl`) | `bootstrap/sbl.asm` (generated) |
| SPITBOL x32 | `s.min` | generated asm |
| CSNOBOL4 | `v311.sil` (processed by `genc.sno`) | `snobol4.c`, `isnobol4.c` (generated) |

Generated files carry a `/* generated from ... */` or `MACHINE
GENERATED` header. Edit the source and regenerate — never edit a
generated file even if the change would "stick" for one session,
because the next regeneration silently reverts it.

---

## No append-only huge files

⛔ Do **not** create or maintain append-only accumulating files (e.g.
`SESSIONS_ARCHIVE.md`). The git commit log is the permanent session record.
HQ docs are state, not history.

---

## Project files — keep small; don't preload reference material

⛔ Do **not** attach large reference files (PDFs, generated C, SIL
dumps, manual scans) as project-file attachments — they are preloaded
into every session's context window before the first message.  Add
them as **project knowledge** instead (retrieved on-demand via
`project_knowledge_search`).  Cloned repos already contain source.

**Target:** sessions open at < 20% context consumed.

---

## Debugging — gdb hardware watchpoints DO NOT work in this container

⛔ The session container does not expose ptrace's hardware debug
registers.  Every `watch <expr>` and `watch -location <expr>` is
silently a no-op — the watchpoint is created, the binary runs, the
watched memory changes, and the watchpoint never fires.  Verified
2026-04-27 with a trivial test program (`long g; g=42; g=100; g=200`
+ `watch g` — zero stops).

This is environmental, not a bug in the inferior.  Do **not** spend
session time chasing "watchpoint paradoxes" where a value clearly
changes but the watchpoint never trips — the watchpoint is broken,
not the inferior.

### What to use instead

| Need | Tool |
|------|------|
| Stop on the **first bad write** to a memory location | C-source instrumentation: write a `_check(site)` helper that asserts the value is in range and `__builtin_trap()`s on violation, then call it after every assignment site (find them with `grep -nE 'D_A\(VAR\)\s*[+\-]?=\|D\(VAR\)\s*=\|POP\(VAR\)' file.c`). Trap fires SIGABRT with a clean gdb backtrace. |
| Stop on the **first read** of a corrupt value | Same pattern, hook the read site with `assert(value_is_sane)` |
| Catch any access to a page | `mprotect()` the containing page read-only after init — works in containers where ptrace HW regs don't |
| Software watchpoint (gdb fallback) | `set can-use-hw-watchpoints 0; watch <expr>` — technically works but **absurdly slow** (instruction-stepping the entire inferior); only viable for tiny repros |

### Diagnostic patches — never commit them

`__builtin_trap()`, `_check()` helpers, `fprintf` to stderr, `mprotect` traps are debugging aids only. Revert before commit; ship the fix, not the instrumentation.

---

## Never patch corpus source to work around runtime bugs

⛔ Do **not** modify `.sno` or `.inc` source files to work around a problem
in the runtime unless the source itself is syntactically or semantically
wrong **and** that wrongness is confirmed by running the program under
SPITBOL (the oracle). If SPITBOL runs it correctly, the bug is in the
runtime — fix the runtime, not the source.

---

## Oracles — SPITBOL x64 primary; CSNOBOL4 retired except for Silly

### SPITBOL x64 — primary (and effectively sole) oracle
```
/home/claude/x64/bin/sbl          # binary
/home/claude/x64/                 # repo (snobol4ever/x64)
```

**Install: clone the repo. That's it.** `snobol4ever/x64` **ships with a prebuilt `sbl` binary at `bin/sbl`** — `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64` and the oracle is live. No build step required for routine validation work. The standard `interp` profile in `.github/snobol4ever_clone.sh` already includes x64; PLAN.md "Session Start" lists this as required alongside the standard three repos.

Rebuild from source only when patching SPITBOL itself (e.g. SN-26-spl-bridge for the IPC monitor wire, or systm.c clock change): `bash /home/claude/one4all/scripts/build_spitbol_oracle.sh`. The script is idempotent and SKIPs when `bin/sbl` already exists, so it's safe to run as part of any setup pipeline.

Always invoke with `-b` to suppress the version banner:
```bash
/home/claude/x64/bin/sbl -b file.sno
```
Derive `.ref`: `/home/claude/x64/bin/sbl -b file.sno > file.ref`
With includes: `-I/home/claude/corpus/programs/snobol4/demo/inc`

SPITBOL is the **oracle for all goals and all testing** (Silly excepted —
see below).

### CSNOBOL4 2.3.3 — RETIRED as a general oracle (Mon Apr 28 2026)

⛔ Do not use CSNOBOL4 for new work (FENCE bug open). Silly exception: CSNOBOL4 is sole oracle for `GOAL-SILLY-*` (bug-for-bug SIL fidelity). All other goals: SPITBOL only.

```
/home/claude/csnobol4/snobol4     # binary (Silly use only)
```
Build: `bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh`

`.ref` files are pre-baked in corpus.  SPITBOL not required to run
test gates.

### SPITBOL `-f` — fixed in SN-30 (x64 @ `cc68516`)

x64 `sbl -bf` accepts UPPERCASE SNOBOL4 source.  Beauty self-host
under `sbl -bf beauty.sno < beauty.sno` with
`SETL4PATH=".:<corpus/include>"` produces 649 lines byte-identical to
CSNOBOL4 HEAD `b3aeb9f` output (md5 `408fc788ca2ef425fc1f87e26d45a7a5`).

The double-function trick still requires `-bf` (case-sensitive) on
both oracles.  CSNOBOL4 `-bf` remains valid.

### SPITBOL include-path env var — `SETL4PATH`

SPITBOL's `-INCLUDE` directive searches `SETL4PATH`, not `SNOLIB` or
`SPITLIB`.  Source of truth: `x64/osint/port.h:293` `#define
SPITFILEPATH "SETL4PATH"`.  The `SNOLIB` name appears in code comments
in `sysif.c` but is not the env var actually read.  Colon-separated
paths supported (e.g. `SETL4PATH=".:/home/claude/corpus/programs/include"`).

### scrip include-path env var — `SNO_LIB`

scrip's SNOBOL4 frontend (`src/frontend/snobol4/snobol4.l`) searches
`SNO_LIB` for `-INCLUDE` directives.  Single-path only (not
colon-separated).  Also walks parent dirs of the input file looking
for a `lib/` sibling.  The `scrip.c` argv handling does **not** accept
a `-I` flag today; include resolution is env-driven only.

### Always uppercase `END`

SNOBOL4 `END` statement must always be uppercase regardless of oracle or
flag. `end` or `End` — never. All `.sno` files, all dialects, always.

### CSNOBOL4 case-sensitive mode — `-bf`

```bash
/home/claude/csnobol4/snobol4 -bf file.sno
```
`-b` suppresses banner. `-f` toggles folding OFF → case-sensitive. Default
is case-insensitive (fold to upper). Override with `-f` when needed.

### Double-function trick requires case-sensitive mode

```snobol4
               DEFINE('push_list(v)')
               DEFINE('Push_list(vs)')                      :(push_list_end)
push_list      dummy          =  stk_push_frame(v)
               push_list      =  .dummy                     :(NRETURN)
Push_list      Push_list      =  EVAL("epsilon . *push_list(" vs ")")  :(RETURN)
push_list_end
```
`push_list` and `Push_list` are distinct labels only under case-sensitive
mode. Run with CSNOBOL4 `-bf` or SPITBOL x64 `-bf` (SN-30 fixed the
lowercase-canonical keyword table; `-bf` now works on both oracles).

---

## Case-sensitive name space — always, for every .sno and .inc

⛔ **Every SNOBOL4 source file (`.sno`, `.inc`) runs in a case-sensitive
name space.** Mixed-case identifiers like `bSlash`, `fSlash`,
`semicolon`, `snoLine`, `UTF_Array`, `Push_list` are preserved
verbatim — they are **not** folded to `BSLASH`, `FSLASH`,
`SEMICOLON`, etc.

### How to invoke the oracles

| Oracle | Invocation |
|--------|------------|
| SPITBOL x64 (SN-30 build) | `/home/claude/x64/bin/sbl -bf file.sno` |
| CSNOBOL4 | `/home/claude/csnobol4/snobol4 -bf file.sno` |
| scrip (one4all) | `/home/claude/one4all/scrip ...` — case-sensitive by default (SN-31) |

`-b` suppresses the banner on the oracles; `-f` toggles folding OFF.
scrip is case-sensitive by default as of SN-31
(`snobol4.l:60 sno_fold_on = 0`).  `--case-sensitive` on scrip is a
no-op kept for backward compatibility with test scripts — pass or
omit, same result.  No flag today reverses to classic fold-to-upper;
if that mode is ever needed, add `--fold-case` in `scrip.c` and call
`sno_set_case_sensitive(0)`.

### Monitor output reports identifiers verbatim

Because the name space is case-sensitive, `scrip-monitor` DIVERGE
reports print identifiers exactly as they appear in source. A monitor
line like `BSLASH IR=)N~ SM=<BS byte>` means **a variable literally
named `BSLASH` is diverging** — it is not `bSlash` that was folded.
If a DIVERGE names `BSLASH` and the source defines `bSlash`, the
corpus file is wrong (or the source isn't the file you think it is)
— do not "fix" by case-folding in the runtime.

### Invariant for all one4all runtime code

No case folding on any .sno / .inc identifier path.  Ingress-at-lex
preserves the byte sequence the user wrote.  Casing decisions in
one4all happen only at the two boundaries already documented above
("Casing belongs at the ingress layer") — and for `.sno`/`.inc`
ingress, the canonical form **is** the source form.

---

## DATATYPE case — authoritative, intentional per runtime

| Runtime | DATATYPE case | Notes |
|---------|---------------|-------|
| SPITBOL x64 (primary oracle, `bin/sbl`) | lowercase — `"integer"`, `"pattern"`, `"string"` | **SN-27 will flip this to UPPERCASE** to match every other runtime below |
| SPITBOL x32 (`snobol4ever/x32`) | **UPPERCASE** — `"INTEGER"`, `"PATTERN"`, `"STRING"` | Source: `s.min` lines 5250-5308 (`DTC /STRING/` etc.).  Discovered 2026-04-21 during SN-25.x32 probe. |
| CSNOBOL4 (secondary oracle) | UPPERCASE — `"INTEGER"`, `"PATTERN"`, `"STRING"` | |
| one4all | UPPERCASE — `"NAME"`, `"PATTERN"`, `"STRING"` | Intentional — SIL SNOBOL4 spec.  Archive D-002. |
| snobol4dotnet | lowercase — matches x64 | User-defined DATA type names also lowercased via `ToLowerInvariant()`.  Open question SN-27f: flip to UPPERCASE too? |
| snobol4jvm | UPPERCASE | |

⛔ Do **not** modify any runtime's DATATYPE case behavior without
opening an explicit rung.  See SN-27 (`GOAL-LANG-SNOBOL4.md`) — the
work to unify on UPPERCASE is tracked there.

### Portable tests only

Any test that checks a DATATYPE result must be portable across case. Do
NOT hardcode `IDENT(DATATYPE(x), 'string')` or `IDENT(DATATYPE(x), 'STRING')`.
Compare against a runtime-derived token:
```snobol4
dSTRING  = DATATYPE('')
dPATTERN = REPLACE(DATATYPE(LEN(1)), &LCASE, &UCASE)
...
IDENT(REPLACE(DATATYPE(x), &LCASE, &UCASE), dPATTERN)  :S(ok)F(fail)
```
Any `.ref` file or driver that hardcodes `'PATTERN'`, `'STRING'`,
`'INTEGER'` etc. in a DATATYPE comparison is **invalid** and must be
rewritten before it can pass.

### `is.sno` is invalid

`IsSnobol4()` / `IsSpitbol()` use `IDENT/DIFFER(.NAME, 'NAME')` to
discriminate dialect. This check is no longer valid — snobol4dotnet uses
lowercase DATATYPE like SPITBOL but `.NAME` yields `'NAME'`. Any test
depending on `IsSnobol4()` / `IsSpitbol()` to gate behavior is invalid
for snobol4dotnet.

---

## SNOBOL4 pattern matching globals — always set both

```snobol4
               &ANCHOR         =  0
               &FULLSCAN       =  1
```

⛔ Never set `&ANCHOR = 1`. ⛔ Never omit `&FULLSCAN = 1`.

---

## NRETURN functions — dot-star calls

When a function is called via `*fn()` in a pattern (indirect call), the
function needs to return a NAME descriptor. Assigning to the function name
IS required when called via `. *fn()` (dot-star) because `.` needs a NAME
result — use `.dummy` as the return.

```snobol4
push_list   dummy = stk_push_frame(v)
            push_list = .dummy        :(NRETURN)
```

Error 021 ("function called by name returned a value") triggers only if
the function is called as a bare `*fn()` without `.`. Safe form: always use
`(epsilon . *fn())` or `(pat . tag) . *fn(tag)`.

---

## Snocone language facts

⛔ See `ARCH-SNOCONE.md` for the Snocone language spec and front-end
architecture. That file is the single source of truth for Snocone.
Working rules whose enforcement matters across all goals (e.g. case-
sensitivity, DATATYPE case) are kept in this file under their own
sections; the language spec itself lives in ARCH-SNOCONE.md.

---

## Test gate before every commit

Run the gate for your goal before committing. Do not commit broken builds.
The gate is defined in the Goal file or REPO file.

### Parallel-gating idiom (Lon directive, 2026-05-17j)

Multiple independent gate scripts can run in parallel — they share the
`scrip` binary and read disjoint corpus subtrees, so there's no
contention. The full smoke matrix (icon, prolog, raku, rebus, snocone,
snobol4, unified_broker, crosscheck_prolog) plus `test_icon_all_rungs.sh`
runs in roughly the wall-clock time of the slowest single gate (~icon
rung ladder, 60–90s) instead of the sum. Pattern:

```bash
cd /home/claude/one4all
( cd /home/claude/one4all && bash scripts/test_smoke_icon.sh > /tmp/g1.out 2>&1 ) &
( cd /home/claude/one4all && bash scripts/test_smoke_prolog.sh > /tmp/g2.out 2>&1 ) &
# ... etc, one '&' per gate ...
wait
for i in /tmp/g*.out; do echo "=== $i ==="; tail -1 "$i"; done
```

Each subshell needs its own `cd` — `&`-detached jobs don't reliably
inherit a `cd` from a chained `&&` in the parent shell. Use absolute
paths or repeat the `cd` inside each subshell.

Do NOT parallelize the flaky gate (see below) — measure that one
serially with 3-5 runs.

---

## Flaky gates — measure by median, not single runs

⛔ Some gates are inherently noisy in this container; a single-run
number is not reliable for measuring deltas between SHAs.  Always take
**median of 3–5 runs** when reporting honest-count or pass-count
deltas, on both the before-SHA and after-SHA.

### Known flaky gates

| Gate | Variance | Centered on | Likely cause |
|------|----------|-------------|--------------|
| _(none currently; `test_icon_sm_no_ast_walk.sh` was the documented flake — deleted 2026-05-17j as part of IJ-DEL-ICN-AST / CLI-3M-10)_ | | | |

Historical note: `test_icon_sm_no_ast_walk.sh` carried ~6 PASS-point variance across 5 runs at the same SHA (`rung24_records_*`, some `rung36_jcon_*` segfaulted intermittently under 8s timeout / Boehm-GC nondeterminism). The gate was deleted after the Icon AST walker was amputated: ABORT semantics ("mode-2 secretly calling the Icon walker") became structurally impossible. Mode-1/mode-2 parity is now measured by `test_icon_all_rungs.sh` under `--interp`, which uses a more generous timeout and a smaller variance window.

---

## Parallel frontend sessions (FI-11)

Each frontend owns a distinct subtree. Six sessions can develop
simultaneously with zero shared-file conflicts on the hot path.

### Inner-loop gate (per-session, before every commit)

| Session | Gate script |
|---------|-------------|
| SNOBOL4 | `bash scripts/test_smoke_snobol4.sh` |
| Icon    | `bash scripts/test_smoke_icon.sh` |
| Prolog  | `bash scripts/test_smoke_prolog.sh` |
| Raku    | `bash scripts/test_smoke_raku.sh` |
| Snocone | `bash scripts/test_smoke_snocone.sh` |
| Rebus   | `bash scripts/test_smoke_rebus.sh` |

### Merge gate (before pushing shared files)

```bash
bash scripts/test_smoke_unified_broker.sh   # must be PASS=31+ FAIL=0
```

### File ownership

| Path | Owner | Merge gate required? |
|------|-------|----------------------|
| `src/frontend/snobol4/` | SNOBOL4 session | No — smoke only |
| `src/frontend/icon/` | Icon session | No — smoke only |
| `src/frontend/prolog/` | Prolog session | No — smoke only |
| `src/frontend/raku/` | Raku session | No — smoke only |
| `src/frontend/snocone/` | Snocone session | No — smoke only |
| `src/frontend/rebus/` | Rebus session | No — smoke only |
| `src/runtime/interp/icn_runtime.c` | Icon session | Yes |
| `src/runtime/interp/pl_runtime.c` | Prolog session | Yes |
| `src/driver/interp.c` | Shared — coordinate | Yes |
| `src/driver/polyglot.c` | Shared — coordinate | Yes |
| `src/driver/scrip.c` | Shared — rarely touched | Yes |
| `src/ir/ir.h` | Shared — coordinate | Yes |
| `src/runtime/x86/sm_lower.c` | Shared x86 backend | Yes |
| `src/runtime/x86/sm_interp.c` | Shared x86 backend | Yes |
| `src/runtime/x86/bb_broker.c` | Shared x86 backend | Yes |

### EKind additions

Before adding a new EKind to `ir/ir.h`, open a `.github` issue naming: the
frontend requiring the new kind, the goal it belongs to, and the SM/BB
classification (functional → SM opcode, generator → BB pump). Coordinate
with any session that touches `sm_lower.c` or `interp.c`.

---

## Three-way diff for sweep goals

For GOAL-SILLY-SWEEP-FORWARD and GOAL-SILLY-SWEEP-BACKWARD: all three
sources simultaneously, one SIL instruction at a time:
1. `v311.sil` — the spec
2. `snobol4.c` — generated C ground truth (resolves all branch ambiguity)
3. `src/silly/sil_*.c` — our translation

Two-way (SIL + ours only) is wrong. All three, every line, no exceptions.

---

## Sync-step monitor — keyword catch-alls only, no source preprocessing

⛔ **The user's source is never modified to enable monitoring.**  No
Python injection.  No SNOBOL4 source-scanning driver that emits an
include file.  No `monitor_preamble.inc` for the user to add at the
top of their program.  No build step that produces an "instrumented"
copy of the input.  Source preprocessing of any kind is banned for
the sync-step monitor.

The instrumentation lives in the **C runtime** of each participant.
At process startup, the runtime checks env vars (`MONITOR_READY_PIPE`,
`MONITOR_GO_PIPE`) and opens the IPC connection.  The runtime's
existing CALL/RETURN/VALUE trace hooks fire on every event when the
catch-all keywords are non-zero, and those hooks write fixed-size
binary records (`monitor_wire.h` format) directly to the wire.  The
controller process reads each runtime's ready FIFO, compares records,
acks each step, and stops at the first divergence.

The user's `.sno` runs unmodified.

| Keyword | Effect | scrip | SPITBOL | CSNOBOL4 |
|---------|--------|-------|---------|----------|
| `&FTRACE = N` (N>0) | Fire CALL/RETURN trace event on every DEFINE'd function | ✓ on IPC wire (session #19) | needs runtime patch — currently routes only to stdout | needs runtime patch — same |
| `&TRACE = N` (N>0)  | Fire VALUE trace event on every variable assignment       | ✓ on IPC wire (session #19) | no native catch-all                                    | no native catch-all                                  |

Removed in session #19: `inject_traces.py`, `inject_traces_bin.py`
(source rewriters).  The controllers (`monitor_sync.py`,
`monitor_sync_bin.py`) and the C IPC libraries (`monitor_ipc_sync.c`,
`monitor_ipc_bin_csn.c`, `x64/monitor_ipc_bin_spl.c`) **stay** —
they are the cross-process comparison engine that reads each
runtime's ready FIFO.

The pre-#19 architecture loaded the IPC `.so` via SNOBOL4 `LOAD()`
calls injected into the user's source.  That violated this rule.
Bringing the oracles to scrip's standard requires patching their C
runtimes to read `MONITOR_READY_PIPE` at startup and bridging
`&FTRACE`/`&TRACE` events to the IPC wire directly — the same
treatment scrip already has in `runtime/x86/snobol4.c`.  Tracked as
an open question; not yet started.

---

## Sync-step monitor — read the divergence point, not the trace

⛔ Never read the full trace stream. The monitor reports exactly two records: last-agree and first-disagree. The bug lives between them. Read only those two records + matching source line numbers, fix, re-run.

---

## Session setup — run only what the Goal file lists

Session setup is defined in the Goal file's `## Session Setup` section.
Run exactly those scripts, no more. Do **not** run
`install_everything_full_stack.sh` for a specific goal unless the Goal
file explicitly lists it. If the Goal file has no `## Session Setup`
section yet, fall back to the matching category in `REPO-one4all.md`.

---

## Self-contained scripts — all scripts in one4all/scripts/

All scripts live in `one4all/scripts/`. One flat directory. No scripts
elsewhere except fixture-local glue scripts co-located with their test
assets.

⛔ Do **not** build or test anything by typing ad-hoc shell commands.
Every action must be driven by a checked-in script in `one4all/scripts/`.
If no script exists, write one, check it in, then run it.

### Naming — prefix declares type, snake_case, descriptive phrases

| Prefix | Meaning |
|--------|---------|
| `install_` | Fetch packages, clone repos, set up environment |
| `build_` | Compile source, produce binaries |
| `regenerate_` | Derive generated files from source (parser/lexer) |
| `run_` | Compile + execute a single file via a specific backend |
| `test_` | Run a test suite, report PASS/FAIL |
| `util_` | Ad-hoc developer tools, sweeps, one-off runners |

### Every script must be self-contained

1. **Paths derived from `$0`**, never from env vars:
   ```bash
   HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   SCRIP="${SCRIP:-$HERE/scrip}"
   ```
2. **Every `scrip` call gets `< /dev/null`** unless the test explicitly
   needs stdin. Zero cost, prevents hangs.
3. **Every `scrip` call gets `timeout N`** — 8s for unit/smoke tests,
   30s for corpus runners.
4. **Corpus path hardcoded** to `/home/claude/corpus`. If missing: clear
   SKIP message, exit 0. Never fail silently, never fail hard.
5. **Oracle paths hardcoded**: SPITBOL = `/home/claude/x64/bin/sbl`,
   CSNOBOL4 = `/home/claude/csnobol4/snobol4`. Same SKIP rule.
6. **`build_*` and `install_*` scripts are idempotent** — running twice
   is safe. Check before acting.
7. **No script sources another script's env** — each is standalone.

### Editing `.y` or `.l` files

1. Run `bash scripts/regenerate_parser_and_lexer_from_sources.sh` —
   regenerates `.tab.c`, `.tab.h`, `.lex.c`.
2. Commit the `.y`/`.l` source AND the updated generated files together
   in one commit.
3. Never edit `.tab.c` or `.lex.c` directly for grammar/lexer logic.
   Exception: epilogue functions hand-written directly in `.tab.c` (e.g.
   `sno_parse_string`) should be migrated to the `.y` epilogue section.

`bison` and `flex` are installed by `build_packages.sh`. Generated files
are committed so normal builds never require bison/flex.

---

## C code style — compact, 120-column, horizontal-first

- 120 character line maximum
- Brace on same line: `if (x) {`
- Short bodies on one line: `if (!p) return NULL;`
- Section dividers exactly 120 chars: `/*====...*/` major, `/*----...*/` minor

---

## Naming conventions (one4all C code)

| Origin | Convention | Example |
|--------|-----------|---------|
| SIL label → C function | `NAME_fn` | `APPLY_fn`, `FINDEX_fn` |
| SIL DESCR global → C typedef | verbatim + `_t` | `DESCR_t`, `SPEC_t` |
| SIL named global → C global | verbatim UPPERCASE | `XPTR`, `NEXFCL` |
| SIL EQU constant → C `#define` | verbatim UPPERCASE | `FBLKSZ`, `OBSIZ` |
| New C struct/enum (no SIL origin) | `Xxxx_yyy` one-cap | `Invoke_entry`, `Scan_ctx` |
| New C function (no SIL origin) | `snake_case` | `arena_init`, `genvar_from_descr` |
| Procedure return typedef | `RESULT_t` | always |

Never CamelCase. Never ALL_CAPS for new C types (exceptions: `RESULT_t` and the established SIL-derived family `AST_t`, `DESCR_t`, `STMT_t`, `SPEC_t` etc. — these predate the rule and are kept verbatim).

### ⛔ IR subsystem naming: uppercase `IR_` prefix throughout

The DCG is the IR.  `IR_t` (node) matches `tree_t`; `IR_prog_t` (graph) matches `SM_Program`.
All IR subsystem types and functions use uppercase `IR_` prefix, not lowercase `ir_`:

```
IR_t          -- one DCG node (matches tree_t)
IR_prog_t     -- the graph envelope: entry + flat node roster (matches SM_Program)
IR_kind_t     -- kind enum
IR_alloc()    -- allocate IR_prog_t
IR_free()     -- free IR_prog_t
IR_reset()    -- reset runtime state in all IR_t nodes
IR_print()    -- dump
IR_exec_once() / IR_exec_pump() -- graph-walk executor
IR_exec_node() -- per IR_t node eval dispatch
IR_lower_pat() -- build IR_prog_t from SNOBOL4 pattern tree
```

Rationale: `IR_` is visually distinct from `tree_t`, `DESCR_t`, `PATND_t`.
Lowercase `ir_` is hard to read in dense C code.


## Snocone parser style — names track the existing frontend; no goto unless required

⛔ When writing a Snocone `parser_<lang>.sc` (any of the six PARSER-*),
non-terminal pattern names MUST mirror the existing C frontend's
parse-function names (and ISO BNF non-terminal names where they
overlap). Token-classifier names MUST mirror the existing lexer's
`TK_*` enum (lowercased where Snocone identifier rules require). IR
node tags MUST be the exact strings `ast_dump` (or equivalent
frontend dumper) emits.

Sources of truth, in order:
1. The frontend's `.l` / lex header (token enum) and `.y` / parse module.
2. The lowering module's IR-tag enum and dumper.
3. The official BNF (ISO/IEC 13211-1 for Prolog; analogous standard
   for Icon, Raku, etc.) — only as a tiebreaker when (1) and (2)
   leave a name unspecified.

Invented names are reserved for the cross-PARSER spine (`Compiland`,
`Command`, `Push`/`Pop`/`Top` helpers, `tree`/`Tree`/`TDump`/`stack`).
Per-language non-terminals are not invented.

⛔ No `goto`/labels in `parser_<lang>.sc` driver loops or anywhere else
unless absolutely necessary for readability. Use Snocone structured
flow (`while ((Line = INPUT)) { ... }`, `if/else`, etc.). The legacy
`goto read_loop`/`goto read_done`/`goto mainErr`/`goto mainEnd` shape
in `parser_snobol4.sc` is grandfathered; new `parser_<lang>.sc` files
do not copy it. When touching one of the legacy parsers for an
unrelated reason, leave its goto-shape alone — replacing it is its
own task.

---

## No duplicate corpus source files

⛔ Do **not** have two copies of the same source file anywhere in corpus.
Applies to all corpus source: `.sno`, `.inc`, `.pl`, `.icn`, and any other
program source extension.

If a duplicate is discovered: keep the more authoritative copy (beauty/
over demo/inc/, crosscheck/ over a redundant subfolder, etc.) and delete
the other. Never resolve duplication with symlinks.

### Exception — self-contained demo programs

A demo or test program that is intentionally **self-contained** — runnable
from a single folder with no `-I` / `SETL4PATH` / `SNO_LIB` flags and no
references to files outside its own folder — is allowed to carry its own
copies of shared helper includes (`is.inc`, `FENCE.inc`, `io.inc`, etc.).
The duplication is the point: the folder is a sealed, portable unit that
runs identically on every runtime regardless of include-path support.

Current self-contained programs (kept verbatim with their includes):

| Folder | Notes |
|--------|-------|
| `programs/snobol4/demo/beauty/` | beauty self-host; carries `is.inc`, `FENCE.inc`, `io.inc` alongside its own 16 includes |

When such a duplicate exists, the canonical copy still lives in
`programs/include/`. Self-contained folders track that copy: if
`programs/include/io.inc` changes, every self-contained folder carrying a
copy must be updated in the same commit. CI / hand verification: a byte
diff between the two paths must come back empty.

---

## No symlinks

⛔ Do **not** use `ln -s` or any symlink creation in shell scripts,
Makefiles, or CI. Symlinks break silently when targets move or are deleted
(see corpus fbab26b incident). Use real files, copies, or path variables
instead.

---

## C code style — 200-character line width (all one4all C/H files)

**The goal:** wide lines, no wasted vertical space, no wasted horizontal space.

### Line width
- **200 characters maximum.** Wrap only when a line would exceed 200.
- No 80-col or 120-col limits. We own the editor.

### Vertical space — no blank lines anywhere
- **Zero blank lines in any C/H file** — not inside bodies, not between functions, not at top or bottom.
- Functions are separated by a minor separator line only (no blank line before or after it).
- **No blank line between a function signature and its opening `{`.**

### Separator lines
- `/*` followed by `-` repeated to column 200, then ` */` — minor section break; goes between every pair of functions and between logical groups.
- `/*` followed by `=` repeated to column 200, then ` */` — major section break (sparingly, for file-level divisions).
- Example minor: `/*---------- ... ----------*/` (total 200 chars including `/*` and `*/`).

### Comments — banners only, no inline comments
- **No inline or end-of-line comments** — no `// text` or trailing `/* text */` after code.
- **No comments inside function bodies.**
- When a function needs a comment, place a `/* Block comment. */` on the line immediately after the separator line, before the function signature. Single line preferred; wrap only when unavoidable.
- Example:
  ```c
  /*----...----*/
  /* Emit push rbp / mov rbp,rsp / sub rsp,8 — standard C ABI frame enter. */
  void emit_seq_frame_enter(void) {
      insn_push_rbp();
      insn_mov_rbp_rsp();
      insn_sub_rsp_i8(8);
  }
  ```

### Operators and star character
- **One space around ` * ` in all contexts** — pointer declarators, multiplication, dereference, comment borders. Never `int*x` or `*p`; always `int * x` or `* p`.
- One space around all binary operators: `a + b`, `x == y`, `p->field`.

### Braces
- **Omit `{` `}` when the body of `if` / `else` / `for` / `while` is exactly one statement.**
- Two or more statements always get braces.
- Opening `{` on the same line as the control keyword: `if (x) {`
- Closing `}` on its own line, same indent as the keyword.

### Horizontal packing — one-liners
- Short related functions that each fit in 200 chars **go on one line**:
  ```c
  int  foo(void) { return g_foo; }
  void set_foo(int v) { g_foo = v; }
  ```
- Use column alignment to make families of one-liners read as a table:
  ```c
  void insn_ret   (void) { if (IS_TEXT) t3("ret",   "");    else B(RET);           }
  void insn_nop   (void) { if (IS_TEXT) t3("nop",   "");    else B(NOP);           }
  void insn_push_r10(void){ if (IS_TEXT) t3("push", "r10"); else { B(0x41); B(0x50); } }
  ```

### Vertical alignment within a function
- Align `=` in sequences of assignments.
- Align argument columns in sequences of similar calls.
- Keep the pattern: declaration block → blank-free logic block → return.

### Conversion order
Convert files in this order (experiment on emitter first, then spread):
`emit_core.c` → `emit_bb.c` → `emit_sm.c` → `sm_jit_interp.c` → all headers.
