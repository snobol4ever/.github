# FINDING 2026-08-30 (ceo, Lon direct) — beauty self-host cured: one unterminated byte (`nl`, sliced from &ALPHABET) broke the whole parse; three length-authority consumers fixed; first beauty-vs-SPITBOL number published

Lon: "Let's fix beauty self host to work. It was working not very long ago." It was — until 2026-08-27. Cure: SCRIP `caffe0d4`. Trees during hunt: witness input `beauty.sno` (corpus, content stable through the demos rename).

## The hunt, each step mechanical
1. **Bisect, not forward-debug.** Dated probes found 08-21 GREEN / 08-28 RED (with fresh objdir per build — the shared-objdir ABI-mix class produced two BUILD-FAIL probes before that discipline). `git bisect run` landed **`89571dd7`** — the slice-captures optimization (capture descriptors point INTO the subject; string_pattern +110%, crossed SPITBOL).
2. **Witness shrink**: full 618-line input → the single line `START` → "Parse Error". One line, no I/O, no replacement in the failing window.
3. **A slice budget** (`SCRIP_CAP_SLICE_MAX=N`: first N mints slice, rest copy; `SCRIP_CAP_SLICE_TRACE=1` names each mint — instrument committed) bisected N: 4 green, 5 red. **Mint #4 = `nl`** — `global.inc`'s `&ALPHABET POS(10) LEN(1) . nl`, a 1-byte slice into the 256-char alphabet, minted once at program init.
4. **The leak**: beauty stores patterns built from `nl` (`BREAK(nl)`, `White`), and `*Parse` deferred evaluation RECOMPILES stored patterns via `dtp_rcp_tree` — which dropped the rcp node's slen when stuffing QLIT/cset tree nodes, so downstream strlen'd the unterminated slice and **BREAK's set became newline plus the entire rest of &ALPHABET**. Every label parse then died: "Parse Error" on beauty's own line 8.

## Fixed (all consumer-side, helper untouched — the length-authority law)
- `dtp_rcp_tree` QLIT/cset arms: terminated, length-honest copies (THE cure; reconstruction-time, never per match step).
- `c_rt_match_replace`: replacement value length now honors slen (a real sibling bug, found en route; not this witness's mechanism).
- `_PAT_SPAN/BREAK/BREAKX/ANY/NOTANY` dispatch wrappers: `VARVAL_fn` → `rt_cstr_d` (they flattened the descriptor before strlen-taking char* builders).
- Two conservative guards, hq_P's to relax behind measurement: `*` deferred arms and thunk-carrying frames never take the slice. string_pattern (no thunks) keeps its +110%; beauty currently gets zero slice benefit — headroom on its number.

## Measured after (floor + the answer to Lon's speed question)
- beauty self-reproduces **byte-for-byte in BOTH modes**; one-line witness clean.
- Floor: corpus m3/m4 1672/0 · both live gates · prolog 5/5 both · icon 14/14 both · snocone 5/5 · rebus 4/4.
- **beauty self-host: 0.18x vs SPITBOL** (wall clock, best of 5×10 runs, outputs byte-verified on both arms first; 21.6 ms vs 3.8 ms per run, clean bench oracle). In the README, dated, with the headroom stated. Rows slice-capture-aliasing-breaks-beauty-selfhost and beauty-selfhost-speed-vs-spitbol closed; hq_P messaged with the relax-behind-measurement handoff.

## Transferable
- **An optimization's hazard analysis is only as complete as its consumer census.** 89571dd7 proved GC, terminators-on-the-poison-board, and the extend-owner — and the poison board was green — but the deferred-eval RECOMPILATION path never ran under poison, and that is exactly where the length died. A property "board-proven" is proven for the paths the board walks.
- **Budgeted enabling of a suspect mechanism is a bisect over DATA, not commits** — `SCRIP_CAP_SLICE_MAX` found one capture out of millions in four runs. Cheap to build, kept for the next one.
- The bisect's two BUILD-FAIL probes were the shared-objdir class wearing a new coat: any historical-build harness must wipe the objdir per step or its verdicts are about stale objects.
