import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import AuthWidget from '../../components/AuthWidget';
import { authClient } from '@site/src/lib/auth-client';

export default function LoginButton() {
  const { user, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = React.useState(false);

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
  };

  const handleLogout = async () => {
    try {
      await authClient.signOut();
      window.location.reload(); // Refresh to update auth state
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return <div className="button button--secondary button--sm" style={{ width: '80px' }}>...</div>;
  }

  return (
    <>
      {user ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{
            color: 'var(--robot-electric-blue)',
            fontWeight: 600,
            textShadow: '0 0 10px rgba(0, 212, 255, 0.3)',
            fontSize: '0.9rem'
          }}>
            {user.name || user.email}
          </span>
          <button
            className="button button--outline button--sm"
            onClick={handleLogout}
            style={{
              border: '1px solid var(--robot-electric-blue)',
              color: 'var(--robot-electric-blue)',
              background: 'transparent',
              fontWeight: 500,
              transition: 'all 0.2s ease',
              padding: '0.4rem 1rem',
              fontSize: '0.85rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--robot-electric-blue)';
              e.currentTarget.style.color = 'var(--robot-dark-graphite)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--robot-electric-blue)';
            }}
          >
            Logout
          </button>
        </div>
      ) : (
        <button
          className="button button--outline"
          onClick={() => setShowAuthModal(true)}
          style={{
            border: '2px solid var(--robot-electric-blue)',
            color: 'var(--robot-electric-blue)',
            background: 'transparent',
            fontWeight: 700,
            fontSize: '1rem',
            transition: 'all 0.3s ease',
            padding: '0.75rem 2rem',
            borderRadius: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--robot-electric-blue)';
            e.currentTarget.style.color = 'var(--robot-dark-graphite)';
            e.currentTarget.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.6)';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = 'var(--robot-electric-blue)';
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          Login
        </button>
      )}
      {showAuthModal && (
        <AuthWidget
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </>
  );
}
