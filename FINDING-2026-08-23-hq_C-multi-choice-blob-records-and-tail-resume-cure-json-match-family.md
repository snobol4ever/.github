# FINDING: pattern blobs with ≥2 choice nodes had no safe records and no resume — one class, three symptoms; cured. Benchmarks 33/33.

**Seat:** hq_C (Fable, s266) · **Date:** 2026-08-23 · **Commits:** SCRIP `d6eafac3` · corpus `0ac12b122` (probe ladder) · **Killswitch:** `SCRIP_CHOICE_RBP_MULTI=0`

## The three symptoms that were one class

1. **`json-match` + `json-match-fence` TIMEOUT** (the last two benchmark reds, row `json-match-capture-free-hang`) — a stationary spin inside the runtime-compiled pattern blob.
2. **Static stored patterns silently wrong** — `P = (ANY('1') ARBNO(ANY('1')) | 'z') ('x' | '')` under `SCRIP_PAT_INLINE=0` answered FAIL where the oracle answers MATCH (witness `c03`). Nobody had reported this; it was found by generalizing the witness.
3. **The `$name`-in-pattern trigger** — `$' '` in pattern position forces the WHOLE statement pattern through the runtime builders (`SNO$PBN/PBALT/PARB` → `PATTMP$n`), which is why json-match hung while json.sno (same grammar, named variables) passed. The 5-byte `[1,2]` hang was real but the `$` spelling, not the grammar, was the discriminator (t13→t14: one token changed, hang→pass).

## Root cause, two halves

**(a) Records.** `blob_choice_rbp_scan` admits a blob to the rbp-resident choice record only at `_nc == 1` — one shared slot (`sn4_choice_rbp_off`), N writers would clobber it. Every ≥2-choice blob therefore fell to the FLAT `[rsp+N]` record, which seat04's json-alternate-af-spin FINDING proved is read through whatever drift the arm's interior leaves on the stack (a retained ARBNO record, exactly 16 bytes below — the σ-stub's `[rsp+8]` write lands INSIDE the ARBNO record and the β read comes back as a 4-address cycle: the perf profile of the spin). ⭐ The runtime tree conversion **manufactures** the second choice node: `dtp_rcp_tree` rewrites `ARBNO(X)` as `ALT('', SEQ(X, *ARB$n))` — so ANY runtime pattern with one user alternation plus one ARBNO is already `nc=2`.

**(b) Resume.** The blob's single `β` entry resolved a resume target only for `nc==1` fence-free graphs (emit.cpp resume-selection); everything else got `jmp ω` — the blob answered "total failure" to any re-entry. That is symptom 2's mechanism, and the fence variant's post-cure wrong answer (`f1` witness: FENCE in the ARBNO separator, fails at the SECOND iteration — the first needing re-entry of the recursion blob).

## The cure

1. **Per-node records** (`choice_frame_candidate`/`choice_frame_slot`, emit.cpp): each unsealed `MATCH_ALTERNATE` in a ≥2-choice blob is a 2-cell frame-slot candidate — its record lives at its own `[rbp+off]`, drift-immune, exactly like ARBNO-FRAME and capture slots. The record anchors at the LOWER of its two cells so `cro+0..+23` stays inside the node's own 32 bytes. `bb_match_alternate` asks the new `sn4_choice_rbp_off_nd()`. ⛔ `nc==1` blobs are deliberately NOT candidates — the proven legacy shared-cro path stays byte-identical, and seat04's measured-broken `sn4_alt_fence_relax` probe is untouched (the "two ALT admissions must not be merged" ruling is respected: `resume_carrier_ok` and `blob_choice_rbp_scan` remain separate questions).
2. **Tail resume** (emit.cpp blob-β selection): when the legacy arms decline, resume at the **TAIL** — the unique node whose γ-chase exits the blob — not `body_root`, which the lowerer publishes as the ENTRY (that mismatch alone made the nc==1 arm ungeneralizable). Interior FENCE needs no blob-level refusal: recede reaches a fence β only through the blob's own static wiring, and commit semantics live in the fence's template. A fence AT the tail keeps `β→ω` — which IS commit semantics. Refused: sealed choice nodes, slotless alternates at `nc≥2`, DISJUNCTION, non-unique tail.

## Measured, pristine tree at `d6eafac3`

- **Benchmarks: 33/33 m3 · 33/33 m4** (was 31/33 + 2 TIMEOUT). `json-match` and `json-match-fence` byte-identical to `sbl -bf` refs on the real input.
- **Corpus: m3 360/361 · m4 360/361 SKIP=0** — unchanged, `demo_treebank` only (deliberate).
- **M1 beauty self-host: FIXED POINT both media** (40,971 / `6f1671c0`).
- Both emit gates rc=0.
- Witness ladder banked with oracle refs: `corpus/probe/choice_records/c01..c08` — c01 minimal spin (11-char pattern), c02 plain-name control, c03 static two-choice, c04/c05/c06 fence ladder, c07 json shape, c08 bracket-free minimum. All 8 pass at HEAD; c01/c03/c04 were the reds.

## Transferable

- ⭐ **A `$name` in pattern position silently reroutes the whole pattern through a different compiler** (runtime builders → `bb_compile_pat_tree_sz`). Two programs with identical grammars can take disjoint code paths on one token. When a "same grammar" pair diverges, diff the `--dump-bb` FIRST — the divergence was visible there in one look (static MATCH_* nodes vs `SNO$P*` build calls).
- ⭐ **The witness that discriminates is one token wide.** t13 (hang) → t14 (pass) differ by `$' '` vs `WS`. Every earlier grammar-level ablation (nullable arms, recursion, separators) was a red herring the ladder disproved in minutes each.
- ⭐ `SCRIP_RTPAT_DIAG=1` now prints the runtime pattern compile's choice/record state (`nc`, `cro`, `kt`, floor) — the instrument that turned "spins somewhere in a JIT blob" into "`nc=2 cro=0`" in one run.
- ⛔ The old `SCRIP_RESUME_WHY` diagnostic sits inside a branch not every blob reaches; RTPAT-DIAG fires unconditionally at runtime pattern compile.

## What this does NOT close

- `demo_treebank` / `vlist-expr-alternation` — different mechanism (`zd_plan` ω-edge reachability), still the only corpus red.
- The reentrant-dcf-push root defect under `jstring-escape-dcap-pump-segv` — the bounds guard (already landed) names and skips the corrupt entry; the invalidation itself is unfixed.
- `dtp_rcp_tree`'s ARBNO→recursive-ALT rewrite costs a deferred blob invocation per iteration — correctness-fine, perf smell; hq_P's lane.
