> STATUS 2026-09-09 (cto): NOT LANDED AND NOT MEASURED. The cure this FINDING describes sits unpushed at SCRIP tag `retired/wip-cto-define-alternate-entry-2026-09-09` (readable, never mergeable); the gate was never run on it. The row is PARKED-LON-HOLD on Lon's Icon-only order (CEO-445). Read the text below as the design record of a candidate, not as a claim.

# FINDING 2026-09-08 (cto, MODE NONET) — `DEFINE` binds per EXECUTION: each bind site seals its own entry, both modes

Row `snobol4-define-alternate-entry-binds-one-entry-for-the-whole-program` (hq_V's diagnosis, hq_B's runnable DONE-WHEN), ruled by the ceo as CEO-429: a name carrying more than one `DEFINE` in the program text dispatches INDIRECTLY, the by-name path a run-time `DEFINE` already takes, in both modes, and the by-name cell is POPULATED at bind time, never cleared. hq_V's FINDING-2026-09-08-hq_V-a-redefine-with-an-alternate-entry-binds-one-entry-for-the-whole-program.md holds the diagnosis and four measured dead ends; none of them is re-walked here.

## What was lost, at two sites

The lowerer already attached every bind node's own entry as a name operand (`sno_bind_attach_entry`), and `ir_define_bind_entry()` already read it. Nobody called it on the path that mattered.

1. **Mode 4, the driver's dentry table** (`src/driver/scrip.c`): for each bind node it resolved the entry BY FUNCTION NAME through `proc_table`, reaching the function's own graph, whose entry is a one-shot trampoline to the LAST-PARSED entry label. So every site sealed the same label into `body_cell$F` — the witness's assembly showed `lea rax, [rip + LBL__F_2]` at all three DEFINE sites and `body_cell$F: .quad LBL__F_2`. The table now prefers the bind node's own entry operand, resolving `LBL__<entry>` in `proc_table`, and falls back to the old walk only when that label is absent. The three sites now seal `LBL__F`, `LBL__F_1`, `LBL__F_2` and the cell's initial value is the FIRST bind's entry. The role-5 seal hq_V called unsatisfiable (label name from `dentry_name`, realstub from `dentry_entry`) is satisfied by the same change: both are set for a resolved operand.
2. **Mode 3, the activation and the trampoline** (`bb_define.cpp` role 4, `bb_goto_deferred.cpp` DEFINE-FOLD arm): the encoder ignores label names in mode 3 and uses numeric pointers, and both the role-4 shim and the trampoline jumped through the PER-LABEL cell `body$<static entry>`, which the driver fills once at slab time and which every `:(label)` goto shares — so it cannot be rewritten per binding. For a name bound more than once (counted from the main graph's bind nodes, nothing new stored) the driver marks the function graph's trampoline and role-4 shim with a name operand; both then jump through a PER-FUNCTION cell `fnbody$<FN>`; each bind site copies its own entry's address out of `body$<entry>` into `fnbody$<FN>` (the mode-3 twin of the mode-4 body seal); and the driver initialises `fnbody$<FN>` to the first bind's entry after the label cells are sealed. A single-`DEFINE` name emits exactly the bytes it emitted before.

Two things worth one line each so the next reader does not re-measure them. The marking must run BEFORE mode 3 emits the function graphs, which happen before the main graph — the first cut marked at the main graph and changed nothing. And the trampoline arm must key on a field that is SET OR CLEARED for every one-shot trampoline: the first cut keyed on the target-label field and filled it in `emit_drive`, which flat chains do not pass through, so the field was stale from the previous function's shim and single-`DEFINE` programs with two functions called an unsealed cell (`make test` went red on `sno_deferred_capture_keeps_the_name_save_stack_balanced`, four of ten gradings, mode 3 only). The fill now lives beside the generic prepare that sets the trampoline's role.

## Measured

- `scripts/test_gate_define_alternate_entry.sh`: RED both modes on `403a7cc0e`; GATE OK both modes after (three DEFINEs with alternating entries print `E0 v` `E1 v` `E2 v` `done`, the oracle's reading).
- Mode-4 assembly of the witness: the only lines that changed are the three seals and the cell's initial value.
- Looped-call cost (CEO-429 asked for it after landing): a 2,000,000-call loop on `F` once-defined vs twice-defined, same body — m3 0.0899 s vs 0.0893 s, m4 0.0860 s vs 0.0853 s. Multiple **1.0×** in both modes: the call path is the same activation and one indirect jump through a cell either way; the multiply-defined name reads a different cell, not a longer path.
- Control arms (shared node): SNOBOL4 master via `make test` (result in the baton ledger and cursor); Icon master **704/704 both modes, watermarks held**; snoflake **112/124 both modes**, unmoved from hq_V's readings on either side of the oracle swap.

## What it unblocks, and the residue that is a different class

`COPYL_driver` (gimpel, hq_B's one red in A–F) no longer overflows the stack: the self-re-`DEFINE` with an alternate entry now enters `COPYL_1`. It now stops with `ERROR 235 -- subscripted operand is not table or array`, and so does snoflake `gimpel-linked-list-functions`, for a reason this row does not own: `DEFINE('COPYL(L)T')` declares `T` local, the re-`DEFINE('COPYL(L)', 'COPYL_1')` declares NO locals, and SPITBOL's inner activation therefore sees the OUTER activation's `T` (dynamic scoping: a local is the global cell saved on entry and restored on exit; an activation whose binding lists no locals saves nothing). SCRIP still treats `T` as the inner call's own local, so `T<L>` reads a null. Minimal witness (oracle prints `memo via a` / `memo via b`, SCRIP raises 235 at the first call):

```
	DEFINE('F(X)T')				:(FEND)
F	DEFINE('F(X)', 'F1')
	T = TABLE()
	T<1> = 'memo'
	F = F(X)
	DEFINE('F(X)T')				:(RETURN)
F1	F = T<1> ' via ' X			:(RETURN)
FEND
	OUTPUT = F('a')
	OUTPUT = F('b')
END
```

That is the LOCAL LIST per binding: each `DEFINE` execution binds its own formals and locals, and the activation must save and restore exactly the list in force. It goes to hq_V's row `snobol4-gimpel-recursive-list-functions-overflow-the-call-stack-where-spitbol-completes`, which this landing unblocks, as its next cause.
