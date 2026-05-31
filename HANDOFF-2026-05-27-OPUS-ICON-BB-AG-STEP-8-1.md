# HANDOFF — 2026-05-27 — Opus 4.7 — GOAL-ICON-BB: AG-PURE Step 8.1 (BB_EVERY)

**SCRIP** `f81e1d51` · **goal:** GOAL-ICON-BB · **mode priority:** mode 2 then mode 3

---

## WATERMARK

GATES: smoke_icon **5/5** · broker **24** · rungs **198** · smoke_prolog **5/5** — ALL UNCHANGED

---

## WHAT WAS DONE THIS SESSION

### 1. Merged `ag-pure-icn` branch into `main`

The previous session's work (Sonnet, AG-PURE Steps 1-7) had landed on the
`ag-pure-icn` branch at `de11aef2`. Meanwhile `main` had moved forward with
Prolog BB V-5 (ff42f323), SBL-BREAKX-3 (e4ffdefe), and RK-BB-2 prereq (8c9b4f0a).
A merge via `git merge --no-ff` followed by `git pull --rebase` cleanly
integrated all 10 ag-pure-icn commits onto main. No conflicts beyond an
auto-merge in `src/lower/bb_exec.c`. Pushed to `origin/main`.

After merge, `main` is at the state where BB_BINOP / BB_SEQ / BB_IF / BB_CONJ /
BB_ALT are all AG-pure (steps 1-7), and the chain walker pushes every node's
`cur->value` (including FAIL) into the `BB_graph_t.ring` after each step.

### 2. AG-PURE Step 8.1 (BB_EVERY) — dispatcher passthrough

**Commit:** `f81e1d51` on `main`.

**The problem:** BB_EVERY's executor drives its child generator via
`bb_exec_node(nd->α)` recursively, which does **not** go through the outer
chain walker. Therefore the generator's value never enters the cfg ring,
so any downstream peek-based consumer can't see it. Per the goal file:
"dispatchers must be AG-pure first" — until BB_EVERY becomes a passthrough,
the generators it dispatches can't be migrated.

**The fix:** Added an AG-pure passthrough branch to BB_EVERY's executor.
When the lowerer has marked the node as AG-pure (`nd->ival == 1`):

- `state == 0`: set `state = 1`, `value = NULVCL`, return `nd->α` — hand
  control to the gen via the outer chain walker. The chain walker then
  drives gen → body → back-edge-to-gen → ... → gen.ω = nd_every (loop exit),
  pushing each step's value to the ring along the way.
- `state == 1`: re-entry from `gen.ω` exhaustion. Reset `state = 0` (so
  this BB_EVERY is re-runnable on the next bb_exec_once), set
  `value = NULVCL`, return `nd->γ` (next stmt).

**Scope (conservative):** the AG-pure intercept in
`lower_icn_expr_threaded_b` activates only when:

```c
gen->α == NULL && gen->β == NULL && gen->γ != NULL
```

i.e. only when TT_EVERY's existing flat-wire (lower_icn.c:444) was actually
laid down. That requires the gen to be a literal-bound generator (BB_TO 1 5,
BB_TO_BY 1 10 by 3, BB_ALT of literals). The flat-wire creates the loop
back-edges that the chain walker needs to follow:

- `gen.γ → body` (gen value → run body)
- `body.γ → gen` (body done → resume gen — the loop back-edge)
- `body.ω → gen` (body fail → resume gen)
- `gen.ω → nd_every` (gen exhausted → loop done)

For dynamic-bound gens (`gen->α != NULL`) and BB_CALL-with-gen-args
(`every write(1 to 5)` — the common idiom — has gen=BB_CALL with arg-chain
on α), the legacy C while-loop in BB_EVERY's executor still drives. This
is intentional: those cases are Step 8.2 and Step 9 respectively.

**Files changed:**

| File | Change |
|---|---|
| `src/lower/lower_icn.c` | Added AG-PURE Family 8.1 intercept in `lower_icn_expr_threaded_b` before the `icn_leaf` fallback. Stamps `nd->ival = 1` as the AG-pure marker; α_out = nd_every (chain enters at the every node itself); β_out = ω_in. |
| `src/lower/bb_exec.c` | Added AG-pure passthrough branch at the top of `case BB_EVERY` in `bb_exec_node`, gated on `nd->ival == 1`. |

**Verification:**

- `every i := 1 to 3 do write(i)` → outputs `1 2 3` correctly (AG-pure path).
- All four gates green (smoke 5/5, broker 24, rungs 198, smoke_prolog 5/5).

---

## WHAT REMAINS (NEXT SESSION ENTRY POINT)

### Step 8.2 — BB_TO / BB_TO_BY dynamic-bound AG-pure

From GOAL-ICON-BB.md:
> Once EVERY drives via the chain walker, these can have AG-pure dynamic-bound
> paths. Cache lo+hi on first run (state==0) into counter (int pos) +
> dval-bit-cast (int hi) for int mode, dval (real pos) + counter-bit-cast
> (real hi) for real mode.

**Architectural question to resolve first:** the AG-pure intercept pattern
(see BB_BINOP at `lower_icn.c:1245`) builds an operand chain whose entry
is reported via `α_out`. But TT_EVERY uses `lower_icn_expr_node` (NOT the
threaded variant) to lower its gen subtree at line 424 of `lower_icn.c`, so
it gets the gen box but NOT a chain entry. For Step 8.2 to work, one of:

1. **(Recommended)** Make TT_EVERY's lowering route the gen through
   `lower_icn_expr_threaded_b` so it captures both the gen box and the
   chain entry. Set `nd_every.α = chain_entry` (= lo, the chain head)
   instead of `nd_every.α = gen`. The flat-wire condition then checks the
   actual gen box (not nd_every.α): if it has been AG-pure-converted, its
   α/β are scrubbed and its γ/ω can be safely overwritten with back-edges.

2. **(Special-case)** Recognize TT_TO with dynamic bounds inline inside
   TT_EVERY's case and build the chain in-place.

Option 1 is cleaner but touches more code; option 2 is local but doesn't
generalize. Lon's call.

**The BB_TO AG-pure executor (once fed via ring):**

- `state == 0`: `lo = peek(1)` (predecessor's predecessor pushed lo to ring),
  `hi = peek(0)` (immediate predecessor pushed hi to ring). Cache: int mode
  → `counter = lo.i`, `dval = bitcast(hi.i)`; real mode → `dval = lo.r`,
  `counter = bitcast(hi.r)`. Coerce errors → return ω. Yield counter as
  value; state = 1; return γ.
- `state == 1`: counter++ (int) or dval += step (real). If past cached hi,
  state = 0, return ω. Else yield; return γ.

Lowering for AG-pure TT_TO with dynamic bounds:
- Lower lo and hi as their own boxes; chain them: `lo.γ = hi; hi.γ = nd_to`.
- Scrub `nd_to.α = NULL; nd_to.β = NULL`. Keep ival as int-step or sval as
  "i"/"r" mode marker.
- Report α_out = lo (chain entry); β_out = self (resumable).

### Step 8.3 — BB_BINOP_GEN cross-product odometer

Explicitly "Major rework. Defer." per goal-file. Skip until 8.2 and 9 done.

### Dispatchers to consider for AG-pure conversion

BB_LIMIT, BB_REPEAT, BB_WHILE, BB_UNTIL, BB_SCAN — all have the same
recursive `bb_exec_node(nd->α/β)` pattern as BB_EVERY had before this
session. The same passthrough technique applies, gated on whether the
corresponding TT_* lowering can lay down the necessary back-edges.

### Step 9 — N-ary applies (BB_CALL / BB_LCONCAT / BB_SECTION / BB_IDX_SET)

This is what unlocks the **common** `every write(generator)` idiom for
AG-pure execution. BB_CALL with gen-args currently runs an internal
arg-odometer via recursive `bb_exec_node`. The migration: args chain via γ,
last arg's γ → apply; apply reads peek(N-1..0) from the ring.

### Step 10 — Sidecar cleanup

Delete `bb_operand_aux_set/get` calls from Icon lower path once all the
above are done. Sidecar struct stays for Prolog/SNOBOL4.

---

## ACCEPTANCE PROGRESS

From GOAL-ICON-BB.md acceptance criteria for the whole rewrite:

1. `grep -nE 'nd->[αβ] = ' src/lower/lower_icn.c | wc -l` == 0
   — **NOT YET**: dynamic-bound gens still set α/β as tree pointers.
2. `grep -nE 'bb_exec_node\(nd->[αβ]\)' src/lower/bb_exec.c | wc -l` == 0
   — **NOT YET**: BB_TO, BB_TO_BY, BB_CALL still do this recursion.
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

**SCRIP** `f81e1d51`

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
