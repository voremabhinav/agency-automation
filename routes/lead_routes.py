from flask import Blueprint, request, jsonify
from db import get_db_connection

lead_bp = Blueprint("lead_bp", __name__)

admin_bp = Blueprint("admin_bp", __name__)


# ============================================================
# 1. ADMIN DASHBOARD
# ============================================================

@admin_bp.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Total leads
        cursor.execute("SELECT COUNT(*) AS total_leads FROM leads")
        total_leads = cursor.fetchone()["total_leads"]

        # Pending HR reviews
        cursor.execute("""
            SELECT COUNT(*) AS pending_reviews
            FROM leads
            WHERE hr_status = 'PENDING'
               OR hr_status IS NULL
        """)
        pending_reviews = cursor.fetchone()["pending_reviews"]

        # Approved leads
        cursor.execute("""
            SELECT COUNT(*) AS approved_leads
            FROM leads
            WHERE hr_status = 'APPROVED'
        """)
        approved_leads = cursor.fetchone()["approved_leads"]

        # Rejected leads
        cursor.execute("""
            SELECT COUNT(*) AS rejected_leads
            FROM leads
            WHERE hr_status = 'REJECTED'
        """)
        rejected_leads = cursor.fetchone()["rejected_leads"]

        # Total employees
        cursor.execute("""
            SELECT COUNT(*) AS total_employees
            FROM employees
        """)
        total_employees = cursor.fetchone()["total_employees"]

        return jsonify({
            "total_leads": total_leads,
            "pending_reviews": pending_reviews,
            "approved_leads": approved_leads,
            "rejected_leads": rejected_leads,
            "total_employees": total_employees
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# ============================================================
# 2. CREATE EMPLOYEE
# ============================================================

@admin_bp.route("/api/employees", methods=["POST"])
def create_employee():

    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    role = data.get("role")
    department = data.get("department")
    joining_date = data.get("joining_date")

    if not name:
        return jsonify({
            "error": "Employee name is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO employees
            (
                name,
                email,
                role,
                department,
                joining_date
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            name,
            email,
            role,
            department,
            joining_date
        ))

        connection.commit()

        employee_id = cursor.lastrowid

        return jsonify({
            "message": "Employee created successfully",
            "employee_id": employee_id
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
# 3. GET ALL EMPLOYEES
# ============================================================

@admin_bp.route("/api/employees", methods=["GET"])
def get_employees():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                department,
                joining_date,
                created_at
            FROM employees
            ORDER BY id DESC
        """)

        employees = cursor.fetchall()

        return jsonify(employees), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 4. GET SINGLE EMPLOYEE
# ============================================================

@admin_bp.route("/api/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                department,
                joining_date,
                created_at
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "error": "Employee not found"
            }), 404

        return jsonify(employee), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 5. UPDATE EMPLOYEE
# ============================================================

@admin_bp.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):

    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE employees
            SET
                name = COALESCE(%s, name),
                email = COALESCE(%s, email),
                role = COALESCE(%s, role),
                department = COALESCE(%s, department),
                joining_date = COALESCE(%s, joining_date)
            WHERE id = %s
        """, (
            data.get("name"),
            data.get("email"),
            data.get("role"),
            data.get("department"),
            data.get("joining_date"),
            employee_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Employee not found"
            }), 404

        return jsonify({
            "message": "Employee updated successfully",
            "employee_id": employee_id
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 6. DELETE / DEACTIVATE EMPLOYEE
# ============================================================

@admin_bp.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM employees
            WHERE id = %s
        """, (employee_id,))

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Employee not found"
            }), 404

        return jsonify({
            "message": "Employee deleted successfully",
            "employee_id": employee_id
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 7. ASSIGN LEAD TO EMPLOYEE
# ============================================================

@admin_bp.route(
    "/api/admin/leads/<int:lead_id>/assign",
    methods=["PUT"]
)
def assign_lead(lead_id):

    data = request.get_json() or {}

    employee_id = data.get("employee_id")

    if not employee_id:
        return jsonify({
            "error": "employee_id is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # Check employee
        cursor.execute("""
            SELECT id, name
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "error": "Employee not found"
            }), 404

        # Check lead
        cursor.execute("""
            SELECT id, name, company_name
            FROM leads
            WHERE id = %s
        """, (lead_id,))

        lead = cursor.fetchone()

        if not lead:
            return jsonify({
                "error": "Lead not found"
            }), 404

        # Assign lead
        cursor.execute("""
            UPDATE leads
            SET assigned_to = %s
            WHERE id = %s
        """, (
            employee_id,
            lead_id
        ))

        connection.commit()

        # =====================================================
        # AUTOMATIC EMPLOYEE NOTIFICATION
        # =====================================================

        notification_cursor = connection.cursor()

        notification_cursor.execute("""
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
        """, (
            "EMPLOYEE",
            employee_id,
            "New Lead Assigned",
            f"Lead #{lead_id} has been assigned to you.",
            "LEAD_ASSIGNMENT",
            lead_id,
            employee_id
        ))

        connection.commit()

        notification_cursor.close()

        return jsonify({
            "message": "Lead assigned successfully",
            "lead_id": lead_id,
            "employee_id": employee_id,
            "employee_name": employee["name"]
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 8. GET EMPLOYEE ASSIGNED LEADS
# ============================================================

@admin_bp.route(
    "/api/employees/<int:employee_id>/leads",
    methods=["GET"]
)
def get_employee_leads(employee_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                phone,
                company_name,
                project_type,
                requirements,
                budget,
                timeline,
                source,
                message,
                status,
                hr_status,
                assigned_to,
                created_at,
                updated_at
            FROM leads
            WHERE assigned_to = %s
            ORDER BY id DESC
        """, (employee_id,))

        leads = cursor.fetchall()

        return jsonify({
            "employee_id": employee_id,
            "assigned_leads": leads
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 9. UPDATE LEAD STATUS BY EMPLOYEE
# ============================================================

@admin_bp.route(
    "/api/employees/<int:employee_id>/leads/<int:lead_id>/status",
    methods=["PUT"]
)
def update_lead_status(employee_id, lead_id):

    data = request.get_json() or {}

    status = data.get("status")

    allowed_statuses = [
        "NEW",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status",
            "allowed_statuses": allowed_statuses
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE leads
            SET status = %s
            WHERE id = %s
              AND assigned_to = %s
        """, (
            status,
            lead_id,
            employee_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Lead not found or not assigned to this employee"
            }), 404

        return jsonify({
            "message": "Lead status updated successfully",
            "lead_id": lead_id,
            "employee_id": employee_id,
            "status": status
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 10. CREATE EMPLOYEE WORK REPORT
# ============================================================

@admin_bp.route(
    "/api/employees/<int:employee_id>/reports",
    methods=["POST"]
)
def create_work_report(employee_id):

    data = request.get_json() or {}

    lead_id = data.get("lead_id")
    report_date = data.get("report_date")
    tasks_completed = data.get("tasks_completed")
    hours_worked = data.get("hours_worked")
    performance_notes = data.get("performance_notes")

    if not report_date:
        return jsonify({
            "error": "report_date is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO performance
            (
                employee_id,
                lead_id,
                report_date,
                tasks_completed,
                hours_worked,
                performance_notes,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'SUBMITTED')
        """, (
            employee_id,
            lead_id,
            report_date,
            tasks_completed,
            hours_worked,
            performance_notes
        ))

        connection.commit()

        report_id = cursor.lastrowid

        return jsonify({
            "message": "Work report submitted successfully",
            "report_id": report_id,
            "employee_id": employee_id,
            "lead_id": lead_id,
            "status": "SUBMITTED"
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
# 11. GET ALL WORK REPORTS
# ============================================================

@admin_bp.route(
    "/api/admin/reports",
    methods=["GET"]
)
def get_all_reports():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                p.id,
                p.employee_id,
                e.name AS employee_name,
                e.email AS employee_email,
                p.lead_id,
                p.report_date,
                p.tasks_completed,
                p.hours_worked,
                p.performance_notes,
                p.status,
                p.created_at
            FROM performance p
            JOIN employees e
                ON p.employee_id = e.id
            ORDER BY p.id DESC
        """)

        reports = cursor.fetchall()

        return jsonify(reports), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


# ============================================================
# 12. CREATE PERFORMANCE REVIEW
# ============================================================

@admin_bp.route(
    "/api/admin/employees/<int:employee_id>/performance",
    methods=["POST"]
)
def create_performance_review(employee_id):

    data = request.get_json() or {}

    review_period = data.get("review_period")
    manager_comments = data.get("manager_comments")
    recommendation = data.get("recommendation")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # Get submitted reports
        cursor.execute("""
            SELECT
                COUNT(*) AS completed_tasks,
                COALESCE(SUM(hours_worked), 0) AS total_hours
            FROM performance
            WHERE employee_id = %s
              AND status = 'SUBMITTED'
        """, (employee_id,))

        result = cursor.fetchone()

        completed_tasks = int(result["completed_tasks"] or 0)
        total_hours = float(result["total_hours"] or 0)

        # ----------------------------------------------------
        # Performance score calculation
        # ----------------------------------------------------

        performance_score = 0.00

        if completed_tasks > 0:

            task_score = min(completed_tasks * 20, 60)
            hour_score = min(total_hours * 5, 40)

            performance_score = task_score + hour_score

        performance_score = min(performance_score, 100)

        # ----------------------------------------------------
        # Automatic recommendation
        # ----------------------------------------------------

        if recommendation:
            final_recommendation = recommendation

        elif performance_score >= 80:
            final_recommendation = "EXCELLENT"

        elif performance_score >= 60:
            final_recommendation = "GOOD"

        elif performance_score >= 40:
            final_recommendation = "AVERAGE"

        else:
            final_recommendation = "NEEDS_IMPROVEMENT"

        # ----------------------------------------------------
        # Insert review
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO performance_reviews
            (
                employee_id,
                review_period,
                completed_tasks,
                total_hours,
                performance_score,
                manager_comments,
                recommendation
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            employee_id,
            review_period,
            completed_tasks,
            total_hours,
            performance_score,
            manager_comments,
            final_recommendation
        ))

        connection.commit()

        review_id = cursor.lastrowid

        # ----------------------------------------------------
        # Automatic performance notification
        # ----------------------------------------------------

        notification_cursor = connection.cursor()

        notification_cursor.execute("""
            INSERT INTO notifications
            (
                user_type,
                user_id,
                title,
                message,
                notification_type,
                related_employee_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "EMPLOYEE",
            employee_id,
            "Performance Review Completed",
            f"Your performance review for {review_period} has been completed.",
            "PERFORMANCE_REVIEW",
            employee_id
        ))

        connection.commit()

        notification_cursor.close()

        return jsonify({
            "message": "Performance review created successfully",
            "review_id": review_id,
            "employee_id": employee_id,
            "completed_tasks": completed_tasks,
            "total_hours": total_hours,
            "performance_score": performance_score,
            "recommendation": final_recommendation
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
# 13. GET ALL PERFORMANCE REVIEWS
# ============================================================

@admin_bp.route(
    "/api/admin/performance",
    methods=["GET"]
)
def get_performance_reviews():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                pr.id,
                pr.employee_id,
                e.name AS employee_name,
                e.email AS employee_email,
                pr.review_period,
                pr.completed_tasks,
                pr.total_hours,
                pr.performance_score,
                pr.manager_comments,
                pr.recommendation,
                pr.created_at
            FROM performance_reviews pr
            JOIN employees e
                ON pr.employee_id = e.id
            ORDER BY pr.id DESC
        """)

        reviews = cursor.fetchall()

        return jsonify(reviews), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()