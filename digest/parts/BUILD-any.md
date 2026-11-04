## Build, run, test (`bash harness/scripts/X` from the root, `bash ../harness/scripts/X` from SCRIP)
```bash
cd SCRIP && make -j8                                   # scrip + out/libscrip_rt.so; never above -j8
./scrip prog.<ext> < /dev/null                           # mode 3, in-process; -d<kb>k -s<kb>k before the file; program args after --
./scrip --compile --out=prog.s prog.<ext> && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog   # mode 4
./scrip --dump-ast|--dump-ir|--dump-bb|--dump-zeta|--dump-plan prog.<ext>
bash ../harness/scripts/util_run_slot.sh <cmd>...      # every hand run takes a run slot; an oracle runs through util_oracle.sh under timeout -k 5
python3 ../harness/scripts/corpus_suite_harness.py run ../corpus/tests/<lang>/ALL.<ext> ../corpus/tests/<lang>/ALL.ref --lang <lang> --modes m3,m4 --partition entry:<name>
bash ../harness/scripts/test_<lang>_ladder.sh --to N | --only N
```
Extensions: `.sno` `.spt` `.sbl` SNOBOL4, `.sc` Snocone, `.reb` Rebus, `.icn` Icon and Unicon, `.pl` Prolog, `.pas` Pascal, `.raku` Raku, `.md` polyglot. Oracles (`ls` one before trusting an all-FAIL table), through `lib_oracle_flags.sh`'s accessors: `sbl -bf` (`/home/resources/x64/bin`), `icont`, `unicon_bin()`, swipl 9.0.4, GNU Prolog 1.6.0, XSB 5.0.0, `fpc -Miso`, rakudo 2026.05 (`rakudo_bin()`; the `raku` on PATH is 2022). Manuals: `/home/resources/manuals/<lang>/`. A package program: its runner `test_<lang>_<pkg>_suite.sh` with `S4E_CHUNK=entry:<name>`. Never `pkill -f`; kill only pids you spawned. Large outputs in `/tmp/s4e/<seat>/`, never under the root.
