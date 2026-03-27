# SESSION-scrip-jvm.md — Scrip Demos × JVM (snobol4x)

**Repo:** snobol4x · **Frontends:** SNOBOL4 + Icon + Prolog · **Backend:** JVM
**Session prefix:** `SD` · **Trigger:** "playing with Scrip demos, JVM backend"
**Harness:** `bash demo/scrip/run_demo.sh demo/scrip/demoN/`
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Demo ladder, firing conditions | `SCRIP_DEMOS.md` | milestone map, expected outputs |
| Icon×JVM emitter §NOW | `SESSION-icon-jvm.md` | Icon block fails in harness |
| Prolog×JVM emitter §NOW | `SESSION-prolog-jvm.md` | Prolog block fails in harness |
| SNOBOL4×JVM emitter §NOW | `SESSION-snobol4-jvm.md` | SNOBOL4 block fails in harness |
| Icon deep reference | `ARCH-icon-jcon.md` | unfamiliar Icon/JCON construct |
| Prolog JVM runtime | `ARCH-jvm-prolog.md` | unfamiliar Jasmin/Prolog pattern |

---

## §BUILD

```bash
cd snobol4x && make -C src
apt-get install -y default-jdk swi-prolog icont
export JAVA_TOOL_OPTIONS=""
SNO2C=$(pwd)/sno2c
ICON_DRIVER=$(pwd)/icon_driver
JASMIN=$(pwd)/src/backend/jvm/jasmin.jar
```

## §RUN

```bash
SNO2C=snobol4x/sno2c ICON_DRIVER=snobol4x/icon_driver \
  JASMIN=snobol4x/src/backend/jvm/jasmin.jar \
  bash demo/scrip/run_demo.sh demo/scrip/demo3/
```

## Milestone firing condition

M-SD-N fires when all six pass:
- SNOBOL4 ✅ · SWIPL ✅ · ICONT ✅ · SNO2C-JVM ✅ · ICON-JVM ✅ · PROLOG-JVM ✅
- Output matches `demo/scrip/demoN/NAME.expected`

---

## §NOW — SD-27

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Scrip Demo** | SD-27 — M-SD-3 🔄 roman | `51e38fc` | M-SD-3 |

### Status

| Demo | SNOBOL4 | SWIPL | ICONT | SNO2C-JVM | ICON-JVM | PROLOG-JVM |
|------|:-------:|:-----:|:-----:|:---------:|:--------:|:----------:|
| DEMO1 hello | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO2 wordcount | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO3 roman | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

### NEXT ACTION — SD-28: fix ICON-JVM blocker, fire M-SD-3

**Blocker:** `vals[i]` list subscript → `Bad type in putfield/putstatic` VerifyError
**Fix location:** `ij_emit_subscript()` in `src/frontend/icon/icon_emit_jvm.c` — list path
**Minimal repro:** `vals := [10,5,1]; i := 1; write(vals[i]);`
**Does NOT affect:** string subscript, table subscript, `!L` bang generator

```bash
# After fix — confirm 6/6:
SNO2C=snobol4x/sno2c ICON_DRIVER=snobol4x/icon_driver \
  JASMIN=snobol4x/src/backend/jvm/jasmin.jar \
  bash demo/scrip/run_demo.sh demo/scrip/demo3/
# Then fire M-SD-3: update PLAN.md, SCRIP_DEMOS.md §NOW, SESSIONS_ARCHIVE, MILESTONE_ARCHIVE
```
