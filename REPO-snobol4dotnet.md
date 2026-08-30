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

# ⛔ STALE, NOT VERIFIED (seat16, citation sweep, 2026-08-29): both paths below are gone. Includes
# now live at $S4E_HOME/corpus/include/ (confirmed present, 16 modules); beauty_suite/ as a loose-file
# directory is confirmed gone (consumed into the master-suite consolidation). This symlink step likely
# doesn't apply to whatever the current extraction recipe is — re-derive before running.
# One-time (ORIGINAL, now unusable as literally written): symlink demo/inc into beauty/ so drivers find include files
ln -sf /home/claude/corpus/programs/snobol4/demo/inc/* \
       /home/claude/corpus/programs/snobol4/beauty_suite/ 2>/dev/null || true
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

**Beauty suite (19 drivers):** ⛔ **STALE, NOT VERIFIED (seat16, citation sweep, 2026-08-29) — see the
same flag in `GOAL-NET-BEAUTY-19.md`: this directory of loose drivers is confirmed gone, consumed into
the master-suite consolidation. Re-derive against the current master format before running.**
```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
cd $S4E_HOME/corpus/programs/snobol4/beauty_suite  # path fossil, will not resolve
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

- HEAD: `18a2946` (S-2-bridge-1..3: MonitorIpc.cs C# IPC bridge + VALUE fire-point at Executive.Assign chokepoint covers all 5 LHS forms — plain scalar, .-capture, \$-capture, array element, table slot — via single hook because PatternMatch BetaStack walk routes through Assign())
- Unit tests: not re-run this session (build clean, beauty gate verifies no regression)
- Beauty suite: 17/17 PASS (verified before-and-after bridge fire-point)
- Crosscheck: not re-baselined this session
- New smoke gates (all green at this HEAD):
  - `scripts/test_smoke_dot_bridge.sh`         PASS=5 (dormancy)
  - `scripts/test_smoke_dot_bridge_value.sh`   PASS=5 (live FIFO hello)
  - `scripts/test_smoke_dot_bridge_complex.sh` PASS=9 (5 LHS forms)

## SPITBOL oracle semantics

SPITBOL MINIMAL is the authoritative oracle.

- `DATATYPE()` builtins → lowercase; user DATA types → `ToLowerInvariant`
- `&UCASE` / `&LCASE` = exactly 26 ASCII letters
- `@N` cursor position is **0-based**
