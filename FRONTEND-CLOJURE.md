# FRONTEND-CLOJURE.md — Clojure-EDN Frontend

Clojure-EDN is the native frontend for snobol4jvm.
Allows expressing SNOBOL4 programs as Clojure EDN data structures,
consumed directly by the JVM runtime without a separate parse step.

*Session state → JVM.md. Backend → BACKEND-JVM.md.*

---

## Status: Active (integrated with JVM runtime)

The EDN cache sprint (`jvm-edn-cache` ✅ `b30f383`) achieved 22× per-program speedup
by caching parsed EDN representations. The Clojure-EDN frontend is the primary
input path for the JVM backend alongside SNOBOL4 text input.
