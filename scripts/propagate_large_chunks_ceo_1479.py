import sys,os
ROOTS=['ceo','cto','coo','cfo','icon','prolog','pascal','snocone','snobol4','raku','templates']
BLOCK=("\n⛔⭐⭐⭐⭐ **LARGE CHUNKS: A DEVELOPMENT ROLLS OUT WHOLE, NEVER IN SLICES (Lon 2026-10-03 14:2x CDT, in-chat to the ceo, verbatim: *\"You should speed that up by increasing those increments. We do not want to take a year.\"* · *\"So, I mean ensure large chunks of new developments are rolled-out, not small chunks.\"*; ruled CEO-1478/1479; RULES.md § FACT RULE — LARGE CHUNKS):** a row is cut by MECHANISM, never by site, helper, file or language; its one landing replaces the whole mechanism it names — every counted site, every helper of the family, every frontend a shared node reaches — and deletes the old mechanism in the same commit; a partial replacement is REFUSED in review as a slice; two genuine mechanisms run IN PARALLEL on different seats with the shared layout agreed by telegram first, never serially on one seat; batching (CEO-1316) grades landings and never sizes them, and *one landing per row* means the WHOLE row in that landing; the DONE-WHEN measures the whole population so a slice cannot close it.\n")
apply='--apply' in sys.argv; n=0
for r in ROOTS:
    p=f'/home/claude_{r}/CLAUDE.md'
    if not os.path.exists(p): print('missing',p); continue
    b=open(p,'rb').read().decode()
    if 'FACT RULE — LARGE CHUNKS' in b: print('already',p); continue
    i=b.index('\n',b.index('# CLAUDE.md'))+1
    nb=b[:i]+BLOCK+b[i:]
    if apply: open(p,'wb').write(nb.encode())
    n+=1; print(('wrote ' if apply else 'would write ')+p)
print(('APPLIED' if apply else 'DRY-RUN'),n,'roots')
