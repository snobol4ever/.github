# fleet-ops-industry: the sources (read 2026-11-04 by the cio through web search; VERIFY marks a figure read from a secondary source)

## 1. Compute: cgroups, PSI, controllers
- Meta cgroup2 docs, CPU controller (weight semantics, no-contention rule): https://facebookmicrosites.github.io/cgroup2/docs/cpu-controller.html
- fbtax2 "Putting it all together" (PSI as oomd's trigger, the slice layout): https://facebookmicrosites.github.io/cgroup2/docs/fbtax-results.html
- oomd announcement and repo (userspace OOM on PSI; build servers named): https://engineering.fb.com/2018/07/19/production-engineering/oomd/ , https://github.com/facebookincubator/oomd
- PSI cgroup support patch (per-cgroup pressure files): https://lkml.iu.edu/hypermail/linux/kernel/1808.0/00541.html
- TMO / senpai (CACM research highlight; 20-32 percent memory; pressure-threshold control loop; memory.reclaim preferred over a memory.high clamp per an LKML thread): https://cacm.acm.org/research-highlights/tmo-transparent-memory-offloading-in-datacenters , https://www.lkml.org/lkml/2022/4/1/39
- CFS bandwidth control (kernel doc; period vs burst; unnecessary throttling paper, up to 12 percent): https://grok.openbmc.org/xref/openbmc/linux/Documentation/scheduler/sched-bwc.rst , https://sol.sbc.org.br/index.php/sbac-pad/article/view/28260 , https://github.com/golang/go/issues/33803
- systemd.resource-control(5) (CPUWeight, CPUQuota, IOWeight, nice fallback): https://www.freedesktop.org/software/systemd/man/260/systemd.resource-control.html ; the CI-runner example CPUWeight=20 CPUQuota=85% IOWeight=20 is a forum answer (VERIFY): https://backiee.wasmer.app/https_unix_stackexchange_com/questions/494843/how-to-limit-a-systemd-service-to-play-nice-with-the-cpu
- HPA as a control system (dead band, stabilization windows as hysteresis, PI-like in production): https://dev.to/piyushjajoo/kubernetes-autoscaling-internals-hpa-and-vpa-under-the-hood-4e0g , https://dev.to/devgeist/kubernetes-through-control-theory-glasses-part-1-hpa-2kcj , https://napolitain.github.io/system-design/feedback-control-for-autoscaling-and-load-shedding

## 2. Build load: jobserver, caches, hermeticity
- GNU make fifo jobserver shared across builds (Yocto class; make 4.4; drop fixed -j; 12 percent on two builds, VERIFY): https://patchwork.yoctoproject.org/project/oe-core/patch/20240403070204.367470-2-martin@geanix.com/raw/ , https://www.mail-archive.com/openembedded-core@lists.openembedded.org/msg183036.html
- ccache shared two-level layout (WebKit wiki), setup: https://trac.webkit.org/wiki/WebKitFlatpakSDK/SpeedUpBuild?version=6 , https://oneuptime.com/blog/post/2026-03-02-how-to-set-up-ccache-for-faster-c-cpp-compilation-on-ubuntu/view
- sccache README (multi-level with backfill; absolute paths must match; one server per local store): https://docs.rs/crate/sccache/0.17.0/source/README.md ; sccache-dist setup: https://blog.davidedmundson.co.uk/blog/setting-up-distributed-compilations-with-sccache/
- icecream(7) (central scheduler, untrusted-network warning): https://dyn.manpages.debian.org/trixie/icecc/icecream.7.en.html
- Bazel hermeticity (undeclared inputs; a bad shared-cache entry reaches everyone): https://bazel.build/basics/hermeticity ; remote cache guide: https://visdom-maturity-matrix.virtuslab.com/guides/delivery/bazel-remote-caching-engflow
- Nix multi-user store (daemon, build users, trusted substituters, signing in the daemon's context): https://sources.debian.org/src/nix/2.3.7%2Bdfsg1-1/doc/manual/installation/multi-user.xml , https://tweag.io/blog/2019-11-21-untrusted-ci/

## 3. Admission, fair share, leases
- GNU sem(1) (counting semaphore, --id, --fg, --wait, --semaphore-timeout, stale semaphores): https://www.gnu.org/software/parallel/sem.html (mirror read: https://man.archlinux.org/man/sem.1.en)
- GitLab resource_group (one job per group across pipelines, process_mode): https://docs.gitlab.com/ci/resource_groups
- Buildkite controlling concurrency (groups, limits, gates in pairs): https://buildkite.com/docs/builds/controlling-concurrency , https://buildkite.com/blog/concurrency-gates
- Jenkins Lockable Resources (lock step, skip-if-locked, slot resources per agent): https://jenkins.io/doc/pipeline/steps/lockable-resources/ , https://dev.to/gpaciga/throttling-jenkins-pipelines-per-node-3kl4
- Slurm fair share, backfill, preemption (university docs): https://docs.icer.msu.edu/How_Jobs_are_Scheduled/ , https://hpc.ncsu.edu/RunningJobs/Priority.php , https://lucaberton.com/blog/slurm-job-scheduling-priority-fairshare/
- Kueue overview (suspend until quota fits, FIFO strategies, cohorts, preemption): https://kueue.sigs.k8s.io/docs/overview/ ; Volcano queues (reclaim, capacity plugin): https://volcano.sh/en/docs/queue_resource_management
- Leases, visibility timeouts, fencing, DLQ: https://oneuptime.com/blog/post/2026-07-22-sqs-visibility-timeouts-concurrent-processing/view , https://github.com/kyan9400/leasequeue , https://www.techinterview.org/post/3233460795/system-design-task-queue/
- Kleppmann, How to do distributed locking (2016; fencing tokens; efficiency vs correctness locks), and the FizzBee note that fencing narrows but does not close the window: https://dnitza.com/bookmarks/067fd0351446ceeb4b7a5d04c8a775d374900f5b , https://surfingcomplexity.blog/2025/03/03/locks-leases-fencing-tokens-fizzbee/ , https://redis.antirez.com/fundamental/redlock.md

## 4. Concurrent development on one repo
- DORA trunk-based development (branches last hours; small batches): https://dora.dev/capabilities/trunk-based-development/ ; the 24 h and three-branch figures are secondary (VERIFY): https://mergify.com/learn/trunk-based-development/short-lived-branches , https://octopus.com/blog/continuous-delivery-office-hours-e3
- Uber, Keeping Master Green at Scale (EuroSys 2019; speculation, conflict analyzer; 5 to 40 percent conflict figure from the author's slides): https://dl.acm.org/doi/10.1145/3302424.3303970 , https://sundaram.io/slides/eurosys19.pdf , https://www.masoud.io/docs/eurosys19.pdf ; CI at Scale: Lean, Green, and Fast (2025; 53 percent CI resources, 44 percent CPU, p95 wait 37 percent): https://arxiv.org/pdf/2501.03440 ; the 52 percent green and 10 percent reverts are secondary (VERIFY): https://parallel-coding-agents.pages.dev/monorepo-tooling
- Merge queues compared (Bors, Zuul, GitLab trains, GitHub queue, batching ~90 percent): https://docs.trunk.io/merge-queue/concepts-and-optimizations/batching , https://www.plushcap.com/content/graphite/blog/graphite-not-rocket-science-how-bors-and-googles-tap-inspired-modern-merge-queues , https://epage.github.io/dev/submit-queue , https://nirvanatech.com/blog/we-cut-pr-merge-time-by-92-heres-the-system-we-built-to-do-it ; the unstated assumption: https://amitkoth.com/merge-queue-test-oracle/
- Chromium CQ (dry run, full run, Mega-CQ; LUCI CV replacing CQ): https://chromium.googlesource.com/chromium/src/+/master/docs/infra/cq.md
- Merge-conflict prediction (267,657 merges, 744 repos; F1 0.57-0.68 on conflicts; same-method edits recall 82.67 percent): https://arxiv.org/pdf/1907.06274 ; ConE at Microsoft: https://arxiv.org/pdf/2101.06542
- Google's monorepo (Potvin and Levenberg, CACM 2016): https://alastairreid.github.io/RelatedWork/papers/potvin:cacm:2016

## 5. Test selection, flakes, culprits
- Affected sets (Nx, Turborepo, Pants, Bazel rdeps; shallow clones; undeclared inputs): https://mergify.com/learn/monorepo/ci , https://oneuptime.com/blog/post/2026-07-28-monorepo-only-affected-builds/view , https://github.com/Rani367/affected
- Google TAP transition-based selection (ICSE SEIP 2019), speculative cycles (ICST 2025), What Breaks Google (2023): https://mpapad.github.io/publications/pdfs/ICSE-SEIP2019.pdf , https://conf.researchr.org/details/icst-2025/icst-2025-industry/17/Speculative-Testing-at-Google-with-Transition-Prediction , https://conf.researchr.org/details/icst-2023/cciw-2023-papers/5/What-Breaks-Google-
- Predictive test selection (Meta figures via Launchable, VERIFY; probabilistic): https://launchableinc.com/eng/predictive-test-selection-efficient-software-test-execution , https://www.browserstack.com/guide/predictive-test-selection
- Flake quarantine (still run, never gate, temporary; Atlassian's tool): https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests , https://www.minware.com/guide/best-practices/flaky-test-quarantine , https://archman.dev/docs/testing-strategy/test-automation/flake-management-and-quarantine ; sharding cuts latency not cost: https://cicdpipelinecost.com/test-optimisation
- Chromium Findit (flake check first, bisect with try jobs, auto-revert compile culprits, notify the culprit's review): https://sites.google.com/chromium.org/cat/findit , https://sites.google.com/chromium.org/cat/findit/reliable-failure/waterfall-failures , https://sites.google.com/chromium.org/cat/findit/flaky-failures/overview

## 6. Outcomes, toil, automation
- Google SRE book, Part II principles (toil, the 50 percent cap, error budgets): https://sre.google/sre-book/part-II-principles/
- DORA four keys and the 2024 history (reliability added): https://dora.dev/guides/dora-metrics-four-keys , https://dora.dev/guides/dora-metrics/history/
- CI health metrics (p50/p95 not averages, queue time separate, main-branch filter; Trunk's time-in-queue): https://www.metabase.com/dashboards/ci-pipeline-health , https://www.harness.io/blog/top-continuous-integration-metrics-every-platform-engineering-leader-should-track , https://docs.trunk.io/merge-queue/administration/metrics.md
- Auto-remediation maturity and guardrails (vendor material): https://thegarnetwiki.pages.dev/sre/runbook-automation , https://hoop.dev/blog/what-auto-remediation-really-means/ , https://edgedelta.com/company/blog/zero-to-self-healing-a-napkin-sketch-for-sre-and-devops

## 7. Parallel agents on one repo (vendor-heavy, 2026)
- https://www.augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace , https://www.mindstudio.ai/blog/git-worktrees-parallel-ai-coding-agents , https://www.mindstudio.ai/blog/parallel-ai-coding-agents-git-worktrees , https://github.com/max-sixty/worktrunk
