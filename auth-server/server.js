import express from "express";
import cors from "cors";
import { auth } from "./auth.js";
import { toNodeHandler } from "better-auth/node";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// CORS configuration
app.use(
  cors({
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    credentials: true,
  })
);

app.use(express.json());

// Better Auth routes - use toNodeHandler for Express compatibility
app.all("/api/auth/*", toNodeHandler(auth));

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "auth-server" });
});

// Get current user endpoint (for frontend)
app.get("/api/auth/me", async (req, res) => {
  try {
    const session = await auth.api.getSession({
      headers: req.headers,
    });

    if (!session) {
      return res.status(401).json({ error: "Not authenticated" });
    }

    res.json({ user: session.user, session: session.session });
  } catch (error) {
    console.error("Error getting session:", error);
    res.status(500).json({ error: "Failed to get session" });
  }
});

// Custom signup endpoint with profile fields
app.post("/api/auth/signup", async (req, res) => {
  try {
    const {
      email,
      password,
      name,
      softwareBackground,
      hardwareBackground,
      pythonFamiliar,
      rosFamiliar,
      aimlFamiliar,
    } = req.body;

    const result = await auth.api.signUpEmail({
      body: {
        email,
        password,
        name: name || email.split("@")[0],
        softwareBackground: softwareBackground || "Beginner",
        hardwareBackground: hardwareBackground || "None",
        pythonFamiliar: pythonFamiliar || false,
        rosFamiliar: rosFamiliar || false,
        aimlFamiliar: aimlFamiliar || false,
      },
      headers: req.headers,
    });

    res.json(result);
  } catch (error) {
    console.error("Signup error:", error);
    res.status(400).json({ error: error.message || "Signup failed" });
  }
});

app.listen(PORT, () => {
  console.log(`🔐 Auth server running on http://localhost:${PORT}`);
  console.log(`📝 Better Auth API: http://localhost:${PORT}/api/auth`);
});
