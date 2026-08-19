# FINDING 2026-08-19 s149 — HQ-21 DOES NOT REPRODUCE AT ORIGIN HEAD, THE KW RUNG IS NOW ACTUALLY SWEPT, AND ONE KILLSWITCH IS TOO COARSE TO ISOLATE THE RUNG IT WAS USED TO MEASURE

**Seat:** claude.ai web (Claude Opus 5), continuing D-3 KW-STATIC.
**Trees:** SCRIP `f80c3f4d` (= origin/main at session start, unmoved) · corpus `a51c7d25` · baseline worktree built at SCRIP `bc0eeff4`.
**Files touched:** `scripts/util_s_md5_sweep.sh`, `scripts/ab_board_sweep.sh`, `scripts/test_gate_kw_static.sh`. **ZERO `src/` files** — so the ×3 `.s` regens are not triggered and the default arm is byte-identical by construction.

---

## 1 ⛔ THE HQ-21 CONVICTION DOES NOT REPRODUCE — MEASURED THREE WAYS

HQ-21 convicted s148's KW-3b (`746f0757`) of breaking the default arm and made the repair top priority
before any new rung. Measured at origin HEAD, with the baseline built in its own worktree at the named
pushed commit `bc0eeff4` (never this seat's tree):

| HQ-21 claim | Measured s149 |
|---|---|
| every `probe/cn` witness FAILS default arm; `&W = "hi"` dies with READ 342 at stmt 0 | **28/28 PASS** — every witness × {arm 0,1} × {m3,m4} |
| UDC gate reads 2/12 (claimed 12/12) | **12/12** |
| all 529 sweep md5s moved (byte-identity violation) | **0 movers**, 527 comparable, 2 excluded (rc≠0) |

The structural repair HQ asked for is **already present and was present at `746f0757`**:
`sno_kw_static_slot()` (`lower_snobol4.c:13`) is the ONE AUTHORITY and returns −1 whenever `rt_kw_index()`
misses, so any name the canonical block does not name — every tier-3 user constant — keeps the verbatim
by-name `SNO$KWSET` route into `rt_keyword_write_snobol4`'s NV fallthrough. That is precisely why the
default arm is byte-identical: the new kind is minted only when **armed AND** the block names the keyword.

### The mechanism that manufactures HQ-shaped numbers — NAMED, MEASURED, AND IT IS NOT KW-3b
Pairing a **fresh driver with a stale `out/libscrip_rt.so`** produced **40 spurious `.s` movers** against an
otherwise identical tree. The emitter lives in the `.so`; `make scrip` alone leaves the previous emitter in
place, so the driver mints the new kind while the runtime half is the old one. RULES already warns
"A/B ON EMITTER BEHAVIOUR MUST SWAP `out/libscrip_rt.so`, NOT THE DRIVER" — this is that law's other edge:
**swapping the driver WITHOUT the `.so` is equally vacuous, and it invents movers rather than hiding them.**
40 ≠ 529, so this does not fully account for HQ's reading; it is the only reproducible mechanism found.

⛔ **The CN-4/CN-4b/CN-5 landings are NOT "unverified riders on a broken write path."** They ride a write
path that measures green in all four cells. The HQ-21 banner should be dispositioned before it costs another
seat a session repairing something that measures correct.

## 2 ⭐ THE SWEEP s148 SAID WAS MANDATORY, AND NEVER RAN, IS NOW RUN

s148's own cursor: *"THE BY-SET A/B WAS NOT RUN … the next seat must run `ab_board_sweep.sh` base-vs-fix and
default-vs-armed BEFORE this rung is trusted."* Run three ways, **row-by-row, not totals** (totals hide
compensating flips — the KW-2 lesson):

| comparison | rows | result |
|---|---|---|
| base `bc0eeff4` default vs HEAD default, m3 | 318 | **IDENTICAL, zero row movement** |
| HEAD default vs HEAD armed, m3 | 318 | **IDENTICAL** |
| HEAD default vs HEAD armed, m4 | 318 | **IDENTICAL** |

`082_keyword_stcount` — the row whose KW-2 regression was invisible to the small witness gate and which is
the entire reason this instrument exists — is **PASS in the armed arm**. KW gate: **armed 10/14**,
legacy 0/14 (by design). The two armed reds are the documented routed pair, neither a regression:
`kw_bare_shadow` = HQ's B1, `kw_protected_write` = needs the KW-5 `&ERRLIMIT`→statement-failure mechanism.

**One pre-existing m3≢m4 gap surfaced and is NOT KW's:** `132_pat_fence_eps_recur_shallow` compiles
identically at both commits (`.s` 48461 bytes, byte-identical) and then **fails to LINK: `undefined reference
to FN__makeP`** — a `DEFINE`'d function referenced but never emitted. Arm-independent, commit-independent,
mode-4 only. It violates DoD-1's m3≡m4 and belongs to the DEFINE/linkage family. **Routed, not taken.**

## 3 ⛔ THE `.s` MD5 SWEEP NOW RECORDS rc — BUT s148 ROUTED THIS DEFECT TO THE WRONG INSTRUMENT

`util_s_md5_sweep.sh` tested only `[ -s p.s ]` — **non-empty** — so a compiler that SEGVs mid-emission left a
truncated-at-a-nondeterministic-point `.s` that was md5'd as if it were real output: the s33 "non-empty is
not alive" false signal living *inside* the instrument every codegen rung is validated against. Fixed: rc is
captured, a non-zero rc reads `RC_<rc>` and is never md5'd, and the summary prints `comparable(rc=0)`.

⛔ **But the s148 cursor pointed at the wrong instrument.** The five rows it named as noise
(`128_pat_recursive_grammar_right_rec`, `160_pat_alt_inner_gen_resume`, `216_indirect_goto_computed`,
`cf_goto_computed`, `null`, rc=139/139/139/132/134) **compile cleanly and stably** — verified rc=0 with
identical md5s across runs. Their crashes are at **RUNTIME**, so the unsound instrument was a runtime sweep,
not this one; and `calculator-1/-2`'s `TIME()` deltas are runtime stdout, which a `.s` sweep never sees.
The `.s` hole was real but **latent** (no row in the 529 list currently trips it — the two rc≠0 rows exit 1
with zero-size output, which the old code already classified stably as `COMPILE_FAIL`).
**The checked-in runtime instrument is sound and needs no fix:** `test_gate_rtx_killswitch_sets.sh` runs N
times per arm, hashes `out|rc=N`, and reports a multi-hash arm as QUARANTINE rather than MOVER.

Proof the fixed sweep is now sound: **529 rows, two consecutive runs on a fixed build, 0 diff.**

## 4 ⛔⭐ NEW — `SCRIP_CONST_STATIC` IS TOO COARSE TO ISOLATE CN-4b/CN-5, SO THE "STAGED, NOT CASHED" READING IS UNSUPPORTED

s148 concluded: *"Isolation A/B (same source, `SCRIP_CONST_STATIC` flipped) is byte-identical: CN-4b and CN-5
are consulted but inert at emit."* Two measured problems with that inference:

**(a) It is not byte-identical across the witness set — 4 of 9 `probe/cn` witnesses MOVE under the flip**
(`cn_arbno_static`, `cn_defer_const`, `cn_t2_inline_and_recurse`, `cn_udc_declare`). Determinism proven
first: 5 consecutive compiles per arm, one stable md5 each, so this is **not** the known nondeterministic-
rodata noise. On `cn_arbno_static` the armed arm emits an entire additional compile-time-built pattern
function `FN__PAT$0` with the full α/β/γ/ω port set.

**(b) Even where it IS identical, the reading cannot support the claim.** `sno_const_feature()`
(`lower_snobol4.c:961`) is deliberately ONE AUTHORITY for **CN-3 and CN-4b together** — the env killswitch and
the program's own `&USER_DECLARED_CONSTANTS = 0` are two inputs to one fact. That is good design and it is
correct per RULES. But it means flipping `SCRIP_CONST_STATIC` moves **CN-3 as well**, and CN-3 is default-ON
and demonstrably reaches emit. **A byte-identity reading on this killswitch can therefore never establish
that CN-4b/CN-5 specifically are inert** — on a witness with no constant patterns it establishes only that
CN-3 did not fire either. The four identical witnesses are exactly that case.

This is HQ-21's class in subtler clothes: not a wrong baseline, but **an instrument that cannot resolve the
question it is asked.** ⛔ CN-4b/CN-5 are neither confirmed live nor confirmed inert; the evidence on record
does not decide it. Deciding it needs a killswitch that gates CN-4b/CN-5 *without* CN-3, or a direct
emit-site probe. **NOT TAKEN HERE** — adding a second flag to `sno_const_feature` would be the spelled-twice
disease the s148 design correctly refused. Route to whoever owns CN-5's un-parking.

## 5 GUIDANCE g1 IMPLEMENTED (outstanding since s147)

`test_gate_kw_static.sh` now prints the expected verdict per arm: the ARMED banner names the two routed reds
so they are not re-hunted as regressions, and the LEGACY banner states that a low score there is **by design**
(those witnesses encode the TARGET table; the legacy arm's only job is to prove the killswitch still isolates
the feature). Scores unchanged by the edit: armed 10/14, legacy 0/14.

## 6 A METHOD NOTE THIS SEAT OWES ITS OWN RECORD

This seat's first attempt to confirm the `132_…` m4 failure used a **relative** program path after `cd`-ing
away from it and reported a confident `rc=1, size=0` — file-not-found wearing a compile-failure costume, and
it briefly read as corroboration of a real defect. Caught by cross-checking against the sweep, which had the
same program at rc=0 with a stable md5. **The instrument disagreeing with the hand-run is the signal; the
hand-run was wrong.** Same family as everything else in this FINDING: the measurement, not the code.

---

## NEXT SEAT

1. **Disposition HQ-21** — the banner currently halts every incoming seat for a repair that measures green.
   Either HQ re-measures on a clean pair (driver **and** `.so` from the same commit) or the banner is struck.
2. **CN-4b/CN-5 remain undecided** (§4). Do not cite the s148 byte-identity as evidence either way.
3. **CN-6** — the `CLEAR()` un-seals a declared constant defect stands, untouched here; note `NV_EXISTS_fn`
   is the wrong predicate at `keywords.c:355`. Manual (Ch.19 CLEAR, p.215) is explicit and worth quoting to
   the fix: `CLEAR(s)` nulls all user variables and `s` is an **exclusion** list, and CLEAR **does not clear
   protected variables** — so a sealed constant surviving CLEAR is the oracle-shaped behaviour to aim at.
4. **KW-4** (delete the gated bare-name family + `kw_*` statics + the `SCRIP_SEED_NAMES` bridge +
   `bb_match_advance`) is unblocked by the sweeps in §2 — the rung is now swept, not merely gated.
5. `132_pat_fence_eps_recur_shallow` m4 `FN__makeP` linkage gap (§2) needs an owner.
