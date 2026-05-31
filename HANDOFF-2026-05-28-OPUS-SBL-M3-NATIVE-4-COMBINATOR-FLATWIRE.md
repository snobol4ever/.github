# HANDOFF — 2026-05-28 · Opus 4.7 · SNOBOL4-BB · M3-NATIVE-4 combinator flat-wire

## Repos / HEADs

| Repo    | HEAD       |
|---------|------------|
| SCRIP | `10f97d29` |
| .github | (this commit) |

Tree: **CLEAN** on SCRIP (post-rebase, pushed to origin/main).

---

## Three commits landed (rebased onto upstream `d805b0fe`)

| Hash       | Title |
|------------|-------|
| `1e9ae6c6` | bb_seq: n==0 BINARY arm walks EP-pair array — audit FAKE-JMP→REAL |
| `a4b62c1f` | M3-NATIVE-4: combinator flat-wire — patnd_to_bb_tree + LIVE routing |
| `10f97d29` | M3-NATIVE-4 extension: XNME/XFNME captures over combinator subtrees |

---

## Gates at handoff

| Gate | Result | Note |
|------|--------|------|
| G1 SNOBOL4 smoke (default+native) | 13/13 + 13/13 | |
| G2 unified broker | 38/53 | |
| G3 mode-4 broad corpus | 162/280 | |
| G4 mode-2 broad corpus | 237/280 | |
| Native broad corpus (`SCRIP_M3_NATIVE=1`) | **157/280** | up from 142 pre-session (+15) |
| Rung suite | M2=19 / M4=14 | unchanged |
| Prolog / Raku / Icon smokes | 5/5 each | |
| audit_m3_native | **GATE FAIL** | NOT my doing — see below |

**Audit FAIL is from upstream commit `6393c743`** ("IBB bb_call + bb_seq(n>0) MEDIUM_BINARY: hello.icn mode 3 PASS"), which landed between my clone and my push. It flagged `bb_lit_scalar.cpp` as FAKE-JMP. My three commits do not touch that file. At my push time the gate was OK. Whoever owns IBB will need to either fill the `bb_lit_scalar` BINARY arm with real bytes or `bomb_bytes` it. This is the ground-zero gap doc'd in PLAN.md's ICON-BB row.

---

## What was done this session

### 1. bb_seq.cpp n==0 BINARY arm rewrite (`1e9ae6c6`)

Audit script flagged the existing n==0 arm at `bytes(1,"\xE9") + u32le(0) + bytes(1,"\xE9") + u32le(0)` as FAKE-JMP STUB because the `bin = {…}` aggregate-init didn't trip the `bin.sites.push_back` substantive matcher. Rewrote both TEXT and BINARY n==0 paths to walk `g_emit.xa_bb_emit_pair_*` (populated by `flat_drive_seq`'s n==0 branch via `EMIT_PAIR_JMP(lbl_γ); EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω);`). Same FACT-clean shape as `bb_pl_seq.cpp`. Byte-emit is inline + `bin.sites/labels/is_def.push_back` per-pair. Audit: FAKE-JMP → REAL.

### 2. M3-NATIVE-4 combinator flat-wire (`a4b62c1f`)

**Root cause confirmed:** PATND_t `kind` enum (XCHR=0..XBRKX=27) and BB_t `t` enum (BB_op_t starting at BB_LIT_I=0) collide structurally — XCAT=19 raw-cast as BB_op_t reads as BB_EVERY=19. This is why `055_pat_concat_seq` aborted in native mode with `[IBB] FATAL walk_bb_flat: BB_EVERY needs flat_drive_every`. The pattern was XCAT but `(BB_t*)pp` misread it.

**Fix:** New `patnd_to_bb_tree` + `build_patnd_tree` in `src/lower/lower_pat_dcg.c`. For XCAT/XOR/XFNCE roots, builds emit_sm-shaped BB nodes (`BB_PAT_CAT/ALT/FENCE` opcodes) with explicit kid arrays via `bb_pat_kids_state_t` stashed in `nd->counter`. Atom leaves delegate to existing `build_patnd` (α/β/γ/ω fields are unread by the flat-drive consumer; sval/ival is what templates read).

**Routing:** New `patnd_tree_eligible` (recursive — combinators + capture wrappers + simple atoms; ARBNO disqualifies) and `patnd_is_combinator_root` in `src/runtime/snobol4/stmt_exec.c`. LIVE-mode dispatch routes combinator-rooted patterns through `patnd_to_bb_tree`; non-combinator patterns unchanged. BROKERED untouched.

**Why the prior attempt regressed (and this one didn't):** The GOAL log records a prior session getting native correct on alt_two/concat_seq but regressing broad corpus 237→229 due to dangling-stack-label addresses in `bin.labels` after flat-driver returns. Commit `744ae342` ("label arena landed") fixed that root cause — `emit_label_alloc` returns heap-backed labels with stable addresses across the emit session. With the arena in place, the tree-builder path is safe.

### 3. Capture-wrap extension (`10f97d29`)

Extended `build_patnd_tree` to handle XNME (`pat . var`) and XFNME (`pat $ var`) — translate inner via `build_patnd_tree`, wrap in `BB_PAT_ASSIGN_COND/IMM` node, attach inner as single kid via `tree_set_kids`. `pre_build_children` in `emit_bb.c` already routes ASSIGN_COND/IMM through `bb_build_brokered` for the child; the `bb_pat_kid(nd, 0)` path with α fallback finds the inner.

Extended `patnd_tree_eligible` and `patnd_is_combinator_root` to accept XNME/XFNME at the root and recursively inside.

**Canonical wins (the exact targets the prior log called out):**

| Test | Pattern | Subject | Native output |
|------|---------|---------|---------------|
| 050_pat_alt_two   | `('cat' \| 'dog') . V`           | `'dog'`      | `dog`     ✓ |
| 055_pat_concat_seq | `LEN(2) . A LEN(2) . B LEN(2) . C` | `'abcdef'` | `ab cd ef` ✓ |

---

## What's still wired wrong / next steps

### Immediate: upstream audit failure

`bb_lit_scalar.cpp` FAKE-JMP from `6393c743`. Not my code. Probably needs either `bin.sites.push_back` style real emission OR `bomb_bytes`. Coordinate with whoever owns IBB ground-zero.

### Next M3-NATIVE-4 step: ARBNO inside combinators

Rung suite still has 5 native FAILs: 052/054 (ARBNO patterns), 053 (alt_commit), 056 (star_deref), 057 (fail_builtin). The tree builder's `patnd_tree_eligible` currently rejects any subtree containing XARBN. The legacy `patnd_to_bb_graph` handles ARBNO (`build_patnd` line 450) by building a nested `BB_graph_t` block. To extend the tree builder, the XARBN branch needs to produce a `BB_PAT_ARBNO` node carrying its inner block in `bb_arbno_state_t` (`nd->counter`) — same shape `build_patnd` produces. Could likely just delegate XARBN to `build_patnd` since it doesn't need γ-chain wiring at this level, only its internal block does.

### 053_pat_alt_commit (`'no match'` instead of expected output)

ALT with commit semantics. Different bug from the route — needs investigation.

### 056_pat_star_deref / 057_pat_fail_builtin

The `*var` deref and `FAIL` builtin — likely not yet routed through the tree path. Add XSTAR/XFAIL handling if they appear at root level (currently `default → build_patnd` catches them as atoms; should work but the eligibility predicate may reject them).

### Eventually

Once all native broad corpus regressions / gaps are closed, flip the default: remove `getenv("SCRIP_M3_NATIVE")` guard in `scrip.c` so `--run` uses native by default. M3-NATIVE-4 endgame from `HANDOFF-2026-05-28-SONNET-SNOBOL4-BB-M3-NATIVE-2B-3.md`.

---

## Files touched

```
src/emitter/BB_templates/bb_seq.cpp        | 35 ++++++++++++++++++++---------
src/lower/lower_pat_dcg.c                  | 110 +++++++++++++++++++++++++++++
src/lower/lower_pat_dcg.h                  |   5 ++
src/runtime/snobol4/stmt_exec.c            |  56 +++++++++++++--
```

---

## Session setup for next session

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
# baseline
bash scripts/audit_m3_native_binary_arms.sh                           # currently FAILing on bb_lit_scalar (upstream)
bash scripts/test_smoke_snobol4.sh                                    # G1: 13/13
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                  # 13/13
bash scripts/test_interp_broad_corpus_and_beauty.sh | tail -1         # G4: 237/280
bash scripts/test_mode4_broad_corpus_snobol4.sh | tail -3             # G3: 162/280
SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh | tail -1   # native: 157/280
bash scripts/test_snobol4_pat_rung_suite.sh | tail -10                # M2=19 / M4=14
```

Canonical regression check:

```bash
SCRIP_M3_NATIVE=1 ./scrip --run /home/claude/corpus/crosscheck/patterns/050_pat_alt_two.sno     # dog
SCRIP_M3_NATIVE=1 ./scrip --run /home/claude/corpus/crosscheck/patterns/055_pat_concat_seq.sno  # ab cd ef
```

---

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
