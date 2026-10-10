#!/usr/bin/env python3
"""Delete exactly the six stray pascal-demos rows the coo's fixture run wrote to /home/resources/progress/results.tsv (CEO-1625).

Lon 2026-10-10, in-chat to the coo, verbatim: "Get CEO to delete those rows for you." The ceo's own run of this deletion was refused by
the session's auto-mode classifier (Modify Shared Resources), so the command is staged here for Lon to run, one critical command:

    python3 /home/claude_ceo/.github/scripts/util_delete_six_stray_pasdemo_progress_rows_ceo_1625.py

THE SELECTION (the coo's, all six conditions): ts_utc = 2026-10-10T20:30:02, scrip = 08c00e5b4, measurer = coo, suite = pascal-demos,
program one of demos/pascal/p4/int/int.pas, demos/pascal/p5/pcom/pcom.pas, demos/pascal/p5/pint/pint.pas -- m3 and m4 each, six rows.
The other eight rows of that timestamp (basics, pascals, prettyp, startrek, m3 and m4) are true readings and are KEPT.
THE METHOD (the appender's own): an exclusive flock on results.tsv.lock, a dated .bak beside the table, the filtered table written to a
temp file in the same directory in BINARY (our files are LF; only the six lines change), its mode copied, os.replace into place, the
lock released. If the selection does not read exactly 6, nothing is written and the script exits 1.
"""
import datetime
import fcntl
import os
import shutil
import sys

P = '/home/resources/progress/results.tsv'
L = P + '.lock'
PROGS = {b'demos/pascal/p4/int/int.pas', b'demos/pascal/p5/pcom/pcom.pas', b'demos/pascal/p5/pint/pint.pas'}


def stray(line):
    c = line.rstrip(b'\n').split(b'\t')
    return len(c) >= 8 and c[0] == b'2026-10-10T20:30:02' and c[1] == b'08c00e5b4' and c[3] == b'coo' and c[5] == b'pascal-demos' and c[7] in PROGS


def main():
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bak = P + '.bak-' + stamp + '-ceo-1625-six-stray-pasdemo-rows'
    with open(L, 'a') as lk:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        try:
            data = open(P, 'rb').read()
            lines = data.split(b'\n')
            trailing = lines[-1] == b''
            if trailing:
                lines = lines[:-1]
            n = sum(1 for l in lines if stray(l))
            print('rows', len(lines), 'stray', n, 'trailing-newline', trailing)
            if n != 6:
                print('REFUSED: the selection reads', n, 'not 6; nothing written')
                return 1
            shutil.copy2(P, bak)
            kept = [l for l in lines if not stray(l)]
            out = b'\n'.join(kept) + (b'\n' if trailing else b'')
            tmp = P + '.tmp-ceo-1625'
            with open(tmp, 'wb') as f:
                f.write(out)
            shutil.copymode(P, tmp)
            os.replace(tmp, P)
            print('written: kept', len(kept), 'removed', len(lines) - len(kept), 'backup', bak)
            left = sum(1 for l in open(P, 'rb').read().split(b'\n') if stray(l))
            print('verify: stray rows left', left)
            return 0 if left == 0 else 1
        finally:
            fcntl.flock(lk.fileno(), fcntl.LOCK_UN)


if __name__ == '__main__':
    sys.exit(main())
