import sys,os
ROOTS=['ceo','cto','coo','cfo','icon','prolog','pascal','snocone','snobol4','raku','templates']
BLOCK=("\n⛔⭐⭐⭐⭐ **LARGE CHUNKS: A SCHEME CHANGE IS DEPLOYED IN LARGE SETS, NEVER IN SMALL ONES (Lon 2026-10-03 14:2x-14:5x CDT, in-chat to the ceo, verbatim: *\"So, I mean ensure large chunks of new developments are rolled-out, not small chunks.\"* · *\"To be clear, when I said larger chunks, I meant after one huge scheme change do not roll out that change to small sets, use larger sets to deploy.\"*; ruled CEO-1478..1481; RULES.md § FACT RULE — LARGE CHUNKS):** once a scheme changes — a frame layout, a calling convention, a storage shape, a dialect rule, a runtime entry replaced by an emitted sequence — it is deployed to its population in LARGE SETS: increments sized to reach the whole population in a few landings, not dozens; a landing carrying a small set (a site, a helper, a handful of files) is REFUSED in review as a small chunk; the whole in one landing is the ordinary case for a small population and never required for a large one; every set lands green on its net; the DONE-WHEN measures the whole population so the row closes at the last set; batching (CEO-1316) grades landings and never sizes them. Who does the work is Lon's seating (CEO-1480: the Prolog rewrite is hq_prolog's alone).\n")
apply='--apply' in sys.argv; n=0
for r in ROOTS:
    p=f'/home/claude_{r}/CLAUDE.md'
    if not os.path.exists(p): print('missing',p); continue
    b=open(p,'rb').read().decode()
    if 'FACT RULE — LARGE CHUNKS' in b:
        if '--replace' not in sys.argv: print('already',p); continue
        a=b.index('\n⛔⭐⭐⭐⭐ **LARGE CHUNKS'); z=b.index('\n',a+1)+1; b=b[:a]+b[z:]
    i=b.index('\n',b.index('# CLAUDE.md'))+1
    nb=b[:i]+BLOCK+b[i:]
    if apply: open(p,'wb').write(nb.encode())
    n+=1; print(('wrote ' if apply else 'would write ')+p)
print(('APPLIED' if apply else 'DRY-RUN'),n,'roots')
