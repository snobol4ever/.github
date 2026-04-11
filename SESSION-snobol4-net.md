# SESSION-snobol4-net.md — SNOBOL4 × .NET

**Session:** one4all · SNOBOL4 · .NET — one unified milestone chain.
**Active work:** `scrip-interp.cs` in `one4all`. No `snobol4dotnet` clone needed. No dotnet test. Interpreter regression only.
**D-166 @N fix** (`snobol4dotnet`) is deferred — see `MILESTONE-NET-SNOBOL4.md` Phase C.

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** .NET MSIL
**Session prefix:** `D` / `N`
**Deep reference:** all ARCH docs cataloged in `PLAN.md`

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SNOBOL4 language | `PARSER-SNOBOL4.md` | language questions |
| snobol4dotnet repo | `REPO-snobol4dotnet.md` | build, @N bug status, crosscheck cmd |
| Milestone ladder | `MILESTONE-NET-SNOBOL4.md` | sprint planning, phase gap details |

---

## §BUILD

```bash
FRONTEND=snobol4 BACKEND=net TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make dotnet-sdk-8.0` — **does NOT build scrip-cc or run x86/nasm tools**.
This is a .NET session. Do not run `run_invariants.sh` or `run_emit_check.sh` (x86 emitter tests).

Build and smoke:
```bash
dotnet build src/driver/dotnet/scrip-interp.csproj -c Release -o /tmp/sni
dotnet /tmp/sni/scrip-interp.dll /home/claude/corpus/crosscheck/hello/hello.sno
# → HELLO WORLD
```

Broad baseline:
```bash
cat > /tmp/sni_run.sh << 'RUN'
#!/bin/bash
dotnet /tmp/sni/scrip-interp.dll "$1"
RUN
chmod +x /tmp/sni_run.sh
INTERP=/tmp/sni_run.sh CORPUS=/home/claude/corpus TIMEOUT=10 bash test/run_interp_broad.sh
```

---

## §TEST

```bash
# Unit tests
cd /home/claude/snobol4dotnet
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# Baseline: 1911/1913

# Corpus crosscheck
DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
DOTNET_ROOT=/usr/local/dotnet10 \
bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
# Baseline: 79/80 (strings/cross — @N bug)
```

---

## §KEY FILES

| File | Role |
|------|------|
| `ThreadedExecuteLoop.cs` | Statement executor — 5-phase spine (phases implicit) |
| `Scanner.cs` | Phase 3: `Match()` trampoline — drives pattern node graph |
| `AbstractSyntaxTreeNode.cs` | Pattern graph nodes — Subsequent/Alternate = γ/β ports |
| `CursorAssignmentPattern.cs` | Phase 3: `@var` cursor capture — writes IdentifierTable |
| `ConditionalVariableAssociationPattern.cs` | Phase 3: `.var` capture |
| `CheckGotoFailure.cs` | Phase 5: :S/:F branch — **@N overwrite suspect** |
| `Builder.cs` | `BuildEval()` / `BuildCode()` — self-hosted runtime compiler |
| `ThreadedCodeCompiler.cs` | Two-pass `Instruction[]` emitter; `AppendCompile` for CODE |
| `BuilderEmitMsil.cs` | `DynamicMethod` JIT — compiles token lists to IL delegates |
| `UnevaluatedPattern.cs` | `*pattern` operator — calls `DeferredCode` delegate at match time |
| `stmt_exec.c` | **Oracle** — explicit 5-phase C reference |

---

## §ORACLE READ ORDER (before Phase 2/3/5 work)

```bash
sed -n '1,50p' /home/claude/one4all/src/runtime/dyn/stmt_exec.c   # 5-phase spec
grep -n "pending_capture\|flush\|perform_repl" \
  /home/claude/one4all/src/runtime/dyn/stmt_exec.c                 # Phase 3/5 boundary
```

---

## §ARCHITECTURE (surveyed D-165)

### Pattern engine = Byrd boxes already

Jeff's `AbstractSyntaxTreeNode` / `Scanner` / `Pattern` hierarchy **is**
a dynamic Byrd box graph — just not named that way:

| Byrd concept | Jeff's equivalent |
|---|---|
| α port | `TerminalPattern.Scan()` |
| β / backtrack | `_state.RestoreAlternate()` |
| γ / success cont. | `node.GetSubsequent()` |
| ω / failure cont. | `MatchResult.Failure` → alternate pop |
| Graph build | `AbstractSyntaxTree.Build(pattern)` |
| Trampoline | `Scanner.Match()` `while(true)` loop |

### EVAL/CODE: self-hosted, no Roslyn

`BuildEval` / `BuildCode` route back through the **same compiler pipeline**:
`ReadCodeInString` → `Lex` → `Parse` → `ResolveSlots` →
`EmitMsilForAllStatements` → `CompileStarFunctions`.

`CODE` uses `AppendCompile` to live-patch the running `Instruction[]` thread.
`EVAL` immediately invokes `StarFunctionList[^1](this)`.

### *pattern via ExpressionVar / DeferredCode / StarFunctionList

When the parser sees a pattern with a variable/expression argument
(e.g. `ARBNO(*Command)`), it wraps it as a `DeferredCode` delegate into
`StarFunctionList`.  `UnevaluatedPattern.Scan` calls it at match time,
gets a `PatternVar`, recursively matches.  Runtime pattern composition
with zero external compilation.

### @N bug anatomy (Phase 3/5)

`CursorAssignmentPattern.Scan` writes `IdentifierTable["N"] = cursor`
during Phase 3 ✅.  Something in `Init` / `Finalize` / `CheckGotoFailure`
clobbers it during Phase 5.  Most likely: `Init` snapshots variable state;
`Finalize` or `CheckGotoFailure` restores on failure path — capture writes
fall inside that window.  Fix: guard so Phase 3 writes survive Phase 5.

---

## §MSIL BOX STRATEGY — D-176 pivot

### Why not static boxes.dll

D-175 assembled `boxes.dll` from IL via native .NET 10 ilasm. D-176 confirmed: Roslyn
refuses to compile C# that references an ilasm-built DLL. Root cause: Roslyn does not
unify `System.Runtime` declared in the DLL's manifest with its own implicit framework
reference — `CS0012: Object defined in unreferenced assembly` on every type from boxes.dll.
No csproj workaround resolves this reliably across SDK versions.

### Correct approach: Reflection.Emit in-memory

The `.il` source files are **templates**, not build inputs. At interpreter startup:

1. `BoxFactory.cs` — uses `AssemblyBuilder` + `ModuleBuilder` + `TypeBuilder` to define
   each box class in memory via `System.Reflection.Emit`
2. `ILGenerator` emits the Alpha/Beta method bodies — opcodes transcribed from the `.il`
   sources (or driven by a lightweight IL template parser)
3. `IByrdBox`, `MatchState`, `Spec`, `MatchResult` defined as **plain C# in scrip-interp**
   — no cross-assembly type identity issue
4. Box classes implement the C#-defined `IByrdBox` directly — Roslyn never sees them

**Result:** Zero DLL reference conflict. Types are in the same CLR context. The `.il` files
remain as the ground-truth spec/oracle for each box's Alpha/Beta logic.

### Key files for D-177

| File | Role |
|------|------|
| `src/driver/dotnet/BoxFactory.cs` | **NEW** — `AssemblyBuilder` scaffold, emits all 25 box types |
| `src/driver/dotnet/IByrdBox.cs` | **NEW** — `IByrdBox` + `MatchState` + `Spec` + `MatchResult` in C# |
| `src/runtime/boxes/shared/bb_box.il` | Oracle — Alpha/Beta opcode reference for each box |
| `src/driver/dotnet/PatternBuilder.cs` | Calls `BoxFactory` instead of `new bb_lit(...)` etc. |
| `src/driver/dotnet/Executor.cs` | Unchanged — calls `PatternBuilder` |

---

## §NOW

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **NET CORPUS** | D-208 | snobol4dotnet `c9dc3e1` · corpus `5c8aa22` · **2292p/0f/2s** | D-209: continue coverage hunting → ≥2300p |

**D-208 first actions:**
1. `cd /home/claude/snobol4dotnet && git pull --rebase`
2. `export PATH=/usr/local/dotnet10:$PATH`
3. `dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true 2>&1 | tail -4` — confirm **2281p/0f/2s**
4. Target thin areas: ObjectCreation(7 tests), Memory(16 tests) — find gaps and add cases

**Key facts:**
- 2 permanent skips: `TEST_Corpus_control_expr_eval` + `TEST_Corpus_099_keyword_rw`
- All 6 L*.cs use `string.CompareOrdinal()` (BUG-NET-STRCOMP fixed D-203)
- rung8 complete 810-818, rung9 complete 910-919
- Gimpel: UPLO(2), BASEB(2), ROMAN(4) — all expanded D-206
- Operator: Interrogation(6), Negation(6), ConditionalAssoc(6), Field(3) — expanded D-207
- dotnet 10 at /usr/local/dotnet10 (install via dotnet-install.sh if missing)

*SESSION-snobol4-net.md — updated D-208, 2026-04-10, Claude Sonnet 4.6.*
*D-208: Copy×3+Collect×2+Dump×2+Date×2+Time×2; +11 tests; 2292p/0f/2s.*
