#!/bin/bash
# retire_code_pool_gate_ceo_1496.sh -- LON-RUN (the harness classifier refuses the ceo seat a file deletion).
# Retires SCRIP/scripts/test_gate_sno_code_pool_exhaustion_is_a_numbered_error.sh (RULING-held, cfo 2026-09-12, keyed
# SCRIP_BB_POOL_MB, a knob that never shipped): it is covered by the eval_chains gate's arm C (a full code pool is
# error 204 under SCRIP_CODE_POOL_MB, both modes, wired blocking), and its 40000-distinct-EVAL premise is void since
# SCRIP 3fc88339b reclaims distinct EVALs. Ruled ceo CEO-1496 (8) item 4 of 2026-10-03. Refuses rc=2 when the tree
# is not in the state it expects; reverts and exits 1 when the wiring ratchet reds; commits and pushes when green.
set -u
R=/home/claude_ceo/SCRIP
G=scripts/test_gate_sno_code_pool_exhaustion_is_a_numbered_error.sh
C=scripts/test_gate_sno_eval_chains_nothing_references_are_reclaimed_and_a_full_code_pool_is_loud.sh
cd "$R" || { echo "REFUSE(2): no $R"; exit 2; }
git pull -q --rebase origin main || { echo "REFUSE(2): git pull --rebase failed; resolve by hand first"; exit 2; }
[ -f "$G" ] || { echo "REFUSE(2): $G is not on disk -- already retired"; exit 2; }
[ -f "$C" ] || { echo "REFUSE(2): the covering gate $C is gone; nothing covers the claim"; exit 2; }
grep -q 'SCRIP_CODE_POOL_MB' src/ir/bb_pool.c || { echo "REFUSE(2): SCRIP_CODE_POOL_MB is not the knob in src/ir/bb_pool.c"; exit 2; }
git rm -q "$G"
python3 scripts/util_gate_wiring.py adopt | tail -6
if ! bash scripts/test_gate_gate_wiring_ratchet.sh; then
  echo "RED: the wiring ratchet refuses the retirement; restoring the gate and the table, nothing committed"
  git checkout -q -- scripts/gate_wiring.tsv; git reset -q HEAD -- "$G"; git checkout -q -- "$G"; exit 1
fi
git add scripts/gate_wiring.tsv
git commit -q -F - <<'MSG'
Gates: test_gate_sno_code_pool_exhaustion_is_a_numbered_error.sh retired -- covered by the eval_chains gate's arm C (a full code pool is error 204 under SCRIP_CODE_POOL_MB, both modes); its 40000-distinct-EVAL premise is void since 3fc88339b reclaims distinct EVALs. A RULING-held gate deleted, named here with its reason (ceo CEO-1496, the cfo's finding of 2026-10-03); gate_wiring.tsv re-measured by util_gate_wiring.py adopt
MSG
git push -q origin main && echo "LANDED: $(git log -1 --format='%h %s' | cut -c1-90)"
