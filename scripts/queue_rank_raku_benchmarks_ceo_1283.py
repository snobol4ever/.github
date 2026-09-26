#!/usr/bin/env python3
"""CEO-1283 (Lon 2026-09-26 13:4x, in-chat to the ceo, verbatim: "Make HQ-RAKU top priority to get ALL Raku benchmarks running by
implementing any missing features."): every FREE hq_raku row minted this sitting for the Raku benchmark gaps -- the seventeen feature
classes, the kernel-convention row -- moves to rank 0 so `next` serves them first when hq_raku is seated. FREE rows only (a live claim's
cells are never rewritten by script, CEO-755c); a dated QUEUE.tsv backup first. --dry-run | --apply"""
import sys, shutil, datetime
Q='/home/resources/postoffice/QUEUE.tsv'; apply='--apply' in sys.argv
rows=open(Q,encoding='utf-8').read().split('\n'); out=[]; moved=[]
for l in rows:
    f=l.split('\t')
    if len(f)>=4 and f[2]=='hq_raku' and f[3]=='FREE' and f[1].startswith('raku-') and ('benchmarks-every-kernel-follows' in f[1] or f[1] in {
        'raku-a-program-s-last-statement-may-omit-its-semicolon-as-rakudo-allows','raku-statement-modifiers-expr-for-list-and-expr-while-cond-and-nil-while',
        'raku-the-c-style-loop-init-cond-step-block','raku-native-typed-variables-my-int-and-my-str','raku-the-x-cross-operator-flat-and-multi-parameter-pointy-blocks-i-j-and-destructuring-i-j',
        'raku-binding-to-a-scalar-or-an-array-my-a-bind-0-and-my-x-bind-todo-x','raku-push-a-x-as-a-sub-call','raku-hyper-method-int-and-reduce-plus-over-a-range-and-a-method-chain-await-do-for-and-the-ternary',
        'raku-grammars-proto-token-token-rule-and-from-json-on-them','raku-the-private-method-call-obj-method','raku-flat-map-block-list','raku-prefix-increment-on-an-indexed-element',
        'raku-the-set-difference-operator-and-a-pointy-block-as-a-listop-argument','raku-a-capture-parameter-sub-a-backslash-and-signature-introspection',
        'raku-mode-3-emitter-an-outer-lexical-read-from-a-nested-sub-a-nil-read-a-constant-and-an-excised-node','raku-wrong-answers-rat-arithmetic-the-whatever-star-index-and-append-and-float-printing-precision',
        'raku-an-empty-for-body-never-terminates'}) and f[0]!='0':
        moved.append(f[1]); f[0]='0'; l='\t'.join(f)
    out.append(l)
print(len(moved),'rows to rank 0'); [print('  ',m[:90]) for m in moved]
if apply and moved:
    shutil.copy2(Q, Q+'.bak.'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-ceo1283-raku-rank0')
    open(Q,'w',encoding='utf-8',newline='\n').write('\n'.join(out)); print('applied')
