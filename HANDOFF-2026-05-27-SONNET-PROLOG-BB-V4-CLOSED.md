# HANDOFF — 2026-05-27 — Sonnet 4.7 — Prolog BB V-4 CLOSED

**one4all HEAD: `88f03a41`** ✅ all gates green
**.github HEAD: pending watermark + V-5 decision doc commit**

---

## What landed

### V-4 — `rt_pl_b_*` runtime BB-rebuild path RETIRED (`88f03a41`)

Predicate BB graphs are now inlined as flat x86 by `SM_BB_SWITCH PL_ENTRY` at
emit time (V-1/V-2/V-3 landed earlier today). The runtime path that rebuilt the
BB graph at standalone-binary startup via `rt_register_predicates_pl` +
`rt_pl_b_*` helpers was **dead code**: the rebuilt `BB_graph_t` was never
executed (0 `bb_exec_*` calls in emitted .s).

**Deletions (~570 LOC net):**

| Site | Removed |
|------|---------|
| `src/emitter/XA_templates/xa_pl_builder.cpp` | entire file |
| `src/emitter/XA_templates/xa_pl_sub_builder.cpp` | entire file |
| `src/emitter/XA_templates/xa_pl_registry_table.cpp` | entire file |
| `src/emitter/XA_templates/xa_pl_kids_rodata.cpp` | entire file |
| `src/emitter/emit_sm.c` | `codegen_pl_predicate_registry` + 4 helpers (~180 LOC) |
| `src/emitter/emit_sm.h` | dead declaration |
| `src/emitter/emit_globals.h` | ~30 dead `xa_pl_*` per-call scalars |
| `src/runtime/rt/rt.c` | `rt_register_predicates_pl` + `rt_pl_b_*` + `rt_pl_b_sub_*` family (~210 LOC) |
| `src/runtime/rt/rt.h` | matching declarations |
| `Makefile` | 4 template `.cpp` source-list entries + 4 compile rules |

**Retirements (kept as marker entries — mirror existing `XA_PL_PREDICATE_REGISTRY` RETIRED pattern):**

- `XA_PL_KIDS_RODATA` → no-op dispatch in `emit_core.c`
- `XA_PL_SUB_BUILDER` → no-op dispatch in `emit_core.c`
- `XA_PL_BUILDER` → no-op dispatch in `emit_core.c`
- `XA_PL_REGISTRY_TABLE` → no-op dispatch in `emit_core.c`

Kept enum slots to avoid renumbering downstream opcodes.

**Stale comments refreshed:**
- `src/runtime/rt/rt.c` `rt_gc_init` comment
- `src/runtime/interp/pl_runtime.h:24` (g_pl_bb_table population path)
- `src/lower/lower.c:2108` (population path)

**Verified outcomes on `main :- X is 1+2, write(X), nl.`:**

| Metric | Before V-4 | After V-4 |
|--------|-----------|-----------|
| Emitted .s lines | 449 | **345** (-23%) |
| `call rt_pl_b_*` | 16 | **0** ✅ |
| `call rt_register_predicates_pl` | 1 | **0** ✅ |
| `call bb_exec_*` | 0 | 0 (unchanged) |
| Runs and prints `3` | ✓ | ✓ |
| FACT RULE grep | 0 | **0** ✅ |
| All remaining `rt_pl_b_*` source refs | live + comments | comments only |

**Gates HELD at `88f03a41`:**

- GATE-1 `test_smoke_prolog.sh`: **5/5** ✅
- GATE-2 `test_crosscheck_prolog.sh`: **132/0** ✅ (5 oracle-miss, pre-existing)
- GATE-3 `test_prolog_rung_suite.sh`: **88/107** ✅
- GATE-4 `test_prolog_mode4_rung.sh`: **4/4** ✅ (m4-seq, m4-call, m4-choice, m4-alt)
- Icon smoke: 5/5 ✅
- Icon rung suite (interp): 198/34/36/268 ✅
- Icon mode-4 rung: 5/5 ✅
- Unified broker: 24/50 (unchanged) ✅

---

## Violations ledger state

- V-1 ✅ Clause-body `BB_PL_SEQ` wrapper (Opus, this morning)
- V-2 ✅ `is/2` → `BB_ARITH` (Opus, this morning)
- V-3 ✅ Structural four-port templates filled (Sonnet, this afternoon)
- **V-4 ✅ `rt_pl_b_*` runtime path retired** (Sonnet, this session)
- **V-5 ⏳ Mode 3 (`--run`) still routes through C SM+BB walker (AGW-1c exception)** ← NEEDS LON DECISION (see below)
- V-6 ⏳ `pl_bb_dcg` C-walker audit (will follow trivially from V-5)

---

## ⛔ NEEDS LON DECISION — V-5 SCOPE

V-5 says: route Prolog `--run` through the same flat-emit path as mode 4, delete
the AGW-1c exception text from `RULES.md`, and confirm modes 3/4 don't reach
`pl_bb_dcg` / `bb_exec_*`.

The flat-emit path emits **GAS-syntax text assembly**, not raw machine bytes
(this is foundational — every byte comes from a template, FACT RULE). To execute
in-process, the emitted text must be turned into executable memory. There are
three credible paths and they have very different scope. Lon needs to call which:

### Option A — fork+exec (small, day's work)

Wire `mode_run && is_prolog` in `scrip.c` to:

1. Emit `.s` to a temp file via `sm_codegen_text` (already exists).
2. `fork` + `execve` to invoke `as` + `gcc -no-pie -lscrip_rt -lgc -lm -lstdc++`
   like `scripts/run_prolog_via_x86_backend.sh` does (or call the libelf+libas
   C-level equivalents to skip the subprocess).
3. `fork` + `execv` the resulting binary, `waitpid` for exit code, route its
   stdout/stderr.

**Pros:** Strictly satisfies V-5 — `sm_interp_run` and `bb_exec_*` are unreached
from the `--run` path. Reuses the existing mode-4 toolchain end-to-end. Minimal
new code.

**Cons:**
- **Per-invocation cost ~200-500 ms** (assemble + link + exec). The crosscheck
  script runs `--run` 132×; runtime goes from ~7s to 1-2 minutes. Acceptable for
  CI but painful for interactive workflows where Lon iterates.
- Two subprocess hops (`as`, `gcc`, then the binary). The temp .s/.o/.bin files
  add filesystem noise unless cleaned up explicitly.

### Option B — in-proc PROT_EXEC via embedded assembler (week's work)

Embed an x86-64 assembler (e.g. `libkeystone`, GNU `gas` linked as a library, or
a hand-written subset assembler for the instructions the templates emit). Pipe
the emitted text through it to get bytes, `mmap` `PROT_READ|PROT_WRITE` →
`mprotect` `PROT_READ|PROT_EXEC`, resolve `@PLT` calls to `rt_*` runtime
helpers via `dlsym`, jump in.

**Pros:** Zero subprocess overhead. Mode 3 becomes the fast-iteration native
path — what the GOAL document and J-2/J-3 phase notes actually anticipate
(`sm_codegen_x64_emit_test.c:18-21`). Solidifies the J-3 phase that was
documented but never built.

**Cons:** Substantial new code surface. Either pulls in an external dep
(`libkeystone`) or writes/maintains a subset assembler. The relocation logic
(PLT, RIP-relative, label fixups) is non-trivial. Cross-language: this becomes
the in-proc path for **every** language, not just Prolog. Other languages have
runtime quirks (Boehm GC frame requirements, `-no-pie` constraints) that need
the same treatment.

### Option C — leave V-5 open; refresh the RULES.md exception text instead

The AGW-1c exception in RULES.md was written when the bb_pl_*.cpp templates
were empty. With V-1..V-4 closed, the templates are filled and the runtime
graph-rebuild is gone. The reason Mode 3 still uses `sm_interp_run` for Prolog
is now **not** "templates missing" but **"in-proc executor for flat x86 not
yet built (J-3)"**. The exception text can be honestly updated to say so, and
V-5 deferred until J-3 lands generally (it would close mode-3 for every
language simultaneously).

**Pros:** Honest. No code change. Lets J-3 be sequenced against the rest of
the roadmap rather than rushed for one language.

**Cons:** AGW-1c stays open. Mode 3 Prolog continues to route through
`sm_interp_run` → `pl_bb_dcg` → `bb_exec_once` (the C walker), which RULES.md
treats as a temporary concession.

### Recommendation

**Option C if J-3 is on a near-term roadmap**, otherwise **A**. The session that
landed V-1..V-4 was inside a single day's work; the natural next priority is
**either** start J-3 (week's project, cross-language benefit) **or** move on to
PJ-AGW-5 / rung 18 / rung 27 / rung 28 (each pays down concrete user-visible
gaps). V-5 doesn't unlock any new Prolog behaviour — m4-seq/call/choice/alt are
already 4/4 green via mode 4.

Either way: **don't pick A and ship it without thinking about whether you want
Mode 3 to be the slow path or the fast path going forward.**

---

## Session start for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all
git clone https://TOKEN@github.com/snobol4ever/corpus   /home/claude/corpus
cat /home/claude/.github/PLAN.md
cat /home/claude/.github/GOAL-PROLOG-BB.md
cat /home/claude/.github/HANDOFF-2026-05-27-SONNET-PROLOG-BB-V4-CLOSED.md
sudo apt-get install -y libgc-dev
cd /home/claude/one4all && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1: 5/5
bash scripts/test_prolog_rung_suite.sh    # GATE-3: 88/107
bash scripts/test_prolog_mode4_rung.sh    # GATE-4: 4/4
bash scripts/test_crosscheck_prolog.sh    # GATE-2: 132/0
```

**Confirm `88f03a41` watermark:**

```bash
cd /home/claude/one4all && git log --oneline -1
# expect: 88f03a41 V-4: retire rt_pl_b_* runtime BB-rebuild path
```
