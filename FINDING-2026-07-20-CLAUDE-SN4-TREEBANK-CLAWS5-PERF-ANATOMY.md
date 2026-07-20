# FINDING-2026-07-20-CLAUDE-SN4-TREEBANK-CLAWS5-PERF-ANATOMY.md

## Session: s114 (2026-07-20, Claude Sonnet 4.6)
## Status: MEASUREMENT + DESIGN — no code landed

---

## BASELINE (this container, interleaved ×7, medians — supersede s113 prose)

| program | SCRIP m4 | SPITBOL | ratio |
|---|---|---|---|
| claws5 | ~317ms | ~46ms | 6.9× behind |
| treebank | ~482ms | ~176ms | 2.7× behind |

Note: contradicts s113's "treebank 137–148 vs 224–255" in opposite directions.
Both measured fresh on this container. Container memcpy bandwidth:
cold first-touch 1.5–2 GB/s, warm 10 GB/s (measured via coldwarm.c probe).

---

## SPITBOL SOURCE VERDICTS (read sbl.min — do not re-derive)

**o_cnc (9486–9497): SPITBOL always copies. No in-place extend, no at-top check.**
Both operand lengths come from SCBLK descriptors (no strlen ever).
`alocs` = pointer bump. `mvc` = straight copy. Four instructions total.
There is NO SCBLK offset field — sharing/substring-without-copy is structurally
impossible in SPITBOL. Every SUBSTR goes through `sbstr` which allocates and copies.

**SIL/CSNOBOL4 (v311.sil — confirmed via web search of S4D58 v3.11):**
YES — SIL has both descriptor AND specifier. The specifier carries base+offset+length
and designates a substring of an existing string without copying. GETBAL, GETLG,
GETSC etc. operate on specifiers directly. This is exactly as Lon suspected.
Despite this, official SPITBOL beats official CSNOBOL4 3–6× across ALL benchmarks
(string_manip 376 vs 1718ms, string_pattern 389 vs 1869) — copy-everything at
memory bandwidth crushes share-everything with overhead. Sharing is not the crown.

**BUFFER datatype (c3.780/781/784):** SPITBOL ships in-place mutation as a
programmer opt-in (BUFFER type). It does NOT do automatic in-place extend.
The capacity-extend (our proposed fix) is therefore an improvement SPITBOL never
built for ordinary strings. BP-5b makes SCRIP strictly better on accumulator
patterns — SPITBOL cannot follow without programmer code changes.

---

## TREEBANK ROOT CAUSE (callgrind, exact, cg-tb.out at s114 container)

**92% of all Ir = __memcpy_avx_unaligned_erms (str_concat_d inclusive).**
The strlen inside str_concat_d is the ~3% term — real but not the bottleneck.

**What Lon identified is correct: treebank does concat only at the beginning
(slurp) and end (node_repr). The middle is list building.**

Scaling probe (1×→2× input):
- SCRIP: 450→1343ms = ×2.98 → quadratic component ~HALF of total wall (~225ms)
- SPITBOL: 159→285ms = ×1.79 → their quadratic coefficient too small to see at
  this input size (runs at 10GB/s warm pages vs our cold first-touch ~1.5GB/s)

2×-input: SCRIP 1343ms vs SPITBOL 285ms → they scale ×1.8, we scale ×3.0.
After BP-5b fix, we should scale ×2.0 and beat SPITBOL's 285ms outright.

**The non-copy wall (~225ms linear half) decomposes as:**
- `rt_proc_hash_lookup` + `name_save_push` + `call_prologue` + `proc_find` +
  both epilogues ≈ 19% of Ir — DEFINE'd function call tax (list/Push_list/etc)
- `strcmp` + `_var_bucket_find` ≈ 11% — DATA field name lookup (head/tail/gen_type
  compared by string on every access)
- PLT lazy resolution: `do_lookup_x`/`_dl_lookup_symbol_x` ~1.5% — FREE KILL
  (bind-now flag or resolve-once cache)
- rt_sxt_extend 1.35% — BP-5 fires on SOME concats; the ones where it doesn't
  fire are the 92% memcpy mass
- alloc/memset ~9%, emitted pattern blobs ~16%

---

## THREE-STRIKE TREEBANK PLAN

**(1) BP-5b CAPACITY EXTEND — kills the 69% memcpy half.**
Mechanism: when the slow path fires, allocate with headroom (~2× growth, capped).
Extend writes into reserved capacity with NO at-top condition and NO cursor bump.
On capacity exhaustion only: copy once into doubled block, re-arm.
Amortized O(1) per append regardless of intervening allocations (INPUT, recursive
node_repr call, NV_SET of local r) — exactly the treebank shape.
Survival of existing safety: GVA ≤1-slot scan at extend; NV_SET/store-sink token
breaks; gc_collect clears. Alias audit slice required for NV_SET-survives-extend.
After: 1×→2× must scale ×2.0; 2× run must beat SPITBOL 285ms.

**(2) BP-7 SLOT-BASED CALL CONVENTION — kills the 19% call-tax half.**
Already fully designed in the goal file. The list/Push_list calls are exactly the
statically-DEFINE'd proc shape BP-7 targets. Also kills the PLT churn.

**(3) DATA FIELD INDEX FAST PATH — kills the 11% head/tail/gen_type strcmp.**
Resolve field names to integer slot indices at first use (or emit time), not
strcmp on every access. Same one-time-cost discipline as the NV fast-path gates.

These three cover ~90% of what treebank does.

---

## CLAWS5 ROOT CAUSE (confirmed s113 finding, not re-measured)

Quadratic ALT/ARBNO γ-forward ring: blob entered 6,703× but ring executes 22.468M
= Σk iterations. Scaling 29→76→342ms at 1×/2×/4× tokens (sbl linear).
Fix = ZB-ITER-LITE path-compress γ-forward so retained records are retreat data
only; successor jump is O(1) not O(k). After fix: scaling must go linear.
SPAN/BREAK ×4 unroll remains pending (label-collision fix: frozen-cset on L(0)/L(1),
strchr arm on L(2)/L(3)).

---

## NUL / SLEN-AUTH FINDING (Lon raised, confirmed)

SCRIP uses zero-terminated strings throughout. CHAR(0) probe:
  SPITBOL: SIZE=3, REPLACE works, assignment works — NUL is an ordinary character.
  SCRIP: SIZE=2, REPLACE silently drops, third statement missing — NUL terminates.

Root: DESCR.slen is unmaintained ("ADVISORY everywhere" — standing facts block).
Every consumer falls back to strlen, which stops at NUL.
Also: slen overloaded as type tag on DT_N (NAMETRAP=slen==2) — must be preserved.

SLEN-AUTH rung (needed regardless of perf):
Law: for DT_S, slen is the authoritative length. Payloads may carry courtesy NUL
at offset slen for C-interop. No str*() on payload paths; memchr/memcmp/fwrite only.
Completion gate: CHAR(0) family + NUL-in-concat/match/output probe suite green;
grep for strXXX on DT_S payload sites → 0.
This is also a ~3% perf win (kills the strlen fallback in str_concat_d).
No corpus program exercises CHAR(0) today — the 307/0 watermark never caught it.

---

## PROBE CORRECTIONS (do not re-derive the retracted cells)

The F-cell (S = S T where T = DUPL(...)) confirmed by callgrind as 92% memcpy.
Earlier claims "SPITBOL A-cell proves extend" and "sbl ×12 mitigation" were
derived from probes where dash-shell produced 1-char appends, not 64-char.
Corrected A-cell (8k iters, 64-char literal): SCRIP 22ms, sbl 4ms — both flat,
consistent with extend firing (SCRIP) and small-volume copy (sbl).
Cold-page thesis confirmed by bandwidth measurement (1.5 vs 10 GB/s).
