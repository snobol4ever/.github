import sys,os
ROOTS=['ceo','cto','coo','cfo','icon','prolog','pascal','snocone','snobol4','raku','templates']
BLOCK=("\n⛔⭐⭐⭐⭐ **LARGE CHUNKS: A SCHEME CHANGE ROLLS OUT SMALL ONCE WITH A SMOKE, THEN EVERYWHERE, THEN ULTRACODE (Lon 2026-10-03 14:2x-15:2x CDT; to the ceo, verbatim: *\"So, I mean ensure large chunks of new developments are rolled-out, not small chunks.\"* · *\"after one huge scheme change do not roll out that change to small sets, use larger sets to deploy.\"*; to hq_prolog, verbatim: *\"after the small roll out and a smoke test of the new feature, then you do massive roll out; roll out every where. Then I'll run ultracode.\"*; ruled CEO-1478..1484; RULES.md § FACT RULE — LARGE CHUNKS):** build the scheme change whole; roll it out ONCE to a small set (one language, one regime) and smoke-test it there, curing what the smoke finds; then the MASSIVE roll-out everywhere the scheme governs, in large sets reaching the whole population in a few landings, never a site or a helper at a time, and never a second small set; then Lon runs ultracode over the whole (the ceo asks him when it is on origin). The DONE-WHEN measures the whole population so the row closes at the end of the massive roll-out and the smoke is a ledger line; batching (CEO-1316) grades landings and never sizes them; every set lands green on its net. Who does the work is Lon's seating (CEO-1480: the Prolog rewrite is hq_prolog's alone).\n")
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
