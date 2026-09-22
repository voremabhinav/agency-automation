import { useState } from "react";

const API_BASE_URL = "http://localhost:5000";

export default function LeadApprovalButton({ lead }) {
  const [isApproving, setIsApproving] = useState(false);

  const handleApproveLead = async () => {
    setIsApproving(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_BASE_URL}/api/leads/approve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token || ""}`,
        },
        body: JSON.stringify({
          clientEmail: lead.client_email || lead.email,
          clientPhone: lead.client_phone || lead.phone,
          generatedReply: lead.suggested_reply,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to approve lead.");
      }

      window.alert(result.message || "Lead approved!");
    } catch (error) {
      console.error("Failed to approve lead:", error);
      window.alert(`Error: ${error.message || "Network error while approving the lead."}`);
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleApproveLead}
      disabled={isApproving}
      style={{
        padding: "10px 16px",
        border: 0,
        borderRadius: "6px",
        backgroundColor: isApproving ? "#9ca3af" : "#16a34a",
        color: "#ffffff",
        fontWeight: 700,
        cursor: isApproving ? "not-allowed" : "pointer",
        opacity: isApproving ? 0.8 : 1,
      }}
    >
      {isApproving ? "Sending AI Replies..." : "Approve & Auto-Reply"}
    </button>
  );
}
