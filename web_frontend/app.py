from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)
API_BACKEND_URL = os.getenv("API_BACKEND_URL", "http://127.0.0.1:8000/api/chat")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    session_id = request.json.get("session_id", "default_session")
    
    try:
        resp = requests.post(API_BACKEND_URL, json={"session_id": session_id, "message": user_msg})
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)