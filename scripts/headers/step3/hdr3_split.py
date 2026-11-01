#!/usr/bin/env python3
# hdr3_split.py <SCRIP-root>: headers step 3 (ARCH-HEADER-SPLIT 3.2 as measured): emit.h un-concatenated into its families by TEXT MOVE, the dead declarations deleted,
# emit_head.h folded into emit.cpp's head, XA.h into x86_ops.h, emit_ir.h gone (ir_node_index.h declares bb_node_id), emit_decls.h (included by nobody) deleted,
# bb_template_common.h re-cut, every includer retargeted to the families whose identifiers it names.
import os, re, sys, importlib.util, collections, json
W = os.path.abspath(sys.argv[1]); SRC = os.path.join(W, 'src')
spec = importlib.util.spec_from_file_location('U', '/home/claude_cto/harness/scripts/util_header_fanin.py'); U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
SEP = '/*' + '-' * 196 + '*/'
def rd(rel): return open(os.path.join(SRC, rel), errors='surrogateescape').read()
def wr(rel, text):
    p = os.path.join(SRC, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', errors='surrogateescape').write(text)
E = rd('emitter/emit.h').split('\n'); assert len(E) == 893 and E[-1] == '', len(E)
L = lambda n: E[n - 1]
def rng(a, b): return list(range(a, b + 1))
# ---- the family table: line numbers of emit.h (1-based) ----
FAM = collections.OrderedDict()
FAM['emitter/emit_medium.h'] = dict(c=[8, 17, 18, 19, 23, 24, 25, 44, 45, 46, 47, 48, 49, 52, 53, 54, 55, 58, 59, 60, 61, 62, 63, 217, 218, 221, 260] + rng(799, 805) + [876], cxx=[861, 867],
    inc=['<stdio.h>', '<stdint.h>', '<stddef.h>', '"ir/bb_pool.h"'], cxxinc=['<string>'])
FAM['emitter/bb_label.h'] = dict(c=[27, 28, 38, 39, 40, 41, 50, 51, 56, 57, 65, 66, 67, 68, 71, 72, 73, 74, 75, 76], cxx=[], inc=['<stdint.h>', '"ir/ct_vec.h"'])
FAM['emitter/emit_state.h'] = dict(c=[42, 276] + rng(278, 672) + [673, 674, 710], cxx=[], inc=['<stdint.h>', '"ir/IR.h"', '"ir/ct_vec.h"', '"emitter/bb_label.h"'], tail_c=['#define _ g_emit'])
FAM['emitter/emit_data.h'] = dict(c=rng(81, 85) + [99, 100] + rng(200, 204), cxx=[], inc=['<stddef.h>', '"ir/ct_vec.h"'])
FAM['emitter/emit_knobs.h'] = dict(c=rng(86, 90) + rng(92, 94), cxx=rng(868, 870), inc=[])
FAM['emitter/emit_regime.h'] = dict(c=rng(693, 697) + [709, 716] + rng(717, 724) + [882, 883, 885, 886, 887, 888, 889], cxx=[865, 866], inc=['<stdint.h>', '"ir/IR.h"', '"emitter/emit_state.h"'])
FAM['emitter/emit_rtx.h'] = dict(c=rng(871, 875), cxx=[], inc=[])
FAM['emitter/emit_walk.h'] = dict(c=[70, 186, 189, 277], cxx=[], inc=['<stdint.h>'], head_c=['struct bb_label_t;'])
FAM['emitter/emit.h'] = dict(c=[4, 20, 21, 22, 69, 78, 95, 97] + rng(141, 155) + [157, 182, 183, 184, 190, 192, 193, 194, 198, 199] + rng(732, 738) + [884], cxx=[862],
    inc=['<stdio.h>', '"ir/IR.h"', '"ir/bb_box.h"', '"emitter/bb_label.h"'])
CXXONLY = collections.OrderedDict()
CXXONLY['emitter/emit_str.h'] = dict(lines=rng(836, 841) + rng(842, 844) + rng(845, 848) + ['std::string emit_seq(std::initializer_list<std::string> parts);'] + rng(850, 860) + [863, 864],
    inc=['<string>', '<cstdint>', '<cstddef>', '<cstdio>', '<cstdlib>', '<initializer_list>', '"emitter/emit_state.h"'])
CXXONLY['emitter/emit_gc_site.h'] = dict(lines=rng(877, 881) + [890], inc=['<string>', '<cstdint>'])
EMITCPP_STATICS = rng(29, 37) + rng(675, 692)          # bb_label_name_set (with its separator), xa_pair_push, STNO_REC + stno_rec_push
EMIT_SEQ_BODY = 849
assigned = collections.Counter()
for f in FAM.values():
    for n in f['c'] + f['cxx']: assigned[n] += 1
for f in CXXONLY.values():
    for n in f['lines']:
        if isinstance(n, int): assigned[n] += 1
for n in EMITCPP_STATICS + [EMIT_SEQ_BODY]: assigned[n] += 1
dup = [n for n, k in assigned.items() if k > 1]; assert not dup, ('a line assigned twice', dup)
DELETED = [n for n in range(1, 893) if n not in assigned]
# every deleted line is a declaration we have measured dead, a duplicate, an include, a guard, a wrapper or a separator -- list the non-trivial ones for the record
record = [(n, L(n)) for n in DELETED if L(n).strip() and not L(n).startswith(('#include', '#ifdef', '#endif', '#else', '#pragma', 'extern "C" {', 'extern "C++" {', '}', 'namespace', 'using namespace')) and L(n) != SEP]
json.dump(dict(deleted=[[n, L(n)] for n in DELETED], record=record), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hdr3_deleted.json'), 'w'), indent=0)
print('emit.h lines: assigned %d, deleted %d (%d declarations deleted as dead or duplicate)' % (sum(assigned.values()), len(DELETED), len(record)))
def guard(rel): return re.sub(r'[^A-Za-z0-9]', '_', rel).upper()
def strip_c_spec(s): return re.sub(r'^extern "C" ', '', s)
def family_text(rel, f):
    g = guard(rel); out = ['#ifndef ' + g, '#define ' + g]
    out += ['#include ' + i for i in f.get('inc', [])]
    out += f.get('head_c', [])
    out += ['#ifdef __cplusplus', 'extern "C" {', '#endif']
    for n in f['c']: out.append(strip_c_spec(L(n)))
    out += f.get('tail_c', [])
    out += ['#ifdef __cplusplus', '}', '#endif']
    if f['cxx']:
        out += ['#ifdef __cplusplus']
        out += ['#include ' + i for i in f.get('cxxinc', [])]
        for n in f['cxx']: out.append(L(n))
        out += ['#endif']
    out += ['#endif', '']
    return '\n'.join(out)
def cxxonly_text(rel, f):
    g = guard(rel); out = ['#ifndef ' + g, '#define ' + g, '#ifndef __cplusplus', '#error ' + os.path.basename(rel) + ' is C++ only', '#endif']
    out += ['#include ' + i for i in f.get('inc', [])]
    for n in f['lines']: out.append(L(n) if isinstance(n, int) else n)
    out += ['#endif', '']
    return '\n'.join(out)
NEW = {}
for rel, f in FAM.items(): NEW[rel] = family_text(rel, f)
for rel, f in CXXONLY.items(): NEW[rel] = cxxonly_text(rel, f)
# ---- the declared identifiers of every new header (from their text), for the retarget ----
IDS = {rel: set(U.scan_header(txt)[0]) for rel, txt in NEW.items()}
IDS['emitter/emit_state.h'].add('_')
EXTRA = {'templates/x86/x86_ops.h': set(['XA_op_t', 'XA_MACRO_LIBRARY', 'XA_MACRO_LIBRARY_OPEN', 'XA_MACRO_LIBRARY_CLOSE', 'XA_BB_MACRO_LIBRARY', 'XA_EXEC_STMT_BLOB', 'XA_FILE_HEADER', 'XA_FILE_FOOTER', 'XA_RODATA_STRTAB',
    'XA_PREDICATE_REGISTRY', 'XA_BB_PTR_SLOT', 'XA_ENTRY_DISPATCH', 'XA_FLAT_DATA_SECTION', 'XA_PATTERN_BLOBS', 'XA_PROLOGUE', 'XA_EPILOGUE', 'XA_EXPRESSION_REGISTRY', 'XA_KIDS_RODATA', 'XA_SUB_BUILDER', 'XA_BUILDER',
    'XA_REGISTRY_TABLE', 'XA_STRTAB_RODATA', 'XA_CSETTAB_RODATA', 'XA_CAP_FIXUP', 'XA_OP_COUNT']),
    'ir/ir_node_index.h': {'bb_node_id'}, 'runtime/keywords.h': {'rt_kw_direct_sym', 'rt_kw_index'}, 'planner/zeta_depth.h': {'x86_zdp_on_c'}, 'planner/frame_layout.h': {'zls_g_resumable_frame'},
    'lower/lower_prolog.h': {'emit_pl_scc_armed'}}
ALLH = dict(IDS); ALLH.update(EXTRA)
# ---- write the new headers, the merged ones, the deletions ----
for rel, txt in NEW.items(): wr(rel, txt)
xa = rd('ir/XA.h').split('\n'); xa_enum = [l for l in xa if not l.startswith(('#pragma', '/*'))]; xa_enum = [l for l in xa_enum if l.strip()]
ops = rd('templates/x86/x86_ops.h'); assert '#include "emitter/emit.h"\nextern "C++" {\n#ifndef _\n#define _ g_emit\n#endif\n' in ops
ops = ops.replace('#include "emitter/emit.h"\nextern "C++" {\n#ifndef _\n#define _ g_emit\n#endif\n', '#include "emitter/emit_state.h"\n' + '\n'.join(xa_enum) + '\nextern "C++" {\n', 1); wr('templates/x86/x86_ops.h', ops)
lp = rd('lower/lower_prolog.h'); assert lp.count('\n#endif\n') >= 1
lp = lp.replace('stage2_t *lower_pl_stage2(const tree_t *prog);\n', 'stage2_t *lower_pl_stage2(const tree_t *prog);\n' + '\n'.join(L(n) for n in rng(698, 702)) + '\n', 1); wr('lower/lower_prolog.h', lp)
ge = rd('emitter/g_emitter.h'); assert '#include "emit.h"\n' in ge
ge = ge.replace('#include "emit.h"\n', '#include "emitter/emit.h"\n#include "emitter/bb_label.h"\n#include "templates/x86/x86_ops.h"\n', 1)
ge = ge.replace('extern g_emitter_t g_emitter;\n#endif', 'extern g_emitter_t g_emitter;\nextern "C" void xa_dispatch(XA_op_t op);\nextern "C" const char * bb_ab_sym_name(const char * nm);\n#endif', 1); wr('emitter/g_emitter.h', ge)
tc = ['/*' + '-' * 196 + '*/', '#pragma once', '#define CSET_CHAIN_MAX 3', '#include "emitter/emit_state.h"', '#include "emitter/bb_label.h"', '#include "templates/x86/x86_ops.h"', '#include "ir/IR.h"',
      'int zls_off(const IR_t *nd);', 'int zls_argv_off(const IR_t *nd);', 'int zls_act_off(const IR_t *nd);', '#define GZ_CELL_OFF(slot) (8 + 16 * (slot))', '']
old_tc = rd('templates/bb/bb_template_common.h'); assert 'int zls_act_off(const IR_t *nd);' in old_tc and '#define GZ_CELL_OFF(slot) (8 + 16 * (slot))' in old_tc
wr('templates/bb/bb_template_common.h', '\n'.join(tc))
es = rd('emitter/emit_str.cpp'); assert L(EMIT_SEQ_BODY).startswith('inline std::string emit_seq(')
es = es.rstrip('\n') + '\n' + SEP + '\n' + L(EMIT_SEQ_BODY)[len('inline '):] + '\n'
if '#include "emitter/emit_str.h"' not in es and '#include "emit_str.h"' not in es: es = '#include "emitter/emit_str.h"\n' + es
wr('emitter/emit_str.cpp', es)
# emit.cpp: the head from emit_head.h, then the statics; the mid-file includes of the merged headers dropped
ec = rd('emitter/emit.cpp').split('\n'); assert ec[0] == '#include "emit_head.h"'
head = ['#include <unordered_map>', '#include "ir/ct_arena.h"', '#include "ir/ct_vec.h"', '#include "runtime/rt/prolog_atom.h"', '#include <string>', '#include <climits>', '#include "emitter/emit.h"',
        '#include "emitter/emit_state.h"', '#include "emitter/bb_label.h"', '#include "emitter/emit_medium.h"', '#include "emitter/emit_data.h"', '#include "emitter/emit_knobs.h"', '#include "emitter/emit_regime.h"',
        '#include "emitter/emit_rtx.h"', '#include "emitter/emit_walk.h"', '#include "emitter/emit_str.h"', '#include "emitter/emit_gc_site.h"', '#include "runtime/keywords.h"', '#include "planner/zeta_depth.h"',
        '#include "planner/frame_layout.h"', '#include "lower/lower_prolog.h"', '#include "ir/gc_frame_map.h"', '#include "ir/dtp.h"', '#include "ir/ir_index.h"', '#include "ir/ir_node_index.h"',
        '#include "templates/bb/bb_templates.h"', '#include <unordered_set>', '#include <vector>', '#include <algorithm>', 'extern "C" {', '#include "driver/scrip_sm.h"', '#include "ir/stage2.h"',
        '#include "templates/xa/xa_templates.h"', '#include <string.h>', '#include <stdlib.h>', '#include <assert.h>', '#include "g_emitter.h"']
statics = [L(n) for n in EMITCPP_STATICS]
k = 1
while k < len(ec) and ec[k].startswith('#include'): k += 1
ec = head + ec[1:k] + statics + ec[k:]
ec = [l for l in ec if l not in ('#include "emit_ir.h"', '#include "XA.h"')]
wr('emitter/emit.cpp', '\n'.join(ec))
for dead in ('emitter/emit_head.h', 'emitter/emit_decls.h', 'ir/XA.h', 'ir/emit_ir.h'):
    os.remove(os.path.join(SRC, dead))
print('written: %d family headers; x86_ops.h, lower_prolog.h, g_emitter.h, bb_template_common.h, emit_str.cpp, emit.cpp rewritten; 4 headers deleted' % len(NEW))
# ---- retarget every includer ----
t = U.Tree(W, U.default_obj(W), 200)
def tokens_of_text(txt, deps=None):
    txt = U.strip_strings(U.strip_comments(txt)); toks = set(U.WORD.findall(txt)); todo = list(toks)
    while todo:
        w = todo.pop()
        for hh, body in t.macro_defs.get(w, ()):
            if deps is None or hh in deps:
                for x in body:
                    if x not in toks: toks.add(x); todo.append(x)
    return toks
OLD_INC = re.compile(r'^[ \t]*#[ \t]*include[ \t]*"((?:\.\./)*(?:[\w/]+/)?(?:emit|XA|emit_ir|emit_head|emit_decls)\.h)"[ \t]*$')
COMMON_CARRIES = {'emitter/emit_state.h', 'emitter/bb_label.h', 'templates/x86/x86_ops.h', 'ir/IR.h'}
changed = collections.Counter(); needs_log = {}
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        if not f.endswith(('.c', '.cpp', '.h', '.inc', '.hpp')): continue
        rel = os.path.relpath(os.path.join(dp, f), SRC)
        if rel in NEW or rel in ('emitter/emit.cpp', 'templates/bb/bb_template_common.h', 'templates/x86/x86_ops.h', 'emitter/g_emitter.h'): continue
        txt = rd(rel); lines = txt.split('\n')
        hits = [i for i, l in enumerate(lines) if OLD_INC.match(l)]
        if not hits: continue
        deps = t.unit_deps.get(rel)
        toks = tokens_of_text(txt, deps)
        is_tpl = rel.startswith(('templates/bb/', 'templates/xa/')) and ('#include "bb_template_common.h"' in txt or '#include "templates/bb/bb_template_common.h"' in txt or 'xa_template_common.h' in txt)
        need = []
        for h, ids in ALLH.items():
            if h == rel: continue
            if toks & ids:
                if is_tpl and h in COMMON_CARRIES: continue
                need.append(h)
        if 'XA_op_t' in toks or any(w.startswith('XA_') for w in toks):
            if 'templates/x86/x86_ops.h' not in need and not (is_tpl): need.append('templates/x86/x86_ops.h')
        order = list(ALLH.keys()); need.sort(key=lambda h: order.index(h))
        incs = ['#include "%s"' % h for h in need if ('#include "%s"' % h) not in txt]
        first = hits[0]
        new_lines = []
        for i, l in enumerate(lines):
            if i == first: new_lines += incs
            elif i in hits: continue
            else: new_lines.append(l)
        wr(rel, '\n'.join(new_lines)); changed[rel.split('/')[0]] += 1; needs_log[rel] = need
json.dump(needs_log, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hdr3_needs.json'), 'w'), indent=0)
print('retargeted includers:', dict(changed), 'total', sum(changed.values()))
