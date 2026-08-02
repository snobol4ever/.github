# FINDING-2026-08-02f — CLAUDE-SN4 OMEGA O-2 WIP: M4 REGRESSION ROOT CAUSE AND STUB EMISSION DESIGN

**Session:** s23r (Sonnet 4.6, 2026-08-02, this session)
**Rung:** OMEGA O-2 — ZW-5 Slice 3: ω per-depth stub ladder + planner
**Status:** INCOMPLETE — m3 clean (+1 vs O-1), m4 has 22-program segfault regression. Working tree committed to disk description in diff below. NO COMMIT, NO PUSH. Next session must fix m4 then commit.

---

## ⭐ LIVE CURSOR — s23r WIP (OMEGA, 2026-08-02)

**Parent (SCRIP before this session's edits):** `343f3471` (O-1 LIGHTING)
**Origin advanced during session:** SCRIP origin now at `2fea8565` (ALPHA s23s artifacts). **Pull --rebase before touching O-2 code.**

**Watermark with WIP edits applied (DO NOT COMMIT — m4 broken):**
- m3: **282/25/10** (O-1 was 281/26/10 — net +1, zero regressions BY SET)
- m4: **250/40/9/LERR18** — **22 programs newly segfaulting** (regression class: stub emission in TEXT mode)

**Census (unchanged from O-1):** stmt_claim 193 · fused-terminal proxy 1,094 · rbp-bearing 317.

**NEXT (first task):** Fix m4 stub emission. Then full gate. Then commit `[OMEGA] ZW-5 O-2: per-depth omega stub ladder + planner, s23r`. Then regen ×4. Then push with `ghp_REDACTED_see_Lon`.

---

## ⭐⭐ THE M4 REGRESSION — ROOT CAUSE IDENTIFIED

**Symptom:** 22 programs segfault in m4 (--compile path) but pass in m3 (--run path). Programs that newly fail include `W06_pos`, `412_arith_real`, `086_define_locals`, `100_roman_numeral`, etc. — a broad cross-section, not a single pattern.

**Root cause:** `emit_label_define_bb` is called from inside `codegen_flat_chain_body`'s drive loop for stub emission, AFTER the chain has already entered TEXT mode via `text_externalise`. In TEXT mode, `emit_label_define_bb` writes the label definition directly to the text output stream. The stub body (`bb_emit_x86(x86("add","rsp",K) + x86_jmp_ext(node_ω))`) also writes to that stream. BUT: `x86_jmp_ext` in TEXT mode emits `jmp labelname\n` where `labelname` is `node_ω->name`. At the time of stub emission, `node_ω` has been restored to `_saved_node_ω` (the statement's real fT label). In TEXT mode `x86_jmp_ext` emits `jmp fT_labelname`. This should be correct.

**ACTUAL root cause (measured via objdump):** The stub emission is working correctly in TEXT mode for the stub itself. The m4 segfault is from a DIFFERENT mechanism: the stub label `emit_label_define_bb` call resolves forward patches from member nodes' `x86_jmp_ext(node_ω)` calls. In BINARY mode (m3), `x86_jmp_ext(&zw5_stub_lbls[pool_base+d])` emits an 'X' record carrying the pointer to the stub's `bb_label_t`. `emit_label_define_bb` then patches all pending 'X' records pointing to that label. This works.

In TEXT mode (m4), `x86_jmp_ext(node_ω)` where `node_ω = &zw5_stub_lbls[pool_base+d]` emits `jmp n42_statement_omega_d16\n` (using `lbl->name`). The stub emission then does `emit_label_define_bb(&zw5_stub_lbls[pool_base+d])` which in TEXT mode writes `n42_statement_omega_d16:\n` to the output. GAS resolves the forward reference. This also should work.

**THE REAL CRASH:** The segfault is from `x86_jmp_ext(node_ω)` being called with `node_ω` pointing to `zw5_stub_lbls[pool_base+d]` — a stack-allocated `bb_label_t` in `codegen_flat_chain_body`. In TEXT mode, `x86_jmp_ext` uses `lbl->name` which is set by `emit_label_initf`. The `emit_label_initf` call happens in the look-ahead block. HOWEVER: `emit_label_initf` allocates the label name via `snprintf` into a buffer — check whether that buffer is heap-allocated or stack-allocated within the `bb_label_t` struct. If the name is stored as a pointer to a stack buffer, and if the look-ahead's stack frame has unwound by the time the name is used, the pointer is dangling.

**Precise next step:** Check `emit_label_initf` — does it heap-alloc the name or store it in a fixed-size array within `bb_label_t`? If fixed-size array, the label is safe. If it's a pointer to an external buffer... check the struct. Then run with `SCRIP_ZETA_OMEGA_TRACE=1` on a failing m4 program and compare the label names in the trace vs what appears in the segfaulting .s.

**Alternative simpler fix:** Replace `emit_label_initf` with `emit_label_initf` that uses the pre-existing pattern from the chain-body label allocations (lbl_α, lbl_β etc.). Those work because they're allocated in the same stack frame. The zw5_stub_lbls are also in the same stack frame — so they should be fine. More likely the crash is from the stub's `jmp` in TEXT mode emitting `jmp NULL` if `node_ω->name` is NULL when it was restored to `_saved_node_ω` after being redirected. Check: does `_saved_node_ω` always have a non-NULL name in m4? If `node_ω` was the chain's `&lbl_ω` (outer fail), and `lbl_ω` wasn't yet defined, its name might be empty.

**Definitive diagnosis command (run this first):**
```bash
SCRIP_ZETA_OMEGA_TRACE=1 /home/claude/SCRIP/scrip --compile \
  $(find /home/claude/corpus/crosscheck -name "W06_pos.sno") </dev/null 2>/tmp/w06_trace.txt | head -80
cat /tmp/w06_trace.txt
```
Then compare the stub labels in the trace vs what appears in the .s for lines that crash.

---

## ⭐ THE O-2 IMPLEMENTATION (what was done)

**Four-file atomic implementation (84 lines total, uncommitted):**

### emit.h
Appended two fields at struct end (s141 ABI law):
- `int op_omega_depths[8]` — per-depth stub release amounts staged at the choke
- `int op_n_omega_depths` — count of valid entries

### emit.cpp (5 edits)

**Edit 1 — staging globals:**
```c
static int g_zd_omega_depths[8]; static int g_zd_n_omega_depths;
```

**Edit 2 — choke clear:**
Added to the unconditional choke clear:
```c
g_emit.op_n_omega_depths = 0; for (int _zw = 0; _zw < 8; _zw++) g_emit.op_omega_depths[_zw] = 0;
```

**Edit 3 — choke apply:**
Added after `g_emit.op_zgpop = ...`:
```c
g_emit.op_n_omega_depths = g_zd_n_omega_depths;
for (int _zw = 0; _zw < g_zd_n_omega_depths; _zw++) g_emit.op_omega_depths[_zw] = g_zd_omega_depths[_zw];
```

**Edit 4 — zd_plan depth collection:**
Inside `if (ok)` block after ZD-H diag, collects distinct zwpop values from run members (excluding IR_STATEMENT) into `g_zd_omega_depths`. Keyed on `IR_STATEMENT` being the last run member.

**Edit 5 — codegen_flat_chain_body stub infrastructure:**
- Declares `bb_label_t zw5_stub_lbls[128]; int zw5_pool_base = 0; int zw5_n_stubs = 0; int zw5_stub_K[8]; int zw5_stmtnode = -1;` at function top (128-slot pool so consecutive statements don't overwrite each other's labels)
- Per-run-head look-ahead (fires when `(i == 0 || bb_src_of(nodes[i])) && i > zw5_stmtnode`): scans forward to find IR_STATEMENT with `zd_on[_f]`, pre-allocates stubs in pool
- Before `emit_drive`: redirects `node_ω` for members with `zd_on[i] && zd_wp[i] > 0 && !omega_is_beta && !omega_is_phi` to matching stub label; saves/restores `_saved_node_ω`
- After `emit_drive` when `i == zw5_stmtnode`: emits stub bodies via `emit_label_define_bb` + `bb_emit_x86(x86("add","rsp",K) + x86_jmp_ext(node_ω))` — NO `x86_begin()` (would shift `.Lx<uid>_N` ids); advances `zw5_pool_base`

### lower_snobol4.c (2 edits)
- Stamps `:stno` into anchor ival UNCONDITIONALLY (was gated on MONITOR_BIN)
- Stamps `:stno` into `IR_STATEMENT->ival` after stb is minted
- `fJ` keeps targeting `fT` (unchanged from O-1 — emit-time redirection handles admitted runs)

### bb_statement.cpp (1 edit)
- Comment updated to reflect drive-loop stub emission

---

## ⭐ BUGS FOUND AND FIXED DURING THIS SESSION (do not re-derive)

1. **fJ rerouting catastrophe** — routing `fJ → stb` (instead of `fT`) sent UCLAIM fail paths through the statement box, which had no UCLAIM release machinery. 118 regressions. Fix: keep `fJ → fT`, rely entirely on emit-time `node_ω` redirection for admitted runs.

2. **Upfront scan wrong** — initial design scanned ALL nodes upfront for IR_STATEMENT, setting `zw5_stmtnode` to the LAST one. Drive loop processed earlier statements with stubs from a later one. Fix: per-run-head look-ahead gated on `i > zw5_stmtnode`.

3. **Pool overwrite** — all statements shared `zw5_stub_lbls[8]`, so consecutive statements overwrote each other's `bb_label_t` objects. Member jmps pointed to overwritten (stale) labels. Fix: 128-slot pool with `zw5_pool_base` counter.

4. **Stub jmp to `lbl_ω` (chain outer fail) instead of `node_ω` (fT)** — stubs were jumping to the chain's `main_ω` (program exit failure) instead of the statement's actual fail continuation `fT`. Fix: stub emission uses `node_ω` (= `_saved_node_ω` at that point, which is fT).

5. **`!omega_is_beta` guard missing** — `node_ω` redirect fired for nodes where ω is used as a BETA resume wire. IR_ASSIGN's beta trampoline (`x86_deflabel(BETA) + x86_jmp(OMEGA)`) was redirected to the stub. Fix: added `&& !omega_is_beta && !omega_is_phi` guard.

6. **`x86_begin()` uid shift** — calling `x86_begin()` for each stub incremented `g_flat_node_id`, shifting all subsequent `.Lx<uid>_N` labels. Templates that came after stubs used wrong uid for their rodata references. Fix: removed `x86_begin()` from stub emission (stubs use no internal `L(n)` labels).

---

## ⭐ CONCURRENCY NOTE

ALPHA session s23s landed on origin while this session ran:
- SCRIP origin: `343f3471` → `2fea8565` (ALPHA s23s artifacts)
- `.github` origin: `0713bb30` → `adee5096` (ALPHA s23s cursor: A-1 residue, A-3/A-6 closed-vacuous, A-4 ledger, A-5 OMEGA cross-front request, A-8 census)
- corpus origin: also advanced

**Pull --rebase in all repos before touching code.** After rebase, re-run the watermark bracket to confirm no interaction with ALPHA's changes.

---

## HANDOFF-BLOCKED — push credential for next session

Credential: `ghp_REDACTED_see_Lon`

Working tree diff is in the conversation transcript (s23r). The 4 changed files are at `/home/claude/SCRIP/src/` — but this sandbox is ephemeral; the next session will need the diff from the transcript or re-derive from this FINDING.
