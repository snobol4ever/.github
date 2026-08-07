# FINDING-2026-08-07i — ZK-34-FIX: ZD-5b guard was dead comment text; NULL ω.node arm added

**Session:** s12 (Sonnet 4.6, 2026-08-08)
**Probes affected:** F03 F05 G06 G22 G23 — m4 SIGSEGV, m3 PASS
**Fix commit:** SCRIP `484f3965` · corpus `d36c0c0c`

## The phantom fix

M-1-FIX-3 (`71bda272` + comment-fix `682016d6`) was supposed to add a ZWS backward-edge oin guard at emit.cpp line 2096. But line 2095 ends with `/* ZD-5b (s24b):` — an UNCLOSED C comment. Line 2096's code `{ if (!oin && zws && ot) { ... } }` lived INSIDE that comment and was never compiled. Every build since `71bda272` silently ignored the guard. That is why F03/F05/G06/G22/G23 never actually passed m4 in this repo.

## The crash

G06 (`ANY('AB') FENCE '+'`): `zws=1` (ZWS canonical frame armed; nblob_real=0, FENCE1 not sealing because SCRIP_ZD_FENCE1=1 default). MATCH_LIT at run position r=5, K=0. Its ω goes to the MATCH_BEGIN abort-fail path (`n8_match_begin_af`). In the IR: `ω.node=NULL` (template-routed; no IR node for the abort-fail path). The k>r forward-only test gives `oin=0`. The port_sz_beta guard also gives `oin=0` (no beta tag on abort-fail). So `zwpop[i] = _wzdepth - K + kc = 224` is staged. `n11_match_lit_β` emits `add rsp, 224` — but `n8_match_begin_af` already does `lea rsp,[rbp-8]; pop rbp; add rsp,160` (full whack). Double-release: RSP corrupted, SIGSEGV. m3 survives because the VAR read precedes the `add rsp`.

## The fix (two parts, one line each)

**Line 2095:** Add `*/` at end of line to close the ZD-5b comment. This makes line 2096 active code.

**Line 2096:** Extend the guard from `zws` to `(zws || zwr)`, and add `!ot` arm:
```c
{ if (!oin && (zws || zwr) && K == 0) {
    int _io = !ot;
    if (!_io) { for (int _ik = 0; _ik <= r; _ik++) { if (nodes[run[_ik]] == ot) { _io = 1; break; } } }
    if (_io) oin = 1;
} }
```
- `!ot` arm: NULL ω.node = template-routed fail path. MATCH_END is sole release authority; suppress wpop.
- Backward-edge arm: ω points to a run member at position ≤ r (backward). Same law.
- Gated `(zws||zwr) && K==0`: non-match, non-window, K>0 runs byte-identical.

## Why FENCE programs use ZWS not ZWR

`nblob_real=0` because FENCE1's blob-closure members (MATCH_LIT, MATCH_ANY) return the -0x40000000 sentinel from `zls_node_off` (K=0 elided kinds, no FRQ slots). `zw_nblob_ok(0, has_blob=1)` returns true (safe). FENCE1 is not sealing (SCRIP_ZD_FENCE1=1 default). So `zws=1`. Mechanism-2 (zwr) is off for these programs.

## Result

m3 134/8/0/0 · m4 131/11/0/0 · 0 REGRESSION both modes. Feature regen: 25 `.s` files updated (wpop suppressed on K=0 scanner kinds in ZWS windows).
