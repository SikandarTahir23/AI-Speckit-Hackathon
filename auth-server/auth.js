import { betterAuth } from "better-auth";
import Database from "better-sqlite3";
import dotenv from "dotenv";

dotenv.config();

// Create SQLite database
const sqliteDb = new Database("./auth.db");

export const auth = betterAuth({
  database: sqliteDb,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3001",
  basePath: "/api/auth",
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },
  user: {
    additionalFields: {
      softwareBackground: {
        type: "string",
        required: false,
        defaultValue: "Beginner",
      },
      hardwareBackground: {
        type: "string",
        required: false,
        defaultValue: "None",
      },
      pythonFamiliar: {
        type: "boolean",
        required: false,
        defaultValue: false,
      },
      rosFamiliar: {
        type: "boolean",
        required: false,
        defaultValue: false,
      },
      aimlFamiliar: {
        type: "boolean",
        required: false,
        defaultValue: false,
      },
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  trustedOrigins: [process.env.FRONTEND_URL || "http://localhost:3000"],
});
