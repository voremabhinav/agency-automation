from flask import Blueprint, request, jsonify
from db import get_db_connection

notification_bp = Blueprint("notification_bp", __name__)


# ============================================================
# 1. CREATE NOTIFICATION
# ============================================================

@notification_bp.route("/api/notifications", methods=["POST"])
def create_notification():

    data = request.get_json() or {}

    user_type = data.get("user_type")
    user_id = data.get("user_id")
    title = data.get("title")
    message = data.get("message")
    notification_type = data.get("notification_type")
    related_lead_id = data.get("related_lead_id")
    related_employee_id = data.get("related_employee_id")

    if not user_type or not title or not message:
        return jsonify({
            "error": "user_type, title and message are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO notifications
        (
            user_type,
            user_id,
            title,
            message,
            notification_type,
            related_lead_id,
            related_employee_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        user_type,
        user_id,
        title,
        message,
        notification_type,
        related_lead_id,
        related_employee_id
    )

    try:

        cursor.execute(query, values)
        connection.commit()

        notification_id = cursor.lastrowid

        return jsonify({
            "message": "Notification created successfully",
            "notification_id": notification_id
        }), 201

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 2. GET NOTIFICATIONS
# ============================================================

@notification_bp.route("/api/notifications", methods=["GET"])
def get_notifications():

    user_type = request.args.get("user_type")
    user_id = request.args.get("user_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if user_type and user_id:

        query = """
            SELECT
                id,
                user_type,
                user_id,
                title,
                message,
                notification_type,
                related_lead_id,
                related_employee_id,
                is_read,
                created_at
            FROM notifications
            WHERE user_type = %s
              AND user_id = %s
            ORDER BY id DESC
        """

        cursor.execute(
            query,
            (user_type, user_id)
        )

    else:

        cursor.execute("""
            SELECT
                id,
                user_type,
                user_id,
                title,
                message,
                notification_type,
                related_lead_id,
                related_employee_id,
                is_read,
                created_at
            FROM notifications
            ORDER BY id DESC
        """)

    notifications = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(notifications), 200


# ============================================================
# 3. MARK NOTIFICATION AS READ
# ============================================================

@notification_bp.route(
    "/api/notifications/<int:notification_id>/read",
    methods=["PUT"]
)
def mark_notification_read(notification_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_read = TRUE
        WHERE id = %s
    """, (notification_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Notification not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Notification marked as read",
        "notification_id": notification_id
    }), 200


# ============================================================
# 4. DELETE NOTIFICATION
# ============================================================

@notification_bp.route(
    "/api/notifications/<int:notification_id>",
    methods=["DELETE"]
)
def delete_notification(notification_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM notifications
        WHERE id = %s
    """, (notification_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Notification not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Notification deleted successfully",
        "notification_id": notification_id
    }), 200