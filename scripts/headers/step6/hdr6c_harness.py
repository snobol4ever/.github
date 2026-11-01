#!/usr/bin/env python3
# hdr6c_harness.py -- the harness twin of headers step 6C: a script that compiles a unit or a checker against src headers with a hand-copied
# sub-directory -I list gains the source root (after the sweep every header names its includes from src/). hdr6c_harness.py <harness/scripts>
import sys, re
H = sys.argv[1].rstrip('/') + '/'
def rd(f): return open(H + f, errors='surrogateescape').read()
def wr(f, t): open(H + f, 'w', errors='surrogateescape').write(t)
def rep(f, old, new):
    t = rd(f); assert t.count(old) == 1, (f, old[:60], t.count(old)); wr(f, t.replace(old, new)); print('  ', f)
rep('test_gate_coexpr_stack_of_uncreated_thread.sh', 'gcc -O0 -g -I "$ROOT/src/runtime/rt" -I "$ROOT/src/ir" -o "$BIN"', 'gcc -O0 -g -I "$ROOT/src" -I "$ROOT/src/runtime/rt" -I "$ROOT/src/ir" -o "$BIN"')
rep('test_gate_shared_builtin_id_table_is_self_consistent.sh', 'gcc -I"$ROOT/src/runtime" -o "$T/bidcheck"', 'gcc -I"$ROOT/src" -I"$ROOT/src/runtime" -o "$T/bidcheck"')
rep('test_gate_ct_grow_grows_in_place_at_the_frontier_or_allocs_copies_and_abandons.sh', 'gcc -O0 -I"$ROOT/src/ir" -I"$ROOT/src/lower" "$T/h.c"', 'gcc -O0 -I"$ROOT/src" -I"$ROOT/src/ir" -I"$ROOT/src/lower" "$T/h.c"')
rep('test_unit_rt_arena.sh', 'gcc -I"$REPO/src/runtime/rt" -o "$T/t" "$T/t.c"', 'gcc -I"$REPO/src" -I"$REPO/src/runtime/rt" -o "$T/t" "$T/t.c"')
t = rd('test_invariants_3x3_harness.sh'); n = t.count('-I"$ROOT/src/parsers/prolog" -w -o'); assert n == 2, n
wr('test_invariants_3x3_harness.sh', t.replace('-I"$ROOT/src/parsers/prolog" -w -o', '-I"$ROOT/src" -I"$ROOT/src/parsers/prolog" -w -o')); print('   test_invariants_3x3_harness.sh (2 lines)')
print('harness twin of 6C applied: five scripts gain the source root; the three rtx scripts read RT_INCS from the Makefile and follow it; the two x86 crosscheck scripts name src/runtime/x86 and src/runtime/asm, directories that no longer exist, and are left as they are')
