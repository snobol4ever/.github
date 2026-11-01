import os, re, sys, glob
S='/tmp/claude-1000/-home-claude-cto/25cbd82c-ea4e-46bc-9ee6-3c52fc5dcc1f/scratchpad'
W=S+'/hdr/SCRIP/src/'; HW=S+'/hdr/harness/scripts/'
def rd(p): return open(p, errors='surrogateescape').read()
def wr(p, t): open(p, 'w', errors='surrogateescape').write(t)
rep=[]
# 1. the preamble header goes; its includers include the state header they name
pre=W+'templates/bb/bb_template_common.h'; assert os.path.exists(pre); os.remove(pre); rep.append('deleted templates/bb/bb_template_common.h')
n_rep=n_del=0
for f in glob.glob(W+'**/*.c', recursive=True)+glob.glob(W+'**/*.cpp', recursive=True)+glob.glob(W+'**/*.h', recursive=True):
    t=rd(f)
    if '#include "bb_template_common.h"\n' not in t: continue
    if '#include "emitter/emit_state.h"\n' in t: t=t.replace('#include "bb_template_common.h"\n', ''); n_del+=1
    else: t=t.replace('#include "bb_template_common.h"\n', '#include "emitter/emit_state.h"\n'); n_rep+=1
    wr(f, t)
rep.append('preamble include: %d replaced by emitter/emit_state.h, %d deleted (already direct)' % (n_rep, n_del))
# 2. CSET_CHAIN_MAX to emit_knobs.h (the form-choice threshold of the five cset templates)
p=W+'emitter/emit_knobs.h'; t=rd(p); m=re.search(r'^#define EMITTER_EMIT_KNOBS_H\n', t, re.M); assert m
t=t[:m.end()]+'#define CSET_CHAIN_MAX 3\n'+t[m.end():]; wr(p, t); rep.append('CSET_CHAIN_MAX -> emit_knobs.h')
# 3. emit_shim9 body to bb_define.cpp, its one user (kept a namespace-scope inline template so the instantiation stays the same COMDAT symbol)
p=W+'emitter/emit_str.h'; t=rd(p)
i=t.index('template<typename F> inline std::string emit_shim9('); j=t.index('long emit_lit_d(')
body=t[i:j]; assert body.count('\n')==11 and body.rstrip().endswith('}'), body
t=t[:i]+t[j:]; wr(p, t)
p=W+'templates/bb/bb_define.cpp'; t=rd(p); k=t.index('#include "runtime/rtx/rtcc.h"\n')+len('#include "runtime/rtx/rtcc.h"\n')
assert t.index('emit_shim9(') > k
t=t[:k]+body+t[k:]; wr(p, t); rep.append('emit_shim9 (11 lines) -> bb_define.cpp after its last include')
# 4. emit_heap_fb_adopt: the two externs at file scope, the body one expression
p=W+'emitter/emit_regime.h'; t=rd(p)
old='static inline int emit_heap_fb_adopt(void) { extern int g_gen_proc_active; extern int g_resumable_callable_active; return g_gen_proc_active || g_resumable_callable_active; }\n'
assert old in t
t=t.replace(old, 'extern int g_gen_proc_active;\nextern int g_resumable_callable_active;\nstatic inline int emit_heap_fb_adopt(void) { return g_gen_proc_active || g_resumable_callable_active; }\n'); wr(p, t); rep.append('emit_heap_fb_adopt: externs hoisted, one-expression body')
# 5. the includes the instrument reads unused that this landing wrote (and emit.cpp's own dead ones; the compile is the judge)
def drop(f, lines):
    p=W+f; t=rd(p); d=[]
    for l in lines:
        if l+'\n' in t: t=t.replace(l+'\n', '', 1); d.append(l)
    wr(p, t); rep.append('%s: dropped %s' % (f, ' '.join(x.split('"')[1] for x in d) or 'nothing'))
p=W+'emitter/emit.cpp'; t=rd(p)
if '#include "ir/bb_box.h"\n' in t: t=t.replace('#include "ir/bb_build.h"\n', '')
else: t=t.replace('#include "ir/bb_build.h"\n', '#include "ir/bb_box.h"\n')
wr(p, t)
drop('emitter/emit.cpp', ['#include "driver/scrip_sm.h"', '#include "planner/zeta_depth.h"', '#include "runtime/builtin_ids.h"', '#include "runtime/snobol4_system_fns.h"'])
for f in ['emitter/emit_call_probe.cpp', 'runtime/rt/bb_pat_build.cpp', 'templates/bb/bb_call_fn.cpp', 'templates/bb/bb_call_pl_leaf.cpp', 'templates/bb/bb_call_proc_staged.cpp']:
    drop(f, ['#include "emitter/emit.h"'])
# 6. harness: the class A/B row follows sm_emit_t; the base set follows the headers; the allowance names the function templates
p=HW+'fixtures/dyn_caps/CLASS_AB.tsv'; t=rd(p); old='src/emitter/emit.h\top_df_b\tB\t'; assert t.count(old)==1
lines=t.split('\n')
for i,l in enumerate(lines):
    if l.startswith(old): lines[i]=l.replace(old, 'src/emitter/emit_state.h\top_df_b\tB\t', 1)+' [re-pointed: sm_emit_t moved from emit.h to emit_state.h by headers step 3, cto 2026-10-31]'
wr(p, '\n'.join(lines)); rep.append('CLASS_AB.tsv: op_df_b row re-pointed to emit_state.h')
p=HW+'header_base_set.tsv'; t=rd(p); old='templates/bb/bb_template_common.h\twhat every template reads\n'; assert old in t
t=t.replace(old, ''); assert t.endswith('\n')
t+='emitter/emit_str.h\tthe text-composition forms every template is written in (IF, IF_M3, IF_M4, FOR, emit_for, emit_seq and the emit_str.cpp byte helpers); its fan-in is the template count by construction (headers step 3, the cto, 2026-10-31; the preamble bb_template_common.h it replaces in this set is deleted)\n'
wr(p, t); rep.append('base set: bb_template_common.h row out, emit_str.h row in')
p=HW+'header_inline_allowed.tsv'; t=rd(p); assert t.endswith('\n')
t+='emitter/emit_str.h\tFOR and emit_for are function templates over a lambda type, instantiated at each call site; a template body cannot leave the header (headers step 3, the cto, 2026-10-31)\n'
wr(p, t); rep.append('inline allowance: emit_str.h (FOR, emit_for)')
print('\n'.join(rep))
