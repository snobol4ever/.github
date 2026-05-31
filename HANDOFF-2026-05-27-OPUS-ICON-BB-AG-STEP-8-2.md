# HANDOFF — 2026-05-27 — Opus 4.7 — GOAL-ICON-BB: AG-PURE Step 8.2 (BB_TO / BB_TO_BY)

**SCRIP** `7acc7849` · **goal:** GOAL-ICON-BB · **mode priority:** mode 2 then mode 3

---

## WATERMARK

GATES: smoke_icon **5/5** · broker **24** · rungs **198** · smoke_prolog **5/5** — ALL UNCHANGED

---

## WHAT WAS DONE THIS SESSION

### AG-PURE Step 8.2 (BB_TO / BB_TO_BY dynamic-bound) — landed on `main`

**Commit:** `7acc7849`.

**The problem (continuing from 8.1):** Step 8.1 made BB_EVERY a passthrough
for literal-bound generators by gating on `gen->α == NULL && gen->β == NULL
&& gen->γ != NULL` — true only when TT_EVERY's lowering at lower_icn.c:444
laid down the flat-wire back-edges, which itself only happens for literal-
bound `to` generators (because those leave gen->α/β NULL). Dynamic-bound
generators (`every lo to hi`) had `gen->α = lo_box; gen->β = hi_box` and
fell through to the legacy C while-loop in BB_EVERY's executor.

For 8.2 we make BB_TO and BB_TO_BY themselves AG-pure when their bounds are
dynamic. After scrubbing their α/β tree refs, the flat-wire condition at
444 becomes true, and 8.1's BB_EVERY passthrough then naturally takes over.
The chain walker drives `lo → hi → nd_to → body → nd_to → … → nd_to.ω =
nd_every → 8.1 reentry → γ_in`.

**The architectural decision (from 8.1's handoff):** Option 1 was preferred —
route TT_EVERY's gen through `lower_icn_expr_threaded_b` so the 8.2
intercept fires before TT_EVERY's flat-wire block runs. This session
implemented option 1 in a **scoped** form: only when `e->c[0]->t` is
`TT_TO` or `TT_TO_BY`. Other gen kinds (BB_ALT, BB_BINOP_GEN, BB_CALL
with gen-args, ...) still go through `lower_icn_expr_node` so they don't
accidentally pick up intercepts written for non-generator forms.

### Implementation

**Three coordinated changes:**

#### 1. New lowering intercepts in `lower_icn_expr_threaded_b`

Placed after the BB_BINOP intercept (line 1267) and before the BB_IF
intercept (now ~line 1330):

- `TT_TO` with `nd->α && nd->β` (dynamic bounds): scrub α/β, chain
  `lo.γ = hi; hi.γ = nd; lo.ω = ω_in; hi.ω = ω_in`. Stamp `nd->sval = "ag"`.
  Report `α_out = lo` (chain head), `β_out = nd` (resumable gen).
- `TT_TO_BY` with `nd->α && nd->β` and `sval[0] ∈ {'i','r'}`: same wiring,
  but stamp `nd->sval = "ar"` (real mode) or `"ai"` (int mode), preserving
  the BB_TO_BY mode bit.

#### 2. New AG-pure executor branches in `bb_exec.c`

At the top of `case BB_TO` and `case BB_TO_BY`, before the legacy paths,
test `if (!nd->α && !nd->β && nd->sval && nd->sval[0] == 'a')`.

On `state == 0`: `lv = ag_ring_peek(cfg, 1)` (lo, pushed two steps ago),
`hv = ag_ring_peek(cfg, 0)` (hi, pushed one step ago); coerce to int (or
real for "ar"); cache `lo` in `counter` and `hi` (bit-cast int64) in `dval`.
For BB_TO_BY real mode, swap slots: `dval = lo_real`, `counter = bit-cast
hi_real`. Step is in `ival` (compile-time folded). Set state=1.

On `state == 1`: bump `counter` (int) or `dval += by` (real). Bound check
against cached hi. If past hi, state=0, return ω. Else yield via γ.

Crucially the chain walker re-enters at `nd_to` (NOT at `lo`) via the
back-edge `body.γ = gen` (where `gen` is the BB_TO box itself, not the
chain head). So lo/hi run exactly once on the initial entry; cached bounds
are stable across all iterations.

#### 3. TT_EVERY routing change in `lower_icn.c:420`

```c
if (e->c[0]->t == TT_TO || e->c[0]->t == TT_TO_BY) {
    BB_t *αo = NULL, *βo = NULL;
    gen = lower_icn_expr_threaded_b(cfg, e->c[0], NULL, NULL, &αo, &βo, 1);
    gen_chain_entry = αo ? αo : gen;
} else {
    gen = lower_icn_expr_node(cfg, e->c[0]);
    gen_chain_entry = gen;
}
```

Then `nd->α = gen_chain_entry` instead of `nd->α = gen`. 8.1's passthrough
returns `nd->α` from state==0, so the walker enters at the chain head (lo)
on AG-pure paths and at gen (unchanged) on legacy paths.

The flat-wire block at line 458–467 keeps using the local `gen` (= the
BB_TO/BB_TO_BY box returned), so the back-edges attach to that box, not
to the chain head. This is correct: the loop must re-enter at the counter
step, not re-run lo/hi.

### Verification (functional)

Hand-coded tests with instrumented trace runs (then removed):

| Source | c[0] kind | Path taken | Output |
|---|---|---|---|
| `every 1 to 5` | TT_TO (literal) | 8.1 only (flat-wire, no 8.2 intercept; α/β already NULL) | silent (no body) — ok |
| `every lo to hi` | TT_TO (dynamic) | **8.2 intercept + 8.1 passthrough + AG executor** | silent — ok |
| `every lo to hi do write("hit")` | TT_TO (dynamic) | **8.2 + 8.1 + AG executor** | 5× `hit` for lo=2..hi=6 ✅ |
| `every lo to hi by 2 do write("h")` | TT_TO_BY (dynamic) | **8.2 + 8.1 + AG_TO_BY executor** | 5× `h` for 1..10 by 2 ✅ |
| `every i := 1 to 3 do write(i)` | TT_ASSIGN | legacy path (no routing, 8.2 doesn't fire on TT_ASSIGN) | 1, 2, 3 ✅ |
| `every i := lo to hi do write(i)` | TT_ASSIGN | legacy path | 1, 2, 3, 4, 5 ✅ |
| `every write(lo to hi)` | TT_FNC | legacy path | 1, 2, 3, 4, 5 ✅ |

Traces confirmed 8.2 intercept fires exactly once at lowering, AG executor
fires exactly N+1 times for a range of size N (1 state=0 entry, N state=1
counter walks where the (N+1)th hits the bound-check failure).

### All four gates green

```
smoke_icon         5/5
broker            24
rungs            198 (FAIL=34 XFAIL=36 — unchanged from f81e1d51)
smoke_prolog       5/5
```

---

## WHAT REMAINS (NEXT SESSION ENTRY POINT)

### Step 8.2 follow-up: TT_ASSIGN-wrapped `every` is the common idiom

The common Icon pattern `every i := lo to hi do body` has `e->c[0]->t ==
TT_ASSIGN` with `e->c[0]->c[1]->t == TT_TO`. My routing only catches the
bare `every TT_TO ...` form, so the assign-wrapped form takes the legacy
executor path (correctly, no regression).

To make the common form AG-pure, one of:

1. **Recognize the TT_ASSIGN-of-TT_TO pattern in TT_EVERY's routing.**
   Walk one level deeper: if `c[0]->t == TT_ASSIGN && c[0]->c[1]->t in
   {TT_TO, TT_TO_BY}`, route the gen subtree through threaded_b. This is
   a local extension to the existing scoped routing — keep it tight.

2. **Make BB_ASSIGN gen-aware (Step 9 territory).** Once n-ary applies
   become AG-pure, BB_ASSIGN with a generator RHS would chain its RHS
   into the ring naturally and re-fire on resume. This is the more
   general fix but is part of step 9, not 8.2.

Option 1 keeps 8.2 scope-clean and unblocks the common idiom without
touching n-ary apply migration. Lon's call.

### Step 8.3 — BB_BINOP_GEN cross-product odometer

Goal-file explicitly defers as "Major rework."

### Other dispatchers to consider

BB_LIMIT, BB_REPEAT, BB_WHILE, BB_UNTIL, BB_SCAN — same recursive
`bb_exec_node(nd->α/β)` swallowing pattern as BB_EVERY had. Apply the
passthrough technique once the corresponding TT_* lowering can lay down
back-edges.

### Step 9 — N-ary applies

BB_CALL / BB_LCONCAT / BB_SECTION / BB_IDX_SET. Unlocks `every write(gen)`
and (with the TT_ASSIGN extension above) `every i := gen do …` for the
common case.

### Step 10 — Sidecar cleanup

Delete `bb_operand_aux_set/get` calls from Icon lower path.

---

## ACCEPTANCE PROGRESS

From GOAL-ICON-BB.md acceptance criteria for the whole rewrite:

1. `nd->α/β = ` writes in lower_icn.c — **DECREASING**: 8.2 intercept
   actively scrubs to NULL, but TT_EVERY still writes `nd->α = chain_entry`
   (refactoring tracks). Goal-file's grep regex uses `[αβ]` which doesn't
   match multi-byte chars correctly on grep -P-less systems; manual count
   of `nd->α =` lines in lower_icn.c is **73** (was 73 before 8.2 — net
   neutral since 8.2 added 2 scrubs and the TT_EVERY change preserves one
   existing write site). Will keep shrinking through steps 8/9/10.
2. `bb_exec_node(nd->α/β)` in bb_exec.c — **UNCHANGED**: 30 nd->β
   recursive sites remain. BB_TO and BB_TO_BY contribute their share via
   the legacy branches; AG-pure branches are additive in this session.
3. `icn_kind_owns_omega_operand` removed — **NOT YET**.
4. `bb_operand_aux_set` not called from Icon lower path — **NOT YET**.
5. rungs PASS≥198 holds throughout — **HOLDING ✅**.

---

## SESSION SETUP

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh            # PASS=5
bash scripts/test_smoke_unified_broker.sh  # PASS=24
bash scripts/test_icon_all_rungs.sh        # PASS=198
bash scripts/test_smoke_prolog.sh          # PASS=5
```

---

**SCRIP** `7acc7849`

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
