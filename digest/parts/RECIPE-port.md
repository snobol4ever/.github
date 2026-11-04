## THE LANDING RECIPE
1. Reproduce: run the entry through the port's runner in its own folder (`run_snobol4<engine>.sh [-dNk] [-sNk] name.sno`, stdin from its sidecar) beside `sbl -bf` on the same input; the first differing line is the defect.
2. The criterion first: a row the coo assigned carries its `DONE-WHEN:`; a row you open is `mint <topic> --owner <seat> --stdin` with `DONE-WHEN:` and `PREMISE-WHEN:` lines, each starting `cd "${S4E_HOME:?REFUSE(2): S4E_HOME unset}" &&`.
3. Cure in the port repo on a clean tree; the SPITBOL semantics are the manual's (`/home/resources/manuals/snobol4/`), never SCRIP's reading of them.
4. Prove: DONE-WHEN green; the entry under `S4E_ENGINE=<engine>` through `corpus_suite_harness.py run ... --modes m3 --partition entry:<name>`; `test_smoke_snobol4_<engine>.sh`.
5. Land: `git add` NAMED FILES; `git commit -F -` with a quoted heredoc, as `LCherryholmes <lcherryh@yahoo.com>`, no trailers; `git pull --rebase`, re-prove, push.
6. Record: the baton's LEDGER and NEXT; `s4e_test_request.sh --engine <engine> <suite-key> <entry>...` to the coo; close by `claim` + `done` once the coo's reading is green.
