# FINDING-2026-08-02f — A-2 ZD-7c LANDED, GE-0 GOTO-ERAD CENSUS (s23r)

**Session:** s23r (2026-08-02, Claude Sonnet 4.6)
**Parent SCRIP:** `a3109d87` (OMEGA's O-1 IR_STATEMENT admission)
**A-2 commit:** `149462ef`

---

## §1 A-2 ZD-7c USER-PROC ARM — LANDED

**Gate:** ZD-7c user-defined proc admission in `zd_wl_kind` (emit.cpp:1889) + ZD arm in `bb_call_proc_staged.cpp`. Killswitch `SCRIP_ZD_PROC=0`.

**Design:** `bcps_det_arm()` gains `if (_.op_zres)` early-return path:
- Args read via `ZOPQ(k,0/8)` before any RSP-shifting (save-block or otherwise).
- For SCC path: args staged via `rt_arg_stage(i, ZOPQ(i,0)/ZOPQ(i,8))` BEFORE `sub rsp, scc_sb` — so ZOPQ offsets are valid; after the save block, args installed from `g_call_args[i]` via GOT-lea into GVA slots.
- For fused-open / DC paths: `lea argreg, ZOPQ(k,0)` (cell address delivery, same XK_RSP route as bb_cmp_test/bb_coerce_numeric).
- For dyn/non-fuse: staged via `rt_arg_stage` loop before open call.
- Result writes: `ZRES(0)/ZRES(8)` from `rax:rdx` post-epilogue.
- Generators stay DECLINED: suspended activation state (retained RSP frontier, pcall record) is incompatible with ZD cell model — callee may resume at arbitrary RSP depth, making emit-time op_zread differences invalid at resume.

**Gates all green:**
- 085/086/087 PASS (the named naive-admission falsification controls flip green)
- Bench board 18/21 EXACT HOLD — roman + eval pair = pre-existing residue
- Crosscheck 318 BY SET IDENTICAL both modes (m3 280/27/10 · m4 268/37/10/2L — flicker accounts for count delta vs s23q record 266/39; zero P→F zero F→P by program-level diff)
- `SCRIP_ZD_PROC=0` restores pre-edit behavior byte-identical (BY SET verified)

---

## §2 GE-0 GOTO-ERAD CENSUS (read-only, per the ALPHA ladder)

**Directive:** Lon s23q: "eradicate the usage of IR_GOTO completely. It is useless."

### 2.1 Corpus-wide emitted counts (318-program crosscheck, fresh compile)

| Form | Boxes emitted | Programs | Notes |
|------|--------------|----------|-------|
| IR_GOTO (static-label) | **904** | 250 of 318 | `bb_goto.cpp`: `x86_alpha() + x86_pair_loop()` — a label + bare jmp, exactly what the γ/ω wire edge already implies |
| IR_GOTO_DEFERRED | **75** | ~20 | `bb_goto_dyn.cpp`: EVAL/CODE runtime label transfer — NOT in scope for eradication (different kind, already admitted K=0, protocol box) |
| IR_GOTO_INDIRECT / IR_INDIRECT_GOTO | **0** | 0 | Retired (slice 3, zero producers — emit.cpp:1024 note) |
| IR_MOVE_LABEL | present | present | Not an IR_GOTO; handles direct `:<VAR>` Code block entry |

**Total IR_GOTO (static-label) target: 904 boxes, 250 programs.**

### 2.2 Declined-run first-blocker count

Running SCRIP_ZD_DIAG=1 across all 318 programs:
- **Total declined runs: 377**
- **IR_GOTO first-blocked runs: 70 (18.5%)**

The ALPHA cursor quoted 68/433 = 15% from the s23q measurement at parent `bed92446`. At HEAD `a3109d87` with A-2 ON, 70/377 = 18.5%. The denominator shrank (A-2 admitted more runs) and the IR_GOTO count is stable — meaning GOTO IS NOW THE TOP RESIDUAL NOISE SOURCE after A-2.

### 2.3 Three SPITBOL GOTO forms (SPITBOL manual ch.14, confirmed)

Per the parent ALPHA ladder's carve-out documentation and manual §14 "Goto Field":

| Form | SPITBOL syntax | Lower-time target known? | Eradication path |
|------|----------------|--------------------------|------------------|
| **Unconditional static** | `:(LABEL)` | YES | **Wire-fold** — γ/ω edge already is the jump; box is a trampoline no-op. GE-3 lower-side (OMEGA file) + GE-8 emitter sweep (ALPHA file) |
| **Indirect** | `:($('VAR' N))` | NO — computed at runtime | **KEEP** — `bb_goto_dyn.cpp` via `rt_goto_transfer`; NOT IR_GOTO kind, it's GOTO_DEFERRED |
| **Direct** | `:<VAR>` | NO — CODE() block | **KEEP** — `bb_move_label.cpp` / IR_MOVE_LABEL; handles CODE() block entry label |

**The 904 IR_GOTO boxes are ALL the static-label form.** The indirect and direct forms are ALREADY different IR kinds (IR_GOTO_DEFERRED and IR_MOVE_LABEL respectively) and are not touched by GOTO-ERAD.

### 2.4 Lowerer site count by language (IR_GOTO build calls)

| Language | Sites in lowerer |
|----------|-----------------|
| snobol4 | 23 |
| icon | 24 |
| prolog | 8 |
| raku | 7 |
| pascal | 10 |
| **Total** | **72** |

These 72 lowerer sites produce the 904 emitted boxes (average ~12.5 per site — most are in loops/conditionals).

### 2.5 Monitor-tap prerequisite (GE-1)

The parent ladder's GE-1 notes: monitor taps are hung on goto nodes for the 2-way IPC monitor. `emit.cpp:997` shows: `if (_mon && g_emit.op_stno > 0) emit_mon_label_tap(g_emit.op_stno)`. This must be relocated before the node type is removed. GE-1 is a prerequisite — do it first.

### 2.6 `zd_chase` already treats IR_GOTO as transparent

`emit.cpp:2609` (optimizer/dead_goto pass): `case IR_CONJUNCTION: case IR_GOTO: return 0;`

And `zd_plan`'s chase: `while (t->op == IR_GOTO) t = t->γ.node` — the planner NEVER makes IR_GOTO a run member and NEVER stages one. This confirms: deleting IR_GOTO from the IR cannot break ZD staging.

### 2.7 Sizing

- GE-0 (this census): DONE — 904 boxes, 72 lowerer sites, 18.5% declined-run noise, three-form split confirmed, monitor-tap prereq identified.
- GE-1 (monitor tap relocation): OMEGA's file territory (`src/lower/lower_snobol4.c` has the stno-stamping); ALPHA executes GE-0 and GE-8 only per contract §1.
- GE-3 (SNOBOL4 lower-side, 23 sites): OMEGA file → CROSS-FRONT REQUEST.
- GE-8 (emitter sweep, ALPHA regions in emit.cpp): `case IR_GOTO` at line 997 minus the monitor tap = `bb_emit_x86(bb_goto())` — the whole box is `x86_alpha() + x86_pair_loop()`, a label + jmp chain. Deleting this case and the template after GE-3 resolves all producers.

