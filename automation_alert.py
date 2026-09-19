"""
automation_alert.py
Sends a real HTTP POST, in Microsoft Teams "Incoming Webhook" MessageCard format,
for every High-risk ACTIVE employee. Point WEBHOOK_URL at:
  - a real Teams channel's Incoming Webhook URL, or
  - a Power Automate "When a HTTP request is received" trigger URL
and this fires for real with no code changes — the payload format is the real
MS Teams connector card schema.

WEBHOOK_URL is read from an environment variable so no real endpoint is hardcoded here.
If it isn't set, this script targets a local mock server (see test_automation_endtoend.py)
so the whole pipeline can still be proven to work end-to-end without live credentials.
"""
import json
import os
import urllib.request
import urllib.error

WEBHOOK_URL = os.environ.get("HR_ALERT_WEBHOOK_URL", "http://127.0.0.1:8765/webhook")


def build_teams_card(employee: dict) -> dict:
    """Real MS Teams Incoming Webhook MessageCard payload."""
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "D9534F",
        "summary": f"Retention risk alert: {employee['EmployeeID']}",
        "sections": [{
            "activityTitle": "⚠ High Attrition-Risk Employee Flagged",
            "facts": [
                {"name": "Employee ID", "value": employee["EmployeeID"]},
                {"name": "Department", "value": employee["Department"]},
                {"name": "Role", "value": employee["Role"]},
                {"name": "Risk Score", "value": f"{employee['RiskScore']} / 100"},
                {"name": "Tenure", "value": f"{employee['TenureYears']} years"},
                {"name": "Overtime", "value": employee["OverTime"]},
                {"name": "Months Since Promotion", "value": str(employee["MonthsSincePromotion"])},
            ],
            "markdown": True,
        }],
    }


def send_alert(payload: dict, url: str = WEBHOOK_URL, timeout: float = 5.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status, "body": resp.read().decode()}
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e)}


def run(csv_path="outputs/high_risk_active_employees.csv", url: str = WEBHOOK_URL, limit=None):
    import pandas as pd
    df = pd.read_csv(csv_path)
    if limit:
        df = df.head(limit)
    results = []
    for _, row in df.iterrows():
        card = build_teams_card(row.to_dict())
        result = send_alert(card, url=url)
        results.append({"EmployeeID": row["EmployeeID"], **result})
    return results


if __name__ == "__main__":
    results = run()
    sent_ok = sum(1 for r in results if r.get("ok"))
    print(f"Attempted {len(results)} alerts -> {sent_ok} delivered successfully to {WEBHOOK_URL}")
    with open("outputs/automation_run_log.json", "w") as f:
        json.dump(results, f, indent=2)
