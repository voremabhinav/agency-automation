from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from db import get_db_connection
from pipeline import run_pipeline
from routes.lead_routes import lead_bp
from routes.admin_routes import admin_bp
from routes.notification_routes import notification_bp

app = Flask(__name__)
CORS(app)

leads_store = []

app.register_blueprint(lead_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notification_bp)


@app.route("/")
def home():
    return send_file("reports_and_analysis.html")


@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()

        if connection.is_connected():
            connection.close()
            return "MySQL connection successful!"

    except Exception as e:
        return f"MySQL connection failed: {str(e)}"


@app.route("/api/run-pipeline", methods=["POST", "GET"])
def trigger_pipeline():
    custom_text = None
    if request.is_json and request.json:
        custom_text = request.json.get("email_text")

    lead = run_pipeline(custom_text)
    leads_store.append(lead)
    return jsonify({
        "success": True,
        "lead": lead,
        "total_leads": len(leads_store)
    })


@app.route("/api/leads", methods=["GET"])
def get_leads():
    return jsonify({"leads": leads_store})


if __name__ == "__main__":
    app.run(debug=True)