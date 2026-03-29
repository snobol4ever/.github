# MILESTONE-RENAME-ANY2MANY — Grand Rename: scrip-cc → scrip-cc, one4all → one4all

**Milestone:** M-G-RENAME-ANY2MANY  
**Session:** G-8 (2026-03-29, Claude Sonnet 4.6)  
**Status:** ⏳ IN PROGRESS

---

## Rationale

The old names were wrong in two dimensions:

- **`scrip-cc`** — implies SNOBOL4 → C. But the compiler accepts *any* of five
  languages (SNOBOL4, Snocone, Rebus, Icon, Prolog) and emits *all* backends
  (x86-64 asm, JVM bytecode, .NET IL, C) — potentially in **one invocation**
  from one IR tree. It is an **any-to-many** compiler, not a sno-to-c compiler.

- **`one4all`** — implies this is a SNOBOL4 extension project. It is a
  **polyglot compilation system**: five frontend languages, four backends,
  C interop in both directions, JVM and .NET as first-class targets.

## The New Identity

```
ANY²MANY²ONE
```

```
  ┌─────────────────────────────────────────┐
  │  ANY language  →  scrip-cc  →  MANY     │
  │  SNOBOL4 ╮                  ╭ x86-64    │
  │  Snocone  ├──► ONE IR ──────┤ JVM       │
  │  Rebus    │                 │ .NET IL   │
  │  Icon     │                 ╰ C         │
  │  Prolog  ─╯                             │
  └─────────────────────────────────────────┘
  
  MANY objects  →  scrip-ld  →  ONE executable
  (.o / .class / .dll / .so)
```

**Markdown badge style:**

> ## `ANY` **²** `MANY` **²** `ONE`
> *scrip-cc · scrip-ld · one4all*

**Coined phrases (for README, docs, future logo):**
- **ANY²MANY** — the compiler direction: any source language, many backend outputs
- **MANY²ONE** — the linker direction: many language objects, one executable
- **ANY²MANY²ONE** — the full pipeline, end to end

This naming is unique. gcc is one-to-one. LLVM is many-to-many but not
*simultaneously* from one IR pass. scrip-cc builds the IR **once** and hands it
to N backends in a single invocation — an optimization gcc has no equivalent of.

---

## Rename Map

| Old | New | Where |
|-----|-----|-------|
| `scrip-cc` (binary) | `scrip-cc` | Makefile BIN, all shell scripts, all .md |
| `scrip-cc_icon` (binary) | `scrip-cc-icon` | Makefile ICON_BIN |
| `scrip-cc.h` (header) | `scrip_cc.h` | src/frontend/snobol4/, all #include sites |
| `one4all` (repo/dir) | `one4all` | all .md, all .sh, PLAN.md table |
| `scrip-cc -asm` | `scrip-cc -asm` | generated file headers, docs |

**snobol4ever** (GitHub org name) — **not changed** in this milestone.
Org rename is a separate GitHub operation (Lon to do manually).

---

## Files Changed

### .github repo
- [ ] PLAN.md — repo table, session table, all scrip-cc refs
- [ ] GRAND_MASTER_REORG.md — all scrip-cc/one4all refs
- [ ] SESSION_BOOTSTRAP.sh — binary name
- [ ] All SESSION-*.md, ARCH-*.md, REPO-*.md
- [ ] This milestone doc

### one4all → one4all repo
- [ ] src/Makefile — BIN, ICON_BIN
- [ ] src/frontend/snobol4/scrip-cc.h → scrip_cc.h
- [ ] All #include "scrip-cc.h" → #include "scrip_cc.h"
- [ ] src/driver/main.c — self-identification strings
- [ ] All .sh scripts
- [ ] All .md docs
- [ ] Generated .s/.j/.il comment headers (--update pass)

### harness repo
- [ ] All .sh, .md refs

### corpus repo  
- [ ] All .sh, .md refs

---

## Completion Criteria

1. `grep -r "scrip-cc" --include="*.md" --include="*.sh" --include="*.c" --include="*.h"` → 0 hits (excluding generated .s/.j/.il headers and .git/)
2. `grep -r "one4all" --include="*.md" --include="*.sh"` → 0 hits
3. `make` in `src/` produces binary named `scrip-cc`
4. `scrip-cc -asm test/snobol4/hello/hello.sno` works
5. SESSION_BOOTSTRAP.sh updated and functional
6. Commit: `G-8: M-G-RENAME-ANY2MANY ✅ — scrip-cc→scrip-cc, one4all→one4all`

