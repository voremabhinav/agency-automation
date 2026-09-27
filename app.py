from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from db import get_db_connection
from pipeline import run_pipeline
from routes.lead_routes import lead_bp
from routes.admin_routes import admin_bp
from routes.notification_routes import notification_bp

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

leads_store = []

app.register_blueprint(lead_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notification_bp)

# --- NEW DATABASE INSERT FUNCTION ---
def save_lead_to_db(name, email, phone, ai_score, budget, suggested_reply, status="New"):
    """Inserts a fully scored lead into the MySQL database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO leads (name, email, phone, ai_score, budget, suggested_reply, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, phone, ai_score, budget, suggested_reply, status))
        conn.commit()
        
        print(f"[SUCCESS] Lead '{name}' saved to MySQL database.")

        cursor.close()
        conn.close()
    except Exception as err:
        print(f"[ERROR] Database insertion failed: {err}")

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

# --- UPDATED PIPELINE ROUTE ---
@app.route("/api/run-pipeline", methods=["POST", "GET"])
def trigger_pipeline():
    custom_text = None
    if request.is_json and request.json:
        custom_text = request.json.get("email_text")

    # 1. Run the AI pipeline
    lead = run_pipeline(custom_text)
    
    # 2. Extract ALL data for the database
    name = lead.get("client_name", "Unknown")
    email = lead.get("client_email", "unknown_email@example.com")
    phone = lead.get("client_phone", "0000000000")
    ai_score = lead.get("ml_score", 0)
    budget = str(lead.get("budget", "Not Specified"))
    suggested_reply = lead.get("suggested_reply", "No reply generated.")

    # 3. Save to MySQL
    save_lead_to_db(name, email, phone, ai_score, budget, suggested_reply)

    leads_store.append(lead)
    return jsonify({
        "success": True,
        "lead": lead,
        "total_leads": len(leads_store)
    })

@app.route("/api/leads", methods=["GET"])
def get_leads():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        
        # Explicitly select all columns including suggested_reply
        cursor.execute("SELECT id, name, email, phone, ai_score, budget, suggested_reply, status FROM leads ORDER BY id DESC")
        db_leads = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"leads": db_leads})
    except Exception as e:
        print(f"[ERROR] Failed to fetch leads from database: {e}")
        return jsonify({"error": str(e), "leads": []}), 500

if __name__ == "__main__":
    app.run(debug=True)