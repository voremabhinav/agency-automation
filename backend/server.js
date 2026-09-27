require("dotenv").config();

const express = require("express");
const cors = require("cors");
const { sendWhatsAppMessage } = require("./services/whatsappService");

const app = express();

const taskRoutes = require("./routes/taskRoutes");
const progressRoutes = require("./routes/progressRoutes");

const corsOptions = {
    origin: "http://localhost:5173",
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true
};

app.use(cors(corsOptions));
app.use(express.json());

app.use("/tasks", taskRoutes);
app.use("/api/progress", progressRoutes);
app.get("/", (req, res) => {
    res.json({
        success: true,
        message: "Task Management Backend is Running..."
    });
});

const PORT = process.env.PORT || 5001;

// The endpoint Python will hit
app.post("/api/send-whatsapp", async (req, res) => {
    const { phoneNumber, message } = req.body;
    
    if (!phoneNumber || !message) {
        return res.status(400).json({ success: false, message: "Missing phoneNumber or message" });
    }

    try {
        await sendWhatsAppMessage(phoneNumber, message);
        res.status(200).json({ success: true, message: "WhatsApp message dispatched via Node!" });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

const server = app.listen(PORT, () => {
    console.log(`✅ Server running at http://localhost:${PORT}`);
});

server.on("close", () => {
    console.log("❌ HTTP SERVER CLOSED");
});

server.on("error", (error) => {
    console.error("❌ SERVER ERROR:", error);
});

process.on("exit", (code) => {
    console.log("⚠️ NODE PROCESS EXITING WITH CODE:", code);
});

process.on("uncaughtException", (error) => {
    console.error("❌ UNCAUGHT EXCEPTION:", error);
});

process.on("unhandledRejection", (error) => {
    console.error("❌ UNHANDLED REJECTION:", error);
});