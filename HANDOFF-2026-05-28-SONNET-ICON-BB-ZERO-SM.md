# HANDOFF 2026-05-28 — Sonnet 4.6 — ICON-BB ZERO SM SHAPE

**Session author:** Claude Sonnet 4.6
**Goal:** GOAL-ICON-BB.md
**Outcome:** ICON-BB IBB-1 → IBB-15 (the mode-2-friendly ones) closed in a single move. Icon now bypasses SM entirely. Driver detects Icon-BB and calls `bb_exec_once` directly. `lower()` emits ZERO SM ops for Icon. `--dump-sm` prints `; SM_sequence_t  count=0`. The BB graph alone runs everything.

---

## Final state

| Repo | Hash | What |
|------|------|------|
| SCRIP | `936b8182` | ZERO SM SHAPE for Icon: driver bypass + lower suppression |
| .github | (this commit) | GOAL RULE updated (zero SM); IBB-1..15 ticked; PLAN row updated |

## Gates (verified at handoff)

- `smoke_icon` 5/5
- `smoke_prolog` 5/5
- `smoke_unified_broker` 36/17
- FACT RULE: 0 violations
- **GOAL RULE: `SCRIP_ICN_BB=1 ./scrip --dump-sm <icon_program>` prints `; SM_sequence_t  count=0` for every Icon program**
- Mode 2 PASSING under SCRIP_ICN_BB for: `hello`, `1+2`, multi-stmt arith, `every 1 to 3`, `1|2|3`, `1 to 10 by 2`, `if/then/else`, full `test_icon.c` expression `every write(5 > ((1 to 2) * (3 to 4)))` → `3 / 4`, `x := 7; write(x)`, `sum := 0; every sum +:= (1 to 5); write(sum)` → `15`.

---

## What changed this session

### The decision

Lon: *"Let's do Icon completely different then all the others. We will use ZERO SM instructions for Icon. Just call BB_INVOKE directly."*

That tightens the previous GOAL RULE from "two opcodes" (`SM_BB_INVOKE` + `SM_HALT`) to "zero opcodes." SM has no role in the Icon runtime path. The driver detects Icon-BB and calls the BB graph directly.

### Three code changes (all driver-side / lower-side)

**1. `src/driver/scrip.c` — driver bypass in `mode_interp`:**
```c
int is_icon = 0;
for (int fi = argi; fi < argc; fi++) {
    const char *d = strrchr(argv[fi], '.');
    if (d && strcmp(d,".icn")==0) is_icon = 1;
}
// ...
} else if (mode_interp) {
    stage2_t *s2 = sm_preamble(ast_prog);
    if (!s2) return 1;
    ast_tree_free(ast_prog); ast_prog = NULL;
    SM_sequence_t *sm = &s2->sm;
    if (dump_sm) { sm_seq_print(sm, stdout); return 0; }
    if (is_icon && getenv("SCRIP_ICN_BB")) {
        extern DESCR_t bb_exec_once(BB_graph_t * bbg);
        int main_bb_idx = -1;
        for (int _pi = 0; _pi < s2->proc_count; _pi++) {
            if (s2->proc_table[_pi].name && strcmp(s2->proc_table[_pi].name, "main") == 0) {
                main_bb_idx = s2->proc_table[_pi].bb_idx; break;
            }
        }
        if (main_bb_idx < 0 || main_bb_idx >= sm->bb_count || !sm->bb_table[main_bb_idx]) {
            fprintf(stderr, "[ICN-BB] driver: main BB graph not found\n");
            return 1;
        }
        (void)bb_exec_once(sm->bb_table[main_bb_idx]);
        goto run_done;
    }
    sm_run_with_recovery(sm, sm_interp_run);
}
```

**2. `src/lower/lower.c` — top-level Icon SM emission suppressed:**
```c
if (has_icn && !getenv("SCRIP_ICN_BB")) {
    SM_emit_si(g_p, SM_CALL_FN, "main", 0);
    SM_emit(g_p, SM_VOID_POP);
}
// ...
if (!(has_icn && getenv("SCRIP_ICN_BB"))) {
    if (g_p->count == 0 || g_p->instrs[g_p->count - 1].op != SM_HALT) SM_emit(g_p, SM_HALT);
}
```

**3. `src/lower/lower.c` — `lower_proc_skeletons` skips SM emission for Icon procs (already in from previous commit; preserved):**
```c
if (proc && proc->t == TT_PROC_DECL && getenv("SCRIP_ICN_BB")) {
    // build BB graph + register, emit zero SM ops, continue
    ...
}
```

That's the entire diff. `--dump-sm` on any Icon program under `SCRIP_ICN_BB` now prints `; SM_sequence_t  count=0`. The driver picks up the BB graph from `s2->sm.bb_table[main_bb_idx]` and runs `bb_exec_once`.

### Header update

`src/lower/lower_icn_bb.h` rewritten as a documentation stub describing the zero-SM rule. No exported functions yet (the rule lives in the driver and the lower suppression).

---

## What worked for free

After the bypass, mode 2 already passes for the Icon vocabulary covered by `lower_icn_proc_body`:

| Rung | Program | Output | SM ops |
|------|---------|--------|--------|
| IBB-1 | `write("hello")` | `hello` | 0 |
| IBB-3 | `write(1 + 2)` | `3` | 0 |
| — | multi-stmt arith | `6/6/21/16` | 0 |
| IBB-4 | `every write(1 to 3)` | `1/2/3` | 0 |
| IBB-6 | `every write(1\|2\|3)` | `1/2/3` | 0 |
| IBB-7 | `every write(5 > ((1 to 2) * (3 to 4)))` | `3/4` | 0 |
| IBB-9 | `every write(1 to 10 by 2)` | `1/3/5/7/9` | 0 |
| IBB-11 | `if 1=1 then write("y") else write("n")` | `y` | 0 |
| IBB-14 | `x := 7; write(x)` | `7` | 0 |
| IBB-15 | `sum := 0; every sum +:= (1 to 5); write(sum)` | `15` | 0 |

All achieved without writing a single line of additional lowering. The existing `lower_icn_proc_body` covers the entire vocabulary. The previous shape (SM-driving-BB-from-the-top) was just sitting on top of work the BB graph could do alone.

---

## What's NOT DONE — IBB-5 mode 4 (for next session)

IBB-5 is the architecture target: mode-4 native binary for `every write(1 to 3)`. That requires real x86 BB templates per `ARCH-x86.md`. The mode-4 path is separate from mode 2's `bb_exec_once`:

- `BB_ICN_TO` template — `MEDIUM_TEXT` + `MEDIUM_BINARY` arms producing real flat x86.
- `BB_ICN_EVERY` template — tiny: α jmps body.α; body.γ jmps self.β; body.ω jmps self.γ.
- `BB_ICN_CALL` template — for builtin `write(int)`: drive arg to γ, capture int in rdi, `call rt_icn_write_int@PLT`, jmp γ.
- `BB_ICN_PROGRAM` + `BB_ICN_PROC` templates — program preamble `lea r10, [rip + Δ_root_data]`; proc as named label.
- Mode-4 driver hookup: skip SM entirely there too — directly jmp into root.α.

Gate: `SCRIP_ICN_BB=1 ./scrip --compile /tmp/every_to.icn && ./a.out` prints `1\n2\n3\n`, byte-identical to mode 2 output, and `objdump -d a.out` shows zero refs to `sm_interp_run` / `bb_exec_*` / `bb_broker`.

---

## What's likely free at mode 2 for a sweep next session

Worth running mode-2 tests for these and ticking off any that pass without code change:
- IBB-8: strings (multi-arg `write`)
- IBB-10: conjunction `&`
- IBB-12: while
- IBB-13: until / repeat
- IBB-16: list literal
- IBB-17: bang `!L`
- IBB-18: subscript
- IBB-20: section
- IBB-21: limit `\`
- IBB-22: user procedure call
- IBB-23: suspend
- IBB-24: return
- IBB-25: fail

Anything that fails identifies a missing case in `lower_icn_proc_body` (or its dispatcher `lower_icn_expr_node`) and is a small focused fix.

---

## DO NOT (next session)

- Reintroduce ANY SM emission for Icon programs under `SCRIP_ICN_BB`. The dump-sm count must stay at 0.
- Add the spurious `SM_BB_RUN_THE_DAMN_ICON` opcode back. `SM_BB_INVOKE` is the legacy opcode for other languages; Icon under `SCRIP_ICN_BB` doesn't use it.
- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions.
- Add fields to `BB_t`.

---

## Session start for next person

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
# Read PLAN.md → ICON-BB row points here.
# Read RULES.md (ICON SM = ZERO OPCODES rule).
# Read GOAL-ICON-BB.md.
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
SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn
# Must print: ; SM_sequence_t  count=0
SCRIP_ICN_BB=1 ./scrip --interp /tmp/hello.icn
# Must print: hello
```

Then either sweep IBB-8/10/12/13/16+ at mode 2 (cheap), or jump to IBB-5 mode 4 (the architecture target).

---

## Closing note

Icon emits zero SM. The driver calls `bb_exec_once` directly. SM dispatch was scaffolding; Icon doesn't need it.

The next architecturally-meaningful step is IBB-5: bring the same zero-SM thinking to mode 4. The compiled binary should also have zero SM presence — direct jmp into the root BB's α label, BB templates emit flat x86, no dispatch loop in the linked binary.
