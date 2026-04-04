# SESSION-icon-jvm.md — Icon × JVM (one4all)

**Repo:** one4all · **Frontend:** Icon · **Backend:** JVM (Jasmin)
**Session prefix:** `IJ` · **Trigger:** "playing with Icon JVM"
**Driver:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (x64 ASM backend)
**Deep reference:** all ARCH docs cataloged in `PLAN.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `PARSER-ICON.md` | parser/AST questions |
| Full milestone history | `ARCH-icon-jvm.md` | completed work, milestone IDs |
| JCON test analysis | `MISC-ICON-JCON.md` | rung36 oracle, four-port templates |
| JVM bytecode patterns | `GENERAL-OVERVIEW.md` | Byrd box → JVM mapping |

---

## §BUILD

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

All tools, repos, and oracles installed by bootstrap. scrip-cc at `/home/claude/one4all/scrip-cc`.


## §TEST

```bash
bash test/frontend/icon/run_bench_rung36.sh /tmp/icon_driver
# Shows full 75-test ladder; [B] marks benchmark-class tests
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | JVM emitter — main work file |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box oracle |
| `src/backend/jvm/jasmin.jar` | Assembler |
| `test/frontend/icon/corpus/rung36_jcon/` | 75-test JCON oracle corpus |
| `test/frontend/icon/run_bench_rung36.sh` | Full ladder + benchmark harness |

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-58 — M-IJ-JCON-HARNESS 🔄 | `5b32daa` IJ-58 | M-IJ-JCON-HARNESS |

### IJ-58 progress — rung36 75-test ladder

**PASS=2 WO=21 VE=48 CE=3 / 75 total** (t01_primes, t72_proto)

**Fixes landed this session (5b32daa):**
- Multi-arg `write` relay chain with jump-over-relay-blocks
- `icn_builtin_parse_long`: trim + radix (`NNrXX`) + sentinel failure
- `integer()` sentinel-based fail on bad parse
- `ij_expr_is_string(write)`: uses last arg not first (fixes `pop`/`pop2` drain)
- `TK_AUGPOW`: static D field temp replaces invalid `swap`-on-double
- Comparison augops (`=:=` `<:=` `<=:=` `>:=` `>=:=` `~=:=` `==:=` etc.): proper emit
- `left()`/`right()`/`center()`: coerce numeric `sarg` to String at `mid` label
- `ij_var_field`/`ij_gvar_field`: sanitize `&` in keyword names (fixes LinkageErrors)
- `IjBuf` forward-emit infrastructure ready to deploy
- `run_bench_rung36.sh`: full 75-test harness with `[B]` benchmark flags

**NOTE: icon_driver.c now integrated into scrip-cc. Build requires shim main + `-Isrc/frontend/snobol4`.**

**Benchmark-class tests [B]:** t01 t27 t28 t39 t54 t66 t70 — all VE/WO, blocked by VE fixes.

**VE breakdown (48 total):**
- "Expecting to find object/array" (~25): type-mismatch bugs in builtins (numeric arg where String expected)
- "Unable to pop off empty stack" (7): live-code stack-merge → needs forward-emit deploy
- LinkageError (~9): `&`-in-field-name — `ij_gvar_field` partial; ~29 raw snprintf sites remain

**NEXT ACTION — IJ-58:**
1. Bulk replace 29 `snprintf(X,sizeof X,"icn_gvar_%s",Y.val.sval)` → `ij_gvar_field(Y.val.sval,X,sizeof X)`  → kills ~9 LinkageErrors
2. Fix remaining "Expecting object/array" VEs in scan/image/other builtins
3. Deploy `IjBuf` forward-emit at `ij_emit_alt` → kills 7 "Unable to pop" VEs
4. `image()` quoting fix → unblocks many WO tests

### Bootstrap IJ-58 (next session)

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

---

## §JVM-NULL — sno_array_get returns null for uninitialized slots

`sno_array_get` returns Java `null` for uninitialized slots. In SNOBOL4 semantics, uninitialized = empty string `""`.

**Rule:** Any JVM emitter path that calls `sno_array_get` and then invokes a String method (`.equals`, `.contains`, concatenation) on the result **must** emit a null→`""` coerce inline first: `dup / ifnonnull / pop / ldc ""`.

`sno_indr_get` already coerces internally — no guard needed there. `sno_array_get` does **not**.

Array subscript assignment with `:S`/`:F` goto: the value may be null (failed sub-expression). Null-check before `sno_array_put`; null → skip put, take `:F`. Root cause: SD-10 NPE on `IDENT(t<key>)`.
