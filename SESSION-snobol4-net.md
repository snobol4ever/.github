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
| **NET CORPUS** | D-214b | snobol4dotnet `b280881` · corpus `5c8aa22` · **2375p/0f/2s** | D-215: continue coverage hunting → ≥2390p |

**D-215 first actions:**
1. `cd /home/claude/snobol4dotnet && git pull --rebase`
2. `export PATH=/usr/local/dotnet10:$PATH`
3. `dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true 2>&1 | tail -4` — confirm **2364p/0f/2s**
4. Target thin areas — run the thin-file finder then expand:
```python
python3 -c "
import os
for subdir in ['Function/Pattern','Function/InputOutput','Function/ArraysTables','Function/Numeric','Function/StringComparison','Function/Miscellaneous','Function/FunctionControl','Function/StringSynthesis','Corpus','Gimpel']:
    base=f'TestSnobol4/{subdir}'
    if not os.path.exists(base): continue
    for f in sorted(os.listdir(base)):
        p=base+'/'+f
        if not p.endswith('.cs'): continue
        with open(p,'rb') as fh: c=fh.read().decode('utf-8-sig','replace')
        n=c.count('[TestMethod]')
        if n < 8: print(n, subdir+'/'+f)
"
```

**Key facts:**
- 2 permanent skips: `TEST_Corpus_control_expr_eval` + `TEST_Corpus_099_keyword_rw`
- All 6 L*.cs use `string.CompareOrdinal()` (BUG-NET-STRCOMP fixed D-203)
- rung8 complete 810-818, rung9 complete 910-919
- Gimpel: UPLO(5), BASEB(4), ROMAN(5) — still thin
- Operator: Interrogation(6), Negation(6), ConditionalAssoc(6), Field(3) — still thin
- dotnet 10 at /usr/local/dotnet10 (install via dotnet-install.sh if missing)
- APPLY with user-defined functions via APPLY() fails error 22 — known gap, use built-ins only
- DIFFER(A,B) FAILS when A==B, SUCCEEDS when A!=B — double-check before writing tests
- TRIM removes trailing tabs as well as spaces (confirmed D-214)
- CODE(CHAR(n)) does NOT roundtrip to n in snobol4dotnet (confirmed D-214)
- D-214 expanded: Reverse(+3→9), Trim(+3→9), Size(+3→8), Char(+1→8), LEq/LGe/LLe/LNe(+1→8 each), Rung11(+1→8), Rung2(+2→8)
- Remaining thin (< 8): Abort(6), Arb(6), ArbNo(6), Concatenate(6), Fail(6), Fence(6), Rem(6), InputOutput files, Prototype(4), Rsort(5), Date(3), Eval(0/placeholder), Time(5), Arg(5), FunctionControl files, Gimpel files, Operator files

*SESSION-snobol4-net.md — updated D-214, 2026-04-11, Claude Sonnet 4.6.*
*D-214: Reverse+3, Trim+3, Size+3, Char+1, LEq/LGe/LLe/LNe+1 each, Rung11+1, Rung2+2; +17 tests; 2364p/0f/2s.*
