import os
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(service="orders-api", version="1.0.0")


@app.get("/health")
def health():
    # Intentional demo bug: the deployment uses APP_ENV=production,
    # but this condition checks for the abbreviated value "prod".
    if os.getenv("APP_ENV", "development") == "prod":
        return jsonify(status="ok"), 200

    return jsonify(status="degraded", reason="production mode not detected"), 503
