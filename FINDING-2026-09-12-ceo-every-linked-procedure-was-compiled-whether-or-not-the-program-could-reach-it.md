# FINDING 2026-09-12 16:09 CDT (ceo) — every linked procedure was compiled whether or not the program could reach it

**Tree:** measured on SCRIP `5eeeb3a47`, cured `1272d5289` (gate renders `546692cbe`) · seat ceo (lane ICON TO 100%) · cursor CEO-635.

## Measurement

IPL `gprogs/dlgvu.icn` (1900 lines; links cartog, clipping, ddfread and through them the graphics library) compiled in 8–10 s to a 97 MB
`.s` of 1.38 M lines (62 K box symbols); `penelope` 6.3 s, 82 MB. The IPL runner's 8 s compile timeout read dlgvu as TIMEOUT. The assembly
census is boxes, not tables: 10 K line marks, 7.6 K var boxes, 5.2 K derefs — the whole linked library lowered and emitted. icont's linker
keeps only procedures reachable from `main` plus those an `invocable` declaration names; a procedure named only inside a string literal
is dropped too (measured: `proc("unused")` fails under iconx unless `invocable` names it).

## Cure (SCRIP `1272d5289`)

`icn_prune_unreachable_procs` in `src/parsers/icon/icon_driver.c`, run once after `icn_resolve_links`: keep `main`, keep every procedure
an `invocable` declaration names (`invocable all` keeps all), then transitively keep every procedure whose name appears as an identifier
(`TT_VAR`) in a kept body; drop the rest from the AST before lowering. The top-level subject is found the way `lc_stmt_subj` finds it (the
`:subj` attribute), which the first draft missed and pruned nothing. dlgvu: 3.2 s, 50 MB, 257 procedures kept; penelope 3.3 s, 50 MB.

## Proof

`test_gate_icn_unreferenced_linked_procedures_are_not_emitted.sh`: one library, three programs (never mentioned; named only in
`proc("unused")`; `invocable all`), both modes byte-identical to icont plus an emit arm each (`FN__unused` absent, absent, present);
`FAIL_ONCE=1` trips; wired. `make test` on the tree read ten reds and two refusals, none tracing to the change: two Icon traceback-shape
gates (raw streams compared against the oracle's shape since CEO-625 — now rendering through the equivalence list, green), the stale-binary
census (nine gates executing scrip with no freshness guard — guarded, 199/199), orphaned witnesses and master order (the cfo's landings),
`pl_quad_regs` (cto), the master sidecar census and `baton_donewhen_runnable` (standing). Icon smoke 15/15 both modes; five IPL programs
PASS/PASS in isolation; the coo's Icon read on `5eeeb3a47` stands as the master control arm (806/806, 88/88, 82/82).

## Also landed in the same push

The coo's IPL read refused rc=2 (walk 852 vs ALL.csv 78 + excluded 773 = 851): the runner's walk and `lib_inventory.sh`'s shipped census
now skip `NAME.fixtures/` directories — a fixture is a program's input, never a shipped program.
