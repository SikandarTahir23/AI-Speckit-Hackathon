/**
 * ChapterFeatures - Standalone component for chapter pages
 * Import this directly in markdown files
 */

import React from 'react';
import { useAuth } from '@site/src/contexts/AuthContext';
import ChapterPersonalization from '@site/src/components/ChapterPersonalization';
import TranslatedChapter from '@site/src/components/TranslatedChapter';

interface ChapterFeaturesProps {
  chapterId: number;
}

export default function ChapterFeatures({ chapterId }: ChapterFeaturesProps) {
  const { user, loading: authLoading } = useAuth();

  console.log('🎯 [ChapterFeatures] Rendering:', {
    chapterId,
    authLoading,
    isAuthenticated: !!user,
    userEmail: user?.email || 'none'
  });

  return (
    <div style={{
      marginTop: '1rem',
      marginBottom: '2rem',
      padding: '1.5rem',
      background: 'linear-gradient(135deg, rgba(26, 31, 46, 0.8) 0%, rgba(37, 45, 61, 0.8) 100%)',
      border: '2px solid rgba(0, 212, 255, 0.4)',
      borderRadius: '12px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 212, 255, 0.15)'
    }}>
      <div style={{
        fontSize: '1.1rem',
        color: '#00d4ff',
        marginBottom: '1.5rem',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '1.5px',
        textShadow: '0 0 15px rgba(0, 212, 255, 0.6)'
      }}>
        ⚡ Chapter {chapterId} Interactive Features
      </div>

      {/* Translation - Always visible */}
      <div style={{ marginBottom: '1rem' }}>
        <TranslatedChapter chapterId={chapterId} />
      </div>

      {/* Personalization - Auth gated */}
      {authLoading ? (
        <div style={{
          padding: '1.5rem',
          textAlign: 'center',
          color: '#c0c7d4',
          background: 'rgba(37, 45, 61, 0.5)',
          border: '2px solid rgba(0, 212, 255, 0.2)',
          borderRadius: '8px',
          fontSize: '0.95rem'
        }}>
          ⏳ Loading authentication status...
        </div>
      ) : (
        <ChapterPersonalization
          chapterId={chapterId}
          isAuthenticated={!!user}
        />
      )}
    </div>
  );
}
