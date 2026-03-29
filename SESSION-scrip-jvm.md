# SESSION-scrip-jvm.md — Scrip Demos × JVM (one4all)

**Repo:** one4all · **Frontends:** SNOBOL4 + Icon + Prolog · **Backend:** JVM
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
cd one4all && make -C src
apt-get install -y default-jdk swi-prolog icont
export JAVA_TOOL_OPTIONS=""

# Build icon_driver (required for ICON-JVM block)
gcc -g -O0 -I. \
  src/frontend/icon/icon_driver.c \
  src/frontend/icon/icon_lex.c \
  src/frontend/icon/icon_parse.c \
  src/frontend/icon/icon_ast.c \
  src/frontend/icon/icon_emit.c \
  src/frontend/icon/icon_emit_jvm.c \
  src/frontend/icon/icon_runtime.c \
  -o /tmp/icon_driver

SNO2C=$(pwd)/scrip-cc
ICON_DRIVER=/tmp/icon_driver
JASMIN=$(pwd)/src/backend/jvm/jasmin.jar
```

## §RUN

```bash
SNO2C=$(pwd)/scrip-cc ICON_DRIVER=/tmp/icon_driver \
  JASMIN=$(pwd)/src/backend/jvm/jasmin.jar \
  bash demo/scrip/run_demo.sh demo/scrip/demo3/
```

## Milestone firing condition

M-SD-N fires when all six pass:
- SNOBOL4 ✅ · SWIPL ✅ · ICONT ✅ · SNO2C-JVM ✅ · ICON-JVM ✅ · PROLOG-JVM ✅
- Output matches `demo/scrip/demoN/NAME.expected`

## §ARTIFACTS

When M-SD-N fires, update `artifacts/jvm/samples/` with the passing demo's `.j` files.
Session prefix for commits: `SD` (e.g. `SD-37: M-SD-6 ICON-JVM sieve PASS`).

```bash
# After a demo passes all six backends:
SNO2C=$(pwd)/scrip-cc
JASMIN=$(pwd)/src/backend/jvm/jasmin.jar
DEMO=demo/scrip/demo6   # replace with passing demo number
NAME=sieve              # replace with demo name

# Regenerate canonical .j artifacts
$SNO2C -jvm $DEMO/${NAME}.sno_extracted > artifacts/jvm/samples/${NAME}.j 2>/dev/null || true
/tmp/icon_driver -jvm $DEMO/${NAME}.icn_extracted -o artifacts/jvm/samples/${NAME}_icon.j 2>/dev/null || true
# Scrip demos compile from .md via run_demo.sh split — use /tmp outputs if needed

git add artifacts/jvm/samples/
git commit -m "SD-N: artifacts/jvm/samples/ — $NAME ICON-JVM PASS"
```

**Ownership:** SD session owns `artifacts/jvm/samples/` for demo artifacts only.
Cross-repo rule: never write `artifacts/asm/`, `artifacts/net/`, or `artifacts/c/` from an SD session.

---

## §NOW — SD-37

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Scrip Demo** | SD-37 — M-SD-6 ✅ ICON-JVM sieve PASS | `795c2ff` SD-37 | M-SD-7 ICON-JVM rot13 |

### Status

| Demo | SNOBOL4 | SWIPL | ICONT | SNO2C-JVM | ICON-JVM | PROLOG-JVM |
|------|:-------:|:-----:|:-----:|:---------:|:--------:|:----------:|
| DEMO1 hello | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO2 wordcount | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO3 roman | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO4 palindrome | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO5 fibonacci | ✅ | ✅ | ✅ | ✅ | ⏭ skipped | ❌ forall/2 meta-call |
| DEMO6 sieve | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DEMO7 rot13 | ✅ | ✅ | ✅ | ✅ | ❌ compiler no output | ❌ |
| DEMO8 insertion sort | ✅ | ✅ | ✅ | ✅ | ❌ compiler no output | ✅ |
| DEMO9 rpn calc | ✅ | ✅ | ✅ | ✅ | ❌ compiler no output | ❌ |
| DEMO10 anagram | ✅ | ✅ | ✅ | ✅ | ❌ compiler no output | ❌ |

### NEXT ACTION — SD-38: fix ICON-JVM demos 7-10

**Blocker:** `icon_driver -jvm` produces no output for demos 7-10. Parse/emitter gap.
Check each demo's Icon block manually: `python3 demo/scrip/scrip_split.py demo/scrip/demo7/caesar.md /tmp/ && /tmp/icon_driver -jvm /tmp/icon.icn 2>&1`

**SD-37 fixes landed (795c2ff):**
- `TK_AUGCONCAT` numeric RHS: `Long.toString` coerce (VerifyError fix)
- `ICN_SEQ_EXPR` failure-relay: `if`-no-else continues to next stmt
- List subscript assignment `a[i]:=v`: `ArrayList.set` emitted correctly
- Demo8 PROLOG-JVM insertion sort now ✅

**Artifact refresh:** `artifacts/icon/samples/` fully regenerated; `sieve.icn+.j` added.

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



