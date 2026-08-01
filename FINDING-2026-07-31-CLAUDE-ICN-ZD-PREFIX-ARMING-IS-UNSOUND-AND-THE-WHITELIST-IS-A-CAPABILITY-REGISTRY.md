# FINDING — ICN-ZD: PREFIX ARMING IS UNSOUND, AND `zd_wl_kind` IS A CAPABILITY REGISTRY, NOT A POLICY WHITELIST

**Session s205 · 2026-07-31 · Claude · SCRIP `85fc743e`, `8f1a1a21`**

## 0. THE LOST FIX WAS REAL — ICN-JCC RE-LANDED, +23 PROGRAMS

s204's cursor reports Icon at **238/25/30 "fixed"**. HEAD measured **215/48/30**. The ICN-JCC fix lived
only in the local, never-pushed commits s204's own banner flags (`7b974446`, `ed3d95a9`) — those hashes
do not exist in origin's history at all. `x86_jcc_invert` still carried the 4-pair table and still
aborted on everything else.

**Re-landed by DERIVATION, not by adding pairs.** In the x86 encoding the LOW BIT OF THE JCC OPCODE IS
THE NEGATION BIT (`0x84^1=0x85` je/jne, `0x8C^1=0x8D` jl/jge, …). `x86_jcc_invert` now returns
`x86_jcc_canon(x86_jcc_op(m) ^ 1)`, so it is total over `x86_jcc_op`'s vocabulary **by construction** and
the two spellings of the one vocabulary can never drift again — which is exactly how they drifted.

MEASURED: **215/48/30 → 238/25/30**, reproducing s204's number exactly. Prolog 5/5/5 green.

⚠ **A 1-PROGRAM SNOBOL4 `--compile` DELTA WAS INVESTIGATED AND DISMISSED AS THE DOCUMENTED FLAKE.** The
first A/B read 276→275. Re-running the BASELINE on identical bytes oscillates **275 ↔ 276**. Measurement
prevented a false regression attribution — and equally prevented dismissing it by argument.

## 1. ⛔ PREFIX ARMING IS UNSOUND — FALSIFIED, DO NOT RE-DERIVE

`zd_plan`'s run gate is ALL-OR-NOTHING: one unarmable node declines every BB in its statement. This is
why the Icon census reads **armed=0 / declined=271**. The obvious relaxation — arm the maximal passing
PREFIX — was implemented and measured.

**RESULT: 238/25/30 → 78/185/30, and the failures are SILENT WRONG ANSWERS at rc=0.**

| probe | baseline | prefix arming |
|---|---|---|
| `x := 1 + 2; write(x)` | `3` | *(nothing)* |
| `every i := 1 to 3 do write(i)` | `1 2 3` | `0` |

⭐ **THE FIRST PROBE HAS NO BACKTRACKING**, so "resume into released storage" is NOT the mechanism, and
the natural four-port explanation is falsified before it is spent.

**ROOT CAUSE.** The operand loop checks only that an armed node's **OPERANDS** are earlier armed nodes.
It never checks the **CONVERSE — that an armed node's CONSUMERS are armed.** An armed producer writes its
rsp cell; an unarmed consumer reads the flat frame slot. Truncating a prefix manufactures exactly that
disagreement at the boundary. **The all-or-nothing gate is not timidity — it is what holds the
producer/consumer STORAGE-REGIME agreement across a run.**

⇒ Any future partial arming must arm a **CONVEX region closed under BOTH operand and consumer edges**,
never a prefix. The counterexample is recorded verbatim at the site in `emit.cpp`.

## 2. `zd_wl_kind` IS A CAPABILITY REGISTRY — FLIPPING IT MAKES IT LIE

Default-admitting every kind outside the pattern-blob block scores **238/25/30 → 130/133/30**.

The whitelist is **not** a policy list someone was being shy with. It records which kinds have a **ZD arm
IMPLEMENTED IN THEIR TEMPLATE**. Admitting a kind whose template has no arm arms the node without anyone
writing its cell, so its consumer reads an unwritten rsp slot. The existing ledger entry says this
already: *"`IR_CALL_BUILTIN_ICON` — 68 declines, absent from the whitelist; likely ONE TEMPLATE ZD ARM."*

**⇒ THE UNIT OF WORK IS A TEMPLATE ARM, ONE KIND AT A TIME.** After each arm lands, the kind is admitted
and the registry becomes total BY CONSTRUCTION. `SCRIP_ZD_TOTAL` is retained as a **probe whose delta
sizes the remaining capability gap and ranks which arm to write next** — never to ship.

## 3. THE FUNCTION-LEVEL VETO IS REAL BUT NOT THE BINDING CONSTRAINT

`SCRIP_ZD_NOGRAPH` removes the whole-graph `flat_jmp_entry && !zd_stub_ok()` early return — the
function-level ζ scoping Lon's directive prohibits. On Icon it is **EXACTLY INERT: 238/25/30, zero
delta.** Because the per-run whitelist already declines every Icon run downstream, the graph veto is
currently *redundant*. It must still go, but removing it buys nothing until the registry has arms.
⇒ **Do not spend a rung on ICN-CARVE-2's `zd_stub_ok` tension before the arms exist; it is dominated.**

## 4. WHAT THE DIRECTIVE'S INFRASTRUCTURE ALREADY IS

Lon's s21x-w directive is largely BUILT; `op_zres`'s own comment (emit.h:605) quotes it verbatim.
- α/β grant seam: `x86_deflabel(X86P_ALPHA)` → `x86_port_hook(X86H_DEF, ALPHA)`. **323 α sites inherit it free.**
- One instruction: `x86_sub("rsp", k16)` in the hook's α arm.
- One traversal computing sliding offsets: `zd_plan`, `zout[i] = zd + K; zd = zout[i]`.
- Statement-level scoping: runs are rooted at `bb_src_of` heads; γ/ω release via `zgpop`/`zwpop`.
- Four modes: `ZC_STORAGE_{FRAME_R12,FRAME_RSP,CELL_STACK,CELL_HEAP}` + `x86_zop_regime()` 1–4.

**The gap is not architecture. It is per-template ZD arms** — plus the 123 `"rsp"` spellings across 17 of
157 templates (the "no RSP in templates" clause) and the result-use predicate, which `ZB-VAL-8B` already
found the IR cannot answer (no use count).

## 5. NEXT RUNGS — ORDERED
1. ⭐⭐⭐ **`IR_CALL_BUILTIN_ICON` ZD arm** — 68 declines, the single largest named gap, "likely one template arm."
2. ⭐⭐ **Rank the rest by `SCRIP_ZD_TOTAL` delta** — the probe exists now; use it as the census instead of guessing.
3. ⭐ **The generator family arm** (`IR_DISJUNCTION`/`IR_TO`/`IR_REPALT`/`IR_TO_BY`/`IR_PROC_GEN`, 67 declines) — ground truth `refs/jcon-master/tran/irgen.icn`.
4. **Convex-region arming** — only after (1)–(3), and only with a consumer-edge check.
5. **`SCRIP_ZD_NOGRAPH` default-on** — free once the registry has arms; inert today.
