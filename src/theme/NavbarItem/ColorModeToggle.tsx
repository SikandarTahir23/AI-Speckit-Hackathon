import React from 'react';
import { useColorMode } from '@docusaurus/theme-common';

export default function ColorModeToggle() {
  const { colorMode, setColorMode } = useColorMode();

  const toggleColorMode = () => {
    setColorMode(colorMode === 'dark' ? 'light' : 'dark');
  };

  return (
    <button
      className="navbar__item navbar__link"
      onClick={toggleColorMode}
      aria-label="Toggle dark mode"
      style={{
        padding: '0.5rem 1rem',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        color: 'var(--ifm-navbar-link-color)',
        transition: 'color 0.2s ease',
      }}
    >
      {colorMode === 'dark' ? (
        <>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="5" strokeWidth="2"/>
            <line x1="12" y1="1" x2="12" y2="3" strokeWidth="2"/>
            <line x1="12" y1="21" x2="12" y2="23" strokeWidth="2"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" strokeWidth="2"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" strokeWidth="2"/>
            <line x1="1" y1="12" x2="3" y2="12" strokeWidth="2"/>
            <line x1="21" y1="12" x2="23" y2="12" strokeWidth="2"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" strokeWidth="2"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" strokeWidth="2"/>
          </svg>
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Light</span>
        </>
      ) : (
        <>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" strokeWidth="2"/>
          </svg>
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Dark</span>
        </>
      )}
    </button>
  );
}
