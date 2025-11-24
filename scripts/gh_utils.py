import os, requests, json, sys

GITHUB_API = "https://api.github.com"
REPO = os.getenv("REPO", "gtsurkav-sudo/JOJIAI")
GH_TOKEN = os.getenv("GH_TOKEN")

def _headers():
    if not GH_TOKEN:
        # fall back to GitHub Actions token (GITHUB_TOKEN) or unauth (read only)
        token = os.getenv("GITHUB_TOKEN", "")
    else:
        token = GH_TOKEN
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def create_issue(title: str, body: str, labels=None):
    labels = labels or ["joji", "automation"]
    url = f"{GITHUB_API}/repos/{REPO}/issues"
    payload = {"title": title, "body": body, "labels": labels}
    r = requests.post(url, headers=_headers(), json=payload)
    if r.status_code >= 400:
        print(f"[WARN] create_issue failed: {r.status_code} {r.text[:200]}", file=sys.stderr)
        return None
    return r.json()

def comment_pr(pr_number: int, body: str):
    url = f"{GITHUB_API}/repos/{REPO}/issues/{pr_number}/comments"
    r = requests.post(url, headers=_headers(), json={"body": body})
    if r.status_code >= 400:
        print(f"[WARN] comment_pr failed: {r.status_code} {r.text[:200]}", file=sys.stderr)
        return None
    return r.json()

def list_recent_issues(limit=10):
    url = f"{GITHUB_API}/repos/{REPO}/issues"
    r = requests.get(url, headers=_headers(), params={"per_page": limit, "state": "all"})
    if r.status_code >= 400:
        print(f"[WARN] list_recent_issues failed: {r.status_code} {r.text[:200]}", file=sys.stderr)
        return []
    return r.json()
