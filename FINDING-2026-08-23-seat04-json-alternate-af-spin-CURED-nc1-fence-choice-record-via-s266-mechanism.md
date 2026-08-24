# FINDING seat04 — json-alternate-af-spin: CURED. `n241_match_alternate` (jarray/jobject's own choice point) is now RBP-resident, drift-immune, by extending the s266 per-node choice-record mechanism to the `nc==1`-with-FENCE gap it deliberately left open. SCRIP `eca52780`, default ON, full ladder green.

**Session:** 2026-08-23 seat04, THE LOOP queue row `json-alternate-af-spin` (rank 0). **SESSION 5 on this row** — resuming seat04's own unfinished claim (picker: "RESUME json-alternate-af-spin (yours, unfinished)").
**Status:** ROOT CAUSE (sessions 1-3) → LATENT-not-cured re-confirmation (session 4) → **CURED (this session)**. Claim closes here.

---

## 1. Starting state this session

Sessions 1-4 (`FINDING-2026-08-22-seat04-json-alternate-af-spin-root-cause-flat-choice-record-rsp-drift.md`) had: root-caused the bug to the byte (§§1-9: `n241_match_alternate`'s FLAT-mode `[rsp+N]` choice record drifts ~1,168-1,232 bytes across an ARBNO re-entry, because `jvalue`'s own 7-arm alternation legitimately leaves backtrack state on the shared stack after a deferred `*jelement` commits); tried the obvious cure (relax `blob_choice_rbp_scan`'s `_fn`/FENCE-presence conjunct behind `SCRIP_CHOICE_RBP_FENCE`) and **measured it broken** — cures the hang, but `[1,2]` answers `NOMATCH` where the oracle says `MATCH` (§12 of that FINDING), root-caused (not fully proven) to ARBNO's own interior back-out edge composing badly with the *legacy* shared, blob-frame-top-anchored record. Session 4 re-confirmed the drift is still live at HEAD (gdb, `[rbp+...]` unchanged... correction, `[rsp+...]` unchanged) and left the row OPEN, LATENT, blocked at the time by an unrelated third bug (FENCE0 stack leak, since fixed separately).

This session pulled fresh and found the ground had shifted again: `SCRIP 69fb4b1a` (hq_C, s266, "Multi-choice pattern blobs: per-node rbp choice records + fence-tolerant tail resume") had landed a **new, general** per-node RBP choice-record mechanism (`choice_frame_candidate`/`choice_frame_slot`, `emit.cpp:2251`) — its own comment names this row and seat04's FINDING as the motivating case. **Did not take this at face value.** Read `choice_frame_candidate` in full: it admits a `MATCH_ALTERNATE` node only when `_nc >= 2` (two-or-more choice points in the blob) — `jarray`/`jobject`'s own alternation is `_nc == 1` (one choice point, `_fn` from the sibling FENCE elsewhere in the blob), which the s266 comment itself flags as *deliberately excluded* ("nc==1 blobs are deliberately NOT candidates — they keep the legacy shared-cro path byte-identical"). **The legacy path (`blob_choice_rbp_scan`) is untouched by s266 and still refuses `jarray`/`jobject` on `_fn`.** Confirmed structurally, not just by reading: rebuilt pristine at `69fb4b1a`+ (before this session's own edit), recreated the exact `jbig_comma.sno` witness from the original FINDING's own recipe (`json.sno` lines 1-257 verbatim + a 4-line driver), compiled `--compile`, and `n241_match_alternate_α` still reads `sub rsp,32; mov dword ptr [rsp+0],r14d; ...` — byte-for-byte the FLAT shape the original FINDING documented. **This row's own mechanism was still live and unfixed by s266.**

## 2. The cure: extend the *new* mechanism, not the *old* one

`choice_frame_candidate` never inspects `_fn` at all — it only refuses on `_nc<2`. That is the whole reason session 3's `SCRIP_CHOICE_RBP_FENCE` probe (relaxing the *legacy* `blob_choice_rbp_scan`'s `_fn` conjunct) produced a wrong answer: the legacy mechanism gives the blob **one shared slot anchored at the frame's own top** (`sn4_choice_rbp_off()` = `-(blob_frame_bytes())`), with no index of its own, and ARBNO's interior back-out edge (`op_arbno_body_actframe`, `bb_match_arbno.cpp`) apparently was never designed/verified against that shape combined with a FENCE-adjacent single choice point. The s266 mechanism gives each admitted alternation its **own indexed** `[rbp+off]` slot (`choice_frame_slot` → `frame_slot_scan`/`frame_slot_off`, the *same* allocator ARBNO-FRAME and capture slots already use safely under ARBNO re-entry) — and hq_C's own verification for the `nc>=2` case already exercised this shape colliding with ARBNO bodies, because `dtp_rcp_tree`'s runtime-tree `ARBNO(X)` → `ALT('', SEQ(X, *ARB$n))` rewrite manufactures exactly an ARBNO-adjacent multi-choice blob as its *normal* case.

**Change** (`src/emitter/emit.cpp`, `choice_frame_candidate`, plus one new function `sn4_choice_rbp_single_fence`): admit `_nc == 1 && _fn` blobs into the *same* per-node mechanism, gated by a new killswitch `SCRIP_CHOICE_RBP_SFENCE` — **additive, not a relaxation of the `_nc<2` refusal**: `_nc==1`-without-fence blobs are completely unaffected (still the untouched, proven legacy path); `_nc>=2` blobs are completely unaffected (still exactly hq_C's own s266 code path, unmodified). This respects the row's own HARD CONSTRAINT (task baton item 3: "the two ALT admissions [`blob_choice_rbp_scan` and `resume_carrier_ok`] answer DIFFERENT QUESTIONS and MUST NOT BE MERGED") by construction — neither of those two functions was touched; a *third*, independent admission function gained one new, narrowly-gated case.

```c
static int choice_frame_candidate(const IR_t * nd) {
    ...
    { int _nc = 0, _lf = 0, _fn = 0; sn4_blob_choice_scan(&_nc, &_lf, &_fn);
      if (_nc >= 2) return 1;                                          // s266, unchanged
      if (_nc == 1 && _fn && sn4_choice_rbp_single_fence()) return 1;  // NEW, this session
      return 0; }
}
```

## 3. Verified — the full ladder, both arms of the killswitch, pristine

**OFF (`SCRIP_CHOICE_RBP_SFENCE=0`) is byte-identical to pre-change**, checked two ways: direct `--compile` `.s` diff of the `jbig_comma.sno` witness against a pristine pre-edit baseline (`diff -q` clean), and the full corpus sweep (below) landing on the exact pre-existing PASS/FAIL set.

**ON is the new default**, flipped this session after the ladder below came back clean (matching this project's own precedent for `SCRIP_FENCE0_DYNAMIC`/`SCRIP_CHOICE_RBP_MULTI`: land the new mechanism, verify same-session, ship default ON):

| check | result |
|---|---|
| Structural: `n241_match_alternate_α` addressing | was `sub rsp,32` / `[rsp+0/8/16]` (FLAT) → now `[rbp-80]`/`[rbp-64]` (RBP-resident), on the **real** `corpus/programs/snobol4/demo/json.sno`, not just the witness |
| 13 hand-built witnesses vs `sbl -bf` oracle (m3) | `[1]` `[1,2]` `[[9]]` `[1,2,3,4,5]` `{"a":1,"b":2}` `{"a":[1,2],"b":{"c":3}}` `[{"a":1},2]` `[]` `{}` — all **MATCH**, oracle-identical; `[1,2,]` `[,1,2]` `[1,,2]` `{"a":1,"b":2,}` (backtrack-forcing malformed inputs, deliberately chosen to force a genuine recede through `n241`'s ports, the exact path the bug lived in) — all **NOMATCH**, oracle-identical |
| Same 5 key witnesses, m4 (`--compile`+gcc+link) | identical to m3, confirming m3≡m4 |
| Row's own DONE-WHEN, real `citm_catalog.json` (1,727,204 bytes), m3 **and** m4 | rc=0 both; structurally identical to the pre-change baseline (same object/array/string/int/real/bool/null counts, `maxdepth=8`) — only the `match_ms=` line differs, as expected |
| Broad corpus (`test_corpus_snobol4.sh`), pristine, OFF then ON | **identical both arms**: m3 363/364, m4 363/364 SKIP=0, sole fail `demo_treebank` both modes (pre-existing, unrelated — `zd_plan` ω-edge reachability per hq_C's own multi-choice FINDING) |
| Smoke (`test_smoke_snobol4.sh`), pristine, OFF then ON | identical both arms: 7/7 both modes |
| M1 self-host fixed point (`board_beauty_m1.sh --modes both`), pristine, OFF then ON | identical both arms: 10/10 rungs green both modes, ⭐M1-FIXED-POINT held |
| `json-match.sno` / `json-match-fence.sno` (benchmarks tree) vs `.ref` | both OFF and ON match `.ref`; OFF-vs-ON output **byte-identical** (their own `.s` changed internally — `json-match-fence.s` picked up the same RBP-mode for its own `nc==1`-with-fence alternation — but program behavior is unchanged, exactly the expected shape for a pure internal-addressing improvement) |

All builds `make pristine` (HQ-27), `RT_OPT=-O0` throughout (no `-O2`, per the s262/s267 fact rule).

## 4. `.s` artifact regen (codegen touched, per CLAUDE.md)

Ran all six in order. Changed, corpus-committed: demo regen (`83354667`) — `json.s`, `json-match-fence.s`, plus `claws5.s`/`claws5-match-fence.s`/`treebank.s`/`treebank-match-fence.s` (same `nc==1`-with-fence shape, confirming the fix is general, not JSON-specific — `demo_treebank`'s own PASS/FAIL verdict is unchanged, still red for its pre-existing unrelated reason); crosscheck regen (`19d55799`) — 7 files, all named `pat_recursive_grammar`/`pat_fence_eps_recur_*`/`pat_balanced_parens_*`/`pat_balanced_mixed`, exactly the recursive-grammar-plus-FENCE shape this fix targets. Benchmark, feature, programs, prolog-bench regens: zero changes (feature/programs surfaced pre-existing, unrelated EMIT-FAILs in Icon/Prolog/Rebus/Snocone gaps and the long-standing `coverage_sno_nodes.sno` pattern-subset gap — none touch `MATCH_ALTERNATE`/choice records, confirmed by direct recompile + git blame showing the `.s` predates this session).

## 5. Disposition

**Row CURED, not merely latent-masked.** Unlike the ARRAY(n) commit (`3a644af1`) that made the ORIGINAL hang symptom stop reproducing by coincidentally perturbing allocation timing while leaving the drift mechanism intact (session 4's own finding), this fix removes the drift itself: `n241`'s choice record no longer lives anywhere `rsp` can carry it away from. Structurally verified (RBP addressing, confirmed on the real corpus file) and behaviorally verified (oracle-exact on 13 witnesses including the specific backtrack-forcing shapes that previously either hung or, under the one prior fix attempt, silently mismatched).

Task baton `## NEXT` rewritten; `s4e_msg.sh done json-alternate-af-spin` follows this FINDING. GOAL-SNOBOL4-100.md LIVE CURSOR updated to match.
