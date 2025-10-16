from flask import Flask, jsonify
from rules.consistency import bp as consistency_bp
from rules.clarity import bp as clarity_bp
from rules.extensibility import bp as extensibility_bp
from rules.naming import bp as naming_bp

app = Flask(__name__)

app.register_blueprint(consistency_bp, url_prefix="/api/consistency")
app.register_blueprint(clarity_bp, url_prefix="/api/clarity")
app.register_blueprint(extensibility_bp, url_prefix="/api/extensibility")
app.register_blueprint(naming_bp, url_prefix="/api/naming")

@app.get("/")
def index():
    return jsonify({
        "message": "Flask REST API Best Practices — per-rule demo",
        "rules": {
            "consistency": "/api/consistency",
            "clarity": "/api/clarity",
            "extensibility": "/api/extensibility",
            "naming": "/api/naming"
        }
    })
