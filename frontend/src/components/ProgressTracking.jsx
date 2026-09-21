import { useEffect, useState } from "react";

const TASK_ID = "948dd1a2-d67a-4b6b-a207-bd1521b47f3b";

function ProgressTracking() {
    const [task, setTask] = useState(null);
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState("");

    // Get task progress
    const fetchProgress = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(
                `http://localhost:5000/api/progress/${TASK_ID}`, 
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    }
                }
            );

            const result = await response.json();

            if (result.success) {
                setTask(result.data);
                setProgress(result.data.progress);
            } else {
                setMessage(result.message);
            }
        } catch (error) {
            setMessage("Unable to connect to backend");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProgress();
    }, []);

    // Update task progress
    const updateProgress = async () => {
        try {
            setMessage("");
            const token = localStorage.getItem("token");

            let status;

            if (Number(progress) === 0) {
                status = "Assigned";
            } else if (Number(progress) === 100) {
                status = "Completed";
            } else {
                status = "In Progress";
            }

            const response = await fetch(
                `http://localhost:5000/api/progress/${TASK_ID}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        progress: Number(progress),
                        status: status
                    })
                }
            );

            const result = await response.json();

            if (result.success) {
                setTask(result.data);
                setProgress(result.data.progress);
                setMessage("Progress updated successfully!");
            } else {
                setMessage(result.message);
            }
        } catch (error) {
            setMessage("Unable to update progress");
        }
    };

    if (loading) {
        return <h2>Loading task progress...</h2>;
    }

    if (!task) {
        return <h2>{message || "Task not found"}</h2>;
    }

    return (
        <div>
            <h1>Progress Tracking</h1>

            <h2>{task.task_title}</h2>

            <p>{task.description}</p>

            <p>
                <strong>Status:</strong> {task.status}
            </p>

            <p>
                <strong>Deadline:</strong> {task.deadline}
            </p>

            <h3>Progress: {progress}%</h3>

            <input
                type="range"
                min="0"
                max="100"
                value={progress}
                onChange={(e) => setProgress(e.target.value)}
            />

            <br />
            <br />

            <button onClick={updateProgress}>
                Update Progress
            </button>

            {message && <p>{message}</p>}
        </div>
    );
}

export default ProgressTracking;