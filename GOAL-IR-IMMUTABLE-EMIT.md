# GOAL-IR-IMMUTABLE-EMIT.md — The emitter READS IR. It NEVER mutates it. (Ground Zero #5)

## ⛔⛔ HARD RULE — ICON ONLY. IGNORE EVERY `lower_*.c` WHERE `* != icon` (Lon, 2026-06-30)
**This goal touches `src/lower/lower_icon.c` and Icon-reachable code ONLY. Do NOT read, open, grep into,
reason about, "clean up," or edit `lower_snobol4.c`, `lower_raku.c`, `lower_prolog.c`, `lower_common.c`'s
per-language arms, or ANY non-Icon frontend/lowerer. They are PARKED — already broken pending their own
GZ#5 rebuilds (not started), by directive — and they reference a wholesale-dead pre-GZ#5 IR vocabulary
(`IR_SEQ`, `IR_PATTERN_*`, `IR_DTP_ASSIGN`, `IR_ALT`, … — none in the current `IR_e`). They are NOT in the
Makefile build **[CORRECTED 2026-07-02: `lower_raku.c` + `lower_pascal.c` ARE compiled (Makefile lines 404-405) — a repo-wide mechanical rename/delete MUST include them or the build breaks (the IR_ALT precedent); rename-only, still zero auditing/fixing of their logic]**. Their stale enum references are INERT and are NOT this goal's concern; "fixing" or even
auditing them is wasted effort and a scope violation.**
- **The ONLY files in scope:** `src/lower/lower_icon.c`, `src/emitter/emit.cpp` (+ `emit.h`, Icon-reachable
  templates `src/templates/bb_*.cpp`), `src/contracts/IR.h`/`scrip_ir.c`, `src/opt/ir_query.c`, the Makefile
  template list, and the Icon corpus/smoke. Nothing else.
- **If a dead enum member (e.g. `IR_ALT`) lingers in a parked non-Icon file, LEAVE IT.** It compiles nowhere,
  ships nowhere, and singling it out is theater. Purge such names ONLY from LIVE, build-included, Icon-reachable
  code (e.g. the `emit.cpp` chain-BFS) — which is done.
- **When in doubt whether a file is in scope:** if its name is not `lower_icon.c` and it is not reached when
  compiling an Icon program through `emit.cpp`, it is OUT. Move on.

## ⛔⛔ HARD RULE — ICON-ONLY TEST EXECUTION. DO NOT RUN ANY NON-ICON LANGUAGE TEST (Lon, 2026-06-30)
**Do not run, invoke, or cite any non-Icon test/smoke/gate — not as setup, not as a sanity check.** Stricter than the scope rule above: don't *execute* another language's test at all. Those frontends are PARKED; their FAILs are pre-existing noise this goal does not pay for.
- **FORBIDDEN:** `test_smoke_prolog.sh`, `test_smoke_snobol4*.sh`, `test_smoke_raku*.sh`, `test_smoke_unified_broker.sh` (cross-language), any `scripts/test_*` whose name contains `prolog`/`snobol4`/`raku`/`rebus`/`snocone`/`pascal`, and any other-language line inherited from another doc's Session Setup (GOAL-ICON-BB.md's `test_smoke_prolog.sh` line does not apply to this goal).
- **PERMITTED (shared build steps, not tests):** `make scrip` / `make libscrip_rt`, cloning the SPITBOL `x64` oracle, and anything named `test_*icon*` / `test_gate_icn_*` / `test_smoke_icon.sh`.
- **THE ONLY GREEN SIGNALS THIS GOAL READS:** `scripts/test_smoke_icon.sh` (12 programs ×2 modes) · `scripts/test_icon_all_rungs.sh` (289-program corpus) · the four `test_gate_icn_*.sh` discipline gates · `scripts/test_gate_emit_no_ir_mutation.sh` · `scripts/audit_jcon_wholesale.sh` (66 probes, icont-oracle 4-way — the per-rung instrument).
- **COMPLETION TEST:** zero non-Icon test invocations in the session's tool-call history; if one ran anyway, its output is not cited as evidence.
## ⛔⛔ STANDING DIRECTIVE (Lon, 2026-06-28) — WHOLESALE JCON-IN-SCRIP, ICON-ONLY
We are doing a complete wholesale rewrite of the Icon LOWER + EMITTER to mirror JCON
(`refs/jcon-master/tran/`) construct-by-construct, because JCON has it CORRECT. Same IR as JCON's `ir.icn`
EXCEPT SCRIP keeps fine-grained `IR_BINOP`/`IR_UNOP` instead of one `ir_OpFunction`. **EVERYTHING ELSE IS
DEFERRED** (old TRACK A/B/C ladder, IRM numbering, the pre-pivot opcode-collapse plan) — go straight to the
JCON spine, one TT at a time, per the CONVERSION PLAYBOOK below.
- **`.s` byte-identity is NOT a gate, ever** (Lon, repeated 4×). The `.s` is the honest current output and
  will keep changing drastically. Never wire it into a gate.
- **No full regression required per rung.** Icon regression may go to zero and grow back; breaking other
  languages mid-ladder is authorized (they are already broken pending their own GZ#5 rebuild — not started).
- **No micro "baseline gate."** The old two-snippet sanity gate (`write("hello world")` + `write(1+1)`,
  both modes) is RETIRED (Lon, 2026-06-30) — it tested almost nothing and was never a script, only this line.
  The honest per-rung signal is `bash scripts/test_smoke_icon.sh` (12 programs, both modes) plus the corpus
  stash/rebuild/FAIL-set diff for the rung you touched; each TT is its own honest pass/fail — land it,
  document it precisely, move on. **Icon-only, full stop — see the ICON-ONLY TEST EXECUTION hard rule at the
  top of this file; do not run a non-Icon smoke to "double-check" anything.**
- **`IR_t.tmp` IS the temporary slot** (not `lhs`; no `IR_TMP` opcode — see CONVERSION PLAYBOOK). Only
  value-producers carry one (`ir_node_produces_value`); control/effect ops don't.

## ⛔⛔ ORIENTATION SYNOPSIS — read this instead of the six docs PLAN.md's session-start sends you to
**Everything load-bearing from `ARCH-ICON.md`, `ARCH-x86.md`, `REGISTER-LAYOUT.md`, `ARCH-SCRIP.md`,
`REPO-SCRIP.md`, and `CORPUS-LOCATIONS.md`, distilled in one place by someone who already read all six this
session — so the next session doesn't have to.** Skip those six for routine work on this goal; open one only
if a specific question genuinely isn't answered here.

**The four-port model (Byrd box).** Every construct = α(start, fresh entry) β(resume, ask for next value)
γ(success, value ready) ω(fail, exhausted). A relop is a 0-or-1-result generator, not a boolean (canonical
Icon `cmplte`: `return y` / `fail`). γ/ω are `IR_t` edges; α/β are positions the chain-BFS discovers from
edges pointing AT a node (see CONVERSION PLAYBOOK above for the full isomorphism). Resumability is ω-wiring
only — see DIVISION RULE below; never a stored flag.

**Stackless boxes.** No value stack, no `r12`-as-TOS, no `rt_push/pop`. RW state lives in the ONE per-glob ζ
frame `[r12+off]` (established once by the glob preamble, `mov r12, rdi`). RO compile-time constants (cset
literals, baked pointers) sealed adjacent, reached `[rip+disp]`. Recursion/re-entry = a fresh per-α-entry
DATA linkage, never a stack push — CODE is shared and reusable, DATA is per-invocation. Never jump into the
middle of a blob from outside; every cross-blob entry lands on the α-preamble.

**Register contract — LIVE table (ignore the SM-era/r10 history in REGISTER-LAYOUT.md; the doc says itself
it's superseded, twice over, and `bb_regs.h` — its other source of truth — is deleted):**

| Reg | Role |
|---|---|
| r12 | ζ — BB-local RW frame `[r12+off]`. **NOT** a value stack. |
| r13 | Σ — subject base pointer |
| r14 | δ — cursor (0-based; `&pos = δ+1`) |
| r15 | Δ — subject length/end |
| rbx | GVA slot-array base — globals at `[rbx+gva_k*16]`, 16-byte DESCR stride (verified vs live templates 2026-06-30) |
| rbp | NV/variable-name hash table base (reserved; GET/SET still plain C calls) |
| r10 | **RETIRED** — no data-block register; `bb_regs.h` (which defined this contract) no longer exists |

**Flat-BB ABI.** A glob = N concatenated boxes' code + one sealed RO region at the end. Entry = jump to the
glob's first byte (no `esi` port-test — that's the legacy dispatched/`--bb-brokered` form only). Both
intra- and extra-blob transitions are plain `jmp rel32` (`r12` is callee-saved, survives either way). Two
block kinds: BB (`bb_*.cpp`, does WORK) vs XA (`xa_*.cpp`, wraps/stitches — prologue/epilogue/data-section/
entry-dispatch; builds no operands).

**Execution modes — current reality (REPO-SCRIP.md; `ARCH-SCRIP.md` is stale here, still describing a
since-deleted mode 2).** Exactly two: `scrip --run f` = mode 3, native x86 BINARY in-process. `scrip
--compile f` = mode 4, x86 TEXT asm → `gcc -no-pie` + `libscrip_rt.so`. Both must produce identical results;
that's the whole isolation invariant — no mode-3/4 code path walks the AST or interprets SM/BB at runtime,
the emitter walks the graph only at EMIT TIME then frees it.

**Build/run.** `cd /home/claude/SCRIP && make scrip && make libscrip_rt`. Oracle: SPITBOL x64 at
`/home/claude/x64/bin/sbl -b file.sno` (clone `snobol4ever/x64` if absent). **Fresh sandbox:** `apt-get install -y libgc-dev gdb` first; the audit oracle = icont/iconx built from the icon-master upload (`make Configure name=linux && make`, never X-Configure), auto-probed via `SCRIP/refs/` symlinks (RULES.md CONSULT CANONICAL SOURCES recipe).

**Corpus.** Icon programs: `/home/claude/corpus/programs/icon/rung<NN>_*.icn` (263, each with a sibling
`.expected`) — **not** `/home/claude/SCRIP/test/icon/` (only 8 smoke files). Full suite:
`bash scripts/test_icon_all_rungs.sh`. Fast smoke (12 programs, both modes): `bash scripts/test_smoke_icon.sh`.

**Concurrency discipline (GOAL-ICON-BB.md, condensed).** One dispatch case per IR kind; one template file
per box; edit only your own language's arms/boxes, never a peer's; a kind with no case ABORTS loud, never
silently declines. Patch-offset bookkeeping is abolished — `bb_bin_t`/hand-counted byte offsets don't exist;
patch metadata travels in-band as tagged records inside a template's returned string, walked once by
`bb_emit_x86`.

## ⛔⛔ IR-LAYOUT JCON-ALIGNMENT DIRECTIVE (Lon, 2026-07-02) — make Icon's IR match JCON's layout
**Principle (Lon verbatim-in-spirit):** match JCON's IR record set as closely as possible. THE ONE EXCEPTION is
`ir_Goto`/labels — SCRIP BBs carry the four ports INSIDE the box template, so instead of varying code output
with labels, SCRIP has varying `IR_*` opcodes that CLASSIFY each form BY NAME, one template each. SNOBOL4 was
done very differently; Icon shall be the JCON-faithful one. All BBs done = Icon at 100%.

**LANDED (`65f8c32e`):** `IR_FIELD`→`IR_FIELD_GET` · `IR_ENTER_INIT`→`IR_INITIAL` (mechanical, FAIL set byte-identical).

**DERIVED ANSWERS (fresh from refs/jcon-master/tran, 2026-07-02):**
- **while/until:** JCON emits PURE `ir_Goto` chunk wiring — `ir_Conj` does not exist ANYWHERE in JCON (0 hits
  in ir.icn/irgen.icn/gen_bc.icn). SCRIP's `IR_CONJ` is our MATERIALIZED Goto: the chain-BFS discards a
  sentinel's edges, so where JCON writes a bare Goto chunk, SCRIP needs a real node to carry the jump
  (while's exit sentinel W, repeat's header H, break/next). Same wiring, one SCRIP-ism justified by the
  ports-in-the-box exception.
- **to / to-by:** JCON has NO `ir_To` at all — `ir_a_ToBy` defaults `/p.byexpr := a_Intlit(1)` and always emits
  ONE `ir_opfn(operator("...",3))`. JCON collapses because its product is a generic opfn dispatch; per the
  classification principle SCRIP splits BY NAME instead.
- **subscript:** canonical subscript yields a VARIABLE (`oref.r` subsc/trapped vars) — lvalue AND rvalue
  through one node is CORRECT. Current `TT_IDX → lower_call("[]")` is the misfit.

**RUNG LADDER (Lon directives, in order):**
- ~~TO-SPLIT~~ **LANDED (SCRIP `7dd2baf7`, 2026-07-02):** `IR_TO` (2-operand, implicit by=1) + `IR_TO_BY` (3-operand,
  runtime by; `lower_to` picks by TT arity) — mirrored at every spec'd IR_TO site plus three the spec didn't name
  (`scrip.c rhs_kind_ok` pre-emission gate, `bb_call_write_route` wintexpr/route-3, `descr_chain_arity`=3).
  `bb_to.cpp`'s static constant-by helper was DEAD on the live path (walk stages `op_node_kind=nd->op`, never
  IR_OP_COUNT, so it always returned 1) — by=1 baked, byte-identical; `bb_to_by.cpp` carries the runtime-by
  four-port arm verbatim. **IR_RESUME_VALUE was NOT needed** (see reserved table). Probes 34/35 hold; negative-by
  hand-checked m3==m4; audit 68/68; corpus 194/59/36 FAIL set byte-identical (stash `comm` diff empty).
- ~~IR_MAKE_LIST~~ **LANDED (SCRIP `138c64dc`, 2026-07-02):** TT_MAKELIST/TT_VLIST → `lower_make_list` →
  `IR_MAKE_LIST` (N operands), retiring the `lower_call("MAKELIST")` by-name string route for Icon; element
  chaining is JCON `ir_a_ListConstructor` verbatim-in-shape. Variable slot grant (k += 1+n_operands: result
  DESCR at tmp, contiguous argv scratch at tmp+16); `bb_make_list.cpp` marshals slots → ONE `rt_make_list`
  call (extracted from the by-name arm, which now delegates — write-once); >16-element literal falls LOUD.
  Probe 50 OK 4-way; audit 68/68; corpus FAIL set byte-identical; empty `[]` + inline `[5,6,7][3]` hand-checked m3==m4.
- [x] **IDX-UNIFY phase 1 — LANDED (SCRIP `264c3994`, 2026-07-02):** `x[i]` is a real LVALUE. `TT_IDX` →
  2-operand variable-producing `IR_SUBSCRIPT` (operands[0]=base, [1]=index; discriminated from the 3-operand
  section by n_operands) + `IR_DEREF` rval partner (identity on non-DT_V) + **`IR_ASSIGN_VAR`** write-through
  (operands[0]=variable, [1]=value; result=value; name CONFIRMED against Lon's criterion 2026-07-02 — it assigns
  through an operand-carried variable; IR_ASSIGN keeps the by-NAME arm). `lower_call("[]")` retired for Icon.
  **Option (ii) mini-trapped var** (Lon: "Continue" on the recommendation; option (i)'s read-inserts divergence
  rejected on canonical-wins): `DT_V=15` + `VCELL_t{cellp,tbl,key,key_d}` (descr.h); tables get the LAZY
  `{tbl,key}` trap — rt_deref does a FRESH lookup mirroring subscript_get verbatim (incl. the `dflt.v!=0`
  quirk), rt_assign_var inserts via `table_set_descr`; a pure READ NEVER inserts (canonical tvtbl). **DISCOVERY:
  Icon `[...]` lists are DT_DATA gen_type=="list" blocks NOT DT_A** — cell = `&frame_elems[i-1]`, negative-index
  wrap, canonical parity with subscript_get (DT_A arm kept for arrays). Strings/records pass through as VALUES
  (probe 63 held; `s[i]:=v` BOMBs loudly citing tvsubs). Probes 72-76 oracle-pinned (audit 71→76).
  **TWO WIRING BUGS found by the corpus diff, fixed, documented in code:** (1) `cx->beta=ω` clobber killed
  generator-index resumption (`every write(s[1 to 3])`, rung16_subscript_sub_every) — beta now inherited from
  the last-lowered operand (lower_call postfix parity); (2) the emission walks (`codegen_flat_chain_body` +
  `descr_chain_operand_refs`) followed ω only for BINOP/CALL/generator kinds — SUBSCRIPT/DEREF/ASSIGN_VAR
  failure blocks were never EMITTED (`if s[5] then/else` printed nothing, rung16_subscript_sub_fail; latent for
  3-operand sections in test position too) — ω-follow added at all 4 walk sites. Evidence: audit 76/76 both
  modes · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 · corpus 194/59/36 → **200/53/36** (six FAIL→PASS:
  rung13_table_subscript_assign, rung23_table_table_{basic,default,member},
  rung35_table_str_str_{default_int_key,table_read}; ZERO new fails) · bench-asm 13/0/0/1/12 updated=0.
  **REMAINING (sub-rungs):** ~~(r1) `tvsubs` string trapped-vars~~ **LANDED (SCRIP `c76ce21d`, 2026-07-02):**
  `s[i]` is a string lvalue — canonical substring trapped variable on the phase-1 rails. `IR_VAR_REF`
  (classify-by-name): identifier subscript bases produce DT_V over the variable's own cell (GVA
  `lea [rbx+k*16]` / local `lea [r12+sa]`, `bb_var_ref.cpp`, `rt_var_ref_cell`); DT_V flows THROUGH the
  chain — `rt_subscript_var` derefs a DT_V base internally (canonical subsc, oref.r:710-758), retiring
  phase-1's between-level IR_DEREF nodes, so `t[k][i] := v` is lvalue-correct lazily (ssvar = the tvtbl
  beneath, fresh-deref at assign). `VCELL_t` + `{sv,pos,len}`; rt_deref tvsubs arm (cnv.r:482); rt_assign_var
  subs_asgn splice (oasgn.r:345 — any-length src, int/real stringified, RECURSIVE write-back through ssvar
  collapses canonical's type_case; trap len updates so revassign β-restore reuses the trap per canonical
  rasgn — probe 84 pins the every-restore AND the successful-unresumed-keeps forks). Out-of-range/0 index
  FAILS (canonical fail, not runerr). ONE wiring bug (probe 83): nested TT_IDX bases went through the rvalue
  DEREF wrapper, losing the variable — lower_idx_var now recurses into itself for TT_IDX bases.
  IR_VAR_REF mirrors IR_VAR's bump-side treatment (walk-preamble op_sval list joined — the clobber-pattern
  gate; flat-assigner exclusion mirrored, though that fn is DEAD — see TMP-ERADICATE). Probes 82/83/84
  oracle-pinned (audit 81→84). NOT covered (loud/absent as before): `s[i:j]` section-assign (3-operand
  SUBSCRIPT stays a value producer), record-field-under-subscript, keyword bases (`&subject[i]`);
  ~~(r2) `arr[i] <- v` subscript-revassign~~ **LANDED (SCRIP `fba88eae`, 2026-07-02):**
  `IR_REV_ASSIGN_VAR` — the through-variable sibling of IR_REV_ASSIGN, IR_ASSIGN_VAR's operand order
  ([0]=variable via lower_idx_var, [1]=value), classify-by-name per the JCON-ALIGNMENT directive;
  bb_rev_assign_var.cpp = canonical rasgn on the phase-1 rails (rt_deref deref-save at off+16 / k+=2 grant,
  rt_assign_var write + β-restore — table traps re-insert the saved value, canonical tvtbl; probe 80 pins the
  absent-key fork oracle-confirmed). bb_rasgn.cpp's dormant pre-doctrine op_ival==1 subscript_get/set arm
  deleted. TT_REVASSIGN's IR_FAIL subscript placeholder retired; ~~(r3) `x[i,j]` COMMA FORM parser gap~~ **LANDED (SCRIP
  `df46db00`, 2026-07-02):** one-arm parser change (plain-subscript else only; sections untouched), extra indices
  append as TT_IDX children, the dormant lower_idx_var chain took them first try — probe 79 oracle-pinned
  (read / write-through / mixed table→list), corpus FAIL set byte-identical; ~~(r4) `*t` table-size gap~~ **STALE
  (SCRIP `ed10358e`, 2026-07-02):** re-derived fresh — `*t`/`*L`/`*"s"` all correct m3==m4==oracle (fixed by
  intervening phase-1 table plumbing; limit-of-RepAlt stale-strike precedent); its payload cashed: probe 78
  = the STRONG fork discriminator (read-of-absent returns default AND `*t` stays 0; insert only on assign) —
  option (ii) canonical-tvtbl laziness pinned at full strength, superseding probe 75's weak form.
- ~~CONJ-RENAME~~ **RE-NAMED (Lon directive 2026-07-02, later same day: `IR_SEQ_EXPR` → `IR_CONJUNCTION`, SCRIP `46c1923a`):**
  the join node carries the name of the operator that motivated it. FOR THE RECORD, so no future session burns an
  hour on this again: **`case TT_CONJ: case TT_SEQ_EXPR:` is ONE shared case body (lower_icon.c:298) and BOTH arms
  build the identical `IR_CONJUNCTION` node** — the `&` arm and the `;` arm differ ONLY in edge wiring (`;` threads
  a failed statement's ω forward to the next statement; `&` adds the ω-to-nearest-resumable-left backtrack chain,
  lower_icon.c:321). Mechanical repo-wide (incl. lower_raku/lower_pascal per the carve-out); `bb_seq_expr.cpp` →
  `bb_conjunction.cpp`; enum + name-table row to the alphabetical C-slot. Proof: 291-program mode-4 emit manifest
  byte-identical (291/291 `.s`; the only 2 `.err` deltas are the numeric op label in the pre-existing
  IR_MAKE_LIST >16-element loud-fall, 26→27, pure enum-slot arithmetic). Audit 71/71 · smoke 12/12×2 · gates green ·
  mutation HARD=4 · bench-asm 13/0/1/12 updated=0. Prior naming state (same day): **LANDED, four commits (IR_GOTO + IR_SEQ_EXPR):** CONJ-0 `7ed39fcb`
  (genuine-`&` probes 69/70/71, oracle-pinned — the eponym had NO probe before) · IR_GOTO split `980d7946`
  (pure junction carved out: break/next/while-W/until-U/repeat-H/every-no-body, operand[0] pushes DROPPED —
  the value-vs-jump-target overload resolved; `bb_goto.cpp` = `x86_pair_loop()` alone, beside pre-existing
  `bb_goto_dyn` = the JCON ir_Goto/ir_IndirectGoto/ir_MoveLabel trio complete by name; NOT in rhs_kind_ok) ·
  IR_CONJ→IR_SEQ_EXPR `633dc295` (the surviving node is ONLY the TT_SEQ/TT_SEQ_EXPR value-forwarding join —
  conjunction semantics are the ω_to-nearest-resumable-left EDGE WIRING in LOWER, never the node, matching
  JCON's 0 ir_Conj; enum moved alphabetical, `bb_seq_expr.cpp`, stale case-result comments corrected) ·
  TT_CONJ `87ab07c4` (root of the naming confusion: Icon's parser BORROWED shared TT_SEQ for `&`; new
  additive shared-enum kind before TT_KIND_COUNT, parse_and builds it, lower case label split — peers'
  TT_SEQ untouched). Every rung: audit 71/71 both modes · corpus 194/59/36 FAIL set byte-identical ·
  smoke 12/12×2 · gates green · mutation HARD=4 · bench-asm 13/0/1/12 updated=0.
- [x] **RESERVED-SET RECONCILE — CLOSED (2026-07-02): all rows resolved. Final row IR_MOVE DELETED (SCRIP `c34d4125`, Lon verdict) — see table:**
  | enum | live refs | JCON record | verdict input |
  |---|---|---|---|
  | ~~`IR_EXEC`~~ | **DELETED (`7138de96`)** — was a payload MACRO (IR.h:109), not an enum member (census miscount corrected) | none | — |
  | ~~`IR_UNREACHABLE`~~ | **DELETED (`7138de96`)** | ir_Unreachable | role served by `x86_bomb` — divergence ratified |
  | ~~`IR_SCAN_SWAP`~~ | **DELETED (`7138de96`)** | ir_ScanSwap | save/restore lives inside IR_SCAN_ENTER — divergence ratified |
  | `IR_DEREF` | live | ir_Deref (gen_bc:125) | **IMPLEMENTED (IDX-UNIFY phase 1, SCRIP `264c3994`):** variable → value, identity on non-DT_V (bb_deref.cpp / rt_deref). Reservation spent exactly as planned. |
  | ~~`IR_MOVE`~~ | **DELETED (`c34d4125`, Lon verdict 2026-07-02)** — tmp-doctrine absorption RATIFIED (producers write own slot; zero construction sites ever); only client copy_prop.c/.h (unexercised pass, zero live material) deleted wholesale with it (Makefile source-list + object rule, optimizer.c cp_run/stats arm); its unverified defs==1&uses==1 divergence question died with it | ir_Move (gen_bc:220) | — |
  | ~~`IR_RESUME_VALUE`~~ | **DELETED (`ed0ac777`, Lon directive 2026-07-02)** — reservation spent: TO-SPLIT (`7dd2baf7`) landed ToBy resume as durable ζ-frame arithmetic (counter at tmp+16, β = plain add), so JCON's resume-value INSTRUCTION dissolves into SCRIP's frame LAYOUT | ir_ResumeValue (gen_bc:551) | — |
  | `IR_MAKE_LIST` | 0 | ir_MakeList (irgen:1346) | **IMPLEMENT** — already this ladder's rung above |

  **CORRECTION (2026-07-02):** `IR_OP_COUNT` was wrongly listed in the earlier 7 — it is the enum COUNT
  SENTINEL (277 structural uses as array bound/name-table size), not an opcode; NOT deletable.

## ⛔⛔ TMP-ERADICATE (Lon directive, 2026-07-02) — the emitter does NOTHING for temporary allocation
**Lon verbatim-in-spirit: "We want not having emitter doing anything for temporary variable allocation
scheme."** The emit-time bump allocator is emitter-side state that makes the graph incomplete at
construction — the same defect the α/β edge-stamp fixed for edges — and the two-counters-over-one-offset-
space design is the documented root of the slot-collision bug family (`a0b3f410`, `024abd2f`, `d225d4a2`,
IR_LIMIT/IR_REPALT grant comments). End state: LOWER owns the ENTIRE ζ-frame layout; `drive_value_slot`
degenerates to a read of `nd->tmp`.

**SURVEY (2026-07-02, fresh census — re-derive before starting, never trust this prose):**
- **Already half-landed:** `ir_drive_slot_assign` (scrip_ir.c; sole live caller `scrip.c:620`) owns every
  value-producer with explicit multi-slot grants (TO/TO_BY k+=2 · MAKE_LIST 1+n · SCAN_ENTER · INITIAL ·
  ITERATE · LIMIT · REPALT · REV_ASSIGN/_VAR — each grant comment records the collision it fixed), and
  `drive_value_slot` already ABORTS on a value-producer with no `nd->tmp` ("fix the gap in LOWER, never
  patch it here").
- **DEAD siblings:** `ir_tmp_slot_assign` + `ir_tmp_slot_assign_flat` (scrip_ir.c) have ZERO callers —
  the flat one carries IR_VAR/IR_VAR_REF exclusions that are now pure archaeology. Delete at TE-FENCE.
- **Survivors (the eradication targets):** `drive_value_slot`'s non-producer tail → `bb_slot_alloc16`;
  15 direct `bb_slot_alloc16` + 14 `bb_slot_claim` sites. Icon-reachable: `emit.cpp` + `bb_call.cpp` /
  `bb_call_fn.cpp` / `bb_call_proc_staged.cpp` (per-arg argv scratch, call-relnd scratch). NOT Icon
  (out of scope, flip with their languages' GZ#5): `bb_match_*` (SNOBOL4 pattern), `bb_gather`/`bb_mapgrep`
  (Raku). Plus the `bb_flat_cursor_reserve` coordination bridge — dies LAST.
- **The varslot cursor (`bb_varslot`, locals) is a THIRD emit-time counter** (the a0b3f410 fix jumped it
  past `jcon_value_region`) — full eradication interns names into `ir_drive_slot_assign`; own rung, biggest.

**LADDER:**
- [ ] **TE-0 GATE** — `scripts/test_gate_emit_no_slot_alloc.sh`: count `bb_slot_alloc16(`/`bb_slot_claim(`
  call sites (comments stripped) in emit.cpp + Icon-reachable templates; informational baseline now
  (15+14 repo-wide), `--strict` zero at TE-FENCE over the Icon set.
- [ ] **TE-1 CALL-FAMILY GRANT** — `ir_drive_slot_assign`: every `ir_is_call_kind` + IR_CALL gets
  `k += 1 + n_args (+1 relnd scratch where used)` (the MAKE_LIST precedent); `bb_call*.cpp` compute
  argv base = `tmp+16` instead of per-arg `bb_slot_alloc16`. The big slice — most Icon-reachable sites.
- [ ] **TE-2 EMIT.CPP RESIDUE** — the remaining direct claims in emit.cpp drive cases → LOWER grants.
- [ ] **TE-3 KILL THE TAIL** — `drive_value_slot` non-producer tail → abort; delete `bb_slot_alloc16` /
  `bb_slot_claim` / `bb_flat_cursor_reserve` from the Icon-reachable path; frame size = LOWER's total only.
- [ ] **TE-4 VARSLOT ABSORPTION** — locals interned into `ir_drive_slot_assign` (own session).
- [ ] **TE-FENCE** — gate `--strict` zero (Icon set); dead assigners deleted; audit + smoke + corpus
  FAIL-set byte-identical.

## ⛔ FACT RULE — THE EMITTER NEVER MUTATES AN IR NODE
The emitter (`src/emitter/**`) dispatches on `nd->op` and reads `nd`'s fields. It does **NOT** write
`nd->op`, does **NOT** write `IR_LIT(nd).*`/`IR_EXEC(nd).*` on an input node, does **NOT** synthesize IR
nodes, and does **NOT** consult `rt_*` to decide IR shape. Every specialization decision is made in LOWER
(per-language) and baked into the IR shape the emitter receives.
**GATE:** `scripts/test_gate_emit_no_ir_mutation.sh` — `[-]>op[[:space:]]*=` (op-writes) + `IR_LIT(...).x =`
on an input node (field-writes) == 0. **Current: HARD=4** (all pre-existing, in code paths the GZ#5 rewrite
hasn't reached yet — not regressed by Icon LOWER work, which the gate doesn't scan).

## ⛔ DIVISION RULE (Lon, 2026-06-27) — RESUMABILITY IS ω-WIRING, NOT A STORED FLAG
"Generator vs coercive vs plain" is not three operators — it's the OPERATION (an immediate on one node) plus
**resumability, which costs ZERO template logic**: a resumable node is reached by routing a consumer's
backtrack edge AT the producer node; the chain-BFS (`codegen_flat_chain_body`) resolves that edge to the
producer's **β** (not its α) whenever `ir_is_generator_kind(producer)` and the consumer sits later in chain
order. **PROVEN (B3, 2026-06-27):** live four-port chains correctly enumerate `(1 to 3)+10`→`11 12 13` and
Cartesian `(1 to 3)+(1 to 2)`→`2 3 3 4 4 5` with **zero dedicated generator-tree walker** — `bb_conj`'s entire
body is `x86_pair_loop()` (pure in-band β-define + γ/ω jumps from the DRIVE_PAIR table). Never store a
generator/resumable flag on the node (`dval=1.0` tags are the violation pattern — remove on sight).

## DO NOT
- Re-introduce ANY `->op =` write in `src/emitter/**`.
- Decide a call kind from `rt_*` runtime state at emit time — proc/builtin tables are compile-time.
- Encode operand-source in an IR opcode — operand-source lives on the OPERAND node (a producer box).
- Add a per-language function to the emitter/templates — language lives in parser + LOWER only.
- Build a separate "generator" opcode/template family — see DIVISION RULE; it's ω-wiring, not a template.

## ⛔⛔ CONVERSION PLAYBOOK — JCON → SCRIP, ONE TT AT A TIME (Claude Sonnet 4.6, 2026-06-30)
**The mechanical recipe for converting any Icon construct from JCON into LOWER + the EMITTER DRIVER +
TEMPLATES. Read once; each TT is then fill-in-the-blanks. This is the head-start for the SNOBOL4/Snocone/
Rebus/Prolog/Pascal sessions doing the same to their own lowers later.**

### THE CENTRAL ISOMORPHISM — 4 JCON labels ⇄ (2 node positions + 2 IR_ref_t edges)
JCON's `ir_info(start, resume, failure, success)` (`irgen.icn` `ir_init`) ⇄ SCRIP's `IR_t.γ`/`IR_t.ω`
(`src/contracts/IR.h`):

| JCON label | SCRIP realization | Set/read by |
|---|---|---|
| `p.ir.start`   | the node's own **α position** in the flat chain | a predecessor's γ/ω points here |
| `p.ir.resume`  | the node's own **β position** | BFS routes a consumer's edge here iff `ir_is_generator_kind` |
| `p.ir.success` | `nd->γ.node` | LOWER: `γ_to(nd, target)` |
| `p.ir.failure` | `nd->ω.node` | LOWER: `ω_to(nd, target)` |

`start`/`resume` are **not stored** — they're positions the BFS discovers from edges pointing AT the node.
You never "set start/resume"; you set OTHER nodes' γ/ω to point here, and the generator-kind check picks
α-vs-β. This is why JCON's four labeled chunks collapse to two edges. `p.ir.x` (loopinfo/scaninfo) has no
struct field — it's carried in `icx_t` (`cx->loop_exit`, `cx->loop_next`, `cx->beta`) during lowering.
JCON's `ir_tmploc`/`ir_MoveLabel`/`ir_IndirectGoto` (unbounded-resume "label variable") usually maps to
**plain β-wiring** — wire ω at the right node and delete the indirection.

**⚙ IR_ref_t CARRIES ITS OWN α/β PORT IN `.sz` — LOWER STAMPS IT, EMITTER READS IT (LANDED 2026-06-30, `bb70a841`).**
`IR_ref_t` = `{IR_t* node; char sz[4];}`. The `sz` field is the **α/β discriminant of the edge**, written by
LOWER at construction and read by the emitter — NOT recomputed downstream. The rule LOWER applies: an edge whose
TARGET is `ir_is_generator_kind` is a RESUME edge → stamp `"β"` (`lc_γ_to_β`/`lc_ω_to_β`); every other edge →
`"α"` (`lc_γ_to`/`lc_ω_to`). The Icon `γ_to`/`ω_to`/`build` wrappers (`lower_icon.c`) do this automatically by
checking `ir_is_generator_kind(target)`. The emitter (`emit.cpp` chain-BFS) reads the stamp:
`node_γ = (γ.sz=="β") ? betas[k] : lbls[k]` (UTF-8 `β` = `CE B2`). **PROVEN equivalent to the old positional
`i > k && ir_is_generator_kind` guess:** with the positional fallback DELETED (pure-stamp routing), icon smoke
stays 11/12 and the full corpus stays 82/289 — zero divergence. The fallback is RETAINED for now only to protect
un-stamped edges during the ongoing GZ#5 rollout; the end state deletes it. **WHY THIS MATTERS (Lon, 2026-06-30):**
the graph must be CORRECT AT CONSTRUCTION — an edge has to say whether it means "enter fresh (α)" or "resume (β)"
or no optimization pass can even know what an edge *means*. Recomputing α/β positionally in the emitter made the
graph incomplete; stamping it on the ref makes the graph self-describing, which is the precondition for sound
optimization. **The remaining un-stamped resume sites** (SEQ/CONJ backtrack chaining `ω_to(val[i],val[lr])`,
`cx->loop_next` loop-backs, `lβ`/`mβ` operand resumes) currently rely on the positional fallback; stamping them
explicitly (so the fallback can be deleted) is the follow-up rung. **NOTE:** a stamp names ONE static target; a DATA-dependent resume (whichever arm last fired) is the label variable — LANDED `dc45d9e2` (`IR_MOVE_LABEL` + `IR_INDIRECT_GOTO`; see Watermark).

### lhs ⇄ tmp
JCON's `lhs`→`ir_Tmp` node ⇄ SCRIP's `int IR_t.tmp` FIELD on the producing node (one node = one value = one
slot — why the `IR_TMP` opcode is dead). LOWER assigns it; `drive_value_slot()` (`emit.cpp`) reads `nd->tmp`
first, falls back to legacy slot-alloc only for unconverted nodes. A consumer reads an operand's value via
`operand->tmp` (see `IR_CALL`'s arm: `a->tmp`).

### THE FOUR CONVERSION SHAPES (classify the JCON `ir_a_X`'s `ir_chunk` list)
1. **Pure edge-threading** (only `ir_Goto` chunks) → LOWER wires γ/ω among sub-exprs; **no opcode, no
   template, no driver case.** Landed: `TT_IF` (`lower_if`, JCON `ir_a_If`). Also this shape: `ir_a_Compound`,
   `ir_a_NoOp`, `ir_conjunction` (→ `IR_CONJ`/`bb_conj`, whose template is pure pair-table threading — the
   zero-template limit case of this shape).
2. **Value-producer + runtime call** (`ir_opfn`/`ir_Call`/lits) → ONE `IR_*` node, operand `tmp`s pushed, the
   TEMPLATE marshals slots into args and `call`s an `rt_*` helper (value work NEVER reimplemented inline —
   that's DUP FORM 1/2 in GOAL-ICON-BB.md). Operation rides as an immediate, not opcode identity. Landed:
   literals, `IR_VAR`, `IR_BINOP`/`_RELOP`, `IR_UNOP`, `IR_CALL*`, `IR_KEYWORD`, `IR_RETURN`.
3. **Resumable generator** (success loops back via resume) → per the DIVISION RULE, make the node
   `ir_is_generator_kind` and point the consumer's backtrack edge at it; the BFS does the rest. Landed:
   `IR_TO` (`bb_to.cpp`). Also landed: `TT_EVERY`, `IR_REPALT`, `IR_LIMIT`, `IR_ITERATE`.
4. **Control/effect** (`ir_Succeed`/`ir_Fail`/`ir_Assign`) → `IR_SUCCEED`/`IR_FAIL`/`IR_ASSIGN`, no tmp.
   JCON's `ir_Move` (copy closure result into target) is usually absorbed — the producer writes its own tmp.

### THE LOOP-BACK & UNCONDITIONAL-JUMP IDIOM (loops, break, next, goto — Claude Sonnet 4.6, 2026-06-30)
**THE TRAP (cost an entire prior session a "diagnosed, not fixed" entry):** an `IR_FAIL` or `IR_SUCCEED` node is
NOT a general "jump-to-my-γ-target" node — it is a CHAIN TERMINATOR. The chain-BFS (`codegen_flat_chain_body`,
`emit.cpp`) does two things that discard a sentinel's edges: (i) it *threads through / skips* `IR_SUCCEED` and
`IR_FAIL` nodes (they're never added to `nodes[]`, lines ~950/955/970), and (ii) when ANOTHER node's γ (or ω)
points AT a sentinel, it resolves that edge to the **chain's** `lbl_γ`/`lbl_ω` exit (lines ~1001-1002:
`γ.node->op == IR_FAIL → node_γ = &lbl_ω`; `== IR_SUCCEED → &lbl_γ`). So a sentinel's *own* γ-target (e.g. the
post-loop continuation you wired into a `break`) is **silently thrown away** — control goes to the enclosing
chain's exit, not your target. This is why `repeat`-via-`IR_FAIL`-loopback ran the body once then left, and why
`break`-as-`IR_FAIL` skipped its post-loop code.

**THE FIX — to jump unconditionally to an arbitrary real target T (and have T's subgraph emitted), use an
`IR_CONJ` node with γ=ω=T, never a sentinel.** `IR_CONJ`'s driver (`emit.cpp` ~line 910) is pure
`DRIVE_PAIR_JMP(lbl_γ)` + `DRIVE_PAIR_DEF_JMP(lbl_β,lbl_ω)` — i.e. "jump to my γ-target," nothing else — and
`IR_CONJ` IS a real chain node, so (a) it is added to `nodes[]`, (b) the BFS *follows* its γ edge (queuing T and
everything reachable from T), and (c) an edge pointing at the `IR_CONJ` resolves to the `IR_CONJ`'s own α label —
a real `jmp`, forward or backward. `IR_CONJ` carries no value and needs no tmp; pushing its jump-target as
operand[0] (as `lower_repeat` does) keeps slot-registration uniform with the value-producing CONJ used for `;`.

**APPLYING IT — the loop family (JCON `ir_a_Repeat`/`ir_a_While`/`ir_a_Until`, decoded to 2-edge form):**
- `while C do B`: sentinel `W=IR_FAIL` with `ω→γ_post`; `C.success→B.start`, `C.failure→W`(=exit),
  `B.success→C.start`, `B.failure→C.start`. (Works because a `while` *does* exit via C's failure — the
  `IR_FAIL` exit semantics align. **Do not "fix" `while`'s `IR_FAIL` — it is the genuine loop exit.**)
- `until C do B`: mirror — `C.success→W`(=exit), `C.failure→B.start`, body loops to `C.start`.
- `repeat B`: **no condition, no failure exit.** Header `H=IR_CONJ`, `γ=ω→B.start`; body lowered with
  `γ=ω→H` (both body success AND body failure loop back); construct entry = `H`; `cx->beta=γ_post`. The loop
  leaves ONLY via `break`/`return`/`fail`. (JCON: `expr.success→ir.start`, `expr.failure→ir.start`,
  `ir.start→expr.start`; the `ir.start` Goto collapses into `H`.)
- `break` (JCON `ir_a_Break`: `expr.success→curloop.success`, `expr.failure→curloop.failure`): jump to
  `cx->loop_exit` (the loop construct's γ = its post-loop continuation) via `IR_CONJ`, γ=ω=`loop_exit`.
- `next` (JCON `ir_a_Next`: `Goto curloop.nextlabel`): jump to `cx->loop_next` (the loop header) via `IR_CONJ`.
  For `repeat`, `cx->loop_next = H`; for `while`/`until`, set it to the condition entry so `next` re-tests.
- **`cx->loop_exit`/`cx->loop_next` save/restore is MANDATORY** around the body lower (nested loops) — already
  done by all three; copy the pattern.

### EXPORTABLE WIRING RULES (proven across LIMIT/REPALT/ALT/IF — apply to every future junction construct, any language)
- **Edge ROLE beats target KIND.** `build()`/`γ_to` auto-stamp β whenever the TARGET is generator-kind — trustworthy ONLY for backtrack edges. A producer's SUCCESS edge into a generator-kind junction (LIMIT gate, REPALT, …) is α (enter fresh); LOWER must α-restamp it (`lc_γ_to`). Enforced at 7 sites: statement spine (guarded — `every` re-aims its own γ), TT_REPALT's γ, TT_LIMIT count→entry, TT_SEQ/SEQ_EXPR, and (2026-07-02, `b3d41c74`) the loop family's body entries — lower_while C.γ→B, lower_until C.ω→B, lower_repeat H→B.
- **A synthesized `*res` junction's γ is the construct's PUBLIC success label.** Wire-later callers re-point only `*res` — internal success paths (each arm's ml) must resolve through the junction's γ at EMIT time (a READ of the finished graph, never a write).

### THE 3-FILE EDIT RECIPE (shapes 2 & 3; shape 1 is LOWER-only)
- **(a) LOWER** (`src/lower/lower_icon.c`): build the node (`build(cx,IR_X,γ,ω)`); recurse sub-exprs
  capturing `*res` + `cx->beta`; wire γ/ω per the JCON chunk list (`γ_to`/`ω_to`); push operands
  (`ir_operand_push`/`bb_operand_aux_set`); set `cx->beta` to this node if it's the resumable thing the
  consumer should target. Return the entry node; set `*res` to the value node.
- **(b) DRIVER** (`src/emitter/emit.cpp`, `emit_drive`): add `case IR_X:` — read operand slots
  (`bb_child0/1`, `ir_call_arg(nd,i)`, `→tmp`), set `g_emit.op_*`, set DRIVE_PAIR if the box jumps via the
  pair loop, `DRIVE_FILL(nd, lbl_γ, lbl_ω, lbl_β)`. **Read-only — never write `nd->op`/`IR_LIT(nd).field`.**
- **(c) TEMPLATE**: `case IR_X: bb_emit_x86(bb_x()); return 0;` in `walk_bb_node`; create
  `src/templates/bb_x.cpp` (`x86(...)` only, both BINARY+TEXT via the same calls); add to Makefile + gate
  scans. Mirror an existing same-shape template (generator→`bb_to.cpp`; pure-thread→`bb_conj.cpp`).
- **(d) BFS REACH:** confirm `codegen_flat_chain_body`'s queue-feeding follows the node's ω where needed
  (generator exhaust, relop fail) — **the single most common silent bug** (sank `until` until `59dafbc0`).
- **(e) VERIFY both modes, then commit:** `SCRIP_ICN_BB=1 ./scrip --run` AND `./scrip --compile` →
  `gcc -no-pie -x assembler X.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out` → run. Mutation gate ≤ baseline. If
  a generator diverges/hangs: **MONITOR-FIRST** (RULES.md) — bracket with the monitor, then gdb
  breakpoint-hit-count to the land mine. Do not guess.

### CANONICAL SOURCE PAIRING
Port topology ← `refs/jcon-master/tran/irgen.icn` `ir_a_X` (the `suspend ir_chunk` list IS the γ/ω wiring).
Emission ← `refs/jcon-master/tran/gen_bc.icn` `bc_gen_ir_Y` for each `ir_Y` in the chunk (JVM bytecode → x86
by analogy). Value semantics ← `refs/icon-master/src/runtime/*.r` (`oarith.r`/`ocomp.r`/`ocat.r`/`oasgn.r`/
`fscan.r`/`fstranl.r`/`invoke.r`). The m2 oracle is a transcription, not truth.

### ⚠ FILE-LAYOUT NOTE (2026-06-30 consolidation — several older docs/PLAN.md are stale on this)
`src/emitter/{emit_bb.c, emit_core.c, emit_drive.c, BB_templates/, XA_templates/, bb_regs.h}` **no longer
exist.** Current: `src/emitter/emit.cpp` + `emit.h` (the ONE driver, `emit_drive`, + dispatch) + `emit_io.c`
+ `emit_str.cpp` + `sil_macros.h`; templates flattened to `src/templates/*.cpp` (161 files, no subdirs). The
register contract is hardcoded as `"r12"`/`"r13"` string literals in templates — no macro header. Use these
paths; ignore any doc still citing the old ones (this file now does, throughout).

## ⛔ TT_* COVERAGE PUNCH LIST (Icon ladder — climb this, not an opcode ladder)
**Ground truth = `bash scripts/audit_jcon_wholesale.sh` — run it fresh; never trust this prose (TECHNIQUE Step 4).** Snapshot 2026-07-01: **64/66 both modes.**

**✅ COVERED (audit-verified OK):** literals I/R/S/CSET · ident/global/invocable · `initial` (once-per-DEPTH caveat below) · binop arith/divmod/relop/concat · unop −/+/*x/\x//x (IR_UNOP + IR_UNOP_TEST) · `not` (via `&null` IR_VAR; IR_NOT deleted) · assign/augop/swap · **if** — statement AND value-context, then+else (value convergence via the ig shared cell, JCON `ir_a_If` :583-610, landed 2026-07-01) · while/until/repeat/break/next · every (postfix, assign, assign+body, noassign-after) · to / to-by · alternation bounded + unbounded (label variable) · repalt · limit · compound · call (builtin/arglist/params/recurse/mutual) · proc fail/suspend/return · list-ctor / `|||` lconcat · record field · section `s[i:j]` + string subscript · scan (move/tab-upto/many/match/cset-arg) · create / `@` activate / exhaust · seq-expr · `&line` / `&pos`-in-scan · case + case-default.

**🔴 OPEN — the audit ladder: EMPTY (66/66 as of SCRIP `a3de01d2`, 2026-07-01).**
- ~~`22_revassign`~~ **LANDED (SCRIP `a3de01d2`):** `IR_REV_ASSIGN` (generator-kind, k+=2 grant, save DESCR at off+16) per canonical `rasgn` (oasgn.r:142-162), reusing the pre-existing orphaned `bb_rasgn.cpp` verbatim. The historic BENCH-F2 op_a_slot collision is defeated by OPERAND ORDER (operands[0]=rhs so walk's clobber-pattern re-derivation lands correctly; [1]=lhs name carrier, IR_SWAP idiom). Root cause of the probe failure: `is_resumable()` (the AST-side conj fail-chain predicate) lacked TT_REVASSIGN — one token. Subscript lvalue `arr[i] <- v` stays an honest IR_FAIL placeholder (own rung).
- **Same commit (Lon directive):** `bb_operand_aux_set/get` DELETED — it was a thin DESTRUCTIVE veneer over `IR_t.operands/n_operands` itself (no side table); 12 setters → `ir_operand_push`, 6 tautological fallback readers collapsed, API gone from IR.h/scrip_ir.c/lower.h. RULES.md PEERS RULE corrected in place. Renames: `IR_RASGN→IR_REV_ASSIGN`, `IR_SECTION→IR_SUBSCRIPT` (Griswold-book naming; dead-name reuse, the IR_UNOP_TEST precedent).
- ~~`54_section_plus`~~ **LANDED (SCRIP `c0e74d52`, 2026-07-01):** `s[i+:n]`/`s[i-:n]` desugared in LOWER per canonical icont (tcode.c:591-600 — dup i; eval n; plus/minus; sect): synthetic IR_BINOP(ADD/SUB) as operand[2], IR_SECTION always plain; driver operands moved to `drive_value_slot` (tmp doctrine); `subscript_get2` reversed positions now SWAP per canonical sect (oref.r:509-513) — also fixes plain reversed `s[4:2]`, previously empty. Audit 65/66.

**🟡 OPEN — beyond the probe set:**
- ~~corpus rung03 suspend shapes~~ **LANDED (SCRIP `a0b3f410`, 2026-07-02):** not a suspend bug — a UNIVERSAL proc-local varslot/tmp collision (`bb_varslot` cursor after param interning == `ir_drive_slot_assign`'s base; the relop's return-y result-write clobbered the first local). Fix: proc builders jump the varslot cursor to `jcon_value_region` so locals sit above tmps. Corpus 190→194 (+rung03_suspend_{gen,compose,filter}, +rung36_jcon_statics), zero regressions.
- ~~`TT_CSET_COMPL` (`~e`) silent no-op~~ **LANDED (SCRIP `bf7f9392`, 2026-07-02):** real IR_UNOP arm (is_unop_tt + UO_CSET_COMPL + `rt_cset_compl` beside the CUNION/CDIFF/CINTER family); probe 81 oracle-pins membership/involution/**-composition. **KNOWN UNIVERSE DIVERGENCE:** SCRIP csets are NUL-terminated char strings — `\0` is never a member, so `*~x` reads one less than canonical &cset-256 (probe avoids absolute counts by design). `TT_RANDOM` (`?e`) + dead `TT_INTERROGATE` — unresolved silent no-ops, deliberately unreclassified (flagged 2026-07-01).
- **COMPUTED-CSET SCAN OPERANDS (finding, own rung):** the scan-family boxes are LITERAL-cset-only — `s ? upto(~x)` (or any computed cset) hits the pre-existing loud `bb_scan_upto` BOMB ("needs literal cset arg"), and bare-call `upto(c,s)` is the pre-existing rung06 corpus FAIL. `~e` composing with the scan suite is blocked on that rung, not on the operator.
- coexpr unary prefixes `.e` / `^e` absent from `parse_unary` (`^` lexes only as binary POW).
- `IR_SCAN_TAB` absent from `ir_is_generator_kind` (UPTO/FIND/MANY/BAL present) — the scan family's "reverses effects if resumed" contract (canonical `tabmat`, `omisc.r:84`) is unverified; own rung.
- ~~limit-of-RepAlt `(|1) \ 3`~~ **STALE — re-tested 2026-07-02, PASSES** (fixed by the intervening repalt/limit rungs); deleted per re-derive-don't-trust-prose.
- ~~`while … do write(|1)` unclassified data point~~ **CLASSIFIED + LANDED (SCRIP `b3d41c74`, 2026-07-02):** loop-family PRODUCE edges into generator-kind bodies were auto-stamped β (asm-verified `jmp …β` skipping REPALT's α flag-clear). lower_while/until/repeat body-entry edges → unconditional α-stamp (EXPORTABLE RULE sites 5-7; bodies are bounded, JCON 'always bounded'). Probe `68_loop_genkind_body` pins all three — **audit 68/68**. SIBLING FLAGGED (no repro yet): the body→condition LOOP-BACK edges have the same latent shape if a loop CONDITION's entry is generator-kind; conditions are bounded too, α when a repro lands.
- ~~unary-test-op failing-`if` else-routing~~ **LANDED (SCRIP `ca31f6e2`, 2026-07-02):** BFS ω-following whitelist lacked IR_UNOP/IR_UNOP_TEST (both loops) — else subgraph never discovered, edge resolution degraded to chain lbl_ω, whole if-else silently vanished. Mirror of the BINOP pair added; probe `67_unop_test_else` pins it — **audit now 67/67**.

**⚠ STANDING AUDIT TARGETS (systemic, not constructs):**
- **INLINE-ARITH POINTER HOLE (live bug, found 2026-07-02 — stands regardless of the DEFERRED CVA ladder):** bb_binop_arith's int fast path guards only `!=DT_DATA`, so a runtime DT_S (or dynamic DT_R) operand falls into the inline integer arm and computes on the pointer/double bits — `x:="3"; write(x+2)` prints 58996226 both modes; relops "pass" by pointer-compare. Canonical semantics already pinned in the deferred CVA section (oarith.r/ocomp.r/ston). Fix architecture TBD by Lon: the deferred CVA convert-box is one candidate; a minimal tag-widen guard (DT_I-only fast path, everything else to the RT coercer) is the small-surface alternative.
- ~~THE CLOBBER PATTERN~~ **EXECUTED (SCRIP `dde4e9fd`, 2026-07-02):** full two-sided diff — 12 emit_drive pre-DRIVE_FILL stagings of preamble-re-derived fields vs `walk_bb_node`'s derivation lists. **TWO LIVE BUGS:** (1) runtime LIMIT count `e \ k` yielded NOTHING silently (staged fallback discarded, preamble baked `IR_LIT(nd).ival`=0) — fixed count-in-slot: `op_sc` staged (surviving field, TO_BY anti-stale precedent), preamble IR_LIMIT special case DELETED, `bb_limit` compares `FRQ(op_sc+8)` at runtime, literal+variable counts ONE path; probe 77 oracle-pinned. (2) EVERY string literal IS_CSET-mislabeled: `bb_lit_scalar` STRING-arm `IF(op_ival!=0→slen=-1)` vestige × IR_t's ANONYMOUS UNION (`IR_LIT(nd).ival` on a string node reads the sval POINTER BITS, always nonzero); vestige deleted (CHARSET arm keys on op_node_kind). Corpus +5 exactly (rung29_builtins_type_{copy,image,type}, rung36_jcon_augment, rung37_cset_ops — all string-vs-cset discriminators). Dead stagings removed (CHARSET op_ival=1, SUBSCRIPT-2op op_ival=0) + stale comments corrected. All other pre-fill stagings verified redundant-but-EQUAL by construction and RETAINED (their `drive_value_slot` calls REGISTER the slot the preamble re-derives). **INVERTED ARROW noted for the class:** in (2) the preamble's re-derivation INJECTED garbage into a conditionally-read field — same ownership mismatch, opposite direction to the discard cases.
- **x86() silent-drop** — the dispatcher returns EMPTY for an unrecognized arg shape (sank `bb_enter_init`'s 4-arg cmp/mov; kept `flat_drive_repalt`'s absence invisible). A default-bomb retrofit at 147-template scale is its own carefully-gated rung, not a drive-by.
- `initial` is once-per-DEPTH, not once-per-procedure (ζ frames = static `g_rt_frames[depth]`, reused) — canonical once-ever needs writable static storage; own rung (the GVA `.bss` arena is the named candidate, GOAL-ICON-BB §ICN-STORAGE).
- ~~Emitted proc preamble still carries `lea r10,[rip+Δ]`~~ **DELETED (SCRIP `2ae6155d`, 2026-07-02):** both mediums (xa_flat text lea ×2 + binary raw `49 BA` movabs ×2 — hand-encoded bytes in the legacy XA), zero readers (census: r10 elsewhere = paired push/pop scratch only in 3 scan templates, value never read — those saves stay, possible call-alignment shims, own gated rung). The BINARY arms' hand-counted `out_site` patch offsets included the dead 10 bytes — decremented in step, smoke m3 = the byte-surgery acid test. `Δ` the C global is LIVE and stays (subject-length shadow, driver save/restore); only its dead r10 courier died. Preamble now = GOAL-ICON-BB's premise shape exactly. Corpus FAIL set byte-identical; bench version.s honest-churned (corpus `48fb69bb`).
- `SCRIP_OPT=1` `branch_chain` crash (optimizer ships OFF by default). Whoever fixes it must defer-protect captured labels: coret β-edges, `g_create_body_entry` targets, every `IR_MOVE_LABEL.operand[0]` target, every `IR_INDIRECT_GOTO` γ-target (JCON `optim_goto_chain_defer` discipline). ~~copy_prop~~ **DELETED with IR_MOVE (`c34d4125`, Lon verdict 2026-07-02)** — its unconditional-elimination divergence question died with it; `arith_fold.c` is unlinked.
## ⛔⛔ MECHANICAL JCON→SCRIP CONVERSION TECHNIQUE (Claude Sonnet 4.6, 2026-06-30) — read before starting any new TT
**This is the by-eye/by-hand recipe used this session, written up so the next session (Icon or, later, any
other language doing the same JCON-mirroring exercise) doesn't have to re-derive it.** It is a refinement of
the CONVERSION PLAYBOOK above with the actual workflow steps that playbook assumes but doesn't spell out.

### Step 0 — find the JCON procedure, read it as a literal wiring diagram
`refs/jcon-master/tran/irgen.icn` has one `ir_a_X` procedure per AST node kind (`grep '^procedure ir_a_'`
gives the full list — **43** of them, one-to-one with JCON's `a_X` AST records; **the "47" this line previously claimed is WRONG — fresh `grep -c '^procedure ir_a_' refs/jcon-master/tran/irgen.icn` = 43, re-verified 2026-07-01**). Each is a `suspend
ir_chunk(LABEL, [INSN, INSN, ...])` sequence. Read it as exactly what it says: a chunk named `p.ir.start` (or
`.resume`/`.success`/`.failure`) containing a list of instructions ending in a `ir_Goto`/`ir_IndirectGoto` to
another chunk's label. **Draw the graph on paper or in your head before writing any C** — nodes = chunks,
edges = the Goto targets. This graph IS the lowering; everything downstream is mechanical translation of it.

### Step 1 — classify by the FOUR CONVERSION SHAPES (already in the playbook above)
Count how many `ir_opfn`/`ir_Call`/value-instructions appear outside pure `ir_Goto` threading. Zero ⇒ shape 1
(pure edge-threading, LOWER-only, no opcode/template). One ⇒ shape 2 or 4 depending on whether a value is
produced (`lhs`/`target` set) or not. A success-chunk that loops back to a `.start`/`.resume` ⇒ shape 3
(resumable generator) — **check this FIRST**, because shape-3 constructs disguise themselves as shape 1 if you
only look at instruction count; the tell is a `Goto` whose target is upstream of the current chunk in the
threading order (a back-edge), not just any `Goto`.

### Step 2 — find the `bounded`/`unbounded` fork, if any
Many `ir_a_X` procedures branch on `/bounded` (Icon: `if bounded is null then ... else ...`). **This single
flag is the entire difference between "this construct needs a label variable" and "this construct doesn't."**
`ir_a_Alt`/`ir_a_RepAlt`/`ir_a_ListConstructor` all do this — the unbounded arm allocates `t := ir_tmploc(...)`
and emits `ir_MoveLabel`/`ir_IndirectGoto`; the bounded arm never does. **Do not implement both arms in one
pass.** Land the bounded arm first (it is always simpler and is what 90% of real call-sites exercise — `write(x)`,
`if`, a plain consumer), prove it, commit it, THEN come back for the unbounded/label-variable arm as its own
rung. This is exactly why `TT_ALTERNATE`'s bounded case (`write(1|2)`) is done and its unbounded case
(`every write(1|2|3)`) is correctly deferred — don't fuse them.

### Step 3 — runtime semantics: which `.r` file, and what to actually extract
`refs/icon-master/src/runtime/*.r` is C, not Icon — it's the OPERATIONAL ground truth for what a value
operation actually computes (overflow rules, type coercion order, fail conditions), which JCON's `irgen.icn`
deliberately doesn't encode (JCON just emits a generic `ir_opfn`/`ir_Call` and defers semantics to its own
runtime, exactly as SCRIP's templates defer to `rt_*` helpers — **never reimplement value semantics inline in
a template; call/mirror the existing `rt_*` helper, or if none exists, the `.r` file tells you what that
helper needs to do**). The useful extraction from a `.r` file is almost never the whole function — it's the
ONE structural fact that disambiguates an implementation choice: this session's two uses were (a) `oasgn.r`'s
`GeneralAsgn` `default:` arm showing assignment is type-uniform once the destination's *address* is resolved
(`Asgn(x,y)` = `*VarLoc(dest)+Offset(dest) = src`, no type-casing at the store), which told us the global-vs-
local distinction must live in ADDRESS RESOLUTION (a template/driver concern), not in assignment semantics
(never needs its own per-kind logic); (b) `rmacros.h`'s `VarLoc`/`Offset` macros confirming a Icon "variable"
descriptor is self-locating regardless of storage class, which is the running theory for why SCRIP's existing
`bb_var_global.cpp`/`bb_gvar_assign*.cpp` family (12 templates, pre-existing, NOT new) already has the right
shape — it just isn't reachable from the new flat-chain driver yet (see GVA-FLAT rung below). Match the genre
of fact you need (control-flow shape vs. value semantics vs. storage-class resolution) to the genre of source
(`irgen.icn` vs `gen_bc.icn` vs `*.r`) — don't read all three cover-to-cover for every TT; **read the chunk
list first, and reach for the `.r` file only when a *specific* implementation choice is actually ambiguous.**

### Step 4 — BEFORE writing LOWER code, grep the CURRENT SCRIP state for the TT
`grep -n "case TT_X:" src/lower/lower_icon.c` and `grep -n "case IR_X" src/emitter/emit.cpp` (note: TWO
`emit.cpp` switches exist — `walk_bb_node`'s TEMPLATE SELECTOR switch and `emit_drive`'s DRIVER switch; a TT
can be live in one and stubbed/missing in the other, which is exactly what the global-assign bug turned out to
be). **Do not assume the punch list's prose is the ground truth for what's broken — it can be stale, and was
this session** (see CORRECTIONS below). Always re-derive from a fresh `gdb` repro + the actual switch
statements before designing a fix. The RULES.md MONITOR-FIRST methodology (bracket via a real crash/gdb
trace, not by reading code and guessing) is not optional even for "obviously" missing cases — this session's
global-assign investigation found a SECOND, upstream, more severe bug (a universal segfault, not the
documented "abort") purely because the repro was run before the fix was designed, not after.

### Step 5 — the 3-FILE EDIT RECIPE (already in the playbook above) applies; ADD: check for PRE-EXISTING
**infrastructure under a different driver mode before writing a new template from scratch.** This session
found `bb_gvar_assign.cpp` (legacy `!g_descr_flat_chain` driver, fully built, untested-but-presumably-working)
and `bb_var_global.cpp` (the flat-chain-NATIVE read-side counterpart, already correctly shaped). The
write-side flat-chain-native template does NOT exist and should be a fresh file MIRRORING `bb_var_global.cpp`'s
shape (dual-path: `[rbx+gva_k*16]` fast path when slot-allocated, `NV_SET_fn(name, DESCR_t)` runtime-call
fallback otherwise) rather than either (a) trying to reuse `bb_gvar_assign.cpp` as-is (wrong shape — it expects
raw `op_a_node_kind` node-shape introspection, the OLD driver's idiom; the flat-chain driver instead
pre-resolves every operand to a `tmp`-backed slot via `IR_t.tmp`/`drive_value_slot`, so the new template should
consume `op_a_slot`, not re-derive the producer's shape) or (b) writing global-assign from a blank page (most of
the addressing logic — `RDQ("rbx", k*16)` vs `FRQ(slot)`, the `g_gva_active`/`op_gva_k` gating — already exists
correctly in sibling templates and should be copied, not reinvented).

## ⏸ CVA — CONVERT-FOR-ARITH LADDER — **DEFERRED (Lon directive, 2026-07-02, same day as opened): ON HOLD until known-type information exists in the system; to be revisited as the future typed/untyped + boxed/unboxed data-type enhancement ("I might be totally wrong about that one" — the optimization depends on type knowledge LOWER doesn't have yet). No CVA rung may be started without Lon re-opening this section. The ladder text is RETAINED below for that day; the EMPIRICAL TRIGGER's live bug stands INDEPENDENT of the deferral — promoted to STANDING AUDIT TARGETS.**
Original directive (2026-07-02) — hoist numeric coercion into its own BB; arith/relop boxes become pure inline int/real:
**THE EMPIRICAL TRIGGER (this session, m3+m4):** `x:="3"; write(x+2)` prints **58996226** — bb_binop_arith's int fast path guards ONLY `tag != DT_DATA` (je slow L(0)), so a runtime DT_S (or dynamic DT_R) operand falls into the inline integer arm and **adds the pointer/double bits**; `"2.5"+1` likewise; `"10">9` "passes" by pointer-compare (wrong mechanism). This ladder is therefore a **CORRECTNESS fix that keeps (and completes) the inline fast path**, not merely an optimization — though the benchmark payoff is the point.
**CANONICAL SEMANTICS (pinned fresh from refs/icon-master/src/runtime, 2026-07-02):** oarith.r per-op ladder = `cnv:(exact)C_integer(x)` → large-integer → `cnv:C_double(x)` → **runerr 102** ("3" exact-converts to int; "3.0" does NOT — falls to double); mixed operands promote to double. ocomp.r numcmp: numeric relops convert BOTH by the same ladder and **return the CONVERTED y** (string comparison is the separate `<<` lexcmp family — `<` on non-convertible is runerr 102, never lexcmp). cnv.r `ston` grammar: spaces, sign, digits, optional fraction/exponent, **radix `NNrDDD`**. Known SCRIP-side divergence candidates to pin (not silently change) in CVA-0: error-102/201 vs FAILDESCR idiom; radix support in the current coercer; no large integers.
**THE ARCHITECTURE (Lon's shape):** a CONVERT box normalizes each non-statically-numeric operand to {DT_I, DT_R} ONCE, so downstream arith/relop templates dispatch on a closed 2-tag set with zero RT calls in the numeric steady state; string parsing happens in ONE runtime fn on the cold path only. **NO-DUP resolution built in:** today inline-int-add (template) + rt_num_arith int-add (RT) is a pre-existing DUP FORM 1; the end state splits ownership — tag-dispatch + int/real machine ops = TEMPLATE (the sanctioned per-medium/per-op encodings of one logic); string→numeric parsing = `rt_cnv_num` ONLY. **Language-blind:** DESCR tags are the shared contract; no `IR_LANG_*` anywhere.
- [ ] **CVA-0 SEMANTICS PIN** — oracle-pinned probes BEFORE code (today's pointer-arith outputs are the floor): `"3"+2`=5 · `"2.5"+1`=3.5 · `"3"*"4"`=12 · exactness `"3.0"+0` real · relop converted-y `write("10">9)`→9, `write(3<"7.5")`→7.5 · div/mod-by-zero current-behavior pin · non-numeric `"abc"+1` (canonical errs 102) · radix `"16rff"+0`=255 (expected-divergence flag if the coercer lacks it).
- [ ] **CVA-1 `rt_cnv_num`** — ONE conversion fn (the ston ladder: exact-int else double else fail-marked), extracted so `rt_num_arith`/`coerce_numeric` DELEGATE to it — no second parser anywhere.
- [ ] **CVA-2 `IR_CNV_NUM` + `bb_cnv_num.cpp`** — classify-by-name, one template: inline tag test, DT_I/DT_R pass through (2×8 copy to own slot), else `call rt_cnv_num`; non-convertible → ω with the pinned error idiom. Emitted only where needed (CVA-3), so pass-through cost ≈ 2 movs + 1 predictable branch.
- [ ] **CVA-3 LOWER INSERTION** — arith/relop/numeric-unop operands get a CNV_NUM producer UNLESS statically numeric: IR_LIT_INTEGER/IR_LIT_REAL **or any producer that is itself numeric-closed (arith/unop-neg output ∈ {I,R})** — so `x*x + y*y` converts only at the leaf reads; interior chain nodes need nothing.
- [ ] **CVA-4 ARITH INLINE COMPLETE** — bb_binop_arith re-guarded on the post-CVA contract: both DT_I → existing inline int ops (zero-test inline for div/mod, current fail semantics preserved); mixed/real → inline cvtsi2sd promote + SSE addsd/subsd/mulsd/divsd result DT_R; DT_DATA → the existing rt_binop_overload arm; the `!=DT_DATA` pointer hole DEAD BY CONSTRUCTION. POW may stay RT. Delete/delegate RT's now-cold two-numeric arm (the NO-DUP payoff).
- [ ] **CVA-5 RELOP** — bb_binop_relop same 2-tag inline treatment + canonical converted-y yield (success result = converted operand[1] value); numeric-required semantics per ocomp.r (lexcmp stays `<<`-family only).
- [ ] **CVA-6 UNOP** — `-e`/`+e` ride the same converts; inline neg for DT_I (neg) / DT_R (xorpd sign-bit).
- [ ] **CVA-BENCH** — tight-loop probes (variable-operand int sum, real accumulate, string-fed leaf) timed m3+m4 before/after; numbers into the Watermark. THE POINT.
- [ ] **CVA-FENCE** — grep-gate: no template reaches rt_num_arith for a two-numeric case; rt_cnv_num is the only string→numeric parser; audit + corpus green with the CVA-0 probes as the new floor.

## Watermark
**2026-07-02 (session, Claude Fable 5) — SCRIP `c76ce21d`: IDX-UNIFY r1 tvsubs LANDED — IDX-UNIFY sub-rung ladder COMPLETE (r1-r4 all closed). `s[i]` is a string lvalue: `IR_VAR_REF` classify-by-name variable-reference producer (DT_V over the variable's cell, GVA/local lea arms, `bb_var_ref.cpp` + `rt_var_ref_cell`); DT_V flows through subscript chains (`rt_subscript_var` derefs DT_V bases internally per canonical subsc — between-level IR_DEREFs retired, `t[k][i]:=v` lvalue-correct via lazy ssvar); `VCELL_t`+`{sv,pos,len}`; rt_deref/rt_assign_var tvsubs arms per cnv.r:482/oasgn.r:345 (recursive write-back collapses canonical's type_case; trap-len update = revassign β-restore correctness). One wiring bug (nested TT_IDX base lost the variable through the rvalue DEREF wrapper) caught by probe 83, fixed by self-recursion. Fresh-sandbox baseline re-derived FIRST and matched the prior close exactly (icont 9.5.25a rebuilt from upload, refs/ symlinked, audit 81/81). Post-rung: audit 81→**84/84 both modes** (probes 82/83/84 oracle-pinned) · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (comm empty) · bench-asm 13/0/0/1/12 updated=0. **TMP-ERADICATE rung OPENED (Lon directive) with executed survey + TE-0..TE-FENCE ladder** — see its section; key findings: eradication half-landed (`ir_drive_slot_assign` + the drive_value_slot abort), survivors = 15 alloc16 + 14 claim sites (Icon-reachable core = the bb_call* argv family, TE-1), `ir_tmp_slot_assign{,_flat}` are DEAD, varslot cursor = the third counter (TE-4). Open board: TE-1 call-family grant · computed-cset scan operands · pointer-hole fix architecture (Lon).**

Prior: **2026-07-02 (new session, Claude Fable 5) — SCRIP `c34d4125`: IR_MOVE DELETED (Lon verdict) — RESERVED-SET RECONCILE CLOSED, all rows resolved. Tmp-doctrine absorption RATIFIED vs JCON ir_Move (gen_bc:220); only client copy_prop.c/.h (unexercised, zero live material) deleted wholesale with it (Makefile source-list + object rule, optimizer.c cp_run/stats arm); residual grep IR_MOVE|cp_run|copy_prop = 0, IR_MOVE_LABEL untouched (word-bounded census, exactly 3 sites). Fresh-sandbox baseline re-derived FIRST (icont 9.5.25a oracle rebuilt from upload, refs/ symlinked per RULES.md recipe, x64 cloned) and matched the prior close exactly before cutting. Audit 81/81 both modes · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (comm empty vs pre-rung capture) · bench-asm 13/0/1/12 updated=0. Open board: IDX-UNIFY r1 tvsubs · computed-cset scan operands · pointer-hole fix architecture (Lon).**

Prior: **2026-07-02 SESSION CLOSE (Claude Fable 5) — two rungs landed: IDX-UNIFY r2 subscript-revassign (SCRIP `fba88eae`, IR_REV_ASSIGN_VAR, probe 80) · TT_CSET_COMPL silent no-op killed (SCRIP `bf7f9392`, rt_cset_compl, probe 81). Audit 79→**81/81 both modes** · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical throughout · bench-asm 13/0/1/12 updated=0 every rung. CVA convert-for-arith ladder authored then **DEFERRED same day (Lon)** — held for the future typed/untyped + boxed/unboxed enhancement; its empirical finding (inline-arith POINTER HOLE, `"3"+2`→58996226) promoted to STANDING AUDIT TARGETS as a live bug independent of fix architecture. Findings also filed: scan boxes are literal-cset-only (own future rung); cset `\0`-universe divergence flagged. Open board: IR_MOVE verdict (Lon) · IDX-UNIFY r1 tvsubs · computed-cset scan operands · pointer-hole fix architecture (Lon).**

Prior: **2026-07-02 (session, Claude Fable 5, second rung) — SCRIP `bf7f9392`: TT_CSET_COMPL (`~e`) SILENT NO-OP KILLED — real IR_UNOP arm + `rt_cset_compl`; probe 81 oracle-pinned 4-way (membership, involution, `**`-composition; absolute-count assertions avoided per the flagged `\0`-universe divergence). FINDING goal-filed: scan boxes are literal-cset-only (computed-cset scan operands = own future rung; bare-call upto = pre-existing rung06 FAIL). Audit 80→**81/81 both modes** · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (comm empty) · bench-asm 13/0/1/12 updated=0. Session total 2 rungs (r2 subscript-revassign `fba88eae` + this). Next rung: Lon's call (IR_MOVE verdict; IDX-UNIFY r1 tvsubs; computed-cset scan operands now also on the board).**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `fba88eae`: IDX-UNIFY r2 LANDED — subscript-revassign `x[i] <- v` via `IR_REV_ASSIGN_VAR` (through-variable sibling of IR_REV_ASSIGN; IR_ASSIGN_VAR operand order; canonical rasgn on the phase-1 rt_deref/rt_assign_var rails; bb_rasgn.cpp's dormant pre-doctrine subscript arm deleted). Probe 80 oracle-pinned 4-way incl. the absent-key restore fork (key stays PRESENT at default, `*u`=1). One in-session splice bug (emit_drive insertion ate `case IR_GOTO:`, loop family op=20 FATAL) found by the audit and fixed with full re-verify. Audit 79→**80/80 both modes** · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical (stash comm empty) · bench-asm 13/0/1/12 updated=0. Next rung: Lon's call (IR_MOVE verdict; IDX-UNIFY r1 tvsubs).**

Prior: **2026-07-02 (continuation session, Claude Fable 5) — SCRIP `2ae6155d`: r10 PREAMBLE RESIDUE DELETED (standing target reconciled) — both mediums' flat preamble loaded &Δ into RETIRED r10 with zero readers (text lea ×2, binary raw-byte movabs ×2 in the legacy xa_flat; hand-counted out_site patch offsets decremented in step — smoke m3 = the byte-surgery acid test). Δ the C global stays live; only the dead courier died. Preamble now = GOAL-ICON-BB premise shape exactly. Audit 79/79 · smoke 12/12×2 · 4 gates PASS · HARD=4 · corpus 205/48/36 FAIL set byte-identical · bench version.s honest-churned (corpus `48fb69bb`). Session running total (4 rungs): clobber audit (2 live fixes) · IDX-UNIFY r4 stale-struck + strong probe 78 · r3 comma form landed (probe 79) · r10 residue. Next rung: Lon's call (IR_MOVE verdict; IDX-UNIFY r1 tvsubs / r2 subscript-revassign).**

Prior: **2026-07-02 (continuation session, Claude Fable 5) — SCRIP `df46db00`: IDX-UNIFY r3 + r4 CLOSED — r3 `x[i,j]` comma form LANDED (`df46db00`: one-arm parser change, dormant lower_idx_var chain took it first try, probe 79 read/write-through/mixed-table→list oracle-pinned) · r4 `*t` table-size STRUCK STALE (`ed10358e`: re-derived fresh, `*t`/`*L`/`*"s"` all correct both modes; payload cashed as probe 78, the STRONG fork discriminator — pure read never inserts, pinned at full strength). Audit 79/79 both modes · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 205/48/36 FAIL set byte-identical across both rungs · bench-asm 13/0/1/12 updated=0. IDX-UNIFY remainder: r1 tvsubs · r2 subscript-revassign. Next rung: Lon's call (IR_MOVE verdict open).**

Prior: **2026-07-02 (continuation session, Claude Fable 5) — SCRIP `dde4e9fd`: CLOBBER-PATTERN AUDIT EXECUTED (the 2026-07-01 standing target) — two LIVE bugs fixed: runtime LIMIT count via op_sc slot (probe 77; `e \ k` had silently yielded nothing) · string-literals-mislabeled-csets via the IR_t anonymous-union ival↔sval alias in bb_lit_scalar's STRING-arm vestige (every string lit, both modes). Three dead stagings removed; all surviving pre-fill stagings verified redundant-but-equal by construction. Audit 77/77 both modes · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 200/53/36 → 205/48/36 (five FAIL→PASS, all string-vs-cset discriminators — the mechanism's fingerprint; ZERO new fails) · bench-asm 13/0/1/12 updated=0. Next rung: Lon's call (IR_MOVE verdict open; IDX-UNIFY sub-rungs r1–r4 standing).**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `264c3994`: IDX-UNIFY PHASE 1 LANDED — x[i] is a real LVALUE (option ii mini-trapped-var; IR_ASSIGN_VAR name confirmed against Lon's criterion). Audit 76/76 both modes · smoke 12/12×2 · 4 gates PASS · mutation HARD=4 baseline · corpus 194/59/36 → 200/53/36 (six FAIL→PASS, ZERO new fails) · bench-asm updated=0. Two wiring bugs found-and-fixed via the corpus diff (cx->beta clobber; emission-walk ω-follow holes — latent for sections too). Remaining sub-rungs in the IDX-UNIFY entry: tvsubs · subscript-revassign · x[i,j] parser · *t table-size gap. Next rung: Lon's call.**

Prior: **2026-07-02 (session, Claude Fable 5) — SCRIP `46c1923a`: IR_SEQ_EXPR → IR_CONJUNCTION rename LANDED (Lon directive; see the re-named CONJ-RENAME entry above for the shared-case-body record). Byte-identical by 291-program emit manifest; audit 71/71 both modes · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation HARD=4 baseline · bench-asm 13/0/1/12 updated=0 · corpus fresh post-rename run PASS=194 FAIL=59 XFAIL=36 /289 (identical to pre-rename watermark counts, as the manifest proof requires). Next implementation rung: IDX-UNIFY (survey + RECON 2 recorded above; table-semantics fork awaits Lon).**

Prior: **2026-07-02 (continuation session, Claude Fable 5) — SCRIP `87ab07c4`: CONJ-RENAME rung CLOSED, four commits — CONJ-0 probes `7ed39fcb` (genuine-`&` oracle-pinned, audit 68→71) · IR_GOTO split `980d7946` (six junction sites, operand pushes dropped) · IR_CONJ→IR_SEQ_EXPR `633dc295` (value-forwarding join; conjunction = edge wiring, not a node) · TT_CONJ `87ab07c4` (Icon `&` gets its own AST kind; shared TT_SEQ left to peers). Every rung: audit 71/71 both modes · smoke 12/12×2 · corpus 194/59/36 FAIL set byte-identical (comm) · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation HARD=4 baseline · bench-asm 13/0/1/12 updated=0. ICON-ONLY scope prose corrected in this file (lower_raku/lower_pascal ARE built). Next implementation rung: IDX-UNIFY (survey already recorded above).**

Prior: **2026-07-02 SESSION CLOSE — SCRIP `ed0ac777`: four commits this session — TO-SPLIT `7dd2baf7` (IR_TO/IR_TO_BY, JCON-ALIGNMENT rung 1) · IR_MAKE_LIST `138c64dc` (rung 2, by-name MAKELIST route retired for Icon) · IR_RESUME_VALUE DELETED `ed0ac777` (Lon directive; reservation spent) · IDX-UNIFY SURVEY recorded (rung open; FINDING: x[i]:=v is today an IR_FAIL placeholder). Every rung: audit 68/68 both modes · corpus 194/59/36 FAIL set byte-identical (stash comm) · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation HARD=4 baseline · bench-asm 13/0/1/12 unchanged. CONJ-RENAME rung opened (Lon names it). Next implementation rung: IDX-UNIFY.** Prior same day: IR_MAKE_LIST LANDED (JCON-ALIGNMENT rung 2) — dedicated opcode replaces the by-name MAKELIST string route for Icon; JCON ListConstructor chaining; variable slot grant (result + contiguous argv scratch); `rt_make_list` extracted, by-name arm delegates. Probe 50 OK 4-way · audit 68/68 both modes · corpus 194/59/36 FAIL set byte-identical · smoke 12/12×2 · all gates green · mutation HARD=4 baseline · bench-asm unchanged. Next ladder rung: IDX-UNIFY (route TT_IDX → IR_SUBSCRIPT 2-operand, lvalue+rvalue, retire lower_call("[]"); unblocks arr[i] <- v; the IR_DEREF partner).** Prior same day: TO-SPLIT LANDED (IR-LAYOUT JCON-ALIGNMENT rung 1) — `IR_TO`/`IR_TO_BY` split per spec + 3 unspec'd mirror sites (rhs_kind_ok, write_route, chain_arity); bb_to constant-by helper proven DEAD and by=1 baked byte-identical; IR_RESUME_VALUE NOT needed (reservation spent, back to Lon). Audit 68/68 both modes (34/35 hold, negative-by hand-checked m3==m4) · corpus 194/59/36 FAIL set byte-identical (stash `comm` diff empty) · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation HARD=4 baseline · bench-asm 13/0/1/12 unchanged (updated=0). Next ladder rung: IR_MAKE_LIST.** Prior: **2026-07-02 SESSION CLOSE — SCRIP `65f8c32e` (push pending): five rungs this session (slot-collision a0b3f410 · unop-else ca31f6e2 · loop-α-restamps b3d41c74 · renames 65f8c32e) + probes 67/68 · audit 68/68 · corpus 194/59/36 · bench-asm re-verified post-rename 13/0/1/12 · reserved-set reconcile EXECUTED: IR_SCAN_SWAP + IR_UNREACHABLE + IR_EXEC-macro DELETED (`7138de96`), IR_DEREF kept as the IDX-UNIFY partner, IR_MOVE/IR_RESUME_VALUE pending Lon. Opening rung next session: TO-SPLIT. IR_FIELD_GET + IR_INITIAL renames (JCON-alignment directive opened — see its section). Prior `b3d41c74`: loop-family PRODUCE-edge α-restamps LANDED (EXPORTABLE RULE sites 5-7; probe 68 — audit **68/68 both modes**). Prior rung `ca31f6e2`: failing unary-test-op else-routing (BFS ω-following UNOP pair; probe 67). Prior rung same session `a0b3f410`: proc-local varslot/tmp SLOT COLLISION fixed (universal — every proc with `local` had its first locals aliasing the first value-producer tmps; relop return-y writes clobbered them). Corpus 190→194/59/36 of 289** — stash/rebuild `comm` diff = exactly +4 FAIL→PASS (rung03_suspend_{gen,gen_compose,gen_filter}, rung36_jcon_statics), ZERO PASS→FAIL · audit 66→**67/67 both modes** (probe 67 added) · smoke 12/12×2 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · mutation gate **HARD=4** (pre-existing baseline) · icont/iconx oracle live · bench-asm baseline 13/0/1/12. Prior rungs same day: `a3de01d2` (`22_revassign`, AUDIT LADDER COMPLETE + operand_aux API deleted + IR_REV_ASSIGN/IR_SUBSCRIPT renames), `c0e74d52` (`54_section_plus`).

### Landed history (compressed 2026-07-01 per RULES.md "DELETE completed steps" — full narratives in `git log` + `.github/HANDOFF-2026-0*.md`)
- **Foundations (06-30):** CONVERSION PLAYBOOK + `TT_EVERY` keystone · IR_ref_t α/β edge-stamp (`bb70a841`) · ICON-ONLY hard rules · `IR_ALT` deleted repo-wide (alternation = pure threading) · repeat/break/next via the IR_CONJ loop-back idiom · unop operand-push fix (`2d2b1ec8`) · universal `op_sval`/`gva_index_of` segfault fixed (`baa3a592`) · GVA-FLAT global assign (`feab99c7`) + slot-collision fixes (`024abd2f`, `d225d4a2`) · the every/TO/TO_BY regression cycle — fixed at HEAD, oracle-confirmed · scan-builtin opcodes TAB/MOVE/UPTO/ANY/MANY/FIND/MATCH/POS/BAL · IR_FIELD_SET / IR_PROC_GEN / IR_SUSPEND incl. binary-mode resume slots (`44c0da…`) · TT_IDX/MAKELIST union-clobber fixed (`8e296381`).
- **Opcode hygiene (07-01):** IR_TERNOP→IR_SECTION · IR_SUBSCRIPT / IR_GOTO / IR_NOT / IR_*_GENERIC deleted · four-opcode can-fail grid (IR_UNOP / IR_UNOP_TEST / IR_BINOP / IR_BINOP_TEST; the `_GEN` axis REJECTED per the DIVISION RULE) · `=s` desugared to `tab(match(s))` per `omisc.r:84` · prove_lower retired.
- **OPTIMIZER stage (07-01, `18a3440e`):** `src/optimizer/` between LOWER and EMITTER, `SCRIP_OPT`-gated OFF; branch_chain + copy_prop built (open items → PUNCH LIST standing targets).
- **Co-expressions (07-01, RUNGs 1-5):** create/coret/cofail pthread+semaphore model (`rt_coexpr.c`), `@` activation end-to-end both modes; three bring-up bugs gdb-bracketed (uninitialized create fields, bb_create k=5 clobber of the staged body-entry, coret γ→chain-default).
- **Label-variable infra (07-01, `dc45d9e2`):** IR_INDIRECT_GOTO re-added + IR_MOVE_LABEL; ig-owned shared 32-byte cell (value + `t`), t0-port sibling-label LEA; unbounded alternation `every write(1|2|3)` → `1 2 3`; corpus exactly +9; also fixed literal-arm ω-cascade discoverability and runtime-failing-arm0 value convergence.
- **Wholesale audit (07-01):** 66-probe icont-oracle instrument built · csetlit/&line/&pos/LIMIT (9 root causes) → 60/66 · initial + lconcat → 62/66 · repalt (`7edb9b9a`: `flat_drive_repalt` built — the phantom exorcised — + three β-mis-stamp PRODUCE-edge fixes + IR_REPALT `k+=2` grant) → 63/66 · if_value_else → **64/66** (SCRIP `6a509382`).
## ⛔⛔ WHOLESALE FROM-SCRATCH VERIFICATION — the executable audit + first fix ladder (Claude Sonnet, 2026-07-01, continuation session)

**Lon's directive verbatim-in-spirit: "do not trust any of it. We need to start the list from scratch and run through a one by one verification step. We are missing and are doing some thing wrong."** This session built the from-scratch list as an EXECUTABLE instrument, ran it, and fixed the first 4 construct families it caught (9 distinct root causes). The instrument is the head start for every future rung AND for the other-language LOWER/EMITTER rewrites.

### THE TECHNIQUE — what, where, when, why, how
- **WHERE:** `SCRIP/scripts/audit_jcon_wholesale.sh` + `SCRIP/test/icon/jcon_audit/NN_name.{icn,.expected}` (66 probes).
- **WHAT:** one minimal probe per JCON `ir_a_*` (all 43 — count re-derived fresh by `grep '^procedure ir_a_' refs/jcon-master/tran/irgen.icn`, matching the prior session's corrected 43; CoexpList excluded, JCON itself punts) plus SCRIP-specific TT extras (swap, revassign, augop, lconcat, scan suite, seq_expr, &pos, string subscript). Each probe runs **4-way**: canonical **icont/iconx ORACLE** vs hand-derived **EXPECTED** vs **MODE-3** vs **MODE-4**. Truth = oracle output when the oracle compiles the probe, else expected; oracle≠expected ⇒ **PROBE-BAD** (the probe is wrong, not SCRIP).
- **WHY the oracle:** hand-expected values drift and encode the author's misconceptions. The oracle caught TWO probe-suite bugs before they could masquerade as SCRIP bugs: (a) declarations joined with `;` — declarations are not statements, rejected by SCRIP AND standard Icon; use a NEWLINE between `end`/`global`/`record`/`invocable` and the next declaration (statements inside bodies stay `;`-separated for SCRIP); (b) icont flag order is `icont -s -o OUT FILE`.
- **HOW to build the oracle:** `cd <icon-master> && make Configure name=linux && make` → `bin/icont`,`bin/iconx` (this session: the uploaded `2-icon-master.zip`, extracted at `/home/claude/workspace/refs-src/icon-master`; a backgrounded make stalled at src/common — foreground retry completed in ~2 min). Harness auto-probes that path + `SCRIP/refs/icon-master/bin/icont`; override with `ICONT=`.
- **HOW to run/extend:** `bash scripts/audit_jcon_wholesale.sh [name-filter]`. To extend: drop `NN_name.icn` + `NN_name.expected` in the audit dir. Verdicts: OK / M3-or-M4 BAD / HANG / CRASH / NOASM (--compile aborted) / NOCC (gcc failed) / PROBE-BAD.
- **WHEN:** per-rung, before AND after — it is cheap (~40s), per-construct, and oracle-anchored, unlike the corpus (feature-rung-organized) and smoke (12 fixtures) suites.

### THE CLOBBER PATTERN — systemic, now named (~~audit target for next session~~ **EXECUTED 2026-07-02, SCRIP `dde4e9fd` — see the struck STANDING AUDIT TARGETS entry for the findings record; the technique below stays for the other-language rewrites**)
`DRIVE_FILL` order is: emit_drive stages `g_emit.*` → `walk_bb_node` RE-DERIVES `op_sval`/`op_ival`/`op_stno`/`op_dval` from the node → template reads. **Any emit_drive staging of those four fields for an opcode outside walk's derivation lists is silently discarded.** Two instances found this session (CHARSET sval, LIMIT ival). NEXT-SESSION AUDIT: diff every `g_emit.op_{sval,ival,dval}` assignment inside emit_drive cases against walk_bb_node's preamble lists; each mismatch is a live or latent bug of this class.


**Status + remaining ladder: single source = the Watermark and the PUNCH LIST above; ground truth = the harness itself.**
