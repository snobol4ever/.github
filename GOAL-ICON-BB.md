# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ⛔⛔ GROUND ZERO 3 — STACKLESS REBUILD (Reset 2026-05-30) ⛔⛔

**This is the THIRD ground-zero reset. The premise that was wrong both prior times: a value stack.**

There is NO value stack. Not an SM value stack, not a `vstack`, not `r12`-as-TOS, not
`rt_push_*`/`rt_pop_*` for Icon value flow. A complete stackless static SNOBOL4/Icon BB
emitter existed ~1.5–2 months ago (archived at `one4all/archive/backend/emit_emitters/emit_x64.c`)
and benchmarked **faster than SPITBOL precisely because there is no stack**. The current
mode-3 Icon path regressed by making an SM value stack the inter-box value mechanism
(`rt_push_int` ×39, `rt_pop_nv_set` ×21, underflow guard in `rt.c`). GROUND ZERO 3 rebuilds
from `write("hello")` upward on the stackless model and never reintroduces the value stack.

**The stackless model (verbatim from the archive + the references):**
- **Values live in flat per-box DATA slots**, addressed at stable emit-time addresses
  (the existing `&pBB->value` / `&pBB->counter` / `&pBB->state` idiom). `emit_x64.c:10` —
  *"All pattern variables live flat in .bss as QWORD (resq 1) slots."*
- **Value flow is static wiring, not push/pop.** A box writes its result into its OWN slot;
  a consumer reads its operand boxes' slots directly (operands are known at emit time via
  α/β). Proebsting `plus`: `plus.value ← E1.value + E2.value` — read children by name.
- **Backtrack state for unbounded depth = a per-box .bss ARENA**, not a global stack. ARBNO
  (`emit_arbno`, `emit_x64.c:932`) and recursion use a per-box frame array indexed by depth
  (`test_sno_1.c` `_1[64]`; `test_sno_3.c` lazy `enter()/ζζ` heap frame). NOT push/pop.
- **Inter-box transitions are direct `jmp`.** No `call`/`ret`, no dispatch loop, no walker.
- The hardware C stack (`rsp`) may be used ONLY as transient scratch inside a single node
  (e.g. protect an arithmetic operand across a nested sub-eval, as the archive does) — never
  to thread values between boxes.

**References (now in-repo at `one4all/refs/bb/`):**
- `Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` — the four-port templates
  (literal N §4.1, uminus §4.2, plus §4.3, LessThan §4.3, to §4.4, ifstmt §4.5). Figure 1/2
  are the exact target for `5 > ((1 to 2) * (3 to 4))`.
- `test_icon.c` — that same expression as flat C goto-graph, named-slot values, ZERO stacks.
  The byte-exact structural target for GZ-1..GZ-6.
- `test_sno_1.c` — SNOBOL4 ARBNO over alternation: the per-box `_1[64]` arena (the only stack).
- `test_sno_2.c` — recursion as four-port functions (`group`→`group`), `_λ` landing pads.
- `test_sno_3.c` — **the EVAL/CODE/`*P` deferred solution**: each deferred sub-pattern is a
  four-port function `str_t E(E_t **ζζ, int entry)`, frame lazily `calloc`'d by `enter()`,
  resumable at α/β, `empty` decoded as failure at `_λ`. This is the model for GZ-DEFER.
- `one4all/archive/backend/emit_emitters/emit_x64.c` — the prior working stackless emitter.

**NEW GATE (enforces stacklessness, parallel to the FACT gate):**
```bash
# Icon emission path must contain ZERO value-stack push/pop:
grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c \
  | grep -v _pl_ | wc -l        # target: 0 for every Icon box family as it is rebuilt
```
Plus the existing per-rung gate: `m2==m3` byte-identical, `--dump-sm` count=0 (zero SM),
FACT 0, smokes hold.

### Rung ladder (HELLO WORLD up — each gated, stackless, no `rt_push`/`rt_pop`)

- [ ] **GZ-0 — Scaffold + gates.** Pin the no-stack gate above into `scripts/`. Confirm the
  per-box slot idiom (`&pBB->value`) is the value-storage primitive. Decide the slot/arena
  conventions by reading `emit_arbno` + one full pattern-node body in the archived `emit_x64.c`
  end-to-end, and `test_icon.c` for the Icon arithmetic shape. No code change beyond the gate script.
- [ ] **GZ-1 — `write("hello")`.** One box, literal value in its own slot, write reads the slot.
  No push. m2==m3, zero-SM, no-stack gate = 0 for this box family.
- [ ] **GZ-2 — `write(42)`.** Literal-N template (PDF §4.1): `lit.start: lit.value ← N; goto succeed`.
  Value in `&lit->value`. write reads it.
- [ ] **GZ-3 — `write(1 + 2)`.** plus template (PDF §4.3): `plus.value ← E1.value + E2.value`,
  read from the two child slots. No operand push/pop.
- [ ] **GZ-4 — `every write(1 to 3)`.** to template (PDF §4.4): `to.I`, `to.value` slots; β
  re-pumps via `to.resume: to.I++`. Mirror `test_icon.c` `to1`.
- [ ] **GZ-5 — `every write(1 | 2 | 3)`.** alt: `α save cursor → left_α; left_ω → right_α`
  (archive ALT wiring). Choice index in a per-box slot.
- [ ] **GZ-6 — `every write(5 > ((1 to 2) * (3 to 4)))`.** The paper's full example. Must be
  byte-identical to `test_icon.c` output AND structurally mirror Figure 1 (nine four-port
  templates, no stack). This rung proves stackless generator-nesting end to end. MILESTONE.
- [ ] **GZ-7 — `x := 42; write(x)`.** Flat slot for `x` (the archive's flat .bss var model).
- [ ] **GZ-8 — `if`/relop control, relop routes its OWN γ/ω.** Bake the branch into the relop
  (PDF LessThan: `if (E1 ≥ E2) goto E2.resume`); NO `LAST_OK` flag, NO `BB_IF` flag-router.
  This is the reference-faithful form (the old IBB-9-RELOP-PORTS, done correctly from scratch).
- [ ] **GZ-9 — `while`/`until`/`repeat`.** body.success/failure → cond.START (JCON `ir_a_While`);
  `until` swaps the cond edges. No router node.
- [ ] **GZ-10 — user procedure as a four-port FLAT box** (not a C-stack `call`). Model on
  `test_sno_3.c`: `(ζζ, entry)` calling convention, frame lazily allocated, `_λ` landing pad.
  Recursion depth lives in per-box arenas / heap frames, never a value stack.
- [ ] **GZ-DEFER — EVAL / CODE / `*P` deferred patterns** via the `test_sno_3.c` model. This was
  the ONE thing that broke the prior stackless build; it is solved in the reference file.
- [ ] **GZ-11+ — corpus features rebuilt stackless** (lists, tables, records, scanning, csets,
  builtins, sort, ...). Each: read the canonical JCON/Icon source first, then a flat slot/arena
  template, gated m2==m3 + zero-SM + no-stack=0 + no corpus regression.

**The IBB-* rungs below are SUPERSEDED.** They are the vstack-based build and are kept only as
the historical record of what the regression looked like. GROUND ZERO 3 does not extend them.

---

**Reset:** 2026-05-28. All Icon legacy SM dispatch deleted. No env-gate `SCRIP_ICN_BB`. The BB-graph lowering is the only path. Every BB template MEDIUM_BINARY arm that isn't real ABORTs loudly at a named site.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7 · Claude Sonnet 4.6
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/jcon_irgen.icn` · `STUDY-JCON-ICON-CONTROL-FLOW-2026-05-29-OPUS48.md` (three-way control-flow comparison; basis for the IBB-9-2 rewrite + IBB-9-RELOP-PORTS).

---

## Premise

Icon IS a Byrd Box graph. Every construct is a box. The whole program is one connected port-graph. **There is no SM around it at all.**

- Mode 2: driver detects Icon and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `sm_interp_run` is never entered. Icon SM stream is empty.
- Modes 3/4: emit `lea r10, [rip + Δ_root]; jmp .Lroot_α`. `SM_HALT`. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in mode-4.

Per `test_icon.c`: every construct gets `_start` / `_resume` / `_succeed` / `_fail` labels wired by flat `goto`. Three-column form: `LABEL / ACTION / GOTO`. That is the target shape.

---

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes emitted for an Icon program.** No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, nothing. Driver calls `bb_exec_once(main_bb_graph)` directly.

Completion tests:
```bash
./scrip --dump-sm any_icon_program.icn        # ; SM_sequence_t  count=0
./scrip --dump-sm any_icon_program.icn | grep -c '^   [0-9]'   # 0
```

## ⛔ CONSULT CANONICAL SOURCES (JCON + Icon)

**Every time a question arises during new SM/BB or feature work — port topology, resume/backtrack wiring, builtin semantics — `grep`/read the relevant canonical procedure FIRST and ground the implementation in it.** Do NOT assume; you do not know until you check. Authority: `refs/jcon-master/tran/irgen.icn` (`ir_a_Every`, `ir_a_Limitation`, `ir_a_Call`, `ir_a_Alt`, … define control-flow/ports) and `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `ocomp.r`, `fscan.r`, … define runtime/builtin semantics). The mode-2 oracle `bb_exec.c` is a transcription, not the source of truth — when they disagree, the canonical source wins. Full statement in `RULES.md`. (Extract the uploaded `icon-master.zip` / `jcon-master.zip` into `refs/` at session start if not present.)

---

## Current state (2026-05-30, every ival=0 FIELD_SET-wrapped generator landed — corpus 166 PASS)

**Baseline note:** the authoritative number is the same-sweep over `/home/claude/corpus/programs/icon/*.icn`
(293 files; m2-OK filter; PASS iff m3 rc==0 && m2==m3 byte-identical):
**56 (pre-IBB-9-2) → 62 → 69 → 82 (IBB-9-6) → 93 (IBB-9-SIZE) → 95 (IBB-9-TOBY) → 100 (IBB-9-INITIAL)
→ 105 (IBB-9-CASE) → 130 (IBB-10) → 134 (IBB-11) → 140 (IBB-12) → 143 (IBB-9-4) → 148 (IBB-LIMIT) → 150 (max/min) → 152 (real TO_BY) → 165 (IBB-IDX) → 166 PASS after every ival=0 FIELD_SET.**
Latest sweep: Total 293, M2-skip 33, PASS 166, SEGV 1, ABORT 51, FAIL 1, MISMATCH 40.

**Landed this session (Sonnet 4.6, build+run verified, corpus delta verified, FACT 0, zero-SM, smokes 5/5·5/5):**
- every ival=0 FIELD_SET-wrapped generator (`every c.n := 1 to 3 do write(c.n)`) — `flat_drive_every` aborted with "ival=0 not yet flat-wired" because lower couldn't certify a streaming generator for a FIELD_SET lvalue (the lhs is not a plain var). Added a specialized ival=0 gate in `flat_drive_every` (emit_bb.c): when `pBB->α` is a `BB_FIELD_SET` whose `β` IS a recognized streaming generator (`icn_bb_is_gen_arg`), apply the JCON two-port split (ir_a_Every: body.success→expr.resume, body.failure→expr.resume): walk inner_gen (α->β, e.g. BB_TO) with γ=store_α, ω=outer_γ, β=gen_resume; at store_α walk object expr (lval_node->α) to push obj, FILL the field_set template (pops obj then value, stores field, vstack order correct: gen yielded value is deepest/rhs, walked obj is top); walk body with γ=ω=gen_resume. No new templates or rt helpers needed — byte-free driver. Newly passing: `rung24_records_record_loop` (+1, `every c.n := 1 to 3 do write(c.n)`). **IDX_SET-wrapped ival=0 deferred** (corpus coverage 0 currently; aborts loudly). Gates: FACT 0, bytes-outside-templates 12 (unchanged), zero-SM count=0, smoke icon/prolog 5/5, 0 regressions (LOST none vs IBB-IDX baseline).

**Prior state (2026-05-30, IBB-IDX subscript get/set landed — corpus 165 PASS)**

**Baseline note:** the authoritative number is the same-sweep over `/home/claude/corpus/programs/icon/*.icn`
(293 files; m2-OK filter; PASS iff m3 rc==0 && m2==m3 byte-identical):
**56 (pre-IBB-9-2) → 62 → 69 → 82 (IBB-9-6) → 93 (IBB-9-SIZE) → 95 (IBB-9-TOBY) → 100 (IBB-9-INITIAL)
→ 105 (IBB-9-CASE) → 130 (IBB-10) → 134 (IBB-11) → 140 (IBB-12) → 143 (IBB-9-4) → 148 (IBB-LIMIT) → 150 (max/min) → 152 (real TO_BY) → 165 PASS after IBB-IDX.**
Latest sweep after IBB-IDX: Total 293, M2-skip 33, PASS 165, SEGV 1, ABORT 53, FAIL 1, MISMATCH 40.

**Landed this session (Opus 4.8, build+run verified, exact corpus deltas, 0 regressions via full pass-list diff, FACT 0, bytes-outside-templates 12 unchanged, zero-SM, smokes 5/5·5/5, broker 61):**
- IBB-IDX — Icon subscript get `base[idx]` (BB_IDX) + set `base[idx] := rhs` (BB_IDX_SET). Both routed off the `bb_stub` no-op (emitted 0 bytes → enclosing write/assign printed empty / hit interp_eval) to new `bb_idx.cpp` templates (`bb_idx`/`bb_idx_set`, the proven no-arg `movabs rax,fn / call / jmp γ / β:jmp ω` 22-byte shape from bb_unop) + byte-free `flat_drive_idx_get`/`flat_drive_idx_set` drivers. Both topologies handled: TREE (α=base, β=index operand subgraphs — driver walks them; for SET, rhs on β->γ) and AG-PURE (α==β==NULL — operands already pushed by the enclosing γ-chain, just FILL). Runtime `rt_icn_idx_get`/`rt_icn_idx_set` (rt.c) pop the operands and dispatch through the shared `subscript_get`/`subscript_set` — the SAME helpers the mode-2 oracle calls → m2==m3 by construction. **slen-normalization bug found+fixed (same class as IBB-10):** `subscript_get` returns DT_S via `STRVAL(buf)` with slen=0; the mode-3 any-write trailer uses `fprintf("%.*s",slen,s)` → printed nothing. Traced to ground (probes: operands correct on vstack, result.s="h" correct, but slen=0); fixed by `r.slen=strlen(r.s)` in rt_icn_idx_get. `BB_IDX` added to `is_write_intexpr`/`arg_is_any` (bb_call.cpp) + `is_intexpr_shape` (emit_bb.c) so `write(s[i])` routes through the any-write trailer. Grounded in JCON `ir_a_Binop` (`[]` ∈ funcs set = single-shot, β→ω). Corpus 152→165 (+13): rung16_subscript_sub_{basic,fail,literal,neg}, rung13_table_{basic,delete,subscript_assign}, rung23_table_table_{basic,default,insert_delete,member}, rung35_table_str_str_{default_int_key,table_read}. Gates: FACT 0, bytes-outside-templates 12 (unchanged — driver byte-free), zero-SM count=0, smoke icon/prolog 5/5, broker 61, canonical 4/4, 0 regressions (clean-baseline pass-list diff: LOST none, GAINED 13).
  **NEW SEGV accounted (queens.icn):** moved from MISMATCH→SEGV. NOT a regression (was never passing; m2=419906 lines vs m3=1 at baseline). Root cause traced: `line := repl("|   ",n) || "|"` produces a slen=0 / "0"-valued string in m3 (pre-existing `repl`+`||` defect, out of IBB-IDX scope); the now-correct subscript-set then feeds a bad (DT_I) base to `subscript_set`, which calls `sno_runtime_error(3)` — and **mode-2 SEGVs identically** on a genuinely-bad subscript (`x[2]:="Q"` crashes rc=139 in BOTH modes), so the crash path itself is oracle-faithful. Fix belongs to a repl/concat goal. **Deferred (generator-bearing subscript, → IBB-9-4/5):** `s[1 to 3]` (rung16_subscript_sub_every) — index is a generator; single-shot IDX yields only the first value (pre-existing MISMATCH, not a regression). `key(t)` (rung23_table_table_key — BB_KEY_GEN still stubbed).

**Prior state (2026-05-29, IBB-LIMIT + max/min + real TO_BY landed — corpus 152 PASS)**

**Baseline note:** the authoritative number is the same-sweep over `/home/claude/corpus/programs/icon/*.icn`
(293 files; m2-OK filter; PASS iff m3 rc==0 && m2==m3 byte-identical):
**56 (pre-IBB-9-2) → 62 → 69 → 82 (IBB-9-6) → 93 (IBB-9-SIZE) → 95 (IBB-9-TOBY) → 100 (IBB-9-INITIAL)
→ 105 (IBB-9-CASE) → 130 (IBB-10) → 134 (IBB-11) → 140 (IBB-12) → 143 (IBB-9-4) → 148 (IBB-LIMIT) → 150 (max/min) → 152 PASS / 0 SEGV / 0 FAIL after real TO_BY.**
Latest sweep after real TO_BY: Total 293, M2-skip 34, PASS 152, SEGV 0, ABORT 50, FAIL 1, MISMATCH 56.

**Landed (Opus 4.8, build+run verified, exact corpus deltas, 0 regressions via full pass-list diff, FACT 0, zero-SM, smokes 5/5·5/5, broker 57):**
- real TO_BY — `lo to hi by step` with REAL literal bounds (`1.0 to 2.0 by 0.5`). mode-3 BB_TO_BY template only handled literal-INT; real fell to a yields-nothing stub → underflow. Added a literal-real arm (bb_to_by.cpp) driven by new `rt_icn_toby_real` (rt.c, mirrors mode-2 real arm w/ 1e-12 epsilon → m2==m3); plus real-only `BB_TO_BY` in `arg_is_any` (bb_call.cpp, gated sval[0]=='r') so `write(real to-by)` formats DT_R via real_str instead of printing raw IEEE bits (int TO_BY unchanged) → 150→152 (+2: rung19_pow_toby_real_toby_pos/neg).
- max/min builtins — added `max`/`min` to the `rt_icn_builtin_is_known` allow-list (the mode-2 oracle `icn_try_call_builtin_by_name` already handles both as multi-arg numeric; mode-3 `rt_icn_call_builtin` calls the same table → m2==m3) → 148→150 (+2: rung30_builtins_misc_maxmin, rung30_builtins_misc_mixed incl. real-valued).
- IBB-LIMIT — `gen \\ N` generator limitation (flat_drive_limit + bb_limit glue + rt_icn_limit_* ; α allow-list guard prevents silent-empty on unsupported sub-generators) → 143→148 (+5). Also fixed kind_names[] drift (--dump-bb mislabeled BB_LIMIT as BB_NONNULL; regenerated as designated initializers).
- IBB-9-4 — assign-wrapped ival=2 `every v := GEN do B` two-port split (JCON ir_a_Every) → 140→143 (+3). NOTE: a single-α first cut yielded only the FIRST element and gave a single-element FALSE POSITIVE on rung13_table_iterate; the landed fix threads the do-body re-pump into the inner generator's OWN β-resume (not the assign's β). Multi-element verified.
- IBB-12 — Icon `!E` list/table/record/string generator (BB_LIST_BANG) → 134→140 (+6)

**ATTEMPTED + REVERTED this session — BB_FIND_GEN (`find(needle,hay)`):** built a full 2-arg find generator
(rt_icn_find_gen mirroring mode-2 BB_FIND_GEN + canonical `refs/icon-master/src/runtime/fstranl.r` find();
bb_find_gen.cpp two-half template; flat_drive_find_gen walking α=needle, β=hay; emit_core/Makefile/header/
dispatch/bb_call wiring). Single-shot `write(find("b","abc"))` worked (→2 4, byte-identical, would be +1).
BUT the generator form `every write(find("a","banana"))` produced m3=`2` vs m2=`2 4 6` — find's β-resume
(reset=0) was NEVER reached through the intexpr re-pump. **This is the loud→silent regression class** (baseline
= underflow-ABORT; broken impl = silent-wrong MISMATCH, +1 to the mismatch gate), so it was fully reverted
rather than landed. **Diagnostics for next attempt (all confirmed):** (a) `every p := find(...) do write(p)`
WORKS in m3 via the IBB-9-4 assign-wrapper path → find's β-resume itself is correct; (b) `every write(!L)`
(BB_LIST_BANG, same flat_drive_call_intexpr path) WORKS, probe shows reset=1,0,0,0; (c) find probe shows
reset=1 ONLY — the re-pump exits after the first value; (d) deep-thread (dval==1.0) ruled out — is_suspendable
(TT_FNC)=1 so the find arg is not deep-threaded; (e) FILL correctly sets `_.lbl_β=arg_β` (doesn't read pBB->β).
The ONLY structural difference: BB_LIST_BANG has β=NULL (a free β control port) while BB_FIND_GEN packs the
hay operand into its β port (mode-2 puts all four ports as operands; "no spare control port"). **Canonical
authority for the fix:** `refs/jcon-master/tran/irgen.icn` `ir_a_Call` — builds the odometer `L:=[p.fn]|||args`,
threads `L[i].success→L[i+1].start`, `L[i].failure→L[i-1].resume`, and the call's own resume to
`L[-1].ir.resume` (the LAST arg's resume), re-running the Call each time the last arg yields. The next attempt
must reconcile BB_FIND_GEN's operand-occupied β port with needing a re-pumpable resume entry — likely a node
redesign (operands in the operand_aux sidecar per the PEERS rule, freeing β as a control port like
BB_LIST_BANG), grounded in ir_a_Call's resume topology.

**NEXT (largest residue, by the same-sweep after IBB-12):** the 62 ABORTs split into clusters.
(1) **`every` do-body ival=2/3** (`flat_drive_every: do-body ival=0/2/3 not yet flat-wired`) — the
generator-bearing two-port split (IBB-9-4/5); now also unblocks `every v := !t do B` (rung13_table_iterate),
`every c.n := 1 to 3 do` (rung24_records_record_loop), the rung10/rung13 augop-in-every mismatches. With the
`!E` generator landed, IBB-9-4 (the two-port every/do split) is the highest-leverage next step. (2) **I/O +
generator builtins** — `open`/`read`/`reads` (file-handle plumbing), `upto`/`max`/`point`/`push`/`put`
(generator or multi-arg builtins). (3) **`interp_eval stub`** — `sortf` (record-field sort comparator),
augop-in-some-contexts. The 56 mismatches are dominated by string scanning (`rung05_scan`, `rung06_cset`,
`rung08` match/move/tab) which need the BB_SCAN / cset-match generator path, plus subscript (`rung16` BB_IDX)
and table-subscript (`rung23`/`rung13` BB_IDX/IDX_SET).

---

## Prior state (2026-05-29, IBB-11 record field get/set landed — corpus 134 PASS)

---

## Prior state (2026-05-29, IBB-9-6 user-proc dispatch landed)

**Baseline note:** the authoritative number is the same-sweep over `/home/claude/corpus/programs/icon/*.icn`
(293 files; m2-OK filter; PASS iff m3 rc==0 && m2==m3 byte-identical):
**56 (pre-IBB-9-2) → 62 (IBB-9-2 etc.) → 69 (IBB-9-UNOP) → 82 PASS / 0 SEGV / 0 ABORT after IBB-9-6
(+13 this session, 0 regressions, worktree-verified).** The `bb_call: unsupported call shape` ABORT
cluster (~158 aborts = user-proc dispatch) is GONE.

| Mode | Path | Canonical (hello) | Full corpus (same-sweep, `c7529bad` base) |
|------|------|-------------|---------------------------------|
| 2 (`--interp`) | `bb_exec_once` C tree-walker | **pass** | oracle (m2-OK filter) |
| 3 (`--run`) | `bb_build_flat` → seal RX → call slab | **pass** | **56 → 62 PASS (+6), SEGV 0** |
| 4 (`--compile`) | deferred per Lon directive | hello.icn ✅ (`f387a7b9`) | n/a |

**Landed this session (Opus 4.8, all verified by build + run with exact before/after corpus diffs, 0 regressions, 0 SEGV, FACT 0, smokes 5/5·5/5·44/11):**
- IBB-9-2 relop-cond `while`/`until` (var/literal/pure-arith/assignment-rvalue operands) → +3
- IBB-9-SWAP `x :=: y` (two-`BB_VAR`) → +2
- IBB-9-ALTWRITE `write(ALT)` any-type fix (was pointer-garbage) → +1


**GATE METHODOLOGY (canonical, use this exact script every session):** same-sweep over `/home/claude/corpus/programs/icon/*.icn`: for each, run `--interp` (skip if rc≠0 — m2-OK filter), then `--run`; PASS iff `m3 rc==0 && m2==m3` (byte-identical). Count PASS / SEGV(rc=139) / ABORT(rc≥134) / FAIL(other). Baseline `30e7c0a1`=213 PASS; `e8f66866`=216. The earlier "22→28"/"28→46" rows used a NARROWER filter (subset dirs) — the 213/216 absolute counts are the whole-tree measure; trust deltas within one methodology only.

Canonical-5: `hello.icn`, `add.icn`, `every_to.icn`, `alt.icn`, `full.icn`. All byte-identical m2 vs m3.

Mode-3 corpus delta IBB-7 → IBB-8a: **+15 PASS (17→32), SEGV 2→0**. Two fixes: (1) xa_flat slab call-alignment (`sub/add rsp,8`) cleared the DT_R `fprintf("%g")` SEGV in `rung26_pow_pow_expr` + `rung37_augop_pow`; (2) DT_R-producing write args (BB_BINOP / BB_BINOP_GEN) now route through `rt_pop_write_any_nl` with canonical `real_str` formatting instead of the int-write trailer printing raw IEEE bits — fixed `rung26_pow_pow_assoc` and ~10 other real-valued write cases. Zero regressions.

ABORT breakdown after IBB-8a (~193):
- `bb_call: unsupported call shape` — non-write fn calls (user-proc dispatch), write(BB_CALL/proc result), write(BB_LIT_S in non-write fn) — main remaining cluster.
- `flat_drive_binop_tree: missing α or β child` — **relop in if-condition (~13). FULLY DIAGNOSED, see IBB-8b below.**
- `flat_drive_every: every-with-do-body` (~4).
- Two new SEGVs: `rung26_pow_pow_expr`, `rung37_augop_pow` — DT_R via `^`, fprintf(`%g`) inside slab. Pre-existing latent stack-alignment issue, exposed by IBB-7 progressing past the prior ABORT site. Both were ABORTing in baseline.

---

## Closed rungs

| Rung | Closed | Test | Commit |
|------|--------|------|--------|
| IBB-0 | Reset | — | — |
| IBB-1 | mode-2 hello | `write("hello")` | reset session |
| IBB-2 | Boot shape decision: zero SM, driver-level bypass | — | — |
| IBB-3 | mode-2 + mode-3 add | `write(1+2)` | `e612d519` |
| IBB-4 | mode-2 + mode-3 every-to | `every write(1 to 3)` | `fac53504` (bin-site reorder) |
| IBB-5 | mode-2 + mode-3 alt | `every write(1\|2\|3)` | `1a97c0a3` (counter-state dispatch) |
| IBB-6 | mode-2 + mode-3 full | `every write(5 > ((1 to 2)*(3 to 4)))` | `3aa200cd` (BINOP_GEN odometer) |
| IBB-7 | write(BB_VAR) + BB_ASSIGN flat-wire (AG-PURE deep-thread aware) | `x := 42; write(x)` byte-identical | `d1c55b0c` |
| IBB-1..32 (mode-2 only) | 22 programs verified zero-SM mode-2 | various | `936b8182` |

Mode-2 verified programs: write_str, arith, every_to/by, alt, conj, if, while, repeat, assign, augop, list-len, bang, idx, idx-gen, section, limit, user-proc, return, fail, table, cset, scan, scan-gens, recursion.

---

## Rungs

### IBB-8 (next) — DT_R fprintf SEGV + remaining mode-3 corpus

Two distinct fronts:

- [x] **DT_R fprintf SEGV** — CLOSED (IBB-8a, this commit). Root cause (gdb-verified): the flat BINARY slab is entered via the driver's `call fn(NULL,0)` at rsp%16==8, but `xa_flat_prologue` pushed nothing, so every internal `call *rax` to a runtime helper was made at rsp%16==8 → callees entered at rsp%16==0, one slot off the SysV ABI. Integer helpers tolerated it; `fprintf("%g")` faulted on its 16-byte-aligned `movaps %xmm0,-0x80(%rbp)`. Fix in `xa_flat.cpp`: `sub rsp,8` (48 83 EC 08) in the BINARY prologue before the esi-dispatch (so both α fall-through and β branch carry it; jne-β rel32 bin-site shifted +4), paired with `add rsp,8` (48 83 C4 08) before each `ret` in the BINARY epilogue (both succ and fail halves; fail-label bin-site tracks succ_half.size() automatically). Plus: `rt_pop_write_any_nl` DT_R branch now uses canonical `real_str` (matches mode-2 `9.0`/`1000000000.0`) instead of naive `%g`; and `bb_call.cpp` extended `arg_is_any` to BB_BINOP/BB_BINOP_GEN so DT_R-producing arithmetic routes through the type-aware any-write trailer (DT_I via %lld unchanged) rather than printing raw IEEE bits. Verified: `rung26_pow_pow_expr`, `rung37_augop_pow`, `rung26_pow_pow_assoc` PASS byte-identical; canonical-5 byte-identical + zero-SM; smokes 5/5/5/39; FACT 0; corpus 17→32, SEGV 2→0.
- [~] **relop in if-condition** — STRING relops DONE (IBB-8b, `0e926c16`); numeric/real relops still blocked on BB_LIT_F push (IBB-8c). **The IBB-8 diagnosis below proposed `flat_drive_if` walking a cond chain off the BB_IF node — that plan was WRONG: BB_IF has no field pointing back to the cond chain (PEERS RULE forbids adding one), and the cond chain is part of the ENCLOSING BB_SEQ, not owned by BB_IF.** Actual topology (verified by graph dump): `if (relop) then T else E` lowers to a branching CFG flattened into the BB_SEQ γ-chain — the relop (AG-pure, α=β=NULL, state=1) has γ==ω==BB_IF; BB_IF has γ=then-entry, ω=else-entry; with no else, BB_IF.ω points at the next statement (branches reconverge via fall-through, no join node). Mode-2's BB_SEQ oracle is itself a per-node CFG walk (γ AND ω both advance). **Implemented (not flat_drive_if):** (1) `flat_drive_seq` became a node-keyed CFG emitter — BFS from pBB->α following γ always + ω only for BB_IF, one arena label per node, emitted once, successors resolved via node→label map; non-IF nodes keep outer lbl_ω (matching baseline — resolving ω generally caused a SEGV regression by mis-wiring operand children, since tree-shape BB_BINOP / write-intexpr drivers walk their own children inline and the deep-thread dval==1.0 gate prevents double-walk only when ω stays outer). (2) `bb_binop.cpp` AG-pure relop/strrel arm: rt_acomp/rt_lcomp + unconditional jmp γ. (3) `bb_if.cpp` router: rt_pop_void; rt_last_ok; test; jz ω; jmp γ. **NEXT for numeric/real (IBB-8c):** add a BB_LIT_F push arm to `bb_lit_scalar.cpp` (currently a pass-through stub that never pushes the real → relop compares garbage → abort/SEGV on rung18_real_relop_*). Targets remaining: rung18_real_relop_{mixed,real_eq,real_gt,real_lt}, rung35_block_body_if_{block,else_block} (needs nested-block flattening).
- [~] **every E do body** — PARTIAL. ival=1 simple-gen (`every 1 to 3 do B`) DONE (IBB-8c). `every x := 1 to N do B` static-TO-assign DONE (IBB-9-1, `e8f66866`). Remaining ival=2/3 shapes → IBB-9.
- [ ] **write(BB_CALL)** — user-proc result → vstack → write trailer. Requires BB_CALL-as-arg semantics + BB_RETURN flat-wire. → IBB-9-7.
- [ ] **user-proc dispatch (non-write fn calls)** — large remaining cluster. Requires BB_CALL of arbitrary fn name + caller-side rt_call_proc helper. → IBB-9-6.

### IBB-9 (CURRENT) — JCON-grounded control-flow completion

**⚠ 2026-05-29 (Opus 4.8) COMPARATIVE REVIEW — read `STUDY-JCON-ICON-CONTROL-FLOW-2026-05-29-OPUS48.md`.**
A full read of `jcon/tran/irgen.icn`, canonical Icon `icon-master/src/runtime/ocomp.r`, and the LIVE
SCRIP tree (one4all `c7529bad`) found three things the text below this banner gets wrong because the
emitters were refactored after it was written:
1. **The `flat_drive_*` references are stale.** `flat_drive_while` (claimed `emit_bb.c:1029`),
   `flat_drive_seq`, `flat_drive_binop_tree` do **not exist** in the live tree. Icon BB emission is now
   per-kind templates in `src/emitter/BB_templates/*.cpp` dispatched from `emit_core.c`.
2. **`BB_WHILE`/`BB_UNTIL`/`BB_REPEAT` currently route to `bb_alt(nd)`** (`emit_core.c:561-565`) — the
   *alternation* driver. There is no while driver; the cond never gates. This is the real IBB-9-2 state,
   not "driver exists, JCON-faithful, cond doesn't gate."
3. **The compound `{...}` divergence is already closed.** `bb_seq.cpp` (header lines 4-6) already
   implements JCON `ir_a_Compound` both-ports-advance semantics; the old `flat_drive_seq` BFS hack is gone.

**Spine finding (verified three ways).** A relational op is NOT a boolean. Canonical Icon declares
`operator{0,1} <= cmplte(x,y)` → `return y` / `fail` (`ocomp.r:10-42`); JCON emits
`ir_opfn(<=, args, failLabel)` so failure jumps to `failLabel`, success falls through (`ir_binary:430`,
funcs set `ir_a_Binop:480`). **SCRIP is the outlier:** the relop sets a `LAST_OK` flag and jumps to a
`BB_IF` router (`bb_if_str`: `rt_pop_void; rt_last_ok; test eax,eax; jz ω; jmp γ`) that tests it. This
works for `if` (BB_IF *is* the router) but leaves `while`/`until`/`case` with no gate. The fix is NOT to
add a second bespoke router (the old IBB-9-2 plan, which doubles down on the outlier and caused the
26-program regression) — it is to make the relop carry its own γ/ω edges as both references do. See the
rewritten IBB-9-2 and the new IBB-9-RELOP-PORTS below.

---

**Source-of-truth:** `jcon/tran/irgen.icn` (the Icon→IR translator SCRIP's lowering mirrors). Read the cited
`ir_a_*` procedure BEFORE implementing each step; the chunk-wiring in JCON is the canonical CFG and SCRIP's
BB port-graph (α=start, β=resume, γ=success, ω=failure) is a direct transcription. The recurring JCON pattern:
each construct lays `ir_chunk`s for `ir.start / ir.resume / sub.success / sub.failure`, and the *only* structural
difference between loop forms is **where body-success/failure routes** — to `expr.resume` (every: pull next
generator value) vs `expr.start` (while/until: re-evaluate condition fresh). This single distinction (JCON
`ir_a_Every:327-330` vs `ir_a_While:1024-1031`) is the spine of every step below.

**Architectural prize from JCON (the deep idea):** for UNBOUNDED (resumable) control structures — if/case/alt
used in expression position — JCON does NOT hardcode the resume target. It emits `ir_MoveLabel(t, chosen.resume)`
on the taken branch and `ir_IndirectGoto(t)` at `ir.resume` (`ir_a_If:596-605`, `ir_a_Alt:183-188`). The taken
arm records its own resume label into a temp-location `t`; re-entry dispatches through `t`. This is a
**computed-goto continuation** — the same mechanism WAM-CP uses for Prolog. SCRIP currently only handles BOUNDED
(statement-context) Icon, where branches reconverge by fall-through and no `t` is needed. Expression-context
generators (`x := if a then (1 to 3) else (4 to 6); every write(x)`) will REQUIRE this. Captured here so it is
not rediscovered; deferred until a corpus program needs it (IBB-9-8).

- [x] **IBB-9-1 — `every x := 1 to N do B` (static-TO assign).** `e8f66866`. JCON `ir_a_Every` treats this as
  `every (x := GEN) do B`: the assignment is the `p.expr`, and because `:=` is in `ir_a_Binop`'s `funcs` set,
  `ir_binary:438-444` routes `expr.resume → right.resume` — the assign is transparent to resume, forwarding it
  into the generator. SCRIP transcription: interpose a BB_ASSIGN store node (ival=1, β=gen for the mode-2 null
  guard) on the ival=1 every topology; `flat_drive_every` emits gen→store→body→gen_β. Corpus 213→216.
- [x] **IBB-9-2 — `while C do B` / `until C do B`: relop-cond driver LANDED (2026-05-29 Opus 4.8).**
  Implemented `flat_drive_while` in `emit_bb.c` (NOT a new template — the gate reuses `bb_if`'s exact
  `LAST_OK` bytes, routed via `emit_core.c` `BB_WHILE`/`BB_UNTIL`→`bb_if`; `bb_if` ignores `pBB`).
  Topology = JCON `ir_a_While`: `cond_entry → cond(jmp gate) → gate(test LAST_OK: true→body / false→exit)
  → body(γ=ω=cond_entry, re-test)`. **`until` swaps the gate's true/false targets.** Two bugs the first
  cut had (caught by build+run, not by the single gate program):
  (a) the loop must exit via **`lbl_γ`** (the node's γ-successor = next statement), NOT `lbl_ω` — `flat_drive_seq`
      sends a non-`BB_IF` node's ω to the seq's outer fail, so exiting via ω dropped the statement after the loop;
  (b) the gate fires ONLY for relop conds with simple operands (`icn_while_operand_simple`: var / literal /
      pure-arith tree); non-relop/generator conds (`while line:=read()`) stay on the degenerate path (they
      crashed otherwise — those read-loops pass trivially under /dev/null and must not regress).
  Cond operands include **assignment-as-rvalue** (`(i:=i+1)>N`): fixed generally in `flat_drive_binop_tree`
  by re-pushing the stored value via `bb_var` after the consuming `bb_assign` (`rt_pop_nv_set` consumes).
  **Verified gains** (corpus same-sweep at `c7529bad`, m2==m3 byte-identical, rc 0): `rung35_block_body_while_do_block`,
  `rung09_loops_until_gen`, `rung09_loops_repeat_break`. zero-SM holds, FACT 0, smokes hold, 0 regressions, 0 SEGV.
  **Still deferred:** non-relop/generator conds (`while line:=read()`), string-relop conds, loop `break`/`next`
  (not wired in mode-3), and the fully reference-faithful no-flag/no-router form (**IBB-9-RELOP-PORTS** below).
- [x] **IBB-9-SWAP — `x :=: y` LANDED (2026-05-29 Opus 4.8).** New template `BB_templates/bb_swap.cpp`
  (two `rt_pop_nv_set`: push x, push y → pop y→x, pop x→y) + `flat_drive_swap`; wired through `Makefile`,
  `bb_templates.h`, `emit_core.c` (moved `BB_SWAP` off the `bb_stub` path). Both operands must be `BB_VAR`.
  Verified gains: `rung15_real_swap_swap_basic`, `rung15_real_swap_swap_str`. (lconcat-`||` swap form deferred.)
- [x] **IBB-9-ALTWRITE — `write(ALT)` any-type fix LANDED (2026-05-29 Opus 4.8).** `bb_call.cpp` `arg_is_any`
  now includes `BB_ALT`, so `write("a"|"b"|"c")` uses `rt_pop_write_any_nl` (was int-write → printed string
  descriptors as pointer garbage). Int-alts unaffected (any-write does DT_I via %lld). Gain: `rung13_alt_alt_every_write`.
- [x] **IBB-9-UNOP — value-producing unary ops `-E`/`+E`/`\E`/`/E`/`not E` LANDED (2026-05-29 Opus 4.8).**
  `BB_NEG`/`BB_POS`/`BB_NONNULL`/`BB_NULL_TEST`/`BB_NOT` previously routed to the `bb_cset`/`bb_stub` no-op
  stubs (emitted ZERO bytes in mode-3 → silent empty output). Now a real path: (1) new grouped template
  `BB_templates/bb_unop.cpp` — calls a per-op `rt_unop_*` helper then jmps γ UNCONDITIONALLY (the relop
  control shape: helper sets `LAST_OK` + pushes the result value; the BB_IF router reads `LAST_OK` to pick
  then/else, and value-context consumers (write/assign) take the pushed value). (2) `flat_drive_unop` in
  `emit_bb.c` walks the operand `pBB->α` first (push its value), then emits the template — mirror of
  `flat_drive_binop_tree`/`flat_drive_call_intexpr`. (3) five `rt_unop_*` helpers in `rt.c`, each a byte-for-byte
  transcription of the mode-2 `bb_exec.c` arm (neg/pos coerce + sign; nonnull fails on null/fail; null_test
  succeeds with &null iff null; not succeeds with &null iff inner failed). (4) `bb_call.cpp` extended
  `is_write_intexpr`/`arg_is_any` + the `BB_CALL` arg dispatch in `walk_bb_flat` to route these as
  value-producing `write` args. **Verified gains (same-sweep, m2==m3, zero-SM each):** `rung07_control_neg`
  (`write(-x)`), `rung07_control_not` (`if not(1>2)`), `rung07_control_repeat_break` (`if not(x<5)`),
  `rung34_null_test_{nonnull_fails,nonnull_succeeds,null_fails,null_succeeds}`. **Also fixed `--dump-bb`**
  (`scrip.c`): the flag set `g_opt_dump_bb` but was never consumed → fell through to `--run` and ABORTed on
  any not-yet-wired shape; now mirrors the `--dump-sm` early-return (build via `sm_preamble`, walk every
  proc's `bb_table` entry, `bb_print`, exit — no native emission). Corpus **62→69 (+7)**, SEGV 0, **0
  regressions** (worktree-verified diff of full pass-lists). Gates: FACT 0, smoke icon/prolog 5/5, broker 49/11,
  zero-SM holds. **Still deferred:** `nonnull_in_every` (`every \(...)` — unop on a generator-bearing chain,
  belongs with IBB-9-4); `BB_SIZE` (`*E`) and `BB_RANDOM` (`?E`) unops (same template slot, just need their
  `rt_unop_*` helpers + SIZE's DT_DATA/DT_T length handling — left for next pass).
- [x] **IBB-9-CONCAT — `||` string concatenation LANDED (2026-05-29 Opus 4.8).** `s1 || s2` lowers to a
  tree-shape `BB_BINOP` with `op=ICN_BINOP_CONCAT` (ival=11), α=lhs/β=rhs — the SAME shape as arith,
  driven by the op-agnostic `flat_drive_binop_tree` (walks both operands → values on vstack → apply).
  The gap was purely the apply: `bb_binop.cpp` handled arith+relop only and ABORTed loudly on ival=11
  (the single largest concrete ABORT cluster: 13 programs). Fix: (1) new CONCAT arm in `bb_binop.cpp`
  (the proven 32-byte arith layout with a dead `movabs rdi,0` so γ/β/ω patch offsets stay {23,27,28};
  calls `rt_icn_concat`). (2) new `rt_icn_concat` in `rt.c` — pops 2, routes through `icn_binop_apply`
  (the mode-2 oracle's ICN_BINOP_CONCAT arm) so m2==m3 byte-identical BY CONSTRUCTION, pushes result,
  sets LAST_OK. **Distinct from `rt_concat`** (the SNOBOL4 SM_CONCAT helper — different `CONCAT_fn`
  descriptor convention, cross-family; reusing it gave empty output and would couple Icon to SNOBOL4).
  Write/assign consumers already route a `BB_BINOP` arg0 through the any-write trailer (`arg_is_any`).
  **Corpus same-sweep 82→92 PASS (+10), SEGV 0, ABORT 146→133, 0 regressions (passlist-verified).**
  Newly passing: rung04_string_concat{,_chain}, rung04_string_str_var, rung11_bang_augconcat_augconcat
  {,_chain,_loop}, rung32_strretval_{basic_strret,chain,strret_assign,two_str_params}. Gates: FACT 0,
  canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 51/11. **Deferred (generator-bearing
  concat, → IBB-9-4/5):** `rung11_bang_augconcat_bang_concat`, `rung13_alt_alt_augconcat`,
  `rung32_strretval_strret_every` now RUN (no longer ABORT) but emit only the FIRST generated value — the
  concat is correct; the gap is generator re-pumping THROUGH the binop (the `every`/alt resume chain), which
  is exactly the IBB-9-4 two-port split. Not a regression (they ABORTed at baseline).
- [x] **IBB-9-SIZE — `*E` size as value-producing unop LANDED (2026-05-29 Opus 4.8).** `*E` (BB_SIZE)
  routed to the STUB `bb_limit` in mode-3 (emitted nothing → the write trailer ABORTed on arg0_kind=23).
  Rerouted to `bb_unop` (the value-producing unop family) + new `rt_unop_size`. Single source of truth:
  extracted `icn_size_value(DESCR_t,int*)` from the inline mode-2 BB_SIZE arm (string strlen / DT_DATA
  list frame_size / record nfields / DT_T table count / cset `icn_kw_cset_len`); both the mode-2 arm and
  the mode-3 `rt_unop_size` call it → byte-identical by construction (mode-2 refactor behavior-preserving,
  m2-as-oracle verified 0 regressions). Wiring: `emit_core.c` BB_SIZE→bb_unop; `bb_unop.cpp` name/fp maps;
  `emit_bb.c` flat_drive_unop dispatch + BB_CALL arg0 routing; `bb_call.cpp` is_write_intexpr + arg_is_any.
  Corpus 92→93 (+1: rung12_strrelop_size_size `write(*s)`). Gates: FACT 0, canonical-5 byte-identical +
  zero-SM, smoke icon/prolog 5/5. **`?E` (BB_RANDOM) deferred** (no corpus coverage; same template slot).
- [x] **IBB-9-TOBY — `write(lo to hi by step)` LANDED (2026-05-29 Opus 4.8).** `BB_TO_BY` was missing from
  the `write` arg-recognition lists, so `every write(1 to 10 by 3)` ABORTed (`bb_call: unsupported call
  shape — arg0_kind=17`). Two-line fix: added `BB_TO_BY` to `is_write_intexpr` (`bb_call.cpp`) and the
  `walk_bb_flat` BB_CALL write dispatch (`emit_bb.c`). The existing `flat_drive_call_intexpr` re-pump
  (`EMIT_PAIR_DEF_JMP(lbl_β, arg_β)`) already cascades the every-resume into the BB_TO_BY's β-advance, so
  no new driver was needed. Corpus 93→95 (+2: rung01_paper_to_by + sibling). Gates: FACT 0, zero-SM, smoke 5/5.
- [x] **IBB-9-INITIAL — `initial expr` once-guard LANDED (2026-05-29 Opus 4.8).** New `bb_initial.cpp`
  template + `flat_drive_initial` driver (`emit_bb.c`); moved `BB_INITIAL` off the `bb_stub` no-op in
  `emit_core.c` (it had emitted nothing → the clause never ran in mode-3). JCON `ir_a_Initial` / mode-2
  oracle: run the clause body on FIRST proc entry only. Mode-3 transcription uses a RUNTIME once-flag in
  `&pBB->counter` (calloc-zeroed at node alloc; persists across slab re-entries since the proc slab is built
  once and `rt_icn_call_proc` never resets it). Guard bytes: `movabs rax,&counter; mov rcx,[rax]; test; jne
  γ` (already ran → skip) `; mov qword [rax],1; jmp body_entry`; `β: jmp ω`. Driver walks `pBB->α` at
  body_entry (success→γ, failure→ω — initial-clause failure propagates as in mode-2). Corpus 95→100 (+5:
  rung21_global_initial_{global_initial,initial_once}, rung25_global_{global_initial,initial_once,initial_zero}).
  Gates: FACT 0, zero-SM, smoke icon/prolog 5/5.
- [x] **IBB-9-CASE — `case E of {...}` selector + clause-equality + `write(case)` LANDED (2026-05-29 Opus 4.8).**
  New `bb_case.cpp` glue (`bb_case_store` + `bb_case_gate`) + `flat_drive_case` driver. JCON `ir_a_Case` /
  mode-2 BB_CASE oracle: selector evaluated ONCE → stored in `&pBB->value` via new `rt_pop_store_descr`;
  each clause key walked, then gated by new `rt_case_eq` (numeric-eq iff both DT_I, else string-eq via
  `VARVAL_fn`) + `rt_last_ok` `jne` to that clause's value body; no-match falls through to the next clause's
  key walk; trailing lone chain node = default (→γ, or `jmp ω` if none). Value bodies emitted after the gate
  chain (each `val_entry_i:` → walk → γ); the matched body leaves the case result on the vstack for the
  rvalue context. The chain γ-links are STRUCTURAL (selector→key1→val1→key2→…); `walk_bb_flat` routes
  control via passed labels, so the driver traverses the chain manually. Driver owns ALL control flow — no
  node-template emit (would route to the `bb_limit` stub and splice dead bytes); defines its own β-stub like
  `flat_drive_seq`. `BB_CASE` added to `is_write_intexpr`/`arg_is_any` (`bb_call.cpp`) + the `walk_bb_flat`
  write dispatch so `write(case …)` routes the matched value through the any-write trailer. Corpus 100→105
  (+5: rung33_case_{arith,int,str,in_proc,no_default}). Gates: FACT 0, bytes-outside-templates 0, canonical-5
  byte-identical + zero-SM, smoke icon/prolog 5/5, broker 57 (5 pre-existing non-Icon fails, unchanged).
- [x] **IBB-10 — Icon builtin dispatch + record-constructor recognition LANDED (2026-05-29 Opus 4.8).**
  Transcribes the builtin (non-user-proc) case of JCON's invoke into the flat-slab model — the analogue of
  IBB-9-6's user-proc arm. Was the single largest ABORT cluster (120 of 127 `bb_call: unsupported call shape`).
  **5 files:** (1) `rt.c` — `rt_icn_call_builtin(name, nargs)`: pops nargs single-shot values (arg0 deepest),
  routes through `icn_try_call_builtin_by_name` (the SAME mode-2 oracle table the bb_exec.c BB_CALL arm calls →
  m2==m3 by construction), pushes result, sets LAST_OK; a name the table can't serve pushes FAILDESCR+LAST_OK=0
  (NO fall-through to INVOKE_fn — Icon stays decoupled from SNOBOL4 dispatch). Plus `rt_icn_builtin_is_known`
  emit-time gate: allow-list of pure single-shot builtins (write/writes/integer/real/string/numeric/char/ord/
  cset/type/image/proc/args/copy/abs/sqrt/trig/log/trim/reverse/repl/map/left/center/right/table/list/set/sort/
  get/pop/pull/member/insert/delete/MAKELIST), EXCLUDING generator builtins (find/upto/any/many/bal/key/seq —
  odometer path) and registered user procs; ALSO returns true for a registered record type (sc_dat_find_type) so
  a `record T(...)` constructor routes here. (2) `rt.h` — decls. (3) `bb_call.cpp` — `is_builtin` arm, byte
  layout identical to the IBB-9-6 userproc arm (only the called fn pointer differs: rt_icn_call_builtin), gated
  on `rt_icn_builtin_is_known && !write_simple1`. (4) `emit_bb.c` — `flat_drive_call_builtin` driver (byte-free;
  walks the arg γ-chain leaving nargs values on the vstack, arg0 deepest, then EMIT_PAIR_FILL → the builtin arm)
  + `icn_call_args_single_shot`/`icn_bb_is_gen_arg` guards (a generator arg → fall through to ABORT as before,
  no regression; it needs the IBB-9-4/5 odometer) + dispatch wiring in `walk_bb_flat`'s BB_CALL case (order:
  userproc → builtin → intexpr → FILL; `write`/`writes` single-simple-arg keeps its proven IBB-3/IBB-7 trailer
  via `write_simple1`). (5) `scrip.c` — driver pre-registers record types (walks every BB graph for BB_RECORD_DEF
  nodes → sc_dat_register) so a constructor is recognised at EMIT time (the runtime BB_RECORD_DEF also registers,
  idempotent, and runs before any ctor call, so runtime dispatch already worked — this only fixes the emit-time
  gate). **Two bugs found + fixed:** (a) the mode-2 table returns DT_S via STRVAL(buf) with **slen=0** (mode-2
  writes via fputs, never reading slen); the mode-3 `rt_pop_write_any_nl` uses `fprintf("%.*s")` so slen=0 printed
  NOTHING — fixed by normalizing `out.slen = strlen(out.s)` in rt_icn_call_builtin. (b) record constructors are
  neither user-procs nor table names at emit time — fixed via the driver pre-registration + sc_dat_find_type gate.
  **Corpus 105→130 (+25), SEGV 0, ABORT 127→68, 0 regressions** (full pass-list diff: 0 of 105 prior passes lost).
  Newly passing: rung28_builtins_str_{char_ord,pad,repl,reverse,trim_map}, rung29_builtins_type_{copy,image,mixed,
  numeric,type}, rung30_builtins_misc_{abs,sqrt}, rung22_lists_{get,pull}, rung13_table_member,
  rung17_real_arith_{integer,real_conv,string_conv}, rung15_real_swap_real_literal, rung36_jcon_{center,concord,
  diffwrds,nargs,radix,trim}. Gates: FACT 0, bytes-outside-templates 12 (unchanged from baseline — driver/driver
  are byte-free), canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 57. **Deferred:** record
  field get/set (IBB-11, hits interp_eval stub); generator-arg builtin calls (IBB-9-4/5); I/O builtins
  (open/read/reads — file-handle plumbing); the generator builtins (find/upto/etc — odometer path).
- [x] **IBB-11 — record field get/set (`obj.field`, `obj.field := rhs`). LANDED (2026-05-29, Opus 4.8) `2aac6fad`.**
  `BB_FIELD_GET`/`BB_FIELD_SET` were routed to the `bb_stub` no-op in mode-3 (emitted nothing → the write
  trailer / consumer hit the `interp_eval` stub: `[NO-AST] interp_eval stub`). Rerouted to new `bb_field.cpp`
  templates (`bb_field_get`/`bb_field_set`, the proven 32-byte movabs/movabs/call/jmp/β-jmp shape, same as
  bb_var/bb_assign — only the called fn pointer differs) + `flat_drive_field_get`/`flat_drive_field_set`
  byte-free drivers. GET driver walks α (object) → [obj] on vstack; SET driver walks β (rhs) THEN α (obj) →
  [rhs,obj] (obj on top), matching the mode-2 oracle's eval order (bb_exec.c BB_FIELD_SET evaluates β then α).
  Runtime: `rt_icn_field_get`/`rt_icn_field_set` in rt.c resolve the field cell via `data_field_ptr` — the SAME
  function the mode-2 bb_exec.c BB_FIELD_GET/SET arms call, so m2==m3 by construction; failed operand / unknown
  field → FAIL + LAST_OK 0 (the oracle's ω edge). `write(obj.field)` routed through `is_write_intexpr` /
  `arg_is_any` (bb_call.cpp) + `is_intexpr_shape` (emit_bb.c walk_bb_flat) so the field-get value flows through
  the any-write trailer. `data_field_ptr` declared extern in rt.c (already linked — interp_data.o is in the
  same binary). Also: `kind_names` + `bb_print` (scrip_ir.c) get BB_FIELD_GET/SET entries (was printing
  `(null)` in `--dump-bb`; cosmetic, dump-path only). **Corpus same-sweep 130→134 (+4), SEGV 0, FAIL 0,
  0 regressions (full pass-list diff: 0 of 130 prior passes lost).** Newly passing:
  rung24_records_{basic,field_assign,two_types,proc_arg}. Gates: FACT 0, canonical-5 byte-identical + zero-SM,
  smoke icon/prolog 5/5, broker 57. **Deferred:** record_loop (rung24_records_record_loop — has an
  `every c.n := 1 to 3 do` body, blocked on IBB-9-4 generator-bearing every).
- [x] **IBB-12 — `!E` list/table/record/string generator (BB_LIST_BANG). LANDED (2026-05-29, Opus 4.8) `da798a11`.**
  `BB_LIST_BANG` was routed to the `bb_stub` no-op in mode-3 (emitted 0 bytes → the value never reached the
  vstack → the enclosing `write` popped an empty stack: `libscrip_rt: SM value stack underflow`). Rerouted to
  new `bb_list_bang.cpp` template + `flat_drive_list_bang` driver. **Single source of truth:** extracted
  `icn_list_bang_at(obj, idx, *out)` from the inline mode-2 BB_LIST_BANG arm (DT_DATA list frame_elems / record
  fields / DT_T table bucket-walk / string per-char), and refactored the mode-2 arm to call it (behavior-preserving,
  m2-as-oracle 0 regressions). The mode-3 `rt_icn_list_bang(obj_slot, idx_slot, state_slot, reset)` calls the SAME
  function → m2==m3 byte-identical by construction. **Generator state** lives in the per-node `&pBB->value`
  (cached iterable), `&pBB->counter` (index), `&pBB->state` (phase) slots — stable emit-time addresses, the same
  idiom bb_to/bb_initial use for `&pBB->counter`; PEERS-compliant, NO new BB_t fields. The template has a live α
  (reset=1: pop iterable, idx 0) and live β (reset=0: ++idx) entry, both `call rt_icn_list_bang; test rax; jz ω;
  jmp γ` (hit pushes element + LAST_OK 1 → γ; exhaustion resets state + pushes FAIL + LAST_OK 0 → ω). The driver
  walks `pBB->α` (iterable) ONCE then FILLs the node (the iterable is evaluated once and cached; β only advances
  the index, it does NOT re-pump the iterable). `BB_LIST_BANG` added to `is_intexpr_shape` (emit_bb.c) so
  `write(!E)` routes through `flat_drive_call_intexpr`, which wires `call.β → arg.β` so the enclosing `every`
  re-pump cascades into the bang's β-advance; plus `is_write_intexpr` + `arg_is_any` (bb_call.cpp) so the yielded
  value flows through the any-write trailer. **Corpus same-sweep 134→140 (+6), SEGV 0, FAIL 1, ABORT 68→62,
  0 regressions (full pass-list diff: stash baseline rebuilt + captured + diffed, 0 of 134 prior passes lost).**
  Newly passing: rung15_iterate_string (`!s`), rung22_lists_bang_list (`!L`), rung31_sort_sort_basic /
  sort_already_sorted / sort_every (`!sort(L)`), rung11_bang_augconcat_bang_str. Gates: FACT 0,
  bytes-outside-templates 12 (unchanged — driver byte-free, template bytes inside `*_templates/`), zero-SM holds,
  smoke icon/prolog 5/5, broker 57. **Deferred:** `every v := !t do B` (rung13_table_iterate — ival=2 generator-
  bearing do-body, IBB-9-4); `put(L, !x)` / generator-arg builtins (rung22_lists_put_bang); `sortf` field-sort
  (rung31_sort_sortf_* — `interp_eval` stub, separate). With `!E` landed, IBB-9-4 (the two-port every/do split)
  is the highest-leverage next step — it unblocks the ival=2 generator-bearing do-bodies across the corpus.
  cond-true ⇒ exit, cond-false ⇒ body). Fix once in the shared driver and both forms work. **JCON `ir_a_Until` (irgen.icn:981-1005)**:
  `expr.success→ir.failure` (cond true ⇒ until ENDS), `expr.failure→body.start` (cond false ⇒ run body). Body
  success/failure → `expr.start`. The inverse-sense twin of while. Most corpus `until` tests
  (`rung09_loops_until*`) ALSO need user-proc dispatch (they wrap the loop in a `procedure countdown(n)`) — so they
  stay blocked on IBB-9-6 even after the cond-router lands; pick a proc-free `until` repro to gate this step.
- [x] **IBB-9-4 — `every E do B` ival=2 (assign-wrapped streaming generator, simple body). LANDED (2026-05-29, Opus 4.8).**
  Corpus same-sweep **140→143 PASS (+3), SEGV 0, 0 regressions** (full pass-list diff: 0 of 140 prior passes lost).
  Newly passing (all byte-identical, sortf cases match the `.expected` oracle): `rung13_table_iterate` (`every v := !t do write(v)`),
  `rung31_sort_sortf_field1`/`field2` (`every p := !S do write(p.x)`). Implemented in `flat_drive_every` (emit_bb.c) — byte-free,
  FACT 0, bytes-outside-templates 12 unchanged.
  **CRITICAL FALSE-START CAUGHT (kept for the record):** the first cut reused the ival=1 single-α two-port topology
  (`walk_bb_flat(pBB->α=assign, body_α, lbl_γ, gen_β)`). This SILENTLY emits only the FIRST generated value: for an
  ASSIGN-WRAPPED generator (`v := !L`), `flat_drive_assign` defines the every's re-pump label (`gen_β`) as `jmp ω`
  (assign doesn't backtrack), which SHADOWS the inner generator's own β-resume port. Verified wrong: `every v := !L do write(v)`
  over `[10,20,30]` printed only `10`; `every c := !"abc"` printed only `a`. `rung13_table_iterate` "passed" only because its
  table held a SINGLE element ("only"→99) — a single-element false positive. **Lesson: gate every generator change with a
  MULTI-element input, never a 1-element corpus case.**
  **Correct fix = JCON two-port split (irgen.icn ir_a_Every 327-331).** When `pBB->α` is `BB_ASSIGN` (lhs `BB_VAR`) over a
  streaming gen (`icn_bb_is_gen_arg(pBB->α->β)`): (1) walk the INNER generator (`gen->β`) with γ=store_α (yield → rebind+body),
  ω=outer γ (exhausted → every succeeds), β=gen_resume (the generator's OWN ++ resume entry); (2) emit the assign store ALONE
  by driving `flat_drive_assign` with a temporary `ival=1` (pops the already-yielded vstack value via `rt_pop_nv_set`, jmps body_α);
  (3) walk the do-body with γ=ω=gen_resume so each pass re-pumps the GENERATOR'S RESUME (not the assign's β). On exhaustion the
  generator takes its ω → outer γ. Verified multi-element: list `10 20 30`, string `a b c`, `1|2|3` alt, empty list (0 iters → "done"),
  `every v := !L do s := s + v` (accumulate). BARE streaming-gen do-body (`every !L do B`) already worked (the generator's own β
  IS the re-pump target when not assign-wrapped) and is unchanged.
  **Gates:** canonical crosscheck 4/4, zero-SM count=0 on all 3 new programs, smoke icon/prolog 5/5, broker 57 (5 pre-existing
  non-Icon fails unchanged), FACT 0.
  **STILL DEFERRED:** (a) **bodyless ival=2** (`every total := total + (1 to n)` — BB_ASSIGN over BB_BINOP_GEN, no do-body,
  rung02_proc_locals) — needs gen re-pump THROUGH the assign without a do-body to anchor the loop; the first attempt underflowed
  the vstack, now cleanly aborts. (b) **nested every** (`every a := !L do every b := !M do …`) — the body bears a generator, so
  lower keeps the OUTER every at ival=0 (generator-bearing body); cleanly aborts (→ needs body-state-reset per outer value).
  (c) **ival=3 BODY-MEDIATED block** (→ IBB-9-5). (d) **PRE-EXISTING latent bug, NOT touched here:** dynamic-bound
  `every v := i to j do B` (i,j vars) emits only the first value in mode-3 — verified identical at baseline `eda4d9aa`, so it is
  not a regression; lives on a different ival path (dynamic TO is excluded from `lic_is_gen_node`).
- [ ] **IBB-9-5 — `every E do { block }` ival=3 (BODY-MEDIATED).** `every x := 1 to 3 do { y := x*2; write(y) }`.
  The hardest: bb sits ON the back-edge (gen.γ=bb, gen.ω=bb, body.γ=bb, body.ω=bb) with a phase machine on bb->state
  (1=just-dispatched-gen, 2=just-dispatched-body) and per-pass BB_SEQ_EXPR state reset. Mode-2 ival=3 executor
  exists (bb_exec.c:1710); mode-3 `bb_every` ival=3 is the gap. **Prefer the JCON two-port split (IBB-9-4 note)
  over the phase machine** — JCON needs no per-state bb because generator and body are distinct boxes; the phase
  machine is a SCRIP artifact of fusing them. NOTE: corpus `rung35_block_body_every_do_block` currently exposes a
  **mode-2 bug** (`every x:=1 to 3 do {y:=x*2;write(y)}` prints `2 2 2` in m2, correct `2 4 6` in m3) — fix mode-2
  ival=3 x-rebind alongside, or the byte-identical gate will never pass. Honor break/next/return via FRAME flags
  (JCON `ir_a_Break:1107`/`ir_a_Next:1082` route to `curloop.ir.x.nextlabel`).
- [x] **IBB-9-6 — user-proc dispatch LANDED (2026-05-29, Opus 4.8).** Transcribes JCON `ir_a_Call`
  (irgen.icn:360-403) + `ir_a_Return` (irgen.icn:867-903) into the SCRIP flat-slab model. **Corpus
  same-sweep 69→82 PASS (+13), SEGV 0, ABORT 0 (the `bb_call: unsupported call shape` cluster is
  GONE), 0 regressions (worktree-verified diff of full pass-lists).** A user procedure is compiled by
  `bb_build_flat` into a self-contained x86 slab (`bb_box_fn`) that leaves its return value on the
  value-stack and exits via `XA_FLAT_EPILOGUE`'s `ret`. Pieces: (1) **`rt.c`/`rt.h`** — Icon proc
  registry (`rt_icn_proc_register(name, entry, pnames, nparams)` / `rt_icn_proc_is_registered` /
  `rt_icn_proc_set_builder` / `rt_icn_proc_reset`) + the caller `rt_icn_call_proc(name, nargs)`: pops
  args (arg0 deepest), binds params as NAMED variables (Icon BB mode-3 resolves vars via
  `NV_GET_fn`/`NV_SET_fn`, no frame slots), invokes the slab, reads the return value by vstack
  depth-delta (fall-off → FAILDESCR, matching mode-2 oracle), restores bindings (recursion-correct).
  **Slabs build LAZILY on first call** (driver sets `bb_build_flat` as the builder) — an unreached proc
  containing a not-yet-supported shape (which would `abort()` inside `bb_build_flat`) must not break a
  program that never calls it (this fixed 5 transient regressions: `meander`, `rung36_jcon_*`).
  (2) **`bb_return.cpp`** — new template (`return E`: value already on vstack from the driver walking
  α → `jmp γ`; bare `return`: `rt_push_null` then `jmp γ`); wired in `bb_templates.h`, `emit_core.c`
  (was routing to `bb_alt` no-op), Makefile. (3) **`emit_bb.c`** — `flat_drive_return` routes the
  success edge to the **slab-level exit** `g_emit.flat_succ_p` (NOT the next SEQ statement — a `return`
  exits the procedure, mirroring mode-2's FRAME.returning chain-stop; `flat_succ_p`/`flat_fail_p`
  hoisted to before the walk); `flat_drive_call_userproc` walks the arg γ-chain then emits the call
  trailer; **`BB_BINOP_GEN` non-streaming collapse** — `n * fact(n-1)` lowers to `BB_BINOP_GEN`
  because `is_suspendable` flags ALL calls (TT_FNC) as generators, but the mode-2 oracle discovers
  neither operand actually streams and does ONE multiply; mode-3 now detects this
  (`icn_binop_operand_streams`: a registered user-proc call is single-shot) and routes to the plain
  `flat_drive_binop_tree` (temporarily coercing `nd->t` to `BB_BINOP` so the apply emits `rt_arith`,
  restored immediately). (4) **`bb_call.cpp`** — userproc arm (`movabs rdi,name; mov esi,nargs;
  call rt_icn_call_proc; jmp γ`) gated on `rt_icn_proc_is_registered`; `BB_CALL` added to
  `is_write_intexpr`/`arg_is_any` so `write(proc())` routes the result through the any-write trailer.
  (5) **`scrip.c`** — driver registers every proc's entry + param-names + sets the lazy builder before
  building `main`. Newly passing: rung02_proc_add_proc/fact, rung03_suspend_fail/return,
  rung09_loops_repeat_counter/until_while, rung21_global_initial_* (×3), rung25_global_* (×4). Gates:
  FACT 0, smoke icon/prolog 5/5, broker 51/11, zero-SM holds, regressions 0. Edge cases verified
  byte-identical: 0-arg proc, nested calls, recursion, early/bare return. **Deferred:** generator
  procs (`suspend` in a called proc — needs the odometer path, not single-shot); rung02_proc_locals
  blocked separately on `every ival=2` (IBB-9-4).
- [ ] **IBB-9-7 — `write(BB_CALL)` / `write(proc-result)`.** Depends on IBB-9-6. Once a user proc leaves its result on
  the vstack, route it through the existing `rt_pop_write_any_nl` trailer (the BB_CALL-as-arg path bb_call.cpp already
  has `arg_is_any`). Also `write(f(x))` where f is a generator proc → every-resumes through the call chain.
- [ ] **IBB-9-8 — DEFERRED: unbounded/expression-context resume (computed-goto continuation).** Only when a corpus
  program assigns a generator-bearing if/case/alt to a variable and resumes it (`x := if … then (1 to 3); every write(x)`).
  Implement JCON's `ir_MoveLabel(t, arm.resume)` + `ir_IndirectGoto(t)` (`ir_a_If:596`, `ir_a_Alt:183`). This is the
  `bounded` flag SCRIP currently ignores. Big; do not start until forced.
- [ ] **IBB-9-RELOP-PORTS — DEFERRED REFACTOR: relop routes via its own γ/ω; retire the flag+router (NEW 2026-05-29).**
  The reference-faithful endgame for the Section-1 spine finding. Today a relop sets a global `LAST_OK` and jumps to a
  `BB_IF` router that tests it (`bb_if_str`); IBB-9-2 reuses that router for while/until. Both references instead make the
  comparison route control directly: canonical Icon `operator{0,1} <=` → `return y`/`fail` (`ocomp.r:10-42`); JCON
  `ir_opfn(<=, args, failLabel)` → fail-edge/success-edge (`ir_binary:430`). **Refactor:** bake the branch into the relop
  template (`bb_binop.cpp` relop arm) — `rt_acomp`/`rt_lcomp; jz ω; jmp γ` — so the relop carries its own edges and NO
  router node and NO `LAST_OK` flag exist. Then `if`/`while`/`until`/`case` all just wire `cond.γ`/`cond.ω`; the two relop
  shapes (AG-pure vs tree, a SCRIP-only bifurcation) collapse to one; `lower_icn_new_If_ag`'s funnel of both cond ports
  into `BB_IF` is removed; `BB_IF` is retired for the relop case (keep only if a non-relop value-test remains). Larger
  blast radius (relop template + If lowering + BB_IF dispatch) — land only after IBB-9-2/9-3 hold the corpus, and gate the
  full same-sweep against the then-current baseline (expect ≥0 regressions and possible new passes from `case`/expression
  relops that the router never reached). Removes the recurring "two relop shapes" trap that has cost multiple sessions.

### IBB-IDX (closed 2026-05-30, Opus 4.8) — subscript get/set `base[idx]`, `base[idx] := rhs`

**Corpus same-sweep 152→165 (+13), 0 regressions** (clean-baseline pass-list diff: LOST none, GAINED 13).
`BB_IDX` / `BB_IDX_SET` were both routed to the `bb_stub` no-op in mode-3 — get emitted 0 bytes (the
enclosing `write` printed empty / silent MISMATCH), set hit the `interp_eval` stub. Rerouted to new
`bb_idx.cpp` (`bb_idx`/`bb_idx_set`: the no-arg `movabs rax,fn; call rax; jmp γ; β:jmp ω` 22-byte shape,
identical to `bb_unop` — only the called fn ptr differs) + byte-free `flat_drive_idx_get` /
`flat_drive_idx_set` drivers (emit_bb.c). Runtime `rt_icn_idx_get` / `rt_icn_idx_set` (rt.c) pop the
operands and dispatch through the shared `subscript_get` / `subscript_set` — the SAME helpers the mode-2
oracle's BB_IDX/BB_IDX_SET arms call → m2==m3 by construction.

**Two topologies, both handled** (both produced by lower_icn, both in the mode-2 oracle): TREE
(`α=base`, `β=index` operand subgraphs — e.g. `write(s[i])` where the IDX is the write-arg; for SET the
rhs sits on `β->γ`) — the driver walks the operands here; and AG-PURE (`α==β==NULL` — operands already
pushed by the enclosing γ-chain, e.g. a bare `t[k] := v` statement) — the driver just FILLs. Pop order:
GET pops idx then base; SET pops rhs, idx, base (matching the oracle's AG-pure `peek(2)=base/peek(1)=idx/
peek(0)=rhs`).

**Grounding:** JCON `ir_a_Binop` (irgen.icn:472) — `[]` is in the `funcs` set (resumption fails
immediately): left (base) evaluated, then right (index), then op applies; single-shot, β-resume → ω. The
SCRIP BB_IDX shape (α=base, β=index, single-shot, β→ω) is a direct transcription.

**slen bug found + fixed (same class as IBB-10).** First cut produced blank output for `write(s[1])`.
Traced to ground with probes (NOT assumed): the operands arrived correctly on the vstack (base.v=1 DT_S,
idx.v=6 DT_I idx.i=1), `subscript_get` returned the correct value (result.v=1 result.s="h") — but
`subscript_get` builds its DT_S via `STRVAL(buf)` which sets `slen=0`, and the mode-3 any-write trailer
uses `fprintf("%.*s", slen, s)` → a slen=0 DT_S prints nothing. Fixed by normalizing
`r.slen = strlen(r.s)` in `rt_icn_idx_get` (the exact fix IBB-10 applied to `rt_icn_call_builtin`).
`BB_IDX` added to `is_write_intexpr`/`arg_is_any` (bb_call.cpp) + `is_intexpr_shape` (emit_bb.c) so
`write(s[i])` / `write(t[k])` route the value through the any-write trailer.

**Newly passing (13, byte-identical, zero-SM verified on samples):** rung16_subscript_sub_{basic,fail,
literal,neg}, rung13_table_{basic,delete,subscript_assign}, rung23_table_table_{basic,default,
insert_delete,member}, rung35_table_str_str_{default_int_key,table_read}.

**NEW SEGV accounted (queens.icn) — NOT a regression.** queens moved MISMATCH→SEGV. It never passed
(baseline m2=419906 lines vs m3=1). Root cause traced to ground: `line := repl("|   ",n) || "|"` yields a
slen=0 / "0"-valued string in m3 — a **pre-existing `repl`+`||` defect** (verified: `*line`=0 in m3 vs 17
in m2), out of IBB-IDX scope. The now-correct subscript-set then passes a DT_I (integer) base to
`subscript_set`, which calls `sno_runtime_error(3)`. **Mode-2 SEGVs identically** on a genuinely-bad
subscript — verified `x[2]:="Q"` (x an int) → rc=139 in BOTH modes — so the crash path is oracle-faithful;
the divergence is purely the upstream repl/concat value. Fixing it belongs to a repl/concat goal.

**Deferred:** generator-index `s[1 to 3]` (rung16_subscript_sub_every) — the index is a generator, so the
subscript must re-pump; single-shot IDX yields only the first value (pre-existing MISMATCH, → IBB-9-4/5).
`key(t)` (rung23_table_table_key) — BB_KEY_GEN still stubbed.

**Gates:** FACT 0, bytes-outside-templates 12 (unchanged — drivers byte-free, template bytes inside
`bb_idx.cpp`), zero-SM count=0 on idx programs, canonical crosscheck 4/4, smoke icon/prolog 5/5, broker 61.

### IBB-23 (open) — `suspend E`

Top-level `procedure g() suspend 1; suspend 2; end; every write(g())` prints nothing in both mode-2 and legacy. Pre-existing — needs `lower_icn_proc_gen`'s GeneratorState bridge wired through to outer `every` loop.

### IBB-LIMIT (closed 2026-05-29, Opus 4.8) — `gen \\ N` generator limitation

**Corpus same-sweep 143→148 (+5), SEGV 0, 0 regressions** (passlist LOST empty). Newly passing (all
byte-identical, multi-value verified): `rung14_limit_limit_{to,alt,str,large,zero}`. `bb_limit.cpp` was a
STUB (emitted 0 bytes → the enclosing `write` popped an empty vstack: `SM value stack underflow` — this was
the largest sub-cluster of the 19 underflow ABORTs). Also note: `--dump-bb` mislabeled `BB_LIMIT` as
`BB_NONNULL` because `kind_names[]` (scrip_ir.c) had drifted out of sync with the `BB_op_t` enum (missing
BB_REPEAT/BB_ALT/BB_SIZE/BB_CASE/BB_NOT and many tail entries) — **fixed by regenerating the whole array as
designated initializers `[BB_X] = "BB_X"`** so it can never drift again (dump-path only; 0 execution change,
verified by sweep). The mislabel had nearly sent the diagnosis down the wrong path.

**Design (mode-2 BB_LIMIT arm + JCON ir_a_Limit).** A new flat driver `flat_drive_limit` (emit_bb.c,
byte-free) + three glue templates in `bb_limit.cpp` (`bb_limit_begin`/`bb_limit_inc`/`bb_limit_more`, same
mid-node-glue precedent as `bb_case_store`/`bb_case_gate`) + three runtime helpers
(`rt_icn_limit_begin`/`_more`/`_inc` in rt.c, mirroring the mode-2 arm so m2==m3 by construction). State in
per-node `&pBB->value` (cached int-coerced max) + `&pBB->counter` (running count) — PEERS-compliant, no new
BB_t fields. Reached as an intexpr generator-arg (γ=yield, ω=exhausted, β=resume). Two-port (fresh vs
resume) split, identical in spirit to the IBB-9-4 gen-threading: (entry) walk count-expr → `bb_limit_begin`
pops it, caches max, count=0, `jz ω` on max<=0, else FALL THROUGH into the generator's fresh entry; walk
`pBB->α` with γ=got_value, ω=outer ω, β=gen_resume; (got_value) `bb_limit_inc` (count++) then `jmp γ`
(value already on vstack); (lbl_β) `bb_limit_more` (counter<max?) `jz ω` else `jmp gen_resume`.

**α allow-list guard (regression-prevention).** `flat_drive_limit` only handles α generator kinds with a
real mode-3 two-port (fresh/resume) emission: BB_TO/BB_TO_BY/BB_ALT/BB_BINOP_GEN/BB_LIST_BANG (seen through
a BB_ASSIGN wrapper). Kinds without mode-3 generator emission yet — **BB_SEQ_GEN** (`seq(1)`), BB_FIND_GEN,
BB_KEY_GEN, BB_UPTO, BB_ITERATE, BB_PROC_GEN — would emit a generator that never yields → a SILENT EMPTY
loop; the guard ABORTS LOUDLY instead, preserving the pre-IBB-LIMIT loud-abort. **This was caught by the
mismatch diff:** without the guard, `every write(seq(1) \\ 3)` (rung30_builtins_misc_seq) went from a loud
underflow-abort to silent-empty (m2 `1 2 3`, m3 empty) — a +1 MISMATCH. With the guard, MISMATCH is back to
the 56 baseline. **Lesson reinforced:** a generator combinator over an unsupported sub-generator must abort,
not emit a degenerate loop.

**Gates:** FACT 0, bytes-outside-templates 12 (unchanged — driver byte-free, glue bytes inside `bb_limit.cpp`),
zero-SM count=0 on limit programs, canonical crosscheck 4/4, smoke icon/prolog 5/5, broker 57. Verified
multi-value: `(1 to 10) \\ 3` → `1 2 3`, `(1|2|3|4) \\ 2` → `1 2`, `!"abcd" \\ 2` → `a b`, `\\ 0` → nothing,
variable count `\\ k`, and limit feeding an assign-do-body (`every v := (10 to 50 by 10) \\ 2 do write(v)` →
`10 20`). **PRE-EXISTING (not this work):** `!L \\ 3` parses as `!(L \\ 3)` (limit wraps the BB_VAR `L`, not
the bang) — a parser-precedence quirk wrong in BOTH modes (m2 prints all elements), out of corpus scope; the
α guard correctly rejects the BB_VAR α in m3.

### IBB-8..34 — remaining (deferred mode-3 + mode-4)

Strings, to-by, conj, if, while, until/repeat, assign, augop, list, bang, idx, idx-gen, section, limit, user-call, suspend, return, fail, tables, sets, records, csets, scan, scan-prims, scan-gens, co-expressions, JCON ir_a_* sweep.

---

## Mode-3 abort map (canonical-5)

| Test | State |
|------|-------|
| hello.icn  | ✅ `6393c743` |
| add.icn    | ✅ `e612d519` |
| every_to.icn | ✅ `fac53504` |
| alt.icn    | ✅ `1a97c0a3` |
| full.icn   | ✅ `3aa200cd` |

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --interp  /tmp/rung_NN.icn  > out_m2.txt
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
diff out_m2.txt out_m3.txt    # must be empty
./scrip --dump-sm /tmp/rung_NN.icn  # ; SM_sequence_t  count=0

# FACT gate
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l   # == 0

# Smokes (must hold)
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md`.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## Watermark

Programs PASS, both modes, byte-identical.

| State | Programs PASS | Notes |
|-------|---------------|-------|
| IBB-IDX ✅ | 5/5 smoke; corpus same-sweep 152→165 (+13), SEGV 0→1 (pre-existing MISMATCH program, NOT a regression), FAIL 1, ABORT 50→53, 0 regressions (clean-baseline pass-list diff LOST=none) | (Opus 4.8, 2026-05-30). **Icon subscript get `base[idx]` (BB_IDX) + set `base[idx] := rhs` (BB_IDX_SET).** Both routed off the `bb_stub` no-op (emitted 0 bytes → write printed empty / assign hit interp_eval) to new `bb_idx.cpp` (`bb_idx`/`bb_idx_set`, the no-arg `movabs rax,fn / call / jmp γ / β:jmp ω` 22-byte shape cloned from bb_unop — only the fn ptr differs) + byte-free `flat_drive_idx_get`/`flat_drive_idx_set` drivers (emit_bb.c). Two topologies handled: TREE (α=base,β=index operand subgraphs — walk them; SET's rhs on β->γ) and AG-PURE (α==β==NULL — operands already pushed by the γ-chain, just FILL), mirroring the mode-2 oracle's two BB_IDX/BB_IDX_SET arms. Runtime `rt_icn_idx_get`/`rt_icn_idx_set` (rt.c) pop operands (GET: idx,base; SET: rhs,idx,base) and dispatch through the shared `subscript_get`/`subscript_set` — the SAME helpers the mode-2 oracle calls → m2==m3 by construction. **slen bug found+fixed (IBB-10 class):** `subscript_get` returns DT_S via `STRVAL(buf)` slen=0; the any-write trailer's `fprintf("%.*s",slen,s)` printed nothing → traced to ground via probes (operands correct, result.s="h" correct, slen=0) → fixed `r.slen=strlen(r.s)`. `BB_IDX` added to `is_write_intexpr`/`arg_is_any` (bb_call.cpp) + `is_intexpr_shape` (emit_bb.c). Grounded in JCON `ir_a_Binop` (`[]` ∈ funcs = single-shot, β→ω). Newly passing (13): rung16_subscript_sub_{basic,fail,literal,neg}, rung13_table_{basic,delete,subscript_assign}, rung23_table_table_{basic,default,insert_delete,member}, rung35_table_str_str_{default_int_key,table_read}. Gates: FACT 0, bytes-outside-templates 12 (unchanged — driver byte-free), zero-SM count=0, canonical 4/4, smoke icon/prolog 5/5, broker 61. **SEGV (queens.icn) accounted:** MISMATCH→SEGV, NOT a regression (never passed: m2=419906 lines vs m3=1 at baseline). Root cause: `repl(...)||"|"` yields a slen=0/"0" string in m3 (pre-existing repl+|| defect, out of scope); the now-correct subscript-set then passes a DT_I base to `subscript_set` → `sno_runtime_error(3)`, which **mode-2 SEGVs on identically** (`x[2]:="Q"` → rc=139 in BOTH modes; the crash path is oracle-faithful). **Deferred:** generator-index `s[1 to 3]` (rung16_subscript_sub_every — single-shot IDX yields first value only; → IBB-9-4/5); `key(t)` (rung23_table_table_key — BB_KEY_GEN still stubbed). |
| real TO_BY ✅ | 5/5 smoke; corpus same-sweep 150→152 (+2), SEGV 0, FAIL 1, ABORT 52→50, 0 regressions, MISMATCH 56 (unchanged) | (Opus 4.8, 2026-05-29). **Icon `lo to hi by step` with REAL literal bounds (`1.0 to 2.0 by 0.5`).** mode-3 `bb_to_by.cpp` handled only literal-INT bounds; the real / dynamic case fell to a yields-nothing passthrough stub → the enclosing `write` popped empty vstack (underflow). Added a `lit_real` arm (α/β are BB_LIT_F, step bit-cast in pBB->ival) driven by new `rt_icn_toby_real(cur_slot, lo_bits, hi_bits, step_bits, reset)` (rt.c) — mirrors the mode-2 BB_TO_BY real arm (cur=lo on reset; check vs hi w/ 1e-12 epsilon by sign of step; yield DT_R(cur); advance cur+=step) → m2==m3 by construction. Two-half template (α reset=1 / β reset=0), bounds/step passed bit-cast as u64 immediates (movabs), state in &pBB->value. **Second bug:** values first printed as raw IEEE bits (4607182418800017408=1.0) because `write(real-toby)` used the int trailer — fixed by adding **real-only** `BB_TO_BY` to `arg_is_any` (bb_call.cpp, gated `sval[0]=='r'`) so DT_R routes through `rt_pop_write_any_nl`/real_str; integer TO_BY stays on its proven int trailer (verified rung01_paper_to_by byte-identical). Newly passing: rung19_pow_toby_real_toby_{pos,neg}. Multi-value verified: `1.0 to 2.0 by 0.5`→`1.0 1.5 2.0`, `0.0 to 1.0 by 0.25`→`0.0 0.25 0.5 0.75 1.0`, neg step `3.0 to 1.0 by -1.0`→`3.0 2.0 1.0`. Gates: FACT 0, bytes-outside-templates 12 (real bytes inside bb_to_by.cpp), zero-SM count=0, canonical crosscheck 4/4, smoke icon/prolog 5/5, broker 57. **Deferred:** DYNAMIC real/int bounds (non-literal α/β) still take the yields-nothing stub — needs operand-box walking (the AG-pure ring path). |
| max/min ✅ | 5/5 smoke; corpus same-sweep 148→150 (+2), SEGV 0, FAIL 1, ABORT 54→52, 0 regressions, MISMATCH 56 (unchanged) | (Opus 4.8, 2026-05-29). **Icon `max`/`min` multi-arg numeric builtins.** Aborted as `bb_call: unsupported call shape fn='max' narg=2` because they were missing from the `rt_icn_builtin_is_known` allow-list (rt.c). One-line add: the mode-2 oracle `icn_try_call_builtin_by_name` (icn_runtime.c) already handles both as multi-arg (real-aware) and the mode-3 `rt_icn_call_builtin` calls the SAME table → m2==m3 by construction. Newly passing: rung30_builtins_misc_maxmin (`7 3 5`), rung30_builtins_misc_mixed (`3.5 5 2`, real-valued). Gates: FACT 0, zero-SM count=0, canonical crosscheck 4/4, smoke icon/prolog 5/5, broker 57. |
| IBB-LIMIT ✅ | 5/5 smoke; corpus same-sweep 143→148 (+5), SEGV 0, FAIL 1, ABORT 59→54, 0 regressions, MISMATCH 56 (unchanged) | (Opus 4.8, 2026-05-29). **Icon `gen \\ N` generator limitation (BB_LIMIT).** `bb_limit.cpp` was a STUB (emitted 0 bytes → enclosing `write` popped empty vstack: `SM value stack underflow` — largest sub-cluster of the 19 underflow ABORTs). New byte-free driver `flat_drive_limit` (emit_bb.c) + 3 glue templates `bb_limit_begin`/`bb_limit_inc`/`bb_limit_more` (bb_case glue precedent) + 3 rt helpers `rt_icn_limit_begin`/`_more`/`_inc` (rt.c, mirror the mode-2 BB_LIMIT arm → m2==m3 by construction). State in `&pBB->value` (cached int max) + `&pBB->counter` (count); PEERS-compliant, no new BB_t fields. Two-port (fresh/resume) split, reached as an intexpr generator-arg: begin pops+caches max/count=0/`jz ω`; fall through to gen fresh; got_value inc+`jmp γ`; `lbl_β` more-gate `jz ω` else `jmp gen_resume`. **α ALLOW-LIST GUARD** (BB_TO/TO_BY/ALT/BINOP_GEN/LIST_BANG through a BB_ASSIGN wrapper): unsupported sub-gens (BB_SEQ_GEN/FIND_GEN/KEY_GEN/UPTO/ITERATE/PROC_GEN) ABORT LOUDLY rather than emit a silent-empty loop — caught by the mismatch diff (`every write(seq(1)\\3)` went loud-abort→silent-empty without it; guard restores MISMATCH to baseline 56). Also fixed `kind_names[]` drift (scrip_ir.c): it was out of sync with the BB_op_t enum (missing BB_REPEAT/ALT/SIZE/CASE/NOT + tail), so `--dump-bb` mislabeled BB_LIMIT as BB_NONNULL — regenerated the whole array as designated initializers `[BB_X]=\"BB_X\"` (dump-path only, 0 execution change). Newly passing (multi-value verified): rung14_limit_limit_{to,alt,str,large,zero}. Gates: FACT 0, bytes-outside-templates 12 (unchanged — driver byte-free), zero-SM count=0, canonical crosscheck 4/4, smoke icon/prolog 5/5, broker 57. **PRE-EXISTING (not this work):** `!L \\ 3` parses as `!(L\\3)` (both modes wrong, out of corpus scope; α guard rejects the BB_VAR α in m3). |
| IBB-9-4 ✅ | 5/5 smoke; corpus same-sweep 140→143 (+3), SEGV 0, FAIL 1, ABORT 62→59, 0 regressions | (Opus 4.8, 2026-05-29). **Assign-wrapped ival=2 `every v := GEN do B` — JCON two-port split (ir_a_Every 327-331).** `flat_drive_every` (emit_bb.c), byte-free. **FALSE-START CAUGHT:** the single-α reuse of the ival=1 topology emits only the FIRST value because `flat_drive_assign` defines the every re-pump label as `jmp ω`, SHADOWING the inner generator's β-resume; `rung13_table_iterate` gave a single-element FALSE POSITIVE ('only'→99). Multi-element (`every v := !L do write(v)` over [10,20,30] → only `10`) exposed it. **Fix:** when `pBB->α` is `BB_ASSIGN`(lhs `BB_VAR`) over `icn_bb_is_gen_arg(pBB->α->β)`, (1) walk the INNER generator with γ=store_α, ω=outer γ, β=gen_resume (its OWN ++ resume); (2) emit the assign store ALONE via `flat_drive_assign` temporarily set `ival=1` (pops the yielded vstack value, jmps body_α); (3) walk the do-body with γ=ω=gen_resume so each pass re-pumps the GENERATOR'S RESUME, not the assign's β. Exhaustion → generator ω → outer γ. Newly passing (byte-identical; sortf cases match `.expected`): rung13_table_iterate, rung31_sort_sortf_field1/field2. Multi-element verified: list `10 20 30`, string `a b c`, `1|2|3`, empty list (0 iters), accumulate-in-body. Bare `every !L do B` already worked (unchanged). Regression proof: stash → clean baseline 140-passlist → restore → diff: LOST empty, GAINED exactly the 3. Gates: FACT 0, bytes-outside-templates 12 (unchanged — driver byte-free), zero-SM count=0 on all 3, canonical crosscheck 4/4, smoke icon/prolog 5/5, broker 57. **Deferred:** bodyless ival=2 (rung02_proc_locals — gen-through-assign with no do-body, clean-aborts); nested every (generator-bearing body, ival=0, clean-aborts); ival=3 BODY-MEDIATED (IBB-9-5). **PRE-EXISTING (not this work):** dynamic-bound `every v := i to j do B` emits only first value — identical at baseline `eda4d9aa`, different ival path (dynamic TO excluded from `lic_is_gen_node`). |
| IBB-12 ✅ | 5/5 smoke; corpus same-sweep 134→140 (+6), SEGV 0, FAIL 1, ABORT 68→62, 0 regressions | `da798a11` (Opus 4.8, 2026-05-29). **Icon `!E` list/table/record/string generator (BB_LIST_BANG).** Routed off the `bb_stub` no-op (emitted 0 bytes → enclosing `write` popped an empty vstack: `SM value stack underflow`) to new `bb_list_bang.cpp` template + `flat_drive_list_bang` driver. Single source of truth: extracted `icn_list_bang_at(obj,idx,*out)` from the inline mode-2 BB_LIST_BANG arm (list frame_elems / record fields / table bucket-walk / string per-char); mode-2 arm refactored to call it (behavior-preserving); mode-3 `rt_icn_list_bang(obj_slot,idx_slot,state_slot,reset)` calls the SAME fn → m2==m3 by construction. Generator state in per-node `&pBB->value`/`&pBB->counter`/`&pBB->state` (stable emit-time addresses, same idiom as bb_to/bb_initial; PEERS-compliant, no new BB_t fields). Template: live α (reset=1, idx 0) + live β (reset=0, ++idx), both `call; test rax; jz ω; jmp γ`. Driver walks `pBB->α` (iterable) ONCE then FILLs (iterable cached; β advances index only, does not re-pump). `BB_LIST_BANG` added to `is_intexpr_shape` (emit_bb.c — `write(!E)` → flat_drive_call_intexpr wires call.β→arg.β for every-resume) + `is_write_intexpr`/`arg_is_any` (bb_call.cpp — any-write trailer). Regression proof: stashed work, rebuilt clean baseline, captured 134-passlist, restored, diffed — LOST empty, GAINED exactly the 6 bang programs. Newly passing: rung15_iterate_string (`!s`), rung22_lists_bang_list (`!L`), rung31_sort_sort_{basic,already_sorted,every} (`!sort(L)`), rung11_bang_augconcat_bang_str. Gates: FACT 0, bytes-outside-templates 12 (unchanged), zero-SM holds, smoke icon/prolog 5/5, broker 57. **Deferred:** `every v:=!t do B` (ival=2, IBB-9-4); `put(L,!x)` generator-arg builtin; `sortf` (interp_eval stub). **NEXT:** IBB-9-4 two-port every/do split (highest leverage — unblocks ival=2 generator-bearing do-bodies). | **Icon record field get/set (`obj.field`, `obj.field := rhs`).** BB_FIELD_GET/SET routed off the `bb_stub` no-op (emitted nothing → hit the `[NO-AST] interp_eval stub`) to new `bb_field.cpp` templates (`bb_field_get`/`bb_field_set`, the proven 32-byte movabs/movabs/call/jmp/β-jmp shape from bb_var/bb_assign — only the called fn ptr differs) + byte-free `flat_drive_field_get`/`flat_drive_field_set` drivers. GET driver walks α (object) → [obj]; SET driver walks β (rhs) THEN α (obj) → [rhs,obj] (obj on top), matching the mode-2 oracle's eval order. Runtime `rt_icn_field_get`/`rt_icn_field_set` resolve the cell via `data_field_ptr` — the SAME fn the mode-2 bb_exec.c arms call → m2==m3 by construction (failed operand/unknown field → FAIL+LAST_OK 0). `write(obj.field)` routed through is_write_intexpr/arg_is_any (bb_call.cpp) + is_intexpr_shape (emit_bb.c). `data_field_ptr` declared extern in rt.c (interp_data.o already in the same binary). kind_names + bb_print (scrip_ir.c) get BB_FIELD_GET/SET entries (fixes `--dump-bb` `(null)`; dump-path only). Newly passing: rung24_records_{basic,field_assign,two_types,proc_arg}. Gates: FACT 0, canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 57. **Deferred:** rung24_records_record_loop (`every c.n := 1 to 3 do` body — blocked on IBB-9-4). |
| IBB-10 ✅ | 5/5 smoke; corpus same-sweep 105→130 (+25), SEGV 0, ABORT 127→68, FAIL 0, 0 regressions | (Opus 4.8, 2026-05-29). **Icon builtin dispatch + record-constructor recognition.** The analogue of IBB-9-6's user-proc arm for the BUILTIN case; killed the single largest ABORT cluster (120 of 127 `bb_call: unsupported call shape`). 5 files: `rt.c` (`rt_icn_call_builtin` pops args arg0-deepest → `icn_try_call_builtin_by_name` mode-2 oracle → push result; `rt_icn_builtin_is_known` allow-list gate excluding generator builtins find/upto/any/many/bal/key/seq + recognising registered record types via `sc_dat_find_type`), `rt.h`, `bb_call.cpp` (`is_builtin` arm, byte layout cloned from the userproc arm), `emit_bb.c` (`flat_drive_call_builtin` byte-free driver + `icn_call_args_single_shot`/`icn_bb_is_gen_arg` guards + dispatch wiring), `scrip.c` (driver pre-registers record types from BB_RECORD_DEF nodes so a constructor is recognised at emit time). Two bugs fixed: (a) mode-2 STRVAL(buf) returns slen=0 → mode-3 `rt_pop_write_any_nl` `%.*s` printed nothing → normalize `out.slen=strlen` in rt_icn_call_builtin; (b) record ctor neither user-proc nor table name at emit → driver pre-reg + sc_dat_find_type gate. Newly passing (25): rung28_builtins_str_{char_ord,pad,repl,reverse,trim_map}, rung29_builtins_type_{copy,image,mixed,numeric,type}, rung30_builtins_misc_{abs,sqrt}, rung22_lists_{get,pull}, rung13_table_member, rung17_real_arith_{integer,real_conv,string_conv}, rung15_real_swap_real_literal, rung36_jcon_{center,concord,diffwrds,nargs,radix,trim}. Gates: FACT 0, bytes-outside-templates 12 (unchanged from baseline; driver+driver byte-free), canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 57 (5 pre-existing non-Icon fails). 0 regressions (full pass-list diff). **Deferred:** record field get/set (IBB-11, interp_eval stub); generator-arg builtin calls (IBB-9-4/5); I/O builtins open/read/reads; generator builtins find/upto (odometer). |
| IBB-9-CASE ✅ | 5/5 smoke; corpus same-sweep 100→105 (+5), SEGV 0, ABORT 0, 0 regressions | `c117aa16` (Opus 4.8, 2026-05-29). **`case E of {...}` selector + clause-equality + `write(case)`.** New `bb_case.cpp` glue (`bb_case_store`/`bb_case_gate`) + `flat_drive_case` driver. Selector evaluated ONCE → `&pBB->value` (new `rt_pop_store_descr`); each clause key walked then gated by new `rt_case_eq` (numeric-eq iff both DT_I else string-eq via `VARVAL_fn`) + `rt_last_ok` `jne` to that clause's value body; no-match falls through; trailing chain node = default. Value bodies after the gate chain (→γ); matched body leaves result on vstack for the rvalue context. Driver owns all control flow (no node-template emit; defines its own β-stub like `flat_drive_seq`). `BB_CASE` added to `is_write_intexpr`/`arg_is_any` + walk_bb_flat write dispatch so `write(case …)` routes the matched value through the any-write trailer. Newly passing: rung33_case_{arith,int,str,in_proc,no_default}. Gates: FACT 0, bytes-outside-templates 0, canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 57 (5 pre-existing non-Icon fails). |
| IBB-9-INITIAL ✅ | 5/5 smoke; corpus same-sweep 95→100 (+5), SEGV 0, 0 regressions | `6d78e915` (Opus 4.8, 2026-05-29). **`initial expr` once-guard.** New `bb_initial.cpp` template + `flat_drive_initial`; moved `BB_INITIAL` off the `bb_stub` no-op (it emitted nothing → clause never ran). Runtime once-flag in `&pBB->counter` (calloc-zeroed, persists across slab re-entries — proc slab built once, `rt_icn_call_proc` never resets). Guard: read slot; `jne` γ (skip); else set slot=1; `jmp` body_entry. Driver walks `pBB->α` at body_entry (success→γ, failure→ω, propagating initial-clause failure as in mode-2). Newly passing: rung21_global_initial_{global_initial,initial_once}, rung25_global_{global_initial,initial_once,initial_zero}. Gates: FACT 0, zero-SM, smoke icon/prolog 5/5. |
| IBB-9-TOBY ✅ | 5/5 smoke; corpus same-sweep 93→95 (+2), SEGV 0, 0 regressions | `6d78e915` (Opus 4.8, 2026-05-29). **`write(lo to hi by step)`.** `BB_TO_BY` was missing from the write arg-recognition lists → `every write(1 to 10 by 3)` ABORTed (arg0_kind=17). Two-line fix: `BB_TO_BY` added to `is_write_intexpr` (`bb_call.cpp`) + `walk_bb_flat` BB_CALL write dispatch (`emit_bb.c`). Existing `flat_drive_call_intexpr` re-pump already cascades the every-resume into BB_TO_BY's β-advance — no new driver. Newly passing: rung01_paper_to_by + sibling. Gates: FACT 0, zero-SM, smoke 5/5. |
| IBB-9-SIZE ✅ | 5/5 smoke; corpus same-sweep 92→93 (+1), SEGV 0, 0 regressions | `254c93a6` (Opus 4.8, 2026-05-29). **`*E` (size) as a value-producing unop.** BB_SIZE routed to the STUB `bb_limit` in mode-3 (emitted nothing → write trailer ABORTed on arg0_kind=23). Rerouted to `bb_unop` + new `rt_unop_size`. Extracted `icn_size_value(DESCR_t,int*)` from the inline mode-2 BB_SIZE arm (string/list/record/table/cset length) as the single source of truth both modes call → byte-identical by construction; mode-2 refactor behavior-preserving (m2-as-oracle, 0 regressions). Newly passing: rung12_strrelop_size_size (`write(*s)`). Gates: FACT 0, canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5. `?E` (RANDOM) deferred (no corpus coverage). |
| IBB-9-CONCAT ✅ | 5/5 smoke; corpus same-sweep 82→92 (+10), SEGV 0, ABORT 146→133, 0 regressions | (Opus 4.8, 2026-05-29). **`||` string concatenation** — `s1\|\|s2` lowers to a tree-shape `BB_BINOP` op=ICN_BINOP_CONCAT (ival=11), the same shape as arith, driven by the op-agnostic `flat_drive_binop_tree`. The single largest concrete ABORT cluster (13 programs, `bb_binop: unsupported op ival=11`) is GONE. Fix: CONCAT arm in `bb_binop.cpp` (proven 32-byte arith layout, dead `movabs rdi,0`, calls `rt_icn_concat`) + new `rt_icn_concat` in `rt.c` routing through `icn_binop_apply` (the mode-2 oracle's CONCAT arm) so m2==m3 byte-identical by construction. Distinct from the SNOBOL4 `rt_concat`/`CONCAT_fn` (different descriptor convention, cross-family). Newly passing: rung04_string_concat{,_chain}, rung04_string_str_var, rung11_bang_augconcat_augconcat{,_chain,_loop}, rung32_strretval_{basic_strret,chain,strret_assign,two_str_params}. Gates: FACT 0, canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 51/11. **Deferred (→ IBB-9-4/5):** generator-bearing concat (rung11_bang_augconcat_bang_concat, rung13_alt_alt_augconcat, rung32_strretval_strret_every) now RUN but emit only the first generated value — needs generator re-pumping through the binop (the two-port `every` split). **NEXT:** the same-sweep ABORT residue is dominated by `bb_call: unsupported call shape` (Icon builtins: table/MAKELIST/set/list/string fns trim/reverse/repl/map/etc, write with non-int/non-str arg kinds); plus `every ival=2/3` (IBB-9-4/5); generator-proc dispatch; finish unop family (SIZE/RANDOM); BB_CASE; BB_AUGOP-in-every (rung10). |
| IBB-9-6 ✅ | 5/5 smoke; corpus same-sweep 69→82 (+13), SEGV 0, ABORT 0, 0 regressions | `8d4c2c2f` (Opus 4.8, 2026-05-29). **User-procedure dispatch** — JCON `ir_a_Call`/`ir_a_Return` in the flat-slab model. A user proc compiles to a `bb_build_flat` slab that leaves its return value on the vstack; `rt_icn_call_proc` binds params as named vars, invokes the slab (built LAZILY on first call), reads the result by vstack depth-delta, restores bindings. New `bb_return.cpp` template; `flat_drive_return` (routes to slab-level exit `flat_succ_p`, not next stmt); `flat_drive_call_userproc`; `BB_BINOP_GEN` non-streaming collapse (`n * fact(n-1)` → plain binop since a registered proc call is single-shot, matching the mode-2 oracle); `bb_call.cpp` userproc arm + `write(proc())` via any-write trailer; driver registers all proc entries + lazy builder. The `bb_call: unsupported call shape` ABORT cluster (~158 aborts) is eliminated. Newly passing: rung02_proc_add_proc/fact, rung03_suspend_fail/return, rung09_loops_repeat_counter/until_while, rung21_global_initial_×3, rung25_global_×4. Lazy build fixed 5 transient regressions (unreached procs with unsupported shapes). Gates: FACT 0, smoke icon/prolog 5/5, broker 51/11, zero-SM holds. **Deferred:** generator procs (`suspend` → needs odometer); rung02_proc_locals (blocked on `every ival=2`, IBB-9-4). |
| IBB-9-UNOP ✅ | 5/5 smoke; corpus same-sweep 62→69 (+7), SEGV 0, 0 regressions | `cc7995c4` (Opus 4.8, 2026-05-29). Value-producing unary ops `-E`/`+E`/`\E`/`/E`/`not E` (BB_NEG/POS/NONNULL/NULL_TEST/NOT). These routed to the `bb_cset`/`bb_stub` no-op stubs that emit ZERO mode-3 bytes → silent empty output. Fix: new grouped template `bb_unop.cpp` (relop control shape: call `rt_unop_*` helper which sets LAST_OK + pushes result, then `jmp γ` UNCONDITIONALLY so the BB_IF router branches in cond-context and write/assign consumers take the value in value-context); `flat_drive_unop` in `emit_bb.c` walks operand `pBB->α` first then emits the template (mirror of `flat_drive_binop_tree`); five `rt_unop_*` helpers in `rt.c` byte-faithful to mode-2 `bb_exec.c` arms; `bb_call.cpp` `is_write_intexpr`/`arg_is_any` + `walk_bb_flat` BB_CALL dispatch extended for unop write-args. Also fixed `--dump-bb` (was set into `g_opt_dump_bb` but never consumed → fell through to `--run` and ABORTed; now mirrors `--dump-sm` early-return via `sm_preamble`+`bb_print`, no native emission). Newly passing: rung07_control_{neg,not,repeat_break}, rung34_null_test_{nonnull_fails,nonnull_succeeds,null_fails,null_succeeds}. Gates: FACT 0, smoke icon/prolog 5/5, broker 49/11, zero-SM holds, regressions worktree-verified == 0. **Deferred:** `nonnull_in_every` (unop over generator-bearing chain → IBB-9-4); `*E` (BB_SIZE) + `?E` (BB_RANDOM) unops (same template slot, need their `rt_unop_*` helpers; SIZE needs DT_DATA/DT_T length). **NEXT:** the big lever remains user-proc dispatch (IBB-9-6, ~158 of the 167 aborts); or finish the unop family (SIZE/RANDOM), `||` lconcat, BB_CASE, BB_AUGOP-in-every (rung10). |
| IBB-6 ✅ | 5/5 canonical (m2 + m3) | `3aa200cd`. BB_BINOP_GEN odometer. |
| IBB-7 ✅ | 5/5 canonical; corpus 13→17 (+4) | `d1c55b0c`. BB_VAR + BB_ASSIGN flat-wire; AG-PURE deep-thread gates (ival==1 / dval==1.0). |
| IBB-8a ✅ | 5/5 canonical; corpus 17→32 (+15), SEGV 2→0 | `e9f09fdc`. xa_flat slab call-alignment (`sub/add rsp,8`) clears DT_R fprintf SEGV; DT_R write args (BB_BINOP/BB_BINOP_GEN) route through any-write trailer w/ canonical real_str. |
| IBB-9-1 ✅ | 5/5 canonical; corpus same-sweep 213→216 (+3), SEGV 0 | `e8f66866` (Opus 4.8, 2026-05-29). `every x := 1 to N do body` (static-TO assign). JCON-grounded: `ir_a_Every` treats it as `every (x:=GEN) do B`; `:=` ∈ `ir_binary` funcs → `expr.resume→right.resume` (assign transparent to resume). SCRIP: `lower_icn_new_Every_ag` intercepts TT_EVERY whose c[0] is TT_ASSIGN over a static literal TT_TO (BB_TO α==β==NULL) + plain TT_VAR lhs; interposes a BB_ASSIGN store node (ival=1, β=gen for mode-2 null guard) on the ival=1 topology (gen.γ=store, store.γ=body, body.γ=gen, body.ω=gen, gen.ω=bb). `flat_drive_every` ival=1 detects the store (β is BB_ASSIGN ival=1 w/ γ) and emits gen→store→body→gen_β; store's β routed to a dead store_ω stub (NOT gen_β — would self-jump gen_β into an infinite loop). TT_TO_BY excluded (keeps operand boxes). Mode-2 reads via ag_ring_peek(0); mode-3 pops vstack via rt_pop_nv_set. Newly passing: every_do_hello, block_body_nested_block, range_to. Gates: FACT 0, smoke icon/prolog 5/5, broker 42/11, zero-SM holds, no regressions. **NEXT (IBB-9-2):** `while C do B` — first verify the `do {block}` parser gap (`expected ; got while`), then transcribe JCON `ir_a_While` (body.success/failure → expr.START, the every-vs-while distinction). Then until (IBB-9-3), every ival=2/3 (IBB-9-4/5), user-proc dispatch (IBB-9-6, JCON `ir_a_Call`), write(BB_CALL) (IBB-9-7). |
| IBB-8c ✅ (partial) | 5/5 canonical; corpus same-sweep 28→46 (+18), SEGV 0 | `91874d71` (Sonnet 4.6, 2026-05-29). THREE fixes: (1) `bb_lit_scalar.cpp` **BB_LIT_F vstack-push** (`0be6e78d`) — mirror BB_LIT_I arm, bit-cast `pBB->dval`→u64, call `rt_push_real_bits` (existing helper used by sm_push_pop_lits.cpp); 32-byte layout, sites {23,27,28}. Fixes rung18 real relops real_gt/real_lt/real_eq/mixed_relop (4/5; real_relop_goal still fails — float LHS in BB_BINOP_GEN gen-context). (2) `emit_bb.c` **BB_SEQ_EXPR flat-wire** (`37517836`) — `{}` block then/else lowers to BB_SEQ_EXPR (γ-chain off α, identical topology to BB_SEQ); `walk_bb_flat` had no case → hit `default:` → silent no-output. Routed through `flat_drive_seq`. Fixes rung35_block_body_if_block/if_else_block. (3) `emit_bb.c` **every-E-do-body ival=1** (`91874d71`) — `every 1 to 3 do write("x")` two-node gen↔body loop; walk gen γ→body_α ω→outer-γ β→gen_β; walk body γ/ω→gen_β (re-pump). Body result discarded, runs once per generated value. Gates: FACT 0, smoke icon/prolog 5/5, broker 39/14, zero-SM holds, no regressions. **NEXT (IBB-8c cont):** every-do ival=2 (gen-bearing chain) and ival=3 (BODY-MEDIATED BB_SEQ_EXPR block + phase machine on bb->state) — corpus rung35 `every x:=1 to 3 do {block}` cases; then while-do-body (rung35_block_body_while_do_block, empty m3, needs while driver + augop body); then real_relop_goal; then write(BB_CALL), user-proc dispatch. |
| IBB-8b ✅ (partial) | 5/5 canonical; corpus same-sweep 22→28 (+6), SEGV 0 | `0e926c16` (Opus 4.8, 2026-05-29). STRING relops in if-condition. Three pieces: (1) `bb_binop.cpp` AG-pure relop/strrel apply arm — `rt_acomp`(numeric)/`rt_lcomp`(string) + unconditional `jmp γ` (both ports of an AG-pure relop reach the BB_IF router, per mode-2 oracle); (2) NEW `bb_if.cpp` router — `rt_pop_void; rt_last_ok; test eax,eax; jz ω(else); jmp γ(then)`; (3) `flat_drive_seq` rewritten from γ-only linear walker into a **node-keyed CFG emitter** (BFS follows γ always, ω ONLY for BB_IF so operand children aren't double-emitted; non-IF nodes keep outer lbl_ω as baseline; one stable arena label per node). AG-pure BB_BINOP routes to FILL; added `case BB_IF`. BB_SEQ is Icon-exclusive → no cross-family impact. Newly passing: rung12_strrelop_size_{slt,sge,sne}, rung37_strrelop_hello, rung07_control_seq, canonical if_expr crosscheck. Gates: FACT 0, smoke icon/prolog 5/5, broker 39/14, zero-SM holds, no regressions. **NOTE:** the "32" in the IBB-8a row used a different corpus filter than this same-sweep 22→28 (+6) measurement — reconcile gate methodology before trusting absolute counts; the +6 delta is apples-to-apples. **NEXT (IBB-8c):** real relops need **BB_LIT_F vstack-push** — `bb_lit_scalar.cpp` BB_LIT_F path is a pass-through stub that never pushes the real (mirror the BB_LIT_I arm with a DT_R DESCR_t push); rung18_real_relop_* blocked on this. Then block-body if (rung35_block_body_if_*) needs nested-block flattening. Then every-E-do-body (~4), write(BB_CALL), user-proc dispatch. |
