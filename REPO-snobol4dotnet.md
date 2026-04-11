# REPO-snobol4dotnet.md — snobol4dotnet

**What:** Jeffrey Cooper's complete SNOBOL4/SPITBOL runtime in C#.
**Repo:** `snobol4ever/snobol4dotnet`

---

## Session Start

```bash
# Git identity
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"

# Clone repos
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4dotnet.git /home/claude/snobol4dotnet
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus.git /home/claude/corpus
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/harness.git /home/claude/harness

# Install .NET
apt-get install -y dotnet-sdk-10.0
export PATH=/usr/local/dotnet10:$PATH

# Build
cd /home/claude/snobol4dotnet
dotnet build Snobol4/Snobol4.csproj -c Release -p:EnableWindowsTargeting=true 2>&1 | tail -3

# One-time: symlink demo/inc into beauty/ so drivers find include files
ln -sf /home/claude/corpus/programs/snobol4/demo/inc/* \
       /home/claude/corpus/programs/snobol4/beauty/ 2>/dev/null || true
```

**Always pass `-p:EnableWindowsTargeting=true`.** Required for cross-platform build.

---

## Test gates

**Unit tests:**
```bash
cd /home/claude/snobol4dotnet
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
# baseline: 2375p/0f/2s
```

**Beauty suite (19 drivers):**
```bash
export PATH=/usr/local/dotnet10:$PATH
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
# baseline: 7/19
```

Note: OUTPUT goes to stderr. Filter it. Strip exception stack lines.

**Corpus crosscheck:**
```bash
DOTNET_REPO=/home/claude/snobol4dotnet CORPUS=/home/claude/corpus/crosscheck \
DOTNET_ROOT=/usr/local/dotnet10 \
bash /home/claude/harness/adapters/dotnet/run_crosscheck_dotnet.sh
# baseline: 79/80
```

---

## Key files

| File | Role |
|------|------|
| `ThreadedExecuteLoop.cs` | 5-phase statement executor |
| `Scanner.cs` | Phase 3 `Match()` — drives pattern graph |
| `AbstractSyntaxTreeNode.cs` | Pattern nodes — Subsequent/Alternate = γ/β |
| `CursorAssignmentPattern.cs` | `@var` cursor capture |
| `CheckGotoFailure.cs` | Phase 5: :S/:F branch |
| `Builder.cs` | `BuildEval()` / `BuildCode()` |
| `ExecutionCache.cs` | Pattern graph cache (optimization target) |
| `BuilderEmitMsil.cs` | `DynamicMethod` JIT (optimization target) |

---

## State

- HEAD: `b280881`
- Unit tests: 2375p/0f/2s
- Beauty suite: 7/19
- Crosscheck: 79/80
