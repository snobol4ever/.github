# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

> **🔄 RESET 2026-06-02 (Lon) — THIS GOAL'S LIVE PURPOSE IS BUILDING SNOBOL4 BYRD BOXES FROM GROUND ZERO (the third time).**
> Two cross-cutting rungs were SPLIT OUT into their own goal files (they touch ALL languages' runtime, not just SNOBOL4):
> - **Runtime DE-NAME (rename by CS concept, the LI ladder) → `GOAL-RUNTIME-RENAME.md`.**
> - **Runtime SUBSYSTEM REORG (organize files by capability, dissolve language silos) → `GOAL-RUNTIME-REORG.md`.**
>
> **The LIVE SNOBOL4-BB work is the BB / pattern / template ladders:** the **x86() TEMPLATE-REVAMP** sub-track, the
> **PB-RB pattern ladder** (SUBJECT→PATTERN→MATCH→REPLACE as emitted byrd-box graphs), the **REG ladder** (pattern
> family → ratified Σ=R13/δ=R14/Δ=R15/ζ=R12; the SNOBOL mode-4 unblocker), and **BROKERED-MODE-ERADICATION** — all
> below, governed by the five byte-identical FACT RULES (NO VALUE STACK · NO C BYRD-BOX · PER-BOX LOCAL STORAGE ·
> SHARED-LOWERER · X86-64 REGISTER). The FACT RULES STAY here (they are shared, byte-identical across the *-BB goals).
>
> **The DE-NAME / LI / REORG rung text retained below is PROVENANCE ONLY — it is NOT this goal's live work; follow the
> two split-out files for those.** (Physical removal of that dead rung text from this file is a future cleanup pass.)


## 🟢 CURRENT FRONTIER — **CAPTURE BOXES ✅ + m4 SCAN-NATIVE ROUTING ✅ — rung M4 1→15** (SCRIP `db23155`+`b96972b`, pat-bb probes **8/8**; M2 18 HELD). Captures: `flat_drive_capture` de-brokers ASSIGN_COND/IMM (SAVE δ→ζ-slot → child INLINE, construct-β≡child-β → CAP `rt_cap_assign_cursor`, one `bb_pat_capture.cpp`, 3 sub-kinds on `op_ival`, SPITBOL ch.13/18). Routing: `flat_drive_scan_native` (TEXT∧compound∧var-subject∧no-repl) synthesizes SUBJECT(var)+MATCH on the PATTERN sub-graph with `g_emit_cfg=pg` (wire_alt aux + capture children resolve); `bb_subject` VAR arm via new `rt_subject_load_nv` (ζ-slot **and** runtime Σ/Σlen — the capture/defer base); gather broadened to the full chain-elem set (+ASSIGN/ALT/FAIL/SUCCEED) with a **stop-node** (capture fences its own back-edge) + a LOUD sentinel-aware truncation guard in `flat_drive_match` (no silent sibling drop, the 057 class); capture child = gather-first then the **wire_alt α-hop** (capture's `->α` is ARM0; the aux ALT sits at `ch->γ`); the latent `??`-label class swept family-wide (lit/any/notany/span/break/defer strtab fallback). **Remaining rungs, honestly:** 052/054 = ARBNO brokered-TEXT child (**BROK-2** lane); 055 = the documented **gvar-concat TEXT gap** (bomb also drags its goto-label registration — success mis-lands on the fail stmt while the bomb body sits at n7; fix rides the concat arm); 053 M2-fails pre-existing. — next: **(1) gvar-concat TEXT arm** (non-constant `A ' ' B` assigns; unblocks 055 + the label-drift), **(2) BROK-2 ARBNO jump-wired** (052/054), **(3) REG-RO + REG-FENCE TIER2** (r10=22).

> **🔄 SR-1b WALKED BACK (Lon 2026-06-03; reconciled into this file 2026-06-03 OPUS48).** The "SAVE/RESTORE as
> boxes bracketing the body" plan (`bb_proc_save` + RESTORE-succ@`lbl_γ` + RESTORE-fail@`lbl_ω`, result via a
> `g_proc_result` global) was explored and **rejected**; the partial implementation was fully reverted (SCRIP
> clean at `3610475`). **The call-frame save/restore STAYS FUSED in the runtime** `rt_call_named_proc` (→ the
> SR-1a helpers `rt_name_save_push` / `rt_name_restore`) — it is correct and green there. Why box-ification was
> wrong: a SNOBOL4 call is **single-shot** (enters once, exits `:(RETURN)`/`:(FRETURN)`), NOT a backtrackable
> generator, so the FENCE/ALT "save-on-α / restore-on-β" model has **no resume edge** to hang a restore on (the
> call box's β is already degenerate `jmp ω`); box-ifying fixes no bug and (SNOBOL being by-name) each box would
> be a thin wrapper around an NV helper; its only payoff is mode-4 relocatability, which is structural debt with
> **no test delta** and premature while m4 is blocked for an UNRELATED reason (below). The caller-side
> `BB_SAVE_RESTORE`+`BB_CALL` pairing was incoherent (caller graph vs. callee body, no port edge) and abandoned.
> See `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-SR-1B-BOX-APPROACH-REJECTED.md`. The SR-1b bullet below is kept,
> struck through, for the record; **SR-2** ("the save-area IS the frame") remains the right *future* shape if
> this is ever revisited — ONE callee-side bracket whose saved-name records live in the ζ-frame, killing the
> global `g_name_save[]` stack, NOT a 3-box / caller-pair spelling.

> **🔭 REG-LADDER + m4 RECONCILIATION (audited 2026-06-03 OPUS48, grep-proven against SCRIP `8970924`).** The
> REG-ladder checkboxes below understate reality: **(1)** the `TEMPLATE_ADDR_SIGMA`/`TEMPLATE_ADDR_SIGLEN`
> process-local-address bake — the thing the ladder calls "the m4 blocker" — is **already GONE family-wide**
> (`grep -lE 'TEMPLATE_ADDR_SIG(MA|LEN)' bb_pat_*.cpp bb_lit.cpp` == empty). **(2) REG-1 (`bb_lit`) is DONE but
> was left unchecked** — `bb_lit.cpp` carries the literal comment `[REG-1 Σ=r13 δ=r14 Δ=r15]`, reads cursor=r14d
> / base=r13 / length=r15d, zero `TEMPLATE_ADDR_SIG*` (checkbox flipped below). **(3)** REG-3/4/5 boxes are
> register-migrated already (cursor on r14, no SIG): of the whole family the boxes that still name `r10` are
> **7 files / 20 refs** — `bb_lit`(4), `bb_pat_atp`(4), `bb_pat_break`(4), `bb_pat_any`(2), `bb_pat_notany`(2),
> `bb_pat_span`(2), `bb_pat_defer`(2) (the `push r10`/`pop r10` guards around `memcmp`/`strchr` + `bb_lit`'s
> `[r10]` cursor-mirror writes); the other leaves/combinators (`len`/`pos`/`tab`/`alt`/`cat`/`fence`/`arb`/`rem`/
> `abort`) are r10-free. `bb_capture.cpp` no longer exists. **(4) m4 is STILL 0/6 and the ladder's premise is now
> STALE: SIG-removal did NOT lift m4.** `--compile` aborts BEFORE any relocation, with: *"sno_ring_to_tree
> REMOVED (VIOLATION, Lon 2026-05-31) … SNOBOL4 mode-4 emission must come from LOWER producing the four-port
> statement-BB graph directly … this is a wiring gap, not a design limit."* So **the real m4 unblocker is the
> LOWER→four-port-graph wiring** (the `## ⭐ MODES 3 & 4` note), NOT the register bake. **(5)** the genuine
> remaining REG work is **REG-RO + REG-FENCE**, and REG-RO is NOT a trivial "delete the dead r10": the `[r10]`
> cursor field is still **live-coupled** to `xa_flat.cpp:140` (`movsxd rcx, dword ptr [r10]`) — the cursor lives
> in BOTH r14 (boxes) and `[r10]` (flat driver), so REG-RO must migrate `xa_flat`'s read to r14 (or keep the
> SUBJECT box syncing it) BEFORE `bb_lit`'s `mov [r10], r14d` mirror writes + the `push/pop r10` guards can be
> removed. **(6)** the **BB-HYGIENE #0 ladder line counts are stale** and largely **subsumed by the x86()
> revamp** (e.g. `bb_pat_cat`/`bb_pat_alt` cited 194/185 are now **14** lines; `bb_capture` cited 226 is gone;
> `bb_pat_break` cited 349 is 200) — same verdict as the Prolog hygiene audit (`4063911c`). **Net NEXT (ordering
> revised after the audit):** **(0) REG-FENCE — ✅ AUTHORED this session** (`scripts/test_gate_sno_pat_reg.sh`,
> TIER 1 = `TEMPLATE_ADDR_SIG*` HARD/0 locked, TIER 2 = r10 residue informational until REG-RO; add to Session
> Setup — see gate list below). **(1) The real m4 unblocker: LOWER four-port wiring** — the abort is at
> `src/driver/scrip.c:801`, which ALREADY has `sbbg` (the four-port `IR_graph_t` for `main` from `sm_preamble`)
> in hand and just `(void)sbbg`-aborts; wire it to the flat **TEXT** emitter (the mode-4 twin of mode-3's
> `bb_build_flat`/`codegen_flat_*`, SAME boxes, TEXT vs BINARY medium). This has a real test delta (m4 0/6 →
> >0/6) and is the genuine #1. **(2) REG-RO — DEFERRED behind (1)** — it is broader than first stated (7 files /
> 20 r10 refs PLUS the SHARED `xa_flat` non-frame epilogue's BINARY+TEXT `[r10]` cursor read + `ADDR_SIGMA`
> base), touches an Icon-shared return contract, and the flat pattern path it polishes is NOT the load-bearing
> m3 pattern driver (that is `rt_scan`/`IR_SCAN`) and is gated by NOTHING standing (only the un-wired
> `test_sno_pat_bb_probe.sh`). So REG-RO is zero-test-delta debt on an ungated shared path — do it only AFTER the
> flat chain is the real m3 pattern driver (PB-RB-CONV) AND under a gate. m2 **7/7 HARD** must hold every step.



**`DOUBLE(21)` → `42` LANDS. SNOBOL4 m3 is 6/6.** The with-arg param-binding blocker was a **one-bit x86
encoding bug**, not the suspected wrong-path. Root cause + fix below; the prior handoff's "proc-call doesn't
route through `rt_call_named_proc`" diagnosis was WRONG (the probes DO fire — see this session's handoff).

**ROOT CAUSE (fixed, SCRIP this commit): `x86_frame_lea` emitted REX `0x48` (W only), missing REX.B.**
`x86_frame_lea(reg, off)` addresses the **r12** frame base via SIB byte `0x24`; r12's low-3-bits (`100`)
alias `rsp` unless **REX.B (0x01)** is set. So `lea rsi,[r12+16]` silently assembled as `lea rsi,[rsp+16]` —
`rsi` pointed into the C stack, not the ζ-frame. The marshalled arg DESCR was written correctly to `[r12+16]`
(stores use `0x49`=REX.W+B), but `rt_call_named_proc` read `args` from `[rsp+16]` (garbage) → `NV_SET_fn("X",
garbage)` → `X+X` = 0. Every sibling frame helper (`x86_frame_store64`/`load64`/`mov_imm`) correctly sets
REX.B; `x86_frame_lea` was the lone outlier. FIX (1 line, `x86_asm.h:269`): `rex = 0x48` → `0x49`, still
OR-ing `0x04` (REX.R) for an extended dest reg. **Only one caller** (`bb_call.cpp:189`), so zero regression
surface. Found by probing `bb_call_str`/`marshal_call_arg`/`rt_call_named_proc` + a blob hexdump, hand-
disassembled to spot `48 8d 74 24 10` vs the correct `49 …`. ALL PROBES REMOVED — only the 1-line fix remains.

**HOW `define` works now (m3, oracle-matched, SPITBOL manual ch.8):** DEFINE registration in the `scrip.c`
SNOBOL `--run` block (`rt_proc_register` + `gvar_flat_chain_build` per non-main proc + `rt_proc_set_fn`);
DEFINE arm `bb_call_gvar_define_str`; user-proc arm `bb_call_gvar_userproc_str` (marshal args → ζ-frame DESCR
array → `call rt_call_named_proc` → store result DESCR → `cmp eax,99/je ω` so FRETURN fails the call);
IR_ASSIGN(call-result) arm in `bb_gvar_assign` + `rt_gvar_assign_descr`; VAR+VAR param arith via
`bb_binop_gvar_arith` → `rt_gvar_arith` (`NV_GET_fn`×2 + `binop_apply`); `flat_drive_return` jumps direct to
slab succ/fail. **Save/restore is FUSED in the runtime** (`rt_call_named_proc`, rt.c:481): save old
param+fn-name DESCRs onto the global `g_name_save[]` stack → install actuals via `NV_SET_fn` → run body on
`g_proc_frame_nest_arena` → capture result → restore LIFO. There is NO dedicated SAVE/RESTORE box.

**✅ RESOLVED-STALE — string-arg `slen` (audited 2026-06-03 session 2; no fix needed).** The note below mis-read
the DESCR convention: `DT_S` with `slen=0` is the CANONICAL `STRVAL()` form (`descr.h:20`; `descr_slen` falls back
to `strlen`), and `VARVAL_d_fn` treats only `DT_N` (tag 9) as a variable name — never `DT_S`+slen=0. Oracle-matched
probes: `G('AB')`→`ABAB` and `SIZE(X)`→`2` pass m2+m3 with the marshal writing plain tag `1`. Retained for record:
`marshal_call_arg` IR_LIT_S (BINARY `bb_call.cpp:96-107`, TEXT `:84`) writes the DT_S tag but leaves `slen`=0;
a string param then reads zero-length (low qword packs `v | (slen<<32)`; `slen==0 && DT_S` is mis-read as a
VARIABLE NAME by `VARVAL_d_fn`). FIX both arms: pack `tag | ((uint64_t)strlen(sval) << 32)`. ⚠ `marshal_call_arg`
is SHARED with the Raku `rt_call_arr` path — make it byte-neutral to Raku (or normalize `slen` inside
`rt_call_named_proc`; prefer the emitter fix if lane-safe).

### NEXT LADDER — DE-FUSE the call-frame save/restore (Lon 2026-06-03, two ideas)

Lon: *"Do we have a BB dedicated to save/restore params, or is it FUSED with the FNC-CALL box? If fused, break
it out — unless that's a bad idea. And: what if the BB-SAVE-RESTORE local storage becomes the effective FRAME
for SNOBOL4/Snocone/Rebus, built into the BB local storage?"* Answer: it is FUSED into the runtime helper
`rt_call_named_proc` (not a box). Verdict: **GOOD to de-fuse, in two rungs.**

- [x] **SR-1a — extract the thin name-save helpers (DONE, gated 2026-06-03).** `rt_call_named_proc` (`rt.c`)
  no longer inlines the save/install/restore loops; it routes through two new extern helpers:
  `int rt_name_save_push(const char **names, DESCR_t *args, int nargs, int n)` (save old DESCRs + install
  actuals, NUL-filling for `k>=nargs`; returns the LIFO base) and `void rt_name_restore(int base)` (restore LIFO
  down to base). BYTE-FAITHFUL — the loop bodies are verbatim, same NV ops in the same order; the fn-name
  save+null is `rt_name_save_push(&name,0,0,1)`. Gate held: SNOBOL m2 7/7 HARD / m3 6/6 (`DOUBLE(21)`→`42`),
  Icon m2 12/12 HARD, `prove_lower2`/`no_bb_bin_t`/LI-FENCE/concurrency all green; diff = `rt.c` only (+23/-15).
  NOTE: `src/runtime/core/name_save.c` is a SEPARATE mechanism — the mode-3 userproc path is rt.c's
  `rt_call_named_proc` (confirmed by the prior handoff's probe trace).
- [~] **SR-1b — ❌ REJECTED / WALKED BACK (Lon 2026-06-03). Save/restore STAYS FUSED in `rt_call_named_proc`; no `bb_proc_save`/`bb_proc_restore_*`/`g_proc_result`. See the SR-1b WALK-BACK note at the top of this file + `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-SR-1B-BOX-APPROACH-REJECTED.md`. The text below is retained for the record only — do NOT implement it.** ~~SAVE/RESTORE as boxes bracketing the body (the remainder of SR-1).~~ Now that the helpers exist,
  make the four-port `SAVE → body → RESTORE` topology explicit WITHOUT touching the shared `XA_FLAT_EPILOGUE`
  (Icon shares it — changing the return contract there risks the Icon HARD gate). **KEY CONSTRAINT (verified this
  session):** the function result is read via `NV_GET(name)` and must be captured BEFORE restore, and restore must
  run on BOTH the RETURN (`lbl_γ`) and FRETURN (`lbl_ω`) paths. **FACTS:** inside the body `r12 = fb`
  (`XA_FLAT_PROLOGUE` = `push r12; mov r12, rdi`); the success epilogue returns `eax=1`, the fail epilogue returns
  `eax=99` and writes `[r12+0]=99` — the result is NOT in the return regs (rt_call_named_proc reads it from the
  NV store after the body returns). **EPILOGUE-NEUTRAL DESIGN:** (1) `bb_proc_save` box at the body head (after
  the prologue, before the first chain node) reads actuals from `[r12+16…]` + baked RO param names, calls
  `rt_name_save_push`, stores the returned base into a STABLE frame slot `[r12+off_base]` (reserve it; must not be
  reused by transient temps); (2) RESTORE-success box inserted at `lbl_γ` BEFORE `XA_FLAT_EPILOGUE`:
  `g_proc_result = NV_GET(name); rt_name_restore([r12+off_base])`; (3) RESTORE-fail box at `lbl_ω`:
  `rt_name_restore([r12+off_base])` only. `rt_call_named_proc` then stages actuals into `fb+16…` (normalize
  nargs→np with NUL fill, like the `g_call_args` path at `rt.c:466`), invokes the body, reads the result from the
  new `g_proc_result` global (no more C-side capture/restore), checks `fret` tag for fail. Recursion-safe:
  rt_call_named_proc reads `g_proc_result` immediately after its body returns and RESTORE-success is the last box
  before `ret`, so there is no clobber window. New box templates wired via `emit_core.c` dispatch. ⚠ HONEST
  CAVEAT (from SR-1): SNOBOL is by-name (`bb_var` = `jmp γ`; values live in the global NV store), so each box is a
  thin wrapper around an NV helper — the win is topology + mode-4 relocatability, not avoiding the runtime. Gate:
  define m3 6/6 + oracle byte-match; m2 7/7 HARD; Icon m2 12/12; `XA_FLAT_EPILOGUE` bytes unchanged (Icon m3/m4
  not regressed). **ALLOCATOR/LAYOUT (resolved 2026-06-03):** the frame allocator is a trivial bump —
  `g_flat_slot_count` (`emit_bb.c:61`), `bb_slot_alloc16` bumps +16. The gvar body path (`emit_bb.c:2096`) starts
  it at 0; offset 0 already doubles as the result slot (the fail epilogue writes `[r12+0]=99`). SR-1b does NOT need
  the body's emitted bytes byte-identical to baseline (boxes are being ADDED) — only OUTPUT-correct (m3 6/6) +
  Icon byte-unchanged. So reserve at body-head BEFORE the node walk by pre-bumping `g_flat_slot_count`: result
  `[0]`, actuals `[16 .. 16+16*np)` (matches the existing staging convention at `rt.c:466`, `fb+16*(k+1)`), base
  `[16+16*np]`, body temps from `16+16*np+8` up. `rt_call_named_proc` stages actuals at `fb+16*(k+1)`
  (np-normalized, NUL-fill); `bb_proc_save` reads `[r12+16*(k+1)]`; the RESTORE boxes read base at
  `[r12+16+16*np]`. Remaining work is purely mechanical (2-3 box templates with TEXT+BINARY arms calling
  `rt_name_save_push` / `rt_name_restore` / a new `g_proc_result` setter via @PLT, `emit_core.c` dispatch, the
  codegen insertion in `codegen_gvar_flat_chain_body`, the `rt_call_named_proc` rewrite) + gating.
- [ ] **SR-2 — the save-area IS the frame (Lon's cooler idea).** Migrate the save-records OUT of the global
  `g_name_save[]` stack INTO `bb_proc_save`/`restore`'s **per-activation ζ-frame local storage** (`[r12+off]`),
  laid out at emit time as N records `{name_ptr (8B), saved_DESCR (16B)}`. Kills the global fixed-max name-save
  stack (cleaner recursion/reentrancy), and **unifies the frame concept** across languages: Icon's ζ-frame
  holds *live* values, the SNOBOL/Snocone/Rebus ζ-frame holds the *saved* values for the activation's lifetime
  — same one-register `[r12+off]` FACT-RULE discipline, different payload. Mode-4-relocatable by construction.
  Do AFTER SR-1. Gate: same as SR-1 + no-stack/one-register-frame gates hold for the new boxes.

**Gate state (GREEN, verified 2026-06-03):** SNOBOL4 m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (output/concat/arith/define/pattern/goto_s
emit→as→gcc→run; was 0/6) · Icon m2 **12/12 HARD** · `prove_lower2` PASS · `no_bb_bin_t` 0 · LI-FENCE 13 (this work's delta 0; 7 prior + 6 from rebased-in Icon GN `c66723e`) ·
concurrency invariants OK · REG-FENCE TIER1=0 · broad interp 105/280 + unified-broker 32 match clean baseline. ENV:
`apt-get install -y libgc-dev`.

## ✅ DONE (mode-3, byte-matched to the SPITBOL oracle)

- **IR_SEQ value-concat** (`OUTPUT='ab' 'cd'`→`abcd`) — reuses `rt_gvar_assign_concat` (`IR_interp.c`),
  which runs the two operand sub-graphs via `IR_interp_once` + `binop_apply(BINOP_CONCAT)` (manual ch.3); m3 →3/6.
- **IR_SCAN** `pattern` (`S 'b'='X'`→`aXc`) + `goto_s` (`'x' 'x' :S()`→`hit`) — `rt_scan` in `IR_interp.c`
  mirrors the mode-2 IR_SCAN handler (manual ch.18 unanchored OUTER loop); `bb_scan_stmt.cpp` box; m3 →5/6.
  NOT the native PB-RB `bb_match` ladder — reuses `IR_interp_once` as the sanctioned mode-3 helper (distinct
  from the FORBIDDEN `bb_exec_*` walker). `lower.c v_scan` populates `operand_aux` with the subject/replacement
  VALUE sub-graphs; `emit_bb.c flat_drive_scan_stmt` promotes them onto `_`; `emit_core.c` adds `case IR_SCAN`.
- **arith** `OUTPUT = 2 + 3`→`5` (`IR_BINOP_GVAR_ARITH`, LIT+LIT, `op_a_slot`) + **`OUTPUT = "hello"`** (`bb_gvar_assign`).
- **`bb_binop` ROUTER DELETED** — four IR kinds (`IR_BINOP_{RELOP,ARITH,GVAR_ARITH,CONCAT}`) dispatch 1:1 in
  `emit_core.c`; no template probes a sibling. (OPEN: `IR_BINOP_GVAR_ARITH` still bakes operands as immediates
  — a de-fuse would make them ζ-slot producer boxes like Icon's `bb_binop_arith`.)

## RUNTIME DE-NAME + SUBSYSTEM REORG — split into their own goal files

The runtime DE-NAME (rename every `src/runtime/**`-DEFINED symbol by its CS concept) and the runtime
SUBSYSTEM REORG (dissolve the language silos so each FILE is a capability, not a language) were SPLIT OUT
(they touch ALL languages' runtime, not just SNOBOL4):
- **DE-NAME → `GOAL-RUNTIME-RENAME.md`.** ✅ Emitter+runtime de-name COMPLETE (gated byte-identical slices +
  LI-FENCE). Only **LI-CORE** (`src/runtime/core/` SNOBOL-lib naming) remains — a runtime-unification decision
  for Lon. **Definition-location is authoritative** — a token's *use* in runtime does NOT make it runtime-owned.
- **REORG → `GOAL-RUNTIME-REORG.md`.** RS-1 CLUSTER done (562-fn inventory + 17-subsystem partition map);
  RS-2 PARTITION in progress (`runtime_eval`, `unification`, `runtime_init`, `io_format`, `arithmetic`,
  `pattern_match` landed). Move/rename-only, byte-identical, build-system in lockstep.

Follow those two files for that work — it is NOT this goal's live frontier (the BB/pattern/template ladders are).

## ✅ RUNG COMPLETE — LANGUAGE-INDEPENDENT EMITTER + RUNTIME (de-name) + COMMENT PURGE

The EMITTER and RUNTIME are language-independent: every box / runtime helper / IR-facing name is its
computer-science concept, NOT the source language that exercises it (so a session never sees `sno_*` while
working Icon and writes a duplicate). Six gated byte-identical slices cleared the whole in-scope surface
(`src/emitter/**` + `src/runtime/**`); **LI-FENCE** (`scripts/test_gate_no_lang_names.sh`, wired into the
Session-Setup gate list) locks it. COMMENT POLICY (RULES.md, Lon 2026-06-02): the ONLY comment permitted in
any source is the 120-char `/*---*/` line-break separator (`/*===*/` for larger sections) between every
function/major block — nothing else (no block comment, no inline, no `//`).
**REMAINING on this rung: only LI-CORE** (`src/runtime/core/` SNOBOL runtime library — a generic CS name
would be vague per the `SNO_INIT_fn` precedent; separate Lon decision).
**HELD (out of emitter/runtime DEFINITION scope):** driver-defined symbols (`icn_ring_to_tree`, `g_raku_*`,
`has_non_sno`); contracts `STAGE2_PL_PRED_TABLE_SIZE`; frontend-contract dispatch-name strings
(`ICN_NULL`/`ICN_CASE_EQ`/`ICN_SCAN_*`/`__rk_jct_*`/`__rk_arr`/`set_prolog_flag`/`current_prolog_flag`);
emitted asm label/comment strings; parser API (`prolog_atom_*`, `pl_write*`, `raku_nfa_*`). EXCLUSIONS kept:
`IR_LANG_*`/`LANG_*` (shared-lowerer dispatch), snocone (different language), `prologue`/`epilogue` (assembly).
The x86() TEMPLATE-REVAMP + PB-RB + REG ladders below remain valid (de-naming changes names, not the ladder).

## ▶ x86() TEMPLATE-REVAMP — sub-track (continues after the cleanup rung above; 2026-06-02)

Convert this language's BB templates to the **`x86()` self-encoding API** (one return per `PLATFORM_*`, pure
`x86(mnem,…)` concat, no `bb_bin_t`, pBB-free). The shared looping-box **keystone is LANDED at SCRIP
`origin/main`=`30e8422` — REBASE ONTO IT BEFORE CONVERTING ANY BOX** (internal-label + ζ-frame support lives in
the SHARED `x86_asm.h`; do not rebuild it or you collide).
- **START HERE:** `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (rules R1–R13, divvy-up table, landed API `x86_begin()`/
  `L(n)`/`FR(off)`/`bb_slot_claim`, `x86_asm.h` vocabulary). **Reference:** `bb_pat_pos.cpp` (loop-free) +
  `bb_pat_span.cpp` (looping). **Recipe:** `HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V3-KEYSTONE-POS-SPAN.md`.
- **STILL OPEN (shared):** the VARIABLE-LENGTH define/jmp-pair loop (combinators + FENCE pair path + Raku `bb_nfa`)
  — first to reach a combinator designs it once in the RULES-DRAFT.
- **YOUR BOXES:** `bb_pat_pos`✅ + `bb_pat_span`✅ + `bb_pat_abort`✅ + `bb_pat_tab`✅ + `bb_pat_atp`✅ +
  `bb_pat_arb`✅ + `bb_pat_defer`✅ + `bb_pat_fence`✅ + `bb_pat_break`✅ DONE (`x86_movimm32` / `mov32` encoder
  landed for TAB δ=r14d set; ARB uses `bb_slot_claim(8)` for its z/zo ζ-frame generator state; DEFER off
  `[r10]`→δ=r14d with the 16-byte-aligned `rt_defer_match` call preserved; FENCE single-shot save-δ-on-α/
  restore-on-β via `bb_slot_claim(4)`; BREAK+BREAKX looping, z/z_orig in `bb_slot_claim(8)` ζ-frame, internal
  labels plain L(0)/L(1) + BREAKX rescan L(2)/L(3), strchr with push/pop r10). Next loop-free leaf: NONE LEFT.
  Also DONE (statement-level, shared lane): `bb_lit_scalar`✅ (pass-through arms) + `bb_nv_assign`✅ (lit_s+var
  arms; **renamed from `bb_sno_assign` 2026-06-02 — see SNO-STRIP below**) + `bb_var`✅ (name-value flat-chain
  pass-through `jmp γ;def β;jmp ω` + ICN flat-chain 16-byte DESCR slot-copy via `x86_frame_load64`/`store64`;
  op_sa/op_off promoted at dispatch in walk_bb_flat IR_VAR — no neighbor read).
  Variable-length combinators (the STILL-OPEN define/jmp-pair design): `bb_pat_cat`, `bb_pat_alt`, `bb_match`,
  `bb_pat_fence` PAIR path (the with-children `FENCE(P)` form — the bare-FENCE primitive above is done).
- Edit only your boxes + their dispatch/decl lines; `x86_asm.h` edits are additive; `git pull --rebase` before push.
- (Full live status is in the **Watermark** near the end of this file.)

### ✅ x86() conversions DONE (loop-free + single-loop SNOBOL4 pattern leaves + statement boxes)

All loop-free + single-loop SNOBOL4 boxes are x86()-self-encoding (pBB-free, read only `_`) on the ratified
regs (Σ=r13/δ=r14/Δ=r15/ζ=r12): `bb_pat_{abort,tab,atp,pos,span,len,rem,any,notany,arb,defer,break,fence}` ·
`bb_lit` · `bb_lit_scalar` · `bb_var`(SNO+ICN) · `bb_gvar_assign`. The variable-length define/jmp-pair loop is
SOLVED: `x86_pair_loop()` in `x86_asm.h` (in-band `E`=define-pair-label / `F`=rel32-patch records walked by
`bb_emit_x86`), consumed by `bb_pat_cat` + `bb_pat_alt`. OP-A-PROMOTE landed (`OUTPUT = 2 + 3` passes m3).
STUB CLEANUP deleted 54 do-nothing `bb_*.cpp` so a `bb_*.cpp` existing ⇔ that box is real. Boxes recreated
later come back as genuine `x86()` (not bombs). Detail: the `HANDOFF-*.md` files + git history.

NAMING NOTE: the assignment box was renamed `bb_sno_assign`→`bb_nv_assign`→`bb_gvar_assign` (concept = global
variables, the user-manual term; runtime is language-independent); `rt_*` helpers track it. The scan box is
`bb_scan_stmt` (not `bb_scan` — a live `BrokerMode` enum value).

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

## ⛔ TWO LITERAL FORMS ONLY — MEDIUM_BINARY IS A HAND-CODED LITERAL BYTE MAP; NO FUNCTION MAY COUNT BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**Every BB template emits its x86 in exactly TWO LITERAL forms, both counted BY HAND.** (1) `MEDIUM_BINARY`
is a hand-coded LITERAL byte map — `bytes("\x..")` opcode literals plus a LITERAL patch-offset map
(`bin = {{13,65,80,84,95}, {…}, {…}}` with HARDCODED constant offsets). (2) `MEDIUM_TEXT` is literal GAS asm.
Both forms are LITERALS. This is DELIBERATE, not a stopgap: a single shared/computed template proved
unmaintainable — it kept getting split apart — so each box is its own small template carrying its own
hand-coded byte map, and that literal form is the one that stays correct. (Lon directive, 2026-06-01 —
re-issued after a session INVERTED it: literal bytes + literal asm are RIGHT; the function-counter is WRONG.)

**FORBIDDEN — the ONLY thing that makes a site BAD: using a FUNCTION to count or compute the bytes.**
Specifically `b.size()` in any form (`bin.sites.push_back((int)b.size())`, `int off = (int)b.size()`,
`int mr_off = (int)b.size()`), or any helper that DERIVES a patch offset from the running buffer length
instead of a hardcoded literal constant. Every offset in `bin` must be a LITERAL integer, never a function
of the buffer. (CARVE-OUT: `bb_emit_asm_result` in `emit_str.cpp` may walk the FINISHED byte string with
`.size()` when it emits/patches — that is the consumer reading a complete literal, NOT a template counting
its own bytes; the prohibition is on a TEMPLATE deriving its patch offsets from a function.)

**NOT bad — explicitly allowed, do NOT flag or "fix" these:** hand-written `bytes("\x..")` opcode literals;
hardcoded `bin = {{…},{…},{…}}` literal offset tuples; literal internal rel32 deltas (`+65`, `-98`) written
as constants; `u8()/u32le()/u64le()` building literal immediates; `TEMPLATE_ADDR_*` address bakes. These ARE
the hand-coded byte map — the CORRECT, supported form. A box that hand-encodes bytes with literal offsets is GREEN.

**GUARD:** `scripts/test_gate_no_handencoded_bytes.sh` (informational baseline now; flips to a HARD `--strict`
zero-check). It counts, per `BB_templates/*.cpp` (comments stripped), every `b.size()` — the function
byte-counter — which is the ONLY bad pattern. The count only ever decreases as `b.size()` sites are rewritten
to literal offset maps; any session that raises it has violated this rule. **COMPLETION TEST:** (a)
`scripts/test_gate_no_handencoded_bytes.sh --strict` green — zero `b.size()` in any `BB_templates/*.cpp`;
(b) every `MEDIUM_BINARY` arm uses a hand-coded LITERAL byte map with hardcoded offsets, never a function to
count bytes; (c) the FACT RULE body is byte-identical across all five GOAL-*-BB files.

> **⛔ SNO/sno DE-NAME — ✅ SUPERSEDED + DONE.** This directive (strip `SNO`/`sno` from emitter/runtime,
> naming by CS concept) is COMPLETE and subsumed by the LANGUAGE-INDEPENDENT cleanup rung above +
> `GOAL-RUNTIME-RENAME.md`; LI-FENCE enforces it. Carve-outs preserved: `IR_LANG_SNO`/`LANG_SNO` (the shared
> lowerer's `switch(cx.lang)`); snocone (a DIFFERENT language — `sno` ⊂ `snocone`, never blanket-sed);
> `src/runtime/core/` SNOBOL runtime LIBRARY (LI-CORE, pending Lon); parser/frontend bridge (`sno_parse_*`,
> `lower_sno`, `tree_to_sno`, `test_sno_*`).

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon directive, 2026-06-01, Opus 4.8). THIS SUPERSEDES the `tree_t`-bake
> "DESIGN QUESTION (DECIDED)" below AND the PATND_t-based PB-1/PB-2 as previously landed. READ THIS FIRST; the
> older blocks are kept only for history and are marked SUPERSEDED.**
>
> The trigger: PB-1 (landed `6483bb5`) built a `PATND_t` via `rt_sno_pat_build_lit`, and a draft PB-2 read a
> `PATND_t*` head. But `PATND_t` is the redundant runtime pattern-IR that is **slated for demolition** (see
> "KILL PATND_t" + PND-1 below). Wiring the new native pattern path onto the type being deleted is backwards.
> The draft PB-2 was reverted (uncommitted); PB-1 needs rework (see PB-1-REWORK below). Five corrections:
>
> **(1) A SNOBOL4 pattern is a graph of EMITTED BYRD-BOXES — `bb_box_fn` machine code in the RX pool — NOT a
> `PATND_t` data structure, NOT a `tree_t`.** The pattern ELEMENTS *are* byrd-boxes (literal-matcher,
> span-matcher, alt-combinator, …); matching is *running* that graph through the **same `bb_broker.c`** that
> drives Icon generators and Prolog goals (four-port α/β/γ/ω resume). There is NO second runtime IR and NO
> interpreted pattern tree. This is why `PATND_t` must die: it was a parallel interpreted pattern-IR beside the
> real thing. The matcher boxes ALREADY EXIST — `bb_lit.cpp`, `bb_pat_span.cpp`, `bb_pat_any.cpp`,
> `bb_pat_alt.cpp`, `bb_pat_cat.cpp`, `bb_pat_len.cpp`, … (most already carry BINARY+TEXT arms). The native
> pattern engine is not invented; it is **driving the existing `IR_PAT_*` matcher boxes as a four-port graph
> from SUBJECT**, replacing the `IR_SCAN` super-node + `PATND_t` bridge.
>
> **(2) `tree_t` (AST) is for EVAL/CODE, NOT for PATTERN.** The older bake-the-AST decision justified itself by
> analogy ("EVAL/CODE use AST in the backend, so why not PATTERN"). The analogy breaks on WHEN the structure
> exists: `EVAL(s)`/`CODE(s)` get a *source string at runtime* and MUST parse → `tree_t` → build boxes (the
> structure does not exist until runtime — the legitimate runtime-codegen path). A PATTERN's structure is
> KNOWN AT COMPILE TIME (already parsed into the statement); baking its `tree_t` just to re-walk it at runtime
> is a pointless round-trip. So: no `tree_t` in the pattern path.
>
> **(3) `DT_P` (the pattern datatype, the `descr.h` `.p` slot being demolished with `PATND_t`) BECOMES a
> `bb_box_fn` graph head** — a function pointer into SEALED EXEC space with the housekeeping (subgraph
> descriptor: entry / single exit / fail boundary) in the right places. Then `COLOR = 'GOLD' | 'BLUE'` stores a
> box-graph in COLOR; `B ? COLOR` runs it; `BOTH = COLOR CRITTER` STITCHES two box-graphs. SPITBOL's "the bead
> diagram recorded in memory" — the recording is emitted byrd-boxes.
>
> **(4) SEAL AT THE ELEMENT GRANULARITY; WIRE AT THE INSTANCE LEVEL. This is the key simplification that makes
> a GRAPH (not a tree) build cleanly.** Each pattern ELEMENT's matcher code (`bb_lit`/`bb_pat_span`/…) is
> sealed (RO). The GRAPH — the wiring of elements by their four ports — is an INSTANCE-level structure:
> `STITCH_*` boxes wire instance records whose `code` field points at the sealed element matchers. STITCH
> therefore NEVER repoints sealed interior jumps; it only wires instance boundary ports. The runtime node is a
> four-port box-instance (`{code, α, β, γ, ω, bound-operand, match-state}`) — the SAME shape `lower2` fills on
> `IR_t`, one layer down; the broker follows the port pointers exactly as for Icon/Prolog. NO tree is held: the
> parse tree survives only as the postfix EMIT ORDER, flattened away (precisely how LOWER builds its graph).
> Back-edges (ω/β) are why it MUST be a graph: "fail of element 2 resumes element 1" and "both ALT arms share
> one success continuation" are edges a tree cannot express.
>
> **(5) THE BUILD SEQUENCE = the runtime twins of LOWER's `wire_seq` / `wire_alt`.** Compile-time `wire_seq`
> (n-ary sequence-with-backtrack) and `wire_alt` (n-ary fail-chain) wire `IR_t` nodes; runtime `STITCH_SEQ` /
> `STITCH_ALT` wire box-INSTANCES with the SAME port equations. ONE construction, TWO times: all-constant
> operands → wire at EMIT time (sealed); any runtime operand → wire at MATCH-BUILD time. Postfix order
> guarantees each STITCH consumes already-finished child heads; it emits a small descriptor `{entry, exit,
> fail}` (= lower2's α_out/β_out synthesized-up, γ_in/ω_in inherited-down) for its parent to wire next.
>
> **DECIDED forks (Lon delegated judgment 2026-06-01):**
>   - **Fork A — `BB_PAT_BUILD_*` is NARROW: it exists ONLY for STRUCTURAL variance** (`*E`, `$NAME`,
>     pattern-valued variable). OPERAND variance (`LEN(N)`, `SPAN(cvar)`) is NOT a builder — the
>     compile-time-emitted element matcher reads its operand late from a `ζ`-slot at match time (operand-binding,
>     no separate box), exactly as the existing variable-arg pattern family already resolves args late.
>   - **Fork B — "build" = SPLICE (wire ports), NOT JIT-emit.** A pattern-valued variable already holds a
>     `bb_box_fn` graph (corollary of (3)), so construction wires existing/sealed graphs. Real runtime codegen
>     happens ONLY for `*E`/EVAL/CODE — the `tree_t` path of (2). Ordinary pattern construction never emits
>     fresh machine code per match.
>   - **Fork C — REUSE the existing `IR_PAT_*` matcher boxes** as the sealed/instance element matchers; do not
>     invent parallel matcher templates.
>   - **Fork D — ε-merge (Thompson/NFA) boundaries for the VARIANT (instance-wired) path** so STITCH is always
>     O(1) "redirect prev.single-exit → next.entry" (single ε-entry / single ε-exit per subgraph; reuse the
>     in-tree `bb_nfa.cpp` / RK-NFA machinery). The all-INVARIANT path seals to direct jumps with NO ε.
>   - **Fork E — sealing depth: seal at ELEMENT granularity (per (4)).** Baseline mechanism = instance-level
>     wiring for the whole pattern (invariant leaves still use their sealed element `code` as an instance's
>     `code`). The ALL-INVARIANT single-sealed-BLOB freeze is the PB-OPT OPTIMIZATION on top (correctness first,
>     bake second) — NOT a special case the base mechanism must carry. So STITCH only ever touches instance
>     records, never a sealed multi-element interior.
>
> **The two NEW boxes this introduces** (the rest of the matcher boxes already exist, Fork C):
>   - **`REF_INVARIANT`** — loads a sealed element/subgraph `bb_box_fn` head into a `ζ`-slot (RO `[rip+disp]` /
>     movabs → `[ζ+off]`). For a FULLY-invariant pattern, this one box's output IS the `DT_P` value handed to
>     MATCH; nothing else runs (the PB-OPT fast path).
>   - **`STITCH_SEQ` / `STITCH_ALT`** — read two child heads from `ζ`-slots, wire their four ports (the runtime
>     twin of `wire_seq`/`wire_alt`), leave the combined head + `{entry,exit,fail}` descriptor in a `ζ`-slot.
>   - **`BB_MATCH`** (still phase 3) — receives the `DT_P` head + Σ/δ/Δ, drives it via the broker with the
>     ch.18 unanchored OUTER start-loop (within-pattern backtracking is already the boxes' β/ω ports).

> **⭐⭐⭐ SEAL-BOUNDARY HOOKS — `BB_LINK` + the per-glob HEAD BLOCK (Lon + Opus 4.8 design session, 2026-06-01).
> This is the mechanism for the ONE thing element-granularity sealing did NOT yet answer: how a SEALED graph's
> OUTERMOST edges (the head's OUTSIDE-γ success-out and OUTSIDE-ω fail-out) reach a target that DIFFERS PER CALL
> SITE. Two coupled ideas; both keep control threading by JUMPS (never a re-dispatcher — stays on the right side
> of BROKERED-ERADICATION) and create NO concurrency hazard.**
>
> **THE PROBLEM (precisely).** Interior jumps inside a seal (element→element, element→its own ε-exit) bake fine —
> both ends live inside the seal. The trouble is the two OUTERMOST edges. When `COLOR = 'GOLD' | 'BLUE'` is a
> sealed reusable head driven from `B ? COLOR` in one statement and `C ? COLOR` in another, the bytes are
> identical but the outward targets differ per call site, so they CANNOT be `jmp rel32 <fixed>` inside the seal.
> Unseal/reseal is OUT — it serializes a shared resource (the concurrency worry), dirties I-cache on a hot path,
> and defeats sharing one sealed copy. The current PB-RB-3 inline emit dodges this (the element is emitted INLINE
> per statement via `walk_bb_flat`, so OUTSIDE-γ/ω are hardwired and there is no seal boundary to cross). **That
> dodge expires the moment `DT_P` becomes a real SHARED sealed head.** This note is the answer for that moment.
>
> **NO REGISTERS for the continuations (decided — Lon).** The obvious "dedicate r8/r9 to OUTSIDE-γ/ω, head does
> `jmp r8`" is WRONG here: those continuations must SURVIVE a `call memcmp@PLT` inside the element matchers, and
> under SysV r8–r11/rax/rcx/rdx/rsi/rdi are caller-saved (the call clobbers them — the same reason `bb_lit` does
> `push r10; call; pop r10` and `bb_match` α re-establishes r10 after `rt_sno_subject_load`). The callee-saved
> set (rbx/rbp/r12–r15) WOULD survive but is fully allocated (ζ/Σ/δ/Δ/DESCR-base/hash-base) — no free register
> to burn. Registers are the wrong home; that points straight at the ζ-frame.
>
> **IDEA 1 — `BB_LINK`: the universal seal-boundary external edge (the ζ-slot indirect jump).** A sealed graph
> reaches OUTSIDE only through a `BB_LINK` box. `BB_LINK` is a SINGLE-ENTRY PURE-TAIL box — its only emitted code
> is `jmp qword [r12 + link_off]` (an indirect jump through a `ζ`-frame slot, ~5 bytes). It has NO β (nothing to
> resume — resumption lives in the boxes UPSTREAM of it, whose β/ω still thread among themselves inside the seal),
> NO γ/ω of its own, NO state, and NEVER returns to itself. That degeneracy is deliberate: it is what stops
> `BB_LINK` from quietly growing back into the broker we deleted. The DRIVER writes the real per-call-site targets
> into the `ζ` slots BEFORE jumping into the sealed head; the sealed bytes stay immutable and re-entrant (the
> instruction is always the same fixed `jmp [r12+off]`; only the DATA in the slot is per-call-site — the dual of a
> return-address slot, one for success and one for fail). **Concurrency-free BY CONSTRUCTION:** nothing in sealed
> code is mutated; every per-activation datum, the continuations included, lives in the R12 frame, and R12
> switches per sequence (callee-saved, survives calls). Two concurrent drives of the same sealed `COLOR` write
> their own targets into their own frames and never touch each other. (The ONLY design with a concurrency problem
> was unseal/reseal; this dissolves the question.) `BB_LINK` ALLOCATES its own `ζ` slot(s) via `bb_slot_alloc`
> like every other box, and the wiring/STITCH step FILLS them — exactly parallel to how `bb_match` α allocates the
> start-cursor + subject slots today. The "two fixed slots (γ, ω)" is the DEGENERATE one-head case; the general
> form is a small VECTOR of link slots, one per `BB_LINK` instance. This IS Fork D's ε-boundary made concrete: a
> single-entry/single-exit node whose exit is `jmp [r12+slot]`; STITCH wires `BB_LINK` instances (it cannot and
> does not rewire sealed interiors), so the ε-merge role and the external-hook role were the same problem in two
> hats. Matcher templates go back to SEAL-PURE — they only ever `jmp` to direct labels; if a label turns out to be
> a `BB_LINK`, the box neither knows nor cares.
>
> **IDEA 2 — every GLOB has a HEAD BLOCK; glob→glob transition is the SAME boundary (recovered prior design).**
> When BBs are GLOBbed into a graph, every glob has a HEAD. Going BB-BLOCK-1 → BB-BLOCK-2 is the SAME external-edge
> case as head→outside: the producing glob's exit and the consuming glob's entry are wired PER-INSTANCE, not baked.
> So the HEAD BLOCK is the universal transition node between ALL globs — the place a `BB_LINK` lives. (This is the
> "HEAD BLOCK to transition between all globs" design from before the repo was re-cut; the history is gone, so this
> is the durable re-statement.) **`BB_MATCH` is *kinda* a `BB_LINK` but NOT really:** `BB_MATCH` must JUMP OFF into
> the element AND be jumped back into (the ch.18 outer-loop driver that establishes the frame + the link slots),
> whereas `BB_LINK` is the pure indirect edge that never returns to itself. The chain is **`BB_MATCH` ↔ `BB_LINK`
> ↔ dynamic land**: `BB_MATCH` drives + sets the slots; `BB_LINK` is the edge; "dynamic land" is the per-call-site
> continuation. A sealed interior therefore NEVER contains an outward `rel32` — all external links go through a
> `BB_LINK` at a HEAD BLOCK.
>
> **REFINEMENT (Lon 2026-06-01) — a HEAD BLOCK is HALF a Byrd box, and that half IS `DT_P`.** A full BB has FOUR
> ports — α/β INBOUND (entered, resumed), γ/ω OUTBOUND (success-out, fail-out). A HEAD BLOCK has ONLY the TWO
> OUTBOUND hooks: OUTSIDE-γ and OUTSIDE-ω. It has NO α/β of its own to be entered-and-resumed at, because it is
> NOT a matcher — it is what the sealed matcher graph's last box flows INTO, and from there back OUT to the
> per-call-site continuation. This is precisely what a `DT_P` value already is: a sealed-body entry plus its two
> escape edges. So the identity is **`DT_P` ≡ HEAD BLOCK ≡ { entry-into-sealed-body, OUTSIDE-γ slot, OUTSIDE-ω
> slot }** — two hooks, not four. The half-BB framing is what makes it correct: `BB_LINK` is NOT a free-floating
> edge box, it IS the OUTBOUND HALF of the head, and the head is the thing `DT_P` denotes. This also collapses an
> apparent third concept: the `{entry, exit, fail}` descriptor STITCH synthesizes (the runtime twin of lower2's
> α_out/β_out synthesized-up, γ_in/ω_in inherited-down) is the SAME object — `exit` = OUTSIDE-γ, `fail` =
> OUTSIDE-ω, `entry` = the jump-in. STITCH's build-time descriptor and the run-time HEAD BLOCK are one object seen
> at two times; there was never a separate third thing.
>
> **TWO PINS for when this lands (open items, not yet code):**
>   - **ONE FRAME PER MATCH.** The slot is `[r12+off]` and r12 switches per sequence, so `BB_LINK` must read the
>     RIGHT frame. Rule: a stitched pattern runs in ONE frame for the whole match — the element graph gets
>     per-element SLOTS in the one statement frame (what PER-BOX-LOCAL-STORAGE already implies), NOT per-element
>     frames. Then `[r12+off]` is unambiguous and no copy-down is needed. The only place a FRESH frame appears is a
>     genuine subroutine-like construct (a pattern-valued variable invoked as a callee, or `*E`/EVAL) — and THAT
>     boundary is exactly the call/return seam where an explicit continuation hand-off is wanted anyway, so it is
>     not an exception to paper over.
>   - **`BB_LINK` IS PURE TAIL, NOT A PORTED BOX.** α loads-and-jumps; no β; no γ/ω. Keep it strictly "indirect
>     jump through a frame slot, no state, no return" so it can never become a re-dispatch point. The all-invariant
>     frozen pattern (PB-OPT) keeps HARDWIRING — that case is emitted into its OWN statement (not shared), so its
>     continuations are known at emit time and pay ZERO indirection. You buy `jmp [r12+off]` ONLY when you actually
>     seal-and-share — pay for sharing only when you use it.
>
> **NEXT TOUCHPOINT (where this drops in or reveals a wrinkle):** the `g_match_*` emit-globals + `bb_slot_alloc`
> path that today passes the boundary labels (`g_match_elem_p`, `g_match_advance_p`) into `bb_match` α — that is the
> concrete spot a `BB_LINK` instance would allocate its slot and the driver would fill it. It sits right next to the
> REG-1 work (both are about what lives in the frame vs. what is baked), but `BB_LINK` is a PB-RB-4+/PB-OPT-era
> concern (shared sealed heads), NOT a REG-ladder blocker — the REG ladder ships first.

> **⭐ MODES 3 & 4 = TWO ARMS OF ONE TEMPLATE PER BOX (Lon, 2026-05-31).** The whole job is LOWER + EMITTER;
> get those right and modes 3/4 run from the SAME IR graph + the SAME per-box template — **BINARY arm = mode 3**
> (raw x86 into the mmap'd RX pool, `bb_build_flat`) / **TEXT arm = mode 4** (GAS → `as`/`gcc`,
> `codegen_flat_build`). Mode 2 is the C oracle (`IR_interp.c`). There is NO per-mode driver code and NO
> ring→tree adapter — `sno_ring_to_tree` is DELETED; LOWER must emit the four-port statement-BB shape directly.
> Recipe per statement: (a) LOWER it into the four-port BB graph (Icon `lower_expr_threaded` is the model;
> `test_sno_1.c` is the SNOBOL4 topology); (b) give each box a BINARY + a TEXT arm, stackless (`[ζ=r12+off]` RW
> + RO `[rip+disp]`, NO ring, NO value stack); (c) both native modes pass from the one graph + one template.
> SNOBOL m4 (0/6) is pending only LOWER emitting that graph — the emission scaffolding is intact and Icon/Prolog
> m4 already emit.
>
> **⚠ SHARED-LOWERER LOCKSTEP NOTE.** `wire_seq` (backs SNOBOL CAT) and `wire_alt` (backs SNOBOL ALT) are SHARED
> three-language helpers; changing their signature/semantics is a LOCKSTEP edit across all three GOAL files +
> re-prove all three. `wire_seq`'s fail-chain walks back past bounded elements to the nearest resumable
> predecessor; `wire_alt` lowers arms right-to-left threading each arm's exhaustion to the next arm's entry.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer’s SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog’s goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static’d into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon’s directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE’S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language’s arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer’s. This is what makes concurrent sessions’ diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer’s proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files’ FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat’s proof cases are ADDITIVE (append your own; never delete a peer’s). Green = your arm wired right AND you didn’t disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case’s language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr (`lea r10,[rip+Δ_data]`); constant inside a BLOB |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).

**Repo:** SCRIP + corpus + .github
**Sister:** GOAL-COMMAND-CENTRAL.md · GOAL-TEMPLATES-X86.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

---

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (SNOBOL4) — ORDERED, DO BEFORE REG LADDER (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** De-cram + de-fuse each file (de-cram first because cram hides the duplicated logic underneath it), then the de-dup/RT-fix sweep. After EACH step: SNOBOL4 m2 7/7 HARD byte-identical, smoke 3-mode unchanged, purity green, commit. Copy the worked example: `bb_binop_*.cpp` + 38-line `bb_binop.cpp` router (Icon-owned; done 2026-06-01). The de-cram steps are prep; **SNO-HY-7 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [ ] **SNO-HY-1 — `bb_pat_break.cpp` (349).** De-cram: one file per distinct four-port shape behind a `bb_pat_break` router. Group 95%-identical cursor-advance shapes (do NOT over-split). De-fuse any `pBB->…->ival/sval` operand reads.
- [ ] **SNO-HY-2 — `bb_pat_tab.cpp` (286) + `bb_pat_span.cpp` (271).** TAB/RTAB and SPAN: split inline-vs-RT-call shapes; group near-identical. Routers.
- [ ] **SNO-HY-3 — `bb_sno_assign.cpp` (226) + `bb_capture.cpp` (226).** Split literal-rhs vs slot-rhs vs name-store; the capture deque-save vs @-cursor-write. **De-fuse: a literal rhs is its own producer box — read its slot, do not seal its value here.**
- [ ] **SNO-HY-4 — `bb_pat_any.cpp` (218) + `bb_pat_notany.cpp` (215).** cset-blob vs single-char; group if 95%-identical between the two files' shapes. Routers.
- [ ] **SNO-HY-5 — `bb_pat_cat.cpp` (194) + `bb_pat_alt.cpp` (185) + `bb_pat_arb.cpp` (183).** Combinators. The variable-length define/jmp-pair loop is its own shape; fixed shape another. (The variable-length define/jmp-pair loop derives offsets from a running length — that is a separate design question; split the shapes now.) Routers.
- [ ] **SNO-HY-6 — audit the rest (`bb_pat_len` 161, `bb_pat_pos` 158).** Split only if >1 four-port shape; else mark NO-SPLIT-NEEDED. `bb_lit.cpp` (185) — its 5 platform arms (`if (PLATFORM_X86/JVM/JS/NET/WASM)`) are the sanctioned per-platform multiplex, NOT a violation; leave it.
- [ ] **SNO-HY-7 — de-dup + RT-fix, all SNOBOL4 boxes.** Any algorithm in both a TEXT and BINARY arm → DELETE both, replace with one `rt_*` call. No emit-time value work (term-build/compare/arith go to RT).
- [ ] **SNO-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for SNOBOL4-owned files; wired into Session Setup. m2 7/7 HARD held throughout.

## 🔴 CURRENT PRIORITY (Lon directive 2026-06-01) — DO THIS FIRST: REG LADDER (BB TEMPLATES → RATIFIED REGISTERS)

**The SNOBOL4 pattern BB templates are NOT yet on the ratified registers** — they still use the legacy subject
model (`[r10]` cursor; Σ/Δ via `movabs &Σ`/`&Σlen` = emitter-process global addresses). Migrating them to
Σ=R13 / δ=R14 / Δ=R15 / ζ=R12 is **the current top priority** (Lon): it brings convention compliance AND removes
the process-local-address bake that blocks SNOBOL **mode-4** (the m4 0/6 cause). This ladder runs BEFORE the rest
of the PB-RB feature ladder (PB-RB-4+) and the BROKERED-ERADICATION rung (both still below, lower priority until
the registers are correct). REG-0 is coupled to PB-RB-3 (now landed), so REG-1 (`bb_lit`) is the first code step.

### ⭐⭐ REG LADDER — SNOBOL4 PATTERN-FAMILY REGISTER-LAYOUT MIGRATION (Lon directive 2026-06-01, Opus 4.8)

Bring the SNOBOL4 pattern family from the **legacy subject model** (cursor in the `[r10]` per-BLOB data-block
field; Σ via `movabs &Σ;deref`/`lea [rip+Σ]`; Δ via `movabs &Σlen`/`[rip+Σlen]` — `TEMPLATE_ADDR_SIGMA`/
`TEMPLATE_ADDR_SIGLEN` = **emitter-process global addresses**) to the **ratified register convention** Σ=R13,
δ=R14, Δ=R15 (ζ=R12, r10 stays the per-BLOB DATA-block ptr). Two wins in one: (a) convention compliance; (b)
**removes the process-local-address bake → SNOBOL mode-4 relocatability** (the m4 0/6 blocker). NOT a convention
change (the table is untouched) → SNOBOL-session-local, no lockstep. Each step: prove topology
(`prove_lower2.sh`) unchanged, migrate BINARY+TEXT arms together (SAME processing, only bytes-vs-GAS differ),
disasm-verify the new register usage, gate. **Mode-2 oracle (`bb_exec.c`) is UNTOUCHED — these are modes-3/4
templates only; m2 7/7 HARD must stay invariant every step.**

- [x] **REG-0 — register-establishment contract + r13 de-confliction — ✅ DONE (2026-06-03 OPUS48 session 4, with the PB-RB-3 RESTORE, SCRIP `8cd05c1`).** Exactly the canonical form: **BB_MATCH (PB-RB-3) HEAD** loads `R13 ← Σ-slot`, `R15 ← Δ-slot` from SUBJECT's ζ-frame and seeds start=0 (ch.18 step 1, the δ-seed); the RETRY piece re-sets R14 per start-iteration (the ch.18 OUTER loop). R13/R14/R15 callee-saved survive `call memcmp@PLT` with only `push/pop r10` per-box guards (REG-RO residue). Original spec retained: Pin who sets
  R13/R14/R15 and that they survive the chain. Canonical: **BB_MATCH (PB-RB-3) α** loads `R13 ← Σ-slot`,
  `R15 ← Δ-slot` from SUBJECT's ζ-frame and `xor r14,r14` (δ=0, ch.18 step 1) before entering the element graph;
  the ch.18 OUTER start-loop re-sets R14 per start-iteration. R13/R14/R15 are **callee-saved (SysV)** so they
  survive `call memcmp@PLT` with NO per-box save (only the caller-saved r10 needs `push r10`/`pop r10`).
  **r13 de-confliction:** r13 doubles as the SM-state register ONLY in SM context; SNOBOL pattern chains emit
  ZERO SM opcodes (sibling of ICON SM = ZERO OPCODES), so R13=Σ is unambiguous on this path. NO element edits in
  REG-0 — it is the contract REG-1+ depend on. **DO REG-0 AS PART OF PB-RB-3's BB_MATCH α** (preferred), or — to
  unit-test elements before BB_MATCH — a thin subject-register prologue shim in `sno_flat_chain_build`/`_text`
  that loads R13/R15 from SUBJECT's ζ-slots + zeroes R14 after the SUBJECT box. Gate: build rc=0; all gates
  invariant (no element bytes changed yet).
- [x] **REG-1 — migrate `bb_lit` (the proven reference element). ✅ DONE (audit-confirmed 2026-06-03, was left unchecked).** `bb_lit.cpp` carries `[REG-1 Σ=r13 δ=r14 Δ=r15]`, reads cursor=r14d / base=r13 / length=r15d, with ZERO `TEMPLATE_ADDR_SIG*`. Only residue is the `[r10]` cursor-mirror writes + `push/pop r10` guards, which are REG-RO's job (and coupled to `xa_flat.cpp:140` — see the REG-LADDER RECONCILIATION note at top). Original spec retained:
  `mov eax, r14d`; cursor write `mov [r10], eax` → `mov r14d, eax`; Σ-base `movabs rax,&Σ; mov rax,[rax]` (BIN) /
  `lea rcx,[rip+Σ]; mov rax,[rcx]` (TEXT) → use `r13` directly; Δ-compare `movabs rcx,&Σlen; cmp eax,[rcx]` →
  `cmp eax, r15d`. β arm: `δ -= len` becomes `sub r14d, len` (no `[r10]`). Re-derive the byte sequence + patch
  offsets (the patch tuple shrinks — the two `movabs`+deref blocks vanish). Removes both `TEMPLATE_ADDR_SIG*`
  bakes from `bb_lit`. Prove: prove_lower2 topology unchanged; mode-3 `S 'b'` in `'abc'` → `[1,2]` under REG-0;
  disasm shows cursor=r14/Σ=r13/Δ=r15, no `&Σ`/`&Σlen` imm64. Gate: m2 7/7 HARD invariant; m3 ≥ floor; purity
  clean; g_vstack==0.
- [x] **REG-2 — cursor-advancing leaves. 6/6 COMPLETE (SCRIP `65686c2`, 2026-06-01 Opus 4.8).** `bb_pat_len`,
  `bb_pat_any`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_break`, `bb_pat_rem` — same rewrite per box (verify each box's
  actual cursor-field offset + `&Σ`/`&Σlen` sites against disasm before editing; they are NOT all identical). Each step
  removes that box's `TEMPLATE_ADDR_SIG*` bakes. Gate per box (or small sub-group); m2 invariant.
  **First 5 (SCRIP `eb4bf7c`):** `bb_pat_len` (34B, sites {13,25,29,30}), `bb_pat_rem` (13B, {4,8,9}), `bb_pat_any`
  (74B, {8,52,61,65,70}), `bb_pat_notany` (74B, same; byte@50 `0F84`→`0F85`), `bb_pat_span` (195B,
  {118,143,147,167,191}; internal Δ jge +62 / je +18 / jmp loop −86; r11 base-copy + its push/pop dropped, Σ=r13 used
  directly). **`bb_pat_break` LANDED THIS SESSION (dual-arm, both converted in one pass for the REG-FENCE grep):**
  plain BREAK **153B, sites {125,129,149}** (internal Δ jge +63 / jnz +19 / jmp loop −88); BREAKX **290B, sites
  {125,130,134,265,286}** (α scan + β rescan; identical per-loop internal jumps jge +87 / jnz +19 / jmp loop −88;
  `z` in [zeta+8], `z_orig` in [zeta+12] — the 4B padding of the 16B `rt_cs_t`, recovered as δ−z before z++). Both
  arms assembled+objdump-verified via the `as`-transcribe route, then Python byte-recounted to confirm every site.
  BINARY+TEXT both; r11 + push/pop r11 dropped (Σ=r13 direct), only push/pop r10 around strchr remains. Token-clean:
  zero `TEMPLATE_ADDR_SIG*`/`[r10]` in code OR comment. β semantics preserved (BREAK δ−=z on β; BREAKX z_orig recover
  + z++ + rescan-to-next). Zero `b.size()` introduced (stash-verified: 123 with and without the diff).
- [x] **REG-3 — cursor-verify / position leaves. ✅ DONE (audit-confirmed 2026-06-03 session 2; was left unchecked — subsumed by the x86() revamp).** `bb_pat_pos`/`bb_pat_tab` carry `[REG-3 δ=r14 Δ=r15]` (RPOS/RTAB read Δ=r15d), `bb_pat_atp` `[REG-3 δ=r14]` (cursor read `mov esi,r14d` into `rt_at_cursor`); zero `TEMPLATE_ADDR_SIG*`; remaining `push/pop r10` guards around the @PLT calls are REG-RO's job. Original spec: `bb_pat_pos` (RPOS folded), `bb_pat_tab` (RTAB folded),
  `bb_pat_atp` (`@var` writes the cursor → write R14). POS/RPOS read R14 (and Δ=R15 for RPOS) and compare; TAB/RTAB
  advance R14 to a computed target. Gate; m2 invariant.
- [x] **REG-4 — combinators. ✅ DONE (audit-confirmed 2026-06-03 session 2).** `bb_pat_fence` saves/restores δ via r14d↔ζ-slot `FR(sdoff())` (`bb_slot_claim(4)`; its comment string says REG-3 but it IS this rung's saved-δ-to-ζ shape); `bb_pat_cat`/`bb_pat_alt` are pure `x86_pair_loop()` port wiring (14 lines each) — they thread δ via the ports BY CONSTRUCTION, zero cursor ops, zero r10. Original spec: `bb_pat_alt`, `bb_pat_cat`, `bb_pat_fence` — they thread δ via the ports and
  save/restore δ on backtrack: the saved-δ slot moves from the `[r10]` data-block field to a **ζ-slot save of R14**
  (`mov [r12+off], r14d` / restore), NOT `[r10]`. FENCE seals δ on α, restores on β (commit) — now via R14+ζ-slot.
  Gate; m2 invariant.
- [x] **REG-5 — generators + capture. ✅ DONE for all SURVIVING members (audit-confirmed 2026-06-03 session 2).** `bb_pat_arb` `[REG-4 Σ=r13 δ=r14 Δ=r15]` with z/zo generator state in ζ-slots (`bb_slot_claim(8)`, `FR(zoff/zooff)`, bound check `cmp eax,r15d`, zero r10); `bb_pat_defer` reads δ `mov edx,r14d` / writes back `mov r14d,eax` (push/pop r10 guard = REG-RO). `bb_arbno.cpp` + `bb_capture.cpp` NO LONGER EXIST (STUB CLEANUP — a `bb_*.cpp` existing ⇔ box is real); when recreated they come back as x86() on the ratified regs, and BROK-1/BROK-2 are their jump-wired rebirth. Original spec: `bb_pat_arb`, `bb_arbno`, `bb_capture`
  (the `std::deque<int>` saved-δ pattern stores R14 snapshots), `bb_pat_defer`. Per-activation δ state migrates
  from the `[r10]` block to R14 + ζ-slot/deque saves. Since BROK-1/BROK-2 convert CAPTURE/ARBNO to jump-to-α/β,
  do REG-5 **with or after** those rungs to avoid double-rework. Gate; m2 invariant.
- [ ] **REG-RO — READ-ONLY locals to IP-RELATIVE (the RW ladder's DUAL; this is what finishes r10 off).** Lon
  directive 2026-06-01. RULES.md **ICON READ-ONLY LOCALS ARE IP-RELATIVE FACT RULE**: a per-box compile-time
  constant — literal string bytes, cset pointer, a fixed bound, an op code, AND the resolved address of a runtime
  helper — is RO and MUST be reached by `[rip+disp]` into SEALED data placed adjacent to (within/next to) the box's
  own BLOB, NEVER by an absolute `movabs` immediate and NEVER from an `[r10]`-block field. Today the SNOBOL pattern
  **BINARY** arms bake their RO ADDRESSES as `movabs` imm64 — `bb_lit` `movabs rsi,&lit` + `movabs rax,&memcmp`;
  `bb_pat_any`/`notany`/`span`/`break` `movabs rdi,&cset` + `movabs rax,&strchr` (the matching **TEXT** arms ALREADY
  do this right: `lea reg,[rip+label]` / `call …@PLT`). Per box, move each baked ADDRESS into a sealed RO data
  trailer emitted immediately after the box code and load it with `lea`/`mov reg,[rip+disp]`, where `disp` is a
  LITERAL emit-time constant derived from the box's fixed layout (data and access live in the SAME box BLOB, so the
  disp is knowable by hand — FACT RULE TWO LITERAL FORMS preserved: the byte map stays hand-coded, only the
  addressing mode changes). NOTE — a small literal INTEGER operand (e.g. `bb_lit`'s `mov rdx,len`) is a normal
  immediate, NOT addressed storage, and is OUT OF SCOPE. **PAYOFF:** (1) conforms the SNOBOL pattern family to the
  RO FACT RULE; (2) makes the box POSITION-INDEPENDENT in the BINARY (mode-3 JIT) arm too — a SECOND contributor to
  lifting SNOBOL m4, alongside the `&Σ`/`&Σlen` removal; (3) with RW state now in ζ=R12 / Σ=R13 / δ=R14 / Δ=R15
  (the RW ladder above) and RO state in `[rip+disp]`, **r10 has NO remaining purpose** — the `[r10]` cursor-mirror
  writes and the `push r10`/`pop r10` guards around `memcmp`/`strchr` are DEAD and are removed here, eliminating
  r10 from the pattern family entirely (the RW ladder removes [r10]-as-cursor; REG-RO removes the last r10 traffic).
  Sequence: do REG-RO **after** the RW ladder (REG-2…REG-5) so each box is touched once; per box re-derive the byte
  map + patch offsets (the `movabs`+imm64 block, 10 bytes, becomes a `lea`/`mov [rip+disp]`, 7 bytes — offsets
  shift; verify with `as`+`objdump` exactly as REG-2 did). Gate per box; m2 7/7 HARD invariant. COMPLETION TEST
  (rung): no `movabs` loading an RO ADDRESS (lit / cset / helper-fn ptr) remains in the SNOBOL pattern BINARY arms —
  each is `[rip+disp]` into sealed RO data; **zero `r10` in ANY form** (`[r10]`, `push r10`, `pop r10`) in the
  pattern family; m3 ≥ floor; probes green.
- [~] **REG-FENCE — gate AUTHORED 2026-06-03 (TIER 1 locked; TIER 2 flips to HARD at REG-RO).** `scripts/test_gate_sno_pat_reg.sh` exists: **TIER 1** = `TEMPLATE_ADDR_SIGMA|TEMPLATE_ADDR_SIGLEN` in the SNOBOL pattern family == **0** (HARD, passes now under `--strict` — the &Σ/&Σlen bake removal is done); **TIER 2** = `r10` residue (currently 20 refs / 7 files), INFORMATIONAL until REG-RO migrates `xa_flat`'s `[r10]` cursor read to r14 and drops the bb_lit mirror + memcmp/strchr guards, at which point flip the marked line in the script to enforce `r10_total==0`. Still TODO: wire it into the live Session-Setup gate runner, and re-measure SNOBOL m4 after the LOWER four-port wiring lands (NOT after the bake removal — that is already done and did not lift m4; the real m4 blocker is the `sno_ring_to_tree` removal at `scrip.c:801`). Original spec retained:
  `grep -lE 'TEMPLATE_ADDR_SIGMA|TEMPLATE_ADDR_SIGLEN' src/emitter/BB_templates/bb_pat_*.cpp src/emitter/BB_templates/bb_lit.cpp src/emitter/BB_templates/bb_capture.cpp src/emitter/BB_templates/bb_arbno.cpp`
  == empty, AND no `[r10]`-as-cursor read/write remains in those files (cursor is r14, subject r13, length r15),
  AND (post-REG-RO) **zero `r10` in any form** (`[r10]`/`push r10`/`pop r10`) in the pattern family with every RO
  address reached `[rip+disp]` (no RO-address `movabs` left). Wire into the Session Setup gate list so it can never
  creep back. **Then RE-CHECK SNOBOL m4 smoke** — with the `&Σ`/`&Σlen` bakes gone AND the RO addresses now
  position-independent, the pattern boxes are relocatable, so the m4 0/6 floor should finally be liftable (track
  the new m4 count). COMPLETION TEST (rung): the new gate green + in Session Setup; m2 7/7 HARD held; m3 ≥ floor;
  SNOBOL m4 re-measured (expected > 0/6 once a pattern chain assembles+links+runs standalone).

**COMPLETION TEST (REG ladder):** `test_gate_sno_pat_reg.sh` green (zero `TEMPLATE_ADDR_SIG*`, zero `[r10]`-cursor,
and — post-REG-RO — zero `r10` in any form with all RO addresses `[rip+disp]`, in the SNOBOL pattern family); every
pattern box reads cursor=R14 / subject=R13 / length=R15 and reaches RO constants by IP-relative addressing; m2 7/7
HARD invariant throughout; SNOBOL mode-4 pattern smoke re-measured and improved (the process-local-address blocker
is gone). The convention TABLE is byte-identical-×3 and UNCHANGED (this rung conforms boxes to it, does not edit it).

---

## ✅ GROUND-ZERO LOWER REWRITE (unified four-port AST→IR) — FOUNDATION PROVEN (2026-05-31)

`src/lower/lower.c` (was `lower2.c`, the new tree root after the old `lower.c` was deleted) is the ONE unified
AST→IR pass on the Proebsting four-port attribute-grammar model: one funnel
`lower2(cx, e, γ_in, ω_in, &α_out, &β_out)` → branch on `cx.role ∈ {VALUE, PATTERN, GOAL}` → ONE
`switch(tree_e)` per role (~2/3 of kinds role-monomorphic). γ/ω (succeed/fail) INHERITED in; α/β (start/resume)
SYNTHESIZED out; `IR_t` ports are POINTERS so goto-chains COLLAPSE (Proebsting Fig-2 for free). Three primitives:
`nalloc` / `set_succ_fail` (default-only) / `ret`. Proven faithful to Proebsting Figs 1&2 via
`scripts/prove_lower2.sh` (topology = node counts + α/β/γ/ω; `5 > ((1 to 2)*(3 to 4))` → exactly 9 IR nodes).
Tree-pattern matching (`tm`/`tm_g`, match shallow shape + capture children) is a later STEP-5 refactor of proven
box code into match-capture-recurse-wire form — the bridge to an Icon-bootstrap lowerer. Refs:
`Proebsting-...-Goal-Directed-Evaluation.pdf`, `jcon_irgen.icn` (`ir_a_*`). (The per-box BB/SM/XA template ladder
below is downstream of emission and is unchanged by this rewrite.)

## ⛔ MANDATORY READ BEFORE EVERY SESSION

> **⛔ READ FIRST for SBL-PAT-BB (modes-3/4 pattern work) — Lon "Eureka" 2026-05-31.** Before touching the
> SUBJECT/PATTERN/REPLACEMENT build path, read **ARCH-SNOBOL4.md → "Native pattern architecture — modes 3 & 4
> (pattern = built BB graph)"** AND **ARCH-x86.md → "Two block TYPES the emitter outputs (BB vs XA)"**. The
> active rung is **SESSION RUNG #0 SBL-PAT-BB** (below); first incomplete step = **PB-1 PATTERN-BUILDER BB** (PB-0 done, 179bf4d). Core idea:
> a SNOBOL4 pattern is a runtime byrd-box GRAPH — phase-2 lowers to BUILDER BBs that build BBs; phase-3 runs
> via a generic BB_MATCH box; later, INVARIANT patterns BAKE to a static BB. (PLAN.md rule 7 already routes
> MODE3/4-EMIT work to ARCH-x86.md + ARCH-SCRIP.md, both of which cross-ref the ARCH-SNOBOL4 section.)

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle)
    → [mode 4] walk_bb_flat → FILL → walk_bb_node → emit_core
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 via bb_bin_t)
```

- **Mode 2 (`--interp`):** `sm_interp_run` + `bb_exec.c` C oracle.
- **Mode 3 (`--run`):** `sm_run_native` → SM_templates BINARY arms → sealed RX → jump in. BB call-outs via flat-wired `bb_build_flat`. Opt-in via `SCRIP_M3_NATIVE=1`; default still `sm_interp_run`.
- **Mode 4 (`--compile`):** Emit phase uses TEXT arms → GAS → gcc link. Standalone runtime builds pattern blobs via `bb_build_brokered` → template BINARY arms.

> **⛔ TESTING DIRECTIVE (Lon 2026-05-31) — ALWAYS RUN ALL THREE MODES FOR THIS GOAL.** Whenever you test
> SCRIP, exercise **mode 2 (`--interp`)**, **mode 3 (`--run` / SB-LINEAR)**, AND **mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run the binary)** — every time, from now on.
> `scripts/test_smoke_snobol4.sh` now does this: mode 2 is the **HARD gate** (exit 0 requires mode-2 all-pass);
> modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked with `MODE3_MIN`/`MODE4_MIN` PASS floors,
> default 0) so the full native picture is always visible. NEVER report a mode-2 number alone — always run and
> record 3 and 4 alongside it. (Mode 3/4 for SNOBOL4 are currently 0/6 — the `--run` native path and the
> SMX-4-excised `--compile` x86 emission are not yet rebuilt; the directive makes that gap visible each run.)
> Raise `MODE3_MIN`/`MODE4_MIN` as those modes come back so regressions in them also fail the gate.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY (no silent cross-mode fallback / no silent eps substitution).

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)`. Template emits α-port code (fresh: match, advance Δ, jump γ or ω) followed by β-port code (retry: undo, advance differently, jump γ or ω; some kinds β = lbl_ω directly).

**Runtime state in TEXT arm:** `[r10]` = Δ (cursor, 32-bit int). `[rip + Σ]` = subject ptr. `[rip + Σlen]` = length. `nd->sval` = charset string baked into `.data`. `nd->counter` (int64) = runtime mutable state for generators.

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing rel32 patch offsets. `movabs` for absolute addresses. Refs: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104B, sites {17,72,86,90,100}), `bb_pat_notany.cpp`, `bb_pat_break.cpp` (178B), `bb_capture.cpp` (128B).

**Per-node persistent BINARY storage (SHARED PATTERN):** brokered blobs have no ELF `.data`. Two patterns:
1. `g_emit.bb_cs_zeta` `rt_cs_t {const char *chars; int delta;}` — `delta @+8` for SPAN/ARBNO counters; baked via `movabs rcx, &zeta`.
2. Process-lifetime `std::deque<int>` allocator (e.g. `cap_alloc_saved_delta_slot()`) — pointer never invalidates, GC-safe via C++ heap. Use for SPAN-2 / CAP / BREAKX scratch.

**DO NOT** use `GC_MALLOC` for per-node scratch baked as imm64 — bb_pool is mmap'd, GC can't see the address.

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## ✅ RENAME BB → IR COMPLETE (2026-05-30)

The uppercase IR-graph constructs were renamed `BB_*`→`IR_*` (the directed graph IS the IR now that the Stack
Machine is gone): `BB_t`→`IR_t`, `BB_graph_t`→`IR_graph_t`, `BB_op_t`→`IR_e`, the ~125 node-kind enum members
(`BB_LIT_I`…`BB_PAT_ATP`+`BB_OP_COUNT`), `BB_LANG_*`→`IR_LANG_*`, the IR API ctors (`BB_alloc`/`BB_free`/
`BB_node_alloc`/`BB_lower_pat`→`IR_*`), the header `BB.h`→`IR.h`, and the `baselines/per_kind/**/BB_*` fixtures.
**STAYS `BB`** (emit-side, reached only via `g_emit` — past the IR boundary): the `BB_templates/` directory +
`BB_MEDIUM_*`/`BB_MODE_*`/`BB_PLATFORM_*`/bb_*.h guards + all lowercase `bb_*`. Templates are TRANSLATORS — they
CONSUME `IR_t` (renamed) but the template MACHINERY (file/dir/fn names, `g_emit.bb_*` fields) stays `BB`/`bb`.

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                   # GATE-1: 13/13
bash scripts/test_smoke_unified_broker.sh            # GATE-2: ~30-36 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh      # GATE-3: 178/280
bash scripts/test_interp_broad_corpus_and_beauty.sh  # GATE-4: 251/280
bash scripts/test_snobol4_pat_rung_suite.sh          # M2=19 M4=15 SKIP=0
bash scripts/audit_m3_native_binary_arms.sh          # GATE OK
bash scripts/test_gate_sno_pat_reg.sh                # REG-FENCE: TIER1 SIG=0 (HARD); TIER2 r10=20 (info, pending REG-RO)
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh  # 195/280
```

For full failure list patch `head -40` to `head -300` in test_interp_broad_corpus_and_beauty.sh copy.

---

## Active rung: M3-NATIVE-4 — per-language bring-up + corpus parity (SNOBOL4)

### ⭐ MILESTONE (2026-05-29 Opus 4.8): NATIVE-ONLY GAP CLOSED

After SBL-1010 + SBL-1016, the broad-corpus partition has **ZERO native-only failures**:
every one of the 28 remaining native FAILs **also fails in `--interp` (mode-2)**. Native ==
mode-2 oracle == **252/280**. The "knock down remaining native-only failures" objective of this
rung is therefore effectively DONE — there are no more native-dispatch bugs in the broad corpus.
All further corpus climb now requires fixing the **mode-2 ORACLE** (which lifts BOTH modes
simultaneously, exactly as SBL-1016 demonstrated: fix once, both modes gain). Verified via
`comm -23 native_fails m2_fails` = empty. To re-confirm: run the broad corpus under
`SCRIP_M3_NATIVE=1` and under plain `--interp`, sort the two FAIL lists, diff them.

### Next phase: ORACLE-PARITY (lifts both modes)

**Completed (mode-2 oracle + native) — full narrative in git log / HANDOFFs:** variable-argument pattern family (SPAN/ANY/NOTANY/BREAK/LEN/POS/RPOS/TAB/RTAB accept `TT_VAR`, resolved late in `bb_exec.c`) + charset-EXPR + ARBNO-combinator wiring; SBL-ARB-CAT-BACKTRACK (m3 native + m4 flat) + ARB-as-pattern-VAR (m2 oracle); DEFERRED capture-commit; 046/047 TAB/RTAB native SIGSEGV fixes; default flipped to native (no fallback). native →243.

**Open (mode-2 oracle gaps — fix oracle first, native parity follows):**
- [ ] 1011_func_redefine / 1013_func_nreturn / 1017_arg_local — fail in BOTH modes (DEFINE-redefinition, NRETURN-as-lvalue, ARG/local introspection). Audit-only bucket.
- [ ] Pre-existing m2 oracle gaps (audit-only): rungs 044/045/046/048/052/054/055/056/057 — `bb_exec.c` POS/RPOS/TAB/REM/star_deref/fail_builtin gaps.

- [~] **FENCE-commit / ALT-fall-through (124 + 114) — INLINE class FIXED; DEFER-capture-resume blocker remains.**
  SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL landed: Δ-advancing single-shot leaves set `β=self` (re-enter to undo Δ on ALT fall-through); FENCE saves Δ on α, restores on β (commit). Inline probes pass m2. **Blocker:** 124/114 reach the ALT through a pattern VARIABLE (`BB_PAT_DEFER`); on `bb_exec_resume` the alt entry is alt1's capture node, which can't distinguish "backtrack" from "commit/regrow" (same `inner.state>0` ambiguity as SBL-CAP-REGROW). Capture-transparency prototype (`resume_at` + `g_resume_backtrack` one-shot) made 124 green but regressed 3 sealed-FENCE-via-var tests (over-reach: re-enters a sealed FENCE). **NEXT FIX:** gate the capture's backtrack-delegation so it does NOT re-enter an inner that wraps a sealed/exhausted FENCE (delegate only when inner holds a live backtrackable generator). Clean floor = `77a39e82`; minimal repro of the pure DEFER-capture-resume gap = p8 (`token=('if'.K|SPAN.I)`).

### ⭐ TOP PRIORITY (Lon directive 2026-05-30): Complete all SNOBOL4 pattern BB BINARY and TEXT arms for mode-3 and mode-4

Every SNOBOL4 pattern BB template must have a working BINARY arm (mode-3 `--run`) and TEXT arm (mode-4 `--compile`). No pattern primitive may fall to the `default: jmp ω` stub once this rung is done. Honest `bomb_bytes()` stub is acceptable only as a temporary placeholder while the arm is being written; a permanent `jmp ω` for a real opcode is a RULES violation once the rung is declared complete.

**Missing BINARY arms (mode-3):** SPAN (SBL-SPAN-2 — deque pattern), ARBNO (SBL-ARBNO-3 — deque pattern), REM, ABORT, FENCE, ALT (combinator EP-walk present but needs corpus validation), CAT (same).
**Mode-4 TEXT arm gaps:** DEFER needs alignment fix (`push r10; push r10` convention per SBL-CAP-OUTPUT-R10); SBL-M4-FLATWIRE — `--compile` must flat-wire at emit time rather than brokering at runtime.
**Work order:** fill BINARY arms first (SPAN → ARBNO → REM → ABORT → FENCE), gate each via `--run` corpus delta, then audit TEXT arms for mode-4.

### ⭐⭐ SESSION RUNG #0 (Lon "Eureka" directive 2026-05-31): SBL-PAT-BB — pattern = built BB graph (modes 3 & 4 ONLY)

**SCOPE: modes 3 (`--run`, BINARY) and 4 (`--compile`, TEXT) ONLY. Mode 2 (interp) is NOT in scope and
must NOT regress.** Full architecture in **ARCH-SNOBOL4.md → "Native pattern architecture — modes 3 & 4"**
and ARCH-x86.md → "Two block TYPES (BB vs XA)". The five phases of `SUBJ ? PAT [= REPL]`, each emitted as
BB(s) (the ONLY vehicle that does work in modes 3/4 — XA blocks only wrap/stitch):

> **THE EUREKA.** Phase 1 build SUBJECT (easiest) → SUBJECT BB loads `Σ/δ/Δ`. Phase 2 build PATTERN →
> **builder BBs that build OTHER BBs dynamically** (a SNOBOL4 pattern is a runtime byrd-box graph: `'a'|'b'`
> CONSTRUCTS). Phase 3 RUN pattern → the generic **BB_MATCH box** runs the SPITBOL ch.18 scanner over the
> built graph against the subject (unanchored start-loop unless `&ANCHOR`, four-port backtrack, NO value
> stack). Phase 4 build REPLACEMENT (can fail). Phase 5 do REPLACE (fails if subject not an lvalue —
> `"hello"`, `99`). **Build (ph.2) and run (ph.3) are GENUINELY SEPARATE.** The current mode-2 `IR_SCAN`
> super-node + hidden `IR_alloc` sub-graph is the WRONG layer (`sno_ring_to_tree` anti-pattern in the
> lowerer) and is NOT this design.
>
> **THEN — OPTIMIZATION (after ph.1–5 work): INVARIANT-PATTERN BAKE.** Collapse any maximal run of builder
> BBs that builds an INVARIANT pattern (all components compile-time constant: literal str/int/cset, fixed
> LEN/POS/RPOS, constant ALT/CAT of such) into ONE **STATIC pattern BB BAKED into the generated code**
> (emitted once as sealed data/code, no runtime rebuild). Only VARIANT builders (`SPAN(VAR)`, `ANY(expr)`,
> deferred `*EXPR`, indirect `$NAME`) stay dynamic. const subtree ⇒ bake; references-runtime ⇒ keep builder.

Each step's discipline: prove the four-port TOPOLOGY first (`prove_lower2.sh`: node counts + α/β/γ/ω), then
the BINARY arm (verify mode-3 `--run`), then the TEXT arm (verify mode-4 `--compile` → `as` → `gcc` → run).
Smoke target ladder: `S 'b'` (plain match) → `S 'b' = 'X'` → `aXc` (match+replace).

**OLD PB-0…PB-OPT ladder — ✅ done / superseded (history in git + HANDOFFs).** PB-0 (`IR_SUBJECT` +
`bb_sno_subject`, loads Σ/δ/Δ into the locked regs / ζ-frame; `rt_sno_subject_load`) and PB-1
(`IR_PAT_BUILD_LIT` literal builder) landed — then the CORRECTED PATTERN ARCHITECTURE (below) retired the
`PATND_t`-builder approach: a pattern element is an EMITTED byrd-box (the existing `IR_PAT_*` matcher template
referenced via `REF_INVARIANT`), NOT a `PATND_t` or a `tree_t`, and an invariant literal needs NO runtime
builder. The `rt_sno_match_lit` ch.18 scan kernel (`PATND_t`-free, raw subj/lit, unit-tested 7/7) SURVIVES as
the literal element's inner scan. The MATCH phase survives as a `bb_box_fn`-graph DRIVER (ch.18 outer
start-loop), not a `PATND_t` reader. Rebuilt as PB-RB-1/2/3 below.

---

### ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE, 2026-06-01)

Supersedes the PB-1/PB-2/PB-3/PB-OPT mechanism above (kept for history, marked SUPERSEDED). The matcher
boxes are the EXISTING `IR_PAT_*` templates (Fork C); the only NEW boxes are `REF_INVARIANT`, `STITCH_SEQ`,
`STITCH_ALT`, and the phase-3 `BB_MATCH` driver. Same discipline every step: prove four-port TOPOLOGY first
(`prove_lower2.sh`), then BINARY arm (mode-3 `--run`), then TEXT arm (mode-4 `--compile`→`as`→`gcc`→run).
**Mode-2 (`IR_SCAN`) stays intact and MUST NOT regress** (m2 7/7 HARD) — the native chain is modes-3/4;
full `IR_SCAN` retirement is deferred to PB-RB-CONV when the native chain has breadth. Each box reads its
inputs RO `[rip+disp]` (sealed head address, literal bytes) or RW `[ζ+off]` (built head, match state) — NO
`PATND_t`, NO `tree_t`, NO value stack, NO ring (PER-BOX LOCAL STORAGE + NO-VALUE-STACK FACT RULES).
Smoke ladder unchanged: `S 'b'` (plain) → `S 'b' = 'X'` → `aXc`.

- [x] **PB-RB-1 — REF_INVARIANT + retire the PATND_t literal builder.** Delete `IR_PAT_BUILD_LIT` /
  `rt_sno_pat_build_lit` / `bb_sno_pat_build_lit.cpp` (the PATND_t literal builder). Add `IR_REF_INVARIANT`
  (IR.h, append-only) + `bb_ref_invariant.cpp`: loads a sealed element `bb_box_fn` head (RO `[rip+disp]` /
  movabs) into a `ζ`-slot. The sealed element for a literal is the EXISTING `IR_PAT_LIT` matcher box
  (`bb_lit.cpp`); `rt_sno_match_lit` survives as its inner scan. lower `TT_QLIT` pattern → REF_INVARIANT over
  a sealed `IR_PAT_LIT`. Prove topology; mode-3 probe: REF_INVARIANT('b') yields a `bb_box_fn` head in its
  ζ-slot whose code is the `'b'` literal matcher. (No runtime construction — Fork A/E.)
  **[DONE 2026-06-01, Opus 4.8 — EMIT ARM + PROBE]** RETIRE half landed earlier (`6343198`: IR_PAT_BUILD_LIT
  family removed, lower2_pat_build_entry repointed to IR_REF_INVARIANT over a sealed IR_PAT_LIT, prove 64/64).
  THIS turn = the EMIT ARM that was the remaining work: (1) `bb_ref_invariant.cpp` BINARY (25-byte) + TEXT arms
  — load the sealed element `bb_box_fn` HEAD (emit-time constant: `movabs rax,head` BINARY / `lea rax,[rip+lbl]`
  TEXT, RO never on a stack) into an 8-byte ζ-slot `[r12+off]` via `bb_slot_alloc`, then `jmp γ`; β = `jmp ω`
  (bounded single-shot, Fork A/E — NO runtime construction). Modeled on bb_sno_subject.cpp; patch tuple
  `{19,23,24}/{γ,β,ω}/{false,true,false}`. (2) `emit_bb.c` — new emitter-global `g_emit_cfg` (exposes the active
  IR_graph_t to the emit path so a node's operand_aux sidecar is resolvable, mirroring bb_exec.c's g_current_cfg;
  set/restored in sno_flat_chain_build / _text); `pre_build_children` + `pre_build_children_text` recognize
  IR_REF_INVARIANT and pre-build its sealed child resolved via `bb_operand_aux_get` (NOT bb_pat_kid, PEERS RULE);
  the two SNOBOL chain builders run a REF-specific child prebuild (`sno_chain_prebuild_children[_text]`) GUARDED
  by `has_ref` so they stay byte-neutral to every prior shape; `flat_drive_sno_ref_invariant` resolves the cached
  child head and hands it to the box via `g_emit.child_fn`/`bb_child_fn`/`bb_child_lbl`. (3) emit_core dispatch
  was already wired (emit_core.c IR_REF_INVARIANT → bb_ref_invariant). **MODE-3 PROBE PASS** (committed artifact:
  `test/snobol4/pat_bb/probe_pb_rb_1_ref_invariant.c` + `scripts/test_sno_pat_bb_probe.sh`): JIT'd
  SUBJECT('abc') → REF_INVARIANT('b') → SUCCEED via `sno_flat_chain_build`, ran with `rt_frame`, result.v=1.
  **DISASM-VERIFIED**: REF box = `movabs $head,%rax ; mov %rax,0x10(%r12) ; jmp γ` / β:`jmp ω` — the sealed head
  address (a real BB-pool box) lands in ζ-slot `[r12+0x10]`, stackless (ζ=r12, `push r12;mov r12,rdi` prologue),
  NO value stack; and the loaded head disassembles as the EXISTING bb_lit('b') four-port matcher (δ from [r10],
  bounds-check vs Σlen, memcmp 1 byte, advance δ → γ). The sealed element is REFERENCED, not run (running is
  PB-RB-3 BB_MATCH). v_scan NOT rewired (mode-2 IR_SCAN super-node intact → ZERO regression; retirement is
  PB-RB-CONV). Gates ALL match watermark: make scrip rc=0, libscrip_rt rc=0, SNOBOL4 m2 **7/7 HARD** / m3 5/6 /
  m4 0/6, Icon m2 **11/11 HARD** / m3 11/11 / m4 9/11, prove_lower2 **64/64**, sm_dead 0, concurrency OK, purity
  7 (MEDIUM_BINARY-exempt baseline), no-vstack `g_vstack`==0. **NEXT (#1): PB-RB-2** (matcher-box four-port ABI —
  how the head box-graph is driven over Σ/δ/Δ via α/β/γ/ω; ground in the canonical Icon/Prolog brokered-graph
  pattern per CONSULT CANONICAL SOURCES) then **PB-RB-3** (BB_MATCH driver reads REF_INVARIANT's ζ-slot head +
  SUBJECT's Σ/δ/Δ and drives the ch.18 unanchored outer start-loop). NOTE on rebuild: `scrip` and
  `out/libscrip_rt.so` MUST be rebuilt in LOCKSTEP — a stale `.so` against a fresh `scrip` shows phantom mode-3
  failures (2/6); always `bash scripts/build_scrip.sh && make libscrip_rt` together before gating.
- [x] **PB-RB-2 — the matcher-box four-port ABI (drive ONE element).** Pin down how the four-port driver runs a
  single matcher element box (`IR_PAT_LIT`) over Σ/δ/Δ via α/β/γ/ω: α tries match at δ, γ on success
  (advance δ, leave span), ω on fail, β to re-offer (generators only). Ground in the canonical
  Icon/Prolog brokered-graph pattern (CONSULT CANONICAL SOURCES rule). Verify the existing `IR_PAT_LIT`
  BINARY/TEXT arms honor it (or adapt minimally). This is the substrate PB-RB-3 drives.
  **[DONE 2026-06-01, Opus 4.8 — SPEC + VERIFY, no code adaptation needed.]** ⚠ STALE REF FIXED: the step said
  "ground in `bb_broker.c`", but `bb_broker.c` (the driver) was DELETED in `646a543` (C-byrd-box teardown). The
  surviving four-port driver is `bb_exec.c` (mode-2 oracle); its `rt_sno_exec_scan` is the ch.18 reference driver
  (anchored/unanchored start-loop). Grounded the ABI there + SPITBOL ch.18 ("Pattern Matching" algorithm steps
  1-6) + the ratified X86-64 REGISTER CONVENTION.
  **PINNED ABI — see "PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI" block below.** Key result: `IR_PAT_LIT`
  (`bb_lit.cpp`) HONORS the port contract in BOTH arms with ZERO adaptation — α bounds-checks `δ+len ≤ Δ`,
  memcmps Σ+δ, advances δ, `jmp γ`; mismatch/overflow `jmp ω` (δ unchanged); β is bounded single-shot (`δ -= len;
  jmp ω` — a literal has NO implicit alternative). Verified vs the PB-RB-1 mode-3 probe disasm + a byte/text
  re-read of both arms this session. The whole SNOBOL pattern family (`bb_pat_any/pos/span/…`) shares this exact
  `[r10]`-cursor / `[rip+Σ]`/`[rip+Σlen]` model (grepped, uniform). **OPEN FORK handed to PB-RB-3 + flagged for
  Lon — see the ABI block's "SUBJECT-STORAGE LOCATION" note: three coexisting homes for Σ/δ/Δ (ratified
  R13/R14/R15 · SUBJECT's ζ-slots · legacy `[r10]`/`[rip+Σ]`); BB_MATCH is the bridge; the family-wide register
  migration is a SEPARATE LOCKSTEP sweep, NOT folded into PB-RB-2/3.** Gates UNTOUCHED (spec-only, no compile this
  step): m2 7/7 HARD / m3 5/6 / m4 0/6, prove_lower2 64/64, sm_dead 0, concurrency OK, g_vstack==0 @ `77bbebc`.

> **⭐ PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI (pinned 2026-06-01, Opus 4.8). The substrate PB-RB-3's BB_MATCH
> drives. Grounded in SPITBOL ch.18 + `bb_exec.c rt_sno_exec_scan` (the ch.18 reference driver) + the ratified
> X86-64 REGISTER CONVENTION. This is a CONTRACT statement, not new code — `IR_PAT_LIT` already conforms.**
>
> **SUBJECT MODEL (names — the casing carries meaning AND the oracle-C vs native-register casing is INVERTED;
> wiring it backwards is the failure mode this note exists to prevent):**
>   - **Σ** (R13) = subject BASE ptr (the fixed whole).
>   - **δ** (R14, lowercase) = CURSOR (the moving scan position), zeroed when the match begins (ch.18 step 1).
>   - **Δ** (R15, uppercase) = subject LENGTH / END (the fixed bound).
>   - ⚠ **In the mode-2 oracle C (`bb_exec.c`/`rt.c`/`stmt_exec.c`) the CURSOR global is named `Δ` (UPPER) and the
>     LENGTH is `Σlen`/`Ω`** (verified: `rt.c:776` `Δ = 0` at match start = cursor; `stmt_exec.c:47` `Σlen` =
>     length; JS `_bb_Δ` "cursor position", `_bb_Ω` loop bound). The RETIREMENT rename sweep **`Δ(cursor)→δ`,
>     `Ω→Δ`, `Σlen→Δ`** reconciles oracle-C ↔ native-register: **oracle-C `Δ` ≡ native `δ` (cursor); oracle-C
>     `Σlen`/`Ω` ≡ native `Δ` (length).**
>
> **FOUR PORTS (per element box; map 1:1 to SPITBOL ch.18 algorithm steps 3-6):**
>   - **α (fresh entry)** = step 4 "apply current pattern at current cursor". Read δ; if `δ + matchlen > Δ` →
>     `jmp ω` (bound check). Compare/scan Σ at offset δ. On match: advance δ past the matched span (step 4
>     "advance the cursor past the characters matched"); the span is IMPLICIT in δ_before..δ_after (a bounded leaf
>     leaves no separate span slot); `jmp γ`. On mismatch: `jmp ω` with **δ UNCHANGED** (the element bound nothing).
>   - **γ (success port)** = step 5 "if subsequent, point to it". Emitter-patched to the successor element's α (or
>     BB_MATCH's success continuation for the last element). The box only `jmp lbl_γ`; it NEVER picks the target.
>   - **ω (fail port)** = step 6 "pop the stack / advance starting cursor". Emitter-patched to the predecessor's β
>     (inner backtrack) or, at the graph root, BB_MATCH's OUTER-loop retry (advance starting δ unless anchored).
>     The box only `jmp lbl_ω`.
>   - **β (resume entry)** = re-offer on backtrack. **BOUNDED single-shot leaf** (literal / LEN / POS / RPOS / TAB
>     / RTAB): β UNDOES its δ advance (`δ -= matchlen`) and `jmp ω` — no alternative to offer. **GENERATOR** (ARB /
>     ARBNO, span-shrink/grow): β yields the next alternative (a different δ) and `jmp γ`, or exhausts → `jmp ω`.
>     (ch.18: "ARB behaves as `(LEN(0)|LEN(1)|LEN(2)|…)`" — the implicit-alternative generator; the bounded leaf
>     has none. This is the ONLY α/β-port difference between leaf and generator.)
>
> **VERIFIED — `IR_PAT_LIT` (`bb_lit.cpp`) conforms, BOTH arms, NO adaptation:** α = `mov eax,[δ]; add eax,len;
> cmp vs Δ(Σlen); jg ω; load Σ+δ; memcmp lit; jne ω; δ += len; jmp γ` (BINARY 121-byte patch tuple
> `{22,89,105,109,121}/{ω,ω,γ,β,ω}` + TEXT `memcmp@PLT` — SAME processing, only bytes-vs-GAS differ). β = `δ -=
> len; jmp ω` (bounded single-shot). Confirmed by the PB-RB-1 probe disasm (the REF_INVARIANT-loaded head IS this
> matcher) + this session's byte/text re-read. The pattern family (`bb_pat_any/pos/span/…`) is uniform on this.
>
> **OPEN — SUBJECT-STORAGE LOCATION (the one unresolved fork; PB-RB-3's bridge, NOT a port-contract issue).**
> Three homes for Σ/δ/Δ coexist today: **(1)** ratified convention Σ=R13/δ=R14/Δ=R15 (registers); **(2)** SUBJECT
> box (PB-0, `bb_sno_subject.cpp`) Σ=`[ζ=r12+off]`, Δ=`[r12+off+8]` (ζ-frame slots), δ "owned by MATCH"; **(3)**
> legacy family (`bb_lit`+siblings) δ=`[r10]`, Σ=`[rip+Σ]`, Δ=`[rip+Σlen]` (sealed data labels). The
> `[rip+Σ]`/`[rip+Σlen]` form is **mode-3-in-process-only** (a baked address breaks mode-4 relocatability — the
> RW-frame rule). **✅ RESOLVED (Lon directive 2026-06-01): adopt the REGISTER model for the pattern family** —
> conform the SNOBOL pattern templates to the ALREADY-RATIFIED convention (Σ=R13, δ=R14, Δ=R15, ζ=R12). **This is
> NOT a change to the convention table** (the byte-identical-×3 table already says R13/R14/R15), so it is NOT a
> lockstep edit — it is the SNOBOL session conforming ITS OWN boxes (`bb_pat_*`) to the table, squarely in its
> lane (EDIT ONLY YOUR OWN LANGUAGE'S BOXES). Lockstep would bite only if the TABLE changed, which it does not.
> BB_MATCH (PB-RB-3) is the register-establishment point: its α loads R13←Σ-slot, R15←Δ-slot, R14←0 from
> SUBJECT's ζ-frame, then drives the element graph; the elements read R13/R14/R15 directly (the **REG ladder**
> below). **⭐ MAJOR PAYOFF: this is ALSO the SNOBOL mode-4 unblocker** — the `&Σ`/`&Σlen` imm64 bakes
> (`TEMPLATE_ADDR_SIGMA`/`TEMPLATE_ADDR_SIGLEN` = addresses of the emitter-process globals) are the reason m4 is
> 0/6 for patterns; removing them = relocatable boxes that a standalone `--compile` binary can run.

---

> **PB-RB-3 DESIGN — RESOLVED (Lon 2026-06-01): MODEL A (INLINE-JUMP).** BB_MATCH `jmp`s the element's α and is
> re-entered via its ω — the proven combinator mechanism (`walk_bb_flat`, as XCAT/XALT), NO `(ζ,int entry)` C call
> (honors the NO-C-BYRD-BOX FACT RULE; `bb_broker.c` is deleted). REF_INVARIANT's load-a-sealed-head-by-call model
> is therefore NOT the base-case drive — it is the primitive for PB-RB-OPT's all-invariant BLOB freeze and
> pattern-valued vars (Fork B) only; the base single-element case emits the element INLINE.

- [x] **PB-RB-3 — BB_MATCH driver (phase 3) — ✅ RESTORED (2026-06-03 OPUS48 session 4, SCRIP `8cd05c1`; was [~] STRUCTURALLY REGRESSED).**
  Rebuilt per `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORE-DESIGN.md` on the **RATIFIED registers** (NOT the
  legacy Σ/Σlen-globals model the `706d665` original used): ONE `bb_match.cpp` x86() template, THREE emissions per
  IR_PAT_MATCH node branched on `op_ival` — **HEAD** (Σ←r13 `FRQ(subj-slot)`, Δ←r15d `FR(subj+8)`, start ζ-slot=0
  ch.18 step 1, `lea r10,[r12+start+8]` ζ-scratch: `bb_lit`'s REG-RO-pending `[r10]` cursor-mirror needs a valid
  cell, and the Icon-shared `xa_flat` FRAME-path epilogue was verified `[r10]`-free, so the mirror lands harmlessly
  in per-activation frame storage until REG-RO deletes it — no global cell, mode-4-relocatable); **RETRY**
  (δ=r14d←start, falls through into the driver-inlined element — no elem_entry label); **ADVANCE** (ch.18 step 6:
  `start++`, `cmp r15d`/`jg ω`, `&ANCHOR` via the new `x86_load_mem64` deref, `jne ω`, `jmp retry`). `bb_subject.cpp`
  loads literal Σ ptr + Δ len into the driver-claimed 16B ζ-slot via `op_a_sval`/`op_sa`. `flat_drive_match`
  rewritten to the 3-piece port-remapped FILL sequence (driver claims the start slot ONCE via `bb_slot_alloc16`,
  promotes `op_sa`/`op_off`, sets `pBB->ival` per piece; `smatch%d_retry`/`_adv` driver-defined);
  `flat_drive_subject` claims+publishes `g_subject_slot` (un-orphaned), loud abort if MATCH precedes SUBJECT;
  `g_subject_slot=-1` reset per chain build. `x86_asm.h` additive: `x86_load_mem64` (`mov reg, qword [base]`,
  `48 8B /r`) + `lea reg,FR(off)` routed to `x86_frame_lea` (REX 0x4D for r10). **VERIFY-FIRST both confirmed:**
  FRQ load64 encodes REX.W+R+B (`4D 8B 2C 24` in the probe disasm); FILL fully resets α+ports per emission and
  BINARY α is record-free, so multi-emission per node is mode-3-safe (TEXT duplicate-α stays the m4 dense-nid
  concern). Probes 3/3 (happy + whole-fail + anchored); disasm-verified stackless, zero `TEMPLATE_ADDR_*`, zero
  `bb_bin_t`, medium-invisible. **The original regressed-state text retained below for history:**
  ~~⚠ STRUCTURALLY REGRESSED (found 2026-06-03 OPUS48 session 3; was [x]).~~
  The `bb_match.cpp` box NO LONGER EXISTS: it was stubbed to `x86_bomb` during TEMPLATE-REVAMP ("was offset-table",
  i.e. never converted off the abolished `bb_bin_t` form) and the stub was then deleted by STUB CLEANUP `cd10224`.
  `emit_core.c` has NO IR_PAT_MATCH / IR_SUBJECT dispatch arms (FILL emits nothing); `g_subject_slot` (emit_bb.c:118)
  is declared with ZERO consumers; `flat_drive_match`/`flat_drive_subject` survive in emit_bb.c. The probe suite was
  DARK (all 3 probes failed to COMPILE since the LI-2 `sno_*`→`gvar_*` rename — now repaired, SCRIP this commit) so
  nobody saw it: honest probe state is **1/3** (`probe_pb_rb_1_ref_invariant` PASS; both `_3_match*` die at
  `bb_emit_end: unresolved 'smatch%d_adv'` — the label only bb_match's body defined). **RESTORE = REG-0** (the
  watermark already says bb_match-α register establishment is the open REG-0): recreate per the pinned PB-RB-2 ABI
  + Model A on the RATIFIED registers (NOT the legacy Σ/Σlen-globals model the original used). Restore spec, from
  this session's vocabulary audit: (1) SUBJECT box writes Σ→`[r12+off]`, Δ→`[r12+off+8]` (driver pre-claims via
  `bb_slot_alloc16`, promotes off through a `_` field — the established op_sa/op_off promote-at-dispatch pattern);
  (2) bb_match head template α: `mov r13,[r12+Σoff]; mov r15,[r12+Σoff+8]`, claim start FR slot, `mov FR,0`, fall
  THROUGH to the element (elem_entry is defined immediately after the box — no jump vocabulary needed);
  (3) match_retry/match_advance are DRIVER labels wired with the sanctioned `EMIT_PAIR_JMP/DEF` glue; the advance
  ARITHMETIC (`start++; cmp start,Δ(r15); jg ω; kw_anchor jne ω; jmp retry`) is its own small dispatched template
  emitted after the element, sharing the driver-claimed start-slot offset; retry body `mov r14d,FR(start)` likewise
  (templates emit PORT records + FR/L(n) only — cross-box targets belong to the driver). Original PB-RB-3 landing
  text retained below for the ABI/probe detail; its gates/checkbox describe `706d665`, NOT the current tree.
  **Drafted x86() bodies + integration checklist + 2 VERIFY-FIRST items:
  `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORE-DESIGN.md`.**
  Inline-jump (Model A). `flat_drive_match` (emit_bb.c) resolves the element from `operand_aux[0]` (PEERS RULE) and
  inline-emits it via `walk_bb_flat(elem, lbl_γ, match_advance, elem_β)`. `bb_match.cpp` BINARY: α loads Σ/Σlen from
  SUBJECT's ζ-slot (`g_sno_subject_slot`) + re-establishes `r10=&Δ` + seeds start=0; `match_retry` sets `Δ=start, jmp
  elem_entry`; `match_advance` (element-ω target) is ch.18 step 6 (`start++; cmp start,Σlen; jg →ω; &kw_anchor jne
  →ω; jmp match_retry`); β=`jmp ω`. Box de-named per Lon (`bb_sno_match`→`bb_match`, `g_sno_match_*`→`g_match_*`).
  LEGACY SUBJECT MODEL deliberate (Σ/Σlen globals + cursor in Δ via `[r10]`, the cells `bb_lit` still reads) until
  the REG ladder migrates elements to R13/R14/R15. TEXT arm = `bomb_text` stub (PB-RB-8). v_scan NOT rewired (mode-2
  IR_SCAN intact → retire is PB-RB-CONV). Probes (`test/snobol4/pat_bb/`, in `test_sno_pat_bb_probe.sh`, 3/3):
  `probe_pb_rb_3_match` (happy path, `'b'` in `'abc'`, v=1) + `probe_pb_rb_3_match_fail` (whole-match-fail `'z'`→v=99;
  anchored-fail `&ANCHOR=1` suppresses the slide→v=99; unanchored control→v=1). Runtime contract (xa_flat_epilogue):
  v==1 SUCCEED / 99 FAIL. Gates: SNOBOL4 m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 12/12 HARD / m3 12/12 / m4 12/12,
  prove_lower2 65, sm_dead 0, concurrency OK, purity 7, g_vstack 0.
- [~] **PB-RB-4 — STITCH_SEQ / STITCH_ALT (the graph builders) — INVARIANT HALF ✅ PROBE-PROVEN (2026-06-03 OPUS48 session 4, SCRIP `f166940`+`c3d5547`): NO new STITCH machinery needed for the all-invariant case.** `probe_pb_rb_4_cat` (CAT('a','b') over 'aab': the right_ω→left_β inner backtrack, lit-β δ-undo, xcat_ω→match_advance, ch.18 slide) + `probe_pb_rb_4_alt` (ALT('q','b') over 'abc': within-position second-alternative, the ch.18 bead-diagram order) both pass through the restored bb_match via the EXISTING `flat_drive_cat`/`flat_drive_alt` pair-loop choreography — `IR_STITCH_SEQ`/`IR_STITCH_ALT` remain only for RUNTIME-variant wiring (pattern-valued vars, `*E`, Fork B). **⭐ CONV-SEAM DISCOVERY+FIX (`c3d5547`):** the LIVE lowerer's `wire_alt` carries arms in **operand_aux** (PEERS RULE) and never populates the legacy counter-held `bb_pat_kids_state_t` the flat driver read — a lowered ALT hit nkids==0 and emitted the DEGENERATE arm (no `jmp γ`, fall-through = SILENT WRONG), the exact seam PB-RB-CONV crosses. `flat_drive_alt` now falls back to `bb_operand_aux_get` when counter-kids are absent (legacy priority preserved; Icon IR_ALT routes elsewhere, untouched); `probe_pb_rb_conv_alt_lowered` builds the ALT byte-for-byte as wire_alt does and passes. **REMAINING:** (a) the lowered-CAT twin — `wire_seq` sets NO sidecar; gather arms in the DRIVER by the γ-chain walk `scan_pat_cat_concat` already proves; (b) runtime-variant STITCH boxes proper; (c) the m4 ALT/var-CAT TEXT path. Original step text retained: **TOPOLOGY PREREQ PROVEN (e39c329):**
  `prove_lower2.c` `MATCH('a' 'b')` (PATMAT + wire_seq(IR_PAT_CAT) + 2 PLIT = 4 nodes) and `MATCH('a'|'b')`
  (PATMAT + wire_alt(IR_PAT_ALT) + 2 PLIT = 4) — `lower2_match_entry` calls `lower2(cx,e,m,m,…)` under
  ROLE_PATTERN, which ALREADY handles TT_CAT/TT_ALT, so the lowering/topology layer EXISTS; the genuinely-new
  PB-RB-4 work is the emitter-side STITCH wiring + mode-3 drive, NOT the IR topology. Remaining: add
  `IR_STITCH_SEQ` / `IR_STITCH_ALT`
  (IR.h) + `bb_stitch_seq.cpp` / `bb_stitch_alt.cpp`: read two child heads from `ζ`-slots, wire their four
  ports (runtime twin of LOWER's `wire_seq`/`wire_alt` — SAME port equations), leave the combined head +
  `{entry,exit,fail}` descriptor in a `ζ`-slot. ε-merge boundaries (Fork D; reuse `bb_nfa.cpp`). Lower
  `TT_CAT`/`TT_ALT` pattern → REF_INVARIANT children + STITCH (all-invariant case still wires instances; the
  BLOB-freeze is PB-RB-OPT). Prove topology + mode-3 `S ('a' | 'b')` and `S 'a' 'b'`.
- [ ] **PB-RB-5 — operand-variant element matchers (Fork A).** `LEN(N)`/`SPAN(cvar)`/`ANY(expr)` etc.:
  the EXISTING `IR_PAT_LEN`/`IR_PAT_SPAN`/… matcher box reads its operand late from a `ζ`-slot (operand
  produced by a preceding value box, ref via `operand_aux`). NO builder box — operand-binding only. Prove +
  mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6 — BB_PAT_BUILD for STRUCTURAL variance (Fork A/B).** `*E` / `$NAME` / pattern-valued var:
  `IR_PAT_BUILD_*` boxes that SPLICE (wire ports) the runtime box-graph (a pattern-valued variable already
  holds a `bb_box_fn` graph — Fork B; `*E`/EVAL/CODE evaluate/compile first via the `tree_t` path) and stitch
  into the surrounding sealed pieces. Prove + mode-3 `P = 'x'; S P` and `S *E`.
- [ ] **PB-RB-7 — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5).** Replacement value-expr → REPLACEMENT
  BB (can fail). SUBSTITUTION BB: lvalue-check (fail for literal/number subject), splice
  `Σ[0:m_start]+repl+Σ[m_end:]`, assign back. mode-3 `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV — IR_SCAN convergence (retire the dual shape).** Once the native chain
  (SUBJECT→REF/BUILD/STITCH→MATCH) covers the corpus breadth, retire `IR_SCAN`: lower `TT_SCAN` to the native
  chain for ALL modes (mode-2 arm drives the same box-graph), removing the super-node + the dual shape. Gate:
  m2 corpus parity held; broad corpus ≥ prior.
- [~] **PB-RB-8 — mode-4 parity sweep. ✅ UNBLOCKED 2026-06-03 (SCRIP `2a146b2`): m4 0/6 → 3/6.** The
  `scrip.c:801` abort is GONE — replaced with the real flat TEXT emitter (mirrors the Prolog mode-4 block):
  header + `.text`; compile-time `rt_proc_register` per non-main proc (so `rt_proc_is_registered` fires the
  userproc arm when emitting main); each proc body via `gvar_flat_chain_build_text`; a `sno_proc_startup` GAS fn
  (runtime `rt_proc_reset`/`rt_proc_register`/`rt_proc_set_fn` with pnames rodata); the `main:` C stub
  (`rt_frame` → `sno_flat_α`); `xa_emit_strtab_rodata`. **Output/arith/define PASS end-to-end** (emit→as→gcc→run).
  Wiring fixes exposed (all mode-4-TEXT-only, mode-3 byte-neutral, gated on new `g_sno_m4_dense_nid`): (1)
  `g_flat_node_id` kept MONOTONIC across proc bodies in the TEXT path (per-body reset collided `snoch%d` labels in
  one asm file; mode-3 unaffected — each body is a separate sealed blob); (2) `bb_node_id` collision-free dense
  pointer→id under the flag; (3) `bb_fill_alpha` per-EMISSION-unique `bb%d_α` self-label (the int-assign's binop RHS
  is emitted twice — standalone chain node + inlined by the assign — which GAS rejects as a duplicate label though
  mode-3 tolerates it; output correct, assign reads the inlined slot); (4) `bb_gvar_assign` `dst/rhs_label` fall
  back to `strtab_label` (was `[rip + ??]`); (5) `bb_binop_gvar_arith` got a TEXT arm (strtab RO name ptrs, FRQ
  slot, `rt_gvar_arith@PLT`). MODE4_MIN raised 0→3. **REMAINING m4 gaps:** **concat** (`'ab' 'cd'`) — the
  `bb_gvar_assign` IR_SEQ arm bombs in TEXT because `rt_gvar_assign_concat` needs process-local subgraph `IR_graph_t*`
  ptrs; the right fix is COMPILE-TIME constant-folding of constant concats in the **driver (`emit_bb.c`
  flat_drive_gvar_assign) or lowerer (`v_seq_concat_pair`)**, NOT the template (the no-IR-walking-in-templates rule
  forbids reading `IR_t->t` there); folding matches SPITBOL Appendix-C item 11 ("constant sub-expressions
  pre-evaluated at compile time"). **pattern + goto_s** — need the IR_SCAN TEXT arm (the bigger native-pattern
  work below). Original concrete-entry-point note retained below for the seams it documents.
  **▶ CONCRETE ENTRY POINT (scoped 2026-06-03 OPUS48 — this IS the SNOBOL m4 unblocker, m4 0/6 → >0/6):** the
  abort is `src/driver/scrip.c:801`, inside `if (PLATFORM_X86)` mode-4, in the SNOBOL `{ … }` block that already
  computes `stage2_t *s2 = sm_preamble(ast_prog)` and `IR_graph_t *sbbg = s2->bbp.table[main_bb_idx]` (the
  four-port graph for `main`) — then `(void)sbbg; abort()`. **REUSE, don't invent:** the body emitter already
  exists — `gvar_flat_chain_build_text(IR_graph_t *g, FILE *out, const char *prefix)` (`emit_bb.c:2153`) emits
  the statement-chain BODY for an `IR_graph_t` (REF-prebuild + operand-refs + slot reset + `g_gvar_flat_chain=1`
  + `codegen_gvar_flat_chain_body` + `emitter_init_text`/`end`). It does NOT emit the header / per-proc
  prologue+epilogue / strtab — the wiring must add those, exactly as the **Prolog mode-4 block IMMEDIATELY ABOVE
  (scrip.c:~770-787) does for itself** (that block is the working template: emit a `main` C-entry stub →
  `codegen_flat_build(flat_root, stdout, "main")` under `g_frame_active=1` → `xa_emit_strtab_rodata()`). Recipe:
  (1) `xa_file_header()`; (2) emit the `main` C-entry stub that inits the SNOBOL runtime (mirror the Prolog stub
  + the SNOBOL `--run` init: `rt_proc_register`/`gvar_flat_chain_build`/`rt_proc_set_fn` per the define m3 path)
  and tail-calls `main_α`; (3) for the main proc AND each non-main proc in `s2->proc_table[]`: `xa_flat_prologue()`
  → `gvar_flat_chain_build_text(s2->bbp.table[proc.bb_idx], stdout, proc.name)` → `xa_flat_epilogue()`, with
  `g_frame_active=1` around proc bodies (the GZ-10 frame epilogue path — NOT the non-frame `[rip+Σ]/[r10]` path);
  (4) `xa_emit_strtab_rodata()`; (5) replace `abort()` with `return rc`. **Then the debug tail:** `--compile
  --target=x86` → `as` → `gcc -no-pie -lscrip_rt` → run; chase TEXT-arm assembly bugs box-by-box until the
  `scripts/test_smoke_snobol4.sh` mode-4 ladder climbs (raise `MODE4_MIN` as it does). ⚠ This is a STANDALONE
  RUNG with a real assembly-debug tail (the boxes' TEXT arms are claimed present but SNOBOL m4 is 0/6, so the
  pipeline has untested seams) — START IT FRESH; do not interleave with REG-RO. ⚠ The XA epilogue is SHARED with
  Icon — use the `g_frame_active=1` (frame) path, leave the non-frame path's bytes untouched so Icon m4 (already
  green) does not regress.
- [ ] **PB-RB-OPT — ALL-INVARIANT BLOB FREEZE (the optimization).** When a pattern is FULLY invariant,
  collapse its REF_INVARIANT + STITCH sequence into ONE sealed `bb_box_fn` BLOB emitted at compile time (the
  wiring frozen to direct jumps, no ε, no runtime stitch); REF_INVARIANT hands MATCH that sealed head
  directly. Variant patterns keep instance-level wiring. Gate: a fully-invariant pattern emits ONE sealed
  BLOB (verify `--dump`/disasm); native behavior unchanged (smoke ladder green). This is the MAX OPTIMIZATION
  — correctness (instance-wiring) first, freeze second.

---

### ⛔⛔ SESSION RUNG — BROKERED-MODE-ERADICATION (Lon directive 2026-06-01, Opus 4.8). THERE IS NO NEED FOR TWO WAYS TO ENTER A BOX.

**THE DIRECTIVE (Lon, verbatim intent):** "Any funky `int entry` MUST be gone. There is no need for two." A box is entered EXACTLY ONE way — a **jump to its α or β label**. The `(void *ζ, int entry)` **call-with-selector** is the second way, and the *existence* of two ways is the confusion. It is FORBIDDEN per the "NO C BYRD-BOX FUNCTIONS — JUMP TO α/β LABELS" FACT RULE at the top of this file. "Still compiles today" is NOT "needed" — propping the brokered path up to keep the build green is the exact green-build preservation that FACT RULE outlaws. **`bb_build_brokered` is NOT needed; it goes.**

**HONEST STATE (verified by grep 2026-06-01 — what `cc23c9f` did NOT finish).** The *driver* (`bb_broker.c`) and the C *functions* with the `(ζ,int entry)` signature were deleted. But the **emit-side brokered CALLING CONVENTION survives** and is the residue to eradicate:
- **`bb_build_brokered(IR_t*)`** (`emit_bb.c:~2196`, decl `emit_bb.h:13`) — emits a box with a `push rbp;mov rbp,rsp` brokered prologue (`0x55 0x48 0x89 0xE5`) in `EMIT_BINARY_BROKERED` mode, producing a `bb_box_fn` *called* with `(ζ,entry)`.
- **`EMIT_BINARY_BROKERED` (=2) + `g_bb_brokered` flag** (`emit_core.h:18`, `emit_core.c:18,30`) and the **`BB_BROKERED`/`BB_WIRED` macros** (`emit_core.h:55-56`) — **VERIFIED: the macros are read NOWHERE (pure dead weight).**
- **`BB_MODE_BROKERED`/`BB_MODE_DRIVER`/`BB_MODE_LIVE` + `bb_build_pure_mode`** (`emit_bb.c:~2230`; `g_bb_mode` set at `rt.c:201`, `stmt_exec.c:63`; branched at `stmt_exec.c:274,278,308,338`).
- **The actual `(ζ,int entry)` call convention lives in exactly TWO templates** — **`bb_capture.cpp`** and **`bb_arbno.cpp`** (`movabs rax, child_fn; edi=ζ; esi=entry(0=α/1=β); call rax; cmp eax,99`). These two boxes are the ONLY real reason `bb_build_brokered` still has live callers. (`bb_pat_defer.cpp` only ALIGNS for the brokered-child case in a comment + dynamic `and rsp,-16`; it calls `rt_defer_match@PLT`, NOT a child box — once the brokered-child context is gone, its alignment dance can simplify but it is not itself a brokered box. **`bb_ref_invariant.cpp` (PB-RB-1) is CLEAN** — it loads `child_fn` as a VALUE via `movabs`/`lea` and NEVER calls it.)
- The `stmt_exec.c:274-338` callers sit inside `exec_stmt`/`exec_stmt_blob` PATND paths that **already `abort()`** ("PATND->IR bridge removed"; `exec_stmt_blob` aborts outright at `:359`) — so those callers are dead-but-compiled.
- `bb_node_t {fn,ζ,ζ_size}` + the `bb_box_fn = DESCR_t(*)(void*,int)` typedef were KEPT by `cc23c9f` (the typedef slips past the FACT-RULE completion-test grep via `grep -v typedef`). The `int` param in the typedef is the last vestige of the selector; it goes too once no caller passes an entry.

**ORDER (FACT-RULE-sanctioned: convert the holdouts to jump-to-α/β FIRST, then delete the builder; a deliberately-broken build between rungs is acceptable, a surviving brokered box is not).** The STITCH_SEQ/STITCH_ALT graph-wiring of PB-RB-4 is what gives CAPTURE/ARBNO a jump-wired form to convert *to*; if BROK-1/BROK-2 are done before PB-RB-4 they must hand-wire the child inline (emit the child body in the same flat sequence, reach it by `jmp child_α`, take its γ/ω back by label) rather than `call child_fn`.

- [ ] **BROK-0 — dead-caller excision (free; no behavior).** Replace the `bb_build_brokered`/`bb_build_pure_mode` calls in `stmt_exec.c` (`:274,296,320,338`) — all inside already-`abort()`ing PATND/`exec_stmt_blob` paths — with the abort that already guards them (delete the now-unreachable `bb_box_fn bfn = …` lines). Delete the `BB_MODE_*` branch ladder (`:278,308`) and the `g_bb_mode` global (`rt.c:201`, `stmt_exec.c:63`) + `bb_build_pure_mode` (`emit_bb.c:~2230`, decl `emit_bb.h:14`) if no live caller remains. Gate: build rc=0; SNOBOL m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 11/11 HARD — byte-neutral (dead code only).
- [ ] **BROK-1 — convert CAPTURE (`bb_capture.cpp`) to jump-to-α/β.** The captured sub-pattern is reached by emitting its element inline and wiring `jmp child_α` (fresh) / `jmp child_β` (resume on backtrack), taking the child's γ (matched → run the capture-assign, then this box's γ) and ω (this box's ω) by LABEL — NO `movabs child_fn; call rax; cmp eax,99`. The saved-Δ slot + `rt_cap_assign_cursor`/`rt_cap_assign_*` assign stays (that is real capture work, not a box entry). Both ASSIGN_COND (`.`) and ASSIGN_IMM (`$`) arms. Stackless `[ζ=r12+off]`, no value stack. Gate: the capture corpus (cross / W07_capt_cur / 074) holds under `--run`; m2/m3 smoke invariant.
- [ ] **BROK-2 — convert ARBNO (`bb_arbno.cpp`) to jump-to-α/β.** ARBNO is a generator loop: α matches the null string (SPITBOL ch.18 — ARB/ARBNO start empty); each retry re-enters the child by `jmp child_α` and threads the child's γ back to ARBNO's γ, child's ω to ARBNO's ω/exhaustion — all by LABEL, no brokered call. Keep the `std::deque<int>` per-activation slot pattern (real per-iteration state, NOT a value stack). Gate: ARBNO corpus under `--run` holds; m2/m3 smoke invariant.
- [ ] **BROK-3 — delete the brokered machinery + add the gate.** Now that NO caller passes `(ζ,entry)`: delete `bb_build_brokered` (`emit_bb.c`, `emit_bb.h`), `EMIT_BINARY_BROKERED` (`emit_core.h:18`, the `emit_core.c:30` case + the `:2201/2206` mode toggles inside the deleted fn), `g_bb_brokered` (`emit_core.c:18`) and the dead `BB_BROKERED`/`BB_WIRED` macros (`emit_core.h:55-56`), and the brokered `push rbp;mov rbp,rsp` prologue. Drop the `int entry` param from the `bb_box_fn` typedef + `bb_node_t` if no surviving signature needs it (else note exactly what does and why). **ADD COMPLETION GATE** `scripts/test_gate_no_brokered.sh`: `grep -rn 'bb_build_brokered\|EMIT_BINARY_BROKERED\|g_bb_brokered\|BB_MODE_BROKERED\|BB_MODE_DRIVER' src/ == 0` AND `grep -rnE 'esi, *1.*call|movabs.*child_fn.*call' src/emitter/BB_templates/ == 0` (no box entered by call-with-selector) — wire it into the Session Setup gate list so it can never creep back. Gate: build rc=0; SNOBOL m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 11/11 HARD / m3 11/11 / m4 9/11; prove_lower2 64/64; concurrency OK; the FACT-RULE completion test (a) still 0 AND the new no-brokered gate green.

**COMPLETION TEST (rung):** `bb_build_brokered`/`EMIT_BINARY_BROKERED`/`g_bb_brokered`/`BB_MODE_BROKERED`/`BB_MODE_DRIVER` all grep to 0 in `src/`; no `bb_*.cpp` template enters a child box by `call` with an entry selector (every box reached by `jmp α`/`jmp β`); `test_gate_no_brokered.sh` green and in the Session Setup list; SNOBOL/Icon HARD gates survive. ONE way to enter a box, not two.

### DESIGN QUESTION (how PATTERN-builder BBs represent the pattern) — ✅ SUPERSEDED

Resolved by the CORRECTED PATTERN ARCHITECTURE at the top of this file: a SNOBOL4 pattern is a `bb_box_fn`
byrd-box GRAPH (emitted matcher boxes driven four-port), NOT a baked `tree_t` (which is for EVAL/CODE only —
those parse a runtime source string → `tree_t` → build boxes; a pattern's structure is known at compile time).
The invariant fast path is the all-invariant single-sealed-BLOB freeze (PB-RB-OPT), not a `tree_t` re-walk.
🏛 MEMORIAL: the AST node `tree(t, v, n, c)` (tag / value-union / arity / children) = `struct tree_t` in
`ast.h`, from Lon's `corpus/programs/snobol4/demo/beauty/beauty.sno` — the canonical shape the EVAL/CODE
runtime-codegen builder consumes.

### M3-NATIVE-5 (final)

Gate sweep + corpus, all langs. Honest failure for unbuilt opcodes.

**Mode-4 sibling (separate goal):** SBL-M4-FLATWIRE — `--compile` standalone brokers at runtime instead of flat-wiring at emit time. Defer until after M3-NATIVE done.

---

## Completed (summary) + Session State

**x86 TEXT+BINARY arms filled & `--run`-validated** for the SNOBOL4 pattern family (LIT/ARB/LEN/POS/RPOS/
TAB/RTAB/REM/ALT/CAT/FENCE/ABORT/EPS/FAIL/ANY/NOTANY/BREAK/SPAN/ARBNO/CAPTURE/DEFER). Runtime translators
`patnd_to_bb_graph` (γ-chain, mode-2) + `patnd_to_bb_tree` (tree-shape, mode-3). Infra: `cap_alloc_saved_delta_slot()`
deque-int pattern; `bomb_text`/`bomb_bytes`/`rt_bomb`; `emit_label_alloc()` session-stable label arena.
**Recovery:** original hand-written boxes at `git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`;
native-SM semantic spec at `git show 22a17fa3~1:src/processor/sm_jit_interp.c`.

**Done (structural):** LOWER-MERGE LM-1…LM-5 (four lowering files → one `src/lower/lower.c`); PND-1 (SNOBOL4
patterns lower `TT_*`→`IR_t` directly like Icon/Prolog).

**Open (ONE AST → ONE IR → ONE LOWER; Icon `lower_expr_threaded` is the canonical four-port model):**
- [ ] **LM-6 (DISPATCH-UNIFY)** — collapse lower.c's three dispatch entry points (`lower_expr_threaded` [Icon] /
  `lower_pl_goal` [Prolog] / `build_node` [SNOBOL4 pat]) into ONE `tree_e`-keyed dispatch. Do AFTER all lower2
  roles are armed + exec-proven.
- [ ] **BOX-ZERO** — cut byrd boxes against the register-allocation scheme (Icon STACKLESS ONE-REGISTER FRAME,
  `[reg+off]` per-sequence frame distinct from r10/r13; RO constants IP-relative; no value stack).

## Session log

Per-session detail (HEAD-by-HEAD writeups, gate logs, design deliberations) lives in the `.github/HANDOFF-*.md`
files and git history. Only the durable carry-forward + the current watermark are kept here.

**Watermark (gvar-concat TEXT arm; SCRIP **PUSHED on handoff**: origin/main = `2704f2e`, stack `fc10199`→`55ec228`→`2704f2e` rebased over `b6913ec` + `84ea1ca` and re-gated green twice; session detail: HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-CAPTURE-SCAN-NATIVE-CONCAT.md; 2026-06-04 OPUS48).** Non-constant value-concat assigns (`OUTPUT = A ' ' B ' ' C`) now **m4==m2** (goto-free micro-proof `ab cd ef`). Driver `gvar_seq_flatten` (left=`counter`, right=`ival`, nested SEQ recursed) → `g_emit.op_parts_{n,tag,str}[16]`; template stages n×{tag@FR, ptr@FRQ+8} in a `bb_slot_claim(16n)` ζ-region → new `rt_gvar_assign_concat_parts` (standalone-safe; lit verbatim, var NV-resolved + int coercion); un-flattenable keeps the bomb; BINARY byte-identical. **055 RECLASSIFIED → NEW NAMED BUG, the CHAIN-LABEL DRIFT:** with the concat body emitting correctly at **n7**, the scan's S-goto still targets **n5** — the goto-label REGISTRY and node EMISSION disagree by +2 on this shape; **disproven as bomb-induced** (the bomb-drags-label hypothesis from the prior watermark is retired); reproducer = 055; owner = the `codegen_gvar_flat_chain_body` label scheme, a separate rung. Gates: rung **M2 18 / M4 15** held · smoke **7/7 HARD / 6/6 / 6/6** ×2 · probes **8/8** · Icon **12/12 HARD** · broker 32 · REG-FENCE T1 strict 0 · no_bb_bin_t 0 · no-handencoded 0. **NEXT: (1) CHAIN-LABEL DRIFT** (registry-vs-emission, flips 055); (2) BROK-2 ARBNO (052/054); (3) REG-RO (r10=22). **— prior watermark below —**

**Watermark (m4 SCAN-NATIVE routing; SCRIP `b96972b` local, 2026-06-04 OPUS48, NOT pushed — no handoff phrase).** **Rung M4 1 → 15** (M2 18 HELD; 039–051 + 043–048 + 055-class minus blockers + 056 + 057 all flip). Mechanism per the frontier header (scan-native synth on pg with `g_emit_cfg` repoint; `bb_subject` VAR arm + `rt_subject_load_nv` setting Σ/Σlen; gather broadened + stop-node back-edge fence; capture α-hop to the wire_alt ALT; LOUD truncation guard; `??`-label sweep ×6 templates). **Two discoveries for the record:** (a) `wire_alt`'s **α_out is ARM0**, not the ALT — any consumer holding a lowered alternation in `->α` must hop `ch->γ` to the aux combinator (the capture hit this; the same trap awaits any future `->α`-held alternation consumer); (b) a **bombing statement drags its goto-label registration** — 055's YES (gvar-concat TEXT bomb) registers at n5 while the bomb body lands at n7, so the scan's S-goto mis-routes into the fail stmt; the drift is a side-effect of the bomb path and rides out with the concat arm. GDB-trace-proven: `rt_subject_load_nv("X")` + all three 055 captures fire with exact deltas (0–2/2–4/4–6) — 055's failure is purely the YES-statement gap. **Gates:** rung **M2 18/1 · M4 15/0/3-SKIP** · smoke m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (+`SCRIP_M3_NATIVE`) · pat-bb **8/8** · Icon m2 **12/12 HARD** (5/12 m3/m4 baseline) · Prolog 5/4/5 baseline · prove_lower2 PASS · no_bb_bin_t 0 · REG-FENCE TIER1 strict 0 (TIER2 **r10=22**) · no-handencoded strict 0 · medium-invisible: neither new arm listed · broker **32** · broad interp **152/280** (machinery untouched). **NEXT:** (1) gvar-concat TEXT arm → 055 + label-drift; (2) BROK-2 ARBNO → 052/054; (3) REG-RO. **— prior watermark below —**

**Watermark (CAPTURE BOXES flat-inline; SCRIP local commit, 2026-06-04 OPUS48, NOT pushed — no handoff phrase).** Pat-bb probes **7/7 → 8/8**. The named 17-rung unblocker landed: `flat_drive_capture` (emit_bb.c, after flat_drive_fence) replaces the brokered `child_cache_get` ASSIGN arms in `walk_bb_flat` — SAVE piece (`mov [r12+off], r14d`, driver-claimed `bb_slot_alloc16`, falls through) → child INLINE (`walk_bb_flat(ch, cap_γ, lbl_ω, lbl_β)`; construct-β ≡ child-β, generator children re-capture through cap_γ on each re-offer, exactly the oracle's non-fresh re-record) → CAP piece (`rt_cap_assign_cursor(varname, [r12+off], r14d, is_imm)` with the defer-style aligned @PLT/movabs call + push/pop r10 guard, `jmp γ`). ONE template `bb_pat_capture.cpp`, 3 sub-kinds on `op_ival` {0,1=COND,2=IMM}, varname free via `_.op_sval` (the node's sval), strtab_label TEXT fallback; dispatch `IR_PAT_ASSIGN_COND/IMM → bb_pat_capture` appended in the SNOBOL block; Makefile both sites. Prebuild: ASSIGN arms recurse-through (no more `bb_build_brokered` for capture children; ARBNO/CALLOUT arms byte-identical) — an ARBNO inside a capture still pre-builds. SEMANTICS GROUNDED (SPITBOL ch.13 + ch.18, manual re-read this session): COND assigns only on overall success, IMM at sub-match — BOTH satisfied by the existing `rt_cap_assign_cursor`/`g_rt_dcap_active` deferred path (scan driver flushes on success / discards per start-position; `rt_dcap_record` overwrites per-variable on retry = the `'A' ARB $ OUTPUT 'E'` re-offer sequence's net effect). Probe `probe_pb_rb_5_capture` (wired into the suite): COND(LIT 'b').V over 'abc' → NV[V]="b" AND IMM(lowered-ALT 'q'|'b')$W → NV[W]="b" — proves composition with the aux-arm `flat_drive_alt` path; probe sets Σ/Σlen as the scan driver would (g_rt_dcap_active=0 → direct NV_SET). Disasm-verified: SAVE@blob+0x5f, inline bb_lit child (β-undo intact), CAP@0xbf, stackless, zero `bb_bin_t`, zero `TEMPLATE_ADDR_SIG*`. **Gates:** pat-bb **8/8** · SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (plain + `SCRIP_M3_NATIVE`) · Icon m2 **12/12 HARD** (m3/m4 5/12 = known baseline) · prove_lower2 PASS · no_bb_bin_t 0 · no-handencoded `--strict` 0 · medium-invisible 343 with bb_pat_capture NOT listed (TEXT-only comments = the allowed carve-out) · REG-FENCE TIER1 `--strict` 0, **TIER2 r10 20→22** (the new CAP guard — REG-RO's job) · broker **32** (= watermark) · rung suite **M2 18/1 byte-identical, M4 1/17 unchanged AS PREDICTED** (the rungs bomb in `flat_drive_scan_stmt` routing BEFORE walk_bb_flat — captures are now ready underneath) · broad interp **152/280** (prior 113 watermark STALE again — intervening lanes; m2 machinery provably untouched by this diff: no IR_interp.c/lower.c/parser edits, smoke + rung-M2 byte-identical). **NEXT: (1) the m4 SCAN ROUTING slice** — `flat_drive_scan_stmt` synthesized SUBJECT/MATCH TEXT emission + var-subject `bb_subject` arm for capture-bearing patterns (with captures inline this flips the 17 `. V` rungs; the gather may need broadening past IR_PAT_LIT to walk ASSIGN/leaf γ-chains — the bare-CAT terminator stays the misfire guard); **(2) REG-RO + REG-FENCE TIER2** (now 22 refs / 8 files). **— prior watermark below —**

**Watermark (lowered-CAT gather + m4 var-subject scan; SCRIP `54ab640` PUSHED, 2026-06-04 OPUS48).** Two commits, pat-bb probes **6/6 → 7/7**, rung **M4 0 → 1**. **(1) `6ffbae3` PB-RB-CONV lowered-CAT γ-chain gather** (prior NEXT-1): `gather_lowered_cat_arms` (`emit_bb.c`) walks the γ-chain from MATCH's element (`c=c->γ` while `IR_PAT_LIT`, the proven `scan_pat_cat_concat` walk), accepting ≥2 lits terminating at a **bare** `IR_PAT_CAT` (nkids==0 — the wire_seq signature, unproducible by the legacy counter-kid encoding so the gather cannot misfire); `flat_drive_cat` refactored to arms-array mode (`flat_drive_cat_arms`, the exact `flat_drive_alt` aux-fallback shape from `c3d5547`) with a byte-equivalent legacy wrapper; `flat_drive_match` routes gather-hit → `flat_drive_cat_arms(catnd, arms, n, lbl_γ, match_adv, elem_β)`. **KEY ASYMMETRY vs the ALT probe:** `wire_seq` sets NO sidecar and `lower2_match_entry` hands MATCH **entry[0]** (the FIRST lit), NOT the combinator — so `probe_pb_rb_conv_cat_lowered.c` builds MATCH aux[0]=la, la.γ=lb, lb.γ=cat, counter zero, over 'aab' (right-fail → left-β δ-undo → ch.18 slide → match at start 1). Driver-only; `wire_seq` untouched (three-language lockstep). **(2) `54ab640` m4 var-subject scan** (prior NEXT-2, first leg): the 038-class m4 bombs were a **LOWERER omission, not an emitter gap** — `v_scan`'s no-repl branch never set `sc->sval`, so `scan_has_name()` was false for every goto-style scan (`X PAT :S/:F`) and the TEXT arm bombed "non-literal subject" even with a single-lit pattern (why the m4 smoke `pattern` — var subject WITH repl — passed while 038 bombed). ONE LINE (`lower.c`): no-repl branch sets `sc->sval` for a TT_VAR subject; `rt_scan_lit` already NV-resolves name + no-repl. Neutrality proven: m2 reads sval only when is_repl (`IR_interp.c:2812`); m3 `rt_scan` ignores subj_name when the subj graph is present (`:206`, always in no-repl). **DISCOVERIES (re-scope the m4 ladder): (a) the dense-nid duplicate-`bb%d_α` hazard is ALREADY SOLVED** — `bb_fill_alpha` (`emit_bb.c:233`) allocs a FRESH `bb%d_α` from `++g_bb_alpha_seq` per FILL under `g_sno_m4_dense_nid`, so bb_match's 3 emissions are TEXT-safe by construction; **(b) CAPTURE BOXES are the real m4 rung unblocker** — rung inventory: **17/18 remaining rungs carry `. V`** (only 057 `'abc' FAIL` is capture-free) and flat-chain captures still ride the brokered `child_cache_get` path (`walk_bb_flat` IR_PAT_ASSIGN_IMM/COND), so the var-subject `bb_subject` arm + `flat_drive_scan_stmt` TEXT routing alone would flip ONLY 057. **Gates (re-run green after EACH commit):** pat-bb **7/7** · SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (plain + `SCRIP_M3_NATIVE`) · rung M2 **18/1** / M4 **1/17** (038 flips; 053 pre-existing) · Icon m2 **12/12 HARD** · broker 32 · prove_lower2 PASS · no_bb_bin_t 0 · REG-FENCE TIER1 strict 0 (TIER2 r10=20 unchanged) · native-arms OK · LI-FENCE stash-Δ0 ×2. **PUSHED on handoff: SCRIP `54ab640` → origin/main (fast-forward `b1a54a0..54ab640`); .github this commit.** **NEXT (re-pointed after the inventory): (1) capture boxes in the flat chain — de-broker IR_PAT_ASSIGN_IMM/COND to flat-inline emission (BINARY first, TEXT with it; COND assigns on overall match, IMM on sub-match success — SPITBOL ch.13/18) — the 17-rung unblocker; (2) the 057-slice TEXT routing — var-subject `bb_subject` arm (NV read → Σ/Δ ζ-slot) + synthesized SUBJECT/MATCH TEXT emission in `flat_drive_scan_stmt` (zero-capture/zero-repl guard), WITH or AFTER (1); (3) REG-RO + REG-FENCE TIER2 (unchanged).** Session detail: `HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-CAT-LOWERED-GATHER-M4-VAR-SUBJECT.md`. **— prior watermark below —**

**Watermark (PB-RB-3 RESTORED + REG-0 + PB-RB-4 invariant + CONV-ALT seam; SCRIP `c3d5547` PUSHED, 2026-06-03 OPUS48 session 4).** Three commits, pat-bb probes **1/3 → 6/6**. **(1) `8cd05c1` PB-RB-3 RESTORE + REG-0** per the RESTORE design doc, on the RATIFIED registers: ONE `bb_match.cpp` (3 emissions on `op_ival`: HEAD Σ←r13/Δ←r15d from SUBJECT ζ-slot + start=0 + `lea r10,[r12+start+8]` ζ-scratch; RETRY δ=r14d←start fall-through; ADVANCE ch.18 step-6) + `bb_subject.cpp` + 3-piece port-remapped `flat_drive_match` + `g_subject_slot` un-orphaned + 2 additive `x86_asm.h` encoders (`x86_load_mem64`, `lea→x86_frame_lea`). Both VERIFY-FIRST items confirmed (FRQ = REX.W+R+B, `4D 8B 2C 24` disasm-proven; FILL resets fully per emission, BINARY α record-free). **KEY r10 DISCOVERY the design doc missed:** REG-1 `bb_lit` still writes the `[r10]` cursor-mirror — with r10 unestablished the chain SEGVs; fixed frame-cleanly (HEAD points r10 at MATCH's own ζ-scratch dword; the Icon-shared `xa_flat` FRAME-path epilogue verified `[r10]`-free, so harmless until REG-RO deletes the mirror — no global cell, m4-relocatable). **(2) `f166940` PB-RB-4 invariant ALT/CAT probe-proven, zero emitter delta:** `probe_pb_rb_4_cat` (right_ω→left_β inner backtrack + lit-β δ-undo + ch.18 slide on 'aab') + `probe_pb_rb_4_alt` (within-position second alternative, bead-diagram order) — the all-invariant case needs NO STITCH machinery; STITCH stays runtime-variant-only (Fork B). **(3) `c3d5547` CONV-SEAM:** `wire_alt` carries arms in operand_aux (PEERS RULE), the flat driver read only legacy counter-kids → a LOWERED ALT emitted the degenerate no-`jmp γ` arm SILENT-WRONG; `flat_drive_alt` now aux-falls-back (legacy priority kept, Icon IR_ALT route untouched); `probe_pb_rb_conv_alt_lowered` builds the exact wire_alt shape and passes — the native chain drives REAL lower2 output. **Gates (re-run green on the rebased tree over upstream `f9677cc` ICN-SCAN-5, zero conflict):** pat-bb **6/6**; SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** (plain + `SCRIP_M3_NATIVE`); Icon m2 **12/12 HARD**; prove_lower2 **67**; no_bb_bin_t 0; REG-FENCE TIER1 strict 0 (TIER2 r10=20 unchanged — the bb_match `lea` is outside the family grep); no-handencoded strict 0; medium-invisible 343 with NEITHER new box listed; no_vstack 3 baseline; broker 32; rung suite byte-identical (M2 18/1, M4 0/18). **PUSHED on handoff: SCRIP `c3d5547` → origin/main; .github this commit.** **NEXT: (1) lowered-CAT γ-chain gather in the driver (wire_seq sets no sidecar; the `scan_pat_cat_concat` walk is the proven collect) → (2) m4 ALT/var-CAT TEXT path (compound-pattern scan currently LOUD-bombs; bb_match/bb_subject TEXT arms exist via x86(), the tail is the m4 dense-nid label discipline + var-subject arm) → (3) REG-RO + REG-FENCE TIER2 — the probe suite now gates the flat chain, lifting half the deferral; the other half (PB-RB-CONV making it the real m3 driver) advances with (1).** Session detail: `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORED-PBRB4-INVARIANT-CONV-ALT.md`. **— prior watermark below —**

**Watermark (m4 scan subj/repl LOUD guards + PB-RB-3 regression + RESTORE design; SCRIP `c4da0b1` PUSHED, 2026-06-03 OPUS48 session 3).** Three legs. **(1) `f406239`:** the prior handoff's flagged-UNVERIFIED hole closed — FIVE m4 scan SILENT-WRONGs (var/var-concat/lit-leading-concat REPLACEMENT silently DELETED because repl=NULL ≡ deletion; compound SUBJECT ×2 silently failed the match) → LOUD bombs naming PB-RB. `scan_val_is_single_lit()` (sentinels + exactly one IR_LIT_S) replaces both entry-only checks in `flat_drive_scan_stmt`; 2 TEXT-arm guards in `bb_scan_stmt.cpp`. Probe ground truth: value graphs carry the combinator (IR_SEQ) at ENTRY; legit deletion lowers as `IR_LIT_S ""` so the NULL-repl path is NEVER legitimate. m2/m3 untouched. **(2) `c4da0b1`:** pat-bb probe suite was DARK since LI-2 (link failure on the `sno_*`→`gvar_*` rename, wired into no gate); sweep landed; honest state **1/3** — both `_3_match` probes die at `bb_emit_end: unresolved smatch%d_adv` because **`bb_match.cpp` NO LONGER EXISTS** (TEMPLATE-REVAMP bomb-stub deleted by STUB CLEANUP `cd10224`; no IR_PAT_MATCH/IR_SUBJECT dispatch arms; `g_subject_slot` orphaned). **PB-RB-3 flipped `[x]`→`[~]` STRUCTURALLY REGRESSED** at the checkbox. **(3) design-only:** original bb_match RECOVERED (`git show 706d665:…`, byte-level doc intact); RESTORE designed on the ratified registers (= **REG-0**): ONE template, THREE emissions per node (`op_ival` sub-kind), ports REMAPPED per FILL (advance-γ→match_retry; retry falls through into the inline element — no elem_entry label), start slot driver-claimed/shared via `op_off`; bb_subject → ζ-slots. Drafted bodies + integration checklist + 2 VERIFY-FIRST items (FRQ qword form / FILL multi-emission) in `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-PBRB3-RESTORE-DESIGN.md`. Gates (final tree, rebased over ICN-SCAN-0 `f13838f` + `0604ae5`, rebuilt + re-gated): SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6**; Icon m2 **12/12 HARD**; prove_lower2 **67**; no_bb_bin_t 0; LANG-NAMES 17 stash-Δ0; concurrency OK; REG-FENCE TIER1=0; no-handencoded `--strict` 0; broker 32; pat-bb 1/3 honest. **NEXT: PB-RB-3-RESTORE per the design doc (VERIFY-FIRST items first) → probes 3/3 → flip PB-RB-3 + REG-0 → PB-RB-4 ALT/CAT probes (flat_drive_alt/cat verified present + port-correct; invariant case likely needs NO new STITCH machinery) → then REG-RO + REG-FENCE TIER2.** Session detail: `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-SCAN-GUARDS-PBRB3-REGRESSION.md`. **— prior watermark below —**

**Watermark (m2 builtin-registry fall-through; SCRIP `715daa5` PUSHED, 2026-06-03 OPUS48 session 2).**
**ROOT CAUSE FOUND for the broad-corpus 251→105 collapse:** the m2 `IR_CALL` dval==2.0 dispatch (`IR_interp.c`)
went user-proc → `try_call_builtin_by_name` → fail-to-ω and NEVER consulted the `register_fn` FNCBLK registry —
so the ENTIRE SNOBOL4 builtin library (IDENT, DIFFER, REPLACE, CONVERT, TABLE, ARRAY, SORT, TRIM, DUPL, LPAD,
EVAL, CODE, …) was unreachable in m2 since SMX-4 deleted the SM path that reached it via `INVOKE_fn`/`APPLY_fn`.
FIX (+5 lines, ONE hunk, SNOBOL dval==2.0 arm only): on try_call miss, probe `FNCEX_fn(bb->sval)` and call
`APPLY_fn` ONLY on a registry hit — old proven semantics for registered names, current ω-fail preserved for
unknowns (oracle ERROR 022 on undefined fns deliberately out of scope; Raku `__rk_jct_*` registry-absent →
untouched). Oracle-matched probes: IDENT/DIFFER goto+predicate-concat, 1+2-arg, top-level + inside DEFINE bodies;
`G('AB')`→`ABAB`. **Gates (all stash-compared where counts moved):** smoke m2 **7/7 HARD** / m3 **6/6** / m4
**6/6** (plain + `SCRIP_M3_NATIVE=1`); broker 32; prove_lower2 67; no_bb_bin_t 0; REG-FENCE TIER1=0; native-arms
audit OK; pat rung suite **byte-identical to clean tree** (M2 18 / FAIL 053_pat_alt_commit BOTH sides; M4 0/18
BOTH sides — the Session-Setup `M2=19 M4=15` comment is STALE, same class as the 251/280). Broad interp 105→**104**:
the single flip is `136_pat_balanced_parens_deep`, which PASSED BY ACCIDENT (DUPL+LEN both silently failed →
null subject → vacuous `POS(0) RPOS(0)` match); with DUPL/LEN now executing it fails HONESTLY on the genuine
blocker — **ROLE_VALUE lowering of TT_LEN(=33)/TT_FENCE(=39) is `lower_unhandled`** (DT_P pattern-construction
in value position, e.g. `eps = LEN(0)`, `B = '(' FENCE(*B|eps) ')'` — the corrected-pattern-architecture/`DT_P`
track owns this). ZERO FAIL→PASS gains confirms the 175 baseline failures are multi-bug: the registry was a
NECESSARY unblock, not sufficient — expect compound gains as the value-role pattern arms land. **ALSO THIS
SESSION (goal-file reconciliation):** slen note struck RESOLVED-STALE (DT_S+slen=0 IS canonical `STRVAL`;
`descr_slen` strlen-fallback; only DT_N is a name); REG-3/REG-4/REG-5 flipped `[x]` with per-box audit evidence
(pos/tab/atp/fence/arb/defer all on r13/r14/r15 + ζ-slots; cat/alt pure `x86_pair_loop` wiring; arbno/capture
files deleted by STUB CLEANUP). **REG-0 stays `[ ]`:** `bb_match` α is still the deliberate LEGACY subject model
(per PB-RB-3 note) — the BB_MATCH-α register establishment (R13←Σ-slot, R15←Δ-slot, xor r14) is genuinely open.
**PUSHED on handoff: SCRIP `715daa5` → origin/main (no upstream movement, no rebase delta); .github this commit.** **NEXT unchanged: REG-RO +
REG-FENCE TIER2; PB-RB-4 STITCH for m4 ALT/var-CAT; NEW named rung candidate: ROLE_VALUE TT_LEN/TT_FENCE arms
(unlocks 136 + pattern-valued-variable corpus).** **— prior watermark below —**

**Watermark (m4 scan single-lit guard + bomb TEXT label + constant-CAT fold; SCRIP `9e8e4b8` pushed, 2026-06-03 OPUS48).** Three layered fixes in the m4 scan fast-path, found by probing past the smoke (single-literal-only): **(1) compound patterns were SILENT-WRONG in m4** — `flat_drive_scan_stmt` classified any pattern whose graph `entry` is `IR_PAT_LIT` as a single literal, but for CAT/ALT the entry IS the first child literal, so `rt_scan_lit` matched only the first element (`S 'a' 'b'='Q'` on `xabz` → `xQbz`; `S ('q'|'b')='Q'` on `abc` → unmatched `abc`). m2/m3 never affected (m2 = IR_interp; the BINARY arm always drives the full graph via `rt_scan`). FIX `scan_pat_is_single_lit()`: only {IR_SUCCEED/IR_FAIL sentinels + exactly ONE IR_PAT_LIT} qualifies. **(2) Surfaced latent, ALL languages: every m4-TEXT `x86_bomb` was unassemblable** — emitted `lea rdi,[rip + ??]` because `emit_intern_str` ALWAYS returns NULL (`g_flat_intern_str`/`lower_flat_set_intern_str` is defined but wired NOWHERE; the scan template's own strings only ever resolved via `scan_lbl`'s `strtab_label` fallback). FIX: TEXT-only `strtab_label` fallback in `x86_bomb` (`x86_asm.h`, +2, BINARY ignores `label` in `x86_load_ro` → mode-3 bytes unchanged); bombs now print `BOMB — <msg>` + `ud2` (rc=134) — "falls LOUD never silent" restored for all languages' m4 bombs. **(3) Constant-CAT fold (PB-RB-OPT subset / manual Appendix-C item 11):** `scan_pat_cat_concat()` folds a PURE literal CAT (all[] = sentinels + ≥2 LIT + ≥1 CAT, NOTHING else — ALT/captures/operand matchers rejected) by concatenating svals along the γ-chain from entry (probe-verified order `LIT(a)→LIT(b)→[LIT(c)→]CAT→SUCCEED`) into a `GC_MALLOC_ATOMIC` buffer for `op_scan_pat_lit`; `S 'a' 'b'='Q'` and the 3-literal CAT now PASS m2==m3==m4. Fold lives in the EMIT DRIVER deliberately — a lowerer fold would shrink node counts and break `prove_lower2`'s `MATCH('a' 'b')` 4-node topology assertion. `rt_scan_lit` multi-char pre-verified (`S 'ab'='Q'` already m4-green). ALT + variable/captured CAT now LOUD-bomb in m4 naming PB-RB — the genuine **PB-RB-4** frontier. Files: `emit_bb.c` (+`<gc/gc.h>`, 2 helpers, guard+fold), `x86_asm.h` (+2 additive). Probe enum ground truth: IR_FAIL=11, IR_SUCCEED=12, IR_PAT_LIT=32, IR_PAT_CAT=38, IR_PAT_ALT=39. ⚠ FLAGGED OPEN: compound SUBJECT/REPLACEMENT beside a literal pattern (`S 'b' = (A B)`) — subj/replace classification is still entry-only (`IR_LIT_S`); compound replacement leaves `op_scan_replace_lit` NULL with `is_repl=1` → `rt_scan_lit(repl=NULL)` UNVERIFIED; likely needs the same guard. Gates (re-run green on rebased tree after mid-handoff upstream `1d92abc` Pascal + `873792f` Prolog float-unify, zero conflict): SNOBOL4 m2 **7/7 HARD** / m3 **6/6** / m4 **6/6**; Icon m2 **12/12 HARD**; prove_lower2 **67/0**; no_bb_bin_t 0; LI-FENCE **13 (Δ0)**; concurrency OK; REG-FENCE TIER1=0 (TIER2 r10=20 info unchanged); no-handencoded `--strict` 0; unified-broker **32**. **NEXT unchanged: REG-RO + REG-FENCE TIER2 — and PB-RB-4 STITCH is now the named, loud blocker for m4 ALT/var-CAT.** Detail: `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-M4-SCAN-GUARD-BOMB-LABEL-CAT-FOLD.md`. **— prior watermark below —**

**Watermark (m4 IR_SCAN TEXT arm — `pattern` + `goto_s`, SCRIP `faea0f4` pushed, 2026-06-03).** m4 4/6 → **6/6**: `S 'b'='X'`→`aXc` (`pattern`) and `'x' 'x' :S(HIT)`→`hit` (`goto_s`) now pass m2/m3/m4. Both smoke cases are the SIMPLE-LITERAL scan (pattern `IR_PAT_LIT`, subject `IR_VAR` or `IR_LIT_S`, replacement `IR_LIT_S`/absent — emit-time probe confirmed). NEW runtime entry `rt_scan_lit(subj_name, subj_lit, pat_lit, is_repl, repl_lit)` in `IR_interp.c`: unanchored `memcmp` honoring `kw_anchor` (manual ch.18 OUTER loop) + ch.14 prefix/replacement/suffix splice on match (only the matched portion replaced); no IR-graph run, so no Σ/Δ save. `emit_bb.c flat_drive_scan_stmt` reads the literal strings off the scan sub-graph ENTRY nodes (emit-time IR inspection in the DRIVER, not the template) and promotes them onto 3 new `_` fields (`op_scan_pat_lit/subj_lit/replace_lit`); `bb_scan_stmt.cpp` TEXT arm emits the call with `[rip+label]` RO-string args (`mov reg,0` for absent), `is_repl` imm, then `test eax,eax / je ω / jmp γ / def β / jmp ω`. Non-literal patterns still honestly `x86_bomb` (the separate native PB-RB pattern ladder). BINARY (mode-3) arm UNTOUCHED — parallels the concat fix (handle the constant case, keep the general path). **LI-FENCE gotcha:** the field, first named `op_scan_repl_lit`, tripped the gate's Prolog `pl_` tag inside `re`**`pl_`**`it` (false positive — concept is "replacement", not Prolog); renamed `op_scan_replace_lit` (`pl`→`a`), my LI-FENCE delta back to 0. (Aside: `BB_templates/` is incidentally outside LI-FENCE because the ALLOW token `template` matches the dir name, but the field name lives in-scope in `emit_bb.c`/`emit_globals.h`.) Files: `emit_globals.h`, `emit_bb.c`, `IR_interp.c`, `BB_templates/bb_scan_stmt.cpp` (4 files). Gates (re-run GREEN post-rebase): m2 **7/7 HARD** / m3 **6/6** / m4 **6/6**; unified-broker 32; native-arms audit OK; REG-FENCE TIER1=0; SCRIP_M3_NATIVE 19/0; no-bb-bin-t 0; medium-invisible (bb_scan_stmt absent); no-vstack 3 (baseline); no-handencoded-bytes 0; LI-FENCE **13** (this work's delta 0 — the +6 vs the prior 7 are the rebased-in upstream Icon GN commit `c66723e`: `g_icn_globals_nv` / `bb_gvar_assign_icn` / `flat_drive_icn_global_assign`). SNOBOL gates count-identical vs `047dded`; rebased onto upstream `c66723e` (Icon GN, m4 12→19) + `bfabff3` (Prolog) with no conflict. MODE4_MIN left at 4 (6/6 ≥ floor). **Committed + pushed: SCRIP `faea0f4` (rebased onto `c66723e`).** **NEXT:** REG-RO + REG-FENCE TIER2. **— prior watermark below —**

**Watermark (define-body RETURN double-execution fix, `591ed37`, 2026-06-03, LOCAL ONLY — no handoff phrase given).** A
function body's FINAL statement (the one carrying `:(RETURN)`/`:(FRETURN)`) executed TWICE in m3 AND m4. Root cause: the
SNOBOL goto-RETURN IR nodes (`lower_program.c:465`, `RET dval=1.0` / `FRET dval=2.0`, **`α=NULL` by design** — SNOBOL
RETURN has no expression; the value lives in the NV store) fell through `gvar_chain_arity` to the shared
`descr_chain_arity`, whose `IR_RETURN → 1` is the Icon/Pascal `return expr` convention; `gvar_stmt_operand_refs` (the
RPN operand-promotion pass) then CLOBBERED `RET->α` with the body's final statement node, and `flat_drive_return`
re-walked that α as a "return expression" — emitting+executing the statement a second time. The define smoke
(`DOUBLE = X + X`) is idempotent, so m3 6/6 never caught it; an OUTPUT-in-body probe does (`a b c c done`). FIX = one
line in `gvar_chain_arity`: `IR_RETURN && (dval==1.0 || dval==2.0) → arity 0` — keyed on the SNOBOL goto-RETURN
markers, structurally proven the ONLY dval-1.0/2.0 IR_RETURN creators are `lower_program.c:465/466` (Icon `lower.c:872`
and Pascal `lower_program.c:228` are dval=0.0 and keep arity 1, byte-identical). Probes (all == SPITBOL oracle, all
three modes): 3-stmt OUTPUT body, `N=N+1` invocation-vs-output discriminator, FRETURN twin (`:S/F` goto honored),
string-arg `G('AB')` → `got:AB` — NOTE the old "slen → empty string-arg" symptom from the SR-1a handoff does NOT
reproduce at tip; string args arrive correctly via the staged path, so that open item is RETIRED pending a counter-case.
ALSO RETIRED: the scan-guard handoff's open item 2 (compound SUBJECT/REPLACEMENT silent-wrong) — already landed as
`f406239` (whole-graph `scan_val_is_single_lit` + TEXT-arm bombs), verified behaviorally (m4 bombs LOUD on
`'got:' X` concat). **Stash-proven vs clean tree `40ec5bc`:** broad interp **112 → 113 (+1, zero regressions)** — the
old 105 watermark was STALE (intervening lanes moved it); SNOBOL m2 **7/7 HARD** / m3 **6/6** / m4 **6/6**; Icon m2
**12/12 HARD** (m3/m4 5/12 unchanged); Prolog smoke m2 5/5 / m3 4/5 / m4 5/5 unchanged; broker 32; prove_lower2 67;
no_bb_bin_t 0; concurrency OK; REG-FENCE TIER1=0 (TIER2 r10=20 info unchanged). **Pascal m3 nested-fn segv observed
during regression sweep is PRE-EXISTING** (clean-tree baseline rc=139 identical, stash-proven) — belongs to
GOAL-PASCAL-BB, flagged there-ward, not touched. Diff = `src/emitter/emit_bb.c` +1 line. PUSHED on handoff as **`591ed37`** (rebased onto upstream `5091102`
ICN-SCAN-2; rebuilt + re-gated green on the rebased tree: SNOBOL m2 7/7 HARD / m3 6/6 / m4 6/6, Icon m2 12/12 HARD,
prove_lower2 67, REG-FENCE TIER1=0, probes re-verified). **FOLLOW-UP PROBES (same session, post-commit):** conditional **`:S(RETURN)`** AND
**`:F(RETURN)`** from mid-body both verified m2==m3==oracle (the label-registry path to the RET node — all THREE
RETURN-goto flavors now proven). **RECURSIVE DEFINE is GREEN in m3** — `R(S)` 4 activations deep matches the oracle
exactly (incl. the null-string OUTPUT line): the `rt_name_save_push`/`rt_name_restore` LIFO is recursion-proven across
nested activations (the SR-2 prerequisite data point), VAR-arg recursive call shape is supported, and
pattern-match-with-replacement on a PARAM works in m3. **NEW M3 GAP (LOUD, correct failure mode):** the numeric
predicate builtins **GT/LE** (manual ch.4 conditional functions) have NO bb_call arm — `[IBB] FATAL bb_call:
unsupported call shape fn='GT' narg=2 a0=-1`; blocks any predicate-conditioned define body in m3 (FACT(5) untestable
until it lands); next-session candidate alongside PB-RB-4. **— prior watermark below —**

**Watermark (m4 unblock 0→3, `2a146b2`).** SCRIP tip **`2a146b2`** (2026-06-03) — **SNOBOL4 mode-4 UNBLOCKED: m4 0/6 → 3/6.** This session
wired the dead `scrip.c:801` abort to the real flat TEXT emitter (`gvar_flat_chain_build_text`), mirroring the
Prolog mode-4 block, plus 5 mode-4-TEXT-only wiring fixes (all gated on the new `g_sno_m4_dense_nid` / TEXT path,
mode-3 byte-neutral — see the PB-RB-8 step above for the full list). `output`/`arith`/`define` now PASS
emit→as→gcc→run. Files: `src/driver/scrip.c`, `src/emitter/emit_bb.c`, `src/emitter/emit_core.c`,
`src/emitter/BB_templates/bb_gvar_assign.cpp`, `src/emitter/BB_templates/bb_binop_gvar_arith.cpp`,
`scripts/test_smoke_snobol4.sh` (MODE4_MIN 0→3). **Verified non-regression by stash-compare:** broad interp
**105/280** and unified-broker **32** are IDENTICAL on the clean tree (the goal's old "251/280" GATE-4 number is a
STALE watermark, not a regression — confirmed by `git stash` + rebuild + re-run). Gates: SNOBOL m2 **7/7 HARD** /
m3 **6/6** / m4 **3/6**; `prove_lower2` PASS; REG-FENCE TIER1=0. **NEXT:** m4 `concat` (constant-fold in
driver/lowerer, NOT the template) → m4 `pattern`/`goto_s` (IR_SCAN TEXT arm) → then REG-RO + REG-FENCE TIER2.
NOT pushed (no handoff phrase given); committed locally only. **— prior watermark below —**

**Watermark (concat follow-up, SCRIP `047dded`, 2026-06-03).** m4 3/6 → **4/6**: `OUTPUT = 'ab' 'cd'` now passes
m2/m3/m4. Fix is in the LOWERER (`v_seq_concat_pair`, `lower.c`), the correct layer per the no-IR-walking-in-templates
rule: a fully-constant string concat (TT_QLIT + nested TT_SEQ of QLIT) folds to one IR_LIT_S via `GC_strdup` — exactly
SPITBOL Appendix-C item 11 (constant sub-expressions pre-evaluated at compile time). Non-constant concat keeps the
IR_SEQ path. SNOBOL-only. MODE4_MIN 3→4. Stash-verified no regression (broad interp 105/280, unified-broker 32,
prove_lower2 PASS all unchanged). **Remaining m4: `pattern` + `goto_s` — the IR_SCAN TEXT arm** (the bb_scan_stmt
TEXT path + native-pattern PB-RB work; `S 'b' = 'X'` and goto-on-match).

**Watermark (prior).** SCRIP tip **`341b59f`** (this session committed ONE file: `scripts/test_gate_sno_pat_reg.sh`,
the REG-FENCE gate — test-only, no emitter/runtime bytes; rebased onto the RUNTIME-REORG lane's `5893518`
RS-2-s27 move-only extraction. Last SNOBOL4-BB *code* commit remains **SR-1a** `3610475`; intervening commits are
other lanes — GN-3, RS-2, PB-8, WAM-CP-7c, etc.). **This session (2026-06-03 OPUS48) landed NO code — it
RECONCILED this goal file** after confirming via git history (`bd8d6453`) + handoff that **SR-1b's box approach
was REJECTED** and reverted (save/restore stays fused in `rt_call_named_proc` via the SR-1a helpers
`rt_name_save_push` / `rt_name_restore`). Edits made: frontier header re-pointed; SR-1b WALK-BACK note added at
top; SR-1b bullet struck through; **REG-1 flipped to [x]** (was done-but-unchecked — `bb_lit` is on Σ=r13/δ=r14/
Δ=r15, zero `TEMPLATE_ADDR_SIG*`); REG-LADDER + m4 reconciliation note added. **Audited baseline (grep + gate,
clean tree):** SNOBOL4 m2 **7/7 HARD** / m3 **6/6** (`DOUBLE(21)`→`42`) / m4 0/6; `TEMPLATE_ADDR_SIG*` ZERO
family-wide; `r10` residue is **20 refs / 7 files** (`bb_lit`, `bb_pat_atp`, `bb_pat_break`, `bb_pat_any`,
`bb_pat_notany`, `bb_pat_span`, `bb_pat_defer` — push/pop guards + bb_lit mirror); `prove_lower2` / `no_bb_bin_t` /
LI-FENCE / concurrency all PASS. **CORRECTED m4 cause:** m4 0/6 is NOT the address bake (gone) — `--compile`
aborts at `src/driver/scrip.c:801` with *"sno_ring_to_tree REMOVED … mode-4 emission must come from LOWER
producing the four-port statement-BB graph directly … wiring gap"* (the abort site ALREADY holds `sbbg`, the
four-port `IR_graph_t` for `main`). **ALSO THIS SESSION (safe, test-only):** authored `scripts/test_gate_sno_pat_reg.sh`
(REG-FENCE) — TIER 1 `TEMPLATE_ADDR_SIG*`==0 HARD (locked, passes `--strict`), TIER 2 r10 informational; added to
the goal's Session Setup gate list; REG-FENCE bullet marked `[~]`. **NEXT (re-pointed after audit):** **(1) the
real m4 unblocker — LOWER four-port wiring** at `scrip.c:801`: walk `sbbg` through the flat TEXT emitter (mode-4
twin of mode-3 `bb_build_flat`/`codegen_flat_*`, SAME boxes TEXT-vs-BINARY) instead of `(void)sbbg`-aborting; real
test delta (m4 0/6 → >0/6). **(2) REG-RO — DEFERRED behind (1)**: it is broad (7 files + the Icon-SHARED `xa_flat`
non-frame epilogue's BINARY+TEXT `[r10]` cursor read + `ADDR_SIGMA` base) and zero-test-delta on an UNGATED path
(the m3 pattern driver is `rt_scan`/`IR_SCAN`, not the flat chain; the flat chain is tested only by the un-wired
`test_sno_pat_bb_probe.sh`) — do it only after the flat chain becomes the real m3 driver (PB-RB-CONV) AND a gate
covers it; then flip REG-FENCE TIER 2 to HARD. **SR-2** (save-area = ζ-frame) remains the right *future* call-frame
shape if ever revisited (NOT the rejected 3-box spelling). String-arg `slen` still open (doesn't block the define
smoke). m2 **7/7 HARD** must hold every step. **No emitter/runtime code landed this session — only the new
REG-FENCE gate script** (SCRIP `341b59f`, rebuilt + re-gated green on the rebased tree: m2 7/7 HARD, m3 6/6,
REG-FENCE TIER1=0). Session detail: `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-SR1B-RECONCILE-REGFENCE-M4-SCOPE.md`.
.github tip this commit.

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- Mode-3 native runner: `src/processor/sm_native.c sm_run_native`
- PATND legacy: `src/runtime/snobol4/stmt_exec.c exec_stmt` DT_P branch
- Translator gate: `src/runtime/snobol4/stmt_exec.c patnd_needs_xlate`
- Pattern-building runtime helpers: `src/runtime/rt/rt.c rt_pat_*` (called @PLT from templates)
- Bomb infra: `src/emitter/emit_str.{cpp,h}` bomb_text/bomb_bytes; `src/runtime/rt/rt.c rt_bomb`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`

---

## LOWER2 BOX LADDER — role arms proven via prove_lower2.sh (2026-05-31)

The lower2 role-arm ladder (VALUE / PATTERN / GOAL) was built + proven box-by-box against Proebsting §4 + jcon
`ir_a_*` + GOAL-LOWER-REDESIGN.md's wiring table, via `scripts/prove_lower2.sh` (topology only = node counts +
α/β/γ/ω; value-plumbing deferred to LOWER2-EXEC). Proven: foundation (literal/unop/binop/to/if), combinators
(conjunction/alternation), loops (every/while/until/repeat/not), the full PATTERN role (all leaves +
LEN/POS/RPOS/TAB/RTAB/FENCE/ABORT/FAIL/SUCCEED/ARBNO + CAT/ALT via shared `wire_seq`/`wire_alt` + captures +
DEFER + bare-VAR + BAL), and GOAL-role unify / arith-compares / conj / disj. SNOBOL4 pattern-match statements
EXECUTE (`v_scan`→`IR_SCAN`, 13/13 byte-identical to the SPITBOL oracle).

**Open arms:** L2-B2/C/D/E/F/G/H (loop-escapes, limitation, assignment, calls/access, scan/match, returns/decls,
data/cset/IO) value-role; remaining GOAL ITE/`is`/user-pred-Call/term-comparison/findall/catch. **LOWER2-EXEC:**
Icon value-level proof — wire `lower2_value_entry`→`IR_interp` on `1 to 5` and confirm/adjust the relational
flag (`dval=1.0`) + if-gate (`node.β` runtime dispatch) + alt-gate (`operand_aux`) AGAINST the executor (do not
assume). **L2-TMATCH:** refactor proven box code into `tm`/`tm_g` pattern form. **LM-6 DISPATCH-UNIFY:** retire
lower.c's 3 dispatch entry points once all roles armed + exec-proven. Refs:
`Proebsting-...-Goal-Directed-Evaluation.pdf`, `jcon_irgen.icn`.
