import { useEffect, useState } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import LeadApprovalButton from './LeadApprovalButton';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function HRDashboard() {
  const [stats, setStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const token = localStorage.getItem("token");
        
        // Hitting your secured Python Flask admin_routes.py
        const response = await fetch("http://localhost:5000/api/admin/dashboard", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`, 
          },
        });

        if (!response.ok) throw new Error("Failed to load HR Dashboard data");

        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardStats();

    const fetchLeads = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/leads");
        if (!response.ok) throw new Error("Failed to load leads");

        const data = await response.json();
        setLeads(data.leads || []);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchLeads();
  }, []);

  if (loading) return <h2>Loading HR Analytics...</h2>;
  if (error) return <h2 style={{ color: "red" }}>{error}</h2>;

  const chartData = {
    labels: ['Pending Review', 'Approved', 'Rejected'],
    datasets: [
      {
        data: [stats.pending_reviews, stats.approved_leads, stats.rejected_leads],
        backgroundColor: ['#f59e0b', '#10b981', '#ef4444'],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
      <h2 style={{ fontSize: "26px", color: "#1f2937", marginBottom: "20px" }}>Agency HR Overview</h2>
      
      {/* KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "20px", marginBottom: "30px" }}>
        <div style={styles.card}>
          <h4 style={styles.cardTitle}>Total Leads</h4>
          <p style={styles.cardNumber}>{stats.total_leads}</p>
        </div>
        <div style={styles.card}>
          <h4 style={styles.cardTitle}>Pending HR Review</h4>
          <p style={{ ...styles.cardNumber, color: "#f59e0b" }}>{stats.pending_reviews}</p>
        </div>
        <div style={styles.card}>
          <h4 style={styles.cardTitle}>Total Employees</h4>
          <p style={styles.cardNumber}>{stats.total_employees}</p>
        </div>
        <div style={styles.card}>
          <h4 style={styles.cardTitle}>System Admins</h4>
          <p style={styles.cardNumber}>{stats.total_admins}</p>
        </div>
      </div>

      {/* Chart Section */}
      <div style={{ background: "white", padding: "20px", borderRadius: "12px", boxShadow: "0 3px 10px rgba(0,0,0,0.08)", maxWidth: "400px" }}>
        <h3 style={{ textAlign: "center", color: "#374151" }}>Lead Status Distribution</h3>
        <Doughnut data={chartData} />
      </div>

      <section style={{ marginTop: "30px" }}>
        <h3 style={{ color: "#374151" }}>Pending Lead Approvals</h3>
        {leads.length === 0 ? (
          <p>No leads are waiting for approval.</p>
        ) : (
          leads.map((lead, index) => (
            <div key={lead.id || index} style={styles.leadCard}>
              <h3 style={styles.leadTitle}>{lead.client_name || "Unknown Client"}</h3>
              <p>Budget: {lead.budget || "Not Specified"}</p>

              <div style={styles.replyBox}>
                <strong>AI-generated reply draft</strong>
                <p>{lead.suggested_reply || "No reply draft available."}</p>
              </div>

              <div style={styles.actionRow}>
                <LeadApprovalButton lead={lead} />
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  );
}

const styles = {
  card: { background: "white", padding: "20px", borderRadius: "12px", boxShadow: "0 3px 10px rgba(0,0,0,0.08)", textAlign: "center" },
  cardTitle: { margin: 0, fontSize: "13px", color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.5px" },
  cardNumber: { fontSize: "32px", fontWeight: "bold", margin: "10px 0 0", color: "#2563eb" },
  leadCard: { background: "white", padding: "16px", marginTop: "16px", borderRadius: "8px", boxShadow: "0 3px 10px rgba(0,0,0,0.08)" },
  leadTitle: { margin: "0 0 8px", color: "#1f2937" },
  replyBox: { padding: "12px", marginTop: "12px", background: "#f3f4f6", borderRadius: "6px", color: "#374151" },
  actionRow: { display: "flex", justifyContent: "flex-end", marginTop: "16px" }
};