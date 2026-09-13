from flask import Blueprint, request, jsonify
from db import get_db_connection

admin_bp = Blueprint("admin_bp", __name__)




@admin_bp.route("/api/admins", methods=["POST"])
def create_admin():

    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO admins
        (name, email, password, role)
        VALUES (%s, %s, %s, %s)
    """

    values = (
        data.get("name"),
        data.get("email"),
        data.get("password"),
        data.get("role", "ADMIN")
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        admin_id = cursor.lastrowid

        return jsonify({
            "message": "Admin created successfully",
            "admin_id": admin_id
        }), 201

    except Exception as e:
        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        cursor.close()
        connection.close()


@admin_bp.route("/api/admins", methods=["GET"])
def get_admins():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                created_at
            FROM admins
            ORDER BY id DESC
        """)

        admins = cursor.fetchall()

        return jsonify(admins), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()



@admin_bp.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                id,
                name,
                email,
                password,
                role
            FROM admins
            WHERE email = %s
        """

        cursor.execute(query, (email,))
        admin = cursor.fetchone()

        if not admin:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        if admin["password"] != password:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        return jsonify({
            "message": "Admin login successful",
            "admin": {
                "id": admin["id"],
                "name": admin["name"],
                "email": admin["email"],
                "role": admin["role"]
            }
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()



@admin_bp.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT COUNT(*) AS total_leads
            FROM leads
        """)
        total_leads = cursor.fetchone()["total_leads"]

        cursor.execute("""
            SELECT COUNT(*) AS pending_reviews
            FROM leads
            WHERE hr_status = 'PENDING'
               OR hr_status IS NULL
        """)
        pending_reviews = cursor.fetchone()["pending_reviews"]

        cursor.execute("""
            SELECT COUNT(*) AS approved_leads
            FROM leads
            WHERE hr_status = 'APPROVED'
        """)
        approved_leads = cursor.fetchone()["approved_leads"]

        cursor.execute("""
            SELECT COUNT(*) AS rejected_leads
            FROM leads
            WHERE hr_status = 'REJECTED'
        """)
        rejected_leads = cursor.fetchone()["rejected_leads"]

        cursor.execute("""
            SELECT COUNT(*) AS total_admins
            FROM admins
        """)
        total_admins = cursor.fetchone()["total_admins"]

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
            "total_admins": total_admins,
            "total_employees": total_employees
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


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

    query = """
        INSERT INTO employees
        (
            name,
            email,
            role,
            department,
            joining_date
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        name,
        email,
        role,
        department,
        joining_date
    )

    try:

        cursor.execute(query, values)
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



@admin_bp.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):

    data = request.get_json() or {}

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE employees
        SET
            name = %s,
            email = %s,
            role = %s,
            department = %s,
            joining_date = %s
        WHERE id = %s
    """

    values = (
        data.get("name"),
        data.get("email"),
        data.get("role"),
        data.get("department"),
        data.get("joining_date"),
        employee_id
    )

    try:

        cursor.execute(query, values)
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




@admin_bp.route(
    "/api/employees/<int:employee_id>/deactivate",
    methods=["PUT"]
)
def deactivate_employee(employee_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE employees
        SET status = 'INACTIVE'
        WHERE id = %s
    """

    try:

        cursor.execute(query, (employee_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Employee not found"
            }), 404

        return jsonify({
            "message": "Employee deactivated successfully",
            "employee_id": employee_id,
            "status": "INACTIVE"
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        cursor.close()
        connection.close()



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

        # ----------------------------------------------------
        # CHECK LEAD
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                hr_status
            FROM leads
            WHERE id = %s
        """, (lead_id,))

        lead = cursor.fetchone()

        if not lead:
            return jsonify({
                "error": "Lead not found"
            }), 404

        # Only approved leads can be assigned
        if lead["hr_status"] != "APPROVED":
            return jsonify({
                "error": "Only approved leads can be assigned"
            }), 400

        # ----------------------------------------------------
        # CHECK EMPLOYEE
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                name,
                status
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return jsonify({
                "error": "Employee not found"
            }), 404

        if employee["status"] != "ACTIVE":
            return jsonify({
                "error": "Employee is inactive"
            }), 400

        # ----------------------------------------------------
        # ASSIGN LEAD
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE leads
            SET assigned_to = %s
            WHERE id = %s
        """, (
            employee_id,
            lead_id
        ))

        # ----------------------------------------------------
        # CREATE EMPLOYEE NOTIFICATION
        # ----------------------------------------------------

        cursor.execute("""
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

        # ----------------------------------------------------
        # SAVE EVERYTHING
        # ----------------------------------------------------

        connection.commit()

        return jsonify({
            "message": "Lead assigned successfully",
            "lead_id": lead_id,
            "employee_id": employee_id,
            "employee_name": employee["name"],
            "notification": "Employee notification created successfully"
        }), 200

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        cursor.close()
        connection.close()



@admin_bp.route(
    "/api/employees/<int:employee_id>/leads",
    methods=["GET"]
)
def get_assigned_leads(employee_id):

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
# 11. UPDATE LEAD STATUS
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



@admin_bp.route(
    "/api/employees/<int:employee_id>/reports",
    methods=["POST"]
)
def create_work_report(employee_id):

    data = request.get_json() or {}

    tasks_completed = data.get("tasks_completed", 0)
    tasks_pending = data.get("tasks_pending", 0)
    quality_score = data.get("quality_score", 0)
    attendance_score = data.get("attendance_score", 0)
    deadline_score = data.get("deadline_score", 0)
    review_period = data.get("review_period")

    if not review_period:
        return jsonify({
            "error": "review_period is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        overall_score = (
            float(quality_score)
            + float(attendance_score)
            + float(deadline_score)
        ) / 3

        cursor.execute("""
            INSERT INTO performance
            (
                employee_id,
                tasks_completed,
                tasks_pending,
                quality_score,
                attendance_score,
                deadline_score,
                overall_score,
                review_period
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            employee_id,
            tasks_completed,
            tasks_pending,
            quality_score,
            attendance_score,
            deadline_score,
            overall_score,
            review_period
        ))

        connection.commit()

        report_id = cursor.lastrowid

        return jsonify({
            "message": "Performance report submitted successfully",
            "report_id": report_id,
            "employee_id": employee_id,
            "tasks_completed": tasks_completed,
            "tasks_pending": tasks_pending,
            "quality_score": quality_score,
            "attendance_score": attendance_score,
            "deadline_score": deadline_score,
            "overall_score": round(overall_score, 2),
            "review_period": review_period
        }), 201

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        cursor.close()
        connection.close()



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
        p.tasks_completed,
        p.tasks_pending,
        p.quality_score,
        p.attendance_score,
        p.deadline_score,
        p.overall_score,
        p.review_period,
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




@admin_bp.route(
    "/api/admin/employees/<int:employee_id>/performance",
    methods=["POST"]
)
@admin_bp.route(
    "/api/admin/employees/<int:employee_id>/performance",
    methods=["POST"]
)
def create_performance_review(employee_id):

    data = request.get_json() or {}

    review_period = data.get("review_period")
    manager_comments = data.get("manager_comments")
    recommendation = data.get("recommendation")

    if not review_period:
        return jsonify({
            "error": "review_period is required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # Get performance data from the actual performance table
        cursor.execute("""
            SELECT
                COALESCE(SUM(tasks_completed), 0) AS completed_tasks,
                COALESCE(AVG(overall_score), 0) AS performance_score
            FROM performance
            WHERE employee_id = %s
        """, (employee_id,))

        result = cursor.fetchone()

        completed_tasks = int(
            result["completed_tasks"] or 0
        )

        performance_score = float(
            result["performance_score"] or 0
        )

        # Determine recommendation
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

        # Total hours is NOT available in the performance table.
        total_hours = float(
            data.get("total_hours", 0) or 0
        )

        # Insert into performance_reviews
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

        review_id = cursor.lastrowid

        # Create employee notification
        cursor.execute("""
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

        return jsonify({
            "message": "Performance review created successfully",
            "review_id": review_id,
            "employee_id": employee_id,
            "completed_tasks": completed_tasks,
            "total_hours": total_hours,
            "performance_score": round(
                performance_score, 2
            ),
            "recommendation": final_recommendation,
            "notification": "Employee notification created successfully"
        }), 201

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        cursor.close()
        connection.close()



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