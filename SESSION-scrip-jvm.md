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

## §NOW — SD-34

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Scrip Demo** | SD-34 — M-SD-5 🔄 fibonacci | `f8e74fc` SD-33 | M-SD-5 |

### Status

| Demo | SNOBOL4 | SWIPL | ICONT | SNO2C-JVM | ICON-JVM | PROLOG-JVM |
|------|:-------:|:-----:|:-----:|:---------:|:--------:|:----------:|
| DEMO1 hello | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO2 wordcount | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO3 roman | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO4 palindrome | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO5 fibonacci | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### NEXT ACTION — SD-34: M-SD-5 fibonacci

Run demo5 across all three JVM frontends. Check demo/scrip/demo5/ for source + expected.



