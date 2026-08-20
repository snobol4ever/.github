# FINDING s172 (seat8 `/home/claude8`, Claude Opus 5, queue row `m4-redefine-labels` = M1-R4b) — **THE DUPLICATE FACE WAS AN *EXACT* DUPLICATE, SO THE FIX IS EMIT-ONCE AND NOTHING ELSE MOVES: 527/527 `.s` BYTE-IDENTICAL, beauty_suite m4 15/17 → 16/17. AND THE ROW UNCOVERED A SECOND, DEEPER DEFECT THAT IS *NOT* A LABEL PROBLEM.**

**Front:** GOAL-SNOBOL4-100 · M1-R4b (row 8), cut by FINDING-2026-08-19-s171 RED-A. Baseline = origin HEAD `bf87289d`, built pristine in its OWN worktree/objdir (HQ-27). RT_OPT=`-O0` (FACT RULE O0-DEV). Oracle `x64/bin/sbl` present and used for every `.ref`.

## What was actually wrong
A function may legally be `DEFINE`'d more than once — plain SPITBOL, and the oracle runs both witnesses green. The role-5 TINY shim is emitted **inline at every DEFINE statement** (`emit.cpp:1239` dispatch) and spells its three faces from the function **name** (`bb_define.cpp:579`): `<FN>_α` / `<FN>_γ` / `<FN>_ω`. Two DEFINE statements for one name therefore emitted the same three symbols twice and `as` rejected the mode-4 `.s` outright — **every redefining program was m4-uncompilable**. m3 never reached the arm (it is `g_is_text`-gated), which is exactly why the class was invisible to the m3 board.

## The measurement that chose the fix — the duplicate is EXACT, not merely similar
s171 offered "site-unique labels **or** emit-once + rebind". Both are wrong-shaped once the emitted text is read, and the `.s` says which:

- **Site-unique labels cannot work.** The call site jumps to `<FN>_α` *statically, by name* (`bb_call_proc_staged.cpp:325` and `:598`). One name, one target — a per-site face has no caller.
- **The two shims are byte-identical modulo their per-instantiation `.Lx` ids.** Extracted both blocks from both witnesses' `.s` and normalized `.Lx<n>_` → `.LxN_`: **zero diff lines**, same faces, same body target. So "rebind" has nothing to rebind.

And that identity is **structural, not lucky**: the dentry stamp (`scrip.c:1345-1354`) resolves a DEFINE's body by looking the function up **in the by-name proc row**, and the lowerer keeps exactly **ONE** row per name (measured — `SCRIP_DEFCENSUS` instrument, since removed: `redef_twice` and `redef_lastwins` each yield rows `main`, one `LBL__…`, and a single `F`). Every DEFINE site of a name therefore stamps the **same** `dentry_entry`. The duplicate can never carry different content.

⇒ **The fix is emit-once.** One guard in the `emit.cpp:1239` bind dispatch: emit the role-5 face at the FIRST bind node of each name, skip it at later ones. Later sites keep their **role-6 bind untouched**, so the per-statement `rt_define_site` registration still happens at every DEFINE exactly as before. One line, no new global, no `bb_tiny_shim_ok` change, no registry change, m3 not reachable.

## Measured (pristine both arms; baseline is ORIGIN HEAD in its own worktree, never this tree)
| instrument | baseline `bf87289d` | after |
|---|---|---|
| `.s` blast, `util_s_md5_sweep.sh` | 529 programs, 527 comparable | **ZERO movers — 527/527 byte-identical** |
| corpus m3 | PASS=326 FAIL=11 | PASS=326 FAIL=11, **identical fail set** |
| corpus m4 | PASS=322 FAIL=13 SKIP=2 | **PASS=323** FAIL=13 SKIP=1, **identical fail set** |
| corpus fail-set diff | — | **exactly one line: `SKIP(compile/link) omega_driver` removed** |
| beauty_suite board | m3 17/17 · m4 15/17 | m3 17/17 · **m4 16/17** |
| `omega_driver` | m4 `as`-rejected | m3 **and** m4 byte-identical to the checked-in `.ref` **and** to the oracle |
| RULES step-4 regen | — | all five scripts **changed=0** (623 + 22 programs) — independent corroboration |
| gates | — | `emit_no_lang` ✅ · `template_medium_invisible` 5/ceiling 5 ✅ · `no_handencoded_bytes` ✅ |

The regen `changed=0` and the sweep's 0/527 are two independent instruments agreeing, which is what makes the byte-identity a **measurement** rather than an argument from construction.

## ⛔ THE SECOND DEFECT — LAST-DEFINE-WINS IS BOUND AT COMPILE TIME, AND IT IS *NOT* A LABEL PROBLEM (successor rung)
`redef_lastwins.sno` (minted here) DEFINEs `F` twice naming **different** bodies, with a call **between** the two DEFINEs — so it prices last-wins as the **runtime** fact SPITBOL says it is. Oracle: `first:a` / `second:b`. **SCRIP answers `second:a` / `second:b` — in BOTH modes, before and after this rung.**

Three things make this the right thing to hand on rather than to fold in:
1. **It is upstream of the faces.** One proc row per name means the row already holds the *last* body when the *first* call compiles. Curing it means the call must dispatch through `fn_cell$<FN>` at run time (the AB/cell road the slim arm already rides), not a static `lea`.
2. **It is not a mode-34 violation.** m3 ≡ m4, both `second:a`. Confirmed independently via the `SCRIP_NO_TINY=1` hatch: with the tiny shim refused the answer is *still* `second:a` in both modes, so the shim was never the cause.
3. **Fixing it inside this rung would have opened a mode-34 divergence.** A naive emit-once that bound the surviving face to the *first* body would give m4 `first:a` against m3's `second:a`. The landed guard does not do that — it dedupes a provably identical block, so it cannot move either mode.

Witness is checked in **known-red with the oracle `.ref`**, in `corpus/probe/redef/` — outside the crosscheck harness feed and outside `util_s_md5_sweep`'s default list, so it gates nothing.

## ⛔ A THIRD, ADJACENT CLASS FOUND WHILE CENSUSING — PRE-EXISTING, NOT THIS ROW
`probe/ab_expr_define.sno` fails to LINK in m4: **`undefined reference to ep_α`**. **Verified pre-existing at baseline `bf87289d`** (same failure, same symbol, baseline binary) — it is *not* a regression from this rung. The name is DEFINE'd exactly once, in **expression** position (`DIFFER(DEFINE('ep(ep)','ep_body'))`), which mints no dentry bind node and hence no role-5 face, while the call site still emits the tiny `jmp ep_α`. That is a live counter-example to the s59 ONE-AUTHORITY promise that *"a jmp `<fn>_α` can never dangle"*: `bb_tiny_shim_ok` admits the site on the strength of the runtime proc registry, which the lowerer's `sno_prescan_expr` hoist populates for expression-position DEFINEs, but the face is only ever emitted from the statement path. The witness's own header already predicted the shape for the AB block; this records that the **tiny face has the same hole**. Not minted as a row here — flagged for HQ to route.

## Census — how wide the class actually is
1911 corpus programs scanned for a name DEFINE'd more than once: **9 hit**, and only the *statement-position* ones can emit a duplicate face. `crosscheck/rung10/1011_func_redefine.sno` and `probe/ab_expr_define.sno` redefine in *expression* position and are correctly unmoved (both appear in the sweep with identical md5s). The gimpel trio (`PERM`, `PERMS`, `COPYL` — three DEFINEs each) and `csnobol4-suite/diag1.sno` are the rest; `diag1` still fails to lower in BOTH modes for an unrelated, pre-existing reason (pattern matching outside the landed subset).

## Ladder impact
**M1-R4b is DONE.** M1-R5 (`beauty-fixed-point`, row 7) now has exactly **one** beauty_suite m4 defect left in front of it — `semantic_driver`, which s171 already routed to row 4 (seat6) as the R1-class witness. m3's suite tail remains ZERO. Nothing in this rung touches R2/R3/R4.
