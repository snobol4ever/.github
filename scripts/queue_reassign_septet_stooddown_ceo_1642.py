#!/usr/bin/env python3
"""Re-lane the FREE rows the SEPTET flip left under stood-down owner cells (CEO-1642, ceo 2026-10-11).

MODE line 2 (SEPTET, CEO-1601): ICON, SNOBOL4, PASCAL, SNOCONE and REBUS are the ceo's; hq_runtime, hq_collector, hq_zetas and hq_templates
are the cto's seats as their officer. `next` constrains the pick by the owner column, so a FREE row owned by a stood-down seat is served to
nobody (CEO-1530: a seat a flip leaves with 0 FREE rows is served nothing) -- 117 rows sat unserved while the ceo's lane read empty.
THE ACT: every row whose state is exactly FREE and whose owner is hq_snobol4, hq_icon or hq_snocone -> ceo; hq_runtime, hq_collector, hq_zetas
or hq_templates -> cto. Never a claimed, assigned or parked row (CEO-755c); hq_pascal's rows stay (ASSIGNED by the ceo, never picked by
language). A dated .bak of QUEUE.tsv beside it; the table read and written in binary, only the owner cells changed (OUR FILES ARE LF).
Run: python3 queue_reassign_septet_stooddown_ceo_1642.py --apply   (without --apply it only counts)
"""
import datetime, shutil, sys
Q = '/home/resources/postoffice/QUEUE.tsv'
TO_CEO = {b'hq_snobol4', b'hq_icon', b'hq_snocone'}
TO_CTO = {b'hq_runtime', b'hq_collector', b'hq_zetas', b'hq_templates'}
def main():
    apply = '--apply' in sys.argv
    data = open(Q, 'rb').read(); lines = data.split(b'\n'); trailing = lines[-1] == b''
    if trailing: lines = lines[:-1]
    out = []; moved = {b'ceo': 0, b'cto': 0}; untouched = 0
    for l in lines:
        c = l.split(b'\t')
        if len(c) >= 4 and c[3] == b'FREE' and (c[2] in TO_CEO or c[2] in TO_CTO):
            new = b'ceo' if c[2] in TO_CEO else b'cto'; moved[new] += 1; c[2] = new; out.append(b'\t'.join(c))
        else:
            out.append(l)
            if len(c) >= 4 and (c[2] in TO_CEO or c[2] in TO_CTO): untouched += 1
    print('to ceo', moved[b'ceo'], 'to cto', moved[b'cto'], 'stood-down owners left on non-FREE rows', untouched)
    if not apply: print('(count only; --apply writes)'); return 0
    bak = Q + '.bak.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-ceo-1642-septet-stooddown-relane'
    shutil.copy2(Q, bak)
    open(Q, 'wb').write(b'\n'.join(out) + (b'\n' if trailing else b''))
    print('written; backup', bak)
    return 0
if __name__ == '__main__': sys.exit(main())
