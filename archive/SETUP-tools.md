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

## Frontend oracle requirements

Each frontend has a reference oracle used to generate `.ref` expected output for corpus tests.

| FRONTEND= | Oracle tool | Install method | Notes |
|-----------|------------|----------------|-------|
| `snobol4` | `spitbol` | prebuilt via snobol4ever/x64 | SPITBOL is the oracle for SNOBOL4 corpus |
| `snocone` | `spitbol` | prebuilt via snobol4ever/x64 | SPITBOL is the oracle for Snocone |
| `icon` | `icont` + `iconx` | apt or build from gtownsend/icon | Required for Icon corpus oracles |
| `prolog` | `swipl` | apt `swi-prolog` | Required for Prolog corpus oracles |
| `rebus` | *(none yet)* | — | Rebus oracle TBD |
| `scrip` | *(self-hosted)* | scrip-cc itself | Scrip demos use scrip-cc as oracle |

---
