import sys, datetime
P='/home/resources/postoffice'
FREE=['prolog-a-directive-name-before-an-infix-operator-is-an-atom-so-use-module-slash-1-parses','prolog-consult-loads-a-file-named-at-run-time','prolog-the-ten-gnu-file-and-os-builtins-logtalk-needs','prolog-clause-on-a-static-predicate-raises-the-iso-permission-error','prolog-read-term-accepts-the-syntax-error-option','prolog-logtalk-startup-emits-logtalk-library-path-twice-so-mode-4-cannot-assemble-and-mode-3-crashes','prolog-logtalk-hello-world-runs-under-scrip-through-the-scrip-adapter','prolog-every-suite-to-100-under-nonet-ceo-1266','icon-table-bucket-len-reads-22656-in-a-2048-bucket-table-and-the-dt-a-gc-arm-dereferences-the-garbage']
SUP={'raku-all-test-suites-of-the-language-read-100-percent-on-the-suite-table-the-home-stretch':'SUPERSEDED:raku-every-suite-to-100-under-nonet-ceo-1266'}
apply='--apply' in sys.argv
q=open(P+'/QUEUE.tsv','rb').read().decode()
out=[];n=0;ts=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
for line in q.split('\n'):
    f=line.split('\t')
    if len(f)>=4 and (f[1] in FREE or f[1] in SUP) and f[3].startswith('PARKED-LON-HOLD'):
        new=SUP.get(f[1],'FREE'); print(f'{f[1]}: {f[3]} -> {new}'); f[3]=new; n+=1
        if apply:
            with open(f'{P}/tasks/{f[1]}.task.md','ab') as b: b.write(f'\n- {ts} **STATE -> {new}** by ceo (CEO-1469: Lon 2026-10-03 "We are not SNOBOL4 only anymore. We are ALL langs ALL the way."; the 10-02 snobol4-only hold is lifted)\n'.encode())
    out.append('\t'.join(f))
if apply: open(P+'/QUEUE.tsv','wb').write('\n'.join(out).encode())
print(f'{"APPLIED" if apply else "DRY-RUN"}: {n} rows')
