# FINDING — an uncommitted porter.sno edit in the CEO root was BROKEN under the oracle; preserved here and in the corpus stash, tree restored

**Seat:** ceo · **Date:** 2026-08-26 · **Mode:** FLEET-16
**Trees:** corpus `7381ae2a2` (after disposition; the edit was found on top of `14c5cf745`)

## WHAT WAS FOUND

The CEO-root corpus working tree carried **two uncommitted modifications of unknown provenance** (left by an earlier session in `/home/claude`; no session claims them), surfaced by the banner's `corpus: 2 uncommitted change(s)` refusal:

1. `demo/snobol4/treebank/treebank.sno` — **whitespace-only**: goto-column alignment on the `ListAppend` line (whitespace in the goto field, insignificant to SNOBOL4). ✅ **Committed** as part of `7381ae2a2` with provenance-unknown noted in the message.
2. `demo/snobol4/porter/porter.sno` — **semantic**: replaces the `s_i()` deferred-function mechanism with an inline deferred assignment `. *(target = 'i')` in the step-1a pattern and guts the `s_i` function body (drops `target = 'i'`, leaving the label bare).

## THE MEASUREMENT (oracle A/B, both arms same input, same flags)

`/home/resources/x64/bin/sbl -bf porter.sno < porter.input`, graded against `porter.ref`:

| arm | vs `porter.ref` |
|---|---|
| HEAD (`git show HEAD:...`) | **MATCHES** |
| the uncommitted edit | **DIVERGES** — `abbey` stems to `abbei` (first divergence at ref line 14; the inline deferral fires where the `s_i()` mechanism did not) |

So the edit is a **broken experiment**, not a fix: committing it would have violated no-broken-commits, and leaving it in the tree blocked every banner from this root.

## DISPOSITION — nothing destroyed

- The edit is preserved TWICE: in the corpus **stash** (`git stash list` → *"porter.sno broken experiment (abbey->abbei vs oracle)"*, recover with `git stash pop`) and verbatim below.
- The working tree is restored to HEAD; corpus is clean and pushed at `7381ae2a2`.
- If the author recognizes this work: pop the stash, fix the conditional firing (the `epsilon . *s_i()` capture context is what made the deferral conditional), and grade against `porter.ref` before committing.

## THE PATCH, VERBATIM

```diff
--- a/demo/snobol4/porter/porter.sno
+++ b/demo/snobol4/porter/porter.sno
@@ -162,7 +162,7 @@ s_ss           target         =  'ss'
                s_ss           =  .dummy                             :(NRETURN)
 s_ss_end
                DEFINE('s_i()')     :(s_i_end)
-s_i            target         =  'i'
+s_i
                s_i            =  .dummy                             :(NRETURN)
 s_i_end
                DEFINE('s_empty()') :(s_empty_end)
@@ -260,7 +260,7 @@ a_s1ab_end
                p1a            =
 +              POS(0)
 +              ( RTAB(4) $ stem 'sses' (epsilon . *s_ss())
-+              | RTAB(3) $ stem 'ies'  (epsilon . *s_i())
++              | RTAB(3) $ stem 'ies'  . *(target = 'i')
 +              | RTAB(2) $ stem 'ss'   (epsilon . *s_ss())
 +              | RTAB(1) $ stem 's'    (epsilon . *s_empty())
 +              )
```

## THE GENERAL NOTE

An uncommitted change in a shared root is invisible until a banner refuses over it, and by then its author is gone. The banner did its job here — the refusal is what surfaced the broken edit before anyone committed it as drive-by hygiene. Grade before you adopt: the whitespace half was committable, the semantic half was not, and only the oracle A/B could tell them apart.
