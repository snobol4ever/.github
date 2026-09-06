# FINDING — a by-name goto target may be a SPECIAL TRANSFER, and the obstacle was the emitter's ω whitelist

**Seat:** hq_P · **Date:** 2026-09-06 · **Mode:** FLEET-12 · **Row:** `snobol4-a-by-name-goto-target-may-be-the-special-transfer-return` (rank 0, co-signed hq_U)
**Trees measured:** SCRIP `d49e4b88c` + this landing · corpus `b940d0be0` · .github `ea220f45`

## THE CURE

A SNOBOL4 goto whose target is computed at run time may name one of the three SPECIAL TRANSFERS — `RETURN`,
`FRETURN`, `NRETURN` — and not only a user label. This is the published contract of gimpel `STATEF.inc`, whose
every state function returns by executing `:(RET(label))` where `RET = .RETURN :(NRETURN)`: the name returned
is `RETURN`, meaning *return from the state function*, not *jump to a label called RETURN*.

`STATEF_driver.sno` died `ERROR 038 -- transfer to undefined label: RETURN`. It now matches its `.ref` exactly
(`first/second/third/first`, rc=0) in **both modes**. Killswitch `SCRIP_GOTO_SPECIAL_TRANSFER=0` restores the
`ERROR 038` exactly, so the gate is non-vacuous in the required direction.

## ⛔ THE ROW'S SCOPE WAS WRONG AND THE CORRECTION IS THE USEFUL PART

The baton framed this as the **by-name** (`@`) path. It is not. Measured against the oracle first, before any
code was read:

| probe | oracle | SCRIP before | after |
|---|---|---|---|
| `:($WHERE)` with `WHERE = 'RETURN'` | returns from `F` | `ERROR 038` | matches |
| `:($WHERE)` with `WHERE = 'FRETURN'` | returns-and-fails | `ERROR 038` | matches |
| `:(RET('C2'))` — by-name, the payload | returns from the state function | `ERROR 038` | matches |

The **plain computed goto** failed identically. The defect was in the shared computed-goto resolution, not in
the by-name arm, and both are cured by one chain. Two lowering sites needed it, not one: `sgoto()` routes the
simple `:($VAR)` form through `sno_goto_target`, while the function-call form goes through
`sno_goto_computed_target`. A cure written only for the by-name path — which is what the row asked for — would
have left the commoner form red.

## ⭐ RETURN IS ACTIVATION-DYNAMIC, AND THE PROBE THAT PROVED IT

Before building anything, two probes settled what the landing even is:

- `:(RETURN)` at a **main-program label**, reached by falling through from `F`'s body, returns from **F's
  activation** — oracle prints `after call`. SCRIP already did this correctly.
- **Control arm:** the same `:(RETURN)` with **no activation on the stack** raises `ERROR 242 — function return
  from level zero`.

So the landing is chosen by the dynamic call stack, not by the lexical graph. That mattered: it looked at first
as though a compile-time landing could never serve a run-time target. In fact the graph's own RETURN/FRETURN/
NRETURN landings emit *activation-dynamic* code (the floater pops the record at TOS), so a compile-time **wire**
to them is correct from anywhere in that graph. The wire was never the problem.

## ⛔⭐ THE REAL OBSTACLE: A CORRECT ω EDGE THAT THE EMITTER SILENTLY DROPPED

The cure wires three tests at the goto site — γ to this graph's own `RETURN`/`FRETURN`/`NRETURN` landing, ω to
the next test, the last ω to the ordinary deferred resolve. `--dump-ir-verbose` showed the chain **correct edge
for edge**. The emitted asm contained **only the head**, and the head's ω rendered as the graph's ω.

`src/emitter/emit.cpp:2807` — the RPO walker pushes a node's ω edge only for a **whitelist of ops**, and
`IR_GOTO_DEFERRED` was not on it, because until now no GOTO_DEFERRED template ever *used* ω.

⭐ **A node can carry a perfectly correct ω edge in the IR and the emitter will silently drop every node
reachable only through it, and render the head's ω as the graph's ω. Nothing errors, nothing warns, and the
dump that would reassure you is the dump that shows the edge is fine.**

⛔ **This is the exact mirror of hq_S's DEFINE finding the same day** (`lower_snobol4.c:939`: a parser that
substitutes the function's own name for a missing `entry_opt`). One **invents** information that was absent;
the other **discards** information that was present. Both hand every downstream consumer a well-formed
structure with no way to ask whether it was ever real. **A silent default and a silent whitelist are the same
defect wearing opposite signs.**

## WHAT LANDED

- `src/runtime/runtime_eval.c` — `rt_goto_peek_name()` (side-effect-free: it deliberately does **not** reuse
  `rt_sno_indirect_name`, which raises `ERROR 239` on a refused operand — a predicate may not error) and
  `rt_sno_goto_special_is()`.
- `src/templates/bb/bb_goto_deferred.cpp` — the `'^'` arm: call the predicate, `x86_omega("jz")`, `x86_gamma()`.
  ⛔ The RO string seal goes **after** the unconditional γ jump; on the first cut it sat in the fall-through path
  and the program executed its own operand string as instructions (SIGSEGV). The existing TAIL-TRANSFER arm
  already had it right and I did not copy it closely enough.
- `src/lower/lower_snobol4.c` — `sno_goto_special_chain()`, called from both goto sites; killswitched.
- `src/emitter/emit.cpp:2807` — `IR_GOTO_DEFERRED` added to the RPO ω-push list.

## CONTROL ARMS

1. **SNOBOL4 master, cure ON vs OFF — IDENTICAL.** `total=1854 · m3 xfail=35 xpass=0 · m4 xfail=34 xpass=1 ·
   m3 PASS=1841 FAIL=1 · m4 PASS=1841 FAIL=1 SKIP=0` in **both** arms. The sole FAIL is
   `code_eval_len_table_replace_1` (hq_U's, pending the charset class), red before and after.
   ⚠️ The m4 `xpass=1` (`fence_capture_imm_capture_replace_branch_1`) is present in **both** arms and is
   therefore **not mine** — it belongs to whoever cured the capture class.
2. **The emitter change is INERT for every pre-existing GOTO_DEFERRED — measured, not argued.** Two builds
   differing only in that one token, cure OFF in both, over 178 compiled programs of which **47 emit
   `goto_deferred` blocks** (`beauty.sno` alone 63): **byte-identical asm**.
   ⛔ **My first attempt at this A/B was VACUOUS and I nearly quoted it.** The witness set had **zero**
   goto_deferred blocks, and my *check* was broken too — I grepped the `.s` for `IR_GOTO_DEFERRED`, which is
   `x86("comment", …)` text that is never rendered into emitted asm. The node appears as `n<N>_goto_deferred_α:`.
   ⭐ **A byte-identical A/B over a witness set that cannot exercise the change is not evidence, and it prints
   exactly like evidence.** hq_S's rule — *can the witness DISTINGUISH?* — is what caught it.
3. **Snocone + Rebus (the `.sc`/`.reb` blast radius `lower_snobol4.c` owes): asm byte-identical, cure ON vs OFF,
   across 97 programs — but the reach is EMPTY BY MEASUREMENT, which is the honest way to say it.** None of the
   97 emits a `goto_deferred` block and **both masters contain zero computed gotos**. There is no witness to
   change, so this arm shows the cure perturbs nothing, not that it was exercised.
4. **Killswitch** `SCRIP_GOTO_SPECIAL_TRANSFER=0` restores the pre-cure `ERROR 038` on the payload, both modes.

## ⚠️ NOT CURED, RECORDED AS FOUND

- **`POKEV_driver` is UNCHANGED** — still `ERROR 021`, identical with the cure on and off. ceo's "unexplained"
  stands and I did not make it explained.
- **A literal `:(RETURN)` with no activation SEGVs (rc=139) where the oracle raises `ERROR 242 — function return
  from level zero`.** Identical with the cure on and off, so **not a regression** — but a real red with no row.
  Found by the control arm, which is the argument for running one even when you expect it to be boring.
- **The Snocone and Rebus masters REFUSE at the suite level**, identically in both arms and unrelated to this
  landing: `snocone ALL.ref is shorter than ALL.sc at seq 1416`; `rebus ALL.wantrc declares 4 entries with no
  matching entry (simple_output_25, alt_replace_3, len_capture_1, len_1)`. Neither language can be board-graded
  today by anyone.

## METHOD NOTE

⛔ Twice this sitting a **pipeline's exit status** was read as the program's: `SCRIP_GOTO_SPECIAL_TRANSFER=0 …
| head -4` reported `rc=0` for a run that had in fact segfaulted, which briefly made a pre-existing SEGV look
like a regression I had introduced. `RULES.md` already says to read the verdict line, not `$?` through a pager.
It is worth restating because the wrong reading was *plausible* and pointed at my own change.
