# REPO-snobol4dotnet.md — snobol4dotnet

**What:** Jeffrey Cooper's complete SNOBOL4/SPITBOL runtime in C#. Compiler pipeline,
threaded execution, MSIL delegate JIT, pattern engine, plugin system.
**Clone:** `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4dotnet.git /home/claude/snobol4dotnet`
**Path:** `/home/claude/snobol4dotnet`

---

## Build

```bash
cd /home/claude/snobol4dotnet && git pull --rebase
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y dotnet-sdk-10.0
export PATH=/usr/local/dotnet10:$PATH
dotnet build Snobol4/Snobol4.csproj -c Release -p:EnableWindowsTargeting=true 2>&1 | tail -3
```

**Always pass `-p:EnableWindowsTargeting=true`.** Required for cross-platform build.

---

## Test gates

**Unit tests:**
```bash
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# baseline: 2375 passed, 0 failed, 2 skipped
```

**Beauty suite (19 drivers):**
```bash
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd /home/claude/corpus/programs/snobol4/beauty
PASS=0; FAIL=0
for driver in beauty_*_driver.sno; do
    name="${driver%_driver.sno}"
    dotnet $SNO4 -b "$driver" > /dev/null 2>/tmp/err.txt || true
    grep -v "^Unhandled\|^ at \|^Aborted" /tmp/err.txt > /tmp/actual.txt
    diff -q /tmp/actual.txt "${driver%.sno}.ref" > /dev/null 2>&1 \
        && { echo "PASS $name"; PASS=$((PASS+1)); } \
        || { echo "FAIL $name"; FAIL=$((FAIL+1)); }
done; echo "$PASS/19"
# current baseline: 7/19
```

**Note:** OUTPUT goes to stderr in snobol4dotnet. Filter stderr, strip exception stack lines.
Include files must be findable from driver's CWD. Symlink `demo/inc/*` into beauty/ once per machine.

**Corpus crosscheck:**
```bash
DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
DOTNET_ROOT=/usr/local/dotnet10 \
bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
```

---

## Key files

| File | Role |
|------|------|
| `ThreadedExecuteLoop.cs` | Statement executor — 5-phase spine |
| `Scanner.cs` | Phase 3: `Match()` trampoline — drives pattern node graph |
| `AbstractSyntaxTreeNode.cs` | Pattern graph nodes — Subsequent/Alternate = γ/β ports |
| `CursorAssignmentPattern.cs` | `@var` cursor capture |
| `ConditionalVariableAssociationPattern.cs` | `.var` capture |
| `CheckGotoFailure.cs` | Phase 5: :S/:F branch |
| `Builder.cs` | `BuildEval()` / `BuildCode()` — runtime compiler |
| `ThreadedCodeCompiler.cs` | Two-pass `Instruction[]` emitter |
| `BuilderEmitMsil.cs` | `DynamicMethod` JIT |

---

## SPITBOL oracle rule

SPITBOL is the authoritative semantic reference.
Key semantics:
- DATATYPE builtins: lowercase (`"name"`, `"pattern"`)
- User DATA types: `ToLowerInvariant`
- `&UCASE`/`&LCASE`: exactly 26 ASCII letters
- `@N`: 0-based cursor position

---

## State

- HEAD: `b280881`
- Unit tests: 2375p/0f/2s
- Beauty suite: 7/19
- Active goal: GOAL-SCRIP-BEAUTY.md (steps S-15 through S-25)
