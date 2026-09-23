#!/usr/bin/env bash
# release_stood_down_claims_ceo_1181.sh -- Lon runs this (CEO-1181/1183): the cfo and coo are STOOD DOWN on Lon's word
# ("All officers are stood down." / "We'll keep CFO and COO stood down.", 2026-09-23) and "Give all the GC to the CTO."
# The bus refuses `assign cto` on a row whose claim file belongs to another seat (a park is not an eviction), the
# stood-down seats cannot send the closing telegram that releases a claim, and the harness refuses the ceo deleting
# another seat's claim file. This moves the seven claims to released/ with a stamp, then the ceo's `assign cto` lands.
set -u
P=/home/resources/postoffice; ST=$(date +%Y%m%dT%H%M%S); n=0
for c in \
  prolog-gc-chunk-b-the-call-and-procedure-family-18-sites-poll-res-where-the-result-is-a-descr \
  gc-a-site-that-refuses-every-poll-form-names-an-unrooted-holder-starting-with-the-concat-slot-capture \
  instruments-the-safe-point-census-counts-sites-in-31-templates-nothing-dispatches-so-the-denominator-carries-dead-code \
  instruments-the-reads-rc-census-misses-a-bare-seat-root-so-37-batons-grade-whichever-tree-one-seat-happens-to-hold \
  gc-the-mark-worklist-walks-typed-visitors-not-words-every-heap-block-kind-has-a-layout-and-hb-ws-is-split-by-allocation-site \
  gc-rt-c-c-to-bb-entries-leave-no-emitted-code-is-entered-from-c-in-rt-c-except-the-original-entry-shims \
  gc-the-block-birth-ledger-names-the-block-at-the-moment-of-the-fault; do
  f="$P/claims/$c.claim"
  if [ -f "$f" ]; then mv "$f" "$P/released/$c.claim.released-CEO-1181-$ST" && n=$((n+1)) && echo "released: $c"; else echo "no claim file (already released): $c"; fi
done
echo "RELEASED $n claim file(s) of the stood-down cfo and coo; now the ceo runs assign cto on the GC rows (CEO-1181)."
