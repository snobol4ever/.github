# FINDING 2026-07-25 (s160b) — `sno_cconst_lookup` ERADICATED (FOLD IS NOW LITERAL/`&LCASE`/`&UCASE`/`CHAR(lit)` ONLY), AND THE TREEBANK m4 DIVERGENCE ROOT-CAUSED TO A 15-LINE REPRO: AN `EVAL`-BUILT DEFERRED PATTERN POISONS THE NEXT DIRECT-BUILT ONE

**Session:** s160 (continued) · **Goal:** GOAL-SNOBOL4-BB.md
**Lon directives this session:** *"remove usage of `sno_cconst_lookup`. Not a valid optimization. We will only fold the actual literal constants, `CHAR(literal)`, and `&LCASE`, and `&UCASE`. Do not go look up other code variables and assume they are constant."* · *"Fix the 15 demo programs to actually work."*

---

## PART 1 — `sno_cconst_lookup` REMOVED (LANDED, GATED)

### What the fold is now
`sno_cset_fold` (`src/lower/lower_snobol4.c`) admits exactly four forms and nothing else:
1. `TT_QLIT` — an actual literal string
2. `TT_KEYWORD` ∈ { `&LCASE`, `&UCASE` } — **and only those two**
3. `TT_FNC` `CHAR(n)` with `n` an integer **literal**, 1..255
4. `TT_SEQ`/`TT_CAT` — concatenation, recursing into the above

**The `TT_VAR` arm is GONE.** The lowerer no longer looks up a program variable and assumes it is constant.

### What was deleted
The entire `sno_cconst_*` subsystem existed to serve that one arm and is now dead and removed:
`SNO_CCONST_MAX`, `g_sno_cconst`, `g_sno_ncconst`, `sno_cconst_write`, `sno_cconst_scan_writes`,
`sno_cconst_scan_indirect_target`, `sno_cconst_note_define_names`, `sno_cconst_build_table`, `sno_cconst_lookup`,
plus its three call sites. **`lower_snobol4.c` 2,440 → 2,387 lines; `grep -c 'sno_cconst\|SNO_CCONST'` = 0.**
(`SNO_CCONST_MAX` was doing double duty as the bound of the unrelated freeze-write table; that got its own
correctly-named `SNO_FZW_MAX` rather than being left as a dangling misnomer.)

### ⭐ THE KEYWORD TABLE WAS ALSO INVENTING KEYWORDS — TRIMMED
The old `kc[]` folded ten names: `lcase ucase digits ht lf nl vt ff cr esc`. **The SPITBOL manual's complete keyword set
(Ch.16, protected p.187–188 + unprotected p.189ff) contains `&LCASE` and `&UCASE` and NONE of the other eight.**
SCRIP was silently accepting `&DIGITS`/`&NL`/`&HT`/… as foldable csets — programs using them compile under SCRIP and
die under `sbl`. This is the same class of latent divergence as the s159 `&DIGITS` warning, now removed at the source.
Blast radius measured before cutting: exactly one corpus file (`programs/csnobol4-suite/digits.sno`) mentions any of the
eight, as `OUTPUT = &DIGITS` — **not** a cset argument, so `sno_cset_fold` never sees it. Unaffected.

### ⭐ WHY THE CORPUS REWRITE HAD TO LAND FIRST — MEASURED BOTH WAYS
With the VAR arm removed, the **rewritten** demos emit **byte-identical** code to what they emitted with it:
claws5 149,023 · treebank-list 217,474 · calc-1 149,714 · calc-2 150,015 — all unchanged. The rewrite fully
substituted for the unsound optimization.

Re-compiling the **pre-rewrite originals** under the new fold shows what removal would have cost without it:

| original source | old fold | new fold | delta |
|---|---|---|---|
| claws5 | 149,023 | 150,457 | **+1,434 B** |
| calculator-1 | 149,714 | 150,807 | **+1,093 B** |
| calculator-2 | 150,015 | 151,108 | **+1,093 B** |
| treebank-list | 221,179 | 221,179 | +0 |

Those three *were* relying on the unsound lookup. `treebank-list` is +0 because its `nl` is capture-assigned
(`&ALPHABET POS(10) LEN(1) . nl`), which `cconst_lookup` refused anyway — the s160a finding.
⇒ **The corpus literalization was a strict prerequisite for removing the unsound arm at zero codegen cost.**

### Gates (all green / at watermark)
- sno smokes **7/7 both modes**
- full crosscheck **m3 314/1 · m4 309/4 · DIVERGE=3** — *identical to the s159 watermark*, same three
  `21{4,5,6}_indirect_goto*`. **Correctness-neutral across all 315 programs.**
- beauty `test_beauty_snocone_all_modes.sh` PASS=39 FAIL=3 SKIP=3; the 3 are `trace --run`, unrelated —
  `sno_cset_fold` is file-`static` in `lower_snobol4.c` with **zero** references outside it, so it cannot reach snocone.
- RT_OPT=`-O0` throughout. No `-O1`/`-O2` (RULES O2-DIRECTED-ONLY).
- Codegen DID change ⇒ **`.s` regen is OWED** (RULES handoff step 4) — see OWED below.

---

## PART 2 — "MAKE THE 15 ACTUALLY WORK": treebank m4 ROOT-CAUSED

Three of the fifteen fail, all pre-existing MODE34 violations: `claws5` m3 DIVERGE/m4 IDENT ·
`treebank-list` m3 IDENT/m4 DIVERGE · `treebank-array` m3 IDENT/m4 DIVERGE. **The treebank pair is now root-caused.**

### Symptom
`treebank-array` m4 emits **17 bytes** (`('NNP', ('NNP'))`) against m3's correct 281,844. Shrinking the input to
400 bytes still reproduces: m3 1,086 B correct tree, m4 15 B (`('NN', ('NN'))`). **The bank's root tag is wrong** —
it is a leaf tag, not `'BANK'` — i.e. the frame stack never pops correctly and the whole tree collapses to one node.

### Excluded by measurement (do not re-walk)
- **The slurp loop and the `spat` match loop are BIT-IDENTICAL in m3 and m4.** Instrumented probe on 3 KB of corpus:
  both report `SIZE(src)=3001`, then matches 1–4 with identical `SIZE(item)` (367/450/400/378) and identical
  remaining sizes. Input handling is not the bug.
- **`nl` is computed correctly in m4.** `&ALPHABET POS(10) LEN(1) . nl` ⇒ `SIZE(nl)=1` in sbl, m3 and m4 alike.
- Not the cset fold (this session's change): the divergence predates it and is unchanged by it.

### ⭐ ROOT CAUSE — 15-LINE REPRO, NO CORPUS NEEDED
The program drives its tree-building entirely through the SNOBOL4 side-effect idiom `epsilon . *f(...)`
(`epsilon` is unassigned ⇒ null string; the deferred `*f(...)` is evaluated when the match reaches that point;
`f` does its side effect and `NRETURN`s the harmless name `dummy`). Five such patterns exist —
`Init_list`, `Push_list`, `Push_item`, `Pop_final` are built via **`EVAL()`** (run-time compilation, needed to
interpolate the variable name), while **`Pop_list` uses the DIRECT form** and is built *after* them (line 78 vs 57/64/71).

**In mode 4, a direct-built `epsilon . *f()` pattern constructed AFTER an `EVAL`-built one binds to the EVAL-built
pattern's deferred expression instead of its own.**

```snobol
               DEFINE('side(v)')
               DEFINE('Side(vs)')                           :(send)
side           OUTPUT = 'SIDE-EFFECT ' v
               side           =  .dummy                     :(NRETURN)
Side           Side           =  EVAL('epsilon . *side(' vs ')')  :(RETURN)
send
               DEFINE('dside()')                            :(dend)
dside          OUTPUT = 'DIRECT-EFFECT'
               dside          =  .dummy                     :(NRETURN)
dend
               tagv = 'HELLO'
               pe = Side('tagv')
               pd = epsilon . *dside()
               'abc' ('a' pe 'b')                           :S(o1)F(f1)
o1             OUTPUT = 'EVAL-form matched'                 :(n2)
f1             OUTPUT = 'EVAL-form FAILED'
n2             'abc' ('a' pd 'b')                           :S(o2)F(f2)
o2             OUTPUT = 'direct-form matched'               :(fin)
f2             OUTPUT = 'direct-form FAILED'
fin
END
```

| engine | line 3 of output |
|---|---|
| `sbl` | `DIRECT-EFFECT` |
| SCRIP m3 | `DIRECT-EFFECT` ✅ |
| **SCRIP m4** | **`SIDE-EFFECT HELLO`** ❌ — fires the EVAL pattern's callback |

### Two controls that sharpen it to a one-line statement
- **Two DIRECT forms, no `EVAL` at all** (`pa = epsilon . *fa()`, `pb = epsilon . *fb()`): m4 prints `AAA` then `BBB`
  — **CORRECT**. So the deferred machinery per se is fine.
- **Reverse order — DIRECT built first, `EVAL` second:** m4 **CORRECT**.

⇒ **The defect is ORDER-DEPENDENT and `EVAL`-TRIGGERED: only `EVAL`-built-then-direct-built collides.** The natural
reading is that the `EVAL` (run-time compile) path leaves a deferred/capture binding latched such that the next
compile-time-built deferred target reuses it rather than allocating its own — a mode-4-only slot-collision, since
m3 is clean on every one of these.

**This maps 1:1 onto treebank:** `Pop_list` (direct, built last) fires `Pop_final`/`Push_item`'s callback instead of
popping ⇒ frames never pop ⇒ bank collapses to a single node ⇒ the observed `('NN', ('NN'))`. `treebank-list` fails the
same way with a different visible residue (`''`), consistent with the same collision hitting a list rather than an array.

### ⚠ METHODOLOGY NOTE (RULES' first absolute rule)
RULES mandates monitor-first. **The monitor is still dark for SNOBOL4** (s158: `PARTICIPANTS="spl scr"` reports DIVERGE
at step 2 on a three-line hello-world) and `probe.py`, the sanctioned fallback, **does not exist in the tree**. This
bug was therefore bracketed by oracle-differential shrinking (input bisect → construct isolation → two controls),
which is the same bracket theorem applied offline. **MON-RE remains the highest-leverage rung** — with a live monitor
this would have been mechanical instead of exploratory.

---

## NEXT / OWED

1. **`.s` REGEN IS OWED** — codegen changed (fold trimmed), so RULES handoff step 4 fires: run all three
   `.s` regen scripts (`util_regen_demo_s_artifacts.sh`, `util_regen_feature_s_artifacts.sh`,
   `util_regen_benchmark_s_artifacts.sh`). **NOT done in this session — do it before/with the commit.**
2. **Fix the m4 EVAL/deferred slot collision** using the 15-line repro above (add it to
   `corpus/crosscheck/patterns/` as a regression once fixed). This fixes 2 of the 3 broken demos.
3. `claws5` m3 ordinal-20 capture bug (s158 localization still stands).
4. `claws5` SEGV @20x volume; `treebank-list` m3 input-size-dependent divergence.
5. **MON-RE** — see methodology note.

`handoff_status.sh` is the push truth. **No push status is asserted in this document** (RULES stale-orientation rule (a)).

---

## PART 3 — LOCALIZATION OF THE m4 EVAL/DEFERRED COLLISION (s160b, partial — handed off mid-hunt)

Progress past the repro, recorded so the next session does not re-walk it.

**THE MECHANISM IS `rt_defer_*`, NOT the expression registry.** The emitted mode-4 asm for the failing repro routes
deferred side-effect patterns through `rt_defer_get_pat_fn@PLT` → `rt_defer_open` → `rt_defer_step` → `rt_defer_close`
(`src/runtime/pattern_match.c`). **`rt_defer_get_pat_fn(const char *varname, int ival_flag)` (pattern_match.c:960)
resolves the deferred target BY NAME STRING** — for a `*`-prefixed name it calls `rt_call_proc_descr(varname+1, 0)`
and, failing that, latches `g_star_peek {nm,val,valid}`. **A single file-static `g_star_peek` shared across
deferred resolutions is the prime suspect for the cross-pattern bleed** — it is exactly a one-entry latch, which
matches an order-dependent "second pattern gets the first's callback" symptom. START THERE.

### EXCLUDED BY MEASUREMENT — do not re-walk
- **NOT the expression registry.** `xa_expression_registry` / `rt_register_expressions` (`xa_file_header.cpp:12-13`)
  appear **zero** times in the emitted asm of both the failing and the working repro. (Note in passing: that symbol is
  declared in `rt/rt.h:92`, emitted as a call by the file-header template, has **no definition anywhere in `src/`**, and is
  **absent from `nm -D out/libscrip_rt.so`** — dead-or-latent machinery worth its own dead-code-sweep ticket, unrelated here.)
- **NOT an `OPQ$` name collision.** The opaque-defer path (`pattern_match.c:51-53`) mints `OPQ$<n>` from a
  `static int opq_uid` and binds via `NV_SET_fn`. Hypothesis was compile-time-baked vs runtime-minted `OPQ$0` colliding.
  **Falsified:** `grep -o 'OPQ\$[0-9]*'` returns **empty** for the failing repro, the working repro, and
  `treebank-array.s` alike — these names are minted purely at runtime and never baked into the `.s`.

### Suggested next probe (cheap, mechanical)
`gdb` the failing repro's m4 binary, break on `rt_defer_get_pat_fn`, and compare `varname` on the two calls
(expect `*side` then `*dside`); if the second call receives the right name but returns the first's `fn`, the fault is in
`rt_call_proc_descr`/`dtp_fn_of`/`g_star_peek`; if it receives the WRONG name, the fault is upstream in how the
compile-time-built `TT_DEFER` node's name reaches the box in mode 4. **The repro is 20 lines and runs instantly — this is
a one-breakpoint question, not an investigation.**
