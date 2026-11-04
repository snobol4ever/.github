## Build, run, test (`bash harness/scripts/X` from the root, `bash ../harness/scripts/X` from SCRIP)
```bash
cd SCRIP && make -j8                                   # scrip + out/libscrip_rt.so; never above -j8
./scrip prog.{ext} < /dev/null                           # mode 3, in-process; -d<kb>k -s<kb>k before the file; program args after --
./scrip --compile --out=prog.s prog.{ext} && gcc prog.s -L$PWD/out -lscrip_rt -lm -Wl,-rpath,$PWD/out -o prog   # mode 4
./scrip --dump-ast|--dump-ir|--dump-bb|--dump-zeta|--dump-plan prog.{ext}
bash ../harness/scripts/util_run_slot.sh <cmd>...      # every hand run takes a run slot; an oracle runs through util_oracle.sh under timeout -k 5
python3 ../harness/scripts/corpus_suite_harness.py run ../corpus/tests/{lang}/ALL.{ext} ../corpus/tests/{lang}/ALL.ref --lang {lang} --modes m3,m4 --partition entry:<name>
bash ../harness/scripts/test_{lang}_ladder.sh --to N | --only N
```
A package program: its runner `test_{lang}_<pkg>_suite.sh` with `S4E_CHUNK=entry:<name>`. Never `pkill -f`; kill only pids you spawned. Large outputs in `/tmp/s4e/<seat>/`, never under the root; a scratch worktree outside the root.
`perf` is the launcher `~/.local/bin/perf`: the `/usr/bin/perf` shim prints `WARNING: perf not found for kernel 6.17.0-1032` because the OEM package ships no perf, yet the counter works. Never `apt install`, never drop an instruction count for it; `perf --version` reads 6.8.12, else `type -a perf` (GOAL-SNOBOL4-100.md BOX FACT).
