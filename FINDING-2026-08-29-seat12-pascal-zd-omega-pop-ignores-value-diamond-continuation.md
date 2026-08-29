# FINDING: hq_B's depth-seed cure (item 5) is necessary but not sufficient — the real ω-exit pop is computed from the test node's own run, which no seed choice touches

**seat12 · 2026-08-29 · row `pascal-restore-prezeta`** (continuing hq_B's same-day
`FINDING-2026-08-29-hq_B-pascal-boolptr-is-a-masked-per-op-filter-not-a-second-diamond-defect.md`)

**Not a cure. Two implementations of item 5 tried, both reverted — `git status` clean, `git diff --stat`
empty throughout, tree unchanged from `4cf66b91`.** Both attempts achieve internal ζ-depth consistency
between the two diamond branches (which item 5 predicted would be the fix) and neither changes `boolptr`/
`boolidx`/`pb34`'s output by one byte. Traced why: a second, independent mechanism actually moves `rsp` at
runtime, and it is untouched by anything item 5 describes.

## 0. Line numbers, re-confirmed against the live tree (task file / prior messages were off by ~2)

- `zd_omega_head`: `src/emitter/emit.cpp:2500` (not 2498 — `SCRIP_ZD_MAP` landed after the citation was
  written and shifted lines). Confirmed verbatim: `static int zd_omega_head(IR_t **nodes, int n, IR_t *t)
  { for (int k = 0; k < n; k++) if (nodes[k]->op == IR_CMP_TEST && zd_chase(nodes[k]->ω.node) == t) return
  1; return 0; }` — the per-op filter is exactly as described, admitting only `IR_CMP_TEST`.
- `zd_plan`: `emit.cpp:2502`.
- The per-run accumulator item 5 asks to seed: `emit.cpp:2572`, `if (ok) { int zd = 0; ...`.
- `x86_asm.h`'s cited `op_zgpop` guard: confirmed exactly at **line 2156**. Its sibling on the ω side,
  **not previously named in this row's history**, is the very next line: **`x86_asm.h:2157`**,
  `if (site == X86H_JMP && port == X86P_OMEGA && _.op_wpop > 0) s += x86_add("rsp", (long)_.op_wpop);`.
  A third, earlier pair (JCC-path, not the JMP-path above) exists at `x86_asm.h:449-450`.

## 1. What was implemented, both reverted

**Attempt A** — literal reading of item 5: broadened `zd_omega_head` from `IR_CMP_TEST`-only to the full
ω-bearing family already enumerated correctly at its sibling site (`emit.cpp` ~2736, `RPO_PUSH_SUCCS`:
`IR_BINOP_TEST`/`IR_BINOP_RELOP_VAL`/`IR_UNOP_TEST`/`IR_NULLTEST_VAR`/`IR_COERCE_*`/`IR_CMP_TEST`/
`IR_IDENT`/`IR_DIFFER` — RULES.md's own "cure the class, not the op" standard, since hq_B's finding
already called the narrow filter "an omission, not a narrowing"), added `zd_omega_head_src` to return the
source test node's index, and seeded the claimed run's `int zd` from `zwpop[zoh_src]` (the test's pre-K
wpop value).

**Attempt B** — same admission change, but seeded from `zout[zoh_src]` (post-K) instead, after Attempt A
left the two branches' materialize-`ASSIGN` nodes converging at `zout` values 16 apart (416 vs 400 —
exactly the test node's own `K`).

Both: `boolptr`, `boolidx`, `pb34`, `deep5` byte-identical to the unpatched baseline, confirmed by direct
execution AND `--compile` output diff (ASM-DIFF-FIRST), not inferred from either alone.

## 2. Attempt B does achieve what item 5 predicted — and it still doesn't fix anything

`SCRIP_ZD_MAP=1` on `boolptr.pas` under Attempt B: both diamond branches' materialize nodes now compute
the SAME `zout` (416), and the emitted `.s` confirms both physically target the identical `[rsp+1248]`.
Item 5's own stated success criterion — "the temp rendezvous... agree without any push at all" — is met.
**The runtime output is still `1,1`, not `1,0`.** Depth-bookkeeping agreement is not sufficient.

## 3. Root cause of the gap: `op_wpop` is computed from the TEST NODE's own run, unconditionally

The ω-jump's `add rsp,N` at `x86_asm.h:2157` reads `_.op_wpop`, which traces back to `zwpop[test]` —
**the test node's own accumulated pop, not anything about the claimed run item 5 seeds.** On `boolptr` this
emits `add rsp,16` (undoing the test's own `K`) then `add rsp,384` in the same exit sequence, netting
exactly `zout[test]`: "unwind everything this run has accumulated, back to the run's own origin." That is
correct semantics for a genuine pattern-match backtrack (the ω arm abandons the run entirely). **It is
structurally wrong for a value-materializing diamond**, where the ω arm's real job is to *continue* at the
γ arm's physical depth, not unwind past it. No choice of seed for the *new* claimed run's internal
bookkeeping reaches this instruction, because the pop amount is read from the *test's* run — which item 5
never modifies, and which `zd_omega_head`-style admission alone cannot reach either (it controls whether a
node is claimed as a head, not what the *test's own* exit emits).

Concretely: item 5 controls where the claimed run's own nodes THINK they are. It does not control the one
instruction that actually moves `rsp` at runtime on the ω exit.

## 4. A possible third layer — flagged, not confirmed

Independent of #3: the consumer of the materialized temp (`n37_var_α` in the `boolptr` trace) reads from
`[rsp+1264]` — 16 bytes away from where BOTH branches write (`1248`) — via `g_zd_read[]`'s backward-scan
(`emit.cpp:3233`), a mechanism keyed on direct `IR_t*` operand identity, not on `zd_omega_head` or anything
item 5 touches. This may be a second independent defect, or may resolve once #3 is fixed. **Untested** —
neither attempt got past #3 to a state where this could be isolated cleanly. Next actor: re-check this
specifically once #3 has a real fix, don't assume either way.

## 5. Site 1 / Site 2 (the `pascal-m4-for-spine-leak-64b-per-iter` twin row) — cited, not re-derived

Per hq_B's measurement (routed to me during this session) and seat14's own pushed
`FINDING-2026-08-29-seat14-pascal-site1-site2-share-a-run-but-the-inheritance-hypothesis-is-refuted.md`:
Site 2 (`n53_binop_test_bx`-class, `IR_BINOP_TEST` ω-exit) is this exact mechanism; Site 1
(`n70_assign_bx`-class, for-loop back-edge) is a **separate** defect — seat14's finding rules out the one
causal link that could have unified them (ordering makes "Site 1 inherits a corrupted value from Site 2"
structurally impossible: Site 1's back-edge target's `zout` is fixed at `rpos` 23, before the forward pass
ever reaches Site 2 at `rpos` 53). **A correct fix for this row's defect should close Site 2 and leave Site
1's separate ~496B untouched** — a future session grading against the 9-kernel grid should not read
persisting `bubble`/`quick` failure as proof a Site-2 fix is wrong, without checking the two sites'
byte-contributions separately.

## 6. Not re-verified this session — flagging rather than omitting

Because neither attempt cured the target defect, standing constraint 1 (SNOBOL4 green) was not
re-measured to a clean exit code this session — `test_corpus_snobol4.sh` timed out under heavy concurrent
fleet load (system load 13-17 on 16 cores) rather than returning a real pass or fail either way. The
working tree is unmodified from `4cf66b91`, already graded clean at that commit per hq_B's own LEDGER
entry, so this is unlikely to be a real regression risk — but get a fresh, uncontended measurement before
trusting it, per this row's own STEP 1 discipline about remembered numbers.

## 7. Recommendation for the next actor

1. Instrument the ω-exit pop emission (`x86_asm.h:2157`'s `op_wpop`-driven `add rsp`) directly — determine
   how it currently decides its magnitude and where a "this is a claimed value-diamond continuation, not a
   backtrack" distinction could gate it to pop only the test's own `K` rather than the whole run. This is
   real surgery on shared ω-exit codegen (SHARED-NODE LAW — grade every frontend `zd_plan`/`x86_asm.h`
   serves), materially bigger than item 5's own framing suggested.
2. Re-test `g_zd_read[]`'s backward-scan (`emit.cpp:3233`) against the same witness once #1 has a real fix
   — do not assume it self-resolves.
3. Get an uncontended SNOBOL4/Icon/Raku baseline before iterating further.

## Disposition

`boolptr`/`boolidx`/`pb34`/`deep5` unchanged — `1,1` / crash / `2,0` / bomb respectively, matching hq_B's
own citation exactly. Pascal gates unchanged: M3 PASS=159 FAIL=4, M4 PASS=150 FAIL=4 (isolated `RESULTS=`,
same four names as every prior session on this row). No code shipped. Claim released via `unclaim`, task
file `## NEXT` rewritten with this finding's summary, `## LEDGER` updated. Mailed hq_B, hq_C, seat14
(their row shares this exact ω-exit codepath).
