import os, re, glob, json, collections
SO='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'; W=SO+'/hdr/SCRIP/src/'; S4='/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad'
def rd(p): return open(p, errors='surrogateescape').read()
def wr(p,t): open(p,'w',errors='surrogateescape').write(t)
SEP='/*' + '-'*196 + '*/'; rep=[]
WORD=re.compile(r'(?<![\w])[^\W\d]\w*')
def strip(text):
    text=re.sub(r'/\*.*?\*/', ' ', text, flags=re.S); text=re.sub(r'//[^\n]*', ' ', text); text=re.sub(r'"(\\.|[^"\\\n])*"', '""', text); return text
# A. emit_resumable_frame out of line (emit.cpp defines g_emit_cfg); emit_regime.h stops reaching the graph record
p=W+'emitter/emit_regime.h'; t=rd(p); old='static inline int emit_resumable_frame(void) { return (g_emit_cfg && g_emit_cfg->pf.resumable_frame) ? 1 : 0; }\n'; assert old in t
t=t.replace(old,'int emit_resumable_frame(void);\n'); assert '#include "ir/ir_graph.h"\n' in t; t=t.replace('#include "ir/ir_graph.h"\n','',1); wr(p,t)
p=W+'emitter/emit.cpp'; t=rd(p); assert t.endswith('}\n'); t+=SEP+'\n'+'extern "C" int emit_resumable_frame(void) { return (g_emit_cfg && g_emit_cfg->pf.resumable_frame) ? 1 : 0; }\n'; wr(p,t); rep.append('A emit_resumable_frame -> emit.cpp; emit_regime.h reaches no IR header')
# H. gen_runtime.h's two graph-reading bodies -> gen_runtime.c
p=W+'runtime/builtins/gen_runtime.h'; t=rd(p); L=t.split('\n')
i1=[k for k,l in enumerate(L) if l.startswith('static inline IR_graph_t *bb_graph_of_proc(')]; i2=[k for k,l in enumerate(L) if l.startswith('static inline IR_t *bb_proc_entry(')]; assert len(i1)==1 and len(i2)==1, (i1,i2)
b1=L[i1[0]]; b2=L[i2[0]]; assert b1.count('{')==b1.count('}') and b2.count('{')==b2.count('}'), 'one-line bodies expected'
L[i1[0]]='IR_graph_t *bb_graph_of_proc(const ProcEntry *e);'; L[i2[0]]='IR_t *bb_proc_entry(const ProcEntry *e);'
t='\n'.join(L); assert '#include "ir/ir_graph.h"\n' in t; t=t.replace('#include "ir/ir_graph.h"\n','#include "ir/ir_fwd.h"\n',1); wr(p,t)
p=W+'runtime/builtins/gen_runtime.c'; t=rd(p); assert 'gen_runtime.h' in t
if '#include "ir/ir_graph.h"' not in t:
    ms=list(re.finditer(r'^#include [<"][^>"]+[>"]\n', t, re.M)); k=ms[-1].end(); t=t[:k]+'#include "ir/ir_graph.h"\n'+t[k:]
if not t.endswith('\n'): t+='\n'
t+=SEP+'\n'+re.sub(r'^static inline ','',b1)+'\n'+SEP+'\n'+re.sub(r'^static inline ','',b2)+'\n'; wr(p,t); rep.append('H bb_graph_of_proc, bb_proc_entry -> gen_runtime.c; gen_runtime.h forward-declares')
open(S4+'/hdr4_moved.txt','a').write('emit_resumable_frame\nbb_graph_of_proc\nbb_proc_entry\n')
# B. units whose emit_regime.h include is unused now that the match registers are bb_box.h's
BOX={'Σ','Δ','Ω','Σlen','α','β','bb_box_fn','bb_node_t'}
for u in ['driver/scrip.c','lower/lower_common.c','lower/lower_icon.c','runtime/core/stmt_exec.c','runtime/rt_runtime.c','templates/bb/bb_scan_any.cpp','templates/bb/bb_scan_bal.cpp','templates/bb/bb_scan_find.cpp','templates/bb/bb_scan_many.cpp','templates/bb/bb_scan_match.cpp','templates/bb/bb_scan_upto.cpp','templates/x86/x86_asm.cpp','templates/x86/x86_icn.cpp','templates/x86/x86_rodata.cpp']:
    p=W+u; t=rd(p); m=re.search(r'^#include "emitter/emit_regime\.h"\n', t, re.M); assert m, u
    tk=set(WORD.findall(strip(t))); new='#include "ir/bb_box.h"\n' if (tk & BOX) and '#include "ir/bb_box.h"' not in t else ''
    t=t[:m.start()]+new+t[m.end():]; wr(p,t); rep.append('B %s: emit_regime.h -> %s' % (u.split('/')[-1], new.strip() or 'dropped'))
# C. the fixer's raw-text over-includes (strings and comments named an op): out where the instrument reads them unused and the unit reads no record field
drop={'templates/bb/bb_call_fn.cpp':['ir/ir_node.h'],'templates/bb/bb_call_value.cpp':['ir/stage2.h'],'templates/bb/bb_glue_flat.cpp':['ir/stage2.h'],'templates/bb/bb_iterate.cpp':['ir/ir_ops.h'],'templates/bb/bb_match_atp.cpp':['ir/ir_ops.h'],'templates/bb/bb_match_flush.cpp':['ir/ir_ops.h','ir/stage2.h'],'templates/bb/bb_match_replace.cpp':['ir/ir_ops.h'],'templates/bb/bb_match_value.cpp':['ir/ir_ops.h'],'templates/bb/bb_scan_alternate.cpp':['ir/ir_ops.h'],'templates/bb/bb_suspend.cpp':['ir/ir_ops.h'],'templates/bb/bb_table_hdr.cpp':['ir/ir_ops.h'],'templates/bb/bb_to_by.cpp':['ir/ir_ops.h'],'templates/bb/bb_to.cpp':['ir/ir_ops.h'],'templates/bb/bb_var.cpp':['ir/ir_ops.h'],'planner/planner_road.cpp':['planner/g_planner.h']}
for u,hs in drop.items():
    p=W+u; t=rd(p)
    for h in hs:
        m=re.search(r'^#include "%s"\n' % re.escape(h), t, re.M); assert m, (u,h); t=t[:m.start()]+t[m.end():]
    wr(p,t)
rep.append('C %d over-includes dropped in %d units' % (sum(len(v) for v in drop.values()), len(drop)))
# I. x86_armed.h names IR_STRICT_RELOP_NUMIFY_BLANK in a macro body: it includes ir_node.h (R2 for a header)
p=W+'templates/x86/x86_armed.h'; t=rd(p); assert '#include "emitter/emit_state.h"\n' in t and 'IR_STRICT_RELOP_NUMIFY_BLANK' in t
t=t.replace('#include "emitter/emit_state.h"\n','#include "emitter/emit_state.h"\n#include "ir/ir_node.h"\n',1); wr(p,t); rep.append('I x86_armed.h includes ir/ir_node.h')
# E. ir_ops.h merges into ir_node.h: the node embeds the op enum, so every reacher of one reaches the other (measured 48 of 48); one family header
ops=rd(W+'ir/ir_ops.h').split('\n'); node=rd(W+'ir/ir_node.h').split('\n')
def body(lines, name):
    a=lines.index('extern "C" {')+2; b=len(lines)-1-lines[::-1].index('#ifdef __cplusplus')
    return lines[a:b]
ob=body(ops,'ops'); nb=body(node,'node')
assert ob[0].startswith('typedef enum {') and nb[0].startswith('typedef struct { IR_t * node;'), (ob[0], nb[0])
WRAP_O=['#ifdef __cplusplus', 'extern "C" {', '#endif']; WRAP_C=['#ifdef __cplusplus', '}', '#endif']
merged=['#ifndef SCRIP_IR_NODE_H','#define SCRIP_IR_NODE_H','#include <stdint.h>','#include "ir/descr.h"','#include "ir/ir_fwd.h"']+WRAP_O+ob+nb+WRAP_C+['#endif','']
wr(W+'ir/ir_node.h','\n'.join(merged)); os.remove(W+'ir/ir_ops.h')
n_files=0
for f in glob.glob(W+'**/*', recursive=True):
    if not os.path.isfile(f) or not re.search(r'\.(c|cpp|h|inc)$', f): continue
    t=rd(f)
    if 'ir/ir_ops.h' not in t: continue
    t=t.replace('#include "ir/ir_ops.h"\n','#include "ir/ir_node.h"\n')
    first=t.find('#include "ir/ir_node.h"\n'); rest=t[first+len('#include "ir/ir_node.h"\n'):].replace('#include "ir/ir_node.h"\n','')
    t=t[:first+len('#include "ir/ir_node.h"\n')]+rest; wr(f,t); n_files+=1
rep.append('E ir_ops.h merged into ir_node.h (%d lines); %d files retargeted and de-duplicated' % (len(merged)-1, n_files))
left=[f for f in glob.glob(W+'**/*', recursive=True) if os.path.isfile(f) and re.search(r'\.(c|cpp|h|inc)$', f) and 'ir_ops.h' in rd(f)]
rep.append('ir_ops.h mentions left: %s' % ([x[len(W):] for x in left] or 'none'))
print('\n'.join(rep))
