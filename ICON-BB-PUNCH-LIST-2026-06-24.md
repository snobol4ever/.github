# ICON-BB PUNCH LIST — JCON→BB wholesale conversion analysis (2026-06-24, Claude)

Scope: catalogue every Icon IR/BB, scan lowerer + template coverage, and decide whether a
wholesale JCON→BB conversion is the right lever for the remaining rungs. Built from
`refs/jcon-master/tran/irgen.icn` (canonical), `src/lower/lower_icon.c`, `src/driver/scrip.c`
(the native-eligibility GATE), and the full `bb_*.cpp` template tree.

---

## 0. HEADLINE FINDING — THE WALL IS THE GATE, NOT THE LOWERER OR THE TEMPLATES

The remaining work is **NOT** missing Byrd Boxes for the most part. It is the
**native-eligibility gate** `graph_native_emittable_mode()` (`scrip.c:266`) that hard-rejects
whole programs the lowerer + templates could already handle.

Proof (`rung24_records_basic`, EXCISED):
```
record point(x, y)
procedure main()  p := point(3, 4);  write(p.x);  write(p.y);  end
```
- LOWERS cleanly: `IR_CALL(point) → IR_ASSIGN(p) → IR_FIELD_GET(x) → IR_CALL(write) → …`,
  every node with proper γ/ω edges. No `[NO-IR]`, no malformed graph.
- Templates EXIST: `bb_call.cpp`, `bb_field_get.cpp`, `bb_assign_local.cpp`, `bb_var.cpp` are all real.
- Yet `--run` prints `[SMX] … EXCISED`. The gate rejects it at `scrip.c` because the
  `IR_ASSIGN(p) := IR_CALL(point)` RHS shape (`point()` = record constructor, a `dval==2.0`
  call not in `rt_builtin_is_known`) trips `graph_native_emittable_mode`'s
  "unknown dval==2.0 call ⇒ return 0" and/or the `local_assign_rhs_ok_g` whitelist.

**89 EXCISED + 5 FAIL = 94 non-green rungs. The dominant blocker is the gate's conservative
whitelists, not absent codegen.** A wholesale BB conversion adds boxes; but if the gate still
rejects the graph, the new boxes never run. So the conversion must be paired with **gate
widening** to pay off.

---

## 1. THE IR/BB VOCABULARY ICON ACTUALLY USES

### 1a. JCON's REAL primitive set (the BB targets)
JCON lowers all 43 `ir_a_*` syntax procedures down to a **tiny** instruction vocabulary emitted
into chunks. Frequency from `irgen.icn`:

| instr | uses | meaning | SCRIP equivalent |
|-------|------|---------|------------------|
| `ir_Goto` | 193 | unconditional edge | the γ/ω port edge itself (no box) |
| `ir_Key` | 20 | keyword value (&pos,&subject,&null…) | `IR_KEYWORD`/`bb_keyword` |
| `ir_Assign` | 16 | store to lvalue | `IR_ASSIGN`/`bb_assign_*` |
| `ir_MoveLabel` | 9 | save resume addr into tmp | folded into `bb_alt` counter |
| `ir_IndirectGoto` | 9 | jump to saved addr | folded into `bb_alt`/`bb_every` β |
| `ir_Fail` | 9 | → failure port | the ω edge / `IR_FAIL` |
| `ir_ScanSwap` | 5 | swap subject/pos (scan) | `bb_scan_*` Σ/δ save-restore |
| `ir_ResumeValue` | 5 | resume a suspended closure | **GAP** (coexpr/gen resume) |
| `ir_Move` | 5 | copy value tmp→tmp | slot-to-slot mov |
| `ir_Succeed` | 4 | YIELD value + resume addr | `IR_SUSPEND`/`bb_suspend` (pieces 2,5 left) |
| `ir_Deref` | 3 | dereference variable | implicit in slot read |
| `ir_OpFunction`/`ir_opfn` | (operators) | apply N-ary operator | `IR_BINOP`/`IR_UNOP`/`bb_binop_*` |
| `ir_Call` | 1 | invoke closure | `IR_CALL`/`bb_call*` |
| literals (`ir_IntLit`/`StrLit`/`RealLit`/`CsetLit`) | — | constants | `IR_LIT_*`/`bb_lit*` |

**KEY ARCHITECTURAL FACT:** SCRIP keeps these as **macro-nodes** (`IR_EVERY`, `IR_ALT`,
`IR_SUSPEND`, `IR_WHILE`…) with γ (success-successor) and ω (fail-successor) edges, whereas
JCON flattens to `ir_Goto` chains. They are **semantically isomorphic** — a SCRIP γ/ω edge IS a
JCON `ir_Goto`, a SCRIP macro-node's internal wiring IS the JCON chunk's `ir_Goto` fan-out.
The `flat_drive_*` functions in `emit_bb.c` perform exactly the chunk-wiring JCON's
`suspend ir_chunk(...)` statements describe. **This is why wholesale conversion is viable:** the
port topology is already a line-by-line correspondence.

### 1b. Icon's IR enum footprint (50 of 222 IR kinds)
Icon lowerer references: `IR_ALT IR_ASSIGN IR_BINOP IR_BREAK IR_CALL IR_CASE IR_CASE_ARM IR_CONJ
IR_EVERY IR_EXEC IR_FAIL IR_FIELD_GET IR_GEN_SCAN IR_IDX_SET IR_IF IR_INITIAL IR_KEYWORD
IR_LCONCAT IR_LIMIT IR_LIST_BANG IR_LIT* IR_NEXT IR_NOT IR_RASGN IR_REPEAT IR_RETURN IR_SCAN_*
IR_SECTION IR_SUCCEED IR_SUSPEND IR_SWAP IR_TO IR_TO_BY IR_UNOP IR_UNTIL IR_VAR IR_WHILE`.

Control-flow IR (`IR_IF/WHILE/UNTIL/REPEAT/BREAK/NEXT/CONJ/CASE`) is **not** in `emit_core.c`
dispatch — it routes through the **flat-chain walker** in `emit_bb.c` (`walk_bb_flat`), which is
the SCRIP analogue of JCON's chunk emitter. That path is healthy.

---

## 2. TEMPLATE HEALTH — 138 bb_*.cpp scanned, essentially ALL real

Classification of every `bb_*.cpp`:
- **BOMB-ONLY (no real emission):** 0 (zero) — there is no purely-empty template.
- **Correctly-minimal (pure pair-loop port wiring, the JCON `ir_Goto`-only shape):**
  `bb_conj`, `bb_match_alt`, `bb_match_cat`, `bb_ite`, `bb_every` — these are RIGHT (a bare
  `jmp ω / def β / jmp ω`, mirroring JCON `ir_a_Every` emitting only `ir_Goto` chunks).
- **Real with a bomb FALLBACK arm (unhandled-shape guard, correct discipline):** ~30 files carry
  ONE `x86_bomb(...)` for the not-yet-covered operand shape and real `x86()` for the covered one
  (`bb_to`, `bb_limit`, `bb_suspend`, `bb_scan_*`, `bb_idx_set`, `bb_section`, `bb_keyword`…).
  These are healthy mid-design boxes.
- **Big routers:** `bb_call.cpp` (632 L, 13 bombs, 141 real x86) is the call-route multiplexer —
  large but legitimate (de-crammed per DUP FORM 4 into route sub-shapes).

**Conclusion: the template tree is NOT the bottleneck.** No wholesale template rewrite is needed.
The few genuinely-absent boxes are: coexpression/`create` (`ir_ResumeValue`), and the
`initial`/`static` persistent-static store (which needs the `.bss` arena, a separate prereq).

---

## 3. THE GATE WHITELISTS — THIS IS THE ACTUAL PUNCH LIST

`graph_native_emittable_mode()` hard-rejects (`return 0`) on these, blocking otherwise-emittable
graphs. Each line below is a discrete, testable widening:

### TIER A — pure gate widenings (lowerer + templates already present; just admit the shape)
| # | Gate reject (scrip.c) | Blocks rungs | Fix |
|---|----------------------|--------------|-----|
| A1 | `IR_CALL dval==2.0 && !rt_builtin_is_known` ⇒ 0 | **records (rung24 ×5, rung23 tables, rung13 tables)** — record constructors `point()` look like unknown calls | register record-constructor names + table builtins (`table`,`member`,`insert`,`delete`,`key`) in the known set OR carve a `dval==2.0 && is_record_ctor` accept arm |
| A2 | `local_assign_rhs_ok_g` whitelist (`rhs_kind_ok`) | **records, list-RHS, call-RHS** — `p := point(...)`, `x := get(...)` | extend `rhs_kind_ok` to accept `IR_CALL dval==2.0` (builtin/ctor as RHS) once A1 lands |
| A3 | `has_alt` whole-graph taint (`alt_safe_kind` over ALL nodes) | **rung13 alt ×3, queens** — any alt-containing graph with IR_BINOP/IR_CONJ/IR_VAR | arm-scope the taint (only the alt's arms must be alt_safe, not the whole graph) — REQUIRES alt-value-in-binop emitter first (verified blanket regresses 3 rungs) |
| A4 | `alt_arms_all_simple_lit` (≤ literal arms) | **rung13 cross-arg, queens** | admit IR_VAR / IR_CALL arms; the `bb_alt` counter already supports N arms |

### TIER B — small codegen + gate (a box arm + admit)
| # | Construct | Blocks | Work |
|---|-----------|--------|------|
| B1 | `suspend` resume-spine | rung03 ×3 | DESIGN-ICON-SUSPEND pieces 2 (prologue entry-dispatch in `xa_flat.cpp`) + 5 (caller gen-call box), then drop the `IR_SUSPEND ⇒ 0` gate line |
| B2 | scan double-emission | rung06 ×2, every+scan cluster | fix `flat_emit_arg_subchain` to dedup vs `flat_chain_set_has` (precise loc known), then drop `gen_scan_body_slotful` reject |
| B3 | `find` as resumable generator | rung08 (rc=124 hang) | the find generator's β doesn't advance — wire resume like `bb_to` |
| B4 | cross-arg alternation value flow | rung13 ×2 (the 2 hard FAILs) | alt arm value must reach the consuming call's operand slot across args |

### TIER C — needs a new facility (larger, separate prereq)
| # | Construct | Blocks | Facility |
|---|-----------|--------|----------|
| C1 | `initial` / `static` | rung21 ×2, rung25 ×3, queens/deal/post/tgrlink/ipxref | persistent-writable-static `.bss` arena (the GVA `__gva` array extended — see ICON-AUDIT §D); m3 RX slab is RO so needs the `.bss`/heap-arena from GOAL-ICN-GVA-M3 |
| C2 | tables (`T[k]`, default, member, delete, iterate) | rung13/rung23 table ×9 | table datatype + `IDX_GET/IDX_SET` on tables (lists work; tables don't) |
| C3 | records (datatype, not just gate) | rung24 ×5 | record alloc/field already partly built (`bb_field_get`); needs ctor + `FIELD_SET` |
| C4 | coexpressions / `create` | micro.icn, args | `ir_Create`/`ir_ResumeValue` — big; coroutine stack |
| C5 | `sort` / list value-gen at top level | rung15, sort ×3, shuffle/deal/post | `every put(a, expr)` accumulate + `sort()` builtin |

---

## 4. THE WHOLESALE-CONVERSION VERDICT

**Is a wholesale JCON→BB conversion the right starting move?** Partially.

**What it WOULD fix:** the handful of constructs with no SCRIP box at all (coexpr/create →
`ir_ResumeValue`; RepAlt; Mutual). And it would give a clean, canonical re-derivation of the
port wiring for `suspend`/`alt`/`limit`/`scan` if any are subtly wrong vs canonical.

**What it would NOT fix (the 80% case):** records, tables, sort, initial/static, cross-arg alt —
these are blocked by (a) the **gate whitelists** and (b) **missing datatypes/facilities**, NOT by
missing port wiring. JCON's `ir_a_Record`/`ir_a_Call` already have SCRIP equivalents that LOWER
correctly; the block is downstream.

**RECOMMENDED STRATEGY (revised from "wholesale dump"):**
1. **Gate-first, construct-by-construct.** For each EXCISED family, instrument the gate, find the
   exact reject, and either widen it (Tier A — free wins) or build the one missing box arm
   (Tier B). This is higher-yield per hour than a blind conversion because the lowering+templates
   are mostly already present.
2. **Convert from JCON ONLY where SCRIP has a genuine gap** (Tier C4 coexpr, RepAlt, Mutual) — there
   the canonical chunk wiring is the right source of truth and a direct transcription is warranted.
3. **Generate the untested code in BATCHES per Tier, test through the full rung suite after each.**
   The suite's `[SMX]→EXCISED` mechanism means a half-built arm fails LOUD, never silently — so
   batched untested code is safe to land behind the gate.

**FIRST CONCRETE TARGET (this session candidate): TIER A1+A2 — records & constructor-RHS.**
Smallest blast radius, unblocks rung24 ×5 immediately (5 rungs, biggest single-family win after
suspend), pure gate widening + record-ctor registration, no new datatype if record alloc already
works. If record *alloc* is missing, it escalates to C3 — verify first.

---

## 5. APPENDIX — full per-rung EXCISE/FAIL inventory (HEAD a872f56, suite 153/283)

FAIL (5): rung08_strbuiltins_find_gen (rc124), rung13_alt_alt_cross_arg,
rung13_alt_alt_cross_arg_sideeffect, + (suspend ×3 are EXCISED not FAIL now), rung30/rung37 cluster.

EXCISED families (89 total): jcon-bench ×34, tables ×~13, records ×5, alt ×3, suspend ×3,
sort ×3, section/seqexpr ×4, global/initial ×5, read ×4, plus singletons (neg, mutual, keywords,
scan, real_swap, etc.).

Construct → blocker map is §3 above.
