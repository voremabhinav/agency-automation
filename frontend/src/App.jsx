import HRDashboard from "./components/HRDashboard";
import { useEffect, useState } from "react";
import Login from "./components/Login";
import ProgressTracking from "./components/ProgressTracking";

function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");

    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setAuthLoading(false);
  }, []);

  useEffect(() => {
    if (!user || user.role !== "EMPLOYEE") {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    const token = localStorage.getItem("token");

    fetch(`http://localhost:5000/tasks/employee/${user.id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch tasks or unauthorized");
        }

        return response.json();
      })
      .then((result) => {
        setTasks(result.data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to load tasks");
        setLoading(false);
      });
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  if (authLoading) return <p>Loading...</p>;

  if (!user) {
    return <Login onLoginSuccess={(userData) => setUser(userData)} />;
  }

  const totalTasks = tasks.length;

  const completedTasks = tasks.filter(
    (task) => task.status === "Completed"
  ).length;

  const inProgressTasks = tasks.filter(
    (task) => task.status === "In Progress"
  ).length;

  const assignedTasks = tasks.filter(
    (task) => task.status === "Assigned"
  ).length;

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Employee Dashboard</h1>
          <p style={styles.subtitle}>Welcome back, {user.name}</p>
        </div>
        <button onClick={handleLogout}>Logout</button>
      </header>

      {/* Summary Cards */}
      <section style={styles.statsContainer}>
        <div style={styles.statCard}>
          <h3>Total Tasks</h3>
          <p style={styles.statNumber}>{totalTasks}</p>
        </div>

        <div style={styles.statCard}>
          <h3>Assigned</h3>
          <p style={styles.statNumber}>{assignedTasks}</p>
        </div>

        <div style={styles.statCard}>
          <h3>In Progress</h3>
          <p style={styles.statNumber}>{inProgressTasks}</p>
        </div>

        <div style={styles.statCard}>
          <h3>Completed</h3>
          <p style={styles.statNumber}>{completedTasks}</p>
        </div>
      </section>

      {user.role === "EMPLOYEE" ? (
        <>
          {/* Tasks */}
          <section style={styles.tasksSection}>
            <h2 style={styles.sectionTitle}>My Tasks</h2>

            {loading && <p>Loading tasks...</p>}

            {error && <p style={styles.error}>{error}</p>}

            {!loading && !error && tasks.length === 0 && (
              <p>No tasks assigned.</p>
            )}

            <div style={styles.taskGrid}>
              {tasks.map((task) => (
                <div key={task.id} style={styles.taskCard}>
                  <div style={styles.taskHeader}>
                    <h3 style={styles.taskTitle}>{task.task_title}</h3>

                    <span
                      style={{
                        ...styles.status,
                        backgroundColor:
                          task.status === "Completed"
                            ? "#dcfce7"
                            : task.status === "In Progress"
                            ? "#fef3c7"
                            : "#dbeafe",
                        color:
                          task.status === "Completed"
                            ? "#166534"
                            : task.status === "In Progress"
                            ? "#92400e"
                            : "#1e40af",
                      }}
                    >
                      {task.status}
                    </span>
                  </div>

                  <p style={styles.description}>{task.description}</p>

                  <div style={styles.taskInfo}>
                    <p>
                      <strong>Priority:</strong>{" "}
                      <span style={styles.priority}>{task.priority}</span>
                    </p>

                    <p>
                      <strong>Deadline:</strong> {task.deadline}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Progress Tracking */}
          <section style={styles.tasksSection}>
            <ProgressTracking />
          </section>
        </>
      ) : (
        <HRDashboard />
      )}
    </div>
  );
}
    
const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f5f7fb",
    padding: "40px",
    fontFamily: "Arial, sans-serif",
    boxSizing: "border-box",
  },

  header: {
    maxWidth: "1100px",
    margin: "0 auto 30px",
  },

  title: {
    margin: 0,
    fontSize: "36px",
    color: "#1f2937",
  },

  subtitle: {
    marginTop: "8px",
    color: "#6b7280",
    fontSize: "17px",
  },

  statsContainer: {
    maxWidth: "1100px",
    margin: "0 auto 35px",
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "20px",
  },

  statCard: {
    backgroundColor: "#ffffff",
    padding: "25px",
    borderRadius: "12px",
    boxShadow: "0 3px 10px rgba(0,0,0,0.08)",
    textAlign: "center",
  },

  statNumber: {
    fontSize: "32px",
    fontWeight: "bold",
    margin: "10px 0 0",
    color: "#2563eb",
  },

  tasksSection: {
    maxWidth: "1100px",
    margin: "0 auto",
  },

  sectionTitle: {
    fontSize: "26px",
    color: "#1f2937",
    marginBottom: "20px",
  },

  taskGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "20px",
  },

  taskCard: {
    backgroundColor: "#ffffff",
    padding: "25px",
    borderRadius: "12px",
    boxShadow: "0 3px 10px rgba(0,0,0,0.08)",
  },

  taskHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "15px",
  },

  taskTitle: {
    margin: 0,
    fontSize: "21px",
    color: "#111827",
  },

  status: {
    padding: "6px 10px",
    borderRadius: "20px",
    fontSize: "13px",
    fontWeight: "bold",
    whiteSpace: "nowrap",
  },

  description: {
    color: "#6b7280",
    lineHeight: "1.6",
    marginTop: "18px",
  },

  taskInfo: {
    marginTop: "20px",
    borderTop: "1px solid #e5e7eb",
    paddingTop: "15px",
    color: "#374151",
  },

  priority: {
    fontWeight: "bold",
    color: "#dc2626",
  },

  error: {
    color: "#dc2626",
  },
};

export default App;