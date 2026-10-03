import sys,os
ROOTS=['ceo','cto','coo','cfo','icon','prolog','pascal','snocone','snobol4','raku','templates']
BLOCK=("\n⛔⭐⭐⭐⭐ **LARGE CHUNKS: A SCHEME CHANGE IS DEPLOYED TO THE WHOLE POPULATION, NEVER TO SMALL SETS (Lon 2026-10-03 14:2x-14:4x CDT, in-chat to the ceo, verbatim: *\"So, I mean ensure large chunks of new developments are rolled-out, not small chunks.\"* · *\"To be clear, when I said larger chunks, I meant after one huge scheme change do not roll out that change to small sets, use larger sets to deploy.\"*; ruled CEO-1478/1479/1480; RULES.md § FACT RULE — LARGE CHUNKS):** once a scheme changes — a frame layout, a calling convention, a storage shape, a dialect rule, a runtime entry replaced by an emitted sequence — it is rolled out to the WHOLE population it governs at once: every counted site, every helper of the family, every corpus file, every suite, every frontend a shared node reaches; never a small set first. A partial deployment is REFUSED in review as a small set; the DONE-WHEN measures the whole population so a partial rollout cannot close it; batching (CEO-1316) grades landings and never sizes them; *one landing per row* means the whole row in that landing. Who does the work is Lon's seating (CEO-1480: the Prolog rewrite is hq_prolog's alone).\n")
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
