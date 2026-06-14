# HANDOFF 2026-06-14 — Icon m3/m4: real bb_every box + native s[i:j] + native !x (Claude)

**Goal:** GOAL-ICON-FULL-PASS — Icon `--run`/`--compile` up to m2 parity.
**Result:** m3/m4 **111 → 117 (+6)**; with concurrent landings the suite reads **118** at the final HEAD. m2 held at **202** (HARD) throughout. FAIL 36 → 29.
**HEAD (SCRIP) = `bcef3df`** (3 commits, rebased onto a fast-moving remote). HEAD (.github) = this file.

All three fixes are the SAME safe class as the prior odometer session: the lowering graph
was already correct (m2 prints the right output from the identical graph), so only native
binding changed and the m2 HARD gate provably cannot move. Each fix passed the full gate
battery before commit.

---

## (1) `bb_every` is now a real four-port box (`52b9ce9`) — byte-identical, no score change

**The finding (HANDOFF-2026-06-13-OPUS48-ICON-BB-EVERY-BOX-MISSING) was right but the literal
ask was not achievable as stated.** That handoff asked to move ALL canonical topology
(start→gen; expr.success→body; body→expr.resume) INTO `bb_every`. Reading canonical
`ir_a_Every` (refs/jcon-master/tran/irgen.icn) and `lower_every` (lower_icon.c) shows why that
is impossible in this lowering:

- Canonical `ir_a_Every` has **NO `ir.success` chunk** — EVERY never succeeds; it only fails
  on generator exhaustion (`expr.failure → ir.failure`), and a bounded resume also fails.
- `lower_every` builds `IR_EVERY` with **ONE operand** (`gen_entry`) and wires the loop
  back-edge (`gen_result.γ → generator.β`) INTO the child subtree during lowering. The
  generator's failure edge targets the EVERY node (`ω=E`), so **E.α is reached at generator
  exhaustion**. The expr and body are FUSED into the one child subtree — they are not separate
  operands the box could wire between.

So the genuine, correct box in this flat/stackless model owns only its two failure-routing
ports; the loop edges are emitted by the chain walk of `child0` (correct data-flow loop, not a
box-owned back-edge). The defects that actually existed:
- `bb_every()` emitted the β label **twice** — once via `x86("label",_.lbl_β)` (TEXT-only:
  empty in BINARY) and once via `x86("def","β")`. Duplicate label + a TEXT/BINARY asymmetry.
- α fell through β instead of owning its own `jmp ω`.
- `flat_drive_every` pushed `EMIT_PAIR_JMP/DEF_JMP` entries `bb_every` never consumed (it does
  not call `x86_pair_loop`) — dead.

**FIX:** `bb_every()` = `comment + jmp ω (α path) + def β (once) + jmp ω (β path)`. Removed the
dead `EMIT_PAIR` pushes in `flat_drive_every` (both CASE A and CASE B). Files:
`src/emitter/BB_templates/bb_every.cpp` (+2/−2), `src/emitter/emit_bb.c` (−3).

**Verification:** byte-snapshot of **all 122 every-bearing rungs × 3 modes** = IDENTICAL
before/after (except 4 known-flaky rung36/37 residuals that vary run-to-run on the current
binary independent of this emitter-only change — proven by running them 3–5× on the unchanged
binary; verdicts stable). m2 202 · m3/m4 unchanged by this commit · compound `every X;
write("done")` routes exhaustion to the next statement in all 3 modes.

## (2) native `IR_SECTION` `s[i:j]` (`29865e0`, +3) and (3) native `!` `IR_LIST_BANG` (`bcef3df`, +3) — SAME root cause

The SECTION machinery (bb_section template + flat_drive_section, committed `5787752` by a prior
session) and the bang driver both already computed the right value into the producer node's own
slot, but `write` printed empty/wrong:

**`descr_chain_arity` (emit_bb.c) had NO case for `IR_SECTION` or `IR_LIST_BANG`** → both fell
to `default: return -1`. In `descr_chain_operand_refs`, `ar < 0` triggers `sp = 0; continue` —
which **resets the operand stack and never pushes the producer node**. The consuming `write`
CALL therefore got `n_operands = 0` (`ir_call_arg(CALL,0) == NULL`), failed the
`g_descr_flat_chain && bb_slot_get(a0) >= 0` test in `bb_call_write_route`, fell to the
`rt_call_arr` by-name route, and that route's `marshal_call_arg` never copied the on-thread
producer result into the arg array (`op_arg_slot` is unpopulated on the descr path) →
uninitialised arg slot → empty (SECTION) / empty-with-right-count (bang, because the bang
generator still self-resumes through the flat chain).

Diagnosis confirmed by instrumenting `bb_call_write_route`: `write(s[1:4])` showed
`a0=nil n_operands=0`; `write(1 to 5)` showed `a0=TO n_operands=1 slot=32`.

**FIX (2 one-line additions, mirroring `IR_FIELD_GET`):**
```c
case IR_SECTION:   return 0;
case IR_LIST_BANG: return 0;
```
Both producers have their operands set by lowering (SECTION `[base,i1,i2]` at lower_icon.c;
bang `[iterable]` at TT_ITERATE) and their result slotted by the driver
(`flat_drive_section`/`flat_drive_list_bang` both `op_off = bb_slot_alloc16(pBB)`), so **arity 0
must NOT re-pop** — it just pushes the producer node onto the operand stack so the CALL adopts
it as `operand[0]`. Then `ir_call_arg(CALL,0)` == the producer, `bb_slot_get` returns its slot,
and `write` takes the clean WRITE_SLOT route (`mov rdi,[slot]; call rt_write_any_nl`) — the same
path `write(1 to 5)`/`write(s)` use.

**Rungs fixed:** rung20_section_seqexpr basic/var/full; rung11_bang_augconcat_bang_str,
rung15_iterate_string, rung22_lists_bang_list. (`.expected` trailing-newline differs across the
bang rungs but the suite strips it via `want=$(cat …)` — not a real mismatch.)

---

## Verification (full battery, run before EACH commit)

| Check | start | final |
|---|---|---|
| Icon m2 (HARD) | 202 | **202** |
| Icon m3 `--run` | 111 | **117** (118 w/ concurrent) |
| Icon m4 `--compile` | 111 | **117** (118 w/ concurrent) |
| Icon FAIL | 36 | 29 (pure FAIL→PASS) |
| Icon smoke | 12/12/12 | 12/12/12 |
| Prolog smoke | 5/5/5 | 5/5/5 |
| Prolog rung suite | 114 interp | 114 interp (IR_SECTION/IR_LIST_BANG are Icon-only; Prolog provably untouchable) |
| no-stack / one-reg / FACT / push-pop | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| bb_one_box | 56 | 56 (PRE-EXISTING — proven by pristine==changed count; the "45" in older handoffs was a stale earlier-HEAD count) |

The two `descr_chain_arity` additions are surgical — they only affect `IR_SECTION`/
`IR_LIST_BANG` nodes, which only the section/bang rungs contain; the suite delta is a clean +6
(FAIL→PASS) with no EXCISE→FAIL and no collateral.

---

## Key intel (reused / re-confirmed this session)

- **The `descr_chain_arity` "missing producer kind" bug is a CLASS.** A producer whose operands
  are set by lowering and whose result is slotted by its driver MUST have a `descr_chain_arity`
  case (arity 0, like `IR_FIELD_GET`) or the consuming CALL never adopts it → off WRITE_SLOT →
  empty/wrong arg. The generator kinds STILL MISSING from `descr_chain_arity` (default −1):
  **`IR_ITERATE`, `IR_LIMIT`, `IR_PROC_GEN`, `IR_KEY_GEN`, `IR_FIND_GEN`, `IR_SEQ_GEN`.** Check
  these FIRST next session — the rc=124 `rung14_limit_*` cluster may be (partly) this same gap
  (though rc=124 is a timeout, so the limit may ALSO have a separate non-termination bug; verify
  with `--dump-bb` + an instrumented `bb_call_write_route`).
- `ir_call_arg(nd,j)` returns `nd->operands[j]` (NOT the arg subgraph `subs[j]->entry`). On-thread
  producers reach the CALL only via `nd->operands[]` set by `descr_chain_operand_refs`.
- `bb_call_write_route`: route 1 (WRITE_SLOT, the clean path) needs
  `g_descr_flat_chain && bb_slot_get(ir_call_arg(nd,0)) >= 0`.
- `bb_every`/`flat_drive_every`: the loop is in the child subtree, NOT the EVERY box. The box is
  reached once, at generator exhaustion, and only routes failure (α→ω, β→ω). Canonical EVERY has
  no `ir.success`, so the box correctly has no γ.
- Repo is FAST-MOVING (Prolog/SNOBOL4/Raku/Pascal land concurrently): `git pull --rebase` before
  every push; expect the suite tally and `bb_one_box` count to drift upward from concurrent work.

## NEXT (clearly scoped, priority order)

1. **`descr_chain_arity` gap sweep** — add the missing generator kinds above; re-triage the
   rc=124 `rung14_limit_*` and any other rc=0 silent-wrong rungs that share the consumer-adoption
   bug. Highest-yield because it is the same one-line fix I just applied twice.
2. **accumulator-in-`every`** (rung02_proc_locals, rung10_augop_break_repeat): `every sum +:=
   (1 to 5)` → gives 5, want 15. Generator-driven augmented assignment not persisting the
   accumulator slot across iterations. Separate root cause (assignment-target slot vs generator
   resume).
3. **real-arith native path** (rc=134: rung17/18, real-VAR pow): `descr_binop_opnd_slot` returns
   −1 for `IR_LIT_F`; no DESCR-in/out real-arith `rt_*`. Add the helper + a real-arith template
   arm (shared dispatch → gate the full suite + FAIL-diff).
4. **list/type builtins** (rc=134/139: rung22 push/put/pull/get, rung29 type/image): wire into the
   native call path.

## Files touched (SCRIP)
`src/emitter/BB_templates/bb_every.cpp`, `src/emitter/emit_bb.c` (bb_every + 2 `descr_chain_arity`
lines). 3 commits: `52b9ce9` (bb_every), `29865e0` (SECTION), `bcef3df` (bang).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
