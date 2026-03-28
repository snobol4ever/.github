# SESSION-icon-x64.md — Icon × x64 ASM (snobol4x)

**Repo:** snobol4x · **Frontend:** Icon · **Backend:** x64 ASM
**Session prefix:** `IX` · **Trigger:** "playing with Icon x64" or "Icon asm"
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| x64 emitter patterns | `BACKEND-X64.md` | codegen, register model |
| JCON deep analysis | `ARCH-icon-jcon.md` | four-port templates |

---

## §BUILD

**Compiler is `sno2c` (built from `src/`). Frontend module is `src/frontend/icon/icn_main.c`.**

```bash
# Clone
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github

# Build
cd snobol4x/src && make
# produces ../sno2c
```

### Run a single test (JVM backend — canonical test path)

```bash
TMPD=$(mktemp -d)
./sno2c -jvm foo.icn -o $TMPD/main.j
for jf in $TMPD/*.j; do java -jar src/backend/jvm/jasmin.jar "$jf" -d $TMPD/; done
cls=$(grep -m1 '\.class' $TMPD/main.j | awk '{print $NF}')
java -cp $TMPD/ "$cls"
```

Note: always assemble **all** `.j` files in the output dir — record types emit
companion `ClassName$RecordType.j` files that must be assembled alongside `main.j`.

### Run a corpus rung

```bash
JASMIN=src/backend/jvm/jasmin.jar; PASS=0; FAIL=0
for icn in test/frontend/icon/corpus/RUNG/t*.icn; do
  base="${icn%.icn}"; exp="$base.expected"; [ -f "$exp" ] || continue
  [ -f "$base.xfail" ] && continue
  TMPD=$(mktemp -d)
  ./sno2c -jvm "$icn" -o $TMPD/main.j 2>/dev/null
  for jf in $TMPD/*.j; do java -jar $JASMIN "$jf" -d $TMPD/ >/dev/null 2>&1; done
  cls=$(grep -m1 '\.class' $TMPD/main.j | awk '{print $NF}')
  stdin_f="$base.stdin"
  [ -f "$stdin_f" ] && got=$(timeout 5 java -cp $TMPD/ "$cls" < "$stdin_f" 2>/dev/null) \
                    || got=$(timeout 5 java -cp $TMPD/ "$cls" 2>/dev/null)
  want=$(cat "$exp")
  [ "$got" = "$want" ] && { echo "PASS $(basename $icn)"; PASS=$((PASS+1)); } \
                       || { echo "FAIL $(basename $icn)"; FAIL=$((FAIL+1)); }
  rm -rf $TMPD
done
echo "--- PASS=$PASS FAIL=$FAIL ---"
```

---

## §NOW — IX-16

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-16 — M-IX-LOOPS ✅ | `3a548ef` | rung03_suspend CE triage |

### Baseline (confirmed IX-15 / IX-15b)

| Rung | Result |
|------|--------|
| rung01_paper | **6/6 ✅** |
| rung02_arith_gen | **5/5 ✅** |
| rung02_proc | **3/3 ✅** |
| rung03_suspend | 3/5 CE — 2 linker failures (pre-existing) |
| rung04–08 | **all 5/5 ✅** |
| rung09_loops | **5/5 ✅** (was 0/5 — `emit_until` implemented) |
| rung10–23 | **all 5/5 ✅** |
| rung24_records | **5/5 ✅** (was 0/5 — record type prepass fix) |
| rung25–26 | **all ✅** |
| rung27_read | **5/5 ✅** (was 4/5 — `reads()` slot_jvm bug fixed) |
| rung28–31 | **all 5/5 ✅** (rung31 was 3/5 — same record fix) |
| rung32–35 | **all ✅** |
| rung36_jcon | 2/52 — jcon subsystem, separate milestone |

### What was fixed (IX-15 + IX-15b, commits `75cfd68` → `3a548ef`)

**M-IX-LOOPS — emit_until (rung09 5/5)**
- `icon_emit.c`: `emit_until()` added, `ICN_UNTIL` wired in dispatch
- `until E do body`: α→cond.α; cond.γ→discard+exit; cond.ω→body.α; body.γ/ω→loop_top

**Rename: `icon_driver` eradicated**
- `src/frontend/icon/icon_driver.c` → `icn_main.c`; function `icn_main()` (was `icon_driver_main`)
- All 46 affected files swept (shell scripts, Makefile, comments, stale binary removed)

**Record type prepass fix (rung24/31)**
- `ij_prepass_types` missing `ij_expr_is_record(rhs)` branch — record vars fell to `'J'` default
- Fix: detect record RHS → `ij_declare_static_obj(fld)` with dual local/global register

**`reads()` slot bug (rung27 t04)**
- `arr_slot` from `ij_alloc_ref_scratch()` is raw JVM slot; wrongly wrapped in `slot_jvm()`
- Fix: use `arr_slot` directly on both `aload` sites

### NOTE: test harness — companion .j assembly required

Record types emit companion `ClassName$RecordType.j` files alongside `main.j`.
Must assemble **all** `.j` files in TMPD and use TMPD as `-cp`. See §BUILD.

### NEXT ACTION — IX-16: rung03_suspend CE triage

Two tests in rung03 produce CE (Jasmin error or runtime crash). Diagnose each,
identify missing emitter feature or linker gap, fix or xfail with reason.
