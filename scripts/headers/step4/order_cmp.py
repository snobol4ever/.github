#!/usr/bin/env python3
# order_cmp.py -- compares two include-order records (hdr_order.py) unit by unit on the headers WHOSE INLINE BODIES THE UNIT NAMES:
# a static inline is emitted in definition order, so a unit whose mattering headers are first reached in a different order has a
# different .text layout (R5 DIFF with equal section sizes). IR.h and its five families are one token; bb_box.h's bodies are gone;
# planner.h's one body is zeta_plan.h's.   order_cmp.py parent.json child.json PARENT_SRC CHILD_SRC
import sys, json, re, glob, os
pj, cj, PS, CS = sys.argv[1:5]
P=json.load(open(pj)); C=json.load(open(cj))
WORD=re.compile(r'(?<![\w])[^\W\d]\w*')
def rd(p): return open(p, errors='surrogateescape').read()
def strip(text):
    text=re.sub(r'/\*.*?\*/', ' ', text, flags=re.S); text=re.sub(r'//[^\n]*', ' ', text); text=re.sub(r'"(\\.|[^"\\\n])*"', '""', text); return text
def inl(src):
    out={}
    for f in glob.glob(src+'/**/*.h', recursive=True):
        names=set(re.findall(r'static\s+inline\s+[\w\s\*]+?\b(\w+)\s*\(', rd(f)))
        if names: out[f[len(src)+1:]]=names
    return out
PI=inl(PS); CI=inl(CS)
GROUP={'ir/IR.h':'IRFAM','ir/ir_ops.h':'IRFAM','ir/ir_node.h':'IRFAM','ir/ir_graph.h':'IRFAM','ir/ir_construct.h':'IRFAM','ir/ir_fwd.h':None,'planner/planner.h':'PLAN','planner/zeta_plan.h':'PLAN','planner/planner_head.h':None,'ir/bb_build.h':None}
def key(h): return GROUP.get(h, h) if h in GROUP else h
def seq_of(order, inlmap, u, tk):
    out=[]; seen=set()
    for d,h in order.get(u, []):
        k=key(h)
        if k is None: continue
        names=inlmap.get(h, set())
        if h=='ir/bb_box.h' and h in PI and inlmap is CI: names=set()
        if not (names & tk): continue
        if k in seen: continue
        seen.add(k); out.append(k)
    return out
diff=0; units=sorted(set(P)|set(C))
for u in units:
    cp=os.path.join(CS, u[4:]) if u.startswith('src/') else None
    if not cp or not os.path.isfile(cp): continue
    tk=set(WORD.findall(strip(rd(cp))))
    a=seq_of(P, PI, u, tk); b=seq_of(C, CI, u, tk)
    if a!=b:
        diff+=1; print('ORDER %s\n   parent: %s\n   child : %s' % (u, ' '.join(a), ' '.join(b)))
print('units=%d order-differences=%d' % (len(units), diff))
