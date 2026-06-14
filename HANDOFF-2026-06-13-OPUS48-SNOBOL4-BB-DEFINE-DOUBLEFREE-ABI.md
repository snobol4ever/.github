# HANDOFF 2026-06-13 · Opus 4.8 · SNOBOL4-BB — DEFINE smoke restored (double-free + M4 ABI)

**SCRIP HEAD:** e089608 (rebased onto concurrent 738b950)
**.github HEAD:** (this commit)

---

## Baseline entering session
SNO smoke **7/6/6** (M3+M4 `define` FAILing) · pat-rung 19/19/19 · fence HARD ·
broad corpus M2=182 M3=168 M4=158. Repo HEAD was 9baaf64 (`ir_delete_all` extended to all langs).

The `define` smoke (`DEFINE('DOUBLE(X)') ; OUTPUT=DOUBLE(21)` → `42`) had regressed in M3/M4.
The concurrent Raku commit 738b950 explicitly flagged "SNOBOL4 define FAIL pre-existing baseline" —
this session fixes the ROOT CAUSE.

## Result
SNO smoke **7/7/7** HARD · pat-rung 19/19/19 no-SKIP · fence HARD · ICON smoke 12/12/12 ·
broad corpus M2=182(=) M3=168(=) M4=158(=). **Zero regress any mode.** One commit (e089608).

---

## Two bugs, both surfaced by `ir_delete_all` physically freeing the IR (f0c3e29/9baaf64)

### Bug 1 — DOUBLE-FREE of the shared proc-view node array (M3 + M4 crash)
Symptom: `free(): invalid pointer` / SIGABRT. M3 at runtime teardown; M4 *during emission's*
post-write `ir_delete_all` (the `.s` was already fully written — crash is purely in the delete).

ROOT CAUSE: `lower_snobol4.c:1009` builds each user-proc graph as a **VIEW** over the main graph:
```c
IR_graph_t *fg = calloc(1, sizeof(IR_graph_t));
*fg = *g;            // shallow struct copy: fg->all ALIASES g->all (same node array, same nodes)
fg->entry = body;    // only the entry pointer differs
```
Both `g` and the view `fg` are added to `g_stage2.bbp`. Proven via instrumentation: the two graph
structs are distinct (`0x…ece0` vs `0x…d180`) but **share one `all[]` pointer** (`0x…20fc0`) and all
N nodes. Pre-`ir_delete_all` this was harmless (graphs never freed at runtime). Now
`bb_program_free → IR_free` runs `free(bbg->all)` **twice on the one shared array** → double-free.
(`IR_free` also `free(bb)`s each node; for a view every node is shared, so those would double-free too.)

FIX (in `bb_program_free`, `scrip_ir.c`): classify each graph **owner vs view** in a FIRST pass —
while all nodes are still alive — using the per-node `->own` back-pointer (set at `IR_node_alloc`,
the SOLE `IR_t` allocator; a view's nodes have `->own != fg`). Then free in a SECOND pass: owners
do full `IR_free` (nodes + `all[]` + struct); views `free()` their struct ONLY. **Two passes are
mandatory** — once the owner frees the shared array, the view's `all[]` dangles, so the
classification MUST precede any free (lazy `all[0]->own` check during the free loop = UAF).
Language-neutral: every non-SNOBOL4 graph is its own owner (`all[0]->own == self`), behaviour
byte-identical for them.

### Bug 2 — M4 `rt_proc_register` ABI mismatch (wrong param binding; empty output, no crash)
After Bug 1 was fixed, M4 `define` compiled+linked+ran but printed **nothing** instead of `42`.

ROOT CAUSE: `scrip.c` M4 `sno_proc_startup` text emission hand-wrote a **4-arg** ABI:
```
lea rdi,[name] ; xor rsi,rsi ; lea rdx,[pnames] ; mov ecx,nparams ; call rt_proc_register
```
but `rt_proc_register(const char *name, const char **pnames, int nparams)` takes **3** args
(rdi=name, rsi=pnames, rdx=nparams). So `pnames` landed in `rdx` (read as `nparams`), and `rsi=0`
became `pnames` → proc registered with **pnames=NULL** → `rt_call_named_proc` binds no params →
`X` never set in `DOUBLE`'s body → `X+X` reads null. FIX: drop the spurious 2nd arg so
name/pnames/nparams land in rdi/rsi/rdx — matching the (correct, compiler-generated) M3 C-call path
at `scrip.c:2780` (`rt_proc_register(pname, pn, np)`).

---

## Files touched (commit e089608)
- `src/contracts/scrip_ir.c` — `bb_program_free` two-pass owner/view classification (+13/-1).
- `src/driver/scrip.c` — M4 `rt_proc_register` 3-arg ABI (+2/-3).

Both respect C-style rules (no blank lines, no inline comments). Disjoint from concurrent 738b950
(runtime `rt.c`/`by_name_dispatch.c`/`rt.h`) — clean rebase, rebuilt + smoke re-verified post-rebase.

## Probes (M2==M3==M4, all = sbl semantics)
- `DEFINE('DOUBLE(X)') OUTPUT=DOUBLE(21)` → `42` (the smoke).
- `DEFINE('ADD3(A,B,C)') OUTPUT=ADD3(10,20,12)` → `42` (multi-param binding generalizes).

## NEXT (do-not-re-derive)
- **Conditional success-goto in proc bodies** is a SEPARATE pre-existing gap (M2 ALSO fails).
  Probe `DEFINE('FACT(N)') FACT = LE(N,1) 1 :S(RETURN); FACT = N * FACT(N-1) :(RETURN)` → all three
  modes abort, sbl gives 120. NOT touched/regressed here; it's `:S(RETURN)` + multi-stmt proc with
  conditional return, an all-mode lowering gap (out of scope for the smoke restoration).
- Resume the watermark's rung (b): `''+1`/`1+''`/`''+''` ADD-WITH-STRING coercion (M3/M4-only;
  `flat_drive_binop_tree`→`binop_slot_kind` emits empty for a string-operand ADD → `rt_bomb;ud2`).
  SPITBOL Ch.3 p.21: null string→0 in arithmetic; null-string CONCAT returns other operand UNCHANGED.
