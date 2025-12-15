/**
 * AuthWidget Component - Better Auth Integration
 *
 * Signup/Signin modal with profile questions using Better Auth
 */

import React, { useState } from 'react';
import styles from './styles.module.css';
import { authClient } from '@site/src/lib/auth-client';

interface AuthWidgetProps {
  onClose?: () => void;
  onAuthSuccess?: (user: any) => void;
}

export default function AuthWidget({ onClose, onAuthSuccess }: AuthWidgetProps) {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Prevent background scroll when modal is open
  React.useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  // Profile fields (for signup)
  const [softwareBackground, setSoftwareBackground] = useState<'Beginner' | 'Intermediate' | 'Advanced'>('Beginner');
  const [hardwareBackground, setHardwareBackground] = useState<'None' | 'Basic' | 'Hands-on'>('None');
  const [pythonFamiliar, setPythonFamiliar] = useState(false);
  const [rosFamiliar, setRosFamiliar] = useState(false);
  const [aimlFamiliar, setAimlFamiliar] = useState(false);

  // Get auth server URL from config
  const getAuthBaseURL = () => {
    if (typeof window !== 'undefined') {
      const docusaurusConfig = (globalThis as any).docusaurus?.siteConfig?.customFields;
      if (docusaurusConfig?.AUTH_BASE_URL) {
        return docusaurusConfig.AUTH_BASE_URL;
      }
    }
    return 'http://localhost:3001';
  };

  // Health check utility - check if auth server is actually reachable
  const checkServerHealth = async (): Promise<boolean> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // Reduced timeout
      const authBaseURL = getAuthBaseURL();

      const response = await fetch(`${authBaseURL}/health`, {
        signal: controller.signal,
        method: 'GET',
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (err) {
      // Server is genuinely unreachable
      console.error('Auth server health check failed:', err);
      return false;
    }
  };

  // Better Auth signup integration
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const result = await authClient.signUp.email({
        email,
        password,
        name: name || email.split('@')[0],
        callbackURL: '/auth/callback',
        data: {
          softwareBackground,
          hardwareBackground,
          pythonFamiliar,
          rosFamiliar,
          aimlFamiliar,
        },
      });

      if (result.error) {
        throw new Error(result.error.message || 'Registration failed');
      }

      console.log('Signup successful:', result.data);

      if (onAuthSuccess && result.data?.user) {
        onAuthSuccess(result.data.user);
      }

      if (onClose) {
        onClose();
      }
    } catch (err: any) {
      console.error('Signup error:', err);

      // Check if it's a network error
      if (err.message?.includes('fetch') || err.name === 'AbortError' || err.message?.includes('Failed to fetch')) {
        // Try health check to confirm server is down
        const isHealthy = await checkServerHealth();
        if (!isHealthy) {
          setError('⏳ Unable to connect to authentication server. Please check if the server is running.');
        } else {
          setError('Connection error. Please try again.');
        }
      } else {
        setError(err.message || 'Failed to create account. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Better Auth signin integration
  const handleSignin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const result = await authClient.signIn.email({
        email,
        password,
        callbackURL: '/auth/callback',
      });

      if (result.error) {
        throw new Error(result.error.message || 'Login failed');
      }

      console.log('Signin successful:', result.data);

      if (onAuthSuccess && result.data?.user) {
        onAuthSuccess(result.data.user);
      }

      if (onClose) {
        onClose();
      }
    } catch (err: any) {
      console.error('Signin error:', err);

      // Check if it's a network error
      if (err.message?.includes('fetch') || err.name === 'AbortError' || err.message?.includes('Failed to fetch')) {
        // Try health check to confirm server is down
        const isHealthy = await checkServerHealth();
        if (!isHealthy) {
          setError('⏳ Unable to connect to authentication server. Please check if the server is running.');
        } else {
          setError('Connection error. Please try again.');
        }
      } else if (err.message?.includes('Invalid credentials') || err.message?.includes('Login failed')) {
        setError('Invalid email or password. Please check your credentials.');
      } else {
        setError(err.message || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          ×
        </button>

        <h2>{mode === 'signin' ? 'Sign In' : 'Create Account'}</h2>

        {error && (
          <div className={styles.error}>{error}</div>
        )}

        {mode === 'signin' ? (
          // T028: Signin form
          <form onSubmit={handleSignin} className={styles.form}>
            <div className={styles.field}>
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
              />
            </div>

            <div className={styles.field}>
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </div>

            <button type="submit" className={styles.submitButton} disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>

            <p className={styles.toggleMode}>
              Don't have an account?{' '}
              <button type="button" onClick={() => setMode('signup')}>
                Sign up
              </button>
            </p>
          </form>
        ) : (
          // Signup form with profile questions
          <form onSubmit={handleSignup} className={styles.form}>
            <div className={styles.field}>
              <label htmlFor="signup-name">Name</label>
              <input
                id="signup-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name (optional)"
              />
            </div>

            <div className={styles.field}>
              <label htmlFor="signup-email">Email</label>
              <input
                id="signup-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
              />
            </div>

            <div className={styles.field}>
              <label htmlFor="signup-password">Password</label>
              <input
                id="signup-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="e.g., MyPassword123"
                minLength={8}
                title="Password must contain at least one uppercase letter, one lowercase letter, and one number"
              />
              <small style={{
                fontSize: '0.8rem',
                color: 'var(--robot-metal-dark)',
                marginTop: '0.25rem'
              }}>
                Must include: uppercase, lowercase, and number (min 8 characters)
              </small>
            </div>

            <h3 className={styles.profileHeader}>Tell us about yourself</h3>

            <div className={styles.field}>
              <label htmlFor="software-background">Software Development Experience</label>
              <select
                id="software-background"
                value={softwareBackground}
                onChange={(e) => setSoftwareBackground(e.target.value as any)}
                required
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div className={styles.field}>
              <label htmlFor="hardware-background">Hardware/Robotics Experience</label>
              <select
                id="hardware-background"
                value={hardwareBackground}
                onChange={(e) => setHardwareBackground(e.target.value as any)}
                required
              >
                <option value="None">None</option>
                <option value="Basic">Basic</option>
                <option value="Hands-on">Hands-on</option>
              </select>
            </div>

            <div className={styles.checkboxGroup}>
              <label>
                <input
                  type="checkbox"
                  checked={pythonFamiliar}
                  onChange={(e) => setPythonFamiliar(e.target.checked)}
                />
                Familiar with Python
              </label>

              <label>
                <input
                  type="checkbox"
                  checked={rosFamiliar}
                  onChange={(e) => setRosFamiliar(e.target.checked)}
                />
                Familiar with ROS
              </label>

              <label>
                <input
                  type="checkbox"
                  checked={aimlFamiliar}
                  onChange={(e) => setAimlFamiliar(e.target.checked)}
                />
                Familiar with AI/ML
              </label>
            </div>

            <button type="submit" className={styles.submitButton} disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>

            <p className={styles.toggleMode}>
              Already have an account?{' '}
              <button type="button" onClick={() => setMode('signin')}>
                Sign in
              </button>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

