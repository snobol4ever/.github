# REPO-SCRIP.md — SCRIP

**What:** All frontends × all backends in one compiler/interpreter/runtime.

## Session Start
```bash
cd /home/claude/SCRIP
git config --local user.name "LCherryholmes"          # ⛔ --local, NEVER --global (HOME law; a global
git config --local user.email "lcherryh@yahoo.com"    #    config leaks across repos and scrambles attribution)
bash /home/claude/SCRIP/scripts/install_system_packages.sh   # ⛔ NOT OPTIONAL — see TOOLING below
rm -f scrip && make -j4 scrip > /tmp/build.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build.log | head -5; exit 1; }
make libscrip_rt
```

## ⛔ TOOLING — RUN THE INSTALL SCRIPT, DO NOT HAND-INSTALL, DO NOT SKIP IT

`scripts/install_system_packages.sh` is the ONE AUTHORITY for what this project needs on the box. It is
idempotent and costs seconds when everything is already present. It ends by printing whether `gdb` is live.

**`gdb` is mandatory tooling, not a convenience:** RULES.md MONITOR-FIRST step (2) *is* "gdb breakpoint at
the bracketed C site with a spin/ignore counter". A session without it cannot run the prescribed hunt and
will hand off half-localized defects instead of fixing them.

⛔ **DO NOT hand-run `apt-get install gdb`.** Bare apt in a fresh container installs gdb's *Recommends*
(`libc-dbg`) against an apt index baked at image-build time; that indexed version has usually been
superseded and deleted from the mirror, so it 404s — on a package gdb does not need. **This exact trap
cost GOAL-RBP-EARN seven sessions (s33–s39):** each seat hit the 404, concluded gdb was unavailable in this
container, and recorded that as fact for the next seat to inherit. The script does `apt-get update` first
and passes `--no-install-recommends`. If gdb is somehow still missing, say so in your cursor rather than
working around it silently.

**Breakpointing runtime symbols:** `rt_*` symbols live in `out/libscrip_rt.so`, which is not loaded when
gdb starts, so a plain `break rt_defer_step` reports *"Function not defined"*. Use `set breakpoint pending
on` (or break after the `.so` loads). That is normal dynamic-linking behaviour — not evidence gdb is broken.
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
