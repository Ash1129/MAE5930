# Publish the review app to Posit Connect

Judges need a public URL. Publish the Flask app only. Airflow does not run on Connect;
**Run now** on the Map does the same analysis.

The publisher key is handed out at the event. Put it in the GitHub repo secrets
`CONNECT_SERVER` and `CONNECT_API_KEY` (Settings, Secrets and variables, Actions).
Never commit it. A gitignored `.env` is only for a manual `./deployme.sh` from your machine.

## GitHub Actions

`.github/workflows/deploy-flask.yml` republishes on every push to `main` once those two
secrets exist. `manifest.json` is written on a developer machine and committed. Actions
ships that file unchanged.

In the Connect app's Vars panel, set `CAPMON_SECRET` to a long random value. The code
default is only for localhost.

The bundle includes the committed feeds, the review database, and the 2026-10-15 report,
so the map opens without Run now. A later publish replaces the server's database, including
any reviews clicked online.

## Manual publish

```bash
python -m pip install rsconnect-python
cp .env.example .env
./manifestme.sh
./deployme.sh
```

On Windows use `.\deployme.ps1` after filling in `.env`.
