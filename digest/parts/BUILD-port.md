## Build, run, test (`bash harness/scripts/X` from the root)
```bash
S4E_ENGINE={engine} python3 harness/scripts/corpus_suite_harness.py run corpus/tests/snobol4/ALL.sno corpus/tests/snobol4/ALL.ref --lang snobol4 --modes m3 --partition entry:<name>   # one entry, the shared ref
bash harness/scripts/run_snobol4{engine}.sh [-dNk] [-sNk] [-u STR] name.sno [-- arg ...]      # the runner, in the entry's own folder, stdin from its sidecar
S4E_ENGINE={engine} bash harness/scripts/test_snobol4_<pkg>_suite.sh                        # a package through run_port_as_scrip.sh, grading untouched
bash harness/scripts/util_instr_count.sh <cmd>...                                           # speed is an instruction count against sbl
```
`/home/resources/x64/bin/sbl -bf` is the oracle; `/home/resources/manuals/snobol4/` the manual. Never `pkill -f`; kill only pids you spawned. Large outputs in `/tmp/s4e/<seat>/`, never under the root.
