---
name: ports
description: The two SNOBOL4 ports, snobol4dotnet (C#, seat hq_dotnet) and snobol4jvm (Clojure, seat hq_jvm): independent SNOBOL4 implementations in their own repos, graded by the fleet's runners against the same SPITBOL-cut refs as SCRIP under S4E_ENGINE=dotnet or jvm, their rows named <suite>@<port>. Their runners, builds and the calling shape every port shares. Not SCRIP's future JVM and .NET backends (skill scrip-backends).
---

# The ports: snobol4dotnet and snobol4jvm

## 1. What they are

- **Two separate SNOBOL4 implementations**, each in its own repo beside the seat's harness and corpus: `/home/claude_dotnet/snobol4dotnet` (C#, Jeffrey Cooper's, built with `dotnet build snobol4dotnet/Snobol4/Snobol4.csproj -c Release`) and `/home/claude_jvm/snobol4jvm` (Clojure, built with `lein uberjar` by `harness/scripts/build_snobol4jvm.sh`, which also records an AppCDS class archive).
- **They are not SCRIP**: not its backends (SCRIP's own JVM and .NET targets are new template sets, skill `scrip-backends`) and not its oracle. The oracle of all three engines is SPITBOL, `sbl -bf` (`lib_oracle_flags.sh`).
- **Seats and lanes** (MODE `LANES:`): `snobol4@dotnet=hq_dotnet`; `snobol4@jvm`, `snocone@jvm`, `rebus@jvm=hq_jvm`. Each port grades its own suites (CEO-1822/1912). Cursors: `GOAL-HQ-DOTNET.md`, `GOAL-HQ-JVM.md`. The two seats are off the ROSTER this evening (Lon 2026-11-01 09:01); their speed rows rest under Lon's hold (CEO-2049).

## 2. How a port is graded (the same runners, the same refs)

- `S4E_ENGINE` in {`scrip`, `dotnet`, `jvm`} names the graded engine. Under a port, `corpus_suite_harness.py`'s mode-3 arm calls the port's runner instead of `scrip --run`, and grades its output with the same reader, masks, `want_rc` and refs; a port has no mode 4 (`--compile` is refused rc 2). The engine's rows leave its own denominator only.
- **The runners share one calling shape:** `run_snobol4dotnet.sh` and `run_snobol4jvm.sh` take `[-dNk] [-sNk] [-u STR] name.sno [-- arg ...]`, run in the entry's own folder with stdin from its input sidecar, and answer `--binaries [--lang LANG]` (the graded files, driver first, or rc 2 for a missing, stale or unsupported build; the board's one check) and `--paths` (the same list, checking nothing, for the fingerprints).
- `run_port_as_scrip.sh` re-says SCRIP's m3 command line in that shape, so a SNOBOL4 package runner grades a port with its own grading untouched; any switch outside the closed vocabulary is refused by name.
- Switch facts: snobol4jvm maps `-sNk` to a thread stack (the declared size the hard cap) and has no heap cap (`-d` accepted, not mapped); snobol4dotnet takes the switches as SPITBOL does and runs SNOBOL4 source only.
- Speed is by instruction count against `sbl` (CEO-2035); the bench scripts are `bench_snobol4jvm.sh`, `bench_snobol4_jvm_demos.sh`, `bench_snobol4_jvm_table.sh`. The smokes are `test_smoke_snobol4_jvm*.sh`.
- The `Dotnet` package (`corpus/packages/snobol4/dotnet`, runner `test_snobol4_dotnet_suite.sh`) is snobol4dotnet's own test programs vendored as a SNOBOL4 suite that SCRIP is graded on too.

## 3. Rules a port landing keeps

- One identity on every commit (`LCherryholmes`, `lcherryh@yahoo.com`); the port repo pushes before `.github`.
- A port's red is cured in the port; a disagreement with SPITBOL is the port's defect unless the ref was cut wrong (CEO-1696: no oracle answer is an exclusion, never a debt).
