# REPO-SCRIP.md — SCRIP

**What:** All frontends × all backends in one compiler/interpreter/runtime.

## Session Start
```bash
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build.log | head -5; exit 1; }
make libscrip_rt
```
Build later: `git pull --rebase; rm -f scrip; make scrip`.

## scrip modes (exactly two; must be 1:1)
| Flag | Mode |
|------|------|
| `scrip --run f` | mode 3 — native x86 BINARY in-process |
| `scrip --compile f` | mode 4 — x86 TEXT asm → gcc -no-pie + libscrip_rt.so |

## Key source paths
| Path | What |
|------|------|
| `src/driver/scrip.c` | mode selector |
| `src/parser/` | language front-ends |
| `src/contracts/IR.h`, `descr.h`, `ast.h` | spine types |
| `src/lower/lower.c` (+ per-language) | AST→IR |
| `src/emitter/emit.cpp` + `emit.h` | the ONE emit driver |
| `src/templates/*.cpp` + `x86_asm.h` | per-box templates + the only x86 encoders |
| `src/optimizer/` | LOWER→OPTIMIZER→EMITTER |
| `src/runtime/` | rt/, core/, builtins/ |

## Oracle
SPITBOL x64: `git clone https://github.com/snobol4ever/x64 /home/claude/x64`; `/home/claude/x64/bin/sbl -b file.sno`.

## Tools by backend
x86: nasm · JVM: default-jdk + jasmin.jar · .NET: mono-complete · WASM: wabt.

Grammar regen (`bison`/`flex`) is fine; the generated `.c` is the committed artifact — regen and confirm byte-identical BEFORE your grammar edit, then edit and regen again.
