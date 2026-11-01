import os, re, sys, glob, json, collections
S='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'
W=S+'/hdr/SCRIP/src/'
def rd(p): return open(p, errors='surrogateescape').read()
def wr(p, t): open(p, 'w', errors='surrogateescape').write(t)
rep=[]
SEP='/*' + '-'*196 + '*/'
# ---------- 1. IR.h -> ir_fwd.h, ir_ops.h, ir_node.h, ir_graph.h, ir_construct.h; the long bodies -> scrip_ir.c
L=rd(W+'ir/IR.h').split('\n')
def lines(a, b): return L[a-1:b]          # 1-based inclusive
def fn_block(name):
    """the static inline function `name` as (first_line, last_line) 1-based by brace matching"""
    for i, l in enumerate(L):
        if re.match(r'static inline .*\b' + re.escape(name) + r'\s*\(', l):
            depth = 0; j = i
            while True:
                depth += L[j].count('{') - L[j].count('}')
                if depth == 0 and '{' in ''.join(L[i:j+1]): return (i+1, j+1)
                j += 1
    raise SystemExit('no inline ' + name)
assert L[23].startswith('typedef enum {') and L[37] == '} IR_e;', (L[23], L[37])
assert L[38].startswith('#define TABLE_HDR_CELLS') and L[39].startswith('typedef enum { CLEANUP_OPEN') and L[40].startswith('typedef enum { SNO_FENCE_LIT_BARE')
assert L[41].startswith('DESCR_SASSERT(IR_OP_COUNT > 0') and L[49].endswith('"dimension and are still homeless.");')
assert L[134].startswith('typedef enum { BINOP_CAT_ARITH'), L[134]
assert L[137].startswith('typedef struct { IR_t * node; char sz[4]; } IR_ref_t;')
assert L[138] == 'struct IR_t {' and L[150] == '};'
assert L[151].startswith('static inline IR_e ir_kind0') and L[152].startswith('#define IR_LIT') and L[165].startswith('#define IR_SEAL_KILL_HOME')
assert L[180].startswith('static inline int ir_range_trailed') and L[181].startswith('static inline int ir_range_operands_must_be_integers')
assert L[184].startswith('static inline int ir_define_sr_citizen') and L[198].startswith('static inline int port_sz_beta') and L[199].startswith('static inline int beta_is_stmt_land')
assert L[200] == '#define ZST_BIAS (1 << 24)'
assert L[221].startswith('typedef enum { IR_CK_GRAPH') and L[222].startswith('typedef struct IR_construct_t {')
assert L[223] == 'struct IR_graph_t {' and L[337] == '};'
assert L[339].startswith('IR_graph_t * IR_alloc') and L[346].startswith('int graph_has_local')
assert L[366].startswith('IR_t * IR_node_alloc') and L[368].startswith('int ir_node_produces_value') and L[369].startswith('void bb_reset') and L[370].startswith('void IR_free') and L[373].startswith('const char * bb_op_name')
MOVED=['ir_is_matcher','ir_is_matcher_element','ir_is_call_kind','ir_decides_own_failure_kind','ir_range_tag_has','ir_range_kind_is','ir_define_ch8_role','ir_floater_kind','ir_floater_member','ir_glue_box','ir_define_bind_entry','ir_define_bind_proto','ir_define_is_bind','ir_graph_has_suspend','ir_call_arg','ir_pair_arg']
bodies={}; protos={}
for n in MOVED:
    a, b = fn_block(n); blk = lines(a, b)
    head = re.sub(r'^static inline ', '', blk[0])
    bodies[n] = [head] + blk[1:]
    sig = head[:head.index('{')].rstrip()
    protos[n] = sig + ';'
    assert sig.endswith(')'), sig
# one-line inline that the instrument would count: ir_is_scan_kind ((void) t; return 0;) and ir_is_call_kind (a one-expression body over two lines)
scan_kind = 'static inline int ir_is_scan_kind(IR_e t) { return 0; }'
WRAP_O=['#ifdef __cplusplus', 'extern "C" {', '#endif']; WRAP_C=['#ifdef __cplusplus', '}', '#endif']
fwd=['#ifndef SCRIP_IR_FWD_H', '#define SCRIP_IR_FWD_H', 'typedef struct IR_t IR_t;', 'typedef struct IR_graph_t IR_graph_t;', 'typedef struct IR_construct_t IR_construct_t;', '#endif', '']
ops=['#ifndef SCRIP_IR_OPS_H', '#define SCRIP_IR_OPS_H', '#include "ir/descr_tags.h"'] + WRAP_O + lines(24, 50) + [L[134]] + [scan_kind, L[124], protos['ir_is_call_kind'], L[129], protos['ir_is_matcher'], protos['ir_is_matcher_element'], protos['ir_decides_own_failure_kind'], L[373]] + WRAP_C + ['#endif', '']
node=['#ifndef SCRIP_IR_NODE_H', '#define SCRIP_IR_NODE_H', '#include <stdint.h>', '#include "ir/ir_fwd.h"', '#include "ir/ir_ops.h"'] + WRAP_O + lines(138, 166) + [protos['ir_range_tag_has'], protos['ir_range_kind_is'], L[180], L[181], protos['ir_define_ch8_role'], L[184], protos['ir_floater_kind'], protos['ir_floater_member'], L[198], L[199], protos['ir_glue_box'], protos['ir_define_bind_entry'], protos['ir_define_bind_proto'], protos['ir_define_is_bind'], protos['ir_call_arg'], protos['ir_pair_arg'], L[366], L[367], L[368]] + WRAP_C + ['#endif', '']
graph=['#ifndef SCRIP_IR_GRAPH_H', '#define SCRIP_IR_GRAPH_H', '#include <stdio.h>', '#include <stdint.h>', '#include "ir/descr.h"', '#include "ir/ir_fwd.h"'] + WRAP_O + lines(224, 338) + [protos['ir_graph_has_suspend'], L[339], L[344], L[345], L[346], L[370], L[371], L[372]] + WRAP_C + ['#endif', '']
cons=['#ifndef SCRIP_IR_CONSTRUCT_H', '#define SCRIP_IR_CONSTRUCT_H', '#include "ir/ir_fwd.h"'] + WRAP_O + [L[221], L[222], L[340], L[341], L[342], L[343]] + WRAP_C + ['#endif', '']
for name, txt in (('ir_fwd.h', fwd), ('ir_ops.h', ops), ('ir_node.h', node), ('ir_graph.h', graph), ('ir_construct.h', cons)):
    wr(W+'ir/'+name, '\n'.join(txt)); rep.append('wrote ir/%s (%d lines)' % (name, len(txt)-1))
os.remove(W+'ir/IR.h'); rep.append('deleted ir/IR.h')
# ZST_BIAS -> planner/frame_layout.h (before its closing wrapper)
p=W+'planner/frame_layout.h'; t=rd(p); k=t.rindex('#ifdef __cplusplus\n}\n#endif'); t=t[:k]+'#define ZST_BIAS (1 << 24)\n'+t[k:]; wr(p, t); rep.append('ZST_BIAS -> planner/frame_layout.h')
# the bodies -> scrip_ir.c (R3); its includes by name
p=W+'ir/scrip_ir.c'; t=rd(p); assert t.startswith('#include "IR.h"\n')
t=t.replace('#include "IR.h"\n', '#include "ir/ir_ops.h"\n#include "ir/ir_node.h"\n#include "ir/ir_graph.h"\n#include "ir/ir_construct.h"\n', 1)
if not t.endswith('\n'): t+='\n'
for n in MOVED: t += SEP + '\n' + '\n'.join(bodies[n]) + '\n'
wr(p, t); rep.append('scrip_ir.c: %d bodies appended' % len(MOVED))
open(S+'/hdr4_moved.txt', 'w').write('\n'.join(MOVED)+'\n')
# ---------- 2. the family identifier table from the new headers (for the retarget)
def idents(path):
    out=set(); text=rd(path)
    for s in text.split('\n'):
        s=s.strip()
        if s.startswith('#define'):
            m=re.match(r'#define\s+(\w+)',s); out.add(m.group(1)) if m else None; continue
        if s.startswith('#') or s.startswith('/*') or not s: continue
        for m in re.finditer(r'typedef\s+struct\s+(\w+)', s): out.add(m.group(1))
        m=re.match(r'typedef\s.*?\b(\w+)\s*;\s*$',s)
        if m: out.add(m.group(1))
        m=re.match(r'^\}\s*(\w+)\s*;',s)
        if m: out.add(m.group(1))
        m=re.match(r'(?:static\s+inline\s+)?[\w\s\*]+?\b(\w+)\s*\(',s)
        if m and not s.startswith('typedef'): out.add(m.group(1))
        m=re.match(r'^struct\s+(\w+)\s*\{',s)
        if m: out.add(m.group(1))
    text2=rd(path)
    for m in re.finditer(r'typedef\s+enum\s*\{([^}]*)\}\s*(\w+)\s*;', text2, re.S):
        out.add(m.group(2))
        for e in m.group(1).split(','):
            e=e.strip().split('=')[0].strip()
            if re.match(r'^\w+$', e): out.add(e)
    return {i for i in out if len(i) > 2 and not i.endswith('_H')}
FAM=collections.OrderedDict()
for h in ('ir/ir_ops.h','ir/ir_node.h','ir/ir_graph.h','ir/ir_construct.h'): FAM[h]=idents(W+h)
FAM['ir/ir_node.h'] -= {'IR_t','IR_graph_t'}; FAM['ir/ir_graph.h'] -= {'IR_t','IR_graph_t'}
FAM['ir/ir_node.h'] |= {'IR_t'}; FAM['ir/ir_graph.h'] |= {'IR_graph_t'}
json.dump({h: sorted(v) for h, v in FAM.items()}, open(S+'/hdr4_fam.json','w'), indent=0)
IRINC=re.compile(r'^#include "(?:\.\./ir/|ir/)?IR\.h"\n', re.M)
WORD=re.compile(r'\b[A-Za-z_]\w*\b')
def strip(text):
    text=re.sub(r'/\*.*?\*/', ' ', text, flags=re.S); text=re.sub(r'//[^\n]*', ' ', text); text=re.sub(r'"(\\.|[^"\\\n])*"', '""', text); return text
def add_includes(path, incs, anchor_rx=IRINC):
    t=rd(path); orig=t
    new=[i for i in incs if ('#include "%s"' % i) not in t]
    m=anchor_rx.search(t)
    block=''.join('#include "%s"\n' % i for i in new)
    if m: t=t[:m.start()]+block+t[m.end():]
    else:
        # after the last #include of the leading include block
        ms=list(re.finditer(r'^#include [<"][^>"]+[>"]\n', t, re.M))
        if ms: k=ms[-1].end(); t=t[:k]+block+t[k:]
        else: t=block+t
    t=IRINC.sub('', t)
    if t!=orig: wr(path, t)
    return t!=orig
n_units=0; retarget=collections.Counter()
for f in glob.glob(W+'**/*.c', recursive=True)+glob.glob(W+'**/*.cpp', recursive=True):
    if f.endswith('ir/scrip_ir.c'): continue
    text=strip(rd(f)); toks=set(WORD.findall(text))
    need=[h for h, ids in FAM.items() if toks & ids]
    if need or IRINC.search(rd(f)):
        if add_includes(f, need): n_units+=1
        for h in need: retarget[h]+=1
rep.append('units retargeted: %d (%s)' % (n_units, ' '.join('%s:%d' % (k.split('/')[-1], v) for k, v in retarget.items())))
# ---------- 3. headers: pointer-only ones forward-declare; the two that name the enum include ir_ops.h; the dereferencing index includes the records
PTR=['planner/zeta_depth.h','optimizer/copy_prop.h','optimizer/const_fold.h','optimizer/proc_collect.h','optimizer/dead_pure.h','optimizer/optimizer.h','optimizer/arith_fold.h','optimizer/dead_goto.h','emitter/emit_regime.h','emitter/emit_state.h','emitter/emit.h','runtime/builtins/gen_runtime.h','planner/frame_layout.h','ir/ir_node_index.h','ir/bb_program.h']
OPS=['ir/call_forms.h','lower/lower_common.h','optimizer/branch_chain.h','optimizer/ir_query.h']
for h in PTR: add_includes(W+h, ['ir/ir_fwd.h']); 
for h in OPS: add_includes(W+h, ['ir/ir_fwd.h','ir/ir_ops.h'])
add_includes(W+'optimizer/ir_index.h', ['ir/ir_node.h','ir/ir_graph.h'])
t=rd(W+'templates/bb/bb_templates.h'); assert '#include "IR.h"\n' in t; wr(W+'templates/bb/bb_templates.h', t.replace('#include "IR.h"\n','',1))
for h in ['emitter/g_emitter.h','lower/g_lower.h','planner/g_planner.h','planner/planner.h','ir/stage2.h','runtime/rt/rt.h','optimizer/gva_collect.h','planner/planner_head.h']:
    add_includes(W+h, ['ir/ir_fwd.h'], anchor_rx=re.compile(r'^#include "(?:\.\./ir/|ir/)?IR\.h"\n', re.M))
rep.append('headers: %d pointer-only -> ir_fwd.h, %d enum-naming -> ir_ops.h, ir_index.h -> node+graph, bb_templates.h drops IR.h, 8 headers that named the records without including add ir_fwd.h' % (len(PTR), len(OPS)))
# ---------- 4. bb_box.h: the live part only; bb_build.h gone; the match registers declared once
p=W+'ir/bb_box.h'; t=rd(p)
keep=['#ifndef BB_BOX_H','#define BB_BOX_H','#include <stddef.h>','#include "ir/descr.h"'] + WRAP_O + ['typedef DESCR_t (*bb_box_fn)(void * zeta, int entry);','typedef struct { bb_box_fn fn; void * ζ; size_t ζ_size; } bb_node_t;','static const int α = 0;','static const int β = 1;','extern const char * Σ;','extern int Δ;','extern int Ω;','extern int Σlen;'] + WRAP_C + ['#endif','']
for must in ('typedef DESCR_t (*bb_box_fn)(void * zeta, int entry);','static const int α = 0;','extern int Σlen;','extern cap_t * bb_cap_new(','int exec_stmt_blob('): assert must in t, must
wr(p, '\n'.join(keep)); rep.append('bb_box.h: 53 -> %d lines (bb_box_fn, bb_node_t, alpha, beta, the four match registers)' % (len(keep)-1))
os.remove(W+'ir/bb_build.h'); rep.append('deleted ir/bb_build.h')
BBINC=re.compile(r'^#include "(?:ir/)?bb_build\.h"\n', re.M)
for f in ['driver/driver_private.h','driver/scrip.c','runtime/core/stmt_exec.c','runtime/rt/rt.c']:
    p=W+f; t=rd(p); assert BBINC.search(t), f
    t=BBINC.sub('#include "ir/bb_box.h"\n' if '#include "ir/bb_box.h"' not in t else '', t); wr(p, t)
p=W+'driver/driver_private.h'; t=rd(p); n0=len(t)
t=re.sub(r'^extern (const char \* ?Σ|int Σlen|int Δ|int Ω);\n', '', t, flags=re.M); wr(p, t); rep.append('driver_private.h: bb_box.h in place of bb_build.h; %d bytes of duplicate register externs out' % (n0-len(t)))
p=W+'runtime/rt/rt.c'; t=rd(p); n=len(re.findall(r'^extern cap_t \*bb_cap_new(_call)?\(.*\n', t, flags=re.M)); assert n==2, n
t=re.sub(r'^extern cap_t \*bb_cap_new(_call)?\(.*\n', '', t, flags=re.M); wr(p, t); rep.append('rt.c: two dead capture externs out')
p=W+'emitter/emit.cpp'; t=rd(p)
for l in ['extern const char * Σ;\n','extern int Σlen;\n']: assert l in t; t=t.replace(l,'',1)
n=len(re.findall(r'^extern (atp_t|cap_t) \* bb_(atp|cap)_new(_call)? \(.*\n', t, flags=re.M)); assert n==3, n
t=re.sub(r'^extern (atp_t|cap_t) \* bb_(atp|cap)_new(_call)? \(.*\n', '', t, flags=re.M); wr(p, t); rep.append('emit.cpp: the register externs and three dead capture externs out (bb_box.h declares the registers)')
p=W+'emitter/emit_regime.h'; t=rd(p); old='extern const char *Σ;\nextern int Σlen;\nextern int Δ;\n'; assert old in t
t=t.replace(old, ''); t=t.replace('#include "emitter/emit_state.h"\n', '#include "emitter/emit_state.h"\n#include "ir/bb_box.h"\n', 1); wr(p, t); rep.append('emit_regime.h: includes ir/bb_box.h for the registers its macros name')
# ---------- 5. stage2.h stops reaching SM.h; bb_program.h forward-declares
p=W+'ir/stage2.h'; t=rd(p); assert '#include "SM.h"\n' in t; t=t.replace('#include "SM.h"\n','',1); wr(p, t); rep.append('stage2.h: SM.h out (it names nothing of it)')
print('\n'.join(rep))
