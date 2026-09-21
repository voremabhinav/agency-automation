const express = require("express");

const {
    createTask,
    getAllTasks,
    getEmployeeTasks,
    updateTask
} = require("../controllers/taskController");

const { verifyToken, requireRole } = require("../middleware/authMiddleware");

const router = express.Router();

router.post("/", verifyToken, requireRole(["HR", "ADMIN"]), createTask);

router.get("/", verifyToken, requireRole(["HR", "ADMIN"]), getAllTasks);

router.get("/employee/:employeeId", verifyToken, requireRole(["EMPLOYEE", "HR", "ADMIN"]), getEmployeeTasks);

router.put("/:id", verifyToken, requireRole(["EMPLOYEE"]), updateTask);

module.exports = router;