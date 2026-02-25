---
signal_name: Profiling Instrumentation
---

## Criterion-Specific Fix Guidance

- **Python (py-spy for continuous profiling)**: Install `py-spy` (`pip install py-spy`). Generate flame graphs from a running process: `py-spy record -o profile.svg --pid <PID>` or `py-spy record -o profile.svg -- python app.py`. For CI integration, run a load test and capture a profile simultaneously. py-spy requires no code changes and can attach to running processes.
- **Python (cProfile + snakeviz)**: For ad-hoc profiling, use the stdlib `cProfile`: `python -m cProfile -o profile.stats app.py`. Visualize with `snakeviz`: `pip install snakeviz; snakeviz profile.stats`. Add a profiling mode to your app: `if os.environ.get("PROFILE"): import cProfile; cProfile.run("main()", "profile.stats")`.
- **Python (Pyroscope continuous profiling)**: Install `pyroscope-io` (`pip install pyroscope-io`). Initialize in app startup: `import pyroscope; pyroscope.configure(application_name="my-service", server_address="http://pyroscope:4040")`. Pyroscope continuously collects profiling data with minimal overhead (<2% CPU) and provides a web UI for analyzing flame graphs over time.
- **TypeScript/JavaScript (Node.js --prof)**: Run with `node --prof app.js` to generate a V8 profiling log. Process with `node --prof-process isolate-*.log > profile.txt`. For programmatic control, use `v8-profiler-next`: `npm install v8-profiler-next` and start/stop profiling around specific code paths.
- **TypeScript/JavaScript (clinic.js)**: Install `clinic` (`npm install -g clinic`). Run `clinic doctor -- node app.js` to auto-detect performance issues, or `clinic flame -- node app.js` for flame graph generation. Clinic generates HTML reports that can be shared.
- **APM tools (Datadog APM / New Relic)**: If already using Datadog or New Relic for tracing, enable continuous profiling in the agent configuration. For Datadog: set `DD_PROFILING_ENABLED=true`. For New Relic: enable thread profiler in the agent config. These provide production profiling data alongside traces.
- **Parca (open-source continuous profiling)**: Deploy Parca server and agent. The agent uses eBPF for zero-instrumentation profiling of any language. Configure via `parca-agent.yaml` with target discovery. This is ideal for Kubernetes environments.
- **Flame graph generation in CI**: Add a CI step that runs a benchmark suite under a profiler and generates a flame graph artifact. Compare flame graphs between commits to detect performance regressions. Use `pytest-benchmark` (Python) or `benchmark.js` (Node.js) as the workload driver.

## Criterion-Specific Exploration Steps

- Check dependencies for profiling tools: `grep -E 'py-spy|pyroscope|snakeviz|clinic|v8-profiler|pprof' pyproject.toml package.json`
- Search for profiling configuration: `grep -rn 'pyroscope\|DD_PROFILING\|profiling.*enabled\|cProfile\|--prof' src/ .env* Dockerfile`
- Look for APM configuration with profiling enabled: `grep -rn 'profiling\|continuous_profiler\|thread_profiler' newrelic.ini datadog.yaml .env*`
- Check for flame graph generation scripts: `grep -rn 'flame\|flamegraph\|py-spy\|clinic' Makefile package.json scripts/`
- Look for benchmark suites: `grep -rn 'benchmark\|pytest-benchmark\|bench' pyproject.toml package.json tests/`
- Check Kubernetes manifests for Parca or Pyroscope agent deployments

## Criterion-Specific Verification Steps

- Confirm a profiling tool is installed and can be invoked: `py-spy record --help` or `npx clinic --help`
- Generate a profile from a running instance or test workload and verify a flame graph or profile report is produced
- For continuous profiling (Pyroscope/Parca/Datadog), verify the profiling agent is running and data is visible in the profiling UI
- For APM-based profiling, check the APM dashboard for profiling data (CPU and memory breakdowns)
- Verify profiling has acceptable overhead: compare request latency with and without profiling enabled (should be <5% impact for continuous profilers)
- If using CI flame graph comparison, verify the CI step produces an artifact and detects intentional performance changes
