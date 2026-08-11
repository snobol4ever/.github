# FINDING 2026-08-10h — RTCC s15 (Opus 5)
## Half the scripts grade a tree by ABSOLUTE PATH, so in a multi-seat container a gate run in your clone can be auditing another seat's worktree — and the finding that proves it also FALSIFIES this session's own first verdict.

**Class:** RC-0 / instrument integrity. **ZERO emitter bytes, ZERO source edits, ZERO script edits, no regen owed.** Audit only, from a private clone.
**Method:** origin `565ecfa`, shallow clone at `/home/claude/s15-rtcc/scrip-audit`. The live peer's canonical trees were **read, never written**.

---

## 1. THE NUMBERS

| quantity | value |
|---|---|
| scripts in `scripts/` | **383** |
| …hardcoding an absolute `/home/claude/…` path | **191 (50%)** |
| gates (`test_gate_*.sh`) | **71** |
| …hardcoding an absolute `/home/claude/…` path | **23** |
| …resolving root via `git rev-parse --show-toplevel` | **0** |
| …resolving root via `dirname $0` | **23** |
| ⇒ gates whose target tree depends on cwd or a pinned path | **48 of 71** |

Pinned targets by frequency: `/home/claude/corpus` **192** · `/home/claude/SCRIP` **34** · `/home/claude/x64` **27** · `/home/claude/work` **13** · `/home/claude/csnobol4` 9 · `/home/claude/.github` 7.

## 2. ⭐ THE HAZARD — A GATE CAN GRADE A TREE YOU ARE NOT EDITING

`test_gate_omega_own_k.sh:25` reads `CORPUS="${CORPUS_DIR:-/home/claude/corpus}"`; `test_gate_pascal_m3.sh:3` reads `SCRIP="${SCRIP:-/home/claude/SCRIP/scrip}"`. Run such a gate from any clone and it does not audit that clone. It audits whatever tree is sitting at the canonical path.

Under one seat this is harmless — the canonical path *is* your tree. Under the multi-seat reality this container has exhibited four times today it is not:

- The tree at `/home/claude/SCRIP` right now carries **1 unpushed commit** belonging to the live peer seat. A gate run by any other seat grades **the peer's in-flight work** and reports the verdict as that seat's own.
- `/home/claude/work` is referenced by **13** scripts, and `/home/claude/work` **did not exist** during this session — it vanished between orientation and first rung.
- Three goals now in flight move source paths: **SRC REORG · RUNTIME RENAME/REORG · SCRIP RENAME.** Every pinned reference is a silent tripwire for all three.

⛔ **CONSEQUENCE FOR THIS GOAL SPECIFICALLY.** GOAL-RTCC requires *"HEAD-stamp every measurement."* A HEAD stamp names the commit of the tree you are *in*; a pinned gate reports on the tree at the *path*. When those differ, the stamp is wrong **by construction, with no one at fault and nothing to notice** — the same defect class as s13b's phantom `.so`, generalised from build artifacts to the entire measurement surface.

## 3. ⛔ RETRACTION — THIS SESSION'S OWN FIRST VERDICT WAS WRONG, AND THE MECHANISM CHECK IS WHAT CAUGHT IT

s15 hypothesised that absence-asserting gates lacking a positive control are dark, built an empty-tree scaffold, ran 8 pure-grep absence-only gates in it, and recorded `test_gate_omega_own_k.sh` as **"DARK — passes over nothing."**

**That verdict is FALSE and is withdrawn.** `omega_own_k:35` carries exactly the positive control the hypothesis said it lacked — `if [ "$TOTAL_FILES" -eq 0 ]; then exit 1` — and it worked perfectly. It passed the empty-tree run because it **never read the empty tree**: `CORPUS` is pinned, so it inspected the real corpus, found files, and passed honestly. **The broken instrument was mine.**

⇒ The audit's own headline number was produced by the failure mode the audit exists to detect. It survived only because the mechanism was opened before the count was quoted — s13b's law (*a census over assembly must expand the project's own macros or it measures their absence*) turning out to bind the auditor as tightly as the audited.

⇒ **`omega_own_k` is hereby the EXEMPLAR to copy, not a defect.** It is the one gate examined here that cannot silently grade nothing. Its four-line file-count guard is the pattern the other 70 want.

## 4. NOT A FINDING — `test_gate_no_lang_names.sh` IS RED (1584) BUT IS NOT THE SANCTIONED GATE

Reported here only to stop the next session re-deriving it as an alarm. RULES.md's LI-FENCE FACT RULE names **`test_gate_emit_no_lang.sh`** as enforcement, and that gate is **GREEN at `565ecfa`** (*"LANG-BLIND — no language-identity identifier in src/emitter or src/templates"*). `test_gate_no_lang_names.sh` is a broader unsanctioned variant over `src/emitter src/runtime` whose TAG regex admits obviously benign hits (`pl_gz_callee_vec_t` matching `pl_`). **No LI-FENCE violation is claimed.** Whether the broad variant should be repaired, narrowed, or deleted is an owner's call.

## 5. FIX (proposed — NOT applied; 191 sites is a shared-file edit and wants a ruling first)

1. **Resolve root once, from git:** `ROOT=$(git rev-parse --show-toplevel)`, absolute path as *fallback only*. **0 of 71 gates do this today.** A gate then grades the tree it is run in — which is what every reader already assumes it does.
2. **Give every absence-asserting gate a positive control** — copy `omega_own_k:35`. An absence gate that has never returned a hit is indistinguishable from a broken one (FINDING 2026-08-10g §4).
3. Order of operations matters: (1) before (2), because a gate fixed to look in the right place may start reporting real violations that were previously invisible.

## 6. NOT DONE / OPEN

- **No script edited.** 191 call sites across 383 files is not a drive-by; it also collides with three live path-moving goals and wants their owners' sequencing.
- **No RTCC ladder rung executed** (RC-5 ANCHOR / RC-6 / RC-6b untouched, as s13b and s14 left them). **No build, no timing, no watermark re-proof** — this seat has no measurement and does not claim one.
- **Unquantified:** how many of the 48 cwd-or-path-dependent gates actually diverge in verdict between a clone and the canonical tree. The experiment is cheap (run the suite from both, diff exit codes) but needs a build and would have raced the peer.
