#!/usr/bin/env python3
"""CEO-1387 (ceo, 2026-10-01 11:0x CDT): the rows the zero-base sweep could not rule by class, ruled by name.
The sweep (CEO-1386) never touches a PARKED-UMBRELLA, BLOCKED, PARKED-SUPERSEDED-BY or PARKED-DUPLICATE-OF row by
script; after it wrote, the census still named twelve rows whose DONE-WHEN runs a board nobody but the coo may run
(CEO-1342 clause 5) and four FREE rank-1 rows in HQ lanes that are neither a SUITE TABLE red nor a blocking gate.
Eleven of the twelve are retired here with a reason each (the twelfth is a live cto assignment, told by telegram);
the four are re-ranked to 2 (RANK IS THE BOARD'S, CEO-1386). Backups beside the files, log under postoffice/salvage/.
    python3 .github/scripts/queue_rule_board_umbrellas_and_reranks_ceo_1387.py [--apply]
"""
import os, shutil, sys, time
PO = "/home/resources/postoffice"; Q, QR = PO + "/QUEUE.tsv", PO + "/QUEUE.retired.tsv"
apply = "--apply" in sys.argv; stamp = time.strftime("%Y%m%d-%H%M%S")
OLD = "a defect of the pre-rebuild Prolog machine (Lon 2026-09-02: rebuilt from rung 0); ProM reads 563/563 and INRIA 442/442 on the SUITE TABLE, the ladder umbrella it parked on is history, and a surviving defect re-enters only as a measured red under prolog-every-suite-to-100"
RETIRE = {
 "icon-ipl-851-run-graded-against-iconx-refs-and-cured-by-class": "superseded by icon-every-suite-to-100-under-nonet-ceo-1266 (IPL is one of its SUITE TABLE rows) and its DONE-WHEN runs the IPL board",
 "prolog-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs": "its DONE-WHEN runs a board; re-mint with a census criterion (every non-package .pl source with a ref present among the master's origins) when hq_prolog takes it up",
 "prolog-inria-445-to-100-percent-by-iso-section": "INRIA reads 442/442 on the SUITE TABLE; the problem the row named no longer exists",
 "prolog-multiclause-uninit-lexprep-frame": OLD,
 "prolog-rung-red-class-dynamic-db-assert-retract-abolish-clause-is-ladder-rung-10": OLD,
 "prolog-rung-red-class-findall-bagof-between-is-ladder-rung-8": OLD,
 "prolog-rung-red-class-rung66-streams-and-existence-error-is-ladder-rung-9": OLD,
 "prolog-rung-red-class-write-canonical-is-ladder-rung-6": OLD,
 "prolog-term-to-descr-eradication": OLD,
 "snobol4-aisnobol-and-dotnet-suites-to-100-percent": "PARKED-SUPERSEDED-BY its named successor; a superseded row is retired, not parked",
 "snobol4-aisnobol-wang-computed-goto-success-branch-segv": "PARKED-DUPLICATE-OF its named twin; a duplicate is retired, not parked",
}
RERANK2 = {
 "raku-monitor-the-instrumented-rakudo-oracle-is-completed-and-used-to-find-and-fix-scrip-bugs",
 "icon-speed-geddump-reads-0-03x-iconx-because-75-percent-of-its-cycles-are-the-collector-over-a-379-kb-gedcom-structure-under-its-16-mb-arena",
 "icon-speed-reverse-complement-reads-0-53x-iconx-in-mode-4-and-0-39x-in-mode-3-profile-it-and-cure-its-first-class",
 "prolog-every-assertz-recompiles-the-whole-predicate-so-n-facts-compile-n-squared-clauses-1000-facts-take-134-s-and-a-gb",
}
lines = open(Q, encoding="utf-8").read().split("\n"); out, ret, log = [], [], []
for ln in lines:
    f = ln.split("\t")
    if len(f) < 4 or ln.startswith("#"): out.append(ln); continue
    rank, topic, owner, state = f[0], f[1], f[2], f[3]
    if topic in RETIRE:
        if state.startswith(("CLAIMED", "ASSIGNED")): out.append(ln); log.append((topic, owner, state, "UNTOUCHED-live-claim", rank)); continue
        f[3] = "RETIRED:ceo-1387-" + RETIRE[topic]; ret.append("\t".join(f)); log.append((topic, owner, state, "RETIRED", rank)); continue
    if topic in RERANK2 and state == "FREE" and rank in ("0", "1"):
        f[0] = "2"; out.append("\t".join(f)); log.append((topic, owner, state, "RERANK-" + rank + "-to-2", "2")); continue
    out.append(ln)
for topic, owner, state, what, rank in log: print("%-14s rank %s %-9s %s" % (what, rank, owner, topic[:100]))
missing = (set(RETIRE) | RERANK2) - {l[0] for l in log}
for m in missing: print("NOT FOUND or not in a ruled state (left alone):", m[:100])
print("retire %d, rerank %d" % (sum(1 for l in log if l[3] == "RETIRED"), sum(1 for l in log if l[3].startswith("RERANK"))))
if not apply: print("DRY RUN: nothing written"); sys.exit(0)
for p in (Q, QR):
    if os.path.exists(p): shutil.copyfile(p, p + ".bak.%s-ceo-1387" % stamp)
open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(out))
cur = open(QR, encoding="utf-8").read().split("\n") if os.path.exists(QR) else []
open(QR, "w", encoding="utf-8", newline="\n").write("\n".join([r for r in cur if r != ""] + ret) + "\n")
os.makedirs(PO + "/salvage", exist_ok=True)
with open(PO + "/salvage/rule-%s-ceo-1387.tsv" % stamp, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("topic\towner\told_state\twhat\trank\n")
    for l in log: fh.write("\t".join(l) + "\n")
print("WRITTEN")
