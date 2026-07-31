# FINDING 2026-07-30 — SN4 ZRUN: THE STATIC-ARM ERROR IS A PER-READER SELF-DOUBLE-ADD, NOT A PER-SPINE PREFIX

**Session:** s21x-t · **Tree:** SCRIP `1c0124f1` (unchanged — everything below was measured and REVERTED)
**Rung:** GOAL-SNOBOL4-BB → the s21x-s cursor's STEP 1 ("emit-time ζ-depth running sum")
**Watermark re-derived at start, clean clone:** m3 **229/88** · m4 **227/88/2** · DIV=1 {W04_arbno_basic} — matches the s21x-s cursor to the digit.

---

## HEADLINE

**The s21x-s plan of record — "STEP 1 = emit-time ζ-depth RUNNING SUM" — is FALSIFIED. The error it was written to repair is not a spine property at all.** It is a **per-reader double-add of the reader's OWN carve**, and a running sum repairs it only by coincidence on nodes where the upstream prefix happens to equal the reader's own K.

Corollary, equally measured: the obvious repair (**delete `op_zdepth` from the static arm**) is ALSO wrong — globally it costs 36 programs. The rule is **conditional per node**, and the condition is which of the two disjoint carve authorities granted that node.

---

## THE ENABLING FACT (measured from source, not assumed)

`fc_leaf_walk` (lower_snobol4.c:1066-1068) accumulates **only** `fc_geom`-granted cells:
```c
long own = 0; { long fck; if (fc_geom(x, &fck)) own = fck; }
fc_leaf_register(x, pfx + (int)own);
pfx += (int)own;
```
and `zw_carve_k` (zeta_storage.c:1078) returns 0 **whenever `fc_geom` grants**:
```c
if (fc_geom(nd, &_d)) return 0;
```

**The two carve sets are therefore DISJOINT, by construction.** Consequences, both load-bearing:

1. A term computed over the `zw` carve set **cannot double-count `op_flat_disp`** — the safety objection that blocked this rung does not apply.
2. `fc_leaf_register(x, pfx + own)` registers each node at a displacement that **ALREADY INCLUDES THAT NODE'S OWN K** — but only for `fc_geom`-granted nodes. For `zw` carve-only nodes `own` is 0, so their `op_flat_disp` is **blind** to their carve. **The two node classes need OPPOSITE compensation, and today one rule serves both.**

---

## THE WITNESS — `028_arith_unary_minus`, complete in 74 lines

`OUTPUT = -5` prints `5`. This is the same program ZTOS-1's own comment claims it cured; CARVE-ERAD re-broke it.

Emitted depth trace (`scrip --compile`, default regime):
```
main_α       sub rsp,56    → rsp = R
n0_lit_α     sub rsp,16    → rsp = R-16 ; writes literal DESCR at [rsp+0]/[rsp+8] = R-16/R-8
                             jmp n1_unop_α   ← NO POP: fc_geom grant, base>=0, cell SUSPENDS at γ (S10c)
n1_unop_α    sub rsp,16    → rsp = R-32 ; reads [rsp+32] = R          ⛔ literal is at R-16, 16 BYTES BELOW
             call rt_num_neg ; writes result back to [rsp+32] = R
             add rsp,16    → rsp = R-16
n2_assign_α  reads [rsp+0] = R-16   ← the ORIGINAL, UN-NEGATED literal
             add rsp,16 ; NV_SET("OUTPUT")  → prints 5
```
`n1` negates garbage from `R` and stores it to `R`; the literal at `R-16` is never touched; `n2` reads it and prints `5`. **Mechanical, no theory required.**

The read is **NOT** ZTOS. The `vfcu()` arm of `bb_unop` was not taken (no `IR_UNOP fc` comment in the `.s`), so those are `FRQ(op_sa)` — the STATIC authority, `x86_frame_off` = `off + op_flat_disp + op_zdepth`.

---

## THE DISCRIMINATING MEASUREMENT — two readers, one program, opposite carves

| reader | own carve | correct offset | emitted (default) | error |
|---|---|---|---|---|
| `n1_unop` | **16** | 16 | **32** | **+16** |
| `n2_assign` | **0** | 0 | **0** | **0** |

**The error equals the reader's own carve, and is zero when the reader carves nothing.** That is the signature of a *self*-double-add. A spine prefix would displace BOTH readers by the same upstream amount (16, n0's suspended cell) — it does not. **This single table falsifies the running-sum reading.**

---

## EXPERIMENT 1 — RUNNING SUM (the plan of record). FALSIFIED. DO NOT RETRY.

Implemented exactly as the s21x-s cursor specifies: `op_zprefix` = running sum of upstream **suspended** carves (`op_fc_base >= 0` only — carve-only cells bracket at both exits and are rsp-neutral), published before each node emits and advanced after, per-graph reset keyed on `g_emit_cfg`, accumulated in `walk_bb_node` (the one traversal the emitter already does — no pre-pass), subtracted in the static arm.

**Result on the witness:**
- `n1_unop` `[rsp+32]` → `[rsp+16]` ✅ **correct**
- `n2_assign` `[rsp+0]` → `[rsp+-16]` ❌ **broken**

`n1` was repaired **by coincidence**: the upstream prefix (n0's 16) happened to equal n1's own carve (16). `n2` has prefix 16 and own carve 0, so the subtraction moved a correct reader off its cell. **A prefix is a property of the SPINE; this error is a property of THE READER.**

## EXPERIMENT 2 — DROP `op_zdepth` FROM THE STATIC ARM GLOBALLY. FALSIFIED. DO NOT RETRY.

Rationale: if `fc_leaf_register(x, pfx+own)` already carries own K, the static arm's `+ op_zdepth` is a pure double-add. Gated `SCRIP_ZRUN=1`, single line in `x86_frame_off`.

- Witness: `-5` ✅ **fixed** (n1 → `[rsp+16]`, n2 → `[rsp+0]`, both correct)
- **Corpus: m3 193/124 · m4 190/125 — a NET LOSS OF 36 PROGRAMS.**

**Why it loses:** it is right only for `fc_geom`-granted readers. For `zw` carve-only readers `fc_leaf_walk` recorded `own = 0`, so `op_flat_disp` never included their carve and `op_zdepth` is their **only** compensation. Removing it strands every one of them.

**Default-path safety re-verified after both experiments:** m3 230/87 · m4 227/88/2 · DIV=1 — byte-neutral within the `test_string` nondeterminism the s21x-s cursor already logs (rc=139, ~27% of environment sizes, ASLR/rsp-sensitive; it is the ±1 between 229 and 230). **Both experiments were REVERTED; the tree is clean at `1c0124f1`.**

---

## THE NARROWING THIS ESTABLISHES (the next rung, precisely stated)

`op_flat_disp` is neither wrong (deleting it costs 3 programs — s21x-s falsified claim 1) nor right (keeping it whole costs 88). **It is correct for exactly one of the two node classes.** The repair is therefore a **per-node conditional in `x86_frame_off`**, not a term added, subtracted, or deleted for everyone:

- **`fc_geom`-granted node** — `op_flat_disp` already carries own K ⇒ static arm must **NOT** add `op_zdepth`.
- **`zw` carve-only node** — `op_flat_disp` is blind to the carve ⇒ static arm **MUST** add `op_zdepth`.

⚠ **THE PREDICATE IS NOT SIMPLY `op_fc_base >= 0`, AND THIS IS THE OPEN QUESTION.** The `SCRIP_ZPROBE` census reports `n1_unop` with `k=16` under `fc_geom(nd,&_d) ? -1 : zw_node_k(nd)` — i.e. **`fc_geom` DECLINED** for n1, which by the rule above should mean "add `op_zdepth`", yet adding it is exactly what emits the wrong `[rsp+32]`. So either (a) `op_sa` for a cross-box operand read is already expressed in the producer's granted frame and the reader's class is the wrong key, or (b) `fc_leaf_register` is reached for n1 through the pair/ALT recursion arms (:1057/:1062) at a `pfx` that differs from the linear-spine walk. **Resolve which BEFORE writing the conditional** — the fastest instrument is a one-line dump of `(nid, op, op_sa, op_flat_disp, op_zdepth, op_fc_base)` at the `x86_frame_off` call site on this 3-node program; it is decisive in one run and the program is small enough to read whole.

## WHAT THIS MEANS FOR "20 SESSIONS OF STRUGGLING FOR UNKNOWN REASONS" (Lon, s21x-t)

The reasons are no longer unknown, and the tree already says so at `x86_asm.h:865` (ZOP-1): four coherent operand regimes were, before that rung, the cartesian product of five independent booleans — 32 representable states per node, decided **per node inside one graph**. ZOP-1 named the arms; **it did not make the arms agree on who compensates for what.** This finding is the next step down that path: the disagreement is now localized to ONE function (`x86_frame_off`) and ONE binary question (which carve authority granted this node), on a two-reader witness that fits on a screen.

**Also worth recording, because it reframes the ask:** most of the s21x-t directive is ALREADY LANDED and was verified live this session — operand access parameterized over the four modes (`x86_zop`, ZOP-1), no raw rsp in templates (ZTOS/ZTOSD/FR/FRQ), sliding offsets indexed from rsp (`x86_ztos` = `off + op_zdepth`), allocation tied through `x86_alpha()`/`x86_beta()` (GLUE-3, x86_asm.h:1920-1923), both glue codes present and wired (`bb_glue_flat.cpp` flat-jumps, `bb_glue_framed.cpp` flat + frame setup), and per-BB dynamic arming (`SCRIP_BB_ALLOC_ALL` / `SCRIP_BB_ONLY` / `SCRIP_BB_SKIP`). The open work is not the allocation mechanism. **It is the addressing rule the readers use.**

---

## PROCESS NOTE (worth one line, RULES.md (a)-shape)

The three repos were first cloned with backgrounded `git clone` and renamed mid-flight, producing exactly the poisoned half-tree the O2-DIRECTED-ONLY rule warns about — `.git` present with a `tmp_pack_*`, worktree empty, and `git log` reporting "does not have any commits yet". Caught before any build. **Clone in the foreground, or verify `git log --oneline -1` per repo before trusting a tree.**
