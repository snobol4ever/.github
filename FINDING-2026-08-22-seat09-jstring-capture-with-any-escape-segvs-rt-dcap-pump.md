# FINDING — seat09: a captured JSON string containing ANY escape sequence SEGVs `rt_dcap_pump()`

**Date:** 2026-08-22 · **Seat:** seat09 (`/home/claude09`) · **Discovered while working:** queue row `fence-jstrbody-cas` (building comma-free witnesses to work around the `json-alternate-af-spin` block — see that row's own FINDING for context; this defect is unrelated to both `json-alternate-af-spin` and `fence-jstrbody-cas` and is filed separately per THE LOOP's "surprising ≠ blocking, record and carry on" rule).
**Status:** NOT FIXED — root cause hypothesized, not verified past the crash site. Reported, not claimed. Routed to HQ via `s4e_msg.sh ask`.

## 1. THE DEFECT, MINIMAL AND DETERMINISTIC

`corpus/programs/snobol4/demo/json.sno`, both m3 and m4, both crash (SIGSEGV) on the 4-byte JSON document `"\t"` — a bare top-level string containing exactly one escape sequence and nothing else. Under normal ASLR the crash is **probabilistic** (sometimes SIGABRT via `[ZHP] heap exhausted`, sometimes SIGSEGV, sometimes a clean pass — same binary, same input, different runs); **with ASLR disabled it is 100% deterministic**:

```
setarch "$(uname -m)" -R ./scrip corpus/programs/snobol4/demo/json.sno < minimal.json   # minimal.json = "\t"  (4 bytes)
→ Segmentation fault, every time, both m3 and m4 (10/10 reps each, confirmed)
```

**Isolation, all ASLR-off / 3+ reps each:**

| input | escapes | result |
|---|---|---|
| `"\t"` (4 B) | 1 | **SEGV, 10/10** |
| `{"\t":1}` (8 B) | 1, in the KEY position | **SEGV** — not value-specific |
| a 200-byte plain string, zero escapes | 0 | clean, 3/3 |
| `{"a":1}` (no string escapes anywhere) | 0 | clean (datatype-case mismatch only, unrelated — see §4) |
| `n`-escape ladder `"plain \t "×n end"`, n=1..8 | 1–8 | **SEGV at every n≥1 tested (1,2,3,4,5,6,7,8), ASLR off** |

**One escape sequence, anywhere in a captured string, is sufficient and necessary** (of everything tried). Escape-free strings of any length tested are clean.

**Capture-specific, not grammar-specific:** `json-match.sno` (the zero-capture recognize-only sibling, identical grammar) runs the SAME `"\t"` input cleanly, 3/3, ASLR off. `json.sno`'s only structural difference at the string sites is the `.` captures (`. jxk`, `. jxs`) and the `*ekey()`/`*estr()` deferred calls — so the defect lives in the capture/deferred-action machinery, not in string matching itself.

## 2. CRASH SITE

```
Program received signal SIGSEGV, Segmentation fault.
__memcpy_avx512_unaligned_erms ()
#0  __memcpy_avx512_unaligned_erms ()
#1  rt_dcap_pump () at src/runtime/pattern_match.c:652
#2  c_rt_dcap_end_ok_open (mark=..., top=..., subj="\\t") at src/runtime/pattern_match.c:684
#3  rt_match_end_all (mark=..., top=..., subj="\\t", outer=...) at src/runtime/pattern_match.c:701
#4-13 ?? (frame walk breaks — the two frames above are the deepest symbolized)
```

`pattern_match.c:652`:
```c
if (copy) { if (len > 0 && c->subj) memcpy(copy, c->subj + e->saved_delta, (size_t)len); copy[len] = '\0'; }
```
`copy = rt_str_alloc(len)` (line 651) succeeded (non-null, checked); the crash is inside the `memcpy` reading from `c->subj + e->saved_delta`. Either that source pointer is out of bounds or `len`/`saved_delta` are stale/corrupt by the time this particular queue entry is pumped.

## 3. WORKING HYPOTHESIS — UNVERIFIED, NOT ROOT-CAUSED, NAMED SO THE NEXT SESSION DOESN'T RESTART FROM ZERO

`rt_dcap_pump()` walks a per-match queue of deferred-capture records (`g_dcf[g_dcf_top-1]`, pushed by `c_rt_dcap_end_ok_open`, `g_dcf_top` incremented on push — **no decrement was found anywhere in the read range**, `pattern_match.c:600-701`). `estr()`'s deferred action (queued as a `*estr()` entry, pumped via the `IS_FAIL_fn`/`by_name` branch at line 655-671) calls `jdec(jxs)`, and `jdec()` itself runs a **second, independent SNOBOL4 pattern match with its own `.` captures** (`s FENCE (BREAK(bslash) | '') . seg bslash LEN(1) . ec = :F(jdec_done)`, json.sno:98). A capturing match executed *from inside* the pump loop of an outer capturing match's deferred call is exactly the reentrant shape `g_dcf_top` as a stack (rather than a single slot) seems designed to support — but the outer `rt_dcap_pump()` (line 646) caches `rt_dcf_t *c = &g_dcf[g_dcf_top - 1]` **before** calling into the deferred function, then keeps using that same `c` pointer in its `while (c->cur < c->top)` loop **after** the nested call returns. If `g_dcf_top` is never restored (popped) when the nested pump finishes, `c` is reading a frame that is no longer "top of stack" by the array's own bookkeeping, which is consistent with — though not proven to cause — corrupted `saved_delta`/`len` on the entries read afterward. **This is a hypothesis to test first, not a diagnosis.** No breakpoint/watchpoint work was done to confirm it; ASM-DIFF-FIRST / gdb-with-hit-counts on `rt_dcap_pump` reentrancy is the next step, not repeated here.

Escapes are the trigger because `jdec()`'s own inner match — hence the reentrant pump — only ever runs when `jdec`'s fast path (`s bslash :F(jdec_fast)`, json.sno:96) is bypassed, i.e., only when the captured string actually contains a backslash. That is exactly and only the condition under which every reproduction above crashed.

## 4. WHAT THIS IS **NOT**

- **Not `json-alternate-af-spin`** (rank-0, seat04 claimed, in progress) — that is a deterministic infinite loop on comma-bearing input, flat RSS, no crash. This is a crash (SIGSEGV/SIGABRT) on a 4-byte, comma-free input; RSS is irrelevant, nothing loops.
- **Not the benchmark-harness heap-exhaustion side-observation** noted in `FINDING-2026-08-22-seat11-cond-assign-double-fire-was-a-missing-break-in-the-dcap-pump.md` ("object-bearing inputs under the benchmark harness's **iteration loop**") — that needs many repeated match iterations; this crashes on a **single** match, no loop, no harness involved.
- **Not the `cond-assign-double-fire` bug seat11 fixed this session** (same file, `continue`-vs-`break` at lines 664-665) — that fix is already in this build (pulled + `make pristine` rebuilt before this investigation) and is confirmably still present; this crash is at line 652, a `memcpy`, a different mechanism. Whether the two are related via `g_dcf_top` bookkeeping is exactly the open question in §3.
- **Not the `datatype-case` mismatch** (`JOBJ` vs `jobj`, rank 34, already queued) — that's a separate, cosmetic, rc=0 output diff seen on plain `{}`/`{"a":1}` witnesses in the course of this same session's baseline runs; unrelated, already tracked.

## 5. BLAST RADIUS, UNMEASURED BUT LIKELY LARGE

Every non-trivial real-world JSON document contains at least one string with an escape (`\"` alone is extremely common). `citm_catalog.json` (the row's own target file, 1.7 MB, "mostly strings") almost certainly contains escapes and would hit this on `json.sno` regardless of the `af-spin` comma defect — i.e., **this may be a second, independent reason `json.sno` cannot run the intended benchmark**, on top of the comma spin. Not confirmed against the actual file (out of scope for this seat's row; flagging for whoever owns either `json-alternate-af-spin` or triages this).

## 6. REPRO ASSETS

Minimal witness and the escape-count ladder are in scratch, not committed (per RULES.md, `.s`/probe artifacts beside corpus programs are honest current output, never pinned goldens — and these are throwaway probes, not corpus programs):
```
"\t"                    # minimal.json, 4 bytes — SEGVs deterministically under: setarch $(uname -m) -R
{"\t":1}                # minimal_key.json, 8 bytes — same crash via the KEY path
```
Reproduce: `setarch "$(uname -m)" -R timeout 8 ./scrip corpus/programs/snobol4/demo/json.sno < minimal.json` (repeat a few times if ASLR is left on — it is probabilistic, not absent).

## 7. WHAT I DID NOT DO, AND WHY

Did not attempt a fix — this was discovered while building regression witnesses for `fence-jstrbody-cas` (a different, already-claimed row) and is squarely a new, unclaimed, HQ-triage-worthy defect, not mine to freelance into. Did not single-step the reentrant `g_dcf_top` hypothesis with breakpoints/hit-counts (RULES.md ASM-DIFF-FIRST step 3) — minting the smallest repro (step 1) is as far as this seat carried it before returning to its own claimed row. Did not check whether `citm_catalog.json` itself contains escapes (would confirm §5) — left for whoever triages this or resumes `json-alternate-af-spin`/the eventual `fence-jstrbody-cas` finish, since both need this defect's disposition before they can run their own real-input measurement anyway.
