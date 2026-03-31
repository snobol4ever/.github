# SESSION-icon-x64.md — Icon × x86 (one4all)

**Repo:** one4all · **Frontend:** Icon · **Backend:** x86
**Session prefix:** `IX` · **Trigger:** "playing with Icon x64" or "Icon asm"
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| x64 emitter patterns | `BACKEND-X64.md` | codegen, register model |
| JCON deep analysis | `ARCH-icon-jcon.md` | four-port templates |

---

## §BUILD

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

All tools, repos, and oracles installed by bootstrap. scrip-cc at `/home/claude/one4all/scrip-cc`.

---

## §NOW — IX-18

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-18 | `c648df5` | rung10–35 all green on x64 backend |

**The JVM backend has rung01–35 all 5/5 ✅. The x64 backend (`icon_emit.c`) is younger — rung01–09 pass, rung10 ✅ (IX-17), rung11–35 mostly ❌.**

### Failure taxonomy (priority order for IX-18)

1. **`ICN_STR`/`ICN_CSET` rdi/push duality (~15 tests)** — `emit_str` leaves pointer in rdi instead of pushing. Fix: make `emit_str` push like all other nodes (`push rdi` after `lea`), remove all `rhs_is_str`/`left_is_str` special-cases.
2. **`ICN_BANG` unimplemented (~8 tests)** — `!str` generator: implement string-only via BSS index counter.
3. **String relops `ICN_SLT/SLE/SGT/SGE/SNE` (~5 tests)** — add `icn_str_lt` etc. to `icon_runtime.c`, wire dispatch.
4. **`ICN_SIZE` (~2 tests)** — `*E`: add `icn_str_len`, wire dispatch.
5. **`ICN_LIMIT` (~4 tests)** — `E \ N`: BSS counter per node, wire dispatch.
6. **`ICN_SEQ_EXPR` (~4 tests)** — emit each subexpr, keep last value.
7. **`ICN_INITIAL` (~2 tests)** — BSS flag per proc, runs once.
8. **`ICN_NONNULL` (~2 tests)** — `\E`: identity except makes non-null explicit.
9. **write() type dispatch (~10 tests)** — after fixing #1, use inferred type for `icn_write_str` vs `icn_write_int`.

**Files:** `src/frontend/icon/icon_emit.c` · `src/frontend/icon/icon_runtime.c`

**Harness:**
```bash
bash test/frontend/icon/run_icon_x64_rung.sh \
  test/frontend/icon/corpus/rung10_augop \
  test/frontend/icon/corpus/rung11_bang_augconcat \
  ... (rung10–35)
```
