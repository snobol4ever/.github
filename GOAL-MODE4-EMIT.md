# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--compile`)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
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
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md` then `ARCH-EMITTER.md`.

**Repo:** one4all. **Done when:** `scrip --compile file.{sno,sc}` → standalone binary output identical to `--interp`. Binary links `libscrip_rt.so`. M5 extends to Icon/Raku/Prolog/Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** One shared emitter; no parallel text-emitter.

---

## Architecture

```
IR ─► sm_lower ─► SM_Program ─► sm_codegen ─► SEG_CODE
                                                  ├─ mode 3: jmp in-process
                                                  └─ mode 4: dump to .s → ld → ELF
```

SM opcodes → GNU-as macros (`sm_macros.s`), 3-col `LABEL: OPCODE args`.
BB boxes → GNU-as procs, 4-col `LABEL: ; ACTION ; jmp target`.

**Current compiled emitter units** (post RW-6 consolidation):

| File | Role |
|---|---|
| `emit_core.c` | L0–L2: buf, form, insn, label, text, mode |
| `emit_bb.c` | L3–L4: BB box templates + macro library writer |
| `emit_sm.c` | L4–L5: SM opcode templates, shape renderers, text+walk codegen |
| `sm_jit_interp.c` | **frozen** — mode-3 C interpreter; never touched |

---

## Tracked artifacts protocol

After any session touching emitter files or `rt.c`, regenerate and commit:

```bash
DEMO=/home/claude/corpus/programs/snobol4/demo; SCRIP=/home/claude/one4all/scrip
cd $DEMO
for f in roman wordcount claws5 treebank-list treebank-array; do
    $SCRIP --compile $f.sno > $f.s 2>/dev/null; done
for s in roman.s wordcount.s claws5.s treebank-list.s treebank-array.s; do
    gcc -c "$s" -o /tmp/$(basename "$s" .s).o 2>/tmp/as_err.txt \
        && echo "OK $s" || { echo "FAIL $s"; cat /tmp/as_err.txt; exit 1; }; done
cd /home/claude/corpus
git add programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array,sm_macros,bb_macros}.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen <rung>"
```

---

## Steps

## EM-STATEFUL-FLAT — Make stateful boxes flat (spec-correct, no RTCALL)

Stateful boxes require per-invocation DATA in the flat glob's DATA block — not a heap struct via RTCALL.

- [x] **SF-1** ✅ `3fcc90a7` — `emit_bb_xbal` flat BAL. `.data` slot for `int δ`; inline `'('`/`')'` byte-compare loop via RIP-relative Σ/Σlen/Δ. Binary: heap zeta (unchanged). Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-2** ✅ `c99fe633` — `emit_bb_xfarb` flat ARB. DATA: .long count; .long start. α: count=0; start=Δ; →γ. β: count++; if start+count>Σlen →ω; else Δ=start+count →γ. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-3** ✅ `4e3306d5` — `emit_bb_xstar` flat REM. Stateless. α: Δ=Σlen →γ. β: →ω. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-4** ✅ `98b2e204` — `emit_bb_xlnth/xtb/xrtb` flat LEN/TAB/RTAB. n baked as immediate; no DATA. LEN: Δ+n≤Σlen→γ. TAB: Δ≤n→γ, Δ=n. RTAB: Δ≤Σlen-n→γ. All β→ω. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-5** ✅ `55857945` — `emit_bb_xbrkx` flat inline BREAKX. DATA: .string chars; .quad chars_ptr; .long δ. α: scan fwd while Σ[Δ+δ] not in chars; δ==0||Δ+δ>=Σlen →ω; else Δ+=δ →γ. β: Δ-=δ →ω. Assembles clean. Gates: smoke 7/7, byte-id 4/4, beauty 10/17.
- [x] **SF-6** ✅ `8a63e515` — ICN_* boxes: `emit_bb_stateful` gains `nquads` param; all 45 ICN box emitters pass `ICN_NQ(state_t)` = `(sizeof(state_t)+7)/8` so TEXT path emits a correctly-sized zeroed `.data` block per box kind. Non-ICN callers (ARBNO/BREAKX/CALLCAP/CHARSET) retain `nquads=6`. Companion gate fixes (SF-6-pre `f7400d23`): JUMP/JUMP_S/JUMP_F dispatch→macro form; rt_arith case values corrected; RETURN macro→plain ret; sm_phase2_sim_test field names fixed; bb_flat_text_test intern_str callback. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13 (em7c runtime pre-existing).
- [x] **SF-7** ✅ — Delete `emit_bb_stateful_int` (zero callers). Fix `emit_bb_xbrkx` binary path: replace `emit_bb_stateful(...)` fallback with direct `emit_seq_port_call(z, "rt_bb_breakx", fn, 0/1, s, f)` + `emit_label_define(b)` between ports — matching the BAL/ARB/REM pattern. `emit_bb_stateful` and `emit_bb_stateful_text_data` stay; they are still live for ARBNO/CALLCAP/CAP_IMM/CAP_COND/CHARSET and all ICN_* emitters. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13 (em7c runtime pre-existing).
- [x] **SF-8** ✅ — Broad corpus ≥160/163 PASS. Beauty gate 17/17. Two rt.c bugs fixed: (1) `_rt_IDENT`/`_rt_DIFFER` now coerce via `VARVAL_fn` so integer args compare correctly; (2) ARBNO/CAP/CALLCAP `.data` blocks now initialized at startup via `rt_init_cap`/`rt_init_cap_call`/`rt_init_arbno` — child fn pointer wired through `cap_fixup_t` table in `emit_file_header`. `child_cache_set_lbl` + `emit_bb_register_child_label` bridge binary blob ptr → text α-label. `rt_bb_cap`/`rt_bb_arbno` detect pointer-slot layout and dereference. Commit.
- [x] **SF-9** ✅ — `emit_bb_charset` binary path: replace `else { emit_bb_stateful(...) }` with direct `emit_seq_port_call(z, rt_name, rt_fn, 0/1, s, f)` + `emit_label_define(b)`. Already has its own IS_TEXT flat path; only the binary else-branch calls `emit_bb_stateful`. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13.
- [x] **SF-10** ✅ — `emit_bb_xcallcap`, `emit_bb_xfnme`, `emit_bb_xnme` (CALLCAP/CAP_IMM/CAP_COND): add IS_TEXT flat path using `emit_bb_stateful_text_data` + `emit_seq_port_call_rip`; binary path uses direct `emit_seq_port_call`. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13.
- [x] **SF-11** ✅ — `emit_bb_xarbn` (ARBNO): add IS_TEXT flat path using `emit_bb_stateful_text_data` + `emit_seq_port_call_rip`; binary path uses direct `emit_seq_port_call`. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13.
- [x] **SF-12** ✅ — `emit_bb_rtcall_data` replaced by `emit_bb_ptr_slot` (1 quad, no nquads param). `emit_bb_rtcall_data_fn` deleted. XFNME/XNME inline cases in `emit_flat_node` now route through `emit_bb_xfnme`/`emit_bb_xnme`. Compile-clean. Gates: smoke_snobol4 7/7, jit_emit_x64 11/13, beauty 17/17.

> Closed history: `git log -p .github/GOAL-MODE4-EMIT.md`

- [~] **M5** — Raku/Prolog/Rebus SM_SUSPEND/RESUME. ⛔ Hold until GOAL-CHUNKS M4 closes. Icon cancelled (pure-BB path instead).

---

## EM-ICN-FLAT — Convert all 44 ICN_* RTCALL boxes to flat DATA-in-glob emit

**Baseline (sess 2026-05-14):** Icon --interp PASS=191 FAIL=44; honest (SCRIP_NO_AST_WALK=1 --interp) PASS=275 FAIL=2; broker 23/49. smoke_icon 5/5.

Every ICN_* emitter currently calls `emit_bb_stateful(...)` which in TEXT mode emits `N` zeroed `.quad` slots in `.data` then routes the α and β ports through `emit_seq_port_call_rip`. That is correct but routes through an abstraction that will be deleted once ARBNO/CALLCAP/CHARSET are also flat. The ICN flat work converts each `emit_bb_icon_*` from the `emit_bb_stateful` wrapper to the canonical two-path pattern: `if (IS_TEXT) { emit_bb_icn_text_data(nquads, zlbl); emit_seq_port_call_rip(...port0...); emit_label_define(b); emit_seq_port_call_rip(...port1...); return; } emit_seq_port_call(...port0...); emit_label_define(b); emit_seq_port_call(...port1...);` — identical semantics, no abstraction layer.

**Helper to add once (IF-0):** `static void emit_bb_icn_text_data(int nquads, char *zlbl_out)` — same body as `emit_bb_stateful_text_data` but renamed for ICN use; keeps the non-ICN `emit_bb_stateful_text_data` intact for ARBNO/CALLCAP/CHARSET until those are also flat.

**Grouping:** ICN boxes are grouped into batches of ~8 per step to keep each commit reviewable. All steps gate on: smoke_icon 5/5; broker ≥23/49; --interp PASS ≥ prev; honest PASS ≥ 275.

- [x] **IF-0** ✅ `3e29a9e3` — Add `emit_bb_icn_text_data(int nquads, char *zlbl_out)` static helper in `emit_bb.c` (copy of `emit_bb_rtcall_data` body, distinct name). No callers yet. Gates: smoke_snobol4 7/7, smoke_icon 5/5.
- [x] **IF-1** ✅ `bfe58803` — Convert batch A (8 boxes): `emit_bb_icon_alt`, `emit_bb_icon_bang`, `emit_bb_icon_every`, `emit_bb_icon_iterate`, `emit_bb_icon_lconcat`, `emit_bb_icon_limit`, `emit_bb_icon_seq`, `emit_bb_icon_to`. ICN_EMIT2 macro; C constructors deleted/moved to static inline. Gates: smoke_snobol4 7/7, smoke_icon 5/5.
- [x] **IF-2** ✅ `9a55b3cf` — Convert batch B (8 boxes): `emit_bb_icon_to_by`, `emit_bb_icon_not`, `emit_bb_icon_repalt`, `emit_bb_icon_while_gen`, `emit_bb_icon_until_gen`, `emit_bb_icon_repeat_gen`, `emit_bb_icon_case_gen`, `emit_bb_icon_compound_gen`. Note: batch B _new funcs live in icon_gen.c; static inline in emit_bb.c is internal-linkage (no conflict). icon_to_by_new deleted from bb_boxes.c. Gates: smoke_snobol4 7/7, smoke_icon 5/5.
- [x] **IF-3** ✅ `158e0a88` — Convert batch C (8 boxes): `emit_bb_icon_field_gen`, `emit_bb_icon_section_gen`, `emit_bb_icon_kw_gen`, `emit_bb_icon_listcon_gen`, `emit_bb_icon_proc_call`, `emit_bb_icon_scan`, `emit_bb_icon_noop`, `emit_bb_icon_intlit`. _new() constructors already extern-declared; no static inline needed. Gates: smoke_icon 5/5, jit_emit 11/13.
- [x] **IF-4** ✅ `dbde3975` — Convert batch D (8 boxes): `emit_bb_icon_reallit`, `emit_bb_icon_strlit`, `emit_bb_icon_csetlit`, `emit_bb_icon_global`, `emit_bb_icon_if`, `emit_bb_icon_initial`, `emit_bb_icon_invocable`, `emit_bb_icon_link`. Gates: smoke_icon 5/5, jit_emit 11/13.
- [x] **IF-5** ✅ `e745f93e` — Convert batch E (remaining 12 boxes): `emit_bb_icon_record`, `emit_bb_icon_return`, `emit_bb_icon_fail`, `emit_bb_icon_unop`, `emit_bb_icon_next`, `emit_bb_icon_break`, `emit_bb_icon_create`, `emit_bb_icon_coexplist`, `emit_bb_icon_arglist`, `emit_bb_icon_procdecl`, `emit_bb_icon_procbody`, `emit_bb_icon_proccode`. All 44 ICN_* boxes now ICN_EMIT2. Gates: smoke_icon 5/5, jit_emit 11/13.
- [x] **IF-6** ✅ `1cc799bc` — Dead `emit_bb_rtcall` wrapper deleted (zero external callers after IF-3..IF-5). `emit_bb_rtcall_data` confirmed live for ARBNO/CALLCAP/CAP_IMM/CAP_COND (4 callers). Compile-clean. Gates: smoke_icon 5/5, jit_emit 11/13.

---

## Watermark

**HEAD** one4all `4f0e2996` · Gates: smoke_snobol4 7/7, jit_emit_x64 11/13, beauty 17/17.

**Completed this session:** SF-8 (IDENT/DIFFER fix + ARBNO/CAP startup patching, beauty 7→17/17) + SF-12 (emit_bb_rtcall_data → emit_bb_ptr_slot, XFNME/XNME inline consolidation). **EM-STATEFUL-FLAT section complete.**

**Best next for mode-4 everywhere:** EM-ICN-FLAT — apply the same startup-patching mechanism (rt_init_cap / rt_init_arbno pattern from SF-8) to ICN_* boxes. All 44 ICN boxes use ICN_EMIT2 (IF-1..IF-5 done) which emits `emit_bb_icn_text_data` + `emit_seq_port_call_rip`. In TEXT mode, the `.Licn{id}_z` `.data` blocks are all zeros — ICN state structs need initialization via a new `rt_init_icn_box(slot_ptr, child_fn, state_t_size)` pattern before rt_init. Baseline: smoke_icon 5/5, broker 23/49, --interp 191/235.

**Next session must:** Read RULES.md, ARCH-x86.md, ARCH-SCRIP.md, GOAL-MODE4-EMIT.md, ARCH-EMITTER.md. Confirm one4all HEAD `4f0e2996`.
