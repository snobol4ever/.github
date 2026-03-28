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

## §NOW — IX-17

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon x64** | IX-17 | `3e4f131` | rung10–35 full scan with correct harness |

### Baseline (confirmed IX-16)

| Rung | Result |
|------|--------|
| rung01_paper | **6/6 ✅** |
| rung02_arith_gen | **5/5 ✅** |
| rung02_proc | **3/3 ✅** |
| rung03_suspend | **5/5 ✅** (was 3/5 CE — suspend body ω routing fixed) |
| rung04–09 | **all 5/5 ✅** |
| rung10–23 | **all 5/5 ✅** |
| rung24_records | **5/5 ✅** |
| rung25–26 | **all ✅** |
| rung27_read | **5/5 ✅** |
| rung28–31 | **all 5/5 ✅** |
| rung32–35 | **all ✅** |
| rung36_jcon | 2/52 — jcon subsystem, separate milestone |

### What was fixed (IX-16, commit `3e4f131`)

**rung03_suspend — suspend body ω routing (5/5)**

`ij_emit_suspend` body wiring had two bugs:
- `bp.ω = ports.γ` — body failure (empty stack) jumped to `body_drain` (which does `pop2`) → VerifyError
- `body_done: pop2; JGoto(ports.γ)` — after draining body result, jumped to `body_drain` again → double pop2

Fix: both paths now target `ports.ω` (= while's `loop_top`, no-value path):
- `bp.ω = ports.ω` — body fail bypasses drain
- `body_done: pop2; JGoto(ports.ω)` — body ok: drain once then loop-back
- no-body resume: `JGoto(ports.ω)`

### NEXT ACTION — IX-17

All rungs 01–35 now passing (rung36_jcon is a separate subsystem).
Next: run the full rung10–35 scan with correct companion-.j harness to confirm
no regressions from IX-15/16 fixes, then update SESSION with final baseline.
