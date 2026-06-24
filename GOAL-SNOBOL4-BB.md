<!-- GOAL-SNOBOL4-BB · SCRIP native pattern-match ladder for modes 3/4 (--run/--compile) -->

# ▶▶▶ NEXT SESSION — START HERE (handoff 2026-06-24, session 15)

## ▶ PRIORITY RUNG (do FIRST): PERF-GVA — Global Variable Array

**GVA-0 + GVA-1 + GVA-2 LANDED LOCAL — UNPUSHED, NOT YET COMMITTED — BLOCKED on push credential (per FACT RULE this is NOT "complete").** Built atop pristine `b3245a2`. **Proven:** zero regressions across all 262 crosscheck programs (stash/diff vs pristine baseline, +1 improvement `1012_func_locals`); bench **OK=14/16** (was 12), 0 FAIL, 2 pre-existing EVAL-path OOM crashes; **`var_access` rescued from >30s timeout → 15.9s**. Broad measured speedups: arith_loop 1630→654ms (**2.5×**), op_dispatch 1.76×, string_manip 1.68×, table_access 1.53×, func_call/func_call_overhead 1.44×, roman 1.34×, fibonacci 1.24×.

**▶ IMMEDIATE NEXT MOVE: GVA-3** (fused integer arith + relop — see §GVA-3 below). In `arith_loop`'s hot loop two calls remain: `rt_gvar_get_int` (the `N = N + 1` read) and `rt_call_arr` (the `LT(N,1000000)` relop). GVA-3 turns both into inline `mov rax,[rbx+kN*16+8]` + `add`/`cmp`. Then GVA-4 (indirect `$X`), then OPSINGLE / REC-COV.

**Files touched for GVA-0/1/2 (ALL UNCOMMITTED):**
- `runtime/core/core.c`: `NV_t` +`cell`/+`is_gva`; `NV_GET_fn`/`NV_SET_fn`/`NV_PTR_fn` forward through `cell` when `is_gva`; +`NV_bind_gva`. `core.h`: prototypes for `NV_bind_gva`, `gva_register`.
- `runtime/rt/rt.c`: +`gva_register(names, cells, n)` (loops `NV_bind_gva`, returns base).
- `emitter/emit_bb.c`: GVA name table + `gva_name_eligible` (excludes `&`-vars + keyword/IO set) + `gva_index_of` + `gva_collect_var` + `gva_collect_graph`; +`g_gva_active` flag.
- `emitter/emit_core.c`: `walk_bb_node` preamble sets `op_gva_k = g_gva_active ? gva_index_of(sval) : -1`. `emit_globals.h`: +`op_gva_k` field.
- `driver/scrip.c` (mode-4 preamble only): collect main-glob globals → emit `__gva` (`.bss`) + `__gva_names` (`.rodata`) + `gva_register@PLT` + `mov rbx,rax`; wrap the main-glob `gvar_flat_chain_build_text` in `g_gva_active`.
- Templates: `bb_var.cpp` (read), `bb_gvar_assign_descr.cpp`/`bb_gvar_assign_call.cpp` + `bb_gvar_assign.cpp` binop arms (write) — GVA arm stores/loads via `RDQ("rbx", k*16)`; works both mediums (rbx=reg3, no SIB).

**Design guards (proven by the green crosscheck):** (a) fast-path gated on `g_gva_active` (main-glob only) — procs read GVA globals via the slow `NV_GET_fn`, which forwards through the cell, so a proc-local accidentally lowered as `IR_VAR` can never alias a main-glob GVA slot (the roman-class trap). (b) keyword/IO names excluded from collection → never assigned a slot → `NV_SET_fn` keyword semantics (`&TRIM` etc.) preserved. (c) `rbx` is callee-saved, set once in `main:` before `flat_α`; the `concat_parts` scratch block still push/pops it. (d) **OPEN RISK:** direct GVA stores bypass `comm_var` (monitor/`&TRACE` notify) — crosscheck is green so harmless for the current corpus, but confirm before relying on tracing a hot global.

**Also landed (turn 1, UNCOMMITTED) — roman/local-var fix:** `lower/lower_snobol4.c:1158` `nparams = np` → `np + nl`. SPITBOL requires *all* locals (not just formals) saved on entry / restored on return; the old value under-counted save-slots so recursive `T` was corrupted across frames. Fixes benchmark `roman` (`MDCCLXXVI`) and crosscheck `1012_func_locals`. (Crosscheck `100_roman_numeral` still red — separate pre-existing issue, likely the `**` POW cluster.)

**Build:** `apt-get install -y libgc-dev && make && make libscrip_rt`. Oracle: `git clone …/x64 /home/claude/x64; sbl -b`. Tri-probe: `scrip --compile p.sno > p.s; gcc -no-pie -x assembler p.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs `sbl -b`. Bench/crosscheck gates: `scripts/test_bench_snobol4_modes.sh`, `scripts/test_crosscheck_snobol4.sh`.

---

## Prior context (session 13 — literal-subject native scan, now history)

roman's scan 2 (`'0,1I,…,9IX,' T BREAK(',') . T`) declined native because `flat_drive_scan_stmt` gated on a *named* subject only. Four-layer fix landed: `emit_bb.c` gate accepts `op_scan_subj_lit`; `flat_drive_scan_native` attaches an `IR_LIT_S` operand to `IR_SUBJECT`; `bb_subject.cpp` lit arm fixed (`mov→lea`, `bb_subj_litlbl()`, `rt_subject_load_lit`); `pattern_match.c` `rt_subject_load_lit` sets ζ-slot AND `Σ`/`Σlen`. Roman's earlier `MCXI` (recursive re-descent) symptom was resolved by the turn-1 local-var fix above. Roman reproduction:
```snobol4
    &TRIM = 1
    DEFINE('ROMAN(N)T')                   :(RE)
ROMAN N RPOS(1) LEN(1) . T =              :F(RETURN)
    '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' T BREAK(',') . T :F(FRETURN)
    ROMAN = REPLACE(ROMAN(N), 'IVXLCDM', 'XLCDM**') T :S(RETURN)F(FRETURN)
RE  R = ROMAN('176')
    OUTPUT = 'RESULT=' R
END
```

**Design note (carried):** the `walk_bb_node` preamble clobbering `op_a_sval` from `operands[0]` is the ambient-`g_emit` class flagged in session 12; the general cure (port-field reset / FILL-only / debug gen-counter assert) is still unbuilt.

---

# Open rungs (not yet started)

## PERF-GVA — Global Variable Array: eliminate GST hash lookup on hot path

### Naming

| Abbrev | Full name | What it is | Register | Access |
|--------|-----------|------------|----------|--------|
| **GST** | Global Symbol Table | Hash dictionary: name→DESCR_t. Runtime/dynamic. Currently called NV. | `rbp` (BBREG_HASH) | by name string |
| **GVA** | Global Variable Array | Flat `DESCR_t[N]` for compile-time-known globals. Static `.data`. | `rbx` (BBREG_BASE) | by integer index k |
| **LVA** | Local Variable Array | Per-call-frame `DESCR_t` slots for procedure locals/params. Already exists as ζ-frame. | `r12` (BBREG_ZETA) | by byte offset |

**The problem:** every global variable read is `call NV_GET_fn@PLT` (hash walk + string compare). Every write is `call rt_gvar_assign_*@PLT`. For `arith_loop` at 1M iterations that is ~14 PLT+hash calls per iteration. SPITBOL bakes variable addresses into code at compile time — zero calls per access.

**The fix:** at compile time, assign each program-global variable name an integer index k. Emit a flat `DESCR_t __gva[N]` array in the program's `.data` section. At preamble, call `gva_register(names, __gva, N)` which (a) populates `__gva[k]` = current GST value (null for new vars), (b) sets `GST_t.is_gva=1` and `GST_t.cell=&__gva[k]` so existing `NV_GET_fn`/`NV_SET_fn` paths transparently read/write through the GVA cell, (c) returns `__gva` base. Preamble stores that base in `rbx`. Templates then access `[rbx + k*16]` — two `mov` instructions, zero calls.

**GC safety:** `__gva` lives in `.data` (static storage, not GC heap). `DESCR_t.s` string payloads are still GC-managed heap pointers written into the cell — BDW scans `.data` as a root, so strings in GVA cells are reachable and not collected. The cell address itself never moves.

**GST forwarding invariant:** after `gva_register`, every GVA-backed variable in GST has `is_gva=1` and `cell→__gva[k]`. `NV_GET_fn` returns `*cell`; `NV_SET_fn` writes `*cell`. Dynamic paths (indirect refs `$X`, EVAL) that resolve to a GVA-backed name still work correctly at the cost of one extra pointer dereference — no correctness regression.

---

### GVA-0 — Infrastructure: GST forwarding flag + gva_register runtime  ✅ DONE (local, unpushed)

**GVA-0a — `GST_t` (rename from `NV_t`) gains `is_gva` + `cell`:**
In `src/runtime/core/core.c` (binary; edit via patch or sed):
```c
typedef struct _VarEntry {
    char              *name;
    DESCR_t            val;    /* live value when is_gva==0 */
    DESCR_t           *cell;   /* points into __gva when is_gva==1 */
    int                is_gva;
    struct _VarEntry  *next;
} GST_t;   /* was NV_t */
```
`NV_GET_fn`: `if (e->is_gva) return *e->cell;` before returning `e->val`.
`NV_SET_fn`: `if (e->is_gva) { *e->cell = val; return val; }` before writing `e->val`.
`NV_PTR_fn`: `if (e->is_gva) return e->cell;`
**Rename `NV_t` → `GST_t` throughout `core.c`.** Public API names `NV_GET_fn`/`NV_SET_fn`/`NV_PTR_fn`/`NV_CLEAR_fn` keep their names for now (rename is a separate rung, not required for correctness).

**GVA-0b — `gva_register` in `src/runtime/rt/rt.c` + `rt.h`:**
```c
/* Register N compile-time globals. Returns cells base (stored in rbx by preamble). */
DESCR_t *gva_register(const char **names, DESCR_t *cells, int n);
```
Implementation: for k in 0..n-1: find-or-create GST entry for `names[k]`; copy existing `e->val` into `cells[k]`; set `e->is_gva=1`, `e->cell=&cells[k]`.
**Exclude** names where `NV_PTR_fn` returns NULL (INPUT, OUTPUT, PUNCH, keyword `&`-prefix vars) — these stay GST-only, no GVA slot.

**GVA-0c — emitter: GVA name collection in `emit_bb.c`:**
New pass before any box emission: walk all IR nodes, collect distinct `op_sval` names for `IR_VAR`, `IR_ASSIGN`, `IR_BINOP_GVAR_ARITH`, `IR_BINOP_GVAR_ARITH_SLOT` that are non-keyword, non-`&`-prefix, non-INPUT/OUTPUT. Assign each a slot index k (stored in a new `int g_gva_slots[]` parallel to a `const char *g_gva_names[]` table, max 1024 entries). Store per-name GVA index in a lookup table `gva_index_of(name) → k` used by all templates.

**GVA-0d — emitter: emit `__gva` array + preamble call in `xa_flat.cpp` / `xa_prologue.cpp`:**
In TEXT mode, after `.section .data` banner:
```asm
  .align 16
__gva:
  .space N*16, 0
__gva_names:
  .quad .Lgvan0, .Lgvan1, ...   /* N name pointers */
  .section .rodata
.Lgvan0: .string "VARNAME0"
...
  .section .text
```
In preamble (before first user BB):
```asm
  lea rdi, [rip + __gva_names]
  lea rsi, [rip + __gva]
  mov edx, N
  call gva_register@PLT
  mov rbx, rax              /* rbx = __gva base for lifetime of program */
```
Also `push rbx` / `pop rbx` around any call that may clobber it per ABI — but since `rbx` is callee-saved in SysV ABI, callees preserve it automatically. No push/pop needed around `call` instructions in templates.

**GVA-0e — update `bb_regs.h` comment block** to document `rbx=GVA base` and `rbp=GST hash base` with new names.

**Gate GVA-0:** compile `arith_loop.sno` → verify `__gva` in `.s`; link and run → output identical to oracle; `gva_register` called once; `NV_GET_fn("N")` returns value through `e->cell`.

---

### GVA-1 — Direct load: IR_VAR global read → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** In `bb_var.cpp` (and `bb_var_global.cpp` if separate), when `gva_index_of(_.op_sval) >= 0` (name has a GVA slot), replace `call NV_GET_fn` with inline load.

Add to `emit_globals.h` `sm_emit_t`:
```c
int op_gva_k;   /* GVA slot index for this node, -1 if GST-only */
```
Populated in `emit_bb.c` `walk_bb_node` preamble alongside existing `op_sval` fill.

Add to `x86_asm.h`:
```c
inline const char *GVAQ(int k, int hi) {
    static char b[8][40]; static int i; i=(i+1)&7;
    snprintf(b[i],40,"qword ptr [rbx + %d]", k*16+hi);
    return b[i];
}
```

`bb_var.cpp` new first arm (checked before existing `g_gvar_flat_chain` arm):
```cpp
(_.op_gva_k >= 0) ?
  x86("comment", "IR_VAR gva")
+ x86("label",   _.lbl_α)
+ x86("mov",     "rax", GVAQ(_.op_gva_k, 0))
+ x86("mov",     "rdx", GVAQ(_.op_gva_k, 8))
+ x86("mov",     FRQ(_.op_off),     "rax")
+ x86("mov",     FRQ(_.op_off + 8), "rdx")
+ x86("jmp",     "γ")
+ x86("def",     "β")
+ x86("jmp",     "ω") :
```

**Gate GVA-1:** `grep "call NV_GET_fn" arith_loop.s` == 0; full `test_crosscheck_snobol4.sh` oracle-identical.

---

### GVA-2 — Direct store: IR_ASSIGN global write → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** Replace `call rt_gvar_assign_int` / `call rt_gvar_assign_descr` / `call rt_gvar_assign_var` / `call rt_gvar_assign_lit_i` / `call rt_gvar_assign_lit_s` with inline stores when the destination name has a GVA slot.

Integer literal store (`N = 5`), DT_I=6:
```asm
mov dword ptr [rbx + k*16],     6
mov dword ptr [rbx + k*16 + 4], 0
mov qword ptr [rbx + k*16 + 8], IMM
```

DESCR_t from frame slot (result already split lo=rax hi=rdx):
```asm
mov qword ptr [rbx + k*16],     rax
mov qword ptr [rbx + k*16 + 8], rdx
```

Steps:
- GVA-2a: `bb_gvar_assign.cpp` — integer and descr paths
- GVA-2b: `bb_gvar_assign_lit_i.cpp`, `bb_gvar_assign_lit_s.cpp`
- GVA-2c: `bb_gvar_assign_var.cpp` — var→var copy through GVA
- GVA-2d: `bb_gvar_assign_call.cpp`, `bb_gvar_assign_concat.cpp`

**Gate GVA-2:** `grep "call rt_gvar_assign" arith_loop.s` == 0; crosscheck suite green.

---

### GVA-3 — Fused integer arithmetic: IR_BINOP_GVAR_ARITH fully inline  ◀ NEXT MOVE

**Mandate:** `N = N + 1` where both operands and destination are GVA-backed integer vars emits zero calls. Detect in `bb_binop_gvar_arith.cpp` when `op_parts` names all have GVA slots.

`N = N + 1` (add, immediate RHS):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]   /* N.i */
add rax, 1
mov dword ptr [rbx + kN*16],     6      /* DT_I */
mov dword ptr [rbx + kN*16 + 4], 0
mov qword ptr [rbx + kN*16 + 8], rax
```

`LT(N, 1000000) N` (relop predicate, GVA int vs immediate):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]
cmp rax, 1000000
jge β_port
/* success fall-through: value = N.i already in rax */
```

Steps:
- GVA-3a: `bb_binop_gvar_arith.cpp` fused path for GVA+GVA and GVA+IMM
- GVA-3b: new `bb_gvar_relop.cpp` for `LT`/`GT`/`LE`/`GE`/`EQ`/`NE` on GVA int operands — emits `cmp` + conditional jump, replaces `call rt_call_arr@PLT`

**Gate GVA-3:** `arith_loop.s` hot loop body (label `LOOP` to next label) contains zero `call` instructions; `fibonacci.s` same; timing run shows ≥5× improvement over baseline on `arith_loop`.

---

### GVA-4 — rbp GST hash path for runtime indirect refs (optimization, not correctness)

**Mandate:** `$X` where X's runtime string value names a GVA-backed variable: use `rbp`-based hash index to skip full GST walk.

New runtime helper `gva_lookup_by_name(const char *name) → int k` (returns -1 if not GVA-backed). Emitted in `.data` beside `__gva`:
```asm
__gst_idx:
  .space GVA_HASH_SIZE*4, 0xff   /* uint32_t[GVA_HASH_SIZE], sentinel=0xffffffff */
```
Preamble fills `__gst_idx` with (hash(name) → k) entries after `gva_register`.

Template for indirect read, fast path:
```asm
/* name string ptr in rdi */
call gva_hash_probe@PLT     /* (rbp, rdi) → k or -1 */
test eax, eax
js   .gst_slow
mov  rdx, qword ptr [rbx + rax*16 + 8]
mov  eax, dword ptr [rbx + rax*16]
jmp  γ
.gst_slow:
call NV_GET_fn@PLT
```

This is an optimization rung — correctness is guaranteed by GVA-0b's `is_gva` forwarding regardless of this rung. Do GVA-4 only after GVA-0 through GVA-3 are green and benchmarked.

**Gate GVA-4:** indirect-ref crosscheck programs (`014_assign_indirect_dollar`, `015_assign_indirect_var`) oracle-identical; `arith_loop` timing unchanged (no indirect refs in that benchmark).

---

### Expected performance impact

| Rung | Calls eliminated per `arith_loop` iteration | Estimated speedup |
|------|---------------------------------------------|-------------------|
| GVA-1 | 2 × `NV_GET_fn` | ~2× |
| GVA-2 | 2 × `rt_gvar_assign_*` | +1.5× |
| GVA-3 | `binop_apply` + both assign calls | closes to ~10× baseline |
| GVA-4 | partial `NV_GET_fn` for indirect | marginal on arith |

---

## OPSINGLE — delete operand_aux, one channel only

**Mandate:** exactly ONE operand channel: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`).

Writers still aux-only (add `ir_operand_push`, keep aux until readers flipped): `lower_snobol4.c` CALL args, `lower_icon.c:134,137,315`, `lower_raku.c:210`, `lower_pascal.c:147,162,177,340`, `lower_prolog.c:140`.

Readers to flip (`bb_operand_aux_get` → `nd->operands[]`): `BB_templates/bb_call.cpp:98`; `emit_bb.c:350,411,438,846,1072,1492,1818,2489,2957(DELETE bridge shim),3035,3240,3335,3398,3458`; `driver/scrip.c:102,245,1931`; `contracts/scrip_ir.c:355`.

Delete last (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all call sites.

**Gate:** `grep operand_aux src/` (excl attic) == 0 AND all language gates green.

## REC-COV — community-recognized corpora

**Mandate:** extend coverage into community corpora. PB-GREEN stays session-first.

Inventory (pass-rates unmeasured — RC-0's job):
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/csnobol4-suite/` — 124 `.sno` WITH `.ref` ← start here
- `corpus/programs/snobol4/demo/` — 18 `.sno`

Steps: RC-0 honest runner + oracle-gen refs + triage table → RC-1 csnobol4-suite → RC-2 gimpel → RC-3 demo → RC-4 promote counts to hard floors → RC-5 re-ground "10×" claim.

---

# Completed / superseded (summary only)

Sessions 1–12 built the full SNOBOL4-BB ladder bottom-up:
- **DDS-0** (session ~8): deleted all `bb_*_proto[]` byte arrays, `DTP_t` head, `rt_dtp_run`. Ground-zero rebuild.
- **TR-1** (`7d6a9c9`): `sno_leaf_buildable` extended for `TT_CAPT_COND_ASGN`; capture patterns routed to builder, not orphaned.
- **TR-LEN** (`75f97e5`): `bb_build_len_blob` allocates `IR_MATCH_LEN` (matcher), not `IR_PATTERN_LEN` (builder). `r1`→`W=CD`.
- **Rename** (`2e5a5a3`): `IR_PAT_*` → `IR_MATCH_*` throughout.
- **TR-BREAK** (`15bda9d`): `bb_pattern_break.cpp` + `bb_build_break_blob`. First ζ-slot box; proves frame mechanism end-to-end.
- **TR-CAPTURE** (`1e962ed`): `bb_build_break_capture_blob`; `PAT=BREAK(',') . W`→`W=alpha`.
- **TR-CAT** (`5d6e7cd`): `bb_build_break_cap_lit_blob`; `PAT=BREAK(',') . W ','`→`W=alpha`.
- **splice fix** (`9ea1251`): `bb_scan_splice_empty` stripped of stale port scaffolding; string_pattern + mixed_workload GREEN.
- **literal-subject scan** (`f3f7cdb`, session 13): gate + `IR_LIT_S` operand + `bb_subj_litlbl` + `rt_subject_load_lit`. Last bomb removed.

Architecture constants (do not re-derive):
- `walk_bb_node` preamble (emit_core.c:328–333) overwrites `op_sval`/`op_ival`/`op_a_sval`/etc. from node+operands every emission — never rely on ambient values set before `FILL`.
- `rt_cap_assign_cursor` reads global `Σ` (set by `rt_subject_load_nv` and now `rt_subject_load_lit`).
- `flat_drive_cat_arms` reads the kids channel (`IR_EXEC(cat).counter`), NOT `operands[]`; a CAT with `nkids==0` emits empty.
- `bb_build_flat` entry CAT with nkids==0 emits empty — kids channel is mandatory.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
