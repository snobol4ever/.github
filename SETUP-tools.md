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
| `bison` | `bison` | Rebus parser generator |
| `flex` | `flex` | Rebus lexer generator |

**bison and flex are NOT required for any non-Rebus session.** Gated on `need_frontend rebus` in SESSION_SETUP.sh. Do not install manually for Snocone/SNOBOL4/Icon/Prolog sessions.

---

## Backend requirements

| BACKEND= | Tools required | Notes |
|----------|---------------|-------|
| `x64` | `nasm`, `libgc-dev` | NASM assembler + Boehm GC for linking |
| `jvm` | `java` (JRE), `javac` (JDK), `jasmin.jar` | JVM bytecode assembly; jasmin.jar bundled in repo |
| `net` | `mono`, `ilasm` | .NET IL assembly + runtime |
| `wasm` | *(none beyond gcc)* | WASM stub — no extra tools yet |
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
| `snocone` | `x64` | gcc make curl unzip | nasm libgc-dev | snobol4 (CSNOBOL4) | bison flex java javac mono ilasm icont swipl spitbol |
| `snobol4` | `x64` | " | nasm libgc-dev | snobol4 (CSNOBOL4) | bison flex java javac mono ilasm icont swipl spitbol |
| `icon` | `x64` | " | nasm libgc-dev | icont iconx | bison flex java javac mono ilasm snobol4 swipl spitbol |
| `prolog` | `x64` | " | nasm libgc-dev | swipl | bison flex java javac mono ilasm snobol4 icont spitbol |
| `snobol4` | `jvm` | " | java javac jasmin.jar | snobol4 (CSNOBOL4) | bison flex nasm libgc-dev mono ilasm icont swipl spitbol |
| `icon` | `jvm` | " | java javac jasmin.jar | icont iconx | bison flex nasm libgc-dev mono ilasm snobol4 swipl spitbol |
| `prolog` | `jvm` | " | java javac jasmin.jar | swipl | bison flex nasm libgc-dev mono ilasm snobol4 icont spitbol |
| `snobol4` | `net` | " | mono ilasm | snobol4 (CSNOBOL4) | bison flex nasm libgc-dev java javac icont swipl spitbol |
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
Skips:    `bison flex java javac mono ilasm icont swipl spitbol` — saves ~5–10 min

---

*SETUP-tools.md — reference only. SESSION_SETUP.sh is the authoritative implementation.*
