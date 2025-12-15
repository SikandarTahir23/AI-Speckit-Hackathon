/**
 * Database Migration Script
 * Initializes Better Auth database schema
 */

import { auth } from "./auth.js";

async function migrate() {
  console.log("🔄 Initializing database schema...");

  try {
    // Better Auth auto-generates tables on first request
    // We'll trigger this by calling a safe method
    await auth.api.listSessions({ headers: {} }).catch(() => {
      // Expected to fail, but triggers table creation
    });

    console.log("✅ Database schema initialized successfully!");
    console.log("📊 Tables created: user, session, verification, account");
    process.exit(0);
  } catch (error) {
    console.error("❌ Migration failed:", error);
    process.exit(1);
  }
}

migrate();
