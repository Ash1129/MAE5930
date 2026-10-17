# Start here: Transformer Capacity Monitor (Tompkins County)

A fixed-rules tool that logs transformer loads, checks load stability with control charts, measures
capacity headroom against each transformer's rated maximum, applies the heat-pump growth forecast,
and prepares a report that a named grid-planning reviewer approves. Every statistic and review decision is a fixed rule; the only AI is an optional, off-by-default rewrite of alert and summary text for display. It never changes
equipment or operating settings.

## Everyday use (three steps)

1. **Open the tool.** On a Mac, double-click `Start Capacity Monitor.command` (or run `./scripts/start_app.sh` and
   `./scripts/start_airflow.sh`). On Windows, double-click `Start Capacity Monitor.bat`, or from this folder run
   `.venv\Scripts\python.exe -m webapp.app`. Your browser opens http://127.0.0.1:5055 on the **Map**: every transformer
   as a dot, green for within limits, amber for needing review and red for needing an inspection now; click an amber or red dot for its numbers and
   **Open full review**. Pick a district on the left to zoom in and see load by hour (recorded) or by month (a labeled model). Scheduled runs happen on their own on Monday, Wednesday and Friday at 06:00 when the Airflow scheduler is running (macOS or Linux; on Windows the review app runs the same analysis when you press **Run now**). The **Dashboard** shows county/district summaries, aggregate control charts and a review queue. Scheduler controls and run history are available in the app.
2. **Review the exceptions.** Open the period, press **Review** on each flagged transformer, read the
   checklist beside the chart and source readings, then choose **Approve conclusion**, **Request changes**
   or **Reject** (with a note). One case at a time; nothing is batch-approved.
3. **Approve and finalize the report.** When every exception has a disposition, press
   **Approve and finalize report**. The final report (HTML, Markdown, JSON) is in
   `data/reports/<period end>/` and linked on the period page. Share it with the grid-planning team.

## Reopen, stop, recover

- **Reopen:** http://127.0.0.1:5055 while the tool is running; otherwise double-click the Start launcher again
  (`.command` on a Mac, `.bat` on Windows).
- **Stop:** double-click `Stop Capacity Monitor.command` on a Mac, or `Stop Capacity Monitor.bat` on Windows
  (or `./scripts/stop.sh` on a Mac).
- **Pause scheduled runs:** the **Pause scheduled runs** button on the dashboard (Resume to continue).
- **A run failed:** the dashboard and the Alerts page explain in plain words what happened and what to do
  (for example a missing feed or a boundary file for the wrong period). With AI explanations turned on in
  Setup, Claude also rewrites each alert. Fix the feed in `data/feeds/` and
  press **Run now** for the same period end date; the rerun replaces that period's draft.
- **Something looks stuck:** on a Mac, `./scripts/status.sh` shows what is running and `./scripts/stop.sh` then the
  Start launcher restarts everything. On Windows, run `Stop Capacity Monitor.bat` and then the Start launcher.
  Logs are in `logs/`.

## Feeding it real data

The tool reads four files from `data/feeds/` (columns are listed on the Setup page):
`readings.csv`, `assets.csv`, `boundaries.geojson`, `heat_pump_forecast.csv`.
The files there now are **synthetic sample data** for 500 made-up transformers. The 2026-10-15 readings, the review database, and that period's report are already in git, so opening the app shows the finished analysis (including Inspect now) without running it again. Replace the feeds with exports from your meter, asset, GIS and forecast systems, keep the same columns, and run a period when you want a new one.

Thresholds (Cpk review level, forecast margin, chart rules, schedule) live in `rules/playbook.json`
and `rules/decision-table.csv`; record who approved any change.
