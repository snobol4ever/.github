#!/bin/bash
# remove_probe_fixture_rows_coo_284.sh -- LON-RUN (a seat may not delete rows from the live progress table; the coo asked at
# COO-284, the ceo staged it at CEO-1501). Removes EXACTLY the eight rows a gate (b) probe of the coo appended to
# /home/resources/progress/results.tsv on 2026-10-04T01:54:14: measurer root:wt, suite pascal-bench, programs deepdecl,
# deepnodecl, livedecl and livenodecl in m3 and m4, note dev-pass=probe. Matched on every one of those cells, never on a
# position. Backs the table up beside itself first, writes in binary with LF, refuses rc=2 unless exactly eight rows match.
set -u
R=/home/resources/progress/results.tsv
[ -f "$R" ] || { echo "REFUSE(2): no $R"; exit 2; }
B="$R.bak-$(date +%Y%m%d-%H%M%S)-coo-284"
cp -p "$R" "$B" || { echo "REFUSE(2): backup failed"; exit 2; }
python3 - "$R" <<'PY'
import sys
r=sys.argv[1]; data=open(r,"rb").read()
lines=data.split(b"\n")
def is_probe(l):
    c=l.split(b"\t")
    return len(c)>=12 and c[0]==b"2026-10-04T01:54:14" and c[3]==b"root:wt" and c[5]==b"pascal-bench" and c[7] in (b"deepdecl",b"deepnodecl",b"livedecl",b"livenodecl") and c[11].startswith(b"dev-pass=probe")
hits=[l for l in lines if is_probe(l)]
if len(hits)!=8:
    print("REFUSE(2): expected exactly 8 probe rows, found %d; nothing written" % len(hits)); sys.exit(2)
kept=[l for l in lines if not is_probe(l)]
open(r,"wb").write(b"\n".join(kept))
print("REMOVED 8 rows; table now %d lines (was %d)" % (len(kept)-1, len(lines)-1))
PY
rc=$?
[ $rc -eq 0 ] && echo "backup: $B" || { echo "the table is untouched; the backup $B is identical and may be removed"; exit $rc; }
