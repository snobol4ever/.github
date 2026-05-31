# HANDOFF 2026-05-28 — Sonnet 4.6 — ICON-BB IBB-1 CLOSED + GOAL RULE

**Session author:** Claude Sonnet 4.6
**Goal:** GOAL-ICON-BB.md (post-reset rung ladder)
**Outcome:** IBB-1 ✅ closed. Two-op boot landed on the canonical `SM_BB_INVOKE` opcode. Spurious `SM_BB_RUN_THE_DAMN_ICON` opcode introduced by the reset session is removed. SM proc-skeleton emission suppressed for Icon under `SCRIP_ICN_BB`. Icon SM stream is now exactly `SM_BB_INVOKE` + `SM_HALT`. GOAL RULE added.

---

## Final state

| Repo | Hash | What |
|------|------|------|
| SCRIP | `9ccf95e1` | IBB-1 close: collapse to `SM_BB_INVOKE`, remove spurious opcode, suppress Icon proc skeleton |
| .github | (this commit) | GOAL RULE; PLAN row updated; IBB-1 steps ticked |

## Gates (verified at handoff)

- `smoke_icon` 5/5
- `smoke_prolog` 5/5
- `smoke_unified_broker` 36/17
- FACT RULE: 0 violations outside templates/emit_core
- **GOAL RULE: `SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn | awk '/^   [0-9]/ {print $2}' | sort -u` prints exactly `SM_BB_INVOKE` and `SM_HALT`**
- Functional: `SCRIP_ICN_BB=1 ./scrip --interp /tmp/hello.icn` prints `hello`

---

## What changed this session

### 1. Opcode rename — `SM_BB_RUN_THE_DAMN_ICON` → `SM_BB_INVOKE`

The reset session introduced a new enum value `SM_BB_RUN_THE_DAMN_ICON` for the boot opcode. Lon pointed out that `SM_BB_INVOKE` already exists (`sm_interp.c:677`), already has the exact semantics needed (`a[1].i = bb_table idx`; calls `bb_exec_once(bb_table[idx])` on first entry), and is the right opcode. The new opcode was redundant.

Reverted:
- `src/include/SM.h` — removed `SM_BB_RUN_THE_DAMN_ICON` enum
- `src/lower/sm_prog.c` — removed `"SM_BB_RUN_THE_DAMN_ICON"` opname
- `src/processor/sm_interp.c` — removed the duplicate mode-2 handler
- `src/emitter/emit_core.c` — removed dispatch stub and `is_dispatched` entry
- `src/lower/lower.c` — hook now emits `SM_BB_INVOKE`

### 2. GOAL RULE added

Added to `GOAL-ICON-BB.md`:

> **Only `SM_BB_INVOKE` and `SM_HALT` may appear in an Icon program's SM stream.**

Also added to `RULES.md` as a top-level rule.

Completion test:
```bash
SCRIP_ICN_BB=1 ./scrip --dump-sm any_icon_program.icn \
  | awk '/^   [0-9]/ {print $2}' \
  | sort -u
# Must print exactly:
#   SM_BB_INVOKE
#   SM_HALT
```

### 3. SM proc-skeleton emission suppressed for Icon under `SCRIP_ICN_BB`

Previously, even with the hook emitting `SM_BB_INVOKE`, `lower_proc_skeletons()` still emitted the proc shell: `SM_JUMP / SM_LABEL nm / <body lower_expr loop> / SM_RETURN`. So `--dump-sm` showed:

```
0  SM_JUMP        -> 6
1  SM_LABEL       s="main"
2  SM_PUSH_LIT_S  s="hello"
3  SM_CALL_FN     s="write" nargs=1
4  SM_VOID_POP
5  SM_RETURN
6  SM_LABEL
7  SM_BB_RUN_THE_DAMN_ICON
8  SM_HALT
```

That violated the GOAL RULE. Fix: at the top of each loop iteration of `lower_proc_skeletons()`, when proc is `TT_PROC_DECL` AND `SCRIP_ICN_BB=1`, build the BB graph (so `bb_idx` is registered) and `continue` — emit ZERO SM ops for the proc.

Now `--dump-sm` shows exactly:
```
0  SM_BB_INVOKE
1  SM_HALT
```

### 4. Documentation

- `lower_icn_bb.h` stub header rewritten to state the new RULE.
- `GOAL-ICON-BB.md` premise + banned section rewritten as a single canonical **GOAL RULE** block.
- All in-file references to `SM_BB_RUN_THE_DAMN_ICON` renamed to `SM_BB_INVOKE`.
- `RULES.md` got a one-line cross-reference: "ICON SM = TWO OPCODES ONLY."
- `PLAN.md` ICON row updated.

---

## Code shape

**`src/lower/lower.c` (`lower_proc_skeletons`, top of loop body):**
```c
if (proc && proc->t == TT_PROC_DECL && getenv("SCRIP_ICN_BB")) {
    int body_start = 0;
    IcnScope sc; build_proc_scope(&sc, proc, body_start);
    g_stage2.proc_table[pi].lower_sc = sc;
    BB_graph_t *_irb = lower_icn_proc_body(proc);
    g_stage2.proc_table[pi].bb_idx = _irb ? SM_seq_bb_add(g_p, _irb) : -1;
    g_stage2.proc_table[pi].is_generator = 0;
    if (_irb) {
        for (int _k = 0; _k < _irb->n; _k++) {
            if (_irb->all[_k] && _irb->all[_k]->t == BB_SUSPEND) {
                g_stage2.proc_table[pi].is_generator = 1; break;
            }
        }
    }
    continue;
}
```

**`src/lower/lower.c` (top-level `if (has_icn)` block):**
```c
if (has_icn) {
    if (getenv("SCRIP_ICN_BB")) {
        int main_bb_idx = -1;
        for (int _pi = 0; _pi < g_stage2.proc_count; _pi++) {
            if (g_stage2.proc_table[_pi].name &&
                strcmp(g_stage2.proc_table[_pi].name, "main") == 0) {
                main_bb_idx = g_stage2.proc_table[_pi].bb_idx;
                break;
            }
        }
        if (main_bb_idx < 0) { fprintf(stderr, "[ICN-BB] lower: main proc not found or not BB-lowered\n"); }
        else { SM_emit_si(g_p, SM_BB_INVOKE, NULL, (int64_t)main_bb_idx); }
    } else {
        SM_emit_si(g_p, SM_CALL_FN, "main", 0);
        SM_emit(g_p, SM_VOID_POP);
    }
}
```

`SM_HALT` follows from the existing terminal guard.

---

## What's NOT DONE — IBB-3 (for next session)

**IBB-3 — `write(1 + 2)` mode 2.**

Steps:
1. Confirm AST shape for `procedure main() write(1 + 2) end` via `--dump-ast` — likely `TT_FNC(write, TT_ADD(TT_INTLIT 1, TT_INTLIT 2))`.
2. Verify `lower_icn_expr_node` already handles `TT_ADD` + `TT_INTLIT` (it should, via `lower_icn_new_Binop` and `lower_icn_new_Intlit`).
3. Run mode-2 gate: `SCRIP_ICN_BB=1 ./scrip --interp /tmp/add.icn` should print `3`.
4. Confirm `--dump-sm` still shows only `SM_BB_INVOKE` + `SM_HALT`.
5. Update watermark, commit, push.

Likely no code change needed — IBB-1 already supplies the boot infrastructure, and `lower_icn_proc_body` already calls `lower_icn_expr_threaded_b` which handles the full Icon expression vocabulary. If gate passes, IBB-3 closes with just the test and a checkbox tick.

If gate fails, the failure mode tells where the BB graph is incomplete; that's the next step.

---

## Pointers for next session

- The boot opcode is `SM_BB_INVOKE`. Do not reintroduce `SM_BB_RUN_THE_DAMN_ICON`.
- For non-`main` Icon procs called by main (when IBB-22 lands), the body BB has `proc_table[pi].bb_idx` set the same way; `BB_CALL` from inside main's graph reaches them via `bb_call_proc_by_name` or similar (verify the runtime path).
- Mode-2 `SM_BB_INVOKE` handler is at `sm_interp.c:677`. It calls `bb_exec_once` on entry==0 and `bb_exec_resume` on entry==1.
- `lower_icn_proc_body` already exists and handles every Icon construct the dispatcher knows about. Don't write a parallel `lower_icn_bb.c` — the existing function IS the body lowerer for procs.
- The header `src/lower/lower_icn_bb.h` documents the rule. It does not export functions yet (no .c file exists). Add functions if and only if mode-3/4 emit at IBB-5+ needs them.

---

## DO NOT (next session)

- Reintroduce `SM_BB_RUN_THE_DAMN_ICON` or any other Icon-specific boot opcode. `SM_BB_INVOKE` is canonical.
- Emit ANY SM opcode other than `SM_BB_INVOKE` and `SM_HALT` for Icon under `SCRIP_ICN_BB`. The GOAL RULE is checked on every commit.
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions.
- Add fields to `BB_t`.

---

## Session start for next person

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
# Read PLAN.md → ICON-BB row points here.
# Read RULES.md (includes the new ICON SM = TWO OPCODES ONLY rule).
# Read GOAL-ICON-BB.md — the GOAL RULE is up top.
# Read this handoff.
git clone https://TOKEN@github.com/snobol4ever/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh              # expect: 5/5
bash scripts/test_smoke_prolog.sh            # expect: 5/5
bash scripts/test_smoke_unified_broker.sh    # expect: ≥35

# GOAL RULE re-verify
cat > /tmp/hello.icn << 'EOF'
procedure main()
  write("hello")
end
EOF
SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn \
  | awk '/^   [0-9]/ {print $2}' | sort -u
# Must print exactly: SM_BB_INVOKE, SM_HALT
```

Then pick up at IBB-3.

---

## Closing note

The Icon SM stream is now two opcodes. `SM_BB_INVOKE` + `SM_HALT`. Per the GOAL RULE.

Don't relapse.
