// backend/middleware/authMiddleware.js
const jwt = require("jsonwebtoken");

// 1. Verify the Token
const verifyToken = (req, res, next) => {
    // Look for the token in the headers (e.g., "Bearer eyJhbGci...")
    const token = req.headers.authorization?.split(" ")[1];

    if (!token) {
        return res.status(401).json({ 
            success: false, 
            message: "Access Denied. No digital ID badge (token) provided." 
        });
    }

    try {
        // Verify the token using your secret key
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded; // Attaches the user's { id, role } to the request
        next(); // The user is legit, let them through
    } catch (error) {
        res.status(403).json({ 
            success: false, 
            message: "Invalid or expired token." 
        });
    }
};

// 2. Check the Role
const requireRole = (allowedRoles) => {
    return (req, res, next) => {
        // If the user's role isn't in the allowed list, kick them out
        if (!req.user || !allowedRoles.includes(req.user.role)) {
            return res.status(403).json({ 
                success: false, 
                message: "Forbidden. Your role does not have access to this data." 
            });
        }
        next();
    };
};

module.exports = { verifyToken, requireRole };