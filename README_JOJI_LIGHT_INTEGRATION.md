# JOJI Oi — Light GitHub Integration Kit

This lightweight kit provides:
- ✅ Auto-create GitHub Issues when pipeline state is `failed`/`unknown`
- ✅ Optional PR comment updates
- ✅ Hourly monitor via GitHub Actions
- ✅ Static HTML status report in `docs/joji_report.html`

## How to use (1 minute)

1) Add two repository secrets (optional but recommended):
   - `ABACUS_API_KEY` (for querying Abacus pipeline status; otherwise state becomes `unknown` but still works)
   - `GITHUB_TOKEN` (automatically provided in Actions; no extra setup needed for basic operations)

2) Commit this folder to your repo root preserving structure.

3) Start the workflow manually (Actions → **JOJI Oi - Light Pipeline Monitor** → Run):
   - Inputs (optional): `repo`, `pipeline_id`, `pipeline_version`, `pr_number`

4) After the run, download the artifact `joji-light-report` or open `docs/joji_report.html` from the workspace.

## Local run (without Actions)

- `python scripts/monitor.py`   → produces `docs/status.json` and issues/comments (if `GH_TOKEN` set)
- `python scripts/generate_report.py` → renders `docs/joji_report.html`

## Notes

- This kit avoids heavy dashboards and complex auth flows.
- You can later evolve it into a full dashboard by adding endpoints and richer data sources.
