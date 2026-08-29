# FINDING — the probe TOTAL CONVERSION preserved the Defect C witnesses' CONTENT and destroyed the
# INSTRUMENT that graded them. All 8 survive inside one consolidated suite; the acceptance gate needs
# them as 8 separately-compiled binaries under `env -i`, and now correctly refuses rc=2 on a fossil path.

**hq_P · 2026-08-29 · row `defect-c-zop-flat-regime-depth-compensate`** (mine, `RESTRICTED:hq_P`).
Found while landing the gate class-split hq_C approved. **No corpus files touched.**

## 1. What happened

`c06960a12` — *"probe/ TOTAL CONVERSION EXECUTED (Lon 2026-08-29 direct order to ceo): corpus/probe
DELETED"* — converted `corpus/probe/vlist_select/` into the suite pair
`corpus/tests/snobol4/probe/vlist_select.{sno,ref}`.

✅ **Content is fully preserved.** All eight witnesses are present in the 233-line converted suite
(`c01 c02 v01 v02 v03 v04 v05 v06`, each named, `v05` three times). The conversion did its job by the rule
it is held to: byte-equal-or-no-delete protects the *files*.

⛔ **But `test_gate_defect_c_vlist_ladder.sh` — this row's acceptance instrument, and the one hq_C's
witness row closes against — cannot use them.** It now refuses:

```
⛔ REFUSES (rc=2): witness dir /home/claude_P/corpus/probe/vlist_select does not resolve.
```

⭐ That refusal is the gate behaving **correctly** — refuse rather than report a smaller ladder — and it is
the only reason this was noticed at all rather than silently grading zero witnesses.

## 2. ⛔ Why repointing the path does NOT fix it

The gate does not merely read the witnesses. Per witness it: compiles a separate `.s`, links a separate
binary, runs it **20× under `env -i`**, then runs it once more under **`env -i` + valgrind**, and grades
each independently. That structure is not decoration — it is the row's whole detection mechanism, because
seat03 established that this defect is **environment-size sensitive** and that `env -i` + valgrind is the
only arm that catches it 8/8 deterministically.

A consolidated suite is **one program in one process in one environment**. So after conversion you can get
one verdict for all eight witnesses, in a single environment, with no per-witness valgrind attribution.
⛔ **The instrument cannot be restored by changing `PROBE=` to the new path** — there is nothing there with
the shape it needs.

## 3. ⭐ The general form, which is the part worth keeping

The consolidation's guard protects **content**. Nothing protected the **shape**.

> **A file can be fully preserved in content and still break the instrument that depended on its being a
> separately compilable, separately runnable unit.**

This is adjacent to hq_B's reachability law (*"a deferral records intent, not reachability"*) and is a
distinct sub-case of it: here the file IS reachable — its text is in a suite that runs — and the thing that
died is the *granularity* an acceptance instrument required. ⛔ A "is anything still running this file?"
check would answer **yes** for `vlist_select` and still miss this entirely. The question that catches it is
**"can every instrument that graded this file still do what it did?"**

## 4. What this means for the row, stated plainly

- ⛔ **The Defect C row currently has no runnable acceptance instrument.** Its DONE-WHEN calls this gate;
  the gate refuses rc=2. That is on top of the separate problem I recorded earlier — that even when it ran,
  a green ladder could not distinguish a cure from a witness that had gone quiet.
- ⚠️ So this row is now **doubly ungradeable**: the criterion cannot run, and if it ran it could not
  discriminate. Nobody should attempt the cure until at least one of those is repaired.
- ⭐ **The cheapest repair is probably to keep the eight witnesses as separate probe files for this gate's
  use** — the conversion's own charter says only *genuinely* stdin/file-driven tests stay standalone, but
  the operative property here is not stdin, it is **per-witness process isolation for an env-size-sensitive
  detector**. That is a real KEEP reason and I would argue it qualifies. ⛔ It is not my unilateral call:
  the conversion was executed on Lon's direct order, so the exception belongs to ceo, and the witness row
  belongs to hq_C.

## 5. Landed alongside, and separate from this

The class-split hq_C approved is in at SCRIP `89207808`: the gate now counts OOB and uninitialised
separately and says so, with a CLASS SPLIT line and an explicit warning when OOB is 0 while UNI is not.
It is negative-tested against synthetic valgrind output (OOB log → `OOB=2 UNI=0` FAILS; uninitialised log →
`OOB=0 UNI=1` FAILS; empty → CLEAN passes), because Defect C is latent and cannot be made to fire on
demand. ⚠️ It could **not** be demonstrated end-to-end on live witnesses — for the reason this FINDING
documents.

- Trees: SCRIP `89207808`, corpus `f6d8098c9`, `.github` at commit time; pristine, `RT_OPT=-O0`.
