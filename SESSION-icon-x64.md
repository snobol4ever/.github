# SESSION-icon-x64.md — Icon × x64 ASM (snobol4x)

**Repo:** snobol4x · **Frontend:** Icon · **Backend:** x64 ASM
**Session prefix:** `I` · **Trigger:** "playing with Icon" (x64 only)

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| x64 emitter patterns | `BACKEND-X64.md` | codegen, register model |
| JCON deep analysis | `ARCH-icon-jcon.md` | four-port templates, IR vocab |

---

## §BUILD

```bash
cd snobol4x && bash setup.sh
gcc -Wall -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_runtime.c \
    -o /tmp/icon_driver_asm
```

## §TEST

```bash
# Baseline rung01-03 (15/15):
bash test/frontend/icon/run_rung01.sh /tmp/icon_driver_asm
bash test/frontend/icon/run_rung02.sh /tmp/icon_driver_asm
bash test/frontend/icon/run_rung03.sh /tmp/icon_driver_asm
```

---

## §NOW — I-11

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | I-11 — rung03 ✅ | `bab5664` | M-ICON-STRING |

### NEXT ACTION — I-12: M-ICON-STRING

Implement `ICN_STR` node + `||` concat via `CAT2_*` macros.
Add rung04 string corpus tests. Fire M-ICON-STRING.

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
bash /home/claude/snobol4x/setup.sh
# Confirm rung03 5/5: bash test/frontend/icon/run_rung03.sh /tmp/icon_driver_asm
# Implement M-ICON-STRING → fire
```
