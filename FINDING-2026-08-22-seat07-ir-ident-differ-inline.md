# FINDING — IR_IDENT/IR_DIFFER inline (s199 slices 2+3): the redefinition question resolves to a
non-issue by measurement, and the real work was two "spelled-twice" classification lists

**seat07 (`/home/claude07`, Claude Sonnet 5), 2026-08-22, THE LOOP queue row `ir-ident-differ-inline`
(rank 1).** Slice 1 (SCRIP `235a812e`) minted `IR_IDENT`/`IR_DIFFER` additively. This row is slices 2
(lower IDENT/DIFFER calls to the new ops) and 3 (emit them inline) — landed, SCRIP `f6c5f9e2` (pre-rebase)
+ rebase onto `2e601a2e`.

## ⭐⭐⭐ THE FIRST-STEP QUESTION, ANSWERED BY MEASUREMENT: the redefinition guard

The brief required deciding, before writing code, between (a) a runtime live-binding check and (b) a
lowering-time refusal by BEHAVIOUR (never a name list) — "state the choice with its measurement."

**Measured via three oracle probes (`sbl -bf`), not assumed:**
1. `DEFINE('IDENT(X)')` targeting IDENT directly → **ERROR 248 "attempted redefinition of system
   function"**, fatal, execution halts at statement 1.
2. `OPSYN('IDENT','SIZE',0)` (OPSYN aliasing something else onto the name IDENT) → **same ERROR 248**.
3. `OPSYN('IDENT','SIZE',0)` routed through `CODE("...")` (the dynamic-string vector the brief named
   as the reason a purely static source-text scan can't be trusted) → does **not** crash the program,
   but the rebinding **silently fails to take effect**: `IDENT('ABCDE')` afterward still uses the
   original builtin (fails, since 'ABCDE' isn't null/SIZE-5).

**Conclusion, measured: real SPITBOL has no live rebinding of IDENT/DIFFER to guard against at a call
site — every avenue tried either fatally errors before a second statement runs, or is inert.** Neither
option (a) nor (b) as originally framed is needed for oracle-correctness.

**⛔ BUT — a real regression was found and fixed anyway.** SCRIP itself (pre-existing, independent of
this rung) is *more permissive* than the oracle on literal-prototype `DEFINE` specifically: `sx_lower`'s
`TT_OPSYN` and `DEFINE`-in-expression-position arms already defer to a compile-time registry,
`sno_predef_registered(name)` (`lower_snobol4.c:140`), that tracks every name this *specific program*
DEFINEs — and pre-slice SCRIP's generic call path honors it (`DEFINE('IDENT(X)')` followed by
`IDENT('A')` calls the user's procedure, unconditionally, printing the user's own return value). The
first version of this change didn't check that registry, so it silently reverted this SCRIP-native
behavior to the (inert) builtin. **Fixed**: `sx_lower`'s IDENT/DIFFER fast-path check now includes
`!sno_predef_registered(name)` (`lower_snobol4.c:425`), refusing the inline path whenever *this
program's own source* DEFINEs the name — a BEHAVIOUR check (does this program's own DEFINE table
contain the name), never a name list, using the exact precedent mechanism `sno_pred_relop`/`TT_OPSYN`
already established for this same class of problem. OPSYN and CODE()/EVAL remain unguarded because
pre-slice SCRIP never honored them for these names either (verified: `opsyn_probe.sno` prints nothing,
unchanged before/after) — there is nothing to preserve there.

Witness: `corpus/probe/` — see below; the compile-time-registry behavior is exercised directly by the
probes in this FINDING's own investigation trail (not checked in as corpus, since matching the ORACLE
here would be *wrong* — SCRIP's answer and the oracle's answer legitimately differ, and the oracle's own
"answer" is a fatal error with environment-dependent diagnostic text, not something worth pinning as a
`.ref`). Reproduce directly:
```
        DEFINE('IDENT(X)')              :(START)
IDENT   IDENT = 'REDEFINED-IDENT'       :(RETURN)
START   OUTPUT = IDENT('A')
END
```
prints `REDEFINED-IDENT` both before and after this rung (oracle: `ERROR 248`).

## ⛔⛔ TWO BUGS FOUND WHILE LANDING THE INLINE EMISSION — both were the SAME class

Once the templates existed and correctness testing began (broad OUTPUT=IDENT/DIFFER probes against the
oracle), results were wrong in a way that got WORSE, not better, as the test program grew — a strong
signal of a slot/offset bug, not a logic bug. ASM-DIFF-FIRST: minted the smallest repro
(`OUTPUT = IDENT('')` alone; correct), then grew it one statement at a time until it broke, then read
the emitted `.s` directly rather than guessing.

**Both bugs were the identical shape: a classification list that already listed `IR_CMP_TEST` (the
closest structural sibling — same "2-operand, boolean-branch, spine-resident" family) but had never been
taught about the two new opcodes, so IR_IDENT/IR_DIFFER fell through to that list's `default:` case
instead of `IR_CMP_TEST`'s case.**

1. **`zeta_storage.c:856`, `zw_carve_k`'s `_spine` exclusion list.** Spine-resident nodes (BINOP, LIT_*,
   VAR, CMP_TEST, COERCE_NUMERIC) are excluded from the FORTH-port incremental "frameless capture" carve
   — that carve is for pattern-matching geometry, not ordinary values. IR_IDENT/IR_DIFFER, lacking the
   exclusion, were eligible for a carve they didn't need. Fixed by adding both to the same list. (There
   is a second, textually-identical but *dead* copy of this exact list at `emit.cpp:979`, inert behind an
   immediate `(void)_spine;` cast — updated too, for whoever eventually resurrects it, but confirmed by
   direct trace to be provably inert today.)

2. **`emit.cpp`, `zd_nops`'s operand-count ternary (the real bug).** This was mis-scoped as
   "Icon/Prolog-cells-only" during design (its sibling `zd_wl_kind` genuinely is gated that way) and
   ruled out of scope on that basis — WRONGLY: `zd_wl_kind` defaults to "admit everything" for plain
   SNOBOL4 (`return 1` when neither `icn_cells_graph` nor `pl_cells_graph` is set), meaning the whole
   "ZD" (`op_zres`) fast operand-array path is live for ordinary SNOBOL4 graphs by default, not an
   Icon/Prolog-only tier. Confirmed by direct instrumentation: `bb_ident()` receives `op_zres=1` for a
   bare `OUTPUT = IDENT('')`. `zd_nops`'s `default:` arm returns `0` operands for any opcode not
   explicitly listed (its own listed sibling, IR_CMP_TEST, returns 2) — so the ZD-mode operand-array
   setup thought IDENT/DIFFER had **zero** operands and never populated `_.op_zread[0]`/`[1]`, and
   `ZOPQ(0,*)`/`ZOPQ(1,*)` read whatever those slots held from unrelated prior state. Since neither box
   variant (`op_sa`/`op_sb`/FRQ **or** `op_zres`/ZOPQ/ZRES) was implemented before this fix — only the
   first — the ZD-selected graphs read garbage operands into `descr_identical`, producing exactly the
   "gets worse with more statements" symptom (more statements → more opportunities to land on stale
   `op_zread` contents from whichever node happened to run before). Fixed two ways, both required: (i)
   `zd_nops` now returns 2 for `IR_IDENT`/`IR_DIFFER` alongside `IR_CMP_TEST`; (ii) `bb_ident.cpp`/
   `bb_differ.cpp` each grew an `_.op_zres` branch (ZOPQ/ZRES-addressed) mirroring `bb_cmp_test.cpp`'s,
   so the box is correct under **both** addressing conventions a graph may select — exactly what every
   other IR_CMP_TEST-family box already does, and what NO-PER-OP-FILTER requires of a new family member.

**Both classes are named here because a future opcode addition in this same "CMP_TEST-shaped" family
will hit them again if it copies only the emit.cpp driving-code case group and the box body — the
`_spine`/`zd_nops` lists are additional, separate registration points, not covered by
`ir_node_produces_value` (which *was* the one other required registration, `scrip_ir.c:237`).**

## Landed: the mechanism

- `IR.h`/`scrip_ir.c` opcode + name table: already landed in slice 1 (`235a812e`), untouched here.
- `scrip_ir.c:237` — `ir_node_produces_value` — added `IR_IDENT`/`IR_DIFFER` (this is the slot-grant
  eligibility authority; every `drive_value_slot` bomb message across the templates cites this function
  by name as the one place to check, confirming single-authority).
- `lower_snobol4.c` — new `sx_ident_differ` (mirrors the existing `sx_pred_cmp` precedent exactly:
  same left-to-right evaluation wiring, same "synthesize a literal operand when one is missing" idiom
  for the 1-arg form). Hooked into `sx_lower`'s `TT_FNC` case at the same spot `sno_pred_relop` is
  checked, guarded by `sno_predef_registered` (see above) and the killswitch.
- `emit.cpp` — operand-slot driving (`IR_COERCE_NUMERIC`/`IR_CMP_TEST` case group, now also
  `IR_IDENT`/`IR_DIFFER`), the main per-opcode dispatch (two new `case` arms calling `bb_ident()`/
  `bb_differ()`), `flat_unwind_beta`'s trivial-beta list, the RPO_PUSH ω-walk macro (CFG-walk
  completeness for the fail edge), and `zd_nops` (bug #2 above).
- `zeta_storage.c` — `zw_carve_k`'s `_spine` list (bug #1 above).
- `optimizer/ir_query.c` — `ir_value_is_null_string` gained `IR_IDENT`/`IR_DIFFER`: both are
  definitionally-null-on-success exactly like `IR_CMP_TEST` (`descr_identical`'s success writes NULVCL
  either way), so the existing `PRED(a,b) expr` copy-propagation recognition (`copy_prop.c`, the
  conditional-value idiom claws5's own `IDENT(mem[wrd]) 0` uses) now also fires for IDENT/DIFFER without
  the concat needing to materialize a real runtime call.
- `Makefile` + `bb_templates.h` — registered the two new template translation units.
- `src/templates/bb_ident.cpp` / `bb_differ.cpp` — new boxes, ONE mechanism shared by both members (the
  second file is the first with the final `jcc` polarity inverted, nothing else): a direct call to
  `descr_identical` (the exact function the slow path's `bn_identdiffer` already delegates to — zero
  semantic drift), replacing the by-name dispatch chain entirely. TEMPLATE-ONLY (`x86(...)` only), BOTH
  media (TEXT and BINARY share the same body — this is the whole point of `x86(...)`), zero `MEDIUM_*`.
  Both the ordinary (`op_sa`/`op_sb`/FRQ) and ZD (`op_zres`/ZOPQ/ZRES) addressing shapes are implemented.
- **Killswitch**: `SCRIP_IDENT_INLINE` (default on; `=0` reverts to the pre-slice by-name call path,
  `sx_call_named`), checked at `lower_snobol4.c`'s call site — cached-getenv, matches the codebase's
  existing killswitch idiom exactly.

## Verification

- **Correctness, broad**: `corpus/probe/ident_differ_inline.sno` (new, checked in with `.ref` from the
  live oracle) — 1-arg/2-arg IDENT/DIFFER over string/integer/null, same-type and mixed-type, plus the
  claws5 `IDENT(x) default` conditional-value idiom exercising a table's first-use-default pattern.
  Byte-identical to the oracle. A second, larger ad-hoc probe (19 statements covering every arity/type
  combination plus the nested-assignment/nullcat interaction) also matches byte-for-byte; not checked in
  separately since `ident_differ_inline.sno` supersedes it.
- **Killswitch control**: `SCRIP_IDENT_INLINE=0` on the same probe reproduces the pre-slice output
  exactly (confirms the fallback path is untouched and the bug fixes above were genuinely new-opcode-
  specific, not latent in the generic call path).
- **SNOBOL4 smoke**: 7/7 both modes (m3 `--run`, m4 `--compile`, HARD GATE).
- **Corpus** (`test_corpus_snobol4.sh`, post-rebase pristine build): m3 PASS=355 FAIL=2, m4 PASS=353
  FAIL=2 SKIP=2 (357 total) — **fail-set identical BY NAME** to the pre-existing baseline
  (`160_pat_alt_inner_gen_resume`, `demo_treebank` fail; `132_pat_fence_eps_recur_shallow`, `demo_porter`
  skip — all four pre-existing, unrelated to this rung).
- **Gates**: `test_gate_emit_no_lang.sh` OK. `test_gate_template_medium_invisible.sh`: 0 BOTH-MEDIUM
  sites in `bb_*.cpp` (ratchet ceiling 0, unmoved); the informational 8-site `xa_flat.cpp` baseline is
  pre-existing WIP debt, untouched.
- **M1 fixed point**: attempted (`beauty.sno < beauty.sno`, both modes) — **did not reproduce the fixed
  point, but confirmed via `SCRIP_IDENT_INLINE=0` control that the failure is byte-identical with this
  rung's change on OR off, i.e. pre-existing and unrelated to this row.** (`Parse Error` appears mid-output
  where the beautified `-INCLUDE` block should be; same failure with the killswitch forcing the pre-slice
  IDENT/DIFFER path.) Observed a sibling seat (`claude01`) independently investigating this exact
  `beauty.sno` self-host question concurrently (worktree at the M1 landing commit `1f6cea4d`, comparing
  MD5s) — flagging here as corroboration, not claiming the diagnosis; not this row's fix to make.
- **Performance** (RT_OPT=-O0, matching the s199 baseline's own label; clean oracle per the s255 ruling,
  `/home/resources/spitbol-clean/sbl -bf -s16m`; `corpus/benchmarks/snobol4/ident_call1.sno`/
  `ident_call2.sno`, new TIME-based micro-kernels checked in, same `harness.inc` the existing 15 kernels
  use — 1/2-arg IDENT added to `arith_loop`'s exact loop body, isolating the call the same way s199's own
  ablation ladder did): **m3:sbl throughput with one IDENT/DIFFER call added to the loop body is now
  1.68x–2.37x FASTER across 3 trials (never slower)** — the pre-slice baseline was **0.35x SLOWER**
  (a call that used to flip SCRIP from winning to losing now leaves it winning). Per-call cost
  (loop-subtracted) is very roughly 5–20ns post-inline against the pre-slice 121.55/126.12ns baseline (a
  ~6–24x reduction) — reported as a range, not a point figure: this session's heavy concurrent fleet load
  (multiple sibling seats mid-`make pristine` throughout) visibly adds noise to the bare-loop baseline
  itself across trials, so the throughput RATIO above (robust to a shared noise floor since both arms of
  each trial share it) is the citable number, not the absolute ns. `claws5.sno` re-measured for
  correctness (`check: 6469` both engines, piping `claws5.dat` on stdin) but NOT for throughput: the TIME
  harness's calibrate/measure phases call `ZBODY` repeatedly against a FINITE piped stream, so once
  `claws5.dat` is exhausted mid-run every further call is a nonrepresentative near-instant EOF no-op that
  dominates the reported `iters:` — the same class of harness confound named in
  `FINDING-2026-08-22-bench-harness-unmeasurable.md`. A trustworthy claws5 end-to-end number needs s199's
  own four-point single-pass ablation methodology (or a fixed-work `echo N |` invocation sized to one
  pass), not this harness's default repeating mode; out of scope to reproduce here given the isolated
  micro-benchmark already answers the mechanism-level question directly, and by s199's own decomposition
  IDENT/callouts are 6.5%+14.1% of claws5's total (table construction is 91.6%, untouched by this slice)
  so the isolated ratio above, not an end-to-end claws5 number, is what this rung's fix actually moves.

## Not done / follow-ons

- **`beauty.sno` self-host Parse Error**: confirmed pre-existing and unrelated (see above); not
  chased further since a sibling seat is already on it. If unclaimed by handoff, worth its own row.
- **System-function DEFINE/OPSYN protection**: SCRIP does not raise SPITBOL's ERROR 248 for
  DEFINE/OPSYN targeting ANY system function (not IDENT/DIFFER-specific — verified the same gap exists
  for the class generally, e.g. `OPSYN('IDENT','SIZE',0)` is silently accepted, not rejected). This is a
  pre-existing, broader gap (predates slice 1, unrelated to this rung's scope) that this rung's own
  redefinition research surfaced as a side effect. Worth its own row if HQ wants oracle-parity there;
  the fix would need a "closed list of protected names" (or a marker on the builtin registration) and
  touches the DEFINE/OPSYN runtime paths generally, not `IR_IDENT`/`IR_DIFFER` specifically.
