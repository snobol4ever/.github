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
| Prolog JVM runtime | `ARCH-prolog-jvm.md` | unfamiliar Jasmin/Prolog pattern |

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

## §NOW — SD-35

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Scrip Demo** | SD-35 — M-SD-6 🔄 sieve ICON-JVM fix | `5d900b8` SD-34 | M-SD-6 |

### Status

| Demo | SNOBOL4 | SWIPL | ICONT | SNO2C-JVM | ICON-JVM | PROLOG-JVM |
|------|:-------:|:-----:|:-----:|:---------:|:--------:|:----------:|
| DEMO1 hello | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO2 wordcount | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO3 roman | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO4 palindrome | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO5 fibonacci | ✅ | ✅ | ✅ | ✅ | ⏭ skipped | ❌ forall/2 meta-call |
| DEMO6 sieve | ✅ | ✅ | ✅ | ✅ | ❌ VerifyError | ✅ |
| DEMO7 rot13 | ✅ | ✅ | ✅ | ✅ | ❌ untested | ❌ |
| DEMO8 insertion sort | ✅ | ✅ | ✅ | ✅ | ❌ untested | ✅ |
| DEMO9 rpn calc | ✅ | ✅ | ✅ | ✅ | ❌ untested | ❌ |
| DEMO10 anagram | ✅ | ✅ | ✅ | ❌ | ❌ untested | ❌ |

### NEXT ACTION — SD-35: fix ICON-JVM demo6 sieve VerifyError

**Blocker:** `out ||:= i` where `out` is String and `i` is long (integer).
String concat augmented-assign with integer RHS → VerifyError "Expecting to find object/array on stack".
**Fix location:** `ij_emit_jvm.c` — augmented string concat (`||:=`) when RHS is numeric type needs `Long.toString()` coercion before concat.
**Also pending:** PROLOG-JVM demo5 forall/2 — `pj_call_goal` doesn't bind variable `N` across `between` iterations.
**Also pending:** demos 7, 9, 10 Prolog failures; demo 10 SNO2C failure.

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



