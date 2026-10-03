import sys,os
ROOTS=['ceo','cto','coo','cfo','icon','prolog','pascal','snocone','snobol4','raku','templates']
NEW=("⛔⭐⭐⭐⭐ **NO FRAME MARKERS, NO SECOND STACK, THE MAPS STAY: THE STACK IS MAPPED, NOT TAGGED (Lon 2026-09-30, in-chat to the cto, three words of one hour, verbatim: *\"Seems you should get rid of frame markers; they appear to be problematic. Find another better solution than scanning to markers on a stack.\"* · *\"How silly. So you have an side-car stack to manage your stack. Is that one way of saying it?\"* · *\"Do you have a plan without markers and without TWO stacks which should be one?\"*; and 2026-10-03 17:1x CDT, in-chat to the cto, verbatim: *\"W do not want markers on the stack. We do want the stack mapped. We spent 3-4 days doing that. We do NOT want everything on the stack tagged. What is your malfunction?\"*; ruled CEO-1368, corrected CEO-1371, corrected again CEO-1492; RULES.md § FACT RULE — NO FRAME MARKERS):** the collector scans the stack for no marker and keeps no side-car ledger of frames; the compile-time frame maps of ARCH-GC-COMPILE-TIME-FRAME-MAPS.md § 7 (FROZEN) STAY, one static map per activation frame; NOTHING on the stack is tagged beyond the DESCR type field § 7 already names, and no raw word is widened into a tagged cell; only the MARKER SCAN goes. The *no map, every raw word a tagged cell* design of CEO-1371 was the cto's reading under Lon's name and is WITHDRAWN (the cto's own retraction, .github 2c42b45c4). The marker-free map-lookup design goes to Lon in a page BEFORE any code; the cto, seated Fable 5.1 at xhigh by Lon for it, owns the redesign as its ONE THING on its rank-0 `gc-one-stack-…` row, whose DONE-WHEN it re-cuts from the withdrawn criterion to the marker-free lookup once Lon approves the page.\n")
apply='--apply' in sys.argv; n=0
for r in ROOTS:
    p=f'/home/claude_{r}/CLAUDE.md'
    if not os.path.exists(p): print('missing',p); continue
    b=open(p,'rb').read().decode()
    k='⛔⭐⭐⭐⭐ **NO FRAME MARKERS, NO SECOND STACK'
    if k not in b: print('no block in',p); continue
    s=b.index(k); e=b.index('\n',s)+1
    nb=b[:s]+NEW+b[e:]
    if apply: open(p,'wb').write(nb.encode())
    n+=1; print(('wrote ' if apply else 'would write ')+p)
print(('APPLIED' if apply else 'DRY-RUN'),n,'roots')
