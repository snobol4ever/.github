# SESSION CLOSE — 2026-06-24 — Sonnet — ICON gate: IR_LIMIT in alt_safe_kind → rung14 5/5

## One-line: Added IR_LIMIT to the alt_safe_kind whitelist; limit-over-alt now native m3+m4. Suite 151→153. Gate analysis maps every EXCISED benchmark blocker precisely.

**Repos:** SCRIP `a872f56` on origin/main. corpus and .github clean at origin HEAD.

---

## 1. WHAT LANDED

### SCRIP `a872f56` — gate widening: IR_LIMIT in alt_safe_kind

`src/driver/scrip.c` `alt_safe_kind()` — added `t == IR_LIMIT` to the whitelist.

The whole-graph `alt_safe_kind` taint excised any alt-containing graph whose nodes were
not all whitelisted. `(1|2|3|4|5)\2` and `("a"|"b"|"c")\2` contain IR_LIMIT (not
whitelisted) so excised, even though the emitter already handles limit-over-alt
(bb_limit counter + bb_alt, both proven). Adding IR_LIMIT admits exactly these two shapes.

The alt-arm literal restriction (`alt_arms_all_simple_lit`) is unchanged. Alt graphs with
IR_BINOP/IR_CONJ/IR_VAR (augconcat/nested/seqexpr) STAY excised — emitter cannot do
alt-value cross-products yet (verified: blanket arm-scoping regresses 3 rungs).

**Suite: 151→153, FAIL=5 unchanged, EXCISED 91→89.**
smoke 12/12 m3+m4, prolog 5/5, no-stack/one-reg/semicolon-prison/local-no-nv green.
Benchmark .s artifacts: version.s current, no drift from gate change.

---

## 2. DIAGNOSTIC MAP — EVERY EXCISED BENCHMARK AT `a872f56`

Instrumented the gate (grej helper + env-gated logging) and peeled layers empirically.
This is the CORRECTED, HEAD-current map (supersedes the 2026-06-23 handoff which was
at fa33cd6, now outdated).

### 2a. LAYER 1 — whole-graph alt_safe_kind taint (FIRST trigger for 7/11)

The old gate: if ANY graph node is not alt_safe_kind, AND the graph contains any IR_ALT,
the whole graph excises. After the IR_LIMIT fix this is only the 7 benchmarks with
IR_BINOP/IR_CONJ/IR_VAR mixed into alt graphs.

After arm-scoping (remove whole-graph taint), the second trigger becomes visible:

### 2b. LAYER 2 — local-assign unsupported RHS shape (first trigger for 9/11 after L1 peeled)

| Benchmark | lhs=… | RHS kind | Specific shape |
|-----------|--------|----------|----------------|
| concord, micsum, options | name/a/x | IR_CALL dval=3.0 "get" | `x := get(arg)` generator-call RHS |
| deal, rsg | hands/line | IR_ALT | `x := a \| b` alt-RHS |
| geddump, ipxref | p | IR_LIST_BANG | `x := !L` |
| post | write | IR_VAR "writes" | `write := writes := 1` chained-assign |
| tgrlink | latmax | IR_SECTION | `x := s[i:j]` |

queens: layer-2 trigger is IR_ALT with non-literal arms (alt_arms_all_simple_lit fails).
shuffle: IR_SWAP with non-var operands (first trigger at L1 peel).

### 2c. HARD REJECTS underneath (per the gate hardcodes)

IR_INITIAL (deal/queens/post/ipxref/tgrlink), IR_SUSPEND (tgrlink), IR_IDX_SET
(queens/rsg/tgrlink), IR_RASGN (queens), IR_SWAP-non-var (shuffle).
These have documented reasons in the gate comments.

---

## 3. PROBE FINDINGS (empirical, not assumed)

### rung14 (the unit that LANDED)
Blanket arm-scoping (remove whole-graph taint) was tested and **regresses 3 rungs**:
rung13_alt_alt_augconcat, rung13_alt_alt_nested, rung16_seqexpr_gen_basic —
all have IR_BINOP/IR_CONJ consuming the alt (concat/augassign/seqexpr cross-products
the emitter can't do). The surgical fix (whitelist IR_LIMIT only) avoids all 3.

### rung06_cset_upto_basic (NOT landed — emitter gap confirmed)
Gate line 320 (gen_scan_body_slotful check) rejects `every write(upto(' '))`.
Neutered the check → m3 produces `6` but **doubled** (6\n6), m4 **asm-fails**
(bb4800_α already defined twice). Root cause: `flat_drive_every`'s chain-level
dedup (`flat_chain_set_has`, emit_bb.c:2762) doesn't cover the scan-body
sub-emission path (`flat_emit_arg_subchain`, line 2224), which re-emits already-
emitted boxes. The gate line 320 reject is CORRECT to keep.

### micro.icn (pre-existing, not touched)
Segfaults the compiler (rc=139) on `--compile`. Flagged for separate investigation.
`micro.s`/`micsum.s` in corpus/benchmarks/icon/ are stale from an earlier compiler
that no longer produces them. Corpus hygiene decision deferred to Lon.

---

## 4. PRECISE NEXT-SESSION TARGETS (by effort/payoff, post-probe)

1. **rung06 scan double-emission** — fix `flat_emit_arg_subchain` to dedup against
   the chain-body emitted set (`flat_chain_set_has`). Precise location known.
   Unblocks a cluster of every+scan rungs.

2. **suspend pieces 2+5** (DESIGN-ICON-SUSPEND §4A) — pieces 1/3/4+wiring already in
   (`545ccd9`/`9b7d463`). Piece 2: prologue entry-dispatch in `xa_flat.cpp` for
   generator procs (gated on `g_gen_proc_active`). Piece 5: caller gen-call box.
   Then flip gate. 3-rung payoff (rung03 ×3). Most documented, Lon-approved design.

3. **rung06_cset_cset_var** — `any(vowels)` where vowels holds a cset value (runtime
   variable-cset dispatch). Separate from the double-emission bug.

4. **richer alternation** (non-literal alt arms + arm-scoped alt_safe_kind) —
   verified regresses 3 rungs if done blanket; needs alt-in-binop/conj emitter work
   FIRST, then the arm-scope change becomes safe.

5. **assign-RHS shapes** (LAYER 2): `x := get(arg)` (gen-call RHS, 3 benchmarks),
   `x := a|b` (alt RHS, 2 benchmarks) are the highest-count missing shapes.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
