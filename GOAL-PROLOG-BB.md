# GOAL-PROLOG-BB.md — Prolog: GDE inside Byrd-Box machine code (PL-GZ track)

Pruned 2026-06-06 (Lon directive): landed rungs + closed-track history DELETED — git history holds them. Byte-identical FACT-RULE bodies kept VERBATIM (md5 invariant with sibling GOAL-*-BB files preserved).

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

## ▶ STATE (2026-06-11-format)

Watermark: SCRIP `5a3e13f` (battery green). **PL-GZ-0..4, 5a–5c, 6, 6b, 7a, 7b, 8, 8b, 9a, 9b LANDED** — details: git history + handoff docs.
Gates: GATE-1 m2 5/5 HARD · m3 5/5 · m4 5/5. GATE-3 m2 **114/115** (rung23_arith_ext_power: `27^3` returns `27.0` not `27` — int-power float promotion bug, pre-existing) · m3 **53**/62-FAIL (ratchet floor = 53) · m4 **57**/41-FAIL+17-EXCISED (ratchet floor = 57).
**PL-GZ-9 ATOM_OPS LANDED (2026-06-11, commit `5a3e13f`):** Admitted `atom_length/2`, `atom_concat/3`, `atom_chars/2`, `atom_codes/2`, `upcase_atom/2`, `downcase_atom/2` onto the m3/m4 GZ path. New IR kind `IR_DET_ATOM_OP`; new runtime function `rt_pl_atom_op_cell(const char *fn, void *a0, void *a1, void *a2)` in `unification.c` (dispatches on fn name; atom_chars/codes handles both forward and reverse; upcase/downcase uses toupper/tolower; all trail-marked); new template `bb_det_atom_op.cpp` (ROQ(0) for sealed fn string, FRQ cells for slots, one `call rt_pl_atom_op_cell`, verdict in eax); prepare block in `emit_bb.c`, dispatch in `emit_core.c`, Makefile two lines. Four admission sites in `scrip.c`: `pl_gz_rule_body_goal_ok` (named arms before generic comparator arm), `pl_gz_rule_clause` whitelist, `pl_gz_count_synth_goal` (both ATOM a0 AND STRUCT a1 count as synth for atom_chars/codes), `pl_gz_build_goal` (ATOM/STRUCT args materialised via IR_CELL_UNIFY synth slots). Key bug in atom_chars/codes: initial build arm only materialised non-LOGICVAR a0 but passed a1 through raw — STRUCT list `[w,o,r,l,d]` as a1 was not materialised, causing admission failure; fix: materialise STRUCT a1 via synth slot. m3: 48→53 (+5). Newly passing: rung12 atom_length, atom_concat, atom_chars, atom_codes, atom_case. No regressions (m2=114, m4+3).

Watermark: SCRIP `70d4eb2` (battery green). **PL-GZ-0..4, 5a–5c, 6, 6b, 7a, 7b, 8, 8b, 9a, 9b LANDED** — details: git history + handoff docs.
Gates: GATE-1 m2 5/5 HARD · m3 5/5 · m4 5/5. GATE-3 m2 **114/115** · m3 **48**/67-FAIL (ratchet floor = 48) · m4 **54**/44-FAIL+17-EXCISED (ratchet floor = 54).
**PL-GZ-9 SUCC/PLUS LANDED (2026-06-11, commit `70d4eb2`):** Admitted `succ/2` and `plus/3` onto the m3/m4 GZ path. Root cause: both were admitted by legacy flat tier (`pl_flat_goal_is_simple` lines 323/328) which mishandled them, printing `[]` — silent-wrong on both m3 and m4. New IR kind `IR_DET_SUCC_PLUS`; new runtime function `rt_pl_succ_plus_cell(long arity, void *a, void *b, void *c)` in `unification.c` (verified against SWI `pl-arith.c` PRED_IMPL succ/plus; arity-2: X-bound → Y=X+1 else Y-bound → X=Y-1; arity-3: two-bound mask solves third; trail-mark/unwind); new template `bb_det_succ_plus.cpp`; prepare block + dispatch + Makefile. Four admission sites in scrip.c. m3: 43→48 (+5). Newly passing: rung18 succ_forward, succ_backward, plus_xy_bound, plus_xz_bound, plus_yz_bound. No regressions (m2=114, m4+5).

Watermark: SCRIP `8a41154` (battery green). **PL-GZ-0..4, 5a–5c, 6, 6b, 7a, 7b, 8, 8b, 9a, 9b LANDED** — details: git history + handoff docs.
Gates: GATE-1 m2 5/5 HARD · m3 5/5 · m4 5/5. GATE-3 m2 **114/115** (rung23_arith_ext_power: `27^3` returns `27.0` not `27` — int-power float promotion bug, pre-existing) · m3 **43**/72-FAIL (ratchet floor = 43) · m4 **49**/49-FAIL+17-EXCISED (ratchet floor = 49).
**PL-GZ-9 FORMAT LANDED (2026-06-11, commit `8a41154`):** Wired `format/1` and `format/2` onto the m3/m4 GZ path. New IR kind `IR_DET_FORMAT`; new runtime function `rt_pl_format_cell(const char *fmt, void *list_cell)` in `unification.c`; new template `bb_det_format.cpp`; `bb_prepare` block for `IR_DET_FORMAT` in `emit_bb.c`; dispatch case in `emit_core.c`; admission in `pl_gz_rule_body_goal_ok`, `pl_gz_rule_clause`, `pl_gz_count_synth_goal`, and `pl_gz_build_goal` (format/1 handled in the arity-1 arm; format/2 handled inline in the arity-2 comparator arm with guard `strcmp(fn,"format") != 0` preventing early rejection). m3: 38→43 (+5). Newly passing: rung19_format_format1_nl, rung19_format_format2_a, rung19_format_format2_d, rung19_format_format2_i, rung19_format_format2_w. No regressions (m2=114, m4=49+17excised).

Watermark: SCRIP `3cce039` (battery green). **PL-GZ-0..4, 5a–5c, 6, 6b, 7a, 7b, 8, 8b, 9a, 9b LANDED** — details: git history + handoff docs.
Gates: GATE-1 m2 5/5 HARD · m3 5/5 · m4 5/5. GATE-3 m2 **114/115** (rung23_arith_ext_power: `27^3` returns `27.0` not `27` — int-power float promotion bug, pre-existing) · m3 **38**/77-FAIL (ratchet floor = 38) · m4 **49**/49-FAIL+17-EXCISED (ratchet floor = 49).
**PL-GZ-9 TERM-ORDER LANDED (2026-06-11, commit `3cce039`):** Wired `@<`, `@>`, `@=<`, `@>=`, `==`, `\==` term-order comparison ops onto the m3 GZ path. Three-file surgical change: (1) `scrip.c` — four sites: `pl_gz_count_synth_goal` counts atom synth slots; `pl_gz_rule_body_goal_ok` admits tcmp shapes with LOGICVAR/ATOM/LIT_I/LIT_F operands; `pl_gz_rule_clause` adds tcmp to IR_BUILTIN continue guard; `pl_gz_build_goal` adds tcmp branch materialising non-LOGICVAR operands as synth slots via IR_CELL_UNIFY then emitting IR_DET_CMP. (2) `emit_bb.c` — IR_DET_CMP prepare block detects tcmp ops, emits new shape 3 with lslot/rslot in op_parts_ival[1]/[2]. (3) `bb_det_cmp.cpp` — new shape-3 IF arm calling `rt_term_cmp_terms` (already in IR_interp.c/rt.h, takes void* Term* directly — no new runtime fn needed). m3: 33→38 (+5). Newly passing: rung16 at_ge, at_gt, at_le, at_lt, at_sort (all 5). No regressions (m2=114, m4=49+17excised). Next open: `format/1,2` (rung19 — still INTERP-FALLBACK abort).
**PL-GZ-9 BUILTINS LANDED (2026-06-11, commit `2c13f1f`):** Added `functor/3`, `arg/3`, `=../2`, and all 11 type-test predicates (`atom`, `integer`, `float`, `number`, `atomic`, `compound`, `callable`, `is_list`, `ground`, `var`, `nonvar`) onto the m3 GZ path. New IR kinds `IR_DET_TYPE_TEST`, `IR_DET_FUNCTOR`, `IR_DET_ARG`, `IR_DET_UNIV`; new cell-based runtime functions `rt_pl_type_test_cell`, `rt_pl_functor_cell`, `rt_pl_arg_cell`, `rt_pl_univ_cell` in `unification.c`; new templates `bb_det_type_test.cpp`, `bb_det_functor.cpp`, `bb_det_arg.cpp`, `bb_det_univ.cpp`; admission wired in `pl_gz_rule_body_goal_ok` + `pl_gz_build_goal` + `pl_gz_count_synth_goal`; struct/const args materialised into synth slots via `IR_CELL_UNIFY` before the det node. Key bug fixed: arity-2 catch-all arm in `pl_gz_build_goal` was intercepting `=..` before the named arm — reordered named arms before catch-all. m3: 28→33 (+5). Newly passing: rung09_builtins_builtins, rung40_typetest_compound_{callable,compound,ground,is_list}. No regressions (m2=114, m4=49+17excised).
**PL-GZ-9 STRUCT-ARG LANDED (2026-06-08, commit `ec605b1`):** Root cause of multi-clause struct head unification failure: `gz_fill_clause` passed raw IR_STRUCT nodes (from original clause graphs) directly into `CELL_UNIFY`, with `IR_LOGICVAR` children carrying raw clause-graph slot numbers NOT mapped through `pl_gz_slot_map(s, ar, lbase)`. In multi-clause case `lbase > ar` so locals are offset — raw slots pointed at wrong frame cells, making X appear unbound on retry. Fix: added `pl_gz_struct_slot_map(nd, ar, lbase)` (recursive mapper mirroring `pl_gz_arith_slot_map`) applied at head-slot `CELL_UNIFY` generation when `u1->t == IR_STRUCT`. Also enabled four admission-gate checks: (1) `pl_gz_rule_clause` removes IR_STRUCT from blanket node-type rejection; (2) `pl_gz_rule_clause` allows IR_STRUCT as head slot RHS; (3) `pl_gz_call_args_ok` allows IR_STRUCT call args; (4) `pl_gz_admit` extends parent_ok to accept struct nodes that are call args inside `bb_goal_state_t`. New pass: `rung05_backtrack_backtrack` (member/2, list backtracking). m3: 26→27 (+1). No regressions.
**M34-4 LANDED (2026-06-08, commit `7ca12b0`):** Deleted 3 `rt_last_ok@PLT` call sites from `bb_goal.cpp` (alpha-path line 82, beta/redo-path line 99, extern declaration). Root cause: `codegen_graph_block` epilog called `rt_set_last_ok(1/0)` then `ret` leaving rax clobbered (void call). Fix: epilog now emits `mov eax,1; ret` (γ) and `xor eax,eax; ret` (ω) — verdict in rax — while keeping `rt_set_last_ok` for `unification.c` meta-rail compatibility. After `call blbl` / `call redo_lbl` verdict is in eax; `test eax,eax` kept, `call rt_last_ok@PLT` deleted. Gate: `grep -rn 'rt_last_ok' src/emitter/BB_templates/` == 0 PASS. GATE-1 5/5. GATE-3 m2=114 m3=26 m4=51. No regressions.
**M34-1 LANDED (2026-06-07):** Deleted `g_resolve_env = GC_MALLOC(...)` from m3 Prolog driver block in `scrip.c`. Honest m3 baseline. Gate: zero live assignments in m3 block confirmed.
**M34-2 LANDED (2026-06-08, commit `2127c82`):** Three `rt_is@PLT`/`rt_is_lint@PLT` TEXT arms in `bb_is_cmp.cpp` replaced with `rt_is_cell@PLT`/`rt_is_cell_lit@PLT`. `icm_arg_load_lit` used for LOGICVAR/LIT_I operands: passes `lea rcx,[r12+GZ_CELL_OFF(slot)]` (frame-cell ptr) for LOGICVAR, `mov rcx,value` for LIT_I. `rt_is_cell` binary op table completed (added `//`, `mod`, `rem`, `div`, `gcd`, `/\`, `\/`, `xor`, `>>`, `<<`); unary table completed (added `\`, `msb`). New `rt_is_cell_lit(long lval, ...)` added for IR_LIT_I dst case — no cell write, equality check only. Gate: `grep rt_is in IR_interp.c g_resolve_env` == 0 PASS. `rt_is@PLT`/`rt_is_lint@PLT` in bb_is_cmp.cpp == 0 PASS. m3: 23→25 (+2); m4: 45→50 (+5). No regressions. Newly passing: rung23_sign, rung23_power, rung23_max_min, rung23_bitwise, rung29_gcd (m4); rung23_truncate, rung23_sign (m3).
**IRD-2b regression fixed (2026-06-07):** `pl_gz_choice_inline` stored `units[j]->β` as the fact-clause constant; post-IRD-2b that field is a port wire. Fix: `units[j]->operands[1]`. Restored m3 from 22→29.
**M34-PARITY diagnosed (2026-06-07):** Four structural violations: (1) `g_resolve_env` allocated in m3 Prolog block only → fixed by M34-1; (2) `rt_is_f/rt_is/rt_is_lint` read `g_resolve_env[slot]` → fixed by M34-2; (3) m4 `pl_rich_body_root` third tier has no m3 equivalent — legacy-path rungs still diverge; (4) `rt_last_ok` in `bb_goal.cpp` (3 sites) → fixed by M34-4. Ladder M34-3 done; M34-5 remains.
Logged m2-only divergences (NOT fixed; m3/m4 already canon): gz6b disj trust_me_else_fail · mid-cut pre-cut-generator gap · 7a per-NODE cp_mark/committed.

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


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
“duplicate the byte-producing code into each template file” clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

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
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_prolog (four-port IR) → IR_interp.c (m2) → bb_*.cpp x86() templates (m3 BINARY / m4 TEXT)`

**⛔ PROEBSTING IS THE CANON — GPROLOG/SWI IMPLEMENTATION AUTHORITY ABANDONED (Lon directive, 2026-06-04).**
SCRIP Prolog is a NEW compilation model: Proebsting four-port goal-directed evaluation HARD-WIRED to machine
code (two-entry α/β boxes). gprolog and SWI-Prolog are **OBSERVABLE-SEMANTICS ORACLES ONLY** — they define
what a conforming program PRINTS, never HOW. Their internals are NOT design authority. New design questions
are answered from the four-port model + the BB FACT RULES.

**Three modes (Lon 2026-06-04 — NORMATIVE: mode-2 is the ONLY interpreter mode; 3 and 4 are EMIT modes):**
- **Mode 2 (`--interp`):** `IR_interp.c` walks the BB port-graph in-process. The correctness oracle.
- **Mode 3 (`--run`):** EMIT x86 BB blobs and RUN them in-memory in the CURRENT process (sealed slab, jump in). Prolog TODAY still has a LOUD INTERP-FALLBACK for unadmitted programs — TRANSITIONAL, owned by PL-GZ; touch ONLY via PL-GZ rungs.
- **Mode 4 (`--compile --target=x86`):** EMIT standalone `.s`, assemble (`as`), link `libscrip_rt.so`, EXECUTE as a separate system process.

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only. No `rt_*` port-logic helpers (conversion/effect helpers like `trail_mark`/`unify`/`term_new_*` are OK).

**Port semantics:**
| Port | Direction | Prolog meaning |
|---|---|---|
| γ | inherited DOWN | success continuation |
| ω | inherited DOWN | failure continuation (pop choice + unwind trail) |
| α | synthesized UP | this node's fresh-solve entry |
| β | synthesized UP | this node's redo/retry entry |

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

### ⛔ NO-RESURRECT — deleted Prolog value-stack push helpers (Lon directive, 2026-05-31)

`rt_pl_atom_push` and `rt_pl_var_push` are **DELETED** and must **never be resurrected**. They pushed a
box's value onto the global value stack (`rt_pl_*_push → rt_push_int/rt_push_str → vstack_push(g_vstack)`)
— exactly the value-stack traffic completion-test (b) bans. A Prolog box value lives in its box: a logic
variable's binding in its per-activation slot `g_resolve_env[slot]`, an atom as a sealed RO operand
constant — and the **consumer reads it directly** (`rt_pl_node_to_term` / `rt_pl_write_atom` /
`rt_pl_write_var` / `rt_pl_arith`), never via a push. Their former boxes `bb_atom.cpp` and
`bb_logicvar.cpp` are now minimal stackless four-port pass-throughs (`α→γ, β→ω`); `RESOLVE_ATOM` /
`RESOLVE_VAR` provably fire zero times on every live mode-3/mode-4 path (atoms/vars are always operand
constants, never executed leaves). **KEEP, do NOT confuse with these:** the trail ops `rt_pl_trail_*`
(`g_resolve_trail`) are the binding-undo ledger, not a value stack (M4 = KEEP). The `g_vstack` array
itself remains only as SNOBOL4/Icon's own machinery (~150 `rt_*` sites: `rt_arith`/`rt_concat`/pattern
prims/`rt_frame`); Prolog has ZERO ties to it. **GUARD:** `scripts/test_gate_pl_no_value_stack.sh` (run
before every Prolog commit) FAILS if either helper is redefined/declared/called or if any Prolog box
template references `rt_push_*`/`rt_pop_*`/`vstack_*`/`g_vstack` (comments stripped; code only). It has a
proven negative test (injecting a resurrection makes it exit 1).

---

## 🔴 PL-GZ — PROLOG GROUND ZERO (Lon directive 2026-06-04: RESET TO SQUARE ONE)

Proebsting-pure rebuild; GDE INSIDE the boxes; no WAM, no byte-code, no C control engine. Landed-rung detail: git history of this file.

KEEP: parser/AST · `lower_prolog.c` split · m2 IR interp as semantics reference · 115-rung corpus + `.expected` · ALL FACT RULES · trail as the ONE spine · x86()-revamped VALUE boxes (bb_unify, bb_arith, bb_conj pair-loop, bb_builtin_*).
GUT (deleted as the new path re-admits each rung; build-green is no license to preserve): resolution.c control engine (`g_resolve_env` swap, `rt_last_ok`, cut-flag, heap CP protocol) · meta rail (`rt_meta_solve/redo`) · control-coupled bb_goal/bb_choice/bb_catch bodies · `sm_interp_run` m3 carve-out.

**THE LAWS:**
· clause cursor + trail-mark = slots in the choice's OWN per-activation frame row.
· activation env = ζ-TREE: each call site owns a child-frame ptr slot, reset at fresh α. No env swap.
· verdict travels IN THE RETURN VALUE — no `last_ok` global.
· cut = pure WIRING when lexical; frame-local GATE (paper §4.5 indirect-goto) when dynamic.
· trail = the one shared spine; logic vars = frame cells; EVERY binding trailed.
· C call stack = the sanctioned recursion spine.
· ONE x86() body per box serves m3 (BINARY → RX slab) and m4 (TEXT → as+gcc); m3 ≡ m4 by construction.

## 🔴 PL-M34-PARITY — m3 ≡ m4: same driver path, same admitted set, no GDE coupling (Lon directive 2026-06-07)

**THE INVARIANT:** For every Prolog program, m3 (`--run`) and m4 (`--compile --target=x86`) must take structurally identical paths through the driver: same admission gate, same box chain, same templates, same runtime helpers — differing ONLY in the final encoding step (BINARY into the RX slab vs TEXT to `as+gcc`). Any rung that passes m3 must pass m4 with byte-identical output, and vice versa. A rung that neither admits must produce an identical SMX/FATAL signal on both sides.

**CURRENT VIOLATIONS (diagnosed 2026-06-07):**

1. **`g_resolve_env` allocated in m3 only** — scrip.c line ~2131 allocates `g_resolve_env` before calling `pl_gz_admit`. This is the old WAM env; THE LAWS forbid it. `rt_is_f` reads `g_resolve_env[slot]` to fetch variable values → works in m3 (env allocated), returns 0 in m4 standalone (env NULL). Causes rung23/29 arith+float family to diverge.

2. **`rt_is_f` is GDE-coupled** — reads `g_resolve_env[slot]` instead of the ζ-frame. Must be replaced by a frame-reading helper `rt_is_cell(int dst_cell, const char *op, int lk, int li_or_cell, double ld, int rk, int ri_or_cell, double rd)` where LOGICVAR args pass their frame-cell address (obtained via `[r12 + GZ_CELL_OFF(slot)]`) not a slot index into the old env.

3. **Three tiers in m4, two in m3** — m4 falls back to `pl_rich_body_root` + `codegen_clause_dispatch` (legacy `RESOLVE`-box flat chain, old C engine behind it); m3 has no matching tier and hard-aborts. These extra tiers in m4 pass rungs that m3 aborts on — they are NOT legitimate m3≡m4 passes. The fix is NOT to add the rich tier to m3; it is to expand `pl_gz_admit` to cover those shapes so both sides go through the GZ path.

4. **`rt_last_ok` in `bb_goal.cpp`** — 3 call sites (`rt_last_ok@PLT`) remain in the goal template, the old verdict global. Must be deleted; verdict travels in the return value per THE LAWS.

Ladder — strict order, gate after each:

- [x] **M34-2 — REPLACE `rt_is_f` with `rt_is_cell` (COMPLETE, 2026-06-08, commit `2127c82`).** Three TEXT arms in `bb_is_cmp.cpp` replaced: LOGICVAR dst binary IR_ARITH → `rt_is_cell@PLT` (lea rdi,[r12+GZ_CELL_OFF]), IR_LIT_I dst binary IR_ARITH → new `rt_is_cell_lit@PLT`, LOGICVAR dst unary IR_ARITH → `rt_is_cell@PLT`. `rt_is_cell` binary op table completed (added `//`, `mod`, `rem`, `div`, `gcd`, `/\`, `\/`, `xor`, `>>`, `<<`) and unary table completed (`\`, `msb`). Gate: `grep 'g_resolve_env' IR_interp.c | grep rt_is` == 0 PASS. `rt_is@PLT`/`rt_is_lint@PLT` in bb_is_cmp.cpp == 0 PASS. m3: 23→25 (+2); m4: 45→50 (+5). Note: `rt_is_cell_lit` reads LOGICVAR args via frame-cell ptr — correct for GZ-admitted procedures. Legacy-path procedures (called via pl_rich_body_root) have their own g_resolve_env-based path that is unaffected (they use different IR shapes or their arith is handled by the legacy C engine itself).

- [x] **M34-3 — ASSERT m3 and m4 take identical tier for every admitted rung (COMPLETE, 2026-06-07-S46).** `scripts/test_gate_pl_m34_parity.sh` written + runs. Honest baseline: PASS=29 FAIL=75 EXCISED=11. Dominant pattern: m3 aborts (rc=134) while m4 legacy `pl_rich_body_root` tier carries the rung → produces output. rung03_unify_unify: both exit 0 but outputs differ (m3=`b a`, m4=`[] []`). Gate becomes green only as PL-GZ-9 admits more shapes. Abort detection: m3_abort = rc=134; m4_abort = rc≠0 from run_prolog_via_x86_backend.sh.

- [x] **M34-4 — DELETE `rt_last_ok` from `bb_goal.cpp` (COMPLETE, 2026-06-08, commit `7ca12b0`).** The 3 `rt_last_ok@PLT` call sites in the goal template deleted. `codegen_graph_block` epilog fixed to return verdict in eax (mov eax,1/xor eax,eax before ret) while keeping `rt_set_last_ok` for meta-rail. Gate: `grep -rn 'rt_last_ok' src/emitter/BB_templates/` == 0 PASS. No regressions.

- [ ] **M34-5 — PARITY SEAL: m4 rich-tier forbidden for admitted shapes.** After M34-1..4, audit: any rung that passes m4 via the `pl_rich_body_root` / `codegen_clause_dispatch` path but fails m3 is a legitimate admission gap — add it to the PL-GZ-9 admission queue (do not patch the m4 fallback path). Verify by temporarily disabling the rich-tier fallback in m4 and confirming the set of passing rungs matches m3 exactly. The rich tier remains for truly unadmitted shapes during reconquest; it is not a crutch for shapes the GZ path should cover.

Ladder (LANDED rungs 0..4, 5a–5c, 6, 6b, 7a, 7b, 8, 8b, 9a, 9b DELETED — git history):
- [ ] **PL-GZ-9** — corpus reconquest: all 115 rungs onto the new path, m3/m4 verdicts byte-identical. Strategy: admission-gate expansion in `pl_flat_goal_is_simple` / `pl_gz_rule_body_goal_ok` / `pl_gz_build_goal` / `pl_gz_admit` for each IR shape encountered; `gz_fill_goal` IR_BUILTIN pass-through fix (`op_sval`/`op_ival` not propagated → rung16/19/40 next). findall = drive the NEW boxes (no meta rail); catch/throw = PT-3 CP-truncate + ball-copy LAW re-landed; aggregate/nb likewise; dynamic DB = **B-full** (runtime assert = lower + MEDIUM_BINARY emit into the RX slab; m3 ≡ m4 by construction). Current m3: **28**/87-FAIL (28 = 2026-06-10 baseline after arity-3 fix). Ratchet: never regress.
**ARITY-3 LANDED (2026-06-10, commit `1a1eeb6`):** rung06 (`append/3`, `length/2`, `reverse/2`) admitted onto m3. Lifted the arity-2 ceiling to arity-3: `pl_gz_choice_state_t`/`pl_gz_call_state_t` arg arrays `[2]`→`[8]` (consts `[4][2]`→`[4][8]`); added `rcx` as the 3rd SysV arg register in `bb_cell_call`/`bb_callee_frame` (`rsi`/`rdx`/`rcx`); lifted six `ar>2` admission guards to `ar>3` in scrip.c; widened the two synth-arg counting caps (`ai<2`→`ai<3` in `pl_gz_clause_nsynth`/`pl_gz_count_synth_goal`) that size the callee frame so a non-logicvar 3rd arg gets its synth slot. `bb_cell_choice` arity guard 2→3. m3: 27→28 (+1). No regressions (m2=114, m4=51). m4 rung06 still prints `[]` (legacy rich-tier mishandles arity-3 — an M34-5 admission-gap item, NOT patched in the m4 fallback). Next: rung09 (`functor/3`, `arg/3`, `=../2` — IR_BUILTIN builtins not yet in `pl_gz_rule_body_goal_ok`).
**STRUCT-ARG FIX LANDED (ec605b1):** `pl_gz_struct_slot_map` added + four admission gates opened. rung05 now passes m3. Next: rung06 (`append/3`, arity-3 predicates) requires lifting `ar > 2` limit in `pl_gz_choice_rule_clauses` / `pl_gz_rule_inline_check` AND adding a 3rd arg register to `bb_cell_call` / `bb_callee_frame` (currently only `rsi`/`rdx` for arity ≤ 2). Then rung09 (functor/3, arg/3, =../2 — IR_BUILTIN builtins not yet in `pl_gz_rule_body_goal_ok`).
- [ ] **PL-GZ-FENCE** — coupling gate ZERO across all Prolog templates · GATE-3 m2/m3/m4 verdict-identical with identical EXCISED sets · resolution.c engine + meta rail DELETED · emitted seed `.s` shape-isomorphic to `test_pl_1.c` (box-for-box, port-for-port).

## LEGACY DISPOSITION AT RESET (2026-06-04)

| Track | Disposition |
|---|---|
| PL-M34 / PL-BBL | ABSORBED into PL-GZ (m3≡m4 principle + THE LAWS); retired. |
| PT | PT-0 pred table SURVIVES. PT-1b meta rail = starve+delete at GZ-9. PT-2 findall · PT-3 catch LAW · PT-4a aggregate · PT-4b B-full dynamic-DB LAW — all re-land at GZ-9. |
| WAM-CP | CLOSED. Survivors: CP-7 unify → GZ-3 · CP-9 → 7a · CP-8 indexing/CP-11/CP-12 + PL-INDEX-L2-1 → post-FENCE optimization tier · CP-13 moot at GZ-9. |
| Legacy m4 path | GATE-3 scaffolding during reconquest only; an admitted program NEVER falls back; each mechanism deleted when its last rung migrates. |
| BB revamp / hygiene | Delegated to GOAL-BB-FIXUP. PL-GZ-1b(e), CORPUS-S-HYGIENE, PLG-7, VSX-8, PJ-AGW-6b, SWI-PLUNIT removed from this file. |

## Session setup

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1
bash scripts/test_prolog_rung_suite.sh    # GATE-3
bash scripts/test_gate_bb_one_box.sh      # PL-HY-FENCE
bash scripts/test_gate_pl_gz7.sh          # + gz2..6b as touched
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```
Full m4 corpus: loop `corpus/programs/prolog/rung*.pl` through `scripts/run_prolog_via_x86_backend.sh`, diff `.expected`.

## Architecture reference

Pipeline: Prolog AST → lower_prolog (four-port IR) → m2 `--interp` (IR_interp) · m3 `--run` (EMIT BINARY → RX slab, in-process) · m4 `--compile` (EMIT TEXT → as+gcc, system process).
GZ ports: δ = callee α, ε = callee β (PORT_DELTA/PORT_EPSILON beside γ/ω/β).
NOTE: corpus `.s` box labels are generation-NONDETERMINISTIC — suite set-diff is the invariant. Legacy counts FROZEN at the 2026-06-04 reset; the new-path counter only ratchets up.

### Per-construct port wiring
| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `IR_GCONJ` (seq) | first goal's α | last goal's β | `goal[i].γ = goal[i+1].α` | `goal[i+1].ω = goal[i].β`; first → ω_in |
| `IR_CHOICE` | first clause α | next clause α | each `.γ = γ_in` | `clause[i].ω = clause[i+1].α`; last → ω_in |
| `IR_GOAL` (call) | callee α | callee β | callee success → γ_in | callee exhausted → ω_in |
| `IR_ITE` | cond.α | ω_in (semidet) | cond.γ→Then, Then.γ→γ_in | cond.ω→Else, Else.ω→ω_in |
| `IR_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `IR_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

### bb_exec.c ↔ x86 template translation
For each `case IR_FOO:` in `bb_exec.c`: state in `nd->{state,counter,value,ival}` (persistent across `bb_reset`);
`entry==α → state==0` (fresh), `entry==β → state>0` (redo); store result in `nd->value`, tail-call `nd->γ(nd)`
or `nd->ω(nd)`. No `rt_*` port helpers — only effect helpers (`trail_mark`/`trail_unwind`/`unify`/
`prolog_atom_intern`/`term_new_*`/`rt_pl_node_to_term`). Mode-4: ≤6 args in registers, >6 pack on stack (SysV).

---

