import os, json, datetime

TEMPLATE = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>JOJI Oi — Light Integration Report</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .ok    { color: #166534; background: #ecfdf5; padding: 2px 8px; border-radius: 999px; }
    .warn  { color: #92400e; background: #fffbeb; padding: 2px 8px; border-radius: 999px; }
    .bad   { color: #991b1b; background: #fef2f2; padding: 2px 8px; border-radius: 999px; }
    pre { background: #f9fafb; padding: 12px; border-radius: 8px; overflow-x: auto; }
    h1 { margin-top: 0; }
  </style>
</head>
<body>
  <h1>JOJI Oi — Light Integration Report</h1>
  <div class="card">
    <b>Generated:</b> {{generated}} (UTC)
  </div>
  <div class="card">
    <h2>Pipeline Status</h2>
    <p><b>Repo:</b> {{repo}}</p>
    <p><b>Pipeline:</b> {{pipeline_id}} @ {{pipeline_version}}</p>
    <p><b>Status:</b> <span class="{{badge_class}}">{{state}}</span></p>
    <details>
      <summary>Details</summary>
      <pre>{{details}}</pre>
    </details>
  </div>
  <div class="card">
    <h2>What's Included (Light)</h2>
    <ul>
      <li>Issue creation on failures/unknown states</li>
      <li>Optional PR comment update</li>
      <li>Static HTML report (this file)</li>
      <li>Simple hourly schedule via GitHub Actions</li>
    </ul>
  </div>
</body>
</html>
"""

def render(template: str, ctx: dict) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace("{{"+k+"}}", str(v))
    return out

def main():
    status_path = "docs/status.json"
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            s = json.load(f)
    else:
        s = {
            "ts_utc": datetime.datetime.utcnow().isoformat(),
            "repo": "gtsurkav-sudo/JOJIAI",
            "pipeline_id": "N/A",
            "pipeline_version": "N/A",
            "state": "unknown",
            "details": {}
        }
    badge = "ok" if s.get("state") in ("success","succeeded","completed") else ("bad" if s.get("state") in ("failed","error") else "warn")
    html = render(TEMPLATE, {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "repo": s.get("repo",""),
        "pipeline_id": s.get("pipeline_id",""),
        "pipeline_version": s.get("pipeline_version",""),
        "state": s.get("state","unknown"),
        "details": json.dumps(s.get("details",{}), indent=2),
        "badge_class": badge
    })
    os.makedirs("docs", exist_ok=True)
    with open("docs/joji_report.html","w",encoding="utf-8") as f:
        f.write(html)
    print("Report generated at docs/joji_report.html")

if __name__ == "__main__":
    main()
