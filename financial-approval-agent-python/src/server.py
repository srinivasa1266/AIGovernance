# src/server.py
# Flask server — serves the frontend and streams agent events via SSE

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, Response, send_from_directory
from dotenv import load_dotenv
from src.agent import run_approval_agent

load_dotenv()

app = Flask(__name__, static_folder=str(Path(__file__).parent.parent / "public"))

PUBLIC_DIR = Path(__file__).parent.parent / "public"


# ── Serve frontend ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return jsonify({
        "status":      "ok",
        "model":       "claude-sonnet-4-20250514",
        "api_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
    })


# ── Main approval endpoint — streams events via SSE ───────────────────────
@app.post("/api/approve")
def approve():
    data = request.get_json()

    required = ["vendor", "amount", "risk_score", "role", "category", "notes", "budget"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if not os.getenv("ANTHROPIC_API_KEY"):
        return jsonify({"error": "ANTHROPIC_API_KEY not set in environment"}), 500

    po = {
        "vendor":     data["vendor"],
        "amount":     float(data["amount"]),
        "risk_score": int(data["risk_score"]),
        "role":       data["role"],
        "category":   data["category"],
        "notes":      data["notes"],
        "budget":     float(data["budget"]),
    }

    def generate():
        def on_event(event):
            nonlocal _buf
            event_type = event.get("type")
            if event_type == "step":
                payload = {"label": event["label"], "content": event["content"], "kind": event["kind"]}
                _buf.append(f"event: step\ndata: {json.dumps(payload)}\n\n")
            elif event_type == "result":
                _buf.append(f"event: result\ndata: {json.dumps(event)}\n\n")

        _buf = []

        # We run the agent and collect events, yielding as they arrive
        # Using a queue-based approach for true streaming
        import queue
        import threading

        q = queue.Queue()

        def on_event_queue(event):
            q.put(event)

        def run():
            try:
                run_approval_agent(po, on_event_queue)
            except Exception as e:
                q.put({"type": "error", "message": str(e)})
            finally:
                q.put(None)  # sentinel

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        while True:
            event = q.get()
            if event is None:
                break

            event_type = event.get("type")
            if event_type == "step":
                payload = {"label": event["label"], "content": event["content"], "kind": event["kind"]}
                yield f"event: step\ndata: {json.dumps(payload)}\n\n"
            elif event_type == "result":
                yield f"event: result\ndata: {json.dumps(event)}\n\n"
            elif event_type == "error":
                yield f"event: error\ndata: {json.dumps({'message': event['message']})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    api_key = os.getenv("ANTHROPIC_API_KEY")

    print("\n🤖  Financial Approval Agent (Python) running")
    print(f"    URL:      http://localhost:{port}")
    print(f"    API key:  {'✓ set' if api_key else '✗ missing — set ANTHROPIC_API_KEY in .env'}")
    print(f"    Model:    claude-sonnet-4-20250514\n")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
