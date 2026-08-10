# FINDING 2026-08-10e (CLIMB s40, Claude Opus 5) — H31 is GREEN at `bce9a4b`: the 3R is a 2R and M-1b loses its only NESTING witness; and TAB/POS + replacement splices the WRONG SPAN in both modes while LEN is correct

**Tips measured:** SCRIP `bce9a4b` · corpus `bea31de` · `.github` `6777add` (pulled at close).
**Code changed: ZERO.** Two measured results, both reproducible; no edit, no commit to any code repo.
**Evidence namespace:** `/tmp/climb_s40/`.

---

## 0. BUILD PROVENANCE (METHOD 8) — and a THIRD stale-artifact layer nobody has named yet

Foreground, exit-checked, no background job, binary mtime predating every measurement.

**⚠️ NEW HAZARD — `out/rt_pic/*.o` IS A THIRD CONTAMINATION LAYER, BESIDE `/tmp/si_objs`.** The goal file's METHOD 8 names `/tmp/si_objs` as shared-across-checkouts. There is a second one, and it bit this session on the way in:

1. `make -j4 scrip` completed in **1 second, 5 log lines, rc=0, binary produced, smoke test green.** Every doorway check METHOD 8 lists was satisfied. It was a **thin-driver link only** — `scrip` is ~196KB of `src/driver/scrip.c`; the entire compiler is `out/libscrip_rt.so` (37MB).
2. `make libscrip_rt` then reported **up-to-date and did nothing**, against a `.so` whose mtime *predated the clone's own build* and which is **untracked** (`.gitignore:32: out/`, `git ls-files out/` = 0 files) — i.e. provenance unknown and unverifiable.
3. `rm -f out/libscrip_rt.so && make libscrip_rt` **relinked in 3 seconds** from ~260 pre-existing `out/rt_pic/*.o` objects that this session never compiled.
4. Only `rm -rf out/rt_pic && make libscrip_rt` produced a genuine build: **258 compile lines, 2m42s, rc=0, 0 errors.**

**The count is the tell.** The goal file's own phrase is *"263-line foreground build"* — one line per object. **A build that prints 2–5 lines is a relink, not a build, and it passes rc=0 + `[ -x scrip ]` + a hello-world smoke test.** METHOD 8 currently says build foreground and check the exit code and mtime; all three passed here on a tree whose compiler was never rebuilt.

**PROPOSED METHOD 8 ADDENDUM:** a watermark requires a build whose **log line count is ~258+**, not merely rc=0 with a fresh `scrip` mtime. `scrip`'s mtime proves only that the *driver* relinked. The artifact under test is the `.so` (consistent with FINDING-2026-08-01-WIREREG, *"the AB artifact is the SO not the binary"*). Recommended re-prove recipe: `rm -rf out/rt_pic && make libscrip_rt && rm -f scrip && make scrip`, then assert `wc -l` of the log.

---

## 1. WATERMARK AT `bce9a4b` — s39's explicitly-unclaimed number, now measured

s39 stated verbatim: *"⛔ WATERMARK: NOT RE-PROVED — DO NOT INHERIT A NUMBER FROM THIS SESSION … The watermark at this tip is **unknown and is not claimed unchanged**."* This fills that gap on a verified clean build.

| | pass | xfail | XPASS | REGRESSION |
|---|---|---|---|---|
| **m3** (`run_suite.sh`) | **134** | 15 | 0 | **2** — D12 · D13 |
| **m4** (`MODE=compile`) | **133** | 16 | 0 | **2** — D12 · D13 |

Prior record (s38 @ `66322b3c`, and MECH s36, and s35 — three independent proofs): m3 133/15/0/**3R**, m4 132/16/0/**3R**, regression set **D12 · D13 · H31**.

### ⭐ H31 IS GREEN. IN BOTH MODES. THE 3R IS NOW A 2R.

```
  ✅ H31   FENCE over ALT with capture: JSON key-value (renamed from 152)
```

Green in m3 and m4. Pass count moved +1 in each mode, exactly accounting for it. The D-2/D-3 **repaired-8 regression guard is fully intact** — D06 ✅ D09 ✅ D10 ✅ D11 ✅ H20 ✅ H21 ✅ X07 ✅ X08 ✅.

**This repair is UNDOCUMENTED.** Every mention of H31 across the FINDING set and both goal files treats it as red; no FINDING claims it. It was repaired by a parallel seat between `66322b3c` and `bce9a4b`, incidentally — the fixing seat did not know it had done it. (Per s37's rule I grepped the FINDING set before spending anything; the answer is that nothing claims it.)

### ⛔ CONSEQUENCE FOR MECH M-1b — ITS ACCEPTANCE SET IS NOW MIS-SPECIFIED

s38's cross-request addendum set M-1b acceptance = `{D12,D13,H31}` green both modes **AND** the repaired-8 staying green. s38's DELTA 2 established that the re-entry class has **two species** and that **H31 was the sole NESTING witness** (7 simultaneously-live blob activations, zero recursion); D12/D13 are the RECURSION species (`*LIST`).

**H31 is now green before M-1b has run.** Therefore:

- M-1b's acceptance set as written now spans **only the recursion species**. GLOBAL-EXECUTE could land, show `{D12,D13}` green, and satisfy the letter of the criterion **while silently regressing nesting**, with no witness to catch it.
- **RECOMMENDATION (MECH's ruling, not mine):** either re-home H31 from *acceptance* to the *regression-guard* set (making it a 9th guard beside the repaired-8), or mint a fresh nesting witness. My preference is the former — it costs nothing and preserves the coverage s38 deliberately constructed.
- **Open question I did NOT spend builds on:** whether the parallel fix repaired nesting *mechanically* or merely perturbed H31's stack layout so its overwrite lands somewhere harmless. If the latter, nesting is still broken and H31 is now a **false green** — which would make re-homing it as a guard actively misleading. This is cheap for MECH to settle from its own `g_blob_ctx[5]` root cause and expensive for CLIMB to settle by bisect (shallow clone, 1-CPU builds, and s37's void-bisect lesson). **Flagged, not claimed.**

---

## 2. ⭐ NEW C-9 DEFECT — TAB/POS + REPLACEMENT SPLICES THE WRONG SPAN (both modes). LEN IS CORRECT.

C-9's rung text names *"TAB-binds-subject trap manual p.143 #10"*; s39's close records it **still unprobed**. Probed now. It is a live defect, previously unwitnessed.

**Manual anchor (p.143 #10), verified against the oracle:** `TAB` and `BREAK` **bind** every character passed over, so the replaced span is the *full extent bound by the match*, not just the trailing primitive. `S ? TAB(49) LEN(1) = '*'` replaces the first **50** characters, not the 50th. Oracle reproduces this exactly.

### Minimal reproducers — subject `'ABCDEFGHIJ'`, one statement per program, literal args only

| statement | oracle | SCRIP m3 | SCRIP m4 | |
|---|---|---|---|---|
| `S TAB(4) LEN(1) = '*'` | `*FGHIJ` | `*BCDEFGHIJ` | `*BCDEFGHIJ` | ❌ |
| `S POS(4) LEN(1) = '*'` | `ABCD*FGHIJ` | `*BCDEFGHIJ` | `*BCDEFGHIJ` | ❌ |
| `S TAB(4) . FRONT LEN(1) = FRONT '*'` | `ABCD*FGHIJ` | `ABCD*BCDEFGHIJ` | `ABCD*BCDEFGHIJ` | ❌ |
| `S LEN(4) LEN(1) = '*'` | `*FGHIJ` | `*FGHIJ` | `*FGHIJ` | ✅ |

All three failing forms collapse the replaced span to **the first character, `[0,1)`**, in both modes, rc=0 — a **silently wrong answer**, not a crash.

### The discriminators (all measured, none inherited)

1. **LEN is CORRECT; TAB and POS are WRONG.** `LEN(4) LEN(1) = '*'` splices the full 5-char bound span correctly. The failing prefixes are the **absolute-cursor** primitives; the working one is **relative-advance**. This is the sharpest available lead.
2. **NOT "non-zero match start."** `S 'CD' = '*'` → `AB*EFGHIJ`, correct. Falsified.
3. **NOT "any cursor-advancing prefix."** Falsified by LEN, above.
4. **NOT the match, and NOT capture — the SPLICE only.** Without replacement, `X TAB(4) . F LEN(1) . G` → `ABCD:E`, and `Y POS(4) LEN(1) . H` → `E`, **both oracle-correct**. And inside the *failing* replacement statement, the capture is still right: `FRONT` = `ABCD` exactly, while the splice beside it is wrong. **That selectivity is the same fingerprint s35 used to convict the C-9 `FRQ`/`op_zdepth` splice defect** (`ROQ`/`ZOPQ` were correct while frame reads were short).
5. **NOT the variable-arg class (s39's rung).** Every arg here is a **literal**; s39's family needs a variable. Two distinct defects. C-3 green does not cover this because C-3 is match-only, never match-with-replacement.
6. **CONTEXT-DEPENDENT, which is the wrong-cell signature.** Isolated, `POS(4) LEN(1) = '*'` yields span `[0,1)`. With three match-replace statements in one program it yields span `[0,0)` (`*ABCDEFGHIJ`) — and **m4 SIGSEGVs, rc=139**, where the same file in m3 returns wrong values at rc=0. Per s39's own reasoning: a wrong *constant* fails uniformly; a wrong *offset* picks up whatever occupies the slot.

### ⚠️ DELIBERATELY LEFT UNCONVICTED

Anti-pattern §2 has falsified *"the offset is wrong by N bytes"* **twice**, and §4 requires measurement before edit. I have a fingerprint and a discriminator, **not** a mechanism. I did **not** read the emitter and I did **not** name a cell or an offset. Do not inherit one from this document.

**NEXT INSTRUMENT: MONITOR-FIRST, and the monitor is NOT dark for this class** — value divergence at rc=0 with live trace events, unlike the 3R crash class where MON-CAP would be a prerequisite. `scripts/test_monitor_2way_sync_step_bin.sh` on the single-statement TAB reproducer, bracketing between last-agree and first-diverge. The cheapest discriminating follow-up before any code is read: diff the emitted asm of `TAB(4) LEN(1) = '*'` (fails) against `LEN(4) LEN(1) = '*'` (passes) — same shape, one primitive apart, one of them correct. Per §4, an instruction byte-identical in the passing sibling is exonerated.

### Corpus witnesses — NOT added, by rule

These reproducers are **not** committed to `corpus/probe/bb/`. New red probes would register as REGRESSION against `XFAIL.run`, and RULES §4 forbids adding to XFAIL absent a Lon-ruled park. Files are in `/tmp/climb_s40/` (`tab_bind.sno`, `ctl.sno`, `match_only.sno`, `one.sno`) and inline above. **Lon: say the word and they become probes + XFAIL entries in the fix's commit, per §4.**

---

## 3. WITNESS SET (reported per METHOD)

Probe suite both modes ✅ measured (§1). Repaired-8 ✅ all green. H31 ✅ green (was red). D12/D13 ❌ unchanged, owner MECH M-1b, correctly parked. TAB/POS replacement ❌ new, §2. Match-only TAB/POS ✅ oracle-correct. LEN replacement ✅ oracle-correct. Not re-run this session: roman, stitch trio, uw2/uw3, 131/141/183/066, eval controls, 127/152 — **not claimed either way.**

## 4. WHAT I DID NOT DO

No code edited, no commit to SCRIP or corpus, no regen (no codegen touched). Did not re-run 061 (s39's live rung). Did not read `GOAL-SN4-ZETA-MECH.md` (RULES: read only the named goal). No bisect for the H31 repair — s37's void-bisect lesson plus a depth-1 clone; the FINDING-set grep came first and returned nothing.
