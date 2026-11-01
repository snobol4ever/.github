import os, re, sys, subprocess, collections
root=sys.argv[1]; log=sys.argv[2]; src=os.path.join(root,'src')
HDRS=['ir/ir_fwd.h','ir/ir_ops.h','ir/ir_node.h','ir/ir_graph.h','ir/ir_construct.h','ir/bb_box.h','ir/bb_program.h','ir/stage2.h','ir/SM.h','ir/call_forms.h','ir/ct_vec.h','ir/ct_arena.h','ir/gc_frame_map.h','ir/dtp.h','ir/ir_node_index.h','optimizer/ir_index.h','optimizer/ir_query.h','planner/zeta_depth.h','planner/frame_layout.h','planner/g_planner.h','emitter/emit_state.h','emitter/emit_regime.h','runtime/keywords.h','lower/lower_common.h','lower/g_lower.h','driver/driver_private.h']
def idents(path):
    out=set(); text=open(os.path.join(src,path),errors='replace').read()
    for s in text.split('\n'):
        s=s.strip()
        if s.startswith('#define'):
            m=re.match(r'#define\s+(\w+)',s); out.add(m.group(1)) if m else None; continue
        if s.startswith('#') or s.startswith('/*') or not s: continue
        m=re.match(r'typedef\s.*?\b(\w+)\s*;\s*$',s)
        if m: out.add(m.group(1))
        m=re.match(r'typedef\s+struct\s+(\w+)',s)
        if m: out.add(m.group(1)); 
        m=re.match(r'^\}\s*(\w+)\s*;',s)
        if m: out.add(m.group(1))
        m=re.match(r'typedef\s.*\(\*(\w+)\)\(',s)
        if m: out.add(m.group(1))
        m=re.match(r'typedef\s+enum\s*\{(.*)\}\s*(\w+)\s*;',s)
        if m:
            out.add(m.group(2))
            for e in m.group(1).split(','):
                e=e.strip().split('=')[0].strip()
                if e: out.add(e)
        m=re.match(r'(?:static\s+inline\s+)?(?:__attribute__\(\(.*?\)\)\s*)*[\w\s\*]+?\b(\w+)\s*\(',s)
        if m and not s.startswith('typedef'): out.add(m.group(1))
        m=re.match(r'extern\s+.*\b(\w+)\s*(\[|;)',s)
        if m: out.add(m.group(1))
        m=re.match(r'struct\s+(\w+)\s*;',s)
        if m: out.add(m.group(1))
    return out
table={}
for h in HDRS:
    for i in idents(h): table.setdefault(i,h)
# multi-line enums/structs: tags and typedef names on their own lines
for h in HDRS:
    text=open(os.path.join(src,h)).read()
    for m in re.finditer(r'typedef\s+struct\s+(\w+)\s*\{',text): table.setdefault(m.group(1),h)
    for m in re.finditer(r'^\}\s*(\w+)\s*;',text,re.M): table.setdefault(m.group(1),h)
    for m in re.finditer(r'typedef\s+enum\s*\{([^}]*)\}\s*(\w+)\s*;',text,re.S):
        table.setdefault(m.group(2),h)
        for e in m.group(1).split(','):
            e=e.strip().split('=')[0].strip()
            if re.match(r'^\w+$',e): table.setdefault(e,h)
table['_']='emitter/emit_state.h'; table['IR_t']='ir/ir_node.h'; table['IR_graph_t']='ir/ir_graph.h'; table['IR_construct_t']='ir/ir_construct.h'; table['FILE']='<stdio.h>'; table['size_t']='<stddef.h>'
for w in ('strlen','memcpy','memset','memcmp','strcmp','strncmp','strchr','strrchr','strstr','strcpy','strncpy','strdup','strcat'): table[w]='<string.h>'
for w in ('snprintf','fprintf','printf','sprintf','fputs','fputc','fwrite','fflush','stderr','stdout','fopen','fclose','vsnprintf','sscanf','puts'): table[w]='<stdio.h>'
for w in ('getenv','abort','exit','strtol','strtoll','strtoul','atoi','atol','qsort','bsearch','llabs','labs'): table[w]='<stdlib.h>'
for w in ('uint8_t','uint32_t','uint64_t','int32_t','int64_t','uintptr_t','intptr_t','UINT32_MAX','INT64_MAX'): table[w]='<stdint.h>'
for w in ('isalpha','isdigit','isalnum','isspace','isupper','islower','toupper','tolower'): table[w]='<ctype.h>'
for w in ('INT_MAX','INT_MIN','LONG_MAX','LONG_MIN','CHAR_BIT'): table[w]='<limits.h>'
table['string']='<string>'; table['vector']='<vector>'; table['initializer_list']='<initializer_list>'
pat=re.compile(r"^(?P<file>[^:\s]+\.(?:c|cpp|h|inc|cc)):(?P<line>\d+):\d+: (?:fatal )?error: (?P<msg>.*)$")
want=collections.OrderedDict(); unmapped=collections.Counter()
for line in open(log,errors='replace'):
    m=pat.match(line.rstrip('\n'))
    if not m: continue
    msg=m.group('msg'); f=m.group('file')
    idm=re.search(r"[‘'](?:struct |union |enum )?(\w+)[’']",msg)
    if not idm: continue
    ident=idm.group(1)
    if not re.search(r'unknown type name|implicit declaration|undeclared|was not declared|does not name a type|has not been declared|incomplete type|undefined type',msg): continue
    h=table.get(ident)
    if ident=='IR_t' and 'incomplete' in msg: h='ir/ir_node.h'
    if ident=='IR_graph_t' and 'incomplete' in msg: h='ir/ir_graph.h'
    if ident=='IR_construct_t' and 'incomplete' in msg: h='ir/ir_construct.h'
    if h is None:
        unmapped[(ident,os.path.basename(f))]+=1; continue
    fp=os.path.normpath(os.path.join(root,f)) if not os.path.isabs(f) else f
    if not fp.startswith(src): continue
    want.setdefault(fp,set()).add(h)
FAM=[h for h in HDRS if h.startswith('ir/ir_') or h in ('ir/bb_box.h','ir/stage2.h','ir/bb_program.h','ir/SM.h')]
famtab={i:h for i,h in table.items() if h in FAM and len(i)>2}
failing=set()
for line in open(log,errors='replace'):
    m=pat.match(line.rstrip('\n'))
    if m:
        f=m.group('file'); fp=os.path.normpath(os.path.join(root,f)) if not os.path.isabs(f) else f
        if fp.startswith(src): failing.add(fp)
for fp in failing:
    t_=open(fp,errors='surrogateescape').read(); rel=os.path.relpath(fp,src)
    for i,h in famtab.items():
        if rel==h: continue
        if re.search(r'\b'+re.escape(i)+r'\b',t_): want.setdefault(fp,set()).add(h)
added=0; skipped=[]
for fp,hs in want.items():
    if fp.endswith(('.h','.inc','.hpp')): skipped.append(fp); continue
    rel=os.path.relpath(fp,src); t=open(fp,errors='surrogateescape').read(); L=t.split('\n')
    for h in sorted(hs):
        inc='#include <%s>'%h.strip('<>') if h.startswith('<') else '#include "%s"'%h
        if rel==h or inc in t: continue
        if rel.endswith('.h') and h in HDRS and rel in HDRS and HDRS.index(h)>=0 and h.endswith('core.h') : pass
        # insertion point: after the last #include of the leading include block (skipping the guard and comment lines)
        pos=None; i=0; n=len(L)
        last_inc=None
        while i<n:
            s=L[i]
            if s.startswith('#include'): last_inc=i
            elif s.startswith('#ifndef') or s.startswith('#define') or s.startswith('/*') or s.strip()=='' or s.startswith('#ifdef __cplusplus') or s.startswith('extern "C"') or s.startswith('#endif') or s.startswith('#if ') or s.startswith('#else'): pass
            else: break
            i+=1
        if last_inc is not None: pos=last_inc+1
        else:
            g=[j for j,s in enumerate(L[:5]) if s.startswith('#define ') and L[max(0,j-1)].startswith('#ifndef')]
            pos=g[0]+1 if g else 0
        L.insert(pos,inc); added+=1
    open(fp,'w',errors='surrogateescape').write('\n'.join(L))
print(f"includes added: {added} in {len(want)} files; headers left alone: {len(skipped)}")
if unmapped:
    print("UNMAPPED:", ', '.join(f"{i}@{f}x{c}" for (i,f),c in unmapped.most_common(25)))
