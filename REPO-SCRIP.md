# REPO-SCRIP.md — SCRIP

**What:** All frontends × all backends in one compiler/interpreter/runtime.

## Session Start (Pascal goal)
```bash
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build.log | head -5; exit 1; }
make libscrip_rt
```

## Build
```bash
cd /home/claude/SCRIP && git pull --rebase
make scrip   # always rm -f scrip first
```

## scrip modes
| Flag | Mode |
|------|------|
| `scrip --interp f` | mode 2 — IR-graph interpreter |
| `scrip --run f` | mode 3 — native x86 in-process |
| `scrip --compile f` | mode 4 — standalone asm → gcc -no-pie + libscrip_rt.so |

## Key source paths
| Path | What |
|------|------|
| `src/driver/scrip.c` | mode selector |
| `src/parser/` | 6 language front-ends |
| `src/contracts/IR.h`, `descr.h`, `ast.h` | spine types |
| `src/lower/lower.c` | AST→IR graph |
| `src/interp/IR_interp.c` | mode-2 interpreter |
| `src/emitter/emit_core.c` | IR→template dispatch |
| `src/emitter/emit_bb.c` | BB driver: slot resolution, flat chains |
| `src/emitter/{BB,XA}_templates/` | per-box x86 templates |
| `src/runtime/` | rt/, core/, builtins/ |

## Oracle
**SPITBOL x64:** `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`
Invoke: `/home/claude/x64/bin/sbl -b file.sno`

## Tools by backend
| Backend | Tools |
|---------|-------|
| x86 | `nasm`, `libgc-dev` |
| JVM | `default-jdk`, `jasmin.jar` |
| .NET | `mono-complete` |
| WASM | `wabt` |

Never install bison or flex — generated parser files are committed.
