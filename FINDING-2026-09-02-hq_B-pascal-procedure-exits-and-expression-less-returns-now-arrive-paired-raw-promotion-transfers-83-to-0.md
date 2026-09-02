# FINDING 2026-09-02 (hq_B) — Pascal procedure exits and expression-less returns now arrive at the promotion site with a paired rax:rdx; the RAW promotion-transfer population went 83 → 0 on the post-cut tree, and quick.pas's m4 checksum came right with it

**Tree:** SCRIP `d754df54` (on hq_C's cut `db299d41`, ceo's `5934802b`, hq_P's quad gate `9623ff55`) · corpus `5c47e247` · `RT_OPT=-O0` · MODE `TRIO` (file read). Row `port-exit-value-contract-untagged-rax-forges-dt-fail`, steps 2 and 3 of its NEXT; obligation 1 (the refusal) is still open and is now landable.

## The population, before and after

| tree | RAW | where |
|---|---|---|
| pre-cut `48b09e04` | 223 in 31 of 171 programs | Prolog 140 (the continuation `lea`s the cut deleted), Pascal 77, Icon 6, SNOBOL4 0 |
| post-cut `76ebd5f2` | 83 in 15 of 146 | Pascal 77, Icon 6, Prolog 0 (every program above rung 0 refuses at compile) |
| **this landing** | **0** over 106 Icon + Pascal programs, 342 transfers all OK_PAIRED | — |

## ⭐ Why the "safe" literal never worked, and what does

`lower_pascal_proc` already planted a `LIT_INTEGER 0` as every procedure body's γ — someone had tried to normalize the exit before. It could not work: **an ordinary value node writes its DESCR into its own slot, never into rax:rdx.** The optimized IR still carried the node (relop ω → literal → SUCCEED) and the emitted code still read `cmp rax, rcx; jge qsort_γ` — the literal box contributes nothing to the registers the promotion site forwards. The one box that DOES load rax:rdx before a γ is `IR_RETURN` (`bb_return.cpp`: `mov rax, FRQ(op); mov rdx, FRQ(op+8); mov FRQ(0), rax; mov FRQ(8), rdx; γ`), and the FUNCTION arm of the same lowering already used it (`IR_VAR(fname) → IR_RETURN`). The cure is one line: the procedure arm mirrors the function arm with the literal as the return's operand. Every last-statement port — a relop's false ω, an int-returning relop γ (`rt_relop_overload`, `rt_jct_relop`, `rt_add`), an unpaired operand load — now lands on the literal, then the return's paired load, then the exit.

The Icon six were all Icon's expression-less `return`: `bb_return`'s no-operand arms stored `DT_SNUL`/0 into FRQ(0)/FRQ(8) and left rax alone. They now reload rax:rdx from the slots they just wrote — a paired load the scanner and the future live classifier both recognize, in both the flat and the ZD arm.

## Control arms (the return box is a shared node)

| arm | reading |
|---|---|
| SNOBOL4 board | m3 1679/0 · m4 1679/0 SKIP=0 · GATE OK (`make test` green) |
| Icon all-rungs | PASS=263 FAIL=6 BADEXIT=1 of 297, failure set identical to the pre-cure baseline; Icon smoke 14/14 both modes |
| Pascal m3 / m4 gates | master 148/1 both modes, unchanged — the 1 is `program_procedure_nested_1` bombing `PAS-DISPLAY L>=4 fallback unimplemented`, reproduced on the untouched baseline (stash, rebuild, run) |
| `quick.pas` | m4 prints `-50000 15505` = m3 = ref — the `pascal-quick-m4-wrong-checksum-crash-masked` witness (noted on that row; its gate conjunct still carries the display-depth red) |
| Prolog | ladder `--to 0` PASS 2/2; trace gate `--to 0` PASS(0); the smoke's 4 reds are rung refusals (`rc=2 … rung 2 lands it`) |
| `test_gate_port_exit_value_contract.sh` | GATE PASS(0), 18 exits, emitter chokepoint 21 / TEXT scan 21 |
| hygiene | strip_comments 0; emit_no_lang, no_handencoded_bytes, template_medium_invisible OK |

**What remains on the row:** obligation 1 — the unconditional generation-time refusal (seat13's forward-classify design, the field Lon granted) — which on this tree would refuse nothing, plus the gate's fail-once arm and the contract sentence (obligation 3). The baton's NEXT names the order.

**Receipts:** SCRIP `d754df54`, corpus `5c47e247` (9 Icon bench `.s` regenerated), the row's ledger.
