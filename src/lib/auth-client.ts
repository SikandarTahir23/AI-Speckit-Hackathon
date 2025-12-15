/**
 * Better Auth Client Configuration
 * Handles authentication on the frontend
 */

import { createAuthClient } from "better-auth/react";

// Get auth server URL from Docusaurus config or use default
const getAuthBaseURL = () => {
  // Only access window/globalThis in browser environment
  if (typeof window !== 'undefined' && typeof globalThis !== 'undefined') {
    const docusaurusConfig = (globalThis as any).docusaurus?.siteConfig?.customFields;
    if (docusaurusConfig?.AUTH_BASE_URL) {
      return docusaurusConfig.AUTH_BASE_URL;
    }
  }

  // Fallback to default localhost for development
  return 'http://localhost:3001';
};

export const authClient = createAuthClient({
  baseURL: getAuthBaseURL(),
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;
