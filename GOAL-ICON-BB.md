# GOAL-ICON-BB.md — All Icon Byrd-Box constructs, modes 1/2/3/4

**Repo:** one4all + .github · **Sister:** GOAL-CHUNKS*, GOAL-LANG-ICON · **Carved:** 2026-05-10

---

## ⛔ MODE PRIORITY (Lon, 2026-05-26) — MODE 2 then 3; MODE 4 DEFERRED

Get correctness in **mode 2 (`--interp`)** first, then **mode 3 (`--run`, in-proc)**. **Mode 4
(`--compile`) is DEFERRED until further notice** — it is the slowest to iterate (emit asm → gcc -c →
link libscrip_rt → run) and should not gate generator/AG work. Bring constructs up in 2→3 order;
mode 4 follows for free once 3 is flat-wired (mode 3 ≡ mode 4 x86, differing only in process
boundary). Do NOT spend a session round-tripping mode-4 binaries while mode 2/3 still have gaps.

---

## ⛔⛔ NEXT SESSION — START HERE. ICN-Z-ATOMIC FAMILIES 3-7. (added 2026-05-27, Opus 4.7)

**Status**: PEERS RULE landed (`78e4c067`). Families 1 (BB_ASSIGN) and 2 (BB_CALL)
migrated to the sidecar. All gates green. See `SESSION-2026-05-27-OPUS-PEERS-RULE.md`
in one4all for the full handoff.

### THE PEERS RULE (new HQ Invariant 17, supersedes the GOLDEN BB RULE)

BB_t stays LEAN. Per-kind auxiliary structure that correlates to BB nodes lives in
CFG-OWNED SIDECARS, not in BB_t fields:

1. **α/β/γ/ω**: control-flow ONLY (four AG attributes).
2. **Operand-value references**: `BB_graph_t.operand_aux` sidecar, keyed by `BB_t*`,
   holding an ordered list of peers whose `->value` the apply step reads.
3. **sval/ival/dval**: IR payload (unchanged).
4. **value/counter/state**: runtime per-activation state (unchanged).

API:
```c
int bb_operand_aux_set(BB_graph_t *cfg, BB_t *nd, BB_t * const *src, int n);
BB_t * const *bb_operand_aux_get(const BB_graph_t *cfg, const BB_t *nd, int *out_n);
```

`bb_exec.c` has `g_current_cfg` (module-static) set with save/restore around each
public `bb_exec_*` entry so recursive callees don't clobber the caller's sidecar.

DO NOT add fields to BB_t. New per-kind aux → new sidecar in BB_graph_t.

### Families 3-7 — mechanical pattern (each is one gate cycle)

3. **BB_BINOP** — 2 operands. Lower: `lhs.γ = rhs.α; rhs.γ = apply; both ω = ω_in;
   bb_operand_aux_set(cfg, nd, {lhs,rhs}, 2)`. Exec: read `ops[0]->value`,
   `ops[1]->value`, apply `icn_binop_apply`. Suspendable operand → BB_BINOP_GEN
   (Family 7).
4. **BB_IF** — 1 operand (condition). Then `icn_kind_owns_omega_operand` retires
   (BB_IF stops using ω as the else-branch operand; ω becomes pure failure port).
5. **BB_CONJ** — 2 operands. Per `ir_conjunction` (irgen.icn:405).
6. **BB_ALT** — N operands. Per `ir_a_Alt` (irgen.icn:167).
7. **BB_EVERY / BB_TO / BB_TO_BY / BB_BINOP_GEN** — generator kinds. β=self for
   resumability (`icn_kind_is_resumable`).

### Gate set after EACH family
- `bash scripts/test_smoke_icon.sh` PASS=5
- `bash scripts/test_icon_all_rungs.sh` PASS ≥ 198
- `bash scripts/test_smoke_prolog.sh` PASS=5
- `bash scripts/test_smoke_unified_broker.sh` PASS ≥ 24
- `grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l` == 0

### Acceptance for the whole rung
1. All 7 families on the sidecar; each apply step reads via `bb_operand_aux_get`.
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0 in composite cases.
3. `icn_kind_owns_omega_operand` removed.
4. rungs PASS ≥ 198 holds.

### DO NOT, this rung
- Do NOT touch SNOBOL4 / Snocone / Rebus / Raku BB families.
- Do NOT touch BB_PAT_*.
- Do NOT add fields to BB_t — sidecars only.

---

## ⛔⛔ PRIOR SESSION CHECKPOINT — RUNG ICN-Z-ATOMIC. FIRST RUNG, FIRST STEP. (added 2026-05-27e, Opus 4.7)

**RUNG ICN-Z-ATOMIC — wholesale conversion of operand-bearing composites to 4-port threaded form,
ONE pass. Do this FIRST, the moment the session opens. Fresh context required (~80%+); the surface
is ~68 `lower_icn_expr_node` sites + ~11 `bb_exec.c` composite cases + a storage-convention change.**

### Why wholesale, NOT incremental (read once)
`bb_exec_node` is a SHARED driver. Today's composite cases (BB_BINOP line 677, BB_BINOP_GEN 693,
BB_CALL 54/478, BB_ASSIGN 422, BB_IF 827, BB_CONJ 854, BB_EVERY 871, BB_ALT 988, BB_TO_BY 1041,
BB_TO 1954) all treat `nd->α` and `nd->β` as **operand-child pointers** — the operand SUBTREES are
stored in α/β and reached by recursive `bb_exec_node(nd->α)`. Convert ONE construct's α/β to be a
control-flow port while its siblings keep operand-child semantics → the shared driver cannot
distinguish "recurse this child" from "follow this port," because both are `BB_t*`. Hybrid breaks.
Either all composites use α/β as ports, or none do. 100 small-rung iterations cannot reach a
self-consistent state — only a wholesale change can.

### The storage convention (the structural insight — read twice)
JCON's irgen does NOT have an operand-child relation. Every operand chunk is a peer in the chunk
list, glued by `ir_Goto`. The 4 ports of a binop in irgen are LABELS on the parent's chunk; the
operand subtrees are reached by `Goto` to their `.start`. `BB.h`'s GOLDEN BB RULE comment forbids
adding `lhs/rhs/c[]/n` to `BB_t` ("DO NOT add c[], n, lhs, rhs, operand..."). So the conversion is:
stop storing operand subtrees in `BB_t.α/β`. Build operands as separate `BB_t` nodes in the SAME
`cfg->all[]` pool. Parent's `α`/`β` become PURE CONTROL-FLOW PORTS (continuation labels). Operand
graphs are reached the same way JCON reaches them: by Goto from the parent's α-chunk to the
operand's α, and the operand's γ/ω fold back into the parent's next-port continuation. The graph
of α-entries and γ/ω-continuations forms the runtime CFG; there is no operand-child tree.

The runtime payload for the operand binding is the operand's `value` field (the result the parent
reads after the operand's γ port fires). `bb_exec.c` becomes a pure port-follower: dispatch on `nd`,
write `nd->value`, return the next port. NO `bb_exec_node(nd->α)` recursive call anywhere.

### EXACT STEPS (do in order, gate after EACH group)

**Step 1 — Read the AG (no code yet).** Open `/home/claude/jcon/jcon-master/tran/irgen.icn` (cloned
from the JCON master in HANDOFF-2026-05-27-OPUS-ICON-BB-ICN-Z-2B context) and read these procedures
in full: `ir_a_Binop` (472), `ir_binary` (430), `ir_a_Call` (360), `ir_a_If` (577), `ir_a_Every`
(309), `ir_a_Alt` (167), `ir_a_ToBy` (1168), `ir_conjunction` (405), `ir_a_Compound` (1231),
`ir_a_ProcBody` (774), and `ir_init` (1426). Build the port-wiring table on paper before touching C.

**Step 2 — Storage convention.** In `lower_icn.c`, change every `lower_icn_*` builder that today
sets `nd->α = lhs_subtree` / `nd->β = rhs_subtree` to instead: (a) allocate the operand subtrees as
PEER `BB_t` nodes via `BB_node_alloc`, (b) thread `nd->α` to the lhs-operand's `α` (its start), (c)
wire lhs-operand's `γ` to the rhs-operand's `α` (or to a synthesized "after-lhs" continuation that
caches `lhs->value`), (d) rhs-operand's `γ` to the parent's apply-chunk, which writes `nd->value`
and returns `nd->γ`. Failure ports fold to `nd->ω`. Mirror `ir_a_Binop` exactly — DO NOT invent.

**Step 3 — bb_exec.c.** Delete the operand recursion in every composite case. Each case becomes:
read `nd->value` (already set by the predecessor port-firing), apply the per-kind operation if any,
write the result to `nd->value`, return the appropriate port. NO `bb_exec_node(nd->α)` calls. The
driver is now a pure port-follower: `while (nd) { nd = bb_exec_node(nd); }`.

**Step 4 — Gate ALL of these after each construct family lands, NOT after each site:**
- `bash scripts/test_smoke_icon.sh` PASS=5
- `bash scripts/test_icon_all_rungs.sh` PASS ≥ 198 (target: monotonic increase)
- `bash scripts/test_smoke_prolog.sh` PASS=5
- `bash scripts/test_smoke_unified_broker.sh` PASS ≥ 23
- `grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l` == 0
- Sanity: `printf 'procedure main()\n write("a")\n write("b")\nend\n' | ./scrip --interp /dev/stdin` MUST print `a\nb\n` (today prints only `a` — this is the litmus for the whole rung)

**Step 5 — Construct families, do in THIS order (each is one gate cycle):**
1. **BB_ASSIGN** (simplest non-leaf with 1 operand subtree — `target := value`). Bridge from leaf.
2. **BB_CALL** (the multi-write blocker). Operands are the argument list; gluing each arg's γ to
   the next arg's α, last arg's γ to the call's apply chunk, all ω to the call's ω.
3. **BB_BINOP** (2 operand subtrees, well-known shape; irgen `ir_binary`).
4. **BB_IF** (note: `ir_a_If` — condition's success→then.α, failure→else.α; then/else γ both →
   parent.γ, ω → parent.ω). `icn_kind_owns_omega_operand` retires when IF stops using ω as operand.
5. **BB_CONJ** (`ir_conjunction` — e1.γ→e2.α; e2.γ→parent.γ; e1.ω→parent.ω; e2.ω→e1.β).
6. **BB_ALT** (`ir_a_Alt` — e1.γ→parent.γ; e1.ω→e2.α; e2.γ→parent.γ; e2.ω→parent.ω; β→e1.β
   for re-entry).
7. **BB_EVERY** / **BB_TO** / **BB_TO_BY** / **BB_BINOP_GEN** (generator kinds — read `ir_a_Every`
   and `ir_a_ToBy`; resumable β=self stays per `icn_kind_is_resumable`).

**Step 6 — Retirements.** When step 5.4 lands, delete `icn_kind_owns_omega_operand` (and its
forward declaration added by ICN-Z-2b) — IF no longer owns ω as operand. The BB_IF guard in
ICN-Z-2b's `lower_icn_proc_body` post-pass and in BB_SEQ's port-follower can both go.

### DO NOT, this rung
- Do NOT touch SNOBOL4 / Snocone / Rebus / Raku BB families (different ports/semantics).
- Do NOT touch BB_PAT_* or pattern-matching (different driver).
- Do NOT add `lhs/rhs/c[]/n` to `BB_t` — the GOLDEN BB RULE forbids it; operands are PEERS not
  children.
- Do NOT half-zip across step 5's families. Either a family is fully converted and green, or it is
  not started this session.

### Acceptance — the rung is done when:
1. The 6-gate set in step 4 is green AND the multi-write sanity passes (`a\nb` not just `a`).
2. `grep -rnE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0 (no operand recursion).
3. `icn_kind_owns_omega_operand` removed.
4. rungs PASS ≥ 198 holds; ideally rises (more multi-stmt programs now work).

---




`lower_icn.c` 2-arg `lower_icn_expr_node(cfg,e)` call sites to convert to 4-port threaded (68 total):
lines 184 188 203 205 217 219 221 235 237 253 255 268 285 308 325 345 350 354 381 382 402 403 424 428
460 464 486 505 507 546 548 577 590 605 607 617 628 630 645 647 649 668 681 683 705 714 730 745 747
759 761 790 810 812 822 834 843 853 864 874 885 898 900 916 950 969 1033 1115.
`bb_exec.c` composite cases to convert to port-follower: BB_CALL(54/478) BB_ASSIGN(422) BB_SEQ(613)
BB_BINOP(672) BB_BINOP_GEN(688) BB_IF(822) BB_CONJ(849) BB_EVERY(866) BB_ALT(983) BB_TO_BY(1036)
BB_TO(1949). Read each construct's `ir_a_*` in `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`
BEFORE wiring it. ONE pass, mode-2 green at each group, cannot half-zip.

---



⛔ **SESSION 2026-05-27c (Opus 4.7) — ICN-XA-1 LANDED + the `lt`/`mult`/`compound` mode-4 FAILs FIXED. mode4_rung PASS=2→5 FAIL=0.**

**KEY CORRECTION to the prior watermark's BINOP_GEN target.** The prior "sharper target" assumed
mode-4 routed `mult`/`lt`/`compound` through `bb_binop_gen.cpp` and only needed a template fill. Tracing
the ACTUAL mode-4 lowering showed it did NOT: `lower_mul`/`lower_acomp` (lower.c) emitted a FLAT SM
scaffold (`SM_BB_SWITCH; SM_BB_SWITCH; SM_MUL`) — TWO independent `BB_TO` graphs with no cross-product
driver between them. The single every-loop back-edge re-drives only the first switch → wrong output.
`bb_binop_gen.cpp` was NEVER reached in mode-4 for these programs. So the gate-movers needed BOTH a
lowering change AND the template fill — not template-only.

**DONE (real, verified, non-regressing):**
1. **ICN-XA-1 `walk_bb_node_str_c`** (emit_core.c/.h): `BB_t* → char*` variant — swaps the shared
   emit sink to an `open_memstream` FILE* around the EXISTING `walk_bb_node` dispatch, restores after.
   NOT a second producer: every byte still originates in the keyed template fns (FACT RULE grep 0).
   `sm_bb_switch.cpp` ICN_GEN arm rewired to `pre + walk_bb_node_str_c(gen) + post` — the LOCAL-PURGE
   violation (`emit_text_n` + `walk_bb_node` mid-`_str()`) is GONE; the arm is now pure.
2. **Generator-binop routing** (lower.c): `lower_add/sub/mul/div/mod/acomp` now call
   `lower_icn_gen_binop(t)` first — if an operand is suspendable, register the WHOLE binop subtree as
   ONE BB graph (`lower_icn_expr_top` builds BB_BINOP_GEN w/ α=lhs β=rhs operand boxes) and emit a
   SINGLE `SM_BB_SWITCH` (exactly like `lower_to`). Mode-4 now routes through `bb_binop_gen.cpp`.
3. **`bb_binop_gen.cpp` real odometer** (TEXT/mode-4): inline x86 cross-product mirroring `bb_exec.c`
   BB_BINOP_GEN (688-762). Seeds outer (lhs) + inner (rhs); on β advances inner, on inner-exhaust
   advances outer + re-seeds inner; applies via `rt_arith` (arith) / `rt_acomp`+`rt_last_ok` (relop,
   with relop-fail retry); outer-exhaust → ω. Operand boxes emitted INLINE: generators via
   `walk_bb_node_str_c`, BB_LIT_I single-shot via `synth_single_shot_box`. DESCR_t pop reads union
   `.i` from **rdx** (16-byte struct SysV ABI — `v|slen`→rax, union→rdx; the all-`36` bug was reading
   rax). Nested BINOP_GEN (compound) works: non-static child labels avoid reentrancy aliasing.

**GATES: smoke_icon 5/5 · broker 23 · icon_all_rungs 198 · smoke_prolog 5/5 (ALL unchanged) ·
mode4_rung PASS=5 FAIL=0 (was 2/3) · FACT RULE grep 0.** `lt`→`3,4`; `mult`→`1,2,2,4,3,6`;
`compound`→`4,6` — all byte-exact vs `--interp`.

**ICN-M4 follow-on (documented, not blocking):** `synth_single_shot_box` handles BB_LIT_I only; BB_VAR
/BB_KEYWORD/non-int-literal single-shot operands fall to a `[non-gen … inline TODO]` port-stub (jmp ω).
DT_I round-trip in the apply path assumes integer operand generators (true for the gate seed set);
real/string operand values need a descr-preserving holding cell. BINARY (mode-3 brokered) arm is still
the α→γ/β→ω passthrough stub — mode-4 TEXT is the gate path per the MODE-PRIORITY directive.

---



⛔ **SESSION 2026-05-27b (Opus 4.7) — ICN-Z-0 + ICN-Z-1 landed; ICN-Z-2 substantial; ICN-Z-3 found BLOCKED.**
ICN-Z-0: `icn_leaf(nd, γ_in, ω_in, &α_out, &β_out, bounded)` + bounded-aware
`lower_icn_expr_threaded_b` (both exported). Bounded rule mirrors irgen + lower_pl.c:
`β=(!bounded && icn_kind_is_resumable) ? self : ω_in`. ICN-Z-1: `icn_tree_is_leaf` classifier;
leaves seed `bounded=1` forced, decoupling leaf β=ω from the resumable table. ICN-Z-2 substantial:
proc-body statement chain lowers `bounded=1` + `bb_exec.c` BB_SEQ already walks the γ-chain forward
(non-backtracking advance per ir_a_Compound); remaining = explicit ω→next.α port wire for mode-3/4.
ALL gates non-regressing: smoke_icon 5/5, broker 23, icon_all_rungs 198, smoke_prolog 5/5,
mode4_rung PASS=2, FACT-RULE grep 0.

⚡ **KEY FINDING — the mode-4 `lt`/`mult`/`compound` FAILs are gated on the FULL ICN-Z pass, not on
any single rung or template.** Verified three ways this session: (1) **Scaffold:** mode-2 passes only
via `SM_BB_PUMP_PROC` (C graph-walk that nests generators); mode-4 runs the flat SM scaffold whose
`SM_JUMP` back-edge re-drives only the innermost generator (emits `2,4,6` not the cross-product).
(2) **Template:** `bb_binop_gen.cpp` is a port-wired stub (α→γ, β→ω; real odometer marked
`TODO(mode-4)`). (3) **BB_CONJ (ICN-Z-3):** isolated rewire blocked by FINAL `BB_t` + operand-bearing
α/β.

⚡⚡ **CORRECTION + SHARPER TARGET (2026-05-27b, Opus 4.7 — supersedes the BINOP_GEN half of the
finding above).** Re-checked the lowering: for `(1 to 3)*(1 to 2)` the BINOP_GEN node holds its TWO
operand generators DIRECTLY — `nd->α` = the `1 to 3` BB_TO box, `nd->β` = the `1 to 2` BB_TO box
(lower_icn.c:513-514). They ARE reachable from `bb_binop_gen(nd)` at emit time; the emitter walks the
graph. So `mult`/`lt`/`compound` are NOT blocked on the driver/scaffold — they are a **template-only**
fix: make `bb_binop_gen.cpp` emit the cross-product odometer inline, recursively emitting its α and β
operand boxes via the same inline-walk `sm_bb_switch.cpp` uses (set `g_emit.lbl_α/β/γ/ω`, then
`walk_bb_node`). The odometer oracle is `bb_exec.c` BB_BINOP_GEN (677-743): seed both on α; on β
advance inner (β), on inner-exhaust reset inner.state=0 + advance outer (α); on relop-fail retry the
loop; outer-exhaust → ω.
**THE ONE REAL PREREQUISITE is ICN-XA-1's `walk_bb_node_str` (a `BB_t* → std::string` variant of
`walk_bb_node`, which currently writes only to `FILE*`).** Without it, a parent template that emits
child boxes inline must interleave `emit_text_n(...)` + `walk_bb_node(...)` mid-body — exactly the
LOCAL-PURGE / template-purity violation ICN-XA-1 names (sm_bb_switch.cpp:78 does this; do NOT copy it
into a clean BB template). **Next-session plan, small + template-only: (a) ICN-XA-1 — add
`walk_bb_node_str` (refactor emit_core.c:476 `walk_bb_node` to build a string via open_memstream or a
string sink, with the FILE* version a thin wrapper); (b) fill `bb_binop_gen.cpp` odometer using it; (c)
gate climbs mode4_rung PASS=2→5.** This is far smaller than the driver rewrite the ICN-Z-3 finding
implied for the conjunction case — CONJ still needs the full pass, but the gate-moving binop cases do
NOT.

⛔ **SESSION 2026-05-27b (Opus 4.7) — ICN-Z-0 + ICN-Z-1 landed; ICN-Z-2 substantial; ICN-Z-3 BLOCKED finding; BINOP_GEN target corrected.**

---

## ⚡ PRIOR WATERMARK (one4all `3a522bd8` — pushed 2026-05-27, Opus 4.7 session; rebased onto upstream Prolog AGW-9A `701403cb`)

GATES: smoke_icon **5/5** ✅ · broker **23** · icon_all_rungs **198** ✅ · smoke_prolog **5/5** ✅
(2026-05-26, Opus 4.7: every-loop control ports FLAT-WIRED per ir_a_Every — `gen.γ→body`,
`body.γ→gen`, `body.ω→gen`, `gen.ω→every` — additive over literal generators; mode-2 oracle intact.
`lower_every` SM back-edge also fixed. β-synthesis in lower_icn_expr_threaded now matches Prolog
zipper rule (resumable→self, single-shot→ω_in via new icn_kind_is_resumable). FACT-RULE 0.)
✅ `grep -rnE 'seg_byte\(SEG_|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/` outside `*_templates/`+`emit_core.c` == **0**.

⛔ **SESSION 2026-05-26 (Sonnet) — J-4a LOWER + SM template + BB box reached; ONE bug remains.**

**DONE (real, verified, non-regressing — smoke_icon 5/5, rungs 198, smoke_prolog 5/5, FACT-RULE 0):**
1. **LOWER fixed (mode-2 generators now correct end-to-end).** `lower_to`/`lower_to_by` (lower.c)
   were building the BB graph then FREEING it + emitting `SM_PUSH_NULL` — the root cause of dead
   generators. Now they `SM_seq_bb_add(g_p,cfg)` to register the graph and emit `SM_BB_SWITCH`
   carrying the bb_idx, tagged `SM_BBSW_ICN_GEN` (new tag in SM.h, twin of SM_BBSW_PL_ENTRY).
   `sm_interp.c` SM_BB_SWITCH consumer got the Icon-gen arm: `bb_exec_once` first / `bb_exec_resume`
   after, γ pushes value + last_ok=1, ω resets a[0].i + last_ok=0. SM dump now shows `SM_BB_SWITCH`
   at the generator slot (was `SM_PUSH_NULL`); `every write(1 to 3)` prints `1 2 3` in --interp.
2. **SM template created** `src/emitter/SM_templates/sm_bb_switch.cpp` (wired: sm_templates.h,
   emit_core.c dispatch de-stubbed, both Makefile lists + per-file compile rule). MACRO_DEF/BINARY/
   TEXT arms. ICN_GEN TEXT arm fetches `g_stage2.sm.bb_table[idx]->entry`, sets α/β/γ/ω labels, and
   calls `walk_bb_node(gen)` — emitting the generator box's four-port x86 INLINE at emit time
   (no runtime BB walk, no C Byrd box — RULES-clean).
3. **BB box now reached + emits valid x86.** Fixed `bb_icn_to.cpp` TEXT yield: was raw-r12 push
   (brokered convention) → segfault in SM mode-4 ABI; now `mov rdi,rcx; call rt_push_int@PLT`
   matching bb_upto's TEXT convention. mode-4 emit of `every write(1 to 3)` now contains the real
   `# BOX TO(lo=1 hi=3)` inline four-port body (α sets cur, β increments, chk `jg ω`, yields via
   rt_push_int); assembles + links clean.

✅ **`lower_every` back-edge target — FIXED (2026-05-26, Opus 4.7).** The diagnosed bug
(`switch_pc = SM_label(g_p)-1` captured the CALL PC, not the SWITCH PC) is now fixed in
`lower.c` `lower_every`: capture `gen_start = g_p->count` BEFORE `lower_expr(gen_expr)`, then
scan forward `[gen_start, g_p->count)` for the first `SM_BB_SWITCH` and use that PC as the
back-edge target. SM dump now shows `SM_JUMP -> 2` (the SWITCH), not `-> 3` (the CALL). The
stray `SM_LABEL` the old `SM_label()` side-effect emitted is gone (count 15→14). **mode-2
`every write(1 to 3)` → `1 2 3` ✅; gates non-regressing (smoke_icon 5/5, broker 23, rungs 198,
smoke_prolog 5/5, FACT-RULE 0).**

⛔ **MODE 3 (`--run`) IS A GLOBAL STUB.** `--run` currently prints
`[NO-SM-BB] --run: linear emitter deleted (FACT RULE); use --interp until templates land` — the
SB-LINEAR emitter was deleted under the FACT RULE and the `bb_*`/`sm_*` mode-3 templates have not
landed. This is NOT Icon-specific; it is the Phase J work. **NEXT for this goal (per Lon's
MODE-PRIORITY directive): bring `--run` (mode 3) up via the shared template producer** — route
`--run` through `sm_emit_linear`→`sm_run_linear` (PROT_EXEC slab), reusing the SAME template
functions mode 4 uses, so mode 3 and mode 4 stay byte-identical. Until `--run` exists, generator
correctness can only be validated in mode 2.

🟡 **MODE 4 (`--compile`) — ω-exhaustion fall-through FIXED (2026-05-27, Opus 4.7).** The
generator-exhaustion (ω) path no longer falls through to the consumer. Per irgen ir_a_Every
(`p.expr.failure → p.ir.failure`), `lower_every` now stamps the loop-exit PC on the SWITCH's free
`a[0].i`, and `sm_bb_switch.cpp`'s ω arm emits `jmp .L<exit_pc>` (after `last_ok=0`), skipping the
welded consumer entirely. `every write(1 to 5)` → `1 2 3 4 5` in mode-4, byte-matching `--interp`.
**ICN-G-1 gate PASS=1** (was 0). Emitted inside the template — no second producer (FACT RULE 0).
REMAINING mode-4 generator gaps are NOT this bug: filter/cross-product cases (`every write(2<(1 to
4))`, `(1 to 3)*(1 to 2)`) run clean (no underflow) but emit no output because `SM_ACOMP` and the
binop-generator opcodes lack honest mode-4 templates — a separate rung (ICN-M4-* / per-opcode), not
every-loop wiring. `to_by` filter likewise.

**Files touched this session (Opus 4.7, mode 2/3 focus):** src/lower/lower.c (lower_every scan fix),
src/emitter/SM_templates/sm_bb_switch.cpp (α/β dispatch — mode-4, deferred). NOT yet committed.

**GATE-PK still RED/stale (455/62/592) since `a5775d1a` — owner decision on re-freeze pending. With
mode 4 deferred, GATE-PK is not a blocking gate; revisit when mode 4 resumes.**

⛔ **SESSION 2026-05-27 (Opus 4.7) — ICN-G-1 gate + mode-4 generator fixes; gate PASS=0→2.**
(1) Added `scripts/test_icon_mode4_rung.sh` (full native pipeline vs `--interp`). (2) Fixed every-loop
ω-exhaustion: `lower_every` stamps loop-exit PC on SWITCH `a[0].i`; `sm_bb_switch.cpp` ω arm emits
`jmp .L<exit>`, skipping the consumer (`every write(1 to N)` → correct). (3) `emit_sm.c` now registers
the SWITCH's ICN_GEN `a[0].i` exit PC as a jump target so `.L<exit>:` is emitted (label-analysis only,
not codegen — FACT RULE intact). (4) Fixed `sm_compare.cpp` ACOMP/LCOMP GAS macro: was `mov edi, 0`
discarding its kind arg → every comparison ran as op 0; now `mov edi, \n` (+ BINARY arm passes the
real kind). (5) Fixed `bb_to_by.cpp` TEXT yield: was raw-r12 (BINARY/brokered convention) →
SEGFAULT in mode-4; now `mov rdi,rcx; call rt_push_int@PLT` (Goal trap #2; mirrors bb_icn_to).
**ICN-G-1 PASS=2** (`to5`, `to_by`). ALL regression gates non-regressing (smoke_icon 5/5, broker 23,
rungs 198, smoke_prolog 5/5); FACT RULE 0. Remaining 3 FAILs (`lt`/`mult`/`compound`) are
filter/cross-product cases needing the BB-port-graph zipper (operand re-eval across the back-edge —
the flat SM scaffold cannot express it; documented in lower_every). Files: scripts/test_icon_mode4_rung.sh
(NEW), src/lower/lower.c, src/emitter/SM_templates/sm_bb_switch.cpp, src/emitter/emit_sm.c,
src/emitter/SM_templates/sm_compare.cpp, src/emitter/BB_templates/bb_to_by.cpp.

---

(prior NEXT, still valid follow-on) fill hollow pattern arms SPAN→ANY→NOTANY→BREAK→CAP→ARBNO.

Files to fill:
- `src/emitter/BB_templates/bb_pat_span.cpp` — SPAN(cset)
- `src/emitter/BB_templates/bb_pat_any.cpp` — ANY(cset)
- `src/emitter/BB_templates/bb_pat_notany.cpp` — NOTANY(cset)
- `src/emitter/BB_templates/bb_pat_break.cpp` — BREAK(cset) + BREAKX
- `src/emitter/BB_templates/bb_capture.cpp` — CAP
- `src/emitter/BB_templates/bb_arbno.cpp` — ARBNO(pat)

Each gets TEXT + BINARY x86 four-port body (α fresh-entry, β retry, γ success, ω fail).
Anchor gate per template: broker pattern rungs climb from RED.
`rt_cs_new` (allocates `rt_cs_t {chars,delta}`) is still live — use it for the charset state pointer.
ARBNO needs a growable frame stack; stash ptr in `pBB->counter` (intptr cast), or GC aux struct.

---

---

## ⚡ CORRECTIVE RUNGS — ZIPPER + GATE (added 2026-05-27, revised vs irgen 2026-05-27, Sonnet 4.6)

**Root diagnosis — read irgen.icn before any session touching lower_icn.c:**

The irgen.icn in `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` is the canonical source of truth for every construct's port wiring. Read the actual procedure before implementing any construct — do not rely on summaries. The following defects are confirmed against irgen:

1. **ICN-1/ICN-2 — α/β USED AS OPERAND-CHILD POINTERS.** In lower_icn.c, BB_IF stores else in `nd->ω`, BB_CALL stores args via `nd->α` γ-chain, BB_ASSIGN stores lhs/rhs in α/β. bb_exec.c walks these as child trees — AST-walking-in-disguise. Fix: one-pass signature change to carry `γ_in/ω_in/&α_out/&β_out`. See ICN-Z below.
2. **ICN-3 — NO MODE-3/4 RUNG GATE.** `test_icon_all_rungs.sh` is `--interp` only. Fix: ICN-G-1.
3. **ICN-4 — sm_bb_switch TEXT ARM VIOLATES TEMPLATE PURITY.** Calls `emit_text_n` mid-body, then returns a string. Fix: ICN-XA-1.
4. **ICN-5 — every-loop SM SCAFFOLD REDUNDANT POST-ZIPPER.** After lower_icn is fully zipper-wired, every's back-edge is a BB port wire, not SM_JUMP. Fix: ICN-Z-5.

**CRITICAL irgen-verified corrections to the prior HOW AG-LOWERING section in this file:**

- **`bounded` is NOT optional.** irgen's signature carries `bounded`: `/bounded &` guards mean the resume chunk is omitted when the context is always-bounded. In always-bounded context, β=ω_in (no retry exists), even for generator kinds. The zipper must carry a bounded flag; `icn_leaf` must respect it.
- **BB_EVERY: body.ω→expr.β, NOT body.γ→expr.β.** irgen `ir_a_Every`: BOTH `body.ir.success` AND `body.ir.failure` go to `expr.ir.resume` (≡ our expr.β). Body success and body failure both re-drive the generator. Body never fails the every-loop — only expr.failure exits to p.ir.failure. The prior HOW section said only "body.γ→expr.β"; it omitted body.ω→expr.β, which is equally essential.
- **BB_COMPOUND: intermediate statement failure ADVANCES, not retries.** irgen `ir_a_Compound`: `L[i].ir.failure → ir_Goto(L[i+1].ir.start)`. Intermediate statement failure is non-fatal and advances to the next statement. **Do NOT apply the Prolog back-to-front zipper to BB_COMPOUND/BB_SEQ.** That zipper is for `ir_Mutual` / Icon `(e1;e2;e3)` mutual evaluation (which does backtrack). Compound statements do not.
- **BB_IF: unbounded context needs an `ir_TmpLabel` resume-pointer slot.** irgen `ir_a_If` in `/bounded` context stores the active branch's resume label in a temp slot `t` (indirect goto register) so the if-node's own β can re-enter the correct branch. Simple `cond.γ→then.α, cond.ω→else.α` is only correct for always-bounded (no-retry) context. In unbounded context, implement the label-register pattern.
- **BB_TOBE / ToBy: operand evaluation is one-time (α only); β is internal.** irgen `ir_a_ToBy` uses `ir_ResumeValue` (resuming a closure) for its own resume chunk — this maps to our BB_TO_BY node's β being **self** (the node increments counter and re-checks bounds internally). The operand sub-expressions (from/to/by) are evaluated once via their own sub-graphs wired `from.success→to.start→by.start`. After by.success the closure/counter is set and the node yields. **β does not re-enter the operand sub-graphs.** The current code's α=lo_box, β=hi_box is wrong because it re-evaluates bounds on every resume.
- **BB_ALT: resume is via `ir_IndirectGoto`, not a simple port chain.** irgen `ir_a_Alt` stores the currently-active arm's resume label in a temp slot `t` (`ir_MoveLabel`) and resumes via `ir_IndirectGoto(t)`. This is NOT equivalent to a simple arm[0].ω→arm[1].α ω-chain for β. The ω-chain is for α (trying arms left-to-right on fresh entry); β re-enters only the currently-active arm via the stored label.

---

### Phase ICN-G — Gate infrastructure (PREREQUISITE for all emitter rungs)

#### ICN-G-1 — Build `test_icon_mode4_rung.sh` ✅ (2026-05-27, Opus 4.7)
- [x] Create `scripts/test_icon_mode4_rung.sh`: for a seed set of rung01 generator programs, runs `scrip --compile --target=x86 file.icn` → `as` (GAS, Intel syntax) → `gcc -no-pie file.o -L out -lscrip_rt -Wl,-rpath,out -lm` → execute, diff stdout against `scrip --interp file.icn` (mode-2 oracle). PASS=N FAIL=M format. emit/assemble/link/run failures are caught and counted FAIL, never fatal — harness always exits 0. **Verified: gate runs clean, reports `PASS=0 FAIL=5`** (mode-4 generators currently emit no output — the documented ω-exhaustion fall-through bug; see below).
- [x] Wire into Session Setup below alongside `test_icon_all_rungs.sh`.
- [x] **Gate threshold: mode-4 PASS ≥ 1 before any emitter rung is marked complete.** A template returning an empty string or stub jumps is NOT done (HQ Invariant 0). (Threshold is documented in the script; not yet met — that is the next emitter rung's job.)

**ICN-G-1 finding — the mode-4 every-loop underflow, now precisely located.** Emitted asm for
`every write(1 to 5)` shows BOTH the generator's `.Licngen0_γ` (success) and `.Licngen0_ω`
(exhausted, last_ok=0, NOTHING pushed) fall through into `.Licngen0_done:` → `CALL_FN write` →
`JUMP_F .L7`. On exhaustion `write` is called on an empty value-stack BEFORE the `JUMP_F` loop-exit
test runs → underflow. Root cause is structural in `lower_every` (lower.c): `lower_expr(gen_expr)`
lowers the WHOLE consuming call `write(1 to 5)`, welding `CALL_FN write` immediately after the
`SM_BB_SWITCH` inside one `lower_expr`; the `SM_JUMP_F` loop-exit is emitted AFTER and tests too
late. Correct fix belongs with ICN-Z-4/ICN-Z-9: the generator's ω port must be a control-flow edge
to loop-exit (a real port wire), not a fall-through into the consumer. Do NOT special-case a
loop-exit label into the switch template — that would seed a second control-flow scheme that drifts
from the zipper. Bring ω-as-port-wire up via the zipper, then this gate climbs from PASS=0.

#### ICN-G-2 — Re-freeze GATE-PK ⏳
- [ ] Run `bash scripts/test_per_kind_diff.sh`. For every FAIL cell: if the template body is an honest stub (returns `std::string()`), the baseline should be empty — re-freeze. If the body claims to emit real x86 but diffs fail, it is a real bug — fix first.
- [ ] Target: GATE-PK FAIL=0. NEW=0 GONE=0.
- [ ] Gate: `test_per_kind_diff.sh` PASS ≥ 504 FAIL=0 before any HQ emitter work resumes.

---

### Phase ICN-Z — Zipper rewire of lower_icn (ONE-PASS signature change)

**⚠ This is NOT additive.** All ~70 call sites in `lower_icn_expr_node` change in ONE pass. Do not attempt partial completion. Gate: `test_icon_all_rungs.sh` ≥198 after each sub-rung. `bb_exec.c` remains the mode-2 oracle.

**Before writing any code for a construct: read its `ir_a_*` procedure in irgen.icn.**
`/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` — the canonical port-wiring source.

#### ICN-Z-0 — Add `icn_leaf` helper + bounded context flag ✅ (2026-05-27, Opus 4.7)
- [x] Added `icn_leaf(nd, γ_in, ω_in, &α_out, &β_out, bounded)` to `lower_icn.c` (exported in
  `lower_icn.h`). Honours bounded rule: `β=(!bounded && icn_kind_is_resumable) ? self : ω_in`.
  γ/ω stamped only when NULL and not an operand slot (mode-2 safe). Twin of `pl_leaf`.
- [x] Added `lower_icn_expr_threaded_b(..., int bounded)` bounded-aware wrapper; the legacy
  `lower_icn_expr_threaded` now delegates with `bounded=0` so the existing call site is unchanged.
- [x] **Exercised (not dead infra):** `lower_icn_proc_body` statement loop now lowers each
  statement via `lower_icn_expr_threaded_b(..., bounded=1)` — irgen `ir_a_Compound` statement
  position is always-bounded (no outer expr can resume a top-level statement). Down payment on
  ICN-Z-2.
- [x] Gate: build clean, smoke_icon 5/5, broker 23, icon_all_rungs 198, smoke_prolog 5/5,
  mode4_rung PASS=2, FACT-RULE grep 0. Non-regressing.

#### ICN-Z-1 — Rewire leaves: BB_LIT_I/F/S, BB_VAR, BB_KEYWORD, BB_FAIL, BB_BREAK, BB_NEXT ✅ (2026-05-27, Opus 4.7)
- [x] Added `icn_tree_is_leaf(e)` classifier (TT_ILIT/FLIT/QLIT/CSET/VAR/KEYWORD/LOOP_BREAK/
  LOOP_NEXT/PROC_FAIL). `lower_icn_expr_threaded_b` now seeds leaf kinds with `bounded=1` forced
  into `icn_leaf`, so a leaf's β=ω_in is guaranteed regardless of the `icn_kind_is_resumable`
  table — the leaf β-contract (irgen: a leaf's resume chunk is just Goto failure) is decoupled from
  that table. Composites keep the caller's bounded flag.
- [x] Leaves: α=self, β=ω_in (no retry). γ/ω stamped via icn_leaf when NULL + not an operand slot.
- [x] Gate: smoke_icon 5/5, broker 23, icon_all_rungs 198, smoke_prolog 5/5, mode4_rung PASS=2,
  FACT-RULE grep 0. Non-regressing. `icn_tree_is_leaf` is live (defined + called).

#### ICN-Z-2 — Rewire BB_COMPOUND / BB_SEQ (Icon statement sequence) ✅ (ICN-Z-2b landed 2026-05-27d, Opus 4.7)
- [x] **Forward chain already correct.** `lower_icn_proc_body` builds the statement chain
  back-to-front with `succ` threading and lowers each statement `bounded=1` (down payment landed
  ICN-Z-0 session). `bb_exec.c` BB_SEQ walks `st = st->γ` (the γ-chain hung off α) — exactly the
  forward, non-backtracking advance irgen ir_a_Compound prescribes; intermediate failure continues
  the loop (advances), not retries.
- [x] DONE (ICN-Z-2b): explicit `stmt[i].ω → stmt[i+1].α` port wire added in `lower_icn_proc_body`
  as a post-build pass (guarded by `icn_kind_owns_omega_operand`, so BB_IF keeps ω as its else-branch
  operand). `bb_exec.c` BB_SEQ re-expressed as a PORT-FOLLOWER: advances via `st->ω` (the explicit
  edge; for ω-operand kinds advances via `st->γ`); last stmt has ω==NULL → proc terminal → FAILDESCR.
  Mirrors irgen ir_a_ProcBody (both success+failure of intermediate → next.α). Behaviour byte-identical
  to baseline (stash diff), additive, mode-2 safe. Operand composites (BINOP/CALL/IF/ALT) untouched —
  those need the full atomic ICN-Z pass.
- [x] Gate: smoke_icon 5/5, smoke_prolog 5/5, rungs 198, broker 23, FACT 0 (all holding).

#### ICN-Z-3 — Rewire BB_CONJ (E1 & E2 — conjunction generator) ⛔ BLOCKED — lockstep finding (2026-05-27, Opus 4.7)
- [ ] irgen `ir_conjunction`: start→E1.start; E1.success→E2.start; E1.failure→p.failure; E2.success→p.success; E2.failure→E1.resume.
- ⛔ **CANNOT be done as an isolated rung — verified this session.** `bb_exec.c` case BB_CONJ
  (bb_exec.c:830) is the mode-2 oracle and reads `nd->α` as E1 and `nd->β` as E2 — BOTH operand
  children. The zipper needs a port for E1's RETRY entry (E2.ω→E1.β), but `BB_t` is FINAL (only
  α/β/γ/ω + payload) and both α and β are already consumed as operand-child reads. There is no free
  slot to carry the zipper wiring without ALSO rewriting `bb_exec.c` BB_CONJ to be a port-follower
  (consume γ/ω instead of recursing into α/β children). That driver rewrite cannot be partial: the
  shared `bb_exec_node` driver recurses into α/β as children for EVERY composite (BB_ASSIGN,
  BB_BINOP, BB_BINOP_GEN, …), so converting one construct to ports while the rest recurse leaves a
  hybrid the single driver cannot walk consistently. This is exactly why the goal file says ICN-Z is
  "ONE pass, ~70 sites, cannot half-zip." **BB_CONJ must be rewired in the same pass as the
  `bb_exec.c` port-follower conversion (Phase H-5 + the whole ICN-Z block), not before.**
- [ ] Gate: smoke_icon 5/5, rungs ≥198 (after the full-pass rewire).

#### ICN-Z-4 — Rewire BB_EVERY ⏳ (mode-4 ω-edge landed 2026-05-27, Opus 4.7)
- [x] **Mode-4 `p.expr.failure → p.ir.failure` wired** for the direct-consumer every case: `lower_every`
  stamps loop-exit PC on SWITCH `a[0].i`; `sm_bb_switch.cpp` ω arm emits `jmp .L<exit_pc>`, skipping
  the consumer. `every write(1 to N)` correct in mode-4 (ICN-G-1 PASS=1). FACT RULE 0.
- [ ] Remaining: filter/cross-product/`to_by` every cases need honest `SM_ACOMP` + binop-generator
  mode-4 templates (separate rung — they run clean but emit no output today). The full irgen edge set
  (`body.γ→expr.β`, `body.ω→expr.β`) is mode-2-correct via BB_PUMP_PROC; mode-4 zipper still pending.
- [ ] **irgen `ir_a_Every` — read it carefully before implementing.**
  - `p.ir.start → expr.ir.start`
  - `expr.ir.success → body.ir.start`
  - `expr.ir.failure → p.ir.failure` (generator exhausted = every fails)
  - `body.ir.success → expr.ir.resume` (body done → pump generator again)
  - `body.ir.failure → expr.ir.resume` (body fail also pumps generator — both paths re-drive)
  - `p.ir.resume → ir_IndirectGoto(continue)` (only in unbounded context — for `break` etc.)
- [ ] **body.ω→expr.β is equally required as body.γ→expr.β.** Both wire to expr.resume.
- [ ] Lower expr unbounded (it is the generator). Lower body always-bounded. Wire the four edges above as BB port connections.
- [ ] Gate: smoke_icon 5/5, rungs ≥198, `every write(1 to 3)` → `1 2 3`.

#### ICN-Z-5 — Rewire BB_IF ⏳
- [ ] **irgen `ir_a_If` has TWO shapes depending on `bounded`:**
  - **Always-bounded (simpler):** `expr.success→then.start; expr.failure→else.start`. then/else each wire `.success→p.success, .failure→p.failure`. No temp label needed.
  - **Unbounded:** ADDITIONALLY stores the active branch's resume in temp label `t` via `ir_MoveLabel`, so `p.ir.resume → ir_IndirectGoto(t)` can re-enter the correct branch.
- [ ] The condition expr is ALWAYS lowered always-bounded (`"always bounded"` in irgen). The then/else branches carry the caller's bounded.
- [ ] `nd->ω` in our current code stores the else-branch operand AND the failure continuation — these must be separate. The else-branch becomes its own BB subgraph; `nd->ω` becomes purely the failure continuation (as per port contract).
- [ ] Gate: smoke_icon 5/5, rungs ≥198.

#### ICN-Z-6 — Rewire BB_ALT (n-ary alternation) ⏳
- [ ] **irgen `ir_a_Alt`:** α = arm[0].start. Arms chained: arm[i].failure → arm[i+1].start; last arm.failure → p.failure. Each arm.success → p.success (with MoveLabel of arm's resume into `t` in unbounded context). Resume: `ir_IndirectGoto(t)` — re-enters only the currently-active arm's resume.
- [ ] This is NOT a simple ω-chain where β tries arm[1] after arm[0] exhausts. β goes to the *same* arm that last succeeded (stored in `t`). **Do not implement as arm[0].ω→arm[1].α for β.** The ω-chain is for α-entry only.
- [ ] In always-bounded context, no `t` needed — each arm.success simply → p.success.
- [ ] Gate: smoke_icon 5/5, rungs ≥198.

#### ICN-Z-7 — Rewire BB_CALL operand chain ⏳
- [ ] **irgen `ir_a_Call`:** L = [fn] ||| args. `L[i].success → L[i+1].start`; `L[i].failure → L[i-1].resume`. `L[1].failure → p.failure`. `L[-1].success → ir_Call(closure, fn, args) → ir_Move → p.success`. `p.ir.resume → ir_ResumeValue(closure, L[-1].resume) → p.success`.
- [ ] The operand chain wires sub-expressions `fn.γ→arg[0].α→arg[1].α...`; failure of any operand re-drives the previous operand. This IS a proper backtracking evaluation. Lower each sub-expression with `bounded=0` (they can be generators).
- [ ] After all operands evaluated, the call node itself: α=fn.α (chain entry). β=self (re-enters via closure resume). **`nd->α` stores the chain entry address; it is NOT the head of a γ-linked operand list as in current code.** The arg nodes are separate BB nodes wired via their own ports.
- [ ] Gate: smoke_icon 5/5, rungs ≥198.

#### ICN-Z-8 — Rewire BB_TO / BB_TO_BY operand evaluation vs internal state ⏳
- [ ] **irgen `ir_a_ToBy`:** fromexpr, toexpr, byexpr are each lowered as sub-graphs. Their results are stored in temp slots `fv, tv, bv`. Chain: `from.success→to.start→by.start`. Then `by.success → ir_opfn("...", [fv,tv,bv]) → ir_Move(target, closure) → p.success`. `p.ir.resume → ir_ResumeValue(target, closure, by.resume) → p.success`.
- [ ] In our BB system: operand sub-graphs evaluated once on α-entry (wired `from.γ→to.α→by.α`); results cached in node fields. **β = self**; β-entry skips the sub-evaluation and directly increments/checks the counter. The current code's α=lo_box, β=hi_box (trying to re-read operands on every β) is wrong.
- [ ] Fix: on α, walk the operand sub-graph to get lo/hi/by values and cache them in `nd->counter` (cur) and `nd->ival` (hi/step). On β, read from those cached fields. `nd->α` in the fixed version points to the operand-chain entry (for walking on α-entry), NOT to lo_box as an always-live child pointer.
- [ ] Gate: smoke_icon 5/5, rungs ≥198, `every write(1 to 3)` and `every write(1 to 9 by 3)` correct.

#### ICN-Z-9 — Delete SM back-edge from `lower_every`; verify every-loop is BB-internal ⏳
- [ ] After ICN-Z-4 lands, `lower_every` in `lower.c` no longer needs `SM_JUMP` (the back-edges are BB port wires inside the graph). Remove the `switch_pc` capture + `SM_label()` + `SM_JUMP` from `lower_every`. The SM carries only `SM_BB_SWITCH` (the generator entry).
- [ ] Verify: `--dump-sm` for `every write(1 to 3)` shows NO `SM_JUMP` targeting the switch PC.
- [ ] Gate: smoke_icon 5/5, rungs ≥198.

---

### Phase ICN-XA — Template purity fix for sm_bb_switch ICN_GEN arm

#### ICN-XA-1 — Route ICN_GEN walk through string-returning walk_bb_node ✅ (2026-05-27c, Opus 4.7)
**⚡ This (specifically the `walk_bb_node_str` half) was the ONE prerequisite for the mode-4
`lt`/`mult`/`compound` gate movers — now landed; gate climbed PASS=2→5.**
- [x] **`walk_bb_node_str_c`** added (emit_core.c/.h): `BB_t* → char*` — `open_memstream` sink swap
  around the existing `walk_bb_node` dispatch, then restore. Caller frees. Zero `emit_text_n` inside;
  same single producer (FACT RULE grep 0).
- [x] `sm_bb_switch_str` ICN_GEN arm rewired to `pre + walk_bb_node_str_c(gen) + post` — the
  LOCAL-PURGE violation (emit_text_n + walk_bb_node mid-body) removed; arm is pure.
- [x] Gate: smoke_icon 5/5, broker 23, rungs 198, smoke_prolog 5/5, mode4_rung PASS=5, FACT RULE 0.
- [ ] (follow-on) The PL_ENTRY arm still has an `emit_text_n` + `walk_bb_flat` mid-body — Prolog scope,
  not Icon; convert when `walk_bb_flat` gets a string variant.

---

### Phase ICN-M4 — Mode-4 emitter rungs (only after ICN-G-1 exists + ICN-Z complete)

**Do NOT begin these until ICN-G-1 gate script exists AND ICN-Z-1..9 are complete.**

#### ICN-M4-1 — `bb_icn_to.cpp` literal generator: honest TEXT + BINARY x86 ⏳
- [ ] LITERAL fast-path TEXT arm exists. Verify via `test_icon_mode4_rung.sh`. If PASS ≥ 1, mark done.
- [ ] BINARY arm: raw x86 (counter in `&pBB->counter`; `cmp; jg ω; rt_push_int; jmp γ; β: add; jmp check`).
- [ ] DYNAMIC operand arm: after ICN-Z-8, α-entry walks operand sub-graph to populate counter/ival; the template reads those cached fields.

#### ICN-M4-2 — `bb_to_by.cpp` literal generator: honest BINARY + dynamic arms ⏳
- [ ] Same pattern as ICN-M4-1. Literal TEXT arm exists; verify via gate. Add BINARY and dynamic.

#### ICN-M4-3 — TEXT arms: rt_push_int@PLT, not raw r12 ⏳
- [ ] TEXT arm (mode-4) must use `mov rdi,<v>; call rt_push_int@PLT`. BINARY arm uses raw r12. Audit both templates.

---

## Session Setup
```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```
Gates:
```bash
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS=23
bash scripts/test_icon_all_rungs.sh        # PASS=198
bash scripts/test_icon_mode4_rung.sh       # ICN-G-1 ✅ exists; currently PASS=0 FAIL=5 (ω-exhaustion bug). PASS≥1 gates emitter rungs.
```

---

## THE FOUR FACTS — READ FIRST

1. **C WALKERS: MODE 2 ONLY.** `icn_bb_dcg` / `bb_exec_once` / `bb_exec_resume` / `bb_exec.c` — permitted in `--interp` only.
2. **NO C WALKERS IN MODE 3/4.** Those symbols stay DEFINED (mode 2 needs them) but UNREACHABLE from `--run`/`--compile`.
3. **SM + BB DO NOT EXIST AT RUNTIME IN MODE 3/4.** Emitter reads them once, bakes flat-wired x86. `scrip.c` frees SM+BB before the runner executes.
4. **ONE x86 PRODUCER.** `src/emitter/ + BB_templates/*.cpp / SM_templates/ / XA_templates/` only. A second producer ALWAYS drifts.
5. **TEMPLATE-ONLY EMISSION (FACT RULE).** Every byte of emitted x86 lives in a template function keyed to a BB/SM/XA opcode, reached only via `emit_core.c` dispatch. `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/` outside `*_templates/` + `emit_core.c` == 0.

**Completion test:** from any `--run`/`--compile` entry, reachability to `icn_bb_dcg`/`pl_bb_dcg`/`bb_exec_once`/`bb_exec_resume` == ZERO.

**Other rules:** NO AST WALKING modes 2/3/4. ZERO C Byrd-box functions (`DESCR_t foo(void*,int entry)`); only exempt: `icn_bb_dcg`, `icn_bb_oneshot`. NO new C functions in `icon_box_rt.c`/`rt.c` to back a template — logic lives inline in `bb_*.cpp`. CONSULT `irgen.icn` before any BB kind (`/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`).

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --interp   → execute_program() → interp_eval()        Mode 2 (SM+BB C walker, reference)
  --run      → lower() → sm_codegen_x64() → exec        Mode 3 (in-proc, PROT_EXEC)
  --compile  → lower() → sm_codegen_x64() → binary      Mode 4 (separate process)
```

`tree_t` → `lower()` → SM bootstrap + `BB_graph_t`. **BB_t IS the IR** (≡ JCON `ir_*`). NOT a tree.

**GOLDEN BB RULE:** BB_t has ONLY: `t` (kind), `α β γ ω` (port ptrs), `sval`/`ival`/`dval` (IR payload), `value`/`counter`/`state` (interp runtime). No `c[]`/`n`/`lhs`/`rhs`/`opaque`/`sval2`/`ival2`/`ival3`. **BB_t struct is FINAL.**

**Four ports (AG over lowering):**
| Port | Direction | Meaning |
|------|-----------|---------|
| γ | DOWN (inherited) | success continuation |
| ω | DOWN (inherited) | failure continuation |
| α | UP (synthesized) | fresh-entry address |
| β | UP (synthesized) | retry-entry address |

Signature: `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`. JCON `{start,resume,success,failure}` → `α/β/γ/ω`.

---

## Done when
1. Every AST kind reachable from a `--interp` PASS Icon program lowers via `lower.c` to pure SM/BB.
2. Every SM opcode Icon emits has a `sm_codegen_x64` mirror.
3. `is_suspendable` / `coro_eval` not reachable from SM dispatch.
4. Mode 3 and mode 4 execute the IDENTICAL emitter-produced flat-wired x86, differing only in process boundary.

---

## Phase H — Attribute Grammar (pointers, no label IR)

#### H-1 — 4-attribute lowerer ✅ SUBSTANTIALLY COMPLETE
- [x] Threaded signature + back-to-front spine; leaves compose; top γ/ω seeded NULL=trampoline-halt.
- [x] BB_IF else→ω. BB_CONJ (`E1 & E2`) own opcode.
- [x] Cross-arg odometer: multi-generator CALL args cross-product (rungs 196→198). Side-effect fix: single-shot args cached, not re-evaluated.
- [ ] **REMAINING:** DOWN-threading of γ/ω into then/else/body for nested non-leaf IF. Blocked: `if` not accepted in expression position by parser (GOAL-PARSER-ICON prereq). Generator-composition corners verified clean.

#### H-2 — BB_SEQ child-array → γ-chain ⏳
- [ ] `lower_icn_proc_body` seq build → γ/ω-chain; `bb_exec.c` BB_SEQ walk via ports. Gate smoke 5/5.

#### H-3 — 2-operand kinds via α/β + thread γ/ω ⏳
- [x] BB_TO_BY proof: JCON `ir_a_ToBy` transliterated; `2 to 7 by 2`→2 4 6.
- [ ] Each binary kind: lower lhs (γ=rhs.α…), lower rhs, wire α/β; executor reads `nd->α->value`/`nd->β->value`.

#### H-4 — N-ary kinds via γ-chain ✅
- [x] CALL args γ-chain + MAKELIST (`82ec79f8`).
- [x] IDX_SET/SECTION 3-operand (`45c1bde2`).

#### H-5 — sweep `c[]/n` in bb_exec.c ⏳
- [ ] `grep -nE 'nd->c\[|nd->n\b|e->c\[|e->n\b|gen->c\[' src/lower/bb_exec.c` empty.

---

## Phase J — Mode 3 executes shared emitter's flat-wired x86

**Root cause of RED:** `scrip.c` mode_run frees `bb_table` + SM before the runner executes; the old baked `rt_bb_pump_proc` read freed `bb_table[]` → NULL → crash. Fix: mode 3 EMITs via the shared template producer, not a C walker.

#### J-2 — memstream sink ✅ (`106b7c51`)
`open_memstream` FILE* sink for `codegen_sm_x86`. `--memcheck` proves memstream==file bytes 3/3.

#### J-3 — `call rel32` to proc SM entry_pc ✅ (`de0f2352`)

#### J-4 — route SM_BB_PUMP_PROC through J-2/J-3 ⏳
- [x] `hello` prints; `double(21)`=42; SM_ACOMP/LCOMP wired; SM_LOAD/STORE_FRAME via rt helpers.
- [ ] **NEXT (J-4a): GENERATORS.** `every`/`to`/`by` abort flag-on. Root cause: `bb_icn_to_by.cpp` / `bb_icn_to.cpp` PLATFORM_X86 arms now hollow (deleted with `rt_bb_*`). Fix = implement four-port literal generator x86 in those templates. Probe: `every write(1 to 3)` → `1 2 3` flag-on.

#### J-5 — migrate PUMP_SM, PUMP_CASE, BB_SWITCH, generator path ⏳
#### J-6 — flip default to flat BB; delete C bridge ⏳

**Phase J done when:** mode 3 ≡ mode 4 flat-wired x86; `icn_bb_dcg`/`bb_exec.c` unreachable from `--run`; smoke 5/5, broker ≥23, rungs ≥198, ASAN clean.

---

## Invariants
1. `--ir-emit` byte-identical at every rung.
2. No `EXPR_t*` in SM bytecode.
3. `is_suspendable` stays in sync with lowering rungs.

---

## Closed rungs
| Rung | Commit | Gain |
|------|--------|------|
| H-1 threading + IDX_SET/SECTION | `45c1bde2` | 189→195 |
| BB_CONJ (E1 & E2) | `9be28a5d` | 195→196 |
| H-1 cross-arg odometer | `fcfc7a73` | 196→197 |
| H-1 odometer side-effect fix | `fcfc7a73` | 197→198 |
| JA-D (engines + JIT deleted) | `e842b724` | — |
| rt_bb_* total deletion | `0206b998` | — |

---

## File ownership (`0206b998`)
`src/lower/lower_icn.c` · `src/lower/bb_exec.c` · `src/lower/scrip_ir.c` · `src/emitter/{emit_bb.c,emit_sm.c,emit_core.c}` · `src/emitter/BB_templates/bb_*.cpp` · `src/processor/sm_codegen.c` · `src/processor/sm_interp.c` · `baselines/icon-bb/`

---

## ⚡ HOW AG-LOWERING + EMITTER TEMPLATES ACTUALLY WORK (Sonnet, 2026-05-26 — learned by reading code)

Hard-won mental model. Read this before touching generators; it cost a full session to assemble.

### The two-stage pipeline, concretely

```
Icon AST → LOWER (builds SM bootstrap + BB graph) → EMITTER walks BB at emit time → x86 via templates
```

There are TWO lowerers and they are NOT the same file:
- `lower.c` — the SM-spine lowerer. Emits the flat `SM_sequence_t` (PUSH/CALL/JUMP/BB_SWITCH...).
  This is the "bootstrap" / statement scaffold. `lower_to`, `lower_to_by`, `lower_every` live here.
- `lower_icn.c` — the BB-graph builder. `lower_icn_expr_top(tree)` returns a `BB_graph_t*` whose
  `->entry` is a four-port-wired `BB_t` tree. THIS is the IR the emitter walks. `BB_t IS the IR`.

The bridge between them: `SM_seq_bb_add(g_p, cfg)` registers a `BB_graph_t*` into
`g_stage2.sm.bb_table[]` and returns an `int bb_idx`. The SM carries that idx in an
`SM_BB_SWITCH` instruction. This is the SAME mechanism SNOBOL4 patterns use (`SM_EXEC_STMT`
carries a bb_idx) and Prolog uses (`SM_BB_SWITCH` + `SM_BBSW_PL_ENTRY`). One pattern, three langs.

### Attribute Grammar = the four ports, threaded by lower_icn.c

γ/ω are INHERITED (passed DOWN into children): success-continuation, fail-continuation.
α/β are SYNTHESIZED (returned UP from children): fresh-entry addr, retry-entry addr.
Signature shape: `lower(cfg, tree, γ_in, ω_in, &α_out, &β_out)`. Leaf: `α=β=self; γ=γ_in; ω=ω_in`.
Composition wires child.γ → next sibling, last.γ → parent.γ, etc. (see `lower_icn.c` arg-γ-chain
at the `BB_CALL` case: `args[j-1]->γ = args[j]`). The mode-2 reference walker `bb_exec.c`
(was `ir_exec.c`) executes this graph by following ports — it is the SEMANTIC SOURCE OF TRUTH for
every BB kind. To implement any construct: read its `case BB_X:` in bb_exec.c, translate to x86.

**ALL FOUR PORTS MUST BE WIRED — flat-wired, no NULL, no trampoline (corrected 2026-05-26, Opus
4.7, after Lon).** The canonical model is JCON `irgen.icn` `record ir_info(start, resume, failure,
success)` ≡ our `α/β/γ/ω`. In irgen EVERY chunk wires EVERY port to a concrete target via
`ir_Goto(coord, <other-port>)` — there is NO NULL exit and NO fall-through to any "trampoline/halt".
Even a LEAF wires all ports: `ir_a_Intlit` does `start: [IntLit; Goto(success)]` and (bounded)
`resume: [Goto(failure)]`. A generator like `ir_a_ToBy` wires eight chunks — `start→fromexpr.start`,
`resume→[ResumeValue; Goto success]`, `fromexpr.success→toexpr.start`,
`fromexpr.failure→ir.failure`, `toexpr.success→byexpr.start`, `toexpr.failure→fromexpr.resume`,
`byexpr.success→[opfn; Move; Goto success]`, `byexpr.failure→toexpr.resume`. Every port lands on a
port; the top-level seeds the terminal success/failure with real halt chunks.

⛔ **OUR CURRENT lower_icn.c DIVERGES — this is the real defect to fix.** Two problems:
(1) **Leaves leave ports NULL.** `BB_node_alloc` NULLs α/β/γ/ω and leaf cases (TT_ILIT/TT_VAR/…)
set only the payload (ival/sval), never wiring start→success / resume→failure as irgen requires.
(2) **α/β are OVERLOADED as operand-child pointers, not control-flow ports.** e.g. TT_TO_BY does
`nd->α = lo; nd->β = hi;` (the lo/hi OPERAND boxes), and the BB_CALL case chains args as
`e->α … a = a->γ` (γ = "next operand sibling"). So `bb_exec.c` walks α/β/γ as an OPERAND TREE in C —
that is AST-walking-in-disguise and is exactly what flat-wiring must eliminate. It "works" in mode 2
ONLY because the C executor patches the holes at runtime (the `? : NULL` guards I earlier mis-read
as "design"). Flat-wired x86 (mode 3/4) has nowhere to fall back to: an unwired port = jump-to-
garbage; an operand-in-port = no control-flow successor at all. **NEXT (mode 2→3): rewire lower_icn.c
so α/β/γ/ω are PURE control-flow links per irgen — operands become separate boxes whose `success`
(γ) flows into the next box's `start` (α) — and verify against `bb_exec.c` re-expressed as a flat
port-follower (no tree recursion). Read each `ir_a_*` in irgen.icn for the exact per-port wiring.**

#### Canonical per-port wiring (extracted from irgen.icn — α=start β=resume γ=success ω=failure)

Terminal seeding (`ir_a_ProcBody`/`ir_a_ProcCode`): the proc's last stmt `γ → proc.γ` and
`ω → proc.ω`; proc.γ/proc.ω are real terminal chunks (`ir_Fail`/halt). The buck stops at concrete
top-level chunks — NEVER a NULL or an implicit trampoline.

- **Intlit/Reallit/Stringlit/Csetlit (leaf):** `α: [emit lit; Goto γ]`; (bounded) `β: [Goto ω]`.
- **Ident/Var (leaf):** same shape — `α` does the load then `Goto γ`; `β → ω`.
- **ToBy:** `α→from.α`; `β: [ResumeValue; Goto γ]`; `from.γ→to.α`; `from.ω→ω`; `to.γ→by.α`;
  `to.ω→from.β`; `by.γ: [opfn "..."; Move target; Goto γ]`; `by.ω→to.β`.
- **Every:** `α→expr.α`; `expr.γ→body.α`; `expr.ω→ω`; `body.γ→expr.β`; `body.ω→expr.β`.
  (`body.γ→expr.β` IS the loop back-edge — a PORT WIRE, not an SM_JUMP. The whole loop is BB-graph
  internal; no SM scaffold needed once lower_icn wires it.)
- **If:** `α→cond.α`; `cond.γ→then.α`; `cond.ω→else.α` (or `→ω` if no else); `then.γ→γ`;
  `then.ω→ω`; `else.γ→γ`; `else.ω→ω`. (Read ir_a_If:577 for the exact bounded/rval variant.)
- **Compound (seq):** chain `stmt[i].γ→stmt[i+1].α`; last `.γ→γ`; failures per ir_a_Compound:1231.
- **Alt (`E1|E2`):** `α→e1.α`; `e1.γ→γ`; `e1.ω→e2.α`; `e2.γ→γ`; `e2.ω→ω`; resume re-enters the
  currently-active arm (ir_a_Alt:167).
- **Field/Binop/Unop/Call:** operand boxes are SEPARATE nodes wired `operand.γ→next.α`; the op's own
  `α` is the first operand's `α`, the result is produced in the last operand's `γ` chunk which then
  `Goto γ`. Operands are NOT stored in α/β as child pointers (our current bug).

REWIRE ORDER (mode 2 must stay green each step — bb_exec.c is the oracle): (1) leaves
(Intlit/Var/Stringlit/Cset) wire α→γ, β→ω; (2) ProcBody/ProcCode terminal seeding; (3) Compound
seq γ-chain; (4) If/Alt; (5) ToBy/Every/Upto generators (back-edge = body.γ→expr.β port wire);
(6) Call/Binop operand-box chains (retire α/β-as-operand-child). After each: smoke_icon 5/5,
rungs ≥198. bb_exec.c must be re-expressed as a pure port-follower (no `a = a->γ` operand-tree
recursion) once ports are control-flow only.

#### THE ZIPPER — copy Prolog's lower_pl.c exactly (Lon, 2026-05-26). lower_pl ALREADY does this.

Two inherited attrs go DOWN (γ_in, ω_in = where to go on success/fail); two synthesized attrs come
UP (α_out, β_out = my fresh-entry, my retry-entry). Signature (mirror EXACTLY):
`lower_icn_expr_node(cfg, e, BB_t *γ_in, BB_t *ω_in, BB_t **α_out, BB_t **β_out)`.

LEAF SEEDER (twin of `pl_leaf`, lower_pl.c:21 — add `icn_leaf`):
```c
static BB_t *icn_leaf(BB_t *nd, BB_t *γ_in, BB_t *ω_in, BB_t **α_out, BB_t **β_out){
    if(!nd) return NULL;
    nd->γ=γ_in; nd->ω=ω_in;            /* inherited DOWN */
    if(α_out)*α_out=nd;                /* leaf is its own fresh-entry, synth UP */
    if(β_out)*β_out=ω_in;              /* leaf has no retry: β=ω → ω-chain skips through it */
    return nd; }
```
Every leaf case becomes: `return icn_leaf(nd, γ_in, ω_in, α_out, β_out);` (see lower_pl.c:62-63).

CONJUNCTION/SEQ = back-to-front zipper (lower_pl_goal conjunction, lower_pl.c:160-203):
build goal[n-1] first with γ=γ_in; then i=n-2..0 with `my_γ = gα[i+1]` (success→next entry);
wire `goal[i].ω = gβ[i-1]` (fail→redo nearest LEFT generator). β-by-kind:
resumable (generators: TO/TO_BY/UPTO/ALT/EVERY/PROC_GEN…) → β=self; non-resumable → β=left neighbor's β.

DISJUNCTION/ALT (lower_pl.c:206-217): lower 2nd branch first (γ_in,ω_in)→bα; lower 1st with
`ω=bα` (1st fails→try 2nd)→aα; node α=aα β=bα γ=γ_in ω=ω_in.

This is NOT additive — it is a signature change touching ~70 call sites in lower_icn_expr_node, done
in ONE pass top-to-bottom (you cannot half-zip). After: α/β/γ/ω are PURE control flow; retire the
α/β-as-operand reads in bb_exec.c (operands become boxes wired operand.γ→next.α). Gate each language
construct group: smoke_icon 5/5, rungs ≥198. EVERY already pre-wired (gen.γ→body, body.γ→gen,
gen.ω→every) for literal generators — fold into the zipper when EVERY's turn comes.

### EMITTER templates — the THREE things that are easy to get wrong

1. **emit_core.c is DISPATCH-ONLY.** Template bodies live in `BB_templates/bb_*.cpp`,
   `SM_templates/sm_*.cpp`, `XA_templates/xa_*.cpp`. emit_core just does `case BB_X: bb_x(nd);`.
   A template emitting empty string / stub jumps is NOTHING (Invariant 0). Real GAS in MEDIUM_TEXT
   AND real bytes in MEDIUM_BINARY, or it is not done.

2. **There are TWO value-stack conventions and they DIFFER BY MEDIUM. This is the #1 trap.**
   - MEDIUM_TEXT (mode-4 `--compile`): values go through the rt ABI — `mov rdi,<v>; call rt_push_int@PLT`.
     This is what `bb_upto.cpp` TEXT does and what WORKS in the SM mode-4 ABI.
   - MEDIUM_BINARY (mode-3 flat/brokered): raw `r12` value-stack — `mov [r12+8],rax; add r12,16`.
   `bb_icn_to.cpp` originally used raw-r12 in its TEXT arm (brokered convention) → SEGFAULT in
   mode-4 because r12 is not set up as a vstack there. FIX was `rt_push_int@PLT`. When you write a
   TEXT arm, push via rt helpers; r12 is for BINARY only. (Invariants 8/9: BINARY must embed no
   emitter-process pointers and no four-port rt_* helper; TEXT may `call util@PLT` for non-port utils.)

3. **last_ok is a FUNCTION, not a data symbol.** `nm` shows `T rt_last_ok` (getter) and
   `T rt_set_last_ok` (setter). Writing `mov [rip+rt_last_ok],1` corrupts code. Use
   `mov rdi,<0|1>; call rt_set_last_ok@PLT`.

### How to make a registered generator graph emit inline (the SM_BB_SWITCH ICN_GEN pattern)

The SM_BB_SWITCH template, for an Icon generator, fetches `g_stage2.sm.bb_table[idx]->entry`,
sets `g_emit.lbl_α/β/γ/ω` (+ `_p` pointers) to fresh labels, then calls `walk_bb_node(gen, out)`.
walk_bb_node dispatches to the box's `bb_*` template, which emits its α-body at lbl_α and jumps to
lbl_γ/ω/β. The SM template then defines those labels: γ → set last_ok=1 + continue; ω → set
last_ok=0 + continue. This emits the box's four-port x86 INLINE at emit time — NO runtime BB walk,
NO C Byrd box (the PD-8 trap). MUST set lbl_α too or the box emits `(null):` → assembler error.

### The every-loop back-edge gotcha (the open J-4a bug)

`lower_every` (lower.c) captures `switch_pc = SM_label-1` AFTER `lower_expr(gen_expr)`. For
`every write(1 to 3)`, gen_expr is the WHOLE call, so lower_expr emits SM_BB_SWITCH (inner `to`)
THEN SM_CALL_FN write — `switch_pc` wrongly points at the CALL. The loop back-edge must re-enter
the GENERATOR's switch PC, not the consuming CALL. Fix: locate the SM_BB_SWITCH PC emitted within
gen_expr (or lower the bare generator separately from its consumer body). mode-2 is immune because
SM_BB_PUMP_PROC drives the whole proc via the C graph walk, ignoring the SM loop scaffold.

### Gate reality

- `test_icon_all_rungs.sh` is `--interp` (mode-2) ONLY — pinned ~198 regardless of emitter work.
  It CANNOT measure mode-4 generator progress. Build a mode-4 Icon rung gate (mirror Prolog GATE-3:
  per-rung emit→assemble→link→run, assert == mode-2 output) to make EMITTER rungs honestly count.
- GATE-PK (per-kind) is the emitter-output gate but has been stale-RED since `a5775d1a` (baseline
  not re-frozen across ~9 emitter commits). Owner decision needed: verify cells then re-freeze.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
