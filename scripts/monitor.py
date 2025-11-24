# Light monitor: tries Abacus to fetch last pipeline run; on failure falls back to neutral status.
import os, json, time
from datetime import datetime

from gh_utils import create_issue, comment_pr

REPO = os.getenv("REPO", "gtsurkav-sudo/JOJIAI")
PIPELINE_ID = os.getenv("PIPELINE_ID", "")
PIPELINE_VERSION = os.getenv("PIPELINE_VERSION", "")
PR_NUMBER = os.getenv("PR_NUMBER", "")

status = {
    "ts_utc": datetime.utcnow().isoformat(),
    "repo": REPO,
    "pipeline_id": PIPELINE_ID,
    "pipeline_version": PIPELINE_VERSION,
    "source": "light-monitor",
    "state": "unknown",
    "details": {}
}

def try_abacus_status():
    try:
        from abacusai import ApiClient
        cli = ApiClient()
        # Heuristic: look for a method to get runs
        run = None
        for name in ("list_pipeline_runs","get_pipeline_runs","describe_pipeline","describe_pipeline_run"):
            if hasattr(cli, name):
                fn = getattr(cli, name)
                try:
                    out = fn(pipeline_id=PIPELINE_ID) if "pipeline_id" in fn.__code__.co_varnames else fn(PIPELINE_ID)
                    run = out[0] if isinstance(out, (list, tuple)) and out else out
                    break
                except Exception:
                    continue
        if run:
            # Best-effort field mapping
            s = getattr(run, "status", None) or getattr(run, "state", None) or run.get("status") if isinstance(run, dict) else None
            rid = getattr(run, "pipeline_run_id", None) or run.get("pipeline_run_id") if isinstance(run, dict) else None
            status["state"] = str(s or "unknown").lower()
            status["details"]["pipeline_run_id"] = rid
            return True
        return False
    except Exception as e:
        status["details"]["abacus_error"] = str(e)
        return False

ok = False
if PIPELINE_ID:
    ok = try_abacus_status()

# Fallback
if not ok:
    status["state"] = "unknown"

# If failure or unknown -> create an issue (idempotent-ish by title)
title = f"[JOJI Light Monitor] Pipeline {status['pipeline_id'] or 'N/A'} state: {status['state'].upper()}"
body = (
    f"**Time (UTC):** {status['ts_utc']}\n"
    f"**Repo:** {status['repo']}\n"
    f"**Pipeline:** {status['pipeline_id']} @ {status['pipeline_version']}\n"
    f"**State:** `{status['state']}`\n"
    f"**Details:** `{json.dumps(status['details'])}`\n"
    "\n_Auto-created by JOJI Light Monitor._"
)
if status["state"] in ("failed","unknown","error"):
    create_issue(title, body, labels=["joji","monitor","needs-triage"])

# Optional PR comment
if PR_NUMBER:
    try:
        prn = int(PR_NUMBER)
        comment_pr(prn, f"JOJI Light Monitor — pipeline state: **{status['state']}** (UTC {status['ts_utc']})")
    except Exception:
        pass

# Store status.json for report
os.makedirs("docs", exist_ok=True)
with open("docs/status.json", "w", encoding="utf-8") as f:
    json.dump(status, f, indent=2)
print("STATUS:", json.dumps(status))
