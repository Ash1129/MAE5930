# Apache Airflow engineering guide

Apply these recommendations when completing the scaffold. The exported workflow does not automatically implement these protections.

## Airflow data intervals, task contracts and dependencies

### Claims

- In time-based interval scheduling, the logical date identifies the interval,
  not actual execution time. Runs generally start after the interval ends.
  Manually triggered runs need not derive their interval from the supplied
  logical date. [airflow-2026-dag-runs §Data Interval; §Manual Triggering and Data Intervals]
- A successful producing task can emit an asset update. Failed or skipped
  producers do not emit that update. A list of asset dependencies waits for all
  listed assets to update since the previous consumer run; repeated updates can
  coalesce into one run. [airflow-2026-assets §Schedule Dags with assets; §Multiple assets]
- ExternalTaskSensor waits for an external task at a specific logical date.
  `execution_delta` can align differently timed runs, and allowed/failed states
  define the result. Combining closely related tasks into one DAG may be simpler.
  [airflow-2026-external-sensor §Cross-Dag Dependencies; §ExternalTaskSensor]
- XComs are intended for small serializable messages between task instances.
  Tasks can run on different machines. XCom data from an unsuccessful task is
  cleared on retry and is not durable retry state.
  [airflow-2026-xcoms §XComs; §Object Storage XCom Backend]
- Airflow recommends shared storage for large intermediate data and passing its
  location between tasks, rather than relying on worker-local files.
  [airflow-2026-best-practices §Communication]

### What this means for the guide

The following is guide synthesis for the Airflow 3.3.2 documentation reviewed
here; verify compatibility with the deployed core and provider versions.

- Specify the input partition, expected schema, output location and completeness
  checks for each task. Pass small references and counts between tasks; persist
  bulk results in storage every relevant worker can access.
- Choose an explicit dependency mechanism. Use task edges within a DAG, asset
  scheduling for published data updates, or an external sensor for a particular
  upstream run. A daily timer alone does not establish data readiness.
- Define what "ready" means before publishing an asset event: validation and
  complete output publication should precede it. Asset notification alone does
  not establish matching business partitions; validate the intended partition
  from the event or data contract before consuming it.
- For an external sensor, document upstream DAG/task identity, date alignment,
  success/failure policy and wait limit. Test different upstream cadences rather
  than assuming two daily schedules refer to the same interval.
- For manual runs, declare how the requested business date maps to input data.
  Do not silently substitute the current date when the interval is unclear.
- Acceptance cases: late upstream data, failed or skipped producer, mismatched
  partitions, empty-but-valid input, malformed schema and a downstream task on
  another worker. Assert the exact partition consumed and ensure incomplete
  outputs are not advertised as ready. These are proposed tests, not executed
  Airflow results.

### Source links

- [airflow-2026-dag-runs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)
- [airflow-2026-assets](https://airflow.apache.org/docs/apache-airflow/3.3.2/authoring-and-scheduling/asset-scheduling.html)
- [airflow-2026-external-sensor](https://airflow.apache.org/docs/apache-airflow-providers-standard/stable/sensors/external_task_sensor.html)
- [airflow-2026-xcoms](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/xcoms.html)
- [airflow-2026-best-practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)


## Airflow safe retries, backfills and failure signals

### Claims

- Tasks should publish complete results and produce the same outcome on rerun.
  Airflow recommends partition-specific reads/writes and UPSERT instead of
  duplicate-producing INSERT operations. [airflow-2026-best-practices §Creating a task]
- `execution_timeout` bounds each task execution. For rescheduling sensors,
  `timeout` bounds the overall wait; retries do not reset it. AirflowFailException
  can fail without using remaining retries.
  [airflow-2026-tasks §Timeouts; §Special Exceptions]
- Backfill creates historical runs for time-based schedules. Reprocessing policy
  distinguishes missing, failed and completed runs. Backfill concurrency is
  controlled independently of the DAG's active-run limit. A dry run previews
  candidate dates, not task outputs. [airflow-2026-backfill §Control over data reprocessing; §Concurrency control; §Dry run]
- Catchup schedules missed intervals when enabled. DAG-run status depends on
  leaf tasks: a successful `all_done` leaf can hide an earlier failure.
  [airflow-2026-dag-runs §Catchup; §Dag Run Status]
- Callbacks respond to worker-driven state changes, not manual UI/CLI status
  changes. Callback failures appear in DAG-processor logs in the reviewed
  version. [airflow-2026-callbacks §Callbacks]

### What this means for the guide

These recommendations interpret the Airflow 3.3.2 docs. They are not a promise
of exactly-once delivery or automatic rollback across external systems.

- Give retryable work a finite attempt count and delay, and distinguish temporary
  service failures from invalid input or credentials. Specify both execution and
  dependency-wait limits; exhausting the wait must have an owner and recovery path.
- Design writes so replaying a partition does not duplicate its business effect.
  For messages, purchases or agent handoffs, verify the receiving service's replay
  contract before retrying. Airflow retry configuration cannot supply a guarantee
  the destination does not provide. Investigate ambiguous outcomes before resend.
- Keep catchup an explicit choice. Before a backfill, review its date range,
  reprocessing policy, resource limits and external actions. Start with a small
  historical interval and compare results before widening the run. The preview
  does not prove that historical inputs still exist or that replay is safe.
- Test failure propagation through branches and cleanup tasks. Decide which
  terminal states indicate a usable result; do not let housekeeping success stand
  in for successful data processing.
- Alerts should identify the DAG, run, task, attempt and relevant partition while
  avoiding sensitive payloads. Test by causing a controlled worker failure, not
  by manually marking a task failed. Verify delivery and inspect callback logs
  when the task fails without an alert.
- Acceptance cases: retry after a partial write, exhausted retries, missing
  upstream data, a repeated historical interval, an earlier failure followed by
  successful cleanup, and an alert-service outage. Check destination records and
  final run state. These tests still need execution in an isolated deployment.

### Source links

- [airflow-2026-best-practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [airflow-2026-tasks](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/tasks.html)
- [airflow-2026-backfill](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html)
- [airflow-2026-dag-runs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)
- [airflow-2026-callbacks](https://airflow.apache.org/docs/apache-airflow/3.3.2/administration-and-deployment/logging-monitoring/callbacks.html)


## Airflow testing, credentials and production capacity

### Claims

- DAG files are parsed repeatedly. Airflow advises keeping expensive computation,
  database access and network work out of top-level code, and testing imports in
  an environment matching the scheduler. [airflow-2026-best-practices §Top level Python Code; §Dag Loader Test]
- Airflow 3 authors should use the public `airflow.sdk` interface rather than
  internal modules or direct metadata-database access.
  [airflow-2026-public-interface §Using Airflow Public Interfaces]
- `dag.test()` executes real tasks. It defaults to local serialized execution;
  `use_executor` enables the configured executor. The reviewed version requires
  an initialized metadata database and a serializable DAG in a configured
  bundle. Marking selected tasks successful skips their behavior.
  [airflow-2026-debug §Testing Dags with dag.test(); §Conditionally skipping tasks]
- Connections and Variables can resolve from secret backends, environment or
  metastore. Lookup precedence and duplicate keys matter; the UI only displays
  metastore values. [airflow-2026-secrets §Secrets Backend; §Search path]
- Pools limit task concurrency; `pool_slots` assigns different weights. Queued
  tasks wait for available capacity. [airflow-2026-pools §Pools; §Using multiple pool slots]
- Deferrable operators release worker slots while waiting and require a
  triggerer. Deferred tasks do not occupy pool slots by default, unless the pool
  is configured otherwise. Rescheduling sensors also release workers between
  checks. [airflow-2026-deferring §Deferrable Operators & Triggers; §Using Deferrable Operators]

### What this means for the guide

This chapter uses Airflow 3.3.2 documentation. The external sensor reference in
R01 uses standard provider 1.20.0; check compatibility rather than assuming every
Airflow 3 installation exposes identical features.

- Keep orchestration definitions lightweight and move work into tasks. Record the
  core, Python and provider versions used for validation; an import passing in an
  unrelated developer environment is insufficient.
- Test in layers: pure business-logic tests, DAG import and dependency assertions,
  an isolated `dag.test()` run, then staging with the deployed executor and real
  dependency mechanism. Syntax compilation does not execute imports or validate
  scheduler behavior. Skipped sensors do not count as tested dependencies.
- Supply test credentials and safe destinations before executing a DAG test.
  Store authentication in Connections or the configured secret backend, keeping
  secret values out of DAG source and generated examples. Verify lookup in the
  worker environment, especially when a key exists in several stores.
- Size pools for the downstream system's capacity and limit overlapping runs.
  Concurrency limits are not requests-per-second limits; add destination-specific
  pacing where needed. Test whether deferred tasks should retain a pool slot for
  the external resource they still occupy.
- Verify the triggerer before choosing deferrable waits. Observe queue time,
  task failures and wait behavior under load, then adjust capacity with evidence.
- Acceptance cases: missing provider, unavailable credentials, worker restart,
  pool saturation and unavailable triggerer. Preserve failure visibility and
  verify output correctness after recovery. The exported scaffold and this guide
  do not demonstrate a production-ready deployment or completed live tests.

### Source links

- [airflow-2026-best-practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [airflow-2026-public-interface](https://airflow.apache.org/docs/apache-airflow/3.3.2/public-airflow-interface.html)
- [airflow-2026-debug](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/debug.html)
- [airflow-2026-secrets](https://airflow.apache.org/docs/apache-airflow/3.3.2/security/secrets/secrets-backend/index.html)
- [airflow-2026-pools](https://airflow.apache.org/docs/apache-airflow/3.3.2/administration-and-deployment/pools.html)
- [airflow-2026-deferring](https://airflow.apache.org/docs/apache-airflow/3.3.2/authoring-and-scheduling/deferring.html)
