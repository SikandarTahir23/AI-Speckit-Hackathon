
/**
 * ChapterControls Component (Hackathon Bonus Feature 2)
 *
 * Difficulty level selector and personalization controls
 * T054-T057: Difficulty UI, personalization API call, loading state, error handling
 */

import React, { useState } from 'react';
import styles from './styles.module.css';

interface ChapterControlsProps {
  chapterId: number;
  isAuthenticated: boolean;
  onPersonalizedContent?: (content: string, level: string) => void;
}

type DifficultyLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export default function ChapterControls({
  chapterId,
  isAuthenticated,
  onPersonalizedContent,
}: ChapterControlsProps) {
  const [selectedLevel, setSelectedLevel] = useState<DifficultyLevel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get API base URL from Docusaurus config
  const API_BASE_URL = (globalThis as any).docusaurus?.siteConfig?.customFields?.API_BASE_URL || 'http://localhost:8000';

  // T055: Personalization API call
  const handlePersonalize = async (level: DifficultyLevel) => {
    setError(null);
    setLoading(true);
    setSelectedLevel(level);

    try {
      const response = await fetch(`${API_BASE_URL}/personalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send auth cookie
        body: JSON.stringify({
          chapter_id: chapterId,
          difficulty_level: level,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Please sign in to use personalization features');
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Personalization failed');
      }

      const data = await response.json();
      console.log(`Personalization ${data.cached ? 'cache HIT' : 'cache MISS'} - ${data.processing_time_ms}ms`);

      // Pass personalized content to parent
      if (onPersonalizedContent) {
        onPersonalizedContent(data.personalized_content, level);
      }
    } catch (err: any) {
      console.error('Personalization error:', err);
      setError(err.message || 'Failed to personalize content');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className={styles.unauthenticated}>
        <p className={styles.message}>
          🔒 Sign in to personalize this chapter to your experience level
        </p>
      </div>
    );
  }

  return (
    <div className={styles.controls}>
      <div className={styles.header}>
        <h4>Personalize Content</h4>
        <p className={styles.subtitle}>
          Adapt this chapter to your experience level
        </p>
      </div>

      <div className={styles.buttonGroup}>
        <button
          className={`${styles.levelButton} ${selectedLevel === 'Beginner' ? styles.selected : ''}`}
          onClick={() => handlePersonalize('Beginner')}
          disabled={loading}
        >
          <span className={styles.icon}>🌱</span>
          <span className={styles.label}>Beginner</span>
          {selectedLevel === 'Beginner' && <span className={styles.check}>✓</span>}
        </button>

        <button
          className={`${styles.levelButton} ${selectedLevel === 'Intermediate' ? styles.selected : ''}`}
          onClick={() => handlePersonalize('Intermediate')}
          disabled={loading}
        >
          <span className={styles.icon}>🚀</span>
          <span className={styles.label}>Intermediate</span>
          {selectedLevel === 'Intermediate' && <span className={styles.check}>✓</span>}
        </button>

        <button
          className={`${styles.levelButton} ${selectedLevel === 'Advanced' ? styles.selected : ''}`}
          onClick={() => handlePersonalize('Advanced')}
          disabled={loading}
        >
          <span className={styles.icon}>⚡</span>
          <span className={styles.label}>Advanced</span>
          {selectedLevel === 'Advanced' && <span className={styles.check}>✓</span>}
        </button>
      </div>

      {loading && (
        <div className={styles.loadingState}>
          <div className={styles.spinner}></div>
          <p>Personalizing content for your level...</p>
        </div>
      )}

      {error && (
        <div className={styles.errorMessage}>
          <span className={styles.errorIcon}>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {selectedLevel && !loading && !error && (
        <div className={styles.successMessage}>
          <span className={styles.successIcon}>✓</span>
          <span>Content personalized for {selectedLevel} level</span>
        </div>
      )}
    </div>
  );
}
