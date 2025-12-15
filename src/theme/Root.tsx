/**
 * Root wrapper - Provides global context providers
 * This wraps the entire Docusaurus app
 */

import React from 'react';
import { AuthProvider } from '@site/src/contexts/AuthContext';

export default function Root({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
