from flask import Flask
from db import get_db_connection
from routes.lead_routes import lead_bp
from routes.admin_routes import admin_bp
from routes.notification_routes import notification_bp

app = Flask(__name__)

app.register_blueprint(lead_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notification_bp)


@app.route("/")
def home():
    return "Agency Automation CRM Backend is running!"


@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()

        if connection.is_connected():
            connection.close()
            return "MySQL connection successful!"

    except Exception as e:
        return f"MySQL connection failed: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)