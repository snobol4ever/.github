# SNOBOL4-plus — Directory

> **New Claude session? Read this file first. Then jump directly to what you need.**
> Everything lives in `PLAN.md`. This file tells you where.

---

## 1. Session Start (every session, in order)

| What | Where |
|------|-------|
| Clone all six repos | `PLAN.md` § Session Start — Clone All Repos |
| Build CSNOBOL4 + SPITBOL oracles | `PLAN.md` § Session Start — Build Oracles |
| Git identity + token decode | `PLAN.md` § Git Identity |
| Current work — what's next | `PLAN.md` § Outstanding Items (P1/P2/P3) |

---

## 2. What This Org Is

| What | Where |
|------|-------|
| Mission + people | `PLAN.md` § What This Organization Is |
| All repos at a glance | `PLAN.md` § Repository Index |
| Setup history | `PLAN.md` § Organization Setup Log |

---

## 3. Per-Repo Plans (read the one you're working in)

| Repo | Where |
|------|-------|
| **SNOBOL4-jvm** — Clojure, full SNOBOL4→JVM | `PLAN.md` § SNOBOL4-jvm — Full Plan |
| **SNOBOL4-dotnet** — C#, full SNOBOL4→MSIL | `PLAN.md` § SNOBOL4-dotnet — Full Plan |
| **SNOBOL4-tiny** — native compiler, Byrd Box | `PLAN.md` § SNOBOL4-tiny — Full Plan |
| **Snocone** — C-like sugar front-end (both targets) | `PLAN.md` § Snocone Front-End Plan |
| **SNOBOL4-python** — pattern library, PyPI | `PLAN.md` § SNOBOL4-python — Plan |
| **SNOBOL4-cpython** — CPython C extension, Byrd Box engine | `PLAN.md` § Architecture Decisions Log (D5) |
| **SNOBOL4-csharp** — pattern library, C# | `PLAN.md` § SNOBOL4-csharp — Plan |
| **SNOBOL4-corpus** — shared programs + benchmarks | `PLAN.md` § SNOBOL4-corpus — Plan |

---

## 4. Protocols (reference when needed)

| What | Where |
|------|-------|
| Commit + push every change | `PLAN.md` § Standing Instruction — Small Increments |
| Save state mid-session | `PLAN.md` § Directive: SNAPSHOT |
| End of session cleanly | `PLAN.md` § Directive: HANDOFF |
| Something broke, exit fast | `PLAN.md` § Directive: EMERGENCY HANDOFF |
| How to declare a snapshot | `PLAN.md` § Snapshot Protocol |
| How to write a handoff prompt | `PLAN.md` § Handoff Protocol |

---

## 5. Key Design References

| What | Where |
|------|-------|
| Byrd Box α/β/γ/ω model | `SNOBOL4-tiny/doc/DESIGN.md` |
| Bootstrap strategy (seed→self-hosting) | `SNOBOL4-tiny/doc/BOOTSTRAP.md` |
| Architecture decisions (resolved) | `SNOBOL4-tiny/doc/DECISIONS.md` |
| **The Double-Trace Monitor** — the story, architecture, telemetry loop | `HQ/MONITOR.md` |
| **Runtime patch log** — every bug found, root cause, fix, commit | `HQ/PATCHES.md` |
| String escape rules (SNOBOL4 / C / Python) | `HQ/STRING_ESCAPES.md` |
| Compiland reachability (inc files → C) | `HQ/COMPILAND_REACHABILITY.md` |
| Snocone semantic rules + label gen | `PLAN.md` § Key Semantic Rules (from Koenig spec) |
| JVM design decisions (immutable) | `PLAN.md` § Design Decisions (Immutable) — SNOBOL4-jvm |
| JVM tradeoff prompt (read before every JVM decision) | `PLAN.md` § Tradeoff Prompt — SNOBOL4-jvm |
| Dotnet token type reference | `PLAN.md` § Token.Type Reference — SNOBOL4-dotnet |

---

## 6. Key Ideas (read before starting runtime work)

| Idea | Where | Status |
|------|-------|--------|
| **The Pick Monitor** — pipe-based live execution monitor with ignore-points | `PLAN.md` § IDEA — The Pick Monitor | **NEXT for Sprint 20 hang diagnosis** |
| Separate backtrack stack (FlatLoopEmitter) | `PLAN.md` § Separate Backtrack Stack vs Call Stack | Planned post-Sprint 20 |
| Automata theory oracles (Chomsky tier proofs) | `PLAN.md` § Automata Theory Oracles | Sprints 6–13 done |
| PDA benchmark vs YACC/Bison | `PLAN.md` § PDA Benchmark | Done — 20× |
| RE benchmark vs PCRE2 | `PLAN.md` § RE Performance Benchmark | Done — 2.3× |
| Exhaustive + random testing (Flash BASIC precedent) | `PLAN.md` § Exhaustive and Random Testing | Planned |
| nPush / Shift / Reduce as engine nodes | `PLAN.md` § IDEA — nPush / Shift / Reduce | Sprint 10–11 |

---

## 7. Sprint 20 — Current State (as of 2026-03-10)

**Goal:** `snoc` compiles Beautiful.sno → binary self-beautifies idempotently.

**Oracle established:**
```bash
cd /home/claude/work/SNOBOL4-corpus/programs/inc
snobol4 -f -P256k beauty_run.sno < beauty_run.sno > /tmp/pass1.txt  # 649 lines, exit 0
snobol4 -f -P256k beauty_run.sno < /tmp/pass1.txt > /tmp/pass2.txt  # 649 lines, exit 0
diff /tmp/pass1.txt /tmp/pass2.txt                                   # empty — IDEMPOTENT ✓
```

**Binary status:** `beautiful` compiles and links cleanly (zero errors).
**Runtime status:** `./beautiful < beauty_run.sno` hangs — timeout exit 124.
**Next action:** Implement the Pick Monitor to find the hang point.

**Compile command:**
```bash
cd /home/claude/work/SNOBOL4-tiny/src/runtime/snobol4
cc -o beautiful beautiful.c snobol4.c snobol4_pattern.c snobol4_inc.c \
   ../engine.c ../runtime.c -I. -I.. -lgc -lm
```

**Paths:**
```
SNOBOL4-tiny/src/runtime/snobol4/beautiful.c     ← generated C
SNOBOL4-tiny/src/runtime/snobol4/snobol4.c       ← runtime (add sno_comm_* here)
SNOBOL4-tiny/src/codegen/emit_c_stmt.py          ← code generator (add COMM calls here)
SNOBOL4-tiny/src/parser/sno_parser.py            ← parser
SNOBOL4-corpus/programs/inc/beauty_run.sno       ← test driver
SNOBOL4-corpus/programs/sno/beauty.sno           ← the program itself
```

---

## 8. Current Baselines (update at every handoff)

| Repo | Tests | Last commit |
|------|-------|-------------|
| SNOBOL4-dotnet | 1,607 / 0 | `63bd297` |
| SNOBOL4-jvm | 1,896 / 4,120 assertions / 0 | `9cf0af3` |
| SNOBOL4-cpython | 70+ / 0 | `330fd1f` |
| SNOBOL4-tiny | Sprint 20: binary links, runtime hangs | `6bb88d9` |

---

## 9. What To Do Next (update at every handoff)

> **COURSE CORRECTION 2026-03-10**: We skipped to Level 3 (beautiful.c / Sprint 20)
> before proving Level 1 and Level 2. The three-level strategy is now the plan.
> See `PLAN.md` § The Three-Level Proof Strategy.
>
> **NEXT ACTION**: Build Level 1 test — no INC, no funcs, no statements.
> Simple pattern + OUTPUT. Run oracle (CSNOBOL4). Run binary. Diff. Zero diffs = certified.
> Also: commit `beauty_run.sno` to SNOBOL4-tiny repo.

**SNOBOL4-tiny — Sprint 20 (CURRENT FOCUS):**
1. Implement the Pick Monitor (`PLAN.md` § IDEA — The Pick Monitor)
   - Add `sno_comm_*` to `snobol4.c`
   - Add `sno_comm_line(N)` to `emit_c_stmt.py` (regenerate `beautiful.c`)
   - Write `monitor.py` — Tkinter GUI, pipe reader, ignore-list, STEP/RUN/IGNORE
2. Run `./beautiful --monitor | python monitor.py < beauty_run.sno`
3. Find and fix the hang

**SNOBOL4-tiny — Sprint 21 (after hang is fixed):**
- DEFINE dispatch: `sno_apply("pp",...)` must call compiled C label

**SNOBOL4-jvm / dotnet:**
- Snocone Step 3 — `if/else` → label/goto pairs (both targets)

**Org:**
- Jeffrey needs to accept GitHub org invitation → promote to Owner
