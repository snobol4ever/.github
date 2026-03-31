# SESSION-linker-sprint1.md — SCRIP Linker JVM Track

**Track:** LINKER (LP) — JVM  
**Session prefix:** `LP-JVM` · **Trigger:** "playing with linker jvm"  
**Gate:** Read `ARCH-scrip-abi.md` before touching any code.

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SCRIP ABI / calling convention | `ARCH-scrip-abi.md` | any cross-lang call site |
| JVM emitter | `BACKEND-JVM.md` | Jasmin patterns |
| .NET linker (parallel track) | `SESSION-linker-net.md` | reference only |

---

## §BUILD

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

---

## §NOW — LP-JVM-4 (next)

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **LINKER JVM** | LP-JVM-3 | `55d8655` one4all | M-SCRIP-DEMO — cross-lang demo green |

**Completed:** M-LINK-JVM-1,2,3 ✅ — EXPORT/IMPORT in JVM, per-file .class, two-file SNOBOL4 link.  
M-LINK-JVM-3 outcome and demo status: see SESSIONS_ARCHIVE LP-JVM-3.

**Next action:** Unblock M-SCRIP-DEMO — fix `pj_call_goal` wrong args to `pj_reflect_call` (see SESSIONS_ARCHIVE LP-JVM-3 session 2 handoff), then verify demo1–3 three-lang links.
