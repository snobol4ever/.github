import sys, glob, os, re, collections
S='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'
W=S+'/hdr/SCRIP'
OBJ='/tmp/si_objs'+W.replace('/','-')
def dset(dirs):
    out={}
    for d in dirs:
        for f in glob.glob(d+'/**/*.d', recursive=True):
            t=open(f,errors='replace').read().replace('\\\n',' ')
            parts=t.split(':',1)
            if len(parts)<2: continue
            pre=parts[1].split()
            unit=None; hs=set()
            for p in pre:
                q=p.split('/src/',1)[-1] if '/src/' in p else (p[4:] if p.startswith('src/') else None)
                if q is None: continue
                if unit is None and re.search(r'\.(c|cpp)$', q): unit=q; continue
                if q.endswith('.h') or q.endswith('.inc'): hs.add(q)
            if unit: out.setdefault(unit,set()).update(hs)
    return out
par=dset([S+'/parent-objs-b275/obj', S+'/parent-objs-b275/out'])
now=dset([OBJ, W+'/out'])
print('units parent=%d now=%d' % (len(par), len(now)))
# direct includers of each header (by basename match in src)
src_hdrs={}
for f in glob.glob(W+'/src/**/*.h', recursive=True)+glob.glob(W+'/src/**/*.inc', recursive=True):
    src_hdrs[f[len(W)+5:]]=re.findall(r'^#include "([^"]+)"', open(f,errors='replace').read(), re.M)
def includers(h):
    b=os.path.basename(h)
    return {x for x,incs in src_hdrs.items() if any(i==h or i.endswith('/'+b) or i==b for i in incs)}
for h in sys.argv[1:]:
    P={u for u,hs in par.items() if h in hs}; N={u for u,hs in now.items() if h in hs}
    print('\n== %s: parent %d now %d; new %d gone %d' % (h, len(P), len(N), len(N-P), len(P-N)))
    inc=includers(h)
    for u in sorted(N-P):
        via=sorted(x for x in inc if x in now[u])
        newvia=[x for x in via if x not in par.get(u,set())]
        print('   + %-44s via %s%s' % (u, ' '.join(via)[:80], ('  NEW:'+' '.join(newvia)) if newvia else ''))
    for u in sorted(P-N)[:6]: print('   - %s' % u)
