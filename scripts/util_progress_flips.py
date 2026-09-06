#!/usr/bin/env python3
import sys, csv, argparse, collections, datetime
ap=argparse.ArgumentParser(); ap.add_argument("--db",default="/home/resources/progress/results.tsv"); ap.add_argument("--since",default="3d"); ap.add_argument("--per",default="hour"); ap.add_argument("--mode",default="m3"); ap.add_argument("--names",action="store_true"); a=ap.parse_args()
n=int(a.since[:-1]); unit=a.since[-1]; delta=datetime.timedelta(days=n) if unit=="d" else datetime.timedelta(hours=n)
since=(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)-delta).strftime("%Y-%m-%dT%H:%M:%S")
rows=[r for r in csv.DictReader(open(a.db),delimiter="\t") if r["mode"]==a.mode]
rows.sort(key=lambda r:r["ts_utc"])
last={}; ups=collections.defaultdict(list); downs=collections.defaultdict(list)
for r in rows:
    k=(r["suite"],r["program"]); prev=last.get(k); last[k]=r
    if prev is None or r["ts_utc"]<since: continue
    b=r["ts_utc"][:13] if a.per=="hour" else r["ts_utc"][:10]
    if prev["outcome"]!="PASS" and r["outcome"]=="PASS": ups[(b,r["class"])].append(f'{r["suite"]}:{r["program"]}')
    if prev["outcome"]=="PASS" and r["outcome"]!="PASS": downs[(b,r["class"])].append(f'{r["suite"]}:{r["program"]}')
buckets=sorted({b for b,_ in list(ups)+list(downs)})
print(f"bucket({a.per}, UTC)   master +/-   package +/-   (mode {a.mode}; rows {len(rows)}; since {since})")
tm=tp=0
for b in buckets:
    mu,md,pu,pd=len(ups[(b,"master")]),len(downs[(b,"master")]),len(ups[(b,"package")]),len(downs[(b,"package")]); tm+=mu; tp+=pu
    print(f"{b:20s} {mu:5d}/{md:<4d}   {pu:5d}/{pd:<4d}  "+("#"*min(mu+pu,60)))
    if a.names:
        for k in ((b,"master"),(b,"package")):
            for x in ups[k]: print("    +",x)
            for x in downs[k]: print("    -",x)
print(f"TOTAL newly-passing: master {tm}, package {tp}")
