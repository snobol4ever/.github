# HANDOFF — 2026-06-28 — Claude Sonnet 4.6 → Next Session
## GOAL: GOAL-IR-IMMUTABLE-EMIT (JCON wholesale Icon conversion; climb-the-rungs-with-conversion)

---

## PUSHED STATE

**SCRIP:** local HEAD `ec3bd5b3` on `main` — **PUSH PENDING, credential needed; handoff INCOMPLETE until pushed (RULES.md).**
**`.github`:** this doc + goal watermark — pending same push.
**Heartbeat (the entire gate per STANDING DIRECTIVE):** `write("hello world")` → `hello world` and
`write(1 + 2)` → `3`, both green mode-3 + full mode-4 cycle. Verified after every change.
**Strategy ratified by Lon this session:** climb the rungs in dependency order, converting each IR
faithfully from the JCON source as we reach it, with the heartbeat as the only check — **NO GATES**, no
full regression, no artifact regen. SCRIP keeps its own names (Greek ports α/β/γ/ω, `bb_*` templates,
`[r12+off]` slots, `nd->tmp`); JCON is a SEMANTIC reference only, never lexical.

---

## THE JCON CONVERSION MODEL (confirmed this session by reading the real source)

- `refs/jcon-master/tran/irgen.icn` `ir_a_<X>(p, st, inuse, target, bounded, rval)` = the LOWER side
  (`lower_icon.c` analog). `ir_init(p)` assigns FOUR labels (start/resume/success/failure); the body is
  wired by `suspend ir_chunk(label, [Goto(...)])` — explicit edge threading. `ir_tmp(st,inuse)` = a value
  temp (`nd->tmp`); `ir_value` decides fresh-tmp vs write-to-target.
- `refs/jcon-master/tran/gen_bc.icn` `bc_gen_ir_<X>(s, p)` = the TEMPLATE side (`bb_*.cpp`). `bc_gen`
  (line 822) = the dispatch (`emit_drive_node` switch). A value temp → JVM local `bc_tmp_table[name]+off`;
  SCRIP → `[r12+off]` via `nd->tmp`.
- **KEY REALIZATION: SCRIP already owns the 4-port→2-label reconciliation** inside `codegen_flat_chain_body`
  (`emit_bb.c`): it walks the γ/ω edges and binds each to the correct per-node α/β label. So where JCON emits
  `ir_chunk(left.success,[Goto(right.start)])`, the SCRIP-native form is just LOWER setting `left.γ = right`.
  **The center of gravity of the conversion is LOWER setting γ/ω edges + operand tmps per JCON's threading —
  NOT the templates** (which are already clean slot-readers). Every prior failed attempt died in slot/edge
  wiring, never in a template.
- start→α, resume→β (both in `IR_t`), success→γ, failure→ω (both `IR_ref_t` edges in `IR_t`).

---

## WHAT LANDED THIS SESSION (3 SCRIP commits)

### `0c6bbf94` — universal driver owns IR_RETURN (a complete, clean rung)
JCON has no `bc_gen_ir_Return`: `ir_a_Return` (irgen.icn:867) lowers `return E` to evaluate E into a tmp
then `ir_Succeed(t, /*no resume*/)` (a bounded return). SCRIP keeps a dedicated `IR_RETURN` node +
`bb_return.cpp` template, and **`walk_bb_node` (emit_core.c:449) ALREADY drives it correctly** for the
descr-flat-chain: reads `operands[0]`'s value slot via `bb_slot_get`, sets `op_sa`/`op_dval`, emits
`bb_return()`. The universal driver just lacked a `case IR_RETURN` — so it fell to `drive_unowned` ([SMX]).
Added `case IR_RETURN: DRIVE_FILL(...)`. `DRIVE_FILL` ≡ the old `FILL` macro byte-for-byte, so this
reproduces the prior descr-chain RETURN path exactly. **Verified:** `proc f(); return 7; end` compiles its
body with `# IR_RETURN` in the `.s`; SMX count for op=14 is now 0.

### `4a308ca2` — D1-CALL step 1: Icon calls take the flat-operand path (names survive the union)
`lc_call_argblks` (lower_common.c:230) does `IR_LIT(call).dval = dv` then builds arg subgraph blocks that
are **discarded** (`(void)(blks)` — the smuggle was killed in RUNG #1). Post-union, `dval` shares storage
with `sval`, so that one write **CLOBBERS the call name**. Effect: the inner `f()` in `write(f())` lost its
name; `resolve_call_kinds_descr` (emit_bb.c:3728) then read `.sval` back as the double bits
`0x4008000000000000` (= 3.0) as a `char*` and deref'd `fn[0]` → SEGV.
Fix (lower_icon.c:101): `int subgraph = !chains && is_idx_or_list;` — only `[]`/`MAKELIST` keep the
(dead) subgraph path; user-proc + builtin calls now take the flat-operand **chaining** path (args lowered
on the spine, pushed as `operands[]`, name set once and never clobbered). This is the JCON model (args ARE
operands). **Names now survive**; `f()` reaches `bb_call` cleanly. `write`/`writes` were already on the
chaining path, so the heartbeat is unaffected by construction.

### `ec3bd5b3` — D1-CALL step 2: route registered user procs to PROC_STAGED independent of `dval`
After step 1 the flat call no longer carries `dval=3.0` (its `dval` is the union's `sval` bits), so the
`dv==3.0||dv==1.0` gate on the descr-flat-chain PROC_STAGED route (`bb_call_route_classify`, emit_bb.c)
never matched → `bb_call` hit the FATAL fallthrough. Relaxed that ONE condition to
`if (g_descr_flat_chain && fn[0] && rt_proc_is_registered(fn)) return CALL_ROUTE_PROC_STAGED;`. Safe: the
generator-proc case is handled by an earlier branch; builtins aren't registered so they're untouched; it's
the SAME `rt_proc_is_registered` query as before (no new emit-time disease, just a relaxed gate). The
PROC_STAGED emitter's only `dval==1.0` read is inside its arg loop (`bcps_arg_slot`), which never runs for a
zero-arg call (`op_ival = n_operands = 0`), so garbage `dval` is harmless here.
**RESULT — zero-arg user procs work END-TO-END, BOTH modes:** `write(f())` with `f` returning a literal,
a string, or an expression (`return 3 + 4 * 2` → `11`) prints correctly in mode-3 (`--run`) AND mode-4
(text `.s` → `as` + `gcc` against `out/libscrip_rt.so`). **This PROVES the IR_RETURN conversion end-to-end**
— RETURN was un-exerciseable until a proc became callable; now it is, with a real binop-tree operand.

---

## THE LIVE FRONTIER — calls WITH ARGS (op=200 arg-handling), fully diagnosed

Zero-arg user procs now work end-to-end (above). The remaining frontier is **calls that pass arguments** —
both user procs (`f(3)`) and builtins (`abs(-5)`, `integer("7")`). These hit
**`[SMX] emit_drive: op=200 has no native template on the universal driver yet`** → EXCISED → segfault.

- **op=200** (map the exact member via the IR.h enum) is the nested arg-handling/marshalling IR op. After
  step 1 routed call args flat, a call's args sit on `operands[]` and the arg-staging op appears on the
  spine; `emit_drive_node` does not own it → `drive_unowned` → [SMX]. **Grow `emit_drive_node` to own op=200
  + the IR_CALL arg-operand marshalling** (drive each arg's value slot into the staging sequence the
  PROC_STAGED / BYNAME emitters consume). The PROC_STAGED arg loop (`bcps_arg_slot`, bb_call_proc_staged.cpp)
  still reads `dval==1.0` to pick arg slots — for flat args that read needs de-`dval`ing (read the operand
  slot directly), part of the B4 cleanup.
- This is still the D1-CALL rung fused with B4 (get the call-kind/arg-marshalling off `dval`, delete the
  emit-time `rt_*` retags). It was correctly NOT started piecemeal here — the "convert against live dval"
  trap that regressed prior sessions. It deserves a fresh full budget.

Note: builtin/arg calls were ALREADY broken before this session by the same union collision, so this
session's changes regressed **no green program** (only hw+adder must stay green; both do, both modes).

### Still-`dval`-gated readers to retire in the full D1-CALL/B4 pass (intelligence)
- `resolve_call_kinds_descr` (emit_bb.c:3724) — the emit-time `rt_*` retag pre-pass; B4 deletes it (resolve
  call kind at LOWER from a compile-time proc table). It no longer crashes (names survive) but is still F2.
- `bb_call_route_classify` — most branches still gate on `dv ∈ {2.0,3.0,1.0}`; move classification into LOWER.
- `bb_call_proc_staged.cpp` `bcps_arg_slot` — `dval==1.0` arg-slot selector.

### ⭐ RECOMMENDED APPROACH for the next rung (Lon, 2026-06-28): discriminate in the OP FIELD
Move the `{1.0, 2.0, 3.0}` call-kind tag OFF `dval` and INTO the op field — i.e. encode `IR_CALL1`/`IR_CALL2`
as distinct opcodes. **The members ALREADY EXIST in `IR.h`:** `IR_CALL_PROC_STAGED`, `IR_CALL_USERPROC`,
`IR_CALL_BYNAME`, `IR_CALL_BUILTIN`, `IR_CALL_GVAR_USERPROC`, plus `ir_is_call_kind()` /
`ir_norm_call_kind()` (folds any call-kind back to `IR_CALL`). So the rung is:
1. **LOWER emits the specific `IR_CALL_*` member directly** (decide user-proc vs builtin vs write/byname at
   lower time from a compile-time proc table — NOT a runtime `rt_*` query, NOT a `dval` tag). `dval` is then
   free to mean a real literal only.
2. **DELETE `resolve_call_kinds_descr`** (the emit-time retag) and make `bb_call_route_classify` switch on
   `nd->op` (the `IR_CALL_*` member) instead of `dv`. Emitter does zero `rt_*` queries.
3. **`bcps_arg_slot` reads the operand slot directly** (flat args), not `dval==1.0`.
This is the JCON-faithful shape too: one logical call, kind carried structurally, args as operands.

### Recommended next-rung plan (D1-CALL, in order; heartbeat-checked, no gates)
1. **Decide the call kind at LOWER time, not from `dval`.** Per JCON, a call is one `ir_Call`; invocation
   resolves the callee. Cleanest SCRIP realization: lower sets the call's final op (e.g. keep `IR_CALL` and
   route BY NAME at runtime via `rt_call_named_proc`/`rt_call_arr`, which already exist) — or a tiny
   `subtag` for builtin-vs-userproc-vs-write, NOT `dval`. Free `dval` to be a real literal only.
2. **Make `bb_call_route_classify` dval-independent** — route a registered named proc → PROC_STAGED (or a
   by-name route) from the name/subtag; drop the `dv==` gating. Ideally move the classification into LOWER
   (B4) so the emitter does zero `rt_*` queries.
3. **De-`dval` the `bb_call_proc_staged` / `bb_call_byname` emitters** (read the subtag/operands, not `dval`).
4. **Grow `emit_drive_node` to own the arg-handling op (op=200) + IR_CALL arg-operand marshalling** so
   `write(builtin(arg))` and `f(arg)` drive through the universal path.
5. Verify end-to-end: `procedure main(); write(f(3)); end  procedure f(x); return x+1; end` → `4`. This is
   the proof RETURN + CALL are both live (they are coupled — no proc is callable until CALL routes, so
   RETURN cannot be exercised end-to-end until this rung lands).

---

## OTHER FINDINGS (intelligence for next session)
- **`if/then/else` already runs** on the spine — it decomposes at lower time into pure γ/ω edge threading
  the driver already owns (`if 1<2 then write("yes") else write("no")` → `yes`). Not a frontier.
- **`--dump-ir` SEGFAULTs on multi-proc programs** (a dump-only IR-printing bug — `--run`/`--compile` reach
  emit fine, so shared lowering is OK; the crash is in `bb_print`/the dump iteration over the 2nd proc).
  Separate low-priority bug; it blocked IR inspection of proc bodies this session (worked around via `.s`).
- **`every i := 1 to 3 do write(i)`** needs op=18 (IR_EVERY) + op=103 (IR_TO) driver ownership — the
  generator/ω-wiring rung (DIVISION RULE: resumability = ω-wiring). A separate, later rung.
- gdb works in-container (`apt-get install -y gdb`); the `SCRIP_NO_SEGV_HANDLER=1` clean-backtrace hook did
  NOT suppress the handler for a clean bt this session — plain `gdb -batch -ex run -ex bt` worked.

---

## FILE MAP (touched this session)
| File | Change |
|---|---|
| `src/emitter/emit_drive.c` | + `case IR_RETURN: DRIVE_FILL(...)` |
| `src/lower/lower_icon.c` | line 101: `subgraph = !chains && is_idx_or_list` (flat call args) |
| `src/emitter/emit_bb.c` | `bb_call_route_classify`: registered proc → PROC_STAGED w/o `dval` gate (one line) |

`emit_core.c`, templates: UNTOUCHED. Build clean (`make scrip` + `make libscrip_rt`; needs
`apt-get install -y libgc-dev`). Mode-4 link recipe (for verifying the text path):
`./scrip --compile --target=x86 F.icn > F.s && as F.s -o F.o && gcc -no-pie F.o -Lout -lscrip_rt -lgc -lm -Wl,-rpath,out -o F.bin && ./F.bin`

---

## DO NOT REGRESS
- Heartbeat `write("hello world")` + `write(1+2)` green both modes — the ONLY required gate.
- Other Icon programs may go to/stay near zero and grow back (STANDING DIRECTIVE; authorized).
- Keep SCRIP-native naming; JCON is semantic reference only.

## HANDOFF STATUS
**BLOCKED on credential.** Two SCRIP commits + this doc are LOCAL only on the disposable sandbox. Per
RULES.md the handoff is NOT complete until `git push` succeeds and `handoff_status.sh` prints
`HANDOFF COMPLETE`. Need the push credential.
