# FINDING — hq_P: bare FENCE0 in a stored-pattern blob now restores rsp to the blob activation floor at commit — the unbounded stack leak of the json family is CURED; citm_catalog.json passes end-to-end for the first time

**Date:** 2026-08-23 · **Seat:** hq_P (`/home/claude_P`) · **Cures:** the defect of `FINDING-2026-08-23-seat04-json-fence0-static-release-cant-see-past-alternation-unbounded-stack-leak.md` (queue row `json-fence0-static-release-leak`, minted hq_C, assigned seat04 — collision note in §5).
**Status:** LANDED, killswitch `SCRIP_FENCE0_DYNAMIC` (default ON; `=0` byte-identical, verified against the checked-in `json.s`). RT_OPT `-O0`, mode m3+m4 (shared codegen), ζ cell-stack, oracle-independent (a crash cure; outputs graded against the same refs as before).

## 1. The mechanism, and why it is NOT the direction the baton endorsed

seat04's suggested fix (endorsed by hq_C) was to admit `IR_MATCH_FENCE0` into `frame_slot_is_candidate`/`blob_frame_bytes` and give the fence a FENCE1-style mark/restore slot. That works, but it perturbs the shared frame-slot registry that `blob_choice_rbp_scan` and every capture/ARBNO slot reads — the exact HARD-CONSTRAINT territory three sessions of `json-alternate-af-spin` warned about.

The landed mechanism needs no slot at all. In **blob scope** (`blob_frame_scope()` — a stored-pattern blob entered by jmp with its own R-4(b) activation), the pattern floor is a **compile-time constant below rbp**: the blob prologue is `push rbp; mov rbp,rsp; sub rsp, blob_frame_bytes()` (emit.cpp:2792), and the blob's own ω-whack (`mov rsp,rbp; pop rbp`) already proves everything below the frame is this activation's disposable state. So an eligible bare FENCE emits at commit:

```
mov rsp, rbp
sub rsp, blob_frame_bytes()      ; restore to the activation floor
```

Same absolute-anchor idiom as MATCH_END's frame_whack — drift-immune by construction, releasing exactly what the fence semantically kills: every left-context backtrack record (ARBNO iteration state, alternation choice records, suspended child defer activations) that success never receded through. `blob_frame_bytes()` is called at fence emission — ONE AUTHORITY with the prologue's carve, so hq_C's `d6eafac3` per-node choice records compose by construction (their bytes are inside the same function's answer).

## 2. Eligibility (conservative, computed per fence at emission)

`fence0_dyn_floor()` (emit.cpp, beside `fence0_release_bytes`): blob scope, cstack port, and the fence's forward γ-chain reaches its terminal without crossing `ALTERNATE / ARBNO / FENCE1 / FENCE0 / MATCH_VALUE / CALL / CALL_VALUE / DISJUNCTION / ABORT`. `MATCH_DEFER` **is** allowed — jkey/jstring end `FENCE (epsilon . *ekey())` and captures ride the R12 arena + rbp frame slots, never pre-fence spine cells; refusing DEFER left the per-string leak in place (measured: 2-of-4 fences dynamic still SIGSEGVs at N=1500 OFF-threshold shapes). The ARBNO/ALTERNATE refusals keep a fence INSIDE a loop body or arm from releasing its enclosing construct's live state — the γ of an ARBNO-body node loops back to the ARBNO head, so the chase refuses those naturally. Statement-scope bare fences are untouched (static path as before): the REPLACE depth model (`g_zd_zpat`, emit.cpp:~3033) subtracts `fence0_release_bytes` per node and never sees blob-resident fences, so no model desynchronizes.

## 3. Measured (merged tree `60e3419e` + this change, pristine)

| arm | witness | result |
|---|---|---|
| `SCRIP_FENCE0_DYNAMIC=0` | `synth_perf224.json` | SIGSEGV rc=139 (the leak, still there — fix is load-bearing) |
| ON (default) | synth_perf 224 / 400 / 800 / 1200 | rc=0 all |
| ON | **`citm_catalog.json` (1,727,204 bytes — the row's DONE-WHEN, never passed before)** | **rc=0, full census, `maxdepth=8`** |
| ON | corpus `test_corpus_snobol4.sh` | m3 360/361 · m4 360/361 · SKIP 0 — fail set identical BY NAME (`demo_treebank` only) |
| ON | hq_C composition witnesses `probe/choice_records/c01..c08` (c04..c06 = FENCE0-inside-multi-choice-blob) | 8/8 PASS |
| ON | gates `emit_no_lang` + `template_medium_invisible` + `board_beauty_m1.sh` | see cursor — run in the landing session |

## 4. The residual, named as its own row: `json-arbno-inloop-stack-accrual`

N≈1500 synthetic records still SIGSEGV on BOTH arms. Different class: **per-iteration state inside ONE long ARBNO loop** — a single array of N records accumulates iteration records/child suspensions for the whole loop, and the array's own trailing fence only runs at the END. Bounded per-element cost × N ⇒ linear stack growth within one array. Cure direction: release-at-ARBNO-commit (an iteration that commits under a fence-bearing grammar could free its predecessor's records), or an in-loop fence placement cure at the grammar level (`fence-jstrbody-cas`'s use-site move is related). citm (243-item max section) fits under the raised ceiling; the row guards the class.

## 5. Process note — the mode collision, recorded honestly

This cure was built under Lon's morning DUO-mode order ("Tag you are it… You will measure. You will cure"). Mid-implementation Lon flipped FLEET-16, and hq_C — unaware hq_P was already curing — minted and assigned the row to seat04 (20:18Z). hq_P doorbelled seat04 (verify-only remainder: re-verify DONE-WHEN, promote `synth_perf224` into corpus as a regression row, merge FINDINGs, close) and hq_C (ack received: mechanism endorsed, composition witnesses named) inside ten minutes. No seat-hours were lost. The general lesson: a mode flip mid-flight makes in-flight HQ work look like lane-crossing; the postoffice record + doorbell is the repair, not abandoning a verified fix.
