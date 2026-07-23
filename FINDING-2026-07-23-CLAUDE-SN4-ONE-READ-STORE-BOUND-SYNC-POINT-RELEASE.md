# FINDING 2026-07-23 (Claude) — ONE-READ LANDED; MATCH PHASE IS STORE-BOUND, NOT INSTRUCTION-BOUND; SYNC-POINT ζ RELEASE RULED

## PART 1 — LANDED: one-read raw-mode input for the *-match trio (SCRIP `db25be45`, corpus `aabd12aa`)

SPITBOL file-processing options `-f` (fd attach) and `-r`/`-q` (raw record length, manual pp.226-228) implemented on
the no-filename `INPUT()` form in `core/core.c`; `input_read()` raw branch = exact-N-or-EOF, EOL in-string, no trim,
fail on 0 bytes. Both modes route through `input_read`, so m3/m4 got it for free. The three `*-match.sno` programs
(claws5, treebank, json) replaced their slurp loops with `INPUT(.INPUT, 9, '[-f0 -r1000000]')` + one `src = INPUT`;
claws5-match's per-item `' '` widened to `SPAN(' ' CHAR(10))` (raw text keeps newlines; data lines end space+NL).
Refs regenerated from sbl: claws5 66757, treebank 100155 (byte-unchanged — file ends with NL), json 631514.
NOTE: per-variable INPUT() association (`INPUT(.x, ch, 'file')`) registers a channel but emitted code reads `x`
through its baked GVA slot, so it silently no-ops — pre-existing, only the INPUT-name form actually works. Latent.

**Both engines collapsed** (the slurp was quadratic churn in BOTH): json-match sbl 856→7ms, SCRIP m3 2714→46ms.
Warm medians this container (RT_OPT=-O0 throughout, no -O2 anywhere per O2-DIRECTED-ONLY):
claws5-match sbl 1 / m3 8 · treebank-match sbl 3 / m3 22 · json-match sbl 7 / m3 46 (ms). Tri-identity sbl≡m3≡m4
all three. Gates: sno smokes 7/7×2 · icon 14/14×2 · prolog 5/5×2 (core.c multi-frontend) · crosscheck m3 302/8 ·
m4 302/6 · DIVERGE=0, fail-set name-identical to s131. Data files corpus-wide verified LF-only (Lon directive) —
zero CR found, nothing to fix.

## PART 2 — MEASURED: the s108 story is slurp-era; the pure match phase is STORE-BOUND

callgrind/cachegrind on the rewritten json-match m4 (632KB twitter.json):
- **SCRIP 15.6M Ir vs SPITBOL 17.2M Ir — SCRIP executes FEWER instructions** yet takes ~35ms match vs ~5ms ⇒ IPC ≈ 0.14 vs ≈ 1.0.
- I1 miss 0.03% (20KB .text) — I-cache exonerated. Branch mispredict 1.0% — exonerated.
- **D refs 9.9M WRITES vs 1.7M reads (63% of all instructions are stores); LL misses 155K, 90% write misses.**
- Stack high-water >64MB for a 632KB input (valgrind default-stack overflow mid-match); s126 treebank finding gave ~400B/input-byte.
- Frames are TINY and correct (census: 47× sub rsp,8 · 16× sub rsp,16 · 2× sub rsp,32; the lone 64KB+rep-stosb is main's frame, once).
- ⇒ the cost is COUNT × RETENTION: under uniform-β every determinate box's 8-32B frame is retained to construct
  exit, so the rsp frontier marches tens of MB cold (write-allocate misses) while SPITBOL retains ~2 words per
  genuine choice point in a warm arena. Store-per-useful-work ≈ 10× theirs. SPD-1 elementary-test inlining is
  DEMOTED (instruction count already at parity on this trio); re-rank after the retention fix.
- Startup floor: loader symbol churn ~1.6M Ir (-rdynamic + big .so) + a 678K-Ir init memset — this is most of the
  gap on claws5-match (sbl total = 1ms; our match is only ~1.4M Ir).
- dtp_fn_of 4.3-4.6% on json/treebank (per-activation DEFER resolve; memoizable).

## PART 3 — RULED (Lon, live session): SYNC-POINT ζ RELEASE — the next rung

ω-free is the done-and-perfect LIFO half. **No per-box γ free — ever.** Release is a BULK WHACK of a whole span at
SYNC POINTS, which are declared by the pattern's own structure (enumerable by IR kind, zero analysis), each
recording an rsp watermark at its α and restoring to it on its sync edge:
1. **Match-bracket END** (IR_MATCH_HEAD…RELEASE, LIFO-paired per s49) — whole-match success/failure kills the span.
2. **FENCE(P) success exit** — manual: alternatives within P invisible when backing up ⇒ P's span dies at forward
   completion. json-match's `ws = FENCE(SPAN…|'')` declares thousands of these in the hot path.
3. **Plain FENCE forward crossing** — backing in fails the whole match ⇒ left-of-fence span dead (ω → match-fail).
4. **Anchor advance** (unanchored) — each failed attempt's span dies before the retry.
s74 SAVE-FRONTIER banked the mechanism empirically (saved-RSP − RSP recovers the span byte-exactly; LIFO holds).
FIRST VERIFY: whether the s71 FENCE seal glue pops the ζ span or only rewires ω arms — the latter is the bug.
HONEST RANKING: json-match is FENCE-rich → full win. treebank-match/claws5-match contain NO FENCE → retention to
match-end is semantically required in both engines → they need the CHOICE-POINT RECORD DIET (retain ~2 words at
genuine alternatives only) as the second half. Startup floor is the third rung (claws5 class).
