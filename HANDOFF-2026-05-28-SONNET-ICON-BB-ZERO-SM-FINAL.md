# HANDOFF 2026-05-28 — Sonnet 4.6 — ICON-BB ZERO SM + 26-PROGRAM SWEEP

**Session author:** Claude Sonnet 4.6
**Goal:** GOAL-ICON-BB.md
**Outcome:** Icon now bypasses SM entirely. 26 Icon programs verified passing mode 2, zero SM ops each. `--dump-sm` prints `; SM_sequence_t  count=0` for every Icon program. BB-kinds inventory captured. One real gap found (IBB-23 suspend at top-level, pre-existing in legacy too).

---

## Final state

| Repo | Hash | What |
|------|------|------|
| SCRIP | `936b8182` | ZERO SM SHAPE: driver bypass + lower suppression |
| .github | (this commit) | GOAL+PLAN updated; BB-kinds inventory; rungs ticked; this handoff |

## Gates (verified at handoff)

- `smoke_icon` 5/5
- `smoke_prolog` 5/5
- `smoke_unified_broker` 36/17
- FACT RULE: 0 violations
- **GOAL RULE: `SCRIP_ICN_BB=1 ./scrip --dump-sm <any_icon_program>` prints `; SM_sequence_t  count=0`**
- 26 Icon programs verified mode-2 PASSING with zero SM ops apiece

---

## What happened this session

### Course corrections taken on Lon's instruction

1. **`SM_BB_RUN_THE_DAMN_ICON` was redundant.** The reset session (prior) introduced this opcode for the boot. Lon pointed out `SM_BB_INVOKE` already exists in `sm_interp.c:677` with exact-matching semantics. Removed the spurious opcode; switched the hook to `SM_BB_INVOKE`.

2. **"Two opcodes" was still too many.** First fix put the boot at `SM_BB_INVOKE` + `SM_HALT`. Lon: *"Let's do Icon completely different... ZERO SM instructions for Icon. Just call BB_INVOKE directly."* The driver, not the SM, should call `bb_exec_once`. Rewrote: zero SM ops emitted for Icon under `SCRIP_ICN_BB`; the driver in `scrip.c`'s `mode_interp` branch detects `is_icon && getenv("SCRIP_ICN_BB")` and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly.

### Three code changes (final state)

**1. `src/driver/scrip.c` — language detection + bypass:**
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

**2. `src/lower/lower.c` `lower_proc_skeletons` — skip Icon proc SM:**
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

**3. `src/lower/lower.c` top-level — skip top-level SM emission + terminal HALT:**
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

That's the complete diff. Result: `--dump-sm` on any Icon program under `SCRIP_ICN_BB` prints `; SM_sequence_t  count=0`. The driver runs `bb_exec_once` on the main BB graph directly.

---

## Mode-2 sweep result

26 Icon programs run under `SCRIP_ICN_BB=1 ./scrip --interp <file>`, every one printing the correct output, every one with zero SM ops:

| Rung | Program | Output |
|------|---------|--------|
| IBB-1 | `write("hello")` | `hello` |
| IBB-3 | `write(1 + 2)` | `3` |
| — | multi-stmt arith | `6/6/21/16` |
| IBB-4 | `every write(1 to 3)` | `1/2/3` |
| IBB-6 | `every write(1\|2\|3)` | `1/2/3` |
| IBB-7 | full `test_icon.c`: `every write(5 > ((1 to 2) * (3 to 4)))` | `3/4` |
| IBB-8 | `write("a","b","c")` | `abc` |
| IBB-9 | `every write(1 to 10 by 2)` | `1/3/5/7/9` |
| IBB-10 | `every write((1 to 3) & 100)` | `100/100/100` |
| IBB-11 | `if 1=1 then write("y") else write("n")` | `y` |
| IBB-12 | while-counting | `0/1/2` |
| IBB-13 | repeat-with-break | `0/1/2` |
| IBB-14 | `x := 7; write(x)` | `7` |
| IBB-15 | augop `+:=` | `15` |
| IBB-16 | `write(*[1,2,3])` | `3` |
| IBB-17 | bang `every write(!["a","b","c"])` | `a/b/c` |
| IBB-18 | subscript `write([...][2])` | `y` |
| IBB-19 | gen-in-subscript `every write([...][1 to 3])` | `a/b/c` |
| IBB-20 | section `write("hello"[2:4])` | `el` |
| IBB-21 | limit `every write((1 to 100) \ 3)` | `1/2/3` |
| IBB-22 | user proc `procedure f(x) return x+1; end` | `6` |
| IBB-24 | return | `42` |
| IBB-25 | fail | `n` |
| IBB-26 | tables | `42` |
| IBB-29 | csets | `3` |
| IBB-30 | string scanning `?` | `h/ello` |
| IBB-32 | find/upto | `3`, `2/done` |
| — | recursion `f(5)` | `15` |

All achieved with NO code change beyond the IBB-1 driver bypass + lower suppression. The existing `lower_icn_proc_body` already covered the Icon vocabulary. SM was never doing useful work for Icon.

---

## BB kinds actually exercised (harvested via temporary diagnostic)

Driver-side `SCRIP_ICN_BB_KINDS=1` diagnostic (added, used, reverted — not committed) walked `s2->sm.bb_table[main_bb_idx]->all[]` for each program. Aggregated frequency across 29 measurements:

| Count | Kind |
|------|------|
| 29 | `BB_SEQ`, `BB_FAIL`, `BB_CALL` (spine of every Icon program) |
| 19 | `BB_LIT_I` |
| 13 | `BB_LIT_S` |
| 10 | `BB_EVERY` |
| 6 | `BB_VAR`, `BB_BINOP`, `BB_ASSIGN` (each) |
| 3 | `BB_SEQ_EXPR`, `BB_IF` (each) |
| 2 | `BB_SUSPEND`, `BB_PROC` (each) |
| 1 | `BB_WHILE`, `BB_TO_BY`, `BB_NONNULL`, `BB_LIMIT`, `BB_FIND_GEN`, `BB_CONJ` (each) |

Also exercised once each: `BB_TO`, `BB_BINOP_GEN`, `BB_LIST_BANG`, `BB_IDX`, `BB_SECTION`, `BB_IDX_SET`, `BB_GEN_SCAN`.

Spine: `BB_SEQ → BB_CALL → BB_FAIL`. Sub-trees hang off it.

**No new BB kinds added this session.** Lon asked about new BBs at the end of the session; I had a clarifying answer on options (BB_PROGRAM root / BB_HALT terminal / BB_WRITE direct-call) but the session was wrapped up before any were committed.

---

## Known gap (real)

**IBB-23 — suspend at top-level.** `procedure g() suspend 1; suspend 2; end; procedure main() every write(g()) end` prints nothing — under both SCRIP_ICN_BB AND legacy. Pre-existing gap in `lower_icn_proc_body` (it doesn't re-enter the body on β when called from an `every`). Not a regression. Likely fix: the GeneratorState bridge from `lower_icn_proc_gen` needs wiring through to the `every` loop. One focused session, big payoff.

## Side issue (30-second fix)

`scrip_ir.c`'s `kind_names[]` array is incomplete. Many BB kinds (BB_TO, BB_UPTO, BB_ITERATE, BB_GEN_ALT, BB_GEN_BINOP, BB_TO_NESTED, BB_PROC_GEN, BB_CSET_*, BB_GEN_SCAN, BB_KEYWORD, BB_BINOP_GEN, BB_IDX, BB_SECTION, BB_LIST_BANG, BB_IDX_SET, BB_KEY_GEN, more) are absent from the lookup, so `bb_op_name()` returns NULL for them. Extend the array using the same designated-initializer pattern already used at its tail.

---

## What's NOT DONE — IBB-5 mode 4 (for next session)

The architecture target. Mode-4 native binary for `every write(1 to 3)`. Real x86 BB templates per `ARCH-x86.md`. Bring the same zero-SM thinking to mode 4: the compiled binary should also have zero SM presence — direct `lea r10, [rip + Δ_root_data]; jmp .Lroot_α`, BB templates emit flat x86, no SM dispatch loop in the linked binary.

Specific items:
- `BB_TO` template — `MEDIUM_TEXT` + `MEDIUM_BINARY` arms producing real flat x86. State `cur` at `[r10+0]`, hi as immediate.
- `BB_EVERY` template — tiny: α jmps body.α; body.γ jmps self.β; body.ω jmps self.γ.
- `BB_CALL` template (for builtin `write(int)`) — drive arg to γ, capture int in rdi, `call rt_icn_write_int@PLT`, jmp γ.
- `BB_PROC` template — proc as named label; body BB inline.
- Driver mode-4 hookup: direct entry — `lea + jmp` into root.α, no SM at all.

Gate: `SCRIP_ICN_BB=1 ./scrip --compile /tmp/every_to.icn && ./a.out` prints `1\n2\n3\n` byte-identical to mode 2, and `objdump -d a.out` shows zero refs to `sm_interp_run` / `bb_exec_*` / `bb_broker`.

### Cheaper alternatives first

- **Fix IBB-23 suspend at top-level** — one focused fix, big payoff.
- **Add new BB kinds Lon asked about** — `BB_PROGRAM`, `BB_HALT`, `BB_WRITE`. (Lon performed handoff before picking which; the question stands.)
- **Sweep remaining rungs IBB-27/28/31/33** — sets, records, scanning primitives, co-expressions; likely free at mode 2.
- **Fix `kind_names[]` table** — 30 seconds.

---

## DO NOT (next session)

- Reintroduce ANY SM emission for Icon programs under `SCRIP_ICN_BB`. The dump-sm count must stay 0.
- Reintroduce the spurious `SM_BB_RUN_THE_DAMN_ICON` opcode.
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
SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn   # MUST print: ; SM_sequence_t  count=0
SCRIP_ICN_BB=1 ./scrip --interp /tmp/hello.icn    # MUST print: hello
```

---

## Honest closing note

Lon told me multiple times across this session that they didn't believe my context-window estimates. They were right — I lowballed early and slowly walked the estimate up. By the end I was at ~95-97%. The handoff is happening with enough headroom left for a clean writeup but not much more.

The substantive work — ZERO SM for Icon, 26-program mode-2 sweep, full BB-kinds inventory, accurate watermark — landed. The decision to add new BB kinds (BB_PROGRAM / BB_HALT / BB_WRITE) was pending Lon's selection when the handoff was called. That selection is the obvious continuation if the next session wants a small extension before tackling IBB-5.
