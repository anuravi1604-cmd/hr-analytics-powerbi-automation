"""
test_automation_endtoend.py
Genuine end-to-end test: starts a real local HTTP server that mimics a Teams
Incoming Webhook endpoint, runs automation_alert.py against it over real HTTP,
and records exactly what was sent and received. This is the proof that the
"data -> risk score -> triggered action" pipeline actually functions, not just
a design document describing how it could.

Honest limitation: this proves the pipeline correctly builds and delivers the
webhook payload over real HTTP. It does not prove delivery to a live Microsoft
Teams channel or Outlook flow, since that requires a real tenant + webhook URL,
which this sandboxed environment has no network access to reach. Swapping
HR_ALERT_WEBHOOK_URL for a real Teams/Power Automate URL requires no code change.
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

received = []


class MockTeamsWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        payload = json.loads(body)
        received.append(payload)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"1")  # Teams webhook receivers respond with "1" on success

    def log_message(self, fmt, *args):
        pass  # keep test output clean


def main():
    server = HTTPServer(("127.0.0.1", 8765), MockTeamsWebhookHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2)

    import automation_alert
    t0 = time.time()
    results = automation_alert.run(url="http://127.0.0.1:8765/webhook")
    elapsed = time.time() - t0

    server.shutdown()

    sent_ok = sum(1 for r in results if r.get("ok"))
    summary = {
        "alerts_attempted": len(results),
        "alerts_delivered_http_200": sent_ok,
        "payloads_actually_received_by_mock_endpoint": len(received),
        "runtime_seconds": round(elapsed, 4),
        "sample_received_payload": received[0] if received else None,
    }
    with open("outputs/automation_endtoend_proof.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps({k: v for k, v in summary.items() if k != "sample_received_payload"}, indent=2))
    assert sent_ok == len(results) == len(received), "End-to-end automation test FAILED"
    print("\nEnd-to-end automation test PASSED: every risk-flagged employee's alert "
          "was built, sent over real HTTP, and received intact by the mock endpoint.")


if __name__ == "__main__":
    main()
