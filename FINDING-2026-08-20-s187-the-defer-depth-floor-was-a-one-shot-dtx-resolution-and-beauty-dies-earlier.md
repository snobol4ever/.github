# FINDING s187 — THE DEFER-DEPTH FLOOR IS A ONE-SHOT DT_X RESOLUTION, AND IT WAS NOT BEAUTY'S FIRST BLOCKER

**Seat2 `/home/claude2`, Claude Opus 5, 2026-08-20. Queue row `defer-depth-floor` (rank 0).**
**SCRIP: fix at `src/runtime/pattern_match.c`, 3 lines + one corrected comment. RT_OPT `-O0`. No codegen file touched; emitted `.s` byte-identical.**

---

## ⭐ THE ROOT CAUSE, IN ONE SENTENCE

**A deferred EXPRESSION (`DT_X`, what `P = *Q` builds via `SNO$MKEXPR`) was resolved exactly ONCE per defer activation; when that one evaluation yielded ANOTHER `DT_X`, the second was stored unresolved and `c_rt_defer_close` `-1`'d it — so a chain of two or more `*`-deferred variables came back NOMATCH in both modes.**

The cap was **explicit, documented, and load-bearing** — not an accident. `pattern_match.c:911`, written at NCB-1c M1 (2026-07-11), states it verbatim:

> *"Round discipline mirrors the old body EXACTLY: one `'*'`-triggered call and at most one DT_X-triggered call (`dtx_used`); a second DT_X result is stored, not re-called, and falls out of close as -1 (it is neither S nor I nor R)."*

⛔ **THE DEFECT IS THE PHRASE "MIRRORS THE OLD BODY EXACTLY."** The round discipline was validated against *SCRIP's previous implementation*, not against the oracle. The very same comment block quotes the manual on the other side of the question — **p.85-86: "the Expression datatype (DT_X) is evaluated only when referenced in a match, and its evaluation MAY ITSELF RUN A MATCH"** — which is precisely the recursion the `dtx_used` flag forbade. A limitation was frozen into a contract by being copied forward.

## ⭐⭐ THE BOUNDARY IS EXACT, AND DEPTH IS THE ONLY VARIABLE — MEASURED, NOT ASSUMED

Ladder minted three ways (plain string terminal · `ARBNO(LEN(1))` · Lon's shape `ARBNO(LEN(1)|LEN(2)|LEN(3))`), depth = number of `DT_X` resolutions the match needs:

| depth | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| string terminal | GREEN | GREEN | **RED** | **RED** | **RED** |
| `ARBNO(LEN(1))` | GREEN | GREEN | **RED** | **RED** | **RED** |
| `ARBNO(LEN(1)\|LEN(2)\|LEN(3))` | GREEN | GREEN | **RED** | **RED** | **RED** |

**The terminal type is irrelevant** — plain literal, ARBNO, ALT all break at the same place and all pass one link earlier. That is what proves the mechanism is the defer road and not any pattern family. The brief's counting is confirmed exactly: one level works, two levels fail.

## ⛔ THE CURE — WALK THE CHAIN, BOUNDED

Two roads reach the same wall and **both** needed it (a fix to either alone leaves half the class red):

- `rt_defer_take` (the shared `c_rt_defer_open` / patv-twin tail) — the `!s->dtx_used` guard became a bounded walk. ⭐ Note the callers at `:1046`/`:1057` set `dtx_used = 1` *before* calling it, so under the old code the guard was **already false on entry** and the second `DT_X` fell straight to `s->val = r`. That is the exact road the 3-line floor witness took.
- `rt_defer_xpat_dtp` (the s178 DEFER-XPAT arm) — single-shot `rt_call_proc_descr`, now looped.

**Why BOUNDED and not `while`:** the oracle **hangs forever** on a self-referential `V = *V` (`sbl -b` had to be killed at 8s, rc=143) — so SPITBOL genuinely walks to exhaustion and a faithful `while` would inherit the hang. `RT_XPAT_CHAIN_MAX 256` walks far past anything real (beauty's deepest is `Expr0 → … → Expr17`, 18 links) and on a cycle **terminates back into the exact pre-s187 answer** — store the `DT_X`, let close `-1` it. Measured: SCRIP returns `nomatch` cleanly in 0s where the oracle spins. ⛔ **No new global:** `RT_XPAT_CHAIN_MAX` is a `#define` (no storage) and `_g` is a loop local.

## ⭐⭐⭐ THE HEADLINE FOR M1 — THE FLOOR WAS REAL, AND BEAUTY DIES BEFORE IT EVER REACHES IT

The brief's premise — *"beauty's grammar is a deep defer chain … DEPTH 2 IS ITS FLOOR. Nothing in beauty's grammar could ever have matched"* — is **TRUE about the grammar and does not move the board.**

`board_beauty_m1.sh --modes m3`, patched: **3/10 green, first red still at 10 lines. UNCHANGED from the s183 first reading.**

The reason is recorded plainly: beauty's first red is the **s183 CLASS A completion SEGV**, and all four of its 1–9 byte witnesses still SIGSEGV (rc=139) on the patched build — `m1_lad_empty` (`"\n"`), `m1_lad_barelabel`, `m1_lad_end`, `m1_lad_comment`. **A one-byte input containing only a newline crashes beauty.** No defer chain is reachable from there; the depth floor sits *behind* a wall beauty never gets past.

⛔ **THE ORIENTING CORRECTION FOR THE NEXT SEAT:** the s183 override sweep (`*Stmt` two levels SEGVs, `*Comment` one level clean) is real evidence and it **did** point at a real defect — this one. But it is evidence of a **second, independent** blocker, not of the first one. `defer-depth-floor` **does not subsume the M1 rows** as the brief expected; it retires one class outright and leaves the class-A completion SEGV as the standing first red. Route class A on its own.

## VERIFICATION — EVERY NUMBER A/B'd, NEVER SINGLE-RUN

Method per RULES: **swap `out/libscrip_rt.so` only**, same tree, one file differing.

**DONE-WHEN witness set (HQ's canonical s183 family, `corpus/probe/passthru/`), both modes:**

| witness | control m3/m4 | patched m3/m4 |
|---|---|---|
| `ptw_min_defer2_floor` | nomatch / nomatch | **match / match** |
| `ptw_min_defer2_pp_L2` | nomatch / nomatch | **match / match** |
| `ptw_min_defer2_pp_L3` | nomatch / nomatch | **match / match** |
| `ptw_min_defer2_arbno` | nomatch / nomatch | **match / match** |
| `ptw_min_defer2_depth9` | nomatch / nomatch | **match / match** |
| `ptw_min_defer2_evalbuilt` | nomatch / nomatch | **match** / Error 22 |
| `ptw_min_defer2_pp_L0` (ctl) | match / match | match / match — **unchanged** |
| `ptw_min_defer2_pp_L1` (ctl) | match / match | match / match — **unchanged** |
| `ptw_min_defer1_arbno_ctl` | match / match | match / match — **unchanged** |

**Corpus board** (`test_corpus_snobol4.sh`), control vs patched: **m3 332/5 · m4 325/11 · SKIP 1 on BOTH arms — fail-set identical BY NAME (`diff` of the two name-lists is empty).** The board never enumerates `probe/`, so a no-op there is the correct result, and it proves no regression.

**Passthru board** (`board_passthru_combo.sh`), control vs patched — the defer-dense board, and the one that moves:

- **m3 134/148 → 139/148 (+5) · m4 121/148 → 125/148 (+4)**
- **movers named, zero regressions in either mode:** `+floor +pp_L3 +defer2_arbno +defer2_depth9 +evalbuilt` (m3); same minus `evalbuilt` (m4).

**Gates:** `test_smoke_snobol4.sh` 7/7 both modes (m4 hard gate) · `test_gate_template_medium_invisible.sh` 0 (ceiling 0) · `test_gate_emit_no_lang.sh` LANG-BLIND OK.

**Killswitches:** `SCRIP_RTSEQ_RESUME=0` — all green, so the defect was never resume-sequencing. `SCRIP_DEFER_XPAT=0` — `pp_L2`/`depth9` return to nomatch, which is that switch **doing its documented job** (it suppresses the DT_X arm wholesale), while **`floor` stays green under it** — the cleanest proof available that the cure landed on *both* roads and not just the XPAT one.

**Codegen untouched:** `.s` for `ptw_min_defer2_floor` is **byte-identical** control vs patched, so the `.s` artifact regens are a provable no-op for this session.

## ⛔ TWO HONEST NON-CLOSURES

1. **`ptw_min_defer2_evalbuilt` m4 is still red, with a NEW and FURTHER first-red.** It advanced from `nomatch` (the defer wall) to `** Error 22 … Undefined function called` — an EVAL-built `DEFINE` that exists in the m3 image but not in the mode-4 compiled binary. That is a **1:1 breach in the m4 direction on a different mechanism**, uncovered *because* the defer wall moved. It is not a regression (the witness was red in both modes before) and it is not this row's class. Worth its own row.
2. **`RT_XPAT_CHAIN_MAX 256` is a ruled bound, not a measured one.** 256 is ~14× beauty's deepest known chain; nothing in the corpus approaches it. A program with a genuinely longer chain would silently get the pre-s187 answer rather than an error. Raising it is free; I did not, because inventing a diagnostic for an unobserved case is how the last cap got frozen in.

## WHAT THE NEXT SEAT SHOULD TAKE FROM THIS

⭐ **THE GENERALISABLE MOVE:** when a round-discipline comment says it *"mirrors the old body exactly,"* that is a statement about **provenance, not correctness** — and the file usually quotes the authority that contradicts it a few lines up. Here the manual citation and the cap that violated it were in the **same comment block**. Read the two against each other before trusting either.
