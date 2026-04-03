# SESSION-snobol4-net.md — SNOBOL4 × .NET (snobol4dotnet)

**Repo:** snobol4dotnet · **Frontend:** SNOBOL4/SPITBOL · **Backend:** .NET MSIL
**Session prefix:** `D` / `N`
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SNOBOL4 language | `FRONTEND-SNOBOL4.md` | language questions |
| snobol4dotnet repo | `REPO-snobol4dotnet.md` | build, @N bug status, crosscheck cmd |
| Milestone ladder | `MILESTONE-NET-SNOBOL4.md` | sprint planning, phase gap details |

---

## §BUILD

```bash
FRONTEND=snobol4 BACKEND=net TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make mono-complete ilasm`
.NET 10 SDK at `/usr/local/dotnet10` — always:
```bash
export PATH=/usr/local/dotnet10:$PATH
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

## §NOW

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **TINY NET** | N-248 — 110/110 ✅ | `425921a` | M-T2-FULL ✅ complete |
| **DOTNET** | D-166 | `e1e4d9e` snobol4dotnet · one4all `90d5531` | **M-NET-P35-FIX** — wire boxes · fix @N Phase 3/5 → 80/80 |
| **NET INTERP** | D-168 | one4all `fb074c9` | **M-NET-INTERP-A01a** — `Snobol4Lexer.cs` token stream mirrors `lex.c` · 19/19 token tests |

**Two parallel tracks from D-166:**

### Track A — ThreadedExecuteLoop (snobol4dotnet @N fix)
1. `git pull --rebase` all repos.
2. `export PATH=/usr/local/dotnet10:$PATH` + `dotnet test` → confirm 1911/1913.
3. Crosscheck → confirm 79/80 baseline.
4. **Read oracle**: `sed -n '1,50p' src/runtime/dyn/stmt_exec.c` — Phase 5 section.
5. Add sentinel printouts before/after `CheckGotoFailure`, `Init`, `Finalize`
   in `ThreadedExecuteLoop.cs`; run `strings/cross`; find the clobber.
6. Fix. Crosscheck → 80/80. `dotnet test` → ≥1911/1913.
7. Commit, push, update SESSIONS_ARCHIVE + push .github.

### Track B — scrip-interp.cs (new interpreter, zero compile/link overhead)
See **MILESTONE-NET-INTERP.md** and **MILESTONE-NET-SNOBOL4.md** for full spec.

Pipeline: `.sno` → **Lexer** → tokens → **Parser** → `IrNode`/`IrStmt` tree → **5-phase interpreter**

1. **M-NET-INTERP-A01a** — Write `Snobol4Lexer.cs`; token stream mirrors `lex.c`; wire into parser; 19/19 token tests.
2. **M-NET-INTERP-A01b** — Replace `Ast.cs` with `IrNode.cs` (mirrors `ir.h` `EKind`/`EXPR_t`/`STMT_t`); update parser to emit `IrNode`/`IrStmt`; 19/19 parse tests.
3. **M-NET-INTERP-A01c** — Update `PatternBuilder.cs` + `Executor.cs` to dispatch on `IrKind`; remove `Ast.cs`; build clean; hello/empty_string/multi 3/3.
4. **M-NET-INTERP-A02** — Stack machine Phases 1/4/5: assignments, OUTPUT, gotos, labels, END, arithmetic via explicit value stack on `IrKind`; rung1 20/20.
5. **M-NET-INTERP-A03** — Byrd box sequencer Phases 2/3: `PatternBuilder` → `IByrdBox` graph; `ByrdBoxExecutor` trampoline; rung2–5 60/60.

**Track B is the recommended starting point for D-166** — it builds momentum
fast, has no dependency on snobol4dotnet, and the @N bug is avoided structurally
(captures commit only on Phase 5 :S, by design).

---

*SESSION-snobol4-net.md — rewritten D-165, 2026-04-02, Claude Sonnet 4.6.*
*Architecture survey: pattern engine = Byrd boxes. EVAL/CODE self-hosted. @N = Phase 3/5 gap.*
