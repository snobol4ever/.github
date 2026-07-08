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
SCRIP has EXACTLY TWO modes (modes 1 and 2 are DELETED — see GOAL-MODE34-IDENTICAL.md). They must be 1:1 corresponding.
| Flag | Mode |
|------|------|
| `scrip --run f` | mode 3 — native x86 BINARY in-process |
| `scrip --compile f` | mode 4 — standalone x86 TEXT asm → gcc -no-pie + libscrip_rt.so |

## Key source paths
| Path | What |
|------|------|
| `src/driver/scrip.c` | mode selector |
| `src/parser/` | 6 language front-ends |
| `src/contracts/IR.h`, `descr.h`, `ast.h` | spine types |
| `src/lower/lower.c` | AST→IR graph |
| `src/emitter/emit.cpp` + `emit.h` | the ONE emit driver (dispatch + chain-BFS + drive) |
| `src/templates/*.cpp` + `x86_asm.h` | per-box templates (flat, no subdirs) + the only x86 encoders |
| `src/optimizer/` | LOWER→OPTIMIZER→EMITTER, `SCRIP_OPT`-gated OFF |
| `src/runtime/` | rt/, core/, builtins/ |

## Oracle
**SPITBOL x64:** `git clone https://github.com/snobol4ever/x64 /home/claude/x64` (public, no token — verified 2026-07-01)
Invoke: `/home/claude/x64/bin/sbl -b file.sno`

## Tools by backend
| Backend | Tools |
|---------|-------|
| x86 | `nasm`, `libgc-dev` |
| JVM | `default-jdk`, `jasmin.jar` |
| .NET | `mono-complete` |
| WASM | `wabt` |

Never RUN bison/flex against the committed `.y`/`.l` grammar sources (alongside every frontend's generated
`.tab.c`/`.lex.c`/`_parse.c`, e.g. `src/parser/snobol4/snobol4.y` next to `snobol4.tab.c`) — the generated `.c`
is the committed, tested artifact with no Makefile rule regenerating it, so running the generator by hand
silently overwrites known-good output with unverified output. Installing the tools is harmless; running them
against these grammars is the hazard (verified 2026-07-01: files are git-tracked, Makefile has zero invocation).
