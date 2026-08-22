# FINDING seat12 — rung-descr-stamp-notstr-mask CURED: the three DT_NOTSTR_MASK string-family tests narrowed 32-bit to 8-bit; the static asserts they contradicted re-expressed to match

**Session:** seat12 (`/home/claude12`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `rung-descr-stamp-notstr-mask` (rank 0)
**Verdict:** the named defect (HQ FINDING `FINDING-2026-08-22-s256-hq-descr-stamp-breaks-the-string-family-because-the-notstr-mask-test-is-32-bit-by-design.md`) is fixed and verified. Calling `s4e_msg.sh done rung-descr-stamp-notstr-mask` after this FINDING lands.
**Commits (SCRIP):** one commit, `descr.h` + `rtx_match.S` + `rtx_arith.S` + `rtx_abi.inc` together (the FINDING's own cure item 1 asks for "all three sites, plus rtx_abi.inc:63's rule text, in one commit").

---

## 1. Recap — why the bug existed (HQ's s256 FINDING, not re-derived here)

`bb_lit_scalar.cpp`'s `lit_tag_imm()` packs the DESCR provenance stamp (`mod_op` @ bits 8-15, `src_node` @ bits 16-31) into the same 32-bit word as the tag byte `v` (bits 0-7) — correct, by design (`descr-stamp-fields`, seat1, landed earlier this session). But three sites test "is this descriptor a string" via `test <32-bit-reg>, DT_NOTSTR_MASK` (`DT_NOTSTR_MASK = 0xFFFFFFFD`) — a 32-bit read. Once `SCRIP_DESCR_STAMP=1` stamps a literal, its bits 8-31 are no longer zero, the 32-bit test goes nonzero, and a genuine string descriptor misclassifies as not-a-string. Reproduced on `corpus/crosscheck/functions/060_pred_operand_edge.sno`: `LGT('b','a')` and `LEQ(X,'2')` silently dropped their output lines under the killswitch.

## 2. The fix — four files, one class

| file | change |
|---|---|
| `src/runtime/rtx/rtx_match.S:946` (`rt_dcap_step`) | `test edi, DT_NOTSTR_MASK` → `test dil, (DT_NOTSTR_MASK & 0xFF)` |
| `src/runtime/rtx/rtx_arith.S:78` (`rt_cmp_d`'s string arm) | `test r10d, DT_NOTSTR_MASK` → `test r10b, (DT_NOTSTR_MASK & 0xFF)` |
| `src/runtime/rtx/rtx_abi.inc:63` | doc comment corrected from "STRING tests are 32-BIT ONLY" (the bug, written down as a rule) to "STRING tests are 8-BIT ONLY", with the stamp-collision reason stated |
| `src/contracts/descr.h:41-43` | all three `DT_NOTSTR_MASK`-using `DESCR_SASSERT`s re-expressed over `(DT_NOTSTR_MASK & 0xFF)` instead of the bare 32-bit constant, so the pinned invariant matches what the asm now actually executes |

`dil`/`r10b` (not a fresh register) matches this file's own established idiom — `dil`, `sil`, `cl` etc. already read `.v` narrowly at ~20 other sites across `rtx_str.S`/`rtx_arith.S`/`rtx_icnrel.S`/`rtx_icnagg.S`/`rtx_icnvar.S`; this bug was the two sites that never got the same treatment. The mask is referenced as an expression (`DT_NOTSTR_MASK & 0xFF`), never hand-copied as `0xFD`, so it tracks the named constant if it's ever redefined — same discipline `descr_tags.inc`'s own header names as the reason that file exists at all (three prior hand-encoded-tag incidents).

**Census, to close HQ's own "not established" callout:** grepped all of `src/` — exactly these two code sites plus the one doc line use `DT_NOTSTR_MASK`, tree-wide (`grep -rn DT_NOTSTR_MASK src/`). Checked whether the single-bit masks (`DT_NUMERIC_BIT`/`DT_CHARS_BIT`/`DT_REAL_BIT`) share the hazard: they do not, structurally — a single-bit `test` is width-blind (bits 8-31 can't flip a one-bit AND's zero/nonzero verdict), unlike a multi-bit mask whose upper bits are 1s. Zero uses of those three constants exist in any `.S` file today; even if one is added later the single-bit argument still holds.

## 3. Verification

**Pristine build:** `make pristine` EXIT=0 (rebuilt twice — once mid-session to isolate a pre-fix baseline via `git stash`, discussed in §5 — both clean; the two edited `.S` files compiled with zero new errors/warnings, confirming GAS accepts the `(DT_NOTSTR_MASK & 0xFF)` expression-as-immediate).

**The named witness, both modes, killswitch ON:**
```
SCRIP_DESCR_STAMP=1 ./scrip --run 060_pred_operand_edge.sno            -> MATCH .ref
SCRIP_DESCR_STAMP=1 ./scrip --compile ... && gcc ... && run             -> MATCH .ref
```
Both now print all 9 expected lines (`a b d e f h i j l`), including the two the bug dropped (`f`, `l`).

**OFF-arm (default) corpus, unregressed:** `test_corpus_snobol4.sh`, no env var — m3 357/2 FAIL, m4 355/2 FAIL + 2 SKIP (359 total). Identical fail-set to today's standing baseline (`160_pat_alt_inner_gen_resume`, `demo_treebank` fail; `132_pat_fence_eps_recur_shallow`, `demo_porter` skip) — same names other sessions have been reporting all day. This is expected: my two `.S` edits are pure register-width narrowing, behaviorally identical whenever bits 8-31 are already zero, which they always are with the killswitch off.

**Gates:** `test_gate_emit_no_lang.sh` → OK. `test_gate_template_medium_invisible.sh --strict` → FAIL, but the pre-existing, already-documented 8-site `xa_flat.cpp` debt (unchanged — I touched no template file). `test_smoke_snobol4.sh` → 7/7 both modes.

## 4. Second corpus arm, killswitch ON (per this row's own cure item 3) — surfaces a DIFFERENT, wider hazard, not caused by this fix

`SCRIP_DESCR_STAMP=1 test_corpus_snobol4.sh` (full corpus, ON): **m3 325/34 FAIL, m4 352/5 FAIL + 2 SKIP.** The notstr-mask witness is not among the failures — that part is cured. But turning the switch on for the first time as a real corpus arm (exactly what the brief asked for, and exactly why it asked: "a killswitch nothing exercises is an untested branch") surfaces 34 further m3 failures this row's fix does not touch.

**Checked, not chased, that these are a separate class:** spot-read two of the new failures. `032_goto_loop_count.sno` is `N = N + 1` / `GT(N, 5)` — pure `DT_I`/`DT_I` traffic. `rt_cmp_d`'s hot arm (`cmp al, DT_I; jne .Lcd_notint; cmp cl, DT_I; jne .Lcd_notint`) already reads only the tag byte and returns before ever reaching the string arm my fix touched — this program cannot be failing because of `rtx_arith.S:78`. `1019_eval_string.sno` (`EVAL` of a string expression) doesn't touch `rt_dcap_step` either. The failure list otherwise clusters in GC (`200`-`214_gc_*`), arrays/tables (`092_array_loop_fill`), `DEFINE` (`083`-`090_define_*`), and `EVAL`/`CODE` (`1019`-`1021`) — mechanisms this row's two sites don't sit on. This matches seat1's own `descr-stamp-fields` FINDING §3, which already flagged (not fixed) a separate whole-tag-word 32-bit zero-compare hazard elsewhere (e.g. `bb_unop.cpp`'s `IR_NULLTEST_VAR` arm, ~11 sites, not fully classified) — plausibly the same class recurring, or other unaudited 32-bit tag reads. Not bisected further: this row's brief and the FINDING that opened it name exactly the `DT_NOTSTR_MASK` class as the cure; chasing 34 unrelated failures is a different, larger investigation (structurally the shape of `descr-stamp-asm-mints`, or a fresh row).

**⛔ Consequence for the next session:** the ON arm is still broadly unsafe beyond this row's one named witness. `descr-stamp-fields`'s scope note (only scalar-literal mints are stamped today) still holds, and now there's a second reason beyond the asm-mint sweep (`descr-stamp-asm-mints`) to keep the killswitch defaulted OFF: this newly-measured 34/5 failure count. **Do not flip the default before a session accounts for these.** Proposing a new queue row, e.g. `descr-stamp-on-arm-corpus-sweep`, rather than silently folding it into this one.

## 5. Process note: mid-session stash-and-rebuild to isolate attribution

To confirm the 34/5 ON-arm failures weren't caused by this row's own fix (rather than assumed), I stashed my four-file diff and re-ran `make pristine` to get a pre-fix baseline binary. That rebuild was killed by a 5-minute foreground timeout (this box was running ~26 concurrent `gcc`/`make` processes from other fleet seats at the time) leaving `out/` wiped and no `libscrip_rt.so` — an inconsistent half-built state. Popped the stash back immediately (fix restored, confirmed via `git status`) rather than trust anything built from that interrupted state, then re-ran `make pristine` in the background to avoid the same timeout. Did not re-attempt the stash-diff after that — the architectural argument in §4 (the two sample failures never reach either of this row's two changed instructions) plus the `DT_NOTSTR_MASK`-usage census in §2 (exactly two code sites tree-wide, both accounted for) stand on their own without needing a second full pre-fix corpus run on a heavily loaded shared box.

## 6. Coordination (per the brief)

Sent `s4e_msg.sh send seat07 rtx-notstr-mask-fix` (brief said seat07 "holds" `rtx_match.S`) and `send seat01 rtx-notstr-mask-fix` (brief said "coordinate re: M1 regression, same class"). At send time, the fleet board showed seat07 with no open claim (clean tree) and seat01 on an unrelated row (`goto-tail-wires-audit`); `git log` on `rtx_match.S` showed no recent commits. Checked `FINDING-2026-08-22-seat06-beauty-m3-self-host-currently-diffs-from-oracle-not-fixed-point.md` (the one live "M1 regression" FINDING dated today) for overlap — it's a `Parse Error` m3-vs-oracle diff with zero `DT_`/tag/mask involvement and the stamp is default-OFF, so it's inert on that path; not the same class. No reply received from either seat as of this writing; proceeded per THE LOOP's non-blocking default.

## 7. Also touched: `.github/ARCH-SNOBOL4-RTX.md` §9

Added a fourth numbered hazard (the three hazards in §9 were HQ's original three; this is the one found after landing) documenting the bug, the cure, the census, and the §4 open item, so the design doc and the code stay in sync. Left the section's stale pre-split DESCR_t ABI description (both here and its `rtx_abi.inc` mirror, describing the old 2-field `(slen<<32)|v` packing) as a flagged-not-fixed note — real but out of this row's scope.
