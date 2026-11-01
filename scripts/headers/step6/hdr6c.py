#!/usr/bin/env python3
# hdr6c.py -- headers step 6C (ARCH-HEADER-SPLIT R2 and section 5 row 6; CEO-2032): every quoted include that resolves through an -I directory
# instead of the includer's own directory is rewritten to its path from src/; the generated parsers are reached through their .y/.l sources
# (the generated files are never hand-edited: the regen script rewrites them); the Makefile's -I lists are cut to -I$(SRC). A spelling move:
# the same file opens in the same order, so R5 reads every object byte-identical.   hdr6c.py <SCRIP root> [--apply]
import os, re, sys, glob, collections
ROOT=os.path.abspath(sys.argv[1]); W=ROOT+'/src/'; APPLY='--apply' in sys.argv
INCDIRS=['', 'ir/','lower/','emitter/','runtime/core/','runtime/builtins/','runtime/','runtime/rt/','parsers/snobol4/','parsers/raku/','optimizer/','templates/bb/','templates/xa/','templates/x86/']
INC=re.compile(r'^([ \t]*#[ \t]*include[ \t]+")([^"]+)(".*)$', re.M)
GENERATED={'parsers/snobol4/snobol4.tab.c','parsers/snobol4/snobol4.tab.h','parsers/snobol4/snobol4.lex.c','parsers/pascal/pascal.tab.c','parsers/pascal/pascal.tab.h','parsers/pascal/pascal.lex.c','parsers/rebus/rebus.tab.c','parsers/rebus/rebus.tab.h','parsers/rebus/lex.rebus.c','parsers/snocone/snocone_parse.tab.c','parsers/snocone/snocone_parse.tab.h'}
def resolve(includer_rel, inc):
    own=os.path.normpath(os.path.join(os.path.dirname(includer_rel), inc))
    if os.path.isfile(W+own): return own, 'own'
    for d in INCDIRS:
        c=os.path.normpath(d+inc)
        if os.path.isfile(W+c): return c, 'incdir'
    return None, None
files=sorted(f[len(W):] for f in glob.glob(W+'**/*', recursive=True) if os.path.isfile(f) and re.search(r'\.(c|cpp|h|inc|s|S|y|l)$', f))
changes={}; stats=collections.Counter(); unresolved=[]; rewritten=collections.Counter()
for rel in files:
    text=open(W+rel, errors='surrogateescape').read()
    def sub(m):
        inc=m.group(2); target, how = resolve(rel, inc)
        if target is None: unresolved.append((rel, inc)); return m.group(0)
        if how=='own' and '/' not in inc: stats['same-dir bare kept']+=1; return m.group(0)
        if inc==target: stats['already a path from src']+=1; return m.group(0)
        stats['rewritten (%s)' % ('own-dir relative' if how=='own' else 'through an -I directory')]+=1; rewritten[rel]+=1
        return m.group(1)+target+m.group(3)
    new=INC.sub(sub, text)
    if new!=text: changes[rel]=new
gen_touched=[r for r in changes if r in GENERATED]
print('files=%d changed=%d (generated among them: %d, rewritten through their sources: %s)' % (len(files), len(changes), len(gen_touched), ' '.join(sorted(r for r in changes if r.endswith(('.y','.l'))))))
for k,v in sorted(stats.items()): print('  %6d %s' % (v,k))
if unresolved: print('UNRESOLVED (left as written):', unresolved[:12])
top=rewritten.most_common(8); print('  most rewritten:', ' '.join('%s:%d' % (os.path.basename(k),v) for k,v in top))
mk=open(ROOT+'/Makefile').read()
old78='CBASE   := -O0 -g $(DBGMAP) $(WARN) $(DEPFLAGS) -I$(SRC) -I$(SRC)/ir -I$(SRC)/lower -I$(SRC)/emitter -I$(SRC)/runtime/core -I$(RT)'
assert mk.count(old78)==1, 'CBASE line'
m80=re.search(r'^CXXRT   := -O0 -g \$\(DBGMAP\) \$\(WARN\) \$\(DEPFLAGS\) -std=c\+\+17 -finput-charset=UTF-8 -I\$\(SRC\)(?: -I\$\((?:SRC|RT)\)[^ ]*)+', mk, re.M); assert m80, 'CXXRT line'
m1930=re.search(r'^RT_INCS := -I\$\(SRC\)(?: -I\$\((?:SRC|RT)\)[^ \\]*)+ \\\n(?:    (?:-I\$\((?:SRC|RT)\)[^ \n]*)(?: -I\$\((?:SRC|RT)\)[^ \n]*)*)\n', mk, re.M); assert m1930, 'RT_INCS lines'
mk2=mk.replace(old78, 'CBASE   := -O0 -g $(DBGMAP) $(WARN) $(DEPFLAGS) -I$(SRC)')
m80=re.search(r'^CXXRT   := -O0 -g \$\(DBGMAP\) \$\(WARN\) \$\(DEPFLAGS\) -std=c\+\+17 -finput-charset=UTF-8 -I\$\(SRC\)(?: -I\$\((?:SRC|RT)\)[^ ]*)+', mk2, re.M)   # re-matched on the edited text: the CBASE cut moved every later offset
mk2=mk2[:m80.start()]+'CXXRT   := -O0 -g $(DBGMAP) $(WARN) $(DEPFLAGS) -std=c++17 -finput-charset=UTF-8 -I$(SRC)'+mk2[m80.end():]
m1930=re.search(r'^RT_INCS := -I\$\(SRC\)(?: -I\$\((?:SRC|RT)\)[^ \\]*)+ \\\n(?:    (?:-I\$\((?:SRC|RT)\)[^ \n]*)(?: -I\$\((?:SRC|RT)\)[^ \n]*)*)\n', mk2, re.M)
mk2=mk2[:m1930.start()]+'RT_INCS := -I$(SRC)\n'+mk2[m1930.end():]
left=re.findall(r'-I\$\((?:SRC|RT)\)/\S+|-I\$\(RT\)', mk2); print('Makefile: three -I lists cut to -I$(SRC); other -I$(SRC)/x or -I$(RT) tokens left:', left or 'none')
if APPLY:
    gen_skipped=0
    for rel,new in changes.items():
        if rel in GENERATED: gen_skipped+=1; continue
        open(W+rel,'w',errors='surrogateescape').write(new)
    open(ROOT+'/Makefile','w').write(mk2)
    print('APPLIED: %d files rewritten (%d generated files left for the regen script), Makefile cut' % (len(changes)-gen_skipped, gen_skipped))
else: print('(dry run; --apply writes)')
