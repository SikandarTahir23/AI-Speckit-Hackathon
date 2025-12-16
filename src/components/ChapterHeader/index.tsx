/**
 * ChapterHeader Component
 *
 * Compact header controls for chapter pages:
 * - Language toggle (EN ⇄ اردو) - always visible
 * - Personalization dropdown - only when authenticated
 *
 * Positioned in the top right of the breadcrumb area
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@site/src/contexts/AuthContext';
import { useChapterContent, DifficultyLevel } from '@site/src/contexts/ChapterContentContext';
import styles from './styles.module.css';

interface ChapterHeaderProps {
  chapterId: number;
}

type Language = 'en' | 'ur';

export default function ChapterHeader({ chapterId }: ChapterHeaderProps) {
  const { user, loading: authLoading } = useAuth();
  const {
    viewMode,
    translationData,
    setViewMode,
    setTranslationData,
    setPersonalizationData
  } = useChapterContent();

  // State management
  const [language, setLanguage] = useState<Language>('en');
  const [selectedLevel, setSelectedLevel] = useState<DifficultyLevel | null>(null);
  const [showPersonalizationDropdown, setShowPersonalizationDropdown] = useState(false);

  // Loading and error states
  const [isTranslating, setIsTranslating] = useState(false);
  const [isPersonalizing, setIsPersonalizing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get API base URL from Docusaurus config
  const API_BASE_URL = typeof window !== 'undefined'
    ? (window as any).docusaurus?.siteConfig?.customFields?.API_BASE_URL || 'http://localhost:8000'
    : 'http://localhost:8000';

  console.log('🔧 [ChapterHeader] Initialized:', {
    chapterId,
    API_BASE_URL,
    isAuthenticated: !!user,
    userEmail: user?.email || 'none',
    authLoading
  });

  // Load language preference from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem(`chapter-${chapterId}-language`);
    if (savedLanguage === 'ur' || savedLanguage === 'en') {
      setLanguage(savedLanguage as Language);
    }
  }, [chapterId]);

  // Handle language toggle
  const handleLanguageToggle = async () => {
    const newLanguage: Language = language === 'en' ? 'ur' : 'en';

    console.log(`🌐 [ChapterHeader] Toggling language: ${language} → ${newLanguage}`);

    if (newLanguage === 'ur') {
      if (!translationData) {
        // Need to fetch translation
        const success = await fetchTranslation();
        if (!success) return;
      }
      setViewMode('translated');
    } else {
      setViewMode('original');
    }

    setLanguage(newLanguage);
    localStorage.setItem(`chapter-${chapterId}-language`, newLanguage);
  };

  // Fetch translation from backend
  const fetchTranslation = async () => {
    setError(null);
    setIsTranslating(true);

    console.log(`📡 [ChapterHeader] Fetching translation for chapter ${chapterId}`);
    console.log(`📡 [ChapterHeader] API URL: ${API_BASE_URL}/translate`);

    try {
      const response = await fetch(`${API_BASE_URL}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          chapter_id: chapterId,
          target_lang: 'ur',
        }),
      });

      console.log(`📡 [ChapterHeader] Translation response status: ${response.status}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `Translation failed (HTTP ${response.status})`);
      }

      const data = await response.json();
      console.log(`✅ [ChapterHeader] Translation successful (${data.cached ? 'cached' : 'new'})`);

      setTranslationData({
        original: data.original_text,
        translated: data.translated_text,
      });

      return true;
    } catch (err: any) {
      console.error('❌ [ChapterHeader] Translation error:', err);

      // Provide specific error messages
      let errorMessage = 'Translation failed';
      if (err.message === 'Failed to fetch') {
        errorMessage = '⚠️ Cannot connect to backend. Is the server running on port 8000?';
      } else if (err.message.includes('HTTP')) {
        errorMessage = `⚠️ Server error: ${err.message}`;
      } else {
        errorMessage = `⚠️ ${err.message}`;
      }

      setError(errorMessage);
      return false;
    } finally {
      setIsTranslating(false);
    }
  };

  // Handle personalization selection
  const handlePersonalizationSelect = async (level: DifficultyLevel) => {
    console.log(`🎯 [ChapterHeader] Personalizing to ${level} level`);

    setError(null);
    setIsPersonalizing(true);
    setSelectedLevel(level);
    setShowPersonalizationDropdown(false);

    console.log(`📡 [ChapterHeader] Fetching personalization for chapter ${chapterId}, level ${level}`);
    console.log(`📡 [ChapterHeader] API URL: ${API_BASE_URL}/personalize`);
    console.log(`📡 [ChapterHeader] Auth status: ${user ? 'authenticated' : 'not authenticated'}`);

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

      console.log(`📡 [ChapterHeader] Personalization response status: ${response.status}`);

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required. Please sign in again.');
        }
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `Personalization failed (HTTP ${response.status})`);
      }

      const data = await response.json();
      console.log(`✅ [ChapterHeader] Personalization successful (${data.cached ? 'cached' : 'new'})`);

      setPersonalizationData({
        content: data.personalized_content,
        level,
      });
      setViewMode('personalized');

      return true;
    } catch (err: any) {
      console.error('❌ [ChapterHeader] Personalization error:', err);

      // Provide specific error messages
      let errorMessage = 'Personalization failed';
      if (err.message === 'Failed to fetch') {
        errorMessage = '⚠️ Cannot connect to backend. Is the server running on port 8000?';
      } else if (err.message.includes('Authentication required')) {
        errorMessage = '⚠️ Please sign in to use personalization features';
      } else if (err.message.includes('HTTP')) {
        errorMessage = `⚠️ Server error: ${err.message}`;
      } else {
        errorMessage = `⚠️ ${err.message}`;
      }

      setError(errorMessage);
      setSelectedLevel(null);
      return false;
    } finally {
      setIsPersonalizing(false);
    }
  };

  return (
    <div className={styles.headerContainer}>
      {/* Language Toggle */}
      <div className={styles.languageToggle}>
        <button
          className={styles.toggleButton}
          onClick={handleLanguageToggle}
          disabled={isTranslating}
          title={language === 'en' ? 'Switch to Urdu' : 'Switch to English'}
        >
          {isTranslating ? (
            <span className={styles.spinner}>⏳</span>
          ) : (
            <span className={styles.languageLabel}>
              EN ⇄ اردو
            </span>
          )}
        </button>
        {language === 'ur' && (
          <span className={styles.activeLanguageIndicator}>اردو</span>
        )}
      </div>

      {/* Personalization Dropdown */}
      {!authLoading && (
        user ? (
          <div className={styles.personalizationDropdown}>
            <button
              className={styles.dropdownButton}
              onClick={() => setShowPersonalizationDropdown(!showPersonalizationDropdown)}
              disabled={isPersonalizing}
              title="Personalize chapter content"
            >
              {isPersonalizing ? (
                <span className={styles.spinner}>⏳</span>
              ) : (
                <>
                  <span>Personalize</span>
                  <span className={styles.dropdownIcon}>▼</span>
                </>
              )}
            </button>

            {selectedLevel && !isPersonalizing && (
              <span className={styles.selectedLevelBadge}>
                {selectedLevel === 'Beginner' && '🌱'}
                {selectedLevel === 'Intermediate' && '🚀'}
                {selectedLevel === 'Advanced' && '⚡'}
              </span>
            )}

            {showPersonalizationDropdown && (
              <div className={styles.dropdownMenu}>
                <button
                  className={`${styles.dropdownItem} ${selectedLevel === 'Beginner' ? styles.selected : ''}`}
                  onClick={() => handlePersonalizationSelect('Beginner')}
                >
                  <span className={styles.levelIcon}>🌱</span>
                  <span>Beginner</span>
                  {selectedLevel === 'Beginner' && <span className={styles.checkmark}>✓</span>}
                </button>
                <button
                  className={`${styles.dropdownItem} ${selectedLevel === 'Intermediate' ? styles.selected : ''}`}
                  onClick={() => handlePersonalizationSelect('Intermediate')}
                >
                  <span className={styles.levelIcon}>🚀</span>
                  <span>Intermediate</span>
                  {selectedLevel === 'Intermediate' && <span className={styles.checkmark}>✓</span>}
                </button>
                <button
                  className={`${styles.dropdownItem} ${selectedLevel === 'Advanced' ? styles.selected : ''}`}
                  onClick={() => handlePersonalizationSelect('Advanced')}
                >
                  <span className={styles.levelIcon}>⚡</span>
                  <span>Advanced</span>
                  {selectedLevel === 'Advanced' && <span className={styles.checkmark}>✓</span>}
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className={styles.authPrompt} title="Sign in to personalize content">
            <span className={styles.lockIcon}>🔒</span>
            <span className={styles.authText}>Sign in to personalize</span>
          </div>
        )
      )}

      {/* Error Message */}
      {error && (
        <div className={styles.errorToast}>
          <span>{error}</span>
          <button onClick={() => setError(null)} className={styles.dismissButton}>✕</button>
        </div>
      )}
    </div>
  );
}
