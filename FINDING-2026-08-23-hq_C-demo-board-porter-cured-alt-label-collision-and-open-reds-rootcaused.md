# FINDING 2026-08-23 hq_C — full demo board measured; porter m4 CURED (alt label collision at N==21); the three open reds root-caused

**Context:** Lon's order this session: *"Get ALL demos working properly so Performance-HQ can do its work."* Instrument: every `corpus/programs/snobol4/demo/*.sno` graded against the live correctness oracle (`/home/resources/x64/bin/sbl -bf -d512m -i64m -s256m`, `-CASE 0` + `&TRIM = 0` temp-prepend, run from the demo dir), both media, timing lines filtered identically on all arms. SCRIP `b7d88465` (cure commit), corpus `6d9782a47`.

## THE BOARD (23 programs × oracle/m3/m4)

**19 of 23 TRI-MATCH byte-for-byte**, including porter (163 KB output), roman, both full calculators, all claws5 arms, all treebank-match arms, treebank-alloc.

| demo | m3 | m4 | verdict |
|---|---|---|---|
| porter | MATCH | **MATCH — CURED this session** (was SKIP(compile)) | ✅ |
| treebank | DIFF | DIFF | ⛔ Error 235 — vlist-expr-alternation, root-caused deeper below |
| json, json-match | TIMEOUT | TIMEOUT | ⛔ ARBNO-in-alternation, NEW minimal witness below |
| json-match-fence | DIFF ("Pattern match failed") | DIFF | ⛔ same family, fence arm |
| all 19 others | MATCH | MATCH | ✅ |

Corpus gate after cure: **m3 357/359 · m4 356/359 + 1 SKIP** (m4 was 355 + 2 SKIP — `demo_porter` SKIP is gone). Both live gates green. Baseline supersedes the s256 numbers in GOAL-HQ-COMPLETE § board.

## CURE 1 — porter m4: internal-label range collision at exactly N==21 alternates

`bb_match_alternate.cpp` mints TWO label series inside one box: entry stubs `L(21..19+N)`, sigma stubs `L(40..39+N)`. At **N==21** (porter's suffix-rule alternation) the first series reaches L(41)… no — L(20+j) reaches **L(40)** at j=20, colliding with sigma's base. `as` refuses the duplicate `.Lx865_40` (porter.s:5665). TEXT medium catches it loudly; **BINARY (m3) resolves the same id to one address silently** — m3's porter pass was not evidence of health. Cure: `alt_sigma_base(N) = max(40, 20+N)`. Same class found latent in `bb_call_proc_staged.cpp`: `stage_arg_inline` L(20+2i) hits `bcps_nret_consult`'s L(29) at i==4 (5+ staged args); moved to its own range (SAI_L0=200). **Class rule worth a gate:** two independent `L(base+k)` series in one box are a collision waiting for the N that joins them.

## ROOT-CAUSE 2 — json family: `(prefix ARBNO(x) | alt) suffix` breaks the box after the alternation

New minimal witness, **independent of JSON entirely**:

```
pat = ('a' ARBNO('b') | 'z') RPOS(0)     'abb' ? pat    → m3/m4 SIGSEGV rc=139
pat = ('a' ARBNO('b') | 'z')             'abb' ? pat    → MATCH (no suffix: fine)
pat = ('a' ARBNO('b')) RPOS(0)           'abb' ? pat    → MATCH (no alternation: fine)
```

Crash bt: garbage rip `0x7fff00000000` reached from `n31_match_alternate_s1` → the sigma resume slot `[rsp+8]` read by `alternate_β` holds junk after the ARBNO arm ran — the ARBNO inside arm 1 moved rsp so the ALT-FLAT own-carved 32-byte record is no longer at the depth the σ/β stubs address. Same defect family as `json-alternate-af-spin` (seat04's FLAT-mode choice-record rsp drift) — this witness is smaller than the JSON one and segfaults instead of spinning, so it brackets the same wound from a new side. On richer inputs (2+ members then an array/third member) it degrades to the observed infinite retry instead of the crash. `demo/json*.{sno}` are all this one class.

## ROOT-CAUSE 3 — treebank: Error 235 "subscripted operand is not table or array"

`ListInsert4`: `a = ARRAY('0:' (IDENT(a(x)) 0, size * 2 - 1))` — the **expression value list** `(e1, e2)` (row `vlist-expr-alternation`, deliberate red). Deeper than previously recorded: an experimental lowering exists (`SCRIP_VLIST_ALT=1`, arm-chained via a temp), and it is **not wrong in the lowering — it is blocked in the emitter**: `zd_plan()` claims ζ-depth only along **linear γ runs from statement heads**; arm 2 of a vlist is reachable only through an ω edge, is never claimed (`zd_on=0`), and its boxes address cells at stale static offsets — **silent wrong values** under cell-stack (default), correct under frame-rsp/cell-heap. Measured: `'p' (IDENT(y) 5, 9)` → `9` instead of `p9`. IR_BOUND/IR_UNMARK spine-restore was tried and is the **wrong tool** — the β chain already unwinds; the missing piece is a second claimed entry mid-expression in zd_plan. Flag stays OFF; mechanism pinned in the TT_VLIST comment (lower_snobol4.c).

## For hq_P

Every emitted-code change this session is porter-shaped only: the sigma-base change alters .s only for boxes with ≥21 alternates or 5+ inline-staged args. Demo .s regen: **zero diffs** except porter's own tree; benchmark kernels untouched. The 19 tri-matching demos are safe to benchmark now; json*/treebank are NOT (broken programs time gloriously).
