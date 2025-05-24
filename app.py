from flask import Flask, render_template, jsonify
import secrets

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/data")
def data():
    key = secrets.token_hex(32)  # 256 bits = 32 bytes = 64 hex chars
    return jsonify({"key": key})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)