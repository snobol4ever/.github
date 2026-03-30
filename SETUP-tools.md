# SETUP-tools.md — Tool requirements by frontend × backend

Used by SESSION_SETUP.sh when FRONTEND= and BACKEND= are specified.
If either is omitted, all tools are installed (safe but slow — avoid for focused sessions).

Pass both to SESSION_SETUP.sh to install only what you need:
```bash
TOKEN=ghp_xxx FRONTEND=snocone BACKEND=x64 bash /home/claude/.github/SESSION_SETUP.sh
```

---

## Always required (every session)

| Tool | Package | Purpose |
|------|---------|---------|
| `gcc` | `gcc` | Compile scrip-cc itself |
| `make` | `make` | Build system |
| `curl` | `curl` | Source downloads |
| `unzip` | `unzip` | Archive extraction |

## Rebus frontend only

| Tool | Package | Purpose |
|------|---------|---------|
| ~~`bison`~~ | — | **Never installed.** `rebus.tab.c/h` are committed. Regenerate on your own machine if you modify `rebus.y`. |
| ~~`flex`~~ | — | **Never installed.** `lex.rebus.c` is committed. Regenerate on your own machine if you modify `rebus.l`. |

**bison and flex are NEVER installed in any session — including Rebus sessions.** Generated files (`rebus.tab.c`, `rebus.tab.h`, `lex.rebus.c`) are committed and always current. If `rebus.y` or `rebus.l` change, regenerate on your own machine and commit the C files.

---

## Backend requirements

| BACKEND= | Tools required | Notes |
|----------|---------------|-------|
| `x64` | `nasm`, `libgc-dev` | NASM assembler + Boehm GC for linking |
| `jvm` | `java` (JRE), `javac` (JDK), `jasmin.jar` | JVM bytecode assembly; jasmin.jar bundled in repo |
| `net` | `mono`, `ilasm` | .NET IL assembly + runtime |
| `wasm` | `wabt` (wat2wasm), `node` | `apt-get install -y wabt`; node pre-installed on Ubuntu 24 |
| `c` | *(none beyond gcc)* | C backend — gcc already required |

---

## Frontend oracle requirements

Each frontend has a reference oracle used to generate `.ref` expected output for corpus tests.

| FRONTEND= | Oracle tool | Install method | Notes |
|-----------|------------|----------------|-------|
| `snobol4` | `snobol4` (CSNOBOL4) | build from source (snobol4.org) | Required for SNOBOL4 corpus oracles |
| `snocone` | `snobol4` (CSNOBOL4) | build from source | Snocone oracles run via CSNOBOL4+snocone.sc; also JVM Snocone |
| `icon` | `icont` + `iconx` | apt or build from gtownsend/icon | Required for Icon corpus oracles |
| `prolog` | `swipl` | apt `swi-prolog` | Required for Prolog corpus oracles |
| `rebus` | *(none yet)* | — | Rebus oracle TBD |
| `scrip` | *(self-hosted)* | scrip-cc itself | Scrip demos use scrip-cc as oracle |

---

## Combination matrix — what SESSION_SETUP.sh installs

| FRONTEND | BACKEND | Always | + Backend | + Oracle | Skip |
|----------|---------|--------|-----------|---------|------|
| `snocone` | `x64` | gcc make curl unzip | nasm libgc-dev | snobol4 (CSNOBOL4) | java javac mono ilasm icont swipl spitbol |
| `snobol4` | `x64` | " | nasm libgc-dev | snobol4 (CSNOBOL4) | java javac mono ilasm icont swipl spitbol |
| `icon` | `x64` | " | nasm libgc-dev | icont iconx | java javac mono ilasm snobol4 swipl spitbol |
| `prolog` | `x64` | " | nasm libgc-dev | swipl | java javac mono ilasm snobol4 icont spitbol |
| `snobol4` | `jvm` | " | java javac jasmin.jar | snobol4 (CSNOBOL4) | nasm libgc-dev mono ilasm icont swipl spitbol |
| `icon` | `jvm` | " | java javac jasmin.jar | icont iconx | nasm libgc-dev mono ilasm snobol4 swipl spitbol |
| `prolog` | `jvm` | " | java javac jasmin.jar | swipl | nasm libgc-dev mono ilasm snobol4 icont spitbol |
| `snobol4` | `net` | " | mono ilasm | snobol4 (CSNOBOL4) | nasm libgc-dev java javac icont swipl spitbol |
| `snobol4` | `wasm` | " | wabt(wat2wasm) node | snobol4 (CSNOBOL4) | nasm libgc-dev java javac mono ilasm icont swipl spitbol |
| *(omitted)* | *(omitted)* | " | ALL backends | ALL oracles | nothing — full install |

**SPITBOL** is never required for any current session — it is an alternative SNOBOL4 oracle
but CSNOBOL4 is always preferred. SESSION_SETUP.sh attempts it as a best-effort install
only when FRONTEND is omitted (full install mode).

---

## Quick reference — Snocone × x86 (most common SC session)

```bash
TOKEN=ghp_xxx FRONTEND=snocone BACKEND=x64 bash /home/claude/.github/SESSION_SETUP.sh
```

Installs: `gcc make curl unzip nasm libgc-dev snobol4(CSNOBOL4)`
Skips:    `java javac mono ilasm icont swipl spitbol` — saves ~5–10 min

---

*SETUP-tools.md — reference only. SESSION_SETUP.sh is the authoritative implementation.*
