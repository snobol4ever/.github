# FINDING-2026-07-28-CLAUDE-SN4-DEFER-GEOM-AND-PATREF-SPLIT.md

Session s200. Root cause of the stored-pattern SIGSEGV localized by bisect;
design discussion with Lon resolved the op-split directive. No code landed.

---

## 1. BISECT RESULT — first bad commit is 2410f938 (FLATDISP-1, s188)

Range: f0914867 (PERF-PAT-1, GOOD) .. 83114981 (s193 HEAD-unlock, BAD).
405 commits. Manual bisect, clean build each step (~134s, single CPU).

First bad: `2410f938` — *"FLATDISP-1 (s188): x86_frame_off() is the ONE
offset function; rsp becomes the frame base by default."*

The commit body itself recorded the sacrifice:

> rbp refs 2951 → 323 (−89%).
> **Known-bad accepted by directive: mixed_workload, pattern_bt,
> string_pattern segfault (pass at baseline).**
> **Remaining blocker is fc_leaf_walk being called on the pattern range only.**

So the stored-pattern segv is the **priced cost of FLATDISP-1**, not a
later regression. It has been open since s188.

---

## 2. ROOT CAUSE — fc_geom omits IR_MATCH_DEFER

`fc_geom()` in `src/contracts/zeta_storage.c` declares the static
16-byte FORTH cell for every carving leaf: SAVE, ARB, SPAN, TAB, RTAB,
BREAK, BREAKX, BAL, REM, ALTERNATE, SCAN_TAB/MOVE/MATCH.

**IR_MATCH_DEFER is absent.**

Consequence: `fc_leaf_walk`'s prefix sum `op_flat_disp` is 16 short for
every node after a DEFER. `FRQ` → `x86_frame_off(off) = off +
op_flat_disp` → emits `[rsp+80]` where the slot is at `[rsp+96]`.

Measured at the fault (gdb, mode-4 binary with symbols, `break
*n10_match_release_α`):

```
entry rsp = 0x7fffffffe8c0
[rsp+80]  = 0x0000000000000005   ← slot content (garbage)
[rsp+96]  = 0x00007fffffffe8d0   ← valid stack address, the real saved rsp
```

`mov rsp, [rsp+80]` loads `0x5`; next `push r14` faults. rsp = 0x1 at
SIGSEGV (confirmed by gdb `info registers`). rbp is intact
(`0x7fffffffe930`).

This explains the inline/stored split exactly:

- `S BREAK(',') . WORD ','` — inline, no DEFER node emitted → clean
- `PAT = BREAK(',') . WORD ','` / `S PAT` — TT_VAR lowers to
  IR_MATCH_DEFER → offset wrong → SIGSEGV

**Minimal 4-line reproducer (keep as permanent gate):**

```snobol
    PAT = ','
    S = 'alpha,beta,'
    S PAT   :F(NO)
OUTPUT = 'matched'  :(END)
NO  OUTPUT = 'failed'
END
```

SPITBOL: `matched`. SCRIP at HEAD: SIGSEGV.

---

## 3. CANDIDATE ONE-LINER AND WHY IT IS NOT CLEAN

Adding beside the ALTERNATE case in `fc_geom`:

```c
if (nd->op == IR_MATCH_DEFER)  { if (k) *k = 16; return 1; }
```

Measured with this applied:

| | s199 baseline | with fix |
|---|---|---|
| m3 PASS/FAIL | 221/94 | **222/93** |
| m4 PASS/FAIL | 219/94 | 220/82 |
| m4 SKIP | 2 | **13** |
| DIVERGE | 1 (W06_tab) | 1 (W06_tab) |
| `scrip --compile` abort | no | **yes** |

m4 SKIP jumped 2→13 because `scrip --compile` **aborted** on newly
credit-16 DEFER programs — a regression hiding inside a better-looking
FAIL count. **Reverted, not landed.**

Flat 16 is wrong because `x86_frame_sink`'s own comment names DEFER a
**deep window** with a *runtime* `fbytes` sink (`sub rsp,rax; sub
rsp,16; and rsp,-16; mov [rsp+0],rcx`). Crediting only 16 double-counts
against the sink, mis-sizing the callee frame.

DEFER's full static contribution requires knowing its *resume-record*
piece (static 16) separately from its *dynamic sink* piece (runtime
fbytes). Those two cannot be flattened to a single constant.

---

## 4. THREE-WAY RBP TAXONOMY (Lon design discussion)

**Case 1 — ALT merge pad. No rbp needed.**

Arms run at their own natural depth with no padding during execution.
Pad stubs fire on the *yield edge* only to reconcile depths at the merge
label. Cost: one `rsp` adjustment per arm exit. Nodes after the ALT get
one unambiguous `op_flat_disp`. rbp would eliminate the pad but is not
required for correctness.

**Case 2 — DEFER dynamic window. No rbp needed.**

`x86_frame_sink` parks old-rsp at `[rsp+0]` of the carved frame and
releases with `mov rsp,[rsp]` — a depth-immune anchor held *in memory*
instead of a register. Works because the callee is `ret`-terminated: rsp
is known at the release point. So the dynamic part of DEFER already has
an rbp-free answer in the codebase.

**Case 3 — PAT$ scan-retry. rbp is genuinely load-bearing.**

`scanfail` is reached by a jmp from *arbitrary* carve depth, not by a
return. The parked-anchor trick fails: you need to know where the anchor
*is* before you can read it, and at arbitrary depth there is no known rsp
to find it from. That is why `mov rsp,rbp` is the only sound unwind.
These 42 refs are not unfinished work — they are the correct answer.

**Conclusion:** s189 "no going back" holds for Cases 1 and 2. Case 3 is
the priced remainder. The 48 in the census = 42 PAT$ scan-retry (Case 3,
irreducible) + 6 marshal reads (IR_SAVE_RESTORE wire-adopt, register
reads not frame references, arguably uncountable).

---

## 5. OP-SPLIT DIRECTIVE (Lon, s200)

Lon: *"S ? P should not be a DEFER, and S ? *P should be."*

Today both TT_VAR (bare pattern-valued variable, eager) and TT_DEFER
(unevaluated-expression `*`, potentially recursive) lower to
IR_MATCH_DEFER. One opcode carries two genuinely different geometries:

- TT_VAR: eager — pattern built at construction time, static footprint
- TT_DEFER: unevaluated — evaluated at match time, dynamic sink

One opcode cannot declare both in `fc_geom`, which is why it currently
declares neither correctly.

**Directive:** split IR_MATCH_DEFER into two opcodes:

| New name | Old source | Semantics |
|---|---|---|
| `IR_MATCH_PATREF` | TT_VAR | Bare pattern-valued variable. Eager, no `*`. Static geometry — no dynamic sink, just the 16-byte resume record. |
| `IR_MATCH_DEFER` | TT_DEFER | Unevaluated `*` expression. Dynamic sink, potentially recursive. Existing deep-arrival classification (DEFER-STAR, s199) applies to this opcode only. |

Lower site: `lower_snobol4.c` ~1212–1218, the `sno_pat_node` TT_VAR /
TT_DEFER arms. Both currently emit IR_MATCH_DEFER; split the emission.

Template site: `bb_match_defer.cpp` — read by both today. After split,
IR_MATCH_PATREF can emit a simpler box (no dynamic sink, no DEFER-STAR
deep-arrival gate). IR_MATCH_DEFER keeps the existing template.

`fc_geom` site: IR_MATCH_PATREF can safely receive `*k = 16; return 1`
because its full carve IS static. IR_MATCH_DEFER must not — its dynamic
fbytes cannot be expressed as a constant.

`emit_graph_has_deep_arrival` / `sno_defer_is_star` (s199 side table):
these gate on the star-source; after the split they simply gate on
IR_MATCH_DEFER (the opcode IS the star-source discriminant — no side
table needed).

**IR name:** Lon flagged the existing `IR_MATCH_DEFER` name as confusing
alongside `DEFER` (the language keyword). Suggested replacement:
`IR_MATCH_UNEVALED` or `IR_MATCH_STAR` (the latter names the `*`
operator directly, matches manual usage, and is unambiguous in the IR
table). `IR_MATCH_PATREF` for the eager arm.

---

## 6. NEXT RUNGS IN ORDER

(a) **IR_MATCH_PATREF split** — the prerequisite for every stored-pattern
fix. Lower site (~1212-1218), fc_geom, emit dispatch, template split,
sno_defer_is_star simplification. Monitor-first on the 4-line reproducer.

(b) **IR_MATCH_PATREF geometry in fc_geom** — after (a), adding
`IR_MATCH_PATREF: k=16` is the safe one-liner. Verify m3/m4 both clean,
no compile abort.

(c) **DEFER dynamic-sink geometry** — IR_MATCH_DEFER's static 16 plus its
runtime fbytes. Requires tracing how `x86_frame_sink` interacts with
`fc_leaf_walk`'s prefix sum; see `x86_frame_sink` comment in x86_asm.h
~1459.

(d) **ARBNO-ELEM dig** — unchanged from s195/s199 cursor, still open.

(e) **fc_cond FIRST-WINS audit** — unchanged.

(f) **SYM-VIS-M3** — unchanged.
