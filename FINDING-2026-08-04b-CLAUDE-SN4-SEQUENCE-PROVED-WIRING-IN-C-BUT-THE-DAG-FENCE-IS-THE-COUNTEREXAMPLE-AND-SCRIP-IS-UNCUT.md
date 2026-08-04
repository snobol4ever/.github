# FINDING-2026-08-04b — SEQUENCE proved wiring in C; the DAG fence is the counterexample; SCRIP is UNCUT

## Session: 2026-08-04 (Opus, session 3). Goal: GOAL-SNOBOL4-BB (HQ seat).

**Zero SCRIP `src/` commits. No codegen file touched** (`src/emitter/`, `src/templates/`, `x86_asm.h`,
`src/lower/lower_snobol4.c` all untouched) — so the handoff's regen ×4 does NOT apply this session.

---

## Result 1 — SEQUENCE-IS-WIRING re-proved independently, and it is cheaper, not merely free

Re-proved rather than inherited. `test_sno_1.c` baseline rebuilt and re-diffed against a freshly written
`case1.sno` under `sbl -b`: 13 lines, byte-identical. Then the `seq_*` box was deleted and replaced with
the eight static edges; output byte-identical to BOTH the original and the oracle.

**New measurement the prior session did not have: the deletion REMOVES 39 instructions** (412 → 373 at
`-O0`, `gcc -S` mnemonic count). Sequence-as-wiring is a size win, not a neutral refactor.

## Result 2 — NESTING proved, including the W-1c.0 crash shape

The prior session's proof covered ONE flat n=3 sequence. Nesting is where a sequence box is most plausibly
needed, so a new embodiment was built: `corpus/probe/bb/test_sno_L13_nested_capture.c`, modelling
`'abcd' ? ((LEN(2) . A) LEN(2)) . B` — TWO nested sequences (n=2 outer, n=1 inner), ZERO sequence boxes,
with a CAS because `.` capture is DEFERRED to match success (manual pg 72). Byte-identical to `sbl -b`
across seven subjects `'' a ab abc abcd abcde abcdef`, i.e. including every failure path that exercises
unanchored retry and the ω→β backtrack chain.

**n=1 degenerates to a pure alias** (P_α→M1_α, P_β→M1_β, M1_γ→P_γ, M1_ω→P_ω) — a sequence box at n=1 would
be a no-op forwarder. **This file is a WORKING reference for W-1c.0**, which SCRIP still fails.

## Result 3 — the structural argument, and its unstated premise

A box earns existence by owning PORTS or STATE. A sequence owns neither: its port map is a fixed bijection
known at LOWER time (constant-folds to member ports, no runtime choice), and its only candidate state — the
matched extent — is `str(Σ+Δ0, Δ−Δ0)` where Δ0 is the CONSUMER's own entry cursor, *identical to P_α's
cursor because P_α IS the consumer's α*. Contrast ALTERNATE, whose β must resume whichever arm won: a
genuine runtime choice, hence its irreducible one word (prior session, proved negative).

⛔ **THE PREMISE: each member OCCURRENCE is its own node. True in a TREE. FALSE in a DAG.**

## Result 4 — ⛔ THE COUNTEREXAMPLE TO "NEVER": the DAG fence, and it is already in our own code

`emit.cpp:2430` states it: SNOBOL4 patterns are VALUES, so a reused pattern variable lowers as a SHARED
SUBTREE, and one physical root can be an element of TWO sequences. Its single σ/φ edge can be statically
aimed at only ONE parent's neighbour. **The counter is the DAG's runtime disambiguator** — a
return-address problem wearing a sequence-counter costume.

MEASURED (`SCRIP_BLOB_MAP=1`, reading `SEQVERDICT clean=`):

| corpus | IR_MATCH_SEQUENCE nodes | clean (static wiring OK) | counter REQUIRED |
|---|---|---|---|
| `corpus/probe/bb/probes` (141 probes) | 150 | 150 | **0** |
| `corpus/programs/snobol4` + `benchmarks/snobol4` | 1087 | 1061 | **26** |

The 26 live in EIGHT files: `Gen.sno` · `Gen_driver.sno` · `omega.sno` · `omega_driver.sno` ·
`TDump_driver.sno` · **`beauty.sno`** · `treebank-list.sno` · `treebank-array.sno` — exactly the programs
that store a pattern in a variable and reuse it. **`beauty.sno` is the Milestone-1 program**, so cutting
the counter before the 26 have a home breaks the milestone.

**PRECISE CLAIM (supersedes the unqualified "NEVER"): BB_SEQUENCE is never required FOR SEQUENCING.** The
counter survives only as a shared-subtree return address — a different job, belonging elsewhere.

## Result 5 — SCRIP had already half-landed this, in code

- `emit.cpp:1135` `seq_static_on()` returns TRUE for **every** `IR_MATCH_SEQUENCE`; its own comment:
  *"sigma/phi static re-point is valid for EVERY match-sequence — celled counter was pure glue-dispatch
  bookkeeping."* Independent corroboration of the proof, from the codebase.
- HEAT-1 H1b (`emit.cpp:1189`) already aliases the FC/SEQ-STATIC arms away, calling them *"pure
  trampolines: jmp γ / af: jmp ω."*
- `bb_match_sequence.cpp` already carries a ZERO-CELL arm (`op_fc_seq`, ZB-FC-3b).
- `lower_snobol4.c:1106` states the governing rule: **"a construct earns a node iff it OWNS RUNTIME
  STATE."** Applied honestly to a TREE, that rule deletes the node itself.

---

## ⛔ Result 6 — IR_GOTO: DO NOT DELETE. It is the monitor's trace anchor.

Question raised this session: is `IR_GOTO` also pure wiring? Its template is
`bb_goto() = x86_alpha() + x86_pair_loop()` — a label plus a jump, structurally the same trampoline shape
as the sequence glue. Built by ALL FIVE lowerers (129 refs). But it owns runtime identity an edge cannot:

1. **MONITOR ANCHOR (decisive).** `emit.cpp:992` — `IR_GOTO` fires `emit_mon_label_tap(op_stno)` under
   `MONITOR_BIN`. Only TWO emitter sites do this: `IR_GOTO` and `IR_STATEMENT_BEGIN`, whose own comment
   says its tap *"mirrors IR_GOTO's so the 2-way monitor syncs on true statement boundaries."* Both
   optimizer passes explicitly PROTECT stamped gotos (`dead_goto.c` skips `IR_GOTO && IR_LIT(nd).ival > 0`;
   `branch_chain.c` `bc_stamped()`). **Deleting IR_GOTO blinds the 2-way monitor — the instrument
   RULES.md makes MANDATORY for every divergence hunt.**
2. **Deferred/indirect targets cannot be edges.** `IR_GOTO_DEFERRED` (EVAL/CODE, manual Ch.9) and
   `IR_INDIRECT_GOTO`: label known only at runtime (`$X`, a CODE fragment's interior label).
3. **The redundant instances are ALREADY folded** by the middle stage — `bc_is_passthrough()` is true for
   `IR_SUCCEED` and `IR_GOTO`; `dead_goto.c` deletes unreferenced ones. That is the optimizer doing its
   job per the OPTIMIZER-STAYS-ON FACT RULE.

**Verdict: the opcode STAYS.** If it should vanish as a codegen artifact, drive the FOLD to totality
(measure survivors to emission, push to zero) — never remove the opcode.

---

## Deliverable — ONE COPY (Lon directive this session)

BB reference embodiments existed as **2–4 divergent copies** across `SCRIP/seed/`, `SCRIP/bench/`, and
`.github/`, and the ARCH docs pointed at THREE DIFFERENT ONES — so a session reading "the golden design"
got whichever copy its doc happened to name. Consolidated to ONE home: **`corpus/probe/bb/`** (25 artifacts).
`SCRIP/seed/` now holds only `beauty_prog_0428.s`; `SCRIP/bench/` and `.github/` hold none.

Two resolutions that were NOT mechanical copies:

- **`test_sno_2.c` / `test_sno_3.c` genuinely DIVERGED.** The `seed` copies are strict SUPERSETS carrying
  reconstructed SNOBOL4 source blocks with manual citations and honest "KNOWN BROKEN / not oracle-verified"
  notes that `bench` and `.github` lacked. `seed` won.
- **`test_sno_4.c` was a NAME COLLISION, not a duplicate.** The probe copy is BB-challenge Case 4
  (conditional capture inside the ARBNO body — the rung that reverted ZW16), which `BB-CHALLENGE-LADDER.md`
  references. `SCRIP/seed/test_sno_4.c` is a DIFFERENT program (labels `a6`/`condition4`/`match2`/`s5`/
  `subj3`). Moved in as **`test_sno_4_seed.c`** — ⚠ PROVISIONAL NAME, Lon to rename if desired.

`seq_*` labels across ALL test embodiments: **0**. Every edited file byte-identical to its pre-edit
baseline; `test_sno_1.c` additionally re-proved against `sbl -b`.

`test_sno_5/6.c` (stored pattern): `pat_frame_t` shrinks from `str_t seq` to `int Δ0`, and the `cat()`
accumulator chain is GONE with the double-count it invited. **These two files also demonstrate the answer
to the DAG problem**: a shared pattern as ONE code body with its OWN ζ plane, entered per-site with a
distinct frame — i.e. the return address belongs to a CALL, not to a sequence counter.

---

## ⛔ Two red flags found, neither caused by this session

1. **`scripts/test_gate_call2bb_stub_regime.sh` is RED at HEAD** — `m4 gated stub kt: got [8] want [48]`.
   PROVED pre-existing: restored the original seed bytes from `git show HEAD:` into a temp dir and re-ran
   with `PROBE=$T` — equally red. The move did not cause it. (Gate now reads `$PROBE`, default
   `corpus/probe/bb`.)
2. **`ARCH-ICON.md` pointed at `SCRIP/refs/bb/test_icon.c`** — a path under the gitignored `refs/` tree
   that does NOT exist in a fresh clone. Dead reference; repointed.

## State

- Build GREEN. Probe suite **95 pass / 46 xfail / 0 XPASS / 0 REGRESSION** — unchanged before and after.
- **BB_SEQUENCE / IR_MATCH_SEQUENCE IS NOT ERADICATED.** 45 refs across 10 files + `IR_SCAN_SEQUENCE`
  18 refs; `bb_match_sequence.cpp` and `bb_scan_sequence.cpp` both intact. Deliberately UNCUT pending two
  Lon rulings (below).

## ⛔ OWED — two rulings block the cut

1. **SEQUENCING:** stage the deletion AFTER W-1c.0 + W-2's flip, or now and accept voiding the W-0b
   baseline and the killswitch-OFF byte-identity net that W-1..W-4 rests on?
2. **THE 26 DAG SEQUENCES:** call-with-frame (the `test_sno_5/6.c` model — shared pattern is a callable,
   return address is the caller's continuation) or tree-ify (duplicate the shared subtree per occurrence:
   zero runtime state, costs code size)?

**Recommended end state once ruled:** keep `IR_MATCH_SEQUENCE` as a LOWER-internal STRUCTURAL node that
EMITS NOTHING — member list, consumed during lowering to assign edges, K=0, no cell, no counter, no
dispatch chain. That is a short step from where the code already is (static arm universally on; only the
fold gates it), preserves `--dump-ir` readability and an optimizer handle, and lets the counter arm and the
SEQ-CELL grant die on MEASUREMENT rather than argument. Retire the node itself later, once shared subtrees
are calls.
