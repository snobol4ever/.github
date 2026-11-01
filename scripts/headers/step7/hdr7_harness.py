#!/usr/bin/env python3
# hdr7_harness.py <harness/scripts> -- the harness side of headers step 7: (a) the fan-in instrument's unused arm leaves a data .inc alone (a .inc is
# spliced text -- an initializer, a table, a setting's source -- renamed .inc at step 6A to say so; its definitions are not declarations a unit
# names); (b) the ceiling gate is BLOCKING: its RULING row leaves gate_wiring.tsv (the Makefile's test target names it in the SCRIP landing beside).
import sys, re
H = sys.argv[1].rstrip('/') + '/'
p = H + 'util_header_fanin.py'; t = open(p).read()
old = """            for nm in self.unit_includes[u]:
                for h in self.resolve(nm, self.unit_deps[u], u):
                    if not self.names(u, h) and not (os.path.splitext(h)[0] == os.path.splitext(u)[0]):"""
assert t.count(old) == 1
t = t.replace(old, """            for nm in self.unit_includes[u]:
                if nm.endswith('.inc'):
                    continue   # a data .inc is spliced text (step 6A renamed them to say so), not an interface a unit names (step 7)
                for h in self.resolve(nm, self.unit_deps[u], u):
                    if not self.names(u, h) and not (os.path.splitext(h)[0] == os.path.splitext(u)[0]):""")
old2 = "#   util_header_fanin.py --unused          per unit the direct includes none of whose declarations the unit names, then \"summary unused=N\"\n"
assert t.count(old2) == 1
t = t.replace(old2, old2 + "#                                          (a data .inc -- an initializer, a table, a setting's source, renamed .inc at step 6A -- is spliced text, never counted)\n")
open(p, 'w').write(t); print('  util_header_fanin.py: the unused arm skips a .inc')
# (b) AS BUILT: gate_wiring.tsv is written by util_gate_wiring.py alone; removing the row by hand (the first draft here) left the gate in no bucket and the
#     step-7 DONE-WHEN red ("still RULING or TASK": it wants a WIRED row). The landing ran, from the harness worktree beside the SCRIP tree whose Makefile names the gate:
#         python3 util_gate_wiring.py --root <SCRIP> adopt
#     which promoted the ceiling gate RULING -> WIRED and recorded two rows the measurement owed already (bootstrap_parse_stage_ir_identity wired but filed RULING;
#     batch_scripts_run_in_the_batch_slice wired tonight and never adopted). The three gates that read what the split moved (pl_trail_mechanism's C harness,
#     the two collector gates' awk of PL_TR_HEADER_BYTES and DT_PCELL) were corrected by hand; the harness commit's patch is beside this file.
print('  gate_wiring.tsv: run util_gate_wiring.py --root <SCRIP> adopt (see the note above)')
p = H + 'test_gate_no_header_reaches_more_units_than_its_users.sh'; t = open(p).read()
old3 = "# DECLARED RULING (reporting) at step 1a, BLOCKING at step 7 when every arm reads 0 (the page)."
assert t.count(old3) == 1
t = t.replace(old3, "# DECLARED RULING (reporting) at step 1a; BLOCKING since step 7 (2026-10-31, the cto: every arm read 0 and the baseline was lowered to that tree).")
open(p, 'w').write(t); print('  the gate header says BLOCKING')
