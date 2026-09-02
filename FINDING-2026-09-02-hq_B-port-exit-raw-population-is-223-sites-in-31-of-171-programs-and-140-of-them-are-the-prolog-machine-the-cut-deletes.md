# FINDING 2026-09-02 (hq_B) — the port-exit RAW population, measured across all four languages for the first time: 223 sites in 31 of 171 programs, SNOBOL4 0, Pascal 77, Icon 6, Prolog 140 — and the 140 are the control machine the rung-0 cut deletes, so obligation 1's unconditional refusal is BLOCKED-ON the cut, not on a grant

**Tree:** SCRIP `48b09e04` · corpus `d0351a54` · `RT_OPT=-O0` · MODE `TRIO` (file read). Row `port-exit-value-contract-untagged-rax-forges-dt-fail` (rank 0; Lon lifted its last governance gate 2026-09-02 14:34Z — *"You can always add as many g_emit values as you want"*). Instrument: the row's own `scripts/port_exit_value_contract_scan.py` with the DESCR-returning allow-list derived from `src/` exactly as `test_gate_port_exit_value_contract.sh` derives it. Population: 171 programs that compile to mode-4 text — all 69 `benchmarks/pascal` + `tests/pascal`, 37 Icon (`benchmarks/icon` + `demos/icon`), 25 Prolog (`demos/prolog` + `benchmarks/prolog/vanroy`), 40 SNOBOL4 (`benchmarks/snobol4` + `demos/snobol4`). Command in the baton's NEXT block; ~3 minutes.

## The number

| verdict | count |
|---|---|
| OK_PAIRED (rax:rdx from `[base+off]`/`[base+off+8]`) | 274 |
| OK_CALL (a DESCR-returning call) | 70 |
| UNKNOWN (block reachable only by jump — the scanner refuses to guess) | 77 |
| **RAW (untagged value in the tag register at a promotion transfer)** | **223, in 31 programs** |

| lang | shape | RAW | example |
|---|---|---|---|
| prolog | `lea rax,[rip+n<k>_call_proc_staged_β]` / `[rip+n<k>_call_prolog_α]` then `jmp <pred>_γ` — a CODE ADDRESS in the tag register | **138** | `crypt.pl`:8495 → `sum/3_γ` |
| prolog | `rax<-eax` computed | 2 | `family_prolog.pl`:25113 → `main_γ` |
| pascal | `rax<-[rsp+N]`, rdx not paired (relop fast-path operand), jcc onto the proc γ | 30 | `fbench.pas`:7694 `jg` → `tracexline_γ` |
| pascal | `call rt_relop_overload` (int) then `cmp eax,1; je <proc>_γ` | 24 | `fbench.pas`:7714 |
| pascal | `call rt_jct_relop` (int) then `test eax,eax; jz <proc>_γ` | 18 | `fbench.pas`:7729 |
| pascal | `call rt_add` (int) then jcc → γ | 5 | `pb31.pas`:484 → `statement_sim_γ` |
| icon | `rax<-[rsp+N]` unpaired then `jmp <proc>_γ` | 4 | `tgrlink.icn`:1222 → `loadfile_γ` |
| icon | `call rt_scan_sync_in` (int) then `jmp` → γ | 2 | `rsg.icn`:1195 → `define_γ` |
| snobol4 | — | **0** | the prepass admits zframe graphs and icn_cells procs only; no SNOBOL4 DEFINE body is a promoting label today |

## ⭐ What the number decides

1. **Obligation 1 cannot land before the cut.** The ruling makes the check an UNCONDITIONAL generation-time refusal, and INSTRUMENT LAWS clause 1 forbids landing it default-OFF. On this tree it would refuse 31 corpus programs; 140 of the 223 sites are the Prolog control machine — the `call_proc_staged_β` / `call_prolog_α` continuation addresses `lea`'d into rax before a predicate's γ — that `RULES.md` § THE PROLOG REBUILD GATE clause 1 deletes in rung 0. Curing them is work on code being deleted; refusing them before the cut takes away the rebuild's own Prolog baseline. The row is parked `BLOCKED-ON:prolog-rung-0-the-cut-and-hello-world-with-zero-globals`, the self-clearing spelling, so the picker un-parks it the moment rung 0 is DONE.
2. **The Pascal 77 are one lowering shape, not 77 sites.** Every one is "a statement's ω, or a relop's int-returning γ, wired straight onto the procedure's own γ because nothing follows it" — the same mechanism seat09 GDB-traced on `quick.pas`. A procedure body needs an explicit exit node (null DESCR for a PROCEDURE, the result-variable load for a FUNCTION) that every last-statement port wires into. One `lower_pascal.c` change, graded by the scanner reading 0 RAW over `benchmarks/pascal` + `tests/pascal` and by `quick.pas` m4 output matching its ref.
3. **The Icon 6 are per-site reads**, three procedures in two programs plus one demo; `return`-less ends or a `return e` whose value load skips rdx. The Icon all-rungs board (`PASS=263 FAIL=6 BADEXIT=1` of 297 on this tree, identical failure set) is the control arm.
4. **SNOBOL4 is not in the population** because its DEFINE bodies are not promoting labels under today's prepass — a fact about the instrument's scope, not a certificate. When SNOBOL4 functions join the promoting set, the scan must be re-run over the board, not assumed clean.

**Receipts:** the row's baton (NEXT block carries the table and the reproducible command); QUEUE.tsv state `BLOCKED-ON:prolog-rung-0-the-cut-and-hello-world-with-zero-globals`.
