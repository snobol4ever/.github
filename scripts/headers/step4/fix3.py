import re
W='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad/hdr/SCRIP/src/'; S4='/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad'
def rd(p): return open(p, errors='surrogateescape').read()
def wr(p,t): open(p,'w',errors='surrogateescape').write(t)
SEP='/*' + '-'*196 + '*/'
p=W+'emitter/emit.cpp'; t=rd(p)
tail=SEP+'\n'+'extern "C" int emit_resumable_frame(void) { return (g_emit_cfg && g_emit_cfg->pf.resumable_frame) ? 1 : 0; }\n'
assert t.endswith(tail); t=t[:-len(tail)]
m=re.search(r'^IR_graph_t \* ?g_emit_cfg[^\n]*\n', t, re.M); assert m, 'g_emit_cfg definition'
t=t[:m.end()]+'extern "C" int emit_resumable_frame(void) { return (g_emit_cfg && g_emit_cfg->pf.resumable_frame) ? 1 : 0; }\n'+t[m.end():]; wr(p,t)
print('emit_resumable_frame defined right after g_emit_cfg (line %d), not at the end of emit.cpp' % (t[:m.end()].count('\n')+1))
mv=open(S4+'/hdr4_moved.txt').read().split()
for n in ['ir_is_call_road_kind','ir_norm_call_kind','ir_define_sr_citizen']:
    if n not in mv: mv.append(n)
open(S4+'/hdr4_moved.txt','w').write('\n'.join(mv)+'\n'); print('moved list:', len(mv), 'names (the three one-line callees whose copies followed the moved bodies added)')
