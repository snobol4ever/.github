#!/usr/bin/env python3
# hdr4.py -- headers step 4 (ARCH-HEADER-SPLIT 3.3, CEO-2032; the cto 2026-10-31): IR.h -> ir_fwd.h ir_ops.h ir_node.h ir_graph.h ir_construct.h with
# sixteen bodies to scrip_ir.c; bb_box.h its live part, bb_build.h gone; stage2.h without SM.h; planner_head.h deleted, planner.h split by definer;
# every includer rewritten so that the family is first reached WHERE IR.h WAS (order-parent.json: a static inline is emitted in definition order).
import os, re, sys, glob, json, collections
S4='/tmp/claude-1000/-home-claude-cto/b1caac4c-9b75-4393-9260-1c72f906f86b/scratchpad'
SO='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'
ROOT=SO+'/hdr/SCRIP'; W=ROOT+'/src/'
ORDER=json.load(open(S4+'/order-parent.json'))
INCDIRS=['', 'ir/','lower/','emitter/','runtime/core/','runtime/builtins/','runtime/','runtime/rt/','parsers/snobol4/','parsers/raku/','optimizer/','templates/bb/','templates/xa/','templates/x86/']
rep=[]; warn=[]
def rd(p): return open(p, errors='surrogateescape').read()
def wr(p, t): open(p, 'w', errors='surrogateescape').write(t)
SEP='/*' + '-'*196 + '*/'
WORD=re.compile(r'(?<![\w])[^\W\d]\w*')
def strip(text):
    text=re.sub(r'/\*.*?\*/', ' ', text, flags=re.S); text=re.sub(r'//[^\n]*', ' ', text); text=re.sub(r'"(\\.|[^"\\\n])*"', '""', text); return text
def toks(path): return set(WORD.findall(strip(rd(path))))
def resolve(includer_rel, inc):
    cands=[os.path.normpath(os.path.join(os.path.dirname(includer_rel), inc))]+[os.path.normpath(d+inc) for d in INCDIRS]
    for c in cands:
        if os.path.isfile(W+c): return c
    return None
INC_RX=re.compile(r'^#include "([^"]+)"', re.M)
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
        m=re.match(r'(?:extern\s+"C"\s+)?(?:static\s+inline\s+)?[\w\s\*]+?\b(\w+)\s*\(',s)
        if m and not s.startswith('typedef'): out.add(m.group(1))
        m=re.match(r'^struct\s+(\w+)\s*\{',s)
        if m: out.add(m.group(1))
        m=re.match(r'typedef\s.*\(\*(\w+)\)\(',s)
        if m: out.add(m.group(1))
        m=re.match(r'extern\s+.*\b(\w+)\s*(\[|;)',s)
        if m: out.add(m.group(1))
    for m in re.finditer(r'typedef\s+enum\s*\{([^}]*)\}\s*(\w+)\s*;', text, re.S):
        out.add(m.group(2))
        for e in m.group(1).split(','):
            e=e.strip().split('=')[0].strip()
            if re.match(r'^\w+$', e): out.add(e)
    for m in re.finditer(r'^enum\s*\{([^}]*)\}\s*;', text, re.S|re.M):
        for e in m.group(1).split(','):
            e=e.strip().split('=')[0].strip()
            if re.match(r'^\w+$', e): out.add(e)
    return {i for i in out if len(i) > 2 and not i.endswith('_H')}
# ===================================================================== 1. IR.h -> the five families
L=rd(W+'ir/IR.h').split('\n')
def lines(a, b): return L[a-1:b]
def fn_block(name):
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
scan_kind = 'static inline int ir_is_scan_kind(IR_e t) { return 0; }'
WRAP_O=['#ifdef __cplusplus', 'extern "C" {', '#endif']; WRAP_C=['#ifdef __cplusplus', '}', '#endif']
fwd=['#ifndef SCRIP_IR_FWD_H', '#define SCRIP_IR_FWD_H', 'typedef struct IR_t IR_t;', 'typedef struct IR_graph_t IR_graph_t;', 'typedef struct IR_construct_t IR_construct_t;', '#endif', '']
ops=['#ifndef SCRIP_IR_OPS_H', '#define SCRIP_IR_OPS_H', '#include "ir/descr.h"'] + WRAP_O + lines(24, 50) + [L[134]] + [scan_kind, L[124], protos['ir_is_call_kind'], L[129], protos['ir_is_matcher'], protos['ir_is_matcher_element'], protos['ir_decides_own_failure_kind'], L[373]] + WRAP_C + ['#endif', '']
node=['#ifndef SCRIP_IR_NODE_H', '#define SCRIP_IR_NODE_H', '#include <stdint.h>', '#include "ir/ir_fwd.h"', '#include "ir/ir_ops.h"'] + WRAP_O + lines(138, 166) + [protos['ir_range_tag_has'], protos['ir_range_kind_is'], L[180], L[181], protos['ir_define_ch8_role'], L[184], protos['ir_floater_kind'], protos['ir_floater_member'], L[198], L[199], protos['ir_glue_box'], protos['ir_define_bind_entry'], protos['ir_define_bind_proto'], protos['ir_define_is_bind'], protos['ir_call_arg'], protos['ir_pair_arg'], L[366], L[367], L[368]] + WRAP_C + ['#endif', '']
graph=['#ifndef SCRIP_IR_GRAPH_H', '#define SCRIP_IR_GRAPH_H', '#include <stdio.h>', '#include <stdint.h>', '#include "ir/descr.h"', '#include "ir/ir_fwd.h"'] + WRAP_O + lines(224, 338) + [protos['ir_graph_has_suspend'], L[339], L[344], L[345], L[346], L[370], L[371], L[372]] + WRAP_C + ['#endif', '']
cons=['#ifndef SCRIP_IR_CONSTRUCT_H', '#define SCRIP_IR_CONSTRUCT_H', '#include "ir/ir_fwd.h"'] + WRAP_O + [L[221], L[222], L[340], L[341], L[342], L[343]] + WRAP_C + ['#endif', '']
for name, txt in (('ir_fwd.h', fwd), ('ir_ops.h', ops), ('ir_node.h', node), ('ir_graph.h', graph), ('ir_construct.h', cons)):
    wr(W+'ir/'+name, '\n'.join(txt)); rep.append('wrote ir/%s (%d lines)' % (name, len(txt)-1))
os.remove(W+'ir/IR.h'); rep.append('deleted ir/IR.h')
p=W+'planner/frame_layout.h'; t=rd(p); k=t.rindex('#ifdef __cplusplus\n}\n#endif'); t=t[:k]+'#define ZST_BIAS (1 << 24)\n'+t[k:]; wr(p, t); rep.append('ZST_BIAS -> planner/frame_layout.h')
p=W+'ir/scrip_ir.c'; t=rd(p); assert t.startswith('#include "IR.h"\n')
t=t.replace('#include "IR.h"\n', '#include "ir/ir_ops.h"\n#include "ir/ir_node.h"\n#include "ir/ir_graph.h"\n#include "ir/ir_construct.h"\n', 1)
if not t.endswith('\n'): t+='\n'
for n in MOVED: t += SEP + '\n' + '\n'.join(bodies[n]) + '\n'
wr(p, t); rep.append('scrip_ir.c: %d bodies appended' % len(MOVED))
open(S4+'/hdr4_moved.txt', 'w').write('\n'.join(MOVED)+'\n')
FAMS=['ir/ir_ops.h','ir/ir_node.h','ir/ir_graph.h','ir/ir_construct.h']
FAM=collections.OrderedDict((h, idents(W+h)) for h in FAMS)
FAM['ir/ir_node.h'] -= {'IR_t','IR_graph_t'}; FAM['ir/ir_graph.h'] -= {'IR_t','IR_graph_t'}; FAM['ir/ir_construct.h'] -= {'IR_t','IR_graph_t'}
FAM['ir/ir_node.h'] |= {'IR_t'}; FAM['ir/ir_graph.h'] |= {'IR_graph_t'}; FAM['ir/ir_ops.h'] -= {'DESCR_SASSERT'}
NODE_FIELDS={'op0','operands','n_operands','pat_static','elem_access','sval','ival','dval','seal','γ','ω'}
GRAPH_FIELDS=set(WORD.findall(' '.join(lines(225, 337)))) - set(WORD.findall(' '.join(lines(300, 336)))) - {'int','char','const','struct','uint64_t','unsigned','IR_t','IR_construct_t','DESCR_t','AG_RING','define','n','max','name','off','serial','ring','pf'}
json.dump({h: sorted(v) for h, v in FAM.items()}, open(S4+'/hdr4_fam.json','w'), indent=0)
def need_unit(text):
    tk=set(WORD.findall(strip(text))); return [h for h in FAMS if tk & FAM[h]]
DEREF=re.compile(r'->\s*(%s)\b')
def own_header(text):
    tk=set(WORD.findall(strip(text))); out=[]
    if tk & (FAM['ir/ir_ops.h']): out.append('ir/ir_ops.h')
    if (tk & (FAM['ir/ir_node.h'] - {'IR_t'})) or re.search(r'->\s*(' + '|'.join(NODE_FIELDS) + r')\b', text): out.append('ir/ir_node.h')
    if (tk & (FAM['ir/ir_graph.h'] - {'IR_graph_t'})) or re.search(r'->\s*(' + '|'.join(sorted(GRAPH_FIELDS)) + r')\b', text): out.append('ir/ir_graph.h')
    if tk & (FAM['ir/ir_construct.h'] - {'IR_construct_t'}): out.append('ir/ir_construct.h')
    fwd = bool(tk & {'IR_t','IR_graph_t','IR_construct_t'})
    return out, fwd
IRINC=re.compile(r'^#include "(?:\.\./ir/|ir/)?IR\.h"\n', re.M)
def inc_lines(fams, fwd):
    ls=[]
    if fwd and not any(f in fams for f in ('ir/ir_node.h','ir/ir_graph.h','ir/ir_construct.h')): ls.append('#include "ir/ir_fwd.h"')
    ls += ['#include "%s"' % f for f in FAMS if f in fams]
    return ls
# ===================================================================== 2. the planner: planner_head.h deleted, planner.h split by definer
PH=rd(W+'planner/planner.h').split('\n'); P=lambda a,b=None: PH[a-1:(b or a)]
assert PH[0]=='#include <vector>' and PH[2].startswith('struct zrd_t') and PH[22].startswith('enum { ZW_NONE') and PH[23]=='struct zeta_plan_t {' and PH[95].startswith('enum { ZETA_NONE')
assert PH[96].startswith('const char * zeta_name') and PH[109].startswith('void planner_facts') and PH[112].startswith('void planner_blob_facts') and PH[113].startswith('void planner_dump_homes') and PH[117].startswith('void planner_pass_plan')
assert PH[171]=='enum {' and PH[172].strip().startswith('PR_SUSPEND') and PH[175]=='extern "C" {' and PH[180]=='}' and PH[181]=='#include "frame_layout.h"'
assert PH[184]=='enum {' and PH[188].startswith('enum { ACT_CLASS_NONE') and PH[189].startswith('extern "C" int planner_act_cause(') and PH[206].startswith('extern "C" int planner_env_encloses') and PH[210].startswith('int planner_retains_emitter_view')
assert PH[228].startswith('static inline int planner_resumable_frame') and PH[229].startswith('void planner_road_none') and PH[243].startswith('int is_global') and PH[244].startswith('int fc_geom') and PH[250].startswith('void planner_stage_release') and len(PH) in (251,252)
PROTO_DEF={}
for l in open('/home/claude_cto/.github/scripts/headers/step4/planner_h_protos.tsv'):
    ln, nm, df = l.rstrip('\n').split('\t'); PROTO_DEF[int(ln)] = (nm, df)
def protos_of(definer, lo, hi): return [PH[k-1] for k in range(lo, hi+1) if k in PROTO_DEF and PROTO_DEF[k][1]==definer]
ZP=['#ifndef SCRIP_ZETA_PLAN_H','#define SCRIP_ZETA_PLAN_H','#ifndef __cplusplus','#error zeta_plan.h is C++ only (the plan record holds std::vector columns)','#endif', PH[0], PH[1], '#include <stdint.h>', '#include "ir/ir_fwd.h"', '#include "ir/stage2.h"'] + P(3,96) + P(172,175)
ZP += protos_of('planner/zeta_plan.cpp', 107, 171) + ['#include "planner/frame_layout.h"'] + protos_of('planner/zeta_plan.cpp', 183, 184) + [PH[206]] + P(211,228) + [PH[228]] + ['#endif','']
assert PH[205].startswith('extern "C" int planner_fence_k') and PH[206].startswith('extern "C" int planner_env_encloses')
AW=['#ifndef SCRIP_ACT_WORDS_H','#define SCRIP_ACT_WORDS_H','#include "planner/zeta_plan.h"'] + P(185,189) + protos_of('planner/act_words.cpp', 97, 106) + protos_of('planner/act_words.cpp', 190, 210) + ['#endif','']
AW=[l.replace(', ACT_CLASS_LEAF = 4', '') for l in AW]
assert any('ACT_CLASS_FENCE = 3, ACT_CLASS_CHOICE = 5' in l for l in AW)
PF=['#ifndef SCRIP_PLAN_FACTS_H','#define SCRIP_PLAN_FACTS_H','#ifndef __cplusplus','#error plan_facts.h is C++ only (it names the plan record)','#endif','#include "ir/ir_fwd.h"','struct zeta_plan_t;'] + [PH[109], PH[112]] + ['#endif','']
PL=['#ifndef SCRIP_PLANNER_H','#define SCRIP_PLANNER_H','#include "ir/ir_fwd.h"','#include "ir/stage2.h"'] + P(114,117) + P(230,243) + P(246,251) + ['#endif','']
assert all(PROTO_DEF[k][1] in ('planner/planner_report.cpp','planner/planner_road.cpp','planner/planner_stage_chains.cpp','planner/planner_operands.cpp','planner/planner_stage.c') for k in list(range(114,118))+list(range(230,244))+list(range(246,252)) if k in PROTO_DEF), 'stage interface definers'
for name, txt in (('zeta_plan.h', ZP), ('act_words.h', AW), ('plan_facts.h', PF), ('planner.h', PL)):
    wr(W+'planner/'+name, '\n'.join(txt)); rep.append('wrote planner/%s (%d lines)' % (name, len(txt)-1))
p=W+'planner/frame_layout.h'; t=rd(p); k=t.rindex('#ifdef __cplusplus\n}\n#endif'); t=t[:k]+'\n'.join(P(177,180)+[PH[244]])+'\n'+t[k:]; wr(p, t); rep.append('frame_layout.h: zls_fcn_hret/hunres/bs_get/bs_set and fc_geom (frame_layout.c is their definer)')
p=W+'lower/lower_common.h'; t=rd(p); k=t.rindex('#endif'); t=t[:k]+PH[243]+'\n'+t[k:]; wr(p, t); rep.append('lower_common.h: is_global (lower_common.c is its definer)')
p=W+'planner/g_planner.h'; t=rd(p)
old='\n'.join(['#include <unordered_map>','#include "ct_arena.h"','#include "ct_vec.h"','#include <string>','#include "gc_frame_map.h"','#include "dtp.h"','#include "ir_index.h"','#include <unordered_set>','#include <vector>','#include <algorithm>','#include "stage2.h"','#include <string.h>','#include <stdlib.h>','#include <assert.h>'])+'\n'
assert old in t; t=t.replace(old, '\n'.join(['#include <unordered_map>','#include <string>','#include <vector>','#include <stdint.h>','#include "ir/ct_vec.h"','#include "ir/ir_fwd.h"'])+'\n'); wr(p, t); rep.append('g_planner.h: six includes it names (was fourteen)')
HEAD_STD=['#include <unordered_map>','#include <unordered_set>','#include <vector>','#include <string>','#include <climits>','#include <algorithm>','#include <string.h>','#include <stdlib.h>','#include <stdio.h>','#include <stdint.h>','#include <assert.h>','#include <math.h>']
HEAD_C=[('ir/ct_arena.h','ct_arena.h'),('ir/ct_vec.h','ct_vec.h'),('IRFAM',None),('ir/stage2.h','stage2.h'),('ir/gc_frame_map.h','gc_frame_map.h'),('ir/dtp.h','dtp.h'),('optimizer/ir_index.h','ir_index.h'),('ir/ir_node_index.h','ir_node_index.h'),('optimizer/ir_query.h','ir_query.h'),('ir/call_forms.h','call_forms.h'),('planner/zeta_depth.h','zeta_depth.h')]
HID={h: idents(W+h) for h,_ in HEAD_C if h!='IRFAM'}
ZP_IDS=idents(W+'planner/zeta_plan.h'); AW_IDS=idents(W+'planner/act_words.h')-ZP_IDS; PF_IDS={'planner_facts','planner_blob_facts'}; PL_IDS=idents(W+'planner/planner.h')-ZP_IDS-AW_IDS; FL_IDS=idents(W+'planner/frame_layout.h')
for u in ['act_words','plan_facts','planner_operands','planner_report','planner_road','planner_stage_chains','zeta_plan']:
    p=W+'planner/'+u+'.cpp'; t=rd(p); tk=set(WORD.findall(strip(t))); need=need_unit(t)
    blk=list(HEAD_STD)+['extern "C" {']
    for h,_ in HEAD_C:
        if h=='IRFAM': blk += inc_lines(need, True)
        elif tk & HID[h]: blk.append('#include "%s"' % h)
    blk += ['}', 'extern "C" {', '#include "planner/g_planner.h"']
    assert '#include "planner_head.h"\n' in t and '#include "planner.h"\n' in t, u
    t=t.replace('#include "planner_head.h"\n', '\n'.join(blk)+'\n', 1)
    fam=[]
    if tk & ZP_IDS: fam.append('#include "planner/zeta_plan.h"')
    if tk & FL_IDS and not fam: fam.append('#include "planner/frame_layout.h"')
    if tk & AW_IDS: fam.append('#include "planner/act_words.h"')
    if tk & PF_IDS: fam.append('#include "planner/plan_facts.h"')
    if tk & PL_IDS: fam.append('#include "planner/planner.h"')
    if 'is_global' in tk: fam.append('#include "lower/lower_common.h"')
    t=t.replace('#include "planner.h"\n', '\n'.join(fam)+'\n', 1); wr(p, t)
    rep.append('%s.cpp: head of %d includes (%s); planner family %s' % (u, len(blk)-4, ' '.join(h.split('/')[-1] for h,_ in HEAD_C if h!='IRFAM' and tk & HID[h]), ' '.join(f.split('/')[-1].rstrip('"') for f in fam)))
os.remove(W+'planner/planner_head.h'); rep.append('deleted planner/planner_head.h')
p=W+'emitter/emit.cpp'; t=rd(p); tk=set(WORD.findall(strip(t))); assert '#include "../planner/planner.h"\n' in t
fam=['#include "planner/zeta_plan.h"'] + (['#include "planner/act_words.h"'] if tk & AW_IDS else []) + (['#include "planner/planner.h"'] if tk & PL_IDS else []) + (['#include "lower/lower_common.h"'] if 'is_global' in tk else [])
t=t.replace('#include "../planner/planner.h"\n', '\n'.join(fam)+'\n', 1); wr(p, t); rep.append('emit.cpp: planner.h -> %s' % ' '.join(f.split('/')[-1].rstrip('"') for f in fam))
# ===================================================================== 3. bb_box.h live part, bb_build.h gone, stage2.h without SM.h, bb_program.h
p=W+'ir/bb_box.h'; t=rd(p)
for must in ('typedef DESCR_t (*bb_box_fn)(void * zeta, int entry);','static const int α = 0;','extern int Σlen;','extern cap_t * bb_cap_new(','int exec_stmt_blob('): assert must in t, must
keep=['#ifndef BB_BOX_H','#define BB_BOX_H','#include <stddef.h>','#include "ir/descr.h"'] + WRAP_O + ['typedef DESCR_t (*bb_box_fn)(void * zeta, int entry);','typedef struct { bb_box_fn fn; void * ζ; size_t ζ_size; } bb_node_t;','static const int α = 0;','static const int β = 1;','extern const char * Σ;','extern int Δ;','extern int Ω;','extern int Σlen;'] + WRAP_C + ['#endif','']
wr(p, '\n'.join(keep)); rep.append('bb_box.h: 53 -> %d lines (bb_box_fn, bb_node_t, alpha, beta, the four match registers stmt_exec.c defines)' % (len(keep)-1))
os.remove(W+'ir/bb_build.h'); rep.append('deleted ir/bb_build.h')
BBINC=re.compile(r'^#include "(?:ir/)?bb_build\.h"\n', re.M); BOX_IDS=idents(W+'ir/bb_box.h')|{'α','β','Σ','Δ','Ω','Σlen'}
for f in ['driver/driver_private.h','driver/scrip.c','emitter/emit.cpp','runtime/core/stmt_exec.c','runtime/rt/rt.c']:
    p=W+f; t=rd(p); assert BBINC.search(t), f; tk=set(WORD.findall(strip(t)))
    t=BBINC.sub('#include "ir/bb_box.h"\n' if ('#include "ir/bb_box.h"' not in t and (tk & BOX_IDS)) else '', t); wr(p, t)
p=W+'driver/driver_private.h'; t=rd(p); n0=len(t)
t=re.sub(r'^extern (const char \* ?Σ|int Σlen|int Δ|int Ω);\n', '', t, flags=re.M); wr(p, t); rep.append('driver_private.h: bb_box.h in place of bb_build.h; %d bytes of duplicate register externs out' % (n0-len(t)))
p=W+'runtime/rt/rt.c'; t=rd(p); n=len(re.findall(r'^extern cap_t \*bb_cap_new(_call)?\(.*\n', t, flags=re.M)); assert n==2, n
t=re.sub(r'^extern cap_t \*bb_cap_new(_call)?\(.*\n', '', t, flags=re.M); wr(p, t); rep.append('rt.c: two dead capture externs out')
p=W+'emitter/emit.cpp'; t=rd(p)
for l in ['extern const char * Σ;\n','extern int Σlen;\n']: assert l in t; t=t.replace(l,'',1)
n=len(re.findall(r'^extern (atp_t|cap_t) \* bb_(atp|cap)_new(_call)? \(.*\n', t, flags=re.M)); assert n==3, n
t=re.sub(r'^extern (atp_t|cap_t) \* bb_(atp|cap)_new(_call)? \(.*\n', '', t, flags=re.M); wr(p, t); rep.append('emit.cpp: the register externs and three dead capture externs out')
p=W+'emitter/emit_regime.h'; t=rd(p); old='extern const char *Σ;\nextern int Σlen;\nextern int Δ;\n'; assert old in t
t=t.replace(old, ''); t=t.replace('#include "emitter/emit_state.h"\n', '#include "emitter/emit_state.h"\n#include "ir/bb_box.h"\n', 1); wr(p, t); rep.append('emit_regime.h: includes ir/bb_box.h for the registers its macros name')
p=W+'ir/stage2.h'; t=rd(p); assert '#include "SM.h"\n' in t; t=t.replace('#include "SM.h"\n','',1); wr(p, t); rep.append('stage2.h: SM.h out (it names nothing of it)')
# ===================================================================== 4. the carriers: every header that included IR.h
HDRS=sorted(h for h in (f[len(W):] for f in glob.glob(W+'**/*.h', recursive=True)) if IRINC.search(rd(W+h)))
reach=collections.defaultdict(set)
for u, seq in ORDER.items():
    for d, h in seq: reach[h].add(u)
UNEED={}
for u in ORDER:
    p=os.path.join(ROOT, u)
    if os.path.isfile(p): UNEED[u]=set(need_unit(rd(p)))
carry={}
for h in HDRS:
    t=rd(W+h); own, fwd = own_header(t)
    allneed=set.intersection(*[UNEED.get(u,set()) for u in reach[h]]) if reach[h] else set()
    carry[h]=(set(own)|allneed, fwd)
def apply_carry(h):
    t=rd(W+h); fams, fwd = carry[h]; ls=inc_lines(fams, fwd)
    m=IRINC.search(t); assert m, h
    t=t[:m.start()]+''.join(l+'\n' for l in ls)+t[m.end():]; t=IRINC.sub('', t); wr(W+h, t)
for h in HDRS: apply_carry(h)
rep.append('carriers (%d): ' % len(HDRS) + '; '.join('%s=%s%s' % (h.split('/')[-1], ','.join(f.split('/')[-1][3:-2] for f in FAMS if f in carry[h][0]) or '-', '+fwd' if carry[h][1] else '') for h in HDRS))
for h in ['emitter/g_emitter.h','lower/g_lower.h','ir/stage2.h','runtime/rt/rt.h','optimizer/gva_collect.h']:
    t=rd(W+h)
    if '#include "ir/ir_fwd.h"' in t or 'IR_t' not in t and 'IR_graph_t' not in t: continue
    ms=list(re.finditer(r'^#include [<"][^>"]+[>"]\n', t, re.M)); k=ms[-1].end() if ms else 0
    t=t[:k]+'#include "ir/ir_fwd.h"\n'+t[k:]; wr(W+h, t); rep.append('%s: ir/ir_fwd.h (named the records without including)' % h)
# transitive family reach of a header in the NEW tree
_memo={}
def brings(h):
    if h in _memo: return _memo[h]
    seen=set(); todo=[h]; out=set()
    while todo:
        x=todo.pop()
        if x in seen or not os.path.isfile(W+x): continue
        seen.add(x)
        if x in FAMS: out.add(x)
        for inc in INC_RX.findall(rd(W+x)):
            r=resolve(x, inc)
            if r and r not in seen: todo.append(r)
    _memo[h]=out; return out
# ===================================================================== 5. the units: the family first reached where IR.h was
INL={}
for f in glob.glob(W+'**/*.h', recursive=True):
    names=set(re.findall(r'static\s+inline\s+[\w\s\*]+?\b(\w+)\s*\(', rd(f)))
    if names: INL[f[len(W):]]=names
PARENT_INL=dict(INL); PARENT_INL['ir/IR.h']={'ir_is_matcher','ir_is_matcher_element','ir_is_scan_kind','ir_is_call_road_kind','ir_is_call_kind','ir_norm_call_kind','ir_decides_own_failure_kind','ir_kind0','ir_range_tag_has','ir_range_kind_is','ir_range_trailed','ir_range_operands_must_be_integers','ir_define_ch8_role','ir_define_sr_citizen','ir_floater_kind','ir_floater_member','port_sz_beta','beta_is_stmt_land','ir_glue_box','ir_define_bind_entry','ir_define_bind_proto','ir_define_is_bind','ir_graph_has_suspend','ir_call_arg','ir_pair_arg','ag_ring_push','ag_ring_peek','ag_ring_clear'}
PARENT_INL['ir/bb_box.h']={'descr_match_span','descr_match','descr_match_cat','descr_bool','bb_enter'}; PARENT_INL['planner/planner.h']={'planner_resumable_frame'}
def matters(h, tk): return bool(PARENT_INL.get(h, set()) & tk)
PLANNER7={'src/planner/%s.cpp' % x for x in ['act_words','plan_facts','planner_operands','planner_report','planner_road','planner_stage_chains','zeta_plan']}
decisions=[]; forced=collections.defaultdict(set)
units=[u for u in ORDER if re.search(r'\.(c|cpp)$', u) and os.path.isfile(os.path.join(ROOT,u)) and u != 'src/ir/scrip_ir.c' and u not in PLANNER7]
def unit_plan(u):
    p=os.path.join(ROOT,u); t=rd(p); need=UNEED[u]; seq=ORDER[u]; tk=set(WORD.findall(strip(t)))
    already={f for f in FAMS if ('#include "%s"' % f) in t}
    i=next((k for k,(d,h) in enumerate(seq) if h=='ir/IR.h'), None)
    if i is None: return ('none', None, need-already) if need-already else None
    if seq[i][0]==1: return ('direct', None, need-already)
    j=i
    while seq[j][0]!=1: j-=1
    h1=seq[j][1]; miss=need-already-brings(h1)
    if not miss: return ('carried', h1, set())
    end=next((k for k in range(j+1, len(seq)) if seq[k][0]==1), len(seq))
    first={}
    for k,(d,h) in enumerate(seq): first.setdefault(h,k)
    Pset={h for k,(d,h) in enumerate(seq[j+1:i], j+1) if first[h]==k and matters(h, tk)}
    i_end=next((k for k in range(i+1, len(seq)) if seq[k][0] <= seq[i][0]), len(seq))
    Qset={h for k,(d,h) in enumerate(seq[i_end:end], i_end) if first[h]==k and matters(h, tk)}
    if not Pset: return ('before', h1, miss)
    if not Qset: return ('after', h1, miss)
    return ('force', h1, miss)
plans={}
for u in units:
    r=unit_plan(u)
    if r: plans[u]=r
for u,(kind,h1,miss) in plans.items():
    if kind=='force': forced[h1] |= miss
for h in forced:
    fams, fwd = carry[h]; carry[h]=(fams|forced[h], fwd); t=rd(W+h)
    m=re.search(r'^#include "ir/ir_(fwd|ops|node|graph|construct)\.h"\n', t, re.M); assert m, h
    first_end=m.end(); have={f for f in FAMS if '#include "%s"' % f in t}
    add=''.join('#include "%s"\n' % f for f in FAMS if f in forced[h] and f not in have)
    t=t[:first_end]+add+t[first_end:]; t=re.sub(r'^#include "ir/ir_fwd\.h"\n', '', t, flags=re.M) if any(f in carry[h][0] for f in FAMS[1:]) else t; wr(W+h, t)
    rep.append('carrier forced by order: %s += %s' % (h, ','.join(f.split('/')[-1] for f in forced[h])))
_memo.clear()
cnt=collections.Counter(); touched=0
def find_inc_line(t, h1, u):
    for m in re.finditer(r'^#include "([^"]+)"\n', t, re.M):
        if resolve(u[4:], m.group(1))==h1: return m
    return None
for u in units:
    r=unit_plan(u)
    if not r: continue
    kind,h1,miss=r; p=os.path.join(ROOT,u); t=rd(p); need=UNEED[u]; ls=''.join(l+'\n' for l in inc_lines(need, False))
    own=IRINC.search(t)
    if kind in ('direct',):
        assert own, u; t=t[:own.start()]+ls+t[own.end():]; t=IRINC.sub('', t)
    elif kind in ('before','after'):
        m=find_inc_line(t, h1, u)
        if not m: warn.append('%s: cannot find the include line of %s' % (u, h1)); kind='none'
        else:
            add=''.join('#include "%s"\n' % f for f in FAMS if f in miss)
            t = t[:m.start()]+add+t[m.start():] if kind=='before' else t[:m.end()]+add+t[m.end():]
            if own: t=IRINC.sub(ls if own.start() > m.start() else '', t, count=1); t=IRINC.sub('', t)
    if kind=='carried' and own: t=IRINC.sub(ls, t, count=1); t=IRINC.sub('', t)
    if kind=='none':
        if own: t=IRINC.sub(ls, t, count=1); t=IRINC.sub('', t)
        elif miss:
            ms=list(re.finditer(r'^#include [<"][^>"]+[>"]\n', t, re.M)); k=ms[-1].end() if ms else 0
            t=t[:k]+''.join('#include "%s"\n' % f for f in FAMS if f in miss)+t[k:]; warn.append('%s: no first-reach record, family appended after the last include' % u)
    cnt[kind]+=1
    if t!=rd(p): wr(p, t); touched+=1
# units never compiled in ORDER (tools, tests) that include IR.h by text
for f in glob.glob(W+'**/*.c', recursive=True)+glob.glob(W+'**/*.cpp', recursive=True):
    rel='src/'+f[len(W):]
    if rel in plans or rel in ORDER or not IRINC.search(rd(f)): continue
    t=rd(f); ls=''.join(l+'\n' for l in inc_lines(need_unit(t), True)); t=IRINC.sub(ls, t, count=1); t=IRINC.sub('', t); wr(f, t); cnt['uncompiled']+=1
rep.append('units: %d touched; placements %s' % (touched, dict(cnt)))
left=[f[len(W):] for f in glob.glob(W+'**/*', recursive=True) if os.path.isfile(f) and re.search(r'\.(c|cpp|h|inc)$', f) and IRINC.search(rd(f))]
rep.append('IR.h includes left: %s' % (left or 'none'))
json.dump({u: [k, h, sorted(m)] for u,(k,h,m) in plans.items()}, open(S4+'/hdr4_plans.json','w'), indent=0)
print('\n'.join(rep)); print('WARN:' if warn else 'no warnings'); print('\n'.join(warn))
